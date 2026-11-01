"""Cidade 2.2 (v3.117.0): acabamento arquitetonico em pixel art.

Mantem o mesmo contrato de mundo da Cidade 2.0, mas corrige a incoerencia
entre a resolução lógica 450x250 e os buffers 900x500; sprites e mapas
acompanham a mesma escala. A construcao dos chunks e offline no init.
"""
from collections import OrderedDict
import math
import random
import pygame
from pixelrush_city2_v3116 import (
    CityPilotScene as _City116, SpriteLibraryPro as _Library116,
    SpriteInstance, ChunkVariant, WIDTH, SCENE_W, SCENE_H, LOW_W, LOW_H,
    SCALE, DEFAULT_NORMAL, NEUTRAL_FLOW, lerp_color, clamp,
)


class SpriteLibrary(_Library116):
    def _build(self):
        super()._build()
        self.assets['flowerpot'] = self._flowerpot()
        self.assets['clock_post'] = self._clock_post()
        self.assets['cafe_board'] = self._cafe_board()
        self.assets['awning_flowers'] = self._flower_box()

    def _flowerpot(self):
        s = self._blank((12, 18))
        pygame.draw.polygon(s, (165, 106, 76), [(2, 10), (10, 10), (9, 17), (3, 17)])
        pygame.draw.rect(s, (241, 158, 118), (2, 9, 8, 2))
        pygame.draw.line(s, (63, 133, 71), (6, 10), (6, 3), 2)
        pygame.draw.circle(s, (254, 193, 100), (5, 2), 3)
        pygame.draw.circle(s, (228, 95, 153), (9, 6), 3)
        pygame.draw.circle(s, (249, 232, 141), (2, 6), 2)
        return self._make_asset(s, material_color=(164, 127, 97))

    def _clock_post(self):
        s = self._blank((18, 47))
        pygame.draw.rect(s, (69, 58, 80), (8, 14, 3, 32))
        pygame.draw.rect(s, (105, 85, 104), (7, 44, 5, 2))
        pygame.draw.circle(s, (64, 57, 82), (9, 10), 9)
        pygame.draw.circle(s, (247, 225, 176), (9, 10), 7)
        pygame.draw.line(s, (100, 69, 86), (9, 10), (9, 5), 1)
        pygame.draw.line(s, (100, 69, 86), (9, 10), (13, 11), 1)
        return self._make_asset(s, material_color=(130, 114, 110))

    def _cafe_board(self):
        s = self._blank((18, 20))
        pygame.draw.rect(s, (96, 66, 64), (2, 1, 14, 15))
        pygame.draw.rect(s, (45, 65, 59), (4, 3, 10, 11))
        pygame.draw.line(s, (208, 201, 157), (5, 5), (13, 5), 1)
        pygame.draw.line(s, (208, 201, 157), (6, 8), (12, 8), 1)
        pygame.draw.line(s, (142, 97, 70), (4, 15), (1, 19), 2)
        pygame.draw.line(s, (142, 97, 70), (14, 15), (17, 19), 2)
        return self._make_asset(s, material_color=(122, 103, 91))

    def _flower_box(self):
        s = self._blank((25, 12))
        pygame.draw.rect(s, (125, 80, 64), (0, 6, 25, 5))
        pygame.draw.rect(s, (188, 125, 91), (0, 6, 25, 1))
        for i in range(2, 24, 5):
            pygame.draw.line(s, (50, 124, 68), (i, 7), (i, 2), 2)
            pygame.draw.circle(s, (243, 157, 176) if i % 2 else (249, 220, 139), (i, 2), 2)
        return self._make_asset(s, material_color=(150, 115, 90))


