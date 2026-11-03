# -*- coding: utf-8 -*-
"""Gates offline QA749 para o compositor realmente usado na Cidade v3125.

Somente roda quando o usuario disparar o workflow de homologacao offline.
Nao cria APK/Android e nao invoca entrada principal do jogo.
"""
import os,sys,random,unittest
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame

class CidadeRealQA749(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_planos_de_tiles_iguais_entre_canais_e_multinstancias(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_qa_city_tiles_v327749 as qa
        qa.restaurar_para_teste()
        referencia=CityPilotScene._layer_tiles
        cidades=[CityPilotScene(), CityPilotScene()]
        try:
            os.environ['PIXELRUSH_QA_CIDADE_TILE_PLAN']='1'
            qa.instalar()
            for scene in cidades:
                for travel in (0,10.2,900.,1165.1,1165.1,20480.):
                    for layer in scene.layers:
                        original=tuple(referencia(travel,layer))
                        otimizado=tuple(scene._layer_tiles(travel,layer))
                        self.assertEqual(
                            [(x,id(variant),flip) for x,variant,flip in original],
                            [(x,id(variant),flip) for x,variant,flip in otimizado])
                        cache=scene._layer_tiles(travel,layer)
                        self.assertEqual(
                            [(x,id(v),flip) for x,v,flip in cache],
                            [(x,id(v),flip) for x,v,flip in original])
            self.assertGreater(qa.estatisticas()['hits'],0)
            self.assertLessEqual(qa.estatisticas()['max_tiles_retidos'],20)
        finally:
            qa.restaurar_para_teste()
        self.assertIs(CityPilotScene._layer_tiles,referencia)

    def test_composicao_cidade_rgba_referencia_multimap(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_qa_city_tiles_v327749 as qa
        qa.restaurar_para_teste()
        scene=CityPilotScene()
        rng=random.getstate()
        for fmt in (0,pygame.SRCALPHA):
            for kind in ('image','normal','geometry','material','fxmask','flow'):
                for night,climate,frame,travel in ((0,'limpo',21,0),
                                                   (.34,'chuva',57,72.1),
                                                   (.9,'tempestade',183,509.3)):
                    old=pygame.Surface((450,500),fmt)
                    old.fill((27,61,88,170) if fmt else (27,61,88))
                    new=old.copy()
                    scene.render_scene(old,travel,frame,night,climate,.54,
                                       map_kind=kind)
                    qa.instalar()
                    try:
                        scene.render_scene(new,travel,frame,night,climate,.54,
                                           map_kind=kind)
                    finally:
                        qa.restaurar_para_teste()
                    self.assertEqual(pygame.image.tobytes(old,'RGBA'),
                                     pygame.image.tobytes(new,'RGBA'),
                                     (fmt,kind,night,frame))
        self.assertEqual(random.getstate(),rng)

    def test_clima_real_rgba_qualidade_clima_dia_noite(self):
        from pixelrush_citylife_v3123 import CityLifeDirector
        import pixelrush_qa_city_weather_v327749 as qa
        qa.restaurar_para_teste()
        scene=CityLifeDirector()
        ref_atm=CityLifeDirector.draw_atmosphere
        ref_ref=CityLifeDirector.draw_wet_reflections
        rng=random.getstate()
        try:
            qa.instalar()
            for flags in (0,pygame.SRCALPHA):
                for qualidade in (0,1):
                    for kind in ('limpo','chuva','tempestade','nevasca',
                                 'vento','areia','cinzas'):
                        for night,frame,travel in ((0,0,0),(.35,71,320.4),
                                                   (.82,211,1989.9)):
                            a=pygame.Surface((450,500),flags)
                            b=a.copy()
                            a.fill((32,54,93,210) if flags else (32,54,93))
                            b.blit(a,(0,0))
                            scene.wind=1.05
                            ref_atm(scene,a,travel,frame,night,kind,qualidade)
                            ref_ref(scene,a,travel,frame,night,kind)
                            scene.draw_atmosphere(b,travel,frame,night,kind,qualidade)
                            scene.draw_wet_reflections(b,travel,frame,night,kind)
                            self.assertEqual(pygame.image.tobytes(a,'RGBA'),
                                             pygame.image.tobytes(b,'RGBA'),
                                             (flags,qualidade,kind,night))
            self.assertGreater(qa.estatisticas()['atmosfera_quadros'],0)
        finally:
            qa.restaurar_para_teste()
        self.assertEqual(random.getstate(),rng)
        self.assertIs(CityLifeDirector.draw_atmosphere,ref_atm)
        self.assertIs(CityLifeDirector.draw_wet_reflections,ref_ref)

    def test_fallback_flags_nao_instalam_qa(self):
        import pixelrush_qa_city_tiles_v327749 as tiles
        import pixelrush_qa_city_weather_v327749 as clima
        olda=os.environ.get('PIXELRUSH_QA_CIDADE_TILE_PLAN')
        oldb=os.environ.get('PIXELRUSH_QA_CITY_WEATHER_FAST')
        tiles.restaurar_para_teste()
        clima.restaurar_para_teste()
        try:
            os.environ['PIXELRUSH_QA_CIDADE_TILE_PLAN']='0'
            os.environ['PIXELRUSH_QA_CITY_WEATHER_FAST']='0'
            tiles.instalar();clima.instalar()
            self.assertFalse(tiles.estatisticas()['instalado'])
            self.assertFalse(clima.estatisticas()['instalado'])
        finally:
            if olda is None:os.environ.pop('PIXELRUSH_QA_CIDADE_TILE_PLAN',None)
            else:os.environ['PIXELRUSH_QA_CIDADE_TILE_PLAN']=olda
            if oldb is None:os.environ.pop('PIXELRUSH_QA_CITY_WEATHER_FAST',None)
            else:os.environ['PIXELRUSH_QA_CITY_WEATHER_FAST']=oldb

if __name__=='__main__':
    unittest.main(verbosity=2)
