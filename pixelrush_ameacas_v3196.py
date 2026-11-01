"""v3.196.0 — articulação pré-renderizada dos 15 perigos ativos.

Somente a superfície de desenho muda. A herança conserva o update, o ritmo de
3 fases, o rect, a hitbox, as colisões, o spawn e o ciclo de dano do gêiser.
Os recortes são RETIRADOS do sprite ANTES da recolocação; nenhuma pata/asa é
simplesmente desenhada por cima de outra igual. Nenhuma operação geométrica
ocorre a cada tick. Todos os seis/nove quadros são preparados por espécie.
"""
import pygame
import numpy as np
from pixelrush_ameacas_v3195 import (
    AMEACAS, POR_BIOMA, escorpiao_frame, cor_aviso_ameaca,
    AmeacaBioma as _Anterior, imagem_ameaca as _original,
    refinar_sprite,
)
from pixelrush_ameacas_v3186 import ATIVOS, quadro_intermediario

ESTATICOS = frozenset(AMEACAS) - ATIVOS
VOADORES = frozenset(('C2', 'N2', 'V2', 'F2', 'IC2'))
# Polygon coordinates from existing original 64x64 painter (never external art).
# (vertices, dx, dy, articulation side). Masks deliberately protect the torso.
PERFIS_PARTES = {
    'C1': [([(0,28),(16,28),(17,49),(0,50)],-1,-2,'left'),
           ([(13,49),(29,49),(28,63),(12,63)],2,-1,'bottom'),
           ([(38,48),(52,48),(53,63),(37,63)],-2,1,'bottom')],
    'C2': [([(0,6),(23,7),(22,25),(17,43),(0,46)],0,-4,'left'),
           ([(41,7),(63,6),(63,46),(47,43),(42,25)],0,-4,'right')],
    'N1': [([(26,8),(49,9),(53,31),(28,30)],1,-2,'top'),
           ([(16,52),(31,52),(31,63),(13,63)],2,-1,'bottom'),
           ([(33,52),(50,52),(51,63),(32,63)],-2,1,'bottom')],
    'N2': [([(0,5),(24,7),(22,23),(16,44),(0,45)],0,-4,'left'),
           ([(40,7),(63,5),(63,45),(47,44),(42,23)],0,-4,'right')],
    'D1': [([(44,13),(63,13),(63,37),(45,36)],1,-2,'top'),
           ([(12,46),(35,48),(33,61),(10,60)],-2,-1,'left')],
    'D2': [([(25,42),(41,43),(40,62),(20,62)],-2,-1,'bottom'),
           ([(42,42),(60,40),(64,62),(41,62)],2,1,'bottom')],
    'V1': [([(10,48),(30,48),(28,64),(10,64)],2,-2,'bottom'),
           ([(40,48),(61,48),(62,64),(39,64)],-2,1,'bottom'),
           ([(44,29),(61,30),(61,46),(47,46)],1,-1,'right')],
    'V2': [([(0,5),(25,6),(22,28),(18,48),(0,46)],0,-4,'left'),
           ([(39,6),(63,5),(63,46),(46,48),(42,28)],0,-4,'right')],
    'F1': [([(46,13),(63,14),(64,34),(48,34)],2,-2,'top')],
    'F2': [([(0,6),(24,7),(21,25),(17,43),(0,46)],0,-4,'left'),
           ([(40,6),(63,6),(63,45),(47,43),(43,26)],0,-4,'right')],
    'CF1': [([(30,1),(42,1),(42,20),(29,20)],2,-2,'top')],
    'CF2': [([(0,17),(19,18),(19,46),(0,47)],1,-3,'left'),
            ([(51,17),(64,17),(64,47),(51,46)],-1,3,'right')],
    'IC1': [([(5,10),(29,11),(29,33),(11,43)],-1,-4,'left'),
            ([(35,11),(60,10),(61,42),(36,33)],1,-4,'right'),
            ([(13,48),(27,48),(27,63),(10,63)],1,-1,'bottom')],
    'IC2': [([(0,8),(24,8),(22,23),(17,45),(0,48)],0,-3,'left'),
            ([(42,8),(64,8),(64,48),(47,45),(43,23)],0,-3,'right')],
}
# A chaminé do gêiser é um líquido, portanto a animação segura é o transporte
# espacial das espumas já existentes, apenas nos pixels internos; não mover
# rachadura, contorno, placa de advertência ou estágio de dano.
_GEISER = 'V4'
_CACHE_FRAMES = {}
_BYTES_CACHE = 0
MAX_CACHE_BYTES = 3 * 1024 * 1024


