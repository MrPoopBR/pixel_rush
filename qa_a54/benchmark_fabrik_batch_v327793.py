# -*- coding: utf-8 -*-
"""R23: A/B batch de tiras FABRIK da Floresta/Neve, RGB oculto preservado.

Candidate substitui exclusivamente 1..N blit por blits em C na mesma ordem.
Nao altera producao, pose, destino, algoritmo de cinemática ou física.
"""
import argparse
import hashlib
import json
import os
import resource
import statistics
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
parser=argparse.ArgumentParser()
parser.add_argument("--candidato",type=int,choices=(0,1),required=True)
parser.add_argument("--output",type=Path,required=True)
args=parser.parse_args()
import pygame
pygame.init()
pygame.display.set_mode((450,800))
from pixelrush_profissional_v3108 import ArticulacaoFABRIK
# A produção já usa o lote; controle restaura a implementação anterior
# APENAS neste processo de benchmark. A física/prod não é modificada.
if not args.candidato:
    def deform_antigo(self,image,strip=4,target=None):
        width,height=image.get_size()
        pad=26
        tamanho=(width+2*pad,height)
        if target is None or target.get_size()!=tamanho:
            result=pygame.Surface(tamanho,pygame.SRCALPHA)
        else:
            result=target
            result.fill((0,0,0,0))
        for y in range(0,height,strip):
            dx=int(round(self.offset_at(y/max(1,height-1))))
            result.blit(image,(pad+dx,y),
                        pygame.Rect(0,y,width,min(strip,height-y)))
        return result,pad
    ArticulacaoFABRIK.deform=deform_antigo
from pixelrush_world_prod_v32777 import LivingWorld
biomes=("floresta","neve")
climates={"floresta":"vento_folhas","neve":"nevasca"}
timings={}
hashes={}
for biome in biomes:
    world=LivingWorld(biome,lightweight=False)
    measured=[]
    current=[]
    for frame in range(1,91):
        world.update(7.2 if frame<=45 else 20.0,.47,climates[biome],.47)
        dst=pygame.Surface((450,800),pygame.SRCALPHA if frame%2 else 0,32)
        dst.fill((23,53,89,(frame*13)%256) if frame%2 else (23,53,89))
        t=time.perf_counter_ns()
        world._animated_props(dst)
        if frame>15:measured.append((time.perf_counter_ns()-t)/1e6)
        current.append(hashlib.sha256(pygame.image.tobytes(dst,"RGBA")).hexdigest())
    hashes[biome]=current
    v=sorted(measured)
    timings[biome]={"p50_ms":round(statistics.median(v),5),
                    "p95_ms":round(v[int(.95*(len(v)-1))],5),
                    "mean_ms":round(statistics.mean(v),5),
                    "max_ms":round(max(v),5)}
    del world
report={"schema":"qa.r23.fabrik_batch.1","candidato":bool(args.candidato),
        "biomes":biomes,"frames_per_biome":90,"hashes_rgba":hashes,
        "timings":timings,
        "rss_peak_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "hardware_android_tested":False}
args.output.write_text(json.dumps(report,indent=2),encoding="utf8")
print(json.dumps({k:v for k,v in report.items() if k!="hashes_rgba"},ensure_ascii=False))
pygame.quit()
