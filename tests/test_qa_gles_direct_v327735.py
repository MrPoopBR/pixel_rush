# -*- coding: utf-8 -*-
"""Teste QA isolado. glReadPixels SOMENTE nesta suite, nunca no renderer.

Checa uma janela SDL com GLES2 e swap real, compara a GPU com a camera
pygame-ce byte a byte e bloqueia integracao sem equivalencia.
"""
import ast
import ctypes as C
import json
import os
from pathlib import Path
import random
import sys
import time
import unittest

os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame
from pixelrush_qa_gles_present_v327735 import GLES2DirectPresenterQA

W,H=450,800
RESULT=Path(os.environ.get('PIXELRUSH_QA_GLES_REPORT',
                           'qa-gles-direct-v327735.json'))


def imagem(tipo):
    superficie=pygame.Surface((W,H)).convert()
    rng=random.Random(327735)
    for y in range(H):
        if tipo=='gradient':
            cor=((y*7)%256,(y*13)%256,(y*29)%256)
        elif tipo=='checker':
            cor=((y//8)%2*255,(y//16)%2*255,(y//32)%2*255)
        else:
            cor=tuple(rng.randrange(256) for _ in range(3))
        pygame.draw.line(superficie,cor,(0,y),(W-1,y))
    if tipo=='checker':
        for x in range(0,W,17):
            pygame.draw.line(superficie,(17,181,240),(x,0),(x,H-1),2)
    elif tipo=='random':
        for j in range(120):
            pygame.draw.circle(superficie,
                (rng.randrange(256),rng.randrange(256),rng.randrange(256)),
                (rng.randrange(W),rng.randrange(H)),rng.randrange(2,14))
    return superficie


def zoom_original(surface,zoom,focus):
    if not zoom:
        return surface
    ex=max(1,int(W*zoom))
    ey=max(1,int(H*zoom))
    resultado=pygame.transform.smoothscale(
        surface,(W+2*ex,H+2*ey))
    sy=max(0,min(2*ey,ey+int(focus)))
    return resultado.subsurface((ex,sy,W,H))


class TestGLESDirectQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.presenter=GLES2DirectPresenterQA(W,H)
        # Estritamente para validacao pixel a pixel OFFLINE/CI.
        # O renderer e a apresentacao NAO podem importar glReadPixels.
        try:
            lib=C.CDLL(None)
            cls.read=lib.glReadPixels
        except AttributeError:
            raise unittest.SkipTest('glReadPixels nao exposto pelo driver de teste')
        cls.read.restype=None
        cls.read.argtypes=[C.c_int,C.c_int,C.c_int,C.c_int,
                           C.c_uint,C.c_uint,C.c_void_p]
        cls.cases=[]

    @classmethod
    def tearDownClass(cls):
        cls.presenter.close()

    def test_copy_zoom_and_gl_swap(self):
        for tipo in ('gradient','random','checker'):
            surface=imagem(tipo)
            for zoom,focus in ((0.0,0),(.012,3),(.025,0),(.034,-4)):
                cpu_start=time.perf_counter_ns()
                original=zoom_original(surface,zoom,focus)
                cpu_ms=(time.perf_counter_ns()-cpu_start)/1e6
                self.presenter.draw(surface,zoom,focus)
                pixels=C.create_string_buffer(W*H*4)
                # Este e o UNICO ponto autorizado a ler GPU->CPU,
                # fora do pipeline de apresentacao, somente para comparar.
                self.read(0,0,W,H,0x1908,0x1401,pixels)
                gpu=pixels.raw
                ref=pygame.image.tobytes(original,'RGBA',True)
                dif=0
                delta_max=0
                delta_soma=0
                for i in range(0,len(ref),4):
                    canais=[abs(gpu[i+c]-ref[i+c]) for c in range(3)]
                    if any(canais):
                        dif+=1
                    delta_max=max(delta_max,*canais)
                    delta_soma+=sum(canais)
                item={'imagem':tipo,'zoom':zoom,'foco':focus,
                      'total_pixels':W*H,'pixels_diferentes':dif,
                      'delta_max_rgb':delta_max,
                      'erro_medio_rgb':round(delta_soma/(W*H*3),3),
                      'tempo_cpu_smoothscale_ms':round(cpu_ms,3),
                      'tempo_chamadas_upload_draw_ms':
                          round(self.presenter.cpu_upload_draw_ns/1e6,3)}
                self.cases.append(item)
                if zoom==0:
                    self.assertEqual(dif,0,'Copia RGB divergente')
                self.presenter.present()
        report={
            'schema':'pixelrush.qa.gles_direct.v1',
            'ambiente':'Linux/Xvfb GL ES2 Mesa; NAO representa Android',
            'gpu_renderer':self.presenter.diagnostico(),
            'testes':self.cases,
            'gpu_readbacks_durante_apresentacao':0,
            'gpu_readbacks_apenas_para_validacao':len(self.cases),
            'equivalencia_visual':all(x['pixels_diferentes']==0
                                      for x in self.cases),
            'ganho_android_comprovado':False,
            'integracao_jogo_aprovada':False,
        }
        RESULT.write_text(json.dumps(report,ensure_ascii=False,indent=2),
                          encoding='utf8')
        self.assertEqual(len(self.cases),12)
        self.assertEqual(self.presenter.frame_count,12)
        self.assertEqual(self.presenter.readbacks,0)
        # Os 9 testes com zoom reportam quaisquer diferencas, mas
        # nao alteram o jogo nem se fazem passar por homologacao.
        self.assertTrue(any(x['pixels_diferentes']>0
                            for x in self.cases if x['zoom']!=0))

    def test_no_gpu_to_cpu_in_presenter_and_main_unchanged(self):
        code=(ROOT/'pixelrush_qa_gles_present_v327735.py').read_text('utf8')
        tree=ast.parse(code)
        clase=next(x for x in tree.body if isinstance(x,ast.ClassDef)
                   and x.name=='GLES2DirectPresenterQA')
        for method in ('draw','present'):
            fun=next(x for x in clase.body if isinstance(x,ast.FunctionDef)
                     and x.name==method)
            for node in ast.walk(fun):
                if isinstance(node,ast.Call):
                    name=getattr(node.func,'attr',getattr(node.func,'id',None))
                    self.assertNotEqual(name,'glReadPixels')
        main=(ROOT/'main.py').read_text('utf8')
        prod=(ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        self.assertNotIn('GLES2DirectPresenterQA',main)
        self.assertNotIn('GLES2DirectPresenterQA',prod)
        self.assertIn('VERSAO = "v3.277.36-QA-ANDROID-RC"',prod)
        self.assertIn('MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15',prod)
        self.assertIn('FPS_RENDER = 30 if E_ANDROID else 60',prod)
        self.assertIn('PIXELRUSH_DEV_BUILD = False',prod)


if __name__=='__main__':
    unittest.main(verbosity=2)
