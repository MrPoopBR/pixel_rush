"""v3.132 — sequências legíveis por bioma; mantém diretor e geração v3.131.

Nenhuma colisão ou objeto novo: só ordena tipos já existentes e acrescenta
uma rota de moedas sem perigo (TRILHA). Sempre no máximo um perigo por evento.
"""
from pixelrush_percursos_v3131 import DiretorSequencias as Anterior


class DiretorSequencias(Anterior):
    _CICLOS = {
        'floresta': ('SALTO','DESCANSO','TRILHA','ESCOLHA','DESCANSO','PASSAGEM','DESCANSO'),
        'vulcao': ('SALTO','DESCANSO','ESCOLHA','DESCANSO','PASSAGEM','TRILHA','DESCANSO'),
        'neve': ('SALTO','TRILHA','DESCANSO','PASSAGEM','DESCANSO','ESCOLHA'),
        'cidade_futurista': ('SALTO','DESCANSO','PASSAGEM','DESCANSO','ESCOLHA','TRILHA'),
        'ilhas_celestes': ('TRILHA','SALTO','DESCANSO','ESCOLHA','DESCANSO','PASSAGEM'),
        'reino_submerso': ('SALTO','DESCANSO','TRILHA','PASSAGEM','DESCANSO'),
    }

    def proxima(self,metros,cenario='cidade'):
        # A Cidade e o Deserto mantêm rigorosamente o ciclo aprovado na v3.131.
        if cenario not in self._CICLOS:
            return super().proxima(metros)
        if metros<120:
            return None
        if metros<350:
            ciclo=('SALTO','DESCANSO')
        else:
            ciclo=self._CICLOS[cenario]
        # O terceiro encontro usa o gerador clássico. Avançar também o
        # índice do ciclo nessa lacuna apagava sempre as mesmas ações
        # em ciclos de 3/6 elementos (ex.: TRILHA nunca aparecia).
        posicao_util=self.indice - self.indice//3
        tipo=ciclo[posicao_util%len(ciclo)]
        self.indice+=1
        return None if self.indice%3==0 else tipo
