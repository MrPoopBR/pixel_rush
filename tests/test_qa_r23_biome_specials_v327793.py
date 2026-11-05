# -*- coding: utf-8 -*-
"""QA793 R23: seis ameaças, cache de atlas, RGBA e barreiras de integridade."""
import ast
import hashlib
import os
from pathlib import Path
import sys
import unittest
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame
pygame.init()
pygame.display.set_mode((450,800))
from src.pixelrush.entities.enemies.biome_specials_v327793 import (
    ESPECIAIS_BIOMA,InimigoEspecialBioma,_FRAMES,memoria_atlas_bytes
)

class AtoresBiomaR23(unittest.TestCase):
    def test_seis_especies_poses_rgba_arte_propria(self):
        self.assertEqual(set(ESPECIAIS_BIOMA),
                         {"cidade","deserto","vulcao","floresta",
                          "cidade_futurista","ilhas_celestes"})
        hashes=set()
        for biome,(codigo,nome) in ESPECIAIS_BIOMA.items():
            with self.subTest(biome=biome):
                s=InimigoEspecialBioma(550,biome)
                self.assertEqual(s.codigo,codigo)
                self.assertEqual(s.nome,nome)
                self.assertEqual(s.bioma,biome)
                self.assertEqual(s.rect.bottom,730)
                self.assertTrue(s._hitboxes_precisas_v342)
                self.assertTrue(all(pygame.Rect((0,0),s.rect.size).contains(x)
                                    for x in s._hitboxes_precisas_v342))
                frames=_FRAMES[biome]
                self.assertEqual(len(frames),3)
                self.assertEqual(len({id(x) for x in frames}),3)
                self.assertEqual(len({pygame.image.tobytes(x,"RGBA")
                                      for x in frames})>1,True)
                for frame in frames:
                    self.assertEqual(frame.get_size(),(58,56))
                    self.assertTrue(frame.get_flags()&pygame.SRCALPHA)
                    self.assertIsNone(frame.get_colorkey())
                    self.assertGreater(frame.get_bounding_rect().width,30)
                    self.assertGreater(frame.get_bounding_rect().height,20)
                hashes.add(hashlib.sha256(pygame.image.tobytes(frames[1],"RGBA")).digest())
        self.assertEqual(len(hashes),6)
        self.assertLessEqual(memoria_atlas_bytes(),6*3*58*56*4)

    def test_sem_superficies_por_frame_e_comportamento_limitado(self):
        for biome in ESPECIAIS_BIOMA:
            first=InimigoEspecialBioma(530,biome)
            another=InimigoEspecialBioma(590,biome)
            self.assertIs(first.image,another.image)
            frame_bytes=memoria_atlas_bytes()
            original=first.rect.copy()
            quadros=_FRAMES[biome]
            for i in range(160):
                first.update(6.0)
                self.assertTrue(first.image is quadros[i//8%3])
                self.assertLessEqual(abs(first.rect.y-original.y),7)
            self.assertLess(first.rect.x,original.x-300)
            self.assertEqual(memoria_atlas_bytes(),frame_bytes)
            self.assertEqual(first.codigo,ESPECIAIS_BIOMA[biome][0])

    def test_no_engine_somente_bioma_local_e_depois_de_750m(self):
        engine=(ROOT/"PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py").read_text("utf8")
        ast.parse(engine)
        self.assertIn("metros >= 750 and cenario in ESPECIAIS_BIOMA",engine)
        self.assertIn('elif tipo_obs == "especial_bioma" and cenario in ESPECIAIS_BIOMA:',engine)
        self.assertIn("InimigoEspecialBioma(x_inicial, cenario)",engine)
        self.assertNotIn("InimigoEspecialBioma(x_inicial, 'neve')",engine)

if __name__=="__main__":
    unittest.main(verbosity=2)
