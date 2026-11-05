"""Pixel Rush v3.213.0 — movimentos de cenário em três atos por bioma.

Extensão estritamente visual de CenasCinematograficas (v3.172). Não cria
entidades, eventos SDL, partículas, aleatoriedade, timers ou áreas de colisão.
As lâminas pré-renderizadas acompanham os monumentos existentes. No modo leve
ou com redução de efeitos, o desenho é exatamente o da classe anterior.
"""
import math
import pygame
from pixelrush_cinema_v3172 import CenasCinematograficas, PALETAS


class CenasMemoraveis(CenasCinematograficas):
    TAMANHO = (260, 145)
    # No máximo 7 biomas x 3 atos x 2 quadros x 260 x 145 x 4 bytes = 6.04 MiB.
    LIMITE_CACHE_BYTES = 7 * 3 * 2 * 260 * 145 * 4

    def __init__(self):
        super().__init__()
        self._laminas = {}

    @staticmethod
    def ato(travel):
        pos = float(travel) % 6400.0
        if 1250 <= pos < 1700:
            return 0
        if 1700 <= pos < 2200:
            return 1
        if 2200 <= pos <= 2900:
            return 2
        return -1

    @property
    def cache_bytes(self):
        return sum(sum(s.get_width() * s.get_height() * 4 for s in quadros)
                   for quadros in self._laminas.values())

    def desenhar(self, surf, bioma, travel, frame=0, night=0, leve=False):
        existente = super().desenhar(surf, bioma, travel, frame, night)
        if leve or not existente or bioma not in PALETAS:
            return existente
        ato = self.ato(travel)
        if ato == -1:
            return existente
        # Animação determinística por posição percorrida, sem avançar relógios
        # nem consumir RNG do jogo, preservando fitas de QA.
        variante = (int(max(0.0, float(travel)) // 65)) & 1
        if bioma not in self._laminas:
            self._laminas[bioma] = tuple(
                self._construir(bioma, etapa, indice)
                for etapa in range(3) for indice in range(2))
        pos = float(travel) % 6400.0
        x = int(402 - (pos - 850) * .25)
        y = 245 if bioma in ('cidade', 'cidade_futurista') else (
            225 if bioma == 'ilhas_celestes' else 275)
        surf.blit(self._laminas[bioma][ato * 2 + variante], (x + 45, y + 15))
        return existente

    @staticmethod
    def _construir(bioma, etapa, variante):
        """Compõe geometria de apoio do próprio monumento, uma vez por lâmina."""
        s = pygame.Surface((260, 145), pygame.SRCALPHA)
        dark, mid, accent = PALETAS[bioma]
        pale = tuple(min(255, round(c * .55 + 110)) for c in accent)
        light = (*accent, 158)
        soft = (*pale, 94)
        phase = -1 if variante == 0 else 1
        n = 1 + etapa
        if bioma == 'cidade':
            # Rede elevada: faróis percorrem as janelas do horizonte.
            for i in range(2 + etapa * 2):
                xx = 25 + ((i * 42 + (etapa * 9 + variante * 12)) % 210)
                yy = 105 - (i % 3) * 20
                pygame.draw.rect(s, soft, (xx, yy, 11, 3))
            pygame.draw.arc(s, light, (5, 26, 248, 92), math.pi * 1.02,
                            math.pi * 1.92, 2)
            if etapa >= 1:
                pygame.draw.lines(s, soft, False, [(25, 112), (112, 102-phase*2),
                                                   (220, 112)], 2)
            if etapa == 2:
                pygame.draw.circle(s, light, (195 + phase*9, 69), 8, 2)
        elif bioma == 'neve':
            # Aurora localizada sobre os picos (não cria novas montanhas).
            for i in range(n + 1):
                xx = 50 + i * 47 + phase * (i + 1) * 3
                pts = [(xx-20, 60), (xx-12, 37-i*5), (xx, 20+phase*3),
                       (xx+10, 42), (xx+15, 62)]
                pygame.draw.lines(s, soft, False, pts, 3)
            for i in range(n):
                pygame.draw.line(s, light, (104 + i*25, 90),
                                 (112 + i*25 + phase*3, 76-i*4), 2)
        elif bioma == 'deserto':
            # Deslocamento de areia sobre a escadaria do templo.
            for i in range(2 + 2*etapa):
                yy = 89 + i * 7
                xx = 35 + (i * 23 + variante * 15) % 65
                pygame.draw.line(s, soft, (xx, yy), (xx + 33 + etapa*6, yy-5), 2)
            if etapa >= 1:
                pygame.draw.lines(s, light, False, [(97, 71), (130, 37-phase*3),
                                                    (165, 72)], 2)
            if etapa == 2:
                for i in range(3):
                    pygame.draw.circle(s, soft, (176 + i*17+phase*3, 66-i*9), 2)
        elif bioma == 'floresta':
            # Pulsos de água e folhas ao redor da cachoeira pré-existente.
            for i in range(2 + etapa):
                xx = 132 + i * 10 + phase * 3
                pygame.draw.line(s, soft, (xx, 60), (xx - 5-phase*2, 118), 2)
            for i in range(2 + etapa*2):
                xx = 45 + i * 34 + phase * (i % 3) * 3
                yy = 37 + (i % 3) * 15 + etapa * 5
                pygame.draw.ellipse(s, light, (xx, yy, 8, 4))
            if etapa >= 1:
                pygame.draw.arc(s, soft, (122, 96, 55, 24), 0, math.pi, 2)
        elif bioma == 'vulcao':
            # Ascensão de fumarolas e pulso de lava no vulcão já existente.
            for i in range(1 + etapa*2):
                xx = 110 + ((i * 19 + variante * 7) % 58)
                yy = 35 - ((i * 8 + etapa * 6) % 28)
                pygame.draw.circle(s, soft, (xx, yy), 5 + i % 3, 2)
            pygame.draw.lines(s, light, False,
                              [(125+phase*2, 68), (131, 87),
                               (125-phase*3, 103+etapa*4)], 2+etapa)
            if etapa == 2:
                pygame.draw.line(s, soft, (123, 112), (153, 124), 2)
        elif bioma == 'cidade_futurista':
            # Tráfego de luz sobre os corredores das torres existentes.
            for i in range(2 + etapa*2):
                xx = 30 + (i * 39 + variante * 17) % 190
                yy = 33 + (i % 3) * 29
                pygame.draw.line(s, light, (xx, yy), (xx+18, yy), 2)
                pygame.draw.line(s, soft, (xx+4, yy+3), (xx+14, yy+3), 1)
            if etapa >= 1:
                pygame.draw.arc(s, soft, (12, 22, 230, 105), math.pi, 2*math.pi, 3)
            if etapa == 2:
                pygame.draw.circle(s, light, (120+phase*8, 58), 9, 2)
        else:  # ilhas_celestes
            # Variação nas quedas d'água minerais das ilhas já desenhadas.
            for i in range(2 + etapa*2):
                xx = 45 + i * 38 + phase * 3
                top = 60 + (i % 2) * 15
                pygame.draw.line(s, soft, (xx, top),
                                 (xx - 5 - phase * 2, min(135, top + 35 + etapa*7)), 2)
            for i in range(n + 1):
                xx = 65 + i * 52 + phase*4
                pygame.draw.polygon(s, light, [(xx, 34-i*4), (xx+4, 42-i*4),
                                               (xx, 49-i*4), (xx-4, 42-i*4)])
        return s
