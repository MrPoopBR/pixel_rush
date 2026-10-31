"""QA pygame-ce dummy: morte didatica, camera reversa e HUD de orientacao."""
import ast
import os
from pathlib import Path
from types import SimpleNamespace
import pygame

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
pygame.init()
pygame.display.set_mode((450, 800))

class Perigo(pygame.sprite.Sprite):
    def __init__(self,x):
        super().__init__()
        self.rect=pygame.Rect(x,677,60,53)
        self._x=float(x)
        self.image=pygame.Surface((60,53))
    def update(self,v):
        self._x-=v
        self.rect.x=int(self._x)
        if self.rect.right < -90:self.kill()

class Jogador:
    def __init__(self):
        self.rect=pygame.Rect(40,650,80,80)
        self.chao_y=730
        self.no_chao=True
        self.agachado=False
        self.morrendo=False
        self.tempo_morte=0
        self.velocidade_y=0
        self.descida_rapida=False
        self.coyote_ticks=0
        self.buffer_pulo_ticks=0
        self.angulo_rotacao=0
        self._visual_dirty=False
        self.deaths=0
        self.death_frames=0
    def obter_hitbox(self):
        return pygame.Rect(self.rect.x+23,self.rect.y+18,34,49)
    def iniciar_morte(self):
        self.deaths+=1
        self.morrendo=True
        self.tempo_morte=60
        self.velocidade_y=-12
    def update(self, *_args, **_kwargs):
        if self.morrendo:
            self.death_frames+=1
            self.tempo_morte-=1
            self.angulo_rotacao+=18
            self.rect.x-=2
            self.rect.y+=3

class Base:
    def __init__(self,jogador):
        self.jogador=jogador
        self.ativo=True
        self.etapa='pular'
        self.ticks=0
        self.ticks_etapa=0
        self.sucesso=False
        self.objetos=[]
        self.tempo_confirmacao=0
        self._etapa_preparada=False
        self.toque_ativo=False
        self.swipe_iniciado=None
        self.segurar_pulo=False
        self.segurar_baixo=False
        self.largura=450
        self.altura=800
        self.idioma='pt_BR'
        self.textos_ui={'textos':{'pular':('PULO','Pule')},
                        'dicas':{'pular':('ESPAÇO','TOQUE PARA PULAR')},
                        'modos':{'teclado':'TECLADO'}}
    def _preparar(self,todos,letras,palavra):
        for obj in self.objetos:obj.kill()
        self.objetos=[Perigo(self.jogador.rect.right+165)]
        todos.add(*self.objetos)
        self._etapa_preparada=True
        self.ticks_etapa=0
        self.sucesso=False
    def atualizar(self,jogador,fundo,todos,letras,palavra,particulas,
                  pool,som,volume,frame):
        self.ticks+=1
        self.ticks_etapa+=1
        return 0,False
    def fonte_tutorial(self,tamanho):
        return pygame.font.SysFont('arial',tamanho)
    def processar_evento(self,*args,**kwargs):
        raise AssertionError('Entrada jamais deve chegar na base durante a animacao')

class Teste(TutorialBase if False else Base):
    pass

mod=ast.parse(Path('pixelrush_tutorial_prod_v32771.py').read_text(encoding='utf-8'))
cl=next(n for n in mod.body if isinstance(n,ast.ClassDef) and n.name=='TutorialCorrida')
ctx={'_TutorialBase':Base,'_USAR_GESTOS':False,'pygame':pygame,
     'mensagem_repetir':lambda idioma:'TENTE NOVAMENTE',
     'instrucoes_plataforma':lambda idioma,etapa,toque,ui:'Pule agora',
     'ETAPAS':('pular','pular_longo','agachar','swipe_down','moedas','letras')}
exec(compile(ast.Module(body=[cl],type_ignores=[]),'<tutorial-atual>', 'exec'),ctx)
Tutorial=ctx['TutorialCorrida']
t=Tutorial(Jogador())
todos=pygame.sprite.Group()
fundo=SimpleNamespace(desloc_chao=400.0,camada_perto=0.0,camada_longe=0.0,
                       _desloc_arte=100.0,_desloc_arte_fundo=100.0)
def passo():
    return t.atualizar(t.jogador,fundo,todos,None,None,None,None,None,1.0,t.ticks)

passo()
assert t.objetos[0].rect.x == t.jogador.rect.right+165-6
for i in range(90):
    passo()
    if t.fase_recuperacao=='morte':break
assert t.fase_recuperacao=='morte', 'Colisao real inicia estado morte'
assert t.jogador.deaths==1 and t.jogador.morrendo
antes=t.objetos[0].rect.x
for i in range(24):
    assert t.processar_evento(pygame.event.Event(pygame.KEYDOWN,{'key':pygame.K_SPACE}))
    passo()
assert t.jogador.death_frames==24, 'Animacao do proprio jogador deve rodar 24 passos'
assert t.fase_recuperacao=='reverso'
assert t.objetos[0].rect.x==antes, 'Perigo congelado durante a morte'
pre_chao=fundo.desloc_chao
xs=[]
for i in range(24):
    passo()
    xs.append(t.objetos[0].rect.x)
assert xs==sorted(xs), 'Retrocesso deve mover o perigo so para direita'
assert t.fase_recuperacao is None and t.tentativas==1
assert not t.jogador.morrendo and t.jogador.no_chao and t.jogador.tempo_morte==0
assert t.objetos[0].rect.x == t.jogador.rect.right+230
assert fundo.desloc_chao != pre_chao and t.aviso_erro_ate > t.ticks
surface=pygame.Surface((450,800))
pixels=[]
for offs in (0,24):
    t.ticks=(t.ticks//48)*48+offs
    surface.fill((0,0,0))
    t.desenhar(surface)
    pixels.append(pygame.image.tostring(
        surface.subsurface((12, 94, 426, 119)), 'RGB'))
assert pixels[0]!=pixels[1], 'Texto de alerta deve piscar'
assert t.jogador.deaths==1, 'Sem Game Over e sem nova morte no retrocesso'
print('APROVADO: morte 24 ticks, camera em reverso 24 ticks, 230 px, 1 retry, comando bloqueado e aviso piscante')
pygame.quit()
