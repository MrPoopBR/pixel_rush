# -*- coding: utf-8 -*-
"""QA773: reciclador pixel-exato do replay 225x400 apos buffer de 72 quadros."""
import os
from functools import wraps
import pygame

_INSTALLED=False
_ORIGINAL=None
_STATUS={'reusadas':0,'originais':0,'fallbacks':0,
         'bytes_evitados':0}

def diagnostico():
    return dict(_STATUS,instalado=_INSTALLED)

def _compatibilidade(src,dst,tamanho):
    return (dst.get_size()==tamanho
        and src.get_bitsize()==dst.get_bitsize()
        and src.get_masks()==dst.get_masks()
        and bool(src.get_flags() & pygame.SRCALPHA)==bool(dst.get_flags() & pygame.SRCALPHA)
        and src.get_colorkey()==dst.get_colorkey()
        and src.get_alpha()==dst.get_alpha()
        and not (src.get_flags() & (pygame.RLEACCEL|getattr(pygame,'RLEACCELOK',0))))

def instalar():
    global _INSTALLED,_ORIGINAL
    if _INSTALLED or os.environ.get('PIXELRUSH_QA_REPLAY_REUSE','1')!='1':
        return
    from pixelrush_extras_v3174 import ReplayCinematografico
    _ORIGINAL=ReplayCinematografico.capturar
    @wraps(_ORIGINAL)
    def capturar(self,superficie,tick):
        if (self.congelado or tick-self.ultima_amostra<self.INTERVALO_TICKS
            or len(self.buffer)<self.MAX_AMOSTRAS):
            _STATUS['originais']+=1
            return _ORIGINAL(self,superficie,tick)
        antigo=self.buffer[0]
        if not _compatibilidade(superficie,antigo,self.TAMANHO):
            _STATUS['originais']+=1
            return _ORIGINAL(self,superficie,tick)
        antigo=self.buffer.popleft()
        try:
            pygame.transform.scale(superficie,self.TAMANHO,antigo)
        except (pygame.error,ValueError,MemoryError,TypeError):
            self.buffer.appendleft(antigo)
            _STATUS['fallbacks']+=1
            _STATUS['originais']+=1
            return _ORIGINAL(self,superficie,tick)
        self.buffer.append(antigo)
        self.ultima_amostra=int(tick)
        _STATUS['reusadas']+=1
        _STATUS['bytes_evitados']+=antigo.get_pitch()*antigo.get_height()
    ReplayCinematografico.capturar=capturar
    _INSTALLED=True

def restaurar_para_teste():
    global _INSTALLED,_ORIGINAL
    if _INSTALLED:
        from pixelrush_extras_v3174 import ReplayCinematografico
        ReplayCinematografico.capturar=_ORIGINAL
    _INSTALLED=False
    _ORIGINAL=None
    _STATUS.update(reusadas=0,originais=0,fallbacks=0,bytes_evitados=0)
