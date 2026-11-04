# -*- coding: utf-8 -*-
"""PIXEL RUSH QA 3.277.50 — gates para executar SOMENTE na homologacao.

Valida frame de apresentacao do jogo (camera, scale, HUD), scroll real,
geometria RGBA persistente e limpeza RSS multi-instancia sem Android/APK.
Nao altera saves ou roda a corrida completa.
"""
import os
import sys
import random
import unittest
from collections import OrderedDict
from pathlib import Path
from types import SimpleNamespace
from weakref import WeakSet

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame


def rgba(surface):
    return pygame.image.tobytes(surface,'RGBA')


class Integracao750(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_pipeline_camera_zoom_escala_apresentacao_rgba(self):
        from pixelrush_cinema_v3172 import CameraCinematica
        from pixelrush_qa_unified_post_v327750 import finalizar_quadro
        from collections import OrderedDict
        for usa_camera in (False,True):
            for tamanho in ((450,800),(390,693)):
                for frame in (0,1,23,98,201):
                    base=pygame.Surface((450,800)).convert()
                    base.fill((21+frame%39,37,97))
                    pygame.draw.rect(base,(202,142,53),(18+frame%60,32,91,64))
                    pygame.draw.circle(base,(82,190,211),(160,520),23+frame%9)
                    jogador=SimpleNamespace(rect=pygame.Rect(160,410+frame%140,32,64),
                                            no_chao=frame%3==0)
                    expected_camera=CameraCinematica()
                    actual_camera=CameraCinematica()
                    expected_camera.zoom=actual_camera.zoom=.015
                    expected_camera.foco_y=actual_camera.foco_y=3.
                    tela=pygame.display.get_surface()
                    dest_size=tela.get_size()
                    position=((dest_size[0]-tamanho[0])//2,
                              (dest_size[1]-tamanho[1])//2)
                    tela.fill((14,19,33))
                    img=base.copy()
                    if usa_camera:
                        img=expected_camera.aplicar(img,jogador,10.,True,True)
                    cache=OrderedDict()
                    if tamanho!=img.get_size():
                        cache[tamanho]=pygame.Surface(tamanho).convert()
                        pygame.transform.scale(img,tamanho,cache[tamanho])
                        img=cache[tamanho]
                    tela.blit(img,position)
                    pygame.display.flip()
                    expected=rgba(tela)
                    tela.fill((14,19,33))
                    trace=[]
                    outcache=OrderedDict()
                    finalizar_quadro(base.copy(),tela,tamanho,position,outcache,
                                    actual_camera,jogador,10.,True,usa_camera,
                                    lambda x:trace.append(('start',x)),
                                    lambda:trace.append(('end',)),
                                    lambda x:trace.append(('mark',x)))
                    self.assertEqual(rgba(tela),expected,
                                     (usa_camera,tamanho,frame))
                    self.assertAlmostEqual(expected_camera.zoom,actual_camera.zoom)
                    self.assertAlmostEqual(expected_camera.foco_y,actual_camera.foco_y)
                    self.assertEqual(trace[-2][0],'start')
                    self.assertEqual(trace[-1][0],'end')

    def test_scroll_cidade_chunks_estaticos_rgba_apos_reconstrucao(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_qa_incremental_scene_v327750 as qa
        qa.restaurar_para_teste()
        scene=CityPilotScene()
        layer=next(x for x in scene.layers if any(not v.sprites for v in x.variants))
        variant=next(v for v in layer.variants if not v.sprites)
        original=CityPilotScene._render_chunk
        prior=os.environ.get('PIXELRUSH_QA_CITY_INCREMENTAL')
        rng=random.getstate()
        try:
            os.environ['PIXELRUSH_QA_CITY_INCREMENTAL']='1'
            qa.instalar()
            for flags in (0,pygame.SRCALPHA):
                for x in (-730,-360,-356,-350,-344,-300,-710,-700,-703,
                          -30,-25,-17,-12,1,3,10):
                    a=pygame.Surface((450,500),flags)
                    a.fill((16,43,82,120) if flags else (16,43,82))
                    b=a.copy()
                    original(scene,a,variant,False,x,23,.51,'limpo',.6,'image')
                    scene._render_chunk(b,variant,False,x,23,.51,'limpo',.6,'image')
                    self.assertEqual(rgba(a),rgba(b),(flags,x))
            diag = qa.diagnostico()
            # QA755+: atlas SDL-RLE real exige fallback para preservar
            # RGB oculto no destino alpha0; nao fabricar hits de cache.
            self.assertGreater(
                diag['cidade_hit'] + diag['cidade_rle_direto'],0)
            self.assertLessEqual(len(qa._CIDADE.get(scene, {})), 2)
        finally:
            qa.restaurar_para_teste()
            if prior is None:os.environ.pop('PIXELRUSH_QA_CITY_INCREMENTAL',None)
            else:os.environ['PIXELRUSH_QA_CITY_INCREMENTAL']=prior
        self.assertEqual(random.getstate(),rng)
        self.assertIs(CityPilotScene._render_chunk,original)

    def test_scroll_clasico_janelas_opacas_rgb_rgba(self):
        from pixelrush_world_v3130 import LivingWorld
        import pixelrush_qa_incremental_scene_v327750 as qa
        qa.restaurar_para_teste()
        world=LivingWorld('cidade')
        original=LivingWorld._blit_strip
        old=os.environ.get('PIXELRUSH_QA_CLASSIC_INCREMENTAL')
        texture=pygame.Surface((730,500)).convert()
        for y in range(500):
            pygame.draw.line(texture,((y*11)%256,(y*7)%256,(y*17)%256),
                             (0,y),(729,y))
        try:
            os.environ['PIXELRUSH_QA_CLASSIC_INCREMENTAL']='1'
            qa.instalar()
            for flags in (0,pygame.SRCALPHA):
                for travel in (0.,7.,19.,31.,42.,110.,550.,1190.):
                    world.travel=travel
                    a=pygame.Surface((450,800),flags)
                    a.fill((17,42,93,200) if flags else (17,42,93))
                    b=a.copy()
                    original(world,a,texture)
                    world._blit_strip(b,texture)
                    self.assertEqual(rgba(a),rgba(b),(flags,travel))
            self.assertGreater(qa.diagnostico()['classico_frames'],0)
        finally:
            qa.restaurar_para_teste()
            if old is None:os.environ.pop('PIXELRUSH_QA_CLASSIC_INCREMENTAL',None)
            else:os.environ['PIXELRUSH_QA_CLASSIC_INCREMENTAL']=old

    def test_geometria_reutilizada_sem_blending_de_rgba(self):
        from pixelrush_city2_v3125 import CityPilotScene
        from pixelrush_biomes2_v3130 import ModularBiomeScene
        for scene in (CityPilotScene(),ModularBiomeScene('neve'),
                      ModularBiomeScene('deserto')):
            previous=None
            for frame in (11,34,78):
                target=pygame.Surface((450,500),pygame.SRCALPHA)
                target.fill((22,54,77,91))
                scene.render_scene(target,frame*2.7,frame,.23,'limpo',.5,
                                   map_kind='geometry')
                snap=scene._geometry_view
                self.assertEqual(rgba(snap),rgba(target))
                if previous is not None:
                    self.assertIs(snap,previous)
                previous=snap

    def test_limpeza_rss_vinhetas_frias_mantem_nivel_atual(self):
        from pixelrush_qa_cache_trim_v327748 import EscalonadorTrimQA
        class World:
            def __init__(self):
                self.biome='cidade'
                self.night=.55
                self.city2=SimpleNamespace(_scaled=OrderedDict(),
                    _night_veils=OrderedDict((i,pygame.Surface((450,500),pygame.SRCALPHA))
                                             for i in range(13)))
        w=World()
        key=max(0,min(12,int(w.night*12+.5)))
        before=len(w.city2._night_veils)
        cleaner=EscalonadorTrimQA(limite_por_passo=2)
        self.assertTrue(cleaner.iniciar(WeakSet([w]),{},900.,560.))
        for _ in range(150):
            if not cleaner.ativo:break
            cleaner.passo()
        self.assertFalse(cleaner.ativo)
        self.assertEqual(before,13)
        self.assertLessEqual(len(w.city2._night_veils),4)
        self.assertIn(key,w.city2._night_veils)
        self.assertGreater(cleaner.removidos,0)

if __name__=='__main__':
    unittest.main(verbosity=2)
