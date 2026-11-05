# -*- coding: utf-8 -*-
"""Fachada de entrada desktop, sem reescrever o motor monolitico.

O entrypoint Android (main.py) e os caminhos de assets permanecem na raiz.
Somente quando a migracao integral for homologada, este modulo sera o motor.
"""
from pathlib import Path
import runpy


def iniciar_desktop():
    raiz = Path(__file__).resolve().parents[2]
    return runpy.run_path(str(raiz / "JOGAR.py"), run_name="__main__")
