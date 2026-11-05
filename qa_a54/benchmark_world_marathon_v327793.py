# -*- coding: utf-8 -*-
"""R23: QA pygame-ce 140 quadros reais, sete biomas, gráficos completos e RSS."""
import hashlib,json,os,resource,statistics,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
pygame.init()
pygame.display.set_mode((450,800))
# Cidade v3122 contorna o init v3118; usar os metadados da rota real R17.
from pixelrush_qa_city_bootstrap_v327759 import instalar as _boot_cidade
from pixelrush_qa_city_scaled_budget_v327785 import instalar as _budget
from pixelrush_qa_city_opaque_overdraw_v327786 import instalar as _opaque
from pixelrush_qa_city_technical_cover_v327787 import instalar as _tech
os.environ['PIXELRUSH_QA_CITY_SCALED_BUDGET']='1'
os.environ['PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW']='1'
os.environ['PIXELRUSH_QA_CITY_TECH_COVER']='1'
_boot_cidade()
_budget()
_opaque()
_tech()
from pixelrush_world_prod_v32777 import LivingWorld
BIOMAS=('cidade','neve','deserto','vulcao','floresta','cidade_futurista','ilhas_celestes')
CLIMAS=('limpo','nevasca','tempestade_areia','cinzas','vento_folhas','chuva_acida','brisa_celeste')
world=LivingWorld('cidade',lightweight=False)
report={}
for biome,clima in zip(BIOMAS,CLIMAS):
    if world.biome!=biome:world.switch(biome)
    world.lightweight=False
    tempos={k:[] for k in ('image','fxmask','normal','material','flow','geometry')}
    hashes=[]
    for frame in range(1,21):
        night=(0.,.45,.91)[(frame//8)%3]
        world.update(6.4 if frame<12 else 14.2,night,clima,.47)
        passes=(('image',world.draw),)
        if frame%5==0:
            passes+=(('fxmask',world.draw_effect_mask),
                     ('normal',world.draw_normal_map),
                     ('material',world.draw_material_map),
                     ('flow',world.draw_flow_map),
                     ('geometry',world.draw_geometry_map))
        for kind,draw in passes:
            dst=pygame.Surface((450,800),pygame.SRCALPHA if frame%2 else 0,32)
            dst.fill((22,38,80,(frame*11)%256) if frame%2 else (22,38,80))
            start=time.perf_counter_ns()
            draw(dst)
            if frame>5:tempos[kind].append((time.perf_counter_ns()-start)/1e6)
            hashes.append(hashlib.sha256(pygame.image.tobytes(dst,'RGBA')).hexdigest())
    assert not world.lightweight
    assert len(hashes)==40,(biome,len(hashes))
    assert len(set(hashes))>=12,(biome,'sem movimento')
    report[biome]={
        'rgba_count':len(hashes),'unique_rgba':len(set(hashes)),
        'timings':{kind:{'p50_ms':round(statistics.median(v),4),
                         'p95_ms':round(sorted(v)[int(.95*(len(v)-1))],4),
                         'max_ms':round(max(v),4)}
                   for kind,v in tempos.items() if v},
        'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
out={'schema':'qa.r23.marathon.v327793','quality':'completo',
     'hardware_android_tested':False,'frames_total':140,
     'rgba_total':sum(v['rgba_count'] for v in report.values()),
     'fifth_period':5,'biomes':report}
assert out['rgba_total']==280
(ROOT/'qa_a54/qa793_seven_biomes.json').write_text(
    json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
pygame.quit()
