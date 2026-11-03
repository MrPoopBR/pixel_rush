# -*- coding: utf-8 -*-
"""PIXEL RUSH QA 3.277.44: cobertura do render REAL v3125/v3130 e caches."""
import os
import sys
import unittest
from pathlib import Path
from collections import OrderedDict
from types import SimpleNamespace

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame


def bits(s):
    return pygame.image.tobytes(s,'RGBA')


class RendererRealQA744(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_classes_usadas_pelo_mundo_sao_atuais(self):
        import pixelrush_world_v3130 as world
        from pixelrush_city2_v3125 import CityPilotScene
        from pixelrush_biomes2_v3130 import ModularBiomeScene
        from pixelrush_biomes2_v3128 import ModularBiomeScene as Scene128
        self.assertIs(world.CityPilotScene,CityPilotScene)
        self.assertIs(world.ModularBiomeScene,ModularBiomeScene)
        self.assertIsNot(ModularBiomeScene._draw_layer, Scene128._draw_layer)
        self.assertIn('neve',world.MODULAR_BIOMES)
        self.assertIn('deserto',world.MODULAR_BIOMES)

    def test_cidade_real_nao_usa_caminho_antigo_de_nuvens(self):
        from pixelrush_city2_v3125 import CityPilotScene
        scene=CityPilotScene()
        old=scene._draw_sky
        # v3124 usa o ceu existente do ParallaxBackground do jogo.
        scene._draw_sky=lambda *_a,**_kw:self.fail('ceu duplicado na cidade real')
        try:
            a=pygame.Surface((450,500),pygame.SRCALPHA)
            for i in range(6):
                scene.render_scene(a,235.7+i*33.3,11+i*21,.12*i,'chuva',.52)
                self.assertEqual(a.get_size(),(450,500))
        finally:
            scene._draw_sky=old

    def test_compositor_real_pixel_exato_por_mapa(self):
        from pixelrush_world_v3130 import LivingWorld
        import pixelrush_qa_render_v327729 as renderer
        from pixelrush_qa_performance_integrated_v327742 import restaurar_para_teste as restore_perf
        import pixelrush_qa_camera_native_auto_v327742 as native
        import pixelrush_qa_camera_v327733 as simd
        import pixelrush_qa_scroll_auto_v327742 as scroll
        import pixelrush_qa_scene_v327733 as scene_qa
        import pixelrush_qa_modular_batch_v327744 as batch
        renderer.restaurar_para_teste()
        restore_perf();native.restaurar_para_teste();simd.restaurar_para_teste()
        scroll.restaurar_para_teste();scene_qa.restaurar_para_teste()
        old=LivingWorld._city_surface
        renderer.instalar()
        try:
            for biome in ('cidade','neve','deserto'):
                world=LivingWorld(biome,lightweight=False)
                for i in range(7):
                    world.frame=23+i*19
                    world.travel=31.7+i*113.8
                    world.night=(.0,.13,.26,.54,.85,.95,1.)[i]
                    world.phase=.37+i*.07
                    world.climate=('limpo','chuva','neve','nevasca','areia','tempestade_areia','vento')[i]
                    for kind in ('image','normal','geometry','material','fxmask','flow'):
                        original=old(world,kind).copy()
                        atual=world._city_surface(kind)
                        self.assertEqual(bits(original),bits(atual),
                                         (biome,i,kind))
                        self.assertEqual(atual.get_size(),(450,500))
        finally:
            restore_perf();native.restaurar_para_teste();simd.restaurar_para_teste()
            scroll.restaurar_para_teste();batch.restaurar_para_teste()
            scene_qa.restaurar_para_teste()
            renderer.restaurar_para_teste()
        self.assertIs(LivingWorld._city_surface,old)

    def test_batch_modular_opcional_preserva_rgba_real(self):
        from pixelrush_biomes2_v3130 import ModularBiomeScene
        import pixelrush_qa_modular_batch_v327744 as batch
        oldflag=os.environ.get('PIXELRUSH_QA_MODULAR_BATCH')
        batch.restaurar_para_teste()
        scenes=[ModularBiomeScene('neve'),ModularBiomeScene('deserto')]
        try:
            os.environ['PIXELRUSH_QA_MODULAR_BATCH']='1'
            for scene in scenes:
                for i in range(8):
                    frame=39+i*39
                    travel=frame*4.3
                    night=(0,.12,.35,.65,1.)[i%5]
                    climate=('limpo','nevasca','tempestade_areia')[i%3]
                    for kind in ('image','normal','geometry','material','fxmask','flow'):
                        original=pygame.Surface((450,500),pygame.SRCALPHA)
                        scene.render_scene(original,travel,frame,night,climate,.52,map_kind=kind)
                        batch.instalar()
                        try:
                            optimized=pygame.Surface((450,500),pygame.SRCALPHA)
                            scene.render_scene(optimized,travel,frame,night,climate,.52,map_kind=kind)
                            self.assertEqual(bits(original),bits(optimized),
                                             (scene.biome,i,kind))
                        finally:
                            batch.restaurar_para_teste()
        finally:
            batch.restaurar_para_teste()
            if oldflag is None:os.environ.pop('PIXELRUSH_QA_MODULAR_BATCH',None)
            else:os.environ['PIXELRUSH_QA_MODULAR_BATCH']=oldflag

    def test_cache_temporal_mantem_periodo_e_5_frames(self):
        from pixelrush_qa_ultraleve_v327730 import CacheFundoUltraQA
        cache=CacheFundoUltraQA(periodo=5)
        surface=pygame.Surface((450,800)).convert()
        redraw=[]
        for i in range(65):
            if not cache.reusar(surface,('cidade','limpo'),True):
                surface.fill((i%256,21,57))
                cache.guardar(surface,('cidade','limpo'),True)
                redraw.append(i)
        self.assertEqual(redraw,list(range(0,65,5)))
        self.assertEqual(cache.passes_evitados,52)
        self.assertEqual(cache.recriacoes,13)
        # Invalidacao de clima impede reutilizar cena visual incorreta.
        self.assertFalse(cache.reusar(surface,('cidade','nevasca'),True))

    def test_pressao_rss_preserva_cidade_ativa_e_mede_limpeza(self):
        import pixelrush_qa_performance_integrated_v327742 as perf
        class FakeWorld:
            def __init__(self,biome):
                self.biome=biome
                self.props_cache={}
                self.cache=OrderedDict()
                self.fx_cache=OrderedDict()
                self.normal_cache=OrderedDict()
                self.material_cache=OrderedDict()
                self.flow_cache=OrderedDict()
                self.geometry_cache=OrderedDict()
                self._city_surfaces={}
                self.city2=SimpleNamespace(_scaled=OrderedDict((str(k),k) for k in range(14)))
        city=FakeWorld('cidade')
        prev=perf._memory_mib
        status=dict(perf._LAST_STATUS)
        try:
            perf._WORLDS.add(city)
            perf._memory_mib=lambda:900.
            perf._LAST_STATUS['cache_budget_mib']=560
            perf._reclaim_inactive_caches()
            self.assertEqual(len(city.city2._scaled),14)
            city.biome='neve'
            perf._reclaim_inactive_caches()
            self.assertEqual(len(city.city2._scaled),8)
        finally:
            perf._WORLDS.discard(city)
            perf._memory_mib=prev
            perf._LAST_STATUS.clear()
            perf._LAST_STATUS.update(status)

    def test_inventario_nao_modifica_referencias(self):
        from pixelrush_qa_audit_offline_v327744 import inventario_recursos,resumo_caches_mundo
        from pixelrush_world_v3130 import LivingWorld
        w=LivingWorld('cidade')
        before=resumo_caches_mundo(w)
        a=inventario_recursos(w)
        b=inventario_recursos(w)
        self.assertEqual(before,resumo_caches_mundo(w))
        self.assertEqual(a['surfaces_unicas'],b['surfaces_unicas'])
        self.assertGreater(a['surfaces_unicas'],0)
        self.assertGreater(a['bytes_logicos_surfaces'],0)
        self.assertFalse(a['limite_excedido'])


if __name__=='__main__':
    unittest.main(verbosity=2)
