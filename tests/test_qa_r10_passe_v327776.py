# -*- coding: utf-8 -*-
"""QA773: guarda de perfil em blocos disjuntos sem alterar cenas/simulacao."""
import ast
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py'
SUBS=('qa_ceu_2d','qa_world_draw','qa_particulas_mundo',
      'qa_fundo_cache_chao','qa_render_antes_sprites',
      'qa_render_apos_sprites','qa_hud_corrida',
      'qa_replay_captura','qa_simulacao_ticks',
      'qa_sim_diretores','qa_sim_parallax','qa_sim_clima')

class PerfilR10773(unittest.TestCase):
    def test_engine_e_instrumentacao_tem_sintaxe_valida(self):
        for name in (str(ENGINE),'pixelrush_qa_android_v327728.py',
                     'pixelrush_profiler_v3204.py',
                     'pixelrush_qa_render_v327729.py',
                     'pixelrush_qa_replay_pool_v327773.py'):
            path=Path(name) if name.startswith('/') else ROOT/name
            ast.parse(path.read_text('utf8'),filename=str(path))
        self.assertIn('v3.277.79-QA-ANDROID-RC',ENGINE.read_text('utf8'))

    def test_todas_as_marcas_saem_na_telemetria(self):
        engine=ENGINE.read_text('utf8')
        qa=(ROOT/'pixelrush_qa_android_v327728.py').read_text('utf8')
        legacy=(ROOT/'pixelrush_profiler_v3204.py').read_text('utf8')
        for name in SUBS:
            self.assertIn('_pro_sub_inicio("%s")'%name,engine)
            self.assertIn(name,qa)
            self.assertIn(name,legacy)
        self.assertIn("render_restante_qa773",qa)
        self.assertIn("simulacao_restante_qa773",qa)
        compact=qa.split("blocos = (",1)[1].split(")",1)[0]
        self.assertNotIn("'mundo_2_5d'",compact)
        self.assertNotIn("'clima_render'",compact)

    def test_gameplay_e_replay_sao_os_originais(self):
        engine=ENGINE.read_text('utf8')
        self.assertIn('while sim_acumulado + 1e-9 >= PASSO_FIXO',engine)
        self.assertIn('atualizar_simulacao()',engine)
        self.assertIn('bg_parallax.draw(display_surface, cor_ceu_render, e_noite)',engine)
        self.assertIn('replay_morte.capturar(display_surface, frame_count)',engine)
        original=(ROOT/'pixelrush_extras_v3174.py').read_text('utf8')
        self.assertIn('INTERVALO_TICKS = 5',original)
        self.assertIn('MAX_AMOSTRAS = 72',original)
        self.assertIn('self.buffer.append(pygame.transform.scale(superficie, self.TAMANHO))',original)
        qa=(ROOT/'pixelrush_qa_render_v327729.py').read_text('utf8')
        self.assertIn('instalar_replay_qa()',qa)

    def test_conta_somente_blocos_disjuntos(self):
        from pixelrush_qa_android_v327728 import QATelemetria
        # Inspecao estatico-independente: os marcadores secundarios nao
        # devem subtrair novamente o mundo incluido no fundo.
        source=(ROOT/'pixelrush_qa_android_v327728.py').read_text('utf8')
        trecho=source.split("blocos = (",1)[1].split(")",1)[0]
        self.assertIn("'qa_fundo_cache_chao'",trecho)
        self.assertIn("'qa_render_apos_sprites'",trecho)

if __name__=='__main__':
    unittest.main(verbosity=2)
