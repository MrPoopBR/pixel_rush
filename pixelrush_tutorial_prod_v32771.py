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
        self._cache_linhas = {}
        self._cache_textos = {}
        # Efeito exclusivo das quatro licoes de obstaculos; nunca causa GAMEOVER.
        self.fase_recuperacao = None
        self.tempo_recuperacao = 0
        self._rect_seguro_jogador = None
        self._inicio_reverso_jogador = None
        self._inicio_reverso_obstaculos = ()
        self._alvos_reverso_obstaculos = ()
        self._reverso_desloc_anterior = 0.0
        self._reverso_teve_colisao = False

    def fonte_tutorial(self, tamanho):
        if self.idioma in ('ja_JP', 'zh_CN', 'ko_KR', 'hi_IN'):
            return _fonte_cjk(self.idioma, tamanho)
        return super().fonte_tutorial(tamanho)

    def processar_evento(self, evento, converter=None, som=None, volume=1.0):
        # Durante a animacao de morte/reverso os comandos nao movem o jogador.
        if self.fase_recuperacao is not None:
            return True
        # O SDL pode sintetizar mouse durante um toque nativo. Nao permitir
        # que esse evento apague a origem antes da liberacao do dedo.
        if (_USAR_GESTOS and self.toque_ativo and evento.type in
                (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP)):
            return True
        # FINGERUP pode ser o unico evento recebido apos FINGERDOWN, sem
        # FINGERMOTION intermediario: validar tambem o deslocamento final.
        if (evento.type == pygame.FINGERUP and self.etapa == 'swipe_down'
                and self.toque_ativo and self.swipe_iniciado is not None
                and not self.jogador.no_chao
                and evento.y * self.altura - self.swipe_iniciado[1] >= 45):
            self.jogador.iniciar_descida_rapida(som, volume)
            self.swipe_feito = bool(self.jogador.descida_rapida)
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
        retorno = super()._preparar(todos, letras, palavra)
        if self.etapa == 'agachar':
            # O ancestral eleva o C2 para a lição de swipe-down. Em agachar,
            # manter a altura real do pombo da Cidade (chao 730, bottom 691).
            # Assim, em pe colide e agachado passa; fisica normal intocada.
            for obj in self.objetos:
                if getattr(obj, 'codigo', None) == 'C2':
                    obj.rect.bottom = self.jogador.chao_y - 39
                    if hasattr(obj, '_base_y'):
                        obj._base_y = obj.rect.y
        return retorno

    def _iniciar_reverso(self):
        """Inicia camera ao contrario sem gravar video/quadros em RAM."""
        self.fase_recuperacao = 'reverso'
        self.tempo_recuperacao = 24
        self._inicio_reverso_jogador = self.jogador.rect.copy()
        self._inicio_reverso_obstaculos = tuple(obj.rect.x for obj in self.objetos)
        self._alvos_reverso_obstaculos = tuple(
            self._rect_seguro_jogador.right + 230 + i * 75
            for i in range(len(self.objetos)))
        self._reverso_desloc_anterior = 0.0

    def _iniciar_recuperacao(self, contato):
        """Colisao: morte visual, depois reverso; falha sem contato: so reverso."""
        self._reverso_teve_colisao = bool(contato)
        self._rect_seguro_jogador = self.jogador.rect.copy()
        self.segurar_pulo = False
        self.segurar_baixo = False
        self.toque_ativo = False
        self.swipe_iniciado = None
        if contato:
            # Chama a animacao ORIGINAL do proprio Jogador, sem atingir
            # o fluxo de morte/Game Over do jogo fora do tutorial.
            self.jogador.iniciar_morte()
            self.fase_recuperacao = 'morte'
            self.tempo_recuperacao = 24
        else:
            self._iniciar_reverso()

    @staticmethod
    def _reposicionar_objeto_reverso(obj, x):
        obj.rect.x = int(x)
        if hasattr(obj, '_x'):
            obj._x = float(obj.rect.x)
        if hasattr(obj, '_posicao_mundo_x'):
            obj._posicao_mundo_x = float(obj.rect.x)
        if hasattr(obj, 'renderizar_visual'):
            obj.renderizar_visual()

    def _atualizar_recuperacao(self, fundo, todos, letras, palavra,
                              particulas, pool, som, volume, frame):
        # Nenhum passo do tutorial/colisao/spawn avanca durante estes estados.
        self.ticks += 1
        if self.fase_recuperacao == 'morte':
            self.jogador.update(0.0, frame, False, False, particulas, pool,
                                som, volume, pode_pousar=True)
            self.tempo_recuperacao -= 1
            if self.tempo_recuperacao <= 0:
                self._iniciar_reverso()
            return (0, False)
        if self.fase_recuperacao == 'reverso':
            restante = self.tempo_recuperacao
            t = (25 - restante) / 24.0
            t = max(0.0, min(1.0, t))
            ease = t * t * (3.0 - 2.0 * t)
            # O mundo e os obstaculos voltam para a DIREITA, simulando uma
            # camera reversa. So a camada didatica utiliza estes deslocamentos.
            for i, obj in enumerate(self.objetos):
                if not obj.alive():
                    todos.add(obj)
                x0 = self._inicio_reverso_obstaculos[i]
                x1 = self._alvos_reverso_obstaculos[i]
                self._reposicionar_objeto_reverso(
                    obj, round(x0 + (x1 - x0) * ease))
            passo = 255.0 * ease - self._reverso_desloc_anterior
            self._reverso_desloc_anterior += passo
            # Recuar o chao, edificios e montanhas existentes, sem afetar
            # a simulacao/velocidade da corrida normal nem alocar frames.
            if hasattr(fundo, 'desloc_chao'):
                fundo.desloc_chao = (fundo.desloc_chao - passo) % 900.0
            if hasattr(fundo, 'camada_perto'):
                fundo.camada_perto += passo * 0.24
            if hasattr(fundo, 'camada_longe'):
                fundo.camada_longe += passo * 0.08
            if hasattr(fundo, '_desloc_arte'):
                fundo._desloc_arte = (fundo._desloc_arte - passo * 0.19) % 2700.0
            if hasattr(fundo, '_desloc_arte_fundo'):
                fundo._desloc_arte_fundo = (fundo._desloc_arte_fundo - passo * 0.06) % 2700.0
            if self._reverso_teve_colisao:
                # A propria animacao de morte volta em sentido contrario antes
                # da restauracao: evita teletransporte visual repentino.
                origem = self._inicio_reverso_jogador
                destino = self._rect_seguro_jogador
                self.jogador.rect.x = round(origem.x + (destino.x - origem.x) * ease)
                self.jogador.rect.y = round(origem.y + (destino.y - origem.y) * ease)
                if hasattr(self.jogador, 'angulo_rotacao'):
                    self.jogador.angulo_rotacao = round(
                        self.jogador.angulo_rotacao * (1.0 - ease))
                self.jogador._visual_dirty = True
            self.tempo_recuperacao -= 1
            if self.tempo_recuperacao <= 0:
                self._rebobinar_desafio(todos, letras, palavra)
            return (0, False)
        return (0, False)

    def _rebobinar_desafio(self, todos, letras, palavra):
        """Finalize o reverso com desafio a distancia segura e vidas infinitas."""
        self.tentativas += 1
        jogador = self.jogador
        if self._rect_seguro_jogador is not None:
            jogador.rect = self._rect_seguro_jogador.copy()
        jogador.rect.bottom = jogador.chao_y
        jogador.velocidade_y = 0.0
        jogador.no_chao = True
        jogador.agachado = False
        jogador.descida_rapida = False
        jogador.morrendo = False
        jogador.tempo_morte = 0
        jogador.coyote_ticks = 0
        jogador.buffer_pulo_ticks = 0
        if hasattr(jogador, 'angulo_rotacao'):
            jogador.angulo_rotacao = 0
        if hasattr(jogador, '_visual_dirty'):
            jogador._visual_dirty = True
        self.toque_ativo = False
        self._preparar(todos, letras, palavra)
        for i, obj in enumerate(self.objetos):
            # 230 px livres em vez de 165: tempo real para ler o aviso e agir.
            self._reposicionar_objeto_reverso(obj, jogador.rect.right + 230 + i * 75)
        self.fase_recuperacao = None
        self._reverso_teve_colisao = False
        self.ticks_etapa = 0
        self.aviso_erro_ate = self.ticks + 130

    @staticmethod
    def _atingiu_corpo(corpo, obstaculo):
        partes = getattr(obstaculo, '_hitboxes_precisas_v342', None)
        if partes:
            return any(corpo.colliderect(parte.move(obstaculo.rect.topleft))
                       for parte in partes)
        return corpo.colliderect(obstaculo.rect)

    def atualizar(self, jogador, fundo, todos, letras, palavra, particulas,
                  pool, som, volume, frame):
        if self.fase_recuperacao is not None:
            return self._atualizar_recuperacao(
                fundo, todos, letras, palavra, particulas, pool, som, volume, frame)
        etapa_anterior = self.etapa
        desafio = etapa_anterior in ('pular', 'pular_longo', 'agachar', 'swipe_down')
        if desafio:
            if not self._etapa_preparada:
                self._preparar(todos, letras, palavra)
            # Usar update() de cada perigo da Cidade em TODO tick, como na
            # corrida normal: cone, hidrante e pombo nao aguardam um comando.
            for obj in tuple(self.objetos):
                if obj.alive():
                    obj.update(6.0)
            # O ancestral so desloca apos sucesso. Neutralizar seu segundo
            # deslocamento para manter velocidade unica de 6 px/tick.
            deslocamento_original = self.passo_obstaculo
            self.passo_obstaculo = 0
            try:
                resposta = super().atualizar(
                    jogador, fundo, todos, letras, palavra,
                    particulas, pool, som, volume, frame)
            finally:
                self.passo_obstaculo = deslocamento_original
        else:
            resposta = super().atualizar(
                jogador, fundo, todos, letras, palavra,
                particulas, pool, som, volume, frame)

        if self.ativo and self.etapa == etapa_anterior and desafio:
            corpo = jogador.obter_hitbox() if hasattr(jogador, 'obter_hitbox') else jogador.rect
            contato = any(self._atingiu_corpo(corpo, obj) for obj in self.objetos
                          if obj.alive())
            deixou_passar = (not self.sucesso and self.objetos
                             and all(obj.rect.right < jogador.rect.left - 35
                                     for obj in self.objetos))
            if contato or deixou_passar or getattr(jogador, 'morrendo', False):
                self._iniciar_recuperacao(contato or getattr(jogador, 'morrendo', False))
        return resposta

    def _render_texto(self, fonte, texto, cor):
        chave = (id(fonte), str(texto), tuple(cor))
        imagem = self._cache_textos.get(chave)
        if imagem is None:
            imagem = fonte.render(texto, True, cor)
            if len(self._cache_textos) >= 96:
                self._cache_textos.clear()
            self._cache_textos[chave] = imagem
        return imagem

    def _encaixar_linhas(self, texto, largura, altura_max, tamanho=17):
        chave = (str(texto), int(largura), int(altura_max), int(tamanho))
        resultado = self._cache_linhas.get(chave)
        if resultado is None:
            resultado = self._calcular_linhas(texto, largura, altura_max, tamanho)
            if len(self._cache_linhas) >= 96:
                self._cache_linhas.clear()
            self._cache_linhas[chave] = resultado
        return resultado

    def _calcular_linhas(self, texto, largura, altura_max, tamanho=17):
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
            surf = self._render_texto(ft, linha, (255, 235, 145))
            tela.blit(surf, (area.x, y))
            y += ha
        fy, linhas, hl = self._encaixar_linhas(explicacao, area.width, max(40, outer.bottom - 6 - y), 17)
        y += 5
        for linha in linhas:
            tex = self._render_texto(fy, linha, (246, 249, 255))
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
            texto = self._render_texto(f_controle, linha, (255, 229, 142))
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
            surf = self._render_texto(ff, rotulo, (255, 245, 195))
            if surf.get_width() <= barra2.width-20:
                tela.blit(surf, surf.get_rect(center=barra2.center))
        # Aviso grande, localizado e piscando (1,25 Hz), sem flashes em tela
        # cheia. Usa o comando real da licao nos treze idiomas existentes.
        if (self.fase_recuperacao is not None
                or self.aviso_erro_ate > self.ticks):
            aviso = pygame.Rect(12, 94, w - 24, 119)
            pygame.draw.rect(tela, (34, 28, 45), aviso, border_radius=13)
            pygame.draw.rect(tela, (255, 198, 98), aviso, 3, border_radius=13)
            if (self.ticks // 24) % 2 == 0:
                mensagem = mensagem_repetir(self.idioma)
                instrucao = ui['dicas'][self.etapa][1 if _USAR_GESTOS else 0]
                fm, lm, hm = self._encaixar_linhas(mensagem, aviso.width - 28, 42, 29)
                fi, li, hi = self._encaixar_linhas(instrucao, aviso.width - 28, 58, 25)
                y_alerta = aviso.y + 10
                for linha in lm:
                    img = self._render_texto(fm, linha, (255, 223, 108))
                    tela.blit(img, img.get_rect(centerx=aviso.centerx, top=y_alerta))
                    y_alerta += hm
                y_alerta += 4
                for linha in li:
                    img = self._render_texto(fi, linha, (255, 255, 255))
                    tela.blit(img, img.get_rect(centerx=aviso.centerx, top=y_alerta))
                    y_alerta += hi
            if self.fase_recuperacao == 'reverso':
                # Trilhas direcionais, desenhadas sem criar superficies extra.
                for i in range(4):
                    yy = 186 + i * 5
                    pygame.draw.line(tela, (255, 194, 100),
                                     (w - 30 - i * 15, yy),
                                     (w - 53 - i * 15, yy), 3)
        if self.objetos and not self.sucesso:
            alvo = self.objetos[0].rect
            x = max(27, min(w-27, alvo.centerx))
            y = max(467, alvo.top - 29)
            pygame.draw.polygon(tela, (255, 223, 95), ((x, y + 16), (x-10, y), (x+10, y)))
