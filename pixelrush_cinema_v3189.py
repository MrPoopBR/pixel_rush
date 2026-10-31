"""Pixel Rush v3.189.0 — acabamento cinematografico do renderizador existente.

Substitui, SEM sobrepor, as rotinas de profundidade e sombra da v3.171.
- Qualidade leve delega exatamente para o sistema anterior;
- nenhuma nova passagem pela tela, sprite, fisica, hitbox ou temporizador;
- gradiente da vinheta e penumbra da sombra pre-renderizados em caches limitados;
- luz noturna quantizada em 5 faixas, sem transicao abrupta em 40% da noite.
"""
from collections import OrderedDict
import pygame
from pixelrush_polimento_v3171 import (
    CORES, sombra_contato as _sombra_antiga,
    profundidade_cinematografica as _profundidade_antiga,
)

_CACHE_PROFUNDIDADE = OrderedDict()
_CACHE_SOMBRA = OrderedDict()
_MAX_PROFUNDIDADE = 12    # 12 x 450 x 460 x 4 ~ 9,9 MB limite conservador
_MAX_SOMBRA = 96         # <= 96 x 44 x 10 x 4, cache pequeno


def _cor_sombra(bioma):
    base = CORES.get(bioma, CORES['cidade'])
    # Cor do material preexistente escurecida, sem cor artificial nova.
    return tuple(max(10, int(v * .34)) for v in base)


def _vinheta(bioma, periodo):
    chave = (bioma, periodo)
    imagem = _CACHE_PROFUNDIDADE.get(chave)
    if imagem is not None:
        _CACHE_PROFUNDIDADE.move_to_end(chave)
        return imagem
    base = CORES.get(bioma, CORES['cidade'])
    imagem = pygame.Surface((450, 460), pygame.SRCALPHA)
    imagem.fill((0, 0, 0, 0))
    # Mesmo limite espacial e posicao do efeito original. Mais progressivo,
    # sem afetar jogador/perigos/HUD, que sao desenhados posteriormente.
    for faixa in range(0, 26, 2):
        opacidade = max(0, 5 + periodo - faixa // 5)
        if opacidade:
            pygame.draw.line(imagem, (*base, opacidade), (faixa, 25), (faixa, 430), 2)
            pygame.draw.line(imagem, (*base, opacidade), (449-faixa, 25), (449-faixa, 430), 2)
    pygame.draw.line(imagem, (*base, 8 + periodo), (26, 435), (423, 435), 1)
    _CACHE_PROFUNDIDADE[chave] = imagem
    if len(_CACHE_PROFUNDIDADE) > _MAX_PROFUNDIDADE:
        _CACHE_PROFUNDIDADE.popitem(last=False)
    return imagem


def profundidade_cinematografica(surface, bioma, noite=False, leve=False):
    """Refina a vinheta EXISTENTE com periodo quantizado em vez de booleano.

    Aceita booleano por compatibilidade e peso de noite float 0..1.
    """
    if leve:
        return _profundidade_antiga(surface, bioma, bool(noite), True)
    periodo = max(0, min(4, int(float(noite) * 4.0 + .5)))
    surface.blit(_vinheta(bioma, periodo), (0, 144))


def _penumbra(bioma, largura, periodo, altitude):
    chave = (bioma, largura, periodo, altitude)
    imagem = _CACHE_SOMBRA.get(chave)
    if imagem is not None:
        _CACHE_SOMBRA.move_to_end(chave)
        return imagem
    # Nao cria sombras projetadas novas: so acabamento da mancha ja existente.
    w, h = largura + 12, 10
    imagem = pygame.Surface((w, h), pygame.SRCALPHA)
    cor = _cor_sombra(bioma)
    # Queda de intensidade conforme altura e noite; sombra nunca gera colisao.
    força = max(0.30, 1.0 - altitude * .13) * (1.0 - periodo * .055)
    for margem, alfa in ((0, 19), (3, 35), (6, 65)):
        pygame.draw.ellipse(imagem, (*cor, int(alfa * força)),
                            (margem, 1 + margem // 2,
                             max(1, w - margem * 2), max(1, h - margem)))
    _CACHE_SOMBRA[chave] = imagem
    if len(_CACHE_SOMBRA) > _MAX_SOMBRA:
        _CACHE_SOMBRA.popitem(last=False)
    return imagem


def sombra_contato(surface, jogador, bioma, leve=False, noite=0.0):
    """Troca apenas a forma de desenho da sombra v3.171, nas MESMAS coordenadas.

    Jetpack e modo leve seguem a rotina original, sem qualquer diferenca.
    """
    if leve:
        return _sombra_antiga(surface, jogador, bioma, True)
    if jogador is None or getattr(jogador, 'jetpack_fase', None) is not None:
        return
    chao = int(jogador.chao_y)
    altura = max(0, chao - int(jogador.rect.bottom))
    largura = max(12, 36 - min(20, altura // 8))
    periodo = max(0, min(4, int(float(noite) * 4.0 + .5)))
    faixa_altura = min(6, altura // 16)
    sombra = _penumbra(bioma, largura, periodo, faixa_altura)
    surface.blit(sombra, (jogador.rect.centerx - sombra.get_width() // 2, chao - 6))
    if altura < 42:
        cor = CORES.get(bioma, CORES['cidade'])
        pygame.draw.line(surface, cor, (jogador.rect.centerx-8, chao-2),
                         (jogador.rect.centerx+8, chao-2), 1)


def limpar_caches():
    _CACHE_PROFUNDIDADE.clear()
    _CACHE_SOMBRA.clear()
