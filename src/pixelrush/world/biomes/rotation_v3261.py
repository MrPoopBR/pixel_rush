"""Rotação ponderada dos sete biomas oficiais do Pixel Rush v3.261.0.

Preserva o tempo de permanência, dados de spawn e a física do jogo.
Garante próxima escolha diferente, não coloca especiais consecutivos e
usa random injetável para reprodutibilidade via fitas/seed.
"""
import random

CLASSICOS = ("cidade", "neve", "deserto")
ESPECIAIS = ("vulcao", "cidade_futurista", "floresta", "ilhas_celestes")
TODOS = CLASSICOS + ESPECIAIS
PESOS = {"cidade": 3, "neve": 3, "deserto": 3,
         "vulcao": 1, "cidade_futurista": 1, "floresta": 1, "ilhas_celestes": 1}
QUADROS_PROTECAO_TRANSICAO = 105  # igual à duração da faixa de apresentação

def candidatos(cenario_atual):
    """Bioma especial nunca precede outro especial; evita repetição direta."""
    if cenario_atual not in TODOS:
        raise ValueError("Bioma atual não pertence aos sete oficiais")
    disponiveis = CLASSICOS if cenario_atual in ESPECIAIS else TODOS
    return tuple(b for b in disponiveis if b != cenario_atual)

def sortear_proximo_cenario(cenario_atual, rng=None):
    rng = rng or random
    opcoes = candidatos(cenario_atual)
    return rng.choices(opcoes, weights=[PESOS[b] for b in opcoes], k=1)[0]
