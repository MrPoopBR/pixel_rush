# -*- coding: utf-8 -*-
"""QA 3.277.50: scroll incremental de pixels no caminho REAL da Cidade e strips.

A Cena 2.5D desenha cada chunk na ordem base -> sprites. A rota inicial
QA753 limita o cache incremental aos chunks ESTATICOS far/mid; os chunks
animados de near seguem intactos. Um modo de laboratório 'all' tambem
preserva sprites pelo metodo original only_sprites=True. O cache trabalha
apenas com canais SRCALPHA de formato exato e no maximo duas surfaces
por instancia da Cidade, sem nunca mudar fisica ou numero de sprites.

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

# Configuradas no boot QA, sem acessar getenv durante os chunks do 5o frame.
_QA_SCROLL_INIT_CLEAR=os.environ.get('PIXELRUSH_QA_SCROLL_INIT_CLEAR','1')=='1'
_QA_SCROLL_JUMP_DIRECT=os.environ.get('PIXELRUSH_QA_SCROLL_JUMP_DIRECT','1')=='1'
# Quando so uma faixa estreita da textura original aparece, preencher
# cache + blitar buffer e mais lento que o blit fonte, sem ganho visual.
# Padrao experimental, scroll geral permanece OFF.
_QA_SCROLL_MIN_COVER=max(0,min(450,int(
    os.environ.get('PIXELRUSH_QA_SCROLL_MIN_COVER','192'))))

_INSTALADO=False
_ORIGINAIS={}
_CIDADE=WeakKeyDictionary()
_CLASSICOS=WeakKeyDictionary()
_STATS={'cidade_hit':0,'cidade_rebuild':0,'cidade_strip_px':0,
        'cidade_fallback':0,'classico_frames':0,'classico_fallback':0,
        'limite_surf_cidade_por_cena':2,'habilitado_cidade':False,
        'habilitado_classico':False,'cidade_rejeitado_formato':0,
        'cidade_sem_cobertura':0,'cidade_sprite_direto':0,
        'cidade_cache_descartado':0,'modo_cidade':'off',
        'cidade_salto_direto':0,'cidade_init_sem_fill':0,
        'cidade_blit_cobertura_px':0,'cidade_cobertura_direta':0,
        'cidade_chunk_sem_base':0,'cidade_rle_direto':0}


def diagnostico():
    return dict(_STATS,instalado=_INSTALADO,cenas=len(_CIDADE),
                mundos_classicos=len(_CLASSICOS),
                extra_buffer_maximo_cidade_bytes=2*450*500*4)


def tem_cache_cena(scene):
    return scene is not None and bool(_CIDADE.get(scene))


def descartar_cena(scene):
    """Liberar o cache incremental de uma Cidade inativa sob RSS alto."""
    if scene is not None and scene in _CIDADE:
        cache=_CIDADE.pop(scene)
        qtd=len(cache)
        cache.clear()
        _STATS['cidade_cache_descartado']+=qtd
        return qtd
    return 0


def _copiar_pixel_exato(buffer,fonte,x,dest_rect):
    """Copia a janela da Surface source SEM alterar canais RGBA intermediários."""
    vis=pygame.Rect(x,0,fonte.get_width(),fonte.get_height())
    area=vis.clip(dest_rect)
    if area.w>0 and area.h>0:
        src=pygame.Rect(area.x-x,area.y,area.w,area.h)
        buffer.blit(fonte,area.topleft,src,special_flags=pygame.BLEND_RGBA_MAX)


def _atualizar_persistente(scene,variant,kind,x):
    from pixelrush_city2_v3115 import WIDTH, SCENE_W, SCENE_H
    fonte=scene._scaled_surface(variant,kind)
    # QA755: SDL-RLE faz skip de alpha0 no blit original e pode manter
    # RGB oculto do target; RGBA_MAX -> buffer -> blit altera tais bytes.
    # RLEACCELOK aparece ja em set_alpha(...RLEACCEL), mesmo ANTES
    # do primeiro blit (quando RLEACCEL ainda nao aparece).
    # Para preservar bytes exatos, RLE deve ir DIRETO a _render_chunk.
    rle_mask=pygame.RLEACCEL | getattr(pygame,'RLEACCELOK',0)
    if fonte.get_flags() & rle_mask:
        _STATS['cidade_rle_direto']+=1
        raise ValueError('fonte SDL-RLE requer blit direto para RGB oculto')
    if (fonte.get_colorkey() is not None or
            fonte.get_alpha() not in (None,255) or
            fonte.get_size()!=(SCENE_W,SCENE_H) or
            not bool(fonte.get_flags() & pygame.SRCALPHA) or
            fonte.get_bitsize()!=32):
        _STATS['cidade_rejeitado_formato']+=1
        raise ValueError('scroll exige RGBA 32bits, origem 900x500 sem colorkey')
    # Nao guardar sequer um OrderedDict para a cena quando a fonte RLE
    # nao passa no gate. No quarto/quinto quadro isso economiza churn.
    cache=_CIDADE.get(scene)
    if cache is None:
        cache=OrderedDict()
        _CIDADE[scene]=cache
    chave=(id(variant),kind)
    assinatura=(id(fonte),fonte.get_size(),fonte.get_flags(),
                fonte.get_alpha())
    entry=cache.get(chave)
    if entry is not None:
        cache.move_to_end(chave)
    # Duas surfaces no máximo, para não crescer memória em trocas de mapas.
    if entry is None or entry[0]!=assinatura:
        quadro=pygame.Surface((WIDTH,SCENE_H),pygame.SRCALPHA,32,
                               masks=fonte.get_masks())
        # QA754: nova Surface SRCALPHA nasce transparente em SDL2; nao
        # fazer outra escrita de 450x500 antes da primeira faixa. Mantem
        # fallback manual selecionavel e sem alterar blending posterior.
        if not _QA_SCROLL_INIT_CLEAR:
            quadro.fill((0,0,0,0))
        else:
            _STATS['cidade_init_sem_fill']+=1
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
        if _QA_SCROLL_JUMP_DIRECT:
            # QA754: reconstruir/limpar 450x500 e depois blitar outro
            # 450x500 seria trabalho E RAM de banda extras. Em saltos
            # grandes usar blit DIRETO, com bytes e ordem iguais.
            cache.pop(chave,None)
            _STATS['cidade_salto_direto']+=1
            return None
        # Fallback exato QA753 selecionado antes do import.
        quadro.fill((0,0,0,0))
        _copiar_pixel_exato(quadro,fonte,x,quadro.get_rect())
        cache[chave]=(assinatura,int(x),quadro)
        _STATS['cidade_rebuild']+=1
        _STATS['cidade_strip_px']+=WIDTH*SCENE_H
        return quadro
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
    # Sem homologacao/flags: NAO monkeypatchar o frame real nem inserir
    # consultas a variaveis de ambiente no caminho quente do quinto quadro.
    habilita_cidade=os.environ.get('PIXELRUSH_QA_CITY_INCREMENTAL','0')=='1'
    habilita_classico=os.environ.get('PIXELRUSH_QA_CLASSIC_INCREMENTAL','0')=='1'
    # 'static' preserva o movimento e animações near inteiramente no
    # renderizador direto; 'all' habilita o antigo experimento com sprites.
    escopo=os.environ.get('PIXELRUSH_QA_CITY_SCROLL_SCOPE','static')
    if escopo not in ('static','all'):
        escopo='static'
    if not (habilita_cidade or habilita_classico):
        _STATS['habilitado_cidade']=False
        _STATS['habilitado_classico']=False
        return
    from pixelrush_city2_v3125 import CityPilotScene
    from pixelrush_world_v3130 import LivingWorld
    _ORIGINAIS['chunk']=CityPilotScene._render_chunk
    _ORIGINAIS['strip']=LivingWorld._blit_strip
    from pixelrush_qa_rolling_v327740 import FaixaPersistenteQA

    @wraps(_ORIGINAIS['chunk'])
    def chunk(self,target,variant,flip,x,frame,night,climate,phase,
              map_kind='image',only_sprites=False):
        if (not habilita_cidade or only_sprites or flip
                or map_kind!='image' or target.get_size()!=(450,500)):
            return _ORIGINAIS['chunk'](self,target,variant,flip,x,frame,
                                       night,climate,phase,map_kind,only_sprites)
        # Base do chunk coberta por [inicio,fim); sprites podem sair
        # dos seus limites, portanto so o passe base pode ser pulado.
        inicio=max(0,int(x))
        fim=min(450,int(x)+900)
        largura=max(0,fim-inicio)
        if largura==0:
            _STATS['cidade_sem_cobertura']+=1
            if variant.sprites:
                _STATS['cidade_chunk_sem_base']+=1
                return _ORIGINAIS['chunk'](self,target,variant,flip,x,frame,
                                           night,climate,phase,map_kind,True)
            return
        if largura<_QA_SCROLL_MIN_COVER:
            _STATS['cidade_cobertura_direta']+=1
            return _ORIGINAIS['chunk'](self,target,variant,flip,x,frame,
                                       night,climate,phase,map_kind,only_sprites)
        if variant.sprites and escopo=='static':
            _STATS['cidade_sprite_direto']+=1
            return _ORIGINAIS['chunk'](self,target,variant,flip,x,frame,
                                       night,climate,phase,map_kind,only_sprites)
        try:
            buffer=_atualizar_persistente(self,variant,map_kind,int(x))
        except (pygame.error,MemoryError,ValueError,TypeError,AttributeError):
            _STATS['cidade_fallback']+=1
            return _ORIGINAIS['chunk'](self,target,variant,flip,x,frame,
                                       night,climate,phase,map_kind,only_sprites)
        # Em mudanca grande de posicao, acesso direto ao atlas evita uma
        # limpeza e uma copia de framebuffer completo.
        if buffer is None:
            return _ORIGINAIS['chunk'](self,target,variant,flip,x,frame,
                                       night,climate,phase,map_kind,only_sprites)
        # QA755: BLIT SOMENTE NA COBERTURA ORIGINAL [inicio,fim)!
        # SDL pode reescrever RGB oculto de destino alpha0 se a origem
        # SRCALPHA tem alpha0. Pixels FORA do chunk nao podem ser tocados:
        # buffer translucido 450x500 inteiro seria regressao RGBA real.
        # Dentro da area, buffer contem RGB+alpha originais via RGBA_MAX.
        target.blit(buffer,(inicio,0),(inicio,0,largura,500))
        _STATS['cidade_blit_cobertura_px']+=largura*500
        if variant.sprites:
            return _ORIGINAIS['chunk'](
                self,target,variant,flip,x,frame,night,climate,phase,
                map_kind,True)

    @wraps(_ORIGINAIS['strip'])
    def strip(self,target,fonte):
        if (not habilita_classico
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
    _STATS['habilitado_cidade']=habilita_cidade
    _STATS['habilitado_classico']=habilita_classico
    _STATS['modo_cidade']=escopo if habilita_cidade else 'off'


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
