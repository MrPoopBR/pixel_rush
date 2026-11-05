# -*- coding: utf-8 -*-
"""Sprite de particula do motor QA790; codigo/metodos preservados literalmente.
O RNG continua no modulo random global, sem wrappers por quadro.
"""
import random
import pygame
from pygame.sprite import Sprite

class Particula(Sprite):
    """Particula reaproveitavel; alpha global evita preencher RGBA a cada frame."""
    def __init__(self, x=0, y=0, cor=(255, 255, 255), vx=None, vy=None, vida=25, tamanho=5):
        super().__init__()
        self.pool_manager = None
        self._pool_livre = False
        self._imagens_por_tamanho = {}
        self.image = None
        self.reset(x, y, cor, vx, vy, vida, tamanho)

    def kill(self):
        super().kill()
        manager = self.pool_manager
        if manager is not None and not self._pool_livre:
            self.ativo = False
            self._pool_livre = True
            manager.particulas_disponiveis.append(self)

    def reset(self, x, y, cor, vx=None, vy=None, vida=25, tamanho=5):
        self.cor = tuple(cor[:3])
        self.vida_max = max(1, int(vida))
        self.vida = int(vida)
        self.tamanho = int(tamanho)
        self.vx = vx if vx is not None else random.uniform(-4, 4)
        self.vy = vy if vy is not None else random.uniform(-4, 4)

        chave = (self.tamanho, self.tamanho)
        imagem = self._imagens_por_tamanho.get(chave)
        if imagem is None:
            try:
                imagem = pygame.Surface(chave).convert()
            except Exception:
                imagem = pygame.Surface(chave)
            self._imagens_por_tamanho[chave] = imagem
        imagem.fill(self.cor)
        imagem.set_alpha(255)
        self.image = imagem
        self.rect = self.image.get_rect(center=(x, y))
        self.ativo = True

    def update(self, *args):
        if not self.ativo:
            return
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vida -= 1
        if self.vida <= 0:
            self.ativo = False
            self.kill()
        else:
            self.image.set_alpha(max(0, min(255, int((self.vida / self.vida_max) * 255))))
