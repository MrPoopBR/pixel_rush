# -*- coding: utf-8 -*-
"""QA780: teste de inicializacao efetiva da ponte GPU Mesa em RGBA8, sem Android."""
import os
import sys
import json
import unittest
from pathlib import Path
from unittest.mock import patch
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame
import pixelrush_qa_gles_present_v327735 as present
from pixelrush_qa_gles_exact_v327736 import shaders
from pixelrush_qa_gpu_preflight_v327780 import verificar,diagnostico

class PreflightRealGPU780(unittest.TestCase):
    def test_falha_no_contexto_nao_autoriza_gles(self):
        class Ausente: pass
        self.assertFalse(verificar(Ausente()))
        self.assertFalse(diagnostico()['aprovado'])
        self.assertIn('fallback_',diagnostico()['motivo'])

    def test_fbo_rgba_e_ganho_qa_mesa_sem_homologacao_android(self):
        pygame.init()
        pygame.display.set_mode((450,800))
        backend=pygame.transform.get_smoothscale_backend()
        previous=present.VERT,present.FRAG
        try:
            # CI Mesa usa SSE2 no mesmo pygame-ce da referencia CPU.
            pygame.transform.set_smoothscale_backend('SSE2')
            present.VERT,present.FRAG=shaders('GLES3','SSE2',(450,800))
            p=present.GLES2DirectPresenterQA(450,800)
            try:
                if not p.version.startswith('OpenGL ES 3'):
                    self.skipTest('GLES3 nao exposto pelo driver Mesa')
                # A testemunha mede pixels reais; ganho CPU/GPU pode variar.
                self.assertTrue(verificar(p,exigir_ganho=False),
                                diagnostico())
                result=diagnostico()
                self.assertEqual(result['casos_rgba'],10)
                self.assertEqual(result['diferencas'],0)
                self.assertTrue(result['leitura_somente_boot'])
                self.assertFalse(result['fps_android_homologado'])
                self.assertGreater(result['tempo_cpu_p50_ms'],0)
                self.assertGreater(result['tempo_gpu_p50_ms'],0)
                (ROOT/'qa-gpu-preflight-v327780.json').write_text(
                    json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
                # Teste visual nao altera flag de integracao do jogo.
                self.assertFalse(p.diagnostico()['integrado_ao_jogo'])
            finally:
                p.close()
        finally:
            present.VERT,present.FRAG=previous
            pygame.transform.set_smoothscale_backend(backend)
            pygame.quit()

if __name__=='__main__':
    unittest.main(verbosity=2)
