"""v3.177.0 — iluminação direcional na arte modular existente de seis biomas."""
from pixelrush_biomes2_v3175 import ModularBiomeScene as Anterior
from pixelrush_luz_materiais_v3177 import iluminar_material


class ModularBiomeScene(Anterior):
    def __init__(self,biome):
        super().__init__(biome)
        if biome in self.FINAL_BIOMES:
            for layer in ('far','mid','near'):
                for surf in self._layers[layer]:
                    iluminar_material(surf,biome,layer)
            if hasattr(self,'_map_cache'):
                self._map_cache.clear()
            if hasattr(self,'_composites'):
                self._composites.clear()
