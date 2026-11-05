# -*- coding: utf-8 -*-
"""PIXEL RUSH v3.277.33-QA — compositor de nuvens e profiling do panorama.

Preserva pixels, ordem de desenho, tempo, profundidade e biomas.
A conversao de 16 primitivas por nuvem em um blit e validada por regressao
RGB/RGBA antes da homologacao. Nunca altera cenas ou gameplay de producao.
"""
from functools import lru_cache, wraps
import os
import pygame
# QA760: SDL SRCALPHA exige RGB oculto preservado. Na rota RGB opaca
# o blit da nuvem precomposta e equivalente aos 16 pygame.draw.rect.
_QA_SAFE_CLOUD_CACHE=os.environ.get('PIXELRUSH_QA_SAFE_CLOUD_CACHE','1')=='1'
_CLOUD_STATS={'blits_rgb':0,'fallback_rgba':0,'fallback_alpha':0,'fallback_escala':0}

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
    # A cena real usa escala 1. Impede que variantes ampliadas,
    # nao usadas no panorama, consumam megabytes no cache mobile.
    if s!=1 or not _QA_SAFE_CLOUD_CACHE:
        _CLOUD_STATS['fallback_escala']+=1
        return _ORIGINAIS['nuvem_pixel'](
            superficie, x, y, escala, cor, sombra, luz)
    # Em destino SRCALPHA, o blit de pixels (0,0,0,0) pode zerar os
    # canais RGB ocultos que pygame.draw.rect jamais alteraria.
    # Preservar o contrato byte RGBA original, sem mascaras extras.
    if superficie.get_flags() & pygame.SRCALPHA:
        _CLOUD_STATS['fallback_rgba']+=1
        return _ORIGINAIS['nuvem_pixel'](
            superficie, x, y, escala, cor, sombra, luz)
    # Em alvo RGB, cores com alpha<255 seriam aplicadas como blend
    # pelo blit, enquanto pygame.draw.rect escreve a cor diretamente.
    if any(len(c)>3 and c[3]!=255 for c in (cor,sombra,luz)):
        _CLOUD_STATS['fallback_alpha']+=1
        return _ORIGINAIS['nuvem_pixel'](
            superficie, x, y, escala, cor, sombra, luz)
    # Os retangulos originais quantizam x e y com int(), nao round().
    textura = _textura_nuvem(s, tuple(cor), tuple(sombra), tuple(luz))
    superficie.blit(textura, (int(x), int(y)))
    _CLOUD_STATS['blits_rgb']+=1


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


def diagnostico_nuvens():
    return dict(_CLOUD_STATS,cache=_textura_nuvem.cache_info()._asdict())


def restaurar_para_teste():
    global _INSTALADO
    if not _INSTALADO:
        return
    import pixelrush_cenarios_v398 as visual
    for metodo, original in _ORIGINAIS.items():
        setattr(visual, metodo, original)
    _ORIGINAIS.clear()
    _textura_nuvem.cache_clear()
    for chave in _CLOUD_STATS:
        _CLOUD_STATS[chave]=0
    _INSTALADO = False
