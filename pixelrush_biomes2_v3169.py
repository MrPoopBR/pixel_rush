"""Pixel Rush v3.169.0 — auditoria visual final e polimento global.

Aplica um passe extra sobre os biomas premium para:
- limpar sensação de emenda / corte entre chunks;
- empurrar decoração para laterais, preservando a pista mais legível;
- reforçar profundidade e acabamento visual sem mexer em gameplay.
"""
from __future__ import annotations
import math
import pygame
from pixelrush_biomes2_v3168 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW


class ModularBiomeScene(Previous):
    FINAL_BIOMES = ('cidade_futurista', 'neve', 'deserto', 'floresta', 'vulcao', 'ilhas_celestes')

    def __init__(self, biome):
        super().__init__(biome)
        if biome in self.FINAL_BIOMES:
            self._final_global_pass()
            if hasattr(self, '_map_cache'):
                self._map_cache.clear()
            if hasattr(self, '_composites'):
                self._composites.clear()

    def _final_global_pass(self):
        for layer, chunks in self._layers.items():
            for idx, surf in enumerate(chunks):
                self._apply_soft_chunk_bind(surf, layer)
                if layer == 'far':
                    self._depth_rim(surf, idx)
                elif layer == 'mid':
                    self._mid_anchor_balance(surf, idx)
                else:
                    self._near_lane_clarity(surf, idx)
                self._biome_signature_pass(surf, idx, layer)

    def _apply_soft_chunk_bind(self, surf, layer):
        h = surf.get_height()
        alpha = 26 if layer == 'far' else 22 if layer == 'mid' else 18
        tone = self.PALETTE.get(self.biome, self.PALETTE['cidade_futurista'])['seal']
        left = pygame.Surface((5, h), pygame.SRCALPHA)
        right = pygame.Surface((5, h), pygame.SRCALPHA)
        for x in range(5):
            a = max(0, alpha - x * 4)
            pygame.draw.line(left, (*tone, a), (x, 0), (x, h - 1), 1)
            pygame.draw.line(right, (*tone, a), (4 - x, 0), (4 - x, h - 1), 1)
        surf.blit(left, (0, 0))
        surf.blit(right, (LW - 5, 0))

    def _depth_rim(self, surf, idx):
        haze = pygame.Surface((LW, 36), pygame.SRCALPHA)
        pal = self.PALETTE.get(self.biome, self.PALETTE['cidade_futurista'])
        for y in range(36):
            a = 3 + y // 8
            pygame.draw.line(haze, (*pal['shade'], a), (0, y), (LW - 1, y), 1)
        surf.blit(haze, (0, 178))
        if idx % 2 == 0:
            pygame.draw.line(surf, pal['seal'], (0, 205), (LW - 1, 205), 1)

    def _mid_anchor_balance(self, surf, idx):
        # Limpa a leitura do centro e joga detalhes decorativos para as laterais.
        wash = pygame.Surface((70, 34), pygame.SRCALPHA)
        pygame.draw.rect(wash, (0, 0, 0, 9), (0, 0, 70, 34))
        surf.blit(wash, (76, 190))
        # Sinais/props pequenos nas laterais para reduzir sensação de pista poluída.
        if self.biome == 'cidade_futurista':
            self._side_pylons_future(surf, idx)
        elif self.biome == 'neve':
            self._side_snow_posts(surf, idx)
        elif self.biome == 'deserto':
            self._side_dry_stakes(surf, idx)
        elif self.biome == 'floresta':
            self._side_forest_roots(surf, idx)
        elif self.biome == 'vulcao':
            self._side_basalt_marks(surf, idx)
        elif self.biome == 'ilhas_celestes':
            self._side_celestial_markers(surf, idx)

    def _near_lane_clarity(self, surf, idx):
        # Base lateral viva, centro mais limpo para leitura de obstáculos.
        edge = pygame.Surface((LW, 28), pygame.SRCALPHA)
        for y in range(28):
            a = 3 + y // 6
            pygame.draw.line(edge, (255, 255, 255, a), (0, y), (LW - 1, y), 1)
        surf.blit(edge, (0, 223))
        gap = pygame.Surface((86, 22), pygame.SRCALPHA)
        pygame.draw.rect(gap, (0, 0, 0, 8), (0, 0, 86, 22), border_radius=6)
        surf.blit(gap, (69, 226))
        if self.biome == 'cidade_futurista':
            self._future_near_edges(surf, idx)
        elif self.biome == 'neve':
            self._snow_near_edges(surf, idx)
        elif self.biome == 'deserto':
            self._desert_near_edges(surf, idx)
        elif self.biome == 'floresta':
            self._forest_near_edges(surf, idx)
        elif self.biome == 'vulcao':
            self._volcano_near_edges(surf, idx)
        elif self.biome == 'ilhas_celestes':
            self._islands_near_edges(surf, idx)

    def _biome_signature_pass(self, surf, idx, layer):
        if self.biome == 'cidade_futurista' and layer == 'far':
            for x in range(18, LW, 54):
                pygame.draw.line(surf, (105, 237, 248, 24), (x, 170), (x, 192), 1)
        elif self.biome == 'neve' and layer == 'far':
            for x in range(18, LW, 48):
                pygame.draw.line(surf, (229, 244, 252, 22), (x, 186), (x + 3, 192), 1)
        elif self.biome == 'deserto' and layer == 'far':
            for x in range(18, LW, 50):
                pygame.draw.arc(surf, (226, 184, 124), (x, 195, 18, 5), math.radians(180), math.radians(360), 1)
        elif self.biome == 'floresta' and layer == 'mid':
            for x in (22, 190):
                pygame.draw.line(surf, (111, 169, 105), (x, 198), (x + 4, 214), 1)
        elif self.biome == 'vulcao' and layer == 'mid':
            for x in (16, 186):
                pygame.draw.line(surf, (255, 157, 74), (x, 212), (x + 7, 212), 1)
        elif self.biome == 'ilhas_celestes' and layer == 'mid':
            for x in (18, 188):
                pygame.draw.line(surf, (169, 236, 201), (x, 198), (x + 5, 192), 1)
                pygame.draw.line(surf, (121, 196, 226), (x + 2, 201), (x + 6, 197), 1)

    # ---------- biome specific side helpers ----------
    def _side_pylons_future(self, surf, idx):
        for x in (10, 192):
            pygame.draw.rect(surf, (39, 62, 100), (x, 196, 8, 17), border_radius=2)
            pygame.draw.line(surf, (111, 238, 249), (x + 2, 198), (x + 2, 209), 1)
            pygame.draw.line(surf, (245, 117, 224), (x + 5, 200), (x + 5, 206), 1)

    def _side_snow_posts(self, surf, idx):
        for x in (10, 194):
            pygame.draw.line(surf, (120, 153, 192), (x, 213), (x, 200), 1)
            pygame.draw.line(surf, (230, 246, 255), (x - 2, 202), (x + 3, 202), 1)

    def _side_dry_stakes(self, surf, idx):
        for x in (12, 194):
            pygame.draw.line(surf, (141, 100, 70), (x, 214), (x + 2, 202), 1)
            pygame.draw.line(surf, (235, 194, 133), (x - 1, 209), (x + 4, 209), 1)

    def _side_forest_roots(self, surf, idx):
        for x in (10, 190):
            pygame.draw.line(surf, (61, 87, 54), (x, 214), (x + 5, 206), 2)
            pygame.draw.line(surf, (97, 145, 84), (x + 3, 210), (x + 7, 212), 1)

    def _side_basalt_marks(self, surf, idx):
        for x in (10, 192):
            pygame.draw.rect(surf, (75, 58, 64), (x, 200, 8, 13))
            pygame.draw.line(surf, (255, 154, 72), (x + 1, 205), (x + 5, 205), 1)

    def _side_celestial_markers(self, surf, idx):
        for x in (12, 192):
            pygame.draw.line(surf, (132, 167, 186), (x + 2, 214), (x + 2, 202), 1)
            pygame.draw.ellipse(surf, (172, 237, 204), (x, 198, 6, 5))

    def _future_near_edges(self, surf, idx):
        for x in (6, 16, 28, LW - 34, LW - 22, LW - 10):
            pygame.draw.line(surf, (100, 239, 250), (x, 246), (x + 5, 246), 1)
            pygame.draw.line(surf, (245, 119, 225), (x + 1, 242), (x + 4, 242), 1)

    def _snow_near_edges(self, surf, idx):
        for x in (8, 18, 30, LW - 36, LW - 24, LW - 12):
            pygame.draw.line(surf, (246, 252, 255), (x, 247), (x + 4, 243), 1)

    def _desert_near_edges(self, surf, idx):
        for x in (8, 18, 30, LW - 36, LW - 24, LW - 12):
            pygame.draw.arc(surf, (230, 186, 121), (x, 244, 8, 4), math.radians(180), math.radians(360), 1)

    def _forest_near_edges(self, surf, idx):
        for x in (8, 18, 28, LW - 38, LW - 26, LW - 14):
            pygame.draw.line(surf, (116, 180, 97), (x + 2, 248), (x, 243), 1)
            pygame.draw.line(surf, (152, 210, 121), (x + 2, 248), (x + 4, 243), 1)

    def _volcano_near_edges(self, surf, idx):
        for x in (8, 18, 28, LW - 38, LW - 26, LW - 14):
            pygame.draw.line(surf, (255, 149, 72), (x, 245), (x + 4, 245), 1)
            pygame.draw.line(surf, (255, 214, 116), (x + 1, 246), (x + 3, 246), 1)

    def _islands_near_edges(self, surf, idx):
        for x in (8, 18, 28, LW - 38, LW - 26, LW - 14):
            pygame.draw.line(surf, (171, 237, 203), (x, 245), (x + 4, 242), 1)
            pygame.draw.line(surf, (122, 195, 223), (x + 1, 246), (x + 5, 244), 1)
