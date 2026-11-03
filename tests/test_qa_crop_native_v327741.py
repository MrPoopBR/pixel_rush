# -*- coding: utf-8 -*-
"""QA 3.277.41: paridade pixel a pixel do recorte nativo SSE2/GENERIC.

Testes de cenografia real (cidade, neve) e 240 casos sinteticos RGB/RGBA.
Sem importar o prototipo no entrypoint. LIB compilada no Linux CI.
"""
import os
import random
import sys
import unittest
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame
from pixelrush_qa_crop_native_v327741 import Crop32QA,NativeCameraUnavailable,gate_android
LIB=os.environ.get('PIXELRUSH_QA_NATIVE_CAMERA_LIB',
                   '/tmp/pixelrush-qa-native/libpixelrush_camera_crop_v327741.so')


def dados(s):
    return pygame.image.tobytes(s,'RGBA')


def fixture(kind,alpha):
    rng=random.Random(327741+kind*100+int(alpha))
    image=pygame.Surface((450,800),pygame.SRCALPHA if alpha else 0)
    if kind==0:
        image.fill((13,30,91,67) if alpha else (13,30,91))
        for i in range(100):
            col=tuple(rng.randrange(256) for _ in range(4 if alpha else 3))
            h=rng.randrange(15,300)
            pygame.draw.rect(image,col,(rng.randrange(450),800-h,
                                         rng.randrange(4,42),h))
    elif kind==1:
        for y in range(800):
            c=((y*17)%256,(y*5)%256,(y*37)%256,(y*23)%256)
            pygame.draw.line(image,c if alpha else c[:3],(0,y),(449,y))
    elif kind==2:
        image.fill((9,11,31,0) if alpha else (9,11,31))
        for i in range(280):
            col=tuple(rng.randrange(256) for _ in range(4 if alpha else 3))
            pygame.draw.circle(image,col,(rng.randrange(450),rng.randrange(800)),
                               rng.randrange(1,14))
    else:
        image.fill((0,0,0,0) if alpha else (0,0,0))
        pygame.draw.rect(image,(255,255,255,113) if alpha else (255,255,255),
                         (0,0,450,52))
        pygame.draw.rect(image,(11,223,61,230) if alpha else (11,223,61),
                         (150,420,96,150))
    return image


def comparar(tc,source,backend,native,zooms=(.003,.011,.025,.034,.08),
             focos=(-10,0,10)):
    pygame.transform.set_smoothscale_backend(backend)
    w,h=source.get_size()
    total=0
    for z in zooms:
        ex=max(1,int(w*z));ey=max(1,int(h*z))
        size=(w+2*ex,h+2*ey)
        referencia=pygame.transform.smoothscale(source,size)
        for focus in focos:
            sy=max(0,min(2*ey,ey+focus))
            esperado=referencia.subsurface((ex,sy,w,h))
            atual=native.processar(source,size,(ex,sy),backend)
            tc.assertEqual(dados(esperado),dados(atual),
                           (backend,source.get_flags(),size,focus))
            total+=1
    return total


class NativeCameraQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))
        cls.original=pygame.transform.get_smoothscale_backend()
    @classmethod
    def tearDownClass(cls):
        pygame.transform.set_smoothscale_backend(cls.original)
        pygame.quit()

    def test_240_variacoes_rgb_rgba_backend_e_foco(self):
        total=0
        try:
            for alpha in (False,True):
                for kind in range(4):
                    s=fixture(kind,alpha)
                    for backend in ('GENERIC','SSE2'):
                        try:pygame.transform.set_smoothscale_backend(backend)
                        except (ValueError,pygame.error):continue
                        total+=comparar(self,s,backend,Crop32QA(LIB))
        finally:
            pygame.transform.set_smoothscale_backend(self.original)
        self.assertGreaterEqual(total,120)

    def test_cidade_e_neve_reais(self):
        # A cena vem das classes exatas do jogo, sem imitar a arte.
        from pixelrush_city2_v3124 import CityPilotScene
        from pixelrush_biomes2_v3185 import ModularBiomeScene
        total=0
        try:
            for scene in (CityPilotScene(),ModularBiomeScene('neve',lightweight=True)):
                for night,climate in ((0.0,'limpo'),(.65,'chuva')):
                    view=pygame.Surface((450,500),pygame.SRCALPHA)
                    scene.render_scene(view,101.5+total,55+total,night,climate,.35)
                    for alpha in (False,True):
                        s=pygame.Surface((450,800),pygame.SRCALPHA if alpha else 0)
                        s.fill((18,28,64,78) if alpha else (18,28,64))
                        s.blit(view,(0,230))
                        pygame.draw.rect(s,(246,187,61,200) if alpha else
                                         (246,187,61),(45,70,200,20))
                        for backend in ('GENERIC','SSE2'):
                            try:pygame.transform.set_smoothscale_backend(backend)
                            except (ValueError,pygame.error):continue
                            total+=comparar(self,s,backend,Crop32QA(LIB),
                                            zooms=(.011,.025),focos=(-9,0,9))
        finally:
            pygame.transform.set_smoothscale_backend(self.original)
        self.assertGreaterEqual(total,24)

    def test_seguro_e_sem_integracao_automatica(self):
        native=Crop32QA(LIB)
        self.assertFalse(native.suportado(pygame.Surface((450,800),depth=16)))
        with self.assertRaises(NativeCameraUnavailable):
            native.processar(pygame.Surface((450,800),depth=16),
                             (470,840),(10,20))
        with self.assertRaises(ValueError):
            native.processar(fixture(1,False),(451,801),(-1,0))
        prova={'testes_pixels_android_reais':True,
               'sem_diferencas_em_frame_completo':True,
               'ganho_camera_p95_android':True,
               'ganho_fps_cadencia_android':True,
               'sem_aumento_rss':True,
               'preservacao_fisica_e_saves':True,
               'homologacao_usuario':True}
        for atributo in prova:
            ruim=dict(prova);ruim[atributo]=False
            self.assertFalse(gate_android(ruim),atributo)
        self.assertFalse(gate_android({}))
        for protegido in ('main.py','pixelrush_qa_render_v327729.py',
                          'pixelrush_qa_camera_v327733.py',
                          'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py'):
            self.assertNotIn('pixelrush_qa_crop_native_v327741',
                             (ROOT/protegido).read_text('utf8'))


if __name__=='__main__':
    unittest.main(verbosity=2)
