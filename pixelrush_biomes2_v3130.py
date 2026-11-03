"""Extended desert districts; bounded caches, coprime layer periods."""
import math,random,os
from collections import OrderedDict
import pygame
import numpy as np
from pixelrush_biomes2_v3129 import ModularBiomeScene as Previous,LAMP,WATER,DISTRICTS
from pixelrush_biomes2_v3128 import DEPTH, _QA_SHARE_DAYLIGHT
from pixelrush_biomes2_v3126 import LW,LH,WIDTH,HEIGHT,SUPPORTED_BIOMES
# Requested refinements are integrated into normal gameplay. Classic remains opt-out.
MODULAR_BIOMES=('neve','deserto')
COUNTS={'far':17,'mid':19,'near':23}
THEMES=('Bazar dos Tecidos','Biblioteca de Arenito','Jardins do Oasis','Portao Imperial','Caravancarai','Templo Escavado','Vila dos Oleiros','Observatorio das Dunas')

class ModularBiomeScene(Previous):
    def __init__(self,biome):
        if biome!='deserto':
            super().__init__(biome);return
        self.biome=biome;self.visual_quality=1;self._pose=0
        self._maps=OrderedDict();self._night_tiles=OrderedDict()
        self._composites={};self._geometry_view=None;self._last_state=None
        self._weather=pygame.Surface((LW,LH),pygame.SRCALPHA)
        self._layers={layer:[self._make_chunk(layer,i) for i in range(COUNTS[layer])] for layer in DEPTH}
        self._poses=[self._layers]
        for pose in (1,2):
            self._pose=pose
            self._poses.append({layer:[self._make_chunk(layer,i) for i in range(COUNTS[layer])] if layer=='near' else self._layers[layer] for layer in DEPTH})
        self._pose=0
        self._lamp_pixels={}
        for layers in self._poses:
            for tiles in layers.values():
                for src in tiles:
                    if id(src) not in self._lamp_pixels:
                        lit=np.all(pygame.surfarray.array3d(src)==LAMP,axis=2)
                        self._lamp_pixels[id(src)]=[tuple(map(int,xy)) for xy in np.argwhere(lit)]

    def _desert_palace(self,s,x,base,w,h,idx):
        super()._desert_palace(s,x,base,w,h,idx)
        if self.biome!='deserto':return
        top=base-h
        # Carved cornice, turquoise mosaic and recessed shutters.
        for xx in range(x+5,x+w-4,6):
            pygame.draw.rect(s,(65,116,122),(xx,top+5,3,3))
            pygame.draw.rect(s,(225,210,151),(xx+1,top+6,1,1))
        for yy in range(top+21,base-25,21):
            for xx in range(x+8,x+w-9,16):
                pygame.draw.rect(s,(113,71,63),(xx,yy,8,11))
                pygame.draw.line(s,(211,148,91),(xx+2,yy+1),(xx+2,yy+9))
                pygame.draw.line(s,(61,91,94),(xx+5,yy+2),(xx+5,yy+8),2)
        if w>39:
            yy=base-29
            pygame.draw.rect(s,(82,65,63),(x+5,yy,w-10,3))
            for xx in range(x+7,x+w-5,5):pygame.draw.line(s,(126,88,69),(xx,yy-5),(xx,yy))
            pygame.draw.line(s,(244,189,121),(x+5,yy-6),(x+w-5,yy-6))
        self._lantern(s,x+w-7,base-18)

    def _arch(self,s,x,base,w,h):
        super()._arch(s,x,base,w,h)
        top=base-h
        # Radial joints and carved keystone give the arch depth.
        for i in range(9):
            a=math.pi*i/8
            cx=x+w/2;cy=top+6+(h-10)/2
            p1=(round(cx+math.cos(a)*(w/2-3)),round(cy-math.sin(a)*(h-10)/2))
            p2=(round(cx+math.cos(a)*(w/2-7)),round(cy-math.sin(a)*(h-16)/2))
            pygame.draw.line(s,(144,96,77),p1,p2)
        pygame.draw.polygon(s,(69,119,123),[(x+w//2-3,top+3),(x+w//2,top),(x+w//2+3,top+3),(x+w//2,top+6)])

    def _rug(self,s,x,y,w,h,color):
        pygame.draw.rect(s,(80,59,65),(x-1,y-1,w+2,h+2))
        pygame.draw.rect(s,color,(x,y,w,h))
        pygame.draw.rect(s,(226,189,122),(x+2,y+2,w-4,h-4),1)
        pygame.draw.polygon(s,(230,197,140),[(x+w//2,y+4),(x+w-4,y+h//2),(x+w//2,y+h-4),(x+4,y+h//2)],1)
        for xx in range(x+1,x+w,3):pygame.draw.line(s,(222,191,139),(xx,y+h),(xx,y+h+2))

    def _well(self,s,x,base):
        pygame.draw.ellipse(s,(106,77,65),(x-14,base-8,28,11))
        pygame.draw.rect(s,(197,146,99),(x-13,base-8,26,6))
        pygame.draw.ellipse(s,(238,190,126),(x-14,base-11,28,7))
        pygame.draw.ellipse(s,(47,67,66),(x-10,base-10,20,4))
        for xx in (x-12,x+12):pygame.draw.line(s,(104,68,52),(xx,base-28),(xx,base-6),2)
        pygame.draw.line(s,(155,103,65),(x-14,base-28),(x+14,base-28),3)
        pygame.draw.line(s,(212,171,110),(x,base-27),(x,base-9))

    def _make_chunk(self,layer,index):
        if self.biome!='deserto':return super()._make_chunk(layer,index)
        rng=random.Random(13000+index*191+{'far':3,'mid':7,'near':11}[layer])
        theme=index%8
        s=pygame.Surface((LW,LH),pygame.SRCALPHA)
        if layer=='far':
            for j in range(rng.randint(2,4)):
                x=12+j*53+rng.randint(0,9);h=rng.randint(29,72);w=rng.randint(19,34)
                pygame.draw.polygon(s,(166,119,104),[(x,179),(x+4,179-h),(x+w-5,175-h),(x+w,179)])
                for y in range(184-h,178,8):pygame.draw.line(s,(195,143,111),(x+5,y),(x+w-4,y+2))
            for k,(base,col) in enumerate(((163,(212,154,102)),(184,(232,177,114)),(205,(244,195,128)))):
                amp=rng.randint(9,22);shape=1+(index+k)%3
                pts=[(x,round(base-amp*math.sin(math.pi*x/LW)**2*(.75+.25*math.cos(shape*math.pi*x/LW)))) for x in range(LW+1)]
                pygame.draw.polygon(s,col,pts+[(LW,234),(0,234)])
                pygame.draw.lines(s,(251,211,150),False,pts,1)
                for x in range(18,LW-20,31):
                    yy=pts[x][1]+5
                    pygame.draw.line(s,(222,163,107),(x,yy),(x+10,yy-1))
        elif layer=='mid':
            pygame.draw.rect(s,(185,128,95),(0,208,LW,25))
            if theme==2:
                pygame.draw.ellipse(s,(130,140,94),(20,191,187,26))
                pygame.draw.ellipse(s,WATER,(28,194,170,17))
                for x in range(36,188,17):pygame.draw.line(s,(123,186,177),(x,199+x%3),(x+9,199+x%3))
                for x,h in ((22,54),(64,68),(179,63),(209,41)):self._palm(s,x,211,h,index)
                self._desert_palace(s,98,193,37,40,index)
            elif theme in (3,5):
                self._arch(s,76,211,70,80+rng.randrange(15))
                for x in (43,150):self._desert_palace(s,x,211,28,71+rng.randrange(15),index+x)
                for x in (17,197):
                    pygame.draw.rect(s,(186,125,86),(x,165,10,46))
                    pygame.draw.rect(s,(242,188,123),(x-2,163,14,4))
            elif theme==7:
                self._desert_palace(s,76,211,73,83,index)
                pygame.draw.ellipse(s,(99,146,146),(82,106,61,28))
                pygame.draw.rect(s,(99,146,146),(82,120,61,9))
                pygame.draw.arc(s,(170,195,169),(87,108,50,23),0,math.pi,2)
                pygame.draw.line(s,(244,201,133),(112,106),(112,99),2)
                for x in (20,174):self._arch(s,x,211,32,51)
            else:
                for j,x in enumerate((8,81,164)):
                    self._desert_palace(s,x,211,rng.randint(39,51),rng.randint(46,76),index+j)
                if theme in (0,4):
                    pygame.draw.line(s,(84,64,61),(44,158),(174,164))
                    for x in range(51,169,12):
                        y=158+(x-44)*6//130
                        pygame.draw.polygon(s,(68,116,121) if x%2 else (168,83,69),[(x,y),(x+6,y),(x+3,y+7)])
            pygame.draw.rect(s,(195,136,95),(0,218,LW,15))
        else:
            pygame.draw.rect(s,(196,138,98),(0,221,LW,12))
            # Eight compositions, plus seeded heights/widths/props: 23 unique near chunks.
            layouts=(((5,42),(150,52)),((8,61),(171,43)),((5,35),(176,40)),((6,46),(165,52)),((7,50),(145,65)),((7,35),(182,35)),((8,52),(160,48)),((5,42),(162,57)))
            for j,(x,w) in enumerate(layouts[theme]):
                h=rng.randint(49,80);w+=rng.randrange(5)
                self._desert_palace(s,x,229,w,h,index+j)
                if theme in (0,1,4,6):self._rug(s,x+8,192,16,23,(153,68,66) if j else (62,111,119))
            if theme in (0,4,6):
                self._market(s,72,229,49+rng.randrange(14),index)
                for x in (60,139):self._pot(s,x,229)
            elif theme==2:
                self._well(s,112,229)
                self._palm(s,62,230,48,index);self._palm(s,151,230,52,index)
            elif theme==1:
                self._arch(s,88,229,48,53)
                self._rug(s,99,193,17,26,(143,67,62))
            elif theme==3:
                self._well(s,99,229);self._palm(s,144,230,46,index)
            elif theme==5:
                self._arch(s,82,229,57,61)
                for x in (59,157):
                    pygame.draw.polygon(s,(171,111,81),[(x-7,229),(x-4,216),(x+5,212),(x+12,229)])
                    pygame.draw.line(s,(239,180,115),(x-2,217),(x+4,214),2)
            else:
                self._palm(s,77,230,49,index);self._well(s,127,229)
            # Mineral chips only inside the pavement; endpoints stay identical.
            pygame.draw.line(s,(250,198,128),(0,228),(LW,228),2)
            pygame.draw.rect(s,(185,123,88),(0,230,LW,4))
            pygame.draw.rect(s,(124,87,73),(0,234,LW,16))
            for _ in range(24):
                x=rng.randrange(4,LW-6);y=rng.randrange(237,249)
                pygame.draw.line(s,(155,105,79),(x,y),(x+rng.randrange(2,5),y))
        haze=DEPTH[layer][1]
        if haze:
            arr=pygame.surfarray.pixels3d(s);arr[:]=arr*(1-haze)+np.array((224,173,132))*haze;del arr
        return s

    def _tile_map(self,layer,idx,kind):
        if self.biome!='deserto':return super()._tile_map(layer,idx,kind)
        pose=self._pose if layer=='near' else 0
        src=self._poses[pose][layer][idx]
        if kind=='image':
            key=(pose,layer,idx,self._night_level)
            if key not in self._night_tiles:
                if self._night_level==0 and _QA_SHARE_DAYLIGHT:
                    # Daylight: multiplicar por (255,255,255,255) e
                    # restaurar pixels LAMP ja identicos seria uma copia
                    # redundante por distrito visivel. Fonte imutavel.
                    dest=src
                else:
                    dest=src.copy()
                    tint=tuple(round(255*(1-c*self._night_level/4)) for c in (.42,.39,.27))+(255,)
                    dest.fill(tint,special_flags=pygame.BLEND_RGBA_MULT)
                    for xy in self._lamp_pixels[id(src)]:dest.set_at(xy,LAMP)
                self._night_tiles[key]=dest
                while len(self._night_tiles)>24:self._night_tiles.popitem(last=False)
            self._night_tiles.move_to_end(key);return self._night_tiles[key]
        key=(pose,layer,idx,'flowmask' if kind=='flow' else kind)
        if key not in self._maps:
            self._prepare_maps(pose,layer,idx,src)
            while len(self._maps)>40:self._maps.popitem(last=False)
        self._maps.move_to_end(key);return self._maps[key]

    def _prepare_maps(self,pose,layer,index,src):
        super()._prepare_maps(pose,layer,index,src)
        if self.biome!='deserto' or layer!='mid' or index%8!=2:return
        rgb=pygame.surfarray.array3d(src)
        color=(np.array(WATER)*.85+np.array((224,173,132))*.15).astype('uint8')
        water=np.all(rgb==color,axis=2)
        for kind,value in (('material',(105,250,105)),('fxmask',(90,0,0)),('flowmask',(90,0,0))):
            arr=pygame.surfarray.pixels3d(self._maps[(pose,layer,index,kind)]);arr[water]=value;del arr

    def _draw_layer(self,dst,layer,travel,kind):
        if self.biome!='deserto':return super()._draw_layer(dst,layer,travel,kind)
        offset=max(0.,travel)*DEPTH[layer][0]*.5;first=int(offset//LW);shift=int(offset%LW)
        # Different coprime lengths/strides prevent the old four-tile refrain.
        count=COUNTS[layer];stride={'far':5,'mid':7,'near':9}[layer]
        for j in range(2):dst.blit(self._tile_map(layer,((first+j)*stride)%count,kind),(j*LW-shift,0))
