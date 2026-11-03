#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA751 — medir CPU/RSS das passagens removidas, apenas quando manualmente executado.

A comparação é no caminho real CityPilotScene v3125; nao extrapolar
para FPS, GPU, temperatura ou desempenho Android sem teste no aparelho.
"""
import json,os,statistics,sys,time
from pathlib import Path
from collections import OrderedDict
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import pygame
from pixelrush_qa_audit_offline_v327744 import rss_mib
from pixelrush_city2_v3125 import CityPilotScene
import pixelrush_city2_v3124 as city
import pixelrush_city2_v3118 as base


def stat(vals):
    x=sorted(vals)
    return {'frames':len(x),'p50_ms':round(statistics.median(x)/1e6,5),
            'p95_ms':round(x[round((len(x)-1)*.95)]/1e6,5),
            'max_ms':round(x[-1]/1e6,5)}


def pixels(s):
    return pygame.image.tobytes(s,'RGBA')


def cena_noturna():
    scene=CityPilotScene()
    entrada=pygame.Surface((450,500),pygame.SRCALPHA)
    antigo=[];otimizado=[];verificados=0
    original=city._QA_DIRECT_NIGHT_MULT
    try:
        for i in range(60):
            frame=i*9
            travel=139.5+i*5.6
            night=(.21,.36,.54,.75,.93)[i%5]
            clima=('limpo','chuva','tempestade')[i%3]
            a=entrada.copy();b=entrada.copy()
            a.fill((26,41,82,178));b.fill((26,41,82,178))
            city._QA_DIRECT_NIGHT_MULT=False
            t=time.process_time_ns()
            scene.render_scene(a,travel,frame,night,clima,.6)
            antigo.append(time.process_time_ns()-t)
            city._QA_DIRECT_NIGHT_MULT=True
            t=time.process_time_ns()
            scene.render_scene(b,travel,frame,night,clima,.6)
            otimizado.append(time.process_time_ns()-t)
            if pixels(a)!=pixels(b):
                raise AssertionError(('cidade_noite_rgba',i))
            verificados+=1
        memoria_veils=len(scene._night_veils)*450*500*4
        return {'frames_rgba_identicos':verificados,
                'referencia_cpu':stat(antigo),
                'com_fill_cpu':stat(otimizado),
                'superficies_veils_no_legado':len(scene._night_veils),
                'bytes_potencialmente_omitidos':memoria_veils,
                'passagem_RGBA_mult_removida':True}
    finally:
        city._QA_DIRECT_NIGHT_MULT=original


def chunks_com_sprite():
    scene=CityPilotScene()
    src=next(v for layer in scene.layers for v in layer.variants if v.sprites)
    original=base._QA_NATIVE_CLIP
    a=pygame.Surface((450,500),pygame.SRCALPHA)
    antigo=[];otimizado=[];checks=0
    try:
        for i in range(120):
            x=-325+i*2
            a.fill((13,24,52,159))
            b=a.copy()
            base._QA_NATIVE_CLIP=False
            t=time.process_time_ns()
            scene._render_chunk(a,src,False,x,i,.63,'vento',.4)
            antigo.append(time.process_time_ns()-t)
            base._QA_NATIVE_CLIP=True
            t=time.process_time_ns()
            scene._render_chunk(b,src,False,x,i,.63,'vento',.4)
            otimizado.append(time.process_time_ns()-t)
            if pixels(a)!=pixels(b):
                raise AssertionError(('chunk_clip_rgba',i,x))
            checks+=1
    finally:
        base._QA_NATIVE_CLIP=original
    return {'casos_rgba_identicos':checks,'referencia_cpu':stat(antigo),
            'clip_SDL_cpu':stat(otimizado)}


def main():
    pygame.init()
    pygame.display.set_mode((450,800))
    before=rss_mib()
    data={'schema':'pixelrush.qa.hotpath.v327751',
          'versao':'v3.277.51-QA','pygame_ce':pygame.version.ver,
          'rss_antes_mib':before,
          'cidade_noite':cena_noturna(),
          'cidade_chunks':chunks_com_sprite(),
          'rss_depois_mib':rss_mib(),
          'renderer_android_homologado':False,
          'fps_android_comprovado':False,
          'bench_loop_completo':False,
          'APK_compilado':False,'AAB_compilado':False}
    assert data['cidade_noite']['frames_rgba_identicos']==60
    assert data['cidade_chunks']['casos_rgba_identicos']==120
    (ROOT/'qa-benchmark-hotpath-v327751.json').write_text(
        json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(data,ensure_ascii=False,indent=2))
    pygame.quit()

if __name__=='__main__':
    main()
