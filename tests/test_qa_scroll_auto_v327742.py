# -*- coding: utf-8 -*-
"""QA 3.277.42: scroll 2.5D integrado - pixel exato e fallback por benchmark."""
import os
import sys
import unittest
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame


def rgba(s):return pygame.image.tobytes(s,'RGBA')


class ScrollIntegrationQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_draw_reference_equivale_world_strip(self):
        from pixelrush_world_v3130 import LivingWorld
        from pixelrush_qa_scroll_auto_v327742 import _draw_reference
        class C:
            offset=0
            def _scroll(self):return self.offset
        world=C()
        for flags in (0,pygame.SRCALPHA):
            for period in (173,450,900,1800):
                tex=pygame.Surface((period,500),pygame.SRCALPHA)
                for y in range(500):
                    rgba_color=((y*11)%256,(y*3)%256,(y*17)%256,(y*23)%256)
                    pygame.draw.line(tex,rgba_color,(0,y),(period-1,y))
                for offset in (-1307,-7,0,1,71,period-1,period+9):
                    world.offset=offset
                    a=pygame.Surface((450,800),flags)
                    a.fill((31,55,95,190) if flags else (31,55,95))
                    b=a.copy()
                    LivingWorld._blit_strip(world,a,tex)
                    _draw_reference(b,tex,offset%period)
                    self.assertEqual(rgba(a),rgba(b),
                                     (flags,period,offset))

    def test_auto_benchmark_nao_habilita_pixel_diferente(self):
        from pixelrush_qa_scroll_auto_v327742 import _bench
        tex=pygame.Surface((900,500),pygame.SRCALPHA)
        for y in range(500):
            pygame.draw.line(tex,(y*3%256,y*7%256,y*11%256,y*13%256),
                             (0,y),(899,y))
        for flags in (0,pygame.SRCALPHA):
            frame=pygame.Surface((450,800),flags)
            frame.fill((20,45,70,110) if flags else (20,45,70))
            active,measurement,reason=_bench(tex,frame)
            if active:
                self.assertEqual(measurement['pixels_testados'],16)
                self.assertGreaterEqual(measurement['ratio'],1.20)
            else:
                self.assertIn(reason,('pixels_diferentes','mais_lento'))
        active,_,reason=_bench(
            pygame.Surface((450,400),pygame.SRCALPHA),
            pygame.Surface((450,800)))
        self.assertFalse(active)
        self.assertEqual(reason,'formato_nao_suportado')


if __name__=='__main__':
    unittest.main(verbosity=2)
