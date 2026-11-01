"""Pixel Rush v3.181.0: integra microvida no render modular da v3.179.

Cidade: preserva integralmente o sistema CityLife (cabos, carros, atmosfera,
janelas e vento). A animação preexistente continua sem novo passe/custo.
"""
from pixelrush_world_v3179 import LivingWorld as Anterior
from pixelrush_world_v3163 import CLASSICOS
from pixelrush_biomes2_v3181 import ModularBiomeScene


class LivingWorld(Anterior):
    def _get_modular(self):
        if CLASSICOS or self.biome == 'cidade':
            return super()._get_modular()
        scene = self.modular.get(self.biome)
        if scene is None:
            scene = ModularBiomeScene(self.biome)
            self.modular.clear()  # mesmo limite de memoria do jogo original
            self.modular[self.biome] = scene
        scene.visual_quality = 0 if self.lightweight else 1
        return scene
