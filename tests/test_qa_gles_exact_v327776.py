# -*- coding: utf-8 -*-
"""Regressão REAL pygame-ce 2.5.8/GLES2 e GLES3 em 450x800.

720 casos: 6 fixtures RGB/RGBA x 10 zooms x 3 focos x
(ES2,ES3) x (SSE2,GENERIC). Leitura da GPU APENAS no teste,
em framebuffer RGBA8 para não perder alpha na janela SDL.
CI de pesquisa: mesmo com pixels iguais, não ativa GPU no jogo.
"""
import ctypes as C
import json
import os
import random
import statistics
import sys
import time
import unittest
from pathlib import Path

os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
import pygame
import pixelrush_qa_gles_present_v327735 as previous
from pixelrush_qa_gles_exact_v327736 import shaders, geometria_camera, gate_integracao

SIZE=(450,800)
W,H=SIZE
OUT=Path(os.environ.get('PIXELRUSH_QA_GLES_EXACT_REPORT',
                        'qa-gles-exact-v327736.json'))


def fixtures():
    rng=np.random.default_rng(327736)
    rgba=rng.integers(0,256,(H,W,4),dtype=np.uint8)
    result={}
    result['random_rgb']=pygame.image.frombuffer(
        rgba.copy().tobytes(),SIZE,'RGBA').convert()
    result['random_rgba']=pygame.image.frombuffer(
        rgba.copy().tobytes(),SIZE,'RGBA').convert_alpha()
    for name in ('horizontal','vertical','checker','transparent'):
        s=pygame.Surface(SIZE,pygame.SRCALPHA if name=='transparent' else 0)
        if name=='horizontal':
            for y in range(H):
                pygame.draw.line(s,((y*3)%256,(y*7)%256,(y*13)%256),
                                 (0,y),(W-1,y))
        elif name=='vertical':
            for x in range(W):
                pygame.draw.line(s,((x*3)%256,(x*7)%256,(x*13)%256),
                                 (x,0),(x,H-1))
        elif name=='checker':
            for y in range(H):
                pygame.draw.line(s,((255 if (y//7)%2 else 0),
                                    (255 if (y//11)%2 else 0),
                                    (255 if (y//13)%2 else 0)),
                                 (0,y),(W-1,y))
        else:
            for x in range(0,W,7):
                pygame.draw.line(s,((x*13)%256,110,220,(x*17)%256),
                                 (x,0),(x,H-1))
        result[name]=s
    return result


def original(source,zoom,focus):
    if zoom < .002:
        return source
    ex=max(1,int(W*zoom));ey=max(1,int(H*zoom))
    sy=max(0,min(2*ey,ey+int(focus)))
    scaled=pygame.transform.smoothscale(source,(W+2*ex,H+2*ey))
    return scaled.subsurface((ex,sy,W,H))


def framebuffer_rgba8(p):
    f=p._f
    gl=p.gl
    def add(name,result,args):
        fn=getattr(gl,name)
        fn.restype,fn.argtypes=result,args
        f[name]=fn
    add('glGenFramebuffers',None,[C.c_int,C.POINTER(C.c_uint)])
    add('glBindFramebuffer',None,[C.c_uint,C.c_uint])
    add('glFramebufferTexture2D',None,
        [C.c_uint,C.c_uint,C.c_uint,C.c_uint,C.c_int])
    add('glCheckFramebufferStatus',C.c_uint,[C.c_uint])
    tx=C.c_uint()
    f['glGenTextures'](1,C.byref(tx))
    f['glBindTexture'](0x0DE1,tx.value)
    f['glTexParameteri'](0x0DE1,0x2801,0x2600)
    f['glTexParameteri'](0x0DE1,0x2800,0x2600)
    f['glTexImage2D'](0x0DE1,0,0x1908,W,H,0,0x1908,0x1401,None)
    fbo=C.c_uint()
    f['glGenFramebuffers'](1,C.byref(fbo))
    f['glBindFramebuffer'](0x8D40,fbo.value)
    f['glFramebufferTexture2D'](0x8D40,0x8CE0,0x0DE1,tx.value,0)
    status=f['glCheckFramebufferStatus'](0x8D40)
    if status != 0x8CD5:
        raise RuntimeError('Frame RGBA8 incompleto: '+hex(status))
    read=gl.glReadPixels
    read.restype=None
    read.argtypes=[C.c_int,C.c_int,C.c_int,C.c_int,C.c_uint,
                   C.c_uint,C.c_void_p]
    return f,read


def highp_mantissa(p):
    gl=p.gl
    try:
        fn=gl.glGetShaderPrecisionFormat
        fn.restype=None
        fn.argtypes=[C.c_uint,C.c_uint,C.POINTER(C.c_int),
                     C.POINTER(C.c_int)]
        bounds=(C.c_int*2)()
        precision=C.c_int()
        fn(0x8B30,0x8DF2,bounds,C.byref(precision)) # fragment, HIGH_FLOAT
        return precision.value
    except AttributeError:
        return -1


class ShaderPixelExactQA(unittest.TestCase):
    def test_regressao_real_rgba_e_benchmark(self):
        pygame.init()
        pygame.display.set_mode(SIZE)
        sources=fixtures()
        tests=[]
        stats=[]
        pairs=[]
        # Esta bancada deve testar COMPARACAO, nao ativar a câmera do jogo.
        for api in ('GLES2','GLES3'):
            for backend in ('SSE2','GENERIC'):
                pygame.transform.set_smoothscale_backend(backend)
                previous.VERT,previous.FRAG=shaders(api,backend,SIZE)
                try:
                    p=previous.GLES2DirectPresenterQA(*SIZE)
                except Exception as exc:
                    if api=='GLES3' and 'Shader GLES2 falhou' in str(exc):
                        stats.append({'api':api,'backend':backend,
                                      'estado':'indisponivel',
                                      'motivo':str(exc)[:150]})
                        pygame.display.quit()
                        continue
                    raise
                try:
                    precision=highp_mantissa(p)
                    if api=='GLES2' and precision != -1 and precision<23:
                        stats.append({'api':api,'backend':backend,
                                      'estado':'sem_alta_precisao',
                                      'bits':precision})
                        continue
                    f,read=framebuffer_rgba8(p)
                    failed=0;max_delta=0;count=0
                    upload=[]
                    for kind,source in sources.items():
                        for zoom in (0,.002,.003,.008,.012,.024,.025,.034,.05,.08):
                            for focus in (-10,0,10):
                                expected=original(source,zoom,focus)
                                p.draw(source,zoom,focus)
                                buf=C.create_string_buffer(W*H*4)
                                read(0,0,W,H,0x1908,0x1401,buf)
                                gpu=np.frombuffer(buf.raw,dtype=np.uint8)
                                cpu=np.frombuffer(pygame.image.tobytes(
                                    expected,'RGBA',True),dtype=np.uint8)
                                delta=np.abs(gpu.astype(np.int16)-cpu.astype(np.int16))
                                dif=int(np.count_nonzero(delta))
                                failed+=int(dif!=0)
                                max_delta=max(max_delta,int(delta.max()))
                                count+=1
                                upload.append(p.cpu_upload_draw_ns/1e6)
                                if dif:
                                    tests.append({'api':api,'backend':backend,
                                                  'cena':kind,'zoom':zoom,
                                                  'foco':focus,'canais_diferentes':dif})
                    # Fluxo de apresentacao real SEM readback:
                    # FBO usado EXCLUSIVAMENTE acima para verificar alpha.
                    f['glBindFramebuffer'](0x8D40,0)
                    src=sources['random_rgb']
                    p.draw(src,.025,0)
                    p.present()
                    self.assertEqual(p.readbacks,0)
                    stats.append({'api':api,'backend':backend,'estado':'medido',
                                  'contexto':p.version,'renderer':p.renderer,
                                  'mantissa_highp':precision,'casos':count,
                                  'casos_diferentes':failed,'delta_max':max_delta,
                                  'median_upload_draw_ms':round(statistics.median(upload),4),
                                  'presentacao_readbacks':p.readbacks,
                                  'swap':p.swap_method})
                    pairs.append((api,backend,count,failed))
                finally:
                    p.close()
        dados={
            'schema':'pixelrush.qa.gles_exact.v1',
            'pygame_ce':'2.5.8',
            'plataforma':'Linux Mesa Xvfb; GPU Android nao medida',
            'metodos':stats,
            'divergencias':tests[:50],
            'total_casos':sum(x[2] for x in pairs),
            'igualdade_total':all(x[3]==0 for x in pairs) and bool(pairs),
            'ganho_estavel_fps_android':False,
            'egl_android_aprovado':False,
            'sem_regressoes_saves_fisica':False,
            'integracao_gpu_aprovada':False,
        }
        dados['integracao_gpu_aprovada']=gate_integracao(dados,False)
        OUT.write_text(json.dumps(dados,indent=2,ensure_ascii=False),
                       encoding='utf8')
        self.assertTrue(pairs,'Nenhum shader ES compilou')
        self.assertTrue(all(x[3]==0 for x in pairs),str(tests[:3]))
        self.assertFalse(dados['integracao_gpu_aprovada'])
        self.assertFalse(any(x.get('presentacao_readbacks',0)
                             for x in stats))

    def test_geometria_e_permissao(self):
        expanded,crop=geometria_camera(450,800,.025,3)
        self.assertEqual(expanded,(472,840))
        # extra_y = 20; sy=23 -> bottom crop=17
        self.assertEqual(crop,(11,17))
        self.assertEqual(geometria_camera(450,800,.001,9),
                         ((450,800),(0,0)))
        self.assertFalse(gate_integracao({'igualdade_total':True},False))
        self.assertFalse(gate_integracao({'igualdade_total':True,
                                         'ganho_estavel_fps_android':True,
                                         'egl_android_aprovado':True,
                                         'sem_regressoes_saves_fisica':True},False))
        assert 'GLES2DirectPresenterQA' not in (ROOT/'main.py').read_text('utf8')
        assert 'pixelrush_qa_gles_exact_v327736' not in (ROOT/'main.py').read_text('utf8')
        code=(ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        self.assertIn('VERSAO = "v3.277.84-QA-ANDROID-RC"',code)
        self.assertIn('MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15',code)
        self.assertIn('FPS_RENDER = 30 if E_ANDROID else 60',code)
        self.assertIn('PIXELRUSH_DEV_BUILD = False',code)


if __name__=='__main__':
    unittest.main(verbosity=2)
