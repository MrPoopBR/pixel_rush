"""v3.165: somente refinamento visual do bioma Vulcão."""
from pixelrush_world_v3164 import LivingWorld as Anterior
from pixelrush_world_v3163 import CLASSICOS
from pixelrush_biomes2_v3165 import ModularBiomeScene

class LivingWorld(Anterior):
    def _get_modular(self):
        if CLASSICOS:
            return super()._get_modular()
        scene = self.modular.get(self.biome)
        if scene is None:
            scene = ModularBiomeScene(self.biome)
            self.modular.clear()
            self.modular[self.biome] = scene
        scene.visual_quality = 0 if self.lightweight else 1
        return scene
