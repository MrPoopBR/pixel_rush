# -*- coding: utf-8 -*-
"""Compatibilidade temporaria: modulo movido sem alterar sua API publica.
Modulo canonico: src/pixelrush/performance/city/cache_budget.py
Nao remover: imports de producao/QA e testes antigos ainda usam este nome.
"""
import importlib as _importlib
import sys as _sys
_sys.modules[__name__] = _importlib.import_module("src.pixelrush.performance.city.cache_budget")
