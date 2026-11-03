# -*- coding: utf-8 -*-
"""QA 3.277.42: integracao real do scroll persistente com autotune pixel-exato.

Somente o strip estatico do caminho classico (camadas dinamicas nao cacheadas).
Se a copia final nao compensar no hardware, usa o blit original em cada frame.
O benchmark roda UMA vez, em superficies de teste, sem tocar na imagem visivel.
"""
import os
import statistics
import time
from functools import wraps

import pygame
from pixelrush_qa_rolling_v327740 import FaixaPersistenteQA

_INSTALLED=False
_ORIGINAL=None
_REPORT={'avaliado':False,'ativo':False,'resultado':'nao_avaliado',
         'ganho_p50':None,'testes_pixel_exatos':0,'tamanho_cache_bytes':0}
_MANAGER={}


def status():
    return dict(_REPORT)


def _draw_reference(target,texture,offset):
    width=texture.get_width()
    x=-offset%width
    x=-x
    operations=[]
    while x<450:
        operations.append((texture,(x,230)))
        x+=width
    if operations:
        target.blits(operations,doreturn=False)


def _bench(texture,target):
    # Do not turn on for source formats/alpha that are not exactly copied.
    if (not isinstance(texture,pygame.Surface) or not texture.get_width() or
        texture.get_height()!=500 or target.get_size()!=(450,800) or
        texture.get_colorkey() is not None):
        return False,None,'formato_nao_suportado'
    rolling=FaixaPersistenteQA(450)
    baseline=target.copy()
    candidate=target.copy()
    positions=[i*7%texture.get_width() for i in range(16)]
    checks=0
    for offset in positions:
        baseline.blit(target,(0,0))
        candidate.blit(target,(0,0))
        _draw_reference(baseline,texture,offset)
        candidate.blit(rolling.gerar(texture,offset),(0,230))
        if pygame.image.tobytes(baseline,'RGBA') != pygame.image.tobytes(candidate,'RGBA'):
            return False,None,'pixels_diferentes'
        checks+=1
    times_direct=[]
    times_cache=[]
    for offset in positions*3:
        baseline.blit(target,(0,0))
        t=time.perf_counter_ns()
        _draw_reference(baseline,texture,offset)
        times_direct.append(time.perf_counter_ns()-t)
        candidate.blit(target,(0,0))
        t=time.perf_counter_ns()
        candidate.blit(rolling.gerar(texture,offset),(0,230))
        times_cache.append(time.perf_counter_ns()-t)
    a=statistics.median(times_direct)
    b=statistics.median(times_cache)
    ganho=a/max(b,1)
    return bool(ganho>=1.20),{'amostras':len(times_direct),'ratio':round(ganho,3),
                               'direto_ms':round(a/1e6,4),
                               'persistente_ms':round(b/1e6,4),
                               'pixels_testados':checks},'aprovado' if ganho>=1.20 else 'mais_lento'


def instalar():
    global _INSTALLED,_ORIGINAL
    if _INSTALLED:
        return
    from pixelrush_world_v3130 import LivingWorld
    _ORIGINAL=LivingWorld._blit_strip

    @wraps(_ORIGINAL)
    def _blit_scroll_qa(self,target,strip):
        if strip is None or os.environ.get('PIXELRUSH_QA_SCROLL_AUTO','1')!='1':
            return _ORIGINAL(self,target,strip)
        entry=_MANAGER.get(id(self))
        # World instance is retained by its owner; store it to avoid false
        # matches from identity reuse across world switches.
        if entry is None or entry[0] is not self or entry[1] is not strip:
            _MANAGER[id(self)]=(self,strip,None)
            entry=_MANAGER[id(self)]
        approved=entry[2]
        if approved is None:
            allow,results,reason=_bench(strip,target)
            _REPORT['avaliado']=True
            _REPORT['ativo']=bool(allow)
            _REPORT['resultado']=reason
            _REPORT['ganho_p50']=results
            _REPORT['testes_pixel_exatos']=results['pixels_testados'] if results else 0
            _REPORT['tamanho_cache_bytes']=450*500*4 if allow else 0
            if not allow:
                _MANAGER[id(self)]=(self,strip,False)
                return _ORIGINAL(self,target,strip)
            rolling=FaixaPersistenteQA(450)
            _MANAGER[id(self)]=(self,strip,rolling)
            approved=rolling
        if approved is False:
            return _ORIGINAL(self,target,strip)
        target.blit(approved.gerar(strip,self._scroll()),(0,230))
    LivingWorld._blit_strip=_blit_scroll_qa
    _INSTALLED=True


def restaurar_para_teste():
    global _INSTALLED
    if not _INSTALLED:
        return
    from pixelrush_world_v3130 import LivingWorld
    LivingWorld._blit_strip=_ORIGINAL
    _MANAGER.clear()
    _REPORT.update(avaliado=False,ativo=False,resultado='nao_avaliado')
    _INSTALLED=False
