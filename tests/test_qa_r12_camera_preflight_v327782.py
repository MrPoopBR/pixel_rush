# -*- coding: utf-8 -*-
"""QA782: o gate NEON inicial precisa avaliar zoom>0.002 e restaurar a camera.
Nao marca homologacao Android porque usa pygame-ce Linux e native fake.
"""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import pygame
import pixelrush_qa_camera_native_auto_v327742 as native

class DummyCamera:
    def __init__(self):
        self.zoom=0.0
        self.foco_y=0.0

class DummyPlayer:
    no_chao=True
    rect=pygame.Rect(52,574,42,52)

class ReferenceNative:
    @staticmethod
    def suportado(s):
        return s.get_bytesize()==4
    @staticmethod
    def processar(s,tamanho,recorte,backend=None):
        expanded=pygame.transform.smoothscale(s,tamanho)
        return expanded.subsurface((*recorte,*s.get_size())).copy()

class GateAndroidQA782(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init()
        pygame.display.set_mode((120,160))

    def test_zoom_zero_do_boot_agora_exercita_recorte_pixel_exato(self):
        camera=DummyCamera()
        origem=pygame.Surface((72,108),depth=32).convert()
        for y in range(origem.get_height()):
            pygame.draw.line(origem,((y*17)%256,(y*61)%256,
                                     (y*103)%256),(0,y),(71,y))
        with patch.object(native,'_load_native',return_value=ReferenceNative()):
            aprovado=native._verificar_primeiro_frame(
                origem,camera,DummyPlayer(),velocidade=12.0,
                momento=False,ativo=True)
        self.assertFalse(aprovado)  # fake usa CPU, nao promete ganho
        self.assertTrue(native._REPORT['teste_real'])
        self.assertTrue(native._REPORT['pixels_exatos'])
        self.assertIsNotNone(native._REPORT['original_p50_ms'])
        self.assertIsNotNone(native._REPORT['native_p50_ms'])
        self.assertEqual(camera.zoom,0.0)
        self.assertEqual(camera.foco_y,0.0)
        self.assertNotEqual(native._REPORT['status'],
                            'aguardando_preflight_fora_de_frame')

    def test_gate_sem_biblioteca_preserva_fallback_original(self):
        camera=DummyCamera()
        surface=pygame.Surface((72,108),depth=32).convert()
        with patch.object(native,'_load_native',return_value=None):
            aprovado=native._verificar_primeiro_frame(
                surface,camera,DummyPlayer(),velocidade=12.0,
                momento=False,ativo=True)
        self.assertFalse(aprovado)
        self.assertEqual(native._REPORT['status'],'biblioteca_nativa_ausente')
        self.assertEqual(camera.zoom,0.0)

    def test_integracao_no_boot_continua_fora_do_frame(self):
        e=(Path(__file__).resolve().parents[1]/
           'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        i=e.index('_qa_camera_native_boot(')
        loop=e.index('    while rodando:')
        self.assertLess(i,loop)
        self.assertIn("camera.zoom = .025",
            Path(native.__file__).read_text('utf8'))

if __name__=='__main__':
    unittest.main(verbosity=2)
