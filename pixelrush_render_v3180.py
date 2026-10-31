"""Pixel Rush v3.180.0 — correção localizada do contorno existente.

Os obstáculos legados não informam sempre seu bioma (ex.: cactos do
Deserto). O renderizador v3.170 caía na paleta Cidade, pouco legível na
areia. A correção usa o bioma ativo APENAS na escolha da paleta dos sprites
sem bioma, sem duplicar desenho, mudar o sprite, física ou a hitbox.
"""
from pixelrush_render_v3170 import ContornosLegiveis as _ContornosAnteriores
from pixelrush_render_v3170 import PALETAS


class ContornosLegiveis(_ContornosAnteriores):
    def __init__(self, largura=450, altura=800, capacidade=96):
        super().__init__(largura, altura, capacidade)
        self._bioma_ativo = 'cidade'

    def _bioma(self, obj):
        declarado = getattr(obj, 'bioma', None) or getattr(obj, 'cenario', None)
        return declarado if declarado in PALETAS else self._bioma_ativo

    def desenhar(self, superficie, obstaculos, frame_contador=0, bioma_atual=None):
        if bioma_atual in PALETAS:
            self._bioma_ativo = bioma_atual
        return super().desenhar(superficie, obstaculos, frame_contador)
