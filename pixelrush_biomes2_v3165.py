"""Pixel Rush v3.165.0 — reconstrução monumental e vida do Vulcão.

ÚNICO bioma alterado: vulcao. Os demais usam exatamente a herança v3.164.
Estruturas pré-renderizadas, lava e fumaça em quatro quadros reutilizáveis,
limites rígidos de objetos animados por tela, zero alocação de sprites por frame.
"""
from __future__ import annotations
import math
import random
import pygame
from pixelrush_biomes2_v3163 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, LH, WIDTH


class ModularBiomeScene(Previous):
    REGIONS = ('obsidiana', 'fumarolas', 'cascatas', 'caldeira', 'ruinas_basalticas')
    # A progressão usa grupos de chunks, não alternância a cada bloco.
    def _region(self, index):
        if self.biome != 'vulcao':
            return super()._region(index)
        return self.REGIONS[(max(0, index) // 3) % len(self.REGIONS)]

    def __init__(self, biome):
        super().__init__(biome)
        if biome == 'vulcao':
            self._build_volcanic_sky()
            self._map_cache.clear()

    def _build_volcano_deluxe(self):
        # Executado pela classe-base durante __init__, apenas para vulcao.
        self._vol_frame = 0
        self._vol_fx = {layer: [] for layer in ('far', 'mid', 'near')}
        self._far_period = 12 * LW
        self._layers['far'] = self._mega_far_chunks()
        self._layers['mid'] = [self._premium_mid(i) for i in range(15)]
        self._layers['near'] = [self._premium_near(i) for i in range(16)]

    def _mega_far_chunks(self):
        period = self._far_period
        whole = pygame.Surface((period, LH), pygame.SRCALPHA)
        rng = random.Random(31650001)
        # Horizonte periódico, sem salto no começo/fim do ciclo.
        for x in range(period):
            t = x * 2 * math.pi / period
            ridge = int(192 + 10 * math.sin(t * 2 + .3) + 8 * math.sin(t * 4 - .2) + 3 * math.sin(t * 9))
            y2 = min(213, ridge + 15)
            pygame.draw.line(whole, (123, 83, 84), (x, ridge), (x, y2))
            pygame.draw.line(whole, (78, 60, 68), (x, y2), (x, 224))
            if (x % 37 == 0) and (x > 12):
                pygame.draw.line(whole, (151, 105, 89), (x, ridge + 3), (x + 4, ridge + 4), 1)

        # Formações com identidade: o vulcão maior atravessa QUATRO chunks.
        self._hero_cone(whole, center=760, summit=59, radius=450, seed=12, second=False)
        self._hero_cone(whole, center=2095, summit=94, radius=335, seed=21, second=True)
        self._caldera(whole, center=1535, summit=123, radius=225)
        # Colunas/maciços basálticos só nas passagens, não dezenas de objetos soltos.
        for idx, x in enumerate((120, 160, 246, 1190, 1260, 2410, 2508)):
            self._basalt_ridge(whole, x, base=216, w=36 + idx % 3 * 7, h=42 + idx % 4 * 9)

        # Fissuras e rios alinhados com faces dos grandes vulcões.
        rivers = [
            ([(757, 91), (772, 124), (754, 146), (780, 177), (793, 210)], 13),
            ([(698, 117), (687, 143), (700, 166), (673, 190), (672, 213)], 7),
            ([(2091, 113), (2104, 139), (2082, 166), (2110, 200), (2117, 213)], 10),
            ([(1534, 143), (1550, 163), (1541, 181), (1560, 212)], 8),
        ]
        self._vol_fx['far'] = [[] for _ in range(12)]
        for points, width in rivers:
            pygame.draw.lines(whole, (66, 37, 43), False, points, width + 5)
            pygame.draw.lines(whole, (166, 59, 41), False, points, width)
            pygame.draw.lines(whole, (245, 113, 44), False, points, max(2, width // 2))
            self._register_river('far', points, width)

        for x, y, seed, sc in ((760, 63, 34, 1.0), (2095, 96, 67, .80), (1535, 128, 93, .65)):
            self._register_smoke('far', x, y, seed, sc)
        pygame.draw.rect(whole, (69, 52, 60), (0, 220, period, 5))
        pygame.draw.line(whole, (122, 84, 75), (0, 220), (period - 1, 220), 1)
        return [whole.subsurface((i * LW, 0, LW, LH)).copy() for i in range(12)]

    def _hero_cone(self, s, center, summit, radius, seed, second=False):
        base = 221
        r = random.Random(seed)
        # Corpo de massa natural: escarpas, crateras e relevos quebrados.
        outer = [
            (center-radius, base), (center-int(radius*.91), base-15),
            (center-int(radius*.72), base-52), (center-int(radius*.48), base-86),
            (center-int(radius*.24), summit+33), (center-92, summit+13),
            (center-56, summit+7), (center-49, summit-4),
            (center+38, summit-4), (center+56, summit+8),
            (center+int(radius*.27), summit+38),
            (center+int(radius*.59), base-74), (center+int(radius*.80), base-32),
            (center+radius, base),
        ]
        pygame.draw.polygon(s, (61, 48, 56), outer)
        pygame.draw.polygon(s, (111, 77, 73), [
            (center-radius+25, base), (center-int(radius*.62), base-79),
            (center-89, summit+22), (center-51, summit+12),
            (center-10, summit+43), (center-90, base-16), (center-172, base)
        ])
        pygame.draw.polygon(s, (42, 39, 49), [
            (center+36, summit+10), (center+int(radius*.22), summit+44),
            (center+int(radius*.70), base-53), (center+radius, base),
            (center+31, base), (center+4, summit+44)
        ])
        # Fendas geológicas e estratos seguem a inclinação da encosta.
        for k in range(22):
            dy = 33 + (k * 9) % max(38, (base-summit-45))
            side = -1 if k % 2 else 1
            xx = center + side * (65 + dy * .70)
            yy = summit + dy + r.randrange(-3, 4)
            col = (154, 104, 84) if side < 0 else (84, 64, 69)
            pygame.draw.line(s, col, (int(xx), yy), (int(xx + side * (13 + k % 6)), yy + 4 + k % 3), 1)
            if k % 3 == 0:
                pygame.draw.line(s, (61, 49, 58), (int(xx+side*8), yy+4), (int(xx+side*15), yy+11), 1)
        # Caldeira larga, com borda fisicamente apoiada nas vertentes.
        pygame.draw.polygon(s, (32, 31, 39), [
            (center-54, summit+6), (center-43, summit-8), (center-25, summit-13),
            (center+18, summit-14), (center+48, summit-5), (center+55, summit+8),
            (center+23, summit+17), (center-24, summit+16),
        ])
        pygame.draw.line(s, (165, 98, 72), (center-29, summit+11), (center+29, summit+10), 3)
        pygame.draw.line(s, (252, 150, 67), (center-23, summit+10), (center+22, summit+10), 2)
        pygame.draw.line(s, (255, 210, 109), (center-8, summit+9), (center+9, summit+9), 1)
        if second:
            # Cadeias de lava solidificada nas encostas.
            for delta in (-108, -65, 80):
                xx = center+delta
                pygame.draw.line(s, (94, 63, 66), (xx, summit+96), (xx+17, summit+122), 3)

    def _caldera(self, s, center, summit, radius):
        base=220
        pygame.draw.polygon(s,(70,53,62),[(center-radius,base),(center-148, summit+35),(center-100,summit+5),
                                         (center-58,summit+22),(center+68,summit+20),(center+125,summit+9),
                                         (center+radius,base)])
        pygame.draw.polygon(s,(121,82,73),[(center-radius+22,base),(center-100,summit+26),
                                         (center-53,summit+29),(center-74,base)])
        pygame.draw.polygon(s,(35,34,43),[(center-104,summit+13),(center-70,summit-2),
                                         (center+53,summit+1),(center+95,summit+15),
                                         (center+55,summit+33),(center-61,summit+31)])
        pygame.draw.line(s,(152,58,41),(center-68,summit+26),(center+67,summit+25),8)
        pygame.draw.line(s,(243,112,48),(center-62,summit+25),(center+60,summit+24),4)
        pygame.draw.line(s,(255,197,100),(center-35,summit+23),(center+15,summit+23),1)

    def _basalt_ridge(self,s,x,base,w,h):
        pts=[(x,base),(x+5,base-h+16),(x+12,base-h+6),(x+w//2,base-h),
             (x+w-13,base-h+9),(x+w-4,base-h+20),(x+w,base)]
        pygame.draw.polygon(s,(50,43,54),pts)
        pygame.draw.polygon(s,(111,78,76),[(x+6,base),(x+11,base-h+17),(x+w//2,base-h+4),(x+w//2-3,base)])
        pygame.draw.line(s,(146,100,85),(x+11,base-h+16),(x+w//2,base-h+4),1)

    # ------------------- sprites animados em cache -------------------
    def _register_river(self,layer,world_points,width):
        left=min(p[0] for p in world_points)-8
        right=max(p[0] for p in world_points)+9
        top=max(0,min(p[1] for p in world_points)-8)
        bottom=min(LH,max(p[1] for p in world_points)+9)
        bw=right-left
        bh=bottom-top
        if bw<=0 or bh<=0:return
        phases=[]
        for phase in range(4):
            image=pygame.Surface((bw,bh),pygame.SRCALPHA)
            pts=[(int(x-left),int(y-top)) for x,y in world_points]
            pygame.draw.lines(image,(218,76+phase*5,44,145),False,pts,max(2,width//2))
            # Ondulação interna desloca o brilho sem alterar a rota/forma do rio.
            for j in range(1,len(pts)):
                p=pts[j-1]; q=pts[j]
                mx=(p[0]+q[0])//2+(phase%3-1)
                my=(p[1]+q[1])//2+((phase+j)%3-1)
                pygame.draw.line(image,(255,189+phase*9,99,180),(mx,my),(mx+1,my+4),1)
            phases.append(image)
        for idx in range(len(self._vol_fx[layer])):
            tile_left=idx*LW
            clip_left=max(left,tile_left)
            clip_right=min(right,tile_left+LW)
            if clip_right<=clip_left:continue
            sx=clip_left-left
            dx=clip_left-tile_left
            sw=clip_right-clip_left
            cropped=tuple(im.subsurface((sx,0,sw,bh)).copy() for im in phases)
            self._vol_fx[layer][idx].append((dx,top,cropped))

    def _register_smoke(self,layer,cx,crater_y,seed,scale):
        """Quatro silhuetas orgânicas de fumaça, com raiz presa na cratera."""
        w=max(34,int(84*scale));h=max(54,int(104*scale))
        phases=[]
        for phase in range(4):
            sp=pygame.Surface((w,h),pygame.SRCALPHA)
            left=[];right=[];spine=[]
            levels=10
            for n in range(levels):
                t=n/(levels-1.)
                y=h-5-int(t*(h-14))
                dx=int((2+9*t)*math.sin(seed*.12+t*4.2+phase*.42))
                x=w//2+dx
                radius=max(3,int(3+16*t*scale+3*math.sin(n*2.4+phase*.3)))
                jitter=int(math.sin(seed*.33+n*1.7+phase*.55)*2)
                left.append((x-radius+jitter,y))
                right.append((x+radius+jitter,y))
                spine.append((x,y))
            # Corpo único e contínuo: sem polígonos empilhados/desconectados.
            pygame.draw.polygon(sp,(105,101,112,144),left+right[::-1])
            # Volume interno e sombras que acompanham a direção da corrente.
            interior=[]
            for n,(x,y) in enumerate(spine):
                interior.append((x-int(1+n*.6),y))
            for n in range(len(interior)-1):
                pygame.draw.line(sp,(168,140,134,41),interior[n],interior[n+1],max(1,3-n//4))
            for n in (3,6,8):
                x,y=spine[n]
                rr=5+n//2
                pygame.draw.line(sp,(168,150,142,40),(x-rr,y-2),(x+rr-1,y-3),1)
            phases.append(sp)
        idx=int(cx//LW)
        if 0<=idx<len(self._vol_fx[layer]):
            self._vol_fx[layer][idx].append((int(cx%LW-w//2),int(crater_y-h+6),tuple(phases)))

    # ------------------------- camadas intermediárias -------------------------
    def _premium_mid(self,i):
        s=super()._mid_volcano(i)
        region=self._region(i+1)
        # Reforços regionais ancorados e menos repetitivos.
        if region=='ruinas_basalticas' and i%3!=0:
            self._ancient_gate(s,112+(i%2)*8,216,64)
        elif region=='cascatas' and i%2==0:
            self._river_terrace(s,90,212,92,i)
        elif region=='obsidiana' and i%2==1:
            self._rock_strata(s,64,153,164,i)
        elif region=='fumarolas' and i%3==1:
            self._thermal_vent(s,131,216,seed=i)
        return s

    def _ancient_gate(self,s,cx,base,width):
        x=cx-width//2
        pygame.draw.rect(s,(42,37,48),(x+4,base-7,width-8,7))
        for px in (x+7,x+width-16):
            pygame.draw.polygon(s,(85,75,83),[(px,base-5),(px-3,base-49),(px+5,base-54),
                                            (px+11,base-46),(px+13,base-5)])
            for y in (base-39,base-23,base-12):
                pygame.draw.line(s,(151,104,88),(px+1,y),(px+8,y-1),1)
        pygame.draw.polygon(s,(99,81,83),[(x+3,base-51),(cx-12,base-64),
                                        (cx+6,base-59),(x+width-2,base-50),
                                        (x+width-7,base-42),(x+10,base-42)])
        pygame.draw.line(s,(230,135,83),(cx-13,base-43),(cx+11,base-42),1)
        pygame.draw.line(s,(255,185,100),(cx-2,base-43),(cx+1,base-43),1)

    def _river_terrace(self,s,x,base,w,seed):
        r=random.Random(16520+seed)
        pygame.draw.polygon(s,(53,43,53),[(x-12,base),(x,base-26),(x+17,base-40),
                                        (x+w-20,base-38),(x+w+5,base-25),(x+w+10,base)])
        pygame.draw.line(s,(129,83,72),(x+12,base-38),(x+w-22,base-36),2)
        for xx in (x+25,x+58):
            pygame.draw.line(s,(76,43,46),(xx,base-34),(xx+2,base-6),8)
            pygame.draw.line(s,(243,105,47),(xx,base-34),(xx+2,base-7),3)
            pygame.draw.line(s,(255,190,106),(xx+1,base-25),(xx+2,base-12),1)

    def _rock_strata(self,s,x,y,w,seed):
        for k in range(7):
            xx=x+k*17
            yy=y+(k%3)*9
            pygame.draw.line(s,(143,104,88),(xx,yy),(xx+10,yy-3),1)
            pygame.draw.line(s,(77,66,72),(xx+2,yy+3),(xx+8,yy+5),1)

    def _thermal_vent(self,s,x,base,seed):
        pygame.draw.polygon(s,(48,40,50),[(x-17,base),(x-9,base-28),(x,base-35),
                                        (x+10,base-20),(x+17,base)])
        pygame.draw.line(s,(222,109,61),(x-2,base-27),(x+2,base-26),2)
        # Fumaça estática de baixa altura apenas aqui, presa ao respiradouro.
        for k in range(3):
            pygame.draw.polygon(s,(113+k*9,105+k*7,112+k*7,95),
                              [(x-5-k,base-37-k*10),(x+3+k,base-40-k*10),
                               (x+8+k,base-44-k*10),(x,base-47-k*10)])

    def _premium_near(self,i):
        s=super()._near_volcano(i)
        # Acabamento de baixo contraste apenas na faixa do solo (sem novos inimigos).
        reg=self._region(i+3)
        rng=random.Random(165600+i)
        for x in range(4,223,27):
            xx=x+(i%3)
            pygame.draw.line(s,(102,80,82),(xx,237),(min(xx+8,224),237),1)
            pygame.draw.line(s,(68,55,66),(xx+2,241),(xx+5,247),1)
        for n in range(10):
            x=rng.randrange(8,216);y=rng.randrange(238,249)
            pygame.draw.rect(s,(129,92,83) if n%3 else (83,74,82),(x,y,2,1))
        if reg=='ruinas_basalticas':
            for x in (22,186):
                pygame.draw.line(s,(156,104,81),(x,217),(x+9,217),1)
        elif reg=='cascatas':
            for x in (42,148):
                pygame.draw.line(s,(232,111,57),(x,242),(x+8,242),1)
        return s

    # --------------------- render sem custo alto ---------------------
    def render_scene(self,target,travel,frame,night,climate,phase,
                     foreground_only=False,map_kind='image'):
        if self.biome=='vulcao':
            self._vol_frame=int(frame)
        return super().render_scene(target,travel,frame,night,climate,phase,
                                    foreground_only=foreground_only,map_kind=map_kind)

    def _draw_layer(self,dst,layer,travel,kind):
        if self.biome!='vulcao' or kind!='image':
            return super()._draw_layer(dst,layer,travel,kind)
        factor={'far':.12,'mid':.28,'near':.52}[layer]
        off=max(0.,travel)*factor*.5
        first=int(off//LW)
        shift=int(off%LW)
        frame_index=(int(self._vol_frame)//12)%4
        for j in range(2):
            idx=(first+j)%len(self._layers[layer])
            x=j*LW-shift
            dst.blit(self._layers[layer][idx],(x,0))
            if layer=='far':
                for lx,ly,frames in self._vol_fx[layer][idx]:
                    dst.blit(frames[frame_index],(x+lx,ly))

    def _build_volcanic_sky(self):
        # Apenas overlay atmosférico do bioma Vulcão: não altera o céu global.
        self._sky_vol_day=pygame.Surface((WIDTH,300),pygame.SRCALPHA)
        self._sky_vol_night=pygame.Surface((WIDTH,300),pygame.SRCALPHA)
        for y in range(300):
            t=y/299
            pygame.draw.line(self._sky_vol_day,(187,104,91,int(6+57*t*t)),(0,y),(WIDTH-1,y))
            pygame.draw.line(self._sky_vol_night,(128,78,88,int(4+37*t*t)),(0,y),(WIDTH-1,y))
        # Nuvens pesadas estratificadas; sem cobrir o sol ou criar outro céu.
        rng=random.Random(31650073)
        for idx in range(16):
            x=rng.randrange(-22,WIDTH-15)
            y=rng.randrange(133,276)
            ww=rng.randrange(25,89)
            hh=rng.randrange(2,6)
            pygame.draw.rect(self._sky_vol_day,(112,97,102,12+idx%3*4),(x,y,ww,hh))
            pygame.draw.rect(self._sky_vol_night,(97,83,94,10+idx%3*3),(x,y,ww,hh))

    def _overlay_harmony(self,surf,frame,climate,night):
        if self.biome!='vulcao':
            return super()._overlay_harmony(surf,frame,climate,night)
        # Faixa de horizonte: o céu diurno permanece, mas com poeira vulcânica.
        surf.blit(self._sky_vol_night if night>.43 else self._sky_vol_day,(0,120))
        # Respingo e poeira coerentes com o clima, sem camadas duplicadas.
        low=not bool(self.visual_quality)
        count=4 if low else 8
        for i in range(count):
            x=int((i*87+frame*(.36+i*.02))%(WIDTH+20))-10
            y=228+(i*43+frame//5)%165
            col=(242,150,80,45) if i%3==0 else (172,145,140,31)
            pygame.draw.rect(surf,col,(x,y,1+(i%2),1))
        if climate in ('cinzas','chuva_meteoros'):
            for i in range(5 if low else 9):
                x=int((i*69-frame*(1.1 if climate=='chuva_meteoros' else .64))%(WIDTH+20))-10
                y=175+(i*37+frame//2)%225
                pygame.draw.line(surf,(171,134,133,38),(x,y),(x-2,y+4),1)
        # Distorção térmica substituída por fitas translucidas de 1px, baratas.
        for i in range(2 if low else 3):
            x=int((i*169+frame*.42)%WIDTH)
            y=402+i*17+int(math.sin(frame*.04+i)*2)
            pygame.draw.line(surf,(246,141,85,11),(x,y),(min(WIDTH,x+25),y),1)
        # Reflexo local suave dos lagos de lava à noite.
        if night>.25:
            surf.blit(self._floor_glow_night,(0,430))
        else:
            surf.blit(self._floor_glow_day,(0,432))
