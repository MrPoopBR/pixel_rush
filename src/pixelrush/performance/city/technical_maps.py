# -*- coding: utf-8 -*-
"""QA787 LAB: culling RGBA exato de geometry/material e fxmask da Cidade.

Somente chunks far/mid, SRCALPHA 32 bits, atlas estaticos previamente
auditados. Sempre restaura clip e preserva 20 slots QA785 e overdraw QA786.
"""
import os
from functools import wraps
import pygame

_INSTALLED=False
_OLD={}
_STATS={'safe_scenes':0,'clip_geo_mat':0,'clip_fxmask':0,
        'rows_culled':0,'enabled':False}

def diagnostico():
    return dict(_STATS, instalado=_INSTALLED)

def _fx_static_bbox(src,variant,w,h,scale):
    if (variant.sprites or not isinstance(src,pygame.Surface) or
        src.get_size()!=(w,h) or src.get_bitsize()!=32 or
        not src.get_flags()&pygame.SRCALPHA or
        src.get_colorkey() is not None or src.get_alpha() not in (None,255)):
        return None
    bbox=src.get_bounding_rect(min_alpha=1)
    if not bbox.width or not bbox.height or bbox.size==(w,h):
        return None
    raw=pygame.image.tobytes(src,'RGBA')
    for y in range(h):
        row=raw[y*w*4:(y+1)*w*4]
        if y<bbox.top or y>=bbox.bottom:
            if any(row):return None
        elif any(row[:bbox.left*4]) or any(row[bbox.right*4:]):
            return None
    # Garantir RGBA zero nos pixels alpha0 antes de liberar crop.
    if any(raw[i] or raw[i+1] or raw[i+2] for i in range(0,len(raw),4)
           if raw[i+3]==0):
        return None
    return pygame.Rect(bbox.x*scale,bbox.y*scale,
                       bbox.width*scale,bbox.height*scale)

def _audit_scene(scene):
    from pixelrush_city2_v3115 import LOW_W,LOW_H,SCALE,SCENE_W,SCENE_H,WIDTH
    scene._qa_tech_cutoffs={}
    scene._qa_tech_sources={}
    scene._qa_tech_fx_bounds={}
    scene._qa_tech_far_ids=frozenset()
    scene._qa_tech_near=None
    scene._qa_tech_active=None
    layers=[l for l in scene.layers if not l.foreground]
    if (len(layers)!=3 or [l.name for l in layers]!=['far','mid','near'] or
        SCENE_W!=LOW_W*SCALE or SCENE_H!=LOW_H*SCALE or SCENE_W<WIDTH):
        return
    near=layers[-1]
    far_ids=frozenset(id(v) for l in layers[:2] for v in l.variants)
    if not far_ids or far_ids.intersection(id(v) for v in near.variants):
        return
    for kind in ('geometry','material'):
        cutoff=0
        sources=[]
        for v in near.variants:
            src=getattr(v,kind,None)
            if (not isinstance(src,pygame.Surface) or
                src.get_size()!=(LOW_W,LOW_H) or src.get_bitsize()!=32 or
                not src.get_flags()&pygame.SRCALPHA or
                src.get_colorkey() is not None or src.get_alpha() not in (None,255)):
                break
            alpha=pygame.image.tobytes(src,'RGBA')[3::4]
            last_nonopaque=max((y for y in range(LOW_H)
                if alpha[y*LOW_W:(y+1)*LOW_W].count(255)!=LOW_W),default=-1)
            cutoff=max(cutoff,(last_nonopaque+1)*SCALE)
            sources.append((v,id(src)))
        if len(sources)==len(near.variants) and cutoff<=SCENE_H-16:
            scene._qa_tech_cutoffs[kind]=cutoff
            scene._qa_tech_sources[kind]=tuple(sources)
    for layer in layers[:2]:
        for v in layer.variants:
            src=getattr(v,'fxmask',None)
            bounds=_fx_static_bbox(src,v,LOW_W,LOW_H,SCALE)
            if bounds is not None:
                scene._qa_tech_fx_bounds[id(v)]=(id(src),bounds)
    scene._qa_tech_far_ids=far_ids
    scene._qa_tech_near=near
    if scene._qa_tech_cutoffs or scene._qa_tech_fx_bounds:
        _STATS['safe_scenes']+=1

