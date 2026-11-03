#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.277.42: gate de integridade, visual, fisica e build debug isolado."""
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
    'pixelrush_qa_render_v327729.py':'5bf4f55f2583ede174726b56a3b4d64ae4de9607',
    'pixelrush_qa_gles_present_v327735.py':'6ebb9bd065f5168bbe18dd43398cc0df1116dba3',
    'pixelrush_qa_gles_exact_v327736.py':'cd8961206cceed86bb392f626c77d68083782739',
    'pixelrush_world_v3130.py':'7ca66b28898cd138538831c5bce1133ea961763f',
    'pixelrush_cenarios_v398.py':'2d9b9f22fd88d2f370ae9216ee3ebeb28a07098e',
    'pixelrush_profissional_v3108.py':'a4a93636d279ef7076d96d5f8fd441e4702642f3',
    'pixelrush_fase_b_visuais_v3272.py':'1d8af98523a683aba9d35e0fa736a74e6345ad92',
    'pixelrush_fase_b_visuais_v3274.py':'99f786af7eacd863f6910d98c4ac81bbb99db1ee',
    'pixelrush_qa_android_v327728.py':'7b6caf24ce0a490b542db5f8ad2d3bdd15bdec94',
    'pixelrush_qa_ultraleve_v327730.py':'1ab13d44739023b50a602aee815151e9003ec7ab',
    'pixelrush_qa_scene_v327733.py':'493a8b967ff235141c4f492eae5d8486617286e2',
    'pixelrush_qa_camera_v327733.py':'da28a0be8567805ff5c8556c2a7d2bbf31fec635',
    'pixelrush_qa_gles_gate_v327734.py':'462b3e8163cb4495fa8d20131b400f8f7a3fce1e',
    'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py':'7a32c2f24a234b2dce865004e8703991d8b38df4',
    'buildozer.spec':'631740f331b9ae331b42136f48bc7d68dd796ac5',
    'pixelrush_qa_async_export_v327737.py':'882f36abca3c7e7718e85d9184b61968b3dcf87e',
    'pixelrush_qa_alpha_blit_v327731.py':'fefb6f0f32dae61cdc8368ced51da2234646fa89',
    'tests/test_qa_perf_v327738.py':'2db0d240a6237b862848705970d91585a71925ad',
    'pixelrush_city2_v3118.py':'ee1dab936030fe42a9560c1d7fe83d3aec933ff4',
    'tests/test_qa_camera_city_v327739.py':'c7015dd330b1d2ebbb7acef711bafb91384a951b',
    '.github/scripts/qa_benchmark_camera_world_v327739.py':'4389307bfcc94d8911d4598e14f2b26603a101a7',
    'pixelrush_qa_rolling_v327740.py':'19377868517c56227db45c3aab782c3021182780',
    'tests/test_qa_rolling_camera_v327740.py':'d5ccef48ae3c9107457e49f39c8c5cf283fc4f43',
    '.github/scripts/qa_benchmark_persistent_camera_v327740.py':'0b175e561e3d927684b5b15c9c7e83f9f5cf6eb2',
    'qa_native/camera_crop_native_v327741.c':'a2c277a9db74c1f03324e86c00429b6d597ae61d',
    'pixelrush_qa_crop_native_v327741.py':'653335fbfeacfa9c684b67c0abe8a37ca7bace6a',
    'tests/test_qa_crop_native_v327741.py':'084ddf5a38b2de0edb7e1f21fe6d4afe269d1df1',
    '.github/scripts/qa_benchmark_neon_gles_v327741.py':'67364bd1b9a69bba36d0ddc83477ecfffb15f518',
    'tests/test_qa_gles_real_v327741.py':'be365c00937c847b8d056b09a6d8fd2d0dc63aae',
    'pixelrush_qa_performance_integrated_v327742.py':'ef65845778b2d2f01dd488db4314cf6905bfdea4',
    'pixelrush_qa_camera_native_auto_v327742.py':'630f370303d15c93ab58946760ea2580c07a1ec9',
    'pixelrush_qa_scroll_auto_v327742.py':'9e7f369b76275661453d1add253a74ccaa96a561',
    'pixelrush_qa_gles_pbo_v327742.py':'3f724b9504f0693390609bd2da8063482a9cd9f6',
    'tests/test_qa_20_integrated_v327742.py':'6f774e20ce0f165c84d3e758b6ec944c0343f4a7',
    'tests/test_qa_scroll_auto_v327742.py':'47d7598f07d8857369f11ebabc4edb8f68319f7e',
    'tests/test_qa_gles_pbo_v327742.py':'6b05e9bcda8e7e87a475801f6f07d478492ecb02',
    '.github/scripts/qa_benchmark_all32_v327742.py':'52afc16803edff0364b10d1b383ea33e733181f0',
    'pixelrush_biomes2_v3126.py':'06abc1cff35dc32db15d732f3e2d76888b240787',
    'tests/test_qa_modular_batch_v327742.py':'12999ec4f632bc0d093e87187751f6e036961fff',
    'tests/test_qa_full_performance_v327737.py':'87dfb7b52c12a782422cc77d76eb21f97532407e',
}


