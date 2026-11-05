# -*- coding: utf-8 -*-
"""PIXEL RUSH QA753 — cortar passes comprovadamente inertes no render REAL.

- Cidade v3125: o foreground 'fg' eh pintado com atlas RGBA totalmente
  transparente e zero sprites. Nao fazer renderizar um tile 900x500 inerte.
  A verificacao da transparencia ocorre UMA unica vez por cena. Se a arte
  mudar ou nao for inteiramente transparente, delegar ao metodo original.
  O campo _last_state continua sendo atualizado como no original.
- LivingWorld: quando o strip inteiro visivel cabe em UM blit, chamar
  Surface.blit em vez de construir lista + Surface.blits. Em 2+ blits,
  preservar integralmente a rotina anterior. Nenhum pixel sai do lugar.

Nao altera velocidade, camera, caches 5:1, HUD, RNG, sprites, pets ou saves.
Duas flags, avaliadas no boot: PIXELRUSH_QA_CITY_EMPTY_FG=0 e
PIXELRUSH_QA_STRIP_ONE_BLIT=0, restauram os caminhos originais.
"""
import os
import pygame
from functools import wraps
from weakref import WeakKeyDictionary

_INSTALADO=False
_ORIGINAIS={}
_FG_VAZIO=WeakKeyDictionary()
_STATUS={'fg_pulado':0,'fg_original':0,'fg_cenas_verificadas':0,
         'strip_um_blit':0,'strip_original':0}

def diagnostico():
    return dict(_STATUS,instalado=_INSTALADO,
                cenas_verificadas=len(_FG_VAZIO),
                afirmacao_fps_android=False)

def _verificar_fg_vazio(scene):
    # Verificar ao criar a cena, nao no quinto quadro de render. Os
    # ChunkVariants e suas Surfaces sao criados uma vez e imutaveis.
    layers=tuple(layer for layer in scene.layers if layer.foreground)
    empty=bool(layers) and all(len(layer.variants)>0 for layer in layers)
    if empty:
        empty=all(
            not variant.sprites
            and bool(variant.image.get_flags() & pygame.SRCALPHA)
            and variant.image.get_colorkey() is None
            and variant.image.get_bounding_rect(min_alpha=1).width==0
            for layer in layers for variant in layer.variants)
    _FG_VAZIO[scene]=empty
    _STATUS['fg_cenas_verificadas']+=1
    return empty


def instalar():
    global _INSTALADO
    if _INSTALADO:
        return
    faz_fg=os.environ.get('PIXELRUSH_QA_CITY_EMPTY_FG','1')=='1'
    faz_strip=os.environ.get('PIXELRUSH_QA_STRIP_ONE_BLIT','1')=='1'
    if not (faz_fg or faz_strip):
        return
    from pixelrush_city2_v3125 import CityPilotScene
    from pixelrush_world_v3130 import LivingWorld, WIDTH, TOP
    if faz_fg:
        _ORIGINAIS['city_init']=CityPilotScene.__init__
        _ORIGINAIS['city_init_local']='__init__' in CityPilotScene.__dict__
        @wraps(_ORIGINAIS['city_init'])
        def init(self,*args,**kwargs):
            _ORIGINAIS['city_init'](self,*args,**kwargs)
            _verificar_fg_vazio(self)
        CityPilotScene.__init__=init
        _ORIGINAIS['render_scene']=CityPilotScene.render_scene
        @wraps(_ORIGINAIS['render_scene'])
        def render(self,target,travel,frame,night,climate,phase,
                   foreground_only=False,map_kind='image'):
            if foreground_only and map_kind=='image':
                empty=_FG_VAZIO.get(self)
                if empty is None:
                    # Cena criada ANTES da instalação: fallback seguro,
                    # verifica uma única vez e reutiliza o resultado.
                    empty=_verificar_fg_vazio(self)
                if empty:
                    self._last_state=(travel,frame,night,climate,phase)
                    _STATUS['fg_pulado']+=1
                    return
            _STATUS['fg_original']+=1
            return _ORIGINAIS['render_scene'](
                self,target,travel,frame,night,climate,phase,
                foreground_only,map_kind)
        CityPilotScene.render_scene=render
    if faz_strip:
        _ORIGINAIS['strip']=LivingWorld._blit_strip
        @wraps(_ORIGINAIS['strip'])
        def strip(self,target,fonte):
            if fonte is None:
                return _ORIGINAIS['strip'](self,target,fonte)
            width=fonte.get_width()
            # Mesmo off e mesmo primeiro blit da versao real.
            # src width <=0 ja falharia no original: nao esconder erros.
            if width>0:
                off=self._scroll()%width
                if width-off>=WIDTH:
                    target.blit(fonte,(-off,TOP))
                    _STATUS['strip_um_blit']+=1
                    return
            _STATUS['strip_original']+=1
            return _ORIGINAIS['strip'](self,target,fonte)
        LivingWorld._blit_strip=strip
    _INSTALADO=True

def restaurar_para_teste():
    global _INSTALADO
    if _INSTALADO:
        from pixelrush_city2_v3125 import CityPilotScene
        from pixelrush_world_v3130 import LivingWorld
        if 'render_scene' in _ORIGINAIS:
            CityPilotScene.render_scene=_ORIGINAIS['render_scene']
        if 'city_init' in _ORIGINAIS:
            if _ORIGINAIS.get('city_init_local'):
                CityPilotScene.__init__=_ORIGINAIS['city_init']
            else:
                delattr(CityPilotScene,'__init__')
        if 'strip' in _ORIGINAIS:
            LivingWorld._blit_strip=_ORIGINAIS['strip']
    _ORIGINAIS.clear()
    _FG_VAZIO.clear()
    _STATUS.update((k,0) for k in _STATUS)
    _INSTALADO=False
