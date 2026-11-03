# -*- coding: utf-8 -*-
"""QA v3.277.56 — gates manuais, não homologação final.

Verifica 1:1 RGBA (inclusive RGB oculto), SRCALPHA, composições com
sprites e equivalência de fill opaco uniforme com blit de atlas 2x;
exige também fallback de scroll SDL-RLE SEM exceção Python.
"""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame


def rgba(surface):
    return pygame.image.tobytes(surface,'RGBA')


class SRCALPHAUniforme756(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_uniformes_reais_identificados_sem_criar_cache_de_escala(self):
        from pixelrush_city2_v3125 import CityPilotScene
        scene=CityPilotScene()
        uniforms=getattr(scene,'_qa_uniform_tech',{})
        self.assertGreater(len(uniforms),0,
                           'sem atlas uniforme: verificar dados reais antes de aprovar gate')
        variants={id(v):v for l in scene.layers for v in l.variants}
        for (variant_id,kind),(source_id,color) in uniforms.items():
            variant=variants[variant_id]
            src=getattr(variant,kind)
            self.assertEqual(id(src),source_id)
            self.assertEqual(color[3],255)
            self.assertEqual(src.get_size(),(450,250))
            self.assertEqual(src.get_pitch(),450*4)
            raw=memoryview(src.get_view('0'))
            try:
                self.assertEqual(raw.tobytes(),raw[:4].tobytes()*(450*250),
                                 (kind,source_id))
            finally:
                raw.release()
        self.assertEqual(scene._qa_uniform_tech_hits,0)

    def test_chunk_real_uniforme_vs_blit_legado_rgb_rgba_e_alpha_zero(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_city2_v3118 as core
        scene=CityPilotScene()
        original=core._QA_UNIFORM_TECH_FILL
        variants={id(v):v for l in scene.layers for v in l.variants}
        probes=list(scene._qa_uniform_tech.items())[:12]
        self.assertGreater(len(probes),0)
        try:
            for flags in (0,pygame.SRCALPHA):
                for a in (0,1,81,255):
                    for x in (-950,-680,-452,-230,0,75,449,450):
                        for (variant_id,kind),_ in probes:
                            variant=variants[variant_id]
                            baseline=pygame.Surface((450,500),flags)
                            baseline.fill((16,69,118,a) if flags else (16,69,118))
                            fast=baseline.copy()
                            core._QA_UNIFORM_TECH_FILL=False
                            scene._render_chunk(baseline,variant,False,x,43,
                                                .41,'vento',.56,map_kind=kind)
                            core._QA_UNIFORM_TECH_FILL=True
                            scene._render_chunk(fast,variant,False,x,43,
                                                .41,'vento',.56,map_kind=kind)
                            self.assertEqual(rgba(baseline),rgba(fast),
                                             (flags,a,x,kind))
            self.assertGreater(scene._qa_uniform_tech_hits,0)
        finally:
            core._QA_UNIFORM_TECH_FILL=original

    def test_render_real_normal_flow_nao_perde_rgb_invisivel(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_city2_v3118 as core
        scene=CityPilotScene()
        before=core._QA_UNIFORM_TECH_FILL
        try:
            for kind in ('normal','flow','image','geometry','fxmask','material'):
                for alpha in (0,1,127,255):
                    for frame in (0,5,23):
                        a=pygame.Surface((450,500),pygame.SRCALPHA,32)
                        a.fill((63,98,147,alpha))
                        b=a.copy()
                        core._QA_UNIFORM_TECH_FILL=False
                        scene.render_scene(a,frame*7.25,frame,.43,
                                           'chuva',.7,map_kind=kind)
                        core._QA_UNIFORM_TECH_FILL=True
                        scene.render_scene(b,frame*7.25,frame,.43,
                                           'chuva',.7,map_kind=kind)
                        self.assertEqual(rgba(a),rgba(b),(kind,alpha,frame))
        finally:
            core._QA_UNIFORM_TECH_FILL=before

    def test_scroll_rle_retorna_fallback_sem_excecao(self):
        import pixelrush_qa_incremental_scene_v327750 as scroll
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_city2_v3118 as core
        scene=CityPilotScene()
        original_accel=core.acelerar_textura_estatica
        src=pygame.Surface((450,250),pygame.SRCALPHA,32)
        src.fill((72,119,161,0))
        pygame.draw.rect(src,(223,89,58,208),(7,23,121,98))
        class Variant:
            image=src
            sprites=[]
        variant=Variant()
        try:
            def enable_rle(s):
                s.set_alpha(255,pygame.RLEACCEL)
                return s
            core.acelerar_textura_estatica=enable_rle
            # nenhum monkeypatch de render / cache precisa ser instalado:
            # valida o retorno seguro da função do módulo QA.
            before=scroll.diagnostico()['cidade_rle_direto']
            outcome=scroll._atualizar_persistente(scene,variant,'image',-700)
            self.assertIsNone(outcome)
            self.assertGreater(scroll.diagnostico()['cidade_rle_direto'],before)
            self.assertFalse(scroll.tem_cache_cena(scene))
        finally:
            core.acelerar_textura_estatica=original_accel

    def test_rollback_uniforme_nao_muda_arte(self):
        from pixelrush_city2_v3125 import CityPilotScene
        import pixelrush_city2_v3118 as core
        scene=CityPilotScene()
        orig=core._QA_UNIFORM_TECH_FILL
        try:
            core._QA_UNIFORM_TECH_FILL=False
            a=pygame.Surface((450,500),pygame.SRCALPHA,32)
            scene.render_scene(a,246.25,61,.74,'tempestade',.41)
            core._QA_UNIFORM_TECH_FILL=True
            b=pygame.Surface((450,500),pygame.SRCALPHA,32)
            scene.render_scene(b,246.25,61,.74,'tempestade',.41)
            self.assertEqual(rgba(a),rgba(b))
        finally:
            core._QA_UNIFORM_TECH_FILL=orig


if __name__=='__main__':
    unittest.main(verbosity=2)
