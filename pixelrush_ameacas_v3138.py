"""v3.138 — passe premium em todos os 28 perigos, sem alterar hitboxes.

Mantém movimento, colisão, tamanhos e spawn. Atua somente na imagem, usando
as artes já refinadas como base e elevando acabamento, contraste e coerência
com os cenários premium.
"""
import os
import pygame
import pixelrush_ameacas_v3127 as motor
from pixelrush_ameacas_v3134 import AMEACAS, POR_BIOMA, AmeacaBioma as Previous, imagem_ameaca as imagem_base
from pixelrush_ameacas_v3133 import escorpiao_frame  # mantido para compatibilidade
from pixelrush_ameacas_v3127 import risco_colisao_ativo

_CACHE = {}
BIOMA_BY_CODE = {code: biome for biome, codes in POR_BIOMA.items() for code in codes}
ACCENTS = {
    'cidade':      {'hi': (255, 204, 96), 'alt': (231, 156, 92), 'shade': (58, 56, 66)},
    'neve':        {'hi': (220, 240, 247), 'alt': (162, 202, 236), 'shade': (88, 107, 137)},
    'deserto':     {'hi': (250, 220, 134), 'alt': (226, 159, 104), 'shade': (115, 86, 71)},
    'vulcao':      {'hi': (255, 182, 86), 'alt': (255, 108, 61), 'shade': (79, 57, 62)},
    'floresta':    {'hi': (186, 224, 133), 'alt': (236, 167, 180), 'shade': (58, 91, 74)},
    'cidade_futurista': {'hi': (112, 241, 247), 'alt': (246, 108, 223), 'shade': (49, 62, 96)},
    'ilhas_celestes':   {'hi': (226, 244, 250), 'alt': (191, 130, 255), 'shade': (118, 133, 159)},
}


def _outline(img, cor=(18, 23, 31, 255)):
    mask = pygame.mask.from_surface(img)
    base = mask.to_surface(setcolor=cor, unsetcolor=(0, 0, 0, 0)).convert_alpha()
    out = pygame.Surface(img.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)):
        out.blit(base, (dx, dy))
    out.blit(img, (0, 0))
    return out


def _shade_bottom(img, col, alpha=32):
    w, h = img.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h // 2, h):
        a = int(alpha * (yy - h // 2) / max(1, h // 2))
        pygame.draw.line(overlay, (*col, a), (0, yy), (w, yy))
    img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)


def _top_highlight(img, colors):
    w, h = img.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(0, max(2, h // 3)):
        a = int(36 * (1.0 - yy / max(1, h // 3)))
        pygame.draw.line(overlay, (*colors['hi'], a), (0, yy), (w, yy))
    img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _draw_shadow(img):
    w, h = img.get_size()
    pygame.draw.ellipse(img, (0, 0, 0, 38), (max(0, w // 8), h - 6, max(8, w * 3 // 4), 4))


def _add_material_specks(img, colors, seed, count=10):
    rng = pygame.time.get_ticks  # placeholder? nope
    import random
    rr = random.Random(seed)
    w, h = img.get_size()
    for _ in range(count):
        x = rr.randrange(1, max(2, w - 2))
        y = rr.randrange(1, max(2, h - 4))
        col = colors['alt'] if (_ % 2) else colors['hi']
        pygame.draw.rect(img, col, (x, y, 1, 1))


def _bird_eye(img, x, y):
    pygame.draw.rect(img, (249, 244, 233), (x, y, 4, 4))
    pygame.draw.rect(img, (26, 28, 35), (x + 1, y + 1, 2, 2))


def _premiumize(code, base, phase):
    img = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    img.blit(base, (0, 0))
    biome = BIOMA_BY_CODE[code]
    colors = ACCENTS[biome]
    w, h = img.get_size()
    _draw_shadow(img)
    _shade_bottom(img, colors['shade'], alpha=24 if h < 40 else 34)
    _top_highlight(img, colors)

    # Code-specific pass, always image-only.
    if code in ('C1', 'N1', 'D1', 'V1', 'F1', 'CF1', 'IC1'):
        # bichos baixos/terrestres: brilho de olhos, placas e contorno interno.
        _add_material_specks(img, colors, hash((code, phase)) & 0xFFFF, count=8)
        pygame.draw.line(img, colors['hi'], (w // 4, h // 3), (w // 4 + 4, h // 3), 1)
        pygame.draw.line(img, colors['alt'], (w // 2, h // 2), (w // 2 + 3, h // 2), 1)
    elif code in ('C2', 'N2', 'F2', 'V2', 'CF2', 'IC2'):
        _bird_eye(img, max(4, w // 2 - 2), max(4, h // 3))
        pygame.draw.line(img, colors['hi'], (w // 4, h // 2), (w * 3 // 4, h // 2), 1)
        _add_material_specks(img, colors, hash((code, phase)) & 0xFFFF, count=6)
    elif code in ('C3', 'C4', 'N3', 'D3', 'D4', 'V3', 'CF3', 'IC3'):
        # obstáculos fixos: mais textura de material e arestas claras.
        for yy in range(4, h - 4, max(4, h // 6)):
            pygame.draw.line(img, colors['hi'], (4, yy), (min(w - 4, 10), yy), 1)
        _add_material_specks(img, colors, hash((code, phase)) & 0xFFFF, count=14)
    elif code in ('N4', 'F3'):
        # troncos rolantes/ocos.
        for x in range(6, w - 6, 10):
            pygame.draw.line(img, colors['alt'], (x, h // 2), (x + 4, h // 2 + 1), 1)
        _add_material_specks(img, colors, hash((code, phase)) & 0xFFFF, count=8)
    elif code in ('F4', 'CF4', 'IC4'):
        # obstáculos altos: realçar borda inferior e pontos de leitura.
        pygame.draw.line(img, colors['hi'], (6, h // 2), (w - 6, h // 2), 1)
        for x in range(10, w - 10, 16):
            pygame.draw.rect(img, colors['alt'], (x, max(3, h // 3), 2, 2))
    elif code == 'V4':
        # gêiser/vapor.
        for y in range(6, h - 8, 10):
            pygame.draw.line(img, colors['hi'], (w // 2 - 3, y), (w // 2 + 3, y - 2), 1)
        _add_material_specks(img, colors, hash((code, phase)) & 0xFFFF, count=6)
    else:
        _add_material_specks(img, colors, hash((code, phase)) & 0xFFFF, count=8)

    return _outline(img)


def imagem_ameaca(codigo, fase=0):
    if os.environ.get('PIXELRUSH_ARTE_CLASSICA') == '1':
        return imagem_base(codigo, fase)
    chave = (codigo, int(fase) % 3)
    if chave not in _CACHE:
        base = imagem_base(codigo, fase).convert_alpha()
        premium = _premiumize(codigo, base, int(fase) % 3)
        # Mantém tamanho final exato.
        if premium.get_size() != base.get_size():
            premium = pygame.transform.scale(premium, base.get_size()).convert_alpha()
        _CACHE[chave] = premium
    return _CACHE[chave]


motor.imagem_ameaca = imagem_ameaca


class AmeacaBioma(Previous):
    pass
