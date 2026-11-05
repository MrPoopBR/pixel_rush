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
         'shader_pixel_exato_solicitado':False,
         'contexto_gles3_solicitado':False,
         'homologado_android':False,'preflight_gpu':None,
         'selecionador_gpu':None,'falha_modulo':None,
         'falha_detalhe':None,'fullscreen_experimental':False,
         'preflight_fisico':None,'twopass_gles3_ativo':False}
_SIZE=(450,800)


class _Ponte:
    def __init__(self):
        self.staging=None
        self.presenter=None
        self.two_pass=None
        self.cpu_window=None
        self.size=None
        self._requested_flags=0
        self.modo='nativo'
        self.zoom=0.0
        self.foco_y=0.0

    def _reabrir_sdl(self):
        if self.two_pass is not None:
            self.two_pass.close()
            self.two_pass=None
        _STATUS['twopass_gles3_ativo']=False
        self.presenter=None
        # Preserva a referencia do jogo a staging: o que muda eh somente
        # a superficie SDL final de apresentacao.
        self.cpu_window=_ORIGINALS['set_mode'](self.size,self._requested_flags)
        self.modo='fallback'
        _STATUS['gpu_ativo']=False

    def set_mode(self, size, flags=0, depth=0, display=0, vsync=0):
        import pygame
        requested=tuple(size)
        # QA782/R12: o perfil A54 caiu em criacao_ModuleNotFoundError.
        # A ponte reconstruia uma janela 450x800 SEM FULLSCREEN e deixou
        # o jogo minúsculo no canto superior esquerdo. Nao converter
        # fullscreen/SCALED em janela GPU experimental sem prova no Mali:
        # SDL preserva a Surface logica e amplia na tela fisica.
        fullscreen_qa=bool(flags & pygame.FULLSCREEN and
            os.environ.get('PIXELRUSH_QA_GLES_FULLSCREEN_PROBE','0')=='1')
        if requested!=_SIZE or (flags & pygame.OPENGL) or (
                flags & (pygame.FULLSCREEN|pygame.SCALED) and not fullscreen_qa):
            if flags & pygame.FULLSCREEN:
                _STATUS['fallback']='sdl_fullscreen_sem_gpu'
            self.modo='nativo'
            self.staging=None
            self.presenter=None
            self.cpu_window=None
            return _ORIGINALS['set_mode'](size,flags,depth,display,vsync)
        self.size=requested
        self._requested_flags=flags
        _STATUS['fullscreen_experimental']=fullscreen_qa
        try:
            import pixelrush_qa_gles_present_v327735 as present_module
            from pixelrush_qa_gles_present_v327735 import GLES2DirectPresenterQA
            # Shader fixo (em vez do bilinear original) somente para laboratorio
            # GLES habilitado; nao se declara paridade Android.
            exacto=os.environ.get('PIXELRUSH_QA_GPU_ZOOM','0')=='1'
            gles3=os.environ.get('PIXELRUSH_QA_GLES3_CONTEXT','0')=='1'
            if exacto:
                from pixelrush_qa_gles_exact_v327736 import shaders
                vshader,fshader=shaders('GLES3' if gles3 else 'GLES2',
                    pygame.transform.get_smoothscale_backend(),requested)
            # A chamada dentro do construtor usa o set_mode nativo, nao o
            # wrapper de entrada, impedindo recursao/segunda janela.
            atual=pygame.display.set_mode
            setter=pygame.display.gl_set_attribute
            original_shader=(getattr(present_module,'VERT',None),
                             getattr(present_module,'FRAG',None))
            # O presenter existente pede ES2. Para o modo PBO3 experimental
            # exige-se ES3 real, sem simular capacidades na CPU.
            def pedir_es3(atributo,valor):
                if atributo==pygame.GL_CONTEXT_MAJOR_VERSION:
                    return setter(atributo,3)
                return setter(atributo,valor)
            pygame.display.set_mode=_ORIGINALS['set_mode']
            if gles3:
                pygame.display.gl_set_attribute=pedir_es3
            try:
                if exacto:
                    present_module.VERT=vshader
                    present_module.FRAG=fshader
                self.presenter=GLES2DirectPresenterQA(
                    *requested,**({'fullscreen':True} if fullscreen_qa else {}))
                if gles3 and not self.presenter.version.startswith('OpenGL ES 3'):
                    raise RuntimeError('Contexto GLES3 solicitado nao entregue')
            finally:
                present_module.VERT,present_module.FRAG=original_shader
                pygame.display.set_mode=atual
                pygame.display.gl_set_attribute=setter
            # QA779: o jogo inteiro cria Surfaces via .convert() durante
            # o boot e em biomas sob demanda. Um contexto OPENGL que nao
            # fornece o formato de display ao pygame pode abrir a janela
            # mas derrubar o jogo DEPOIS do bootstrap. Testar agora, antes
            # de entregar a staging ao main. Se nao houver convert valido,
            # voltar a SDL software sem risco de tela preta.
            try:
                pygame.Surface((2,2),depth=32).convert()
            except (pygame.error,ValueError):
                raise RuntimeError('Contexto GLES sem suporte a Surface.convert')
            # QA780: proibido apresentar quadros de jogo no backend GPU
            # sem a prova no dispositivo REAL, fora do loop. O preflight
            # compara 10 quadros RGBA completos em FBO dedicado, mede custo
            # com upload efetivo e remove o FBO antes da corrida.
            # Mesa/Xvfb roda em testes próprios; não aprova Mali por tabela.
            if ('ANDROID_ARGUMENT' in os.environ or os.name=='android'):
                from pixelrush_qa_gpu_preflight_v327780 import (
                    verificar as _qa_verificar_gpu,
                    diagnostico as _qa_gpu_relatorio)
                if not _qa_verificar_gpu(self.presenter,exigir_ganho=True):
                    _STATUS['preflight_gpu']=_qa_gpu_relatorio()
                    raise RuntimeError('GPU_preflight_sem_paridade_ou_ganho')
                _STATUS['preflight_gpu']=_qa_gpu_relatorio()
                # Seletor unico de CPU/GPU: so autoriza a rota QA local
                # depois da prova de driver; nunca marca FPS Android final.
                from pixelrush_qa_backend_gate_v327747 import (
                    CapacidadeVideo, selecionar)
                decisoes=selecionar(CapacidadeVideo(
                    janela_opengl=True,
                    input_compatível=True, hud_compatível=True,
                    pixels_todos_iguais=True,
                    ganho_camera_local=True,
                    sem_readback=True, dispositivo_real_medido=True,
                    perfil='gles_qa_boot'),
                    qa_candidato=True)
                _STATUS['selecionador_gpu']=decisoes
                if decisoes['backend']!='gles_qa_experimental':
                    raise RuntimeError('Seletor_GPU_QA_rejeitou_backend')
                self.presenter._qa_integrado=True
                self.presenter._qa_equivalencia_visual=True
            if fullscreen_qa:
                # QA784: gate físico RGBA + velocidade no boot e somente opt-in.
                # Se nao superar pygame-ce: SDL fullscreen permanece padrão.
                from pixelrush_qa_gles_twopass_v327784 import (
                    FullscreenTwoPassQA,verificar_boot_fisico)
                self.two_pass=FullscreenTwoPassQA(self.presenter)
                gate=verificar_boot_fisico(self.presenter,self.two_pass,True)
                _STATUS['preflight_fisico']=gate
                if not gate['selecionado']:
                    raise RuntimeError('GLES_fullscreen_fisico_sem_paridade_ou_ganho')
                _STATUS['twopass_gles3_ativo']=True
            self.staging=pygame.Surface(requested,depth=32)
            self.cpu_window=None
            self.modo='gles'
            _STATUS['gpu_ativo']=True
            _STATUS['shader_pixel_exato_solicitado']=bool(exacto)
            _STATUS['contexto_gles3_solicitado']=bool(gles3)
            _STATUS['fallback']='nenhum'
            return self.staging
        except (ImportError,AttributeError,OSError,RuntimeError,ValueError,pygame.error,MemoryError) as exc:
            _STATUS['falhas_gpu']+=1
            _STATUS['fallback']='criacao_'+type(exc).__name__
            _STATUS['falha_modulo']=getattr(exc,'name',None)
            _STATUS['falha_detalhe']=(type(exc).__name__+': '+str(exc))[:180]
            if self.two_pass is not None:
                self.two_pass.close()
                self.two_pass=None
            _STATUS['twopass_gles3_ativo']=False
            self.presenter=None
            self.staging=pygame.Surface(requested)
            try:
                self._reabrir_sdl()
                # No fallback a Surface precisa manter a referencia do jogo.
                # Nao trocar por outra Surface depois da primeira entrega.
                # Antes da primeira entrega, converte apenas se seguro.
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
                if self.two_pass is not None:
                    self.two_pass.draw(self.staging,zoom=self.zoom,
                                       focus_y=self.foco_y)
                else:
                    self.presenter.draw(self.staging,zoom=self.zoom,
                                        focus_y=self.foco_y)
                current=pygame.display.flip
                pygame.display.flip=_ORIGINALS['flip']
                try:
                    self.presenter.present()
                finally:
                    pygame.display.flip=current
                _STATUS['frames_gles']+=1
                self.zoom=self.foco_y=0.0
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
            imagem=self.staging
            if self.zoom>=.002:
                try:
                    w,h=self.staging.get_size()
                    extra_x=max(1,int(w*self.zoom))
                    extra_y=max(1,int(h*self.zoom))
                    sz=(w+2*extra_x,h+2*extra_y)
                    expanded=pygame.transform.smoothscale(self.staging,sz)
                    sy=max(0,min(2*extra_y,extra_y+int(self.foco_y)))
                    imagem=expanded.subsurface((extra_x,sy,w,h))
                except (pygame.error,ValueError,MemoryError):
                    imagem=self.staging
            self.cpu_window.blit(imagem,(0,0))
            _STATUS['frames_fallback']+=1
        self.zoom=self.foco_y=0.0
        return _ORIGINALS['flip']()


