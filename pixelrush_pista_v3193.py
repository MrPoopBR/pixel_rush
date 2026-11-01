"""Plano G v3.193.0 — limpeza de elementos cosméticos redundantes da pista.

Mantém a geometria, a borda de contato, a rolagem e as texturas existentes.
A microtextura de contraste alto é atenuada UMA VEZ, no cache RGB da
qualidade alta; o modo leve não faz nenhum preprocessamento adicional.
"""
import pygame

# Linhas superiores (contato), juntas longitudinais e camada inferior intocadas.
_LINHAS_INTERIORES = tuple(list(range(15, 30)) + list(range(33, 47)))
_BIOMAS = frozenset(('cidade', 'neve', 'deserto', 'floresta', 'vulcao',
                     'cidade_futurista', 'ilhas_celestes'))


def limpar_microcontraste(tile):
    """Suaviza pixels de alto contraste no miolo do material, sem apagar bordas.

    Trabalha apenas em RGB e usa cores que já estão presentes em cada linha,
    jamais desenha um novo objeto ou elemento sobre o chão.
    """
    if tile.get_width() < 150 or tile.get_height() != 70:
        return tile
    import numpy as np
    out = tile.copy()
    rgb = pygame.surfarray.pixels3d(out)
    try:
        for y in _LINHAS_INTERIORES:
            row = rgb[:, y, :]
            packed = (row[:, 0].astype(np.uint32) << 16) | (row[:, 1].astype(np.uint32) << 8) | row[:, 2].astype(np.uint32)
            colors, counts = np.unique(packed, return_counts=True)
            frequent = int(colors[counts.argmax()])
            base = np.array(((frequent >> 16) & 255, (frequent >> 8) & 255, frequent & 255), dtype=np.int16)
            original = row.astype(np.int16)
            contraste = np.max(np.abs(original - base), axis=1)
            # Os detalhes de baixo contraste são preservados integralmente.
            peso = np.where(contraste > 38, 0.43,
                            np.where(contraste > 26, 0.28, 0.0))
            if np.any(peso):
                updated = np.rint(original * (1.0 - peso[:, None]) + base * peso[:, None])
                row[:] = np.clip(updated, 0, 255).astype(np.uint8)
    finally:
        del rgb
    return out


def instalar_limpeza_pista(parallax_class):
    """Substitui só dois hooks VISUAIS já existentes, depois dos patches antigos."""
    obter_anterior = parallax_class._obter_tile_chao

    def obter_tile_limpo(self):
        source = obter_anterior(self)
        if (self.cenario not in _BIOMAS or
                getattr(getattr(self, 'world', None), 'lightweight', False)):
            return source
        cache = getattr(self, '_cache_pista_v3193', None)
        if cache is None:
            cache = {}
            self._cache_pista_v3193 = cache
        chave = (self.cenario, id(source))
        cleaned = cache.get(chave)
        if cleaned is None:
            # Máximo um tile por bioma. Tudo pré-calculado, nunca por quadro.
            cleaned = limpar_microcontraste(source)
            if len(cache) >= len(_BIOMAS):
                cache.clear()
            cache[chave] = cleaned
        return cleaned

    def desenhar_pista_limpa(self, superficie):
        # O tile de bioma já contém acabamento, juntas e marcações. Não repetir
        # o overlay fixo e os riscos cosméticos que flutuavam sobre a rolagem.
        return None

    parallax_class._obter_tile_chao = obter_tile_limpo
    parallax_class._desenhar_chao_vivo = desenhar_pista_limpa
    return obter_anterior
