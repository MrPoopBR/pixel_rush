"""Pixel Rush v3.136 — refinamento artístico pesado dos 4 biomas extras.

Objetivo: elevar Floresta Densa, Vulcão, Cidade Futurista e Ilhas Celestiais
para um nível visual mais próximo dos biomas aprovados (Cidade/Neve/Deserto),
sem alterar jogabilidade, colisões, geração central, HUD ou custos por frame.
Toda a complexidade é gerada uma única vez por chunk e reutilizada.
"""
import math
import random
import pygame
from pixelrush_biomes2_v3135 import ModularBiomeScene as Previous, TEMAS
from pixelrush_biomes2_v3133 import EXTRA_BIOMES
from pixelrush_biomes2_v3126 import LW, LH, WIDTH, HEIGHT, _rect, _line, _p


def _clamp(v, lo=0, hi=255):
    return lo if v < lo else hi if v > hi else v


def _mix(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


class ModularBiomeScene(Previous):
    # ---------------------------- micro helpers ----------------------------
    def _pix_noise(self, surf, rect, palette, density, seed, size=(1, 1)):
        rng = random.Random(seed)
        x0, y0, w, h = rect
        sw, sh = size
        for _ in range(density):
            x = rng.randrange(x0, max(x0 + 1, x0 + w - sw + 1))
            y = rng.randrange(y0, max(y0 + 1, y0 + h - sh + 1))
            col = palette[rng.randrange(0, len(palette))]
            pygame.draw.rect(surf, col, (x, y, sw, sh))

    def _dither_strip(self, surf, y, x0, x1, c1, c2):
        toggle = 0
        for x in range(x0, x1, 2):
            pygame.draw.line(surf, c1 if toggle % 2 == 0 else c2, (x, y), (min(x + 1, x1), y))
            toggle += 1

    def _tree_rich(self, surf, x, base, h, seed, shape='round'):
        rng = random.Random(seed)
        top = base - h
        # tronco com dois lados e marcas de casca
        pygame.draw.line(surf, (78, 54, 39), (x, base), (x + 1, top + 20), 8)
        pygame.draw.line(surf, (118, 87, 58), (x - 1, base - 3), (x, top + 24), 3)
        pygame.draw.line(surf, (52, 36, 28), (x + 3, base - 1), (x + 4, top + 23), 2)
        for yy in range(top + 26, base - 9, 10):
            pygame.draw.line(surf, (66, 47, 32), (x - 2, yy), (x + 5, yy - 1), 1)
            if yy % 20 == 0:
                pygame.draw.line(surf, (148, 114, 73), (x - 1, yy + 2), (x + 2, yy + 3), 1)
        # galhos
        for off, ang in ((12, -15), (25, 12), (34, -12)):
            by = base - off
            bx = x + (1 if off % 2 else -1)
            pygame.draw.line(surf, (83, 59, 41), (bx, by), (bx + ang // 3, by - 8), 2)
        # copa em massas sobrepostas, com textura de folhas.
        if shape == 'cone':
            blobs = [(-8, 17, 20, 18), (0, 1, 28, 24), (9, -16, 22, 19)]
        elif shape == 'wide':
            blobs = [(-18, 8, 28, 18), (2, -6, 34, 23), (18, 8, 26, 18)]
        else:
            blobs = [(-14, 8, 25, 19), (3, -7, 31, 23), (17, 10, 23, 17)]
        colors = [(35, 101, 67), (69, 136, 84), (116, 177, 103), (170, 209, 123)]
        for i, (dx, dy, rx, ry) in enumerate(blobs):
            rect = pygame.Rect(x + dx - rx // 2, top + 15 + dy - ry // 2, rx, ry)
            pygame.draw.ellipse(surf, colors[i], rect)
        # textura / luz na copa
        for _ in range(30):
            px = x + rng.randint(-24, 24)
            py = top + 2 + rng.randint(0, 36)
            if shape == 'wide' and py > top + 34 and px < x - 18:
                continue
            col = colors[rng.randrange(1, 4)]
            surf.set_at((max(0, min(px, LW - 1)), max(0, min(py, LH - 1))), col)
            if rng.random() < 0.33 and px + 1 < LW:
                surf.set_at((px + 1, py), _mix(col, (220, 242, 168), 0.25))
        for _ in range(12):
            lx = x + rng.randint(-22, 20)
            ly = top + 10 + rng.randint(0, 22)
            pygame.draw.line(surf, (187, 230, 141), (lx, ly), (lx + 2, ly + 1), 1)

    def _fern_cluster(self, surf, x, y, seed, scale=1.0):
        rng = random.Random(seed)
        base = (78, 138, 83)
        hi = (170, 208, 129)
        for i in range(4):
            h = int((9 + rng.randint(0, 6)) * scale)
            spread = int((5 + rng.randint(0, 3)) * scale)
            px = x + i * int(4 * scale)
            pygame.draw.line(surf, (60, 102, 64), (px, y), (px, y - h), 1)
            for k in range(1, h, 3):
                pygame.draw.line(surf, base, (px, y - k), (px - spread, y - k - 1), 1)
                pygame.draw.line(surf, hi, (px, y - k), (px + spread - 1, y - k - 1), 1)

    def _grass_strip(self, surf, y, seed, density=30, h=7):
        rng = random.Random(seed)
        for _ in range(density):
            x = rng.randrange(0, LW - 3)
            hh = h + rng.randrange(-2, 3)
            col = ((83, 126, 80), (115, 168, 96), (168, 204, 118))[rng.randrange(0, 3)]
            pygame.draw.line(surf, col, (x, y), (x + rng.randrange(-2, 3), y - hh), 1)

    def _ruin_rich(self, surf, x, base, w, h, seed, moss=True):
        rng = random.Random(seed)
        top = base - h
        pygame.draw.rect(surf, (117, 126, 110), (x, top, w, h))
        pygame.draw.rect(surf, (153, 164, 146), (x + 4, top + 4, w - 8, h - 8))
        pygame.draw.rect(surf, (87, 98, 84), (x, base - 8, w, 8))
        for off in range(5, w - 6, 10):
            pygame.draw.line(surf, (188, 197, 175), (x + off, top + 6), (x + off + 2, base - 14), 1)
            if off % 2 == 0:
                pygame.draw.line(surf, (100, 109, 91), (x + off + 1, top + 10), (x + off + 4, top + 16), 1)
        # janela/porta quebrada
        if w > 30:
            pygame.draw.rect(surf, (70, 84, 81), (x + w // 2 - 8, top + h // 2 - 6, 16, 18))
            pygame.draw.line(surf, (160, 171, 150), (x + w // 2, top + h // 2 - 6), (x + w // 2, top + h // 2 + 11), 1)
        # rachaduras
        for _ in range(5):
            cx = x + rng.randrange(6, w - 6)
            cy = top + rng.randrange(6, h - 8)
            pygame.draw.line(surf, (90, 101, 86), (cx, cy), (cx + rng.randrange(-5, 6), cy + rng.randrange(5, 11)), 1)
        if moss:
            for xx in range(x + 4, x + w - 7, 8):
                pygame.draw.line(surf, (67, 118, 73), (xx, top + 2), (xx + 3, top + 2), 1)
                if xx % 3 == 0:
                    pygame.draw.line(surf, (49, 92, 63), (xx + 1, base - 8), (xx - 2, base - 17), 2)

    def _basalt_column(self, surf, x, base, w, h, glow=False, seed=0):
        top = base - h
        pts = [(x, base), (x + 4, top + h // 4), (x + w // 3, top + 4), (x + w - 6, top + h // 5), (x + w, base)]
        _p(surf, (54, 48, 57), pts)
        _p(surf, (88, 77, 83), [(x + 4, base - 2), (x + w // 2 - 3, top + 8), (x + w - 6, base - 2)])
        for xx in range(x + 5, x + w - 4, 6):
            pygame.draw.line(surf, (107, 96, 102), (xx, top + 8), (xx, base - 5), 1)
            if xx % 3 == 0:
                pygame.draw.line(surf, (34, 30, 38), (xx + 1, top + 12), (xx + 1, base - 7), 1)
        if glow:
            for yy in range(top + 7, base - 7, 8):
                pygame.draw.line(surf, (244, 124, 66), (x + w // 2, yy), (x + w // 2 + 1, yy + 3), 1)
                pygame.draw.line(surf, (255, 187, 96), (x + w // 2 + 1, yy), (x + w // 2 + 2, yy + 2), 1)

    def _lava_pool(self, surf, x, y, w, h):
        pygame.draw.ellipse(surf, (198, 76, 43), (x, y, w, h))
        pygame.draw.ellipse(surf, (233, 111, 55), (x + 4, y + 2, w - 8, h - 5))
        pygame.draw.ellipse(surf, (255, 188, 96), (x + 10, y + 4, max(8, w - 20), max(4, h - 9)))
        for xx in range(x + 7, x + w - 8, 11):
            pygame.draw.line(surf, (255, 220, 145), (xx, y + h // 2), (xx + 3, y + h // 2 + 1), 1)

    def _future_tower_rich(self, surf, x, base, w, h, seed, color_bias=0):
        rng = random.Random(seed)
        top = base - h
        body = (43 + color_bias, 58 + color_bias, 88 + color_bias)
        edge = (79 + color_bias, 99 + color_bias, 137 + color_bias)
        pygame.draw.rect(surf, body, (x, top, w, h))
        pygame.draw.rect(surf, edge, (x + 3, top + 3, w - 6, h - 5))
        # recortes laterais e teto
        pygame.draw.polygon(surf, (97, 116, 156), ((x + 3, top + 5), (x + w // 2, top - 5), (x + w - 4, top + 5)))
        pygame.draw.line(surf, (100, 236, 246), (x + w // 2, top - 8), (x + w // 2, top + 3), 2)
        if w > 22:
            pygame.draw.rect(surf, (247, 206, 110), (x + w // 2 - 2, top - 5, 5, 2))
        for yy in range(top + 10, base - 10, 11):
            for xx in range(x + 6, x + w - 8, 7):
                col = (102, 238, 246) if (xx + yy + seed) % 3 else (244, 106, 221)
                pygame.draw.rect(surf, col, (xx, yy, 4, 4))
        # letreiro/anel
        if rng.random() < 0.8:
            cy = top + h // 2 + rng.randrange(-8, 9)
            pygame.draw.rect(surf, (80, 99, 140), (x - 3, cy - 2, w + 6, 6))
            pygame.draw.line(surf, (97, 241, 247), (x - 1, cy), (x + w + 1, cy), 2)

    def _sky_island_rich(self, surf, x, y, w, h, seed, temple=False, waterfall=False):
        rng = random.Random(seed)
        # base rochosa
        _p(surf, (96, 92, 114), [(x, y), (x + 10, y + h // 3), (x + w // 3, y + h), (x + w - 14, y + h // 2 + 5), (x + w, y + 6)])
        _p(surf, (126, 119, 145), [(x + 6, y + 4), (x + w // 2 - 3, y + h // 2), (x + w - 9, y + 9)])
        # relva superior
        _p(surf, (120, 176, 111), [(x - 3, y + 3), (x + w // 4, y - 4), (x + w - 10, y + 2), (x + w - 6, y + 11), (x + 5, y + 11)])
        for xx in range(x + 7, x + w - 10, 10):
            pygame.draw.line(surf, (181, 226, 132), (xx, y + 4), (xx + 5, y + 4), 1)
            if xx % 3 == 0:
                pygame.draw.line(surf, (86, 142, 97), (xx + 1, y + 8), (xx + 2, y + 13), 1)
        # raízes / lianas
        for xx in range(x + 9, x + w - 9, 15):
            pygame.draw.line(surf, (87, 102, 107), (xx, y + h // 2), (xx + rng.randrange(-2, 3), y + h + 8), 1)
        if waterfall:
            wx = x + w // 2 - 5
            pygame.draw.rect(surf, (82, 170, 186), (wx, y + h // 3, 10, h + 12))
            pygame.draw.rect(surf, (150, 223, 229), (wx + 2, y + h // 3, 4, h + 12))
            for yy in range(y + h // 3 + 5, y + h + 10, 10):
                pygame.draw.line(surf, (221, 246, 250), (wx + 6, yy), (wx + 8, yy + 4), 1)
        if temple:
            self._temple_rich(surf, x + w // 2 - 27, y + 24)

    def _temple_rich(self, surf, x, base):
        pygame.draw.rect(surf, (184, 193, 208), (x, base - 28, 58, 24))
        pygame.draw.rect(surf, (150, 168, 188), (x + 5, base - 22, 48, 18))
        pygame.draw.polygon(surf, (227, 235, 246), ((x - 4, base - 28), (x + 29, base - 39), (x + 62, base - 28)))
        for xx in (x + 8, x + 22, x + 36, x + 47):
            pygame.draw.rect(surf, (218, 226, 237), (xx, base - 21, 4, 17))
            pygame.draw.line(surf, (165, 178, 197), (xx + 1, base - 18), (xx + 1, base - 6), 1)
        pygame.draw.line(surf, (164, 241, 250), (x + 8, base - 28), (x + 13, base - 36), 2)
        pygame.draw.line(surf, (164, 241, 250), (x + 50, base - 28), (x + 45, base - 36), 2)

    def _sky_steps(self, surf, x, y, steps=4):
        for i in range(steps):
            pygame.draw.rect(surf, (218, 229, 239), (x + i * 11, y + i * 4, 12, 4))
            pygame.draw.rect(surf, (166, 179, 199), (x + i * 11, y + i * 4 + 3, 12, 2))

    # --------------------------- chunk generation ---------------------------
    def _make_chunk(self, layer, index):
        if self.biome not in EXTRA_BIOMES:
            return super()._make_chunk(layer, index)
        if self.biome == 'floresta':
            return self._make_forest_refined(layer, index)
        if self.biome == 'vulcao':
            return self._make_volcano_refined(layer, index)
        if self.biome == 'cidade_futurista':
            return self._make_future_refined(layer, index)
        return self._make_skyisles_refined(layer, index)

    def _make_forest_refined(self, layer, index):
        rng = random.Random(23610 + index * 83 + {'far': 0, 'mid': 1000, 'near': 2000}[layer])
        s = pygame.Surface((LW, LH), pygame.SRCALPHA)
        if layer == 'far':
            _rect(s, (36, 72, 58), 0, 132, LW, 86)
            for x, h, shape in ((14, 56, 'cone'), (54, 82, 'round'), (101, 68, 'wide'), (148, 89, 'round'), (196, 61, 'cone')):
                self._tree_rich(s, x, 208, h + rng.randint(-5, 6), index * 17 + x, shape)
            pygame.draw.rect(s, (56, 95, 72), (0, 206, LW, 16))
            self._pix_noise(s, (0, 142, LW, 68), [(58, 95, 72), (73, 116, 82), (94, 145, 98)], 180, 100 + index, (2, 2))
        elif layer == 'mid':
            theme = index % 4
            # base do terreno
            pts = [(0, 205), (26, 201), (61, 197), (104, 202), (148, 196), (LW, 200), (LW, 236), (0, 236)]
            _p(s, (82, 120, 83), pts)
            _line(s, (156, 197, 135), 0, 201, LW, 201, 2)
            if theme == 0:
                self._tree_rich(s, 36, 207, 78, 200 + index, 'round')
                self._tree_rich(s, 103, 206, 66, 220 + index, 'wide')
                self._tree_rich(s, 186, 207, 72, 240 + index, 'cone')
                for x in (24, 74, 136, 198):
                    self._fern_cluster(s, x, 209 + (x % 5), 260 + x)
            elif theme == 1:
                self._ruin_rich(s, 23, 205, 54, 47, 310 + index)
                self._ruin_rich(s, 117, 204, 72, 57, 340 + index, moss=True)
                self._tree_rich(s, 197, 206, 61, 360 + index, 'wide')
                self._grass_strip(s, 206, 390 + index, density=22, h=8)
            elif theme == 2:
                self._tree_rich(s, 38, 206, 72, 430 + index, 'wide')
                pygame.draw.ellipse(s, (85, 144, 154), (84, 198, 62, 12))
                pygame.draw.ellipse(s, (129, 198, 194), (91, 200, 48, 8))
                for xx in range(94, 136, 11):
                    pygame.draw.line(s, (209, 239, 231), (xx, 202), (xx + 3, 204), 1)
                self._waterfall(s, 160, 170, 15, 35)
                self._tree_rich(s, 197, 207, 61, 470 + index, 'cone')
            else:
                self._tree_rich(s, 25, 208, 61, 510 + index, 'cone')
                self._tree_rich(s, 87, 206, 83, 530 + index, 'round')
                self._tree_rich(s, 160, 207, 71, 550 + index, 'wide')
                self._ruin_rich(s, 187, 205, 33, 35, 590 + index, moss=False)
            self._pix_noise(s, (0, 194, LW, 22), [(95, 133, 91), (62, 102, 68), (167, 201, 132)], 70, 670 + index, (2, 1))
        else:
            # camada próxima discreta, com detalhe forte porém abaixo da área dos perigos
            _p(s, (100, 136, 88), [(0, 223), (24, 220), (67, 219), (130, 222), (177, 220), (LW, 221), (LW, 250), (0, 250)])
            _line(s, (183, 210, 149), 0, 228, LW, 228, 2)
            _rect(s, (121, 92, 67), 0, 234, LW, 16)
            theme = index % 4
            if theme == 0:
                self._tree_rich(s, 20, 225, 46, 700 + index, 'cone')
                self._tree_rich(s, 195, 225, 49, 730 + index, 'cone')
                for x in (58, 84, 112, 142, 169):
                    self._fern_cluster(s, x, 227 + (x % 3), 740 + x, 0.85)
            elif theme == 1:
                self._ruin_rich(s, 18, 227, 51, 34, 800 + index, moss=True)
                self._ruin_rich(s, 153, 228, 57, 38, 850 + index, moss=False)
                self._fern_cluster(s, 84, 228, 890 + index, 0.9)
            elif theme == 2:
                pygame.draw.ellipse(s, (88, 146, 151), (53, 216, 108, 16))
                pygame.draw.ellipse(s, (151, 208, 206), (65, 219, 84, 10))
                self._tree_rich(s, 28, 224, 39, 900 + index, 'wide')
                self._tree_rich(s, 196, 225, 40, 930 + index, 'wide')
                self._waterfall(s, 166, 205, 10, 25)
            else:
                self._tree_rich(s, 17, 226, 37, 970 + index, 'cone')
                self._tree_rich(s, 113, 223, 44, 995 + index, 'round')
                self._tree_rich(s, 206, 227, 34, 1010 + index, 'cone')
            for x in range(8, LW, 20):
                _line(s, (153, 110, 80), x, 240, x + 8, 240)
            self._grass_strip(s, 229, 1040 + index, density=24, h=5)
        return s

    def _make_volcano_refined(self, layer, index):
        rng = random.Random(24610 + index * 79 + {'far': 0, 'mid': 1000, 'near': 2000}[layer])
        s = pygame.Surface((LW, LH), pygame.SRCALPHA)
        if layer == 'far':
            # horizonte vulcânico
            _p(s, (74, 51, 56), [(0, 202), (20, 172), (46, 148), (66, 165), (92, 136), (118, 154), (150, 124), (192, 149), (220, 182), (LW, 202), (LW, 250), (0, 250)])
            _p(s, (100, 74, 76), [(0, 202), (42, 170), (88, 145), (141, 131), (176, 147), (LW, 188), (LW, 250), (0, 250)])
            # lava ao longe
            pygame.draw.line(s, (238, 104, 56), (134, 146), (144, 164), 2)
            pygame.draw.line(s, (255, 186, 94), (140, 150), (147, 165), 1)
            for x, y, sc in ((30, 78, 0.85), (118, 66, 1.15), (194, 86, 0.9)):
                self._cloud(s, x, y, sc, (128, 110, 117))
            self._pix_noise(s, (0, 146, LW, 58), [(99, 71, 75), (72, 50, 57), (137, 104, 97)], 140, 1200 + index, (2, 2))
        elif layer == 'mid':
            theme = index % 4
            _p(s, (92, 71, 75), [(0, 209), (18, 205), (58, 197), (96, 199), (137, 192), (LW, 197), (LW, 236), (0, 236)])
            _line(s, (150, 110, 92), 0, 200, LW, 200, 1)
            if theme == 0:
                self._basalt_column(s, 16, 206, 31, 52, False, 1300 + index)
                self._basalt_column(s, 63, 205, 37, 73, True, 1330 + index)
                self._basalt_column(s, 121, 206, 42, 66, False, 1360 + index)
                self._basalt_column(s, 183, 206, 31, 51, True, 1390 + index)
            elif theme == 1:
                self._lava_pool(s, 36, 200, 74, 17)
                self._basalt_column(s, 126, 206, 36, 55, False, 1420 + index)
                self._basalt_column(s, 171, 205, 43, 71, True, 1460 + index)
            elif theme == 2:
                self._basalt_column(s, 22, 206, 37, 62, False, 1500 + index)
                self._basalt_column(s, 73, 205, 31, 51, False, 1540 + index)
                self._lava_pool(s, 121, 198, 96, 18)
                pygame.draw.line(s, (255, 146, 77), (142, 195), (142, 171), 2)
                pygame.draw.line(s, (255, 204, 101), (144, 197), (147, 176), 1)
            else:
                self._basalt_column(s, 13, 205, 44, 79, True, 1580 + index)
                self._basalt_column(s, 77, 206, 46, 58, False, 1610 + index)
                self._basalt_column(s, 145, 206, 47, 68, True, 1640 + index)
                pygame.draw.ellipse(s, (111, 97, 103), (170, 154, 34, 16))
                pygame.draw.ellipse(s, (144, 124, 122), (177, 149, 22, 9))
            self._pix_noise(s, (0, 192, LW, 28), [(76, 58, 62), (122, 96, 98), (165, 129, 102)], 70, 1680 + index, (2, 1))
        else:
            _p(s, (93, 72, 74), [(0, 223), (18, 219), (61, 218), (121, 221), (171, 219), (LW, 220), (LW, 250), (0, 250)])
            _line(s, (195, 126, 77), 0, 228, LW, 228, 2)
            _rect(s, (85, 66, 71), 0, 234, LW, 16)
            theme = index % 4
            if theme == 0:
                self._basalt_column(s, 12, 228, 47, 54, True, 1700 + index)
                self._basalt_column(s, 177, 228, 40, 47, False, 1730 + index)
                self._lava_pool(s, 78, 220, 61, 12)
            elif theme == 1:
                self._basalt_column(s, 24, 227, 32, 45, False, 1760 + index)
                self._basalt_column(s, 77, 228, 46, 61, True, 1790 + index)
                self._basalt_column(s, 160, 228, 48, 55, False, 1820 + index)
            elif theme == 2:
                pygame.draw.polygon(s, (60, 49, 57), ((19, 229), (48, 205), (68, 229)))
                pygame.draw.polygon(s, (60, 49, 57), ((161, 229), (190, 201), (213, 229)))
                self._lava_pool(s, 82, 219, 68, 14)
                pygame.draw.line(s, (255, 174, 86), (113, 218), (113, 205), 2)
            else:
                self._basalt_column(s, 16, 228, 50, 58, True, 1850 + index)
                self._lava_pool(s, 88, 220, 43, 12)
                self._basalt_column(s, 150, 228, 55, 63, True, 1880 + index)
            for x in range(8, LW, 21):
                _line(s, (115, 89, 86), x, 240, x + 9, 240)
            self._pix_noise(s, (0, 235, LW, 11), [(99, 73, 70), (142, 104, 79), (185, 132, 92)], 48, 1910 + index, (2, 1))
        return s

    def _make_future_refined(self, layer, index):
        rng = random.Random(25610 + index * 71 + {'far': 0, 'mid': 1000, 'near': 2000}[layer])
        s = pygame.Surface((LW, LH), pygame.SRCALPHA)
        if layer == 'far':
            _rect(s, (32, 48, 81), 0, 138, LW, 74)
            silhouette = [(0, 201)]
            xs = [0, 22, 41, 67, 89, 118, 141, 165, 192, LW]
            hs = [46, 62, 51, 80, 70, 58, 77, 54, 66]
            for x, h in zip(xs[:-1], hs):
                silhouette.extend([(x, 201 - h), (x + 18, 201 - h), (x + 18, 201)])
            silhouette.extend([(LW, 201), (LW, 250), (0, 250)])
            _p(s, (43, 61, 99), silhouette)
            for x in (18, 55, 92, 130, 168, 206):
                pygame.draw.rect(s, (65, 88, 129), (x, 161 + (x % 9), 16, 40 + (x % 13)))
                pygame.draw.line(s, (101, 233, 244), (x + 8, 154 + (x % 9)), (x + 8, 161 + (x % 9)), 2)
            if index % 2 == 0:
                pygame.draw.line(s, (243, 99, 223), (16, 167), (208, 167), 2)
                for x in (30, 70, 110, 150, 190):
                    pygame.draw.line(s, (110, 239, 245), (x, 167), (x, 188), 1)
            self._pix_noise(s, (0, 152, LW, 48), [(44, 60, 91), (55, 74, 117), (82, 106, 151)], 120, 2000 + index, (2, 2))
        elif layer == 'mid':
            _rect(s, (47, 63, 101), 0, 187, LW, 40)
            _rect(s, (87, 108, 149), 0, 173, LW, 7)
            theme = index % 4
            if theme == 0:
                self._future_tower_rich(s, 12, 208, 40, 63, 2100 + index)
                self._future_tower_rich(s, 69, 208, 31, 83, 2140 + index, 4)
                self._future_tower_rich(s, 116, 208, 44, 56, 2180 + index)
                self._future_tower_rich(s, 171, 208, 35, 74, 2220 + index, 2)
            elif theme == 1:
                pygame.draw.rect(s, (75, 96, 139), (15, 188, 70, 23))
                pygame.draw.rect(s, (104, 240, 246), (20, 193, 60, 4))
                self._future_tower_rich(s, 103, 208, 30, 68, 2260 + index)
                pygame.draw.rect(s, (71, 92, 133), (149, 182, 58, 29))
                pygame.draw.rect(s, (242, 102, 223), (154, 188, 47, 4))
                pygame.draw.line(s, (104, 240, 246), (15, 182), (206, 182), 1)
            elif theme == 2:
                self._future_tower_rich(s, 5, 208, 34, 58, 2300 + index)
                self._future_tower_rich(s, 56, 208, 51, 88, 2340 + index, 6)
                self._future_tower_rich(s, 132, 208, 29, 61, 2380 + index)
                self._future_tower_rich(s, 174, 208, 36, 52, 2420 + index, 2)
            else:
                pygame.draw.rect(s, (73, 94, 136), (14, 187, 48, 23))
                pygame.draw.rect(s, (240, 103, 221), (18, 192, 40, 3))
                self._future_tower_rich(s, 80, 208, 36, 86, 2460 + index)
                pygame.draw.rect(s, (73, 94, 136), (134, 187, 73, 25))
                pygame.draw.rect(s, (103, 241, 247), (139, 193, 64, 3))
                pygame.draw.line(s, (102, 238, 246), (90, 177), (90, 143), 2)
            self._pix_noise(s, (0, 178, LW, 34), [(72, 92, 132), (52, 69, 106), (128, 152, 191)], 72, 2500 + index, (2, 1))
        else:
            _rect(s, (54, 70, 105), 0, 221, LW, 8)
            _line(s, (92, 240, 248), 0, 228, LW, 228, 2)
            _rect(s, (72, 84, 112), 0, 230, LW, 4)
            _rect(s, (46, 57, 79), 0, 234, LW, 16)
            theme = index % 4
            if theme == 0:
                self._future_tower_rich(s, -2, 229, 48, 70, 2600 + index)
                self._future_tower_rich(s, 81, 229, 36, 92, 2640 + index)
                self._future_tower_rich(s, 159, 229, 50, 66, 2680 + index, 3)
            elif theme == 1:
                self._future_tower_rich(s, 20, 229, 28, 61, 2720 + index)
                pygame.draw.rect(s, (77, 96, 141), (73, 194, 78, 26))
                pygame.draw.rect(s, (103, 240, 246), (78, 198, 68, 4))
                self._future_tower_rich(s, 177, 229, 30, 64, 2760 + index)
            elif theme == 2:
                self._future_tower_rich(s, 0, 229, 36, 67, 2800 + index, 2)
                self._future_tower_rich(s, 62, 229, 42, 87, 2840 + index, 6)
                self._future_tower_rich(s, 148, 229, 38, 67, 2880 + index)
            else:
                pygame.draw.rect(s, (67, 85, 122), (17, 193, 59, 28))
                pygame.draw.rect(s, (242, 106, 221), (21, 198, 51, 4))
                self._future_tower_rich(s, 101, 229, 34, 89, 2920 + index)
                pygame.draw.rect(s, (67, 85, 122), (151, 193, 57, 28))
                pygame.draw.rect(s, (103, 241, 247), (156, 199, 47, 4))
            for x in range(10, LW, 21):
                _line(s, (98, 112, 140), x, 240, x + 9, 240)
            self._pix_noise(s, (0, 236, LW, 10), [(81, 97, 129), (45, 56, 80), (132, 151, 177)], 44, 2960 + index, (2, 1))
        return s

    def _make_skyisles_refined(self, layer, index):
        rng = random.Random(26610 + index * 89 + {'far': 0, 'mid': 1000, 'near': 2000}[layer])
        s = pygame.Surface((LW, LH), pygame.SRCALPHA)
        if layer == 'far':
            for x, y, sc in ((18, 90, 1.0), (106, 66, 1.15), (186, 96, 0.92)):
                self._cloud(s, x, y, sc, (240, 247, 255))
            self._sky_island_rich(s, 9, 126, 73, 44, 3000 + index, temple=False, waterfall=False)
            self._sky_island_rich(s, 123, 103, 83, 55, 3040 + index, temple=False, waterfall=False)
            self._pix_noise(s, (0, 95, LW, 68), [(233, 243, 255), (190, 226, 241), (161, 210, 230)], 90, 3080 + index, (2, 2))
        elif layer == 'mid':
            for x, y, sc in ((27, 109, 1.1), (150, 84, 0.95)):
                self._cloud(s, x, y, sc, (226, 239, 255))
            theme = index % 4
            if theme == 0:
                self._sky_island_rich(s, 20, 158, 80, 48, 3120 + index, temple=False, waterfall=False)
                self._sky_island_rich(s, 124, 142, 84, 54, 3160 + index, temple=True, waterfall=False)
            elif theme == 1:
                self._sky_island_rich(s, 22, 154, 70, 43, 3200 + index, temple=False, waterfall=True)
                self._sky_island_rich(s, 118, 146, 94, 58, 3240 + index, temple=False, waterfall=False)
                self._sky_steps(s, 91, 151)
            elif theme == 2:
                self._sky_island_rich(s, 14, 161, 62, 38, 3280 + index, temple=False, waterfall=False)
                self._sky_island_rich(s, 90, 145, 63, 44, 3320 + index, temple=False, waterfall=True)
                self._sky_island_rich(s, 161, 157, 61, 39, 3360 + index, temple=False, waterfall=False)
            else:
                self._sky_island_rich(s, 26, 156, 80, 46, 3400 + index, temple=True, waterfall=False)
                self._sky_island_rich(s, 150, 151, 58, 36, 3440 + index, temple=False, waterfall=True)
            self._pix_noise(s, (0, 136, LW, 72), [(185, 228, 201), (150, 205, 182), (208, 239, 233)], 80, 3480 + index, (2, 1))
        else:
            _rect(s, (132, 151, 176), 0, 221, LW, 8)
            _line(s, (205, 239, 255), 0, 228, LW, 228, 2)
            _rect(s, (176, 184, 198), 0, 230, LW, 4)
            _rect(s, (120, 130, 148), 0, 234, LW, 16)
            theme = index % 4
            if theme == 0:
                self._sky_island_rich(s, 5, 187, 55, 35, 3520 + index, temple=False, waterfall=False)
                self._sky_island_rich(s, 166, 181, 56, 38, 3560 + index, temple=False, waterfall=False)
                for x in (82, 115, 132):
                    _p(s, (160, 236, 247), [(x, 218), (x + 5, 207), (x + 10, 218), (x + 5, 227)])
            elif theme == 1:
                self._sky_island_rich(s, 17, 180, 74, 43, 3600 + index, temple=False, waterfall=False)
                self._sky_island_rich(s, 156, 190, 50, 31, 3640 + index, temple=False, waterfall=False)
                self._waterfall(s, 118, 186, 11, 32)
            elif theme == 2:
                self._sky_island_rich(s, 30, 188, 52, 33, 3680 + index, temple=False, waterfall=False)
                self._sky_island_rich(s, 95, 176, 66, 42, 3720 + index, temple=True, waterfall=False)
                self._sky_island_rich(s, 174, 188, 46, 29, 3760 + index, temple=False, waterfall=False)
            else:
                self._temple_rich(s, 84, 203)
                self._sky_island_rich(s, 8, 191, 42, 26, 3800 + index, temple=False, waterfall=False)
                self._sky_island_rich(s, 177, 191, 41, 26, 3840 + index, temple=False, waterfall=False)
                self._sky_steps(s, 90, 210, 3)
            for x in range(8, LW, 20):
                _line(s, (155, 166, 180), x, 240, x + 8, 240)
            self._pix_noise(s, (0, 235, LW, 10), [(142, 157, 175), (120, 130, 148), (191, 205, 220)], 44, 3880 + index, (2, 1))
        return s
