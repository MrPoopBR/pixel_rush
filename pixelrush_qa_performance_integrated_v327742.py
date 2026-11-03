# -*- coding: utf-8 -*-
"""QA v3.277.42: lifecycle, particles, memory, CPU/GPU observability.

Only enabled from the QA Android entrypoint; production/DEV remain untouched.
Pixel-exact: all draws use the SAME pygame primitives, colors and coordinates.
No approximation of animation/time; cached values are frame-independent seeds.
"""
from collections import deque
from functools import wraps
from weakref import WeakSet
import ctypes
import gc
import math
import os
import time

import pygame

_INSTALLED=False
_ORIGINALS={}
_WORLDS=WeakSet()
_SEEDS_RAIN=tuple((i*103,i*71) for i in range(48))
_SEEDS_SNOW=tuple((i,i*61,i*73) for i in range(42))
_SEEDS_SAND=tuple((i*53,i*47) for i in range(36))
_SEEDS_ASH=tuple((i,i*61,i*23) for i in range(24))
_SEEDS_WIND=tuple((i*51,i*18%260) for i in range(16))
_GPU_TRACE=None
_LAST_STATUS={'frames':0,'renderer':None,'cpu_backend':None,'gc_pause_p95_ms':None,
              'gc_events':0,'peak_rss_mib':None,'cache_trim_events':0,
              'cache_budget_mib':560,'gpu_accelerated':False}
_GC_START={}
_GC_PAUSES=deque(maxlen=256)
_FLIP_SAMPLES=deque(maxlen=256)


def _ram_budget_mib():
    """Orcamento agregado adaptativo (sem reduzir a qualidade renderizada)."""
    try:
        with open('/proc/meminfo',encoding='ascii') as handle:
            for line in handle:
                if line.startswith('MemTotal:'):
                    total_mib=int(line.split()[1])/1024.
                    return max(384,min(560,int(total_mib*.25)))
    except (OSError,ValueError,IndexError):
        pass
    return 560


def _memory_mib():
    try:
        with open('/proc/self/status',encoding='ascii') as handle:
            for line in handle:
                if line.startswith('VmRSS:'):
                    return int(line.split()[1])/1024.
    except (OSError,ValueError,IndexError):
        pass
    return None


def _gc_observer(phase,info):
    generation=info.get('generation',-1)
    if phase=='start':
        _GC_START[generation]=time.perf_counter_ns()
    elif phase=='stop':
        start=_GC_START.pop(generation,None)
        if start is not None:
            _GC_PAUSES.append((time.perf_counter_ns()-start)/1e6)
            _LAST_STATUS['gc_events']+=1


class _AndroidTrace:
    def __init__(self):
        self.begin=None
        self.end=None
        if os.environ.get('PIXELRUSH_QA_TRACE','0')!='1':
            return
        if not ('ANDROID_ARGUMENT' in os.environ or os.name=='android'):
            return
        try:
            lib=ctypes.CDLL('libandroid.so')
            active=lib.ATrace_isEnabled
            active.restype=ctypes.c_bool
            if not active():
                return
            self._lib=lib
            self.begin=lib.ATrace_beginSection
            self.begin.argtypes=[ctypes.c_char_p]
            self.end=lib.ATrace_endSection
            self.end.argtypes=[]
        except (OSError,AttributeError):
            self.begin=self.end=None


def _trace(name,fn,*args,**kwargs):
    if _GPU_TRACE is None or _GPU_TRACE.begin is None:
        return fn(*args,**kwargs)
    _GPU_TRACE.begin(name)
    try:
        return fn(*args,**kwargs)
    finally:
        _GPU_TRACE.end()


