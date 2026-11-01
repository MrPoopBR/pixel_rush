# -*- coding: utf-8 -*-
"""Pixel Rush v3.239.0 — diretor de APARIÇÕES de perseguidores.

A etapa 9 prepara apenas a ocorrência rara, a identidade por bioma e os
estados de aproximação/saída. Sem colisão/captura, que pertencem à v3.242.
Não gera obstáculos e nunca altera o RNG global, física ou spawn existente.
Os ícones temporários são substituíveis pela arte futura v3.240.
"""
import hashlib
import random
import pygame

# Ícones provisórios distintos; sprites premium pertencem à etapa 10.
PERFIS = {
    'cidade': ('Vigia urbano', (84, 159, 203), 'antena'),
    'neve': ('Caçador polar', (204, 235, 247), 'orelhas'),
    'deserto': ('Predador das dunas', (219, 149, 70), 'cauda'),
    'floresta': ('Guardião selvagem', (89, 163, 105), 'chifres'),
    'vulcao': ('Sentinela ígnea', (244, 100, 61), 'chamas'),
    'cidade_futurista': ('Sentinela neon', (64, 231, 229), 'antena'),
    'ilhas_celestes': ('Caçador celestial', (166, 161, 249), 'asas'),
}


class DiretorPerseguidores:
    """Orquestra perseguição CENOGRÁFICA sem criar hitbox/obstáculo.

    Evento planejado para não colidir com condições especiais. Não tem
    consequência letal até a etapa 12, quando escape justo será desenvolvido.
    """
    AVISO = 56
    APROXIMACAO = 178
    RECUO = 62
    MAX_POR_PARTIDA = 2

    def __init__(self):
        self._imagens = {}
        self.reiniciar(None)

    def reiniciar(self, estado_rng):
        # Extrai uma semente de um SNAPSHOT do RNG do jogo, sem consumi-lo.
        # Com corrida reproduzível, a sequência de aparições também se repete.
        if estado_rng is None:
            seed = 2390
        else:
            seed = int.from_bytes(hashlib.sha256(repr(estado_rng).encode('ascii')).digest()[:8], 'big')
        self._rng = random.Random(seed)
        self.fase = 'inativo'
        self.ticks = 0
        self.bioma = None
        self.aparicoes = 0
        self.biomas_usados = set()
        self.proxima_tentativa = 850 + self._rng.randrange(0, 350)
        self.proximidade = 0.0

    @property
    def ativo(self):
        return self.fase != 'inativo'

    def atualizar(self, metros, bioma, *, permitido, jogador_x=40, perigos_proximos=False):
        """Invocado apenas pelo tick fixo, nunca pelo render."""
        metros = max(0, int(metros))
        if self.ativo:
            # Um evento especial ou troca de bioma cancela imediatamente a cena.
            if not permitido or bioma != self.bioma:
                self._encerrar(metros)
                return
            self.ticks += 1
            if self.fase == 'aviso' and self.ticks >= self.AVISO:
                self.fase = 'aproximacao'
                self.ticks = 0
            elif self.fase == 'aproximacao':
                # Aumenta a pressão visual, mas respeita o limite à esquerda da hitbox.
                self.proximidade = min(1.0, self.proximidade + 1.0 / 110.0)
                if self.ticks >= self.APROXIMACAO:
                    self.fase = 'recuo'
                    self.ticks = 0
            elif self.fase == 'recuo':
                self.proximidade = max(0.0, self.proximidade - 1.0 / self.RECUO)
                if self.ticks >= self.RECUO:
                    self._encerrar(metros)
            return
        if (not permitido or perigos_proximos or metros < self.proxima_tentativa
                or bioma not in PERFIS or self.aparicoes >= self.MAX_POR_PARTIDA
                or bioma in self.biomas_usados):
            return
        # Só 24% das janelas qualificadas geram a aparição.
        if self._rng.random() >= 0.24:
            self.proxima_tentativa = metros + 320 + self._rng.randrange(180)
            return
        self.fase = 'aviso'
        self.bioma = bioma
        self.ticks = 0
        self.proximidade = 0.0
        self.aparicoes += 1
        self.biomas_usados.add(bioma)
        self.proxima_tentativa = metros + 850 + self._rng.randrange(350)

    def _encerrar(self, metros):
        self.fase = 'inativo'
        self.bioma = None
        self.proximidade = 0.0
        self.ticks = 0
        self.proxima_tentativa = max(self.proxima_tentativa, metros + 800)

    def _icone(self, bioma):
        """Gera uma superfície por bioma, somente no primeiro uso."""
        if bioma in self._imagens:
            return self._imagens[bioma]
        _, cor, detalhe = PERFIS[bioma]
        s = pygame.Surface((42, 50), pygame.SRCALPHA)
        escuro = (22, 26, 37)
        pygame.draw.ellipse(s, (9, 18, 30, 90), (3, 43, 38, 6))
        pygame.draw.rect(s, escuro, (6, 22, 30, 22), border_radius=5)
        pygame.draw.rect(s, cor, (9, 20, 24, 21), border_radius=5)
        pygame.draw.ellipse(s, escuro, (6, 9, 30, 25))
        pygame.draw.ellipse(s, cor, (9, 11, 24, 20))
        for ex in (15, 26):
            pygame.draw.rect(s, (255, 236, 180), (ex, 21, 4, 4))
        pygame.draw.rect(s, escuro, (10, 40, 8, 7))
        pygame.draw.rect(s, escuro, (25, 40, 8, 7))
        if detalhe == 'antena':
            pygame.draw.line(s, cor, (21, 10), (21, 1), 3)
            pygame.draw.circle(s, (255, 219, 95), (21, 2), 3)
        elif detalhe == 'orelhas':
            pygame.draw.polygon(s, cor, ((7, 17), (6, 2), (18, 13)))
            pygame.draw.polygon(s, cor, ((25, 13), (37, 2), (36, 17)))
        elif detalhe == 'cauda':
            pygame.draw.lines(s, cor, False, ((31, 31), (40, 26), (38, 11)), 3)
        elif detalhe == 'chifres':
            pygame.draw.polygon(s, cor, ((10, 13), (2, 1), (18, 11)))
            pygame.draw.polygon(s, cor, ((25, 11), (40, 1), (33, 13)))
        elif detalhe == 'chamas':
            pygame.draw.polygon(s, (255, 195, 64), ((15, 14), (18, 1), (22, 11), (27, 0), (29, 15)))
        elif detalhe == 'asas':
            pygame.draw.polygon(s, cor, ((12, 27), (0, 10), (4, 37)))
            pygame.draw.polygon(s, cor, ((30, 27), (42, 10), (38, 37)))
        self._imagens[bioma] = s.convert_alpha()
        return self._imagens[bioma]

    def desenhar(self, destino, jogador_x=40, leve=False):
        if not self.ativo or self.bioma not in PERFIS:
            return
        # Não oclui o jogador nem os obstáculos. Ícone atrás do jogador,
        # dentro dos ~36 pixels da borda esquerda da tela virtual.
        if self.fase != 'aviso':
            sprite = self._icone(self.bioma)
            ponto = max(-42, min(int(jogador_x) - 45,
                                    int(-42 + 36 * self.proximidade)))
            destino.blit(sprite, (ponto, 680))
        # Aviso mínimo (sem texto novo na HUD e sem novas fontes).
        if not leve and self.fase == 'aviso':
            pygame.draw.rect(destino, (29, 35, 49), (7, 260, 106, 22), border_radius=4)
            pygame.draw.rect(destino, PERFIS[self.bioma][1], (9, 262, 102, 18), 2)
            pygame.draw.polygon(destino, (255, 213, 110), ((19, 266), (14, 275), (24, 275)))
            pygame.draw.rect(destino, (255, 213, 110), (18, 270, 2, 3))
