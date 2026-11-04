# -*- coding: utf-8 -*-
"""QA v3.277.76: cronometros observacionais R11 para o 5o quadro.

Wrappers somente em APK QA e somente apos hooks de otimizacao existentes.
Nao cria superficies, nao olha saves nem sensores e nao muda os argumentos,
retornos, ordem de desenho, RNG, excecoes ou pixels. Times sao inclusivos.
"""
import os
from functools import wraps

_INSTALADO=False
_ORIGINAIS=[]

def instalado():
    return _INSTALADO

def _aplicar(classe,metodo,nome):
    from pixelrush_profiler_v3204 import sub_inicio,sub_fim
    original=getattr(classe,metodo)
    local=metodo in classe.__dict__
    @wraps(original)
    def medir(*a,**k):
        sub_inicio(nome)
        try:
            return original(*a,**k)
        finally:
            sub_fim()
    setattr(classe,metodo,medir)
    _ORIGINAIS.append((classe,metodo,original,local))

def instalar():
    global _INSTALADO
    if _INSTALADO or os.environ.get('PIXELRUSH_QA_ANDROID')!='1':
        return False
    if os.environ.get('PIXELRUSH_QA_R11_PASS_TRACE','1')!='1':
        return False
    from pixelrush_world_v3130 import LivingWorld
    from pixelrush_city2_v3125 import CityPilotScene
    from pixelrush_citylife_v3123 import CityLifeDirector
    from pixelrush_renderfx_v3125 import WorldDebris
    try:
        for classe,metodo,nome in (
            (LivingWorld,'draw','r11_world_total'),
            (LivingWorld,'_city_surface','r11_world_cena'),
            (WorldDebris,'draw','r11_world_particulas'),
            (CityPilotScene,'render_scene','r11_city_total'),
            (CityPilotScene,'_render_chunk','r11_city_chunk'),
            (CityPilotScene,'_scaled_surface','r11_city_textura'),
            (CityPilotScene,'_draw_train','r11_city_trem'),
            (CityLifeDirector,'draw_bridge_life','r11_city_ponte'),
            (CityLifeDirector,'draw_suspended_cables','r11_city_cabos'),
            (CityLifeDirector,'draw_pigeons','r11_city_pombos'),
            (CityLifeDirector,'draw_windows_lights','r11_city_janelas'),
            (CityLifeDirector,'draw_atmosphere','r11_city_atmosfera'),
            (CityLifeDirector,'draw_wet_reflections','r11_city_reflexos'),
        ):
            _aplicar(classe,metodo,nome)
    except Exception:
        restaurar_para_teste()
        raise
    _INSTALADO=True
    return True

def restaurar_para_teste():
    global _INSTALADO
    for classe,metodo,original,local in reversed(_ORIGINAIS):
        if local:
            setattr(classe,metodo,original)
        else:
            delattr(classe,metodo)
    _ORIGINAIS.clear()
    _INSTALADO=False
