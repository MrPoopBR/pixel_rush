# -*- coding: utf-8 -*-
"""Microbenchmark end-to-end: CPU smoothscale+blit+flip vs GPU GLES2+swap.

Linux/Xvfb Mesa SOMENTE. Nunca registra ganho Android ou aprova integracao.
A GPU nao chama glReadPixels. P95/medianas de 200 quadros apos warmup.
"""
import json
import os
import statistics
import sys
import time
from pathlib import Path

os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import pygame
import pixelrush_qa_gles_present_v327735 as old
from pixelrush_qa_gles_exact_v327736 import shaders, gate_integracao

W,H=450,800


def quantis(valores):
    xs=sorted(valores)
    return {
        'amostras':len(xs),
        'mediana_ms':round(statistics.median(xs),4),
        'p95_ms':round(xs[int(.95*(len(xs)-1))],4),
        'min_ms':round(xs[0],4),
        'max_ms':round(xs[-1],4),
    }


def benchmark(frames=200,warmup=20):
    pygame.init()
    pygame.display.set_mode((W,H))
    src=pygame.Surface((W,H)).convert()
    for y in range(H):
        pygame.draw.line(src,((y*7)%256,(y*13)%256,(y*29)%256),
                         (0,y),(W-1,y))
    for x in range(20,W,33):
        pygame.draw.circle(src,(40,195,242),(x,(x*13)%600+100),19)

    z=.025
    ex=max(1,int(W*z));ey=max(1,int(H*z))
    tamanho=(W+2*ex,H+2*ey)
    dest=pygame.Surface(tamanho).convert(src)
    cpu=[]
    for frame in range(warmup+frames):
        t0=time.perf_counter_ns()
        scaled=pygame.transform.smoothscale(src,tamanho,dest)
        pygame.display.get_surface().blit(
            scaled.subsurface((ex,ey,W,H)),(0,0))
        pygame.display.flip()
        if frame>=warmup:
            cpu.append((time.perf_counter_ns()-t0)/1e6)
    pygame.display.quit()

    # Usar o mesmo shader do teste de equivalência, sem alterar main.
    old.VERT,old.FRAG=shaders('GLES2',pygame.transform.get_smoothscale_backend(),(W,H))
    p=old.GLES2DirectPresenterQA(W,H)
    gpu=[]
    upload=[]
    try:
        for frame in range(warmup+frames):
            t0=time.perf_counter_ns()
            p.draw(src,z,0)
            p.present()
            if frame>=warmup:
                gpu.append((time.perf_counter_ns()-t0)/1e6)
                upload.append(p.cpu_upload_draw_ns/1e6)
        resultado={
            'schema':'pixelrush.qa.benchmark_gles_exact.v1',
            'ambiente':'Linux Xvfb Mesa; nao Android',
            'gpu':p.renderer,
            'versao_gl':p.version,
            'swap':p.swap_method,
            'backend_pygame':pygame.transform.get_smoothscale_backend(),
            'frames_por_caminho':frames,
            'aquecimento':warmup,
            'cpu_smoothscale_blit_flip':quantis(cpu),
            'gles2_upload_shader_swap':quantis(gpu),
            'gles2_chamada_upload_draw':quantis(upload),
            'igualdade_visual_testada_separadamente':True,
            'gpu_android_medida':False,
            'ganho_estavel_fps_android':False,
            'integracao_gpu_aprovada':gate_integracao({'igualdade_total':True},False),
        }
    finally:
        p.close()
    return resultado


if __name__=='__main__':
    r=benchmark()
    dest=Path('qa-gles-exact-benchmark-v327736.json')
    dest.write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(r,indent=2,ensure_ascii=False))
    if r['integracao_gpu_aprovada']:
        raise SystemExit('ERRO: nenhum ambiente Linux aprova integracao Android')
