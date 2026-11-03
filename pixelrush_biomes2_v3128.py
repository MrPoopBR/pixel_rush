"""Art-directed modular biomes. All material work is done during loading."""
import math
import os
import numpy as np
import pygame
from pixelrush_biomes2_v3127 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW,LH,WIDTH,HEIGHT,SUPPORTED_BIOMES
MODULAR_BIOMES=('neve','deserto') if os.getenv('PIXELRUSH_DESERTO_2_0')=='1' else ('neve',)
# QA758: nunca omitir o BLIT do overlay SRCALPHA vazio: no SDL ele
# zera RGB oculto quando alpha=0. Otimizar apenas a limpeza redundante
# da Surface meteorologica, sem adicionar RAM nem mudar pixels.
_QA_SKIP_INERT_WEATHER=os.environ.get('PIXELRUSH_QA_MODULAR_WEATHER_SKIP','1')=='1'
# Nivel 0 nao multiplica cor nem altera emissao: e a Surface original.
_QA_SHARE_DAYLIGHT=os.environ.get('PIXELRUSH_QA_SHARE_DAYLIGHT','1')=='1'
# speed, atmospheric mix, ground anchor, decoration ceiling/floor
DEPTH={'far':(.10,.34,200,(70,227)), 'mid':(.25,.15,204,(80,229)), 'near':(.52,0.,230,(110,231))}

