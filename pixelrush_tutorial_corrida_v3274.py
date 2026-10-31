"""Tutorial obrigatório da primeira corrida — Pixel Rush v3.274.0.

Usa o Jogador, parallax, ObstaculoTerrestre, ObstaculoVoador,
Moeda, LetraColetavel e PalavraDaPartida ORIGINAIS do jogo.
Não cria janela, não troca de estado, não muda física ou colisões normais.
Obstáculos roteirizados são didáticos e não fatais. Sem timeout/skip.
"""
from __future__ import annotations
import random
import pygame
from pixelrush_letras_v3218 import LetraColetavel

ETAPAS = ("pular", "pular_longo", "agachar", "swipe_down", "moedas", "letras")
TEXTOS = {
 "pular": ("01 / 06   PULO", "Toque, clique ou aperte ESPAÇO para saltar sobre o obstáculo."),
 "pular_longo": ("02 / 06   PULO LONGO", "SEGURE o toque ou ESPAÇO por mais tempo para atravessar o obstáculo duplo."),
 "agachar": ("03 / 06   AGACHAR", "Segure BAIXO / S ou o botão de agachar para passar sob o drone."),
 "swipe_down": ("04 / 06   SWIPE-DOWN", "No ar, deslize o dedo para BAIXO para descer rápido. No teclado: BAIXO."),
 "moedas": ("05 / 06   MOEDAS", "Recolha as moedas. Elas servem para comprar skins, pets e melhorias na LOJA."),
 "letras": ("06 / 06   LETRAS", "Pegue as letras na ordem: complete a palavra para ganhar moedas bônus!"),
}

