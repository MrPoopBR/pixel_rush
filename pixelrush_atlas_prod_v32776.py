"""v3.277.6-PROD — carrega os atlas originais pré-calculados, sem criar arte nova.

Os atlas são gerados uma única vez a partir do renderizador intacto da
v3.277.5 e guardam RGBA, camadas, poses, máscaras e materiais originais.
A verificação SHA-256 ocorre ANTES da desserialização dos arquivos locais.
Nenhuma cena inativa permanece em RAM.
"""
from pathlib import Path
import hashlib
from pixelrush_hash_compat_v327725 import sha256_stream, load_verified_pickle
import pickle
import pygame
from pixelrush_biomes2_v3185 import ModularBiomeScene

_ATLAS = Path(__file__).resolve().parent / 'assets' / 'atlas_prod_v32776'
# HASHES_ATLAS_V32776 — preenchidos após gerar os recursos de release.
_HASHES = {
    'neve': 'ac9bc12ec49d538469a0c3bc2ce2e073632f06c46a49534e9b691cd8a6eef574',
    'neve_lite': 'de9f9eb6d54aac9a3ec900fc9917e72197238a21836f92c3ebb02a25b7ae1648',
    'cidade_futurista': '1605717719739e14916eec09a580686a6ac4469f959b5ba5d6fb49a9d861f5b9',
    'cidade_futurista_lite': '3a3dfbf8ef937892412ef028f7e38cad161b7c0dad6d5bf074661ab07b86f1d4',
    'deserto': '6649945527fb7a844f97d8100e4b133699f884306eddd0758f1c6ccadc9770aa',
    'deserto_lite': '88b5c1432caee0a5ce42f8222bd0add5da7177332d5640a9c62ad93d6248584c',
}

def _restore_surface(dados, tamanho):
    return pygame.image.frombytes(dados, tamanho, 'RGBA').convert_alpha()

def carregar_cena(bioma, lightweight=False):
    """Restaura uma cena modular original ou usa construtor se atlas indisponível."""
    nome = f"{bioma}_lite" if lightweight else bioma
    esperado = _HASHES.get(nome)
    if esperado is None:
        return ModularBiomeScene(bioma, lightweight=lightweight)
    try:
        with (_ATLAS / f'{nome}.atlas').open('rb') as arquivo:
            # Fluxo em blocos: evita uma cópia temporária do atlas inteiro
            # (até 24 MiB no Deserto) na memória residente do processo.
            if sha256_stream(arquivo) != esperado:
                raise ValueError('atlas de cenário não íntegro')
            arquivo.seek(0)
            estado = load_verified_pickle(arquivo)  # arquivo local validado por SHA-256
        if estado.get('biome') != bioma:
            raise ValueError('atlas pertence a outro cenário')
        cena = ModularBiomeScene.__new__(ModularBiomeScene)
        lampas = estado.pop('_lampas_indexadas_v32776', ())
        cena.__dict__.update(estado)
        if bioma == 'cidade_futurista':
            # O original usa hash(bioma), que varia por processo, no nevoeiro.
            # Reproduzir somente esse overlay barato preserva a variacao original.
            cena._build_global_overlays()
        if bioma == 'deserto':
            # O código original indexa a luz pelo id() da Surface em memória.
            # Reconstruir estes índices após restaurar as poses do atlas.
            cena._lamp_pixels = {
                id(cena._poses[pose][plano][indice]): pontos
                for pose, plano, indice, pontos in lampas
            }
        return cena
    except (OSError, ValueError, EOFError, pickle.UnpicklingError, AttributeError, TypeError, KeyError):
        # Compatibilidade no caso de instalação incompleta/atlas ausente.
        return ModularBiomeScene(bioma, lightweight=lightweight)
