"""v3.194.0 — acabamento cromático dos pisos já existentes (Plano G / Etapa 2).

NÃO cria geometria. Respeita o contato, os pixels alfa, as hitboxes e
os timers. Faz o trabalho apenas na criação do tile, em qualidade alta.
A edição leve devolve exatamente a superfície produzida pela v3.193.0.
"""

import numpy as np
import pygame

_BIOMAS = frozenset((
    'cidade', 'neve', 'deserto', 'floresta', 'vulcao',
    'cidade_futurista', 'ilhas_celestes',
))
# Matizes discretas de materiais existentes, não cores de objetos artificiais.
_TONS = {
    'cidade': (-1, -1, 1),
    'neve': (-1, 1, 3),
    'deserto': (3, 1, -1),
    'floresta': (0, 2, -1),
    'vulcao': (3, 0, -1),
    'cidade_futurista': (-1, 1, 3),
    'ilhas_celestes': (0, 2, 3),
}
# Variação progressiva na face já desenhada pelo jogo (y=49..66).
# A borda de contato e a divisória geométrica ficam intocadas.
_PROFUNDA = (6, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -6, -7, -7, -8, -8)


def refinar_material_piso(tile, bioma):
    """Prepara uma única variante: relevo cromático e emendas contínuas RGB.

    Não modifica dimensões, canal alfa, perfil de solo, tile offsets ou camada
    de obstáculos. Contato y<15 preservado; juntas internas só mudam nos 9px de emenda.
    """
    if bioma not in _BIOMAS or tile.get_height() != 70 or tile.get_width() < 450:
        return tile
    out = tile.copy()
    rgb = pygame.surfarray.pixels3d(out)
    try:
        matiz = np.array(_TONS[bioma], dtype=np.int16)
        # Acabamento sutil da superfície do material. Os brilhos já existentes
        # muito saturados não precisam de outra passada de luz.
        for y in range(16, 28):
            if y in (23, 24):
                continue
            row = rgb[:, y, :]
            shade = 3 if y <= 19 else (-2 if y >= 25 else 1)
            src = row.astype(np.int16)
            # Não altera as cores brilhantes: preserve marcas e sinalizadores.
            mask = (src.max(axis=1) < 210) & (src.min(axis=1) > 15)
            src[mask] = np.clip(src[mask] + shade + matiz, 0, 255)
            row[:] = src.astype(np.uint8)
        # Lateral vertical com transição iluminada -> sombra de oclusão inferior.
        # A largura da face não cresce nem um pixel e não cria feições que
        # possam parecer buracos, perigos ou novos obstáculos.
        for dy, shade in enumerate(_PROFUNDA):
            y = 49 + dy
            row = rgb[:, y, :]
            src = row.astype(np.int16)
            # Mantém reflexos e detalhes antigos com intensidade controlada.
            source_max = src.max(axis=1)
            safe = (source_max < 235) & (src.min(axis=1) > 10)
            # Em contraste forte, apenas metade do sombreado para não apagar
            # marcas dos materiais que já estavam na v3.193.0.
            delta = np.where(source_max > 190, int(round(shade / 2)), shade)
            corrected = src + delta[:, None] + matiz[None, :]
            src[safe] = np.clip(corrected[safe], 0, 255)
            row[:] = src.astype(np.uint8)
        # Alguns tiles antigos têm detalhes atingindo x=0 ou x=width-1,
        # causando linhas descontínuas quando o sprite longo se repete.
        # Harmonizar somente linhas internas e apenas se houver diferença RGB.
        # A transição não toca as faixas de contato (y=0..14), junção geométrica
        # (y=67..69), nem desenho da pista fora do tile. As juntas
        # y=30..32 e a borda y=47..48 só mudam nas extremidades do tile.
        width = rgb.shape[0]
        for y in range(15, 67):
            left = rgb[0, y].astype(np.int16)
            right = rgb[width - 1, y].astype(np.int16)
            if np.max(np.abs(left - right)) <= 7:
                continue
            anchor = np.rint((left + right) / 2).astype(np.int16)
            for step in range(9):
                k = ((9 - step) / 9.0) ** 2
                for xx in (step, width - 1 - step):
                    original = rgb[xx, y].astype(np.int16)
                    rgb[xx, y] = np.clip(np.rint(original * (1 - k) + anchor * k), 0, 255).astype(np.uint8)
    finally:
        del rgb
    return out


def instalar_pisos_premium(parallax_class):
    """Acopla-se depois do hook v3.193; não altera o método draw_chao."""
    anterior = parallax_class._obter_tile_chao

    def obter_tile_premium(self):
        origem = anterior(self)
        if (self.cenario not in _BIOMAS or
                getattr(getattr(self, 'world', None), 'lightweight', False)):
            return origem
        cache = getattr(self, '_cache_pisos_v3194', None)
        if cache is None:
            cache = {}
            self._cache_pisos_v3194 = cache
        chave = (self.cenario, id(origem))
        tile = cache.get(chave)
        if tile is None:
            tile = refinar_material_piso(origem, self.cenario)
            # Apenas sete entradas, sem crescimento ilimitado em biomas alternados.
            if len(cache) >= len(_BIOMAS):
                cache.clear()
            cache[chave] = tile
        return tile

    parallax_class._obter_tile_chao = obter_tile_premium
    return anterior
