# -*- coding: utf-8 -*-
"""QA 3.277.40: compositor incremental *experimental*, NAO conectado ao jogo.

Reconstrucao pixel exata do mosaico estatico a partir da Surface original.
So e valido para texturas imutaveis (sem draw/set_alpha durante o uso).
O desempenho deve ser medido incluindo o blit final; nao ativar sem prova
Android de ganho no caminho completo e equivalencia RGBA/colorkey.
"""
import pygame


class FaixaPersistenteQA:
    """Um unico buffer 450xH reutilizado, sem tocar na cena ou no framebuffer."""

    def __init__(self, largura=450):
        self.largura = int(largura)
        if self.largura <= 0:
            raise ValueError('largura invalida')
        self._fonte = None
        self._quadro = None
        self._offset = None
        self._formato = None
        self.faixas_reconstruidas = 0
        self.pixels_reconstruidos = 0

    def invalidar(self):
        self._fonte = None
        self._quadro = None
        self._offset = None
        self._formato = None

    def _pintar(self, fonte, offset, x, largura):
        """Mesma ordem de blits com areas de origem sem sobreposicao."""
        destino = self._quadro
        periodo = fonte.get_width()
        area_inicio = (offset + x) % periodo
        pos = 0
        while pos < largura:
            tamanho = min(largura - pos, periodo - area_inicio)
            destino.blit(fonte, (x + pos, 0),
                         (area_inicio, 0, tamanho, fonte.get_height()))
            pos += tamanho
            area_inicio = 0
        self.faixas_reconstruidas += 1
        self.pixels_reconstruidos += largura * fonte.get_height()

    def gerar(self, fonte, scroll):
        if not isinstance(fonte, pygame.Surface):
            raise TypeError('fonte deve ser Surface')
        periodo, altura = fonte.get_size()
        if periodo <= 0 or altura <= 0:
            raise ValueError('textura invalida')
        # Colorkey e alfa constantes. Pixels da Surface-fonte devem ser
        # imutaveis pelo chamador; se mudar, invalidar() explicitamente.
        assinatura = (fonte.get_size(), fonte.get_flags(),
                      fonte.get_alpha(), fonte.get_colorkey())
        if fonte is not self._fonte or assinatura != self._formato:
            self._fonte = fonte
            self._quadro = pygame.Surface((self.largura, altura), pygame.SRCALPHA)
            self._offset = None
            self._formato = assinatura
        novo = int(scroll) % periodo
        previo = self._offset
        if previo is None:
            movimento = self.largura
        else:
            movimento = (previo - novo) % periodo
            if movimento > periodo // 2:
                movimento -= periodo
        quadro = self._quadro
        if previo is None or abs(movimento) >= self.largura:
            quadro.fill((0, 0, 0, 0))
            self._pintar(fonte, novo, 0, self.largura)
        elif movimento:
            quadro.scroll(dx=movimento)
            if movimento < 0:
                rect = pygame.Rect(self.largura + movimento, 0,
                                   -movimento, altura)
            else:
                rect = pygame.Rect(0, 0, movimento, altura)
            quadro.fill((0, 0, 0, 0), rect)
            self._pintar(fonte, novo, rect.x, rect.w)
        self._offset = novo
        return quadro


def mosaico_referencia(fonte, scroll, largura=450):
    """Referencia exclusiva de teste; nenhuma aproximacao/resampling."""
    periodo, altura = fonte.get_size()
    quadro = pygame.Surface((largura, altura), pygame.SRCALPHA)
    offset = int(scroll) % periodo
    x = 0
    while x < largura:
        tamanho = min(largura - x, periodo - offset)
        quadro.blit(fonte, (x, 0), (offset, 0, tamanho, altura))
        x += tamanho
        offset = 0
    return quadro


def gate_integracao(diagnostico, android_real=False):
    """Sem ganho do frame COMPLETO, qualidade intacta e test Android: OFF."""
    return bool(
        android_real and diagnostico.get('pixel_exato_rgba')
        and diagnostico.get('pixel_exato_rgb')
        and diagnostico.get('ganho_estavel_frame_completo_android')
        and diagnostico.get('rss_no_limite')
        and diagnostico.get('sem_alteracoes_de_jogabilidade')
    )
