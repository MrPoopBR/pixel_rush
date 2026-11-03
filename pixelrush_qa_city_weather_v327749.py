# -*- coding: utf-8 -*-
"""QA v3.277.49 — deslocamentos invariantes nas particulas da Cidade REAL.

O sistema meteorologico de LivingWorld._weather nao desenha nos caminhos
Cidade/Neve/Deserto modulares. Esta integracao atua em CityLifeDirector,
instancia real usada pelo compositor CityPilotScene v3125, inclusive quando
a qualidade esta no modo original 1. Ordem, int, modulo, cores e SDL identicos.
"""
import os
from functools import wraps

_INSTALADO=False
_ORIGINALS={}
_STATUS={'atmosfera_quadros':0,'reflexos_quadros':0}
_QA_CITY_SEEDS=os.environ.get('PIXELRUSH_QA_CITY_PARTICLE_SEEDS','1')=='1'
_PARTICLE_SEEDS=tuple((i*67.0,i*37.0,i*41.0,(i%3)*.08) for i in range(12))


def estatisticas():
    return dict(_STATUS,instalado=_INSTALADO)


def instalar():
    global _INSTALADO
    if _INSTALADO:
        return
    if os.environ.get('PIXELRUSH_QA_CITY_WEATHER_FAST','1')!='1':
        return
    import pygame
    from pixelrush_citylife_v3123 import CityLifeDirector
    _ORIGINALS['draw_atmosphere']=CityLifeDirector.draw_atmosphere
    _ORIGINALS['draw_wet_reflections']=CityLifeDirector.draw_wet_reflections

    @wraps(_ORIGINALS['draw_atmosphere'])
    def atmosfera(self,target,travel,frame,night,climate,quality=1):
        # Mantem o numero e os detalhes originais, sem downsample.
        count=4 if not quality else self.MAX_PARTICLES
        rainy=climate in ('chuva','tempestade')
        wind=self.wind
        tw=target.get_width()+20
        deslocamento=travel*.07
        impulso=wind*3
        if count>len(_PARTICLE_SEEDS):
            return _ORIGINALS['draw_atmosphere'](
                self,target,travel,frame,night,climate,quality)
        for i in range(count):
            sx,sy,sp,sv=(_PARTICLE_SEEDS[i] if _QA_CITY_SEEDS
                         else (i*67.0,i*37.0,i*41.0,(i%3)*.08))
            p=(frame*(.42+sv)+sp)
            x=int((sx+p*.42+deslocamento+impulso)%tw)-10
            y=int(352+((sy-p*.53)%102))
            if rainy:
                pygame.draw.line(target,(153,201,227),(x,y),(x-2,y+6),1)
            elif i%4==0:
                if y>427:
                    pygame.draw.circle(target,(146,151,157),(x,y),2)
            elif i%3==0:
                pygame.draw.rect(target,(143,179,119),(x,y,2,1))
            else:
                pygame.draw.rect(target,(171,169,152),(x,y,1,1))
        _STATUS['atmosfera_quadros']+=1

    @wraps(_ORIGINALS['draw_wet_reflections'])
    def reflexos(self,target,travel,frame,night,climate):
        if climate not in ('chuva','tempestade'):
            return
        y0=480
        largura=target.get_width()+30
        deslocamento=travel*.63
        cor=(151,172,185) if night<.4 else (214,171,133)
        forte=night>.25
        for i in range(8):
            x=int((i*71-deslocamento)%largura)-15
            w=5+(i%3)*3
            pygame.draw.line(target,cor,(x,y0+i%3*4),(x+w,y0+i%3*4),1)
            if forte and i%2==0:
                pygame.draw.line(target,(218,191,144),(x+2,y0+8),(x+w-1,y0+8),1)
        _STATUS['reflexos_quadros']+=1

    CityLifeDirector.draw_atmosphere=atmosfera
    CityLifeDirector.draw_wet_reflections=reflexos
    _INSTALADO=True


def restaurar_para_teste():
    global _INSTALADO
    if not _INSTALADO:
        return
    from pixelrush_citylife_v3123 import CityLifeDirector
    for nome,original in _ORIGINALS.items():
        setattr(CityLifeDirector,nome,original)
    _ORIGINALS.clear()
    _STATUS.update(atmosfera_quadros=0,reflexos_quadros=0)
    _INSTALADO=False
