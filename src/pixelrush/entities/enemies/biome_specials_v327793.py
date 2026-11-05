# -*- coding: utf-8 -*-
"""PIXEL RUSH R23: seis inimigos inéditos, um por bioma, sem novas texturas PNG.

Somente 18 poses pygame-ce predesenhadas (3 por espécie) no primeiro spawn.
Movimento 100% em coordenadas existentes, imagem em cache, sem aleatoriedade
no update, sem superfícies SDL por quadro nem perturbar a física do jogador.
"""
import math
import pygame

ESPECIAIS_BIOMA={
    "cidade":("C5","Carrinho de Limpeza Desgovernado"),
    "deserto":("D5","Besouro das Dunas"),
    "vulcao":("V5","Golem de Cinzas"),
    "floresta":("F5","Sapo de Folhas"),
    "cidade_futurista":("CF5","Robô Varredor"),
    "ilhas_celestes":("IC5","Guardião das Nuvens"),
}
CORES={
    "cidade":((245,168,88),(39,75,96),(118,225,225)),
    "deserto":((246,213,120),(99,65,45),(248,130,81)),
    "vulcao":((255,136,82),(66,50,65),(255,222,117)),
    "floresta":((174,237,107),(48,91,66),(250,224,111)),
    "cidade_futurista":((118,247,242),(37,54,110),(253,122,204)),
    "ilhas_celestes":((215,241,252),(94,115,177),(250,204,136)),
}
_W,_H=58,56
_FRAMES={}

