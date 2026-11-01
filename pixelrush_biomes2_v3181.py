"""Pixel Rush v3.181.0 — microvida nos MATERIAIS existentes dos biomas.

Usa pixels opacos e coordenadas dos chunks prontos; nao cria sprites ou
particulas, nao muda geometria, mapas tecnicos, spawns nem as mascaras alfa.
O efeito acompanha o parallax original, custa O(1) por quadro e tem limite
reduzido na qualidade Android. As animacoes historicas continuam intactas.
"""
import math
import pygame
from pixelrush_biomes2_v3179 import ModularBiomeScene as Anterior


PERFIS = {
    'neve': ((247, 250, 255), 0.12),
    'deserto': ((249, 205, 133), 0.13),
    'floresta': ((155, 218, 132), 0.18),
    'vulcao': ((255, 172, 93), 0.22),
    'ilhas_celestes': ((177, 234, 219), 0.19),
    'cidade_futurista': ((124, 226, 241), 0.19),
}


def cor_compativel(bioma, cor):
    """Uma luz ambiental somente sobre tinta real, nunca sobre o alfa vazio."""
    r, g, b, a = cor
    if a < 230:
        return False
    if bioma == 'floresta':
        return g >= 76 and g > r * 1.13 and g > b * 1.10
    if bioma == 'vulcao':
        return r > 68 and r > g * 1.20 and g > b * 0.77
    if bioma == 'ilhas_celestes':
        return g > 107 and b > 101 and g > r * .92 and b > r * .90
    if bioma == 'deserto':
        return r > 118 and r > g * 1.13 and g > b * 1.08
    if bioma == 'neve':
        return b > 119 and b >= r * .84 and g >= r * .73
    if bioma == 'cidade_futurista':
        return b > 100 and b > r * 1.20 and g > r * 1.08
    return False


