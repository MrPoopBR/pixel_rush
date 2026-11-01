"""UI adaptativa do tutorial obrigatório v3.275.0.

Herda todas as seis lições, física, colisões não fatais e progresso da v3.274.
Somente desenha dicas de teclado/toque/controle, sem avançar estados nem salvar.
"""
from __future__ import annotations
import pygame
from pixelrush_tutorial_corrida_v3274 import TutorialCorrida as _TutorialAnterior, ETAPAS, TEXTOS

DICAS = {
    "pular": ("ESPAÇO / SETA CIMA", "TOQUE RÁPIDO NA TELA", "BOTÃO DE PULAR"),
    "pular_longo": ("SEGURE ESPAÇO", "TOQUE E SEGURE", "SEGURE PULAR"),
    "agachar": ("SEGURE S / SETA BAIXO", "TOQUE E SEGURE", "SEGURE AGACHAR"),
    "swipe_down": ("NO AR: SETA BAIXO", "NO AR: ARRASTE PARA BAIXO", "NO AR: BOTÃO DE DESCIDA"),
    "moedas": ("ENCOSTE NAS 3 MOEDAS", "ENCOSTE NAS 3 MOEDAS", "ENCOSTE NAS 3 MOEDAS"),
    "letras": ("ENCOSTE NAS 5 LETRAS", "ENCOSTE NAS 5 LETRAS", "ENCOSTE NAS 5 LETRAS"),
}

class TutorialCorrida(_TutorialAnterior):
    """Adaptação visual a diferentes comandos, com progresso original intacto."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.modo_entrada='teclado'

    def processar_evento(self,evento,converter=None,som=None,volume=1.0):
        if evento.type in (pygame.KEYDOWN, pygame.KEYUP):
            self.modo_entrada='teclado'
        elif evento.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP,
                              pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            self.modo_entrada='toque'
        elif evento.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
            self.modo_entrada='controle'
        return super().processar_evento(evento,converter,som,volume)

    def desenhar(self,tela,fonte=None):
        if not self.ativo:
            return
        super().desenhar(tela,fonte)
        # Faixa de dicas abaixo do painel original (226..320), mas acima do chão.
        w=tela.get_width()
        if w<150 or tela.get_height()<440:return
        modo=self.modo_entrada if self.modo_entrada in ('teclado','toque','controle') else 'teclado'
        indice={'teclado':0,'toque':1,'controle':2}[modo]
        ui=getattr(self,'textos_ui',{})
        dicas=ui.get('dicas',DICAS)
        principal=dicas[self.etapa][indice]
        alternativa=dicas[self.etapa][1-indice] if indice in (0,1) else dicas[self.etapa][0]
        etiqueta=ui.get('modos',{'teclado':'TECLADO','toque':'TOQUE / MOUSE','controle':'CONTROLE'})[modo]
        faixaw=w-24
        faixa=pygame.Surface((faixaw,47),pygame.SRCALPHA)
        pygame.draw.rect(faixa,(13,28,42,219),faixa.get_rect(),border_radius=9)
        pygame.draw.rect(faixa,(87,195,216,194),faixa.get_rect(),1,border_radius=9)
        local=getattr(self,'fonte_tutorial',None)
        f=local(17) if local else pygame.font.Font(None,19)
        f2=local(14) if local else pygame.font.Font(None,16)
        linha=f'{etiqueta}: {principal}'
        if f.size(linha)[0]>faixaw-20:
            f=self.ajustar_fonte_tutorial(linha,faixaw-20,16) if local else pygame.font.Font(None,16)
        faixa.blit(f.render(linha,True,(246,223,151)),(9,5))
        outra=ui.get('alternativa','ALTERNATIVA')+': '+alternativa
        if local:
            f2=self.ajustar_fonte_tutorial(outra,faixaw-20,14)
        elif f2.size(outra)[0]>faixaw-20:
            outra='OUTRO COMANDO: '+alternativa
        faixa.blit(f2.render(outra,True,(212,231,240)),(9,26))
        tela.blit(faixa,(12,368))
