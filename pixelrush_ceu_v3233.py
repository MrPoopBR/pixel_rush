"""Plano K etapa 3: acabamento do gradiente EXISTENTE, sem criar outro céu.

Apenas o primeiro plano de fundo (y 0..239) fica mais profundo e com
horizonte cromático integrado, antes dos astros e nuvens originais.
Cache LRU limitado; em modo leve os 40 retângulos originais são idênticos.
Não toca nas artes, parallax, atmosferas/efeitos nem nos objetos jogáveis.
"""
from collections import OrderedDict
import pygame

W, H = 450, 800
ALTURA_CEU = 240
LIMITE_CACHE = 4
_CACHE = OrderedDict()
TONS = {
    'cidade': (119, 166, 226),
    'neve': (136, 190, 247),
    'deserto': (235, 168, 110),
    'floresta': (82, 153, 159),
    'vulcao': (201, 108, 120),
    'cidade_futurista': (104, 132, 235),
    'ilhas_celestes': (140, 190, 228),
}

def _mix(a, b, peso):
    p = max(0., min(1., float(peso)))
    return tuple(max(0, min(255, int(a[k]*(1-p)+b[k]*p))) for k in range(3))

def _preparar(cor, fase, noite, bioma):
    chave = (tuple((int(c)//4)*4 for c in cor), int(max(0.,min(1.,fase))*16),
             int(max(0.,min(1.,noite))*8), bioma)
    pronto = _CACHE.get(chave)
    if pronto is not None:
        _CACHE.move_to_end(chave)
        return pronto
    quant, fr, nr, b = chave
    f = fr/16.; n = nr/8.
    amanhecer = max(0., 1. - abs(f-.15)/.14)
    poente = max(0., 1. - abs(f-.745)/.13)
    crepusculo = max(amanhecer, poente)
    tema = TONS.get(b, TONS['cidade'])
    surface = pygame.Surface((W,ALTURA_CEU)).convert()
    for y in range(0, ALTURA_CEU, 4):
        # Reutiliza a mesma saturação e inclinação luminosa do céu clássico.
        fator = .74 + (y//20)*.0105
        original = tuple(max(0,min(255,int(v*fator))) for v in quant)
        topo = max(0., (220.-y)/220.)
        cromatico = _mix(original, tema, .12*topo)
        frio = _mix(cromatico, (34, 47, 93), n*.11*topo)
        horizonte = max(0., 1.-abs(y-179.)/145.)
        cor_final = _mix(frio, (255,170,114), crepusculo*.26*horizonte)
        # Um leve relevo atmosférico, sem texturas artificiais nem aleatoriedade.
        if n < .32:
            cor_final = _mix(cor_final,(214,227,245), .045*topo)
        pygame.draw.rect(surface,cor_final,(0,y,W,4))
    _CACHE[chave] = surface
    if len(_CACHE)>LIMITE_CACHE:
        _CACHE.popitem(last=False)
    return surface

def desenhar_gradiente(surf, cor_saturada, fase, noite, bioma, leve=False):
    """Substitui somente os 40 retângulos originais, sem passes extras.

    Modo leve é pixel a pixel equivalente ao código anterior.
    Normal usa 1 blit para céu superior e os 28 retângulos inalterados
    no panorama inferior. O cache não é gerado na corrida em modo leve.
    """
    if not leve:
        surf.blit(_preparar(cor_saturada,fase,noite,bioma),(0,0))
    for faixa in range(0 if leve else ALTURA_CEU//20,40):
        fator = .74 + faixa*.0105
        cor = tuple(max(0,min(255,int(cor_saturada[k]*fator))) for k in range(3))
        y0=faixa*(H//40)
        pygame.draw.rect(surf,cor,(0,y0,W,H//40+1))

def estatisticas_cache():
    return {'entradas':len(_CACHE),'limite':LIMITE_CACHE,
            'bytes_pixels':sum(s.get_pitch()*s.get_height() for s in _CACHE.values())}
