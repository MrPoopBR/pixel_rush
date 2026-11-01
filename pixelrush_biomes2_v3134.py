"""Polimento e reações econômicas dos quatro biomas modulares (v3.134).

Extensão estritamente VISUAL da arte já criada na v3.133. Chunks são refinados
uma vez, no carregamento. Animações usam somente primitivas pequenas, sem I/O,
partículas físicas ou novos sprites. Mapas técnicos acompanham os chunks.
"""
import math
import random
import pygame
from pixelrush_biomes2_v3133 import (ModularBiomeScene as Anterior,
                                          MODULAR_BIOMES, EXTRA_BIOMES, LW, LH, WIDTH, HEIGHT)


class ModularBiomeScene(Anterior):
    def __init__(self, biome):
        super().__init__(biome)
        self._tempo_mask = None
        self._luz_pulsante = None
        self._pouso_restante = 0
        self._pouso_x = 90
        self._pouso_forca = 0.0

    # Passagem artística de volume e textura. Chamadas só na criação dos chunks.
    def _tree(self, surf, x, base, h, seed, canopy=True):
        super()._tree(surf, x, base, h, seed, canopy)
        if canopy:
            rng = random.Random(seed + 13400)
            cy = base - h + 18
            # Fragmentos de copa em três valores para volume, sem sprite extra.
            for i in range(28):
                dx, dy = rng.randrange(-33, 34), rng.randrange(-28, 25)
                if dx*dx + (dy*1.40)**2 > 32**2:
                    continue
                col = ((30, 91, 63), (91, 160, 93), (150, 202, 117))[i%3]
                px, py = x+dx, cy+dy
                pygame.draw.rect(surf, col, (px, py, 3 if i%4 else 5, 2))
            for dx in (-12, 8, 20):
                pygame.draw.line(surf, (51, 99, 66), (x+dx, cy+12), (x+dx+2, cy+22), 1)
        # Reentrâncias e casca lateral no tronco — alto contraste ao solo.
        for dy in range(28, max(31,h-5), 13):
            ty = base-dy
            pygame.draw.line(surf, (63, 47, 36), (x+3, ty), (x+5, ty+5), 1)
            pygame.draw.line(surf, (156, 119, 69), (x-1, ty+3), (x+1, ty+5), 1)

    def _rock(self, surf, x, base, w, h, c1=(74,62,70), c2=(110,94,101), c3=(168,144,138)):
        super()._rock(surf,x,base,w,h,c1,c2,c3)
        top=base-h
        for dy in range(12,h-5,12):
            pygame.draw.line(surf,(40,38,49),(x+w//3,top+dy),(x+w//3+4,top+dy+3),1)
            pygame.draw.line(surf,(202,136,91),(x+w//2+1,top+dy-2),(x+w//2+3,top+dy+1),1)

    def _ruin(self, surf,x,base,w,h):
        super()._ruin(surf,x,base,w,h)
        top=base-h
        for off in range(7,w-5,10):
            pygame.draw.line(surf,(150,169,117),(x+off,top+10),(x+off+4,top+11))
            if off%3:
                pygame.draw.line(surf,(45,105,62),(x+off,base-7),(x+off-2,base-16),2)

    def _island(self, surf,x,y,w,h):
        super()._island(surf,x,y,w,h)
        for i,xx in enumerate(range(x+11,x+w-8,16)):
            pygame.draw.line(surf,(77,94,108),(xx,y+h//2),(xx+3,y+h//2+9+i%3),2)
            pygame.draw.line(surf,(130,219,177),(xx+3,y+h//2+5),(xx+7,y+h//2+8),1)
        for xx in range(x+9,x+w-6,11):
            pygame.draw.rect(surf,(181,223,133),(xx,y-2,3,2))
            pygame.draw.rect(surf,(92,151,110),(xx+2,y+2,2,2))

    def _neon_tower(self,surf,x,base,w,h,seed):
        super()._neon_tower(surf,x,base,w,h,seed)
        top=base-h
        pygame.draw.line(surf,(33,43,72),(x+3,top+6),(x+3,base-5),2)
        pygame.draw.line(surf,(133,166,210),(x+w-4,top+8),(x+w-4,base-8),1)
        for yy in range(top+12,base-6,17):
            pygame.draw.line(surf,(43,63,94),(x+3,yy),(x+w-4,yy),1)
            if w>20:
                pygame.draw.rect(surf,(152,227,241),(x+w//2,yy+2,3,2))

    def registrar_pouso(self, x, intensidade):
        self._pouso_x = max(12, min(430, int(x)))
        self._pouso_restante = 12
        self._pouso_forca = max(.2, min(1.5, float(intensidade)))

    def _reacao_pouso(self, surf, frame):
        if self._pouso_restante <= 0:
            return
        # Decai em 12 updates do mundo, sem ficar preso se os quadros pararem.
        radius = int((13-self._pouso_restante)*1.5*self._pouso_forca)
        x = self._pouso_x
        paleta = {'floresta':(146,191,95),'vulcao':(226,129,72),
                  'cidade_futurista':(109,217,235),'ilhas_celestes':(184,236,216)}
        cor = paleta[self.biome]
        for sign in (-1,1):
            xx = x + sign*(14 + radius)
            for j in range(3 if self.visual_quality else 2):
                yy = 459-j*8-((12-self._pouso_restante)//2)
                pygame.draw.line(surf,cor,(xx,yy+4),(xx+sign*3,yy))

    def _make_chunk(self, layer, index):
        src = super()._make_chunk(layer, index)
        if self.biome not in EXTRA_BIOMES:
            return src
        # Microtextura somente dentro dos objetos/terreno, respeitando o vazio
        # superior (céu). Há sempre 2-3 grupos por quadro, baixa densidade.
        if layer == 'near':
            colors = {
                'floresta': ((47, 65, 51), (121, 153, 93)),
                'vulcao': ((54, 43, 50), (145, 93, 77)),
                'cidade_futurista': ((51, 66, 102), (123, 155, 191)),
                'ilhas_celestes': ((113, 129, 148), (213, 230, 235)),
            }
            sombra, luz = colors[self.biome]
            for k in range(9):
                x = (k * 37 + index * 17) % LW
                y = 237 + (k * 7 + index) % 11
                pygame.draw.line(src, sombra if k % 3 else luz, (x, y), (x + 4, y), 1)
            if self.biome == 'floresta':
                # Pequenas vinhas ligadas aos troncos, não folhas sobre a pista.
                for x, y in ((29, 184), (192, 183)):
                    pygame.draw.line(src, (84, 145, 85), (x, y), (x + 3, y + 12), 2)
                    pygame.draw.ellipse(src, (139, 182, 87), (x + 1, y + 5, 8, 4))
            elif self.biome == 'vulcao':
                for x in (52, 120, 191):
                    pygame.draw.line(src, (238, 107, 54), (x, 224), (x + 5, 226), 2)
                    pygame.draw.line(src, (255, 183, 79), (x + 1, 224), (x + 3, 225), 1)
            elif self.biome == 'cidade_futurista':
                for x in (19, 103, 185):
                    pygame.draw.rect(src, (61, 93, 123), (x, 228, 18, 2))
                    pygame.draw.rect(src, (96, 220, 234), (x + 4, 228, 7, 1))
            elif self.biome == 'ilhas_celestes':
                for x in (44, 128, 199):
                    pygame.draw.circle(src, (166, 231, 216), (x, 223), 2)
        elif layer == 'far' and self.biome == 'floresta':
            for x in (11, 61, 111, 164, 208):
                pygame.draw.line(src, (47, 113, 78), (x, 200), (x + 8, 207), 2)
        return src

    def _tile_map(self, layer, idx, kind):
        if self.biome not in EXTRA_BIOMES:
            return super()._tile_map(layer, idx, kind)
        src = self._layers[layer][idx]
        if kind == 'image':
            return src
        key = (layer, idx, kind)
        if key not in self._map_cache:
            target = pygame.Surface((LW, LH), pygame.SRCALPHA)
            if kind != 'fxmask':
                colors = {
                    'normal': (128, 128, 255, 255),
                    'flow': (128, 128, 0, 255),
                    'flowmask': (128, 128, 0, 255),
                    'geometry': (0, 210, 0, 255),
                    'material': {'floresta': (194, 218, 103, 255),
                                 'vulcao': (223, 84, 65, 255),
                                 'cidade_futurista': (129, 193, 238, 255),
                                 'ilhas_celestes': (143, 221, 201, 255)}[self.biome],
                }
                pygame.mask.from_surface(src, threshold=90).to_surface(
                    surface=target, setcolor=colors.get(kind, (0, 0, 0, 0)),
                    unsetcolor=(0, 0, 0, 0))
            elif layer != 'far':
                if self.biome == 'vulcao':
                    pygame.draw.rect(target, (255, 118, 50, 165), (78, 218, 58, 9))
                elif self.biome == 'cidade_futurista':
                    for x in (20, 92, 181):
                        pygame.draw.rect(target, (84, 232, 248, 165), (x, 183, 21, 3))
                elif self.biome == 'ilhas_celestes':
                    for x in (44, 128, 198):
                        pygame.draw.circle(target, (137, 232, 242, 134), (x, 218), 3)
                elif self.biome == 'floresta':
                    for x in (28, 193):
                        pygame.draw.circle(target, (135, 215, 130, 102), (x, 193), 2)
            self._map_cache[key] = target
            while len(self._map_cache) > 36:
                self._map_cache.popitem(last=False)
        self._map_cache.move_to_end(key)
        return self._map_cache[key]

    def _draw_layer(self, dst, layer, travel, kind):
        if self.biome not in EXTRA_BIOMES:
            return super()._draw_layer(dst, layer, travel, kind)
        # Mesmas velocidades do motor modular v3.128; períodos de camada
        # diferentes e índices de variação determinísticos por distância.
        factor = {'far': .10, 'mid': .25, 'near': .52}[layer]
        offset = max(0.0, travel) * factor * .5
        first, shift = divmod(int(offset), LW)
        count = len(self._layers[layer])
        for j in range(2):
            indice = ((first + j) * {'far': 5, 'mid': 3, 'near': 3}[layer]) % count
            dst.blit(self._tile_map(layer, indice, kind), (j * LW - shift, 0))

    def render_scene(self, target, travel, frame, night, climate, phase,
                     foreground_only=False, map_kind='image'):
        if self.biome not in EXTRA_BIOMES:
            return super().render_scene(target, travel, frame, night, climate, phase,
                                        foreground_only=foreground_only, map_kind=map_kind)
        if foreground_only:
            return target
        low = self._composites.get(map_kind)
        if low is None:
            low = pygame.Surface((LW, LH), pygame.SRCALPHA)
            self._composites[map_kind] = low
        if map_kind == 'normal':
            low.fill((128, 128, 255, 255))
        elif map_kind in ('flow', 'flowmask'):
            low.fill((128, 128, 0, 255))
        else:
            low.fill((0, 0, 0, 0))
        for layer in ('far', 'mid', 'near'):
            self._draw_layer(low, layer, travel, map_kind)
        if map_kind == 'image' and night > .035:
            level = min(12, max(0, round(night * 12)))
            veil = self._night_veils.get(level)
            if veil is None:
                veil = pygame.Surface((LW, LH), pygame.SRCALPHA)
                strength = level / 12.0
                veil.fill((round(255 - 112 * strength),
                           round(255 - 104 * strength),
                           round(255 - 74 * strength), 255))
                self._night_veils[level] = veil
                if len(self._night_veils) > 6:
                    self._night_veils.popitem(last=False)
            low.blit(veil, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pygame.transform.scale(low, (WIDTH, HEIGHT), target)
        if map_kind == 'image':
            self._reacao_pouso(target,frame)
            if self.biome == 'floresta':
                self._overlay_forest(target, frame, climate, night)
            elif self.biome == 'vulcao':
                self._overlay_volcano(target, frame, climate, night)
            elif self.biome == 'cidade_futurista':
                self._overlay_future(target, frame, climate, night)
            else:
                self._overlay_sky(target, frame, climate, night)
        elif map_kind == 'geometry':
            if self._geometry_view is None:
                self._geometry_view = target.copy()
            else:
                self._geometry_view.blit(target, (0, 0))
        self._last_state = (travel, frame, night, climate, phase)
        return target

    def _overlay_forest(self, surface, frame, climate, night):
        # Clima existente de Floresta: pólen ou vento_folhas.
        if night > .16:
            n = 8 if self.visual_quality else 4
            for k in range(n):
                x = 28 + (k * 59 + frame // 4) % 410
                y = 92 + (k * 43 + int(5 * math.sin(frame * .035 + k))) % 185
                col = (158, 218, 136) if frame // 18 % 3 else (211, 237, 156)
                pygame.draw.circle(surface, col, (x, y), 2)
        if climate in ('vento_folhas', 'polen', 'vento', 'tempestade_vento'):
            count = 13 if self.visual_quality else 6
            for i in range(count):
                x = int((i * 43 + frame * (2.0 if climate != 'polen' else .65)) % 484) - 12
                y = 24 + (i * 31 + int(math.sin((frame + i * 17) * .065) * 11)) % 215
                pygame.draw.ellipse(surface, (143, 201, 98) if i % 3 else (203, 222, 115), (x, y, 4, 3))
        elif climate in ('chuva', 'tempestade'):
            for i in range(14 if self.visual_quality else 7):
                x = int((i * 47 - frame * 3) % 472)
                y = int((i * 39 + frame * 2) % 245)
                pygame.draw.line(surface, (142, 196, 206), (x, y), (x - 4, y + 11))

    def _overlay_volcano(self, surface, frame, climate, night):
        # Cinzas e chuva de meteoros existentes; nada de superfícies por quadro.
        if night > .12:
            shade = (244, 119, 65) if frame // 12 % 2 else (255, 163, 81)
            for x, y in ((174, 424), (243, 434), (386, 425)):
                pygame.draw.line(surface, shade, (x, y), (x + 31, y), 2)
        for i in range(10 if climate in ('cinzas', 'chuva_meteoros') else 5):
            x = int((i * 79 - frame * .9) % 490) - 10
            y = 45 + int((i * 37 + frame * .43) % 190)
            pygame.draw.ellipse(surface, (133, 119, 120) if i % 3 else (240, 128, 72), (x, y, 3, 3))
        if climate == 'chuva_meteoros':
            for i in range(4 if self.visual_quality else 2):
                x = int((i * 131 - frame * 4.5) % 490)
                y = (i * 67 + frame * 2) % 235
                pygame.draw.line(surface, (255, 197, 94), (x, y), (x - 9, y + 10), 2)

    def _overlay_future(self, surface, frame, climate, night):
        # Janelas de neon reagem à noite; asfalto molhado, sem espelhamento caro.
        if night > .09:
            for x in (46, 129, 213, 314, 395):
                c = (113, 241, 248) if (x + frame // 15) % 3 else (243, 127, 221)
                pygame.draw.line(surface, c, (x, 192), (x, 218), 2)
        if climate in ('chuva_acida', 'vento_neon', 'chuva', 'tempestade'):
            for i in range(15 if self.visual_quality else 7):
                x = int((i * 37 - frame * 3.7) % 465)
                y = int((i * 43 + frame * 2.1) % 245)
                pygame.draw.line(surface, (134, 234, 247), (x, y), (x - 4, y + 12))
            for x in (26, 152, 311, 403):
                pygame.draw.line(surface, (103, 211, 221), (x, 468), (x + 14, 468))

    def _overlay_sky(self, surface, frame, climate, night):
        for i in range(7 if self.visual_quality else 4):
            x = int((i * 91 - frame * .6) % 512) - 25
            y = 44 + (i * 41) % 142
            pygame.draw.ellipse(surface, (225, 242, 251), (x, y, 18, 5))
        for i in range(9 if self.visual_quality else 4):
            x = int((i * 47 + frame * 1.1) % 464)
            y = 74 + (i * 29 + int(6 * math.sin(frame * .05 + i))) % 165
            pygame.draw.circle(surface, (172, 239, 236) if night < .2 else (218, 253, 247), (x, y), 2)
        if climate in ('brisa_celeste', 'tempestade_vento'):
            for i in range(10 if self.visual_quality else 5):
                x = int((i * 53 - frame * (2.6 if climate == 'tempestade_vento' else 1.2)) % 480)
                y = 40 + (i * 39) % 205
                pygame.draw.line(surface, (201, 233, 244), (x, y), (x + 12, y))
        if climate == 'tempestade_vento' and frame % 120 < 4:
            pygame.draw.lines(surface, (246, 252, 254), False, [(307, 85), (294, 113), (321, 118), (300, 151)], 2)
