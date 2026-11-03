# -*- coding: utf-8 -*-
"""QA768: internacao de atlas tecnicos IMUTAVEIS entre cenas Cidade.

Somente atlas finalizados apos CityPilotScene.__init__ e antes do primeiro
render. Compara formato, alpha, pixel bytes completos (inclusive RGB oculto).
A tabela global e weak: nao impede liberar cenas antigas. Nenhum Surface
novo e criado ou textura animada alterada; desative por env para rollback.
"""
import hashlib
import os
from weakref import WeakValueDictionary

import pygame

_COMPARTILHADOS=WeakValueDictionary()
# A imagem do chunk tambem e estatica APOS _prebake_static_props.
# Nunca incluir sprites animados: continuam exclusivos de cada cena.
_KINDS=('image','geometry','normal','material','flow','fxmask')
_STATS={'cenas':0,'visitados':0,'reusados':0,'bytes_evitaram':0,
        'sem_paridade':0,'fallbacks':0}

def diagnostico():
    return dict(_STATS,tabela=len(_COMPARTILHADOS),
                habilitado=os.environ.get('PIXELRUSH_QA_CITY_GLOBAL_INTERN','1')=='1')

def compartilhar(scene):
    if os.environ.get('PIXELRUSH_QA_CITY_GLOBAL_INTERN','1')!='1':
        return False
    _STATS['cenas']+=1
    for layer in scene.layers:
        for variant in layer.variants:
            for kind in _KINDS:
                tex=getattr(variant,kind,None)
                if not isinstance(tex,pygame.Surface):
                    continue
                if (tex.get_bitsize()!=32 or
                        tex.get_colorkey() is not None or
                        not (tex.get_flags() & pygame.SRCALPHA) or
                        tex.get_alpha() not in (None,255)):
                    continue
                _STATS['visitados']+=1
                try:
                    view=memoryview(tex.get_view('0'))
                    try:
                        digest=hashlib.blake2b(view,digest_size=16).digest()
                    finally:
                        view.release()
                    chave=(kind,tex.get_size(),tex.get_pitch(),
                           tex.get_flags(),tex.get_masks(),tex.get_alpha(),
                           digest)
                    original=_COMPARTILHADOS.get(chave)
                    if original is tex:
                        continue
                    if original is not None:
                        a=memoryview(original.get_view('0'))
                        b=memoryview(tex.get_view('0'))
                        try:
                            igual=(a==b)
                        finally:
                            a.release();b.release()
                        if igual:
                            setattr(variant,kind,original)
                            _STATS['reusados']+=1
                            _STATS['bytes_evitaram']+=tex.get_pitch()*tex.get_height()
                            continue
                        _STATS['sem_paridade']+=1
                    else:
                        _COMPARTILHADOS[chave]=tex
                except (pygame.error,MemoryError,BufferError,ValueError,
                        TypeError,AttributeError):
                    _STATS['fallbacks']+=1
                    # A variante original permanece proprietaria: sem alias.
                    continue
    return True

def restaurar_para_teste():
    _COMPARTILHADOS.clear()
    for chave in _STATS:
        _STATS[chave]=0
