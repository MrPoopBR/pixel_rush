# -*- coding: utf-8 -*-
"""QA758: saída RGBA do render modular e limpeza de meteorologia, sem assets."""
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame
import pixelrush_biomes2_v3128 as modular

class MeteoroRGBA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((modular.WIDTH,modular.HEIGHT))
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def _scene(self,biome):
        tiles={}
        for name in modular.DEPTH:
            src=pygame.Surface((modular.LW,modular.LH),pygame.SRCALPHA)
            src.fill((39,96,181,0))
            pygame.draw.line(src,(61,130,88,0),(0,11),(modular.LW-1,11))
            pygame.draw.rect(src,(31,113,191,195),(20,70,130,90))
            tiles[name]=src
        def draw_layer(dst,layer,travel,kind):
            dst.blit(tiles[layer],(0,0))
        return SimpleNamespace(biome=biome,visual_quality=True,_poses=[None],
            _composites={},_weather=pygame.Surface((modular.LW,modular.LH),pygame.SRCALPHA),
            _geometry_view=None,_last_state=None,_draw_layer=draw_layer)

    def test_transicoes_clima_completo_byte_exato_vs_fallback(self):
        original=modular._QA_SKIP_INERT_WEATHER
        try:
            for biome in ('neve','deserto'):
                referência=self._scene(biome)
                otimizada=self._scene(biome)
                climas=('limpo','limpo','chuva','nevasca','neve','limpo',
                         'limpo','tempestade_areia','areia','limpo','limpo')
                for frame,clima in enumerate(climas):
                    outs=[]
                    for flag,scene in ((False,referência),(True,otimizada)):
                        modular._QA_SKIP_INERT_WEATHER=flag
                        surface=pygame.Surface((modular.WIDTH,modular.HEIGHT),pygame.SRCALPHA)
                        modular.ModularBiomeScene.render_scene(
                            scene,surface,travel=frame*23,frame=frame*17,
                            night=.25,climate=clima,phase=.4,map_kind='image')
                        outs.append(pygame.image.tobytes(surface,'RGBA'))
                    self.assertEqual(outs[0],outs[1],(biome,frame,clima))
        finally:
            modular._QA_SKIP_INERT_WEATHER=original

    def test_blit_sempre_preservado_e_buffer_ja_limpo(self):
        scene=self._scene('neve')
        old=modular._QA_SKIP_INERT_WEATHER
        try:
            modular._QA_SKIP_INERT_WEATHER=True
            surface=pygame.Surface((modular.WIDTH,modular.HEIGHT),pygame.SRCALPHA)
            for frame,climate in enumerate(('nevasca','limpo','limpo')):
                modular.ModularBiomeScene.render_scene(scene,surface,0,frame,0,climate,.5)
            self.assertTrue(scene._qa_weather_overlay_clean)
            self.assertEqual(scene._weather.get_at((0,0)).a,0)
        finally:
            modular._QA_SKIP_INERT_WEATHER=old

if __name__=='__main__':
    unittest.main(verbosity=2)
