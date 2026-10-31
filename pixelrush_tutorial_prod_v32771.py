# -*- coding: utf-8 -*-
"""Exclusivo da variante PROD: HUD de seis lições sem cortes e repetição não fatal."""
import os
import sys
import pygame
from pixelrush_tutorial_corrida_v3277 import TutorialCorrida as _TutorialBase, ETAPAS
from pixelrush_fontes_prod_v32771 import fonte_unicode as _fonte_cjk
from functools import lru_cache
from pixelrush_tutorial_textos_prod_v32773 import instrucoes_plataforma, mensagem_repetir

_E_ANDROID = sys.platform == 'android' or 'ANDROID_ARGUMENT' in os.environ

def _toque_nativo_ou_emulador():
    """Emulador Android em PC: oferecer teclado/clique, não swipe obrigatório."""
    if not _E_ANDROID:
        return False
    if os.environ.get('PIXELRUSH_EMULADOR_PC', '').lower() in ('1', 'true', 'sim'):
        return False
    if os.environ.get('PIXELRUSH_CONTROLES', '').lower() in ('pc', 'teclado', 'mouse'):
        return False
    try:
        # Detectar por características de hardware só uma vez ao carregar.
        from jnius import autoclass
        build = autoclass('android.os.Build')
        sinal = ' '.join(str(getattr(build, nome, '') or '').lower()
                         for nome in ('FINGERPRINT', 'MODEL', 'PRODUCT', 'HARDWARE'))
        if any(p in sinal for p in ('generic', 'emulator', 'sdk_gphone',
                                   'goldfish', 'ranchu', 'vbox86', 'genymotion')):
            return False
    except Exception:
        pass
    return True

_USAR_GESTOS = _toque_nativo_ou_emulador()


