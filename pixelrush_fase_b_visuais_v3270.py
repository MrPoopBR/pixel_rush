"""Fase B v3.270: acabamentos VISUAIS para biomas e legibilidade de lasers.

Nao altera timer, RNG, grupos, hitboxes, trajetorias, save ou dificuldade.
Todos os indicadores leem apenas o estado existente dos objetos.
"""
from __future__ import annotations
from functools import lru_cache
import pygame

# Tons deliberadamente suaves para nao camuflar objetos e inimigos.
PALETAS = {
    'cidade': (95, 175, 216), 'neve': (187, 222, 247),
    'deserto': (241, 190, 129), 'floresta': (111, 190, 142),
    'vulcao': (236, 112, 88), 'cidade_futurista': (96, 215, 232),
    'ilhas_celestes': (179, 209, 250),
}

@lru_cache(maxsize=7)
def _faixa_distante(bioma):
    """Gera uma vez uma textura RGBA pequena, com dois planos de profundidade."""
    cor = PALETAS[bioma]
    tela = pygame.Surface((900, 166), pygame.SRCALPHA)
    # Plano distante: alturas baixas, translúcido, atrás dos perigos.
    for i in range(12):
        x = i * 86 - 20
        y = 84 + (i % 4) * 12
        pygame.draw.polygon(tela, (*cor, 21), ((x, 164), (x + 25, y), (x + 57, 164)))
    for i in range(10):
        x = i * 108 + 8
        y = 113 + (i % 3) * 10
        pygame.draw.line(tela, (*cor, 34), (x, y), (x + 40, y - 8), 2)
    return tela


def desenhar_profundidade_bioma(superficie, bioma, deslocamento, peso_noite=0.0, leve=False):
    """Camada decorativa que passa lentamente atrás de todos os sprites.

    Preserva o parallax preexistente; o efeito e omitido no modo grafico leve.
    """
    if leve or bioma not in PALETAS:
        return False
    tex = _faixa_distante(bioma)
    deslocamento = float(deslocamento)
    x = -int(deslocamento * 0.12) % 900 - 900
    y = 305
    # Largura virtual e 450; dois blits cobrem sempre o fundo.
    superficie.blit(tex, (x, y))
    superficie.blit(tex, (x + 900, y))
    return True


def desenhar_legibilidade_jetpack(superficie, gate, frame=0, leve=False):
    """Minimapa de tres faixas: vermelho indica a ocupada pelo laser.

    So aparece durante o aviso do gate que JA existe. Nao muda duracao.
    """
    if not getattr(gate, 'ligado', False) or int(getattr(gate, 'aviso', 0)) <= 0:
        return False
    faixa = max(0, min(2, int(gate.faixa)))
    # Nao cobrir painel antigo de alerta; barra de faixas no canto direito.
    x0, y0 = superficie.get_width() - 89, 262
    fundo = pygame.Surface((75, 68), pygame.SRCALPHA)
    pygame.draw.rect(fundo, (10, 28, 48, 204), (0, 0, 75, 68), border_radius=8)
    pygame.draw.rect(fundo, (133, 222, 237, 94), (0, 0, 75, 68), 1, border_radius=8)
    for nivel in (2, 1, 0):
        pos = 2 - nivel
        cor = (254, 119, 114) if nivel == faixa else (97, 220, 191)
        pygame.draw.rect(fundo, (*cor, 205), (10, 9 + pos * 19, 55, 11), border_radius=3)
        if nivel == faixa:
            pygame.draw.line(fundo, (255, 246, 198, 255), (29, 14 + pos * 19), (47, 14 + pos * 19), 2)
    superficie.blit(fundo, (x0, y0))
    return True


def desenhar_legibilidade_corredor(superficie, faixas, frame=0, leve=False):
    """Enfatiza a abertura segura APENAS durante o aviso existente do corredor."""
    desenhou = 0
    for faixa in faixas:
        if int(faixa.get('warning', 0)) <= 0:
            continue
        x = int(faixa['x']); y = int(faixa['gap_y']); h = max(0, int(faixa['gap_h']))
        if x < -40 or x > superficie.get_width() + 40 or not h:
            continue
        # Moldura do VAO e apenas linha, sem alterar hitbox ou feixe.
        topo = y - h//2 + 3
        base = y + h//2 - 3
        pygame.draw.line(superficie, (130, 244, 220), (x + 2, topo), (x + 30, topo), 2)
        pygame.draw.line(superficie, (130, 244, 220), (x + 2, base), (x + 30, base), 2)
        desenhou += 1
    return desenhou
