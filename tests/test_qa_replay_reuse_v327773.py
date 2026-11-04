# -*- coding: utf-8 -*-
"""QA773: compara visual real do replay e bytes completos após 72 amostras."""
import os
import statistics
import time
import unittest
from unittest.mock import patch
from collections import deque

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
from pixelrush_extras_v3174 import ReplayCinematografico
import pixelrush_qa_replay_pool_v327773 as qa

class ReplayR10773(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        qa.restaurar_para_teste()
        pygame.quit()
    def tearDown(self):
        qa.restaurar_para_teste()

    def comparar(self,flag):
        qa.restaurar_para_teste()
        original=ReplayCinematografico.capturar
        controle=ReplayCinematografico()
        candidato=ReplayCinematografico()
        with patch.dict(os.environ,{'PIXELRUSH_QA_REPLAY_REUSE':'1'}):
            qa.instalar()
        quadro=pygame.Surface((450,800),flag,32)
        for tick in range(1,500):
            if flag:
                quadro.fill(((tick*3)%256,(tick*11)%256,(tick*17)%256,0))
                pygame.draw.rect(quadro,((tick*5)%256,(tick*7)%256,234,217),
                                 (13+tick%30,20+tick%27,85,90))
            else:
                quadro.fill(((tick*3)%256,(tick*11)%256,(tick*17)%256))
                pygame.draw.rect(quadro,((tick*5)%256,(tick*7)%256,234),
                                 (13+tick%30,20+tick%27,85,90))
            original(controle,quadro,tick)
            candidato.capturar(quadro,tick)
            self.assertEqual(len(controle.buffer),len(candidato.buffer))
            self.assertEqual(controle.ultima_amostra,candidato.ultima_amostra)
            if tick in (1,27,356,391,440,499):
                for a,b in zip(controle.buffer,candidato.buffer):
                    self.assertEqual(pygame.image.tobytes(a,'RGBA'),
                                     pygame.image.tobytes(b,'RGBA'))
        self.assertEqual(len(candidato.buffer),72)
        self.assertGreater(qa.diagnostico()['reusadas'],0)
        self.assertGreater(qa.diagnostico()['bytes_evitados'],0)
        self.assertEqual(qa.diagnostico()['fallbacks'],0)
        controle.iniciar()
        candidato.iniciar()
        for _ in range(20):
            tela_original=pygame.Surface((450,800),flag,32)
            tela_reuso=pygame.Surface((450,800),flag,32)
            controle.desenhar(tela_original)
            candidato.desenhar(tela_reuso)
            self.assertEqual(pygame.image.tobytes(tela_original,'RGBA'),
                             pygame.image.tobytes(tela_reuso,'RGBA'))
        self.assertTrue(controle.congelado and candidato.congelado)

    def test_replay_rgb_completo(self):
        self.comparar(0)

    def test_replay_rgba_com_rgb_oculto_alpha_zero(self):
        self.comparar(pygame.SRCALPHA)

    def test_flag_off_delega_totalmente_ao_original(self):
        qa.restaurar_para_teste()
        anterior=ReplayCinematografico.capturar
        with patch.dict(os.environ,{'PIXELRUSH_QA_REPLAY_REUSE':'0'}):
            qa.instalar()
        self.assertIs(ReplayCinematografico.capturar,anterior)
        self.assertFalse(qa.diagnostico()['instalado'])

    def test_fallback_em_formato_diferente_e_byte_identico(self):
        qa.restaurar_para_teste()
        base=ReplayCinematografico()
        wrapped=ReplayCinematografico()
        original=ReplayCinematografico.capturar
        qa.instalar()
        rgb=pygame.Surface((450,800))
        for tick in range(1,362):
            rgb.fill(((tick*17)%256,(tick*9)%256,(tick*11)%256))
            original(base,rgb,tick)
            wrapped.capturar(rgb,tick)
        rgba=pygame.Surface((450,800),pygame.SRCALPHA,32)
        rgba.fill((50,180,120,89))
        original(base,rgba,362)
        wrapped.capturar(rgba,362)
        self.assertGreaterEqual(qa.diagnostico()['originais'],1)
        self.assertEqual(pygame.image.tobytes(base.buffer[-1],'RGBA'),
                         pygame.image.tobytes(wrapped.buffer[-1],'RGBA'))

    def test_microbenchmark_captura_buffer_cheio(self):
        quadro=pygame.Surface((450,800)).convert()
        destino=(225,400)
        frames=deque((pygame.transform.scale(quadro,destino) for _ in range(72)),maxlen=72)
        med={'original':[],'reuso':[]}
        for grupo in range(10):
            rotas=('original','reuso') if grupo%2==0 else ('reuso','original')
            for rota in rotas:
                for i in range(60):
                    quadro.fill(((i*19)%256,(i*17)%256,(i*29)%256))
                    t=time.perf_counter_ns()
                    if rota=='original':
                        frames.append(pygame.transform.scale(quadro,destino))
                    else:
                        antigo=frames.popleft()
                        pygame.transform.scale(quadro,destino,antigo)
                        frames.append(antigo)
                    med[rota].append((time.perf_counter_ns()-t)/1e6)
        orig=statistics.median(med['original'])
        novo=statistics.median(med['reuso'])
        print('QA773 capture p50 original=%.5fms, reuso=%.5fms'%(orig,novo))
        self.assertLess(novo,orig*1.35)

if __name__=='__main__':
    unittest.main(verbosity=2)
