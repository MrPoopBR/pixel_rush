"""Telemetria v3.277.28-QA: observacional, ativa somente no APK QA.

Tempos de fases: relogio de parede; CPU: tempo de processo (todas as threads).
GPU real NAO pode ser inferida de pygame.display.flip: usar Perfetto/gfxinfo.
Nenhuma informacao pessoal, de save ou de entrada do jogador e registrada.
"""
from collections import defaultdict, deque
import csv
import json
import os
from pathlib import Path
import statistics
import time

SECOES = (
    'inicio_e_preparacao', 'audio', 'simulacao', 'entrada',
    'renderizacao_e_ui', 'posprocessamento', 'apresentacao', 'limitador_fps',
    'fisica_jogador', 'inimigos_objetos', 'particulas_update',
    'mundo_2_5d', 'sprites_render', 'clima_render',
    'mundo_composicao_interna', 'profundidade_fundo',
    'camera_smoothscale', 'camera_gamefeel',
)


def _destino():
    escolha = os.environ.get('PIXELRUSH_QA_PATH')
    if escolha:
        return Path(escolha)
    if 'ANDROID_ARGUMENT' in os.environ:
        try:
            from jnius import autoclass
            atividade = autoclass('org.kivy.android.PythonActivity').mActivity
            pasta = atividade.getExternalFilesDir(None)
            if pasta is not None:
                return Path(str(pasta.getAbsolutePath())) / 'pixelrush_qa'
        except Exception:
            pass
    return Path(os.environ.get('ANDROID_PRIVATE') or os.getcwd()) / 'pixelrush_qa'


def _renderer_backend_qa():
    """Metadados tecnicos observacionais; nenhuma mudanca no render."""
    try:
        import pygame
        backend = pygame.transform.get_smoothscale_backend()
        driver = pygame.display.get_driver() if pygame.display.get_init() else None
        return {'smoothscale': str(backend), 'sdl_video': str(driver) if driver else None}
    except (ImportError, AttributeError, RuntimeError):
        return {'smoothscale': None, 'sdl_video': None}


def _memoria_rss_mb():
    try:
        with open('/proc/self/status', encoding='ascii') as arquivo:
            for linha in arquivo:
                if linha.startswith('VmRSS:'):
                    return round(int(linha.split()[1]) / 1024, 2)
    except (OSError, ValueError, IndexError):
        pass
    return None


def _stats(valores):
    if not valores:
        return {'n': 0, 'media': None, 'p50': None, 'p95': None, 'p99': None, 'max': None}
    v = sorted(valores)
    def percentil(f):
        return round(v[round((len(v) - 1) * f)], 3)
    return {'n': len(v), 'media': round(statistics.mean(v), 3),
            'p50': percentil(.5), 'p95': percentil(.95),
            'p99': percentil(.99), 'max': round(v[-1], 3)}


