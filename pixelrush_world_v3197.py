"""Plano G v3.197.0 — instala volume 2.5D visual no motor existente."""
from pixelrush_world_v3185 import LivingWorld as Anterior
from pixelrush_geometria_v3197 import instalar_cidade, instalar_modular


class LivingWorld(Anterior):
    def __init__(self, biome='cidade', lightweight=False):
        super().__init__(biome=biome, lightweight=lightweight)
        if self.biome == 'cidade' and self.city2 is not None:
            instalar_cidade(self.city2, leve=self.lightweight)

    def _get_modular(self):
        scene = super()._get_modular()
        instalar_modular(scene, leve=self.lightweight)
        return scene

    def switch(self, biome):
        super().switch(biome)
        if self.biome == 'cidade' and self.city2 is not None:
            instalar_cidade(self.city2, leve=self.lightweight)
