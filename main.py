"""PIXEL RUSH Android QA v3.277.23: coleta opt-in SOMENTE nesta branch.

Aplicativo QA isolado com package.name proprio; sem mexer em main/producao.
"""
import os
from pathlib import Path
import runpy

def _preparar_telemetria_qa():
    caminho = Path(os.environ.get("ANDROID_PRIVATE") or Path.cwd()) / "qa_desempenho_v327723"
    caminho.mkdir(parents=True, exist_ok=True)
    configuracao = {
        "PIXELRUSH_PROFILER": "1",
        "PIXELRUSH_PROFILER_INTERVALO": "5",
        "PIXELRUSH_PROFILER_PATH": str(caminho / "profiler"),
        "PIXELRUSH_PERF_BIOMAS": "1",
        "PIXELRUSH_PERF_BIOMAS_INTERVALO": "1",
        "PIXELRUSH_PERF_BIOMAS_PATH": str(caminho / "perf_biomas.json"),
        "PIXELRUSH_DIAGNOSTICO": "1",
        "PIXELRUSH_DIAG_PATH": str(caminho / "diagnostico.json"),
        "PIXELRUSH_DIAG_DEVICE": "QA-Android",
    }
    for chave,valor in configuracao.items():
        os.environ.setdefault(chave, valor)
    # Somente QA: persistir a cadencia a cada ~30s para sobreviver a
    # encerramentos forçados da Activity. Nao altera atualizacao nem pixels.
    import pixelrush_perf_biomas_v3251 as mod
    original = mod.PerfBiomas.fim
    def fim_qa(self):
        original(self)
        if (self.habilitado and self.quadros_jogando
                and self.quadros_jogando % 900 == 0
                and getattr(self, "_qa_ultimo_salvo", -1) != self.quadros_jogando):
            self._qa_ultimo_salvo = self.quadros_jogando
            self.salvar()
    mod.PerfBiomas.fim = fim_qa
    print("PIXEL_RUSH_QA_PERF_PATH:", caminho, flush=True)


def _executar_jogo():
    origem = Path(__file__).resolve().parent / "PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py"
    if not origem.is_file() and origem.with_suffix(".pyc").is_file():
        origem = origem.with_suffix(".pyc")
    runpy.run_path(str(origem), run_name="__main__")


if __name__ == "__main__":
    _preparar_telemetria_qa()
    from pixelrush_android_abertura_v327712 import mostrar_abertura
    mostrar_abertura()
    _executar_jogo()
