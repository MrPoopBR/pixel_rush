# -*- coding: utf-8 -*-
"""QA783: regressao real RGBA/pygame e falhas de backends R13."""
import ast
import os
import sys
import statistics
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ['PIXELRUSH_QA_CITY_INCREMENTAL']='1'
os.environ['PIXELRUSH_QA_CITY_RLE_FASTPATH']='1'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame
import pixelrush_qa_incremental_scene_v327750 as scroll
import pixelrush_qa_camera_native_auto_v327742 as camera
import pixelrush_qa_gles_bridge_v327749 as gles

ROOT=Path(__file__).resolve().parents[1]

class FakeNative:
    @staticmethod
    def suportado(s):
        return True
    def processar(self,s,size,crop,backend=None):
        img=pygame.transform.smoothscale(s,size)
        return img.subsurface((*crop,*s.get_size())).copy()

class DummyCamera:
    zoom=0.0
    foco_y=0.0

class QuatroBackendsQA783(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        scroll.restaurar_para_teste()
        pygame.quit()

    def test_glteximage2d_declara_nove_argumentos(self):
        fonte=(ROOT/'pixelrush_qa_gles_present_v327735.py').read_text('utf8')
        tree=ast.parse(fonte)
        chamadas=[node for node in ast.walk(tree)
                  if isinstance(node,ast.Call) and
                     isinstance(node.func,ast.Name) and
                     node.func.id=='f' and node.args and
                     isinstance(node.args[0],ast.Constant) and
                     node.args[0].value=='glTexImage2D']
        self.assertEqual(len(chamadas),1)
        self.assertEqual(len(chamadas[0].args[2].elts),9)
        self.assertIn('except ImportError:',fonte)

    def test_fullscreen_fallback_nao_recria_janela_pequena(self):
        chamadas=[]
        def setmode(size,flags=0,depth=0,display=0,vsync=0):
            chamadas.append((tuple(size),flags))
            return pygame.Surface((450,800))
        ponte=gles._Ponte()
        flags=pygame.SCALED|pygame.FULLSCREEN
        with patch.dict(os.environ,{'PIXELRUSH_QA_GLES_FULLSCREEN_PROBE':'1'}),\
             patch.dict(gles._ORIGINALS,{'set_mode':setmode}),\
             patch.dict(sys.modules,{'pixelrush_qa_gles_present_v327735':None}):
            superficie=ponte.set_mode((450,800),flags)
        self.assertEqual(superficie.get_size(),(450,800))
        self.assertEqual(chamadas,[((450,800),flags)])
        self.assertEqual(ponte.modo,'fallback')
        self.assertEqual(gles.diagnostico()['falha_modulo'],
                         'pixelrush_qa_gles_present_v327735')

    def test_preflight_neon_multigeometria_preserva_zoom(self):
        origem=pygame.Surface((72,108),depth=32).convert()
        for y in range(108):
            pygame.draw.line(origem,((y*17)%256,(y*43)%256,
                                     (y*101)%256),(0,y),(71,y))
        cam=DummyCamera()
        pessoa=SimpleNamespace(no_chao=True,rect=pygame.Rect(10,66,15,20))
        camera._REPORT['casos_rgba']=0
        with patch.object(camera,'_load_native',return_value=FakeNative()):
            camera._verificar_primeiro_frame(
                origem,cam,pessoa,velocidade=12.0,momento=False,ativo=True)
        self.assertEqual((cam.zoom,cam.foco_y),(0.0,0.0))
        self.assertGreaterEqual(camera.diagnostico()['casos_rgba'],3)
        self.assertTrue(camera.diagnostico()['pixels_exatos'])

    def test_cidade_rle_usa_blt_original_e_rgba_exato(self):
        from pixelrush_city2_v3125 import CityPilotScene
        from pixelrush_city2_v3115 import SCENE_H,SCENE_W
        scroll.instalar()
        self.assertTrue(scroll.diagnostico()['habilitado_cidade'])
        source=pygame.Surface((SCENE_W,SCENE_H),pygame.SRCALPHA,32)
        source.fill((211,37,117,0))
        for i in range(0,SCENE_W,17):
            pygame.draw.rect(source,((i*9)%256,(i*17)%256,
                                     (i*37)%256,80+i%175),(i,11,14,SCENE_H-22))
        source.set_alpha(255,pygame.RLEACCEL)
        mask=pygame.RLEACCEL|getattr(pygame,'RLEACCELOK',0)
        self.assertTrue(source.get_flags() & mask)
        scene=object.__new__(CityPilotScene)
        scene._scaled_surface=lambda variant,kind:source
        scene._qa_uniform_tech={}
        scene._qa_alpha_bounds={}
        scene._qa_empty_base_maps=set()
        scene._qa_opaque_safe_target=None
        variant=SimpleNamespace(image=source,sprites=[])
        original=scroll._ORIGINAIS['chunk']
        posicoes=(-350,-225,-80,0,75,240,400)
        ratios=[]
        for flags in (0,pygame.SRCALPHA):
            for x in posicoes:
                base=pygame.Surface((450,500),flags,32)
                base.fill((21,33,105,0) if flags else (21,33,105))
                pygame.draw.rect(base,(149,211,61,77) if flags else
                                     (149,211,61),(40,70,240,160))
                ref=base.copy()
                atual=base.copy()
                original(scene,ref,variant,False,x,33,0.2,'limpo',0.4,'image',False)
                scene._render_chunk(atual,variant,False,x,33,0.2,'limpo',0.4,'image',False)
                self.assertEqual(pygame.image.tobytes(ref,'RGBA'),
                                 pygame.image.tobytes(atual,'RGBA'),(flags,x))
        self.assertGreater(scroll.diagnostico()['cidade_rle_fastpath'],0)
        base=pygame.Surface((450,500),pygame.SRCALPHA,32)
        for x in (0,-60,120):
            direta=[];rapida=[]
            for _ in range(45):
                target=base.copy()
                t=time.perf_counter_ns()
                original(scene,target,variant,False,x,33,0.2,'limpo',0.4,'image',False)
                direta.append(time.perf_counter_ns()-t)
                target=base.copy()
                t=time.perf_counter_ns()
                scene._render_chunk(target,variant,False,x,33,0.2,'limpo',0.4,'image',False)
                rapida.append(time.perf_counter_ns()-t)
            ratios.append(round(statistics.median(direta)/
                                max(1,statistics.median(rapida)),3))
        print('QA783 RLE direct/fastpath p50 ratios:',ratios)

if __name__=='__main__':
    unittest.main(verbosity=2)
