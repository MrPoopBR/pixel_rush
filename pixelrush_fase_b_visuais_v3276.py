"""v3.276.0 — atmosfera contextual de clima/horário por bioma.

Camada 100% visual, cacheada, no céu entre y=405 e 463. Nenhuma
mutação de RNG, clima, timers, physics ou estado de progresso.
"""
from __future__ import annotations
from functools import lru_cache
import pygame
from pixelrush_fase_b_visuais_v3275 import (
    desenhar_profundidade_bioma as _anterior,
    desenhar_legibilidade_jetpack,
    desenhar_legibilidade_corredor,
    desenhar_alerta_moveis,
    _CORES,
)

CLIMAS_CHUVA = frozenset(('chuva','tempestade','chuva_acida'))
CLIMAS_VENTO = frozenset(('vento','vento_folhas','vento_neon','cinzas','polen'))

def _tipo_clima(tipo):
    if tipo in CLIMAS_CHUVA:return 'chuva'
    if tipo in CLIMAS_VENTO:return 'vento'
    if tipo=='neve':return 'neve'
    return 'limpo'

@lru_cache(maxsize=7*4*5)
def _textura_contextual(bioma,condicao,grau_noite):
    if bioma not in _CORES:raise ValueError('Bioma desconhecido: '+str(bioma))
    cor=_CORES[bioma]
    alfa=max(8,34-5*int(grau_noite))
    s=pygame.Surface((600,57),pygame.SRCALPHA)
    a=(*cor,alfa)
    b=(220,235,242,max(7,alfa-7)) if condicao=='neve' else (*cor,max(5,alfa-11))
    for i in range(12):
        x=23+i*53;y=9+(i*7)%29
        if condicao=='chuva':
            pygame.draw.line(s,b,(x,y),(x-5,y+12),1)
        elif condicao=='neve':
            pygame.draw.line(s,b,(x-3,y),(x+3,y),1)
            pygame.draw.line(s,b,(x,y-3),(x,y+3),1)
        elif condicao=='vento':
            pygame.draw.arc(s,a,(x-14,y,28,10),3.4,6.0,1)
        else:
            # Distintas leituras por bioma, inclusive no céu limpo.
            if bioma in ('cidade','cidade_futurista'):
                pygame.draw.line(s,a,(x,y+12),(x,y-2),1)
            elif bioma in ('deserto','vulcao'):
                pygame.draw.arc(s,a,(x-12,y,26,14),3.2,6.1,1)
            elif bioma=='floresta':
                pygame.draw.ellipse(s,a,(x-6,y,12,7),1)
            elif bioma=='neve':
                pygame.draw.line(s,a,(x-8,y+5),(x,y-3),1)
            else:
                pygame.draw.ellipse(s,a,(x-9,y,19,5),1)
    return s

def desenhar_profundidade_bioma(superficie,bioma,deslocamento,peso_noite=0,leve=False,clima_tipo='limpo'):
    resultado=_anterior(superficie,bioma,deslocamento,peso_noite,leve)
    if not resultado or leve or bioma not in _CORES:return resultado
    condicao=_tipo_clima(clima_tipo)
    grau=max(0,min(4,round(float(peso_noite)*4)))
    tex=_textura_contextual(bioma,condicao,grau)
    largura=superficie.get_width()
    x=(-int(float(deslocamento)*.078))%600-600
    for xx in range(x,largura,600):superficie.blit(tex,(xx,405))
    return True
