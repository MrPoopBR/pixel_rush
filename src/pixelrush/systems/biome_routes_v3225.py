# -*- coding: utf-8 -*-
"""Pixel Rush v3.225.0: percurso por bioma SEM gerador de perigos novo.

Decorador de uma chamada do diretor existente por evento. O comando, a chance
real dos moveis e os reflexos ficam INTACTOS. Somente a disposicao dos premios
varia: trechos abertos com tres moedas e trilhas pos-perigo em parte dos
movimentos/reflexos. O sprite original, o pool e a colisao nao sao alterados.
"""

from pixelrush_moveis_v3222 import PERFIS

BIOMAS = tuple(PERFIS)
# Ordem ciclica de temas dos sete biomas, sem consultar nem consumir random.
TEMAS = {
    'cidade': ('avenida', 'viaduto', 'bairro'),
    'neve': ('geleira', 'travesia', 'nevasca'),
    'deserto': ('dunas', 'caravana', 'oasis'),
    'floresta': ('raizes', 'copas', 'clareira'),
    'vulcao': ('caldeira', 'cinzas', 'basalto'),
    'cidade_futurista': ('aerovia', 'neon', 'corredor'),
    'ilhas_celestes': ('cristais', 'pontes', 'nuvens'),
}
ABERTOS = ('TRIO_HORIZONTAL', 'DIAGONAL_SUBINDO', 'SMILEY',
           'TRIO_VERTICAL', 'DIAGONAL_DESCENDO')
VALIDOS = frozenset(('SALTO','ESCOLHA','PASSAGEM','DESCANSO','TRILHA',
                    'REFLEXO_CURTO','REFLEXO_LONGO','REFLEXO_BAIXO'))

class DiretorRotasBioma:
    """Envelope transparente do diretor oficial: nao gera eventos extras.

    `rota_atual` descreve APENAS a recompensa do encontro ja autorizado.
    Reinicio e troca de bioma cancelam o trecho anterior e mantem replay igual.
    """
    INICIO = 1600
    SETOR = 560
    def __init__(self, diretor):
        self.diretor = diretor
        self.reiniciar(contar_base=False)

    def reiniciar(self, contar_base=True):
        if contar_base:
            self.diretor.reiniciar()
        self.bioma = None
        self.encontros = 0
        self.rota_atual = None
        self.trechos_ativos = 0
        self.temas_vistos = set()

    def proxima(self, metros, cenario='cidade'):
        comando = self.diretor.proxima(metros, cenario)
        if cenario != self.bioma:
            self.bioma = cenario
            self.encontros = 0
        self.rota_atual = None
        if cenario not in TEMAS or metros < self.INICIO or comando not in VALIDOS:
            return comando
        indice = (int(metros) // self.SETOR + self.encontros // 5 +
                  BIOMAS.index(cenario)) % 3
        self.encontros += 1
        tema = TEMAS[cenario][indice]
        # Metadados imutaveis, nao interferem com sequencias de reflexo.
        self.rota_atual = (tema, indice, comando)
        self.trechos_ativos += 1
        self.temas_vistos.add((cenario, tema))
        return comando


def formato_aberto(rota, descanso=False):
    """Sempre exatamente 3 moedas; nao muda a economia dos trechos abertos."""
    if rota is None:
        return 'TRIO_HORIZONTAL' if descanso else 'DIAGONAL_SUBINDO'
    _, fase, _ = rota
    return ABERTOS[(fase * 2 + int(not descanso)) % len(ABERTOS)]


def posicoes_pos_perigo(rota, rect, altura_virtual):
    """Moedas APOS o perigo, nao sobre/sob a hitbox dele.

    O perigo movel aproxima mais rapido que moedas comuns, aumentando o
    afastamento da trilha a cada tick. Evita inducao a colisao por moeda.
    Metade dos trechos fica sem premio extra para limitar pool/CPU.
    """
    if rota is None:
        return ()
    _, fase, comando = rota
    if fase == 0 or comando not in ('SALTO','PASSAGEM','ESCOLHA',
                                   'REFLEXO_CURTO','REFLEXO_LONGO','REFLEXO_BAIXO'):
        return ()
    # Ate 3 sprites por evento; distancia >120 px alem da borda do perigo.
    x0 = int(rect.right) + 134
    y = int(altura_virtual) - 128
    if fase == 1:
        return ((x0, y), (x0+34, y-10), (x0+68, y-20))
    return ((x0, y-20), (x0+34, y-10), (x0+68, y))


def premiar_pos_perigo(rota, obstaculo, altura_virtual,
                       todos_sprites, moedas, pool_manager):
    """Usa o pool original; sem novos timers, RNG ou sprites criados a cada tick."""
    if pool_manager is None:
        return 0
    pontos = posicoes_pos_perigo(rota, obstaculo.rect, altura_virtual)
    for x, y in pontos:
        sprite = pool_manager.obter_moeda(x, y)
        todos_sprites.add(sprite)
        moedas.add(sprite)
    return len(pontos)
