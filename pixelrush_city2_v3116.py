"""Pixel Rush v3.116.0 — Cidade 2.1 mais refinada.

Refino da Cidade 2.0 com foco em:
- maior riqueza visual dos chunks;
- mais variedade de fachadas e blocos centrais;
- elementos urbanos separados em sprites;
- mais vida na cena: passarinhos, tráfego distante, reflexos e brilho noturno;
- base modular preservada para expansão dos próximos biomas.
"""
from __future__ import annotations
import math
import random
import pygame
from pixelrush_city2_v3115 import (
    CityPilotScene as BaseCityPilotScene,
    SpriteLibrary as BaseSpriteLibrary,
    SpriteInstance, ChunkVariant, Layer,
    WIDTH, HEIGHT, TOP, GROUND, SCENE_W, SCENE_H, LOW_W, LOW_H, SCALE,
    DEFAULT_NORMAL, NEUTRAL_FLOW,
    clamp, lerp, lerp_color,
)


class SpriteLibraryPro(BaseSpriteLibrary):
    def _build_bench(self):
        s = self._blank((24, 14))
        pygame.draw.rect(s, (134, 87, 66), (3, 6, 18, 3))
        pygame.draw.rect(s, (154, 104, 81), (3, 2, 18, 3))
        pygame.draw.rect(s, (76, 63, 72), (5, 9, 2, 5))
        pygame.draw.rect(s, (76, 63, 72), (17, 9, 2, 5))
        return self._make_asset(s, material_color=(120, 88, 76))

    def _build_kiosk(self):
        s = self._blank((24, 24))
        pygame.draw.rect(s, (96, 71, 86), (2, 8, 20, 14))
        pygame.draw.rect(s, (255, 206, 102), (0, 6, 24, 3))
        pygame.draw.rect(s, (247, 238, 223), (5, 11, 14, 8))
        pygame.draw.rect(s, (231, 103, 141), (7, 13, 10, 2))
        return self._make_asset(s, material_color=(173, 128, 116))

    def _build_pennant(self):
        s = self._blank((28, 12))
        pygame.draw.line(s, (70, 63, 93), (0, 1), (27, 1), 1)
        colors = [(255, 197, 102), (238, 98, 145), (111, 199, 238), (169, 221, 104)]
        for i, x in enumerate((2, 8, 14, 20)):
            pygame.draw.polygon(s, colors[i % len(colors)], [(x, 2), (x + 4, 2), (x + 2, 8)])
        return self._make_asset(s, material_color=(180, 150, 124))

    def _build_bird(self):
        s = self._blank((12, 8))
        pygame.draw.arc(s, (62, 55, 66), (0, 2, 6, 4), 3.14, 6.0, 1)
        pygame.draw.arc(s, (62, 55, 66), (5, 1, 6, 5), 3.4, 6.2, 1)
        return self._make_asset(s, material_color=(70, 70, 84))

    def _build(self):
        super()._build()
        self.assets['bench'] = self._build_bench()
        self.assets['kiosk'] = self._build_kiosk()
        self.assets['pennant'] = self._build_pennant()
        self.assets['bird'] = self._build_bird()


