"""HUD mais limpo para v3.133: sem card superior direito de poderes.

Mantém distância/moedas em destaque, missões resumidas e combo/febre
compactos. Poderes ativos viram pequenos chips discretos sob o painel das
missões, poupando área nobre da pista.
"""
import pygame

# Pixel Rush v3.153.0: pausa abaixo do card COMBO/FEBRE.
# Uma só área compartilhada entre desenho e detecção do toque/clique.
HUD_PAUSA_AREA = (395, 135, 40, 40)

BG = (17, 28, 47)
BORDA = (65, 105, 133)
TEXTO = (237, 246, 249)
SUAVE = (151, 172, 190)
OURO = (255, 217, 105)
CIANO = (115, 225, 240)
VERDE = (132, 214, 171)


def _painel(surf, area, cor=BORDA):
    pygame.draw.rect(surf, BG, area, border_radius=9)
    pygame.draw.rect(surf, cor, area, 1, border_radius=9)


def _txt(surf, render, fonte, texto, cor, x, y):
    surf.blit(render(fonte, str(texto), cor), (int(x), int(y)))


def _coletar_ativos(jogador, pt=True):
    ativos = []
    if jogador is None:
        return ativos
    for nome, atributo in ((('IMÃ' if pt else 'MAG'), 'tempo_ima'),
                           ('TURBO', 'tempo_turbo'), ('2X', 'tempo_mult'),
                           (('LENTO' if pt else 'SLOW'), 'tempo_slow'),
                           ('JET', 'tempo_jetpack'), ('CRONO', 'tempo_crono'),
                           ('FANT.' if pt else 'GHOST', 'tempo_turbo_fantasma')):
        ticks = max(0, int(getattr(jogador, atributo, 0)))
        if ticks:
            ativos.append((f'{nome} {max(1, (ticks + 59) // 60)}s', CIANO))
    for nome, valor in (('ESC', getattr(jogador, 'escudo_hits', 0)),
                        ('CLONE', getattr(jogador, 'clones_ativos', 0)),
                        ('PRISMA', getattr(jogador, 'prisma_hits', 0))):
        if valor > 0:
            ativos.append((f'{nome} {int(valor)}', VERDE))
    return ativos


def _chips_poderes(surf, render, fonte, ativos, x, y, max_w=238):
    if not ativos:
        return 0
    cx = x
    cy = y
    row_h = 18
    used = row_h
    for rotulo, cor in ativos[:6]:
        w = max(42, min(92, fonte.size(rotulo)[0] + 14))
        if cx + w > x + max_w:
            cx = x
            cy += row_h + 4
            used += row_h + 4
        rect = pygame.Rect(cx, cy, w, row_h)
        pygame.draw.rect(surf, BG, rect, border_radius=8)
        pygame.draw.rect(surf, cor, rect, 1, border_radius=8)
        _txt(surf, render, fonte, rotulo, cor, cx + 7, cy + 2)
        cx += w + 6
    return used


