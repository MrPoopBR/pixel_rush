# -*- coding: utf-8 -*-
"""QA774: player pet real em modo placeholder e agenda QA menu sem RNG."""
import ast
import os
import random
import unittest
from pathlib import Path

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import pygame
from pixelrush_qa_pet_preload_v327769 import (
    preparar_pet_compativel, TAMANHOS_PET_COMPAT)

ENGINE = Path(__file__).resolve().parents[1] / 'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py'


def studio_placeholder_real():
    # Extrai a DEFINICAO real, sem iniciar a corrida do executavel.
    arvore = ast.parse(ENGINE.read_text(encoding='utf8'))
    clazz = next(n for n in arvore.body
                 if isinstance(n, ast.ClassDef) and n.name == 'PetStudioPlayer')
    namespace = {'pygame': pygame}
    codigo = compile(ast.fix_missing_locations(ast.Module(body=[clazz],type_ignores=[])),
                     str(ENGINE), 'exec')
    exec(codigo, namespace)
    return namespace['PetStudioPlayer'](None, budget_bytes=16*1024*1024,
                                         strict=False)


class PetPreload769(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450, 800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_studio_real_reusa_surfaces_e_rgba_transparente(self):
        studio = studio_placeholder_real()
        chamadas = []
        def original(pet_id):
            chamadas.append(pet_id)
            return studio.preload(pet_id, airborne=False)
        antes = random.getstate()
        self.assertTrue(preparar_pet_compativel('FANTASMA', original,
                                               studio.frames))
        self.assertEqual(chamadas, ['FANTASMA'])
        self.assertEqual(random.getstate(), antes)
        self.assertEqual(set(studio._transparentes), set(TAMANHOS_PET_COMPAT))
        for tamanho in TAMANHOS_PET_COMPAT:
            quadro = studio.frames('FANTASMA', 'ESPERA', tamanho)[0]
            self.assertIs(quadro, studio.frames('DRAGAO', 'FESTA', tamanho)[0])
            self.assertEqual(pygame.image.tobytes(quadro, 'RGBA'),
                             b'\0' * (tamanho[0] * tamanho[1] * 4))

    def test_preloader_nao_trabalha_na_corrida_e_nao_muda_rng(self):
        from pixelrush_qa_precarregamento_visual_v327757 import PrecargaVisuaisQA
        studio = studio_placeholder_real()
        nomes = []
        def skin(item):
            nomes.append(item)
        def pet(item):
            return preparar_pet_compativel(item,studio.preload,studio.frames)
        queue = PrecargaVisuaisQA('VERDE', {'AZUL','ROSA','VERDE'},
                                 'FANTASMA', skin, pet, aquecer_tiles=False)
        rng = random.getstate()
        for _ in range(60):
            self.assertFalse(queue.passo('JOGANDO'))
        self.assertEqual(len(studio._transparentes), 0)
        self.assertEqual(queue.diagnostico()['tarefas_pendentes'],4)
        for _ in range(40):
            queue.passo('INICIO')
        self.assertEqual(nomes, ['VERDE', 'AZUL', 'ROSA'])
        self.assertEqual(queue.diagnostico()['pets_preparados'],1)
        self.assertEqual(set(studio._transparentes),set(TAMANHOS_PET_COMPAT))
        self.assertEqual(random.getstate(),rng)

    def test_integracao_somente_no_qa(self):
        texto=ENGINE.read_text(encoding='utf8')
        self.assertIn('VERSAO = "v3.277.89-QA-ANDROID-RC"',texto)
        self.assertIn('preparar_pet_compativel(',texto)
        self.assertIn("dados.get('pet_equipado')",texto)
        self.assertIn('PIXELRUSH_QA_PRELOAD_VISUAL',texto)
        self.assertIn("if _qa_precarga_visuais is not None and estado in ('INICIO','LOJA','CONFIG','UPGRADES')",texto)


if __name__=='__main__':
    unittest.main(verbosity=2)
