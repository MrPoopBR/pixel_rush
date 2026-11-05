# -*- coding: utf-8 -*-
"""QA776: instrumentar cenas reais sem alterar bytes, hooks nem estado."""
import os,random,unittest
from pathlib import Path
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
import pixelrush_qa_r11_passes_v327776 as trace

ROOT=Path(__file__).resolve().parents[1]
def rgba(s):return pygame.image.tobytes(s,'RGBA')

class PassesR11QA776(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        trace.restaurar_para_teste();pygame.quit()

    def test_codigo_pessoal_preservado_e_instrumentacao_explicita(self):
        codigo=(ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        assert 'VERSAO = "v3.277.85-QA-ANDROID-RC"' in codigo
        assert codigo.count('_r11_sub_inicio("r11_post_')>=7
        for nome in ('alertas','pets','efeitos_portais','particulas',
                     'frente_gamefeel','gamefeel','clima_transicoes'):
            self.assertIn('r11_post_'+nome,codigo)
        telemetria=(ROOT/'pixelrush_qa_android_v327728.py').read_text('utf8')
        for nome in ('r11_city_atmosfera','r11_city_chunk','r11_world_cena',
                     'r11_post_gamefeel','r11_post_vinheta'):
            self.assertIn(nome,telemetria)
        self.assertIn("if os.environ.get('PIXELRUSH_QA_ANDROID') == '1'",codigo)

    def test_desativado_foraproducao_e_rollback(self):
        trace.restaurar_para_teste()
        from pixelrush_city2_v3125 import CityPilotScene
        before=CityPilotScene._render_chunk
        with patch.dict(os.environ,{'PIXELRUSH_QA_ANDROID':'0'}):
            self.assertFalse(trace.instalar())
        self.assertIs(CityPilotScene._render_chunk,before)
        self.assertFalse(trace.instalado())

    def test_cidade_mundo_real_rgba_igual_e_hooks_reversiveis(self):
        from pixelrush_qa_city_bootstrap_v327759 import instalar as bootstrap
        from pixelrush_qa_city_bootstrap_v327759 import restaurar_para_teste as fim_boot
        from pixelrush_world_v3130 import LivingWorld
        from pixelrush_city2_v3125 import CityPilotScene
        trace.restaurar_para_teste()
        bootstrap()
        world=LivingWorld('cidade')
        orig=CityPilotScene.render_scene
        rng=random.getstate()
        try:
            with patch.dict(os.environ,{'PIXELRUSH_QA_ANDROID':'1',
                                        'PIXELRUSH_QA_R11_PASS_TRACE':'1'}):
                frames=[]
                for flags in (0,pygame.SRCALPHA):
                    a=pygame.Surface((450,800),flags,32)
                    a.fill((17,56,79,0) if flags else (17,56,79))
                    b=a.copy()
                    world.draw(a)
                    frames.append((a,b))
                self.assertTrue(trace.instalar())
                self.assertTrue(trace.instalado())
                for a,b in frames:
                    world.draw(b)
                    self.assertEqual(rgba(a),rgba(b))
                self.assertIsNot(CityPilotScene.render_scene,orig)
        finally:
            trace.restaurar_para_teste()
            fim_boot()
        self.assertIs(CityPilotScene.render_scene,orig)
        self.assertEqual(random.getstate(),rng)

if __name__=='__main__':unittest.main(verbosity=2)
