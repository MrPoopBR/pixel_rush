"""Pixel Rush v3.168.0 — passe fino premium nos demais biomas.

Escopo desta versão:
- aplicar refinamento de nível premium aos biomas restantes;
- melhorar profundidade, encaixe, decoração e leitura do chão;
- manter gameplay, física, obstáculos e sistemas intactos.
"""
from __future__ import annotations
import math
import random
import pygame
from pixelrush_biomes2_v3167 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, WIDTH


class ModularBiomeScene(Previous):
    REFINED_BIOMES = ('neve', 'deserto', 'floresta', 'vulcao', 'ilhas_celestes')

    def __init__(self, biome):
        super().__init__(biome)
        if biome in self.REFINED_BIOMES:
            self._premium_pass_remaining_biomes()
            if hasattr(self, '_map_cache'):
                self._map_cache.clear()
            if hasattr(self, '_composites'):
                self._composites.clear()

    # ------------------------- master pass -------------------------
    def _premium_pass_remaining_biomes(self):
        for layer, chunks in self._layers.items():
            for idx, surf in enumerate(chunks):
                self._seal_chunk_edges(surf, layer)
                if layer == 'far':
                    self._far_ultra_polish(surf, idx)
                elif layer == 'mid':
                    self._mid_ultra_polish(surf, idx)
                else:
                    self._near_ultra_polish(surf, idx)

    def _far_ultra_polish(self, surf, idx):
        biome = self.biome
        if biome == 'neve':
            self._snow_far_ultra(surf, idx)
        elif biome == 'deserto':
            self._desert_far_ultra(surf, idx)
        elif biome == 'floresta':
            self._forest_far_ultra(surf, idx)
        elif biome == 'vulcao':
            self._volcano_far_ultra(surf, idx)
        elif biome == 'ilhas_celestes':
            self._islands_far_ultra(surf, idx)

    def _mid_ultra_polish(self, surf, idx):
        biome = self.biome
        if biome == 'neve':
            self._snow_mid_ultra(surf, idx)
        elif biome == 'deserto':
            self._desert_mid_ultra(surf, idx)
        elif biome == 'floresta':
            self._forest_mid_ultra(surf, idx)
        elif biome == 'vulcao':
            self._volcano_mid_ultra(surf, idx)
        elif biome == 'ilhas_celestes':
            self._islands_mid_ultra(surf, idx)

    def _near_ultra_polish(self, surf, idx):
        biome = self.biome
        if biome == 'neve':
            self._snow_near_ultra(surf, idx)
        elif biome == 'deserto':
            self._desert_near_ultra(surf, idx)
        elif biome == 'floresta':
            self._forest_near_ultra(surf, idx)
        elif biome == 'vulcao':
            self._volcano_near_ultra(surf, idx)
        elif biome == 'ilhas_celestes':
            self._islands_near_ultra(surf, idx)

    # ------------------------- snow biome -------------------------
    def _snow_far_ultra(self, surf, idx):
        seal = self.PALETTE['neve']['seal']
        shade = self.PALETTE['neve']['shade']
        peaks = [(12, 198, 44), (86, 194, 58), (152, 200, 38)] if idx % 2 == 0 else [(28, 200, 36), (94, 193, 62), (170, 198, 34)]
        for x, base, w in peaks:
            h = 12 + w // 4
            pygame.draw.polygon(surf, (123, 161, 197), [(x, base), (x + w//2, base - h), (x + w, base)])
            pygame.draw.polygon(surf, (154, 192, 224), [(x + 2, base - 1), (x + w//2, base - h + 4), (x + w - 2, base - 1)])
            pygame.draw.line(surf, seal, (x + w//2 - 5, base - h + 6), (x + w//2 + 6, base - h + 3), 1)
        for x in range(18, LW, 52):
            pygame.draw.line(surf, (219, 240, 249, 28), (x, 154), (x + 3, 188), 1)
        pygame.draw.rect(surf, (*shade, 22), (0, 204, LW, 9))
        pygame.draw.line(surf, seal, (0, 204), (LW - 1, 204), 1)

    def _snow_mid_ultra(self, surf, idx):
        seal = self.PALETTE['neve']['seal']
        shade = self.PALETTE['neve']['shade']
        groups = [(18, 210, 32), (62, 208, 24), (168, 211, 26)] if idx % 2 == 0 else [(28, 209, 24), (84, 210, 34), (176, 208, 22)]
        for x, base, w in groups:
            self._snow_hut(surf, x, base, w)
        if idx % 3 != 1:
            self._snow_fence_strip(surf, 114, 212, 38, seal, shade)
        for x in range(14, LW - 12, 46):
            pygame.draw.line(surf, (204, 230, 244, 36), (x, 214), (x + 9, 214), 1)

    def _snow_near_ultra(self, surf, idx):
        for x in (10, 24, 34, LW - 40, LW - 28, LW - 14):
            y = 241 + ((x + idx) % 2)
            pygame.draw.line(surf, (246, 252, 255), (x, 248), (x + 2, y), 1)
            pygame.draw.line(surf, (198, 228, 244), (x + 2, y), (x + 5, y - 1), 1)
        snowbank = pygame.Surface((LW, 13), pygame.SRCALPHA)
        pygame.draw.rect(snowbank, (228, 241, 249, 28), (0, 0, LW, 13))
        surf.blit(snowbank, (0, 226))
        pygame.draw.line(surf, (255, 255, 255), (0, 228), (LW - 1, 228), 1)

    def _snow_hut(self, surf, x, base, w):
        body_h = 10 + w // 6
        pygame.draw.rect(surf, (108, 138, 176), (x, base - body_h, w, body_h))
        pygame.draw.polygon(surf, (88, 111, 147), [(x - 2, base - body_h), (x + w // 2, base - body_h - 7), (x + w + 2, base - body_h)])
        pygame.draw.line(surf, (232, 246, 255), (x + 2, base - body_h + 2), (x + w - 3, base - body_h + 2), 1)
        for px in range(x + 4, x + w - 5, 6):
            pygame.draw.rect(surf, (224, 242, 250), (px, base - body_h + 5, 2, 2))

    def _snow_fence_strip(self, surf, x, y, w, seal, shade):
        for px in range(x, x + w, 6):
            pygame.draw.line(surf, shade, (px, y), (px, y - 7), 1)
        pygame.draw.line(surf, seal, (x, y - 5), (x + w, y - 5), 1)

    # ------------------------- desert biome -------------------------
    def _desert_far_ultra(self, surf, idx):
        seal = self.PALETTE['deserto']['seal']
        mesas = [(10, 202, 44), (82, 198, 58), (168, 204, 34)] if idx % 2 == 0 else [(18, 200, 36), (90, 196, 64), (180, 202, 30)]
        for x, base, w in mesas:
            self._mesa_shape(surf, x, base, w)
        for x in range(0, LW, 32):
            y = 210 + ((x + idx * 5) % 5)
            pygame.draw.arc(surf, (198, 146, 93), (x, y - 8, 26, 8), math.radians(180), math.radians(360), 1)
        pygame.draw.line(surf, seal, (0, 208), (LW - 1, 208), 1)

    def _desert_mid_ultra(self, surf, idx):
        if idx % 3 == 0:
            self._market_awning(surf, 20, 210, 24)
            self._market_awning(surf, 176, 212, 20)
        else:
            self._ruin_column(surf, 28, 213, 13)
            self._ruin_column(surf, 188, 212, 11)
        for x in range(60, 150, 24):
            pygame.draw.line(surf, (224, 183, 117), (x, 214), (x + 8, 214), 1)
        pygame.draw.line(surf, (176, 116, 74), (0, 214), (LW - 1, 214), 1)

    def _desert_near_ultra(self, surf, idx):
        for x in (12, 22, 34, LW - 42, LW - 26, LW - 12):
            pygame.draw.arc(surf, (230, 187, 120), (x, 242, 10, 4), math.radians(180), math.radians(360), 1)
        for x in (16, 28, LW - 32):
            pygame.draw.line(surf, (157, 114, 68), (x, 248), (x + 2, 242), 1)
            pygame.draw.line(surf, (214, 171, 111), (x + 2, 242), (x + 4, 246), 1)
        veil = pygame.Surface((LW, 11), pygame.SRCALPHA)
        pygame.draw.rect(veil, (243, 200, 128, 18), (0, 0, LW, 11))
        surf.blit(veil, (0, 227))

    def _mesa_shape(self, surf, x, base, w):
        dark = (136, 97, 62)
        mid = (173, 124, 79)
        top = (233, 187, 121)
        pygame.draw.polygon(surf, dark, [(x, base), (x + 6, base - 12), (x + w - 8, base - 13), (x + w, base)])
        pygame.draw.polygon(surf, mid, [(x + 2, base - 1), (x + 8, base - 10), (x + w - 10, base - 11), (x + w - 2, base - 1)])
        pygame.draw.line(surf, top, (x + 7, base - 10), (x + w - 11, base - 10), 1)

    def _market_awning(self, surf, x, base, w):
        pygame.draw.line(surf, (126, 87, 60), (x + 4, base), (x + 4, base - 10), 1)
        pygame.draw.line(surf, (126, 87, 60), (x + w - 4, base), (x + w - 4, base - 10), 1)
        pygame.draw.polygon(surf, (188, 99, 80), [(x, base - 9), (x + w // 2, base - 15), (x + w, base - 9)])
        pygame.draw.line(surf, (243, 214, 168), (x + 2, base - 10), (x + w - 2, base - 10), 1)

    def _ruin_column(self, surf, x, base, h):
        pygame.draw.rect(surf, (144, 107, 77), (x, base - h, 6, h))
        pygame.draw.line(surf, (234, 200, 141), (x, base - h + 3), (x + 5, base - h + 3), 1)
        pygame.draw.line(surf, (170, 125, 90), (x + 2, base - h + 1), (x + 2, base - 2), 1)

    # ------------------------- forest biome -------------------------
    def _forest_far_ultra(self, surf, idx):
        tones = [(44, 83, 55), (54, 96, 62), (70, 118, 77)]
        clusters = [(8, 205, 34), (74, 201, 42), (152, 206, 30)] if idx % 2 == 0 else [(18, 206, 28), (86, 202, 44), (168, 204, 26)]
        for i, (x, base, w) in enumerate(clusters):
            self._forest_canopy_cluster(surf, x, base, w, tones[i % len(tones)])
        haze = pygame.Surface((LW, 44), pygame.SRCALPHA)
        for y in range(44):
            pygame.draw.line(haze, (88, 133, 92, 8 + y // 9), (0, y), (LW - 1, y), 1)
        surf.blit(haze, (0, 176))

    def _forest_mid_ultra(self, surf, idx):
        stems = [(18, 214, 19), (66, 212, 24), (176, 214, 17)] if idx % 2 == 0 else [(26, 214, 18), (90, 211, 28), (182, 213, 16)]
        for x, base, h in stems:
            self._forest_tall_tree(surf, x, base, h)
        for x in (44, 138, 204):
            self._forest_vine(surf, x + (idx % 3), 192 + (x % 4), 20)
        pygame.draw.line(surf, (84, 126, 79), (0, 214), (LW - 1, 214), 1)

    def _forest_near_ultra(self, surf, idx):
        left_clusters = [8, 18, 30]
        right_clusters = [LW - 38, LW - 28, LW - 16]
        for x in left_clusters + right_clusters:
            self._fern_tuft(surf, x, 248, 1 + ((x + idx) % 2))
        for x in (12, 24, 36, LW - 40, LW - 30):
            self._forest_leaf_bush(surf, x, 243)
        soil = pygame.Surface((LW, 10), pygame.SRCALPHA)
        pygame.draw.rect(soil, (44, 69, 41, 24), (0, 0, LW, 10))
        surf.blit(soil, (0, 228))
        pygame.draw.line(surf, (124, 179, 101), (0, 229), (LW - 1, 229), 1)

    def _forest_canopy_cluster(self, surf, x, base, w, color):
        pygame.draw.rect(surf, (62, 88, 56), (x + w // 2 - 2, base - 18, 4, 18))
        lumps = [(x, base - 18, w // 2), (x + w // 4, base - 26, w // 2), (x + w // 2, base - 18, w // 2)]
        for lx, ly, lw in lumps:
            pygame.draw.ellipse(surf, color, (lx, ly, lw, 16))
        pygame.draw.line(surf, (136, 192, 111), (x + 6, base - 12), (x + w - 8, base - 12), 1)

    def _forest_tall_tree(self, surf, x, base, h):
        trunk = (72, 88, 60)
        leaf = (71, 118, 70)
        leaf2 = (102, 152, 91)
        pygame.draw.rect(surf, trunk, (x + 7, base - h, 5, h))
        pygame.draw.ellipse(surf, leaf, (x, base - h - 4, 20, 13))
        pygame.draw.ellipse(surf, leaf2, (x + 2, base - h - 10, 16, 10))
        pygame.draw.line(surf, (145, 196, 122), (x + 4, base - h - 2), (x + 16, base - h - 5), 1)

    def _forest_vine(self, surf, x, y, h):
        for n in range(h):
            surf.set_at((max(0, min(LW - 1, x + int(math.sin(n * 0.35) * 1.5))), y + n), (66, 108, 61))
        pygame.draw.line(surf, (111, 178, 104), (x - 1, y + 4), (x + 2, y + 6), 1)
        pygame.draw.line(surf, (111, 178, 104), (x - 2, y + 10), (x + 1, y + 12), 1)

    def _fern_tuft(self, surf, x, base, phase):
        for i, h in enumerate((8, 11, 9, 6)):
            pygame.draw.line(surf, (90, 148, 79), (x + i * 2, base), (x + i * 2 + (-1 if i < 2 else 1), base - h + phase), 1)
            pygame.draw.line(surf, (125, 186, 105), (x + i * 2 + 1, base - 3), (x + i * 2 + 2, base - h // 2), 1)

    def _forest_leaf_bush(self, surf, x, y):
        pygame.draw.ellipse(surf, (68, 115, 66), (x, y, 9, 5))
        pygame.draw.ellipse(surf, (90, 145, 82), (x + 2, y - 2, 7, 4))

    # ------------------------- volcano biome -------------------------
    def _volcano_far_ultra(self, surf, idx):
        peaks = [(16, 205, 48), (88, 198, 64), (170, 204, 34)] if idx % 2 == 0 else [(28, 202, 40), (94, 196, 58), (176, 205, 32)]
        for x, base, w in peaks:
            self._basalt_peak(surf, x, base, w)
        for x in range(20, LW, 60):
            y = 188 + ((x + idx * 3) % 6)
            pygame.draw.line(surf, (164, 95, 84, 28), (x, y), (x + 4, y - 8), 1)
        haze = pygame.Surface((LW, 52), pygame.SRCALPHA)
        for y in range(52):
            pygame.draw.line(haze, (146, 92, 88, 7 + y // 8), (0, y), (LW - 1, y), 1)
        surf.blit(haze, (0, 168))

    def _volcano_mid_ultra(self, surf, idx):
        formations = [(20, 213, 18), (74, 212, 26), (178, 213, 16)] if idx % 2 == 0 else [(28, 212, 15), (98, 211, 21), (182, 213, 18)]
        for x, base, h in formations:
            self._volcano_column_mini(surf, x, base, h)
        if idx % 3 == 0:
            self._lava_channel(surf, 122, 214, 32)
        pygame.draw.line(surf, (112, 61, 60), (0, 214), (LW - 1, 214), 1)

    def _volcano_near_ultra(self, surf, idx):
        for x in (10, 22, 32, LW - 38, LW - 24, LW - 12):
            pygame.draw.polygon(surf, (68, 50, 56), [(x, 248), (x + 3, 242), (x + 7, 248)])
        for x in (16, 28, LW - 30):
            pygame.draw.line(surf, (255, 137, 70), (x, 244), (x + 4, 244), 1)
            pygame.draw.line(surf, (255, 202, 116), (x + 1, 245), (x + 3, 245), 1)
        veil = pygame.Surface((LW, 11), pygame.SRCALPHA)
        pygame.draw.rect(veil, (72, 44, 47, 24), (0, 0, LW, 11))
        surf.blit(veil, (0, 228))

    def _basalt_peak(self, surf, x, base, w):
        pygame.draw.polygon(surf, (70, 55, 60), [(x, base), (x + w // 3, base - 16), (x + 2 * w // 3, base - 21), (x + w, base)])
        pygame.draw.polygon(surf, (92, 70, 75), [(x + 2, base - 1), (x + w // 3 + 1, base - 13), (x + 2 * w // 3 - 2, base - 17), (x + w - 2, base - 1)])
        pygame.draw.line(surf, (255, 145, 72), (x + w // 2 - 2, base - 13), (x + w // 2 + 4, base - 16), 1)

    def _volcano_column_mini(self, surf, x, base, h):
        pygame.draw.rect(surf, (74, 58, 63), (x, base - h, 8, h))
        pygame.draw.line(surf, (104, 82, 86), (x + 2, base - h + 1), (x + 2, base - 2), 1)
        pygame.draw.line(surf, (255, 148, 72), (x + 1, base - h + 4), (x + 5, base - h + 4), 1)

    def _lava_channel(self, surf, x, y, w):
        pygame.draw.line(surf, (255, 136, 67), (x, y), (x + w, y), 2)
        pygame.draw.line(surf, (255, 208, 114), (x + 4, y), (x + w - 4, y), 1)

    # ------------------------- sky islands biome -------------------------
    def _islands_far_ultra(self, surf, idx):
        clusters = [(10, 178, 58), (90, 170, 44), (164, 182, 40)] if idx % 2 == 0 else [(22, 180, 50), (104, 172, 42), (176, 184, 32)]
        for x, y, w in clusters:
            self._floating_archipelago(surf, x, y, w)
        mist = pygame.Surface((LW, 58), pygame.SRCALPHA)
        for y in range(58):
            pygame.draw.line(mist, (188, 221, 232, 6 + y // 10), (0, y), (LW - 1, y), 1)
        surf.blit(mist, (0, 164))

    def _islands_mid_ultra(self, surf, idx):
        monuments = [(20, 213, 26), (88, 211, 22), (176, 212, 24)] if idx % 2 == 0 else [(30, 213, 20), (104, 210, 28), (182, 212, 19)]
        for x, base, w in monuments:
            self._marble_shrine(surf, x, base, w)
        if idx % 3 != 1:
            self._hanging_bridge(surf, 126, 197, 36)
        pygame.draw.line(surf, (122, 166, 194), (0, 214), (LW - 1, 214), 1)

    def _islands_near_ultra(self, surf, idx):
        for x in (12, 24, 34, LW - 40, LW - 28, LW - 14):
            self._glow_plant(surf, x, 246, idx)
        for x in (18, 30, LW - 34):
            pygame.draw.line(surf, (188, 236, 220), (x, 248), (x + 3, 242), 1)
            pygame.draw.line(surf, (133, 211, 178), (x + 3, 242), (x + 5, 247), 1)
        veil = pygame.Surface((LW, 11), pygame.SRCALPHA)
        pygame.draw.rect(veil, (176, 208, 224, 20), (0, 0, LW, 11))
        surf.blit(veil, (0, 228))
        pygame.draw.line(surf, (220, 249, 241), (0, 229), (LW - 1, 229), 1)

    def _floating_archipelago(self, surf, x, y, w):
        dark = (111, 143, 168)
        top = (203, 224, 230)
        glow = (160, 232, 198)
        pygame.draw.polygon(surf, dark, [(x, y + 10), (x + 8, y + 2), (x + w - 10, y), (x + w, y + 12), (x + w - 6, y + 16), (x + 10, y + 15)])
        pygame.draw.line(surf, top, (x + 8, y + 4), (x + w - 11, y + 3), 1)
        pygame.draw.line(surf, glow, (x + w // 2 - 5, y + 14), (x + w // 2, y + 23), 1)
        pygame.draw.line(surf, glow, (x + w // 2 + 2, y + 14), (x + w // 2 + 6, y + 22), 1)

    def _marble_shrine(self, surf, x, base, w):
        pygame.draw.rect(surf, (185, 203, 214), (x + 5, base - 15, w - 10, 11))
        pygame.draw.rect(surf, (211, 226, 234), (x + 3, base - 20, w - 6, 5))
        pygame.draw.line(surf, (164, 232, 198), (x + 8, base - 18), (x + w - 8, base - 18), 1)
        for px in range(x + 7, x + w - 7, 8):
            pygame.draw.line(surf, (129, 161, 182), (px, base - 15), (px, base - 5), 1)

    def _hanging_bridge(self, surf, x, y, w):
        pygame.draw.line(surf, (173, 196, 209), (x, y), (x + w, y), 1)
        for px in range(x + 4, x + w, 6):
            pygame.draw.line(surf, (132, 162, 182), (px, y), (px, y + 5), 1)
        pygame.draw.arc(surf, (167, 235, 204), (x + 2, y - 3, w - 4, 10), math.radians(0), math.radians(180), 1)

    def _glow_plant(self, surf, x, base, idx):
        stem = (122, 177, 155)
        glow = (156, 239, 194)
        blue = (120, 194, 226)
        pygame.draw.line(surf, stem, (x + 2, base), (x + 2, base - 6), 1)
        pygame.draw.line(surf, stem, (x + 2, base - 3), (x, base - 5), 1)
        pygame.draw.line(surf, stem, (x + 2, base - 4), (x + 5, base - 6), 1)
        col = glow if (x + idx) % 2 == 0 else blue
        pygame.draw.ellipse(surf, col, (x, base - 9, 6, 4))

    # ------------------------- animated harmony -------------------------
    def _overlay_harmony(self, surf, frame, climate, night):
        super()._overlay_harmony(surf, frame, climate, night)
        if self.biome not in self.REFINED_BIOMES:
            return
        low = not bool(getattr(self, 'visual_quality', 1))
        count = 3 if low else 5
        if self.biome == 'neve':
            for i in range(count):
                x = int((frame * 0.42 + i * 77) % (WIDTH + 10)) - 5
                y = 236 + (i * 21 + frame // 5) % 150
                pygame.draw.line(surf, (246, 252, 255, 40), (x, y), (x + 1, y + 3), 1)
        elif self.biome == 'deserto':
            for i in range(count):
                x = int((i * 95 - frame * 0.26) % (WIDTH + 24)) - 12
                y = 404 + (i * 7) % 15
                pygame.draw.line(surf, (245, 214, 151, 18), (x, y), (min(WIDTH, x + 18), y), 1)
                pygame.draw.line(surf, (234, 183, 121, 12), (x + 4, y + 2), (min(WIDTH, x + 12), y + 2), 1)
        elif self.biome == 'floresta':
            for i in range(count):
                x = int((i * 73 + frame * 0.16) % (WIDTH - 20)) + 8
                y = 280 + (i * 39) % 140
                col = (191, 236, 132, 34) if night > 0.25 else (138, 210, 126, 20)
                pygame.draw.rect(surf, col, (x, y, 2, 2))
        elif self.biome == 'vulcao':
            for i in range(count):
                x = int((i * 81 + frame * 0.23) % (WIDTH - 12)) + 4
                y = 292 + (i * 35 + frame // 4) % 120
                pygame.draw.line(surf, (255, 155, 71, 34), (x, y), (x + 1, y - 2), 1)
                if not low and i % 2 == 0:
                    pygame.draw.line(surf, (255, 214, 114, 24), (x + 1, y - 1), (x + 2, y - 3), 1)
        elif self.biome == 'ilhas_celestes':
            for i in range(count):
                x = int((i * 89 + frame * 0.18) % (WIDTH - 20)) + 6
                y = 255 + (i * 31) % 150
                pygame.draw.line(surf, (184, 236, 220, 28), (x, y), (x + 5, y - 3), 1)
                pygame.draw.line(surf, (122, 195, 224, 18), (x + 2, y + 1), (x + 6, y - 1), 1)
