#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.277.47: gate de integridade, visual, fisica e build debug isolado."""
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
    'pixelrush_qa_render_v327729.py':'ab94a261f1aee37459872ed0df0477073a515ca6',
    'pixelrush_qa_gles_present_v327735.py':'6ebb9bd065f5168bbe18dd43398cc0df1116dba3',
    'pixelrush_qa_gles_exact_v327736.py':'cd8961206cceed86bb392f626c77d68083782739',
    'pixelrush_world_v3130.py':'7ca66b28898cd138538831c5bce1133ea961763f',
    'pixelrush_cenarios_v398.py':'2d9b9f22fd88d2f370ae9216ee3ebeb28a07098e',
    'pixelrush_profissional_v3108.py':'a4a93636d279ef7076d96d5f8fd441e4702642f3',
    'pixelrush_fase_b_visuais_v3272.py':'1d8af98523a683aba9d35e0fa736a74e6345ad92',
    'pixelrush_fase_b_visuais_v3274.py':'99f786af7eacd863f6910d98c4ac81bbb99db1ee',
    'pixelrush_qa_android_v327728.py':'fa69158dff39a452c3fded8b0676d88dd6d21aad',
    'pixelrush_qa_ultraleve_v327730.py':'1ab13d44739023b50a602aee815151e9003ec7ab',
    'pixelrush_qa_scene_v327733.py':'493a8b967ff235141c4f492eae5d8486617286e2',
    'pixelrush_qa_camera_v327733.py':'6186a1cef5fe79f0d9e954c6d1cd6a5478588c5b',
    'pixelrush_qa_gles_gate_v327734.py':'462b3e8163cb4495fa8d20131b400f8f7a3fce1e',
    'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py':'e05cf0f7bb2a140d8a67e5d9cd252fc0873740a6',
    'buildozer.spec':'03de5181f00a3caa1029b30d44bd425f9621baec',
    'pixelrush_qa_async_export_v327737.py':'0995f9f16b8298ea90418eab048d093f082d3985',
    'pixelrush_qa_alpha_blit_v327731.py':'fefb6f0f32dae61cdc8368ced51da2234646fa89',
    'tests/test_qa_perf_v327738.py':'2ba50cb13af7021d2af102c1865297cd278e8489',
    'pixelrush_city2_v3118.py':'af3605f1824be478ae3fd6cc52f27a56b2057261',
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
    'pixelrush_qa_performance_integrated_v327742.py':'07dffa03467bcec9e66c6e6063c6417e3f1e706f',
    'pixelrush_qa_camera_native_auto_v327742.py':'211f3b313c9a39c0e961a169de9b97c8a2c519b1',
    'pixelrush_qa_scroll_auto_v327742.py':'1446889db9e6cbc4c85ce9ea4de86fb345d89319',
    'pixelrush_qa_gles_pbo_v327742.py':'3f724b9504f0693390609bd2da8063482a9cd9f6',
    'tests/test_qa_20_integrated_v327742.py':'1f330871d857b20e236d99b7dad832772880324d',
    'tests/test_qa_scroll_auto_v327742.py':'47d7598f07d8857369f11ebabc4edb8f68319f7e',
    'tests/test_qa_gles_pbo_v327742.py':'6b05e9bcda8e7e87a475801f6f07d478492ecb02',
    '.github/scripts/qa_benchmark_all32_v327742.py':'7b1de8e33b3bd1a359f0bffe336f9b6a29107e21',
    'pixelrush_biomes2_v3126.py':'06abc1cff35dc32db15d732f3e2d76888b240787',
    'tests/test_qa_modular_batch_v327742.py':'12999ec4f632bc0d093e87187751f6e036961fff',
    'tests/test_qa_city_clouds_v327742.py':'4a028b9f28693d7d5d57d4b966a230b52e75de8e',
    'tests/test_qa_full_performance_v327737.py':'716033c6571f0e0c585dd1e4f9c1beaa05f117c9',
    'pixelrush_qa_snapshot_v327743.py':'611355ac5bee960c45a930815f5afedf98e8226f',
    'tests/test_qa_safe_performance_v327743.py':'817e20570739a724cc4e5281bf212e59dc89f2f9',
    'tests/test_qa_frame_completo_v327743.py':'76f701766360e36b924a2e009b60ba10d4c0fe0b',
    '.github/scripts/qa_benchmark_frame_completo_v327743.py':'78a8cd5e10ed89959b55d93f026e243b7f175a10',
    'tests/test_qa_camera_scene_v327733.py':'f90d5a4ea2d726201374432dba47f11bdba0b806',
    'tests/test_qa_performance_full_v327732.py':'a3a1860e60f05efb3c7a8281cda2c6566053abb6',
    '.github/scripts/test_qa_android_v327728.py':'810f3bd2e4a7604400b3e127ab1d92e2d239145c',
    '.github/workflows/qa-offline-v327743.yml':'9086836d15c5ccc266c0003d672575a5169ecc38',
    'QA_CHANGELOG_v327743.md':'a12e5aa320082cb292ee89ee36d28a29440f42e8',
    'pixelrush_qa_modular_batch_v327744.py':'a817fc6e8bf2b8baca19cbccac98064d355d7796',
    'pixelrush_qa_audit_offline_v327744.py':'d26dad42cc360b6815eeab0d5ecfe304ab00f86f',
    'tests/test_qa_render_real_v327744.py':'67a1ba71b529b97da97de5af76025590ce89f6a3',
    '.github/scripts/qa_benchmark_world_real_v327744.py':'61b4389e3a535d8f1ecc24b0a01a5beecaa0b567',
    '.github/workflows/qa-offline-v327744.yml':'8da46eb2d9d887305477ea1a595a6713bc9a45f3',
    'QA_CHANGELOG_v327744.md':'c3b375b9e365a05ce755867460fee301f98babab',
    'QA_AUDITORIA_MEMORIA_RENDER_v327744.md':'6d89a644b75c8f7dac6093c7e78dd686991d3acb',
    'tests/test_qa_fifth_memory_v327745.py':'fe82551a87b8319e7eb17cf81ca6c624d06b1c76',
    '.github/scripts/qa_benchmark_fifth_memory_v327745.py':'49d154f61d1d4c86c7aa333dec8aab88306277b3',
    '.github/workflows/qa-offline-v327745.yml':'916ba68ebd6100852d8fde75831da79a11c0ba22',
    'QA_CHANGELOG_v327745.md':'4a7d05a1daa7500b38d400f9d2dfc154511ebdea',
    'QA_AUDITORIA_QUINTO_QUADRO_v327745.md':'7cb8c580529e7184fc3014782f04512893a87272',
    'pixelrush_qa_biome_preheat_v327746.py':'674f3a487083093cb6fdbddd75a9646fb60a49aa',
    'tests/test_qa_preheat_buffer_v327746.py':'18ca6d3acdea24d5bf89c6dab0d67995af77fc1f',
    'tests/test_qa_buffer_full_v327746.py':'5d99d6d2ac982d713914328308f684fc7c5b5369',
    '.github/scripts/qa_benchmark_preheat_buffer_v327746.py':'db79235dda5d4a4f07bae4bc8a0c7f2887d0d890',
    'QA_TRACKER_32_v327746.md':'3ecd954bc340848c04d29e5abb15e305d23af26c',
    'QA_CHANGELOG_v327746.md':'f76ec55663750a2b5b5814769fc7b68ba9ff3b7e',
    '.github/workflows/qa-offline-v327746.yml':'9202e64e5fbba9d21a5479a42aed42f76071f391',
    'pixelrush_qa_atlas_io_v327747.py':'a53f27ac7620a9b134d59c36ee3148e80bfc8717',
    'pixelrush_qa_backend_gate_v327747.py':'d8b04d2c3359bbb2c7ef2af02bf665802c50ccc2',
    'tests/test_qa_atlas_io_v327747.py':'83f1df5cb3dad3c8a32b6cb75d61501d9d311b8c',
    'tests/test_qa_backend_gate_v327747.py':'6d9f55292928a9dc32aec88501905312296f872e',
    '.github/scripts/qa_buffer_stage_v327747.py':'c9802f38ca17ac85c2da19be04acb023025587e3',
    '.github/workflows/qa-offline-v327747.yml':'df53a059efb7e8f5e365f8f035f85d641c52b2b6',
    'QA_TRACKER_32_v327747.md':'e4164a1fe57115d9fcc8451632ad863a0e919aab',
    'QA_CHANGELOG_v327747.md':'a4e930bf67dc243456d3222b96612d2a8c7be296',
}


