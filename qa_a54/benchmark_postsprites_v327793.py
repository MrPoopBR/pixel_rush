# -*- coding: utf-8 -*-
"""R23: diagnostico de desenho apos sprites com SDL dummy e arte COMPLETA.

Executa o modulo REAL de clima e GameFeel, com grupo representativo de
particulas em coordenadas fixas. Nao e o loop completo nem Android real;
mede chamadas por passe, memoria RSS, pixel e custo sem alterar saves.
"""
import hashlib
import json
import os
import random
import resource
import runpy
import statistics
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame
pygame.init()
tela=pygame.display.set_mode((450,800))
engine=runpy.run_path(str(ROOT/"PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py"),
                      run_name="pixelrush_r23_postsprites_import")
from pixelrush_gamefeel_v3152 import GameFeel
SistemaClima=engine["SistemaClima"]

def metricas(valores):
    values=sorted(valores)
    if not values:return {}
    def p(frac):return round(values[int((len(values)-1)*frac)],5)
    return {"n":len(values),"p50_ms":p(.50),"p95_ms":p(.95),
            "p99_ms":p(.99),"mean_ms":round(statistics.mean(values),5)}

def medir():
    random.seed(20261105)
    clima=SistemaClima()
    camera=GameFeel()
    camera.zoom=.015
    camera.vel_efeito=.9
    jogador=SimpleNamespace(
        rect=pygame.Rect(98,560,56,72),no_chao=False,morrendo=False,
        jetpack_fase=None,descida_rapida=False,anim_pulo_frames=2,
        anim_pouso_ticks=0,agachado=False)
    grupo=pygame.sprite.Group()
    img=pygame.Surface((9,9),pygame.SRCALPHA)
    pygame.draw.circle(img,(255,230,156,215),(4,4),3)
    for i in range(48):
        sp=pygame.sprite.Sprite()
        sp.image=img
        sp.rect=img.get_rect(topleft=(i*67%449,180+(i*41)%520))
        grupo.add(sp)
    grupo_hud=pygame.sprite.Group()
    chuva=("limpo","chuva","tempestade","areia","nevasca",
           "cinzas","vento_folhas","chuva_acida")
    tempos={"grupo_48":[],"gamefeel":[],"camera":[],"apresentacao":[]}
    for tipo in chuva:tempos["clima_"+tipo]=[]
    hashes=[]
    for frame in range(1,241):
        tipo=chuva[(frame//30)%len(chuva)]
        clima.tipo=tipo
        camera.tempo=frame
        tela.fill((28,51,92))
        t0=time.perf_counter_ns()
        grupo.draw(tela)
        t1=time.perf_counter_ns()
        camera.desenhar(tela,jogador,combo=7,bioma="cidade")
        t2=time.perf_counter_ns()
        clima.draw(tela,reduzir_flash=False)
        t3=time.perf_counter_ns()
        final=camera.acabamento_camera(tela,True)
        t4=time.perf_counter_ns()
        pygame.display.get_surface().blit(final,(0,0))
        pygame.display.flip()
        t5=time.perf_counter_ns()
        if frame>24:
            tempos["grupo_48"].append((t1-t0)/1e6)
            tempos["gamefeel"].append((t2-t1)/1e6)
            tempos["clima_"+tipo].append((t3-t2)/1e6)
            tempos["camera"].append((t4-t3)/1e6)
            tempos["apresentacao"].append((t5-t4)/1e6)
        if frame in (1,30,75,110,145,180,215,240):
            hashes.append(hashlib.sha256(pygame.image.tobytes(tela,"RGBA")).hexdigest())
    return {"hashes":hashes,"tempos":{k:metricas(v) for k,v in tempos.items()},
            "rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}

baseline=medir()
repeticao=medir()
assert baseline["hashes"]==repeticao["hashes"],"visuais nao deterministas"
report={
    "schema":"pixelrush.qa.r23.postsprites.v327793",
    "hardware_android_testado":False,
    "render_completo_real":False,
    "nota":"GameFeel, clima e sprite Group reais; sprites mock; sem simulacao/saves/Android",
    "plataforma":sys.platform,"pygame_ce":pygame.version.ver,
    "quadros_por_passagem":240,"amostras_rgba_comparadas":len(baseline["hashes"]),
    "hashes_rgba_repetidos":baseline["hashes"],
    "tempos_primeira":baseline["tempos"],
    "tempos_repeticao":repeticao["tempos"],
    "rss_max_kib":max(baseline["rss_kib"],repeticao["rss_kib"]),
}
output=ROOT/"qa_a54/qa793_postsprites.json"
output.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf8")
print(json.dumps({k:v for k,v in report.items() if k!="hashes_rgba_repetidos"},
                 ensure_ascii=False))
pygame.quit()
