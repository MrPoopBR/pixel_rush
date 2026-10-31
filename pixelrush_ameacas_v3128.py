"""New authored silhouettes; legacy simulation class is kept byte-for-byte."""
import os
import pygame
import pixelrush_ameacas_v3127 as legacy
from pixelrush_ameacas_v3127 import AMEACAS, POR_BIOMA, AmeacaBioma, risco_colisao_ativo
_ORIGINAL = legacy.imagem_ameaca
_CACHE = {}
REDESIGNED = tuple(c for c in AMEACAS if c[0] in 'CND' and not c.startswith('CF'))

def paint(code, phase):
    s=pygame.Surface((96,80),pygame.SRCALPHA)
    outline=(24,28,43); light=(248,236,201)
    def poly(color,pts): pygame.draw.polygon(s,color,pts)
    def line(color,pts,width=2): pygame.draw.lines(s,color,False,pts,width)
    def oval(color,rect): pygame.draw.ellipse(s,color,rect)
    def rect(color,box): pygame.draw.rect(s,color,box)
    def eye(x,y):
        oval(light,(x-2,y-2,7,7));rect(outline,(x,y,3,4));rect((255,255,255),(x,y,1,1))
    step=(0,3,-2)[phase]; wing=(0,9,-6)[phase]
    if code=='C1':
        line(outline,[(25,55),(10,52),(5,37),(11,32)],5)
        line((192,126,137),[(25,55),(10,52),(5,37),(11,32)],3)
        poly((88,96,112),[(17,55),(23,36),(38,27),(55,30),(67,38),(88,49),(82,57),(60,60),(40,65),(24,62)])
        poly((151,159,171),[(25,41),(39,32),(53,34),(62,42),(42,41),(31,51)])
        poly((59,67,86),[(22,55),(43,54),(61,48),(80,55),(61,61),(40,65)])
        oval(outline,(53,20,17,24));oval((171,153,161),(55,22,13,19));oval((223,153,165),(59,26,7,12))
        poly((128,137,153),[(60,35),(76,40),(89,49),(78,51),(65,46)])
        for x in (32,59):
            poly(outline,[(x,58),(x+4,58),(x+8+step,70),(x-4+step,70),(x-5+step,67)])
        eye(72,42);oval((235,148,150),(84,47,6,5))
        for dy in (-4,2): line((210,203,195),[(78,51),(91,51+dy)],1)
    elif code in ('C2','N2'):
        owl=code=='N2'; body=(201,216,230) if owl else (102,123,161)
        feather=(124,153,181) if owl else (61,83,122)
        poly(feather,[(45,40),(31,30),(12,12+wing),(6,17+wing),(14,38),(9,35),(19,49),(15,48),(30,58),(43,55)])
        poly(body,[(52,38),(65,25),(88,10+wing),(90,19+wing),(82,38),(87,34),(76,50),(80,49),(62,58)])
        for i in range(4):
            line(light if owl else (154,177,201),[(36,43+i*3),(13+i*5,23+wing+i*4)],2)
            line(feather,[(61,43+i*3),(87-i*5,24+wing+i*4)],2)
        poly(feather,[(36,55),(28,70),(43,66),(48,71),(57,64)])
        oval(body,(33,29,31,36));oval((234,229,206) if owl else (174,190,207),(41,40,20,22))
        if owl:
            poly(body,[(34,35),(30,16),(44,23),(57,21),(67,14),(64,38)])
            oval((243,239,218),(33,25,32,24));eye(40,33);eye(54,33)
            poly((201,149,65),[(47,39),(53,39),(49,46)])
            for x in (42,49,56):line(feather,[(x,51),(x+2,54),(x,57)],1)
        else:
            oval(body,(48,20,24,27));poly((212,159,98),[(68,33),(83,37),(69,41)])
            line((94,164,154),[(48,42),(57,46),(65,43)],3);eye(62,28)
        for x in (40,54): line((216,164,85),[(x,62),(x-2,68),(x+5,67)],2)
    elif code=='C3':
        for x,y in ((9,15),(47,7)):
            poly(outline,[(x,66),(x+33,66),(x+39,73),(x-3,73)])
            poly((218,83,41),[(x+3,64),(x+14,y),(x+20,y),(x+31,64)])
            poly((255,157,65),[(x+5,62),(x+15,y+3),(x+17,y+3),(x+17,63)])
            for yy in (y+19,y+36):poly(light,[(x+10-(yy-y)//7,yy),(x+24+(yy-y)//12,yy),(x+26+(yy-y)//12,yy+6),(x+8-(yy-y)//7,yy+6)])
            line((89,60,51),[(x+8,67),(x+30,67)],2)
    elif code=='C4':
        for x in (17,66):
            poly((94,66,48),[(x,18),(x+7,18),(x+16,73),(x+8,73)])
            poly((181,138,83),[(x+4,19),(x+9,19),(x-5,73),(x-10,73)])
        poly(outline,[(5,25),(87,22),(90,49),(7,53)])
        poly((241,177,57),[(8,28),(84,25),(86,46),(10,49)])
        for x in range(13,78,18):poly((60,62,65),[(x,28),(x+9,27),(x+19,47),(x+9,48)])
        for x in (13,79):oval(light,(x,31,3,3));oval(outline,(x,42,3,3))
        oval(outline,(38,7,18,17));oval((244,139,44),(41,9,12,12));rect((255,223,124),(43,10,4,5))
    elif code=='N1':
        poly((37,52,71),[(15,57),(20,35),(32,19),(49,18),(64,29),(78,40),(82,55),(63,66),(34,67)])
        poly((56,76,97),[(24,38),(35,23),(48,23),(56,32),(36,39)])
        oval((234,239,229),(33,36,43,27))
        poly((24,38,58),[(36,36),(54,37),(61,50+step),(45,53+step),(30,47)])
        poly((221,153,61),[(73,37),(91,43),(75,48)])
        eye(65,32)
        for x in (27,49): poly((227,155,62),[(x,62),(x+13,63),(x+19+step,71),(x+1,70)])
        line((155,201,220),[(9,72),(39,73),(73,71)],1)
    elif code=='N3':
        poly((73,128,171),[(11,21),(37,7),(78,13),(87,61),(65,73),(12,67)])
        poly((153,213,231),[(11,21),(37,7),(78,13),(59,26)])
        poly((102,176,210),[(13,24),(59,28),(64,68),(14,63)])
        poly((57,115,158),[(62,28),(78,16),(84,60),(67,69)])
        for pts in ([(37,19),(33,36),(45,43),(38,59)],[(33,36),(20,39)],[(45,43),(56,40)],[(70,27),(74,46),(69,53)]):line((36,91,132),pts,2)
        line((231,250,249),[(17,56),(17,28),(29,24)],3)
        poly((239,249,244),[(11,21),(34,7),(78,13),(70,18),(36,14),(24,23)])
    elif code=='N4':
        poly((82,62,57),[(9,34),(21,27),(76,29),(89,41),(87,62),(73,69),(18,66),(7,54)])
        for y in (37,46,57):line((140,97,69),[(16,y),(38,y-3),(60,y+2),(78,y)],3)
        oval((194,151,103),(66,32,24,34));oval((115,78,59),(71,37,15,24));oval((207,165,113),(74,40,9,17))
        poly((107,78,59),[(32,32),(28,17),(37,14),(44,32)])
        poly((232,246,248),[(8,34),(17,25),(29,25),(35,29),(49,25),(77,28),(84,35),(70,40),(49,36),(29,39),(12,38)])
        line((149,201,223),[(13,39),(30,41),(49,38),(69,42)],2)
    elif code=='D1':
        line(outline,[(9,65),(24,54),(43,61),(58,59),(64,45),(58,28+step),(72,20+step),(85,24+step)],15)
        line((183,120,54),[(9,65),(24,54),(43,61),(58,59),(64,45),(58,28+step),(72,20+step),(85,24+step)],11)
        line((239,190,92),[(11,62),(24,51),(42,57),(56,55),(60,44),(55,29+step)],3)
        poly((210,151,65),[(62,15+step),(80,16+step),(88,23+step),(82,32+step),(64,30+step),(57,24+step)])
        for x,y in ((24,55),(40,60),(57,56),(62,42)):poly((89,66,49),[(x-3,y-3),(x+2,y-4),(x+4,y+2),(x,y+3)])
        eye(76,22+step);line((190,72,59),[(84,29+step),(91,33+step),(94,30+step)],1)
    elif code=='D2':
        for x in (30,43,57):
            line(outline,[(x,44),(x-9,53+step),(x-14,65)],4)
            line((146,103,61),[(x,43),(x+7,54-step),(x+6,66)],3)
        poly((43,68,72),[(20,43),(27,27),(44,22),(60,30),(66,47),(54,56),(31,55)])
        poly((82,126,124),[(25,40),(30,30),(42,26),(43,49),(30,50)])
        poly((55,96,94),[(46,27),(57,33),(61,45),(49,51)])
        line((180,186,125),[(29,33),(37,29),(39,43)],2)
        oval((34,51,57),(55,34,18,18));eye(66,37)
        line(outline,[(63,34),(70,25),(76,27)],2)
        oval(outline,(71,43,21,27));oval((160,119,73),(73,45,17,22))
        line((211,167,106),[(77,48),(84,51),(80+step,61)],2)
    elif code=='D3':
        poly((101,69,66),[(20,69),(25,60),(28,24),(20,18),(24,8),(66,8),(75,19),(64,25),(68,61),(79,70)])
        poly((212,161,108),[(29,25),(61,25),(65,62),(26,62)])
        for x in (31,41,52):rect((151,103,77),(x,28,4,31));rect((242,197,132),(x+4,28,2,29))
        poly((235,186,121),[(23,11),(64,11),(70,18),(23,18)])
        poly((227,176,117),[(24,62),(68,62),(74,68),(19,68)])
        line((91,68,63),[(59,15),(51,22),(55,32),(47,40)],2)
        for x in (17,73):poly((176,123,88),[(x,70),(x+7,63),(x+13,72)])
    elif code=='D4':
        line((128,101,76),[(12,61),(34,53),(59,51),(78,58)],5)
        for i in range(5):
            x=24+i*9;y=30+abs(i-2)*3
            line((225,202,149),[(x-4,59),(x-6,y+7),(x,y),(x+7,y+6),(x+9,58)],4)
            line((254,232,176),[(x-5,y+7),(x,y),(x+6,y+5)],1)
        poly((230,207,158),[(6,48),(10,34),(23,34),(31,43),(29,56),(22,65),(7,62)])
        poly((61,57,56),[(9,44),(16,41),(17,51),(10,53)])
        poly((115,94,75),[(22,52),(26,55),(21,60)])
        line((243,224,175),[(10,36),(5,24),(9,15)],3)
        for x in (8,13,18):line((137,112,82),[(x,58),(x,63)],1)
    return legacy._aplicar_contorno(s)

def imagem_ameaca(codigo,fase=0):
    if codigo not in REDESIGNED or os.environ.get('PIXELRUSH_ARTE_CLASSICA')=='1':
        return _ORIGINAL(codigo,fase)
    key=(codigo,int(fase)%3)
    if key not in _CACHE:
        _,_,w,h,_=AMEACAS[codigo]
        _CACHE[key]=pygame.transform.scale(paint(*key),(w,h)).convert_alpha()
    return _CACHE[key]

# The inherited class resolves its renderer in the legacy module globals.
legacy.imagem_ameaca=imagem_ameaca

def escorpiao_frame(size,phase):
    """Articulated legs, two pincers and a segmented recurved tail."""
    key=('scorpion',tuple(size),phase%2)
    if key in _CACHE:return _CACHE[key]
    s=pygame.Surface((120,64),pygame.SRCALPHA)
    dark=(51,33,40);shell=(177,91,49);lit=(235,153,79)
    for i in range(4):
        x=38+i*10;dy=3 if (i+phase)%2 else -2
        pygame.draw.lines(s,dark,False,[(x,39),(x-7,47),(x-14,56+dy)],4)
        pygame.draw.lines(s,lit,False,[(x,40),(x+9,47),(x+13,57-dy)],3)
    pygame.draw.lines(s,dark,False,[(73,37),(90,28),(96,17),(92,7),(80,5),(74,12)],10)
    pygame.draw.lines(s,shell,False,[(73,37),(90,28),(96,17),(92,7),(80,5),(74,12)],6)
    for x,y in ((84,29),(93,20),(92,11),(84,6)):pygame.draw.line(s,lit,(x-3,y-2),(x+2,y+1),2)
    pygame.draw.polygon(s,dark,[(72,9),(79,14),(72,22),(73,15),(68,15)])
    pygame.draw.polygon(s,shell,[(27,35),(39,27),(67,27),(78,34),(74,44),(42,46),(28,41)])
    for x in (42,51,60,69):
        pygame.draw.line(s,dark,(x,29),(x+2,43),2)
        pygame.draw.line(s,lit,(x+3,30),(x+4,36),2)
    for y,sgn in ((28,-1),(45,1)):
        pygame.draw.lines(s,dark,False,[(34,y+3),(23,y),(16,y+sgn*4)],5)
        pts=[(17,y-6),(5,y-8-phase),(3,y-3),(11,y),(3,y+4),(8,y+8+phase),(20,y+4),(23,y)]
        pygame.draw.polygon(s,shell,pts);pygame.draw.lines(s,lit,False,pts[:4],2)
    for y in (32,39):pygame.draw.circle(s,(255,214,120),(30,y),2)
    out=pygame.transform.scale(legacy._aplicar_contorno(s),size)
    _CACHE[key]=out
    return out
