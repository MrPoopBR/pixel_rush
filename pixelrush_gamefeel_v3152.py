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
        # Seguimento de câmera abaixo de 5px, sem warp de textura.
        self._qa_camera_x = 0.0
        self._qa_camera_y = 0.0
        self._coleta_pos = None
        self._coleta_ttl = 0

    def reiniciar(self):
        super().reiniciar()
        self._qa_camera_x = 0.0
        self._qa_camera_y = 0.0
        self._coleta_pos = None
        self._coleta_ttl = 0

    def seguir_jogador(self, jogador, segurando_pulo=False, reduzir_efeitos=False):
        """Foco vertical amortecido, inclinação sugerida por drift lateral.

        Alteração exclusivamente de câmera; não altera rect/colisão, cria
        Surface, shaders nem zoom. Mantém acessibilidade com fallback 0.
        """
        if reduzir_efeitos or jogador is None or getattr(jogador,"morrendo",False):
            alvo_x = alvo_y = 0.0
        elif getattr(jogador,"descida_rapida",False) and not jogador.no_chao:
            alvo_x, alvo_y = -1.0, 4.0
        elif not jogador.no_chao and getattr(jogador,"jetpack_fase",None) is None:
            chao_y=float(getattr(jogador,"chao_y",730))
            altura=max(0.,min(1.0,(chao_y-jogador.rect.bottom)/125.))
            alvo_x = 2.4 if segurando_pulo else 1.0
            alvo_y = -4.0*altura
        else:
            alvo_x = alvo_y = 0.0
        self._qa_camera_x += (alvo_x-self._qa_camera_x)*.18
        self._qa_camera_y += (alvo_y-self._qa_camera_y)*.16

    def deslocamento(self):
        x,y=super().deslocamento()
        return (x+int(round(self._qa_camera_x)),
                y+int(round(self._qa_camera_y)))

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
