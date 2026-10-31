"""Pixel Rush v3.147.0 — horizonte contínuo da Floresta Densa.

Só substitui o relevo da camada 'far'. A paisagem distante é construída
uma vez por chunk (225x250) e acompanha o mesmo parallax/caches do jogo.
As funções são periódicas em quatro chunks, inclusive na junção 3 -> 0.
"""
import math
import pygame
from pixelrush_biomes2_v3146 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, LH


class ModularBiomeScene(Previous):
    _FOREST_PERIOD = LW * 4

    @classmethod
    def _ridge_height(cls, absolute_x, plane):
        # Continuidade matemática, inclusive no final do ciclo de 4 chunks.
        angle = 2.0 * math.pi * (absolute_x % cls._FOREST_PERIOD) / cls._FOREST_PERIOD
        if plane == 0:  # distância azulada: pequena e irregular, sem painel plano
            return round(197.0 - 5.0 * math.sin(angle * 2.0 + 0.65)
                         - 3.0 * math.sin(angle * 5.0 - 0.4)
                         - 1.0 * math.sin(angle * 11.0 + 0.9))
        if plane == 1:  # mata intermediária de contraste suave
            return round(204.0 - 4.0 * math.sin(angle * 3.0 - 0.35)
                         - 2.0 * math.sin(angle * 7.0 + 1.1))
        # Base vegetada baixa; a pista continua sob o chão já existente.
        return round(211.0 - 3.0 * math.sin(angle * 2.0 + 2.2)
                     - 1.0 * math.sin(angle * 9.0 - 0.4))

    def _far_ridge(self, surface, index):
        """Desenha três planos contínuos sem retângulos cobrindo o horizonte."""
        colors = ((111, 155, 149), (83, 128, 117), (57, 102, 87))
        offset = (index % 4) * LW
        # Tudo por coluna, sem arredondamento nos pontos de junção do polígono.
        # O limite superior de cada plano é pré-calculado só no carregamento.
        heights = []
        for plane, color in enumerate(colors):
            top = [self._ridge_height(offset + x, plane) for x in range(LW)]
            heights.append(top)
            for x, y in enumerate(top):
                pygame.draw.line(surface, color, (x, y), (x, 218), 1)
        # Arbustos azulados no horizonte, ancorados ao relevo. Nenhuma forma
        # fica encostada ao limite do chunk e não criamos objetos flutuantes.
        for local_x in (18, 57, 106, 154, 201):
            y = heights[1][local_x] + 2
            shade = (92, 138, 127) if (local_x + index) % 2 else (100, 143, 134)
            pygame.draw.line(surface, shade, (local_x - 5, y + 4), (local_x, y - 2), 1)
            pygame.draw.line(surface, shade, (local_x, y - 2), (local_x + 5, y + 4), 1)
            pygame.draw.line(surface, (120, 166, 151), (local_x - 3, y + 1),
                             (local_x + 2, y), 1)
        # Bosquetes baixos preenchem apenas vazios irregulares entre troncos,
        # sem faixa horizontal ou copas recortadas na borda dos tiles.
        for n, cx in enumerate((22, 58, 96, 142, 174, 210)):
            top = (166 if n in (3, 4) else 176) + ((index * 3 + n * 7) % 9)
            half = (11, 14, 11, 19, 18, 10)[n]
            dark = (78, 119, 108) if n % 2 else (86, 128, 117)
            light = (110, 151, 135)
            outline = [
                (cx-half, 213), (cx-half+2, top+15),
                (cx-half+5, top+9), (cx-half+8, top+12),
                (cx-4, top+3), (cx, top), (cx+4, top+3),
                (cx+half-7, top+7), (cx+half-4, top+5),
                (cx+half, top+12), (cx+half-2, 214),
            ]
            pygame.draw.polygon(surface, dark, outline)
            pygame.draw.line(surface, light, (cx-6, top+9), (cx+2, top+6), 1)
            pygame.draw.line(surface, (65, 108, 97), (cx+3, top+13), (cx+8, top+16), 1)
        # Pequenas janelas de céu entre os bosquetes ainda ficam transparentes.
        # Texturas finas de folhas apenas em pixels preenchidos, nunca no céu.
        for k in range(34):
            x = (23 + k * 37 + (index * 13)) % LW
            y = heights[1][x] + 3 + (k % 5)
            if y < 216:
                col = (119, 165, 145) if k % 3 else (66, 110, 99)
                pygame.draw.line(surface, col, (x, y), (min(LW - 1, x + 2), y), 1)
