# -*- coding: utf-8 -*-
"""QA767: buffer SDF apos dano, inventario global e fallback RSS com SDL."""
import os,sys,types,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame
from pixelrush_qa_memory_budget_v327765 import inventariar
from pixelrush_qa_cache_trim_v327748 import EscalonadorTrimQA

class World:
    def __init__(self):
        self.biome='cidade';self.frame=200
        self.damage=SimpleNamespace(chunks={})
        self._qa_damage_layer=pygame.Surface((450,500),pygame.SRCALPHA)
        self._qa_damage_layer.fill((92,122,188,57))
        self._city_surfaces={}
        self.props_cache={};self.cache={};self.fx_cache={};self.normal_cache={}
        self.material_cache={};self.flow_cache={};self.geometry_cache={}
        self._qa_mirror_props={};self._qa_deform_buffers={}
        self.city2=None;self.modular={}

class DanoRAM767(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_inventario_inclui_dano_e_nao_duplicar_alias_rgba(self):
        w=World()
        w._city_surfaces[('geometry',False)]=w._qa_damage_layer
        memo=inventariar((w,))
        self.assertEqual(memo['surfaces_unicas'],1)
        self.assertEqual(memo['bytes'],450*500*4)
        self.assertFalse(memo['truncado'])

    def test_trim_so_apaga_buffer_sem_dano_ativo(self):
        a,b=World(),World()
        b.damage.chunks={'ativo':object()}
        original=b._qa_damage_layer
        t=EscalonadorTrimQA(limite_por_passo=1)
        self.assertTrue(t.iniciar((a,b),{},100,384,pressao_cache=True))
        for _ in range(100):
            if not t.ativo:break
            t.passo()
        self.assertFalse(t.ativo)
        self.assertIsNone(a._qa_damage_layer)
        self.assertIs(b._qa_damage_layer,original)
        self.assertGreaterEqual(t.removidos,1)
        # Somente apos cessar SDF a segunda cena pode descartar.
        b.damage.chunks.clear()
        t.iniciar((b,),{},100,384,pressao_cache=True)
        for _ in range(40):
            if not t.ativo:break
            t.passo()
        self.assertIsNone(b._qa_damage_layer)

    def test_fallback_rss_preserva_dano_ativo_e_libera_inerte(self):
        import pixelrush_qa_performance_integrated_v327742 as perf
        a,b=World(),World()
        b.damage.chunks={'ativo':object()}
        original=b._qa_damage_layer
        source=types.ModuleType('pixelrush_world_v3130')
        source._SOURCE={}
        budget=perf._LAST_STATUS['cache_budget_mib']
        perf._LAST_STATUS['cache_budget_mib']=384
        perf._WORLDS.add(a);perf._WORLDS.add(b)
        try:
            with patch.object(perf,'_memory_mib',return_value=900),\
                 patch.dict(sys.modules,{'pixelrush_world_v3130':source}):
                perf._reclaim_inactive_caches()
            self.assertIsNone(a._qa_damage_layer)
            self.assertIs(b._qa_damage_layer,original)
        finally:
            perf._WORLDS.discard(a);perf._WORLDS.discard(b)
            perf._LAST_STATUS['cache_budget_mib']=budget

if __name__=='__main__':
    unittest.main(verbosity=2)
