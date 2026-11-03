# -*- coding: utf-8 -*-
"""QA 757: culling modular real, pixel-exato para SRCALPHA, sem assets."""

import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame
from pixelrush_biomes2_v3128 import ModularBiomeScene as Neve, DEPTH, LW, LH
from pixelrush_biomes2_v3130 import ModularBiomeScene as Deserto, COUNTS


def raw(s):
    return pygame.image.tobytes(s,'RGBA')


class CullingModular757(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_culling_do_tile_100_por_cento_invisivel(self):
        for biome,klass in (('neve',Neve),('deserto',Deserto)):
            for layer in DEPTH:
                for kind in ('image','geometry','normal','flow','fxmask'):
                    count=COUNTS[layer] if biome=='deserto' else 4
                    textured=[]
                    for i in range(count):
                        tile=pygame.Surface((LW,LH),pygame.SRCALPHA,32)
                        tile.fill(((i*73+19)%256,(i*61+37)%256,
                                   (i*41+111)%256,(i*31+5)%256))
                        pygame.draw.line(tile,(200,11,77,0),(0,i%LH),(LW-1,i%LH))
                        textured.append(tile)
                    calls=[]
                    def tile_at(layer_name,idx,kind_name):
                        calls.append(idx)
                        return textured[idx]
                    mock=SimpleNamespace(biome=biome,_tile_map=tile_at)
                    stride={'far':5,'mid':7,'near':9}[layer] if biome=='deserto' else 1
                    for travel in (0,1,31,100,367,1603):
                        offset=max(0.,travel)*DEPTH[layer][0]*.5
                        first=int(offset//LW);shift=int(offset%LW)
                        prev=pygame.Surface((LW,LH),pygame.SRCALPHA,32)
                        prev.fill((14,26,71,0))
                        current=prev.copy()
                        for j in range(2):
                            idx=((first+j)*stride)%count
                            prev.blit(textured[idx],(j*LW-shift,0))
                        calls.clear()
                        klass._draw_layer(mock,current,layer,travel,kind)
                        self.assertEqual(raw(prev),raw(current),
                                         (biome,layer,kind,travel))
                        self.assertEqual(len(calls),1 if shift==0 else 2,
                                         ('chamadas tile',biome,layer,travel))


if __name__=='__main__':
    unittest.main(verbosity=2)
