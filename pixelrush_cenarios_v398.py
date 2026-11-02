"""Pixel Rush 3.98: cenarios mais vivos, menos poluidos e com parallax mais profundo.

Modulo visual focado em desempenho para Pygame-ce/Pygame.
As artes aprovadas continuam sendo a base principal, enquanto elementos animados
leves (primitivos pixel-art) adicionam vida ao mundo sem roubar foco da pista.
"""
import math
import pygame

W, H = 450, 800
PANORAMA_W = 2700
PANORAMA_H = 500
PANORAMA_Y = 230

_TONS_BIOMA = {
    'cidade': (135, 177, 224),
    'neve': (116, 121, 196),
    'deserto': (194, 186, 191),
    'vulcao': (181, 97, 126),
    'floresta': (49, 117, 117),
    'cidade_futurista': (149, 109, 179),
    'ilhas_celestes': (142, 159, 199),
    'reino_submerso': (77, 163, 200),
}


def mistura(a, b, t):
    t = max(0., min(1., float(t)))
    return tuple(max(0, min(255, int(a[i] * (1 - t) + b[i] * t))) for i in range(3))


def _loop_x(x, scroll, periodo=PANORAMA_W):
    return int((x - scroll) % periodo)


def _orbit_tempo(tempo, fator):
    return tempo * fator


def _sinal_suave(tempo, fase=0.0, escala=1.0):
    return math.sin(tempo * escala + fase)


