# -*- coding: utf-8 -*-
"""QA782: tela fullscreen fisica Android, fallback e lib C/NEON real.

O canvas da corrida continua 450x800 e a captura de entrada nao e alterada.
Testes SDL dummy para fluxo, sem alegar que um A54 rodou esta revisao.
"""
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch, call

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame
import pixelrush_qa_android_display_v327782 as display
import pixelrush_qa_camera_native_auto_v327742 as neon

ENGINE=ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py'
SPEC=ROOT/'buildozer.spec'


class DisplayAndroidQA782(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_fullscreen_fisico_sem_mudar_canvas_virtual(self):
        real=pygame.Surface((1080,2340))
        with patch.object(pygame.display,'set_mode',return_value=real) as setter:
            result=display.criar_tela((450,800))
        self.assertIs(result,real)
        setter.assert_called_once_with((0,0),pygame.FULLSCREEN)
        self.assertEqual(display.diagnostico()['janela_px'],(1080,2340))
        self.assertTrue(display.diagnostico()['fullscreen_fisico'])
        self.assertEqual(display.diagnostico()['logico_px'],(450,800))

    def test_fallback_se_driver_recusar_modo_fisico(self):
        logical=pygame.Surface((450,800))
        with patch.object(pygame.display,'set_mode',
                          side_effect=[pygame.error('sem fullscreen'),logical]) as setter:
            result=display.criar_tela((450,800))
        self.assertIs(result,logical)
        self.assertEqual(setter.call_args_list,[
            call((0,0),pygame.FULLSCREEN),call((450,800))])
        self.assertEqual(display.diagnostico()['modo'],'fallback_logico')
        self.assertFalse(display.diagnostico()['fullscreen_fisico'])

    def test_fallback_se_driver_der_tamanho_menor(self):
        pequena=pygame.Surface((400,700))
        logica=pygame.Surface((450,800))
        with patch.object(pygame.display,'set_mode',
                          side_effect=[pequena,logica]):
            result=display.criar_tela((450,800))
        self.assertIs(result,logica)
        self.assertEqual(display.diagnostico()['fallback'],
                         'modo_fisico_menor_que_logico')

    def test_r13_respeita_escala_pygame_original_e_entrada(self):
        engine=ENGINE.read_text('utf8')
        self.assertIn('criar_tela as _qa_criar_tela',engine)
        self.assertIn('tela = _qa_criar_tela((LARGURA_VIRTUAL, ALTURA_VIRTUAL))',
                      engine)
        self.assertIn('LARGURA_VIRTUAL = 450',engine)
        self.assertIn('ALTURA_VIRTUAL = 800',engine)
        self.assertIn('tamanho_final = (LARGURA_TELA, ALTURA_TELA)',engine)
        self.assertIn('(px / largura_atual_tela) * LARGURA_VIRTUAL',engine)
        self.assertIn('(py / altura_atual_tela) * ALTURA_VIRTUAL',engine)
        self.assertIn('VERSAO = "v3.277.82-QA-ANDROID-RC"',engine)
        spec=SPEC.read_text('utf8')
        self.assertIn('version = 3.277.82',spec)
        self.assertIn('android.numeric_version = 327782',spec)
        self.assertIn('android.archs = arm64-v8a',spec)

    def test_relatorio_r12_v2_compativel_com_qa782(self):
        from pixelrush_qa_android_v327728 import QATelemetria
        with patch.dict(os.environ,{'PIXELRUSH_QA_ANDROID':'1'}):
            with patch('pixelrush_qa_android_v327728._renderer_backend_qa',
                       return_value={'sdl_video':'dummy','smoothscale':'SSE2'}):
                t=QATelemetria('v3.277.82-QA-ANDROID-RC','LIMPA')
                self.assertTrue(t.r12)
                self.assertEqual(t.prefixo,'pixelrush_qa_v327781_r12')
                d=t.relatorio()
                self.assertEqual(d['r12_revision'],'v327782_camera_tela_cheia')
                self.assertIn('tela_cheia_fisica',
                              d['r12_runtime']['execucao_observada'])
                self.assertFalse(d['r12_hardware_homologado_a54'])

    def test_gles_que_falhou_r12_desligado_somente_com_override(self):
        from pixelrush_qa_render_v327729 import preparar_perfil_qa_android
        with patch.dict(os.environ,{
            'PIXELRUSH_QA_ANDROID':'1','ANDROID_ARGUMENT':'fake',
            'PIXELRUSH_QA_ACCEL_PROFILE':'agressivo'
        },clear=True):
            self.assertTrue(preparar_perfil_qa_android())
            self.assertEqual(os.environ['PIXELRUSH_QA_GLES_BRIDGE'],'0')
            self.assertEqual(os.environ['PIXELRUSH_QA_NATIVE_AUTO'],'1')
            self.assertEqual(os.environ['PIXELRUSH_QA_CITY_INCREMENTAL'],'1')
        with patch.dict(os.environ,{
            'PIXELRUSH_QA_ANDROID':'1','ANDROID_ARGUMENT':'fake',
            'PIXELRUSH_QA_GLES_BRIDGE':'1'
        },clear=True):
            self.assertTrue(preparar_perfil_qa_android())
            self.assertEqual(os.environ['PIXELRUSH_QA_GLES_BRIDGE'],'1')


class NativeAndroidQA782(unittest.TestCase):
    def test_tenta_soname_e_native_library_dir_sem_path_pessoal(self):
        soname='libpixelrush_camera_crop_v327741.so'
        antiga=neon._NATIVE
        class FakeCrop:
            def __init__(self,path):
                if path==soname:
                    raise RuntimeError('lib not visible')
                self.path=path
        class FakeActivity:
            def getApplicationInfo(self):
                return types.SimpleNamespace(nativeLibraryDir='/tmp/lib/app')
        jnius=types.SimpleNamespace(autoclass=lambda _:types.SimpleNamespace(mActivity=FakeActivity()))
        try:
            neon._NATIVE=None
            with patch.dict(sys.modules,{
                    'pixelrush_qa_crop_native_v327741':types.SimpleNamespace(Crop32QA=FakeCrop),
                    'jnius':jnius}),patch.dict(os.environ,{
                    'ANDROID_ARGUMENT':'fake'},clear=True):
                loaded=neon._load_native()
            self.assertEqual(loaded.path,'/tmp/lib/app/'+soname)
            self.assertEqual(neon.diagnostico()['load_attempts'],2)
            self.assertEqual(neon.diagnostico()['native_lib_resolvida'],'app_native_lib')
        finally:
            neon._NATIVE=antiga

    def test_preflight_boot_inicial_zoom_zero_restaura_estado(self):
        # R12: zoom=0 no boot, primeira aplicacao com velocidade 12
        # ficava abaixo de 0.002, pulava a prova e nunca ligava C/NEON.
        image=pygame.Surface((90,160)).convert()
        for y in range(160):
            pygame.draw.line(image,(y*17%256,y*23%256,y*37%256),
                             (0,y),(89,y))
        player=types.SimpleNamespace(
            no_chao=True,rect=pygame.Rect(45,100,16,24))
        camera=types.SimpleNamespace(zoom=0.0,foco_y=0.0)
        class NativeFake:
            def suportado(self,s):
                return True
            def processar(self,source,size,crop,backend=None):
                w,h=source.get_size()
                return pygame.transform.smoothscale(source,size).subsurface(
                    (crop[0],crop[1],w,h))
        neon._REPORT.update(teste_real=False,pixels_exatos=None)
        with patch.object(neon,'_load_native',return_value=NativeFake()):
            neon._verificar_primeiro_frame(
                image,camera,player,velocidade=12,momento=False,ativo=True)
        self.assertTrue(neon.diagnostico()['teste_real'])
        self.assertTrue(neon.diagnostico()['pixels_exatos'])
        self.assertGreater(neon.diagnostico()['boot_passos_geometria'],1)
        self.assertTrue(neon.diagnostico()['boot_zoom_estado_preservado'])
        self.assertEqual((camera.zoom,camera.foco_y),(0.0,0.0))

    def test_falha_boot_nativa_nao_impede_fallback(self):
        neon.registrar_falha_boot('ImportError')
        self.assertEqual(neon.diagnostico()['status'],
                         'erro_preflight_boot_ImportError')

    def test_gates_camera_nativa_continuam_exigindo_pixel_rgba_e_ganho(self):
        codigo=(ROOT/'pixelrush_qa_camera_native_auto_v327742.py').read_text('utf8')
        self.assertIn("_REPORT['pixels_exatos']",codigo)
        self.assertIn('if b<.85*a and (a-b)>=.10:',codigo)
        self.assertIn("if not _REPORT['selecionado']",codigo)
        self.assertIn('registrar_falha_boot',codigo)


if __name__ == '__main__':
    unittest.main(verbosity=2)
