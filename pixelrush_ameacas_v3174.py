"""v3.174.0: direção de iluminação compartilhada das ameaças existentes.

Preserva exatamente a geometria, o canal alfa e a física originais.
"""
from pixelrush_ameacas_v3171 import *
from pixelrush_ameacas_v3171 import imagem_ameaca as _imagem_anterior
from pixelrush_ameacas_v3171 import AmeacaBioma as _AmeacaAnterior
from pixelrush_extras_v3174 import HarmonizadorFrames
import pixelrush_ameacas_v3127 as _motor

_harmonia = HarmonizadorFrames(limite=96)


def imagem_ameaca(codigo, fase=0):
    original = _imagem_anterior(codigo, fase)
    return _harmonia.processar(original, 'ameaca')


_motor.imagem_ameaca = imagem_ameaca


class AmeacaBioma(_AmeacaAnterior):
    pass
