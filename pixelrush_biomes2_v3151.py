"""v3.151 — Ilhas Celestiais: acabamento nas ilhas existentes, sem novas entidades.
Arte elaborada uma vez por chunk, reutilizando o renderizador e seus mapas técnicos.
"""
import math
import random
import pygame
from pixelrush_biomes2_v3150 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW

class ModularBiomeScene(Previous):
    def _cloud(self, surf, x, y, scale=1.0, tint=(236,244,255)):
        # Somente Ilhas: substitui as antigas bolas brancas arredondadas por
        # nuvens pixeladas de borda escalonada, sem duplicar sprites existentes.
        if self.biome != 'ilhas_celestes':
            return super()._cloud(surf,x,y,scale,tint)
        px=lambda a: int(x+a*scale)
        py=lambda a: int(y+a*scale)
        shadow=tuple(max(0,int(c*.79)) for c in tint)
        mid=tuple(max(0,int(c*.91)) for c in tint)
        line=[(-31,10),(-28,2),(-20,2),(-17,-7),(-7,-7),(-4,-12),(10,-12),
              (13,-4),(23,-4),(25,2),(32,2),(32,14),(24,14),
              (24,19),(-24,19),(-24,15),(-31,15)]
        pygame.draw.polygon(surf,shadow,[(px(a),py(b)) for a,b in line])
        highlight=[(-26,8),(-22,1),(-15,1),(-13,-5),(-4,-5),(0,-10),
                   (9,-10),(12,-2),(20,-2),(23,4),(28,4),(28,11),(-26,11)]
        pygame.draw.polygon(surf,mid,[(px(a),py(b)) for a,b in highlight])
        for a,b,c in ((-17,4,13),(-6,-6,13),(9,1,12)):
            pygame.draw.line(surf,tint,(px(a),py(b)),(px(a+c),py(b)),max(1,int(scale)))
        for a,b,c in ((-19,14,14),(3,15,16)):
            pygame.draw.line(surf,shadow,(px(a),py(b)),(px(a+c),py(b)),1)

    def __init__(self, biome):
        super().__init__(biome)
        if biome == 'ilhas_celestes':
            for layer, chunks in self._layers.items():
                for index, surf in enumerate(chunks):
                    self._polish_islands(surf, layer, index)
            self._map_cache.clear()

    @staticmethod
    def _landmarks(layer, i):
        if layer == 'far':
            return ((9,126,73,44,False,False),(123,103,83,55,False,False))
        if layer == 'mid':
            return (
              ((20,158,80,48,False,False),(124,142,84,54,True,False)),
              ((22,154,70,43,False,True),(118,146,94,58,False,False)),
              ((14,161,62,38,False,False),(90,145,63,44,False,True),(161,157,61,39,False,False)),
              ((26,156,80,46,True,False),(150,151,58,36,False,True)),
            )[i%4]
        return (
          ((5,187,55,35,False,False),(166,181,56,38,False,False)),
          ((17,180,74,43,False,False),(156,190,50,31,False,False)),
          ((30,188,52,33,False,False),(95,176,66,42,True,False),(174,188,46,29,False,False)),
          ((8,191,42,26,False,False),(177,191,41,26,False,False)),
        )[i%4]

    def _polish_islands(self, surface, layer, index):
        rng = random.Random(315100 + index*109 + {'far':0,'mid':1000,'near':2000}[layer])
        for island_no,(x,y,w,h,temple,waterfall) in enumerate(self._landmarks(layer,index)):
            # Não redesenha a ilha: textura rochosa acompanha o volume existente.
            for dx in range(12,w-12,9):
                xx=x+dx
                yy=y+11 + int((h*.3) * (1-abs(dx-w*.5)/max(1,w*.5)))
                if 0 <= xx < LW:
                    pygame.draw.line(surface,(94,105,128),(xx,yy),(xx+2,yy+4),1)
                    pygame.draw.line(surface,(145,156,179),(xx+1,yy),(xx+3,yy+2),1)
                    if dx%3==0:
                        pygame.draw.line(surface,(70,86,111),(xx+2,yy+5),(xx+1,yy+11),1)
            # Gramado com folhas pequenas, flores e bioluminescência pontual.
            for k in range(max(6,w//7)):
                xx=x+7+(k*7)%(w-15)
                yy=y+2+(k%3)
                if 0 <= xx < LW:
                    c=((164,220,129),(207,233,148),(123,191,141))[k%3]
                    pygame.draw.line(surface,c,(xx,yy),(xx+2,yy-1-(k%2)),1)
                    if (k+index+island_no)%5==0:
                        pygame.draw.rect(surface,(241,191,213) if k%2 else (227,229,174),(xx+1,yy-3,2,2))
            # Lianas ancoradas nas bordas rochosas. Mantém a pista intocada.
            if layer!='near':
                for d in (w//4,w*3//4):
                    xx=x+d
                    by=y+12 + h//3
                    length= min(13,6+h//5)
                    if 0 < xx < LW-3:
                        pygame.draw.line(surface,(83,137,117),(xx,by),(xx+1,by+length),1)
                        pygame.draw.line(surface,(131,194,154),(xx,by+length-3),(xx+4,by+length-6),1)
            if temple:
                # Entalhes e detalhes nos templos existentes, sem redesenhá-los.
                left=x+w//2-20
                ty=y-6
                for k in range(4):
                    xx=left+ k*12
                    if 1<xx<LW-2:
                        pygame.draw.rect(surface,(231,244,244),(xx,ty,2,3))
                        pygame.draw.line(surface,(156,203,205),(xx+1,ty+5),(xx+1,ty+9),1)
            if waterfall:
                # Reflexos no canal existente (estáticos no chunk; o fluxo já é animado).
                wx=x+w//2
                for yy in range(y+h//3+6, min(244,y+h+10),11):
                    pygame.draw.line(surface,(223,251,253),(wx,yy),(wx+1,yy+4),1)
                    pygame.draw.line(surface,(112,197,218),(wx+3,yy+3),(wx+3,yy+7),1)
        if layer == 'near':
            # Discretos cristais laterais, fora do corredor de corrida.
            for xx in (12,31,194,210):
                yy=218+(index+xx)%3
                pygame.draw.polygon(surface,(138,211,215),[(xx,yy+5),(xx+2,yy-4),(xx+5,yy+5)])
                pygame.draw.line(surface,(234,252,242),(xx+2,yy-2),(xx+2,yy+3),1)

    def _overlay_harmony(self, surf, frame, climate, night):
        super()._overlay_harmony(surf,frame,climate,night)
        if self.biome != 'ilhas_celestes':
            return
        # Partículas leves; reusa apenas primitivas, sem novas Surface por quadro.
        windy=climate in ('brisa_celeste','tempestade_vento')
        amount=8 if self.visual_quality else 4
        for i in range(amount):
            x=int((i*67-frame*(1.7 if windy else .35))%475)-12
            y=125+(i*31+int(5*math.sin(frame*.033+i)))%167
            col=(188,240,223) if i%3 else (235,224,184)
            pygame.draw.line(surf,col,(x,y),(x+2+(1 if windy else 0),y),1)
        if night>.28:
            for i in range(6 if self.visual_quality else 3):
                xx=int((i*73+frame*.43)%465)-5
                yy=187+(i*29)%135+int(3*math.sin(frame*.04+i))
                pygame.draw.circle(surf,(172,239,219),(xx,yy),1)
