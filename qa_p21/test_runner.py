"""Regressões do próprio QA P21, sem executar o jogo."""
from __future__ import annotations
import hashlib
from pathlib import Path
import tempfile
import unittest
from qa_p21 import runner as q

class TesteP21(unittest.TestCase):
    def test_01_versao(self): self.assertEqual(q.VERSION, 'v3.285.4')
    def test_02_sha256(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / 'x'; f.write_bytes(b'abc')
            self.assertEqual(q.digest(f), hashlib.sha256(b'abc').hexdigest())
    def test_03_ausente(self): self.assertEqual(q.sources(None)['estado'], 'nao_executado')
    def test_04_pasta_nao_existe(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(q.sources(Path(d) / 'ausente')['estado'], 'bloqueado')
    def test_05_pasta_vazia(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(q.sources(Path(d))['estado'], 'bloqueado')
    def test_06_historica_recusada(self):
        with tempfile.TemporaryDirectory() as d:
            for v in ('LIMPA', 'DEV'):
                (Path(d) / f'PixelRush_{v}.py').write_text('VERSAO="v3.277.11"\n')
            self.assertEqual(q.sources(Path(d))['estado'], 'bloqueado')
    def test_07_ast_sem_executar(self):
        with tempfile.TemporaryDirectory() as d:
            for v in ('LIMPA', 'DEV'):
                (Path(d) / f'PixelRush_{v}.py').write_text('VERSAO="v3.285.4"\nraise RuntimeError("nao executar")\n')
            self.assertEqual(q.sources(Path(d))['estado'], 'aprovado_estatico')
    def test_08_sintaxe_ruim(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / 'error.py').write_text('def (:\n')
            self.assertEqual(q.sources(Path(d))['estado'], 'falha')
    def test_09_nenhuma_escrita(self):
        with tempfile.TemporaryDirectory() as d:
            fs = []
            for v in ('LIMPA', 'DEV'):
                f = Path(d) / f'PixelRush_{v}.py'; f.write_text('VERSAO="v3.285.4"\n'); fs.append(f)
            before = [q.digest(f) for f in fs]
            q.sources(Path(d))
            self.assertEqual(before, [q.digest(f) for f in fs])
    def test_10_caminho_absoluto(self):
        with self.assertRaises(ValueError): q.safe_path(str(q.ROOT.resolve()))
    def test_11_caminho_pai(self):
        with self.assertRaises(ValueError): q.safe_path('../fora')
    def test_12_caminho_vazio(self): self.assertIsNone(q.safe_path(''))
    def test_13_caminho_relativo(self): self.assertEqual(q.safe_path('qa_p21'), (q.ROOT / 'qa_p21').resolve())
    def test_14_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            real = Path(d) / 'src.py'; real.write_text('VERSAO="v3.285.4"\n')
            link = Path(d) / 'link.py'
            try: link.symlink_to(real)
            except (OSError, NotImplementedError): self.skipTest('sistema sem symlinks')
            self.assertEqual(q.sources(Path(d))['estado'], 'bloqueado')
    def test_15_smoke(self): self.assertEqual(q.smoke()['estado'], 'aprovado')
    def test_16_restricao_ast(self):
        code = (q.ROOT / 'qa_p21' / 'runner.py').read_text(encoding='utf-8')
        self.assertNotIn('import PixelRush', code)
        self.assertNotIn('import main', code)
    def test_17_sem_gate_automatico(self):
        code = (q.ROOT / 'qa_p21' / 'runner.py').read_text(encoding='utf-8')
        self.assertIn('INALTERADOS', code)
    def test_18_arquivo_grande(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / 'grande.py').write_bytes(b'#' * (8 * 1024 * 1024 + 1))
            self.assertEqual(q.sources(Path(d))['estado'], 'bloqueado')

if __name__ == '__main__': unittest.main()
