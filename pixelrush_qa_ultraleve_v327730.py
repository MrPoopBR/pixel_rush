# -*- coding: utf-8 -*-
"""PIXEL RUSH QA 3.277.30 — cache temporal Android, estritamente visual.

A v3.277.29 renderizava o mundo inteiro em alternancia de dois quadros,
apenas na corrida leve e nunca no tutorial/menus. No Android medido, o passe
2.5D custava ~84 ms por execucao; ele dominava todos os estados.

Este modulo reaproveita a COMPOSICAO DE FUNDO durante 4 quadros intermediarios,
refazendo-a no quinto. HUD, sprites, controles, colisoes, fisica 60 Hz, saves,
audio, recompensas, efeitos na frente do personagem e replay nao sao cacheados.
Os pixels dos quadros efetivamente redesenhados sao os do renderizador original.
Ha um compromisso temporal deliberado: o parallax do fundo e mostrado em menos
quadros, em vez de reduzir resolucao, remover detalhes ou alterar shaders.

A implementacao so e ligada na branch APK QA; nenhum modulo PROD e editado.
"""
from pixelrush_fundo_mobile_v327726 import CacheFundoMobile


class CacheFundoUltraQA(CacheFundoMobile):
    """Uma surface RGB 450x800 reaproveitada sem nova alocacao por frame."""

    def __init__(self, periodo=5):
        super().__init__()
        self.periodo = max(1, min(8, int(periodo)))
        self.pedidos = 0
        self.passes_evitados = 0

    def reusar(self, superficie, chave, habilitado):
        self.pedidos += 1
        if not habilitado:
            self.invalidar()
            return False
        if (self._quadro is None or self._chave != chave or
                self._quadro.get_size() != superficie.get_size() or
                self._idade >= self.periodo - 1):
            return False
        superficie.blit(self._quadro, (0, 0))
        self._idade += 1
        self.acertos += 1
        self.passes_evitados += 1
        return True


class FundoMenusUltraQA:
    """Cache somente do background de menus; UI animada sempre e redesenhada."""

    def __init__(self, periodo=5):
        self.cache = CacheFundoUltraQA(periodo=periodo)

    def desenhar(self, superficie, parallax, ceu, estado):
        # QA v3.277.32: medir fundo de menus separadamente do restante da UI.
        from pixelrush_profiler_v3204 import sub_inicio, sub_fim
        sub_inicio('menus_fundo')
        try:
            chave = (
                str(estado), parallax.cenario, parallax.world.biome,
                tuple(ceu), parallax.clima_tipo,
                bool(parallax.world.lightweight), superficie.get_size()
            )
            if not self.cache.reusar(superficie, chave, True):
                parallax.draw(superficie, ceu, False)
                self.cache.guardar(superficie, chave, True)
        finally:
            sub_fim()


def modo_qa_ultraleve(rodando_android):
    return bool(rodando_android)
