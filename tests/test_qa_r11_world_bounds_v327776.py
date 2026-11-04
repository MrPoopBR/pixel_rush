# -*- coding: utf-8 -*-
"""QA776: helper RGB16 do mundo e LivingWorld City real em todos formatos."""
import os, random, unittest
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ['PIXELRUSH_QA_ANDROID']='1'
import pygame
from pixelrush_world_v3130 import LivingWorld
from pixelrush_qa_city_bootstrap_v327759 import instalar as bootstrap
from pixelrush_qa_city_bootstrap_v327759 import restaurar_para_teste as fim_boot
import pixelrush_qa_r11_world_bounds_v327776 as qa
def rgba(s): return pygame.image.tobytes(s,'RGBA')

class WorldBBoxQA776(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800));bootstrap()
    @classmethod
    def tearDownClass(cls):
        fim_boot();pygame.quit()

    def test_synthetic_rgba_hidden_e_bpp_com_rollback(self):
        rng=random.Random(327776)
        for alpha in (0,1,99,255):
            src=pygame.Surface((450,500),pygame.SRCALPHA,32)
            src.fill((91,47,158,0))
            for i in range(40):
                x=rng.randrange(450);y=rng.randrange(110,495)
                pygame.draw.rect(src,
                    (rng.randrange(256),rng.randrange(256),rng.randrange(256),
                     rng.choice((0,1,63,151,255))),(x,y,17,9))
            for flags,bpp in ((0,16),(0,24),(0,32),(pygame.SRCALPHA,32)):
                dst=pygame.Surface((450,800),flags,bpp)
                dst.fill((15,91,159,alpha) if flags else (15,91,159))
                orig=dst.copy();out=dst.copy()
                orig.blit(src,(0,230))
                qa.compor(out,src,230)
                self.assertEqual(rgba(orig),rgba(out),(flags,bpp,alpha))
        self.assertGreater(qa.diagnostico()['recortes_rgb16'],0)

    def test_cidade_real_clima_noite_bioma_qualidade(self):
        rng=random.getstate()
        world=LivingWorld('cidade')
        for quality in (False,True):
            world.lightweight=quality
            for night,climate,phase in ((0.,'limpo',.5),(.6,'chuva',.7),
                                        (1.,'tempestade',.12)):
                world.update(6.,night,climate,phase)
                for flags,bpp in ((0,16),(0,24),(0,32),(pygame.SRCALPHA,32)):
                    before=pygame.Surface((450,800),flags,bpp)
                    before.fill((97,29,101,0) if flags else (97,29,101))
                    after=before.copy()
                    with patch.dict(os.environ,{'PIXELRUSH_QA_R11_WORLD_BBOX':'0'}):
                        world.draw(before)
                    with patch.dict(os.environ,{'PIXELRUSH_QA_R11_WORLD_BBOX':'1'}):
                        world.draw(after)
                    self.assertEqual(rgba(before),rgba(after),
                                     (quality,night,climate,flags,bpp))
        self.assertEqual(random.getstate(),rng)
        diag=qa.diagnostico()
        self.assertGreater(diag['recortes_rgb16'],0)
        self.assertGreater(diag['originais'],0)

    def test_outro_bioma_nao_usa_atalho(self):
        from pixelrush_world_v3130 import _qa_r11_compor_city
        self.assertIs(_qa_r11_compor_city,qa.compor)
        # AST do ramo de render do outro bioma preserva o blit original.
        from pathlib import Path
        src=Path(__file__).resolve().parents[1]/'pixelrush_world_v3130.py'
        texto=src.read_text('utf8')
        self.assertIn("if self.biome=='cidade' and _qa_r11_compor_city is not None:",texto)
        self.assertIn("surface.blit(layer,(0,TOP))",texto)

if __name__=='__main__':unittest.main(verbosity=2)
