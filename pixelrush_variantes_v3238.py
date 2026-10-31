# -*- coding: utf-8 -*-
"""v3.238.0: variantes pré-renderizadas e alturas aéreas conservadoras.

Somente os sete perigos acrescentados na v3.237.0 podem variar. Reutiliza
as classes/atlas/hitboxes/rotas/spawn anteriores, sem RNG extra. Alturas
variam apenas PARA CIMA (0, 6 ou 12 pixels), preservando a passagem inferior.
PNG alternativo pré-preparado no pacote e sem pós-processamento por quadro.
"""
from functools import lru_cache
from pathlib import Path
import pygame
from pixelrush_perigos_v3237 import (
    ObstaculoMovel as _Base, POR_NOME, quadros_novos,
    escolher, NOVOS,
)
from pixelrush_moveis_v3222 import LARGURA, ALTURA, FRAMES

_ATLAS = Path(__file__).resolve().parent / 'assets' / 'variacoes_v3238'
AEREOS_VARIAVEIS = frozenset(('polvo_eletrostatico', 'vespa_prismatica'))
DESLOCAMENTOS_ALTURA = (0, -6, -12)


@lru_cache(maxsize=7)
def quadros_alternativos(tipo):
    if tipo not in POR_NOME:
        raise ValueError('Variação não autorizada: ' + str(tipo))
    atlas = pygame.image.load(str(_ATLAS / (tipo + '_alt.png'))).convert_alpha()
    if atlas.get_size() != (FRAMES * LARGURA, ALTURA):
        raise ValueError('Atlas alternativo inválido: ' + str(tipo))
    return tuple(atlas.subsurface((i * LARGURA, 0, LARGURA, ALTURA)).copy()
                 for i in range(FRAMES))


class ObstaculoMovel(_Base):
    """Mesma mecânica e hitbox relativa; altera somente novos sprites.

    A faixa superior não desce, não fecha a rota PASSAGEM e nunca envolve
    tipos herdados, obstáculos de solo ou física do jogador.
    """
    def __init__(self, x_pos, tipo):
        super().__init__(x_pos, tipo)
        if tipo not in POR_NOME:
            return
        # Função pura, sem RNG ou contador: replays iguais a partir do mesmo x.
        setor = int(x_pos) // 53
        self.variante_visual_v3238 = (setor + len(tipo)) % 2
        if self.variante_visual_v3238:
            self._frames = quadros_alternativos(tipo)
            self.image = self._frames[0]
        self.faixa_aerea_v3238 = 0
        if tipo in AEREOS_VARIAVEIS:
            self.faixa_aerea_v3238 = DESLOCAMENTOS_ALTURA[setor % 3]
            self.rect.y += self.faixa_aerea_v3238
            self._base_y = self.rect.y
