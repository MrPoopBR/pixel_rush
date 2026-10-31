"""Guarda de integridade das 7 artes aprovadas do Pixel Rush.

Compara SHA-256 na PRIMEIRA utilização de cada bioma.
Sem modificar imagem, gameplay, hitboxes ou jogo salvo.
PIXELRUSH_ART_STRICT=1 torna incompatibilidade um erro explícito para builds QA.
"""
from pathlib import Path
import hashlib
import os
import warnings

EXPECTED={'cidade': '32cbe1586cd72715f8e78cb8994df2d0ee03384726691bc5665becd16db0461a', 'deserto': 'b4e2d1173633bfd9abe46110de9ab34edf512a58bb286bef5b533f449e199b6f', 'vulcao': 'b9ab5118b604ad81744db0c658cf7ec7946d5484545815c5fa0a64b6b4b47893', 'floresta': '5afe60341e051770d7206fdc3ee57652c00ec907c6f6c3e9f74ba6139faa6e00', 'cidade_futurista': 'c04f82ea5a60874a52870256e94691887404edbf5587fda05ebc45c811493bf0', 'ilhas_celestes': '4e9a1a669ee48130f8a4db32328cf6a5932823c331cf10b4c05185def21cb6fe', 'neve': '4921cc17d6fff8d6795746f94f13ceb622630d1acc2354df41d266f8b6622633'}
_ALREADY_CHECKED=set()

def verificar_arte(caminho,bioma):
    caminho=Path(caminho)
    chave=(str(caminho),bioma)
    if chave in _ALREADY_CHECKED:return True
    _ALREADY_CHECKED.add(chave)
    expected=EXPECTED.get(bioma)
    if not expected:return True
    digest=hashlib.sha256(caminho.read_bytes()).hexdigest()
    if digest==expected:return True
    msg='Pixel Rush: arte oficial do bioma %s difere da arte aprovada! (%s)' % (bioma,caminho.name)
    if os.environ.get('PIXELRUSH_ART_STRICT')=='1':raise RuntimeError(msg)
    warnings.warn(msg,RuntimeWarning,stacklevel=2)
    return False