def checar():
    conf=configparser.ConfigParser(interpolation=None)
    assert conf.read('buildozer.spec'), 'buildozer.spec ausente'
    spec=conf['app']
    exp=dict(EXPECTED_CONFIG)
    exp.update({'version':'3.277.47','android.numeric_version':'327747'})
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
    assert 'VERSAO = "v3.277.47-QA-ANDROID-RC"' in jogo
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
    assert 'pixelrush_qa_v327747' in io
    assert 'apresentacao_swap' in io
    assert 'salvar(esperar=False)' in io
    assert 'v3.277.47-QA-ANDROID-RC' in Path('VERSAO_ATUAL.txt').read_text('utf8')
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
                   'tests/test_qa_city_clouds_v327742.py',
                   'qa_native/libpixelrush_camera_crop_v327741.so',
                   'Compilar biblioteca C/NEON antes do APK'):
        # O ultimo gate verifica a etapa cujo nome explicita o empacotamento.
        if marker=='Compilar biblioteca C/NEON antes do APK':
            assert 'Preparar NDK r28c e compilar biblioteca C/NEON antes do APK' in workflow
        else:
            assert marker in workflow,'gate 32 ausente: '+marker
    assert 'buildozer -v android release' not in workflow
    offline47=Path('.github/workflows/qa-offline-v327747.yml').read_text('utf8')
    assert 'qa/android-full-performance-v3.277.47' in offline47
    for gate in ('qa_preflight_v327747.py','test_qa_atlas_io_v327747.py',
                 'test_qa_backend_gate_v327747.py','qa_buffer_stage_v327747.py'):
        assert gate in offline47
    for banned in ('buildozer -v android','gradle assemble','adb shell'):
        assert banned not in offline47.lower()
    assert "preaquecer_arquivos_fora_do_jogo" in Path(
        'pixelrush_qa_atlas_io_v327747.py').read_text('utf8')
    assert 'instalar_no_boot_qa' in Path(
        'pixelrush_qa_render_v327729.py').read_text('utf8')
    assert 'fps_comprovadamente_melhor' in Path(
        'pixelrush_qa_backend_gate_v327747.py').read_text('utf8')
    assert 'CacheFundoUltraQA(periodo=5)' in jogo
    offline46=Path('.github/workflows/qa-offline-v327746.yml').read_text('utf8')
    assert 'qa/android-full-performance-v3.277.46' in offline46
    for marker46 in ('qa_preflight_v327746.py',
                     'test_qa_preheat_buffer_v327746.py',
                     'test_qa_buffer_full_v327746.py',
                     'qa_benchmark_preheat_buffer_v327746.py'):
        assert marker46 in offline46
    for forbidden in ('buildozer -v android','gradle assemble','adb shell'):
        assert forbidden not in offline46.lower()
    from pixelrush_qa_biome_preheat_v327746 import diagnostico
    assert diagnostico()['preparacao_automatica_na_corrida'] is False
    assert 'world_prod_v32777' in Path(
        'pixelrush_qa_biome_preheat_v327746.py').read_text('utf8')
    assert 'CacheFundoUltraQA(periodo=5)' in jogo
    offline45=Path('.github/workflows/qa-offline-v327745.yml').read_text('utf8')
    assert 'qa/android-full-performance-v3.277.45' in offline45
    for marker45 in ('qa_preflight_v327745.py', 'tests/test_qa_fifth_memory_v327745.py',
                     'qa_benchmark_fifth_memory_v327745.py',
                     'qa-benchmark-quinto-memoria-v327745.json'):
        assert marker45 in offline45
    for forbidden45 in ('buildozer -v android','gradle assemble','adb shell'):
        assert forbidden45 not in offline45.lower()
    assert "CacheFundoUltraQA(periodo=5)" in jogo
    assert "self._idade >= self.periodo - 1" in Path(
        'pixelrush_qa_ultraleve_v327730.py').read_text('utf8')
    assert "_LAST_STATUS['frames']%180==0" in Path(
        'pixelrush_qa_performance_integrated_v327742.py').read_text('utf8')
    assert "world.biome!='cidade'" in Path(
        'pixelrush_qa_performance_integrated_v327742.py').read_text('utf8')
    offline44=Path('.github/workflows/qa-offline-v327744.yml').read_text('utf8')
    assert 'qa/android-full-performance-v3.277.44' in offline44
    assert "PIXELRUSH_QA_MODULAR_BATCH: '0'" in offline44
    for marker44 in ('qa_preflight_v327744.py',
                     'tests/test_qa_render_real_v327744.py',
                     'qa_benchmark_world_real_v327744.py',
                     'qa-benchmark-world-real-v327744.json'):
        assert marker44 in offline44, 'novo CI offline incompleto: '+marker44
    for forbidden44 in ('buildozer -v android', 'gradle assemble', 'adb shell'):
        assert forbidden44 not in offline44.lower(), 'tentativa Android: '+forbidden44
    assert "PIXELRUSH_QA_MODULAR_BATCH','0'" in Path(
        'pixelrush_qa_modular_batch_v327744.py').read_text('utf8')
    assert "world.biome!='cidade'" in Path(
        'pixelrush_qa_performance_integrated_v327742.py').read_text('utf8')
    assert 'cache_cleanup_p95_ms' in Path(
        'pixelrush_qa_performance_integrated_v327742.py').read_text('utf8')
    assert 'pixelrush_qa_modular_batch_v327744' in Path(
        'pixelrush_qa_render_v327729.py').read_text('utf8')
    offline=Path('.github/workflows/qa-offline-v327743.yml').read_text('utf8')
    assert 'qa/android-full-performance-v3.277.43' in offline
    assert 'buildozer -v android' not in offline
    assert 'gradle ' not in offline.lower()
    assert 'adb ' not in offline.lower()
    for esperado in ('qa_preflight_v327743.py',
                     'tests/test_qa_safe_performance_v327743.py',
                     'tests/test_qa_frame_completo_v327743.py',
                     'qa_benchmark_frame_completo_v327743.py'):
        assert esperado in offline
    assert "os.environ.get('PIXELRUSH_QA_SCROLL_AUTO','0')" in Path(
        'pixelrush_qa_scroll_auto_v327742.py').read_text('utf8')
    assert 'if key not in ativos' in Path(
        'pixelrush_qa_performance_integrated_v327742.py').read_text('utf8')
    assert "PIXELRUSH_QA_CLOUD_CACHE','0'" in Path(
        'pixelrush_city2_v3118.py').read_text('utf8')
    assert 'CapturaParceladaQA' in io
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
                 'tests/test_qa_modular_batch_v327742.py',
                 'tests/test_qa_city_clouds_v327742.py',
                 'pixelrush_qa_snapshot_v327743.py',
                 'tests/test_qa_safe_performance_v327743.py',
                 'tests/test_qa_frame_completo_v327743.py',
                 '.github/scripts/qa_benchmark_frame_completo_v327743.py',
                 'tests/test_qa_camera_scene_v327733.py',
                 'tests/test_qa_performance_full_v327732.py',
                 '.github/scripts/test_qa_android_v327728.py',
                 'pixelrush_qa_modular_batch_v327744.py',
                 'pixelrush_qa_audit_offline_v327744.py',
                 'tests/test_qa_render_real_v327744.py',
                 '.github/scripts/qa_benchmark_world_real_v327744.py',
                 'tests/test_qa_fifth_memory_v327745.py',
                 '.github/scripts/qa_benchmark_fifth_memory_v327745.py',
                 'pixelrush_qa_biome_preheat_v327746.py',
                 'tests/test_qa_preheat_buffer_v327746.py',
                 'tests/test_qa_buffer_full_v327746.py',
                 '.github/scripts/qa_benchmark_preheat_buffer_v327746.py',
                 'pixelrush_qa_atlas_io_v327747.py',
                 'pixelrush_qa_backend_gate_v327747.py',
                 'tests/test_qa_atlas_io_v327747.py',
                 'tests/test_qa_backend_gate_v327747.py',
                 '.github/scripts/qa_buffer_stage_v327747.py'):
        ast.parse(Path(path).read_text('utf8'),filename=path)
    return {
        'resultado':'APROVADO_GATES_ESTATICOS_APENAS',
        'versao':'v3.277.47-QA','modo':'QA_OFFLINE_PYGAME_SEM_APK',
        'pinned_sha':len(PINNED),'arquivos_protegidos':protegidos,
        'assets_android_visual':len(ANDROID_VISUAL_ASSETS),
        'gpu_experimental_ativada':False,'fps_android_homologado':False,
        'apk_compilado':False,'aab_compilado':False,
    }


if __name__=='__main__':
    resultado=checar()
    Path('preflight-qa-v327747.json').write_text(
        json.dumps(resultado,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(resultado,indent=2,ensure_ascii=False))
