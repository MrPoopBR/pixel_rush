# -*- coding: utf-8 -*-
"""QA v3.277.31: recorte estritamente equivalente de blits RGBA de profundidade.

Ativado SOMENTE pelo entrypoint QA, antes de importar o jogo. Texturas
cacheadas, deslocamento, ordem de camadas, alfa, shaders, física e saves
permanecem os originais. Não ativa RLE, que altera arredondamentos de pixels.
"""
from weakref import WeakKeyDictionary

_INSTALADO = False
_REGIOES = WeakKeyDictionary()


def _blit_visivel(destino, textura, x, y):
    """Evita processar a moldura inteiramente transparente da textura RGBA."""
    recorte = _REGIOES.get(textura)
    if recorte is None:
        recorte = textura.get_bounding_rect(min_alpha=1)
        _REGIOES[textura] = recorte
    if recorte.width and recorte.height:
        return destino.blit(textura, (x + recorte.x, y + recorte.y), recorte)
    return None


def instalar():
    global _INSTALADO
    if _INSTALADO:
        return
    import pixelrush_fase_b_visuais_v3272 as b2
    import pixelrush_fase_b_visuais_v3273 as b3
    import pixelrush_fase_b_visuais_v3274 as b4
    import pixelrush_fase_b_visuais_v3275 as b5
    import pixelrush_fase_b_visuais_v3276 as b6

    def depth_3272(superficie, bioma, deslocamento, peso_noite=0.0, leve=False):
        if leve or bioma not in b2.PALETAS:
            return False
        tex = b2._faixa_distante(bioma)
        noite = max(0.0, min(1.0, float(peso_noite)))
        if noite:
            tex = b2._faixa_noturna(bioma, round(noite * 4) / 4)
        x = (-int(float(deslocamento) * 0.12)) % 900 - 900
        for pos in range(x, superficie.get_width(), 900):
            _blit_visivel(superficie, tex, pos, 305)
        return True

    def depth_3273(superficie, bioma, deslocamento, peso_noite=0.0, leve=False):
        ok = depth_3272(superficie, bioma, deslocamento, peso_noite, leve)
        if not ok:
            return False
        noite = max(0.0, min(1.0, float(peso_noite)))
        tex = (b3._ambiente_noturno(bioma, round(noite * 4))
               if noite else b3._ambiente_segundo_plano(bioma))
        x = (-int(float(deslocamento) * 0.062)) % 720 - 720
        for pos in range(x, superficie.get_width(), 720):
            _blit_visivel(superficie, tex, pos, 262)
        return True

    def depth_3275(superficie, bioma, deslocamento, peso_noite=0, leve=False):
        aplicado = b4.desenhar_profundidade_bioma(
            superficie, bioma, deslocamento, peso_noite, leve)
        if not aplicado or leve or bioma not in b5._CORES:
            return aplicado
        noite = max(0.0, min(1.0, float(peso_noite)))
        tex = (b5._detalhes_noite(bioma, round(noite * 4))
               if noite else b5._detalhes_distantes(bioma))
        x = (-int(float(deslocamento) * 0.094)) % 600 - 600
        for pos in range(x, superficie.get_width(), 600):
            _blit_visivel(superficie, tex, pos, 335)
        return True

    def depth_3276(superficie, bioma, deslocamento, peso_noite=0,
                   leve=False, clima_tipo='limpo'):
        resultado = depth_3275(superficie, bioma, deslocamento, peso_noite, leve)
        if not resultado or leve or bioma not in b6._CORES:
            return resultado
        condicao = b6._tipo_clima(clima_tipo)
        grau = max(0, min(4, round(float(peso_noite) * 4)))
        tex = b6._textura_contextual(bioma, condicao, grau)
        x = (-int(float(deslocamento) * .078)) % 600 - 600
        for pos in range(x, superficie.get_width(), 600):
            _blit_visivel(superficie, tex, pos, 405)
        return True

    # O encadeamento é instalado só nesta instância QA. v3274 conserva
    # a própria renderização, mas passa a chamar a etapa otimizada v3273.
    b2.desenhar_profundidade_bioma = depth_3272
    b3.desenhar_profundidade_bioma = depth_3273
    b4._profundidade = depth_3273
    b5.desenhar_profundidade_bioma = depth_3275
    b6.desenhar_profundidade_bioma = depth_3276
    _INSTALADO = True
