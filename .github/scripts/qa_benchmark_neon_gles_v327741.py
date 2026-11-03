# -*- coding: utf-8 -*-
"""QA v3.277.41: benchmark real pygame-ce vs C recorte; nao Android real."""
import hashlib
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
from pixelrush_qa_crop_native_v327741 import Crop32QA,gate_android
from pixelrush_qa_gles_exact_v327736 import shaders,gate_integracao as gate_gles

LIB=os.environ.get('PIXELRUSH_QA_NATIVE_CAMERA_LIB',
    '/tmp/pixelrush-qa-native/libpixelrush_camera_crop_v327741.so')


def perfil(fn,n=70,warmup=12):
    valores=[]
    for i in range(n+warmup):
        t=time.perf_counter_ns()
        fn()
        if i>=warmup:valores.append((time.perf_counter_ns()-t)/1e6)
    s=sorted(valores)
    return {'n':len(s),'p50_ms':round(statistics.median(s),5),
            'p95_ms':round(s[int(.95*(len(s)-1))],5)}


def imagem_realista(alpha):
    s=pygame.Surface((450,800),pygame.SRCALPHA if alpha else 0)
    s.fill((22,46,97,253) if alpha else (22,46,97))
    for i in range(110):
        h=(i*33)%270
        c=((i*19)%255,(i*7)%255,(i*37)%255,(i*11)%256)
        pygame.draw.rect(s,c if alpha else c[:3],
                         ((i*113)%450,730-h,22+i%13,h))
    pygame.draw.rect(s,(215,160,62,147) if alpha else (215,160,62),
                     (24,75,209,31))
    return s


def executar():
    pygame.init()
    pygame.display.set_mode((450,800))
    original=pygame.transform.get_smoothscale_backend()
    engine=Crop32QA(LIB)
    out={'schema':'pixelrush.qa.v327741.native_camera.v1',
         'ambiente':'Linux SDL dummy; nao Android',
         'pygame':pygame.version.ver,'backend_inicial':original,
         'resultados':{},'android_medicao':False,
         'neon_android_medicao':False,'native_integrado_ao_jogo':False,
         'gpu_integrado_ao_jogo':False,
         'somente_copia_qa_prototipo':True}
    try:
        for alpha in (False,True):
            src=imagem_realista(alpha)
            for zoom in (.005,.025,.034):
                ex=max(1,int(450*zoom))
                ey=max(1,int(800*zoom))
                dims=(450+2*ex,800+2*ey)
                for backend in ('SSE2','GENERIC','NEON'):
                    try:pygame.transform.set_smoothscale_backend(backend)
                    except (ValueError,pygame.error):continue
                    buffer=pygame.Surface(dims).convert(src)
                    size=(ex,ey)
                    referencia=pygame.transform.smoothscale(src,dims,buffer)
                    nativo=engine.processar(src,dims,size,backend)
                    equal=pygame.image.tobytes(
                        referencia.subsurface((ex,ey,450,800)),'RGBA'
                    )==pygame.image.tobytes(nativo,'RGBA')
                    if not equal:raise AssertionError((alpha,zoom,backend))
                    def cpu():
                        pygame.transform.smoothscale(src,dims,buffer)
                        buffer.subsurface((ex,ey,450,800))
                    def nat():
                        engine.processar(src,dims,size,backend)
                    a=perfil(cpu)
                    b=perfil(nat)
                    out['resultados'][f'{int(alpha)}|{zoom}|{backend}']={
                       'pixel_exato':equal,'baseline_smoothscale_crop':a,
                       'recorte_c_32bpp':b,
                       'speedup_p50':round(a['p50_ms']/max(.000001,b['p50_ms']),3)}
        frag2=shaders('GLES2',original,(450,800))[1]
        frag3=shaders('GLES3',original,(450,800))[1]
        out['alternativas_gles']={
           'gles2_shader_sha256':hashlib.sha256(frag2.encode()).hexdigest(),
           'gles3_shader_sha256':hashlib.sha256(frag3.encode()).hexdigest(),
           'custo_upload_readback_android_medido':False,
           'backend_android_egl_comprovado':False,
           'aprovado':gate_gles({'igualdade_total':True},False)}
        out['cpu_android_aprovado']=gate_android({})
        if out['cpu_android_aprovado'] or out['alternativas_gles']['aprovado']:
            raise AssertionError('gate Android deve ficar BLOQUEADO')
    finally:
        pygame.transform.set_smoothscale_backend(original)
        pygame.quit()
    return out


if __name__=='__main__':
    dados=executar()
    arquivo=Path('qa-benchmark-neon-gles-v327741.json')
    arquivo.write_text(json.dumps(dados,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps({'schema':dados['schema'],'resultados':dados['resultados'],
                      'android_medicao':False,'gpu_ativo':False},ensure_ascii=False))
