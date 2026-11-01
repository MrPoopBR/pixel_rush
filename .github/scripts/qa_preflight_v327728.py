#!/usr/bin/env python3
"""Gate independente do APK QA; nao flexibiliza a auditoria RC/AAB legada."""
import configparser
import hashlib
import json
from pathlib import Path
from android_debug_audit import EXPECTED_BLOBS, ANDROID_VISUAL_ASSETS, EXPECTED_CONFIG, REQUIRED_EXTENSIONS


def blob_sha(arquivo):
    b = Path(arquivo).read_bytes()
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def preflight():
    conf = configparser.ConfigParser(interpolation=None)
    assert conf.read('buildozer.spec'), 'spec ausente'
    spec = conf['app']
    esperado = dict(EXPECTED_CONFIG)
    esperado.update({'version': '3.277.28', 'android.numeric_version': '327728'})
    for chave, valor in esperado.items():
        assert spec.get(chave, '').strip() == valor, f'{chave} nao corresponde ao QA esperado'
    assert set(REQUIRED_EXTENSIONS) <= set(s.strip() for s in spec['source.include_exts'].split(','))
    assert {'pygame-ce', 'numpy', 'python3==3.12.12', 'hostpython3==3.12.12'} <= set(s.strip() for s in spec['requirements'].split(','))
    for caminho, sha in EXPECTED_BLOBS.items():
        if caminho not in {'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py', 'main.py', 'VERSAO_ATUAL.txt'}:
            assert blob_sha(caminho) == sha, f'original protegido mudou: {caminho}'
    for caminho, sha in ANDROID_VISUAL_ASSETS.items():
        assert hashlib.sha256(Path(caminho).read_bytes()).hexdigest() == sha, f'asset protegido mudou: {caminho}'
    jogo = Path('PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
    qa_bloco = '''        # Somente rótulo de telemetria: replay não executa a simulação da corrida.
        # Fisica, eventos, sorteio, renderizacao e replay permanecem intocados.
        _qa_estado = ("GAMEOVER_REPLAY_QA" if
                      estado == "GAMEOVER" and
                      (replay_morte.ativo or
                       (not replay_morte.congelado and bool(replay_morte.buffer)))
                      else estado)
        _pro_inicio(_qa_estado, cenario_atual)
        perf_biomas.iniciar(estado, cenario_atual)'''
    original = '''        _pro_inicio(estado, cenario_atual)
        perf_biomas.iniciar(estado, cenario_atual)'''
    assert jogo.count(qa_bloco) == 1, 'bloco replay QA divergente'
    restaurado = jogo.replace(qa_bloco, original).replace('v3.277.28-QA-ANDROID-RC', 'v3.277.27-PROD-ANDROID-RC')
    b = restaurado.encode('utf8')
    sha_restaurado = hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
    assert sha_restaurado == EXPECTED_BLOBS['PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py'], 'fonte original de jogo diverge alem do QA'
    main = Path('main.py').read_text('utf8')
    assert main.count("    os.environ['PIXELRUSH_QA_ANDROID'] = '1'\n") == 1
    assert 'v3.277.28-QA-ANDROID-RC' in Path('VERSAO_ATUAL.txt').read_text('utf8')
    assert Path('pixelrush_qa_android_v327728.py').is_file()
    assert Path('pixelrush_profiler_v3204.py').is_file()
    return {'resultado': 'APROVADO', 'versao': '3.277.28-QA', 'modo_build': 'apk-debug',
            'jogo_original_intacto_exceto_versao_e_rotulo_replay': True,
            'assets_originais_preservados': len(ANDROID_VISUAL_ASSETS),
            'blobs_protegidos_preservados': len(EXPECTED_BLOBS) - 3}


if __name__ == '__main__':
    resultado = preflight()
    Path('preflight-qa-v327728.json').write_text(json.dumps(resultado, indent=2), encoding='utf8')
    print(json.dumps(resultado, ensure_ascii=False, indent=2))