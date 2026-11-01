"""v3.151 — integração do passe visual das Ilhas Celestiais."""
from pixelrush_world_v3150 import LivingWorld as Previous, CLASSICOS
from pixelrush_biomes2_v3151 import ModularBiomeScene

class LivingWorld(Previous):
    def _get_modular(self):
        if CLASSICOS:
            return super()._get_modular()
        scene=self.modular.get(self.biome)
        if scene is None:
            scene=ModularBiomeScene(self.biome)
            self.modular.clear()
            self.modular[self.biome]=scene
        scene.visual_quality=0 if self.lightweight else 1
        return scene
