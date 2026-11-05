"""v3.277.5-PROD: libera cenas modulares descartadas sem coleta global síncrona.

Não interfere no desenho, na física, nos caches do cenário ativo ou nos
quadros da transição, cuja imagem já foi capturada antes de switch().
"""
from pixelrush_world_v3232 import LivingWorld as _MundoAnterior


def _liberar_cena_descartada(cena):
    """Rompe referências cíclicas de callbacks, exclusivamente na cena fora do cache.

    Os módulos visuais históricos adicionam métodos vinculados à própria cena.
    Seus caches de SDL ficam vivos por esses ciclos até um GC completo.
    Uma cena aposentada nunca volta a ser reutilizada: a próxima visita a
    um bioma cria uma cena nova, como no comportamento original.
    """
    if cena is not None:
        cena.__dict__.clear()


class LivingWorld(_MundoAnterior):
    def _get_modular(self):
        descartadas = tuple(
            cena for nome, cena in self.modular.items() if nome != self.biome
        )
        cena = super()._get_modular()
        for antiga in descartadas:
            if all(antiga is not atual for atual in self.modular.values()):
                _liberar_cena_descartada(antiga)
        return cena

    def switch(self, biome):
        anterior = self.biome
        super().switch(biome)
        if anterior != self.biome and self.biome == 'cidade' and self.modular:
            descartadas = tuple(self.modular.values())
            self.modular.clear()
            for antiga in descartadas:
                _liberar_cena_descartada(antiga)
