"""v3.151 — acabamento de material para os 28 perigos existentes.
Sem alterações de geometria, hitboxes, deslocamento, spawn ou animação.
As 3 imagens de cada perigo são calculadas no primeiro uso e cacheadas.
"""
import os
import random
import numpy as np
import pygame
import pixelrush_ameacas_v3127 as motor
from pixelrush_ameacas_v3146 import (
    AMEACAS, POR_BIOMA, escorpiao_frame,
    AmeacaBioma as BaseAmeaca, imagem_ameaca as imagem_original
)

_CACHE = {}
PALETAS = {
    'cidade': ((239,211,144),(107,116,138)),
    'neve': ((225,246,249),(111,157,197)),
    'deserto': ((249,213,139),(137,94,72)),
    'vulcao': ((255,192,113),(94,61,77)),
    'floresta': ((185,222,140),(65,111,79)),
    'cidade_futurista': ((131,237,243),(88,75,153)),
    'ilhas_celestes': ((210,249,233),(136,117,196)),
}
MATERIAIS = {
    'C1':'pele','C2':'plumas','C3':'pintura','C4':'madeira',
    'N1':'pele','N2':'plumas','N3':'cristal','N4':'madeira',
    'D1':'escamas','D2':'carapaca','D3':'pedra','D4':'osso',
    'V1':'escamas','V2':'plumas','V3':'pedra','V4':'vapor',
    'F1':'carapaca','F2':'plumas','F3':'madeira','F4':'madeira',
    'CF1':'metal','CF2':'metal','CF3':'metal','CF4':'energia',
    'IC1':'carapaca','IC2':'pele','IC3':'cristal','IC4':'pedra',
}


def _refinar(codigo, fase, base):
    out=base.copy().convert_alpha()
    alpha=pygame.surfarray.array_alpha(base)
    rgb=pygame.surfarray.array3d(base)
    w,h=base.get_size()
    biome=AMEACAS[codigo][0]
    luz,sombra=PALETAS[biome]
    material=MATERIAIS[codigo]
    rr=random.Random(315100+sum((i+1)*ord(c) for i,c in enumerate(codigo))*31+fase*109)
    # Extrai apenas regiões visíveis do sprite; nada pode aparecer fora do contorno.
    solid=alpha >= 195
    luma=(rgb[:,:,0].astype(np.uint16)*3 + rgb[:,:,1].astype(np.uint16)*5 + rgb[:,:,2].astype(np.uint16)*2)//10
    mask=solid & (luma>58) & (luma<224)
    arr=pygame.surfarray.pixels3d(out)
    # Luz superior e oclusão inferior dentro da mesma silhueta já aprovada.
    for y in range(2,h-2):
        sl=mask[:,y]
        if not np.any(sl): continue
        if y < h*.42:
            strength=0.14*(1-y/max(1,h*.44))
            old=arr[:,y,:].astype(np.float32)
            arr[:,y,:]=np.where(sl[:,None], np.clip(old*(1-strength)+np.array(luz)*strength,0,255),old).astype(np.uint8)
        elif y > h*.63:
            strength=.10*((y-h*.63)/max(1,h*.37))
            old=arr[:,y,:].astype(np.float32)
            arr[:,y,:]=np.where(sl[:,None],np.clip(old*(1-strength)+np.array(sombra)*strength,0,255),old).astype(np.uint8)
    # Texturas guiadas pelo material, respeitando pixels transparentes.
    density={'pele':10,'plumas':10,'escamas':13,'carapaca':13,'pintura':9,
             'madeira':14,'cristal':12,'pedra':15,'osso':10,'vapor':8,
             'metal':12,'energia':9}[material]
    candidatos=np.argwhere(mask)
    if len(candidatos):
        for n in range(density):
            x,y=map(int,candidatos[rr.randrange(len(candidatos))])
            if x<3 or x>w-4 or y<4 or y>h-5: continue
            # Uma ou duas células de textura, nunca uma nova forma externa.
            col=luz if (n%4)!=0 else sombra
            arr[x,y,:]=col
            if material in ('madeira','pedra','escamas','carapaca'):
                xx=x+1 if material!='madeira' else x
                yy=y+1 if material=='madeira' else y
                if xx<w and yy<h and mask[xx,yy]: arr[xx,yy,:]=col
            elif material in ('cristal','metal','energia'):
                if x+1<w and mask[x+1,y] and n%3==0:arr[x+1,y,:]=luz
    # Filete interior superior: acrescenta volume sem engrossar outline.
    for x in range(3,w-3,5):
        for y in range(3,min(h-3,max(8,h//2))):
            if solid[x,y] and (not solid[x,y-1]) and luma[x,y]>50:
                arr[x,y,:]=luz
                break
    del arr
    # Preserva inclusive o canal alfa parcial do original, pixel por pixel.
    assert np.array_equal(pygame.surfarray.array_alpha(out),alpha)
    return out


def imagem_ameaca(codigo, fase=0):
    if codigo not in AMEACAS or os.environ.get('PIXELRUSH_ARTE_CLASSICA')=='1':
        return imagem_original(codigo,fase)
    fase=int(fase)%3
    chave=(codigo,fase)
    if chave not in _CACHE:
        src=imagem_original(codigo,fase)
        _CACHE[chave]=_refinar(codigo,fase,src)
    return _CACHE[chave]

# A implementação do motor base referencia o nome no seu próprio módulo.
motor.imagem_ameaca=imagem_ameaca

class AmeacaBioma(BaseAmeaca):
    pass
