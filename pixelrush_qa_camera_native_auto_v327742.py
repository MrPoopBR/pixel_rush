# -*- coding: utf-8 -*-
"""PIXEL RUSH QA v3.277.42: selecao nativa ARM/NEON em camera real.

Integrada ao ponto de instalacao QA; so troca a camera por native quando a
biblioteca existe, e pixels RGBA e benchmark da imagem REAL sao aprovados.
Sem alterar fisica, animacao do zoom, coordenadas ou estado do jogador.
Falhas caem de volta no smoothscale original com estado ja atualizado.
"""
import os
import statistics
import time
from functools import wraps

import pygame

_INSTALLED=False
_ORIGINAL=None
_NATIVE=None
_REPORT={'status':'nao_avaliado','selecionado':False,
         'pixels_exatos':None,'teste_real':False,
         'backend':None,'original_p50_ms':None,'native_p50_ms':None,
         'fallbacks':0,'frames_native':0}

def diagnostico():
    return dict(_REPORT)


def _load_native():
    global _NATIVE
    if _NATIVE is not None:
        return _NATIVE
    from pixelrush_qa_crop_native_v327741 import Crop32QA
    # APK: lib nativa em lib/arm64-v8a. Desktop: caminho absoluto fornecido.
    lib=os.environ.get('PIXELRUSH_QA_NATIVE_CAMERA_LIB',
                       'libpixelrush_camera_crop_v327741.so')
    try:
        _NATIVE=Crop32QA(lib)
        return _NATIVE
    except (OSError,RuntimeError,ValueError):
        return None


def _geometria_camera(self,imagem,jogador,velocidade,momento,ativo):
    if not ativo or jogador is None:
        self.zoom*=.9
        return None
    alvo_zoom=.034 if momento else min(.025,max(0.,(velocidade-8.)*.0018))
    self.zoom+=(alvo_zoom-self.zoom)*.045
    p_y=0. if getattr(jogador,'no_chao',True) else max(
        -10.,min(10.,(jogador.rect.centery-600)*.06))
    self.foco_y+=(p_y-self.foco_y)*.065
    if self.zoom<.002:
        return None
    w,h=imagem.get_size()
    ex=max(1,int(w*self.zoom));ey=max(1,int(h*self.zoom))
    tamanho=(w+ex*2,h+ey*2)
    sy=max(0,min(2*ey,ey+int(self.foco_y)))
    return tamanho,(ex,sy)


def _cpu_depois_do_fallback(self,imagem,geometria):
    tamanho,recorte=geometria
    if self._cache_zoom_tamanho != tamanho or self._cache_zoom_expandido is None:
        self._cache_zoom_expandido=pygame.Surface(tamanho).convert(imagem)
        self._cache_zoom_tamanho=tamanho
    expandida=pygame.transform.smoothscale(imagem,tamanho,
                                          self._cache_zoom_expandido)
    return expandida.subsurface((recorte[0],recorte[1],*imagem.get_size()))


