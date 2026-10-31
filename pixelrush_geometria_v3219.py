"""Plano I / v3.219.0 — lapidacao geometrica de cenografia existente.

Apenas Cidade, Cidade Nevada e Deserto, nos planos FAR/MID em qualidade alta.
Faces iluminadas / laterais / topo sao calculadas OFFLINE (primeiro uso de tile),
utilizando somente a silhueta e as cores da arte corrente (v3.218.0).
Nunca toca no canal alfa, mapas tecnicos, perto do chao, fisica ou hitboxes.
"""
from collections import OrderedDict
from types import MethodType

import numpy as np
import pygame

BIOMAS = frozenset(('cidade', 'neve', 'deserto'))
PLANOS = frozenset(('far', 'mid'))
# Ate 12 mini-atlases modulares 225x250x4 = 2,58 MiB.
CACHE_MAXIMO = 12


def _deslocar(mask, dx=0, dy=0):
    """Deslocamento sem envolvimento, para nao criar luz nas costuras."""
    resultado = np.zeros_like(mask, dtype=bool)
    x0=max(0,dx); x1=mask.shape[0]+min(0,dx)
    y0=max(0,dy); y1=mask.shape[1]+min(0,dy)
    if x1>x0 and y1>y0:
        resultado[x0:x1,y0:y1] = mask[x0-dx:x1-dx,y0-dy:y1-dy]
    return resultado


