"""PIXEL RUSH v3.277.27: aceleracao SDL-RLE apenas em texturas RGBA imutaveis.

Preserva alfa, cores, geometria, ordem de desenho e todos os quadros.
Em sprites com bordas translucidas, manter o blend SDL convencional:
RLE pode alterar o arredondamento da mistura em +/-1 no RGB.
"""
import pygame

_EXAMINADAS = set()
MAX_IDS = 2048


def acelerar_textura_estatica(surface, alpha_binario=False):
    if surface is None or not (surface.get_flags() & pygame.SRCALPHA):
        return surface
    if surface.get_alpha() != 255:
        return surface
    ident = id(surface)
    if ident in _EXAMINADAS:
        return surface
    if alpha_binario:
        # Verificacao apenas no PRIMEIRO uso de um atlas pronto.
        # Evita custo por quadro, import NumPy ja exigido pelos biomas.
        import numpy as np
        pixels = pygame.surfarray.pixels_alpha(surface)
        try:
            opaco_ou_vazio = not np.any((pixels > 0) & (pixels < 255))
        finally:
            del pixels
        if not opaco_ou_vazio:
            _EXAMINADAS.add(ident)
            return surface
    try:
        surface.set_alpha(255, pygame.RLEACCEL)
    except pygame.error:
        return surface
    if len(_EXAMINADAS) >= MAX_IDS:
        _EXAMINADAS.clear()
    _EXAMINADAS.add(ident)
    return surface
