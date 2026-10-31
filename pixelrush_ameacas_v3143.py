"""v3.143 — passe extra nas ameaças da Floresta, preservando hitboxes e movimento."""
import os, random, pygame
import pixelrush_ameacas_v3127 as motor
from pixelrush_ameacas_v3141 import (
    AMEACAS, POR_BIOMA, escorpiao_frame, AmeacaBioma as Previous,
    imagem_ameaca as imagem_base
)

_CACHE = {}

def _outline(img, cor=(14,20,23,255)):
    mask = pygame.mask.from_surface(img)
    base = mask.to_surface(setcolor=cor, unsetcolor=(0,0,0,0)).convert_alpha()
    out = pygame.Surface(img.get_size(), pygame.SRCALPHA)
    for dx,dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)):
        out.blit(base,(dx,dy))
    out.blit(img,(0,0))
    return out

def _specks(img, seed, cols, n=12):
    rr=random.Random(seed); w,h=img.get_size()
    for i in range(n):
        x=rr.randrange(1,max(2,w-2)); y=rr.randrange(1,max(2,h-2))
        pygame.draw.rect(img, cols[i % len(cols)], (x,y,1,1))

def _forest_pass(code, base, phase):
    img=pygame.Surface(base.get_size(), pygame.SRCALPHA); img.blit(base,(0,0))
    w,h=img.get_size()
    # brilho/contraste geral
    for yy in range(max(2,h//3)):
        a=int(28*(1-yy/max(1,h//3)))
        pygame.draw.line(img,(181,224,123,a),(0,yy),(w,yy))
    for yy in range(h//2,h):
        a=int(24*(yy-h//2)/max(1,h//2))
        pygame.draw.line(img,(24,44,40,a),(0,yy),(w,yy))
    if code=='F1':
        # felino/jaguar: manchas, olhos e barriga mais legíveis
        _specks(img, hash((code,phase)) & 0xffff, [(95,143,85),(182,213,121),(218,171,112)], 16)
        pygame.draw.rect(img,(247,240,209),(max(3,w//3),max(3,h//3+2),5,3))
        pygame.draw.rect(img,(28,30,34),(max(4,w//3+1),max(4,h//3+3),2,1))
        for x in range(5,w-5,7): pygame.draw.line(img,(74,108,67),(x,h//2),(x+1,h//2+1),1)
    elif code=='F2':
        # inimigo aéreo: asas mais legíveis e brilho nos olhos
        eye=(max(4,w//2-2), max(4,h//3))
        pygame.draw.rect(img,(251,246,230),(eye[0],eye[1],4,4)); pygame.draw.rect(img,(20,24,28),(eye[0]+1,eye[1]+1,2,2))
        pygame.draw.line(img,(188,225,130),(w//5,h//2),(w*4//5,h//2),1)
        pygame.draw.line(img,(122,182,103),(w//4,h//2+3),(w*3//4,h//2+2),1)
        _specks(img, hash((code,phase)) & 0xffff, [(99,158,96),(202,230,146)], 10)
    elif code=='F3':
        # tronco rolante: anéis, casca, musgo e folhas secas
        for x in range(6,w-7,8): pygame.draw.line(img,(145,103,77),(x,h//2),(x+3,h//2+1),1)
        pygame.draw.line(img,(90,149,81),(5,h//3),(w-6,h//3),1)
        pygame.draw.line(img,(176,219,117),(7,h//3-2),(w-10,h//3-2),1)
        _specks(img, hash((code,phase)) & 0xffff, [(110,80,60),(168,124,92),(88,145,82)], 18)
    elif code=='F4':
        # obstáculo alto: cipós e pontas destacadas
        pygame.draw.line(img,(181,225,126),(6,h//2),(w-6,h//2),1)
        for y in range(7,h-8,11):
            x=w//2 + ((y//11)%2)*3 - 2
            pygame.draw.line(img,(96,151,86),(x,y),(x+2,y+6),1)
        for x in range(9,w-9,14): pygame.draw.rect(img,(231,176,135),(x,max(3,h//3),2,2))
        _specks(img, hash((code,phase)) & 0xffff, [(80,121,78),(132,183,102),(188,223,131)], 14)
    return _outline(img)

def imagem_ameaca(codigo, fase=0):
    if os.environ.get('PIXELRUSH_ARTE_CLASSICA') == '1':
        return imagem_base(codigo, fase)
    phase=int(fase)%3
    key=(codigo, phase)
    if key not in _CACHE:
        base=imagem_base(codigo, fase).convert_alpha()
        if codigo.startswith('F'):
            _CACHE[key]=_forest_pass(codigo, base, phase)
        else:
            _CACHE[key]=base
    return _CACHE[key]

motor.imagem_ameaca = imagem_ameaca

class AmeacaBioma(Previous):
    pass
