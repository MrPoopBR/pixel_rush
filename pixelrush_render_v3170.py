"""v3.170.0 — realce de ameaças com silhueta em cache por bioma.

Substitui somente as cores e a estrutura do contorno de alto contraste;
nenhuma imagem original, física, hitbox, ou taxa de spawn é alterada.
"""
from collections import OrderedDict
import pygame

PALETAS = {
    'cidade': ((254, 222, 130), (255, 242, 199)),
    'neve': ((255, 180, 83), (255, 217, 147)),
    'deserto': ((119, 240, 255), (201, 252, 255)),
    'floresta': ((251, 225, 108), (255, 246, 177)),
    'vulcao': ((120, 237, 255), (207, 252, 255)),
    'cidade_futurista': ((255, 213, 104), (255, 238, 176)),
    'ilhas_celestes': ((255, 190, 113), (255, 239, 164)),
}


class ContornosLegiveis:
    """Duas superfícies cacheadas por sprite; 1 blit de contorno por perigo.

    Respeita a silhueta real (inclusive transparência da arte); objetos com
    animações recebem versões cacheadas sem criar efeitos por quadro.
    """
    def __init__(self, largura=450, altura=800, capacidade=96):
        self.largura = largura
        self.altura = altura
        self.capacidade = max(16, int(capacidade))
        self._cache = OrderedDict()
        self.construidos = 0
        self.acertos = 0
        self.misses = 0
        self._margem = 4

    def limpar(self):
        self._cache.clear()

    @staticmethod
    def _bioma(obj):
        return getattr(obj, 'bioma', getattr(obj, 'cenario', 'cidade'))

    def _obter(self, imagem, bioma):
        chave = (imagem, bioma)
        if chave in self._cache:
            self.acertos += 1
            self._cache.move_to_end(chave)
            return self._cache[chave]
        self.misses += 1
        w, h = imagem.get_size()
        pad = self._margem
        try:
            pts = pygame.mask.from_surface(imagem, 110).outline(2)
        except pygame.error:
            pts = []
        cores = PALETAS.get(bioma, PALETAS['cidade'])
        if len(pts) >= 3:
            coords = tuple((x + pad, y + pad) for x, y in pts)
            frames = []
            for cor in cores:
                s = pygame.Surface((w + 2 * pad, h + 2 * pad), pygame.SRCALPHA)
                # A borda externa escura isola as ameaças dos fundos coloridos.
                pygame.draw.lines(s, (13, 20, 33, 245), True, coords, 6)
                pygame.draw.lines(s, (*cor, 255), True, coords, 2)
                frames.append(s)
            item = tuple(frames)
            self.construidos += 1
        else:
            item = ()
        self._cache[chave] = item
        if len(self._cache) > self.capacidade:
            self._cache.popitem(last=False)
        return item

    def desenhar(self, superficie, obstaculos, frame_contador=0):
        fase = (frame_contador // 14) % 2
        for obj in obstaculos:
            r = obj.rect
            if r.right < -6 or r.left > self.largura + 6:
                continue
            imagem = getattr(obj, 'image', None)
            if imagem is None or imagem.get_width() < 3 or imagem.get_height() < 3:
                continue
            cached = self._obter(imagem, self._bioma(obj))
            if cached:
                superficie.blit(cached[fase], (r.x - self._margem, r.y - self._margem))
            if r.bottom >= self.altura - 132:
                pygame.draw.ellipse(superficie, (20, 28, 42),
                                    (r.centerx - 17, self.altura - 81, 34, 5), 1)
