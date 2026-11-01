"""Tutorial v3.276: obstáculos EXCLUSIVOS da Cidade e feedback por lição.

Herda integralmente física, comando, progressão e salvamento do tutorial v3.275.
Substitui apenas a criação de obstáculos didáticos e o HUD de sucesso.
"""
from __future__ import annotations
import pygame
from pixelrush_tutorial_corrida_v3275 import TutorialCorrida as _Anterior, ETAPAS, DICAS
from pixelrush_inimigos_v3221 import AmeacaBioma
from pixelrush_hidrante_cidade_v3276 import HidranteCidade
from pixelrush_tutorial_corrida_v3274 import TEXTOS as _TEXTOS_TUTORIAL
# Na Cidade o perigo aéreo real é um pombo, não o drone do protótipo anterior.
_TEXTOS_TUTORIAL['agachar'] = ('03 / 06   AGACHAR', 'Segure BAIXO / S ou o botão de agachar para passar sob o pombo.')

ROTAS_CIDADE = {
    'pular': ('C3',),               # Cone urbano existente
    'pular_longo': ('C3', 'HIDRANTE'),  # Cone + novo hidrante da Cidade
    'agachar': ('C2',),            # Pombo original
    'swipe_down': ('C2',),         # Pombo original como referência didática
}
FEEDBACK = {
    'pular': 'PULO CERTO!',
    'pular_longo': 'PULO LONGO CERTO!',
    'agachar': 'AGACHOU CORRETAMENTE!',
    'swipe_down': 'DESCIDA RAPIDA FEITA!',
    'moedas': '3 MOEDAS! USE NA LOJA',
    'letras': 'PALAVRA COMPLETA! BONUS DE MOEDAS',
}

class TutorialCorrida(_Anterior):
    def __init__(self,*args,classe_cidade=None,classe_hidrante=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.classe_cidade = classe_cidade or AmeacaBioma
        self.classe_hidrante = classe_hidrante or HidranteCidade

    def _preparar(self,todos,letras,palavra):
        etapa=self.etapa
        if etapa not in ROTAS_CIDADE:
            return super()._preparar(todos,letras,palavra)
        # A preparação replica somente os campos didáticos do ancestral;
        # nenhuma velocidade/controle/física se altera.
        self._etapa_preparada=True
        self.ticks_etapa=0
        self.sucesso=False
        self.tempo_confirmacao=0
        self.hold_pulo=self.hold_baixo=0
        self.segurar_pulo=self.segurar_baixo=False
        self.swipe_iniciado=None
        self.swipe_feito=False
        for antigo in self.objetos:
            antigo.kill()
        self.objetos=[]
        self.proximo_objeto=None
        x=self.jogador.rect.right+165
        for idx,codigo in enumerate(ROTAS_CIDADE[etapa]):
            pos=x+idx*75
            if codigo=='HIDRANTE':
                obj=self._somente_objeto_original(lambda pos=pos:self.classe_hidrante(pos))
            else:
                obj=self._somente_objeto_original(lambda pos=pos,codigo=codigo:self.classe_cidade(pos,codigo))
            if etapa in ('agachar','swipe_down'):
                obj.rect.y=self.jogador.chao_y-118
                if hasattr(obj,'_base_y'):obj._base_y=obj.rect.y
            todos.add(obj)
            self.objetos.append(obj)

    def desenhar(self,tela,fonte=None):
        super().desenhar(tela,fonte)
        if not self.ativo:return
        w=tela.get_width()
        if w<160:return
        # Feedback inequívoco, sem bloquear os comandos nem cobrir obstáculos.
        pronto=self.sucesso
        progresso=self.contagem_coletas if self.etapa in ('moedas','letras') else 0
        limite=3 if self.etapa=='moedas' else 5
        if not pronto and progresso==0:return
        ui=getattr(self,'textos_ui',{})
        texto=ui.get('feedback',FEEDBACK)[self.etapa] if pronto else f"{ui.get('coleta','COLETA')}: {progresso}/{limite}"
        rect=pygame.Rect(16,419,min(w-32,417),36)
        placa=pygame.Surface(rect.size,pygame.SRCALPHA)
        pygame.draw.rect(placa,(15,55,46,218) if pronto else (17,41,62,215),placa.get_rect(),border_radius=7)
        pygame.draw.rect(placa,(138,239,169) if pronto else (244,218,126),placa.get_rect(),2,border_radius=7)
        local=getattr(self,'fonte_tutorial',None)
        if local:
            f=self.ajustar_fonte_tutorial(texto,rect.width-22,22)
        else:
            f=pygame.font.Font(None,24)
            while f.size(texto)[0]>rect.width-22 and f.get_height()>13:
                f=pygame.font.Font(None,max(13,f.get_height()-2))
        placa.blit(f.render(texto,True,(248,244,201)),(12,8))
        tela.blit(placa,rect.topleft)
