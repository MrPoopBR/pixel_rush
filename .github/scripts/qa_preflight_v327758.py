#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v758 — preflight somente leitura e offline de caminho real / preservação."""
import ast
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PROTECTED={
    'main.py':'620a3cdcad571168b31c2633b28da94c251b8855',
    'pixelrush_biomes2_v3130.py':'01a711dc82c563c401a25218c508de6d0784032f',
    'pixelrush_qa_gles_bridge_v327749.py':'8304b52070896d749579c7041728c65dd4c599b3',
    'pixelrush_qa_camera_native_auto_v327742.py':'211f3b313c9a39c0e961a169de9b97c8a2c519b1',
}
MODULES=(
    'pixelrush_qa_cache_policy_v327758.py',
    'pixelrush_qa_cache_trim_v327748.py',
    'pixelrush_qa_performance_integrated_v327742.py',
    'pixelrush_qa_gc_cooperativo_v327757.py',
    'pixelrush_qa_precarregamento_visual_v327757.py',
    'pixelrush_qa_tiles_menu_v327761.py',
    'pixelrush_qa_atlas_io_v327747.py',
    'tests/test_qa_tiles_menu_v327761.py',
    'pixelrush_qa_render_v327729.py',
    'pixelrush_biomes2_v3128.py',
    'pixelrush_qa_city_weather_v327749.py',
    'pixelrush_qa_city_bootstrap_v327759.py',
    'tests/test_qa_geometry_weather_v327759.py',
    'tests/test_qa_world_real_v327759.py',
    'pixelrush_qa_scene_v327733.py',
    'tests/test_qa_cloud_weather_v327760.py',
    'pixelrush_qa_geometry_retire_v327761.py',
    'tests/test_qa_geometry_retire_v327761.py',
    'tests/test_qa_sky_full_v327761.py',
    'tests/test_qa_cache_gc_v327758.py',
    'tests/test_qa_fechamento32_v327757.py',
    'tests/test_qa_fechamento_modular_v327757.py',
    'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py',
)
def blob(path):
    b=(ROOT/path).read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
    checks={p:(blob(p)==hashval) for p,hashval in PROTECTED.items()}
    assert all(checks.values()),checks
    ast_ok={}
    for path in MODULES:
        ast.parse((ROOT/path).read_text('utf8'),filename=path)
        ast_ok[path]=True
    engine=(ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
    assert 'VERSAO = "v3.277.62-QA-ANDROID-RC"' in engine
    assert "_qa_precarga_visuais.passo(estado)" in engine
    assert "instalar_render_qa()" in (ROOT/'main.py').read_text('utf8')
    perf=(ROOT/'pixelrush_qa_performance_integrated_v327742.py').read_text('utf8')
    trimmer=(ROOT/'pixelrush_qa_cache_trim_v327748.py').read_text('utf8')
    policy=(ROOT/'pixelrush_qa_cache_policy_v327758.py').read_text('utf8')
    gc=(ROOT/'pixelrush_qa_gc_cooperativo_v327757.py').read_text('utf8')
    assert 'mapa_tecnico_quente(world,key)' in perf
    assert 'mapa_tecnico_quente(world,key)' in trimmer
    assert 'janela_quadros=180' in policy
    assert "elif _FRAMES>=180 and _FRAMES%180==1:" in gc
    assert "elif _FRAMES>=30 and _FRAMES%30==1:" in gc
    biome=(ROOT/'pixelrush_biomes2_v3128.py').read_text('utf8')
    assert "low.blit(self._weather,(0,0))" in biome
    assert "_qa_weather_overlay_clean" in biome
    spec=(ROOT/'buildozer.spec').read_text('utf8')
    assert re.search(r'(?m)^version = 3\.277\.62$',spec)
    assert re.search(r'(?m)^android\.numeric_version = 327762$',spec)
    assert (ROOT/'QA_TRACKER_32_v327758.md').is_file()
    assert (ROOT/'QA_CHANGELOG_v327758.md').is_file()
    assert (ROOT/'QA_CHANGELOG_v327759.md').is_file()
    assert (ROOT/'QA_TRACKER_32_v327759.md').is_file()
    assert (ROOT/'QA_TRACKER_32_v327760.md').is_file()
    assert (ROOT/'QA_CHANGELOG_v327760.md').is_file()
    assert (ROOT/'QA_TRACKER_32_v327761.md').is_file()
    assert (ROOT/'QA_CHANGELOG_v327761.md').is_file()
    assert (ROOT/'QA_TRACKER_32_v327762.md').is_file()
    assert (ROOT/'QA_CHANGELOG_v327762.md').is_file()
    assert 'aquecer_tiles=True' in engine
    assert 'tiles_adiados_para_menu' in (ROOT/'pixelrush_qa_atlas_io_v327747.py').read_text('utf8')
    assert 'instalar_geometry_retire_qa()' in (ROOT/'pixelrush_qa_render_v327729.py').read_text('utf8')
    assert '_QA_SAFE_CLOUD_CACHE' in (ROOT/'pixelrush_qa_scene_v327733.py').read_text('utf8')
    assert "PIXELRUSH_QA_GEOMETRY_BORROW','1'" in (ROOT/'pixelrush_qa_render_v327729.py').read_text('utf8')
    assert 'instalar_city_bootstrap_qa()' in (ROOT/'pixelrush_qa_render_v327729.py').read_text('utf8')
    assert '_SNOW_SEEDS' in (ROOT/'pixelrush_biomes2_v3128.py').read_text('utf8')
    assert '_PARTICLE_SEEDS' in (ROOT/'pixelrush_qa_city_weather_v327749.py').read_text('utf8')
    result={'schema':'pixelrush.qa.preflight.v327758','status':'AST_E_PINS_APROVADOS',
            'sha_preservados':checks,'sintaxe':ast_ok,'apk':False,
            'android_homologado':False,'gpu_hardware':False}
    Path('qa-preflight-v327758.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    main()
