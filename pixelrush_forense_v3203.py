"""Plano H v3.203: diagnostico forense de encerramentos do Pixel Rush.

Independente do profiler de desempenho v3154. Nao muda eventos, simulacao,
renderizacao ou saves. DEV: habilitado por padrao; LIMPA: apenas opt-in.
PIXELRUSH_FORENSE=0/1 e PIXELRUSH_FORENSE_PATH=<diretorio> controlam os logs.
Falhas de I/O neste componente nunca podem interromper a partida.
"""
import atexit
import faulthandler
import json
import os
from pathlib import Path
import sys
import threading
import time
import traceback
from collections import deque
from datetime import datetime, timezone

_ATIVO = None
_VERSAO_REGISTRO = 'v3.203.0'


def _carimbo():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _atualizar_json(caminho, objeto):
    """Escrita atomica: evita arquivo truncado se o processo cair no meio."""
    temporario = caminho.with_name(caminho.name + '.tmp')
    with open(temporario, 'w', encoding='utf-8') as fluxo:
        json.dump(objeto, fluxo, ensure_ascii=False, sort_keys=True, indent=2)
        fluxo.flush()
        os.fsync(fluxo.fileno())
    os.replace(str(temporario), str(caminho))


class DiarioForense:
    def __init__(self, versao, edicao, pasta):
        self.versao = str(versao)
        self.edicao = str(edicao)
        self.pasta = Path(pasta)
        self.destino = self.pasta / ('ultima_sessao_' + self.edicao + '.json')
        self.incidentes = self.pasta / ('incidentes_' + self.edicao + '.jsonl')
        self.erro_io = None
        self.solicitou_quit = False
        self.terminou = False
        self.frames = 0
        self.estado = 'INICIALIZANDO'
        self.bioma = 'indeterminado'
        self.metros = 0
        self.qualidade = 'indeterminada'
        self.inicio = time.monotonic()
        self.ultimo_disco = self.inicio
        self.marcos = deque(maxlen=24)
        self.marcos.append({'evento': 'inicio', 'utc': _carimbo(), 'quadro': 0})
        self.pasta.mkdir(parents=True, exist_ok=True)
        self._identificar_anterior()
        self.gravar('executando')

    def _identificar_anterior(self):
        try:
            if not self.destino.exists():
                return
            anterior = json.loads(self.destino.read_text(encoding='utf-8'))
            if anterior.get('situacao') == 'executando':
                self._incidente({
                    'tipo': 'sessao_anterior_sem_fechamento',
                    'explicacao': 'Pode ser falha, kill do Android ou interrupcao externa; nao comprova crash.',
                    'observado_utc': _carimbo(),
                    'ultima_sessao': anterior,
                })
        except (OSError, ValueError, TypeError) as exc:
            self.erro_io = type(exc).__name__

    def _incidente(self, item):
        """Historico limitado para nao aumentar indefinidamente o armazenamento."""
        try:
            if self.incidentes.exists() and self.incidentes.stat().st_size > 131072:
                backup = self.incidentes.with_suffix('.jsonl.old')
                os.replace(str(self.incidentes), str(backup))
            with open(self.incidentes, 'a', encoding='utf-8') as saida:
                saida.write(json.dumps(item, ensure_ascii=False, separators=(',', ':')) + '\n')
        except (OSError, ValueError, TypeError) as exc:
            self.erro_io = type(exc).__name__

    def resumo(self, situacao):
        return {
            'formato': 1, 'modulo': _VERSAO_REGISTRO,
            'versao_jogo': self.versao, 'edicao': self.edicao,
            'situacao': situacao, 'utc': _carimbo(),
            'segundos_desde_inicio': round(time.monotonic() - self.inicio, 2),
            'quadros': self.frames, 'estado': self.estado, 'bioma': self.bioma,
            'metros_aproximados': self.metros, 'qualidade': self.qualidade,
            'recebeu_evento_quit': self.solicitou_quit,
            'ultimos_marcos': list(self.marcos),
            'erro_gravacao': self.erro_io,
        }

    def gravar(self, situacao):
        try:
            _atualizar_json(self.destino, self.resumo(situacao))
            self.ultimo_disco = time.monotonic()
        except (OSError, ValueError, TypeError) as exc:
            self.erro_io = type(exc).__name__

    def quadro(self, estado, bioma, metros, qualidade):
        self.frames += 1
        mudou = estado != self.estado or bioma != self.bioma
        self.estado, self.bioma = str(estado)[:48], str(bioma)[:48]
        self.qualidade = str(qualidade)[:24]
        try:
            self.metros = max(0, int(metros))
        except (TypeError, ValueError):
            pass
        if mudou:
            self.marcos.append({'evento': 'mudanca_de_contexto', 'quadro': self.frames,
                                'estado': self.estado, 'bioma': self.bioma})
        elif self.frames % 120 == 0:
            self.marcos.append({'evento': 'checkpoint', 'quadro': self.frames,
                                'estado': self.estado, 'bioma': self.bioma})
        # Salvar ao mudar de tela/bioma, alem do batimento a cada 5 s.
        # Crucial para quedas prematuras (1-122 quadros) observadas na DEV.
        # Nao existe I/O por quadro; estados estaveis so atualizam a cada 5 s.
        if mudou or (self.frames % 60 == 0 and
                     time.monotonic() - self.ultimo_disco >= 5.0):
            self.gravar('executando')

    def quit(self, motivo):
        self.solicitou_quit = True
        self.marcos.append({'evento': 'saida_solicitada', 'motivo': str(motivo)[:40],
                            'quadro': self.frames})

    def finalizar(self, situacao, excecao=None):
        if self.terminou:
            return
        self.terminou = True
        if excecao is not None:
            pilha = ''.join(traceback.format_exception(type(excecao), excecao, excecao.__traceback__))[-12000:]
            self._incidente({'tipo': situacao, 'utc': _carimbo(),
                             'classe': type(excecao).__name__, 'traceback': pilha,
                             'contexto': self.resumo(situacao)})
        elif situacao == 'retorno_sem_quit':
            self._incidente({'tipo': situacao, 'utc': _carimbo(),
                             'contexto': self.resumo(situacao)})
        self.marcos.append({'evento': 'encerramento', 'tipo': situacao,
                            'quadro': self.frames})
        self.gravar(situacao)