def instalar():
    global _INSTALLED
    if _INSTALLED or os.environ.get('PIXELRUSH_QA_CITY_TECH_COVER','0')!='1':
        return
    from pixelrush_city2_v3125 import CityPilotScene
    _OLD.update(init=CityPilotScene.__init__,render=CityPilotScene.render_scene,
                chunk=CityPilotScene._render_chunk)
    @wraps(_OLD['init'])
    def init(self,*args,**kwargs):
        _OLD['init'](self,*args,**kwargs)
        _audit_scene(self)
    @wraps(_OLD['render'])
    def render(self,target,travel,frame,night,climate,phase,
               foreground_only=False,map_kind='image'):
        previous=getattr(self,'_qa_tech_active',None)
        allowed=(not foreground_only and
                 map_kind in ('geometry','material','fxmask') and
                 target.get_size()==(450,500) and target.get_bitsize()==32 and
                 bool(target.get_flags()&pygame.SRCALPHA) and
                 target.get_colorkey() is None)
        if allowed:
            near=getattr(self,'_qa_tech_near',None)
            layers=[l for l in self.layers if not l.foreground]
            allowed=(len(layers)==3 and layers[-1] is near and
                     [l.name for l in layers]==['far','mid','near'])
        if allowed and map_kind in ('geometry','material'):
            sources=self._qa_tech_sources.get(map_kind,())
            allowed=(len(sources)==len(near.variants) and
                all(near.variants[i] is v and
                    id(getattr(v,map_kind,None))==original
                    for i,(v,original) in enumerate(sources)))
        elif allowed:
            allowed=bool(self._qa_tech_fx_bounds)
        self._qa_tech_active=map_kind if allowed else None
        try:
            return _OLD['render'](self,target,travel,frame,night,climate,
                                  phase,foreground_only,map_kind)
        finally:
            self._qa_tech_active=previous
    @wraps(_OLD['chunk'])
    def chunk(self,target,variant,flip,x,frame,night,climate,phase,
              map_kind='image',only_sprites=False):
        if (not only_sprites and not flip and
            map_kind==getattr(self,'_qa_tech_active',None) and
            id(variant) in self._qa_tech_far_ids):
            old_clip=target.get_clip()
            if map_kind=='fxmask' and not variant.sprites:
                meta=self._qa_tech_fx_bounds.get(id(variant))
                if meta is not None and id(getattr(variant,'fxmask',None))==meta[0]:
                    new_clip=old_clip.clip(meta[1].move(x,0))
                    if not new_clip:return
                    if new_clip!=old_clip:
                        target.set_clip(new_clip)
                        _STATS['clip_fxmask']+=1
                        try:
                            return _OLD['chunk'](self,target,variant,flip,x,
                                frame,night,climate,phase,map_kind,only_sprites)
                        finally:
                            target.set_clip(old_clip)
            elif map_kind in ('geometry','material'):
                top=self._qa_tech_cutoffs.get(map_kind)
                if top is not None and old_clip.bottom>top:
                    new_clip=old_clip.clip(pygame.Rect(0,0,450,top))
                    if not new_clip:return
                    target.set_clip(new_clip)
                    _STATS['clip_geo_mat']+=1
                    _STATS['rows_culled']+=old_clip.bottom-top
                    try:
                        return _OLD['chunk'](self,target,variant,flip,x,
                            frame,night,climate,phase,map_kind,only_sprites)
                    finally:
                        target.set_clip(old_clip)
        return _OLD['chunk'](self,target,variant,flip,x,frame,night,
                             climate,phase,map_kind,only_sprites)
    CityPilotScene.__init__=init
    CityPilotScene.render_scene=render
    CityPilotScene._render_chunk=chunk
    _INSTALLED=True
    _STATS['enabled']=True

def restaurar_para_teste():
    global _INSTALLED
    if _INSTALLED:
        from pixelrush_city2_v3125 import CityPilotScene
        CityPilotScene.__init__=_OLD['init']
        CityPilotScene.render_scene=_OLD['render']
        CityPilotScene._render_chunk=_OLD['chunk']
    _OLD.clear()
    _INSTALLED=False
    _STATS.update(safe_scenes=0,clip_geo_mat=0,clip_fxmask=0,
                  rows_culled=0,enabled=False)
