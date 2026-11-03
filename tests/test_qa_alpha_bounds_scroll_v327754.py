# -*- coding: utf-8 -*-
"""QA754: regressões Pygame-ce PREPARADAS, não homologadas nesta entrega.

Compara canais da Cidade REAL (v3125) com os caminhos anteriores, inclusive
alpha invisível, sprites animados e scroll com saltos. Sem APK/Android.
"""
import os
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pygame


def raw_rgba(surface):
    return pygame.image.tobytes(surface, "RGBA")


class CidadeAlphaScroll754(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450, 800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_canais_reais_alpha_bounds_e_base_vazia(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_city2_v3118 as base
        cena = CityPilotScene()
        self.assertTrue(cena._qa_alpha_bounds, "sem mapas com crop: inspecionar atlas")
        self.assertTrue(cena._qa_empty_base_maps, "sem mapas vazios: inspecionar atlas")
        orig = (base._QA_SKIP_EMPTY_BASE, base._QA_ALPHA_BOUNDS,
                base._QA_CULL_SPRITES_EARLY)
        rng = random.getstate()
        try:
            for target_flags in (0, pygame.SRCALPHA):
                for layer in cena.layers:
                    for variant in layer.variants[:1]:
                        for kind in ("image", "geometry", "fxmask", "normal",
                                     "material", "flow"):
                            for j, x in enumerate((-780, -450, -20, 410, 450)):
                                old = pygame.Surface((450, 500), target_flags)
                                old.fill((22, 68, 110, 147) if target_flags
                                         else (22, 68, 110))
                                fast = old.copy()
                                base._QA_SKIP_EMPTY_BASE = False
                                base._QA_ALPHA_BOUNDS = False
                                base._QA_CULL_SPRITES_EARLY = False
                                cena._render_chunk(old, variant, False, x,
                                                  35+j, .42, "vento", .51,
                                                  map_kind=kind)
                                base._QA_SKIP_EMPTY_BASE = True
                                base._QA_ALPHA_BOUNDS = True
                                base._QA_CULL_SPRITES_EARLY = True
                                cena._render_chunk(fast, variant, False, x,
                                                  35+j, .42, "vento", .51,
                                                  map_kind=kind)
                                self.assertEqual(raw_rgba(old), raw_rgba(fast),
                                                 (target_flags, layer.name, kind, x))
            self.assertEqual(random.getstate(), rng)
        finally:
            (base._QA_SKIP_EMPTY_BASE, base._QA_ALPHA_BOUNDS,
             base._QA_CULL_SPRITES_EARLY) = orig

    def test_near_plan_sem_tuple_em_canais_nao_consumidores(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_city2_v3124 as city
        cena = CityPilotScene()
        saved = city._QA_NEAR_TUPLE_ON_DEMAND
        try:
            for kind in ("normal", "geometry", "material", "flow",
                         "image", "fxmask"):
                old = pygame.Surface((450, 500), pygame.SRCALPHA)
                fast = old.copy()
                city._QA_NEAR_TUPLE_ON_DEMAND = False
                cena.render_scene(old, 247.75, 38, .34, "chuva", .55,
                                  map_kind=kind)
                city._QA_NEAR_TUPLE_ON_DEMAND = True
                cena.render_scene(fast, 247.75, 38, .34, "chuva", .55,
                                  map_kind=kind)
                self.assertEqual(raw_rgba(old), raw_rgba(fast), kind)
        finally:
            city._QA_NEAR_TUPLE_ON_DEMAND = saved

    def test_destino_rgba_alpha_zero_rgb_oculto_requer_blit_inteiro(self):
        # SDL2 com source alpha=0 modifica RGB oculto quando dest alpha=0.
        # Um crop baseado apenas no bbox de alpha mudaria esses bytes.
        src=pygame.Surface((2, 2), pygame.SRCALPHA, 32)
        src.fill((91, 63, 20, 0))
        dest=pygame.Surface((2, 2), pygame.SRCALPHA, 32)
        dest.fill((18, 37, 71, 0))
        original=dest.copy()
        original.blit(src, (0,0))
        self.assertNotEqual(raw_rgba(original),raw_rgba(dest))
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_city2_v3118 as base
        scene=CityPilotScene()
        flags=(base._QA_ALPHA_BOUNDS,base._QA_SKIP_EMPTY_BASE)
        try:
            for initial_alpha in (0,1,17,147,255):
                for layer in scene.layers:
                    variant=layer.variants[0]
                    for kind in ('image','geometry','normal',
                                 'flow','fxmask','material'):
                        a=pygame.Surface((450,500),pygame.SRCALPHA,32)
                        a.fill((18,37,71,initial_alpha))
                        b=a.copy()
                        base._QA_ALPHA_BOUNDS=False
                        base._QA_SKIP_EMPTY_BASE=False
                        scene._render_chunk(a,variant,False,-465,42,.4,
                                            'limpo',.55,map_kind=kind)
                        base._QA_ALPHA_BOUNDS=True
                        base._QA_SKIP_EMPTY_BASE=True
                        scene._render_chunk(b,variant,False,-465,42,.4,
                                            'limpo',.55,map_kind=kind)
                        self.assertEqual(raw_rgba(a),raw_rgba(b),
                                         ("hidden_rgba",initial_alpha,layer.name,kind))
        finally:
            base._QA_ALPHA_BOUNDS,base._QA_SKIP_EMPTY_BASE=flags

    def test_scroll_saltos_direto_sem_reconstruir_frame(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_qa_incremental_scene_v327750 as incr
        import pixelrush_city2_v3118 as original_city
        # Verificar o algoritmo de scroll SOMENTE com textura sem SDL-RLE.
        # Atlas reais RLE seguem blit direto, cobertos por gates v755.
        saved_accel=original_city.acelerar_textura_estatica
        incr.restaurar_para_teste()
        old = CityPilotScene._render_chunk
        old_flags = (incr._QA_SCROLL_INIT_CLEAR, incr._QA_SCROLL_JUMP_DIRECT)
        with patch.dict(os.environ, {
                "PIXELRUSH_QA_CITY_INCREMENTAL": "1",
                "PIXELRUSH_QA_CLASSIC_INCREMENTAL": "0",
                "PIXELRUSH_QA_CITY_SCROLL_SCOPE": "static"}):
            try:
                incr._QA_SCROLL_INIT_CLEAR = True
                incr._QA_SCROLL_JUMP_DIRECT = True
                original_city.acelerar_textura_estatica=lambda tex:tex
                incr.instalar()
                cena = CityPilotScene()
                fonte = cena.layers[0].variants[0]
                for flags in (0, pygame.SRCALPHA):
                    for i, x in enumerate(
                            (-560, -558, -555, -552, -300, -299, -296,
                             -780, -778, -550, -548, -546)):
                        expected = pygame.Surface((450, 500), flags)
                        expected.fill((18, 51, 99, 143) if flags
                                      else (18, 51, 99))
                        got = expected.copy()
                        old(cena, expected, fonte, False, x, i+90,
                            .6, "limpo", .5, "image")
                        cena._render_chunk(got, fonte, False, x, i+90,
                                           .6, "limpo", .5, "image")
                        self.assertEqual(raw_rgba(expected), raw_rgba(got),
                                         (flags, i, x))
                diag = incr.diagnostico()
                self.assertGreater(diag["cidade_salto_direto"], 0)
                self.assertGreater(diag["cidade_init_sem_fill"], 0)
                self.assertGreater(diag["cidade_hit"], 0)
                self.assertLessEqual(len(incr._CIDADE.get(cena, {})), 2)
            finally:
                incr.restaurar_para_teste()
                original_city.acelerar_textura_estatica=saved_accel
                (incr._QA_SCROLL_INIT_CLEAR,
                 incr._QA_SCROLL_JUMP_DIRECT) = old_flags
        self.assertIs(CityPilotScene._render_chunk, old)

    def test_scroll_salto_fallback_antigo_equivalente(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_qa_incremental_scene_v327750 as incr
        import pixelrush_city2_v3118 as original_city
        saved_accel=original_city.acelerar_textura_estatica
        incr.restaurar_para_teste()
        old = CityPilotScene._render_chunk
        saved = incr._QA_SCROLL_JUMP_DIRECT
        with patch.dict(os.environ, {
                "PIXELRUSH_QA_CITY_INCREMENTAL": "1",
                "PIXELRUSH_QA_CITY_SCROLL_SCOPE": "static"}):
            try:
                incr._QA_SCROLL_JUMP_DIRECT = False
                original_city.acelerar_textura_estatica=lambda tex:tex
                incr.instalar()
                cena = CityPilotScene()
                variant = cena.layers[1].variants[0]
                for i, x in enumerate((-530, -527, -350, -348, -790)):
                    expected = pygame.Surface((450, 500), pygame.SRCALPHA)
                    expected.fill((33, 52, 82, 111))
                    got = expected.copy()
                    old(cena, expected, variant, False, x, i+80,
                        .2, "vento", .4, "image")
                    cena._render_chunk(got, variant, False, x, i+80,
                                       .2, "vento", .4, "image")
                    self.assertEqual(raw_rgba(expected), raw_rgba(got),
                                     ("fallback", i))
            finally:
                incr.restaurar_para_teste()
                original_city.acelerar_textura_estatica=saved_accel
                incr._QA_SCROLL_JUMP_DIRECT = saved


if __name__ == "__main__":
    unittest.main(verbosity=2)
