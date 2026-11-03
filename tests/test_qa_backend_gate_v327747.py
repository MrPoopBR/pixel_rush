# -*- coding: utf-8 -*-
"""QA v3.277.47 — gates de segurança de CPU/GPU sem Android."""
import os,sys,unittest
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from pixelrush_qa_backend_gate_v327747 import CapacidadeVideo,selecionar,diagnostico_display


class BackendGateQA747(unittest.TestCase):
    def test_sdl_surface_permanece_cpu(self):
        d=selecionar()
        self.assertEqual(d['backend'],'cpu_sdl_original')
        self.assertIn('janela_sdl_surface_sem_opengl',d['aprovacao_necessaria'])
        self.assertTrue(d['fallback_preservado'])

    def test_gl_sem_entrada_e_hud_nao_aprovado(self):
        c=CapacidadeVideo(janela_opengl=True,pixels_todos_iguais=True,
          fps_comprovadamente_melhor=True,sem_readback=True,
          dispositivo_real_medido=True)
        d=selecionar(c,laboratorio=True)
        self.assertEqual(d['backend'],'cpu_sdl_original')
        self.assertIn('hud_sem_adapter',d['aprovacao_necessaria'])

    def test_gl_sem_paridade_rgba_nao_aprovado(self):
        c=CapacidadeVideo(janela_opengl=True,input_compatível=True,
          hud_compatível=True,fps_comprovadamente_melhor=True,
          dispositivo_real_medido=True)
        self.assertEqual(selecionar(c,laboratorio=True)['backend'],
                         'cpu_sdl_original')

    def test_gpu_todos_gates_somente_laboratorio(self):
        c=CapacidadeVideo(janela_opengl=True,input_compatível=True,
          hud_compatível=True,pixels_todos_iguais=True,
          fps_comprovadamente_melhor=True,sem_readback=True,
          dispositivo_real_medido=True)
        self.assertEqual(selecionar(c)['backend'],'cpu_sdl_original')
        lab=selecionar(c,laboratorio=True)
        self.assertEqual(lab['backend'],'gles_laboratorio')
        self.assertFalse(lab['pronto_para_trocar_entrada_real'])

    def test_gles_gate_real_nao_muda_pygame_display(self):
        import pygame
        pygame.init()
        display=pygame.display.set_mode((450,800))
        antes=pygame.display.get_surface()
        info=diagnostico_display()
        self.assertIs(pygame.display.get_surface(),antes)
        self.assertEqual(info['arbitragem']['backend'],'cpu_sdl_original')
        self.assertFalse(info['shader_gate_offline_sem_android'])
        pygame.quit()


if __name__=='__main__':
    unittest.main(verbosity=2)
