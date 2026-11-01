"""Pixel Rush v3.138 — combo premium: Floresta + harmonização + cenários extras.

Base: v3.137.0. Escopo restrito ao refinamento visual dos 4 biomas extras.
Preserva jogabilidade, física e integrações anteriores.
"""
import math
import random
import pygame
from pixelrush_biomes2_v3137 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3133 import EXTRA_BIOMES
from pixelrush_biomes2_v3126 import LW, LH, _line, _rect

SKIN_ACCENTS = {
    'floresta': {
        'hi': (168, 225, 138),      # verde / dinossauro
        'spark': (255, 211, 120),   # dourado suave
        'alt': (236, 172, 186),     # rosa suave
        'shade': (52, 92, 68),
    },
    'vulcao': {
        'hi': (255, 151, 78),       # chama
        'spark': (199, 128, 255),   # roxo/cósmico
        'alt': (255, 214, 121),
        'shade': (84, 58, 66),
    },
    'cidade_futurista': {
        'hi': (113, 241, 247),      # robô/neon
        'spark': (247, 108, 223),   # roxo neon
        'alt': (187, 228, 233),     # platina
        'shade': (54, 69, 102),
    },
    'ilhas_celestes': {
        'hi': (184, 230, 236),      # platina
        'spark': (188, 128, 255),   # cósmica
        'alt': (255, 219, 118),     # dourado suave
        'shade': (118, 134, 157),
    },
}


