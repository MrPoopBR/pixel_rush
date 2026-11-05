# -*- coding: utf-8 -*-
"""QA759: restaura metadados de atlas City sem reconstruir nem trocar a arte.

A classe CityPilotScene v3122 redefine __init__ sem chamar o v3118,
mas herda _render_chunk/_scaled_surface que leem os metadados do v3118.
Este hook roda no bootstrap real da Cidade, somente depois de montar os
chunks da versao FINAL. Falha de metadados deixa renderer SDL original.
"""
import hashlib
import os
from functools import wraps

import pygame

_INSTALLED=False
_ORIGINAL=None
_HAD_LOCAL_INIT=False
_STATS={'cenas':0,'uniformes':0,'aliases':0,'vazios':0,'recortes':0,'falhas':0}


def diagnostico():
    return dict(_STATS,instalado=_INSTALLED)


def _preparar(scene):
    from pixelrush_city2_v3118 import (
        _QA_SKIP_EMPTY_BASE, _QA_ALPHA_BOUNDS,
        _QA_DEDUP_TECH_SCALED, _QA_UNIFORM_TECH_FILL)
    from pixelrush_city2_v3115 import LOW_W, LOW_H, SCALE
    # Estes atributos sao referenciados pelo v3118 herdado e nao existem
    # quando o construtor mais recente v3122 contorna aquele __init__.
    scene._qa_cloud_sprite_cache={}
    scene._qa_cloud_use_cache=(os.environ.get('PIXELRUSH_QA_CLOUD_CACHE','0')=='1')
    scene._qa_empty_base_maps=set()
    scene._qa_alpha_bounds={}
    scene._qa_scaled_alias={}
    scene._qa_scaled_alias_hits=0
    scene._qa_uniform_tech={}
    scene._qa_uniform_tech_hits=0
    if os.environ.get('PIXELRUSH_QA_CITY_BOOTSTRAP_METADATA','1')!='1':
        return

    iguais={}
    for layer in scene.layers:
        for variant in layer.variants:
            for kind in ('image','geometry','fxmask','normal','material','flow'):
                tex=getattr(variant,kind,None)
                if tex is None:
                    continue
                try:
                    if (_QA_UNIFORM_TECH_FILL and
                            kind in ('geometry','fxmask','normal','material','flow') and
                            tex.get_size()==(LOW_W,LOW_H) and
                            tex.get_bitsize()==32 and
                            tex.get_pitch()==LOW_W*4 and
                            tex.get_flags() & pygame.SRCALPHA and
                            tex.get_colorkey() is None and
                            tex.get_alpha() in (None,255)):
                        color=tex.get_at((0,0))
                        if color.a==255:
                            pixel=memoryview(tex.get_view('0'))
                            try:
                                first=pixel[:4].tobytes()
                                if pixel.tobytes()==first*(LOW_W*LOW_H):
                                    scene._qa_uniform_tech[
                                        (id(variant),kind)]=(id(tex),tuple(color))
                            finally:
                                pixel.release()
                    if (_QA_DEDUP_TECH_SCALED and
                            kind in ('geometry','fxmask','normal','material','flow') and
                            tex.get_bitsize()==32):
                        fmt=(kind,tex.get_size(),tex.get_flags(),tex.get_masks(),
                             tex.get_alpha(),tex.get_colorkey())
                        raw=memoryview(tex.get_view('0'))
                        try:
                            digest=hashlib.blake2b(raw,digest_size=16).digest()
                            chave=(fmt,digest)
                            igual=False
                            for orig_variant,orig_tex in iguais.get(chave,()):
                                other=memoryview(orig_tex.get_view('0'))
                                try:
                                    valido=raw==other
                                finally:
                                    other.release()
                                if valido:
                                    scene._qa_scaled_alias[(id(variant),kind)]=(
                                        id(tex),(id(orig_variant),kind))
                                    igual=True
                                    break
                            if not igual:
                                iguais.setdefault(chave,[]).append((variant,tex))
                        finally:
                            raw.release()
                    if (not (_QA_SKIP_EMPTY_BASE or _QA_ALPHA_BOUNDS) or
                            not tex.get_flags() & pygame.SRCALPHA or
                            tex.get_colorkey() is not None or
                            tex.get_alpha() not in (None,255)):
                        continue
                    bbox=tex.get_bounding_rect(min_alpha=1)
                    key=(id(variant),kind,id(tex))
                    if bbox.width==0 or bbox.height==0:
                        if _QA_SKIP_EMPTY_BASE:
                            scene._qa_empty_base_maps.add(key)
                    elif (_QA_ALPHA_BOUNDS and
                            tex.get_size()==(LOW_W,LOW_H) and
                            bbox.size!=(LOW_W,LOW_H)):
                        scene._qa_alpha_bounds[key]=(
                            bbox.x*SCALE,bbox.y*SCALE,
                            bbox.w*SCALE,bbox.h*SCALE)
                except (pygame.error,BufferError,ValueError,TypeError,
                        MemoryError,AttributeError):
                    # Sem prova de bits idênticos nao aplicar atalho.
                    _STATS['falhas']+=1
                    continue
    _STATS['uniformes']+=len(scene._qa_uniform_tech)
    _STATS['aliases']+=len(scene._qa_scaled_alias)
    _STATS['vazios']+=len(scene._qa_empty_base_maps)
    _STATS['recortes']+=len(scene._qa_alpha_bounds)


def instalar():
    global _INSTALLED,_ORIGINAL,_HAD_LOCAL_INIT
    if _INSTALLED:
        return
    from pixelrush_city2_v3125 import CityPilotScene
    _ORIGINAL=CityPilotScene.__init__
    _HAD_LOCAL_INIT='__init__' in CityPilotScene.__dict__
    @wraps(_ORIGINAL)
    def init(self,*args,**kwargs):
        _ORIGINAL(self,*args,**kwargs)
        # QA768: somente atlas tecnicos finalizados, antes de indexar
        # as identidades dos tiles em _preparar. Tabela global weak,
        # igualdade RAW; se indisponivel, original continua intacto.
        from pixelrush_qa_city_intern_v327768 import compartilhar
        compartilhar(self)
        _preparar(self)
        _STATS['cenas']+=1
    CityPilotScene.__init__=init
    _INSTALLED=True


def restaurar_para_teste():
    global _INSTALLED,_ORIGINAL,_HAD_LOCAL_INIT
    if not _INSTALLED:
        return
    from pixelrush_city2_v3125 import CityPilotScene
    if _HAD_LOCAL_INIT:
        CityPilotScene.__init__=_ORIGINAL
    else:
        delattr(CityPilotScene,'__init__')
    from pixelrush_qa_city_intern_v327768 import restaurar_para_teste as limpar_intern
    limpar_intern()
    _ORIGINAL=None
    _HAD_LOCAL_INIT=False
    _INSTALLED=False
