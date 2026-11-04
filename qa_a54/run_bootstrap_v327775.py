# -*- coding: utf-8 -*-
"""Executa testes historicos com bootstrap real da City v3.277.59+.

Testes v755/v741 criavam CityPilotScene diretamente sem instalar
o hook que a engine QA instala. Nao tocar nos testes originais nem no jogo.
"""
import os, runpy, sys
from pathlib import Path
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from pixelrush_qa_city_bootstrap_v327759 import instalar
instalar()
if len(sys.argv)<2:
    raise SystemExit("uso: run_bootstrap_v327775.py tests/<arquivo>.py")
target=Path(sys.argv[1])
if not target.is_file() or not target.resolve().is_relative_to(ROOT/'tests'):
    raise SystemExit('Somente testes existentes no repo sao permitidos')
sys.argv=[str(target)]
runpy.run_path(str(target),run_name='__main__')
