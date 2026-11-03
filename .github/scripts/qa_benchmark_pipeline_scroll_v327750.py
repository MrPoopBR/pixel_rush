#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Medição offline PREPARADA para v3.277.50 — executar manualmente depois.

CPU + RSS + RGBA de chunks Cidade 2.5D, scroll incremental, pipeline CPU,
e geometria real; nunca confundir com FPS/GPU Android do jogo inteiro.
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
import pixelrush_qa_incremental_scene_v327750 as scroll_qa
from pixelrush_qa_unified_post_v327750 import diagnostico as diagnostico_pipeline


def resumo(samples):
    if not samples:return {'amostras':0}
    samples=sorted(samples)
    return {'amostras':len(samples),
            'p50_ms':round(statistics.median(samples)/1e6,5),
            'p95_ms':round(samples[round((len(samples)-1)*.95)]/1e6,5),
            'max_ms':round(samples[-1]/1e6,5)}


def bench_cidade():
    scene=CityPilotScene()
    no_sprite=[v for layer in scene.layers for v in layer.variants if not v.sprites]
    if not no_sprite:raise RuntimeError('sem chunk estatico para ensaio')
    variant=no_sprite[0]
    original=CityPilotScene._render_chunk
    a=pygame.Surface((450,500),pygame.SRCALPHA)
    b=a.copy()
    raw=[];inc=[];pixels=0
    prev=os.environ.get('PIXELRUSH_QA_CITY_INCREMENTAL')
    try:
        os.environ['PIXELRUSH_QA_CITY_INCREMENTAL']='1'
        scroll_qa.instalar()
        for k in range(145):
            x=-210-k*2
            a.fill((17,33,59,140))
            b.fill((17,33,59,140))
            begin=time.process_time_ns()
            original(scene,a,variant,False,x,k,.5,'limpo',.5,'image')
            raw.append(time.process_time_ns()-begin)
            begin=time.process_time_ns()
            scene._render_chunk(b,variant,False,x,k,.5,'limpo',.5,'image')
            inc.append(time.process_time_ns()-begin)
            if pygame.image.tobytes(a,'RGBA')!=pygame.image.tobytes(b,'RGBA'):
                raise AssertionError(('chunk_rgba',k,x))
            pixels+=1
        return {'rgba_idênticos':pixels,'baseline':resumo(raw),
                'incremental':resumo(inc),'status':scroll_qa.diagnostico()}
    finally:
        scroll_qa.restaurar_para_teste()
        if prev is None:os.environ.pop('PIXELRUSH_QA_CITY_INCREMENTAL',None)
        else:os.environ['PIXELRUSH_QA_CITY_INCREMENTAL']=prev


def bench_geometria():
    scene=CityPilotScene()
    times=[]
    identities=set()
    target=pygame.Surface((450,500),pygame.SRCALPHA)
    for k in range(35):
        t=time.process_time_ns()
        scene.render_scene(target,k*7.3,k,.32,'limpo',.5,
                           map_kind='geometry')
        times.append(time.process_time_ns()-t)
        identities.add(id(scene._geometry_view))
        if pygame.image.tobytes(target,'RGBA')!=pygame.image.tobytes(scene._geometry_view,'RGBA'):
            raise AssertionError(('geometry_copy',k))
    return {'rgba_idênticos':35,'buffers_unicos':len(identities),
            'cpu':resumo(times)}


def main():
    pygame.init()
    pygame.display.set_mode((450,800))
    before=rss_mib()
    result={'schema':'pixelrush.qa.pipeline_scroll.v327750',
            'versao':'v3.277.50-QA','pygame_ce':pygame.version.ver,
            'rss_antes_mib':before,
            'cidade_incremental':bench_cidade(),
            'geometria_reuso':bench_geometria(),
            'pipeline':diagnostico_pipeline(),
            'rss_depois_mib':rss_mib(),
            'loop_completo_do_jogo':False,
            'homologacao_android':False,
            'ganho_fps_android_comprovado':False,
            'apk_compilado':False,'aab_compilado':False,
            'teste_gpu_fisico':False}
    destino=ROOT/'qa-benchmark-pipeline-scroll-v327750.json'
    destino.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    pygame.quit()


if __name__=='__main__':
    main()
