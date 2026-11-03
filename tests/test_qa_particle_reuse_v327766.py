# -*- coding: utf-8 -*-
"""QA766 — regressao real das rotinas ambient do engine via AST isolada.

Compila os 3 metodos originais intactos da engine, sem executar main(),
sem carregar saves/pets, e compara estado RNG, coordenadas e RGBA.
"""
import ast,os,sys,math,random,unittest
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame
from pixelrush_qa_particle_reuse_v327766 import instalar,restaurar_para_teste,diagnostico

def extrair_metodos():
    src=(Path(__file__).resolve().parents[1]/
         'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf-8')
    classe=next(n for n in ast.parse(src).body
                if isinstance(n,ast.ClassDef) and n.name=='ParallaxBackground')
    nomes=('_reiniciar_particulas_ambiente','_atualizar_particulas_ambiente',
           '_desenhar_particulas_ambiente')
    funcoes=[n for n in classe.body if isinstance(n,ast.FunctionDef) and n.name in nomes]
    assert len(funcoes)==3
    mod=ast.fix_missing_locations(ast.Module(body=funcoes,type_ignores=[]))
    env={'random':random,'math':math,'pygame':pygame,'LARGURA_VIRTUAL':450,
         'misturar_cores':lambda a,b,t:tuple(
             max(0,min(255,int(a[i]+(b[i]-a[i])*t))) for i in range(3))}
    exec(compile(mod,'<engine_methods_real>', 'exec'),env)
    return env

def snapshot(obj):
    return tuple(tuple(sorted(p.items())) for p in obj._particulas_ambiente)

class Particulas766(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        restaurar_para_teste();pygame.quit()

    def test_8_biomas_estados_rng_cores_rgba_reuso(self):
        methods=extrair_metodos()
        class Original:pass
        class Pooled:pass
        for cls in (Original,Pooled):
            for name in ('_reiniciar_particulas_ambiente',
                         '_atualizar_particulas_ambiente',
                         '_desenhar_particulas_ambiente'):
                setattr(cls,name,methods[name])
        instalar(Pooled)
        orig,pool=Original(),Pooled()
        orig._particulas_ambiente=[]
        pool._particulas_ambiente=[]
        rng_anterior=random.getstate()
        biomas=('cidade','neve','deserto','vulcao','floresta',
                'cidade_futurista','ilhas_celestes','reino_submerso',
                'cidade','neve','deserto','cidade')
        ids=set()
        for biome in biomas:
            orig.cenario=pool.cenario=biome
            orig._reiniciar_particulas_ambiente()
            pool._reiniciar_particulas_ambiente()
            self.assertEqual(snapshot(orig),snapshot(pool),biome)
            self.assertEqual(random.getstate(),rng_anterior)
            ids.update(map(id,pool._particulas_ambiente))
            for velocidade in (0,5.25,22.0):
                antes=random.getstate()
                orig._atualizar_particulas_ambiente(velocidade)
                depois_original=random.getstate()
                random.setstate(antes)
                pool._atualizar_particulas_ambiente(velocidade)
                depois_pool=random.getstate()
                self.assertEqual(depois_original,depois_pool,biome)
                self.assertEqual(snapshot(orig),snapshot(pool),(biome,velocidade))
                for alpha in (False,True):
                    flags=pygame.SRCALPHA if alpha else 0
                    a=pygame.Surface((450,800),flags)
                    b=pygame.Surface((450,800),flags)
                    a.fill((31,71,117,0 if alpha else 255))
                    b.fill((31,71,117,0 if alpha else 255))
                    orig._desenhar_particulas_ambiente(a)
                    pool._desenhar_particulas_ambiente(b)
                    self.assertEqual(pygame.image.tobytes(a,'RGBA'),
                                     pygame.image.tobytes(b,'RGBA'),
                                     (biome,velocidade,alpha))
            rng_anterior=random.getstate()
        self.assertLessEqual(len(ids),14,msg='pool ambiental cresceu além do máximo de 14')
        self.assertGreater(diagnostico()['reusados'],0)
        self.assertEqual(diagnostico()['fallbacks'],0)

    def test_pool_original_limita_somente_inativos_excedentes_sem_sumir_ativos(self):
        src=(Path(__file__).resolve().parents[1]/
             'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf-8')
        parte=next(n for n in ast.parse(src).body
                   if isinstance(n,ast.ClassDef) and n.name=='Particula')
        node=ast.fix_missing_locations(ast.Module(body=[parte],type_ignores=[]))
        env={'Sprite':pygame.sprite.Sprite,'pygame':pygame,'random':random}
        exec(compile(node,'<classe_particula_real>','exec'),env)
        P=env['Particula']
        class Dummy:
            _reiniciar_particulas_ambiente=lambda self:None
        instalar(Dummy,P)
        from types import SimpleNamespace
        objetos=[P(vx=0.,vy=0.) for _ in range(300)]
        gerente=SimpleNamespace(particulas_pool=list(objetos),
                                particulas_disponiveis=[])
        grupo=pygame.sprite.Group()
        for p in objetos:
            p.pool_manager=gerente
            p._pool_livre=False
            grupo.add(p)
        # NENHUMA particula ativa removida, mesmo > limite de RAM idle.
        self.assertEqual(len(grupo),300)
        self.assertEqual(len(gerente.particulas_pool),300)
        for p in objetos:
            p.kill()
        self.assertEqual(len(grupo),0)
        self.assertEqual(len(gerente.particulas_pool),256)
        self.assertEqual(len(gerente.particulas_disponiveis),256)
        self.assertEqual(diagnostico()['particulas_excedentes_liberadas'],44)
        # Reutilizacao do pool permanece funcionando apos a tempestade.
        algum=gerente.particulas_disponiveis.pop()
        algum._pool_livre=False
        algum.reset(23,47,(150,200,250),vx=0.2,vy=0.4)
        self.assertTrue(algum.ativo)
        grupo.add(algum)
        self.assertEqual(len(grupo),1)
        algum.kill()
        self.assertEqual(len(gerente.particulas_pool),256)

    def test_desligamento_por_flag_nao_modifica_metodo(self):
        methods=extrair_metodos()
        class C:pass
        C._reiniciar_particulas_ambiente=methods['_reiniciar_particulas_ambiente']
        old=C._reiniciar_particulas_ambiente
        from unittest.mock import patch
        with patch.dict(os.environ,{'PIXELRUSH_QA_PARTICULAS_POOL':'0'}):
            instalar(C)
        self.assertIs(C._reiniciar_particulas_ambiente,old)
        self.assertNotIn(C.__name__,diagnostico())

if __name__=='__main__':
    unittest.main(verbosity=2)
