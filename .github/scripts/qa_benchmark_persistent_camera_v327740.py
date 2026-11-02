#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bancada QA v3.277.40: custos finais e pixel exato de scroll e camera.

Executa somente no Linux/SDL dummy do CI. GPU Android nao medida.
O teste do cache inclui scroll, fill E blit final, para evitar falsos ganhos.
"""
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import time

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import pygame
from pixelrush_qa_rolling_v327740 import (
    FaixaPersistenteQA, mosaico_referencia, gate_integracao,
)
from pixelrush_qa_gles_exact_v327736 import (
    gate_integracao as gate_gpu, shaders,
)


def quantis(series):
    v=sorted(series)
    return dict(n=len(v),p50_ms=round(statistics.median(v),4),
                p95_ms=round(v[round(.95*(len(v)-1))],4),
                max_ms=round(v[-1],4))


def medir(acao,rodadas=90,aquecer=15):
    tempos=[]
    for i in range(rodadas+aquecer):
        t=time.perf_counter_ns()
        acao(i)
        if i>=aquecer:
            tempos.append((time.perf_counter_ns()-t)/1e6)
    return quantis(tempos)


def cena(razao=900):
    tex=pygame.Surface((razao,500),pygame.SRCALPHA)
    for y in range(500):
        pygame.draw.line(tex,((y*11)%256,(y*7)%256,(y*23)%256,
                               (y*13)%256),(0,y),(razao-1,y))
    return tex


def benchmark_persistente():
    saida={}
    for periodo in (173,450,900):
        tex=cena(periodo)
        base=pygame.Surface((450,800)).convert()
        final=base.copy()
        rolling=FaixaPersistenteQA()
        deslocamentos=[12 + (i*3) for i in range(128)]
        def antigo(i):
            scroll=deslocamentos[i%len(deslocamentos)]
            base.fill((31,45,83))
            offset=scroll%periodo
            x=-offset
            while x<450:
                base.blit(tex,(x,230))
                x+=periodo
        def novo(i):
            scroll=deslocamentos[i%len(deslocamentos)]
            final.fill((31,45,83))
            final.blit(rolling.gerar(tex,scroll),(0,230))
        for sc in deslocamentos[:25]:
            antigo(deslocamentos.index(sc))
            novo(deslocamentos.index(sc))
            if pygame.image.tobytes(base,'RGBA')!=pygame.image.tobytes(final,'RGBA'):
                raise AssertionError('diferenca full-frame '+str((periodo,sc)))
        a=medir(antigo)
        b=medir(novo)
        saida[str(periodo)]={
            'baseline_frame_completo':a,
            'cache_frame_completo':b,
            'speedup_p50':round(a['p50_ms']/max(1e-9,b['p50_ms']),3),
            'pixel_exato':True,
            'ram_buffer_extra_bytes':450*500*4,
        }
    return saida


def camera():
    original=pygame.transform.get_smoothscale_backend()
    resultados={}
    try:
        for tipo in ('RGB','RGBA'):
            src=pygame.Surface((450,800),pygame.SRCALPHA if tipo=='RGBA' else 0)
            for y in range(800):
                cor=((y*13)%256,(y*23)%256,(y*3)%256)
                pygame.draw.line(src,cor+(y*17%256,) if tipo=='RGBA' else cor,
                                 (0,y),(449,y))
            for z in (.002,.01,.025,.034):
                ex=max(1,int(src.get_width()*z))
                ey=max(1,int(src.get_height()*z))
                dest=(450+2*ex,800+2*ey)
                escolhido={}
                hash_ref=None
                for backend in [original]+[x for x in ('GENERIC','SSE2','NEON') if x!=original]:
                    try:
                        pygame.transform.set_smoothscale_backend(backend)
                    except (ValueError,pygame.error):
                        continue
                    saida=pygame.Surface(dest).convert(src)
                    def cham(i):
                        pygame.transform.smoothscale(src,dest,saida)
                    medido=medir(cham,rodadas=30,aquecer=5)
                    dados=pygame.image.tobytes(saida,tipo)
                    digest=hashlib.sha256(dados).hexdigest()
                    if backend==original:hash_ref=digest
                    escolhido[backend]=dict(
                        tempos=medido,pixels_identicos_ao_original=digest==hash_ref)
                resultados[f'{tipo}|{z}']=escolhido
    finally:
        pygame.transform.set_smoothscale_backend(original)
    return dict(backend_original=original,matriz=resultados)


def executar():
    pygame.init()
    pygame.display.set_mode((450,800))
    try:
        p=benchmark_persistente()
        c=camera()
        vert,frag=shaders('GLES2',c['backend_original'],(450,800))
        habilita_cache=gate_integracao({
           'pixel_exato_rgba':True,'pixel_exato_rgb':True,
           'ganho_estavel_frame_completo_android':False,
           'rss_no_limite':False,'sem_alteracoes_de_jogabilidade':True,
        },android_real=False)
        habilita_gpu=gate_gpu({
           'igualdade_total':True,'ganho_estavel_fps_android':False,
           'egl_android_aprovado':False,'sem_regressoes_saves_fisica':True,
        },medicao_android=False)
        if habilita_cache or habilita_gpu:
            raise AssertionError('integracao sem evidencia Android')
        return {
           'schema':'pixelrush.qa.v327740.benchmark.v1',
           'ambiente':'Linux SDL dummy; nao Android',
           'pygame_ce':pygame.version.ver,
           'faixas_persistentes':p,
           'camera_smoothscale':c,
           'gles_prototipo':{
               'sha256_shader_es2':hashlib.sha256((vert+frag).encode()).hexdigest(),
               'upload_gpu_android_medido':False,
               'egl_android_medido':False,
               'pipeline_completo_gpu_aprovado':False},
           'mudancas_de_gameplay':False,
           'cache_persistente_ativo_no_jogo':False,
           'gpu_ativo_no_jogo':False,
           'observacao':'P95 sao amostras de bancada; nao prova FPS real Android.',
        }
    finally:
        pygame.quit()


if __name__=='__main__':
    resultado=executar()
    destino=Path('qa-benchmark-persistent-camera-v327740.json')
    destino.write_text(json.dumps(resultado,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({
        'schema':resultado['schema'],
        'faixas':resultado['faixas_persistentes'],
        'camera_backend_original':resultado['camera_smoothscale']['backend_original'],
        'cache_ativo':False,'gpu_ativo':False},ensure_ascii=False,indent=2))
