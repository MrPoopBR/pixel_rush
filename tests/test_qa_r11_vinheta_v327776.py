# -*- coding: utf-8 -*-
"""R11/A54 QA776: vinheta real, RGB/RGBA bytes, fallback e benchmark SDL."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ['PIXELRUSH_QA_ANDROID']='1'
import random,statistics,time,unittest
import pygame
from pixelrush_gamefeel_v3129 import GameFeel
import pixelrush_qa_r11_vinheta_v327776 as qa

def rgba(s):
    return pygame.image.tobytes(s,'RGBA')

class VignetteQA776(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    def setUp(self):qa.restaurar_para_teste()

    def test_gamefeel_original_igual_rgb_rgba_oculto(self):
        obj=GameFeel()
        rnd=random.Random(327776)
        for flags,bpp in ((0,16),(0,24),(0,32),(pygame.SRCALPHA,32)):
            for alpha in (0,1,48,127,255):
                dest=pygame.Surface((450,800),flags,bpp)
                dest.fill((31,57,99,alpha) if flags else (31,57,99))
                for _ in range(72):
                    color=(rnd.randrange(256),rnd.randrange(256),rnd.randrange(256),
                           rnd.choice((0,1,127,255)))
                    pygame.draw.rect(dest,color if flags else color[:3],
                        (rnd.randrange(450),rnd.randrange(800),17,39))
                esperado=dest.copy();novo=dest.copy()
                esperado.blit(obj._vinheta,(0,0))
                obj.desenhar(novo,jogador=None,combo=0)
                self.assertEqual(rgba(esperado),rgba(novo),(flags,bpp,alpha))
        self.assertEqual(qa.diagnostico()['rapido'],15)
        self.assertEqual(qa.diagnostico()['fallback'],5)
        self.assertEqual(qa.diagnostico()['verificacoes'],1)

    def test_centro_inesperado_fallback(self):
        obj=GameFeel()
        s=obj._vinheta.copy();s.set_at((225,400),(17,91,223,1))
        d=pygame.Surface((450,800),0,32)
        d.fill((53,97,101));ref=d.copy();ref.blit(s,(0,0))
        qa.desenhar_vinheta(d,s)
        self.assertEqual(rgba(ref),rgba(d))
        self.assertEqual(qa.diagnostico()['centro_rejeitado'],1)
        self.assertEqual(qa.diagnostico()['fallback'],1)

    def test_rollback_optout(self):
        s=GameFeel()._vinheta
        dest=pygame.Surface((450,800))
        old=os.environ.get('PIXELRUSH_QA_R11_VINHETA')
        try:
            os.environ['PIXELRUSH_QA_R11_VINHETA']='0'
            qa.desenhar_vinheta(dest,s)
            self.assertEqual(qa.diagnostico()['rapido'],0)
            self.assertEqual(qa.diagnostico()['fallback'],1)
        finally:
            if old is None:os.environ.pop('PIXELRUSH_QA_R11_VINHETA',None)
            else:os.environ['PIXELRUSH_QA_R11_VINHETA']=old

    def test_benchmark_real_mais_rapido_sem_pixel_perdido(self):
        s=GameFeel()._vinheta
        old=pygame.Surface((450,800)).convert()
        new=old.copy()
        old.fill((22,43,77));new.fill((22,43,77))
        a=[];b=[]
        # Warmup evita medir mascara one-shot.
        qa.desenhar_vinheta(new,s)
        old.blit(s,(0,0))  # aquecimento identico antes de comparar bytes finais
        for _ in range(350):
            start=time.perf_counter_ns();old.blit(s,(0,0));a.append(time.perf_counter_ns()-start)
            start=time.perf_counter_ns();qa.desenhar_vinheta(new,s);b.append(time.perf_counter_ns()-start)
        self.assertEqual(rgba(old),rgba(new))
        ma=statistics.median(a);mb=statistics.median(b)
        print('QA776 R11 vinheta SDL dummy old_ns=',ma,
              'new_ns=',mb,'speedup=',round(ma/mb,3))
        # Falhar em regressoes claras, sem afirmar ganho de FPS em A54.
        self.assertLess(mb,ma*1.1)

if __name__=='__main__':unittest.main(verbosity=2)
