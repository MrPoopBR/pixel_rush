"""Observador de cadência de FPS por bioma (opt-in), sem modificar o profiler legado.

Mede frame total incluindo o limitador (cadência aparente) e custo do frame
antes do limitador. Registra exclusivamente frames iniciados em JOGANDO.
O tempo de 60 Hz não mede a velocidade máxima da CPU/GPU. Nunca escreve por frame.
"""
from __future__ import annotations
from collections import defaultdict, deque
import json
import os
from pathlib import Path
import statistics
import time


def resumo(valores):
    if not valores:
        return {'amostras': 0, 'media_ms': None, 'p50_ms': None, 'p95_ms': None,
                'p99_ms': None, 'max_ms': None}
    ordenado = sorted(valores)
    def percentil(q):
        return round(ordenado[int((len(ordenado)-1)*q + .5)], 3)
    return {'amostras': len(valores), 'media_ms': round(statistics.mean(valores), 3),
            'p50_ms': percentil(.50), 'p95_ms': percentil(.95),
            'p99_ms': percentil(.99), 'max_ms': round(ordenado[-1], 3)}


class PerfBiomas:
    def __init__(self, versao, edicao, *, habilitado=None, caminho=None, intervalo=None, relogio=None):
        self.habilitado = os.getenv('PIXELRUSH_PERF_BIOMAS', '0') == '1' if habilitado is None else bool(habilitado)
        self.versao, self.edicao = str(versao), str(edicao)
        self.caminho = Path(caminho or os.getenv('PIXELRUSH_PERF_BIOMAS_PATH') or
                            f'qa_desempenho/perf_biomas_v3251_{self.edicao}.json')
        try:
            intervalo = int(intervalo if intervalo is not None else os.getenv('PIXELRUSH_PERF_BIOMAS_INTERVALO', '5'))
        except (ValueError, TypeError):
            intervalo = 5
        self.intervalo = max(1, min(intervalo, 120))
        self.relogio = relogio or time.perf_counter_ns
        self.quadros_jogando = 0
        self._inicio = self._antes_limite = self._bioma = None
        self._por_bioma = defaultdict(lambda: {'total_ms': deque(maxlen=3000),
                                              'trabalho_ms': deque(maxlen=3000)})
        self.ultimo_erro = None

    def iniciar(self, estado, bioma):
        if not self.habilitado:
            return
        self._inicio = self._antes_limite = self._bioma = None
        if estado != 'JOGANDO':
            return
        self.quadros_jogando += 1
        if self.quadros_jogando % self.intervalo != 0:
            return
        self._bioma = str(bioma)[:60]
        self._inicio = self.relogio()

    def antes_limitador(self):
        if self._inicio is not None:
            self._antes_limite = self.relogio()

    def fim(self):
        if self._inicio is None:
            return
        fim = self.relogio()
        trabalho = self._antes_limite
        inicio = self._inicio
        bioma = self._bioma
        self._inicio = self._antes_limite = self._bioma = None
        if trabalho is None or fim < trabalho or trabalho < inicio:
            return
        dados = self._por_bioma[bioma]
        dados['total_ms'].append((fim - inicio)/1_000_000)
        dados['trabalho_ms'].append((trabalho - inicio)/1_000_000)

    def relatorio(self):
        por_bioma = {}
        for bioma in sorted(self._por_bioma):
            total = list(self._por_bioma[bioma]['total_ms'])
            trabalho = list(self._por_bioma[bioma]['trabalho_ms'])
            media = statistics.mean(total) if total else 0
            por_bioma[bioma] = {
                'frame_total_com_limitador': resumo(total),
                'trabalho_sem_limitador': resumo(trabalho),
                'fps_estimado_pela_media_total': round(1000/media, 2) if media else None,
                'frames_acima_20ms': sum(v > 20 for v in total),
                'frames_acima_33ms': sum(v > 33.333 for v in total),
            }
        return {'schema':'pixelrush.perf_biomas.v1', 'versao':self.versao,
                'edicao':self.edicao, 'intervalo_quadros':self.intervalo,
                'quadros_jogando_observados':self.quadros_jogando,
                'por_bioma':por_bioma,
                'notas': ('Amostra com limitador de 60 FPS e tempo de espera incluso; '
                          'medição por frame não representa FPS de dispositivo móvel; '
                          'máximo de 3000 amostras recentes por bioma; usar profiler '
                          'v3204 para subdivisões de CPU e não somar suas submedidas.')}

    def salvar(self):
        if not self.habilitado:
            return False
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.caminho.with_name(self.caminho.name + '.tmp')
            tmp.write_text(json.dumps(self.relatorio(), ensure_ascii=False, indent=2), encoding='utf8')
            os.replace(tmp, self.caminho)
            self.ultimo_erro = None
            return True
        except (OSError, ValueError, TypeError) as exc:
            self.ultimo_erro = type(exc).__name__
            return False


def criar_monitor(versao, edicao):
    return PerfBiomas(versao, edicao)