def _quadro(bioma, fase):
    luz,escuro,destaque=CORES[bioma]
    img=pygame.Surface((_W,_H),pygame.SRCALPHA).convert_alpha()
    eixo=fase-1
    # Sombra de contato e contorno escuro dão leitura contra piso e céu.
    pygame.draw.ellipse(img,(28,39,61,95),(7,47,45,7))
    if bioma=="cidade":
        # Carrinho operário com rodas, farol e escova giratória.
        pygame.draw.circle(img,escuro,(15,43),9)
        pygame.draw.circle(img,escuro,(43,43),9)
        pygame.draw.circle(img,(223,234,240),(15,43),5)
        pygame.draw.circle(img,(223,234,240),(43,43),5)
        pygame.draw.rect(img,escuro,(8,20,43,23),border_radius=5)
        pygame.draw.rect(img,luz,(10,18+eixo,39,22),border_radius=4)
        pygame.draw.rect(img,(253,240,208),(15,21+eixo,15,8),border_radius=2)
        pygame.draw.line(img,destaque,(31,26+eixo),(45,26+eixo),3)
        pygame.draw.rect(img,escuro,(7,29,5,10))
        pygame.draw.line(img,(55,76,82),(45,15),(49,6),3)
        pygame.draw.circle(img,(255,239,116),(49,6),4)
        for xx in (16,23,30):pygame.draw.line(img,destaque,(xx,38),(xx+2,40),1)
        pygame.draw.line(img,(52,68,80),(5,41),(5,48),3)
        pygame.draw.line(img,destaque,(3,48),(10,48),2)
    elif bioma=="deserto":
        # Besouro escaravelho: carapaça articulada e patas com ritmo.
        for px in (12,46):
            for yy in (30,38,45):
                pygame.draw.line(img,escuro,(px,yy),(px+(-7 if px<30 else 7),yy+3+eixo),3)
        pygame.draw.ellipse(img,escuro,(10,17+eixo,38,31))
        pygame.draw.ellipse(img,luz,(12,16+eixo,34,29))
        pygame.draw.ellipse(img,(187,121,60),(15,19+eixo,28,20))
        pygame.draw.arc(img,(255,235,161),(16,19+eixo,27,19),.2,2.9,3)
        pygame.draw.line(img,escuro,(29,22+eixo),(29,40+eixo),2)
        pygame.draw.ellipse(img,escuro,(7,26+eixo,15,14))
        for yy in (29,34):
            pygame.draw.circle(img,destaque,(13,yy+eixo),2)
        pygame.draw.line(img,escuro,(14,26+eixo),(10,14+eixo),2)
        pygame.draw.line(img,escuro,(19,26+eixo),(22,13+eixo),2)
        pygame.draw.circle(img,destaque,(10,13+eixo),3)
        pygame.draw.circle(img,destaque,(22,13+eixo),3)
    elif bioma=="vulcao":
        # Golem compacto de basalto, rachaduras quentes e olhos incandescentes.
        pygame.draw.polygon(img,escuro,((8,20),(17,11+eixo),(41,12+eixo),(51,21),(49,44),(10,47)))
        pygame.draw.polygon(img,(82,63,70),((12,23),(22,15+eixo),(38,15+eixo),(46,25),(45,42),(13,43)))
        pygame.draw.polygon(img,(49,53,69),((13,24),(26,20),(37,27),(46,24),(44,39),(16,41)))
        for path in (((25,18),(23,29),(31,34),(27,43)),((38,18),(35,25),(42,31))):
            pygame.draw.lines(img,luz,False,[(x,y+eixo) for x,y in path],3)
        for xx in (21,38):
            pygame.draw.rect(img,(255,227,119),(xx,29+eixo,6,4))
            pygame.draw.rect(img,escuro,(xx+1,29+eixo,2,3))
        pygame.draw.rect(img,(245,137,92),(17,44,26,5),border_radius=2)
        pygame.draw.polygon(img,destaque,((19,8),(22,2+eixo),(27,10)))
        pygame.draw.polygon(img,luz,((38,11),(43,4+eixo),(46,15)))
    elif bioma=="floresta":
        # Sapo de folhas: olhos saltados, corpo verde e folhas nas costas.
        pygame.draw.ellipse(img,escuro,(6,34,47,13))
        pygame.draw.ellipse(img,luz,(8,23+eixo*2,43,23))
        pygame.draw.ellipse(img,(101,171,81),(12,29+eixo*2,35,14))
        for xx in (17,40):
            pygame.draw.circle(img,escuro,(xx,24+eixo*2),9)
            pygame.draw.circle(img,(230,249,186),(xx,22+eixo*2),6)
            pygame.draw.circle(img,(37,59,45),(xx+1,22+eixo*2),3)
            pygame.draw.circle(img,(255,255,255),(xx,21+eixo*2),1)
        pygame.draw.arc(img,escuro,(19,29+eixo*2,20,12),.2,2.9,2)
        pygame.draw.ellipse(img,destaque,(28,11+eixo*2,20,14))
        pygame.draw.line(img,(56,106,72),(29,22+eixo*2),(42,13+eixo*2),2)
        pygame.draw.ellipse(img,(237,177,119),(12,43,14,6))
        pygame.draw.ellipse(img,(237,177,119),(37,43,14,6))
        pygame.draw.circle(img,(240,165,134),(15,32+eixo*2),3)
        pygame.draw.circle(img,(240,165,134),(43,32+eixo*2),3)
    elif bioma=="cidade_futurista":
        # Robo patrulheiro varredor, luzes neon e rodas em campo magnetico.
        pygame.draw.line(img,destaque,(13,45),(45,45),2)
        pygame.draw.ellipse(img,escuro,(7,36+eixo,44,13))
        pygame.draw.rect(img,escuro,(12,14+eixo,35,28),border_radius=5)
        pygame.draw.rect(img,(74,99,161),(14,16+eixo,31,23),border_radius=4)
        pygame.draw.rect(img,luz,(17,20+eixo,25,11),border_radius=2)
        pygame.draw.rect(img,escuro,(21,23+eixo,6,5),border_radius=2)
        pygame.draw.rect(img,escuro,(34,23+eixo,5,5),border_radius=2)
        pygame.draw.rect(img,destaque,(26,34+eixo,11,3),border_radius=2)
        pygame.draw.line(img,luz,(29,14+eixo),(29,7+eixo),2)
        pygame.draw.circle(img,destaque,(29,6+eixo),4)
        pygame.draw.line(img,(210,243,254),(15,40+eixo),(8,34+eixo),3)
        pygame.draw.line(img,(210,243,254),(47,40+eixo),(52,34+eixo),3)
        for xx in (17,43):pygame.draw.circle(img,(216,238,246),(xx,45+eixo),3)
    else:
        # Guardiao das Nuvens: criatura de cristal/papel com asas.
        pygame.draw.polygon(img,escuro,((10,28+eixo),(24,12+eixo),(43,14+eixo),(51,31+eixo),(43,44+eixo),(15,43+eixo)))
        pygame.draw.polygon(img,luz,((13,28+eixo),(26,14+eixo),(41,16+eixo),(47,31+eixo),(41,42+eixo),(17,41+eixo)))
        pygame.draw.polygon(img,destaque,((5,21+eixo),(16,17+eixo),(19,30+eixo),(11,35+eixo)))
        pygame.draw.polygon(img,destaque,((48,17+eixo),(55,22+eixo),(50,36+eixo),(43,29+eixo)))
        pygame.draw.polygon(img,(126,199,236),((25,16+eixo),(34,9+eixo),(41,17+eixo),(36,26+eixo)))
        pygame.draw.circle(img,escuro,(25,30+eixo),3)
        pygame.draw.circle(img,escuro,(38,30+eixo),3)
        pygame.draw.circle(img,(255,255,255),(24,29+eixo),1)
        pygame.draw.circle(img,(255,255,255),(37,29+eixo),1)
        pygame.draw.line(img,(165,124,161),(27,37+eixo),(35,37+eixo),2)
        pygame.draw.circle(img,(247,215,164),(32,8+eixo),3)
        pygame.draw.line(img,(236,251,255),(16,42+eixo),(23,47+eixo),2)
        pygame.draw.line(img,(236,251,255),(42,42+eixo),(36,47+eixo),2)
    return img

