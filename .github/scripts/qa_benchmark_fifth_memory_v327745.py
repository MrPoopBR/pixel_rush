#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA 3.277.45: quinto quadro e RSS sob pressao simulada, SEM Android.

Mede o subpipeline real LivingWorld + cache temporal + camera + SDL dummy.
Separa desenho do mundo, copia cache, reuso e flip (incl. cleanup 180).
NÃO representa loop de partida completo, shaders, fisica nem FPS Android.
"""
import gc
import json
import os
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ.setdefault('PIXELRUSH_QA_MODULAR_BATCH','0')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import pygame
import pixelrush_qa_performance_integrated_v327742 as perf
from pixelrush_qa_ultraleve_v327730 import CacheFundoUltraQA
from pixelrush_qa_audit_offline_v327744 import rss_mib, resumo_caches_mundo


def quantiles(v):
    s=sorted(v)
    if not s:
        return {'n':0}
    return {'n':len(s),
            'p50_ms':round(s[round((len(s)-1)*.50)],4),
            'p95_ms':round(s[round((len(s)-1)*.95)],4),
            'p99_ms':round(s[round((len(s)-1)*.99)],4),
            'max_ms':round(s[-1],4)}


def medir(biome,frames,forced=False):
    from pixelrush_world_v3130 import LivingWorld
    from pixelrush_cinema_v3172 import CameraCinematica
    world=LivingWorld(biome)
    cache=CacheFundoUltraQA(periodo=5)
    screen=pygame.Surface((450,800)).convert()
    camera=CameraCinematica()
    player=SimpleNamespace(rect=pygame.Rect(177,535,32,68),no_chao=True)
    climate={'cidade':'chuva','neve':'nevasca','deserto':'tempestade_areia'}[biome]
    if forced:
        # Pressao SIMULADA: forca o ramo de RSS sem alocar gigabytes.
        oldmem=perf._memory_mib
        perf._memory_mib=lambda:900.
        world._city_surfaces[('normal',False)]=pygame.Surface((450,500),pygame.SRCALPHA)
        world._city_surfaces[('image',False)]=pygame.Surface((450,500),pygame.SRCALPHA)
    else:
        oldmem=None
    samples=defaultdict(list)
    checkpoints=[]
    events=[]
    counts={'draw':0,'reuse':0}
    first_perf_frame=perf._LAST_STATUS['frames']
    try:
        for i in range(frames):
            begin=time.perf_counter_ns()
            world.update(9.2,night=.4,climate=climate,phase=.5)
            t1=time.perf_counter_ns()
            key=(biome,climate,True,False,screen.get_size())
            t2=time.perf_counter_ns()
            hit=cache.reusar(screen,key,True)
            t3=time.perf_counter_ns()
            if not hit:
                screen.fill((25,44,67))
                t4=time.perf_counter_ns()
                world.draw(screen)
                t5=time.perf_counter_ns()
                cache.guardar(screen,key,True)
                t6=time.perf_counter_ns()
                counts['draw']+=1
            else:
                t4=t5=t6=t3
                counts['reuse']+=1
            pygame.draw.rect(screen,(35,68,94),(0,0,450,43))
            pygame.draw.rect(screen,(227,199,119),(11,13,19+(i%113),12))
            t7=time.perf_counter_ns()
            player.no_chao=(i%4==0)
            player.rect.centery=518+(i*7)%130
            final=camera.aplicar(screen,player,10.3,i%11==0,True)
            t8=time.perf_counter_ns()
            pygame.display.get_surface().blit(final,(0,0))
            t9=time.perf_counter_ns()
            pygame.display.flip()
            t10=time.perf_counter_ns()
            global_mod=perf._LAST_STATUS['frames']%180
            if i>=20:
                mode='hit' if hit else 'redraw'
                samples['total_'+mode].append((t10-begin)/1e6)
                samples['total_mod5_'+str(i%5)].append((t10-begin)/1e6)
                samples['world_update'].append((t1-begin)/1e6)
                samples['cache_lookup_'+mode].append((t3-t2)/1e6)
                if not hit:
                    samples['fill_redraw'].append((t4-t3)/1e6)
                    samples['world_draw_redraw'].append((t5-t4)/1e6)
                    samples['cache_store_redraw'].append((t6-t5)/1e6)
                samples['hud'].append((t7-t6)/1e6)
                samples['camera'].append((t8-t7)/1e6)
                samples['present_blit'].append((t9-t8)/1e6)
                samples['flip_with_cleanup'].append((t10-t9)/1e6)
                if global_mod==0:
                    samples['flip_180_cleanup'].append((t10-t9)/1e6)
                else:
                    samples['flip_no_cleanup'].append((t10-t9)/1e6)
            if global_mod==0:
                events.append({
                    'local_frame':i,
                    'draw':not hit,
                    'cleanup_last_ms':perf._LAST_STATUS.get('cache_cleanup_last_ms'),
                    'trim_events_accumulated':perf._LAST_STATUS['cache_trim_events'],
                    'rss_real_mib':rss_mib(),
                })
            if i%60==0 or i==frames-1:
                checkpoints.append({'frame':i,'rss_real_mib':rss_mib(),
                                    'city_scaled':len(getattr(getattr(world,'city2',None),'_scaled',{})),
                                    'world_buffers':len(world._city_surfaces)})
        assert counts['draw']==(frames+4)//5
        assert counts['reuse']==frames-counts['draw']
        return {
            'biome':biome,'frames':frames,'forced_rss_branch':forced,
            'rss_simulated_value_mib':900 if forced else None,
            'draws':counts['draw'],'hits':counts['reuse'],
            'phase_stats':{k:quantiles(v) for k,v in sorted(samples.items())},
            'cleanup_180_events':events,
            'rss_samples':checkpoints,
            'city_scaled_final':len(getattr(getattr(world,'city2',None),'_scaled',{})),
            'world_cache_final':resumo_caches_mundo(world),
            'first_global_flip':first_perf_frame,'last_global_flip':perf._LAST_STATUS['frames'],
        }
    finally:
        if oldmem is not None:
            perf._memory_mib=oldmem


def transicoes():
    from pixelrush_world_v3130 import LivingWorld
    world=LivingWorld('cidade')
    display=pygame.Surface((450,800),pygame.SRCALPHA)
    data=[]
    for biome in ('cidade','neve','deserto','cidade','neve','cidade'):
        rss_before=rss_mib()
        t=time.perf_counter_ns()
        if world.biome!=biome:
            world.switch(biome)
        world.update(12,night=.5,climate='limpo',phase=.5)
        world.draw(display)
        dur=(time.perf_counter_ns()-t)/1e6
        data.append({'bioma':biome,'custo_primeiro_frame_ms':round(dur,4),
                     'rss_before_mib':rss_before,'rss_after_mib':rss_mib(),
                     'caches':resumo_caches_mundo(world)})
    return data


def main():
    pygame.init()
    pygame.display.set_mode((450,800))
    # Instala apenas a instrumentacao QA originalmente usada no jogo;
    # nenhum backend de GPU, autotune ou batching experimental.
    from pixelrush_qa_render_v327729 import instalar
    instalar()
    started=time.perf_counter()
    try:
        stats={}
        for biome,frames in (('cidade',1200),('neve',1200),('deserto',360)):
            stats[biome]=medir(biome,frames)
        # Forca SOMENTE o retorno do medidor RSS; no SO a memoria permanece real.
        stats['cidade_rss_forcado']=medir('cidade',540,True)
        changes=transicoes()
        report={
            'schema':'pixelrush.qa.quinto_quadro.memoria.offline.v327745',
            'source_branch':'v3.277.44-QA',
            'versao_diagnostico':'v3.277.45-QA',
            'pygame_ce':pygame.version.ver,
            'driver':pygame.display.get_driver(),
            'frames_medidos':1200+1200+360+540,
            'cache_period_frames':5,
            'memory_pressure_real':False,
            'memory_pressure_simulated_in_selected_run':True,
            'apk_compilado':False,'android_testado':False,
            'full_game_loop_testado':False,
            'benchmark_scope':'LivingWorld.draw + buffer + HUD sintetico + camera + SDL dummy',
            'results':stats,'transitions':changes,
            'perf_status':perf.diagnostico(),
            'total_duration_s':round(time.perf_counter()-started,3),
            'notas':[
                'Custo da limpeza de 180 flips separado do swap puro.',
                'A limpeza precede o redraw 5-frame seguinte quando a fase inicia no frame 0.',
                'A RAM da simulação vem de _memory_mib substituido, RSS do SO permanece real.',
                'Nenhum valor demonstra FPS ou VRAM Android.',
            ]}
        path=ROOT/'qa-benchmark-quinto-memoria-v327745.json'
        path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
        print(json.dumps(report,indent=2,ensure_ascii=False))
        assert report['apk_compilado'] is False
        assert report['android_testado'] is False
        assert report['cache_period_frames']==5
        assert stats['cidade_rss_forcado']['cleanup_180_events']
    finally:
        perf.restaurar_para_teste()
        pygame.quit()


if __name__=='__main__':
    main()
