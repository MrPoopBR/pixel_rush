import os,unittest
from pathlib import Path
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
import pixelrush_qa_camera_v327733 as qa
BASE=Path(__file__).resolve().parents[1]
class Camera771(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):pygame.quit()
    def test_sem_flag_backend_original(self):
        s=pygame.Surface((41,67)).convert();s.fill((21,37,81))
        orig=pygame.transform.get_smoothscale_backend()
        with patch.dict(os.environ,{'PIXELRUSH_QA_CAMERA_AUTOTUNE':'0'}):
            self.assertEqual(qa.preparar_fora_do_frame(s,(45,73)),orig)
        self.assertEqual(pygame.transform.get_smoothscale_backend(),orig)
    def test_backend_restaurado_apos_comparacao_de_pixels(self):
        s=pygame.Surface((45,63)).convert()
        for i in range(45):
            pygame.draw.line(s,((13*i)%256,(19*i)%256,(7*i)%256),(i,0),(i,62))
        orig=pygame.transform.get_smoothscale_backend()
        with patch.dict(os.environ,{'PIXELRUSH_QA_CAMERA_AUTOTUNE':'1'}):
            x=qa.preparar_fora_do_frame(s,(49,69))
        self.assertIn(x,('SSE2','NEON','GENERIC'))
        self.assertEqual(pygame.transform.get_smoothscale_backend(),orig)
        self.assertTrue(qa.resultado()['avaliado'])
    def test_stress_rgba_opaco_e_oculto_instalado(self):
        codigo=(BASE/'pixelrush_qa_camera_v327733.py').read_text('utf8')
        self.assertIn("for alpha in (False,True):",codigo)
        self.assertIn("diferenca_rgba_estresse",codigo)
        self.assertIn("pygame.image.tobytes",codigo)
    def test_preflight_qa_antes_loop_e_preserva_camera_real(self):
        s=(BASE/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        i=s.index('_qa_camera_boot_bench(display_surface')
        j=s.index('    rodando = True\n    while rodando:',i)
        self.assertLess(i,j)
        self.assertIn('PIXELRUSH_QA_ANDROID',s[i-510:i])
        self.assertIn('v3.277.83-QA-ANDROID-RC',s)
        original=(BASE/'pixelrush_cinema_v3172.py').read_text('utf8')
        self.assertIn('pygame.transform.smoothscale(imagem,tamanho,self._cache_zoom_expandido)',original)
if __name__=='__main__':unittest.main(verbosity=2)
