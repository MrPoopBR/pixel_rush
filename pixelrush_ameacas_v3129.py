"""Rolling log presentation, with unchanged movement, spawn and collision."""
import math
import os
import pygame
from pixelrush_ameacas_v3128 import AMEACAS,POR_BIOMA,escorpiao_frame
from pixelrush_ameacas_v3128 import AmeacaBioma as Previous, imagem_ameaca as previous_image
from pixelrush_ameacas_v3127 import risco_colisao_ativo
ROLLING=('N4','F3')
_CACHE={}

def log_frame(code,phase):
    key=(code,phase%12)
    if key in _CACHE:return _CACHE[key]
    w,h=AMEACAS[code][2:4]
    s=pygame.Surface((w,h),pygame.SRCALPHA)
    dark=(41,31,32);bark=(105,69,47)
    left=5;right=w-15;cy=h//2+1;ry=h//2-4
    pygame.draw.ellipse(s,(0,0,0,45),(5,h-5,w-10,4))
    pygame.draw.rect(s,dark,(left,cy-ry,right-left,ry*2))
    pygame.draw.ellipse(s,dark,(1,cy-ry,12,ry*2))
    pygame.draw.rect(s,bark,(left,cy-ry+2,right-left,ry*2-4))
    # Bark travels around the cylinder rather than rotating the collision rect.
    theta=-phase*math.tau/12
    for i in range(7):
        angle=theta+i*math.tau/7
        z=math.cos(angle)
        if z<=0:continue
        yy=round(cy+math.sin(angle)*(ry-2))
        color=(183,126,75) if math.sin(angle)<0 else (65,43,37)
        pygame.draw.lines(s,color,False,[(5,yy),(w//3,yy-1),(w//2,yy+1),(right,yy)],max(1,round(z*2)))
        if code=='N4' and i in (0,1):
            pygame.draw.lines(s,(221,238,240),False,[(8,yy),(22,yy-1),(37,yy),(right-3,yy-1)],max(1,round(z*3)))
    pygame.draw.ellipse(s,dark,(right-6,cy-ry,18,ry*2))
    pygame.draw.ellipse(s,(198,150,91),(right-4,cy-ry+2,14,ry*2-4))
    for inset in (3,6):pygame.draw.ellipse(s,(130,87,53),(right-4+inset//2,cy-ry+2+inset,14-inset,ry*2-4-inset*2),1)
    cx=right+3
    for shift in (0,2.5):
        angle=theta+shift
        pygame.draw.line(s,(92,62,43),(cx,cy),(round(cx+5*math.cos(angle)),round(cy+(ry-4)*math.sin(angle))),2)
    if code=='F3':pygame.draw.ellipse(s,(48,36,33),(cx-3,cy-4,6,8))
    _CACHE[key]=s
    return s

def imagem_ameaca(code,phase=0):
    return log_frame(code,phase) if code in ROLLING and os.getenv('PIXELRUSH_ARTE_CLASSICA')!='1' else previous_image(code,phase)

class AmeacaBioma(Previous):
    def __init__(self,x,codigo):
        super().__init__(x,codigo)
        self._roll_start=float(x)
        if codigo in ROLLING and os.getenv('PIXELRUSH_ARTE_CLASSICA')!='1':
            self._roll_frames=tuple(log_frame(codigo,i) for i in range(12))
            self.image=self._roll_frames[0]
        else:self._roll_frames=None

    def update(self,velocidade_jogo):
        super().update(velocidade_jogo)
        if self._roll_frames:
            circumference=math.pi*max(8,self.rect.height-8)
            phase=int((self._roll_start-self._x)*12/circumference)%12
            self.image=self._roll_frames[phase]
