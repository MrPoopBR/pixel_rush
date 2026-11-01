"""Pixel Rush v3.137 — polimento final premium dos 4 biomas extras.

Base: v3.136.0. Preserva gameplay e toda a integração já aprovada; atua só
na arte dos quatro biomas extras com microdetalhes, iluminação aparente e
acabamento premium. Tudo é leve: detalhes de chunk são gerados uma única vez e
os overlays em runtime usam apenas primitivas pequenas.
"""
import math
import random
import pygame
from pixelrush_biomes2_v3136 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3133 import EXTRA_BIOMES
from pixelrush_biomes2_v3126 import LW, LH, _line, _rect


class ModularBiomeScene(Previous):
    def __init__(self, biome):
        super().__init__(biome)
        self._premium_seed = sum(ord(c) for c in biome) + 31370
        if biome in EXTRA_BIOMES:
            self._premium_polish_layers()
            self._map_cache.clear()

    # ---------------------- premium one-time polish ----------------------
    def _premium_polish_layers(self):
        for layer, chunks in self._layers.items():
            for idx, surf in enumerate(chunks):
                seed = self._premium_seed + idx * 97 + {'far': 0, 'mid': 1000, 'near': 2000}[layer]
                if self.biome == 'floresta':
                    self._polish_forest_chunk(surf, layer, seed)
                elif self.biome == 'vulcao':
                    self._polish_volcano_chunk(surf, layer, seed)
                elif self.biome == 'cidade_futurista':
                    self._polish_future_chunk(surf, layer, seed)
                elif self.biome == 'ilhas_celestes':
                    self._polish_sky_chunk(surf, layer, seed)

    def _sprinkle_pixels(self, surf, rect, colors, amount, seed, size=(1, 1)):
        rng = random.Random(seed)
        x0, y0, w, h = rect
        sw, sh = size
        for _ in range(amount):
            x = rng.randrange(x0, max(x0 + 1, x0 + w - sw + 1))
            y = rng.randrange(y0, max(y0 + 1, y0 + h - sh + 1))
            pygame.draw.rect(surf, colors[rng.randrange(0, len(colors))], (x, y, sw, sh))

    def _glow_orbs(self, surf, positions, palette):
        for x, y, r in positions:
            pygame.draw.circle(surf, palette[0], (x, y), r)
            if r > 1:
                pygame.draw.circle(surf, palette[1], (x, y), max(1, r - 1))

    def _polish_forest_chunk(self, surf, layer, seed):
        rng = random.Random(seed)
        if layer == 'far':
            for _ in range(12):
                x = rng.randrange(3, LW - 8)
                y = rng.randrange(145, 202)
                _line(surf, (146, 197, 118), x, y, x + 3, y + 1)
            self._sprinkle_pixels(surf, (0, 196, LW, 16), [(78, 114, 72), (112, 149, 95), (168, 200, 128)], 28, seed + 1, (2, 1))
        elif layer == 'mid':
            for _ in range(10):
                x = rng.randrange(6, LW - 12)
                y = rng.randrange(164, 210)
                pygame.draw.line(surf, (60, 107, 66), (x, y), (x + rng.randrange(-2, 3), y + 10), 1)
                if rng.random() < 0.6:
                    pygame.draw.line(surf, (178, 220, 136), (x + 1, y + 3), (x + 4, y + 4), 1)
            # florzinhas discretas
            for _ in range(7):
                x = rng.randrange(8, LW - 8)
                y = rng.randrange(203, 214)
                col = ((241, 153, 149), (248, 226, 142), (206, 228, 239))[rng.randrange(0, 3)]
                pygame.draw.rect(surf, col, (x, y, 2, 2))
        else:
            for _ in range(18):
                x = rng.randrange(2, LW - 4)
                y = rng.randrange(217, 231)
                pygame.draw.line(surf, (88, 142, 86), (x, y), (x + rng.randrange(-1, 2), y - rng.randrange(3, 8)), 1)
            for _ in range(9):
                x = rng.randrange(6, LW - 6)
                y = rng.randrange(223, 230)
                pygame.draw.rect(surf, (223, 102, 115) if _ % 2 else (240, 210, 119), (x, y, 2, 2))

    def _polish_volcano_chunk(self, surf, layer, seed):
        rng = random.Random(seed)
        if layer == 'far':
            self._sprinkle_pixels(surf, (0, 145, LW, 55), [(126, 93, 89), (94, 70, 72), (153, 114, 104)], 36, seed + 1, (2, 1))
            for _ in range(8):
                x = rng.randrange(12, LW - 18)
                y = rng.randrange(150, 193)
                pygame.draw.line(surf, (232, 112, 56), (x, y), (x + 2, y + 5), 1)
                pygame.draw.line(surf, (255, 189, 98), (x + 1, y), (x + 2, y + 3), 1)
        elif layer == 'mid':
            for _ in range(10):
                x = rng.randrange(4, LW - 8)
                y = rng.randrange(189, 214)
                pygame.draw.line(surf, (58, 50, 57), (x, y), (x + rng.randrange(-3, 4), y + rng.randrange(5, 10)), 1)
                if rng.random() < 0.4:
                    pygame.draw.line(surf, (246, 128, 67), (x + 1, y + 1), (x + 2, y + 4), 1)
            self._sprinkle_pixels(surf, (0, 194, LW, 20), [(176, 126, 91), (122, 92, 84), (82, 64, 68)], 26, seed + 2, (2, 1))
        else:
            for _ in range(13):
                x = rng.randrange(0, LW - 4)
                y = rng.randrange(216, 232)
                pygame.draw.line(surf, (61, 54, 59), (x, y), (x + rng.randrange(-2, 3), y + rng.randrange(3, 8)), 1)
            for _ in range(10):
                x = rng.randrange(8, LW - 8)
                y = rng.randrange(220, 230)
                pygame.draw.line(surf, (255, 179, 84), (x, y), (x + 3, y + 1), 1)

    def _polish_future_chunk(self, surf, layer, seed):
        rng = random.Random(seed)
        if layer == 'far':
            for _ in range(10):
                x = rng.randrange(10, LW - 16)
                y = rng.randrange(154, 194)
                pygame.draw.rect(surf, (93, 116, 160), (x, y, rng.randrange(8, 18), 2))
                if rng.random() < 0.7:
                    pygame.draw.rect(surf, (103, 241, 247), (x + 1, y + 1, 4, 1))
        elif layer == 'mid':
            for _ in range(16):
                x = rng.randrange(4, LW - 6)
                y = rng.randrange(178, 209)
                col = (102, 239, 247) if _ % 3 else (244, 106, 221)
                pygame.draw.rect(surf, col, (x, y, 2, 2))
            for _ in range(6):
                x = rng.randrange(0, LW - 25)
                y = rng.randrange(180, 205)
                pygame.draw.line(surf, (130, 214, 236), (x, y), (x + 12, y), 1)
        else:
            for _ in range(18):
                x = rng.randrange(2, LW - 4)
                y = rng.randrange(214, 229)
                col = (106, 241, 247) if _ % 2 else (247, 109, 223)
                pygame.draw.rect(surf, col, (x, y, 2, 1))
            for _ in range(6):
                x = rng.randrange(14, LW - 14)
                y = rng.randrange(199, 223)
                pygame.draw.line(surf, (88, 104, 140), (x, y), (x, y + 10), 1)

    def _polish_sky_chunk(self, surf, layer, seed):
        rng = random.Random(seed)
        if layer == 'far':
            for _ in range(8):
                x = rng.randrange(6, LW - 6)
                y = rng.randrange(105, 166)
                pygame.draw.rect(surf, (232, 246, 255), (x, y, 2, 1))
                if rng.random() < 0.5:
                    pygame.draw.rect(surf, (171, 228, 243), (x + 1, y + 1, 1, 1))
        elif layer == 'mid':
            for _ in range(10):
                x = rng.randrange(8, LW - 8)
                y = rng.randrange(144, 205)
                pygame.draw.line(surf, (175, 223, 140), (x, y), (x + 3, y), 1)
                if rng.random() < 0.4:
                    pygame.draw.line(surf, (142, 206, 226), (x + 1, y + 1), (x + 1, y + 5), 1)
        else:
            for _ in range(10):
                x = rng.randrange(8, LW - 8)
                y = rng.randrange(178, 223)
                pygame.draw.rect(surf, (229, 236, 246), (x, y, 2, 1))
                if rng.random() < 0.6:
                    pygame.draw.rect(surf, (164, 241, 250), (x + 2, y, 1, 1))
            self._sprinkle_pixels(surf, (0, 212, LW, 18), [(170, 189, 206), (210, 225, 239), (133, 150, 170)], 18, seed + 3, (2, 1))

    # ---------------------- runtime premium atmosphere --------------------
    def _overlay_forest_premium(self, surf, frame, climate, night):
        if night < 0.18:
            # feixes de luz suaves de cima
            for x in (38, 112, 196, 282, 358):
                y0 = 60 + ((frame // 9 + x) % 4)
                pygame.draw.line(surf, (194, 223, 152, 34), (x, y0), (x - 20, 220), 2)
                pygame.draw.line(surf, (230, 244, 181, 22), (x + 10, y0 + 8), (x + 2, 215), 1)
        else:
            # névoa noturna discreta
            for x in (22, 90, 178, 260, 340):
                pygame.draw.ellipse(surf, (152, 181, 144, 18), (x, 180 + (x % 9), 52, 12))
        if climate in ('polen', 'vento_folhas'):
            for i in range(6):
                x = int((i * 71 + frame * 1.3) % 470) - 8
                y = 70 + (i * 23 + frame // 2) % 150
                pygame.draw.rect(surf, (238, 236, 162, 100), (x, y, 2, 2))

    def _overlay_volcano_premium(self, surf, frame, climate, night):
        # brilhos de lava e calor aparente
        for rect in ((155, 428, 72, 4), (176, 380, 12, 24)):
            glow = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
            glow.fill((255, 138, 62, 26 if night < 0.15 else 44))
            surf.blit(glow, rect[:2])
        for i in range(4):
            x = 120 + i * 40 + int(math.sin((frame + i * 11) * 0.08) * 2)
            pygame.draw.line(surf, (255, 189, 95, 40), (x, 165), (x + 2, 193), 1)
        if climate in ('cinzas', 'chuva_meteoros'):
            for i in range(10):
                x = int((i * 41 - frame * 0.8) % 500) - 10
                y = 44 + (i * 19 + frame // 3) % 160
                pygame.draw.rect(surf, (147, 129, 126, 90), (x, y, 2, 2))

    def _overlay_future_premium(self, surf, frame, climate, night):
        # bloom fake econômico em letreiros/faixas
        for y in (220, 226):
            pygame.draw.line(surf, (94, 239, 246, 36 if night > 0.1 else 18), (0, y), (450, y), 1)
        for i, x in enumerate((66, 118, 192, 254, 328, 390)):
            col = (99, 240, 247, 48) if ((frame // 14 + i) % 2 == 0) else (243, 105, 222, 42)
            pygame.draw.line(surf, col, (x, 142), (x + 5, 228), 1)
        if climate in ('vento_neon', 'chuva_acida'):
            for i in range(8):
                x = int((i * 53 + frame * 2.6) % 470) - 10
                y = 85 + (i * 17 + frame) % 140
                pygame.draw.line(surf, (117, 229, 245, 48), (x, y), (x - 6, y + 14), 1)

    def _overlay_sky_premium(self, surf, frame, climate, night):
        # brilho etéreo e estrelas/partículas elegantes
        alpha = 20 if night < 0.2 else 34
        for x in (52, 138, 226, 312, 394):
            pygame.draw.ellipse(surf, (220, 239, 255, alpha), (x, 138 + (x % 11), 46, 12))
        for i in range(8):
            x = int((i * 57 + frame * 0.9) % 470) - 8
            y = 48 + (i * 27 + frame // 2) % 170
            pygame.draw.rect(surf, (241, 248, 255, 110 if night > 0.25 else 82), (x, y, 2, 2))
            if i % 3 == 0:
                pygame.draw.line(surf, (166, 241, 250, 85), (x - 1, y + 1), (x + 3, y + 1), 1)
        if climate in ('brisa_celeste', 'tempestade_vento'):
            for i in range(6):
                x = int((i * 73 - frame * 1.1) % 490) - 10
                y = 92 + (i * 24 + frame) % 120
                pygame.draw.line(surf, (218, 243, 251, 60), (x, y), (x + 10, y), 1)

    def render_scene(self, target, travel, frame, night, climate, phase,
                     foreground_only=False, map_kind='image'):
        result = super().render_scene(target, travel, frame, night, climate, phase,
                                      foreground_only=foreground_only, map_kind=map_kind)
        if foreground_only or map_kind != 'image' or self.biome not in EXTRA_BIOMES:
            return result
        if self.biome == 'floresta':
            self._overlay_forest_premium(target, frame, climate, night)
        elif self.biome == 'vulcao':
            self._overlay_volcano_premium(target, frame, climate, night)
        elif self.biome == 'cidade_futurista':
            self._overlay_future_premium(target, frame, climate, night)
        else:
            self._overlay_sky_premium(target, frame, climate, night)
        return result
