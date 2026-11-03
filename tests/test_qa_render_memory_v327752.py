# -*- coding: utf-8 -*-
"""QA752 — regressões PREPARADAS, execução apenas na homologação futura.

Valida os módulos reais de Neve/Deserto, cópias diurnas, cache de planos,
geometria borrowed e alternância seca/precipitação. Sem tocar saves, PETs,
física ou RNG do jogo. Nenhum teste Android é executado automaticamente.
"""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame


def rgba(surface):
    return pygame.image.tobytes(surface,'RGBA')


class Integracao752(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_modular_pular_overlay_vazio_preserva_rgba_e_retorno_da_chuva(self):
        import pixelrush_biomes2_v3128 as base
        from pixelrush_biomes2_v3130 import ModularBiomeScene
        original=base._QA_SKIP_INERT_WEATHER
        try:
            for biome,chuva in (('neve','nevasca'),('deserto','tempestade_areia')):
                scene=ModularBiomeScene(biome)
                for flags in (0,pygame.SRCALPHA):
                    for quality in (0,1):
                        scene.visual_quality=quality
                        # Chuva -> seco -> limpo -> chuva, mais dois níveis de noite.
                        for frame,climate,night in (
                                (1,chuva,.0),(2,'limpo',.0),(5,'vento',.5),
                                (6,chuva,1.),(9,'limpo',.8),(33,chuva,.2)):
                            old=pygame.Surface((450,500),flags)
                            new=pygame.Surface((450,500),flags)
                            old.fill((19,27,43,96) if flags else (19,27,43))
                            new.fill((19,27,43,96) if flags else (19,27,43))
                            base._QA_SKIP_INERT_WEATHER=False
                            scene.render_scene(old,frame*4.27,frame,night,climate,.6)
                            base._QA_SKIP_INERT_WEATHER=True
                            scene.render_scene(new,frame*4.27,frame,night,climate,.6)
                            self.assertEqual(rgba(old),rgba(new),
                                             (biome,flags,quality,frame,climate))
        finally:
            base._QA_SKIP_INERT_WEATHER=original

    def test_neve_tile_dia_usa_atlas_src_sem_copia(self):
        import pixelrush_biomes2_v3128 as base
        from pixelrush_biomes2_v3130 import ModularBiomeScene
        with patch.object(base,'_QA_SHARE_DAYLIGHT',True):
            snow=ModularBiomeScene('neve')
        for layer,tiles in snow._poses[0].items():
            for idx,src in enumerate(tiles):
                self.assertIs(snow._night_tiles[(0,layer,idx,0)],src)
                self.assertEqual(rgba(snow._night_tiles[(0,layer,idx,0)]),
                                 rgba(src))

    def test_deserto_tile_dia_usa_atlas_src_sem_copia(self):
        import pixelrush_biomes2_v3130 as current
        scene=current.ModularBiomeScene('deserto')
        scene._pose=0;scene._night_level=0
        old=current._QA_SHARE_DAYLIGHT
        key=(0,'near',0,0)
        src=scene._poses[0]['near'][0]
        try:
            current._QA_SHARE_DAYLIGHT=True
            scene._night_tiles.pop(key,None)
            day=scene._tile_map('near',0,'image')
            self.assertIs(day,src)
            original_rgba=rgba(day)
            current._QA_SHARE_DAYLIGHT=False
            scene._night_tiles.pop(key,None)
            snapshot=scene._tile_map('near',0,'image')
            self.assertIsNot(snapshot,src)
            self.assertEqual(original_rgba,rgba(snapshot))
        finally:
            current._QA_SHARE_DAYLIGHT=old

    def test_geometry_borrow_evolui_ao_mesmo_rgba_e_reverte_para_snapshot(self):
        from pixelrush_city2_v3125 import CityPilotScene
        from pixelrush_biomes2_v3130 import ModularBiomeScene
        for scene in (CityPilotScene(),ModularBiomeScene('neve')):
            destino=pygame.Surface((450,500),pygame.SRCALPHA)
            destino.fill((21,32,47,91))
            scene._qa_geometry_borrow_target=destino
            try:
                scene.render_scene(destino,38.4,19,.28,'limpo',.55,
                                   map_kind='geometry')
            finally:
                scene._qa_geometry_borrow_target=None
            self.assertIs(scene._geometry_view,destino)
            esperado_mundo=rgba(destino)
            proximo=pygame.Surface((450,500),pygame.SRCALPHA)
            proximo.fill((31,22,77,123))
            scene.render_scene(proximo,45.2,20,.28,'limpo',.55,
                               map_kind='geometry')
            self.assertIsNot(scene._geometry_view,proximo)
            self.assertIsNot(scene._geometry_view,destino)
            self.assertEqual(rgba(scene._geometry_view),rgba(proximo))
            self.assertEqual(rgba(destino),esperado_mundo,
                             'snapshot externo nao pode mutar buffer World-owned')

    def test_plano_tiles_modo_auto_sdl_nao_instala_e_flag_forcada_funciona(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_qa_city_tiles_v327749 as plan
        plan.restaurar_para_teste()
        original=CityPilotScene._layer_tiles
        try:
            with patch.dict(os.environ,{
                'PIXELRUSH_GPU':'off','PIXELRUSH_QA_CIDADE_TILE_PLAN':'auto'}):
                plan.instalar()
                self.assertFalse(plan.estatisticas()['instalado'])
                self.assertIs(CityPilotScene._layer_tiles,original)
            with patch.dict(os.environ,{
                'PIXELRUSH_GPU':'off','PIXELRUSH_QA_CIDADE_TILE_PLAN':'1'}):
                plan.instalar()
                self.assertTrue(plan.estatisticas()['instalado'])
                scene=CityPilotScene()
                layer=scene.layers[0]
                expected=tuple(original(37.4,layer))
                self.assertEqual(tuple(CityPilotScene._layer_tiles(37.4,layer)),
                                 expected)
                self.assertEqual(tuple(CityPilotScene._layer_tiles(37.4,layer)),
                                 expected)
                iterator=CityPilotScene._layer_tiles(37.4,layer)
                next(iterator)
                with self.assertRaisesRegex(ValueError,'erro_consumidor'):
                    iterator.throw(ValueError('erro_consumidor'))
                # Um consumidor que errou nao deve provocar novo render do
                # plano original nem criar segunda lista de sprites.
                self.assertEqual(plan.estatisticas()['fallbacks'],0)
        finally:
            plan.restaurar_para_teste()
            self.assertIs(CityPilotScene._layer_tiles,original)


if __name__=='__main__':
    unittest.main(verbosity=2)