def checkpoint(estado, bioma, metros, qualidade):
    # No modo normal LIMPA, _ATIVO=None: apenas um teste e retorno imediato.
    if _ATIVO is not None:
        _ATIVO.quadro(estado, bioma, metros, qualidade)


def solicitar_saida(motivo='pygame.QUIT'):
    if _ATIVO is not None:
        _ATIVO.quit(motivo)


def executar_com_forense(funcao, versao, edicao):
    global _ATIVO
    valor = os.environ.get('PIXELRUSH_FORENSE', '').strip().lower()
    habilitar = (valor in ('1', 'true', 'sim', 'on') or
                 (not valor and edicao.upper() == 'DEV'))
    if not habilitar:
        return funcao()
    caminho = os.environ.get('PIXELRUSH_FORENSE_PATH') or 'pixelrush_logs'
    try:
        monitor = DiarioForense(versao, edicao, caminho)
    except (OSError, ValueError) as exc:
        # Caminho sem permissao: a partida nao pode deixar de iniciar.
        print('Pixel Rush: log forense indisponivel:', type(exc).__name__, file=sys.stderr)
        return funcao()
    anterior = _ATIVO
    _ATIVO = monitor
    arquivo_nativo = None
    habilitou_faulthandler = False
    try:
        try:
            if not faulthandler.is_enabled():
                arquivo_nativo = open(monitor.pasta / ('falha_nativa_' + edicao + '.log'), 'a', encoding='utf-8')
                faulthandler.enable(file=arquivo_nativo, all_threads=True)
                habilitou_faulthandler = True
        except (OSError, RuntimeError, ValueError):
            if arquivo_nativo is not None:
                arquivo_nativo.close()
                arquivo_nativo = None
        try:
            resultado = funcao()
        except SystemExit as exc:
            monitor.finalizar('systemexit_sem_confirmacao_de_quit', exc)
            raise
        except KeyboardInterrupt as exc:
            monitor.finalizar('interrupcao_teclado', exc)
            raise
        except BaseException as exc:
            monitor.finalizar('falha_python', exc)
            raise
        monitor.finalizar('saida_normal' if monitor.solicitou_quit else 'retorno_sem_quit')
        return resultado
    finally:
        _ATIVO = anterior
        if habilitou_faulthandler:
            try:
                faulthandler.disable()
            except RuntimeError:
                pass
        if arquivo_nativo is not None:
            arquivo_nativo.close()
