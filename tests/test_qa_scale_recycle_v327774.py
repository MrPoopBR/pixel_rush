# -*- coding: utf-8 -*-
"""QA774: cidade real e escalas LRU, RGBA oculto, referencias e rollback.

Nenhum teste Android/APK. Compara o metodo herdado realmente usado no jogo
com o caminho original e mede somente a operacao de escala de atlas.
"""
import os
import random
import statistics
import sys
import time
import unittest
from collections import OrderedDict
from pathlib import Path
from types import SimpleNamespace
from weakref import WeakSet

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pygame


def rgba(s):
    return pygame.image.tobytes(s, 'RGBA')


class QA774ReusoEscalas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450, 800))
        from pixelrush_qa_city_bootstrap_v327759 import instalar
        instalar()
        from pixelrush_city2_v3125 import CityPilotScene
        cls.scene = CityPilotScene()

    @classmethod
    def tearDownClass(cls):
        from pixelrush_qa_city_bootstrap_v327759 import restaurar_para_teste
        restaurar_para_teste()
        pygame.quit()

    def setUp(self):
        import pixelrush_city2_v3118 as base
        self.base = base
        self.old = base._QA_RECYCLE_TECH_SCALE
        self.scene._scaled_limit = 14

    def tearDown(self):
        self.base._QA_RECYCLE_TECH_SCALE = self.old
        self.scene._scaled.clear()
        self.scene._scaled_limit = 14

    def clear(self, limit=4):
        scene = self.scene
        scene._scaled.clear()
        scene._scaled_limit = limit
        scene._qa_scaled_owned = WeakSet()
        scene._qa_scaled_allocated = 0
        scene._qa_scaled_reused = 0
        scene._qa_scaled_rejected = 0

    def atlas(self, qtd=32):
        # Superficies tecnicas unicas com alfa zero e RGB oculto; descartaveis.
        rng = random.Random(774)
        out = []
        for i in range(qtd):
            tex = pygame.Surface((450, 250), pygame.SRCALPHA, 32)
            tex.fill((rng.randrange(256), rng.randrange(256),
                      rng.randrange(256), 0 if i%3 == 0 else 120))
            pygame.draw.rect(tex, (i*7%256, 200, 43, 255),
                             (i%33, 2+i%43, 30, 28))
            out.append(SimpleNamespace(geometry=tex))
        return out

    def test_escalas_rgba_identicas_sem_alocar_em_cada_miss(self):
        variations = self.atlas(28)
        indices = [(i*11)%28 for i in range(96)]
        self.base._QA_RECYCLE_TECH_SCALE = False
        self.clear()
        referencia = [rgba(self.scene._scaled_surface(variations[i],'geometry'))
                      for i in indices]
        self.base._QA_RECYCLE_TECH_SCALE = True
        self.clear()
        resultado = [rgba(self.scene._scaled_surface(variations[i],'geometry'))
                     for i in indices]
        self.assertEqual(referencia, resultado)
        self.assertGreater(self.scene._qa_scaled_reused, 40)
        self.assertLessEqual(self.scene._qa_scaled_allocated, 6)
        self.assertEqual(len(self.scene._scaled),4)

    def test_referencia_externa_nunca_e_reescrita(self):
        variation = self.atlas(20)
        self.base._QA_RECYCLE_TECH_SCALE = True
        self.clear(limit=2)
        retida = self.scene._scaled_surface(variation[0],'geometry')
        exata = rgba(retida)
        for v in variation[1:]:
            self.scene._scaled_surface(v,'geometry')
        self.assertEqual(rgba(retida),exata)
        self.assertGreater(self.scene._qa_scaled_rejected,0)

    def test_rollback_original_e_ausencia_de_alias_1a1(self):
        a=pygame.Surface((900,500),pygame.SRCALPHA,32)
        a.fill((13,29,183,0))
        v=SimpleNamespace(geometry=a)
        self.base._QA_RECYCLE_TECH_SCALE=True
        self.clear(limit=1)
        self.assertIs(self.scene._scaled_surface(v,'geometry'),a)
        before=rgba(a)
        b=self.atlas(3)
        for var in b:self.scene._scaled_surface(var,'geometry')
        self.assertEqual(before,rgba(a))
        self.base._QA_RECYCLE_TECH_SCALE=False
        self.clear(limit=2)
        self.scene._scaled_surface(b[0],'geometry')
        self.scene._scaled_surface(b[1],'geometry')
        self.scene._scaled_surface(b[2],'geometry')
        self.assertEqual(self.scene._qa_scaled_reused,0)
        self.assertEqual(self.scene._qa_scaled_allocated,0)

    def test_cidade_real_passe_image_e_5_mapas_rgba_rgb(self):
        from pixelrush_city2_v3115 import WIDTH, SCENE_H
        s=self.scene
        # Comparacao integral do render_scene herdado no jogo, incluindo
        # sprites, luz, noite, chuva, canais e RGB oculto de alpha zero.
        for flags in (0,pygame.SRCALPHA):
            for kind in ('image','geometry','normal','material','flow','fxmask'):
                for i,(frame,night,climate) in enumerate(
                        ((4,.0,'limpo'),(55,.37,'chuva'))):
                    self.base._QA_RECYCLE_TECH_SCALE=False
                    self.clear(limit=4)
                    a=pygame.Surface((WIDTH,SCENE_H),flags,32)
                    a.fill((45,72,99,0) if flags else (45,72,99))
                    s.render_scene(a,190.3+i*83.7,frame,night,climate,.48,
                                   map_kind=kind)
                    self.base._QA_RECYCLE_TECH_SCALE=True
                    self.clear(limit=4)
                    b=pygame.Surface((WIDTH,SCENE_H),flags,32)
                    b.fill((45,72,99,0) if flags else (45,72,99))
                    s.render_scene(b,190.3+i*83.7,frame,night,climate,.48,
                                   map_kind=kind)
                    self.assertEqual(rgba(a),rgba(b),
                                     (flags,kind,frame,night,climate))

    def test_benchmark_alternado_escala_com_igualdade(self):
        arr=self.atlas(18)
        indices=[(i*7)%18 for i in range(72)]
        resultados={}
        snapshots={}
        for recycle in (False,True,True,False):
            self.base._QA_RECYCLE_TECH_SCALE=recycle
            self.clear(limit=4)
            samples=[]
            outputs=[]
            for i in indices:
                t=time.perf_counter_ns()
                dst=self.scene._scaled_surface(arr[i],'geometry')
                samples.append(time.perf_counter_ns()-t)
                # Capturar bytes apos a operacao: o proximo LRU pode
                # reutilizar a mesma Surface sem referencias externas.
                outputs.append(rgba(dst))
            name='reuso' if recycle else 'original'
            resultados.setdefault(name,[]).append(statistics.median(samples)/1e6)
            if name in snapshots:
                self.assertEqual(snapshots[name],outputs)
            else:
                snapshots[name]=outputs
        self.assertEqual(snapshots['original'],snapshots['reuso'])
        print('QA774 LRU escala original p50 ms:',resultados['original'],
              'reuso p50 ms:',resultados['reuso'])
        # Bench e informativo (runner CI variavel); evidencia de menos
        # alocacoes e igualdade sao gates deterministas acima.


    def test_benchmark_renderizacao_cidade_real_multicanal(self):
        """Percurso real CityPilotScene, comparando passes de todos os canais.

        Bytes RGBA completos incluindo alpha0; reporta tempos sem impor
        threshold inconstante de runner compartilhado. LRU14 original.
        """
        scene=self.scene
        outputs={}
        tempos={}
        stats={}
        roteiro=[(kind,j) for j in range(5)
                 for kind in ('image','geometry','normal','material','flow','fxmask')]
        for mode in (False,True):
            self.base._QA_RECYCLE_TECH_SCALE=mode
            self.clear(limit=14)
            images=[]
            ns=[]
            for kind,j in roteiro:
                dst=pygame.Surface((450,500),pygame.SRCALPHA,32)
                dst.fill((23,45,77,0))
                t=time.perf_counter_ns()
                scene.render_scene(dst, 180.9+71.3*j, 44+j*5,
                                   .33,'chuva',.47,map_kind=kind)
                ns.append(time.perf_counter_ns()-t)
                images.append(rgba(dst))
            outputs[mode]=images
            tempos[mode]=(statistics.median(ns)/1e6,
                          max(ns)/1e6,sum(ns)/1e6)
            stats[mode]=(scene._qa_scaled_allocated,
                         scene._qa_scaled_reused,
                         scene._qa_scaled_rejected)
        self.assertEqual(outputs[False],outputs[True])
        print('QA774 Cidade REAL 30 passes p50/max/total (ms):',tempos,
              'alocadas/reusadas/rejeitadas:',stats)
        # Nenhuma aprovacao de FPS Android baseada no runner Ubuntu.


if __name__=='__main__':
    unittest.main(verbosity=2)
