"""Floresta Densa 3.0 (v3.139): reconstrução artística das camadas.

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

    def _crown(self, surf, cx, cy, rx, ry, seed, light=0, kind='oak'):
        """Manchas assimétricas dentadas, jamais círculos simples.

        As copas possuem duas massas irregulares e raminhos nas bordas;
        textura limitada pela máscara da copa para não aparecer no céu.
        """
        rng=random.Random(seed)
        base=[(29,75,57),(43,107,66),(68,135,77),(104,163,94),(155,198,118)]
        if light == 1:
            base=[(57,98,91),(67,125,108),(89,151,118),(124,174,133),(166,207,158)]
        elif light == 2:
            base=[(69,104,106),(78,122,111),(102,146,117),(140,175,130),(172,196,150)]
        poly=[]
        steps=28
        for j in range(steps):
            a=math.tau*j/steps
            # variações amplas e serrilhas formam uma copa de verdade, não oval
            notch=rng.uniform(.77,1.08) * (1.0+.14*math.sin(a*5+seed*.1))
            xx=int(cx+rx*math.cos(a)*notch)
            yy=int(cy+ry*math.sin(a)*notch)
            if kind == 'cedar': xx+=int((yy-cy)*.18)
            poly.append((xx,yy))
        pygame.draw.polygon(surf,base[0],poly)
        # Internos irregulares e descentrados simulam luz de cima à esquerda.
        for i in range(8):
            dx=rng.randrange(-max(2,rx//2),max(3,rx//2))
            dy=rng.randrange(-max(2,ry//2),max(3,ry//2))
            wr=max(5,rx//2+rng.randint(-2,3))
            hr=max(4,ry//2+rng.randint(-2,3))
            pygame.draw.polygon(surf,base[1+i%3],[
                (cx+dx-wr,cy+dy+2),(cx+dx-wr//2,cy+dy-hr),
                (cx+dx+wr//3,cy+dy-hr-2),(cx+dx+wr,cy+dy-2),
                (cx+dx+wr//2,cy+dy+hr),(cx+dx-wr//3,cy+dy+hr)])
        # Pintar pontas somente onde existe folhagem de fato.
        # A máscara é derivada desta copa recém-pintada em um sprite temporário
        # na criação da imagem, evitando pontos suspensos no céu.
        for i in range(27):
            px=cx+rng.randrange(-rx+3,max(-rx+4,rx-2))
            py=cy+rng.randrange(-ry+3,max(-ry+4,ry-2))
            if (px-cx)**2/(rx*rx)+(py-cy)**2/(ry*ry) > .76:
                continue
            col=base[3] if i%4 else base[4]
            pygame.draw.line(surf,col,(px,py),(px+2+(i%2),py),1)
        for i in range(6):
            px=cx+rng.randrange(-rx+4,max(-rx+5,rx-3))
            py=cy+rng.randint(-max(2,ry//2),max(2,ry//2))
            pygame.draw.line(surf,base[2],(px,py),(px+3,py+1),1)

    def _tree(self,s,x,ground,height,seed,depth='mid',shape='broad'):
        """Árvore ramificada com casca, raízes e massas de folhas sem elipses."""
        rng=random.Random(seed)
        x=int(x); ground=int(ground);height=int(height)
        top=ground-height
        if depth=='far':
            bark=(65,91,83);barkhi=(91,125,110)
            leaflight=2
        else:
            bark=(74,54,47);barkhi=(133,95,65)
            leaflight=0 if depth=='mid' else 1
        twist=rng.choice((-5,-3,2,4))
        topx=x+twist
        # galhos ramificados por baixo, sem flutuar.
        pygame.draw.line(s,(37,55,51) if depth=='far' else (39,40,35),(x+2,ground),(topx,top+11),8 if depth!='far' else 5)
        pygame.draw.line(s,bark,(x,ground-1),(topx-1,top+13),6 if depth!='far' else 4)
        pygame.draw.line(s,barkhi,(x-1,ground-7),(topx-2,top+16),2)
        for k,(side,d) in enumerate(((-1,.43),(1,.35),(-1,.68),(1,.60))):
            sy=ground-int(height*d)
            sx=x+int(twist*d)
            dx=side*(10+k*3)
            dy=-rng.randint(11,21)
            pygame.draw.line(s,bark,(sx,sy),(sx+dx,sy+dy),max(2,4-k//2))
            pygame.draw.line(s,barkhi,(sx-1,sy-1),(sx+dx-1,sy+dy+1),1)
        for side in (-1,1):
            pts=[(x,ground-7),(x+side*4,ground-3),(x+side*13,ground+1),(x+side*16,ground+1)]
            pygame.draw.lines(s,(76,57,44) if depth!='far' else bark,False,pts,3)
        for yy in range(top+17,ground-11,8):
            pygame.draw.line(s,(42,38,35) if depth!='far' else (69,100,91),(x-2,yy),(x+3,yy-2),1)
        # copa dominante assimétrica com múltiplos recortes.
        radius=28 if depth=='mid' else 19 if depth=='far' else 23
        if shape=='umbrella':radius+=7
        cx=topx;cy=top+17
        self._crown(s,cx-13,cy+5,max(11,radius-5),15,seed+10,leaflight)
        self._crown(s,cx+14,cy+3,max(12,radius-3),17,seed+11,leaflight)
        self._crown(s,cx-2,cy-11,max(14,radius),20 if shape=='umbrella' else 24,seed+12,leaflight)
        if shape=='cedar':
            self._crown(s,cx+5,cy-24,max(9,radius-8),17,seed+13,leaflight,'cedar')
        # cipós curtos presos a galhos e pontas pendentes.
        for i in range(3):
            vx=cx+(-21+i*20)
            vy=cy+rng.randrange(9,17)
            length=rng.randint(7,16)
            pygame.draw.line(s,(55,112,72) if depth!='far' else (82,134,123),(vx,vy),(vx+2,vy+length),1)
            if i!=1:pygame.draw.line(s,(131,173,94),(vx+2,vy+length-3),(vx+5,vy+length-5),1)

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
        rng=random.Random(139000+index*131+{'far':0,'mid':1000,'near':2000}[layer])
        s=pygame.Surface((LW,LH),pygame.SRCALPHA)
        if layer=='far':
            # Mata azul-esverdeada à distância, abertura de céu até as copas.
            self._far_ridge(s,index)
            for i,x in enumerate((35,76,129,181)):
                hh=rng.randint(45,84)
                self._tree(s,x,213,hh,13910+index*47+i,'far','cedar' if i%2 else 'broad')
            # recorte de neblina ao nível do solo, não faixa lisa.
            for i in range(11):
                x=rng.randrange(0,LW-9)
                y=rng.randrange(200,215)
                _line(s,(119,157,147),x,y,x+rng.randint(5,16),y,1)
        elif layer=='mid':
            self._ground(s,'mid',139100+index)
            theme=index%8
            if theme in (0,4):
                self._tree(s,45,216,99,14000+index,'mid','umbrella')
                self._tree(s,169,217,111,14100+index,'mid','cedar')
                self._shrub(s,105,216,index+150,1)
            elif theme in (1,5):
                self._tree(s,45,217,104,14200+index,'mid','broad')
                self._tree(s,177,217,86,14300+index,'mid','umbrella')
                self._ruins(s,79,217,64,14400+index)
            elif theme in (2,6):
                self._tree(s,48,218,97,14500+index,'mid','cedar')
                self._tree(s,172,217,94,14600+index,'mid','umbrella')
                self._water(s,79,200,69,14700+index)
                self._fern(s,145,217,14800+index)
            else:
                self._tree(s,44,216,92,14900+index,'mid','umbrella')
                self._tree(s,102,216,102,15000+index,'mid','cedar')
                self._tree(s,172,216,100,15100+index,'mid','broad')
            for j in range(4):
                x=(26+j*57+rng.randrange(-7,8))%LW
                if j%2:self._fern(s,x,218,15200+index*17+j,1)
                else:self._shrub(s,x,218,15300+index*17+j)
            for i in range(2):
                x=rng.randint(8,LW-9)
                self._mushroom(s,x,216,15400+index*23+i)
        else:
            self._ground(s,'near',15500+index)
            theme=index%5
            # raízes e grandes folhas presas ao solo; nunca sobre os perigos.
            placements=((13,59,116,170,199),(23,82,149,205),(17,105,186),(25,76,142,203),(15,56,120,183,198))[theme]
            for i,x in enumerate(placements):
                if i%3==0:self._bigleaf(s,x,228,15600+index*20+i)
                elif i%3==1:self._fern(s,x,229,15700+index*20+i,1.0)
                else:self._shrub(s,x,226,15800+index*20+i,style=i%3)
            # Silhuetas de árvores nas extremidades de alguns trechos.
            if theme==0:
                self._tree(s,38,225,62,15900+index,'near','cedar')
                self._tree(s,183,225,71,16000+index,'near','umbrella')
            elif theme==2:
                self._rock(s,52,227,16100+index)
                self._rock(s,189,227,16200+index)
            elif theme==3:
                self._ruins(s,143,226,43,16300+index)
            for j in range(2):
                x=rng.randrange(11,LW-11)
                self._mushroom(s,x,229,16400+index*11+j)
            # Folhas animadas serão desenhadas sobre a vegetação já enraizada.
            self._forest_anchors[index]=tuple((x, 221-(i%3)*2) for i,x in enumerate(placements[::2]))
        return s

    def _overlay_forest(self,surf,frame,climate,night):
        # Variação real ligada a clima existente, não sistema novo de tempo.
        wind=climate in ('vento','vento_folhas','tempestade_vento','tempestade')
        storm=climate in ('tempestade','tempestade_vento','chuva')
        # A posição é fornecida pelo render_scene desta classe.
        travel=getattr(self,'_forest_travel',0.0)
        off=max(0.,travel)*.52*.5
        first=int(off//LW);shift=int(off%LW)
        count=len(self._layers['near'])
        for j in range(2):
            index=((first+j)*3)%count
            for i,(ax,ay) in enumerate(self._forest_anchors.get(index,())):
                xx=int((j*LW-shift+ax)*2)
                yy=int((ay-13)*2)
                if not (-30<=xx<=455):continue
                phase=(frame//(7 if wind else 17)+i+index)%4
                surf.blit(self._forest_leaf_frames[phase],(xx-13,yy))
        if wind:
            for i in range(7 if self.visual_quality else 4):
                x=int((i*79+frame*2.2)%(WIDTH+20))-10
                y=220+int(15*math.sin((frame+i*29)*.045))+(i%3)*25
                pygame.draw.line(surf,(127,179,95),(x,y),(x+5,y+2),1)
        elif climate=='polen':
            for i in range(6 if self.visual_quality else 3):
                x=int((i*83+frame*.45)%(WIDTH+12))
                y=148+(i*31+frame//4)%160
                pygame.draw.circle(surf,(220,218,148),(x,y),1)
        if night>.26:
            for i in range(9 if self.visual_quality else 5):
                x=22+(i*53+int(6*math.sin(frame*.027+i)))%409
                y=258+(i*37)%139+int(3*math.sin(frame*.055+i))
                col=(163,217,123) if (frame//17+i)%3 else (228,234,158)
                pygame.draw.circle(surf,col,(x,y),1 if i%3 else 2)
        if storm:
            for i in range(10 if self.visual_quality else 5):
                x=int((i*49-frame*2.9)%(WIDTH+30))-15
                y=110+(i*41+frame*3)%310
                pygame.draw.line(surf,(137,186,189),(x,y),(x-5,y+13),1)

    def _overlay_forest_premium(self,surf,frame,climate,night):
        # Não duplicar efeitos de chuva/vento ou criar feixes retilíneos na tela.
        return

    def _overlay_forest_combo(self,surf,frame,climate,night):
        return

    def render_scene(self,target,travel,frame,night,climate,phase,foreground_only=False,map_kind='image'):
        if self.biome=='floresta':self._forest_travel=travel
        return super().render_scene(target,travel,frame,night,climate,phase,
                                    foreground_only=foreground_only,map_kind=map_kind)
