# -*- coding: utf-8 -*-
"""Plano H 3.205 — fita de eventos para QA, opt-in, sem tocar o gameplay normal.

Registra seed global, tempo do loop, eventos SDL (incluindo timer de spawn),
estados de teclas/mouse e assinatura de estado em JSONL compacto.
Na reproducao injeta as mesmas entradas por quadro; registra divergencias.
Nao garante bit-exatidao entre hardwares/versoes SDL diferentes.
"""
import json
import os
import random
from pathlib import Path

TECLAS = (32, 1073741906, 119, 1073741905, 115)  # space, up, w, down, s
ATRIBUTOS = ('key', 'mod', 'unicode', 'scancode', 'pos', 'rel', 'button', 'buttons',
             'x', 'y', 'dx', 'dy', 'finger_id', 'touch_id', 'pressure',
             'gain', 'state', 'size', 'w', 'h', 'which', 'axis', 'value', 'hat')
MAX_LINHA = 65536


class _Teclas:
    def __init__(self, marcadas):
        self.marcadas = set(int(k) for k in marcadas)

    def __getitem__(self, k):
        return int(k) in self.marcadas


class _Mouse:
    def __init__(self, flags):
        self.flags = tuple(bool(x) for x in flags)

    def __getitem__(self, k):
        return self.flags[k] if k < len(self.flags) else False


