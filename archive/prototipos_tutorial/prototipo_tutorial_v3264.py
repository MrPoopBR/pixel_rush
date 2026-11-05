"""Apresentação Pygame reutilizável: POC e integração opcional no jogo.

Pygame independente, apenas arte provisória desenhada via primitives;
NÃO importa o jogo principal nem modifica seus controles e progressão.
"""
from __future__ import annotations
import argparse, math, os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

W,H=450,800
SKY=(13,24,47); GOLD=(255,211,93); WHITE=(239,249,251); CYAN=(80,226,219)
@dataclass
class Estado:
    etapa:str='abertura'
    tick:int=0
    saltos:int=0
    agachamentos:int=0
    finalizado:bool=False
    aviso:str=''
    abertura_pulada:bool=False
    def acao(self,acao):
        if self.etapa=='abertura' and acao in ('iniciar','avancar','pular_abertura'):
            self.abertura_pulada=(acao=='pular_abertura');self.etapa='pulo';self.tick=0;self.aviso='' 
        elif self.etapa=='pulo' and acao=='pular':
            self.saltos+=1;self.etapa='agachar';self.tick=0;self.aviso='Boa! Agora tente agachar.'
        elif self.etapa=='agachar' and acao=='agachar':
            self.agachamentos+=1;self.etapa='fim';self.finalizado=True;self.tick=0
        elif self.etapa=='fim' and acao=='reiniciar':
            self.__dict__.update(Estado().__dict__)
    def progredir(self):self.tick+=1
    def quadro(self):return {'etapa':self.etapa,'saltos':self.saltos,'agachamentos':self.agachamentos,
                            'finalizado':self.finalizado,'tick':self.tick,'abertura_pulada':self.abertura_pulada}

def texto(tela,font,content,x,y,color=WHITE,centro=False):
    import pygame
    im=font.render(content,True,color)
    rect=im.get_rect(center=(x,y)) if centro else im.get_rect(topleft=(x,y))
    tela.blit(im,rect)

@lru_cache(maxsize=1)
def _fundo_original():
    """Captura já existente do próprio Pixel Rush, sem criação de novos assets."""
    import pygame
    p=Path(__file__).parent/'RELATORIOS_VISUAIS_v3230'/'depois'/'cidade_dia.png'
    if not p.is_file():return None
    return pygame.transform.smoothscale(pygame.image.load(str(p)).convert_alpha(),(W,H))

def _apresentacao_premium(tela, est):
    """Partículas, foco e telegraph didático: desenho apenas, sem RNG nem lógica."""
    import pygame
    t=est.tick
    # Vinheta por barras laterais e feixes ritmados de luz no plano de fundo.
    vignette=pygame.Surface((W,H),pygame.SRCALPHA)
    pygame.draw.rect(vignette,(5,12,30,63),(0,0,34,H))
    pygame.draw.rect(vignette,(5,12,30,63),(W-34,0,34,H))
    for idx in range(18):
        x=int((idx*109 + t*1.8)%540)-45
        y=int((idx*73+int(t*.25))%360)+245
        cor=(80,222,229,38+(idx%5)*9)
        pygame.draw.circle(vignette,cor,(x,y),1+(idx%3))
    tela.blit(vignette,(0,0))
    # Prévia de risco: a área de perigo pulsa, sem mover perigo/hitbox.
    if est.etapa in ('pulo','agachar'):
        amp=(1+math.sin(t*.14))/2
        alert=pygame.Surface((145,90),pygame.SRCALPHA)
        pygame.draw.rect(alert,(255,191,78,int(10+amp*25)),(0,0,145,90),border_radius=10)
        pygame.draw.rect(alert,(255,211,93,int(50+amp*90)),(0,0,145,90),2,border_radius=10)
        tela.blit(alert,(282,510))
    # Progressão audiovisual simulada visualmente (som do jogo não é tocado).
    if est.etapa=='fim':
        for i in range(10):
            angle=(i*2*math.pi/10)+t*.02
            x=225+int(math.cos(angle)*(48+12*math.sin(t*.06)))
            y=390+int(math.sin(angle)*(48+12*math.sin(t*.06)))
            pygame.draw.circle(tela,GOLD,(x,y),3)

