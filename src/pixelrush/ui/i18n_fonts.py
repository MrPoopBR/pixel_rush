# -*- coding: utf-8 -*-
"""Adaptadores de fontes localizadas extraidos do motor QA790 sem alterar metodos.
O modulo de traducoes e o mesmo objeto importado pelo motor (sem copia de estado).
"""
import pixelrush_traducoes_v3247 as _i18n247

class _FonteHindiComFallback:
    """Mescla trechos Devanagari e latinos para preservar nomes/números sem fontes enormes."""
    __slots__ = ("deva", "latina")

    def __init__(self, deva, latina):
        self.deva, self.latina = deva, latina

    def _partes(self, texto):
        if not texto:
            return []
        grupos = []
        atual = ""
        indice = None
        for caractere in texto:
            deva = '\u0900' <= caractere <= '\u097f'
            if atual and deva != indice:
                grupos.append((atual, indice))
                atual = ""
            atual += caractere
            indice = deva
        grupos.append((atual, indice))
        return grupos

    def size(self, texto):
        partes = self._partes(str(texto))
        larguras = [ (self.deva if d else self.latina).size(t) for t, d in partes ]
        return (sum(w for w, h in larguras), max((h for w, h in larguras), default=self.latina.get_height()))

    def render(self, texto, antialias, cor):
        import pygame
        partes = [(self.deva if d else self.latina).render(t, antialias, cor)
                  for t, d in self._partes(str(texto))]
        largura = sum(s.get_width() for s in partes)
        altura = max((s.get_height() for s in partes), default=self.latina.get_height())
        superficie = pygame.Surface((max(1, largura), max(1, altura)), pygame.SRCALPHA)
        x = 0
        for segmento in partes:
            superficie.blit(segmento, (x, max(0, (altura-segmento.get_height()) // 2)))
            x += segmento.get_width()
        return superficie

    def get_height(self):
        return max(self.deva.get_height(), self.latina.get_height())

    def get_linesize(self):
        return max(self.deva.get_linesize(), self.latina.get_linesize())

class _FontePainelLocalizado:
    __slots__ = ('original', 'idioma')

    def __init__(self, original, idioma):
        self.original = original
        self.idioma = idioma

    def _traduzir(self, texto):
        return _i18n247.localizar_literal(str(texto), self.idioma)

    def size(self, texto):
        return self.original.size(self._traduzir(texto))

    def render(self, texto, antialias, cor, *args, **kwargs):
        txt = self._traduzir(texto)
        imagem = self.original.render(txt, antialias, cor, *args, **kwargs)
        # Evita cortes nos painéis de 450px sem recriar fontes.
        if imagem.get_width() > 402:
            import pygame
            imagem = pygame.transform.smoothscale(imagem, (402, imagem.get_height()))
        return imagem

    def __getattr__(self, nome):
        return getattr(self.original, nome)
