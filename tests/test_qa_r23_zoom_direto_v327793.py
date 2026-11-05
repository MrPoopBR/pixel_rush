# -*- coding: utf-8 -*-
"""R23 QA793: teste RGBA do zoom sem executar main, saves ou Android."""
import os
import random
import statistics
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

pygame.init()
pygame.display.set_mode((450, 800))
from pixelrush_gamefeel_v3132 import GameFeel as GameFeelBase
from pixelrush_gamefeel_v3152 import GameFeel as GameFeelQA

W, H = 450, 800
r = random.Random(327793)
src = pygame.Surface((W, H)).convert()
src.fill((28, 51, 92))
for _ in range(650):
    pygame.draw.rect(src,
        (r.randrange(256), r.randrange(256), r.randrange(256)),
        (r.randrange(W), r.randrange(H),
         r.randrange(1, 50), r.randrange(1, 80)))
rgba = lambda surface: pygame.image.tobytes(surface, "RGBA")

old, new = GameFeelBase(), GameFeelQA()
old_ms, new_ms = [], []
for frame in range(500):
    zoom = .0023 + (frame % 25) * .00083
    old.zoom = new.zoom = zoom
    t0 = time.perf_counter_ns()
    antigo = old.acabamento_camera(src, True)
    t1 = time.perf_counter_ns()
    novo = new.acabamento_camera(src, True)
    t2 = time.perf_counter_ns()
    assert antigo.get_size() == novo.get_size() == (W, H)
    assert rgba(antigo) == rgba(novo), ("RGBA", frame, zoom)
    old_ms.append((t1-t0)/1e6)
    new_ms.append((t2-t1)/1e6)
assert new._cache_zoom_quadro is None, "Caminho RGB alocou buffer legado"

alpha = pygame.Surface((W, H), pygame.SRCALPHA)
alpha.fill((80, 165, 221, 93))
colorkey = src.copy()
colorkey.set_colorkey((28, 51, 92))
global_alpha = src.copy()
global_alpha.set_alpha(143)
dimensao = pygame.Surface((400, 700)).convert()
dimensao.fill((80, 170, 190))
for name, image in (("srcalpha", alpha), ("colorkey", colorkey),
                    ("alpha_global", global_alpha), ("dimensao", dimensao)):
    old.zoom = new.zoom = .015
    assert rgba(old.acabamento_camera(image, True)) == rgba(
        new.acabamento_camera(image, True)), name
for active, zoom in ((False, .022), (True, 0.), (True, .002)):
    new.zoom = zoom
    assert new.acabamento_camera(src, active) is src
before, after = statistics.median(old_ms), statistics.median(new_ms)
print("QA793 CAMERA: 500 RGBA iguais, 4 fallbacks e 3 casos sem zoom")
print("p50 do zoom isolado pygame-ce/ms:", round(before, 5), round(after, 5),
      "delta%:", round(100*(after/before-1),2) if before else "NA")
print("Teste Linux SDL dummy: nao implica FPS Android ou frame completo")
pygame.quit()
