# Pixel Rush v3.208.0 — aprendizado contextual pós-morte.
# Somente apresentação e categorização da causa real de morte; sem save nem RNG.
import pygame


class AprendizadoContextual:
    __slots__ = ("causa", "_rotulos")

    def __init__(self):
        self.causa = None
        self._rotulos = {}

    def limpar(self):
        self.causa = None

    def registrar(self, categoria, objeto=None):
        """Armazena apenas o primeiro evento fatal efetivamente confirmado."""
        if self.causa is not None:
            return
        if categoria == 'obstaculo':
            nome = type(objeto).__name__ if objeto is not None else ''
            tipo = str(getattr(objeto, 'tipo', '')).lower() if objeto is not None else ''
            if nome == 'ObstaculoVoador' or any(x in tipo for x in ('drone', 'voador', 'morcego', 'coruja')):
                categoria = 'aereo'
            elif nome == 'ObstaculoPulaPula':
                categoria = 'movel'
            elif nome == 'ObstaculoTerrestre' or tipo in ('bola_neve', 'escorpiao'):
                categoria = 'solo'
            else:
                categoria = 'desafio'
        if categoria not in ('buraco', 'laser_corredor', 'laser_perigo', 'aereo', 'movel', 'solo', 'desafio'):
            categoria = 'desafio'
        self.causa = categoria

    def mensagem(self, idioma='pt_BR'):
        if not self.causa:
            return None
        pt = {
            'buraco': ('QUEDA NO BURACO', 'Salte antes da borda e observe a pista.'),
            'laser_corredor': ('CORREDOR DE LASERS', 'Siga a abertura segura entre os feixes.'),
            'laser_perigo': ('COLISAO COM LASER', 'Observe o aviso e ajuste a altura a tempo.'),
            'aereo': ('PERIGO AEREO', 'Antecipe o inimigo e ajuste a altura.'),
            'movel': ('OBSTACULO MOVEL', 'Observe o movimento antes de reagir.'),
            'solo': ('OBSTACULO NO SOLO', 'Prepare o salto antes de se aproximar.'),
            'desafio': ('COLISAO COM OBSTACULO', 'Observe a silhueta e planeje a esquiva.'),
        }
        en = {
            'buraco': ('FELL INTO A GAP', 'Jump before the edge; watch the track.'),
            'laser_corredor': ('LASER CORRIDOR', 'Follow the safe opening between beams.'),
            'laser_perigo': ('LASER COLLISION', 'Watch the warning and adjust your height.'),
            'aereo': ('AIRBORNE HAZARD', 'Anticipate it and adjust your height.'),
            'movel': ('MOVING OBSTACLE', 'Watch its movement before reacting.'),
            'solo': ('GROUND OBSTACLE', 'Prepare your jump before you get close.'),
            'desafio': ('OBSTACLE COLLISION', 'Read the silhouette and plan an escape.'),
        }
        return (en if idioma == 'en_US' else pt)[self.causa]

    def desenhar(self, superficie, idioma='pt_BR'):
        """Desenha apenas na faixa livre entre card de resultados e botão de reinício.

        Superfícies de texto ficam cacheadas (no máximo 14 variantes).
        """
        mensagem = self.mensagem(idioma)
        if not mensagem:
            return False
        chave = (self.causa, idioma == 'en_US')
        linhas = self._rotulos.get(chave)
        if linhas is None:
            fonte = pygame.font.Font(None, 17)
            titulo, orientacao = mensagem
            linhas = (fonte.render(titulo, True, (250, 219, 120)),
                      fonte.render(orientacao, True, (225, 236, 245)))
            self._rotulos[chave] = linhas
        for img, y in zip(linhas, (503, 521)):
            # Apenas desenho simples, sem mudar posições/clickboxes originais.
            superficie.blit(img, (225 - img.get_width() // 2, y))
        return True
