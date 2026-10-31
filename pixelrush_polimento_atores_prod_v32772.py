# -*- coding: utf-8 -*-
"""v3.277.2-PROD: polimento visual offline das skins e dos inimigos.

Apenas cores RGB de pixels opacos existentes são modificadas. Dimensões,
alpha, poses, quantidade/ordem/cadência dos quadros, hitboxes e movimento
permanecem iguais. As operações vetorizadas rodam uma única vez quando os
atlases entram no cache, e nunca dentro do update ou do desenho por frame.
Esta revisão pertence SOMENTE à variante de publicação.
"""
from __future__ import annotations
import numpy as np
import pygame

SKINS_ATIVAS = frozenset(('AZUL', 'VERDE', 'ROSA'))
PALETAS = {
    'AZUL': ((105, 218, 255), (38, 66, 115)),
    'VERDE': ((233, 255, 142), (37, 97, 50)),
    'ROSA': ((255, 224, 248), (142, 53, 117)),
}
# Perigos cromáticos de todos os biomas: nenhum novo tipo de inimigo.
PALETAS_BIOMA = {
    'C': ((255, 239, 175), (70, 77, 99)),
    'N': ((228, 249, 255), (53, 88, 115)),
    'D': ((255, 237, 154), (122, 77, 43)),
    'CF': ((115, 254, 249), (34, 85, 129)),
    'V': ((255, 202, 122), (107, 48, 43)),
    'F': ((191, 241, 156), (43, 91, 64)),
    'IC': ((212, 247, 255), (67, 84, 128)),
}
ESTADOS_GESTO = frozenset(('CORRER', 'IMPULSO', 'SUBINDO', 'PULAR',
                            'CAINDO', 'AGACHAR', 'SWIPE_DOWN', 'POUSO'))


def _polir_rgb(quadro, luz, sombra, fase, papel, estado=''):
    """Modifica somente RGB de pixels interiores; não cria pixels ou contornos."""
    alfa_antes = pygame.surfarray.array_alpha(quadro)
    w, h = quadro.get_size()
    if w < 8 or h < 8:
        return quadro
    original = pygame.surfarray.array3d(quadro)
    solido = alfa_antes >= 245
    # Proteção de pelo menos 1 pixel ao redor do interior.
    interno = solido.copy()
    interno[1:, :] &= solido[:-1, :]
    interno[:-1, :] &= solido[1:, :]
    interno[:, 1:] &= solido[:, :-1]
    interno[:, :-1] &= solido[:, 1:]
    interno[0, :] = interno[-1, :] = False
    interno[:, 0] = interno[:, -1] = False
    maior = original.max(axis=2)
    menor = original.min(axis=2)
    # Evitar reforçar pixels negros do contorno, a pupila, o branco dos olhos
    # e os pixels mais saturados que sinalizam colisão/ataque.
    material = interno & (maior >= 62) & (maior <= 236)
    xy = np.indices((w, h), dtype=np.int16)
    x, y = xy[0], xy[1]
    top_esq = material & ((x * 13 // w + y * 11 // h) < 11)
    fundo_dir = material & ((x * 10 // w + y * 14 // h) > 13)
    # Shading de 2px na borda INTERNA, sem qualquer halo adicional.
    topo = np.zeros((w, h), dtype=bool)
    esquerda = np.zeros((w, h), dtype=bool)
    baixo = np.zeros((w, h), dtype=bool)
    direita = np.zeros((w, h), dtype=bool)
    topo[:, 2:] = ~solido[:, :-2]
    esquerda[2:, :] = ~solido[:-2, :]
    baixo[:, :-2] = ~solido[:, 2:]
    direita[:-2, :] = ~solido[2:, :]
    iluminar = material & (top_esq | topo | esquerda)
    escurecer = material & (fundo_dir | baixo | direita) & ~iluminar
    # A diferença é leve para conservar o pixel art e identidade do desenho.
    rgb = original.astype(np.int16)
    cor_luz = np.asarray(luz, dtype=np.int16)
    cor_sombra = np.asarray(sombra, dtype=np.int16)
    if np.any(iluminar):
        rgb[iluminar] = (rgb[iluminar] * 76 + cor_luz * 24 + 50) // 100
    if np.any(escurecer):
        rgb[escurecer] = (rgb[escurecer] * 85 + cor_sombra * 15 + 50) // 100
    # Micro-contraste do material: texturas já existentes ganham relevo.
    meio = material & ~iluminar & ~escurecer & ((maior - menor) > 20)
    destaque = meio & ((x * 3 + y * 5 + fase * 7) % 13 < 2)
    if np.any(destaque):
        rgb[destaque] = (rgb[destaque] * 92 + cor_luz * 8 + 50) // 100
    # Highlights distintos por frame dão leitura às asas, patas e botas,
    # mas NÃO mudam as poses nem a frequência do ciclo.
    if papel == 'skin' and estado in ESTADOS_GESTO:
        faixa = (y >= h * (.73 if estado in ('CORRER', 'POUSO') else .53))
        faixa &= y <= h * .91
        faixa &= x >= w * .23
        faixa &= x <= w * .78
        movimento = material & faixa & ((x + y * 2 + fase * 3) % 11 < 2)
        if np.any(movimento):
            rgb[movimento] = (rgb[movimento] * 78 + cor_luz * 22 + 50) // 100
    elif papel == 'inimigo':
        # Brilho que acompanha a sequência do atlas, não o contador global.
        faixa = material & (y > h * .28) & (y < h * .78)
        movimento = faixa & ((x * 2 + y + fase * 5) % 17 < 2)
        if np.any(movimento):
            rgb[movimento] = (rgb[movimento] * 80 + cor_luz * 20 + 50) // 100
    atualizado = np.uint8(np.clip(rgb, 0, 255))
    matriz = pygame.surfarray.pixels3d(quadro)
    matriz[:, :, :] = atualizado
    del matriz
    # Guardas fortes: a renderização deve ser 100% visual.
    assert quadro.get_size() == (w, h)
    assert np.array_equal(pygame.surfarray.array_alpha(quadro), alfa_antes)
    return quadro


def refinar_atlas_personagem(atlas, skin):
    """Reusa as mesmas superfícies e a mesma estrutura de animação."""
    if skin not in SKINS_ATIVAS:
        return atlas
    luz, sombra = PALETAS[skin]
    for estado, quadros in atlas.items():
        for i, quadro in enumerate(quadros):
            _polir_rgb(quadro, luz, sombra, i, 'skin', estado)
    return atlas


def refinar_quadro_inimigo(quadro, codigo, fase):
    """Refina a superfície fornecida pelo atlas v3221, in-place, sem cache extra."""
    bioma = ''.join(ch for ch in codigo if ch.isalpha()).upper()
    luz, sombra = PALETAS_BIOMA.get(bioma, PALETAS_BIOMA['C'])
    return _polir_rgb(quadro, luz, sombra, int(fase), 'inimigo')
