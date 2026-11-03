#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Benchmark manual QA752: custo CPU/RSS e paridade RGBA dos passes removidos.

Executar SOMENTE na homologacao offline futura. Nao mede GPU nem FPS Android,
nao compila APK/AAB, nao ativa scroll sem prova de custo end-to-end.
"""
import json
import os
import statistics
import sys
import time
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import pygame
import pixelrush_biomes2_v3128 as base
from pixelrush_biomes2_v3130 import ModularBiomeScene
from pixelrush_qa_audit_offline_v327744 import rss_mib


def summarize(samples):
    values=sorted(samples)
    if not values:
        return {'count':0}
    return {'count':len(values),
            'p50_ms':round(statistics.median(values)/1e6,5),
            'p95_ms':round(values[round(.95*(len(values)-1))]/1e6,5),
            'max_ms':round(values[-1]/1e6,5)}


def bench(biome):
    scene=ModularBiomeScene(biome)
    old=base._QA_SKIP_INERT_WEATHER
    orig=[];novo=[];same=0
    try:
        for f in range(72):
            frame=f*5
            climate=('limpo','vento','nevasca' if biome=='neve' else 'tempestade_areia',
                     'limpo')[f%4]
            night=(.0,.24,.57,.9)[f%4]
            travel=frame*4.17
            a=pygame.Surface((450,500),pygame.SRCALPHA)
            b=a.copy()
            base._QA_SKIP_INERT_WEATHER=False
            tic=time.process_time_ns()
            scene.render_scene(a,travel,frame,night,climate,.5)
            orig.append(time.process_time_ns()-tic)
            base._QA_SKIP_INERT_WEATHER=True
            tic=time.process_time_ns()
            scene.render_scene(b,travel,frame,night,climate,.5)
            novo.append(time.process_time_ns()-tic)
            if pygame.image.tobytes(a,'RGBA')!=pygame.image.tobytes(b,'RGBA'):
                raise AssertionError(('rgba',biome,f,frame,climate))
            same+=1
        return {'bioma':biome,'quadros_rgba_identicos':same,
                'cpu_referencia':summarize(orig),'cpu_sem_overlay_vazio':summarize(novo)}
    finally:
        base._QA_SKIP_INERT_WEATHER=old


def daylight_bytes(biome):
    scene=ModularBiomeScene(biome)
    scene._pose=0;scene._night_level=0
    count=0
    aliased=0
    if biome=='neve':
        for layer,tiles in scene._poses[0].items():
            for i,src in enumerate(tiles):
                count+=1
                aliased+=int(scene._night_tiles[(0,layer,i,0)] is src)
    else:
        import pixelrush_biomes2_v3130 as mod
        for layer,tiles in scene._poses[0].items():
            for i,src in enumerate(tiles):
                count+=1
                texture=scene._tile_map(layer,i,'image')
                aliased+=int(texture is src)
    # Referencia logica antiga: uma Surface 225x250x4 por tile.
    return {'bioma':biome,'tiles_dia':count,'aliases_identicos':aliased,
            'bytes_logicos_copia_omitida':aliased*225*250*4,
            'ressalva':'nao corresponde a economia real de RSS do SO'}


def main():
    pygame.init()
    pygame.display.set_mode((450,800))
    start=rss_mib()
    result={'schema':'pixelrush.qa.render_memory.v327752',
            'versao':'v3.277.52-QA',
            'pygame_ce':pygame.version.ver,
            'neve':bench('neve'),
            'deserto':bench('deserto'),
            'atlas_diurno':[daylight_bytes('neve'),daylight_bytes('deserto')],
            'rss_inicial_mib':start,
            'rss_final_mib':rss_mib(),
            'homologacao_final':False,
            'android_testado':False,
            'fps_android_comprovado':False,
            'gpu_real_testada':False,
            'apk_compilado':False,'aab_compilado':False}
    assert result['neve']['quadros_rgba_identicos']==72
    assert result['deserto']['quadros_rgba_identicos']==72
    target=ROOT/'qa-benchmark-render-memory-v327752.json'
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
    pygame.quit()


if __name__=='__main__':
    main()
