# -*- coding: utf-8 -*-
"""QA v3.277.76: vinheta SDL pixel-exata sem processar centro transparente.

GameFeel original: 450x800 com efeito somente nas 48 colunas laterais e
25 linhas superior/inferior. Verificacao C/SDL uma vez por Surface. Destinos
SRCALPHA (inclusive RGB oculto), formatos diferentes e arte inesperada
sempre usam blit original. Nenhum save, RNG, fisica, sprite ou efeito removido.
"""
import os
from weakref import WeakKeyDictionary
import pygame
from pixelrush_profiler_v3204 import sub_inicio as _sub_inicio, sub_fim as _sub_fim

W,H=450,800
_X,_Y=48,25
_BORDAS=(
    pygame.Rect(0,0,W,_Y),
    pygame.Rect(0,H-_Y,W,_Y),
    pygame.Rect(0,_Y,_X,H-2*_Y),
    pygame.Rect(W-_X,_Y,_X,H-2*_Y),
)
_CENTRO=pygame.Rect(_X,_Y,W-2*_X,H-2*_Y)
_SEGURAS=WeakKeyDictionary()
_STATS={'tentativas':0,'rapido':0,'fallback':0,
        'verificacoes':0,'centro_rejeitado':0}

def diagnostico():
    return dict(_STATS,superficies_verificadas=len(_SEGURAS))

def restaurar_para_teste():
    _SEGURAS.clear()
    for k in _STATS:_STATS[k]=0

def _seguro(efeito):
    valido=_SEGURAS.get(efeito)
    if valido is not None:return valido
    _STATS['verificacoes']+=1
    try:
        # Alpha=0 em TODO pixel interno; nenhuma amostragem parcial.
        valido=pygame.mask.from_surface(
            efeito.subsurface(_CENTRO),threshold=0).count()==0
    except (pygame.error,ValueError,TypeError,MemoryError):
        valido=False
    _SEGURAS[efeito]=valido
    if not valido:_STATS['centro_rejeitado']+=1
    return valido

def desenhar_vinheta(destino,efeito):
    """Substituicao somente na Surface RGB32 usada pelo render principal.

    O alpha0 de uma fonte SRCALPHA pode modificar RGB oculto de DESTINO
    SRCALPHA, portanto essa combinacao permanece no caminho original.
    """
    _STATS['tentativas']+=1
    _sub_inicio('r11_post_vinheta')
    try:
        return _desenhar_validado(destino,efeito)
    finally:
        _sub_fim()

def _desenhar_validado(destino,efeito):
    if (os.environ.get('PIXELRUSH_QA_R11_VINHETA','1')!='1' or
            destino.get_flags() & pygame.SRCALPHA or
            destino.get_colorkey() is not None or
            destino.get_bitsize()!=32 or destino.get_size()!=(W,H) or
            efeito.get_size()!=(W,H) or
            not (efeito.get_flags() & pygame.SRCALPHA) or
            efeito.get_colorkey() is not None or
            efeito.get_alpha() not in (None,255) or
            not _seguro(efeito)):
        _STATS['fallback']+=1
        return destino.blit(efeito,(0,0))
    for r in _BORDAS:
        destino.blit(efeito,r.topleft,r)
    _STATS['rapido']+=1
    return None
