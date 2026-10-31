"""v3.156 — refinamento premium final da Cidade Futurista.

Escopo:
- aprofundar identidade arquitetônica da Cidade Futurista;
- melhorar base/solo urbano, encaixes e variedade de loops;
- aprimorar atmosfera, iluminação dia/noite e tráfego aéreo;
- preservar todos os demais biomas via herança da v3.155.0.
"""
from __future__ import annotations
import math
import random
import pygame
from pixelrush_biomes2_v3155 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, WIDTH

CH = 250


class ModularBiomeScene(Previous):
    def __init__(self, biome):
        super().__init__(biome)
        if biome == 'cidade_futurista':
            self._rebuild_future_city()
            self._map_cache.clear()

    def _surface(self):
        return pygame.Surface((LW, CH), pygame.SRCALPHA)

    # ----------------------------- city rebuild -----------------------------
    def _rebuild_future_city(self):
        # mais chunks únicos para dar sensação de metrópole gigantesca
        self._layers['far'] = [self._future_far_chunk(i) for i in range(16)]
        self._layers['mid'] = [self._future_mid_chunk(i) for i in range(18)]
        self._layers['near'] = [self._future_near_chunk(i) for i in range(20)]

    @staticmethod
    def _district_name(index: int) -> str:
        return ('corporativo', 'residencial', 'transito', 'holografico', 'industrial', 'jardins')[index % 6]

    def _future_far_chunk(self, index):
        pal = self.FUTURE
        s = self._surface()
        district = self._district_name(index)
        base = 214
        rng = random.Random(315600 + index * 97)
        # layouts amplos e diferentes por distrito
        if district == 'corporativo':
            layout = [(8, 30, 92, 0), (46, 28, 66, 1), (80, 42, 124, 2), (128, 30, 70, 0), (164, 34, 86, 1)]
        elif district == 'residencial':
            layout = [(10, 26, 68, 1), (42, 28, 78, 2), (76, 26, 62, 0), (108, 28, 72, 1), (142, 30, 92, 0), (178, 24, 60, 2)]
        elif district == 'transito':
            layout = [(8, 36, 74, 2), (50, 26, 88, 0), (82, 34, 66, 1), (120, 28, 98, 2), (166, 28, 76, 0)]
        elif district == 'holografico':
            layout = [(8, 28, 82, 1), (40, 30, 66, 2), (74, 38, 104, 0), (118, 30, 70, 1), (156, 34, 92, 2)]
        elif district == 'industrial':
            layout = [(8, 34, 60, 0), (48, 40, 74, 2), (92, 32, 84, 1), (132, 34, 72, 0), (174, 28, 62, 2)]
        else:  # jardins suspensos
            layout = [(8, 28, 72, 1), (40, 30, 88, 2), (78, 24, 62, 0), (108, 38, 116, 1), (156, 28, 78, 2)]

        for n, (x, w, h, roof) in enumerate(layout):
            height = h + rng.randrange(-6, 7)
            if district == 'corporativo' and n in (0, 2, 4):
                height += 12
            if district == 'holografico' and n == 2:
                height += 15
            if district == 'industrial' and n == 1:
                height += 8
            height = max(58, min(144, height))
            top = base - height
            body = {
                'corporativo': (45, 59, 93),
                'residencial': (50, 66, 101),
                'transito': (48, 63, 98),
                'holografico': (44, 58, 98),
                'industrial': (52, 62, 94),
                'jardins': (46, 64, 95),
            }[district]
            accent = {
                'corporativo': pal['hi'],
                'residencial': pal['alt'],
                'transito': pal['spark'],
                'holografico': pal['spark'],
                'industrial': (152, 180, 206),
                'jardins': (125, 239, 192),
            }[district]
            neon2 = pal['alt'] if district not in ('industrial', 'jardins') else (163, 214, 228)
            self._future_building(s, x, base, w, height, body, (31, 44, 73), accent, neon2,
                                  roof=roof, window_step=7, window_size=1, row_gap=8, border=False)
            if n == len(layout) // 2 or (district == 'corporativo' and n == 0):
                self._future_landmark(s, x, top, w, height, seed=500 + index * 9 + n, distant=True)
            if district == 'jardins' and w > 24:
                self._future_sky_garden(s, x + 4, top + 8, w - 8)
            if district == 'industrial' and n % 2 == 0:
                self._future_energy_stack(s, x + w // 2, top - 2)

        # horizonte com linha contínua e aerovia mais alta em alguns distritos
        pygame.draw.rect(s, (44, 61, 97), (0, 211, LW, 6))
        pygame.draw.line(s, (94, 127, 154), (0, 211), (LW - 1, 211), 1)
        if district in ('corporativo', 'transito', 'holografico'):
            y = 162 + (index % 3)
            self._future_bridge(s, 12, y, 70, pal, support=False)
            self._future_bridge(s, 132, y - 4, 64, pal, support=False)
        return s

    def _future_mid_chunk(self, index):
        pal = self.FUTURE
        s = self._surface()
        district = self._district_name(index + 1)
        base = 214
        rng = random.Random(316200 + index * 113)
        templates = {
            'corporativo': [(8, 30, 58, 1), (42, 34, 84, 0), (80, 28, 64, 2), (112, 40, 98, 0), (158, 28, 70, 1), (190, 26, 60, 2)],
            'residencial': [(8, 28, 52, 0), (40, 30, 64, 1), (74, 32, 70, 2), (110, 30, 58, 0), (144, 34, 82, 1), (182, 28, 56, 2)],
            'transito': [(8, 26, 56, 2), (38, 38, 78, 0), (82, 24, 54, 1), (110, 34, 72, 2), (148, 28, 60, 0), (180, 32, 66, 1)],
            'holografico': [(8, 28, 58, 1), (40, 30, 68, 2), (74, 42, 96, 0), (122, 26, 60, 1), (152, 28, 70, 2), (186, 26, 54, 0)],
            'industrial': [(8, 34, 50, 0), (46, 26, 72, 2), (76, 30, 60, 1), (110, 34, 68, 0), (148, 28, 74, 2), (180, 28, 58, 1)],
            'jardins': [(8, 26, 54, 1), (38, 30, 72, 2), (72, 28, 62, 0), (104, 34, 76, 1), (142, 30, 68, 2), (178, 28, 58, 0)],
        }
        accent_pairs = {
            'corporativo': ((pal['hi'], pal['spark']), (pal['spark'], pal['alt'])),
            'residencial': (((154, 218, 238), pal['alt']), (pal['alt'], (194, 240, 255))),
            'transito': ((pal['spark'], pal['hi']), (pal['hi'], pal['spark'])),
            'holografico': ((pal['spark'], pal['alt']), (pal['hi'], pal['spark'])),
            'industrial': (((193, 220, 235), (128, 218, 241)), ((160, 200, 219), pal['hi'])),
            'jardins': (((125, 239, 192), pal['hi']), (pal['hi'], (167, 255, 214))),
        }
        for n, (x, w, h, roof) in enumerate(templates[district]):
            height = h + rng.randrange(-5, 7)
            if district == 'corporativo' and n in (1, 3):
                height += 15
            if district == 'holografico' and n == 2:
                height += 18
            if district == 'industrial' and n == 4:
                height += 10
            if district == 'jardins' and n == 3:
                height += 9
            body = {
                'corporativo': (70, 90, 129),
                'residencial': (74, 96, 138),
                'transito': (69, 89, 128),
                'holografico': (67, 88, 136),
                'industrial': (74, 87, 120),
                'jardins': (69, 96, 126),
            }[district]
            shade = {
                'corporativo': (42, 58, 91),
                'residencial': (47, 61, 95),
                'transito': (44, 59, 92),
                'holografico': (42, 55, 93),
                'industrial': (50, 60, 86),
                'jardins': (44, 61, 84),
            }[district]
            c1, c2 = accent_pairs[district][(n + index) % 2]
            self._future_building(s, x, base, w, height, body, shade, c1, c2,
                                  roof=(roof + index + n) % 3,
                                  window_step=6 if n % 2 == 0 else 7,
                                  window_size=2 if district not in ('industrial',) else 1,
                                  row_gap=7 if district in ('corporativo', 'holografico') else 8,
                                  border=True)
            top = base - height
            if w >= 24 and height >= 56 and n % 2 == 0:
                panel_h = 7 if district != 'holografico' else 8
                self._future_facade_panel(s, x + 4, top + 14 + (n % 3) * 5, min(w - 8, 19), panel_h, c1, c2)
            if district == 'jardins' and w >= 24 and n in (1, 4):
                self._future_sky_garden(s, x + 4, top + 10, w - 8)
            if district == 'industrial' and n in (1, 4):
                self._future_energy_stack(s, x + w // 2, top - 1)
            if district == 'transito' and n in (1, 3):
                self._future_transit_gate(s, x + 4, top + height - 20, w - 8, c1)
            if district in ('corporativo', 'holografico') and height >= 78 and n in (1, 3):
                self._future_landmark(s, x, top, w, height, seed=840 + index * 7 + n, distant=False)
            if n % 3 == 1 and w > 26:
                self._future_accent_facade(s, x, top, w, height, c1)

        # Skyways distintas por distrito, sempre ancoradas.
        if district in ('transito', 'corporativo', 'holografico'):
            bridges = [(26, 186, 42), (120, 190, 52)] if district != 'corporativo' else [(30, 184, 50), (138, 188, 44)]
            for x, y, w in bridges:
                self._future_bridge(s, x, y, w, pal, support=True)
                pygame.draw.line(s, (48, 63, 96), (x + 2, y + 4), (x + 2, 212), 2)
                pygame.draw.line(s, (48, 63, 96), (x + w - 3, y + 4), (x + w - 3, 212), 2)

        # Rodapé estrutural contínuo.
        pygame.draw.rect(s, (54, 72, 108), (0, 211, LW, 6))
        pygame.draw.line(s, (94, 130, 158), (0, 211), (LW - 1, 211), 1)
        return s

    def _future_near_chunk(self, index):
        pal = self.FUTURE
        s = self._surface()
        district = self._district_name(index + 2)
        rng = random.Random(316900 + index * 149)
        deck_top = 180
        deck_mid = 197
        deck_bottom = 219
        canal_top = 223

        # base urbana em três materiais: placa superior, corpo estrutural e faixa inferior
        pygame.draw.rect(s, (53, 72, 110), (0, deck_top, LW, deck_bottom - deck_top))
        pygame.draw.rect(s, (40, 55, 86), (0, deck_mid, LW, deck_bottom - deck_mid))
        pygame.draw.line(s, pal['hi'], (0, deck_top + 2), (LW, deck_top + 2), 1)
        pygame.draw.line(s, pal['spark'], (0, deck_mid + 2), (LW, deck_mid + 2), 1)

        # avenida superior mais premium
        avenue_y = 193
        pygame.draw.rect(s, (83, 104, 148), (0, avenue_y, LW, 9))
        pygame.draw.line(s, (202, 233, 239), (0, avenue_y), (LW, avenue_y), 1)
        pygame.draw.line(s, pal['hi'], (0, avenue_y + 2), (LW, avenue_y + 2), 1)
        pygame.draw.line(s, pal['spark'], (0, avenue_y + 7), (LW, avenue_y + 7), 1)
        # subdivisões do piso metálico
        for x in range(0, LW + 1, 28):
            pygame.draw.line(s, (65, 83, 123), (x, avenue_y), (x, avenue_y + 8), 1)
        for x in range(8, LW - 8, 32):
            pygame.draw.line(s, (100, 124, 176), (x, avenue_y - 1), (x + 10, avenue_y - 1), 1)

        # guarda-corpo e postes de luz suaves
        for x in range(0, LW, 18):
            pygame.draw.line(s, (104, 128, 178), (x, avenue_y), (x, avenue_y - 7), 1)
        for x in range(10, LW, 56):
            pygame.draw.line(s, (83, 100, 140), (x, avenue_y - 7), (x, avenue_y - 15), 1)
            pygame.draw.rect(s, pal['spark'] if (x // 56 + index) % 2 else pal['hi'], (x - 1, avenue_y - 16, 3, 2))

        # pilares e encaixes de engenharia
        pillar_sets = [14, 48, 84, 118, 156, 196] if index % 2 == 0 else [8, 38, 72, 110, 150, 188, 214]
        for x in pillar_sets:
            height = 30 + (x % 3)
            pygame.draw.rect(s, (46, 61, 94), (x, avenue_y + 9, 6, height))
            pygame.draw.line(s, (91, 113, 158), (x + 2, avenue_y + 9), (x + 2, avenue_y + height + 8), 1)
            pygame.draw.line(s, (68, 86, 124), (x, avenue_y + 18), (x - 4, avenue_y + height + 8), 1)
            pygame.draw.line(s, (68, 86, 124), (x + 6, avenue_y + 18), (x + 10, avenue_y + height + 8), 1)

        # módulos baixos e estabelecimentos laterais, fora do centro da pista
        modules_by_district = {
            'corporativo': [(8, 170, 28, 24), (42, 166, 36, 28), (150, 170, 26, 22), (182, 166, 34, 28)],
            'residencial': [(8, 174, 24, 20), (38, 168, 30, 24), (152, 174, 24, 20), (182, 168, 30, 24)],
            'transito': [(10, 171, 30, 23), (46, 168, 26, 26), (148, 171, 30, 23), (182, 168, 28, 26)],
            'holografico': [(6, 170, 28, 24), (40, 166, 34, 28), (150, 170, 28, 24), (184, 166, 32, 28)],
            'industrial': [(6, 172, 30, 22), (40, 168, 34, 26), (148, 172, 30, 22), (184, 168, 30, 26)],
            'jardins': [(10, 172, 24, 22), (40, 166, 34, 28), (150, 172, 24, 22), (182, 166, 34, 28)],
        }
        for n, (x, y, w, h) in enumerate(modules_by_district[district]):
            body = (67, 88, 129) if n % 2 == 0 else (58, 77, 116)
            pygame.draw.rect(s, body, (x, y, w, h))
            pygame.draw.rect(s, (42, 58, 88), (x, y + h - 4, w, 4))
            pygame.draw.line(s, pal['hi'] if n % 2 == 0 else pal['spark'], (x + 2, y + 3), (x + w - 3, y + 3), 1)
            if w > 24:
                pygame.draw.line(s, pal['alt'], (x + 3, y + 8), (x + w - 4, y + 8), 1)
            if district == 'jardins' and n in (1, 3):
                self._future_small_plants(s, x + 4, y + 1, max(8, w - 8))
            elif district == 'industrial' and n in (1, 2):
                self._future_pipe_run(s, x + 2, y + 10, w - 4)

        # jardineiras laterais e vida urbana controlada
        planter_sets = [((78, 186, 18), (128, 186, 20)), ((90, 186, 18), (138, 186, 18)), ((72, 186, 18), (142, 186, 18)), ((86, 186, 18), (132, 186, 18))]
        for x, y, w in planter_sets[index % len(planter_sets)]:
            pygame.draw.rect(s, (74, 92, 128), (x, y, w, 6))
            pygame.draw.line(s, pal['spark'], (x + 1, y + 1), (x + w - 2, y + 1), 1)
            self._future_small_plants(s, x + 3, y, w - 6)

        # canal/reflexo inferior menos saturado e mais elegante
        pygame.draw.rect(s, (29, 73, 108), (0, canal_top, LW, 12))
        pygame.draw.line(s, (82, 176, 191), (0, canal_top), (LW - 1, canal_top), 1)
        for x in range(8, LW - 8, 28):
            c = (108, 204, 221) if ((x // 28) + index) % 2 == 0 else (151, 114, 182)
            pygame.draw.line(s, c, (x, canal_top + 4), (x + 8, canal_top + 4), 1)
            pygame.draw.line(s, (56, 121, 154), (x + 4, canal_top + 8), (x + 11, canal_top + 8), 1)

        # luzes de borda e detalhes de encaixe
        for x in range(12, LW - 12, 24):
            c = pal['hi'] if ((x // 24) + index) % 2 == 0 else pal['spark']
            pygame.draw.line(s, c, (x, avenue_y - 2), (x + 6, avenue_y - 2), 1)
        return s

    # ----------------------------- small helpers -----------------------------
    @staticmethod
    def _future_sky_garden(s, x, y, width):
        cols = ((123, 238, 187), (149, 255, 214), (102, 214, 168))
        for i, xx in enumerate(range(x, x + width, 5)):
            c = cols[i % len(cols)]
            pygame.draw.line(s, c, (xx, y + 6), (xx + 1, y + 2), 1)
            if i % 2 == 0:
                pygame.draw.line(s, c, (xx + 1, y + 4), (xx + 3, y + 1), 1)

    @staticmethod
    def _future_energy_stack(s, cx, top):
        pygame.draw.rect(s, (58, 75, 112), (cx - 3, top - 7, 6, 7))
        pygame.draw.line(s, (208, 233, 238), (cx, top - 12), (cx, top - 7), 1)
        pygame.draw.rect(s, (125, 239, 244), (cx - 1, top - 13, 3, 2))

    @staticmethod
    def _future_transit_gate(s, x, y, width, accent):
        pygame.draw.rect(s, (55, 74, 109), (x, y, width, 4))
        pygame.draw.line(s, accent, (x + 1, y + 1), (x + width - 2, y + 1), 1)
        pygame.draw.line(s, (45, 61, 94), (x + 3, y + 4), (x + 3, y + 11), 1)
        pygame.draw.line(s, (45, 61, 94), (x + width - 4, y + 4), (x + width - 4, y + 11), 1)

    @staticmethod
    def _future_pipe_run(s, x, y, width):
        pygame.draw.line(s, (166, 200, 216), (x, y), (x + width, y), 1)
        pygame.draw.line(s, (103, 127, 152), (x, y + 2), (x + width, y + 2), 1)
        for px in range(x + 4, x + width, 8):
            pygame.draw.line(s, (69, 86, 118), (px, y - 1), (px, y + 3), 1)

    # ----------------------------- overlays -----------------------------
    def _overlay_harmony(self, surf, frame, climate, night):
        if self.biome != 'cidade_futurista':
            return super()._overlay_harmony(surf, frame, climate, night)
        pal = self.FUTURE
        # profundidade atmosférica: névoa luminosa no horizonte
        haze_alpha = 12 if night < 0.25 else 20
        for y, spread in ((340, 7), (370, 10), (404, 13)):
            yy = y + int(math.sin(frame * 0.01 + y * 0.02) * 2)
            pygame.draw.line(surf, (106, 190, 208, haze_alpha), (0, yy), (WIDTH, yy), 1)
            pygame.draw.line(surf, (190, 103, 184, max(4, haze_alpha - spread)), (0, yy + 6), (WIDTH, yy + 6), 1)

        # padrão de janelas/letreiros vivos ao anoitecer
        if night > 0.20:
            for k in range(7 if self.visual_quality else 4):
                xx = (36 + k * 57 + frame // 4) % WIDTH
                yy = 285 + (k % 3) * 18
                col = (pal['spark'][0], pal['spark'][1], pal['spark'][2], 34) if k % 2 == 0 else (pal['hi'][0], pal['hi'][1], pal['hi'][2], 28)
                pygame.draw.rect(surf, col, (xx, yy, 3, 2))

        # tráfego aéreo cinematográfico em duas alturas, com três modelos
        count = 5 if self.visual_quality else 3
        for i in range(count):
            direction = -1 if i % 3 == 1 else 1
            speed = (0.47, 0.68, 0.92, 0.58, 1.08)[i % 5]
            x = int((i * 127 + frame * speed * direction) % (WIDTH + 80)) - 40
            y = 228 + i * 27 + int(math.sin(frame * 0.024 + i * 1.7) * 4)
            style = (i + frame // 70) % 3
            phase = (frame // (10 + i % 2 * 2) + i) % 2
            sprite = self._future_car_flip_sprites[(style, phase)] if direction < 0 else self._future_car_sprites[(style, phase)]
            surf.blit(sprite, (x, y))
            exhaust_x = x - 2 if direction > 0 else x + 29
            for j in range(3):
                off = (frame // 3 + j * 3 + i * 2) % 12
                color = (120, 228, 243, 86 - j * 20) if j < 2 else (244, 132, 210, 44)
                pygame.draw.line(surf, color, (exhaust_x - direction * off, y + 9 + j), (exhaust_x - direction * (off + 4), y + 9 + j), 1)

        # drones menores e sinais de navegação muito discretos
        if self.visual_quality:
            for i in range(3):
                xx = int((60 + i * 154 - frame * (0.25 + i * 0.06)) % (WIDTH + 40)) - 10
                yy = 250 + i * 36 + int(math.sin(frame * 0.03 + i) * 2)
                pygame.draw.line(surf, (pal['alt'][0], pal['alt'][1], pal['alt'][2], 26), (xx, yy), (xx + 7, yy), 1)
                pygame.draw.rect(surf, (pal['spark'][0], pal['spark'][1], pal['spark'][2], 34), (xx + 6, yy, 2, 1))

        # clima reativo
        if climate == 'vento_neon':
            for k in range(6 if self.visual_quality else 3):
                xx = int((k * 93 + frame * 1.35) % (WIDTH + 30)) - 15
                yy = 210 + (k * 41 + frame // 2) % 150
                pygame.draw.line(surf, (108, 224, 239, 34), (xx, yy), (xx + 10, yy + 2), 1)
                if k % 2 == 0:
                    pygame.draw.line(surf, (244, 132, 210, 20), (xx + 4, yy + 1), (xx + 12, yy + 2), 1)
        elif climate == 'chuva_acida':
            for k in range(8 if self.visual_quality else 4):
                xx = int((k * 71 - frame * 1.65) % (WIDTH + 30)) - 15
                yy = 180 + (k * 53 + frame * 2) % 200
                pygame.draw.line(surf, (146, 241, 135, 44), (xx, yy), (xx - 3, yy + 10), 1)
