"""Polimento visual Pixel Rush v3.171.0 — sem alteração de sprites/hitboxes.
Elementos de baixo custo para HUD/menu e contato do corredor com piso.
"""
import pygame

CORES = {
    'cidade': (93, 139, 163), 'neve': (191, 225, 242),
    'deserto': (205, 160, 97), 'vulcao': (215, 111, 74),
    'floresta': (105, 179, 105), 'cidade_futurista': (98, 218, 237),
    'ilhas_celestes': (160, 224, 208), 'reino_submerso': (115, 202, 214)
}


def sombra_contato(surface, jogador, biome, qualidade_leve=False):
    if jogador is None or getattr(jogador, 'jetpack_fase', None) is not None:
        return
    chao = int(jogador.chao_y)
    altura = max(0, chao - int(jogador.rect.bottom))
    # Reduz o tamanho com a distância; mantém sombra fora da hitbox do corredor.
    size = max(12, 36 - min(20, altura // 8))
    color = CORES.get(biome, CORES['cidade'])
    if altura > 90:
        cor = tuple(int(c * .60) for c in color)
    else:
        cor = tuple(int(c * .43) for c in color)
    pygame.draw.ellipse(surface, cor, (jogador.rect.centerx-size//2, chao-3, size, 4))
    if not qualidade_leve and altura < 42:
        pygame.draw.line(surface, color, (jogador.rect.centerx-9, chao-2),
                         (jogador.rect.centerx+9, chao-2), 1)


def painel_menu(surf, frame, modo_leve=False):
    # Formas muito pequenas para dar acabamento: nada é alocado por quadro.
    c = (87, 205, 232)
    for x in (45, 405):
        lado = 1 if x < 200 else -1
        pygame.draw.line(surf, c, (x, 222), (x + lado * 15, 222), 1)
        pygame.draw.line(surf, (160, 224, 239), (x, 222), (x, 232), 1)
    if not modo_leve:
        px = 95 + (frame % 260)
        pygame.draw.line(surf, (176, 221, 233), (px, 218), (min(390, px+6), 218), 1)

# As faixas são preparadas somente no primeiro uso de cada tema.
_CACHE_PROFUNDIDADE = {}


def profundidade_cinematografica(surface, bioma, night=False, leve=False):
    """Vinheta discreta por bioma. Não toca nos sprites ou colisões."""
    if leve:
        return
    key = (bioma, bool(night))
    overlay = _CACHE_PROFUNDIDADE.get(key)
    if overlay is None:
        color = CORES.get(bioma, CORES['cidade'])
        overlay = pygame.Surface((450, 460), pygame.SRCALPHA)
        # Diminui discretamente o contraste das bordas do segundo plano.
        for band in range(0, 26, 2):
            a = max(0, 8 - band//4) if night else max(0, 6 - band//5)
            pygame.draw.line(overlay, (*color, a), (band, 25), (band, 430), 2)
            pygame.draw.line(overlay, (*color, a), (449-band, 25), (449-band, 430), 2)
        pygame.draw.line(overlay, (*color, 13 if night else 8), (26, 435), (423, 435), 1)
        _CACHE_PROFUNDIDADE[key] = overlay
    surface.blit(overlay, (0, 144))


def brilho_coletaveis(surface, moedas, powerups, frame, leve=False):
    """Realce de brilho localizado, com limite fixo e sem criar sprites extras."""
    if leve:
        return
    # Brilha em poucos objetos por quadro, mantendo fundo e perigos legíveis.
    for i, coin in enumerate(moedas):
        if i >= 5:
            break
        rect = coin.rect
        if 0 <= rect.centerx < 450 and 80 < rect.centery < 760 and (frame//12+i) % 4 == 0:
            pygame.draw.line(surface,(255,245,178),(rect.centerx+12,rect.centery-13),
                             (rect.centerx+16,rect.centery-13),1)
            pygame.draw.line(surface,(255,245,178),(rect.centerx+14,rect.centery-15),
                             (rect.centerx+14,rect.centery-11),1)
    for i, power in enumerate(powerups):
        if i >= 3:
            break
        rect = power.rect
        if 0 <= rect.centerx < 450 and (frame//14+i) % 3 == 0:
            pygame.draw.line(surface,(198,241,249),(rect.left-3,rect.top+5),
                             (rect.left-3,rect.top+11),1)
            pygame.draw.line(surface,(198,241,249),(rect.left-6,rect.top+8),
                             (rect.left,rect.top+8),1)


def acabamento_hud(surface, frame, leve=False):
    # Pequenos acentos, fora das barras/textos e da área de clique.
    for x, color in ((16,(87,214,234)),(265,(238,201,108))):
        pygame.draw.line(surface,color,(x,13),(x+19,13),1)
