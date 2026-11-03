# -*- coding: utf-8 -*-
"""QA 3.277.43: quadros completos de Cidade/Neve, camera e HUD, byte-exatos."""
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame


def rgba(s):
    return pygame.image.tobytes(s,'RGBA')


def montar_frame(scene,frame,travel,night,climate,optimized=False):
    from pixelrush_world_v3130 import LivingWorld
    from pixelrush_qa_performance_integrated_v327742 import _weather_cached
    output=pygame.Surface((450,800),pygame.SRCALPHA)
    output.fill((22,39,59,255))
    scene._qa_cloud_use_cache=bool(optimized) if hasattr(scene,'_qa_cloud_use_cache') else False
    view=output.subsurface((0,230,450,500))
    scene.render_scene(view,travel,frame,night,climate,.53)
    weather=SimpleNamespace(frame=frame,climate=climate)
    (_weather_cached if optimized else LivingWorld._weather)(weather,output)
    # Sobreposicoes HUD/cenario, com os mesmos comandos nos dois caminhos.
    pygame.draw.rect(output,(34,66,96,255),(0,0,450,43))
    pygame.draw.rect(output,(239,203,117,255),(10,12,92,13),border_radius=3)
    pygame.draw.circle(output,(228,186,88,255),(406,25),9)
    pygame.draw.line(output,(135,212,235,255),(0,739),(450,739),2)
    return output


class FrameCompletoQA743(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_sequencia_cidade_neve_clima_camera_hud(self):
        from pixelrush_city2_v3118 import CityPilotScene
        from pixelrush_biomes2_v3126 import ModularBiomeScene
        from pixelrush_cinema_v3172 import CameraCinematica
        import pixelrush_qa_camera_v327733 as simd
        import pixelrush_qa_camera_native_auto_v327742 as native
        native.restaurar_para_teste()
        simd.restaurar_para_teste()
        baseline=CameraCinematica.aplicar
        simd.instalar()
        native.instalar()
        try:
            for biome,scene in (('cidade',CityPilotScene()),
                                ('neve',ModularBiomeScene('neve'))):
                ref=CameraCinematica()
                qa=CameraCinematica()
                ref.zoom=qa.zoom=.006
                for index in range(16):
                    frame=13+index*19
                    travel=frame*11.7
                    night=(0.,.2,.54,.85)[index%4]
                    climate=('limpo','chuva','nevasca','vento')[index%4]
                    a=montar_frame(scene,frame,travel,night,climate,False)
                    b=montar_frame(scene,frame,travel,night,climate,True)
                    self.assertEqual(rgba(a),rgba(b),(biome,index,'frame completo'))
                    player=SimpleNamespace(rect=pygame.Rect(170,400+(index*13)%210,32,68),
                                           no_chao=index%3==0)
                    args=(player,10.+index*.3,index%6==0,True)
                    cpu=baseline(ref,a,*args)
                    output=qa.aplicar(b,*args)
                    self.assertEqual(rgba(cpu),rgba(output),(biome,index,'camera'))
                    self.assertEqual((ref.zoom,ref.foco_y),(qa.zoom,qa.foco_y))
        finally:
            native.restaurar_para_teste()
            simd.restaurar_para_teste()
        self.assertIs(CameraCinematica.aplicar,baseline)


if __name__=='__main__':
    unittest.main(verbosity=2)
