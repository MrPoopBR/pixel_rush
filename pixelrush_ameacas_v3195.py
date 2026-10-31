"""Pixel Rush v3.195.0 — direção de arte interna dos 28 perigos existentes.

Não altera alfa, bordas, dimensões, rect, máscaras, fases, colisão ou spawn.
Sombras por volume, acentos por material e pontos faciais existentes são
pré-renderizados e cacheados; o update do motor anterior continua intacto.
"""
import numpy as np
import pygame
from pixelrush_ameacas_v3187 import (
    AMEACAS, POR_BIOMA, escorpiao_frame, cor_aviso_ameaca,
    AmeacaBioma as _AmeacaAnterior,
    imagem_ameaca as _imagem_anterior,
)

# Perigo -> (familia de material, paleta de iluminacao); todos os 28 perfis.
PERFIS = {
    'C1': ('organico',(232,191,175)), 'C2': ('penas',(219,232,255)),
    'C3': ('sinal',(255,210,136)), 'C4': ('sinal',(255,218,156)),
    'N1': ('organico',(230,244,255)), 'N2': ('penas',(233,247,255)),
    'N3': ('mineral',(197,247,255)), 'N4': ('fibroso',(236,221,201)),
    'D1': ('escamas',(241,216,148)), 'D2': ('casco',(239,209,144)),
    'D3': ('mineral',(243,206,153)), 'D4': ('osso',(247,231,195)),
    'V1': ('escamas',(255,189,103)), 'V2': ('asas',(255,175,137)),
    'V3': ('mineral',(211,174,231)), 'V4': ('vapor',(226,241,246)),
    'F1': ('casco',(212,229,173)), 'F2': ('penas',(225,239,173)),
    'F3': ('fibroso',(210,180,135)), 'F4': ('fibroso',(194,207,152)),
    'CF1': ('tecnico',(153,243,252)), 'CF2': ('tecnico',(147,242,253)),
    'CF3': ('tecnico',(153,242,250)), 'CF4': ('energia',(199,167,250)),
    'IC1': ('casco',(192,247,218)), 'IC2': ('asas',(216,247,252)),
    'IC3': ('mineral',(197,246,255)), 'IC4': ('mineral',(205,211,248)),
}
# As coordenadas faciais vêm das poses 64x64 originais do jogo.
# Apenas realçamos pixels claros JÁ EXISTENTES, sem criar novos olhos.
OLHOS = {
    'C1': ((49,36),), 'C2': ((42,29),), 'N1': ((39,24),),
    'N2': ((30,29),(42,29)), 'D1': ((51,25),), 'D2': ((45,33),),
    'F1': ((57,27),), 'F2': ((38,28),), 'IC1': ((51,40),),
    'IC2': ((27,29),(40,29)), 'V2': ((28,33),(39,33)),
    'CF1': ((29,29),(43,29)), 'CF2': ((34,33),),
}
_CACHE = {}
_JA_REFINADO = set()


def _erosao(m):
    """Vizinhanca cruzada inteiramente opaca, para proteger bordas pixeladas."""
    r = m.copy()
    r[0, :] = False; r[-1, :] = False
    r[:, 0] = False; r[:, -1] = False
    r[1:, :] &= m[:-1, :]
    r[:-1, :] &= m[1:, :]
    r[:, 1:] &= m[:, :-1]
    r[:, :-1] &= m[:, 1:]
    return r