class QATelemetria:
    """Mede todos os frames; so escreve no disco de tempos em tempos ou ao sair."""
    def __init__(self, versao, edicao, caminho=None, relogio=None, cpu_relogio=None):
        self.versao, self.edicao = str(versao), str(edicao)
        self.pasta = Path(caminho) if caminho is not None else _destino()
        self.relogio = relogio or time.perf_counter_ns
        self.cpu_relogio = cpu_relogio or time.process_time_ns
        self.contagem = 0
        self.inicio = None
        self.anterior_inicio = None
        self.atual = None
        self.fase = None
        self.marca = None
        self.pilha = []
        self.agregados = defaultdict(lambda: defaultdict(lambda: deque(maxlen=1800)))
        self.quantidades = defaultdict(int)
        self.picos = defaultdict(lambda: {'mais_33ms': 0, 'mais_50ms': 0, 'mais_100ms': 0})
        self.ultimos = deque(maxlen=4000)
        self.piores = []
        self.rss_mb = None
        self.rss_pico_mb = None
        self.erros_escrita = 0
        self.ultima_falha = None
        self.gravacoes = 0

    def iniciar(self, estado, bioma):
        agora = self.relogio()
        self.inicio = agora
        self.marca = agora
        self.fase = 'inicio_e_preparacao'
        intervalo = (agora - self.anterior_inicio) / 1e6 if self.anterior_inicio is not None else None
        self.anterior_inicio = agora
        self.atual = {'estado': str(estado), 'bioma': str(bioma)[:40],
                      'intervalo_entre_inicios_ms': intervalo,
                      'fases_ms': {}, 'cpu_inicial': self.cpu_relogio()}
        self.pilha.clear()

    def _fechar_fase(self, agora):
        if self.atual is not None and self.fase in SECOES:
            fases = self.atual['fases_ms']
            fases[self.fase] = fases.get(self.fase, 0.0) + max(0, agora - self.marca) / 1e6

    def marcar(self, proxima):
        if self.atual is None:
            return
        agora = self.relogio()
        self._fechar_fase(agora)
        self.fase, self.marca = proxima, agora

    def sub_inicio(self, nome):
        if self.atual is not None and nome in SECOES:
            self.pilha.append((nome, self.relogio()))

    def sub_fim(self):
        if self.atual is not None and self.pilha:
            nome, inicio = self.pilha.pop()
            fases = self.atual['fases_ms']
            fases[nome] = fases.get(nome, 0.0) + max(0, self.relogio() - inicio) / 1e6

    def fim(self):
        if self.atual is None:
            return
        agora = self.relogio()
        self._fechar_fase(agora)
        entrada = self.atual
        self.atual = None
        self.fase = None
        self.pilha.clear()
        self.contagem += 1
        estado = entrada['estado']
        modo = ('tutorial' if estado == 'JOGANDO_TUTORIAL_QA' else
                'corrida_normal' if estado == 'JOGANDO' else
                'replay' if estado == 'GAMEOVER_REPLAY_QA' else estado.lower())
        bioma = entrada['bioma']
        chave = modo + '|' + bioma
        fases = entrada['fases_ms']
        # Resto do desenho, descontando passes inclusivos do ramo de render.
        if 'renderizacao_e_ui' in fases:
            fases['render_residual_estimado'] = max(0.0, fases['renderizacao_e_ui'] -
                sum(fases.get(k, 0.0) for k in
                    ('mundo_2_5d', 'profundidade_fundo', 'sprites_render', 'clima_render')))
        total = max(0, agora - self.inicio) / 1e6
        trabalho = max(0, total - fases.get('limitador_fps', 0))
        cpu = max(0, self.cpu_relogio() - entrada['cpu_inicial']) / 1e6
        intervalo = entrada['intervalo_entre_inicios_ms']
        amostras = self.agregados[chave]
        for campo, valor in [('quadro_total_ms', total), ('trabalho_sem_limitador_ms', trabalho),
                             ('cpu_processo_ms', cpu), ('intervalo_entre_inicios_ms', intervalo)]:
            if valor is not None:
                amostras[campo].append(valor)
        for nome, ms in fases.items():
            amostras[nome].append(ms)
        self.quantidades[chave] += 1
        if trabalho > 33.333:
            self.picos[chave]['mais_33ms'] += 1
        if trabalho > 50:
            self.picos[chave]['mais_50ms'] += 1
        if trabalho > 100:
            self.picos[chave]['mais_100ms'] += 1
        if self.contagem % 120 == 0:
            self.rss_mb = _memoria_rss_mb()
            if self.rss_mb is not None:
                self.rss_pico_mb = max(self.rss_pico_mb or 0, self.rss_mb)
        linha = {'modo': modo, 'bioma': bioma, 'total_ms': round(total, 3),
                 'trabalho_ms': round(trabalho, 3), 'cpu_ms': round(cpu, 3),
                 'intervalo_ms': round(intervalo, 3) if intervalo is not None else None,
                 'rss_mb': self.rss_mb}
        self.ultimos.append(linha)
        if trabalho >= 33.333:
            evento = dict(linha, fases_ms={k: round(v, 3) for k, v in fases.items()})
            self.piores.append(evento)
            self.piores.sort(key=lambda x: x['trabalho_ms'], reverse=True)
            del self.piores[100:]
        if self.contagem % 600 == 0:
            self.salvar()

    def relatorio(self):
        por_modo_bioma = {}
        for chave, amostras in self.agregados.items():
            resumo = {nome: _stats(list(valores)) for nome, valores in amostras.items()}
            gaps = resumo.get('intervalo_entre_inicios_ms', {})
            media_gap = gaps.get('media')
            por_modo_bioma[chave] = {
                'quadros_observados': self.quantidades[chave],
                'fps_cadencia_estimado': round(1000 / media_gap, 2) if media_gap else None,
                'metricas_ms': resumo, 'travamentos_trabalho': dict(self.picos[chave]),
            }
        return {
            'schema': 'pixelrush.qa.android.v1', 'versao': self.versao, 'edicao': self.edicao,
            'quadros_observados': self.contagem, 'grupos': por_modo_bioma,
            'rss_atual_mb': self.rss_mb, 'rss_pico_observado_mb': self.rss_pico_mb,
            'piores_100_quadros_sem_limitador': self.piores,
            'gpu_ms_real': None, 'gpu_estado': 'nao_disponivel_no_pygame; usar Perfetto/gfxinfo Android',
            'renderer_backend_qa': _renderer_backend_qa(),
            'observacoes': [
                'Fases principais exclusivas; subsistemas dentro delas: NAO somar duas vezes.',
                'render_residual_estimado = renderizacao_e_ui menos passes medidos; nao representa um intervalo contiguo.',
                'CPU de processo inclui threads SDL/audio; nao e porcentagem de um nucleo.',
                'apresentacao inclui scale/blit/pygame.display.flip e espera do driver; nao prova gargalo GPU.',
                'FPS estimado por intervalo entre inicios, inclui limitador e pausas do SO.',
                'Travamentos calculados por trabalho sem espera intencional do limitador.',
                'Janela de 1800 amostras recentes por grupo, ultimos 4000 quadros em CSV.',
                'A gravacao periodica a cada 600 frames pode acrescentar custo de I/O ao quadro seguinte.',
                'Nenhum save, entrada de jogador, identificador pessoal ou conteudo do frame coletado.',
            ],
            'exportacoes_realizadas': self.gravacoes, 'erros_exportacao': self.erros_escrita,
            'ultimo_erro_exportacao': self.ultima_falha,
        }

    def salvar(self):
        try:
            self.pasta.mkdir(parents=True, exist_ok=True)
            arquivo = self.pasta / 'pixelrush_qa_v327732.json'
            temporario = self.pasta / 'pixelrush_qa_v327732.json.tmp'
            temporario.write_text(json.dumps(self.relatorio(), ensure_ascii=False, indent=2), encoding='utf-8')
            os.replace(temporario, arquivo)
            csv_final = self.pasta / 'pixelrush_qa_frames_v327732.csv'
            csv_tmp = self.pasta / 'pixelrush_qa_frames_v327732.csv.tmp'
            with csv_tmp.open('w', encoding='utf-8', newline='') as f:
                campos = ['modo', 'bioma', 'total_ms', 'trabalho_ms', 'cpu_ms', 'intervalo_ms', 'rss_mb']
                w = csv.DictWriter(f, fieldnames=campos)
                w.writeheader()
                w.writerows(self.ultimos)
            os.replace(csv_tmp, csv_final)
            self.gravacoes += 1
            self.ultima_falha = None
            return True
        except (OSError, ValueError, TypeError) as erro:
            self.erros_escrita += 1
            self.ultima_falha = type(erro).__name__
            return False