"""v3.198.0 — usa a geometria 2.5D v3.197 e separa profundidade dinâmica."""
from pixelrush_world_v3197 import LivingWorld as Anterior
from pixelrush_profundidade_v3198 import instalar_cidade, instalar_modular


class LivingWorld(Anterior):
    def __init__(self, biome='cidade', lightweight=False):
        super().__init__(biome=biome, lightweight=lightweight)
        if self.biome == 'cidade' and self.city2 is not None:
            instalar_cidade(self.city2, leve=self.lightweight)

    def _get_modular(self):
        cena = super()._get_modular()
        instalar_modular(cena, leve=self.lightweight)
        return cena

    def switch(self, biome):
        super().switch(biome)
        if self.biome == 'cidade' and self.city2 is not None:
            instalar_cidade(self.city2, leve=self.lightweight)
