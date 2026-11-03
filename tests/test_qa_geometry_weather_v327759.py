# -*- coding: utf-8 -*-
"""QA759: regression gate byte RGBA para geometry/oclusao e clima em SDL dummy."""
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame
import pixelrush_biomes2_v3128 as snow
import pixelrush_qa_city_weather_v327749 as weather
from pixelrush_biomes2_v3126 import ModularBiomeScene as Base
from pixelrush_citylife_v3123 import CityLifeDirector
from pixelrush_city2_v3125 import CityPilotScene

def raw(surface):
    return pygame.image.tobytes(surface, 'RGBA')

class GeometryWeather759(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450, 800))
    @classmethod
    def tearDownClass(cls):
        weather.restaurar_para_teste()
        pygame.quit()

    def test_cidade_geometry_sem_copia_equivalente(self):
        scene = CityPilotScene()
        scene.visual_quality = 1
        target = pygame.Surface((450, 500), pygame.SRCALPHA)
        scene._qa_geometry_borrow_target = None
        scene.render_scene(target, 191.5, 151, .43, 'limpo', .5, map_kind='geometry')
        expected = raw(target)
        self.assertIsNot(scene._geometry_view, target)
        ao = scene.ambient_occlusion(130, 90, 480, 630)
        scene._qa_geometry_borrow_target = target
        scene.render_scene(target, 191.5, 151, .43, 'limpo', .5, map_kind='geometry')
        self.assertEqual(expected, raw(target))
        self.assertIs(scene._geometry_view, target)
        self.assertEqual(ao, scene.ambient_occlusion(130, 90, 480, 630))
        img = pygame.Surface((450, 500), pygame.SRCALPHA)
        scene.render_scene(img, 191.5, 151, .43, 'limpo', .5, map_kind='image')
        self.assertEqual(expected, raw(target))
        scene._qa_geometry_borrow_target = None
        scene.render_scene(target, 191.5, 151, .43, 'limpo', .5, map_kind='geometry')
        self.assertIsNot(scene._geometry_view, target)
        self.assertEqual(expected, raw(scene._geometry_view))

    def _mock_scene(self, biome):
        def draw(dst, layer, travel, kind):
            pygame.draw.rect(dst, (16, 115, 212, 77), (12, 50, 40, 80))
        return SimpleNamespace(
            biome=biome, visual_quality=1, _poses=[None],
            _composites={}, _weather=pygame.Surface((snow.LW, snow.LH), pygame.SRCALPHA),
            _geometry_view=None, _last_state=None, _draw_layer=draw)

    def test_modulares_geometry_sem_copia_equivalente(self):
        for biome in ('neve', 'deserto'):
            scene = self._mock_scene(biome)
            target = pygame.Surface((snow.WIDTH, snow.HEIGHT), pygame.SRCALPHA)
            scene._qa_geometry_borrow_target = None
            snow.ModularBiomeScene.render_scene(scene,target,91,20,.3,'limpo',.5,map_kind='geometry')
            expected = raw(target)
            ao = Base.ambient_occlusion(scene, 130, 80, 440, 580)
            scene._qa_geometry_borrow_target = target
            snow.ModularBiomeScene.render_scene(scene,target,91,20,.3,'limpo',.5,map_kind='geometry')
            self.assertIs(scene._geometry_view, target)
            self.assertEqual(expected, raw(target))
            self.assertEqual(ao, Base.ambient_occlusion(scene, 130, 80, 440, 580))
            scene._qa_geometry_borrow_target = None
            snow.ModularBiomeScene.render_scene(scene,target,91,20,.3,'limpo',.5,map_kind='geometry')
            self.assertIsNot(scene._geometry_view, target)
            self.assertEqual(expected, raw(scene._geometry_view))

    def test_clima_modular_sementes_iguais_rgba(self):
        original = snow._QA_MODULAR_SEEDS
        try:
            for biome in ('neve', 'deserto'):
                slow,fast = self._mock_scene(biome),self._mock_scene(biome)
                for quality in (0,1):
                    slow.visual_quality=fast.visual_quality=quality
                    for frame in (0,5,18,143,777):
                        for climate in ('limpo','neve','nevasca','areia','tempestade_areia'):
                            buffers=[]
                            for mode,scene in ((False,slow),(True,fast)):
                                snow._QA_MODULAR_SEEDS=mode
                                dst=pygame.Surface((snow.WIDTH,snow.HEIGHT),pygame.SRCALPHA)
                                snow.ModularBiomeScene.render_scene(
                                    scene,dst,78.5,frame,.41,climate,.2,map_kind='image')
                                buffers.append(raw(dst))
                            self.assertEqual(buffers[0],buffers[1],(biome,quality,frame,climate))
        finally:
            snow._QA_MODULAR_SEEDS=original

    def test_cidade_atmosfera_original_vs_qa_rgba(self):
        original = CityLifeDirector.draw_atmosphere
        weather.instalar()
        try:
            fast = CityLifeDirector.draw_atmosphere
            for quality in (0,1):
                for frame in (0,4,37,153,491):
                    for climate in ('limpo','chuva','tempestade','neve','vento'):
                        for wind in (-1.3,0.,1.17):
                            obj=SimpleNamespace(MAX_PARTICLES=12,wind=wind)
                            a=pygame.Surface((450,500),pygame.SRCALPHA)
                            b=pygame.Surface((450,500),pygame.SRCALPHA)
                            a.fill((47,92,188,0));b.fill((47,92,188,0))
                            original(obj,a,99.75,frame,.3,climate,quality)
                            fast(obj,b,99.75,frame,.3,climate,quality)
                            self.assertEqual(raw(a),raw(b),(quality,frame,climate,wind))
            extra=SimpleNamespace(MAX_PARTICLES=16,wind=.1)
            a=pygame.Surface((450,500),pygame.SRCALPHA)
            b=a.copy()
            original(extra,a,10,9,.1,'chuva',1)
            fast(extra,b,10,9,.1,'chuva',1)
            self.assertEqual(raw(a),raw(b))
        finally:
            weather.restaurar_para_teste()
            self.assertIs(CityLifeDirector.draw_atmosphere,original)

if __name__ == '__main__':
    unittest.main(verbosity=2)
