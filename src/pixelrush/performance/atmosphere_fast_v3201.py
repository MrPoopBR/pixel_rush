"""Plano G v3.201.0 — conversao unica do filtro atmosferico para o formato destino.

O filtro de 24 bits da v3.199 e a operacao BLEND_RGB_ADD permanecem os mesmos.
A unica diferenca e realizar a conversao SDL de pixels antecipadamente, no
primeiro uso de cada estado e formato, em vez de repeti-la em cada frame.
Nao cria um passe grafico, nao altera cores, luz, alfa, geometria ou gameplay.
"""
from collections import OrderedDict

from pixelrush_atmosfera_v3199 import PERFIS, LIMITE, _estado, _gerar
import pygame

_CACHE_COMPATIVEL = OrderedDict()


def aplicar_otimizado(destino, bioma, noite, fase, clima):
    """Mesmo filtro e mesmo blend da v3.199, cacheado no formato do destino."""
    if bioma not in PERFIS:
        return
    estado = _estado(noite, fase, clima)
    chave = (bioma, *estado, destino.get_masks())
    filtro = _CACHE_COMPATIVEL.get(chave)
    if filtro is None:
        # Exatamente a geracao de pixel art/luz original, sem recalcular tintas.
        original = _gerar(bioma, *estado)
        filtro = original.convert(destino)
        _CACHE_COMPATIVEL[chave] = filtro
        if len(_CACHE_COMPATIVEL) > LIMITE:
            _CACHE_COMPATIVEL.popitem(last=False)
    else:
        _CACHE_COMPATIVEL.move_to_end(chave)
    destino.blit(filtro, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def estatisticas_otimizadas():
    return {
        'entradas': len(_CACHE_COMPATIVEL),
        'limite': LIMITE,
        'bytes_pixels': sum(s.get_pitch() * s.get_height()
                            for s in _CACHE_COMPATIVEL.values()),
        'formatos_bits': sorted(set(s.get_bitsize() for s in _CACHE_COMPATIVEL.values())),
    }
