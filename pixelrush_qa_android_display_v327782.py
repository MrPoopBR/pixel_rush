# -*- coding: utf-8 -*-
"""QA782: janela Android em resolucao fisica para preencher o Galaxy A54.

A superficie interna do jogo permanece 450x800. O loop do jogo ja converte
coordenadas de toque de dimensoes reais para as virtuais, e ja apresenta
com pygame.transform.scale para a janela final; este modulo so solicita
uma janela fullscreen REAL no lugar de uma janela logica 450x800.
Nunca altera fisica, camera, politica de render, saves ou demais plataformas.
"""
import pygame

_STATUS = {
    'solicitado': False,
    'modo': 'nao_avaliado',
    'janela_px': None,
    'logico_px': (450, 800),
    'fullscreen_fisico': False,
    'fallback': None,
}


def diagnostico():
    return dict(_STATUS)


def criar_tela(tamanho_logico=(450, 800)):
    """Janela real fullscreen, com fallback identico a v781.

    SDL/Android pode impor uma janela menor ou recusar 0x0. Nesses casos,
    nao tenta forcar DPI no sistema nem mexer nos dados do dispositivo.
    """
    largura, altura = map(int, tamanho_logico)
    if largura <= 0 or altura <= 0:
        raise ValueError('Tamanho logico invalido')
    _STATUS.update(solicitado=True, logico_px=(largura,altura),
                   fullscreen_fisico=False, fallback=None)
    try:
        tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        w, h = tela.get_size()
        if w >= largura and h >= altura and w > 0 and h > 0:
            _STATUS.update(modo='fullscreen_fisico',janela_px=(w,h),
                           fullscreen_fisico=True)
            return tela
        _STATUS['fallback'] = 'modo_fisico_menor_que_logico'
    except (pygame.error, ValueError, RuntimeError, OSError) as exc:
        _STATUS['fallback'] = type(exc).__name__
    # A rota antiga e mantida somente quando a nova nao funciona.
    tela = pygame.display.set_mode((largura,altura))
    _STATUS.update(modo='fallback_logico',janela_px=tela.get_size())
    return tela
