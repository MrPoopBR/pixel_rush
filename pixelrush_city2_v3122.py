"""Pixel Rush v3.122.0 — Cidade Definitiva Plus (despoluição e acabamento premium).

Escopo exclusivamente cenografico: estilos arquitetonicos, vegetacao e
mobiliario em pixel-art, sprites independentes, iluminacao e materiais.
Base tecnica da v3.120.0 mantida: coordenadas/chunks/colisoes intactas.
Todo detalhe de fachada e precomputado durante o carregamento dos chunks.
"""
from collections import OrderedDict
import math
import random
import pygame
from pixelrush_city2_v3120 import CityPilotScene as _City120, SpriteLibraryPremium as _Sprites120
from pixelrush_city2_v3115 import Layer, SpriteInstance, ChunkVariant, LOW_W, LOW_H, SCENE_W, SCENE_H, WIDTH, lerp_color

# Paleta compartilhada com a pixel-art das skins: poucos tons por superficie,
# outlines frios, brilho quente e materiais que mantem contraste no escuro.
INK=(46,48,66)
RIM=(248,225,181)
MINT=(111,204,142)
DARK_GREEN=(34,89,68)


class SpriteLibraryFinalPlus(_Sprites120):
    """Novas especies e objetos com mapas GPU gerados junto com o sprite."""
    def _build(self):
        super()._build()
        self.assets['tree_blossom']=self._blossom_tree()
        self.assets['tree_copper']=self._copper_tree()
        self.assets['planter_stone']=self._stone_planter()
        self.assets['bike_rack']=self._bike_rack()
        self.assets['lantern_sign']=self._lantern_sign()
        self.assets['hedge']=self._hedge()

    def _blossom_tree(self):
        s=self._blank((40,49))
        pygame.draw.rect(s,(65,60,77),(17,29,6,20))
        pygame.draw.rect(s,(115,81,91),(19,28,3,18))
        pygame.draw.line(s,(65,60,77),(19,36),(11,25),2)
        pygame.draw.line(s,(65,60,77),(22,32),(31,23),2)
        heads=((11,24,9),(20,17,10),(29,26,9),(10,16,7),(27,13,8),(19,27,11))
        for i,(cx,cy,r) in enumerate(heads):
            pygame.draw.circle(s,(144,78,116),(cx,cy+2),r+1)
            pygame.draw.circle(s,(229,132,159) if i%2 else (250,170,182),(cx,cy),r)
        for x,y in ((7,17),(16,12),(28,11),(30,22),(13,30),(22,24)):
            pygame.draw.rect(s,(255,217,204),(x,y,3,2))
        for x,y in ((8,27),(27,30),(18,7)):
            pygame.draw.rect(s,(186,89,136),(x,y,3,2))
        return self._make_asset(s,material_color=(175,132,153))

    def _copper_tree(self):
        s=self._blank((36,48))
        pygame.draw.rect(s,(60,54,64),(16,29,6,19))
        pygame.draw.rect(s,(129,88,67),(18,30,3,16))
        pygame.draw.line(s,(77,56,52),(18,34),(10,27),2)
        pygame.draw.line(s,(77,56,52),(20,32),(27,24),2)
        shapes=((11,24,9),(25,25,10),(19,17,12),(10,18,7),(27,13,6),(19,30,8))
        for i,(x,y,r) in enumerate(shapes):
            pygame.draw.circle(s,(105,64,70),(x,y+2),r+1)
            pygame.draw.circle(s,(186,98,74) if i%2 else (220,137,80),(x,y),r)
        for x,y in ((11,13),(22,10),(27,24),(14,28),(20,20)):
            pygame.draw.rect(s,(251,191,105),(x,y,3,3))
        return self._make_asset(s,material_color=(175,116,84))

    def _stone_planter(self):
        s=self._blank((22,16))
        pygame.draw.rect(s,(65,66,79),(2,7,18,8))
        pygame.draw.rect(s,(137,137,145),(3,8,16,5))
        pygame.draw.rect(s,(203,193,180),(3,7,16,2))
        pygame.draw.rect(s,(64,124,82),(5,3,12,6))
        for i,x in enumerate((6,12,16)):
            pygame.draw.rect(s,(114,197,123),(x,2+i%2,3,3))
            pygame.draw.rect(s,(255,179,151) if i%2 else (255,222,124),(x+1,1+i%2,2,2))
        return self._make_asset(s,material_color=(144,139,132))

    def _bike_rack(self):
        s=self._blank((29,17))
        for x in (7,20):
            pygame.draw.circle(s,INK,(x,11),5,2)
            pygame.draw.circle(s,(174,184,192),(x,11),3,1)
        pygame.draw.line(s,(96,118,139),(7,11),(13,5),2)
        pygame.draw.line(s,(96,118,139),(13,5),(20,11),2)
        pygame.draw.line(s,(96,118,139),(7,11),(17,11),2)
        pygame.draw.line(s,(96,118,139),(13,5),(11,3),2)
        pygame.draw.line(s,(69,61,81),(11,3),(16,3),2)
        pygame.draw.line(s,(69,61,81),(20,11),(23,4),2)
        return self._make_asset(s,material_color=(129,148,160))

    def _lantern_sign(self):
        s=self._blank((21,24))
        pygame.draw.rect(s,INK,(0,0,3,22))
        pygame.draw.rect(s,(109,102,117),(2,3,6,2))
        pygame.draw.rect(s,INK,(7,3,2,6))
        pygame.draw.rect(s,INK,(5,9,12,12))
        pygame.draw.rect(s,(241,170,114),(7,11,8,8))
        pygame.draw.rect(s,(255,233,160),(9,13,4,4))
        def fx(_):
            out=self._blank((21,24))
            for rad,alpha in ((10,18),(7,52),(4,120)):
                pygame.draw.circle(out,(255,195,108,alpha),(11,15),rad)
            return out
        return self._make_asset(s,material_color=(205,153,110),fx_builder=fx)

    def _hedge(self):
        s=self._blank((31,16))
        pygame.draw.rect(s,(57,71,63),(2,11,27,5))
        for x,y,r,col in ((6,9,7,(38,118,77)),(16,7,8,(60,158,93)),(25,9,6,(42,129,84))):
            pygame.draw.circle(s,INK,(x,y),r+1)
            pygame.draw.circle(s,col,(x,y),r)
        for px,py in ((9,5),(16,3),(23,8)):
            pygame.draw.rect(s,(118,213,138),(px,py,3,2))
        return self._make_asset(s,material_color=(64,135,89))


