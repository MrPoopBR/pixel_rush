# -*- coding: utf-8 -*-
"""Funções extraídas sem reescrever algoritmos da v3.277.89-QA.
Nomes de funções permanecem importados no motor nos pontos originais.
"""

def _suavizar_intervalo(inicio, fim, valor):
    """Smoothstep barato para transicoes graduais do ciclo dia/noite."""
    if fim <= inicio:
        return 1.0 if valor >= fim else 0.0
    x = max(0.0, min(1.0, (valor - inicio) / float(fim - inicio)))
    return x * x * (3.0 - 2.0 * x)

