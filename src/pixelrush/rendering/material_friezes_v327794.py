# -*- coding: utf-8 -*-
"""PIXEL RUSH R24: microjuntas de pigmento existentes, so no carregamento.

Nenhuma Surface, objeto de gameplay ou passe novo por quadro; somente RGB
dos materiais opacos, sem tocar alfa, hitboxes, RNG, fisica ou mapa geometrico.
"""
import numpy as np
import pygame
import os
# Microacentos separados dos frisos antigos; rollback preserva QA794 byte a byte.
_R25_DETAILS=os.environ.get('PIXELRUSH_QA_R25_ART_DETAILS','1')=='1'
# R26: luz de aresta pintada somente na carga de atlas, sem mudar alpha.
_R26_EDGE_RIM=os.environ.get('PIXELRUSH_QA_R26_EDGE_RIM','1')=='1'

PERFIS = {
    'cidade': (47,23,0,4),
    'neve': (39,19,1,4),
    'deserto': (57,17,2,5),
    'vulcao': (43,29,3,5),
    'floresta': (31,37,-1,4),
    'cidade_futurista': (27,31,0,5),
    'ilhas_celestes': (53,23,-2,4),
}

def aplicar_friso(imagem, bioma, plano, indice):
    """Detalhe estatico, devolve delta int8 para as paletas noite existentes."""
    if (plano!='near' or bioma not in PERFIS
            or not imagem.get_flags()&pygame.SRCALPHA
            or imagem.get_width()<48 or imagem.get_height()<48):
        return None,0
    from pixelrush_texturas_v3185 import _material
    rgb=pygame.surfarray.array3d(imagem)
    alpha=pygame.surfarray.array_alpha(imagem)
    largura,altura=alpha.shape
    valido=_material(bioma,rgb)&(alpha==255)
    atual=rgb.astype(np.int16)
    # Vizinhos por views contiguas: evita 8 np.roll integrais e conserva
    # pixels exatos no interior; a borda externa ja e zerada abaixo.
    for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
        if dx==-1:
            slice_atual=(slice(None,-1),slice(None))
            vizinho=rgb[1:,:,:]
            alpha_vizinho=alpha[1:,:]
        elif dx==1:
            slice_atual=(slice(1,None),slice(None))
            vizinho=rgb[:-1,:,:]
            alpha_vizinho=alpha[:-1,:]
        elif dy==-1:
            slice_atual=(slice(None),slice(None,-1))
            vizinho=rgb[:,1:,:]
            alpha_vizinho=alpha[:,1:]
        else:
            slice_atual=(slice(None),slice(1,None))
            vizinho=rgb[:,:-1,:]
            alpha_vizinho=alpha[:,:-1]
        valido[slice_atual] &= (
            (alpha_vizinho==255) &
            (np.max(np.abs(atual[slice_atual]-vizinho.astype(np.int16)),axis=2)<=24))
    valido[:15]=False
    valido[-15:]=False
    valido[:,:12]=False
    valido[:,-12:]=False
    # Dois eixos broadcast em vez de dois arrays W*H int32 (~450 KiB poupados
    # por variante na preparacao Android; mesmos pixels para o friso QA794).
    xx=np.arange(largura,dtype=np.int32)[:,None]
    yy=np.arange(altura,dtype=np.int32)[None,:]
    px,py,skew,forca=PERFIS[bioma]
    fase=int(indice)*11
    risco=(xx+skew*yy+fase)%px
    faixa=(yy+3*fase)%py
    escuro=valido&(risco<=1)&(faixa<=3)
    claro=valido&(risco==2)&(faixa<=2)
    delta=np.zeros((largura,altura),dtype=np.int8)
    delta[escuro]=-forca
    delta[claro]=forca
    if _R25_DETAILS:
        # Microrelief de material solido por bioma, deslocado de QA794 para
        # nao duplicar o padrao de juntas: duas pinceladas a cada ~60x30 px.
        # As cores historicas, alfa e os canais fisicos nao mudam.
        mini=valido & ((xx+indice*5)%(px+17)==7) & ((yy+indice*3)%(py+11)<=2)
        mini &= (delta==0)
        sinal=-1 if bioma in ('vulcao','floresta') else 1
        delta[mini]=sinal*max(2,forca-2)
    if _R26_EDGE_RIM:
        # Acabamento de contorno do proprio telhado/encosta, nao cria
        # sprite nem objeto. Aplica apenas onde o material solido toca
        # transparencia logo acima, com pinceladas espaçadas por bioma.
        material=_material(bioma,rgb)
        borda=np.zeros((largura,altura),dtype=np.bool_)
        borda[:,1:]=(alpha[:,1:]==255)&(alpha[:,:-1]<255)
        borda&=material
        borda[:15]=False; borda[-15:]=False
        borda[:,:12]=False; borda[:,-12:]=False
        borda &= ((xx+fase*2)%(px+5)<5) & (delta==0)
        tom=(-3 if bioma in ('floresta','vulcao') else
             5 if bioma in ('neve','cidade_futurista','ilhas_celestes') else 3)
        delta[borda]=tom
    quantidade=int(np.count_nonzero(delta))
    if not quantidade:return None,0
    tela=pygame.surfarray.pixels3d(imagem)
    try:
        tela[:]=np.clip(tela.astype(np.int16)+delta[:,:,None],0,255).astype(np.uint8)
    finally:
        del tela
    return delta,quantidade

def aplicar_cidade(cidade):
    """Uma vez nos atlases perto da Cidade, mantendo mapas tecnicos."""
    if getattr(cidade,'_r24_friso_aplicado',False):
        return cidade
    total=0
    for camada in cidade.layers:
        if camada.foreground or camada.name!='near':
            continue
        for indice,variante in enumerate(camada.variants):
            _,contagem=aplicar_friso(variante.image,'cidade','near',indice)
            total+=contagem
    cidade._r24_friso_aplicado=True
    cidade._r24_friso_pixels=total
    return cidade
