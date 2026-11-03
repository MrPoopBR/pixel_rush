# -*- coding: utf-8 -*-
"""QA759: integração do caminho main->render QA->LivingWorld real, sem Android."""
import os, sys, statistics, time, unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import pygame
import pixelrush_qa_render_v327729 as qa

def rgba(surface):
    return pygame.image.tobytes(surface,'RGBA')

class CaminhoRealWorld759(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))
        # Instala os mesmos hooks do main QA (sem iniciar engine/Android).
        cls.env=patch.dict(os.environ, {
            'PIXELRUSH_QA_ANDROID':'0',
            'PIXELRUSH_QA_ATLAS_IO_PREWARM':'0',
            'PIXELRUSH_QA_GEOMETRY_BORROW':'1',
            'PIXELRUSH_QA_GLES_BRIDGE':'0',
            'PIXELRUSH_QA_CITY_INCREMENTAL':'0',
            'PIXELRUSH_QA_CLASSIC_INCREMENTAL':'0'})
        cls.env.start()
        qa.instalar()

    @classmethod
    def tearDownClass(cls):
        qa.restaurar_para_teste()
        cls.env.stop()
        pygame.quit()

    def test_world_multiinstancia_emprestimo_memo_e_troca_bioma(self):
        from pixelrush_world_v3130 import LivingWorld
        before_borrow=qa._QA_BORROW_GEOMETRY
        before_memo=qa._QA_TECH_SAME_FRAME
        try:
            qa._QA_TECH_SAME_FRAME=False
            qa._QA_BORROW_GEOMETRY=False
            w1=LivingWorld('cidade',lightweight=False)
            w2=LivingWorld('cidade',lightweight=True)
            for world in (w1,w2):
                self.assertTrue(hasattr(world.city2,'_qa_uniform_tech'))
                original=world._city_surface('geometry')
                raw=rgba(original)
                ao=world.ambient_occlusion(125,70,460,615)
                self.assertIsNot(world.city2._geometry_view,original)
                qa._QA_BORROW_GEOMETRY=True
                borrowed=world._city_surface('geometry')
                self.assertIs(world.city2._geometry_view,borrowed)
                self.assertIs(borrowed,world._city_surfaces[('geometry',False)])
                self.assertEqual(raw,rgba(borrowed))
                self.assertEqual(ao,world.ambient_occlusion(125,70,460,615))
                qa._QA_BORROW_GEOMETRY=False
            self.assertIsNot(w1.city2,w2.city2)
            qa._QA_BORROW_GEOMETRY=True
            qa._QA_TECH_SAME_FRAME=True
            for world in (w1,w2):
                world.frame+=1
                first=world._city_surface('geometry')
                second=world._city_surface('geometry')
                self.assertIs(first,second)
                self.assertIs(first,world.city2._geometry_view)
            self.assertIsNot(w1._city_surfaces[('geometry',False)],
                             w2._city_surfaces[('geometry',False)])
            previous=w1._city_surfaces[('geometry',False)]
            w1.switch('neve')
            self.assertEqual(w1.biome,'neve')
            self.assertFalse(w1._city_surfaces)
            fresh=w1._city_surface('geometry')
            self.assertIsNot(fresh,previous)
            self.assertIs(w1._get_modular()._geometry_view,fresh)
        finally:
            qa._QA_BORROW_GEOMETRY=before_borrow
            qa._QA_TECH_SAME_FRAME=before_memo

    def test_micromedida_geometry_sem_homologacao(self):
        from pixelrush_world_v3130 import LivingWorld
        world=LivingWorld('cidade')
        before_borrow=qa._QA_BORROW_GEOMETRY
        before_memo=qa._QA_TECH_SAME_FRAME
        try:
            qa._QA_TECH_SAME_FRAME=False
            amostras={}
            for enabled in (False,True):
                qa._QA_BORROW_GEOMETRY=enabled
                for _ in range(2):
                    world._city_surface('geometry')
                values=[]
                for _ in range(15):
                    start=time.perf_counter_ns()
                    world._city_surface('geometry')
                    values.append((time.perf_counter_ns()-start)/1e6)
                amostras['borrow' if enabled else 'snapshot']=statistics.median(values)
            # Apenas evidência de um host CI, não garantia de ganho Android.
            print('BENCH_GEOMETRY_OFFLINE_MS',amostras)
            self.assertGreater(amostras['snapshot'],0)
            self.assertGreater(amostras['borrow'],0)
            self.assertIs(world.city2._geometry_view,
                          world._city_surfaces[('geometry',False)])
        finally:
            qa._QA_BORROW_GEOMETRY=before_borrow
            qa._QA_TECH_SAME_FRAME=before_memo

if __name__=='__main__':
    unittest.main(verbosity=2)
