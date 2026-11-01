"""v3.133 — reconstrução modular de Floresta, Vulcão, Cidade Futurista e Ilhas Celestes.

Segue o mesmo contrato dos cenários modulares anteriores: arte desenhada na
inicialização em chunks 225x250, sem sprites soltos na pista, com repetição
controlada, caches limitados e reatividade leve ao clima e ao ciclo noite.
"""
import math
import random
from collections import OrderedDict
import pygame
from pixelrush_biomes2_v3131 import ModularBiomeScene as Previous, MODULAR_BIOMES as PREVIOUS_BIOMES
from pixelrush_biomes2_v3126 import LW, LH, WIDTH, HEIGHT, _rect, _line, _p, _rgb

EXTRA_BIOMES = ('floresta', 'vulcao', 'cidade_futurista', 'ilhas_celestes')
MODULAR_BIOMES = tuple(dict.fromkeys(PREVIOUS_BIOMES + EXTRA_BIOMES))
SUPPORTED_BIOMES = MODULAR_BIOMES


class ModularBiomeScene(Previous):
    def __init__(self, biome):
        if biome in PREVIOUS_BIOMES:
            super().__init__(biome)
            return
        if biome not in MODULAR_BIOMES:
            raise ValueError('bioma modular nao suportado: ' + str(biome))
        self.biome = biome
        self.visual_quality = 1
        self._layers = {}
        self._map_cache = OrderedDict()
        self._sky_cache = OrderedDict()
        self._composites = {}
        self._night_veils = OrderedDict()
        self._geometry_view = None
        self._last_state = None
        counts = {'far': 6, 'mid': 8, 'near': 10}
        for layer in ('far', 'mid', 'near'):
            self._layers[layer] = [self._make_chunk(layer, i) for i in range(counts[layer])]

    # ---------------- base shapes ----------------
    def _tree(self, surf, x, base, h, seed, canopy=True):
        rng = random.Random(seed)
        trunk = (88, 64, 46)
        bark = (125, 91, 58)
        top = base - h
        _line(surf, trunk, x, base, x + 2, top + 18, 7)
        _line(surf, bark, x + 1, base - 2, x + 3, top + 22, 2)
        for yy in range(top + 28, base - 8, 9):
            _line(surf, (69, 49, 36), x - 1, yy, x + 4, yy - 1)
        if canopy:
            for dx, dy, r, col in ((-18, 0, 18, (48, 106, 69)), (3, -11, 22, (62, 126, 75)), (20, 1, 18, (94, 155, 91))):
                pygame.draw.circle(surf, col, (x + dx, top + 18 + dy), r)
            for _ in range(7):
                lx = x + rng.randint(-22, 22)
                ly = top + 8 + rng.randint(0, 26)
                _line(surf, (157, 208, 116), lx, ly, lx + 2, ly + 1)

    def _ruin(self, surf, x, base, w, h):
        top = base - h
        _rect(surf, (103, 117, 91), x, top, w, h)
        _rect(surf, (72, 88, 70), x + 4, top + 6, w - 8, h - 11)
        _rect(surf, (167, 181, 143), x - 2, top - 3, w + 4, 5)
        for yy in range(top + 14, base - 10, 14):
            _line(surf, (124, 139, 108), x + 5, yy, x + w - 6, yy)
        _p(surf, (58, 130, 77), [(x - 2, top + 10), (x + w // 2, top - 5), (x + w + 3, top + 9), (x + w, top + 18), (x + 3, top + 15)])

    def _waterfall(self, surf, x, y, w, h):
        _rect(surf, (79, 165, 170), x, y, w, h)
        _rect(surf, (128, 210, 216), x + 3, y, max(2, w // 3), h)
        for yy in range(y + 4, y + h, 11):
            _line(surf, (196, 244, 248), x + w // 2, yy, x + w // 2 + 2, yy + 5)

    def _rock(self, surf, x, base, w, h, c1=(74, 62, 70), c2=(110, 94, 101), c3=(168, 144, 138)):
        top = base - h
        _p(surf, c1, [(x, base), (x + 4, top + h // 3), (x + w // 2, top), (x + w - 4, top + h // 4), (x + w, base)])
        _p(surf, c2, [(x + 6, base - 3), (x + w // 2 - 2, top + 8), (x + w - 8, base - 4)])
        _line(surf, c3, x + w // 2 - 1, top + 9, x + w // 2 + 8, top + h // 2, 2)

    def _cloud(self, surf, x, y, scale=1.0, tint=(236, 244, 255)):
        circles = [(-18, 6, 15), (-2, 0, 18), (17, 7, 14), (2, 10, 18)]
        for dx, dy, r in circles:
            pygame.draw.circle(surf, tint, (int(x + dx * scale), int(y + dy * scale)), max(4, int(r * scale)))

    def _island(self, surf, x, y, w, h):
        _p(surf, (104, 96, 118), [(x, y), (x + 10, y + h // 2), (x + w // 2, y + h), (x + w - 8, y + h // 2), (x + w, y + 2)])
        _p(surf, (123, 176, 104), [(x - 4, y + 1), (x + w // 3, y - 5), (x + w - 10, y + 2), (x + w - 6, y + 10), (x + 4, y + 11)])
        for xx in range(x + 5, x + w - 10, 11):
            _line(surf, (95, 215, 126), xx, y + 4, xx + 6, y + 4)
        _line(surf, (140, 210, 222), x + w // 2, y + h // 2, x + w // 2, y + h + 15, 2)

    def _neon_tower(self, surf, x, base, w, h, seed):
        rng = random.Random(seed)
        top = base - h
        _rect(surf, (46, 58, 90), x, top, w, h)
        _rect(surf, (75, 96, 137), x + 3, top + 3, w - 6, h - 4)
        for yy in range(top + 10, base - 8, 12):
            for xx in range(x + 6, x + w - 8, 8):
                col = (100, 230, 244) if (xx + yy + seed) % 3 else (240, 104, 221)
                _rect(surf, col, xx, yy, 4, 5)
        if w >= 18:
            _rect(surf, (248, 202, 110), x + w // 2 - 1, top - 8, 3, 8)
            _rect(surf, (103, 244, 248), x + w // 2 - 3, top - 3, 7, 2)
        if rng.random() < 0.7:
            _line(surf, (94, 238, 247), x + 2, top + h // 2, x + w - 2, top + h // 2)

    # ---------------- chunk generation ----------------
    def _make_chunk(self, layer, index):
        if self.biome in PREVIOUS_BIOMES:
            return super()._make_chunk(layer, index)
        if self.biome == 'floresta':
            return self._make_forest(layer, index)
        if self.biome == 'vulcao':
            return self._make_volcano(layer, index)
        if self.biome == 'cidade_futurista':
            return self._make_future(layer, index)
        return self._make_skyisles(layer, index)

    def _make_forest(self, layer, index):
        rng = random.Random(13300 + index * 67 + {'far': 0, 'mid': 1000, 'near': 2000}[layer])
        s = pygame.Surface((LW, LH), pygame.SRCALPHA)
        if layer == 'far':
            _rect(s, (42, 80, 62), 0, 136, LW, 78)
            for x, h in ((18, 54), (58, 78), (104, 62), (149, 85), (196, 57)):
                self._tree(s, x, 206, h + rng.randint(-6, 6), 20 + index * 3 + x)
            _rect(s, (54, 104, 77), 0, 203, LW, 25)
        elif layer == 'mid':
            _rect(s, (51, 99, 73), 0, 188, LW, 40)
            for x in (15, 69, 176):
                self._tree(s, x, 207, 56 + (x + index) % 18, 330 + x + index, canopy=(x != 69 or index % 2 == 0))
            if index % 4 in (1, 3):
                self._ruin(s, 88, 210, 52, 66)
            else:
                self._waterfall(s, 101, 150, 18, 59)
                _rect(s, (38, 102, 107), 71, 203, 99, 12)
                _rect(s, (81, 149, 148), 80, 207, 82, 8)
            for x in (34, 57, 154, 187):
                pygame.draw.ellipse(s, (89, 143, 84), (x, 204 + (x % 5), 17, 9))
        else:
            _rect(s, (57, 98, 73), 0, 221, LW, 9)
            themes = index % 5
            if themes in (0, 3):
                self._tree(s, 27, 229, 70, 602 + index)
                self._tree(s, 196, 229, 79, 702 + index)
                self._ruin(s, 84, 229, 56, 56)
            elif themes == 1:
                self._tree(s, 39, 229, 67, 801 + index)
                self._waterfall(s, 97, 176, 20, 42)
                self._tree(s, 177, 229, 61, 901 + index)
            elif themes == 2:
                self._ruin(s, 22, 229, 44, 50)
                self._tree(s, 111, 229, 73, 1001 + index)
                self._ruin(s, 169, 229, 41, 46)
            else:
                self._tree(s, 25, 229, 61, 1101 + index)
                self._tree(s, 186, 229, 63, 1201 + index)
                for x in (81, 100, 126):
                    pygame.draw.ellipse(s, (78, 128, 83), (x, 210 + (x % 3), 16, 9))
                    _line(s, (164, 205, 102), x + 7, 214, x + 11, 214)
            _line(s, (150, 203, 114), 0, 228, LW, 228, 2)
            _rect(s, (84, 68, 57), 0, 230, LW, 4)
            _rect(s, (61, 73, 57), 0, 234, LW, 16)
            for x in range(0, LW, 18):
                _line(s, (96, 82, 63), x, 240, x + 7, 240)
        return s

    def _make_volcano(self, layer, index):
        rng = random.Random(13400 + index * 79 + {'far': 0, 'mid': 1000, 'near': 2000}[layer])
        s = pygame.Surface((LW, LH), pygame.SRCALPHA)
        if layer == 'far':
            _rect(s, (72, 43, 63), 0, 152, LW, 64)
            for cx, peak, width in ((22, 95, 62), (93, 76, 83), (174, 102, 75)):
                _p(s, (96, 56, 72), [(cx - width // 2, 180), (cx, peak), (cx + width // 2, 180)])
                _line(s, (149, 92, 85), cx - 9, peak + 18, cx + 4, peak + 49, 2)
            _rect(s, (120, 58, 54), 0, 178, LW, 36)
        elif layer == 'mid':
            _rect(s, (99, 52, 53), 0, 200, LW, 25)
            for x in (20, 76, 135, 190):
                self._rock(s, x, 213, 32 + (x % 11), 37 + (x % 9), (60, 53, 64), (95, 79, 88), (142, 120, 104))
            if index % 3 == 0:
                _rect(s, (230, 106, 60), 93, 205, 36, 5)
                _line(s, (255, 188, 82), 98, 206, 122, 206, 2)
            for x in (48, 112, 176):
                _line(s, (158, 149, 153), x, 197, x - 5, 171, 2)
                _line(s, (108, 99, 103), x + 2, 197, x + 8, 173, 2)
        else:
            _rect(s, (78, 59, 67), 0, 221, LW, 8)
            style = index % 4
            if style in (0, 2):
                self._rock(s, 15, 229, 42, 49, (47, 43, 52), (91, 74, 84), (149, 109, 87))
                self._rock(s, 164, 229, 47, 58, (47, 43, 52), (91, 74, 84), (149, 109, 87))
                _rect(s, (246, 108, 57), 80, 224, 56, 4)
                _line(s, (255, 191, 92), 89, 225, 124, 225, 2)
            elif style == 1:
                self._rock(s, 18, 229, 34, 43, (47, 43, 52), (91, 74, 84), (149, 109, 87))
                self._rock(s, 99, 229, 25, 53, (47, 43, 52), (91, 74, 84), (149, 109, 87))
                self._rock(s, 165, 229, 34, 45, (47, 43, 52), (91, 74, 84), (149, 109, 87))
            else:
                for x in (43, 96, 152):
                    _line(s, (161, 151, 154), x, 224, x - 5, 193, 2)
                    _line(s, (102, 94, 101), x + 2, 224, x + 8, 195, 2)
            _line(s, (255, 163, 78), 0, 228, LW, 228, 2)
            _rect(s, (92, 65, 61), 0, 230, LW, 4)
            _rect(s, (63, 49, 51), 0, 234, LW, 16)
            for x in range(6, LW, 17):
                _line(s, (106, 79, 77), x, 240, x + 6, 241)
        return s

    def _make_future(self, layer, index):
        rng = random.Random(13500 + index * 71 + {'far': 0, 'mid': 1000, 'near': 2000}[layer])
        s = pygame.Surface((LW, LH), pygame.SRCALPHA)
        if layer == 'far':
            _rect(s, (39, 48, 86), 0, 136, LW, 90)
            for x, w, h in ((8, 22, 58), (42, 17, 73), (74, 29, 65), (122, 18, 80), (154, 23, 71), (189, 21, 60)):
                self._neon_tower(s, x, 205, w, h + rng.randint(-8, 7), 1400 + x + index)
            _line(s, (106, 239, 246), 0, 201, LW, 201)
        elif layer == 'mid':
            _rect(s, (48, 63, 103), 0, 187, LW, 41)
            _rect(s, (90, 111, 150), 0, 173, LW, 8)
            for x in range(7, LW, 31):
                _rect(s, (67, 89, 127), x, 177, 20, 26)
                _rect(s, (106, 233, 245), x + 4, 182, 12, 3)
            if index % 4 in (1, 2):
                _line(s, (243, 99, 223), 16, 164, 208, 164, 2)
                for x in (28, 88, 148, 196):
                    _line(s, (89, 232, 248), x, 164, x, 187, 2)
            else:
                self._neon_tower(s, 26, 208, 38, 58, 1600 + index)
                self._neon_tower(s, 95, 208, 31, 71, 1700 + index)
                self._neon_tower(s, 164, 208, 39, 63, 1800 + index)
        else:
            _rect(s, (52, 67, 101), 0, 221, LW, 8)
            theme = index % 4
            if theme == 0:
                self._neon_tower(s, -3, 229, 46, 72, 1900 + index)
                self._neon_tower(s, 78, 229, 36, 88, 2000 + index)
                self._neon_tower(s, 157, 229, 51, 67, 2100 + index)
            elif theme == 1:
                self._neon_tower(s, 20, 229, 27, 58, 2200 + index)
                _rect(s, (75, 96, 139), 73, 195, 78, 26)
                _rect(s, (106, 240, 246), 78, 199, 68, 4)
                self._neon_tower(s, 177, 229, 28, 61, 2300 + index)
            elif theme == 2:
                self._neon_tower(s, 0, 229, 35, 63, 2400 + index)
                self._neon_tower(s, 64, 229, 42, 81, 2500 + index)
                self._neon_tower(s, 151, 229, 35, 63, 2600 + index)
            else:
                _rect(s, (66, 84, 120), 19, 194, 58, 27)
                _rect(s, (239, 98, 220), 22, 198, 52, 3)
                self._neon_tower(s, 100, 229, 32, 83, 2700 + index)
                _rect(s, (66, 84, 120), 150, 194, 56, 27)
                _rect(s, (106, 241, 247), 154, 200, 48, 3)
            _line(s, (84, 233, 248), 0, 228, LW, 228, 2)
            _rect(s, (71, 83, 111), 0, 230, LW, 4)
            _rect(s, (45, 56, 78), 0, 234, LW, 16)
            for x in range(9, LW, 21):
                _line(s, (98, 113, 141), x, 240, x + 9, 240)
        return s

    def _make_skyisles(self, layer, index):
        rng = random.Random(13600 + index * 83 + {'far': 0, 'mid': 1000, 'near': 2000}[layer])
        s = pygame.Surface((LW, LH), pygame.SRCALPHA)
        if layer == 'far':
            for x, y, sc in ((18, 88, 1.0), (107, 66, 1.2), (182, 94, 0.9)):
                self._cloud(s, x, y, sc, (240, 247, 255))
            self._island(s, 13, 127, 67, 42)
            self._island(s, 126, 106, 80, 52)
        elif layer == 'mid':
            for x, y, sc in ((30, 108, 1.2), (150, 83, 0.95)):
                self._cloud(s, x, y, sc, (226, 239, 255))
            self._island(s, 26, 159, 75, 46)
            self._island(s, 124, 143, 83, 55)
            if index % 3 == 0:
                _rect(s, (178, 160, 224), 93, 129, 34, 6)
                for xx in range(95, 124, 8):
                    _line(s, (207, 242, 255), xx, 128, xx + 4, 120, 2)
            else:
                self._waterfall(s, 154, 153, 12, 48)
        else:
            _rect(s, (132, 151, 176), 0, 221, LW, 8)
            theme = index % 4
            if theme == 0:
                self._island(s, 5, 188, 54, 34)
                self._island(s, 165, 181, 56, 38)
                for x in (84, 116, 132):
                    _p(s, (158, 236, 247), [(x, 218), (x + 5, 208), (x + 10, 218), (x + 5, 227)])
            elif theme == 1:
                self._island(s, 17, 180, 72, 41)
                self._waterfall(s, 119, 186, 11, 32)
                self._island(s, 157, 190, 48, 29)
            elif theme == 2:
                self._island(s, 30, 189, 51, 32)
                self._island(s, 96, 178, 63, 40)
                self._island(s, 173, 189, 45, 28)
            else:
                self._rect_temple(s, 83, 203)
                self._island(s, 8, 192, 42, 26)
                self._island(s, 177, 192, 40, 26)
            _line(s, (205, 239, 255), 0, 228, LW, 228, 2)
            _rect(s, (176, 184, 198), 0, 230, LW, 4)
            _rect(s, (120, 130, 148), 0, 234, LW, 16)
            for x in range(8, LW, 20):
                _line(s, (155, 166, 180), x, 240, x + 8, 240)
        return s

    def _rect_temple(self, surf, x, base):
        _rect(surf, (194, 200, 214), x, base - 27, 58, 24)
        _rect(surf, (155, 171, 190), x + 6, base - 22, 46, 17)
        for xx in (x + 10, x + 24, x + 38):
            _rect(surf, (213, 221, 232), xx, base - 20, 5, 17)
        _p(surf, (230, 236, 246), [(x - 4, base - 27), (x + 29, base - 39), (x + 62, base - 27)])
        for xx in (x + 7, x + 50):
            _p(surf, (168, 244, 255), [(xx, base - 27), (xx + 5, base - 35), (xx + 10, base - 27)])

    # ---------------- extra reactivity ----------------
    def render_scene(self, target, travel, frame, night, climate, phase, foreground_only=False, map_kind='image'):
        super().render_scene(target, travel, frame, night, climate, phase, foreground_only=foreground_only, map_kind=map_kind)
        if foreground_only or map_kind != 'image' or self.biome in PREVIOUS_BIOMES:
            return
        if self.biome == 'floresta':
            self._overlay_forest(target, frame, climate, night)
        elif self.biome == 'vulcao':
            self._overlay_volcano(target, frame, climate, night)
        elif self.biome == 'cidade_futurista':
            self._overlay_future(target, frame, climate, night)
        elif self.biome == 'ilhas_celestes':
            self._overlay_sky(target, frame, climate, night)
        self._last_state = (travel, frame, night, climate, phase)

    def _overlay_forest(self, surf, frame, climate, night):
        if night > .18:
            for x in (46, 111, 195, 255, 329, 396):
                r = 2 if (frame // 20 + x) % 3 else 3
                pygame.draw.circle(surf, (184, 232, 130, 135), (x, 155 + (x % 13)), r)
        if climate in ('chuva', 'tempestade', 'tempestade_vento'):
            for i in range(16 if self.visual_quality else 8):
                x = int((i * 31 + frame * 3.3) % 470) - 10
                y = int((i * 27 + frame * 1.7) % 270) + 20
                pygame.draw.line(surf, (182, 220, 228), (x, y), (x - 6, y + 16), 1)
        elif climate in ('vento_folhas', 'vento', 'polen'):
            count = 18 if self.visual_quality else 9
            for i in range(count):
                x = int((i * 23 + frame * 1.8) % 490) - 20
                y = int((40 + i * 19 + math.sin((frame + i * 7) * .08) * 12) % 240)
                col = (184, 212, 95) if i % 3 else (219, 232, 139)
                pygame.draw.ellipse(surf, col, (x, y, 5, 3))

    def _overlay_volcano(self, surf, frame, climate, night):
        if night > .14 or climate in ('chuva_meteoros', 'tempestade'):
            glow = 85 if night < .14 else 128
            for rect in ((172, 426, 53, 5), (156, 430, 76, 4), (195, 381, 14, 26)):
                glow_s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
                glow_s.fill((255, 142, 66, glow))
                surf.blit(glow_s, rect[:2])
        for i in range(7 if self.visual_quality else 4):
            x = int((i * 59 - frame * (0.9 if climate not in ('vento', 'tempestade_vento') else 1.6)) % 500) - 18
            y = 60 + (i * 43 + frame // 3) % 110
            pygame.draw.ellipse(surf, (118, 109, 117, 90), (x, y, 18, 10))
        if climate in ('chuva', 'tempestade'):
            for i in range(10 if self.visual_quality else 5):
                x = int((i * 49 + frame * 3.2) % 470) - 10
                y = int((i * 33 + frame * 1.5) % 220) + 20
                pygame.draw.line(surf, (185, 210, 217), (x, y), (x - 5, y + 13), 1)
                if i % 2 == 0:
                    pygame.draw.line(surf, (210, 215, 220), (x - 3, y + 9), (x + 2, y + 16), 1)

    def _overlay_future(self, surf, frame, climate, night):
        if night > .10:
            for x in range(28, 426, 58):
                col = (102, 240, 247, 120) if ((frame // 14 + x) % 2 == 0) else (244, 109, 221, 112)
                pygame.draw.line(surf, col, (x, 52), (x + 12, 232), 1)
        for y in (88, 149, 227):
            alpha = 26 if (frame // 10 + y) % 2 == 0 else 14
            scan = pygame.Surface((450, 2), pygame.SRCALPHA)
            scan.fill((91, 240, 248, alpha))
            surf.blit(scan, (0, y))
        if climate in ('chuva', 'tempestade', 'vento_neon'):
            for i in range(18 if self.visual_quality else 10):
                x = int((i * 29 + frame * 3.4) % 470) - 10
                y = int((i * 24 + frame * 1.6) % 250) + 20
                pygame.draw.line(surf, (137, 230, 246), (x, y), (x - 7, y + 18), 1)
        for x in (82, 168, 259, 347):
            if ((frame // 18 + x) % 4) != 0:
                pygame.draw.rect(surf, (102, 240, 247, 105), (x, 98 + (x % 25), 22, 6), border_radius=3)

    def _overlay_sky(self, surf, frame, climate, night):
        for i in range(10 if self.visual_quality else 6):
            x = int((i * 57 - frame * 0.7) % 520) - 35
            y = 35 + (i * 33) % 140
            self._cloud(surf, x, y, 0.55, (248, 252, 255, 230))
        for i in range(12 if self.visual_quality else 7):
            x = int((i * 39 + frame * 1.2) % 470) - 12
            y = int((i * 29 + math.sin((frame + i * 8) * .07) * 7 + 90) % 230)
            pygame.draw.ellipse(surf, (173, 242, 255, 95 if night < .2 else 132), (x, y, 4, 8))
        if climate in ('vento', 'tempestade_vento', 'chuva'):
            for i in range(12 if self.visual_quality else 6):
                x = int((i * 43 - frame * 2.1) % 490) - 10
                y = int((i * 37 + frame * 0.8) % 220) + 20
                pygame.draw.line(surf, (210, 240, 250), (x, y), (x + 11, y), 1)
        if climate in ('tempestade', 'tempestade_vento') and frame % 70 < 4:
            pygame.draw.lines(surf, (232, 248, 255), False, [(312, 88), (298, 116), (320, 116), (304, 145)], 2)
