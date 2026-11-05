# -*- coding: utf-8 -*-
"""Candidato GLES3 fullscreen QA784: camera RGBA exata em FBO 450x800,
apresentada na tela fisica com o mapeamento fixed-point de pygame.scale.
Opt-in e condicionado a RGBA fisico completo + ganho contra CPU no boot.
"""
import ctypes as C

class FullscreenTwoPassQA:
    def __init__(self,p):
        if not p.qa_fullscreen or not p.version.startswith('OpenGL ES 3'):
            raise RuntimeError('exige GLES3 fullscreen')
        self.p=p
        self.w,self.h=p.width,p.height
        f=p._f
        self._delete_fbo=p._fcall('glDeleteFramebuffers',None,[C.c_int,C.POINTER(C.c_uint)])
        self._gen_fbo=p._fcall('glGenFramebuffers',None,[C.c_int,C.POINTER(C.c_uint)])
        self._bind_fbo=p._fcall('glBindFramebuffer',None,[C.c_uint,C.c_uint])
        self._attach=p._fcall('glFramebufferTexture2D',None,[C.c_uint,C.c_uint,C.c_uint,C.c_uint,C.c_int])
        self._check=p._fcall('glCheckFramebufferStatus',C.c_uint,[C.c_uint])
        self._delete_texture=p._fcall('glDeleteTextures',None,[C.c_int,C.POINTER(C.c_uint)])
        self._delete_program=p._fcall('glDeleteProgram',None,[C.c_uint])
        tex=C.c_uint();fbo=C.c_uint()
        f['glGenTextures'](1,C.byref(tex))
        self.tex=tex
        f['glBindTexture'](0x0DE1,tex.value)
        for name,val in ((0x2801,0x2600),(0x2800,0x2600),
                         (0x2802,0x812F),(0x2803,0x812F)):
            f['glTexParameteri'](0x0DE1,name,val)
        f['glTexImage2D'](0x0DE1,0,0x1908,self.w,self.h,0,0x1908,0x1401,None)
        self._gen_fbo(1,C.byref(fbo));self.fbo=fbo
        self._bind_fbo(0x8D40,fbo.value)
        self._attach(0x8D40,0x8CE0,0x0DE1,tex.value,0)
        if self._check(0x8D40)!=0x8CD5:
            raise RuntimeError('FBO incompleto para QA')
        self._bind_fbo(0x8D40,0)
        vs='''#version 300 es
        in vec2 a_pos;
        void main(){gl_Position=vec4(a_pos,0.0,1.0);}'''
        fs='''#version 300 es
        precision highp float;
        precision highp int;
        uniform sampler2D u_resolved;
        uniform ivec2 u_origin;
        uniform ivec2 u_view;
        uniform ivec2 u_steps;
        out vec4 color;
        void main(){
          ivec2 pos=ivec2(gl_FragCoord.xy)-u_origin;
          int src_x=((2*pos.x+1)*u_steps.x)>>17;
          int top=u_view.y-1-pos.y;
          int src_top=((2*top+1)*u_steps.y)>>17;
          int src_y=799-src_top;
          color=texelFetch(u_resolved,clamp(ivec2(src_x,src_y),ivec2(0),ivec2(449,799)),0);
        }'''
        program=f['glCreateProgram']()
        v=p._shader(0x8B31,vs)
        fragment=p._shader(0x8B30,fs)
        f['glAttachShader'](program,v)
        f['glAttachShader'](program,fragment)
        f['glLinkProgram'](program)
        ok=C.c_int()
        f['glGetProgramiv'](program,0x8B82,C.byref(ok))
        if not ok.value:raise RuntimeError('Shader de copia fullscreen nao compilou')
        self.program=program
        self.u_tex=f['glGetUniformLocation'](program,b'u_resolved')
        self.u_origin=f['glGetUniformLocation'](program,b'u_origin')
        self.u_view=f['glGetUniformLocation'](program,b'u_view')
        self.u_steps=f['glGetUniformLocation'](program,b'u_steps')
        self._uniform_2i=p._fcall('glUniform2i',None,[C.c_int,C.c_int,C.c_int])
        if min(self.u_tex,self.u_origin,self.u_view,self.u_steps)<0:
            raise RuntimeError('uniform perdido')
        self.attrib=f['glGetAttribLocation'](program,b'a_pos')
        if self.attrib<0:raise RuntimeError('atributo perdido')
        f['glUseProgram'](program)
        f['glEnableVertexAttribArray'](self.attrib)
        f['glVertexAttribPointer'](self.attrib,2,0x1406,0,0,None)
        f['glUseProgram'](p.program)
        f['glBindTexture'](0x0DE1,p.texture)

    def draw(self,image,zoom=0.,focus_y=0.):
        p=self.p;f=p._f
        self._bind_fbo(0x8D40,self.fbo.value)
        p._qa_fbo_gate=True
        try:
            f['glUseProgram'](p.program)
            p.draw(image,zoom,focus_y)
        finally:
            p._qa_fbo_gate=False
        self._bind_fbo(0x8D40,0)
        x,y,w,h=p.qa_viewport
        f['glViewport'](*p.qa_viewport)
        f['glClearColor'](0.,0.,0.,1.)
        f['glClear'](0x00004000)
        f['glUseProgram'](self.program)
        f['glBindTexture'](0x0DE1,self.tex.value)
        f['glUniform1i'](self.u_tex,0)
        self._uniform_2i(self.u_origin,x,y)
        self._uniform_2i(self.u_view,w,h)
        self._uniform_2i(self.u_steps,(p.width<<16)//w,(p.height<<16)//h)
        f['glDrawArrays'](0x0004,0,6)
        f['glUseProgram'](p.program)
        f['glBindTexture'](0x0DE1,p.texture)
        if f['glGetError']():
            raise RuntimeError('GL apresentou erro em 2passes')

    def close(self):
        self._delete_program(self.program)
        self._bind_fbo(0x8D40,0)
        self._delete_fbo(1,C.byref(self.fbo))
        self._delete_texture(1,C.byref(self.tex))

def _cpu_result(image,zoom,focus):
    import pygame
    w,h=image.get_size()
    if zoom<.002:
        return image
    ex=max(1,int(w*zoom));ey=max(1,int(h*zoom))
    sy=max(0,min(2*ey,ey+int(focus)))
    return pygame.transform.smoothscale(image,(w+2*ex,h+2*ey)).subsurface(
        (ex,sy,w,h))

def verificar_boot_fisico(p,twopass,exigir_ganho=True):
    """Oito quadros RGBA completos + benchmark CPU/GPU no hardware local.
    Nao medir dentro da corrida nem aprovar Mali a partir de Mesa.
    """
    import pygame,time,statistics
    result={'pixels_rgba_exatos':False,'casos_rgba':0,
            'diferencas':None,'rgba_fisico':False,'ganho_p50':None,
            'gpu_p50_ms':None,'cpu_p50_ms':None,'selecionado':False,
            'motivo':'iniciado','aprovado_aparelho':False}
    try:
        if pygame.display.gl_get_attribute(pygame.GL_ALPHA_SIZE)<8:
            result['motivo']='tela_fisica_sem_alpha8'
            return result
        result['rgba_fisico']=True
        read=p._fcall('glReadPixels',None,[C.c_int,C.c_int,C.c_int,
            C.c_int,C.c_uint,C.c_uint,C.c_void_p])
        finish=p._fcall('glFinish',None,[])
        x,y,w,h=p.qa_viewport
        for alpha in (False,True):
            source=pygame.Surface((p.width,p.height),
                pygame.SRCALPHA if alpha else 0,32)
            for row in range(p.height):
                c=((row*13+17)%256,(row*43+53)%256,
                   (row*79+97)%256,(row*31+29)%256)
                pygame.draw.line(source,c if alpha else c[:3],
                    (0,row),(p.width-1,row))
            if alpha:
                source.fill((171,22,91,0),(4,7,49,33))
            for zoom,focus in ((0,0),(.008,-10),(.025,0),(.034,4)):
                twopass.draw(source,zoom,focus)
                finish()
                actual=C.create_string_buffer(w*h*4)
                read(x,y,w,h,0x1908,0x1401,actual)
                expected=pygame.image.tobytes(
                    pygame.transform.scale(_cpu_result(source,zoom,focus),(w,h)),
                    'RGBA',True)
                result['casos_rgba']+=1
                if actual.raw!=expected:
                    result['diferencas']=sum(a!=b for a,b in zip(actual.raw,expected))
                    result['motivo']='divergencia_rgba_fisica'
                    return result
        result['pixels_rgba_exatos']=True
        result['diferencas']=0
        image=pygame.Surface((p.width,p.height),pygame.SRCALPHA,32)
        for row in range(p.height):
            pygame.draw.line(image,((row*17)%256,(row*41)%256,
                 (row*53)%256,(row*11)%256),(0,row),(p.width-1,row))
        zoom=.025
        target=pygame.Surface((w,h),pygame.SRCALPHA,32)
        baseline=[];gpu=[]
        for _ in range(12):
            t0=time.perf_counter_ns()
            pygame.transform.scale(_cpu_result(image,zoom,0),(w,h),target)
            baseline.append((time.perf_counter_ns()-t0)/1e6)
            t0=time.perf_counter_ns()
            twopass.draw(image,zoom,0)
            finish()
            gpu.append((time.perf_counter_ns()-t0)/1e6)
        c=statistics.median(baseline[2:]);g=statistics.median(gpu[2:])
        result.update(cpu_p50_ms=round(c,4),gpu_p50_ms=round(g,4),
                      ganho_p50=round(c/max(g,1e-9),4))
        passed=g<c*.85 and c-g>=.15
        result['selecionado']=bool(passed or not exigir_ganho)
        result['motivo']='pixel_exato_e_ganho_local' if passed else 'sem_ganho_contra_cpu'
        return result
    except (pygame.error,RuntimeError,OSError,MemoryError,ValueError,
            AttributeError) as exc:
        result['motivo']='excecao_'+type(exc).__name__
        return result
