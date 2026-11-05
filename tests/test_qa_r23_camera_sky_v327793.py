# -*- coding: utf-8 -*-
"""QA R23: camera cinemática de custo constante e ciclo azul/laranja 180s."""
import os,sys,unittest
from pathlib import Path
from types import SimpleNamespace
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame
pygame.init()
pygame.display.set_mode((450,800))
from pixelrush_gamefeel_v3152 import GameFeel
from src.pixelrush.world.daynight_v327793 import calcular_ciclo_ceu
from src.pixelrush.rendering.sky_v3233 import _preparar,estatisticas_cache

class CameraCeu(unittest.TestCase):
    def test_camera_suave_limites_sem_alterar_hitbox(self):
        cam=GameFeel()
        j=SimpleNamespace(rect=pygame.Rect(84,590,44,69),
            chao_y=730,no_chao=False,morrendo=False,descida_rapida=False,
            jetpack_fase=None)
        origem=j.rect.copy()
        for _ in range(30):
            cam.seguir_jogador(j,True)
        ox,oy=cam.deslocamento()
        self.assertGreaterEqual(ox,1)
        self.assertLessEqual(ox,3)
        self.assertGreaterEqual(oy,-5)
        self.assertLess(oy,0)
        self.assertEqual(j.rect,origem)
        j.descida_rapida=True
        for _ in range(30):
            cam.seguir_jogador(j,False)
        self.assertGreaterEqual(cam.deslocamento()[1],2)
        self.assertLessEqual(cam.deslocamento()[1],5)
        j.no_chao=True
        j.rect.bottom=j.chao_y
        for _ in range(50):
            cam.seguir_jogador(j,False)
        self.assertEqual(cam.deslocamento(),(0,0))
        j.no_chao=False
        for _ in range(20):cam.seguir_jogador(j,True,reduzir_efeitos=True)
        self.assertEqual(cam.deslocamento(),(0,0))
        cam.seguir_jogador(j,True)
        self.assertGreater(cam._qa_camera_x,0.0)
        cam.reiniciar()
        self.assertEqual(cam.deslocamento(),(0,0))

    def test_camera_sem_surface_por_quadro_e_zoom_legado(self):
        cam=GameFeel()
        j=SimpleNamespace(rect=pygame.Rect(84,600,44,69),
            chao_y=730,no_chao=False,morrendo=False,descida_rapida=False,
            jetpack_fase=None)
        frame_original=id(cam._buffer_zoom)
        vignette=id(cam._vinheta)
        for tick in range(500):
            j.rect.bottom=600+tick%120
            cam.seguir_jogador(j,tick%2==0)
            cam.deslocamento()
        self.assertEqual(id(cam._buffer_zoom),frame_original)
        self.assertEqual(id(cam._vinheta),vignette)

    def test_ceu_64_fases_32_niveis_noite_cache_limitado(self):
        from src.pixelrush.rendering.sky_v3233 import _CACHE
        _CACHE.clear()
        cores=[]
        for t in range(0,10801,45):
            fase,cor,noite,_=calcular_ciclo_ceu(0,t)
            img=_preparar(cor,fase,noite,"cidade")
            cores.append(img.get_at((210,175))[:3])
            self.assertLessEqual(estatisticas_cache()["entradas"],4)
        self.assertEqual(cores[0],cores[-1])
        # Nenhuma mudança agressiva entre amostras de 0,75 segundo.
        maior=max(max(abs(a[k]-b[k]) for k in range(3))
                  for a,b in zip(cores,cores[1:]))
        self.assertLessEqual(maior,22)

    def test_tinta_do_amanhecer_e_entardecer_agora_sincronizada(self):
        fonte=(138,165,207)
        img_inicio=_preparar(fonte,0.,0.,"cidade")
        img_dia=_preparar(fonte,.25,0.,"cidade")
        img_poente=_preparar(fonte,.47,0.,"cidade")
        img_noite=_preparar(fonte,.77,0.9,"cidade")
        self.assertNotEqual(img_inicio.get_at((210,175)),img_dia.get_at((210,175)))
        self.assertNotEqual(img_poente.get_at((210,175)),img_dia.get_at((210,175)))
        self.assertNotEqual(img_noite.get_at((210,175)),img_dia.get_at((210,175)))

if __name__=="__main__":
    unittest.main(verbosity=2)
