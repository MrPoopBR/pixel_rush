"""Fase B v3.271: acabamentos VISUAIS para biomas e legibilidade de lasers.

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
    """Plano de fundo de leitura suave, apenas no pass visual.

    A redução de contraste noturno é feita em cache e não modifica
    o clima, o fundo original, a física nem a ordem dos sprites.
    """
    if leve or bioma not in PALETAS:
        return False
    # Textura do efeito da versão anterior, mas com camada própria discreta.
    tex = _faixa_distante(bioma)
    noite = max(0.0, min(1.0, float(peso_noite)))
    # A noite diminui a conspicuidade em vez de aumentar brilho no céu.
    if noite:
        tex = _faixa_noturna(bioma, round(noite * 4) / 4)
    # Um desenho estável na faixa intermediária, atrás de chão e obstáculos.
    x = (-int(float(deslocamento) * 0.12)) % 900 - 900
    largura = superficie.get_width()
    for pos in range(x, largura, 900):
        superficie.blit(tex, (pos, 305))
    return True


@lru_cache(maxsize=28)
def _faixa_noturna(bioma, intensidade):
    original = _faixa_distante(bioma)
    result = original.copy()
    result.set_alpha(round(255 * (1 - 0.55 * intensidade)))
    return result


def desenhar_legibilidade_jetpack(superficie, gate, frame=0, leve=False):
    """Aviso em três faixas: X no perigo e sinal geométrico no seguro.

    Não depende apenas de cor nem altera a duração ou o gate.
    """
    if not getattr(gate, 'ligado', False) or int(getattr(gate, 'aviso', 0)) <= 0:
        return False
    faixa = max(0, min(2, int(gate.faixa)))
    x0, y0 = superficie.get_width() - 89, 262
    fundo = pygame.Surface((75, 68), pygame.SRCALPHA)
    pygame.draw.rect(fundo, (10, 28, 48, 216), (0, 0, 75, 68), border_radius=8)
    pygame.draw.rect(fundo, (180, 229, 246, 130), (0, 0, 75, 68), 1, border_radius=8)
    for nivel in (2, 1, 0):
        pos = 2 - nivel
        y = 9 + pos * 19
        perigo = nivel == faixa
        cor = (255, 125, 116) if perigo else (111, 219, 204)
        pygame.draw.rect(fundo, (*cor, 205), (10, y, 55, 11), border_radius=3)
        if perigo:
            # Duas diagonais, legíveis até em escala de cinza.
            pygame.draw.line(fundo, (29, 38, 52), (33, y + 2), (40, y + 9), 2)
            pygame.draw.line(fundo, (29, 38, 52), (40, y + 2), (33, y + 9), 2)
        else:
            # Ponto vazado + contorno contrastante indica alternativa livre.
            pygame.draw.circle(fundo, (22, 57, 64), (36, y + 5), 3, 1)
    superficie.blit(fundo, (x0, y0))
    return True


def desenhar_legibilidade_corredor(superficie, faixas, frame=0, leve=False):
    """Marcas das bordas do vão livre durante warning; sem tocar no laser."""
    desenhou = 0
    for faixa in faixas:
        if int(faixa.get('warning', 0)) <= 0:
            continue
        x = int(faixa['x']); y = int(faixa['gap_y']); h = max(0, int(faixa['gap_h']))
        if x < -40 or x > superficie.get_width() + 40 or not h:
            continue
        topo = y - h//2 + 3
        base = y + h//2 - 3
        if base <= topo:
            continue
        for yy in (topo, base):
            pygame.draw.line(superficie, (226, 248, 235), (x + 2, yy), (x + 30, yy), 2)
            pygame.draw.line(superficie, (42, 82, 97), (x + 2, yy + 3), (x + 30, yy + 3), 1)
        # Um pequeno losango no centro: não depende de vermelho/verde.
        meio = (topo + base) // 2
        pygame.draw.lines(superficie, (170, 244, 222), True,
                          [(x + 10, meio), (x + 16, meio - 5),
                           (x + 22, meio), (x + 16, meio + 5)], 2)
        desenhou += 1
    return desenhou
