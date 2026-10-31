# -*- coding: utf-8 -*-
"""Pixel Rush v3.241.0 — animação pré-renderizada dos sete perseguidores.

Exclusivamente visual. Herda estados, atualização, RNG, tempos, posição,
frequência e ausência de colisão/captura da v3.239.0. Reusa o único blit
original da classe herdada: a seleção do quadro depende dos ticks FIXOS
já existentes, sem relógios, alocações, filtros nem RNG por frame.
"""
from pathlib import Path
import pygame
from pixelrush_perseguidores_v3240 import DiretorPerseguidores as _Diretor240, PERFIS

_PASTA = Path(__file__).resolve().parent / 'assets' / 'perseguidores_v3241'
_QUADROS = 8
_CADENCIA = 5
_LARGURA = 42
_ALTURA = 50


class DiretorPerseguidores(_Diretor240):
    def _icone(self, bioma):
        if bioma not in PERFIS:
            raise ValueError('Bioma desconhecido: %r' % (bioma,))
        if not hasattr(self, '_quadros_perseguidor'):
            self._quadros_perseguidor = {}
            self._atlases_perseguidor = {}
        if bioma not in self._quadros_perseguidor:
            atlas = pygame.image.load(str(_PASTA / (bioma + '.png'))).convert_alpha()
            if atlas.get_size() != (_LARGURA * _QUADROS, _ALTURA):
                raise ValueError('Dimensões incompatíveis no atlas de %s' % bioma)
            frames = tuple(atlas.subsurface(pygame.Rect(i * _LARGURA, 0,
                                                      _LARGURA, _ALTURA))
                           for i in range(_QUADROS))
            self._atlases_perseguidor[bioma] = atlas
            self._quadros_perseguidor[bioma] = frames
            self._imagens[bioma] = frames[0]
        frames = self._quadros_perseguidor[bioma]
        if self.fase != 'aproximacao' and self.fase != 'recuo':
            return frames[0]
        return frames[(self.ticks // _CADENCIA) % _QUADROS]
