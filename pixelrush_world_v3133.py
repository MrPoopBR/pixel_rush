"""v3.133 — seleção dos cenários modulares reconstruídos.

Preserva toda a infraestrutura da v3.130/v3.131: parallax, caches, transições,
GPU maps, detritos e clima. A diferença é que Floresta, Vulcão, Cidade
Futurista e Ilhas Celestes agora entram no mesmo pipeline modular dos cenários
novos, substituindo os PNGs antigos dessas faixas.
"""
from pixelrush_world_v3130 import LivingWorld as Previous
from pixelrush_biomes2_v3133 import ModularBiomeScene, MODULAR_BIOMES


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
