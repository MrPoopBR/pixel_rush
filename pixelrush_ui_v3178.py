"""Pixel Rush v3.178.0 — acabamento de HUD/menus do Plano D, etapa 4.

Somente superfícies visuais, sem alterar rects clicáveis, física ou dados.
Compartilha os renderizadores existentes, evitando duplicar a lógica do HUD.
Compatível com Python 3.9, Pygame-ce e SDL2.
"""
import math
from collections import OrderedDict
import pygame

PAPEL = (16, 27, 46)
TOPO = (33, 50, 77)
BRANCO = (241, 249, 252)
SUAVE = (185, 209, 225)
CIANO = (99, 225, 247)
OURO = (246, 210, 112)
VERDE = (116, 220, 179)
BORDA = (88, 143, 177)
_CACHE_PAINEL = OrderedDict()
_CACHE_MAX = 96


def mistura(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1[:3], c2[:3]))


def _painel_em_cache(tamanho, destaque, cabecalho=False, discreto=False, tipo='padrao'):
    w, h = map(int, tamanho)
    color = tuple(destaque[:3])
    chave = (w, h, color, bool(cabecalho), bool(discreto), tipo)
    p = _CACHE_PAINEL.get(chave)
    if p is not None:
        _CACHE_PAINEL.move_to_end(chave)
        return p
    p = pygame.Surface((w, h), pygame.SRCALPHA)
    if w <= 1 or h <= 1:
        return p
    raio = min(12, max(5, h // 6))
    body = PAPEL if tipo != 'botao' else mistura(PAPEL, color, .35)
    pygame.draw.rect(p, (*body, 247), p.get_rect(), border_radius=raio)
    # Quatro bandas tonais horizontais: volume sem gradiente borrado.
    pygame.draw.rect(p, (*TOPO, 235), (2, 2, w - 4, max(3, min(h // 3, 13))),
                     border_top_left_radius=max(3, raio - 2), border_top_right_radius=max(3, raio - 2))
    if h > 30:
        for k in range(3):
            yy = h - 13 + k * 3
            pygame.draw.line(p, (*mistura(body, color, .07 + .025 * k), 120),
                             (6, yy), (w - 7, yy), 1)
    borda = mistura(color, TOPO, .18 if not discreto else .50)
    pygame.draw.rect(p, (*borda, 255), p.get_rect().inflate(-1, -1),
                     2 if not discreto else 1, border_radius=raio)
    # Cantos internos com hierarquia; não alteram o conteúdo/área clicável.
    if w >= 65:
        pygame.draw.line(p, (*mistura(color, BRANCO, .36), 220),
                         (12, 4), (min(w - 14, 51), 4), 1)
        pygame.draw.line(p, (*mistura(color, BRANCO, .20), 130),
                         (w - 41, h - 5), (w - 12, h - 5), 1)
    if cabecalho and w >= 110 and h >= 45:
        pygame.draw.line(p, (*color, 150), (13, min(22, h // 4)),
                         (w - 13, min(22, h // 4)), 1)
    _CACHE_PAINEL[chave] = p
    if len(_CACHE_PAINEL) > _CACHE_MAX:
        _CACHE_PAINEL.popitem(last=False)
    return p


def painel_identidade(surf, rect, destaque=CIANO, cabecalho=False, discreto=False):
    r = pygame.Rect(rect)
    if r.w < 4 or r.h < 4:
        return
    pygame.draw.rect(surf, (8, 14, 25), r.move(0, 3), border_radius=min(12, r.h // 6))
    surf.blit(_painel_em_cache(r.size, destaque, cabecalho, discreto), r.topleft)


def hud_painel(surf, area, cor=BORDA):
    r = pygame.Rect(area)
    if r.w < 4 or r.h < 4:
        return
    pygame.draw.rect(surf, (9, 16, 29), r.move(0, 2), border_radius=8)
    surf.blit(_painel_em_cache(r.size, cor, False, True, 'hud'), r.topleft)


def instalar_hud(modulo_hud):
    """Aproveita renderização de valores/status do HUD existente; muda somente cartões."""
    modulo_hud._painel = hud_painel
    modulo_hud.BG = PAPEL
    modulo_hud.BORDA = BORDA
    modulo_hud.TEXTO = BRANCO
    modulo_hud.SUAVE = SUAVE
    modulo_hud.OURO = OURO
    modulo_hud.CIANO = CIANO
    modulo_hud.VERDE = VERDE


def botao(surf, rect, texto, fonte_obj, cor_fundo, cor_texto, frame, ativo=False,
          rotulo_original=None):
    """Botões com arestas uniformes; rect original é usado sem deslocamento."""
    r = pygame.Rect(rect)
    cor = mistura(cor_fundo, (99, 164, 199), .17)
    pygame.draw.rect(surf, (7, 14, 26), r.move(0, 3), border_radius=10)
    surf.blit(_painel_em_cache(r.size, cor, False, False, 'botao'), r.topleft)
    if ativo:
        # Indicador discreto de foco no botão Jogar (sem ampliar hitbox visual).
        marker = int((math.sin(frame * .075) + 1) * 30)
        pygame.draw.line(surf, mistura(cor, BRANCO, .40),
                         (r.x + 15, r.bottom - 6), (r.right - 15 - marker // 12, r.bottom - 6), 2)
    if rotulo_original is not None:
        rotulo_original(surf, texto, fonte_obj, cor_texto, (7, 15, 27), r)


def palco_menu(surf, frame, leve, original):
    original(surf, frame, leve)
    # Iluminação do palco apenas; mantém a posição da skin e todos os botões.
    pygame.draw.arc(surf, (115, 217, 237), (136, 196, 178, 32),
                    math.pi * .12, math.pi * .88, 1)
    pygame.draw.line(surf, (87, 158, 187), (158, 230), (292, 230), 1)
    pygame.draw.circle(surf, (238, 211, 142), (225, 230), 2)


def card_menu(surf, rect, frame, acento, leve, original=None):
    r = pygame.Rect(rect)
    if r.w < 70:
        return
    c = mistura(acento, BRANCO, .24)
    pygame.draw.line(surf, c, (r.x + 12, r.y + 7), (r.x + min(59, r.w - 26), r.y + 7), 1)
    pygame.draw.line(surf, mistura(acento, PAPEL, .20),
                     (r.right - 25, r.bottom - 8), (r.right - 12, r.bottom - 8), 1)


def controles(surf, dados, fonte, pequena, rects, frame, original):
    """Refina painel de controle preservando texto, retângulos e acionamentos originais."""
    original(surf, dados, fonte, pequena, rects, frame)
    # Linha guia lateral e divisões fora dos labels/valores clicáveis.
    pygame.draw.line(surf, (96, 195, 212), (43, 100), (43, 685), 1)
    pygame.draw.line(surf, (234, 208, 133), (155, 147), (295, 147), 1)
    for key in ('modo', 'sensibilidade', 'canhoto', 'ajuda', 'gamepad'):
        r = pygame.Rect(rects[key])
        pygame.draw.line(surf, (108, 217, 230), (r.x + 4, r.y + 7), (r.x + 4, r.bottom - 7), 2)
        pygame.draw.line(surf, (60, 89, 115), (r.x + 12, r.bottom - 5),
                         (r.right - 12, r.bottom - 5), 1)
    r = pygame.Rect(rects['voltar'])
    pygame.draw.line(surf, (192, 247, 208), (r.x + 17, r.y + 7), (r.right - 17, r.y + 7), 1)


def acabamento_config(surf):
    """Linhas discretas fora dos textos da configuração; sem mover controles."""
    for y, cor in ((170, CIANO), (265, OURO), (366, VERDE), (441, CIANO),
                   (520, CIANO), (594, OURO)):
        pygame.draw.line(surf, cor, (46, y), (50, y), 2)
    pygame.draw.line(surf, (94, 157, 188), (67, 125), (383, 125), 1)
    pygame.draw.line(surf, (94, 157, 188), (67, 699), (383, 699), 1)


def acabamento_hud(surf, frame, leve=False):
    """Acentos alinhados aos cartões, preservando labels, valores e pause hitbox."""
    pygame.draw.line(surf, CIANO, (26, 16), (65, 16), 1)
    pygame.draw.line(surf, OURO, (274, 16), (312, 16), 1)
    pygame.draw.line(surf, (100, 173, 196), (25, 95), (77, 95), 1)
    # A seção inferior direita (pausa) só recebe um filete, nunca muda de posição.
    pygame.draw.line(surf, (116, 199, 219), (401, 136), (429, 136), 1)


def gameover(surf, frame, inicio, metros, moedas, combo, recorde, missoes, leve,
             original, dados=None):
    original(surf, frame, inicio, metros, moedas, combo, recorde, missoes, leve, dados)
    # Cards estatísticos: microdetalhes fora das métricas/labels.
    for i, cor in enumerate((CIANO, OURO, (190, 166, 247))):
        x = 62 + i * 111
        pygame.draw.line(surf, cor, (x + 12, 256), (x + 36, 256), 1)
        pygame.draw.line(surf, mistura(cor, PAPEL, .2), (x + 65, 322), (x + 90, 322), 1)
