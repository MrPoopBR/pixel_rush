"""v3.133 — ciclos intencionais atualizados e sem mundo submerso."""
from pixelrush_percursos_v3132 import DiretorSequencias as Previous


class DiretorSequencias(Previous):
    _CICLOS = {
        'floresta': ('SALTO','DESCANSO','TRILHA','ESCOLHA','DESCANSO','PASSAGEM','DESCANSO','TRILHA'),
        'vulcao': ('SALTO','DESCANSO','ESCOLHA','TRILHA','DESCANSO','PASSAGEM','DESCANSO'),
        'neve': ('SALTO','TRILHA','DESCANSO','PASSAGEM','DESCANSO','ESCOLHA'),
        'cidade_futurista': ('SALTO','DESCANSO','PASSAGEM','TRILHA','DESCANSO','ESCOLHA'),
        'ilhas_celestes': ('TRILHA','SALTO','DESCANSO','ESCOLHA','DESCANSO','PASSAGEM','DESCANSO'),
    }

    def proxima(self, metros, cenario='cidade'):
        return super().proxima(metros, cenario if cenario != 'reino_submerso' else 'ilhas_celestes')
