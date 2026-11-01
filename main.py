"""Entrada SDL2 experimental para empacotamento Android. Nao publicada."""
from pathlib import Path
import runpy
import os


def _executar_jogo():
    origem = Path(__file__).resolve().parent / 'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py'
    # O python-for-android pode distribuir apenas bytecode compilado (.pyc).
    if not origem.is_file() and origem.with_suffix('.pyc').is_file():
        origem = origem.with_suffix('.pyc')
    runpy.run_path(str(origem), run_name='__main__')


if __name__ == '__main__':
    from pixelrush_android_abertura_v327712 import mostrar_abertura
    # QA isolado: ativar apenas neste APK (nunca no ramo de producao).
    os.environ['PIXELRUSH_QA_ANDROID'] = '1'
    mostrar_abertura()
    # Instala exclusivamente o compositor QA, sem tocar o entrypoint de producao.
    from pixelrush_qa_render_v327729 import instalar as instalar_render_qa
    instalar_render_qa()
    _executar_jogo()
