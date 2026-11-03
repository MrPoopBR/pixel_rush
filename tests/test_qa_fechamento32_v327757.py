# -*- coding: utf-8 -*-
"""Fechamento 32 QA — autotestes offline direcionados, sem APK/Android.

Testa caminhos efetivamente chamados pelo main QA, inclusive múltiplos mundos,
páginas de atlas sem RNG, skins/pets sem corrida e GC fora do quinto quadro.
Nao é a homologação final de FPS, pixels Android ou EGL.
"""
import gc
import hashlib
import os
import random
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame


class Fechamento32QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_prewarm_skins_pets_somente_menu_rng_preservado(self):
        from pixelrush_qa_precarregamento_visual_v327757 import PrecargaVisuaisQA
        chamados=[]
        def skin(nome):
            chamados.append(('skin',nome))
            random.random()
        def pet(nome):
            chamados.append(('pet',nome))
            random.random()
        before=random.getstate()
        p=PrecargaVisuaisQA('AZUL',frozenset(('AZUL','VERDE','ROSA')),
                           'BOLHA',skin,pet)
        for _ in range(100):self.assertFalse(p.passo('JOGANDO'))
        self.assertEqual(chamados,[])
        for _ in range(32):p.passo('INICIO')
        self.assertEqual([x[0] for x in chamados],['skin','skin','skin','pet'])
        self.assertEqual(chamados[0][1],'AZUL')
        self.assertEqual(random.getstate(),before)
        self.assertEqual(p.diagnostico()['tarefas_pendentes'],0)

    def test_coleta_gc_forca_fora_quinto_quadro_e_restauracao(self):
        import pixelrush_qa_gc_cooperativo_v327757 as qa
        original=pygame.display.flip
        gc_original=gc.isenabled()
        with patch.dict(os.environ,{'PIXELRUSH_QA_ANDROID':'1',
                                     'PIXELRUSH_QA_GC_COOPERATIVO':'1'}):
            if not gc_original:gc.enable()
            qa.instalar()
            try:
                self.assertFalse(gc.isenabled())
                for _ in range(181):pygame.display.flip()
                diag=qa.diagnostico()
                self.assertEqual(diag['frames'],181)
                self.assertEqual(diag['coletas_0'],5)
                self.assertEqual(diag['coletas_1'],1)
                self.assertEqual(diag['coletas_no_quinto_quadro'],0)
            finally:
                qa.restaurar_para_teste()
                self.assertIs(pygame.display.flip,original)
                if not gc_original:gc.disable()
                self.assertEqual(gc.isenabled(),gc_original)

    def test_prewarm_prod_atlas_mais_tiles_sha_sem_carregar_sdl(self):
        import pixelrush_qa_atlas_io_v327747 as qa
        with tempfile.TemporaryDirectory(prefix='pixelrush_qa757_') as d:
            root=Path(d)
            a=root/'atlases';a.mkdir()
            t=root/'tiles';t.mkdir()
            esperado_a=b'atlas-sha-verificado-qa'
            esperado_t=b'tiles-prod-sha-verificado-qa'
            (a/'neve.atlas').write_bytes(esperado_a)
            (t/'neve.tiles').write_bytes(esperado_t)
            atlas=types.ModuleType('pixelrush_atlas_prod_v32776')
            atlas._ATLAS=a
            atlas._HASHES={'neve':hashlib.sha256(esperado_a).hexdigest()}
            tiles=types.ModuleType('pixelrush_tiles_prod_v32777')
            tiles._DIR=t
            tiles._HASHES={'neve':hashlib.sha256(esperado_t).hexdigest()}
            before=random.getstate()
            with patch.dict(sys.modules,{atlas.__name__:atlas,tiles.__name__:tiles}),\
                 patch.dict(os.environ,{'PIXELRUSH_QA_TILES_IO_PREWARM':'1'}):
                result=qa.preaquecer_arquivos_fora_do_jogo(
                    'INICIO',alvos=('neve',),max_total_bytes=2*1024*1024)
            self.assertEqual(result['arquivos'][0]['status'],'sha_ok')
            self.assertEqual(result['tiles_prod'][0]['status'],'sha_ok')
            self.assertEqual(result['bytes_lidos'],len(esperado_a)+len(esperado_t))
            self.assertTrue(result['preparado'])
            self.assertEqual(result['superficies_criadas'],0)
            self.assertFalse(result['sorteio_usado'])
            self.assertEqual(random.getstate(),before)

    def test_memo_multiinstancia_mesmo_frame_com_weakrefs(self):
        import importlib
        import weakref
        class FakeScene:
            visual_quality=1
            def __init__(self):
                self.calls=0
            def render_scene(self,target,travel,frame,night,climate,phase,
                             foreground_only=False,map_kind='image'):
                self.calls+=1
                color={'geometry':(24,48,72,255),
                       'normal':(128,128,255,255),
                       'flow':(0,0,0,255),
                       'fxmask':(0,0,0,0),
                       'material':(180,245,90,255),
                       'image':(18,38,72,129)}[map_kind]
                target.fill(color)

        class FakeWorld:
            def __init__(self):
                self.biome='cidade';self.frame=10;self.travel=90.25
                self.night=.3;self.climate='limpo';self.phase=.5
                self.lightweight=False
                self._city_surfaces={}
                self.city2=FakeScene()
                self.modular=FakeScene()
            def _get_modular(self):
                return self.modular
            def _city_surface(self,kind='image',foreground_only=False):
                self.city2.render_scene(pygame.Surface((450,500),pygame.SRCALPHA),
                                        self.travel,self.frame,self.night,
                                        self.climate,self.phase,
                                        foreground_only,map_kind=kind)

        fake_world=types.ModuleType('pixelrush_world_v3130')
        fake_world.LivingWorld=FakeWorld
        fake_world.WIDTH=450;fake_world.GROUND=730;fake_world.TOP=230
        fake_world.MODULAR_BIOMES=('neve','deserto')
        prof=types.ModuleType('pixelrush_profiler_v3204')
        prof.sub_inicio=lambda *a:None;prof.sub_fim=lambda *a:None
        stubs={'pixelrush_world_v3130':fake_world,
               'pixelrush_profiler_v3204':prof}
        names={
            'pixelrush_qa_alpha_blit_v327731':('instalar',),
            'pixelrush_qa_scene_v327733':('instalar',),
            'pixelrush_qa_camera_v327733':('instalar',),
            'pixelrush_qa_camera_native_auto_v327742':('instalar',),
            'pixelrush_qa_hotpath_v327753':('instalar','restaurar_para_teste'),
            'pixelrush_qa_scroll_auto_v327742':('instalar','restaurar_para_teste'),
            'pixelrush_qa_incremental_scene_v327750':('instalar','restaurar_para_teste'),
            'pixelrush_qa_modular_batch_v327744':('instalar',),
            'pixelrush_qa_city_tiles_v327749':('instalar','restaurar_para_teste'),
            'pixelrush_qa_city_weather_v327749':('instalar','restaurar_para_teste'),
            'pixelrush_qa_gles_bridge_v327749':('instalar','restaurar_para_teste'),
            'pixelrush_qa_performance_integrated_v327742':('instalar',),
            'pixelrush_qa_atlas_io_v327747':('instalar_no_boot_qa',),
            'pixelrush_qa_gc_cooperativo_v327757':('instalar','restaurar_para_teste'),
            'pixelrush_qa_geometry_retire_v327761':('instalar','restaurar_para_teste'),
        }
        for name,fns in names.items():
            module=types.ModuleType(name)
            for fn in fns:
                setattr(module,fn,lambda *a,**kw:None)
            stubs[name]=module
        import pixelrush_qa_render_v327729 as qa
        orig=qa._QA_TECH_SAME_FRAME
        qa._QA_TECH_SAME_FRAME=True
        with patch.dict(sys.modules,stubs):
            try:
                qa.instalar()
                w1,w2=FakeWorld(),FakeWorld()
                for w in (w1,w2):
                    first=w._city_surface('geometry')
                    first_bytes=pygame.image.tobytes(first,'RGBA')
                    second=w._city_surface('geometry')
                    self.assertIs(first,second)
                    self.assertEqual(pygame.image.tobytes(second,'RGBA'),first_bytes)
                    self.assertEqual(w.city2.calls,1)
                    w.frame+=1
                    w._city_surface('geometry')
                    self.assertEqual(w.city2.calls,2)
                    w.travel+=1.5
                    w._city_surface('geometry')
                    self.assertEqual(w.city2.calls,3)
                    w.biome='neve'
                    w._city_surfaces.clear()
                    w._city_surface('geometry')
                    self.assertEqual(w.modular.calls,1)
                self.assertGreater(qa._QA_TECH_STATS['hits'],0)
            finally:
                qa.restaurar_para_teste()
                qa._QA_TECH_SAME_FRAME=orig


if __name__=='__main__':
    unittest.main(verbosity=2)
