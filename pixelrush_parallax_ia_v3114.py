"""Parallax IA v3.114.0, laboratorio opcional e cache de atlas por cena.

A pintura aprovada e sempre o padrao; nunca requer PyTorch em runtime.
Manifestos com hashes, dimensoes e coordenadas impedem recursos incorretos.
Atlas evita abrir cada PNG separado e cacheia as versoes espelhadas dos
sprites uma unica vez. Dois biomas mantidos em RAM no maximo.
"""
import hashlib
import json
import math
import os
from collections import OrderedDict
from pathlib import Path
import pygame
from pixelrush_chunks_v3113 import CHUNK_STEP, CHUNK_OVERLAP, CHUNK_MIRRORS, visible_chunks

HERE = Path(__file__).resolve().parent
ART = HERE / 'world_art_v3106'
LAYERS = HERE / 'world_parallax_v3112'
REVISADOS = {'cidade', 'deserto', 'floresta', 'cidade_futurista'}

class ParallaxIA:
    """Ativa somente com PIXELRUSH_PARALLAX_IA=1/all e fora do modo leve."""
    def __init__(self, lightweight=False):
        flag = os.environ.get('PIXELRUSH_PARALLAX_IA', '0').lower().strip()
        self.enabled = flag in ('1', 'true', 'on', 'all') and not lightweight
        self.review_all = flag == 'all'
        self.cache = OrderedDict()
        self._atlas_pages = {}
        self._atlas_index = None
        self.stats = {'atlas_pages_loaded': 0, 'sprite_png_reads': 0, 'sprite_flips': 0, 'qa_rejected': 0}
        self._certificates = None

    def _verify_reconstructed_background(self, biome, base_file, original_file):
        """Checks offline QA certificates only when experimental art is requested.

        Kept out of default rendering and off the 60 FPS hot path; no heavy
        dependencies or neural models are loaded on Android/PC at runtime.
        """
        if self._certificates is None:
            cert_file = LAYERS / 'qa_certificados_v3114.json'
            content = json.loads(cert_file.read_text(encoding='utf-8'))
            if content.get('schema') != 'pixelrush-qa-v3114':
                raise ValueError('Versao inesperada dos certificados QA')
            self._certificates = content['biomes']
        cert = self._certificates.get(biome)
        if not cert or not cert.get('automatic_checks_passed'):
            raise ValueError('Fundo experimental sem certificado QA v3114')
        if hashlib.sha256(original_file.read_bytes()).hexdigest() != cert['source_sha256']:
            raise ValueError('Pintura nao corresponde ao certificado QA')
        if hashlib.sha256(base_file.read_bytes()).hexdigest() != cert['base_sha256']:
            raise ValueError('Fundo experimental modificado apos o QA')
        if cert['old_new_artificial_white_pixels'][1] != 0:
            raise ValueError('QA identifica brilho artificial residual')

    def _index(self):
        if self._atlas_index is None:
            manifest = LAYERS / 'atlas_manifest.json'
            raw = json.loads(manifest.read_text(encoding='utf-8'))
            if raw.get('type') != 'ATLAS_EXPERIMENTAL' or raw.get('atlas_size') != [512, 512]:
                raise ValueError('Atlas experimental inesperado')
            names = raw['atlases']
            if not names or len(names) > 4 or any(Path(name).name != name for name in names):
                raise ValueError('Indice do atlas invalido')
            index = {}
            for entry in raw['sprites']:
                key = (entry['biome'], int(entry['sprite_index']))
                if key in index:
                    raise ValueError('Sprite duplicado no indice de atlas')
                index[key] = entry
            self._atlas_index = (names, index)
        return self._atlas_index

    def _sprite_from_atlas(self, biome, i, obj):
        names, refs = self._index()
        ref = refs[(biome, i)]
        rect = tuple(int(v) for v in ref['atlas_rect'])
        if ref['world_rect'] != obj['rect'] or len(rect) != 4:
            raise ValueError('Atlas aponta para outra regiao original')
        px, py, w, h = rect
        if min(px, py) < 0 or w <= 0 or h <= 0 or px + w > 512 or py + h > 512:
            raise ValueError('Atlas fora dos limites')
        pg = int(ref['atlas_page'])
        if pg < 0 or pg >= len(names):
            raise ValueError('Pagina invalida do atlas')
        if pg not in self._atlas_pages:
            atlas = pygame.image.load(str(LAYERS / names[pg])).convert_alpha()
            if atlas.get_size() != (512, 512):
                raise ValueError('Dimensoes divergentes de atlas')
            self._atlas_pages[pg] = atlas
            self.stats['atlas_pages_loaded'] += 1
        sprite = self._atlas_pages[pg].subsurface(pygame.Rect(px, py, w, h)).copy()
        return sprite

    def data(self, biome):
        if not self.enabled or (not self.review_all and biome not in REVISADOS):
            return None
        if biome in self.cache:
            self.cache.move_to_end(biome)
            return self.cache[biome]
        file = LAYERS / (biome + '.json')
        if not file.exists():
            return None
        result = None
        try:
            meta = json.loads(file.read_text(encoding='utf-8'))
            original = ART / (biome + '.png')
            if hashlib.sha256(original.read_bytes()).hexdigest() != meta['sources_sha256']:
                raise ValueError('Integridade da pintura aprovada divergente')
            if meta['biome'] != biome or not meta.get('qa_automatic_passed'):
                raise ValueError('Manifesto sem QA ou bioma diferente')
            base_file = LAYERS / meta['base']
            if base_file.name != meta['base']:
                raise ValueError('Caminho do fundo invalido')
            self._verify_reconstructed_background(biome, base_file, original)
            base = pygame.image.load(str(base_file)).convert_alpha()
            if base.get_size() != (900, 500):
                raise ValueError('Fundo de tamanho inesperado')
            sprites = []
            for i, obj in enumerate(meta['sprites'][:2]):
                x, y, w, h = [int(v) for v in obj['rect']]
                if min(x, y) < 0 or min(w, h) < 1 or x + w > 900 or y + h > 500:
                    raise ValueError('Recorte fora da pintura')
                sprite = self._sprite_from_atlas(biome, i, obj)
                if sprite.get_size() != (w, h):
                    raise ValueError('Sprite com tamanho divergente')
                # O flip nao acontece durante a corrida: economia de CPU, mesmo
                # quando o plano aparece repetido em varios chunks.
                flipped = pygame.transform.flip(sprite, True, False)
                self.stats['sprite_flips'] += 1
                # Elementos arquitetonicos e presos ao fundo; elementos leves
                # podem oscilar no maximo 2 pixels, sem drift acumulativo.
                role = str(obj.get('role', 'decoracao'))
                speed = float(obj['parallax_speed'])
                amp = 0.0 if role in ('arquitetura', 'estrutura', 'ancorado') else min(2.0, max(0.4, abs(speed - .235) * 100.0))
                sprites.append((sprite, flipped, (x, y, w, h), amp))
            result = {'base': base, 'sprites': sprites}
        except (OSError, ValueError, KeyError, IndexError, pygame.error, TypeError) as exc:
            self.stats['qa_rejected'] += 1
            print('[Pixel Rush v3.114 QA] Pintura original mantida: ' + str(exc))
        self.cache[biome] = result
        self.cache.move_to_end(biome)
        while len(self.cache) > 2:
            self.cache.popitem(last=False)
        return result

    def source(self, biome):
        data = self.data(biome)
        return data['base'] if data else None

    def draw(self, surface, biome, travel, top):
        data = self.data(biome)
        if not data:
            return
        view_w = surface.get_width()
        for chunk, mirror, x0 in visible_chunks(travel, .235, view_w):
            for j, (sprite, flip, (x, y, w, h), amplitude) in enumerate(data['sprites']):
                # Nao duplicar recortes na costura de 48 pixels.
                # A camada original continua desenhada por baixo se for limiar.
                local_x = 900 - x - w if mirror else x
                if local_x < CHUNK_OVERLAP or local_x + w > CHUNK_STEP:
                    continue
                dx = int(round(amplitude * math.sin(travel * .005 + j * 1.2 + (chunk % len(CHUNK_MIRRORS)) * .1))) if amplitude else 0
                if mirror:
                    dx = -dx
                px = x0 + local_x + dx
                if px > view_w or px + w < 0:
                    continue
                surface.blit(flip if mirror else sprite, (px, top + y))
