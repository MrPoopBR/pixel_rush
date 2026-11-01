# -*- coding: utf-8 -*-
"""Plano H v3.206 — frases autorais combináveis sobre o diretor existente.

Não agenda spawn, não cria obstáculos e não chama RNG: traduz somente os cinco
comandos já aceitos por gerar_padrao. Cada chamada do diretor original continua
ocorrendo exatamente uma vez (inclusive as lacunas None do gerador clássico).
Uma ação continua sendo ação, e um encontro sem perigo continua sem perigo.
O AuditorVariedade(AuditorJustica) continua sendo a camada interna de segurança.
"""

CHOQUES = frozenset((('PASSAGEM', 'SALTO'), ('SALTO', 'PASSAGEM'),
                    ('ESCOLHA', 'PASSAGEM'), ('PASSAGEM', 'ESCOLHA')))

ACOES = frozenset(('SALTO', 'ESCOLHA', 'PASSAGEM'))
RESPIROS = frozenset(('DESCANSO', 'TRILHA'))

# Motivos: dois subciclos INDEPENDENTES: rota do perigo e recompensa sem perigo.
# Ao combinar os dois, muda a frase musical da corrida sem aumentar perigos ou
# tocar nos intervalos, na geometria das colisões ou no gerador de moedas.
MOTIVOS = {
    'convite': (('SALTO', 'ESCOLHA', 'PASSAGEM'), ('DESCANSO', 'TRILHA', 'DESCANSO')),
    'travessia': (('PASSAGEM', 'SALTO', 'ESCOLHA'), ('TRILHA', 'DESCANSO', 'TRILHA')),
    'ascensao': (('ESCOLHA', 'SALTO', 'PASSAGEM'), ('TRILHA', 'DESCANSO', 'DESCANSO')),
    'pulso': (('SALTO', 'PASSAGEM', 'ESCOLHA'), ('DESCANSO', 'TRILHA', 'TRILHA')),
    'retorno': (('ESCOLHA', 'PASSAGEM', 'SALTO'), ('DESCANSO', 'DESCANSO', 'TRILHA')),
}

# Cada bioma tem uma assinatura de três motivos combináveis. Nenhum item aqui
# define frequência, velocidade ou quantidade de perigos — só sua apresentação.
FRASES = {
    'cidade': ('convite', 'travessia', 'retorno'),
    'neve': ('ascensao', 'convite', 'retorno'),
    'deserto': ('travessia', 'pulso', 'convite'),
    'floresta': ('convite', 'retorno', 'ascensao'),
    'vulcao': ('pulso', 'travessia', 'retorno'),
    'cidade_futurista': ('travessia', 'ascensao', 'pulso'),
    'ilhas_celestes': ('ascensao', 'retorno', 'convite'),
}


class DiretorAutorais:
    """Decora DiretorSequencias sem substituí-lo nem alterar sua cadência.

    Somente depois de 900 m, combinando motivos de sete encontros úteis.
    Os encontros None continuam intocados e NÃO avançam o motivo; o diretor
    interno segue recebendo todos os encontros para preservar seu ritmo.
    """
    JANELA = 7
    LIMIAR = 900

    def __init__(self, diretor):
        self.diretor = diretor
        self.reiniciar(contar_base=False)

    def reiniciar(self, contar_base=True):
        if contar_base:
            self.diretor.reiniciar()
        self.bioma_atual = None
        self.ultimo_emitido = None
        self.encontros = 0
        self.acoes = 0
        self.respiros = 0
        self.transformacoes = 0
        self.frases_usadas = set()

    def proxima(self, metros, cenario='cidade'):
        # Receber o comando ANTES de qualquer decisão garante os contadores,
        # descanso e lacunas originais, inclusive para biomas desconhecidos.
        original = self.diretor.proxima(metros, cenario)
        if original is None or metros < self.LIMIAR or cenario not in FRASES:
            self.ultimo_emitido = original
            return original
        if original not in ACOES and original not in RESPIROS:
            self.ultimo_emitido = original
            return original
        if cenario != self.bioma_atual:
            self.bioma_atual = cenario
            self.encontros = self.acoes = self.respiros = 0

        assinatura = FRASES[cenario]
        # A alternância lenta por setor varia as combinações em corridas longas,
        # sem tocar o RNG global (essencial para gravação/reprodução v3.205).
        setor = max(0, int(metros) // 1300)
        posicao = ((self.encontros // self.JANELA) + setor) % len(assinatura)
        nome = assinatura[posicao]
        acoes, respiros = MOTIVOS[nome]
        if original in ACOES:
            resultado = acoes[self.acoes % len(acoes)]
            self.acoes += 1
        else:
            resultado = respiros[self.respiros % len(respiros)]
            self.respiros += 1
        # A troca de tipo não pode criar um choque entre dois perigos.
        # A conversão de uma ação para DESCANSO é a única redução permitida.
        if (self.ultimo_emitido, resultado) in CHOQUES:
            resultado = 'DESCANSO'
        self.ultimo_emitido = resultado
        self.encontros += 1
        self.frases_usadas.add((cenario, nome))
        self.transformacoes += resultado != original
        return resultado
