# -*- coding: utf-8 -*-
"""Pixel Rush Plano H v3.204.0: profiler amostrado e estritamente observacional.

Subdivisões instrumentadas apenas para diagnóstico. NÃO muda o passo fixo,
a ordem de processamento de eventos, a renderização ou os estados do jogo.
"""
import collections
import json
import os
import statistics
import time
from pathlib import Path

SECOES = (
    "inicio_e_preparacao", "audio", "simulacao", "entrada",
    "renderizacao_e_ui", "posprocessamento", "apresentacao", "limitador_fps"
)
SUBSISTEMAS = (
    "fisica_jogador", "inimigos_objetos", "particulas_update",
    "mundo_2_5d", "sprites_render", "clima_render",
    "qa_ceu_2d", "qa_world_draw", "qa_particulas_mundo",
    "qa_fundo_cache_chao", "qa_render_antes_sprites",
    "qa_render_apos_sprites", "qa_hud_corrida",
    "qa_replay_captura", "qa_simulacao_ticks",
    "qa_sim_diretores", "qa_sim_parallax", "qa_sim_clima",
)

class Profiler:
    def __init__(self, versao, edicao):
        self.versao = str(versao)
        self.edicao = str(edicao)
        flag = os.environ.get("PIXELRUSH_PROFILER", "1" if edicao == "DEV" else "0")
        self.ativo = flag.strip().lower() in ("1", "true", "on", "sim")
        try:
            intervalo = int(os.environ.get("PIXELRUSH_PROFILER_INTERVALO", "5"))
        except ValueError:
            intervalo = 5
        self.intervalo = max(1, min(120, intervalo))
        self.quadros = 0
        self.amostrando = False
        self.t0 = 0
        self.ultimo = 0
        self.anterior = "inicio_e_preparacao"
        self.pilha = []
        self.medidas = {chave: collections.deque(maxlen=720)
                        for chave in SECOES + SUBSISTEMAS}
        self.contexto = {"estado": "inicializacao", "bioma": "desconhecido"}
        self.erros_io = 0
        self.arquivo = self._destino()
        self.gravacoes = 0

    def _destino(self):
        pasta = os.environ.get("PIXELRUSH_PROFILER_PATH", "").strip()
        if not pasta:
            pasta = str(Path(__file__).resolve().parent / "diagnosticos")
        return Path(pasta) / ("profiler_v3204_%s.json" % self.edicao)

    def iniciar(self, estado, bioma):
        if not self.ativo:
            return
        self.quadros += 1
        self.amostrando = self.quadros % self.intervalo == 0
        self.contexto = {"estado": str(estado)[:45], "bioma": str(bioma)[:45]}
        if self.amostrando:
            self.t0 = self.ultimo = time.perf_counter_ns()
            self.anterior = "inicio_e_preparacao"
            self.pilha.clear()

    def marcar(self, proximo):
        if not self.amostrando:
            return
        instante = time.perf_counter_ns()
        if self.anterior in self.medidas:
            self.medidas[self.anterior].append((instante - self.ultimo) / 1000000.)
        self.anterior = proximo
        self.ultimo = instante

    def sub_inicio(self, nome):
        if self.amostrando and nome in self.medidas:
            self.pilha.append((nome, time.perf_counter_ns()))

    def sub_fim(self):
        if self.amostrando and self.pilha:
            nome, inicio = self.pilha.pop()
            self.medidas[nome].append((time.perf_counter_ns() - inicio) / 1000000.)

    def fim(self):
        if not self.amostrando:
            return
        self.marcar(None)
        self.amostrando = False
        self.pilha.clear()
        # I/O é raro e ocorre fora da região medida, nunca em cada quadro.
        if self.quadros % (self.intervalo * 240) == 0:
            self.salvar()

    @staticmethod
    def _estatisticas(valores):
        if not valores:
            return {"amostras": 0, "media_ms": 0., "mediana_ms": 0.,
                    "p95_ms": 0., "p99_ms": 0., "max_ms": 0.}
        ordenados = sorted(valores)
        def pct(fracao):
            return ordenados[min(len(ordenados)-1, max(0, int((len(ordenados)-1)*fracao + 0.5)))]
        return {"amostras": len(valores),
                "media_ms": round(statistics.mean(valores), 5),
                "mediana_ms": round(statistics.median(valores), 5),
                "p95_ms": round(pct(0.95), 5),
                "p99_ms": round(pct(0.99), 5),
                "max_ms": round(ordenados[-1], 5)}

    def relatorio(self):
        return {
            "versao": self.versao, "edicao": self.edicao,
            "ativo": self.ativo, "intervalo_quadros": self.intervalo,
            "quadros_observados": self.quadros,
            "ultima_situacao": dict(self.contexto),
            "secoes_exclusivas": {chave: self._estatisticas(self.medidas[chave]) for chave in SECOES},
            "submedidas_inclusivas": {chave: self._estatisticas(self.medidas[chave]) for chave in SUBSISTEMAS},
            "observacao": ("Os tempos das submedidas estao contidos nas secoes principais. "
                           "Nao somar submedidas ao tempo de frame. O limitador de FPS "
                           "inclui espera intencional. SDL dummy nao equivale a Android real."),
            "erros_io": self.erros_io
        }

    def salvar(self):
        if not self.ativo:
            return False
        try:
            self.arquivo.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.arquivo.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.relatorio(), ensure_ascii=False, indent=2), encoding="utf-8")
            os.replace(str(tmp), str(self.arquivo))
            self.gravacoes += 1
            return True
        except (OSError, ValueError):
            self.erros_io += 1
            return False

_ATUAL = None
_QA_ATUAL = None  # somente no APK QA; observador separado do profiler legado

def instalar(versao, edicao):
    global _ATUAL, _QA_ATUAL
    _ATUAL = Profiler(versao, edicao)
    _QA_ATUAL = None
    if os.environ.get("PIXELRUSH_QA_ANDROID") == "1":
        from pixelrush_qa_android_v327728 import QATelemetria
        _QA_ATUAL = QATelemetria(versao, edicao)
    return _ATUAL

def iniciar(estado, bioma):
    if _QA_ATUAL is not None: _QA_ATUAL.iniciar(estado, bioma)
    p = _ATUAL
    if p is not None: p.iniciar(estado, bioma)

def marcar(nome):
    if _QA_ATUAL is not None: _QA_ATUAL.marcar(nome)
    p = _ATUAL
    if p is not None: p.marcar(nome)

def sub_inicio(nome):
    if _QA_ATUAL is not None: _QA_ATUAL.sub_inicio(nome)
    p = _ATUAL
    if p is not None: p.sub_inicio(nome)

def sub_fim():
    if _QA_ATUAL is not None: _QA_ATUAL.sub_fim()
    p = _ATUAL
    if p is not None: p.sub_fim()

def fim():
    if _QA_ATUAL is not None: _QA_ATUAL.fim()
    p = _ATUAL
    if p is not None: p.fim()

def executar_com_profiler(funcao, versao, edicao):
    p = instalar(versao, edicao)
    try:
        return funcao()
    finally:
        p.salvar()
        if _QA_ATUAL is not None:
            try:
                _QA_ATUAL.salvar()  # bloqueante: nao perde o ultimo JSON/CSV
            finally:
                gravador = getattr(_QA_ATUAL, '_qa_gravador', None)
                if gravador is not None:
                    gravador.finalizar()  # encerra worker antes do processo sair
