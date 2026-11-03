#!/usr/bin/env python3
"""QA v3.277.46: benchmarks offline do loader PROD e buffer integral real."""
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
sys.path.insert(0,str(ROOT/'tests'))
import pygame
from pixelrush_qa_biome_preheat_v327746 import preparar_fora_da_corrida
from pixelrush_qa_audit_offline_v327744 import rss_mib


def pct(a):
    v=sorted(a)
    if not v:return {'n':0}
    return {'n':len(v),'p50_ms':round(v[round((len(v)-1)*.50)],4),
            'p95_ms':round(v[round((len(v)-1)*.95)],4),
            'p99_ms':round(v[round((len(v)-1)*.99)],4),
            'max_ms':round(v[-1],4)}


def bench_preheat(biome, lightweight=True, samples=3):
    from pixelrush_world_prod_v32777 import LivingWorld
    results=[]
    for _ in range(samples):
        baseline=LivingWorld('cidade',lightweight=lightweight)
        prepared=LivingWorld('cidade',lightweight=lightweight)
        before=rss_mib()
        begin=time.perf_counter_ns()
        baseline.switch(biome)
        baseline.update(7.5,night=.35,climate='limpo',phase=.51)
        reference=pygame.Surface((450,800)).convert()
        reference.fill((24,39,62))
        baseline.draw(reference)
        t1=time.perf_counter_ns()
        # O preload e intencionalmente chamado num estado de MENU/CARREGAMENTO,
        # antes de qualquer tick/estado JOGANDO.
        prebegin=time.perf_counter_ns()
        status=preparar_fora_da_corrida(prepared,biome,'CARREGANDO',
            teto_rss_mib=9999,max_aumento_mib=64)
        preend=time.perf_counter_ns()
        if status['estado']!='preparado':
            raise AssertionError('preload PROD falhou: '+str(status))
        t2=time.perf_counter_ns()
        prepared.switch(biome)
        prepared.update(7.5,night=.35,climate='limpo',phase=.51)
        result=pygame.Surface((450,800)).convert()
        result.fill((24,39,62))
        prepared.draw(result)
        t3=time.perf_counter_ns()
        if pygame.image.tobytes(reference,'RGBA') != pygame.image.tobytes(result,'RGBA'):
            raise AssertionError('preload alterou pixels '+biome)
        results.append({'baseline_first_frame_ms':(t1-begin)/1e6,
                        'preheat_off_game_ms':(preend-prebegin)/1e6,
                        'prepared_first_frame_ms':(t3-t2)/1e6,
                        'rss_preheat_delta_mib':status.get('delta_rss_mib'),
                        'rss_before_mib':before,'rss_after_mib':rss_mib(),
                        'cache_count':len(prepared.modular),
                        'pixel_identico':True})
        del baseline,prepared,reference,result
    return {'bioma':biome,'modo':'leve' if lightweight else 'completo',
            'n':len(results),
            'baseline_first':pct([v['baseline_first_frame_ms'] for v in results]),
            'preheat_loading':pct([v['preheat_off_game_ms'] for v in results]),
            'prepared_first':pct([v['prepared_first_frame_ms'] for v in results]),
            'rss_extra': [v['rss_preheat_delta_mib'] for v in results],
            'pixel_identico':all(v['pixel_identico'] for v in results),
            'amostras':results}


def main():
    from test_qa_buffer_full_v327746 import game_module, comparar_bioma
    pygame.init();pygame.display.set_mode((450,800))
    import random
    random.seed(746)
    game=game_module()
    buffers={}
    for biome in ('cidade','neve','deserto'):
        data=comparar_bioma(game,biome,frames=35,cronometrar=True)
        times=data.pop('tempos_ms')
        data['medicoes']={k:pct(v) for k,v in times.items()}
        buffers[biome]=data
    prec={}
    for biome in ('neve','deserto'):
        prec[biome]=bench_preheat(biome,lightweight=True,samples=3)
    report={'schema':'pixelrush.qa.preheat_full_buffer.v327746',
        'version':'v3.277.46-QA',
        'engine':'pixelrush_world_prod_v32777 (atlas SHA v32776)',
        'full_background_stack':True,
        'full_gameplay_loop':False,'android_tested':False,'apk_built':False,
        'preheat_auto_in_game':False,'preheat_limited_to_menus':True,
        'baseline_cache_period':5,
        'buffers':buffers,'preheat':prec,
        'comparability':'benchmark offline Linux SDL dummy, ordem fixa; velocidade de caminhos divergentes nao comparavel; desempenho Android nao homologado',
        'offscreen_automatico_habilitado':False,
        'resultado_do_offscreen':'reprovar se qualquer pixel divergir; bench de copia isolada nao equivale ao frame completo'}
    path=ROOT/'qa-benchmark-preheat-buffer-v327746.json'
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    # Uma hipotese que divergiu em RGB/RGBA nao deve causar falha no
    # DIAGNOSTICO: deve ser reportada REPROVADA e jamais ser ativada no game.
    assert all(x['quadros_comparados']==35 for x in buffers.values())
    assert all(not x['alternativa_aprovada'] for x in buffers.values())
    assert all(x['frames_rgba_identicos']+x['total_quadros_divergentes']==35
               for x in buffers.values())
    assert all(x['pixel_identico'] for x in prec.values())
    pygame.quit()


if __name__=='__main__':
    main()
