# -*- coding: utf-8 -*-
"""QA761 — Live LivingWorld geometry 2.5D, destroca e liberacao weakref."""
import gc
import os
import sys
import unittest
import weakref
from pathlib import Path

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame
import pixelrush_qa_render_v327729 as render


class Retire761(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))
        render.instalar()
    @classmethod
    def tearDownClass(cls):
        render.restaurar_para_teste()
        pygame.quit()

    def test_troca_cidade_neve_cidade_libera_aliased_sem_mudar_rgba(self):
        from pixelrush_world_v3130 import LivingWorld
        from pixelrush_qa_geometry_retire_v327761 import diagnostico
        mundo=LivingWorld('cidade')
        city=mundo.city2
        img=mundo._city_surface('geometry')
        self.assertIs(city._geometry_view,img)
        referencia=weakref.ref(img)
        antes=pygame.image.tobytes(img,'RGBA')
        ao_antes=mundo.ambient_occlusion(130,80,440,580)
        del img
        mundo.switch('neve')
        self.assertEqual(mundo.biome,'neve')
        self.assertIsNone(city._geometry_view)
        self.assertIsNone(getattr(city,'_qa_geometry_borrowed_surface',None))
        gc.collect()
        self.assertIsNone(referencia())
        self.assertGreaterEqual(diagnostico()['aliases_aposentados'],1)
        snow=mundo._city_surface('geometry')
        snow_scene=mundo._get_modular()
        self.assertIs(snow_scene._geometry_view,snow)
        snow_ref=weakref.ref(snow)
        del snow
        mundo.switch('cidade')
        self.assertIsNone(snow_scene._geometry_view)
        gc.collect()
        self.assertIsNone(snow_ref())
        novo=mundo._city_surface('geometry')
        self.assertEqual(antes,pygame.image.tobytes(novo,'RGBA'))
        self.assertEqual(ao_antes,mundo.ambient_occlusion(130,80,440,580))

    def test_sem_emprestimo_nao_destroi_snapshot_da_cena(self):
        import pixelrush_qa_geometry_retire_v327761 as retire
        from pixelrush_world_v3130 import LivingWorld
        antigo=render._QA_BORROW_GEOMETRY
        try:
            render._QA_BORROW_GEOMETRY=False
            w=LivingWorld('cidade')
            original=w._city_surface('geometry')
            snapshot=w.city2._geometry_view
            self.assertIsNot(snapshot,original)
            raw=pygame.image.tobytes(snapshot,'RGBA')
            before=retire.diagnostico()['outros_preservados']
            w.switch('neve')
            self.assertIs(w.city2._geometry_view,snapshot)
            self.assertEqual(raw,pygame.image.tobytes(snapshot,'RGBA'))
            self.assertGreater(retire.diagnostico()['outros_preservados'],before)
        finally:
            render._QA_BORROW_GEOMETRY=antigo

    def test_mesmo_bioma_nao_limpa_geometry(self):
        from pixelrush_world_v3130 import LivingWorld
        w=LivingWorld('cidade')
        target=w._city_surface('geometry')
        w.switch('cidade')
        self.assertIs(w.city2._geometry_view,target)


if __name__=='__main__':
    unittest.main(verbosity=2)
