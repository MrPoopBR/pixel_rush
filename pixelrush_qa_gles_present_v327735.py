# -*- coding: utf-8 -*-
"""QA experimental: janela SDL/OpenGL ES2 com apresentacao direta.

Nunca importado por main.py. Nao usa glReadPixels no renderizador.
Sem equivalencia visual e FPS Android comprovados, esta classe NAO
substitui a camera pygame-ce original.
"""
import ctypes as C
import ctypes.util
# Usar o mesmo alias C em todo o caminho EGL/GLES; 'ctypes' nao foi importado.
import time
import os
from collections import deque
import pygame

VERT = """attribute vec2 a_pos;
void main(){gl_Position=vec4(a_pos,0.0,1.0);}
"""
FRAG = """precision highp float;
uniform sampler2D u_scene;
uniform vec2 u_expanded;
uniform vec2 u_crop_bottom;
void main(){
 vec2 uv=(gl_FragCoord.xy+u_crop_bottom)/u_expanded;
 gl_FragColor=texture2D(u_scene,uv);
}
"""


class GLES2Unavailable(RuntimeError):
    pass


class GLES2DirectPresenterQA:
    """Janela separada; EGL swap nativo no Android, SDL GLX no desktop.

    O renderer nao suporta input, HUD ou janela Surface do jogo original.
    Sua integracao e expressamente proibida enquanto gate visual reprovado.
    """
    def __init__(self,width=450,height=800):
        self.width,self.height=int(width),int(height)
        self.frame_count=0
        self.readbacks=0
        self.swap_method=None
        self._egl=None
        self.swap_interval_aplicado=None
        self.frame_intervals_ns=deque(maxlen=256)
        self._last_present_ns=None
        self._f={}
        self._create_window()
        self._create_gl()

    def _fcall(self,name,returns,args):
        f=getattr(self.gl,name)
        f.restype=returns
        f.argtypes=args
        self._f[name]=f
        return f

    def _create_window(self):
        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION,2)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION,0)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,
                                        pygame.GL_CONTEXT_PROFILE_ES)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER,1)
        # Janela OPENGL NOVA, nao compartilha SDL_GetWindowSurface do jogo.
        pygame.display.set_mode((self.width,self.height),
                                pygame.OPENGL|pygame.DOUBLEBUF)
        if pygame.display.gl_get_attribute(
                pygame.GL_CONTEXT_PROFILE_MASK)!=pygame.GL_CONTEXT_PROFILE_ES:
            raise GLES2Unavailable('SDL nao abriu contexto OpenGL ES')
        lib=None
        for name in ('libGLESv2.so',C.util.find_library('GLESv2'),
                     None,C.util.find_library('GL')):
            try:
                candidate=C.CDLL(name)
                if getattr(candidate,'glGetString',None):
                    lib=candidate
                    break
            except (OSError,TypeError):
                continue
        if lib is None:
            raise GLES2Unavailable('Biblioteca GLES nao encontrada')
        self.gl=lib
        version=self._fcall('glGetString',C.c_char_p,[C.c_uint])(0x1F02)
        if not version or b'OpenGL ES' not in version:
            raise GLES2Unavailable('Contexto GL ES nao encontrado')
        self.version=version.decode(errors='replace')
        renderer=self._fcall('glGetString',C.c_char_p,[C.c_uint])(0x1F01)
        self.renderer=renderer.decode(errors='replace')
        self._configure_swap()

    def _configure_swap(self):
        try:
            egl=C.CDLL(C.util.find_library('EGL') or 'libEGL.so')
            egl.eglGetCurrentDisplay.restype=C.c_void_p
            egl.eglGetCurrentSurface.restype=C.c_void_p
            egl.eglGetCurrentSurface.argtypes=[C.c_int]
            egl.eglSwapBuffers.restype=C.c_uint
            egl.eglSwapBuffers.argtypes=[C.c_void_p,C.c_void_p]
            display=egl.eglGetCurrentDisplay()
            surface=egl.eglGetCurrentSurface(0x3059)  # EGL_DRAW
            if display and surface:
                self._egl=egl
                self._egl_display=display
                self._egl_surface=surface
                self.swap_method='eglSwapBuffers'
                # QA779: definir VSync de maneira explicita quando a EGL
                # aceita eglSwapInterval. Evitar sincronizacao forçada
                # sem EGL ativa; em erro, manter o swap original.
                intervalo=(0 if os.environ.get('PIXELRUSH_QA_VSYNC_INTERVAL','1')=='0'
                           else 1)
                try:
                    egl.eglSwapInterval.restype=C.c_uint
                    egl.eglSwapInterval.argtypes=[C.c_void_p,C.c_int]
                    if egl.eglSwapInterval(display,intervalo):
                        self.swap_interval_aplicado=intervalo
                except (AttributeError,OSError,ValueError):
                    self.swap_interval_aplicado=None
                return
        except (OSError,AttributeError):
            pass
        # Linux/Xvfb GLX: somente fallback de teste desktop.
        self.swap_method='SDL_GL_SwapWindow (desktop GLX)'

    def _shader(self,kind,source):
        f=self._f
        shader=f['glCreateShader'](kind)
        raw=C.c_char_p(source.encode('ascii'))
        f['glShaderSource'](shader,1,C.byref(raw),None)
        f['glCompileShader'](shader)
        status=C.c_int()
        f['glGetShaderiv'](shader,0x8B81,C.byref(status))
        if not status.value:
            raise GLES2Unavailable('Shader GLES2 falhou')
        return shader

    def _create_gl(self):
        # GLES2 core, todos os simbolos sao suportados no Android API 26+.
        def f(name,ret,args):
            return self._fcall(name,ret,args)
        f('glCreateShader',C.c_uint,[C.c_uint])
        f('glShaderSource',None,[C.c_uint,C.c_int,
                                C.POINTER(C.c_char_p),C.POINTER(C.c_int)])
        f('glCompileShader',None,[C.c_uint])
        f('glGetShaderiv',None,[C.c_uint,C.c_uint,C.POINTER(C.c_int)])
        f('glCreateProgram',C.c_uint,[])
        f('glAttachShader',None,[C.c_uint,C.c_uint])
        f('glLinkProgram',None,[C.c_uint])
        f('glGetProgramiv',None,[C.c_uint,C.c_uint,C.POINTER(C.c_int)])
        f('glUseProgram',None,[C.c_uint])
        f('glGetUniformLocation',C.c_int,[C.c_uint,C.c_char_p])
        f('glUniform1i',None,[C.c_int,C.c_int])
        f('glUniform2f',None,[C.c_int,C.c_float,C.c_float])
        f('glGenBuffers',None,[C.c_int,C.POINTER(C.c_uint)])
        f('glBindBuffer',None,[C.c_uint,C.c_uint])
        f('glBufferData',None,[C.c_uint,C.c_ssize_t,C.c_void_p,C.c_uint])
        f('glGetAttribLocation',C.c_int,[C.c_uint,C.c_char_p])
        f('glEnableVertexAttribArray',None,[C.c_uint])
        f('glVertexAttribPointer',None,
          [C.c_uint,C.c_int,C.c_uint,C.c_uint,C.c_int,C.c_void_p])
        f('glGenTextures',None,[C.c_int,C.POINTER(C.c_uint)])
        f('glBindTexture',None,[C.c_uint,C.c_uint])
        f('glTexParameteri',None,[C.c_uint,C.c_uint,C.c_int])
        f('glTexImage2D',None,[C.c_uint,C.c_int,C.c_int,C.c_int,C.c_int,
                               C.c_uint,C.c_uint,C.c_void_p])
        f('glTexSubImage2D',None,
          [C.c_uint,C.c_int,C.c_int,C.c_int,C.c_int,C.c_int,C.c_uint,
           C.c_uint,C.c_void_p])
        f('glPixelStorei',None,[C.c_uint,C.c_int])
        f('glViewport',None,[C.c_int,C.c_int,C.c_int,C.c_int])
        f('glDrawArrays',None,[C.c_uint,C.c_int,C.c_int])
        f('glGetError',C.c_uint,[])
        p=f('glCreateProgram',C.c_uint,[])()
        vs=self._shader(0x8B31,VERT)
        fs=self._shader(0x8B30,FRAG)
        f('glAttachShader',None,[C.c_uint,C.c_uint])(p,vs)
        self._f['glAttachShader'](p,fs)
        self._f['glLinkProgram'](p)
        ok=C.c_int()
        self._f['glGetProgramiv'](p,0x8B82,C.byref(ok))
        if not ok.value:
            raise GLES2Unavailable('Link GLES2 falhou')
        self.program=p
        self._f['glUseProgram'](p)
        self.u_expanded=self._f['glGetUniformLocation'](p,b'u_expanded')
        self.u_crop=self._f['glGetUniformLocation'](p,b'u_crop_bottom')
        self._f['glUniform1i'](self._f['glGetUniformLocation'](p,b'u_scene'),0)
        coords=(C.c_float*12)(-1,-1,1,-1,-1,1,1,-1,1,1,-1,1)
        buf=C.c_uint()
        self._f['glGenBuffers'](1,C.byref(buf))
        self._f['glBindBuffer'](0x8892,buf.value)
        self._f['glBufferData'](0x8892,C.sizeof(coords),
                                C.cast(coords,C.c_void_p),0x88E4)
        a=self._f['glGetAttribLocation'](p,b'a_pos')
        if a<0: raise GLES2Unavailable('Atributo a_pos indisponivel')
        self._f['glEnableVertexAttribArray'](a)
        self._f['glVertexAttribPointer'](a,2,0x1406,0,0,None)
        tex=C.c_uint()
        self._f['glGenTextures'](1,C.byref(tex))
        self.texture=tex.value
        self._f['glBindTexture'](0x0DE1,self.texture)
        for parameter,value in ((0x2801,0x2601),(0x2800,0x2601),
                                (0x2802,0x812F),(0x2803,0x812F)):
            self._f['glTexParameteri'](0x0DE1,parameter,value)
        self._f['glPixelStorei'](0x0CF5,1)
        self._f['glTexImage2D'](0x0DE1,0,0x1908,self.width,self.height,
                                0,0x1908,0x1401,None)
        self._f['glViewport'](0,0,self.width,self.height)
        self._f['glUseProgram'](p)
        if self._f['glGetError']():
            raise GLES2Unavailable('Erro GL na criacao de textura')

    def draw(self,image,zoom=0.0,focus_y=0):
        """Upload RGBA e desenho ES2; NUNCA glReadPixels."""
        if image.get_size() != (self.width,self.height):
            raise ValueError('Tamanho da imagem diferente da tela')
        if not 0 <= zoom <= .2: raise ValueError('Zoom fora do intervalo QA')
        ex=max(1,int(self.width*zoom)) if zoom else 0
        ey=max(1,int(self.height*zoom)) if zoom else 0
        w,h=self.width+2*ex,self.height+2*ey
        sy=max(0,min(2*ey,ey+int(focus_y))) if zoom else 0
        # QA 3.277.39: bytes ficam vivos ate glTexSubImage2D retornar.
        # Evita a segunda copia de 450x800x4 bytes em create_string_buffer.
        # A ordem RGBA e flip vertical sao exatamente os originais.
        data=pygame.image.tobytes(image,'RGBA',True)
        data_ptr=C.cast(C.c_char_p(data),C.c_void_p)
        t0=time.perf_counter_ns()
        self._f['glBindTexture'](0x0DE1,self.texture)
        # QA v3.277.42: PBO GLES3 opcional. A classe continua somente no
        # laboratorio: nenhum caminho do jogo importa este presenter.
        if not hasattr(self,'_qa_pbo'):
            self._qa_pbo=None
            self._qa_pbo_disabled=False
            import os
            if os.environ.get('PIXELRUSH_QA_GLES_PBO','0')=='1':
                try:
                    from pixelrush_qa_gles_pbo_v327742 import UploadGLES3PBOQA
                    self._qa_pbo=UploadGLES3PBOQA(self)
                except (ImportError,RuntimeError,OSError,AttributeError):
                    self._qa_pbo_disabled=True
        usado_pbo=False
        if self._qa_pbo is not None:
            try:
                self._qa_pbo.enviar(data,self.width,self.height)
                usado_pbo=True
            except (RuntimeError,ValueError,OSError,AttributeError):
                self._qa_pbo_disabled=True
                try:
                    self._qa_pbo.fechar()
                except (RuntimeError,OSError):
                    pass
                self._qa_pbo=None
        if not usado_pbo:
            self._f['glTexSubImage2D'](0x0DE1,0,0,0,self.width,self.height,
                                       0x1908,0x1401,data_ptr)
        self._f['glUniform2f'](self.u_expanded,float(w),float(h))
        self._f['glUniform2f'](self.u_crop,float(ex),float(h-self.height-sy))
        self._f['glDrawArrays'](0x0004,0,6)
        self.cpu_upload_draw_ns=time.perf_counter_ns()-t0
        if self._f['glGetError'](): raise RuntimeError('Erro desenhando GLES2')
        return {'extra_x':ex,'extra_y':ey,'crop_y':sy,
                'readback_gpu_cpu':False}

    def present(self):
        """EGLSwapBuffers direto no Android; desktop usa swap SDL_GL (GLX)."""
        t0=time.perf_counter_ns()
        if self._egl is not None:
            if not self._egl.eglSwapBuffers(self._egl_display,self._egl_surface):
                raise RuntimeError('eglSwapBuffers falhou')
        else:
            pygame.display.flip()
        fim_ns=time.perf_counter_ns()
        self.cpu_swap_ns=fim_ns-t0
        if self._last_present_ns is not None:
            self.frame_intervals_ns.append(fim_ns-self._last_present_ns)
        self._last_present_ns=fim_ns
        self.frame_count+=1

    def diagnostico(self):
        pbo=getattr(self,'_qa_pbo',None)
        # P50/P95 fora do caminho de desenho. Sem quantis no frame quente.
        intervalos=sorted(self.frame_intervals_ns)
        p50=(round(intervalos[len(intervalos)//2]/1e6,3)
             if intervalos else None)
        p95=(round(intervalos[min(len(intervalos)-1,round(.95*(len(intervalos)-1)))]/1e6,3)
             if intervalos else None)
        jank=sum(1 for n in intervalos if n>50_000_000)
        return {'renderer':self.renderer,
                'egl_vsync_aplicado':self.swap_interval_aplicado,
                'frame_interval_p50_ms':p50,
                'frame_interval_p95_ms':p95,
                'quadros_intervalo_acima_50ms':jank,'gl_version':self.version,
                'video_driver':pygame.display.get_driver(),
                'swap_method':self.swap_method,'frames':self.frame_count,
                'gpu_to_cpu_readbacks':self.readbacks,
                'integrado_ao_jogo':False,'equivalencia_visual_aprovada':False,
                'qa_pbo_ativo':pbo is not None,
                'qa_pbo_desabilitado':getattr(self,'_qa_pbo_disabled',False),
                'qa_pbo_stats':pbo.diagnostico() if pbo else None}

    def close(self):
        # Apenas encerra a janela propria do harness, nunca do jogo em producao.
        pbo=getattr(self,'_qa_pbo',None)
        if pbo is not None:
            try:pbo.fechar()
            except (RuntimeError,OSError):pass
        pygame.display.quit()
