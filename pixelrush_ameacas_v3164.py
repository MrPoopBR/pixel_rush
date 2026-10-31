"""Pixel Rush v3.164.0 — acabamento APENAS dos quatro perigos do Vulcão.

V1 Salamandra, V2 Morcego, V3 Rocha e V4 Gêiser. Mantém integralmente:
- 3 poses originais por perigo;
- dimensões e canal alfa (portanto área ocupada para colisão);
- movimento, velocidade, spawn, dano e temporização existentes.
Tudo é computado UMA VEZ por frame/ID e guardado em cache.
"""
import random
import numpy as np
import pygame
import pixelrush_ameacas_v3127 as _motor
from pixelrush_ameacas_v3163 import *
from pixelrush_ameacas_v3163 import imagem_ameaca as _sprite_anterior
from pixelrush_ameacas_v3163 import AmeacaBioma as _ClasseAnterior

_CACHE_VULCAO_3164 = {}
_PERIGOS_VULCAO = frozenset(('V1', 'V2', 'V3', 'V4'))


def _acabar_sprite(codigo, fase, original):
    result = original.copy().convert_alpha()
    alpha = pygame.surfarray.array_alpha(original)
    original_rgb = pygame.surfarray.array3d(original)
    width, height = result.get_size()
    xx = np.arange(width, dtype=np.int16)[:, None]
    yy = np.arange(height, dtype=np.int16)[None, :]
    r0 = original_rgb[:, :, 0].astype(np.int16)
    g0 = original_rgb[:, :, 1].astype(np.int16)
    b0 = original_rgb[:, :, 2].astype(np.int16)
    lum = (r0 * 3 + g0 * 5 + b0 * 2) // 10
    solid = (alpha >= 230) & (lum > 46)
    # Somente miolo visível, respeitando antialiasing, olhos e contorno original.
    body = solid & (lum < 233)

    out = original_rgb.astype(np.int16)
    # Iluminação: magma aquece a parte baixa, sem engolir os contornos escuros.
    glow_y = np.clip((yy.astype(np.float32) - height * .54) / max(1.0, height * .46), 0, 1)
    upper = np.clip((height * .43 - yy.astype(np.float32)) / max(1.0, height * .43), 0, 1)

    if codigo == 'V1':
        # Escamas da salamandra: superfície vítrea escurecida e canais quentes.
        shades = body & (r0 > 75) & (r0 > g0 * .92) & (yy >= height * .28)
        alternado = (((xx // 5) + (yy // 3) + fase) % 3 == 0)
        inc = np.where(shades & alternado, 14, 0)
        out[:, :, 0] += inc
        out[:, :, 1] += (inc // 2)
        out[:, :, 2] -= np.where(shades & alternado, 5, 0)
        edge = shades & ((yy + (xx // 7)) % 8 == 0)
        out[:, :, 0] += np.where(edge, 16, 0)
        out[:, :, 1] += np.where(edge, 7, 0)
        # Sombreamento profundo na barriga mantendo brilho do dorso.
        out[:, :, 2] += np.where(shades, (upper * 7).astype(np.int16), 0)
        fleck_colors = ((255, 193, 103), (240, 121, 63), (160, 88, 80))
        density = 18
    elif codigo == 'V2':
        # Membranas aladas: fibras diagonais e variação de transparência aparente
        # SEM mudar o alfa real nem as arestas das asas.
        wings = body & (r0 > 78) & (r0 > g0 * 1.13) & (yy < height * .76)
        veins = wings & ((xx + yy * 2 + fase * 3) % 12 == 0)
        shadow = wings & ((xx * 2 - yy + fase) % 13 == 0)
        out[:, :, 0] += np.where(veins, 20, 0)
        out[:, :, 1] += np.where(veins, 9, 0)
        out[:, :, 2] += np.where(veins, 8, 0)
        out[:, :, 0] -= np.where(shadow, 13, 0)
        out[:, :, 2] += np.where(shadow, 10, 0)
        # Couro escuro do corpo, em contraste com a membrana incandescente.
        chest = body & (xx > width * .32) & (xx < width * .72) & (yy > height * .45)
        out[:, :, 0] += np.where(chest, (glow_y * 15).astype(np.int16), 0)
        out[:, :, 1] += np.where(chest, (glow_y * 5).astype(np.int16), 0)
        fleck_colors = ((245, 154, 113), (200, 102, 112), (151, 94, 143))
        density = 14
    elif codigo == 'V3':
        # Facetas irregulares da obsidiana, com contraste entre mineral frio
        # e fissuras quentes já existentes.
        rock = body & (yy > 3) & (r0 < 210) & (r0 < g0 * 2.9)
        facets = rock & (((xx - yy * 2 + fase) % 14) < 2)
        strata = rock & (((yy + xx // 7) % 11) == 0)
        out[:, :, 0] += np.where(facets, 19, 0)
        out[:, :, 1] += np.where(facets, 13, 0)
        out[:, :, 2] += np.where(facets, 23, 0)
        out[:, :, 0] -= np.where(strata, 12, 0)
        out[:, :, 1] -= np.where(strata, 7, 0)
        hot = body & (r0 > 165) & (g0 > 55) & (r0 > b0 * 1.4)
        out[:, :, 0] += np.where(hot, 7, 0)
        out[:, :, 1] += np.where(hot, 11, 0)
        fleck_colors = ((173, 129, 155), (121, 97, 146), (250, 177, 92))
        density = 17
    else:  # V4 — gêiser
        # Concentração de vapor com filamentos verticais e iluminados por baixo.
        steam = body & (yy < height * .79) & (b0 > 94) & (g0 > 112)
        filaments = steam & (((xx * 2 + yy + fase * 5) % 11) < 2)
        cool = steam & (((xx - yy // 2 + fase * 3) % 13) == 0)
        out[:, :, 0] += np.where(filaments, 15, 0)
        out[:, :, 1] += np.where(filaments, 19, 0)
        out[:, :, 2] += np.where(filaments, 22, 0)
        out[:, :, 0] -= np.where(cool, 7, 0)
        out[:, :, 2] += np.where(cool, 13, 0)
        hot_base = body & (yy > height * .72) & (r0 > 130)
        out[:, :, 0] += np.where(hot_base, (glow_y * 10).astype(np.int16), 0)
        out[:, :, 1] += np.where(hot_base, (glow_y * 5).astype(np.int16), 0)
        fleck_colors = ((239, 246, 242), (198, 220, 225), (250, 171, 106))
        density = 13 if fase else 7

    # Micropixels minerais em regiões internas, sem grudar novos pixels no céu.
    rng = random.Random(316400 + int(codigo[-1]) * 697 + fase * 91)
    valid = np.argwhere(body & (xx >= 5) & (xx < width - 5) & (yy >= 5) & (yy < height - 5))
    if len(valid):
        for n in range(density):
            x, y = (int(v) for v in valid[rng.randrange(len(valid))])
            if codigo == 'V4' and y < height * .15:
                continue
            # Mistura em vez de pontos sólidos: mais riqueza e menos ruído.
            col = fleck_colors[n % len(fleck_colors)]
            out[x, y, :] = (out[x, y, :] * 3 + np.array(col, dtype=np.int16)) // 4

    out = np.clip(out, 0, 255).astype(np.uint8)
    pixels = pygame.surfarray.pixels3d(result)
    pixels[:, :, :] = out
    del pixels
    # A matriz alfa é preservada integralmente, inclusive pixels semitransparentes:
    # área visual ocupada e máscara de colisão ficam exatamente iguais.
    assert np.array_equal(pygame.surfarray.array_alpha(result), alpha)
    return result


def imagem_ameaca(codigo, fase=0):
    if codigo not in _PERIGOS_VULCAO:
        return _sprite_anterior(codigo, fase)
    import os
    if os.environ.get('PIXELRUSH_ARTE_CLASSICA') == '1':
        return _sprite_anterior(codigo, fase)
    fase = int(fase) % 3
    key = (codigo, fase)
    value = _CACHE_VULCAO_3164.get(key)
    if value is None:
        value = _acabar_sprite(codigo, fase, _sprite_anterior(codigo, fase))
        _CACHE_VULCAO_3164[key] = value
    return value


# A classe original de ameaça desenha através do motor. Usar SOMENTE
# o ponto de extensão visual já existente, sem tocar em colisões/física.
_motor.imagem_ameaca = imagem_ameaca


# Preserva a MESMA classe e comportamento, sem acrescentar herança.
AmeacaBioma = _ClasseAnterior
