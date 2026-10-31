"""Pixel Rush v3.217.0 — corredores de moedas sincronizados a perigos existentes.

Sem sprites, timers, RNG, nova colisao ou novo gerador de obstaculos.
So prepara centros de moedas para os tres encontros autorais existentes.
"""

TIPOS = ("SALTO", "ESCOLHA", "PASSAGEM")
QUANTIDADE = {"SALTO": 6, "ESCOLHA": 4, "PASSAGEM": 2}


def calcular_rota(tipo, rect, altura_virtual, metros, bioma):
    """Retorna centros absolutos x/y; sem efeitos colaterais nem sorteios.

    Um centro de moeda so e aceito se o quadrado 24x24 do sprite
    nao intercepta o retangulo de colisao VISUAL do perigo + margem.
    A geometria nao promete que toda moeda sera coletada, apenas que
    a rota nao induzira o jogador a tocar o obstaculo para busca-la.
    """
    if tipo not in QUANTIDADE:
        raise ValueError("tipo de sequencia desconhecido")
    x0, topo, largura, altura = int(rect.x), int(rect.y), int(rect.width), int(rect.height)
    fundo = topo + altura
    base = altura_virtual - 120
    variante = (int(metros) // 240 + sum(ord(c) for c in str(bioma))) % 3

    if tipo == "SALTO":
        # A pista dos centros nao depende da sorte. O arco alto se adapta
        # ao topo REAL do perigo, nao a uma altura generica de cactus.
        alto = max(altura_virtual - 247, min(topo - 29, altura_virtual - 186))
        if topo < altura_virtual - 224:
            # Perigo muito alto: a curva permanece ANTES dele.
            xs = (-199, -164, -129, -94, -59, -24)
            ys = (base, base-15, base-33, base-47, base-33, base-15)
        elif variante == 0:  # pulo curto
            xs = (-174, -139, -104, -69, -34, 1)
            ys = (base, base-14, base-30, alto+9, alto, alto)
        elif variante == 1:  # pulo longo (com ponto de saida)
            xs = (-164, -127, -90, -45, 25, largura+42)
            ys = (base, base-17, base-38, alto+8, alto, base-35)
        else:  # arco seguido de pouso
            xs = (-184, -147, -110, -65, 19, largura+44)
            ys = (base, base-17, base-35, alto+8, alto, base-24)
    elif tipo == "ESCOLHA":
        # Inimigo elevado: trilha inferior realmente livre, sem exigir
        # saltar para a propria hitbox. As pequenas ondas guiam a altura.
        xs = ((-129, -54, 35, largura+48),
              (-152, -92, -32, largura+45),
              (-144, -72, 23, largura+51))[variante]
        ys = ((base+2, base-2, base-4, base+1),
              (base, base+3, base-3, base),
              (base-2, base, base+3, base-2))[variante]
    else:
        # Passagem baixa: pontos de aproximacao/saida; jamais moedas
        # colocadas dentro da faixa fisicamente ocupada pelo voador.
        xs = ((-143, largura+56), (-171, largura+49), (-118, largura+79))[variante]
        ys = ((base+3, base+3), (base+1, base+1), (base, base))[variante]

    moedas = []
    for dx, y in zip(xs, ys):
        cx = x0 + int(dx)
        cy = max(altura_virtual-250, min(altura_virtual-110, int(y)))
        # Margem de 12 px para borda da moeda, +8 px de tolerancia
        # contra confusao visual no contato com perigo.
        if (cx + 20 > x0 and cx - 20 < x0 + largura and
                cy + 20 > topo and cy - 20 < fundo):
            if tipo == "SALTO" and topo - 30 >= altura_virtual - 250:
                cy = min(cy, topo-30)
            else:
                # Realoca a moeda para o corredor anterior, nao apaga
                # uma recompensa nem inventa deslocamento vertical inviavel.
                cx = x0 - 27 - 35 * (len(moedas)+1)
        # Margem valida no pior caso, inclusive obstaculos enormes.
        assert not (cx+20 > x0 and cx-20 < x0+largura and
                    cy+20 > topo and cy-20 < fundo), (tipo, (cx,cy), rect)
        moedas.append((cx, cy))
    assert len(moedas) == QUANTIDADE[tipo]
    assert all(altura_virtual-250 <= y <= altura_virtual-110 for _, y in moedas)
    assert len(set(moedas)) == len(moedas)
    return tuple(sorted(moedas))


def gerar_corredor(tipo, obstaculo, altura_virtual, metros, bioma,
                   todos_sprites, moedas, pool_manager):
    """Usa exatamente o pool e grupos originais, nenhum novo RNG."""
    for x, y in calcular_rota(tipo, obstaculo.rect, altura_virtual, metros, bioma):
        sprite = pool_manager.obter_moeda(x, y)
        todos_sprites.add(sprite)
        moedas.add(sprite)
