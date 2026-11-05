# -*- coding: utf-8 -*-
"""QA793: acabamento estatico da Cidade, mapas tecnicos preservados."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((450,800))
from pixelrush_city2_v3125 import CityPilotScene
from pixelrush_city2_v3123 import CityPilotScene as Parent
scene=CityPilotScene()
layer=next(l for l in scene.layers if l.name=="near")
assert len(layer.variants)>=3
# Interceptar o mesmo objeto produzido pelo metodo base ANTES da pintura.
# Gerar uma segunda variante independente mudaria estado procedural e
# invalidaria a comparacao, mesmo sem tocar nos canais tecnicos.
original=Parent._make_near_variant
local="_make_near_variant" in Parent.__dict__
captured=[]
def observe(self,idx):
    v=original(self,idx)
    captured.append({name:pygame.image.tobytes(getattr(v,name),"RGBA")
                     for name in ("normal","geometry","flow","fxmask")})
    return v
try:
    Parent._make_near_variant=observe
    for idx,existing in enumerate(layer.variants):
        captured.clear()
        v=scene._make_near_variant(idx)
        assert len(captured)==1, "base nao passou pelo observador"
        for name, before in captured[0].items():
            assert pygame.image.tobytes(getattr(v,name),"RGBA")==before,(idx,name)
        x=56+(idx%3)*12
        for variant in (existing,v):
            assert tuple(variant.image.get_at((x,228)))[:3] == (77,79,83), (idx,"junta")
            assert tuple(variant.image.get_at((x+1,228)))[:3] == (158,155,151), (idx,"realce")
            assert tuple(variant.material.get_at((x,228)))[:3] == (93,91,91), (idx,"material")
finally:
    if local: Parent._make_near_variant=original
    else: delattr(Parent,"_make_near_variant")
print("QA793 City art: pintura prebaked, 4 canais RGBA invariantes por variante")
pygame.quit()