def _desenhar_reflexo_pixel(surf, x, y, largura, altura, cor1, cor2):
    for i in range(0, largura, 3):
        cor = cor1 if (i // 3) % 2 == 0 else cor2
        pygame.draw.rect(surf, cor, (x + i, y + (i % 2), 2, altura))


def nuvem_pixel(surface, x, y, escala, cor, sombra, luz):
    """Silhueta pixelada com tres planos, compartilhada com chuva/neve."""
    s = max(1, int(escala)); x = int(x); y = int(y)
    blocos = ((0, 14, 58, 11), (7, 8, 48, 12), (14, 3, 28, 12),
              (20, 0, 16, 11), (35, 7, 25, 14), (48, 13, 17, 8))
    for dx,dy,w,h in blocos:
        pygame.draw.rect(surface, sombra, (x+(dx+1)*s, y+(dy+3)*s, w*s, h*s))
    for dx,dy,w,h in blocos:
        pygame.draw.rect(surface, cor, (x+dx*s, y+dy*s, w*s, h*s))
    for dx,dy,w,h in ((20,2,14,3),(14,8,19,3),(37,9,13,3),(7,16,12,2)):
        pygame.draw.rect(surface, luz, (x+dx*s, y+dy*s, w*s, h*s))


def desenhar_ceu(surf, cor_base, fase, noite, bioma, estrelas, tempo, nuvens):
    """Gradiente vertical em faixas pixel-art; usa o sol/lua real do jogo."""
    tema = _TONS_BIOMA.get(bioma, _TONS_BIOMA['cidade'])
    ceu = mistura(cor_base, tema, 0.26)
    alba = max(0., 1. - abs(fase - .15) / .105)
    tarde = max(0., 1. - abs(fase - .745) / .10)
    crepusculo = max(alba, tarde)
    # v3.227.0: componentes constantes no mesmo quadro nao precisam ser
    # recalculados nas 40 faixas. Nenhuma quantizacao ou cache entre quadros.
    cor_topo = mistura((11, 24, 56), ceu, .82)
    cor_base_arte = mistura(ceu, tema, .74)
    for faixa in range(0, H, 20):
        ymedio = min(1.0, (faixa + 10) / 280.0)
        cor = mistura(cor_topo, cor_base_arte, ymedio)
        if crepusculo:
            rosa = mistura((149, 95, 172), (255, 175, 110), ymedio)
            cor = mistura(cor, rosa, crepusculo * (.13 + .42 * ymedio))
        if noite > .1:
            cor = mistura(cor, (16, 20, 53), noite * (0.47 - 0.16 * ymedio))
        pygame.draw.rect(surf, cor, (0, faixa, W, min(20, H-faixa)))

    if noite > .04:
        for i, estrela in enumerate(estrelas):
            x, y = int(estrela['x']), int(estrela['y'])
            if y > 310:
                continue
            cintilar = .5 + .5 * math.sin(tempo * estrela['blink'] + estrela['offset'])
            if cintilar * noite < .2:
                continue
            c = mistura((77, 102, 156), (246, 245, 230), cintilar * noite)
            pygame.draw.rect(surf, c, (x, y, 1 + (i % 11 == 0), 1 + (i % 11 == 0)))
            if i % 13 == 0 and cintilar * noite > .70:
                pygame.draw.line(surf, c, (x-2, y), (x+2, y))
                pygame.draw.line(surf, c, (x, y-2), (x, y+2))

    if .10 <= fase <= .81:
        t = (fase-.10)/.71
        x = int(-20 + t * (W+40))
        y = int(242 - 157*math.sin(math.pi*t))
        lua = False
    elif fase >= .83 or fase <= .08:
        t = ((fase-.83) % 1.) / .25
        x = int(-30 + t*(W+60))
        y = int(208 - 112*math.sin(math.pi*min(1., t)))
        lua = True
    else:
        x = -100; y = -100; lua = False
    if -16 < x < W+16 and y > -16:
        if lua:
            pygame.draw.circle(surf, mistura(ceu, (158, 184, 234), .54), (x,y), 20)
            pygame.draw.circle(surf, (244, 244, 222), (x,y), 13)
            pygame.draw.circle(surf, mistura((26,36,76),ceu,.25), (x+5,y-5), 11)
        else:
            halo = mistura(ceu, (255, 201, 107), .45)
            pygame.draw.circle(surf, halo, (x,y), 28)
            pygame.draw.circle(surf, (255, 219, 142), (x,y), 17)
            pygame.draw.circle(surf, (255, 245, 190), (x-3,y-4), 12)
            for dx,dy in ((-33,0),(33,0),(0,-33),(0,33)):
                pygame.draw.rect(surf, (248, 210, 135), (x+dx-2,y+dy-2,4,4))

    # Mesmas tintas para todas as nuvens do quadro (antes: 6 recomputacoes).
    base = mistura(ceu, (232,242,249) if noite < .3 else (108,127,162), .67)
    sombra = mistura(base, (69,90,137), .34)
    brilho = mistura(base, (255,251,239), .38)
    sombra_escura = mistura(sombra, (41,59,100), .2)
    for i, n in enumerate(nuvens):
        x = int(n['x']); y = int(n['y']); escala = 1
        if (i % 2) == 0:
            nuvem_pixel(surf, x, y, escala, base, sombra, brilho)
        else:
            nuvem_pixel(surf, x, y + 18, escala, sombra, sombra_escura, base)


def desenhar_panorama(surf, panorama, scroll, y=PANORAMA_Y):
    """Blit unico por secao; jamais desenhar tiles antigos por cima ou cortar y."""
    comprimento = panorama.get_width()
    offset = int(scroll) % comprimento
    p = 0
    operacoes = []
    while p < W:
        n = min(W-p, comprimento-offset)
        operacoes.append((panorama, (p,y),
                         (offset,0,n,panorama.get_height())))
        p += n
        offset = 0
    # Mesmos recortes e sobreposicoes; Surface.blits agrupa chamadas em C.
    if operacoes:
        surf.blits(operacoes, doreturn=False)


def desenhar_emenda_panorama(surf, cor_ceu, bioma, noite, y=PANORAMA_Y):
    """Suaviza a junção do céu com a arte para evitar o efeito de recorte."""
    paleta = {
        'vulcao': (224, 150, 109),
        'floresta': (168, 199, 151),
        'cidade_futurista': (174, 196, 239),
        'ilhas_celestes': (184, 226, 229),
        'deserto': (221, 195, 162),
        'neve': (203, 223, 239),
        'cidade': (191, 209, 226),
    }
    alvo = paleta.get(bioma, (196, 210, 226))
    for idx, altura in enumerate((6, 8, 10, 12, 14, 16)):
        peso = 0.18 + idx * 0.08 + noite * 0.04
        cor = mistura(cor_ceu, alvo, min(0.82, peso))
        pygame.draw.rect(surf, cor, (0, y - 2 + idx * 4, W, altura))
    # A cor das marcas de emenda e independente da posicao horizontal.
    cor_marca = mistura(alvo, (255, 255, 255), 0.12 + noite * 0.08)
    for i in range(0, W, 18):
        ond = int(math.sin((i * 0.07) + y * 0.01) * 2)
        pygame.draw.line(surf, cor_marca,
                         (i, y + 4 + ond), (i + 10, y + 4 + ond), 1)


def desenhar_foco_pista(surf, bioma, noite):
    """Haze minimo proximo ao chao para manter foco sem criar barras visiveis."""
    alvo = {
        'vulcao': (187, 135, 112),
        'floresta': (166, 188, 152),
        'cidade_futurista': (170, 182, 214),
        'ilhas_celestes': (184, 205, 212),
        'deserto': (194, 182, 164),
    }.get(bioma, (176, 184, 194))
    cor = mistura((116, 132, 152), alvo, 0.08 + noite * 0.03)
    pygame.draw.line(surf, cor, (0, 610), (W, 610), 1)
    pygame.draw.line(surf, cor, (0, 640), (W, 640), 1)


def desenhar_animacoes_fundo(surf, bioma, tempo, scroll_fundo, scroll_panorama, fase, noite):
    """Elementos vivos desenhados atras ou acima do panorama principal."""
    t = _orbit_tempo(tempo, 1.0)
    if bioma == 'vulcao':
        # Fumaca do vulcao ao fundo, lenta e barata, com dois planos.
        for idx, (base_x, base_y) in enumerate(((410, 340), (1380, 326), (2220, 350), (3020, 335))):
            x = _loop_x(base_x, scroll_fundo * 0.70)
            osc = _sinal_suave(t, idx * 0.9, 0.035)
            for puff in range(5):
                py = base_y - puff * 16 - int((tempo * 0.28 + idx * 9 + puff * 3) % 22)
                px = x + int(osc * (5 + puff * 2)) + puff * 3
                raio = 8 + puff * 4
                cor = mistura((82, 78, 88), (153, 147, 159), 0.24 + puff * 0.15)
                pygame.draw.circle(surf, cor, (px, py), raio)
                if puff >= 2:
                    pygame.draw.circle(surf, mistura(cor, (235, 220, 208), 0.28), (px + 4, py - 3), max(3, raio // 2))
        for i in range(4):
            x = int((i * 120 - scroll_fundo * 0.35) % (W + 130)) - 30
            yy = 388 + (i % 2) * 17
            pygame.draw.line(surf, (221, 169, 112), (x, yy), (x + 34, yy - 1), 1)
    elif bioma == 'cidade_futurista':
        # Faixas de transito aereo ao fundo com mais rotas e hovercars.
        for seed, y, vel, cor_a, cor_b in (
            (260, 310, 0.95, (113, 244, 255), (255, 124, 241)),
            (820, 345, 0.72, (127, 235, 255), (171, 121, 255)),
            (1580, 290, 1.08, (84, 224, 248), (233, 182, 255)),
            (2320, 370, 0.64, (106, 211, 255), (219, 120, 255)),
            (3180, 332, 0.84, (93, 242, 235), (255, 163, 230)),
        ):
            wx = (seed - tempo * vel - scroll_fundo * 0.85) % 5400.0
            if wx > W + 40:
                wx -= 5400.0
            if -50 < wx < W + 30:
                x = int(wx)
                dy = int(_sinal_suave(t, seed * 0.01, 0.055) * 4)
                pygame.draw.rect(surf, cor_b, (x - 11, y + dy + 4, 24, 2))
                pygame.draw.rect(surf, cor_a, (x, y + dy, 16, 6), border_radius=2)
                pygame.draw.rect(surf, (242, 251, 255), (x + 2, y + dy + 1, 4, 2))
                pygame.draw.rect(surf, cor_b, (x - 18, y + dy + 2, 10, 2))
                pygame.draw.rect(surf, cor_a, (x + 18, y + dy + 2, 9, 2))
    elif bioma == 'ilhas_celestes':
        # Pequenas ilhas adicionais bem discretas para alongar a variacao.
        for seed, y, vel in ((210, 322, 0.20), (1110, 356, 0.14), (3010, 328, 0.17), (4730, 375, 0.12), (5510, 338, 0.16)):
            wx = (seed - scroll_fundo * 0.48 - tempo * vel) % 6200.0
            if wx > W + 70:
                wx -= 6200.0
            if -80 < wx < W + 50:
                x = int(wx)
                dy = int(_sinal_suave(t, seed * 0.01, 0.028) * 5)
                pygame.draw.ellipse(surf, (118, 177, 214), (x, y + dy, 56, 11))
                pygame.draw.polygon(surf, (72, 124, 173), ((x + 8, y + dy + 9), (x + 28, y + dy + 33), (x + 50, y + dy + 9)))
                pygame.draw.polygon(surf, (184, 235, 222), ((x + 12, y + dy + 7), (x + 24, y + dy + 4), (x + 38, y + dy + 7)))
                pygame.draw.line(surf, (189, 241, 255), (x + 27, y + dy + 15), (x + 27, y + dy + 38), 2)
                pygame.draw.line(surf, (223, 249, 255), (x + 28, y + dy + 18), (x + 28, y + dy + 34), 1)
    elif bioma == 'floresta':
        # Camada de folhas altas balancando ao fundo.
        for seed, x0 in enumerate((35, 132, 256, 372)):
            sway = int(_sinal_suave(t, seed * 0.8, 0.05) * 5)
            pygame.draw.line(surf, (43, 104, 84), (x0, 230), (x0 + sway, 285), 3)
            pygame.draw.ellipse(surf, (76, 162, 114), (x0 - 12 + sway, 246, 36, 18))
            pygame.draw.ellipse(surf, (152, 216, 142), (x0 - 7 + sway, 250, 18, 8))
    elif bioma == 'deserto':
        # Distorcao termica / areia distante.
        for i in range(7):
            x = int((i * 88 - scroll_fundo * 0.45) % (W + 50)) - 20
            y = 395 + (i % 3) * 18
            largura = 24 + (i % 3) * 14
            pygame.draw.line(surf, (220, 195, 152), (x, y), (x + largura, y - (i % 2)), 1)
    elif bioma in ('cidade', 'neve'):
        # Pequeno transporte ao fundo para ajudar no looping e dar vida.
        base_y = 455 if bioma == 'cidade' else 468
        cor = (175, 205, 224) if bioma == 'cidade' else (224, 240, 249)
        detalhe = (98, 134, 168) if bioma == 'cidade' else (146, 171, 196)
        wx = (620 - scroll_fundo * 0.95 - tempo * 0.65) % 3600.0
        if wx > W + 90:
            wx -= 3600.0
        if -120 < wx < W + 30:
            x = int(wx)
            pygame.draw.rect(surf, cor, (x, base_y, 92, 14), border_radius=4)
            pygame.draw.rect(surf, detalhe, (x + 5, base_y + 3, 15, 5))
            pygame.draw.rect(surf, detalhe, (x + 26, base_y + 3, 15, 5))
            pygame.draw.rect(surf, detalhe, (x + 47, base_y + 3, 15, 5))


def desenhar_animacoes_frente(surf, bioma, tempo, scroll_fundo, scroll_panorama, fase, noite):
    """Elementos desenhados na frente da pintura principal, ainda atras da pista."""
    t = _orbit_tempo(tempo, 1.0)
    if bioma == 'vulcao':
        # Rios de lava pulsando.
        brilho_noite = 0.35 + noite * 0.35
        for idx, lx in enumerate((210, 1180, 1700, 2460)):
            x = _loop_x(lx, scroll_panorama)
            base_y = 480 + (idx % 2) * 24
            for seg in range(4):
                yy = base_y + seg * 18
                dx = int(_sinal_suave(t, idx * 1.2 + seg, 0.09) * 4)
                pygame.draw.rect(surf, mistura((140, 54, 34), (246, 121, 62), brilho_noite), (x + dx, yy, 6, 18))
                pygame.draw.rect(surf, (255, 204, 118), (x + dx + 1, yy + 4, 2, 8))
                pygame.draw.rect(surf, (255, 236, 165), (x + dx + 3, yy + 7, 1, 4))
    elif bioma == 'floresta':
        # Copas e vinhas oscilando + brilho d'agua.
        for idx, lx in enumerate((90, 188, 305, 404)):
            sway = int(_sinal_suave(t, idx * 0.7, 0.055) * 6)
            pygame.draw.line(surf, (57, 123, 82), (lx, 448), (lx + sway, 520), 4)
            pygame.draw.ellipse(surf, (87, 178, 112), (lx - 18 + sway, 440, 44, 26))
            pygame.draw.ellipse(surf, (161, 222, 130), (lx - 8 + sway, 447, 18, 8))
            pygame.draw.line(surf, (44, 118, 74), (lx + 10, 438), (lx + 14 + sway, 470), 2)
        for lx in (1340, 2230, 3150):
            x = _loop_x(lx, scroll_panorama)
            onda = int(_sinal_suave(t, lx * 0.01, 0.09) * 2)
            for j in range(6):
                yy = 386 + j * 22
                pygame.draw.line(surf, (123, 211, 222), (x + onda, yy), (x + 7 + onda, yy + 18), 2)
                pygame.draw.line(surf, (213, 248, 252), (x + 3 + onda, yy + 4), (x + 4 + onda, yy + 15), 1)
    elif bioma == 'cidade_futurista':
        # Faixas neon discretas e holofotes das torres. A noite fica mais viva.
        intensidade = 0.35 + noite * 0.55
        for lx in (210, 620, 990, 1540, 1880, 2390):
            x = _loop_x(lx, scroll_panorama)
            cor = mistura((74, 202, 241), (225, 126, 255), (lx % 7) / 7.0)
            pygame.draw.rect(surf, cor, (x, 450 + (lx % 3) * 18, 2, 42))
            if noite > 0.08:
                pygame.draw.rect(surf, mistura(cor, (255, 255, 255), intensidade), (x - 1, 451 + (lx % 3) * 18, 4, 2))
    elif bioma == 'ilhas_celestes':
        # Cachoeiras celestiais e bioluminescencia estilo Avatar.
        brilho = 0.28 + noite * 0.50
        for lx in (420, 1080, 1770, 2450):
            x = _loop_x(lx, scroll_panorama)
            osc = int(_sinal_suave(t, lx * 0.005, 0.06) * 2)
            for seg in range(6):
                yy = 364 + seg * 26
                pygame.draw.line(surf, mistura((116, 214, 236), (225, 247, 255), brilho), (x + osc, yy), (x + osc + 3, yy + 21), 2)
                pygame.draw.line(surf, (238, 252, 255), (x + osc + 1, yy + 5), (x + osc + 1, yy + 14), 1)
        if noite > 0.08:
            for lx, ly in ((100, 465), (170, 490), (280, 458), (346, 488)):
                pulso = 0.35 + 0.65 * (0.5 + 0.5 * _sinal_suave(t, lx * 0.05, 0.09))
                cor = mistura((92, 193, 154), (198, 248, 214), pulso)
                pygame.draw.circle(surf, cor, (lx, ly), 3)
                pygame.draw.circle(surf, (235, 255, 247), (lx, ly), 1)
    elif bioma in ('cidade', 'neve'):
        # Luzes de janelas e postes reagindo ao ciclo.
        intensidade = max(0.0, noite)
        if intensidade > 0.06:
            tons = (255, 218, 128) if bioma == 'cidade' else (255, 233, 172)
            for lx, ly, w, h in ((40, 455, 4, 8), (84, 430, 5, 9), (176, 444, 4, 8), (238, 422, 5, 10), (318, 448, 4, 8), (392, 430, 5, 9)):
                cor = mistura((164, 184, 196), tons, intensidade)
                pygame.draw.rect(surf, cor, (lx, ly, w, h))
            for px in (64, 219, 366):
                pygame.draw.rect(surf, (88, 96, 120), (px, 470, 3, 38))
                pygame.draw.circle(surf, mistura((170, 182, 202), tons, intensidade), (px + 1, 469), 4)
    elif bioma == 'deserto':
        # Ventos de areia e palmeiras bem discretas ao longe.
        for seed, base_y in ((120, 480), (290, 510), (410, 458)):
            osc = int(_sinal_suave(t, seed * 0.08, 0.08) * 3)
            pygame.draw.line(surf, (121, 103, 75), (seed, base_y), (seed + osc, base_y - 30), 3)
            for dx in (-10, -4, 2, 8):
                pygame.draw.line(surf, (92, 141, 87), (seed + osc, base_y - 28), (seed + osc + dx, base_y - 38 + abs(dx)//3), 2)


def desenhar_reacao_noturna(surf, bioma, noite, tempo, scroll_panorama):
    """Destaca reacoes do mundo ao ciclo de dia/noite sem poluir a leitura."""
    if noite <= 0.04:
        return
    if bioma in ('cidade', 'neve'):
        # Janela por janela em ciclo lento, sem precisar editar a arte base.
        for idx, (lx, ly) in enumerate(((24, 448), (60, 432), (108, 466), (153, 441), (205, 455), (272, 432), (338, 462), (401, 448))):
            brilho = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(tempo * 0.05 + idx))
            cor = mistura((84, 97, 120), (255, 222, 142), brilho * noite)
            pygame.draw.rect(surf, cor, (lx, ly, 5, 8))
    elif bioma == 'cidade_futurista':
        for idx, lx in enumerate((30, 84, 135, 198, 268, 332, 404)):
            brilho = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(tempo * 0.07 + idx * 0.6))
            cor = mistura((88, 218, 239), (241, 132, 255), brilho)
            pygame.draw.rect(surf, cor, (lx, 430 + (idx % 3) * 11, 8, 2))
    elif bioma == 'ilhas_celestes':
        for idx, (lx, ly) in enumerate(((70, 420), (138, 462), (188, 403), (260, 438), (332, 410), (389, 455))):
            pulso = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(tempo * 0.09 + idx))
            cor = mistura((96, 204, 170), (220, 255, 233), pulso)
            pygame.draw.circle(surf, cor, (lx, ly), 3)
            pygame.draw.circle(surf, (245, 255, 250), (lx, ly), 1)
    elif bioma == 'vulcao':
        for lx in (125, 238, 364):
            pygame.draw.rect(surf, mistura((161, 74, 51), (255, 180, 96), noite), (lx, 492, 18, 3))


def desenhar_acabamento_proximo(surf, bioma, distancia, noite=0.0):
    """Microdetalhes discretos abaixo da faixa de colisao, camada proxima."""
    paletas = {
        'cidade': ((102,151,135),(193,213,163)),
        'neve': ((187,218,235),(244,248,252)),
        'deserto': ((188,139,91),(236,203,135)),
        'vulcao': ((128,70,64),(232,122,69)),
        'floresta': ((60,113,78),(140,194,102)),
        'cidade_futurista': ((51,101,142),(99,226,236)),
        'ilhas_celestes': ((103,157,171),(180,233,196)),
    }
    c1,c2 = paletas.get(bioma, ((108,161,151),(192,223,197)))
    base = int(distancia*.65)
    for i in range(12):
        x = (i*121 - base) % (W+90) - 25
        y = 715 + (i%3)*4
        pygame.draw.rect(surf, c1 if i%3 else c2, (x,y,2+i%3,1))
    if bioma == 'cidade_futurista' and noite > 0.05:
        for i in range(9):
            x = int((i * 57 - base * 1.2) % (W + 40)) - 10
            pygame.draw.rect(surf, (107, 226, 238), (x, 720 + (i % 2), 6, 1))
    elif bioma == 'vulcao':
        for i in range(5):
            x = int((i * 93 - base) % (W + 30))
            pygame.draw.rect(surf, (235, 125, 67), (x, 717 + (i % 2) * 2, 4, 1))
