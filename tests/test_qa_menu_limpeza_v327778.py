# -*- coding: utf-8 -*-
"""QA778: regressao isolada da interface, piso do menu e perfil Completo.

Nao roda o jogo nem toca no save; executa somente metodos de render extraidos
do codigo de producao QA usando pygame-ce/SDL dummy.
"""
import ast
import math
import os
from pathlib import Path
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py"
CODE = GAME.read_text(encoding="utf-8")
TREE = ast.parse(CODE, filename=str(GAME))


def funcao_isolada(nome):
    candidatos = [n for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef) and n.name == nome]
    assert len(candidatos) == 1, (nome, len(candidatos))
    no = candidatos[0]
    mod = ast.fix_missing_locations(ast.Module(body=[no], type_ignores=[]))
    ambiente = {"pygame": pygame, "math": math, "LARGURA_VIRTUAL": 450, "ALTURA_VIRTUAL": 800}
    exec(compile(mod, str(GAME), "exec"), ambiente)
    return ambiente[nome]


class TestMenuQA778(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init()
        pygame.display.set_mode((450, 800))

    @classmethod
    def tearDownClass(cls):
        pygame.display.quit()

    def test_python_compila_e_versao(self):
        compile(CODE, str(GAME), "exec")
        self.assertIn('VERSAO = "v3.277.90-QA-ANDROID-RC"', CODE)
        spec = (ROOT / "buildozer.spec").read_text("utf-8")
        self.assertIn("version = 3.277.90", spec)
        self.assertIn("android.numeric_version = 327790", spec)

    def test_perfil_unico_e_migracao(self):
        fn = funcao_isolada("modo_grafico_leve")
        for modo in ("auto", "leve", "completo", "indefinido"):
            self.assertFalse(fn({"modo_grafico": modo}))
        self.assertIn('"vibracao": True, "modo_grafico": "completo"', CODE)
        self.assertIn('dados["modo_grafico"] = "completo"', CODE)
        self.assertNotIn("modos = ('auto', 'completo', 'leve')", CODE)

    def test_configuracoes_apenas_controles_essenciais(self):
        clique = CODE.split('        elif estado == "CONFIG":\n', 1)[1].split('        elif estado == "JOGANDO":', 1)[0]
        for proibido in ("btn_acessibilidade.collidepoint", "btn_config_controles.collidepoint",
                         "btn_modo_grafico.collidepoint"):
            self.assertNotIn(proibido, clique)
        for essencial in ("btn_musica_menos.collidepoint", "btn_sfx_mais.collidepoint",
                          "btn_vibracao.collidepoint", "btn_lang.collidepoint",
                          "btn_voltar_config.collidepoint"):
            self.assertIn(essencial, clique)

        desenhar = CODE.split('            elif estado == "CONFIG":\n                t_anim', 1)[1].split('            elif estado == "CONQUISTAS":', 1)[0]
        for proibido in ("btn_acessibilidade", "btn_config_controles", "btn_modo_grafico"):
            self.assertNotIn(proibido, desenhar)
        self.assertIn("btn_voltar_config", desenhar)

    def test_progresso_sem_os_quatro_atalhos(self):
        clique = CODE.split('        elif estado in ("CONQUISTAS", "RECORDES", "DESAFIOS", "RANKING"):', 1)[1].split('        elif estado == "BASE_CORREDOR":', 1)[0]
        for removido in ("btn_progress_conquistas.collidepoint", "btn_progress_base.collidepoint",
                         "btn_progress_reliquias.collidepoint", "btn_progress_ranking.collidepoint"):
            self.assertNotIn(removido, clique)
        self.assertIn('estado == "RECORDES" and btn_voltar_progresso.collidepoint(pos)', clique)
        render = CODE.split('            elif estado == "RECORDES":\n', 1)[1].split('            elif estado == "RANKING":', 1)[0]
        for removido in ('"CONQUISTAS", (230', '"BASE", (30', '"RELÍQUIAS", (150',
                         '"RANKING LOCAL"'):
            self.assertNotIn(removido, render)
        self.assertIn("btn_voltar_progresso", render)
        self.assertIn('"RECORDES POR BIOMA"', render)

    def test_chao_real_sobre_fundo_do_menu_rgba(self):
        metodo = funcao_isolada("draw_chao")
        class Parallax:
            cenario = "cidade"
            desloc_chao = 0.0
            def _obter_tile_chao(self):
                tile = pygame.Surface((450, 70))
                tile.fill((82, 84, 96))
                pygame.draw.rect(tile, (114, 132, 150), (0, 0, 450, 4))
                return tile
            def _desenhar_chao_vivo(self, destino):
                pass

        fundo = pygame.Surface((450, 800), pygame.SRCALPHA, 32)
        fundo.fill((35, 110, 203, 255))
        metodo(Parallax(), fundo)
        self.assertEqual(fundo.get_at((225, 720)), (35, 110, 203, 255))
        self.assertEqual(fundo.get_at((225, 730)), (114, 132, 150, 255))
        self.assertEqual(fundo.get_at((225, 780)), (82, 84, 96, 255))
        inicio = CODE.split('            if estado == "INICIO":\n                t_anim', 1)[1].split('            elif estado == "CANTINHO_PETS":', 1)[0]
        self.assertIn("bg_parallax.draw_chao(display_surface)", inicio)

    def test_cache_mundo_8_quadros_vs_5_e_paridade_rgba_estatica(self):
        from pixelrush_qa_ultraleve_v327730 import CacheFundoUltraQA
        self.assertIn("periodo_fundo_qa = 8 if os.environ.get('PIXELRUSH_QA_FUNDO_PERIODO') == '8' else 5", CODE)
        base = pygame.Surface((450, 800)).convert()
        base.fill((62, 84, 112))
        pygame.draw.rect(base, (130, 136, 142), (0, 730, 450, 70))
        esperado = pygame.image.tobytes(base, "RGBA")
        contagens = []
        for periodo in (5, 8):
            cache = CacheFundoUltraQA(periodo=periodo)
            destino = pygame.Surface((450, 800)).convert()
            redesenhos = 0
            for frame in range(80):
                if not cache.reusar(destino, ("cidade", "limpo"), True):
                    destino.blit(base, (0, 0))
                    cache.guardar(destino, ("cidade", "limpo"), True)
                    redesenhos += 1
                if frame in (0, 7, 39, 79):
                    self.assertEqual(pygame.image.tobytes(destino, "RGBA"), esperado)
            contagens.append(redesenhos)
        # Reduz reconstrucoes em 37.5%; nenhum ganho de FPS fisico inferido.
        self.assertEqual(contagens, [16, 10])


if __name__ == "__main__":
    unittest.main()
