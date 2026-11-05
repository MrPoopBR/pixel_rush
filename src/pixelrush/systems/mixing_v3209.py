"""Plano H / v3.209 — mixagem contextual sobre o áudio existente.

Apenas ganho de canais já existentes, sem síntese, novo áudio ou mudança no
ritmo musical. O DiretorMusical continua responsável pelos stems e sua curva.
"""
import math
import time

import pygame


class MixagemContextual:
    """Ducking temporário após alertas e canal prioritário para avisos críticos.

    atualizar() deve ser chamado DEPOIS de GerenciadorSons.atualizar_musica()
    e DiretorMusical.atualizar(), pois ambos reescrevem volumes dos canais.
    """
    # prioridade por tipo; também define o ganho alvo e o tempo de proteção.
    EVENTOS = {
        'alerta_laser': (3, 0.47, 0.42),
        'contagem_laser': (2, 0.64, 0.12),
        'contagem_laser_high': (4, 0.44, 0.22),
        'disparo_laser': (5, 0.38, 0.38),
        'gameover': (6, 0.35, 0.45),
        'novo_recorde': (0, 0.78, 0.30),
        'missao': (0, 0.84, 0.18),
    }
    ATAQUE_SEG = 0.075
    SOLTURA_SEG = 0.40
    CANAL_AVISOS = 1

    def __init__(self, relogio=None):
        self._agora = relogio or time.monotonic
        self._ultima = None
        self._limite = 0.0
        self._alvo_durante = 1.0
        self.ganho = 1.0
        self._prioridade_atuando = 0
        self._canal_aviso = None
        self._preparar_canal()

    def _preparar_canal(self):
        try:
            if pygame.mixer.get_init():
                # 0 já toca a música, 1 passa a preservar os avisos críticos.
                # Não interfere no número dos canais de stems e ambientação.
                pygame.mixer.set_reserved(2)
                self._canal_aviso = pygame.mixer.Channel(self.CANAL_AVISOS)
        except pygame.error:
            self._canal_aviso = None

    def tocar_prioritario(self, nome, som):
        """Retorna True se tratou a chamada (reproduzindo ou protegendo o aviso atual).

        Sons comuns continuam com Sound.play(), como na versão anterior.
        """
        info = self.EVENTOS.get(nome)
        if not info or info[0] <= 0 or som is None:
            return False
        ch = self._canal_aviso
        if ch is None:
            return False  # fallback original sem mixer
        try:
            prio = info[0]
            if ch.get_busy() and prio < self._prioridade_atuando:
                return True  # alerta superior não é interrompido
            ch.play(som)
            self._prioridade_atuando = prio
            self.avisar(nome)
            return True
        except pygame.error:
            return False

    def avisar(self, nome):
        info = self.EVENTOS.get(nome)
        if not info:
            return
        _, minimo, duracao = info
        instante = self._agora()
        if instante >= self._limite:
            self._alvo_durante = minimo
        else:
            self._alvo_durante = min(self._alvo_durante, minimo)
        self._limite = max(self._limite, instante + duracao)

    def atualizar(self, audio, estado, dt=None):
        """Atualiza somente volumes existentes; nunca reinicia sons/stems.

        dt opcional facilita testes determinísticos; em execução normal é tempo
        de relógio monotônico (transição não depende do FPS).
        """
        agora = self._agora()
        if dt is None:
            dt = 0.0 if self._ultima is None else max(0.0, min(0.10, agora-self._ultima))
        else:
            dt = max(0.0, min(0.10, float(dt)))
        self._ultima = agora
        ativo = estado == 'JOGANDO' and agora < self._limite
        alvo = self._alvo_durante if ativo else 1.0
        tau = self.ATAQUE_SEG if alvo < self.ganho else self.SOLTURA_SEG
        frac = 1.0 - math.exp(-dt / tau) if dt > 0 else 0.0
        self.ganho = max(0.0, min(1.0, self.ganho + (alvo-self.ganho)*frac))
        if not ativo and self.ganho >= .9995:
            self.ganho = 1.0
            self._alvo_durante = 1.0
        if self.ganho >= 1.0:
            return
        # Volumes acabaram de ser definidos pelo GerenciadorSons e DiretorMusical.
        # Não toca nos canais de SFX (1-6) nem nos dois da paisagem (14/15).
        canais = [getattr(audio, 'canal_musica', None), getattr(audio, 'canal_ritmo', None)]
        canais.extend(getattr(audio, 'canais_stems', ()) or ())
        for ch in canais:
            if ch is not None:
                try:
                    ch.set_volume(max(0.0, min(1.0, ch.get_volume() * self.ganho)))
                except pygame.error:
                    pass
