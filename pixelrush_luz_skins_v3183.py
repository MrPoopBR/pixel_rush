"""Pixel Rush v3.183.0: integra visualmente as skins à luz ambiental existente.

Apenas um blit RGB multiplicativo sobre uma COPIA da imagem visual já pronta:
- reutiliza os perfis do sistema de materiais v3.177 (sem luzes duplicadas);
- mantém canal alfa e dimensões byte a byte; nunca lê ou altera hitboxes;
- cria/cacheia os filtros só quando bioma, iluminação ou tamanho mudar;
- evita trabalho de pixel/NumPy por frame; perfil mais econômico no modo leve;
- nunca altera os atlas das nove skins nem os efeitos em image_original.
"""
from collections import OrderedDict
import pygame
from pixelrush_luz_materiais_v3177 import PERFIS

_CLIMAS_UMIDOS = frozenset((
    'chuva', 'tempestade', 'chuva_acida', 'nevasca',
    'cinzas', 'tempestade_areia', 'neve', 'neblina',
))
_CACHE = OrderedDict()
_MAX_CACHE = 64


def _filtro(bioma, noite_bin, clima_umido, tamanho, leve):
    """Filtro 24-bit em cache; nenhum pixel fora da imagem do sprite."""
    chave = (bioma, noite_bin, clima_umido, tamanho, bool(leve))
    s = _CACHE.get(chave)
    if s is not None:
        _CACHE.move_to_end(chave)
        return s
    w, h = tamanho
    s = pygame.Surface((w, h), depth=24)
    reflexo, sombra, _, _, emissao = PERFIS[bioma]
    n = noite_bin / 6.0
    # De dia predomina a reflexão do material existente; à noite a temperatura
    # das fontes luminosas já definidas para o próprio bioma.
    ambiente = tuple(round((reflexo[c] * (1 - n) + emissao[c] * n) * .88
                          + sombra[c] * .12) for c in range(3))
    energia = 0.13 + 0.11 * n + (0.055 if clima_umido else 0.0)
    # Uma leve gradação vertical faz os pés se integrarem à luz do piso.
    # Modo leve usa uma faixa única; não cria texturas intermediárias grandes.
    bandas = 1 if leve else 8
    for i in range(bandas):
        y0 = h * i // bandas
        y1 = h * (i + 1) // bandas
        if y1 <= y0:
            continue
        prof = 0.80 if leve else (0.67 + 0.55 * ((i + 0.5) / bandas))
        f = energia * prof
        rgb = tuple(max(198, min(255, round(255 * (1.0 - f) + ambiente[c] * f)))
                    for c in range(3))
        s.fill(rgb, (0, y0, w, y1-y0))
    _CACHE[chave] = s
    if len(_CACHE) > _MAX_CACHE:
        _CACHE.popitem(last=False)
    return s


def integrar_skin(jogador, bioma, noite, clima, leve=False):
    """Altera SOMENTE `jogador.image` depois das poses; `rect` fica intacto.

    Também é seguro para imagens rotacionadas, de morte e escaladas.
    Não mantém referências a imagem_original/atlas nem ao rect do jogador.
    """
    if jogador is None or bioma not in PERFIS:
        return
    original = getattr(jogador, 'image', None)
    if not isinstance(original, pygame.Surface):
        return
    tamanho = original.get_size()
    if not tamanho[0] or not tamanho[1]:
        return
    n = max(0., min(1., float(noite)))
    periodo = min(6, int(n * 6.0 + .5))
    mask = _filtro(bioma, periodo, clima in _CLIMAS_UMIDOS, tamanho, leve)
    # O cache de escalonamento do Jogador é reutilizado e mutado pelo jogo:
    # blitar SEMPRE em cópia para não manchar próximas poses, loja ou HUD.
    novo = original.copy()
    novo.blit(mask, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    jogador.image = novo
