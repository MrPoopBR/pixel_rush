"""Pixel Rush 3.175.0 — composição cromática por profundidade.

Tratamento de arte existente. Não cria objetos, sprites, partículas ou geometria.
Aplicado uma única vez por superfície renderizada em cache; alfa preservado.
"""
from __future__ import annotations
import pygame

# Misturas de cor são específicas do bioma; FAR menos contrastado que MID.
# A pista e a camada NEAR NÃO recebem alteração: ameaças seguem nítidas.
PLANOS = {
    'cidade': ((145, 174, 203), 0.25, (119, 144, 173), 0.11),
    'neve': ((184, 208, 230), 0.24, (158, 188, 216), 0.11),
    'deserto': ((225, 177, 139), 0.22, (201, 154, 119), 0.11),
    'vulcao': ((176, 125, 115), 0.22, (142, 100, 98), 0.12),
    'floresta': ((147, 184, 159), 0.24, (113, 155, 127), 0.13),
    'cidade_futurista': ((126, 168, 209), 0.25, (93, 139, 180), 0.12),
    'ilhas_celestes': ((184, 215, 229), 0.23, (149, 196, 216), 0.11),
}


def compor_plano(surface: pygame.Surface, biome: str, plano: str) -> None:
    """Aplica perspectiva atmosférica ao RGB visível sem tocar no canal alfa.

    Preserva bordas pixeladas; não faz blur nem aplica escala ou nova imagem.
    """
    if biome not in PLANOS or plano not in ('far', 'mid'):
        return
    a, fa, b, fb = PLANOS[biome]
    alvo, amount = (a, fa) if plano == 'far' else (b, fb)
    mix = int(amount * 256 + .5)
    if mix == 0:
        return
    import numpy as np
    rgb = pygame.surfarray.pixels3d(surface)
    alpha = pygame.surfarray.pixels_alpha(surface)
    try:
        solid = alpha > 0
        for c in range(3):
            channel = rgb[:, :, c]
            old = channel[solid].astype(np.uint16)
            channel[solid] = ((old * (256 - mix) + alvo[c] * mix + 128) // 256).astype(np.uint8)
    finally:
        del alpha, rgb
