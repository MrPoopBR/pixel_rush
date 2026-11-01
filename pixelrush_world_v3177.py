"""v3.177.0 — ponto de integração de luz e materiais no motor existente."""
from pixelrush_world_v3175 import LivingWorld as Anterior
from pixelrush_world_v3163 import CLASSICOS
from pixelrush_biomes2_v3177 import ModularBiomeScene
from pixelrush_city2_v3177 import aplicar_luz_cidade


class LivingWorld(Anterior):
    def __init__(self, biome='cidade', lightweight=False):
        super().__init__(biome=biome, lightweight=lightweight)
        if self.biome=='cidade':
            aplicar_luz_cidade(self.city2)

    def _get_modular(self):
        if CLASSICOS or self.biome=='cidade':
            return super()._get_modular()
        scene=self.modular.get(self.biome)
        if scene is None:
            scene=ModularBiomeScene(self.biome)
            self.modular.clear()
            self.modular[self.biome]=scene
        scene.visual_quality=0 if self.lightweight else 1
        return scene

    def switch(self,biome):
        anterior=self.biome
        super().switch(biome)
        if self.biome=='cidade' and anterior != 'cidade':
            aplicar_luz_cidade(self.city2)
