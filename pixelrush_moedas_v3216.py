"""Formacoes geometricas v3.216.0.

Somente dados de posicao de moedas. Precalculo uma vez no import, sem
surfaces, alocacoes de sprites ou trigonometria no loop de jogo.
As geometrias existentes permanecem no gerador original.
"""
import math


def _espiral():
    # Espiral horizontal compacta; remove pontos proximos ao centro para
    # evitar sprites de moedas visualmente sobrepostos.
    candidatos = (
        (round((17 + 4 * i) * math.cos(i * .62)),
         round((13 + 2.8 * i) * math.sin(i * .62)))
        for i in range(20)
    )
    pontos = []
    for x, y in candidatos:
        if all((x - px) ** 2 + (y - py) ** 2 >= 23 ** 2
               for px, py in pontos):
            pontos.append((x, y))
    return tuple(pontos)


def _oito():
    # Dois aneis lado a lado sem centros sobrepostos.
    return tuple(
        (round(cx + 36 * math.cos(2 * math.pi * i / 8)),
         round(-5 + 34 * math.sin(2 * math.pi * i / 8)))
        for cx in (36, 134) for i in range(8)
    )


# Desenhos imutaveis e sem sorteios adicionais: todos utilizam o pool
# original, a mesma limitacao de altura e os sprites/moedas originais.
PADROES_GEOMETRICOS_3216 = {
    "HELICE_DUPLA": tuple(
        (i * 29, round(-31 + 8 * math.sin(i * .83)))
        for i in range(7)
    ) + tuple(
        (i * 29 + 2, round(14 - 8 * math.sin(i * .83)))
        for i in range(7)
    ),
    "OITO_DUPLO": _oito(),
    "RAMPA_MERGULHO": tuple(
        (i * 27, round(-53 * math.sin(i / 10 * math.pi)))
        for i in range(11)
    ),
    "TUNEL_COLETA": tuple(
        (i * 30, altura) for i in range(7) for altura in (-36, 10)
    ),
    "PONTE_INTERROMPIDA": tuple(
        (i * 28, round(-48 * math.sin(i / 11 * math.pi)))
        for i in range(12) if i not in (5, 6)
    ),
    "ONDA_TRIPLA": tuple(
        (i * 30, round(10 * math.sin(i * .9)) + altura)
        for i in range(5) for altura in (-55, -19, 17)
    ),
    "ESPIRAL_ACHATADA": _espiral(),
    "LOSANGOS_ENCADEADOS": (
        (0, 0), (25, -25), (50, 0), (25, 25),
        (78, 0), (103, -25), (128, 0), (103, 25),
        (154, 0), (179, -25), (204, 0), (179, 25),
    ),
}

# Validacao offline tambem funciona sem Pygame e nao roda por quadro.
if __debug__:
    for _nome, _pontos in PADROES_GEOMETRICOS_3216.items():
        assert 8 <= len(_pontos) <= 16, _nome
        assert max(x for x, _ in _pontos) - min(x for x, _ in _pontos) <= 310
        assert max(y for _, y in _pontos) - min(y for _, y in _pontos) <= 140
        assert len(set(_pontos)) == len(_pontos), _nome
        assert all(
            (x - x2) ** 2 + (y - y2) ** 2 >= 23 ** 2
            for i, (x, y) in enumerate(_pontos)
            for x2, y2 in _pontos[i+1:]
        ), _nome
