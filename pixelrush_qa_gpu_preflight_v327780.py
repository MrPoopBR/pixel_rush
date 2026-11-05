# -*- coding: utf-8 -*-
"""QA780: gate REAL de pixels GLES + benchmark antes do primeiro frame.

Executa somente em Android QA/autorizações de laboratorio, fora do loop.
Framebuffer RGBA8 dedicado para comparar TODOS os bytes (inclusive alpha).
Nao confundir microbenchmark GPU/camera com FPS integral homologado do A54.
Em erro, rejeita a ponte: fallback SDL. Nenhum readback durante a corrida.
"""
import ctypes as C
import statistics
import time
import pygame

GL_TEXTURE_2D=0x0DE1
GL_RGBA=0x1908
GL_UNSIGNED_BYTE=0x1401
GL_FRAMEBUFFER=0x8D40
GL_COLOR_ATTACHMENT0=0x8CE0
GL_FRAMEBUFFER_COMPLETE=0x8CD5
_RELATORIO={'executado':False,'aprovado':False,'motivo':'nao_solicitado',
           'casos_rgba':0,'diferencas':0,'tempo_gpu_p50_ms':None,
           'tempo_cpu_p50_ms':None,'ganho_relativo':None,
           'leitura_somente_boot':True,'fps_android_homologado':False}

def diagnostico():
    return dict(_RELATORIO)

def _fun(gl,nome,retorno,argumentos):
    f=getattr(gl,nome)
    f.restype=retorno
    f.argtypes=argumentos
    return f

def _padrao(rgba=False):
    modo=pygame.SRCALPHA if rgba else 0
    s=pygame.Surface((450,800),modo,32)
    for y in range(800):
        a=(y*23+17)%256 if rgba else 255
        pygame.draw.line(s,((y*19)%256,(y*47)%256,(y*31)%256,a),
                         (0,y),(449,y))
    # Pixel alpha 0 com RGB oculto diferente: nao aceitar gate RGB-only.
    if rgba:
        s.fill((177,32,91,0),(3,4,43,17))
    return s

def _camera_cpu(s,zoom,focus):
    w,h=s.get_size()
    if zoom<.002:
        return s
    ex=max(1,int(w*zoom))
    ey=max(1,int(h*zoom))
    sy=max(0,min(2*ey,ey+int(focus)))
    tmp=pygame.transform.smoothscale(s,(w+2*ex,h+2*ey))
    return tmp.subsurface((ex,sy,w,h))

