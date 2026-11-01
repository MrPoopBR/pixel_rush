"""Plano I v3.219.0 — lapidacao de silhuetas Cidade, Neve e Deserto."""
from pixelrush_world_v3201 import LivingWorld as Anterior
from pixelrush_geometria_v3219 import instalar_cidade, instalar_modular


class LivingWorld(Anterior):
    def __init__(self, biome='cidade', lightweight=False):
        super().__init__(biome=biome, lightweight=lightweight)
        if self.biome == 'cidade' and self.city2 is not None:
            instalar_cidade(self.city2, leve=self.lightweight)

    def _get_modular(self):
        cena=super()._get_modular()
        instalar_modular(cena, leve=self.lightweight)
        return cena

    def switch(self,biome):
        super().switch(biome)
        if self.biome == 'cidade' and self.city2 is not None:
            instalar_cidade(self.city2, leve=self.lightweight)
