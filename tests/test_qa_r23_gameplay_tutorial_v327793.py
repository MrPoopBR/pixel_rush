# -*- coding: utf-8 -*-
"""PIXEL RUSH QA793: tutorial integrado, neve, RNG de biomas e ciclo de 180s.
SDL dummy, sem APK nem escrita em saves.
"""
import ast
import importlib
import os
from pathlib import Path
import random
import sys
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame
pygame.init()
pygame.display.set_mode((450,800))

from src.pixelrush.ui.tutorial.premium_v327793 import TutorialCorrida, _ETAPAS_EXTRA
from src.pixelrush.world.daynight_v327793 import (CICLO_QUADROS, calcular_ciclo_ceu,
                                                     posicao_astro)
from src.pixelrush.entities.enemies.snowman_v327793 import BonecoNeve, BolaDeNeve

class FalsoJogador:
    def __init__(self):
        self.rect=pygame.Rect(80,664,40,66)
        self.chao_y=730
        self.base_h=66
        self.no_chao=True
        self.morrendo=False
        self.tempo_morte=0
        self.velocidade_y=0.0
        self.agachado=False
        self.descida_rapida=False
        self.coyote_ticks=0
        self.buffer_pulo_ticks=0
        self.angulo_rotacao=0
        self._visual_dirty=False
        self.saltos=0
    def update(self,velocidade,frame,pulo,baixo,particulas,pool,som,volume,pode_pousar=True):
        self.no_chao=True
        self.agachado=bool(baixo)
        self.velocidade_y=0.0
        self.rect.bottom=self.chao_y
    def pular(self,som=None,volume=1.):
        self.saltos+=1
        self.no_chao=False
    def iniciar_descida_rapida(self,som=None,volume=1.):
        self.descida_rapida=True
    def iniciar_morte(self):
        self.morrendo=True
        self.tempo_morte=24
    def obter_hitbox(self):
        return self.rect

class FalsoFundo:
    def __init__(self):
        self.ticks=0
        self.desloc_chao=0
        self.camada_perto=0.
        self.camada_longe=0.
        self._desloc_arte=0.
        self._desloc_arte_fundo=0.
    def update(self,*args):
        self.ticks+=1

class FalsoSprite(pygame.sprite.Sprite):
    def __init__(self,x,y_or_codigo=0):
        super().__init__()
        self.codigo=y_or_codigo if isinstance(y_or_codigo,str) else None
        self.image=pygame.Surface((36,36),pygame.SRCALPHA)
        pygame.draw.rect(self.image,(253,211,100),(1,1,33,34))
        y=685 if isinstance(y_or_codigo,str) else int(y_or_codigo)
        self.rect=self.image.get_rect(midleft=(int(x),int(y)))
        self._base_y=self.rect.y
        self._x=float(self.rect.x)
        self._x_float=float(self.rect.x)
    def update(self,v,*args,**kwargs):
        self._x-=float(v)
        self.rect.x=round(self._x)
    def renderizar_visual(self):
        pass

def novo_tutorial():
    j=FalsoJogador()
    t=TutorialCorrida(j,450,800,classe_terrestre=FalsoSprite,
                     classe_voador=FalsoSprite,classe_moeda=FalsoSprite,
                     classe_cidade=FalsoSprite,classe_hidrante=FalsoSprite,
                     classe_bau=FalsoSprite,idioma="pt_BR")
    return t,j,FalsoFundo(),pygame.sprite.Group(),pygame.sprite.Group(),SimpleNamespace(
        palavra="PIXEL",progresso=0,ativo=None)

