# -*- coding: utf-8 -*-
"""QA v3.277.41: shaders GLES2/3 vs frames reais cidade/neve.

GPU readback APENAS em ambiente de teste GL. Nada no APK ou jogo usa GL
experimental. O renderer de Linux Mesa NAO comprova driver do Android.
"""
import ctypes as C
import json
import os
import sys
import unittest
from pathlib import Path
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame
import pixelrush_qa_gles_present_v327735 as gl_original
from pixelrush_qa_gles_exact_v327736 import shaders,gate_integracao
from tests.test_qa_gles_exact_v327736 import framebuffer_rgba8,original,highp_mantissa
REPORT=Path('qa-gles-real-scenes-v327741.json')


def cenas_reais():
    from pixelrush_city2_v3124 import CityPilotScene
    from pixelrush_biomes2_v3185 import ModularBiomeScene
    conjunto={}
    for nome,cena in (
        ('cidade',CityPilotScene()),
        ('neve',ModularBiomeScene('neve',lightweight=True)),
    ):
        for noite,clima in ((0.0,'limpo'),(.72,'chuva')):
            vista=pygame.Surface((450,500),pygame.SRCALPHA)
            cena.render_scene(vista,118.5,83,noite,clima,.33)
            for alpha in (False,True):
                src=pygame.Surface((450,800),pygame.SRCALPHA if alpha else 0)
                src.fill((22,44,90,57) if alpha else (22,44,90))
                src.blit(vista,(0,230))
                pygame.draw.rect(src,(211,164,81,180) if alpha else
                                 (211,164,81),(30,75,210,34))
                conjunto[f'{nome}-{clima}-{int(alpha)}']=src
    return conjunto


class TestGLESRealQA(unittest.TestCase):
    def test_camera_gles2_3_cena_real_pixelexata(self):
        pygame.init()
        pygame.display.set_mode((450,800))
        original_backend=pygame.transform.get_smoothscale_backend()
        fontes=cenas_reais()
        reports=[]
        total=0
        try:
            for api in ('GLES2','GLES3'):
                for backend in ('GENERIC','SSE2'):
                    try: pygame.transform.set_smoothscale_backend(backend)
                    except (ValueError,pygame.error):continue
                    gl_original.VERT,gl_original.FRAG=shaders(api,backend,(450,800))
                    presenter=gl_original.GLES2DirectPresenterQA(450,800)
                    try:
                        precision=highp_mantissa(presenter)
                        if api=='GLES2' and precision!=-1 and precision<23:
                            self.fail('GLES2 highp insuficiente para paridade')
                        f,read=framebuffer_rgba8(presenter)
                        casos=0
                        for nome,source in fontes.items():
                            for zoom in (.005,.025,.034):
                                for foco in (-9,0,9):
                                    esperado=original(source,zoom,foco)
                                    presenter.draw(source,zoom,foco)
                                    buf=C.create_string_buffer(450*800*4)
                                    read(0,0,450,800,0x1908,0x1401,buf)
                                    reference=pygame.image.tobytes(esperado,'RGBA',True)
                                    if buf.raw!=reference:
                                        diferencas=sum(a!=b for a,b in zip(buf.raw,reference))
                                        self.fail(f'GLES frame divergente: {api}/{backend}/{nome}/{zoom}/{foco}: {diferencas} canais')
                                    casos+=1
                        total+=casos
                        self.assertEqual(presenter.readbacks,0)
                        reports.append({'api':api,'backend':backend,'casos':casos,
                            'renderer_mesa':presenter.renderer,
                            'versao_gl':presenter.version,'pixels_exatos':True,
                            'gpu_android_real':False})
                    finally:
                        presenter.close()
        finally:
            pygame.transform.set_smoothscale_backend(original_backend)
            pygame.quit()
        resultado={'schema':'pixelrush.qa.gles.real.v327741',
             'casos':total,'fontes_reais':len(fontes),
             'resultados':reports,'android_medido':False,
             'gles_integrado_jogo':False,
             'autorizacao_android':gate_integracao({'igualdade_total':True},False)}
        REPORT.write_text(json.dumps(resultado,indent=2,ensure_ascii=False),encoding='utf8')
        self.assertGreaterEqual(total,144)
        self.assertFalse(resultado['autorizacao_android'])


if __name__=='__main__':
    unittest.main(verbosity=2)
