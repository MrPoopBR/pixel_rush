# -*- coding: utf-8 -*-
"""Funções extraídas sem reescrever algoritmos da v3.277.89-QA.
Nomes de funções permanecem importados no motor nos pontos originais.
"""

from datetime import date
import random

def chave_periodo_semanal(hoje=None):
    hoje = hoje or date.today()
    iso = hoje.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"

def gerar_missoes_rodada():
    """Gera 3 missões variadas; alvos equilibrados para corridas curtas e longas."""
    banco_missoes = [
        {"tipo": "MOEDAS", "key": "missao_moedas", "alvo": random.randint(90, 220), "atual": 0, "recompensa": 100, "concluida": False},
        {"tipo": "DISTANCIA", "key": "missao_distancia", "alvo": random.randint(700, 1600), "atual": 0, "recompensa": 180, "concluida": False},
        {"tipo": "QUEBRAR", "key": "missao_quebrar", "alvo": random.randint(8, 18), "atual": 0, "recompensa": 130, "concluida": False},
        {"tipo": "PULOS", "key": "missao_pulos", "alvo": random.randint(25, 70), "atual": 0, "recompensa": 90, "concluida": False},
        {"tipo": "POWERUPS", "key": "missao_powerups", "alvo": random.randint(3, 8), "atual": 0, "recompensa": 120, "concluida": False},
        {"tipo": "SLOW", "key": "missao_slow", "alvo": random.randint(2, 5), "atual": 0, "recompensa": 80, "concluida": False},
        {"tipo": "COMBO", "key": "missao_combo", "alvo": random.choice((12, 18, 25)), "atual": 0, "recompensa": 140, "concluida": False},
        {"tipo": "BAUS", "key": "missao_baus", "alvo": random.choice((1, 2, 3)), "atual": 0, "recompensa": 150, "concluida": False},
        {"tipo": "FEBRE", "key": "missao_febre", "alvo": 1, "atual": 0, "recompensa": 160, "concluida": False},
        {"tipo": "QUASE", "key": "missao_quase", "alvo": random.randint(3, 8), "atual": 0, "recompensa": 120, "concluida": False},
    ]
    # Não sortear missão que depende de power-up ainda bloqueado ou evento
    # suspenso na edição de produção; somente objetivos possíveis para todos.
    banco_missoes = [m for m in banco_missoes
                     if m['tipo'] not in ('QUEBRAR', 'POWERUPS', 'SLOW')]
    return random.sample(banco_missoes, 3)

