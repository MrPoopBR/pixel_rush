"""Pixel Rush v3.127.0 — acabamento visual opcional das ameacas legadas.

Somente opera quando uma surface é criada. Preserva dimensões, máscara de
transparência e colorkey, sem alterar colisões ou a geometria jogável.
"""
import numpy as np
import pygame

# Padrões moderados de materiais existentes. Todos são calculados uma vez.
_MATERIAL = {
    'cacto':     ((104, 201, 111), (20, 56, 34), 7),
    'voador':    ((157, 222, 251), (29, 35, 83), 9),
    'pulador':   ((250, 206, 255), (77, 42, 116), 6),
    'escorpiao': ((255, 191, 121), (87, 40, 39), 7),
    'gelo':      ((238, 251, 255), (74, 118, 169), 10),
}


def acabamento_legado(surface, material):
    """Microtextura e volume por contraste SEM mexer no alpha do obstaculo.

    Nunca troca um pixel de colorkey, nem adiciona borda fora da silhueta.
    Retorna surface com as mesmas dimensões; custo amortizado na criação.
    """
    if material not in _MATERIAL:
        return surface
    out = surface.copy()
    rgb = pygame.surfarray.pixels3d(out)
    bg = out.get_colorkey()
    if bg is not None:
        bg = tuple(bg[:3])
        opaque = np.any(rgb != np.asarray(bg, dtype=rgb.dtype), axis=2)
    else:
        if out.get_flags() & pygame.SRCALPHA:
            alpha = pygame.surfarray.pixels_alpha(out)
            opaque = alpha > 0
            del alpha
        else:
            opaque = np.ones(rgb.shape[:2], dtype=bool)
    if not opaque.any():
        del rgb
        return out
    highlight, shadow, period = _MATERIAL[material]
    xx = np.arange(rgb.shape[0], dtype=np.int32)[:, None]
    yy = np.arange(rgb.shape[1], dtype=np.int32)[None, :]
    lum = rgb.astype(np.int16)
    # não mexe em olhos brancos, linhas de contorno escuras ou pontos emissivos.
    light = lum.max(axis=2)
    dark = lum.min(axis=2)
    mid = opaque & (light >= 58) & (light <= 228) & ((light - dark) > 11)
    fine = ((xx*5 + yy*11 + xx*yy//period) % (period+13)) == 2
    shade = ((xx//(period+2) + yy//5) % 5) == 3
    hi = mid & fine
    lo = mid & shade & ~hi
    if np.any(hi):
        lum[hi] = (lum[hi]*3 + np.array(highlight, dtype=np.int16))/4
    if np.any(lo):
        lum[lo] = (lum[lo]*4 + np.array(shadow, dtype=np.int16))/5
    # volume direcional da mesma silhueta: bordas internas superiores levemente
    # iluminadas, inferiores levemente sombreadas, sem halos extras.
    above = np.zeros_like(opaque)
    above[:, 1:] = opaque[:, :-1]
    below = np.zeros_like(opaque)
    below[:, :-1] = opaque[:, 1:]
    left = np.zeros_like(opaque)
    left[1:, :] = opaque[:-1, :]
    right = np.zeros_like(opaque)
    right[:-1, :] = opaque[1:, :]
    rim_top = mid & (~above | ~left)
    rim_bottom = mid & (~below | ~right) & ~rim_top
    lum[rim_top] = np.minimum(255, lum[rim_top] + 11)
    lum[rim_bottom] = np.maximum(0, lum[rim_bottom] - 13)
    rgb[opaque] = np.clip(lum[opaque], 0, 255).astype(np.uint8)
    del rgb
    if bg is not None:
        out.set_colorkey(bg)
    return out
