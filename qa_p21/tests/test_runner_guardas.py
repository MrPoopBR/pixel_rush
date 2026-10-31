from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile
import unittest
from qa_p21 import ci_runner as ci

class TestRunnerProtecoes(unittest.TestCase):
    def test_tracker_ausente_nao_homologa(self):
        self.assertEqual(ci.check_tracker(None)['estado'],'nao_executado')
    def test_source_ausente_nao_homologa(self):
        self.assertEqual(ci.check_game_sources(None)['estado'],'nao_executado')
    def test_source_pasta_vazia_bloqueia(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(ci.check_game_sources(Path(t))['estado'],'bloqueado')
    def test_source_lima_dev_sintaxe_reconhecida(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for variant in ('LIMPA','DEV'):
                (root/f'PixelRush_v3.285.4_{variant}.py').write_text('VERSAO = "v3.285.4"\nif __name__ == "__main__": raise RuntimeError("NÃO EXECUTAR")\n',encoding='utf8')
            result=ci.check_game_sources(root)
            self.assertEqual(result['estado'],'aprovado_estatico')
            self.assertEqual(result['arquivos_parseados'],2)
    def test_source_versao_incorreta_bloqueia(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for variant in ('LIMPA','DEV'):
                (root/f'PixelRush_v3.277.11_{variant}.py').write_text('VERSAO="v3.277.11"\n',encoding='utf8')
            self.assertEqual(ci.check_game_sources(root)['estado'],'bloqueado')
    def test_source_invalido_sintaxe_falha(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            (root/'qualquer.py').write_text('def broken(:\n',encoding='utf8')
            self.assertEqual(ci.check_game_sources(root)['estado'],'falha')
    def test_source_nao_mexe_nos_arquivos(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            paths=[]
            for variant in ('LIMPA','DEV'):
                p=root/f'PixelRush_v3.285.4_{variant}.py'
                p.write_text('VERSAO="v3.285.4"\n',encoding='utf8');paths.append(p)
            original=[ci.sha256_file(p) for p in paths]
            ci.check_game_sources(root)
            self.assertEqual(original,[ci.sha256_file(p) for p in paths])
    def test_link_simbolico_bloqueia(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            (root/'real.py').write_text('VERSAO="v3.285.4"\n')
            try: (root/'link.py').symlink_to(root/'real.py')
            except (NotImplementedError,OSError): self.skipTest('sem permissão para symlinks')
            self.assertEqual(ci.check_game_sources(root)['estado'],'bloqueado')
    def test_modo_faltante_falha_fechada(self):
        result={'qa_local_aprovado': True,
                'auditoria_tracker':{'estado':'nao_executado'},
                'sintaxe_fontes':{'estado':'nao_executado'}}
        estado, faltantes=ci.avaliar_resultado(result,require_source=True)
        self.assertEqual(estado,'FALHA_OU_BLOQUEADO')
        self.assertEqual(faltantes,['fontes'])
    def test_nao_sobrescrever_relatorio(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'qa.json'; out.write_text('ORIGINAL')
            with self.assertRaises(SystemExit): ci.main(['--output',str(out)])
            self.assertEqual(out.read_text(),'ORIGINAL')
    def test_smoke_pygame_2_5_8(self):
        self.assertEqual(ci.check_pygame()['estado'],'aprovado')

if __name__=='__main__': unittest.main()