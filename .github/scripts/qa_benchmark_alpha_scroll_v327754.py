#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA754 benchmark OFFLINE manual: CPU/RSS e RGBA da Cidade real + scroll.

Nao disparado ao salvar este script. Mede p50/p95 de CPU, nao FPS Android.
Nunca altera main/DEV, recursos ou saves, nao gera APK/AAB.
"""
import json
import os
import statistics
import sys
import time
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import pygame
from pixelrush_city2_v3125 import CityPilotScene
import pixelrush_city2_v3118 as core
import pixelrush_city2_v3124 as city
from pixelrush_qa_audit_offline_v327744 import rss_mib
import pixelrush_qa_incremental_scene_v327750 as rolling


def stats(numbers):
    s = sorted(numbers)
    return {"samples": len(s),
            "p50_ms": round(statistics.median(s)/1e6, 5),
            "p95_ms": round(s[round((len(s)-1)*.95)]/1e6, 5),
            "max_ms": round(s[-1]/1e6, 5)}


def rgba(surface):
    return pygame.image.tobytes(surface, "RGBA")


def render_real():
    scene = CityPilotScene()
    a = pygame.Surface((450, 500), pygame.SRCALPHA)
    b = a.copy()
    orig = (core._QA_SKIP_EMPTY_BASE, core._QA_ALPHA_BOUNDS,
            core._QA_CULL_SPRITES_EARLY, city._QA_NEAR_TUPLE_ON_DEMAND)
    base, fast = [], []
    valid = 0
    try:
        for frame in range(96):
            kind = ("image", "fxmask", "normal", "geometry",
                    "material", "flow")[frame % 6]
            night = (0., .4, .9)[frame % 3]
            climate = ("limpo", "vento", "chuva")[frame % 3]
            travel = 37.15+frame*7.48
            a.fill((13, 35, 85, 95))
            b.fill((13, 35, 85, 95))
            core._QA_SKIP_EMPTY_BASE = False
            core._QA_ALPHA_BOUNDS = False
            core._QA_CULL_SPRITES_EARLY = False
            city._QA_NEAR_TUPLE_ON_DEMAND = False
            t = time.process_time_ns()
            scene.render_scene(a, travel, frame, night, climate, .55,
                               map_kind=kind)
            base.append(time.process_time_ns()-t)
            core._QA_SKIP_EMPTY_BASE = True
            core._QA_ALPHA_BOUNDS = True
            core._QA_CULL_SPRITES_EARLY = True
            city._QA_NEAR_TUPLE_ON_DEMAND = True
            t = time.process_time_ns()
            scene.render_scene(b, travel, frame, night, climate, .55,
                               map_kind=kind)
            fast.append(time.process_time_ns()-t)
            if rgba(a) != rgba(b):
                raise AssertionError(("RGBA_450x500", frame, kind))
            valid += 1
        return {"frames_rgba_identicos": valid,
                "referencia_cpu": stats(base),
                "qa754_cpu": stats(fast),
                "texturas_estaticas_vazias": len(scene._qa_empty_base_maps),
                "atlas_recortados_alpha": len(scene._qa_alpha_bounds)}
    finally:
        (core._QA_SKIP_EMPTY_BASE, core._QA_ALPHA_BOUNDS,
         core._QA_CULL_SPRITES_EARLY,
         city._QA_NEAR_TUPLE_ON_DEMAND) = orig


def scroll_saltos():
    rolling.restaurar_para_teste()
    env = {key: os.environ.get(key)
           for key in ("PIXELRUSH_QA_CITY_INCREMENTAL",
                       "PIXELRUSH_QA_CITY_SCROLL_SCOPE",
                       "PIXELRUSH_QA_CLASSIC_INCREMENTAL")}
    os.environ.update(PIXELRUSH_QA_CITY_INCREMENTAL="1",
                      PIXELRUSH_QA_CITY_SCROLL_SCOPE="static",
                      PIXELRUSH_QA_CLASSIC_INCREMENTAL="0")
    original = CityPilotScene._render_chunk
    base, fast, same = [], [], 0
    try:
        rolling.instalar()
        scene = CityPilotScene()
        v = scene.layers[0].variants[0]
        a = pygame.Surface((450, 500), pygame.SRCALPHA)
        b = a.copy()
        for i in range(90):
            x = -540 + i*2 if i%11 < 8 else -350-i*3
            a.fill((19, 47, 87, 171))
            b.fill((19, 47, 87, 171))
            t = time.process_time_ns()
            original(scene, a, v, False, x, 60+i, .34,
                     "vento", .5, "image")
            base.append(time.process_time_ns()-t)
            t = time.process_time_ns()
            scene._render_chunk(b, v, False, x, 60+i, .34,
                                "vento", .5, "image")
            fast.append(time.process_time_ns()-t)
            if rgba(a) != rgba(b):
                raise AssertionError(("RGBA_SCROLL", i, x))
            same += 1
        return {"comparacoes_rgba_identicas": same,
                "direto_cpu": stats(base),
                "scroll_qa754_cpu": stats(fast),
                "diagnostico": rolling.diagnostico(),
                "scroll_em_producao": False}
    finally:
        rolling.restaurar_para_teste()
        for name, value in env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def main():
    pygame.init()
    pygame.display.set_mode((450, 800))
    start = rss_mib()
    report = {
        "schema": "pixelrush.qa.alpha_scroll.v327754",
        "versao": "v3.277.54-QA",
        "pygame_ce": pygame.version.ver,
        "rss_antes_mib": start,
        "cidade_canais_reais": render_real(),
        "scroll_saltos": scroll_saltos(),
        "rss_depois_mib": rss_mib(),
        "homologacao_final": False, "apk_compilado": False,
        "android_executado": False, "fps_android_comprovado": False,
        "shader_gpu_testado": False,
    }
    assert report["cidade_canais_reais"]["frames_rgba_identicos"] == 96
    assert report["scroll_saltos"]["comparacoes_rgba_identicas"] == 90
    target = ROOT/"qa-benchmark-alpha-scroll-v327754.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                      encoding="utf8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    pygame.quit()


if __name__ == "__main__":
    main()
