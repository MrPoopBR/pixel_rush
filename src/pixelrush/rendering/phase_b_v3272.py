"""Fase B v3.272: acabamentos VISUAIS para biomas e legibilidade de lasers.

Nao altera timer, RNG, grupos, hitboxes, trajetorias, save ou dificuldade.
Todos os indicadores leem apenas o estado existente dos objetos.
"""
from __future__ import annotations
from functools import lru_cache
import pygame

# Tons deliberadamente suaves para nao camuflar objetos e inimigos.
PALETAS = {
    'cidade': (95, 175, 216), 'neve': (187, 222, 247),
    'deserto': (241, 190, 129), 'floresta': (111, 190, 142),
    'vulcao': (236, 112, 88), 'cidade_futurista': (96, 215, 232),
    'ilhas_celestes': (179, 209, 250),
}

@lru_cache(maxsize=7)
def _faixa_distante(bioma):
    """Silhuetas temáticas 2.5D. Cache e geometria determinística, sem RNG.

    São planos discretos atrás do chão e dos perigos; não são hitboxes.
    O fundo original continua responsável por toda a identidade principal.
    """
    c=PALETAS[bioma]
    tela=pygame.Surface((900,166),pygame.SRCALPHA)
    traseiro=(*c,21)
    frente=(*c,33)
    risco=(*c,43)
    if bioma in ('cidade','cidade_futurista'):
        # Skyline de blocos com formatos e janelas diferentes para cada época.
        for i in range(17):
            x=i*57-18
            altura=(44+(i*31)%69) if bioma=='cidade' else (73+(i*23)%71)
            largura=39 if bioma=='cidade' else 29+(i%3)*7
            pygame.draw.rect(tela,traseiro,(x,165-altura,largura,altura))
            if bioma=='cidade_futurista':
                pygame.draw.line(tela,risco,(x+largura//2,165-altura-14),(x+largura//2,165-altura),2)
                pygame.draw.polygon(tela,frente,[(x+2,165-altura+12),(x+largura//2,165-altura-7),(x+largura-2,165-altura+12)],1)
            for j in range(3):
                wy=165-altura+20+j*19
                if wy<165:
                    pygame.draw.rect(tela,risco,(x+9,wy,4,7))
    elif bioma=='neve':
        for i in range(11):
            x=i*103-48; ponta=44+(i*17)%51
            pygame.draw.polygon(tela,traseiro,[(x,165),(x+57,ponta),(x+114,165)])
            pygame.draw.polygon(tela,frente,[(x+40,ponta+17),(x+57,ponta),(x+74,ponta+17)],2)
        for i in range(15):
            x=i*69+8; pygame.draw.line(tela,risco,(x,155),(x+14,145),1)
    elif bioma=='deserto':
        for i in range(10):
            x=i*107-65
            pygame.draw.ellipse(tela,traseiro,(x,96+(i%3)*14,175,105))
            pygame.draw.arc(tela,frente,(x+15,100+(i%3)*14,138,76),3.25,5.6,2)
        for x in (84,315,560,812):
            pygame.draw.line(tela,risco,(x,140),(x,115),2)
            pygame.draw.line(tela,risco,(x,125),(x+11,116),2)
    elif bioma=='floresta':
        for i in range(15):
            x=i*67-16; h=57+(i*19)%54
            pygame.draw.line(tela,frente,(x+19,165),(x+19,165-h),4)
            for off,y in ((-20,165-h+20),(15,165-h+4),(0,165-h-8)):
                pygame.draw.circle(tela,traseiro,(x+19+off,y),22)
        for i in range(9):
            pygame.draw.line(tela,risco,(i*115,164),(i*115+21,143),2)
    elif bioma=='vulcao':
        for i in range(9):
            x=i*125-70; h=52+(i*21)%50
            pygame.draw.polygon(tela,traseiro,[(x,165),(x+70,165-h),(x+140,165)])
            pygame.draw.lines(tela,risco,False,[(x+53,165-h+17),(x+70,165-h),(x+87,165-h+17)],2)
            pygame.draw.line(tela,frente,(x+70,165-h+2),(x+66,165-h+27),2)
    elif bioma=='ilhas_celestes':
        for i in range(11):
            x=i*93-28; h=72+(i%3)*19
            pygame.draw.ellipse(tela,traseiro,(x,h,115,32))
            pygame.draw.polygon(tela,frente,[(x+21,h+23),(x+44,h+67),(x+83,h+23)])
            pygame.draw.line(tela,risco,(x+18,h+22),(x+90,h+22),2)
    return tela


def desenhar_profundidade_bioma(superficie, bioma, deslocamento, peso_noite=0.0, leve=False):
    """Plano de fundo de leitura suave, apenas no pass visual.

    A redução de contraste noturno é feita em cache e não modifica
    o clima, o fundo original, a física nem a ordem dos sprites.
    """
    if leve or bioma not in PALETAS:
        return False
    # Textura do efeito da versão anterior, mas com camada própria discreta.
    tex = _faixa_distante(bioma)
    noite = max(0.0, min(1.0, float(peso_noite)))
    # A noite diminui a conspicuidade em vez de aumentar brilho no céu.
    if noite:
        tex = _faixa_noturna(bioma, round(noite * 4) / 4)
    # Um desenho estável na faixa intermediária, atrás de chão e obstáculos.
    x = (-int(float(deslocamento) * 0.12)) % 900 - 900
    largura = superficie.get_width()
    for pos in range(x, largura, 900):
        superficie.blit(tex, (pos, 305))
    return True


@lru_cache(maxsize=28)
def _faixa_noturna(bioma, intensidade):
    original = _faixa_distante(bioma)
    result = original.copy()
    result.set_alpha(round(255 * (1 - 0.55 * intensidade)))
    return result


@lru_cache(maxsize=3)
def _icone_laser_qa(faixa):
    """QA v3.277.32: cache para as tres imagens fixas de aviso."""
    fundo=pygame.Surface((75,70),pygame.SRCALPHA)
    pygame.draw.rect(fundo,(8,27,43,220),(0,0,75,70),border_radius=8)
    pygame.draw.rect(fundo,(225,245,249,165),(0,0,75,70),2,border_radius=8)
    for pos,nivel in enumerate((2,1,0)):
        y=8+pos*20; perigo=nivel==faixa
        cor=(245,128,113,229) if perigo else (101,207,206,195)
        pygame.draw.rect(fundo,cor,(8,y,59,14),border_radius=3)
        if perigo:
            # Icone X + linhas hachuradas visível mesmo em preto e branco.
            pygame.draw.line(fundo,(20,33,47),(35,y+3),(43,y+11),3)
            pygame.draw.line(fundo,(20,33,47),(43,y+3),(35,y+11),3)
            for dx in (12,18,24,49,55):
                pygame.draw.line(fundo,(57,48,51,150),(dx,y+12),(dx+4,y+3),1)
        else:
            # Seta dupla para faixa disponível, iconografia independente da cor.
            for dx in (31,39):
                pygame.draw.lines(fundo,(13,54,65),False,[(dx,y+3),(dx+4,y+7),(dx,y+11)],2)
    return fundo

def desenhar_legibilidade_jetpack(superficie, gate, frame=0, leve=False):
    """Três faixas com X, chevrons e separadores: redundância sem depender de cores.

    Nunca escreve em gate, usa o aviso real e não gera comandos ou temporizadores.
    """
    if not getattr(gate,'ligado',False) or int(getattr(gate,'aviso',0))<=0:
        return False
    faixa=max(0,min(2,int(gate.faixa)))
    x0,y0=superficie.get_width()-89,262
    superficie.blit(_icone_laser_qa(faixa),(x0,y0))
    return True


def desenhar_legibilidade_corredor(superficie, faixas, frame=0, leve=False):
    """Marca o vão existente durante o warning com bordas, seta e traços.

    Nenhuma sugestão visual é dada após a fase de aviso; nada muda na colisão.
    """
    desenhou=0
    for f in faixas:
        if int(f.get('warning',0))<=0:continue
        x,y,h=int(f['x']),int(f['gap_y']),max(0,int(f['gap_h']))
        if x< -40 or x>superficie.get_width()+40 or h==0:continue
        topo=y-h//2+3; base=y+h//2-3
        if base<=topo:continue
        for yy,sentido in ((topo,1),(base,-1)):
            pygame.draw.line(superficie,(240,245,226),(x+2,yy),(x+31,yy),3)
            pygame.draw.line(superficie,(35,72,85),(x+2,yy+sentido*4),(x+31,yy+sentido*4),1)
            # Três traços para distinguir as bordas do feixe.
            for dx in (4,13,22):
                pygame.draw.line(superficie,(112,228,211),(x+dx,yy+sentido*6),(x+dx+4,yy+sentido*10),1)
        meio=(topo+base)//2
        pygame.draw.lines(superficie,(178,243,218),True,[(x+9,meio),(x+16,meio-6),
                          (x+23,meio),(x+16,meio+6)],2)
        pygame.draw.line(superficie,(178,243,218),(x+12,meio),(x+20,meio),2)
        desenhou+=1
    return desenhou
