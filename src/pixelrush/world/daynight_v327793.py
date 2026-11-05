# -*- coding: utf-8 -*-
"""Dia e noite cronológicos: ciclo completo em três minutos de simulação."""
import math
CICLO_QUADROS = 180 * 60
PALETA = (
    (0.00, (235, 146, 111)),
    (0.10, (172, 205, 235)),
    (0.24, (111, 188, 235)),
    (0.39, (118, 191, 239)),
    (0.47, (255, 178, 116)),
    (0.54, (130, 107, 164)),
    (0.63, (43, 61, 111)),
    (0.77, (20, 34, 75)),
    (0.88, (32, 43, 81)),
    (0.96, (127, 112, 153)),
    (1.00, (235, 146, 111)),
)
def _suave(a, b, v):
    if v <= a: return 0.
    if v >= b: return 1.
    u = (v-a)/(b-a)
    return u*u*(3-2*u)
def calcular_ciclo_ceu(metros=0, ticks=None):
    valor = max(0, int(ticks if ticks is not None else metros))
    fase = (valor % CICLO_QUADROS) / float(CICLO_QUADROS)
    cor = PALETA[-1][1]
    for (a, ca), (b, cb) in zip(PALETA, PALETA[1:]):
        if a <= fase <= b:
            u = _suave(a, b, fase)
            cor = tuple(int(ca[i] + (cb[i]-ca[i])*u) for i in range(3))
            break
    noite = _suave(.52,.64,fase) * (1.-_suave(.88,.99,fase))
    return fase, cor, noite, noite >= .5
def posicao_astro(fase, nome, largura=450):
    if nome == "sol": a,b,altura = .0,.52,185
    elif nome == "lua": a,b,altura = .52,1.0,154
    else: raise ValueError(nome)
    if not a <= fase <= b: return None
    u = (fase-a)/(b-a)
    return (-32 + int((largura+64)*u), 322-int(math.sin(math.pi*u)*altura))
