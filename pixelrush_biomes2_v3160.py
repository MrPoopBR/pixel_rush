"""v3.160 — Ilhas Celestiais: rodada final de polimento premium.

Escopo restrito ao bioma `ilhas_celestes`.
Refinamento final do cenário com foco em acabamento visual, variedade orgânica,
monumentos mais ricos, cachoeiras/brilhos melhores e sensação de bioma vivo,
sem alterar física, jogabilidade ou demais biomas.
"""
from __future__ import annotations
import math
import random
import pygame
from pixelrush_biomes2_v3159 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, WIDTH


class ModularBiomeScene(Previous):
    def __init__(self, biome):
        super().__init__(biome)
        if biome == 'ilhas_celestes':
            self._premium_pass_celestial_layers()
            self._map_cache.clear()

    def _premium_pass_celestial_layers(self):
        for i, surf in enumerate(self._layers['far']):
            self._premium_far_chunk(surf, i, self._district_name(i))
        for i, surf in enumerate(self._layers['mid']):
            self._premium_mid_chunk(surf, i, self._district_name(i + 2))
        for i, surf in enumerate(self._layers['near']):
            self._premium_near_chunk(surf, i, self._district_name(i + 4))

    # ---------------- premium pass per layer ----------------
    def _premium_far_chunk(self, surf, index, district):
        pal = self._district_palette(district)
        rng = random.Random(324900 + index * 79)
        # cristais / brilhos flutuantes muito discretos em camadas distantes.
        for _ in range(3):
            x = rng.randrange(24, LW - 24)
            y = rng.randrange(98, 148)
            self._tiny_crystal(surf, x, y, pal)
        # borda de luz sob algumas ilhas distantes para maior separação.
        for x in range(18 + (index % 2) * 7, LW - 20, 58):
            yy = 146 + ((x + index * 9) % 18)
            pygame.draw.line(surf, (*pal['glow'], 16), (x, yy), (x + 8, yy), 1)
        # filetes de névoa em ondas mais suaves no horizonte.
        for y, a in ((166, 10), (176, 8), (186, 6)):
            pts = []
            for x in range(0, LW + 6, 6):
                pts.append((x, y + int(math.sin(x * 0.06 + index) * 1.5)))
            pygame.draw.lines(surf, (194, 235, 239, a), False, pts, 1)

    def _premium_mid_chunk(self, surf, index, district):
        pal = self._district_palette(district)
        rng = random.Random(325700 + index * 83)
        # mais variedade de flora nas ilhas médias.
        for _ in range(5):
            x = rng.randrange(8, LW - 14)
            y = rng.choice((137, 143, 149, 154, 160, 166))
            kind = rng.randrange(4)
            if kind == 0:
                self._tuft_flora(surf, x, y, pal)
            elif kind == 1:
                self._flower_cluster(surf, x, y, pal)
            elif kind == 2:
                self._micro_plant(surf, x, y, pal['glow_soft'])
            else:
                self._leaf_bush(surf, x, y, pal)
        # pequenos frisos nos monumentos / plataformas de mármore.
        for x in range(14, LW - 16, 46):
            y = 128 + ((x + index * 3) % 29)
            pygame.draw.line(surf, (*pal['marble_hi'], 120), (x, y), (x + 4, y), 1)
            pygame.draw.line(surf, (*pal['gold'], 64), (x + 1, y + 1), (x + 3, y + 1), 1)
        # reforço nas cachoeiras com reflexo/espuma sutil.
        for x in range(20, LW - 24, 64):
            if rng.random() < 0.55:
                self._water_sparkles(surf, x, 173 + (x % 11), pal)
        # lianas / raízes pendentes organizadas.
        for _ in range(2):
            x = rng.randrange(18, LW - 18)
            y = rng.randrange(166, 190)
            pygame.draw.line(surf, (90, 169, 139, 110), (x, y - 10), (x, y), 1)
            pygame.draw.line(surf, (142, 210, 169, 94), (x + 1, y - 7), (x + 3, y - 2), 1)

    def _premium_near_chunk(self, surf, index, district):
        pal = self._district_palette(district)
        rng = random.Random(326500 + index * 89)
        # variações extras de flora nas ilhas laterais.
        for base_x in (10, 165):
            for off in (4, 10, 17):
                y = 173 + rng.randrange(-2, 3)
                kind = (base_x + off + index) % 4
                if kind == 0:
                    self._tuft_flora(surf, base_x + off, y, pal)
                elif kind == 1:
                    self._flower_cluster(surf, base_x + off, y, pal)
                elif kind == 2:
                    self._leaf_bush(surf, base_x + off, y, pal)
                else:
                    self._micro_plant(surf, base_x + off, y, pal['glow_soft'])
        # mais refinamento na pista premium sem colocar decoração jogável.
        for x in range(8, LW - 10, 32):
            pygame.draw.line(surf, pal['marble_hi'], (x, 221), (x + 3, 221), 1)
            pygame.draw.line(surf, pal['glow'], (x + 1, 247), (x + 4, 247), 1)
        # runas extras discretas.
        for x in range(24, LW - 18, 48):
            self._mini_rune(surf, x, 239, pal)
        # cristais pendentes minúsculos sob ilhas laterais.
        for x in (28, 197):
            self._hanging_crystal(surf, x + (index % 5), 205 + (x % 7), pal)
        # espuma e brilho reforçados nas quedas de água.
        for x in range(22, LW - 22, 57):
            if rng.random() < 0.6:
                self._water_sparkles(surf, x, 211 + (x % 5), pal)
        # reflexo ondulado no canal inferior.
        for x in range(0, LW, 18):
            pygame.draw.line(surf, (205, 242, 246, 20), (x, 229 + (x // 18) % 2), (x + 8, 229 + (x // 18) % 2), 1)

    # ---------------- small shape helpers ----------------
    @staticmethod
    def _tiny_crystal(surf, x, y, pal):
        pygame.draw.polygon(surf, (*pal['accent'], 96), [(x, y + 3), (x + 2, y), (x + 4, y + 3), (x + 2, y + 6)])
        pygame.draw.line(surf, (*pal['glow_soft'], 110), (x + 2, y + 1), (x + 2, y + 4), 1)

    def _tuft_flora(self, surf, x, y, pal):
        pygame.draw.line(surf, pal['grass'], (x, y), (x + 1, y - 4), 1)
        pygame.draw.line(surf, pal['grass'], (x + 2, y), (x + 2, y - 5), 1)
        pygame.draw.line(surf, pal['glow_soft'], (x + 1, y - 1), (x + 4, y - 4), 1)
        pygame.draw.line(surf, pal['grass_dark'], (x + 2, y - 1), (x - 1, y - 3), 1)

    @staticmethod
    def _flower_cluster(surf, x, y, pal):
        pygame.draw.line(surf, pal['grass_dark'], (x + 2, y), (x + 2, y - 3), 1)
        pygame.draw.rect(surf, pal['glow_soft'], (x + 1, y - 4, 3, 2))
        pygame.draw.rect(surf, (241, 209, 223), (x + 2, y - 5, 1, 1))

    @staticmethod
    def _leaf_bush(surf, x, y, pal):
        pygame.draw.rect(surf, pal['grass_dark'], (x, y - 1, 6, 2))
        pygame.draw.rect(surf, pal['grass'], (x + 1, y - 3, 4, 2))
        pygame.draw.rect(surf, pal['glow_soft'], (x + 2, y - 4, 2, 1))

    @staticmethod
    def _mini_rune(surf, x, y, pal):
        pygame.draw.line(surf, pal['gold'], (x, y), (x + 2, y), 1)
        pygame.draw.line(surf, pal['glow_soft'], (x + 1, y - 1), (x + 1, y + 1), 1)

    @staticmethod
    def _hanging_crystal(surf, x, y, pal):
        pygame.draw.line(surf, (140, 196, 180), (x, y - 4), (x, y), 1)
        pygame.draw.polygon(surf, pal['accent'], [(x - 1, y), (x, y + 2), (x + 1, y), (x, y + 3)])
        pygame.draw.rect(surf, pal['glow_soft'], (x, y + 1, 1, 1))

    @staticmethod
    def _water_sparkles(surf, x, y, pal):
        pygame.draw.rect(surf, (*pal['glow_soft'], 120), (x, y, 1, 2))
        pygame.draw.rect(surf, (*pal['glow'], 90), (x + 1, y + 2, 2, 1))
        pygame.draw.rect(surf, (245, 249, 251, 110), (x - 1, y + 4, 4, 1))

    # ---------------- overlay final polish ----------------
    def _overlay_harmony(self, surf, frame, climate, night):
        if self.biome != 'ilhas_celestes':
            return super()._overlay_harmony(surf, frame, climate, night)

        super()._overlay_harmony(surf, frame, climate, night)

        # camada extra de partículas orgânicas, bem leve.
        count = 6 if self.visual_quality else 3
        for i in range(count):
            x = int((i * 97 + frame * (0.16 + i * 0.01)) % WIDTH)
            y = 226 + ((i * 39 + frame // 10) % 122)
            c = (164, 248, 220, 46) if i % 2 else (247, 230, 190, 42)
            pygame.draw.rect(surf, c, (x, y, 1 + (i % 2), 1))

        # criaturas voadoras um pouco mais ricas.
        creature_count = 3 if self.visual_quality else 1
        for i in range(creature_count):
            x = int((i * 169 + frame * (0.54 + i * 0.12)) % (WIDTH + 24)) - 12
            y = 230 + i * 26 + int(math.sin(frame * 0.05 + i * 1.6) * (4 + i))
            wing = (142, 244, 227, 58) if night > 0.25 else (197, 235, 229, 34)
            body = (239, 246, 245, 68) if night > 0.25 else (220, 231, 229, 40)
            pygame.draw.line(surf, wing, (x - 4, y), (x - 1, y + 1), 1)
            pygame.draw.line(surf, wing, (x + 4, y), (x + 1, y + 1), 1)
            pygame.draw.line(surf, wing, (x - 2, y + 2), (x + 2, y + 2), 1)
            pygame.draw.rect(surf, body, (x, y + 1, 1, 1))

        # brilhos de cachoeira mais vivos à noite.
        if night > 0.28:
            for i in range(5 if self.visual_quality else 2):
                x = int((i * 83 + frame * 0.22) % WIDTH)
                y = 310 + (i * 27) % 82
                pygame.draw.line(surf, (121, 233, 255, 24), (x, y), (x + 7, y), 1)
                pygame.draw.line(surf, (196, 247, 255, 14), (x + 1, y + 1), (x + 5, y + 1), 1)

        # clima com pequenos detalhes adicionais.
        if climate == 'brisa_celeste':
            for i in range(2 if self.visual_quality else 1):
                x = int((i * 177 - frame * 0.8) % (WIDTH + 30)) - 15
                y = 240 + (i * 53 + frame // 5) % 88
                pygame.draw.line(surf, (232, 249, 247, 18), (x, y), (x + 10, y), 1)
        elif climate == 'tempestade_vento':
            for i in range(3 if self.visual_quality else 1):
                x = int((i * 141 - frame * 1.35) % (WIDTH + 34)) - 17
                y = 226 + (i * 44 + frame // 3) % 110
                pygame.draw.line(surf, (220, 245, 246, 18), (x, y), (x + 12, y), 1)
                pygame.draw.line(surf, (126, 227, 236, 14), (x + 2, y + 1), (x + 8, y + 1), 1)
