# -*- coding: utf-8 -*-
"""QA781: R12 escreve dados reais sem acesso a save, entrada ou framebuffer.

Cobre export assincrono JSON/CSV, p50/p95/p99, fases 2.5D, pos-sprites,
RSS e estado observado do backend PBO/NEON, sem fingir driver Android real.
"""
import csv
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from pixelrush_qa_android_v327728 import QATelemetria
from pixelrush_qa_r12_v327781 import coletar


class Relogio:
    def __init__(self,passo=1_000_000):
        self.n=0
        self.passo=passo
    def __call__(self):
        self.n+=self.passo
        return self.n


class R12TelemetriaQA781(unittest.TestCase):
    def _gerar(self,pasta,versao):
        relogio=Relogio()
        cpu=Relogio(400_000)
        q=QATelemetria(versao,"QA",caminho=pasta,
                       relogio=relogio,cpu_relogio=cpu)
        for i in range(20):
            q.iniciar("JOGANDO","cidade")
            q.marcar("simulacao")
            q.marcar("renderizacao_e_ui")
            q.sub_inicio("mundo_2_5d")
            q.sub_fim()
            q.sub_inicio("qa_render_apos_sprites")
            q.sub_fim()
            q.sub_inicio("r11_post_pets")
            q.sub_fim()
            q.marcar("apresentacao")
            q.sub_inicio("apresentacao_swap")
            q.sub_fim()
            q.marcar("limitador_fps")
            q.fim()
        self.assertTrue(q.salvar(esperar=True))
        q._qa_gravador.finalizar()
        return q

    def test_json_csv_r12_p50_p95_p99_e_passes_reais(self):
        with tempfile.TemporaryDirectory(prefix="pixelrush-r12-") as pasta:
            with patch.dict(os.environ,{"PIXELRUSH_QA_ANDROID":"1"}):
                q=self._gerar(pasta,"v3.277.82-QA-ANDROID-RC")
            self.assertTrue(q.r12)
            destino=Path(pasta)
            j=destino/"pixelrush_qa_v327781_r12.json"
            c=destino/"pixelrush_qa_frames_v327781_r12.csv"
            self.assertTrue(j.is_file())
            self.assertTrue(c.is_file())
            d=json.loads(j.read_text("utf8"))
            self.assertEqual(d["schema"],"pixelrush.qa.android.r12.v327781")
            self.assertEqual(d["quadros_observados"],20)
            metrics=d["grupos"]["corrida_normal|cidade"]["metricas_ms"]
            for key in ("quadro_total_ms","trabalho_sem_limitador_ms",
                        "cpu_processo_ms","intervalo_entre_inicios_ms",
                        "mundo_2_5d","qa_render_apos_sprites","r11_post_pets",
                        "apresentacao_swap"):
                # O 1o quadro nao tem intervalo anterior por definicao.
                esperado_n = 19 if key == "intervalo_entre_inicios_ms" else 20
                self.assertEqual(metrics[key]["n"],esperado_n,key)
                for pct in ("p50","p95","p99"):
                    self.assertIsNotNone(metrics[key][pct],(key,pct))
            self.assertFalse(d["r12_hardware_homologado_a54"])
            self.assertFalse(d["r12_runtime"]["homologacao_32_a54"])
            self.assertTrue(d["r12_runtime"]["sem_coleta_pessoal"])
            with c.open("r",encoding="utf8",newline="") as f:
                linhas=list(csv.DictReader(f))
            self.assertEqual(len(linhas),20)
            for name in ("mundo_2_5d_ms","world_total_r11_ms","pos_sprites_ms",
                         "pos_pets_ms","swap_cpu_ms","rss_mb"):
                self.assertIn(name,linhas[0])
            for campo in ("save","user_id","input","touch","login","imei"):
                self.assertNotIn(campo,linhas[0])

    def test_exportacao_legada_intacta(self):
        with tempfile.TemporaryDirectory(prefix="pixelrush-r11-") as pasta:
            with patch.dict(os.environ,{"PIXELRUSH_QA_ANDROID":"1"}):
                q=self._gerar(pasta,"v3.277.80-QA")
            self.assertFalse(q.r12)
            with (Path(pasta)/"pixelrush_qa_frames_v327747.csv").open(
                    "r",encoding="utf8",newline="") as f:
                campos=next(csv.reader(f))
            self.assertEqual(campos,["modo","bioma","total_ms","trabalho_ms",
                                     "cpu_ms","intervalo_ms","rss_mb"])

    def test_modulos_telemetria_sem_import_lateral(self):
        fake={
            "pixelrush_qa_gles_bridge_v327749": {
                "frames_gles":19,"falhas_gpu":1,"frames_fallback":2
            },
            "pixelrush_qa_camera_native_auto_v327742": {
                "frames_native":14,"selecionado":True
            },
            "pixelrush_qa_incremental_scene_v327750": {
                "cidade_hit":123,"cidade_rebuild":7
            },
            "pixelrush_qa_gc_cooperativo_v327757": {
                "coletas_0":3,"coletas_1":1,"coletas_2":0
            },
            "pixelrush_qa_performance_integrated_v327742": {
                "gpu_presenter":{
                    "qa_pbo_stats":{"frames_upload":16},
                    "egl_vsync_aplicado":1,
                    "frame_interval_p50_ms":28.2,
                    "frame_interval_p95_ms":44.2,
                    "frame_interval_p99_ms":62.1,
                    "quadros_intervalo_acima_50ms":2
                }
            },
        }
        modules={name:types.SimpleNamespace(
            diagnostico=lambda data=data:dict(data))
            for name,data in fake.items()}
        with patch.dict(sys.modules,modules):
            d=coletar()["execucao_observada"]
        self.assertEqual(d["gles_frames"],19)
        self.assertEqual(d["gles_falhas"],1)
        self.assertEqual(d["gles_pbo_uploads"],16)
        self.assertEqual(d["camera_native_frames"],14)
        self.assertEqual(d["scroll_cidade_hits"],123)
        self.assertEqual(d["egl_vsync_aplicado"],1)
        self.assertEqual(d["egl_swap_p99_ms"],62.1)


if __name__=="__main__":
    unittest.main(verbosity=2)
