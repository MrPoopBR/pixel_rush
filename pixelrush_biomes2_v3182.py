"""Pixel Rush v3.182.0 — continuidade cromatica e ancoragem de parallax.

Somente RGB dos materiais preexistentes nas margens FAR/MID, precomputado no
carregamento. Preserva alfa, mapas, geometria, scroll/camera e conteudo artistico.
A microvida v3.181 passa a usar o indice e a velocidade REAIS de cada rota.
"""
import math

import numpy as np
import pygame

from pixelrush_biomes2_v3181 import ModularBiomeScene as Anterior, PERFIS, cor_compativel
from pixelrush_biomes2_v3126 import LW
from pixelrush_biomes2_v3131 import ROTAS, DISTRITOS


# Parceria de chunks estabelecida pelo motor original. Mid do Deserto varia
# conforme distritos, por isso nao pode ser modificado com um sucessor fixo.
# O panorama distante do Vulcao tambem ja tem continuidade geometrica propria.
PASSOS = {
    'neve': {'far': 1, 'mid': 1},
    'deserto': {'far': 5},
    'floresta': {'far': 5, 'mid': 3},
    'vulcao': {'mid': 1},
    'cidade_futurista': {'far': 5, 'mid': 3},
    'ilhas_celestes': {'far': 5, 'mid': 3},
}


def _harmonizar_margens(tiles, passo, largura=11):
    """Compensa pequenas discrepancias de tinta em continuidade de material.

    Corrige somente superficies opacas de cor semelhante e borda local lisa.
    Nunca inventa pixel, preenche vazio ou suaviza objetos distintos. Executa
    uma vez por instancia; sem superficie extra residente nem passe por frame.
    """
    orig = [pygame.surfarray.array3d(s).astype(np.int16) for s in tiles]
    alfa = [pygame.surfarray.array_alpha(s) for s in tiles]
    saida = [r.copy() for r in orig]
    alterados = 0
    avaliados = 0
    for index, esquerda in enumerate(orig):
        prox = (index + passo) % len(tiles)
        direita = orig[prox]
        ae, ad = alfa[index], alfa[prox]
        # Assinaturas das cores em cada lateral; apenas materiais continuos.
        col_e, col_d = esquerda[-1, :, :], direita[0, :, :]
        dif = col_d - col_e
        salto = np.max(np.abs(dif), axis=1)
        plano_e = np.max(np.abs(esquerda[-1, :, :] - esquerda[-3, :, :]), axis=1)
        plano_d = np.max(np.abs(direita[0, :, :] - direita[2, :, :]), axis=1)
        elegivel = ((ae[-1, :] == 255) & (ae[-3, :] == 255) &
                    (ad[0, :] == 255) & (ad[2, :] == 255) &
                    (salto >= 10) & (salto <= 66) &
                    (plano_e <= 26) & (plano_d <= 26) &
                    (np.max(col_e, axis=1) < 244) &
                    (np.max(col_d, axis=1) < 244))
        # Apenas linhas de superficie continua, nao pixels isolados.
        valido = elegivel & np.roll(elegivel, 1) & np.roll(elegivel, -1)
        valido[0] = valido[-1] = False
        avaliados += int(np.count_nonzero(valido))
        if not np.any(valido):
            continue
        # Restringe a correcao central a 14 niveis/canal por lado.
        ajuste = np.clip(np.rint(dif * .43), -14, 14).astype(np.int16)
        for d in range(largura):
            peso = ((largura - d) / largura) ** 2
            mod = np.rint(ajuste * peso).astype(np.int16)
            xe, xd = LW - 1 - d, d
            mascara = (valido & (ae[xe, :] == 255) & (ad[xd, :] == 255) &
                       (np.max(np.abs(esquerda[xe, :, :] - col_e), axis=1) <= 43) &
                       (np.max(np.abs(direita[xd, :, :] - col_d), axis=1) <= 43))
            if not np.any(mascara):
                continue
            saida[index][xe, mascara, :] = np.clip(esquerda[xe, mascara, :] + mod[mascara], 0, 255)
            saida[prox][xd, mascara, :] = np.clip(direita[xd, mascara, :] - mod[mascara], 0, 255)
            alterados += int(mascara.sum()) * 2
    for surf, old, new in zip(tiles, orig, saida):
        if np.array_equal(old, new):
            continue
        rgb = pygame.surfarray.pixels3d(surf)
        rgb[:] = new.astype('uint8')
        del rgb
    return {'pixels_editados': alterados, 'linhas_elegiveis': avaliados}


