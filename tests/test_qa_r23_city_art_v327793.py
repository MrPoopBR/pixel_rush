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
for idx,v in enumerate(layer.variants):
    x=56+(idx%3)*12
    assert tuple(v.image.get_at((x,228)))[:3] == (77,79,83), (idx,"junta")
    assert tuple(v.image.get_at((x+1,228)))[:3] == (158,155,151), (idx,"realce")
    assert tuple(v.material.get_at((x,228)))[:3] == (93,91,91), (idx,"material")
    original=Parent._make_near_variant(scene,idx)
    for name in ("normal","geometry","flow","fxmask"):
        assert pygame.image.tobytes(getattr(v,name),"RGBA")==pygame.image.tobytes(
            getattr(original,name),"RGBA"),(idx,name)
print("QA793 City art: juntas prebaked, 4 canais tecnicos originais RGBA iguais")
pygame.quit()
