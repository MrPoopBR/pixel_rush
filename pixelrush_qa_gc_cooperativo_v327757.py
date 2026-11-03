# -*- coding: utf-8 -*-
"""PIXEL RUSH fechamento QA — GC cooperativo fora do quinto quadro.

Nao muda objetos do jogo, RNG, pygame surfaces ou fisica. Apenas realoca
coletas cíclicas Python (nao refcount) para frames de apresentacao que NAO
coincidem com o redraw 5:1. Coleta imediatamente sob pressao persistente
de memoria, sem desligar nunca a destruicao por refcount. Rollback completo.
"""
import gc
import os
from functools import wraps

_ATIVO=False
_FLIP_ORIGINAL=None
_GC_ORIGINAL=None
_FRAMES=0
_STATS={'coletas_0':0,'coletas_1':0,'coletas_2':0,'frames':0,
        'coletas_no_quinto_quadro':0,'fallbacks':0,
        'gc_original_restaurado':False}

def diagnostico():
    return dict(_STATS,ativo=_ATIVO,
                gc_auto_ativo=gc.isenabled(),fase_coleta=1,
                homologia_android=False)

def instalar():
    """Instalar depois dos demais wrappers de flip na entrada QA do jogo."""
    global _ATIVO,_FLIP_ORIGINAL,_GC_ORIGINAL,_FRAMES
    if _ATIVO:
        return
    if os.environ.get('PIXELRUSH_QA_ANDROID','0')!='1':
        return
    if os.environ.get('PIXELRUSH_QA_GC_COOPERATIVO','1')!='1':
        return
    if not gc.isenabled():
        # Nao substituir deliberadamente uma politica do hospedeiro.
        _STATS['fallbacks']+=1
        return
    import pygame
    _FLIP_ORIGINAL=pygame.display.flip
    _GC_ORIGINAL=gc.isenabled()
    _FRAMES=0
    gc.disable()

    @wraps(_FLIP_ORIGINAL)
    def apresentar():
        global _FRAMES
        resultado=_FLIP_ORIGINAL()
        _FRAMES+=1
        _STATS['frames']=_FRAMES
        # Coletas pequenas fora do frame de redraw. Ficam fora da
        # fisica/ticks e NAO executam o render nem alteram RNG.
        if _FRAMES%5!=1:
            return resultado
        if _FRAMES>=30 and _FRAMES%30==1:
            gc.collect(0)
            _STATS['coletas_0']+=1
        if _FRAMES>=180 and _FRAMES%180==1:
            gc.collect(1)
            _STATS['coletas_1']+=1
        if _FRAMES>=900 and _FRAMES%900==1:
            gc.collect(2)
            _STATS['coletas_2']+=1
        return resultado

    try:
        pygame.display.flip=apresentar
    except (TypeError,AttributeError):
        _STATS['fallbacks']+=1
        if _GC_ORIGINAL:
            gc.enable()
        _FLIP_ORIGINAL=_GC_ORIGINAL=None
        return
    _ATIVO=True

def restaurar_para_teste():
    global _ATIVO,_FLIP_ORIGINAL,_GC_ORIGINAL,_FRAMES
    if _ATIVO:
        import pygame
        pygame.display.flip=_FLIP_ORIGINAL
    if _GC_ORIGINAL and not gc.isenabled():
        gc.enable()
        _STATS['gc_original_restaurado']=True
    _ATIVO=False
    _FLIP_ORIGINAL=None
    _GC_ORIGINAL=None
    _FRAMES=0
