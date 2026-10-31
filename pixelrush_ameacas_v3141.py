"""v3.141 — passe premium focado nas ameaças da Floresta.

Refina apenas F1/F2/F3/F4, preservando tamanho, hitboxes e movimento.
Os demais perigos permanecem exatamente como estavam na v3.140.
"""
import os
import random
import pygame
import pixelrush_ameacas_v3127 as motor
from pixelrush_ameacas_v3138 import (
    AMEACAS, POR_BIOMA, AmeacaBioma as Previous,
    imagem_ameaca as imagem_base, escorpiao_frame
)

_CACHE = {}


def _outline(img, cor=(15, 21, 24, 255)):
    mask = pygame.mask.from_surface(img)
    base = mask.to_surface(setcolor=cor, unsetcolor=(0, 0, 0, 0)).convert_alpha()
    out = pygame.Surface(img.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)):
        out.blit(base, (dx, dy))
    out.blit(img, (0, 0))
    return out


def _shade(img, top=(177, 217, 119), mid=(88, 145, 87), deep=(37, 73, 58)):
    w, h = img.get_size()
    # brilho superior
    glow = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(max(2, h // 3)):
        a = int(34 * (1.0 - yy / max(1, h // 3)))
        pygame.draw.line(glow, (*top, a), (0, yy), (w, yy))
    img.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # sombra inferior
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h // 2, h):
        a = int(28 * (yy - h // 2) / max(1, h // 2))
        pygame.draw.line(sh, (*deep, a), (0, yy), (w, yy))
    img.blit(sh, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    pygame.draw.ellipse(img, (0, 0, 0, 34), (max(0, w // 7), h - 6, max(8, w * 3 // 4), 4))


def _specks(img, seed, cols):
    rr = random.Random(seed)
    w, h = img.get_size()
    for i in range(max(6, (w*h)//120)):
        x = rr.randrange(1, max(2, w-2))
        y = rr.randrange(1, max(2, h-3))
        col = cols[i % len(cols)]
        pygame.draw.rect(img, col, (x, y, 1, 1))


def _refine_forest(code, base, phase):
    img = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    img.blit(base, (0, 0))
    w, h = img.get_size()
    _shade(img)
    # passe específico por tipo
    if code == 'F1':
        # jaguar/animal baixo: olhos, manchas e faixa de leitura dorsal.
        for x in range(max(4, w//5), min(w-4, w*4//5), 7):
            pygame.draw.line(img, (172, 214, 116), (x, h//3), (x+2, h//3), 1)
        pygame.draw.rect(img, (250, 238, 196), (max(3,w//3), max(3,h//3), 4, 3))
        pygame.draw.rect(img, (27, 29, 31), (max(4,w//3+1), max(4,h//3+1), 2, 1))
        _specks(img, hash((code, phase)) & 0xFFFF, [(71,116,68),(151,188,102),(224,170,115)])
    elif code == 'F2':
        # ave/inimigo aéreo: olho, bico/asa com highlight.
        eye_x = max(4, w//2-2)
        eye_y = max(4, h//3)
        pygame.draw.rect(img, (248, 244, 226), (eye_x, eye_y, 4, 4))
        pygame.draw.rect(img, (26, 28, 33), (eye_x+1, eye_y+1, 2, 2))
        pygame.draw.line(img, (193, 224, 133), (w//4, h//2), (w*3//4, h//2), 1)
        pygame.draw.line(img, (120, 171, 94), (w//4, h//2+3), (w*3//4, h//2+2), 1)
        _specks(img, hash((code, phase)) & 0xFFFF, [(100,155,92),(200,229,145)])
    elif code == 'F3':
        # tronco rolante: anéis, musgo e volume.
        for x in range(6, w-6, 8):
            pygame.draw.line(img, (148, 104, 79), (x, h//2), (x+3, h//2+1), 1)
        pygame.draw.line(img, (96, 152, 86), (5, h//3), (w-6, h//3), 1)
        pygame.draw.line(img, (177, 219, 116), (7, h//3-2), (w-10, h//3-2), 1)
        _specks(img, hash((code, phase)) & 0xFFFF, [(111,81,60),(168,124,92),(91,145,83)])
    elif code == 'F4':
        # obstáculo alto: borda viva, cipós e brilho sutil.
        pygame.draw.line(img, (179, 223, 125), (6, h//2), (w-6, h//2), 1)
        for y in range(7, h-8, 11):
            x = w//2 + ((y//11)%2)*3 - 2
            pygame.draw.line(img, (97, 151, 86), (x, y), (x+2, y+6), 1)
        for x in range(9, w-9, 15):
            pygame.draw.rect(img, (229, 172, 132), (x, max(3, h//3), 2, 2))
        _specks(img, hash((code, phase)) & 0xFFFF, [(79,120,77),(133,183,102),(187,222,130)])
    return _outline(img)


def imagem_ameaca(codigo, fase=0):
    if os.environ.get('PIXELRUSH_ARTE_CLASSICA') == '1':
        return imagem_base(codigo, fase)
    phase = int(fase) % 3
    chave = (codigo, phase)
    if chave not in _CACHE:
        base = imagem_base(codigo, fase).convert_alpha()
        if codigo.startswith('F'):
            novo = _refine_forest(codigo, base, phase)
            if novo.get_size() != base.get_size():
                novo = pygame.transform.scale(novo, base.get_size()).convert_alpha()
            _CACHE[chave] = novo
        else:
            _CACHE[chave] = base
    return _CACHE[chave]


motor.imagem_ameaca = imagem_ameaca


class AmeacaBioma(Previous):
    pass
