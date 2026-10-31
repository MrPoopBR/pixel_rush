"""Plano G v3.200.0: identidade de materiais dos sete biomas (somente cenário)."""
from pixelrush_world_v3199 import LivingWorld as Anterior
from pixelrush_identidade_v3200 import instalar_cidade, instalar_modular


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
