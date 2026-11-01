"""v3.158 — Ilhas Celestiais 2.0 premium.

Escopo:
- aplicar nas Ilhas Celestiais as 6 frentes de refino usadas como base na Cidade Futurista,
  mas reinterpretadas para um bioma celeste inspirado por Avatar:
  1) distritos arquitetônicos únicos sobre ilhas;
  2) iluminação inteligente dia/noite;
  3) piso/base premium em mármore e pedra luminosa;
  4) tráfego aéreo cinematográfico com aeronaves celestiais;
  5) atmosfera e profundidade cinematográficas;
  6) acabamento técnico anti-bugs, com 42 chunks (12+14+16).
- preservar Cidade Futurista e Vulcão da v3.157.0.
"""
from __future__ import annotations
import math
import random
import pygame
from pixelrush_biomes2_v3157 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, LH, WIDTH


class ModularBiomeScene(Previous):
    DISTRICTS = (
        'acropole_marmore',
        'jardins_bioluminescentes',
        'residencial_suspenso',
        'santuario_cristal',
        'pontes_celestes',
        'docas_aereas',
    )

    def __init__(self, biome):
        super().__init__(biome)
        if biome == 'ilhas_celestes':
            self._rebuild_celestial_islands()
            self._build_celestial_aircraft_cache()
            self._map_cache.clear()

    # ----------------------------- setup -----------------------------
    @staticmethod
    def _s():
        return pygame.Surface((LW, LH), pygame.SRCALPHA)

    @classmethod
    def _district_name(cls, index: int) -> str:
        return cls.DISTRICTS[index % len(cls.DISTRICTS)]

    def _rebuild_celestial_islands(self):
        # 42 chunks totais para QA específico das Ilhas Celestiais.
        self._layers['far'] = [self._celestial_far_chunk(i) for i in range(12)]
        self._layers['mid'] = [self._celestial_mid_chunk(i) for i in range(14)]
        self._layers['near'] = [self._celestial_near_chunk(i) for i in range(16)]

    def _build_celestial_aircraft_cache(self):
        self._cel_air = {}
        self._cel_air_flip = {}
        for style in range(3):
            for phase in range(2):
                sp = pygame.Surface((30, 15), pygame.SRCALPHA)
                glow = ((114, 241, 255), (152, 255, 225), (248, 221, 247))[style]
                hull = ((156, 176, 193), (168, 185, 208), (143, 165, 188))[style]
                trim = ((77, 108, 141), (88, 121, 151), (67, 97, 131))[style]
                # casco em formato de barca/raia
                pygame.draw.polygon(sp, hull, [(2, 9), (7, 4), (18, 2), (26, 5), (28, 8), (21, 12), (9, 13)])
                pygame.draw.line(sp, (233, 244, 245), (8, 5), (19, 3), 1)
                pygame.draw.line(sp, trim, (4, 10), (22, 11), 1)
                pygame.draw.line(sp, glow, (7, 10), (18, 10), 1)
                if style == 0:
                    pygame.draw.polygon(sp, (189, 219, 226), [(11, 2), (14, 0), (17, 2), (17, 5), (11, 5)])
                elif style == 1:
                    pygame.draw.polygon(sp, (206, 236, 242), [(9, 3), (15, 0), (20, 3), (18, 6), (10, 6)])
                    pygame.draw.line(sp, glow, (15, 1), (15, 5), 1)
                else:
                    pygame.draw.polygon(sp, (198, 230, 234), [(10, 3), (14, 1), (20, 2), (22, 5), (13, 6)])
                    pygame.draw.line(sp, glow, (9, 8), (21, 8), 1)
                # propulsão / fase
                thr = 3 + phase
                for j in range(thr):
                    px = 1 - j * 2
                    py = 8 + (j % 2)
                    c = glow if j < 2 else (255, 246, 181)
                    pygame.draw.rect(sp, c, (max(0, px), py, 2, 1))
                self._cel_air[(style, phase)] = sp
                self._cel_air_flip[(style, phase)] = pygame.transform.flip(sp, True, False)

    # ----------------------------- far -----------------------------
    def _celestial_far_chunk(self, index):
        s = self._s()
        district = self._district_name(index)
        rng = random.Random(318800 + index * 91)
        palettes = self._district_palette(district)
        configs = {
            'acropole_marmore': [(12, 116, 74, 42, 'acropole', True), (134, 127, 60, 35, 'obelisk', False)],
            'jardins_bioluminescentes': [(16, 122, 70, 40, 'garden', True), (126, 112, 78, 48, 'tree', True)],
            'residencial_suspenso': [(18, 120, 68, 40, 'residences', False), (129, 127, 65, 37, 'arches', False)],
            'santuario_cristal': [(14, 123, 74, 42, 'crystal', True), (132, 115, 70, 45, 'shrine', False)],
            'pontes_celestes': [(12, 128, 62, 38, 'arches', False), (127, 120, 74, 41, 'bridge', False)],
            'docas_aereas': [(16, 124, 68, 39, 'docks', False), (128, 116, 76, 45, 'towerdock', False)],
        }
        for x, y, w, h, style, glow in configs[district]:
            self._celestial_island(s, x, y, w, h, rng, palettes, level=0, style=style, glow=glow,
                                   waterfalls=1 if style in ('garden', 'shrine') else 0)
        # névoa de profundidade já pré-renderizada no fundo
        pygame.draw.rect(s, (181, 221, 229, 16), (0, 176, LW, 8))
        pygame.draw.line(s, (156, 209, 224), (0, 184), (LW - 1, 184), 1)
        return s

    # ----------------------------- mid -----------------------------
    def _celestial_mid_chunk(self, index):
        s = self._s()
        district = self._district_name(index + 2)
        rng = random.Random(319600 + index * 113)
        palettes = self._district_palette(district)
        chunk_map = {
            'acropole_marmore': [
                (14, 148, 82, 53, 'acropole', 1, True),
                (126, 140, 78, 49, 'obelisk', 0, False),
            ],
            'jardins_bioluminescentes': [
                (18, 147, 75, 50, 'garden', 1, True),
                (122, 138, 84, 55, 'tree', 1, True),
            ],
            'residencial_suspenso': [
                (16, 150, 79, 49, 'residences', 0, False),
                (128, 145, 74, 45, 'bridge', 0, False),
            ],
            'santuario_cristal': [
                (14, 150, 77, 50, 'crystal', 1, True),
                (120, 142, 86, 57, 'shrine', 0, True),
            ],
            'pontes_celestes': [
                (16, 147, 72, 46, 'arches', 0, False),
                (116, 142, 92, 53, 'bridge', 1, False),
            ],
            'docas_aereas': [
                (15, 149, 76, 48, 'docks', 0, False),
                (127, 141, 82, 52, 'towerdock', 1, False),
            ],
        }
        entries = chunk_map[district]
        for x, y, w, h, style, falls, glow in entries:
            self._celestial_island(s, x, y, w, h, rng, palettes, level=1, style=style, glow=glow, waterfalls=falls)
        # passarelas/templos de apoio distintos por distrito
        if district in ('pontes_celestes', 'acropole_marmore', 'docas_aereas'):
            if district == 'pontes_celestes':
                self._celestial_bridge(s, 52, 156, 120, palettes['accent'])
            elif district == 'acropole_marmore':
                self._celestial_bridge(s, 42, 162, 96, palettes['gold'])
            else:
                self._celestial_bridge(s, 58, 160, 106, palettes['glow'])
        # véu de profundidade do plano médio
        pygame.draw.rect(s, (192, 228, 236, 12), (0, 188, LW, 7))
        return s

    # ----------------------------- near -----------------------------
    def _celestial_near_chunk(self, index):
        s = self._s()
        district = self._district_name(index + 4)
        palettes = self._district_palette(district)
        rng = random.Random(320400 + index * 131)

        deck_y = 221
        # piso premium em mármore / pedra luminosa, mantendo corredor limpo
        pygame.draw.rect(s, palettes['road_top'], (0, deck_y, LW, 11))
        pygame.draw.line(s, palettes['road_edge'], (0, deck_y), (LW - 1, deck_y), 2)
        pygame.draw.line(s, palettes['glow'], (0, deck_y + 2), (LW - 1, deck_y + 2), 1)
        pygame.draw.rect(s, palettes['road_body'], (0, 232, LW, 18))
        pygame.draw.line(s, palettes['shadow'], (0, 232), (LW - 1, 232), 1)
        # placas/junções discretas e runas embutidas
        for x in range(8 + (index % 3) * 2, LW, 26):
            pygame.draw.line(s, palettes['joint'], (x, deck_y + 1), (x, 249), 1)
            pygame.draw.line(s, palettes['glow_soft'], (x + 2, deck_y + 6), (min(LW - 1, x + 11), deck_y + 6), 1)
        for x in range(12, LW - 10, 36):
            self._celestial_rune(s, x, 240, palettes)
        # guarda-corpo marmóreo e suportes pendentes
        for x in range(0, LW, 18):
            pygame.draw.line(s, palettes['rail'], (x, deck_y), (x, deck_y - 7), 1)
        for x in (14, 46, 81, 116, 154, 191, 214):
            h = 12 + (x % 3) * 3
            pygame.draw.rect(s, palettes['support'], (x, 233, 5, h))
            pygame.draw.line(s, palettes['support_hi'], (x + 2, 233), (x + 2, 233 + h - 1), 1)
            pygame.draw.line(s, palettes['support_lo'], (x, 238), (x - 3, 233 + h), 1)
            pygame.draw.line(s, palettes['support_lo'], (x + 5, 238), (x + 8, 233 + h), 1)
        # canal celeste inferior sutil
        pygame.draw.rect(s, palettes['mist_water'], (0, 223, LW, 8))
        pygame.draw.line(s, palettes['mist_line'], (0, 223), (LW - 1, 223), 1)
        for x in range(8, LW - 8, 28):
            pygame.draw.line(s, palettes['mist_shimmer'], (x, 226), (x + 8, 226), 1)

        # duas ilhas laterais, deixando o centro livre
        left_style, right_style = {
            'acropole_marmore': ('obelisk', 'acropole'),
            'jardins_bioluminescentes': ('garden', 'tree'),
            'residencial_suspenso': ('residences', 'arches'),
            'santuario_cristal': ('crystal', 'shrine'),
            'pontes_celestes': ('arches', 'bridge'),
            'docas_aereas': ('docks', 'towerdock'),
        }[district]
        self._celestial_island(s, 8, 176, 58, 37, rng, palettes, level=2, style=left_style, glow=True,
                               waterfalls=1 if left_style in ('garden', 'shrine') else 0)
        self._celestial_island(s, 162, 176, 55, 36, rng, palettes, level=2, style=right_style, glow=True,
                               waterfalls=1 if right_style in ('tree', 'bridge') else 0)
        return s

    # ----------------------------- drawing helpers -----------------------------
    def _district_palette(self, district):
        base = {
            'acropole_marmore': dict(grass=(118, 210, 155), grass_dark=(78, 141, 114), rock=(111, 118, 154),
                                     side=(152, 160, 193), marble=(219, 228, 234), marble_hi=(244, 248, 249),
                                     glow=(127, 230, 242), glow_soft=(172, 244, 249), gold=(227, 213, 156), accent=(154, 193, 223)),
            'jardins_bioluminescentes': dict(grass=(98, 214, 162), grass_dark=(63, 145, 115), rock=(97, 108, 144),
                                     side=(132, 147, 181), marble=(205, 220, 229), marble_hi=(238, 246, 247),
                                     glow=(122, 249, 212), glow_soft=(183, 255, 228), gold=(215, 229, 173), accent=(136, 232, 210)),
            'residencial_suspenso': dict(grass=(121, 203, 162), grass_dark=(79, 138, 119), rock=(104, 113, 147),
                                     side=(141, 150, 186), marble=(214, 224, 232), marble_hi=(242, 247, 249),
                                     glow=(136, 224, 246), glow_soft=(188, 244, 252), gold=(226, 215, 177), accent=(156, 202, 229)),
            'santuario_cristal': dict(grass=(114, 209, 167), grass_dark=(77, 147, 124), rock=(100, 109, 150),
                                     side=(139, 151, 188), marble=(213, 225, 235), marble_hi=(244, 248, 250),
                                     glow=(143, 221, 255), glow_soft=(203, 246, 255), gold=(220, 206, 177), accent=(196, 182, 255)),
            'pontes_celestes': dict(grass=(113, 197, 158), grass_dark=(76, 132, 113), rock=(98, 109, 143),
                                     side=(135, 148, 182), marble=(207, 221, 231), marble_hi=(240, 246, 249),
                                     glow=(136, 232, 250), glow_soft=(189, 247, 255), gold=(221, 208, 168), accent=(148, 205, 240)),
            'docas_aereas': dict(grass=(111, 188, 148), grass_dark=(73, 125, 102), rock=(99, 107, 136),
                                     side=(132, 143, 174), marble=(205, 217, 226), marble_hi=(237, 243, 246),
                                     glow=(140, 215, 240), glow_soft=(195, 238, 250), gold=(211, 203, 167), accent=(162, 190, 222)),
        }[district].copy()
        base.update(dict(
            road_top=(184, 194, 210), road_edge=(236, 244, 246), road_body=(108, 125, 153),
            shadow=(83, 96, 119), joint=(120, 137, 166), rail=(170, 202, 217),
            support=(96, 113, 140), support_hi=(153, 182, 204), support_lo=(77, 93, 115),
            mist_water=(66, 132, 154), mist_line=(139, 219, 228), mist_shimmer=(182, 240, 246),
        ))
        return base

    def _celestial_island(self, s, x, y, w, h, rng, pal, level, style, glow=False, waterfalls=0):
        # base volumétrica única para evitar fragmentos soltos.
        top_y = y
        bottom = y + h
        rock = pal['rock'] if level == 0 else tuple(max(0, c - (6 if level == 1 else 0)) for c in pal['rock'])
        side = pal['side'] if level < 2 else tuple(min(255, c + 5) for c in pal['side'])
        # silhueta principal da ilha
        pts = [
            (x + 4, top_y + 6), (x + 14, top_y), (x + w - 18, top_y), (x + w - 4, top_y + 6),
            (x + w - 10, top_y + 18), (x + w // 2 + 8, bottom - 6), (x + w // 2, bottom),
            (x + w // 3, bottom - 8), (x + 9, top_y + 20)
        ]
        pygame.draw.polygon(s, rock, pts)
        pygame.draw.polygon(s, side, [(x + 7, top_y + 11), (x + w // 2, top_y + 12), (x + w // 2 - 5, bottom - 11),
                                      (x + w // 3, top_y + h // 2), (x + 8, top_y + h // 3)])
        pygame.draw.polygon(s, (max(0, rock[0] - 25), max(0, rock[1] - 20), max(0, rock[2] - 14)),
                            [(x + w // 2 + 5, top_y + 14), (x + w - 8, top_y + 8), (x + w - 12, top_y + h // 2),
                             (x + w // 2 + 7, bottom - 7)])
        # platô gramado azul-esverdeado brilhante
        pygame.draw.polygon(s, pal['grass_dark'], [(x + 3, top_y + 5), (x + 12, top_y - 1), (x + w - 13, top_y - 1),
                                                   (x + w - 4, top_y + 4), (x + w - 8, top_y + 9), (x + 6, top_y + 9)])
        pygame.draw.polygon(s, pal['grass'], [(x + 5, top_y + 3), (x + 15, top_y - 3), (x + w - 16, top_y - 3),
                                              (x + w - 6, top_y + 2), (x + w - 10, top_y + 6), (x + 8, top_y + 6)])
        pygame.draw.line(s, (216, 244, 218), (x + 12, top_y), (x + w - 12, top_y), 1)
        # estratificação mineral e pequenos brilhos orgânicos
        for k in range(max(3, w // 14)):
            xx = x + 9 + k * max(4, (w - 18) // max(3, w // 14))
            pygame.draw.line(s, (170, 181, 201), (xx, top_y + 14 + (k % 2) * 4), (xx + 5, top_y + 17 + (k % 2) * 4), 1)
            pygame.draw.line(s, (98, 115, 146), (xx + 1, top_y + 18), (xx, top_y + 25), 1)
            if glow and k % 2 == 0:
                pygame.draw.rect(s, pal['glow_soft'], (xx + 1, top_y - 2 - (k % 2), 2, 2))

        # raízes e cipós presos à ilha
        if level < 2:
            for dx in (w // 3, 2 * w // 3):
                xx = x + dx
                yy = top_y + h // 2 + 2
                pygame.draw.line(s, (90, 141, 127), (xx, yy), (xx + 1, yy + 10), 1)
                pygame.draw.line(s, (130, 194, 163), (xx + 1, yy + 5), (xx + 4, yy + 2), 1)

        # monumentos/arquitetura contextual
        self._place_celestial_architecture(s, x, top_y, w, pal, style, level)

        # cachoeiras integradas
        for f in range(waterfalls):
            wx = x + w // 2 + (f * 9 - 3)
            self._water_from_island(s, wx, top_y + 8, min(60, 250 - top_y - 8), rng)

    def _place_celestial_architecture(self, s, x, top_y, w, pal, style, level):
        cx = x + w // 2
        base = top_y + 1
        if style == 'acropole':
            self._marble_acropolis(s, cx, base, min(w - 14, 34), pal, level)
        elif style == 'obelisk':
            self._marble_obelisk(s, cx, base, pal, level)
        elif style == 'garden':
            self._garden_terraces(s, cx, base, min(w - 14, 32), pal)
        elif style == 'tree':
            self._sacred_tree(s, cx, base, min(w - 18, 28), pal)
        elif style == 'residences':
            self._suspended_houses(s, cx, base, min(w - 12, 32), pal)
        elif style == 'crystal':
            self._crystal_monument(s, cx, base, min(w - 16, 24), pal)
        elif style == 'shrine':
            self._open_shrine(s, cx, base, min(w - 14, 30), pal)
        elif style == 'arches':
            self._marble_arches(s, cx, base, min(w - 14, 32), pal)
        elif style == 'bridge':
            self._small_bridge_complex(s, cx, base, min(w - 10, 36), pal)
        elif style == 'docks':
            self._sky_docks(s, cx, base, min(w - 10, 34), pal)
        elif style == 'towerdock':
            self._dock_tower(s, cx, base, min(w - 14, 28), pal)

    @staticmethod
    def _marble_acropolis(s, cx, base, w, pal, level):
        x = cx - w // 2
        pygame.draw.rect(s, pal['marble'], (x, base - 22, w, 22))
        pygame.draw.rect(s, pal['marble_hi'], (x + 2, base - 21, w - 4, 18))
        pygame.draw.polygon(s, pal['marble_hi'], [(x - 2, base - 22), (cx, base - 30 - level), (x + w + 2, base - 22)])
        for col in range(x + 5, x + w - 4, 8):
            pygame.draw.rect(s, pal['accent'], (col, base - 17, 3, 14))
            pygame.draw.line(s, (247, 250, 250), (col, base - 16), (col, base - 4), 1)
        pygame.draw.rect(s, pal['glow'], (cx - 2, base - 10, 4, 7))
        pygame.draw.line(s, pal['gold'], (x + 3, base - 23), (x + w - 4, base - 23), 1)

    @staticmethod
    def _marble_obelisk(s, cx, base, pal, level):
        pygame.draw.polygon(s, pal['marble'], [(cx - 6, base), (cx - 2, base - 23 - level), (cx + 2, base - 23 - level), (cx + 6, base)])
        pygame.draw.line(s, pal['marble_hi'], (cx - 1, base - 22), (cx - 1, base - 2), 1)
        pygame.draw.rect(s, pal['glow'], (cx - 2, base - 10, 5, 2))
        pygame.draw.rect(s, pal['gold'], (cx - 1, base - 27 - level, 3, 3))

    @staticmethod
    def _garden_terraces(s, cx, base, w, pal):
        x = cx - w // 2
        pygame.draw.rect(s, pal['marble'], (x, base - 9, w, 9))
        pygame.draw.rect(s, pal['marble_hi'], (x + 1, base - 8, w - 2, 6))
        pygame.draw.rect(s, pal['marble'], (x + 5, base - 18, w - 10, 8))
        for xx in range(x + 4, x + w - 4, 5):
            pygame.draw.line(s, pal['glow_soft'], (xx, base - 11), (xx + 1, base - 15), 1)
            pygame.draw.line(s, pal['grass'], (xx + 1, base - 14), (xx + 3, base - 17), 1)

    @staticmethod
    def _sacred_tree(s, cx, base, w, pal):
        pygame.draw.line(s, (116, 156, 176), (cx, base), (cx, base - 16), 3)
        pygame.draw.line(s, (130, 176, 194), (cx, base - 10), (cx - 5, base - 18), 2)
        pygame.draw.line(s, (130, 176, 194), (cx, base - 11), (cx + 6, base - 20), 2)
        for px, py in ((cx - 6, base - 21), (cx, base - 24), (cx + 7, base - 20), (cx - 10, base - 16), (cx + 11, base - 15)):
            pygame.draw.circle(s, pal['glow_soft'], (px, py), 2)
            pygame.draw.circle(s, pal['glow'], (px, py), 1)

    @staticmethod
    def _suspended_houses(s, cx, base, w, pal):
        x = cx - w // 2
        for offset in (0, w // 2):
            hx = x + offset
            pygame.draw.rect(s, pal['marble'], (hx + 2, base - 16, w // 2 - 4, 12))
            pygame.draw.polygon(s, pal['marble_hi'], [(hx, base - 16), (hx + w // 4, base - 21), (hx + w // 2, base - 16)])
            pygame.draw.rect(s, pal['accent'], (hx + w // 4 - 2, base - 11, 4, 7))
            pygame.draw.line(s, pal['glow'], (hx + 4, base - 17), (hx + w // 2 - 5, base - 17), 1)
        pygame.draw.line(s, pal['gold'], (x + 3, base - 3), (x + w - 4, base - 3), 1)

    @staticmethod
    def _crystal_monument(s, cx, base, w, pal):
        pygame.draw.polygon(s, pal['accent'], [(cx - 7, base), (cx - 3, base - 18), (cx + 1, base - 10), (cx + 5, base - 22), (cx + 8, base)])
        pygame.draw.polygon(s, pal['glow_soft'], [(cx - 5, base), (cx - 2, base - 14), (cx + 1, base - 8), (cx + 4, base - 18), (cx + 5, base)])
        pygame.draw.line(s, pal['glow'], (cx - 1, base - 14), (cx + 2, base - 4), 1)
        pygame.draw.rect(s, pal['marble'], (cx - 8, base, 16, 4))

    @staticmethod
    def _open_shrine(s, cx, base, w, pal):
        x = cx - w // 2
        pygame.draw.rect(s, pal['marble'], (x + 2, base - 7, w - 4, 7))
        pygame.draw.rect(s, pal['marble'], (x + 5, base - 19, 3, 12))
        pygame.draw.rect(s, pal['marble'], (x + w - 8, base - 19, 3, 12))
        pygame.draw.polygon(s, pal['marble_hi'], [(x, base - 19), (cx, base - 26), (x + w, base - 19)])
        pygame.draw.circle(s, pal['glow'], (cx, base - 13), 2)
        pygame.draw.line(s, pal['gold'], (x + 4, base - 20), (x + w - 5, base - 20), 1)

    @staticmethod
    def _marble_arches(s, cx, base, w, pal):
        x = cx - w // 2
        pygame.draw.rect(s, pal['marble'], (x, base - 5, w, 5))
        for off in (2, w // 2 + 1):
            ax = x + off
            pygame.draw.rect(s, pal['marble_hi'], (ax, base - 16, 4, 11))
            pygame.draw.arc(s, pal['marble_hi'], (ax - 2, base - 16, 10, 10), math.pi, 2 * math.pi, 1)
        pygame.draw.line(s, pal['glow'], (x + 3, base - 6), (x + w - 4, base - 6), 1)

    @staticmethod
    def _small_bridge_complex(s, cx, base, w, pal):
        x = cx - w // 2
        pygame.draw.rect(s, pal['marble'], (x, base - 8, w, 4))
        pygame.draw.line(s, pal['glow'], (x + 2, base - 7), (x + w - 3, base - 7), 1)
        pygame.draw.line(s, pal['accent'], (x + 4, base - 4), (x + 4, base + 3), 1)
        pygame.draw.line(s, pal['accent'], (x + w - 5, base - 4), (x + w - 5, base + 3), 1)
        pygame.draw.line(s, pal['gold'], (x + 2, base - 1), (x + 8, base - 1), 1)
        pygame.draw.line(s, pal['gold'], (x + w - 9, base - 1), (x + w - 3, base - 1), 1)

    @staticmethod
    def _sky_docks(s, cx, base, w, pal):
        x = cx - w // 2
        pygame.draw.rect(s, pal['marble'], (x + 2, base - 8, w - 4, 6))
        pygame.draw.line(s, pal['glow'], (x + 3, base - 7), (x + w - 4, base - 7), 1)
        pygame.draw.line(s, pal['accent'], (x + w // 2, base - 16), (x + w // 2, base - 2), 1)
        pygame.draw.rect(s, pal['glow_soft'], (x + w // 2 - 2, base - 16, 5, 2))
        pygame.draw.line(s, pal['gold'], (x + 4, base - 3), (x + w - 5, base - 3), 1)

    @staticmethod
    def _dock_tower(s, cx, base, w, pal):
        x = cx - w // 2
        pygame.draw.rect(s, pal['marble'], (x + 8, base - 22, w - 16, 22))
        pygame.draw.line(s, pal['marble_hi'], (cx, base - 22), (cx, base - 3), 1)
        pygame.draw.rect(s, pal['glow'], (cx - 2, base - 15, 5, 2))
        pygame.draw.rect(s, pal['marble'], (x, base - 6, w, 5))
        pygame.draw.line(s, pal['gold'], (x + 2, base - 7), (x + w - 3, base - 7), 1)

    @staticmethod
    def _celestial_bridge(s, x, y, w, accent):
        pygame.draw.rect(s, (208, 221, 232), (x, y, w, 4))
        pygame.draw.line(s, accent, (x + 2, y + 1), (x + w - 3, y + 1), 1)
        pygame.draw.line(s, (147, 172, 196), (x + 4, y + 4), (x + 4, y + 11), 1)
        pygame.draw.line(s, (147, 172, 196), (x + w - 5, y + 4), (x + w - 5, y + 11), 1)

    @staticmethod
    def _celestial_rune(s, x, y, pal):
        pygame.draw.line(s, pal['glow'], (x, y), (x + 4, y), 1)
        pygame.draw.line(s, pal['glow_soft'], (x + 2, y - 2), (x + 2, y + 2), 1)
        pygame.draw.rect(s, pal['gold'], (x + 1, y + 1, 2, 1))

    # ----------------------------- overlay -----------------------------
    def _overlay_harmony(self, surf, frame, climate, night):
        if self.biome != 'ilhas_celestes':
            return super()._overlay_harmony(surf, frame, climate, night)

        # névoa aérea suave e profundidade cinematográfica
        haze_base = 14 if night < 0.35 else 20
        for y, a in ((265, haze_base), (308, haze_base - 3), (352, haze_base - 6)):
            yy = y + int(math.sin(frame * 0.01 + y * 0.03) * 2)
            pygame.draw.line(surf, (170, 228, 232, a), (0, yy), (WIDTH, yy), 1)
            pygame.draw.line(surf, (112, 196, 220, max(4, a - 8)), (0, yy + 5), (WIDTH, yy + 5), 1)

        # iluminação inteligente noturna nos monumentos/ilhas
        if night > 0.22:
            for i in range(8 if self.visual_quality else 4):
                xx = (22 + i * 54 + frame // 5) % WIDTH
                yy = 260 + (i % 4) * 19
                c = (140, 247, 222, 34) if i % 2 == 0 else (137, 226, 255, 32)
                pygame.draw.rect(surf, c, (xx, yy, 3, 2))

        # tráfego aéreo: aeronaves celestiais em duas camadas e três modelos
        count = 5 if self.visual_quality else 3
        for i in range(count):
            direction = 1 if i % 3 != 1 else -1
            speed = (0.42, 0.61, 0.86, 0.54, 0.73)[i % 5]
            x = int((i * 133 + frame * speed * direction) % (WIDTH + 80)) - 40
            y = 215 + i * 28 + int(math.sin(frame * 0.025 + i * 1.4) * 4)
            style = (i + frame // 90) % 3
            phase = (frame // (11 + i % 2 * 2) + i) % 2
            sprite = self._cel_air_flip[(style, phase)] if direction < 0 else self._cel_air[(style, phase)]
            surf.blit(sprite, (x, y))
            exhaust_x = x - 1 if direction > 0 else x + 29
            trail = ((126, 244, 255, 76), (162, 255, 228, 66), (249, 231, 185, 52))[style]
            for j in range(3):
                off = (frame // 4 + j * 3 + i * 2) % 10
                pygame.draw.line(surf, trail, (exhaust_x - direction * off, y + 8 + j),
                                 (exhaust_x - direction * (off + 3), y + 8 + j), 1)

        # sementes/pólen brilhante orgânico estilo Avatar
        particle_count = 9 if self.visual_quality else 5
        for i in range(particle_count):
            x = int((i * 71 - frame * 0.24) % (WIDTH + 10)) - 5
            y = 200 + (i * 41 + frame // 6) % 150
            col = (189, 241, 222, 66) if i % 3 else (245, 227, 182, 62)
            pygame.draw.rect(surf, col, (x, y, 2, 1))
        if night > 0.30:
            for i in range(6 if self.visual_quality else 3):
                x = int((i * 91 + frame * 0.22) % WIDTH)
                y = 226 + (i * 35) % 105
                pygame.draw.circle(surf, (136, 248, 213, 64), (x, y), 1)

        # clima reativo sem exageros
        if climate in ('brisa_celeste', 'tempestade_vento'):
            for i in range(5 if self.visual_quality else 2):
                x = int((i * 101 - frame * 1.05) % (WIDTH + 10)) - 5
                y = 218 + (i * 42 + frame // 3) % 92
                pygame.draw.line(surf, (226, 247, 247, 40), (x, y), (x + 5, y), 1)
                pygame.draw.line(surf, (158, 244, 227, 22), (x + 1, y + 1), (x + 6, y + 1), 1)