def _mascara_poligono(tamanho, pontos):
    w,h = tamanho
    surf = pygame.Surface(tamanho,pygame.SRCALPHA,32)
    vertices = [(min(w-1,max(0,round(x*w/64))),min(h-1,max(0,round(y*h/64)))) for x,y in pontos]
    pygame.draw.polygon(surf,(255,255,255,255),vertices)
    return pygame.surfarray.array_alpha(surf)>0


def _articular(codigo, origem, intensidade):
    """Move pixels realmente; destrói a posição anterior ANTES da recomposição."""
    w,h=origem.get_size()
    entrada=pygame.surfarray.array3d(origem)
    alfa=pygame.surfarray.array_alpha(origem)
    rgba=np.empty((w,h,4),dtype=np.uint8)
    rgba[:,:,:3]=entrada;rgba[:,:,3]=alfa
    saida=rgba.copy()
    zonas=PERFIS_PARTES[codigo]
    # Extrair TODOS os membros a partir de um único quadro, para que um membro
    # movido nunca entre como material de origem de outro.
    movimentos=[]
    ocupados=np.zeros((w,h),dtype=bool)
    for vertices,dx,dy,articulacao in zonas:
        area=_mascara_poligono((w,h),vertices) & (alfa>=170) & ~ocupados
        ocupados |= area
        xs,ys=np.nonzero(area)
        if len(xs)==0:continue
        # Amplitude cresce progressivamente em direção à ponta livre.
        if articulacao=='left':power=np.clip((.47*w-xs)/(.47*w),.25,1.)
        elif articulacao=='right':power=np.clip((xs-.53*w)/(.47*w),.25,1.)
        elif articulacao=='top':power=np.clip((.54*h-ys)/(.54*h),.3,1.)
        else:power=np.clip((ys-.62*h)/(.38*h),.3,1.)
        sx=np.rint(dx*w/64*intensidade*power).astype(np.int32)
        sy=np.rint(dy*h/64*intensidade*power).astype(np.int32)
        destx=np.clip(xs+sx,0,w-1);desty=np.clip(ys+sy,0,h-1)
        movimentos.append((xs,ys,destx,desty,rgba[xs,ys].copy()))
    for xs,ys,_,_,_ in movimentos:
        saida[xs,ys]=0
    for xs,ys,tx,ty,pixels in movimentos:
        # Previne pintura de asas sobre o tronco ou de membros sobre outros.
        livre=(saida[tx,ty,3] < 170)
        saida[tx[livre],ty[livre]]=pixels[livre]
        # Restitui raiz protegida em pontos onde a asa se prende ao corpo.
        # Mantém o corpo sem cortes nas zonas de sobreposição.
    protegido=(ocupados & (alfa>0) & (saida[:,:,3]==0))
    # Um pequeno vão de articulação é fisicamente possível, mas a parte
    # interna contígua ao tronco não deve ficar furada por deslocamento.
    vizinho=np.zeros_like(protegido)
    vizinho[1:,:] |= (~ocupados[:-1,:] & (alfa[:-1,:]>=170))
    vizinho[:-1,:] |= (~ocupados[1:,:] & (alfa[1:,:]>=170))
    vizinho[:,1:] |= (~ocupados[:,:-1] & (alfa[:,:-1]>=170))
    vizinho[:,:-1] |= (~ocupados[:,1:] & (alfa[:,1:]>=170))
    sel=protegido & vizinho
    saida[sel]=rgba[sel]
    # Audita conectividade em cada quadro pré-renderizado. Remover somente
    # ilhotas 1-2 px NOVAS, nunca as pequenas partículas que já existiam.
    def fragmentos(dados):
        mapa=(dados[:,:,3]>=170).copy()
        vistos=[]
        for px in range(w):
            for py in range(h):
                if not mapa[px,py]:continue
                ilha=[(px,py)];mapa[px,py]=False;idx=0
                while idx<len(ilha):
                    cx,cy=ilha[idx];idx+=1
                    for nx,ny in ((cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)):
                        if 0<=nx<w and 0<=ny<h and mapa[nx,ny]:
                            mapa[nx,ny]=False;ilha.append((nx,ny))
                if len(ilha)<=2:vistos.append(frozenset(ilha))
        return vistos
    ilhotas_antigas=set(fragmentos(rgba))
    for ilha in fragmentos(saida):
        if ilha not in ilhotas_antigas:
            for px,py in ilha:saida[px,py]=0
    final=pygame.Surface((w,h),pygame.SRCALPHA,32)
    pygame.surfarray.blit_array(final,saida[:,:,:3])
    a=pygame.surfarray.pixels_alpha(final)
    a[:,:]=saida[:,:,3]
    del a
    return final


