# -*- coding: utf-8 -*-
"""QA 3.277.34: gate GL observacional e fallback GPU inativo."""
import os
import sys
from pathlib import Path
import unittest

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame


class TestGlesGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_gate_nao_altera_janela_nem_backend(self):
        from pixelrush_qa_gles_gate_v327734 import diagnosticar
        tela=pygame.display.get_surface()
        flags=tela.get_flags()
        backend=pygame.transform.get_smoothscale_backend()
        estado=diagnosticar()
        self.assertFalse(estado['integracao_aprovada'])
        self.assertFalse(estado['ativa_gpu'])
        self.assertTrue(estado['fallback_cpu_preservado'])
        self.assertEqual(tela,pygame.display.get_surface())
        self.assertEqual(flags,pygame.display.get_surface().get_flags())
        self.assertEqual(backend,pygame.transform.get_smoothscale_backend())
        self.assertIn(estado['tipo_janela'],('surface_sdl','opengl'))
        self.assertEqual(estado['schema'],'pixelrush.qa.gles_gate.v1')

    def test_camera_qa_exige_rgba_na_segunda_prova(self):
        codigo=(ROOT/'pixelrush_qa_camera_v327733.py').read_text('utf8')
        self.assertIn("pygame.transform.smoothscale(amostra, alt_tamanho), formato)",codigo)
        self.assertNotIn("pygame.transform.smoothscale(amostra, alt_tamanho), 'RGB')",codigo)
        self.assertIn('set_smoothscale_backend(original_backend)',codigo)

    def test_geracao_android_somente_debug(self):
        tela=(ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        workflow=(ROOT/'.github/workflows/qa-apk-debug-v327734.yml').read_text('utf8')
        saida=(ROOT/'pixelrush_qa_android_v327728.py').read_text('utf8')
        bootstrap=(ROOT/'main.py').read_text('utf8')
        self.assertIn('VERSAO = "v3.277.35-QA-ANDROID-RC"',tela)
        self.assertIn('MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15',tela)
        self.assertIn('FPS_RENDER = 30 if E_ANDROID else 60',tela)
        self.assertIn('PIXELRUSH_DEV_BUILD = False',tela)
        self.assertIn("getExternalFilesDir(None)",saida)
        self.assertIn("pixelrush_qa_v327734.json",saida)
        self.assertIn("pixelrush_qa_frames_v327734.csv",saida)
        self.assertIn("'gles_camera_gate_qa': _gles_gate_qa()",saida)
        self.assertIn("buildozer -v android debug",workflow)
        self.assertNotIn("buildozer -v android release",workflow)
        self.assertIn('qa/android-gles-gate-v3.277.34',workflow)
        self.assertNotIn('pixelrush_qa_gles_gate_v327734',bootstrap)
        self.assertIn("from pixelrush_qa_render_v327729",bootstrap)

    def test_gles_prototipo_nao_importado_no_jogo(self):
        caminho=ROOT/'.github/scripts/qa_gles_camera_probe_v327734.py'
        codigo=caminho.read_text('utf8')
        self.assertIn('eglCreateContext',codigo)
        self.assertIn('glTexSubImage2D',codigo)
        self.assertIn('glReadPixels',codigo)
        self.assertIn("'aprovado':False",codigo)
        self.assertNotIn('pygame.display.set_mode((450,800),pygame.OPENGL)',codigo)
        main=(ROOT/'main.py').read_text('utf8')
        self.assertNotIn('qa_gles_camera_probe_v327734',main)


if __name__=='__main__':
    unittest.main(verbosity=2)
