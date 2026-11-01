"""Resposta visual mais legível ao salto, corrida e deslizamento (somente desenho).

Reaproveita quadros de animação, feedback de aterrissagem e áudio existentes;
nenhum toque em posição física, sons, hitboxes, temporizadores ou movimento.
"""
import pygame
from pixelrush_gamefeel_v3129 import GameFeel as Anterior, criar_variantes_pitch, criar_camada_ritmica


class GameFeel(Anterior):
    def desenhar(self,surf,jogador=None,combo=0,bioma='cidade'):
        super().desenhar(surf,jogador,combo,bioma)
        if jogador is None or jogador.morrendo or jogador.jetpack_fase is not None:
            return
        r=jogador.rect
        if r.bottom<170 or r.top>735:
            return
        # Sinais de comando curtos, com três linhas sólidas no máximo.
        # Não são pegadas, poeira permanente, rastro ou novas partículas.
        cor=(203,182,132) if bioma=='deserto' else ((177,224,236) if bioma=='neve' else (140,202,157) if bioma=='floresta' else (157,199,224))
        if not jogador.no_chao and not jogador.descida_rapida and jogador.anim_pulo_frames<=3:
            t=max(0,3-jogador.anim_pulo_frames)
            y=r.bottom+2
            pygame.draw.line(surf,cor,(r.left+9,y+t),(r.left-1-t,y+8+t),2)
            pygame.draw.line(surf,cor,(r.right-9,y+t),(r.right+1+t,y+7+t),2)
        elif jogador.descida_rapida and not jogador.no_chao and self.tempo%3==0:
            pygame.draw.line(surf,cor,(r.left+7,r.top-14),(r.left+7,r.top-3),2)
            pygame.draw.line(surf,cor,(r.right-7,r.top-10),(r.right-7,r.top+1),2)
        elif jogador.no_chao and jogador.anim_pouso_ticks>0:
            t=4-jogador.anim_pouso_ticks
            pygame.draw.line(surf,cor,(r.left-4-t,r.bottom-3),(r.left+4,r.bottom-3),2)
            pygame.draw.line(surf,cor,(r.right-4,r.bottom-3),(r.right+4+t,r.bottom-3),2)
        elif jogador.no_chao and jogador.agachado and self.tempo%8<3:
            pygame.draw.line(surf,cor,(r.left-8,r.bottom-4),(r.left+4,r.bottom-4),1)
