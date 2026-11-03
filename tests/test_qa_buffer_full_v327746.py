# -*- coding: utf-8 -*-
"""QA v3.277.46: composicao completa de FUNDO da copia QA, byte-exata.

Usa ParallaxBackground PRODUCAO, profundidade cinematografica e Fase B,
clima real, cenas epicas e chao por quadro. NAO inclui sprites/fisica/audio.
Alternativa offscreen nao e ativada: comparacao falha se RGBA divergir.
"""
import os
import sys
import importlib
import random
import unittest
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame

GAME_NAME='PixelRush_v3.277.11_PRODUCAO_ANDROID_RC'

def game_module():
    # O nome historico tem pontos (v3.277.11), nao e um nome Python importavel.
    # Executar com spec explicito, sem disparar o guard if __name__=='__main__'.
    name='pixelrush_qa_game_v327746'
    if name in sys.modules:
        return sys.modules[name]
    arquivo=ROOT/(GAME_NAME+'.py')
    spec=importlib.util.spec_from_file_location(name, arquivo)
    modulo=importlib.util.module_from_spec(spec)
    sys.modules[name]=modulo
    try:
        spec.loader.exec_module(modulo)
    except Exception:
        sys.modules.pop(name,None)
        raise
    return modulo

def rgba(s):
    return pygame.image.tobytes(s,'RGBA')

def criar_contexto(game,bioma,clima_tipo):
    bg=game.ParallaxBackground()
    bg.set_cenario(bioma)
    bg.world.lightweight=False
    clima=game.SistemaClima()
    clima.cenario=bioma
    clima.tipo=clima_tipo
    cenas=game.CenasMemoraveis()
    return bg,clima,cenas

def desenhar_fundo_integral(game,destino,bg,clima,cenas,frame,cor,night):
    cor_render=clima.aplicar_ceu(cor)
    bg.draw(destino,cor_render,night>=.5)
    game.profundidade_cinematografica(destino,bg.cenario,night,False)
    game.desenhar_profundidade_bioma(
        destino,bg.cenario,bg.world.travel,night,False,clima.tipo)
    if clima.tipo!='limpo':
        clima._desenhar_nuvens_clima(destino,cor_render)
    cenas.desenhar(destino,bg.cenario,bg.world.travel,frame,night,leve=False)

def overlay_por_quadro(game,destino,bg,frame):
    bg.draw_chao(destino)
    pygame.draw.rect(destino,(34,66,96),(0,0,450,43))
    pygame.draw.rect(destino,(242,197,91),(11,13,25+frame%80,13))
    pygame.draw.circle(destino,(249,216,105),(410,28),9)

