# -*- coding: utf-8 -*-
"""QA 3.277.42: prova pixel-exata das mudancas integradas e fallback nativo.

Compara a funcao de clima anterior com pool/culling em TODOS os climas,
multiple frames and 2 pixel formats. No Android device required.
"""
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


def bits(s):
    return pygame.image.tobytes(s,'RGBA')


class TestQA742(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_ambiente_clima_pool_todos_estados_pixels_exatos(self):
        from pixelrush_world_v3130 import LivingWorld
        from pixelrush_qa_performance_integrated_v327742 import _weather_cached
        anterior=LivingWorld._weather
        tipos=('limpo','chuva','tempestade','chuva_acida','neve',
               'nevasca','areia','tempestade_areia','cinzas',
               'chuva_meteoros','vento','vento_folhas','polen',
               'brisa_celeste','desconhecido')
        for flags in (0,pygame.SRCALPHA):
            for nome in tipos:
                for frame in (0,1,37,101,455,10001):
                    world=SimpleNamespace(climate=nome,frame=frame)
                    antigo=pygame.Surface((450,800),flags)
                    antigo.fill((31,65,102,140) if flags else (31,65,102))
                    novo=antigo.copy()
                    anterior(world,antigo)
                    _weather_cached(world,novo)
                    self.assertEqual(bits(antigo),bits(novo),
                                     ('clima',flags,nome,frame))

    def test_cache_veu_noturno_mesmos_pixels(self):
        from pixelrush_city2_v3118 import CityPilotScene
        city=CityPilotScene()
        for night in (.121,.20,.48,.79,1.0):
            for frame in (10,39):
                a=pygame.Surface((450,500),pygame.SRCALPHA)
                b=pygame.Surface((450,500),pygame.SRCALPHA)
                city._qa_night_veil=None
                city.render_scene(a,110.0,frame,night,'limpo',.52)
                city.render_scene(b,110.0,frame,night,'limpo',.52)
                self.assertEqual(bits(a),bits(b),(night,frame,'veil reuse'))
        self.assertIsNotNone(city._qa_night_veil)

    def test_culling_sprite_conservador_fora_tela(self):
        from pixelrush_city2_v3118 import CityPilotScene
        from pixelrush_city2_v3115 import WIDTH,SCENE_W,SCENE_H,SCALE
        import math
        img=pygame.Surface((900,500),pygame.SRCALPHA)
        img.fill((45,79,100,47))
        art=pygame.Surface((35,20),pygame.SRCALPHA)
        art.fill((194,165,87,117))
        sprites=[
            SimpleNamespace(kind='x',x=j*42-1000,y=20+j%40,
                            phase=j*.13,sway=j%8)
            for j in range(75)]
        variant=SimpleNamespace(sprites=sprites)
        city=CityPilotScene.__new__(CityPilotScene)
        city.lib=SimpleNamespace(assets={'x':SimpleNamespace(image=art,normal=art)})
        city._scaled_surface=lambda _v,_kind:img
        city._draw_sprite=lambda tgt,k,x,y,f,n,c,m,fl:tgt.blit(art,(x,y))
        def anterior(tgt,xx,frame,climate):
            tex=img
            rr=pygame.Rect(max(0,-xx),0,min(SCENE_W,WIDTH-xx)-max(0,-xx),SCENE_H)
            if rr.w>0:tgt.blit(tex,(max(0,xx),0),rr)
            for sp in variant.sprites:
                asset=city.lib.assets.get(sp.kind)
                if asset is None:continue
                texture=getattr(asset,'image')
                width=texture.get_width()
                wind=1.5 if climate in ('vento','tempestade','nevasca') else 1.
                dx=int(round(math.sin(frame*.025+sp.phase)*sp.sway*wind))
                x=xx+sp.x*SCALE+dx
                if x>=WIDTH+2 or x+width<=-2:continue
                city._draw_sprite(tgt,sp.kind,x,sp.y*SCALE,frame,.42,climate,'image',False)
        for frame in (0,17,391,1012):
            for xx in (-1800,-700,-25,450,980):
                for climate in ('limpo','nevasca'):
                    ref=pygame.Surface((450,500),pygame.SRCALPHA)
                    candidate=ref.copy()
                    anterior(ref,xx,frame,climate)
                    city._render_chunk(candidate,variant,False,xx,frame,.42,climate,.63,'image')
                    self.assertEqual(bits(ref),bits(candidate),
                                     (frame,xx,climate,'culling sprite'))

    def test_camera_nativa_integra_sem_duplo_zoom_e_fallback(self):
        from pixelrush_cinema_v3172 import CameraCinematica
        from pixelrush_qa_crop_native_v327741 import Crop32QA
        import pixelrush_qa_camera_native_auto_v327742 as qa
        lib=os.environ.get('PIXELRUSH_QA_NATIVE_CAMERA_LIB',
            '/tmp/pixelrush-qa-native/libpixelrush_camera_crop_v327741.so')
        original=CameraCinematica.aplicar
        jogadores=[
          SimpleNamespace(no_chao=(i%3==0),rect=pygame.Rect(182,500+i%7*15,34,70))
          for i in range(18)]
        s=pygame.Surface((450,800),pygame.SRCALPHA)
        for y in range(800):
            pygame.draw.line(s,((y*11)%256,(y*17)%256,(y*3)%256,(y*7)%256),
                             (0,y),(449,y))
        aa=CameraCinematica();bb=CameraCinematica()
        try:
            qa.instalar()
            qa._NATIVE=Crop32QA(lib)
            qa._REPORT['selecionado']=True
            qa._REPORT['status']='teste_forcado_no_CI'
            for i,jogador in enumerate(jogadores):
                momento=bool(i%5==0)
                velocidade=10.3+i*.13
                ref=original(aa,s,jogador,velocidade,momento,True)
                novo=bb.aplicar(s,jogador,velocidade,momento,True)
                self.assertEqual(bits(ref),bits(novo),('native',i))
                self.assertAlmostEqual(aa.zoom,bb.zoom,places=12)
                self.assertAlmostEqual(aa.foco_y,bb.foco_y,places=12)
            class Falha:
                def processar(self,*args,**kwargs):raise RuntimeError('falha QA')
            qa._NATIVE=Falha()
            qa._REPORT['selecionado']=True
            ref=original(aa,s,jogadores[1],13.4,False,True)
            novo=bb.aplicar(s,jogadores[1],13.4,False,True)
            self.assertEqual(bits(ref),bits(novo),('native fallback'))
            self.assertAlmostEqual(aa.zoom,bb.zoom,places=12)
            self.assertAlmostEqual(aa.foco_y,bb.foco_y,places=12)
            self.assertGreaterEqual(qa.diagnostico()['fallbacks'],1)
        finally:
            qa.restaurar_para_teste()
        self.assertIs(CameraCinematica.aplicar,original)

    def test_budget_rss_sem_afetar_o_bioma_ativo(self):
        import pixelrush_qa_performance_integrated_v327742 as qa
        from collections import OrderedDict
        from types import SimpleNamespace
        class FakeWorld:
            def __init__(self):
                self.biome='cidade'
                self.props_cache={('cidade',0):'ativo',('neve',1):'frio'}
                self.cache=OrderedDict([('cidade','ativo'),('neve','frio')])
                self.fx_cache=OrderedDict([('cidade','ativo'),('deserto','frio')])
                self.normal_cache={}
                self.material_cache={}
                self.flow_cache={}
                self.geometry_cache={}
                self._city_surfaces={('image',False):'quadro',
                                     ('normal',False):'frio'}
                self.city2=SimpleNamespace(_scaled=OrderedDict(
                    (str(i),i) for i in range(12)))
        fake=FakeWorld()
        old_func=qa._memory_mib
        old_limit=qa._LAST_STATUS['cache_budget_mib']
        try:
            qa._WORLDS.add(fake)
            qa._LAST_STATUS['cache_budget_mib']=560
            qa._memory_mib=lambda:700.
            qa._reclaim_inactive_caches()
            self.assertEqual(fake.props_cache,{('cidade',0):'ativo'})
            self.assertEqual(dict(fake.cache),{'cidade':'ativo'})
            self.assertEqual(dict(fake.fx_cache),{'cidade':'ativo'})
            self.assertEqual(fake._city_surfaces,{('image',False):'quadro'})
            self.assertEqual(len(fake.city2._scaled),8)
        finally:
            qa._WORLDS.discard(fake)
            qa._LAST_STATUS['cache_budget_mib']=old_limit
            qa._memory_mib=old_func

    def test_gc_e_tracing_nao_alteram_resultados(self):
        from pixelrush_qa_performance_integrated_v327742 import (
            instalar,restaurar_para_teste,diagnostico)
        from pixelrush_world_v3130 import LivingWorld
        from pixelrush_cinema_v3172 import CameraCinematica
        import gc
        w=LivingWorld._weather
        camera=CameraCinematica.aplicar
        prev_callbacks=tuple(gc.callbacks)
        try:
            instalar()
            instalar()
            self.assertIsNot(LivingWorld._weather,w)
            self.assertIsNot(CameraCinematica.aplicar,camera)
            r=diagnostico()
            self.assertFalse(r['gpu_accelerated'])
            self.assertGreaterEqual(r['cache_budget_mib'],384)
            self.assertLessEqual(r['cache_budget_mib'],560)
        finally:
            restaurar_para_teste()
        self.assertIs(LivingWorld._weather,w)
        self.assertIs(CameraCinematica.aplicar,camera)
        self.assertEqual(tuple(gc.callbacks),prev_callbacks)


if __name__=='__main__':
    unittest.main(verbosity=2)