def _verificar_primeiro_frame(imagem,camera,jogador,velocidade,momento,ativo):
    native=_load_native()
    if native is None:
        _REPORT['status']='biblioteca_nativa_ausente'
        return False
    if not native.suportado(imagem) or imagem.get_colorkey() is not None:
        _REPORT['status']='formato_nativo_nao_suportado'
        return False
    backend=pygame.transform.get_smoothscale_backend()
    _REPORT['backend']=backend
    if backend not in ('SSE2','NEON','GENERIC'):
        _REPORT['status']='backend_desconhecido'
        return False
    # Calcular geometria SEM alterar o estado real da camera.
    z=camera.zoom;f=camera.foco_y
    try:
        # QA782/R12 A54: no boot o zoom inicia em zero e o primeiro passo
        # (<0.002) nunca atinge a geometria de teste. O backend ficou
        # "aguardando_preflight" em TODOS os 2.594 quadros reais.
        # Usar zoom de AMOSTRA apenas no gate e restaurar o estado integral
        # antes da primeira simulacao/desenho. Nao altera zoom do jogador.
        if camera.zoom < .012:
            camera.zoom = .025
        geometria=_geometria_camera(camera,imagem,jogador,velocidade,momento,ativo)
    finally:
        camera.zoom=z;camera.foco_y=f
    if geometria is None:
        _REPORT['status']='sem_geometria_validavel_no_boot'
        return False
    size,crop=geometria
    buf=pygame.Surface(size).convert(imagem)
    formato='RGBA'
    try:
        # Primeiro compara o frame real exato, depois mede custos completos.
        esperado=pygame.transform.smoothscale(imagem,size,buf)
        esperado=pygame.image.tobytes(
            esperado.subsurface((*crop,*imagem.get_size())),formato)
        candidato=native.processar(imagem,size,crop,backend)
        _REPORT['teste_real']=True
        _REPORT['pixels_exatos']=(pygame.image.tobytes(candidato,formato)==esperado)
        if not _REPORT['pixels_exatos']:
            _REPORT['status']='diferenca_pixel_inaceitavel'
            return False
        baseline=[];new=[]
        for i in range(6):
            t=time.perf_counter_ns()
            pygame.transform.smoothscale(imagem,size,buf)
            baseline.append((time.perf_counter_ns()-t)/1e6)
            t=time.perf_counter_ns()
            native.processar(imagem,size,crop,backend)
            new.append((time.perf_counter_ns()-t)/1e6)
        a=statistics.median(baseline[1:])
        b=statistics.median(new[1:])
        _REPORT['original_p50_ms']=round(a,4)
        _REPORT['native_p50_ms']=round(b,4)
        if b<.85*a and (a-b)>=.10:
            _REPORT['status']='native_homologado_localmente'
            return True
        _REPORT['status']='cpu_original_mais_rapida_ou_empate'
    except (ValueError,pygame.error,MemoryError,RuntimeError,OSError):
        _REPORT['status']='erro_no_teste_local'
    return False


def preparar_fora_do_frame(imagem,camera,jogador,velocidade=6,momento=False,ativo=True):
    """Homologacao explicita OFFLINE, nunca invocada no render."""
    if os.environ.get('PIXELRUSH_QA_NATIVE_AUTO','0')!='1':
        _REPORT['status']='nao_solicitado'
        return False
    aprovado=_verificar_primeiro_frame(imagem,camera,jogador,velocidade,momento,ativo)
    _REPORT['selecionado']=bool(aprovado)
    return bool(aprovado)


def instalar():
    global _INSTALLED,_ORIGINAL
    if _INSTALLED:
        return
    from pixelrush_cinema_v3172 import CameraCinematica
    _ORIGINAL=CameraCinematica.aplicar

    @wraps(_ORIGINAL)
    def aplicar_native(self,imagem,jogador=None,velocidade=6,momento=False,ativo=True):
        if not ativo or jogador is None:
            return _ORIGINAL(self,imagem,jogador,velocidade,momento,ativo)
        if not _REPORT['selecionado']:
            # O teste completo envolve 12 resamplings e nao cabe no frame.
            if _REPORT['status']=='nao_avaliado':
                _REPORT['status']='aguardando_preflight_fora_de_frame'
            return _ORIGINAL(self,imagem,jogador,velocidade,momento,ativo)
        # Native selecionado: aplica EXATAMENTE a mesma evolucao de zoom/foco.
        geometria=_geometria_camera(
            self,imagem,jogador,velocidade,momento,ativo)
        if geometria is None:
            return imagem
        try:
            result=_NATIVE.processar(imagem,*geometria,
                                     backend=pygame.transform.get_smoothscale_backend())
            _REPORT['frames_native']+=1
            return result
        except (ValueError,pygame.error,MemoryError,RuntimeError,OSError):
            # NAO chamar _ORIGINAL: atualizaria zoom/foco duas vezes.
            _REPORT['selecionado']=False
            _REPORT['fallbacks']+=1
            _REPORT['status']='fallback_cpu_em_tempo_real'
            return _cpu_depois_do_fallback(self,imagem,geometria)
    CameraCinematica.aplicar=aplicar_native
    _INSTALLED=True


def restaurar_para_teste():
    global _INSTALLED,_NATIVE
    if _INSTALLED:
        from pixelrush_cinema_v3172 import CameraCinematica
        CameraCinematica.aplicar=_ORIGINAL
    _INSTALLED=False
    _NATIVE=None
    _REPORT.update(status='nao_avaliado',selecionado=False,teste_real=False,
                   pixels_exatos=None,frames_native=0,fallbacks=0)
