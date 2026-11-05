# -*- coding: utf-8 -*-
"""QA793 LAB: percurso real da Cidade com 5 canais tecnicos por 5o quadro.
Executar separadamente em processo fresco para comparar baseline/candidato.
Nao altera saves, jogador, fisica, RNG do gameplay ou arte do jogo.
"""
import argparse,collections,hashlib,json,os,random,resource,statistics,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
p=argparse.ArgumentParser()
p.add_argument('--limit',type=int,choices=(14,20),required=True)
p.add_argument('--light',type=int,choices=(0,1),default=0)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--opaque',type=int,choices=(0,1),required=True)
p.add_argument('--tech',type=int,choices=(0,1),required=True)
p.add_argument('--skip-train',type=int,choices=(0,1),default=0)
p.add_argument('--skip-layers',type=int,choices=(0,1),default=0)
args=p.parse_args()
os.environ['PIXELRUSH_QA_R26_SKIP_OCCLUDED_LAYERS']=str(args.skip_layers)
os.environ['PIXELRUSH_QA_SKIP_HIDDEN_TRAIN']=str(args.skip_train)
os.environ['PIXELRUSH_QA_CITY_SCALED_BUDGET']='1' if args.limit==20 else '0'
os.environ['PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW']=str(args.opaque)
os.environ['PIXELRUSH_QA_CITY_TECH_COVER']=str(args.tech)
import pygame
pygame.init()
pygame.display.set_mode((450,800))
from pixelrush_qa_city_bootstrap_v327759 import instalar as boot
boot()
from pixelrush_qa_city_scaled_budget_v327785 import instalar as budget
budget()
from pixelrush_qa_city_opaque_overdraw_v327786 import instalar as instalar_opaque,diagnostico as diagnostico_opaque
instalar_opaque()
from pixelrush_qa_city_technical_cover_v327787 import instalar as instalar_tech,diagnostico as diag_tech
instalar_tech()
from pixelrush_city2_v3125 import CityPilotScene
from pixelrush_world_v3130 import LivingWorld
random.seed(20261105)
world=LivingWorld('cidade')
world.lightweight=bool(args.light)
assert world.city2._scaled_limit==args.limit
old_train=CityPilotScene._draw_train
train_calls=collections.Counter()
def contar_train(self,target,travel,frame,night,map_kind='image'):
    train_calls[map_kind]+=1
    return old_train(self,target,travel,frame,night,map_kind)
CityPilotScene._draw_train=contar_train
old_layer_tiles=CityPilotScene._layer_tiles
layer_calls=collections.Counter()
def contar_camadas(travel,layer):
    layer_calls[layer.name]+=1
    return old_layer_tiles(travel,layer)
CityPilotScene._layer_tiles=staticmethod(contar_camadas)
old=CityPilotScene._scaled_surface
stats=collections.defaultdict(collections.Counter)

def observar(self,variant,kind):
    key=(id(variant),kind)
    alias=self._qa_scaled_alias.get(key)
    if alias is not None and id(getattr(variant,kind))==alias[0]:
        key=alias[1]
    stats[kind]['hit' if key in self._scaled else 'miss']+=1
    return old(self,variant,kind)

CityPilotScene._scaled_surface=observar
times=collections.defaultdict(list)
hashes=[]
cached_max=0
for frame in range(1,131):
    night=(0.,.45,.92)[(frame//35)%3]
    climate=('limpo','chuva','tempestade')[(frame//35)%3]
    speed=36. if 75<=frame<=110 else 6.3
    world.update(speed,night,climate,.37)
    img=pygame.Surface((450,800),pygame.SRCALPHA if frame%2 else 0,32)
    img.fill((19,38,79,(frame*7)%256) if frame%2 else (19,38,79))
    t=time.perf_counter_ns()
    world.draw(img)
    image_ms=(time.perf_counter_ns()-t)/1e6
    times['image'].append(image_ms)
    hashes.append(hashlib.sha256(pygame.image.tobytes(img,'RGBA')).hexdigest())
    if frame%5==0:
        complete_ms=image_ms
        passes=(('fxmask',world.draw_effect_mask),
                ('normal',world.draw_normal_map),
                ('geometry',world.draw_geometry_map),
                ('material',world.draw_material_map),
                ('flow',world.draw_flow_map))
        for name,fn in passes:
            surf=pygame.Surface((450,800),pygame.SRCALPHA,32)
            surf.fill((113,57,193,0))
            t=time.perf_counter_ns()
            fn(surf)
            elapsed=(time.perf_counter_ns()-t)/1e6
            times[name].append(elapsed)
            complete_ms+=elapsed
            hashes.append(hashlib.sha256(pygame.image.tobytes(surf,'RGBA')).hexdigest())
        times['fifth_total'].append(complete_ms)
    cached_max=max(cached_max,len(world.city2._scaled))
def metrics(v):
    warm=v[3:] if len(v)>10 else v[2:]
    ordered=sorted(warm)
    return {'p50_ms':round(statistics.median(warm),4),
            'p95_ms':round(ordered[int(.95*(len(ordered)-1))],4),
            'mean_ms':round(statistics.mean(warm),4)}
result={
    'schema':'pixelrush.qa.r17.city_technical.v327787',
    'base':'LivingWorld+CityPilotScene v3125; 130 quadros, 26 quintos',
    'hardware_android_testado':False,
    'limit':args.limit,'light':bool(args.light),'opaque':bool(args.opaque),
    'tech':bool(args.tech),'tech_stats':diag_tech(),
    'opaque_stats':diagnostico_opaque(),
    'hashes_rgba':hashes,'quadros_rgba':len(hashes),
    'counters':{name:dict(c) for name,c in stats.items()},
    'timings':{k:metrics(v) for k,v in times.items()},
    'cache_maximo_observado':cached_max,
    'memoria_rss_pico_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    'periodo_redesenho_preservado':5,
    'train_calls':dict(train_calls),
    'layer_calls':dict(layer_calls),
    'skip_layers':bool(args.skip_layers),
    'skip_hidden_train':bool(args.skip_train),
}
assert len(hashes)==260, len(hashes)
assert cached_max<=args.limit
args.output.write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='hashes_rgba'},
                 ensure_ascii=False,sort_keys=True))
pygame.quit()
