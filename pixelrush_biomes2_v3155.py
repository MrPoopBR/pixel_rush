"""v3.155 — reconstrução premium da Cidade Futurista.

Escopo desta versão:
- limpar a composição do bioma cidade_futurista;
- corrigir sensação de peças cortadas / mal encaixadas;
- reduzir poluição visual;
- melhorar silhueta, profundidade e acabamento;
- adicionar vida de forma controlada.

Todo o restante dos biomas permanece herdado da v3.154.0.
"""
import math
import random
import pygame
from pixelrush_biomes2_v3151 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, WIDTH

CH = 250

class ModularBiomeScene(Previous):
    def __init__(self, biome):
        super().__init__(biome)
        if biome == 'cidade_futurista':
            self._rebuild_future_city()
            self._future_car_sprites = {(kind, phase): self._future_car_art(kind, phase)
                                        for kind in range(3) for phase in range(2)}
            self._future_car_flip_sprites = {(kind, phase): pygame.transform.flip(sprite, True, False)
                                            for (kind,phase), sprite in self._future_car_sprites.items()}
            self._map_cache.clear()

    def _surface(self):
        return pygame.Surface((LW, CH), pygame.SRCALPHA)

    # ----------------------------- city rebuild -----------------------------
    def _rebuild_future_city(self):
        # mais variedade de loops para parecer uma cidade bem maior
        self._layers['far'] = [self._future_far_chunk(i) for i in range(12)]
        self._layers['mid'] = [self._future_mid_chunk(i) for i in range(14)]
        self._layers['near'] = [self._future_near_chunk(i) for i in range(16)]

    def _future_far_chunk(self, index):
        """12 trechos distantes únicos: edifícios com pés e coroas completos."""
        pal = self.FUTURE
        s = self._surface()
        rng = random.Random(155500 + index * 101)
        # Corpos contidos nos limites do chunk, sem telhados/fachadas cortados.
        slots = [(7, 34), (47, 34), (87, 34), (127, 37), (174, 40)]
        anchor = (index * 7 + 2) % len(slots)
        for n, (x, maxw) in enumerate(slots):
            w = maxw - rng.randrange(0, 6)
            h = rng.randrange(58, 93)
            if n == anchor:
                h = rng.randrange(115, 143)
                w = min(maxw, w + 1)
            top = 214 - h
            c0 = ((42, 57, 91), (46, 62, 96), (49, 64, 101))[((index // 3) + n) % 3]
            c1 = (63, 85, 125) if n == anchor else (70, 92, 128)
            self._future_building(s, x, 214, w, h, c0, (31, 44, 73), c1, pal['alt'],
                                  roof=(index+n)%3, window_step=7, window_size=1,
                                  row_gap=8, border=False)
            if n == anchor:
                self._future_landmark(s, x, top, w, h, seed=index * 11 + n, distant=True)
            else:
                # luzes de navegação integradas ao teto (sem painel solto)
                if (index+n) % 4 == 0:
                    pygame.draw.line(s, (131, 187, 204), (x + w//2, top-4), (x+w//2, top+2), 1)
                    pygame.draw.rect(s, pal['spark'], (x+w//2-1, top-5, 2, 2))
        # Plataforma/horizonte inferior contínuo nesta profundidade.
        pygame.draw.rect(s, (45, 62, 98), (0, 212, LW, 5))
        pygame.draw.line(s, (93, 127, 151), (0, 212), (LW-1, 212), 1)
        return s

    def _future_mid_chunk(self, index):
        """14 distritos de fachadas diversas, painéis fixos e aerovias apoiadas."""
        pal = self.FUTURE
        s = self._surface()
        rng = random.Random(155900 + index * 137)
        slots = ((8, 28), (42, 32), (79, 27), (111, 35), (152, 31), (188, 29))
        district = index % 5
        accent_cycle = ((pal['hi'], pal['spark']), (pal['spark'], pal['alt']),
                        (pal['alt'], pal['hi']))
        for n, (x, maxw) in enumerate(slots):
            w = maxw - rng.randrange(0, 4)
            h = rng.randrange(45, 78)
            if n in ((index+1)%6, (index+4)%6):
                h += rng.randrange(12, 25)
            top = 214 - h
            col1, col2 = accent_cycle[(district + n) % 3]
            body = ((66, 87, 124), (74, 91, 134), (65, 85, 118),
                    (77, 93, 131), (69, 92, 133))[(n + index) % 5]
            self._future_building(s, x, 214, w, h, body, (42, 57, 91), col1, col2,
                                  roof=(index * 3 + n) % 3,
                                  window_step=7 if index % 2 else 6,
                                  window_size=1 if n % 3 == 0 else 2,
                                  row_gap=8 if index % 3 else 9, border=True)
            if h >= 66 and w >= 27 and (n+index) % 3 == 0:
                # Não ultrapassa limites do edifício: prende o letreiro à fachada.
                self._future_facade_panel(s, x + 5, top + 16,
                                          min(w-10, 19), 7, col1, col2)
            if h >= 80:
                self._future_landmark(s, x, top, w, h, seed=300+index * 11 + n, distant=False)
            if n % 3 == 1 and w > 26:
                self._future_accent_facade(s, x, top, w, h, col1)
        # Passarelas somente com extremidades ancoradas aos edifícios da mesma faixa:
        # não desenhar plataformas suspensas atravessando fachadas independentes.
        # Seus suportes descem até o rodapé estrutural.
        for n, (x, w) in enumerate(((70, 12), (140, 13))):
            y = 192 + ((index + n) % 2)
            pygame.draw.rect(s, (59, 77, 114), (x, y, w, 4))
            pygame.draw.line(s, pal['alt'], (x+1,y), (x+w-2,y), 1)
            pygame.draw.line(s, (48, 63, 96), (x+2, y+4), (x+2, 212), 2)
            pygame.draw.line(s, (48, 63, 96), (x+w-3, y+4), (x+w-3, 212), 2)
        pygame.draw.rect(s, (53, 71, 105), (0, 211, LW, 6))
        pygame.draw.line(s, (90, 124, 153), (0, 211), (LW-1, 211), 1)
        return s

    def _future_landmark(self, s, x, top, w, h, seed, distant):
        """Coroa monumental conectada ao corpo, sempre dentro do edifício."""
        style = seed % 4
        cx = x + w//2
        base = (31, 44, 73) if distant else (45, 58, 92)
        edge = (94, 141, 177) if distant else (161, 200, 220)
        if style == 0:  # torre de observação com espira
            pygame.draw.rect(s, base, (cx-8, top-7, 16, 7))
            pygame.draw.line(s, edge, (cx-6, top-7), (cx+5, top-7), 1)
            pygame.draw.line(s, edge, (cx, top-14), (cx, top-7), 1)
            pygame.draw.rect(s, (224, 135, 219), (cx-1, top-15, 3, 2))
        elif style == 1:  # plataformas escalonadas
            pygame.draw.rect(s, base, (x+5, top-4, w-10, 4))
            pygame.draw.rect(s, base, (x+10, top-9, w-20, 5))
            pygame.draw.line(s, edge, (x+6, top-5), (x+w-7, top-5), 1)
        elif style == 2:  # arco corporativo sustentado em duas colunas
            pygame.draw.line(s, base, (x+6, top), (x+6, top-10), 3)
            pygame.draw.line(s, base, (x+w-7, top), (x+w-7, top-10), 3)
            pygame.draw.rect(s, base, (x+6, top-12, w-12, 4))
            pygame.draw.line(s, edge, (x+9, top-12), (x+w-10, top-12), 1)
        else:  # antenas/heliporto com base física
            pygame.draw.rect(s, base, (cx-10, top-3, 20, 3))
            pygame.draw.rect(s, base, (cx-4, top-7, 8, 4))
            pygame.draw.line(s, edge, (cx, top-13), (cx, top-7), 1)
            pygame.draw.rect(s, (125, 232, 231), (cx-1, top-14, 2, 2))
        # janelas panorâmicas na própria fachada
        if not distant and h > 72:
            pygame.draw.rect(s, (32, 51, 81), (x+5, top+5, w-10, 5))
            pygame.draw.line(s, edge, (x+7, top+7), (x+w-8, top+7), 1)

    @staticmethod
    def _future_accent_facade(s, x, top, w, h, accent):
        """Frisos de fachada com terminações; sem traços livres no ar."""
        pygame.draw.line(s, (41, 57, 90), (x+w-5, top+11), (x+w-5, top+h-12), 2)
        for y in range(top+14, top+h-12, 14):
            pygame.draw.rect(s, accent, (x+w-6, y, 2, 2))

    def _future_near_chunk(self, index):
        pal = self.FUTURE
        s = self._surface()
        # grande base urbana: resolve sensação de prédios flutuando
        deck_top = 182
        deck_mid = 198
        deck_bottom = 218
        water_top = 222
        # paredão inferior da cidade / subestrutura
        pygame.draw.rect(s, (51, 71, 108), (0, deck_top, LW, deck_bottom - deck_top))
        pygame.draw.rect(s, (39, 54, 84), (0, deck_mid, LW, deck_bottom - deck_mid))
        pygame.draw.line(s, pal['hi'], (0, deck_top + 3), (LW, deck_top + 3), 1)
        pygame.draw.line(s, pal['spark'], (0, deck_mid + 2), (LW, deck_mid + 2), 1)
        # blocos baixos integrados à base
        modules = [
            [(6, 176, 28, 20), (40, 170, 34, 24), (152, 174, 24, 18), (181, 168, 36, 26)],
            [(10, 172, 26, 22), (42, 176, 30, 18), (148, 170, 30, 24), (184, 174, 28, 20)],
            [(8, 170, 30, 24), (44, 174, 26, 20), (150, 176, 24, 18), (178, 170, 34, 24)],
            [(10, 176, 24, 18), (38, 168, 36, 26), (150, 172, 28, 22), (184, 176, 26, 18)],
            [(14, 170, 28, 24), (48, 176, 24, 18), (146, 168, 34, 26), (184, 174, 24, 20)],
            [(6, 174, 32, 20), (44, 168, 28, 24), (154, 174, 26, 18), (184, 169, 30, 24)],
            [(8, 168, 30, 24), (44, 174, 28, 18), (150, 170, 28, 22), (184, 176, 24, 18)],
            [(12, 174, 24, 18), (40, 169, 34, 24), (149, 174, 24, 18), (178, 168, 36, 26)],
        ]
        for n, (x, y, w, h) in enumerate(modules[index % len(modules)]):
            body = (67, 88, 129) if n % 2 == 0 else (58, 77, 116)
            pygame.draw.rect(s, body, (x, y, w, h))
            pygame.draw.rect(s, (42, 58, 88), (x, y + h - 4, w, 4))
            pygame.draw.line(s, pal['hi'] if n % 2 == 0 else pal['spark'], (x + 2, y + 3), (x + w - 3, y + 3), 1)
            if w > 24:
                pygame.draw.line(s, pal['alt'], (x + 3, y + 8), (x + w - 4, y + 8), 1)
        # passarela/avenida superior contínua para sustentar a cidade
        avenue_y = 194
        pygame.draw.rect(s, (78, 101, 145), (0, avenue_y, LW, 8))
        pygame.draw.line(s, pal['hi'], (0, avenue_y + 1), (LW, avenue_y + 1), 1)
        pygame.draw.line(s, pal['spark'], (0, avenue_y + 6), (LW, avenue_y + 6), 1)
        # grades / guarda-corpo
        for x in range(0, LW, 18):
            pygame.draw.line(s, (102, 126, 176), (x, avenue_y), (x, avenue_y - 7), 1)
        # pilares descendo até a água/faixa inferior
        pillar_sets = [18, 50, 86, 132, 176, 208] if index % 2 == 0 else [10, 42, 78, 120, 164, 200]
        for x in pillar_sets:
            pygame.draw.rect(s, (45, 60, 92), (x, avenue_y + 8, 6, 28))
            pygame.draw.line(s, (90, 110, 154), (x + 2, avenue_y + 8), (x + 2, avenue_y + 35), 1)
            pygame.draw.line(s, (68, 86, 124), (x, avenue_y + 17), (x - 4, avenue_y + 35), 1)
            pygame.draw.line(s, (68, 86, 124), (x + 6, avenue_y + 17), (x + 10, avenue_y + 35), 1)
        # faixa inferior tecnológica / canal refletivo acima da pista
        # Canal urbano menos saturado; emendas horizontais ininterruptas.
        pygame.draw.rect(s, (31, 76, 112), (0, water_top, LW, 12))
        pygame.draw.line(s, (79, 174, 191), (0, water_top), (LW-1, water_top), 1)
        for x in range(10, LW-8, 36):
            c = (103, 204, 221) if (x // 36 + index) % 2 == 0 else (133, 102, 167)
            pygame.draw.line(s, c, (x, water_top + 4), (x+6, water_top+4), 1)
            pygame.draw.line(s, (54, 121, 156), (x+3, water_top+8), (x+9, water_top+8), 1)
        # jardineiras e vegetação holográfica discretas na avenida alta
        planter_sets = [((78, 187, 18), (128, 187, 20)), ((88, 187, 20), (138, 187, 18)), ((96, 187, 18), (124, 187, 18)), ((72, 187, 18), (142, 187, 18)), ((84, 187, 18), (132, 187, 18))]
        for x, y, w in planter_sets[index % len(planter_sets)]:
            pygame.draw.rect(s, (74, 92, 128), (x, y, w, 6))
            pygame.draw.line(s, pal['spark'], (x + 1, y + 1), (x + w - 2, y + 1), 1)
            self._future_small_plants(s, x + 3, y, w - 6)
        # luzes da borda da avenida
        for x in range(12, LW - 12, 24):
            c = pal['hi'] if ((x // 24) + index) % 2 == 0 else pal['spark']
            pygame.draw.line(s, c, (x, avenue_y - 2), (x + 6, avenue_y - 2), 1)
        return s

    # ----------------------------- helpers -----------------------------
    def _future_building(self, s, x, base, w, h, body, shade, neon1, neon2, roof=0, window_step=6, window_size=2, row_gap=7, border=True):
        top = base - h
        pygame.draw.rect(s, body, (x, top, w, h))
        pygame.draw.rect(s, shade, (x, top + h - 5, w, 5))
        if border:
            pygame.draw.line(s, (156, 176, 214), (x, top), (x + w - 1, top), 1)
            pygame.draw.line(s, shade, (x, top), (x, base - 1), 1)
        pygame.draw.rect(s, (max(0, body[0]-18), max(0, body[1]-20), max(0, body[2]-22)), (x + w - 4, top + 2, 4, max(4, h - 7)))
        if roof == 0:
            pygame.draw.rect(s, shade, (x + 3, top - 4, max(5, w - 6), 4))
            pygame.draw.line(s, neon1, (x + 5, top - 2), (x + w - 6, top - 2), 1)
        elif roof == 1:
            pygame.draw.rect(s, shade, (x + w // 2 - 3, top - 7, 6, 7))
            pygame.draw.line(s, neon2, (x + w // 2, top - 10), (x + w // 2, top - 1), 1)
            pygame.draw.rect(s, neon2, (x + w // 2 - 1, top - 10, 3, 2))
        else:
            pygame.draw.polygon(s, shade, [(x + 4, top), (x + w // 2, top - 7), (x + w - 4, top)])
            pygame.draw.line(s, neon1, (x + 8, top - 1), (x + w - 8, top - 1), 1)
        wx0 = x + 4
        wx1 = x + w - 6
        for wy in range(top + 8, base - 10, row_gap):
            for wx in range(wx0, wx1, window_step):
                col = neon1 if ((wx + wy) // 3) % 2 == 0 else neon2
                pygame.draw.rect(s, col, (wx, wy, window_size, window_size + 1))
        pygame.draw.line(s, neon1, (x + 2, top + 4), (x + 2, base - 8), 1)
        if w >= 24:
            pygame.draw.line(s, neon2, (x + w - 7, top + 6), (x + w - 7, base - 12), 1)

    def _future_facade_panel(self, s, x, y, w, h, c1, c2):
        pygame.draw.rect(s, (55, 74, 109), (x, y, w, h))
        pygame.draw.rect(s, (40, 55, 84), (x, y + h - 2, w, 2))
        pygame.draw.line(s, c1, (x + 2, y + 2), (x + w - 3, y + 2), 1)
        pygame.draw.line(s, c2, (x + 2, y + 4), (x + w - 5, y + 4), 1)
        if w > 12:
            pygame.draw.line(s, c1, (x + 3, y + h - 3), (x + w - 6, y + h - 3), 1)

    def _future_roof_billboard(self, s, x, y, w, h, pal, mode=0, compact=False):
        c1, c2 = (pal['hi'], pal['spark']) if mode == 0 else ((pal['spark'], pal['alt']) if mode == 1 else (pal['alt'], pal['hi']))
        pygame.draw.line(s, (80, 98, 138), (x + 2, y + h), (x + 2, y + h + 4), 1)
        pygame.draw.line(s, (80, 98, 138), (x + w - 3, y + h), (x + w - 3, y + h + 4), 1)
        pygame.draw.rect(s, (66, 84, 124), (x, y, w, h))
        pygame.draw.rect(s, (42, 57, 88), (x, y + h - 2, w, 2))
        pygame.draw.line(s, c1, (x + 1, y + 1), (x + w - 2, y + 1), 1)
        if not compact:
            pygame.draw.line(s, c2, (x + 2, y + 3), (x + w - 4, y + 3), 1)
        else:
            pygame.draw.line(s, c2, (x + 2, y + 2), (x + w - 4, y + 2), 1)

    def _future_bridge(self, s, x, y, w, pal, support=True):
        pygame.draw.rect(s, (82, 99, 140), (x, y, w, 4))
        pygame.draw.line(s, pal['hi'], (x + 2, y + 1), (x + w - 3, y + 1), 1)
        pygame.draw.line(s, pal['spark'], (x + 4, y + 3), (x + w - 5, y + 3), 1)
        if support:
            pygame.draw.line(s, (64, 82, 116), (x + 4, y + 4), (x + 4, y + 12), 1)
            pygame.draw.line(s, (64, 82, 116), (x + w - 4, y + 4), (x + w - 4, y + 12), 1)

    def _future_hover_car(self, s, x, y, pal, style=0):
        body = (60, 77, 119)
        top = (188, 228, 235)
        canopy = (131, 226, 247)
        accent = pal['spark'] if style == 0 else pal['hi']
        # casco principal
        pygame.draw.polygon(s, body, [(x, y+4), (x+4, y), (x+14, y), (x+18, y+3), (x+16, y+7), (x+2, y+7)])
        pygame.draw.line(s, top, (x+4, y+1), (x+13, y+1), 1)
        pygame.draw.line(s, canopy, (x+6, y+2), (x+11, y+2), 1)
        pygame.draw.line(s, accent, (x+2, y+6), (x+15, y+6), 1)
        pygame.draw.rect(s, accent, (x+13, y+3, 3, 1))
        # brilho de levitação / motores
        pygame.draw.line(s, pal['hi'], (x+3, y+8), (x+6, y+8), 1)
        pygame.draw.line(s, pal['hi'], (x+11, y+8), (x+14, y+8), 1)
        # partículas/cauda discretas
        for n in range(3):
            px = x - 2 - n * 3
            py = y + 4 + (n % 2)
            c = pal['hi'] if n % 2 == 0 else pal['alt']
            pygame.draw.rect(s, c, (px, py, 2, 1))
            if n == 2:
                pygame.draw.rect(s, pal['spark'], (px - 2, py, 1, 1))

    def _future_drone(self, s, x, y, pal):
        pygame.draw.line(s, pal['alt'], (x, y), (x + 9, y), 1)
        pygame.draw.rect(s, pal['hi'], (x + 2, y + 1, 4, 1))
        pygame.draw.rect(s, pal['spark'], (x + 7, y, 2, 1))

    def _future_small_plants(self, s, x, y, width):
        cols = ((91, 222, 184), (134, 246, 205), (170, 255, 150))
        for i, xx in enumerate(range(x, x + width, 5)):
            yy = y - (i % 2)
            c = cols[i % len(cols)]
            pygame.draw.line(s, c, (xx, yy), (xx + 1, yy - 4 - (i % 2)), 1)
            if i % 3 == 0:
                pygame.draw.line(s, c, (xx + 1, yy - 2), (xx + 3, yy - 4), 1)

    # ----------------------------- overlays -----------------------------
    def _overlay_harmony(self, surf, frame, climate, night):
        if self.biome != 'cidade_futurista':
            return super()._overlay_harmony(surf, frame, climate, night)
        # Única camada dinâmica do bioma: evita duplicar tráfego/glow da cadeia
        # anterior (o super aqui invocava vários passes semelhantes).
        pal = self.FUTURE
        # 2–4 veículos reais, com tráfego bidirecional e velocidades distintas.
        count = 3 if self.visual_quality else 2
        for i in range(count):
            direction = -1 if i % 3 == 1 else 1
            velocity = (0.52, 0.76, 1.03)[i % 3]
            x = int((i*179 + frame*velocity*direction) % 526) - 40
            y = 245 + i*36 + int(math.sin(frame*.037+i*2.4)*3)
            frame_index=(i%3, (frame//12+i)%2)
            sprite = (self._future_car_flip_sprites if direction<0
                      else self._future_car_sprites)[frame_index]
            surf.blit(sprite, (x, y))
            # partículas do propulsor são localizadas: sem ruído espalhado pela cidade.
            exhaust_x = x-3 if direction>0 else x+29
            for j in range(2):
                off = (frame//3 + j*4 + i*2) % 10
                pygame.draw.line(surf, (106, 209, 226, 84-j*28),
                                 (exhaust_x - direction*off, y+9+j),
                                 (exhaust_x - direction*(off+3), y+9+j), 1)
        # Sinalizadores suaves sincronizados (sem letreiro pairando).
        if night > .25:
            for k in range(3):
                xx = (71 + k*157 + frame//3) % WIDTH
                yy = 355 + (k%2)*14
                pygame.draw.rect(surf, (140, 239, 241, 54), (xx, yy, 2, 2))
        if climate == 'vento_neon':
            for k in range(4 if self.visual_quality else 2):
                xx = int((k*129 + frame*1.5)%480)-15
                yy = 190+(k*59+frame//2)%120
                pygame.draw.line(surf,(100,224,239,32),(xx, yy),(xx+9, yy+2),1)
        elif climate == 'chuva_acida':
            for k in range(6 if self.visual_quality else 3):
                xx=int((k*83-frame*1.7)%480)-15
                yy=176+(k*69+frame*2)%170
                pygame.draw.line(surf,(146,241,135,43),(xx, yy),(xx-3,yy+10),1)

    @staticmethod
    def _future_car_art(style, phase):
        """Pixel-art de carro feita uma vez por estilo/fase (30x16 px)."""
        s=pygame.Surface((32, 17), pygame.SRCALPHA)
        bodies = ((63, 87, 130), (92, 78, 135), (62, 118, 129))
        trims = ((102, 223, 239), (242, 127, 207), (135, 239, 194))
        body=bodies[style]; trim=trims[style]
        edge=(32, 49, 82)
        # carroceria integral, aerodinâmica em degraus pixelados
        pygame.draw.polygon(s, edge, [(2,11),(4,7),(8,6),(12,3),(23,3),
                                     (29,7),(30,10),(27,13),(6,13)])
        pygame.draw.polygon(s, body, [(4,10),(7,7),(12,6),(15,4),
                                     (22,4),(27,7),(28,10),(25,12),(7,12)])
        # cabine com visor graduado
        pygame.draw.polygon(s,(45,81,112),[(11,7),(15,5),(22,5),(25,8),(11,8)])
        pygame.draw.line(s,(156,226,238),(14,5),(22,5),1)
        pygame.draw.line(s,(88,188,211),(12,7),(24,7),1)
        # divisor, trim e faróis
        pygame.draw.line(s, trim, (6,11),(25,11),1)
        pygame.draw.rect(s, (242,243,211), (26,8,3,2))
        pygame.draw.rect(s, (247,129,168), (3,9,2,2))
        # dois reatores; fluxo alterna a cada fase, mas permanecem sob a nave
        for x in (9, 22):
            pygame.draw.rect(s,(33,57,82),(x-3,12,6,2))
            pygame.draw.rect(s,(114,239,239),(x-2,14,4,1+phase))
        pygame.draw.line(s,(123,215,246,115),(8,16),(25,16),1)
        return s
