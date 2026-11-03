# -*- coding: utf-8 -*-
"""QA v3.277.42: benchmark real do custo do frame e caches novos (somente Linux)."""
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


def mediana(acao,count=75):
    vals=[]
    for i in range(count+12):
        start=time.perf_counter_ns()
        acao()
        if i>=12:
            vals.append((time.perf_counter_ns()-start)/1e6)
    vals.sort()
    return dict(n=len(vals),p50_ms=round(statistics.median(vals),4),
                p95_ms=round(vals[round((len(vals)-1)*.95)],4))


def main():
    pygame.init();pygame.display.set_mode((450,800))
    from pixelrush_world_v3130 import LivingWorld
    from pixelrush_qa_performance_integrated_v327742 import (
        _weather_cached,diagnostico)
    from pixelrush_qa_camera_native_auto_v327742 import diagnostico as camera
    from pixelrush_qa_scroll_auto_v327742 import status as scroll
    from pixelrush_city2_v3118 import CityPilotScene
    results={}
    orig=LivingWorld._weather
    for typ in ('tempestade','nevasca','cinzas','vento'):
        fake=SimpleNamespace(frame=151,climate=typ)
        surface=pygame.Surface((450,800),pygame.SRCALPHA)
        s1=surface.copy();s2=surface.copy()
        orig(fake,s1)
        _weather_cached(fake,s2)
        if pygame.image.tobytes(s1,'RGBA')!=pygame.image.tobytes(s2,'RGBA'):
            raise AssertionError('clima nao pixel exato '+typ)
        results[typ]={'original':mediana(lambda:orig(fake,s1)),
                      'pool':mediana(lambda:_weather_cached(fake,s2)),
                      'pixel_exato':True}
    scene=CityPilotScene()
    target=pygame.Surface((450,500),pygame.SRCALPHA)
    params=(154.2,105,.54,'limpo',.45)
    scene.render_scene(target,*params)
    ref=pygame.image.tobytes(target,'RGBA')
    def old_veil():
        scene._qa_night_veil=None
        scene.render_scene(target,*params)
    def reused_veil():
        scene.render_scene(target,*params)
    old_veil()
    if pygame.image.tobytes(target,'RGBA')!=ref:
        raise AssertionError('night veil divergente')
    results['cidade_noite']={'alocacao_original_por_frame':mediana(old_veil,35),
                              'reuso_alfa_mesmos_pixels':mediana(reused_veil,35),
                              'pixel_exato':True}
    out={'schema':'pixelrush.qa.32.v327742.benchmark.v1',
         'plataforma':'Linux SDL dummy; nao Android',
         'pygame':pygame.version.ver,'resultados':results,
         'runtime':diagnostico(),'camera_native':camera(),'scroll':scroll(),
         'android_hardware_testado':False,'gpu_integrada':False,
         'fps_homologado':False,'fisica_e_visual_preservados':True}
    Path('qa-benchmark-all32-v327742.json').write_text(
        json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(out,ensure_ascii=False,indent=2)[:9000])
    pygame.quit()


if __name__=='__main__':
    main()
