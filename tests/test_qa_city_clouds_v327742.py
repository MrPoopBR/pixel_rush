# -*- coding: utf-8 -*-
"""QA v3.277.42: clouds cached 48x33 == four original circles byte-for-byte."""
import os
import sys
import unittest
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame


class TestCityCloudQA742(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_cloudes_pre_render_paridade_clipping_e_vento(self):
        from pixelrush_city2_v3118 import CityPilotScene
        scene=CityPilotScene()
        original=pygame.draw.circle
        for flags in (0,pygame.SRCALPHA):
            for night in (0.,.2,.54,.55,.75,1.0):
                color=(245,238,231) if night<.55 else (109,105,150)
                for travel in (-500.,0.,.1,101.,1200.,100000.):
                    a=pygame.Surface((450,500),flags)
                    a.fill((18,28,60,129) if flags else (18,28,60))
                    b=a.copy()
                    for i in range(7):
                        cx=int((i*97+26-travel*.047)%(450+120))-50
                        cy=37+(i%3)*26
                        for dx,dy,r in ((0,0,15),(-12,5,10),(13,5,11),(4,-6,9)):
                            original(a,color,(cx+dx,cy+dy),r)
                        cache=scene._qa_cloud_sprite_cache
                        tile=cache.get(color)
                        if tile is None:
                            tile=pygame.Surface((48,33),pygame.SRCALPHA)
                            for dx,dy,r in ((0,0,15),(-12,5,10),(13,5,11),(4,-6,9)):
                                original(tile,color,(22+dx,15+dy),r)
                            cache[color]=tile
                        b.blit(tile,(cx-22,cy-15))
                    self.assertEqual(pygame.image.tobytes(a,'RGBA'),
                                     pygame.image.tobytes(b,'RGBA'),
                                     (flags,night,travel))
        self.assertEqual(len(scene._qa_cloud_sprite_cache),2)

    def test_draw_sky_reuso_identico_com_state_estatico(self):
        from pixelrush_city2_v3118 import CityPilotScene
        scene=CityPilotScene()
        for night in (0.,.53,.55,.87):
            for travel in (-50.,0.,700.):
                for flags in (0,pygame.SRCALPHA):
                    a=pygame.Surface((450,500),flags)
                    b=pygame.Surface((450,500),flags)
                    a.fill((12,11,21,129) if flags else (12,11,21))
                    b.fill((12,11,21,129) if flags else (12,11,21))
                    scene._draw_sky(a,travel,13,night,.5,'chuva')
                    scene._draw_sky(b,travel,13,night,.5,'chuva')
                    self.assertEqual(pygame.image.tobytes(a,'RGBA'),
                                     pygame.image.tobytes(b,'RGBA'),
                                     (night,travel,flags))
        self.assertLessEqual(len(scene._qa_cloud_sprite_cache),2)


if __name__=='__main__':
    unittest.main(verbosity=2)
