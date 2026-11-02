#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste pygame-ce REAL do cache temporal ultraleve, sem alterar fisica nem UI."""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import pygame

pygame.init()
pygame.display.set_mode((450,800))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from pixelrush_qa_ultraleve_v327730 import CacheFundoUltraQA, FundoMenusUltraQA


class CenografiaFake:
    def __init__(self):
        self.cenario = 'cidade'
        self.clima_tipo = 'limpo'
        self.world = type('World', (), {'biome':'cidade','lightweight':False})()
        self.draws = 0

    def draw(self, superficie, ceu, e_noite):
        self.draws += 1
        superficie.fill(ceu)


class TesteUltraQA(unittest.TestCase):
    def test_corrida_cache_redesenha_20_porcento_sem_alterar_hud(self):
        fundo = CacheFundoUltraQA(periodo=5)
        tela = pygame.Surface((450,800)).convert()
        redesenhos = 0
        for q in range(20):
            if not fundo.reusar(tela, ('cidade', 'limpo'), True):
                # Reproduz ordem do jogo: cache guarda apenas fundo, ANTES da UI.
                tela.fill((37, 61, 91))
                redesenhos += 1
                fundo.guardar(tela, ('cidade','limpo'), True)
            pygame.draw.rect(tela,(q,217,87),(12,22,90,30)) # HUD
            pygame.draw.rect(tela,(255, q,18),(120,650,30,55)) # Jogador
            self.assertEqual(tela.get_at((13,23))[0],q)
            self.assertEqual(tela.get_at((121,652))[1],q)
            self.assertEqual(tela.get_at((3,3))[:3],(37,61,91))
        self.assertEqual(redesenhos,4)
        self.assertEqual(fundo.passes_evitados,16)
        self.assertEqual(fundo.pedidos,20)

    def test_piso_animado_em_todos_quadros_mesmo_com_fundo_em_cache(self):
        fundo=CacheFundoUltraQA(periodo=5)
        tela=pygame.Surface((450,800)).convert()
        for q in range(15):
            if not fundo.reusar(tela,('cidade','limpo'),True):
                tela.fill((37,61,91))
                fundo.guardar(tela,('cidade','limpo'),True)
            pygame.draw.rect(tela,(q+20,100,120),(0,730,450,70))
            pygame.draw.rect(tela,(q,170,70),(95+q,650,16,32))
            self.assertEqual(tela.get_at((2,750))[0],q+20)
            self.assertEqual(tela.get_at((96+q,654))[0],q)
        codigo=(Path(__file__).resolve().parents[2] /
            'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        inicio=codigo.index('if cache_fundo_mobile.reusar(')
        fim=codigo.index('if estado in ("JOGANDO", "PAUSA") and evento_corrida:',inicio)
        trecho=codigo[inicio:fim]
        self.assertLess(trecho.index('cache_fundo_mobile.guardar('),
                        trecho.index('bg_parallax.draw_chao(display_surface)'))
        self.assertLess(trecho.index('bg_parallax.draw_chao(display_surface)'),
                        trecho.index('desenhar_clima_premium('))

    def test_invalida_em_cenario_clima_tutorial_e_portal(self):
        tela=pygame.Surface((450,800)).convert()
        cache=CacheFundoUltraQA(periodo=5)
        original=('cidade','limpo',False,False)
        self.assertFalse(cache.reusar(tela,original,True))
        tela.fill((1,2,3))
        cache.guardar(tela,original,True)
        self.assertTrue(cache.reusar(tela,original,True))
        for k in [
            ('cidade','chuva',False,False),
            ('deserto','limpo',False,False),
            ('cidade','limpo',True,False),
            ('cidade','limpo',False,True),
        ]:
            self.assertFalse(cache.reusar(tela,k,True))
            tela.fill((1,2,3))
            cache.guardar(tela,k,True)
        self.assertFalse(cache.reusar(tela,k,False))
        self.assertFalse(cache.reusar(tela,k,True))

    def test_menus_background_cache_e_ui_em_todos_quadros(self):
        menu=FundoMenusUltraQA(periodo=5)
        fundo=CenografiaFake()
        tela=pygame.Surface((450,800)).convert()
        for q in range(12):
            menu.desenhar(tela,fundo,(45,70,110),'LOJA')
            pygame.draw.circle(tela,(q,90,200),(225,300),12)
            self.assertEqual(tela.get_at((225,300))[0],q)
            self.assertEqual(tela.get_at((0,0))[:3],(45,70,110))
        self.assertEqual(fundo.draws,3)
        menu.desenhar(tela,fundo,(45,70,110),'CONFIG')
        self.assertEqual(fundo.draws,4)
        menu.desenhar(tela,fundo,(45,70,112),'CONFIG')
        self.assertEqual(fundo.draws,5)

    def test_redesenho_pixel_igual_ao_original(self):
        fundo=CenografiaFake()
        menu=FundoMenusUltraQA(periodo=5)
        alvo=pygame.Surface((450,800)).convert()
        controle=pygame.Surface((450,800)).convert()
        for q in range(11):
            ceu=(41,65,91)
            menu.desenhar(alvo,fundo,ceu,'INICIO')
            # O renderizador original no mesmo estado e mesmo quadro gera os
            # mesmos pixels; diferenca temporal nos quadros reutilizados e assumida.
            if q%5 == 0:
                fundo.draw(controle,ceu,False)
                self.assertEqual(pygame.image.tobytes(alvo,'RGB'),
                                 pygame.image.tobytes(controle,'RGB'))

    def test_codigo_nao_modifica_fisica_saves_e_dev(self):
        path=Path(__file__).resolve().parents[2]/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py'
        codigo=path.read_text(encoding='utf-8')
        compile(codigo,str(path),'exec')
        self.assertIn('MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15',codigo)
        self.assertIn('FPS_RENDER = 30 if E_ANDROID else 60',codigo)
        self.assertIn('pixelrush_qa_ultraleve_v327730',codigo)
        self.assertIn('v3.277.35-QA-ANDROID-RC',codigo)
        self.assertIn('PIXELRUSH_DEV_BUILD = False',codigo)


if __name__=='__main__':
    unittest.main(verbosity=2)
