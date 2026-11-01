"""v3.148 — remove vazamentos/borrões azuis da Floresta Densa.

Correção pontual na camada distante: fecha vazios grandes do horizonte
com massas baixas de vegetação, mantendo a leitura leve e contínua.
"""
import math
import pygame
from pixelrush_biomes2_v3147 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW


class ModularBiomeScene(Previous):
    _FOREST_PERIOD = LW * 4

    def _mid_gap_fill(self, surface, index):
        """Preenche vazios grandes da camada média que deixavam o céu aparecer como borrão."""
        dark = (95, 141, 121)
        mid = (117, 160, 139)
        light = (139, 179, 157)
        groups = [
            (48, 199, 17, 10),
            (82, 201, 13, 8),
            (160, 200, 18, 9),
            (193, 202, 12, 7),
        ]
        for n, (cx, base_y, half_w, rise) in enumerate(groups):
            top = int(base_y - rise - math.sin((index + n) * 0.9) * 1.0)
            pts = [
                (cx-half_w, base_y),
                (cx-half_w+3, top+8),
                (cx-half_w+7, top+4),
                (cx-5, top+2),
                (cx, top),
                (cx+5, top+2),
                (cx+half_w-6, top+4),
                (cx+half_w-2, top+8),
                (cx+half_w, base_y),
            ]
            pygame.draw.polygon(surface, dark, pts)
            pygame.draw.line(surface, mid, (cx-half_w+5, top+6), (cx-1, top+3), 1)
            pygame.draw.line(surface, light, (cx+1, top+4), (cx+7, top+5), 1)

    @classmethod
    def _ridge_height(cls, absolute_x, plane):
        return super()._ridge_height(absolute_x, plane)

    def _fill_horizon_voids(self, surface, index, heights):
        """Fecha janelas de céu largas demais no miolo inferior do horizonte.
        Usa uma faixa baixa e irregular de vegetação distante, sutil e contínua.
        """
        dark = (74, 118, 106)
        mid = (96, 142, 128)
        light = (120, 162, 146)

        # 1) linha-base contínua, mas ondulada, para impedir "borrões" de céu.
        band_top = []
        for x in range(LW):
            a = 2.0 * math.pi * ((index % 4) * LW + x) / (LW * 4)
            y = int(186 - 5.0 * math.sin(a * 1.3 + 0.4)
                      - 3.0 * math.sin(a * 3.1 - 1.1)
                      - 1.2 * math.sin(a * 6.2 + 0.8))
            band_top.append(y)
            pygame.draw.line(surface, dark, (x, y), (x, 214), 1)
        # textura horizontal leve na faixa contínua
        for x in range(4, LW, 9):
            y = band_top[x] + (x % 3)
            pygame.draw.line(surface, mid if (x // 9) % 2 else light,
                             (x, y), (min(LW - 1, x + 2), y), 1)

        # 2) massas orgânicas em alguns trechos para quebrar a silhueta contínua.
        patches = [
            (30, 207, 13, 8),
            (82, 206, 24, 10),
            (126, 208, 17, 7),
            (176, 207, 21, 9),
        ]
        for n, (cx, base_y, half_w, rise) in enumerate(patches):
            cx = int(cx + (n % 2) * 2)
            top = int(base_y - rise - math.sin((index + n) * 1.15) * 1.2)
            pts = [
                (cx - half_w, base_y),
                (cx - half_w + 4, top + 8),
                (cx - half_w + 8, top + 4),
                (cx - 4, top + 1),
                (cx, top),
                (cx + 5, top + 2),
                (cx + half_w - 8, top + 5),
                (cx + half_w - 3, top + 8),
                (cx + half_w, base_y),
            ]
            pygame.draw.polygon(surface, dark, pts)
            pygame.draw.line(surface, mid, (cx - half_w + 6, top + 7), (cx - 1, top + 3), 1)
            pygame.draw.line(surface, light, (cx, top + 4), (cx + 6, top + 5), 1)

    def _far_ridge(self, surface, index):
        # Base da v3.147.0.
        colors = ((111, 155, 149), (83, 128, 117), (57, 102, 87))
        offset = (index % 4) * LW
        heights = []
        for plane, color in enumerate(colors):
            top = [self._ridge_height(offset + x, plane) for x in range(LW)]
            heights.append(top)
            for x, y in enumerate(top):
                pygame.draw.line(surface, color, (x, y), (x, 218), 1)
        for local_x in (18, 57, 106, 154, 201):
            y = heights[1][local_x] + 2
            shade = (92, 138, 127) if (local_x + index) % 2 else (100, 143, 134)
            pygame.draw.line(surface, shade, (local_x - 5, y + 4), (local_x, y - 2), 1)
            pygame.draw.line(surface, shade, (local_x, y - 2), (local_x + 5, y + 4), 1)
            pygame.draw.line(surface, (120, 166, 151), (local_x - 3, y + 1), (local_x + 2, y), 1)
        for n, cx in enumerate((22, 58, 96, 142, 174, 210)):
            top = (166 if n in (3, 4) else 176) + ((index * 3 + n * 7) % 9)
            half = (11, 14, 11, 19, 18, 10)[n]
            dark = (78, 119, 108) if n % 2 else (86, 128, 117)
            light = (110, 151, 135)
            outline = [
                (cx-half, 213), (cx-half+2, top+15),
                (cx-half+5, top+9), (cx-half+8, top+12),
                (cx-4, top+3), (cx, top), (cx+4, top+3),
                (cx+half-7, top+7), (cx+half-4, top+5),
                (cx+half, top+12), (cx+half-2, 214),
            ]
            pygame.draw.polygon(surface, dark, outline)
            pygame.draw.line(surface, light, (cx-6, top+9), (cx+2, top+6), 1)
            pygame.draw.line(surface, (65, 108, 97), (cx+3, top+13), (cx+8, top+16), 1)
        for k in range(34):
            x = (23 + k * 37 + (index * 13)) % LW
            y = heights[1][x] + 3 + (k % 5)
            if y < 216:
                col = (119, 165, 145) if k % 3 else (66, 110, 99)
                pygame.draw.line(surface, col, (x, y), (min(LW - 1, x + 2), y), 1)
        # Fechamento seletivo dos vazios que viravam borrões azuis.
        self._fill_horizon_voids(surface, index, heights)

    def _forest_chunk(self, layer, index):
        s = super()._forest_chunk(layer, index)
        if layer == 'mid':
            self._mid_gap_fill(s, index)
        return s
