# -*- coding: utf-8 -*-
"""Pixel Rush v3.237.0 — sete encontros inéditos sobre o diretor móvel EXISTENTE.

Não aumenta o número de eventos: substitui visual e tipo em parte dos eventos
já aceitos pelo seletor v3.222, mantendo a janela de dificuldade e as rotas.
Sem animação calculada por quadro: atlas PNG 6 quadros pronto, lru_cache(7).
O update, deslocamento, temporização, remoção e tempo de reação são herdados.
Nenhuma perseguição ou altura variável foi antecipada das próximas etapas.
"""
from functools import lru_cache
from pathlib import Path
import pygame
from pixelrush_moveis_v3222 import (
    ObstaculoMovel as _Original,
    escolher as _escolher_original,
    LARGURA, ALTURA, FRAMES,
)

# A classificação das rotas reaproveita a semântica da v3.222.0.
# Não registra perfis no módulo anterior, preservando todos os 21 antigos.
NOVOS = {
    'cidade': ('varredora_urbana', 'chao', 0.85, (8, 13, 68, 40)),
    'neve': ('raposa_glacial', 'chao', 1.20, (9, 12, 65, 44)),
    'deserto': ('lagarto_espinhoso', 'chao', 1.10, (7, 15, 70, 40)),
    'floresta': ('javali_musgoso', 'chao', 1.25, (8, 11, 70, 45)),
    'vulcao': ('caranguejo_basalto', 'chao', 1.00, (7, 13, 68, 42)),
    'cidade_futurista': ('polvo_eletrostatico', 'alto', 1.10, (13, 13, 55, 43)),
    'ilhas_celestes': ('vespa_prismatica', 'alto', 1.20, (8, 10, 68, 43)),
}
POR_NOME = {item[0]: (bioma, *item[1:]) for bioma, item in NOVOS.items()}
RAIZ = Path(__file__).resolve().parent / 'assets' / 'novos_perigos_v3237'

@lru_cache(maxsize=7)
def quadros_novos(tipo):
    if tipo not in POR_NOME:
        raise ValueError('Perigo v3.237.0 desconhecido: ' + str(tipo))
    atlas = pygame.image.load(str(RAIZ / (tipo + '.png'))).convert_alpha()
    if atlas.get_size() != (FRAMES * LARGURA, ALTURA):
        raise ValueError('Atlas inválido: ' + str(tipo))
    return tuple(atlas.subsurface((i * LARGURA, 0, LARGURA, ALTURA)).copy()
                 for i in range(FRAMES))


def escolher(bioma, sequencia, metros, aleatorio):
    """Apenas diversifica um encontro v3.222 autorizado. Nenhum spawn extra."""
    antigo = _escolher_original(bioma, sequencia, metros, aleatorio)
    if antigo is None or bioma not in NOVOS:
        return antigo
    nome, rota, _, _ = NOVOS[bioma]
    # A rota não pode mudar a exigência SALTO/PASSAGEM do diretor antigo.
    from pixelrush_moveis_v3222 import TIPOS
    rota_antiga = TIPOS[antigo][1]
    if rota_antiga != rota:
        return antigo
    # Um terço dos encontros compatíveis recebe espécie nova; chance de
    # gerar encontro continua idêntica, independente do bioma.
    return nome if aleatorio.random() < 0.33 else antigo


class ObstaculoMovel(_Original):
    """Mesmo update/hitbox/física da classe antiga; carrega novos PNGs por tipo."""
    def __init__(self, x_pos, tipo):
        if tipo not in POR_NOME:
            super().__init__(x_pos, tipo)
            return
        pygame.sprite.Sprite.__init__(self)
        bioma, rota, bonus, hitbox = POR_NOME[tipo]
        self.cenario = bioma
        self.tipo_movel = tipo
        self.rota = rota
        self.bonus = bonus
        self.qtd_cactos = 0
        self._frames = quadros_novos(tipo)
        self.image = self._frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = int(x_pos)
        self.rect.bottom = 692 if rota == 'alto' else 730
        self._x = float(self.rect.x)
        self._base_y = self.rect.y
        self._tick = 0
        self._hitboxes_precisas_v342 = (pygame.Rect(hitbox),)
