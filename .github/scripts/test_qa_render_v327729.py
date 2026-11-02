#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comparacao pixel a pixel real do compositor 2.5D antes/depois, sem dispositivo."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import json
import pathlib
import sys
import time
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import pygame
pygame.init()
pygame.display.set_mode((450, 800))
from pixelrush_world_v3130 import LivingWorld
from pixelrush_qa_render_v327729 import instalar, restaurar_para_teste


def bytes_rgba(surf):
    return pygame.image.tobytes(surf, 'RGBA')


class TesteRender329(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        restaurar_para_teste()
        pygame.quit()

    def test_cidade_real_rgba_idêntico(self):
        mundo = LivingWorld('cidade', lightweight=True)
        # Testa buffers reutilizados e multiplos valores de travel, noite, clima, frame.
        canais = ('image', 'normal', 'geometry', 'fxmask', 'material', 'flow')
        casos = ((0., 0, 0., 'limpo', .5),
                 (231., 15, .42, 'chuva', .37),
                 (902., 27, .88, 'tempestade', .91))
        import pixelrush_world_v3130 as engine
        referencia = engine.LivingWorld._city_surface
        anterior = []
        otimizado = []
        for travel, frame, night, climate, phase in casos:
            mundo.travel, mundo.frame, mundo.night = travel, frame, night
            mundo.climate, mundo.phase = climate, phase
            for kind in canais:
                t0 = time.perf_counter_ns()
                img_antes = referencia(mundo, kind).copy()
                anterior.append((time.perf_counter_ns()-t0)/1e6)
                instalar()
                t1 = time.perf_counter_ns()
                img_depois = mundo._city_surface(kind).copy()
                otimizado.append((time.perf_counter_ns()-t1)/1e6)
                self.assertEqual(bytes_rgba(img_antes), bytes_rgba(img_depois),
                    'Pixels diferentes: %s em %s' % (kind, (travel,frame,night,climate,phase)))
                restaurar_para_teste()
        print('PIXELS=IDENTICOS cidade %d casos; media legado=%.3f ms, QA=%.3f ms'
              % (len(anterior),sum(anterior)/len(anterior),
                 sum(otimizado)/len(otimizado)))

    def test_outros_seis_biomas_rgb_identicos(self):
        # Usa a mesma hierarquia de producao que o jogo importa.
        from pixelrush_world_prod_v32777 import LivingWorld as MundoJogo
        biomas = ('neve', 'deserto', 'vulcao', 'floresta',
                  'cidade_futurista', 'ilhas_celestes')
        total = 0
        for bioma in biomas:
            mundo = MundoJogo(bioma, lightweight=True)
            mundo.travel, mundo.frame = 343.5, 19
            mundo.night, mundo.phase, mundo.climate = .37, .62, 'chuva'
            for kind in ('image', 'normal', 'material'):
                baseline = mundo._city_surface(kind).copy()
                instalar()
                alterado = mundo._city_surface(kind).copy()
                self.assertEqual(bytes_rgba(baseline), bytes_rgba(alterado),
                                 'Bioma/canal divergente: %s/%s' % (bioma, kind))
                restaurar_para_teste()
                total += 1
            del mundo
        print('PIXELS=IDENTICOS %d casos em 6 biomas modulares' % total)

    def test_sem_limpeza_perdida_foreground(self):
        mundo = LivingWorld('cidade',lightweight=True)
        import pixelrush_world_v3130 as engine
        anterior = engine.LivingWorld._city_surface
        base = anterior(mundo, 'image', True).copy()
        instalar()
        novo = mundo._city_surface('image',True).copy()
        self.assertEqual(bytes_rgba(base), bytes_rgba(novo))
        restaurar_para_teste()

    def test_codigo_tutorial_fisica_e_camera_preservados(self):
        base = pathlib.Path(__file__).resolve().parents[2]
        codigo = (base / 'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        self.assertIn('cache_tutorial_congelado is not None', codigo)
        self.assertIn('MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15', codigo)
        self.assertIn('relogio.tick(FPS_RENDER)',codigo)
        self.assertIn('camera_cinematica.aplicar(',codigo)
        self.assertIn('v3.277.30-QA-ANDROID-RC',codigo)


if __name__ == '__main__':
    unittest.main(verbosity=2)