class QA793(unittest.TestCase):
    def test_swipe_down_em_duas_etapas_mesmo_dedo(self):
        t,j,f,todos,letras,palavra=novo_tutorial()
        t._intro_restante=0
        t.etapa_indice=3
        t._preparar(todos,letras,palavra)
        self.assertEqual(t.etapa,"swipe_down")
        self.assertEqual(len(t.objetos),2)
        t.objetos[0].rect.left=j.rect.right+118
        t.atualizar(j,f,todos,letras,palavra,pygame.sprite.Group(),None,None,0.,1)
        self.assertTrue(t._pausa_comando)
        self.assertEqual(t._swipe_etapa,0)
        # Não permite executar o segundo comando antes do pulo longo.
        t.processar_evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_DOWN))
        self.assertEqual(t._swipe_etapa,0)
        t.processar_evento(pygame.event.Event(pygame.FINGERDOWN,x=.5,y=.40,finger_id=2))
        self.assertEqual(t._swipe_etapa,1)
        self.assertTrue(j.saltos>=1)
        self.assertFalse(t._pausa_comando)
        # Forçar proximidade do segundo pombo mantendo o MESMO dedo na tela.
        t.objetos[1].rect.left=j.rect.right+154
        t.atualizar(j,f,todos,letras,palavra,pygame.sprite.Group(),None,None,0.,2)
        self.assertEqual(t._swipe_etapa,2)
        self.assertTrue(t._pausa_comando)
        self.assertFalse(t.swipe_feito)
        t.processar_evento(pygame.event.Event(pygame.FINGERMOTION,
                                            x=.5,y=.58,finger_id=2))
        self.assertEqual(t._swipe_etapa,3)
        self.assertTrue(t.swipe_feito)
        self.assertTrue(j.descida_rapida)
        self.assertFalse(t._pausa_comando)

    def test_intro_exatos_300_ticks_e_save_nao_antecipado(self):
        t,j,f,todos,letras,palavra=novo_tutorial()
        particulas=pygame.sprite.Group()
        for frame in range(300):
            ganho,terminou=t.atualizar(j,f,todos,letras,palavra,particulas,None,None,0.,frame)
            self.assertEqual(ganho,0)
            self.assertFalse(terminou)
            self.assertTrue(t.ativo)
            self.assertEqual(len(todos),0)
        self.assertEqual(t._intro_restante,0)
        self.assertEqual(f.ticks,300)
        self.assertEqual(t.etapa,"pular")

    def test_morte_reverso_limpam_particulas(self):
        t,j,f,todos,letras,palavra=novo_tutorial()
        t._intro_restante=0
        t._preparar(todos,letras,palavra)
        particulas=pygame.sprite.Group()
        particula=FalsoSprite(150,700)
        particulas.add(particula);todos.add(particula)
        t.fase_recuperacao="morte"
        t.tempo_recuperacao=3
        t.atualizar(j,f,todos,letras,palavra,particulas,None,None,0.,1)
        self.assertEqual(len(particulas),0)
        self.assertFalse(particula.alive())
        self.assertTrue(t.ativo)

    def test_etapas_extras_fluem_ate_concluir(self):
        t,j,f,todos,letras,palavra=novo_tutorial()
        t._intro_restante=0
        t._extra_indice=0
        self.assertEqual(len(_ETAPAS_EXTRA),4)
        for etapa_esperada in ("combo_moedas","febre","baus","descanso"):
            self.assertTrue(t.ativo)
            self.assertEqual(t.etapa,etapa_esperada)
            t._extra_popup=True
            self.assertEqual(t.atualizar(j,f,todos,letras,palavra,pygame.sprite.Group(),
                                         None,None,0.,50),(0,False))
            t.processar_evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE))
            self.assertFalse(t._extra_popup)
            fase=t._extra_indice
            for frame in range(900):
                _,terminou=t.atualizar(j,f,todos,letras,palavra,pygame.sprite.Group(),
                                      None,None,0.,60+frame)
                if t._extra_indice != fase or terminou:
                    break
            else:
                self.fail("Lição extra travou: "+etapa_esperada)
        self.assertFalse(t.ativo)
        self.assertTrue(t.corrida_continua)
        self.assertIsNone(t.etapa)

    def test_ui_animada_sem_rastro_rgba(self):
        t,j,f,todos,letras,palavra=novo_tutorial()
        t._intro_restante=0
        t._extra_indice=1
        t._extra_popup=True
        surf=pygame.Surface((450,800)).convert()
        surf.fill((14,32,55))
        t.desenhar(surf)
        base=surf.copy()
        t.desenhar_fx_congelado(surf,0)
        f0=pygame.image.tobytes(surf,"RGBA")
        surf.blit(base,(0,0))
        t.desenhar_fx_congelado(surf,350)
        f350=pygame.image.tobytes(surf,"RGBA")
        self.assertNotEqual(f0,f350)
        surf.blit(base,(0,0))
        t.desenhar_fx_congelado(surf,0)
        self.assertEqual(f0,pygame.image.tobytes(surf,"RGBA"))

    def test_ciclo_ceu_180s_suave_cores_e_orbitas(self):
        self.assertEqual(CICLO_QUADROS,10800)
        samples=[calcular_ciclo_ceu(0,t)[1] for t in range(CICLO_QUADROS+1)]
        self.assertEqual(samples[0],samples[-1])
        delta=max(abs(a[i]-b[i]) for a,b in zip(samples,samples[1:]) for i in range(3))
        self.assertLessEqual(delta,2)
        for nome,limites in (("sol",(0,.52)),("lua",(.52,1.))):
            a=posicao_astro(limites[0],nome)
            b=posicao_astro(limites[1],nome)
            self.assertIsNotNone(a);self.assertIsNotNone(b)
            self.assertLess(a[0],0)
            self.assertGreater(b[0],450)
            self.assertLess(posicao_astro(sum(limites)/2,nome)[1],a[1])
        self.assertIsNone(posicao_astro(.75,"sol"))
        self.assertIsNone(posicao_astro(.25,"lua"))

    def test_boneco_neve_arremesso_3_alturas_e_pool_visuais(self):
        grupo=pygame.sprite.Group(); perigos=pygame.sprite.Group()
        snow=[BonecoNeve(475,grupo,perigos) for _ in range(3)]
        self.assertIs(snow[0].image,snow[1].image)
        for _ in range(35):
            for b in snow:b.update(1.)
        self.assertEqual(len(perigos),3)
        self.assertEqual(len({x.rect.centery for x in perigos}),3)
        self.assertTrue(all(isinstance(x,BolaDeNeve) for x in perigos))
        for _ in range(15):
            for b in snow:b.update(1.)
        self.assertEqual(len(perigos),3)
        self.assertIsNotNone(BolaDeNeve._quadro)

    def test_biomas_e_codigo_escopo(self):
        engine=(ROOT/"PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py").read_text("utf8")
        ast.parse(engine)
        self.assertIn('v3.277.94-QA-ANDROID-RC',engine)
        self.assertIn('("cidade", "cidade_futurista", "neve", "deserto", "vulcao", "floresta", "ilhas_celestes")',engine)
        self.assertIn('if metros >= 600 and cenario == "cidade_futurista"',engine)
        self.assertIn('inicio_ciclo_frame',engine)
        self.assertIn('retomada_contagem_quadros = 180',engine)
        self.assertIn('self.sons["pegada"]',engine)
        self.assertIn('self.trilhas_bioma.get(cenario)',engine)
        self.assertIn('LivingWorld(self.cenario, lightweight=False)',engine)
        self.assertIn('self.world.lightweight = False',engine)
        self.assertIn('classe_bau=BauSecreto',engine)
        self.assertIn('dados["tutorial_inicial_concluido"] = True',engine)
        self.assertIn('btn_missoes_partida.collidepoint(pos)',engine)

if __name__=="__main__":
    unittest.main(verbosity=2)
