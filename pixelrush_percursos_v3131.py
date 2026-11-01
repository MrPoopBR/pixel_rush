"""Direção de encontros da v3.131: sem mexer em velocidade, física ou hitboxes.

Um encontro usa no máximo um perigo. O espaçamento existente controla o próximo.
A sequência nunca agenda eventos futuros nem cria objetos fora do pool original.
"""

class DiretorSequencias:
    CICLO = ('SALTO', 'DESCANSO', 'ESCOLHA', 'PASSAGEM', 'DESCANSO')

    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        self.indice = 0

    def proxima(self, metros):
        if metros < 120:
            return None
        if metros < 350:
            tipo = ('SALTO', 'DESCANSO')[self.indice % 2]
        else:
            tipo = self.CICLO[self.indice % len(self.CICLO)]
        self.indice += 1
        # Um terço dos encontros continua usando os geradores originais,
        # inclusive sua chance de power-ups e perigos próprios de cada bioma.
        return None if self.indice % 3 == 0 else tipo