class ModularBiomeScene(Anterior):
    def __init__(self, biome):
        super().__init__(biome)
        self._continuidade = {}
        self._bandas_originais = {}
        for plano in PASSOS.get(biome, {}):
            for idx, tile in enumerate(self._layers[plano]):
                rgb = pygame.surfarray.array3d(tile)
                self._bandas_originais[(plano, idx)] = (rgb[:11].copy(), rgb[-11:].copy())
        # A neve usa paletas noturnas PRONTAS de uma versao anterior. Nunca
        # reconstruir esses tiles a partir de _layers: as composicoes artisticas
        # v3.175 foram aplicadas posteriormente e seriam indevidamente duplicadas.
        orig_neve = ({p: [pygame.surfarray.array3d(t).astype(np.int16)
                          for t in self._layers[p]] for p in ('far', 'mid')}
                     if biome == 'neve' else {})
        for plano, passo in PASSOS.get(biome, {}).items():
            self._continuidade[plano] = _harmonizar_margens(self._layers[plano], passo)
        # Nao guardar originais de tiles onde nenhum pixel foi alterado.
        for (plano, idx), (antes_e, antes_d) in tuple(self._bandas_originais.items()):
            rgb = pygame.surfarray.array3d(self._layers[plano][idx])
            if np.array_equal(rgb[:11], antes_e) and np.array_equal(rgb[-11:], antes_d):
                del self._bandas_originais[(plano, idx)]
        if biome == 'neve':
            for plano in ('far', 'mid'):
                for idx, src in enumerate(self._layers[plano]):
                    novo = pygame.surfarray.array3d(src).astype(np.int16)
                    delta = novo - orig_neve[plano][idx]
                    if not np.any(delta):
                        continue
                    for nivel in range(5):
                        dest = self._night_tiles[(0, plano, idx, nivel)]
                        fatores = 1.0 - np.array((.42, .39, .27)) * nivel / 4
                        ajuste = np.rint(delta * fatores).astype(np.int16)
                        arr = pygame.surfarray.pixels3d(dest)
                        arr[:] = np.clip(arr.astype(np.int16) + ajuste, 0, 255).astype(np.uint8)
                        del arr
        # Invalida somente imagens derivadas do RGB, nunca os mapas tecnicos.
        if hasattr(self, '_composites'):
            self._composites.pop('image', None)

    def _tile_map(self, layer, idx, kind):
        # v3.135 recalcula normal/material com RGB do atlas sob demanda.
        # Restaurar temporariamente as margens APENAS durante esse calculo
        # mantem os mapas fisico/GLSL byte a byte identicos a v3.181.
        bandas = getattr(self, '_bandas_originais', {}).get((layer, idx))
        if (bandas is None or kind not in ('normal', 'material') or
                self.biome not in ('floresta','vulcao','cidade_futurista','ilhas_celestes')):
            return super()._tile_map(layer, idx, kind)
        if (layer, idx, kind) in self._map_cache:
            return super()._tile_map(layer, idx, kind)
        original = self._layers[layer][idx]
        arr = pygame.surfarray.pixels3d(original)
        novas = (arr[:11].copy(), arr[-11:].copy())
        arr[:11], arr[-11:] = bandas
        del arr
        try:
            return super()._tile_map(layer, idx, kind)
        finally:
            arr = pygame.surfarray.pixels3d(original)
            arr[:11], arr[-11:] = novas
            del arr

    def _prepare_maps(self, pose, layer, index, src):
        # O mapa normal do motor da Neve usa derivadas do RGB do chunk.
        # Preserva o contrato tecnico antigo ao calcular o mapa com a mesma
        # tinta original, sem modificar as imagens finais ja harmonizadas.
        bandas = getattr(self, '_bandas_originais', {}).get((layer, index)) if pose == 0 else None
        if bandas is None or self.biome != 'neve':
            return super()._prepare_maps(pose, layer, index, src)
        arr = pygame.surfarray.pixels3d(src)
        novas = (arr[:11].copy(), arr[-11:].copy())
        arr[:11], arr[-11:] = bandas
        del arr
        try:
            return super()._prepare_maps(pose, layer, index, src)
        finally:
            arr = pygame.surfarray.pixels3d(src)
            arr[:11], arr[-11:] = novas
            del arr

    def _indice_parallax(self, plano, bloco):
        """Mesmo indice de chunk do renderizador original em cada bioma."""
        if self.biome == 'deserto':
            if plano == 'far':
                return bloco * 5 % len(self._layers[plano])
            distrito = (bloco // 3) % len(DISTRITOS)
            grupo = ROTAS[plano][distrito]
            return grupo[(bloco + bloco // 12) % len(grupo)]
        if self.biome in ('floresta', 'cidade_futurista', 'ilhas_celestes'):
            return bloco * (5 if plano == 'far' else 3) % len(self._layers[plano])
        return bloco % len(self._layers[plano])

    def _aplicar_vida_materiais(self, surf, frame, climate, night):
        """Iluminacao v3.181 ancorada no MESMO tile/shift do parallax real."""
        bioma = self.biome
        if bioma not in PERFIS:
            return
        cor_luz, peso = PERFIS[bioma]
        if night > .60:
            peso *= 1.18
        vento_forte = climate in ('vento', 'vento_folhas', 'tempestade',
                                   'nevasca', 'tempestade_areia', 'vento_neon')
        fase = frame // (3 if vento_forte else 5)
        qualidade = bool(getattr(self, 'visual_quality', 1))
        limite = 20 if qualidade else 7
        count = 0
        for plano, fator in (('far', .12 if bioma == 'vulcao' else .10),
                              ('mid', .28 if bioma == 'vulcao' else .25)):
            offset = max(0., getattr(self, '_vida_travel', 0.)) * fator * .5
            primeiro = int(offset // LW)
            shift = int(offset % LW)
            for j in range(2):
                idx = self._indice_parallax(plano, primeiro + j)
                for i, (px, py) in enumerate(self._vida_ancoras[plano][idx][:limite]):
                    x, y = (j * LW - shift + px) * 2, py * 2
                    if x < 2 or x >= surf.get_width() - 2 or y >= surf.get_height() - 2:
                        continue
                    onda = math.sin((fase + i * 13 + idx * 19 + (8 if j else 0)) * .16)
                    intensidade = peso * (.34 + .66 * max(0., onda))
                    if intensidade < .055 or not cor_compativel(bioma, surf.get_at((x, y))):
                        continue
                    for ox in (0, 1):
                        for oy in (0, 1):
                            rx, ry = x + ox, y + oy
                            original = surf.get_at((rx, ry))
                            if not cor_compativel(bioma, original):
                                continue
                            rgb = tuple(max(0, min(255, int(original[k] * (1.-intensidade) +
                                                   cor_luz[k] * intensidade))) for k in range(3))
                            surf.set_at((rx, ry), (*rgb, original.a))
                            count += 1
        self._vida_amostras_visiveis = count
