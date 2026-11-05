"""Hidrante de rua para a Cidade (v3.276.0), sem dependências do spawn global.

Sprite com hitbox local compatível com _hitboxes_locais_obstaculo.
Spawn é autorizado exclusivamente pela seleção de cenário = cidade.
"""
import pygame

class HidranteCidade(pygame.sprite.Sprite):
    tipo = 'hidrante_cidade'
    nome = 'Hidrante de Rua'
    bioma = 'cidade'
    qtd_cactos = 0
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((51, 60), pygame.SRCALPHA)
        s = self.image
        # Contorno de aço, corpo vermelho, duas saídas laterais e refletor.
        pygame.draw.ellipse(s, (20, 31, 49), (3, 53, 45, 6))
        pygame.draw.rect(s, (45, 55, 68), (16, 12, 22, 40), border_radius=6)
        pygame.draw.rect(s, (186, 54, 52), (14, 13, 24, 40), border_radius=6)
        pygame.draw.rect(s, (238, 106, 76), (19, 14, 8, 37), border_radius=3)
        pygame.draw.rect(s, (191, 61, 56), (5, 29, 41, 14), border_radius=5)
        pygame.draw.rect(s, (240, 183, 110), (4, 29, 8, 13), border_radius=3)
        pygame.draw.rect(s, (240, 183, 110), (39, 29, 8, 13), border_radius=3)
        pygame.draw.rect(s, (58, 62, 75), (19, 6, 14, 10), border_radius=3)
        pygame.draw.rect(s, (243, 196, 117), (21, 7, 10, 5), border_radius=2)
        pygame.draw.rect(s, (64, 63, 72), (11, 47, 31, 6), border_radius=2)
        self.rect = s.get_rect(left=int(x), bottom=730)
        self._x = float(x)
        self._hitboxes_precisas_v342 = (
            pygame.Rect(15, 8, 24, 44),
            pygame.Rect(5, 30, 43, 13),
        )
    def update(self, velocidade_jogo):
        self._x -= float(velocidade_jogo)
        self.rect.x = int(self._x)
        if self.rect.right < -60:
            self.kill()
