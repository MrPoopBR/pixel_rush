# -*- coding: utf-8 -*-
"""QA 3.277.42: PBO GLES3 ring e comparacao exata do framebuffer Mesa."""
import ctypes as C
import importlib.util
import os
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ['PIXELRUSH_QA_GLES_PBO']='1'
import pygame
import pixelrush_qa_gles_present_v327735 as presenter
from pixelrush_qa_gles_exact_v327736 import shaders

spec=importlib.util.spec_from_file_location(
    'qa_gles_ref_742',ROOT/'tests'/'test_qa_gles_exact_v327736.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestPBOQA742(unittest.TestCase):
    def test_pbo_gles3_vs_smoothscale_real(self):
        pygame.init()
        pygame.display.set_mode((450,800))
        original_backend=pygame.transform.get_smoothscale_backend()
        try:
            pygame.transform.set_smoothscale_backend('SSE2')
            presenter.VERT,presenter.FRAG=shaders('GLES3','SSE2',(450,800))
            p=presenter.GLES2DirectPresenterQA(450,800)
            try:
                if not p.version.startswith('OpenGL ES 3'):
                    self.skipTest('Driver nao expoe GLES3; sem forcar PBO')
                _,read=module.framebuffer_rgba8(p)
                frames=[]
                for index in (0,0,1,1,2,2):
                    source=pygame.Surface((450,800),pygame.SRCALPHA)
                    for y in range(800):
                        pygame.draw.line(source,(
                            (y*7+index*23)%256,(y*13+index*29)%256,
                            (y*17+index*31)%256,(y*19+index*17)%256),
                            (0,y),(449,y))
                    frames.append((index,source))
                for index,source in frames:
                    zoom=.025 if index==0 else .034
                    focus=0 if index==0 else 4
                    expected=module.original(source,zoom,focus)
                    p.draw(source,zoom,focus)
                    buf=C.create_string_buffer(450*800*4)
                    read(0,0,450,800,0x1908,0x1401,buf)
                    ref=pygame.image.tobytes(expected,'RGBA',True)
                    self.assertEqual(buf.raw,ref,('GLES3 PBO pixel',index))
                self.assertIsNotNone(p._qa_pbo)
                self.assertGreaterEqual(p._qa_pbo.skipped,3)
                self.assertEqual(p._qa_pbo.encoded,3)
                self.assertFalse(p.diagnostico()['integrado_ao_jogo'])
                self.assertEqual(p.readbacks,0)
            finally:
                p.close()
        finally:
            pygame.transform.set_smoothscale_backend(original_backend)
            pygame.quit()


if __name__=='__main__':
    unittest.main(verbosity=2)
