# -*- coding: utf-8 -*-
"""Pixel Rush v3.245.0: trilhas alternativas SEGURAS dos corredores oficiais.

Mantem spawn, pool, moedas por encontro (6/4/2), hitboxes e RNG.
Tres novas trajetorias, opt-in deterministico; fora disso delega ao v3.217.
"""
from pixelrush_corredores_v3217 import gerar_corredor as _gerar_original
from pixelrush_corredores_v3217 import calcular_rota as _calcular_original
from pixelrush_corredores_v3217 import QUANTIDADE


def calcular_rota(tipo, rect, altura_virtual, metros, bioma):
    if tipo not in QUANTIDADE:
        raise ValueError('tipo de sequencia desconhecido')
    fase = (int(metros)//320 + sum(map(ord,str(bioma)))) % 4
    if fase != 0:
        return _calcular_original(tipo,rect,altura_virtual,metros,bioma)
    x, topo, largura, fundo = int(rect.x), int(rect.y), int(rect.width), int(rect.bottom)
    base = int(altura_virtual)-120
    # Trilhos de aproximacao ou de passagem, todos com >=20px de folga.
    if tipo == 'SALTO':
        xs = (-240,-205,-170,-135,-100,-65)
        ys = (base,base-12,base-26,base-41,base-56,base-70)
    elif tipo == 'ESCOLHA':
        xs = (-195,-152,-109,-66)
        ys = (base,base-3,base+2,base)
    else:  # PASSAGEM - pontos antes e depois do voador.
        xs = (-110,largura+110)
        ys = (base,base)
    saida = tuple(sorted((x+dx,y) for dx,y in zip(xs,ys)))
    assert len(saida) == QUANTIDADE[tipo]
    assert all(altura_virtual-250 <= y <= altura_virtual-110 for cx,y in saida)
    assert all(not (cx+20>x and cx-20<x+largura and cy+20>topo and cy-20<fundo)
               for cx,cy in saida)
    return saida


def gerar_corredor(tipo, obstaculo, altura_virtual, metros, bioma,
                   todos_sprites, moedas, pool_manager):
    # Sem nova geracao se o modulo antigo ja define a trilha escolhida.
    fase=(int(metros)//320 + sum(map(ord,str(bioma))))%4
    if fase != 0:
        return _gerar_original(tipo, obstaculo, altura_virtual, metros, bioma,
                               todos_sprites, moedas, pool_manager)
    for x,y in calcular_rota(tipo,obstaculo.rect,altura_virtual,metros,bioma):
        sprite = pool_manager.obter_moeda(x,y)
        todos_sprites.add(sprite)
        moedas.add(sprite)
