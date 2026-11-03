# -*- coding: utf-8 -*-
"""QA v3.277.44: batching opcional no render modular REAL (v3128/v3130).

Somente altera chamadas SDL blit->blits de dois tiles RGBA mantendo ordem,
coordenadas, camadas, chunks, alfa e estado do jogo. QA749 ligado por padrao SOMENTE na branch isolada: a equivalencia RGBA
ja foi demonstrada para os mapas de Cidade/Neve/Deserto em testes offline
anteriores; o ganho de CPU ainda precisa ser confirmado antes de homologar.
Desligue imediatamente com PIXELRUSH_QA_MODULAR_BATCH=0.
"""
import os
from functools import wraps

_INSTALLED=False
_ORIGINALS={}
_STATS={'tile_invisivel_culado':0,'blits_lote':0}

def diagnostico():
    return dict(_STATS,instalado=_INSTALLED)


def instalar():
    global _INSTALLED
    if _INSTALLED:
        return
    # Nenhum monkeypatch ou import adicional no caminho normal.
    if os.environ.get('PIXELRUSH_QA_MODULAR_BATCH','1')!='1':
        return
    from pixelrush_biomes2_v3128 import ModularBiomeScene as SnowScene, DEPTH, LW
    from pixelrush_biomes2_v3130 import ModularBiomeScene as CurrentScene, COUNTS
    _ORIGINALS['snow']=SnowScene._draw_layer
    _ORIGINALS['current']=CurrentScene._draw_layer

    @wraps(_ORIGINALS['snow'])
    def _snow_batch(self,dst,layer,travel,kind):
        if self.biome!='neve':
            return _ORIGINALS['snow'](self,dst,layer,travel,kind)
        offset=max(0.,travel)*DEPTH[layer][0]*.5
        first=int(offset//LW);shift=int(offset%LW)
        if shift==0 and dst.get_width()==LW:
            # O segundo tile inicia exatamente fora da area alvo.
            # Evitar lookup, construcao e blit sem alterar nenhum byte.
            dst.blit(self._tile_map(layer,first%4,kind),(0,0))
            _STATS['tile_invisivel_culado']+=1
            return
        tiles=[(self._tile_map(layer,(first+j)%4,kind),(j*LW-shift,0))
               for j in range(2)]
        dst.blits(tiles,doreturn=False)
        _STATS['blits_lote']+=1

    @wraps(_ORIGINALS['current'])
    def _current_batch(self,dst,layer,travel,kind):
        if self.biome!='deserto':
            return _ORIGINALS['current'](self,dst,layer,travel,kind)
        offset=max(0.,travel)*DEPTH[layer][0]*.5
        first=int(offset//LW);shift=int(offset%LW)
        count=COUNTS[layer];stride={'far':5,'mid':7,'near':9}[layer]
        if shift==0 and dst.get_width()==LW:
            dst.blit(self._tile_map(layer,(first*stride)%count,kind),(0,0))
            _STATS['tile_invisivel_culado']+=1
            return
        tiles=[(self._tile_map(layer,((first+j)*stride)%count,kind),
                (j*LW-shift,0)) for j in range(2)]
        dst.blits(tiles,doreturn=False)
        _STATS['blits_lote']+=1

    SnowScene._draw_layer=_snow_batch
    CurrentScene._draw_layer=_current_batch
    _INSTALLED=True


def restaurar_para_teste():
    global _INSTALLED
    if not _INSTALLED:
        return
    from pixelrush_biomes2_v3128 import ModularBiomeScene as SnowScene
    from pixelrush_biomes2_v3130 import ModularBiomeScene as CurrentScene
    SnowScene._draw_layer=_ORIGINALS['snow']
    CurrentScene._draw_layer=_ORIGINALS['current']
    _ORIGINALS.clear()
    _INSTALLED=False
