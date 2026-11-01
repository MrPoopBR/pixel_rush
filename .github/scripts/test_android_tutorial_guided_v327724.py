"""QA v3.277.24: passos 60Hz, pausa, swipe e sucesso apos obstaculo."""
import ast
import os
from pathlib import Path
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame
pygame.init()
pygame.display.set_mode((450,800))

class Perigo:
    def __init__(self,x):
        self.rect=pygame.Rect(x,620,34,45)

class Jogador:
    def __init__(self):
        self.rect=pygame.Rect(40,650,80,80)
        self.no_chao=True
        self.descida_rapida=False
        self.pulos=0
    def pular(self,*a):
        self.no_chao=False
        self.pulos+=1
    def iniciar_descida_rapida(self,*a):
        if not self.no_chao:
            self.descida_rapida=True

class Base:
    def __init__(self,jogador):
        self.jogador=jogador
        self.ativo=True
        self.etapa="pular"
        self.etapa_indice=0
        self.fase_recuperacao=None
        self._etapa_preparada=False
        self.objetos=[]
        self.sucesso=False
        self.ticks=0
        self.largura,self.altura=450,800
        self.swipe_feito=False
        self.aviso_erro_ate=-1
        self._aviso_erro_inicio=0
        self.idioma="pt_BR"
        self.contagem_coletas=0
        self.textos_ui={"textos":{x:(x,"instrucao") for x in (
            "pular","pular_longo","agachar","swipe_down","moedas","letras")},
            "dicas":{x:("TECLA","DESLIZE PARA BAIXO") for x in (
            "pular","pular_longo","agachar","swipe_down","moedas","letras")},
            "feedback":{x:"CERTO" for x in (
            "pular","pular_longo","agachar","swipe_down","moedas","letras")}}
        self.render_capturado=[]
    def _preparar(self,*a):
        self.objetos=[Perigo(self.jogador.rect.right+165)]
        self._etapa_preparada=True
        self.sucesso=False
        self.swipe_feito=False
    def processar_evento(self,e,*a):
        if e.type in (pygame.FINGERDOWN,pygame.KEYDOWN):
            if self.etapa in ("pular","pular_longo"):
                self.jogador.pular()
                self.sucesso=True
            if self.etapa=="agachar":self.sucesso=True
        return True
    def atualizar(self,*a):
        self.ticks+=1
        for obj in self.objetos: obj.rect.x-=6
        if self.swipe_feito:self.sucesso=True
        return (0,False)
    def _encaixar_linhas(self,txt,w,h,tam=17):
        f=pygame.font.Font(None,tam)
        return f,[str(txt)[:50]],f.get_linesize()
    def _render_texto(self,f,txt,cor):
        self.render_capturado.append(txt)
        return f.render(txt,True,cor)

root=Path(__file__).resolve().parents[2]
main=ast.parse((root/"PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py").read_text("utf-8"))
texto=(root/"PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py").read_text("utf-8")
assert "MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15" in texto
assert "from pixelrush_tutorial_guia_prod_v327724 import TutorialCorrida" in texto
assert "if not (tutorial_corrida and tutorial_corrida.ativo):" in texto

tree=ast.parse((root/"pixelrush_tutorial_guia_prod_v327724.py").read_text("utf-8"))
classe=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="TutorialCorrida")
scope={"_Anterior":Base,"_OBSTACULOS":frozenset(("pular","pular_longo","agachar","swipe_down")),
       "_USAR_GESTOS":True,"ETAPAS":("pular","pular_longo","agachar","swipe_down","moedas","letras"),
       "pygame":pygame,"instrucoes_plataforma":lambda *_:"INSTRUCAO",
       "mensagem_repetir":lambda *_:"TENTE NOVAMENTE"}
exec(compile(ast.Module(body=[classe],type_ignores=[]),"<guided>","exec"),scope)
Tutorial=scope["TutorialCorrida"]

def step(t):
    return t.atualizar(t.jogador,None,None,None,None,None,None,None,1,0)
def event(t,kind,**kwargs):
    return t.processar_evento(pygame.event.Event(kind,kwargs))
def pause(t):
    for _ in range(20):
        step(t)
        if t._pausa_comando:return
    raise AssertionError("A pausa nao foi ativada")

j=Jogador();t=Tutorial(j)
event(t,pygame.FINGERDOWN,x=.2,y=.2)
assert not j.pulos
pause(t)
assert t._pausa_comando
x=t.objetos[0].rect.x
for _ in range(20):
    step(t)
assert t.objetos[0].rect.x==x
event(t,pygame.FINGERDOWN,x=.2,y=.2)
assert j.pulos==1 and t._comando_liberado and not t._pausa_comando
assert not t._passagem_validada()
t.sucesso=True
t.objetos[0].rect.x=j.rect.right+12
assert not t._passagem_validada()
t.objetos[0].rect.right=j.rect.left-40
assert t._passagem_validada()
t.desenhar(pygame.Surface((450,800)))
assert "CERTO" in t.render_capturado

j=Jogador();t=Tutorial(j)
t.etapa="swipe_down"
pause(t)
assert j.pulos==1 and not j.no_chao and t._salto_automatico
assert t._pausa_comando
x=t.objetos[0].rect.x
for _ in range(15):step(t)
assert x==t.objetos[0].rect.x
event(t,pygame.FINGERDOWN,x=.2,y=.2)
event(t,pygame.FINGERUP,x=.2,y=.22)
assert not t.swipe_feito and t._pausa_comando
event(t,pygame.KEYDOWN,key=pygame.K_DOWN)
assert not t.swipe_feito
event(t,pygame.FINGERDOWN,x=.2,y=.2)
event(t,pygame.MOUSEBUTTONUP,button=1,pos=(90,200))
assert t._pausa_comando, "mouse sintetico nao deve liberar"
event(t,pygame.FINGERUP,x=.2,y=.4)
assert t.swipe_feito and j.descida_rapida and not t._pausa_comando
step(t)
assert t.sucesso and not t._passagem_validada()
t.objetos[0].rect.right=j.rect.left-40
assert t._passagem_validada()
print("APROVADO: 8 passos Android, pausa antes do perigo, sem toque precoce, swipe real e passagem")
pygame.quit()
