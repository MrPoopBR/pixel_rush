"""Plano F v3.185.0 — ativação pontual do microacabamento de texturas."""
from pixelrush_world_v3182 import LivingWorld as Anterior
from pixelrush_world_v3163 import CLASSICOS
from pixelrush_biomes2_v3185 import ModularBiomeScene
from pixelrush_texturas_v3185 import aplicar_texturas_cidade


class LivingWorld(Anterior):
    def __init__(self, biome='cidade', lightweight=False):
        super().__init__(biome=biome, lightweight=lightweight)
        if self.biome == 'cidade' and not self.lightweight:
            aplicar_texturas_cidade(self.city2)

    def _get_modular(self):
        if CLASSICOS or self.biome == 'cidade':
            return super()._get_modular()
        scene = self.modular.get(self.biome)
        if scene is None:
            scene = ModularBiomeScene(self.biome, lightweight=self.lightweight)
            self.modular.clear()  # mesmo limite original: 1 bioma residente
            self.modular[self.biome] = scene
        scene.visual_quality = 0 if self.lightweight else 1
        return scene

    def switch(self, biome):
        anterior = self.biome
        super().switch(biome)
        if self.biome == 'cidade' and anterior != 'cidade' and not self.lightweight:
            aplicar_texturas_cidade(self.city2)
