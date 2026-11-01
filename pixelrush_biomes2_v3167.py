"""Pixel Rush v3.167.0 — revisão fina premium da Cidade Futurista.

Escopo desta versão:
- refinar exclusivamente o bioma cidade_futurista;
- aumentar sensação de megacidade coesa e limpa;
- melhorar chão estrutural, encaixes, profundidade e tráfego aéreo;
- manter os demais biomas exatamente como estavam na v3.166.0.
"""
from __future__ import annotations
import math
import random
import pygame
from pixelrush_biomes2_v3166 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, LH, WIDTH


class ModularBiomeScene(Previous):
    def __init__(self, biome):
        super().__init__(biome)
        if biome == 'cidade_futurista':
            self._build_future_fx_cache()
            self._future_ultra_pass()
            if hasattr(self, '_map_cache'):
                self._map_cache.clear()
            if hasattr(self, '_composites'):
                self._composites.clear()

    def _build_future_fx_cache(self):
        self._future_cars = []
        base_colors = [
            ((102, 241, 251), (247, 125, 233), (201, 244, 255)),
            ((176, 244, 255), (128, 226, 255), (244, 150, 242)),
            ((132, 228, 255), (255, 170, 242), (233, 251, 255)),
        ]
        for i, (c1, c2, c3) in enumerate(base_colors):
            for phase in range(2):
                w = 28 + i * 4
                h = 11 + i
                s = pygame.Surface((w, h), pygame.SRCALPHA)
                body = [(3, h // 2 + 1), (7, 2), (w - 12, 2), (w - 6, h // 2), (w - 10, h - 2), (7, h - 2)]
                pygame.draw.polygon(s, (39, 58, 96), body)
                pygame.draw.line(s, c1, (7, 3), (w - 12, 3), 1)
                pygame.draw.line(s, c2, (8, h - 3), (w - 10, h - 3), 1)
                pygame.draw.line(s, c3, (10, h // 2), (w - 14, h // 2), 1)
                pygame.draw.rect(s, c1, (5, h // 2, 3, 1))
                pygame.draw.rect(s, c2, (w - 8, h // 2, 3, 1))
                pygame.draw.line(s, (*c1, 120), (1, h // 2 + phase), (4, h // 2 + phase), 1)
                pygame.draw.line(s, (*c2, 120), (w - 4, h // 2 - phase), (w - 1, h // 2 - phase), 1)
                if phase == 1:
                    pygame.draw.line(s, (*c1, 85), (w // 2 - 2, h - 1), (w // 2 + 3, h - 1), 1)
                self._future_cars.append(s)

    def _future_ultra_pass(self):
        for layer, chunks in self._layers.items():
            for idx, surf in enumerate(chunks):
                self._future_seal_edges(surf, layer)
                if layer == 'far':
                    self._future_far_polish(surf, idx)
                elif layer == 'mid':
                    self._future_mid_polish(surf, idx)
                else:
                    self._future_near_polish(surf, idx)

    def _future_seal_edges(self, surf, layer):
        ymap = {'far': (209, 211, 213), 'mid': (211, 213, 215), 'near': (178, 193, 200, 218, 223)}
        shade = (47, 65, 103)
        hi = self.FUTURE['hi']
        for y in ymap[layer]:
            pygame.draw.line(surf, shade, (0, y), (LW - 1, y), 1)
        if layer != 'far':
            pygame.draw.line(surf, (*hi[:3], 90), (0, ymap[layer][0]), (LW - 1, ymap[layer][0]), 1)
        for y in ymap[layer][:2]:
            surf.set_at((0, y), shade)
            surf.set_at((LW - 1, y), shade)

    def _future_far_polish(self, surf, idx):
        district = idx % 6
        haze = pygame.Surface((LW, 80), pygame.SRCALPHA)
        for y in range(80):
            a = 8 + y // 7
            pygame.draw.line(haze, (95, 130, 177, a), (0, y), (LW - 1, y), 1)
        surf.blit(haze, (0, 128))
        # base skyline / grand scale
        pygame.draw.rect(surf, (40, 58, 94), (0, 205, LW, 7))
        pygame.draw.line(surf, (90, 129, 173), (0, 205), (LW - 1, 205), 1)
        if district == 0:
            self._future_super_spire(surf, 36, 196, 20)
            self._future_super_spire(surf, 172, 196, 28)
        elif district == 1:
            self._future_residential_cluster(surf, 30, 189, 42)
            self._future_residential_cluster(surf, 150, 191, 36)
        elif district == 2:
            self._future_transit_ring(surf, 42, 173, 60)
            self._future_transit_ring(surf, 150, 176, 52)
        elif district == 3:
            self._future_hologram_tower(surf, 30, 194, 36)
            self._future_hologram_tower(surf, 152, 188, 46)
        elif district == 4:
            self._future_industrial_stack(surf, 42, 200, 30)
            self._future_industrial_stack(surf, 162, 198, 26)
        else:
            self._future_garden_dome(surf, 36, 196, 28)
            self._future_garden_dome(surf, 152, 194, 32)
        for x in range(16, LW, 46):
            pygame.draw.line(surf, (113, 171, 214, 22), (x, 142), (x + 3, 188), 1)

    def _future_mid_polish(self, surf, idx):
        district = (idx + 1) % 6
        hi = self.FUTURE['hi']; spark = self.FUTURE['spark']; alt = self.FUTURE['alt']
        # extra sky bridge segments, always anchored
        if district in (0, 2, 3):
            for x, y, w in ((18, 182, 48), (136, 186, 42)):
                self._future_connector(surf, x + (idx % 2) * 3, y + (idx % 3), w, hi, spark)
        # controlled signage small and embedded
        signs = ((20, 168, 24, 7), (176, 171, 22, 7)) if idx % 2 == 0 else ((30, 164, 18, 6), (164, 169, 20, 6))
        colors = [(hi, alt), (spark, hi)]
        for j, (x, y, w, h) in enumerate(signs):
            bg = pygame.Rect(x, y, w, h)
            pygame.draw.rect(surf, (33, 45, 74), bg, border_radius=2)
            pygame.draw.rect(surf, colors[j][0], bg, 1, border_radius=2)
            for xx in range(x + 3, x + w - 3, 4):
                pygame.draw.line(surf, colors[j][1], (xx, y + 2), (min(x + w - 4, xx + 1), y + 2), 1)
        # facade edge lighting to improve depth
        for x in range(12, LW, 34):
            pygame.draw.line(surf, (73, 102, 146), (x, 125), (x, 205), 1)
        # lower structural band
        pygame.draw.rect(surf, (45, 64, 101), (0, 206, LW, 10))
        pygame.draw.line(surf, (117, 180, 216), (0, 206), (LW - 1, 206), 1)

    def _future_near_polish(self, surf, idx):
        hi = self.FUTURE['hi']; spark = self.FUTURE['spark']; alt = self.FUTURE['alt']
        # clearer premium platform and anti-pollution cleanup on center lane
        pygame.draw.rect(surf, (58, 81, 124), (0, 176, LW, 4))
        pygame.draw.rect(surf, (76, 103, 149), (0, 191, LW, 9))
        pygame.draw.line(surf, alt, (0, 193), (LW - 1, 193), 1)
        for x in range(0, LW, 24):
            pygame.draw.line(surf, (59, 83, 125), (x, 193), (x, 201), 1)
        # supports / engineering improved
        for x in (18, 50, 84, 140, 176, 206):
            px = x + (idx % 3 - 1)
            pygame.draw.rect(surf, (45, 62, 97), (px, 201, 6, 19))
            pygame.draw.line(surf, (90, 125, 168), (px + 2, 201), (px + 2, 219), 1)
        # neon lane shoulders, keep center readable
        for x in range(6, 44, 9):
            pygame.draw.line(surf, hi, (x, 194), (x + 4, 194), 1)
        for x in range(LW - 44, LW - 6, 9):
            pygame.draw.line(surf, spark, (x, 194), (x + 4, 194), 1)
        # subtle veil in center reduces floating clutter feel without removing art
        veil = pygame.Surface((LW - 84, 25), pygame.SRCALPHA)
        pygame.draw.rect(veil, (16, 21, 35, 26), (0, 0, veil.get_width(), veil.get_height()))
        surf.blit(veil, (42, 198))
        # side kiosks and pods only at margins
        self._future_side_pod(surf, 4, 170, 28, idx)
        self._future_side_pod(surf, LW - 34, 170, 28, idx + 1)
        # canal / energy reflection strip
        pygame.draw.rect(surf, (25, 37, 72), (0, 223, LW, 10))
        for x in range(4, LW, 18):
            pygame.draw.line(surf, (89, 236, 250), (x, 227), (x + 6, 227), 1)
            if (x // 18 + idx) % 2 == 0:
                pygame.draw.line(surf, (242, 122, 233), (x + 3, 231), (x + 7, 231), 1)
        # bottom structure
        pygame.draw.rect(surf, (34, 48, 82), (0, 233, LW, 17))
        for x in range(10, LW, 32):
            pygame.draw.line(surf, (61, 82, 117), (x, 233), (x + 6, 249), 1)
            pygame.draw.line(surf, (61, 82, 117), (x + 16, 233), (x + 10, 249), 1)

    # ---------- small future themed drawings ----------
    def _future_super_spire(self, surf, x, base, h):
        pygame.draw.polygon(surf, (53, 72, 111), [(x, base), (x + 7, base - h), (x + 14, base)])
        pygame.draw.line(surf, self.FUTURE['hi'], (x + 7, base - h + 3), (x + 7, base - 3), 1)
        pygame.draw.line(surf, self.FUTURE['spark'], (x + 4, base - 5), (x + 10, base - 5), 1)

    def _future_residential_cluster(self, surf, x, base, w):
        pygame.draw.rect(surf, (60, 79, 119), (x, base - 16, w, 16))
        pygame.draw.rect(surf, (79, 106, 150), (x + 8, base - 22, w - 16, 6))
        for px in range(x + 4, x + w - 4, 6):
            pygame.draw.rect(surf, self.FUTURE['alt'], (px, base - 11, 2, 2))

    def _future_transit_ring(self, surf, x, y, w):
        pygame.draw.arc(surf, self.FUTURE['hi'], (x, y, w, 14), math.radians(180), math.radians(360), 2)
        pygame.draw.line(surf, (72, 100, 148), (x + 6, y + 7), (x + w - 6, y + 7), 1)

    def _future_hologram_tower(self, surf, x, base, h):
        pygame.draw.rect(surf, (47, 66, 104), (x + 8, base - h, 18, h))
        pygame.draw.line(surf, self.FUTURE['spark'], (x + 17, base - h + 4), (x + 17, base - 6), 1)
        pygame.draw.arc(surf, self.FUTURE['hi'], (x, base - h - 6, 34, 12), math.radians(180), math.radians(360), 1)
        pygame.draw.line(surf, self.FUTURE['hi'], (x + 2, base - h - 1), (x + 30, base - h - 1), 1)

    def _future_industrial_stack(self, surf, x, base, h):
        pygame.draw.rect(surf, (53, 66, 95), (x, base - h, 10, h))
        pygame.draw.line(surf, self.FUTURE['alt'], (x + 4, base - h + 2), (x + 4, base - 4), 1)
        pygame.draw.line(surf, self.FUTURE['spark'], (x - 2, base - h + 3), (x + 12, base - h + 3), 1)

    def _future_garden_dome(self, surf, x, base, r):
        pygame.draw.arc(surf, (153, 224, 210), (x, base - r // 2, r, r // 2), math.radians(180), math.radians(360), 1)
        pygame.draw.line(surf, self.FUTURE['hi'], (x + 3, base - 4), (x + r - 3, base - 4), 1)
        pygame.draw.line(surf, (127, 239, 194), (x + r // 2, base - r // 2 + 2), (x + r // 2, base - 4), 1)

    def _future_connector(self, surf, x, y, w, c1, c2):
        pygame.draw.line(surf, (52, 73, 110), (x, y), (x + w, y), 3)
        pygame.draw.line(surf, c1, (x + 3, y - 1), (x + w - 3, y - 1), 1)
        pygame.draw.line(surf, c2, (x + 7, y + 1), (x + w - 7, y + 1), 1)
        pygame.draw.line(surf, (47, 66, 104), (x + 2, y + 2), (x + 2, 210), 1)
        pygame.draw.line(surf, (47, 66, 104), (x + w - 2, y + 2), (x + w - 2, 210), 1)

    def _future_side_pod(self, surf, x, y, w, seed):
        body = (43, 61, 95)
        hi = self.FUTURE['hi'] if seed % 2 == 0 else self.FUTURE['spark']
        pygame.draw.rect(surf, body, (x, y, w, 18), border_radius=3)
        pygame.draw.rect(surf, (63, 88, 130), (x + 3, y + 3, w - 6, 12), border_radius=3)
        pygame.draw.line(surf, hi, (x + 4, y + 5), (x + w - 5, y + 5), 1)
        pygame.draw.line(surf, self.FUTURE['alt'], (x + 6, y + 11), (x + w - 8, y + 11), 1)
        for px in range(x + 4, x + w - 5, 6):
            pygame.draw.line(surf, (35, 48, 77), (px, y + 18), (px + 2, y + 24), 1)

    def _overlay_harmony(self, surf, frame, climate, night):
        super()._overlay_harmony(surf, frame, climate, night)
        if self.biome != 'cidade_futurista':
            return
        # tráfego aéreo mais cinematográfico, controlado e barato.
        low = not bool(getattr(self, 'visual_quality', 1))
        count = 2 if low else 4
        lanes = [258, 284, 312, 340]
        speeds = [0.22, 0.34, 0.28, 0.40]
        scales = [1.00, 0.85, 0.95, 0.75]
        for i in range(count):
            sprite = self._future_cars[(frame // 18 + i * 2) % len(self._future_cars)]
            sc = scales[i]
            car = pygame.transform.scale(sprite, (max(12, int(sprite.get_width() * sc)), max(5, int(sprite.get_height() * sc))))
            direction = -1 if i % 2 else 1
            x = int(((frame * speeds[i] * direction) + i * 131) % (WIDTH + 80)) - 40
            if direction < 0:
                x = WIDTH - x
                car = pygame.transform.flip(car, True, False)
            y = lanes[i] + int(math.sin(frame * 0.045 + i * 1.4) * 2)
            surf.blit(car, (x, y))
            glow = self.FUTURE['hi'] if i % 2 == 0 else self.FUTURE['spark']
            tailx = x - 8 if direction > 0 else x + car.get_width() + 2
            for k in range(3 if not low else 2):
                py = y + car.get_height() // 2 + (k - 1)
                ln = 4 + k * 2
                if direction > 0:
                    pygame.draw.line(surf, (*glow, 55 - k * 10), (tailx - ln, py), (tailx, py), 1)
                else:
                    pygame.draw.line(surf, (*glow, 55 - k * 10), (tailx, py), (tailx + ln, py), 1)
        # chuva/neon coerente à iluminação
        if climate in ('chuva', 'tempestade', 'chuva_acida'):
            for i in range(6 if not low else 4):
                x = int((frame * 0.8 + i * 71) % WIDTH)
                pygame.draw.line(surf, (106, 215, 233, 30), (x, 220 + i * 18), (x + 6, 232 + i * 18), 1)
