"""v3.143 — floresta com mais variedade e cidade futurista com céu/clima premium."""
import math
import random
import pygame
from pixelrush_biomes2_v3142 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, LH, WIDTH, _line


class ModularBiomeScene(Previous):
    FOREST_FLOWERS = ((255, 208, 99), (245, 157, 176), (164, 214, 118), (195, 184, 255))

    def _wildflower(self, s, x, y, seed, tint=0):
        rng = random.Random(seed)
        stem=(84,127,78)
        petal=self.FOREST_FLOWERS[tint % len(self.FOREST_FLOWERS)]
        pygame.draw.line(s, stem, (x, y), (x, y-4-rng.randint(0,2)), 1)
        cy=y-5
        pygame.draw.rect(s, petal, (x-1, cy, 1, 1))
        pygame.draw.rect(s, petal, (x+1, cy, 1, 1))
        pygame.draw.rect(s, petal, (x, cy-1, 1, 1))
        pygame.draw.rect(s, (245,236,181), (x, cy, 1, 1))

    def _small_tree_far(self, s, x, ground, height, seed, shape='cedar'):
        """Árvore distante pequena, mais orgânica e sem aparência de corte."""
        rng = random.Random(seed)
        bark=(73,96,87); barkhi=(112,142,128); barkdark=(51,71,66)
        x=int(x); ground=int(ground); height=int(height)
        top=ground-height
        trunk_w=3
        lean=rng.choice((-2,-1,1,2))
        topx=x+lean
        pygame.draw.line(s,barkdark,(x+1,ground),(topx+1,top+14),trunk_w+1)
        pygame.draw.line(s,bark,(x,ground-1),(topx,top+14),trunk_w)
        pygame.draw.line(s,barkhi,(x-1,ground-6),(topx-1,top+17),1)
        for side in (-1,1):
            sy=ground-int(height*(0.38 if side<0 else 0.56))
            sx=x+int(lean*(0.38 if side<0 else 0.56))
            dx=side*(6+rng.randint(0,3)); dy=-(6+rng.randint(0,3))
            pygame.draw.line(s,bark,(sx,sy),(sx+dx,sy+dy),2)
        leaflight=2
        cx=topx; cy=top+20
        if shape=='cedar':
            self._crown(s,cx-6,cy+5,9,10,seed+10,leaflight,'cedar')
            self._crown(s,cx+6,cy+5,8,10,seed+11,leaflight,'cedar')
            self._crown(s,cx,cy-5,11,15,seed+12,leaflight,'cedar')
            self._crown(s,cx+1,cy-16,8,11,seed+13,leaflight,'cedar')
        else:
            self._crown(s,cx-8,cy+4,10,10,seed+10,leaflight,'oak')
            self._crown(s,cx+7,cy+4,9,10,seed+11,leaflight,'oak')
            self._crown(s,cx,cy-6,12,14,seed+12,leaflight,'oak')
            self._crown(s,cx,cy-15,8,9,seed+13,leaflight,'oak')

    def _forest_chunk(self, layer, index):
        rng=random.Random(143000+index*131+{'far':0,'mid':1000,'near':2000}[layer])
        s=pygame.Surface((LW,LH),pygame.SRCALPHA)
        if layer=='far':
            self._far_ridge(s,index)
            # evita silhuetas encostando nas bordas do chunk/horizonte
            far_positions=(40,84,127,170)
            for i,x in enumerate(far_positions):
                hh=rng.randint(48,74)
                self._small_tree_far(s,x,213,hh,14310+index*47+i,'cedar' if i%2 else 'broad')
            for i in range(5):
                x=rng.randrange(18,LW-22); y=rng.randrange(203,214)
                _line(s,(122,161,149),x,y,x+rng.randint(5,10),y,1)
        elif layer=='mid':
            self._ground(s,'mid',143100+index)
            theme=index%8
            if theme in (0,4):
                self._tree(s,42,216,103,14300+index,'mid','umbrella')
                self._tree(s,171,217,116,14400+index,'mid','cedar')
                self._shrub(s,98,214,index+150,1)
                self._wildflower(s, 116, 216, 14550+index, 0)
                self._wildflower(s, 121, 217, 14551+index, 1)
            elif theme in (1,5):
                self._tree(s,44,217,108,14500+index,'mid','broad')
                self._tree(s,179,217,92,14600+index,'mid','umbrella')
                self._ruins(s,82,217,62,14700+index)
                self._wildflower(s, 24, 215, 14770+index, 2)
            elif theme in (2,6):
                self._tree(s,48,218,100,14800+index,'mid','cedar')
                self._tree(s,171,217,99,14900+index,'mid','umbrella')
                self._fern(s,148,216,15100+index)
                self._shrub(s,28,215,15120+index,2)
                self._shrub(s,89,214,15130+index,1)
                self._wildflower(s, 100, 216, 15140+index, 2)
                self._wildflower(s, 106, 216, 15141+index, 1)
            else:
                self._tree(s,42,216,95,15200+index,'mid','umbrella')
                self._tree(s,101,216,108,15300+index,'mid','cedar')
                self._tree(s,173,216,103,15400+index,'mid','broad')
                self._wildflower(s, 74, 216, 15410+index, 3)
                self._wildflower(s, 78, 217, 15411+index, 0)
            side_plants=(24,52,172,200)
            for j,x in enumerate(side_plants):
                if j%2:
                    self._fern(s,x,217,15500+index*17+j,1)
                else:
                    self._shrub(s,x,216,15600+index*17+j, style=2 if j==0 else 0)
            if theme in (1,6):
                self._mushroom(s, 31 if theme==1 else 194, 214, 15700+index)
        else:
            self._ground(s,'near',15800+index)
            edge_sets=((18,34,50,172,188,204),
                       (22,38,56,168,184,201),
                       (20,36,54,170,186,203),
                       (17,33,48,174,191,207),
                       (24,42,58,166,182,199))
            placements=edge_sets[index%len(edge_sets)]
            theme=index%5
            # árvores/rochas primeiro
            if theme in (0,3):
                self._tree(s,30,223,66,16000+index,'near','cedar')
                self._tree(s,194,223,72,16100+index,'near','umbrella')
            elif theme==1:
                self._rock(s,32,225,16200+index)
                self._tree(s,194,223,68,16300+index,'near','broad')
            elif theme==2:
                self._tree(s,28,223,70,16400+index,'near','umbrella')
                self._rock(s,194,225,16500+index)
            else:
                self._rock(s,31,225,16600+index)
                self._rock(s,194,225,16700+index)
            # vegetação por cima com mais variedade e cor
            for i,x in enumerate(placements):
                if i in (0,3): self._bigleaf(s,x,222,16800+index*20+i)
                elif i in (1,4): self._fern(s,x,223,16900+index*20+i,1.0)
                else: self._shrub(s,x,221,17000+index*20+i,style=1 if x<70 else 2)
            self._shrub(s, 24, 221, 17100+index, style=2)
            self._shrub(s, 198, 221, 17110+index, style=2)
            self._fern(s, 14, 224, 17120+index, .88)
            self._fern(s, 208, 224, 17130+index, .84)
            # flores pequenas laterais discretas
            for j,xx in enumerate((18,27,44,178,191,205)):
                if j%2==0:
                    self._wildflower(s, xx, 223-(j%3), 17200+index*10+j, j)
            self._forest_anchors[index]=tuple((x, 216-(i%2)*2) for i,x in enumerate((placements[0],placements[2],placements[3],placements[5])))
        return s

    def _future_combo_polish(self, surf, layer, seed, pal):
        super()._future_combo_polish(surf, layer, seed, pal)
        rng = random.Random(seed)
        if layer == 'far':
            for _ in range(5):
                x=rng.randrange(12, LW-28)
                y=rng.randrange(120, 162)
                pygame.draw.line(surf, pal['hi'], (x, y), (x+18, y), 1)
                pygame.draw.line(surf, pal['spark'], (x+3, y+2), (x+13, y+2), 1)
        elif layer == 'mid':
            for _ in range(6):
                x=rng.randrange(8, LW-22)
                y=rng.randrange(150, 196)
                pygame.draw.line(surf, pal['alt'], (x, y), (x+12, y-4), 1)
        else:
            for _ in range(7):
                x=rng.randrange(8, LW-12)
                y=rng.randrange(206, 226)
                pygame.draw.rect(surf, pal['hi'] if _%2 else pal['spark'], (x, y, 3, 1))

    def _overlay_harmony(self, surf, frame, climate, night):
        if self.biome != 'cidade_futurista':
            return super()._overlay_harmony(surf, frame, climate, night)
        # base existente + reforço premium do céu/clima futurista
        super()._overlay_harmony(surf, frame, climate, night)
        # linhas de energia no céu
        base_alpha = 18 if night < 0.2 else 28
        for y in (112, 146, 186):
            yy = y + int(math.sin(frame*0.03 + y) * 2)
            pygame.draw.line(surf, (108, 241, 247, base_alpha), (0, yy), (450, yy), 1)
        # reflexos/hologramas noturnos
        if night > 0.22:
            for i in range(8):
                x = int((i*57 + frame*0.9) % 480) - 10
                y = 76 + (i*21) % 90
                pygame.draw.rect(surf, (247,108,223,44), (x, y, 2, 2))
                pygame.draw.line(surf, (132,248,255,28), (x-1, y+2), (x+4, y+2), 1)
        else:
            for i in range(6):
                x = int((i*73 + frame*0.6) % 470) - 8
                y = 62 + (i*17) % 70
                pygame.draw.line(surf, (188,228,233,24), (x, y), (x+10, y), 1)
        if climate == 'vento_neon':
            for i in range(10):
                x=int((i*43 + frame*2.6)%(WIDTH+40))-20
                y=96 + (i*26 + frame//2) % 165
                pygame.draw.line(surf, (70,245,255,34), (x,y), (x+9,y+2), 1)
                if i%2==0:
                    pygame.draw.line(surf, (247,108,223,26), (x+4,y-1), (x+12,y+1), 1)
        elif climate == 'chuva_acida':
            for i in range(13):
                x=int((i*35 - frame*2.8)%(WIDTH+30))-15
                y=92 + (i*33 + frame*3) % 290
                pygame.draw.line(surf, (125,255,112,34), (x,y), (x-3,y+10), 1)
                if i%3==0:
                    pygame.draw.line(surf, (108,241,247,24), (x+1,y+3), (x-1,y+13), 1)
