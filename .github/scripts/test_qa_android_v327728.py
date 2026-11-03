"""QA: exercicio REAL do pygame-ce (SDL dummy), telemetria + saida JSON/CSV."""
import json
import os
import sys
from pathlib import Path
import tempfile
import unittest

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import pygame
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from pixelrush_qa_android_v327728 import QATelemetria


class TesteQAndroid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.tela = pygame.display.set_mode((450, 800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_corrida_replay_exportar(self):
        with tempfile.TemporaryDirectory() as pasta:
            qa = QATelemetria('v3.277.46-QA-ANDROID', 'LIMPA', caminho=pasta)
            for modo in ['JOGANDO', 'GAMEOVER_REPLAY_QA', 'GAMEOVER', 'INICIO', 'JOGANDO_TUTORIAL_QA']:
                for i in range(20):
                    qa.iniciar(modo, 'cidade')
                    qa.marcar('simulacao')
                    qa.sub_inicio('fisica_jogador')
                    pygame.draw.rect(self.tela, (i*5, 50, 90), (0, 0, 100, 100))
                    qa.sub_fim()
                    qa.marcar('renderizacao_e_ui')
                    qa.sub_inicio('mundo_2_5d')
                    self.tela.fill((40, 50, 70))
                    qa.sub_fim()
                    qa.marcar('apresentacao')
                    pygame.display.flip()
                    qa.marcar('limitador_fps')
                    qa.fim()
            self.assertTrue(qa.salvar())
            rel = json.loads((Path(pasta) / 'pixelrush_qa_v327746.json').read_text('utf-8'))
            self.assertEqual(rel['quadros_observados'], 100)
            self.assertEqual(set(rel['grupos']), {'corrida_normal|cidade', 'replay|cidade', 'gameover|cidade', 'inicio|cidade', 'tutorial|cidade'})
            self.assertEqual(rel['grupos']['corrida_normal|cidade']['metricas_ms']['mundo_2_5d']['n'], 20)
            self.assertEqual(rel['grupos']['replay|cidade']['metricas_ms']['quadro_total_ms']['n'], 20)
            self.assertIn('render_residual_estimado',rel['grupos']['corrida_normal|cidade']['metricas_ms'])
            self.assertIsNone(rel['gpu_ms_real'])
            self.assertEqual((Path(pasta) / 'pixelrush_qa_frames_v327746.csv').read_text('utf-8').count('\n'), 101)

    def test_picos_e_limite_de_memoria(self):
        with tempfile.TemporaryDirectory() as pasta:
            qa = QATelemetria('teste', 'LIMPA', caminho=pasta)
            qa.iniciar('JOGANDO', 'neve')
            qa.marcar('apresentacao')
            pygame.time.wait(40)
            qa.marcar('limitador_fps')
            qa.fim()
            rel = qa.relatorio()
            self.assertEqual(rel['grupos']['corrida_normal|neve']['travamentos_trabalho']['mais_33ms'], 1)
            self.assertGreater(rel['grupos']['corrida_normal|neve']['metricas_ms']['trabalho_sem_limitador_ms']['max'], 33.333)
            self.assertEqual(len(rel['piores_100_quadros_sem_limitador']), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)