"""Pixel Rush v3.210.0 — acessibilidade visual opcional.

Desenho puramente visual: nao altera colisoes, tempos ou entrada.
Todas as opcoes desligadas reproduzem exatamente o comportamento v3.209.0.
Sem texturas externas, filtros por pixel ou alocacoes de superficies por frame.
"""
import pygame

OPCOES = (
    ('acess_contraste', 'CONTRASTE DOS PERIGOS', 'HAZARD CONTRAST'),
    ('acess_sinais', 'SINAIS SEM DEPENDER DE COR', 'COLOR-INDEPENDENT SIGNS'),
    ('acess_reduzir_efeitos', 'REDUZIR FLASHES / CAMERA', 'REDUCE FLASHES / CAMERA'),
)

def opcoes_ativas(dados):
    return tuple(bool(dados.get(k, False)) for k, _, _ in OPCOES)


def desenhar_painel(superficie, dados, fontes, retangulos):
    """Tela estatica de configuracao com botoes grandes (450x800 virtual)."""
    fonte, pequena, titulo = fontes
    ingles = dados.get('idioma') == 'en_US'
    superficie.fill((11, 21, 36))
    pygame.draw.rect(superficie, (23, 38, 58), (25, 98, 400, 645), border_radius=16)
    pygame.draw.rect(superficie, (119, 206, 235), (25, 98, 400, 645), 2, border_radius=16)
    cabecalho = 'ACCESSIBILITY' if ingles else 'ACESSIBILIDADE'
    surf = titulo.render(cabecalho, True, (253, 230, 150))
    superficie.blit(surf, (225 - surf.get_width() // 2, 43))
    texto = ('Optional visual aids. No gameplay changes.' if ingles
             else 'Recursos visuais opcionais. Mesma jogabilidade.')
    surf = pequena.render(texto, True, (215, 231, 245))
    superficie.blit(surf, (225 - surf.get_width() // 2, 133))
    for chave, pt, en in OPCOES:
        r = retangulos[chave]
        ativo = bool(dados.get(chave, False))
        pygame.draw.rect(superficie, (39, 77, 93) if ativo else (45, 54, 75), r, border_radius=12)
        pygame.draw.rect(superficie, (176, 248, 208) if ativo else (195, 210, 228), r, 2, border_radius=12)
        texto = en if ingles else pt
        surf = pequena.render(texto, True, (255, 255, 255))
        superficie.blit(surf, (r.x + 13, r.y + 10))
        rotulo = 'ON' if ativo else 'OFF' if ingles else 'DESLIGADO'
        if ativo and not ingles: rotulo = 'LIGADO'
        estado = pequena.render(rotulo, True, (242, 255, 227) if ativo else (214, 223, 234))
        superficie.blit(estado, (r.right - estado.get_width() - 16, r.y + 36))
    infos = (('Destaque sem modificar hitboxes.' if not ingles else 'Outlines do not change hitboxes.'),
             ('Sinais: solo / voador / buraco.' if not ingles else 'Signs: ground / flying / gaps.'),
             ('Sem flashes fortes e movimentos de camera.' if not ingles else 'No strong flashes or camera movement.'))
    for n, texto in enumerate(infos):
        surf = pequena.render(texto, True, (184, 209, 223))
        superficie.blit(surf, (225 - surf.get_width() // 2, 492 + 29*n))
    r = retangulos['voltar']
    pygame.draw.rect(superficie, (43, 141, 104), r, border_radius=11)
    pygame.draw.rect(superficie, (245, 255, 244), r, 2, border_radius=11)
    surf = fonte.render('SAVE AND BACK' if ingles else 'SALVAR E VOLTAR', True, (255,255,255))
    superficie.blit(surf, surf.get_rect(center=r.center))


def desenhar_sinais(superficie, jogador, obstaculos, buracos, dados, modo_leve=False):
    """Avisos vetoriais em torno das artes; nao sao areas fisicas de colisao.

    Nenhum bitmap ou surface adicional. A marcacao e uma ajuda visual,
    nao uma representacao exata da hitbox.
    """
    contraste, sinais, _ = opcoes_ativas(dados)
    if not (contraste or sinais) or jogador is None or jogador.morrendo:
        return 0
    inicio = jogador.rect.right
    limite = 2 if modo_leve else 4
    desenhados = 0
    for obs in obstaculos:
        r = obs.rect
        if r.right < inicio or r.left > min(449, inicio + 300) or r.bottom < 190:
            continue
        if contraste:
            moldura = r.inflate(6, 6).clip(superficie.get_rect())
            if moldura.width > 3 and moldura.height > 3:
                pygame.draw.rect(superficie, (9, 16, 29), moldura, 3, border_radius=3)
                pygame.draw.rect(superficie, (255, 246, 193), moldura, 1, border_radius=3)
        if sinais:
            voador = bool(getattr(obs, 'movimento', '') in ('voar', 'voando', 'voador')) or (
                obs.__class__.__name__ == 'ObstaculoVoador')
            # Forma + letra evitam dependencia exclusiva da cor.
            x = max(15, min(435, int(r.centerx)))
            y = max(196, min(680, int(r.top - 19)))
            if voador:
                pygame.draw.circle(superficie, (12, 18, 32), (x, y), 11)
                pygame.draw.circle(superficie, (250, 248, 238), (x, y), 9, 2)
                pygame.draw.line(superficie, (255, 255, 255), (x-4,y-3),(x,y+4),2)
                pygame.draw.line(superficie, (255, 255, 255), (x,y+4),(x+4,y-3),2)
            else:
                pygame.draw.polygon(superficie, (8, 17, 33), ((x,y-12),(x-12,y+10),(x+12,y+10)))
                pygame.draw.polygon(superficie, (255, 249, 223), ((x,y-11),(x-11,y+9),(x+11,y+9)),2)
                pygame.draw.line(superficie, (255,255,255), (x,y-5),(x,y+3), 2)
                pygame.draw.circle(superficie, (255,255,255), (x,y+6), 1)
        desenhados += 1
        if desenhados >= limite: break
    if (contraste or sinais) and desenhados < limite:
        for buraco in buracos:
            r = buraco.rect
            if r.right < inicio or r.left > min(449, inicio + 300): continue
            x = max(18, min(432, r.centerx))
            y = max(215, min(650, r.y - 22))
            if contraste:
                pygame.draw.line(superficie,(255,252,216),(max(0,r.left),r.top),(min(449,r.right),r.top),3)
            if sinais:
                pygame.draw.rect(superficie,(10,19,32),(x-15,y-10,30,20),border_radius=3)
                pygame.draw.rect(superficie,(255,252,233),(x-15,y-10,30,20),2,border_radius=3)
                pygame.draw.line(superficie,(255,252,233),(x-6,y-5),(x-6,y+5),2)
                pygame.draw.line(superficie,(255,252,233),(x+6,y-5),(x+6,y+5),2)
            desenhados += 1
            if desenhados>=limite: break
    return desenhados
