"""Plano G v3.199.0 — luz volumetrica ilustrada somente no panorama.

Aproveita a iluminacao de materiais (v3.177) e o fluxo atmosferico existentes:
este passe nao desenha particulas/clima, nao altera tiles, mapas tecnicos,
colisoes nem mundo. Utiliza uma superficie RGB aditiva pre-renderizada por
bioma/iluminacao/clima e uma unica composicao no pano de fundo por frame.
"""
from collections import OrderedDict

import pygame
from pixelrush_luz_materiais_v3177 import PERFIS

LARGURA, ALTURA = 450, 374
LIMITE = 6
# Formato RGB de 24 bits, em um conjunto de ate 6 superficies de 450x374:
# no maximo 3.03 MB de dados de pixels (fora overhead SDL/Python).
_CACHE = OrderedDict()
_CLIMAS_DENSOS = frozenset(('nevasca', 'neblina', 'tempestade', 'chuva',
                           'chuva_acida', 'tempestade_areia', 'areia', 'cinzas'))


def _mistura(a, b, t):
    return tuple(int(a[i] * (1.0 - t) + b[i] * t + .5) for i in range(3))


def _estado(noite, fase, clima):
    n = max(0., min(1., float(noite)))
    escuro = min(4, int(n * 4.0 + .5))
    crepusculo = int(.12 < float(fase) < .25 or .68 < float(fase) < .83)
    denso = int(clima in _CLIMAS_DENSOS)
    return escuro, crepusculo, denso


def _gerar(bioma, noite, crepusculo, denso):
    """Apenas pintura de LUZ em RGB: nenhuma modificacao de alfa/fonte.

    A zona proxima ao contato de pista (y >= 375) fica zero. O formato 24bpp
    evita grandes texturas RGBA e nao necessita shader/NumPy por frame.
    """
    base = pygame.Surface((LARGURA, ALTURA), depth=24)
    base.fill((0, 0, 0))
    reflexo, _, _, _, emissao = PERFIS[bioma]
    cor = _mistura(reflexo, emissao, noite / 4.)
    if crepusculo and noite <= 2:
        cor = _mistura(cor, (255, 175, 104), .36)
    if denso:
        cor = _mistura(cor, (174, 184, 198), .34)

    # Névoa de distância: faixa contínua (não partículas nem novos objetos),
    # máxima atrás dos planos FAR/MID, desaparece antes da pista/hitboxes.
    # Quantizar sem dithering impede tremor e bloqueia alocações em loop.
    for y in range(34, 374, 3):
        distancia = y / 374.
        faixa = max(0., 1. - abs(distancia - .51) / .52)
        peso = faixa ** 1.35
        intensidade = (0.105 + .085 * denso + .033 * crepusculo +
                       .020 * (noite / 4.)) * peso
        # Energia ambiente mais rica em áreas luminosas, preserva a pista.
        rgb = tuple(min(255, round(c * intensidade)) for c in cor)
        if max(rgb) > 0:
            pygame.draw.rect(base, rgb, (0, y, LARGURA, min(3, 374-y)))

    # Volumes direcionais translúcidos, conectados à região superior do
    # cenário (iluminação, não sprites de raios). Concentrar em poucos feixes
    # amplos dá volume sem criar ruído, fragmentos flutuantes ou tremores.
    inclinacao = {'cidade': -11, 'neve': 15, 'deserto': -20,
                  'floresta': 14, 'vulcao': -17,
                  'cidade_futurista': -14, 'ilhas_celestes': 18}[bioma]
    energia = 0.074 + .039 * crepusculo + .041 * (noite / 4.)
    if denso:
        energia *= .68
    for raiz in (72, 274):
        for passo, frac in ((0, 1.0), (1, .64), (2, .31)):
            x = raiz + passo * 13
            largura_top = 3 + passo * 4
            largura_base = 17 + passo * 7
            brilho = energia * frac
            tint = tuple(round(c * brilho) for c in cor)
            pontos = [(x, 49), (x+largura_top, 49),
                      (x + inclinacao + largura_base, 292),
                      (x + inclinacao - largura_base//3, 292)]
            pygame.draw.polygon(base, tint, pontos)
    # Fade de máscara determinístico para não deixar borda horizontal dura.
    return base


def aplicar(destino, bioma, noite, fase, clima):
    """Usar APENAS dentro de LivingWorld._city_surface('image', False).

    BLEND_RGB_ADD nao altera o alfa da superfície: céu/transparências,
    elementos jogaveis e demais passes continuam inteiramente isolados.
    """
    if bioma not in PERFIS:
        return
    estado = _estado(noite, fase, clima)
    chave = (bioma, *estado)
    filtro = _CACHE.get(chave)
    if filtro is None:
        filtro = _gerar(bioma, *estado)
        _CACHE[chave] = filtro
        if len(_CACHE) > LIMITE:
            _CACHE.popitem(last=False)
    else:
        _CACHE.move_to_end(chave)
    destino.blit(filtro, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def estatisticas():
    return {'entradas': len(_CACHE), 'limite': LIMITE,
            'bytes_pixels_estimados': sum(s.get_pitch() * s.get_height()
                                         for s in _CACHE.values())}
