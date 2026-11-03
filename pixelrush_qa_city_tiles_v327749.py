# -*- coding: utf-8 -*-
"""QA 3.277.49: reuso de PLANO de tiles no compositor da Cidade real v3125.

Nas chamadas de _city_surface para image, normal, fxmask, geometry etc.,
travel e layers costumam ser idênticos. Recalcular divmod/indices de layers
para cada canal e desnecessario. Cache guarda APENAS tuples de metadados,
nunca RGBA, nem mundo, nem sprites; todas as chamadas de render continuam.

Jogo, física, clima, phase, iluminação, blend, ordem de desenho e pixel RGBA
permanecem controlados pelas rotinas originais. Retorna tupla consumível
como iterable (contrato de _layer_tiles). Sem alocacao por pixel.
"""
import os
from weakref import WeakKeyDictionary
from functools import wraps

_INSTALADO=False
_ORIGINAL=None
_PLANOS=WeakKeyDictionary()
_STATUS={'chamadas':0,'hits':0,'misses':0,'fallbacks':0,'max_tiles_retidos':0}


def _plano_para(scene):
    state=_PLANOS.get(scene)
    if state is None:
        state={'travel':None,'layers':{},'ultimo_frame':None}
        _PLANOS[scene]=state
    return state


def estatisticas():
    return dict(_STATUS,instalado=_INSTALADO,mundos_com_plano=len(_PLANOS))


def instalar():
    global _INSTALADO,_ORIGINAL
    if _INSTALADO:
        return
    if os.environ.get('PIXELRUSH_QA_CIDADE_TILE_PLAN','1')!='1':
        return
    from pixelrush_city2_v3125 import CityPilotScene
    _ORIGINAL=CityPilotScene._layer_tiles

    @wraps(_ORIGINAL)
    def plano(self,travel,layer):
        _STATUS['chamadas']+=1
        # Nao interferir nos casos nao convencionais (ex. plano sintetico).
        if not isinstance(travel,(int,float)) or not any(layer is obj for obj in self.layers):
            _STATUS['fallbacks']+=1
            return _ORIGINAL(travel,layer)
        try:
            estado=_plano_para(self)
            if estado['travel']!=travel:
                # Invalida imediatamente na troca de posicao. Nao faz cache
                # de 32 fases, evitando texturas/surfaces retidas por historico.
                estado['travel']=travel
                estado['layers'].clear()
            layer_id=id(layer)
            entry=estado['layers'].get(layer_id)
            if entry is not None and entry[0] is layer:
                _STATUS['hits']+=1
                return entry[1]
            tile_list=tuple(_ORIGINAL(travel,layer))
            estado['layers'][layer_id]=(layer,tile_list)
            _STATUS['misses']+=1
            _STATUS['max_tiles_retidos']=max(_STATUS['max_tiles_retidos'],
                                              sum(len(k[1]) for k in estado['layers'].values()))
            return tile_list
        except (AttributeError,TypeError,ValueError,MemoryError):
            _STATUS['fallbacks']+=1
            return _ORIGINAL(travel,layer)

    CityPilotScene._layer_tiles=plano
    _INSTALADO=True


def restaurar_para_teste():
    global _INSTALADO
    if _INSTALADO:
        from pixelrush_city2_v3125 import CityPilotScene
        CityPilotScene._layer_tiles=staticmethod(_ORIGINAL)
    _PLANOS.clear()
    _STATUS.update(chamadas=0,hits=0,misses=0,fallbacks=0,max_tiles_retidos=0)
    _INSTALADO=False
