#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA 3.277.43: microbenchmark de quadro COMPLETO offline em Cidade e Neve.

Mundo 2.5D real + clima + HUD + zoom pygame + blit/flip SDL dummy.
Percentis Linux nao autorizam velocidade em GPU Android.
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
sys.path.insert(0,str(ROOT/'tests'))
import pygame
from test_qa_frame_completo_v327743 import montar_frame, rgba


def percentis(v):
    valores=sorted(v)
    if not valores:
        return {'n':0,'p50_ms':None,'p95_ms':None,'p99_ms':None}
    def p(frac):
        return round(valores[round((len(valores)-1)*frac)],4)
    return {'n':len(valores),'p50_ms':p(.50),'p95_ms':p(.95),
            'p99_ms':p(.99),'max_ms':round(valores[-1],4)}


def main():
    from pixelrush_city2_v3118 import CityPilotScene
    from pixelrush_biomes2_v3126 import ModularBiomeScene
    from pixelrush_cinema_v3172 import CameraCinematica
    import pixelrush_qa_camera_native_auto_v327742 as native
    import pixelrush_qa_camera_v327733 as simd
    pygame.init()
    display=pygame.display.set_mode((450,800))
    native.restaurar_para_teste()
    simd.restaurar_para_teste()
    original=CameraCinematica.aplicar
    simd.instalar()
    native.instalar()
    out={}
    try:
        for biome,scene in (('cidade',CityPilotScene()),
                            ('neve',ModularBiomeScene('neve'))):
            results={'original':{'quadro':[],'mundo_hud':[],'camera':[],
                                 'blit_flip':[]},
                     'qa_seguro':{'quadro':[],'mundo_hud':[],'camera':[],
                                  'blit_flip':[]}}
            cam0,cam1=CameraCinematica(),CameraCinematica()
            cam0.zoom=cam1.zoom=.006
            for idx in range(12):
                f=13+idx*19
                travel=f*11.7
                night=(0.,.2,.54,.85)[idx%4]
                climate=('limpo','chuva','nevasca','vento')[idx%4]
                player=SimpleNamespace(rect=pygame.Rect(170,400+(idx*13)%210,32,68),
                                       no_chao=idx%3==0)
                outputs=[]
                for optimized,label,cam in ((False,'original',cam0),
                                            (True,'qa_seguro',cam1)):
                    t0=time.perf_counter_ns()
                    pixels=montar_frame(scene,f,travel,night,climate,optimized)
                    t1=time.perf_counter_ns()
                    zoom=cam.aplicar(pixels,player,10.+idx*.3,idx%6==0,True) if optimized else original(
                        cam,pixels,player,10.+idx*.3,idx%6==0,True)
                    t2=time.perf_counter_ns()
                    display.blit(zoom,(0,0))
                    pygame.display.flip()
                    t3=time.perf_counter_ns()
                    outputs.append(rgba(zoom))
                    if idx>=2:
                        for key,ns in (('quadro',t3-t0),('mundo_hud',t1-t0),
                                       ('camera',t2-t1),('blit_flip',t3-t2)):
                            results[label][key].append(ns/1e6)
                if outputs[0]!=outputs[1]:
                    raise AssertionError('divergencia frame inteiro '+biome+' '+str(idx))
                if (cam0.zoom,cam0.foco_y)!=(cam1.zoom,cam1.foco_y):
                    raise AssertionError('camera divergiu '+biome+' '+str(idx))
            out[biome]={label:{key:percentis(v) for key,v in timings.items()}
                        for label,timings in results.items()}
            out[biome]['pixels_exatos_em_12_frames']=True
        relatorio={'schema':'pixelrush.qa.frame_completo.v327743',
                   'plataforma':'Linux SDL dummy pygame-ce 2.5.8; NAO Android',
                   'biomas':out,'android_hardware_testado':False,
                   'gpu_ativa':False,'comparacao_fps_android':False,
                   'sem_troca_de_fisica_e_visual':True}
        path=ROOT/'qa-benchmark-frame-completo-v327743.json'
        path.write_text(json.dumps(relatorio,indent=2,ensure_ascii=False),encoding='utf8')
        print(json.dumps(relatorio,indent=2,ensure_ascii=False))
    finally:
        native.restaurar_para_teste()
        simd.restaurar_para_teste()
        pygame.quit()


if __name__=='__main__':
    main()
