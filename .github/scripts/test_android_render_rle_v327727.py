"""QA pygame-ce v3.277.27: SDL RLE sem diferenca visual em NORMAL."""
import hashlib
import os
import statistics
import sys
import time
from pathlib import Path
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import pygame
pygame.init()
pygame.display.set_mode((450,800))
import pixelrush_city2_v3118 as city
import pixelrush_biomes2_v3185 as biome
from pixelrush_world_v3201 import LivingWorld

# Comparar bit a bit a textura antes e depois do RLE com recorte real.
cidade=city.CityPilotScene()
fontes=[cidade._scaled_surface(layer.variants[0],'image')
        for layer in cidade.layers]
for fonte in fontes:
    if not (fonte.get_flags() & pygame.SRCALPHA):
        continue
    fonte.set_alpha(255,0)
    for rgb in (True,False):
        alvo=(pygame.Surface((450,500)).convert() if rgb else
              pygame.Surface((450,500),pygame.SRCALPHA).convert_alpha())
        alvo.fill((50,80,130,255))
        alvo.blit(fonte,(-13,0),pygame.Rect(13,0,450,500))
        esperado=pygame.image.tobytes(alvo,'RGBA')
        fonte.set_alpha(255,pygame.RLEACCEL)
        alvo.fill((50,80,130,255))
        alvo.blit(fonte,(-13,0),pygame.Rect(13,0,450,500))
        assert pygame.image.tobytes(alvo,'RGBA')==esperado
        fonte.set_alpha(255,0)

# Caminho verdadeiro do mundo 2.5D: mesmos passos, clima e noite.
for nome in ('cidade','neve','deserto','cidade_futurista'):
    mundo=LivingWorld(nome,lightweight=False)
    tela=pygame.Surface((450,800)).convert()
    for passo in range(10):
        mundo.update(2.4,(passo%3)*.18,('limpo','chuva','vento')[passo%3],.4)
        with patch.object(city,'acelerar_textura_estatica',lambda s,**kw:s), \
             patch.object(biome,'acelerar_textura_estatica',lambda s,**kw:s):
            tela.fill((71,124,183))
            mundo.draw(tela)
            antes=hashlib.sha256(pygame.image.tobytes(tela,'RGB')).digest()
        tela.fill((71,124,183))
        mundo.draw(tela)
        depois=hashlib.sha256(pygame.image.tobytes(tela,'RGB')).digest()
        assert antes==depois,(nome,passo,'pixels divergentes')
    print('APROVADO pixel a pixel:',nome,'10 quadros')

# Microbenchmark informativo: nao impor ganho artificial na CPU do CI.
fonte=fontes[0]
tela=pygame.Surface((450,500),pygame.SRCALPHA)
medidas={}
for nome,flag in (('original',0),('rle',pygame.RLEACCEL)):
    fonte.set_alpha(255,flag)
    duracoes=[]
    for _ in range(7):
        t0=time.perf_counter_ns()
        for i in range(70):
            tela.blit(fonte,(-14,0),pygame.Rect(14,0,450,500))
        duracoes.append((time.perf_counter_ns()-t0)/70e6)
    medidas[nome]=round(statistics.median(duracoes),5)
print('MEDICAO SDL RGBA ms:',medidas)
print('APROVADO: 4 biomas, 40 quadros, 0 divergencias visuais')
pygame.quit()
