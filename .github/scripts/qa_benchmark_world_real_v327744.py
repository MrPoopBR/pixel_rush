#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.277.44: benchmark longo OFFLINE de caminhos REAIS de mundo/camera.

Cenario real City v3125 e neve/deserto v3130 via LivingWorld.draw, cache
periodo 5 do jogo e CameraCinematica; HUD sintético. Nao inclui loop principal,
fisica, spawn, audio, touch nem GPU Android. Nao extrapolar FPS Android.
"""
import gc
import json
import os
import statistics
import sys
import time
import tracemalloc
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ.setdefault('PIXELRUSH_QA_MODULAR_BATCH','0')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))

import pygame
from pixelrush_qa_audit_offline_v327744 import inventario_recursos, resumo_caches_mundo, rss_mib


def stats(xs):
    v=sorted(xs)
    if not v:
        return {'n':0,'p50_ms':None,'p95_ms':None,'p99_ms':None,'max_ms':None}
    def f(n):
        return round(v[round((len(v)-1)*n)],3)
    return {'n':len(v),'p50_ms':f(.50),'p95_ms':f(.95),
            'p99_ms':f(.99),'max_ms':round(v[-1],3)}


def medir(biome,frames,display):
    from pixelrush_world_v3130 import LivingWorld
    from pixelrush_qa_ultraleve_v327730 import CacheFundoUltraQA
    from pixelrush_cinema_v3172 import CameraCinematica

    world=LivingWorld(biome,lightweight=False)
    cache=CacheFundoUltraQA(periodo=5)
    camera=CameraCinematica()
    buffer=pygame.Surface((450,800),pygame.SRCALPHA)
    jogador=SimpleNamespace(no_chao=True,rect=pygame.Rect(175,540,33,66))
    clima='nevasca' if biome=='neve' else 'tempestade_areia' if biome=='deserto' else 'chuva'
    phase={'update':[],'fundo_cache_hit':[],'fundo_redraw':[],
           'hud':[],'camera':[],'present':[],'total':[]}
    mem=[]
    gc_start=gc.get_count()
    for i in range(frames):
        t0=time.perf_counter_ns()
        world.update(9.2,night=.4,climate=clima,phase=.5)
        t1=time.perf_counter_ns()
        key=(biome,clima,True,False,buffer.get_size())
        reused=cache.reusar(buffer,key,True)
        if not reused:
            buffer.fill((25,44,67,255))
            world.draw(buffer)
            cache.guardar(buffer,key,True)
        t2=time.perf_counter_ns()
        # HUD simplificado: nao representa HUD real do jogo.
        pygame.draw.rect(buffer,(34,66,96,255),(0,0,450,43))
        pygame.draw.rect(buffer,(239,203,117,255),(10,12,92,13),border_radius=3)
        t3=time.perf_counter_ns()
        jogador.no_chao=i%4==0
        jogador.rect.centery=520+(i*7)%120
        final=camera.aplicar(buffer,jogador,10.5,i%11==0,True)
        t4=time.perf_counter_ns()
        display.blit(final,(0,0))
        pygame.display.flip()
        t5=time.perf_counter_ns()
        if i>=20:
            phase['update'].append((t1-t0)/1e6)
            phase['fundo_cache_hit' if reused else 'fundo_redraw'].append((t2-t1)/1e6)
            phase['hud'].append((t3-t2)/1e6)
            phase['camera'].append((t4-t3)/1e6)
            phase['present'].append((t5-t4)/1e6)
            phase['total'].append((t5-t0)/1e6)
        if i%60==0:
            mem.append({'frame':i,'rss_mib':rss_mib(),
                        'scaled':len(getattr(getattr(world,'city2',None),'_scaled',{})),
                        'cache_hit':cache.acertos,'cache_miss':cache.recriacoes})
    assert cache.pedidos==frames and cache.recriacoes==(frames+4)//5
    return {'bioma':biome,'frames_totais':frames,'amostras_validas':frames-20,
            'desenhos_de_fundo':cache.recriacoes,
            'reusos_de_fundo':cache.passes_evitados,
            'periodicidade':5,'gc_count_antes':gc_start,'gc_count_depois':gc.get_count(),
            'fases':{k:stats(v) for k,v in phase.items()},
            'rss_60_frames':mem,'cache_final':resumo_caches_mundo(world),
            'recursos_unicos':inventario_recursos(world)}


def main():
    from pixelrush_qa_render_v327729 import instalar
    from pixelrush_qa_performance_integrated_v327742 import diagnostico
    pygame.init()
    display=pygame.display.set_mode((450,800))
    instalar()
    start=time.perf_counter()
    result={}
    for biome,frames in (('cidade',1200),('neve',1200),('deserto',240)):
        result[biome]=medir(biome,frames,display)
    # Caminho separado: tracemalloc nao contamina medições de CPU anteriores.
    from pixelrush_world_v3130 import LivingWorld
    tracemalloc.start()
    sandbox=LivingWorld('deserto',lightweight=False)
    sandbox._get_modular()
    traced,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    result['deserto']['tracemalloc_carregamento_python_mib']={
        'atual':round(traced/1048576,3),'pico':round(peak/1048576,3),
        'nota':'Nao conta todos os bytes de pygame/SDL/nativos.'}
    del sandbox
    report={
        'schema':'pixelrush.qa.atuacao_real.offline.v327744',
        'versao':'v3.277.44-QA',
        'tipo':'SUBPIPELINE_REAL_WORLD_DRAW; NAO_QUADRO_COMPLETO_DO_JOGO',
        'plataforma':'Linux SDL dummy pygame-ce; nao Android',
        'fps_android_comprovado':False,'apk_compilado':False,
        'classes_reais':['pixelrush_city2_v3125.CityPilotScene',
                         'pixelrush_biomes2_v3130.ModularBiomeScene'],
        'cache_fundo_mantido_5_quadros':True,'gpu_experimental_ativa':False,
        'duracao_bancada_s':round(time.perf_counter()-start,2),
        'biomas':result,'qa_performance':diagnostico(),
        'observacoes':[
            'O jogo faz render fisico, inimigos, audio, HUD real e eventos adicionais; esta bancada nao.',
            'Frame p95/p99 da bancada Linux nao equivale ao FPS Android.',
            'Cache temporal redesenha 1x em 5 quadros e preserva o mesmo compromisso visual anterior.',
            'Memoria SDL em bytes logicos pode compartilhar buffers; RSS e valor do processo.',
            'Nao deduzir VRAM a partir de inventario de pygame.Surface.',
        ]}
    path=ROOT/'qa-benchmark-world-real-v327744.json'
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=='__main__':
    main()
