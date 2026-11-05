# -*- coding: utf-8 -*-
"""QA784: oito quadros RGBA na tela fisica e gate CPU/GPU do aparelho."""
import os,sys,unittest
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import pygame
import pixelrush_qa_gles_present_v327735 as presenter
from pixelrush_qa_gles_exact_v327736 import shaders
from pixelrush_qa_gles_twopass_v327784 import (FullscreenTwoPassQA,
                                                verificar_boot_fisico)

class TestPhysicalRGBAQA784(unittest.TestCase):
    def test_8_cenas_rgba_e_benchmark_com_ganho_obrigatorio(self):
        pygame.init()
        b=pygame.transform.get_smoothscale_backend()
        old=presenter.VERT,presenter.FRAG
        p=None;two=None
        try:
            pygame.transform.set_smoothscale_backend('SSE2')
            presenter.VERT,presenter.FRAG=shaders('GLES3','SSE2',(450,800))
            p=presenter.GLES2DirectPresenterQA(450,800,fullscreen=True)
            self.assertTrue(p.version.startswith('OpenGL ES 3'))
            two=FullscreenTwoPassQA(p)
            report=verificar_boot_fisico(p,two,exigir_ganho=True)
            self.assertEqual(report['casos_rgba'],8,report)
            self.assertTrue(report['pixels_rgba_exatos'],report)
            self.assertEqual(report['diferencas'],0)
            self.assertEqual((p.width,p.height),(450,800))
            self.assertFalse(report['aprovado_aparelho'])
            self.assertEqual(report['selecionado'],
                bool(report['ganho_p50'] and report['ganho_p50']>1/0.85))
            print('QA784 fullscreen GPU vs CPU',pygame.display.get_window_size(),report)
        finally:
            if two is not None:two.close()
            if p is not None:p.close()
            presenter.VERT,presenter.FRAG=old
            pygame.transform.set_smoothscale_backend(b)
            pygame.quit()
if __name__=='__main__':unittest.main(verbosity=2)
