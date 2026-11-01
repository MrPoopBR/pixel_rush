"""v3.145 — passe premium específico nas árvores da Floresta."""
import random
import pygame
from pixelrush_biomes2_v3144 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW


class ModularBiomeScene(Previous):
    def _leaf_dab(self, s, x, y, col):
        if 1 <= x < s.get_width()-1 and 1 <= y < s.get_height()-1:
            pygame.draw.rect(s, col, (x, y, 2, 1))
            pygame.draw.rect(s, col, (x-1, y+1, 1, 1))

    def _forest_tree_polish(self, s, x, ground, height, seed, layer='mid', shape='umbrella'):
        """Acabamento adicional sobre árvores já desenhadas: copa, galhos e tronco."""
        rng = random.Random(seed)
        x=int(x); ground=int(ground); height=int(height)
        top = ground - height
        # paletas por camada
        if layer == 'near':
            hi=(125, 181, 98); mid=(82, 137, 78); deep=(39, 81, 61)
            bark_hi=(145, 108, 76); bark=(101, 71, 50); bark_dark=(64, 44, 34)
        else:
            hi=(114, 167, 99); mid=(74, 125, 85); deep=(49, 88, 74)
            bark_hi=(126, 98, 76); bark=(88, 66, 52); bark_dark=(58, 46, 38)
        crown_y = top + (22 if layer=='near' else 18)
        # volumes extras na copa, respeitando formato
        if shape == 'cedar':
            clumps=((0,-18,12,8),(0,-8,17,10),(-7,2,16,10),(7,2,15,9),(0,11,20,10))
        elif shape == 'broad':
            clumps=((-11,-6,16,10),(11,-6,16,10),(0,-12,18,10),(-7,4,18,11),(8,5,18,11),(0,10,22,12))
        else:  # umbrella
            clumps=((-13,-6,18,10),(13,-6,18,10),(0,-12,16,10),(-8,4,20,11),(9,4,20,11),(0,11,22,12))
        for i,(dx,dy,w,h) in enumerate(clumps):
            px=x+dx+rng.randint(-1,1); py=crown_y+dy+rng.randint(-1,1)
            pygame.draw.ellipse(s, mid, (px-w//2, py-h//2, w, h))
            pygame.draw.ellipse(s, deep, (px-w//2+1, py-h//2+3, max(4,w-4), max(3,h-4)))
            pygame.draw.line(s, hi, (px-w//3, py-h//4), (px+w//4, py-h//4), 1)
        # recortes de silhueta com brilhos nas bordas superiores
        for i in range(7):
            px=x + rng.randint(-16,16)
            py=crown_y + rng.randint(-16,10)
            self._leaf_dab(s, px, py, hi if i % 2 == 0 else mid)
        for i in range(6):
            px=x + rng.randint(-14,14)
            py=crown_y + rng.randint(-8,14)
            self._leaf_dab(s, px, py, deep)
        # tronco mais trabalhado
        trunk_h = int(height * (0.50 if shape != 'umbrella' else 0.44))
        trunk_top = ground - trunk_h
        for i in range(0, max(12, trunk_h), 6):
            yy = trunk_top + i
            pygame.draw.line(s, bark_hi, (x, yy), (x, yy+2), 1)
            pygame.draw.line(s, bark_dark, (x+3, yy+1), (x+3, yy+3), 1)
        # galhos secundários
        branch_specs = [(-1, -7, -8, -10), (2, -12, 8, -8)] if shape!='cedar' else [(-1,-9,-6,-11),(1,-14,5,-10)]
        for bx,by,dx,dy in branch_specs:
            sx=x+bx; sy=ground+by
            pygame.draw.line(s, bark, (sx, sy), (sx+dx, sy+dy), 2)
            pygame.draw.line(s, bark_hi, (sx-1, sy-1), (sx+dx-1, sy+dy), 1)
        # pequenas folhas / cipós pendendo da copa
        if layer != 'far':
            for i in range(3 if shape!='cedar' else 2):
                vx = x + rng.randint(-10, 10)
                vy = crown_y + rng.randint(4, 14)
                for j in range(4 + (i % 2)):
                    px=vx + (j//3) * rng.choice((-1,0,1))
                    py=vy + j
                    if 0 <= px < s.get_width() and 0 <= py < s.get_height():
                        s.set_at((px, py), (74, 118, 78))
        # raízes discretas apenas acima da vegetação frontal
        if layer == 'near':
            pygame.draw.line(s, bark_dark, (x-1, min(ground,218)), (x-7, min(ground+3,218)), 1)
            pygame.draw.line(s, bark_dark, (x+2, min(ground,218)), (x+8, min(ground+2,218)), 1)

    def _small_far_tree_polish(self, s, x, ground, height, seed):
        rng = random.Random(seed)
        top = ground - height
        for i in range(4):
            px = x + rng.randint(-9, 9)
            py = top + 16 + rng.randint(-7, 6)
            self._leaf_dab(s, px, py, (131, 165, 148) if i%2==0 else (92, 131, 117))
        for yy in range(top+20, min(ground-6, top+44), 7):
            pygame.draw.line(s, (110, 129, 115), (x, yy), (x, yy+1), 1)

    def _forest_chunk(self, layer, index):
        s = super()._forest_chunk(layer, index)
        rng = random.Random(145000 + index * 173 + {'far':0,'mid':1000,'near':2000}[layer])
        if layer == 'far':
            far_positions=(40,84,127,170)
            for i,tx in enumerate(far_positions):
                hh=rng.randint(48,74)
                self._small_far_tree_polish(s, tx + (1 if i%2 else 0), 213, hh, 14510 + index*29 + i)
        elif layer == 'mid':
            theme=index%8
            if theme in (0,4):
                trees=[(42,216,103,'umbrella'),(171,217,116,'cedar')]
            elif theme in (1,5):
                trees=[(44,217,108,'broad'),(179,217,92,'umbrella')]
            elif theme in (2,6):
                trees=[(48,218,100,'cedar'),(171,217,99,'umbrella')]
            else:
                trees=[(42,216,95,'umbrella'),(101,216,108,'cedar'),(173,216,103,'broad')]
            for i,(tx,gy,h,shape) in enumerate(trees):
                self._forest_tree_polish(s, tx, gy, h, 14600 + index*31 + i, 'mid', shape)
        else:
            theme=index%5
            if theme in (0,3):
                trees=[(30,223,66,'cedar'),(194,223,72,'umbrella')]
            elif theme==1:
                trees=[(194,223,68,'broad')]
            elif theme==2:
                trees=[(28,223,70,'umbrella')]
            else:
                trees=[]
            for i,(tx,gy,h,shape) in enumerate(trees):
                self._forest_tree_polish(s, tx, gy, h, 14700 + index*37 + i, 'near', shape)
        return s
