# -*- coding: utf-8 -*-
"""QA794: sete materiais polidos na carga, preservando RGB de fora e alfa."""
import os
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame
pygame.init()
pygame.display.set_mode((450,800))
from src.pixelrush.rendering.material_friezes_v327794 import aplicar_friso,PERFIS
from pixelrush_texturas_v3185 import refinar_textura

COLORS={'cidade':(125,125,127),'neve':(146,170,190),
    'deserto':(198,150,113),'vulcao':(145,90,65),
    'floresta':(70,138,70),'cidade_futurista':(79,156,182),
    'ilhas_celestes':(126,165,195)}
assert set(COLORS)==set(PERFIS)
for biome,cor in COLORS.items():
    a=pygame.Surface((225,250),pygame.SRCALPHA)
    b=pygame.Surface((225,250),pygame.SRCALPHA)
    a.fill((*cor,255));b.fill((*cor,255))
    refinar_textura(a,biome,'near',3)
    refinar_textura(b,biome,'near',3)
    old=pygame.image.tobytes(a,'RGBA')
    delta,n=aplicar_friso(b,biome,'near',3)
    new=pygame.image.tobytes(b,'RGBA')
    assert delta is not None and n>0,(biome,n)
    assert n<225*250//8,(biome,'arte excessiva')
    assert old!=new,(biome,'arte nao aplicada')
    assert old[3::4]==new[3::4],(biome,'alfa divergente')
    assert int(delta.min())>=-5 and int(delta.max())<=5
    other=pygame.Surface((225,250),pygame.SRCALPHA)
    other.fill((*cor,255))
    original=pygame.image.tobytes(other,'RGBA')
    assert aplicar_friso(other,biome,'mid',3)==(None,0)
    assert pygame.image.tobytes(other,'RGBA')==original
    print('QA794 friso',biome,n,'pixels')
print('QA794 sete biomas: apenas RGB da arte, alfa e planos nao-near preservados')
pygame.quit()
