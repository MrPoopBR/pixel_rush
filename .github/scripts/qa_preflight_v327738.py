#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.277.38: gate de integridade, visual, fisica e build debug isolado."""
import ast
import configparser
import hashlib
import json
from pathlib import Path
from android_debug_audit import EXPECTED_BLOBS, EXPECTED_CONFIG, ANDROID_VISUAL_ASSETS, REQUIRED_EXTENSIONS


def gitblob(path):
    data=Path(path).read_bytes()
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


PINNED={
    'main.py':'620a3cdcad571168b31c2633b28da94c251b8855',
    'pixelrush_qa_render_v327729.py':'f488b32c8eeea96204fc56fd746d4f6c3eafaa29',
    'pixelrush_qa_gles_present_v327735.py':'e498035ce96e0bc8eb1846bbe3fae28e5e94b739',
    'pixelrush_qa_gles_exact_v327736.py':'cd8961206cceed86bb392f626c77d68083782739',
    'pixelrush_world_v3130.py':'7ca66b28898cd138538831c5bce1133ea961763f',
    'pixelrush_cenarios_v398.py':'2d9b9f22fd88d2f370ae9216ee3ebeb28a07098e',
    'pixelrush_profissional_v3108.py':'a4a93636d279ef7076d96d5f8fd441e4702642f3',
    'pixelrush_fase_b_visuais_v3272.py':'1d8af98523a683aba9d35e0fa736a74e6345ad92',
    'pixelrush_fase_b_visuais_v3274.py':'99f786af7eacd863f6910d98c4ac81bbb99db1ee',
    'pixelrush_qa_android_v327728.py':'4b3454441b6bcf03a0a00e17f3b97f436c7f99ef',
    'pixelrush_qa_ultraleve_v327730.py':'1ab13d44739023b50a602aee815151e9003ec7ab',
    'pixelrush_qa_scene_v327733.py':'493a8b967ff235141c4f492eae5d8486617286e2',
    'pixelrush_qa_camera_v327733.py':'da28a0be8567805ff5c8556c2a7d2bbf31fec635',
    'pixelrush_qa_gles_gate_v327734.py':'462b3e8163cb4495fa8d20131b400f8f7a3fce1e',
    'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py':'d63a9ec12a7c0d0cdcb2106901a4faf8f5065ad7',
    'buildozer.spec':'bdae40a86d5d574551304d0646f0ba9ce13a8bd7',
    'pixelrush_qa_async_export_v327737.py':'882f36abca3c7e7718e85d9184b61968b3dcf87e',
    'pixelrush_qa_alpha_blit_v327731.py':'fefb6f0f32dae61cdc8368ced51da2234646fa89',
    'tests/test_qa_perf_v327738.py':'caa12aab79f06dd4fe1e376e0efcffcb7f53339c',
    'tests/test_qa_full_performance_v327737.py':'583844e36c0ec25a19276e67d768a78a84033f51',
}


def checar():
    conf=configparser.ConfigParser(interpolation=None)
    assert conf.read('buildozer.spec'), 'buildozer.spec ausente'
    spec=conf['app']
    exp=dict(EXPECTED_CONFIG)
    exp.update({'version':'3.277.38','android.numeric_version':'327738'})
    for key,original in exp.items():
        assert spec.get(key,'').strip()==original, 'config mudada: '+key
    assert set(REQUIRED_EXTENSIONS)<=set(x.strip() for x in spec['source.include_exts'].split(','))
    assert {'python3==3.12.12','hostpython3==3.12.12','numpy','pygame-ce'}<=set(
        x.strip() for x in spec['requirements'].split(','))
    protegidos=0
    for path,sha in EXPECTED_BLOBS.items():
        if path in ('main.py','VERSAO_ATUAL.txt','PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py'):
            continue
        assert gitblob(path)==sha,'fonte/asset alterado: '+path
        protegidos+=1
    for path,sha in ANDROID_VISUAL_ASSETS.items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha,'PNG alterado: '+path
    for path,sha in PINNED.items():
        assert gitblob(path)==sha,'mudanca inesperada: '+path
    jogo=Path('PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
    assert 'VERSAO = "v3.277.38-QA-ANDROID-RC"' in jogo
    for marker in ('MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15',
                   'FPS_RENDER = 30 if E_ANDROID else 60',
                   'PIXELRUSH_DEV_BUILD = False',
                   'CacheFundoUltraQA(periodo=5)',
                   'FundoMenusUltraQA(periodo=5)'):
        assert marker in jogo,'invariante sem evidencia: '+marker
    for path in ('main.py','PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py',
                 'pixelrush_qa_render_v327729.py'):
        assert 'pixelrush_qa_gles_exact_v327736' not in Path(path).read_text('utf8'), 'GPU experimental ativada indevidamente'
    io=Path('pixelrush_qa_android_v327728.py').read_text('utf8')
    assert 'pixelrush_qa_v327738' in io
    assert 'apresentacao_swap' in io
    assert 'salvar(esperar=False)' in io
    assert 'v3.277.38-QA-ANDROID-RC' in Path('VERSAO_ATUAL.txt').read_text('utf8')
    workflow=Path('.github/workflows/qa-apk-debug-v327738.yml').read_text('utf8')
    for check in ('refs/heads/qa/android-full-performance-v3.277.38',
                  'tests/test_qa_full_performance_v327737.py',
                  'qa_preflight_v327738.py','tests/test_qa_perf_v327738.py',
                  'buildozer -v android debug',
                  'android_debug_audit.py apk'):
        assert check in workflow,'workflow incompleto: '+check
    assert 'buildozer -v android release' not in workflow
    for path in ('pixelrush_world_v3130.py','pixelrush_cenarios_v398.py',
                 'pixelrush_qa_async_export_v327737.py',
                 'tests/test_qa_full_performance_v327737.py',
                 'tests/test_qa_perf_v327738.py',
                 'pixelrush_qa_alpha_blit_v327731.py'):
        ast.parse(Path(path).read_text('utf8'),filename=path)
    return {
        'resultado':'APROVADO_GATES_ESTATICOS_APENAS',
        'versao':'v3.277.38-QA','modo':'APK_DEBUG_ARM64',
        'pinned_sha':len(PINNED),'arquivos_protegidos':protegidos,
        'assets_android_visual':len(ANDROID_VISUAL_ASSETS),
        'gpu_experimental_ativada':False,'fps_android_homologado':False,
        'apk_compilado':False,'aab_compilado':False,
    }


if __name__=='__main__':
    resultado=checar()
    Path('preflight-qa-v327738.json').write_text(
        json.dumps(resultado,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(resultado,indent=2,ensure_ascii=False))
