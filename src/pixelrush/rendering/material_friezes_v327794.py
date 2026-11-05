# -*- coding: utf-8 -*-
"""PIXEL RUSH R24: microjuntas de pigmento existentes, so no carregamento.

Nenhuma Surface, objeto de gameplay ou passe novo por quadro; somente RGB
dos materiais opacos, sem tocar alfa, hitboxes, RNG, fisica ou mapa geometrico.
"""
import numpy as np
import pygame

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
    for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
        outro=np.roll(rgb,(dx,dy),axis=(0,1))
        valido&=(np.roll(alpha,(dx,dy),axis=(0,1))==255)&(
            np.max(np.abs(atual-outro.astype(np.int16)),axis=2)<=24)
    valido[:15]=False
    valido[-15:]=False
    valido[:,:12]=False
    valido[:,-12:]=False
    xx,yy=np.indices((largura,altura),dtype=np.int32)
    px,py,skew,forca=PERFIS[bioma]
    fase=int(indice)*11
    risco=(xx+skew*yy+fase)%px
    faixa=(yy+3*fase)%py
    escuro=valido&(risco<=1)&(faixa<=3)
    claro=valido&(risco==2)&(faixa<=2)
    delta=np.zeros((largura,altura),dtype=np.int8)
    delta[escuro]=-forca
    delta[claro]=forca
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
