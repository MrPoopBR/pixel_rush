# -*- coding: utf-8 -*-
"""Plano K v3.243: eventos raros I (Cidade, Neve, Deserto, Floresta).

Diretor independente. Não modifica o gerador de obstáculos, as velocidades,
as hitboxes antigas ou o RNG global. Eventos têm 90 ticks de aviso e são
cancelados caso surja perigo tradicional em distância de conflito. Novas
hitboxes pertencem SOMENTE ao evento; impacto é resolvido pelo jogador.
Todos os efeitos visuais ficam em sprites/cache de uma única criação.
"""
import hashlib
import random
import pygame

EVENTOS = {
    'cidade': ('ABALO URBANO - SALTE!', (237, 179, 94), 'fissura'),
    'neve': ('AVALANCHE - SALTE!', (162, 216, 251), 'avalanche'),
    'deserto': ('RAJADA DE AREIA - AGACHE!', (237, 190, 116), 'detritos'),
    'floresta': ('ARVORE CAINDO - SALTE!', (135, 207, 131), 'tronco'),
}


class DiretorEventosRaros:
    AVISO = 90
    VELOCIDADE = 4.6
    X_INICIAL = 450
    MAX_POR_PARTIDA = 2

    def __init__(self):
        self._sprites = {}
        self._avisos = {}
        self.reiniciar(None)

    def reiniciar(self, estado_rng):
        seed = 2430 if estado_rng is None else int.from_bytes(
            hashlib.sha256(repr(estado_rng).encode('ascii')).digest()[:8], 'big') ^ 2430
        self._rng = random.Random(seed)
        self.fase = 'inativo'
        self.bioma = None
        self.ticks = 0
        self.x = self.X_INICIAL
        self.aparicoes = 0
        self.biomas_usados = set()
        self.tentativa = 1100 + self._rng.randrange(500)
        self.impacto_pendente = False
        self.impactou = False
        self.superados = 0
        self.cancelados = 0

    @property
    def ativo(self):
        return self.fase != 'inativo'

    def _encerrar(self, metros, cancelado=False):
        if cancelado:
            self.cancelados += 1
        else:
            self.superados += 1
        self.fase = 'inativo'
        self.bioma = None
        self.ticks = 0
        self.x = self.X_INICIAL
        self.impacto_pendente = False
        self.impactou = False
        self.tentativa = max(self.tentativa, int(metros) + 700)

    def atualizar(self, metros, bioma, *, permitido, perigo_proximo=False):
        """Chamar uma vez por tick FIXO; nunca no loop gráfico.

        A aproximação NÃO avança se há risco de sobreposição: cancelamos
        o evento em vez de deslocar obstáculos existentes, e sua hitbox
        nunca fica ativa sem 90 ticks de alerta.
        """
        metros = max(0, int(metros))
        if self.ativo:
            if not permitido or bioma != self.bioma or perigo_proximo:
                self._encerrar(metros, cancelado=True)
                return
            self.ticks += 1
            if self.fase == 'aviso':
                if self.ticks >= self.AVISO:
                    self.fase = 'perigo'
                    self.ticks = 0
                    self.x = self.X_INICIAL
            elif self.fase == 'perigo':
                self.x = self.X_INICIAL - self.ticks * self.VELOCIDADE
                if self.x < -85:
                    self._encerrar(metros)
            return
        if (not permitido or perigo_proximo or bioma not in EVENTOS
                or self.aparicoes >= self.MAX_POR_PARTIDA
                or bioma in self.biomas_usados or metros < self.tentativa):
            return
        if self._rng.random() >= 0.18:
            self.tentativa = metros + 300 + self._rng.randrange(250)
            return
        self.bioma = bioma
        self.fase = 'aviso'
        self.ticks = 0
        self.aparicoes += 1
        self.biomas_usados.add(bioma)
        self.tentativa = metros + 950 + self._rng.randrange(300)
        self.impacto_pendente = False
        self.impactou = False

    def perigo_rect(self):
        if self.fase != 'perigo':
            return None
        x = round(self.x)
        if self.bioma == 'cidade':
            return pygame.Rect(x + 6, 713, 65, 17)
        if self.bioma == 'neve':
            return pygame.Rect(x + 9, 662, 57, 52)
        if self.bioma == 'deserto':
            return pygame.Rect(x + 13, 642, 49, 56)
        if self.bioma == 'floresta':
            return pygame.Rect(x + 8, 656, 60, 56)
        return None

    def detectar_colisao(self, jogador):
        """Sem alterar hitbox do jogador; trata buraco pelo contato no solo.
        Efeito de impacto ocorre no máximo uma vez a cada aparição.
        """
        if self.fase != 'perigo' or self.impactou or jogador.morrendo:
            return False
        area = self.perigo_rect()
        if area is None:
            return False
        if self.bioma == 'cidade':
            atingiu = bool(jogador.no_chao and not jogador.jetpack_fase
                            and area.left < jogador.rect.centerx < area.right)
        else:
            atingiu = jogador.obter_hitbox().colliderect(area)
        if atingiu:
            self.impactou = True
            self.impacto_pendente = True
        return atingiu

    def resolver_impacto(self, jogador, *, protegido=False, imortal=False):
        if not self.impacto_pendente:
            return 'sem_impacto'
        self.impacto_pendente = False
        if jogador.morrendo:
            return 'sem_impacto'
        if protegido or imortal:
            return 'protegido'
        if jogador.escudo_hits > 0:
            jogador.escudo_hits -= 1
            return 'escudo'
        jogador.iniciar_morte(por_buraco=self.bioma == 'cidade')
        return 'morte'

    def _sprite(self, bioma):
        """Uma superfície pre-renderizada por bioma; nunca desenhar geometria no frame."""
        if bioma in self._sprites:
            return self._sprites[bioma]
        s = pygame.Surface((80, 76), pygame.SRCALPHA)
        color = EVENTOS[bioma][1]
        dark = (23, 28, 43)
        if bioma == 'cidade':
            pygame.draw.polygon(s, (17, 24, 35), [(2, 63),(77, 63),(69, 75),(51, 67),(36, 75),(22, 66)])
            pygame.draw.lines(s, (239, 146, 71), False, [(4, 65),(26, 69),(36, 66),(51, 72),(74, 66)], 3)
            for x in range(8, 72, 12):
                pygame.draw.line(s, (116, 133, 145), (x, 62), (x+4, 58), 2)
        elif bioma == 'neve':
            pygame.draw.ellipse(s, (16, 33, 51, 90), (4, 65, 69, 9))
            pygame.draw.circle(s, dark, (40, 40), 33)
            pygame.draw.circle(s, (120, 170, 200), (40, 39), 30)
            pygame.draw.circle(s, (222, 245, 255), (36, 31), 26)
            for px,py in [(24, 17),(52, 45),(38, 54),(17, 38),(46, 20)]:
                pygame.draw.rect(s, (145, 192, 223), (px,py,9,5))
            pygame.draw.line(s, (255,255,255), (23, 21), (37, 15),3)
        elif bioma == 'deserto':
            pygame.draw.ellipse(s, (54, 40, 36, 90), (5, 67, 72, 7))
            for a,b,w,h in [(12,29,20,35),(35,20,28,42),(51,38,18,29)]:
                pygame.draw.polygon(s, dark, [(a,b+6),(a+w,b),(a+w-3,b+h),(a+2,b+h)])
                pygame.draw.polygon(s, color,[(a+3,b+5),(a+w-4,b+3),(a+w-6,b+h-5),(a+5,b+h-7)])
            pygame.draw.line(s, (255, 240, 173), (7, 26), (65, 14),2)
        else:  # Floresta: árvore inclinada com folha e raízes identificáveis.
            pygame.draw.ellipse(s, (8, 33, 21, 80), (7, 67, 67, 7))
            pygame.draw.polygon(s, (28, 36, 29), [(7, 48),(27, 44),(71, 29),(74, 43),(28, 59),(13, 69)])
            pygame.draw.polygon(s, (112, 76, 42), [(9, 48),(28, 46),(70, 31),(67, 38),(26, 54),(12, 59)])
            for px,py in [(44,29),(61,17),(73,24),(30,39)]:
                pygame.draw.circle(s, (28, 61, 35), (px,py), 13)
                pygame.draw.circle(s, (74, 143, 70), (px-2,py-3), 10)
                pygame.draw.rect(s, (162, 210, 105), (px-5,py-7,5,3))
        self._sprites[bioma] = s.convert_alpha()
        return self._sprites[bioma]

    def _aviso(self, bioma, leve):
        k = (bioma, bool(leve))
        if k in self._avisos:
            return self._avisos[k]
        text, cor, _ = EVENTOS[bioma]
        w = 186 if leve else 246
        s = pygame.Surface((w, 32), pygame.SRCALPHA)
        pygame.draw.rect(s, (15, 22, 35, 224), (0,0,w,32), border_radius=5)
        pygame.draw.rect(s, cor, (1,1,w-2,30), 2, border_radius=5)
        font = pygame.font.Font(None, 16 if leve else 19)
        img = font.render(text, True, (255, 247, 221))
        s.blit(img, (5, 6))
        self._avisos[k] = s
        return s

    def desenhar(self, destino, leve=False):
        if not self.ativo or self.bioma not in EVENTOS:
            return
        if self.fase == 'aviso':
            destino.blit(self._aviso(self.bioma, leve), (119 if leve else 94, 320))
            return
        sprite = self._sprite(self.bioma)
        destino.blit(sprite, (round(self.x), 654))
        # Não criar superfícies por quadro, nem obscurecer a região do jogador.
