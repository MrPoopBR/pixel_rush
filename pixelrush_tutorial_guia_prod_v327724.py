# -*- coding: utf-8 -*-
"""PIXEL RUSH v3.277.24: tutorial PROD guiado, sem modificar fisica."""
import pygame
from pixelrush_tutorial_prod_v32771 import (
    TutorialCorrida as _Anterior, ETAPAS, _USAR_GESTOS,
    instrucoes_plataforma, mensagem_repetir,
)
_OBSTACULOS = frozenset(("pular", "pular_longo", "agachar", "swipe_down"))

class TutorialCorrida(_Anterior):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pausa_comando = False
        self._comando_liberado = False
        self._salto_automatico = False
        self._dedo_gesto = None

    def _preparar(self, todos, letras, palavra):
        resultado = super()._preparar(todos, letras, palavra)
        self._pausa_comando = False
        self._comando_liberado = False
        self._salto_automatico = False
        self._dedo_gesto = None
        return resultado

    def processar_evento(self, evento, converter=None, som=None, volume=1.0):
        """Aceitar apenas o comando mostrado e somente na pausa didatica."""
        if not self.ativo:
            return False
        if self.fase_recuperacao is not None:
            return True
        etapa, tipo = self.etapa, evento.type
        if etapa not in _OBSTACULOS:
            return True
        # SDL gera eventos de mouse sinteticos ao arrastar o dedo.
        if _USAR_GESTOS and tipo in (
                pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
            return True
        if not self._pausa_comando:
            if self._comando_liberado and etapa != "swipe_down" and tipo in (
                    pygame.KEYUP, pygame.FINGERUP, pygame.MOUSEBUTTONUP,
                    pygame.JOYBUTTONUP):
                return super().processar_evento(evento, converter, som, volume)
            return True
        if etapa == "swipe_down":
            if tipo in (pygame.FINGERDOWN, pygame.MOUSEBUTTONDOWN):
                if tipo == pygame.MOUSEBUTTONDOWN and getattr(evento, "button", 1) != 1:
                    return True
                pos = ((evento.x * self.largura, evento.y * self.altura)
                       if tipo == pygame.FINGERDOWN
                       else (converter(evento.pos) if converter else evento.pos))
                self._dedo_gesto = (tipo, float(pos[1]))
                return True
            if tipo in (pygame.FINGERUP, pygame.MOUSEBUTTONUP):
                anterior = self._dedo_gesto
                self._dedo_gesto = None
                if anterior is None or (
                        (anterior[0] == pygame.FINGERDOWN) !=
                        (tipo == pygame.FINGERUP)):
                    return True
                pos = ((evento.x * self.largura, evento.y * self.altura)
                       if tipo == pygame.FINGERUP
                       else (converter(evento.pos) if converter else evento.pos))
                if (float(pos[1]) - anterior[1] >= 55
                        and self._salto_automatico and not self.jogador.no_chao):
                    self.jogador.iniciar_descida_rapida(som, volume)
                    if self.jogador.descida_rapida:
                        self.swipe_feito = True
                        self._comando_liberado = True
                        self._pausa_comando = False
                return True
            # PC/emulador sem toque nativo conserva seta para baixo.
            if (not _USAR_GESTOS and not self.jogador.no_chao
                    and ((tipo == pygame.KEYDOWN and getattr(evento, "key", None)
                          in (pygame.K_DOWN, pygame.K_s))
                         or (tipo == pygame.JOYBUTTONDOWN
                             and getattr(evento, "button", None) in (1, 3)))):
                self.jogador.iniciar_descida_rapida(som, volume)
                if self.jogador.descida_rapida:
                    self.swipe_feito = True
                    self._comando_liberado = True
                    self._pausa_comando = False
            return True
        salto = ((tipo == pygame.KEYDOWN and getattr(evento, "key", None)
                  in (pygame.K_SPACE, pygame.K_UP, pygame.K_w))
                 or (tipo == pygame.JOYBUTTONDOWN
                     and getattr(evento, "button", None) in (0, 2))
                 or tipo == pygame.FINGERDOWN
                 or (tipo == pygame.MOUSEBUTTONDOWN
                     and getattr(evento, "button", 1) == 1))
        baixo = ((tipo == pygame.KEYDOWN and getattr(evento, "key", None)
                 in (pygame.K_DOWN, pygame.K_s))
                 or (tipo == pygame.JOYBUTTONDOWN
                     and getattr(evento, "button", None) in (1, 3))
                 or tipo == pygame.FINGERDOWN
                 or (tipo == pygame.MOUSEBUTTONDOWN
                     and getattr(evento, "button", 1) == 1))
        if (etapa in ("pular", "pular_longo") and salto) or (
                etapa == "agachar" and baixo):
            super().processar_evento(evento, converter, som, volume)
            self._comando_liberado = True
            self._pausa_comando = False
        return True

    def atualizar(self, jogador, fundo, todos, letras, palavra,
                  particulas, pool, som, volume, frame):
        if self.ativo and self.fase_recuperacao is None and self.etapa in _OBSTACULOS:
            if not self._etapa_preparada:
                self._preparar(todos, letras, palavra)
            if self._pausa_comando:
                # Sem tick de jogo, fisica, perigo, cenario nem cronometro.
                return (0, False)
            if not self._comando_liberado and self.objetos:
                distancia = min(obj.rect.left - jogador.rect.right for obj in self.objetos)
                if distancia <= 122:
                    if self.etapa == "swipe_down":
                        if not self._salto_automatico and jogador.no_chao:
                            jogador.pular(som, volume)
                            self._salto_automatico = True
                        if self._salto_automatico and not jogador.no_chao:
                            self._pausa_comando = True
                            self._dedo_gesto = None
                            return (0, False)
                    else:
                        self._pausa_comando = True
                        return (0, False)
        return super().atualizar(
            jogador, fundo, todos, letras, palavra, particulas,
            pool, som, volume, frame)

    def _passagem_validada(self):
        if not self.sucesso:
            return False
        if self.etapa in ("moedas", "letras"):
            return True
        return bool(self.objetos) and all(
            obj.rect.right < self.jogador.rect.left - 35 for obj in self.objetos)

    def desenhar(self, tela, fonte=None):
        """Um cartao de orientacao, sem mensagens de acerto prematuras."""
        if not self.ativo:
            return
        w, h = tela.get_size()
        if w < 220 or h < 475:
            return
        ui = self.textos_ui
        if self.fase_recuperacao is not None or self.aviso_erro_ate > self.ticks:
            aviso = pygame.Rect(16, 94, w - 32, 90)
            pygame.draw.rect(tela, (33, 29, 47), aviso, border_radius=12)
            pygame.draw.rect(tela, (255, 193, 102), aviso, 2, border_radius=12)
            if ((self.ticks - self._aviso_erro_inicio) // 24) % 2 == 0:
                texto = mensagem_repetir(self.idioma)
                f, linhas, altura = self._encaixar_linhas(texto, aviso.width - 24, 60, 25)
                y = aviso.y + 17
                for linha in linhas:
                    imagem = self._render_texto(f, linha, (255, 229, 153))
                    tela.blit(imagem, imagem.get_rect(centerx=aviso.centerx, top=y))
                    y += altura
            return
        titulo = ui["textos"][self.etapa][0]
        progresso = self.contagem_coletas if self.etapa in ("moedas", "letras") else 0
        if self._passagem_validada():
            instrucao = ui.get("feedback", {}).get(self.etapa, "OK")
        elif progresso:
            instrucao = f"{ui.get('coleta','COLETA')}: {progresso}/{3 if self.etapa == 'moedas' else 5}"
        elif self._pausa_comando:
            instrucao = ui["dicas"][self.etapa][1 if _USAR_GESTOS else 0]
        else:
            instrucao = instrucoes_plataforma(self.idioma, self.etapa, _USAR_GESTOS, ui)
        area = pygame.Rect(16, 222, w - 32, 100)
        pygame.draw.rect(tela, (10, 26, 43), area, border_radius=11)
        pygame.draw.rect(tela, (109, 214, 235), area, 2, border_radius=11)
        largura = (area.width - 34) // 6
        for i in range(len(ETAPAS)):
            cor = ((100, 222, 163) if i < self.etapa_indice else
                   (252, 219, 134) if i == self.etapa_indice else (58, 87, 108))
            pygame.draw.rect(tela, cor, (area.x + 14 + i * largura, area.y + 7,
                                         max(2, largura - 4), 3), border_radius=1)
        ft, linhas, ha = self._encaixar_linhas(titulo, area.width - 28, 26, 19)
        y = area.y + 16
        for linha in linhas:
            tela.blit(self._render_texto(ft, linha, (255, 229, 146)), (area.x + 13, y))
            y += ha
        f, linhas, ha = self._encaixar_linhas(instrucao, area.width - 32, 51, 17)
        y = max(y + 4, area.y + 47)
        for linha in linhas[:2]:
            tela.blit(self._render_texto(f, linha, (242, 248, 252)), (area.x + 13, y))
            y += ha
        if self._pausa_comando and self.etapa == "swipe_down":
            x = area.right - 24
            pygame.draw.line(tela, (255, 222, 127),
                             (x, area.y + 53), (x, area.y + 79), 4)
            pygame.draw.polygon(tela, (255, 222, 127), (
                (x - 9, area.y + 72), (x + 9, area.y + 72),
                (x, area.y + 84)))
