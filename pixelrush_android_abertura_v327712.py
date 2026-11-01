"""Abertura visual exclusiva do APK Android da PIXEL RUSH v3.277.12.

O Android exibe primeiro o presplash nativo (estatico). Quando o SDL/Pygame
estiver disponivel, esta abertura alterna quadros coloridos do titulo e
entrega a janela ao jogo original. Nao modifica corrida, fisica ou saves.
"""

import os
from pathlib import Path
import sys
import traceback


QUADROS = (
    'splash_01_vermelho.png',
    'splash_02_laranja.png',
    'splash_03_amarelo.png',
    'splash_04_ciano.png',
)


def _executando_android():
    return (sys.platform == 'android' or
            any(k in os.environ for k in ('ANDROID_ARGUMENT', 'ANDROID_PRIVATE')))


def mostrar_abertura():
    """Exibe 1,8 s de animacao no Android; em desktop nao faz nada."""
    if not _executando_android():
        return

    try:
        import pygame
        pygame.display.init()
        tela = pygame.display.get_surface()
        if tela is None:
            tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        tamanho = tela.get_size()
        recursos = Path(__file__).resolve().parent / 'assets_android'
        imagens = [
            pygame.transform.smoothscale(
                pygame.image.load(str(recursos / nome)).convert(), tamanho
            ) for nome in QUADROS
        ]
        relogio = pygame.time.Clock()
        inicio = pygame.time.get_ticks()
        duracao_ms = 1800
        quadro_ms = 375
        while pygame.time.get_ticks() - inicio < duracao_ms:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    raise SystemExit(0)
            decorrido = pygame.time.get_ticks() - inicio
            indice = (decorrido // quadro_ms) % len(imagens)
            tela.blit(imagens[indice], (0, 0))
            pygame.display.flip()
            relogio.tick(30)
        # Nao chamar pygame.quit(): a atividade SDL permanece viva para o jogo.
    except Exception:
        # Splash opcional: erro visual nao deve impedir o carregamento do jogo.
        print('PIXEL_RUSH_ANDROID_SPLASH_ERROR:', file=sys.stderr)
        traceback.print_exc()
