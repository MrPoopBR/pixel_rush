# -*- coding: utf-8 -*-
"""Tutorial cinematográfico QA793: extensão das seis lições existentes, sem motor duplicado.

Princípios: usa Jogador/Parallax/Sprites do jogo, não grava save, não altera física
ou RNG da corrida normal, nunca causa Game Over. Renderiza UI sem Surface por
frame; textos usam cache do tutorial QA anteriores.
"""
import math
import pygame
from pixelrush_tutorial_guia_prod_v327724 import TutorialCorrida as _Anterior

_ETAPAS_EXTRA = (
    ("combo_moedas", "COMBO DE MOEDAS", "Pegue moedas em sequência: cada coleta renova a janela do COMBO e aumenta o multiplicador das recompensas."),
    ("febre", "MODO FEBRE", "Quase colisões e esquivas perfeitas carregam a FEBRE. Observe três desvios seguros automáticos e o brilho de ativação."),
    ("baus", "BAÚS DE TESOURO", "Baús raros dão recompensas extras. Eles aparecem próximos de rotas de risco: planeje a aproximação antes de coletar."),
    ("descanso", "RESPIRE E APROVEITE", "Entre desafios há corredores de moedas para recuperar o ritmo. Sua corrida normal começa depois desta lição."),
)
_DICAS = {
    "pular": ("TOQUE", "↑", "Um toque curto salta sobre o cone."),
    "pular_longo": ("SEGURE", "↑", "Segure para atravessar o cone e o hidrante."),
    "agachar": ("ABAIXO", "↓", "Mantenha pressionado BAIXO e passe sob o pombo."),
    "swipe_down": ("SEGURE + DESLIZE", "↓", "Primeiro segure para subir; no ar deslize para baixo."),
}
_CU = ((244, 207, 112), (128, 234, 245), (129, 231, 178))

