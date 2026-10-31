# -*- coding: utf-8 -*-
"""Camada de apresentação localizada do tutorial v3.277, sem alterar mecânicas."""
from functools import lru_cache
import pygame
from pixelrush_tutorial_corrida_v3276 import TutorialCorrida as _TutorialAnterior, ETAPAS
from pixelrush_tutorial_i18n_v3277 import dados_tutorial
from pixelrush_traducoes_v3247 import ARQUIVOS_FONTES, fonte_unicode
from pixelrush_i18n_v3246 import normalizar_idioma

@lru_cache(maxsize=64)
def _fonte(idioma,tamanho):
    if idioma in ARQUIVOS_FONTES:
        return fonte_unicode(idioma,tamanho)
    return pygame.font.SysFont('arial',tamanho,bold=True)

class TutorialCorrida(_TutorialAnterior):
    def __init__(self,*args,idioma='pt_BR',**kwargs):
        super().__init__(*args,**kwargs)
        self.idioma=normalizar_idioma(idioma)
        self.textos_ui=dados_tutorial(self.idioma)

    def fonte_tutorial(self,tamanho):
        return _fonte(self.idioma,tamanho)

    def ajustar_fonte_tutorial(self,texto,max_largura,tamanho):
        for tam in range(tamanho,10,-1):
            fonte=self.fonte_tutorial(tam)
            if fonte.size(texto)[0]<=max_largura:
                return fonte
        return self.fonte_tutorial(11)

    def quebrar_texto_tutorial(self,texto,max_largura,tamanho,max_linhas):
        """Quebra visual inclusive CJK sem espaços, sem mexer no conteúdo do save."""
        for tam in range(tamanho,10,-1):
            fonte=self.fonte_tutorial(tam)
            linhas=[]; atual=''
            tokens=texto.split(' ') if ' ' in texto else list(texto)
            separador=' ' if ' ' in texto else ''
            for tok in tokens:
                novo=(atual+separador+tok).strip() if atual else tok
                if fonte.size(novo)[0]>max_largura and atual:
                    linhas.append(atual);atual=tok
                else:atual=novo
            if atual:linhas.append(atual)
            if len(linhas)<=max_linhas and all(fonte.size(x)[0]<=max_largura for x in linhas):
                return fonte,linhas
        # Último recurso: não invadir as outras áreas do HUD.
        f=self.fonte_tutorial(11)
        linhas=linhas[:max_linhas]
        if linhas and len(linhas)==max_linhas:
            ultima=linhas[-1]
            while ultima and f.size(ultima+'…')[0]>max_largura:
                ultima=ultima[:-1]
            linhas[-1]=ultima+'…'
        return f,linhas
