# -*- coding: utf-8 -*-
"""Adaptador de compatibilidade para o modulo real em src/pixelrush/rendering/sky_v3233.py.
A API e o objeto de modulo permanecem unicos (nao duplicar estado).
Nao remover ate a homologacao de imports, CI e empacotamento Android.
"""
import importlib as _importlib
import sys as _sys
_sys.modules[__name__] = _importlib.import_module("src.pixelrush.rendering.sky_v3233")