def _efeitos_poc(tela,est):
    """Acabamentos visuais determinísticos, sem modificar Estado e sem usar RNG."""
    import pygame
    t=est.tick
    # Traços de velocidade e pequenos brilhos nos pisos (parallax apenas decorativo).
    for i in range(14):
        pos=(i*113+t*6)%620-85
        linha=pygame.Surface((75,4),pygame.SRCALPHA)
        linha.fill((80,225,219,42+(i%3)*22))
        tela.blit(linha,(pos,604+(i%4)*31))
    # Pulso de alerta ao aproximar-se do laser; sem colisões reais.
    if est.etapa=='agachar':
        brilho=int(75+65*abs(math.sin(t*.18)))
        halo=pygame.Surface((106,12),pygame.SRCALPHA)
        halo.fill((255,69,98,brilho))
        tela.blit(halo,(305,548))
    # Marcas da progressão da POC.
    for idx,etapa in enumerate(('pulo','agachar')):
        feito=est.saltos>0 if idx==0 else est.agachamentos>0
        ativo=etapa==est.etapa
        color=GOLD if feito else CYAN if ativo else (74,94,117)
        pygame.draw.circle(tela,color,(361+idx*26,213),7)
        if feito:pygame.draw.circle(tela,(17,43,67),(361+idx*26,213),3)
    if est.etapa=='abertura':
        # Cinematic matte dissolves quickly, retaining the SKIP intro button.
        frac=max(0.0,1.0-min(t,42)/42)
        h=int(5+8*frac)
        pygame.draw.rect(tela,(7,13,27),(0,0,W,h))
        pygame.draw.rect(tela,(7,13,27),(0,H-h,W,h))
        pygame.draw.line(tela,GOLD,(22,213),(22+int(320*(1-frac)),213),3)


def _animacao_cinematografica_3262(tela, est):
    """Animação apenas decorativa, sem eventos nem física do jogo principal."""
    import pygame
    t = est.tick
    # Feixe de luz percorrendo o cenário e camada atmosférica sincronizada.
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    if est.etapa == 'abertura':
        alfa = max(0, int(110 * (1-min(t, 65)/65)))
        overlay.fill((5, 12, 25, alfa))
        raio = int(-90 + min(t, 80) * 7.5)
        pygame.draw.polygon(overlay, (96, 216, 245, 28), [(raio, 210), (raio+30,210), (raio+165,610), (raio+60,610)])
    elif est.etapa in ('pulo', 'agachar'):
        pulse = (1+math.sin(t*0.13))*0.5
        color = (255, 215, 105, int(25+35*pulse)) if est.etapa=='pulo' else (255, 104, 121, int(25+35*pulse))
        pygame.draw.circle(overlay, color, (340, 550), 57 + int(pulse*8), width=3)
        for j in range(5):
            px = (120 + j*79 - t*5) % 560 - 30
            pygame.draw.line(overlay, (255, 255, 255, 30+j*4), (px, 614+j*10), (px+43,614+j*10), 1)
    elif est.etapa == 'fim':
        fade = min(1.0,t/42)
        for j in range(6):
            a = 2*math.pi*j/6 + t*0.025
            x = 225 + int(math.cos(a)*(68 + 12*fade))
            y = 424 + int(math.sin(a)*(68 + 12*fade))
            pygame.draw.circle(overlay, (255, 215, 94, int(90*fade)), (x,y), 5)
    tela.blit(overlay, (0,0))

