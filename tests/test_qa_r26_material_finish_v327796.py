# -*- coding: utf-8 -*-
"""R26 sete biomas: 2D reference RGBA exato sem rim; rim so cor, nao alpha."""
import os,random,runpy
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import numpy as np
import pygame
pygame.init();pygame.display.set_mode((450,800))
from src.pixelrush.rendering import material_friezes_v327794 as new
old=runpy.run_path('tests/fixtures/material_friezes_r25_reference.py')
from pixelrush_texturas_v3185 import refinar_textura
C={'cidade':(125,125,127),'neve':(146,170,190),'deserto':(198,150,113),
   'vulcao':(145,90,65),'floresta':(70,138,70),
   'cidade_futurista':(79,156,182),'ilhas_celestes':(126,165,195)}
assert set(C)==set(new.PERFIS)
for i,(biome,color) in enumerate(C.items()):
    for test_case in range(5):
        size=(225,250)
        a=pygame.Surface(size,pygame.SRCALPHA)
        b=pygame.Surface(size,pygame.SRCALPHA)
        a.fill((*color,255))
        rng=random.Random(20261105+i*17+test_case)
        for z in range(18):
            w=rng.randrange(7,28);h=rng.randrange(6,18)
            rect=pygame.Rect(rng.randrange(0,225-w),rng.randrange(0,250-h),w,h)
            rgba=(*color,rng.choice((0,90,170,255)))
            pygame.draw.rect(a,rgba,rect)
        # Copia RAW: preserva tambem RGB oculto dos pixels alpha zero.
        pygame.transform.scale(a,a.get_size(),b)
        # Ambos começam com a mesma textura Premium já existente.
        refinar_textura(a,biome,'near',test_case)
        refinar_textura(b,biome,'near',test_case)
        new._R26_EDGE_RIM=False
        old_result=old['aplicar_friso'](a,biome,'near',test_case)
        new_result=new.aplicar_friso(b,biome,'near',test_case)
        assert old_result[1]==new_result[1],(biome,test_case,'count')
        assert (old_result[0] is None)==(new_result[0] is None)
        if old_result[0] is not None:
            assert np.array_equal(old_result[0],new_result[0]),(biome,test_case,'delta')
        assert pygame.image.tobytes(a,'RGBA')==pygame.image.tobytes(b,'RGBA'),(biome,test_case,'RGBA')
    # Novo contorno: um teto opaco com espaço translúcido acima.
    sample=pygame.Surface((225,250),pygame.SRCALPHA)
    sample.fill((0,0,0,0))
    pygame.draw.rect(sample,(*color,255),(18,48,190,165))
    plain=sample.copy()
    new._R26_EDGE_RIM=False
    new.aplicar_friso(plain,biome,'near',3)
    new._R26_EDGE_RIM=True
    delta,n=new.aplicar_friso(sample,biome,'near',3)
    assert pygame.image.tobytes(sample,'RGBA')[3::4]==pygame.image.tobytes(plain,'RGBA')[3::4],biome
    assert pygame.image.tobytes(sample,'RGBA')!=pygame.image.tobytes(plain,'RGBA'),(biome,'rim invisible')
    assert delta is not None and abs(int(delta.min()))<=5 and abs(int(delta.max()))<=5
    print('QA796',biome,'borda premium com alfa igual e delta limitado')
new._R26_EDGE_RIM=True
print('QA796 35 RGBA 100% iguais ao legado sem rim + 7 biomas de contorno alfa preservado')
pygame.quit()
