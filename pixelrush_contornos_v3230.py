"""Pixel Rush v3.230.0 — correção localizada do contorno do gêiser.

Reutiliza o renderizador e o cache LRU da v3.180.0. Na pose de
preparação do gêiser (V4), os trechos separados da coluna de erupção
não recebiam contorno, pois pygame.mask.outline() retorna apenas um
contorno. Corrigimos exclusivamente os trechos da coluna (>=30 pixels);
centelhas decorativas e os outros 27 tipos não são modificados.

O processamento ocorre APENAS quando a sprite entra no cache já existente.
Preserva sprites originais, alfa, posições, hitboxes, etapas e física.
"""
import pygame
from pixelrush_render_v3180 import ContornosLegiveis as _Base
from pixelrush_render_v3170 import PALETAS


class ContornosLegiveis(_Base):
    def _bioma(self, obj):
        self._codigo_em_desenho = getattr(obj, 'codigo', None)
        return super()._bioma(obj)

    def _obter(self, imagem, bioma):
        # Mantém o mesmo cache, capacidade, descarte e blit do sistema antigo.
        chave = (imagem, bioma)
        ja_cacheado = chave in self._cache
        frames = super()._obter(imagem, bioma)
        if ja_cacheado or not frames or getattr(self, '_codigo_em_desenho', None) != 'V4':
            return frames

        mascara = pygame.mask.from_surface(imagem, 110)
        componentes = sorted(mascara.connected_components(),
                             key=lambda parte: parte.count(), reverse=True)
        if len(componentes) < 2:
            return frames
        corpo_rects = componentes[0].get_bounding_rects()
        if not corpo_rects:
            return frames
        inicio_corpo = corpo_rects[0].top
        cores = PALETAS.get(bioma, PALETAS['cidade'])
        margem = self._margem
        for parte in componentes[1:]:
            # São exclusivamente as faixas reais do jato acima da base.
            # Ignora centelhas soltas menores que 30 pixels.
            if parte.count() < 30:
                continue
            rects = parte.get_bounding_rects()
            if not rects or rects[0].bottom > inicio_corpo:
                continue
            borda = parte.outline(2)
            if len(borda) < 3:
                continue
            pontos = tuple((x + margem, y + margem) for x, y in borda)
            for sprite_contorno, cor in zip(frames, cores):
                pygame.draw.lines(sprite_contorno, (13, 20, 33, 245),
                                  True, pontos, 6)
                pygame.draw.lines(sprite_contorno, (*cor, 255),
                                  True, pontos, 2)
        return frames
