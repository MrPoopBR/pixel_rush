"""Cache opcional do FUNDO durante FPS baixo no Android (sem tocar jogabilidade).

Somente usa blit das camadas anteriores aos perigos/sprites/HUD. Renderiza
um novo quadro de fundo no maximo a cada 2 quadros visiveis; nunca guarda
sprites, moedas, personagens, UI, hitboxes, saves, fisica ou efeitos de replay.
"""
import pygame

class CacheFundoMobile:
    def __init__(self):
        self._quadro = None
        self._chave = None
        self._idade = 0
        self.acertos = 0
        self.recriacoes = 0

    def invalidar(self):
        self._chave = None
        self._idade = 0

    def reusar(self, superficie, chave, habilitado):
        if not habilitado:
            self.invalidar()
            return False
        if (self._quadro is None or chave != self._chave or self._idade >= 1
                or self._quadro.get_size() != superficie.get_size()):
            return False
        superficie.blit(self._quadro, (0, 0))
        self._idade += 1
        self.acertos += 1
        return True

    def guardar(self, superficie, chave, habilitado):
        if not habilitado:
            return
        if self._quadro is None or self._quadro.get_size() != superficie.get_size():
            # Memoria limitada a 450x800x3 bytes (uma Surface RGB do display).
            self._quadro = pygame.Surface(superficie.get_size()).convert(superficie)
        self._quadro.blit(superficie, (0, 0))
        self._chave = chave
        self._idade = 0
        self.recriacoes += 1
