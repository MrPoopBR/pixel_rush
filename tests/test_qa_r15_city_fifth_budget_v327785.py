# -*- coding: utf-8 -*-
"""QA785: comparar Mundo + Cidade completos e paridade RGBA byte-a-byte."""
import json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame

class R15CacheFifthQA785(unittest.TestCase):
    def test_instalacao_opt_in_rollback_somente_cidade(self):
        os.environ.setdefault('SDL_VIDEODRIVER','dummy')
        os.environ.setdefault('SDL_AUDIODRIVER','dummy')
        pygame.init()
        pygame.display.set_mode((450,800))
        from pixelrush_qa_city_bootstrap_v327759 import (
            instalar as bootstrap,restaurar_para_teste as restore_bootstrap)
        from pixelrush_qa_city_scaled_budget_v327785 import (
            instalar,restaurar_para_teste,diagnostico)
        bootstrap()
        from pixelrush_city2_v3125 import CityPilotScene
        old_init=CityPilotScene.__init__
        try:
            with unittest.mock.patch.dict(os.environ,
                                          {'PIXELRUSH_QA_CITY_SCALED_BUDGET':'1'}):
                instalar()
            one=CityPilotScene()
            self.assertEqual(one._scaled_limit,20)
            self.assertEqual(diagnostico()['extra_maximo_bytes'],10_800_000)
            self.assertEqual(len(one._scaled),0)
            self.assertEqual(diagnostico()['aumentos'],1)
            restaurar_para_teste()
            self.assertIs(CityPilotScene.__init__,old_init)
            self.assertEqual(CityPilotScene()._scaled_limit,14)
        finally:
            restaurar_para_teste()
            restore_bootstrap()
            pygame.quit()

    def test_livingworld_130_frames_quinto_rgba_e_cpu(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            for light in (0,1):
                result={}
                for limit in (14,20):
                    path=Path(tmp)/f'cidade_{light}_{limit}.json'
                    env=os.environ.copy()
                    env.update(SDL_AUDIODRIVER='dummy',
                               SDL_VIDEODRIVER='dummy',
                               PYTHONPATH=str(ROOT))
                    subprocess.run([sys.executable,
                        str(ROOT/'qa_a54/benchmark_city_fifth_v327785.py'),
                        '--limit',str(limit),'--light',str(light),
                        '--output',str(path)],
                        check=True,env=env,stdout=subprocess.DEVNULL,
                        timeout=90,cwd=ROOT)
                    result[limit]=json.loads(path.read_text('utf8'))
                a,b=result[14],result[20]
                self.assertEqual(a['quadros_rgba'],260)
                self.assertEqual(a['hashes_rgba'],b['hashes_rgba'],
                                 f'R15 RGBA diferente: lightweight={light}')
                self.assertEqual(a['periodo_redesenho_preservado'],5)
                self.assertEqual(b['periodo_redesenho_preservado'],5)
                self.assertLessEqual(b['cache_maximo_observado'],20)
                misses=lambda d:sum(d['counters'].get(kind,{}).get('miss',0)
                    for kind in ('image','fxmask','normal','geometry','material'))
                self.assertLess(misses(b),misses(a)*.3,
                                'Thrashing deve cair pelo menos 70%')
                orig=a['timings']['fifth_total']['p50_ms']
                new=b['timings']['fifth_total']['p50_ms']
                self.assertLess(new,orig*.90,
                    'Ganho >=10% no mundo completo quinto quadro (host)')
                extra_kib=b['memoria_rss_pico_kib']-a['memoria_rss_pico_kib']
                self.assertLess(extra_kib,16*1024,
                    'Aumento observado de RSS alem do orcamento de laboratorio')
                print('QA785',{'light':light,'quadros_rgba':260,
                     'falhas_baseline':misses(a),'falhas_qa':misses(b),
                     'fifth_p50_ms_base':orig,'fifth_p50_ms_qa':new,
                     'ganho_percentual':round(100*(1-new/orig),2),
                     'p95_base':a['timings']['fifth_total']['p95_ms'],
                     'p95_qa':b['timings']['fifth_total']['p95_ms'],
                     'rss_extra_kib':extra_kib})
if __name__=='__main__':
    import unittest.mock
    unittest.main(verbosity=2)
