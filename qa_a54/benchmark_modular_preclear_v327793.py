# -*- coding: utf-8 -*-
"""QA793: teste do fill redundante nos biomas modulares, sem alterar produção.

Compara controle x candidato em dois processos Python idênticos.
Registra hashes RGBA (inclusive RGB oculto), p50/p95 por bioma e passe,
máxima RAM RSS; não aprova otimização sem igualdade bit a bit.
"""
import argparse
import hashlib
import json
import os
import random
import resource
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
p=argparse.ArgumentParser()
p.add_argument("--candidato",type=int,choices=(0,1,2,3),required=True)
p.add_argument("--output",type=Path,required=True)
args=p.parse_args()
import pygame
pygame.init()
pygame.display.set_mode((450,800))
from pixelrush_world_v3130 import LivingWorld as Base, WIDTH, TOP, GROUND, MODULAR_BIOMES
def superficie(self,kind="image",foreground_only=False):
    key=(kind,bool(foreground_only))
    surf=self._city_surfaces.get(key)
    if surf is None:
        surf=pygame.Surface((WIDTH,GROUND-TOP),pygame.SRCALPHA)
        self._city_surfaces[key]=surf
    # 0=controle com fill, 1=normal integrado QA793, 2=LAB todos os passes.
    # render_scene modular usa scale(low,(450,500),target), regravando todo destino.
    # Os demais mapas conservam seus fills para evitar regressao em outros passes.
    clear=(not args.candidato or self.biome not in MODULAR_BIOMES or foreground_only
           or (args.candidato==1 and kind!='normal'))
    if clear:
        if kind=="normal":surf.fill((128,128,255))
        elif kind=="flow":surf.fill((128,128,0))
        else:surf.fill((0,0,0,0))
    if self.biome in MODULAR_BIOMES:
        self._get_modular().render_scene(
            surf,self.travel,self.frame,self.night,self.climate,self.phase,
            foreground_only=foreground_only,map_kind=kind)
    else:
        self.city2.render_scene(
            surf,self.travel,self.frame,self.night,self.climate,self.phase,
            foreground_only=foreground_only,map_kind=kind)
    return surf
if args.candidato!=3:
    # Modo 3 exercita o codigo integrado de producao (sem monkeypatch).
    Base._city_surface=superficie
from pixelrush_world_prod_v32777 import LivingWorld
random.seed(20261105)
BIOMES=("neve","deserto")
assert all(b in MODULAR_BIOMES for b in BIOMES),MODULAR_BIOMES
frames=40
hashes={}
samples=defaultdict(list)
resident={}
for biome in BIOMES:
    world=LivingWorld(biome,lightweight=False)
    for frame in range(1,frames+1):
        night=(.0,.45,.93)[(frame//14)%3]
        climate=(("neve","nevasca","limpo") if biome=="neve"
                 else ("areia","tempestade_areia","limpo"))[(frame//14)%3]
        world.update(6.1 if frame<=24 else 25.0,night,climate,.47)
        targets=(("image",world.draw),)
        if frame%5==0:
            targets+=(("fxmask",world.draw_effect_mask),
                      ("normal",world.draw_normal_map),
                      ("geometry",world.draw_geometry_map),
                      ("material",world.draw_material_map),
                      ("flow",world.draw_flow_map))
        for kind,draw in targets:
            target=pygame.Surface((450,800),pygame.SRCALPHA if frame%2 else 0,32)
            target.fill((23,37,85,(frame*11)%256) if frame%2 else (23,37,85))
            t=time.perf_counter_ns()
            draw(target)
            if frame>6:
                samples[(biome,kind)].append((time.perf_counter_ns()-t)/1e6)
            hashes["%s:%03d:%s"%(biome,frame,kind)]=hashlib.sha256(
                pygame.image.tobytes(target,"RGBA")).hexdigest()
    resident[biome]=sorted(str(x) for x in world._city_surfaces)
    del world
def stats(a):
    v=sorted(a)
    return {"p50_ms":round(statistics.median(v),5),
            "p95_ms":round(v[int(.95*(len(v)-1))],5),
            "mean_ms":round(statistics.mean(v),5)}
report={"schema":"pixelrush.qa.r23.modular_preclear.1",
        "biomes":BIOMES,"frames_per_biome":frames,
        "candidato":bool(args.candidato),"rgba_hashes":hashes,
        "per_pass":{"%s/%s"%key:stats(v) for key,v in samples.items()},
        "resident_buffers":resident,
        "rss_peak_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "quality":"completo","android_hardware_tested":False}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf8")
print(json.dumps({k:v for k,v in report.items() if k!="rgba_hashes"},ensure_ascii=False))
pygame.quit()
