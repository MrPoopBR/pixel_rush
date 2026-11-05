# -*- coding: utf-8 -*-
"""Plano H v3.212.0: sementes compartilháveis e recordes locais, sem rede.

O código configura somente o gerador random global quando o usuário escolhe
um desafio. A igualdade total de eventos SDL / tempo de renderização entre
hardware diferente NÃO é garantida. O modo normal não chama random.seed.
"""
from datetime import date
import hashlib
import random

PREFIXO = 'PR-'
MAX_RECORDES = 32


def normalizar_codigo(texto):
    """Retorna PR-NNNNNN ou lança ValueError; aceita digitos ou prefixo PR-."""
    if not isinstance(texto, str):
        raise ValueError('Código inválido')
    texto = texto.strip().upper()
    if texto.startswith(PREFIXO):
        texto = texto[len(PREFIXO):]
    if len(texto) != 6 or not (texto.isascii() and texto.isdecimal()):
        raise ValueError('O código precisa ter seis dígitos')
    return PREFIXO + texto


def codigo_diario(hoje=None):
    hoje = hoje or date.today()
    bruto = ('PIXELRUSH-H212-DIARIO-V1:' + hoje.isoformat()).encode('ascii')
    numero = int.from_bytes(hashlib.sha256(bruto).digest()[:8], 'big') % 1000000
    return PREFIXO + ('%06d' % numero)


def semente(codigo):
    return int(normalizar_codigo(codigo)[len(PREFIXO):])


class DesafioPercurso:
    def __init__(self):
        self.codigo = None
        self.ultimo_resultado = None

    def escolher(self, codigo):
        self.codigo = normalizar_codigo(codigo)
        self.ultimo_resultado = None
        return self.codigo

    def cancelar(self):
        self.codigo = None

    def preparar_corrida(self):
        """Chamar antes de iniciar a nova corrida, apenas para código ativo."""
        if self.codigo is not None:
            random.seed(semente(self.codigo))
            return True
        return False

    def registrar_morte(self, dados, metros):
        """Só atualiza recorde de desafio; nunca concede recompensas."""
        if self.codigo is None:
            return False
        if not isinstance(dados, dict):
            return False
        placar = dados.setdefault('desafios_percurso_v3212', {})
        if not isinstance(placar, dict):
            placar = {}
            dados['desafios_percurso_v3212'] = placar
        anterior = max(0, int(placar.get(self.codigo, 0)))
        atual = max(0, min(100000000, int(metros)))
        self.ultimo_resultado = atual
        if atual <= anterior:
            return False
        # Ordem de inserção determina quais desafios antigos descartar.
        placar.pop(self.codigo, None)
        placar[self.codigo] = atual
        while len(placar) > MAX_RECORDES:
            placar.pop(next(iter(placar)))
        return True

    def recorde(self, dados, codigo=None):
        chave = normalizar_codigo(codigo) if codigo else self.codigo
        if chave is None:
            return 0
        placar = dados.get('desafios_percurso_v3212', {})
        return max(0, int(placar.get(chave, 0))) if isinstance(placar, dict) else 0
