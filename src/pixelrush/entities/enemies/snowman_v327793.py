# -*- coding: utf-8 -*-
"""Boneco de Neve do bioma gelado, sprites e projéteis leves, sem assets extras.

Preparação dos quadros e superfície da bola somente uma vez após pygame.init().
A IA lança no máximo uma bola por aparição, com aviso visual e 3 alturas.
"""
import pygame

GELO=(209,235,253)
NEVE=(246,252,255)
SOMBRA=(100,159,201)
LARANJA=(255,172,83)
ESCURO=(40,66,103)

class BolaDeNeve(pygame.sprite.Sprite):
    _quadro=None

    def __init__(self,x,y):
        super().__init__()
        if BolaDeNeve._quadro is None:
            img=pygame.Surface((20,20),pygame.SRCALPHA).convert_alpha()
            pygame.draw.circle(img,(54,107,149,120),(11,12),9)
            pygame.draw.circle(img,NEVE,(9,9),8)
            pygame.draw.circle(img,GELO,(10,11),6)
            pygame.draw.circle(img,(255,255,255),(6,6),3)
            pygame.draw.circle(img,SOMBRA,(14,12),2)
            BolaDeNeve._quadro=img
        self.image=BolaDeNeve._quadro
        self.rect=self.image.get_rect(center=(int(x),int(y)))
        self._x=float(self.rect.x)
        self.codigo="N5_BOLA"
        self.tipo="projetil_bola_neve"
        self.qtd_cactos=0
        self._hitboxes_precisas_v342=(pygame.Rect(3,3,14,14),)

    def update(self,velocidade_jogo):
        self._x-=max(3.0,float(velocidade_jogo)+2.2)
        self.rect.x=int(self._x)
        if self.rect.right < -28:self.kill()

class BonecoNeve(pygame.sprite.Sprite):
    _quadros=None
    def __init__(self,x,grupo_todos=None,grupo_perigos=None):
        super().__init__()
        if BonecoNeve._quadros is None:
            BonecoNeve._quadros=tuple(self._desenhar_frame(i) for i in range(3))
        self.image=BonecoNeve._quadros[0]
        self.rect=self.image.get_rect(midbottom=(int(x),730))
        self._x=float(self.rect.x)
        self.ticks=0
        self._atirou=False
        self._grupo_todos=grupo_todos
        self._grupo_perigos=grupo_perigos
        self.codigo="N5"
        self.tipo="boneco_neve"
        self.bioma="neve"
        self.nome="Boneco de Neve Atirador"
        self.qtd_cactos=0
        self._hitboxes_precisas_v342=(pygame.Rect(6,8,45,62),)

    @staticmethod
    def _desenhar_frame(fase):
        tela=pygame.Surface((56,74),pygame.SRCALPHA).convert_alpha()
        # Sombra baixa ajuda leitura contra estrada azul clara.
        pygame.draw.ellipse(tela,(43,91,134,105),(5,66,47,7))
        pygame.draw.ellipse(tela,ESCURO,(7,30,44,39))
        pygame.draw.ellipse(tela,GELO,(8,31,42,37))
        pygame.draw.ellipse(tela,NEVE,(10,30,38,33))
        pygame.draw.ellipse(tela,ESCURO,(10,5,38,34))
        pygame.draw.ellipse(tela,GELO,(11,6,36,32))
        pygame.draw.ellipse(tela,NEVE,(13,7,33,28))
        # Cartola e fita vermelha destacável do fundo.
        pygame.draw.rect(tela,ESCURO,(12,3,32,5),border_radius=1)
        pygame.draw.rect(tela,(54,72,103),(18,0,20,6))
        pygame.draw.line(tela,(240,95,110),(19,5),(36,5),2)
        pygame.draw.circle(tela,(25,39,69),(22,19),3)
        pygame.draw.circle(tela,(25,39,69),(35,19),3)
        pygame.draw.circle(tela,(255,255,255),(21,18),1)
        pygame.draw.circle(tela,(255,255,255),(34,18),1)
        pygame.draw.polygon(tela,LARANJA,((26,25),(42,29),(27,30)))
        pygame.draw.arc(tela,(42,66,96),(19,24,19,13),3.3,6.0,2)
        pygame.draw.rect(tela,(221,62,83),(12,34,33,5),border_radius=2)
        pygame.draw.polygon(tela,(245,105,118),((38,35),(49,40+fase),(44,52+fase),(39,42)))
        for y in (45,56):
            pygame.draw.circle(tela,ESCURO,(28,y),3)
            pygame.draw.circle(tela,(255,255,255),(27,y-1),1)
        # Braço que aponta antes do arremesso.
        pygame.draw.line(tela,(89,63,53),(11,43),(1,33-fase*2),4)
        pygame.draw.line(tela,(89,63,53),(42,43),(53,32-fase*4),4)
        pygame.draw.line(tela,(129,92,67),(53,32-fase*4),(55,25-fase*4),2)
        pygame.draw.line(tela,(217,241,253),(13,51),(22,49),2)
        pygame.draw.line(tela,(255,255,255),(17,57),(20,58),1)
        return tela

    def update(self,velocidade_jogo):
        self.ticks+=1
        self._x-=max(0.1,float(velocidade_jogo))
        self.rect.x=int(self._x)
        if self.ticks%16==0:
            self.image=BonecoNeve._quadros[(self.ticks//16)%3]
        # Uma bola, aviso de braço levantado por ~0,25s antes do disparo.
        if (not self._atirou and self.ticks>=32 and
                self.rect.left>=300 and self.rect.left<=510 and
                self._grupo_todos is not None and self._grupo_perigos is not None):
            y=(self.rect.top+22,self.rect.top+38,self.rect.top+53)[(self.ticks//7)%3]
            bola=BolaDeNeve(self.rect.left-14,y)
            self._grupo_todos.add(bola)
            self._grupo_perigos.add(bola)
            self._atirou=True
        if self.rect.right<-70:self.kill()
