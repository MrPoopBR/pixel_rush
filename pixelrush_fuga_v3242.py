# -*- coding: utf-8 -*-
"""Pixel Rush v3.242.0 — fuga por habilidade dos perseguidores.

Aproveita integralmente o diretor e os atlases v3.241.0. Uma perseguição
continua rara e tem dois resultados: 3 manobras nos intervalos anunciados
permitem escapar; sem isso a ameaça alcança o jogador. Nenhuma alteração na
física, nas hitboxes nem no RNG global. O relógio da ameaça é pausado quando
há perigos próximos, de forma que o evento não exija gesto incompatível com
um obstáculo já presente. HUD global inalterada: aviso local pré-renderizado.
"""
import pygame
from pixelrush_perseguidores_v3241 import DiretorPerseguidores as _Base


class DiretorPerseguidores(_Base):
    # Distância RELATIVA, não move o jogador e não altera a velocidade real.
    DISTANCIA_INICIAL = 104.0
    VANTAGEM_PERSEGUIDOR = 0.90   # unidades de aproximação por tick.
    BONUS_MANOBRA = 30.0
    # Um dos comandos padrão (pulo OU agachar) em cada janela.
    JANELAS = ((24, 60), (65, 108), (112, 162))
    RECUO_VITORIA = 62

    def reiniciar(self, estado_rng):
        super().reiniciar(estado_rng)
        self._limpar_fuga()

    def _limpar_fuga(self):
        self.separacao = self.DISTANCIA_INICIAL
        self.manobras = 0
        self._no_chao_anterior = True
        self._agachado_anterior = False
        self._perigo_na_pista = False
        self._captura_pendente = False
        self.escapadas = getattr(self, 'escapadas', 0) if hasattr(self, 'escapadas') else 0
        self._avisos_fuga = getattr(self, '_avisos_fuga', {})
        self._sucesso_fuga = False

    def _encerrar(self, metros):
        super()._encerrar(metros)
        self._limpar_fuga()
        self._captura_pendente = False

    def atualizar(self, metros, bioma, *, permitido, jogador_x=40,
                  perigos_proximos=False, velocidade_jogador=6.0):
        inicio = self.fase
        # Cancela eventos especiais exatamente como na versão anterior.
        if self.ativo and (not permitido or bioma != self.bioma):
            super().atualizar(metros, bioma, permitido=permitido,
                              jogador_x=jogador_x, perigos_proximos=perigos_proximos)
            return
        # Evita exigências de manobra enquanto o jogador já precisa reagir a
        # obstáculos tradicionais. Não altera o spawn; apenas o relógio da fuga.
        self._perigo_na_pista = bool(perigos_proximos) if inicio == 'aproximacao' else False
        if inicio == 'aproximacao' and self._perigo_na_pista:
            return
        super().atualizar(metros, bioma, permitido=permitido,
                          jogador_x=jogador_x, perigos_proximos=perigos_proximos)
        if inicio == 'inativo' and self.fase == 'aviso':
            self._limpar_fuga()
        if inicio == 'aviso' and self.fase == 'aproximacao':
            self.separacao = self.DISTANCIA_INICIAL
            self.manobras = 0
        elif inicio == 'aproximacao':
            # O perseguidor corre mais rápido que o jogador em qualquer
            # velocidade. Guardamos a grandeza para diagnóstico de QA.
            self.velocidade_perseguidor = float(velocidade_jogador) + self.VANTAGEM_PERSEGUIDOR
            self.separacao -= self.velocidade_perseguidor - float(velocidade_jogador)
            self.proximidade = max(0.0, min(1.0, 1.0 - self.separacao / self.DISTANCIA_INICIAL))
            if self.manobras >= len(self.JANELAS) and self.ticks >= 156:
                self._sucesso_fuga = True
                self.escapadas += 1
                self.fase = 'recuo'
                self.ticks = 0
            elif self.separacao <= 0.0 or self.fase == 'recuo':
                self._captura_pendente = True
                self.fase = 'recuo'
                self.ticks = 0

    def registrar_manuobra(self, *, no_chao, agachado, subindo):
        """Somente estados EXISTENTES depois do update da física do jogador."""
        salto = self._no_chao_anterior and not no_chao and bool(subindo)
        abaixar = not self._agachado_anterior and bool(agachado) and bool(no_chao)
        self._no_chao_anterior = bool(no_chao)
        self._agachado_anterior = bool(agachado)
        if self.fase != 'aproximacao' or self._perigo_na_pista:
            return False
        if self.manobras >= len(self.JANELAS):
            return False
        inicio, fim = self.JANELAS[self.manobras]
        if not (inicio <= self.ticks <= fim and (salto or abaixar)):
            return False
        self.manobras += 1
        self.separacao = min(self.DISTANCIA_INICIAL + 16, self.separacao + self.BONUS_MANOBRA)
        return True

    def consumir_captura(self):
        """Evento de dano único. O loop aplica as proteções JÁ existentes."""
        if not self._captura_pendente:
            return False
        self._captura_pendente = False
        return True

    def resolver_captura(self, jogador, protegido=False, imortal=False):
        """Segue a regra atual: invulnerabilidade > escudo > morte.

        Um resultado pendente é sempre consumido uma única vez; o perseguidor
        não tem hitbox extra e nunca altera a física da vítima.
        """
        if not self.consumir_captura() or jogador.morrendo:
            return 'sem_captura'
        if protegido or imortal:
            return 'protegido'
        if jogador.escudo_hits > 0:
            jogador.escudo_hits -= 1
            return 'escudo'
        jogador.iniciar_morte()
        return 'morte'

    def _aviso_de_fuga(self, leve):
        if self.fase != 'aproximacao':
            return None
        passo = min(self.manobras, len(self.JANELAS))
        janela = (passo < len(self.JANELAS) and
                  self.JANELAS[passo][0] <= self.ticks <= self.JANELAS[passo][1])
        chave = (passo, bool(janela), bool(leve), self._perigo_na_pista)
        if chave in self._avisos_fuga:
            return self._avisos_fuga[chave]
        largura = 154 if leve else 176
        s = pygame.Surface((largura, 35), pygame.SRCALPHA)
        pygame.draw.rect(s, (13, 20, 33, 205), (0, 0, largura, 35), border_radius=5)
        cor = (255, 208, 97) if janela else (112, 165, 196)
        pygame.draw.rect(s, cor, (1, 1, largura-2, 33), 1, border_radius=5)
        fonte = pygame.font.Font(None, 19 if leve else 20)
        if self._perigo_na_pista:
            texto = 'PERIGO: FUGA PAUSADA'
        elif janela:
            texto = 'PULO OU AGACHAR!'
        elif passo == 3:
            texto = 'MANTENHA A FUGA!'
        else:
            texto = 'PREPARE A MANOBRA'
        img = fonte.render(texto, True, (248, 242, 214))
        s.blit(img, (6, 3))
        for i in range(3):
            pygame.draw.rect(s, (108, 229, 167) if i < passo else (72, 87, 107),
                             (8 + i*27, 24, 20, 5), border_radius=2)
        self._avisos_fuga[chave] = s
        return s

    def desenhar(self, destino, jogador_x=40, leve=False):
        super().desenhar(destino, jogador_x, leve)
        aviso = self._aviso_de_fuga(leve)
        if aviso is not None:
            destino.blit(aviso, (8, 293))
