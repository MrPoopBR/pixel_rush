#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preflight independente v3.277.34: protege assets e release / AAB / DEV."""
import configparser
import hashlib
import json
from pathlib import Path
from android_debug_audit import EXPECTED_BLOBS, ANDROID_VISUAL_ASSETS, EXPECTED_CONFIG, REQUIRED_EXTENSIONS

def gitblob(path):
    content=Path(path).read_bytes()
    return hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()

def executar():
    conf=configparser.ConfigParser(interpolation=None)
    assert conf.read('buildozer.spec')
    app=conf['app']
    exp=dict(EXPECTED_CONFIG)
    exp.update({'version':'3.277.34','android.numeric_version':'327734'})
    for k,v in exp.items():
        assert app.get(k,'').strip()==v, 'buildozer divergente: '+k
    assert set(REQUIRED_EXTENSIONS) <= set(k.strip() for k in app['source.include_exts'].split(','))
    assert {'pygame-ce','numpy','python3==3.12.12','hostpython3==3.12.12'} <= set(x.strip() for x in app['requirements'].split(','))
    protegidos = 0
    for arquivo, sha in EXPECTED_BLOBS.items():
        if arquivo in ('PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py','VERSAO_ATUAL.txt','main.py'):
            continue
        assert gitblob(arquivo)==sha, 'arquivo protegido divergente: '+arquivo
        protegidos+=1
    # Alteracoes permitidas nesta branch experimental. SHA de blob Git
    # evita alteracoes colaterais em jogo, visual ou telemetria.
    expected_qa = {
        'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py': 'c2f29a71c84307c944e41ce56d779ad68b67b2a1',
        'pixelrush_world_v3130.py': '99615c4c866adf75fcf47ae63cb134a333c434ad',
        'pixelrush_profissional_v3108.py': 'a4a93636d279ef7076d96d5f8fd441e4702642f3',
        'pixelrush_fase_b_visuais_v3272.py': '1d8af98523a683aba9d35e0fa736a74e6345ad92',
        'pixelrush_fase_b_visuais_v3274.py': '99f786af7eacd863f6910d98c4ac81bbb99db1ee',
        'pixelrush_qa_android_v327728.py': '37c25b5edab3451fc0259ce2e465ff0a759d5f69',
        'pixelrush_qa_ultraleve_v327730.py': '1ab13d44739023b50a602aee815151e9003ec7ab',
        'pixelrush_qa_scene_v327733.py': '493a8b967ff235141c4f492eae5d8486617286e2',
        'pixelrush_qa_camera_v327733.py': 'da28a0be8567805ff5c8556c2a7d2bbf31fec635',
        'pixelrush_qa_gles_gate_v327734.py': '462b3e8163cb4495fa8d20131b400f8f7a3fce1e',
        '.github/scripts/qa_gles_camera_probe_v327734.py': '5637dc2132c3ff30d34f7f50858a48c0386f5149',
        'tests/test_qa_gles_gate_v327734.py': 'eca73d3c797093da3c363eb3948e24611689ed57',
        'buildozer.spec': '7bd813bc6d33c785817e8c5e3313e766a1dd639c',
    }
    for arquivo,sha in expected_qa.items():
        assert gitblob(arquivo)==sha, 'mudanca QA nao prevista: '+arquivo
    for arquivo, sha in ANDROID_VISUAL_ASSETS.items():
        assert hashlib.sha256(Path(arquivo).read_bytes()).hexdigest()==sha, 'asset visual modificado: '+arquivo
    # Entrypoint e compositor v327729 preservados integralmente.
    assert gitblob('main.py')=='620a3cdcad571168b31c2633b28da94c251b8855'
    assert gitblob('pixelrush_qa_render_v327729.py')=='f488b32c8eeea96204fc56fd746d4f6c3eafaa29'
    codigo=Path('PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf-8')
    assert 'VERSAO = "v3.277.34-QA-ANDROID-RC"' in codigo
    for marker in (
        'MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15',
        'FPS_RENDER = 30 if E_ANDROID else 60',
        'PIXELRUSH_DEV_BUILD = False',
        'CacheFundoUltraQA(periodo=5)',
        'FundoMenusUltraQA(periodo=5)',
        'bg_parallax.draw_chao(display_surface)',
        'cache_fundo_mobile.guardar(',
    ):
        assert marker in codigo, 'invariante indisponivel: '+marker
    i=codigo.index('if cache_fundo_mobile.reusar(')
    j=codigo.index('if estado in ("JOGANDO", "PAUSA") and evento_corrida:',i)
    parte=codigo[i:j]
    assert parte.index('cache_fundo_mobile.guardar(') < parte.index('bg_parallax.draw_chao(display_surface)')
    assert parte.index('bg_parallax.draw_chao(display_surface)') < parte.index('desenhar_clima_premium(')
    modulo=Path('pixelrush_qa_ultraleve_v327730.py')
    assert modulo.is_file()
    assert 'class CacheFundoUltraQA' in modulo.read_text('utf8')
    assert 'class FundoMenusUltraQA' in modulo.read_text('utf8')
    assert 'v3.277.34-QA-ANDROID-RC' in Path('VERSAO_ATUAL.txt').read_text('utf8')
    workflow=Path('.github/workflows/qa-apk-debug-v327734.yml').read_text('utf8')
    assert 'refs/heads/qa/android-gles-gate-v3.277.34' in workflow
    assert 'buildozer -v android debug' in workflow
    assert 'buildozer -v android release' not in workflow
    assert 'buildozer -v android debug' in workflow
    assert '.github/scripts/test_qa_ultraleve_v327730.py' in workflow
    assert 'tests/test_qa_alpha_blit_v327731.py' in workflow
    assert 'tests/test_qa_performance_full_v327732.py' in workflow
    assert 'tests/test_qa_camera_scene_v327733.py' in workflow
    assert 'tests/test_qa_gles_gate_v327734.py' in workflow
    assert 'qa_gles_camera_probe_v327734.py' in workflow
    assert 'qa-gles-gate-v327734.json' in workflow
    assert 'pixelrush_qa_gles_gate_v327734' not in Path('main.py').read_text('utf8')
    gate=Path('pixelrush_qa_gles_gate_v327734.py').read_text('utf8')
    assert "'integracao_aprovada': False" in gate
    assert "'ativa_gpu': False" in gate
    assert 'instalar_cenario_qa()' in Path('pixelrush_qa_render_v327729.py').read_text('utf8')
    assert 'instalar_camera_qa()' in Path('pixelrush_qa_render_v327729.py').read_text('utf8')
    assert Path('tests/test_qa_performance_full_v327732.py').is_file()
    assert Path('pixelrush_qa_alpha_blit_v327731.py').is_file()
    assert 'instalar_alpha_blit_qa()' in Path('pixelrush_qa_render_v327729.py').read_text('utf8')
    return {'resultado':'APROVADO','versao':'3.277.34-QA','protegidos_intactos':protegidos,
            'assets_visuais_intactos':len(ANDROID_VISUAL_ASSETS),'modo':'APK_DEBUG_ARM64',
            'fisica_e_apresentacao_protegidas_por_gates':True}

if __name__=='__main__':
    resultado=executar()
    Path('preflight-qa-v327734.json').write_text(json.dumps(resultado,indent=2),encoding='utf8')
    print(json.dumps(resultado,ensure_ascii=False,indent=2))
