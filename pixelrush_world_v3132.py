"""Floresta Densa 2.0: preserva todas as camadas aprovadas da v3.131."""
import os
from pixelrush_world_v3131 import LivingWorld as Previous
from pixelrush_floresta_v3132 import MarcosFloresta


class LivingWorld(Previous):
    def __init__(self,biome='cidade',lightweight=False):
        super().__init__(biome,lightweight)
        self._marcos_floresta=None

    def switch(self,biome):
        super().switch(biome)
        if self.biome != 'floresta':
            # Libera os 8 quadros ao sair do bioma: memória previsível no Android.
            self._marcos_floresta=None

    def draw(self,surface):
        super().draw(surface)
        if self.biome == 'floresta' and os.getenv('PIXELRUSH_CENARIOS_CLASSICOS') != '1':
            if self._marcos_floresta is None:
                self._marcos_floresta=MarcosFloresta()
            self._marcos_floresta.desenhar(surface,self.travel,self.lightweight)
