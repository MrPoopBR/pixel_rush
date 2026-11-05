"""Pixel Rush v3.115.0 — Cidade 2.0 modular e em camadas.

Novo caminho A+B:
- bioma piloto Cidade reconstruido do zero com chunks modulares;
- objetos decorativos separados em sprites;
- multiplas camadas de parallax, dia/noite e pequenas animacoes;
- estrutura generica pronta para expandir aos demais biomas.

Tudo e gerado proceduralmente em superfícies pixel-art de baixa resolucao e
escalado por inteiro, preservando o estilo sem depender de PNG unico estatico.
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import pygame

WIDTH, HEIGHT, TOP, GROUND = 450, 800, 230, 730
SCENE_W, SCENE_H = 900, 500
LOW_W, LOW_H, SCALE = 450, 250, 2
DEFAULT_NORMAL = (128, 128, 255, 255)
NEUTRAL_FLOW = (128, 128, 0, 255)


def clamp(v, a, b):
    return a if v < a else b if v > b else v


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def scale_low(surface: pygame.Surface) -> pygame.Surface:
    return pygame.transform.scale(surface, (surface.get_width() * SCALE, surface.get_height() * SCALE))


@dataclass
class SpriteAsset:
    image: pygame.Surface
    geometry: pygame.Surface
    fxmask: pygame.Surface
    normal: pygame.Surface
    material: pygame.Surface
    flow: pygame.Surface
    anchor_bottom: int = 0


@dataclass
class SpriteInstance:
    kind: str
    x: int
    y: int
    sway: float = 0.0
    bob: float = 0.0
    phase: float = 0.0
    glow: float = 0.0


@dataclass
class ChunkVariant:
    image: pygame.Surface
    geometry: pygame.Surface
    fxmask: pygame.Surface
    normal: pygame.Surface
    material: pygame.Surface
    flow: pygame.Surface
    sprites: List[SpriteInstance] = field(default_factory=list)


@dataclass
class Layer:
    name: str
    speed: float
    step: int
    variants: List[ChunkVariant]
    sequence: Tuple[int, ...]
    flips: Tuple[bool, ...]
    foreground: bool = False


class SpriteLibrary:
    def __init__(self):
        self.assets: Dict[str, SpriteAsset] = {}
        self._build()

    @staticmethod
    def _blank(size):
        return pygame.Surface(size, pygame.SRCALPHA)

    @staticmethod
    def _silhouette_map(src: pygame.Surface, fill_rgba) -> pygame.Surface:
        out = pygame.Surface(src.get_size(), pygame.SRCALPHA)
        alpha = pygame.surfarray.pixels_alpha(src)
        out_alpha = pygame.surfarray.pixels_alpha(out)
        rgb = pygame.surfarray.pixels3d(out)
        mask = alpha > 0
        rgb[:, :, 0][mask] = fill_rgba[0]
        rgb[:, :, 1][mask] = fill_rgba[1]
        rgb[:, :, 2][mask] = fill_rgba[2]
        out_alpha[:, :][mask] = fill_rgba[3] if len(fill_rgba) > 3 else 255
        del alpha, out_alpha, rgb
        return out

    def _make_asset(self, low_image, material_color=(120, 120, 120), fx_builder=None, normal_tint=DEFAULT_NORMAL):
        img = scale_low(low_image)
        geom = scale_low(self._silhouette_map(low_image, (0, 220, 0, 255)))
        fx = scale_low(fx_builder(low_image) if fx_builder else self._blank(low_image.get_size()))
        normal = scale_low(self._silhouette_map(low_image, (*normal_tint[:3], 255)))
        mat = scale_low(self._silhouette_map(low_image, (*material_color, 255)))
        flow = scale_low(self._silhouette_map(low_image, NEUTRAL_FLOW))
        return SpriteAsset(img, geom, fx, normal, mat, flow)

    def _build_tree(self, size=(24, 34), trunk=(95, 66, 53), leaf1=(42, 129, 79), leaf2=(74, 171, 92), big=False):
        w, h = size
        s = self._blank((w, h))
        pygame.draw.rect(s, trunk, (w // 2 - 2, h - 11, 4, 11))
        centers = [(w // 2 - 6, h - 16, 8), (w // 2 + 3, h - 18, 9), (w // 2 - 1, h - 23, 10)]
        if big:
            centers += [(w // 2 - 10, h - 20, 8), (w // 2 + 10, h - 20, 7)]
        for i, (cx, cy, r) in enumerate(centers):
            pygame.draw.circle(s, leaf1 if i % 2 == 0 else leaf2, (cx, cy), r)
        return self._make_asset(s, material_color=(60, 145, 85))

    def _build_lamp(self):
        s = self._blank((14, 32))
        pygame.draw.rect(s, (65, 54, 79), (6, 2, 2, 20))
        pygame.draw.rect(s, (84, 73, 100), (5, 8, 4, 12))
        pygame.draw.rect(s, (255, 218, 119), (4, 11, 6, 7))

        def fx_builder(_):
            out = self._blank((14, 32))
            for r, a in ((9, 40), (6, 84), (3, 180)):
                pygame.draw.circle(out, (255, 212, 92, a), (7, 15), r)
            return out

        return self._make_asset(s, material_color=(140, 122, 104), fx_builder=fx_builder)

    def _build_banner(self, color=(228, 96, 174), accent=(255, 233, 123)):
        s = self._blank((16, 26))
        pygame.draw.rect(s, (60, 52, 83), (0, 0, 2, 26))
        pygame.draw.rect(s, color, (2, 3, 12, 18))
        pygame.draw.polygon(s, color, [(2, 21), (8, 25), (14, 21)])
        pygame.draw.circle(s, accent, (8, 11), 3)
        return self._make_asset(s, material_color=(200, 140, 190))

    def _build_canopy(self):
        s = self._blank((24, 14))
        pygame.draw.rect(s, (89, 63, 90), (0, 6, 24, 2))
        cols = [(255, 200, 99), (255, 233, 196)]
        for i in range(6):
            pygame.draw.rect(s, cols[i % 2], (i * 4, 2, 4, 6))
        return self._make_asset(s, material_color=(220, 188, 125))

    def _build_sign(self):
        s = self._blank((22, 18))
        pygame.draw.rect(s, (66, 58, 92), (0, 2, 22, 14), border_radius=2)
        pygame.draw.rect(s, (255, 155, 130), (2, 4, 18, 10), border_radius=2)
        pygame.draw.rect(s, (223, 237, 112), (7, 6, 8, 6), border_radius=2)

        def fx_builder(_):
            out = self._blank((22, 18))
            pygame.draw.rect(out, (255, 143, 120, 75), (0, 1, 22, 14), border_radius=2)
            pygame.draw.rect(out, (255, 238, 140, 120), (6, 5, 10, 8), border_radius=2)
            return out

        return self._make_asset(s, material_color=(225, 142, 122), fx_builder=fx_builder)

    def _build_train(self):
        s = self._blank((50, 18))
        pygame.draw.rect(s, (70, 121, 218), (0, 4, 50, 10), border_radius=2)
        pygame.draw.rect(s, (220, 234, 255), (5, 6, 8, 4))
        pygame.draw.rect(s, (220, 234, 255), (18, 6, 8, 4))
        pygame.draw.rect(s, (220, 234, 255), (31, 6, 8, 4))
        pygame.draw.rect(s, (255, 214, 96), (0, 8, 50, 1))
        return self._make_asset(s, material_color=(97, 130, 200), fx_builder=None)

    def _build_fg_leaves(self):
        s = self._blank((26, 42))
        for pts in (((2, 12), (15, 2), (22, 12), (15, 28)), ((4, 23), (17, 14), (24, 24), (18, 40))):
            pygame.draw.polygon(s, (33, 61, 47), pts)
        return self._make_asset(s, material_color=(50, 78, 61))

    def _build_bush(self):
        s = self._blank((20, 10))
        pygame.draw.circle(s, (58, 153, 90), (5, 7), 5)
        pygame.draw.circle(s, (73, 174, 96), (10, 5), 5)
        pygame.draw.circle(s, (62, 142, 85), (15, 7), 5)
        return self._make_asset(s, material_color=(60, 145, 85))

    def _build(self):
        self.assets['tree_small'] = self._build_tree()
        self.assets['tree_big'] = self._build_tree(size=(30, 42), big=True)
        self.assets['lamp'] = self._build_lamp()
        self.assets['banner'] = self._build_banner()
        self.assets['canopy'] = self._build_canopy()
        self.assets['sign'] = self._build_sign()
        self.assets['train'] = self._build_train()
        self.assets['fg_leaves'] = self._build_fg_leaves()
        self.assets['bush'] = self._build_bush()


class CityPilotScene:
    """Cena modular Cidade 2.0. Estrutura pronta para outros biomas."""
    def __init__(self):
        self.rand = random.Random(31150)
        self.lib = SpriteLibrary()
        self.layers = self._build_layers()
        self.sky_period = 960
        self._geometry_view = None
        self._last_state = (0.0, 0, 0.0, 'limpo', 0.5)

    def _blank_maps(self):
        blank = pygame.Surface((SCENE_W, SCENE_H), pygame.SRCALPHA)
        normal = pygame.Surface((SCENE_W, SCENE_H), pygame.SRCALPHA)
        normal.fill(DEFAULT_NORMAL)
        flow = pygame.Surface((SCENE_W, SCENE_H), pygame.SRCALPHA)
        flow.fill(NEUTRAL_FLOW)
        return {
            'image': blank.copy(),
            'geometry': blank.copy(),
            'fxmask': blank.copy(),
            'normal': normal,
            'material': blank.copy(),
            'flow': flow,
        }

    def _draw_building(self, maps, x, base_y, w, h, body, shade, roof=None, win_color=(244, 228, 176), win_lit=(255, 231, 115), night=0.0, material=(143, 118, 128)):
        img = maps['image']; geom = maps['geometry']; fx = maps['fxmask']; normal = maps['normal']; mat = maps['material']
        y = base_y - h
        pygame.draw.rect(img, shade, (x + 2, y + 1, w, h))
        pygame.draw.rect(img, body, (x, y, w, h))
        pygame.draw.rect(geom, (0, 220, 0), (x, y, w, h))
        pygame.draw.rect(mat, material, (x, y, w, h))
        if roof == 'spire':
            pygame.draw.polygon(img, tuple(max(0, c - 14) for c in body), [(x + w // 2, y - 12), (x + w // 2 - 4, y), (x + w // 2 + 4, y)])
            pygame.draw.polygon(geom, (0, 220, 0), [(x + w // 2, y - 12), (x + w // 2 - 4, y), (x + w // 2 + 4, y)])
            pygame.draw.polygon(mat, material, [(x + w // 2, y - 12), (x + w // 2 - 4, y), (x + w // 2 + 4, y)])
        elif roof == 'clock':
            pygame.draw.rect(img, (227, 195, 142), (x + w // 2 - 6, y - 10, 12, 10))
            pygame.draw.circle(img, (248, 244, 229), (x + w // 2, y - 5), 3)
        elif roof == 'tower':
            pygame.draw.polygon(img, (184, 124, 113), [(x + 3, y), (x + w // 2, y - 12), (x + w - 3, y)])
        wx = x + 4
        lit_mod = clamp(night * 1.25, 0.0, 1.0)
        while wx < x + w - 6:
            wy = y + 5
            while wy < base_y - 6:
                if (wx + wy) % 7 != 0:
                    lit = ((wx * 3 + wy * 5 + w + h) % 11) < int(2 + lit_mod * 5)
                    color = win_lit if lit else win_color
                    pygame.draw.rect(img, color, (wx, wy, 3, 4))
                    if lit:
                        pygame.draw.rect(fx, (255, 220, 128, int(90 + 120 * lit_mod)), (wx, wy, 3, 4))
                wy += 9
            wx += 8
        # normal map simplificada: esquerda mais fria, direita mais quente
        pygame.draw.rect(normal, (105, 128, 255), (x, y, max(2, w // 3), h))
        pygame.draw.rect(normal, DEFAULT_NORMAL, (x + max(2, w // 3), y, max(2, w // 3), h))
        pygame.draw.rect(normal, (150, 128, 255), (x + max(4, (2 * w) // 3), y, w - max(4, (2 * w) // 3), h))

    def _draw_bridge(self, maps, y, color=(107, 131, 182), depth=(77, 95, 132)):
        img = maps['image']; geom = maps['geometry']; mat = maps['material']; normal = maps['normal']
        pygame.draw.rect(img, color, (0, y, LOW_W, 8))
        pygame.draw.rect(img, depth, (0, y + 8, LOW_W, 3))
        pygame.draw.rect(geom, (0, 210, 0), (0, y, LOW_W, 11))
        pygame.draw.rect(mat, (92, 110, 125), (0, y, LOW_W, 11))
        pygame.draw.rect(normal, DEFAULT_NORMAL, (0, y, LOW_W, 11))
        for ax in range(-10, LOW_W + 30, 36):
            pygame.draw.arc(img, depth, (ax, y + 3, 32, 24), math.pi, math.tau, 2)
            pygame.draw.arc(geom, (0, 210, 0), (ax, y + 3, 32, 24), math.pi, math.tau, 2)
            pygame.draw.arc(mat, (92, 110, 125), (ax, y + 3, 32, 24), math.pi, math.tau, 2)
            pygame.draw.arc(normal, DEFAULT_NORMAL, (ax, y + 3, 32, 24), math.pi, math.tau, 2)

    def _make_far_variant(self, idx: int) -> ChunkVariant:
        maps = self._blank_maps()
        base_y = LOW_H - 22
        rnd = random.Random(1000 + idx)
        palette = [
            ((131, 147, 224), (110, 122, 195)),
            ((177, 184, 238), (142, 151, 216)),
            ((154, 166, 230), (125, 138, 198)),
        ]
        x = 0
        while x < LOW_W + 20:
            w = rnd.randint(16, 32)
            h = rnd.randint(46, 102)
            body, shade = palette[rnd.randrange(len(palette))]
            roof = rnd.choice((None, 'spire', None, None))
            self._draw_building(maps, x, base_y, w, h, body, shade, roof=roof, win_color=(216, 222, 242), win_lit=(255, 238, 162), night=0.0, material=(132, 147, 168))
            x += w - 2
        # nuvens
        for c in range(9):
            cx = rnd.randint(10, LOW_W - 20); cy = rnd.randint(20, 74); r = rnd.randint(8, 16)
            for dx, dy, rr in ((0, 0, r), (-r + 4, 2, r - 2), (r - 3, 4, r - 3), (3, -5, r - 4)):
                pygame.draw.circle(maps['image'], (241, 234, 231), (cx + dx, cy + dy), rr)
        return ChunkVariant(**maps)

    def _make_mid_variant(self, idx: int) -> ChunkVariant:
        maps = self._blank_maps()
        rnd = random.Random(2000 + idx)
        base_y = LOW_H - 6
        # skyline de predios medios
        x = rnd.randint(0, 10)
        colors = [((206, 165, 142), (157, 119, 116)), ((172, 140, 154), (129, 98, 112)), ((204, 188, 154), (163, 146, 116))]
        while x < LOW_W + 10:
            w = rnd.randint(22, 42)
            h = rnd.randint(48, 92)
            body, shade = colors[rnd.randrange(len(colors))]
            roof = rnd.choice((None, 'clock', 'tower', None))
            self._draw_building(maps, x, base_y, w, h, body, shade, roof=roof, win_color=(244, 231, 210), win_lit=(255, 234, 153), night=0.0, material=(164, 136, 118))
            x += w - rnd.randint(2, 6)
        self._draw_bridge(maps, 128 + (idx % 2) * 8, color=(115, 142, 193), depth=(87, 103, 142))
        self._draw_bridge(maps, 172 + (idx % 3) * 4, color=(143, 165, 206), depth=(107, 123, 162))
        # canal/agua distante e faixa urbana
        pygame.draw.rect(maps['image'], (98, 182, 231), (0, LOW_H - 34, LOW_W, 8))
        pygame.draw.rect(maps['material'], (86, 132, 171), (0, LOW_H - 34, LOW_W, 8))
        pygame.draw.rect(maps['flow'], (175, 95, 0), (0, LOW_H - 34, LOW_W, 8))
        pygame.draw.rect(maps['image'], (116, 104, 102), (0, LOW_H - 26, LOW_W, 4))
        pygame.draw.rect(maps['material'], (105, 95, 93), (0, LOW_H - 26, LOW_W, 4))
        return ChunkVariant(**maps)

    def _make_near_variant(self, idx: int) -> ChunkVariant:
        maps = self._blank_maps()
        rnd = random.Random(3000 + idx)
        sprites = []
        # fachadas laterais / centro livre
        side_w = 66 + (idx % 3) * 8
        for left in (0, LOW_W - side_w):
            body = (214, 154, 123) if left == 0 else (200, 148, 126)
            shade = (160, 108, 97)
            self._draw_building(maps, left, LOW_H - 10, side_w, 110 + rnd.randint(-10, 18), body, shade, roof='tower', win_color=(247, 234, 219), win_lit=(255, 239, 145), material=(174, 133, 113))
        # predio central cafe / praça
        center_x = LOW_W // 2 - 34
        self._draw_building(maps, center_x, LOW_H - 5, 68, 96, (187, 137, 120), (144, 97, 89), roof='clock', win_color=(243, 225, 201), win_lit=(255, 228, 132), material=(165, 123, 107))
        # varandas laterais para dar volume sem poluir a pista
        pygame.draw.rect(maps['image'], (161, 121, 109), (22, LOW_H - 70, 56, 8))
        pygame.draw.rect(maps['image'], (158, 114, 102), (LOW_W - 78, LOW_H - 66, 56, 8))
        pygame.draw.rect(maps['geometry'], (0, 210, 0), (22, LOW_H - 70, 56, 8))
        pygame.draw.rect(maps['geometry'], (0, 210, 0), (LOW_W - 78, LOW_H - 66, 56, 8))
        pygame.draw.rect(maps['material'], (155, 118, 104), (22, LOW_H - 70, 56, 8))
        pygame.draw.rect(maps['material'], (155, 118, 104), (LOW_W - 78, LOW_H - 66, 56, 8))
        # calçada / gramado / canteiros
        pygame.draw.rect(maps['image'], (71, 112, 66), (0, LOW_H - 18, LOW_W, 7))
        pygame.draw.rect(maps['image'], (96, 77, 70), (0, LOW_H - 11, LOW_W, 11))
        pygame.draw.rect(maps['geometry'], (0, 210, 0), (0, LOW_H - 18, LOW_W, 18))
        pygame.draw.rect(maps['material'], (70, 120, 74), (0, LOW_H - 18, LOW_W, 7))
        pygame.draw.rect(maps['material'], (101, 83, 75), (0, LOW_H - 11, LOW_W, 11))
        for bed_x in (92, 126, LOW_W - 148, LOW_W - 112):
            pygame.draw.rect(maps['image'], (116, 96, 84), (bed_x, LOW_H - 26, 20, 6))
            pygame.draw.rect(maps['image'], (228, 104, 145), (bed_x + 3, LOW_H - 24, 3, 2))
            pygame.draw.rect(maps['image'], (250, 204, 104), (bed_x + 9, LOW_H - 23, 3, 2))
        # separa decoracoes
        sprites.extend([
            SpriteInstance('tree_big', 34, LOW_H - 11, sway=2.4, phase=.3 + idx),
            SpriteInstance('tree_big', LOW_W - 58, LOW_H - 10, sway=2.0, phase=.8 + idx),
            SpriteInstance('tree_small', 102, LOW_H - 11, sway=1.6, phase=.5 + idx),
            SpriteInstance('tree_small', LOW_W - 116, LOW_H - 11, sway=1.8, phase=1.1 + idx),
            SpriteInstance('lamp', 62, LOW_H - 9, glow=1.0),
            SpriteInstance('lamp', LOW_W - 74, LOW_H - 9, glow=1.0),
            SpriteInstance('lamp', center_x - 22, LOW_H - 8, glow=1.0),
            SpriteInstance('lamp', center_x + 86, LOW_H - 8, glow=1.0),
            SpriteInstance('banner', center_x - 16, LOW_H - 56, sway=1.5, phase=.5),
            SpriteInstance('banner', center_x + 68, LOW_H - 56, sway=1.7, phase=1.3),
            SpriteInstance('banner', 82, LOW_H - 84, sway=1.2, phase=1.8),
            SpriteInstance('banner', LOW_W - 96, LOW_H - 80, sway=1.1, phase=2.2),
            SpriteInstance('canopy', center_x + 20, LOW_H - 72, bob=1.0, phase=.7),
            SpriteInstance('bush', center_x - 16, LOW_H - 10),
            SpriteInstance('bush', center_x + 70, LOW_H - 10),
            SpriteInstance('bush', 14, LOW_H - 10),
            SpriteInstance('bush', LOW_W - 28, LOW_H - 10),
        ])
        return ChunkVariant(**maps, sprites=sprites)

    def _make_fg_variant(self, idx: int) -> ChunkVariant:
        maps = self._blank_maps()
        sprites = [
            SpriteInstance('fg_leaves', 4, 132, sway=2.0, phase=idx * .8),
            SpriteInstance('fg_leaves', 24, 176, sway=1.4, phase=idx * .5),
            SpriteInstance('fg_leaves', LOW_W - 40, 142, sway=2.6, phase=idx * 1.1),
            SpriteInstance('fg_leaves', LOW_W - 58, 186, sway=1.8, phase=idx * .9),
            SpriteInstance('sign', 16, 44, bob=.6, phase=.6 + idx),
            SpriteInstance('sign', LOW_W - 42, 58, bob=.5, phase=1.4 + idx),
        ]
        return ChunkVariant(**maps, sprites=sprites)

    def _build_layers(self) -> List[Layer]:
        far = [self._make_far_variant(i) for i in range(6)]
        mid = [self._make_mid_variant(i) for i in range(6)]
        near = [self._make_near_variant(i) for i in range(6)]
        fg = [self._make_fg_variant(i) for i in range(4)]
        return [
            Layer('far', 0.10, 820, far, (0, 1, 2, 3, 4, 5, 2, 1, 4, 0, 3, 5), (False, False, True, False, True, False, False, True, False, False, True, False)),
            Layer('mid', 0.23, 828, mid, (0, 2, 1, 4, 3, 5, 1, 0, 5, 3, 2, 4), (False, True, False, False, True, False, True, False, False, True, False, False)),
            Layer('near', 0.47, 836, near, (0, 1, 2, 3, 4, 5, 3, 1, 4, 0, 2, 5), (False, False, True, False, False, True, False, True, False, False, True, False)),
            Layer('fg', 1.08, 840, fg, (0, 1, 2, 3, 1, 2, 0, 3), (False, True, False, True, False, False, True, False), foreground=True),
        ]

    def _layer_tiles(self, travel, layer: Layer):
        total = layer.step * len(layer.sequence)
        offset = int(max(0.0, travel) * layer.speed) % total
        first = max(0, (offset - SCENE_W) // layer.step)
        last = min(len(layer.sequence) + 1, (offset + WIDTH + SCENE_W) // layer.step + 1)
        for i in range(first, last + 1):
            seq_i = i % len(layer.sequence)
            x = i * layer.step - offset
            if x <= WIDTH and x + SCENE_W >= 0:
                yield x, layer.variants[layer.sequence[seq_i]], layer.flips[seq_i]

    def _draw_sprite(self, surface, kind, x, y, frame, night, climate, map_kind='image', flip=False):
        asset = self.lib.assets[kind]
        surf = getattr(asset, map_kind)
        if surf is None:
            return
        if flip:
            surf = pygame.transform.flip(surf, True, False)
        rect = surf.get_rect(bottomleft=(x, y))
        surface.blit(surf, rect)
        if map_kind == 'image' and kind == 'lamp' and night > 0.12:
            glow = pygame.Surface((34, 34), pygame.SRCALPHA)
            for r, a in ((16, 16), (11, 28), (6, 58)):
                pygame.draw.circle(glow, (255, 213, 112, int(a * night + 4)), (17, 17), r)
            surface.blit(glow, (rect.centerx - 17, rect.top + 5), special_flags=pygame.BLEND_RGBA_ADD)

    def _render_chunk(self, target, variant: ChunkVariant, flip, x, frame, night, climate, phase, map_kind='image', only_sprites=False):
        base = getattr(variant, map_kind)
        if not only_sprites:
            draw_base = pygame.transform.flip(base, True, False) if flip else base
            target.blit(draw_base, (x, 0))
        for sp in variant.sprites:
            sway = math.sin(frame * 0.03 + sp.phase) * sp.sway
            bob = math.sin(frame * 0.04 + sp.phase) * sp.bob
            wind_boost = 1.7 if climate in ('vento', 'tempestade', 'tempestade_areia', 'nevasca') else 1.0
            px = x + (SCENE_W - sp.x - 10 if flip else sp.x) + int(round(sway * wind_boost))
            py = sp.y + int(round(bob))
            # foreground nao pode poluir centro: so desenha se visivel.
            if px > WIDTH + 60 or px < -80:
                continue
            self._draw_sprite(target, sp.kind, px, py * SCALE, frame, night, climate, map_kind=map_kind, flip=flip and sp.kind not in ('lamp',))

    def _draw_sky(self, target, travel, frame, night, phase, climate):
        day_top = (82, 171, 255); day_horizon = (237, 226, 208)
        eve_top = (54, 91, 171); eve_horizon = (255, 183, 137)
        night_top = (26, 31, 59); night_horizon = (72, 61, 106)
        dusk = abs(phase - 0.5) * 2.0
        dusk_mix = clamp(1.0 - dusk, 0.0, 1.0)
        top = lerp_color(lerp_color(day_top, eve_top, dusk_mix), night_top, night)
        horizon = lerp_color(lerp_color(day_horizon, eve_horizon, dusk_mix), night_horizon, night)
        for y in range(SCENE_H):
            t = y / float(SCENE_H - 1)
            color = lerp_color(top, horizon, min(1.0, t * 1.15))
            pygame.draw.line(target, color, (0, y), (WIDTH, y))
        # sol/lua do jogo: unico corpo celeste, transicao por cor/alpha.
        celestial_x = int((90 - travel * 0.02) % (WIDTH + 120)) - 60
        celestial_y = 58 + int(math.sin(frame * 0.005) * 4)
        if night < 0.55:
            pygame.draw.circle(target, (255, 240, 120), (celestial_x, celestial_y), 24)
            pygame.draw.circle(target, (255, 211, 115, 65), (celestial_x, celestial_y), 34)
        else:
            pygame.draw.circle(target, (232, 238, 255), (celestial_x, celestial_y), 22)
            pygame.draw.circle(target, (219, 228, 255, 65), (celestial_x, celestial_y), 32)
            pygame.draw.circle(target, tuple(list(top) + [255]) if len(top) == 4 else top, (celestial_x + 8, celestial_y - 6), 18)
        # nuvens suaves
        cloud_color = lerp_color((255, 243, 236), (109, 99, 141), night)
        speed = travel * 0.06
        for i in range(7):
            cx = int((i * 96 - speed + (i % 3) * 17) % (WIDTH + 120)) - 60
            cy = 44 + (i % 3) * 26 + int(math.sin(frame * 0.01 + i) * 2)
            for dx, dy, r in ((0, 0, 16), (-14, 4, 12), (14, 5, 11), (6, -6, 10)):
                pygame.draw.circle(target, cloud_color, (cx + dx, cy + dy), r)
        if climate in ('chuva', 'tempestade'):
            veil = pygame.Surface((WIDTH, SCENE_H), pygame.SRCALPHA)
            veil.fill((60, 74, 103, 28 if climate == 'chuva' else 44))
            target.blit(veil, (0, 0))

    def _draw_train(self, target, travel, frame, night, map_kind='image'):
        asset = self.lib.assets['train']
        surf = getattr(asset, map_kind)
        x = int((WIDTH + 90) - (frame * 3.1 % (WIDTH + 180)))
        y = 124 * SCALE
        if map_kind == 'image' and night > 0.10:
            glow = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
            glow.fill((255, 232, 160, int(18 + 34 * night)))
            target.blit(glow, (x, y), special_flags=pygame.BLEND_RGBA_ADD)
        target.blit(surf, (x, y))

    def render_scene(self, target: pygame.Surface, travel: float, frame: int, night: float, climate: str, phase: float, foreground_only=False, map_kind='image'):
        if not foreground_only:
            if map_kind == 'image':
                self._draw_sky(target, travel, frame, night, phase, climate)
            elif map_kind == 'normal':
                target.fill(DEFAULT_NORMAL)
            elif map_kind == 'flow':
                target.fill(NEUTRAL_FLOW)
            else:
                target.fill((0, 0, 0, 0))
        for layer in self.layers:
            if foreground_only != layer.foreground:
                continue
            for x, variant, flip in self._layer_tiles(travel, layer):
                self._render_chunk(target, variant, flip, int(x), frame, night, climate, phase, map_kind=map_kind)
            if layer.name == 'mid' and not foreground_only:
                self._draw_train(target, travel, frame, night, map_kind=map_kind)
        if map_kind == 'image' and not foreground_only and night > 0.18:
            overlay = pygame.Surface((WIDTH, SCENE_H), pygame.SRCALPHA)
            overlay.fill((28, 29, 64, int(70 * night)))
            target.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        if map_kind == 'image' and not foreground_only and climate in ('tempestade', 'chuva'):
            for i in range(34 if climate == 'tempestade' else 22):
                x = int((i * 37 - frame * (6.5 if climate == 'tempestade' else 3.4)) % (WIDTH + 30)) - 15
                y = int((i * 43 + frame * 7.2) % SCENE_H)
                pygame.draw.line(target, (160, 209, 250, 100), (x, y), (x - 6, y + 13), 1)
        self._last_state = (travel, frame, night, climate, phase)
        if map_kind == 'geometry' and not foreground_only:
            self._geometry_view = target.copy()

    def ambient_occlusion(self, source_x, listener_x=90, source_y=490, listener_y=652):
        if self._geometry_view is None:
            return 0.0
        geom = self._geometry_view
        blocked = 0.0; steps = 20
        y0 = max(0, min(geom.get_height() - 1, int(source_y - TOP)))
        y1 = max(0, min(geom.get_height() - 1, int(listener_y - TOP)))
        for n in range(1, steps):
            r = n / float(steps)
            x = int(listener_x + (source_x - listener_x) * r)
            y = int(y1 + (y0 - y1) * r)
            if 0 <= x < geom.get_width() and 0 <= y < geom.get_height():
                c = geom.get_at((x, y)).g / 255.0
                blocked += max(0.0, c - 0.30)
        return min(0.85, blocked / (steps - 1) * 1.25)
