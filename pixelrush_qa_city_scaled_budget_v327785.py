# -*- coding: utf-8 -*-
"""QA785: evita thrash de atlas da Cidade no quinto quadro.

Somente CityPilotScene QA: 14 -> 20 entradas no LRU existente.
Nao transforma pixels, fisica, sprites, estado ou mapas; no pior caso
6 superficies extra 900x500 RGBA = 10.80 MB decimais (10.30 MiB).
O trimmer existente libera caches de cenas inativas em pressao RSS.
"""
import os
from functools import wraps

_INSTALADO=False
_ORIGINAL=None
_STATUS={'cenas':0,'aumentos':0,'cache_original':14,'cache_qa':20,
         'extra_maximo_bytes':6*900*500*4,'enabled':False}

def diagnostico():
    return dict(_STATUS,instalado=_INSTALADO)

def instalar():
    global _INSTALADO,_ORIGINAL
    if _INSTALADO:
        return
    if os.environ.get('PIXELRUSH_QA_CITY_SCALED_BUDGET','1')!='1':
        _STATUS['enabled']=False
        return
    from pixelrush_city2_v3125 import CityPilotScene
    _ORIGINAL=CityPilotScene.__init__

    @wraps(_ORIGINAL)
    def init(self,*args,**kwargs):
        _ORIGINAL(self,*args,**kwargs)
        _STATUS['cenas']+=1
        # Se outra versao alterar a capacidade original, nao sobrescrever.
        if getattr(self,'_scaled_limit',None)==14:
            self._scaled_limit=20
            _STATUS['aumentos']+=1

    CityPilotScene.__init__=init
    _INSTALADO=True
    _STATUS['enabled']=True

def restaurar_para_teste():
    global _INSTALADO,_ORIGINAL
    if _INSTALADO:
        from pixelrush_city2_v3125 import CityPilotScene
        CityPilotScene.__init__=_ORIGINAL
    _INSTALADO=False
    _ORIGINAL=None
    _STATUS.update(cenas=0,aumentos=0,enabled=False)
