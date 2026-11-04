# -*- coding: utf-8 -*-
"""QA772: reproduce R9 fatal fc-list on the real tutorial completion banner."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
import pixelrush_producao_fx_v32771 as fx
import pixelrush_fontes_prod_v32771 as fontes

ROOT=Path(__file__).resolve().parents[1]

class BannerFont772(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    def setUp(self):
        fx._FONTE_CACHE.clear()
        fontes._caminho_sistema.cache_clear()

    def test_r9_permissionerror_fc_list_ao_terminar_letras(self):
        tela=pygame.Surface((450,800),pygame.SRCALPHA)
        with (patch.dict(os.environ,{'ANDROID_ARGUMENT':'/data/user/0/app/files'}),
              patch.object(fontes,'fonte_unicode',
                  side_effect=PermissionError(13,'Permission denied','fc-list')),
              patch.object(pygame.font,'SysFont',
                  side_effect=PermissionError(13,'Permission denied','fc-list'))):
            fx.desenhar_mensagem_tutorial(tela,'pt_BR',180)
            self.assertIsInstance(fx._fonte('pt_BR',23),pygame.font.FontType)
        self.assertGreater(tela.get_bounding_rect().width,0)

    def test_android_cjk_fonte_ausente_nao_chama_fc_list(self):
        with (patch.dict(os.environ,{'ANDROID_ARGUMENT':'1'}),
              patch.object(Path,'is_file',return_value=False),
              patch.object(pygame.font,'match_font',
                  side_effect=PermissionError(13,'Permission denied','fc-list'))):
            for lang in ('ja_JP','zh_CN','ko_KR','hi_IN'):
                self.assertIsNone(fontes._caminho_sistema(lang))

    def test_preserva_unicode_existente(self):
        fonte=pygame.font.Font(None,21)
        with (patch.dict(os.environ,{'ANDROID_ARGUMENT':'1'}),
              patch.object(fontes,'fonte_unicode',return_value=fonte),
              patch.object(pygame.font,'SysFont',
                  side_effect=PermissionError(13,'Permission denied','fc-list'))):
            self.assertIs(fx._fonte('ja_JP',21),fonte)

    def test_desktop_mantem_arial(self):
        fonte=pygame.font.Font(None,19)
        with (patch.dict(os.environ,{},clear=True),
              patch.object(sys,'platform','linux'),
              patch.object(fontes,'fonte_unicode',return_value=None),
              patch.object(pygame.font,'SysFont',return_value=fonte) as original):
            self.assertIs(fx._fonte('pt_BR',19),fonte)
            original.assert_called_once_with('arial',19,bold=True)

    def test_cache_por_idioma_e_tamanho(self):
        with (patch.dict(os.environ,{'ANDROID_ARGUMENT':'1'}),
              patch.object(fontes,'fonte_unicode',return_value=None),
              patch.object(pygame.font,'SysFont',
                  side_effect=PermissionError('fc-list'))):
            a=fx._fonte('pt_BR',17)
            self.assertIs(a,fx._fonte('pt_BR',17))

    def test_chamada_real_no_engine_e_versao(self):
        codigo=(ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        self.assertIn('desenhar_mensagem_tutorial as _prod_mensagem_tutorial',codigo)
        self.assertIn('_prod_mensagem_tutorial(',codigo)
        self.assertIn('v3.277.81-QA-ANDROID-RC',codigo)

if __name__=='__main__':
    unittest.main(verbosity=2)
