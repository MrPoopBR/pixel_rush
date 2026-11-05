"""Pixel Rush v3.177.0 — iluminação coerente e acabamento MATERIAL EXISTENTE.

Etapa 3 do Plano D: não cria props, ruas, obstáculos, inimigos nem eventos.
O acabamento de materiais ocorre uma vez por sprite/chunk; alfa intacto.
A iluminação ambiental é cacheada por bioma / condição de luz, apenas atrás
personagens e obstáculos, sem modificar câmera, física ou controles.
"""
from __future__ import annotations
import math
import pygame

# reflexão, borda superior, sombreamento inferior, proporção do acabamento
PERFIS = {
    'cidade':            ((214,221,234),(35,45,65), .13, .12, (238,196,126)),
    'neve':              ((253,252,255),(92,139,180), .20, .16, (203,228,255)),
    'deserto':           ((255,222,163),(124,80,59), .20, .16, (255,207,125)),
    'vulcao':            ((255,172,94), (43,34,48), .22, .18, (255,136,63)),
    'floresta':          ((181,221,147),(43,77,52), .17, .15, (171,220,126)),
    'cidade_futurista':  ((114,234,254),(24,30,66), .22, .17, (112,234,255)),
    'ilhas_celestes':    ((239,250,255),(84,144,185), .19, .15, (195,248,221)),
}


def iluminar_material(surf, biome, plano='mid'):
    """Trata metal/pedra/neve/terra por luz vinda do alto sem mover um pixel.

    - mantém exatamente a mesma máscara alfa original;
    - reforça bordas de cima e recessos de baixo de objetos já existentes;
    - moderação progressiva em planos distantes para não competir com o jogador;
    - usa numpy só no carregamento do cenário, nunca na atualização do frame.
    """
    if biome not in PERFIS or surf.get_width()<8 or surf.get_height()<8:
        return surf
    import numpy as np
    light, shade, p_light, p_shade, emissive = PERFIS[biome]
    scale = {'far':.55,'mid':.86,'near':1.0}.get(plano, .8)
    if not (surf.get_flags() & pygame.SRCALPHA):
        # Sem alfa per-pixel: não deslocar nem modificar material legado inesperado.
        return surf
    rgb = pygame.surfarray.pixels3d(surf)
    alpha = pygame.surfarray.pixels_alpha(surf)
    try:
        opaque = alpha >= 160
        # O eixo dos arrays de Pygame é X,Y: a luz chega pela superfície superior.
        above = np.zeros(opaque.shape, dtype=np.bool_)
        below = np.zeros(opaque.shape, dtype=np.bool_)
        above[:,1:] = opaque[:,:-1]
        below[:,:-1] = opaque[:,1:]
        # Pequena topologia de facetas e relevo interno: costura de chunks intacta.
        top = opaque & ~above
        bottom = opaque & ~below
        # Arestas de material são normalmente 1 pixel; corpo recebe 5% de gradação.
        luminance = (rgb[:,:,0].astype(np.uint16)*3 + rgb[:,:,1].astype(np.uint16)*5 + rgb[:,:,2].astype(np.uint16)*2)//10
        # Focar as superfícies que já são legíveis, evitando iluminar poeira preta.
        midtone = opaque & (luminance>55) & (luminance<225) & ~top & ~bottom
        weight_light = np.zeros(opaque.shape, np.float32)
        weight_shade = np.zeros(opaque.shape, np.float32)
        weight_light[top] = p_light * scale
        weight_shade[bottom] = p_shade * scale
        # iluminação de materiais mais rica mas extremamente leve
        weight_light[midtone] = p_light * scale * .18
        if plano == 'near':
            # Reentrâncias na base para dar peso a pedestais/chão já existentes.
            mask = midtone & (luminance < 95)
            weight_shade[mask] = p_shade * .08
        for c in range(3):
            src = rgb[:,:,c].astype(np.float32)
            value = src * (1.0-weight_light-weight_shade) + light[c]*weight_light + shade[c]*weight_shade
            rgb[:,:,c] = np.clip(value+.5, 0, 255).astype(np.uint8)
    finally:
        del rgb, alpha
    return surf


_CACHE_AMBIENTE = {}


def _luz_ambiente(biome, periodo, chuva, largura=450, altura=247):
    chave=(biome, periodo, bool(chuva), largura, altura)
    s=_CACHE_AMBIENTE.get(chave)
    if s is not None:
        return s
    profile=PERFIS.get(biome)
    s=pygame.Surface((largura, altura),pygame.SRCALPHA)
    if profile is None:
        return s
    quente=profile[4]
    frio=profile[0]
    # Luz na arquitetura, não no céu vazio, usando gradiente de faixas largas.
    # Para entardecer há um reflexo lateral discreto na estrutura.
    for y in range(altura):
        depth=y/max(1,altura-1)
        if periodo=='dia':
            strength=int(3 + 7*(depth**1.7))
            col=frio
        elif periodo=='tarde':
            strength=int(5 + 15*(depth**1.5))
            col=(255,185,120)
        else:
            strength=int(3 + 17*(depth**2.1))
            col=quente
        if chuva:
            strength=int(strength*.68)
            col=tuple(int(0.65*c + 0.35*130) for c in col)
        pygame.draw.line(s,(*col,strength),(0,y),(largura-1,y),1)
    _CACHE_AMBIENTE[chave]=s
    return s


def iluminar_panorama(superficie,biome,noite,fase,clima):
    """Ilumina *só* a arquitetura entre y=475 e y=722; sprites ficam acima.

    Não introduz um novo sistema de partículas, nem altera iluminação do HUD.
    """
    if biome not in PERFIS:
        return
    noite=max(0.,min(1.,float(noite)))
    periodo=('noite' if noite >= .56 else
             'tarde' if (.12 < float(fase) < .25 or .68 < float(fase) < .83) else 'dia')
    chuva=clima in ('chuva','tempestade','chuva_acida','nevasca','cinzas','tempestade_areia')
    superficial=_luz_ambiente(biome,periodo,chuva)
    superficie.blit(superficial,(0,475))


_CACHE_REFLEXO = {}


def acabamento_tile_chao(tile,biome):
    """Refina luz e relevo do piso no cache, preservando desenho e scroll.

    Não altera largura, geometria, pixels fora do piso ou lógica de collision.
    """
    if biome not in PERFIS:
        return tile
    key=(biome,id(tile))
    if key in _CACHE_REFLEXO:
        return tile
    _CACHE_REFLEXO[key]=True
    luz,sombra,_,_,_ = PERFIS[biome]
    largura,altura=tile.get_size()
    # Microfacetas presas às linhas do piso, nunca itens soltos.
    for x in range(16,largura-16,53):
        y=15 + ((x//53)%3)*6
        col=tile.get_at((x,y))
        mix=tuple(int(col[c]*.52 + luz[c]*.48) for c in range(3))
        pygame.draw.line(tile,mix,(x,y),(x+8,y),1)
        # sombra de contacto sob as facetas
        y2=min(altura-3,y+2)
        col2=tile.get_at((x,y2))
        mix2=tuple(int(col2[c]*.72 + sombra[c]*.28) for c in range(3))
        pygame.draw.line(tile,mix2,(x+1,y2),(x+6,y2),1)
    # Um filete coerente com a iluminação na borda superior da pista.
    edge = (max(0,altura-67))
    cor0=tile.get_at((18,edge))
    cor_luz=tuple(int(cor0[c]*.65 + luz[c]*.35) for c in range(3))
    pygame.draw.line(tile,cor_luz,(0,edge),(largura-1,edge),1)
    return tile
