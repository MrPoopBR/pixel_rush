"""v3.191.0 — variedade progressiva sem novo gerador, perigos ou timers.

Aproveita o DiretorSequencias e AuditorJustica originais. A auditoria e o
espaçamento são executados ANTES de qualquer variação. Só remapeia os três
comandos de ação já existentes; não troca pausas, trilhas ou eventos clássicos.
"""
from pixelrush_cinema_v3172 import AuditorJustica as _AuditorAnterior


class AuditorVariedade(_AuditorAnterior):
    """Varia rotas de perigo mantendo ritmo e proteções do auditor existente."""
    ROTACOES = (
        {'SALTO': 'ESCOLHA', 'ESCOLHA': 'PASSAGEM', 'PASSAGEM': 'SALTO'},
        {'SALTO': 'PASSAGEM', 'ESCOLHA': 'SALTO', 'PASSAGEM': 'ESCOLHA'},
        {},
    )
    BIOMAS = frozenset(('cidade', 'neve', 'deserto', 'floresta', 'vulcao',
                        'cidade_futurista', 'ilhas_celestes'))

    def __init__(self, diretor):
        super().__init__(diretor)
        self._ultimo_real = None
        self.variacoes = 0
        self.protecoes = 0

    def reiniciar(self):
        super().reiniciar()
        self._ultimo_real = None
        self.variacoes = 0
        self.protecoes = 0

    def proxima(self, metros, cenario='cidade'):
        base = super().proxima(metros, cenario)
        escolhido = base
        if base in self.ACOES and cenario in self.BIOMAS and metros >= 900:
            if self._ultimo_real not in self.ACOES:
                etapa = (int(metros) - 900) // 650
                escolhido = self.ROTACOES[etapa % len(self.ROTACOES)].get(base, base)
            # Caso uma rotação anterior cause conflito com a próxima ação,
            # manter a mesma densidade de riscos escolhendo um comando seguro.
            if (self._ultimo_real, escolhido) in self.CHOQUES:
                for alternativa in (base, 'SALTO', 'ESCOLHA', 'PASSAGEM'):
                    if (self._ultimo_real, alternativa) not in self.CHOQUES:
                        escolhido = alternativa
                        self.protecoes += 1
                        break
        if escolhido != base:
            self.variacoes += 1
        self._ultimo_real = escolhido
        return escolhido