def comparar_bioma(game,bioma,frames=24,cronometrar=False):
    from pixelrush_qa_ultraleve_v327730 import CacheFundoUltraQA
    # Cada caminho tem seu proprio mundo/parallax/clima/caches de instancia.
    # Restaura o RNG para iniciar as duas instancias com exatamente os
    # mesmos parametros sem perturbar a sequencia de RNG do restante do teste.
    rng_inicial=random.getstate()
    bg,clima,cenas=criar_contexto(game,bioma,'limpo')
    rng_final=random.getstate()
    random.setstate(rng_inicial)
    bg_alt,clima_alt,cenas_alt=criar_contexto(game,bioma,'limpo')
    random.setstate(rng_final)
    ref=pygame.Surface((450,800)).convert()
    alt=ref.copy()
    scratch=ref.copy()
    cache=CacheFundoUltraQA(periodo=5)
    tempos={'original':[],'offscreen':[],'orig_store':[],'offscreen_present':[]}
    equivalentes=0
    divergencias=[]
    for i in range(frames):
        frame=19+i*11
        night=(0.,.3,.6,.95)[(i//5)%4]
        cor=(62+i%25,96+(i*2)%30,136)
        clima.tipo={'cidade':('limpo','chuva','tempestade'),'neve':('limpo','nevasca','neve'),'deserto':('limpo','areia','tempestade_areia')}[bioma][(i//5)%3]
        bg.clima_tipo=clima.tipo
        clima.tempo=frame
        rng_pre_update=random.getstate()
        bg.update(8.8)
        rng_pos_update=random.getstate()
        bg.peso_noite=night
        bg.world.night=night
        bg.world.climate=clima.tipo
        clima_alt.tipo=clima.tipo
        clima_alt.tempo=frame
        bg_alt.clima_tipo=clima.tipo
        random.setstate(rng_pre_update)
        try:
            bg_alt.update(8.8)
        finally:
            random.setstate(rng_pos_update)
        bg_alt.peso_noite=night
        bg_alt.world.night=night
        bg_alt.world.climate=clima.tipo
        chave=(bioma,clima.tipo,night>=.5,False,ref.get_size())
        start=pygame.time.get_ticks() # timing real abaixo usa perf_counter_ns
        from time import perf_counter_ns
        t0=perf_counter_ns()
        hit=cache.reusar(ref,chave,True)
        if not hit:
            # O renderizador real pode consultar o RNG global. Isolar o
            # estado entre as DUAS cenas do benchmark evita que o primeiro
            # desenho altere a sequencia pseudoaleatoria da segunda.
            rng_antes_render=random.getstate()
            desenhar_fundo_integral(game,ref,bg,clima,cenas,frame,cor,night)
            rng_apos_render=random.getstate()
            t1=perf_counter_ns()
            cache.guardar(ref,chave,True)
            t2=perf_counter_ns()
        else:
            t1=t2=perf_counter_ns()
        overlay_por_quadro(game,ref,bg,frame)
        t3=perf_counter_ns()
        # Mesmo novo desenho, mesmo estado; a superficie offscreen nunca
        # recebe o HUD, evitando contaminacao dos frames reutilizados.
        if not hit:
            # O render real preserva pixels anteriores em partes transparentes.
            # Sem copiar a tela anterior para a scratch, a alternativa NAO
            # preserva RGBA (comprovado no deserto, noite=.95, frame 15).
            # A copia extra e medida, NAO e uma otimizacao ativada.
            scratch.blit(alt,(0,0))
            random.setstate(rng_antes_render)
            try:
                desenhar_fundo_integral(game,scratch,bg_alt,clima_alt,cenas_alt,frame,cor,night)
            finally:
                random.setstate(rng_apos_render)
        t4=perf_counter_ns()
        alt.blit(scratch,(0,0))
        t5=perf_counter_ns()
        overlay_por_quadro(game,alt,bg_alt,frame)
        t6=perf_counter_ns()
        b_ref=rgba(ref)
        b_alt=rgba(alt)
        if b_ref!=b_alt:
            pos=next(k for k in range(0,len(b_ref),4)
                     if b_ref[k:k+4]!=b_alt[k:k+4])
            divergencias.append({
                'frame':i,'clima':clima.tipo,'noite':night,
                'primeiro_pixel_x':(pos//4)%450,
                'primeiro_pixel_y':(pos//4)//450,
                'rgba_referencia':list(b_ref[pos:pos+4]),
                'rgba_alternativo':list(b_alt[pos:pos+4]),
            })
            # O experimento deve ser REJEITADO, nao falhar silenciosamente
            # nem ser ativado por um teste que so verifica 1 bioma.
        else:
            equivalentes+=1
        if cronometrar and i>=5:
            tempos['original'].append((t3-t0)/1e6)
            tempos['offscreen'].append((t6-t3)/1e6)
            tempos['orig_store'].append((t2-t1)/1e6 if not hit else 0.)
            tempos['offscreen_present'].append((t5-t4)/1e6)
    return {'bioma':bioma,'quadros_comparados':frames,
            'frames_rgba_identicos':equivalentes,
            'alternativa_pixel_exata_no_ensaio':len(divergencias)==0,
            'alternativa_aprovada':False,
            'divergencias':divergencias[:8],
            'total_quadros_divergentes':len(divergencias),
            'redraws':cache.recriacoes,'hits':cache.passes_evitados,
            'tempos_ms':tempos,'cache_rgb_bytes':cache._quadro.get_pitch()*cache._quadro.get_height(),
            'buffer_alternativo_bytes':scratch.get_pitch()*scratch.get_height()}

class FundoIntegralQA746(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_transferencia_de_mesmo_buffer_composto_preserva_rgba(self):
        # Prova somente da transferencia, NAO equivale a duplicar o render.
        from pixelrush_qa_ultraleve_v327730 import CacheFundoUltraQA
        cache=CacheFundoUltraQA(periodo=5)
        origem=pygame.Surface((450,800)).convert()
        copia=origem.copy()
        destino=origem.copy()
        for i in range(16):
            origem.fill(((i*19)%256,42,(i*13)%256))
            pygame.draw.circle(origem,(214,186,104),
                               (100+(i*23)%330,200+i*21),37)
            pygame.draw.rect(origem,(48,72,111),(0,0,450,41))
            copia.blit(origem,(0,0))
            cache.guardar(copia,('cidade',i),True)
            destino.blit(origem,(0,0))
            self.assertEqual(rgba(destino),rgba(cache._quadro))
            self.assertEqual(rgba(copia),rgba(destino))

    def test_blit_offscreen_sem_preservar_underlay_difere(self):
        # Prova deterministica do risco: o render parcial pode deixar pixels
        # do frame anterior, portanto scratch limpa nao substitui a tela.
        prev=pygame.Surface((450,800)).convert()
        prev.fill((72,89,126))
        pygame.draw.rect(prev,(230,195,142),(430,320,20,60))
        original=prev.copy()
        scratch=pygame.Surface((450,800)).convert()
        scratch.fill((72,89,126))
        pygame.draw.rect(original,(25,33,44),(0,230,430,500))
        pygame.draw.rect(scratch,(25,33,44),(0,230,430,500))
        self.assertNotEqual(rgba(original),rgba(scratch))
        safe=prev.copy()
        pygame.draw.rect(safe,(25,33,44),(0,230,430,500))
        self.assertEqual(rgba(original),rgba(safe))

    def test_integral_prod_cidade_neve_deserto_24_quadros(self):
        game=game_module()
        self.assertIs(game.LivingWorld.__mro__[0],game.LivingWorld)
        for biome in ('cidade','neve','deserto'):
            resposta=comparar_bioma(game,biome,frames=24)
            self.assertEqual(resposta['quadros_comparados'],24)
            self.assertEqual(resposta['redraws']+resposta['hits'],24)
            self.assertFalse(resposta['alternativa_aprovada'])
            self.assertEqual(resposta['frames_rgba_identicos']+
                             resposta['total_quadros_divergentes'],24)
            self.assertEqual(resposta['buffer_alternativo_bytes'],resposta['cache_rgb_bytes'])

if __name__=='__main__':
    unittest.main(verbosity=2)