class FitaQA:
    def __init__(self, versao, edicao):
        self.versao, self.edicao = versao, edicao
        self.modo = os.environ.get('PIXELRUSH_REPRO', 'off').strip().lower()
        if self.modo not in ('record', 'replay'):
            self.modo = 'off'
        self.ativo = self.modo != 'off'
        self.caminho = Path(os.environ.get('PIXELRUSH_REPRO_PATH',
                             'diagnosticos/corrida_qa_%s.jsonl' % edicao))
        try:
            limite = int(os.environ.get('PIXELRUSH_REPRO_MAX_FRAMES', '12000'))
        except ValueError:
            limite = 12000
        self.max_quadros = max(1, min(60000, limite))
        self.max_bytes = 12 * 1024 * 1024
        self.quadros = 0
        self.erros = []
        self.arquivo = None
        self.base_tempo = 0
        self.tempo_atual = 0
        self.linha = None
        self.seed = None
        self.bytes_escritos = 0
        self.parar = False
        self._header = None
        if not self.ativo:
            return
        try:
            if self.modo == 'record':
                self.caminho.parent.mkdir(parents=True, exist_ok=True)
                self.arquivo = self.caminho.open('w', encoding='utf-8')
                self.seed = int(os.environ.get('PIXELRUSH_REPRO_SEED', '2052026'))
                self._header = {'tipo':'pixelrush_qa_fita', 'versao':self.versao,
                                'edicao':self.edicao, 'formato':1, 'seed':self.seed,
                                'teclas':list(TECLAS), 'reprodutibilidade':'diagnostico'}
                self._gravar(self._header)
            else:
                self.arquivo = self.caminho.open('r', encoding='utf-8')
                primeira = self.arquivo.readline()
                if len(primeira) > MAX_LINHA:
                    raise ValueError('Cabecalho grande demais')
                self._header = json.loads(primeira)
                if (self._header.get('tipo') != 'pixelrush_qa_fita' or
                        self._header.get('formato') != 1 or
                        self._header.get('edicao') != self.edicao):
                    raise ValueError('Fita invalida ou de outra edicao')
                self.seed = int(self._header['seed'])
            random.seed(self.seed)  # SOMENTE opt-in de QA
        except (OSError, ValueError, KeyError, TypeError) as exc:
            self.erros.append('Preparacao: %s' % exc)
            self.fechar()
            self.ativo = False
            self.modo = 'off'

    def _gravar(self, item):
        blob = json.dumps(item, separators=(',', ':'), ensure_ascii=False)
        if len(blob) > MAX_LINHA:
            raise ValueError('Linha de eventos excedeu limite')
        self.arquivo.write(blob + '\n')
        self.bytes_escritos += len(blob.encode('utf-8')) + 1

    def iniciar_relogio(self, agora):
        if self.ativo:
            self.base_tempo = int(agora)
        return agora

    def inicio_quadro(self, agora):
        if not self.ativo:
            return agora
        self.quadros += 1
        self.tempo_atual = int(agora)
        if self.modo == 'record':
            self.linha = {'q':self.quadros, 't':max(0, int(agora) - self.base_tempo),
                          'e':[], 'k':[], 'm':[]}
            return agora
        if self.parar:
            self.linha = None
            return self.tempo_atual
        try:
            texto = self.arquivo.readline()
            if not texto or len(texto) > MAX_LINHA:
                self.parar = True
                self.linha = None
                return agora
            self.linha = json.loads(texto)
            if self.linha.get('q') != self.quadros:
                raise ValueError('Indice de quadro inconsistente')
            self.tempo_atual = self.base_tempo + int(self.linha['t'])
            return self.tempo_atual
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            self.erros.append('Leitura quadro %d: %s' % (self.quadros, exc))
            self.parar = True
            self.linha = None
            return agora

    def tempo(self, agora):
        return self.tempo_atual if self.modo == 'replay' and self.linha else agora

    @staticmethod
    def _evento_registro(evento):
        attrs = {}
        for nome in ATRIBUTOS:
            if hasattr(evento, nome):
                val = getattr(evento, nome)
                if isinstance(val, (str, int, float, bool)) or val is None:
                    attrs[nome] = val
                elif isinstance(val, (tuple, list)) and len(val) <= 8 and all(
                        isinstance(x, (str, int, float, bool)) for x in val):
                    attrs[nome] = list(val)
        return [int(evento.type), attrs]

    def eventos(self, eventos_reais):
        if not self.ativo:
            return eventos_reais
        if self.modo == 'record':
            if self.linha is not None:
                self.linha['e'] = [self._evento_registro(e) for e in eventos_reais[:256]]
            return eventos_reais
        import pygame
        if self.parar or self.linha is None:
            return [pygame.event.Event(pygame.QUIT)]
        # Permite encerrar manualmente uma reproducao; ignora outros eventos vivos.
        if any(e.type == pygame.QUIT for e in eventos_reais):
            return [pygame.event.Event(pygame.QUIT)]
        try:
            return [pygame.event.Event(int(t), **a) for t, a in self.linha.get('e', [])]
        except (ValueError, TypeError) as exc:
            self.erros.append('Evento %d: %s' % (self.quadros, exc))
            self.parar = True
            return [pygame.event.Event(pygame.QUIT)]

    def entradas(self, teclas, mouse):
        if not self.ativo or self.linha is None:
            return teclas, mouse
        if self.modo == 'record':
            self.linha['k'] = [k for k in TECLAS if teclas[k]]
            self.linha['m'] = [bool(mouse[i]) for i in range(3)]
            return teclas, mouse
        return _Teclas(self.linha.get('k', [])), _Mouse(self.linha.get('m', [False]*3))

    def fim_quadro(self, estado, bioma, metros, sim_ticks, jogador):
        if not self.ativo or self.linha is None:
            return
        pos = None if jogador is None else [int(jogador.rect.x), int(jogador.rect.y)]
        assinatura = [str(estado), str(bioma), int(metros), int(sim_ticks), pos]
        if self.modo == 'record':
            self.linha['s'] = assinatura
            try:
                if self.quadros <= self.max_quadros and self.bytes_escritos < self.max_bytes:
                    self._gravar(self.linha)
                    if self.quadros % 60 == 0:
                        self.arquivo.flush()
                else:
                    self.erros.append('Limite de tamanho/quadros de fita atingido')
                    self.ativo = False
            except (OSError, ValueError) as exc:
                self.erros.append('Escrita: %s' % exc)
                self.ativo = False
        elif assinatura != self.linha.get('s') and len(self.erros) < 40:
            self.erros.append('Divergencia no quadro %d: esperado=%r, real=%r' %
                              (self.quadros, self.linha.get('s'), assinatura))
        self.linha = None

    def fechar(self):
        if self.arquivo:
            try:
                self.arquivo.flush()
                self.arquivo.close()
            except OSError:
                pass
            self.arquivo = None
        if self.erros and self.modo == 'replay':
            try:
                caminho = self.caminho.with_suffix('.divergencias.txt')
                caminho.write_text('\n'.join(self.erros), encoding='utf-8')
            except OSError:
                pass


_ATUAL = None


def executar_com_repro(funcao, versao, edicao):
    global _ATUAL
    _ATUAL = FitaQA(versao, edicao)
    try:
        return funcao()
    finally:
        _ATUAL.fechar()
        _ATUAL = None


def iniciar_relogio(agora):
    return _ATUAL.iniciar_relogio(agora) if _ATUAL is not None else agora


def inicio_quadro(agora):
    return _ATUAL.inicio_quadro(agora) if _ATUAL is not None else agora


def tempo(agora):
    return _ATUAL.tempo(agora) if _ATUAL is not None else agora


def eventos(lista):
    return _ATUAL.eventos(lista) if _ATUAL is not None else lista


def entradas(teclas, mouse):
    return _ATUAL.entradas(teclas, mouse) if _ATUAL is not None else (teclas, mouse)


def fim_quadro(estado, bioma, metros, sim_ticks, jogador):
    if _ATUAL is not None:
        _ATUAL.fim_quadro(estado, bioma, metros, sim_ticks, jogador)
