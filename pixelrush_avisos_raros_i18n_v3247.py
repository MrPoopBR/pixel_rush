# -*- coding: utf-8 -*-
"""Plano K/17: localização apenas do quadro de aviso dos sete eventos raros.
Diretor, hitboxes, RNG, estados, sprites e tempos seguem herdados sem alterações.
"""
from functools import lru_cache
from pathlib import Path
import pygame
from pixelrush_eventos_raros_v3244 import DiretorEventosRaros as DiretorOriginal, EVENTOS
from pixelrush_traducoes_v3247 import ARQUIVOS_FONTES, fonte_unicode

LOCALES=('es_ES','ja_JP','fr_FR','de_DE','it_IT','tr_TR','pt_PT','hi_IN','zh_CN','ko_KR','ru_RU')
# Frases CURTAS, orientadas ao gesto, para o painel original de 186/246px.
# Ordem: es, ja, fr, de, it, tr, pt_PT, hi, zh, ko, ru.
_FRASES={
 'cidade':('¡SISMO! ¡SALTA!','揺れ！ジャンプ','SÉISME ! SAUTE !','BEBEN! SPRING!','SCOSSA! SALTA!','DEPREM! ZIPLA!','ABALO! SALTA!','भूकंप! कूदें','地震！跳跃','지진! 점프','ТОЛЧОК! ПРЫГАЙ!'),
 'neve':('¡AVALANCHA! ¡SALTA!','雪崩！ジャンプ','AVALANCHE ! SAUTE !','LAWINE! SPRING!','VALANGA! SALTA!','ÇIĞ! ZIPLA!','AVALANCHE! SALTA!','हिमस्खलन! कूदें','雪崩！跳跃','눈사태! 점프','ЛАВИНА! ПРЫГАЙ!'),
 'deserto':('¡ARENA! ¡AGÁCHATE!','砂嵐！しゃがむ','SABLE ! BAISSE-TOI !','SAND! DUCKEN!','SABBIA! ABBASSATI!','KUM! EĞİL!','AREIA! AGACHA!','रेत! झुकें','沙暴！下蹲','모래바람! 숙이기','ПЕСОК! ПРИСЯДЬ!'),
 'floresta':('¡ÁRBOL! ¡SALTA!','倒木！ジャンプ','ARBRE ! SAUTE !','BAUM! SPRING!','ALBERO! SALTA!','AĞAÇ! ZIPLA!','ÁRVORE! SALTA!','पेड़! कूदें','倒树！跳跃','나무! 점프','ДЕРЕВО! ПРЫГАЙ!'),
 'vulcao':('¡ERUPCIÓN! ¡SALTA!','噴火！ジャンプ','ÉRUPTION ! SAUTE !','AUSBRUCH! SPRING!','ERUZIONE! SALTA!','PATLAMA! ZIPLA!','ERUPÇÃO! SALTA!','विस्फोट! कूदें','喷发！跳跃','분화! 점프','ИЗВЕРЖЕНИЕ! ПРЫГАЙ!'),
 'cidade_futurista':('¡DRONES! ¡AGÁCHATE!','ドローン！しゃがむ','DRONES ! BAISSE-TOI !','DROHNEN! DUCKEN!','DRONI! ABBASSATI!','DRONLAR! EĞİL!','DRONES! AGACHA!','ड्रोन! झुकें','无人机！下蹲','드론! 숙이기','ДРОНЫ! ПРИСЯДЬ!'),
 'ilhas_celestes':('¡CRISTALES! ¡AGÁCHATE!','結晶！しゃがむ','CRISTAUX ! BAISSE-TOI !','KRISTALLE! DUCKEN!','CRISTALLI! ABBASSATI!','KRİSTALLER! EĞİL!','CRISTAIS! AGACHA!','क्रिस्टल! झुकें','水晶！下蹲','수정! 숙이기','КРИСТАЛЛЫ! ПРИСЯДЬ!'),
}
TRADUCOES={bioma:dict(zip(LOCALES,frases)) for bioma,frases in _FRASES.items()}
_LATIN=Path(__file__).resolve().parent/'assets_i18n_v3247'/'NotoSans-Avisos-Latin-v3247.ttf'

@lru_cache(maxsize=8)
def _fonte_latin(tamanho):
    return pygame.font.Font(str(_LATIN),tamanho)

class DiretorEventosRaros(DiretorOriginal):
    """Única substituição: imagens dos avisos; a atualização é idêntica à original."""
    def __init__(self, idioma_provider=None):
        super().__init__()
        self._idioma_provider=idioma_provider
        self._idioma_aviso_atual=None

    def _aviso(self, bioma, leve):
        idioma=self._idioma_provider() if self._idioma_provider else 'pt_BR'
        if idioma!=self._idioma_aviso_atual:
            # O jogador nunca vê dois idiomas simultaneamente: liberar avisos
            # antigos para não acumular superfícies ao trocar idioma no Android.
            for chave in tuple(self._avisos):
                if len(chave)==3:
                    del self._avisos[chave]
            self._idioma_aviso_atual=idioma
        if idioma not in LOCALES or bioma not in TRADUCOES:
            return super()._aviso(bioma,leve)
        key=(bioma,bool(leve),idioma)
        pronto=self._avisos.get(key)
        if pronto is not None:
            return pronto
        largura=186 if leve else 246
        mensagem=TRADUCOES[bioma][idioma]
        cor=EVENTOS[bioma][1]
        superficie=pygame.Surface((largura,32),pygame.SRCALPHA)
        pygame.draw.rect(superficie,(15,22,35,224),(0,0,largura,32),border_radius=5)
        pygame.draw.rect(superficie,cor,(1,1,largura-2,30),2,border_radius=5)
        for tamanho in ((14,12,10) if leve else (17,14,12)):
            fonte=(fonte_unicode(idioma,tamanho) if idioma in ARQUIVOS_FONTES
                   else _fonte_latin(tamanho))
            if fonte.size(mensagem)[0] <= largura-10:
                break
        imagem=fonte.render(mensagem,True,(255,247,221))
        # Segurança visual para fontes/escala excepcionais. Nunca altera o dado original.
        if imagem.get_width() > largura-10:
            imagem=pygame.transform.smoothscale(imagem,(largura-10,imagem.get_height()))
        superficie.blit(imagem,((largura-imagem.get_width())//2,(32-imagem.get_height())//2))
        self._avisos[key]=superficie
        return superficie
