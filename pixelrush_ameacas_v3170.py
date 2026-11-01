"""v3.170.0 — correção restrita às hitboxes visuais CF4/IC4.

O dano já usa retângulos internos (_hitboxes_precisas_v342). Para os dois
perigos altos com placas de energia, a colisão antiga se estendia abaixo
os pixels visíveis. Corrige SOMENTE esta faixa transparente. Demais 26 perigos
conservam geometria e movimento idênticos.
"""
import pygame
from pixelrush_ameacas_v3169 import *
from pixelrush_ameacas_v3169 import AmeacaBioma as Anterior


class AmeacaBioma(Anterior):
    def __init__(self, x, codigo):
        super().__init__(x, codigo)
        if codigo not in ('CF4', 'IC4'):
            return
        bbox = pygame.mask.from_surface(self.image, 100).get_bounding_rects()
        if not bbox:
            return
        bounds = bbox[0].unionall(bbox[1:])
        atual = self._hitboxes_precisas_v342[0]
        # Recalibra apenas o limite inferior que antes invadia transparência.
        # Preserva início, largura, coordenadas mundiais e movimento.
        bottom = min(atual.bottom, bounds.bottom - 1)
        if bottom >= atual.y + 6:
            self._hitboxes_precisas_v342 = (pygame.Rect(atual.x, atual.y, atual.w, bottom - atual.y),)
