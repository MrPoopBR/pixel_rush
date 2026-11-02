# -*- coding: utf-8 -*-
"""Exportacao QA 3.277.37 fora do frame, sem tocar saves ou jogo.

A thread recebe APENAS snapshots JSON e CSV (sem Surface/pygame).
Preserva gravacao atomica anterior e serializacao FIFO. Na saida,
fechar() garante que o ultimo snapshot foi gravado.
"""
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import os
from pathlib import Path


def _escrever(pasta, prefixo, relatorio, linhas, preparar_relatorio=None):
    # Estatisticas pesadas calculadas no worker sobre snapshot desconectado
    # das deques e superficies usadas no frame principal.
    if preparar_relatorio is not None:
        relatorio = preparar_relatorio(relatorio)
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    destino_json = pasta / (prefixo + '.json')
    temporario_json = pasta / (prefixo + '.json.tmp')
    temporario_json.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding='utf8')
    os.replace(temporario_json, destino_json)
    destino_csv = pasta / (prefixo.replace('pixelrush_qa_v', 'pixelrush_qa_frames_v') + '.csv')
    temporario_csv = destino_csv.with_suffix('.csv.tmp')
    with temporario_csv.open('w', encoding='utf8', newline='') as arquivo:
        campos = ['modo','bioma','total_ms','trabalho_ms','cpu_ms','intervalo_ms','rss_mb']
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)
    os.replace(temporario_csv, destino_csv)
    return True


class GravadorQA:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='pixelrush-qa-io')
        self._pendente = None
        self.concluidas = 0
        self.falhas = 0
        self.ultimo_erro = None

    def _conferir(self, esperar):
        futuro = self._pendente
        if futuro is None:
            return True
        if not esperar and not futuro.done():
            return False
        try:
            futuro.result()
            self.concluidas += 1
            self.ultimo_erro = None
        except (OSError,ValueError,TypeError) as exc:
            self.falhas += 1
            self.ultimo_erro = type(exc).__name__
        self._pendente = None
        return True

    def enviar(self, pasta, prefixo, relatorio, linhas, esperar=False, preparar_relatorio=None):
        # So a thread principal chama enviar(). Nenhum dado mutavel do jogo
        # e acessado pelo worker: as linhas e relatorio sao snapshots.
        if not self._conferir(esperar):
            return False
        self._pendente = self._executor.submit(
            _escrever, Path(pasta), str(prefixo), relatorio,
            tuple(dict(l) for l in linhas), preparar_relatorio)
        if esperar:
            self._conferir(True)
        return True

    def finalizar(self):
        self._conferir(True)
        self._executor.shutdown(wait=True)
