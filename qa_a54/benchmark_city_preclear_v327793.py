# -*- coding: utf-8 -*-
"""QA793: perfil por passe da Cidade 2.5D, antes/depois de um fill redundante.

NÃO modifica produção nem salva dados; compara 130 quadros e 260 RGBA exatos.
Dois monkey-patches temporários: controle volta à rotina anterior, candidato
repete a rotina integrada. A diferença depende de medida, não de suposições.
"""
import argparse
import hashlib
import json
import os
import random
import statistics
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
os.environ["PIXELRUSH_QA_CITY_SCALED_BUDGET"]="1"
os.environ["PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW"]="1"
os.environ["PIXELRUSH_QA_CITY_TECH_COVER"]="1"
parser=argparse.ArgumentParser()
parser.add_argument("--candidato",type=int,choices=(0,1),required=True)
parser.add_argument("--direto",type=int,choices=(0,1),default=0)
parser.add_argument("--output",type=Path,required=True)
args=parser.parse_args()
import pygame
pygame.init()
pygame.display.set_mode((450,800))
from pixelrush_qa_city_bootstrap_v327759 import instalar as instalar_boot
from pixelrush_qa_city_scaled_budget_v327785 import instalar as instalar_budget
from pixelrush_qa_city_opaque_overdraw_v327786 import instalar as instalar_opaque
from pixelrush_qa_city_technical_cover_v327787 import instalar as instalar_tech
instalar_boot()
instalar_budget()
instalar_opaque()
instalar_tech()
if True:
    from pixelrush_world_v3130 import LivingWorld as _WorldBase,WIDTH,GROUND,TOP,MODULAR_BIOMES
    def superficie_sem_duplo_fill(self,kind="image",foreground_only=False):
        key=(kind,bool(foreground_only))
        surf=self._city_surfaces.get(key)
        if surf is None:
            surf=pygame.Surface((WIDTH,GROUND-TOP),pygame.SRCALPHA)
            self._city_surfaces[key]=surf
        # A Cidade limpa o destino em render_scene ANTES de cada layer.
        # Só pula o primeiro fill quando o renderer realmente o sobrescreve.
        if not args.candidato or self.biome!="cidade" or foreground_only:
            if kind=="normal":
                surf.fill((128,128,255))
            elif kind=="flow":
                surf.fill((128,128,0))
            else:
                surf.fill((0,0,0,0))
        if self.biome in MODULAR_BIOMES:
            self._get_modular().render_scene(
                surf,self.travel,self.frame,self.night,self.climate,self.phase,
                foreground_only=foreground_only,map_kind=kind)
        else:
            self.city2.render_scene(
                surf,self.travel,self.frame,self.night,self.climate,self.phase,
                foreground_only=foreground_only,map_kind=kind)
        return surf
    _WorldBase._city_surface=superficie_sem_duplo_fill

# Experimento 2: desenhar apenas flow diretamente na janela 450x500,
# sem o buffer intermediário de 900 KB nem o blit subsequente.
if args.direto:
    from pixelrush_world_v3130 import LivingWorld as _Base,WIDTH,GROUND,TOP
    # Normal direto foi 56% mais lento no benchmark; apenas fluxo entra no gate.
    _original_flow=_Base.draw_flow_map
    def _desenhar_direto(self,surface,kind,original):
        if (self.biome!='cidade' or surface.get_size()!=(450,800)
                or surface.get_colorkey() is not None
                or surface.get_alpha() not in (None,255)):
            return original(self,surface)
        # Somente mapas opacos: os demais canais dependem de alpha blend.
        area=surface.subsurface((0,TOP,WIDTH,GROUND-TOP))
        self.city2.render_scene(area,self.travel,self.frame,self.night,
                                self.climate,self.phase,False,map_kind=kind)
    def fluxo_direto(self,surface):
        return _desenhar_direto(self,surface,'flow',_original_flow)
    _Base.draw_flow_map=fluxo_direto
else:
    # Experimento A/B continua comparando contra a implementacao anterior.
    from pixelrush_world_v3130 import LivingWorld as _Base,MODULAR_BIOMES,TOP
    def fluxo_original(self,surface):
        if self.biome=='cidade' or self.biome in MODULAR_BIOMES:
            surface.blit(self._city_surface('flow'),(0,TOP))
        else:
            self._blit_strip(surface,self._load('flowmask'))
    _Base.draw_flow_map=fluxo_original

from pixelrush_world_prod_v32777 import LivingWorld
random.seed(20261105)
world=LivingWorld("cidade")
world.lightweight=False
assert world.city2._scaled_limit==20
passes=(("image",world.draw),
        ("fxmask",world.draw_effect_mask),
        ("normal",world.draw_normal_map),
        ("geometry",world.draw_geometry_map),
        ("material",world.draw_material_map),
        ("flow",world.draw_flow_map))
timings={kind:[] for kind,_ in passes}
hashes=[]
for frame in range(1,131):
    night=(0.,.45,.92)[(frame//35)%3]
    climate=("limpo","chuva","tempestade")[(frame//35)%3]
    world.update(36. if 75<=frame<=110 else 6.3,night,climate,.37)
    for kind,fn in passes[:1] if frame%5 else passes:
        surf=pygame.Surface((450,800),pygame.SRCALPHA if frame%2 else 0,32)
        surf.fill((19,38,79,(frame*7)%256) if frame%2 else (19,38,79))
        start=time.perf_counter_ns()
        fn(surf)
        if frame>15:
            timings[kind].append((time.perf_counter_ns()-start)/1e6)
        hashes.append(hashlib.sha256(pygame.image.tobytes(surf,"RGBA")).hexdigest())
def dados(values):
    v=sorted(values)
    return {"p50_ms":round(statistics.median(v),5),
            "p95_ms":round(v[int(.95*(len(v)-1))],5),
            "mean_ms":round(statistics.mean(v),5)}
report={"schema":"pixelrush.qa.r23.city.preclear.v327793",
        "candidato":bool(args.candidato),"direto":bool(args.direto),"frames":130,
        "rgba_count":len(hashes),"hashes_rgba":hashes,
        "per_pass":{k:dados(v) for k,v in timings.items()},
        "cache_max":len(world.city2._scaled),
        "quality":"completo","hardware_android":False}
assert report["rgba_count"]==260
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(report,indent=2),encoding="utf8")
print(json.dumps({k:v for k,v in report.items() if k!="hashes_rgba"},ensure_ascii=False))
pygame.quit()
