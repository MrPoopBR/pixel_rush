# -*- coding: utf-8 -*-
"""Funções extraídas sem reescrever algoritmos da v3.277.89-QA.
Nomes de funções permanecem importados no motor nos pontos originais.
"""

def saturar_cor(cor, fator=1.1):
    media = sum(cor) / 3.0
    return tuple(max(0, min(255, int(media + (c - media) * fator))) for c in cor)

def misturar_cores(cor_a, cor_b, proporcao):
    """Mistura duas cores RGB sem superfícies alpha (compatível com SDL/Android)."""
    t = max(0.0, min(1.0, float(proporcao)))
    return tuple(max(0, min(255, int(cor_a[i] + (cor_b[i] - cor_a[i]) * t))) for i in range(3))

