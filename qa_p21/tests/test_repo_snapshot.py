"""22 casos novos P21: regressao estatica de fontes reais do checkout, sem importar jogo."""
from __future__ import annotations
import ast
from pathlib import Path
import tempfile
import unittest
from qa_p21.repo_snapshot import BASELINES, BASE_COMMIT, audit_checkout, canonical_bytes, declared_version, git_blob_sha

ROOT = Path(__file__).resolve().parents[2]

class TestRepoSnapshot(unittest.TestCase):
    def test_01_manifesto_tem_cinco_arquivos(self): self.assertEqual(len(BASELINES), 5)
    def test_02_commit_base_registrado(self): self.assertEqual(len(BASE_COMMIT), 40)
    def test_03_main_presente(self): self.assertTrue((ROOT/'main.py').is_file())
    def test_04_buildozer_presente(self): self.assertTrue((ROOT/'buildozer.spec').is_file())
    def test_05_workflow_aab_presente(self): self.assertTrue((ROOT/'.github/workflows/build-aab.yml').is_file())
    def test_06_receita_android_presente(self): self.assertTrue((ROOT/'p4a-recipes/pygame-ce/__init__.py').is_file())
    def test_07_readme_presente(self): self.assertTrue((ROOT/'README.md').is_file())
    def test_08_hash_main_inalterado(self): self.assertEqual(git_blob_sha((ROOT/'main.py').read_bytes()), BASELINES['main.py'])
    def test_09_hash_buildozer_inalterado(self): self.assertEqual(git_blob_sha((ROOT/'buildozer.spec').read_bytes()), BASELINES['buildozer.spec'])
    def test_10_hash_aab_inalterado(self): self.assertEqual(git_blob_sha((ROOT/'.github/workflows/build-aab.yml').read_bytes()), BASELINES['.github/workflows/build-aab.yml'])
    def test_11_hash_receita_inalterado(self): self.assertEqual(git_blob_sha((ROOT/'p4a-recipes/pygame-ce/__init__.py').read_bytes()), BASELINES['p4a-recipes/pygame-ce/__init__.py'])
    def test_12_hash_readme_inalterado(self): self.assertEqual(git_blob_sha((ROOT/'README.md').read_bytes()), BASELINES['README.md'])
    def test_13_git_blob_diferente_quando_mutado(self): self.assertNotEqual(git_blob_sha(b'prova original'), git_blob_sha(b'prova alterada'))
    def test_14_normaliza_crlf(self): self.assertEqual(canonical_bytes(b'a\r\nb\r\n'), b'a\nb\n')
    def test_15_hash_independe_crlf(self): self.assertEqual(git_blob_sha(b'a\r\nb\r\n'), git_blob_sha(b'a\nb\n'))
    def test_16_ast_main_real(self): ast.parse((ROOT/'main.py').read_bytes().decode('utf-8-sig'))
    def test_17_ast_receita_android_real(self): ast.parse((ROOT/'p4a-recipes/pygame-ce/__init__.py').read_bytes().decode('utf-8-sig'))
    def test_18_versao_main_real_diferente_da_32854(self):
        tree=ast.parse((ROOT/'main.py').read_bytes().decode('utf-8-sig'))
        self.assertEqual(declared_version(tree), 'v3.9.1')
        self.assertNotEqual(declared_version(tree), 'v3.285.4')
    def test_19_auditoria_estatica_sucesso(self):
        outcome=audit_checkout(ROOT)
        self.assertEqual(outcome['estado'], 'aprovado_estatico',outcome['erros'])
        self.assertEqual(len(outcome['protegidos']),5)
    def test_20_auditoria_nao_homologa_32854(self):
        self.assertEqual(audit_checkout(ROOT)['fontes_v3_285_4'], 'NAO_TESTADAS')
    def test_21_bloqueia_arquivo_ausente(self):
        with tempfile.TemporaryDirectory() as d:
            result=audit_checkout(Path(d))
            self.assertEqual(result['estado'], 'falha')
            self.assertTrue(result['erros'])
    def test_22_arquivo_verdadeiro_nao_e_regravado(self):
        p=ROOT/'main.py'
        before=git_blob_sha(p.read_bytes())
        audit_checkout(ROOT)
        self.assertEqual(before,git_blob_sha(p.read_bytes()))

if __name__=='__main__': unittest.main()
