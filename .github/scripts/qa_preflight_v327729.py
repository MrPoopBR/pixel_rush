#!/usr/bin/env python3
"""Gate estrito v3.277.29: arquivos de jogo restauraveis EXATAMENTE ao QA anterior."""
import configparser, hashlib, json
from pathlib import Path
from android_debug_audit import EXPECTED_BLOBS, ANDROID_VISUAL_ASSETS, EXPECTED_CONFIG, REQUIRED_EXTENSIONS

BASE = {"PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py":"f5b962f5b9862f71039256faebc0b30af99bd8a8","main.py":"d9dfd4ba04550d33d1482db70d98f555fcd22f85","pixelrush_qa_android_v327728.py":"741cfefb86ce0601711b7e6632740e096370376d"}
REVERSO_JOGO = [["        _qa_estado = (\"JOGANDO_TUTORIAL_QA\" if\n                      estado == \"JOGANDO\" and tutorial_corrida and tutorial_corrida.ativo\n                      else \"GAMEOVER_REPLAY_QA\" if\n                      estado == \"GAMEOVER\" and\n                      (replay_morte.ativo or\n                       (not replay_morte.congelado and bool(replay_morte.buffer)))\n                      else estado)","        _qa_estado = (\"GAMEOVER_REPLAY_QA\" if\n                      estado == \"GAMEOVER\" and\n                      (replay_morte.ativo or\n                       (not replay_morte.congelado and bool(replay_morte.buffer)))\n                      else estado)"],["                    _pro_sub_inicio(\"profundidade_fundo\")\n                    profundidade_cinematografica(display_surface, cenario_atual, peso_noite,\n                                                  modo_grafico_leve(dados))","                    profundidade_cinematografica(display_surface, cenario_atual, peso_noite,\n                                                  modo_grafico_leve(dados))"],["                                                 clima.tipo)\n                    _pro_sub_fim()\n                    # Nuvens de clima sao fundo do mundo","                                                 clima.tipo)\n                    # Nuvens de clima sao fundo do mundo"],["        _pro_sub_inicio('camera_gamefeel')\n        tela_gamefeel = (display_surface if dados.get('acess_reduzir_efeitos', False)\n                          else gamefeel.acabamento_camera(display_surface, estado == \"JOGANDO\"))\n        _pro_sub_fim()","        tela_gamefeel = (display_surface if dados.get('acess_reduzir_efeitos', False)\n                          else gamefeel.acabamento_camera(display_surface, estado == \"JOGANDO\"))"],["            _pro_sub_inicio(\"camera_smoothscale\")\n            tela_gamefeel = camera_cinematica.aplicar(\n                tela_gamefeel, jogador, vel_jogo,\n                cenas_epicas.momento(bg_parallax.world.travel), True)\n            _pro_sub_fim()","            tela_gamefeel = camera_cinematica.aplicar(\n                tela_gamefeel, jogador, vel_jogo,\n                cenas_epicas.momento(bg_parallax.world.travel), True)"],["v3.277.29-QA-ANDROID-RC","v3.277.28-QA-ANDROID-RC"]]
REVERSO_QA = [["    'mundo_2_5d', 'sprites_render', 'clima_render',\n    'mundo_composicao_interna', 'profundidade_fundo',\n    'camera_smoothscale', 'camera_gamefeel',","    'mundo_2_5d', 'sprites_render', 'clima_render',"],["        modo = ('tutorial' if estado == 'JOGANDO_TUTORIAL_QA' else\n                'corrida_normal' if estado == 'JOGANDO' else\n                'replay' if estado == 'GAMEOVER_REPLAY_QA' else 'outros')","        modo = 'corrida_normal' if estado == 'JOGANDO' else 'replay' if estado == 'GAMEOVER_REPLAY_QA' else 'outros'"]]
REVERTER_MAIN = ("    mostrar_abertura()\n    # Instala exclusivamente o compositor QA, sem tocar o entrypoint de producao.\n    from pixelrush_qa_render_v327729 import instalar as instalar_render_qa\n    instalar_render_qa()\n    _executar_jogo()", "    mostrar_abertura()\n    _executar_jogo()")

def blob_sha(conteudo):
    b = conteudo.encode('utf-8')
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()

def reverter(conteudo, regras):
    for novo, original in regras:
        assert conteudo.count(novo) == 1, 'patch esperado ausente, duplicado ou divergente'
        conteudo = conteudo.replace(novo, original)
    return conteudo

def executar():
    conf=configparser.ConfigParser(interpolation=None)
    assert conf.read('buildozer.spec')
    app=conf['app']
    cfg=dict(EXPECTED_CONFIG)
    cfg.update({'version':'3.277.29','android.numeric_version':'327729'})
    for k,v in cfg.items():
        assert app.get(k, '').strip()==v, f'spec divergente: {k}'
    assert set(REQUIRED_EXTENSIONS) <= set(x.strip() for x in app['source.include_exts'].split(','))
    for arquivo,sha in EXPECTED_BLOBS.items():
        if arquivo not in ('PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py','main.py','VERSAO_ATUAL.txt'):
            assert hashlib.sha1(b'blob '+str(len(Path(arquivo).read_bytes())).encode()+b'\0'+Path(arquivo).read_bytes()).hexdigest()==sha, arquivo
    for arquivo,sha in ANDROID_VISUAL_ASSETS.items():
        assert hashlib.sha256(Path(arquivo).read_bytes()).hexdigest()==sha, arquivo
    assert 'v3.277.29-QA-ANDROID-RC' in Path('VERSAO_ATUAL.txt').read_text('utf8')
    for arquivo, regras in (
        ('PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py', REVERSO_JOGO),
        ('main.py', [REVERTER_MAIN]),
        ('pixelrush_qa_android_v327728.py', REVERSO_QA)):
        codigo=Path(arquivo).read_text('utf8')
        restaurado=reverter(codigo,regras)
        if arquivo == 'pixelrush_qa_android_v327728.py':
            restaurado=restaurado.replace('pixelrush_qa_v327729.json','pixelrush_qa_v327728.json')
            restaurado=restaurado.replace('pixelrush_qa_frames_v327729.csv','pixelrush_qa_frames_v327728.csv')
        assert blob_sha(restaurado)==BASE[arquivo], 'arquivo divergente fora do escopo: '+arquivo
    qa=Path('pixelrush_qa_render_v327729.py').read_text('utf8')
    assert 'def instalar():' in qa and 'def restaurar_para_teste():' in qa
    wf=Path('.github/workflows/qa-apk-debug-v327729.yml').read_text('utf8')
    assert 'buildozer -v android debug' in wf
    assert 'buildozer -v android release' not in wf
    assert "refs/heads/qa/android-render-v3.277.29" in wf
    assert '.github/scripts/test_qa_render_v327729.py' in wf
    return {'resultado':'APROVADO','versao':'3.277.29-QA',
        'arquivos_protegidos_preservados':len(EXPECTED_BLOBS)-3,
        'assets_visuais_identicos':len(ANDROID_VISUAL_ASSETS),
        'fontes_QA_base_restauraveis':len(BASE),
        'so_apk_debug':True}

if __name__ == '__main__':
    resultado=executar()
    Path('preflight-qa-v327729.json').write_text(json.dumps(resultado,indent=2),encoding='utf8')
    print(json.dumps(resultado,ensure_ascii=False,indent=2))
