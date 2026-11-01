"""v3.157: consistência visual em Cidade Futurista, Vulcão e Ilhas Celestiais.

Arte criada uma vez no carregamento (surfaces de 225x250). Sem alteração
em física, velocidade, personagens, spawn, moedas ou obstáculos.
"""
import math
import random
import pygame
from pixelrush_biomes2_v3156 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, LH, WIDTH


class ModularBiomeScene(Previous):
    def __init__(self, biome):
        super().__init__(biome)
        if biome == 'vulcao':
            self._layers = {name: [self._volcano_chunk(name, i) for i in range(n)]
                            for name, n in [('far', 8), ('mid', 10), ('near', 12)]}
            self._map_cache.clear()
        elif biome == 'ilhas_celestes':
            self._layers = {name: [self._islands_chunk(name, i) for i in range(n)]
                            for name, n in [('far', 8), ('mid', 12), ('near', 14)]}
            self._map_cache.clear()
        elif biome == 'cidade_futurista':
            # Acabamento somente em suportes e materiais existentes.
            for i, surf in enumerate(self._layers['near']):
                self._city_finish(surf, i)
            self._map_cache.clear()

    @staticmethod
    def _s():
        return pygame.Surface((LW, LH), pygame.SRCALPHA)

    @staticmethod
    def _line(s, col, x1, y1, x2, y2, n=1):
        pygame.draw.line(s, col, (int(x1), int(y1)), (int(x2), int(y2)), n)

    def _city_finish(self, s, i):
        """Junções no deck; sem novos prédios, carros ou néon atmosférico."""
        for x in range(5 + (i % 3) * 3, LW - 6, 32):
            # juntas com dois rebites localizados no metal
            pygame.draw.line(s, (40, 62, 92), (x, 201), (x, 212), 1)
            pygame.draw.rect(s, (136, 159, 183), (x + 3, 207, 2, 1))
            pygame.draw.rect(s, (136, 159, 183), (x + 3, 211, 2, 1))
        # remate de concreto/metal contínuo de ponta a ponta.
        pygame.draw.line(s, (88, 119, 154), (0, 218), (LW - 1, 218), 1)

    # =========================== VULCÃO ====================================
    @staticmethod
    def _v157_ridge_height(u, plane):
        """Onda periódica nas bordas, sem descontinuidade de x 224 para x 0."""
        a = 2 * math.pi * (u % (LW * 8)) / (LW * 8)
        if plane == 0:
            return int(171 - 24 * abs(math.sin(2*a + .5)) - 11 * abs(math.sin(5*a - .6)))
        return int(197 - 12 * abs(math.sin(3*a + .8)) - 5 * abs(math.sin(7*a)))

    def _volcano_chunk(self, layer, i):
        s = self._s()
        rng = random.Random(315700 + 113*i + {'far':0,'mid':1000,'near':2000}[layer])
        if layer == 'far':
            # Dois relevos com altura contínua entre todos os 8 chunks.
            for p, col in ((0, (84, 64, 75)), (1, (65, 53, 65))):
                for x in range(LW):
                    y = self._v157_ridge_height(i * LW + x, p)
                    self._line(s, col, x, y, x, 217)
            for x in range(12, LW-4, 19):
                y = self._v157_ridge_height(i*LW+x,1) + 3
                self._line(s,(114,83,91),x,y,x+5,y+2)
            # Um cone por distrito vulcânico, com cume e lava conectados à montanha.
            if i in (1, 5):
                cx = 120 if i == 1 else 105
                top = 109 if i == 1 else 122
                pygame.draw.polygon(s,(71,50,61),[(cx-62,202),(cx,top),(cx+65,202)])
                pygame.draw.polygon(s,(106,73,76),[(cx-39,190),(cx,top+18),(cx+17,169),(cx+30,202)])
                pygame.draw.polygon(s,(42,36,47),[(cx-14,top+10),(cx-7,top-1),(cx+9,top-1),(cx+14,top+10)])
                self._line(s,(231,107,57),cx+3,top+10,cx+12,top+29,2)
                self._line(s,(255,183,89),cx+6,top+14,cx+11,top+25)
                self._smoke_column(s, cx, top-8, 51, rng)
            # Silhueta de cinzas no pé, sem fumaça arredondada voando.
            pygame.draw.rect(s,(64,51,63),(0,215,LW,6))
        elif layer == 'mid':
            pygame.draw.rect(s,(76,60,70),(0,207,LW,17))
            pygame.draw.line(s,(111,84,89),(0,207),(LW-1,207),1)
            # Máximo 3 colunas; todas encostam na rocha de base.
            variants = (
                ((14,41,54),(93,34,68),(175,36,60)),
                ((27,35,59),(104,47,77),(181,29,50)),
                ((12,29,47),(70,35,64),(151,48,73)),
                ((18,43,69),(113,37,57),(188,26,49)),
                ((34,34,55),(112,43,72),(181,32,60)),
            )
            for j,(x,w,h) in enumerate(variants[i % len(variants)]):
                self._basalt(s, x, 211, w, h, rng, glow=(j+i)%3==0)
            if i % 3 == 1:
                self._lava_fissure(s, 77, 209, 41, rng)
            # restrição de partículas: só dentro da base mineral.
            for _ in range(17):
                xx=rng.randrange(0,LW); yy=rng.randrange(211,222)
                pygame.draw.rect(s,(117,86,83), (xx,yy,2,1))
        else:
            # Platô contínuo com crosta preta e lava em fissuras, nunca soltas.
            pygame.draw.rect(s,(86,66,69),(0,216,LW,17))
            pygame.draw.rect(s,(56,46,55),(0,233,LW,17))
            pygame.draw.line(s,(157,105,80),(0,216),(LW-1,216),1)
            pygame.draw.line(s,(227,119,62),(0,230),(LW-1,230),2)
            pygame.draw.line(s,(92,67,69),(0,236),(LW-1,236),1)
            for x in range(8+(i%3)*3,LW-9,36):
                self._lava_fissure(s, x, 223, 15 + (x//30)%8, rng)
            # rochas como afloramentos da base: nunca flutuando.
            for x,w,h in ((12,17,11),(90,24,14),(177,18,10)):
                if (i + x) % 3 != 1:
                    self._v157_rock(s,x+(i%2)*2,217,w,h,rng)
            for x in range(4,LW,22):
                yy=240+(x+i)%6
                self._line(s,(103,76,72),x,yy,min(LW-1,x+8),yy)
        return s

    @staticmethod
    def _smoke_column(s, x, crater, height, rng):
        """Coluna segmentada ancorada ao cone; sem elipses flutuantes."""
        for n in range(6):
            y = crater - n * 8
            cx = x + int(4 * math.sin(n * 0.9 + (x % 7)))
            w = 12 + n * 2
            c = ((102,90,103),(114,103,113),(127,116,122))[min(2,n//2)]
            pygame.draw.polygon(s,c,[(cx-w//2,y+7),(cx-w//2-2,y+2),(cx-3,y-2),
                                     (cx+w//2,y-4),(cx+w//2+2,y+4),(cx+w//2-1,y+9)])
            selfcol=(151,128,128) if n%2==0 else (142,124,133)
            pygame.draw.line(s,selfcol,(cx-w//3,y+1),(cx,y-2),1)

    @staticmethod
    def _basalt(s,x,base,w,h,rng,glow=False):
        top=base-h
        pygame.draw.polygon(s,(41,37,47),[(x,base),(x+3,top+7),(x+8,top),
                                          (x+w-8,top+2),(x+w-2,top+12),(x+w,base)])
        pygame.draw.polygon(s,(73,62,71),[(x+6,base-2),(x+8,top+10),
                                         (x+w//2,top+3),(x+w-7,base-2)])
        pygame.draw.line(s,(110,90,90),(x+9,top+9),(x+11,base-4),1)
        pygame.draw.line(s,(35,32,44),(x+w-7,top+10),(x+w-8,base-3),2)
        for yy in range(top+14,base-8,14):
            pygame.draw.line(s,(99,80,83),(x+w//2-3,yy),(x+w//2+6,yy-2),1)
        if glow:
            xx=x+w//2
            for yy in range(top+18,base-4,7):
                pygame.draw.line(s,(223,105,56),(xx,yy),(xx+2,yy+3),2)
                pygame.draw.line(s,(255,194,103),(xx+1,yy),(xx+1,yy+2),1)
        pygame.draw.line(s,(116,91,87),(x+1,base-1),(x+w-2,base-1),1)

    @staticmethod
    def _lava_fissure(s,x,y,w,rng):
        pygame.draw.polygon(s,(42,38,45),[(x-2,y+3),(x+4,y-1),(x+w-3,y-2),(x+w+2,y+3)])
        pygame.draw.line(s,(213,92,46),(x+2,y),(x+w-2,y),2)
        pygame.draw.line(s,(255,188,90),(x+5,y-1),(x+w-5,y-1),1)
        pygame.draw.rect(s,(255,213,113),(x+w//2,y-1,2,1))

    @staticmethod
    def _v157_rock(s,x,base,w,h,rng):
        pygame.draw.polygon(s,(49,43,52),[(x,base),(x+3,base-h+6),(x+w//2,base-h),
                                          (x+w-3,base-h+5),(x+w,base)])
        pygame.draw.line(s,(126,100,98),(x+5,base-h+7),(x+w//2,base-h+2),1)
        pygame.draw.line(s,(88,70,76),(x+w//2,base-h+2),(x+w-5,base-3),1)

    # ========================== ILHAS ======================================
    def _islands_chunk(self, layer, index):
        s=self._s()
        rng=random.Random(317900+index*139+{'far':0,'mid':1000,'near':2000}[layer])
        if layer=='far':
            # Fundo: poucas ilhas completas; nuvens do céu já existentes.
            configs=(((12,122,65,39),(129,111,71,44)),
                     ((22,108,76,45),(135,128,60,37)),
                     ((12,132,62,38),(108,104,87,50)),
                     ((26,115,70,42),(146,127,55,33)))
            for j,(x,y,w,h) in enumerate(configs[index%4]):
                self._island_shape(s,x,y,w,h,rng,level=0, temple=False,fall=False)
        elif layer=='mid':
            configs=(
                ((18,155,84,56,False,False),(128,137,78,49,True,False)),
                ((22,147,78,50,False,True),(132,159,71,41,False,False)),
                ((14,160,65,42,False,False),(110,142,95,59,True,True)),
                ((27,150,79,49,True,False),(149,157,58,44,False,False)),
                ((16,150,73,50,False,True),(110,142,89,54,False,False)),
                ((22,159,75,47,False,False),(130,142,78,56,True,False)),
            )
            for x,y,w,h,temple,fall in configs[index%6]:
                self._island_shape(s,x,y,w,h,rng,level=1,temple=temple,fall=fall)
        else:
            # Piso modular, claro e contínuo. Cenário NÃO altera hitbox real.
            pygame.draw.rect(s,(118,137,155),(0,221,LW,11))
            pygame.draw.line(s,(215,239,242),(0,221),(LW-1,221),2)
            pygame.draw.rect(s,(87,113,139),(0,233,LW,17))
            pygame.draw.line(s,(162,206,222),(0,233),(LW-1,233),1)
            for xx in range(8+(index%3)*3,LW,26):
                pygame.draw.line(s,(128,161,182),(xx,227),(min(LW-1,xx+10),227),1)
                pygame.draw.line(s,(74,95,116),(xx+2,241),(min(LW-1,xx+8),241),1)
            # Apenas duas ilhas laterais; deixam o corredor livre de ruído.
            configs=(((5,177,57,34),(162,176,58,37)),
                     ((15,184,58,31),(173,181,49,34)),
                     ((8,175,62,38),(163,186,56,29)),
                     ((16,182,54,34),(169,173,54,39)))
            for x,y,w,h in configs[index%4]:
                self._island_shape(s,x,y,w,h,rng,level=2,temple=False,fall=False)
        return s

    def _island_shape(self,s,x,y,w,h,rng,level,temple=False,fall=False):
        """Volume único conectado: grama acima, rocha abaixo, sem fragmentos soltos."""
        # A ilha se mantém inteiramente dentro do chunk para não cortar no limite.
        assert 0 <= x and x+w <= LW
        rock=(76,80,112) if level==0 else ((70,75,107) if level==1 else (80,91,121))
        side=(115,117,146) if level==0 else (125,131,161)
        grass=(113,175,131) if level==0 else ((104,191,137) if level==1 else (119,206,146))
        # Pontas em segmentos, nenhuma elipse, fechamento em cone.
        pygame.draw.polygon(s,rock,[(x+1,y+4),(x+w-2,y+5),(x+w-9,y+h//2),
                                    (x+w//2+7,y+h-5),(x+w//2,y+h),(x+w//3,y+h-9),
                                    (x+8,y+h//2)])
        pygame.draw.polygon(s,side,[(x+4,y+7),(x+w//2,y+11),(x+w//2-3,y+h-12),
                                    (x+w//3,y+h//2),(x+6,y+h//3)])
        pygame.draw.polygon(s,(51,62,92),[(x+w//2+7,y+12),(x+w-6,y+6),
                                         (x+w-11,y+h//2),(x+w//2+5,y+h-7)])
        # Platô gramado sem ultrapassar os limites do bloco.
        pygame.draw.polygon(s,(70,122,104),[(x+1,y+4),(x+7,y-1),(x+w-9,y-1),(x+w-2,y+4),(x+w-7,y+9),(x+4,y+9)])
        pygame.draw.polygon(s,grass,[(x+3,y+2),(x+12,y-3),(x+w-14,y-3),
                                    (x+w-4,y+2),(x+w-9,y+6),(x+6,y+6)])
        pygame.draw.line(s,(187,230,161),(x+9,y),(x+w-11,y),1)
        # Estratificação mineral e fissuras realmente sobre a ilha.
        for k in range(3):
            dx = 8 + k*(w-15)//3
            xx=x+dx
            yy=y+10+k%2*5
            pygame.draw.line(s,(153,155,177),(xx,yy),(xx+5,yy+3),1)
            pygame.draw.line(s,(96,112,146),(xx+2,yy+4),(xx+1,yy+9),1)
        for k in range(max(3,w//11)):
            xx=x+8+k*(w-16)//max(3,w//11)
            pygame.draw.line(s,(166,229,170),(xx,y),(xx+2,y-2),1)
            if k%4==0 and level>0:
                pygame.draw.rect(s,(239,198,219),(xx+1,y-3,2,2))
        # Raízes pequenas presas à rocha.
        if level<2:
            for dx in (w//3,2*w//3):
                xx=x+dx; yy=y+h//2+2
                pygame.draw.line(s,(85,134,119),(xx,yy),(xx+1,yy+9),1)
                pygame.draw.line(s,(130,190,153),(xx+1,yy+5),(xx+4,yy+2),1)
        if temple:
            self._temple_on_island(s,x+w//2,y,w)
        if fall:
            self._water_from_island(s,x+w//2+5,y+8,min(54,250-y-9),rng)

    @staticmethod
    def _temple_on_island(s,cx,grass_y,island_w):
        # Templo compacto assenta diretamente sobre o platô.
        w=min(35,max(25,island_w-25)); x=cx-w//2; base=grass_y
        pygame.draw.rect(s,(145,165,185),(x,base-24,w,24))
        pygame.draw.rect(s,(199,218,228),(x+2,base-23,w-4,20))
        pygame.draw.polygon(s,(224,233,242),[(x-2,base-24),(cx,base-33),(x+w+2,base-24)])
        for col in range(x+5,x+w-4,9):
            pygame.draw.rect(s,(143,170,188),(col,base-19,3,18))
            pygame.draw.line(s,(237,246,246),(col,base-18),(col,base-4),1)
        pygame.draw.rect(s,(103,138,161),(x+w//2-3,base-11,6,10))
        pygame.draw.line(s,(155,235,233),(x+3,base-25),(x+w-3,base-25),1)
        pygame.draw.line(s,(93,135,128),(x-2,base+2),(x+w+2,base+2),2)

    @staticmethod
    def _water_from_island(s,x,y,length,rng):
        # Água nasce na borda da ilha e se dissolve em gotas, não em bloco abrupto.
        pygame.draw.line(s,(63,143,175),(x,y),(x,y+length-10),5)
        pygame.draw.line(s,(136,221,233),(x-1,y),(x-1,y+length-12),2)
        pygame.draw.line(s,(218,248,250),(x,y+5),(x,y+length-14),1)
        for k in range(6):
            xx=x+rng.randrange(-4,5); yy=y+length-12+k*2
            if yy<250:pygame.draw.rect(s,(137,217,231),(xx,yy,1+(k%2),1))

    # Os passes antigos pintavam nuvens redondas, extras fora das ilhas e
    # efeitos duplicados. Este bioma já tem arte e overlay próprios.
    def _microeventos(self, surf, travel, frame, climate, night):
        if self.biome in ('vulcao','ilhas_celestes'):
            return
        return super()._microeventos(surf,travel,frame,climate,night)

    def _overlay_volcano(self, surf, frame, climate, night):
        if self.biome != 'vulcao':
            return super()._overlay_volcano(surf,frame,climate,night)

    def _overlay_sky(self, surf, frame, climate, night):
        if self.biome != 'ilhas_celestes':
            return super()._overlay_sky(surf,frame,climate,night)

    def _overlay_volcano_premium(self, surf, frame, climate, night):
        if self.biome != 'vulcao':
            return super()._overlay_volcano_premium(surf,frame,climate,night)

    def _overlay_sky_premium(self, surf, frame, climate, night):
        if self.biome != 'ilhas_celestes':
            return super()._overlay_sky_premium(surf,frame,climate,night)

    # ========================= DYNAMIC ================================
    def _overlay_harmony(self,surf,frame,climate,night):
        if self.biome == 'cidade_futurista':
            return super()._overlay_harmony(surf,frame,climate,night)
        if self.biome == 'vulcao':
            # poucos fragmentos e cinza quente; não repete os overlays históricos.
            count=9 if self.visual_quality else 4
            for i in range(count):
                x=int((i*71-frame*(.7+i%3*.18))%(WIDTH+30))-15
                y=230+int((i*41-frame*(.36+i%2*.12))%155)
                c=(255,160,92,58) if i%3 else (216,130,89,42)
                pygame.draw.rect(surf,c,(x,y,2,2))
            if climate in ('cinzas','chuva_meteoros'):
                for i in range(5 if self.visual_quality else 3):
                    x=int((i*101-frame*1.5)%(WIDTH+25))-12
                    y=175+int((i*47+frame*.8)%210)
                    pygame.draw.line(surf,(160,137,139,58),(x,y),(x-3,y+8),1)
        elif self.biome == 'ilhas_celestes':
            # Partículas celestes quase pontuais, maiores apenas no modo normal.
            for i in range(8 if self.visual_quality else 4):
                x=int((i*71-frame*.32)%(WIDTH+12))-6
                y=205+(i*39+frame//6)%140
                pygame.draw.rect(surf,(192,239,222,68) if i%3 else (240,217,174,62),(x,y,2,1))
            if night>.35:
                for i in range(5 if self.visual_quality else 2):
                    x=int((i*91+frame*.27)%WIDTH)
                    y=235+(i*35)%98
                    pygame.draw.circle(surf,(156,243,204,61),(x,y),1)
            if climate in ('brisa_celeste','tempestade_vento'):
                for i in range(4 if self.visual_quality else 2):
                    x=int((i*101-frame*1.1)%(WIDTH+10))-5
                    y=230+(i*44+frame//3)%90
                    pygame.draw.line(surf,(222,247,247,45),(x,y),(x+4,y),1)
        else:
            return super()._overlay_harmony(surf,frame,climate,night)
