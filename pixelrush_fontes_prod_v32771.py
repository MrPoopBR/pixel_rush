# -*- coding: utf-8 -*-
"""Fallback local para glyphs Unicode; nenhuma fonte adicional é distribuída.

Nos sistemas com fontes CJK completas (inclusive Android), prioriza a fonte do
sistema. Mantém os subsets já presentes no próprio projeto como fallback.
Fontes cacheadas uma vez por idioma/tamanho, fora do loop de desenho.
"""
from functools import lru_cache
from pathlib import Path
import os
import sys
import pygame
from pixelrush_traducoes_v3247 import fonte_unicode as _fonte_integrada

_NOMES = {
    'ja_JP': ('noto sans cjk jp', 'yu gothic', 'meiryo', 'ms gothic'),
    'zh_CN': ('noto sans cjk sc', 'microsoft yahei', 'simsun'),
    'ko_KR': ('noto sans cjk kr', 'malgun gothic', 'batang'),
    'hi_IN': ('noto sans devanagari', 'mangal', 'nirmala ui'),
}
_ANDROID = {
    'ja_JP': ('NotoSansCJK-Regular.ttc', 'NotoSansJP-Regular.otf'),
    'zh_CN': ('NotoSansCJK-Regular.ttc', 'NotoSansSC-Regular.otf'),
    'ko_KR': ('NotoSansCJK-Regular.ttc', 'NotoSansKR-Regular.otf'),
    'hi_IN': ('NotoSansDevanagari-Regular.ttf', 'NotoSansDevanagariUI-Regular.ttf'),
}

@lru_cache(maxsize=16)
def _caminho_sistema(codigo):
    for nome in _ANDROID.get(codigo, ()):
        caminho = Path('/system/fonts') / nome
        if caminho.is_file():
            return str(caminho)
    # match_font() usa fc-list no Unix; o Android/MEmu bloqueia a execucao.
    # Conservar fontes nativas existentes ou o subset integrado no projeto.
    if sys.platform == 'android' or 'ANDROID_ARGUMENT' in os.environ:
        return None
    for nome in _NOMES.get(codigo, ()):
        resultado = pygame.font.match_font(nome)
        if resultado:
            return resultado
    return None

@lru_cache(maxsize=40)
def fonte_unicode(codigo, tamanho):
    caminho = _caminho_sistema(codigo)
    if caminho:
        try:
            return pygame.font.Font(caminho, tamanho)
        except (OSError, pygame.error):
            pass
    return _fonte_integrada(codigo, tamanho)