def lapidar(original, biome, plano):
    """Modelagem de faces sobre *pixels existentes*, sem novos volumes soltos.

    O desenho e orientado pelas bordas REAIS do sprite. Diferente de uma
    sobreposicao de padrao decorativo, as faces acompanham as formas opacas.
    """
    if biome not in BIOMAS or plano not in PLANOS or not (original.get_flags() & pygame.SRCALPHA):
        return original.copy(), {'rgb': 0, 'alfa': True}
    width,height=original.get_size()
    if width<44 or height<50:
        return original.copy(), {'rgb': 0, 'alfa': True}
    rgb=pygame.surfarray.array3d(original)
    alpha=pygame.surfarray.array_alpha(original)
    solido=alpha>=245
    seguro=solido.copy()
    for dx,dy in ((-2,0),(2,0),(0,-2),(0,2),(-1,0),(1,0),(0,-1),(0,1)):
        seguro &= _deslocar(solido,dx,dy)
    # Na cidade, proteger emendas das variantes; nos tiles, preservar margens.
    margem=20 if width>=400 else 17
    seguro[:margem,:]=False
    seguro[-margem:,:]=False
    seguro[:,:13]=False
    seguro[:,-17:]=False
    # Modular y=184 equivale a faixa protegida do contato da pista (2x).
    if width==225 and height==250:
        seguro[:,184:]=False
    if not seguro.any():
        return original.copy(), {'rgb':0,'alfa':True}

    # Deteccao de superfices por direcao. O mapa alfa existente e a unica
    # fonte para definir uma face (nao ha extrusao ou adicao de partes).
    cima=seguro & ~_deslocar(solido, 0, 6)
    esquerda=seguro & ~_deslocar(solido, 7, 0)
    direita=seguro & ~_deslocar(solido,-8, 0)
    baixo=seguro & ~_deslocar(solido,0,-6)
    lum=(rgb[:,:,0].astype(np.uint16)*3+rgb[:,:,1].astype(np.uint16)*6+rgb[:,:,2].astype(np.uint16))//10
    material=seguro & (lum>=28) & (lum<=243)
    # Formas pequenas ja recebem os contornos originais: nao sobrescrever
    # pixels de silhueta de 1-2px nem detalhes artisticos delicados.
    cima &= material
    esquerda &= material
    direita &= material
    baixo &= material

    # Luz ambiente e faces laterais ajustadas por material, nao por sprites.
    if biome=='cidade':
        top_boost, left_boost, right_drop, bottom_drop=17,10,24,8
        x,y=np.ogrid[:width,:height]
        # Painel de fachada interior: modula a sombra SOMENTE nas faces
        # grandes ja delimitadas pela silhueta da arquitetura, sem janelas novas.
        plano_lateral=material & ~esquerda & direita & (y>24)
        plano_superior=material & cima & (y<height-30)
        ajuste_plano=np.zeros_like(lum,dtype=np.int16)
        ajuste_plano[plano_lateral]=-7
        ajuste_plano[plano_superior]=8
    elif biome=='neve':
        top_boost,left_boost,right_drop,bottom_drop=19,8,14,8
        x,y=np.ogrid[:width,:height]
        # Facetas da montanha: lados alternos orientados na diagonal,
        # e profundidade sob o topo existente, sem cristais artificiais.
        vertente=((x+2*y)//68)%3
        claro=material & (vertente==0) & (lum>66) & (lum<210)
        escuro=material & (vertente==2) & (lum>66) & (lum<210)
        ajuste_plano=np.zeros_like(lum,dtype=np.int16)
        ajuste_plano[claro]=5
        ajuste_plano[escuro]=-6
        # Occlusao discreta sob o limite das calotas claras ja existentes.
        acima=np.roll(lum,2,axis=1)
        occlusao=material & (lum+25<acima) & (acima>175)
        occlusao[:,:3]=False
        ajuste_plano[occlusao]=-11
    else:  # deserto
        top_boost,left_boost,right_drop,bottom_drop=14,8,24,9
        x,y=np.ogrid[:width,:height]
        # Grandezas de planos obliquos — camadas esculpidas da propria rocha,
        # distintas das linhas de materiais da v3.200.0.
        face=((2*x+y)//82)%4
        pedra=material & (lum>48) & (lum<219)
        ajuste_plano=np.zeros_like(lum,dtype=np.int16)
        ajuste_plano[pedra & (face==0)]=6
        ajuste_plano[pedra & (face==3)]=-9

    # Acompanhamento das faces reais com direito de precedencia ao contorno.
    mod=ajuste_plano.copy()
    mod[baixo] -= bottom_drop
    mod[direita] -= right_drop
    mod[esquerda] += left_boost
    mod[cima] += top_boost
    # Reforco mais discreto no FAR, que deve continuar afastado.
    if plano=='far':
        mod=np.rint(mod*.72).astype(np.int16)
    mod[~material]=0
    novo_rgb=np.clip(rgb.astype(np.int16)+mod[:,:,None],0,255).astype(np.uint8)
    mudaram=int(np.count_nonzero(np.any(novo_rgb!=rgb,axis=2)))
    novo=pygame.Surface((width,height),pygame.SRCALPHA,32)
    with_rgb=pygame.surfarray.pixels3d(novo)
    with_rgb[:]=novo_rgb
    del with_rgb
    with_alpha=pygame.surfarray.pixels_alpha(novo)
    with_alpha[:]=alpha
    del with_alpha
    return novo,{'rgb':mudaram,'alfa':True}


def instalar_cidade(cidade, leve=False):
    if getattr(cidade,'_geometria_3219',False):
        return cidade
    cidade._geometria_3219=True
    cidade._geo3219_estatistica={'rgb':0,'superficies':0}
    if leve:
        return cidade
    visitados={}
    for layer in cidade.layers:
        if layer.foreground or layer.name not in PLANOS:
            continue
        for variant in layer.variants:
            img=variant.image
            key=(id(img),layer.name)
            if key not in visitados:
                novo,medida=lapidar(img,'cidade',layer.name)
                visitados[key]=novo
                cidade._geo3219_estatistica['rgb']+=medida['rgb']
                cidade._geo3219_estatistica['superficies']+=1
            variant.image=visitados[key]
    return cidade


def _refinar_cacheado(cena,superficie,plano):
    estado=cena._geometria_3219
    cache=estado['cache']
    key=(plano,id(superficie))
    if key in cache:
        cache.move_to_end(key)
        return cache[key]
    novo,medida=lapidar(superficie,cena.biome,plano)
    cache[key]=novo
    estado['pixels']+=medida['rgb']
    estado['gerados']+=1
    while len(cache)>CACHE_MAXIMO:
        cache.popitem(last=False)
    return novo


def instalar_modular(cena,leve=False):
    if getattr(cena,'_geometria_3219',None) is not None:
        return cena
    cena._geometria_3219={'cache':OrderedDict(),'pixels':0,'gerados':0,'maximo':CACHE_MAXIMO}
    if leve or cena.biome not in ('neve','deserto'):
        return cena
    anterior=cena._tile_map
    cena._geometria_3219_anterior=anterior
    def _tile(self,plano,indice,tipo):
        superficie=self._geometria_3219_anterior(plano,indice,tipo)
        if superficie is None or tipo!='image' or plano not in PLANOS:
            return superficie
        return _refinar_cacheado(self,superficie,plano)
    cena._tile_map=MethodType(_tile,cena)
    return cena
