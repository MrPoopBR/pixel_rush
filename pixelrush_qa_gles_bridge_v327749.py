# -*- coding: utf-8 -*-
"""QA749: ponte opt-in entre a Surface CPU REAL do jogo e EGL/GLES2.

O jogo desenha em "tela.blit(...)" e finaliza em display.flip(); estes dois
pontos recebem uma superficie CPU de staging e uma janela GLES dedicada. O
HUD e a entrada SDL continuam inteiros no mesmo loop. A ponte esta DESLIGADA
por padrao porque zoom, escala fisica e pixel RGBA ainda exigem gates no
Android. Esta nao e a alternativa homologada para producao.

Ativacao EXPERIMENTAL explicita: PIXELRUSH_QA_GLES_BRIDGE=1 e
PIXELRUSH_QA_ANDROID=1. NUNCA ativa por simplesmente importar o modulo.
Se GLES falhar, reabre SDL Surface e apresenta a mesma staging Surface,
sem perder saves, estado de input nem alterar camera/fisica.
"""
import os

_INSTALLED=False
_ORIGINALS={}
_BRIDGE=None
_STATUS={'instalado':False,'gpu_ativo':False,'falhas_gpu':0,
         'frames_gles':0,'frames_fallback':0,'fallback':'nao_solicitado',
         'input_sdl_preservado':True,'hud_cpu_preservado':True,
         'readback_gpu_cpu':False,'zoom_gpu_ativado':False,
         'homologado_android':False}
_SIZE=(450,800)


class _Ponte:
    def __init__(self):
        self.staging=None
        self.presenter=None
        self.cpu_window=None
        self.size=None
        self.modo='nativo'

    def _reabrir_sdl(self):
        self.presenter=None
        # Preserva a referencia do jogo a staging: o que muda eh somente
        # a superficie SDL final de apresentacao.
        self.cpu_window=_ORIGINALS['set_mode'](self.size)
        self.modo='fallback'
        _STATUS['gpu_ativo']=False

    def set_mode(self, size, flags=0, depth=0, display=0, vsync=0):
        import pygame
        requested=tuple(size)
        # Nao rouba a janela SDL alheia ao jogo nem fullscreen desktop.
        if requested!=_SIZE or (flags & pygame.OPENGL):
            self.modo='nativo'
            self.staging=None
            self.presenter=None
            self.cpu_window=None
            return _ORIGINALS['set_mode'](size,flags,depth,display,vsync)
        self.size=requested
        try:
            from pixelrush_qa_gles_present_v327735 import GLES2DirectPresenterQA
            # A chamada dentro do construtor usa o set_mode nativo, nao o
            # wrapper de entrada, impedindo recursao/segunda janela.
            atual=pygame.display.set_mode
            pygame.display.set_mode=_ORIGINALS['set_mode']
            try:
                self.presenter=GLES2DirectPresenterQA(*requested)
            finally:
                pygame.display.set_mode=atual
            # O pygame-ce tambem usa a Surface display atual para convert().
            self.staging=pygame.Surface(requested).convert()
            self.cpu_window=None
            self.modo='gles'
            _STATUS['gpu_ativo']=True
            _STATUS['fallback']='nenhum'
            return self.staging
        except (ImportError,OSError,RuntimeError,ValueError,pygame.error,MemoryError) as exc:
            _STATUS['falhas_gpu']+=1
            _STATUS['fallback']='criacao_'+type(exc).__name__
            self.presenter=None
            self.staging=pygame.Surface(requested)
            try:
                self._reabrir_sdl()
                self.staging=self.staging.convert(self.cpu_window)
                return self.staging
            except (pygame.error,MemoryError):
                self.staging=None
                self.modo='nativo'
                return _ORIGINALS['set_mode'](size,flags,depth,display,vsync)

    def get_surface(self):
        return self.staging if self.staging is not None else _ORIGINALS['get_surface']()

    def flip(self):
        import pygame
        if self.modo=='gles' and self.staging is not None and self.presenter is not None:
            try:
                # O zoom original continua sendo calculado pela camera CPU.
                # Renderizar na GPU com zoom 0 apenas mostra a imagem final.
                # Este adaptador NAO afirma acelerar a camera.
                self.presenter.draw(self.staging,zoom=0.0,focus_y=0)
                current=pygame.display.flip
                pygame.display.flip=_ORIGINALS['flip']
                try:
                    self.presenter.present()
                finally:
                    pygame.display.flip=current
                _STATUS['frames_gles']+=1
                return None
            except (OSError,RuntimeError,ValueError,pygame.error,MemoryError) as exc:
                _STATUS['falhas_gpu']+=1
                _STATUS['fallback']='apresentacao_'+type(exc).__name__
                try:
                    self._reabrir_sdl()
                except (pygame.error,MemoryError):
                    _STATUS['fallback']='reabertura_sdl_falhou'
                    raise
        if self.modo=='fallback' and self.staging is not None:
            self.cpu_window.blit(self.staging,(0,0))
            _STATUS['frames_fallback']+=1
        return _ORIGINALS['flip']()


def diagnostico():
    return dict(_STATUS,modo=_BRIDGE.modo if _BRIDGE else 'nao_instalado')


def instalar():
    global _INSTALLED,_BRIDGE
    if _INSTALLED:
        return diagnostico()
    if os.environ.get('PIXELRUSH_QA_GLES_BRIDGE','0')!='1':
        return diagnostico()
    if os.environ.get('PIXELRUSH_QA_ANDROID','0')!='1':
        _STATUS['fallback']='fora_branch_QA'
        return diagnostico()
    if not ('ANDROID_ARGUMENT' in os.environ or
            os.environ.get('PIXELRUSH_QA_GL_DESKTOP_LAB','0')=='1'):
        _STATUS['fallback']='sem_dispositivo_android_ou_lab_autorizado'
        return diagnostico()
    import pygame
    _ORIGINALS.update(set_mode=pygame.display.set_mode,
                      get_surface=pygame.display.get_surface,
                      flip=pygame.display.flip)
    _BRIDGE=_Ponte()
    pygame.display.set_mode=_BRIDGE.set_mode
    pygame.display.get_surface=_BRIDGE.get_surface
    pygame.display.flip=_BRIDGE.flip
    _INSTALLED=True
    _STATUS['instalado']=True
    return diagnostico()


def restaurar_para_teste():
    global _INSTALLED,_BRIDGE
    if not _INSTALLED:
        return
    import pygame
    pygame.display.set_mode=_ORIGINALS['set_mode']
    pygame.display.get_surface=_ORIGINALS['get_surface']
    pygame.display.flip=_ORIGINALS['flip']
    _ORIGINALS.clear()
    _BRIDGE=None
    _INSTALLED=False
    _STATUS.update(instalado=False,gpu_ativo=False)
