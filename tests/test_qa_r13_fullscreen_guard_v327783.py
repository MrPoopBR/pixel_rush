# -*- coding: utf-8 -*-
"""R13: candidato GLES fullscreen precisa passar no gate de pixel fisico.
A bancada Mesa pode reprovar: o jogo continua seguro em SDL.
"""
import os
import ctypes as C
import unittest
from pathlib import Path
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ['PIXELRUSH_QA_GLES_PBO']='1'
import pygame
import pixelrush_qa_gles_present_v327735 as presenter
from pixelrush_qa_gles_exact_v327736 import shaders
from pixelrush_qa_gpu_preflight_v327780 import verificar,diagnostico
ROOT=Path(__file__).resolve().parents[1]

class GlesFullscreenGuardQA783(unittest.TestCase):
    def test_gate_real_fullscreen_sem_ativacao_nao_comprovada(self):
        profile=(ROOT/'pixelrush_qa_render_v327729.py').read_text('utf8')
        self.assertNotIn("('PIXELRUSH_QA_GLES_FULLSCREEN_PROBE','1')",profile)
        pygame.init()
        old_shaders=(presenter.VERT,presenter.FRAG)
        old_backend=pygame.transform.get_smoothscale_backend()
        p=None
        try:
            pygame.transform.set_smoothscale_backend('SSE2')
            presenter.VERT,presenter.FRAG=shaders('GLES3','SSE2',(450,800))
            p=presenter.GLES2DirectPresenterQA(450,800,fullscreen=True)
            if not p.version.startswith('OpenGL ES 3'):
                self.skipTest('Driver nao ofereceu GLES3')
            ok=verificar(p,exigir_ganho=True)
            report=diagnostico()
            if ok:
                self.assertEqual(report['diferencas'],0)
                self.assertEqual(report['casos_rgba'],10)
                self.assertLess(report['tempo_gpu_p50_ms'],report['tempo_cpu_p50_ms'])
            else:
                self.assertFalse(report['aprovado'])
            fonte=pygame.Surface((450,800),depth=32)
            fonte.fill((47,89,147))
            p.draw(fonte,0.,0)
            px=(p.qa_viewport[0]+p.qa_viewport[2]//2)
            py=(p.qa_viewport[1]+p.qa_viewport[3]//2)
            buf=(C.c_ubyte*4)()
            read=p.gl.glReadPixels
            read.restype=None
            read.argtypes=[C.c_int,C.c_int,C.c_int,C.c_int,C.c_uint,C.c_uint,C.c_void_p]
            read(px,py,1,1,0x1908,0x1401,buf)
            fisico_exato=tuple(buf)[:3]==(47,89,147)
            if not fisico_exato:
                self.assertNotIn("('PIXELRUSH_QA_GLES_FULLSCREEN_PROBE','1')",profile)
            print('QA783 fullscreen FBO=',ok,'motivo=',report['motivo'],
                  'RGBA=',report['casos_rgba'],'diferencas=',report['diferencas'],
                  'pixel_fisico_exato=',fisico_exato)
        finally:
            if p is not None:
                p.close()
            presenter.VERT,presenter.FRAG=old_shaders
            pygame.transform.set_smoothscale_backend(old_backend)
            pygame.quit()

if __name__=='__main__':unittest.main(verbosity=2)
