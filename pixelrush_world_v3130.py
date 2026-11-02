"""Pixel Rush v3.126.0 — camadas coesas das 7 artes aprovadas.

Pano de fundo inteiro com costura por espelhamento e alpha graduado no céu;
sem a colagem de recortes aleatórios de v3.104.0. Props usam recortes reais
com transparência e mapas técnicos separados para efeitos GPU ModernGL.
"""
import math
import json
import os
from collections import OrderedDict
import pygame
from pixelrush_renderfx_v3125 import AtmosphereFlow, WorldDebris
from pixelrush_art_guard_v3111 import verificar_arte
from pixelrush_parallax_ia_v3114 import ParallaxIA
from pixelrush_chunks_v3113 import CHUNK_MIRRORS, CHUNK_OVERLAP
from pixelrush_profissional_v3108 import ArticulacaoFABRIK, SDFDestrutivel, OclusaoAcustica2D
from pixelrush_city2_v3125 import CityPilotScene
from pixelrush_biomes2_v3130 import ModularBiomeScene, MODULAR_BIOMES
if os.environ.get('PIXELRUSH_CENARIOS_CLASSICOS') == '1':
    from pixelrush_biomes2_v3127 import ModularBiomeScene, MODULAR_BIOMES
WIDTH, HEIGHT, TOP, GROUND=450,800,230,730
DIR=os.path.join(os.path.dirname(__file__),'world_art_v3106')
BIOMES=('cidade','neve','deserto','vulcao','floresta','cidade_futurista','ilhas_celestes')
LAYER_SPEEDS=(.108,.235,.465,.86)
PROPS={
'cidade':((0,230,140,215,'sway'),(755,224,140,214,'sway')),
'neve':((0,120,105,330,'sway'),(796,120,104,330,'sway')),
'deserto':((0,295,140,175,'sway'),(765,297,130,175,'sway')),
'vulcao':((78,74,110,185,'smoke'),(719,77,115,190,'smoke')),
'floresta':((2,15,190,435,'sway'),(708,13,187,435,'sway')),
'cidade_futurista':((1,50,125,260,'flicker'),(770,50,125,260,'flicker')),
'ilhas_celestes':((0,15,178,418,'sway'),(724,10,175,418,'sway')),
}
COLORS={'cidade':(244,187,112),'neve':(255,216,173),'deserto':(255,201,121),
'vulcao':(255,128,68),'floresta':(136,234,153),'cidade_futurista':(89,222,253),
'ilhas_celestes':(146,243,215)}
_SOURCE={}
_ATLAS=None
_ATLAS_INDEX=None

def _atlas_prop(biome,index):
    global _ATLAS,_ATLAS_INDEX
    if _ATLAS is None:
        _ATLAS=pygame.image.load(os.path.join(DIR,'props_atlas.png')).convert_alpha()
        with open(os.path.join(DIR,'props_atlas.json'),'r',encoding='utf-8') as f:
            _ATLAS_INDEX=json.load(f)['sprites']
    frame=_ATLAS_INDEX['{}_{}.png'.format(biome,index)]
    return _ATLAS.subsurface(pygame.Rect(frame['x'],frame['y'],frame['w'],frame['h'])).copy()

def _source(b):
    if b not in _SOURCE:
        path=os.path.join(DIR,b+'.png')
        verificar_arte(path,b)
        _SOURCE[b]=pygame.image.load(path).convert_alpha()
    return _SOURCE[b]

PIPE_OVERLAP=CHUNK_OVERLAP
PIPE_FLIPS=CHUNK_MIRRORS

