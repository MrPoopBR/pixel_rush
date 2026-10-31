"""v3.175.0 — composição/organização dos planos dos seis biomas modulares.

Reaproveita integralmente a arte anterior. Remove os realces artificiais
aplicados nas extremidades de cada chunk pela v3.169 e reequilibra somente
os planos distantes. Sem novos elementos decorativos.
"""
from pixelrush_biomes2_v3169 import ModularBiomeScene as Anterior
from pixelrush_composicao_v3175 import compor_plano


class ModularBiomeScene(Anterior):
    def _apply_soft_chunk_bind(self, surf, layer):
        # Evita listras verticais recorrentes exatamente nas emendas.
        # As faixas de terreno contínuo anteriores seguem preservadas.
        return None

    def _depth_rim(self, surf, idx):
        # Aplica a mesma névoa em todo chunk, inclusive nos índices ímpares.
        # Antes a linha y=205 existia só nos índices pares: quebra perceptível.
        import pygame
        pal = self.PALETTE.get(self.biome, self.PALETTE['cidade_futurista'])
        haze = pygame.Surface((surf.get_width(), 36), pygame.SRCALPHA)
        for y in range(36):
            a = 3 + y // 8
            pygame.draw.line(haze, (*pal['shade'], a), (0, y), (surf.get_width()-1, y), 1)
        surf.blit(haze, (0, 178))

    def __init__(self, biome):
        super().__init__(biome)
        if biome in self.FINAL_BIOMES:
            for layer in ('far', 'mid'):
                for surf in self._layers[layer]:
                    compor_plano(surf, biome, layer)
            if hasattr(self, '_map_cache'):
                self._map_cache.clear()
            if hasattr(self, '_composites'):
                self._composites.clear()
