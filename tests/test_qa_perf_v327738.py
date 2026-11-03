# -*- coding: utf-8 -*-
"""Regressoes QA v3.277.38: lote de profundidade, SDF e estatisticas worker."""
import ast
import csv
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest

os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame


def rgba(surface):
    return pygame.image.tobytes(surface, 'RGBA')


class TestDeepPerformanceV327738(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450, 800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_profundidade_batch_pixel_exato(self):
        from pixelrush_qa_alpha_blit_v327731 import (
            _blit_visivel, _blits_visiveis,
        )
        for flags in (0, pygame.SRCALPHA):
            for tipo in ('rgba', 'colorkey'):
                tex = pygame.Surface((600, 450),
                                     pygame.SRCALPHA if tipo == 'rgba' else 0)
                if tipo == 'rgba':
                    tex.fill((0, 0, 0, 0))
                    for n in range(80):
                        pygame.draw.rect(tex,
                            ((n*11)%256, (n*7)%256, (n*3)%256, (n*31)%256),
                            (105+n*4, 35+n*3, 70, 42))
                else:
                    tex.fill((255, 0, 255))
                    tex.set_colorkey((255, 0, 255))
                    pygame.draw.rect(tex, (73, 196, 132), (105, 65, 250, 280))
                for pos in ((), (-880,), (-880, -280),
                            (-900, -300, 300, 900),
                            (-600, -100, 400, 900, 1400)):
                    for altura in (-80, 0, 200, 650):
                        a = pygame.Surface((450, 800), flags)
                        a.fill((29, 68, 97, 152) if flags else (29, 68, 97))
                        b = a.copy()
                        for x in pos:
                            _blit_visivel(a, tex, x, altura)
                        _blits_visiveis(b, tex, pos, altura)
                        self.assertEqual(rgba(a), rgba(b),
                                         (flags, tipo, pos, altura))

    def test_sdf_batch_transparencia_e_scroll(self):
        for flags in (0, pygame.SRCALPHA):
            strip = pygame.Surface((171, 500), pygame.SRCALPHA)
            for y in range(500):
                pygame.draw.line(strip, ((y*2)%256, (y*5)%256, 77, (y*9)%256),
                                 (0,y), (170,y))
            for deslocamento in (0, 1, 77, 171, 900, 25007):
                left = -(deslocamento % strip.get_width())
                xs = list(range(left, 450, strip.get_width()))
                a = pygame.Surface((450,800),flags)
                a.fill((51,31,19,118) if flags else (51,31,19))
                b = a.copy()
                for x in xs:
                    a.blit(strip,(x,0))
                b.blits([(strip,(x,0)) for x in xs],doreturn=False)
                self.assertEqual(rgba(a),rgba(b))
        src = (ROOT / 'pixelrush_world_v3130.py').read_text('utf8')
        arvore = ast.parse(src)
        self.assertIn('layer.blits(operacoes,doreturn=False)',src)
        self.assertIn('self.damage.apply(layer,self.travel*LAYER_SPEEDS[1])',src)
        self.assertTrue(any(isinstance(n,ast.ClassDef) and n.name=='LivingWorld'
                            for n in arvore.body))

    def test_percentis_exatamente_iguais_e_fora_da_thread_principal(self):
        import pixelrush_qa_android_v327728 as qa_module
        with tempfile.TemporaryDirectory() as pasta:
            qa = qa_module.QATelemetria('v3.277.44-QA', 'LIMPA', caminho=pasta)
            chave = 'corrida_normal|cidade'
            qa.agregados[chave]['quadro_total_ms'].extend((10.,12.,100.,50.))
            qa.agregados[chave]['intervalo_entre_inicios_ms'].extend((16.,17.,19.))
            qa.agregados[chave]['camera_smoothscale'].extend((30.,40.,11.))
            qa.quantidades[chave] = 4
            qa.picos[chave]['mais_33ms'] = 2
            qa.ultimos.append({'modo':'corrida_normal','bioma':'cidade',
                'total_ms':50.,'trabalho_ms':43.,'cpu_ms':39.,
                'intervalo_ms':17.,'rss_mb':70.})
            referencia = qa.relatorio()
            chamadores = []
            anterior = qa_module._stats
            def marcado(valores):
                chamadores.append(threading.current_thread().name)
                return anterior(valores)
            qa_module._stats = marcado
            try:
                self.assertTrue(qa.salvar(esperar=False))
                # v743: snapshot periodico nao cria um worker no frame.
                self.assertIsNotNone(qa._qa_snapshot_pendente)
                self.assertIsNone(qa._qa_gravador)
                while qa._qa_snapshot_pendente is not None:
                    pronto=qa._qa_snapshot_pendente.passo()
                    if pronto is not None:
                        qa._qa_snapshot_pendente=None
                        qa._enviar_snapshot_periodico(*pronto)
                qa._qa_gravador.finalizar()
            finally:
                qa_module._stats = anterior
            self.assertTrue(chamadores)
            self.assertTrue(all(nome.startswith('pixelrush-qa-io')
                                for nome in chamadores),chamadores)
            destino = Path(pasta)/'pixelrush_qa_v327744.json'
            documento = json.loads(destino.read_text('utf8'))
            self.assertEqual(documento['grupos'],referencia['grupos'])
            self.assertEqual(documento['grupos'][chave]['quadros_observados'],4)
            with (Path(pasta)/'pixelrush_qa_frames_v327744.csv').open(newline='') as f:
                linhas = list(csv.DictReader(f))
            self.assertEqual(len(linhas),1)
            self.assertEqual(linhas[0]['modo'],'corrida_normal')
            self.assertFalse(list(Path(pasta).glob('*.tmp')))

    def test_inalterado_produto_fisica_e_build_debug(self):
        fonte = (ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        self.assertIn('VERSAO = "v3.277.44-QA-ANDROID-RC"',fonte)
        self.assertIn('MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15',fonte)
        self.assertIn('FPS_RENDER = 30 if E_ANDROID else 60',fonte)
        self.assertIn('PIXELRUSH_DEV_BUILD = False',fonte)
        self.assertNotIn('pixelrush_qa_gles_exact_v327736',fonte)


if __name__=='__main__':
    unittest.main(verbosity=2)
