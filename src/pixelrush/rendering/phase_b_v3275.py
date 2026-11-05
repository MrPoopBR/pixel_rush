"""Detalhes de profundidade 2.5D v3.275, somente renderização.

Reutiliza integralmente os indicadores e silhuetas anteriores. Acima da faixa
jogável, motivos discretos e animados apenas pelo deslocamento já existente.
Não usa random, timers, física, eventos ou dados de save.
"""
from __future__ import annotations
from functools import lru_cache
import pygame
from pixelrush_fase_b_visuais_v3274 import (
    desenhar_profundidade_bioma as _profundidade_anterior,
    desenhar_legibilidade_jetpack,
    desenhar_legibilidade_corredor,
    desenhar_alerta_moveis,
    _CORES,
)

@lru_cache(maxsize=7)
def _detalhes_distantes(bioma):
    if bioma not in _CORES:raise ValueError('Bioma desconhecido')
    cor=_CORES[bioma]
    camada=pygame.Surface((600,64),pygame.SRCALPHA)
    linha=(*cor,28);ponto=(*cor,38)
    for i in range(9):
        x=27+i*69
        if bioma=='cidade':
            pygame.draw.rect(camada,linha,(x,23+i%3*5,13,32),1)
            pygame.draw.line(camada,ponto,(x+4,27+i%3*5),(x+4,34+i%3*5),1)
        elif bioma=='neve':
            pygame.draw.lines(camada,linha,False,((x-15,49),(x,20+i%3*6),(x+16,49)),1)
        elif bioma=='deserto':
            pygame.draw.arc(camada,linha,(x-24,34+i%3*5,54,25),3.3,6.0,1)
        elif bioma=='floresta':
            pygame.draw.line(camada,linha,(x,55),(x,33+i%4*4),1)
            pygame.draw.ellipse(camada,ponto,(x-11,24+i%4*4,23,20),1)
        elif bioma=='vulcao':
            pygame.draw.lines(camada,linha,False,((x-18,53),(x,24+i%3*6),(x+18,53)),1)
            pygame.draw.circle(camada,ponto,(x+12,12+i%4*4),2)
        elif bioma=='cidade_futurista':
            pygame.draw.rect(camada,linha,(x-4,16+i%4*4,10,41),1)
            pygame.draw.line(camada,ponto,(x+1,12+i%4*4),(x+1,18+i%4*4),1)
        elif bioma=='ilhas_celestes':
            pygame.draw.ellipse(camada,linha,(x-21,24+i%3*5,44,13),1)
            pygame.draw.line(camada,ponto,(x,37+i%3*5),(x+4,48+i%3*5),1)
    return camada

@lru_cache(maxsize=35)
def _detalhes_noite(bioma,grau):
    tex=_detalhes_distantes(bioma).copy()
    tex.set_alpha(round(255*(1-.63*grau/4)))
    return tex

def desenhar_profundidade_bioma(superficie,bioma,deslocamento,peso_noite=0,leve=False):
    aplicado=_profundidade_anterior(superficie,bioma,deslocamento,peso_noite,leve)
    if not aplicado or leve or bioma not in _CORES:return aplicado
    noite=max(0.,min(1.,float(peso_noite)))
    textura=_detalhes_noite(bioma,round(noite*4)) if noite else _detalhes_distantes(bioma)
    # 335..399: 3a velocidade de parallax; sem pixels abaixo de y=400.
    largura=superficie.get_width()
    x=(-int(float(deslocamento)*.094))%600-600
    for xx in range(x,largura,600):
        superficie.blit(textura,(xx,335))
    return True
