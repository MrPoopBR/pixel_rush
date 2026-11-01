"""Pixel Rush v3.174.0 — efeitos autorais, replay, áudio e direção de arte.

Módulo independente e testável: não modifica hitboxes, física, spawns nem saves.
Compatível com Python 3.9 e Pygame(-ce). Sem Pillow/IA/dependências novas.
"""
from collections import deque, OrderedDict
from array import array
import math
import random
import pygame

BIOMES = ('cidade', 'neve', 'deserto', 'vulcao', 'floresta',
          'cidade_futurista', 'ilhas_celestes')
class ReplayCinematografico:
    """Replay VISUAL dos últimos 6 s. Não reexecuta colisão/simulação.

    12 amostras/s a 225x400 = até 72 superfícies (~26 MB RGBA).
    Após a morte as amostras congelam. Uma tela própria mostra a sequência,
    com desaceleração nos quadros finais. Sem gravar dados pessoais no disco.
    """
    DURACAO_SEG = 6
    INTERVALO_TICKS = 5
    MAX_AMOSTRAS = 72
    TAMANHO = (225, 400)

    def __init__(self):
        self.buffer = deque(maxlen=self.MAX_AMOSTRAS)
        self.ativo = False
        self.congelado = False
        self.indice = 0
        self.ticks_exibicao = 0
        self.ultima_amostra = -999
        self._fonte = None

    def limpar(self):
        self.buffer.clear()
        self.ativo = False
        self.congelado = False
        self.indice = 0
        self.ticks_exibicao = 0
        self.ultima_amostra = -999

    def capturar(self, superficie, tick):
        if self.congelado or tick - self.ultima_amostra < self.INTERVALO_TICKS:
            return
        self.ultima_amostra = int(tick)
        # Não inclui canvas do Game Over. Captura a cena virtual já composta.
        self.buffer.append(pygame.transform.scale(superficie, self.TAMANHO))

    def iniciar(self):
        if not self.buffer:
            self.ativo = False
            self.congelado = True
            return False
        self.congelado = True
        self.ativo = True
        self.indice = 0
        self.ticks_exibicao = 0
        return True

    def pular(self):
        self.ativo = False

    def desenhar(self, destino):
        if not self.ativo or not self.buffer:
            return False
        idx = min(self.indice, len(self.buffer) - 1)
        atual = self.buffer[idx]
        # Escala nearest-neighbour conserva os pixels da arte original.
        pygame.transform.scale(atual, destino.get_size(), destino)
        w, h = destino.get_size()
        escurecer = pygame.Surface((w, 85), pygame.SRCALPHA)
        escurecer.fill((9, 13, 29, 178))
        destino.blit(escurecer, (0, 0))
        destino.blit(escurecer, (0, h - 85))
        if self._fonte is None:
            self._fonte = pygame.font.Font(None, 30)
        label = self._fonte.render('REPLAY CINEMATOGRAFICO', True, (249, 218, 156))
        destino.blit(label, label.get_rect(center=(w // 2, 34)))
        msg = self._fonte.render('TOQUE PARA VER RESULTADOS', True, (235, 243, 255))
        destino.blit(msg, msg.get_rect(center=(w // 2, h - 45)))
        progresso = int((w - 64) * (idx + 1) / len(self.buffer))
        pygame.draw.rect(destino, (75, 90, 118), (32, h - 19, w - 64, 4))
        pygame.draw.rect(destino, (255, 191, 119), (32, h - 19, progresso, 4))
        # Slow motion nas últimas amostras — não mexe no passo fixo do jogo.
        self.ticks_exibicao += 1
        intervalo = 4 if idx >= len(self.buffer) * .72 else 2
        if self.ticks_exibicao % intervalo == 0:
            self.indice += 1
            if self.indice >= len(self.buffer):
                self.ativo = False
        return True

    @staticmethod
    def desenhar_botao(destino):
        r = pygame.Rect(124, 683, 202, 45)
        pygame.draw.rect(destino, (28, 55, 90), r, border_radius=10)
        pygame.draw.rect(destino, (155, 221, 247), r, 2, border_radius=10)
        font = pygame.font.Font(None, 28)
        img = font.render('VER REPLAY', True, (244, 250, 255))
        destino.blit(img, img.get_rect(center=r.center))
        return r


class PaisagemSonora:
    """Ambiente musical autoral contínuo com crossfade por bioma.

    Reutiliza mixer existente; usa dois canais reservados de numeração alta.
    Não reinicia trilha base, nem altera o volume de SFX dos demais canais.
    """
    _idx = {b: i for i, b in enumerate(BIOMES)}
    DURACAO = 2  # segundos de loop por bioma
    RATE = 22050

    def __init__(self):
        self.sons = {}
        self.canais = []
        self.ativo = None
        self.tempo = 0
        self.volume = [0.0, 0.0]
        self.slot = 0
        self.disponivel = False
        try:
            if pygame.mixer.get_init():
                pygame.mixer.set_num_channels(max(16, pygame.mixer.get_num_channels()))
                self.canais = [pygame.mixer.Channel(14), pygame.mixer.Channel(15)]
                self.disponivel = True
        except pygame.error:
            self.disponivel = False

    def _som(self, bioma):
        if bioma in self.sons:
            return self.sons[bioma]
        # Ruído pseudoaleatório controlado + subharmônicos, loop sem estalos:
        # envelope pequeno nas extremidades, no máximo 2 segundos de amostra.
        rng = random.Random(317300 + self._idx[bioma] * 113)
        buf = array('h')
        freqs = {'cidade': (62, .055), 'neve': (130, .015), 'deserto': (82, .07),
                 'vulcao': (46, .085), 'floresta': (205, .025),
                 'cidade_futurista': (110, .045), 'ilhas_celestes': (262, .014)}
        freq, noise_amp = freqs[bioma]
        spec = pygame.mixer.get_init() or (self.RATE, -16, 2)
        rate, fmt, chans = spec
        count = rate * self.DURACAO
        wind = 0.0
        for i in range(count):
            t = i / rate
            wind = wind * .993 + (rng.random() * 2.0 - 1.0) * .007
            env = min(1., t / .045, (self.DURACAO - t) / .045)
            tone = (math.sin(2 * math.pi * freq * t) * .018
                    + math.sin(2 * math.pi * freq * .5 * t) * .013
                    + noise_amp * wind)
            # Motivos ambientais reconhecíveis, sem repetir a música de cada bioma.
            if bioma == 'cidade':
                # Compressores de trem / maquinaria de fundo, suave.
                pulse = max(0., 1. - ((t * 3.0) % 1.) * 7.)
                tone += .014 * pulse * math.sin(2 * math.pi * 72 * t)
            elif bioma == 'neve':
                # Assobio gelado e leve sino distante.
                tone += .009 * math.sin(2 * math.pi * 390 * t) * (0.5 + .5 * math.cos(math.pi * t))
            elif bioma == 'deserto':
                # Rajadas arenosas com oscilação de intensidade.
                tone += .012 * wind * (1 + math.sin(2 * math.pi * .5 * t))
            elif bioma == 'vulcao':
                # Borbulhas e pulsos de magma, graves e espaçados.
                burst = max(0., 1 - ((t * 2.5) % 1.) * 6.)
                tone += .024 * burst * math.sin(2 * math.pi * 37 * t)
            elif bioma == 'floresta':
                # Dois cantos de pássaro, distantes, com envelope suave.
                chirp = max(0., 1 - abs((t * 2) % 2 - .8) * 4.)
                tone += .013 * chirp * math.sin(2 * math.pi * (670 + 150 * t) * t)
            elif bioma == 'cidade_futurista':
                # Pulsos eletrônicos de sinalização sintética.
                tick = max(0., 1 - ((t * 4) % 1.) * 9.)
                tone += .012 * tick * math.sin(2 * math.pi * (360 + 80 * int(t * 4) % 3) * t)
            elif bioma == 'ilhas_celestes':
                # Harmônicos claros e sinos etéreos, sem percussão.
                tone += .009 * math.sin(2 * math.pi * 523.25 * t) * (.5 + .5 * math.cos(math.pi * t))
            level = max(-.25, min(.25, tone * max(0.0, env)))
            val = int(level * 32767)
            if chans == 1:
                buf.append(val)
            else:
                buf.extend((val, val))
        sound = pygame.mixer.Sound(buffer=buf.tobytes())
        self.sons[bioma] = sound
        return sound

    def atualizar(self, bioma, estado, vol_sfx, clima='limpo'):
        if not self.disponivel:
            return
        jogando = estado == 'JOGANDO' and bioma in self._idx and vol_sfx > 0.0
        if jogando and bioma != self.ativo:
            self.slot = 1 - self.slot
            canal = self.canais[self.slot]
            canal.play(self._som(bioma), loops=-1)
            canal.set_volume(0.)
            self.ativo = bioma
        clima_mult = 1.2 if clima in ('chuva', 'tempestade', 'nevasca', 'cinzas', 'tempestade_areia') else 1.0
        alvo = min(.34, vol_sfx * .28 * clima_mult)
        for i, canal in enumerate(self.canais):
            meta = alvo if jogando and i == self.slot else 0.0
            self.volume[i] += (meta - self.volume[i]) * .035
            canal.set_volume(max(0., self.volume[i]))
            if i != self.slot and self.volume[i] < .002 and canal.get_busy():
                canal.stop()
        if not jogando and all(v < .002 for v in self.volume):
            self.ativo = None

    def parar(self):
        for ch in self.canais:
            ch.stop()
        self.volume = [0., 0.]
        self.ativo = None


class HarmonizadorFrames:
    """Regra comum de luz superior / sombra inferior para sprites existentes.

    Usa RGB sem editar alpha; preserva silhueta/colisão e quadros de origem.
    """
    def __init__(self, limite=512):
        self.cache = OrderedDict()
        self.limite = limite

    def processar(self, original, categoria='jogador'):
        chave = (id(original), categoria)
        entry = self.cache.get(chave)
        if entry and entry[0] is original:
            self.cache.move_to_end(chave)
            return entry[1]
        # Não interfere com sprites de formato sem canal de alpha.
        out = original.copy().convert_alpha()
        w, h = out.get_size()
        if w > 0 and h > 7:
            import numpy as np
            alpha = pygame.surfarray.array_alpha(out)
            rgb = pygame.surfarray.pixels3d(out)
            # Luz única esquerda/superior sem corruir cores de identidade e olhos.
            ys = np.arange(h, dtype=np.float32)[None, :]
            xs = np.arange(w, dtype=np.float32)[:, None]
            luz = np.clip((.45 - ys / h), 0, 1) * (.70 + .30 * (1 - xs / w))
            sombra = np.clip((ys / h - .62), 0, 1) * (.20 + .10 * xs / w)
            mascara = (alpha > 225) & (rgb[:, :, 0] + rgb[:, :, 1] + rgb[:, :, 2] > 115)
            gain = np.clip(1 + luz * .11 - sombra * .13, .88, 1.11)
            dados = rgb.astype(np.float32)
            rgb[:, :, :] = np.where(mascara[:, :, None],
                                   np.clip(dados * gain[:, :, None], 0, 255), dados).astype('uint8')
            del rgb
            assert (pygame.surfarray.array_alpha(out) == alpha).all()
        self.cache[chave] = (original, out)
        if len(self.cache) > self.limite:
            self.cache.popitem(last=False)
        return out
