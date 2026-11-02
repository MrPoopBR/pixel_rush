#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prova offscreen OpenGL ES 2.0/EGL da camera PIXEL RUSH.
Nunca abre a janela do jogo. Sem dependencia GL Python; usa ctypes e pygame-ce.
Resultado NEGADO se GLES linear divergir de pygame.transform.smoothscale.
Falha na disponibilidade EGL gera "indisponivel", NAO aprova GPU.
"""
import ctypes as C
import ctypes.util
import json
import os
import time
from pathlib import Path

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

OUT = Path('qa-gles-gate-v327734.json')
PTR, INT, UINT = C.c_void_p, C.c_int, C.c_uint


def executar():
    import pygame
    pygame.init()
    pygame.display.set_mode((450, 800))
    lib = ctypes.util.find_library('EGL')
    if not lib:
        return {'estado': 'indisponivel', 'motivo': 'libEGL ausente',
                'aprovado': False}
    egl = C.CDLL(lib)
    glname = ctypes.util.find_library('GL')
    gl = C.CDLL(glname) if glname else egl

    def e(nome, result, args):
        fn = getattr(egl, nome)
        fn.restype, fn.argtypes = result, args
        return fn

    getproc = e('eglGetProcAddress', PTR, [C.c_char_p])

    def g(nome, result, args):
        fn = getattr(gl, nome, None)
        if fn is None:
            ptr = getproc(nome.encode('ascii'))
            if not ptr:
                raise RuntimeError('simbolo GLES ausente: ' + nome)
            return C.CFUNCTYPE(result, *args)(ptr)
        fn.restype, fn.argtypes = result, args
        return fn

    getdisplay = e('eglGetDisplay', PTR, [PTR])
    eglinit = e('eglInitialize', INT, [PTR, C.POINTER(INT), C.POINTER(INT)])
    bindapi = e('eglBindAPI', INT, [UINT])
    choose = e('eglChooseConfig', INT,
               [PTR, C.POINTER(INT), C.POINTER(PTR), INT, C.POINTER(INT)])
    createcontext = e('eglCreateContext', PTR,
                      [PTR, PTR, PTR, C.POINTER(INT)])
    createpbuf = e('eglCreatePbufferSurface', PTR,
                   [PTR, PTR, C.POINTER(INT)])
    current = e('eglMakeCurrent', INT, [PTR, PTR, PTR, PTR])
    geterror = e('eglGetError', UINT, [])
    platform_ptr = getproc(b'eglGetPlatformDisplayEXT')
    display = None
    if platform_ptr:
        platform = C.CFUNCTYPE(PTR, UINT, PTR, C.POINTER(INT))(platform_ptr)
        display = platform(0x31DD, None, None)  # EGL_PLATFORM_SURFACELESS_MESA
    if not display:
        display = getdisplay(None)
    if not display:
        raise RuntimeError('EGL display indisponivel')
    major, minor = INT(), INT()
    if not eglinit(display, C.byref(major), C.byref(minor)):
        raise RuntimeError('eglInitialize: ' + hex(geterror()))
    if not bindapi(0x30A0):  # EGL_OPENGL_ES_API
        raise RuntimeError('eglBindAPI: ' + hex(geterror()))
    attribs = (INT * 15)(0x3024,8,0x3023,8,0x3022,8,0x3021,8,
                          0x3040,4,0x3033,1,0x3038) # GLES2, pbuffer, RGBA8
    cfg, qtd = PTR(), INT()
    if not choose(display, attribs, C.byref(cfg), 1, C.byref(qtd)) or not qtd.value:
        raise RuntimeError('EGL_CONFIG GLES2 ausente')
    context = createcontext(display, cfg, None, (INT * 3)(0x3098,2,0x3038))
    w,h = 450,800
    surface = createpbuf(display, cfg, (INT * 5)(0x3057,w,0x3056,h,0x3038))
    if not context or not surface or not current(display,surface,surface,context):
        raise RuntimeError('EGL context GLES2/pbuffer falhou')

    make_shader = g('glCreateShader', UINT, [UINT])
    shader_src = g('glShaderSource', None,
                   [UINT,INT,C.POINTER(C.c_char_p),C.POINTER(INT)])
    shader_compile = g('glCompileShader', None, [UINT])
    shader_status = g('glGetShaderiv', None, [UINT,UINT,C.POINTER(INT)])
    shader_log = g('glGetShaderInfoLog',None,[UINT,INT,C.POINTER(INT),PTR])
    newprogram = g('glCreateProgram',UINT,[])
    attach = g('glAttachShader',None,[UINT,UINT])
    link = g('glLinkProgram',None,[UINT])
    progstatus = g('glGetProgramiv',None,[UINT,UINT,C.POINTER(INT)])
    proglog = g('glGetProgramInfoLog',None,[UINT,INT,C.POINTER(INT),PTR])

    vertex = b'''attribute vec2 in_pos;
void main(){ gl_Position=vec4(in_pos,0.0,1.0); }'''
    fragment = b'''precision highp float;
uniform sampler2D scene; uniform vec2 expanded; uniform vec2 extra;
void main(){gl_FragColor=texture2D(scene,(gl_FragCoord.xy+extra)/expanded);}'''

    def shader(tipo, codigo):
        ident = make_shader(tipo)
        pointer = C.c_char_p(codigo)
        shader_src(ident,1,C.byref(pointer),None)
        shader_compile(ident)
        ok = INT()
        shader_status(ident,0x8B81,C.byref(ok))
        if not ok.value:
            log = C.create_string_buffer(2048)
            shader_log(ident,2048,None,log)
            raise RuntimeError('GLSL: '+log.value.decode(errors='replace'))
        return ident

    prog = newprogram()
    attach(prog,shader(0x8B31,vertex))
    attach(prog,shader(0x8B30,fragment))
    link(prog)
    ok = INT()
    progstatus(prog,0x8B82,C.byref(ok))
    if not ok.value:
        log=C.create_string_buffer(2048)
        proglog(prog,2048,None,log)
        raise RuntimeError('link GLES2: '+log.value.decode(errors='replace'))

    use = g('glUseProgram',None,[UINT])
    loc = g('glGetUniformLocation',INT,[UINT,C.c_char_p])
    vec2 = g('glUniform2f',None,[INT,C.c_float,C.c_float])
    uni = g('glUniform1i',None,[INT,INT])
    genbuf = g('glGenBuffers',None,[INT,C.POINTER(UINT)])
    bindbuf = g('glBindBuffer',None,[UINT,UINT])
    data = g('glBufferData',None,[UINT,C.c_ssize_t,PTR,UINT])
    attrib = g('glGetAttribLocation',INT,[UINT,C.c_char_p])
    enable = g('glEnableVertexAttribArray',None,[UINT])
    pointer = g('glVertexAttribPointer',None,[UINT,INT,UINT,UINT,INT,PTR])
    gentex = g('glGenTextures',None,[INT,C.POINTER(UINT)])
    bindtex = g('glBindTexture',None,[UINT,UINT])
    parameter = g('glTexParameteri',None,[UINT,UINT,INT])
    create_tex = g('glTexImage2D',None,
                   [UINT,INT,INT,INT,INT,INT,UINT,UINT,PTR])
    upload = g('glTexSubImage2D',None,
               [UINT,INT,INT,INT,INT,INT,UINT,UINT,PTR])
    store = g('glPixelStorei',None,[UINT,INT])
    viewport = g('glViewport',None,[INT,INT,INT,INT])
    draw = g('glDrawArrays',None,[UINT,INT,INT])
    read = g('glReadPixels',None,[INT,INT,INT,INT,UINT,UINT,PTR])
    finish = g('glFinish',None,[])
    getstr = g('glGetString',C.c_char_p,[UINT])

    use(prog)
    coords=(C.c_float*12)(-1,-1, 1,-1, -1,1, 1,-1, 1,1, -1,1)
    vbo=UINT()
    genbuf(1,C.byref(vbo))
    bindbuf(0x8892,vbo)
    data(0x8892,C.sizeof(coords),C.cast(coords,PTR),0x88E4)
    idx=attrib(prog,b'in_pos')
    if idx<0:raise RuntimeError('GLSL atributo in_pos ausente')
    enable(idx)
    pointer(idx,2,0x1406,0,0,None)
    tex=UINT()
    gentex(1,C.byref(tex))
    bindtex(0x0DE1,tex.value)
    for par,val in ((0x2801,0x2601),(0x2800,0x2601),
                    (0x2802,0x812F),(0x2803,0x812F)):
        parameter(0x0DE1,par,val)
    store(0x0CF5,1)
    store(0x0D05,1)
    create_tex(0x0DE1,0,0x8058,w,h,0,0x1908,0x1401,None)
    viewport(0,0,w,h)
    uni(loc(prog,b'scene'),0)
    imagem=pygame.Surface((w,h)).convert()
    # Fixture deterministica; fora do jogo e sem acesso a saves/inputs.
    for y in range(h):
        pygame.draw.line(imagem,
            ((y*7)%256,(y*13)%256,(y*29)%256),(0,y),(w-1,y))
    raw=C.create_string_buffer(pygame.image.tobytes(imagem,'RGBA',True))
    pixels=C.create_string_buffer(w*h*4)
    resultado=[]
    for zoom in (0.0, .025, .034):
        ex=max(1,int(w*zoom)) if zoom else 0
        ey=max(1,int(h*zoom)) if zoom else 0
        tw,th=w+2*ex,h+2*ey
        baseline=pygame.transform.smoothscale(imagem,(tw,th))
        baseline=baseline.subsurface((ex,ey,w,h))
        ref=pygame.image.tobytes(baseline,'RGBA',True)
        vec2(loc(prog,b'expanded'),float(tw),float(th))
        vec2(loc(prog,b'extra'),float(ex),float(ey))
        t0=time.perf_counter_ns()
        upload(0x0DE1,0,0,0,w,h,0x1908,0x1401,raw)
        draw(0x0004,0,6)
        finish()
        gpu_ms=(time.perf_counter_ns()-t0)/1e6
        t0=time.perf_counter_ns()
        read(0,0,w,h,0x1908,0x1401,pixels)
        readback_ms=(time.perf_counter_ns()-t0)/1e6
        got=pixels.raw
        distintos=sum(
            ref[p:p+3]!=got[p:p+3] for p in range(0,len(ref),4))
        resultado.append({
            'zoom':zoom,'pixels_diferentes':distintos,
            'total_pixels':w*h,'upload_draw_ms':round(gpu_ms,3),
            'readback_ms':round(readback_ms,3)
        })
    return {
        'estado':'avaliado','backend':getstr(0x1F02).decode(errors='replace'),
        'renderer':getstr(0x1F01).decode(errors='replace'),
        'egl_versao':str(major.value)+'.'+str(minor.value),
        'teste':resultado,
        'identidade_sem_zoom':resultado[0]['pixels_diferentes']==0,
        'zoom_pixel_identico':all(
            r['pixels_diferentes']==0 for r in resultado[1:]),
        'aprovado':False,
        'nota':'Pesquisa offscreen: nao substitui a apresentacao SDL do jogo nem valida FPS Android.'
    }


if __name__=='__main__':
    try:
        result=executar()
    except (OSError,RuntimeError,ImportError) as exc:
        result={'estado':'indisponivel','erro':str(exc)[:220],
                'aprovado':False}
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
    # Falha somente se GL copiou erroneamente imagem SEM zoom, pois
    # isto invalida a propria comparacao; indisponibilidade e bloqueio seguro.
    if result['estado']=='avaliado' and not result['identidade_sem_zoom']:
        raise SystemExit(1)
