#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA755 benchmark MANUAL pygame-ce: SRCALPHA real + scroll RGB oculto.

Nao executado na implementacao. Nao representa FPS Android, shader ou
homologacao final. Preserva producao, DEV, saves e todo o conteudo do jogo.
"""
import json
import os
import statistics
import sys
import time
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import pygame
from pixelrush_city2_v3125 import CityPilotScene
import pixelrush_city2_v3124 as city
import pixelrush_qa_incremental_scene_v327750 as rolling
from pixelrush_qa_audit_offline_v327744 import rss_mib


def timings(ns):
    a=sorted(ns)
    return {"amostras":len(a),
            "p50_cpu_ms":round(statistics.median(a)/1e6,5),
            "p95_cpu_ms":round(a[round((len(a)-1)*.95)]/1e6,5),
            "max_cpu_ms":round(a[-1]/1e6,5)}


def rgba(s):
    return pygame.image.tobytes(s,"RGBA")


def bench_scene():
    scene=CityPilotScene()
    default=city._QA_TECH_OPAQUE_BOUNDS
    original=[]
    novo=[]
    checked=0
    try:
        for i in range(96):
            kind=("normal","flow")[i%2]
            travel=81.0+i*6.75
            night=(0.,.35,.82)[i%3]
            alpha=(0,1,71,255)[i%4]
            a=pygame.Surface((450,500),pygame.SRCALPHA,32)
            a.fill((71,28,46,alpha))
            b=a.copy()
            city._QA_TECH_OPAQUE_BOUNDS=False
            t=time.process_time_ns()
            scene.render_scene(a,travel,i,night,"chuva",.5,map_kind=kind)
            original.append(time.process_time_ns()-t)
            city._QA_TECH_OPAQUE_BOUNDS=True
            t=time.process_time_ns()
            scene.render_scene(b,travel,i,night,"chuva",.5,map_kind=kind)
            novo.append(time.process_time_ns()-t)
            if rgba(a)!=rgba(b):
                raise AssertionError(("RGBA_opaque_scope",i,kind,alpha))
            checked+=1
        return {"frames_rgba_identicos":checked,
                "referencia":timings(original),"qa755":timings(novo),
                "aliases_exactos":len(scene._qa_scaled_alias),
                "hits_aliases":scene._qa_scaled_alias_hits,
                "economia_logica_maxima_potencial_bytes":
                    len(scene._qa_scaled_alias)*900*500*4,
                "observacao":"estimativa de duplicacoes evitadas no atlas, nao RSS medido"}
    finally:
        city._QA_TECH_OPAQUE_BOUNDS=default


def bench_scroll():
    rolling.restaurar_para_teste()
    previous={k:os.environ.get(k) for k in (
        "PIXELRUSH_QA_CITY_INCREMENTAL",
        "PIXELRUSH_QA_CLASSIC_INCREMENTAL",
        "PIXELRUSH_QA_CITY_SCROLL_SCOPE")}
    os.environ.update(PIXELRUSH_QA_CITY_INCREMENTAL="1",
                      PIXELRUSH_QA_CLASSIC_INCREMENTAL="0",
                      PIXELRUSH_QA_CITY_SCROLL_SCOPE="static")
    old=CityPilotScene._render_chunk
    orig=[]
    new=[]
    checked=0
    try:
        rolling.instalar()
        scene=CityPilotScene()
        src=pygame.Surface((450,250),pygame.SRCALPHA,32)
        src.fill((83,101,212,0))
        for j in range(14):
            pygame.draw.rect(src,(40+j*9,99+j*4,135,20+j*15),
                             (j*31,30+j*11,47,39))
        variant=SimpleNamespace(image=src,sprites=[])
        positions=(-897,-804,-703,-699,-695,-691,-688,-530,
                   -526,-521,-516,-511,-507,-499,-490,-482,
                   -475,-467,-455,-451,-447,-280,-276,-271,
                   -267,-263,-258,-251,-244,-240,-236)
        for i,x in enumerate(positions*4):
            a=pygame.Surface((450,500),pygame.SRCALPHA,32)
            a.fill((19,47,103,(0,1,117,255)[i%4]))
            b=a.copy()
            t=time.process_time_ns()
            old(scene,a,variant,False,x,i,.31,"vento",.53,"image")
            orig.append(time.process_time_ns()-t)
            t=time.process_time_ns()
            scene._render_chunk(b,variant,False,x,i,.31,
                                "vento",.53,"image")
            new.append(time.process_time_ns()-t)
            if rgba(a)!=rgba(b):
                raise AssertionError(("RGBA_SCROLL",i,x))
            checked+=1
        return {"frames_rgba_identicos":checked,
                "blit_direto":timings(orig),"scroll_qa755":timings(new),
                "diagnostico":rolling.diagnostico(),
                "scroll_ativado_no_jogo":False}
    finally:
        rolling.restaurar_para_teste()
        for k,v in previous.items():
            if v is None:os.environ.pop(k,None)
            else:os.environ[k]=v


def main():
    pygame.init()
    pygame.display.set_mode((450,800))
    rss_inicial=rss_mib()
    out={
        "schema":"pixelrush.qa.srcalpha_scroll.v327755",
        "versao":"v3.277.55-QA",
        "pygame_ce":pygame.version.ver,
        "rss_antes_mib":rss_inicial,
        "srcalpha_normal_flow":bench_scene(),
        "scroll_srcalpha_rgb_oculto":bench_scroll(),
        "rss_depois_mib":rss_mib(),
        "homologacao_final":False,
        "teste_android_real":False,
        "fps_android_comprovado":False,
        "apk_compilado":False,
        "aab_compilado":False,
    }
    assert out["srcalpha_normal_flow"]["frames_rgba_identicos"]==96
    assert out["scroll_srcalpha_rgb_oculto"]["frames_rgba_identicos"]==124
    path=ROOT/"qa-benchmark-srcalpha-scroll-v327755.json"
    path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf8")
    print(json.dumps(out,ensure_ascii=False,indent=2))
    pygame.quit()


if __name__=="__main__":
    main()
