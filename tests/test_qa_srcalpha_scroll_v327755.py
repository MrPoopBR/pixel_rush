# -*- coding: utf-8 -*-
"""QA755: gates offline preparados; nao executar homologacao final/APK/Android.

Testam canais RGB ocultos em SRCALPHA, contexto normal/flow preenchido alfa
255, deduplicacao de atlas RGBA exatos e scroll por cobertura/salto.
"""
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame


def bytes_rgba(s):
    return pygame.image.tobytes(s,"RGBA")


class SrcAlpha755(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_normal_flow_real_rgba_mantem_bytes_apos_alfa255(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_city2_v3124 as city
        scene=CityPilotScene()
        saved=city._QA_TECH_OPAQUE_BOUNDS
        try:
            for kind in ("normal","flow"):
                for alpha in (0,1,127,255):
                    for step in (0,3,15,48,90):
                        old=pygame.Surface((450,500),pygame.SRCALPHA,32)
                        old.fill((73,31,56,alpha))
                        fast=old.copy()
                        city._QA_TECH_OPAQUE_BOUNDS=False
                        scene.render_scene(old,41.3+step*8,step,.36,
                                           "chuva",.6,map_kind=kind)
                        city._QA_TECH_OPAQUE_BOUNDS=True
                        scene.render_scene(fast,41.3+step*8,step,.36,
                                           "chuva",.6,map_kind=kind)
                        self.assertEqual(bytes_rgba(old),bytes_rgba(fast),
                                         ("opaque_real",kind,alpha,step))
                        self.assertIsNone(
                            getattr(scene,"_qa_opaque_safe_target",None))
        finally:
            city._QA_TECH_OPAQUE_BOUNDS=saved

    def test_contexto_opaque_nao_vaza_apos_excecao(self):
        from pixelrush_city2_v3125 import CityPilotScene
        scene=CityPilotScene()
        target=pygame.Surface((450,500),pygame.SRCALPHA,32)
        orig=scene._render_chunk
        def falhar(*args,**kwargs):
            raise RuntimeError("render_falhou_deliberadamente")
        try:
            scene._render_chunk=falhar
            with self.assertRaisesRegex(RuntimeError,"render_falhou"):
                scene.render_scene(target,100.,30,.2,"limpo",.5,
                                   map_kind="normal")
            self.assertIsNone(getattr(scene,"_qa_opaque_safe_target",None))
        finally:
            scene.__dict__.pop("_render_chunk",None)
            self.assertIs(scene._render_chunk.__func__,orig.__func__)

    def test_crop_opaque_tech_provado_e_alpha_zero_bloqueado(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_city2_v3118 as core
        scene=CityPilotScene()
        low=pygame.Surface((450,250),pygame.SRCALPHA,32)
        low.fill((45,91,120,0)) # RGBA oculto precisa ser preservado fora do bbox
        pygame.draw.rect(low,(121,199,54,172),(33,29,160,70))
        src=SimpleNamespace(normal=low,sprites=[])
        roi=(33*2,29*2,160*2,70*2)
        scene._qa_alpha_bounds[(id(src),"normal",id(low))]=roi
        oldflag=core._QA_ALPHA_BOUNDS
        try:
            for alpha in (0,1,77,255):
                a=pygame.Surface((450,500),pygame.SRCALPHA,32)
                a.fill((15,33,70,alpha))
                b=a.copy()
                core._QA_ALPHA_BOUNDS=False
                scene._qa_opaque_safe_target=None
                scene._render_chunk(a,src,False,-350,2,.4,
                                    "limpo",.5,"normal")
                core._QA_ALPHA_BOUNDS=True
                scene._render_chunk(b,src,False,-350,2,.4,
                                    "limpo",.5,"normal")
                self.assertEqual(bytes_rgba(a),bytes_rgba(b),
                                 ("unmarked",alpha))
            a=pygame.Surface((450,500),pygame.SRCALPHA,32)
            a.fill((128,128,255,255))
            b=a.copy()
            core._QA_ALPHA_BOUNDS=False
            scene._render_chunk(a,src,False,-350,2,.4,"limpo",.5,"normal")
            core._QA_ALPHA_BOUNDS=True
            scene._qa_opaque_safe_target=b
            try:
                scene._render_chunk(b,src,False,-350,2,.4,"limpo",.5,"normal")
            finally:
                scene._qa_opaque_safe_target=None
            self.assertEqual(bytes_rgba(a),bytes_rgba(b),"opaque_bbox")
        finally:
            core._QA_ALPHA_BOUNDS=oldflag

    def test_scaled_tech_dedup_rgba_identico_e_sem_alias_se_trocou(self):
        from pixelrush_city2_v3125 import CityPilotScene
        scene=CityPilotScene()
        self.assertGreater(len(scene._qa_scaled_alias),0)
        self.assertEqual(len(scene._scaled),0)
        variants={id(v):v for layer in scene.layers for v in layer.variants}
        # Mesma origem exata em bytes, flags, alpha e mascaras.
        for (variant_id,kind),(src_id,canonical_key) in list(
                scene._qa_scaled_alias.items())[:16]:
            v=variants[variant_id]
            representative=variants[canonical_key[0]]
            src=getattr(v,kind)
            orig=getattr(representative,kind)
            self.assertEqual(bytes_rgba(src),bytes_rgba(orig))
            scaled_a=scene._scaled_surface(v,kind)
            scaled_b=scene._scaled_surface(representative,kind)
            self.assertIs(scaled_a,scaled_b)
            self.assertEqual(bytes_rgba(scaled_a),bytes_rgba(scaled_b))
        self.assertGreater(scene._qa_scaled_alias_hits,0)

    def test_scroll_rgba_hidden_0_respeita_cobertura_fonte(self):
        import pixelrush_qa_incremental_scene_v327750 as mod
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_city2_v3118 as city_core
        saved_accel=city_core.acelerar_textura_estatica
        mod.restaurar_para_teste()
        original=CityPilotScene._render_chunk
        with patch.dict(os.environ,{
                "PIXELRUSH_QA_CITY_INCREMENTAL":"1",
                "PIXELRUSH_QA_CLASSIC_INCREMENTAL":"0",
                "PIXELRUSH_QA_CITY_SCROLL_SCOPE":"static"}):
            try:
                # Testar cache de fato em atlas NAO RLE; a rota RLE real
                # possui gate próprio de fallback byte-exato abaixo.
                city_core.acelerar_textura_estatica=lambda surf:surf
                mod.instalar()
                scene=CityPilotScene()
                low=pygame.Surface((450,250),pygame.SRCALPHA,32)
                low.fill((67,90,123,0))
                pygame.draw.rect(low,(193,72,101,169),
                                 (42,77,155,60))
                variant=SimpleNamespace(image=low,sprites=[])
                for alpha in (0,1,127,255):
                    for step,x in enumerate((-899,-820,-708,-705,-700,
                                             -693,-690,-400,-397,-394,-390,
                                             -385,-382,-250,-247,-244,
                                             -191,-189,0,2,3,447)):
                        ref=pygame.Surface((450,500),pygame.SRCALPHA,32)
                        ref.fill((23,57,99,alpha))
                        new=ref.copy()
                        original(scene,ref,variant,False,x,step,.6,
                                 "vento",.5,"image")
                        scene._render_chunk(new,variant,False,x,step,.6,
                                            "vento",.5,"image")
                        self.assertEqual(bytes_rgba(ref),bytes_rgba(new),
                                         ("scroll_hidden_rgba",alpha,step,x))
                stats=mod.diagnostico()
                self.assertGreater(stats["cidade_cobertura_direta"],0)
                self.assertGreater(stats["cidade_blit_cobertura_px"],0)
                self.assertGreater(stats["cidade_hit"],0)
                self.assertLessEqual(len(mod._CIDADE.get(scene,{})),2)
            finally:
                mod.restaurar_para_teste()
                city_core.acelerar_textura_estatica=saved_accel
        self.assertIs(CityPilotScene._render_chunk,original)


    def test_scroll_rle_alpha_zero_mantem_rgb_oculto_sem_cache(self):
        # SDL-RLE nao equivale a RGBA_MAX intermediario em destino alpha=0.
        # O caminho real deve cair no blit original, sem criar OrderedDict.
        import pixelrush_qa_incremental_scene_v327750 as mod
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_city2_v3118 as city_core
        old_accelerator=city_core.acelerar_textura_estatica
        mod.restaurar_para_teste()
        previous=CityPilotScene._render_chunk
        with patch.dict(os.environ,{
                "PIXELRUSH_QA_CITY_INCREMENTAL":"1",
                "PIXELRUSH_QA_CLASSIC_INCREMENTAL":"0",
                "PIXELRUSH_QA_CITY_SCROLL_SCOPE":"static"}):
            try:
                def rle_requerido(surface):
                    surface.set_alpha(255,pygame.RLEACCEL)
                    return surface
                # Independe do id-cache global do acelerador de sprites:
                # RLE pedido explicitamente na textura escala do fixture.
                city_core.acelerar_textura_estatica=rle_requerido
                mod.instalar()
                scene=CityPilotScene()
                low=pygame.Surface((450,250),pygame.SRCALPHA,32)
                low.fill((83,49,101,0))
                pygame.draw.rect(low,(204,51,91,197),(25,31,170,66))
                variant=SimpleNamespace(image=low,sprites=[])
                for alpha in (0,1,81,255):
                    for j,x in enumerate((-898,-700,-695,-690,-450,
                                          -445,-442,-180,0)):
                        expected=pygame.Surface((450,500),pygame.SRCALPHA,32)
                        expected.fill((29,71,113,alpha))
                        got=expected.copy()
                        previous(scene,expected,variant,False,x,j,.2,
                                 "limpo",.5,"image")
                        scene._render_chunk(got,variant,False,x,j,.2,
                                            "limpo",.5,"image")
                        self.assertEqual(bytes_rgba(expected),bytes_rgba(got),
                                         ("rle",alpha,j,x))
                self.assertGreater(mod.diagnostico()["cidade_rle_direto"],0)
                self.assertFalse(mod.tem_cache_cena(scene))
            finally:
                mod.restaurar_para_teste()
                city_core.acelerar_textura_estatica=old_accelerator
        self.assertIs(CityPilotScene._render_chunk,previous)


if __name__=="__main__":
    unittest.main(verbosity=2)