class CityPilotScene(_City120):
    """Finalizacao visual do bioma piloto: nenhum sistema de gameplay novo."""
    def __init__(self):
        # Mantem os caches existentes e as mesmas velocidades/steps de chunk.
        self._flips=OrderedDict();self._flip_limit=10
        self._glows={};self._sky_cache=OrderedDict()
        self._scaled=OrderedDict();self._scaled_limit=14
        # QA774: apenas weakrefs de outputs do scale, sem Surface extra.
        from weakref import WeakSet
        self._qa_scaled_owned=WeakSet()
        self._qa_scaled_reused=0
        self._qa_scaled_allocated=0
        self._qa_scaled_rejected=0
        self.rand=random.Random(31220)
        self.lib=SpriteLibraryFinalPlus()
        self.layers=self._build_layers()
        self._prebake_static_props()
        self.sky_period=960
        self._geometry_view=None
        self._last_state=(0.0,0,0.0,'limpo',0.5)
        self._build_glows()

    def _prebake_static_props(self):
        """Compõe props imóveis uma vez nos chunks e em todos os mapas.

        Mantém o mesmo pixel art e mesma posição renderizada: 450x250 (chunk)
        vira 900x500 por NEAREST, enquanto os sprites chegam em 2x; por isso
        eles são reduzidos para 1x apenas durante o pré-processamento.
        Não pré-compõe lâmpadas, árvores ou elementos que balançam.
        """
        static_maps=('image','geometry','fxmask','normal','material','flow')
        downscaled={}
        for layer in self.layers:
            for variant in layer.variants:
                moving=[]
                for sp in variant.sprites:
                    if sp.sway or sp.bob or sp.kind=='lamp':
                        moving.append(sp)
                        continue
                    asset=self.lib.assets[sp.kind]
                    for map_kind in static_maps:
                        key=(sp.kind,map_kind)
                        sprite=downscaled.get(key)
                        if sprite is None:
                            raw=getattr(asset,map_kind)
                            sprite=pygame.transform.scale(raw,(raw.get_width()//2,raw.get_height()//2))
                            downscaled[key]=sprite
                        r=sprite.get_rect(bottomleft=(sp.x,sp.y))
                        getattr(variant,map_kind).blit(sprite,r)
                variant.sprites=moving



    def _asset_box_low(self, kind, x, y):
        asset=self.lib.assets[kind]
        w=max(1, asset.image.get_width()//2)
        h=max(1, asset.image.get_height()//2)
        return pygame.Rect(int(x), int(y-h), int(w), int(h))

    def _sprite_priority(self, kind):
        order={
            'tree_blossom':5,'tree_copper':5,
            'lantern_sign':4,
            'bike_rack':3,'hedge':2,'planter_stone':1,
        }
        return order.get(kind, 0)

    def _filter_decor_sprites(self, sprites, max_count=5):
        """Regra anti-poluição/anti-sobreposição para decoração.

        - mantém poucos objetos por chunk;
        - impede interseção entre bounding boxes;
        - exige folga extra para objetos altos;
        - evita objeto baixo escondido atrás de árvore/poste.
        """
        placed=[]
        tall_kinds={'tree_blossom','tree_copper','lantern_sign'}
        ground_kinds={'tree_blossom','tree_copper','bike_rack','hedge','planter_stone'}
        # ordem: maiores prioridades primeiro, depois esquerda->direita
        ordered=sorted(sprites, key=lambda sp:(-self._sprite_priority(sp.kind), sp.x, sp.y))
        for sp in ordered:
            rect=self._asset_box_low(sp.kind, sp.x, sp.y)
            ok=True
            for other, orect in placed:
                # margem horizontal base
                gap=10
                if sp.kind in tall_kinds or other.kind in tall_kinds:
                    gap=18
                expanded=pygame.Rect(orect.x-gap, orect.y, orect.w+gap*2, orect.h)
                if rect.colliderect(expanded):
                    ok=False
                    break
                # evita esconder objeto baixo atrás de alto, mesmo sem colisão direta
                if (sp.kind in ground_kinds and other.kind in tall_kinds) or (other.kind in ground_kinds and sp.kind in tall_kinds):
                    if abs(rect.centerx-orect.centerx) < 20 and abs(rect.bottom-orect.bottom) < 4:
                        ok=False
                        break
            if ok:
                placed.append((sp, rect))
            if len(placed) >= max_count:
                break
        # desenha da esquerda para a direita para estabilidade visual
        return [sp for sp,_ in sorted(placed, key=lambda item:(item[0].x, item[0].y, self._sprite_priority(item[0].kind)))]

    def _draw_storefront_boost(self, img, mat, x, y, w):
        # vitrine/porta discretas com volume de pixel art premium
        door_w=max(8, min(12, w//4))
        door_x=x+w//2-door_w//2
        pygame.draw.rect(img,(68,63,78),(door_x,y,door_w,15))
        pygame.draw.rect(img,(116,148,160),(door_x+2,y+2,door_w-4,10))
        pygame.draw.line(img,(235,239,232),(door_x+3,y+3),(door_x+3,y+11),1)
        pygame.draw.rect(img,(208,193,171),(door_x+door_w-3,y+8,1,2))
        # janelas laterais
        side=max(7,(w-door_w-8)//2)
        if side>=7:
            for wx in (x+3, x+w-side-3):
                pygame.draw.rect(img,(91,87,98),(wx,y+1,side,12))
                pygame.draw.rect(img,(170,201,214),(wx+1,y+2,side-2,10))
                pygame.draw.line(img,(236,238,227),(wx+2,y+3),(wx+2,y+10),1)
                pygame.draw.line(img,(124,139,149),(wx+side//2,y+2),(wx+side//2,y+11),1)
                pygame.draw.line(img,(124,139,149),(wx+1,y+7),(wx+side-2,y+7),1)
        pygame.draw.line(mat,(153,144,136),(x+1,y+15),(x+w-2,y+15),1)

    def _refine_structure_pass(self, variant):
        img, mat, norm, fx = variant.image, variant.material, variant.normal, variant.fxmask
        # Detalhe de calçada: juntas mais finas e tampas de inspeção
        for x in range(12, LOW_W-10, 34):
            pygame.draw.line(img,(189,180,168),(x,232),(x+10,232),1)
            pygame.draw.line(img,(92,92,102),(x,246),(x+6,246),1)
        for x in (95, 286):
            pygame.draw.rect(img,(91,95,104),(x,242,7,3))
            pygame.draw.line(img,(128,136,144),(x+1,242),(x+5,242),1)
        # reflexo leve no asfalto/guia
        pygame.draw.line(img,(140,145,153),(0,237),(LOW_W-1,237),1)
        pygame.draw.line(norm,(112,128,252),(0,237),(LOW_W-1,237),1)
        pygame.draw.line(mat,(128,127,125),(0,237),(LOW_W-1,237),1)
        pygame.draw.rect(fx,(255,204,138,9),(0,233,LOW_W,2))

    def _facade_details(self,maps,x,y,w,bottom,seed,palette):
        super()._facade_details(maps,x,y,w,bottom,seed,palette)
        img,fx,mat,norm=maps['image'],maps['fxmask'],maps['material'],maps['normal']
        hi,lo,lit=palette
        kind=seed%5
        top=y
        if w<15 or bottom-y<40:return
        dark=self._shade(lo,.62)
        bright=self._lit(hi,.34)
        # moldura superior + materiais
        pygame.draw.rect(img,dark,(x+2,top+3,max(1,w-4),2))
        pygame.draw.line(img,bright,(x+3,top+1),(x+w-4,top+1),1)
        if kind in (0,3):
            for xx in range(x+7,x+w-7,12):
                pygame.draw.rect(img,(114,99,108),(xx,top+4,4,3))
                pygame.draw.rect(img,bright,(xx+1,top+4,2,1))
            for yy in range(top+12,bottom-30,19):
                pygame.draw.rect(img,self._shade(hi,.86),(x+4,yy,2,5))
                pygame.draw.rect(img,self._lit(hi,.13),(x+w-7,yy,2,5))
        elif kind in (1,2):
            for row,yy in enumerate(range(top+8,bottom-25,11)):
                for xx in range(x+4+(row%2)*4,x+w-6,11):
                    pygame.draw.line(img,self._shade(hi,.82),(xx,yy),(min(xx+5,x+w-6),yy),1)
                    if kind==2:
                        pygame.draw.rect(img,self._lit(lo,.14),(xx+2,yy+3,2,1))
        else:
            for xx in (x+5,x+w-8):
                pygame.draw.rect(img,self._shade(hi,.8),(xx,top+7,3,max(1,bottom-top-39)))
                pygame.draw.line(img,bright,(xx,top+7),(xx,bottom-33),1)
            pygame.draw.rect(img,bright,(x+4,top+9,w-8,2))
        # piso térreo reforçado: vitrines, portas e letreiro limpo
        if bottom>210 and w>=32:
            awn_y=bottom-31
            pygame.draw.line(img,dark,(x+6,awn_y+5),(x+w-7,awn_y+5),1)
            pygame.draw.line(img,(240,216,187),(x+7,awn_y+1),(x+w-8,awn_y+1),1)
            pygame.draw.rect(fx,(250,201,143,20),(x+8,bottom-20,max(1,w-16),6))
            for x0 in (x+4,x+w-6):
                pygame.draw.rect(mat,(148,134,132),(x0,bottom-24,2,12))
            self._draw_storefront_boost(img, mat, x+4, bottom-20, w-8)
        # floreiras integradas às janelas (poucas para não poluir)
        if w>=30:
            for wx in range(x+7, x+w-10, 18):
                wy = top + 22 + ((wx+x+seed)%2)*14
                if wy < bottom-42:
                    pygame.draw.rect(img,(135,95,76),(wx,wy,8,2))
                    pygame.draw.rect(img,(72,132,88),(wx+1,wy-2,6,2))
                    pygame.draw.rect(img,(244,179,165),(wx+1,wy-3,2,2))
                    pygame.draw.rect(img,(252,222,126),(wx+4,wy-3,2,2))
        for xx in (x+2,x+w-4):
            pygame.draw.rect(norm,(107,126,254),(xx,top+6,1,max(1,bottom-top-17)))

    def _make_near_variant(self,idx):
        v=super()._make_near_variant(idx)
        img,mat,geom=v.image,v.material,v.geometry
        for x in range(0,LOW_W,14):
            pygame.draw.line(img,(74,76,87),(x+1,248),(x+5,248),1)
            pygame.draw.line(img,(226,211,191),(x+1,232),(x+8,232),1)
            if x%42==0:
                pygame.draw.rect(img,(70,79,85),(x+3,239,8,3))
                pygame.draw.line(img,(125,134,139),(x+3,239),(x+10,239),1)
        seq=(26,142,252,384)
        for n,x in enumerate(seq):
            pygame.draw.rect(img,(114,103,93),(x,225,24,4))
            pygame.draw.rect(img,(73,120,83),(x+2,220,20,5))
            pygame.draw.rect(img,(116,195,124),(x+7,219,5,2))
            pygame.draw.rect(mat,(119,115,104),(x,225,24,4))
        # composição decorativa mais rica, mas com regra anti-acúmulo
        candidates=[]
        if idx%4==0:
            candidates.extend((
                SpriteInstance('tree_blossom',60,230,sway=.72,phase=.4+idx),
                SpriteInstance('planter_stone',146,230),
                SpriteInstance('hedge',214,230),
                SpriteInstance('bike_rack',330,230),
            ))
        elif idx%4==1:
            candidates.extend((
                SpriteInstance('tree_copper',86,230,sway=.68,phase=.7+idx),
                SpriteInstance('planter_stone',202,230),
                SpriteInstance('hedge',294,230),
                SpriteInstance('bike_rack',360,230),
            ))
        elif idx%4==2:
            candidates.extend((
                SpriteInstance('hedge',62,230),
                SpriteInstance('tree_blossom',154,230,sway=.72,phase=.55+idx),
                SpriteInstance('planter_stone',286,230),
                SpriteInstance('bike_rack',352,230),
            ))
        else:
            candidates.extend((
                SpriteInstance('planter_stone',72,230),
                SpriteInstance('bike_rack',142,230),
                SpriteInstance('tree_copper',286,230,sway=.70,phase=.85+idx),
                SpriteInstance('hedge',364,230),
            ))
        # lanternas permanecem ancoradas às fachadas
        for x in (154,336):
            pygame.draw.rect(img,(73,67,80),(x,186,2,34))
            pygame.draw.rect(geom,(0,205,0),(x,186,2,34))
            pygame.draw.rect(mat,(125,112,116),(x,186,2,34))
            candidates.append(SpriteInstance('lantern_sign',x,202))
        v.sprites=self._filter_decor_sprites(candidates, max_count=5)
        self._refine_structure_pass(v)
        return v

    def _make_far_variant(self,idx):
        v=super()._make_far_variant(idx)
        img=v.image
        for x in range(3,LOW_W,49):
            pygame.draw.line(img,(170,180,218),(x,155),(x,165),1)
            pygame.draw.rect(img,(235,231,217),(x-1,154,3,2))
        return v

    def _make_mid_variant(self,idx):
        v=super()._make_mid_variant(idx)
        img,geom,mat=v.image,v.geometry,v.material
        pygame.draw.line(img,(209,216,235),(0,133),(LOW_W-1,133),1)
        for x in range(0,LOW_W,27):
            pygame.draw.line(img,(117,136,175),(x,135),(x,140),1)
            pygame.draw.line(geom,(0,180,0),(x,135),(x,140),1)
            pygame.draw.line(mat,(110,128,151),(x,135),(x,140),1)
        # pequenas luzes/placas presas ao viaduto, sem virar objetos flutuantes
        for x in range(14,LOW_W,54):
            pygame.draw.rect(img,(222,208,168),(x,130,6,2))
            pygame.draw.rect(img,(136,118,110),(x,132,6,1))
        return v

    def _make_fg_variant(self,idx):
        maps=self._blank_maps()
        sprites=[
            SpriteInstance('hedge',0,230,sway=.15,phase=.7+idx),
            SpriteInstance('hedge',LOW_W-30,230,sway=.12,phase=1.1+idx),
        ]
        sprites=self._filter_decor_sprites(sprites, max_count=2)
        return ChunkVariant(**maps,sprites=sprites)

    def _build_layers(self):
        return super()._build_layers()