class CityPilotScene(_City116):
    def __init__(self):
        # Evita recalcular a mesma textura espelhada durante toda a corrida.
        self._flips = OrderedDict()
        self._flip_limit = 18  # LRU: limita memoria em dispositivos modestos.
        self._glows = {}
        self._sky_cache = OrderedDict()
        self.rand = random.Random(31170)
        self.lib = SpriteLibrary()
        self.layers = self._build_layers()
        self.sky_period = 960
        self._geometry_view = None
        self._last_state = (0.0, 0, 0.0, 'limpo', 0.5)
        # Os assets existentes do pai eram reduzidos (escala lógica 450x250),
        # enquanto o canvas já era 900x500. Aqui escalamos base e mapas uma
        # unica vez na inicialização, eliminando chunks incompletos/flutuantes.
        for layer in self.layers:
            for variant in layer.variants:
                for name in ('image', 'geometry', 'fxmask', 'normal', 'material', 'flow'):
                    tex = getattr(variant, name)
                    if tex.get_size() != (SCENE_W, SCENE_H):
                        setattr(variant, name, pygame.transform.scale(tex, (SCENE_W, SCENE_H)))
        self._build_glows()

    def _build_glows(self):
        for intensity in (0.35, 0.60, 0.85, 1.0):
            glow = pygame.Surface((42, 42), pygame.SRCALPHA)
            for rad, alpha in ((20, 8), (14, 16), (9, 28), (5, 54)):
                pygame.draw.circle(glow, (255, 210, 129, round(alpha * intensity)), (21, 21), rad)
            self._glows[intensity] = glow

    def _surface_flipped(self, surf):
        key = id(surf)
        data = self._flips.get(key)
        if data is not None:
            self._flips.move_to_end(key)
            return data
        mirrored = pygame.transform.flip(surf, True, False)
        self._flips[key] = mirrored
        if len(self._flips) > self._flip_limit:
            self._flips.popitem(last=False)
        return mirrored

    def _draw_building(self, maps, x, base_y, w, h, body, shade, roof=None,
                       win_color=(244, 228, 176), win_lit=(255, 231, 115),
                       night=0.0, material=(143, 118, 128)):
        super()._draw_building(maps, x, base_y, w, h, body, shade, roof,
                               win_color, win_lit, night, material)
        img, mat, geom = maps['image'], maps['material'], maps['geometry']
        y = base_y - h
        if w <= 13 or h <= 22:
            return
        # Beiral + sombras de alvenaria; mesma geometria em todas as variantes.
        trim = tuple(min(255, int(c + (255-c)*0.2)) for c in body)
        dark = tuple(int(c*0.68) for c in shade)
        pygame.draw.rect(img, trim, (x - 1, y, w + 2, 2))
        pygame.draw.line(img, dark, (x, base_y-2), (x + w, base_y-2), 2)
        for off in range(y+11, base_y-6, 23):
            pygame.draw.line(img, dark, (x+2, off), (x+w-2, off), 1)
            pygame.draw.line(mat, material, (x+2, off), (x+w-2, off), 1)
        # Recuo lateral e arremates, sombra de oclusao pintada.
        pygame.draw.rect(img, dark, (x+w-3, y+3, 2, max(1,h-5)))
        pygame.draw.rect(img, trim, (x+1, y+3, 1, max(1,h-5)))
        # Varandas de lojas nas fachadas de primeiro plano.
        if h >= 65 and w >= 25:
            for level in range(base_y - 25, max(y+12, base_y-h+12), -30):
                width=max(12,w-11)
                pygame.draw.rect(img, trim, (x+5, level, width, 3))
                pygame.draw.rect(img, dark, (x+4, level+3, width+2, 1))
                for bx in range(x+7, x+w-7, 8):
                    pygame.draw.rect(img, dark, (bx, level+4, 1, 5))
                pygame.draw.rect(geom, (0, 210, 0), (x+5, level, width, 3))

    def _make_far_variant(self, idx):
        v = super()._make_far_variant(idx)
        # Duas camadas distantes de silhuetas com cobertura variada: completam o horizonte.
        img = v.image; rnd = random.Random(11710+idx)
        # Antenas distantes e torres leves; sempre conectadas aos telhados.
        for i in range(0, LOW_W, 38):
            x = i + rnd.randint(0, 12)
            y = 116 + rnd.randint(-12, 15)
            pygame.draw.line(img, (150, 154, 210), (x, y), (x, y-9), 1)
            pygame.draw.rect(img, (246, 225, 185), (x-1, y-10, 3, 2))
        return v

    def _make_mid_variant(self, idx):
        v = super()._make_mid_variant(idx)
        # Arcos de ponte com volume e sombra, vegetacao junto a pilares.
        img = v.image; geom = v.geometry; mat = v.material
        y = 171 + (idx % 3)*5
        for x in range(12, LOW_W, 46):
            pygame.draw.line(img, (103, 116, 164), (x, y+8), (x, y+34), 3)
            pygame.draw.line(img, (170, 189, 218), (x+2, y+8), (x+2, y+31), 1)
            pygame.draw.line(geom, (0, 180, 0), (x, y+8), (x, y+34), 3)
            pygame.draw.line(mat, (107, 122, 140), (x, y+8), (x, y+34), 3)
            pygame.draw.circle(img, (82, 147, 101), (x+5, y+30), 6)
        # O reflexo existente permanece restrito à água.
        return v

    def _make_near_variant(self, idx):
        v = super()._make_near_variant(idx)
        img, geom, mat = v.image, v.geometry, v.material
        # Dois quarteiroes intercalados ocupam a faixa que estava vazia entre
        # o centro e as fachadas laterais. Sao cenografia, sem hitboxes novas.
        rnd = random.Random(11730+idx)
        for x, width, height, body, shadow in (
            (92, 72, 67+idx%4*3, (213, 174, 145), (163, 125, 108)),
            (LOW_W-164, 74, 71+(idx*3)%9, (186, 152, 171), (143, 111, 130)),
        ):
            self._draw_building(v.__dict__, x, LOW_H-9, width, height,
                                body, shadow,
                                roof=('clock' if idx%3==0 else 'tower' if idx%3==1 else None),
                                win_color=(250, 234, 211),win_lit=(255,226,142),
                                material=(157,127,129))
            # Lojas completas e vitrines sob as fachadas.
            self._draw_shopfront(v.__dict__, x+5, LOW_H-36, width-10,
                                 ((186,133,119), (230,119,151), (255,216,132)),
                                 striped=(idx%2==0))
            # floreiras nas varandas ficam presas à fachada.
            pygame.draw.rect(img, (117,85,79), (x+9,LOW_H-49,width-18,3))
            pygame.draw.rect(geom,(0,210,0),(x+9,LOW_H-49,width-18,3))
            pygame.draw.rect(mat,(142,104,96),(x+9,LOW_H-49,width-18,3))
            for fx in range(x+12,x+width-10,11):
                pygame.draw.rect(img,(69,153,84),(fx,LOW_H-54,6,5))
                pygame.draw.rect(img,(238,145,165),(fx+2,LOW_H-56,2,3))
        # Tijolinhos irregulares nas regiões de fachadas, sem afetar hitboxes.
        for side in (0, LOW_W-67):
            for yy in range(153, LOW_H-24, 14):
                for xx in range(side+6+(yy//14)%2*5, min(side+62,LOW_W), 13):
                    pygame.draw.line(img, (238, 194, 166), (xx, yy), (xx+6, yy), 1)
        # Pavimentacao leve sem aumentar destaque dos obstaculos.
        for xx in range(0, LOW_W, 14):
            pygame.draw.line(img, (149, 134, 122), (xx, LOW_H-4), (xx+7, LOW_H-4), 1)
        # Elementos independentes e presos por ancora fisica na calçada.
        cx=LOW_W//2-36
        v.sprites.extend([
            SpriteInstance('clock_post', 120+idx%3*8, LOW_H-8),
            SpriteInstance('flowerpot', cx-20, LOW_H-8, sway=.4, phase=idx*.5),
            SpriteInstance('flowerpot', cx+84, LOW_H-8, sway=.4, phase=idx*.3),
            SpriteInstance('awning_flowers', cx+14, LOW_H-41),
            SpriteInstance('cafe_board', cx+18, LOW_H-9),
            SpriteInstance('flowerpot', 108, LOW_H-8),
            SpriteInstance('flowerpot', LOW_W-110, LOW_H-8),
        ])
        return v

    def _make_fg_variant(self, idx):
        v = super()._make_fg_variant(idx)
        # Planta nas extremidades: a pista fica sem poluicao visual.
        v.sprites.append(SpriteInstance('flowerpot', 28, 212, sway=0.5, phase=idx*.6))
        v.sprites.append(SpriteInstance('flowerpot', LOW_W-45, 215, sway=0.5, phase=idx*.9))
        return v

    def _draw_sprite(self, surface, kind, x, y, frame, night, climate, map_kind='image', flip=False):
        asset = self.lib.assets[kind]
        tex = getattr(asset, map_kind)
        if flip:
            tex = self._surface_flipped(tex)
        rect = tex.get_rect(bottomleft=(x, y))
        surface.blit(tex, rect)
        if map_kind == 'image' and kind == 'lamp' and night > 0.08:
            level = min(self._glows, key=lambda v: abs(v-night))
            glow=self._glows[level]
            surface.blit(glow, (rect.centerx-21,rect.top+3))

    def _render_chunk(self, target, variant, flip, x, frame, night, climate, phase, map_kind='image', only_sprites=False):
        base = getattr(variant,map_kind)
        if not only_sprites:
            target.blit(self._surface_flipped(base) if flip else base, (x,0))
        wind_boost = 1.7 if climate in ('vento','tempestade','nevasca','tempestade_areia') else 1.0
        for sp in variant.sprites:
            asset=self.lib.assets[sp.kind]
            width = getattr(asset,map_kind).get_width()
            dx = int(round(math.sin(frame*.03 + sp.phase)*sp.sway*wind_boost))
            dy = int(round(math.sin(frame*.04 + sp.phase)*sp.bob))
            px = int(x) + (SCENE_W - sp.x*SCALE - width if flip else sp.x*SCALE) + (-dx if flip else dx)
            py = (sp.y*SCALE)+dy
            if px >= WIDTH+6 or px+width <= -6:
                continue
            self._draw_sprite(target, sp.kind, px, py, frame, night, climate, map_kind, flip)

    def render_scene(self,target,travel,frame,night,climate,phase,foreground_only=False,map_kind='image'):
        # Reutiliza a ordem de camadas e todos os mapas da implementacao anterior;
        # corrige a iluminacao noturna: remover o banho amarelo global que
        # antes estourava a imagem toda. Luz deve partir de fontes reais.
        if not foreground_only:
            if map_kind == 'image':
                self._draw_sky(target,travel,frame,night,phase,climate)
            elif map_kind == 'normal':target.fill(DEFAULT_NORMAL)
            elif map_kind == 'flow':target.fill(NEUTRAL_FLOW)
            else:target.fill((0,0,0,0))
        for layer in self.layers:
            if layer.foreground != foreground_only:continue
            for x,variant,flipped in self._layer_tiles(travel,layer):
                self._render_chunk(target,variant,flipped,int(x),frame,night,climate,phase,map_kind)
            if layer.name=='mid' and not foreground_only:
                self._draw_train(target,travel,frame,night,map_kind)
        if map_kind=='image' and not foreground_only:
            self._draw_traffic(target,frame,night)
            self._draw_birds(target,frame,map_kind)
        if map_kind=='image' and not foreground_only and night>0.16:
            dark=pygame.Surface((WIDTH,SCENE_H),pygame.SRCALPHA)
            dark.fill((23,31,61,int(45*night)))
            target.blit(dark,(0,0))
        if map_kind=='image' and not foreground_only and climate in ('tempestade','chuva'):
            for i in range(22 if climate=='chuva' else 34):
                rx=int((i*37-frame*(3.4 if climate=='chuva' else 6.5))%(WIDTH+30))-15
                ry=int((i*43+frame*7.2)%SCENE_H)
                pygame.draw.line(target,(160,209,250,100),(rx,ry),(rx-6,ry+13),1)
        if map_kind=='geometry' and not foreground_only:
            self._geometry_view=target.copy()
        self._last_state=(travel,frame,night,climate,phase)
