# -*- coding: utf-8 -*-
"""QA v3.277.40 — compositor incremental, camera e integracao GLES bloqueada."""
import os
import random
from pathlib import Path
import sys
import unittest
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame
from pixelrush_qa_rolling_v327740 import (
    FaixaPersistenteQA, mosaico_referencia, gate_integracao,
)


def bytes_rgba(s):
    return pygame.image.tobytes(s,'RGBA')


def blit_direto(destino, textura, deslocamento, top):
    largura=destino.get_width()
    periodo=textura.get_width()
    pos=-int(deslocamento)%periodo
    x=-pos
    # Mesmo strip por x, recorte automatizado pelo pygame.
    while x<largura:
        destino.blit(textura,(x,top))
        x+=periodo


class TestRollingQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def _source(self, largura, formato):
        tex=pygame.Surface((largura,170),
              pygame.SRCALPHA if formato=='rgba' else 0)
        if formato=='colorkey':
            tex.fill((255,0,255));tex.set_colorkey((255,0,255))
        elif formato=='rgb':
            tex.fill((19,44,87))
        else:
            tex.fill((0,0,0,0))
        for y in range(0,170,3):
            rgba=((y*7)%256,(y*3)%256,(y*11)%256,
                  (y*17)%256 if formato=='rgba' else 255)
            pygame.draw.rect(tex,rgba,(y*11%largura,y,60,7))
        return tex

    def test_equivalencia_sequencial_scroll_rgb_rgba_colorkey(self):
        rng=random.Random(740)
        deslocamentos=[0,1,2,3,173,174,200,450,900,1001,
                       -1,-13,-200,-900,3200]
        deslocamentos += [rng.randrange(-5000,5000) for i in range(45)]
        for formato in ('rgba','rgb','colorkey'):
            for largura in (173,450,900):
                fonte=self._source(largura,formato)
                compositor=FaixaPersistenteQA()
                for f in (0,pygame.SRCALPHA):
                    compositor.invalidar()
                    for scroll in deslocamentos:
                        referencia=mosaico_referencia(fonte,scroll)
                        atual=compositor.gerar(fonte,scroll)
                        # Saida da Surface intermediaria e do destino real
                        # passam por caminhos distintos, ambos comparados.
                        self.assertEqual(bytes_rgba(referencia),
                                         bytes_rgba(atual),
                                         (formato,largura,scroll,'buffer'))
                        a=pygame.Surface((450,400),f)
                        a.fill((29,59,91,137) if f else (29,59,91))
                        b=a.copy()
                        blit_direto(a,fonte,scroll,230)
                        b.blit(atual,(0,230))
                        self.assertEqual(bytes_rgba(a),bytes_rgba(b),
                                         (formato,largura,f,scroll,'tela'))

    def test_invalida_fonte_formato_e_teleporte(self):
        a=self._source(900,'rgba')
        b=self._source(450,'rgba')
        rolling=FaixaPersistenteQA()
        for fonte,scroll in ((a,0),(a,23),(b,27),(b,-12000),
                             (a,-5),(a,30000)):
            self.assertEqual(bytes_rgba(rolling.gerar(fonte,scroll)),
                             bytes_rgba(mosaico_referencia(fonte,scroll)))
        a.fill((12,16,220,77))
        rolling.invalidar()
        self.assertEqual(bytes_rgba(rolling.gerar(a,250)),
                         bytes_rgba(mosaico_referencia(a,250)))

    def test_gate_nao_confunde_mesa_com_android(self):
        ok={
           'pixel_exato_rgba':True,'pixel_exato_rgb':True,
           'ganho_estavel_frame_completo_android':True,
           'rss_no_limite':True,'sem_alteracoes_de_jogabilidade':True,
        }
        self.assertFalse(gate_integracao(ok,False))
        for item in ok:
            diagnostico=dict(ok)
            diagnostico[item]=False
            self.assertFalse(gate_integracao(diagnostico,True))

    def test_camera_nao_troca_backend_por_imagem_aproximada(self):
        from pixelrush_qa_gles_exact_v327736 import gate_integracao as gate_gpu
        from pixelrush_cinema_v3172 import CameraCinematica
        self.assertFalse(gate_gpu({
             'igualdade_total':True,'ganho_estavel_fps_android':True,
             'egl_android_aprovado':True,'sem_regressoes_saves_fisica':True
        },False))
        for flags in (0,pygame.SRCALPHA):
            imagem=pygame.Surface((450,800),flags)
            for y in range(800):
                pygame.draw.line(imagem,((y*7)%256,(y*11)%256,(y*3)%256,
                    (y*13)%256) if flags else ((y*7)%256,(y*11)%256,(y*3)%256),
                    (0,y),(449,y))
            cam=CameraCinematica()
            cam.zoom=.02
            cam.foco_y=3
            player=type('Player',(),{
                'no_chao':False,'rect':pygame.Rect(175,590,35,70)
            })()
            resultado=cam.aplicar(imagem,player,12,True,True)
            w,h=imagem.get_size()
            x=max(1,int(w*cam.zoom));y=max(1,int(h*cam.zoom))
            yy=max(0,min(2*y,y+int(cam.foco_y)))
            referencia=pygame.transform.smoothscale(imagem,(w+2*x,h+2*y))
            self.assertEqual(bytes_rgba(resultado),
                bytes_rgba(referencia.subsurface((x,yy,w,h))))


if __name__=='__main__':
    unittest.main(verbosity=2)