class ModularBiomeScene(Anterior):
    """Mantem a cadeia v3.179 + todos os sistemas ja existentes."""

    def __init__(self, biome):
        super().__init__(biome)
        # Amostras fixas e escassas de tinta do proprio chunk, feitas UMA VEZ.
        # Selecionar mid/far evita qualquer novo detalhe diante dos perigos.
        self._vida_ancoras = {}
        for plano in ('far', 'mid'):
            listas = []
            for idx, imagem in enumerate(self._layers[plano]):
                candidatos = []
                for y in range(92 + (idx % 3) * 3, 220, 11):
                    for x in range(10 + (idx % 2) * 5, 218, 12):
                        if cor_compativel(biome, imagem.get_at((x, y))):
                            candidatos.append((x, y))
                # Limita a densidade e a dispersa, sem aleatoriedade no frame.
                passo = max(1, (len(candidatos) + 20 - 1) // 20)
                listas.append(tuple(candidatos[::passo][:20]))
            self._vida_ancoras[plano] = tuple(listas)
        self._vida_amostras_visiveis = 0
        # Variantes somente em qualidade alta: Android leve nao aloca atlas extra.
        self._folhagem_animada = None


    def _preparar_folhagem(self):
        """Reusa tinta VERDE dentro das copas, sem mover silhueta ou alfa.

        Quatro variantes leves, geradas fora do loop de desenho. Troncos, céu,
        chunks, geometria, transparencias e todas as outras cores ficam iguais.
        """
        if self.biome != 'floresta' or self._folhagem_animada is not None:
            return
        import numpy as np
        quadros = {}
        for idx, original in enumerate(self._layers['mid']):
            rgb = pygame.surfarray.array3d(original)
            alpha = pygame.surfarray.array_alpha(original)
            r = rgb[:, :, 0].astype(np.uint16)
            g = rgb[:, :, 1].astype(np.uint16)
            b = rgb[:, :, 2].astype(np.uint16)
            copa = ((g > r * 1.13) & (g > b * 1.10) & (g > 78) & (alpha >= 230))
            copa[:14, :] = False
            copa[-14:, :] = False  # emendas preservadas
            copa[:, :70] = False
            copa[:, 218:] = False
            for deslocamento in (-2, -1, 1, 2):
                saida = rgb.copy()
                for y in range(70, 218):
                    # Copas flexiveis; partes baixas permanecem ancoradas.
                    d = int(round(deslocamento * min(1., max(0., (218-y)/72.))))
                    if not d:
                        continue
                    xs = np.flatnonzero(copa[:, y])
                    if not len(xs):
                        continue
                    destinos = xs + d
                    validos = (destinos >= 14) & (destinos < original.get_width()-14)
                    xs, destinos = xs[validos], destinos[validos]
                    pares = copa[destinos, y]
                    saida[destinos[pares], y, :] = rgb[xs[pares], y, :]
                variante = original.copy()
                rgb_dst = pygame.surfarray.pixels3d(variante)
                rgb_dst[:] = saida
                del rgb_dst
                quadros[(idx, deslocamento)] = variante
        self._folhagem_animada = quadros

    def _tile_map(self, layer, idx, kind):
        if (self.biome == 'floresta' and layer == 'mid' and kind == 'image'
                and getattr(self, 'visual_quality', 1)):
            if self._folhagem_animada is None:
                self._preparar_folhagem()
            # Oito posicoes de um ciclo: 0,1,2,1,0,-1,-2,-1; onda suave.
            seq = (0, 1, 2, 1, 0, -1, -2, -1)
            delta = seq[(getattr(self, '_vida_frame', 0)//9 + idx) % len(seq)]
            if delta:
                return self._folhagem_animada[(idx, delta)]
        return super()._tile_map(layer, idx, kind)

    def _aplicar_vida_materiais(self, surf, frame, climate, night):
        # Chamado APOS a renderizacao e a animacao historica, inclusive nos
        # biomas neve/deserto que nao executam _overlay_harmony no pai.
        biome = self.biome
        if biome not in PERFIS:
            return
        cor_luz, peso = PERFIS[biome]
        if night > .60:
            peso *= 1.18
        vento_forte = climate in ('vento', 'vento_folhas', 'tempestade',
                                   'nevasca', 'tempestade_areia', 'vento_neon')
        ritmo = 3 if vento_forte else 5
        fase = frame // ritmo
        qualidade = bool(getattr(self, 'visual_quality', 1))
        limite = 7 if not qualidade else 20
        count = 0
        # Exatamente o deslocamento utilizado por _draw_layer na v3.126.
        for plano, fator in (('far', .12), ('mid', .28)):
            deslocamento = max(0., getattr(self, '_vida_travel', 0.)) * fator * .5
            largura = self._layers[plano][0].get_width()
            primeiro = int(deslocamento // largura)
            shift = int(deslocamento % largura)
            for j in range(2):
                idx = (primeiro + j) % len(self._layers[plano])
                for i, (px, py) in enumerate(self._vida_ancoras[plano][idx][:limite]):
                    x = (j * largura - shift + px) * 2
                    y = py * 2
                    if x < 2 or x >= surf.get_width() - 2 or y >= surf.get_height() - 2:
                        continue
                    # Uma onda lenta com fases distintas por plano/chunk.
                    onda = math.sin((fase + i * 13 + idx * 19 + (8 if j else 0)) * .16)
                    intensidade = peso * (.34 + .66 * max(0., onda))
                    if intensidade < .055:
                        continue
                    pixel = surf.get_at((x, y))
                    if not cor_compativel(biome, pixel):
                        continue
                    for ox in (0, 1):
                        for oy in (0, 1):
                            rx, ry = x + ox, y + oy
                            original = surf.get_at((rx, ry))
                            if not cor_compativel(biome, original):
                                continue
                            rgb = tuple(max(0, min(255, int(original[k] * (1. - intensidade) +
                                                  cor_luz[k] * intensidade))) for k in range(3))
                            surf.set_at((rx, ry), (*rgb, original.a))
                            count += 1
        self._vida_amostras_visiveis = count

    def render_scene(self, target, travel, frame, night, climate, phase,
                     foreground_only=False, map_kind='image'):
        # Nao altera o estado de travel/frame: so registra a rolagem para as
        # coordenadas da amostragem visual, antes do render do pai.
        if map_kind == 'image' and not foreground_only:
            self._vida_travel = travel
            self._vida_frame = frame
        resultado = super().render_scene(target, travel, frame, night, climate, phase,
                                         foreground_only=foreground_only, map_kind=map_kind)
        if map_kind == "image" and not foreground_only:
            self._aplicar_vida_materiais(target, frame, climate, night)
        return resultado
