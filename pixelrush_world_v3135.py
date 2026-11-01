"""Pixel Rush v3.135 — módulos artísticos vivos, sem refazer motor de corrida."""
from pixelrush_world_v3134 import LivingWorld as Anterior, CLASSICOS
from pixelrush_biomes2_v3135 import ModularBiomeScene


class LivingWorld(Anterior):
    def _get_modular(self):
        if CLASSICOS:
            return super()._get_modular()
        scene = self.modular.get(self.biome)
        if scene is None:
            scene = ModularBiomeScene(self.biome)
            self.modular.clear()  # 1 bioma modular residente no Android
            self.modular[self.biome] = scene
        scene.visual_quality = 0 if self.lightweight else 1
        return scene