class ModularBiomeScene(Previous):
    def __init__(self, biome):
        super().__init__(biome)
        self._combo_seed = sum(ord(c) for c in biome) + 31380
        if biome in EXTRA_BIOMES:
            self._combo_polish_layers()
            self._map_cache.clear()

    def _combo_polish_layers(self):
        pal = SKIN_ACCENTS[self.biome]
        for layer, chunks in self._layers.items():
            for idx, surf in enumerate(chunks):
                seed = self._combo_seed + idx * 101 + {'far': 0, 'mid': 1000, 'near': 2000}[layer]
                self._harmonize_palette(surf, layer, seed, pal)
                if self.biome == 'floresta':
                    self._forest_master_polish(surf, layer, seed, pal)
                elif self.biome == 'vulcao':
                    self._volcano_combo_polish(surf, layer, seed, pal)
                elif self.biome == 'cidade_futurista':
                    self._future_combo_polish(surf, layer, seed, pal)
                else:
                    self._sky_combo_polish(surf, layer, seed, pal)

    def _sprinkle(self, surf, rect, colors, amount, seed, size=(1, 1)):
        rng = random.Random(seed)
        x0, y0, w, h = rect
        sw, sh = size
        for _ in range(amount):
            x = rng.randrange(x0, max(x0 + 1, x0 + w - sw + 1))
            y = rng.randrange(y0, max(y0 + 1, y0 + h - sh + 1))
            pygame.draw.rect(surf, colors[rng.randrange(0, len(colors))], (x, y, sw, sh))

    def _harmonize_palette(self, surf, layer, seed, pal):
        # Costura a linguagem dos cenários extras com as skins aprovadas.
        rng = random.Random(seed)
        if layer == 'far':
            self._sprinkle(surf, (0, 136, LW, 72), [pal['shade'], pal['hi']], 10, seed + 1, (2, 1))
        elif layer == 'mid':
            self._sprinkle(surf, (0, 172, LW, 48), [pal['hi'], pal['spark'], pal['alt']], 14, seed + 2, (2, 1))
        else:
            self._sprinkle(surf, (0, 208, LW, 22), [pal['spark'], pal['alt'], pal['hi']], 12, seed + 3, (2, 1))
            # sombra de contato discreta para manter volume e elegância
            for x in range(0, LW, 18):
                if rng.random() < 0.55:
                    pygame.draw.line(surf, pal['shade'], (x, 231), (x + 10, 231), 1)

    def _forest_master_polish(self, surf, layer, seed, pal):
        rng = random.Random(seed)
        if layer == 'far':
            # segunda massa de copa e miolos claros para profundidade.
            for _ in range(12):
                x = rng.randrange(4, LW - 18)
                y = rng.randrange(148, 196)
                pygame.draw.ellipse(surf, (54, 97, 71), (x, y, rng.randrange(12, 22), rng.randrange(8, 15)))
                if rng.random() < 0.7:
                    pygame.draw.ellipse(surf, pal['hi'], (x + 3, y + 2, rng.randrange(5, 10), rng.randrange(3, 6)))
        elif layer == 'mid':
            # samambaias maiores, pequenas pedras, cipós e cogumelos discretos.
            for _ in range(7):
                x = rng.randrange(6, LW - 12)
                y = rng.randrange(192, 208)
                pygame.draw.line(surf, (68, 110, 72), (x, y), (x, y - rng.randrange(8, 14)), 1)
                for k in range(3):
                    pygame.draw.line(surf, pal['hi'], (x, y - 2 - k * 3), (x + 3 + k, y - 4 - k * 3), 1)
                    pygame.draw.line(surf, (103, 155, 98), (x, y - 2 - k * 3), (x - 3 - k, y - 4 - k * 3), 1)
            for _ in range(5):
                x = rng.randrange(8, LW - 8)
                y = rng.randrange(199, 213)
                pygame.draw.ellipse(surf, (113, 121, 105), (x, y, 6, 4))
                pygame.draw.line(surf, (158, 166, 146), (x + 2, y + 1), (x + 3, y + 1), 1)
            for _ in range(4):
                x = rng.randrange(16, LW - 16)
                y = rng.randrange(166, 198)
                pygame.draw.line(surf, (82, 103, 75), (x, y), (x + rng.randrange(-2, 3), y + 17), 1)
            for _ in range(6):
                x = rng.randrange(10, LW - 10)
                y = rng.randrange(204, 214)
                top = y - rng.randrange(3, 5)
                pygame.draw.line(surf, (216, 201, 173), (x, y), (x, top), 1)
                pygame.draw.ellipse(surf, pal['alt'], (x - 2, top - 2, 5, 3))
        else:
            # Frente mais rica, mas ainda limpa para não competir com ameaças.
            for _ in range(22):
                x = rng.randrange(4, LW - 6)
                y = rng.randrange(218, 231)
                pygame.draw.line(surf, (72, 126, 79), (x, y), (x + rng.randrange(-1, 2), y - rng.randrange(4, 9)), 1)
                if rng.random() < 0.25:
                    pygame.draw.line(surf, pal['spark'], (x, y - 1), (x + 1, y - 1), 1)
            for _ in range(7):
                x = rng.randrange(10, LW - 10)
                y = rng.randrange(223, 231)
                pygame.draw.rect(surf, pal['alt'] if _ % 2 else pal['spark'], (x, y, 2, 2))

    def _volcano_combo_polish(self, surf, layer, seed, pal):
        rng = random.Random(seed)
        if layer == 'far':
            self._sprinkle(surf, (0, 145, LW, 52), [pal['shade'], pal['spark'], pal['hi']], 14, seed + 10, (2, 1))
        elif layer == 'mid':
            for _ in range(7):
                x = rng.randrange(6, LW - 18)
                y = rng.randrange(175, 205)
                pygame.draw.line(surf, pal['hi'], (x, y), (x + 2, y + 6), 1)
                pygame.draw.line(surf, pal['spark'], (x + 1, y), (x + 1, y + 3), 1)
        else:
            for _ in range(8):
                x = rng.randrange(8, LW - 8)
                y = rng.randrange(220, 231)
                pygame.draw.line(surf, pal['hi'], (x, y), (x + 3, y + 1), 1)

    def _future_combo_polish(self, surf, layer, seed, pal):
        rng = random.Random(seed)
        if layer == 'far':
            for _ in range(7):
                x = rng.randrange(8, LW - 18)
                y = rng.randrange(150, 193)
                pygame.draw.rect(surf, pal['alt'], (x, y, rng.randrange(8, 14), 1))
        elif layer == 'mid':
            for _ in range(10):
                x = rng.randrange(10, LW - 10)
                y = rng.randrange(180, 208)
                pygame.draw.line(surf, pal['hi'], (x, y), (x + 6, y), 1)
                if rng.random() < 0.5:
                    pygame.draw.line(surf, pal['spark'], (x + 2, y + 2), (x + 4, y + 2), 1)
        else:
            for _ in range(13):
                x = rng.randrange(10, LW - 10)
                y = rng.randrange(214, 229)
                pygame.draw.rect(surf, pal['spark'] if _ % 2 else pal['hi'], (x, y, 2, 1))

    def _sky_combo_polish(self, surf, layer, seed, pal):
        rng = random.Random(seed)
        if layer == 'far':
            self._sprinkle(surf, (0, 104, LW, 62), [pal['alt'], pal['hi']], 10, seed + 20, (2, 1))
        elif layer == 'mid':
            for _ in range(8):
                x = rng.randrange(10, LW - 10)
                y = rng.randrange(143, 201)
                pygame.draw.line(surf, pal['hi'], (x, y), (x + 3, y), 1)
                if rng.random() < 0.4:
                    pygame.draw.line(surf, pal['spark'], (x + 1, y + 1), (x + 2, y + 1), 1)
        else:
            for _ in range(11):
                x = rng.randrange(8, LW - 8)
                y = rng.randrange(179, 222)
                pygame.draw.rect(surf, pal['alt'] if _ % 2 else pal['hi'], (x, y, 2, 1))

    def _overlay_forest_combo(self, surf, frame, climate, night):
        # mais vida e profundidade sem chamar mais atenção que a pista.
        if night < 0.2:
            for x in (60, 150, 242, 334, 412):
                y0 = 68 + ((frame // 8 + x) % 5)
                pygame.draw.line(surf, (203, 231, 168, 22), (x, y0), (x - 24, 214), 2)
        else:
            for i in range(8):
                x = int((i * 63 + frame * 0.9) % 470) - 8
                y = 82 + (i * 27 + frame // 2) % 145
                pygame.draw.rect(surf, (170, 231, 140, 86), (x, y, 2, 2))
                if i % 2 == 0:
                    pygame.draw.rect(surf, (255, 216, 122, 50), (x + 1, y, 1, 1))
        if climate in ('polen', 'vento_folhas'):
            for i in range(8):
                x = int((i * 59 + frame * 1.5) % 470) - 8
                y = 78 + (i * 19 + frame // 2) % 150
                pygame.draw.rect(surf, (244, 231, 150, 90), (x, y, 2, 2))

    def _overlay_harmony(self, surf, frame, climate, night):
        if self.biome == 'floresta':
            self._overlay_forest_combo(surf, frame, climate, night)
        elif self.biome == 'vulcao':
            # brilho extra com leve acento roxo/cósmico.
            for y in (427, 429):
                pygame.draw.line(surf, (255, 142, 68, 30 if night < .15 else 46), (150, y), (230, y), 1)
            pygame.draw.line(surf, (194, 121, 255, 18), (174, 380), (184, 404), 1)
        elif self.biome == 'cidade_futurista':
            for y in (220, 226):
                pygame.draw.line(surf, (108, 241, 247, 18 if night < .15 else 28), (0, y), (450, y), 1)
            if night > 0.25:
                for x in (70, 126, 192, 254, 326, 388):
                    pygame.draw.line(surf, (247, 108, 223, 20), (x, 150), (x + 4, 225), 1)
        else:
            for i in range(7):
                x = int((i * 67 + frame * 0.7) % 470) - 8
                y = 56 + (i * 21 + frame // 2) % 162
                pygame.draw.rect(surf, (240, 248, 255, 80 if night > 0.25 else 58), (x, y, 2, 2))
                if i % 3 == 0:
                    pygame.draw.line(surf, (188, 128, 255, 35), (x - 1, y + 1), (x + 3, y + 1), 1)

    def render_scene(self, target, travel, frame, night, climate, phase,
                     foreground_only=False, map_kind='image'):
        result = super().render_scene(target, travel, frame, night, climate, phase,
                                      foreground_only=foreground_only, map_kind=map_kind)
        if foreground_only or map_kind != 'image' or self.biome not in EXTRA_BIOMES:
            return result
        self._overlay_harmony(target, frame, climate, night)
        return result
