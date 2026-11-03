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
    # O plano so e reutilizado quando o jogo solicita varios canais
    # image/normal/geometry/material para a MESMA posicao. Na corrida SDL
    # de um unico canal ele aloca tuples e atributos sem obter cache hits.
    # O modo auto evita esse overhead no quinto quadro sem remover o recurso.
    modo=os.environ.get('PIXELRUSH_QA_CIDADE_TILE_PLAN','auto')
    if modo=='0' or (modo=='auto' and
            os.environ.get('PIXELRUSH_GPU','off').lower() in ('off','0','false','none')):
        return
    from pixelrush_city2_v3125 import CityPilotScene
    _ORIGINAL=CityPilotScene._layer_tiles

    @wraps(_ORIGINAL)
    def plano(travel,layer):
        _STATUS['chamadas']+=1
        if not isinstance(travel,(int,float)):
            _STATUS['fallbacks']+=1
            yield from _ORIGINAL(travel,layer)
            return
        # NUNCA incluir "yield from" no try de calculo: excecao no
        # consumidor durante o yield poderia ser capturada e provocar
        # renderizacao duplicada de chunks/sprites (regressao v749).
        try:
            cached=getattr(layer,_CACHE_ATTR,None)
            if (cached is not None and cached[0]==travel and
                    cached[2] is layer.sequence and
                    cached[3] is layer.variants and
                    cached[4] is layer.flips):
                _STATUS['hits']+=1
                tiles=cached[1]
            else:
                tiles=tuple(_ORIGINAL(travel,layer))
                setattr(layer,_CACHE_ATTR,
                        (travel,tiles,layer.sequence,layer.variants,layer.flips))
                _LAYER_REFS[id(layer)]=layer
                _STATUS['misses']+=1
                _STATUS['max_tiles_retidos']=max(_STATUS['max_tiles_retidos'],len(tiles))
        except (AttributeError,TypeError,ValueError,MemoryError):
            _STATUS['fallbacks']+=1
            yield from _ORIGINAL(travel,layer)
            return
        yield from tiles

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
