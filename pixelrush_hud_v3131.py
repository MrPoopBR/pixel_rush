"""HUD compacto informativo, coordenadas 450x800, desenho leve com fontes já cacheadas.

Não lê entradas, não altera timers/recompensas, não instancia superfícies por quadro.
"""
import pygame

BG = (17, 28, 47)
BORDA = (65, 105, 133)
TEXTO = (237, 246, 249)
SUAVE = (151, 172, 190)
OURO = (255, 217, 105)
CIANO = (115, 225, 240)


def _painel(surf, area, cor=BORDA):
    pygame.draw.rect(surf, BG, area, border_radius=9)
    pygame.draw.rect(surf, cor, area, 1, border_radius=9)


def _txt(surf, render, fonte, texto, cor, x, y):
    surf.blit(render(fonte, str(texto), cor), (int(x), int(y)))


def desenhar_hud_compacto(surf, *, metros, moedas, missoes, jogador, combo, multiplicador,
                          combo_timer, febre, febre_timer, febre_turbo_restante,
                          idioma, frame, fonte_grande, fonte_missoes, fonte_pequena,
                          render, botao_pausa):
    pt = idioma == 'pt_BR'
    # Informações principais: sempre na primeira leitura (topo esquerdo).
    _painel(surf, (15, 15, 238, 72))
    _txt(surf, render, fonte_pequena, 'DISTÂNCIA' if pt else 'DISTANCE', SUAVE, 26, 20)
    _txt(surf, render, fonte_grande, f'{int(metros)} m', TEXTO, 25, 34)
    pygame.draw.circle(surf, (139, 103, 33), (36, 75), 7)
    pygame.draw.circle(surf, OURO, (36, 73), 6)
    pygame.draw.circle(surf, (255, 246, 186), (34, 71), 2)
    _txt(surf, render, fonte_missoes, str(int(moedas)), OURO, 49, 66)

    # Power-ups ativos: não mostrar dezenas de espaços vazios.
    ativos = []
    if jogador is not None:
        for nome, atributo in (('IMÃ' if pt else 'MAG', 'tempo_ima'),
                               ('TURBO', 'tempo_turbo'), ('2X', 'tempo_mult'),
                               ('LENTO' if pt else 'SLOW', 'tempo_slow'),
                               ('JET', 'tempo_jetpack'), ('CRONO', 'tempo_crono'),
                               ('FANT.', 'tempo_turbo_fantasma')):
            ticks = max(0, int(getattr(jogador, atributo, 0)))
            if ticks:
                ativos.append(f'{nome} {max(1, (ticks + 59) // 60)}s')
        for nome, valor in (('ESC', getattr(jogador, 'escudo_hits', 0)),
                            ('CLONE', getattr(jogador, 'clones_ativos', 0)),
                            ('PRISMA', getattr(jogador, 'prisma_hits', 0))):
            if valor > 0:
                ativos.append(f'{nome} {int(valor)}')
    _painel(surf, (264, 15, 121, 72), CIANO if ativos else BORDA)
    _txt(surf, render, fonte_pequena, 'PODERES' if pt else 'POWERS', SUAVE, 273, 20)
    if ativos:
        for i, rotulo in enumerate(ativos[:2]):
            _txt(surf, render, fonte_pequena, rotulo, CIANO, 273, 39 + i * 18)
        if len(ativos) > 2:
            _txt(surf, render, fonte_pequena, f'+{len(ativos)-2}', OURO, 356, 67)
    else:
        _txt(surf, render, fonte_pequena, '—', SUAVE, 273, 47)

    # Botão com o MESMO retângulo de toque da versão anterior.
    pygame.draw.rect(surf, BG, botao_pausa, border_radius=9)
    pygame.draw.rect(surf, BORDA, botao_pausa, 1, border_radius=9)
    pygame.draw.rect(surf, TEXTO, (botao_pausa.x + 13, botao_pausa.y + 11, 5, 18), border_radius=2)
    pygame.draw.rect(surf, TEXTO, (botao_pausa.x + 23, botao_pausa.y + 11, 5, 18), border_radius=2)

    # Missões: progresso resumido, não três textos longos sobre a pista.
    completas = sum(bool(m.get('concluida')) for m in missoes)
    total = max(1, len(missoes))
    _painel(surf, (15, 94, 238, 35))
    _txt(surf, render, fonte_pequena, ('MISSÕES' if pt else 'MISSIONS') + f'  {completas}/{len(missoes)}', SUAVE, 25, 99)
    pygame.draw.rect(surf, (43, 62, 78), (25, 118, 214, 4), border_radius=2)
    if completas:
        pygame.draw.rect(surf, (88, 192, 151), (25, 118, int(214 * completas / total), 4), border_radius=2)

    # Combo/Febre compacto: mantenha as porcentagens com duas casas decimais.
    _painel(surf, (264, 94, 171, 104), OURO if febre_timer else BORDA)
    _txt(surf, render, fonte_pequena, f'{"COMBO" if pt else "COMBO"} {int(combo)}  x{int(multiplicador)}',
         OURO if combo else SUAVE, 274, 99)
    pygame.draw.rect(surf, (43, 62, 78), (274, 121, 151, 5), border_radius=2)
    if combo_timer > 0:
        pygame.draw.rect(surf, OURO, (274, 121, min(151, int(151 * combo_timer / 180)), 5), border_radius=2)
    nome_febre = 'FEBRE' if pt else 'FEVER'
    status = ('ATIVA' if pt else 'ACTIVE') if febre_timer else f'{float(febre):.2f}%'
    _txt(surf, render, fonte_pequena, f'{nome_febre}  {status}', OURO if febre_timer else CIANO, 274, 135)
    tamanho = int(151 * (febre_timer / (900.0 if febre_turbo_restante > 0 else 480.0)
                          if febre_timer else febre / 100.0))
    pygame.draw.rect(surf, (43, 62, 78), (274, 155, 151, 5), border_radius=2)
    if tamanho > 0:
        pygame.draw.rect(surf, OURO if febre_timer else CIANO,
                         (274, 155, max(1, min(151, tamanho)), 5), border_radius=2)
    if jogador is not None and (jogador.tempo_impulso > 0 or jogador.carga_impulso > 0):
        nivel = (jogador.tempo_impulso / 120.0 if jogador.tempo_impulso > 0
                 else jogador.carga_impulso / 100.0)
        _txt(surf, render, fonte_pequena, 'IMPULSO' if pt else 'BOOST', SUAVE, 274, 168)
        pygame.draw.rect(surf, (43, 62, 78), (344, 174, 80, 5), border_radius=2)
        pygame.draw.rect(surf, CIANO, (344, 174, max(1, min(80, int(80 * nivel))), 5), border_radius=2)
