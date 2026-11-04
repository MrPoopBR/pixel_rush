# -*- coding: utf-8 -*-
"""QA782: janela Android tela cheia e coordenadas de toque com aspecto intacto.

A Surface virtual permanece 450x800: sprites, hud, fisica e camera nao sao
esticados. SDL SCALED+FULLSCREEN amplia o quadro no compositor do Android;
se o renderer indisponivel, abre a resolucao fisica e usa letterbox.
Nenhuma inicializacao ou mutacao acontece durante import.
"""
import pygame

_STATUS = {
    'modo': 'nao_iniciado', 'logical': (450, 800),
    'surface_size': None, 'window_size': None,
    'fallbacks': 0, 'erros': [],
}

def area_preservada(tamanho, virtual=(450, 800)):
    w,h = map(int,tamanho)
    vw,vh = map(int,virtual)
    if min(w,h,vw,vh) <= 0:
        raise ValueError('dimensao_de_tela_invalida')
    # Math do aspecto e independentemente de modo SDL (SCALED ou físico).
    escala=min(w/vw,h/vh)
    rw=max(1,min(w,int(vw*escala)))
    rh=max(1,min(h,int(vh*escala)))
    return (rw,rh,(w-rw)//2,(h-rh)//2)

def ponto_virtual(px,py,tamanho,virtual=(450,800)):
    rw,rh,ox,oy=area_preservada(tamanho,virtual)
    vw,vh=map(int,virtual)
    return (int((float(px)-ox)*vw/rw),int((float(py)-oy)*vh/rh))

def dedo_normalizado(x,y,virtual=(450,800),tamanho_fisico=None):
    # pygame FINGER*.x/y representam fração da janela FISICA, mesmo
    # quando mouse + pygame.SCALED usam coordenadas da Surface logica.
    if tamanho_fisico is None:
        try:
            tamanho_fisico=pygame.display.get_window_size()
        except (AttributeError,pygame.error):
            tamanho_fisico=pygame.display.get_surface().get_size()
    px=float(x)*tamanho_fisico[0]
    py=float(y)*tamanho_fisico[1]
    return ponto_virtual(px,py,tamanho_fisico,virtual)

def abrir(largura=450,altura=800):
    tamanho=(int(largura),int(altura))
    _STATUS['logical']=tamanho
    _STATUS['erros']=[]
    # A Surface 450x800 usa SDL_Renderer para preencher uma janela
    # fisica fullscreen, sem expandir pixels via smoothscale Python.
    try:
        tela=pygame.display.set_mode(tamanho,pygame.SCALED|pygame.FULLSCREEN)
        if tela.get_size()!=tamanho:
            raise pygame.error('SDL_SCALED_nao_ofereceu_surface_logica')
        _STATUS['modo']='sdl_scaled_fullscreen'
    except (pygame.error,ValueError) as exc:
        _STATUS['fallbacks']+=1
        _STATUS['erros'].append(type(exc).__name__)
        try:
            tela=pygame.display.set_mode((0,0),pygame.FULLSCREEN)
            _STATUS['modo']='fullscreen_fisico_letterbox'
        except (pygame.error,ValueError) as exc2:
            _STATUS['fallbacks']+=1
            _STATUS['erros'].append(type(exc2).__name__)
            # O fallback final nunca deve impedir o boot.
            tela=pygame.display.set_mode(tamanho)
            _STATUS['modo']='fallback_janela_450x800_nao_homologado'
    _STATUS['surface_size']=tuple(tela.get_size())
    try:
        _STATUS['window_size']=tuple(pygame.display.get_window_size())
    except (AttributeError,pygame.error):
        _STATUS['window_size']=None
    return tela

def diagnostico():
    return dict(_STATUS,fullscreen_sem_bordas=
                _STATUS['modo'] in ('sdl_scaled_fullscreen',
                                     'fullscreen_fisico_letterbox'),
                validado_android_fisico=False)