def _personagem_animado(tela,est,y):
    """Animação articulada/procedural SOMENTE na POC: braços e pernas em fase.

    Não altera a classe do jogador, a física ou as hitboxes do jogo.
    """
    import pygame
    t=est.tick
    agacha=est.etapa=='agachar'
    salto=est.etapa=='pulo' and est.saltos>0
    fase=math.sin(t*0.23)
    base_y = 570 if agacha else y + 38
    sombra=pygame.Surface((94,19),pygame.SRCALPHA)
    pygame.draw.ellipse(sombra,(1,9,24,110),(2,4,87,11))
    tela.blit(sombra,(87,607))
    if agacha:
        pygame.draw.ellipse(tela,(29,173,189),(95,564,75,29))
        pygame.draw.ellipse(tela,GOLD,(151,555,20,18))
        pygame.draw.circle(tela,(22,49,66),(160,562),3)
        pygame.draw.line(tela,(11,42,58),(102,589),(165,589),4)
        return
    # Suavização determinística das pernas e braços, sem impacto em eventos.
    amp=0 if salto or est.etapa in ('abertura','fim') else 11
    leg_a=int(amp*fase);leg_b=-leg_a
    pygame.draw.line(tela,(39,221,205),(121,base_y),(114+leg_a,base_y+29),9)
    pygame.draw.line(tela,(27,169,200),(142,base_y),(146+leg_b,base_y+29),9)
    pygame.draw.line(tela,(10,29,45),(110+leg_a,base_y+30),(121+leg_a,base_y+30),6)
    pygame.draw.line(tela,(10,29,45),(143+leg_b,base_y+30),(154+leg_b,base_y+30),6)
    pygame.draw.rect(tela,(22,55,74),(111,y+4,43,47),border_radius=10)
    pygame.draw.rect(tela,CYAN,(115,y+7,35,42),border_radius=9)
    pygame.draw.line(tela,(255,204,81),(115,y+19),(106-leg_a//2,y+31),8)
    pygame.draw.line(tela,(255,204,81),(148,y+21),(157-leg_b//2,y+32),8)
    pygame.draw.circle(tela,GOLD,(132,y-12),20)
    pygame.draw.rect(tela,(25,51,75),(123,y-17,31,10),border_radius=4)
    pygame.draw.rect(tela,(253,93,112),(143,y-15,6,5),border_radius=2)
    # Pequena trilha na saída da fase de salto: só visual.
    if salto:
        for i in range(3):
            pygame.draw.circle(tela,(71,208,212),(107-i*11,y+44+i*6),2)

def _transicao_suave_poc(tela,est):
    """Fade curto de 15 quadros ao entrar em qualquer etapa; apenas desenho."""
    import pygame
    alpha=max(0,int(170*(1-min(est.tick,15)/15)))
    if alpha:
        layer=pygame.Surface((W,H),pygame.SRCALPHA)
        layer.fill((6,16,35,alpha))
        tela.blit(layer,(0,0))

def desenhar(tela,est,fonts):
    import pygame
    t=est.tick
    tela.fill(SKY)
    fundo=_fundo_original()
    if fundo is not None:
        tela.blit(fundo,(0,0))
        veil=pygame.Surface((W,H),pygame.SRCALPHA)
        veil.fill((8,15,29,105))
        tela.blit(veil,(0,0))
    else:
        for i in range(18):
            x=(i*61-int(t*.24))%500
            pygame.draw.rect(tela,(27,59,81),(x,310+(i%4)*45,32,320))
    # Trilha e acabamento visual do protótipo; sem ler estado do jogo.
    pygame.draw.rect(tela,(21,32,49),(0,610,W,190))
    pygame.draw.line(tela,CYAN,(0,608),(W,608),4)
    for i in range(7):
        pygame.draw.rect(tela,(126,168,166),((i*85-t*3)%560-45,695,33,5))
    pygame.draw.rect(tela,(7,16,30),(12,14,426,186),border_radius=14)
    pygame.draw.rect(tela,(44,177,180),(12,14,426,186),width=2,border_radius=14)
    # jogador estilizado provisório e dois perigos didáticos roteirizados
    y=534
    if est.etapa=='pulo': y-=int(70*abs(math.sin(t*.065))) if est.saltos else 0
    _personagem_animado(tela, est, y)
    if est.etapa in ('pulo','agachar'):
        obstacle_x=310
        if est.etapa=='pulo':
            pygame.draw.polygon(tela,(237,103,122),[(obstacle_x,605),(obstacle_x+45,547),(obstacle_x+92,605)])
        else:
            pygame.draw.line(tela,(255,90,104),(obstacle_x,553),(obstacle_x+96,553),8)
            pygame.draw.rect(tela,(75,215,225),(obstacle_x+8,524,10,62))
            pygame.draw.rect(tela,(75,215,225),(obstacle_x+80,524,10,62))
    pygame.draw.rect(tela,(12,27,46),(16,17,418,174),border_radius=16)
    pygame.draw.rect(tela,(57,128,143),(16,17,418,174),width=2,border_radius=16)
    texto(tela,fonts['tiny'],'PIXEL RUSH  /  APRESENTACAO v3.264.0',32,34,CYAN)
    if est.etapa=='abertura':
        titulo='A CORRIDA COMECA';sub='Uma abertura cinematografica curta'
        info='Inicie ou pule a abertura; o treino continua'
    elif est.etapa=='pulo':
        titulo='1 / 2  PULE';sub='Um obstaculo no caminho!'
        info='Pressione ESPACO ou o botao PULAR'
    elif est.etapa=='agachar':
        titulo='2 / 2  AGACHE';sub='Um laser no alto!'
        info='Pressione SETA BAIXO ou o botao AGACHAR'
    else:
        titulo='PRONTO PARA CORRER';sub='Voce completou a demonstracao'
        info='Nenhuma moeda ou save foi alterado'
    texto(tela,fonts['head'],titulo,31,73,GOLD)
    texto(tela,fonts['body'],sub,31,114)
    texto(tela,fonts['small'],info,31,151,CYAN)
    _efeitos_poc(tela,est)
    _apresentacao_premium(tela,est)
    _animacao_cinematografica_3262(tela,est)
    if est.etapa=='abertura':
        # A escolha pula apenas a apresentação, nunca as instruções.
        pygame.draw.rect(tela,(23,37,58),(16,638,418,54),border_radius=11)
        pygame.draw.rect(tela,(77,178,183),(16,638,418,54),width=2,border_radius=11)
        texto(tela,fonts['body'],'PULAR ABERTURA  >>',225,664,WHITE,True)
    pygame.draw.rect(tela,(17,43,67),(16,717,418,65),border_radius=13)
    pygame.draw.rect(tela,(67,193,192),(16,717,418,65),width=2,border_radius=13)
    botao={'abertura':'INICIAR','pulo':'PULAR','agachar':'AGACHAR','fim':'REINICIAR'}[est.etapa]
    texto(tela,fonts['button'],botao,225,749,GOLD,True)
    if est.etapa!='abertura':texto(tela,fonts['small'],'TREINO INTEGRADO  /  SEM RECOMPENSAS',225,671,WHITE,True)

def executar(frames=0,captura=None,simular=False,pular_abertura=False):
    import pygame
    pygame.init();screen=pygame.display.set_mode((W,H));pygame.display.set_caption('Pixel Rush - Tutorial POC v3.264.0 (isolado)')
    fonts={'tiny':pygame.font.SysFont('arial',14,bold=True),'small':pygame.font.SysFont('arial',15),
           'body':pygame.font.SysFont('arial',18),'head':pygame.font.SysFont('arial',26,bold=True),
           'button':pygame.font.SysFont('arial',23,bold=True)}
    est=Estado();
    if pular_abertura:est.acao('pular_abertura')
    clock=pygame.time.Clock();q=0;running=True
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:running=False
            elif event.type==pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE,pygame.K_RETURN,pygame.K_UP):
                    est.acao('iniciar' if est.etapa=='abertura' else 'pular' if est.etapa=='pulo' else 'reiniciar' if est.etapa=='fim' else 'avancar')
                elif event.key in (pygame.K_DOWN,pygame.K_s):est.acao('agachar')
                elif event.key==pygame.K_p and est.etapa=='abertura':est.acao('pular_abertura')
                elif event.key==pygame.K_ESCAPE:running=False
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if est.etapa=='abertura' and pygame.Rect(16,638,418,54).collidepoint(event.pos):
                    est.acao('pular_abertura')
                elif pygame.Rect(16,717,418,65).collidepoint(event.pos):
                    est.acao({'abertura':'iniciar','pulo':'pular','agachar':'agachar','fim':'reiniciar'}[est.etapa])
        if simular and q in ((25,40) if pular_abertura else (10,25,40)):
            est.acao({10:'iniciar',25:'pular',40:'agachar'}[q])
        est.progredir();desenhar(screen,est,fonts);pygame.display.flip();q+=1
        if frames and q>=frames:running=False
        clock.tick(60 if not os.getenv('SDL_VIDEODRIVER')=='dummy' else 0)
    if captura:
        Path(captura).parent.mkdir(parents=True,exist_ok=True)
        pygame.image.save(screen,str(captura))
    out=est.quadro();pygame.quit();return out

def main():
    ap=argparse.ArgumentParser(description='POC de tutorial em Pygame, inteiramente independente')
    ap.add_argument('--frames',type=int,default=0,help='0 = interativo')
    ap.add_argument('--captura',type=Path)
    ap.add_argument('--simular',action='store_true',help='Cliques didáticos artificiais para smoke test')
    ap.add_argument('--pular-abertura',action='store_true',help='Salta somente a abertura no teste')
    a=ap.parse_args();print(executar(a.frames,a.captura,a.simular,a.pular_abertura))
if __name__=='__main__':main()
