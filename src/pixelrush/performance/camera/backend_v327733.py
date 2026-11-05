# -*- coding: utf-8 -*-
"""QA v3.277.33: backend SIMD da CAMERA com teste estrito de equivalencia.

O zoom, a interpolacao, os pixels e a classe originais sao mantidos. Somente
um backend pygame-ce mais rapido E byte-identico no frame real pode ser usado.
Sem NEON/SSE2 apropriado ou com diferenca RGB: fica no original. O ajuste e
temporario e nao altera o backend usado por HUD, sprites ou outros efeitos.
"""
import os
import statistics
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
    'chamadas': 0,
    'pico_camera_ms': 0.0,
    'pico_zoom': 0.0,
    'pico_tamanho': None,
}


def resultado():
    return dict(_RESULTADO)


def _teste_real(imagem, tamanho):
    import pygame
    original = pygame.transform.get_smoothscale_backend()
    _RESULTADO['backend_original'] = original
    _RESULTADO['backend_camera'] = original
    _RESULTADO['avaliado'] = True
    # Sob traducao ARM64/x86_64, NEON nao e necessariamente o mais rapido.
    # Um candidato so sera ativado apos paridade de pixels e benchmark.
    if os.environ.get('PIXELRUSH_QA_CAMERA_AUTOTUNE', '0') != '1':
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
        formato = 'RGBA' if imagem.get_flags() & pygame.SRCALPHA else 'RGB'
        referencia_bytes = pygame.image.tobytes(referencia, formato)
        _RESULTADO['tempo_original_ms'] = round(custo, 3)
        for candidato in ('NEON', 'SSE2', 'GENERIC'):
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
                if pygame.image.tobytes(saida, formato) != referencia_bytes:
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
                    pygame.transform.smoothscale(amostra, alt_tamanho), formato)
                pygame.transform.set_smoothscale_backend(candidato)
                obtido = pygame.image.tobytes(
                    pygame.transform.smoothscale(amostra, alt_tamanho), formato)
                if obtido != esperado:
                    _RESULTADO['resultado'] = 'diferenca_de_pixels_teste2: ' + candidato
                    continue
                # Terceira prova: cores independentes e RGBA oculto sob
                # alfa zero. Um frame simples de boot pode esconder divergencia
                # entre GENERIC e NEON/SSE2 que aparece na corrida real.
                diferente=False
                for alpha in (False,True):
                    if alpha:
                        amostra_cores=pygame.Surface((37,53),pygame.SRCALPHA,32)
                    else:
                        amostra_cores=pygame.Surface((37,53)).convert(imagem)
                    for yy in range(53):
                        for xx in range(37):
                            amostra_cores.set_at((xx,yy),
                                ((xx*23+yy*17)%256,(xx*7+yy*43)%256,
                                 (xx*59+yy*11)%256,
                                 (xx*19+yy*13)%256 if alpha else 255))
                    pygame.transform.set_smoothscale_backend(original)
                    esperado=pygame.image.tobytes(
                        pygame.transform.smoothscale(amostra_cores,(43,61)),'RGBA')
                    pygame.transform.set_smoothscale_backend(candidato)
                    obtido=pygame.image.tobytes(
                        pygame.transform.smoothscale(amostra_cores,(43,61)),'RGBA')
                    if esperado!=obtido:
                        _RESULTADO['resultado']='diferenca_rgba_estresse: '+candidato
                        diferente=True
                        break
                if diferente:
                    continue
                # Alternar 4 pares de medições para reduzir variacao de CPU.
                originais=[custo]
                alternativas=[custo_novo]
                for _ in range(4):
                    pygame.transform.set_smoothscale_backend(original)
                    t0=time.perf_counter_ns()
                    pygame.transform.smoothscale(imagem,tamanho,buffer)
                    originais.append((time.perf_counter_ns()-t0)/1e6)
                    pygame.transform.set_smoothscale_backend(candidato)
                    t1=time.perf_counter_ns()
                    pygame.transform.smoothscale(imagem,tamanho,buffer)
                    alternativas.append((time.perf_counter_ns()-t1)/1e6)
                mediana_original=statistics.median(originais[1:])
                mediana_alternativa=statistics.median(alternativas[1:])
                if (mediana_alternativa < mediana_original*.80 and
                        mediana_original-mediana_alternativa >= .10):
                    _RESULTADO['backend_camera']=candidato
                    _RESULTADO['tempo_original_ms']=round(mediana_original,3)
                    _RESULTADO['tempo_candidato_ms']=round(mediana_alternativa,3)
                    _RESULTADO['resultado']='backend_pixel_exato_mais_rapido'
                    return candidato
                _RESULTADO['resultado']='sem_ganho_relevante: '+candidato
            finally:
                pygame.transform.set_smoothscale_backend(original)
        return original
    except (pygame.error, ValueError, MemoryError, RuntimeError) as exc:
        _RESULTADO['resultado'] = 'fallback: ' + type(exc).__name__
        return original
    finally:
        pygame.transform.set_smoothscale_backend(original)


def preparar_fora_do_frame(imagem, tamanho):
    """Bancada explicita: certifica backend fora do frame."""
    return _teste_real(imagem, tamanho)


def instalar():
    global _INSTALADO, _ORIGINAL
    if _INSTALADO:
        return
    import pygame
    from pixelrush_cinema_v3172 import CameraCinematica
    _ORIGINAL = CameraCinematica.aplicar

    @wraps(_ORIGINAL)
    def aplicar_qa(self, imagem, jogador=None, velocidade=6, momento=False, ativo=True):
        # Qualquer comparacao de backend ocorre apenas antes da corrida.
        escolhido = _RESULTADO['backend_camera']
        original_backend = pygame.transform.get_smoothscale_backend()
        t0=time.perf_counter_ns()
        try:
            if escolhido is None or escolhido == original_backend:
                return _ORIGINAL(self,imagem,jogador,velocidade,momento,ativo)
            try:
                pygame.transform.set_smoothscale_backend(escolhido)
                return _ORIGINAL(self,imagem,jogador,velocidade,momento,ativo)
            finally:
                pygame.transform.set_smoothscale_backend(original_backend)
        finally:
            # Sem Surface extra nem I/O no frame.
            _RESULTADO['chamadas']+=1
            ms=(time.perf_counter_ns()-t0)/1e6
            if ms>_RESULTADO['pico_camera_ms']:
                _RESULTADO['pico_camera_ms']=round(ms,3)
                _RESULTADO['pico_zoom']=round(float(getattr(self,'zoom',0)),5)
                _RESULTADO['pico_tamanho']=tuple(imagem.get_size())

    CameraCinematica.aplicar = aplicar_qa
    _INSTALADO = True


def restaurar_para_teste():
    global _INSTALADO
    if not _INSTALADO:
        return
    from pixelrush_cinema_v3172 import CameraCinematica
    CameraCinematica.aplicar = _ORIGINAL
    _INSTALADO = False
