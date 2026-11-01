"""v3.159 — Ilhas Celestiais: segunda rodada de polimento premium.

Escopo restrito ao bioma `ilhas_celestes`.
Aprimora microdetalhes, vegetação, acabamento marmóreo e sensação de vida,
sem alterar jogabilidade, hitboxes ou os demais biomas.
"""
from __future__ import annotations
import math
import random
import pygame
from pixelrush_biomes2_v3158 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, LH, WIDTH


class ModularBiomeScene(Previous):
    def __init__(self, biome):
        super().__init__(biome)
        if biome == 'ilhas_celestes':
            self._polish_celestial_layers()
            self._map_cache.clear()

    def _polish_celestial_layers(self):
        for i, surf in enumerate(self._layers['far']):
            self._polish_far_chunk(surf, i, self._district_name(i))
        for i, surf in enumerate(self._layers['mid']):
            self._polish_mid_chunk(surf, i, self._district_name(i + 2))
        for i, surf in enumerate(self._layers['near']):
            self._polish_near_chunk(surf, i, self._district_name(i + 4))

    # ---------------- far / mid / near polish ----------------
    def _polish_far_chunk(self, surf, index, district):
        rng = random.Random(321900 + index * 59)
        pal = self._district_palette(district)
        # brilho discreto sob ilhas distantes para maior leitura/vida.
        for x in range(14 + (index % 3) * 3, LW - 8, 52):
            yy = 160 + ((x + index * 7) % 19)
            pygame.draw.line(surf, (*pal['glow'], 26), (x, yy), (x + 13, yy), 1)
            pygame.draw.line(surf, (*pal['glow_soft'], 14), (x + 1, yy + 1), (x + 10, yy + 1), 1)
        # pequenas faixas de neblina entre camadas para profundidade.
        for y, a in ((171, 18), (181, 12)):
            pygame.draw.line(surf, (188, 231, 236, a), (0, y), (LW - 1, y), 1)
        # luzes arquitetônicas minúsculas no horizonte.
        for _ in range(4):
            x = rng.randrange(20, LW - 20)
            y = rng.randrange(104, 150)
            pygame.draw.rect(surf, (*pal['glow_soft'], 42), (x, y, 2, 1))

    def _polish_mid_chunk(self, surf, index, district):
        rng = random.Random(322700 + index * 61)
        pal = self._district_palette(district)
        # micro vegetação/arbustos brilhantes no topo das ilhas médias.
        top_bands = [140, 147, 151, 158, 163]
        plant_cols = [pal['grass'], pal['glow_soft'], (236, 204, 222)]
        for y in top_bands:
            if rng.random() < 0.8:
                x = rng.randrange(10, LW - 18)
                self._micro_plant(surf, x, y, plant_cols[rng.randrange(0, len(plant_cols))])
            if rng.random() < 0.35:
                x = rng.randrange(12, LW - 20)
                self._micro_shrub(surf, x, y + 1, pal)
        # pingos/lianas pendentes sob algumas ilhas.
        for _ in range(3):
            x = rng.randrange(18, LW - 18)
            y = rng.randrange(170, 202)
            pygame.draw.line(surf, (104, 185, 151, 120), (x, y - 8), (x, y), 1)
            pygame.draw.rect(surf, (171, 241, 197, 120), (x, y, 1, 1))
        # filetes de ouro/mármore em monumentos para acabamento.
        for x in range(20, LW - 22, 37):
            yy = 131 + ((x + index) % 27)
            pygame.draw.line(surf, (*pal['gold'], 85), (x, yy), (x + 6, yy), 1)

    def _polish_near_chunk(self, surf, index, district):
        rng = random.Random(323500 + index * 67)
        pal = self._district_palette(district)
        # reforço da pista premium com pequenas inlays e reflexos.
        for x in range(10 + (index % 2) * 2, LW - 8, 24):
            pygame.draw.line(surf, pal['glow_soft'], (x, 224), (x + 5, 224), 1)
            if x % 48 == 10:
                pygame.draw.line(surf, pal['gold'], (x + 2, 236), (x + 2, 242), 1)
        # pequenas plantas e flores apenas nas ilhas laterais, não na pista.
        for base_x in (14, 170):
            self._micro_shrub(surf, base_x + rng.randrange(3, 9), 176 + rng.randrange(-2, 2), pal)
            self._micro_plant(surf, base_x + rng.randrange(10, 18), 174 + rng.randrange(-1, 2), pal['glow_soft'])
        # pingos nas cachoeiras / espuma sutil.
        for x in range(20, LW - 20, 58):
            if rng.random() < 0.5:
                pygame.draw.rect(surf, (*pal['glow_soft'], 140), (x, 212 + (x % 5), 1, 2))
                pygame.draw.rect(surf, (*pal['glow'], 120), (x + 2, 216 + (x % 4), 1, 1))
        # detalhes extras nos suportes inferiores para dar acabamento.
        for x in (14, 46, 81, 116, 154, 191, 214):
            pygame.draw.rect(surf, pal['accent'], (x + 1, 237, 3, 1))
            pygame.draw.line(surf, pal['glow'], (x + 2, 244), (x + 2, 247), 1)
        # névoa azulada muito sutil na lâmina de água inferior.
        pygame.draw.line(surf, (193, 242, 247, 30), (0, 228), (LW - 1, 228), 1)

    @staticmethod
    def _micro_plant(surf, x, y, color):
        pygame.draw.line(surf, color, (x, y), (x + 1, y - 3), 1)
        pygame.draw.line(surf, color, (x + 1, y - 1), (x + 3, y - 4), 1)
        pygame.draw.line(surf, color, (x + 1, y - 2), (x - 1, y - 4), 1)

    @staticmethod
    def _micro_shrub(surf, x, y, pal):
        pygame.draw.rect(surf, pal['grass_dark'], (x, y - 1, 5, 2))
        pygame.draw.rect(surf, pal['grass'], (x + 1, y - 2, 3, 1))
        pygame.draw.rect(surf, pal['glow_soft'], (x + 2, y - 3, 1, 1))

    # ---------------- overlay polish ----------------
    def _overlay_harmony(self, surf, frame, climate, night):
        if self.biome != 'ilhas_celestes':
            return super()._overlay_harmony(surf, frame, climate, night)

        super()._overlay_harmony(surf, frame, climate, night)

        # fitas energéticas / aura suave no horizonte noturno.
        if night > 0.18:
            for i, yy in enumerate((248, 274, 301)):
                wav = 3 + i
                pts = []
                for x in range(0, WIDTH + 8, 8):
                    y = yy + int(math.sin((frame * 0.015) + x * 0.02 + i) * wav)
                    pts.append((x, y))
                pygame.draw.lines(surf, (116, 220, 248, 16 if i != 1 else 22), False, pts, 1)

        # sementes luminosas adicionais e vagalumes celestes para mais vida.
        extra = 5 if self.visual_quality else 3
        for i in range(extra):
            x = int((i * 127 + frame * 0.18) % WIDTH)
            y = 214 + (i * 31 + frame // 8) % 132
            col = (249, 228, 182, 64) if i % 2 == 0 else (169, 248, 218, 60)
            pygame.draw.rect(surf, col, (x, y, 2, 1))
            if night > 0.34:
                pygame.draw.circle(surf, (139, 255, 225, 52), (x + 1, y), 1)

        # pequenas criaturas voadoras bioluminescentes estilo Avatar.
        creature_count = 2 if self.visual_quality else 1
        for i in range(creature_count):
            x = int((i * 201 + frame * (0.65 + i * 0.17)) % (WIDTH + 20)) - 10
            y = 240 + i * 34 + int(math.sin(frame * 0.04 + i * 1.7) * 6)
            wing = (153, 244, 230, 58) if night > 0.24 else (200, 236, 228, 36)
            core = (238, 246, 245, 72) if night > 0.24 else (219, 232, 229, 42)
            pygame.draw.line(surf, wing, (x - 3, y), (x, y + 1), 1)
            pygame.draw.line(surf, wing, (x + 3, y), (x, y + 1), 1)
            pygame.draw.rect(surf, core, (x, y, 1, 1))

        # resposta de clima mais elegante.
        if climate == 'brisa_celeste':
            for i in range(3 if self.visual_quality else 2):
                x = int((i * 143 - frame * 0.9) % (WIDTH + 24)) - 12
                y = 228 + (i * 37 + frame // 4) % 90
                pygame.draw.line(surf, (222, 248, 244, 30), (x, y), (x + 7, y), 1)
        elif climate == 'tempestade_vento':
            for i in range(4 if self.visual_quality else 2):
                x = int((i * 117 - frame * 1.28) % (WIDTH + 30)) - 15
                y = 220 + (i * 41 + frame // 3) % 102
                pygame.draw.line(surf, (214, 244, 247, 38), (x, y), (x + 9, y), 1)
                pygame.draw.line(surf, (124, 230, 239, 22), (x + 1, y + 1), (x + 7, y + 1), 1)
