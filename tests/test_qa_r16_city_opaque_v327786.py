# -*- coding: utf-8 -*-
"""QA786 LAB: jogo real, hashes integrais RGBA, cinco mapas do 5o quadro."""
import os,sys,unittest,json,subprocess,tempfile,statistics
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame

class CityOpaqueQA786(unittest.TestCase):
    def test_gate_opaco_mutacao_e_rollback_sem_pendencias(self):
        pygame.init()
        pygame.display.set_mode((450,800))
        from pixelrush_qa_city_bootstrap_v327759 import instalar as boot,restaurar_para_teste as unboot
        from pixelrush_qa_city_scaled_budget_v327785 import instalar as cache,restaurar_para_teste as uncache
        from pixelrush_qa_city_opaque_overdraw_v327786 import instalar,restaurar_para_teste,diagnostico,_check_scene
        boot();cache()
        from pixelrush_city2_v3125 import CityPilotScene
        orig=(CityPilotScene.__init__,CityPilotScene._render_chunk,CityPilotScene.render_scene)
        try:
            with patch.dict(os.environ,{'PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW':'1'}):
                instalar()
            scene=CityPilotScene()
            self.assertEqual(scene._scaled_limit,20)
            self.assertEqual(set(scene._qa_opaque_maps_srcs),{'normal','flow'})
            self.assertTrue(diagnostico()['scenes_safe'])
            for kind in ('normal','flow'):
                a=pygame.Surface((450,500),pygame.SRCALPHA,32)
                b=a.copy()
                a.fill((37,59,121,11));b.fill((37,59,121,11))
                # O wrapper so pode eliminar as camadas inteiramente ocultas.
                original=orig[2]
                original(scene,a,202.,84,.9,'tempestade',.37,False,kind)
                scene.render_scene(b,202.,84,.9,'tempestade',.37,False,kind)
                self.assertEqual(pygame.image.tobytes(a,'RGBA'),
                                 pygame.image.tobytes(b,'RGBA'),kind)
            # Uma substituicao de atlas invalida a aprovacao por identidade.
            near=next(layer for layer in scene.layers if layer.name=='near')
            v=near.variants[0]
            orig_normal=v.normal
            v.normal=orig_normal.copy()
            try:
                a=pygame.Surface((450,500),pygame.SRCALPHA,32)
                b=a.copy()
                a.fill((53,18,97,0));b.fill((53,18,97,0))
                orig[2](scene,a,170.,72,.8,'chuva',.37,False,'normal')
                scene.render_scene(b,170.,72,.8,'chuva',.37,False,'normal')
                self.assertEqual(pygame.image.tobytes(a,'RGBA'),
                                 pygame.image.tobytes(b,'RGBA'))
            finally:
                v.normal=orig_normal
            # O gate reprova fonte incompleta; nao valida por bounding-box.
            near.variants[0].flow.set_at((101,17),(22,77,124,0))
            _check_scene(scene)
            self.assertNotIn('flow',scene._qa_opaque_maps_srcs)
        finally:
            restaurar_para_teste()
            self.assertEqual((CityPilotScene.__init__,CityPilotScene._render_chunk,
                              CityPilotScene.render_scene),orig)
            uncache();unboot()
            pygame.quit()

    def test_260_rgba_mundo_real_e_melhora_do_quinto(self):
        with tempfile.TemporaryDirectory() as temp:
            for light in (0,1):
                runs={}
                for candidate in (0,1):
                    report=Path(temp)/f'report_{light}_{candidate}.json'
                    env=os.environ.copy()
                    env.update(SDL_AUDIODRIVER='dummy',SDL_VIDEODRIVER='dummy',
                               PYTHONPATH=str(ROOT))
                    subprocess.run([sys.executable,
                        str(ROOT/'qa_a54/benchmark_city_opaque_v327786.py'),
                        '--limit','20','--light',str(light),
                        '--opaque',str(candidate),'--output',str(report)],
                        env=env,check=True,timeout=110,stdout=subprocess.DEVNULL,
                        cwd=ROOT)
                    runs[candidate]=json.loads(report.read_text('utf8'))
                a,b=runs[0],runs[1]
                self.assertEqual(a['quadros_rgba'],260)
                self.assertEqual(a['hashes_rgba'],b['hashes_rgba'],
                    'RGBA completo divergiu: light='+str(light))
                self.assertEqual(a['periodo_redesenho_preservado'],5)
                self.assertEqual(b['periodo_redesenho_preservado'],5)
                self.assertEqual(a['limit'],20)
                self.assertEqual(b['limit'],20)
                self.assertGreater(b['opaque_stats']['chunks_hidden'],0)
                self.assertLessEqual(b['cache_maximo_observado'],20)
                before=a['timings']['fifth_total']['p50_ms']
                after=b['timings']['fifth_total']['p50_ms']
                gain=100*(1-after/before)
                self.assertLess(after,before*.96,
                     'Sem ganho >=4% no quinto quadro completo: '+str((before,after)))
                for kind in ('normal','flow'):
                    self.assertLess(b['timings'][kind]['p50_ms'],
                                    a['timings'][kind]['p50_ms']*.95,
                                    'Canal '+kind+' sem ganho >=5%')
                print('QA786',dict(light=light,rgba=260,
                      skips=b['opaque_stats']['chunks_hidden'],
                      full_baseline_p50=before,full_candidate_p50=after,
                      gain_percent=round(gain,2),
                      normal=[a['timings']['normal']['p50_ms'],
                              b['timings']['normal']['p50_ms']],
                      flow=[a['timings']['flow']['p50_ms'],
                            b['timings']['flow']['p50_ms']],
                      rss_delta_KiB=b['memoria_rss_pico_kib']-a['memoria_rss_pico_kib']))
if __name__=='__main__':
    unittest.main(verbosity=2)
