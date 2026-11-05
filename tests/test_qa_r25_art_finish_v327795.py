# -*- coding: utf-8 -*-
"""QA795: arte premium sutil nos 7 biomas, sem alterar alfa e com rollback."""
import os
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame
pygame.init()
pygame.display.set_mode((450,800))
import src.pixelrush.rendering.material_friezes_v327794 as m
from pixelrush_texturas_v3185 import refinar_textura
COLORS={'cidade':(125,125,127),'neve':(146,170,190),
        'deserto':(198,150,113),'vulcao':(145,90,65),
        'floresta':(70,138,70),'cidade_futurista':(79,156,182),
        'ilhas_celestes':(126,165,195)}
assert set(COLORS)==set(m.PERFIS)
try:
    for biome,color in COLORS.items():
        a=pygame.Surface((225,250),pygame.SRCALPHA)
        b=pygame.Surface((225,250),pygame.SRCALPHA)
        a.fill((*color,255));b.fill((*color,255))
        refinar_textura(a,biome,"near",3)
        refinar_textura(b,biome,"near",3)
        m._R25_DETAILS=False
        base,count_base=m.aplicar_friso(a,biome,"near",3)
        m._R25_DETAILS=True
        cand,count_cand=m.aplicar_friso(b,biome,"near",3)
        old=pygame.image.tobytes(a,"RGBA");new=pygame.image.tobytes(b,"RGBA")
        assert old!=new,(biome,"novo acabamento invisivel")
        assert old[3::4]==new[3::4],(biome,"mudou o alpha")
        assert count_cand>count_base>0,(biome,count_base,count_cand)
        assert count_cand<225*250//8,(biome,"poluicao visual")
        rgba_a=pygame.surfarray.array3d(a).astype("int16")
        rgba_b=pygame.surfarray.array3d(b).astype("int16")
        diff=rgba_b-rgba_a
        assert int(diff.min())>=-3 and int(diff.max())<=3,(biome,"delta acima do limite")
        print("QA795 detalhes",biome,"antigo",count_base,"novo",count_cand)
finally:
    m._R25_DETAILS=True
pygame.quit()
