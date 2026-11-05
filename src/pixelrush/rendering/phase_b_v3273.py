"""Fase B v3.273: profundidade ambiental animada e avisos adicionais de leitura.

Somente renderização. Os objetos e seus dados permanecem intocados, sem RNG.
A visão evita prever colisão, latência ou uma rota supostamente segura.
"""
from __future__ import annotations
from functools import lru_cache
import math
import pygame
from pixelrush_fase_b_visuais_v3272 import (
    PALETAS, desenhar_profundidade_bioma as _profundidade_existente,
    desenhar_legibilidade_jetpack as _jetpack_existente,
    desenhar_legibilidade_corredor as _corredor_existente,
)

@lru_cache(maxsize=7)
def _ambiente_segundo_plano(bioma):
    """Detalhes ambientais em RGBA cacheados e únicos por bioma."""
    if bioma not in PALETAS:
        raise ValueError('Bioma inválido')
    cor=PALETAS[bioma]
    palco=pygame.Surface((720,146),pygame.SRCALPHA)
    suave=(*cor,24)
    leve=(*cor,36)
    for i in range(10):
        x=42+i*74
        if bioma=='cidade':
            pygame.draw.line(palco,suave,(x,127),(x,65+i%3*11),2)
            pygame.draw.circle(palco,leve,(x,65+i%3*11),5,1)
        elif bioma=='neve':
            pygame.draw.line(palco,leve,(x-14,116),(x,95-i%4*7),2)
            pygame.draw.line(palco,suave,(x,95-i%4*7),(x+14,116),1)
        elif bioma=='deserto':
            pygame.draw.arc(palco,leve,(x-27,83+i%3*8,71,34),3.1,5.9,2)
        elif bioma=='floresta':
            pygame.draw.circle(palco,suave,(x,74+i%3*8),10+i%3*3,1)
            pygame.draw.line(palco,leve,(x,130),(x,84+i%3*8),2)
        elif bioma=='vulcao':
            pygame.draw.line(palco,leve,(x-15,114),(x,90+i%4*4),2)
            pygame.draw.line(palco,suave,(x,90+i%4*4),(x+16,114),2)
            pygame.draw.circle(palco,leve,(x+5,62+i%3*9),2)
        elif bioma=='cidade_futurista':
            pygame.draw.rect(palco,suave,(x-8,62+i%3*9,16,57),2)
            pygame.draw.circle(palco,leve,(x,57+i%3*9),4,1)
        elif bioma=='ilhas_celestes':
            pygame.draw.ellipse(palco,suave,(x-20,75+i%3*10,55,12),2)
            pygame.draw.line(palco,leve,(x-4,90+i%3*10),(x+4,110+i%3*10),1)
    return palco

@lru_cache(maxsize=28)
def _ambiente_noturno(bioma,passo):
    img=_ambiente_segundo_plano(bioma).copy()
    img.set_alpha(round(255*(1-0.65*passo/4)))
    return img

def desenhar_profundidade_bioma(superficie, bioma, deslocamento, peso_noite=0.0, leve=False):
    """Preserva a camada original e acrescenta motivo ambiental de velocidade distinta.

    A animação depende exclusivamente do deslocamento que o jogo já expõe.
    Sem fase global, eventos ou atualização de objetos.
    """
    ok=_profundidade_existente(superficie,bioma,deslocamento,peso_noite,leve)
    if not ok:return False
    noite=max(0.,min(1.,float(peso_noite)))
    tex=_ambiente_noturno(bioma,round(noite*4)) if noite else _ambiente_segundo_plano(bioma)
    # Camada mais distante e suave; nunca ocupa HUD, piso, área do tutorial.
    largura=superficie.get_width()
    x=(-int(float(deslocamento)*0.062))%720-720
    for xx in range(x,largura,720):
        superficie.blit(tex,(xx,262))
    return True

def desenhar_legibilidade_jetpack(superficie,gate,frame=0,leve=False):
    """Acento redundante no aviso já existente; não inventa cronômetro."""
    resultado=_jetpack_existente(superficie,gate,frame,leve)
    if not resultado or leve:return resultado
    w=superficie.get_width()
    x=w-89
    # Triângulo + risco, legível sem depender de cor nem de texto na imagem.
    pygame.draw.polygon(superficie,(238,242,222),[(x+9,258),(x+18,242),(x+27,258)],2)
    pygame.draw.line(superficie,(238,242,222),(x+18,248),(x+18,253),2)
    pygame.draw.circle(superficie,(238,242,222),(x+18,256),1)
    # Rótulos de faixa neutros; não sugerem ação de controle.
    for idx in range(3):
        yy=274+idx*20
        pygame.draw.rect(superficie,(17,37,52),(x+2,yy,5,10),border_radius=1)
    return resultado

def desenhar_legibilidade_corredor(superficie,faixas,frame=0,leve=False):
    resultado=_corredor_existente(superficie,faixas,frame,leve)
    if not resultado or leve:return resultado
    # Marcas de borda de corredor, só quando o laser está avisando.
    w,h=superficie.get_size()
    for faixa in faixas:
        if int(faixa.get('warning',0))<=0:continue
        x=int(faixa['x']);centro=int(faixa['gap_y'])
        if x<0 or x>w or centro<180 or centro>h-25:continue
        pygame.draw.line(superficie,(211,244,223),(x+11,centro-14),(x+11,centro+14),2)
        pygame.draw.line(superficie,(211,244,223),(x+7,centro-11),(x+11,centro-14),2)
        pygame.draw.line(superficie,(211,244,223),(x+7,centro+11),(x+11,centro+14),2)
    return resultado

def desenhar_alerta_moveis(superficie,obstaculos,jogador,frame=0,leve=False):
    """Um ícone de alerta acima de móveis PRÓXIMOS, nunca previsão de colisão.

    Lê somente tipo_movel e rect, já pertencentes aos objetos reais. Não é
    aplicado a obstáculos terrestres estáticos, lasers ou efeitos decorativos.
    """
    if leve or jogador is None or not hasattr(jogador,'rect'):return 0
    jp=jogador.rect
    feitos=0
    for perigo in obstaculos:
        if not getattr(perigo,'tipo_movel',None) or not hasattr(perigo,'rect'):
            continue
        rect=perigo.rect
        distancia=rect.left-jp.right
        if not (16<=distancia<=220) or not (8<rect.centerx<superficie.get_width()-8):
            continue
        x=max(18,min(superficie.get_width()-18,rect.centerx))
        y=max(245,min(superficie.get_height()-30,rect.top-20))
        pygame.draw.polygon(superficie,(21,46,63),[(x,y-12),(x-13,y+8),(x+13,y+8)])
        pygame.draw.polygon(superficie,(242,211,123),[(x,y-12),(x-13,y+8),(x+13,y+8)],2)
        pygame.draw.line(superficie,(245,242,220),(x,y-5),(x,y+1),2)
        pygame.draw.circle(superficie,(245,242,220),(x,y+4),1)
        feitos+=1
        if feitos>=2:break
    return feitos
