#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v776 — preflight somente leitura e offline de caminho real / preservação."""
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
    'tests/test_qa_r11_chunk_trace_v327777.py',
    'tests/test_qa_r11_city_hotspots_v327776.py',
    'tests/test_qa_r11_vinheta_views_bench_v327776.py',
    'pixelrush_qa_r11_vinheta_v327776.py',
    'pixelrush_qa_r11_world_bounds_v327776.py',
    'tests/test_qa_r11_world_bounds_v327776.py',
    'tests/test_qa_r11_world_bands_v327776.py',
    'pixelrush_world_v3130.py',
    'pixelrush_qa_r11_passes_v327776.py',
    'pixelrush_gamefeel_v3129.py',
    'tests/test_qa_r11_vinheta_v327776.py',
    'tests/test_qa_r11_passe_v327776.py',
    'pixelrush_qa_cache_policy_v327758.py',
    'pixelrush_qa_cache_trim_v327748.py',
    'pixelrush_qa_memory_budget_v327765.py',
    'tests/test_qa_damage_memory_v327767.py',
    'pixelrush_qa_particle_reuse_v327766.py',
    'tests/test_qa_particle_reuse_v327766.py',
    'pixelrush_qa_unified_post_v327750.py',
    'tests/test_qa_memory_budget_v327765.py',
    'tests/test_qa_unified_post_v327765.py',
    'tests/test_qa_modular_cold_cache_v327762.py',
    'pixelrush_qa_performance_integrated_v327742.py',
    'pixelrush_qa_gc_cooperativo_v327757.py',
    'pixelrush_qa_precarregamento_visual_v327757.py',
    'pixelrush_qa_tiles_menu_v327761.py',
    'pixelrush_qa_atlas_io_v327747.py',
    'tests/test_qa_tiles_menu_v327761.py',
    'pixelrush_qa_render_v327729.py',
    'pixelrush_city2_v3118.py',
    'pixelrush_city2_v3122.py',
    'tests/test_qa_scale_recycle_v327774.py',
    'tests/test_qa_a54_matrix_v327776.py',
    'tests/test_qa_pet_preload_v327776.py',
    'tests/test_qa_camera_backend_v327776.py',
    'tests/test_qa_fx_tutorial_font_v327776.py',
    'tests/test_qa_r10_passe_v327776.py',
    'pixelrush_qa_replay_pool_v327773.py',
    'tests/test_qa_replay_reuse_v327773.py',
    'tests/test_qa_r10_passe_v327773.py',
    'pixelrush_biomes2_v3128.py',
    'pixelrush_qa_city_weather_v327749.py',
    'pixelrush_qa_city_bootstrap_v327759.py',
    'pixelrush_qa_city_intern_v327768.py',
    'pixelrush_qa_pet_preload_v327769.py',
    'pixelrush_qa_camera_v327733.py',
    'pixelrush_tutorial_corrida_v3274.py',
    'tests/test_qa_tutorial_letras_v327771.py',
    'tests/test_qa_camera_backend_v327771.py',
    'pixelrush_tutorial_corrida_v3277.py',
    'pixelrush_producao_fx_v32771.py',
    'pixelrush_fontes_prod_v32771.py',
    'tests/test_qa_fx_tutorial_font_v327772.py',
    'tests/test_qa_tutorial_android_font_v327770.py',
    'tests/test_qa_pet_preload_v327769.py',
    'tests/test_qa_city_intern_v327768.py',
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
    assert 'VERSAO = "v3.277.77-QA-ANDROID-RC"' in engine
    assert 'qa_replay_captura' in engine and 'qa_fundo_cache_chao' in engine
    assert 'instalar_replay_qa()' in (ROOT/'pixelrush_qa_render_v327729.py').read_text('utf8')
    assert "_qa_precarga_visuais.passo(estado)" in engine
    assert "instalar_render_qa()" in (ROOT/'main.py').read_text('utf8')
    perf=(ROOT/'pixelrush_qa_performance_integrated_v327742.py').read_text('utf8')
    trimmer=(ROOT/'pixelrush_qa_cache_trim_v327748.py').read_text('utf8')
    policy=(ROOT/'pixelrush_qa_cache_policy_v327758.py').read_text('utf8')
    gc=(ROOT/'pixelrush_qa_gc_cooperativo_v327757.py').read_text('utf8')
    assert 'mapa_tecnico_quente(world,key)' in perf
    assert 'mapa_tecnico_quente(world,key)' in trimmer
    assert 'janela_quadros=180' in policy
    assert 'modular_cache_fria' in policy
    assert (ROOT/'QA_TRACKER_32_v327765.md').is_file()
    assert (ROOT/'QA_CHANGELOG_v327765.md').is_file()
    assert (ROOT/'QA_TRACKER_32_v327766.md').is_file()
    assert (ROOT/'QA_CHANGELOG_v327766.md').is_file()
    assert (ROOT/'QA_TRACKER_32_v327767.md').is_file()
    assert (ROOT/'QA_CHANGELOG_v327767.md').is_file()
    assert (ROOT/'QA_TRACKER_32_v327768.md').is_file()
    assert (ROOT/'QA_TRACKER_32_v327769.md').is_file()
    assert (ROOT/'QA_CHANGELOG_v327769.md').is_file()
    tutorial=(ROOT/'pixelrush_tutorial_corrida_v3277.py').read_text('utf8')
    fx=(ROOT/'pixelrush_producao_fx_v32771.py').read_text('utf8')
    unicode=(ROOT/'pixelrush_fontes_prod_v32771.py').read_text('utf8')
    assert "from pixelrush_tutorial_corrida_v3277 import _fonte as fonte_tutorial" in fx
    assert "'ANDROID_ARGUMENT' in os.environ" in unicode
    assert "'/system/fonts/Roboto-Bold.ttf'" in tutorial
    assert "'ANDROID_ARGUMENT' in os.environ" in tutorial
    assert '_qa_camera_boot_bench(display_surface,(_qa_w+18,_qa_h+32))' in engine
    assert "'GENERIC'" in (ROOT/'pixelrush_qa_camera_v327733.py').read_text('utf8')
    assert 'preparar_pet_compativel(' in engine
    assert (ROOT/'QA_CHANGELOG_v327768.md').is_file()
    assert 'compartilhar(self)' in (ROOT/'pixelrush_qa_city_bootstrap_v327759.py').read_text('utf8')
    assert "'_qa_damage_layer'" in (ROOT/'pixelrush_qa_memory_budget_v327765.py').read_text('utf8')
    assert 'instalar_pool_particulas_qa(ParallaxBackground,Particula)' in engine
    assert "elif _FRAMES>=180 and _FRAMES%180==1:" in gc
    assert "elif _FRAMES>=30 and _FRAMES%30==1:" in gc
    biome=(ROOT/'pixelrush_biomes2_v3128.py').read_text('utf8')
    assert "low.blit(self._weather,(0,0))" in biome
    assert "_qa_weather_overlay_clean" in biome
    spec=(ROOT/'buildozer.spec').read_text('utf8')
    assert re.search(r'(?m)^version = 3\.277\.77$',spec)
    assert re.search(r'(?m)^android\.numeric_version = 327777$',spec)
    assert (ROOT/'QA_TRACKER_32_v327777.md').is_file()
    assert (ROOT/'QA_CHANGELOG_v327777.md').is_file()
    assert (ROOT/'QA_TRACKER_32_v327776.md').is_file()
    assert (ROOT/'QA_CHANGELOG_v327776.md').is_file()
    assert (ROOT/'QA_TRACKER_32_v327774.md').is_file()
    assert (ROOT/'QA_CHANGELOG_v327774.md').is_file()
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
    assert (ROOT/'QA_TRACKER_32_v327763.md').is_file()
    assert (ROOT/'QA_CHANGELOG_v327763.md').is_file()
    assert (ROOT/'QA_TRACKER_32_v327765.md').is_file()
    assert (ROOT/'QA_CHANGELOG_v327765.md').is_file()
    assert 'pressao_cache=pressionado' in perf
    assert 'cache_surface_mib' in perf
    assert 'aquecer_tiles=True' in engine
    assert 'tiles_adiados_para_menu' in (ROOT/'pixelrush_qa_atlas_io_v327747.py').read_text('utf8')
    assert 'instalar_geometry_retire_qa()' in (ROOT/'pixelrush_qa_render_v327729.py').read_text('utf8')
    assert '_QA_SAFE_CLOUD_CACHE' in (ROOT/'pixelrush_qa_scene_v327733.py').read_text('utf8')
    assert "PIXELRUSH_QA_GEOMETRY_BORROW','1'" in (ROOT/'pixelrush_qa_render_v327729.py').read_text('utf8')
    assert 'instalar_city_bootstrap_qa()' in (ROOT/'pixelrush_qa_render_v327729.py').read_text('utf8')
    assert '_SNOW_SEEDS' in (ROOT/'pixelrush_biomes2_v3128.py').read_text('utf8')
    assert '_PARTICLE_SEEDS' in (ROOT/'pixelrush_qa_city_weather_v327749.py').read_text('utf8')
    # Auditoria QA775: sem mudancas nos gates CPU/GPU, saves, main ou DEV.
    assert "PIXELRUSH_QA_CITY_RECYCLE_SCALE','1'" in (ROOT/'pixelrush_city2_v3118.py').read_text('utf8')
    assert "PIXELRUSH_QA_GLES_BRIDGE','0'" in (ROOT/'pixelrush_qa_gles_bridge_v327749.py').read_text('utf8')
    result={'schema':'pixelrush.qa.preflight.v327776','status':'AST_E_PINS_APROVADOS',
            'sha_preservados':checks,'sintaxe':ast_ok,'apk':False,
            'android_homologado':False,'gpu_hardware':False}
    Path('qa-preflight-v327776.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    main()
