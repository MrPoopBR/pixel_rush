# -*- coding: utf-8 -*-
"""Política única QA: nunca expulsar mapas técnicos ainda quentes.

O rastreio é por LivingWorld e não retém Surfaces ou cenas. Sem marcador
confiável, a política é conservadora para preservar o caminho de imagem.
"""

_TECH_KINDS = frozenset(('geometry', 'normal', 'material', 'flow', 'fxmask'))


def mapa_tecnico_quente(world, chave, janela_quadros=180):
    """True quando a Surface pode estar em uso ou não há prova de frieza.

    Um marcador de outro bioma permite desalocar a Surface antiga. O frame
    atual pode reiniciar em transições; nesse caso não inferir frieza.
    """
    if not (isinstance(chave, tuple) and len(chave) >= 2 and
            chave[0] in _TECH_KINDS):
        return False
    usos = getattr(world, '_qa_surface_last_used', None)
    if not isinstance(usos, dict):
        return True
    ultimo = usos.get(chave)
    if ultimo is None:
        return True
    try:
        bioma_uso, quadro_uso = ultimo
        if bioma_uso != world.biome:
            return False
        atual = world.frame
        delta = atual - quadro_uso
        return delta < 0 or delta <= janela_quadros
    except (AttributeError, TypeError, ValueError):
        return True

# QA762: caches derivados de cenas 2.5D que podem ser reconstruídos.
# Neve precompõe TODAS as variantes de _night_tiles no __init__ e consulta
# por chave direta: JAMAIS esvaziar esse dicionário, mesmo em RSS alto.
# Deserto gera _night_tiles sob demanda. _maps e _composites são lazy
# nos dois biomas. Nunca expulsar mapas do bioma ativo deste World.
_MODULAR_CACHES_COMUNS=frozenset(('_maps','_composites'))
_MODULAR_DESERTO=frozenset(('_maps','_composites','_night_tiles'))


def modular_cache_fria(world, biome, atributo):
    if biome==getattr(world,'biome',None):
        return False
    if biome=='deserto':
        return atributo in _MODULAR_DESERTO
    if biome=='neve':
        return atributo in _MODULAR_CACHES_COMUNS
    return False
