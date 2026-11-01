"""v3.232.0 — FLO-001: bruma da Floresta, composicao alfa correta.

Reutiliza o overlay e a hierarquia de render existentes. A versao anterior
escrevia RGBA quase transparente DIRETO no panorama opaco, apagando a tinta
das arvores. Preparamos as mesmas elipses num pequeno atlas SRCALPHA cacheado
e fazemos BLIT normal, em vez de substituir o alfa do panorama.
Nenhuma modificacao nos chunks, colisoes, parallax, geometria ou outras artes.
"""
import pygame
from pixelrush_biomes2_v3142 import ModularBiomeScene as _Origem

_CACHE_BRUMA = {}
_LIMITE = 2  # manhã e chuva, únicas configurações usadas no jogo
_INSTALADO = False
_ORIGINAL = _Origem._mist_patch


def _bruma_composta(self, surf, x, y, w, h, color):
    if self.biome != 'floresta':
        return _ORIGINAL(self, surf, x, y, w, h, color)
    chave = (int(w), int(h), tuple(color))
    sprite = _CACHE_BRUMA.get(chave)
    if sprite is None:
        largura, altura = int(w), int(h)
        sprite = pygame.Surface((largura, altura + 3), pygame.SRCALPHA)
        for k in range(0, altura, 3):
            alfa = max(6, color[3] - k * 2)
            pygame.draw.ellipse(sprite, (*color[:3], alfa),
                                (0, k, largura, max(2, altura - k)))
        if len(_CACHE_BRUMA) >= _LIMITE:
            _CACHE_BRUMA.clear()
        _CACHE_BRUMA[chave] = sprite
    surf.blit(sprite, (int(x), int(y)))


def instalar():
    global _INSTALADO
    if not _INSTALADO:
        _Origem._mist_patch = _bruma_composta
        _INSTALADO = True
