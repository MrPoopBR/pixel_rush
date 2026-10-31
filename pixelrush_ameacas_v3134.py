"""v3.134: conecta os 15 novos sprites da v3.133 ao ciclo REAL dos 28 perigos.

A classe base v3127 chama imagem_ameaca pelo espaço global DO módulo de
origem. Apenas importar uma função homônima v3133 não altera esse binding.
Aqui conectamos uma vez esse gancho visual ao carregamento. Não muda sprite
rect, _hitboxes_precisas_v342, spawn, tipo, posição ou a física do perigo.
"""
import os
import pygame
import pixelrush_ameacas_v3127 as motor
from pixelrush_ameacas_v3133 import (AMEACAS, POR_BIOMA, escorpiao_frame,
                                        _paint, _outline, REFINADOS)
from pixelrush_ameacas_v3129 import (AmeacaBioma as Anterior,
                                        imagem_ameaca as imagem_legada)
from pixelrush_ameacas_v3127 import risco_colisao_ativo

_CACHE = {}


def imagem_ameaca(codigo, fase=0):
    if codigo not in REFINADOS or os.environ.get('PIXELRUSH_ARTE_CLASSICA') == '1':
        return imagem_legada(codigo, fase)
    chave = (codigo, int(fase) % 3)
    if chave not in _CACHE:
        w, h = AMEACAS[codigo][2:4]
        # Vizinho mais próximo preserva o pixel art (sem embaçar contornos).
        quadro = pygame.transform.scale(_paint(*chave), (w, h)).convert_alpha()
        _CACHE[chave] = quadro
    return _CACHE[chave]


motor.imagem_ameaca = imagem_ameaca


class AmeacaBioma(Anterior):
    pass
