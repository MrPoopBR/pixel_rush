"""Plano F v3.185.0 — texturas materiais dos seis biomas modulares."""
import numpy as np
import pygame
from pixelrush_biomes2_v3182 import ModularBiomeScene as Anterior
from pixelrush_texturas_v3185 import refinar_textura


class ModularBiomeScene(Anterior):
    def __init__(self, biome, lightweight=False):
        super().__init__(biome)
        self._estatistica_texturas_3185 = {'far': 0, 'mid': 0, 'near': 0}
        if lightweight:
            # Modo leve idêntico RGB/alfa à v3.184: custo de carga e frame nulo.
            return
        # A variante de pose altera APENAS o plano próximo. Texturizar cada
        # imagem uma vez, inclusive os quadros do Deserto já existentes.
        vistas = set()
        poses = getattr(self, '_poses', None) if biome in ('deserto', 'neve') else None
        conjuntos = poses if poses else [self._layers]
        for pose, camadas in enumerate(conjuntos):
            for plano in ('mid', 'near'):
                for indice, imagem in enumerate(camadas[plano]):
                    if id(imagem) in vistas:
                        continue
                    vistas.add(id(imagem))
                    delta, qtd = refinar_textura(imagem, biome, plano, indice)
                    self._estatistica_texturas_3185[plano] += qtd
                    if delta is None or biome not in ('neve', 'deserto'):
                        continue
                    # Os dois biomas possuem 5 paletas noturnas PREEXISTENTES.
                    # Atualiza apenas seu RGB nos mesmos pixels de material,
                    # sem refazer o atlas nem alterar sua transparência.
                    for nivel in range(5):
                        night = self._night_tiles.get((pose, plano, indice, nivel))
                        if night is None:
                            continue
                        fatores = 1. - np.array((.42, .39, .27), dtype=np.float32) * (nivel / 4.)
                        ajuste = np.rint(delta[:, :, None].astype(np.float32) * fatores).astype(np.int16)
                        arr = pygame.surfarray.pixels3d(night)
                        arr[:] = np.clip(arr.astype(np.int16) + ajuste, 0, 255).astype(np.uint8)
                        del arr
        # Invalidar só imagem renderizada, NUNCA mapas físicos nem GLSL.
        self._composites.pop('image', None)
