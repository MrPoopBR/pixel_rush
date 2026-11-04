# -*- coding: utf-8 -*-
"""QA782: regressoes do Android A54 (345px de jogo no canto da captura).

SDL SCALED+FULLSCREEN preserva superficie logica, inputs e camera. Em
fallback fisico, letterbox tem geometria invertivel inclusive no toque.
Testes reais pygame-ce, mas NAO equivalem ao driver Mali Android.
"""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame
from pixelrush_qa_android_display_v327782 import (
    area_preservada,ponto_virtual,dedo_normalizado,abrir,diagnostico)
from pixelrush_qa_gles_bridge_v327749 import _Ponte,_ORIGINALS


class AndroidFullscreenQA782(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init()
        pygame.display.set_mode((450,800))

    def test_tela_a54_e_captura_nao_esticam_aspecto(self):
        for size in ((1080,2340),(945,2048),(720,1600),(450,800),
                     (1440,3200)):
            rw,rh,ox,oy=area_preservada(size)
            self.assertLessEqual(rw,size[0])
            self.assertLessEqual(rh,size[1])
            self.assertEqual((size[0]-rw)//2,ox)
            self.assertEqual((size[1]-rh)//2,oy)
            self.assertLess(abs(rw/rh-450/800),0.003)
            self.assertEqual(ponto_virtual(ox+rw/2,oy+rh/2,size),
                             (225,400))
        self.assertEqual(area_preservada((1080,2340)),
                         (1080,1920,0,210))
        self.assertEqual(area_preservada((945,2048)),
                         (945,1680,0,184))

    def test_touches_normalizados_no_letterbox_preservam_swipe(self):
        physical=(1080,2340)
        # Centro, topo, base e gestos verticais em area renderizada.
        self.assertEqual(dedo_normalizado(.5,.5,tamanho_fisico=physical),
                         (225,400))
        self.assertEqual(dedo_normalizado(0,210/2340,tamanho_fisico=physical),
                         (0,0))
        self.assertEqual(dedo_normalizado(1,(210+1920)/2340,
                                         tamanho_fisico=physical),(450,800))
        # Delta de 100 pixels fisicos: mesmo delta de input normalizado.
        y0=dedo_normalizado(.5,1100/2340,tamanho_fisico=physical)[1]
        y1=dedo_normalizado(.5,1200/2340,tamanho_fisico=physical)[1]
        self.assertIn(y1-y0,(41,42))

    def test_tamanho_logico_e_flags_fullscreen_reais(self):
        call=[]
        def set_mode(size,flags=0):
            call.append((size,flags))
            return pygame.Surface((450,800))
        with patch.object(pygame.display,'set_mode',side_effect=set_mode),\
             patch.object(pygame.display,'get_window_size',return_value=(1080,2340)):
            screen=abrir()
        self.assertEqual(call,[((450,800),pygame.SCALED|pygame.FULLSCREEN)])
        self.assertEqual(screen.get_size(),(450,800))
        self.assertEqual(diagnostico()['modo'],'sdl_scaled_fullscreen')

    def test_renderer_escalado_indisponivel_vai_para_fullscreen_fisico(self):
        calls=[]
        def set_mode(size,flags=0):
            calls.append((size,flags))
            if len(calls)==1:
                raise pygame.error('SDL_Renderer_sem_suporte')
            return pygame.Surface((1080,2340))
        with patch.object(pygame.display,'set_mode',side_effect=set_mode),\
             patch.object(pygame.display,'get_window_size',return_value=(1080,2340)):
            screen=abrir()
        self.assertEqual(calls[0],((450,800),pygame.SCALED|pygame.FULLSCREEN))
        self.assertEqual(calls[1],((0,0),pygame.FULLSCREEN))
        self.assertEqual(screen.get_size(),(1080,2340))
        self.assertEqual(diagnostico()['modo'],'fullscreen_fisico_letterbox')

    def test_ponte_gpu_nao_reduz_window_fullscreen_para_450x800(self):
        calls=[]
        def original(size,flags=0,depth=0,display=0,vsync=0):
            calls.append((size,flags))
            return pygame.Surface((450,800))
        ponte=_Ponte()
        with patch.dict(_ORIGINALS,{'set_mode':original}):
            result=ponte.set_mode((450,800),pygame.SCALED|pygame.FULLSCREEN)
        self.assertEqual(result.get_size(),(450,800))
        self.assertEqual(calls,[((450,800),pygame.SCALED|pygame.FULLSCREEN)])
        self.assertEqual(ponte.modo,'nativo')
        self.assertIsNone(ponte.presenter)

    def test_engine_integra_viewport_no_loop_real_sem_tocar_fisica(self):
        e=(Path(__file__).resolve().parents[1]/
           'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        self.assertIn('v3.277.82-QA-ANDROID-RC',e)
        self.assertIn('abrir as _qa_abrir_tela',e)
        self.assertIn('area_preservada(',e)
        self.assertGreaterEqual(e.count('dedo_normalizado(evento.x,evento.y)'),4)
        self.assertIn('tamanho_final = (largura_render, altura_render)',e)
        self.assertIn('pos_final = (offset_x + ox, offset_y + oy)',e)

if __name__=='__main__':
    unittest.main(verbosity=2)
