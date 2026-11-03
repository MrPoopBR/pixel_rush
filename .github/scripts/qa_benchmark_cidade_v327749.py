#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Benchmark QA749 (SDL dummy): compositor real da Cidade e clima integrado.
Execucao exclusivamente posterior/manual; nao coleta dados Android nem APK.
"""
import json,os,random,statistics,sys,time
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import pygame
from pixelrush_qa_audit_offline_v327744 import rss_mib
from pixelrush_city2_v3125 import CityPilotScene
from pixelrush_citylife_v3123 import CityLifeDirector
import pixelrush_qa_city_tiles_v327749 as tile_plan
import pixelrush_qa_city_weather_v327749 as weather_qa

def resumo(vals):
    s=sorted(vals)
    return {'n':len(s),'mediana_cpu_ms':round(statistics.median(s)/1e6,5),
            'p95_cpu_ms':round(s[round((len(s)-1)*.95)]/1e6,5)}

def render_city():
    scene=CityPilotScene()
    maps=('image','normal','geometry','material','fxmask','flow')
    old=[];optimized=[];equal=0
    for frame in (5,19,61,101,203,409):
        travel=frame*7.35
        clima=('limpo','chuva','tempestade')[frame%3]
        noite=(0,.23,.56,.91)[frame%4]
        for kind in maps:
            ref=pygame.Surface((450,500),pygame.SRCALPHA)
            trial=ref.copy()
            ref.fill((25,41,69,211));trial.blit(ref,(0,0))
            tile_plan.restaurar_para_teste()
            t=time.process_time_ns()
            scene.render_scene(ref,travel,frame,noite,clima,.51,map_kind=kind)
            old.append(time.process_time_ns()-t)
            tile_plan.instalar()
            try:
                t=time.process_time_ns()
                scene.render_scene(trial,travel,frame,noite,clima,.51,map_kind=kind)
                optimized.append(time.process_time_ns()-t)
            finally:
                # Conserva cache ate o fim do conjunto de mapas, a repeticao
                # entre mapas e a caracteristica central sob teste.
                pass
            if pygame.image.tobytes(ref,'RGBA')!=pygame.image.tobytes(trial,'RGBA'):
                raise AssertionError(('cidade',kind,frame))
            equal+=1
    out={'quadros_rgba_identicos':equal,'original':resumo(old),
         'com_plano':resumo(optimized),'plano':tile_plan.estatisticas()}
    tile_plan.restaurar_para_teste()
    return out

def climate_city():
    director=CityLifeDirector()
    reference=CityLifeDirector.draw_atmosphere
    wet_ref=CityLifeDirector.draw_wet_reflections
    direct=[];fast=[];equals=0
    try:
        for i in range(64):
            a=pygame.Surface((450,500),pygame.SRCALPHA)
            b=a.copy()
            a.fill((34,75,92,220));b.blit(a,(0,0))
            frame=i*9
            travel=i*14.7
            night=(0.,.4,.85)[i%3]
            climate=('limpo','chuva','tempestade','vento')[i%4]
            t=time.process_time_ns()
            reference(director,a,travel,frame,night,climate,1)
            wet_ref(director,a,travel,frame,night,climate)
            direct.append(time.process_time_ns()-t)
            weather_qa.instalar()
            t=time.process_time_ns()
            director.draw_atmosphere(b,travel,frame,night,climate,1)
            director.draw_wet_reflections(b,travel,frame,night,climate)
            fast.append(time.process_time_ns()-t)
            if pygame.image.tobytes(a,'RGBA')!=pygame.image.tobytes(b,'RGBA'):
                raise AssertionError(('clima_real',frame))
            equals+=1
    finally:
        weather_qa.restaurar_para_teste()
    return {'quadros_rgba_identicos':equals,
            'original':resumo(direct),'qa':resumo(fast)}

def main():
    pygame.init();pygame.display.set_mode((450,800))
    rng=random.getstate()
    rss0=rss_mib()
    results={'schema':'pixelrush.qa.city.real.v327749',
             'versao':'v3.277.49-QA',
             'cidade_compositor':render_city(),
             'cidade_clima':climate_city(),
             'rss_antes_mib':rss0,'rss_depois_mib':rss_mib(),
             'pygame_ce':pygame.version.ver,
             'android_testado':False,'apk_compilado':False,
             'gpu_ativa':False,'fps_android_comprovado':False,
             'loop_completo_corrida':False}
    assert random.getstate()==rng
    ROOT.joinpath('qa-benchmark-cidade-v327749.json').write_text(
        json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(results,ensure_ascii=False,indent=2))
    pygame.quit()

if __name__=='__main__':
    main()
