# -*- coding: utf-8 -*-
"""QA 3.277.50: scroll incremental de pixels no caminho REAL da Cidade e strips.

A Cena 2.5D desenha cada chunk na ordem base -> sprites; o wrapper conserva
essa ordem e só reconstrói a base estática de chunks SEM sprites, usando o
scroll horizontal e a faixa recém-exposta. Camadas com sprites e qualquer
estado não suportado usam o método real sem alteração.

Para texturas com alpha não usamos uma segunda composição convencional:
BLEND_RGBA_MAX sobre buffer TRANSPARENTE copia os canais originais e depois
um blit normal aplica o alpha UMA só vez no alvo final (contrato RGBA).

O caminho ainda exige homologação CPU/RSS/RGBA real (flag default OFF).
PIXELRUSH_QA_CITY_INCREMENTAL=1 habilita Cidade no QA.
PIXELRUSH_QA_CLASSIC_INCREMENTAL=1 habilita strips clássicos opacos.
"""
import os
import pygame
from collections import OrderedDict
from functools import wraps
from weakref import WeakKeyDictionary

_INSTALADO=False
_ORIGINAIS={}
_CIDADE=WeakKeyDictionary()
_CLASSICOS=WeakKeyDictionary()
_STATS={'cidade_hit':0,'cidade_rebuild':0,'cidade_strip_px':0,
        'cidade_fallback':0,'classico_frames':0,'classico_fallback':0,
        'limite_surf_cidade_por_cena':2,'habilitado_cidade':False,
        'habilitado_classico':False}


def diagnostico():
    return dict(_STATS,instalado=_INSTALADO,cenas=len(_CIDADE),
                mundos_classicos=len(_CLASSICOS),
                extra_buffer_maximo_cidade_bytes=2*450*500*4)


def _copiar_pixel_exato(buffer,fonte,x,dest_rect):
    """Copia a janela da Surface source SEM alterar canais RGBA intermediários."""
    vis=pygame.Rect(x,0,fonte.get_width(),fonte.get_height())
    area=vis.clip(dest_rect)
    if area.w>0 and area.h>0:
        src=pygame.Rect(area.x-x,area.y,area.w,area.h)
        buffer.blit(fonte,area.topleft,src,special_flags=pygame.BLEND_RGBA_MAX)


def _atualizar_persistente(scene,variant,kind,x):
    from pixelrush_city2_v3115 import WIDTH, SCENE_H
    cache=_CIDADE.get(scene)
    if cache is None:
        cache=OrderedDict()
        _CIDADE[scene]=cache
    chave=(id(variant),kind)
    fonte=scene._scaled_surface(variant,kind)
    if (fonte.get_colorkey() is not None or
            fonte.get_alpha() not in (None,255) or
            fonte.get_height()!=SCENE_H):
        raise ValueError('formato de textura nao suportado em scroll QA')
    assinatura=(id(fonte),fonte.get_size(),fonte.get_flags(),
                fonte.get_alpha())
    entry=cache.get(chave)
    if entry is not None:
        cache.move_to_end(chave)
    # Duas surfaces no máximo, para não crescer memória em trocas de mapas.
    if entry is None or entry[0]!=assinatura:
        quadro=pygame.Surface((WIDTH,SCENE_H),pygame.SRCALPHA)
        quadro.fill((0,0,0,0))
        _copiar_pixel_exato(quadro,fonte,x,quadro.get_rect())
        cache[chave]=(assinatura,int(x),quadro)
        while len(cache)>2:
            cache.popitem(last=False)
        _STATS['cidade_rebuild']+=1
        _STATS['cidade_strip_px']+=WIDTH*SCENE_H
        return quadro
    assinatura,anterior,quadro=entry
    delta=int(x)-anterior
    if delta==0:
        _STATS['cidade_hit']+=1
        return quadro
    if abs(delta)>=WIDTH or abs(delta)>48:
        quadro.fill((0,0,0,0))
        _copiar_pixel_exato(quadro,fonte,x,quadro.get_rect())
        _STATS['cidade_rebuild']+=1
        _STATS['cidade_strip_px']+=WIDTH*SCENE_H
    else:
        quadro.scroll(dx=delta)
        strip=(pygame.Rect(0,0,delta,SCENE_H) if delta>0
               else pygame.Rect(WIDTH+delta,0,-delta,SCENE_H))
        quadro.fill((0,0,0,0),strip)
        _copiar_pixel_exato(quadro,fonte,x,strip)
        _STATS['cidade_hit']+=1
        _STATS['cidade_strip_px']+=abs(delta)*SCENE_H
    cache[chave]=(assinatura,int(x),quadro)
    return quadro


