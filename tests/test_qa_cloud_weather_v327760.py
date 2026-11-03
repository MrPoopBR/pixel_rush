# -*- coding: utf-8 -*-
"""QA760: nuvens SDL cacheadas RGB/rgba e clima classico byte exato."""
import os, sys, statistics, time, unittest
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import pygame
import pixelrush_cenarios_v398 as visual
import pixelrush_qa_scene_v327733 as qa_cloud
import pixelrush_qa_performance_integrated_v327742 as qa_weather
from pixelrush_world_v3130 import LivingWorld

def rgba(s):
    return pygame.image.tobytes(s,'RGBA')

class CloudWeather760(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        qa_cloud.restaurar_para_teste()
        pygame.quit()

    def test_nuvens_rgb_ou_rgba_iguais_ao_original(self):
        original=qa_cloud._ORIGINAIS.get('nuvem_pixel',visual.nuvem_pixel)
        qa_cloud.instalar()
        colores=(
            ((205,223,241),(120,158,190),(240,251,255)),
            ((205,223,241,255),(120,158,190,255),(240,251,255,255)),
            ((205,223,241,130),(120,158,190,180),(240,251,255,170))
        )
        for alpha in (False,True):
            for fundo in ((15,55,99,0),(15,55,99,255)):
                for cores in colores:
                    for s in (1,2):
                        for x,y in ((2,2),(-15,9),(42.8,14.7),(60,29)):
                            flags=pygame.SRCALPHA if alpha else 0
                            a=pygame.Surface((128,96),flags)
                            b=pygame.Surface((128,96),flags)
                            a.fill(fundo);b.fill(fundo)
                            original(a,x,y,s,*cores)
                            visual.nuvem_pixel(b,x,y,s,*cores)
                            self.assertEqual(rgba(a),rgba(b),(alpha,fundo,cores,s,x,y))
        diag=qa_cloud.diagnostico_nuvens()
        self.assertGreater(diag['blits_rgb'],0)
        self.assertGreater(diag['fallback_rgba'],0)
        self.assertGreater(diag['fallback_alpha'],0)

    def test_weather_classica_igual_por_bioma_clima_rgb_oculto(self):
        original=LivingWorld._weather
        climates=('limpo','chuva','tempestade','chuva_acida',
                  'neve','nevasca','areia','tempestade_areia','cinzas',
                  'chuva_meteoros','vento','vento_folhas','polen','brisa_celeste')
        for alpha in (False,True):
            for frame in (0,1,37,204,732):
                for climate in climates:
                    fake=SimpleNamespace(frame=frame,climate=climate)
                    a=pygame.Surface((450,800),pygame.SRCALPHA if alpha else 0)
                    b=pygame.Surface((450,800),pygame.SRCALPHA if alpha else 0)
                    a.fill((19,76,142,0));b.fill((19,76,142,0))
                    original(fake,a)
                    qa_weather._weather_cached(fake,b)
                    self.assertEqual(rgba(a),rgba(b),(alpha,frame,climate))

    def test_micromedida_rgb_nuvem_sem_afirmacao_android(self):
        original=qa_cloud._ORIGINAIS.get('nuvem_pixel')
        if original is None:
            original=visual.nuvem_pixel
            qa_cloud.instalar()
        fast=visual.nuvem_pixel
        colors=((205,223,241),(120,158,190),(240,251,255))
        dst=pygame.Surface((450,800))
        def measure(fn):
            samples=[]
            for group in range(7):
                start=time.perf_counter_ns()
                for i in range(250):
                    fn(dst,20+i%4,40+i%7,1,*colors)
                samples.append((time.perf_counter_ns()-start)/250/1000)
            return round(statistics.median(samples),3)
        result={'draw_rect_us':measure(original),'cache_rgb_us':measure(fast)}
        print('BENCH_CLOUD_LINUX_US',result)
        self.assertGreater(result['draw_rect_us'],0)
        self.assertGreater(result['cache_rgb_us'],0)

if __name__=='__main__':
    unittest.main(verbosity=2)
