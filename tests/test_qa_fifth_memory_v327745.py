# -*- coding: utf-8 -*-
"""PIXEL RUSH QA 3.277.45: 5o quadro e memoria, testes pygame-ce offline.

Nao altera politica, imagens, fisica ou codigo de jogo. Experimentos de
buffers/copia sao isolados do runtime; alternativas NAO sao ativadas.
"""
import os
import sys
import unittest
from pathlib import Path
from collections import OrderedDict
from types import SimpleNamespace

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame


def pixels(s):
    return pygame.image.tobytes(s,'RGBA')


def fundo(s,frame):
    s.fill(((frame*3)%256,38,(frame*7)%256))
    for j in range(21):
        pygame.draw.rect(s,((frame+j*7)%256,105,179),
                         ((frame*2+j*41)%495-30,234+j*20,32,23))
    camada=pygame.Surface((91,41),pygame.SRCALPHA)
    camada.fill((31,218,175,111))
    s.blit(camada,((frame*13)%375,405))


def hud(s,frame):
    pygame.draw.rect(s,(30,55,90),(0,0,450,42))
    pygame.draw.rect(s,(255,206,78),(10,12,20+frame%95,15))


class QuintoQuadroMemoriaQA745(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_600_frames_ciclo_cinco_pixel_exato_hud_dinamico(self):
        from pixelrush_qa_ultraleve_v327730 import CacheFundoUltraQA
        cache=CacheFundoUltraQA(periodo=5)
        surf=pygame.Surface((450,800)).convert()
        referencia=surf.copy()
        guardado=None
        ultimo_redraw=None
        for i in range(600):
            # Mudancas de clima e bioma sao parte da chave do jogo.
            chave=('cidade' if i<300 else 'neve',
                   'chuva' if i<150 else 'nevasca' if i<450 else 'limpo')
            hit=cache.reusar(surf,chave,True)
            if not hit:
                fundo(surf,i)
                cache.guardar(surf,chave,True)
                ultimo_redraw=i
                guardado=surf.copy()
            # Reconstroi a MESMA politica de 1 redraw/4 hit, sem cache pygame.
            referencia.blit(guardado,(0,0))
            hud(surf,i)
            hud(referencia,i)
            self.assertEqual(pixels(surf),pixels(referencia),('frame',i))
            if i not in (150,300,450) and ultimo_redraw is not None:
                self.assertLess(i-ultimo_redraw,5)
        self.assertEqual(cache.recriacoes,120)
        self.assertEqual(cache.passes_evitados,480)

    def test_copia_do_cache_preserva_pixels_e_suporte_RGB(self):
        from pixelrush_qa_ultraleve_v327730 import CacheFundoUltraQA
        for flags in (0,pygame.SRCALPHA):
            dest=pygame.Surface((450,800),flags)
            cache=CacheFundoUltraQA(periodo=5)
            for i in range(12):
                fundo(dest,i)
                cache.guardar(dest,('city',flags),True)
                back=pygame.Surface((450,800),flags)
                self.assertTrue(cache.reusar(back,('city',flags),True))
                # O cache conserva RGB do fundo; alpha do destino nao faz parte
                # do contrato original do cache, que usa convert() sem SRCALPHA.
                expected=pygame.Surface((450,800),flags)
                expected.blit(cache._quadro,(0,0))
                self.assertEqual(pixels(back),pixels(expected))
                self.assertIsNotNone(cache._quadro)
                self.assertEqual(cache._quadro.get_size(),(450,800))

    def test_mundo_real_render_direto_em_buffer_separado_pixel_a_pixel(self):
        from pixelrush_world_v3130 import LivingWorld
        # Hipotese OFFLINE: renderizar diretamente no buffer de cache, com
        # mesmo formato e fundo, poderia substituir a copia. Nao ativa nada.
        for biome in ('cidade','neve','deserto'):
            world=LivingWorld(biome,lightweight=False)
            ref=pygame.Surface((450,800)).convert()
            direct=ref.copy()
            for i in range(10):
                clima=('chuva','nevasca','tempestade_areia')[('cidade','neve','deserto').index(biome)]
                world.update(10.5,night=(i%5)/5,climate=clima,phase=.51)
                ref.fill((29,52,71))
                direct.fill((29,52,71))
                world.draw(ref)
                world.draw(direct)
                self.assertEqual(pixels(ref),pixels(direct),(biome,i))
                # A prova e limitada ao mundo 2.5D: outros efeitos e fundo
                # principal do jogo NAO estao presentes nesta fixture.
                cached=pygame.Surface((450,800)).convert(ref)
                cached.blit(ref,(0,0))
                self.assertEqual(pixels(cached),pixels(direct),(biome,i,'copy'))

    def test_limpador_180_flips_preserva_cidade_e_registra_tempo(self):
        import pixelrush_qa_performance_integrated_v327742 as perf
        class FakeWorld:
            def __init__(self):
                self.biome='cidade'
                self.props_cache={}
                self.cache=OrderedDict()
                self.fx_cache=OrderedDict()
                self.normal_cache=OrderedDict()
                self.material_cache=OrderedDict()
                self.flow_cache=OrderedDict()
                self.geometry_cache=OrderedDict()
                self._city_surfaces={('image',False):object(),
                                     ('normal',False):object()}
                self.city2=SimpleNamespace(_scaled=OrderedDict((i,object()) for i in range(14)))
        old_mem=perf._memory_mib
        old_status=dict(perf._LAST_STATUS)
        perf.restaurar_para_teste()
        fake=FakeWorld()
        try:
            perf.instalar()
            perf._WORLDS.add(fake)
            perf._memory_mib=lambda:900.
            perf._LAST_STATUS['frames']=0
            for i in range(360):
                pygame.display.flip()
                if i in (179,359):
                    self.assertGreaterEqual(perf._LAST_STATUS['cache_cleanup_last_ms'],0)
                    self.assertGreaterEqual(perf._LAST_STATUS['cache_cleanup_p95_ms'],0)
                    self.assertEqual(len(fake.city2._scaled),14)
            self.assertNotIn(('normal',False),fake._city_surfaces)
            self.assertIn(('image',False),fake._city_surfaces)
        finally:
            perf._memory_mib=old_mem
            perf.restaurar_para_teste()
            perf._LAST_STATUS.clear()
            perf._LAST_STATUS.update(old_status)

    def test_trocas_de_bioma_retencao_delimitada(self):
        from pixelrush_world_v3130 import LivingWorld
        world=LivingWorld('cidade',lightweight=False)
        out=pygame.Surface((450,800),pygame.SRCALPHA)
        for biome in ('cidade','neve','deserto','cidade','neve','cidade'):
            if world.biome!=biome:
                world.switch(biome)
            world.update(12.3,night=.52,climate='limpo',phase=.61)
            world.draw(out)
            self.assertLessEqual(len(world.modular),1)
            self.assertLessEqual(len(world.city2._scaled),14)
            self.assertLessEqual(len(world.city2._night_veils),13)
            self.assertLessEqual(len(world._city_surfaces),8)
        self.assertEqual(world.biome,'cidade')


if __name__=='__main__':
    unittest.main(verbosity=2)
