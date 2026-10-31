"""PIXEL RUSH P21 — QA independente v1.2.0, sem importar produção/pets."""
from __future__ import annotations
import ast
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import unittest
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'v3.285.4'

def digest(file: Path) -> str:
    h = hashlib.sha256()
    with file.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def safe_path(raw: str) -> Path | None:
    if not raw:
        return None
    relative = Path(raw)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('O caminho precisa ser relativo ao checkout')
    result = (ROOT / relative).resolve()
    if not result.is_relative_to(ROOT.resolve()):
        raise ValueError('Caminho fora do checkout')
    return result

def sources(folder: Path | None) -> dict:
    if folder is None:
        return {'estado': 'nao_executado', 'motivo': 'Fontes reais v3.285.4 indisponíveis'}
    if not folder.is_dir() or folder.is_symlink():
        return {'estado': 'bloqueado', 'motivo': 'Pasta inválida'}
    files = sorted(folder.rglob('*.py'))
    if not files or len(files) > 1500:
        return {'estado': 'bloqueado', 'motivo': 'Quantidade de fontes inválida'}
    matched = {'LIMPA': [], 'DEV': []}
    for f in files:
        if f.is_symlink() or not f.is_file() or f.stat().st_size > 8 * 1024 * 1024:
            return {'estado': 'bloqueado', 'motivo': 'Link, tipo ou tamanho não permitido'}
        try:
            raw = f.read_bytes()
            tree = ast.parse(raw.decode('utf-8-sig'), filename=f.name)
        except (SyntaxError, UnicodeError) as exc:
            return {'estado': 'falha', 'erro': type(exc).__name__, 'arquivo': f.name}
        declarations = [node.value.value for node in tree.body if isinstance(node, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == 'VERSAO' for t in node.targets)
                        and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)]
        for edition in matched:
            if edition in f.name.upper() and VERSION in declarations:
                matched[edition].append(f.name)
    if not all(matched.values()):
        return {'estado': 'bloqueado', 'motivo': 'Par LIMPA/DEV v3.285.4 ausente', 'encontrados': matched}
    return {'estado': 'aprovado_estatico', 'fontes': matched, 'total_parseado': len(files),
            'limite': 'AST estático; jogo não executado'}

def smoke() -> dict:
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    try:
        import pygame
        if pygame.version.ver != '2.5.8':
            return {'estado': 'falha', 'versao': pygame.version.ver}
        pygame.init()
        try:
            surf = pygame.display.set_mode((32, 32))
            surf.fill((1, 2, 3))
            pygame.draw.rect(surf, (10, 20, 30), pygame.Rect(4, 4, 10, 10))
            ok = surf.get_at((5, 5))[:3] == (10, 20, 30) and surf.get_at((0, 0))[:3] == (1, 2, 3)
        finally:
            pygame.quit()
        return {'estado': 'aprovado' if ok else 'falha', 'versao': pygame.version.ver}
    except Exception as exc:
        return {'estado': 'falha', 'erro': type(exc).__name__}

def tests() -> dict:
    import io
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'qa_p21'), 'test_*.py', top_level_dir=str(ROOT))
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return {'estado': 'aprovado' if result.wasSuccessful() and result.testsRun else 'falha',
            'total': result.testsRun, 'falhas': len(result.failures), 'erros': len(result.errors)}

def main() -> int:
    output = ROOT / 'artifacts' / 'p21-qa.json'
    output.parent.mkdir(exist_ok=True)
    if output.exists():
        print('Falha fechada: saída já existe', file=sys.stderr)
        return 2
    try:
        source = safe_path(os.environ.get('P21_SOURCE_ROOT', ''))
    except ValueError as exc:
        print('Entrada recusada:', exc, file=sys.stderr)
        return 2
    a = sources(source)
    t = tests()
    p = smoke()
    required = os.environ.get('P21_REQUIRE_SOURCE', 'false').lower() == 'true'
    success = t['estado'] == 'aprovado' and p['estado'] == 'aprovado' and a['estado'] not in ('falha', 'bloqueado') and (not required or a['estado'] == 'aprovado_estatico')
    doc = {'schema': 'pixelrush.p21.branch_ci.v1', 'qa_version': '1.3.0',
           'versao_do_jogo_referencia': VERSION, 'executado_em': datetime.now(timezone.utc).isoformat(),
           'python': platform.python_version(), 'sistema': platform.system(),
           'git_sha': os.getenv('GITHUB_SHA', ''), 'evento': os.getenv('GITHUB_EVENT_NAME', ''),
           'regressoes': t, 'pygame_dummy': p, 'fontes': a,
           'resultado': 'QA_ISOLADO_APROVADO' if success else 'FALHA_OU_BLOQUEIO',
           'gates_p21': '1/4 (25%) — INALTERADOS',
           'limites': 'Não valida gameplay, 7 biomas, Android, hardware ou produção'}
    output.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'resultado': doc['resultado'], 'testes': t['total'], 'fontes': a['estado']}))
    return 0 if success else 2

if __name__ == '__main__':
    raise SystemExit(main())
