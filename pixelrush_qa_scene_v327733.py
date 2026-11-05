# -*- coding: utf-8 -*-
"""Compatibilidade de import QA R26: implementação canônica em src/pixelrush/rendering/scene_qa_v327733.py.
Preserva estado global/flags e nome histórico para Android sem cópias vivas.
"""
import importlib as _importlib
import sys as _sys
_sys.modules[__name__] = _importlib.import_module("src.pixelrush.rendering.scene_qa_v327733")
