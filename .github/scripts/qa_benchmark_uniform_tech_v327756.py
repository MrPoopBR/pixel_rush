#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA756: benchmark pygame-ce MANUAL dos fills técnicos SRCALPHA e RLE.

Comparações de RGBA integral, CPU p50/p95, RSS e atlas de 900x500.
Não confundir com FPS Android, não rodar homologação final nem APK/AAB.
"""
import json, os, statistics, sys, time
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import pygame
from pixelrush_city2_v3125 import CityPilotScene
import pixelrush_city2_v3118 as core
from pixelrush_qa_audit_offline_v327744 import rss_mib


def info(values):
    s=sorted(values)
    return {
        'amostras':len(s),
        'p50_cpu_ms':round(statistics.median(s)/1e6,5),
        'p95_cpu_ms':round(s[round((len(s)-1)*.95)]/1e6,5),
        'max_cpu_ms':round(s[-1]/1e6,5),
    }


def rgba(s):
    return pygame.image.tobytes(s,'RGBA')


def medir_cidade():
    scene=CityPilotScene()
    orig=core._QA_UNIFORM_TECH_FILL
    antigo=[]
    novo=[]
    verificados=0
    try:
        for frame in range(96):
            kind=('normal','flow','geometry','fxmask','material','image')[frame%6]
            desloc=37.5+frame*6.75
            night=(0,.31,.73,1.)[frame%4]
            chuva=('limpo','vento','chuva','tempestade')[frame%4]
            target_flags=(0,pygame.SRCALPHA)[frame%2]
            old=pygame.Surface((450,500),target_flags)
            old.fill((73,51,119,0 if frame%5==0 else 177)
                     if target_flags else (73,51,119))
            fast=old.copy()
            core._QA_UNIFORM_TECH_FILL=False
            t=time.process_time_ns()
            scene.render_scene(old,desloc,frame,night,chuva,.5,map_kind=kind)
            antigo.append(time.process_time_ns()-t)
            core._QA_UNIFORM_TECH_FILL=True
            t=time.process_time_ns()
            scene.render_scene(fast,desloc,frame,night,chuva,.5,map_kind=kind)
            novo.append(time.process_time_ns()-t)
            if rgba(old)!=rgba(fast):
                raise AssertionError((frame,kind,'RGBA integral diferente'))
            verificados+=1
    finally:
        core._QA_UNIFORM_TECH_FILL=orig
    return {'quadros_rgba_identicos':verificados,
            'caminho_legado':info(antigo),
            'fill_unif_qa756':info(novo),
            'fontes_uniformes_reais':len(scene._qa_uniform_tech),
            'hits_sem_blit_900x500':scene._qa_uniform_tech_hits,
            'entradas_atlas_lru':len(scene._scaled),
            'teto_entradas_lru':scene._scaled_limit,
            'fps_android':None,
            'observacao':'CPU offline: não comprova melhora no Android real'}


def medir_instancia_isolada():
    # Duas instâncias com mesmo seed: a diferença de LRU após 1 redraw
    # técnico indica atlas que deixaram de ser criados no caminho QA.
    flag=core._QA_UNIFORM_TECH_FILL
    try:
        result={}
        for enabled in (False,True):
            core._QA_UNIFORM_TECH_FILL=enabled
            scene=CityPilotScene()
            for kind in ('normal','flow'):
                surface=pygame.Surface((450,500),pygame.SRCALPHA)
                scene.render_scene(surface,177.125,32,.35,'limpo',.5,
                                   map_kind=kind)
            result['qa_ativado' if enabled else 'original']={
                'surfaces_900x500_em_lru':len(scene._scaled),
                'memoria_logica_lru_bytes':sum(
                    x.get_pitch()*x.get_height() for x in scene._scaled.values()),
                'atlas_uniformes':len(scene._qa_uniform_tech),
                'fills_uniformes':scene._qa_uniform_tech_hits,
            }
        return result
    finally:
        core._QA_UNIFORM_TECH_FILL=flag


def main():
    pygame.init()
    pygame.display.set_mode((450,800))
    start=rss_mib()
    result={
        'schema':'pixelrush.qa.uniform.technical.v327756',
        'versao':'v3.277.56-QA',
        'pygame_ce':pygame.version.ver,
        'rss_inicial_mib':start,
        'cidade_rgba_e_cpu':medir_cidade(),
        'comparacao_lru_instancias':medir_instancia_isolada(),
        'rss_final_mib':rss_mib(),
        'homologacao_final':False,
        'android_testado':False,
        'fps_android_comprovado':False,
        'apk_compilado':False,
        'aab_compilado':False,
    }
    assert result['cidade_rgba_e_cpu']['quadros_rgba_identicos']==96
    dest=ROOT/'qa-benchmark-uniform-tech-v327756.json'
    dest.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    pygame.quit()


if __name__=='__main__':
    main()
