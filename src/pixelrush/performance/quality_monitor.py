# -*- coding: utf-8 -*-
"""QA792: classe original QA791, alvo Android configurado uma vez pelo motor."""
E_ANDROID = False

class MonitorQualidadeVisual:
    """Histerese evita flicker ao alternar detalhes, sem mudar o passo fixo."""
    def __init__(self):
        self.reduzido = False
        self.fps_suavizado = 30.0 if E_ANDROID else 60.0
        self.tempo_baixo = 0.0
        self.tempo_recuperacao = 0.0

    def atualizar(self, fps, dt, modo, jogando):
        if modo != 'auto':
            self.reduzido = False
            self.tempo_baixo = self.tempo_recuperacao = 0.0
            return
        if not jogando or fps < 1:
            self.tempo_baixo = self.tempo_recuperacao = 0.0
            return
        dt = max(0.0, min(0.12, float(dt)))
        self.fps_suavizado += (fps - self.fps_suavizado) * min(1.0, dt * 3.0)
        fps = self.fps_suavizado
        # Proporcao identica dos limiares 49/55 FPS de desktop,
        # mas sobre alvo de apresentacao 30 FPS no Android.
        alvo_fps = 30.0 if E_ANDROID else 60.0
        if fps < alvo_fps * (49.0 / 60.0):
            self.tempo_baixo += dt
            self.tempo_recuperacao = 0.0
        elif fps > alvo_fps * (55.0 / 60.0):
            self.tempo_recuperacao += dt
            self.tempo_baixo = 0.0
        else:
            self.tempo_baixo = max(0.0, self.tempo_baixo - dt * 0.25)
            self.tempo_recuperacao = max(0.0, self.tempo_recuperacao - dt * 0.5)
        if not self.reduzido and self.tempo_baixo >= 2.0:
            self.reduzido = True
            self.tempo_baixo = 0.0
        elif self.reduzido and self.tempo_recuperacao >= 12.0:
            self.reduzido = False
            self.tempo_recuperacao = 0.0
