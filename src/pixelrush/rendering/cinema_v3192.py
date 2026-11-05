"""Plano F v3.192.0 — otimização rigorosamente equivalente da vinheta.

A v3.189 desenhava a vinheta com um blit RGBA de 450x460, mas seus
pixels efetivos estão só em duas tiras laterais e uma linha de base.
Esta versão mantém exatamente o RGB/alfa, posição, quantização noturna e
limite de cache. O modo leve permanece a rotina original, sem custo extra.
Nenhum estado de simulação, retângulo ou propriedade do jogador é tocado.
"""
from collections import OrderedDict
import pygame
from pixelrush_polimento_v3171 import CORES
from pixelrush_cinema_v3189 import (
    sombra_contato, limpar_caches as _limpar_caches_v3189,
    profundidade_cinematografica as _profundidade_v3189,
)

# 12 itens, como v3.189; cada item usa (26*406*2 + 398)*4 bytes
# em lugar de 450*460*4 bytes. 83.2 KiB contra 808.6 KiB por chave.
_CACHE_FAIXAS = OrderedDict()
_MAX_FAIXAS = 12


def _faixas(bioma, periodo):
    chave = (bioma, periodo)
    cached = _CACHE_FAIXAS.get(chave)
    if cached is not None:
        _CACHE_FAIXAS.move_to_end(chave)
        return cached
    base = CORES.get(bioma, CORES['cidade'])
    esquerda = pygame.Surface((26, 406), pygame.SRCALPHA)
    direita = pygame.Surface((26, 406), pygame.SRCALPHA)
    rodape = pygame.Surface((398, 1), pygame.SRCALPHA)
    for faixa in range(0, 26, 2):
        opacidade = max(0, 5 + periodo - faixa // 5)
        if opacidade:
            # Equivalência da linha v3.189 após transladar para y=25.
            pygame.draw.line(esquerda, (*base, opacidade),
                             (faixa, 0), (faixa, 405), 2)
            pygame.draw.line(direita, (*base, opacidade),
                             (449 - faixa - 424, 0),
                             (449 - faixa - 424, 405), 2)
    pygame.draw.line(rodape, (*base, 8 + periodo), (0, 0), (397, 0), 1)
    ret = (esquerda, direita, rodape)
    _CACHE_FAIXAS[chave] = ret
    if len(_CACHE_FAIXAS) > _MAX_FAIXAS:
        _CACHE_FAIXAS.popitem(last=False)
    return ret


def profundidade_cinematografica(surface, bioma, noite=False, leve=False):
    """Mesmo resultado visual da v3.189 com bem menos pixels em blit."""
    if leve:
        return _profundidade_v3189(surface, bioma, noite, True)
    periodo = max(0, min(4, int(float(noite) * 4.0 + .5)))
    esquerda, direita, rodape = _faixas(bioma, periodo)
    surface.blit(esquerda, (0, 169))
    surface.blit(direita, (424, 169))
    surface.blit(rodape, (26, 579))


def limpar_caches():
    _CACHE_FAIXAS.clear()
    _limpar_caches_v3189()
