"""Somente a seleção do novo mosaico modular; resto é a v3.130."""
from pixelrush_world_v3130 import LivingWorld as Previous
import os
if os.environ.get('PIXELRUSH_CENARIOS_CLASSICOS') == '1':
    from pixelrush_biomes2_v3127 import ModularBiomeScene
else:
    from pixelrush_biomes2_v3131 import ModularBiomeScene

class LivingWorld(Previous):
    def _get_modular(self):
        scene = self.modular.get(self.biome)
        if scene is None:
            scene = ModularBiomeScene(self.biome)
            self.modular[self.biome] = scene
            if len(self.modular) > 1:
                for nome in list(self.modular):
                    if nome != self.biome:
                        self.modular.pop(nome, None)
        scene.visual_quality = 0 if self.lightweight else 1
        return scene
