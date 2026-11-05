"""Ferramentas 2D integradas ao Pixel Rush v3.108.0.

FABRIK + amortecimento para props recortados; máscara SDF destrutível em partes
puramente decorativas; oclusão acústica por raycasting em mapa geométrico.
Não são SAM 2, IK artístico com pesos pintados, acústica de sala tridimensional
nem destruição que altera as hitboxes principais.
"""
import math
from collections import OrderedDict
import pygame


def limitar(x, minimum, maximum):
    return max(minimum, min(maximum, x))


class ArticulacaoFABRIK:
    """Corrente de 3 segmentos com âncora fixa e alvo guiado por vento.

    Coordenadas locais: âncora na base, eixo y para cima. Atualização por
    integração amortecida e correção FABRIK forward/backward.
    """
    def __init__(self, height=120, seed=0):
        self.length = max(24.0, float(height))
        self.segments = (self.length * .34, self.length * .33, self.length * .33)
        self.nodes = [(0.0, 0.0), (0.0, self.segments[0]),
                      (0.0, sum(self.segments[:2])), (0.0, self.length)]
        self.phase = (seed % 19) * .29
        self.velocity = 0.0
        self.displacement = 0.0

    def update(self, frame, wind=0.0, wake=0.0):
        desired = (math.sin(frame * (.031 + abs(wind) * .009) + self.phase)
                   * (1.8 + abs(wind) * 4.3) + wake * 6.0)
        self.velocity = (self.velocity + (desired - self.displacement) * .095) * .79
        self.displacement = limitar(self.displacement + self.velocity, -22., 22.)
        target = (self.displacement, math.sqrt(max(0., self.length ** 2 - self.displacement ** 2)))
        points = list(self.nodes)
        for _ in range(4):
            points[3] = target
            for idx in range(2, -1, -1):
                dx = points[idx][0] - points[idx + 1][0]
                dy = points[idx][1] - points[idx + 1][1]
                distance = max(1e-6, math.hypot(dx, dy))
                d = self.segments[idx] / distance
                points[idx] = (points[idx + 1][0] + dx * d, points[idx + 1][1] + dy * d)
            points[0] = (0.0, 0.0)
            for idx in range(3):
                dx = points[idx + 1][0] - points[idx][0]
                dy = points[idx + 1][1] - points[idx][1]
                distance = max(1e-6, math.hypot(dx, dy))
                d = self.segments[idx] / distance
                points[idx + 1] = (points[idx][0] + dx * d, points[idx][1] + dy * d)
        self.nodes = points

    def offset_at(self, fraction_from_top):
        fraction_from_top = limitar(fraction_from_top, 0., 1.)
        k = (1. - fraction_from_top) * 3.
        a = min(2, int(k))
        t = limitar(k - a, 0., 1.)
        return self.nodes[a][0] * (1. - t) + self.nodes[a + 1][0] * t

    def deform(self, image, strip=4, target=None):
        """Skinning identico, com buffer QA opcional para evitar alocacoes."""
        width, height = image.get_size()
        pad = 26
        tamanho = (width + 2 * pad, height)
        if target is None or target.get_size() != tamanho:
            result = pygame.Surface(tamanho, pygame.SRCALPHA)
        else:
            result = target
            # Todos os pixels fora das tiras precisam continuar transparentes.
            result.fill((0, 0, 0, 0))
        # R23: tira a tira, exatamente na mesma ordem, mas com uma
        # unica chamada SDL em C. 180 amostras RGBA Floresta/Neve idênticas.
        # Conserva o mesmo buffer reutilizado; nao muda cinemática ou pose.
        # Em rigs pequenos, o lote pode custar mais do que os blits
        # originais (lab Neve). Limitar a grandes copas de arvore:
        # Floresta 435px, ganho observado em duas execuções independentes.
        # As demais alturas mantem literalmente a sequencia SDL anterior.
        if height < 420:
            for y in range(0, height, strip):
                dx = int(round(self.offset_at(y / max(1, height - 1))))
                result.blit(image, (pad + dx, y),
                            pygame.Rect(0, y, width, min(strip, height - y)))
            return result, pad
        denom = max(1, height - 1)
        operacoes = []
        for y in range(0, height, strip):
            dx = int(round(self.offset_at(y / denom)))
            operacoes.append((image, (pad + dx, y), (0, y, width, min(strip, height - y))))
        if operacoes:
            result.blits(operacoes, doreturn=False)
        return result, pad


