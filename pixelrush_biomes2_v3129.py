"""Desert art pass: authored districts, animated props, existing CPU/GPU contracts.
Snow inherits the approved v3.128 artwork unchanged. Desert remains opt-in.
"""
import os
import math
import pygame
import numpy as np
from pixelrush_biomes2_v3128 import ModularBiomeScene as Previous,DEPTH
from pixelrush_biomes2_v3126 import LW,LH,WIDTH,HEIGHT,SUPPORTED_BIOMES
MODULAR_BIOMES=('neve','deserto') if os.getenv('PIXELRUSH_DESERTO_2_0')=='1' else ('neve',)
DISTRICTS=('Mercado das Dunas','Ruinas do Sol','Oasis das Palmeiras','Portao de Arenito')
LAMP=(255,207,123)
WATER=(53,133,145)

class ModularBiomeScene(Previous):
    def _arch(self,s,x,base,w,h):
        top=base-h;cx=x+w//2
        pygame.draw.rect(s,(111,75,72),(x,top,w,h))
        pygame.draw.rect(s,(208,147,98),(x+2,top+2,w-4,h-2))
        pygame.draw.rect(s,(98,75,78),(x+7,top+h//2,w-14,h//2))
        pygame.draw.ellipse(s,(98,75,78),(x+7,top+10,w-14,h-10))
        pygame.draw.rect(s,(98,75,78),(x+7,top+h//2,w-14,h//2))
        pygame.draw.arc(s,(248,200,137),(x+4,top+6,w-8,h-10),0,math.pi,3)
        for xx in (x+3,x+w-6):pygame.draw.rect(s,(237,183,120),(xx,top+h//2,3,h//2))
        for yy in range(top+7,base,9):
            pygame.draw.line(s,(160,107,83),(x,yy),(x+5,yy))
            pygame.draw.line(s,(160,107,83),(x+w-5,yy),(x+w-1,yy))
        pygame.draw.rect(s,(251,205,142),(x-2,top-2,w+4,4))

    def _lantern(self,s,x,y):
        pygame.draw.line(s,(61,57,59),(x,y-7),(x,y),1)
        pygame.draw.rect(s,(70,60,57),(x-3,y,7,8))
        pygame.draw.rect(s,LAMP,(x-2,y+2,5,4))
        pygame.draw.rect(s,(223,150,81),(x-1,y+3,2,2))

    def _market(self,s,x,base,w,idx):
        top=base-26
        for xx in (x+2,x+w-3):pygame.draw.line(s,(104,70,54),(xx,top),(xx,base),2)
        sway=(0,1,-1)[self._pose]
        pygame.draw.polygon(s,(64,106,112),[(x,top),(x+w,top),(x+w+3,top+8+sway),(x-3,top+8+sway)])
        for xx in range(x,w+x,7):pygame.draw.polygon(s,(187,190,139),[(xx,top+1),(xx+3,top+1),(xx+4,top+8+sway),(xx,top+8+sway)])
        pygame.draw.rect(s,(121,77,57),(x+1,base-8,w-2,8))
        pygame.draw.line(s,(230,175,104),(x+1,base-9),(x+w-1,base-9),2)
        for xx in range(x+5,x+w-3,7):
            pygame.draw.ellipse(s,(211,119,67),(xx,base-14,5,6))
            pygame.draw.line(s,(249,184,96),(xx+1,base-13),(xx+2,base-13))
        self._lantern(s,x+w-5,top+9)

    def _pot(self,s,x,base):
        pygame.draw.polygon(s,(137,78,63),[(x-3,base-9),(x+3,base-9),(x+5,base-5),(x+3,base),(x-3,base),(x-5,base-5)])
        pygame.draw.line(s,(238,164,105),(x-3,base-7),(x-3,base-3))
        pygame.draw.line(s,(71,99,66),(x,base-9),(x+1,base-17),2)
        pygame.draw.lines(s,(100,143,78),False,[(x-4,base-13),(x+1,base-16),(x+5,base-12)],2)

    def _make_chunk(self,layer,index):
        if self.biome!='deserto':return super()._make_chunk(layer,index)
        s=pygame.Surface((LW,LH),pygame.SRCALPHA)
        if layer=='far':
            # Broad low-contrast mesas behind three seamless dune contours.
            for x,h in ((12,45),(83,67),(166,51)):
                pygame.draw.polygon(s,(163,119,111),[(x,179),(x+8,165-h),(x+29,160-h),(x+39,179)])
                pygame.draw.lines(s,(201,151,124),False,[(x+10,164-h),(x+28,162-h),(x+34,174)],2)
                for y in range(172-h,175,11):pygame.draw.line(s,(178,128,110),(x+9,y),(x+28,y+2))
            for base,amp,col in ((163,17,(209,151,103)),(181,15,(229,174,112)),(201,11,(242,194,129))):
                points=[(x,round(base-amp*math.sin(x/LW*math.pi)**2)) for x in range(LW+1)]
                pygame.draw.polygon(s,col,points+[(LW,234),(0,234)])
                pygame.draw.lines(s,(250,209,148),False,points,1)
        elif layer=='mid':
            pygame.draw.rect(s,(185,127,94),(0,206,LW,27))
            if index==0:
                self._desert_palace(s,10,208,55,54,0)
                self._arch(s,86,208,53,67)
                self._desert_palace(s,164,208,56,48,2)
                pygame.draw.line(s,(94,72,65),(58,176),(169,170))
                for x in range(65,165,16):
                    y=176-(x-58)*6//111
                    pygame.draw.polygon(s,(136,79,71) if x%3 else (65,112,118),[(x,y),(x+7,y),(x+4,y+9)])
            elif index==1:
                for x,h in ((12,41),(47,59),(153,46),(195,63)):
                    pygame.draw.rect(s,(159,105,83),(x,208-h,12,h))
                    pygame.draw.rect(s,(232,172,112),(x+2,209-h,4,h-1))
                    pygame.draw.polygon(s,(244,190,126),[(x-3,209-h),(x+2,202-h),(x+8,205-h),(x+15,203-h),(x+14,211-h)])
                    for yy in range(216-h,208,10):pygame.draw.line(s,(126,91,78),(x+1,yy),(x+10,yy))
                self._arch(s,77,209,59,73)
                pygame.draw.polygon(s,(182,122,90),[(36,211),(58,199),(72,211)])
            elif index==2:
                # Water remains entirely behind the sidewalk, never on the lane.
                pygame.draw.ellipse(s,(114,124,91),(25,192,175,24))
                pygame.draw.ellipse(s,WATER,(34,194,157,15))
                for x in range(43,182,19):pygame.draw.line(s,(123,186,177),(x,199+(x%3)),(x+12,199+(x%3)))
                for x,size in ((20,47),(61,62),(171,57),(209,43)):self._palm(s,x,210,size,index)
                self._desert_palace(s,98,193,38,38,index)
            else:
                self._arch(s,68,211,90,91)
                for x in (48,159):
                    self._desert_palace(s,x,211,23,85,x)
                    pygame.draw.polygon(s,(205,141,95),[(x-2,126),(x+11,110),(x+25,126)])
                for x in (12,197):self._cactus(s,x,210,30)
            # Consistent distant ground connection, independent of district.
            pygame.draw.rect(s,(192,134,95),(0,216,LW,17))
        else:
            pygame.draw.rect(s,(196,138,98),(0,221,LW,12))
            if index==0:
                self._desert_palace(s,-7,229,51,70,1)
                self._desert_palace(s,139,229,53,67,3)
                self._market(s,52,229,60,index)
                self._palm(s,211,230,42,index)
                self._pot(s,124,229)
            elif index==1:
                self._desert_palace(s,-12,229,45,58,4)
                self._arch(s,153,229,47,61)
                for x in (48,114,213):self._pot(s,x,230)
                pygame.draw.polygon(s,(170,114,85),[(66,229),(72,215),(83,211),(94,224),(104,229)])
                pygame.draw.lines(s,(239,180,119),False,[(69,224),(77,214),(84,215)],2)
            elif index==2:
                self._desert_palace(s,-13,229,45,57,1)
                self._palm(s,49,230,51,index)
                self._market(s,125,229,42,index)
                self._palm(s,202,230,56,index)
                self._pot(s,91,229)
            else:
                self._desert_palace(s,-6,229,52,63,3)
                self._market(s,59,229,43,index)
                self._desert_palace(s,173,229,52,60,2)
                self._palm(s,138,230,40,index)
            # Real facade lanterns: reserved pigment permits exact emission masks.
            for x in ((14,184),(14,196),(14,145),(14,190))[index]:self._lantern(s,x,207)
            pygame.draw.line(s,(250,198,128),(0,228),(LW,228),2)
            pygame.draw.rect(s,(185,123,88),(0,230,LW,4))
            pygame.draw.rect(s,(124,87,73),(0,234,LW,16))
            for x in range(5,LW,21):
                pygame.draw.line(s,(161,109,81),(x,240),(x+7,240))
                pygame.draw.line(s,(143,97,77),(x+4,247),(x+11,247))
        # Distance grades are baked, preserving the exact lantern pigment.
        haze=DEPTH[layer][1]
        if haze:
            arr=pygame.surfarray.pixels3d(s)
            arr[:]=arr*(1-haze)+np.array((224,173,132))*haze;del arr
        return s

    def _prepare(self,pose,layer,index,src):
        super()._prepare(pose,layer,index,src)
        if self.biome!='deserto':return
        rgb=pygame.surfarray.array3d(src)
        lit=np.all(rgb==LAMP,axis=2)
        for level in range(5):
            arr=pygame.surfarray.pixels3d(self._night_tiles[(pose,layer,index,level)])
            arr[lit]=LAMP;del arr

    def _prepare_maps(self,pose,layer,index,src):
        super()._prepare_maps(pose,layer,index,src)
        if self.biome!='deserto':return
        rgb=pygame.surfarray.array3d(src).astype('int16')
        alpha=pygame.surfarray.array_alpha(src)>90
        lit=np.all(rgb==LAMP,axis=2)&alpha
        # Oasis pigment has atmospheric grading in the mid layer.
        haze=DEPTH[layer][1]
        water_color=(np.array(WATER)*(1-haze)+np.array((224,173,132))*haze).astype('int16')
        water=np.all(rgb==water_color,axis=2)&alpha if layer=='mid' and index==2 else np.zeros_like(alpha)
        green=(rgb[:,:,1]>rgb[:,:,0]+8)&(rgb[:,:,1]>rgb[:,:,2]+8)&alpha
        mat=pygame.surfarray.pixels3d(self._maps[(pose,layer,index,'material')])
        mat[:,:,0]=230;mat[:,:,2]=18;mat[water]=(105,250,105);mat[green]=(242,240,12)
        mat[lit]=(220,255,12);del mat
        fx=pygame.surfarray.pixels3d(self._maps[(pose,layer,index,'fxmask')])
        fx[:]=0;fx[lit]=(0,0,155);fx[water]=(90,0,0);del fx
        flow=pygame.surfarray.pixels3d(self._maps[(pose,layer,index,'flowmask')])
        flow[:]=0;flow[water]=(90,0,0);flow[green]=(0,45,0);del flow