def instalar():
    global _INSTALADO
    if _INSTALADO:
        return
    from pixelrush_city2_v3125 import CityPilotScene
    from pixelrush_world_v3130 import LivingWorld
    _ORIGINAIS['chunk']=CityPilotScene._render_chunk
    _ORIGINAIS['strip']=LivingWorld._blit_strip
    from pixelrush_qa_rolling_v327740 import FaixaPersistenteQA

    @wraps(_ORIGINAIS['chunk'])
    def chunk(self,target,variant,flip,x,frame,night,climate,phase,
              map_kind='image',only_sprites=False):
        if (os.environ.get('PIXELRUSH_QA_CITY_INCREMENTAL','0')!='1'
                or only_sprites or flip or variant.sprites
                or map_kind!='image' or target.get_size()!=(450,500)):
            return _ORIGINAIS['chunk'](self,target,variant,flip,x,frame,
                                       night,climate,phase,map_kind,only_sprites)
        try:
            buffer=_atualizar_persistente(self,variant,map_kind,int(x))
        except (pygame.error,MemoryError,ValueError,TypeError,AttributeError):
            _STATS['cidade_fallback']+=1
            return _ORIGINAIS['chunk'](self,target,variant,flip,x,frame,
                                       night,climate,phase,map_kind,only_sprites)
        # Mesma posição na pilha que o blit de base original; nenhum sprite
        # foi rearranjado, filtros de noite e passagens posteriores intactos.
        target.blit(buffer,(0,0))

    @wraps(_ORIGINAIS['strip'])
    def strip(self,target,fonte):
        if (os.environ.get('PIXELRUSH_QA_CLASSIC_INCREMENTAL','0')!='1'
                or fonte is None or fonte.get_colorkey() is not None
                or bool(fonte.get_flags() & pygame.SRCALPHA)
                or fonte.get_alpha() not in (None,255)):
            return _ORIGINAIS['strip'](self,target,fonte)
        try:
            state=_CLASSICOS.get(self)
            if state is None:
                state=FaixaPersistenteQA(450)
                _CLASSICOS[self]=state
            target.blit(state.gerar(fonte,self._scroll()),(0,230))
            _STATS['classico_frames']+=1
        except (pygame.error,MemoryError,ValueError,TypeError,AttributeError):
            _STATS['classico_fallback']+=1
            return _ORIGINAIS['strip'](self,target,fonte)

    CityPilotScene._render_chunk=chunk
    LivingWorld._blit_strip=strip
    _INSTALADO=True
    _STATS['habilitado_cidade']=os.environ.get('PIXELRUSH_QA_CITY_INCREMENTAL','0')=='1'
    _STATS['habilitado_classico']=os.environ.get('PIXELRUSH_QA_CLASSIC_INCREMENTAL','0')=='1'


def restaurar_para_teste():
    global _INSTALADO
    if _INSTALADO:
        from pixelrush_city2_v3125 import CityPilotScene
        from pixelrush_world_v3130 import LivingWorld
        CityPilotScene._render_chunk=_ORIGINAIS['chunk']
        LivingWorld._blit_strip=_ORIGINAIS['strip']
    _ORIGINAIS.clear()
    _CIDADE.clear()
    _CLASSICOS.clear()
    _INSTALADO=False