class CityPilotScene(BaseCityPilotScene):
    def __init__(self):
        super().__init__()
        self.lib = SpriteLibraryPro()
        self.layers = self._build_layers()

    def _draw_shopfront(self, maps, x, y, w, palette, striped=False):
        img = maps['image']; geom = maps['geometry']; mat = maps['material']; fx = maps['fxmask']
        wall, awn_dark, awn_light = palette
        pygame.draw.rect(img, wall, (x, y, w, 18))
        pygame.draw.rect(geom, (0, 210, 0), (x, y, w, 18))
        pygame.draw.rect(mat, wall, (x, y, w, 18))
        # vitrine
        pygame.draw.rect(img, (245, 240, 234), (x + 2, y + 5, w - 4, 10))
        pygame.draw.rect(img, (190, 221, 241), (x + 3, y + 6, w - 6, 8))
        pygame.draw.rect(fx, (255, 240, 160, 46), (x + 3, y + 6, w - 6, 8))
        # toldo
        for i in range(0, w, 4):
            col = awn_dark if (i // 4) % 2 == 0 or not striped else awn_light
            pygame.draw.rect(img, col, (x + i, y + 1, min(4, w - i), 4))

    def _draw_promenade(self, maps, start_x, end_x):
        img = maps['image']; mat = maps['material']
        for x in range(start_x, end_x, 12):
            pygame.draw.rect(img, (121, 111, 106), (x, LOW_H - 15, 8, 2))
            pygame.draw.rect(mat, (111, 102, 96), (x, LOW_H - 15, 8, 2))

    def _draw_reflection_strip(self, maps, y):
        img = maps['image']; fx = maps['fxmask']
        for x in range(0, LOW_W, 20):
            w = 10 + ((x // 20) % 3) * 4
            pygame.draw.rect(img, (136, 207, 241), (x, y, w, 1))
            pygame.draw.rect(fx, (180, 230, 255, 32), (x, y, w, 1))

    def _make_far_variant(self, idx: int) -> ChunkVariant:
        maps = self._blank_maps()
        base_y = LOW_H - 24
        rnd = random.Random(4100 + idx)
        palette = [
            ((137, 154, 231), (111, 125, 199)),
            ((172, 181, 236), (142, 152, 210)),
            ((156, 170, 240), (122, 139, 207)),
            ((184, 192, 242), (152, 159, 219)),
        ]
        x = 0
        while x < LOW_W + 18:
            w = rnd.randint(16, 28)
            h = rnd.randint(52, 118)
            body, shade = palette[rnd.randrange(len(palette))]
            roof = rnd.choice((None, 'spire', None, None, 'spire'))
            self._draw_building(maps, x, base_y, w, h, body, shade, roof=roof, win_color=(219, 224, 245), win_lit=(255, 241, 166), night=0.0, material=(140, 152, 176))
            # antenas/pinaculos simples
            if rnd.random() < 0.32:
                pygame.draw.line(maps['image'], (120, 135, 182), (x + w // 2, base_y - h), (x + w // 2, base_y - h - 8), 1)
            x += w - rnd.randint(0, 3)
        for c in range(10):
            cx = rnd.randint(12, LOW_W - 18); cy = rnd.randint(18, 76); r = rnd.randint(9, 17)
            col = (246, 238, 233)
            for dx, dy, rr in ((0, 0, r), (-r + 4, 2, r - 2), (r - 3, 4, r - 3), (3, -5, r - 4)):
                pygame.draw.circle(maps['image'], col, (cx + dx, cy + dy), rr)
        return ChunkVariant(**maps)

    def _make_mid_variant(self, idx: int) -> ChunkVariant:
        maps = self._blank_maps()
        rnd = random.Random(5100 + idx)
        base_y = LOW_H - 10
        x = rnd.randint(0, 8)
        colors = [((210, 172, 150), (161, 124, 118)), ((181, 147, 164), (137, 106, 120)), ((208, 192, 160), (169, 149, 120)), ((194, 170, 187), (146, 121, 139))]
        while x < LOW_W + 10:
            w = rnd.randint(22, 44)
            h = rnd.randint(50, 96)
            body, shade = colors[rnd.randrange(len(colors))]
            roof = rnd.choice((None, 'clock', 'tower', None, 'spire'))
            self._draw_building(maps, x, base_y, w, h, body, shade, roof=roof, win_color=(244, 231, 210), win_lit=(255, 234, 153), night=0.0, material=(170, 142, 123))
            if rnd.random() < 0.28:
                self._draw_shopfront(maps, x + 2, base_y - 18, max(16, w - 4), ((190, 136, 116), (255, 212, 116), (248, 240, 227)), striped=True)
            x += w - rnd.randint(2, 5)
        self._draw_bridge(maps, 124 + (idx % 2) * 8, color=(113, 142, 194), depth=(87, 103, 143))
        self._draw_bridge(maps, 171 + (idx % 3) * 5, color=(147, 172, 212), depth=(109, 125, 162))
        # canal mais rico
        pygame.draw.rect(maps['image'], (96, 181, 231), (0, LOW_H - 36, LOW_W, 10))
        pygame.draw.rect(maps['material'], (88, 133, 174), (0, LOW_H - 36, LOW_W, 10))
        pygame.draw.rect(maps['flow'], (175, 95, 0), (0, LOW_H - 36, LOW_W, 10))
        pygame.draw.rect(maps['image'], (116, 103, 100), (0, LOW_H - 26, LOW_W, 4))
        self._draw_reflection_strip(maps, LOW_H - 33)
        return ChunkVariant(**maps)

    def _make_near_variant(self, idx: int) -> ChunkVariant:
        maps = self._blank_maps()
        rnd = random.Random(6100 + idx)
        sprites = []
        style = idx % 4
        side_w = 64 + (idx % 3) * 10
        side_palettes = [((218, 156, 124), (160, 108, 98)), ((200, 153, 140), (150, 112, 106)), ((221, 169, 132), (173, 123, 101))]
        left_pal = side_palettes[idx % len(side_palettes)]
        right_pal = side_palettes[(idx + 1) % len(side_palettes)]
        self._draw_building(maps, 0, LOW_H - 10, side_w, 112 + rnd.randint(-6, 22), left_pal[0], left_pal[1], roof='tower', win_color=(247, 234, 219), win_lit=(255, 239, 145), material=(174, 133, 113))
        self._draw_building(maps, LOW_W - side_w, LOW_H - 10, side_w, 108 + rnd.randint(-6, 18), right_pal[0], right_pal[1], roof='tower', win_color=(247, 234, 219), win_lit=(255, 239, 145), material=(174, 133, 113))
        center_x = LOW_W // 2 - 36
        if style == 0:
            # praça/café
            self._draw_building(maps, center_x, LOW_H - 4, 72, 98, (189, 141, 122), (145, 100, 91), roof='clock', win_color=(244, 225, 198), win_lit=(255, 229, 134), material=(166, 124, 108))
            self._draw_shopfront(maps, center_x + 6, LOW_H - 34, 60, ((204, 151, 124), (255, 200, 101), (248, 240, 228)), striped=True)
            sprites += [
                SpriteInstance('canopy', center_x + 20, LOW_H - 74, bob=0.8, phase=.7),
                SpriteInstance('bench', center_x - 26, LOW_H - 9),
                SpriteInstance('bench', center_x + 82, LOW_H - 9),
                SpriteInstance('pennant', center_x + 20, LOW_H - 86, sway=1.2, phase=0.8),
            ]
        elif style == 1:
            # galeria/mercado
            self._draw_building(maps, center_x - 12, LOW_H - 4, 96, 88, (179, 132, 140), (132, 94, 106), roof=None, win_color=(240, 226, 202), win_lit=(255, 227, 132), material=(160, 121, 127))
            self._draw_shopfront(maps, center_x - 6, LOW_H - 31, 34, ((184, 136, 116), (233, 100, 146), (248, 240, 228)), striped=True)
            self._draw_shopfront(maps, center_x + 32, LOW_H - 31, 40, ((184, 136, 116), (112, 198, 232), (248, 240, 228)), striped=True)
            sprites += [
                SpriteInstance('kiosk', center_x + 34, LOW_H - 9),
                SpriteInstance('bench', center_x - 30, LOW_H - 9),
                SpriteInstance('pennant', center_x + 14, LOW_H - 78, sway=1.0, phase=1.1),
            ]
        elif style == 2:
            # boulevard/com varandas
            self._draw_building(maps, center_x - 4, LOW_H - 6, 84, 108, (201, 152, 127), (157, 109, 95), roof='tower', win_color=(243, 228, 205), win_lit=(255, 231, 140), material=(174, 130, 110))
            pygame.draw.rect(maps['image'], (160, 121, 107), (center_x + 8, LOW_H - 72, 68, 8))
            pygame.draw.rect(maps['geometry'], (0,210,0), (center_x + 8, LOW_H - 72, 68, 8))
            self._draw_shopfront(maps, center_x + 10, LOW_H - 32, 62, ((191, 140, 116), (255, 205, 113), (246, 236, 224)), striped=False)
            sprites += [
                SpriteInstance('banner', center_x - 12, LOW_H - 62, sway=1.3, phase=0.4),
                SpriteInstance('banner', center_x + 82, LOW_H - 62, sway=1.4, phase=1.4),
                SpriteInstance('bench', center_x - 26, LOW_H - 9),
            ]
        else:
            # estação/câmara
            self._draw_building(maps, center_x - 6, LOW_H - 4, 86, 92, (174, 144, 166), (134, 108, 128), roof='clock', win_color=(242, 229, 207), win_lit=(255, 235, 150), material=(154, 132, 146))
            pygame.draw.rect(maps['image'], (150, 115, 136), (center_x + 8, LOW_H - 56, 62, 8))
            pygame.draw.rect(maps['image'], (231, 184, 194), (center_x + 14, LOW_H - 52, 50, 4))
            sprites += [
                SpriteInstance('kiosk', center_x + 26, LOW_H - 9),
                SpriteInstance('bench', center_x - 28, LOW_H - 9),
                SpriteInstance('pennant', center_x + 16, LOW_H - 82, sway=1.2, phase=2.1),
            ]
        # varandas laterais coesas
        pygame.draw.rect(maps['image'], (160, 120, 108), (18, LOW_H - 68, side_w - 10, 8))
        pygame.draw.rect(maps['image'], (157, 114, 103), (LOW_W - side_w + 8, LOW_H - 66, side_w - 12, 8))
        pygame.draw.rect(maps['geometry'], (0,210,0), (18, LOW_H - 68, side_w - 10, 8))
        pygame.draw.rect(maps['geometry'], (0,210,0), (LOW_W - side_w + 8, LOW_H - 66, side_w - 12, 8))
        # base de passeio
        pygame.draw.rect(maps['image'], (66, 112, 70), (0, LOW_H - 20, LOW_W, 8))
        pygame.draw.rect(maps['image'], (121, 107, 99), (0, LOW_H - 12, LOW_W, 12))
        pygame.draw.rect(maps['geometry'], (0,210,0), (0, LOW_H - 20, LOW_W, 20))
        pygame.draw.rect(maps['material'], (69, 119, 73), (0, LOW_H - 20, LOW_W, 8))
        pygame.draw.rect(maps['material'], (109, 97, 92), (0, LOW_H - 12, LOW_W, 12))
        self._draw_promenade(maps, 0, LOW_W)
        for bed_x in (92, 126, LOW_W - 148, LOW_W - 112, 196, 228):
            pygame.draw.rect(maps['image'], (120, 98, 86), (bed_x, LOW_H - 27, 20, 6))
            pygame.draw.rect(maps['image'], (228, 104, 145), (bed_x + 3, LOW_H - 24, 3, 2))
            pygame.draw.rect(maps['image'], (250, 204, 104), (bed_x + 9, LOW_H - 23, 3, 2))
            pygame.draw.rect(maps['image'], (118, 210, 134), (bed_x + 13, LOW_H - 24, 3, 2))
        # sprites comuns
        sprites.extend([
            SpriteInstance('tree_big', 30, LOW_H - 10, sway=2.5, phase=.3 + idx),
            SpriteInstance('tree_big', LOW_W - 60, LOW_H - 10, sway=2.1, phase=.8 + idx),
            SpriteInstance('tree_small', 98, LOW_H - 10, sway=1.7, phase=.5 + idx),
            SpriteInstance('tree_small', LOW_W - 116, LOW_H - 10, sway=1.8, phase=1.1 + idx),
            SpriteInstance('lamp', 58, LOW_H - 8, glow=1.0),
            SpriteInstance('lamp', LOW_W - 74, LOW_H - 8, glow=1.0),
            SpriteInstance('lamp', center_x - 22, LOW_H - 8, glow=1.0),
            SpriteInstance('lamp', center_x + 92, LOW_H - 8, glow=1.0),
            SpriteInstance('banner', 82, LOW_H - 82, sway=1.2, phase=1.8),
            SpriteInstance('banner', LOW_W - 96, LOW_H - 80, sway=1.1, phase=2.2),
            SpriteInstance('bush', 12, LOW_H - 10),
            SpriteInstance('bush', LOW_W - 28, LOW_H - 10),
            SpriteInstance('bush', center_x - 16, LOW_H - 10),
            SpriteInstance('bush', center_x + 76, LOW_H - 10),
        ])
        return ChunkVariant(**maps, sprites=sprites)

    def _make_fg_variant(self, idx: int) -> ChunkVariant:
        maps = self._blank_maps()
        sprites = [
            SpriteInstance('fg_leaves', 4, 132, sway=2.2, phase=idx * .8),
            SpriteInstance('fg_leaves', 22, 182, sway=1.6, phase=idx * .5),
            SpriteInstance('fg_leaves', LOW_W - 40, 142, sway=2.7, phase=idx * 1.1),
            SpriteInstance('fg_leaves', LOW_W - 60, 188, sway=1.9, phase=idx * .9),
            SpriteInstance('sign', 18, 46, bob=.6, phase=.6 + idx),
            SpriteInstance('sign', LOW_W - 44, 60, bob=.5, phase=1.4 + idx),
            SpriteInstance('pennant', 86, 46, sway=1.1, phase=idx * 0.4),
            SpriteInstance('pennant', LOW_W - 114, 54, sway=1.0, phase=1.4 + idx),
        ]
        return ChunkVariant(**maps, sprites=sprites)

    def _build_layers(self):
        far = [self._make_far_variant(i) for i in range(8)]
        mid = [self._make_mid_variant(i) for i in range(8)]
        near = [self._make_near_variant(i) for i in range(8)]
        fg = [self._make_fg_variant(i) for i in range(6)]
        return [
            Layer('far', 0.09, 820, far, (0,1,2,3,4,5,6,7,2,1,4,0,3,6,5,7), (False,False,True,False,True,False,True,False,False,True,False,False,True,False,True,False)),
            Layer('mid', 0.24, 828, mid, (0,2,1,4,3,5,6,7,1,0,5,3,2,4,7,6), (False,True,False,False,True,False,True,False,True,False,False,True,False,False,True,False)),
            Layer('near', 0.49, 836, near, (0,1,2,3,4,5,6,7,3,1,4,0,2,5,7,6), (False,False,True,False,False,True,False,True,False,True,False,False,True,False,True,False)),
            Layer('fg', 1.10, 840, fg, (0,1,2,3,4,5,1,2,0,4,3,5), (False,True,False,True,False,False,True,False,True,False,True,False), foreground=True),
        ]

    def _draw_sky(self, target, travel, frame, night, phase, climate):
        day_top = (87, 176, 255); day_mid = (168, 216, 255); day_horizon = (245, 228, 208)
        eve_top = (61, 93, 178); eve_mid = (127, 131, 220); eve_horizon = (255, 185, 138)
        night_top = (24, 29, 58); night_mid = (46, 57, 108); night_horizon = (80, 64, 109)
        dusk = abs(phase - 0.5) * 2.0
        dusk_mix = clamp(1.0 - dusk, 0.0, 1.0)
        top = lerp_color(lerp_color(day_top, eve_top, dusk_mix), night_top, night)
        mid = lerp_color(lerp_color(day_mid, eve_mid, dusk_mix), night_mid, night)
        horizon = lerp_color(lerp_color(day_horizon, eve_horizon, dusk_mix), night_horizon, night)
        for y in range(SCENE_H):
            t = y / float(SCENE_H - 1)
            if t < 0.55:
                color = lerp_color(top, mid, t / 0.55)
            else:
                color = lerp_color(mid, horizon, (t - 0.55) / 0.45)
            pygame.draw.line(target, color, (0, y), (WIDTH, y))
        celestial_x = int((90 - travel * 0.02) % (WIDTH + 120)) - 60
        celestial_y = 56 + int(math.sin(frame * 0.005) * 4)
        if night < 0.55:
            pygame.draw.circle(target, (255, 241, 122), (celestial_x, celestial_y), 24)
            pygame.draw.circle(target, (255, 214, 117, 70), (celestial_x, celestial_y), 35)
        else:
            pygame.draw.circle(target, (233, 240, 255), (celestial_x, celestial_y), 22)
            pygame.draw.circle(target, (220, 229, 255, 80), (celestial_x, celestial_y), 32)
            pygame.draw.circle(target, top, (celestial_x + 8, celestial_y - 5), 18)
            # estrelas
            for i in range(18):
                sx = int((i * 41 + frame * 0.2) % WIDTH)
                sy = 18 + (i * 27) % 88
                glow = 110 + int(70 * math.sin(frame * 0.04 + i))
                pygame.draw.rect(target, (255, 252, 222, max(50, glow)), (sx, sy, 2, 2))
        cloud_color = lerp_color((255, 243, 236), (111, 101, 145), night)
        speed = travel * 0.06
        for i in range(8):
            cx = int((i * 88 - speed + (i % 3) * 17) % (WIDTH + 120)) - 60
            cy = 42 + (i % 3) * 24 + int(math.sin(frame * 0.01 + i) * 2)
            for dx, dy, r in ((0, 0, 16), (-14, 4, 12), (14, 5, 11), (6, -6, 10)):
                pygame.draw.circle(target, cloud_color, (cx + dx, cy + dy), r)
        # haze sutil no horizonte
        haze = pygame.Surface((WIDTH, 86), pygame.SRCALPHA)
        haze.fill((255, 215, 166, int(30 * (1.0 - night) + 10)))
        target.blit(haze, (0, 135), special_flags=pygame.BLEND_RGBA_ADD)
        if climate in ('chuva', 'tempestade'):
            veil = pygame.Surface((WIDTH, SCENE_H), pygame.SRCALPHA)
            veil.fill((60, 74, 103, 28 if climate == 'chuva' else 44))
            target.blit(veil, (0, 0))

    def _draw_train(self, target, travel, frame, night, map_kind='image'):
        super()._draw_train(target, travel, frame, night, map_kind)
        # segunda composição mais distante para enriquecer o skyline
        asset = self.lib.assets['train']
        surf = getattr(asset, map_kind)
        surf = pygame.transform.scale(surf, (int(surf.get_width() * 0.82), int(surf.get_height() * 0.82)))
        x = int((-120 + (frame * 2.0 % (WIDTH + 220)))) - 40
        y = 171 * SCALE
        if map_kind == 'image':
            target.blit(surf, (x, y))

    def _draw_traffic(self, target, frame, night):
        for lane, color_a, color_b, speed, y in ((0, (255,218,131), (255,111,105), 2.6, 180), (1, (110,198,255), (246,240,200), 1.9, 193)):
            for i in range(5):
                x = int((i * 110 + frame * speed + lane * 27) % (WIDTH + 120)) - 60
                pygame.draw.rect(target, color_a if (i + lane) % 2 == 0 else color_b, (x, y, 16, 4), border_radius=1)
                if night > 0.2:
                    pygame.draw.rect(target, (255, 224, 130, 45), (x - 4, y - 1, 24, 6), border_radius=2)

    def _draw_birds(self, target, frame, map_kind='image'):
        if map_kind != 'image':
            return
        bird = self.lib.assets['bird'].image
        for i in range(4):
            x = int((WIDTH + 60 - (frame * (1.1 + i * 0.2)) + i * 78) % (WIDTH + 180)) - 40
            y = 68 + i * 9 + int(math.sin(frame * 0.06 + i) * 4)
            target.blit(bird, (x, y))

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
        if map_kind == 'image' and not foreground_only:
            self._draw_traffic(target, frame, night)
            self._draw_birds(target, frame, map_kind)
        if map_kind == 'image' and not foreground_only and night > 0.18:
            overlay = pygame.Surface((WIDTH, SCENE_H), pygame.SRCALPHA)
            overlay.fill((28, 29, 64, int(68 * night)))
            target.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            glow = pygame.Surface((WIDTH, SCENE_H), pygame.SRCALPHA)
            glow.fill((255, 215, 140, int(10 + 18 * night)))
            target.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        if map_kind == 'image' and not foreground_only and climate in ('tempestade', 'chuva'):
            for i in range(34 if climate == 'tempestade' else 22):
                x = int((i * 37 - frame * (6.5 if climate == 'tempestade' else 3.4)) % (WIDTH + 30)) - 15
                y = int((i * 43 + frame * 7.2) % SCENE_H)
                pygame.draw.line(target, (160, 209, 250, 100), (x, y), (x - 6, y + 13), 1)
        self._last_state = (travel, frame, night, climate, phase)
        if map_kind == 'geometry' and not foreground_only:
            self._geometry_view = target.copy()
