"""Pixel Rush v3.234.0 — acabamento da sombra de contato EXISTENTE.

Substitui exclusivamente o desenho da penumbra do jogador em qualidade normal.
Reutiliza o cache LRU da v3.189, a paleta das v3.171/v3.177 e o MESMO
blit do jogo; sem shaders, pixel loops por quadro, novos sprites, novos estados
ou geometria de colisão. Modo leve delega integralmente à v3.189.
"""
import pygame
import pixelrush_cinema_v3189 as _cinema
from pixelrush_luz_materiais_v3177 import PERFIS
from pixelrush_polimento_v3171 import CORES


def _penumbra_premium(bioma, largura, periodo, altitude):
    # Usa o LRU de sombra original; o prefixo evita misturar entradas antigas.
    chave = ('v3234', bioma, largura, periodo, altitude)
    cache = _cinema._CACHE_SOMBRA
    imagem = cache.get(chave)
    if imagem is not None:
        cache.move_to_end(chave)
        return imagem
    w, h = largura + 12, 12
    imagem = pygame.Surface((w, h), pygame.SRCALPHA)
    # A paleta já aprovada evita cinza/preto universal nos pisos coloridos.
    cor_fundo = CORES.get(bioma, CORES['cidade'])
    perfil = PERFIS.get(bioma)
    cor_material = perfil[1] if perfil is not None else (30, 36, 50)
    rgb = tuple(max(10, min(125, int(cor_fundo[i] * .14 + cor_material[i] * .36)))
                for i in range(3))
    densidade = max(.34, 1.0 - altitude * .11) * (1.0 - periodo * .055)
    # Quatro anéis concentrados: borda suave e maior contato no eixo dos pés.
    # Todas as primitivas são desenhadas SOMENTE quando o cache falha.
    for margem, yy, espessura, alpha in ((0,0,11,13),(2,1,9,25),
                                          (5,2,7,46),(8,4,4,85)):
        pygame.draw.ellipse(imagem, (*rgb, int(alpha * densidade)),
                            (margem, yy, max(1, w-2*margem), espessura))
    cache[chave] = imagem
    if len(cache) > _cinema._MAX_SOMBRA:
        cache.popitem(last=False)
    return imagem


def sombra_contato(surface, jogador, bioma, leve=False, noite=0.0):
    """Ajuste localizado do contato sem tocar em rect/hitbox/estado do jogador.

    O caminho de modo leve retorna exatamente os mesmos pixels da v3.233.0.
    """
    if leve:
        return _cinema.sombra_contato(surface, jogador, bioma, True, noite)
    if jogador is None or getattr(jogador, 'jetpack_fase', None) is not None:
        return
    chao = int(jogador.chao_y)
    altura = max(0, chao - int(jogador.rect.bottom))
    largura = max(12, 36 - min(20, altura // 8))
    periodo = max(0, min(4, int(float(noite) * 4.0 + .5)))
    faixa_altura = min(6, altura // 16)
    sombra = _penumbra_premium(bioma, largura, periodo, faixa_altura)
    surface.blit(sombra, (jogador.rect.centerx - sombra.get_width()//2, chao - 7))
    # Preserva o filete de contato existente na mesma posição/condição.
    if altura < 42:
        cor = CORES.get(bioma, CORES['cidade'])
        pygame.draw.line(surface, cor, (jogador.rect.centerx-8, chao-2),
                         (jogador.rect.centerx+8, chao-2), 1)


def estatisticas_cache():
    entradas = [v for k,v in _cinema._CACHE_SOMBRA.items()
                if isinstance(k,tuple) and k and k[0] == 'v3234']
    return {'entradas_premium':len(entradas),
            'limite_compartilhado':_cinema._MAX_SOMBRA,
            'bytes_pixels_premium':sum(s.get_pitch()*s.get_height() for s in entradas)}
