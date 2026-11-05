"""v3.170.0 — faixa viva otimizada para leitura em alta velocidade.

A pista continua usando os tiles já existentes; apenas consolida as
sucessivas camadas antigas de micro-linhas móveis em um sprite estático
cacheado (por bioma/noite/clima) + no máximo 3 riscos de velocidade.
Não muda scroll, físicas, colisões ou obstáculos.
"""
import math
import pygame

CORES = {
    'cidade': ((210, 219, 224), (155, 170, 190)),
    'neve': ((246, 252, 255), (198, 226, 246)),
    'deserto': ((248, 221, 165), (215, 172, 115)),
    'floresta': ((181, 223, 148), (128, 187, 114)),
    'vulcao': ((255, 183, 94), (181, 101, 74)),
    'cidade_futurista': ((100, 237, 253), (229, 132, 255)),
    'ilhas_celestes': ((232, 251, 248), (170, 234, 202)),
    'reino_submerso': ((165, 240, 232), (105, 201, 217)),
}
_CACHE = {}


def _overlay(cenario, noite, molhado, largura=450):
    chave = (cenario, noite, molhado, largura)
    s = _CACHE.get(chave)
    if s is not None:
        return s
    cor, acento = CORES.get(cenario, CORES['cidade'])
    s = pygame.Surface((largura, 28), pygame.SRCALPHA)
    intensidade = 85 if noite else 54
    for x in range(16, largura - 16, 82):
        pygame.draw.line(s, (*cor, intensidade), (x, 5), (x + 11, 5), 1)
        pygame.draw.line(s, (*acento, 43), (x + 19, 18), (x + 29, 18), 1)
    for x in (4, largura - 34):
        pygame.draw.line(s, (*acento, 65), (x, 3), (x + 27, 3), 1)
        pygame.draw.line(s, (*cor, 48), (x + 5, 22), (x + 24, 22), 1)
    if molhado:
        for x in range(30, largura - 24, 103):
            pygame.draw.line(s, (*cor, 86), (x, 10), (x + 18, 11), 1)
            pygame.draw.line(s, (*acento, 65), (x + 7, 14), (x + 20, 14), 1)
    _CACHE[chave] = s
    return s


def desenhar_pista_legivel(self, superficie):
    """Chamado DEPOIS dos tiles existentes. Quadro comum: uma única blit."""
    cenario = self.cenario
    night = float(getattr(self, 'peso_noite', 0.0)) > .35
    climate = getattr(self, 'clima_tipo', 'limpo')
    wet = climate in ('chuva', 'tempestade', 'chuva_acida')
    superficie.blit(_overlay(cenario, night, wet), (0, 731))

    # A velocidade real já influencia desloc_chao; diferenças com wrap são
    # tratadas sem alterar o scroll. O efeito rápido é puramente cosmético.
    novo = float(self.desloc_chao)
    anterior = getattr(self, '_v3170_scroll_anterior', None)
    self._v3170_scroll_anterior = novo
    if anterior is None:
        return
    delta = (novo - anterior) % 900.0
    if delta <= 9.0 or delta > 80.0:
        return
    cor, _ = CORES.get(cenario, CORES['cidade'])
    for i in range(3):
        x = int((i * 161 - novo * (0.65 + .07 * i)) % 450)
        y = 742 + 5 * i
        pygame.draw.line(superficie, cor, (x, y), (x + 7 + min(10, int(delta) // 3), y), 1)
