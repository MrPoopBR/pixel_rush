"""Cidade v3.124.2: elimina vegetação flutuante na frente dos obstáculos.

O render de primeiro plano acontecia DEPOIS dos sprites jogáveis; duas cercas-
vivas da camada fg se moviam a 1.06x a velocidade de scroll, sobre o asfalto.
A vegetação correta permanece no layer near, ancorada atrás da pista.
"""
from pixelrush_city2_v3124 import CityPilotScene as _CidadeAnterior
from pixelrush_city2_v3115 import ChunkVariant


class CityPilotScene(_CidadeAnterior):
    def _make_fg_variant(self, idx):
        # Nenhum arbusto na frente do jogador/inimigos. Props urbanos
        # continuam na layer near (composta no fundo da Cidade).
        return ChunkVariant(**self._blank_maps(), sprites=[])
