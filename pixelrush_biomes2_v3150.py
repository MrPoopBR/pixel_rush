"""v3.150 — combo A+B+C: Cidade Futurista premium + Vulcão premium + revisão fina em corrida.

Escopo:
- refino premium final da Cidade Futurista;
- refino premium final do Vulcão;
- pequenos ajustes de leitura/variedade percebidos em corrida simulada;
- preserva jogabilidade, ameaças e demais biomas fora do escopo.
"""
import math
import random
import pygame
from pixelrush_biomes2_v3149 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, LH, WIDTH


class ModularBiomeScene(Previous):
    FUTURE = {
        'hi': (116, 243, 248),
        'spark': (246, 108, 223),
        'alt': (191, 231, 236),
        'shade': (59, 74, 109),
        'deep': (43, 55, 87),
    }
    VOLCANO = {
        'lava': (255, 145, 72),
        'lava_hi': (255, 214, 114),
        'ash': (135, 112, 120),
        'rock': (76, 66, 74),
        'deep': (54, 45, 52),
        'smoke': (116, 100, 109),
        'violet': (188, 128, 255),
    }

    def __init__(self, biome):
        super().__init__(biome)
        if biome in ('cidade_futurista', 'vulcao'):
            self._premium_pass_layers()
            self._map_cache.clear()

    # --------------------------- helpers ---------------------------
    def _sprinkle(self, surf, rect, colors, amount, seed, size=(1, 1)):
        rng = random.Random(seed)
        x0, y0, w, h = rect
        sw, sh = size
        for _ in range(amount):
            x = rng.randrange(x0, max(x0 + 1, x0 + w - sw + 1))
            y = rng.randrange(y0, max(y0 + 1, y0 + h - sh + 1))
            pygame.draw.rect(surf, colors[rng.randrange(0, len(colors))], (x, y, sw, sh))

    def _window_strip(self, surf, x, y, w, h, c1, c2, seed):
        rng = random.Random(seed)
        for yy in range(y, y + h, 4):
            for xx in range(x, x + w, 4):
                pygame.draw.rect(surf, c1 if ((xx + yy) // 4 + seed) % 2 else c2, (xx, yy, 2, 2))
                if rng.random() < 0.12:
                    pygame.draw.rect(surf, c2, (xx + 2, yy, 1, 1))

    def _smoke_blob(self, surf, x, y, w, h, color, seed):
        rng = random.Random(seed)
        lumps = 4 + rng.randint(0, 2)
        for i in range(lumps):
            rx = x + rng.randint(-3, 3) + i * max(5, w // max(1, lumps))
            ry = y + rng.randint(-2, 2)
            rw = max(5, w // 3 + rng.randint(-2, 2))
            rh = max(4, h // 2 + rng.randint(-1, 2))
            pygame.draw.ellipse(surf, color, (rx, ry, rw, rh))

    def _clampx(self, x):
        return max(0, min(LW - 1, int(x)))

    # ---------------------- premium static pass ---------------------
    def _premium_pass_layers(self):
        for layer, chunks in self._layers.items():
            base_seed = {'far': 0, 'mid': 1000, 'near': 2000}[layer]
            for idx, surf in enumerate(chunks):
                seed = 31500 + idx * 131 + base_seed
                if self.biome == 'cidade_futurista':
                    self._future_premium_polish(surf, layer, idx, seed)
                elif self.biome == 'vulcao':
                    self._volcano_premium_polish(surf, layer, idx, seed)

    def _future_premium_polish(self, surf, layer, index, seed):
        pal = self.FUTURE
        rng = random.Random(seed)
        if layer == 'far':
            # torres extras finas e letreiros baixos para dar mais profundidade.
            for n, x in enumerate((16, 48, 91, 132, 175, 210)):
                if (index + n) % 2 == 0:
                    base_y = 213
                    top = 152 + ((n * 5 + index * 3) % 18)
                    w = 8 + (n % 3) * 2
                    pygame.draw.rect(surf, pal['deep'], (x, top, w, base_y - top))
                    pygame.draw.line(surf, pal['shade'], (x + 1, top + 2), (x + 1, base_y - 3), 1)
                    self._window_strip(surf, x + 3, top + 6, max(3, w - 4), max(8, base_y - top - 12), pal['hi'], pal['spark'], seed + n)
                    if n % 3 == 0:
                        pygame.draw.line(surf, pal['alt'], (x + w // 2, top - 6), (x + w // 2, top), 1)
                        pygame.draw.rect(surf, pal['spark'], (x + w // 2 - 1, top - 7, 2, 1))
            # passarelas / linhas de tráfego ao longe
            for x, y, w in ((22, 176, 32), (86, 168, 28), (150, 173, 34)):
                yy = y + ((index + x) % 4)
                pygame.draw.line(surf, pal['hi'], (x, yy), (x + w, yy), 1)
                pygame.draw.line(surf, pal['spark'], (x + 4, yy + 2), (x + w - 4, yy + 2), 1)
            self._sprinkle(surf, (0, 146, LW, 54), [pal['shade'], pal['hi'], pal['spark']], 18, seed + 90, (2, 1))
        elif layer == 'mid':
            # skybridges / painéis neon / variação de fachadas
            bridges = [(26, 188, 42), (108, 184, 35), (172, 191, 36)] if index % 2 == 0 else [(44, 186, 36), (130, 189, 46)]
            for x, y, w in bridges:
                pygame.draw.rect(surf, (96, 110, 150), (x, y, w, 4))
                pygame.draw.line(surf, pal['hi'], (x + 2, y + 1), (x + w - 3, y + 1), 1)
                pygame.draw.line(surf, pal['spark'], (x + 5, y + 3), (x + w - 6, y + 3), 1)
                if x > 10:
                    pygame.draw.line(surf, pal['shade'], (x + 4, y + 4), (x + 4, y + 12), 1)
                pygame.draw.line(surf, pal['shade'], (x + w - 4, y + 4), (x + w - 4, y + 13), 1)
            for n, x in enumerate((20, 58, 95, 138, 182)):
                y = 176 + (n % 3) * 7 + (index % 2)
                w = 8 + (n % 2) * 3
                h = 12 + (n % 3) * 4
                pygame.draw.rect(surf, pal['shade'], (x, y, w, h))
                pygame.draw.line(surf, pal['alt'], (x, y), (x + w - 1, y), 1)
                self._window_strip(surf, x + 1, y + 2, w - 2, h - 3, pal['hi'], pal['spark'], seed + 150 + n)
            # pequenos veículos voadores estilizados
            for n, x in enumerate((18, 72, 146, 198)):
                y = 171 + ((index + n) % 3) * 8
                pygame.draw.line(surf, pal['alt'], (x, y), (x + 10, y), 1)
                pygame.draw.line(surf, pal['hi'], (x + 2, y + 1), (x + 8, y + 1), 1)
                pygame.draw.rect(surf, pal['spark'], (x + 8, y, 2, 1))
        else:
            # frente: luzes de piso, painéis baixos e reflexos discretos na estrada alta
            for x in range(8, LW - 10, 22):
                c = pal['hi'] if (x // 22 + index) % 2 == 0 else pal['spark']
                pygame.draw.line(surf, c, (x, 225), (x + 5, 225), 1)
            for x in (24, 92, 160, 206):
                y = 214 + ((x + index) % 4)
                pygame.draw.rect(surf, pal['shade'], (x, y, 10, 5))
                pygame.draw.line(surf, pal['spark'], (x + 1, y + 1), (x + 8, y + 1), 1)
                pygame.draw.line(surf, pal['hi'], (x + 2, y + 3), (x + 7, y + 3), 1)
            self._sprinkle(surf, (0, 214, LW, 16), [pal['hi'], pal['spark'], pal['alt']], 18, seed + 240, (1, 1))

    def _volcano_premium_polish(self, surf, layer, index, seed):
        pal = self.VOLCANO
        rng = random.Random(seed)
        if layer == 'far':
            # fumaça adicional e fissuras sutis na cordilheira.
            for n, x in enumerate((18, 56, 102, 148, 194)):
                y = 168 + ((index + n) % 8)
                self._smoke_blob(surf, x - 6, y, 18, 10, (*pal['smoke'],), seed + n)
                pygame.draw.line(surf, pal['ash'], (x, y + 10), (x + 2, y + 16), 1)
            for x, y in ((34, 189), (92, 181), (144, 186), (203, 183)):
                yy = y + (index % 3)
                pygame.draw.line(surf, pal['lava'], (x, yy), (x + 5, yy + 8), 1)
                pygame.draw.line(surf, pal['lava_hi'], (x + 1, yy + 2), (x + 3, yy + 6), 1)
            self._sprinkle(surf, (0, 154, LW, 56), [pal['ash'], pal['lava'], pal['deep']], 16, seed + 90, (1, 1))
        elif layer == 'mid':
            # colunas com rachaduras, vapor e poças extras de lava
            for x in (26, 68, 109, 151, 197):
                base_y = 214
                top = 177 + ((x + index) % 11)
                pygame.draw.line(surf, pal['deep'], (x, top), (x, base_y), 2)
                pygame.draw.line(surf, pal['rock'], (x + 2, top + 3), (x + 2, base_y - 1), 1)
                pygame.draw.line(surf, pal['lava'], (x + 1, top + 6), (x + 1, min(base_y - 6, top + 22)), 1)
                if (x // 10 + index) % 2 == 0:
                    pygame.draw.line(surf, pal['lava_hi'], (x + 1, top + 10), (x + 1, min(base_y - 11, top + 18)), 1)
            for x, y, w in ((16, 211, 24), (118, 212, 20), (176, 210, 25)):
                if (x + index) % 2 == 0:
                    pygame.draw.ellipse(surf, pal['lava'], (x, y, w, 7))
                    pygame.draw.ellipse(surf, pal['lava_hi'], (x + 5, y + 2, max(8, w - 10), 2))
            for n, x in enumerate((42, 87, 162, 205)):
                y = 186 + (n % 2) * 7
                pygame.draw.line(surf, pal['smoke'], (x, y), (x + 2, y - 9), 1)
                pygame.draw.rect(surf, pal['ash'], (x + 1, y - 10, 2, 2))
        else:
            # frente: brasas, cacos de rocha e reflexos quentes baixos
            for x in range(12, LW - 10, 19):
                c = pal['lava'] if (x // 19 + index) % 2 == 0 else pal['lava_hi']
                pygame.draw.line(surf, c, (x, 226), (x + 3, 226), 1)
            for x in (18, 46, 84, 122, 166, 204):
                y = 220 + ((x + index) % 5)
                pygame.draw.polygon(surf, pal['rock'], [(x, y), (x + 3, y - 2), (x + 6, y + 1), (x + 2, y + 2)])
                if x % 2 == 0:
                    pygame.draw.line(surf, pal['lava_hi'], (x + 1, y + 1), (x + 2, y + 1), 1)
            self._sprinkle(surf, (0, 216, LW, 14), [pal['lava'], pal['lava_hi'], pal['violet']], 16, seed + 240, (1, 1))

    # -------------------------- dynamic overlays --------------------
    def _overlay_harmony(self, surf, frame, climate, night):
        super()._overlay_harmony(surf, frame, climate, night)
        if self.biome == 'cidade_futurista':
            self._overlay_future_runreview(surf, frame, climate, night)
        elif self.biome == 'vulcao':
            self._overlay_volcano_runreview(surf, frame, climate, night)
        elif self.biome == 'floresta':
            self._overlay_forest_runreview(surf, frame, climate, night)

    def _overlay_future_runreview(self, surf, frame, climate, night):
        pal = self.FUTURE
        # linhas de tráfego contínuas e escaneamentos holográficos discretos.
        alpha = 18 if night < 0.25 else 26
        for y in (118, 154, 194):
            yy = y + int(math.sin(frame * 0.03 + y * 0.07) * 2)
            pygame.draw.line(surf, (pal['hi'][0], pal['hi'][1], pal['hi'][2], alpha), (0, yy), (450, yy), 1)
        for i in range(5):
            x = int((i * 97 + frame * 1.2) % 520) - 24
            y = 160 + (i * 12) % 52
            pygame.draw.line(surf, (pal['alt'][0], pal['alt'][1], pal['alt'][2], 24), (x, y), (x + 18, y), 1)
            pygame.draw.rect(surf, (pal['spark'][0], pal['spark'][1], pal['spark'][2], 38), (x + 14, y - 1, 2, 2))
        if night > 0.25:
            for i in range(6):
                x = int((i * 71 + frame * 0.7) % 470) - 8
                y = 72 + (i * 23 + frame // 2) % 110
                pygame.draw.line(surf, (pal['spark'][0], pal['spark'][1], pal['spark'][2], 22), (x, y), (x + 8, y), 1)
        if climate == 'vento_neon':
            for i in range(10):
                x = int((i * 43 + frame * 2.5) % (WIDTH + 40)) - 20
                y = 96 + (i * 26 + frame // 2) % 165
                pygame.draw.line(surf, (70, 245, 255, 34), (x, y), (x + 10, y + 2), 1)
                if i % 2 == 0:
                    pygame.draw.line(surf, (247, 108, 223, 26), (x + 4, y - 1), (x + 12, y + 1), 1)
        elif climate == 'chuva_acida':
            for i in range(12):
                x = int((i * 36 - frame * 2.8) % (WIDTH + 30)) - 15
                y = 92 + (i * 33 + frame * 3) % 290
                pygame.draw.line(surf, (125, 255, 112, 34), (x, y), (x - 3, y + 11), 1)
                if i % 3 == 0:
                    pygame.draw.line(surf, (108, 241, 247, 24), (x + 1, y + 3), (x - 1, y + 13), 1)

    def _overlay_volcano_runreview(self, surf, frame, climate, night):
        # mais vida no ar do vulcão: calor, brasas e fumaça, sem pesar.
        glow_alpha = 20 if night < 0.2 else 30
        for y in (428, 430):
            pygame.draw.line(surf, (255, 142, 68, glow_alpha), (146, y), (232, y), 1)
        for i in range(8):
            x = int((i * 57 - frame * 0.9) % 500) - 10
            y = 132 + (i * 29 + frame // 2) % 210
            pygame.draw.rect(surf, (255, 160, 76, 34), (x, y, 2, 2))
            if i % 2 == 0:
                pygame.draw.rect(surf, (255, 216, 132, 24), (x + 1, y - 1, 1, 1))
        # colunas de calor finas ao fundo
        for x in (68, 142, 221, 303, 386):
            yy = 160 + ((frame // 6 + x) % 9)
            pygame.draw.line(surf, (255, 183, 120, 16), (x, yy), (x + 4, 230), 1)
        if climate in ('cinzas', 'chuva_meteoros'):
            for i in range(10):
                x = int((i * 43 - frame * (2.6 if climate == 'chuva_meteoros' else 1.4)) % 490) - 15
                y = 84 + (i * 31 + frame * (3 if climate == 'chuva_meteoros' else 1)) % 250
                if climate == 'chuva_meteoros':
                    pygame.draw.line(surf, (255, 158, 74, 40), (x, y), (x - 6, y + 10), 2)
                    pygame.draw.line(surf, (255, 222, 124, 28), (x, y + 1), (x - 3, y + 5), 1)
                else:
                    pygame.draw.rect(surf, (150, 128, 134, 24), (x, y, 2, 2))

    def _overlay_forest_runreview(self, surf, frame, climate, night):
        # revisão fina: só um acabamento de profundidade e vaga-lumes noturnos leves.
        if night > 0.28:
            for i in range(6):
                x = int((i * 69 + frame * 0.8) % 470) - 8
                y = 110 + (i * 25 + frame // 3) % 140
                pygame.draw.rect(surf, (210, 236, 164, 36), (x, y, 2, 2))
                if i % 2 == 0:
                    pygame.draw.rect(surf, (255, 220, 120, 24), (x + 1, y, 1, 1))
