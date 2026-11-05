"""Pixel Rush v3.120.0 — Cidade premium.

Refinamento pesado da Cidade para aproximar a linguagem visual do cenário do
mesmo cuidado e do mesmo estilo pixel-art das skins do jogador: formas mais
limpas, contraste mais forte, contorno mais legível e paleta mais coesa.

Escopo:
- elevar a Cidade ao nível premium sem quebrar alinhamento/parallax;
- aprofundar prédios, árvores, postes, vitrines e calçadas;
- reforçar coesão de paleta e leitura em pixel art.
"""
from collections import OrderedDict
import math
import random
import pygame
from pixelrush_city2_v3119 import CityPilotScene as _City119, SpriteLibraryUltra as _UltraLib
from pixelrush_city2_v3117 import SpriteInstance, ChunkVariant
from pixelrush_city2_v3115 import Layer, WIDTH, LOW_W, SCENE_W, SCENE_H, lerp_color


class SpriteLibraryPremium(_UltraLib):
    """Sprites mais coesos, com silhueta limpa e contraste mais premium."""

    @staticmethod
    def _outline(surface, color=(42, 42, 58)):
        rect = surface.get_bounding_rect()
        if rect.width <= 0 or rect.height <= 0:
            return surface
        mask = pygame.mask.from_surface(surface)
        outline = mask.outline()
        if len(outline) > 1:
            pygame.draw.lines(surface, color, True, outline, 1)
        return surface

    def _build(self):
        super()._build()
        self.assets['tree_small'] = self._tree_premium(size=(28, 38), profile='small')
        self.assets['tree_big'] = self._tree_premium(size=(36, 50), profile='big')
        self.assets['lamp'] = self._lamp_premium()
        self.assets['banner'] = self._banner_premium()
        self.assets['flowerpot'] = self._flowerpot_premium()
        self.assets['clock_post'] = self._clock_post_premium()
        self.assets['cafe_board'] = self._cafe_board_premium()
        self.assets['awning_flowers'] = self._flower_box_premium()
        self.assets['bush'] = self._bush_premium()
        self.assets['fg_leaves'] = self._fg_leaves_premium()
        self.assets['sign'] = self._sign_premium()
        self.assets['canopy'] = self._canopy_premium()

    def _tree_premium(self, size=(28, 38), profile='small'):
        w, h = size
        s = self._blank((w, h))
        outline = (39, 52, 54)
        trunk_dark = (88, 60, 49)
        trunk_mid = (123, 87, 63)
        trunk_light = (153, 118, 84)
        foliage_shadow = (34, 111, 76)
        foliage_mid = (55, 157, 99)
        foliage_light = (112, 214, 136)
        # tronco mais estilizado
        pygame.draw.rect(s, trunk_dark, (w//2 - 4, h - 15, 8, 15))
        pygame.draw.rect(s, trunk_mid, (w//2 - 3, h - 15, 6, 13))
        pygame.draw.line(s, trunk_light, (w//2 - 1, h - 15), (w//2 - 1, h - 3), 1)
        pygame.draw.line(s, trunk_light, (w//2 + 1, h - 14), (w//2 + 1, h - 4), 1)
        if profile == 'big':
            blobs = [
                (w//2 - 11, h - 20, 8, foliage_shadow), (w//2 - 1, h - 29, 11, foliage_mid),
                (w//2 + 9, h - 21, 8, foliage_mid), (w//2 - 4, h - 37, 7, foliage_light),
                (w//2 - 15, h - 28, 6, foliage_mid), (w//2 + 14, h - 29, 6, foliage_shadow),
                (w//2 + 1, h - 18, 10, foliage_light),
            ]
        else:
            blobs = [
                (w//2 - 7, h - 17, 7, foliage_shadow), (w//2 + 5, h - 18, 7, foliage_mid),
                (w//2 - 1, h - 26, 9, foliage_mid), (w//2 - 2, h - 32, 6, foliage_light),
                (w//2 + 8, h - 27, 5, foliage_light),
            ]
        for cx, cy, r, col in blobs:
            pygame.draw.circle(s, col, (cx, cy), r)
        # pequenos blocos de brilho estilo "skin do jogador"
        for px, py in ((w//2 - 5, h - 31), (w//2 + 4, h - 24), (w//2 - 10, h - 23), (w//2 + 1, h - 20)):
            pygame.draw.rect(s, foliage_light, (px, py, 2, 2))
        pygame.draw.line(s, trunk_dark, (w//2, h - 20), (w//2 - 6, h - 25), 1)
        pygame.draw.line(s, trunk_dark, (w//2, h - 20), (w//2 + 6, h - 25), 1)
        self._outline(s, outline)
        return self._make_asset(s, material_color=(73, 151, 96))

    def _lamp_premium(self):
        s = self._blank((18, 42))
        body_dark = (56, 56, 73)
        body_mid = (86, 82, 99)
        body_light = (128, 122, 137)
        glow_core = (255, 236, 170)
        glow_mid = (255, 217, 108)
        pygame.draw.rect(s, body_dark, (8, 5, 2, 27))
        pygame.draw.rect(s, body_mid, (7, 5, 4, 27))
        pygame.draw.rect(s, body_dark, (5, 32, 8, 7))
        pygame.draw.rect(s, body_light, (6, 34, 6, 2))
        pygame.draw.rect(s, body_dark, (9, 7, 5, 2))
        pygame.draw.rect(s, body_dark, (12, 9, 2, 5))
        pygame.draw.rect(s, body_mid, (4, 13, 9, 7))
        pygame.draw.rect(s, glow_mid, (5, 14, 7, 5))
        pygame.draw.rect(s, glow_core, (6, 15, 5, 2))
        self._outline(s)
        def fx_builder(_):
            out = self._blank((18, 42))
            for r, a in ((13, 22), (10, 45), (7, 88), (4, 170)):
                pygame.draw.circle(out, (255, 219, 98, a), (8, 16), r)
            return out
        return self._make_asset(s, material_color=(138, 121, 110), fx_builder=fx_builder)

    def _banner_premium(self):
        s = self._blank((18, 32))
        pole = (56, 55, 78)
        cloth = (232, 98, 159)
        cloth_shade = (195, 76, 135)
        accent = (255, 226, 113)
        pygame.draw.rect(s, pole, (0, 0, 2, 32))
        pygame.draw.rect(s, (86, 81, 108), (1, 0, 1, 32))
        pygame.draw.rect(s, cloth, (3, 3, 12, 20))
        pygame.draw.polygon(s, cloth, [(3, 23), (9, 29), (15, 23)])
        pygame.draw.rect(s, cloth_shade, (13, 4, 2, 19))
        pygame.draw.rect(s, (255, 192, 223), (4, 4, 10, 2))
        pygame.draw.circle(s, accent, (9, 12), 3)
        pygame.draw.rect(s, (255, 245, 188), (7, 16, 4, 2))
        self._outline(s)
        return self._make_asset(s, material_color=(208, 153, 187))

    def _flowerpot_premium(self):
        s = self._blank((16, 20))
        pot_dark = (145, 92, 72)
        pot_mid = (188, 126, 95)
        pot_light = (217, 155, 116)
        pygame.draw.polygon(s, pot_dark, [(2, 10), (14, 10), (12, 19), (4, 19)])
        pygame.draw.rect(s, pot_mid, (2, 9, 12, 2))
        pygame.draw.line(s, pot_light, (3, 10), (12, 10), 1)
        for bx in (6, 9):
            pygame.draw.line(s, (53, 128, 76), (bx, 10), (bx, 4), 2)
        pygame.draw.circle(s, (245, 150, 167), (5, 4), 3)
        pygame.draw.circle(s, (255, 223, 126), (10, 6), 3)
        pygame.draw.circle(s, (255, 241, 183), (12, 10), 2)
        self._outline(s)
        return self._make_asset(s, material_color=(166, 127, 94))

    def _clock_post_premium(self):
        s = self._blank((22, 50))
        body = (62, 58, 77)
        body2 = (89, 82, 100)
        face = (249, 237, 198)
        pygame.draw.rect(s, body, (10, 15, 3, 33))
        pygame.draw.rect(s, body2, (9, 46, 5, 2))
        pygame.draw.circle(s, body, (11, 11), 9)
        pygame.draw.circle(s, face, (11, 11), 7)
        pygame.draw.circle(s, (255, 247, 226), (11, 11), 5)
        pygame.draw.line(s, (126, 82, 88), (11, 11), (11, 7), 1)
        pygame.draw.line(s, (126, 82, 88), (11, 11), (15, 13), 1)
        self._outline(s)
        return self._make_asset(s, material_color=(140, 121, 110))

    def _cafe_board_premium(self):
        s = self._blank((20, 24))
        frame = (99, 69, 67)
        chalk = (52, 76, 72)
        textc = (220, 210, 168)
        pygame.draw.rect(s, frame, (2, 1, 16, 17))
        pygame.draw.rect(s, chalk, (4, 3, 12, 13))
        for y in (5, 8, 11):
            pygame.draw.line(s, textc, (5 if y==5 else 6, y), (14 if y==5 else 13, y), 1)
        pygame.draw.line(s, (140, 96, 70), (4, 17), (1, 23), 2)
        pygame.draw.line(s, (140, 96, 70), (16, 17), (19, 23), 2)
        self._outline(s)
        return self._make_asset(s, material_color=(122, 103, 92))

    def _flower_box_premium(self):
        s = self._blank((28, 14))
        base = (129, 86, 66)
        pygame.draw.rect(s, base, (0, 7, 28, 5))
        pygame.draw.rect(s, (184, 128, 96), (0, 7, 28, 1))
        for i in range(2, 27, 5):
            pygame.draw.line(s, (57, 132, 76), (i, 8), (i, 3), 2)
            pygame.draw.circle(s, (244, 155, 171) if i % 2 else (252, 222, 132), (i, 3), 2)
        self._outline(s)
        return self._make_asset(s, material_color=(151, 116, 92))

    def _bush_premium(self):
        s = self._blank((24, 14))
        pygame.draw.circle(s, (47, 132, 80), (6, 9), 5)
        pygame.draw.circle(s, (65, 164, 97), (12, 7), 6)
        pygame.draw.circle(s, (54, 145, 87), (18, 9), 5)
        pygame.draw.rect(s, (109, 205, 122), (11, 4, 2, 2))
        pygame.draw.rect(s, (109, 205, 122), (8, 6, 2, 2))
        self._outline(s)
        return self._make_asset(s, material_color=(64, 147, 89))

    def _fg_leaves_premium(self):
        s = self._blank((30, 44))
        for pts, col in [(((2, 12), (17, 2), (24, 12), (16, 30)), (31, 63, 48)),
                         (((5, 24), (19, 14), (28, 25), (20, 43)), (43, 84, 63)),
                         (((8, 10), (19, 4), (26, 13), (17, 24)), (26, 52, 40))]:
            pygame.draw.polygon(s, col, pts)
        pygame.draw.rect(s, (72, 111, 87), (13, 11, 2, 2))
        self._outline(s, (21, 39, 31))
        return self._make_asset(s, material_color=(52, 82, 64))

    def _sign_premium(self):
        s = self._blank((24, 20))
        frame = (61, 57, 90)
        neon = (255, 154, 130)
        inner = (228, 244, 124)
        pygame.draw.rect(s, frame, (0, 2, 24, 15))
        pygame.draw.rect(s, neon, (2, 4, 20, 11))
        pygame.draw.rect(s, inner, (7, 6, 10, 6))
        pygame.draw.rect(s, (255, 213, 162), (3, 14, 18, 1))
        self._outline(s)
        def fx_builder(_):
            out = self._blank((24, 20))
            pygame.draw.rect(out, (255, 145, 120, 75), (0, 1, 24, 15))
            pygame.draw.rect(out, (255, 241, 146, 130), (6, 5, 12, 8))
            return out
        return self._make_asset(s, material_color=(225, 142, 122), fx_builder=fx_builder)

    def _canopy_premium(self):
        s = self._blank((28, 16))
        pygame.draw.rect(s, (84, 63, 93), (0, 8, 28, 2))
        cols = [(255, 205, 102), (255, 240, 205)]
        for i in range(0, 28, 4):
            pygame.draw.rect(s, cols[(i // 4) % 2], (i, 2, min(4, 28-i), 6))
        pygame.draw.line(s, (121, 95, 97), (1, 10), (26, 10), 1)
        self._outline(s)
        return self._make_asset(s, material_color=(222, 191, 128))


class CityPilotScene(_City119):
    def __init__(self):
        self._flips = OrderedDict()
        self._flip_limit = 10
        self._glows = {}
        self._sky_cache = OrderedDict()
        self._scaled = OrderedDict()
        self._scaled_limit = 14
        self.rand = random.Random(31200)
        self.lib = SpriteLibraryPremium()
        self.layers = self._build_layers()
        self.sky_period = 960
        self._geometry_view = None
        self._last_state = (0.0, 0, 0.0, 'limpo', 0.5)
        self._build_glows()

    @staticmethod
    def _palette(idx):
        palettes = [
            ((214, 171, 142), (145, 104, 92), (252, 222, 171)),
            ((213, 191, 165), (150, 136, 118), (255, 230, 177)),
            ((190, 162, 186), (128, 103, 136), (252, 220, 178)),
            ((220, 173, 140), (155, 113, 95), (255, 226, 167)),
            ((173, 169, 202), (117, 111, 159), (248, 224, 182)),
            ((197, 153, 165), (135, 97, 111), (255, 222, 171)),
            ((185, 179, 154), (123, 113, 95), (245, 219, 168)),
            ((176, 191, 204), (112, 132, 145), (255, 226, 170)),
        ]
        return palettes[idx % len(palettes)]

    def _facade_details(self, maps, x, y, w, bottom, seed, palette):
        img = maps['image']; mat = maps['material']; fx = maps['fxmask']; normal = maps['normal']
        hi, lo, lit = palette
        outline = self._shade(lo, 0.58)
        trim = self._lit(hi, 0.18)
        bright = self._lit(hi, 0.10)
        stone = self._shade(hi, 0.86)
        deep = self._shade(lo, 0.70)
        glass = (193, 219, 241)
        # contorno principal e cornija
        pygame.draw.rect(img, outline, (x, y, w, bottom-y), 1)
        pygame.draw.rect(img, trim, (x, y, w, 3))
        pygame.draw.rect(img, self._shade(lo, 0.85), (x, y+3, w, 2))
        pygame.draw.rect(img, stone, (x, bottom-8, w, 8))
        pygame.draw.rect(img, deep, (x+w-4, y+3, 4, bottom-y-3))
        # pilastras e filetes verticais
        for px in (x+1, x+w-6):
            pygame.draw.rect(img, bright, (px, y+4, 2, max(1, bottom-y-12)))
            pygame.draw.rect(mat, (150, 131, 126), (px, y+4, 2, max(1, bottom-y-12)))
        # tijolos e juntas leves
        row = 0
        for yy in range(y+9, bottom-11, 8):
            start = x + 4 + (row % 2) * 3
            for xx in range(start, x + w - 8, 9):
                pygame.draw.rect(img, self._shade(hi, 0.78), (xx, yy, 6, 1))
            row += 1
        # janela premium: moldura, peitoril, cruzeta e brilho
        col_step = 14 if w < 42 else 16
        window_y0 = y + 12
        for yy in range(window_y0, bottom-28, 18):
            for xx in range(x+6, x+w-9, col_step):
                pygame.draw.rect(img, outline, (xx-1, yy-1, 8, 10))
                pygame.draw.rect(img, (236, 242, 247), (xx, yy, 6, 8))
                inner = lit if ((xx + yy + seed) % 3 == 0) else glass
                pygame.draw.rect(img, inner, (xx+1, yy+1, 4, 6))
                pygame.draw.line(img, (255, 248, 238), (xx+1, yy+1), (xx+1, yy+6), 1)
                pygame.draw.line(img, self._shade(lo, 0.65), (xx+3, yy+1), (xx+3, yy+6), 1)
                pygame.draw.line(img, self._shade(lo, 0.65), (xx+1, yy+3), (xx+4, yy+3), 1)
                pygame.draw.rect(img, self._lit(hi, 0.20), (xx, yy+8, 6, 1))
                pygame.draw.rect(fx, (255, 214, 126, 48 if inner == lit else 16), (xx+1, yy+1, 4, 6))
                pygame.draw.rect(normal, (138, 128, 255), (xx, yy, 6, 8))
        # varandas com floreira e sombra mais legível
        for yy in range(y+29, bottom-28, 34):
            barw = max(10, w - 12)
            pygame.draw.rect(img, outline, (x+6, yy, barw, 4))
            pygame.draw.rect(img, (116, 92, 92), (x+6, yy, barw, 3))
            pygame.draw.rect(img, (155, 130, 127), (x+6, yy+3, barw, 1))
            for vx in range(x+9, x+w-11, 8):
                pygame.draw.rect(img, (105, 88, 88), (vx, yy+3, 1, 4))
            for px in range(x+8, x+w-13, 12):
                pygame.draw.rect(img, (58, 140, 84), (px, yy-3, 8, 3))
                flower = (241, 156, 174) if (px + seed) % 2 else (253, 223, 133)
                pygame.draw.rect(img, flower, (px+2, yy-5, 3, 3))
        # térreo comercial com toldo, porta e duas vitrines laterais
        if bottom >= 205:
            door_x = x + max(4, w // 2 - 8)
            store_y = bottom-21
            pygame.draw.rect(img, outline, (door_x, store_y, 16, 16))
            pygame.draw.rect(img, (72, 76, 92), (door_x, store_y, 16, 16))
            pygame.draw.rect(img, (173, 220, 238), (door_x+2, store_y+2, 12, 12))
            pygame.draw.line(img, (245, 229, 197), (door_x+8, store_y+2), (door_x+8, bottom-7), 2)
            # vitrines laterais, se couber
            if w >= 36:
                pygame.draw.rect(img, outline, (x+4, bottom-20, 10, 13))
                pygame.draw.rect(img, outline, (x+w-14, bottom-20, 10, 13))
                pygame.draw.rect(img, (171, 214, 230), (x+5, bottom-19, 8, 11))
                pygame.draw.rect(img, (171, 214, 230), (x+w-13, bottom-19, 8, 11))
            pygame.draw.rect(img, self._lit(hi, 0.20), (x+4, bottom-27, w-8, 4))
            pygame.draw.rect(img, self._shade(lo, 0.85), (x+4, bottom-23, w-8, 2))
            pygame.draw.rect(fx, (255, 214, 126, 82), (door_x+2, store_y+2, 12, 12))
            if w >= 28:
                awn_color = (236, 118, 154) if seed % 2 else (255, 205, 108)
                alt_color = (255, 239, 208)
                awn_y = bottom - 31
                for i, xx in enumerate(range(x+6, x+w-6, 4)):
                    pygame.draw.rect(img, awn_color if i % 2 == 0 else alt_color, (xx, awn_y, min(4, x+w-6-xx), 4))
                pygame.draw.rect(img, outline, (x+5, awn_y+4, w-10, 2))
        # pequenas máquinas/tubulações extras
        if w >= 32:
            pipe_x = x + w - 8
            pygame.draw.rect(img, (93, 92, 106), (pipe_x, y+10, 2, max(10, bottom-y-22)))
            pygame.draw.rect(img, (143, 146, 159), (pipe_x+1, y+12, 1, max(8, bottom-y-26)))
            pygame.draw.rect(mat, (115, 118, 130), (pipe_x, y+10, 2, max(10, bottom-y-22)))
            ac_x = x + 5
            pygame.draw.rect(img, outline, (ac_x, y+18, 8, 5))
            pygame.draw.rect(img, (182, 190, 196), (ac_x+1, y+19, 6, 3))
            pygame.draw.line(img, (132, 143, 150), (ac_x+2, y+20), (ac_x+5, y+20), 1)
        # acentua material do plinto
        pygame.draw.rect(mat, (126, 111, 104), (x, bottom-6, w, 6))

    def _buildings(self, maps, seed, baseline, min_h, max_h, min_w, max_w, near=False):
        rng = random.Random(seed)
        x = -3
        n = 0
        while x < LOW_W:
            w = rng.randint(min_w, max_w)
            h = rng.randint(min_h, max_h)
            hi, lo, lit = self._palette(n + seed)
            roof = ('tower','spire','clock',None,None,'spire','clock',None)[(n+seed)%8] if near else ('spire',None,'spire',None)[(n+seed)%4]
            self._draw_building(maps, x, baseline, w+1, h, hi, lo, roof=roof,
                                win_color=(215, 222, 236) if not near else (236,225,205),
                                win_lit=lit, material=(150, 135, 139))
            if near:
                self._facade_details(maps, x, baseline-h, w, baseline, n+seed, (hi,lo,lit))
                if n % 2 == 0 and w > 42:
                    # mansarda/platibanda suave para silhueta mais rica
                    pygame.draw.rect(maps['image'], self._shade(hi, 0.88), (x+5, baseline-h-5, w-10, 4))
                    pygame.draw.rect(maps['image'], self._lit(hi, 0.10), (x+6, baseline-h-4, w-12, 1))
            if near and n % 3 == 0:
                pygame.draw.rect(maps['image'], (96, 92, 104), (x+w-6, baseline-30, 2, 26))
            x += w
            n += 1

    def _draw_extra_sidewalk_details(self, maps, seed):
        img = maps['image']; mat = maps['material']
        for xx in range(0, LOW_W, 12):
            pygame.draw.line(img, (95, 88, 87), (xx, 243), (xx+5, 243), 1)
            pygame.draw.line(img, (198, 188, 175), (xx, 233), (xx+6, 233), 1)
            if xx % 36 == 0:
                pygame.draw.rect(img, (63, 76, 82), (xx+2, 238, 7, 3))
                pygame.draw.rect(mat, (86, 91, 93), (xx+2, 238, 7, 3))
        rng = random.Random(seed)
        for bx in range(22, LOW_W, 54):
            pygame.draw.rect(img, (128, 91, 78), (bx, 224, 27, 5))
            pygame.draw.rect(img, (51, 132, 76), (bx+2, 220, 23, 5))
            for fx in range(bx+5, bx+23, 6):
                col = (241, 156, 174) if (fx + seed) % 2 else (253, 223, 133)
                pygame.draw.rect(img, col, (fx, 219, 2, 2))
            if rng.random() < 0.6:
                pygame.draw.circle(img, (98, 185, 108), (bx+18, 220), 3)
        # filete escuro de separação chão-calçada
        pygame.draw.line(img, (88, 81, 80), (0, 236), (LOW_W, 236), 1)

    def _make_far_variant(self, idx):
        v = super()._make_far_variant(idx)
        img = v.image; mat = v.material
        rnd = random.Random(12010 + idx)
        for i in range(10, LOW_W, 34):
            if rnd.random() < 0.62:
                x = i + rnd.randint(0, 8)
                y = 118 + rnd.randint(-11, 10)
                pygame.draw.line(img, (153, 159, 213), (x, y), (x, y-10), 1)
                pygame.draw.rect(img, (247, 229, 188), (x-1, y-11, 3, 2))
        # faixa de bruma urbana para ligar camadas
        haze = pygame.Surface((LOW_W, 18), pygame.SRCALPHA)
        pygame.draw.rect(haze, (235, 225, 232, 24), (0, 0, LOW_W, 18))
        img.blit(haze, (0, 152))
        pygame.draw.rect(mat, (121, 141, 169), (0, 166, LOW_W, 4))
        return v

    def _make_mid_variant(self, idx):
        v = super()._make_mid_variant(idx)
        img = v.image; geom = v.geometry; mat = v.material
        for x in range(16, LOW_W, 54):
            pygame.draw.arc(img, (116, 128, 169), (x-10, 174, 24, 18), math.pi, math.tau, 2)
            pygame.draw.arc(img, (170, 186, 214), (x-10, 173, 24, 16), math.pi, math.tau, 1)
            pygame.draw.line(geom, (0, 180, 0), (x, 180), (x, 198), 2)
            pygame.draw.line(mat, (108, 124, 150), (x, 180), (x, 198), 2)
        # trem/placa distante coeso com a linguagem
        if idx % 2 == 1:
            tx = 132
            pygame.draw.rect(img, (65, 114, 232), (tx, 140, 40, 9))
            pygame.draw.rect(img, (235, 240, 247), (tx+3, 142, 6, 4))
            pygame.draw.rect(img, (235, 240, 247), (tx+13, 142, 6, 4))
            pygame.draw.rect(img, (235, 240, 247), (tx+23, 142, 6, 4))
            pygame.draw.rect(img, (65, 114, 232), (tx+35, 142, 8, 7))
        for xx in range(0, LOW_W, 18):
            pygame.draw.line(img, (133, 203, 235), (xx, 208), (xx+8, 208), 1)
        return v

    def _make_near_variant(self, idx):
        maps = self._blank_maps()
        self._buildings(maps, 5200+idx, baseline=235, min_h=96, max_h=146, min_w=38, max_w=62, near=True)
        img, mat, geo = maps['image'], maps['material'], maps['geometry']
        # gramado/faixa superior do passeio
        pygame.draw.rect(img, (94, 123, 91), (0, 225, LOW_W, 6))
        pygame.draw.rect(img, (188, 175, 156), (0, 231, LOW_W, 6))
        pygame.draw.rect(img, (112, 103, 102), (0, 237, LOW_W, 13))
        pygame.draw.rect(mat, (82, 113, 88), (0, 225, LOW_W, 6))
        pygame.draw.rect(mat, (154, 144, 132), (0, 231, LOW_W, 6))
        pygame.draw.rect(mat, (100, 93, 90), (0, 237, LOW_W, 13))
        pygame.draw.rect(geo, (0, 220, 0), (0, 225, LOW_W, 25))
        self._draw_extra_sidewalk_details(maps, 5300+idx)
        sprites = []
        # árvores mais bem distribuídas, evitando esconder entradas principais
        for i, bx in enumerate((22, 122, 216, 320, 420)):
            sprites.append(SpriteInstance('tree_big' if i % 2 == 0 else 'tree_small', bx, 230,
                                          sway=1.0 + 0.16 * i, phase=idx + i * .3))
        for i, bx in enumerate((64, 164, 272, 380)):
            sprites.append(SpriteInstance('lamp', bx, 230, phase=idx*.1 + i*.22, glow=1.0))
        for bx in (90, 196, 298, 402):
            sprites.append(SpriteInstance('flowerpot', bx, 230, phase=idx + bx*.01))
        for x in (52, 246, 414):
            pygame.draw.rect(img, (65, 60, 79), (x, 186, 2, 42))
            pygame.draw.rect(geo, (0, 190, 0), (x, 186, 2, 42))
            sprites.append(SpriteInstance('banner', x, 186, sway=.42, phase=.2 + idx))
        # letreiros/toldos premium
        for x in (30, 144, 334):
            pygame.draw.rect(img, (80, 69, 88), (x, 202, 46, 3))
            pygame.draw.rect(img, (239, 177, 118), (x+2, 199, 42, 3))
            if x != 144:
                sprites.append(SpriteInstance('awning_flowers', x+10, 204))
                sprites.append(SpriteInstance('canopy', x+8, 198))
        sprites.extend([
            SpriteInstance('clock_post', 118, 230),
            SpriteInstance('cafe_board', 208, 230),
            SpriteInstance('cafe_board', 350, 230),
            SpriteInstance('bush', 28, 230),
            SpriteInstance('bush', LOW_W-36, 230),
            SpriteInstance('bush', 248, 230),
            SpriteInstance('flowerpot', 140, 230),
            SpriteInstance('sign', 258, 190, glow=0.9),
            SpriteInstance('sign', 74, 188, glow=0.7),
        ])
        return ChunkVariant(**maps, sprites=sprites)

    def _make_fg_variant(self, idx):
        maps = self._blank_maps()
        sprites = [
            SpriteInstance('fg_leaves', 0, 241, sway=.7, phase=.8 + idx),
            SpriteInstance('fg_leaves', LOW_W-28, 242, sway=.8, phase=1.3 + idx),
            SpriteInstance('flowerpot', 20, 241, sway=.25, phase=0.5 + idx),
            SpriteInstance('flowerpot', LOW_W-36, 241, sway=.25, phase=0.8 + idx),
            SpriteInstance('bush', 84, 242, sway=.15, phase=0.4 + idx),
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
        quant = (round(float(night)*20)/20., round(float(phase)*10)/10.)
        grad = self._sky_cache.get(quant)
        if grad is None:
            grad = pygame.Surface((WIDTH, SCENE_H)).convert()
            dusk = max(0., 1. - abs(phase - .48) * 4.)
            top = lerp_color((89, 157, 243), (44, 46, 98), night)
            horizon = lerp_color((192, 220, 247), (97, 91, 147), night)
            lower = lerp_color((230, 214, 204), (93, 82, 126), night)
            top = lerp_color(top, (117, 95, 172), .50 * dusk * (1-night))
            horizon = lerp_color(horizon, (244, 169, 129), .65 * dusk * (1-night))
            lower = lerp_color(lower, (248, 198, 152), .52 * dusk * (1-night))
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
        x = int((82 - travel*.019) % (WIDTH+110)) - 35; y = 56
        if night < .55:
            pygame.draw.circle(target, (251, 226, 134), (x, y), 23)
            pygame.draw.circle(target, (255, 245, 191), (x-5, y-5), 7)
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
        # passarinhos discretos e limpos em certos momentos
        if frame % 280 < 120 and night < 0.5:
            bx = int((400 - travel*0.06) % (WIDTH + 90)) - 30
            by = 74
            for off in (0, 10, 20):
                pygame.draw.line(target, (76, 70, 88), (bx+off, by), (bx+off+4, by-2), 1)
                pygame.draw.line(target, (76, 70, 88), (bx+off+4, by-2), (bx+off+8, by), 1)
        if climate in ('chuva', 'tempestade'):
            for i in range(22 if climate == 'chuva' else 32):
                xx = int((i*51 - frame*(3.4 if climate == 'chuva' else 5.8)) % (WIDTH+35)) - 15
                yy = int((i*41 + frame*6.2) % SCENE_H)
                pygame.draw.line(target, (133, 177, 217), (xx, yy), (xx-4, yy+11), 1)
