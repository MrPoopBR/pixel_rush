# -*- coding: utf-8 -*-
"""PIXEL RUSH QA 3.277.43: gates sem Android para correcoes A-D."""
import json
import os
import sys
import tempfile
import unittest
from collections import OrderedDict, deque, defaultdict
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pygame


def pixels(imagem):
    return pygame.image.tobytes(imagem, 'RGBA')


class SafePerf743(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450, 800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_camera_nativa_e_simd_sem_benchmark_no_frame(self):
        from pixelrush_cinema_v3172 import CameraCinematica
        import pixelrush_qa_camera_native_auto_v327742 as native
        import pixelrush_qa_camera_v327733 as simd
        native.restaurar_para_teste()
        simd.restaurar_para_teste()
        original = CameraCinematica.aplicar
        old_native = native._verificar_primeiro_frame
        old_simd = simd._teste_real
        native._verificar_primeiro_frame = lambda *a, **kw: self.fail('benchmark native no frame')
        simd._teste_real = lambda *a, **kw: self.fail('benchmark SIMD no frame')
        before = CameraCinematica()
        after = CameraCinematica()
        source = pygame.Surface((450, 800), pygame.SRCALPHA)
        for y in range(800):
            pygame.draw.line(source, (y % 256, (y*3) % 256, (y*7) % 256, 255),
                             (0, y), (449, y))
        try:
            simd.instalar()
            native.instalar()
            for i in range(25):
                player = SimpleNamespace(rect=pygame.Rect(160, 410 + (i*7)%170, 32, 64),
                                         no_chao=(i%4==0))
                args = (source, player, 9.5+i*.2, i%7==0, True)
                esperado = original(before, *args)
                obtido = after.aplicar(*args)
                self.assertEqual(pixels(esperado), pixels(obtido), ('camera',i))
                self.assertEqual((before.zoom, before.foco_y),
                                 (after.zoom, after.foco_y))
            self.assertEqual(native.diagnostico()['frames_native'], 0)
        finally:
            native.restaurar_para_teste()
            simd.restaurar_para_teste()
            native._verificar_primeiro_frame = old_native
            simd._teste_real = old_simd
        self.assertIs(CameraCinematica.aplicar, original)

    def test_scroll_nao_chama_benchmark_mesmo_com_optin(self):
        from pixelrush_world_v3130 import LivingWorld
        import pixelrush_qa_scroll_auto_v327742 as scroll
        scroll.restaurar_para_teste()
        antigo = LivingWorld._blit_strip
        benchmark = scroll._bench
        old_env = os.environ.get('PIXELRUSH_QA_SCROLL_AUTO')
        strip = pygame.Surface((900, 500), pygame.SRCALPHA)
        strip.fill((27, 93, 141, 201))
        world = LivingWorld.__new__(LivingWorld)
        world.travel = 100
        try:
            os.environ['PIXELRUSH_QA_SCROLL_AUTO'] = '1'
            scroll._bench = lambda *_args: self.fail('benchmark scroll no frame')
            scroll.instalar()
            for offset in (0, 1, 48, 400, 2200):
                world.travel = offset
                a = pygame.Surface((450, 800), pygame.SRCALPHA)
                a.fill((11, 23, 31, 75))
                b = a.copy()
                antigo(world, a, strip)
                world._blit_strip(b, strip)
                self.assertEqual(pixels(a), pixels(b), offset)
            self.assertFalse(scroll.status()['ativo'])
        finally:
            scroll.restaurar_para_teste()
            scroll._bench = benchmark
            if old_env is None:
                os.environ.pop('PIXELRUSH_QA_SCROLL_AUTO', None)
            else:
                os.environ['PIXELRUSH_QA_SCROLL_AUTO'] = old_env

    def test_cache_global_protege_todos_biomas_vivos(self):
        import pixelrush_qa_performance_integrated_v327742 as perf
        from pixelrush_world_v3130 import _SOURCE
        class FakeWorld:
            def __init__(self, biome):
                self.biome = biome
                self.props_cache = {(biome,0):'live',('deserto',1):'cold'}
                self.cache = OrderedDict([(biome,'live'),('deserto','cold')])
                self.fx_cache = OrderedDict()
                self.normal_cache = OrderedDict()
                self.material_cache = OrderedDict()
                self.flow_cache = OrderedDict()
                self.geometry_cache = OrderedDict()
                self._city_surfaces = {}
                self.city2 = None
        city = FakeWorld('cidade')
        snow = FakeWorld('neve')
        old_src = dict(_SOURCE)
        old_func = perf._memory_mib
        old_status = dict(perf._LAST_STATUS)
        try:
            _SOURCE.clear()
            _SOURCE.update({'cidade':'city', 'neve':'snow', 'deserto':'cold'})
            perf._WORLDS.add(city)
            perf._WORLDS.add(snow)
            perf._memory_mib = lambda: 900.
            perf._LAST_STATUS['cache_budget_mib'] = 560
            perf._reclaim_inactive_caches()
            self.assertEqual(_SOURCE, {'cidade':'city','neve':'snow'})
            self.assertEqual(city.props_cache, {('cidade',0):'live'})
            self.assertEqual(snow.props_cache, {('neve',0):'live'})
        finally:
            _SOURCE.clear()
            _SOURCE.update(old_src)
            perf._WORLDS.discard(city)
            perf._WORLDS.discard(snow)
            perf._memory_mib = old_func
            perf._LAST_STATUS.clear()
            perf._LAST_STATUS.update(old_status)

    def test_nuvens_opcao_off_e_on_pixels_identicos(self):
        from pixelrush_city2_v3118 import CityPilotScene
        scene = CityPilotScene()
        self.assertFalse(scene._qa_cloud_use_cache)
        for flags in (0, pygame.SRCALPHA):
            for night in (0., .54, .55, .9):
                for travel in (-500., 0., 101., 10000.):
                    a = pygame.Surface((450, 500), flags)
                    a.fill((16, 28, 41, 131) if flags else (16, 28, 41))
                    b = a.copy()
                    scene._qa_cloud_use_cache = False
                    scene._draw_sky(a, travel, 109, night, .5, 'chuva')
                    scene._qa_cloud_use_cache = True
                    scene._draw_sky(b, travel, 109, night, .5, 'chuva')
                    self.assertEqual(pixels(a), pixels(b), (flags,night,travel))
        self.assertEqual(len(scene._qa_cloud_sprite_cache), 2)

    def test_snapshot_parcelado_limita_custo_por_passo(self):
        from pixelrush_qa_snapshot_v327743 import CapturaParceladaQA
        groups = {}
        counts = defaultdict(int)
        peaks = defaultdict(lambda: {'mais_33ms':0,'mais_50ms':0,'mais_100ms':0})
        for bioma in ('cidade','neve','deserto'):
            chave = 'corrida_normal|' + bioma
            groups[chave] = {('metric_%02d' % i): deque(range(1800),maxlen=1800)
                             for i in range(20)}
            counts[chave] = 1800
        logs = deque(({'modo':'corrida_normal','bioma':'cidade','total_ms':i}
                      for i in range(4000)),maxlen=4000)
        qa = SimpleNamespace(agregados=groups, quantidades=counts,
                             picos=peaks, ultimos=logs)
        capture = CapturaParceladaQA(qa)
        steps = 0
        while True:
            prev_metrics = capture.copiadas
            prev_rows = len(capture._linhas)
            output = capture.passo()
            steps += 1
            self.assertLessEqual(capture.copiadas-prev_metrics, 2)
            self.assertLessEqual(len(capture._linhas)-prev_rows, 64)
            if output is not None:
                break
            self.assertLess(steps, 100)
        result_groups, result_rows = output
        self.assertEqual(len(result_rows), 4000)
        self.assertEqual(sum(len(x['amostras']) for x in result_groups.values()), 60)
        self.assertEqual(steps, 63)

    def test_exportacao_periodica_e_final_em_json_csv(self):
        from pixelrush_qa_android_v327728 import QATelemetria
        with tempfile.TemporaryDirectory(prefix='pixelrush-qa743-') as temp:
            qa = QATelemetria('v3.277.45-QA', 'LIMPA', caminho=temp)
            for _ in range(625):
                qa.iniciar('JOGANDO', 'cidade')
                qa.marcar('renderizacao_e_ui')
                qa.fim()
            self.assertIsNone(qa._qa_snapshot_pendente)
            self.assertTrue(qa.salvar(esperar=True))
            if qa._qa_gravador:
                qa._qa_gravador.finalizar()
            path = Path(temp) / 'pixelrush_qa_v327745.json'
            csv = Path(temp) / 'pixelrush_qa_frames_v327745.csv'
            self.assertTrue(path.is_file())
            self.assertTrue(csv.is_file())
            document = json.loads(path.read_text('utf8'))
            self.assertEqual(document['versao'], 'v3.277.45-QA')
            self.assertEqual(document['quadros_observados'],625)
            self.assertIn('corrida_normal|cidade', document['grupos'])
            self.assertTrue(csv.read_text('utf8').startswith('modo,bioma,total_ms'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
