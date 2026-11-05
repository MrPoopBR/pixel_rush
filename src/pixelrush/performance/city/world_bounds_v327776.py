# -*- coding: utf-8 -*-
"""QA776 R11: composicao City 2.5D por bbox SDL, SOMENTE destino RGB16.

R11 no A54 88.631ms/call. Linux pygame-ce 2.5.8, City REAL:
bbox + blit em RGB16 ~15% melhor no blit de 450x500, RGB24/32 pior.
Sem gate por formato, alteraria visual/RGB oculto; jamais ativar neles.
"""
import os
import pygame

_APROVADO=0
_FALLBACK=0
_ULTIMO_BPP=None

def diagnostico():
    return {'ativo_qa':os.environ.get('PIXELRUSH_QA_ANDROID')=='1',
            'recortes_rgb16':_APROVADO,'originais':_FALLBACK,
            'ultimo_destino_bpp':_ULTIMO_BPP,
            'perfis_aprovados':['RGB16 opaco sem colorkey, SRCALPHA na origem'],
            'hardware_medido':False}

def compor(destino,origem,y):
    """Desenhar byte-exato no caminho geral, otimizar somente condicao provada."""
    global _APROVADO,_FALLBACK,_ULTIMO_BPP
    _ULTIMO_BPP=destino.get_bitsize()
    if (os.environ.get('PIXELRUSH_QA_R11_WORLD_BBOX','1')!='1'
            or destino.get_bitsize()!=16
            or destino.get_flags() & pygame.SRCALPHA
            or destino.get_colorkey() is not None
            or destino.get_alpha() not in (None,255)
            or origem.get_size()!=(450,500)
            or not (origem.get_flags() & pygame.SRCALPHA)
            or origem.get_colorkey() is not None
            or origem.get_alpha() not in (None,255)):
        _FALLBACK+=1
        return destino.blit(origem,(0,y))
    try:
        rect=origem.get_bounding_rect(min_alpha=1)
        # alpha0 nao pode afetar destino RGB16 opaco (SDL alpha-blend).
        if not rect.width or not rect.height:
            _APROVADO+=1
            return pygame.Rect(0,y,0,0)
        result=destino.blit(origem,(rect.x,y+rect.y),rect)
        _APROVADO+=1
        return result
    except (pygame.error,ValueError,TypeError,MemoryError):
        _FALLBACK+=1
        return destino.blit(origem,(0,y))
