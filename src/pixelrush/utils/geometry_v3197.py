"""Plano G v3.197.0: facetas/isometria leve, somente nas artes de fundo.

Preserva completamente os assets fonte, mapas de geometria/colisao, scroll,
camadas proximas, gameplay. Somente superficies do tipo `image` recebem volume.
Nenhum calculo de pixel e feito em cada quadro: mini-atlases LRU por tile.
"""
from collections import OrderedDict
from types import MethodType

import numpy as np
import pygame


# Dimensoes em pixels dos atlases existentes; nenhuma alteracao de resolucao.
PROFUNDIDADE = {'far': 3, 'mid': 5}
LIMITE_CACHE = 18  # max 18 x 225 x 250 x RGBA = ~3.87 MiB, apenas PC


def esculpir_volume(original, plano, biome, borda=12):
    """Extruda contornos *solidos* para baixo/direita, com faces laterais reais.

    Pinta o volume ATRAS da silhueta, jamais duplica sprite/membro. A extrusao
    eh pixelada e restrita as areas transparentes, evitando overlays soltos.
    Protege faixas de costura nas bordas e nao invade a camada `near`/pista.
    """
    largura, altura = original.get_size()
    espessura = PROFUNDIDADE[plano]
    src = pygame.surfarray.array3d(original)
    a = pygame.surfarray.array_alpha(original)
    out = src.copy()
    out_a = a.copy()
    solido = a >= 220
    # Isolar planos continuos; linhas de um pixel e folhas soltas nao projetam
    # volumes artificiais.  Descartar extremidades do chunk para evitar emendas.
    esp = np.zeros_like(solido)
    esp[1:-1, 1:-1] = (solido[1:-1, 1:-1] &
                          solido[:-2, 1:-1] & solido[2:, 1:-1] &
                          solido[1:-1, :-2] & solido[1:-1, 2:])
    m = max(borda, espessura + 4)
    esp[:m, :] = False
    esp[-m:, :] = False
    esp[:, :14] = False
    esp[:, -16:] = False

    # Sombra na face lateral, com valores do PROPRIO material original;
    # nenhuma cor de objetos inventados ou textura/microbrilho superposta.
    sombra = {'neve': .77, 'deserto': .66, 'floresta': .63,
              'vulcao': .60, 'cidade_futurista': .59,
              'ilhas_celestes': .70, 'cidade': .65}.get(biome, .66)
    # Primeiro o fundo da extrusao (ordem inversa, ultima faceta mais proxima)
    # e depois o material frontal original.
    for d in range(1, espessura + 1):
        dx, dy = d, max(1, (d + 1) // 2)
        origem = esp[:-dx, :-dy]
        destino = (out_a[dx:, dy:] == 0) & origem
        # So prolongar uma face ja conectada por ARESTA ao volume anterior.
        # Impede ilhas de pixels diagonais/flutuantes sem usar OpenCV/SciPy.
        apoio = ((out_a[dx-1:-1, dy:] > 0) |
                 (out_a[dx:, dy-1:-1] > 0))
        destino &= apoio
        if not np.any(destino):
            continue
        cor = np.maximum(0, np.minimum(255,
                 np.rint(src[:-dx, :-dy] * (sombra - .04 * d / espessura)))).astype(np.uint8)
        # Matiz nao ultrapassa o canal alfa permitido no desenho original.
        parcela = out[dx:, dy:]
        parcela[destino] = cor[destino]
        alfa = out_a[dx:, dy:]
        alfa[destino] = 255

    # Faces geométricas internas: bevel em cristas e sombra nos flancos.
    # So nos pixels originais opacos. Não faz glow nem troca paleta geral.
    topo = np.zeros_like(solido)
    direita = np.zeros_like(solido)
    topo[:, 1:] = solido[:, 1:] & ~solido[:, :-1]
    direita[:-1, :] = solido[:-1, :] & ~solido[1:, :]
    faixa = np.zeros_like(solido)
    faixa[m:-m, 14:-16] = True
    topo &= faixa
    direita &= faixa
    # Excluir fragmentos minúsculos e pelo/antena de 1 px.
    topo &= (solido & np.roll(solido, 1, 0) & np.roll(solido, -1, 0))
    direita &= (solido & np.roll(solido, 1, 1) & np.roll(solido, -1, 1))
    if np.any(topo):
        out[topo] = np.minimum(255, np.rint(src[topo].astype(np.float32) * 1.115 + 6)).astype(np.uint8)
    if np.any(direita):
        out[direita] = np.rint(src[direita].astype(np.float32) * sombra).astype(np.uint8)
    # Frente permanece por cima da extrusao, inclusive onde ja era transparente
    # parcial (rebarbas e bordas semiopacas antigas ficam como na arte-base).
    frente = a != 0
    # Nao apagar as faces internas calculadas em pixels originalmente opacos.
    parciais = frente & (a < 220)
    out[parciais] = src[parciais]
    out_a[frente] = a[frente]

    modificados = int(np.count_nonzero(np.any(out != src, axis=2) | (out_a != a)))
    externo = int(np.count_nonzero((a == 0) & (out_a != 0)))
    novo = pygame.Surface((largura, altura), pygame.SRCALPHA, 32)
    pixels = pygame.surfarray.pixels3d(novo)
    pixels[:] = out
    del pixels
    alphas = pygame.surfarray.pixels_alpha(novo)
    alphas[:] = out_a
    del alphas
    return novo, {'pixels': modificados, 'extrudados': externo}


def _decorar_cacheado(scene, superficie, plano):
    dados = scene._geometria_3197
    cache = dados['cache']
    chave = (plano, id(superficie))
    if chave in cache:
        cache.move_to_end(chave)
        return cache[chave]
    novo, info = esculpir_volume(superficie, plano, scene.biome)
    cache[chave] = novo
    dados['pintados'] += info['pixels']
    dados['extrudados'] += info['extrudados']
    if len(cache) > LIMITE_CACHE:
        cache.popitem(last=False)
    return novo


class _VisaoVolume:
    """Lista virtual utilizada somente durante o blit legado do Vulcão."""
    def __init__(self, scene, plano, originais):
        self.scene = scene
        self.plano = plano
        self.originais = originais

    def __len__(self):
        return len(self.originais)

    def __getitem__(self, indice):
        return _decorar_cacheado(self.scene, self.originais[indice], self.plano)


def instalar_modular(scene, leve=False):
    if getattr(scene, '_geometria_3197', None) is not None:
        return scene
    scene._geometria_3197 = {'cache': OrderedDict(), 'pintados': 0,
                             'extrudados': 0, 'limite': LIMITE_CACHE,
                             'leve': bool(leve)}
    if leve:
        return scene
    original = scene._tile_map
    scene._geo3197_tile_anterior = original

    def _tile_mapeado(self, plano, indice, tipo):
        superficie = self._geo3197_tile_anterior(plano, indice, tipo)
        if tipo != 'image' or plano not in PROFUNDIDADE or superficie is None:
            return superficie
        # Identifica poses noturnas, variantes de vento e tiles normais.
        return _decorar_cacheado(self, superficie, plano)

    # Na cadeia v3.165, o Vulcão desenha tiles diretamente de _layers,
    # ignorando _tile_map('image'). Interceptar SOMENTE os dois acessos de
    # fundo e passar pelo desenho ORIGINAL (inclui lava/fumaça originais).
    # Não trocar o atlas real: mapas técnicos e colisões seguem idênticos.
    if scene.biome == 'vulcao':
        desenho_legado = scene._draw_layer
        scene._geo3197_draw_legado = desenho_legado
        def _desenho(self, destino, plano, travel, tipo):
            if tipo != 'image' or plano not in PROFUNDIDADE:
                return self._geo3197_draw_legado(destino, plano, travel, tipo)
            anterior = self._layers[plano]
            self._layers[plano] = _VisaoVolume(self, plano, anterior)
            try:
                return self._geo3197_draw_legado(destino, plano, travel, tipo)
            finally:
                self._layers[plano] = anterior
        scene._draw_layer = MethodType(_desenho, scene)
    scene._tile_map = MethodType(_tile_mapeado, scene)
    return scene


def instalar_cidade(cidade, leve=False):
    if getattr(cidade, '_geometria_3197', False):
        return cidade
    cidade._geometria_3197 = True
    cidade._geometria_contagem_3197 = {'pixels': 0, 'extrudados': 0}
    if leve:
        return cidade
    tratados = set()
    # Somente `image` de FAR/MID. Todos os outros atlas e mapas intactos.
    for layer in cidade.layers:
        if layer.foreground or layer.name not in PROFUNDIDADE:
            continue
        for variant in layer.variants:
            if id(variant.image) in tratados:
                continue
            tratados.add(id(variant.image))
            novo, info = esculpir_volume(variant.image, layer.name, 'cidade', borda=20)
            # Alterar apenas a entrada image da variante; os seis mapas tecnicos
            # e os outros campos da variante permanecem byte a byte na RAM.
            variant.image = novo
            for chave in ('pixels', 'extrudados'):
                cidade._geometria_contagem_3197[chave] += info[chave]
    return cidade