class TutorialCorrida(_Anterior):
    """Conserva a herança da QA724: física, rebobinamento e seis gestos originais."""

    def __init__(self, *args, classe_bau=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.classe_bau = classe_bau
        self._intro_restante = 300
        self._extra_indice = -1
        self._extra_popup = False
        self._extra_preparada = False
        self._extra_timer = 0
        self._extra_coletados = 0
        self._extra_objs = []
        self._extra_reward = 0
        self._swipe_etapa = 0
        self._touch_y_tutorial = None
        self._swipe_inicio_segunda = None
        self.demo_febre = False
        self._ultimo_frame = 0
        self._instante_ui = 0
        self._popup_desde_ms = 0

    @property
    def etapa(self):
        if not self.ativo:
            return None
        if self._extra_indice >= 0:
            return _ETAPAS_EXTRA[self._extra_indice][0]
        return super().etapa

    def _preparar(self, todos, letras, palavra):
        res = super()._preparar(todos, letras, palavra)
        if self.etapa == "swipe_down":
            self._swipe_etapa = 0
            self._touch_y_tutorial = None
            self._swipe_inicio_segunda = None
            if self.objetos:
                # Segundo pombo: treino em dois tempos, usando o sprite real.
                pos = self.objetos[0].rect.left + 190
                obj = self._somente_objeto_original(lambda: self.classe_cidade(pos, "C2"))
                obj.rect.y = self.objetos[0].rect.y
                if hasattr(obj, "_base_y"):
                    obj._base_y = obj.rect.y
                todos.add(obj)
                self.objetos.append(obj)
        return res

    @staticmethod
    def _limpar_particulas_de_morte(particulas):
        # Kill devolve partículas ao pool e limpa TODOS os grupos de sprite.
        for sprite in tuple(particulas):
            sprite.kill()
        particulas.empty()

    def _reset_visual_jogador(self):
        jogador = self.jogador
        if jogador is None:
            return
        if getattr(jogador, "morrendo", False):
            jogador.morrendo = False
            jogador.tempo_morte = 0
            jogador.velocidade_y = 0
            jogador.no_chao = True
            jogador.rect.bottom = jogador.chao_y
        if hasattr(jogador, "_visual_dirty"):
            jogador._visual_dirty = True

    def _altura_do_toque(self, evento, converter):
        if evento.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            return float(evento.y) * self.altura
        if hasattr(evento,"pos"):
            pos=converter(evento.pos) if converter else evento.pos
            return float(pos[1])
        return None

    def _completar_descida_tutorial(self, som, volume):
        if self.jogador.no_chao:
            return
        self.jogador.iniciar_descida_rapida(som,volume)
        if self.jogador.descida_rapida:
            self.swipe_feito=True
            self.segurar_pulo=False
            self._comando_liberado=True
            self._pausa_comando=False
            self._swipe_etapa=3
            self._swipe_inicio_segunda=None

    def processar_evento(self, evento, converter=None, som=None, volume=1.0):
        if self._intro_restante > 0:
            return True
        if self._extra_indice >= 0:
            if self._extra_popup and evento.type in (
                    pygame.KEYDOWN, pygame.FINGERUP, pygame.MOUSEBUTTONUP,
                    pygame.JOYBUTTONDOWN):
                # Dedo solto da etapa anterior não pode pular a explicação.
                if (evento.type in (pygame.FINGERUP, pygame.MOUSEBUTTONUP) and
                        pygame.time.get_ticks() - self._popup_desde_ms < 220):
                    return True
                if evento.type == pygame.MOUSEBUTTONUP and getattr(evento,"button",1) != 1:
                    return True
                self._extra_popup=False
                self._extra_preparada=False
            return True

        if self.etapa == "swipe_down" and self.fase_recuperacao is None:
            tipo=evento.type
            y=self._altura_do_toque(evento,converter)
            if self._pausa_comando and self._swipe_etapa == 0:
                # PARTE 1: o jogador inicia o pulo longo na pausa didática.
                certo=((tipo==pygame.KEYDOWN and getattr(evento,"key",None)
                        in (pygame.K_SPACE,pygame.K_UP,pygame.K_w))
                       or (tipo==pygame.JOYBUTTONDOWN and getattr(evento,"button",None) in (0,2))
                       or tipo==pygame.FINGERDOWN
                       or (tipo==pygame.MOUSEBUTTONDOWN and getattr(evento,"button",1)==1))
                if certo and self.jogador.no_chao:
                    self.jogador.pular(som,volume)
                    self.segurar_pulo=True
                    self._salto_automatico=True
                    self._comando_liberado=True
                    self._pausa_comando=False
                    self._swipe_etapa=1
                    self._touch_y_tutorial=y
                return True

            if self._pausa_comando and self._swipe_etapa == 2:
                # PARTE 2: aceita também deslizar no MESMO contato, sem
                # exigir soltar o dedo depois do pulo longo.
                if tipo==pygame.KEYDOWN and getattr(evento,"key",None) in (pygame.K_DOWN,pygame.K_s):
                    self._completar_descida_tutorial(som,volume)
                    return True
                if tipo==pygame.JOYBUTTONDOWN and getattr(evento,"button",None) in (1,3):
                    self._completar_descida_tutorial(som,volume)
                    return True
                if tipo in (pygame.FINGERDOWN,pygame.MOUSEBUTTONDOWN):
                    if tipo!=pygame.MOUSEBUTTONDOWN or getattr(evento,"button",1)==1:
                        self._swipe_inicio_segunda=y
                    return True
                if tipo in (pygame.FINGERMOTION,pygame.MOUSEMOTION,pygame.FINGERUP,pygame.MOUSEBUTTONUP) and y is not None:
                    if self._swipe_inicio_segunda is None:
                        self._swipe_inicio_segunda=y
                    if y-self._swipe_inicio_segunda>=55:
                        self._completar_descida_tutorial(som,volume)
                    return True
                return True

            if self._swipe_etapa == 1 and tipo in (pygame.FINGERMOTION,pygame.MOUSEMOTION) and y is not None:
                self._touch_y_tutorial=y
            if self._swipe_etapa == 1 and tipo in (pygame.FINGERUP,pygame.MOUSEBUTTONUP,pygame.KEYUP,pygame.JOYBUTTONUP):
                self.segurar_pulo=False
                self._touch_y_tutorial=None
            return True
        return super().processar_evento(evento,converter,som,volume)

    def _iniciar_extra(self, todos):
        self._extra_preparada = True
        self._extra_timer = 0
        self._extra_coletados = 0
        self._extra_objs.clear()
        self.demo_febre = False
        j = self.jogador
        etapa = self.etapa
        if etapa in ("combo_moedas","descanso"):
            quantidade = 7 if etapa == "combo_moedas" else 12
            for i in range(quantidade):
                pos = j.rect.right + 145 + i * 35
                obj = self._somente_objeto_original(
                    lambda x=pos:self.classe_moeda(x,j.rect.centery))
                todos.add(obj)
                self._extra_objs.append(obj)
        elif etapa == "febre":
            for i in range(3):
                pos = j.rect.right + 165 + i * 210
                codigo = "C3" if i != 1 else "C4"
                obj = self._somente_objeto_original(
                    lambda x=pos,c=codigo:self.classe_cidade(x,c))
                todos.add(obj)
                self._extra_objs.append(obj)
        elif etapa == "baus" and self.classe_bau is not None:
            obj = self._somente_objeto_original(
                lambda:self.classe_bau(j.rect.right+165,j.rect.centery))
            todos.add(obj)
            self._extra_objs.append(obj)

    def _avancar_extra(self, todos):
        for obj in self._extra_objs:
            obj.kill()
        self._extra_objs.clear()
        self.demo_febre = False
        self._extra_indice += 1
        self._extra_popup = True
        self._popup_desde_ms = pygame.time.get_ticks()
        self._extra_preparada = False
        self._extra_timer = 0
        if self._extra_indice >= len(_ETAPAS_EXTRA):
            self._extra_indice = -1
            self.ativo = False
            self.corrida_continua = True
            return True
        return False

    def atualizar(self, jogador, fundo, todos, letras, palavra, particulas,
                  pool, som, volume, frame):
        self._ultimo_frame = frame
        if self._intro_restante > 0:
            self._intro_restante -= 1
            self.ticks += 1
            jogador.update(6.0,frame,False,False,particulas,pool,som,volume,pode_pousar=True)
            fundo.update(6.0,self.ticks//5)
            self._reset_visual_jogador()
            return 0,False
        if self._extra_indice < 0:
            if self.etapa=="swipe_down" and self.fase_recuperacao is None:
                if not self._etapa_preparada:
                    self._preparar(todos,letras,palavra)
                if self.objetos and self._swipe_etapa==0 and not self._pausa_comando:
                    distancia=self.objetos[0].rect.left-jogador.rect.right
                    if distancia <= 122:
                        self._pausa_comando=True
                        return 0,False
                if len(self.objetos)>1 and self._swipe_etapa==1 and not self._pausa_comando:
                    distancia=self.objetos[1].rect.left-jogador.rect.right
                    if distancia <= 168:
                        if jogador.no_chao:
                            # A lição impede pouso fatal antes da segunda manobra.
                            jogador.pular(som,volume)
                        self._pausa_comando=True
                        self._comando_liberado=False
                        self._swipe_etapa=2
                        self._swipe_inicio_segunda=self._touch_y_tutorial
                        return 0,False
            recuperando = self.fase_recuperacao is not None
            resultado = super().atualizar(
                jogador,fundo,todos,letras,palavra,particulas,pool,som,volume,frame)
            if recuperando or self.fase_recuperacao is not None:
                # Correção: nenhuma partícula de morte pode permanecer após o reverso.
                self._limpar_particulas_de_morte(particulas)
                if self.fase_recuperacao is None:
                    self._reset_visual_jogador()
            if resultado[1]:
                # O save só será gravado quando as etapas extras também terminarem.
                self.ativo = True
                self.corrida_continua = False
                self._extra_indice = 0
                self._extra_popup = True
                self._popup_desde_ms = pygame.time.get_ticks()
                self._extra_preparada = False
                self._extra_timer = 0
                return resultado[0],False
            return resultado

        self.ticks += 1
        if self._extra_popup:
            return 0,False
        if not self._extra_preparada:
            self._iniciar_extra(todos)
        self._extra_timer += 1
        jogador.update(6.0,frame,False,False,particulas,pool,som,volume,pode_pousar=True)
        fundo.update(6.0,self.ticks//5)
        self._reset_visual_jogador()
        etapa = self.etapa
        ganhos = 0
        if etapa in ("combo_moedas","descanso","baus"):
            for obj in self._extra_objs:
                if not obj.alive():
                    continue
                # Movimento didático independente: sem gerar perigos naturalmente.
                obj.rect.x -= 6
                if hasattr(obj,"_x_float"):
                    obj._x_float=float(obj.rect.x)
                if obj.rect.colliderect(jogador.rect):
                    obj.kill()
                    self._extra_coletados += 1
                    ganhos += 10 if etapa == "baus" else 1
                elif obj.rect.right < jogador.rect.left-30:
                    # Falhar a coleta não impede um tutorial obrigatório.
                    obj.rect.x = jogador.rect.right+145
                    if hasattr(obj,"_x_float"):
                        obj._x_float=float(obj.rect.x)
            if self._extra_coletados >= len(self._extra_objs):
                if self._extra_timer > 26:
                    return ganhos,self._avancar_extra(todos)
        elif etapa == "febre":
            for obj in self._extra_objs:
                if not obj.alive():
                    continue
                distancia = obj.rect.left-jogador.rect.right
                if 0 < distancia < 88 and jogador.no_chao:
                    jogador.pular(som,volume)
                obj.update(6.0)
                if obj.rect.right < jogador.rect.left - 20:
                    obj.kill()
                    self._extra_coletados += 1
            if self._extra_coletados >= 3:
                self.demo_febre = True
                if self._extra_timer > 160:
                    return 0,self._avancar_extra(todos)
        return ganhos,False

    def _texto(self,tela,texto,tamanho,cor,centro,y,largura=None):
        fonte=self.fonte_tutorial(tamanho)
        if largura:
            fonte,linhas,altura=self._encaixar_linhas(texto,largura,78,tamanho)
        else:
            linhas=[texto]
            altura=fonte.get_height()
        for linha in linhas:
            img=self._render_texto(fonte,linha,cor)
            tela.blit(img,img.get_rect(centerx=centro,top=y))
            y+=altura

    def _cartao(self,tela,titulo,mensagem,rodape,numero,aguardando=False):
        w,h=tela.get_size()
        if w<220 or h<475:return
        area=pygame.Rect(16,207,w-32,148 if aguardando else 125)
        pygame.draw.rect(tela,(10,27,46),area,border_radius=12)
        pygame.draw.rect(tela,(108,220,242),area,2,border_radius=12)
        pygame.draw.rect(tela,(246,199,105),(area.left+14,area.top+13,7,7),border_radius=2)
        self._texto(tela,titulo,21,(252,226,142),area.centerx,area.top+14,area.w-36)
        self._texto(tela,mensagem,16,(234,245,251),area.centerx,area.top+50,area.w-40)
        if rodape:
            self._texto(tela,rodape,17,(131,235,179),area.centerx,area.bottom-26,area.w-36)
        pygame.draw.rect(tela,(33,53,73),(26,370,w-52,5),border_radius=2)
        pygame.draw.rect(tela,(134,224,186),(26,370,int((w-52)*min(1,numero/10.0)),5),border_radius=2)

    def desenhar(self,tela,fonte=None):
        if not self.ativo:return
        if self._intro_restante>0:
            self._cartao(tela,"BEM-VINDO AO PIXEL RUSH",
                "Conheça a cidade. Em instantes, você aprenderá cada gesto sem perder vidas.",
                "CINCO SEGUNDOS DE INTRODUÇÃO",0)
            return
        if self._extra_indice>=0:
            _,titulo,mensagem=_ETAPAS_EXTRA[self._extra_indice]
            rodape=("TOQUE PARA CONTINUAR" if self._extra_popup else
                     "COMBO: "+str(self._extra_coletados)+" MOEDAS" if self.etapa in ("combo_moedas","descanso") else
                     "QUASE COLISÕES AUTOMÁTICAS: "+str(self._extra_coletados)+"/3" if self.etapa=="febre" else
                     "BAÚS COLETADOS: "+str(self._extra_coletados))
            self._cartao(tela,titulo,mensagem,rodape,7+self._extra_indice,self._extra_popup)
            if self.demo_febre:
                pygame.draw.rect(tela,(249,196,72),(4,4,tela.get_width()-8,tela.get_height()-8),3,border_radius=8)
            return
        super().desenhar(tela,fonte)
        if self._pausa_comando and self.etapa in _DICAS:
            nome,seta,dica=_DICAS[self.etapa]
            if self.etapa=="swipe_down":
                nome="DESLIZE PARA BAIXO" if self._swipe_etapa else "MANTENHA PRESSIONADO"
            self._texto(tela,nome,18,_CU[0],tela.get_width()//2,420,tela.get_width()-70)

    def desenhar_fx_congelado(self,tela,tempo_ms):
        """Movimento na interface, sem mover o mundo nem alocar superfícies."""
        if not (self._pausa_comando or self._extra_popup):
            return
        w=tela.get_width()
        t=(tempo_ms%1400)/1400.0
        pulso=0.5+0.5*math.sin(t*math.tau)
        cx=w//2
        cy=535
        pygame.draw.circle(tela,(240,216,135),(cx,cy),int(23+3*pulso),2)
        pygame.draw.circle(tela,(242,245,255),(cx,cy),12,2)
        pygame.draw.rect(tela,(132,205,237),(cx-5,cy-7,10,19),border_radius=4)
        if self.etapa in ("pular","pular_longo"):
            sinal=-1
        elif self.etapa=="swipe_down" and self._swipe_etapa==0:
            sinal=0
        else:
            sinal=1
        if sinal:
            dy=int(sinal*(30+10*pulso))
            alvo=cy+dy
            pygame.draw.line(tela,(251,212,128),(cx,cy+int(sinal*13)),(cx,alvo),4)
            ponta=alvo
            pygame.draw.polygon(tela,(251,212,128),
                ((cx,ponta+7*sinal),(cx-9,ponta-5*sinal),(cx+9,ponta-5*sinal)))
        else:
            pygame.draw.circle(tela,(246,213,132),(cx,cy),int(28+5*pulso),2)
        # Duas marcas discretas de lente ajudam a indicar pausa intencional.
        pygame.draw.line(tela,(80,177,205),(cx-75,cy-49),(cx-51,cy-49),2)
        pygame.draw.line(tela,(80,177,205),(cx+51,cy+49),(cx+75,cy+49),2)
