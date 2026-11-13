#!/usr/bin/env python3
"""Aplica R156 somente sobre R155 autenticada. Falha antes de escrever se preflight falhar."""
from __future__ import annotations
import ast
import argparse
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
CLASS_NAMES = {"ParallaxBackground", "LivingWorld"}
METHOD_NAMES = {"draw", "desenhar"}
FUNCTION_NAMES = {"update_morte", "atualizar_morte", "desenhar"}
INJECTED_IMPORT = "import pixelrush_qa_internal as _pixelrush_qa_internal\n"

def _top_insert_line(tree):
    nodes = list(tree.body)
    after = 0
    if nodes and isinstance(nodes[0], ast.Expr) and isinstance(nodes[0].value, ast.Constant) and isinstance(nodes[0].value.value, str):
        after = nodes.pop(0).end_lineno
    for node in nodes:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            after = node.end_lineno
        else:
            break
    return after

def _collect(tree, short_name):
    decorators, presentation = [], []
    class_stack = []
    class Visit(ast.NodeVisitor):
        def visit_ClassDef(self, node):
            class_stack.append(node.name)
            self.generic_visit(node)
            class_stack.pop()
        def visit_FunctionDef(self, node):
            cls = class_stack[-1] if class_stack else ""
            selected = (cls in CLASS_NAMES and node.name in METHOD_NAMES) or (
                node.name in FUNCTION_NAMES and (not class_stack or node.name == "update_morte"))
            if selected and not any(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in ast.walk(node)):
                label = short_name + ":" + ".".join(class_stack + [node.name])
                decorators.append((node.lineno, "@_pixelrush_qa_internal.measure(" + repr(label) + ")"))
            self.generic_visit(node)
        visit_AsyncFunctionDef = visit_FunctionDef
        def visit_Expr(self, node):
            call = node.value
            if (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                and call.func.attr in ("flip", "update")
                and isinstance(call.func.value, ast.Attribute)
                and call.func.value.attr == "display"
                and isinstance(call.func.value.value, ast.Name)
                and call.func.value.value.id == "pygame"):
                presentation.append(node.lineno)
            self.generic_visit(node)
    Visit().visit(tree)
    return decorators, presentation

def _recover_source(patched, is_engine):
    lines = []
    for ln in patched.splitlines(keepends=True):
        v = ln.strip()
        if v == INJECTED_IMPORT.strip() or v == "_pixelrush_qa_internal.frame_tick()" or v.startswith("@_pixelrush_qa_internal.measure("):
            continue
        lines.append(ln)
    result = "".join(lines)
    if is_engine:
        result = result.replace('VERSAO = "v3.279.08-QA-PROFILER"', 'VERSAO = "v3.279.07-ANDROID-RC"')
    return result

def patch_file(path, is_engine=False):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    lines = source.splitlines(keepends=True)
    decorators, possible = _collect(tree, path.name)
    edits, display_count = [], 0
    for num, marker in decorators:
        indent = re.match(r"[ \t]*", lines[num - 1]).group()
        edits.append((num - 1, indent + marker + "\n"))
    for num in possible:
        line = lines[num - 1]
        if re.match(r"^[ \t]*pygame\.display\.(flip|update)\(.*\)\s*(#.*)?$", line):
            indent = re.match(r"[ \t]*", line).group()
            edits.append((num, indent + "_pixelrush_qa_internal.frame_tick()\n"))
            display_count += 1
    if not edits:
        return None, 0, 0
    edits.append((_top_insert_line(tree), INJECTED_IMPORT))
    for pos, added in sorted(edits, key=lambda x: x[0], reverse=True):
        lines.insert(pos, added)
    modified = "".join(lines)
    if is_engine:
        modified = modified.replace('VERSAO = "v3.279.07-ANDROID-RC"', 'VERSAO = "v3.279.08-QA-PROFILER"')
    ast.parse(modified, filename=str(path))
    if _recover_source(modified, is_engine) != source:
        raise ValueError("Codigo original mudou alem da instrumentacao: " + str(path))
    return modified, len(decorators), display_count

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source_dir", type=Path)
    opts = ap.parse_args()
    root = opts.source_dir.resolve()
    spec = root / "buildozer.spec"
    engine = root / "PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py"
    loader = root / "src/pixelrush/platform/legacy_imports_v327797.py"
    if not all(p.is_file() for p in (spec, engine, loader)):
        raise SystemExit("R156: faltam arquivos obrigatorios da fonte R155")
    s = spec.read_text(encoding="utf-8")
    eng = engine.read_text(encoding="utf-8")
    if not re.search(r"^version\s*=\s*3\.279\.07\s*$", s, re.M) or not re.search(r"^android.numeric_version\s*=\s*327907\s*$", s, re.M):
        raise SystemExit("R156: fonte nao corresponde a v3.279.07")
    if not re.search(r"^package.name\s*=\s*bigheadmobile_pixelrush\s*$", s, re.M):
        raise SystemExit("R156: package R155 divergiu")
    if 'VERSAO = "v3.279.07-ANDROID-RC"' not in eng or "class _LegacyBytecodeLoader" not in loader.read_text(encoding="utf-8"):
        raise SystemExit("R156: correcoes oficiais R155 ausentes")
    if INJECTED_IMPORT.strip() in eng:
        raise SystemExit("R156: instrumentacao ja aplicada")
    staged = {}
    tally = []
    all_files = [engine] + sorted((root / "src").rglob("*.py"))
    for file in all_files:
        patched, funcs, frames = patch_file(file, file == engine)
        if patched is not None:
            staged[file] = patched
        if funcs or frames:
            tally.append((str(file.relative_to(root)), funcs, frames))
    if sum(x[2] for x in tally) < 1:
        raise SystemExit("R156: nenhuma chamada de apresentacao foi encontrada; abortando")
    if sum(x[1] for x in tally) < 1:
        raise SystemExit("R156: nenhuma funcao-alvo instrumentada; abortando")
    if engine not in staged:
        # Caso somente modulos importados tenham pontos de perfilamento:
        staged[engine] = eng.replace('VERSAO = "v3.279.07-ANDROID-RC"', 'VERSAO = "v3.279.08-QA-PROFILER"')
    for file, modified in staged.items():
        file.write_text(modified, encoding="utf-8")
    shutil.copyfile(HERE / "pixelrush_qa_internal.py", root / "pixelrush_qa_internal.py")
    s = re.sub(r"^package.name\s*=\s*bigheadmobile_pixelrush\s*$",
               "package.name = bigheadmobile_pixelrush_qa", s, flags=re.M)
    s = re.sub(r"^version\s*=\s*3\.279\.07\s*$", "version = 3.279.08", s, flags=re.M)
    s = re.sub(r"^android.numeric_version\s*=\s*327907\s*$", "android.numeric_version = 327908", s, flags=re.M)
    spec.write_text(s, encoding="utf-8")
    (root / "VERSAO_ATUAL.txt").write_text(
        "PIXEL RUSH R156 v3.279.08-QA. Somente instrumentacao interna e cProfile curto. "
        "Package isolado com.bigheadmobile_pixelrush_qa; saves R155 preservados. "
        "Nao homologado no Android.\n", encoding="utf-8")
    report = ["R156: arquivo, funcoes, chamadas de apresentacao"]
    report.extend(f"{name}: funcoes={f}, display={n}" for name, f, n in tally)
    report.append("TOTAL: funcoes=" + str(sum(x[1] for x in tally)) + " displays=" + str(sum(x[2] for x in tally)))
    (root / "RELATORIO_INSTRUMENTACAO_R156.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))

if __name__ == "__main__":
    main()
