"""Pixel Rush v3.118.0 — Cidade 2.3, correção da estrutura espacial.

Todos os chunks são criados em coordenadas LÓGICAS 450x250 e têm largura 900
na saída. O posicionamento usa stride exato, sem overlap ou flip de chunk.
Camadas diferentes sempre usam a mesma linha do horizonte e pavimento. Props
ficam presos a ruas, canteiros e fachadas — nunca suspensos no vazio.

O cache LRU contém apenas texturas visíveis (sem duplicar dezenas de mapas
900x500 em memória). Este módulo não muda colisões do jogador ou obstáculos.
"""
from collections import OrderedDict
import math
import random
import pygame
from pixelrush_rle_prod_v327727 import acelerar_textura_estatica
from pixelrush_city2_v3117 import CityPilotScene as PreviousCity, SpriteLibrary, SpriteInstance, ChunkVariant
from pixelrush_city2_v3115 import Layer
from pixelrush_city2_v3115 import WIDTH, LOW_W, LOW_H, SCENE_W, SCENE_H, SCALE, DEFAULT_NORMAL, NEUTRAL_FLOW, clamp, lerp_color


class CityPilotScene(PreviousCity):
    def __init__(self):
        # Não chamar PreviousCity.__init__: ele criava seis superfícies gigantes
        # por chunk, consumindo centenas de MB antes mesmo de entrar na corrida.
        self._flips = OrderedDict()
        self._flip_limit = 10
        self._glows = {}
        self._sky_cache = OrderedDict()
        self._scaled = OrderedDict()
        self._scaled_limit = 14
        self.rand = random.Random(31180)
        self.lib = SpriteLibrary()
        self.layers = self._build_layers()
        self.sky_period = 960
        self._geometry_view = None
        self._last_state = (0.0, 0, 0.0, 'limpo', 0.5)
        self._build_glows()

    @staticmethod
    def _blank_maps():
        # A raiz do bug era usar mapas 900x500 desenhando coordenadas 450x250.
        # TODOS os canais comecam em 450x250 e sao escalados juntos para 900x500.
        def blank():return pygame.Surface((LOW_W,LOW_H),pygame.SRCALPHA)
        normal=blank();normal.fill(DEFAULT_NORMAL)
        flow=blank();flow.fill(NEUTRAL_FLOW)
        return dict(image=blank(), geometry=blank(), fxmask=blank(),
                    normal=normal, material=blank(), flow=flow)

    @staticmethod
    def _palette(idx):
        return [
            ((205, 157, 133), (149, 107, 99), (249, 215, 161)),
            ((203, 183, 159), (147, 137, 123), (255, 224, 165)),
            ((181, 152, 174), (128, 103, 127), (251, 208, 170)),
            ((203, 167, 129), (145, 110, 90), (254, 222, 157)),
            ((175, 159, 190), (125, 111, 155), (244, 217, 177)),
            ((187, 145, 151), (137, 102, 115), (254, 218, 161)),
        ][idx % 6]

    @staticmethod
    def _facade_details(maps, x, y, w, bottom, seed, palette):
        """Pixel textures packed into their parent building bounds."""
        img = maps['image']; mat = maps['material']; fx = maps['fxmask']
        hi, lo, lit = palette
        # telhado/sombra de oclusão e juntas discretas de alvenaria
        pygame.draw.rect(img, tuple(min(255, c + 27) for c in hi), (x, y, w, 3))
        pygame.draw.rect(img, lo, (x+w-4, y+3, 4, bottom-y-3))
        pygame.draw.rect(img, lo, (x, bottom-5, w, 5))
        for yy in range(y+14, bottom-15, 16):
            pygame.draw.line(img, tuple(int(c*.85) for c in hi), (x+3, yy), (x+w-5, yy), 1)
        # varandas e floreiras inteiramente conectadas à fachada
        for yy in range(y+27, bottom-24, 34):
            pygame.draw.rect(img, (100, 79, 79), (x+6, yy, max(8,w-12), 3))
            for px in range(x+9, x+w-12, 13):
                pygame.draw.rect(img, (51, 128, 81), (px, yy-3, 7, 3))
                pygame.draw.rect(img, (234, 149, 167) if (px+seed)%2 else (255, 217, 122), (px+2, yy-5, 3, 3))
            pygame.draw.rect(mat, (111, 95, 92), (x+6, yy, max(8,w-12), 3))
        # sacadas laterais / entrada sombreada, se perto do nível da rua
        if bottom >= 205:
            pygame.draw.rect(img, (61, 65, 83), (x+6, bottom-20, max(10,w-12), 15))
            pygame.draw.rect(img, (170, 218, 236), (x+8, bottom-18, max(6,w-16), 11))
            pygame.draw.line(img, (245, 229, 197), (x+w//2, bottom-17), (x+w//2, bottom-7), 2)
            pygame.draw.rect(fx, (255, 210, 130, 90), (x+8, bottom-18, max(6,w-16), 11))
            pygame.draw.rect(img, lo, (x+3, bottom-22, w-6, 4))

    def _buildings(self, maps, seed, baseline, min_h, max_h, min_w, max_w, near=False):
        rng = random.Random(seed)
        x = -3  # iniciar antes da borda: nenhuma fresta na junção dos chunks
        n = 0
        while x < LOW_W:
            w = rng.randint(min_w, max_w)
            h = rng.randint(min_h, max_h)
            hi, lo, lit = self._palette(n + seed)
            roof = ('tower','spire','clock',None,None,None)[(n+seed)%6] if near else ('spire',None,None)[(n+seed)%3]
            self._draw_building(maps, x, baseline, w+1, h, hi, lo, roof=roof,
                                win_color=(215, 222, 236) if not near else (236,225,205),
                                win_lit=lit, material=(150, 135, 139))
            if near:
                self._facade_details(maps, x, baseline-h, w, baseline, n+seed, (hi,lo,lit))
            # juntas da parede e canos vinculados ao edifício
            if near and n % 3 == 0:
                pygame.draw.rect(maps['image'], (96, 92, 104), (x+w-6, baseline-30, 2, 26))
            x += w  # sem sobreposição, sem buracos, sem preenchimentos suspensos
            n += 1

    def _make_far_variant(self, idx):
        maps = self._blank_maps()
        self._buildings(maps, 1800+idx, baseline=169, min_h=62, max_h=110,
                        min_w=14, max_w=31, near=False)
        # skyline estaciona sobre uma linha de horizonte constante em TODOS os chunks
        pygame.draw.rect(maps['image'], (123,147,202), (0, 166, LOW_W, 4))
        pygame.draw.rect(maps['material'], (130,150,177), (0, 166, LOW_W, 4))
        return ChunkVariant(**maps)

    def _make_mid_variant(self, idx):
        maps=self._blank_maps()
        self._buildings(maps, 2800+idx, baseline=205, min_h=62, max_h=112,
                        min_w=26, max_w=48, near=False)
        # Viaduto contínuo ao longo do mundo, sustentado por pilares.
        rail_y = 133
        pygame.draw.rect(maps['image'], (99,131,182), (0,rail_y,LOW_W,9))
        pygame.draw.rect(maps['image'], (161,184,211), (0,rail_y,LOW_W,2))
        pygame.draw.rect(maps['geometry'], (0,210,0), (0,rail_y,LOW_W,9))
        pygame.draw.rect(maps['material'], (103,123,154), (0,rail_y,LOW_W,9))
        for bx in range(21,LOW_W+35,54):
            pygame.draw.rect(maps['image'], (102,127,160), (bx,rail_y+8,7,65))
            pygame.draw.rect(maps['image'], (168,182,203), (bx+1,rail_y+9,2,65))
            pygame.draw.rect(maps['geometry'], (0,210,0), (bx,rail_y+8,7,65))
            pygame.draw.rect(maps['material'], (100,124,154), (bx,rail_y+8,7,65))
        # Abaixo do viaduto, cidade ao fundo, sem ilhas gráficas à deriva.
        pygame.draw.rect(maps['image'], (113,143,159), (0,202,LOW_W,4))
        return ChunkVariant(**maps)

    def _make_near_variant(self, idx):
        maps=self._blank_maps()
        # Fachadas da rua: a frente cobre horizontalmente TODO o chunk.
        self._buildings(maps, 3800+idx, baseline=235, min_h=82, max_h=138,
                        min_w=36, max_w=66, near=True)
        img,mat,geo=maps['image'],maps['material'],maps['geometry']
        # Chão em TODA a largura, alinhado à borda inferior da área cenográfica.
        pygame.draw.rect(img, (95,122,91), (0,225,LOW_W,6))
        pygame.draw.rect(img, (174,163,146), (0,231,LOW_W,6))
        pygame.draw.rect(img, (110,102,102), (0,237,LOW_W,13))
        pygame.draw.rect(mat,(87,117,93),(0,225,LOW_W,6))
        pygame.draw.rect(mat,(149,140,130),(0,231,LOW_W,6))
        pygame.draw.rect(mat,(102,94,91),(0,237,LOW_W,13))
        pygame.draw.rect(geo,(0,220,0),(0,225,LOW_W,25))
        # Padrão estável de pavimento, ladrilhos e bueiros amarrados à calçada.
        for xx in range(0,LOW_W,14):
            pygame.draw.rect(img,(209,199,183),(xx,233,8,1))
            pygame.draw.line(img,(78,75,77),(xx,245),(xx+7,245),1)
            if xx % 70 == 0:
                pygame.draw.rect(img,(63,75,78),(xx+2,238,8,3))
        # canteiros sobre o chão, não suspensos
        rng=random.Random(4500+idx)
        for bx in range(28,LOW_W,53):
            pygame.draw.rect(img,(125,88,78),(bx,224,24,5))
            pygame.draw.rect(img,(53,135,75),(bx+2,221,21,5))
            for fx in range(bx+5,bx+22,7):
                pygame.draw.circle(img,(240,156,175) if (fx+idx)%2 else (245,220,132),(fx,220),2)
        sprites=[]
        # Todos os sprites têm raízes/pontos de apoio na mesma cota y=230.
        for i, bx in enumerate((13,109,212,315,417)):
            sprites.append(SpriteInstance('tree_big' if i%2==0 else 'tree_small',bx,230,
                                          sway=1.2+0.2*i,phase=idx+i*.4))
        for i,bx in enumerate((64,166,269,372)):
            sprites.append(SpriteInstance('lamp',bx,230,phase=idx*.1+i*.2,glow=1.))
        for i,bx in enumerate((82,185,288,391)):
            sprites.append(SpriteInstance('flowerpot',bx,230,phase=idx+i*.3))
        # Placas presas à fachada: com haste que chega à calçada, sem objetos soltos.
        for x in (50, 244, 418):
            pygame.draw.rect(img,(72,64,81),(x,190,2,38))
            pygame.draw.rect(geo,(0,190,0),(x,190,2,38))
            sprites.append(SpriteInstance('banner',x,191,sway=.5,phase=.3+idx))
        # letreiros presos ao próprio prédio (não colocados aleatoriamente no céu)
        for x in (40, 155, 342):
            pygame.draw.rect(img,(74,63,75),(x,205,40,3))
            pygame.draw.rect(img,(235,172,116),(x+1,202,38,3))
        return ChunkVariant(**maps,sprites=sprites)

    def _make_fg_variant(self, idx):
        # Camada da frente SEM placas nem árvores flutuantes. Apenas plantas
        # fixadas na borda da calçada, em primeiro plano.
        maps=self._blank_maps()
        sprites=[SpriteInstance('fg_leaves',0,241,sway=.7,phase=.8+idx),
                 SpriteInstance('fg_leaves',LOW_W-24,242,sway=.8,phase=1.3+idx)]
        return ChunkVariant(**maps,sprites=sprites)

    def _build_layers(self):
        # Menos variantes base 900x500 na RAM; sequência ilimitada por módulo.
        far=[self._make_far_variant(i) for i in range(3)]
        mid=[self._make_mid_variant(i) for i in range(3)]
        near=[self._make_near_variant(i) for i in range(5)]
        fg=[self._make_fg_variant(i) for i in range(2)]
        return [
            Layer('far',.12,SCENE_W,far,(0,1,2,1,0,2,0,2,1), (False,)*9),
            Layer('mid',.28,SCENE_W,mid,(0,1,2,0,2,1,2,0,1), (False,)*9),
            Layer('near',.63,SCENE_W,near,(0,1,2,3,4,2,0,4,1,3), (False,)*10),
            Layer('fg',1.06,SCENE_W,fg,(0,1,0,0,1), (False,)*5,foreground=True),
        ]

    @staticmethod
    def _layer_tiles(travel,layer):
        # sempre cobrir a viewport inclusive ao atravessar o fim do período
        scroll = max(0, int(float(travel)*layer.speed))
        tile_index, remainder = divmod(scroll,SCENE_W)
        x=-remainder
        while x<WIDTH:
            idx=tile_index%len(layer.sequence)
            yield x, layer.variants[layer.sequence[idx]], False
            x+=SCENE_W
            tile_index+=1

    def _scaled_surface(self,variant,kind):
        key=(id(variant),kind)
        cached=self._scaled.get(key)
        if cached is not None:
            self._scaled.move_to_end(key)
            return cached
        tex=getattr(variant,kind)
        # somente texturas realmente desenhadas chegam à resolução 900x500.
        if tex.get_size()!=(SCENE_W,SCENE_H):
            tex=pygame.transform.scale(tex,(SCENE_W,SCENE_H))
        # Atlas estatico: acelera o blit, mas nao os buffers dinamicos.
        if kind == 'image':
            acelerar_textura_estatica(tex)
        self._scaled[key]=tex
        if len(self._scaled)>self._scaled_limit:self._scaled.popitem(last=False)
        return tex

    def _draw_sprite(self, surface, kind, x, y, frame, night, climate,
                     map_kind='image', flip=False):
        # Sprite pronto: evitar RLE onde ha transparencia intermediaria.
        if map_kind == 'image':
            asset = self.lib.assets.get(kind)
            if asset is not None:
                acelerar_textura_estatica(asset.image, alpha_binario=True)
        return super()._draw_sprite(surface, kind, x, y, frame, night,
                                    climate, map_kind, flip)

    def _render_chunk(self,target,variant,flip,x,frame,night,climate,phase,map_kind='image',only_sprites=False):
        if not only_sprites:
            tex=self._scaled_surface(variant,map_kind)
            # Blit com recorte de viewport: nenhum pix fora da tela e menos RAM.
            r=pygame.Rect(max(0,-x),0,min(SCENE_W,WIDTH-x)-max(0,-x),SCENE_H)
            if r.w>0:target.blit(tex,(max(0,x),0),r)
        for sp in variant.sprites:
            asset=self.lib.assets.get(sp.kind)
            if asset is None:continue
            tex=getattr(asset,map_kind)
            width=tex.get_width()
            wind=1.5 if climate in ('vento','tempestade','nevasca') else 1.
            # sway de no máximo 2px e y do sprite ancorado no chão.
            dx=int(round(math.sin(frame*.025+sp.phase)*sp.sway*wind))
            px=x+sp.x*SCALE+dx
            if px>=WIDTH+2 or px+width<=-2:continue
            self._draw_sprite(target,sp.kind,px,sp.y*SCALE,frame,night,climate,map_kind,False)

    def _draw_sky(self,target,travel,frame,night,phase,climate):
        """Céu com gradiente de verdade, sem BLEND_RGBA_ADD em tela inteira."""
        quant=(round(float(night)*20)/20.,round(float(phase)*10)/10.)
        grad=self._sky_cache.get(quant)
        if grad is None:
            grad=pygame.Surface((WIDTH,SCENE_H)).convert()
            dusk=max(0.,1.-abs(phase-.48)*4.)
            top=lerp_color((79,151,239),(47,46,100),night)
            horizon=lerp_color((179,211,244),(100,92,149),night)
            top=lerp_color(top,(109,90,167),.48*dusk*(1-night))
            horizon=lerp_color(horizon,(241,160,122),.55*dusk*(1-night))
            for y in range(SCENE_H):
                t=min(1.,y/(SCENE_H*.68))
                pygame.draw.line(grad,lerp_color(top,horizon,t),(0,y),(WIDTH-1,y))
            self._sky_cache[quant]=grad
            if len(self._sky_cache)>4:self._sky_cache.popitem(last=False)
        else:self._sky_cache.move_to_end(quant)
        target.blit(grad,(0,0))
        # Sol/lua bem afastados da pista; nunca cobrem o chão.
        x=int((75-travel*.019)%(WIDTH+110))-35;y=58
        if night<.55:
            pygame.draw.circle(target,(250,222,128),(x,y),23)
        else:
            pygame.draw.circle(target,(227,232,245),(x,y),18)
            pygame.draw.circle(target,(64,67,113),(x+7,y-5),17)
            for i in range(13):
                pygame.draw.rect(target,(227,225,241),((i*83+31)%WIDTH,13+(i*29)%100,2,2))
        cloud=(245,238,231) if night<.55 else (109,105,150)
        for i in range(7):
            cx=int((i*97+26-travel*.047)%(WIDTH+120))-50
            cy=37+(i%3)*26
            for dx,dy,r in ((0,0,15),(-12,5,10),(13,5,11),(4,-6,9)):
                pygame.draw.circle(target,cloud,(cx+dx,cy+dy),r)
        if climate in ('chuva','tempestade'):
            for i in range(22 if climate=='chuva' else 32):
                xx=int((i*51-frame*(3.4 if climate=='chuva' else 5.8))%(WIDTH+35))-15
                yy=int((i*41+frame*6.2)%SCENE_H)
                pygame.draw.line(target,(133,177,217),(xx,yy),(xx-4,yy+11),1)

    def _draw_train(self,target,travel,frame,night,map_kind='image'):
        # Trem apenas na linha férrea que existe fisicamente em y=133.
        asset=self.lib.assets['train']; tex=getattr(asset,map_kind)
        x=int((WIDTH+130)-((frame*2.2)%(WIDTH+240)))
        y=133*SCALE-tex.get_height()+3
        target.blit(tex,(x,y))

    def _draw_traffic(self,target,frame,night):
        # trânsito ao fundo exclusivamente sobre a via, sem carros no ar
        y=237* SCALE -5
        for i in range(3):
            x=int((i*220+frame*1.1)%(WIDTH+240))-50
            pygame.draw.rect(target,(68,108,144),(x,y,25,6),border_radius=2)
            pygame.draw.rect(target,(250,225,155),(x,y+1,4,2))
            pygame.draw.rect(target,(230,93,86),(x+22,y+1,3,2))

    def _draw_birds(self,target,frame,map_kind='image'):
        if map_kind!='image':return
        # aves apenas no céu e sem silhuetas duplicadas enormes
        bird=self.lib.assets.get('bird')
        if bird:
            for i in range(2):
                x=int((WIDTH+30-(frame*(.6+i*.15))+i*135)%(WIDTH+180))-45
                target.blit(bird.image,(x,65+i*23))

    def render_scene(self,target,travel,frame,night,climate,phase,foreground_only=False,map_kind='image'):
        if not foreground_only:
            if map_kind=='image':self._draw_sky(target,travel,frame,night,phase,climate)
            elif map_kind=='normal':target.fill(DEFAULT_NORMAL)
            elif map_kind=='flow':target.fill(NEUTRAL_FLOW)
            else:target.fill((0,0,0,0))
        for layer in self.layers:
            if layer.foreground!=foreground_only:continue
            for x,variant,flip in self._layer_tiles(travel,layer):
                self._render_chunk(target,variant,flip,int(x),frame,night,climate,phase,map_kind)
            if layer.name=='mid' and not foreground_only:
                self._draw_train(target,travel,frame,night,map_kind)
        if map_kind=='image' and not foreground_only:
            self._draw_traffic(target,frame,night)
            self._draw_birds(target,frame)
            if night>.12:
                veil=pygame.Surface((WIDTH,SCENE_H),pygame.SRCALPHA)
                veil.fill((18,31,63,int(72*night)))
                target.blit(veil,(0,0))
        if map_kind=='geometry' and not foreground_only:
            self._geometry_view=target.copy()
        self._last_state=(travel,frame,night,climate,phase)
