# -*- coding: utf-8 -*-
"""QA786 LAB: elimina exclusivamente blits encobertos por near 100% opaco.

Somente normal/flow, apenas depois de validar TODOS os pixels RGBA de
TODOS os atlas near (inclusive alpha interior), nao altera sprites da imagem,
luzes, fisica, ordem das camadas near, nem mapa geometry/fxmask/material.
Gate por instancia/identidade. Reversivel por PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW=0.
"""
import os
from functools import wraps
import pygame

_INSTALLED=False
_OLD={}
_STATS={'scenes_checked':0,'scenes_safe':0,'chunks_hidden':0,'original_chunks':0}

def diagnostico():
    return dict(_STATS,instalado=_INSTALLED)

def _check_scene(scene):
    from pixelrush_city2_v3115 import LOW_W, LOW_H, SCALE, SCENE_W, SCENE_H, WIDTH
    _STATS['scenes_checked']+=1
    scene._qa_opaque_maps_pass=None
    scene._qa_opaque_maps_srcs={}
    scene._qa_occluded_variant_ids=frozenset()
    layers=[layer for layer in scene.layers if not layer.foreground]
    if (len(layers)!=3 or [layer.name for layer in layers]!=['far','mid','near']
            or SCENE_W!=LOW_W*SCALE or SCENE_H!=LOW_H*SCALE
            or SCENE_W<WIDTH):
        return
    near=layers[-1]
    far_mid=frozenset(id(v) for l in layers[:2] for v in l.variants)
    if not far_mid or any(id(v) in far_mid for v in near.variants):
        return
    srcs={}
    for kind in ('normal','flow'):
        entries=[]
        for variant in near.variants:
            src=getattr(variant,kind,None)
            if (not isinstance(src,pygame.Surface) or
                    src.get_size()!=(LOW_W,LOW_H) or
                    src.get_bitsize()!=32 or
                    not src.get_flags()&pygame.SRCALPHA or
                    src.get_alpha() not in (None,255) or
                    src.get_colorkey() is not None):
                entries=[];break
            raw=pygame.image.tobytes(src,'RGBA')
            alpha=raw[3::4]
            if alpha.count(255)!=len(alpha):
                entries=[];break
            entries.append((variant,id(src)))
        if entries and len(entries)==len(near.variants):
            srcs[kind]=tuple(entries)
    if not srcs:
        return
    scene._qa_opaque_maps_srcs=srcs
    scene._qa_occluded_variant_ids=far_mid
    scene._qa_opaque_near_layer=near
    _STATS['scenes_safe']+=1

def instalar():
    global _INSTALLED
    if _INSTALLED or os.environ.get('PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW','0')!='1':
        return
    from pixelrush_city2_v3125 import CityPilotScene
    _OLD['init']=CityPilotScene.__init__
    _OLD['render']=CityPilotScene.render_scene
    _OLD['chunk']=CityPilotScene._render_chunk
    @wraps(_OLD['init'])
    def init(self,*args,**kwargs):
        _OLD['init'](self,*args,**kwargs)
        _check_scene(self)
    @wraps(_OLD['render'])
    def render(self,target,travel,frame,night,climate,phase,
               foreground_only=False,map_kind='image'):
        old=getattr(self,'_qa_opaque_maps_pass',None)
        eligible=(not foreground_only and map_kind in ('normal','flow')
            and target.get_size()==(450,500)
            and target.get_bitsize()==32
            and bool(target.get_flags()&pygame.SRCALPHA))
        if eligible:
            entries=getattr(self,'_qa_opaque_maps_srcs',{}).get(map_kind)
            near=getattr(self,'_qa_opaque_near_layer',None)
            if (entries is None or
                near not in self.layers or
                any(layer is not near and not layer.foreground
                    for layer in self.layers[self.layers.index(near)+1:])
                if near is not None else True):
                eligible=False
            elif len(near.variants)!=len(entries) or any(
                near.variants[i] is not variant or
                id(getattr(variant,map_kind,None))!=ident
                for i,(variant,ident) in enumerate(entries)):
                eligible=False
        self._qa_opaque_maps_pass=map_kind if eligible else None
        try:
            return _OLD['render'](self,target,travel,frame,night,climate,
                                   phase,foreground_only,map_kind)
        finally:
            self._qa_opaque_maps_pass=old
    @wraps(_OLD['chunk'])
    def chunk(self,target,variant,flip,x,frame,night,climate,phase,
              map_kind='image',only_sprites=False):
        if (not only_sprites and not flip and
                map_kind==getattr(self,'_qa_opaque_maps_pass',None) and
                id(variant) in getattr(self,'_qa_occluded_variant_ids',())):
            _STATS['chunks_hidden']+=1
            return
        _STATS['original_chunks']+=1
        return _OLD['chunk'](self,target,variant,flip,x,frame,night,climate,
                             phase,map_kind,only_sprites)
    CityPilotScene.__init__=init
    CityPilotScene.render_scene=render
    CityPilotScene._render_chunk=chunk
    _INSTALLED=True

def restaurar_para_teste():
    global _INSTALLED
    if _INSTALLED:
        from pixelrush_city2_v3125 import CityPilotScene
        CityPilotScene.__init__=_OLD['init']
        CityPilotScene.render_scene=_OLD['render']
        CityPilotScene._render_chunk=_OLD['chunk']
    _OLD.clear()
    _STATS.update(scenes_checked=0,scenes_safe=0,chunks_hidden=0,original_chunks=0)
    _INSTALLED=False
