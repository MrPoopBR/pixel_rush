# -*- coding: utf-8 -*-
"""PIXEL RUSH QA765: inventario agregado de caches de Surfaces SDL.

Inventaria sem copiar imagens; um id de Surface conta apenas UMA vez, mesmo
quando emprestada por mundo, atlas ou vista de oclusao. Nao confundir o
inventario de cache com RSS total do processo. Executar fora do frame5.
"""
import pygame

_CACHE_WORLD=('props_cache','cache','fx_cache','normal_cache','material_cache',
              'flow_cache','geometry_cache','_qa_mirror_props',
              '_qa_deform_buffers','_city_surfaces','_qa_damage_layer')
_CACHE_CITY=('_scaled','_night_veils','_qa_cloud_sprite_cache')
_CACHE_MODULAR=('_maps','_composites','_night_tiles')

def inventariar(mundos, fonte=None, max_entradas=8192):
    vistos=set()
    total=0
    acessos=0
    contagem=0
    truncado=False
    por_grupo={}
    def examinar(valor, grupo):
        nonlocal total,acessos,contagem,truncado
        if acessos>=max_entradas:
            truncado=True
            return
        acessos+=1
        if isinstance(valor,pygame.Surface):
            sid=id(valor)
            if sid in vistos:return
            vistos.add(sid)
            memoria=valor.get_pitch()*valor.get_height()
            total+=memoria
            contagem+=1
            por_grupo[grupo]=por_grupo.get(grupo,0)+memoria
        elif isinstance(valor,dict):
            for item in valor.values():
                examinar(item,grupo)
                if truncado:break
        elif isinstance(valor,(tuple,list)):
            for item in valor:
                examinar(item,grupo)
                if truncado:break
    for world in tuple(mundos):
        for campo in _CACHE_WORLD:
            examinar(getattr(world,campo,None),campo)
            if truncado:break
        if truncado:break
        city=getattr(world,'city2',None)
        for campo in _CACHE_CITY:
            examinar(getattr(city,campo,None),'city.'+campo)
            if truncado:break
        if truncado:break
        for biome,scene in tuple(getattr(world,'modular',{}).items()):
            for campo in _CACHE_MODULAR:
                examinar(getattr(scene,campo,None),'modular.'+biome+'.'+campo)
                if truncado:break
            if truncado:break
        if truncado:break
    if fonte is not None and not truncado:
        examinar(fonte,'_SOURCE')
    return {'schema':'pixelrush.qa.memory.v327765','bytes':total,
            'mib':round(total/(1024*1024),3),
            'surfaces_unicas':contagem,'entradas_visitadas':acessos,
            'truncado':truncado,'grupos_bytes':por_grupo}

def cache_em_pressao(relatorio,limite_mib):
    # Relatorio truncado e somente limite inferior: nao inventar RAM.
    return (not relatorio['truncado'] and
            relatorio['bytes']>float(limite_mib)*1024*1024)
