#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preflight QA v3.277.36: exige preservacao integral do jogo e GPU desligada.

Aprova SOMENTE isolamento de pesquisa; nunca homologacao Android ou FPS.
"""
import ast
import configparser
import hashlib
import json
from pathlib import Path
from android_debug_audit import EXPECTED_BLOBS, ANDROID_VISUAL_ASSETS, EXPECTED_CONFIG, REQUIRED_EXTENSIONS


def gitblob(path):
    raw=Path(path).read_bytes()
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def executar():
    config=configparser.ConfigParser(interpolation=None)
    assert config.read('buildozer.spec')
    app=config['app']
    expected=dict(EXPECTED_CONFIG)
    expected.update({'version':'3.277.36','android.numeric_version':'327736'})
    for key,value in expected.items():
        assert app.get(key,'').strip()==value, 'Config mudou: '+key
    assert set(REQUIRED_EXTENSIONS)<=set(x.strip() for x in app['source.include_exts'].split(','))
    assert {'pygame-ce','numpy','python3==3.12.12','hostpython3==3.12.12'}<=set(
        x.strip() for x in app['requirements'].split(','))
    protegidos=0
    for filename,sha in EXPECTED_BLOBS.items():
        if filename in ('PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py',
                        'main.py','VERSAO_ATUAL.txt'):
            continue
        assert gitblob(filename)==sha, 'Fonte/asset protegido mudou: '+filename
        protegidos+=1
    for filename,sha in ANDROID_VISUAL_ASSETS.items():
        assert hashlib.sha256(Path(filename).read_bytes()).hexdigest()==sha, 'Asset visual alterado: '+filename
    expected_blobs={
        'main.py':'620a3cdcad571168b31c2633b28da94c251b8855',
        'pixelrush_qa_render_v327729.py':'f488b32c8eeea96204fc56fd746d4f6c3eafaa29',
        'pixelrush_qa_gles_present_v327735.py':'e498035ce96e0bc8eb1846bbe3fae28e5e94b739',
        'pixelrush_world_v3130.py':'99615c4c866adf75fcf47ae63cb134a333c434ad',
        'pixelrush_profissional_v3108.py':'a4a93636d279ef7076d96d5f8fd441e4702642f3',
        'pixelrush_fase_b_visuais_v3272.py':'1d8af98523a683aba9d35e0fa736a74e6345ad92',
        'pixelrush_fase_b_visuais_v3274.py':'99f786af7eacd863f6910d98c4ac81bbb99db1ee',
        'pixelrush_qa_android_v327728.py':'37c25b5edab3451fc0259ce2e465ff0a759d5f69',
        'pixelrush_qa_ultraleve_v327730.py':'1ab13d44739023b50a602aee815151e9003ec7ab',
        'pixelrush_qa_scene_v327733.py':'493a8b967ff235141c4f492eae5d8486617286e2',
        'pixelrush_qa_camera_v327733.py':'da28a0be8567805ff5c8556c2a7d2bbf31fec635',
        'pixelrush_qa_gles_gate_v327734.py':'462b3e8163cb4495fa8d20131b400f8f7a3fce1e',
        'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py':'5ad5087ed9836f2d4289dfb8f6f9943a89ce8326',
        'buildozer.spec':'0f17597a15c7c49010dd11de3460d835062fc6d7',
        'pixelrush_qa_gles_exact_v327736.py':'cd8961206cceed86bb392f626c77d68083782739',
        'tests/test_qa_gles_exact_v327736.py':'6c849f9c73ba7418e4436fdebb46ae2f0da9386b',
        '.github/scripts/qa_benchmark_gles_exact_v327736.py':'10967bd23bfded50d46724505ba6ac50bae40e82',
    }
    for path,sha in expected_blobs.items():
        assert gitblob(path)==sha, 'Hash de isolamento divergente: '+path
    code=Path('PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
    assert 'VERSAO = "v3.277.36-QA-ANDROID-RC"' in code
    for marker in ('PIXELRUSH_DEV_BUILD = False',
                   'MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15',
                   'FPS_RENDER = 30 if E_ANDROID else 60',
                   'CacheFundoUltraQA(periodo=5)',
                   'FundoMenusUltraQA(periodo=5)'):
        assert marker in code, 'Invariante de jogabilidade ausente: '+marker
    for entry in ('main.py','pixelrush_qa_render_v327729.py',
                  'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py'):
        assert 'pixelrush_qa_gles_exact_v327736' not in Path(entry).read_text('utf8'), 'Shader experimental entrou no jogo!'
    shader=Path('pixelrush_qa_gles_exact_v327736.py').read_text('utf8')
    ast.parse(shader)
    assert 'SCALE=__STEP__' in shader and 'SCALE=__STEP__.0' in shader
    assert 'return bool(medicao_android and' in shader
    assert 'v3.277.36-QA-ANDROID-RC' in Path('VERSAO_ATUAL.txt').read_text('utf8')
    workflow=Path('.github/workflows/qa-gles-exact-v327736.yml').read_text('utf8')
    assert "refs/heads/qa/android-gles-pixel-exact-v3.277.36" in workflow
    assert 'tests/test_qa_gles_exact_v327736.py' in workflow
    assert '.github/scripts/qa_benchmark_gles_exact_v327736.py' in workflow
    assert 'buildozer -v android debug' not in workflow
    assert 'buildozer -v android release' not in workflow
    return {
        'resultado':'APROVADO_ISOLAMENTO_APENAS',
        'versao':'v3.277.36-QA',
        'blobs_conferidos':len(expected_blobs)+protegidos,
        'assets_visuais_intactos':len(ANDROID_VISUAL_ASSETS),
        'gpu_integrada_no_jogo':False,
        'fps_android_homologado':False,
        'build_apk':False,'build_aab':False,
    }


if __name__=='__main__':
    r=executar()
    Path('preflight-qa-v327736.json').write_text(
        json.dumps(r,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(r,indent=2,ensure_ascii=False))
