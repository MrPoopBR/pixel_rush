"""Pixel Rush v3.162.0 — reconstrução artística premium do Vulcão.

Cinco regiões vulcânicas distintas, formações ancoradas, rios de lava ligados à
rocha, piso de obsidiana coerente, fumaça na saída de crateras, parallax longo.
Somente o bioma 'vulcao' é alterado. Todo desenho denso é feito uma única vez
no carregamento, sem custos de desenho complexo no loop dos quadros.
"""
from __future__ import annotations
import math
import random
import pygame
from pixelrush_biomes2_v3161 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, LH, WIDTH


class ModularBiomeScene(Previous):
    VOLCANO_DISTRICTS = (
        'caldeira', 'obsidiana', 'cascatas', 'fumarolas', 'ruinas_basalticas',
    )
    DARK = (37, 34, 46)
    BLACK_ROCK = (49, 42, 52)
    MED_ROCK = (79, 62, 69)
    ROCK_HI = (124, 93, 86)
    LAVA = (245, 120, 55)
    LAVA_HI = (255, 203, 115)
    LAVA_DARK = (169, 67, 45)

    def __init__(self, biome):
        super().__init__(biome)
        if biome == 'vulcao':
            self._rebuild_volcano()
            self._build_ash_haze()
            self._map_cache.clear()

    @staticmethod
    def _new_chunk():
        return pygame.Surface((LW, LH), pygame.SRCALPHA)

    def _build_ash_haze(self):
        """Véu atmosférico pré-renderizado, não polui o quadro com fumaça solta."""
        self._ash_haze_day = pygame.Surface((WIDTH, 92), pygame.SRCALPHA)
        self._ash_haze_night = pygame.Surface((WIDTH, 92), pygame.SRCALPHA)
        rng = random.Random(316217)
        for y in range(92):
            t = y/91.
            alpha = int(1 + 26 * t*t)
            pygame.draw.line(self._ash_haze_day,(127,105,103,alpha), (0,y),(WIDTH-1,y),1)
            pygame.draw.line(self._ash_haze_night,(115,79,90,int(alpha*.5)), (0,y),(WIDTH-1,y),1)
        # Mechas horizontais compridas, suaves e espalhadas no ar, não massas brancas.
        for j in range(10):
            x = rng.randrange(8,WIDTH-68)
            y = rng.randrange(27,88)
            width = rng.randrange(25,78)
            palette = ((174,141,124,13), (115,88,90,17))
            pygame.draw.line(self._ash_haze_day,palette[j%2],(x,y),(x+width,y),1)
            pygame.draw.line(self._ash_haze_night,(131,86,88,8),(x,y),(x+width,y),1)

    def _rebuild_volcano(self):
        # 36 chunks em lugar dos 30 antigos, ciclos coerentes, sem gerar a cada frame.
        self._layers['far'] = [self._far_volcano(i) for i in range(10)]
        self._layers['mid'] = [self._mid_volcano(i) for i in range(12)]
        self._layers['near'] = [self._near_volcano(i) for i in range(14)]

    def _region(self, i):
        return self.VOLCANO_DISTRICTS[i % len(self.VOLCANO_DISTRICTS)]

    @staticmethod
    def _ridge(absolute_x, plane=0):
        # A função tem período EXATO de 10 chunks, sem degraus nas emendas.
        a = 2 * math.pi * (absolute_x % (10 * LW)) / (10 * LW)
        if plane == 0:
            return int(176 - 17 * math.sin(2*a + .55) - 9 * math.sin(5*a - .7)
                       - 5 * math.sin(8*a + .2))
        return int(202 - 6 * math.sin(3*a + .45) - 4 * math.sin(6*a - .9))

    def _far_volcano(self, i):
        s = self._new_chunk()
        rng = random.Random(316200 + i*139)
        region = self._region(i)
        # Fundo de cristas unido em ciclo longo; nenhum bloco vertical abrupto.
        for plane, col, bottom in ((0, (105, 79, 88), 221), (1, (76, 60, 72), 222)):
            for x in range(LW):
                y = self._ridge(i*LW+x, plane)
                pygame.draw.line(s, col, (x, y), (x, bottom), 1)
        # camadas de minerais sobre as cristas, sem pontos soltos no céu.
        for x in range(12, LW-8, 19):
            y = self._ridge(i*LW + x, 0) + 5
            pygame.draw.line(s, (139, 102, 95), (x,y), (x+5,y+2), 1)
            if (x+i) % 3 == 0:
                pygame.draw.line(s, (83, 69, 79), (x+2,y+3), (x+7,y+5),1)
        # Dois cones realmente monumentais por ciclo, base larga, cume ancorado.
        if i in (1,5,8):
            cx,top = ((111,94) if i == 1 else (111,106) if i==5 else (112,111))
            size = 87 if i == 1 else 76 if i == 5 else 70
            self._cone(s,cx,top,size,222,rng,region)
        elif region == 'fumarolas':
            # Chaminé mineral saindo do solo, fumo NÃO flutuante.
            self._vent_rock(s, 100, 218, 41, 53, rng, smoke=True)
        elif region == 'cascatas':
            # Geologia da encosta com lava conectada à crista.
            self._far_lava_cascade(s, 76, self._ridge(i*LW+76,0)+7, 206, rng)
        elif region == 'obsidiana':
            self._far_obsidian_outcrop(s, 115, 216, 74, 44)
        else:
            self._far_obsidian_outcrop(s, 109, 218, 57, 36)
        # Camada basal constante e sem juntas.
        pygame.draw.rect(s,(65,53,64),(0,216,LW,7))
        pygame.draw.line(s,(98,75,79),(0,216),(LW-1,216),1)
        return s

    def _cone(self,s,cx,top,half,ground,rng,region):
        # Polígono completamente dentro do chunk.
        x1=max(2,cx-half);x2=min(LW-3,cx+half)
        pygame.draw.polygon(s, (65,49,58),[(x1,ground),(cx-9,top+15),(cx,top),(cx+12,top+14),(x2,ground)])
        pygame.draw.polygon(s, (112,77,74),[(x1+20,ground-6),(cx-8,top+30),(cx,top+5),(cx+4,top+23),(cx+14,ground-3)])
        pygame.draw.polygon(s, (43,40,51),[(cx+9,top+16),(x2-5,ground),(cx+20,ground-7),(cx+4,top+32)])
        pygame.draw.polygon(s, (31,31,43),[(cx-17,top+10),(cx-9,top-2),(cx+11,top-2),(cx+18,top+10),(cx+5,top+13),(cx-8,top+12)])
        pygame.draw.line(s,(171,116,89),(cx-half//2,ground-14),(cx-15,top+45),2)
        pygame.draw.line(s,(149,107,91),(cx+half//2,ground-12),(cx+21,top+55),1)
        for dy in (26,44,62):
            xx=cx-10-(dy//6)
            if xx>x1+10:
                pygame.draw.line(s,(153,109,93),(xx,top+dy),(xx+7,top+dy-3),1)
        # Canal de magma seguindo a encosta, começando NA CRATERA.
        px=cx+5
        route=[(px,top+14),(px+5,top+29),(px+1,top+41),
               (px+10,top+58),(px+15, min(ground-10,top+88)),
               (px+17,ground-4)]
        pygame.draw.lines(s,(76,40,43),False,route,7)
        pygame.draw.lines(s,self.LAVA_DARK,False,route,4)
        pygame.draw.lines(s,self.LAVA,False,route,2)
        pygame.draw.line(s,self.LAVA_HI,(px+5,top+29),(px+1,top+41),1)
        # Fumaça segmentada e conectada à cratera, no próprio chunk.
        self._anchored_smoke(s,cx,top-1,rng,opacity='far')

    @staticmethod
    def _anchored_smoke(s,cx,crater,rng,opacity='far'):
        # em filetes progressivos sem elipses separadas.
        for n in range(5):
            yy=crater - n*9
            ww=7+n*3
            dx=int(4*math.sin(n*.8 + cx*.15))
            xx=cx+dx
            col=((112,105,114),(124,116,124),(136,126,132))[min(2,n//2)]
            pts=[(xx-ww//2,yy+8),(xx-ww//2-2,yy+4),(xx-3,yy),
                 (xx+ww//2,yy-3),(xx+ww//2+2,yy+4),(xx+ww//2,yy+9)]
            pygame.draw.polygon(s,col,pts)
            if n in (1,3):
                pygame.draw.line(s,(162,143,142),(xx-3,yy+2),(xx+4,yy),1)

    def _vent_rock(self,s,x,base,w,h,rng,smoke=False):
        top=base-h
        pygame.draw.polygon(s,(50,43,53),[(x,base),(x+4,top+18),(x+w//3,top),(x+w-11,top+5),(x+w,base)])
        pygame.draw.polygon(s,(100,73,76),[(x+6,base-6),(x+w//3,top+4),(x+w//2,top+10),(x+w//2-4,base-8)])
        pygame.draw.line(s,(142,98,87),(x+9,base-12),(x+11,top+19),1)
        pygame.draw.line(s,(255,157,74),(x+w//2,base-5),(x+w//2+3,base-19),2)
        if smoke:
            self._anchored_smoke(s,x+w//3,top+5,rng)

    @staticmethod
    def _far_obsidian_outcrop(s,cx,base,w,h):
        x=cx-w//2
        pygame.draw.polygon(s,(52,48,61),[(x,base),(x+9,base-h+13),(cx,base-h),(x+w-11,base-h+17),(x+w,base)])
        pygame.draw.polygon(s,(104,79,88),[(x+8,base-4),(cx-7,base-h+12),(cx-3,base-h+3),(cx+1,base-8)])
        pygame.draw.line(s,(135,98,97),(x+14,base-13),(cx-2,base-h+8),1)

    def _far_lava_cascade(self,s,x,y,base,rng):
        # Constrói primeiro a rocha suporte; lava fica completamente dentro dela.
        w=52
        pygame.draw.polygon(s,(57,46,57),[(x-w//2,base),(x-w//2+8,y+10),(x,y),(x+w//2-9,y+14),(x+w//2,base)])
        route=[(x-4,y+12),(x-5,y+30),(x+4,y+43),(x+2,base-8)]
        pygame.draw.lines(s,(86,44,48),False,route,7)
        pygame.draw.lines(s,self.LAVA_DARK,False,route,4)
        pygame.draw.lines(s,self.LAVA,False,route,2)
        pygame.draw.line(s,self.LAVA_HI,(x-5,y+30),(x+4,y+43),1)

    def _mid_volcano(self,i):
        s=self._new_chunk()
        rng=random.Random(317100 + i*151)
        region=self._region(i+1)
        base=216
        # Uma só formação baixa que prende a perspectiva, sem colunas flutuantes.
        pygame.draw.rect(s,(68,54,64),(0,209,LW,15))
        pygame.draw.line(s,(127,88,81),(0,209),(LW-1,209),1)
        configs={
          'caldeira':((10,39,52),(74,56,73),(158,50,59)),
          'obsidiana':((12,47,71),(80,35,54),(142,69,77)),
          'cascatas':((17,59,81),(102,48,73),(174,35,57)),
          'fumarolas':((12,52,63),(83,45,71),(154,55,62)),
          'ruinas_basalticas':((10,42,62),(68,72,77),(155,54,69)),
        }
        for n,(x,w,h) in enumerate(configs[region]):
            h+=rng.randint(-7,6)
            shape='spires' if region == 'obsidiana' else 'terraces' if region in ('caldeira','cascatas') else 'slabs'
            self._basalt_mass(s,x,base,w,h,rng,shape=shape,glow=(region=='cascatas' and n==1))
        if region=='ruinas_basalticas':
            self._ruined_gate(s,90,base,58,60)
        elif region=='fumarolas':
            self._fumarole_tower(s,115,base,53)
        elif region=='caldeira':
            self._lava_pool_on_rock(s,120,203,48)
        elif region=='cascatas':
            self._lava_pool_on_rock(s,108,204,40)
        else:
            self._obsidian_geodes(s,108,197,rng)
        # Estratificação pontual somente em áreas rochosas.
        for xx in range(18, LW-10, 27):
            yy=211+((xx+i)%7)
            pygame.draw.line(s,(143,104,94),(xx,yy),(xx+6,yy),1)
        return s

    def _basalt_mass(self,s,x,base,w,h,rng,shape='slabs',glow=False):
        top=base-h
        if shape=='spires':
            pts=[(x,base),(x+2,top+22),(x+9,top+16),(x+11,top+4),
                 (x+w//3,top),(x+w//2,top+12),(x+2*w//3,top+3),
                 (x+w-6,top+16),(x+w,base)]
        elif shape=='terraces':
            pts=[(x,base),(x+3,top+24),(x+10,top+19),(x+12,top+11),
                 (x+w//2,top+11),(x+w//2+2,top+2),(x+w-12,top+2),
                 (x+w-8,top+15),(x+w-2,top+18),(x+w,base)]
        else:
            pts=[(x,base),(x+5,top+12),(x+8,top+6),(x+w//3,top+6),
                 (x+w//3+4,top),(x+w-8,top+3),(x+w-4,top+16),(x+w,base)]
        pygame.draw.polygon(s,(44,40,51),pts)
        pygame.draw.polygon(s,(91,72,79),[(x+8,base-3),(x+10,top+19),
                                         (x+w//3+3,top+9),(x+w//2,base-3)])
        pygame.draw.line(s,(133,101,93),(x+10,base-14),(x+12,top+22),1)
        pygame.draw.line(s,(35,34,46),(x+w-8,top+15),(x+w-7,base-3),2)
        for yy in range(top+24,base-10,17):
            pygame.draw.line(s,(121,88,86),(x+w//2-7,yy),(x+w//2+6,yy-2),1)
        if glow:
            xx=x+w//2+3
            route=[(xx-2,top+24),(xx+3,top+41),(xx,base-9)]
            pygame.draw.lines(s,self.LAVA_DARK,False,route,6)
            pygame.draw.lines(s,self.LAVA,False,route,3)
            pygame.draw.line(s,self.LAVA_HI,route[0],route[1],1)

    def _ruined_gate(self,s,cx,base,w,h):
        # Ruínas integradas ao afloramento rochoso.
        x=cx-w//2;top=base-h
        pygame.draw.rect(s,(35,35,47),(x,base-6,w,7))
        for px,hh in ((x+8,45),(x+w-15,40)):
            pygame.draw.polygon(s,(83,77,84),[(px,base-7),(px+1,base-hh),(px+6,base-hh-3),(px+11,base-6)])
            pygame.draw.line(s,(149,118,106),(px+4,base-hh+4),(px+4,base-12),1)
        pygame.draw.polygon(s,(102,86,89),[(x+5,base-50),(x+w//2,base-58),(x+w-8,base-50),
                                         (x+w-8,base-45),(x+5,base-45)])
        pygame.draw.line(s,self.LAVA,(cx-2,base-46),(cx+6,base-47),1)

    def _fumarole_tower(self,s,cx,base,height):
        top=base-height
        pygame.draw.polygon(s,(53,47,56),[(cx-18,base),(cx-16,top+12),
                                          (cx-9,top+6),(cx-7,top),(cx+7,top+4),
                                          (cx+18,base)])
        pygame.draw.line(s,(131,94,94),(cx-9,top+15),(cx-8,base-8),1)
        # Emanacao fixa pequena exatamente no respiradouro.
        for j in range(3):
            yy=top-j*9;xx=cx+int(2*math.sin(j))
            pygame.draw.polygon(s,(115+j*9,102+j*9,106+j*9),[(xx-5,yy+3),(xx-3,yy),
                                                                (xx+5,yy-3),(xx+7,yy+4)])

    def _lava_pool_on_rock(self,s,cx,y,w):
        pygame.draw.polygon(s,(44,37,45),[(cx-w//2-2,y+5),(cx-w//2+4,y-1),
                                          (cx+w//2-4,y-2),(cx+w//2+3,y+5)])
        pygame.draw.line(s,self.LAVA_DARK,(cx-w//2+3,y+1),(cx+w//2-4,y+1),3)
        pygame.draw.line(s,self.LAVA,(cx-w//2+5,y),(cx+w//2-6,y),2)
        pygame.draw.line(s,self.LAVA_HI,(cx-8,y-1),(cx+10,y-1),1)

    def _obsidian_geodes(self,s,x,y,rng):
        for j in range(3):
            px=x+j*10;hh=10+j%2*5
            pygame.draw.polygon(s,(47,43,57),[(px,y+5),(px+2,y-hh),(px+7,y+3)])
            pygame.draw.line(s,(147,115,120),(px+2,y-hh+3),(px+3,y+1),1)

    def _near_volcano(self,i):
        s=self._new_chunk()
        region=self._region(i+3)
        rng=random.Random(317900+i*179)
        # Crosta superior contínua de obsidiana, sem lava cobrindo a pista toda.
        pygame.draw.rect(s,(91,75,78),(0,215,LW,11))
        pygame.draw.rect(s,(57,47,59),(0,226,LW,24))
        pygame.draw.line(s,(163,118,94),(0,215),(LW-1,215),1)
        pygame.draw.line(s,(43,37,48),(0,226),(LW-1,226),1)
        pygame.draw.line(s,(115,77,77),(0,243),(LW-1,243),1)
        # Estratos das junções de pedra, finos e não confundem objetos jogáveis.
        for x in range(7+(i%3)*2,LW-6,30):
            pygame.draw.line(s,(72,58,67),(x,226),(x+2,249),1)
            pygame.draw.line(s,(130,98,90),(x+4,219),(x+14,219),1)
            pygame.draw.rect(s,(119,93,88),(x+3,237,2,1))
        # Bolsões presos ao piso e fissuras localizadas (não viram 'obstáculos').
        fissures = {
            'caldeira': (25,97,179), 'obsidiana':(36,184),
            'cascatas':(20,112,190), 'fumarolas':(45,152),
            'ruinas_basalticas':(39,175),
        }[region]
        for j,cx in enumerate(fissures):
            self._crack_lava(s,cx+(i%3)*2,229,18+(j%2)*6,region,phase=(i+j)%3)
        # Basalto decorativo integrado à borda, fora da lógica de colisão.
        rockloc={
            'caldeira':((16,17,12),(175,21,13)),
            'obsidiana':((12,25,22),(172,24,20)),
            'cascatas':((17,20,15),(177,18,12)),
            'fumarolas':((9,22,17),(185,18,14)),
            'ruinas_basalticas':((14,26,18),(172,26,19)),
        }[region]
        for x,w,h in rockloc:
            self._ground_rock(s,x,216,w,h,region)
        # Partículas minerais estáticas SÓ na crosta.
        for j in range(16):
            x=rng.randrange(7,LW-7);y=rng.randrange(235,249)
            c=(116,84,79) if j%3 else (150,100,84)
            pygame.draw.rect(s,c,(x,y,2,1))
        return s

    def _crack_lava(self,s,cx,y,w,region,phase=0):
        x=max(2,cx-w//2);r=min(LW-3,cx+w//2)
        if phase == 0:
            pts=[(x,y+2),(x+5,y-2),(cx-3,y+1),(cx+4,y-3),(r,y+1)]
        elif phase == 1:
            pts=[(x,y-1),(x+7,y+2),(cx-2,y),(cx+5,y-2),(r,y-2)]
        else:
            pts=[(x,y+2),(x+5,y+1),(cx,y-3),(cx+4,y-1),(r,y+1)]
        pygame.draw.lines(s,(42,36,46),False,pts,6)
        pygame.draw.lines(s,(172,69,47),False,pts,4)
        pygame.draw.lines(s,self.LAVA,False,pts,2)
        pygame.draw.line(s,self.LAVA_HI,pts[2],pts[3],1)
        if region in ('caldeira','cascatas'):
            pygame.draw.rect(s,(255,231,144),(cx-1,y-2,2,1))

    def _ground_rock(self,s,x,base,w,h,region):
        y=base-h
        pygame.draw.polygon(s,(42,38,49),[(x,base),(x+3,y+9),(x+9,y),
                                          (x+w-8,y+4),(x+w-2,y+10),(x+w,base)])
        pygame.draw.polygon(s,(101,77,81),[(x+4,base-2),(x+8,y+9),
                                            (x+w//2,y+3),(x+w//2+2,base-3)])
        pygame.draw.line(s,(144,102,89),(x+8,y+7),(x+w//2,y+2),1)
        if region=='obsidiana':
            pygame.draw.line(s,(166,130,121),(x+w//2+2,y+5),(x+w-7,base-5),1)

    def _overlay_harmony(self,surf,frame,climate,night):
        if self.biome != 'vulcao':
            return super()._overlay_harmony(surf,frame,climate,night)
        # Horizonte levemente impregnado de cinzas, camada pré-renderizada.
        # Posicionado acima das cristas, sem encobrir obstáculos nem a pista.
        surf.blit(self._ash_haze_night if night > .48 else self._ash_haze_day,(0,150))
        # Atmosfera vulcânica em movimento sem emitir fumaça 'solta'.
        count = 7 if self.visual_quality else 4
        for k in range(count):
            x=int((k*73-frame*(.35+(k%3)*.12)) % (WIDTH+24))-12
            y=243+((k*47+frame//5)%135)
            col=(178,151,149,43) if k%3 else (235,151,99,53)
            pygame.draw.rect(surf,col,(x,y,1+(k%2),1))
        if climate in ('cinzas','chuva_meteoros'):
            ashcount=8 if self.visual_quality else 4
            for k in range(ashcount):
                x=int((k*61-frame*(1.4 if climate=='chuva_meteoros' else .78))%(WIDTH+24))-12
                y=186+((k*39+frame*(1.2 if climate=='chuva_meteoros' else .7))%180)
                c=(180,150,148,47) if k%2 else (151,131,143,38)
                pygame.draw.line(surf,c,(x,y),(x-2,y+5),1)
        # Noite: pequeno reflexo localizado na rocha, sem glow alto no céu.
        if night>.38:
            for k in range(3 if self.visual_quality else 2):
                x=int((k*139+frame*.23)%WIDTH)
                y=425+(k%2)*7
                pygame.draw.line(surf,(255,153,76,17),(x,y),(x+7,y),1)
