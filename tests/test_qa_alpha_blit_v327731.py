# -*- coding: utf-8 -*-
"""Regressao QA: os quatro planos de profundidade nao podem mudar 1 pixel."""
import hashlib
import itertools
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from pixelrush_fase_b_visuais_v3276 import desenhar_profundidade_bioma as original


BIOMAS = (
    "cidade", "neve", "deserto", "floresta", "vulcao",
    "cidade_futurista", "ilhas_celestes",
)


def renderizar(renderizador, bioma, distancia, noite, clima, leve):
    superficie = pygame.Surface((450, 800)).convert()
    superficie.fill((52, 83, 111))
    retorno = renderizador(superficie, bioma, distancia, noite, leve, clima)
    digest = hashlib.sha256(pygame.image.tobytes(superficie, "RGB")).hexdigest()
    return retorno, digest


class TestRecorteQA(unittest.TestCase):
    def test_equivalencia_exata(self):
        pygame.init()
        pygame.display.set_mode((450, 800))
        cenarios = list(itertools.product(
            BIOMAS, (0.0, 0.23, 0.58, 1.0),
            (-950.0, 0.0, 103.0, 6210.0),
            ("limpo", "chuva", "vento"), (False, True),
        ))
        # Imagens originais sao medidas antes de instalar o patch,
        # pois o original usa aliases internos que passam a ser otimizados.
        baseline = [
            renderizar(original, biome, travel, noite, clima, leve)
            for biome, noite, travel, clima, leve in cenarios
        ]
        from pixelrush_qa_alpha_blit_v327731 import instalar
        instalar()
        from pixelrush_fase_b_visuais_v3276 import (
            desenhar_profundidade_bioma as otimizado,
        )
        for args, esperado in zip(cenarios, baseline):
            biome, noite, travel, clima, leve = args
            obtido = renderizar(otimizado, biome, travel, noite, clima, leve)
            self.assertEqual(obtido, esperado, "Cena divergente: " + repr(args))
        pygame.quit()


if __name__ == "__main__":
    unittest.main()
