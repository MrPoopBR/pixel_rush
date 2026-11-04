# -*- coding: utf-8 -*-
"""QA775 A54: gates reais de CPU e bloqueios das 10 frentes pendentes.

NUNCA marca GPU/driver como homologado a partir de Linux/Mesa.
Nao inicia app Android, nao altera saves, fisica ou pixels do jogo.
"""
import json
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame

PENDENTES = {
    1: "zoom GPU", 3: "compositor CPU/GPU", 5: "scroll incremental",
    7: "grandes alocacoes", 8: "SIMD smoothscale", 10: "copias e passes",
    12: "backend por dispositivo", 28: "recorte NEON",
    29: "uploads PBO GLES3", 32: "VSync driver Perfetto",
}


class A54Matriz775(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450, 800))
        cls.backend = pygame.transform.get_smoothscale_backend()

    @classmethod
    def tearDownClass(cls):
        pygame.transform.set_smoothscale_backend(cls.backend)
        pygame.quit()

    def test_matriz_completa_sem_promocao_indevida(self):
        from pixelrush_qa_backend_gate_v327747 import selecionar
        self.assertEqual(sorted(PENDENTES), [1,3,5,7,8,10,12,28,29,32])
        self.assertEqual(selecionar()["backend"], "cpu_sdl_original")
        d = {str(k): {"frente": v, "codigo": "existente",
                       "gate_offline": "coberto",
                       "homologado_a54": False}
             for k, v in PENDENTES.items()}
        (ROOT/"qa-a54-matriz-v327776.json").write_text(json.dumps({
            "schema": "pixelrush.qa.a54.matrix.v327776",
            "versao": "3.277.76-QA",
            "device_real_testado": False,
            "frentes": d, "aprovadas_android": 0,
            "status": "aguardando_coleta_fisica"
        }, ensure_ascii=False, indent=2), encoding="utf8")

    def test_gpu_hibrido_exige_entrada_hud_paridade_e_fps(self):
        from pixelrush_qa_backend_gate_v327747 import selecionar, CapacidadeVideo
        self.assertEqual(selecionar(CapacidadeVideo(
            janela_opengl=True, pixels_todos_iguais=True,
            fps_comprovadamente_melhor=True, dispositivo_real_medido=True),
            laboratorio=True)["backend"], "cpu_sdl_original")
        all_ok = CapacidadeVideo(
            janela_opengl=True, input_compatível=True, hud_compatível=True,
            pixels_todos_iguais=True, fps_comprovadamente_melhor=True,
            sem_readback=True, dispositivo_real_medido=True)
        self.assertEqual(selecionar(all_ok)["backend"], "cpu_sdl_original")
        self.assertEqual(selecionar(all_ok,laboratorio=True)["backend"],
                         "gles_laboratorio")
        self.assertFalse(selecionar(all_ok,laboratorio=True)
                         ["pronto_para_trocar_entrada_real"])

    def test_sdl_bridge_nunca_liga_silenciosamente(self):
        import pixelrush_qa_gles_bridge_v327749 as bridge
        bridge.restaurar_para_teste()
        old = pygame.display.set_mode
        with patch.dict(os.environ, {
                "PIXELRUSH_QA_GLES_BRIDGE":"0", "PIXELRUSH_QA_ANDROID":"1"}):
            bridge.instalar()
            self.assertIs(pygame.display.set_mode, old)
            self.assertFalse(bridge.diagnostico()["gpu_ativo"])

    def test_pbo_recusa_gles2_antes_de_alocar_buffer(self):
        from pixelrush_qa_gles_pbo_v327742 import (
            UploadGLES3PBOQA, GLES3PboUnavailable)
        with self.assertRaises(GLES3PboUnavailable):
            UploadGLES3PBOQA(SimpleNamespace(version="OpenGL ES 2.0"))
        with self.assertRaises(ValueError):
            UploadGLES3PBOQA(SimpleNamespace(version="OpenGL ES 3.2"),
                            count=8)

    def test_simd_sem_optin_preserva_backend_e_pixels(self):
        from pixelrush_qa_camera_v327733 import preparar_fora_do_frame
        frame = pygame.Surface((75, 103), pygame.SRCALPHA, 32)
        for y in range(103):
            pygame.draw.line(frame, ((y*17)%256, (y*31)%256,
                             (y*47)%256, (y*23)%256), (0,y),(74,y))
        before = pygame.image.tobytes(frame,"RGBA")
        with patch.dict(os.environ, {"PIXELRUSH_QA_CAMERA_AUTOTUNE":"0"}):
            result = preparar_fora_do_frame(frame,(81,117))
        self.assertEqual(result,self.backend)
        self.assertEqual(pygame.transform.get_smoothscale_backend(),self.backend)
        self.assertEqual(pygame.image.tobytes(frame,"RGBA"), before)

    def test_rolling_rgba_hidden_e_fallback_sem_ganho(self):
        from pixelrush_qa_scroll_auto_v327742 import _bench
        surface = pygame.Surface((450,400), pygame.SRCALPHA,32)
        dest = pygame.Surface((450,800), pygame.SRCALPHA,32)
        dest.fill((139,72,203,0))
        initial = pygame.image.tobytes(dest,"RGBA")
        approved, metric, reason = _bench(surface, dest)
        self.assertFalse(approved)
        self.assertIsNone(metric)
        self.assertEqual(reason,"formato_nao_suportado")
        self.assertEqual(initial,pygame.image.tobytes(dest,"RGBA"))

    def test_native_ausente_nao_seleciona_backend(self):
        import pixelrush_qa_camera_native_auto_v327742 as camera_native
        with patch.dict(os.environ, {"PIXELRUSH_QA_NATIVE_AUTO":"0"}):
            self.assertFalse(camera_native.preparar_fora_do_frame(
                pygame.Surface((450,800)),object(),object()))
        self.assertFalse(camera_native.diagnostico()["selecionado"])

    def test_perfetto_no_host_nao_cria_sessao_android(self):
        from pixelrush_qa_performance_integrated_v327742 import _AndroidTrace
        with patch.dict(os.environ,{"PIXELRUSH_QA_TRACE":"1",
                                    "ANDROID_ARGUMENT":""}, clear=False):
            # ANDROID_ARGUMENT vazio ainda identifica plataforma para o
            # codigo antigo: remover no sub-escopo sem mudar o ambiente.
            with patch.dict(os.environ, {"ANDROID_ARGUMENT": ""}):
                # No host, se variable existe, ATrace_isEnabled pode
                # ser consultado, mas fallback continua sem session.
                trace = _AndroidTrace()
        self.assertIsNone(trace.begin)
        self.assertIsNone(trace.end)

    def test_producao_e_rollback_nao_forcam_gpu(self):
        spec=(ROOT/"buildozer.spec").read_text("utf8")
        game=(ROOT/"PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py").read_text("utf8")
        a=(ROOT/"pixelrush_qa_gles_bridge_v327749.py").read_text("utf8")
        scroll=(ROOT/"pixelrush_qa_incremental_scene_v327750.py").read_text("utf8")
        self.assertIn("android.archs = arm64-v8a",spec)
        self.assertIn("android.numeric_version = 327776",spec)
        self.assertIn('VERSAO = "v3.277.76-QA-ANDROID-RC"',game)
        self.assertIn("PIXELRUSH_QA_GLES_BRIDGE','0'",a)
        self.assertIn("PIXELRUSH_QA_CITY_INCREMENTAL','0'",scroll)
        self.assertIn("PIXELRUSH_QA_CITY_RECYCLE_SCALE','1'",
                      (ROOT/"pixelrush_city2_v3118.py").read_text("utf8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
