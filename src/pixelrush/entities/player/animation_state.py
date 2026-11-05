# -*- coding: utf-8 -*-
"""Funções extraídas sem reescrever algoritmos da v3.277.89-QA.
Nomes de funções permanecem importados no motor nos pontos originais.
"""

def _estado_skin_jogador(jogador, frame_contador):
    if jogador.morrendo:
        tempo_total = 70 if jogador.morte_por_buraco else 60
        return 'MORRER', min(5, max(0, tempo_total - jogador.tempo_morte) // 10)
    if jogador.descida_rapida and not jogador.no_chao:
        return 'SWIPE_DOWN', (frame_contador // 3) % 4
    if jogador.jetpack_fase is not None:
        if jogador.jetpack_fase == 'subindo':
            return 'SUBINDO', min(3, max(0, int((jogador.jetpack_subida_duracao - jogador.jetpack_transicao_timer) / 12)))
        if jogador.jetpack_fase == 'descendo':
            return 'CAINDO', min(3, max(0, int((jogador.jetpack_descida_duracao - jogador.jetpack_transicao_timer) / 12)))
        return 'PULAR', 1
    if not jogador.no_chao:
        duracao = getattr(jogador, 'anim_pulo_frames', 0)
        vy = float(getattr(jogador, 'velocidade_y', 0.0))
        if duracao <= 4 and vy < -6.0:
            return 'IMPULSO', min(2, duracao // 2)
        if vy < -2.4:
            return 'SUBINDO', min(3, max(0, int(abs(vy + 2.4) * 0.45)))
        if vy <= 2.0:
            return 'PULAR', 1
        return 'CAINDO', min(3, max(0, int((vy - 2.0) * 0.35)))
    if jogador.agachado:
        return 'AGACHAR', (frame_contador // 2) % 6
    if getattr(jogador, 'anim_pouso_ticks', 0) > 0:
        return 'POUSO', min(2, max(0, 3 - jogador.anim_pouso_ticks))
    return 'CORRER', (frame_contador // 2) % 10

def jogador_invencivel_por_velocidade(jogador, febre_timer=0, febre_metros=0.0):
    """Febre e Turbo protegem contra terreno, buracos, lasers e inimigos."""
    return bool(jogador and not jogador.morrendo and (
        febre_timer > 0 or febre_metros > 0 or
        jogador.tempo_turbo > 0 or jogador.tempo_turbo_fantasma > 0
    ))

