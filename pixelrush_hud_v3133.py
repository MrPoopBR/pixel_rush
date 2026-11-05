# -*- coding: utf-8 -*-
"""Compatibilidade Android/QA: codigo original agora em src/pixelrush/ui/hud/legacy_v3133.py.
Import resolve uma vez; sem chamadas extras em cada quadro.
"""
import importlib as _importlib
import sys as _sys
_sys.modules[__name__] = _importlib.import_module("src.pixelrush.ui.hud.legacy_v3133")
