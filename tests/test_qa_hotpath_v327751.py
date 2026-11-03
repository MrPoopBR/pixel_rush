# -*- coding: utf-8 -*-
"""QA751: gates MANUAIS dos caminhos quentes e bordas RGBA.

Nenhum APK ou emulador. A suite fica pronta para a homologacao solicitada
futuramente e NAO e executada durante a implementacao v751.
"""
import os,random,sys,unittest,weakref
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame


def rgba(surface):
    return pygame.image.tobytes(surface,'RGBA')


class HotPath751(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_vinheta_real_13_niveis_alpha_rgb_rgba(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_city2_v3124 as city
        scene=CityPilotScene()
        previous=city._QA_DIRECT_NIGHT_MULT
        rng=random.getstate()
        try:
            for flags in (0,pygame.SRCALPHA):
                for level in range(13):
                    for kind in ('image',):
                        a=pygame.Surface((450,500),flags)
                        a.fill((19,43,92,180) if flags else (19,43,92))
                        b=a.copy()
                        n=max(.121,level/12.)
                        city._QA_DIRECT_NIGHT_MULT=False
                        scene.render_scene(a,421.3,33,n,'chuva',.62,map_kind=kind)
                        city._QA_DIRECT_NIGHT_MULT=True
                        scene.render_scene(b,421.3,33,n,'chuva',.62,map_kind=kind)
                        self.assertEqual(rgba(a),rgba(b),(flags,level))
            self.assertEqual(random.getstate(),rng)
        finally:
            city._QA_DIRECT_NIGHT_MULT=previous

    def test_clipping_sdl_idem_retangulo_e_sprites_reais(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_city2_v3118 as scene118
        scene=CityPilotScene()
        prev=scene118._QA_NATIVE_CLIP
        try:
            variants=[layer.variants[0] for layer in scene.layers if layer.variants]
            for flags in (0,pygame.SRCALPHA):
                for variant in variants:
                    for x in (-950,-900,-899,-470,-450,-18,-1,0,1,212,449,450,600):
                        a=pygame.Surface((450,500),flags)
                        a.fill((16,25,43,140) if flags else (16,25,43))
                        b=a.copy()
                        scene118._QA_NATIVE_CLIP=False
                        scene._render_chunk(a,variant,False,x,79,.72,'nevasca',.42)
                        scene118._QA_NATIVE_CLIP=True
                        scene._render_chunk(b,variant,False,x,79,.72,'nevasca',.42)
                        self.assertEqual(rgba(a),rgba(b),(flags,x))
        finally:
            scene118._QA_NATIVE_CLIP=prev

    def test_scroll_incremental_cidade_inclui_sprites_ativos(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_qa_incremental_scene_v327750 as incremental
        incremental.restaurar_para_teste()
        original=CityPilotScene._render_chunk
        scene=CityPilotScene()
        variant=next(v for layer in scene.layers for v in layer.variants
                     if v.sprites)
        env=os.environ.get('PIXELRUSH_QA_CITY_INCREMENTAL')
        try:
            os.environ['PIXELRUSH_QA_CITY_INCREMENTAL']='1'
            incremental.instalar()
            for flags in (0,pygame.SRCALPHA):
                for i,x in enumerate((-430,-429,-425,-421,-417,-399,-397,
                                      -380,-356,-349,-347,-344)):
                    a=pygame.Surface((450,500),flags)
                    a.fill((21,35,64,91) if flags else (21,35,64))
                    b=a.copy()
                    original(scene,a,variant,False,x,78+i,.43,'vento',.52,
                             map_kind='image')
                    scene._render_chunk(b,variant,False,x,78+i,.43,'vento',.52,
                                        map_kind='image')
                    self.assertEqual(rgba(a),rgba(b),(flags,i,x))
            # QA755: texturas reais image usam SDL-RLE e devem seguir
            # blit original: cache RGBA_MAX preservaria visual mas
            # alteraria RGB oculto em destino alpha=0.
            self.assertGreater(incremental.diagnostico()['cidade_rle_direto'],0)
        finally:
            incremental.restaurar_para_teste()
            if env is None:os.environ.pop('PIXELRUSH_QA_CITY_INCREMENTAL',None)
            else:os.environ['PIXELRUSH_QA_CITY_INCREMENTAL']=env
        self.assertIs(CityPilotScene._render_chunk,original)

    def test_limpeza_nao_remove_mapas_gpu_ativos(self):
        from pixelrush_qa_cache_trim_v327748 import EscalonadorTrimQA
        class World:
            pass
        w=World()
        w.biome='cidade'
        w.frame=240
        key=('geometry',False)
        w._city_surfaces={key:object(),('image',False):object()}
        w._qa_surface_last_used={key:('cidade',239)}
        cleaner=EscalonadorTrimQA(limite_por_passo=3)
        self.assertFalse(cleaner._aplicar(weakref.ref(w),'_city_surfaces',key))
        self.assertIn(key,w._city_surfaces)
        w.frame=440
        self.assertTrue(cleaner._aplicar(weakref.ref(w),'_city_surfaces',key))
        self.assertNotIn(key,w._city_surfaces)
        self.assertIn(('image',False),w._city_surfaces)


if __name__=='__main__':
    unittest.main(verbosity=2)
