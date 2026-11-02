# -*- coding: utf-8 -*-
"""PIXEL RUSH v3.277.33-QA — compositor de nuvens e profiling do panorama.

Preserva pixels, ordem de desenho, tempo, profundidade e biomas.
A conversao de 16 primitivas por nuvem em um blit e validada por regressao
RGB/RGBA antes da homologacao. Nunca altera cenas ou gameplay de producao.
"""
from functools import lru_cache, wraps

_INSTALADO = False
_ORIGINAIS = {}


@lru_cache(maxsize=96)
def _textura_nuvem(escala, cor, sombra, luz):
    import pygame
    import pixelrush_cenarios_v398 as visual
    s = max(1, int(escala))
    # Limites originais dos retangulos, inclusive a sombra deslocada.
    tex = pygame.Surface((70 * s, 33 * s), pygame.SRCALPHA)
    _ORIGINAIS['nuvem_pixel'](tex, 0, 0, s, cor, sombra, luz)
    return tex


def _nuvem_qa(superficie, x, y, escala, cor, sombra, luz):
    s = max(1, int(escala))
    # Os retangulos originais quantizam x e y com int(), nao round().
    textura = _textura_nuvem(s, tuple(cor), tuple(sombra), tuple(luz))
    superficie.blit(textura, (int(x), int(y)))


# Medir apenas as chamadas reais do caminho visual ativo, sem instrumentar
# a pilha do profiler legado e sem duplicar submedidas.
_CAMADAS = {
    'desenhar_ceu': 'cenario_ceu',
    'desenhar_panorama': 'cenario_panorama',
    'desenhar_emenda_panorama': 'cenario_emenda',
    'desenhar_animacoes_fundo': 'cenario_animacoes_fundo',
    'desenhar_animacoes_frente': 'cenario_animacoes_frente',
    'desenhar_reacao_noturna': 'cenario_reacao_noturna',
    'desenhar_foco_pista': 'cenario_foco_pista',
    'desenhar_acabamento_proximo': 'cenario_acabamento',
}


def _medido(original, nome):
    @wraps(original)
    def chamar(*args, **kwargs):
        from pixelrush_profiler_v3204 import _QA_ATUAL
        qa = _QA_ATUAL
        ativo = qa is not None and qa.atual is not None
        if ativo:
            qa.sub_inicio(nome)
        try:
            return original(*args, **kwargs)
        finally:
            if ativo:
                qa.sub_fim()
    return chamar


def instalar():
    global _INSTALADO
    if _INSTALADO:
        return
    import pixelrush_cenarios_v398 as visual
    _ORIGINAIS['nuvem_pixel'] = visual.nuvem_pixel
    for metodo, nome in _CAMADAS.items():
        original = getattr(visual, metodo)
        _ORIGINAIS[metodo] = original
        setattr(visual, metodo, _medido(original, nome))
    visual.nuvem_pixel = _nuvem_qa
    _INSTALADO = True


def restaurar_para_teste():
    global _INSTALADO
    if not _INSTALADO:
        return
    import pixelrush_cenarios_v398 as visual
    for metodo, original in _ORIGINAIS.items():
        setattr(visual, metodo, original)
    _ORIGINAIS.clear()
    _textura_nuvem.cache_clear()
    _INSTALADO = False
