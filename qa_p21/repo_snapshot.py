"""P21 v1.4.0: prova estatica do checkout do GitHub, sem importar jogo.

Baselines Git Blob SHA-1 obtidos de main c07fe01c07cc (somente estes 5 arquivos).
Nao homologa fontes oficiais PIXEL RUSH v3.285.4.
"""
from __future__ import annotations
import ast
import hashlib
from pathlib import Path

BASELINES = {
    'main.py': 'a8e7b0a37aa5b39dcc6db725ad236a4210f79d40',
    'buildozer.spec': '5306be1cea00874ac6a8a33741e69f5f887251df',
    '.github/workflows/build-aab.yml': '72d81e620c860fc7ec7d1f845ca5ccf2ee0aa2d3',
    'p4a-recipes/pygame-ce/__init__.py': '489dee70f5b089d7f73a16e2348bf4744e3f4607',
    'README.md': 'b0e43055ab207ff30f82f314235fe4646a59f1cb',
}
BASE_COMMIT = 'c07fe01c07cc9b914aafc4799adc08f8855d5770'

def canonical_bytes(data: bytes) -> bytes:
    """Compensa core.autocrlf do checkout Windows antes de comparar Git blobs."""
    return data.replace(b'\r\n', b'\n')

def git_blob_sha(raw: bytes) -> str:
    data = canonical_bytes(raw)
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()

def declared_version(tree: ast.Module):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'VERSAO' for t in node.targets):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                return node.value.value
    return None

def audit_checkout(root: Path) -> dict:
    """Somente leitura. Falha fechada em arquivo ausente, modificado ou inseguro."""
    result = {'estado': 'falha', 'origem_main': BASE_COMMIT, 'tipo': 'snapshot_estatico',
              'fontes_v3_285_4': 'NAO_TESTADAS', 'protegidos': {}, 'erros': [],
              'nota': 'O main.py deste checkout e v3.9.1; nao e a distribuicao v3.285.4.'}
    raw_files = {}
    for name, expected in BASELINES.items():
        path = root / name
        if path.is_symlink() or not path.is_file():
            result['erros'].append(f'{name}: ausente ou link simbolico')
            continue
        try:
            if path.stat().st_size > 8 * 1024 * 1024:
                result['erros'].append(f'{name}: tamanho acima do limite')
                continue
            raw = path.read_bytes()
            digest = git_blob_sha(raw)
            result['protegidos'][name] = {'git_blob': digest, 'igual_main': digest == expected}
            if digest != expected:
                result['erros'].append(f'{name}: Git blob diferente de main {BASE_COMMIT[:12]}')
            raw_files[name] = raw
        except OSError as exc:
            result['erros'].append(f'{name}: {type(exc).__name__}')
    if len(raw_files) != len(BASELINES) or result['erros']:
        return result
    try:
        main_tree = ast.parse(raw_files['main.py'].decode('utf-8-sig'), 'main.py')
        recipe_tree = ast.parse(raw_files['p4a-recipes/pygame-ce/__init__.py'].decode('utf-8-sig'), 'pygame-ce/__init__.py')
        ver = declared_version(main_tree)
        result['versao_main_checkout'] = ver
        if ver != 'v3.9.1':
            result['erros'].append('Versao main do snapshot mudou')
        if not any(isinstance(n, (ast.Import, ast.ImportFrom)) and
                   ((isinstance(n, ast.Import) and any(a.name == 'pygame' for a in n.names)) or
                    (isinstance(n, ast.ImportFrom) and n.module == 'pygame')) for n in main_tree.body):
            result['erros'].append('Import pygame ausente no main historico')
        if not any(isinstance(n, ast.ClassDef) and n.name == 'PygameCeRecipe' for n in recipe_tree.body):
            result['erros'].append('Receita pygame-ce nao identificada')
        spec = raw_files['buildozer.spec'].decode('utf-8-sig')
        if 'version = 3.9.1' not in spec:
            result['erros'].append('Versao do buildozer historico divergiu')
        aab = raw_files['.github/workflows/build-aab.yml'].decode('utf-8-sig')
        if "if: github.ref == 'refs/heads/main'" not in aab:
            result['erros'].append('Restricao da AAB ao main ausente')
        if 'workflow_dispatch:' not in aab or 'contents: read' not in aab:
            result['erros'].append('AAB manual e permissao read nao confirmadas')
        result['analisados_ast'] = ['main.py', 'p4a-recipes/pygame-ce/__init__.py']
    except (UnicodeError, SyntaxError) as exc:
        result['erros'].append(f'Sintaxe ou unicode: {type(exc).__name__}')
    if not result['erros']:
        result['estado'] = 'aprovado_estatico'
    return result
