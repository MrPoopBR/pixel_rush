"""v3.277.4-PROD: liberação pontual de recursos de biomas já descarregados.

Mantém o desenho e os limites originais dos caches. A coleta só acontece
nas trocas de cenário (nunca no ciclo por frame); não altera a física.
Não solicita a memória de volta a um alocador específico de SO.
"""
import gc
from pixelrush_world_v3232 import LivingWorld as _MundoAnterior


class LivingWorld(_MundoAnterior):
    def _get_modular(self):
        # O motor original elimina o bioma modular anterior, mas as camadas
        # de identidade/geometria contêm callbacks vinculados ao próprio
        # objeto e, portanto, ciclos de referência. Sem coleta, seus grandes
        # buffers SDL podem continuar alocados durante muitas transições.
        descarregara_outro = bool(self.modular and self.biome not in self.modular)
        cena = super()._get_modular()
        if descarregara_outro:
            gc.collect()
        return cena

    def switch(self, biome):
        anterior = self.biome
        super().switch(biome)
        if anterior != self.biome and self.biome == 'cidade' and self.modular:
            # O framebuffer da transição já foi capturado por super().switch;
            # não é necessário manter um cenário modular que saiu de cena.
            self.modular.clear()
            gc.collect()
