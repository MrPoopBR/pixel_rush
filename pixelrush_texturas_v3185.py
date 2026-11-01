"""Plano F / v3.185.0 — microtexturas de materiais EXISTENTES.

Arte pré-processada na carga, sem passes por frame, novas entidades ou
modificações de alfa/geometria. Intencionalmente não desenha decoração solta.
"""
import numpy as np
import pygame


# Intensidades moderadas: o desenho original e a luz da v3.177 predominam.
INTENSIDADE = {
    'cidade': (4, 7, 9),
    'neve': (4, 7, 9),
    'deserto': (5, 8, 11),
    'floresta': (4, 7, 10),
    'vulcao': (4, 7, 10),
    'cidade_futurista': (4, 7, 9),
    'ilhas_celestes': (4, 7, 9),
}


def _material(bioma, rgb):
    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)
    lum = (3 * r + 5 * g + 2 * b) // 10
    base = (lum > 56) & (lum < 228)
    if bioma == 'cidade':
        return base & (abs(r-g) < 62) & (abs(g-b) < 65)
    if bioma == 'neve':
        return base & (b >= r - 24) & (g >= r - 28) & (b > 104)
    if bioma == 'deserto':
        return base & (r > g + 12) & (g > b - 8) & (r > 105)
    if bioma == 'floresta':
        verde = (g > r + 14) & (g > b + 7)
        madeira = (r > g + 17) & (g > b - 12) & (r < 175)
        return base & (verde | madeira)
    if bioma == 'vulcao':
        rocha = (lum < 154) & (abs(r-b) < 64)
        brasa = (r > g + 21) & (g > b + 5) & (r > 100)
        return base & (rocha | brasa)
    if bioma == 'cidade_futurista':
        return base & (b > r + 13) & (g > r - 14) & (b < 222)
    if bioma == 'ilhas_celestes':
        return base & (g > r - 15) & (b > r - 21) & (g > 86)
    return np.zeros(lum.shape, dtype=np.bool_)


def refinar_textura(imagem, bioma, plano='mid', indice=0):
    """Tonaliza trechos INTERNOS de material liso; devolve delta/sumário.

    Restrições: somente pixels 100% opacos, margem 15px intacta, região
    homogênea de 5 pixels, mudanças de no máximo 11/255, sem nova superfície.
    A fase depende do índice do chunk e não do frame (zero custo na corrida).
    """
    if (bioma not in INTENSIDADE or not (imagem.get_flags() & pygame.SRCALPHA)
            or imagem.get_width() < 48 or imagem.get_height() < 48):
        return None, 0
    src = pygame.surfarray.array3d(imagem)
    alpha = pygame.surfarray.array_alpha(imagem)
    w, h = alpha.shape
    rgba = src.astype(np.int16)
    x, y = np.indices((w, h), dtype=np.int16)
    # Somente pigmento que já ocupa um plano sólido, sem texturizar bordas.
    integro = _material(bioma, src) & (alpha == 255)
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        vizinho = np.roll(rgba, (dx, dy), axis=(0, 1))
        dif = np.max(np.abs(rgba-vizinho), axis=2)
        integro &= (np.roll(alpha, (dx, dy), axis=(0, 1)) == 255) & (dif <= 30)
    integro[:15] = False
    integro[-15:] = False
    integro[:, :8] = False
    integro[:, -8:] = False
    # Filigranas/estratos embutidos no material, não ruído aleatório solto.
    fase = (indice * 7 + (2 if plano == 'mid' else 5))
    if bioma in ('deserto', 'vulcao'):
        trama = (x // 7 + 3 * (y // 3) + fase) % 13
    elif bioma in ('floresta', 'ilhas_celestes'):
        trama = (2 * (x // 4) + y // 5 + (x+y)//17 + fase) % 13
    else:
        trama = (x // 3 + 2 * (y // 6) + fase) % 13
    # 3 classes de pincelada: facetamento escuro, luz suave, zona neutra.
    forca = INTENSIDADE[bioma][('far', 'mid', 'near').index(plano)]
    delta = np.zeros((w, h), dtype=np.int16)
    delta[integro & ((trama == 0) | (trama == 1))] = forca
    delta[integro & ((trama == 6) | (trama == 7))] = -forca
    pixels = int(np.count_nonzero(delta))
    if not pixels:
        return None, 0
    saida = np.clip(rgba + delta[:, :, None], 0, 255).astype(np.uint8)
    mapa = pygame.surfarray.pixels3d(imagem)
    mapa[:] = saida
    del mapa
    # Delta int8 pequeno para propagar exclusivamente à paleta noturna já gerada.
    return delta.astype(np.int8), pixels


def aplicar_texturas_cidade(cidade):
    """Reusa superfícies existentes do CityPilot, sem tocar nos outros mapas."""
    if getattr(cidade, '_texturas_3185', False):
        return cidade
    totais = {'far': 0, 'mid': 0, 'near': 0}
    vistas = set()
    for camada in cidade.layers:
        if camada.foreground or camada.name not in ('mid', 'near'):
            continue
        for i, variante in enumerate(camada.variants):
            imagem = variante.image
            if id(imagem) in vistas:
                continue
            vistas.add(id(imagem))
            _, qtd = refinar_textura(imagem, 'cidade', camada.name, i)
            totais[camada.name] += qtd
    cidade._texturas_3185 = True
    cidade._estatistica_texturas_3185 = totais
    return cidade
