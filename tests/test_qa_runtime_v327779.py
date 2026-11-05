# -*- coding: utf-8 -*-
"""QA779: perfil Android QA, GC/trim e fallback do backend nativo.

Uso offline: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
python tests/test_qa_runtime_v327780.py
"""
import ast
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame


class RuntimeQA779(unittest.TestCase):
    def test_sintaxe_modulos_e_versao(self):
        arquivos=('pixelrush_qa_gc_cooperativo_v327757.py',
                 'pixelrush_qa_performance_integrated_v327742.py',
                 'pixelrush_qa_gles_present_v327735.py',
                 'pixelrush_qa_render_v327729.py',
                 'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py')
        for path in arquivos:
            with self.subTest(path=path):
                p=ROOT/path
                ast.parse(p.read_text('utf8'),filename=str(p))
        jogo=(ROOT/arquivos[-1]).read_text('utf8')
        self.assertIn('VERSAO = "v3.277.84-QA-ANDROID-RC"',jogo)
        self.assertIn('preparar_fora_do_frame as _qa_camera_native_boot',jogo)
        self.assertIn("PIXELRUSH_QA_NATIVE_AUTO",jogo)

    def test_perfil_nao_atinge_prod_dev_ou_desktop(self):
        from pixelrush_qa_render_v327729 import preparar_perfil_qa_android
        with patch.dict(os.environ,{'PIXELRUSH_QA_ANDROID':'0','ANDROID_ARGUMENT':'fake'},clear=True):
            self.assertFalse(preparar_perfil_qa_android())
            self.assertNotIn('PIXELRUSH_QA_GLES_BRIDGE',os.environ)
        with patch.dict(os.environ,{'PIXELRUSH_QA_ANDROID':'1',
                       'PIXELRUSH_QA_ACCEL_PROFILE':'estavel',
                       'ANDROID_ARGUMENT':'fake'},clear=True):
            self.assertFalse(preparar_perfil_qa_android())
            self.assertNotIn('PIXELRUSH_QA_GLES_BRIDGE',os.environ)

    def test_perfil_acelera_com_rollback_individual(self):
        from pixelrush_qa_render_v327729 import preparar_perfil_qa_android
        with patch.dict(os.environ,{'PIXELRUSH_QA_ANDROID':'1',
                'ANDROID_ARGUMENT':'fake','PIXELRUSH_QA_GLES_BRIDGE':'0'},clear=True):
            self.assertTrue(preparar_perfil_qa_android())
            self.assertEqual(os.environ['PIXELRUSH_QA_GLES_BRIDGE'],'0')
            for flag in ('PIXELRUSH_QA_GPU_ZOOM','PIXELRUSH_QA_GLES3_CONTEXT',
                         'PIXELRUSH_QA_GLES_PBO','PIXELRUSH_QA_CAMERA_AUTOTUNE',
                         'PIXELRUSH_QA_NATIVE_AUTO','PIXELRUSH_QA_CITY_INCREMENTAL',
                         'PIXELRUSH_QA_CLASSIC_INCREMENTAL','PIXELRUSH_QA_TRACE'):
                self.assertEqual(os.environ[flag],'1',flag)

    def test_gles_ctypes_alias_sem_nameerror(self):
        texto=(ROOT/'pixelrush_qa_gles_present_v327735.py').read_text('utf8')
        self.assertIn('import ctypes as C',texto)
        self.assertIn('import ctypes.util',texto)
        self.assertIn("C.util.find_library('GLESv2')",texto)
        self.assertIn("C.util.find_library('EGL')",texto)
        self.assertNotIn("ctypes.util.find_library(",texto)

    def test_gc_coleta_em_fase_fora_5_8(self):
        import pixelrush_qa_gc_cooperativo_v327757 as qa
        antes=pygame.display.flip
        ligado=qa.gc.isenabled()
        pygame.init()
        pygame.display.set_mode((450,800))
        with patch.dict(os.environ,{'PIXELRUSH_QA_ANDROID':'1',
                         'PIXELRUSH_QA_GC_COOPERATIVO':'1'}):
            if not qa.gc.isenabled():qa.gc.enable()
            qa.instalar()
            try:
                frames=[]
                with patch.object(qa.gc,'collect',side_effect=lambda n:frames.append((qa._FRAMES,n))):
                    for _ in range(902):pygame.display.flip()
                self.assertEqual(len(frames),30)
                self.assertEqual([n for _,n in frames].count(2),1)
                self.assertEqual([n for _,n in frames].count(1),4)
                self.assertTrue(all(f%5!=1 and f%8!=1 for f,_ in frames))
            finally:
                qa.restaurar_para_teste()
                if not ligado:qa.gc.disable()
        self.assertIs(pygame.display.flip,antes)

    def test_trim_apenas_fora_redraws(self):
        import pixelrush_qa_performance_integrated_v327742 as perf
        pygame.init()
        pygame.display.set_mode((450,800))
        class TrimFake:
            ativo=True
            removidos=0
            def __init__(self):self.amostras=[]
            def passo(self):
                self.amostras.append(perf._LAST_STATUS['frames'])
                return True
        t=TrimFake()
        original_flip=pygame.display.flip
        original_trim=perf._TRIMMER
        n=perf._LAST_STATUS['frames']
        try:
            perf._TRIMMER=t
            perf._LAST_STATUS['frames']=0
            perf._wrap_flip()
            for _ in range(55):pygame.display.flip()
            self.assertTrue(t.amostras)
            self.assertTrue(all(k%5!=1 and k%8!=1 for k in t.amostras))
            self.assertNotIn(1,t.amostras)
            self.assertNotIn(9,t.amostras)
        finally:
            pygame.display.flip=original_flip
            perf._TRIMMER=original_trim
            perf._LAST_STATUS['frames']=n
        texto=(ROOT/'pixelrush_qa_performance_integrated_v327742.py').read_text('utf8')
        self.assertIn("PIXELRUSH_QA_TRIM_PROBE_PHASE','2'",texto)

    def test_pacing_e_jank_gles_sem_gpu_fisica(self):
        from collections import deque
        from pixelrush_qa_gles_present_v327735 import GLES2DirectPresenterQA
        import pixelrush_qa_gles_present_v327735 as gles
        pygame.init()
        pygame.display.set_mode((450,800))
        presenter=GLES2DirectPresenterQA.__new__(GLES2DirectPresenterQA)
        presenter._egl=None
        presenter.frame_count=0
        presenter.frame_intervals_ns=deque(maxlen=256)
        presenter._last_present_ns=None
        presenter.swap_method='SDL mock'
        presenter.swap_interval_aplicado=None
        presenter.renderer='GLES fake'
        presenter.version='OpenGL ES3 mock'
        presenter.readbacks=0
        ticks=iter([0,10_000_000,40_000_000,70_000_000,
                    100_000_000,170_000_000])
        with patch.object(pygame.display,'flip',return_value=None), \
             patch.object(gles.time,'perf_counter_ns',side_effect=lambda:next(ticks)):
            presenter.present()
            presenter.present()
            presenter.present()
        resultado=presenter.diagnostico()
        self.assertEqual(resultado['frames'],3)
        self.assertEqual(resultado['frame_interval_p95_ms'],100.0)
        self.assertEqual(resultado['quadros_intervalo_acima_50ms'],2)
        self.assertEqual(resultado['gpu_to_cpu_readbacks'],0)




if __name__=='__main__':
    unittest.main(verbosity=2)