def _testar(p):
    gl=p.gl
    width,height=p.width,p.height
    if (width,height)!=(450,800):
        raise ValueError('Gate aprovado somente para superficie 450x800')
    # O resultado dos shaders deve bater em framebuffer RGBA8. A janela SDL
    # pode nao preservar alpha; por isso a verificacao tem FBO independente.
    gen_tex=_fun(gl,'glGenTextures',None,[C.c_int,C.POINTER(C.c_uint)])
    bind_tex=p._f['glBindTexture']
    tex_param=p._f['glTexParameteri']
    tex_image=p._f['glTexImage2D']
    gen_fbo=_fun(gl,'glGenFramebuffers',None,[C.c_int,C.POINTER(C.c_uint)])
    bind_fbo=_fun(gl,'glBindFramebuffer',None,[C.c_uint,C.c_uint])
    attach=_fun(gl,'glFramebufferTexture2D',None,
                [C.c_uint,C.c_uint,C.c_uint,C.c_uint,C.c_int])
    check=_fun(gl,'glCheckFramebufferStatus',C.c_uint,[C.c_uint])
    read=_fun(gl,'glReadPixels',None,
              [C.c_int,C.c_int,C.c_int,C.c_int,C.c_uint,C.c_uint,C.c_void_p])
    finish=_fun(gl,'glFinish',None,[])
    delete_tex=_fun(gl,'glDeleteTextures',None,[C.c_int,C.POINTER(C.c_uint)])
    delete_fbo=_fun(gl,'glDeleteFramebuffers',None,[C.c_int,C.POINTER(C.c_uint)])
    tex=C.c_uint()
    fbo=C.c_uint()
    gen_tex(1,C.byref(tex))
    try:
        bind_tex(GL_TEXTURE_2D,tex.value)
        tex_param(GL_TEXTURE_2D,0x2801,0x2600) # GL_NEAREST
        tex_param(GL_TEXTURE_2D,0x2800,0x2600)
        tex_image(GL_TEXTURE_2D,0,GL_RGBA,width,height,0,GL_RGBA,
                  GL_UNSIGNED_BYTE,None)
        gen_fbo(1,C.byref(fbo))
        bind_fbo(GL_FRAMEBUFFER,fbo.value)
        p._qa_fbo_gate=True
        attach(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,tex.value,0)
        if check(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError('FBO_RGBA8_incompleto')
        buf=C.create_string_buffer(width*height*4)
        checks=0
        for alpha in (False,True):
            source=_padrao(alpha)
            for zoom,focus in ((0,0),(.002,-10),(.008,0),(.025,4),(.034,-7)):
                ref=pygame.image.tobytes(_camera_cpu(source,zoom,focus),
                                         'RGBA',True)
                p.draw(source,zoom,focus)
                finish()
                read(0,0,width,height,GL_RGBA,GL_UNSIGNED_BYTE,buf)
                checks+=1
                if buf.raw!=ref:
                    dif=sum(a!=b for a,b in zip(buf.raw,ref))
                    _RELATORIO['diferencas']+=dif
                    _RELATORIO['casos_rgba']=checks
                    return False,'pixels_diferentes',None,None
        _RELATORIO['casos_rgba']=checks
        if p._f['glGetError']():
            return False,'gl_error',None,None
        # Inclusao do upload/transferencia no custo do candidato. Cada quadro
        # e diferente para nunca aprovar PBO por repetir textura sem upload.
        cpu=[]
        gpu=[]
        target=pygame.Surface((width,height),depth=32)
        for i in range(8):
            img=_padrao(False)
            img.set_at((i+2,42),((i*33)%255,17,223))
            start=time.perf_counter_ns()
            target.blit(_camera_cpu(img,.025,0),(0,0))
            cpu.append((time.perf_counter_ns()-start)/1e6)
            start=time.perf_counter_ns()
            p.draw(img,.025,0)
            finish()
            gpu.append((time.perf_counter_ns()-start)/1e6)
        c=statistics.median(cpu[2:])
        g=statistics.median(gpu[2:])
        _RELATORIO['tempo_cpu_p50_ms']=round(c,4)
        _RELATORIO['tempo_gpu_p50_ms']=round(g,4)
        _RELATORIO['ganho_relativo']=round(c/max(g,1e-9),3)
        # Nao habilitar GPU se so empata ou piora no proprio driver. Ganho
        # minimo 15% e 0.15ms (microbench), sem inferir FPS do frame completo.
        if g >= c*.85 or c-g<.15:
            return False,'sem_ganho_microbenchmark',c,g
        return True,'pixels_exatos_e_custo_menor',c,g
    finally:
        p._qa_fbo_gate=False
        bind_fbo(GL_FRAMEBUFFER,0)
        if fbo.value:
            delete_fbo(1,C.byref(fbo))
        if tex.value:
            delete_tex(1,C.byref(tex))
        bind_tex(GL_TEXTURE_2D,p.texture)

def verificar(p, exigir_ganho=True):
    """Aprovacao local temporal e de bytes; nao certifica Mali/Android."""
    _RELATORIO.update(executado=True,aprovado=False,
                      motivo='inicio',casos_rgba=0,diferencas=0,
                      tempo_gpu_p50_ms=None,tempo_cpu_p50_ms=None,
                      ganho_relativo=None)
    try:
        ok,motivo,c,g=_testar(p)
        if not exigir_ganho and motivo=='sem_ganho_microbenchmark':
            ok=True
            motivo='paridade_aprovada_ganho_pendente'
        _RELATORIO['aprovado']=bool(ok)
        _RELATORIO['motivo']=motivo
        _RELATORIO['renderer']=getattr(p,'renderer','desconhecido')
        _RELATORIO['gl_version']=getattr(p,'version','desconhecida')
        return bool(ok)
    except (AttributeError,TypeError,ValueError,OSError,RuntimeError,
            pygame.error,MemoryError) as exc:
        _RELATORIO['motivo']='fallback_'+type(exc).__name__
        return False