class InimigoEspecialBioma(pygame.sprite.Sprite):
    """Diversidade por bioma: 6 visuais/IA simples, um atlas com 3 poses por tipo."""
    def __init__(self,x,bioma):
        super().__init__()
        if bioma not in ESPECIAIS_BIOMA:
            raise ValueError("Sem espécie especial neste bioma")
        sprites=_FRAMES.get(bioma)
        if sprites is None:
            sprites=tuple(_quadro(bioma,i) for i in range(3))
            _FRAMES[bioma]=sprites
        self.image=sprites[0]
        self.rect=self.image.get_rect(midbottom=(int(x),730))
        self.bioma=bioma
        self.codigo,self.nome=ESPECIAIS_BIOMA[bioma]
        self.tipo="ameaca_bioma_especial"
        self.qtd_cactos=0
        self._hitboxes_precisas_v342=(pygame.Rect(9,13,40,35),)
        self._x=float(self.rect.x)
        self._base_y=self.rect.y
        self.ticks=0
        self._fase=int(x)%21
        self._vel_extra={
            "cidade":.7,"deserto":1.1,"vulcao":.6,
            "floresta":.9,"cidade_futurista":1.6,"ilhas_celestes":.8
        }[bioma]

    def update(self,velocidade_jogo):
        self.ticks+=1
        self._x-=max(.1,float(velocidade_jogo))+self._vel_extra
        t=self.ticks+self._fase
        # Caminho separado por bioma: dança leve para não aumentar a dificuldade
        # de maneira imprevisível além dos hitboxes existentes.
        if self.bioma=="cidade":
            dx=4*math.sin(t*.07);dy=0
        elif self.bioma=="deserto":
            dx=7*math.sin(t*.095);dy=round(abs(math.sin(t*.1))*2)
        elif self.bioma=="vulcao":
            dx=2*math.sin(t*.04);dy=-round(abs(math.sin(t*.13))*3)
        elif self.bioma=="floresta":
            dx=2*math.sin(t*.07);dy=-round(abs(math.sin(t*.08))*7)
        elif self.bioma=="cidade_futurista":
            dx=5*math.sin(t*.11);dy=-round(abs(math.sin(t*.15))*2)
        else:
            dx=4*math.sin(t*.09);dy=-round(abs(math.sin(t*.085))*5)
        self.rect.x=round(self._x+dx)
        self.rect.y=self._base_y+dy
        self.image=_FRAMES[self.bioma][(self.ticks//8)%3]
        if self.rect.right < -70:self.kill()

def memoria_atlas_bytes():
    return sum(s.get_width()*s.get_height()*4 for conjunto in _FRAMES.values()
               for s in conjunto)
