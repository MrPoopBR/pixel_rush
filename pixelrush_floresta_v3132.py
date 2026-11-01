"""Floresta Densa 2.0: marcos de cenário pré-renderizados, SEM sprites de colisão.

Preserva arte panorâmica e props da v3.131. Camadas leves adicionam quatro
regiões (bosque, clareira, ruínas, rio) em tiles de baixa resolução. Não há
superfícies criadas, I/O, textura recalculada nem RNG no loop de desenho.
"""
import math
import random
import pygame

W, H = 225, 250
REGIOES = ('BOSQUE GIGANTE', 'CLAREIRA LUMINOSA', 'RUINAS VERDES', 'RIO ANTIGO')


def _folhagem(s, x, y, r, rng, destaque=False):
    sombra = (29, 86, 63)
    meio = (47, 111, 69)
    luz = (105, 150, 76) if not destaque else (141, 178, 91)
    pygame.draw.ellipse(s, sombra, (x-r, y-r//2, r*2, r))
    for i in range(7):
        a = i * (2 * math.pi / 7)
        bx = x + int(math.cos(a) * r * .58)
        by = y + int(math.sin(a) * r * .27)
        pygame.draw.circle(s, meio if i%3 else luz, (bx, by), max(3, r//3))
    for _ in range(12):
        px=x+rng.randrange(-r+3,r-2)
        py=y+rng.randrange(-max(3,r//3), max(4,r//3))
        pygame.draw.line(s, (139, 174, 83), (px,py), (px+2,py-1), 1)


def _tronco(s,x,base,h,largura,rng):
    # Raiz sempre presa ao solo do panorama (y=226), sem arbustos suspensos.
    topo=base-h
    pygame.draw.polygon(s,(39,58,50),[(x-largura//2-7,base),(x-largura//2,topo+12),
       (x-largura//4,topo),(x+largura//2,topo+5),(x+largura//2+8,base)])
    pygame.draw.polygon(s,(91,92,57),[(x-largura//2+3,base),(x-largura//3,topo+10),
        (x,topo+4),(x+3,base)])
    for dy in range(11,h-5,14):
        xx=x-largura//3+(dy//9)%5
        pygame.draw.line(s,(130,128,76),(xx,topo+dy),(xx+3,topo+dy+5),1)
    for rdx in (-largura//2, largura//2):
        pygame.draw.polygon(s,(46,68,50),[(x,base-24),(x+rdx,base-5),
                            (x+rdx*2,base),(x,base)])
    _folhagem(s,x,topo+8,30,rng)
    for dx in (-18,20):
        pygame.draw.line(s,(52,121,78),(x+dx,topo+17),(x+dx+4,topo+39),2)
        for yy in (topo+27,topo+35):
            pygame.draw.ellipse(s,(93,151,73),(x+dx+2, yy,7,3))


def _ruina(s,x,base,rng):
    w = rng.randrange(25,40)
    h = rng.randrange(61,85)
    pygame.draw.rect(s,(45,75,67),(x-3,base-h-5,w+6,9))
    pygame.draw.rect(s,(118,133,105),(x,base-h,w,h))
    pygame.draw.rect(s,(79,107,87),(x+6,base-h+3,w-10,h-6))
    pygame.draw.rect(s,(53,78,72),(x+10,base-h+12,max(3,w-18),h-22))
    pygame.draw.line(s,(183,185,131),(x+3,base-h+9),(x+w-2,base-h+9),2)
    for dy in range(20,h,17):
        pygame.draw.line(s,(143,154,117),(x+5,base-h+dy),(x+w-5,base-h+dy),2)
        pygame.draw.line(s,(29,81,59),(x+w-7,base-h+dy),(x+w-11,base-h+dy+7),2)
    pygame.draw.polygon(s,(39,103,66),[(x-3,base-h+6),(x+w//2,base-h-3),
                                         (x+w+5,base-h+5),(x+w+2,base-h+13),(x+2,base-h+9)])
    _folhagem(s,x+w//2,base-14,14,rng)


def _tile(regiao,variacao):
    rng=random.Random(13220 + regiao*79 + variacao*37)
    s=pygame.Surface((W,H),pygame.SRCALPHA)
    # Composição propositalmente vazada no centro: os perigos conservam prioridade.
    if regiao==0:
        # A arte aprovada já contém grandes troncos. Novos detalhes só na
        # base das árvores existentes, jamais colunas simples por cima delas.
        for x in (17, 201):
            pygame.draw.polygon(s,(53,85,66),[(x-26,227),(x-19,215),(x-5,203),
                                               (x+8,216),(x+23,227)])
            pygame.draw.line(s,(119,121,77),(x-13,216),(x-4,210),2)
            for off in (-15,-4,13):
                _folhagem(s,x+off,213+(off%5),10,rng)
        # Cogumelos de luz localizados em raízes reais.
        for x in (29,42,188,197):
            y=221-(x%7)
            pygame.draw.line(s,(173,200,146),(x,y+7),(x,y+2),1)
            pygame.draw.ellipse(s,(87,177,150),(x-4,y,9,5))
            pygame.draw.line(s,(200,226,157),(x-2,y+1),(x+2,y+1),1)
    elif regiao==1:
        # Clareira mais vazia: pequena lagoa recuada, abertura luminosa.
        pygame.draw.ellipse(s,(35,103,108,135),(37,212,150,15))
        pygame.draw.ellipse(s,(76,159,159,135),(47,216,125,7))
        for x in (66,102,157):
            pygame.draw.line(s,(186,225,194),(x,217),(x+10,218),1)
        for x in (17,206):
            _folhagem(s,x,211,13,rng,True)
            pygame.draw.line(s,(159,175,112),(x-5,221),(x+4,218),1)
        for x in (34,193):
            pygame.draw.polygon(s,(86,112,94),[(x-10,227),(x-8,218),(x+4,216),(x+12,225)])
            pygame.draw.line(s,(160,170,121),(x-6,219),(x+4,217),1)
    elif regiao==2:
        # As ruínas ganham escala discreta para não competir com inimigos.
        _ruina(s,13+variacao*4,221,rng)
        _ruina(s,177-variacao*5,221,rng)
        for x in (53,153):
            _folhagem(s,x,216,12,rng)
        for x in (91,127):
            pygame.draw.polygon(s,(83,121,97),[(x-10,225),(x-5,217),(x+10,220),(x+12,225)])
            pygame.draw.line(s,(154,167,119),(x-6,218),(x+4,220),1)
    else:
        # Riacho fino e ponte abandonada atrás do piso; sem barra azul na pista.
        pygame.draw.ellipse(s,(45,113,114,140),(34,214,160,13))
        pygame.draw.ellipse(s,(86,169,160,150),(42,217,143,6))
        for x in range(20,213,28):
            pygame.draw.rect(s,(75,98,88),(x,208,16,4))
            pygame.draw.line(s,(158,162,116),(x+2,208),(x+13,208),1)
        for x in (12,201):
            pygame.draw.polygon(s,(70,107,84),[(x-14,226),(x-9,210),(x+8,208),(x+15,225)])
            _folhagem(s,x,210,13,rng)
    # Ao fundo do terreno; não gera rastros/pegadas e não invade faixa da pista.
    pygame.draw.line(s,(56,117,74),(0,230),(W,230),1)
    return pygame.transform.scale(s,(450,500))


class MarcosFloresta:
    """Máximo 8 quadros armazenados (criados na primeira visita ao bioma)."""
    def __init__(self):
        self._quadros=tuple(tuple(_tile(i,j) for j in range(2)) for i in range(4))

    @staticmethod
    def etapa(travel):
        # Mesmo deslocamento da camada média existente: sem saltos no scroll.
        bloco=int(max(0.,travel)*.235//450)
        return (bloco//3)%4

    def desenhar(self,superficie,travel,leve=False):
        offset=max(0.,travel)*.235
        bloco=int(offset//450)
        desloc=int(offset%450)
        for j in range(2):
            k=bloco+j
            etapa=(k//3)%4
            variante=(k//12+k)%2
            # Não há scale, sprite novo nem emissão de partículas aqui.
            superficie.blit(self._quadros[etapa][variante],(j*450-desloc,230))