class TutorialCorrida:
    """Uma única corrida: só passa de lição com sucesso real, nunca mata."""
    def __init__(self, jogador, largura=450, altura=800, *, classe_terrestre=None,
                 classe_voador=None, classe_moeda=None):
        self.ativo=True
        self.etapa_indice=0
        self.ticks=0
        self.ticks_etapa=0
        self.sucesso=False
        self.tempo_confirmacao=0
        self.segurar_pulo=False
        self.segurar_baixo=False
        self.hold_pulo=0
        self.hold_baixo=0
        self.swipe_iniciado=None
        self.swipe_feito=False
        self.toque_ativo=False
        self.objetos=[]
        self.proximo_objeto=None
        self.contagem_coletas=0
        self.credito=0
        self.classe_terrestre=classe_terrestre
        self.classe_voador=classe_voador
        self.classe_moeda=classe_moeda
        self.largura=largura
        self.altura=altura
        self.jogador=jogador
        self.corrida_continua=False
        self._etapa_preparada=False

    @property
    def etapa(self):
        return ETAPAS[self.etapa_indice] if self.ativo else None

    def _somente_objeto_original(self, factory):
        # Construtores antigos de sprites usam random para arte; não alterar
        # a sequência global do RNG que governa a corrida normal.
        state=random.getstate()
        try: return factory()
        finally: random.setstate(state)

    def _preparar(self, todos, letras, palavra):
        self._etapa_preparada=True
        self.ticks_etapa=0
        self.sucesso=False
        self.tempo_confirmacao=0
        self.hold_pulo=self.hold_baixo=0
        self.segurar_pulo=self.segurar_baixo=False
        self.swipe_iniciado=None
        self.swipe_feito=False
        for objeto_antigo in self.objetos:
            objeto_antigo.kill()
        self.objetos=[]
        self.proximo_objeto=None
        etapa=self.etapa
        base_x=self.jogador.rect.right+165
        if etapa in ('pular','pular_longo'):
            quantidade=2 if etapa=='pular_longo' else 1
            for i in range(quantidade):
                obj=self._somente_objeto_original(lambda:self.classe_terrestre(base_x+i*66,1))
                todos.add(obj)
                self.objetos.append(obj)
        elif etapa in ('agachar','swipe_down'):
            obj=self._somente_objeto_original(lambda:self.classe_voador(base_x,'cidade'))
            obj.rect.y=self.jogador.chao_y-118
            todos.add(obj)
            self.objetos.append(obj)
        elif etapa=='letras':
            # Mesma palavra e mesma classe coletável da corrida normal.
            self.contagem_coletas=0
            palavra.ativo=None
        elif etapa=='moedas':
            self.contagem_coletas=0

    def processar_evento(self, evento, converter=None, som=None, volume=1.0):
        """Somente gestos esperados têm efeito; comandos errados são ignorados."""
        if not self.ativo: return False
        et=self.etapa
        tipo=evento.type
        jump=(pygame.K_SPACE,pygame.K_UP,pygame.K_w)
        down=(pygame.K_DOWN,pygame.K_s)
        if tipo==pygame.KEYDOWN:
            if evento.key in jump and et in ('pular','pular_longo') and self.jogador.no_chao:
                self.jogador.pular(som,volume)
                self.segurar_pulo=True
                if et=='pular': self.sucesso=True
            elif evento.key in down:
                if et=='agachar': self.segurar_baixo=True
                elif et=='swipe_down' and not self.jogador.no_chao:
                    self.jogador.iniciar_descida_rapida(som,volume)
                    self.swipe_feito=self.jogador.descida_rapida
            return True
        if tipo==pygame.KEYUP:
            if evento.key in jump:self.segurar_pulo=False
            if evento.key in down:self.segurar_baixo=False
            return True
        if tipo in (pygame.MOUSEBUTTONDOWN,pygame.FINGERDOWN):
            if tipo==pygame.MOUSEBUTTONDOWN and getattr(evento,'button',0)!=1:return True
            pos=(evento.x*self.largura, evento.y*self.altura) if tipo==pygame.FINGERDOWN else (converter(evento.pos) if converter else evento.pos)
            self.swipe_iniciado=(int(pos[0]),int(pos[1])); self.toque_ativo=True
            if et in ('pular','pular_longo') and self.jogador.no_chao:
                self.jogador.pular(som,volume)
                self.segurar_pulo=True
                if et=='pular': self.sucesso=True
            if et=='agachar':self.segurar_baixo=True
            return True
        if tipo in (pygame.FINGERMOTION,pygame.MOUSEMOTION) and self.toque_ativo and self.swipe_iniciado:
            pos=(evento.x*self.largura, evento.y*self.altura) if tipo==pygame.FINGERMOTION else (converter(evento.pos) if converter else evento.pos)
            if et=='swipe_down' and pos[1]-self.swipe_iniciado[1]>=45 and not self.jogador.no_chao:
                self.jogador.iniciar_descida_rapida(som,volume)
                self.swipe_feito=self.jogador.descida_rapida
            return True
        if tipo in (pygame.MOUSEBUTTONUP,pygame.FINGERUP):
            self.segurar_pulo=self.segurar_baixo=False
            self.toque_ativo=False;self.swipe_iniciado=None
            return True
        if tipo==pygame.JOYBUTTONDOWN:
            if evento.button in (0,2) and et in ('pular','pular_longo') and self.jogador.no_chao:
                self.jogador.pular(som,volume);self.segurar_pulo=True
                if et=='pular':self.sucesso=True
            elif evento.button in (1,3):
                if et=='agachar':self.segurar_baixo=True
                if et=='swipe_down' and not self.jogador.no_chao:
                    self.jogador.iniciar_descida_rapida(som,volume)
                    self.swipe_feito=self.jogador.descida_rapida
            return True
        if tipo==pygame.JOYBUTTONUP:
            if evento.button in (0,2):self.segurar_pulo=False
            if evento.button in (1,3):self.segurar_baixo=False
            return True
        return True

    def _coletavel(self,todos,letras,palavra):
        x=self.jogador.rect.right+180
        y=self.jogador.chao_y-self.jogador.base_h//2
        if self.etapa=='moedas':
            obj=self._somente_objeto_original(lambda:self.classe_moeda(x,y))
        else:
            obj=LetraColetavel(palavra.palavra[palavra.progresso],x,y)
            palavra.ativo=obj
            letras.add(obj)
        todos.add(obj)
        self.proximo_objeto=obj

    def atualizar(self, jogador, fundo, todos, letras, palavra, particulas,
                  pool, som, volume, frame):
        """Retorna (moedas_ganhas, concluiu). Não aplica collision/death/gameover."""
        if not self.ativo:return 0,False
        if not self._etapa_preparada:self._preparar(todos,letras,palavra)
        self.ticks+=1;self.ticks_etapa+=1
        et=self.etapa;ganho=0
        # Usa a física e o sprite exatos do jogo normal. Sem buracos e sem morte.
        if et=='swipe_down' and self.ticks_etapa>=25 and jogador.no_chao and not self.swipe_feito:
            jogador.pular(som,volume)
        jogador.update(6.0,frame,self.segurar_pulo,
                       self.segurar_baixo and et=='agachar',particulas,pool,som,volume,pode_pousar=True)
        fundo.update(6.0,self.ticks//5)
        if et=='pular_longo':
            if self.segurar_pulo and not jogador.no_chao:
                self.hold_pulo+=1
            if self.hold_pulo>=19:self.sucesso=True
            if jogador.no_chao and not self.sucesso and self.ticks_etapa>24:
                self.hold_pulo=0
        elif et=='agachar':
            if jogador.agachado and self.segurar_baixo:self.hold_baixo+=1
            else:self.hold_baixo=0
            if self.hold_baixo>=15:self.sucesso=True
        elif et=='swipe_down':
            if self.swipe_feito:self.sucesso=True
        if et in ('pular','pular_longo','agachar','swipe_down'):
            if self.sucesso:
                for obj in self.objetos:
                    if obj.alive():
                        # Exclusivo das barreiras didáticas: não modifica a velocidade
                        # nem a física de nenhum obstáculo da corrida normal.
                        deslocamento = getattr(self, 'passo_obstaculo', 6)
                        if hasattr(obj,'_posicao_mundo_x'):obj._posicao_mundo_x-=float(deslocamento)
                        obj.rect.x-=int(deslocamento)
                        if hasattr(obj,'renderizar_visual'):obj.renderizar_visual()
                if all(obj.rect.right<jogador.rect.left-35 for obj in self.objetos):
                    self.tempo_confirmacao+=1
            else:
                # Perigo aguarda a ação correta, jamais atravessa o jogador.
                for obj in self.objetos:
                    if hasattr(obj,'renderizar_visual'):obj.renderizar_visual()
        else:
            if et=='letras' and palavra.concluida:
                self.sucesso=True
            if not self.sucesso and (self.proximo_objeto is None or not self.proximo_objeto.alive()):
                self._coletavel(todos,letras,palavra)
            obj=self.proximo_objeto
            if obj is not None:
                obj.rect.x-=5
            if obj is not None and hasattr(obj,'_x_float'):obj._x_float=float(obj.rect.x)
            if obj is not None and obj.rect.colliderect(jogador.rect):
                if et=='moedas':
                    obj.kill();ganho+=1;self.contagem_coletas+=1
                else:
                    coletou,completa,bonus=palavra.coletar(jogador.rect,self.ticks//5)
                    if coletou:
                        self.contagem_coletas+=1;ganho+=bonus
                self.proximo_objeto=None
            elif obj is not None and obj.rect.right < jogador.rect.left:
                # Repetir sem punição se um item passar fora da hitbox.
                obj.kill();self.proximo_objeto=None
            if et=='moedas' and self.contagem_coletas>=3:self.sucesso=True
            if et=='letras' and palavra.concluida:self.sucesso=True
            if self.sucesso:self.tempo_confirmacao+=1
        if self.sucesso and self.tempo_confirmacao>=16 and (jogador.no_chao or et in ('moedas','letras')):
            self.etapa_indice+=1
            self._etapa_preparada=False
            if self.etapa_indice==len(ETAPAS):
                self.ativo=False
                self.corrida_continua=True
                return ganho,True
        return ganho,False

    def desenhar(self,tela,fonte=None):
        if not self.ativo:return
        # v3.277: textos opcionais por instância, sem alterar a lição ou globais.
        ui=getattr(self,'textos_ui',{})
        titulo,explicacao=ui.get('textos',TEXTOS)[self.etapa]
        fonte_local=getattr(self,'fonte_tutorial',None)
        f_titulo=(fonte_local(21) if fonte_local else (fonte or pygame.font.SysFont('arial',21,bold=True)))
        f_texto=fonte_local(16) if fonte_local else pygame.font.SysFont('arial',16,bold=True)
        w=tela.get_width()
        painel=pygame.Surface((w-24,94),pygame.SRCALPHA)
        pygame.draw.rect(painel,(10,24,39,232),painel.get_rect(),border_radius=13)
        pygame.draw.rect(painel,(95,218,244,245),painel.get_rect(),2,border_radius=13)
        for i in range(len(ETAPAS)):
            cor=(105,239,174) if i<self.etapa_indice else ((255,217,111) if i==self.etapa_indice else (61,83,103))
            pygame.draw.rect(painel,cor,(12+i*(w-50)//6,9,(w-58)//6,5),border_radius=2)
        if fonte_local:
            f_titulo=self.ajustar_fonte_tutorial(titulo,w-50,21)
        painel.blit(f_titulo.render(titulo,True,(255,226,131)),(12,20))
        # Quebra automática do texto, sem esconder o cenário ou os obstáculos.
        if fonte_local:
            f_texto,linhas=self.quebrar_texto_tutorial(explicacao,w-50,16,2)
        else:
            palavras=explicacao.split();linhas=[];linha=''
            for p in palavras:
                candidato=(linha+' '+p).strip()
                if f_texto.size(candidato)[0]>w-50 and linha:
                    linhas.append(linha);linha=p
                else:linha=candidato
            if linha:linhas.append(linha)
        for i,txt in enumerate(linhas[:2]):painel.blit(f_texto.render(txt,True,(224,244,252)),(12,50+i*18))
        # A HUD real ocupa o topo e a palavra, por isso o painel fica abaixo.
        tela.blit(painel,(12,226))
        # Seta para o perigo real da lição; não é um segundo personagem.
        if self.objetos and not self.sucesso:
            alvo=self.objetos[0].rect
            x=max(25,min(w-25,alvo.centerx));y=max(218,alvo.top-42)
            pygame.draw.polygon(tela,(255,218,100),((x,y+20),(x-12,y),(x+12,y)))
        elif self.etapa in ('moedas','letras'):
            txt=f"{ui.get('coletadas','COLETADAS')}: {self.contagem_coletas}/{3 if self.etapa=='moedas' else 5}"
            tela.blit(f_texto.render(txt,True,(255,236,149)),(23,332))
        if self.sucesso and self.tempo_confirmacao:
            texto_final=ui.get('continue','ÓTIMO! CONTINUE CORRENDO')
            fonte_final=self.ajustar_fonte_tutorial(texto_final,w-50,16) if fonte_local else f_texto
            tela.blit(fonte_final.render(texto_final,True,(142,251,192)),(25,347))
