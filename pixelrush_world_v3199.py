"""Plano G v3.199.0: acabamento atmosférico somente no pano de fundo."""
from pixelrush_world_v3198 import LivingWorld as Anterior
from pixelrush_atmosfera_v3199 import aplicar


class LivingWorld(Anterior):
    def _city_surface(self, kind='image', foreground_only=False):
        resultado = super()._city_surface(kind, foreground_only)
        if kind == 'image' and not foreground_only and not self.lightweight:
            aplicar(resultado, self.biome, self.night, self.phase, self.climate)
        return resultado
