"""v3.152.0 — confirmação visual curta de coleta, aproveitando o GameFeel.

O pulo, o pouso, o deslize e as partículas/áudio já existem. Este módulo
apenas acrescenta um brilho mínimo às moedas coletadas por 5 quadros visíveis;
nenhuma Surface, som, timer de física ou partícula persistente é criada.
"""
import pygame
from pixelrush_gamefeel_v3132 import GameFeel as Anterior, criar_variantes_pitch, criar_camada_ritmica


class GameFeel(Anterior):
    def __init__(self):
        super().__init__()
        self._coleta_pos = None
        self._coleta_ttl = 0

    def reiniciar(self):
        super().reiniciar()
        self._coleta_pos = None
        self._coleta_ttl = 0

    def registrar_coleta(self, x, y):
        # O efeito complementa as partículas de coleta já existentes,
        # sem acionar vibração ou novo áudio repetitivo.
        self._coleta_pos = (int(x), int(y))
        self._coleta_ttl = 5

    def desenhar(self, surf, jogador=None, combo=0, bioma='cidade'):
        super().desenhar(surf, jogador, combo, bioma)
        if self._coleta_ttl and self._coleta_pos is not None:
            x, y = self._coleta_pos
            if 12 <= x < 438 and 140 <= y < 720:
                raio = 2 + (5 - self._coleta_ttl)
                cor = (255, 240, 166)
                pygame.draw.line(surf, cor, (x - raio, y), (x - raio - 2, y), 1)
                pygame.draw.line(surf, cor, (x + raio, y), (x + raio + 2, y), 1)
                pygame.draw.line(surf, cor, (x, y - raio), (x, y - raio - 2), 1)
                pygame.draw.line(surf, cor, (x, y + raio), (x, y + raio + 2), 1)
            self._coleta_ttl -= 1
