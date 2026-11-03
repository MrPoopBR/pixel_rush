"""Pixel Rush v3.126.0 — biomas modulares originais Cidade Nevada/Deserto.

Arte no carregamento: camadas 225x250 desenhadas em pixel art, chunks seamless,
props presos a estruturas, intervalos fixos, mapas GLSL compatíveis.
Durante a corrida somente cópias de texturas prontas e uma escala nearest-neighbor.
Nao modifica fisica, inimigos, hitboxes, spawn ou gameplay.
"""
import math
import random
import os
import pygame
from collections import OrderedDict

LW, LH, SCALE, WIDTH, HEIGHT = 225, 250, 2, 450, 500
SUPPORTED_BIOMES = ('neve', 'deserto')
# O Deserto 2.0 ainda e piloto: a pintura atual permanece como padrao.
MODULAR_BIOMES = ('neve', 'deserto') if os.environ.get('PIXELRUSH_DESERTO_2_0')=='1' else ('neve',)
DARK_NIGHT = (55, 62, 109)


def _rgb(c, a=1.):
    return tuple(int(max(0, min(255, v*a))) for v in c)


def _rect(dst, col, x, y, w, h):
    pygame.draw.rect(dst, col, (int(x), int(y), int(w), int(h)))


def _p(dst, col, pts):
    pygame.draw.polygon(dst, col, [(int(x), int(y)) for x, y in pts])


def _line(dst, col, x1, y1, x2, y2, w=1):
    pygame.draw.line(dst, col, (int(x1), int(y1)), (int(x2), int(y2)), w)