class ModularBiomeScene(Previous):
    def __init__(self,biome):
        self._pose=0
        super().__init__(biome)
        self._poses=[self._layers]
        if biome=='deserto':
            for pose in (1,2):
                self._pose=pose
                self._poses.append({layer: [self._make_chunk(layer,i) for i in range(4)] if layer=='near' else self._layers[layer] for layer in DEPTH})
        self._pose=0
        self._maps={};self._night_tiles={}
        for pose,layers in enumerate(self._poses):
            for layer,tiles in layers.items():
                for i,src in enumerate(tiles):
                    # Shared far/mid pose data avoids duplicate maps.
                    if pose and layer!='near': continue
                    self._prepare(pose,layer,i,src)
        self._weather=pygame.Surface((LW,LH),pygame.SRCALPHA)

    def _snow_house(self,s,x,base,w,h,seed):
        super()._snow_house(s,x,base,w,h,seed)
        y=base-h
        # Chimney, snow cornice and tapered icicles are attached to each roof.
        pygame.draw.rect(s,(63,70,110),(x+w-13,y-14,6,12))
        pygame.draw.rect(s,(232,247,252),(x+w-15,y-16,10,3))
        for j in range(3):
            xx=x+5+j*(w-10)//3
            pygame.draw.polygon(s,(179,220,242),[(xx,y+5),(xx+3,y+5),(xx+1,y+11+(seed+j)%5)])
        if seed%2:
            pygame.draw.polygon(s,(60,79,116),[(x+4,base-24),(x+w-5,base-24),(x+w-2,base-18),(x+1,base-18)])
            pygame.draw.line(s,(242,249,251),(x+2,base-24),(x+w-4,base-24),2)
        pygame.draw.line(s,(44,59,85),(x,base-1),(x+w-2,base-1),2)

    def _desert_palace(self,s,x,base,w,h,idx):
        super()._desert_palace(s,x,base,w,h,idx)
        top=base-h
        # Recessed portal with stepped voussoirs, cornice and mineral strata.
        cx=x+w//2
        pygame.draw.rect(s,(89,68,74),(cx-6,base-20,12,17))
        pygame.draw.circle(s,(89,68,74),(cx,base-20),6)
        pygame.draw.arc(s,(245,197,132),(cx-9,base-29,18,18),0,math.pi,3)
        for xx in (cx-9,cx+7):pygame.draw.rect(s,(234,178,117),(xx,base-20,2,17))
        for yy in range(top+15,base-27,13):
            pygame.draw.line(s,(185,124,94),(x+2,yy),(x+w-4,yy+2))
        if idx%3==0:
            pygame.draw.polygon(s,(94,132,129),[(x+6,top+26),(x+w-8,top+26),(x+w-4,top+33),(x+3,top+33)])
            pygame.draw.line(s,(191,198,152),(x+5,top+27),(x+w-7,top+27))
        pygame.draw.line(s,(109,76,69),(x,base-1),(x+w-2,base-1),2)

    def _palm(self,s,x,ground,size,idx):
        # Anchored trunk; only frond tips sway, never the root or hitboxes.
        tip=(x+3,ground-size);sway=(0,2,-1)[self._pose]
        pygame.draw.line(s,(92,66,51),(x,ground),tip,4)
        pygame.draw.line(s,(186,132,81),(x+1,ground),tip,1)
        for yy in range(ground-size+8,ground,6):pygame.draw.line(s,(65,54,47),(x-1,yy),(x+3,yy-2))
        for sign,dy in ((-1,-4),(1,-5),(-1,5),(1,7)):
            end=(x+sign*int(size*.56)+sway,tip[1]+dy+8)
            elbow=(x+sign*int(size*.33),tip[1]+dy)
            pygame.draw.polygon(s,(52,100,69),[tip,elbow,end,(elbow[0],elbow[1]+4)])
            pygame.draw.lines(s,(126,168,91),False,[tip,elbow,end],1)

    def _make_chunk(self,layer,index):
        s=super()._make_chunk(layer,index)
        if layer=='near':
            # Alternating plazas reveal deeper architecture; all roots stay at 230.
            s.fill((0,0,0,0))
            cold=self.biome=='neve'
            pygame.draw.rect(s,(84,95,128) if cold else (204,141,107),(0,224,LW,10))
            layouts=((( -8,48),(48,42),(132,45),(190,44)),
                     ((-6,39),(43,51),(105,40),(188,44)),
                     ((-5,53),(82,43),(132,50),(193,40)),
                     ((-8,46),(49,40),(102,48),(184,49)))
            for j,(x,w) in enumerate(layouts[index]):
                h=50+(index*13+j*17)%35
                if cold:self._snow_house(s,x,228,w,h,index*7+j)
                else:self._desert_palace(s,x,229,w,h,index*7+j)
            gap=(110,164,64,164)[index]
            if cold:self._pine(s,gap,230,24,True)
            else:self._palm(s,gap,230,38,index)
            self._lamp(s,18,230,cold)
            pygame.draw.rect(s,(128,139,155) if cold else (198,138,102),(0,228,LW,5))
            pygame.draw.line(s,(225,242,252) if cold else (255,199,129),(0,228),(LW,228),2)
            pygame.draw.rect(s,(72,88,108) if cold else (132,93,83),(0,233,LW,17))
            for x in range(8,LW,27):pygame.draw.line(s,(99,121,139) if cold else (164,114,93),(x,244),(x+11,244))
        if self.biome=='deserto' and layer=='far':
            # Smooth periodic dune crests share the same height at chunk edges.
            for base,amp,col in ((183,9,(226,174,116)),(201,7,(238,189,126))):
                pts=[(x,base-round(amp*math.sin(x/LW*math.tau)**2)) for x in range(LW+1)]
                pygame.draw.polygon(s,col,pts+[(LW,227),(0,227)])
                pygame.draw.lines(s,(249,205,145),False,pts,1)
        if layer=='near' and self.biome=='neve':
            # Short subdued ice reflections live below the sidewalk.
            for x in range(10,LW,43):
                pygame.draw.line(s,(111,143,166),(x,237),(x+13,237))
                pygame.draw.line(s,(91,117,143),(x+3,239),(x+19,239))
        haze=DEPTH[layer][1]
        if haze:
            rgb=pygame.surfarray.pixels3d(s)
            fog=np.array((150,177,209) if self.biome=='neve' else (223,172,130))
            rgb[:]=np.clip(rgb*(1-haze)+fog*haze,0,255).astype('uint8');del rgb
        return s

    def _prepare(self,pose,layer,index,src):
        rgb=pygame.surfarray.array3d(src).astype(np.float32)
        alpha=pygame.surfarray.array_alpha(src)
        warm=(rgb[:,:,0]>225)&(rgb[:,:,1]>185)&(rgb[:,:,2]<195)&(alpha>90)
        if self.biome!='neve' or layer=='far':warm[:]=False
        # Quantized night palettes are prebuilt, so scrolling never allocates tiles.
        for level in range(5):
            if level==0 and _QA_SHARE_DAYLIGHT:
                # Nao duplicar 225x250 RGBA para o dia: fator RGB 1.0;
                # lampadas quentes ja possuem a cor exata na fonte.
                # O atlas base e imutavel durante draw(). Sem alteracao RNG.
                self._night_tiles[(pose,layer,index,level)]=src
                continue
            dest=src.copy();arr=pygame.surfarray.pixels3d(dest)
            factor=1-np.array((.42,.39,.27))*level/4
            arr[:]=rgb*factor;arr[warm]=rgb[warm];del arr
            self._night_tiles[(pose,layer,index,level)]=dest

    def _prepare_maps(self,pose,layer,index,src):
        rgb=pygame.surfarray.array3d(src).astype(np.float32)
        alpha=pygame.surfarray.array_alpha(src)
        opaque=alpha>90
        warm=(rgb[:,:,0]>225)&(rgb[:,:,1]>185)&(rgb[:,:,2]<195)&opaque
        # Only real warm windows/lanterns emit. Desert stone never emits.
        if self.biome!='neve' or layer=='far':warm[:]=False
        ice=(rgb[:,:,2]>rgb[:,:,0]+12)&(rgb[:,:,1]>150)&opaque
        lum=rgb.mean(axis=2)/255
        gx,gy=np.gradient(lum)
        normal=np.stack((-gx*.45,-gy*.45,np.ones_like(gx)),axis=2)
        normal/=np.linalg.norm(normal,axis=2,keepdims=True)
        mat=np.empty_like(rgb);mat[:]=(226,240,22)
        mat[ice]=(145,245,85)
        # Contact occlusion at downward color/alpha boundaries, not a global glow.
        below=np.zeros_like(opaque);below[:,:-1]=opaque[:,1:]
        mat[opaque & ~below,1]=175
        for kind in ('normal','material','fxmask','flowmask','geometry'):
            dest=pygame.Surface((LW,LH),pygame.SRCALPHA)
            arr=pygame.surfarray.pixels3d(dest)
            if kind=='normal':arr[:]=np.clip((normal+1)*127.5,0,255)
            elif kind=='material':arr[:]=mat
            elif kind=='geometry':arr[:]=(int(DEPTH[layer][0]*255),210,0)
            elif kind=='fxmask':arr[:]=0;arr[warm]=(0,0,160)
            elif kind=='emission':arr[:]=rgb
            else:arr[:]=0
            del arr
            a=pygame.surfarray.pixels_alpha(dest)
            a[:]=np.where(warm,alpha,0) if kind=='emission' else alpha;del a
            self._maps[(pose,layer,index,kind)]=dest

    def _tile_map(self,layer,idx,kind):
        pose=self._pose if layer=='near' else 0
        if kind=='image':return self._night_tiles[(pose,layer,idx,self._night_level)]
        key=(pose,layer,idx,'flowmask' if kind=='flow' else kind)
        if key not in self._maps:self._prepare_maps(pose,layer,idx,self._poses[pose][layer][idx])
        return self._maps[key]

    def _draw_layer(self,dst,layer,travel,kind):
        offset=max(0.,travel)*DEPTH[layer][0]*.5
        first=int(offset//LW);shift=int(offset%LW)
        # Quando a tela tem 225 px e shift e zero, tile j=1 comeca
        # exatamente fora da Surface: omitir consulta/criacao e blit
        # preserva a imagem integral, incluindo alpha e RGB oculto.
        dst.blit(self._tile_map(layer,first%4,kind),(-shift,0))
        if shift:
            dst.blit(self._tile_map(layer,(first+1)%4,kind),(LW-shift,0))

    def render_scene(self,target,travel,frame,night,climate,phase,foreground_only=False,map_kind='image'):
        if foreground_only:return
        self._pose=(frame//18)%len(self._poses) if self.visual_quality else 0
        self._night_level=round(max(0,min(1,night))*4)
        low=self._composites.get(map_kind)
        if low is None:
            low=pygame.Surface((LW,LH),pygame.SRCALPHA);self._composites[map_kind]=low
        low.fill((128,128,255,255) if map_kind=='normal' else (0,0,0,0))
        for layer in DEPTH:self._draw_layer(low,layer,travel,map_kind)
        if map_kind=='image':
            # O SDL altera RGB oculto (alpha=0) ao blitar uma
            # Surface vazia. Pular o blit do overlay nao e byte-exato.
            # Quando nao ha clima e o buffer JA esta limpo, omitir somente
            # o fill redundante; manter o blit e todos os bytes RGBA.
            neve_ativa=self.biome=='neve' and climate in ('neve','nevasca')
            areia_ativa=self.biome=='deserto' and climate in ('areia','tempestade_areia')
            if (not _QA_SKIP_INERT_WEATHER or neve_ativa or areia_ativa or
                    not getattr(self,'_qa_weather_overlay_clean',False)):
                self._weather.fill((0,0,0,0))
            self._qa_weather_overlay_clean=not (neve_ativa or areia_ativa)
            if neve_ativa:
                for i in range(18 if self.visual_quality else 6):
                    x=int((i*47+frame*.5)%LW);y=int((i*31+frame*.55)%LH)
                    pygame.draw.circle(self._weather,(237,246,255,150),(x,y),1)
            elif areia_ativa:
                for i in range(12 if self.visual_quality else 4):
                    x=int((i*41-frame*1.7)%LW);y=70+int((i*29+frame*.5)%140)
                    pygame.draw.line(self._weather,(235,186,125,110),(x,y),(x+5,y))
            low.blit(self._weather,(0,0))
        pygame.transform.scale(low,(WIDTH,HEIGHT),target)
        if map_kind=='geometry':
            # QA752: alias somente da Surface geometry pertencente ao
            # compositor World; demais chamadas preservam snapshot.
            if getattr(self,'_qa_geometry_borrow_target',None) is target:
                self._geometry_view=target
                self._qa_geometry_borrowed_surface=target
            else:
                # QA750: copia somente na primeira passagem. Nos quadros
                # seguintes faz escrita exata 1:1 sem alpha-blend anterior.
                if (self._geometry_view is None or
                        self._geometry_view is target or
                        self._geometry_view is getattr(self,'_qa_geometry_borrowed_surface',None) or
                        self._geometry_view.get_size()!=target.get_size() or
                        self._geometry_view.get_bitsize()!=target.get_bitsize() or
                        self._geometry_view.get_masks()!=target.get_masks() or
                        bool(self._geometry_view.get_flags() & pygame.SRCALPHA)!=
                        bool(target.get_flags() & pygame.SRCALPHA)):
                    self._geometry_view=target.copy()
                    self._qa_geometry_borrowed_surface=None
                else:
                    pygame.transform.scale(target,target.get_size(),self._geometry_view)
        self._last_state=(travel,frame,night,climate,phase)
