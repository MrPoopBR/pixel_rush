"""Pixel Rush v3.221.0 — anatomia Premium 4.0 com atlases offline.

Os novos quadros são PIXEL ART produzida a partir das poses da v3.196. Os
arquivos PNG foram gerados antes do jogo: nenhuma morfologia/NumPy adicional é
executada durante a corrida. Herança conserva estado, física, fases e hitbox.
"""
from pathlib import Path
import math
import pygame
from pixelrush_polimento_atores_prod_v32772 import refinar_quadro_inimigo as _prod_refinar_inimigo
from pixelrush_ameacas_v3196 import (
    AMEACAS, POR_BIOMA, escorpiao_frame, cor_aviso_ameaca,
    ATIVOS, _construir, _CACHE_FRAMES,
    AmeacaBioma as _Anterior, imagem_ameaca as _imagem_original,
)

_DIRETORIO = Path(__file__).resolve().parent / 'assets' / 'inimigos_v3221'
_QUADROS = {}
_POR_IDENTIDADE = {}
_ANIMACOES_VOO = {}
_CACHE_BYTES = 0
MAX_CACHE_BYTES = 2*1024*1024


def _preparar(codigo):
    global _CACHE_BYTES
    if codigo in _QUADROS:return
    if codigo not in ATIVOS:return
    _construir(codigo)
    anteriores=_CACHE_FRAMES[codigo]
    largura,altura=anteriores[0][0].get_size()
    total=sum(len(poses) for poses in anteriores)
    atlas=pygame.image.load(str(_DIRETORIO / (codigo+'.png'))).convert_alpha()
    if atlas.get_size()!=(largura*total,altura):
        raise ValueError('Atlas incorreto para '+codigo)
    bytes_novos=total*largura*altura*4
    if _CACHE_BYTES+bytes_novos>MAX_CACHE_BYTES:
        raise MemoryError('Cache de inimigos Premium 4.0 excede 2 MiB')
    quadros=[];i=0
    for fase in anteriores:
        novos=[]
        for original in fase:
            novo=atlas.subsurface((i*largura,0,largura,altura)).copy()
            # RGB do próprio frame: sem criar superfícies ou modificar colisão.
            _prod_refinar_inimigo(novo, codigo, i)
            novos.append(novo)
            _POR_IDENTIDADE[id(original)]=novo
            i+=1
        quadros.append(tuple(novos))
    _QUADROS[codigo]=tuple(quadros)
    if codigo=="C2":
        # O pombo usa TODAS as poses do atlas existente (sem gerar frames).
        # O custo de montagem da sequencia ocorre só no primeiro spawn.
        _ANIMACOES_VOO[codigo]=tuple(frame for fase in quadros for frame in fase)
    _CACHE_BYTES+=bytes_novos


def imagem_ameaca(codigo,fase=0):
    if codigo not in ATIVOS:return _imagem_original(codigo,fase)
    _preparar(codigo)
    return _QUADROS[codigo][int(fase)%3][0]


class AmeacaBioma(_Anterior):
    """A troca é só visual. Atualização e hitboxes vêm de v3.196.0."""
    def __init__(self,x,codigo):
        super().__init__(x,codigo)
        if codigo in ATIVOS:
            _preparar(codigo)
            self.image=_POR_IDENTIDADE[id(self.image)]
        if codigo=="C2":
            sequencia=_ANIMACOES_VOO.get("C2",())
            self._fase_voo=float(self._giro%len(sequencia)) if sequencia else 0.0

    def update(self,velocidade_jogo):
        super().update(velocidade_jogo)
        if self.codigo in ATIVOS:
            self.image=_POR_IDENTIDADE[id(self.image)]
        # Movimento próprio em C1/C2/N1. A arte é pré-calculada, sem novas
        # superfícies e sem RNG extra durante o quadro.
        if self.codigo == 'C1':
            self.rect.x = round(self._x + 14 * math.sin(self.ticks * .095 + self._giro))
            self.rect.y = self._base_y + int(abs(math.sin(self.ticks*.15))*2)
        elif self.codigo == 'C2':
            self.rect.x = round(self._x + 10*math.sin(self.ticks*.12+self._giro))
            self.rect.y = round(self._base_y + 8*math.sin(self.ticks*.19) +
                                6*math.sin(self.ticks*.05+self._giro))
            # Fase fracionaria acompanha velocidade e percorre poses
            # intermediarias reais do atlas sem recomputar pixels.
            sequencia=_ANIMACOES_VOO.get("C2",())
            if sequencia:
                self._fase_voo += min(.88,.34 + float(velocidade_jogo)*.022)
                self.image=sequencia[int(self._fase_voo)%len(sequencia)]
        elif self.codigo == 'N1':
            self.rect.x = round(self._x + 7*math.sin(self.ticks*.078+self._giro))
            self.rect.y = self._base_y + round(abs(math.sin(self.ticks*.11))*2)
