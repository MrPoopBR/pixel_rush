"""v3.144 — passe premium de profundidade e microdetalhes na Floresta."""
import math
import random
import pygame
from pixelrush_biomes2_v3143 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, LH, WIDTH, _line


class ModularBiomeScene(Previous):
    def _vine_strand(self, s, x, y, length, seed, bright=False):
        rng = random.Random(seed)
        col = (88, 131, 90) if not bright else (118, 171, 113)
        sway = rng.choice((-1, 0, 1))
        for i in range(length):
            xx = x + (i // 4) * sway
            yy = y + i
            if 0 <= xx < LW and 0 <= yy < LH:
                s.set_at((xx, yy), col)
                if i % 5 == 0 and xx + 1 < LW:
                    s.set_at((xx + 1, yy), (61, 95, 67))

    def _ground_scatter(self, s, seed, y0=219, y1=231, density=12):
        rng = random.Random(seed)
        for i in range(density):
            x = rng.randrange(6, LW - 8)
            y = rng.randrange(y0, y1)
            tone = ((108, 143, 76), (138, 180, 93), (177, 157, 99), (96, 119, 72))[i % 4]
            if i % 3 == 0:
                pygame.draw.line(s, tone, (x, y), (x + 2, y - 1), 1)
            elif i % 3 == 1:
                pygame.draw.rect(s, tone, (x, y, 1, 1))
            else:
                pygame.draw.line(s, tone, (x, y), (x + 3, y), 1)

    def _small_glow(self, s, x, y, warm=False):
        if 0 <= x < LW and 0 <= y < LH:
            c = (236, 233, 170) if warm else (175, 223, 136)
            pygame.draw.rect(s, c, (x, y, 1, 1))
            if x + 1 < LW:
                pygame.draw.rect(s, (255, 246, 212) if warm else (216, 241, 185), (x + 1, y, 1, 1))

    def _forest_chunk(self, layer, index):
        # Base v3.143 + microdetalhes e profundidade adicional.
        s = super()._forest_chunk(layer, index)
        rng = random.Random(144000 + index * 149 + {'far': 0, 'mid': 1000, 'near': 2000}[layer])
        if layer == 'far':
            # Máscaras extras de copas distantes para aumentar profundidade.
            for i in range(3):
                x = 18 + i * 64 + rng.randint(-6, 6)
                y = 176 + (i % 2) * 8 + rng.randint(-3, 3)
                pygame.draw.ellipse(s, (86, 125, 111, 255), (x, y, 42 + rng.randint(-4, 6), 18 + rng.randint(-2, 3)))
                pygame.draw.ellipse(s, (120, 157, 143, 255), (x + 6, y + 3, 16, 6))
            for i in range(4):
                x = 20 + i * 48 + rng.randint(-4, 4)
                _line(s, (146, 180, 162), x, 205 + (i % 2), x + 5, 205 + (i % 2), 1)
        elif layer == 'mid':
            # Cipós curtos, pequenas plantas e luz filtrada nas copas.
            for i, x in enumerate((28, 63, 104, 146, 186, 210)):
                if i % 2 == 0:
                    self._vine_strand(s, x, 170 + (i % 3) * 5, 10 + (i % 2) * 4, 14410 + index * 11 + i, bright=(i % 4 == 0))
            for i, x in enumerate((18, 46, 73, 118, 154, 189, 207)):
                if i % 3 == 0:
                    self._wildflower(s, x, 216 + (i % 2), 14450 + index * 17 + i, i)
                else:
                    pygame.draw.line(s, (86, 133, 79), (x, 217), (x + 1, 211 - (i % 3)), 1)
                    pygame.draw.line(s, (128, 171, 97), (x + 1, 217), (x + 3, 213 - (i % 2)), 1)
            for i in range(8):
                x = 10 + i * 26 + rng.randint(-3, 3)
                y = 164 + (i % 3) * 7
                pygame.draw.line(s, (150, 187, 117), (x, y), (x + 5, y), 1)
        else:
            # Primeiro plano com mais riqueza de base, sem invadir a pista.
            for i, x in enumerate((12, 22, 34, 48, 177, 191, 206, 214)):
                if i % 2 == 0:
                    self._wildflower(s, x, 224 - (i % 3), 14500 + index * 23 + i, i)
                else:
                    pygame.draw.line(s, (78, 124, 77), (x, 224), (x + 1, 219 - (i % 2)), 1)
                    pygame.draw.line(s, (118, 162, 95), (x + 1, 224), (x + 3, 221 - (i % 3)), 1)
            self._ground_scatter(s, 14600 + index * 13, 219, 229, 18)
            for i, x in enumerate((26, 58, 170, 198)):
                pygame.draw.line(s, (87, 66, 46), (x, 220), (x + 8, 217 + (i % 2)), 1)
                pygame.draw.line(s, (66, 48, 35), (x + 1, 221), (x + 7, 219 + (i % 2)), 1)
        return s

    def _overlay_harmony(self, surf, frame, climate, night):
        if self.biome != 'floresta':
            return super()._overlay_harmony(surf, frame, climate, night)
        # overlay base da floresta vindo das versões anteriores
        super()._overlay_harmony(surf, frame, climate, night)
        # luz filtrada nas copas durante o dia
        if night < 0.18:
            for x in (58, 132, 214, 306, 388):
                y0 = 88 + ((frame // 10 + x) % 4)
                pygame.draw.line(surf, (212, 235, 170, 16), (x, y0), (x - 18, 208), 1)
                pygame.draw.line(surf, (175, 220, 136, 12), (x + 4, y0 + 8), (x - 10, 230), 1)
        # poeira/pólen florestal baixo e discreto
        if climate in ('limpo', 'vento_folhas', 'polen'):
            for i in range(7):
                x = int((i * 67 + frame * (0.4 if climate == 'limpo' else 0.8)) % (WIDTH + 10)) - 4
                y = 205 + (i * 9) % 48 + int(math.sin(frame * 0.03 + i) * 2)
                self._small_glow(surf, x, y, warm=(i % 3 == 0 and night < 0.18))
        # vaga-lumes extras ao anoitecer/noite
        if night > 0.22:
            for i in range(9):
                x = 18 + (i * 47 + int(frame * 0.55)) % 414
                y = 228 + (i * 19) % 122 + int(math.sin(frame * 0.04 + i) * 3)
                self._small_glow(surf, x, y, warm=(i % 4 == 0))
                if i % 4 == 0:
                    pygame.draw.circle(surf, (175, 223, 136, 22), (x, y), 3, 1)
