# -*- coding: utf-8 -*-
"""QA749: cache de PLANO de tiles da Cidade real, sem guardar pixels.

Preserva a API estatica original CityPilotScene._layer_tiles(travel, layer).
Cada Layer e proprietaria do seu pequeno plano; sem chave global de mundo,
sem references de Surface extras e com invalidacao a cada novo travel.
"""
import os
from functools import wraps
from weakref import WeakValueDictionary

_INSTALADO=False
_ORIGINAL=None
_LAYER_REFS=WeakValueDictionary()
_CACHE_ATTR='_qa_tile_plan_v327749'
_STATUS={'chamadas':0,'hits':0,'misses':0,'fallbacks':0,
         'max_tiles_retidos':0}


def estatisticas():
    return dict(_STATUS,instalado=_INSTALADO,
                layers_com_plano=len(_LAYER_REFS))


def instalar():
    global _INSTALADO,_ORIGINAL
    if _INSTALADO:
        return
    if os.environ.get('PIXELRUSH_QA_CIDADE_TILE_PLAN','1')!='1':
        return
    from pixelrush_city2_v3125 import CityPilotScene
    _ORIGINAL=CityPilotScene._layer_tiles

    @wraps(_ORIGINAL)
    def plano(travel,layer):
        _STATUS['chamadas']+=1
        if not isinstance(travel,(int,float)):
            _STATUS['fallbacks']+=1
            return _ORIGINAL(travel,layer)
        try:
            cached=getattr(layer,_CACHE_ATTR,None)
            if (cached is not None and cached[0]==travel and
                    cached[2] is layer.sequence and
                    cached[3] is layer.variants and
                    cached[4] is layer.flips):
                _STATUS['hits']+=1
                return cached[1]
            tiles=tuple(_ORIGINAL(travel,layer))
            setattr(layer,_CACHE_ATTR,
                    (travel,tiles,layer.sequence,layer.variants,layer.flips))
            _LAYER_REFS[id(layer)]=layer
            _STATUS['misses']+=1
            _STATUS['max_tiles_retidos']=max(_STATUS['max_tiles_retidos'],len(tiles))
            return tiles
        except (AttributeError,TypeError,ValueError,MemoryError):
            _STATUS['fallbacks']+=1
            return _ORIGINAL(travel,layer)

    # Preserva a assinatura estatica da versao real v3118->v3125.
    CityPilotScene._layer_tiles=staticmethod(plano)
    _INSTALADO=True


def restaurar_para_teste():
    global _INSTALADO
    if _INSTALADO:
        from pixelrush_city2_v3125 import CityPilotScene
        CityPilotScene._layer_tiles=staticmethod(_ORIGINAL)
    for layer in tuple(_LAYER_REFS.values()):
        if hasattr(layer,_CACHE_ATTR):
            delattr(layer,_CACHE_ATTR)
    _LAYER_REFS.clear()
    _STATUS.update(chamadas=0,hits=0,misses=0,fallbacks=0,max_tiles_retidos=0)
    _INSTALADO=False
