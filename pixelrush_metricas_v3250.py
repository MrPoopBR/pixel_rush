"""v3.250.0 — métricas LOCAIS e opt-in de corridas concluídas (P19/P21).

Não importa pygame nem modifica RNG, save, render, controles ou física.
O JSONL é criado somente ao concluir uma partida com a coleta explicitamente ligada.
Falhas de gravação nunca impedem a corrida nem a tela de game over.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import random
import time
import uuid


SCHEMA = 'pixelrush.corrida.v1'
CHAVE_AMBIENTE = 'PIXELRUSH_METRICAS_CORRIDA'
CAMINHO_AMBIENTE = 'PIXELRUSH_METRICAS_PATH'


class MetricasCorrida:
    """Observação leve somente na entrada/saída da corrida, sem hooks por quadro."""

    def __init__(self, versao: str, edicao: str, *, habilitado=None, caminho=None):
        self.habilitado = (os.environ.get(CHAVE_AMBIENTE, '') == '1') if habilitado is None else bool(habilitado)
        self.versao = str(versao)
        self.edicao = str(edicao)
        self.caminho = Path(caminho if caminho is not None else os.environ.get(CAMINHO_AMBIENTE) or 'metricas_corridas_v3250.jsonl')
        self._corrida = None
        self.ultimo_erro = None

    def iniciar(self, *, skin: str, pet: str, bioma: str, quadro: int):
        if not self.habilitado:
            return
        try:
            # Consulta RNG sem gerar valores; fingerprint NÃO é semente recuperável.
            estado_hash = hashlib.sha256(repr(random.getstate()).encode('ascii')).hexdigest()[:16]
            self._corrida = {
                'id_corrida': uuid.uuid4().hex,
                'skin': str(skin), 'pet': str(pet), 'bioma_inicial': str(bioma),
                'quadro_inicial': int(quadro), 'fingerprint_rng': estado_hash,
                'inicio_monotonico': time.monotonic(),
            }
            self.ultimo_erro = None
        except Exception as exc:
            self._corrida = None
            self.ultimo_erro = type(exc).__name__

    def encerrar(self, *, quadro: int, bioma: str, distancia_m: int, moedas: int,
                 maior_combo: int, quase_colisoes: int, esquivas: int,
                 powerups: int, obstaculos_destruidos: int, fases_bonus: int,
                 chefes: int, portais: dict, febres: int, baus: int):
        if not self.habilitado or self._corrida is None:
            return
        inicio, self._corrida = self._corrida, None  # impede duplicação do registro
        try:
            duracao = max(0.0, time.monotonic() - inicio['inicio_monotonico'])
            distancia = max(0, int(distancia_m))
            coletadas = max(0, int(moedas))
            registro = {
                'schema': SCHEMA, 'versao': self.versao, 'edicao': self.edicao,
                'id_corrida': inicio['id_corrida'], 'resultado': 'morte',
                'skin': inicio['skin'], 'pet': inicio['pet'],
                'bioma_inicial': inicio['bioma_inicial'], 'bioma_final': str(bioma),
                'fingerprint_rng': inicio['fingerprint_rng'],
                'quadros_desde_inicio': max(0, int(quadro) - inicio['quadro_inicial']),
                'duracao_relogio_s': round(duracao, 3),
                'distancia_m': distancia, 'moedas_coletadas': coletadas,
                'moedas_por_100m': round(coletadas * 100 / distancia, 3) if distancia else 0.0,
                'maior_combo': max(0, int(maior_combo)),
                'quase_colisoes': max(0, int(quase_colisoes)),
                'esquivas_perfeitas': max(0, int(esquivas)),
                'powerups_coletados': max(0, int(powerups)),
                'obstaculos_destruidos': max(0, int(obstaculos_destruidos)),
                'fases_bonus': max(0, int(fases_bonus)),
                'chefes_derrotados': max(0, int(chefes)),
                'portais_aquaticos': max(0, int(portais.get('AQUATICO', 0))),
                'portais_lasers': max(0, int(portais.get('LASERS', 0))),
                'febres': max(0, int(febres)), 'baus_abertos': max(0, int(baus)),
            }
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            with self.caminho.open('a', encoding='utf-8') as arquivo:
                arquivo.write(json.dumps(registro, ensure_ascii=False, sort_keys=True) + '\n')
            self.ultimo_erro = None
        except Exception as exc:
            # Observabilidade é opcional: jamais propagar erros para o jogo.
            self.ultimo_erro = type(exc).__name__


def criar_coletor(versao: str, edicao: str) -> MetricasCorrida:
    return MetricasCorrida(versao, edicao)
