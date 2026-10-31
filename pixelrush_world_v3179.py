"""Plano D / Etapa 5: mantém o motor v3.177 e corrige exclusivamente emendas de Floresta e Ilhas Celestiais."""
from pixelrush_world_v3177 import LivingWorld as Anterior
from pixelrush_world_v3163 import CLASSICOS
from pixelrush_biomes2_v3179 import ModularBiomeScene


class LivingWorld(Anterior):
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
