# -*- coding: utf-8 -*-
"""QA761 — céu REAL inteiro com cache de nuvens vs desenho original, RGBA."""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import pygame
import pixelrush_cenarios_v398 as sky
import pixelrush_qa_scene_v327733 as qa


class SkyRGBA761(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))
        qa.instalar()

    @classmethod
    def tearDownClass(cls):
        qa.restaurar_para_teste()
        pygame.quit()

    def test_ceu_integral_sete_biomas_alfa_noite_nuvens(self):
        original=qa._ORIGINAIS['nuvem_pixel']
        fast=sky.nuvem_pixel
        draw=qa._ORIGINAIS['desenhar_ceu']
        biomas=('cidade','neve','deserto','vulcao','floresta',
                'cidade_futurista','ilhas_celestes')
        nuvens=[{'x':float(x),'y':float(y)} for x,y in
                ((0,45),(55,85),(120,60),(240,25),(402,140),(-24,175))]
        estrelas=[{'x':x,'y':y,'blink':.12*(i+1),'offset':.23*i}
                  for i,(x,y) in enumerate(((10,12),(120,96),(234,131),(309,220)))]
        try:
            for biome in biomas:
                for fase in (.03,.15,.42,.77):
                    for noite in (0.,.31,.92):
                        for alpha in (False,True):
                            flags=pygame.SRCALPHA if alpha else 0
                            a=pygame.Surface((450,800),flags)
                            b=pygame.Surface((450,800),flags)
                            a.fill((97,45,119,0))
                            b.fill((97,45,119,0))
                            try:
                                sky.nuvem_pixel=original
                                draw(a,(35,88,155),fase,noite,biome,
                                     estrelas,447.5,nuvens)
                                sky.nuvem_pixel=fast
                                draw(b,(35,88,155),fase,noite,biome,
                                     estrelas,447.5,nuvens)
                            finally:
                                sky.nuvem_pixel=fast
                            self.assertEqual(
                                pygame.image.tobytes(a,'RGBA'),
                                pygame.image.tobytes(b,'RGBA'),
                                (biome,fase,noite,alpha))
            status=qa.diagnostico_nuvens()
            self.assertGreater(status['blits_rgb'],0)
            self.assertGreater(status['fallback_rgba'],0)
        finally:
            sky.nuvem_pixel=fast


if __name__=='__main__':
    unittest.main(verbosity=2)
