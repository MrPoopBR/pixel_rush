"""v3.146 — passe premium específico em arbustos e plantas baixas da Floresta."""
import random
import pygame
from pixelrush_biomes2_v3145 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW


class ModularBiomeScene(Previous):
    def _leaf_spark(self, s, x, y, base, hi=None):
        if 1 <= x < s.get_width()-2 and 1 <= y < s.get_height()-2:
            pygame.draw.rect(s, base, (x, y, 2, 1))
            pygame.draw.rect(s, base, (x-1, y+1, 1, 1))
            if hi:
                pygame.draw.rect(s, hi, (x, y, 1, 1))

    def _low_grass_blade(self, s, x, y, h, c1, c2):
        pygame.draw.line(s, c1, (x, y), (x+1, y-h), 1)
        if h > 3:
            pygame.draw.line(s, c2, (x+1, y-1), (x+2, y-h+1), 1)

    def _fern_polish(self, s, x, y, seed, scale=1.0, dense=False):
        rng = random.Random(seed)
        c_dark=(48,104,70); c_mid=(93,156,90); c_hi=(164,212,118)
        count = 4 if not dense else 6
        for side in (-1,1):
            for i in range(count):
                off = 2 + i*2
                hh = int((8 + rng.randint(0,5)) * scale)
                xx = x + side * off
                yy = y - i
                pygame.draw.line(s, c_mid, (x, y-1), (xx, yy-hh), 1)
                pygame.draw.line(s, c_hi, (xx, yy-hh+1), (xx+side*2, yy-hh+3), 1)
                if i % 2 == 0:
                    pygame.draw.line(s, c_dark, (xx, yy-hh+2), (xx+side*1, yy-hh+5), 1)
        for i in range(3):
            self._leaf_spark(s, x+rng.randint(-5,5), y-rng.randint(4,12), c_mid, c_hi)

    def _shrub_polish(self, s, x, y, seed, style=0, scale=1.0):
        rng = random.Random(seed)
        dark=(34,87,66); mid=(61,131,80); hi=(132,191,104); shine=(183,220,136)
        accent = (222,166,178) if style==2 else (145,184,99)
        # massa base extra para dar volume
        blobs=[(-11,-6,10,7),(0,-10,12,9),(12,-5,10,7),(-6,1,14,8),(8,1,14,8)]
        for i,(dx,dy,w,h) in enumerate(blobs):
            px=x+dx; py=y+dy
            pygame.draw.ellipse(s, mid if i%2 else dark, (px-w//2, py-h//2, w, h))
            pygame.draw.line(s, hi, (px-w//3, py-h//4), (px+w//4, py-h//4), 1)
        # folhas pontudas e brilhos
        for i in range(14):
            px=x+rng.randint(-16,16); py=y+rng.randint(-15,2)
            self._leaf_spark(s, px, py, hi if i%3 else mid, shine if i%4==0 else None)
        # brotos altos
        for i in range(4 if style!=2 else 3):
            bx=x+rng.randint(-12,12); by=y-rng.randint(7,13)
            pygame.draw.line(s, (86,132,81), (bx, y), (bx, by), 1)
            pygame.draw.line(s, shine, (bx, by), (bx+rng.choice((-2,2)), by-2), 1)
        # flores discretas somente onde já havia estilo floral
        if style == 2:
            for dx in (-10, -1, 9):
                pygame.draw.rect(s, accent, (x+dx, y-7-rng.randint(0,1), 2, 2))
                pygame.draw.rect(s, (247,226,201), (x+dx+1, y-6, 1, 1))
        # pequenas folhas baixas nas bordas
        for i in range(3):
            lx=x+rng.randint(-15,15); ly=y+rng.randint(-1,4)
            pygame.draw.line(s, dark, (lx, ly), (lx+rng.choice((-2,2)), ly-3), 1)
            pygame.draw.line(s, hi, (lx, ly-1), (lx+rng.choice((-1,1)), ly-3), 1)

    def _bigleaf_polish(self, s, x, y, seed):
        rng = random.Random(seed)
        c1=(65,129,83); c2=(100,171,104); c3=(184,220,136)
        for side in (-1,1):
            reach = 8 + rng.randint(0,4)
            tipx = x + side * (10 + rng.randint(0,4))
            tipy = y - reach - rng.randint(2,6)
            pygame.draw.line(s, c1, (x, y), (tipx, tipy), 1)
            pygame.draw.line(s, c3, (x+side, y-2), (tipx, tipy+1), 1)
            for k in range(2,4):
                xx = x + side*k*2
                yy = y - k*3
                pygame.draw.line(s, c2, (xx, yy), (xx+side*2, yy-2), 1)

    def _ground_flora_polish(self, s, xs, seed, flower_rate=0.0):
        rng = random.Random(seed)
        for i,x in enumerate(xs):
            basey = 224 - (i % 2)
            self._low_grass_blade(s, x+rng.randint(-1,1), basey, 4+rng.randint(0,3), (72,118,74), (122,171,98))
            if i % 2 == 0:
                self._low_grass_blade(s, x+2, basey, 3+rng.randint(0,2), (78,125,76), (148,191,111))
            if flower_rate > 0 and (i % int(1/flower_rate + 1) == 0):
                pygame.draw.rect(s, (240,201,112) if i%3==0 else (214,164,188), (x, basey-3, 1, 1))

    def _forest_chunk(self, layer, index):
        s = super()._forest_chunk(layer, index)
        rng = random.Random(146000 + index * 181 + {'far':0,'mid':1000,'near':2000}[layer])
        if layer == 'mid':
            theme=index%8
            # mesmos pontos-base da versão anterior, só com acabamento nas plantas baixas
            side_plants=(24,52,172,200)
            for j,x in enumerate(side_plants):
                if j%2:
                    self._fern_polish(s, x, 217, 14610 + index*19 + j, 1.0, dense=(j==1))
                else:
                    style = 2 if j==0 and theme in (2,6) else (2 if j==0 and theme not in (2,6) and index%4==0 else 0)
                    self._shrub_polish(s, x, 216, 14620 + index*19 + j, style=style)
            # pontos centrais por tema
            if theme in (0,4):
                self._shrub_polish(s, 98, 214, 14640 + index, style=1)
                self._ground_flora_polish(s, (90,96,101,107,114,120), 14650 + index, flower_rate=0.18)
            elif theme in (1,5):
                self._ground_flora_polish(s, (26,34,40,142,150,158,184,190), 14660 + index, flower_rate=0.10)
            elif theme in (2,6):
                self._fern_polish(s, 148, 216, 14670 + index, 1.0, dense=True)
                self._shrub_polish(s, 28, 215, 14671 + index, style=2)
                self._ground_flora_polish(s, (22,30,37,142,148,156,166), 14672 + index, flower_rate=0.14)
            else:
                self._ground_flora_polish(s, (66,72,78,84,116,124,132), 14680 + index, flower_rate=0.16)
        elif layer == 'near':
            edge_sets=((18,34,50,172,188,204),
                       (22,38,56,168,184,201),
                       (20,36,54,170,186,203),
                       (17,33,48,174,191,207),
                       (24,42,58,166,182,199))
            placements=edge_sets[index%len(edge_sets)]
            # polimento nas massas que já existem
            for i,x in enumerate(placements):
                if i in (0,3):
                    self._bigleaf_polish(s, x, 222, 14690 + index*17 + i)
                elif i in (1,4):
                    self._fern_polish(s, x, 223, 14710 + index*17 + i, 1.0, dense=True)
                else:
                    self._shrub_polish(s, x, 221, 14730 + index*17 + i, style=1 if x<70 else 2)
            self._shrub_polish(s, 24, 221, 14750 + index, style=2)
            self._shrub_polish(s, 198, 221, 14751 + index, style=2)
            self._ground_flora_polish(s, (14,20,26,34,44,178,186,194,202,210), 14760 + index, flower_rate=0.12)
        else:
            # apenas leve ganho de leitura no fundo, sem exagero
            for x in (26, 58, 92, 134, 168, 198):
                if (x + index) % 2 == 0:
                    self._leaf_spark(s, x, 210 - ((x//8)%3), (126,164,143), (170,191,172))
        return s
