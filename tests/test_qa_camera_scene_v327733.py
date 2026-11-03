# -*- coding: utf-8 -*-
"""Regressoes v3.277.33-QA: nuvens/panoramas e camera byte-identicos."""
import hashlib
import os
from pathlib import Path
import random
import sys
import time
import unittest

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import pygame

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def imagem(src):
    canal='RGBA' if src.get_flags() & pygame.SRCALPHA else 'RGB'
    return pygame.image.tobytes(src,canal)


class QA327733(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_nuvens_rgb_rgba_igual_ao_original(self):
        import pixelrush_cenarios_v398 as visual
        from pixelrush_qa_scene_v327733 import instalar, restaurar_para_teste
        restaurar_para_teste()
        rng=random.Random(337733)
        amostras=[]
        for fmt in ('RGB','RGBA'):
            for rep in range(24):
                pos=[]
                for i in range(6):
                    pos.append((rng.randint(-70,450), rng.randint(-18,220)))
                cores=(tuple(rng.randint(10,240) for _ in range(3)),
                       tuple(rng.randint(10,240) for _ in range(3)),
                       tuple(rng.randint(10,240) for _ in range(3)))
                amostras.append((fmt,pos,cores))
        def renderizar(fn, fmt, pos, cores):
            target=(pygame.Surface((450,800),pygame.SRCALPHA)
                    if fmt=='RGBA' else pygame.Surface((450,800)).convert())
            target.fill((27,83,129,88) if fmt=='RGBA' else (27,83,129))
            for x,y in pos:
                fn(target,x,y,1,*cores)
            return imagem(target)
        original=visual.nuvem_pixel
        esperados=[renderizar(original,*a) for a in amostras]
        try:
            instalar()
            for n,a in enumerate(amostras):
                self.assertEqual(esperados[n],renderizar(visual.nuvem_pixel,*a),
                                 'nuvens amostra '+str(n))
        finally:
            restaurar_para_teste()

    def test_cenario_ceu_pixel_igual_sete_biomas(self):
        import pixelrush_cenarios_v398 as visual
        from pixelrush_qa_scene_v327733 import instalar, restaurar_para_teste
        restaurar_para_teste()
        biomas=['cidade','neve','deserto','vulcao','floresta',
                'cidade_futurista','ilhas_celestes']
        estrelas=[{'x':(i*41)%450,'y':(i*37)%305,
                   'blink':.03+i*.001,'offset':i*.15} for i in range(40)]
        nuvens=[{'x':i*79-24,'y':35+(i%4)*27} for i in range(6)]
        cenarios=[(b,f,n) for b in biomas
                  for f,n in ((.15,0.),(.45,.22),(.88,.75),(1.,1.))]
        def render():
            out=[]
            for b,f,n in cenarios:
                surface=pygame.Surface((450,800)).convert()
                surface.fill((13,38,74))
                visual.desenhar_ceu(surface,(61,123,182),f,n,b,estrelas,275,nuvens)
                out.append(hashlib.sha256(imagem(surface)).hexdigest())
            return out
        esperado=render()
        try:
            instalar()
            self.assertEqual(esperado,render())
        finally:
            restaurar_para_teste()

    def test_camera_equivalente_e_backend_restaurado(self):
        from pixelrush_cinema_v3172 import CameraCinematica
        from pixelrush_qa_camera_v327733 import instalar, restaurar_para_teste, resultado
        restaurar_para_teste()
        imagem0=pygame.Surface((450,800)).convert()
        for y in range(800):
            pygame.draw.line(imagem0,((y*7)%256,(y*3)%256,(y*13)%256),
                             (0,y),(449,y))
        class Jogador:
            no_chao=True
            rect=pygame.Rect(120,600,45,68)
        ref=CameraCinematica()
        fromqa=CameraCinematica()
        jogador=Jogador()
        backend_inicial=pygame.transform.get_smoothscale_backend()
        try:
            instalar()
            # Guarda referencia do metodo antes do patch via teste independente.
            from pixelrush_qa_camera_v327733 import _ORIGINAL
            for idx in range(42):
                if idx % 11==0:
                    jogador.no_chao=not jogador.no_chao
                args=dict(jogador=jogador, velocidade=11.5+idx*.05,
                          momento=idx%7==0,ativo=True)
                esperado=_ORIGINAL(ref, imagem0,**args)
                obtido=fromqa.aplicar(imagem0,**args)
                self.assertEqual(imagem(esperado),imagem(obtido),
                                 'camera '+str(idx))
                self.assertEqual(pygame.transform.get_smoothscale_backend(),
                                 backend_inicial)
        finally:
            restaurar_para_teste()

    def test_escopo_fisica_e_profiling(self):
        main=(ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        telemetria=(ROOT/'pixelrush_qa_android_v327728.py').read_text('utf8')
        workflow=(ROOT/'.github/workflows/qa-apk-debug-v327733.yml').read_text('utf8')
        self.assertIn('VERSAO = "v3.277.46-QA-ANDROID-RC"',main)
        self.assertIn('MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15',main)
        self.assertIn('FPS_RENDER = 30 if E_ANDROID else 60',main)
        self.assertIn('PIXELRUSH_DEV_BUILD = False',main)
        self.assertIn('cenario_panorama',telemetria)
        self.assertIn('cenario_animacoes_frente',telemetria)
        self.assertIn('camera_backend_autotune_qa',telemetria)
        self.assertIn("buildozer -v android debug",workflow)
        self.assertNotIn("buildozer -v android release",workflow)


if __name__=='__main__':
    unittest.main(verbosity=2)
