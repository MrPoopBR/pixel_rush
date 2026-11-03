# -*- coding: utf-8 -*-
"""QA753 — gates pygame-ce REAIS para executar somente na homologacao manual.

Comparacao RGBA em Cena v3125, strip SDL e cache incremental, sem imagem
simplificada ou mudanca na jogabilidade. Sonda 180/181 por mock de memoria;
nenhum APK, Android ou teste final executado ao criar este arquivo.
"""
import os
import random
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from weakref import ref

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame


def rgba(surface):
    return pygame.image.tobytes(surface,'RGBA')


class RenderScroll753(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_cidade_foreground_real_transparente_sem_efeitos_colaterais(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_qa_hotpath_v327753 as qa
        qa.restaurar_para_teste()
        old_render=CityPilotScene.render_scene
        old_init=CityPilotScene.__init__
        with patch.dict(os.environ,{'PIXELRUSH_QA_CITY_EMPTY_FG':'1',
                                    'PIXELRUSH_QA_STRIP_ONE_BLIT':'0'}):
            try:
                qa.instalar()
                scene=CityPilotScene()
                rng=random.getstate()  # isolar desenho do bootstrap da cena
                self.assertEqual(qa.diagnostico()['fg_cenas_verificadas'],1)
                for flags in (0,pygame.SRCALPHA):
                    for frame in (0,1,29,100):
                        for night in (.0,.43,1.):
                            a=pygame.Surface((450,500),flags)
                            a.fill((40,63,96,171) if flags else (40,63,96))
                            b=a.copy()
                            old_render(scene,a,frame*2.2,frame,night,'chuva',
                                       .5,True,'image')
                            expected_state=scene._last_state
                            scene.render_scene(b,frame*2.2,frame,night,'chuva',
                                               .5,True,'image')
                            self.assertEqual(rgba(a),rgba(b),
                                             (flags,frame,night))
                            self.assertEqual(scene._last_state,expected_state)
                self.assertGreater(qa.diagnostico()['fg_pulado'],0)
                self.assertEqual(random.getstate(),rng)
            finally:
                qa.restaurar_para_teste()
        self.assertIs(CityPilotScene.render_scene,old_render)
        self.assertIs(CityPilotScene.__init__,old_init)

    def test_strip_um_blit_exato_e_multiblit_fallback(self):
        from pixelrush_world_v3130 import LivingWorld
        import pixelrush_qa_hotpath_v327753 as qa
        qa.restaurar_para_teste()
        old=LivingWorld._blit_strip
        rng=random.Random(753)
        for flags in (0,pygame.SRCALPHA):
            for alpha in (None,81,255):
                for off in (0,10,450,451,700,899):
                    src=pygame.Surface((900,500),flags)
                    src.fill((32,75,109,170) if flags else (32,75,109))
                    for k in range(15):
                        pygame.draw.rect(src, (rng.randrange(256),44,90,135)
                                         if flags else (rng.randrange(256),44,90),
                                         (rng.randrange(900),rng.randrange(500),9,12))
                    src.set_alpha(alpha)
                    a=pygame.Surface((450,800),flags)
                    a.fill((12,47,65,89) if flags else (12,47,65))
                    b=a.copy()
                    fake=SimpleNamespace(_scroll=lambda x=off:x)
                    old(fake,a,src)
                    with patch.dict(os.environ,{'PIXELRUSH_QA_CITY_EMPTY_FG':'0',
                                                'PIXELRUSH_QA_STRIP_ONE_BLIT':'1'}):
                        qa.instalar()
                        try:
                            LivingWorld._blit_strip(fake,b,src)
                        finally:
                            qa.restaurar_para_teste()
                    self.assertEqual(rgba(a),rgba(b),(flags,alpha,off))
        self.assertIs(LivingWorld._blit_strip,old)

    def test_scroll_far_mid_rgba_near_sprites_no_original(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_qa_incremental_scene_v327750 as qa
        qa.restaurar_para_teste()
        old=CityPilotScene._render_chunk
        with patch.dict(os.environ,{'PIXELRUSH_QA_CITY_INCREMENTAL':'1',
                                    'PIXELRUSH_QA_CLASSIC_INCREMENTAL':'0',
                                    'PIXELRUSH_QA_CITY_SCROLL_SCOPE':'static'}):
            try:
                qa.instalar()
                scene=CityPilotScene()
                far=scene.layers[0].variants[0]
                mid=scene.layers[1].variants[0]
                near=next(v for l in scene.layers for v in l.variants if v.sprites)
                for flags in (0,pygame.SRCALPHA):
                    for i,x in enumerate((-530,-528,-522,-517,-510,-505,-500,
                                          -493,-490,-483,-477,-470)):
                        for variant in (far,mid,near):
                            a=pygame.Surface((450,500),flags)
                            a.fill((25,41,79,83) if flags else (25,41,79))
                            b=a.copy()
                            old(scene,a,variant,False,x,40+i,.45,'vento',
                                .52,map_kind='image')
                            scene._render_chunk(b,variant,False,x,40+i,.45,
                                                'vento',.52,map_kind='image')
                            self.assertEqual(rgba(a),rgba(b),
                                             (flags,variant is near,i,x))
                # QA755: textura real SDL-RLE exige blit direto para
                # preservar RGB oculto quando destino tem alpha zero.
                self.assertGreater(qa.diagnostico()['cidade_rle_direto'],0)
                self.assertGreater(qa.diagnostico()['cidade_sprite_direto'],0)
                self.assertLessEqual(len(qa._CIDADE.get(scene,{})),2)
                self.assertEqual(qa.diagnostico()['modo_cidade'],'static')
            finally:
                qa.restaurar_para_teste()
        self.assertIs(CityPilotScene._render_chunk,old)

    def test_trim_descarta_scroll_somente_cidade_inativa(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_qa_incremental_scene_v327750 as qa
        from pixelrush_qa_cache_trim_v327748 import EscalonadorTrimQA
        qa.restaurar_para_teste()
        with patch.dict(os.environ,{'PIXELRUSH_QA_CITY_INCREMENTAL':'1',
                                    'PIXELRUSH_QA_CITY_SCROLL_SCOPE':'static'}):
            try:
                qa.instalar()
                scene=CityPilotScene()
                surface=pygame.Surface((450,500),pygame.SRCALPHA)
                variant=scene.layers[0].variants[0]
                scene._render_chunk(surface,variant,False,-400,14,.5,'limpo',.5)
                self.assertTrue(qa.tem_cache_cena(scene))
                class World:
                    pass
                world=World()
                world.city2=scene
                world.biome='cidade'
                worker=EscalonadorTrimQA(limite_por_passo=1)
                self.assertFalse(worker._aplicar(ref(world),
                                  '_qa_city_incremental_cache',None))
                self.assertTrue(qa.tem_cache_cena(scene))
                world.biome='neve'
                self.assertTrue(worker._aplicar(ref(world),
                                 '_qa_city_incremental_cache',None))
                self.assertFalse(qa.tem_cache_cena(scene))
                self.assertGreater(qa.diagnostico()['cidade_cache_descartado'],0)
            finally:
                qa.restaurar_para_teste()

    def test_sonda_rss_181_nunca_180_com_escalonador(self):
        import pixelrush_qa_performance_integrated_v327742 as perf
        perf.restaurar_para_teste()
        old_mem=perf._memory_mib
        old_frames=perf._LAST_STATUS['frames']
        with patch.dict(os.environ,{'PIXELRUSH_QA_TRIM_PROBE_PHASE':'1',
                                    'PIXELRUSH_QA_STAGGER_TRIM':'1'}):
            try:
                perf.instalar()
                self.assertEqual(perf.diagnostico()['cache_trim_sonda_fase_180'],1)
                chamados=[]
                perf._memory_mib=lambda: (chamados.append(perf._LAST_STATUS['frames']) or 400.)
                perf._LAST_STATUS['frames']=179
                pygame.display.flip()
                self.assertEqual(chamados,[])
                pygame.display.flip()
                self.assertEqual(chamados,[181])
            finally:
                perf._memory_mib=old_mem
                perf.restaurar_para_teste()
                perf._LAST_STATUS['frames']=old_frames


if __name__=='__main__':
    unittest.main(verbosity=2)