class SDFDestrutivel:
    """Geometria decorativa com operações SDF persistentes por chunk.

    Os recortes já preparados são desconstruídos em uma MÁSCARA ALFA real.
    Nunca altera a hitbox do chão nem salva mutações no save do usuário.
    """
    def __init__(self, max_chunks=24, chunk_width=360, height=18):
        self.max_chunks = max_chunks
        self.chunk_width = chunk_width
        self.height = height
        self.chunks = OrderedDict()
        try:
            import numpy  # opcionais os efeitos SDF em instalações Pygame puro
            self.enabled = True
        except ImportError:
            self.enabled = False

    def impact(self, world_x, radius=11):
        if not self.enabled:
            return
        import numpy as np
        index = math.floor(world_x / self.chunk_width)
        cx = int(world_x - index * self.chunk_width)
        mask = self.chunks.get(index)
        if mask is None:
            mask = np.full((self.height, self.chunk_width), 255, dtype=np.uint8)
        yy, xx = np.ogrid[:self.height, :self.chunk_width]
        # Elipse SDF: buraco na face do adorno, sem interferir na física.
        d = np.sqrt(((xx - cx) / max(1.0, radius)) ** 2 +
                    ((yy - self.height * .60) / max(1.0, radius * .52)) ** 2) - 1.0
        mask[d <= 0] = 0
        edge = (d > 0) & (d < .15)
        mask[edge] = np.minimum(mask[edge], 125)
        self.chunks[index] = mask
        self.chunks.move_to_end(index)
        while len(self.chunks) > self.max_chunks:
            self.chunks.popitem(last=False)

    def get_mask(self, index):
        return self.chunks.get(index)

    def apply(self, decorative_layer, travel, y=472):
        """Recorta pixels reais da camada de arte, não desenha algo por cima.

        Layer é uma cópia temporária em RGBA do pano de fundo. A operação
        modifica o canal alfa dos pixels dos chunks danificados; o chão físico
        e as máscaras de colisão não são alterados.
        """
        import numpy as np
        if not self.chunks:
            return decorative_layer
        width, height = decorative_layer.get_size()
        first = math.floor(travel / self.chunk_width)
        alpha = pygame.surfarray.pixels_alpha(decorative_layer)
        for index in (first, first + 1, first + 2):
            mask = self.chunks.get(index)
            if mask is None:
                continue
            x = round(index * self.chunk_width - travel)
            left, right = max(0, x), min(width, x + self.chunk_width)
            top, bottom = max(0, y), min(height, y + self.height)
            if right <= left or bottom <= top:
                continue
            patch = mask[top - y:bottom - y, left - x:right - x]
            region = alpha[left:right, top:bottom]
            region[...] = (region.astype(np.uint16) * patch.T.astype(np.uint16) // 255).astype(np.uint8)
        del alpha
        return decorative_layer


class OclusaoAcustica2D:
    """Raycasting screen-space sobre mapa de ocupação da pintura.

    O mapa heurístico não prova a existência de paredes; o resultado é
    uma atenuação artística, não um simulador físico de acústica arquitetônica.
    """
    def __init__(self):
        self.cache = {}

    @staticmethod
    def fator(geometry, source, listener, samples=18):
        if geometry is None:
            return 0.0
        w, h = geometry.get_size()
        if w <= 1 or h <= 1:
            return 0.0
        blocked = 0.0
        for i in range(1, samples):
            ratio = i / float(samples)
            px = round(listener[0] + (source[0] - listener[0]) * ratio)
            py = round(listener[1] + (source[1] - listener[1]) * ratio)
            if 0 <= px < w and 0 <= py < h:
                # canal G ~ proxy de cobertura do material no mapa auxiliar.
                occupancy = geometry.get_at((px, py)).g / 255.0
                blocked += max(0., occupancy - .38)
        return limitar(blocked / max(1., samples - 1) * 1.6, 0., .92)

    def som_filtrado(self, sound, level):
        """Filtro passa-baixas FFT pré-calculado por faixa de oclusão."""
        level = int(limitar(round(level * 4), 0, 4))
        if level == 0 or sound is None:
            return sound
        key = (id(sound), level)
        if key in self.cache:
            return self.cache[key]
        try:
            import numpy as np
            original = pygame.sndarray.array(sound)
            sample_rate = (pygame.mixer.get_init() or (44100, -16, 2))[0]
            spectrum = np.fft.rfft(original.astype(np.float32), axis=0)
            frequencies = np.fft.rfftfreq(original.shape[0], 1. / sample_rate)
            cutoff = (7000, 4800, 2600, 1500, 950)[level]
            cutoff_filter = 1. / np.sqrt(1. + (frequencies / cutoff) ** 6)
            if spectrum.ndim == 2:
                cutoff_filter = cutoff_filter[:, None]
            recovered = np.fft.irfft(spectrum * cutoff_filter, n=original.shape[0], axis=0)
            result = np.clip(recovered, -32768, 32767).astype(original.dtype)
            filtered = pygame.sndarray.make_sound(np.ascontiguousarray(result))
            if len(self.cache) > 32:
                self.cache.clear()
            self.cache[key] = filtered
            return filtered
        except (ValueError, TypeError, pygame.error, ImportError, AttributeError):
            return sound
