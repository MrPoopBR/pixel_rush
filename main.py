"""Entrada SDL2 experimental para empacotamento Android. Nao publicada."""
from pathlib import Path
import runpy
if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parent / 'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py'),run_name='__main__')
