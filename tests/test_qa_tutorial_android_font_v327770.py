# -*- coding: utf-8 -*-
"""QA770: crash Android/MEmu R7 provocado pelo SysFont->fc-list bloqueado.
Extrai a funcao real: nenhuma tela/jogabilidade e inicializada.
"""
import ast
import os
from pathlib import Path
import sys
import unittest
from functools import lru_cache
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import pygame

SOURCE = Path(__file__).resolve().parents[1] / 'pixelrush_tutorial_corrida_v3277.py'

def fonte_do_tutorial():
    tree = ast.parse(SOURCE.read_text(encoding='utf8'))
    func = next(node for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name == '_fonte')
    namespace = {'pygame': pygame, 'os': os, 'sys': sys, 'lru_cache': lru_cache,
                 'ARQUIVOS_FONTES': {'ja_JP': 'subset'},
                 'fonte_unicode': lambda idioma, tam: 'CJK'}
    module = ast.fix_missing_locations(ast.Module(body=[func], type_ignores=[]))
    exec(compile(module, str(SOURCE), 'exec'), namespace)
    return namespace['_fonte']

class AndroidTutorialFontCrash770(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.font.init()

    def test_android_sem_fc_list_mesmo_com_permissionerror(self):
        fonte = fonte_do_tutorial()
        with patch.dict(os.environ, {'ANDROID_ARGUMENT': '/data/user/0/app/files'}), \
             patch.object(pygame.font, 'SysFont',
                          side_effect=PermissionError(13, 'Permission denied', 'fc-list')):
            f = fonte('pt_BR', 20)
        self.assertIsInstance(f, pygame.font.FontType)
        self.assertTrue(f.get_bold())
        self.assertGreater(f.size('PULAR E AGACHAR')[0], 0)

    def test_desktop_preserva_arial_sysfont(self):
        fonte = fonte_do_tutorial()
        with patch.dict(os.environ, {}, clear=True), \
             patch.object(sys, 'platform', 'linux'), \
             patch.object(pygame.font, 'SysFont', return_value='ARIAL') as original:
            self.assertEqual(fonte('pt_BR', 19), 'ARIAL')
            original.assert_called_once_with('arial', 19, bold=True)

    def test_cjk_preserva_fonte_original(self):
        fonte = fonte_do_tutorial()
        with patch.dict(os.environ, {'ANDROID_ARGUMENT': '1'}), \
             patch.object(pygame.font, 'SysFont',
                          side_effect=PermissionError('fc-list')):
            self.assertEqual(fonte('ja_JP', 20), 'CJK')

    def test_android_prioriza_roboto_bold(self):
        fonte = fonte_do_tutorial()
        original = pygame.font.Font
        chamadas = []
        def simular(path, size):
            chamadas.append(path)
            return original(None, size)
        with patch.dict(os.environ, {'ANDROID_ARGUMENT': '1'}), \
             patch.object(pygame.font, 'SysFont',
                          side_effect=PermissionError('fc-list')), \
             patch.object(pygame.font, 'Font', side_effect=simular):
            self.assertIsNotNone(fonte('pt_BR', 22))
        self.assertEqual(chamadas, ['/system/fonts/Roboto-Bold.ttf'])

    def test_android_fallback_regular_ou_default_e_negrito(self):
        fonte = fonte_do_tutorial()
        original = pygame.font.Font
        calls = []
        def simular(path, size):
            calls.append(path)
            if path == '/system/fonts/Roboto-Bold.ttf':
                raise OSError('Roboto Bold indisponivel')
            return original(None, size)
        with patch.dict(os.environ, {'ANDROID_ARGUMENT': '1'}), \
             patch.object(pygame.font, 'SysFont',
                          side_effect=PermissionError('fc-list')), \
             patch.object(pygame.font, 'Font', side_effect=simular):
            f = fonte('pt_BR', 21)
        self.assertEqual(calls[:2],
                         ['/system/fonts/Roboto-Bold.ttf',
                          '/system/fonts/Roboto-Regular.ttf'])
        self.assertTrue(f.get_bold())
        fonte = fonte_do_tutorial()
        def sem_fontes(path, size):
            if path is not None:
                raise OSError('fonts indisponiveis')
            return original(None, size)
        with patch.dict(os.environ, {'ANDROID_ARGUMENT': '1'}), \
             patch.object(pygame.font, 'SysFont',
                          side_effect=PermissionError('fc-list')), \
             patch.object(pygame.font, 'Font', side_effect=sem_fontes):
            self.assertTrue(fonte('pt_BR', 21).get_bold())

if __name__ == '__main__':
    unittest.main(verbosity=2)