def checar():
    conf=configparser.ConfigParser(interpolation=None)
    assert conf.read('buildozer.spec'), 'buildozer.spec ausente'
    spec=conf['app']
    exp=dict(EXPECTED_CONFIG)
    exp.update({'version':'3.277.42','android.numeric_version':'327742'})
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
    assert 'VERSAO = "v3.277.42-QA-ANDROID-RC"' in jogo
    for marker in ('MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15',
                   'FPS_RENDER = 30 if E_ANDROID else 60',
                   'PIXELRUSH_DEV_BUILD = False',
                   'CacheFundoUltraQA(periodo=5)',
                   'FundoMenusUltraQA(periodo=5)'):
        assert marker in jogo,'invariante sem evidencia: '+marker
    for path in ('main.py','PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py',
                 'pixelrush_qa_render_v327729.py'):
        assert 'pixelrush_qa_gles_exact_v327736' not in Path(path).read_text('utf8'), 'GPU experimental ativada indevidamente'
    for entrada in ('main.py','pixelrush_qa_render_v327729.py',
                    'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py'):
        assert 'pixelrush_qa_rolling_v327740' not in Path(entrada).read_text('utf8'), (
            'compositor experimental conectado indevidamente: '+entrada)
    for entrada in ('main.py','pixelrush_qa_render_v327729.py',
                    'pixelrush_qa_camera_v327733.py',
                    'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py'):
        assert 'pixelrush_qa_crop_native_v327741' not in Path(entrada).read_text('utf8'), (
            'native C fora de prototipo ativado no jogo: '+entrada)
    assert 'qa_native/camera_crop_native_v327741.c' in PINNED
    assert 'tests/test_qa_crop_native_v327741.py' in PINNED
    assert 'tests/test_qa_gles_real_v327741.py' in PINNED
    jogo_qa=Path('PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
    assert 'pixelrush_qa_gles_pbo_v327742' not in jogo_qa
    assert 'pixelrush_qa_gles_present_v327735' not in jogo_qa
    assert 'pixelrush_qa_camera_native_auto_v327742' not in jogo_qa
    assert 'pixelrush_qa_camera_native_auto_v327742' in Path('pixelrush_qa_render_v327729.py').read_text('utf8')
    assert 'pixelrush_qa_scroll_auto_v327742' in Path('pixelrush_qa_render_v327729.py').read_text('utf8')
    io=Path('pixelrush_qa_android_v327728.py').read_text('utf8')
    assert 'pixelrush_qa_v327742' in io
    assert 'apresentacao_swap' in io
    assert 'salvar(esperar=False)' in io
    assert 'v3.277.42-QA-ANDROID-RC' in Path('VERSAO_ATUAL.txt').read_text('utf8')
    workflow=Path('.github/workflows/qa-apk-debug-v327742.yml').read_text('utf8')
    for check in ('refs/heads/qa/android-full-performance-v3.277.42',
                  'tests/test_qa_full_performance_v327737.py',
                  'qa_preflight_v327742.py','tests/test_qa_perf_v327738.py',
                  'tests/test_qa_camera_city_v327739.py',
                  'qa_benchmark_camera_world_v327739.py',
                  'tests/test_qa_rolling_camera_v327740.py',
                  'qa_benchmark_persistent_camera_v327740.py',
                  'tests/test_qa_crop_native_v327741.py',
                  'qa_benchmark_neon_gles_v327741.py',
                  'buildozer -v android debug',
                  'buildozer -v android debug',
                  'android_debug_audit.py apk'):
        assert check in workflow,'workflow incompleto: '+check
    assert 'android.add_libs_arm64_v8a' in spec, 'lib ARM64 nao incluida no Buildozer'
    assert 'qa_native/libpixelrush_camera_crop_v327741.so' in spec['android.add_libs_arm64_v8a']
    for marker in ('tests/test_qa_20_integrated_v327742.py',
                   'tests/test_qa_scroll_auto_v327742.py',
                   'qa_benchmark_all32_v327742.py',
                   'tests/test_qa_modular_batch_v327742.py',
                   'qa_native/libpixelrush_camera_crop_v327741.so',
                   'Compilar biblioteca C/NEON antes do APK'):
        # O ultimo gate verifica a etapa cujo nome explicita o empacotamento.
        if marker=='Compilar biblioteca C/NEON antes do APK':
            assert 'Preparar NDK r28c e compilar biblioteca C/NEON antes do APK' in workflow
        else:
            assert marker in workflow,'gate 32 ausente: '+marker
    assert 'buildozer -v android release' not in workflow
    for path in ('pixelrush_world_v3130.py','pixelrush_cenarios_v398.py',
                 'pixelrush_qa_async_export_v327737.py',
                 'tests/test_qa_full_performance_v327737.py',
                 'tests/test_qa_perf_v327738.py',
                 'pixelrush_qa_alpha_blit_v327731.py',
                 'pixelrush_city2_v3118.py',
                 'tests/test_qa_camera_city_v327739.py',
                 '.github/scripts/qa_benchmark_camera_world_v327739.py',
                 'pixelrush_qa_rolling_v327740.py',
                 'tests/test_qa_rolling_camera_v327740.py',
                 '.github/scripts/qa_benchmark_persistent_camera_v327740.py',
                 'pixelrush_qa_crop_native_v327741.py',
                 'tests/test_qa_crop_native_v327741.py',
                 'tests/test_qa_gles_real_v327741.py',
                 '.github/scripts/qa_benchmark_neon_gles_v327741.py',
                 'pixelrush_qa_performance_integrated_v327742.py',
                 'pixelrush_qa_camera_native_auto_v327742.py',
                 'pixelrush_qa_scroll_auto_v327742.py',
                 'pixelrush_qa_gles_pbo_v327742.py',
                 'tests/test_qa_20_integrated_v327742.py',
                 'tests/test_qa_scroll_auto_v327742.py',
                 'tests/test_qa_gles_pbo_v327742.py',
                 '.github/scripts/qa_benchmark_all32_v327742.py',
                 'pixelrush_biomes2_v3126.py',
                 'tests/test_qa_modular_batch_v327742.py'):
        ast.parse(Path(path).read_text('utf8'),filename=path)
    return {
        'resultado':'APROVADO_GATES_ESTATICOS_APENAS',
        'versao':'v3.277.42-QA','modo':'APK_DEBUG_ARM64',
        'pinned_sha':len(PINNED),'arquivos_protegidos':protegidos,
        'assets_android_visual':len(ANDROID_VISUAL_ASSETS),
        'gpu_experimental_ativada':False,'fps_android_homologado':False,
        'apk_compilado':False,'aab_compilado':False,
    }


if __name__=='__main__':
    resultado=checar()
    Path('preflight-qa-v327742.json').write_text(
        json.dumps(resultado,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(resultado,indent=2,ensure_ascii=False))