def refinar_sprite(codigo, original):
    """Melhora material e leitura de volume; máscara alfa 100% idêntica."""
    if id(original) in _JA_REFINADO:
        return original
    ident = (codigo, id(original))
    imagem = _CACHE.get(ident)
    if imagem is not None:
        return imagem
    familia, luz = PERFIS[codigo]
    w, h = original.get_size()
    fonte = pygame.surfarray.array3d(original)
    alpha = pygame.surfarray.array_alpha(original)
    lum = (fonte[:,:,0].astype(np.int16)*3 + fonte[:,:,1].astype(np.int16)*6
           + fonte[:,:,2].astype(np.int16))//10
    solido = alpha == 255
    interno = _erosao(solido)
    # Protege o contorno, sombras muito escuras, reflexos e marcações brilhantes.
    material = interno & (lum >= 62) & (lum <= 219)
    xx = np.arange(w,dtype=np.int16)[:,None]
    yy = np.arange(h,dtype=np.int16)[None,:]
    # Sombreamento em blocos de pixel art: cima/esquerda mais claro;
    # abaixo/direita, peso visual. Não muda deslocamento nem sprites físicos.
    pos = (xx / max(1,w-1) * .36 + yy / max(1,h-1) * .64)
    claro = material & (pos < .42)
    escuro = material & (pos > .61)
    # Material diferente pede marcação diferente; nenhum ruído aleatório.
    if familia in ('escamas','casco'):
        relevo = ((xx//5 + yy//4) % 3 == 0)
    elif familia in ('fibroso','osso'):
        relevo = ((yy//3 + xx//11) % 4 == 0)
    elif familia in ('mineral','vapor'):
        relevo = ((2*xx//9 - yy//7) % 4 == 0)
    elif familia in ('tecnico','energia','sinal'):
        relevo = ((xx//9 + yy//6) % 5 == 0)
    else:
        relevo = ((xx//7 + yy//5) % 4 == 0)
    cor = fonte.astype(np.int16)
    for ch in range(3):
        # Acento cromático ligado à paleta de cada criatura/material.
        aproxima = (luz[ch] - cor[:,:,ch])//6
        cor[:,:,ch] += np.where(claro, 8 + aproxima, 0)
        cor[:,:,ch] -= np.where(escuro, 9, 0)
        cor[:,:,ch] += np.where(material & relevo & ~escuro, 3 + aproxima//3, 0)
    # Mais separação de volume nas faixas internas SEM tocar a borda externa.
    segunda = _erosao(interno)
    luz_interna = interno & ~segunda & (lum >= 80) & (lum < 210)
    cor[:,:,0] += np.where(luz_interna & (xx < w*.40) & (yy < h*.65), 6, 0)
    cor[:,:,1] += np.where(luz_interna & (xx < w*.40) & (yy < h*.65), 5, 0)
    cor[:,:,2] += np.where(luz_interna & (xx < w*.40) & (yy < h*.65), 4, 0)
    # Para criaturas com olhos existentes: realçar 1 pixel claro dentro
    # da região facial, somente quando a pose contém esse detalhe visível.
    for face in OLHOS.get(codigo, ()):
        fx = round(face[0] * w / 64)
        fy = round(face[1] * h / 64)
        x1,x2=max(0,fx-2),min(w,fx+3)
        y1,y2=max(0,fy-2),min(h,fy+3)
        if x1>=x2 or y1>=y2:continue
        area = solido[x1:x2,y1:y2] & (lum[x1:x2,y1:y2] >= 135)
        if not np.any(area):continue
        candidatos = np.where(area,lum[x1:x2,y1:y2],-1)
        dx,dy=np.unravel_index(int(np.argmax(candidatos)),candidatos.shape)
        x,y=x1+dx,y1+dy
        # Realce de brilho existente sem redesenhar olho nem retirar pupila.
        cor[x,y,:] = np.minimum(255,cor[x,y,:]+np.array((13,12,10)))
    novo=original.copy()
    pixels=pygame.surfarray.pixels3d(novo)
    pixels[:,:,:]=np.clip(cor,0,255).astype(np.uint8)
    del pixels
    assert np.array_equal(pygame.surfarray.array_alpha(novo),alpha)
    assert novo.get_size()==original.get_size()
    _CACHE[ident] = novo
    _JA_REFINADO.add(id(novo))
    return novo


def imagem_ameaca(codigo, fase=0):
    """Compatibilidade com visualizações/loja sem recriar quadros no update."""
    return refinar_sprite(codigo, _imagem_anterior(codigo, fase))


class AmeacaBioma(_AmeacaAnterior):
    """Herdança da lógica antiga: alteração somente da superfície desenhada."""
    def __init__(self, x, codigo):
        super().__init__(x,codigo)
        self.image=refinar_sprite(self.codigo,self.image)

    def update(self, velocidade_jogo):
        super().update(velocidade_jogo)
        self.image=refinar_sprite(self.codigo,self.image)
