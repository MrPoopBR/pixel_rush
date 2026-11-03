# -*- coding: utf-8 -*-
"""QA749: testes MOCKADOS do adapter GLES, sem GL real, GPU ou Android.
A parte de GPU REAL deve ser homologada posteriormente no aparelho.
"""
import os,sys,types,unittest
from pathlib import Path
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame
import pixelrush_qa_gles_bridge_v327749 as adapter

class PresenterFake:
    ultimo=None
    falhar=False
    def __init__(self,width,height):
        pygame.display.set_mode((width,height))
        self.width=width
        self.height=height
        type(self).ultimo=self
        self.frames=[]
    def draw(self,image,zoom=0.0,focus_y=0):
        if type(self).falhar:
            raise RuntimeError('GPU simulada interrompida')
        self.frames.append(pygame.image.tobytes(image,'RGBA'))
    def present(self):
        pygame.display.flip()

class BridgeQA749(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        adapter.restaurar_para_teste()
        pygame.quit()

    def test_gpu_desligada_por_padrao(self):
        adapter.restaurar_para_teste()
        with patch.dict(os.environ,{'PIXELRUSH_QA_GLES_BRIDGE':'0'}):
            old=pygame.display.set_mode
            adapter.instalar()
            self.assertIs(pygame.display.set_mode,old)
            self.assertFalse(adapter.diagnostico()['gpu_ativo'])

    def test_fim_a_fim_mockado_fundo_hud_entrada_fallback(self):
        adapter.restaurar_para_teste()
        fake_module=types.SimpleNamespace(GLES2DirectPresenterQA=PresenterFake)
        old_flip=pygame.display.flip
        try:
            with patch.dict(os.environ,{
                   'PIXELRUSH_QA_GLES_BRIDGE':'1',
                   'PIXELRUSH_QA_ANDROID':'1',
                   'PIXELRUSH_QA_GL_DESKTOP_LAB':'1'}), \
                 patch.dict(sys.modules,{
                   'pixelrush_qa_gles_present_v327735':fake_module}):
                adapter.instalar()
                surface=pygame.display.set_mode((450,800))
                self.assertIs(surface,pygame.display.get_surface())
                surface.fill((41,93,120))
                pygame.draw.circle(surface,(255,171,55),(160,500),42)
                pygame.draw.rect(surface,(12,22,61),(0,0,450,70))
                ref=pygame.image.tobytes(surface,'RGBA')
                pygame.display.flip()
                self.assertEqual(PresenterFake.ultimo.frames[-1],ref)
                self.assertTrue(adapter.diagnostico()['gpu_ativo'])
                PresenterFake.falhar=True
                # Mesma staging Surface e pixels sao preservados no fallback.
                pygame.display.flip()
                self.assertIs(surface,pygame.display.get_surface())
                native=adapter._BRIDGE.cpu_window
                self.assertEqual(pygame.image.tobytes(native,'RGBA'),ref)
                self.assertFalse(adapter.diagnostico()['gpu_ativo'])
                self.assertEqual(adapter.diagnostico()['falhas_gpu'],1)
                self.assertGreater(adapter.diagnostico()['frames_fallback'],0)
        finally:
            PresenterFake.falhar=False
            adapter.restaurar_para_teste()
            self.assertIs(pygame.display.flip,old_flip)

if __name__=='__main__':
    unittest.main(verbosity=2)
