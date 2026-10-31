"""Pixel Rush v3.166.0 — passe premium global em todos os cenários spriteados.

Escopo desta versão:
- refino visual em neve, deserto, vulcão, floresta, cidade futurista e ilhas celestes;
- correção preventiva de emendas/rodapés nas camadas modularizadas;
- decoração adicional ancorada, sem roubar a leitura da pista;
- contraste/atmosfera mais consistentes de dia e de noite;
- zero mudança em física, spawn, hitboxes ou ameaças.
"""
from __future__ import annotations
import math
import random
import pygame
from pixelrush_biomes2_v3165 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, LH, WIDTH


class ModularBiomeScene(Previous):
    PREMIUM_BIOMES = ('neve','deserto','vulcao','floresta','cidade_futurista','ilhas_celestes')
    PALETTE = {
        'neve': {
            'seal': (218, 238, 250), 'shade': (92, 126, 170), 'spark': (255,255,255),
            'fog_day': (196, 223, 242, 32), 'fog_night': (126, 151, 192, 22),
        },
        'deserto': {
            'seal': (238, 196, 123), 'shade': (168, 112, 72), 'spark': (255, 222, 158),
            'fog_day': (241, 195, 122, 28), 'fog_night': (156, 116, 96, 16),
        },
        'vulcao': {
            'seal': (255, 143, 69), 'shade': (96, 48, 49), 'spark': (255, 209, 119),
            'fog_day': (189, 113, 92, 28), 'fog_night': (136, 82, 88, 22),
        },
        'floresta': {
            'seal': (128, 191, 104), 'shade': (56, 88, 56), 'spark': (198, 230, 145),
            'fog_day': (101, 150, 92, 23), 'fog_night': (62, 98, 72, 18),
        },
        'cidade_futurista': {
            'seal': (98, 241, 255), 'shade': (34, 60, 93), 'spark': (214, 116, 255),
            'fog_day': (82, 220, 236, 22), 'fog_night': (131, 89, 186, 24),
        },
        'ilhas_celestes': {
            'seal': (220, 243, 246), 'shade': (96, 154, 194), 'spark': (176, 233, 197),
            'fog_day': (176, 214, 226, 20), 'fog_night': (117, 149, 191, 18),
        },
    }

    def __init__(self, biome):
        super().__init__(biome)
        if biome in self.PREMIUM_BIOMES:
            self._build_global_overlays()
            self._apply_global_premium_pass()
            if hasattr(self, '_map_cache'):
                self._map_cache.clear()
            if hasattr(self, '_composites'):
                self._composites.clear()

    def _build_global_overlays(self):
        pal=self.PALETTE[self.biome]
        self._premium_overlay_day=pygame.Surface((WIDTH, 164), pygame.SRCALPHA)
        self._premium_overlay_night=pygame.Surface((WIDTH, 164), pygame.SRCALPHA)
        fd=pal['fog_day']; fn=pal['fog_night']
        for y in range(164):
            t=y/163.0
            ad=int(fd[3]*(0.15+0.85*t*t))
            an=int(fn[3]*(0.15+0.85*t*t))
            pygame.draw.line(self._premium_overlay_day, (*fd[:3], ad), (0,y), (WIDTH-1,y),1)
            pygame.draw.line(self._premium_overlay_night, (*fn[:3], an), (0,y), (WIDTH-1,y),1)
        rng=random.Random(316600 + hash(self.biome)%1000)
        for idx in range(12):
            x=rng.randrange(-10, WIDTH-40); y=rng.randrange(18, 150); w=rng.randrange(20, 84)
            pygame.draw.line(self._premium_overlay_day, (*pal['spark'], 6 + (idx%3)*2), (x,y), (x+w,y),1)
            pygame.draw.line(self._premium_overlay_night, (*pal['spark'], 7 + (idx%4)*2), (x,y), (x+w,y),1)

    def _apply_global_premium_pass(self):
        for layer, chunks in self._layers.items():
            for idx, surf in enumerate(chunks):
                self._seal_chunk_edges(surf, layer)
                self._paint_foundation(surf, layer, idx)
                self._add_depth_microdetail(surf, layer, idx)
                if layer == 'far':
                    self._add_far_landmark(surf, idx)
                elif layer == 'mid':
                    self._add_mid_landmark(surf, idx)
                else:
                    self._add_near_shoulder_detail(surf, idx)
                    self._trim_low_visual_noise(surf)

    def _seal_chunk_edges(self, surf, layer):
        pal=self.PALETTE[self.biome]
        ys = {'far': (218,220,222), 'mid': (214,216,218), 'near': (225,232,242,248)}[layer]
        for y in ys:
            pygame.draw.line(surf, pal['shade'], (0,y), (LW-1,y), 1)
        for y in ys[:2]:
            surf.set_at((0,y), pal['shade'])
            surf.set_at((LW-1,y), pal['shade'])
        if layer == 'near':
            pygame.draw.line(surf, pal['seal'], (0,224), (LW-1,224), 1)

    def _paint_foundation(self, surf, layer, idx):
        pal=self.PALETTE[self.biome]
        if layer == 'far':
            pygame.draw.rect(surf, (*pal['shade'], 26), (0, 205, LW, 18))
        elif layer == 'mid':
            pygame.draw.rect(surf, (*pal['shade'], 18), (0, 214, LW, 14))
            for x in range(10, LW, 42):
                pygame.draw.line(surf, (*pal['seal'], 80), (x, 216 + (x//21)%2), (x+12, 216 + (x//21)%2), 1)
        else:
            pygame.draw.rect(surf, (*pal['shade'], 20), (0, 224, LW, 8))
            for x in range(7, LW, 26):
                pygame.draw.line(surf, (*pal['seal'], 96), (x, 228 + (x//13)%2), (min(LW-1,x+8), 228 + (x//13)%2), 1)
            if self.biome in ('cidade_futurista','ilhas_celestes','vulcao'):
                y=236 if self.biome!='vulcao' else 239
                for x in range(12, LW-12, 58):
                    pygame.draw.line(surf, (*pal['spark'], 125), (x, y), (x+10, y), 1)

    def _add_depth_microdetail(self, surf, layer, idx):
        pal=self.PALETTE[self.biome]
        rng=random.Random(316610 + idx*37 + len(layer)*11 + len(self.biome)*13)
        band_top = 138 if layer == 'far' else (158 if layer == 'mid' else 205)
        band_bottom = 212 if layer == 'far' else (220 if layer == 'mid' else 246)
        count = 8 if layer == 'far' else (9 if layer == 'mid' else 11)
        for n in range(count):
            x=rng.randrange(0, LW-14)
            y=rng.randrange(band_top, band_bottom)
            w=rng.randrange(6, 18)
            pygame.draw.line(surf, (*pal['shade'], 42), (x,y), (x+w, y+rng.choice((-1,0,1))), 1)
            if n % 3 == 0:
                pygame.draw.line(surf, (*pal['spark'], 36), (x+2, y-1), (x+max(3,w//2), y-1), 1)

    def _add_far_landmark(self, surf, idx):
        pal=self.PALETTE[self.biome]
        if self.biome == 'neve' and idx % 2 == 0:
            self._spire(surf, 38 + (idx*23)%120, 196, 22, pal['shade'], pal['seal'])
        elif self.biome == 'deserto' and idx % 3 == 1:
            self._dune_arch(surf, 34 + (idx*17)%110, 208, 44, pal['shade'], pal['seal'])
        elif self.biome == 'floresta' and idx % 2 == 1:
            self._tree_mass(surf, 28 + (idx*19)%130, 205, 28, pal['shade'], pal['seal'])
        elif self.biome == 'cidade_futurista' and idx % 2 == 0:
            self._skybridge(surf, 26 + (idx*29)%124, 184, 72, pal['shade'], pal['spark'])
        elif self.biome == 'ilhas_celestes':
            self._floating_islet(surf, 32 + (idx*31)%120, 176, 54, pal['shade'], pal['spark'])

    def _add_mid_landmark(self, surf, idx):
        pal=self.PALETTE[self.biome]
        if self.biome == 'neve':
            self._banner_posts(surf, 24 + (idx*19)%110, 210, pal['shade'], pal['seal'])
        elif self.biome == 'deserto':
            self._stone_outcrop(surf, 25 + (idx*17)%130, 214, 26, pal['shade'], pal['seal'])
        elif self.biome == 'floresta':
            self._vine_arch(surf, 28 + (idx*21)%122, 213, pal['shade'], pal['seal'])
        elif self.biome == 'cidade_futurista':
            self._hover_lane(surf, 20 + (idx*27)%120, 191, 78, pal['seal'], pal['spark'])
        elif self.biome == 'ilhas_celestes':
            self._marble_monument(surf, 34 + (idx*23)%120, 212, pal['shade'], pal['spark'])
        elif self.biome == 'vulcao' and idx % 4 == 1:
            self._ember_totem(surf, 26 + (idx*19)%120, 213, pal['shade'], pal['spark'])

    def _add_near_shoulder_detail(self, surf, idx):
        pal=self.PALETTE[self.biome]
        xs=(12, 24, LW-34, LW-20)
        if self.biome == 'neve':
            for x in xs[:2]:
                pygame.draw.line(surf, (232,245,252), (x, 230), (x+2, 224), 1)
            for x in xs[2:]:
                pygame.draw.line(surf, (187,214,232), (x, 231), (x+3, 225), 1)
        elif self.biome == 'deserto':
            for x in xs:
                pygame.draw.arc(surf, (228,190,122), (x, 236, 12, 4), math.radians(180), math.radians(360), 1)
        elif self.biome == 'vulcao':
            for x in (18, LW-28):
                pygame.draw.polygon(surf, (76,55,60), [(x, 247),(x+5,239),(x+10,247)])
                pygame.draw.rect(surf, (255,132,67), (x+4,243,2,1))
        elif self.biome == 'floresta':
            for x in (14,28,LW-29):
                pygame.draw.line(surf, (114,178,96), (x,248), (x+1,241), 1)
        elif self.biome == 'cidade_futurista':
            for x in (16, LW-30):
                pygame.draw.line(surf, (82,232,244), (x, 243), (x+9,243), 1)
                pygame.draw.line(surf, (227,114,255), (x+2,246), (x+6,246), 1)
        elif self.biome == 'ilhas_celestes':
            for x in (15, LW-32):
                pygame.draw.line(surf, (186,236,221), (x,244), (x+6,239), 1)
                pygame.draw.line(surf, (219,253,238), (x+2,246), (x+9,240), 1)

    def _trim_low_visual_noise(self, surf):
        # Limpa micro-ruídos no miolo da pista para reduzir poluição visual.
        center=pygame.Rect(44, 236, LW-88, 14)
        veil=pygame.Surface((center.w, center.h), pygame.SRCALPHA)
        pygame.draw.rect(veil, (18, 22, 30, 18), (0,0,center.w,center.h))
        surf.blit(veil, center.topleft)

    # pequenos desenhos auxiliares
    def _spire(self, surf, x, base, h, dark, hi):
        pygame.draw.polygon(surf, dark, [(x,base),(x+5,base-h+7),(x+10,base-h),(x+15,base-h+7),(x+18,base)])
        pygame.draw.line(surf, hi, (x+10, base-h+3), (x+10, base-3), 1)

    def _dune_arch(self, surf, x, base, w, dark, hi):
        pygame.draw.arc(surf, dark, (x, base-24, w, 20), math.radians(180), math.radians(360), 2)
        pygame.draw.line(surf, hi, (x+8, base-15), (x+w-8, base-15), 1)

    def _tree_mass(self, surf, x, base, h, dark, hi):
        pygame.draw.rect(surf, dark, (x+10, base-h+7, 4, h))
        pygame.draw.polygon(surf, dark, [(x,base-h+14),(x+13,base-h),(x+28,base-h+12),(x+18,base-h+20),(x+3,base-h+19)])
        pygame.draw.line(surf, hi, (x+8, base-h+10), (x+18, base-h+6), 1)

    def _skybridge(self, surf, x, y, w, dark, hi):
        pygame.draw.line(surf, dark, (x,y), (x+w,y), 3)
        pygame.draw.line(surf, hi, (x+10,y-1), (x+w-10,y-1), 1)
        for px in (x+14, x+w-15):
            pygame.draw.line(surf, dark, (px,y), (px, y+13), 2)

    def _floating_islet(self, surf, x, y, w, dark, hi):
        pygame.draw.polygon(surf, dark, [(x,y+12),(x+10,y),(x+w-15,y+2),(x+w,y+14),(x+w-8,y+18),(x+12,y+17)])
        pygame.draw.line(surf, hi, (x+10,y+4), (x+w-16,y+4), 1)
        pygame.draw.line(surf, hi, (x+w//2,y+17), (x+w//2-4,y+25), 1)

    def _banner_posts(self, surf, x, base, dark, hi):
        for px in (x, x+24):
            pygame.draw.line(surf, dark, (px, base), (px, base-20), 2)
        pygame.draw.line(surf, hi, (x+2, base-18), (x+22, base-18), 1)

    def _stone_outcrop(self, surf, x, base, h, dark, hi):
        pygame.draw.polygon(surf, dark, [(x,base),(x+6,base-h+12),(x+15,base-h),(x+28,base-h+9),(x+34,base)])
        pygame.draw.line(surf, hi, (x+10, base-h+9), (x+21, base-h+5), 1)

    def _vine_arch(self, surf, x, base, dark, hi):
        pygame.draw.line(surf, dark, (x+2,base), (x+8, base-26), 2)
        pygame.draw.line(surf, dark, (x+30,base), (x+24, base-26), 2)
        pygame.draw.arc(surf, hi, (x+5, base-28, 20, 14), math.radians(180), math.radians(360), 1)

    def _hover_lane(self, surf, x, y, w, seal, spark):
        pygame.draw.line(surf, seal, (x,y), (x+w,y), 2)
        for px in range(x+6, x+w-5, 18):
            pygame.draw.line(surf, spark, (px, y+3), (px+5, y+3), 1)

    def _marble_monument(self, surf, x, base, dark, spark):
        pygame.draw.rect(surf, (184, 205, 214), (x+8, base-28, 18, 24))
        pygame.draw.rect(surf, (146, 176, 188), (x+6, base-4, 22, 4))
        pygame.draw.arc(surf, spark, (x+6, base-32, 20, 8), math.radians(180), math.radians(360), 1)
        pygame.draw.line(surf, dark, (x+17, base-28), (x+17, base-9), 1)

    def _ember_totem(self, surf, x, base, dark, spark):
        pygame.draw.rect(surf, dark, (x+7, base-23, 8, 20))
        pygame.draw.line(surf, spark, (x+10, base-21), (x+10, base-9), 1)
        pygame.draw.line(surf, spark, (x+8, base-14), (x+14, base-14), 1)

    def _overlay_harmony(self, surf, frame, climate, night):
        super()._overlay_harmony(surf, frame, climate, night)
        if self.biome not in self.PREMIUM_BIOMES or self.biome == 'vulcao':
            return
        surf.blit(self._premium_overlay_night if night > .35 else self._premium_overlay_day, (0, 146))
        # microefeitos baratos por bioma para dar vida sem poluição.
        low=not bool(getattr(self,'visual_quality',1))
        count = 3 if low else 5
        if self.biome == 'neve':
            for i in range(count):
                x=int((frame*0.35 + i*91)%(WIDTH+10))-5; y=205 + (i*27 + frame//3)%150
                pygame.draw.line(surf, (240,248,255,48), (x,y), (x+1,y+2), 1)
        elif self.biome == 'deserto':
            for i in range(count):
                x=int((i*123 - frame*0.22)%(WIDTH+20))-10; y=396 + (i*11)%18
                pygame.draw.line(surf, (246, 212, 153, 18), (x,y), (min(WIDTH,x+18),y), 1)
        elif self.biome == 'floresta' and night > .2:
            for i in range(count):
                x=int((i*79 + frame*0.19)%(WIDTH-20))+10; y=292 + (i*41)%130
                pygame.draw.rect(surf, (195, 236, 134, 36), (x,y,2,2))
        elif self.biome == 'cidade_futurista':
            for i in range(count):
                x=int((i*87 + frame*0.28)%(WIDTH-30))+8; y=268 + (i*33)%132
                pygame.draw.line(surf, (83, 233, 245, 28), (x,y), (x+8,y), 1)
        elif self.biome == 'ilhas_celestes':
            for i in range(count):
                x=int((i*93 + frame*0.17)%(WIDTH-30))+8; y=255 + (i*29)%140
                pygame.draw.line(surf, (182, 235, 220, 28), (x,y), (x+6, y-4), 1)
