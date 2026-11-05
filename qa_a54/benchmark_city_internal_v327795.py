# -*- coding: utf-8 -*-
"""R25: perfil do quinto quadro do render REAL Cidade, sem alterar o motor.

Mede API Python/SDL por chamada, cache de scale e 240 hashes RGBA em
120 quadros completos, cinco mapas por quinto quadro, sem reduzir qualidade.
Nao extrapolar p50 Linux para o A54/MEmu.
"""
import collections,hashlib,json,os,random,resource,statistics,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ['PIXELRUSH_QA_CITY_SCALED_BUDGET']='1'
os.environ['PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW']='1'
os.environ['PIXELRUSH_QA_CITY_TECH_COVER']='1'
import pygame
pygame.init()
pygame.display.set_mode((450,800))
from pixelrush_qa_city_bootstrap_v327759 import instalar as boot
boot()
from pixelrush_qa_city_scaled_budget_v327785 import instalar as budget
budget()
from pixelrush_qa_city_opaque_overdraw_v327786 import instalar as opaque
opaque()
from pixelrush_qa_city_technical_cover_v327787 import instalar as technical
technical()
from pixelrush_city2_v3125 import CityPilotScene
from pixelrush_world_v3130 import LivingWorld
random.seed(20261105)
world=LivingWorld('cidade')
world.lightweight=False
assert world.city2._scaled_limit==20
timings=collections.defaultdict(list)
counts=collections.Counter()
cache=collections.Counter()
def metric(name,func,kind_position,default):
    def wrapped(*args,**kwargs):
        kind=(args[kind_position] if len(args)>kind_position
              else kwargs.get('map_kind',kwargs.get('kind',default)))
        if kind is None:kind=default
        if name=='scale':
            key=(id(args[1]),kind)
            alias=args[0]._qa_scaled_alias.get(key)
            if alias is not None and id(getattr(args[1],kind))==alias[0]:
                key=alias[1]
            cache[(kind,'hit' if key in args[0]._scaled else 'miss')]+=1
        t=time.perf_counter_ns()
        result=func(*args,**kwargs)
        timings[f'{name}/{kind}'].append((time.perf_counter_ns()-t)/1e6)
        counts[f'{name}/{kind}']+=1
        return result
    return wrapped
for name,position,default in [
    ('render',8,'image'),('chunk',9,'image'),
    ('sprite',7,'image'),('scale',2,'image')]:
    attr={'render':'render_scene','chunk':'_render_chunk',
          'sprite':'_draw_sprite','scale':'_scaled_surface'}[name]
    setattr(CityPilotScene,attr,metric(name,getattr(CityPilotScene,attr),position,default))
all_pass=collections.defaultdict(list)
hashes=[]
for f in range(1,121):
    night=(0.,.47,.94)[(f//40)%3]
    climate=('limpo','chuva','tempestade')[(f//40)%3]
    speed=36. if 75<=f<=110 else 6.3
    world.update(speed,night,climate,.37)
    actions=(('image',world.draw),)
    if f%5==0:
        actions+=(('fxmask',world.draw_effect_mask),('normal',world.draw_normal_map),
                  ('geometry',world.draw_geometry_map),('material',world.draw_material_map),
                  ('flow',world.draw_flow_map))
    total=0
    for kind,fn in actions:
        surface=pygame.Surface((450,800),pygame.SRCALPHA if f%2 else 0,32)
        surface.fill((16,41,91,(f*7)%256) if f%2 else (16,41,91))
        t=time.perf_counter_ns()
        fn(surface)
        duration=(time.perf_counter_ns()-t)/1e6
        total+=duration
        all_pass[kind].append(duration)
        hashes.append(hashlib.sha256(pygame.image.tobytes(surface,'RGBA')).hexdigest())
    if f%5==0:all_pass['fifth_total'].append(total)
assert len(hashes)==240
def stat(v):
    a=sorted(v[3:] if len(v)>12 else v)
    return {'n':len(v),'p50_ms':round(statistics.median(a),5),
            'p95_ms':round(a[int(.95*(len(a)-1))],5),
            'total_ms':round(sum(v),4)}
report={'schema':'qa.r25.city_internal.v327795',
        'frames':120,'fifth_period':5,'rgba_samples':len(hashes),
        'rgba_hashes':hashes,'per_pass':{k:stat(v) for k,v in all_pass.items()},
        'internals':{k:stat(v) for k,v in timings.items()},
        'calls':dict(counts),
        'scale_cache':{f'{k}/{state}':n for (k,state),n in cache.items()},
        'scale_peak':len(world.city2._scaled),
        'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'android_hardware_tested':False,'quality':'completo'}
assert report['scale_peak']<=20
out=ROOT/'qa_a54/qa795_city_internal.json'
out.write_text(json.dumps(report,indent=2),encoding='utf8')
print('QA795 City per-pass',report['per_pass'])
print('QA795 City internal',report['internals'])
print('QA795 City scale cache',report['scale_cache'])
pygame.quit()
