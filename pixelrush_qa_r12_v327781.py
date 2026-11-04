# -*- coding: utf-8 -*-
"""Coleta R12 PASSIVA para APK QA 3.277.81; sem tocar no jogo ou em saves.

Os percentis das fases e FPS sao produzidos pela QATelemetria real. Este
modulo adiciona somente instantaneos dos backends realmente instalados.
Nenhum readback GL, nome de usuario, save, toque, imagem ou identificador
do aparelho e capturado. Importar nao instala nem ativa aceleradores.
"""
import os
import platform
import sys


_MODULES = {
    "display_fullscreen": "pixelrush_qa_android_display_v327782",
    "gpu_bridge": "pixelrush_qa_gles_bridge_v327749",
    "gpu_preflight": "pixelrush_qa_gpu_preflight_v327780",
    "camera_neon": "pixelrush_qa_camera_native_auto_v327742",
    "camera_simd": "pixelrush_qa_camera_v327733",
    "scroll_incremental": "pixelrush_qa_incremental_scene_v327750",
    "gc_cooperativo": "pixelrush_qa_gc_cooperativo_v327757",
    "memoria_e_pacing": "pixelrush_qa_performance_integrated_v327742",
    "world_passes": "pixelrush_qa_r11_passes_v327776",
}


def _somente_carregados():
    # Evitar auto-import de modulos que podem instalar hooks, inicializar
    # um contexto GL ou fazer consultas ao driver. Os carregados sao reais.
    saida = {}
    for nome, modulo in _MODULES.items():
        carregado = sys.modules.get(modulo)
        diagnostico = getattr(carregado, "diagnostico", None)
        if not callable(diagnostico):
            saida[nome] = {"carregado": False}
            continue
        try:
            d = diagnostico()
            saida[nome] = d if isinstance(d, dict) else {"estado": "invalido"}
        except (AttributeError, RuntimeError, OSError, ValueError, TypeError) as exc:
            saida[nome] = {"carregado": True, "erro": type(exc).__name__}
    return saida


def coletar():
    """Instantaneo tecnico; chamados apenas na criacao de relatorios R12."""
    modulos = _somente_carregados()
    bridge = modulos["gpu_bridge"]
    nativo = modulos["camera_neon"]
    scroll = modulos["scroll_incremental"]
    gc = modulos["gc_cooperativo"]
    perf = modulos["memoria_e_pacing"]
    display = modulos["display_fullscreen"]
    presenter = perf.get("gpu_presenter") or {}
    pbo = presenter.get("qa_pbo_stats") or {}
    return {
        "schema": "pixelrush.qa.r12.runtime.v327781",
        "plataforma": sys.platform,
        "arquitetura": platform.machine(),
        "android_ambiente": bool(sys.platform == "android" or
                                "ANDROID_ARGUMENT" in os.environ),
        "aplicativo_qa": os.environ.get("PIXELRUSH_QA_ANDROID") == "1",
        "sem_coleta_pessoal": True,
        "modulos": modulos,
        "execucao_observada": {
            "display_modo": display.get("modo"),
            "display_surface_size": display.get("surface_size"),
            "display_window_size": display.get("window_size"),
            "gles_frames": int(bridge.get("frames_gles") or 0),
            "gles_fallback_frames": int(bridge.get("frames_fallback") or 0),
            "gles_falhas": int(bridge.get("falhas_gpu") or 0),
            "camera_native_frames": int(nativo.get("frames_native") or 0),
            "scroll_cidade_hits": int(scroll.get("cidade_hit") or 0),
            "scroll_cidade_rebuild": int(scroll.get("cidade_rebuild") or 0),
            "gc_coletas_0": int(gc.get("coletas_0") or 0),
            "gc_coletas_1": int(gc.get("coletas_1") or 0),
            "gc_coletas_2": int(gc.get("coletas_2") or 0),
            "gles_pbo_uploads": int(pbo.get("frames_upload") or 0),
            "egl_vsync_aplicado": presenter.get("egl_vsync_aplicado"),
            "egl_swap_p50_ms": presenter.get("frame_interval_p50_ms"),
            "egl_swap_p95_ms": presenter.get("frame_interval_p95_ms"),
            "egl_swap_p99_ms": presenter.get("frame_interval_p99_ms"),
            "egl_jank_acima_50ms": presenter.get("quadros_intervalo_acima_50ms"),
        },
        "homologacao_32_a54": False,
        "gpu_ms_real": None,
        "motivo_gpu_ms": "Perfetto/driver externo exigido para GPU real",
    }
