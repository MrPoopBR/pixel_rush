# -*- coding: utf-8 -*-
"""PIXEL RUSH QA v3.277.37: equivalencia RGBA, caches, I/O e gates.

Nao inicia o jogo, nao altera saves e nao importa o shader experimental.
"""
import ast
import csv
from functools import lru_cache
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame


def pix(surface):
    return pygame.image.tobytes(surface,'RGBA')


class TestPerformanceFullQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_batch_panorama_rgb_rgba(self):
        from pixelrush_cenarios_v398 import desenhar_panorama, PANORAMA_Y
        for flags in (0,pygame.SRCALPHA):
            for largura in (175,450,700):
                panorama=pygame.Surface((largura,175),pygame.SRCALPHA)
                for y in range(175):
                    pygame.draw.line(panorama,((y*11)%256,(y*7)%256,(y*17)%256,(y*23)%256),(0,y),(largura-1,y))
                for scroll in (-2100,-451,-1,0,1,181,640,2711):
                    esperado=pygame.Surface((450,800),flags)
                    recebido=esperado.copy()
                    esperado.fill((31,54,91,172) if flags else (31,54,91))
                    recebido.blit(esperado,(0,0))
                    comprimento=panorama.get_width()
                    offset=int(scroll)%comprimento
                    p=0
                    while p<450:
                        n=min(450-p,comprimento-offset)
                        esperado.blit(panorama,(p,PANORAMA_Y),(offset,0,n,panorama.get_height()))
                        p+=n
                        offset=0
                    desenhar_panorama(recebido,panorama,scroll)
                    self.assertEqual(pix(esperado),pix(recebido),
                                     f'panorama {flags} {largura} {scroll}')

    def test_strip_e_halos(self):
        import pixelrush_world_v3130 as world
        stub=world.LivingWorld.__new__(world.LivingWorld)
        strip=pygame.Surface((174,210),pygame.SRCALPHA)
        for y in range(210):
            pygame.draw.line(strip,(y*3%256,y*7%256,y*5%256,y*11%256),
                             (0,y),(173,y))
        for flags in (0,pygame.SRCALPHA):
            for deslocamento in (0,1,72,200,456,781,9999):
                stub.travel=float(deslocamento)
                a=pygame.Surface((450,800),flags)
                b=a.copy()
                a.fill((18,47,83,131) if flags else (18,47,83))
                b.blit(a,(0,0))
                off=stub._scroll()%strip.get_width()
                x=-off
                while x<world.WIDTH:
                    a.blit(strip,(x,world.TOP))
                    x+=strip.get_width()
                stub._blit_strip(b,strip)
                self.assertEqual(pix(a),pix(b))
        for night in (0.,.05,.14,.25,.5,.72,.95,1.):
            cor=(113,197,244)
            alfas=tuple(max(0,int((20-r)*.55*(.35+night))) for r in (19,15,10,6))
            a=pygame.Surface((42,42),pygame.SRCALPHA)
            for raio,alpha in zip((19,15,10,6),alfas):
                pygame.draw.circle(a,(*cor,alpha),(21,21),raio)
            b=world._qa_halo_pixel_exato(cor,alfas)
            self.assertEqual(pix(a),pix(b))
            self.assertIs(b,world._qa_halo_pixel_exato(cor,alfas))
        self.assertEqual(world._qa_halo_pixel_exato.cache_info().maxsize,96)

    def test_alfa_temporario_rgb_rgba(self):
        src=pygame.Surface((110,80),pygame.SRCALPHA)
        for y in range(80):
            pygame.draw.line(src,(y*3%256,y*5%256,90,y*11%256),
                             (0,y),(109,y))
        for flags in (0,pygame.SRCALPHA):
            for alpha in (0,1,7,55,127,200,255):
                out1=pygame.Surface((450,800),flags)
                out1.fill((51,79,112,155) if flags else (51,79,112))
                out2=out1.copy()
                baseline=src.copy()
                baseline.set_alpha(alpha)
                out1.blit(baseline,(41,138))
                before=src.get_alpha()
                src.set_alpha(alpha)
                try:
                    out2.blit(src,(41,138))
                finally:
                    src.set_alpha(before)
                self.assertEqual(pix(out1),pix(out2))
                self.assertEqual(src.get_alpha(),before)

    def test_foreground_cache(self):
        import pixelrush_world_v3130 as world
        source=world._source
        imagem=pygame.Surface((900,510),pygame.SRCALPHA)
        for y in range(510):
            pygame.draw.line(imagem,(y*3%256,y*7%256,190,y*9%256),
                             (0,y),(899,y))
        world._source=lambda biome: imagem
        try:
            stub=world.LivingWorld.__new__(world.LivingWorld)
            stub.biome='vulcao'
            stub.lightweight=False
            for frame in (0,1,13,41,201):
                stub.frame=frame
                esperado=pygame.Surface((450,800)).convert()
                esperado.fill((33,67,89))
                saida=esperado.copy()
                for rect,x in (((0,310,124,188),-30),
                               ((776,310,124,188),world.WIDTH-16)):
                    tex=pygame.transform.smoothscale(imagem.subsurface(rect),(45,136))
                    tex.set_alpha(50)
                    esperado.blit(tex,(x+int(__import__('math').sin(frame*.035)*2),
                                       world.GROUND-145))
                stub.draw_foreground(saida)
                self.assertEqual(pix(esperado),pix(saida),str(frame))
            cache=stub._qa_foreground_cache
            self.assertEqual(len(cache),1)
            self.assertEqual(len(cache['vulcao']),2)
        finally:
            world._source=source

    def test_preview_skin_ja_escalada_em_cache(self):
        source=(ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        tree=ast.parse(source)
        func=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and
                  n.name=='_sprite_skin_enquadrado')
        sprites=[]
        for i in range(8):
            s=pygame.Surface((80,80),pygame.SRCALPHA)
            pygame.draw.circle(s,(i*23%256,130,220,120+i*15),(40,40),25)
            sprites.append(s)
        namespace={'pygame':pygame,'_qa_lru_skins_enquadradas':lru_cache,
                   '_quadros_skin':lambda name:{'OCIOSO':sprites}}
        exec(compile(ast.Module(body=[func],type_ignores=[]),
                     str(ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py'),
                     'exec'),namespace)
        cached=namespace['_sprite_skin_enquadrado']
        for frame in range(8):
            a=cached('AZUL','OCIOSO',frame,70,82,4)
            b=cached('AZUL','OCIOSO',frame,70,82,4)
            self.assertIs(a,b)
            self.assertEqual(pix(a),pix(b))
        self.assertEqual(cached.cache_info().maxsize,96)
        self.assertGreaterEqual(cached.cache_info().hits,8)

    def test_exportacao_json_csv_assincrona(self):
        from pixelrush_qa_async_export_v327737 import GravadorQA
        with tempfile.TemporaryDirectory() as td:
            writer=GravadorQA()
            try:
                for indice in range(3):
                    doc={'schema':'pixelrush.qa.android.v1',
                         'versao':'v3.277.37','indice':indice}
                    row={'modo':'corrida_normal','bioma':'cidade','total_ms':12.,
                         'trabalho_ms':11.,'cpu_ms':9.,'intervalo_ms':16.7,
                         'rss_mb':48.5}
                    self.assertTrue(writer.enviar(
                        td,'pixelrush_qa_v327743',doc,(row,),esperar=True))
                final=json.loads((Path(td)/'pixelrush_qa_v327743.json').read_text('utf8'))
                self.assertEqual(final['indice'],2)
                with (Path(td)/'pixelrush_qa_frames_v327743.csv').open(newline='') as f:
                    linhas=list(csv.DictReader(f))
                self.assertEqual(len(linhas),1)
                self.assertEqual(linhas[0]['modo'],'corrida_normal')
                self.assertEqual(writer.concluidas,3)
                self.assertEqual(writer.falhas,0)
                self.assertFalse(list(Path(td).glob('*.tmp')))
            finally:
                writer.finalizar()

    def test_telemetria_flush_e_nomes(self):
        from pixelrush_qa_android_v327728 import QATelemetria
        with tempfile.TemporaryDirectory() as td:
            qa=QATelemetria('v3.277.43-QA','LIMPA',caminho=td)
            qa.iniciar('JOGANDO','cidade')
            qa.marcar('renderizacao_e_ui')
            qa.fim()
            self.assertTrue(qa.salvar())
            destino=Path(td)/'pixelrush_qa_v327743.json'
            self.assertTrue(destino.exists())
            doc=json.loads(destino.read_text('utf8'))
            self.assertEqual(doc['versao'],'v3.277.43-QA')
            self.assertEqual(doc['quadros_observados'],1)
            self.assertIn('apresentacao_swap',__import__('pixelrush_qa_android_v327728').SECOES)
            qa._qa_gravador.finalizar()

    def test_versao_preservacao_fisica_e_gpu(self):
        src=(ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        self.assertIn('VERSAO = "v3.277.43-QA-ANDROID-RC"',src)
        for invariavel in ('MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15',
                           'FPS_RENDER = 30 if E_ANDROID else 60',
                           'PIXELRUSH_DEV_BUILD = False'):
            self.assertIn(invariavel,src)
        self.assertNotIn('pixelrush_qa_gles_exact_v327736', (ROOT/'main.py').read_text('utf8'))
        self.assertNotIn('pixelrush_qa_gles_exact_v327736', src)
        self.assertIn('_pro_sub_inicio("apresentacao_swap")',src)


if __name__=='__main__':
    unittest.main(verbosity=2)
