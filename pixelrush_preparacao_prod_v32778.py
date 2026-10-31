"""v3.277.8-PROD: prepara SOMENTE assets já existentes, sem alterar algoritmos.

Áudio e cinemática: buffers e RGBA gerados offline pelo código original.
Atlas: leitura e SHA-256 antecipados em thread de I/O; a thread não usa pygame.
A restauração de superfícies continua no thread principal; arquivo ausente ou
não validado recai nas rotinas exatas da v3.277.7. Não altera gameplay/ticks.
"""
from pathlib import Path
import hashlib
import json
import os
import pickle
import threading
import zlib
import pygame

_BIOMAS = frozenset(('cidade', 'neve', 'cidade_futurista', 'deserto'))
_DIR = Path(__file__).resolve().parent / 'assets' / 'preparacao_prod_v32778'
_ATLAS_OK = {}
_MANIFESTO = None


def _manifesto():
    global _MANIFESTO
    if _MANIFESTO is None:
        try:
            _MANIFESTO = json.loads((_DIR / 'manifesto.json').read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            _MANIFESTO = {'assets': {}}
    return _MANIFESTO


def _carregar(nome):
    """Validação SHA dos binários de release; fallback se faltar/corromper."""
    info = _manifesto()['assets'].get(nome)
    if not info:
        return None
    try:
        data = (_DIR / nome).read_bytes()
        if hashlib.sha256(data).hexdigest() != info['sha256']:
            return None
        raw = zlib.decompress(data)
        if len(raw) != info['raw_size'] or hashlib.sha256(raw).hexdigest() != info['raw_sha256']:
            return None
        return raw, info
    except (OSError, KeyError, zlib.error, ValueError, TypeError):
        return None


def instalar():
    """Chamado uma vez após a inicialização de Pygame."""
    from pixelrush_extras_v3174 import PaisagemSonora
    from pixelrush_cinema_v3172 import CenasCinematograficas
    from pixelrush_cenas_v3213 import CenasMemoraveis
    import pixelrush_atlas_prod_v32776 as atlas
    import pixelrush_world_v3185 as motor

    if getattr(PaisagemSonora, '_prod_2778', False):
        return
    original_som = PaisagemSonora._som
    original_marco = CenasCinematograficas._criar
    original_lamina = CenasMemoraveis._construir
    def som(self, bioma):
        if bioma in self.sons:
            return self.sons[bioma]
        spec = pygame.mixer.get_init()
        if bioma in _BIOMAS and spec and tuple(spec) in ((22050, -16, 2), (44100, -16, 2)):
            nome = 'audio_' + bioma + ('_44100' if spec[0] == 44100 else '') + '.pcmz'
            entrada = _carregar(nome)
            if entrada is not None:
                try:
                    sound = pygame.mixer.Sound(buffer=entrada[0])
                    self.sons[bioma] = sound
                    return sound
                except pygame.error:
                    pass
        return original_som(self, bioma)

    def imagem_preparada(nome):
        entrada = _carregar(nome)
        if entrada is None:
            return None
        raw, info = entrada
        tamanho = info.get('dimensions')
        if not tamanho or len(raw) != 4 * tamanho[0] * tamanho[1]:
            return None
        try:
            return pygame.image.frombytes(raw, tamanho, 'RGBA')
        except (ValueError, pygame.error):
            return None

    def marco(self, bioma):
        pronto = imagem_preparada('marco_' + bioma + '.rgbaz') if bioma in _BIOMAS else None
        return pronto if pronto is not None else original_marco(self, bioma)

    def lamina(bioma, etapa, variante):
        pronto = (imagem_preparada('lamina%d_%d_%s.rgbaz' % (etapa, variante, bioma))
                  if bioma in _BIOMAS else None)
        return pronto if pronto is not None else original_lamina(bioma, etapa, variante)

    PaisagemSonora._som = som
    PaisagemSonora._prod_2778 = True
    CenasCinematograficas._criar = marco
    CenasMemoraveis._construir = staticmethod(lamina)

    # Somente I/O + SHA-256 em segundo plano; nenhuma Surface/SDL na thread.
    # A função de carregamento usa a verificação original se o aquecimento
    # ainda não tiver terminado ou se um arquivo for alterado.
    def antecipar_verificacoes():
        for nome, esperado in atlas._HASHES.items():
            path = atlas._ATLAS / (nome + '.atlas')
            try:
                before = path.stat()
                with path.open('rb') as fd:
                    digest = hashlib.file_digest(fd, 'sha256').hexdigest()
                after = path.stat()
                if (digest == esperado and before.st_size == after.st_size and
                    before.st_mtime_ns == after.st_mtime_ns):
                    _ATLAS_OK[nome] = (after.st_size, after.st_mtime_ns)
            except OSError:
                continue
    threading.Thread(target=antecipar_verificacoes, name='pixelrush-atlas-prefetch', daemon=True).start()

    # Versão original byte-a-byte equivalente, evitando re-hash no primeiro
    # frame apenas quando a verificação SHA já terminou e o arquivo não mudou.
    original_cena = atlas.carregar_cena
    def cena(bioma, lightweight=False):
        nome = f'{bioma}_lite' if lightweight else bioma
        ok = _ATLAS_OK.get(nome)
        if not ok:
            return original_cena(bioma, lightweight)
        path = atlas._ATLAS / (nome + '.atlas')
        try:
            st = path.stat()
            if (st.st_size, st.st_mtime_ns) != ok:
                return original_cena(bioma, lightweight)
            with path.open('rb') as arquivo:
                estado = pickle.load(arquivo)
            if estado.get('biome') != bioma:
                raise ValueError('bioma incorreto')
            classe = atlas.ModularBiomeScene
            instancia = classe.__new__(classe)
            lampas = estado.pop('_lampas_indexadas_v32776', ())
            instancia.__dict__.update(estado)
            if bioma == 'cidade_futurista':
                instancia._build_global_overlays()
            if bioma == 'deserto':
                instancia._lamp_pixels = {
                    id(instancia._poses[pose][plano][indice]): pontos
                    for pose, plano, indice, pontos in lampas
                }
            return instancia
        except (OSError, ValueError, EOFError, pickle.UnpicklingError,
                AttributeError, TypeError, KeyError, IndexError):
            return original_cena(bioma, lightweight)
    motor.ModularBiomeScene = cena
