"""v3.175.0 — conexões exclusivas de arte nos sete cenários."""
from pixelrush_world_v3169 import LivingWorld as Anterior
from pixelrush_world_v3163 import CLASSICOS
from pixelrush_biomes2_v3175 import ModularBiomeScene
from pixelrush_city2_v3175 import aplicar_composicao_cidade


class LivingWorld(Anterior):
    def __init__(self, biome='cidade', lightweight=False):
        super().__init__(biome=biome, lightweight=lightweight)
        if self.biome == 'cidade':
            aplicar_composicao_cidade(self.city2)

    def _get_modular(self):
        if CLASSICOS or self.biome == 'cidade':
            return super()._get_modular()
        scene = self.modular.get(self.biome)
        if scene is None:
            scene = ModularBiomeScene(self.biome)
            self.modular.clear()
            self.modular[self.biome] = scene
        scene.visual_quality = 0 if self.lightweight else 1
        return scene

    def switch(self, biome):
        anterior = self.biome
        super().switch(biome)
        if self.biome == 'cidade' and anterior != 'cidade':
            aplicar_composicao_cidade(self.city2)
