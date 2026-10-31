"""Plano D / Etapa 5: correções localizadas das costuras já existentes.

Floresta Densa: realinha centros das árvores originais para não cortar copas.
Ilhas Celestiais: remove linhas de 1px isoladas no começo dos chunks próximos.
Nada adiciona conteúdo, nem altera hitboxes, física ou regras da partida.
"""
from pixelrush_biomes2_v3177 import ModularBiomeScene as Anterior


class ModularBiomeScene(Anterior):
    def __init__(self, biome):
        super().__init__(biome)
        if biome == 'ilhas_celestes':
            # Cada chunk da v3.178 começa com 7 pixels opacos isolados
            # (x=0, y=214..220) sem continuidade com x=1 ou o chunk anterior.
            # A faixa de terreno real inicia em y>=221 e não é modificada.
            consertos = 0
            proximos = self._layers['near']
            for i, surf in enumerate(proximos):
                anterior = proximos[i - 1]
                for y in range(214, 221):
                    if (surf.get_at((0, y)).a == 255 and
                            surf.get_at((1, y)).a == 0 and
                            anterior.get_at((anterior.get_width() - 1, y)).a == 0):
                        surf.set_at((0, y), (0, 0, 0, 0))
                        consertos += 1
            # Não pagar custo de edição nem invalidação a cada quadro.
            if consertos:
                if hasattr(self, '_map_cache'):
                    self._map_cache.clear()
                if hasattr(self, '_composites'):
                    self._composites.clear()

    @staticmethod
    def _posicao_copa(bioma, x, plano, margem):
        if bioma != 'floresta':
            return x
        # Limites internos do chunk de 225px para não cortar copas existentes.
        if plano == 'mid':
            return max(40, min(160, x))
        return max(margem, min(225 - margem - 1, x))

    def _tree(self, s, x, ground, height, seed, depth='mid', shape='broad'):
        # Nas copas largas, o centro anterior em x=171..198 cruzava a costura.
        margem = 64 if depth == 'mid' else 38
        x = self._posicao_copa(self.biome, x, depth, margem)
        return super()._tree(s, x, ground, height, seed, depth, shape)

    def _tree_rich(self, surf, x, base, h, seed, shape='round'):
        # Respeita os volumes originais das árvores enriquecidas na v3.136.
        x = self._posicao_copa(self.biome, x, None, 39)
        return super()._tree_rich(surf, x, base, h, seed, shape)

    def _forest_tree_polish(self, s, x, ground, height, seed,
                            layer='mid', shape='umbrella'):
        # O acabamento deve seguir o tronco reposicionado, não a antiga posição.
        margem = 64 if layer == 'mid' else 38
        x = self._posicao_copa(self.biome, x, layer, margem)
        return super()._forest_tree_polish(s, x, ground, height, seed, layer, shape)
