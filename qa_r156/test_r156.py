"""Testes isolados pygame-ce para patch QA, sem modificar o APK de producao."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
PATCH = HERE / "aplicar_r156_qa.py"
SAMPLE = '''import pygame, random, hashlib, json
VERSAO = "v3.279.07-ANDROID-RC"
pygame.init()
screen = pygame.display.set_mode((64, 64))
rng = random.Random(271828)
class ParallaxBackground:
    def draw(self, surf):
        surf.fill((rng.randrange(255), 15, 21))
class LivingWorld:
    @staticmethod
    def draw(surf):
        pygame.draw.rect(surf,(85, 33, 9), (5, 8, 11, 12))
def update_morte(i): return i + 1
def run():
    for i in range(60):
        ParallaxBackground().draw(screen)
        LivingWorld.draw(screen)
        update_morte(i)
        pygame.display.flip()
    print("RESULT", json.dumps({"rng": list(rng.getstate()[1][:4]),
                                "rgba": hashlib.sha256(pygame.image.tobytes(screen, "RGBA")).hexdigest()}))
if __name__ == "__main__": run()
'''

class ValidateR156(unittest.TestCase):
    def setup_source(self, root):
        root.mkdir(parents=True)
        (root / "PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py").write_text(SAMPLE, encoding="utf-8")
        (root / "buildozer.spec").write_text(
            "[app]\npackage.name = bigheadmobile_pixelrush\nversion = 3.279.07\nandroid.numeric_version = 327907\n", encoding="utf-8")
        loader = root / "src/pixelrush/platform/legacy_imports_v327797.py"
        loader.parent.mkdir(parents=True)
        loader.write_text("class _LegacyBytecodeLoader: pass\n", encoding="utf-8")
    def run_game(self, root):
        env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", PIXELRUSH_QA_DIR=str(root))
        out = subprocess.run([sys.executable, "PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py"],
                             cwd=root, env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(out.returncode, 0, out.stderr)
        return next(x for x in out.stdout.splitlines() if x.startswith("RESULT "))
    def patch(self, root):
        return subprocess.run([sys.executable, str(PATCH), str(root)],
                              capture_output=True, text=True, timeout=60)
    def test_deterministic_rgba_rng_and_function_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a", Path(tmp) / "b"
            self.setup_source(a)
            shutil.copytree(a, b)
            baseline = self.run_game(a)
            result = self.patch(b)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(baseline, self.run_game(b))
            self.assertIn("TOTAL:", result.stdout)
            self.assertIn("com.bigheadmobile_pixelrush_qa", (b / "VERSAO_ATUAL.txt").read_text())
            self.assertTrue((b / "pixelrush_qa_internal/r156_metrics.jsonl").exists())
            parsed = json.loads((b / "pixelrush_qa_internal/r156_metrics.jsonl").read_text().splitlines()[-1])
            self.assertIn("FRAME_PRESENT_INTERVAL", parsed["stats"])
            self.assertEqual(parsed["stats"]["FRAME_PRESENT_INTERVAL"]["calls"], 59)
    def test_version_mismatch_fails_without_touching_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "src"
            self.setup_source(root)
            spec = root / "buildozer.spec"
            spec.write_text(spec.read_text().replace("327907", "327909"))
            before = (root / "PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py").read_bytes()
            result = self.patch(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(before, (root / "PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py").read_bytes())
    def test_no_display_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "src"
            self.setup_source(root)
            engine = root / "PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py"
            engine.write_text(engine.read_text().replace("pygame.display.flip()", "pass"))
            self.assertNotEqual(self.patch(root).returncode, 0)
    def test_all_patched_code_python_syntax(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "src"
            self.setup_source(root)
            self.assertEqual(self.patch(root).returncode, 0)
            for f in root.rglob("*.py"):
                ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
    def test_exception_preservation(self):
        sys.path.insert(0, str(HERE))
        import pixelrush_qa_internal as profiler
        @profiler.measure("test_exceptions")
        def sample(x):
            if x == 1: raise ArithmeticError("expected")
            return x * 3
        self.assertEqual(sample(2), 6)
        with self.assertRaises(ArithmeticError): sample(1)
        self.assertEqual(profiler._stats["test_exceptions"]["count"], 2)

if __name__ == "__main__":
    unittest.main()
