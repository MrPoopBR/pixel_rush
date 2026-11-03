# -*- coding: utf-8 -*-
"""QA v3.277.42: batching/culling do motor modular, pixel-exato RGB/RGBA."""
import os
import sys
import unittest
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame


class TestModularBatchQA742(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_modular_biomas_batch_byte_igual_blit_sequencial(self):
        from pixelrush_biomes2_v3126 import ModularBiomeScene,LW,LH
        for flags in (0,pygame.SRCALPHA):
            scene=ModularBiomeScene.__new__(ModularBiomeScene)
            layers={}
            for n,name in enumerate(('far','mid','near')):
                tiles=[]
                for i in range(4):
                    s=pygame.Surface((LW,LH),pygame.SRCALPHA)
                    for y in range(LH):
                        col=(((y*9+n*37+i*11)%256),
                             ((y*23+n*19+i*17)%256),
                             ((y*3+n*61+i*29)%256),
                             (y*7+n*17+i*13)%256)
                        pygame.draw.line(s,col,(0,y),(LW-1,y))
                    tiles.append(s)
                layers[name]=tiles
            scene._layers=layers
            scene._tile_map=lambda layer,idx,kind:scene._layers[layer][idx]
            for travel in (0,1,25,115,475,1499,10001,135000):
                for layer in ('far','mid','near'):
                    for kind in ('image','normal'):
                        a=pygame.Surface((LW,LH),flags)
                        a.fill((15,30,89,149) if flags else (15,30,89))
                        b=a.copy()
                        factor={'far':.12,'mid':.28,'near':.52}[layer]
                        off=max(0.,travel)*factor*.5
                        first=int(off//LW)
                        shift=int(off%LW)
                        for j in range(2):
                            variant=(first+j)%len(layers[layer])
                            tile=scene._tile_map(layer,variant,kind)
                            a.blit(tile,(j*LW-shift,0))
                        scene._draw_layer(b,layer,travel,kind)
                        self.assertEqual(
                           pygame.image.tobytes(a,'RGBA'),
                           pygame.image.tobytes(b,'RGBA'),
                           (flags,travel,layer,kind))
            self.assertEqual(len(layers),3)


if __name__=='__main__':
    unittest.main(verbosity=2)
