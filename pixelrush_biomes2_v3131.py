"""Percursos com identidade no Deserto: dunas, mercado, ruínas e oásis.

Reutiliza o mosaico do v3.130, sem novas texturas em disco nem cálculos caros
por quadro. Neve e demais cenários permanecem sem mudanças.
"""
import math
import random
import pygame
from pixelrush_biomes2_v3130 import ModularBiomeScene as Previous, MODULAR_BIOMES
from pixelrush_biomes2_v3128 import DEPTH
from pixelrush_biomes2_v3126 import LW, LH

DISTRITOS = ('DUNAS', 'MERCADO', 'RUINAS', 'OASIS')
# Índices existentes do atlas procedural anterior. Variações do mesmo distrito.
ROTAS = {
    'near': ((8, 16, 20), (0, 4, 6, 12, 14, 22), (5, 13, 21), (2, 10, 18)),
    'mid': ((8, 16), (0, 4, 6, 12, 14), (5, 13), (2, 10, 18)),
}


class ModularBiomeScene(Previous):
    def _make_chunk(self, layer, index):
        if self.biome != 'deserto' or layer not in ('near', 'mid'):
            return super()._make_chunk(layer, index)
        if index in ROTAS[layer][3]:
            return self._oasis_chunk(layer, index)
        if index not in ROTAS[layer][0]:
            return super()._make_chunk(layer, index)
        # Abertura real entre construções: camadas leves só com dunas/rochas.
        # É gerado UMA VEZ no carregamento, não durante cada frame.
        rng = random.Random(13100 + index * 101 + (3 if layer == 'mid' else 9) + self._pose * 17)
        s = pygame.Surface((LW, LH), pygame.SRCALPHA)
        if layer == 'mid':
            for k, (base, color) in enumerate(((189, (217, 162, 112)), (212, (234, 177, 116)))):
                phase = (index % 5) * .38 + k
                points = [(x, int(base - (14 + k * 9) * (0.5 + .5 * math.sin((x / LW) * math.tau + phase))))
                          for x in range(0, LW + 1, 3)]
                pygame.draw.polygon(s, color, points + [(LW, 234), (0, 234)])
                pygame.draw.lines(s, (247, 204, 146), False, points, 1)
            # Pedra de referência recortada em silhueta, bem atrás da área jogável.
            x = 82 + (index * 13) % 59
            pygame.draw.polygon(s, (171, 124, 93), ((x-28, 215), (x-22, 195), (x-9, 180),
                                                     (x+10, 182), (x+23, 214)))
            pygame.draw.line(s, (233, 183, 124), (x-19, 195), (x-7, 184), 2)
        else:
            pygame.draw.polygon(s, (207, 149, 106), [(0, 231), (0, 224), (47, 218),
                                                    (96, 225), (164, 218), (LW, 223), (LW, 250), (0, 250)])
            # Ruínas baixas/pedras no fundo; nunca à frente do corredor do jogador.
            for x in (30 + index % 11, 173 - index % 9):
                y = rng.choice((220, 223))
                pygame.draw.polygon(s, (153, 108, 83), ((x-14, y), (x-9, y-9),
                                                        (x+3, y-12), (x+14, y-4), (x+17, y)))
                pygame.draw.line(s, (227, 181, 127), (x-7, y-9), (x+4, y-11), 2)
            pygame.draw.line(s, (244, 194, 130), (0, 229), (LW, 229), 2)
            pygame.draw.rect(s, (124, 87, 73), (0, 234, LW, 16))
            for _ in range(13):
                x = rng.randrange(5, LW - 8)
                y = rng.randrange(237, 249)
                pygame.draw.line(s, (153, 107, 81), (x, y), (x + 3, y))
        return s

    def _oasis_chunk(self, layer, index):
        """Oásis legível: palmeiral e lagoa no plano de fundo, sem colisão.

        Desenhado antes da corrida; não adiciona sprites, água física nem sons.
        """
        rng = random.Random(13131 + index * 71 + self._pose * 43)
        s = pygame.Surface((LW, LH), pygame.SRCALPHA)
        if layer == 'mid':
            pygame.draw.polygon(s, (217, 163, 110),
                                ((0, 208), (0, 201), (50, 197), (116, 206), (175, 196),
                                 (LW, 199), (LW, 235), (0, 235)))
            pygame.draw.ellipse(s, (102, 145, 134), (26, 201, 184, 25))
            pygame.draw.ellipse(s, (83, 163, 162), (32, 204, 175, 18))
            pygame.draw.line(s, (158, 206, 187), (55, 208), (147, 211), 2)
            for x, height in ((24, 67), (58, 53), (162, 74), (201, 58)):
                self._palm(s, x + (index % 3), 216, height + index % 4, index + x)
            for x in (74, 123, 192):
                pygame.draw.ellipse(s, (108, 137, 78), (x-9, 207, 20, 9))
            pygame.draw.rect(s, (195, 139, 100), (0, 222, LW, 20))
        else:
            pygame.draw.polygon(s, (209, 153, 106),
                                ((0, 231), (0, 221), (44, 219), (92, 224),
                                 (161, 220), (LW, 221), (LW, 250), (0, 250)))
            pygame.draw.ellipse(s, (81, 130, 130), (40, 213, 155, 19))
            pygame.draw.ellipse(s, (73, 175, 169), (50, 216, 137, 12))
            pygame.draw.arc(s, (174, 214, 185), (56, 216, 125, 10), .3, 2.6, 1)
            for x, height in ((26, 53), (95, 64), (193, 58)):
                self._palm(s, x, 224, height + (index % 5), index + x)
            self._well(s, 147, 229)
            for x in (19, 68, 180, 212):
                pygame.draw.ellipse(s, (97, 132, 82), (x-8, 218, 18, 10))
                pygame.draw.line(s, (164, 187, 94), (x-4, 220), (x+7, 217))
            pygame.draw.line(s, (244, 194, 130), (0, 229), (LW, 229), 2)
            pygame.draw.rect(s, (124, 87, 73), (0, 234, LW, 16))
            for _ in range(13):
                x, y = rng.randrange(5, LW-8), rng.randrange(236, 248)
                pygame.draw.line(s, (158, 109, 81), (x, y), (x+3, y))
        return s

    def _draw_layer(self, dst, layer, travel, kind):
        if self.biome != 'deserto' or layer not in ROTAS:
            return super()._draw_layer(dst, layer, travel, kind)
        # 3 mosaicos por distrito, trocando apenas quando o próximo entra pela
        # borda. O percurso não depende de frame-rate e dispensa RNG em render.
        offset = max(0., travel) * DEPTH[layer][0] * .5
        primeiro = int(offset // LW)
        deslocamento = int(offset % LW)
        for j in range(2):
            bloco = primeiro + j
            distrito = (bloco // 3) % len(DISTRITOS)
            conjunto = ROTAS[layer][distrito]
            indice = conjunto[(bloco + bloco // 12) % len(conjunto)]
            dst.blit(self._tile_map(layer, indice, kind), (j * LW - deslocamento, 0))
