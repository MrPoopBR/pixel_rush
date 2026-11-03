#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PIXEL RUSH QA 3.277.57: preflight fechamento 32 (somente leitura).

Gates de sintaxe, integridade e conexao ao caminho real. Nao compila Android,
nao aprova FPS/GLES/NEON, nao reclassifica implementação por suposicao.
"""
import ast
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def blob(path):
    data=(ROOT/path).read_bytes()
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\x00'+data).hexdigest()


PIN={
    'main.py':'620a3cdcad571168b31c2633b28da94c251b8855',
    'pixelrush_qa_render_v327729.py':'01e736770c8b4a3cfc3e475bc443b5975768bc9e',
    'pixelrush_biomes2_v3128.py':'b1fd021a7f1a9d98da564ab6d53c343af4827df2',
    'pixelrush_biomes2_v3130.py':'01a711dc82c563c401a25218c508de6d0784032f',
    'pixelrush_qa_modular_batch_v327744.py':'acceb53f4740a20c6b53725b06d10c063cc69ce2',
    'pixelrush_qa_gc_cooperativo_v327757.py':'1798c8caf0d267fb872182aff6ebca5bd1accd06',
    'pixelrush_qa_precarregamento_visual_v327757.py':'3c9a08dd4a2dbfe24c352c912a9973531264e877',
    'pixelrush_qa_atlas_io_v327747.py':'b775500abd8d7b66cd44009dcb18c2aa1b7afae0',
    'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py':'7970815c1df4ef60d50fbc6877f58bd3a5b82993',
    'buildozer.spec':'569a12c041a417eff97105f82a6173ea1dde78d8',
    'tests/test_qa_fechamento32_v327757.py':'2c34d944e3f7ea889e4304cc54b1dbe7c0a195d8',
    'tests/test_qa_fechamento_modular_v327757.py':'ec7ff889d986ee7d646a999fd52acefd9c792abc',
    # Estes dois backends NAO foram forçados sem Android.
    'pixelrush_qa_gles_bridge_v327749.py':'8304b52070896d749579c7041728c65dd4c599b3',
    'pixelrush_qa_camera_native_auto_v327742.py':'211f3b313c9a39c0e961a169de9b97c8a2c519b1',
}
CODE=[name for name in PIN if name.endswith('.py')]
PROTECTED={
    'main.py':PIN['main.py'],
    'pixelrush_qa_gles_bridge_v327749.py':PIN['pixelrush_qa_gles_bridge_v327749.py'],
    'pixelrush_qa_camera_native_auto_v327742.py':PIN['pixelrush_qa_camera_native_auto_v327742.py'],
}


def gate():
    resultados={'schema':'pixelrush.qa.fechamento32.v327757',
                'fase':'preflight_estatico',
                'homologacao_final':False,
                'gpu_android_testada':False,
                'apk_compilado':False,
                'pin_sha':{},'sintaxe_ast':{}}
    for path,esperado in PIN.items():
        real=blob(path)
        resultados['pin_sha'][path]=real==esperado
        assert real==esperado, (path,'hash divergente',real,esperado)
    for path in CODE:
        ast.parse((ROOT/path).read_text(encoding='utf8'),filename=path)
        resultados['sintaxe_ast'][path]=True
    entry=(ROOT/'main.py').read_text('utf8')
    render=(ROOT/'pixelrush_qa_render_v327729.py').read_text('utf8')
    engine=(ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
    modular=(ROOT/'pixelrush_qa_modular_batch_v327744.py').read_text('utf8')
    snow=(ROOT/'pixelrush_biomes2_v3128.py').read_text('utf8')
    desert=(ROOT/'pixelrush_biomes2_v3130.py').read_text('utf8')
    gc_src=(ROOT/'pixelrush_qa_gc_cooperativo_v327757.py').read_text('utf8')
    atlas=(ROOT/'pixelrush_qa_atlas_io_v327747.py').read_text('utf8')
    assert "'PIXELRUSH_QA_ANDROID' " in entry or "['PIXELRUSH_QA_ANDROID']" in entry
    assert 'instalar_render_qa()' in entry
    assert '_QA_TECH_SAME_FRAME' in render
    assert 'ref(cena),ref(surf)' in render
    assert 'instalar_gc_qa()' in render
    assert 'PIXELRUSH_QA_PRELOAD_VISUAL' in engine
    assert '_qa_precarga_visuais.passo(estado)' in engine
    assert 'if shift:' in snow and 'if shift:' in desert
    assert "tile_invisivel_culado" in modular
    assert 'gc.disable()' in gc_src and "gc.collect(2)" in gc_src
    assert "PIXELRUSH_QA_TILES_IO_PREWARM" in atlas
    assert "sha.hexdigest()==esperado" in atlas
    assert 'VERSAO = "v3.277.57-QA-ANDROID-RC"' in engine
    spec=(ROOT/'buildozer.spec').read_text('utf8')
    assert re.search(r'(?m)^version = 3\.277\.57$',spec)
    assert re.search(r'(?m)^android\.numeric_version = 327757$',spec)
    assert (ROOT/'QA_CHANGELOG_v327757.md').is_file()
    assert (ROOT/'QA_TRACKER_32_v327757.md').is_file()
    wf=(ROOT/'.github/workflows/qa-offline-v327757.yml').read_text('utf8')
    assert 'workflow_dispatch:' in wf and '  push:' not in wf
    assert 'qa/fechamento-32-v3.277.57' in wf
    for name in ('test_qa_fechamento32_v327757.py',
                 'test_qa_fechamento_modular_v327757.py',
                 'qa_preflight_v327757.py'):
        assert name in wf
    for prohibited in ('buildozer -v android','gradle assemble','adb shell'):
        assert prohibited not in wf.lower()
    resultados['resultado']='GATES_ESTATICOS_APROVADOS'
    (ROOT/'qa-preflight-fechamento32-v327757.json').write_text(
        json.dumps(resultados,indent=2,ensure_ascii=False),encoding='utf8')
    return resultados


if __name__=='__main__':
    print(json.dumps(gate(),indent=2,ensure_ascii=False))