def _loop_strip(src,feather=False,normal=False):
    """Chunks modulares 12x a partir da arte preservada.

    Emendas por crossfade de 48px. O conjunto é repetido, não se afirma
    geração infinita de arte única. Todos os mapas compartilham o mesmo layout.
    """
    original=src.copy(); w,h=original.get_size()
    if feather:
        fade=pygame.Surface((w,h),pygame.SRCALPHA)
        fade.fill((255,255,255,255))
        for y in range(min(78,h)):
            a=int(255*(y/77.)**1.70)
            pygame.draw.line(fade,(255,255,255,a),(0,y),(w,y))
        original.blit(fade,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
    step=w-PIPE_OVERLAP
    out=pygame.Surface((step*len(PIPE_FLIPS),h),pygame.SRCALPHA)
    for i,flip in enumerate(PIPE_FLIPS):
        tile=pygame.transform.flip(original,True,False) if flip else original
        if normal and flip:
            # Corrige componente X das normais ao espelhar geometria.
            tile=tile.copy()
            rgb=pygame.surfarray.pixels3d(tile)
            rgb[:,:,0]=255-rgb[:,:,0]
            del rgb
        x=i*step
        if i:
            prev=out.subsurface(pygame.Rect(x,0,PIPE_OVERLAP,h)).copy()
            # Desenha a parte nova e restaura uma fração da borda anterior.
            out.blit(tile,(x,0))
            for j in range(PIPE_OVERLAP):
                a=int(255*(1.0-j/float(PIPE_OVERLAP)))
                row=prev.subsurface(pygame.Rect(j,0,1,h)).copy()
                row.set_alpha(a)
                out.blit(row,(x+j,0))
        else:
            out.blit(tile,(x,0))
    # Costura do fim para o primeiro chunk do mesmo ciclo.
    last=out.subsurface(pygame.Rect(out.get_width()-PIPE_OVERLAP,0,PIPE_OVERLAP,h)).copy()
    first=out.subsurface(pygame.Rect(0,0,PIPE_OVERLAP,h)).copy()
    for j in range(PIPE_OVERLAP):
        srcrow=first.subsurface(pygame.Rect(j,0,1,h)).copy()
        srcrow.set_alpha(int(255*(j/float(PIPE_OVERLAP))))
        out.blit(srcrow,(out.get_width()-PIPE_OVERLAP+j,0))
    return out

class LivingWorld:
    def __init__(self,biome='cidade',lightweight=False):
        self.biome=biome if biome in BIOMES else 'cidade'
        self.lightweight=bool(lightweight)
        self.parallax_ia=ParallaxIA(lightweight=self.lightweight)
        self.frame=0;self.travel=0.0;self.night=0.0;self.phase=.5;self.climate='limpo'
        self.cache=OrderedDict();self.fx_cache=OrderedDict();self.normal_cache=OrderedDict();self.material_cache=OrderedDict();self.flow_cache=OrderedDict();self.geometry_cache=OrderedDict();self.props_cache={}
        self.debris=WorldDebris();self.atmosphere=AtmosphereFlow()
        self.events=set();self.cables={};self.springs={}
        self.rigs={};self.damage=SDFDestrutivel();self.acoustics=OclusaoAcustica2D()
        self._transition=None;self._transition_frames=0
        self._bg_wind=0.0
        self.city2=CityPilotScene() if self.biome=='cidade' else None
        self.modular={}
        self._city_surfaces={}

    def _scroll(self):return int(self.travel*LAYER_SPEEDS[1])
    def _load(self,kind):
        cache={'image':self.cache,'fxmask':self.fx_cache,'normal':self.normal_cache,
               'material':self.material_cache,'flowmask':self.flow_cache,'geometry':self.geometry_cache}[kind]
        key=self.biome
        if key in cache:
            if kind=='image':cache.move_to_end(key)
            return cache[key]
        if kind=='image':
            data=_loop_strip(self.parallax_ia.source(key) or _source(key),True)
        else:
            path=os.path.join(DIR,key+'_'+kind+'.png')
            data=_loop_strip(pygame.image.load(path).convert_alpha(),feather=kind=='fxmask',normal=kind=='normal') if os.path.isfile(path) else None
        cache[key]=data
        while len(cache)>2:cache.popitem(last=False)
        return data
    def _blit_strip(self,target,strip):
        if strip is None:return
        off=self._scroll()%strip.get_width()
        x=-off
        while x<WIDTH:
            target.blit(strip,(x,TOP));x+=strip.get_width()

    def _get_modular(self):
        """Cria a arte uma vez por bioma. Nao ativa outras modificacoes."""
        scene=self.modular.get(self.biome)
        if scene is None:
            scene=ModularBiomeScene(self.biome)
            self.modular[self.biome]=scene
            # limite de memoria em celulares: libera o outro bioma modular.
            if len(self.modular)>1:
                for key in list(self.modular):
                    if key!=self.biome:
                        self.modular.pop(key,None)
            # As surfaces sao limpas no switch; nao descartar o buffer
            # acabado de criar durante a primeira chamada a _city_surface.
        scene.visual_quality=0 if self.lightweight else 1
        return scene

    def _city_surface(self, kind='image', foreground_only=False):
        # Reutiliza as superfícies e evita ~900KB de alocação por camada/quadro.
        cache_key=(kind,bool(foreground_only))
        surf=self._city_surfaces.get(cache_key)
        if surf is None:
            surf=pygame.Surface((WIDTH,GROUND-TOP),pygame.SRCALPHA)
            self._city_surfaces[cache_key]=surf
        if kind=='normal':
            surf.fill((128,128,255))
        elif kind=='flow':
            surf.fill((128,128,0))
        else:
            surf.fill((0,0,0,0))
        if self.biome in MODULAR_BIOMES:
            self._get_modular().render_scene(surf,self.travel,self.frame,self.night,self.climate,self.phase,foreground_only=foreground_only,map_kind=kind)
        else:
            self.city2.render_scene(surf,self.travel,self.frame,self.night,self.climate,self.phase,foreground_only=foreground_only,map_kind=kind)
        return surf

    def update(self,speed,night=0,climate='limpo',phase=.5):
        self.travel+=max(0.,float(speed));self.frame+=1
        self.night=max(0.,min(1.,float(night)))
        self.phase=max(0.,min(1.,float(phase)))
        self.climate=climate
        if self.biome=='cidade':self.city2.tick_life(self.frame,self.travel,self.climate)
        storm=climate in ('tempestade','nevasca','tempestade_areia','vento','vento_neon','vento_folhas','tempestade_vento')
        self._bg_wind+=.021+(.04 if storm else 0)
        self.debris.tick(speed)
        if self.frame%3==0:self.atmosphere.update(self.frame,self.biome,climate,speed)
        if self._transition_frames:
            self._transition_frames-=1
            if not self._transition_frames:self._transition=None
        for key,(pos,v,ttl) in tuple(self.springs.items()):
            v=(v-.085*pos)*.88;pos+=v;ttl-=1
            if ttl<=0 or abs(pos)+abs(v)<.02:self.springs.pop(key,None)
            else:self.springs[key]=(pos,v,ttl)

    def switch(self,biome):
        if biome not in BIOMES:biome='cidade'
        if biome==self.biome:return
        previous=None
        if self.frame>5:
            try:
                previous=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
                self.draw(previous)
            except (pygame.error,MemoryError):pass
        self.biome=biome;self.travel=0.;self.frame=0
        self._city_surfaces.clear()
        self.events.clear();self.springs.clear();self.cables.clear();self.rigs.clear();self.damage=SDFDestrutivel()
        self.debris=WorldDebris();self.atmosphere=AtmosphereFlow()
        if biome=='cidade' and self.city2 is None:self.city2=CityPilotScene()
        self._transition=previous;self._transition_frames=38 if previous is not None else 0

    def ambient_x(self):return int((210-self.travel*LAYER_SPEEDS[2])%(WIDTH+95))

    def ambient_occlusion(self, source_x, listener_x=90, source_y=490, listener_y=652):
        """Raycast leve no mapa geométrico que acompanha os chunks."""
        if self.biome in MODULAR_BIOMES:
            return self._get_modular().ambient_occlusion(source_x, listener_x, source_y, listener_y)
        if self.biome=='cidade':
            return self.city2.ambient_occlusion(source_x, listener_x, source_y, listener_y)
        geometry=self._load('geometry')
        if geometry is None:return 0.0
        off=self._scroll()%geometry.get_width()
        y0=max(0,source_y-TOP);y1=max(0,listener_y-TOP)
        blocked=0.;steps=20
        for n in range(1,steps):
            ratio=n/float(steps)
            x=int((listener_x+(source_x-listener_x)*ratio+off)%geometry.get_width())
            y=int(min(geometry.get_height()-1,y1+(y0-y1)*ratio))
            val=geometry.get_at((x,y)).g/255.
            blocked+=max(0.,val-.40)
        return min(.9,blocked/(steps-1)*1.7)

    def register_landing(self,player_x,intensity=1.0):
        """Preserva a API da v3.103 para pousos/poeira e marcas por chunk."""
        world_x=self.travel*LAYER_SPEEDS[1]+float(player_x)
        chunk=math.floor(world_x/360.0)
        local=world_x-chunk*360.0
        self.debris.emit(chunk,local,self.biome,'pouso',5 if self.lightweight else 9)
        # v3.125.0: sem entalhe SDF/pegadas permanentes no chao ao pousar.
        self.atmosphere.excite(player_x,float(intensity))
        if self.biome=='cidade':self.city2.react_to_player(intensity)

    @staticmethod
    def _deform_sprite_2bones(sprite, tip_dx, mid_dx):
        """Malha vertical de 2 ossos visuais: base presa, topo flexível.

        A interpolação dos deslocamentos acompanha o vento/mola e conserva
        o desenho original. É um rig procedural 2D, NÃO Spine/IK completo.
        """
        width,height=sprite.get_size()
        if abs(tip_dx)<.3 and abs(mid_dx)<.3:
            return sprite, 0
        margem=max(4,int(max(abs(tip_dx),abs(mid_dx)))+3)
        out=pygame.Surface((width+margem*2,height),pygame.SRCALPHA)
        tira=4 if height<300 else 6
        for y in range(0,height,tira):
            k=min(1.0,(y+tira*.5)/max(1.0,height))
            if k<.5:
                u=k*2.
                offset=(1.-u)*tip_dx+u*mid_dx
            else:
                u=(k-.5)*2.
                offset=(1.-u)*mid_dx
            out.blit(sprite,(margem+int(round(offset)),y),pygame.Rect(0,y,width,min(tira,height-y)))
        return out,margem

    def _animated_props(self,surface):
        # Recortes feathered gerados off-line, fixados exatamente na geometria da arte.
        w=_source(self.biome).get_width()
        scroll=self._scroll()%(2*w)
        storm=self.climate in ('vento','tempestade','nevasca','vento_folhas','tempestade_areia')
        for i,(sx,sy,sw,sh,kind) in enumerate(PROPS[self.biome]):
            key=(self.biome,i)
            if key not in self.props_cache:
                self.props_cache[key]=_atlas_prop(self.biome,i)
            piece=self.props_cache[key]
            for location,mirror in ((sx,False),(w*2-sx-sw,True)):
                x=(location-scroll)%(w*2)
                if x>WIDTH+sw:x-=2*w
                if x<-sw or x>WIDTH:continue
                dx=dy=0
                if kind=='sway':
                    dx=int(math.sin(self._bg_wind+i*1.3)* (4 if storm else 2))
                    sk=(self.biome,i,mirror)
                    if 70<x+sw//2<150 and sk not in self.springs:self.springs[sk]=(0.,2.2,70)
                    dx+=int(self.springs.get(sk,(0.,0.,0))[0])
                elif kind=='smoke':
                    dx=int(math.sin(self._bg_wind+i)*3)
                    dy=-int((self.frame*.26+i*7)%8)
                if mirror:
                    # QA v3.277.32: espelhamento de props estaticos em cache.
                    # Mesma Surface que transform.flip produziria a cada desenho;
                    # invalidacao por identidade evita usar arte anterior.
                    cache_mirror = getattr(self, '_qa_mirror_props', None)
                    if cache_mirror is None:
                        cache_mirror = {}
                        self._qa_mirror_props = cache_mirror
                    stored = cache_mirror.get(key)
                    if stored is not None and stored[0] is piece:
                        pp = stored[1]
                    else:
                        pp = pygame.transform.flip(piece, True, False)
                        if len(cache_mirror) >= 64:
                            cache_mirror.clear()
                        cache_mirror[key] = (piece, pp)
                else:
                    pp = piece
                left_shift=0
                if kind=='sway':
                    # FABRIK real (3 segmentos) com raiz fixa, vento e turbulência.
                    rig_key=(self.biome,i,mirror)
                    rig=self.rigs.get(rig_key)
                    if rig is None:
                        rig=ArticulacaoFABRIK(pp.get_height(),seed=i+int(mirror)*17)
                        self.rigs[rig_key]=rig
                    wake=1.0 if 65 < x+sw//2 < 160 else 0.0
                    rig.update(self.frame,wind=(-1 if mirror else 1)*(1.1 if storm else .3),wake=wake)
                    pp,left_shift=rig.deform(pp)
                    dx=0
                if kind=='flicker':
                    pp=pp.copy();pp.set_alpha(int(174+77*abs(math.sin(self.frame*.08+i)))*max(.5,self.night))
                surface.blit(pp,(int(x)+dx-left_shift,TOP+sy+dy))

    def _lights(self,surface):
        if self.night<.10 and self.biome not in ('cidade_futurista','ilhas_celestes','vulcao'):return
        color=COLORS[self.biome]
        for n in range(4):
            x=int((95+n*185-self._scroll())%(1800))
            if x>WIDTH+15:continue
            y=380+n%3*65
            # halo muito discreto, sem bolhas/brancos sobre o cenário
            g=pygame.Surface((42,42),pygame.SRCALPHA)
            for r in (19,15,10,6):
                a=int((20-r)*.55*(.35+self.night))
                pygame.draw.circle(g,(*color,max(0,a)),(21,21),r)
            surface.blit(g,(x-21,y-21))

    def _weather(self,surface):
        kind=self.climate;f=self.frame
        if kind in ('chuva','tempestade','chuva_acida'):
            for i in range(48 if kind=='tempestade' else 26):
                x=int((i*103-f*(5.2 if kind=='tempestade' else 2.9))%(WIDTH+80))-30
                y=TOP+int((i*71+f*7.7)%(GROUND-TOP))
                pygame.draw.line(surface,(153,206,240,106),(x,y),(x-4,y+12),1)
        elif kind in ('neve','nevasca'):
            for i in range(42 if kind=='nevasca' else 26):
                x=int((i*61+math.sin(f*.04+i)*11-f*(2 if kind=='nevasca' else .7))%(WIDTH+50))-15
                y=TOP+int((i*73+f*(1.9 if kind=='nevasca' else .75))%(GROUND-TOP))
                pygame.draw.circle(surface,(244,250,255,182),(x,y),1 + int(i%3==0))
        elif kind in ('areia','tempestade_areia'):
            for i in range(36):
                x=int((i*53-f*3.2)%(WIDTH+50))-18;y=310+(i*47)%370
                pygame.draw.line(surface,(233,192,119,88),(x,y),(x+12,y-1),1)
        elif kind in ('cinzas','chuva_meteoros'):
            for i in range(24):
                x=int((i*61-f*.8)%(WIDTH+30))-10;y=TOP+int((i*23+f*.9)%(GROUND-TOP))
                pygame.draw.circle(surface,(155,117,121,115),(x,y),2 if i%7==0 else 1)
        elif kind in ('vento','vento_folhas','polen','brisa_celeste'):
            for i in range(16):
                x=int((i*51-f*1.6)%(WIDTH+35))-15;y=430+i*18%260
                pygame.draw.line(surface,(142,215,147,80),(x,y),(x+8,y+2),1)

    def draw(self,surface):
        if self.biome=='cidade' or self.biome in MODULAR_BIOMES:
            if self.biome=='cidade':self.city2.visual_quality=0 if self.lightweight else 1
            layer=self._city_surface('image', foreground_only=False)
            if self.damage.chunks:
                self.damage.apply(layer,self.travel*LAYER_SPEEDS[1])
            surface.blit(layer,(0,TOP))
            self.debris.draw(surface,self.travel,LAYER_SPEEDS[2])
            if self.climate in ('tempestade','nevasca','tempestade_areia','cinzas'):
                self.atmosphere.draw(surface,self.biome,self.night)
            if self._transition is not None and self._transition_frames:
                old=self._transition.copy();old.set_alpha(int(210*(self._transition_frames/38.)**1.45))
                surface.blit(old,(0,0))
            return
        if self.damage.chunks:
            # Somente cenografia (TOP..GROUND); máscara SDF remove pixels reais.
            layer=pygame.Surface((WIDTH,GROUND-TOP),pygame.SRCALPHA)
            strip=self._load('image')
            offset=self._scroll()%strip.get_width()
            left=-offset
            while left<WIDTH:
                layer.blit(strip,(left,0));left+=strip.get_width()
            self.damage.apply(layer,self.travel*LAYER_SPEEDS[1])
            surface.blit(layer,(0,TOP))
        else:
            self._blit_strip(surface,self._load('image'))
        self.parallax_ia.draw(surface,self.biome,self.travel,TOP)
        self._animated_props(surface)
        self._lights(surface)
        self._weather(surface)
        if self.climate in ('tempestade','nevasca','tempestade_areia','cinzas'):
            self.atmosphere.draw(surface,self.biome,self.night)
        self.debris.draw(surface,self.travel,LAYER_SPEEDS[2])
        if self._transition is not None and self._transition_frames:
            old=self._transition.copy();old.set_alpha(int(210*(self._transition_frames/38.)**1.45))
            surface.blit(old,(0,0))

    def draw_effect_mask(self,surface):
        if self.biome=='cidade' or self.biome in MODULAR_BIOMES:surface.blit(self._city_surface('fxmask'),(0,TOP))
        else:self._blit_strip(surface,self._load('fxmask'))
    def draw_normal_map(self,surface):
        if self.biome=='cidade' or self.biome in MODULAR_BIOMES:surface.blit(self._city_surface('normal'),(0,TOP))
        else:self._blit_strip(surface,self._load('normal'))
    def draw_material_map(self,surface):
        if self.biome=='cidade' or self.biome in MODULAR_BIOMES:surface.blit(self._city_surface('material'),(0,TOP))
        else:self._blit_strip(surface,self._load('material'))
    def draw_flow_map(self,surface):
        if self.biome=='cidade' or self.biome in MODULAR_BIOMES:surface.blit(self._city_surface('flow'),(0,TOP))
        else:self._blit_strip(surface,self._load('flowmask'))
    def draw_geometry_map(self,surface):
        if self.biome=='cidade' or self.biome in MODULAR_BIOMES:surface.blit(self._city_surface('geometry'),(0,TOP))
        else:self._blit_strip(surface,self._load('geometry'))

    def draw_foreground(self,surface):
        if self.lightweight:return
        if self.biome=='cidade' or self.biome in MODULAR_BIOMES:
            # v3.124.2: Cidade nao tem mais props em primeiro plano.
            # Este passe ocorria depois dos inimigos e ocultava obstaculos;
            # nao desenhar tambem elimina uma composicao por quadro.
            return
        # A frente extrema só aparece nas bordas, com textura original da arte.
        image=_source(self.biome)
        for rect,x in (((0,310,124,188),-30),((776,310,124,188),WIDTH-16)):
            tex=pygame.transform.smoothscale(image.subsurface(rect),(45,136))
            tex.set_alpha(50)
            surface.blit(tex,(x+int(math.sin(self.frame*.035)*2),GROUND-145))
