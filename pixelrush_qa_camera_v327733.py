# -*- coding: utf-8 -*-
"""QA v3.277.33: backend SIMD da CAMERA com teste estrito de equivalencia.

O zoom, a interpolacao, os pixels e a classe originais sao mantidos. Somente
um backend pygame-ce mais rapido E byte-identico no frame real pode ser usado.
Sem NEON/SSE2 apropriado ou com diferenca RGB: fica no original. O ajuste e
temporario e nao altera o backend usado por HUD, sprites ou outros efeitos.
"""
import os
import time
from functools import wraps

_INSTALADO = False
_ORIGINAL = None
_RESULTADO = {
    'avaliado': False,
    'backend_original': None,
    'backend_camera': None,
    'resultado': 'nao_avaliado',
    'tempo_original_ms': None,
    'tempo_candidato_ms': None,
}


def resultado():
    return dict(_RESULTADO)


def _teste_real(imagem, tamanho):
    import pygame
    original = pygame.transform.get_smoothscale_backend()
    _RESULTADO['backend_original'] = original
    _RESULTADO['backend_camera'] = original
    _RESULTADO['avaliado'] = True
    if original in ('NEON', 'SSE2'):
        _RESULTADO['resultado'] = 'backend_simd_ja_ativo'
        return original
    if os.environ.get('PIXELRUSH_QA_CAMERA_AUTOTUNE', '1') != '1':
        _RESULTADO['resultado'] = 'desativado_por_flag'
        return original

    # Teste feito na imagem REAL da camera; nunca troca para um resampler
    # com resultados visuais diferentes. Os backends MMX/SSE depreciados
    # nao sao candidatos.
    buffer = pygame.Surface(tamanho).convert(imagem)
    try:
        pygame.transform.set_smoothscale_backend(original)
        t0 = time.perf_counter_ns()
        referencia = pygame.transform.smoothscale(imagem, tamanho, buffer)
        custo = (time.perf_counter_ns() - t0) / 1e6
        referencia_bytes = pygame.image.tobytes(referencia, 'RGB')
        _RESULTADO['tempo_original_ms'] = round(custo, 3)
        for candidato in ('NEON', 'SSE2'):
            if candidato == original:
                continue
            try:
                pygame.transform.set_smoothscale_backend(candidato)
            except (ValueError, pygame.error):
                continue
            try:
                t1 = time.perf_counter_ns()
                saida = pygame.transform.smoothscale(imagem, tamanho, buffer)
                custo_novo = (time.perf_counter_ns() - t1) / 1e6
                if pygame.image.tobytes(saida, 'RGB') != referencia_bytes:
                    _RESULTADO['resultado'] = 'diferenca_de_pixels: ' + candidato
                    continue
                # Segunda prova com pixels independentes e zoom diferente.
                # Evita aprovar um backend que coincida por acaso no frame
                # real, mas produza arredondamento distinto em outras cenas.
                amostra = pygame.Surface((41, 67)).convert(imagem)
                for y in range(67):
                    pygame.draw.line(amostra,
                        ((y * 11) % 256, (y * 7) % 256, (y * 23) % 256),
                        (0, y), (40, y))
                alt_tamanho = (45, 73)
                pygame.transform.set_smoothscale_backend(original)
                esperado = pygame.image.tobytes(
                    pygame.transform.smoothscale(amostra, alt_tamanho), 'RGB')
                pygame.transform.set_smoothscale_backend(candidato)
                obtido = pygame.image.tobytes(
                    pygame.transform.smoothscale(amostra, alt_tamanho), 'RGB')
                if obtido != esperado:
                    _RESULTADO['resultado'] = 'diferenca_de_pixels_teste2: ' + candidato
                    continue
                # Evitar trocar backend por variacao estatistica pequena.
                if custo_novo < custo * 0.80:
                    _RESULTADO['backend_camera'] = candidato
                    _RESULTADO['tempo_candidato_ms'] = round(custo_novo, 3)
                    _RESULTADO['resultado'] = 'simd_equivalente_mais_rapido'
                    return candidato
                _RESULTADO['resultado'] = 'sem_ganho_relevante: ' + candidato
            finally:
                pygame.transform.set_smoothscale_backend(original)
        return original
    except (pygame.error, ValueError, MemoryError, RuntimeError) as exc:
        _RESULTADO['resultado'] = 'fallback: ' + type(exc).__name__
        return original
    finally:
        pygame.transform.set_smoothscale_backend(original)


def instalar():
    global _INSTALADO, _ORIGINAL
    if _INSTALADO:
        return
    import pygame
    from pixelrush_cinema_v3172 import CameraCinematica
    _ORIGINAL = CameraCinematica.aplicar

    @wraps(_ORIGINAL)
    def aplicar_qa(self, imagem, jogador=None, velocidade=6, momento=False, ativo=True):
        if not _RESULTADO['avaliado'] and ativo and jogador is not None:
            # Avaliar somente apos zoom tornar-se efetivamente visivel.
            # O primeiro frame normal nao e retido nem renderizado duas vezes.
            if self.zoom >= .002:
                w,h = imagem.get_size()
                ex=max(1,int(w*self.zoom))
                ey=max(1,int(h*self.zoom))
                _teste_real(imagem,(w+2*ex,h+2*ey))
        escolhido = _RESULTADO['backend_camera']
        original_backend = pygame.transform.get_smoothscale_backend()
        if escolhido is None or escolhido == original_backend:
            return _ORIGINAL(self,imagem,jogador,velocidade,momento,ativo)
        try:
            pygame.transform.set_smoothscale_backend(escolhido)
            return _ORIGINAL(self,imagem,jogador,velocidade,momento,ativo)
        finally:
            pygame.transform.set_smoothscale_backend(original_backend)

    CameraCinematica.aplicar = aplicar_qa
    _INSTALADO = True


def restaurar_para_teste():
    global _INSTALADO
    if not _INSTALADO:
        return
    from pixelrush_cinema_v3172 import CameraCinematica
    CameraCinematica.aplicar = _ORIGINAL
    _INSTALADO = False
