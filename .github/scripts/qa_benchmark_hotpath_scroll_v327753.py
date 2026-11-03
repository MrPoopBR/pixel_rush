#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA753 benchmark MANUAL de CPU/RSS quinto quadro + scroll 2.5D real.

Quando executar posteriormente: SDL dummy e Pygame-ce 2.5.8, compara RGBA
pixel por pixel, mede CPU p50/p95/max e RSS. NÃO substitui teste Android
de jogo completo, GPU, VSync ou Perfetto; sem compilar APK/AAB.
"""
import json
import os
import statistics
import sys
import time
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import pygame
from pixelrush_city2_v3125 import CityPilotScene
from pixelrush_world_v3130 import LivingWorld
from pixelrush_qa_audit_offline_v327744 import rss_mib
import pixelrush_qa_hotpath_v327753 as hot
import pixelrush_qa_incremental_scene_v327750 as scroll


def stat(values):
    data=sorted(values)
    if not data:return {'n':0}
    return {'n':len(data),
            'p50_ms':round(statistics.median(data)/1e6,5),
            'p95_ms':round(data[round((len(data)-1)*.95)]/1e6,5),
            'max_ms':round(data[-1]/1e6,5)}


def rgba(s):
    return pygame.image.tobytes(s,'RGBA')


def cidade_foreground():
    hot.restaurar_para_teste()
    previous=os.environ.get('PIXELRUSH_QA_CITY_EMPTY_FG')
    os.environ['PIXELRUSH_QA_CITY_EMPTY_FG']='1'
    old=CityPilotScene.render_scene
    baseline=[];optimized=[];verified=0
    try:
        hot.instalar()
        scene=CityPilotScene()
        a=pygame.Surface((450,500),pygame.SRCALPHA)
        b=a.copy()
        # Aquecer assets da referencia antes de iniciar medições.
        old(scene,a,30.2,12,.1,'limpo',.5,True,'image')
        for i in range(140):
            frame=i+20
            travel=frame*4.71
            n=(.0,.48,.91)[i%3]
            a.fill((35,71,120,99))
            b.fill((35,71,120,99))
            t=time.process_time_ns()
            old(scene,a,travel,frame,n,'chuva',.55,True,'image')
            baseline.append(time.process_time_ns()-t)
            t=time.process_time_ns()
            scene.render_scene(b,travel,frame,n,'chuva',.55,True,'image')
            optimized.append(time.process_time_ns()-t)
            if rgba(a)!=rgba(b):
                raise AssertionError(('foreground_rgba',i))
            verified+=1
        return {'rgba_identicos':verified,'original':stat(baseline),
                'qa753':stat(optimized),'diag':hot.diagnostico()}
    finally:
        hot.restaurar_para_teste()
        if previous is None:os.environ.pop('PIXELRUSH_QA_CITY_EMPTY_FG',None)
        else:os.environ['PIXELRUSH_QA_CITY_EMPTY_FG']=previous


def strips():
    old=LivingWorld._blit_strip
    hot.restaurar_para_teste()
    prev=os.environ.get('PIXELRUSH_QA_STRIP_ONE_BLIT')
    prev_fg=os.environ.get('PIXELRUSH_QA_CITY_EMPTY_FG')
    os.environ['PIXELRUSH_QA_CITY_EMPTY_FG']='0'
    os.environ['PIXELRUSH_QA_STRIP_ONE_BLIT']='1'
    old_samples=[];new_samples=[];verified=0
    try:
        hot.instalar()
        texture=pygame.Surface((900,500),pygame.SRCALPHA)
        texture.fill((90,120,220,212))
        for j in range(20):
            pygame.draw.rect(texture,(j*11%256,170,90,140),
                             (j*34,100+j*5,48,85))
        for i in range(120):
            off=(i*11)%900
            fake=SimpleNamespace(_scroll=lambda x=off:x)
            a=pygame.Surface((450,800),pygame.SRCALPHA)
            a.fill((39,51,78,101))
            b=a.copy()
            t=time.process_time_ns()
            old(fake,a,texture)
            old_samples.append(time.process_time_ns()-t)
            t=time.process_time_ns()
            LivingWorld._blit_strip(fake,b,texture)
            new_samples.append(time.process_time_ns()-t)
            if rgba(a)!=rgba(b):raise AssertionError(('strip_rgba',i,off))
            verified+=1
        return {'rgba_identicos':verified,'original':stat(old_samples),
                'qa753':stat(new_samples),'diag':hot.diagnostico()}
    finally:
        hot.restaurar_para_teste()
        if prev is None:os.environ.pop('PIXELRUSH_QA_STRIP_ONE_BLIT',None)
        else:os.environ['PIXELRUSH_QA_STRIP_ONE_BLIT']=prev
        if prev_fg is None:os.environ.pop('PIXELRUSH_QA_CITY_EMPTY_FG',None)
        else:os.environ['PIXELRUSH_QA_CITY_EMPTY_FG']=prev_fg


def scroll_estatico():
    scroll.restaurar_para_teste()
    prev={key:os.environ.get(key) for key in
          ('PIXELRUSH_QA_CITY_INCREMENTAL','PIXELRUSH_QA_CITY_SCROLL_SCOPE',
           'PIXELRUSH_QA_CLASSIC_INCREMENTAL')}
    os.environ.update(PIXELRUSH_QA_CITY_INCREMENTAL='1',
                      PIXELRUSH_QA_CITY_SCROLL_SCOPE='static',
                      PIXELRUSH_QA_CLASSIC_INCREMENTAL='0')
    old=CityPilotScene._render_chunk
    original_samples=[];new_samples=[];verified=0
    try:
        scroll.instalar()
        scene=CityPilotScene()
        far=scene.layers[0].variants[0]
        mid=scene.layers[1].variants[0]
        for frame in range(120):
            x=-500-frame*2
            for variant in (far,mid):
                a=pygame.Surface((450,500),pygame.SRCALPHA)
                a.fill((12,23,47,110))
                b=a.copy()
                t=time.process_time_ns()
                old(scene,a,variant,False,x,frame,.44,'limpo',.53,'image')
                original_samples.append(time.process_time_ns()-t)
                t=time.process_time_ns()
                scene._render_chunk(b,variant,False,x,frame,.44,'limpo',.53,'image')
                new_samples.append(time.process_time_ns()-t)
                if rgba(a)!=rgba(b):raise AssertionError(('scroll_rgba',frame))
                verified+=1
        return {'rgba_identicos':verified,'original':stat(original_samples),
                'qa753':stat(new_samples),'diag':scroll.diagnostico()}
    finally:
        scroll.restaurar_para_teste()
        for key,val in prev.items():
            if val is None:os.environ.pop(key,None)
            else:os.environ[key]=val


def main():
    pygame.init()
    pygame.display.set_mode((450,800))
    before=rss_mib()
    report={'schema':'pixelrush.qa.hotpath_scroll.v327753',
            'versao':'v3.277.53-QA','pygame_ce':pygame.version.ver,
            'rss_inicial_mib':before,
            'foreground_cidade':cidade_foreground(),
            'strips_classicos':strips(),
            'scroll_estatico':scroll_estatico(),
            'rss_final_mib':rss_mib(),
            'homologacao_final':False,
            'teste_android_real':False,
            'fps_android_comprovado':False,
            'comparacao_GPU_real':False,
            'APK_compilado':False,'AAB_compilado':False}
    assert report['foreground_cidade']['rgba_identicos']==140
    assert report['strips_classicos']['rgba_identicos']==120
    assert report['scroll_estatico']['rgba_identicos']==240
    dest=ROOT/'qa-benchmark-hotpath-scroll-v327753.json'
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    pygame.quit()


if __name__=='__main__':
    main()
