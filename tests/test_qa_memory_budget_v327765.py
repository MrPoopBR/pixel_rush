# -*- coding: utf-8 -*-
"""QA765 — memoria agregada SDL sem duplicar aliases nem expulsar caches ativos."""
import os,sys,unittest
from pathlib import Path
from types import SimpleNamespace
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame
from pixelrush_qa_memory_budget_v327765 import inventariar,cache_em_pressao
from pixelrush_qa_cache_trim_v327748 import EscalonadorTrimQA

class World:
    def __init__(self):
        self.biome='cidade';self.frame=210
        self.city2=SimpleNamespace(_scaled={},_night_veils={},_qa_cloud_sprite_cache={})
        self._city_surfaces={};self.modular={}
        self.props_cache={};self.cache={};self.fx_cache={}
        self.normal_cache={};self.material_cache={}
        self.flow_cache={};self.geometry_cache={}
        self._qa_mirror_props={};self._qa_deform_buffers={}

class MemoryBudget765(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_uma_surface_compartilhada_conta_uma_vez_em_tres_mundos(self):
        surf=pygame.Surface((225,250),pygame.SRCALPHA)
        a=World();b=World();c=World()
        for w in (a,b,c):
            w.cache['cidade']=surf
            w._city_surfaces[('geometry',False)]=surf
            w.city2._scaled['sprite']=surf
        r=inventariar((a,b,c),fonte={'cidade':surf})
        self.assertEqual(r['surfaces_unicas'],1)
        self.assertEqual(r['bytes'],surf.get_pitch()*surf.get_height())
        self.assertFalse(r['truncado'])
        self.assertFalse(cache_em_pressao(r,1.0))

    def test_pressao_do_cache_independe_do_rss_sem_remover_ativo(self):
        w=World()
        quente=pygame.Surface((450,500),pygame.SRCALPHA)
        fria=pygame.Surface((450,500),pygame.SRCALPHA)
        w.props_cache[('cidade','sprite')]=quente
        w.props_cache[('neve','sprite')]=fria
        w.modular={'deserto':SimpleNamespace(_maps={'x':fria},_composites={},
                                           _night_tiles={})}
        inventario=inventariar((w,))
        self.assertEqual(inventario['surfaces_unicas'],2)
        self.assertTrue(cache_em_pressao(inventario,.5))
        t=EscalonadorTrimQA(limite_por_passo=2)
        # RSS abaixo do teto; orcamento agregado aciona limpeza somente fria.
        self.assertFalse(t.iniciar((w,),{},100,384))
        self.assertTrue(t.iniciar((w,),{},100,384,pressao_cache=True))
        for _ in range(80):
            if not t.ativo:break
            t.passo()
        self.assertFalse(t.ativo)
        self.assertIs(w.props_cache[('cidade','sprite')],quente)
        self.assertNotIn(('neve','sprite'),w.props_cache)
        self.assertFalse(w.modular['deserto']._maps)
        self.assertEqual(inventariar((w,))['surfaces_unicas'],1)

    def test_cenario_sem_dados_e_limite_de_inventario_conservadores(self):
        a=World()
        for i in range(30):
            a.cache[i]=pygame.Surface((8,8),pygame.SRCALPHA)
        r=inventariar((a,),max_entradas=5)
        self.assertTrue(r['truncado'])
        self.assertFalse(cache_em_pressao(r,.00001))
        self.assertTrue(inventariar((a,),max_entradas=999)['surfaces_unicas']>=30)

if __name__=='__main__':
    unittest.main(verbosity=2)