def _weather_cached(self,surface):
    """Identical particle positions; reuses 166 static (integer) spawn seeds.

    Per-frame sinus, colors, alpha, strokes, cadence and draw order are intact.
    Culling is conservative for primitive diameter/line endpoints only.
    """
    kind=self.climate;f=self.frame
    if kind in ('chuva','tempestade','chuva_acida'):
        storm=kind=='tempestade'
        for xseed,yseed in _SEEDS_RAIN[:48 if storm else 26]:
            x=int((xseed-f*(5.2 if storm else 2.9))%(450+80))-30
            y=230+int((yseed+f*7.7)%(730-230))
            if 0<=x<450+4:
                pygame.draw.line(surface,(153,206,240,106),(x,y),(x-4,y+12),1)
    elif kind in ('neve','nevasca'):
        storm=kind=='nevasca'
        for i,xseed,yseed in _SEEDS_SNOW[:42 if storm else 26]:
            x=int((xseed+math.sin(f*.04+i)*11-f*(2 if storm else .7))%(450+50))-15
            y=230+int((yseed+f*(1.9 if storm else .75))%(730-230))
            rad=1+int(i%3==0)
            if -rad<=x<450+rad:
                pygame.draw.circle(surface,(244,250,255,182),(x,y),rad)
    elif kind in ('areia','tempestade_areia'):
        for xseed,yseed in _SEEDS_SAND:
            x=int((xseed-f*3.2)%(450+50))-18
            y=310+yseed%370
            if x+12>=0 and x<450:
                pygame.draw.line(surface,(233,192,119,88),(x,y),(x+12,y-1),1)
    elif kind in ('cinzas','chuva_meteoros'):
        for i,xseed,yseed in _SEEDS_ASH:
            x=int((xseed-f*.8)%(450+30))-10
            y=230+int((yseed+f*.9)%(730-230))
            rad=2 if i%7==0 else 1
            if -rad<=x<450+rad:
                pygame.draw.circle(surface,(155,117,121,115),(x,y),rad)
    elif kind in ('vento','vento_folhas','polen','brisa_celeste'):
        for xseed,yseed in _SEEDS_WIND:
            x=int((xseed-f*1.6)%(450+35))-15
            y=430+yseed
            if x+8>=0 and x<450:
                pygame.draw.line(surface,(142,215,147,80),(x,y),(x+8,y+2),1)


def _reclaim_inactive_caches():
    """Only after present, and only under Android high-RSS pressure.

    Removes stale cache ENTRIES, never live animation state or textures bound
    to the currently active scene. Reconstructed bitmaps retain original pixels.
    """
    rss=_memory_mib()
    if rss is None:
        return
    previous=_LAST_STATUS['peak_rss_mib'] or 0
    _LAST_STATUS['peak_rss_mib']=round(max(rss,previous),2)
    if rss<=_LAST_STATUS['cache_budget_mib']:
        return
    count=0
    for world in tuple(_WORLDS):
        active=world.biome
        for key in list(world.props_cache):
            if key[0]!=active:
                world.props_cache.pop(key,None)
                count+=1
        # Caches antigos de tiles/atlas tambem compoem o orcamento global.
        # A classe LivingWorld os reconstitui via o mesmo arquivo/algoritmo.
        for atributo in ('cache','fx_cache','normal_cache','material_cache',
                         'flow_cache','geometry_cache'):
            cache=getattr(world,atributo,None)
            if cache:
                for key in tuple(cache):
                    if key!=active:
                        cache.pop(key,None)
                        count+=1
        for attr in ('_qa_mirror_props','_qa_deform_buffers'):
            cache=getattr(world,attr,None)
            if cache:
                for key in list(cache):
                    if isinstance(key,tuple) and key and key[0]!=active:
                        cache.pop(key,None)
                        count+=1
        # Keep the HOT destination buffers. Only cold maps are freed; those
        # are deterministically reconstructed by the original code as needed.
        cold=[key for key in world._city_surfaces
              if key[0] in ('geometry','flow','material','normal','fxmask')]
        for key in cold:
            world._city_surfaces.pop(key,None)
            count+=1
        # O atlas-base de outros biomas fica em _SOURCE global. O atual
        # permanece residente, outros reaparecem byte-identicos via PNG.
        try:
            from pixelrush_world_v3130 import _SOURCE
            for key in tuple(_SOURCE):
                if key!=active:
                    _SOURCE.pop(key,None)
                    count+=1
        except (ImportError,AttributeError):
            pass
        city=getattr(world,'city2',None)
        if city is not None and len(getattr(city,'_scaled',{}))>8:
            while len(city._scaled)>8:
                city._scaled.popitem(last=False)
                count+=1
    if count:
        _LAST_STATUS['cache_trim_events']+=1


