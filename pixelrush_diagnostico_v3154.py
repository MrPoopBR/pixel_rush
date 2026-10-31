"""Diagnóstico opcional e leve do Pixel Rush v3.154.0.

Ativar com PIXELRUSH_DIAGNOSTICO=1. É totalmente inativo na execução padrão.
Reporta custo de renderização por quadro (antes do tick de 60 Hz), sem confundir
um frame limitado a 60 FPS com um frame lento. Nunca coleta dados pessoais.
O JSON pode ser movido do aparelho para o PC para comparação.
"""
import json
import math
import os
import time
from collections import defaultdict, deque
from pathlib import Path


class MonitorDiagnostico:
    def __init__(self, caminho='pixelrush_diagnostico_v3154.json', intervalo=600):
        self.caminho = Path(caminho)
        self.intervalo = max(120, int(intervalo))
        self.inicio = time.perf_counter()
        self._inicio_quadro = self.inicio
        self.total = 0
        self.total_ms = 0.0
        self.pior_ms = 0.0
        self.picos_33ms = 0
        self.picos_50ms = 0
        self.picos_100ms = 0
        self.amostras = defaultdict(lambda: deque(maxlen=2048))
        self.contagem = defaultdict(int)
        self.erro_gravacao = None
        self.rss_pico_mb = None
        self.ult_resolucao = None
        self.dispositivo = 'nao_informado'

    @classmethod
    def from_environment(cls):
        monitor = cls(os.environ.get('PIXELRUSH_DIAG_PATH', 'pixelrush_diagnostico_v3154.json'))
        monitor.dispositivo = os.environ.get('PIXELRUSH_DIAG_DEVICE', 'nao_informado')[:48]
        return monitor

    def iniciar_quadro(self):
        self._inicio_quadro = time.perf_counter()

    def registrar_quadro(self, estado, bioma, largura, altura, modo_grafico='normal'):
        ms = max(0.0, (time.perf_counter() - self._inicio_quadro) * 1000.0)
        self.total += 1
        self.total_ms += ms
        self.pior_ms = max(self.pior_ms, ms)
        self.picos_33ms += ms > 33.333
        self.picos_50ms += ms > 50.0
        self.picos_100ms += ms > 100.0
        chave = '{}|{}|{}'.format(estado, bioma, modo_grafico)
        self.amostras[chave].append(ms)
        self.contagem[chave] += 1
        self.ult_resolucao = [int(largura), int(altura)]
        if self.total % self.intervalo == 0:
            self.salvar()

    @staticmethod
    def _percentil(valores, percentual):
        if not valores:
            return None
        ordenados = sorted(valores)
        indice = min(len(ordenados) - 1, max(0, math.ceil(len(ordenados) * percentual) - 1))
        return round(ordenados[indice], 3)

    @staticmethod
    def _pico_rss_mb():
        try:
            import resource
            import sys
            rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            # macOS reporta bytes; Linux/Android normalmente KiB.
            fator = 1024.0 * 1024.0 if sys.platform == 'darwin' else 1024.0
            return round(rss / fator, 2)
        except (ImportError, OSError, ValueError, AttributeError):
            return None

    def relatorio(self):
        por_estado_bioma = {}
        for chave, amostras in self.amostras.items():
            valores = list(amostras)
            por_estado_bioma[chave] = {
                'quadros_total': self.contagem[chave],
                'amostras_mais_recentes': len(valores),
                'media_ms_amostrada': round(sum(valores) / len(valores), 3) if valores else None,
                'p95_ms_amostrado': self._percentil(valores, .95),
                'pior_ms_amostrado': round(max(valores), 3) if valores else None,
            }
        return {
            'versao': 'v3.154.0',
            'dispositivo_tag': self.dispositivo,
            'origem': 'Pygame (custo de quadro antes do limite de 60 FPS)',
            'diagnostico_opt_in': True,
            'quadros_total': self.total,
            'media_ms': round(self.total_ms / self.total, 3) if self.total else None,
            'pior_ms': round(self.pior_ms, 3),
            'quadros_acima_33ms': self.picos_33ms,
            'quadros_acima_50ms': self.picos_50ms,
            'quadros_acima_100ms': self.picos_100ms,
            'resolucao_render_ultima': self.ult_resolucao,
            'pico_rss_mb_sistema': self._pico_rss_mb(),
            'duracao_segundos': round(time.perf_counter() - self.inicio, 1),
            'por_estado_e_bioma': por_estado_bioma,
            'observacao': 'RSS pode nao estar disponivel em Windows. Este perfil inclui IO periodico do diagnostico e nao e uma medicao fisica de FPS Android.',
        }

    def salvar(self):
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            temporario = self.caminho.with_name(self.caminho.name + '.tmp')
            temporario.write_text(json.dumps(self.relatorio(), ensure_ascii=False, indent=2), encoding='utf-8')
            os.replace(str(temporario), str(self.caminho))
            self.erro_gravacao = None
            return True
        except (OSError, ValueError, TypeError) as exc:
            # Diagnóstico não deve interromper o jogo em pastas protegidas.
            self.erro_gravacao = str(exc)
            return False
