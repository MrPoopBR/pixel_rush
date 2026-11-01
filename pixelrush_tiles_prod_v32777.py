"""v3.277.7-PROD: resultados de acabamento já calculados pelo motor original.

Somente cache de sprites por conteúdo (RGBA + plano + algoritmo). Nenhuma
alteração de material, shader, efeito, física, tick ou hitbox. Falhas de
arquivo/assinatura levam SEMPRE ao algoritmo original.
"""
from pathlib import Path
import hashlib
import pickle
import zlib
import pygame

_DIR = Path(__file__).resolve().parent / 'assets' / 'tiles_prod_v32777'
_HASHES = {
    'neve': '08d8d3273e4d2b27a9060b4106333c102f680cb7f92bc914edd09466f41aabd3',
    'cidade_futurista': 'cbbf3e1adf04b96462fde33400149f00e3722bfe82324d309ae0cd20a7e1f9a6',
    'deserto': '2aacf6a247548412725b5c3f643ff1ba1115ccc89fb2eabcdb335a52fe2a1726',
}
_cache_nome = None
_cache_dados = None
_instalado = False


def _dados_bioma(nome):
    global _cache_nome, _cache_dados
    if nome == _cache_nome:
        return _cache_dados
    # Somente um bioma preparado residente de cada vez. Quando muda,
    # todos os sprites e buffers do anterior deixam de ser referenciados.
    _cache_nome = nome
    _cache_dados = None
    try:
        caminho = _DIR / f'{nome}.tiles'
        dados = caminho.read_bytes()
        if hashlib.sha256(dados).hexdigest() != _HASHES[nome]:
            return None
        conteudo = pickle.loads(zlib.decompress(dados))
        if not isinstance(conteudo, dict):
            return None
        _cache_dados = conteudo
        return conteudo
    except (OSError, ValueError, EOFError, TypeError, zlib.error, pickle.UnpicklingError):
        return None


def _envolver(algoritmo, etapa):
    def usar(original, *args, **kwargs):
        # A rotina original permanece a fonte de verdade e é chamada se não
        # houver imagem pré-calculada para o contexto exato.
        biome = next((arg for arg in args if arg in _HASHES), None)
        plano = next((arg for arg in args if arg in ('far', 'mid')), None)
        if biome is None or plano is None:
            return algoritmo(original, *args, **kwargs)
        borda = kwargs.get('borda', 12) if etapa == 'extrusao' else None
        dados = _dados_bioma(biome)
        if dados is None:
            return algoritmo(original, *args, **kwargs)
        assinatura = hashlib.sha256(pygame.image.tobytes(original, 'RGBA')).digest()
        item = dados.get((etapa, biome, plano, borda, assinatura))
        if item is None:
            return algoritmo(original, *args, **kwargs)
        tamanho, rgba, metricas = item
        # A cópia garante que os passes existentes possam modificar o sprite
        # sem alterar o atlas empacotado nem outra pose.
        superficie = pygame.image.frombytes(zlib.decompress(rgba), tamanho, 'RGBA').convert_alpha()
        return superficie, dict(metricas)
    return usar


def instalar():
    global _instalado
    if _instalado:
        return
    import pixelrush_geometria_v3197 as g197
    import pixelrush_identidade_v3200 as g200
    import pixelrush_geometria_v3219 as g219
    import pixelrush_geometria_v3220 as g220
    for modulo, funcao, etapa in (
        (g197, 'esculpir_volume', 'extrusao'),
        (g200, 'entalhar', 'identidade'),
        (g219, 'lapidar', 'lapidacao_neve'),
        (g220, 'lapidar', 'lapidacao_futura'),
    ):
        setattr(modulo, funcao, _envolver(getattr(modulo, funcao), etapa))
    _instalado = True
