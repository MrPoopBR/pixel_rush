# -*- coding: utf-8 -*-
"""QA 3.277.44: censo offline de memoria CPU/SDL, sem alterar o jogo.

Conta pygame.Surface por identidade (sem duplicar subsurfaces compartilhadas
na contagem LOGICA) e buffers NumPy. Inclui RSS do processo, que e a medicao
de memoria residente mais util; os totais de surfaces sao estimativas, nao
VRAM nem memoria efetivamente retornada ao sistema.
"""
from collections import deque
from collections.abc import Mapping


def rss_mib():
    try:
        with open('/proc/self/status',encoding='ascii') as f:
            for line in f:
                if line.startswith('VmRSS:'):
                    return round(int(line.split()[1])/1024.,3)
    except (OSError,ValueError,IndexError):
        pass
    return None


def inventario_recursos(raiz, max_objetos=90000):
    import pygame
    try:
        import numpy as np
    except ImportError:
        np=None
    fila=deque([raiz])
    vistos=set()
    surfaces=0
    pixels_bytes=0
    numpy_arrays=0
    numpy_bytes=0
    limitou=False
    while fila:
        item=fila.popleft()
        chave=id(item)
        if chave in vistos:
            continue
        vistos.add(chave)
        if len(vistos)>max_objetos:
            limitou=True
            break
        if isinstance(item,pygame.Surface):
            surfaces+=1
            pixels_bytes+=item.get_pitch()*item.get_height()
        elif np is not None and isinstance(item,np.ndarray):
            numpy_arrays+=1
            numpy_bytes+=item.nbytes
        elif isinstance(item,Mapping):
            fila.extend(item.values())
        elif isinstance(item,(list,tuple,deque,set,frozenset)):
            fila.extend(item)
        elif hasattr(item,'__dict__') and not isinstance(item,type):
            fila.extend(vars(item).values())
    return {'objetos_visitados':len(vistos),'limite_excedido':limitou,
            'surfaces_unicas':surfaces,
            'bytes_logicos_surfaces':pixels_bytes,
            'mib_logicos_surfaces':round(pixels_bytes/1048576.,3),
            'numpy_arrays':numpy_arrays,'numpy_bytes':numpy_bytes,
            'rss_processo_mib':rss_mib()}


def resumo_caches_mundo(mundo):
    def n(v):
        return len(v) if v is not None else 0
    city=getattr(mundo,'city2',None)
    modular=getattr(mundo,'modular',{})
    return {
        'bioma_ativo':str(getattr(mundo,'biome','?')),
        'cidade_retida':city is not None,
        'cidade_scaled':n(getattr(city,'_scaled',None)) if city else 0,
        'cidade_night_veils':n(getattr(city,'_night_veils',None)) if city else 0,
        'cidade_flips':n(getattr(city,'_flips',None)) if city else 0,
        'world_canais_buffers':n(getattr(mundo,'_city_surfaces',None)),
        'world_props':n(getattr(mundo,'props_cache',None)),
        'world_modular_biomas':tuple(sorted(modular)),
        'modular_night_tiles':sum(n(getattr(s,'_night_tiles',None)) for s in modular.values()),
        'modular_maps':sum(n(getattr(s,'_maps',None)) for s in modular.values()),
    }
