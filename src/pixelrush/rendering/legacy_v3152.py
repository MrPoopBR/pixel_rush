"""v3.152.0 — contorno de ameaças pre-renderizado e cacheado.

Mesmo desenho visual da v3.151.0: contorno escuro de 5px e acento
âmbar alternado de 2px, mais a sombra rente ao chão. Apenas o custo de
construção das linhas sai do quadro corrente. Não toca colisões nem sprites.
"""
from collections import OrderedDict
import pygame


class ContornosCacheados:
    def __init__(self, largura=450, altura=800, capacidade=96):
        self.largura = int(largura)
        self.altura = int(altura)
        self.capacidade = max(4, int(capacidade))
        self._cache = OrderedDict()
        self.construidos = 0
        self.acertos = 0
        self.misses = 0
        self._margem = 4

    def limpar(self):
        self._cache.clear()

    def _obter(self, imagem):
        # Surface como chave: evita colisão de id() quando imagens antigas
        # são liberadas pelo Pygame.
        item = self._cache.get(imagem)
        if item is not None:
            self.acertos += 1
            self._cache.move_to_end(imagem)
            return item
        self.misses += 1
        w, h = imagem.get_size()
        pad = self._margem
        tons = ((255, 221, 113), (255, 180, 74))
        try:
            pts = tuple(pygame.mask.from_surface(imagem, 100).outline(2))
        except pygame.error:
            pts = ()
        if len(pts) >= 3:
            coords = [(x + pad, y + pad) for x, y in pts]
            frames = []
            for cor in tons:
                s = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
                pygame.draw.lines(s, (14, 17, 27), True, coords, 5)
                pygame.draw.lines(s, cor, True, coords, 2)
                frames.append(s)
            item = tuple(frames)
            self.construidos += 1
        else:
            item = ()
        self._cache[imagem] = item
        if len(self._cache) > self.capacidade:
            self._cache.popitem(last=False)
        return item

    def desenhar(self, superficie, obstaculos, frame_contador=0):
        # Uma blit por perigo visível; custo do mask/contorno apenas no cache miss.
        fase = 0 if (frame_contador // 12) % 2 == 0 else 1
        for obj in obstaculos:
            r = obj.rect
            if r.right < -6 or r.left > self.largura + 6:
                continue
            img = getattr(obj, 'image', None)
            if img is None or img.get_width() < 3 or img.get_height() < 3:
                continue
            surfaces = self._obter(img)
            if surfaces:
                superficie.blit(surfaces[fase], (r.x - self._margem, r.y - self._margem))
            if r.bottom >= self.altura - 132:
                pygame.draw.ellipse(superficie, (37, 36, 48),
                                    (r.centerx - 16, self.altura - 82, 32, 5), 1)
