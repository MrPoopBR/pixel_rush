"""Pixel Rush v3.187.0 — acabamento de 13 obstáculos e avisos existentes.

Somente RGB interno dos sprites estáticos, processado sob demanda e cacheado.
Os ícones triangulares de aviso existentes recebem cor temática, mantendo posição,
frequência, antecipação e número máximo inalterados. Nenhuma regra de jogo muda.
"""
import pygame
import numpy as np
from pixelrush_ameacas_v3186 import (AMEACAS, POR_BIOMA, escorpiao_frame,
                                   AmeacaBioma as _AmeacaAnterior)
from pixelrush_ameacas_v3174 import imagem_ameaca as _imagem_anterior

ESTATICOS = frozenset(c for c, d in AMEACAS.items()
                      if d[4] in ('parado', 'parado_alto'))
# Suaves contrastes em materiais do obstáculo, sem halos ou pixels novos.
MATERIAL = {
    'C3': ((14, 9, -5), 17, 3),   # faixas nos cones
    'C4': ((13, 10, -5), 16, 4),  # cavalete
    'N3': ((-8, 8, 17), 14, 5),   # gelo facetado
    'N4': ((10, 5, -4), 18, 6),   # madeira e neve
    'D3': ((13, 8, -4), 15, 7),   # ruínas
    'D4': ((9, 7, 2), 19, 8),    # ossada
    'V3': ((14, 1, -5), 15, 9),   # obsidiana
    'F3': ((8, 7, -3), 17, 10),  # madeira
    'F4': ((9, 7, 0), 16, 11),   # galho suspenso
    'CF3': ((-5, 10, 13), 13, 12),# caixa tecnológica
    'CF4': ((-5, 8, 14), 12, 13),# cabos
    'IC3': ((-2, 10, 16), 15, 14),# cristal
    'IC4': ((8, 9, 13), 18, 15), # arco mineral
}
_CACHE = {}


def imagem_ameaca(codigo, fase=0):
    """Preserva o desenho original para todos os perigos não-estáticos."""
    if codigo not in ESTATICOS:
        return _imagem_anterior(codigo, fase)
    chave = (codigo, int(fase) % 3)
    pronto = _CACHE.get(chave)
    if pronto is not None:
        return pronto
    original = _imagem_anterior(*chave)
    rgb = pygame.surfarray.array3d(original)
    alpha = pygame.surfarray.array_alpha(original)
    w, h = original.get_size()
    # Só áreas integralmente opacas e cercadas de pixels opacos, de modo a
    # proteger máscaras, bordas, antialias e costuras das silhuetas.
    seguro = alpha == 255
    interior = seguro.copy()
    interior[0, :] = False
    interior[-1, :] = False
    interior[:, 0] = False
    interior[:, -1] = False
    interior[1:, :] &= seguro[:-1, :]
    interior[:-1, :] &= seguro[1:, :]
    interior[:, 1:] &= seguro[:, :-1]
    interior[:, :-1] &= seguro[:, 1:]
    x = np.arange(w, dtype=np.int32)[:, None]
    y = np.arange(h, dtype=np.int32)[None, :]
    brilho = (3*rgb[:,:,0].astype(np.int32)
              + 5*rgb[:,:,1].astype(np.int32)
              + 2*rgb[:,:,2].astype(np.int32)) // 10
    delta, periodo, semente = MATERIAL[codigo]
    # Marcas imersas no material existente. Distribuição determinística;
    # nunca executada a cada quadro, sem partículas, sprites ou overlays.
    if codigo in ('C3', 'C4', 'CF3', 'CF4'):
        padrao = ((x + 2*y + semente) % periodo) <= 3
    elif codigo in ('N3', 'IC3', 'V3'):
        padrao = (((2*x - y + semente) % periodo) <= 2)
    elif codigo in ('N4', 'F3', 'F4', 'IC4'):
        padrao = (((y + x//5 + semente) % periodo) <= 2)
    else:
        padrao = (((x*3 + y + semente) % periodo) <= 2)
    destino = interior & padrao & (brilho >= 55) & (brilho <= 235)
    # Materiais quentes/técnicos se destacam sem alterar os marcadores de dano.
    if codigo == 'C3':
        destino &= (rgb[:,:,0].astype(np.int16) > rgb[:,:,2].astype(np.int16) + 35)
    if codigo == 'CF4':
        destino &= (rgb[:,:,2] >= 68)
    novo = original.copy()
    pixels = pygame.surfarray.pixels3d(novo)
    if np.any(destino):
        pixels[destino] = np.clip(pixels[destino].astype(np.int16)
                                  + np.array(delta, dtype=np.int16), 0, 255).astype(np.uint8)
    del pixels
    assert pygame.surfarray.array_alpha(novo).tobytes() == alpha.tobytes()
    assert novo.get_size() == original.get_size()
    _CACHE[chave] = novo
    return novo


_COR_AVISO = {
    'C3': (255, 225, 118), 'C4': (255, 225, 118),
    'N3': (142, 235, 251), 'N4': (142, 235, 251),
    'D3': (255, 220, 143), 'D4': (255, 220, 143),
    'V3': (255, 156, 110),
    'F3': (213, 242, 140), 'F4': (213, 242, 140),
    'CF3': (127, 244, 246), 'CF4': (127, 244, 246),
    'IC3': (206, 187, 255), 'IC4': (206, 187, 255),
}


def cor_aviso_ameaca(obs):
    """Cor para o aviso triangular EXISTENTE; sem desenhos ou temporizadores novos."""
    codigo = getattr(obs, 'codigo', None)
    if codigo == 'V4':
        # Usa somente o estado de dano que o motor antigo já calculou.
        return (255, 147, 83) if not getattr(obs, '_colisao_ativa', True) else (255, 210, 114)
    return _COR_AVISO.get(codigo, (255, 216, 109))


class AmeacaBioma(_AmeacaAnterior):
    """Troca somente imagem de estáticos; motor e update v3.186 intactos."""
    def __init__(self, x, codigo):
        super().__init__(x, codigo)
        if codigo in ESTATICOS:
            rect_original = self.rect.copy()
            self.image = imagem_ameaca(codigo, 0)
            assert self.rect == rect_original
