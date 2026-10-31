"""Floresta Densa 3.2 (v3.142): vegetação e clima ainda mais refinados.

Só a floresta: substitui horizonte sólido e copas circulares por árvores
orgânicas, plantas terrestres enraizadas, conjuntos temáticos e animação
vegetal leve ancorada no parallax. Tudo é desenhado nos chunks uma única vez;
nenhum PNG de fundo e nenhuma superfície grande por quadro.
"""
import math
import random
import pygame
from pixelrush_biomes2_v3138 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW, LH, WIDTH, _p, _line, _rect


class ModularBiomeScene(Previous):
    def __init__(self, biome):
        self._forest_anchors = {}
        self._forest_leaf_frames = ()
        super().__init__(biome)
        if biome == 'floresta':
            self._forest_leaf_frames = tuple(self._leaf_anim_frame(i) for i in range(4))

    # Evitar introduzir antigos círculos, salpicos soltos ou luzes retas no céu.
    def _premium_polish_layers(self):
        if self.biome != 'floresta':
            return super()._premium_polish_layers()

    def _combo_polish_layers(self):
        if self.biome != 'floresta':
            return super()._combo_polish_layers()

    def _make_chunk(self, layer, index):
        if self.biome != 'floresta':
            return super()._make_chunk(layer, index)
        return self._forest_chunk(layer, index)

    @staticmethod
    def _leaf_anim_frame(phase):
        """Pequena ponta de samambaia: 4 poses pré-renderizadas em baixa resolução."""
        s=pygame.Surface((13,13),pygame.SRCALPHA)
        sway=(-2,0,2,0)[phase]
        stem=(7,12)
        pygame.draw.line(s,(75,113,70),stem,(7+sway,2),1)
        for k in (3,5,7,9):
            xx=7+int(sway*(12-k)/12)
            pygame.draw.line(s,(87,158,83),(xx,k),(xx-3,k-2),1)
            pygame.draw.line(s,(156,203,111),(xx,k),(xx+3,k-3),1)
        pygame.draw.rect(s,(179,217,127),(7+sway,1,2,2))
        return pygame.transform.scale(s,(26,26))


    @staticmethod
    def _blit_safe(dest, src, x, y):
        r = src.get_rect(topleft=(int(x), int(y)))
        dr = dest.get_rect()
        if r.right <= 0 or r.left >= dr.width or r.bottom <= 0 or r.top >= dr.height:
            return
        area = r.clip(dr)
        dest.blit(src, area.topleft, pygame.Rect(area.x-r.x, area.y-r.y, area.width, area.height))

    def _small_tree_far(self, s, x, ground, height, seed, shape='cedar'):
        """Árvore distante menor, com silhueta mais rica e sem parecer cortada."""
        rng = random.Random(seed)
        bark=(72,95,84); barkhi=(108,138,125); barkdark=(48,69,63)
        x=int(x); ground=int(ground); height=int(height)
        top=ground-height
        trunk_w=3
        lean=rng.choice((-3,-2,-1,1,2))
        topx=x+lean
        pygame.draw.line(s,barkdark,(x+1,ground),(topx+1,top+14),trunk_w+1)
        pygame.draw.line(s,bark,(x,ground-1),(topx,top+14),trunk_w)
        pygame.draw.line(s,barkhi,(x-1,ground-6),(topx-1,top+18),1)
        for yy in range(top+18, ground-9, 6):
            pygame.draw.line(s,barkdark,(x-1,yy),(x+2,yy-1),1)
        for side in (-1,1):
            sy=ground-int(height*(0.42 if side<0 else 0.56))
            sx=x+int(lean*(0.42 if side<0 else 0.56))
            dx=side*(7+rng.randint(0,3)); dy=-(7+rng.randint(0,4))
            pygame.draw.line(s,bark,(sx,sy),(sx+dx,sy+dy),2)
            pygame.draw.line(s,barkhi,(sx-1,sy-1),(sx+dx-1,sy+dy),1)
        leaflight=2
        radius=13 if shape=='cedar' else 15
        cx=topx; cy=top+20
        self._crown(s,cx-8,cy+4,max(8,radius-4),10,seed+10,leaflight,'cedar' if shape=='cedar' else 'oak')
        self._crown(s,cx+7,cy+5,max(8,radius-5),10,seed+11,leaflight,'cedar' if shape=='cedar' else 'oak')
        self._crown(s,cx,cy-6,max(10,radius),15,seed+12,leaflight,'cedar' if shape=='cedar' else 'oak')
        if shape=='cedar':
            self._crown(s,cx+2,cy-18,max(7,radius-6),12,seed+13,leaflight,'cedar')
        else:
            self._crown(s,cx,cy-16,max(8,radius-7),10,seed+13,leaflight,'oak')
        for i in range(2):
            vx=cx+(-8+i*10); vy=cy+rng.randrange(4,11); length=rng.randint(5,9)
            pygame.draw.line(s,(89,138,115),(vx,vy),(vx+1,vy+length),1)

    def _mist_patch(self, surf, x, y, w, h, color):
        for k in range(0, h, 3):
            a = max(6, color[3] - k*2)
            pygame.draw.ellipse(surf, (color[0], color[1], color[2], a), (x, y+k, w, max(2, h-k)))

    def _crown(self, surf, cx, cy, rx, ry, seed, light=0, kind='oak'):
        """Copa orgânica premium: massas assimétricas, bordas dentadas e miolos ricos."""
        rng=random.Random(seed)
        base=[(29,75,57),(43,107,66),(68,135,77),(104,163,94),(155,198,118)]
        if light == 1:
            base=[(57,98,91),(67,125,108),(89,151,118),(124,174,133),(166,207,158)]
        elif light == 2:
            base=[(69,104,106),(78,122,111),(102,146,117),(140,175,130),(172,196,150)]
        # base em várias ilhas dentadas, sem elipse limpa.
        centers=[(cx-rx//2, cy+ry//5, max(9,rx-7), max(8,ry-6)),
                 (cx+rx//2, cy+ry//7, max(10,rx-5), max(8,ry-5)),
                 (cx, cy-ry//2, max(12,rx-2), max(10,ry-2))]
        if kind=='cedar':
            centers.append((cx+3, cy-ry-6, max(8,rx-10), max(9,ry-8)))
        for n,(mx,my,mrx,mry) in enumerate(centers):
            poly=[]
            steps=22
            for j in range(steps):
                a=math.tau*j/steps
                jag=0.78 + 0.24*rng.random() + 0.12*math.sin(a*4+seed*0.13+n)
                xx=int(mx+mrx*math.cos(a)*jag)
                yy=int(my+mry*math.sin(a)*jag)
                if kind=='cedar':
                    xx += int((yy-my)*0.12)
                poly.append((xx,yy))
            pygame.draw.polygon(surf, base[min(n,2)], poly)
        # volumes internos / highlights quebrados
        for i in range(18):
            px=cx+rng.randrange(-rx+4,max(-rx+5,rx-3))
            py=cy+rng.randrange(-ry,max(-ry+1,ry-2))
            if (px-cx)**2/(max(1,rx*rx)) + (py-cy)**2/(max(1,ry*ry)) > 1.18:
                continue
            col=base[3] if i%3 else base[4]
            pygame.draw.line(surf,col,(px,py),(px+2+(i%2),py),1)
            if i%5==0:
                pygame.draw.line(surf,base[2],(px-1,py+1),(px+1,py+1),1)
        # serrilhas/folhas periféricas
        for i in range(18):
            ang=math.tau*i/18.0
            edge_x=int(cx+math.cos(ang)*(rx+1))
            edge_y=int(cy+math.sin(ang)*(ry+1))
            pygame.draw.line(surf,base[1 if i%2 else 2],(edge_x,edge_y),(edge_x+rng.randint(-3,3),edge_y+rng.randint(-2,2)),1)
    def _tree(self,s,x,ground,height,seed,depth='mid',shape='broad'):
        """Árvore premium com tronco mais rico, ramificações e copa profissional."""
        rng=random.Random(seed)
        x=int(x); ground=int(ground); height=int(height)
        top=ground-height
        if depth=='far':
            bark=(65,91,83); barkhi=(91,125,110); barkdark=(45,69,63); leaflight=2
            trunk_w=4
        else:
            bark=(84,60,49) if depth=='mid' else (96,69,55)
            barkhi=(145,104,69) if depth=='mid' else (164,120,79)
            barkdark=(49,37,31)
            leaflight=0 if depth=='mid' else 1
            trunk_w=6 if depth=='mid' else 5
        twist=rng.choice((-6,-4,-2,3,5))
        topx=x+twist
        # tronco principal com contrafortes
        pygame.draw.line(s,barkdark,(x+2,ground),(topx+1,top+14),trunk_w+2 if depth!='far' else trunk_w)
        pygame.draw.line(s,bark,(x,ground-1),(topx,top+15),trunk_w)
        pygame.draw.line(s,barkhi,(x-1,ground-8),(topx-2,top+18),2)
        for side in (-1,1):
            pts=[(x,ground-8),(x+side*4,ground-4),(x+side*9,ground-1),(x+side*14,ground+1)]
            pygame.draw.lines(s,bark,False,pts,3 if depth!='far' else 2)
            pygame.draw.line(s,barkhi,(x+side*3,ground-5),(x+side*10,ground-1),1)
        # fissuras de casca
        for yy in range(top+18,ground-12,7):
            pygame.draw.line(s,barkdark,(x-1,yy),(x+3,yy-2),1)
            if yy%14==0:
                pygame.draw.line(s,barkhi,(x+1,yy+1),(x+4,yy),1)
        # galhos principais
        branch_specs=[(-1,.38,12,18), (1,.34,13,21), (-1,.56,16,16), (1,.64,18,14)]
        for k,(side,d,dxmag,dymag) in enumerate(branch_specs):
            sy=ground-int(height*d)
            sx=x+int(twist*d)
            dx=side*(dxmag+rng.randint(-2,2))
            dy=-dymag+rng.randint(-2,2)
            width=max(2,4-k//2) if depth!='far' else max(1,3-k//2)
            pygame.draw.line(s,bark,(sx,sy),(sx+dx,sy+dy),width)
            pygame.draw.line(s,barkhi,(sx-1,sy-1),(sx+dx-1,sy+dy+1),1)
            # bifurcação curta na ponta
            pygame.draw.line(s,barkdark,(sx+dx,sy+dy),(sx+dx+side*5,sy+dy-5),1)
            if k%2==0:
                pygame.draw.line(s,barkdark,(sx+dx,sy+dy),(sx+dx-side*3,sy+dy-4),1)
        # copas em massas irregulares mais ricas
        radius=29 if depth=='mid' else 18 if depth=='far' else 23
        if shape=='umbrella': radius += 8
        elif shape=='cedar': radius -= 2
        cx=topx; cy=top+18
        self._crown(s,cx-14,cy+6,max(11,radius-6),15,seed+10,leaflight)
        self._crown(s,cx+14,cy+5,max(12,radius-4),17,seed+11,leaflight)
        self._crown(s,cx,cy-10,max(15,radius),22 if shape!='cedar' else 20,seed+12,leaflight,'cedar' if shape=='cedar' else 'oak')
        if shape=='umbrella':
            self._crown(s,cx,cy-20,max(10,radius-9),12,seed+13,leaflight)
        elif shape=='cedar':
            self._crown(s,cx+4,cy-26,max(8,radius-11),16,seed+14,leaflight,'cedar')
        # cipós curtos e discretos
        for i in range(2 if depth=='far' else 3):
            vx=cx+(-18+i*14)
            vy=cy+rng.randrange(8,16)
            length=rng.randint(7,14)
            pygame.draw.line(s,(55,112,72) if depth!='far' else (82,134,123),(vx,vy),(vx+2,vy+length),1)
            pygame.draw.line(s,(131,173,94),(vx+2,vy+max(2,length-3)),(vx+4,vy+max(1,length-5)),1)
    @staticmethod
    def _fern(s,x,y,seed,scale=1):
        rng=random.Random(seed)
        for side in (-1,1):
            stem=(x,y)
            length=int(rng.randint(10,16)*scale)
            endpoint=(x+side*int(length*.73),y-length)
            pygame.draw.line(s,(57,111,74),stem,endpoint,2)
            for k in range(2,6):
                xx=x+side*int(length*.73*k/6)
                yy=y-int(length*k/6)
                pygame.draw.line(s,(115,176,95),(xx,yy),(xx+side*4,yy-4),1)
                pygame.draw.line(s,(176,208,119),(xx,yy),(xx-side*2,yy-3),1)
        pygame.draw.line(s,(64,122,73),(x,y),(x,y-18*scale),1)
        for i in range(4):
            yy=y-int(6+i*3*scale)
            pygame.draw.line(s,(126,184,95),(x,yy),(x+(-1)**i*5,yy-3),1)

    def _shrub(self,s,x,y,seed,style=0):
        rng=random.Random(seed)
        dark=(31,83,65);med=(58,125,74);light=(123,185,99)
        # folhas dentadas e triangulares, nada de círculos.
        blobs=[(-14,-3,12,11),(0,-8,15,15),(12,-3,12,12)]
        for j,(dx,dy,ww,hh) in enumerate(blobs):
            px=x+dx;py=y+dy
            pygame.draw.polygon(s,(dark,med,(69,146,86))[j],
                 [(px-ww,py+hh),(px-ww+2,py-3),(px-5,py-8),(px,py-hh),
                  (px+6,py-5),(px+ww,py-2),(px+ww-2,py+hh)])
        for i in range(15):
            px=x+rng.randrange(-19,20);py=y+rng.randrange(-17,5)
            if abs(px-x)+abs(py-(y-6))>27:continue
            pygame.draw.line(s,light if i%3 else (172,211,125),(px,py),(px+2,py),1)
        if style==1:
            for i in (-8,8):
                pygame.draw.line(s,(146,183,97),(x+i,y-4),(x+i+3,y-7),1)
        if style==2:
            for i in (-11,2,11):
                pygame.draw.rect(s,(215,163,174),(x+i,y-7,2,2))

    def _bigleaf(self,s,x,y,seed):
        rng=random.Random(seed)
        for side in (-1,1):
            size=rng.randint(11,19)
            px=x+side*(size//2)
            tip=(x+side*size,y-size-rng.randint(0,7))
            pygame.draw.line(s,(56,103,67),(x,y),tip,2)
            pygame.draw.polygon(s,(47,112,82) if side<0 else (76,150,91),
                [(x,y-4),(px-4,y-size//2),(tip[0],tip[1]),(px+3,y-size//2),(x+2,y-2)])
            pygame.draw.line(s,(172,211,128),(x,y-4),tip,1)
            for i in range(2,5):
                xx=x+side*i*3
                yy=y-i*3
                pygame.draw.line(s,(95,165,105),(xx,yy),(xx+side*3,yy-2),1)

    @staticmethod
    def _mushroom(s,x,y,seed):
        cc=(201,117,100) if seed%3 else (220,175,112)
        _rect(s,(213,204,170),x-1,y-5,3,5)
        pygame.draw.polygon(s,(130,74,69),[(x-5,y-5),(x-2,y-10),(x+3,y-11),(x+7,y-5)])
        pygame.draw.polygon(s,cc,[(x-4,y-6),(x-2,y-11),(x+2,y-12),(x+6,y-6)])
        _rect(s,(246,211,152),x-1,y-10,2,1)

    @staticmethod
    def _rock(s,x,y,seed):
        col=(91,104,91) if seed%2 else (112,115,100)
        pygame.draw.polygon(s,(57,70,65),[(x-9,y),(x-7,y-7),(x-2,y-10),(x+8,y-6),(x+10,y)])
        pygame.draw.polygon(s,col,[(x-7,y-2),(x-4,y-7),(x+3,y-8),(x+7,y-5),(x+8,y-2)])
        _line(s,(155,169,130),x-4,y-7,x+2,y-8)
        if seed%3==0:_line(s,(60,125,82),x-4,y-2,x+2,y-3)

    def _water(self,s,x,y,w,seed):
        rng=random.Random(seed)
        pygame.draw.polygon(s,(51,96,108),[(x,y+3),(x+13,y),(x+w-11,y+1),(x+w,y+6),(x+w-7,y+13),(x+7,y+12)])
        pygame.draw.polygon(s,(76,153,157),[(x+5,y+5),(x+15,y+3),(x+w-14,y+5),(x+w-6,y+8),(x+w-15,y+10),(x+9,y+10)])
        for i in range(8):
            xx=x+rng.randrange(8,max(9,w-12))
            yy=y+rng.randrange(5,10)
            _line(s,(175,220,196),xx,yy,xx+rng.randrange(3,9),yy)
        for cx in (x+4,x+w-9):
            pygame.draw.line(s,(55,109,76),(cx,y+5),(cx+1,y-8),2)
            pygame.draw.polygon(s,(119,167,89),[(cx-5,y-7),(cx,y-15),(cx+5,y-7)])

    def _ruins(self,s,x,y,w,seed):
        rng=random.Random(seed)
        # arco parcialmente desmoronado, integrado a raízes e plantas
        _rect(s,(68,85,73),x,y-42,8,42)
        _rect(s,(130,142,114),x+2,y-39,4,36)
        _rect(s,(74,86,77),x+w-8,y-32,8,32)
        pygame.draw.polygon(s,(129,136,115),[(x-3,y-45),(x+w//3,y-47),(x+w-9,y-34),(x+w-6,y-29),(x+2,y-36)])
        for dx in range(4,w-7,9):
            yy=y-45+(dx*9//w)
            _line(s,(177,184,148),x+dx,yy,x+dx+4,yy,1)
            if dx%3==0:_line(s,(43,67,55),x+dx+1,yy+1,x+dx+3,yy+6,1)
        for i in range(4):
            rx=x+rng.randint(0,w)
            _line(s,(55,121,73),rx,y-40,rx+1,y-17-rng.randint(0,9))
        self._shrub(s,x,y,seed+7)
        self._fern(s,x+w-7,y,seed+18)

    def _ground(self,s,layer,seed):
        """Contorno contínuo abaixo do jogo; evita a faixa verde no horizonte."""
        rng=random.Random(seed)
        # Não há qualquer retângulo opaco cobrindo o céu.
        if layer=='far':
            return
        if layer=='mid':
            pygame.draw.polygon(s,(58,102,77),[(0,218),(30,216),(67,217),(110,216),(167,216),(LW,218),(LW,236),(0,236)])
            _line(s,(115,165,109),0,217,LW,217)
            return
        pygame.draw.polygon(s,(73,119,76),[(0,227),(21,225),(58,226),(93,224),(151,226),(191,225),(LW,226),(LW,250),(0,250)])
        _line(s,(151,186,119),0,229,LW,229,2)
        # trilha de terra fica abaixo do bordo, sem plantas voando na pista.
        _rect(s,(103,78,58),0,233,LW,17)
        _line(s,(149,113,76),0,234,LW,234,2)
        for j in range(32):
            x=rng.randrange(4,LW-4);y=rng.randrange(237,249)
            col=(135,99,70) if j%2 else (76,67,53)
            _rect(s,col,x,y,3+(j%3),1)
        for j in range(8):
            x=rng.randrange(7,LW-8)
            _line(s,(53,82,50),x,230,x+3,230,1)

    def _far_ridge(self,s,index):
        """Linha irregular, com vazios transparentes de céu entre copas.

        A linha de base toca y=217 e não forma mais um painel a y=132.
        Todos os chunks se unem na altura da trilha inferior.
        """
        pts=[]
        # Todos os tiles começam/terminam em y=193. A seleção embaralhada de
        # variantes do parallax nunca cria um degrau na linha do horizonte.
        for x in range(0,LW+1,3):
            u=x/LW*math.tau
            valley=(1-math.cos(u))*.5
            height=193-(14+(index%4)*3)*valley-(4+index%3)*math.sin(u*2)
            pts.append((x,int(height)))
        poly=pts+[(LW,219),(0,219)]
        pygame.draw.polygon(s,(83,124,117),poly)
        for x,y in pts[::5]:
            _line(s,(117,155,141),x,y,x+4,y+2)

    def _forest_chunk(self,layer,index):
        rng=random.Random(140000+index*131+{'far':0,'mid':1000,'near':2000}[layer])
        s=pygame.Surface((LW,LH),pygame.SRCALPHA)
        if layer=='far':
            self._far_ridge(s,index)
            far_positions=(28, 70, 116, 162, 196)
            for i,x in enumerate(far_positions):
                hh=rng.randint(46,76)
                self._small_tree_far(s,x,213,hh,14010+index*47+i,'cedar' if i%2 else 'broad')
            for i in range(7):
                x=rng.randrange(10,LW-18); y=rng.randrange(201,214)
                _line(s,(120,160,150),x,y,x+rng.randint(4,10),y,1)
        elif layer=='mid':
            self._ground(s,'mid',140100+index)
            theme=index%8
            if theme in (0,4):
                self._tree(s,42,216,103,14100+index,'mid','umbrella')
                self._tree(s,171,217,116,14200+index,'mid','cedar')
                self._shrub(s,98,214,index+150,1)
            elif theme in (1,5):
                self._tree(s,44,217,108,14300+index,'mid','broad')
                self._tree(s,179,217,92,14400+index,'mid','umbrella')
                self._ruins(s,82,217,62,14500+index)
            elif theme in (2,6):
                self._tree(s,48,218,100,14600+index,'mid','cedar')
                self._tree(s,171,217,99,14700+index,'mid','umbrella')
                self._water(s,80,201,66,14800+index)
                self._fern(s,148,216,14900+index)
            else:
                self._tree(s,42,216,95,15000+index,'mid','umbrella')
                self._tree(s,101,216,108,15100+index,'mid','cedar')
                self._tree(s,173,216,103,15200+index,'mid','broad')
            side_plants=(22,51,174,202)
            for j,x in enumerate(side_plants):
                if j%2:self._fern(s,x,217,15300+index*17+j,1)
                else:self._shrub(s,x,216,15400+index*17+j)
            if theme in (1,6):
                self._mushroom(s, 27 if theme==1 else 198, 214, 15500+index)
        else:
            self._ground(s,'near',15600+index)
            edge_sets=((14,31,44,180,196,209),
                       (18,34,52,173,191,208),
                       (15,28,47,177,194,206),
                       (20,38,58,168,187,204),
                       (16,33,49,179,198,211))
            placements=edge_sets[index%len(edge_sets)]
            theme=index%5
            # Primeiro desenha árvores/rochas mais ao fundo do primeiro plano.
            if theme in (0,3):
                self._tree(s,28,223,66,16000+index,'near','cedar')
                self._tree(s,196,223,72,16100+index,'near','umbrella')
            elif theme==1:
                self._rock(s,30,225,16200+index)
                self._tree(s,198,223,68,16300+index,'near','broad')
            elif theme==2:
                self._tree(s,26,223,70,16400+index,'near','umbrella')
                self._rock(s,198,225,16500+index)
            else:
                self._rock(s,29,225,16600+index)
                self._rock(s,197,225,16700+index)
            # Depois a vegetação próxima, para nunca ficar atrás das árvores.
            for i,x in enumerate(placements):
                if i in (0,3): self._bigleaf(s,x,222,15700+index*20+i)
                elif i in (1,4): self._fern(s,x,223,15800+index*20+i,1.0)
                else: self._shrub(s,x,221,15900+index*20+i,style=1 if x<70 else 0)
            # reforços baixos de borda, sem invadir a rua
            self._fern(s, 12 + (index%2)*3, 224, 16800+index, .86)
            self._fern(s, 211 - (index%3)*2, 224, 16900+index, .84)
            self._shrub(s, 24, 222, 17000+index, style=0)
            self._shrub(s, 199, 222, 17100+index, style=1)
            self._forest_anchors[index]=tuple((x, 216-(i%2)*2) for i,x in enumerate((placements[0],placements[2],placements[3],placements[5])))
        return s
    def _overlay_forest(self,surf,frame,climate,night):
        # Clima vivo e leve: folhas, pólen, bruma e chuva com mais identidade.
        wind=climate in ('vento','vento_folhas','tempestade_vento','tempestade')
        storm=climate in ('tempestade','tempestade_vento','chuva')
        rain=climate in ('chuva','tempestade')
        pollen=climate=='polen'
        travel=getattr(self,'_forest_travel',0.0)
        off=max(0.,travel)*.52*.5
        first=int(off//LW);shift=int(off%LW)
        count=len(self._layers['near'])
        # folhas/samambaias animadas ancoradas nas laterais
        for j in range(2):
            index=(first+j)%count
            for i,(ax,ay) in enumerate(self._forest_anchors.get(index,())):
                xx=int((j*LW-shift+ax)*2)
                yy=int((ay-13)*2)
                if not (-30<=xx<=455):continue
                phase=(frame//(6 if wind else 15)+i+index)%4
                surf.blit(self._forest_leaf_frames[phase],(xx-13,yy))
        # bruma baixa suave em manhã úmida / chuva
        if rain or (night < .18 and not pollen):
            for i in range(2 if self.visual_quality else 1):
                x = int((i*170 - frame*0.35) % (WIDTH + 80)) - 40
                self._mist_patch(surf, x, 300 + i*34, 120, 28, (185, 215, 198, 18 if rain else 12))
        # folhas carregadas pelo vento
        if wind:
            for i in range(10 if self.visual_quality else 6):
                x=int((i*61+frame*2.1)%(WIDTH+26))-13
                y=214+int(17*math.sin((frame+i*23)*.05))+(i%4)*22
                col=(132,181,92) if i%3 else (181,206,110)
                pygame.draw.line(surf,col,(x,y),(x+5,y+2),1)
                if i%2==0:
                    pygame.draw.line(surf,(82,133,74),(x+1,y+1),(x+3,y+3),1)
        elif pollen:
            for i in range(9 if self.visual_quality else 5):
                x=int((i*71+frame*.55)%(WIDTH+20))-4
                y=136+(i*29+frame//4)%190
                pygame.draw.circle(surf,(226,221,156),(x,y),1)
                if i%3==0:
                    pygame.draw.circle(surf,(247,236,171),(x+2,y-1),1)
        # chuva da floresta: mais vertical e suave
        if storm:
            for i in range(12 if self.visual_quality else 7):
                x=int((i*41-frame*3.1)%(WIDTH+36))-18
                y=108+(i*37+frame*3)%320
                pygame.draw.line(surf,(133,182,186),(x,y),(x-4,y+12),1)
                if rain and i%3==0:
                    pygame.draw.line(surf,(169,208,204),(x+1,y+5),(x-2,y+15),1)
        # vaga-lumes / bioluminescência noturna discreta
        if night>.24:
            for i in range(11 if self.visual_quality else 6):
                x=20+(i*49+int(8*math.sin(frame*.027+i)))%412
                y=248+(i*31)%150+int(4*math.sin(frame*.055+i))
                col=(166,221,126) if (frame//17+i)%3 else (234,236,165)
                pygame.draw.circle(surf,col,(x,y),1 if i%4 else 2)
                if i%4==0:
                    pygame.draw.circle(surf,(*col,50),(x,y),3,1)

    def _overlay_forest_premium(self,surf,frame,climate,night):
        # Não duplicar efeitos de chuva/vento ou criar feixes retilíneos na tela.
        return

    def _overlay_forest_combo(self,surf,frame,climate,night):
        return

    def render_scene(self,target,travel,frame,night,climate,phase,foreground_only=False,map_kind='image'):
        if self.biome=='floresta':self._forest_travel=travel
        return super().render_scene(target,travel,frame,night,climate,phase,
                                    foreground_only=foreground_only,map_kind=map_kind)
