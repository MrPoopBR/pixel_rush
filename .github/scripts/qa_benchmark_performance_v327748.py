#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Benchmark offline v3.277.48: CPU, RSS e custo maximo de limpeza.
Nao representa FPS do jogo inteiro, GPU, driver Android ou APK.
"""
import json,os,statistics,sys,time
from collections import OrderedDict
from pathlib import Path
from types import SimpleNamespace
from weakref import WeakSet
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import pygame
from pixelrush_qa_audit_offline_v327744 import rss_mib
from pixelrush_qa_cache_trim_v327748 import EscalonadorTrimQA
from pixelrush_qa_performance_integrated_v327742 import _weather_cached
from pixelrush_world_v3130 import LivingWorld

class MundoSintetico:
    def __init__(self):
        self.biome='cidade'
        self.props_cache={('cidade',i):i for i in range(24)}
        self.props_cache.update({('neve',i):i for i in range(24)})
        self.props_cache.update({('deserto',i):i for i in range(24)})
        for attr in ('cache','fx_cache','normal_cache','material_cache',
                     'flow_cache','geometry_cache'):
            setattr(self,attr,OrderedDict((b,pygame.Surface((32,32)))
                   for b in ('cidade','neve','deserto')))
        self._qa_mirror_props={('neve',i):i for i in range(10)}
        self._qa_deform_buffers={('deserto',i):i for i in range(10)}
        self._city_surfaces={('image',False):pygame.Surface((450,500)),
                             ('normal',False):pygame.Surface((450,500))}
        self.city2=SimpleNamespace(_scaled=OrderedDict((i,pygame.Surface((24,24)))
                                   for i in range(14)))

def percentis(ns):
    samples=sorted(ns)
    return {'n':len(samples),
            'p50_ms':round(statistics.median(samples)/1e6,6),
            'p95_ms':round(samples[round((len(samples)-1)*.95)]/1e6,6),
            'max_ms':round(samples[-1]/1e6,6),
            'cpu_total_ms':round(sum(samples)/1e6,5)}

def clima():
    antes=pygame.Surface((450,800),pygame.SRCALPHA)
    depois=antes.copy()
    frames=(0,5,30,103,200,890)
    tipos=('chuva','tempestade','nevasca','neve','areia',
           'tempestade_areia','cinzas','vento')
    amostras={'original':[],'qa748':[]}
    identicos=0
    for tipo in tipos:
        for frame in frames:
            w=SimpleNamespace(frame=frame,climate=tipo)
            antes.fill((27,53,91,140))
            depois.fill((27,53,91,140))
            LivingWorld._weather(w,antes)
            _weather_cached(w,depois)
            if pygame.image.tobytes(antes,'RGBA')!=pygame.image.tobytes(depois,'RGBA'):
                raise AssertionError((tipo,frame,'rgba_divergente'))
            identicos+=1
    for nome,funcao in (('original',LivingWorld._weather),('qa748',_weather_cached)):
        dest=pygame.Surface((450,800),pygame.SRCALPHA)
        for k in range(1200):
            w=SimpleNamespace(frame=(k*23)%1000,climate=tipos[k%len(tipos)])
            t0=time.process_time_ns()
            funcao(w,dest)
            amostras[nome].append(time.process_time_ns()-t0)
    return {'quadros_rgba':identicos,
            'tempos_cpu':{k:percentis(v) for k,v in amostras.items()}}

def cleanup():
    rss_inicio=rss_mib()
    mundos=[MundoSintetico() for _ in range(3)]
    ativos=WeakSet(mundos)
    cache_fonte={k:pygame.Surface((32,32)) for k in ('cidade','neve','deserto')}
    worker=EscalonadorTrimQA(limite_por_passo=12)
    assert worker.iniciar(ativos,cache_fonte,900,560)
    per_frame=[]
    total=0
    for frame in range(181,540):
        if frame%5==0:continue
        t0=time.process_time_ns()
        worker.passo()
        per_frame.append(time.process_time_ns()-t0)
        total+=1
        if not worker.ativo:break
    assert not worker.ativo
    assert all('cidade' in w.cache for w in mundos)
    assert 'cidade' in cache_fonte
    return {'rss_antes_mib':rss_inicio,'rss_depois_mib':rss_mib(),
            'pressao_rss_sintetica':True,'itens_removidos':worker.removidos,
            'frames_com_passo':total,'custo_cpu_por_frame':percentis(per_frame),
            'remocoes_no_frame_multiplo_5':0,'limite_itens_por_frame':12}

def main():
    pygame.init()
    pygame.display.set_mode((450,800))
    t0=time.process_time_ns()
    clima_out=clima()
    trim_out=cleanup()
    report={'schema':'pixelrush.qa.performance.v327748',
            'versao':'v3.277.48-QA','pygame_ce':pygame.version.ver,
            'clima':clima_out,'limpeza_rss':trim_out,
            'cpu_total_process_ms':round((time.process_time_ns()-t0)/1e6,3),
            'rss_final_mib':rss_mib(),
            'baseline_subsistema_apenas':True,
            'loop_completo_do_jogo_testado':False,
            'ganho_fps_android_comprovado':False,
            'android_testado':False,'apk_compilado':False,
            'gpu_ativa':False,'efeitos_visuais_desligados':False}
    destino=ROOT/'qa-benchmark-performance-v327748.json'
    destino.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    pygame.quit()
    print(json.dumps(report,ensure_ascii=False,indent=2))
    assert clima_out['quadros_rgba']==48
    assert trim_out['itens_removidos']>0

if __name__=='__main__':
    main()
