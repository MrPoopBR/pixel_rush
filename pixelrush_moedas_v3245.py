# -*- coding: utf-8 -*-
"""Pixel Rush v3.245.0: quatro formacoes adicionais sem inflar economia.

Reutiliza os 45 formatos anteriores, o sprite Moeda, seu pool e o RNG original.
Alterna ocasionalmente APENAS desenhos com a mesma quantidade de moedas.
"""
from pixelrush_moedas_v3216 import PADROES_GEOMETRICOS_3216
import math

NOVOS_PADROES_3245 = {
    # 12 moedas cada: mesmos totais das formacoes substituiveis.
    'TRILHO_TRANCADO': tuple((26*i, -38 if i%2 else 0) for i in range(12)),
    'ESCADA_SERRILHADA': tuple((26*i, (-54,-27,0,-27)[i%4]) for i in range(12)),
    # 14 moedas, mesmo total do corredor original de 14.
    'RAMPA_PONTILHADA': tuple((23*i, int(round(-52*math.sin(math.pi*i/13))) + (6 if i%2 else 0)) for i in range(14)),
    # 16 moedas, duas pistas deslocadas, sem sobreposicoes.
    'TRILHO_ALTERNADO': tuple((39*i, 0) for i in range(8)) +
                         tuple((39*i+15, -42) for i in range(8)),
}

# Acesso somente de leitura por contrato; nenhuma superficie criada.
PADROES_GEOMETRICOS_3245 = dict(PADROES_GEOMETRICOS_3216, **NOVOS_PADROES_3245)
SUBSTITUICOES = {
    'MEGASERPENTE': 'TRILHO_TRANCADO',       # 12 -> 12
    'MEGA_ANEL': 'ESCADA_SERRILHADA',       # 12 -> 12
    'CORREDOR_GIGANTE': 'RAMPA_PONTILHADA', # 14 -> 14
    'ONDA_DUPLA_GIGANTE': 'TRILHO_ALTERNADO',# 16 -> 16
}


def variar_formato(formato, metros, bioma):
    """Deterministico, sem RNG: conserva contagem e chance de encontro."""
    if formato in SUBSTITUICOES:
        ciclo = int(metros)//240 + sum(map(ord,str(bioma)))
        if ciclo % 3 == 0:
            return SUBSTITUICOES[formato]
    return formato


def verificar_geometrias():
    for nome, pontos in NOVOS_PADROES_3245.items():
        assert 8 <= len(pontos) <= 16, nome
        assert max(x for x,y in pontos)-min(x for x,y in pontos) <= 310
        assert max(y for x,y in pontos)-min(y for x,y in pontos) <= 140
        assert len(set(pontos)) == len(pontos)
        assert all((x-x2)**2+(y-y2)**2 >= 23**2
                   for i,(x,y) in enumerate(pontos) for x2,y2 in pontos[i+1:]),nome
    for velho,novo in SUBSTITUICOES.items():
        assert len(NOVOS_PADROES_3245[novo]) == (12 if velho in ('MEGASERPENTE','MEGA_ANEL') else 14 if velho=='CORREDOR_GIGANTE' else 16)

verificar_geometrias()