def _wrap_world():
    from pixelrush_world_v3130 import LivingWorld
    _ORIGINALS['world_init']=LivingWorld.__init__
    _ORIGINALS['weather']=LivingWorld._weather
    @wraps(LivingWorld.__init__)
    def init(self,*args,**kwargs):
        _ORIGINALS['world_init'](self,*args,**kwargs)
        _WORLDS.add(self)
    LivingWorld.__init__=init
    LivingWorld._weather=_weather_cached


def _wrap_trace_camera():
    from pixelrush_cinema_v3172 import CameraCinematica
    _ORIGINALS['camera_trace']=CameraCinematica.aplicar
    @wraps(_ORIGINALS['camera_trace'])
    def camera(self,*args,**kwargs):
        return _trace(b'pixelrush/camera',_ORIGINALS['camera_trace'],self,*args,**kwargs)
    CameraCinematica.aplicar=camera


def _wrap_flip():
    _ORIGINALS['display_flip']=pygame.display.flip
    @wraps(_ORIGINALS['display_flip'])
    def flip():
        t0=time.perf_counter_ns()
        result=_trace(b'pixelrush/present',_ORIGINALS['display_flip'])
        _FLIP_SAMPLES.append((time.perf_counter_ns()-t0)/1e6)
        _LAST_STATUS['frames']+=1
        if _LAST_STATUS['frames']%180==0:
            _reclaim_inactive_caches()
            try:
                _LAST_STATUS['renderer']=pygame.display.get_driver()
                _LAST_STATUS['cpu_backend']=pygame.transform.get_smoothscale_backend()
            except pygame.error:
                pass
        return result
    pygame.display.flip=flip


def diagnostico():
    out=dict(_LAST_STATUS)
    if _GC_PAUSES:
        s=sorted(_GC_PAUSES)
        out['gc_pause_p95_ms']=round(s[round(.95*(len(s)-1))],3)
    if _FLIP_SAMPLES:
        s=sorted(_FLIP_SAMPLES)
        out['swap_cpu_p95_ms']=round(s[round(.95*(len(s)-1))],3)
    out['trace_android_ativo']=bool(_GPU_TRACE is not None and _GPU_TRACE.begin)
    out['android_gpu_real_medido']=False
    try:
        from pixelrush_qa_camera_native_auto_v327742 import diagnostico as native
        n=native()
        out['nova_camera_ativada']=bool(n['selecionado'])
        out['native_camera']=n
    except (ImportError,RuntimeError):
        out['nova_camera_ativada']=False
    return out


def instalar():
    global _INSTALLED,_GPU_TRACE
    if _INSTALLED:
        return
    _LAST_STATUS['cache_budget_mib']=_ram_budget_mib()
    _GPU_TRACE=_AndroidTrace()
    _wrap_world()
    _wrap_trace_camera()
    _wrap_flip()
    if _gc_observer not in gc.callbacks:
        gc.callbacks.append(_gc_observer)
    _INSTALLED=True


def restaurar_para_teste():
    global _INSTALLED
    if not _INSTALLED:
        return
    from pixelrush_world_v3130 import LivingWorld
    from pixelrush_cinema_v3172 import CameraCinematica
    LivingWorld.__init__=_ORIGINALS['world_init']
    LivingWorld._weather=_ORIGINALS['weather']
    CameraCinematica.aplicar=_ORIGINALS['camera_trace']
    pygame.display.flip=_ORIGINALS['display_flip']
    if _gc_observer in gc.callbacks:
        gc.callbacks.remove(_gc_observer)
    _ORIGINALS.clear()
    _WORLDS.clear()
    _INSTALLED=False