class TutorialCorrida(_TutorialBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modo_entrada = 'toque' if _USAR_GESTOS else 'teclado'
        self.tentativas = 0
        self.aviso_erro_ate = -1
        self.passo_obstaculo = 6

    def fonte_tutorial(self, tamanho):
        if self.idioma in ('ja_JP', 'zh_CN', 'ko_KR', 'hi_IN'):
            return _fonte_cjk(self.idioma, tamanho)
        return super().fonte_tutorial(tamanho)

    def processar_evento(self, evento, converter=None, som=None, volume=1.0):
        retorno = super().processar_evento(evento, converter, som, volume)
        # O meio físico, e não o último evento de mouse sintetizado, escolhe
        # as instruções exibidas. Mouse de emulador = controle PC.
        self.modo_entrada = 'toque' if _USAR_GESTOS else 'teclado'
        return retorno

    def _preparar(self, todos, letras, palavra):
        # Ajustar unicamente a cadência do desafio de cone + hidrante. O
        # personagem continua com a mesma física e hitbox da corrida real.
        self.passo_obstaculo = (12 if self.etapa == 'pular' else
                                16 if self.etapa == 'pular_longo' else 6)
        return super()._preparar(todos, letras, palavra)

    def atualizar(self, jogador, fundo, todos, letras, palavra, particulas,
                  pool, som, volume, frame):
        etapa_anterior = self.etapa
        resposta = super().atualizar(jogador, fundo, todos, letras, palavra,
                                    particulas, pool, som, volume, frame)
        if (self.ativo and etapa_anterior == self.etapa and self.sucesso
                and self.etapa in ('pular', 'pular_longo', 'agachar', 'swipe_down')):
            # Desafio não fatal: se a pose não protegeu durante a passagem,
            # recoloca o obstáculo ~28 quadros à frente e repete a lição.
            corpo = jogador.obter_hitbox() if hasattr(jogador, 'obter_hitbox') else jogador.rect
            em_contato = any(obj.alive() and corpo.colliderect(obj.rect) for obj in self.objetos)
            defesa = ((self.etapa in ('pular', 'pular_longo') and not jogador.no_chao)
                     or (self.etapa == 'agachar' and jogador.agachado)
                     or (self.etapa == 'swipe_down' and getattr(jogador, 'descida_rapida', False)))
            if em_contato and not defesa:
                self.tentativas += 1
                self.aviso_erro_ate = self.ticks + 90
                self._preparar(todos, letras, palavra)
                # Reset tutorial apenas: a morte/gameover não é chamada.
                jogador.velocidade_y = 0.0
                jogador.rect.bottom = jogador.chao_y
                jogador.no_chao = True
                jogador.descida_rapida = False
                self.ticks_etapa = 0
        return resposta

    def _encaixar_linhas(self, texto, largura, altura_max, tamanho=17):
        """Quebra palavras e CJK sem cortar ou extrapolar a borda do card."""
        texto = str(texto or '')
        for tam in range(tamanho, 9, -1):
            f = self.fonte_tutorial(tam)
            separador = ' ' if ' ' in texto else ''
            tokens = texto.split(' ') if separador else list(texto)
            linhas, linha = [], ''
            for token in tokens:
                candidato = (linha + separador + token).strip() if linha else token
                if f.size(candidato)[0] <= largura:
                    linha = candidato
                else:
                    if linha:
                        linhas.append(linha)
                    linha = token
                    if f.size(linha)[0] > largura:
                        # Para palavras longas, quebrar por grafema simples.
                        prefixo = ''
                        for char in linha:
                            if prefixo and f.size(prefixo + char)[0] > largura:
                                linhas.append(prefixo)
                                prefixo = char
                            else:
                                prefixo += char
                        linha = prefixo
            if linha:
                linhas.append(linha)
            altura_linha = max(f.get_height(), f.get_linesize())
            if linhas and len(linhas) * altura_linha <= altura_max:
                return f, linhas, altura_linha
        # Caracteres sem cobertura na fonte são tratados pelo fallback existente.
        return self.fonte_tutorial(10), [''], 12

    def desenhar(self, tela, fonte=None):
        if not self.ativo:
            return
        w, h = tela.get_size()
        if w < 220 or h < 475:
            return
        ui = self.textos_ui
        titulo, explicacao = ui['textos'][self.etapa]
        explicacao = instrucoes_plataforma(self.idioma, self.etapa, _USAR_GESTOS, ui)

        outer = pygame.Rect(12, 219, w - 24, 133)
        pygame.draw.rect(tela, (7, 20, 36), outer, border_radius=13)
        pygame.draw.rect(tela, (118, 234, 249), outer, 3, border_radius=13)
        area = pygame.Rect(outer.x + 12, outer.y + 20, outer.width - 24, 108)
        for i in range(len(ETAPAS)):
            cor = (95, 238, 170) if i < self.etapa_indice else ((255, 224, 125) if i == self.etapa_indice else (65, 88, 110))
            pygame.draw.rect(tela, cor, (outer.x + 12 + i * (outer.width - 28) // 6,
                                         outer.y + 8, (outer.width - 34) // 6, 5), border_radius=2)
        ft, linhas_titulo, ha = self._encaixar_linhas(titulo, area.width, 28, 20)
        y = area.y
        for linha in linhas_titulo:
            surf = ft.render(linha, True, (255, 235, 145))
            tela.blit(surf, (area.x, y))
            y += ha
        fy, linhas, hl = self._encaixar_linhas(explicacao, area.width, max(40, outer.bottom - 6 - y), 17)
        y += 5
        for linha in linhas:
            tex = fy.render(linha, True, (246, 249, 255))
            tela.blit(tex, (area.x, y))
            y += hl
        # Única plataforma: teclado+cliques no PC, gestos no Android.
        modo = 'toque' if _USAR_GESTOS else 'teclado'
        dica = ui['dicas'][self.etapa][1 if _USAR_GESTOS else 0]
        if not _USAR_GESTOS and self.etapa in ('pular', 'pular_longo'):
            dica = dica + ' / ' + ('CLIQUE' if self.idioma == 'pt_BR' else 'CLICK')
        etiqueta = (ui.get('modos', {}).get('teclado', 'TECLADO') if not _USAR_GESTOS
                    else instrucoes_plataforma(self.idioma, 'etiqueta_toque', True, ui))
        controle = f'{etiqueta}: {dica}'
        barra = pygame.Rect(12, 358, w-24, 53)
        pygame.draw.rect(tela, (16, 42, 64), barra, border_radius=9)
        pygame.draw.rect(tela, (133, 209, 244), barra, 2, border_radius=9)
        f_controle, linhas, h_controle = self._encaixar_linhas(controle, barra.width-24, 45, 17)
        start_y = barra.y + (barra.height - len(linhas)*h_controle)//2
        for linha in linhas:
            texto = f_controle.render(linha, True, (255, 229, 142))
            tela.blit(texto, (barra.x + 12, start_y))
            start_y += h_controle
        # Feedback só após coleta ou sucesso e sem extrapolar o card.
        progresso = self.contagem_coletas if self.etapa in ('moedas', 'letras') else 0
        if self.sucesso or progresso or self.aviso_erro_ate > self.ticks:
            barra2 = pygame.Rect(19, 418, w-38, 40)
            pygame.draw.rect(tela, (14, 62, 49), barra2, border_radius=8)
            pygame.draw.rect(tela, (119, 244, 163), barra2, 2, border_radius=8)
            if self.sucesso:
                rotulo = ui.get('feedback', {}).get(self.etapa, 'PERFEITO!')
            elif progresso:
                rotulo = f"{ui.get('coleta','COLETA')}: {progresso}/{3 if self.etapa == 'moedas' else 5}"
            else:
                rotulo = mensagem_repetir(self.idioma)
            ff, _, _ = self._encaixar_linhas(rotulo, barra2.width-20, 33, 20)
            surf = ff.render(rotulo, True, (255, 245, 195))
            if surf.get_width() <= barra2.width-20:
                tela.blit(surf, surf.get_rect(center=barra2.center))
        if self.objetos and not self.sucesso:
            alvo = self.objetos[0].rect
            x = max(27, min(w-27, alvo.centerx))
            y = max(467, alvo.top - 29)
            pygame.draw.polygon(tela, (255, 223, 95), ((x, y + 16), (x-10, y), (x+10, y)))
