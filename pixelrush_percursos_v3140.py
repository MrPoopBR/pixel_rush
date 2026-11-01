"""v3.140 — floresta com mais respiro visual entre sequências.

Preserva o comportamento dos demais biomas e só deixa a Floresta mais legível,
evita encavalamento de leitura entre situações seguidas.
"""
from pixelrush_percursos_v3133 import DiretorSequencias as Previous


class DiretorSequencias(Previous):
    _CICLOS = dict(Previous._CICLOS)
    _CICLOS['floresta'] = (
        'SALTO','DESCANSO','TRILHA','DESCANSO','ESCOLHA',
        'DESCANSO','PASSAGEM','DESCANSO','TRILHA','DESCANSO'
    )

    def __init__(self):
        super().__init__()
        self._ultimo_tipo_floresta = None

    def proxima(self, metros, cenario='cidade'):
        tipo = super().proxima(metros, cenario)
        if cenario != 'floresta' or tipo is None:
            return tipo
        # Garante que eventos de ação tenham sempre um respiro antes do próximo.
        if self._ultimo_tipo_floresta in ('SALTO','ESCOLHA','PASSAGEM') and tipo != 'DESCANSO':
            tipo = 'DESCANSO'
        self._ultimo_tipo_floresta = tipo
        return tipo
