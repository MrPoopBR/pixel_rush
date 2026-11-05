# -*- coding: utf-8 -*-
"""QA792: moeda e pool AST-identicos, constantes compartilhadas na inicializacao."""
import math
import random
import pygame
from pygame.sprite import Sprite
from src.pixelrush.entities.particles import Particula
CHAVE_TRANSPARENCIA_SPRITES = (255, 0, 255)
AMARELO_MOEDA = (255, 215, 0)
PRETO = (0, 0, 0)

class Moeda(Sprite):
    # Variantes leves para evitar repeticao visual sem custo por frame.
    _imagens_variantes = None

    @staticmethod
    def _criar_variantes():
        variantes = []
        for estilo in range(4):
            imagem = pygame.Surface((24, 24)).convert()
            imagem.fill(CHAVE_TRANSPARENCIA_SPRITES)
            cor_brilho = (255, 243, 161)
            cor_sombra = (209, 155, 22)
            pygame.draw.circle(imagem, cor_sombra, (12, 12), 11)
            pygame.draw.circle(imagem, AMARELO_MOEDA, (11, 11), 10)
            pygame.draw.circle(imagem, (255, 236, 115), (11, 11), 8)
            pygame.draw.circle(imagem, PRETO, (11, 11), 11, 2)
            pygame.draw.circle(imagem, cor_brilho, (8, 8), 3)
            pygame.draw.circle(imagem, (230, 180, 35), (11, 11), 4, 1)
            pygame.draw.rect(imagem, (255, 249, 205), (7, 5, 3, 2))
            pygame.draw.line(imagem, (255, 228, 90), (11, 8), (11, 14), 1)
            pygame.draw.rect(imagem, (217, 150, 27), (17, 15, 3, 2))
            if estilo == 1:
                pygame.draw.line(imagem, cor_brilho, (16, 2), (16, 7), 1)
                pygame.draw.line(imagem, cor_brilho, (13, 4), (19, 4), 1)
            elif estilo == 2:
                pygame.draw.circle(imagem, (255, 250, 223), (15, 6), 2)
                pygame.draw.circle(imagem, (255, 236, 115), (16, 16), 2)
            elif estilo == 3:
                pygame.draw.rect(imagem, cor_brilho, (15, 3, 4, 3))
                pygame.draw.line(imagem, cor_brilho, (17, 1), (17, 7), 1)
                pygame.draw.line(imagem, cor_brilho, (14, 4), (20, 4), 1)
            else:
                pygame.draw.rect(imagem, cor_brilho, (16, 4, 3, 3))
                pygame.draw.line(imagem, cor_brilho, (17, 1), (17, 6), 1)
                pygame.draw.line(imagem, cor_brilho, (14, 4), (20, 4), 1)
            imagem.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
            variantes.append(imagem)
        return variantes

    def __init__(self, x_pos=0, y_pos=0):
        super().__init__()
        self.pool_manager = None
        self._pool_livre = False
        if Moeda._imagens_variantes is None:
            Moeda._imagens_variantes = Moeda._criar_variantes()
        self.image = random.choice(Moeda._imagens_variantes)
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self._x_float = float(self.rect.x)
        self._y_float = float(self.rect.y)
        self.ativo = True

    def kill(self):
        super().kill()
        manager = self.pool_manager
        if manager is not None and not self._pool_livre:
            self.ativo = False
            self._pool_livre = True
            manager.moedas_disponiveis.append(self)

    def reset(self, x_pos, y_pos):
        if Moeda._imagens_variantes is not None:
            self.image = random.choice(Moeda._imagens_variantes)
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self._x_float = float(self.rect.x)
        self._y_float = float(self.rect.y)
        self.ativo = True

    def update(self, velocidade_jogo, jogador=None):
        if not self.ativo:
            return
        if jogador and jogador.tempo_ima > 0 and not jogador.morrendo:
            dx = jogador.rect.centerx - self.rect.centerx
            dy = jogador.rect.centery - self.rect.centery
            distancia_quadrada = dx * dx + dy * dy
            if 0 < distancia_quadrada < (220 * 220):
                distancia = math.sqrt(distancia_quadrada)
                self._x_float += (dx / distancia) * 12.0
                self._y_float += (dy / distancia) * 12.0
        self._x_float -= float(velocidade_jogo)
        self.rect.x = int(round(self._x_float))
        self.rect.y = int(round(self._y_float))
        if self.rect.right < -50:
            self.ativo = False
            self.kill()

class PoolManager:
    def __init__(self):
        self.particulas_pool = [Particula() for _ in range(250)]
        self.particulas_disponiveis = list(self.particulas_pool)
        for p in self.particulas_pool:
            p.pool_manager = self
            p.ativo = False
            p._pool_livre = True

        self.moedas_pool = [Moeda() for _ in range(120)]
        self.moedas_disponiveis = list(self.moedas_pool)
        for m in self.moedas_pool:
            m.pool_manager = self
            m.ativo = False
            m._pool_livre = True

    def obter_particula(self, x, y, cor, vx=None, vy=None, vida=25, tamanho=5):
        if self.particulas_disponiveis:
            p = self.particulas_disponiveis.pop()
            p._pool_livre = False
            p.reset(x, y, cor, vx, vy, vida, tamanho)
        else:
            p = Particula(x, y, cor, vx, vy, vida, tamanho)
            p.pool_manager = self
            p._pool_livre = False
            self.particulas_pool.append(p)
        return p

    def obter_moeda(self, x_pos, y_pos):
        if self.moedas_disponiveis:
            m = self.moedas_disponiveis.pop()
            m._pool_livre = False
            m.reset(x_pos, y_pos)
        else:
            m = Moeda(x_pos, y_pos)
            m.pool_manager = self
            m._pool_livre = False
            self.moedas_pool.append(m)
        return m