def _vapor_organico(origem, tempo):
    """Advecta detalhes internos da coluna; canal alfa e borda 100% iguais."""
    w,h=origem.get_size()
    cor=pygame.surfarray.array3d(origem)
    a=pygame.surfarray.array_alpha(origem)
    xx=np.arange(w)[:,None]
    yy=np.arange(h)[None,:]
    zona=(xx>=int(w*.40)) & (xx<=int(w*.66)) & (yy>=int(h*.22)) & (yy<=int(h*.77))
    # Apenas miolo com vizinhos opacos, evitando contorno e deslocamento de vapor
    # na borda. Pixels de corpo visivelmente sobem sem cores fabricadas.
    interno=(a==255)
    interno[1:,:] &= (a[:-1,:]==255)
    interno[:-1,:] &= (a[1:,:]==255)
    deslize=1+(tempo%2)
    fonte_y=np.minimum(h-1,np.arange(h)+deslize)
    seguro=zona & interno & (a[:,fonte_y]==255)
    saida=origem.copy()
    arr=pygame.surfarray.pixels3d(saida)
    transferido=cor[:,fonte_y,:]
    arr[seguro]=transferido[seguro]
    del arr
    return saida


def _construir(codigo):
    global _BYTES_CACHE
    if codigo in _CACHE_FRAMES:return
    if codigo not in ATIVOS:raise ValueError('Perigo estatico nao recebe animacao: '+codigo)
    quadros=[]
    for fase in range(3):
        base=_original(codigo,fase)
        if codigo==_GEISER:
            intermediario=refinar_sprite(codigo,quadro_intermediario(codigo,fase))
            quadros.append((base,intermediario) if fase==0 else
                          (base,_vapor_organico(intermediario,fase)))
            continue
        if codigo in VOADORES:
            # 9 poses: 3 fases herdadas x [pose, extensão, retração].
            variantes=(base, _articular(codigo,base,1.65),
                       _articular(codigo,refinar_sprite(codigo,quadro_intermediario(codigo,fase)),-1.65))
        else:
            # 6 poses: 3 fases herdadas x [pose, articulação real].
            variantes=(base,_articular(codigo,
                        refinar_sprite(codigo,quadro_intermediario(codigo,fase)),
                        1.85 if fase%2==0 else -1.85))
        quadros.append(variantes)
    soma=sum(im.get_width()*im.get_height()*4 for conj in quadros for im in conj)
    if _BYTES_CACHE+soma>MAX_CACHE_BYTES:
        raise MemoryError('Limite rigido do cache organico excedido')
    _CACHE_FRAMES[codigo]=tuple(quadros)
    _BYTES_CACHE+=soma


def imagem_ameaca(codigo,fase=0):
    """Imagem de referência antiga, inclusive estáticos, para lojas e painéis."""
    return _original(codigo,fase)


class AmeacaBioma(_Anterior):
    """Wrapper de animação; zero alterações no simulador/collision engine."""
    def __init__(self,x,codigo):
        super().__init__(x,codigo)
        if codigo in ATIVOS:
            _construir(codigo)
            self.image=_CACHE_FRAMES[codigo][0][0]

    def update(self,velocidade_jogo):
        super().update(velocidade_jogo)
        if self.codigo not in ATIVOS:return
        fases=_CACHE_FRAMES[self.codigo]
        poses=fases[self._fase]
        if self.codigo==_GEISER:
            # 38 ticks da rachadura não perigosa inalterados; fase 1/2 intacta.
            subfase=int(self.ticks%10>=5)
        elif len(poses)==3:
            subfase=min(2,(self.ticks%9)//3)
        else:
            subfase=int(self.ticks%9>=5)
        self.image=poses[subfase]
