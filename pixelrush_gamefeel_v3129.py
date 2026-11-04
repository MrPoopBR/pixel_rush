"""Pixel Rush v3.102.0 - game feel cinematográfico com física intacta.

FX puramente de apresentação: câmera amortecida, batida de impacto, zoom,
vinheta e linhas direcionais. Áudio reutiliza o mixer SDL já existente.
Nenhum posicionamento usado aqui altera hitboxes ou spawn.
"""
import array
import math
import random
from collections import OrderedDict
import pygame
import os

# QA Android isolado: sem efeitos na versao LIMPA/DEV fora da branch QA.
if os.environ.get('PIXELRUSH_QA_ANDROID') == '1':
    from pixelrush_qa_r11_vinheta_v327776 import desenhar_vinheta as _qa_vinheta
else:
    _qa_vinheta = None

W, H = 450, 800


def _limitar(valor, baixo, alto):
    return max(baixo, min(alto, valor))


class GameFeel:
    def __init__(self):
        self.pos_x = self.vel_x = self.pos_y = self.vel_y = 0.0
        self.lideranca = 0.0
        self.vel_efeito = 0.0
        self.impulso_flash = 0
        self.hitstop = 0
        self.onda = 0.0
        self.tempo = 0
        self.zoom = 0.0
        self._vinheta = pygame.Surface((W, H), pygame.SRCALPHA)
        self._preparar_vinheta()
        self._buffer_zoom = pygame.Surface((W, H)).convert()
        # Buffer de escala reutilizado; cada quadro mantém a mesma imagem, sem alocação SDL repetida.
        self._cache_zoom_quadro = None
        self._cache_zoom_tamanho = None
        self._fonte_combo = pygame.font.Font(None, 20)
        # Cache pequeno para evitar rasterizacao da mesma contagem a cada frame.
        self._cache_rotulos_combo = OrderedDict()

    def _preparar_vinheta(self):
        s = self._vinheta
        s.fill((0, 0, 0, 0))
        # Vinheta periférica, sem prejudicar a faixa central de obstáculos.
        for lado in range(2):
            for faixa in range(8):
                alpha = max(0, 15 - faixa * 2)
                x = faixa * 6 if lado == 0 else W - (faixa + 1) * 6
                pygame.draw.rect(s, (11, 13, 38, alpha), (x, 0, 6, H))
        for faixa in range(5):
            alpha = max(0, 8 - faixa * 2)
            pygame.draw.rect(s, (10, 14, 35, alpha), (0, faixa * 5, W, 5))
            pygame.draw.rect(s, (10, 14, 35, alpha), (0, H - (faixa + 1) * 5, W, 5))

    def reiniciar(self):
        self.pos_x = self.vel_x = self.pos_y = self.vel_y = 0.0
        self.lideranca = self.vel_efeito = self.zoom = 0.0
        self.hitstop = self.impulso_flash = 0
        self.onda = 0.0

    def impacto(self, intensidade, direcao_x=-1.0, direcao_y=-0.2, congelar=True):
        f = _limitar(float(intensidade), 0, 18)
        self.vel_x += f * direcao_x * 0.52
        self.vel_y += f * direcao_y * 0.55
        self.impulso_flash = max(self.impulso_flash, 4 if f >= 9 else 2)
        self.onda = max(self.onda, f / 18.0)
        if congelar and f >= 10:
            self.hitstop = max(self.hitstop, 4 if f > 13 else 3)

    def tick_congelado(self):
        if self.hitstop > 0:
            self.hitstop -= 1
            return True
        return False

    def atualizar(self, velocidade, velocidade_base, turbo=False, pausado=False):
        if pausado:
            return
        self.tempo += 1
        ratio = _limitar(max(0., velocidade) / max(0.1, velocidade_base), 0, 3.4)
        meta = _limitar((ratio - 1.0) * 6.0, 0.0, 10.0)
        self.lideranca += (meta - self.lideranca) * 0.08
        self.vel_efeito += ((ratio - 1.0) - self.vel_efeito) * 0.085
        meta_zoom = 0.022 if turbo else (0.010 if ratio > 1.30 else 0.)
        self.zoom += (meta_zoom - self.zoom) * 0.10
        # Oscilador harmônico criticamente amortecido em tempo fixo 60 Hz.
        self.vel_x = (self.vel_x - self.pos_x * 0.19) * 0.77
        self.vel_y = (self.vel_y - self.pos_y * 0.19) * 0.77
        self.pos_x = _limitar(self.pos_x + self.vel_x, -12.0, 12.0)
        self.pos_y = _limitar(self.pos_y + self.vel_y, -11.0, 11.0)
        if abs(self.pos_x) < .03 and abs(self.vel_x) < .03:
            self.pos_x = self.vel_x = 0.0
        if abs(self.pos_y) < .03 and abs(self.vel_y) < .03:
            self.pos_y = self.vel_y = 0.0
        self.onda *= .82
        if self.impulso_flash:
            self.impulso_flash -= 1

    def deslocamento(self):
        return int(round(self.pos_x - self.lideranca)), int(round(self.pos_y))

    def desenhar(self, surf, jogador=None, combo=0, bioma='cidade'):
        velocidade = max(0., self.vel_efeito)
        if velocidade > .12:
            cor = (192, 231, 255) if bioma != 'vulcao' else (255, 206, 155)
            qtd = min(16, max(3, int(velocidade * 9)))
            for i in range(qtd):
                fase = (self.tempo * (8 + (i % 5) * 3) + i * 197) % (W + 110)
                x = int(W - fase + 40)
                y = (i * 83 + i*i*27) % (H - 150) + 100
                # Somente a periferia, sem esconder o personagem.
                if 110 < y < 655 and 38 < x < W - 38:
                    continue
                pygame.draw.line(surf, cor, (x, y), (x - min(48, 9 + 8 * int(velocidade)), y), 1)
            # Aberração cromática simulada apenas nas bordas: nenhum canal do HUD é deslocado.
            intensidade = min(4, int(velocidade * 2.5))
            if intensidade:
                for lado in (0, W - 4):
                    for i in range(5):
                        y = (i * 173 + self.tempo * 4) % H
                        pygame.draw.line(surf, (228, 77, 153), (lado, y), (lado + 2, y), 1)
                        pygame.draw.line(surf, (72, 222, 253), (lado + 1, y + 2), (lado + 3, y + 2), 1)
        # v3.129: pickup/impact feedback has no expanding player ring.
        if self.impulso_flash > 0:
            pygame.draw.rect(surf, (214, 232, 249), (0, 0, W, H), 1)
        if combo >= 3 and jogador is not None and self.tempo % 60 < 52:
            # Feedback compacto no mundo, sem novo painel fixo.
            x = _limitar(jogador.rect.right + 12, 24, W - 72)
            y = max(175, jogador.rect.top - 7)
            pygame.draw.circle(surf, (30, 44, 65), (int(x + 17), int(y)), 17)
            pygame.draw.circle(surf, (245, 206, 85), (int(x + 17), int(y)), 16, 2)
            chave_combo = str(min(999, combo))
            texto = self._cache_rotulos_combo.get(chave_combo)
            if texto is None:
                texto = self._fonte_combo.render(chave_combo, True, (255, 240, 172))
                self._cache_rotulos_combo[chave_combo] = texto
                if len(self._cache_rotulos_combo) > 32:
                    self._cache_rotulos_combo.popitem(last=False)
            else:
                self._cache_rotulos_combo.move_to_end(chave_combo)
            surf.blit(texto, (int(x + 17 - texto.get_width() / 2), int(y - texto.get_height() / 2)))
        if _qa_vinheta is None:
            surf.blit(self._vinheta, (0, 0))
        else:
            _qa_vinheta(surf, self._vinheta)

    def acabamento_camera(self, surf, ativo):
        if not ativo or self.zoom <= .002:
            return surf
        # Zoom OUT de no máximo 2,2% durante turbo. Não move hitboxes.
        escala = 1.0 - self.zoom
        dest_w = max(1, int(W * escala))
        dest_h = max(1, int(H * escala))
        destino = self._buffer_zoom
        destino.fill((13, 20, 40))
        tamanho = (dest_w, dest_h)
        if self._cache_zoom_tamanho != tamanho or self._cache_zoom_quadro is None:
            self._cache_zoom_quadro = pygame.Surface(tamanho).convert(surf)
            self._cache_zoom_tamanho = tamanho
        quadro = pygame.transform.scale(surf, tamanho, self._cache_zoom_quadro)
        destino.blit(quadro, ((W - dest_w) // 2, (H - dest_h) // 2))
        return destino


def criar_variantes_pitch(sound, fatores=(0.955, 0.982, 1.023, 1.047)):
    """Variações de pitch pré-calculadas com resampling de 16 bits.

    Opera com array da stdlib: sem numpy/pitch DSP em tempo real, e fallback
    para o som original quando SDL usa outra configuração.
    """
    if sound is None or not pygame.mixer.get_init():
        return (sound,)
    freq, tamanho, canais = pygame.mixer.get_init()
    if tamanho != -16 or canais not in (1, 2):
        return (sound,)
    try:
        amostras = array.array('h')
        amostras.frombytes(sound.get_raw())
        quadros = len(amostras) // canais
        if quadros < 64:
            return (sound,)
        variantes = [sound]
        for fator in fatores:
            out_count = int(quadros / fator)
            out = array.array('h')
            for n in range(out_count):
                src = min(quadros - 1, int(n * fator)) * canais
                for canal in range(canais):
                    out.append(amostras[src + canal])
            variantes.append(pygame.mixer.Sound(buffer=out.tobytes()))
        return tuple(variantes)
    except (pygame.error, ValueError, OverflowError, TypeError):
        return (sound,)


def criar_camada_ritmica(duracao=2.0):
    """Percussão sintética opcional, inicia junto da trilha em canal separado.

    Não há stems da música original: isto é uma camada reativa, não um remix
    com sincronismo de BPM comprovado da trilha preexistente.
    """
    try:
        init = pygame.mixer.get_init()
        if not init or init[1] != -16:
            return None
        freq, _bits, canais = init
        n = int(freq * duracao)
        out = array.array('h')
        for i in range(n):
            t = i / float(freq)
            pos = t % .5
            envelope = max(0., 1.0 - pos / .075) ** 4
            kick = math.sin(2 * math.pi * (95 - 50 * min(pos / .08, 1.0)) * pos) * envelope
            hat_p = t % .25
            hat_env = max(0., 1.0 - hat_p / .025) ** 3
            ruido = (((i * 1103515245 + 12345) >> 12) & 1023) / 512. - 1.
            v = int(_limitar(kick * 3900 + ruido * hat_env * 750, -32700, 32700))
            for _ in range(canais):
                out.append(v)
        return pygame.mixer.Sound(buffer=out.tobytes())
    except (pygame.error, ValueError, TypeError):
        return None
