"""Plano G v3.200.0: gravura de materiais nos tiles FAR/MID existentes.

Sem novas entidades ou geometria jogavel; a pixel-art original e o alfa sao
preservados. Os acentos de material sao pre-renderizados uma unica vez por
superficie e armazenados num LRU limitado. Nunca processar pixels no loop.
"""
from collections import OrderedDict
from types import MethodType
import numpy as np
import pygame
from pixelrush_luz_materiais_v3177 import PERFIS

LIMITE = 16
# tiles de cena normalmente 225x250; tamanho real contabilizado pelo cache


def entalhar(superficie, bioma, plano):
    """Aplica grafismos distintos SOMENTE em pixels opacos existentes.

    Regras: sem novos pixels alfa, sem alteracao nas faixas laterais de emenda,
    sem grafismos em fragmentos delgados, sem alterar dimensoes ou movimento.
    """
    if bioma not in PERFIS or plano not in ('far', 'mid'):
        return superficie.copy(), {'pixels_rgb': 0, 'alfa_igual': True}
    largura, altura = superficie.get_size()
    if largura < 40 or altura < 40 or not (superficie.get_flags() & pygame.SRCALPHA):
        return superficie.copy(), {'pixels_rgb': 0, 'alfa_igual': True}
    cor = pygame.surfarray.array3d(superficie)
    alpha = pygame.surfarray.array_alpha(superficie)
    mask = alpha >= 245
    # Suporte solido de 3x3, impedindo riscos em antenas/folhas/linhas soltas.
    seguro = mask.copy()
    for dx, dy in ((-2,0),(2,0),(0,-2),(0,2),(-1,-1),(1,1),(-1,1),(1,-1)):
        deslocado = np.roll(mask, (dx,dy), axis=(0,1))
        seguro &= deslocado
    seguro[:17, :] = False
    seguro[-17:, :] = False
    seguro[:, :16] = False
    seguro[:, -18:] = False
    # Tiles modulares são ampliados 2x no panorama de 500px.
    # O limite da pista protegida começa no pixel 374 local (= y604 global).
    # Logo nenhuma gravação após a linha fonte 186 (374 / 2).
    if largura == 225 and altura == 250:
        seguro[:, 184:] = False
    x, y = np.ogrid[:largura, :altura]
    # Padroes internos inspirados nos materiais EXISTENTES do bioma.
    # Os cortes sao esparsos, quebrados e ancorados nas coordenadas do tile:
    # arquitetura de superficie, nao objetos adicionados/ilhas de alfa.
    if bioma == 'cidade':
        desenho = (((y % 19 == 0) & ((x+7*(y//19)) % 29 < 18)) |
                   ((x % 24 == 0) & (y % 19 > 4) & (y % 19 < 14)))
        peso = .25
        tom = PERFIS[bioma][0]
    elif bioma == 'neve':
        desenho = (((2*x + y) % 43 == 0) & ((y//13 + x//23) % 3 != 0) |
                   ((x + 2*y) % 61 == 0) & (y % 17 < 9))
        peso = .31
        tom = (225, 245, 255)
    elif bioma == 'deserto':
        desenho = (((y + ((x//19) % 3)*3) % 23 == 0) & (x % 41 < 31) |
                   ((y + (x//13)) % 49 == 0) & (x % 31 < 12))
        peso = .27
        tom = (250, 195, 132)
    elif bioma == 'floresta':
        desenho = (((x + 3*y) % 47 == 0) & (y % 39 < 24) |
                   ((3*x - y) % 59 == 0) & (x % 35 < 12))
        peso = .23
        tom = (154, 218, 139)
    elif bioma == 'vulcao':
        desenho = (((2*x - y) % 43 == 0) & (x % 37 < 22) |
                   ((x + y) % 67 == 0) & (y % 27 < 13))
        peso = .24
        tom = (216, 123, 81)
    elif bioma == 'cidade_futurista':
        desenho = (((y % 23 == 0) & (x % 34 < 20)) |
                   ((x % 31 == 0) & (y % 45 > 7) & (y % 45 < 24)))
        peso = .29
        tom = (97, 236, 245)
    else:  # ilhas_celestes
        desenho = (((y + (x//21)*2) % 31 == 0) & (x % 35 < 24) |
                   ((2*x + y) % 73 == 0) & (y % 35 < 14))
        peso = .26
        tom = (182, 246, 225)
    if plano == 'far':
        peso *= .68
    luminancia = (cor[:,:,0].astype(np.uint16)*3 +
                  cor[:,:,1].astype(np.uint16)*6 + cor[:,:,2].astype(np.uint16))//10
    # Exclui tinta muito escura ou excessivamente clara; detalha volumes reais.
    aplicar = seguro & desenho & (luminancia > 37) & (luminancia < 229)
    if not np.any(aplicar):
        return superficie.copy(), {'pixels_rgb': 0, 'alfa_igual': True}
    nova = cor.copy()
    for canal in range(3):
        a = cor[:,:,canal][aplicar].astype(np.float32)
        nova[:,:,canal][aplicar] = np.clip(np.rint(a*(1-peso)+tom[canal]*peso),0,255).astype(np.uint8)
    resultado = pygame.Surface((largura, altura), pygame.SRCALPHA, 32)
    rgb = pygame.surfarray.pixels3d(resultado)
    rgb[:] = nova
    del rgb
    aa = pygame.surfarray.pixels_alpha(resultado)
    aa[:] = alpha
    del aa
    return resultado, {'pixels_rgb': int(np.count_nonzero(np.any(cor != nova, axis=2))),
                       'alfa_igual': True}


class _VisaoIdentidade:
    def __init__(self, cena, plano, originais):
        self.cena, self.plano, self.originais = cena, plano, originais
    def __len__(self):
        return len(self.originais)
    def __getitem__(self, indice):
        return _cachear(self.cena, self.originais[indice], self.plano)


def _cachear(cena, superficie, plano):
    dados = cena._identidade_3200
    cache = dados['cache']
    chave = (plano, id(superficie))
    if chave in cache:
        cache.move_to_end(chave)
        return cache[chave]
    resultado, metricas = entalhar(superficie, cena.biome, plano)
    cache[chave] = resultado
    dados['pixels_rgb'] += metricas['pixels_rgb']
    dados['bytes'] += resultado.get_pitch() * resultado.get_height()
    while len(cache) > LIMITE:
        _, removido = cache.popitem(last=False)
        dados['bytes'] -= removido.get_pitch() * removido.get_height()
    return resultado


def instalar_modular(cena, leve=False):
    if getattr(cena, '_identidade_3200', None) is not None:
        return cena
    cena._identidade_3200 = {'cache': OrderedDict(), 'pixels_rgb': 0,
                             'bytes': 0, 'limite': LIMITE, 'leve': bool(leve)}
    if leve:
        return cena
    antigo = cena._tile_map
    cena._identidade_tile_antigo_3200 = antigo
    def _tile(self, plano, indice, tipo):
        surf = self._identidade_tile_antigo_3200(plano, indice, tipo)
        if tipo == 'image' and plano in ('far','mid') and surf is not None:
            return _cachear(self, surf, plano)
        return surf
    cena._tile_map = MethodType(_tile, cena)
    if cena.biome == 'vulcao':
        # Vulcao acessa _layers diretamente no desenho legado; so trocar
        # a VISTA no momento do passe image, sem modificar os atlases fonte.
        original = cena._draw_layer
        cena._identidade_draw_antigo_3200 = original
        def _desenhar(self, destino, plano, percurso, tipo):
            if tipo != 'image' or plano not in ('far','mid'):
                return self._identidade_draw_antigo_3200(destino, plano, percurso, tipo)
            velho = self._layers[plano]
            self._layers[plano] = _VisaoIdentidade(self, plano, velho)
            try:
                return self._identidade_draw_antigo_3200(destino, plano, percurso, tipo)
            finally:
                self._layers[plano] = velho
        cena._draw_layer = MethodType(_desenhar,cena)
    return cena


def instalar_cidade(cidade, leve=False):
    if getattr(cidade, '_identidade_3200', False):
        return cidade
    cidade._identidade_3200 = True
    cidade._identidade_dados_3200 = {'sprites': 0, 'pixels_rgb': 0}
    if leve:
        return cidade
    vistos = {}
    for layer in cidade.layers:
        if layer.foreground or layer.name not in ('far','mid'):
            continue
        for variante in layer.variants:
            origem = variante.image
            chave = id(origem)
            if chave not in vistos:
                nova, m = entalhar(origem, 'cidade', layer.name)
                vistos[chave] = nova
                cidade._identidade_dados_3200['sprites'] += 1
                cidade._identidade_dados_3200['pixels_rgb'] += m['pixels_rgb']
            variante.image = vistos[chave]
    return cidade
