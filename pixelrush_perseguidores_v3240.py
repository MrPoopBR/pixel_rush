# -*- coding: utf-8 -*-
"""Pixel Rush v3.240.0: arte estática premium dos sete perseguidores.

Somente substitui os ícones provisórios por PNG 42x50 pré-renderizados.
Herda integralmente o diretor v3.239.0: estados, tempos, RNG, spawn,
avisos, posição em tela, cancelamento e ausência de dano/escape.
Sem filtros, recoloração, resize nem geração de formas por quadro.
"""
from pathlib import Path
import pygame
from pixelrush_perseguidores_v3239 import DiretorPerseguidores as _Diretor239, PERFIS

_PASTA_ARTES = Path(__file__).resolve().parent / "assets" / "perseguidores_v3240"


class DiretorPerseguidores(_Diretor239):
    def _icone(self, bioma):
        if bioma in self._imagens:
            return self._imagens[bioma]
        if bioma not in PERFIS:
            raise ValueError("Bioma de perseguidor desconhecido: %r" % (bioma,))
        origem = _PASTA_ARTES / (bioma + ".png")
        imagem = pygame.image.load(str(origem)).convert_alpha()
        if imagem.get_size() != (42, 50):
            raise ValueError("Atlas de perseguidor incompatível: %s" % origem)
        self._imagens[bioma] = imagem
        return imagem