class ModularBiomeScene:
    """Motor unificado de chunks: arte própria por bioma e saída de mapas técnicos."""

    def __init__(self, biome):
        if biome not in SUPPORTED_BIOMES:
            raise ValueError('bioma modular nao suportado: '+str(biome))
        self.biome = biome
        self.visual_quality = 1
        self._layers = {}
        self._map_cache = OrderedDict()
        self._sky_cache = OrderedDict()
        self._composites = {}
        self._night_veils = OrderedDict()
        self._geometry_view = None
        self._last_state = None
        for layer in ('far', 'mid', 'near'):
            self._layers[layer] = [self._make_chunk(layer, i) for i in range(4)]

    def _pine(self, surf, x, base, height, snow=True):
        x=int(x); base=int(base); h=int(height)
        _rect(surf, (83,69,93) if snow else (119,80,65), x-2,base-8,4,8)
        for j, width in enumerate((h//2, h*2//5, h//3)):
            y = base-9 - j*(h//4)
            col=((40, 89, 104),(44, 112, 120),(56, 125, 128))[j] if snow else ((48,108,88),(58,131,91),(77,155,98))[j]
            _p(surf,col,[(x-width//2,y),(x,y-(h//3)),(x+width//2,y)])
            if snow:
                _line(surf,(218,241,255),x-width//5,y-7,x+width//5,y-7,2)
                _rect(surf,(249,251,253),x-1,y-h//3,3,3)
            else:
                _line(surf,(96,177,118),x-width//6,y-10,x+width//6,y-10,1)

    def _snow_house(self, surf, x, ybase, w, h, seed):
        x=int(x); w=int(w); ybase=int(ybase); h=int(h)
        light=(234,201,140); glow=(255,238,175)
        color=((94,91,151),(110,106,165),(86,99,148),(121,99,150))[seed%4]
        dark=_rgb(color,.72)
        y=ybase-h
        _rect(surf,dark,x+2,y+2,w,h)
        _rect(surf,color,x,y,w-2,h)
        _rect(surf,_rgb(color,1.20),x+2,y+3,3,h-4)
        # telhado inclinado frio, com espessa neve acumulada
        _p(surf,(53,69,123),[(x-5,y+3),(x+w//2,y-13),(x+w+4,y+3)])
        _p(surf,(225,246,255),[(x-5,y+1),(x+w//2,y-15),(x+w+4,y+1),(x+w,y+5),(x+w//2,y-9),(x-3,y+5)])
        _line(surf,(170,211,239),x-5,y+3,x+w+4,y+3,2)
        # módulos janelas com moldura e luz amarela
        for yy in range(y+14, ybase-11,14):
            for xx in range(x+5,x+w-10,13):
                lit=((xx*3+yy+seed)%5)!=0
                _rect(surf,(54,62,103),xx-1,yy-1,9,11)
                _rect(surf,glow if lit else (146,193,222),xx,yy,7,9)
                _line(surf,(222,230,240),xx+3,yy,xx+3,yy+8)
                _line(surf,(210,213,223),xx,yy+4,xx+6,yy+4)
                _line(surf,(255,248,200) if lit else (187,219,238),xx+1,yy+1,xx+1,yy+3)
        _rect(surf,(70,68,111),x+w//2-4,ybase-17,9,17)
        _rect(surf,(222,185,129),x+w//2-2,ybase-15,5,13)
        _rect(surf,(234,247,255),x-2,ybase-4,w+3,4)
        _line(surf,(171,205,223),x-2,ybase-1,x+w,ybase-1)
        # beirais, adornos e jardineiras de inverno
        if seed%3==0:
            for xx in range(x+7,x+w-7,20):
                _rect(surf,(59,92,106),xx,ybase-8,8,3)
                _rect(surf,(223,247,253),xx+1,ybase-9,6,2)
                _rect(surf,(205,79,100),xx+3,ybase-10,2,2)

    def _lamp(self, surf, x, ybase, cold=True):
        _rect(surf,(52,54,86) if cold else (99,69,56),x-1,ybase-25,3,25)
        _rect(surf,(79,77,105),x-2,ybase-3,5,3)
        _rect(surf,(63,66,97),x-5,ybase-29,11,5)
        _rect(surf,(255,221,130),x-3,ybase-28,7,4)
        _rect(surf,(255,248,182),x-2,ybase-27,4,2)
        if cold:
            _rect(surf,(249,250,255),x-5,ybase-30,11,2)

    def _snow_arch(self, surf, x, ybase, width, height):
        base=ybase; h=height
        col=(72,79,134); stone=(112,123,174)
        _rect(surf,col,x,base-h,width,h)
        _rect(surf,stone,x+3,base-h+2,width-6,h-2)
        # vãos de arco sem transparecer à pista
        for a in range(x+9,x+width-9,29):
            _rect(surf,(69,94,147),a,base-h//2,19,h//2)
            pygame.draw.circle(surf,(69,94,147),(a+9,base-h//2),9)
        _rect(surf,(203,230,253),x-2,base-h-3,width+4,5)
        _rect(surf,(83,95,149),x-2,base-h+2,width+4,4)
        for a in range(x+8,x+width-8,16):
            _rect(surf,(177,199,225),a,base-h+7,2,5)

    def _snow_clocktower(self, surf, x, base):
        _rect(surf,(69,72,127),x-11,base-89,22,89)
        _rect(surf,(111,108,172),x-8,base-88,17,86)
        _p(surf,(53,61,117),[(x-15,base-88),(x,base-110),(x+15,base-88)])
        _p(surf,(241,247,255),[(x-15,base-91),(x,base-112),(x+15,base-91),(x,base-103)])
        _rect(surf,(55,62,115),x-9,base-83,18,21)
        pygame.draw.circle(surf,(254,238,193),(x,base-73),8)
        pygame.draw.circle(surf,(182,132,99),(x,base-73),6,1)
        _line(surf,(98,64,80),x,base-73,x,base-77)
        _line(surf,(98,64,80),x,base-73,x+3,base-71)
        for yy in (base-49,base-32):
            _rect(surf,(255,216,141),x-4,yy,8,11)
            _line(surf,(79,73,127),x,yy,x,yy+11)
        _rect(surf,(222,239,251),x-12,base-63,24,3)

    def _mountains(self, surf, idx, snow=True):
        rng=random.Random(2000+idx+int(not snow)*409)
        # montanhas com pontos iguais nas bordas: chunks sem abismos
        base=132 if snow else 152
        for passno in (0,1):
            if snow:
                col=(114,133,202) if passno==0 else (83,113,182)
                cap=(225,240,255) if passno==0 else (198,226,246)
            else:
                col=(193,127,122) if passno==0 else (162,106,104)
                cap=(238,183,131) if passno==0 else (224,154,110)
            y_base=base+passno*22
            _rect(surf,col,0,y_base,LW,84)
            xpos=-25
            peaks=[(0,y_base),(LW,y_base)]
            while xpos<LW+45:
                half=rng.randint(28,57)
                peak=y_base-rng.randint(25,66) + passno*4
                _p(surf,col,[(xpos,y_base),(xpos+half,peak),(xpos+2*half,y_base)])
                if snow:
                    _p(surf,cap,[(xpos+half-12,peak+18),(xpos+half,peak),(xpos+half+15,peak+22),(xpos+half+5,peak+16),(xpos+half,peak+20),(xpos+half-4,peak+14)])
                else:
                    _line(surf,cap,xpos+half,peak+8,xpos+half-7,peak+20,2)
                xpos+=half*2
        # base linear para conectar azuis de distância
        _rect(surf,(78,110,173) if snow else (174,116,97),0,181,LW,12)

    def _desert_palace(self, surf, x, base, width, h, idx):
        wall=((209,140,104),(226,161,111),(191,119,92))[idx%3]
        shade=(141,84,79)
        top=base-h
        _rect(surf,shade,x+2,top+3,width,h)
        _rect(surf,wall,x,top,width-2,h)
        for bx in (x+4,x+width-9):
            _rect(surf,_rgb(wall,.78),bx,top+5,3,h-8)
        # ornamento em friso
        _rect(surf,(243,190,122),x-2,top+3,width+2,4)
        for zx in range(x+3,x+width-3,9):
            _rect(surf,(140,85,81),zx,top+9,2,2)
            _rect(surf,(247,212,154),zx+2,top+10,3,1)
        # topo com platibanda e torre nas laterais
        _rect(surf,(163,99,82),x-2,top-5,width+2,7)
        _rect(surf,(244,182,116),x-2,top-6,width+2,3)
        for xx in (x+3,x+width-10):
            _rect(surf,(157,95,84),xx,top-16,7,11)
            _rect(surf,(244,175,114),xx+1,top-17,5,2)
        # arcos e relevos em blocos
        for xx in range(x+8,x+width-9,15):
            for yy in range(top+16,base-14,20):
                _rect(surf,(103,73,87),xx-1,yy,10,14)
                _rect(surf,(75,75,101),xx+1,yy+2,6,10)
                pygame.draw.circle(surf,(75,75,101),(xx+4,yy+2),3)
                _line(surf,(250,220,157),xx,yy+3,xx,yy+8)
        _rect(surf,(248,208,139),x,base-4,width,4)
        for x0 in range(x+4,x+width-3,9):
            _line(surf,(165,106,84),x0,base-8,x0+4,base-8)

    def _palm(self, surf, x, ground, size, idx):
        trunk=(121,77,60); leafdark=(54,103,67); leaf=(77,133,78)
        _line(surf,trunk,x,ground,x+3,ground-size,4)
        _line(surf,(167,115,74),x+1,ground-1,x+4,ground-size+3,1)
        crown=(x+3,ground-size)
        for sign,dy in ((-1,-2),(1,-1),(-1,7),(1,6)):
            pts=[crown,(crown[0]+sign*int(size*.43),crown[1]+dy),(crown[0]+sign*int(size*.63),crown[1]+dy+6)]
            _p(surf,leafdark,pts)
            _line(surf,leaf,*crown,pts[1][0],pts[1][1],2)
        for yy in range(ground-size+10,ground-2,7):
            _line(surf,(91,58,54),x+1,yy,x+3,yy-2)

    def _cactus(self, surf, x, ground, height):
        green=(73,131,92); green2=(112,165,97)
        _rect(surf,(54,91,75),x-4,ground-height,8,height)
        _rect(surf,green,x-3,ground-height,6,height)
        _line(surf,green2,x-1,ground-height+3,x-1,ground-3,1)
        _rect(surf,green,x-9,ground-height//2,5,5)
        _rect(surf,green,x-10,ground-height//2-9,4,13)
        _rect(surf,green,x+4,ground-height*2//3,5,5)
        _rect(surf,green,x+6,ground-height*2//3-10,4,14)
        for py in (ground-6,ground-13,ground-19):
            _line(surf,(208,195,129),x-3,py,x-5,py+2)
        _rect(surf,(247,129,151),x-2,ground-height-3,4,3)

    def _make_chunk(self, layer, index):
        rng=random.Random((100 if self.biome=='neve' else 800)+{'far':0,'mid':1000,'near':2000}[layer]+index*37)
        s=pygame.Surface((LW,LH),pygame.SRCALPHA)
        if self.biome=='neve':
            if layer=='far':
                self._mountains(s,index,snow=True)
                for i in range(0,LW,35):
                    if rng.random()<.65:self._pine(s,i+4,197,rng.randint(12,26),snow=True)
                _rect(s,(111,155,208),0,200,LW,27)
            elif layer=='mid':
                _rect(s,(104,133,184),0,202,LW,33)
                # arco central conectado ao chão, estrutura posterior clara
                self._snow_arch(s,-4,204,233,42)
                self._snow_clocktower(s,111+rng.randint(-16,16),200)
                for x in (10,54,172):
                    self._pine(s,x,201,rng.randint(23,43),snow=True)
                # festões de luz conectados à estrutura
                _line(s,(62,73,106),0,159,LW,159)
                for x in range(9,LW,20):
                    _rect(s,(245,210,120),x,160,3,3)
            elif layer=='near':
                _rect(s,(84,95,128),0,224,LW,6)
                x=-4
                while x<LW:
                    w=rng.randint(36,55);h=rng.randint(48,89)
                    self._snow_house(s,x,228,w,h,index*7+x)
                    x+=w+2
                # props intercalados: sem sobreposição; todos apoiados no calçamento
                for cx in (12,114,214):
                    if cx ==114:self._pine(s,cx,231,21,snow=True)
                    else:self._lamp(s,cx,230,True)
                # asfalto / neve restrita às bordas, pista contínua
                _rect(s,(128,139,155),0,228,LW,5)
                _line(s,(225,242,252),0,228,LW,228,2)
                _rect(s,(72,88,108),0,233,LW,17)
                _line(s,(173,195,211),0,233,LW,233,1)
                for x in range(5,LW,21):
                    _rect(s,(99,121,139),x,244,12,1)
                # faixa descontínua somente como textura visual
                for x in range(12,LW,48):
                    _rect(s,(189,203,207),x,242,21,1)
        else:
            if layer=='far':
                self._mountains(s,index,snow=False)
                # dunas geométricas contínuas em silhueta
                _rect(s,(222,166,108),0,178,LW,49)
                for cx in range(-40,LW+65,71):
                    _p(s,(241,191,119),[(cx,194),(cx+36,169),(cx+86,194)])
                    _line(s,(255,209,131),cx+36,169,cx+62,183,2)
                for x in (23,109,182):
                    _rect(s,(169,111,92),x,159,7,27)
                    _rect(s,(227,164,111),x-2,156,11,4)
            elif layer=='mid':
                # aqueduto em colunas e arcos reais, sem objetos flutuando
                _rect(s,(151,97,86),0,188,LW,27)
                _rect(s,(219,158,113),0,177,LW,11)
                _rect(s,(239,184,127),0,176,LW,3)
                for x in range(6,LW,36):
                    _rect(s,(110,87,95),x,192,23,25)
                    pygame.draw.circle(s,(110,87,95),(x+11,192),11)
                    _rect(s,(191,131,108),x-3,178,5,39)
                    _rect(s,(191,131,108),x+25,178,4,39)
                self._desert_palace(s,73,193,82,83,index)
            elif layer=='near':
                # blocos urbanos doásis — distintos da Cidade, sem vegetação na pista
                _rect(s,(204,141,107),0,213,LW,18)
                for left in (-6,37,100,155,206):
                    w=39+rng.randint(0,10);h=rng.randint(54,85)
                    self._desert_palace(s,left,229,w,h,index+left)
                for x in (17,117,216):
                    if x==117:self._cactus(s,x,230,29)
                    else:self._palm(s,x,230,37,index)
                # pista batida em rocha, contínua e sem vegetação no trajeto
                _rect(s,(198,138,102),0,229,LW,5)
                _line(s,(255,199,129),0,228,LW,228,2)
                _rect(s,(132,93,83),0,234,LW,16)
                for x in range(0,LW,19):
                    _line(s,(164,114,93),x,240,x+7,240)
                    _rect(s,(204,140,100),x+4,247,5,1)
        return s

    def _tile_map(self,layer,idx,kind):
        key=(layer,idx,kind)
        if key in self._map_cache:
            self._map_cache.move_to_end(key)
            return self._map_cache[key]
        src=self._layers[layer][idx]
        if kind=='image': return src
        target=pygame.Surface((LW,LH),pygame.SRCALPHA)
        if kind in ('normal','flow'):
            # somente pixels preenchidos recebem o mapa; céu transparente
            col=(128,128,255,255) if kind=='normal' else (128,128,0,255)
        elif kind=='geometry':
            col=(0,210,0,255)
        elif kind=='material':
            col=(142,162,193,255) if self.biome=='neve' else (194,139,111,255)
        else:
            col=(0,0,0,0)
        if kind=='fxmask':
            if layer in ('mid','near'):
                for y in range(110 if layer=='mid' else 130,217,22):
                    for x in range(8,LW,20):
                        _rect(target,(255,206,112,170),x,y,3,5)
        else:
            if src.get_colorkey() is not None: pass
            pygame.mask.from_surface(src,threshold=90).to_surface(surface=target,setcolor=col,unsetcolor=(0,0,0,0))
        self._map_cache[key]=target
        while len(self._map_cache)>30:
            self._map_cache.popitem(last=False)
        return target

    def _draw_layer(self,dst,layer,travel,kind):
        factor={'far':.12,'mid':.28,'near':.52}[layer]
        off=max(0.,travel)*factor*.5
        first=int(off//LW)
        shift=int(off%LW)
        # QA 3.277.42: 1 lote C em vez de 2 chamadas Python->SDL;
        # mantem ordem e area exata, descarta apenas tiles 100% fora.
        operations=[]
        for j in range(2):
            variant=(first+j)%len(self._layers[layer])
            tile=self._tile_map(layer,variant,kind)
            x=j*LW-shift
            if x<dst.get_width() and x+tile.get_width()>0:
                operations.append((tile,(x,0)))
        if operations:
            dst.blits(operations,doreturn=False)

    def render_scene(self,target,travel,frame,night,climate,phase,foreground_only=False,map_kind='image'):
        if foreground_only: return
        # Sem segundo céu: o ParallaxBackground original já possui um céu do
        # ciclo dia/noite. Não o sobrescrever com gradientes sobrepostos.
        low=self._composites.get(map_kind)
        if low is None:
            low=pygame.Surface((LW,LH),pygame.SRCALPHA)
            self._composites[map_kind]=low
        if map_kind=='normal':low.fill((128,128,255,255))
        elif map_kind=='flow':low.fill((128,128,0,255))
        else:low.fill((0,0,0,0))
        for layer in ('far','mid','near'):
            self._draw_layer(low,layer,travel,map_kind)
        if map_kind=='image':
            # A neve e a pedra reagem à noite sem escurecer novamente o céu
            if night>.04:
                v=min(1.,night)
                night_idx=int(v*12+.5)
                veil=self._night_veils.get(night_idx)
                if veil is None:
                    veil=pygame.Surface((LW,LH),pygame.SRCALPHA)
                    k=night_idx/12.
                    veil.fill((int(255-106*k),int(255-99*k),int(255-70*k),255))
                    self._night_veils[night_idx]=veil
                    if len(self._night_veils)>6:self._night_veils.popitem(last=False)
                low.blit(veil,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
            # iluminação localizada: sem halos brancos gigantes
            if night>.20:
                for cx in (12,114,214):
                    # pontos luminosos restritos a lanternas reais (sem bolhas)
                    _rect(low,(255,231,162,255),cx-1,201,3,3)
            # clima granular pouco agressivo e determinístico
            if climate in ('neve','nevasca') and self.biome=='neve':
                count=18 if self.visual_quality else 9
                for i in range(count):
                    x=int((i*47+frame*0.5+(i%3)*7)%LW)
                    y=int((i*31+frame*(1.1 if climate=='nevasca' else .55))%LH)
                    pygame.draw.circle(low,(237,246,255,190),(x,y),1)
            if climate in ('areia','tempestade_areia') and self.biome=='deserto':
                for i in range(12 if self.visual_quality else 6):
                    x=int((i*41-frame*1.7)%LW);y=70+int((i*29+frame*.5)%140)
                    _line(low,(235,186,125),x,y,x+7,y)
        pygame.transform.scale(low,(WIDTH,HEIGHT),target)
        if map_kind=='geometry': self._geometry_view=target.copy()
        self._last_state=(travel,frame,night,climate,phase)

    def ambient_occlusion(self,source_x,listener_x=90,source_y=490,listener_y=652):
        geom=self._geometry_view
        if geom is None:return 0.
        total=0.
        for i in range(1,17):
            t=i/17.
            x=int(listener_x+(source_x-listener_x)*t)
            y=int(listener_y+(source_y-listener_y)*t)-230
            if 0<=x<geom.get_width() and 0<=y<geom.get_height():
                total+=geom.get_at((x,y)).g/255.
        return min(.70,total/16*.7)
