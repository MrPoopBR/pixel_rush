# -*- coding: utf-8 -*-
"""QA762 — trim frio modular, active guard, fallback e Desert real RGBA."""
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import pygame
from pixelrush_qa_cache_policy_v327758 import modular_cache_fria
from pixelrush_qa_cache_trim_v327748 import EscalonadorTrimQA


class SceneFalsa:
    def __init__(self):
        def nova():
            dst=pygame.Surface((225,250),pygame.SRCALPHA)
            dst.fill((41,77,116,137))
            return dst
        self._maps={'normal':nova(),'geometry':nova()}
        self._composites={'image':nova()}
        self._night_tiles={'day':nova(),'night':nova()}
        self._layers={'far':[]}


class WorldFalso:
    def __init__(self,active='cidade'):
        self.biome=active
        self.frame=240
        self.city2=None
        self._city_surfaces={}
        self.props_cache={}
        self.cache={};self.fx_cache={};self.normal_cache={}
        self.material_cache={};self.flow_cache={};self.geometry_cache={}
        self._qa_mirror_props={};self._qa_deform_buffers={}
        self.modular={'neve':SceneFalsa(),'deserto':SceneFalsa()}


class CacheModular762(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_conserva_prebake_neve_e_libera_3_caches_deserto(self):
        w=WorldFalso()
        self.assertFalse(modular_cache_fria(w,'neve','_night_tiles'))
        self.assertTrue(modular_cache_fria(w,'neve','_maps'))
        self.assertTrue(modular_cache_fria(w,'deserto','_night_tiles'))
        t=EscalonadorTrimQA(limite_por_passo=3)
        self.assertTrue(t.iniciar((w,),{},900,384))
        for _ in range(100):
            if not t.ativo:
                break
            t.passo()
        self.assertFalse(t.ativo)
        snow=w.modular['neve'];desert=w.modular['deserto']
        self.assertFalse(snow._maps)
        self.assertFalse(snow._composites)
        self.assertTrue(snow._night_tiles)
        self.assertFalse(desert._maps)
        self.assertFalse(desert._composites)
        self.assertFalse(desert._night_tiles)

    def test_troca_para_neve_antes_de_aplicar_preserva_bioma_ativo(self):
        w=WorldFalso()
        snow=w.modular['neve']
        oldmap=snow._maps['geometry']
        trim=EscalonadorTrimQA(limite_por_passo=1)
        self.assertTrue(trim.iniciar((w,),{},999,384))
        w.biome='neve'
        for _ in range(120):
            if not trim.ativo:
                break
            trim.passo()
        self.assertFalse(trim.ativo)
        self.assertIs(snow._maps['geometry'],oldmap)
        self.assertTrue(snow._composites)
        self.assertTrue(snow._night_tiles)
        self.assertFalse(w.modular['deserto']._maps)

    def test_fallback_sob_rss_preserva_prebake_e_ativos(self):
        import pixelrush_qa_performance_integrated_v327742 as perf
        w=WorldFalso('neve')
        source=types.ModuleType('pixelrush_world_v3130')
        source._SOURCE={}
        oldbudget=perf._LAST_STATUS['cache_budget_mib']
        perf._LAST_STATUS['cache_budget_mib']=384
        perf._WORLDS.add(w)
        try:
            with patch.object(perf,'_memory_mib',return_value=900),\
                 patch.dict(sys.modules,{'pixelrush_world_v3130':source}):
                perf._reclaim_inactive_caches()
            self.assertTrue(w.modular['neve']._maps)
            self.assertTrue(w.modular['neve']._night_tiles)
            self.assertFalse(w.modular['deserto']._maps)
            self.assertFalse(w.modular['deserto']._night_tiles)
        finally:
            perf._WORLDS.discard(w)
            perf._LAST_STATUS['cache_budget_mib']=oldbudget

    def test_deserto_real_cores_rgba_iguais_antes_e_depois_eviction(self):
        from pixelrush_biomes2_v3130 import ModularBiomeScene
        scene=ModularBiomeScene('deserto')
        w=WorldFalso()
        w.modular={'deserto':scene}
        expected=[]
        for kind in ('image','geometry','material'):
            dst=pygame.Surface((450,500),pygame.SRCALPHA)
            scene.render_scene(dst,211.0,55,.41,'areia',.53,map_kind=kind)
            expected.append(pygame.image.tobytes(dst,'RGBA'))
        self.assertTrue(scene._maps)
        self.assertTrue(scene._night_tiles)
        self.assertTrue(scene._composites)
        trim=EscalonadorTrimQA(limite_por_passo=12)
        self.assertTrue(trim.iniciar((w,),{},900,384))
        for _ in range(500):
            if not trim.ativo: break
            trim.passo()
        self.assertFalse(trim.ativo)
        self.assertFalse(scene._maps)
        self.assertFalse(scene._night_tiles)
        self.assertFalse(scene._composites)
        for kind,reference in zip(('image','geometry','material'),expected):
            dst=pygame.Surface((450,500),pygame.SRCALPHA)
            scene.render_scene(dst,211.0,55,.41,'areia',.53,map_kind=kind)
            self.assertEqual(reference,pygame.image.tobytes(dst,'RGBA'),kind)


if __name__=='__main__':
    unittest.main(verbosity=2)