def _instalar_camera_gpu():
    # Este wrapper substitui somente o smoothscale da camera. A evolucao
    # de zoom/foco e identica; input, estado do jogador e fisica intactos.
    if os.environ.get('PIXELRUSH_QA_GPU_ZOOM','0')!='1':
        return
    from functools import wraps
    from pixelrush_cinema_v3172 import CameraCinematica
    from pixelrush_qa_camera_native_auto_v327742 import _geometria_camera
    original=CameraCinematica.aplicar
    _ORIGINALS['camera_aplicar']=original

    @wraps(original)
    def aplicar(self,imagem,jogador=None,velocidade=6,momento=False,ativo=True):
        ponte=_BRIDGE
        if ponte is None or ponte.modo!='gles':
            return original(self,imagem,jogador,velocidade,momento,ativo)
        geometria=_geometria_camera(self,imagem,jogador,velocidade,momento,ativo)
        if geometria is None:
            ponte.zoom=ponte.foco_y=0.0
            return imagem
        if imagem.get_size()!=_SIZE:
            # Forma diferente: ajustar a imagem pela CPU, sem aplicar duplo
            # zoom nem divergir da geometria historica.
            from pixelrush_qa_camera_native_auto_v327742 import _cpu_depois_do_fallback
            ponte.zoom=ponte.foco_y=0.0
            return _cpu_depois_do_fallback(self,imagem,geometria)
        ponte.zoom=self.zoom
        ponte.foco_y=self.foco_y
        _STATUS['zoom_gpu_ativado']=True
        return imagem

    CameraCinematica.aplicar=aplicar


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
    _instalar_camera_gpu()
    return diagnostico()


def restaurar_para_teste():
    global _INSTALLED,_BRIDGE
    if not _INSTALLED:
        return
    import pygame
    if 'camera_aplicar' in _ORIGINALS:
        from pixelrush_cinema_v3172 import CameraCinematica
        CameraCinematica.aplicar=_ORIGINALS['camera_aplicar']
    pygame.display.set_mode=_ORIGINALS['set_mode']
    pygame.display.get_surface=_ORIGINALS['get_surface']
    pygame.display.flip=_ORIGINALS['flip']
    _ORIGINALS.clear()
    _BRIDGE=None
    _INSTALLED=False
    _STATUS.update(instalado=False,gpu_ativo=False,
                   zoom_gpu_ativado=False,shader_pixel_exato_solicitado=False,
                   contexto_gles3_solicitado=False)
