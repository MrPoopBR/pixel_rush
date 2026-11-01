"""Acabamentos visuais v3.274: sete biomas, perigos e continuidade.

Extensão dos efeitos v3.273, sem novos timers, RNG, física ou spawns.
"""
import math
import pygame
from pixelrush_fase_b_visuais_v3273 import (
    desenhar_profundidade_bioma as _profundidade,
    desenhar_legibilidade_jetpack as _jetpack,
    desenhar_legibilidade_corredor as _corredor,
    desenhar_alerta_moveis as _moveis,
)

_CORES = {
    'cidade': (74, 187, 221), 'neve': (156, 222, 244),
    'deserto': (235, 188, 94), 'floresta': (111, 211, 132),
    'vulcao': (245, 112, 76), 'cidade_futurista': (130, 240, 220),
    'ilhas_celestes': (189, 214, 254),
}

def desenhar_profundidade_bioma(superficie, bioma, deslocamento, peso_noite=0, leve=False):
    ok=_profundidade(superficie,bioma,deslocamento,peso_noite,leve)
    if not ok or leve or bioma not in _CORES:return ok
    # Reflexos baixíssimos de fundo: menos de 1% da área, só no plano distante.
    cor=_CORES[bioma]; intensidade=max(.15,.50-.28*max(0.,min(1.,float(peso_noite))))
    cor=tuple(int(v*intensidade+22*(1-intensidade)) for v in cor)
    w=superficie.get_width(); fase=int(float(deslocamento)*.037)
    for i in range(7):
        x=(i*111-fase)%max(1,w)
        y=283+(i%3)*14
        pygame.draw.line(superficie,cor,(x,y),(x+9,y-2),1)
    return ok

def desenhar_legibilidade_jetpack(superficie,gate,frame=0,leve=False):
    resultado=_jetpack(superficie,gate,frame,leve)
    if resultado and not leve:
        # Três marcas numéricas: faixas reconhecíveis independentemente de cor.
        font=pygame.font.Font(None,18)
        for indice in range(3):
            rotulo=font.render(str(3-indice),True,(240,243,229))
            superficie.blit(rotulo,(superficie.get_width()-60,274+indice*20))
    return resultado

def desenhar_legibilidade_corredor(superficie,faixas,frame=0,leve=False):
    resultado=_corredor(superficie,faixas,frame,leve)
    if resultado and not leve:
        for f in faixas:
            if int(f.get('warning',0))<=0:continue
            x=int(f['x']);y=int(f['gap_y'])
            if 6<=x<superficie.get_width()-12 and 192<=y<=superficie.get_height()-36:
                pygame.draw.line(superficie,(231,244,227),(x-4,y),(x+6,y),2)
    return resultado

def desenhar_alerta_moveis(superficie,obstaculos,jogador,frame=0,leve=False):
    n=_moveis(superficie,obstaculos,jogador,frame,leve)
    if n and not leve and jogador is not None:
        # Sinal neutro persistente próximo ao chão: não prevê colisões.
        x=max(15,min(superficie.get_width()-15,jogador.rect.right+74))
        y=max(240,min(superficie.get_height()-72,jogador.rect.bottom-135))
        pygame.draw.line(superficie,(244,234,164),(x-9,y),(x+9,y),2)
        pygame.draw.circle(superficie,(244,234,164),(x,y),3)
    return n