def desenhar_hud_compacto(surf, *, metros, moedas, missoes, jogador, combo, multiplicador,
                          combo_timer, febre, febre_timer, febre_turbo_restante,
                          idioma, frame, fonte_grande, fonte_missoes, fonte_pequena,
                          render, botao_pausa):
    pt = idioma == 'pt_BR'

    # Topo principal: distância e moedas.
    _painel(surf, (15, 15, 238, 72))
    _txt(surf, render, fonte_pequena, 'DISTÂNCIA' if pt else 'DISTANCE', SUAVE, 26, 20)
    _txt(surf, render, fonte_grande, f'{int(metros)} m', TEXTO, 25, 34)
    pygame.draw.circle(surf, (139, 103, 33), (36, 75), 7)
    pygame.draw.circle(surf, OURO, (36, 73), 6)
    pygame.draw.circle(surf, (255, 246, 186), (34, 71), 2)
    _txt(surf, render, fonte_missoes, str(int(moedas)), OURO, 49, 66)

    # Pausa abaixo do card de combo/febre; área de toque v3.153.0.
    pygame.draw.rect(surf, BG, botao_pausa, border_radius=9)
    pygame.draw.rect(surf, BORDA, botao_pausa, 1, border_radius=9)
    pygame.draw.rect(surf, TEXTO, (botao_pausa.x + 13, botao_pausa.y + 11, 5, 18), border_radius=2)
    pygame.draw.rect(surf, TEXTO, (botao_pausa.x + 23, botao_pausa.y + 11, 5, 18), border_radius=2)

    # Missões resumidas.
    completas = sum(bool(m.get('concluida')) for m in missoes)
    total = max(1, len(missoes))
    _painel(surf, (15, 94, 238, 35))
    _txt(surf, render, fonte_pequena, ('MISSÕES' if pt else 'MISSIONS') + f'  {completas}/{len(missoes)}', SUAVE, 25, 99)
    pygame.draw.rect(surf, (43, 62, 78), (25, 118, 214, 4), border_radius=2)
    if completas:
        pygame.draw.rect(surf, VERDE, (25, 118, int(214 * completas / total), 4), border_radius=2)

    # Poderes ativos discretos, sem card superior direito.
    ativos = _coletar_ativos(jogador, pt)
    if ativos:
        _painel(surf, (15, 136, 238, 26 + (22 if len(ativos) > 3 else 0)), CIANO)
        _txt(surf, render, fonte_pequena, 'ATIVOS' if pt else 'ACTIVE', SUAVE, 24, 141)
        _chips_poderes(surf, render, fonte_pequena, ativos, 74, 139, max_w=170)

    # Combo/FEBRE alinhado pelo topo com o card de distância.
    box_y = 15
    box_h = 104
    _painel(surf, (264, box_y, 171, box_h), OURO if febre_timer else BORDA)
    _txt(surf, render, fonte_pequena, f'COMBO {int(combo)}  x{int(multiplicador)}',
         OURO if combo else SUAVE, 274, box_y + 5)
    pygame.draw.rect(surf, (43, 62, 78), (274, box_y + 27, 151, 5), border_radius=2)
    if combo_timer > 0:
        pygame.draw.rect(surf, OURO, (274, box_y + 27, min(151, int(151 * combo_timer / 180)), 5), border_radius=2)

    nome_febre = 'FEBRE' if pt else 'FEVER'
    status = ('ATIVA' if pt else 'ACTIVE') if febre_timer else f'{float(febre):.2f}%'
    _txt(surf, render, fonte_pequena, f'{nome_febre}  {status}', OURO if febre_timer else CIANO, 274, box_y + 41)
    tamanho = int(151 * (febre_timer / (900.0 if febre_turbo_restante > 0 else 480.0)
                          if febre_timer else febre / 100.0))
    pygame.draw.rect(surf, (43, 62, 78), (274, box_y + 61, 151, 5), border_radius=2)
    if tamanho > 0:
        pygame.draw.rect(surf, OURO if febre_timer else CIANO,
                         (274, box_y + 61, max(1, min(151, tamanho)), 5), border_radius=2)

    if jogador is not None and (getattr(jogador, 'tempo_impulso', 0) > 0 or getattr(jogador, 'carga_impulso', 0) > 0):
        nivel = (jogador.tempo_impulso / 120.0 if jogador.tempo_impulso > 0
                 else jogador.carga_impulso / 100.0)
        _txt(surf, render, fonte_pequena, 'IMPULSO' if pt else 'BOOST', SUAVE, 274, box_y + 75)
        pygame.draw.rect(surf, (43, 62, 78), (344, box_y + 81, 80, 5), border_radius=2)
        pygame.draw.rect(surf, CIANO, (344, box_y + 81, max(1, min(80, int(80 * nivel))), 5), border_radius=2)
