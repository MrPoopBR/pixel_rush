"""Pixel Rush v3.119.0 — Cidade 2.4 ultra-refinada.

Mantém a base estrutural correta da v3.118.0 e aprofunda a qualidade artística
sem reintroduzir chunks quebrados: fachadas mais ricas, árvores e postes mais
sofisticados, banners/placas mais coerentes e calçada mais detalhada.

Escopo:
- melhorar TEXTURAS INDIVIDUAIS de prédios, árvores, postes e props;
- preservar alinhamento, chão contínuo e parallax estável;
- não alterar colisões, física do jogador nem gameplay.
"""
from collections import OrderedDict
import math
import random
import pygame
from pixelrush_city2_v3118 import CityPilotScene as _City118, SpriteLibrary as _BaseLib
from pixelrush_city2_v3117 import SpriteInstance, ChunkVariant
from pixelrush_city2_v3115 import Layer, WIDTH, LOW_W, LOW_H, SCENE_W, SCENE_H, SCALE, DEFAULT_NORMAL, NEUTRAL_FLOW, clamp, lerp_color


class SpriteLibraryUltra(_BaseLib):
    """Sprites urbanos mais ricos, ainda em pixel art limpa."""

    def _build(self):
        super()._build()
        self.assets['tree_small'] = self._tree_pro(size=(26, 36), profile='small')
        self.assets['tree_big'] = self._tree_pro(size=(34, 46), profile='big')
        self.assets['lamp'] = self._lamp_pro()
        self.assets['banner'] = self._banner_pro()
        self.assets['flowerpot'] = self._flowerpot_pro()
        self.assets['clock_post'] = self._clock_post_pro()
        self.assets['cafe_board'] = self._cafe_board_pro()
        self.assets['awning_flowers'] = self._flower_box_pro()
        self.assets['bush'] = self._bush_pro()
        self.assets['fg_leaves'] = self._fg_leaves_pro()
        self.assets['sign'] = self._sign_pro()
        self.assets['canopy'] = self._canopy_pro()

    def _tree_pro(self, size=(26, 36), profile='small'):
        w, h = size
        s = self._blank((w, h))
        trunk_dark = (78, 56, 47)
        trunk_mid = (104, 74, 58)
        trunk_light = (133, 99, 74)
        pygame.draw.rect(s, trunk_dark, (w//2 - 3, h - 14, 6, 14))
        pygame.draw.rect(s, trunk_mid, (w//2 - 2, h - 14, 4, 13))
        pygame.draw.line(s, trunk_light, (w//2 - 1, h - 14), (w//2 - 1, h - 2), 1)
        leaf_shadow = (37, 114, 71)
        leaf_mid = (59, 157, 96)
        leaf_light = (107, 205, 118)
        # copa irregular com profundidade
        if profile == 'big':
            blobs = [
                (w//2 - 9, h - 19, 8, leaf_shadow), (w//2 + 7, h - 20, 8, leaf_mid),
                (w//2 - 1, h - 27, 10, leaf_mid), (w//2 - 13, h - 26, 6, leaf_mid),
                (w//2 + 12, h - 28, 6, leaf_shadow), (w//2 - 2, h - 34, 7, leaf_light),
            ]
        else:
            blobs = [
                (w//2 - 6, h - 17, 7, leaf_shadow), (w//2 + 4, h - 18, 7, leaf_mid),
                (w//2 - 1, h - 24, 9, leaf_mid), (w//2 - 2, h - 30, 6, leaf_light),
            ]
        for cx, cy, r, col in blobs:
            pygame.draw.circle(s, col, (cx, cy), r)
        # highlights em folhas
        for cx, cy, r in ((w//2 - 2, h - 29, 4), (w//2 + 6, h - 22, 3), (w//2 - 8, h - 22, 3)):
            pygame.draw.circle(s, leaf_light, (cx, cy), r)
        # ramificações sutis
        pygame.draw.line(s, trunk_dark, (w//2, h - 19), (w//2 - 5, h - 24), 1)
        pygame.draw.line(s, trunk_dark, (w//2, h - 19), (w//2 + 5, h - 25), 1)
        return self._make_asset(s, material_color=(70, 149, 90))

    def _lamp_pro(self):
        s = self._blank((16, 40))
        # base e haste metálica com relevo
        pygame.draw.rect(s, (72, 61, 84), (7, 4, 2, 25))
        pygame.draw.rect(s, (93, 81, 104), (6, 6, 4, 22))
        pygame.draw.rect(s, (62, 53, 73), (5, 28, 6, 9))
        pygame.draw.rect(s, (112, 95, 114), (5, 35, 6, 2))
        # braço superior
        pygame.draw.rect(s, (74, 63, 84), (8, 6, 4, 2))
        pygame.draw.rect(s, (74, 63, 84), (10, 8, 2, 4))
        # luminária
        pygame.draw.rect(s, (253, 219, 132), (4, 11, 8, 7))
        pygame.draw.rect(s, (255, 242, 182), (5, 12, 6, 2))
        pygame.draw.line(s, (255, 231, 170), (6, 16), (10, 16), 1)
        def fx_builder(_):
            out = self._blank((16, 40))
            for r, a in ((12, 28), (9, 55), (6, 90), (3, 170)):
                pygame.draw.circle(out, (255, 221, 112, a), (8, 15), r)
            return out
        return self._make_asset(s, material_color=(148, 123, 108), fx_builder=fx_builder)

    def _banner_pro(self, color=(230, 102, 170), accent=(255, 236, 128)):
        s = self._blank((18, 30))
        pygame.draw.rect(s, (64, 58, 84), (0, 0, 2, 30))
        pygame.draw.rect(s, (88, 77, 100), (1, 0, 1, 30))
        pygame.draw.rect(s, color, (3, 3, 12, 20))
        pygame.draw.polygon(s, color, [(3, 23), (9, 28), (15, 23)])
        pygame.draw.rect(s, (255, 196, 228), (4, 4, 10, 2))
        pygame.draw.circle(s, accent, (9, 12), 3)
        pygame.draw.rect(s, (255, 242, 182), (7, 16, 4, 2))
        return self._make_asset(s, material_color=(205, 149, 190))

    def _flowerpot_pro(self):
        s = self._blank((14, 20))
        pygame.draw.polygon(s, (161, 102, 75), [(2, 10), (12, 10), (10, 19), (4, 19)])
        pygame.draw.rect(s, (215, 143, 104), (2, 9, 10, 2))
        pygame.draw.rect(s, (128, 77, 57), (4, 18, 6, 1))
        for bx in (5, 8):
            pygame.draw.line(s, (56, 132, 74), (bx, 10), (bx, 4), 2)
        pygame.draw.circle(s, (250, 204, 106), (4, 4), 3)
        pygame.draw.circle(s, (239, 141, 162), (9, 6), 3)
        pygame.draw.circle(s, (255, 233, 168), (11, 10), 2)
        return self._make_asset(s, material_color=(160, 126, 92))

    def _clock_post_pro(self):
        s = self._blank((20, 50))
        pygame.draw.rect(s, (71, 58, 78), (9, 15, 3, 33))
        pygame.draw.rect(s, (104, 84, 99), (8, 46, 5, 2))
        pygame.draw.circle(s, (68, 60, 82), (10, 11), 9)
        pygame.draw.circle(s, (248, 233, 193), (10, 11), 7)
        pygame.draw.circle(s, (255, 245, 219), (10, 11), 5)
        pygame.draw.line(s, (105, 71, 86), (10, 11), (10, 6), 1)
        pygame.draw.line(s, (105, 71, 86), (10, 11), (14, 12), 1)
        return self._make_asset(s, material_color=(139, 120, 111))

    def _cafe_board_pro(self):
        s = self._blank((20, 22))
        pygame.draw.rect(s, (101, 69, 66), (2, 1, 16, 16))
        pygame.draw.rect(s, (46, 67, 62), (4, 3, 12, 12))
        pygame.draw.line(s, (213, 205, 161), (5, 5), (14, 5), 1)
        pygame.draw.line(s, (213, 205, 161), (6, 8), (13, 8), 1)
        pygame.draw.line(s, (213, 205, 161), (6, 11), (12, 11), 1)
        pygame.draw.line(s, (141, 96, 70), (4, 16), (1, 21), 2)
        pygame.draw.line(s, (141, 96, 70), (16, 16), (19, 21), 2)
        return self._make_asset(s, material_color=(122, 102, 92))

    def _flower_box_pro(self):
        s = self._blank((28, 13))
        pygame.draw.rect(s, (123, 82, 65), (0, 7, 28, 5))
        pygame.draw.rect(s, (180, 124, 94), (0, 7, 28, 1))
        for i in range(2, 27, 5):
            pygame.draw.line(s, (58, 132, 74), (i, 8), (i, 3), 2)
            pygame.draw.circle(s, (242, 154, 173) if i % 2 else (248, 220, 140), (i, 3), 2)
        return self._make_asset(s, material_color=(151, 116, 91))

    def _bush_pro(self):
        s = self._blank((22, 12))
        pygame.draw.circle(s, (53, 141, 84), (5, 8), 5)
        pygame.draw.circle(s, (75, 173, 98), (10, 6), 6)
        pygame.draw.circle(s, (61, 152, 88), (16, 8), 5)
        pygame.draw.circle(s, (114, 206, 124), (10, 5), 2)
        return self._make_asset(s, material_color=(63, 147, 88))

    def _fg_leaves_pro(self):
        s = self._blank((30, 44))
        for pts, col in [(((2, 12), (17, 2), (24, 12), (16, 30)), (35, 66, 50)),
                         (((5, 24), (19, 14), (28, 25), (20, 43)), (46, 84, 64)),
                         (((8, 10), (19, 4), (26, 13), (17, 24)), (28, 53, 42))]:
            pygame.draw.polygon(s, col, pts)
        return self._make_asset(s, material_color=(52, 82, 64))

    def _sign_pro(self):
        s = self._blank((24, 20))
        pygame.draw.rect(s, (66, 58, 92), (0, 2, 24, 15), border_radius=2)
        pygame.draw.rect(s, (255, 158, 132), (2, 4, 20, 11), border_radius=2)
        pygame.draw.rect(s, (224, 238, 116), (7, 6, 10, 6), border_radius=2)
        pygame.draw.rect(s, (255, 210, 160), (3, 14, 18, 1))
        def fx_builder(_):
            out = self._blank((24, 20))
            pygame.draw.rect(out, (255, 145, 120, 75), (0, 1, 24, 15), border_radius=2)
            pygame.draw.rect(out, (255, 241, 146, 120), (6, 5, 12, 8), border_radius=2)
            return out
        return self._make_asset(s, material_color=(225, 142, 122), fx_builder=fx_builder)

    def _canopy_pro(self):
        s = self._blank((26, 16))
        pygame.draw.rect(s, (86, 61, 91), (0, 7, 26, 2))
        cols = [(255, 202, 101), (255, 235, 197)]
        for i in range(0, 26, 4):
            pygame.draw.rect(s, cols[(i // 4) % 2], (i, 2, min(4, 26-i), 6))
        pygame.draw.line(s, (117, 91, 96), (1, 9), (24, 9), 1)
        return self._make_asset(s, material_color=(220, 189, 126))


class CityPilotScene(_City118):
    def __init__(self):
        # réplica controlada do init da v3.118.0 para usar novos assets + overrides
        self._flips = OrderedDict()
        self._flip_limit = 10
        self._glows = {}
        self._sky_cache = OrderedDict()
        self._scaled = OrderedDict()
        self._scaled_limit = 14
        self.rand = random.Random(31190)
        self.lib = SpriteLibraryUltra()
        self.layers = self._build_layers()
        self.sky_period = 960
        self._geometry_view = None
        self._last_state = (0.0, 0, 0.0, 'limpo', 0.5)
        self._build_glows()

    @staticmethod
    def _lit(col, amt):
        return tuple(max(0, min(255, int(c + (255 - c) * amt))) for c in col)

    @staticmethod
    def _shade(col, amt):
        return tuple(max(0, min(255, int(c * amt))) for c in col)

    def _facade_details(self, maps, x, y, w, bottom, seed, palette):
        img = maps['image']; mat = maps['material']; fx = maps['fxmask']; normal = maps['normal']
        hi, lo, lit = palette
        trim = self._lit(hi, 0.17)
        mortar = self._shade(hi, 0.82)
        deep = self._shade(lo, 0.72)
        stone = self._lit(lo, 0.08)
        # cornija, pilastras e plinto
        pygame.draw.rect(img, trim, (x, y, w, 3))
        pygame.draw.rect(img, self._shade(lo, 0.88), (x, y+3, w, 2))
        pygame.draw.rect(img, stone, (x, bottom-7, w, 7))
        pygame.draw.rect(img, deep, (x+w-4, y+3, 4, bottom-y-3))
        for px in (x+1, x+w-6):
            pygame.draw.rect(img, self._lit(hi, 0.08), (px, y+4, 2, max(1, bottom-y-12)))
            pygame.draw.rect(mat, (150, 131, 126), (px, y+4, 2, max(1, bottom-y-12)))
        # textura de alvenaria/tijolo em painéis alternados
        row = 0
        for yy in range(y+8, bottom-11, 8):
            start = x + 4 + (row % 2) * 3
            for xx in range(start, x + w - 8, 10):
                pygame.draw.rect(img, mortar, (xx, yy, 7, 1))
            row += 1
        # janelas embutidas com moldura, reflexo e luz
        col_step = 14 if w < 42 else 16
        window_y0 = y + 12
        for yy in range(window_y0, bottom-26, 18):
            for xx in range(x+6, x+w-9, col_step):
                pygame.draw.rect(img, deep, (xx-1, yy-1, 8, 10))
                pygame.draw.rect(img, (230, 236, 244), (xx, yy, 6, 8))
                inner = lit if ((xx + yy + seed) % 3 == 0) else (173, 205, 224)
                pygame.draw.rect(img, inner, (xx+1, yy+1, 4, 6))
                pygame.draw.line(img, (250, 248, 238), (xx+1, yy+1), (xx+1, yy+6), 1)
                pygame.draw.line(img, deep, (xx+3, yy+1), (xx+3, yy+6), 1)
                pygame.draw.rect(fx, (255, 214, 126, 42 if inner == lit else 18), (xx+1, yy+1, 4, 6))
                pygame.draw.rect(normal, (138, 128, 255), (xx, yy, 6, 8))
        # varandas, jardineiras e toldos de rua
        for yy in range(y+29, bottom-28, 34):
            barw = max(10, w - 12)
            pygame.draw.rect(img, (98, 79, 79), (x+6, yy, barw, 3))
            pygame.draw.rect(img, (134, 114, 113), (x+6, yy+3, barw, 1))
            for vx in range(x+9, x+w-11, 8):
                pygame.draw.rect(img, (108, 92, 90), (vx, yy+3, 1, 4))
            for px in range(x+8, x+w-13, 12):
                pygame.draw.rect(img, (60, 138, 82), (px, yy-3, 8, 3))
                pygame.draw.rect(img, (238, 150, 168) if (px+seed) % 2 else (251, 221, 136), (px+2, yy-5, 3, 3))
        # entrada comercial com marquise e vitrine
        if bottom >= 205:
            door_x = x + max(4, w // 2 - 8)
            pygame.draw.rect(img, (71, 74, 90), (door_x, bottom-21, 16, 16))
            pygame.draw.rect(img, (170, 219, 236), (door_x+2, bottom-19, 12, 12))
            pygame.draw.line(img, (245, 229, 197), (door_x+8, bottom-19), (door_x+8, bottom-7), 2)
            pygame.draw.rect(img, self._lit(hi, 0.20), (x+5, bottom-25, w-10, 4))
            pygame.draw.rect(img, self._shade(lo, 0.85), (x+4, bottom-23, w-8, 2))
            pygame.draw.rect(fx, (255, 214, 126, 75), (door_x+2, bottom-19, 12, 12))
            if w >= 28:
                awn_color = (232, 118, 150) if seed % 2 else (255, 201, 112)
                alt_color = (255, 236, 202)
                awn_y = bottom - 31
                for i, xx in enumerate(range(x+7, x+w-7, 4)):
                    pygame.draw.rect(img, awn_color if i % 2 == 0 else alt_color, (xx, awn_y, min(4, x+w-7-xx), 4))
                pygame.draw.rect(img, (86, 68, 90), (x+6, awn_y+4, w-12, 2))
        # caixas de ar e descidas d'água pequenas
        if w >= 32:
            pipe_x = x + w - 8
            pygame.draw.rect(img, (94, 92, 104), (pipe_x, y+10, 2, max(10, bottom-y-22)))
            pygame.draw.rect(img, (140, 143, 157), (pipe_x+1, y+12, 1, max(8, bottom-y-26)))
            pygame.draw.rect(mat, (115, 118, 130), (pipe_x, y+10, 2, max(10, bottom-y-22)))
            ac_x = x + 5
            pygame.draw.rect(img, (177, 186, 191), (ac_x, y+18, 8, 5))
            pygame.draw.rect(img, (125, 137, 144), (ac_x+1, y+19, 6, 1))
        # base material ligeiramente mais rica
        pygame.draw.rect(mat, (126, 111, 104), (x, bottom-6, w, 6))

    def _draw_extra_sidewalk_details(self, maps, seed):
        img = maps['image']; mat = maps['material']
        # mosaico da calçada e guias mais finos
        for xx in range(0, LOW_W, 12):
            pygame.draw.line(img, (92, 85, 84), (xx, 243), (xx+5, 243), 1)
            if xx % 36 == 0:
                pygame.draw.rect(img, (66, 77, 81), (xx+2, 238, 7, 3))
                pygame.draw.rect(mat, (86, 91, 93), (xx+2, 238, 7, 3))
        # pequenas faixas de flores e arbustos melhor definidos
        rng = random.Random(seed)
        for bx in range(24, LOW_W, 54):
            pygame.draw.rect(img, (128, 91, 78), (bx, 224, 25, 5))
            pygame.draw.rect(img, (51, 132, 76), (bx+2, 220, 21, 5))
            for fx in range(bx+5, bx+21, 7):
                pygame.draw.circle(img, (239, 153, 170) if (fx + seed) % 2 else (249, 219, 135), (fx, 220), 2)
            if rng.random() < 0.5:
                pygame.draw.circle(img, (98, 185, 108), (bx+18, 220), 3)

    def _make_far_variant(self, idx):
        v = super()._make_far_variant(idx)
        img = v.image; mat = v.material
        # antenas, água-furtadas e nuvens urbanas discretas
        rnd = random.Random(11910 + idx)
        for i in range(12, LOW_W, 34):
            if rnd.random() < 0.55:
                x = i + rnd.randint(0, 8)
                y = 116 + rnd.randint(-10, 12)
                pygame.draw.line(img, (149, 156, 210), (x, y), (x, y-10), 1)
                pygame.draw.rect(img, (247, 229, 188), (x-1, y-11, 3, 2))
        pygame.draw.rect(mat, (121, 141, 169), (0, 166, LOW_W, 4))
        return v

    def _make_mid_variant(self, idx):
        v = super()._make_mid_variant(idx)
        img = v.image; geom = v.geometry; mat = v.material
        # aprimora o viaduto com arcadas, guard rail e reflexos d'água
        for x in range(16, LOW_W, 54):
            pygame.draw.arc(img, (116, 128, 169), (x-10, 174, 24, 18), math.pi, math.tau, 2)
            pygame.draw.arc(img, (170, 186, 214), (x-10, 173, 24, 16), math.pi, math.tau, 1)
            pygame.draw.line(geom, (0, 180, 0), (x, 180), (x, 198), 2)
            pygame.draw.line(mat, (108, 124, 150), (x, 180), (x, 198), 2)
        pygame.draw.line(img, (202, 212, 226), (0, 135), (LOW_W, 135), 1)
        for xx in range(0, LOW_W, 18):
            pygame.draw.line(img, (133, 203, 235), (xx, 208), (xx+8, 208), 1)
        return v

    def _make_near_variant(self, idx):
        maps = self._blank_maps()
        # fachadas integradas com textura mais profunda
        self._buildings(maps, 4800+idx, baseline=235, min_h=90, max_h=140,
                        min_w=38, max_w=64, near=True)
        img, mat, geo = maps['image'], maps['material'], maps['geometry']
        pygame.draw.rect(img, (92, 120, 89), (0, 225, LOW_W, 6))
        pygame.draw.rect(img, (182, 170, 152), (0, 231, LOW_W, 6))
        pygame.draw.rect(img, (111, 103, 103), (0, 237, LOW_W, 13))
        pygame.draw.rect(mat, (82, 113, 88), (0, 225, LOW_W, 6))
        pygame.draw.rect(mat, (150, 141, 131), (0, 231, LOW_W, 6))
        pygame.draw.rect(mat, (100, 93, 90), (0, 237, LOW_W, 13))
        pygame.draw.rect(geo, (0, 220, 0), (0, 225, LOW_W, 25))
        self._draw_extra_sidewalk_details(maps, 5100+idx)
        sprites = []
        # árvores, postes e props com ancoragem consistente
        for i, bx in enumerate((14, 108, 210, 316, 418)):
            sprites.append(SpriteInstance('tree_big' if i % 2 == 0 else 'tree_small', bx, 230,
                                          sway=1.15 + 0.18 * i, phase=idx + i * .4))
        for i, bx in enumerate((60, 160, 264, 368)):
            sprites.append(SpriteInstance('lamp', bx, 230, phase=idx*.1 + i*.25, glow=1.0))
        for bx in (80, 184, 286, 392):
            sprites.append(SpriteInstance('flowerpot', bx, 230, phase=idx + bx*.01))
        # placas e caixas florais mais coerentes
        for x in (48, 240, 414):
            pygame.draw.rect(img, (70, 64, 82), (x, 188, 2, 40))
            pygame.draw.rect(geo, (0, 190, 0), (x, 188, 2, 40))
            sprites.append(SpriteInstance('banner', x, 188, sway=.45, phase=.2 + idx))
        for x in (36, 150, 335):
            pygame.draw.rect(img, (77, 67, 79), (x, 204, 44, 3))
            pygame.draw.rect(img, (238, 174, 116), (x+2, 201, 40, 3))
            if x != 150:
                sprites.append(SpriteInstance('awning_flowers', x+9, 205))
        # alguns elementos adicionais para vida urbana
        sprites.extend([
            SpriteInstance('clock_post', 120, 230),
            SpriteInstance('cafe_board', 208, 230),
            SpriteInstance('cafe_board', 352, 230),
            SpriteInstance('bush', 26, 230),
            SpriteInstance('bush', LOW_W-34, 230),
            SpriteInstance('bush', 244, 230),
            SpriteInstance('flowerpot', 136, 230),
        ])
        return ChunkVariant(**maps, sprites=sprites)

    def _make_fg_variant(self, idx):
        maps = self._blank_maps()
        sprites = [
            SpriteInstance('fg_leaves', 0, 241, sway=.7, phase=.8 + idx),
            SpriteInstance('fg_leaves', LOW_W-28, 242, sway=.8, phase=1.3 + idx),
            SpriteInstance('flowerpot', 20, 241, sway=.25, phase=0.5 + idx),
            SpriteInstance('flowerpot', LOW_W-36, 241, sway=.25, phase=0.8 + idx),
        ]
        return ChunkVariant(**maps, sprites=sprites)

    def _build_layers(self):
        far = [self._make_far_variant(i) for i in range(3)]
        mid = [self._make_mid_variant(i) for i in range(3)]
        near = [self._make_near_variant(i) for i in range(5)]
        fg = [self._make_fg_variant(i) for i in range(2)]
        return [
            Layer('far', .12, SCENE_W, far, (0,1,2,1,0,2,0,2,1), (False,)*9),
            Layer('mid', .28, SCENE_W, mid, (0,1,2,0,2,1,2,0,1), (False,)*9),
            Layer('near', .63, SCENE_W, near, (0,1,2,3,4,2,0,4,1,3), (False,)*10),
            Layer('fg', 1.06, SCENE_W, fg, (0,1,0,0,1), (False,)*5, foreground=True),
        ]

    def _draw_sky(self, target, travel, frame, night, phase, climate):
        # mesmo contrato, porém com gradação mais nobre e horizonte menos chapado
        quant = (round(float(night)*20)/20., round(float(phase)*10)/10.)
        grad = self._sky_cache.get(quant)
        if grad is None:
            grad = pygame.Surface((WIDTH, SCENE_H)).convert()
            dusk = max(0., 1. - abs(phase - .48) * 4.)
            top = lerp_color((86, 159, 243), (45, 47, 100), night)
            horizon = lerp_color((190, 217, 246), (99, 93, 148), night)
            lower = lerp_color((224, 212, 205), (94, 84, 128), night)
            top = lerp_color(top, (118, 95, 172), .48 * dusk * (1-night))
            horizon = lerp_color(horizon, (242, 166, 126), .60 * dusk * (1-night))
            lower = lerp_color(lower, (246, 194, 150), .50 * dusk * (1-night))
            split = int(SCENE_H * .58)
            for y in range(SCENE_H):
                if y < split:
                    t = y / max(1, split)
                    col = lerp_color(top, horizon, t)
                else:
                    t = (y - split) / max(1, SCENE_H - split)
                    col = lerp_color(horizon, lower, t)
                pygame.draw.line(grad, col, (0, y), (WIDTH-1, y))
            self._sky_cache[quant] = grad
            if len(self._sky_cache) > 4:
                self._sky_cache.popitem(last=False)
        else:
            self._sky_cache.move_to_end(quant)
        target.blit(grad, (0,0))
        x = int((80 - travel*.019) % (WIDTH+110)) - 35; y = 56
        if night < .55:
            pygame.draw.circle(target, (250, 224, 132), (x, y), 23)
            pygame.draw.circle(target, (255, 242, 181), (x-5, y-5), 7)
        else:
            pygame.draw.circle(target, (227, 232, 245), (x, y), 18)
            pygame.draw.circle(target, (63, 66, 112), (x+7, y-5), 17)
            for i in range(14):
                pygame.draw.rect(target, (228, 226, 241), ((i*79+31)%WIDTH, 12+(i*27)%98, 2, 2))
        cloud = (245, 238, 231) if night < .55 else (109, 105, 150)
        shade = (234, 227, 221) if night < .55 else (88, 84, 131)
        for i in range(7):
            cx = int((i*97+26 - travel*.047) % (WIDTH+120)) - 50
            cy = 35 + (i % 3) * 24
            for dx, dy, r in ((0,0,15), (-12,5,10), (13,5,11), (4,-6,9)):
                pygame.draw.circle(target, cloud, (cx+dx, cy+dy), r)
            pygame.draw.line(target, shade, (cx-10, cy+10), (cx+16, cy+10), 1)
        if climate in ('chuva', 'tempestade'):
            for i in range(22 if climate == 'chuva' else 32):
                xx = int((i*51 - frame*(3.4 if climate == 'chuva' else 5.8)) % (WIDTH+35)) - 15
                yy = int((i*41 + frame*6.2) % SCENE_H)
                pygame.draw.line(target, (133, 177, 217), (xx, yy), (xx-4, yy+11), 1)
