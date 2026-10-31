"""Pixel Rush v3.163.0 — Vulcão Premium Definitivo.

Escopo: somente o bioma ``vulcao``.

Objetivo desta versão:
- vulcões mais monumentais e geologia mais rica;
- rios de lava e lagoas com leitura mais líquida;
- ruínas basálticas melhor acabadas e bem encaixadas;
- chão de obsidiana premium, ainda legível para a jogabilidade;
- atmosfera com cinzas, névoa térmica e reflexos noturnos discretos;
- tudo pré-renderizado nos chunks sempre que possível, priorizando Android fraco.

Nenhum outro bioma é alterado.
"""
from __future__ import annotations
import math
import random
import pygame
from pixelrush_biomes2_v3162 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, LH, WIDTH


class ModularBiomeScene(Previous):
    VOLCANO_DISTRICTS = (
        'caldeira', 'obsidiana', 'cascatas', 'fumarolas', 'ruinas_basalticas',
    )
    SKY_HAZE_DAY = (146, 110, 94)
    SKY_HAZE_NIGHT = (120, 86, 92)
    ROCK_DARK = (37, 34, 44)
    ROCK = (55, 47, 58)
    ROCK_MID = (83, 66, 72)
    ROCK_HI = (131, 96, 87)
    BASALT = (46, 40, 51)
    OBSIDIAN = (62, 52, 68)
    ASH = (134, 110, 107)
    LAVA_DARK = (163, 61, 39)
    LAVA = (238, 117, 54)
    LAVA_HI = (255, 207, 132)
    LAVA_WHITE = (255, 239, 181)
    RUNE = (236, 154, 98)

    def __init__(self, biome):
        super().__init__(biome)
        if biome == 'vulcao':
            self._build_volcano_deluxe()
            self._build_ash_haze_deluxe()
            self._build_lava_reflection_masks()
            self._map_cache.clear()
            self._composites.clear()

    # --------------------------- build ---------------------------
    @staticmethod
    def _new_chunk():
        return pygame.Surface((LW, LH), pygame.SRCALPHA)

    def _region(self, index):
        return self.VOLCANO_DISTRICTS[index % len(self.VOLCANO_DISTRICTS)]

    def _build_volcano_deluxe(self):
        self._layers['far'] = [self._far_volcano(i) for i in range(10)]
        self._layers['mid'] = [self._mid_volcano(i) for i in range(12)]
        self._layers['near'] = [self._near_volcano(i) for i in range(14)]

    def _build_ash_haze_deluxe(self):
        self._ash_haze_day = pygame.Surface((WIDTH, 108), pygame.SRCALPHA)
        self._ash_haze_night = pygame.Surface((WIDTH, 108), pygame.SRCALPHA)
        for y in range(108):
            t = y / 107.0
            ad = int(2 + 34 * (t ** 1.7))
            an = int(1 + 18 * (t ** 1.6))
            pygame.draw.line(self._ash_haze_day, (*self.SKY_HAZE_DAY, ad), (0, y), (WIDTH - 1, y), 1)
            pygame.draw.line(self._ash_haze_night, (*self.SKY_HAZE_NIGHT, an), (0, y), (WIDTH - 1, y), 1)
        rng = random.Random(316300)
        for j in range(13):
            x = rng.randrange(0, WIDTH - 90)
            y = rng.randrange(20, 104)
            w = rng.randrange(24, 96)
            pygame.draw.line(self._ash_haze_day, (182, 146, 126, 12 + (j % 4) * 3), (x, y), (x + w, y), 1)
            pygame.draw.line(self._ash_haze_night, (136, 94, 96, 8 + (j % 3) * 2), (x, y), (x + w, y), 1)
            if j % 2 == 0:
                pygame.draw.line(self._ash_haze_day, (156, 122, 110, 8), (x + 6, y + 5), (x + w - 2, y + 5), 1)

    def _build_lava_reflection_masks(self):
        self._floor_glow_day = pygame.Surface((WIDTH, 54), pygame.SRCALPHA)
        self._floor_glow_night = pygame.Surface((WIDTH, 54), pygame.SRCALPHA)
        for y in range(54):
            t = 1.0 - y / 53.0
            ad = int(6 * (t ** 2))
            an = int(12 * (t ** 2.1))
            if ad:
                pygame.draw.line(self._floor_glow_day, (255, 136, 70, ad), (0, y), (WIDTH - 1, y), 1)
            if an:
                pygame.draw.line(self._floor_glow_night, (255, 141, 76, an), (0, y), (WIDTH - 1, y), 1)

    # ------------------------- geometry helpers -------------------------
    @staticmethod
    def _ridge(absolute_x, plane=0):
        a = 2 * math.pi * (absolute_x % (10 * LW)) / (10 * LW)
        if plane == 0:
            return int(173 - 18 * math.sin(2 * a + .35) - 11 * math.sin(5 * a - .4)
                       - 6 * math.sin(8 * a + .25))
        return int(198 - 8 * math.sin(2.7 * a + .5) - 5 * math.sin(6.2 * a - .9))

    @staticmethod
    def _ridge_back(absolute_x):
        a = 2 * math.pi * (absolute_x % (10 * LW)) / (10 * LW)
        return int(150 - 11 * math.sin(1.4 * a + .4) - 5 * math.sin(3.8 * a - 1.0))

    @staticmethod
    def _safe_polyline(surface, points, width, dark, main, hi):
        pygame.draw.lines(surface, dark, False, points, width)
        if width >= 4:
            pygame.draw.lines(surface, main, False, points, max(2, width - 3))
        else:
            pygame.draw.lines(surface, main, False, points, width)
        if len(points) >= 2:
            pygame.draw.line(surface, hi, points[0], points[1], 1)

    def _draw_distant_range(self, s, i):
        for plane, col, bottom in (
            (0, (96, 73, 83), 218),
            (1, (74, 60, 72), 220),
        ):
            for x in range(LW):
                y = self._ridge(i * LW + x, plane)
                pygame.draw.line(s, col, (x, y), (x, bottom), 1)
        for x in range(LW):
            y = self._ridge_back(i * LW + x)
            pygame.draw.line(s, (121, 92, 96), (x, y), (x, 176), 1)

    def _draw_monumental_cone(self, s, cx, ground, height, spread, seed, open_crater=False, dual_flow=False):
        rng = random.Random(seed)
        top = ground - height
        x1 = max(1, cx - spread)
        x2 = min(LW - 2, cx + spread)
        pts = [
            (x1, ground),
            (cx - spread // 2, top + 40),
            (cx - 16, top + 15),
            (cx + rng.randint(-5, 4), top),
            (cx + 18, top + 17),
            (cx + spread // 2, top + 43),
            (x2, ground),
        ]
        pygame.draw.polygon(s, (63, 48, 57), pts)
        pygame.draw.polygon(s, (118, 80, 76), [
            (x1 + 18, ground - 5), (cx - 19, top + 38), (cx - 4, top + 8), (cx + 10, top + 30), (cx + 18, ground - 2)
        ])
        pygame.draw.polygon(s, (45, 39, 49), [
            (cx + 7, top + 14), (cx + 23, top + 22), (x2 - 6, ground), (cx + 16, ground - 8), (cx, top + 35)
        ])
        crater = [
            (cx - 18, top + 10), (cx - 12, top - 2), (cx + 9, top - 3), (cx + 19, top + 11), (cx + 3, top + 15), (cx - 11, top + 14)
        ]
        pygame.draw.polygon(s, (31, 30, 39), crater)
        if open_crater:
            pygame.draw.line(s, self.LAVA_HI, (cx - 5, top + 7), (cx + 4, top + 7), 1)
        for dy in (28, 46, 64, 80):
            xx = cx - 12 - (dy // 8)
            if xx > x1 + 10:
                pygame.draw.line(s, (154, 109, 92), (xx, top + dy), (xx + 7, top + dy - 3), 1)
        route = [(cx + 6, top + 13), (cx + 10, top + 29), (cx + 7, top + 44),
                 (cx + 15, top + 61), (cx + 19, min(ground - 11, top + 91)),
                 (cx + 21, ground - 4)]
        self._safe_polyline(s, route, 8, (78, 41, 43), self.LAVA_DARK, self.LAVA)
        pygame.draw.line(s, self.LAVA_HI, (cx + 9, top + 29), (cx + 7, top + 44), 1)
        if dual_flow:
            route2 = [(cx - 8, top + 18), (cx - 12, top + 35), (cx - 10, top + 49), (cx - 18, top + 68), (cx - 19, ground - 8)]
            self._safe_polyline(s, route2, 5, (83, 41, 43), (198, 77, 49), self.LAVA)
        self._anchored_smoke_plume(s, cx, top + 1, seed + 9, far=True)

    def _draw_far_caldera(self, s, cx, base, width, seed):
        x1 = cx - width // 2
        x2 = cx + width // 2
        top = base - 54
        pygame.draw.polygon(s, (61, 49, 59), [(x1, base), (x1 + 18, top + 18), (cx - 16, top), (cx + 16, top), (x2 - 16, top + 18), (x2, base)])
        pygame.draw.polygon(s, (118, 82, 77), [(x1 + 18, base - 5), (cx - 10, top + 17), (cx + 4, top + 12), (cx + 15, base - 8)])
        pygame.draw.polygon(s, (37, 33, 42), [(cx - 18, top + 3), (cx - 6, top - 5), (cx + 15, top - 3), (cx + 22, top + 5), (cx + 4, top + 9)])
        lake = [(cx - 10, top + 6), (cx - 2, top + 4), (cx + 7, top + 5), (cx + 12, top + 8)]
        self._safe_polyline(s, lake, 4, (88, 45, 45), self.LAVA_DARK, self.LAVA_HI)
        route = [(cx + 9, top + 8), (cx + 15, top + 20), (cx + 13, top + 37), (cx + 19, base - 8)]
        self._safe_polyline(s, route, 5, (87, 44, 45), self.LAVA_DARK, self.LAVA)
        self._anchored_smoke_plume(s, cx, top + 1, seed + 91, far=True, strength=4)

    def _draw_distant_ruins(self, s, x, base, width):
        top = base - 33
        pygame.draw.polygon(s, (50, 45, 56), [(x, base), (x + 7, top + 10), (x + 14, top), (x + width - 15, top + 4), (x + width, base)])
        for px in (x + 8, x + width - 14):
            pygame.draw.polygon(s, (84, 73, 82), [(px, base - 2), (px + 2, top + 8), (px + 6, top + 6), (px + 8, base - 2)])
        pygame.draw.line(s, self.RUNE, (x + width // 2 - 4, top + 12), (x + width // 2 + 4, top + 11), 1)

    def _draw_obsidian_cluster(self, s, x, base, width, height, glow=False):
        pts = [(x, base), (x + 5, base - height + 18), (x + 11, base - height + 9), (x + width // 3, base - height),
               (x + width // 2, base - height + 12), (x + 2 * width // 3, base - height + 5),
               (x + width - 7, base - height + 16), (x + width, base)]
        pygame.draw.polygon(s, (44, 38, 49), pts)
        pygame.draw.polygon(s, (96, 72, 80), [(x + 7, base - 4), (x + width // 3, base - height + 11), (x + width // 2 - 4, base - 7)])
        pygame.draw.line(s, (149, 115, 114), (x + width // 3, base - height + 8), (x + width // 3 + 2, base - 7), 1)
        if glow:
            pygame.draw.line(s, self.LAVA_HI, (x + width // 2, base - height + 18), (x + width // 2 + 5, base - height + 10), 1)

    def _anchored_smoke_plume(self, s, cx, crater_y, seed, far=False, strength=5):
        rng = random.Random(seed)
        base_w = 8 if far else 10
        for n in range(strength):
            yy = crater_y - n * (8 if far else 10)
            ww = base_w + n * (3 if far else 4)
            drift = int(math.sin(seed * 0.07 + n * .75) * (4 + n))
            xx = cx + drift
            col = [(108, 102, 111), (122, 115, 121), (138, 127, 132), (149, 134, 137)][min(3, n)]
            pts = [(xx - ww // 2, yy + 8), (xx - ww // 2 - 3, yy + 4), (xx - 4, yy),
                   (xx + ww // 2, yy - 3), (xx + ww // 2 + 2, yy + 4), (xx + ww // 2, yy + 9)]
            pygame.draw.polygon(s, col, pts)
            if n % 2 == 0:
                pygame.draw.line(s, (164, 145, 142), (xx - 3, yy + 2), (xx + 4, yy), 1)
            if not far and n >= 2 and rng.random() < 0.7:
                pygame.draw.line(s, (93, 89, 96), (xx - ww // 3, yy + 7), (xx + ww // 4, yy + 7), 1)

    def _draw_lava_fall(self, s, x, top, base, tall=False):
        width = 6 if tall else 5
        route = [(x, top), (x - 1, top + 14), (x + 4, top + 31), (x + 2, base - 10)]
        self._safe_polyline(s, route, width, (76, 39, 42), self.LAVA_DARK, self.LAVA)
        pygame.draw.line(s, self.LAVA_HI, route[1], route[2], 1)
        pygame.draw.line(s, (255, 220, 162), (route[-1][0] - 2, base - 3), (route[-1][0] + 3, base - 4), 1)

    def _draw_lava_pool(self, s, cx, y, width):
        pygame.draw.polygon(s, (40, 35, 45), [(cx - width // 2 - 3, y + 5), (cx - width // 2 + 4, y - 1),
                                               (cx + width // 2 - 4, y - 2), (cx + width // 2 + 3, y + 5)])
        pygame.draw.line(s, self.LAVA_DARK, (cx - width // 2 + 3, y + 1), (cx + width // 2 - 4, y + 1), 4)
        pygame.draw.line(s, self.LAVA, (cx - width // 2 + 5, y), (cx + width // 2 - 6, y), 2)
        pygame.draw.line(s, self.LAVA_HI, (cx - 10, y - 1), (cx + 9, y - 1), 1)
        pygame.draw.line(s, self.LAVA_WHITE, (cx - 3, y - 1), (cx + 3, y - 1), 1)

    def _draw_basalt_temple(self, s, cx, base, width, height):
        x = cx - width // 2
        top = base - height
        pygame.draw.rect(s, (34, 33, 43), (x + 8, base - 8, width - 16, 8))
        for px, hh in ((x + 12, 47), (x + width - 20, 43)):
            pygame.draw.polygon(s, (82, 75, 83), [(px, base - 7), (px + 1, base - hh), (px + 7, base - hh - 3), (px + 11, base - 6)])
            pygame.draw.line(s, (143, 113, 100), (px + 4, base - hh + 5), (px + 4, base - 12), 1)
        pygame.draw.polygon(s, (97, 82, 87), [(x + 7, top + 17), (cx, top), (x + width - 8, top + 17), (x + width - 8, top + 24), (x + 7, top + 24)])
        pygame.draw.rect(s, (42, 38, 49), (cx - 8, base - 35, 16, 28))
        pygame.draw.line(s, self.RUNE, (cx - 6, base - 24), (cx + 5, base - 25), 1)
        pygame.draw.line(s, self.LAVA_HI, (cx - 1, base - 22), (cx + 1, base - 22), 1)

    def _draw_basal_plate(self, s, x, y, width, region, phase=0):
        h = 14 + (phase % 2) * 2
        pygame.draw.polygon(s, (41, 36, 47), [(x, y + h), (x + 3, y + 4), (x + width // 3, y),
                                               (x + width - 8, y + 2), (x + width, y + 9), (x + width, y + h)])
        pygame.draw.line(s, (108, 84, 88), (x + 6, y + h - 3), (x + width - 6, y + h - 3), 1)
        pygame.draw.line(s, (138, 103, 90), (x + width // 3, y + 3), (x + width // 3 + 7, y + 1), 1)
        if region == 'obsidiana':
            pygame.draw.line(s, (165, 130, 121), (x + width // 2, y + 4), (x + width - 8, y + 8), 1)

    # --------------------------- layers ---------------------------
    def _far_volcano(self, i):
        s = self._new_chunk()
        region = self._region(i)
        self._draw_distant_range(s, i)

        # detalhes da crista com mais profundidade, sem poluir o céu
        for x in range(11, LW - 8, 18):
            y = self._ridge(i * LW + x, 0) + 5
            pygame.draw.line(s, (135, 102, 95), (x, y), (x + 5, y + 2), 1)
            if (x + i) % 3 == 0:
                pygame.draw.line(s, (81, 68, 77), (x + 1, y + 3), (x + 7, y + 5), 1)

        if i in (1, 6):
            self._draw_monumental_cone(s, 111, 221, 110 if i == 1 else 96, 90 if i == 1 else 82,
                                       316310 + i, open_crater=True, dual_flow=(i == 6))
        elif i == 4:
            self._draw_far_caldera(s, 114, 220, 108, 316340 + i)
        elif region == 'cascatas':
            self._draw_far_caldera(s, 96, 220, 84, 316350 + i)
            self._draw_lava_fall(s, 118, 143, 214, tall=True)
        elif region == 'fumarolas':
            self._draw_obsidian_cluster(s, 72, 216, 41, 47)
            self._draw_obsidian_cluster(s, 122, 218, 58, 41)
            self._anchored_smoke_plume(s, 87, 166, 316360 + i, far=True, strength=4)
            self._anchored_smoke_plume(s, 148, 175, 316370 + i, far=True, strength=3)
        elif region == 'ruinas_basalticas':
            self._draw_obsidian_cluster(s, 42, 218, 52, 37)
            self._draw_distant_ruins(s, 108, 219, 68)
        else:  # obsidiana / fallback
            self._draw_obsidian_cluster(s, 33, 217, 45, 38)
            self._draw_obsidian_cluster(s, 106, 218, 68, 43, glow=True)
            self._draw_obsidian_cluster(s, 176, 219, 37, 29)

        pygame.draw.rect(s, (66, 52, 63), (0, 216, LW, 7))
        pygame.draw.line(s, (101, 77, 80), (0, 216), (LW - 1, 216), 1)
        return s

    def _mid_volcano(self, i):
        s = self._new_chunk()
        rng = random.Random(316500 + i * 97)
        region = self._region(i + 1)
        base = 216
        pygame.draw.rect(s, (68, 54, 64), (0, 209, LW, 15))
        pygame.draw.line(s, (128, 90, 82), (0, 209), (LW - 1, 209), 1)

        if region == 'caldeira':
            self._draw_obsidian_cluster(s, 10, base, 62, 56, glow=True)
            self._draw_obsidian_cluster(s, 86, base, 74, 66)
            self._draw_obsidian_cluster(s, 158, base, 52, 53)
            self._draw_lava_pool(s, 112, 201, 54)
            self._draw_lava_fall(s, 84, 168, 212)
        elif region == 'obsidiana':
            self._draw_obsidian_cluster(s, 12, base, 42, 74)
            self._draw_obsidian_cluster(s, 63, base, 54, 58, glow=True)
            self._draw_obsidian_cluster(s, 125, base, 78, 70)
            self._draw_obsidian_cluster(s, 190, base, 24, 41)
            for px in (54, 97, 156):
                pygame.draw.line(s, (153, 117, 118), (px, 173), (px + 3, 201), 1)
        elif region == 'cascatas':
            self._draw_obsidian_cluster(s, 9, base, 56, 54)
            self._draw_obsidian_cluster(s, 71, base, 52, 68)
            self._draw_obsidian_cluster(s, 133, base, 68, 61)
            self._draw_lava_fall(s, 92, 159, 212, tall=True)
            self._draw_lava_fall(s, 148, 170, 213)
            self._draw_lava_pool(s, 164, 204, 33)
        elif region == 'fumarolas':
            self._draw_obsidian_cluster(s, 12, base, 53, 53)
            self._draw_obsidian_cluster(s, 72, base, 59, 62)
            self._draw_obsidian_cluster(s, 145, base, 56, 50)
            self._draw_obsidian_cluster(s, 186, base, 28, 41)
            self._anchored_smoke_plume(s, 43, 164, 316620 + i, far=False, strength=4)
            self._anchored_smoke_plume(s, 103, 156, 316630 + i, far=False, strength=5)
        else:  # ruinas_basalticas
            self._draw_obsidian_cluster(s, 10, base, 47, 42)
            self._draw_basalt_temple(s, 112, base, 68, 62)
            self._draw_obsidian_cluster(s, 166, base, 47, 48)
            pygame.draw.line(s, self.RUNE, (100, 164), (124, 164), 1)
            pygame.draw.line(s, self.LAVA_HI, (110, 164), (114, 164), 1)

        for xx in range(18, LW - 10, 24):
            yy = 210 + ((xx + i) % 6)
            pygame.draw.line(s, (141, 103, 95), (xx, yy), (xx + 8, yy), 1)
            if xx % 2:
                pygame.draw.rect(s, (98, 74, 78), (xx + 3, yy + 4, 2, 1))
        return s

    def _near_volcano(self, i):
        s = self._new_chunk()
        region = self._region(i + 3)
        rng = random.Random(316800 + i * 163)

        pygame.draw.rect(s, (91, 74, 78), (0, 215, LW, 10))
        pygame.draw.rect(s, (56, 46, 58), (0, 225, LW, 25))
        pygame.draw.line(s, (162, 118, 95), (0, 215), (LW - 1, 215), 1)
        pygame.draw.line(s, (41, 36, 47), (0, 225), (LW - 1, 225), 1)
        pygame.draw.line(s, (111, 76, 75), (0, 243), (LW - 1, 243), 1)

        # Placas maiores de obsidiana para sensação de piso premium.
        start = 6 + (i % 3) * 2
        for idx, x in enumerate(range(start, LW - 20, 28)):
            self._draw_basal_plate(s, x, 220 + (idx % 2), 22 + (idx % 3) * 2, region, phase=idx)
            pygame.draw.line(s, (77, 61, 70), (x + 8, 226), (x + 9, 248), 1)

        fissures = {
            'caldeira': (24, 98, 181),
            'obsidiana': (37, 184),
            'cascatas': (18, 113, 189),
            'fumarolas': (44, 150),
            'ruinas_basalticas': (38, 174),
        }[region]
        for j, cx in enumerate(fissures):
            self._crack_lava_deluxe(s, cx + (i % 3) * 2, 229, 19 + (j % 2) * 7, region, phase=(i + j) % 4)

        rock_sets = {
            'caldeira': ((12, 20, 16), (174, 28, 21)),
            'obsidiana': ((10, 27, 23), (170, 28, 24)),
            'cascatas': ((16, 22, 17), (176, 21, 15)),
            'fumarolas': ((9, 23, 17), (184, 18, 15)),
            'ruinas_basalticas': ((13, 27, 19), (170, 27, 20)),
        }[region]
        for x, w, h in rock_sets:
            self._ground_rock_deluxe(s, x, 216, w, h, region)

        if region == 'ruinas_basalticas':
            self._mini_fore_temple(s, 111, 226)
        elif region == 'fumarolas':
            pygame.draw.line(s, (131, 101, 94), (92, 220), (97, 217), 1)
            self._small_vent(s, 95, 218)
        elif region == 'cascatas':
            pygame.draw.line(s, self.LAVA_HI, (173, 221), (179, 221), 1)
            self._small_lava_channel(s, 177, 219)

        for _ in range(18):
            x = rng.randrange(7, LW - 7)
            y = rng.randrange(236, 249)
            c = (116, 84, 79) if _ % 3 else (151, 100, 84)
            pygame.draw.rect(s, c, (x, y, 2, 1))
        return s

    def _crack_lava_deluxe(self, s, cx, y, w, region, phase=0):
        x = max(2, cx - w // 2)
        r = min(LW - 3, cx + w // 2)
        phase %= 4
        if phase == 0:
            pts = [(x, y + 2), (x + 6, y - 2), (cx - 2, y + 1), (cx + 5, y - 3), (r, y + 1)]
        elif phase == 1:
            pts = [(x, y - 1), (x + 7, y + 2), (cx - 3, y), (cx + 4, y - 2), (r, y - 2)]
        elif phase == 2:
            pts = [(x, y + 2), (x + 5, y + 1), (cx, y - 3), (cx + 4, y - 1), (r, y + 1)]
        else:
            pts = [(x, y), (x + 6, y - 1), (cx - 1, y + 2), (cx + 7, y - 2), (r, y)]
        pygame.draw.lines(s, (42, 36, 46), False, pts, 7)
        pygame.draw.lines(s, self.LAVA_DARK, False, pts, 4)
        pygame.draw.lines(s, self.LAVA, False, pts, 2)
        pygame.draw.line(s, self.LAVA_HI, pts[2], pts[3], 1)
        pygame.draw.line(s, self.LAVA_WHITE, (cx - 1, y - 1), (cx + 2, y - 1), 1)
        if region in ('caldeira', 'cascatas'):
            pygame.draw.rect(s, (255, 231, 144), (cx - 1, y - 2, 2, 1))

    def _ground_rock_deluxe(self, s, x, base, w, h, region):
        y = base - h
        pygame.draw.polygon(s, (42, 38, 49), [(x, base), (x + 3, y + 10), (x + 9, y),
                                               (x + w - 8, y + 4), (x + w - 2, y + 10), (x + w, base)])
        pygame.draw.polygon(s, (101, 77, 81), [(x + 4, base - 2), (x + 8, y + 9),
                                               (x + w // 2, y + 3), (x + w // 2 + 2, base - 3)])
        pygame.draw.line(s, (144, 102, 89), (x + 8, y + 7), (x + w // 2, y + 2), 1)
        pygame.draw.line(s, (57, 51, 61), (x + w // 2 + 1, y + 5), (x + w - 6, base - 4), 1)
        if region == 'obsidiana':
            pygame.draw.line(s, (166, 130, 121), (x + w // 2 + 2, y + 5), (x + w - 7, base - 5), 1)

    def _mini_fore_temple(self, s, cx, base):
        pygame.draw.rect(s, (36, 33, 43), (cx - 10, base, 20, 5))
        pygame.draw.rect(s, (56, 47, 59), (cx - 8, base - 10, 16, 10))
        pygame.draw.line(s, self.RUNE, (cx - 5, base - 6), (cx + 4, base - 6), 1)
        pygame.draw.line(s, self.LAVA_HI, (cx - 1, base - 6), (cx + 1, base - 6), 1)

    def _small_vent(self, s, x, y):
        pygame.draw.polygon(s, (48, 43, 54), [(x - 6, y + 8), (x - 3, y + 2), (x, y), (x + 5, y + 3), (x + 7, y + 8)])
        pygame.draw.line(s, self.LAVA, (x, y + 3), (x + 1, y + 7), 2)
        pygame.draw.polygon(s, (116, 108, 115), [(x - 2, y - 3), (x + 1, y - 6), (x + 4, y - 2), (x + 3, y + 2)])

    def _small_lava_channel(self, s, x, y):
        route = [(x - 3, y + 1), (x - 2, y + 6), (x + 3, y + 11)]
        self._safe_polyline(s, route, 3, (84, 42, 44), self.LAVA_DARK, self.LAVA)

    # --------------------------- final overlay ---------------------------
    def _overlay_harmony(self, surf, frame, climate, night):
        if self.biome != 'vulcao':
            return super()._overlay_harmony(surf, frame, climate, night)

        # horizonte tomado por cinzas leves e atmosfera de calor
        surf.blit(self._ash_haze_night if night > .45 else self._ash_haze_day, (0, 142))

        # brasa fina/poeira vulcânica: pouca quantidade, priorizando clareza
        embers = 8 if self.visual_quality else 4
        for k in range(embers):
            x = int((k * 67 + frame * (0.42 + (k % 3) * .08)) % (WIDTH + 16)) - 8
            y = 208 + ((k * 39 + frame // 3) % 170)
            c = (235, 148, 92, 54) if k % 3 == 0 else (174, 148, 142, 33)
            pygame.draw.rect(surf, c, (x, y, 1 + (k % 2), 1))
            if k % 4 == 0:
                pygame.draw.line(surf, (255, 210, 140, 26), (x - 1, y + 1), (x + 2, y + 1), 1)

        # clima reativo: cinzas e meteoros mais coerentes
        if climate in ('cinzas', 'chuva_meteoros'):
            ashcount = 10 if self.visual_quality else 5
            speed = 1.35 if climate == 'chuva_meteoros' else 0.78
            for k in range(ashcount):
                x = int((k * 61 - frame * speed) % (WIDTH + 28)) - 12
                y = 168 + ((k * 33 + frame * (1.1 if climate == 'chuva_meteoros' else .63)) % 192)
                col = (182, 148, 146, 48) if k % 2 else (152, 130, 142, 38)
                pygame.draw.line(surf, col, (x, y), (x - 2, y + 5), 1)

        # névoa térmica localizada próxima da lava e do chão, sem shader pesado
        waves = 4 if self.visual_quality else 2
        base_y = 410 if night > .3 else 398
        for i in range(waves):
            y = base_y + i * 12
            x0 = int((frame * (0.7 + i * 0.1) + i * 59) % 70)
            for seg in range(0, WIDTH + 40, 70):
                xx = seg - x0
                off = int(2 * math.sin((frame * 0.06) + seg * 0.02 + i))
                pygame.draw.line(surf, (255, 150, 79, 10 if night < .25 else 15), (xx, y + off), (xx + 24, y + off), 1)

        # reflexo noturno da lava na região baixa
        if night > .22:
            surf.blit(self._floor_glow_night, (0, 430))
            for k in range(4 if self.visual_quality else 2):
                x = int((k * 117 + frame * .23) % WIDTH)
                y = 427 + (k % 2) * 6
                pygame.draw.line(surf, (255, 153, 76, 16), (x, y), (x + 8, y), 1)
        else:
            surf.blit(self._floor_glow_day, (0, 432))

        # pequenos brilhos dirigidos nas fachadas/ruínas, sem parecer neon.
        if night > .32:
            for x in (91, 188, 296, 378):
                pygame.draw.line(surf, (255, 173, 106, 17), (x, 332), (x + 6, 334), 1)
                pygame.draw.line(surf, (255, 209, 148, 10), (x + 1, 333), (x + 4, 333), 1)
