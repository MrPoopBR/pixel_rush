# -*- coding: utf-8 -*-
"""QA758: integração offline de política RSS/GC; sem compilar Android."""
import gc
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
from pixelrush_qa_cache_policy_v327758 import mapa_tecnico_quente
from pixelrush_qa_cache_trim_v327748 import EscalonadorTrimQA

class MundoFalso:
    def __init__(self,biome,frame):
        self.biome=biome
        self.frame=frame
        self.props_cache={}
        self.cache={};self.fx_cache={};self.normal_cache={}
        self.material_cache={};self.flow_cache={};self.geometry_cache={}
        self._qa_mirror_props={};self._qa_deform_buffers={}
        self.city2=None
        self._city_surfaces={}
        self._qa_surface_last_used={}

class CacheGC758(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def mundos(self):
        a,b=MundoFalso('cidade',240),MundoFalso('neve',240)
        for w in (a,b):
            for kind in ('geometry','normal','flow','fxmask'):
                key=(kind,False)
                surf=pygame.Surface((450,500),pygame.SRCALPHA)
                surf.fill((18,45,111,0))
                pygame.draw.rect(surf,(203,12,73,137),(5,10,12,18))
                w._city_surfaces[key]=surf
                w._qa_surface_last_used[key]=(w.biome,239 if kind=='geometry' else 2)
        return a,b

    def test_politica_por_mundo_e_rgba(self):
        a,b=self.mundos()
        marker=('geometry',False)
        first=pygame.image.tobytes(a._city_surfaces[marker],'RGBA')
        self.assertTrue(mapa_tecnico_quente(a,marker))
        self.assertTrue(mapa_tecnico_quente(b,marker))
        self.assertFalse(mapa_tecnico_quente(a,('normal',False)))
        self.assertEqual(first,pygame.image.tobytes(a._city_surfaces[marker],'RGBA'))
        a._qa_surface_last_used.pop(marker)
        self.assertTrue(mapa_tecnico_quente(a,marker))
        self.assertFalse(mapa_tecnico_quente(a,('image',False)))

    def test_escalonador_respeita_mapas_quentes(self):
        a,b=self.mundos()
        source={'cidade':1,'neve':2,'deserto':3}
        t=EscalonadorTrimQA(limite_por_passo=2)
        self.assertTrue(t.iniciar((a,b),source,900,384))
        for _ in range(300):
            if not t.ativo:break
            t.passo()
        self.assertFalse(t.ativo)
        for w in (a,b):
            self.assertIn(('geometry',False),w._city_surfaces)
            self.assertNotIn(('normal',False),w._city_surfaces)
        self.assertEqual(source,{'cidade':1,'neve':2})

    def test_fallback_rss_nao_descarta_ativos(self):
        import pixelrush_qa_performance_integrated_v327742 as perf
        a,b=self.mundos()
        fake=types.ModuleType('pixelrush_world_v3130')
        fake._SOURCE={'cidade':1,'neve':2,'deserto':3}
        perf._WORLDS.add(a);perf._WORLDS.add(b)
        oldbudget=perf._LAST_STATUS['cache_budget_mib']
        perf._LAST_STATUS['cache_budget_mib']=384
        try:
            with patch.dict(sys.modules,{'pixelrush_world_v3130':fake}),patch.object(perf,'_memory_mib',return_value=900):
                perf._reclaim_inactive_caches()
            for w in (a,b):
                self.assertIn(('geometry',False),w._city_surfaces)
                self.assertNotIn(('normal',False),w._city_surfaces)
            self.assertEqual(fake._SOURCE,{'cidade':1,'neve':2})
        finally:
            perf._WORLDS.clear()
            perf._LAST_STATUS['cache_budget_mib']=oldbudget

    def test_gc_sem_geracoes_sobrepostas_em_901_flips(self):
        import pixelrush_qa_gc_cooperativo_v327757 as qa
        original=pygame.display.flip
        enabled=gc.isenabled()
        with patch.dict(os.environ,{'PIXELRUSH_QA_ANDROID':'1','PIXELRUSH_QA_GC_COOPERATIVO':'1'}):
            if not enabled:gc.enable()
            qa.instalar()
            try:
                with patch.object(qa.gc,'collect',wraps=gc.collect) as collect:
                    for _ in range(901):pygame.display.flip()
                self.assertEqual(collect.call_count,30)
                self.assertEqual([qa.diagnostico()[x] for x in ('coletas_0','coletas_1','coletas_2')],[25,4,1])
                self.assertEqual(qa.diagnostico()['coletas_no_quinto_quadro'],0)
            finally:
                qa.restaurar_para_teste()
                if not enabled:gc.disable()
        self.assertIs(pygame.display.flip,original)
        self.assertEqual(gc.isenabled(),enabled)

if __name__=='__main__':
    unittest.main(verbosity=2)
