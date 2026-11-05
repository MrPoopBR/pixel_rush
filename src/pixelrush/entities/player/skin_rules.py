# -*- coding: utf-8 -*-
"""Funções extraídas sem reescrever algoritmos da v3.277.89-QA.
Nomes de funções permanecem importados no motor nos pontos originais.
"""

def raridade_de_skin(ident):
    if ident in ('COSMICA', 'PLATINA', 'CHAMA'):
        return 'Lendário'
    if ident in ('ROXO', 'ROBO', 'DOURADO'):
        return 'Épico'
    return 'Raro' if ident in ('VERDE', 'ROSA') else 'Comum'

def nivel_visual_skin(dados):
    # Sistema de evolução visual/estilos alternativos removido.
    return 1

