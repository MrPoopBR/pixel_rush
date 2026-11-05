# -*- coding: utf-8 -*-
"""R23: pombo C2 com quadros do atlas Premium, sem criar pixels por tick."""
import hashlib,os,random,sys,unittest
from pathlib import Path
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame
pygame.init()
pygame.display.set_mode((450,800))
from pixelrush_inimigos_v3221 import (
    AmeacaBioma,_ANIMACOES_VOO,_QUADROS,_CACHE_BYTES,MAX_CACHE_BYTES)

class PomboR23(unittest.TestCase):
    def test_atlas_completo_e_variedade_de_voo(self):
        random.seed(793)
        pombo=AmeacaBioma(460,"C2")
        self.assertIn("C2",_ANIMACOES_VOO)
        quadros=_ANIMACOES_VOO["C2"]
        self.assertGreaterEqual(len(quadros),6)
        self.assertEqual(len(quadros),
                         sum(len(fase) for fase in _QUADROS["C2"]))
        self.assertLessEqual(_CACHE_BYTES,MAX_CACHE_BYTES)
        ids={id(q) for q in quadros}
        observadas=[]
        offsets=[]
        for tick in range(130):
            pombo.update(6.3)
            observadas.append(id(pombo.image))
            offsets.append(pombo.rect.x-int(pombo._x))
            self.assertIn(id(pombo.image),ids)
        self.assertGreaterEqual(len(set(observadas)),6)
        self.assertGreater(max(offsets)-min(offsets),8)

    def test_velocidade_anima_sem_gastar_memoria_nova(self):
        random.seed(124)
        lento=AmeacaBioma(460,"C2")
        random.seed(124)
        rapido=AmeacaBioma(460,"C2")
        identidades={id(q) for q in _ANIMACOES_VOO["C2"]}
        for _ in range(75):
            lento.update(6.0)
            rapido.update(17.0)
        self.assertGreater(rapido._fase_voo,lento._fase_voo)
        self.assertIn(id(lento.image),identidades)
        self.assertIn(id(rapido.image),identidades)
        self.assertFalse(lento.image.get_locked())
        self.assertTrue(all(q.get_size()==lento.image.get_size()
                            for q in _ANIMACOES_VOO["C2"]))

if __name__=="__main__":
    unittest.main(verbosity=2)
