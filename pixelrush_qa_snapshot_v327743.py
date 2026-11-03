# -*- coding: utf-8 -*-
"""PIXEL RUSH QA v3.277.43: snapshot periodico em parcelas seguras por frame.

Nao toca pygame, fisica, saves ou entradas. Percentis/JSON/CSV continuam
fora do frame e a exportacao final continua sincronizada na saida.
"""
from collections import deque


class CapturaParceladaQA:
    def __init__(self, qa):
        self.grupos = {}
        tarefas = []
        for chave, amostras in tuple(qa.agregados.items()):
            self.grupos[chave] = {
                'quadros_observados': qa.quantidades[chave],
                'amostras': {},
                'travamentos_trabalho': dict(qa.picos[chave]),
            }
            for nome, valores in tuple(amostras.items()):
                tarefas.append((chave, nome, valores))
        self._tarefas = deque(tarefas)
        # Uma unica copia de referencias; sem copiar milhares de dicts aqui.
        self._src_linhas = tuple(qa.ultimos)
        self._indice = 0
        self._linhas = []
        self.copiadas = 0

    def passo(self, max_metricas=2, max_linhas=64):
        """Uma chamada/quadra: no maximo 2 deques e 64 dicts, sem I/O."""
        if max_metricas < 1 or max_linhas < 1:
            raise ValueError('orcamento de snapshot QA invalido')
        for _ in range(max_metricas):
            if not self._tarefas:
                break
            chave, nome, valores = self._tarefas.popleft()
            self.grupos[chave]['amostras'][nome] = tuple(valores)
            self.copiadas += 1
        fim = min(len(self._src_linhas), self._indice + max_linhas)
        for linha in self._src_linhas[self._indice:fim]:
            self._linhas.append(dict(linha))
        self._indice = fim
        if self._tarefas or self._indice < len(self._src_linhas):
            return None
        return self.grupos, tuple(self._linhas)
