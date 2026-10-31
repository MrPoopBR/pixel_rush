"""Pixel Rush v3.188.0 — continuidade expressiva das nove skins.

Complementa o atlas que a v3.176.0 ja gerou: nunca recria membros,
nao altera alfa, dimensoes, hitboxes, estados ou ticks da fisica.
Somente dois estados de dois ticks (CORRER/AGACHAR) recebem transicao
cromatica interna opcional. No modo leve usa so quadros-chave.
"""
from collections import OrderedDict
import pygame

# Paletas de materiais ja usados pelos sprites. A luz permanece dentro da arte.
_ACENTOS = {
    'AZUL': (105, 210, 255), 'VERDE': (178, 237, 117),
    'ROSA': (255, 183, 228), 'DOURADO': (255, 228, 103),
    'ROXO': (181, 139, 254), 'ROBO': (120, 231, 255),
    'CHAMA': (255, 189, 84), 'COSMICA': (206, 178, 255),
    'PLATINA': (174, 231, 255),
}
_ESTADOS_ATIVOS = frozenset(('CORRER', 'IMPULSO', 'SUBINDO',
    'PULAR', 'CAINDO', 'AGACHAR', 'SWIPE_DOWN', 'POUSO'))
_INTERPOLAVEIS = frozenset(('CORRER', 'AGACHAR'))
_MEIO_QUADROS = OrderedDict()
_LIMITE_MEIOS = 60    # Aprox. 1,5 MiB em RGBA a 80x80.


def _no_interior(imagem, x, y):
    """Nao tocar no contorno ou nas bordas semi-transparentes."""
    return (imagem.get_at((x, y)).a == 255 and
            imagem.get_at((x-1, y)).a == 255 and
            imagem.get_at((x+1, y)).a == 255 and
            imagem.get_at((x, y-1)).a == 255 and
            imagem.get_at((x, y+1)).a == 255)


def _acentuar_estado(quadro, skin, estado, indice, quantidade):
    """Micro-reflexos no traje e nas botas, acompanhando as poses existentes."""
    if estado not in _ESTADOS_ATIVOS:
        return
    w, h = quadro.get_size()
    if (w, h) != (80, 80):
        return
    alvo = _ACENTOS[skin]
    # Oscilacao artistica deterministica por pose, sem RNG e sem fisica.
    fase = indice % max(1, quantidade)
    direcao = (-1, 0, 1, 0)[fase % 4]
    # Blocos curtos de luz que seguem as dobras do peito, bracos e botas.
    areas = ((28 + direcao, 47, 4, 3),
             (49 - direcao, 55, 4, 3),
             (31 - direcao, 67, 4, 3),
             (47 + direcao, 68, 4, 3))
    if estado in ('SUBINDO', 'IMPULSO', 'PULAR'):
        areas = ((31 + direcao, 46, 4, 3),
                 (47 - direcao, 54, 4, 3),
                 (32 + direcao, 63, 4, 3))
    if estado in ('AGACHAR', 'SWIPE_DOWN'):
        areas = ((29 + direcao, 54, 4, 3),
                 (46 - direcao, 61, 4, 3),
                 (34, 69, 4, 3))
    if estado == 'POUSO':
        areas = ((30 + direcao, 59, 5, 3), (45 - direcao, 66, 5, 3))
    if estado == 'CAINDO':
        areas = ((28 + direcao, 48, 4, 3), (51 - direcao, 58, 3, 4))
    for ax, ay, aw, ah in areas:
        for y in range(ay, ay+ah):
            for x in range(ax, ax+aw):
                if not (2 <= x < w-2 and 2 <= y < h-2):
                    continue
                if not _no_interior(quadro, x, y):
                    continue
                r, g, b, a = quadro.get_at((x, y))
                # Somente pixels opacos de materiais; nunca acrescenta corpo,
                # halo ou pixel fora da silhueta aprovada.
                peso = 0.10 if (x+y+fase) % 3 else 0.16
                cor = tuple(int(round(c*(1-peso)+k*peso)) for c,k in zip((r,g,b),alvo))
                quadro.set_at((x,y), (*cor,a))


def refinar_atlas(atlas, skin):
    """Usa superfícies RECeM-geradas pela v3176; nenhuma copia extra do atlas."""
    if skin not in _ACENTOS:
        return atlas
    for estado, quadros in atlas.items():
        for i, quadro in enumerate(quadros):
            _acentuar_estado(quadro, skin, estado, i, len(quadros))
    return atlas


def _meio_quadro(atlas, skin, estado, indice):
    """Transicao discreta dentro da AREA COMUM opaca, sem alterar contorno."""
    key = (skin, estado, indice)
    entry = _MEIO_QUADROS.get(key)
    atual = atlas[estado][indice]
    if entry is not None and entry[0] is atual:
        _MEIO_QUADROS.move_to_end(key)
        return entry[1]
    proximo = atlas[estado][(indice+1) % len(atlas[estado])]
    saida = atual.copy()
    # Calculado uma vez para cada par de poses; sem transform por frame.
    for y in range(36, 75):
        for x in range(21, 60):
            if not _no_interior(atual,x,y) or proximo.get_at((x,y)).a != 255:
                continue
            ar,ag,ab,aa = atual.get_at((x,y))
            br,bg,bb,_ = proximo.get_at((x,y))
            # Evita interpolar entre olho, acessorio e partes incompatíveis.
            if max(abs(ar-br),abs(ag-bg),abs(ab-bb)) > 65:
                continue
            rgb = (int(ar*.68+br*.32+.5), int(ag*.68+bg*.32+.5), int(ab*.68+bb*.32+.5))
            if rgb != (ar,ag,ab):
                saida.set_at((x,y), (*rgb,aa))
    _MEIO_QUADROS[key] = (atual, saida)
    if len(_MEIO_QUADROS) > _LIMITE_MEIOS:
        _MEIO_QUADROS.popitem(last=False)
    return saida


def escolher_quadro(atlas, skin, estado, indice, tick, modo_leve=False):
    """Mantem o keyframe do motor e apenas intercala RGB no segundo tick."""
    atual = atlas[estado][indice]
    if (modo_leve or estado not in _INTERPOLAVEIS or tick % 2 == 0
            or len(atlas[estado]) < 2):
        return atual
    return _meio_quadro(atlas, skin, estado, indice)


def limpar_cache():
    _MEIO_QUADROS.clear()
