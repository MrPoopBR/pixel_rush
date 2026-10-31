"""Letras coletaveis por corrida — Pixel Rush v3.218.0.

Modulo visual/colecao separado do pool de moedas. Sem RNG, gravacao de save,
novo timer SDL, ou modificacao de hitboxes do jogo.
"""
import pygame
import pixelrush_traducoes_v3247 as _i18n247

PALAVRAS = ("PIXEL", "RUSH", "TURBO", "NEON", "COMBO")
BONUS_PALAVRA = 50


class LetraColetavel(pygame.sprite.Sprite):
    _imagens = {}

    def __init__(self, letra, x, y):
        super().__init__()
        self.letra = letra
        imagem = self._imagens.get(letra)
        if imagem is None:
            imagem = pygame.Surface((34, 40), pygame.SRCALPHA)
            pygame.draw.rect(imagem, (14, 29, 49, 240), (2, 3, 30, 34), border_radius=7)
            pygame.draw.rect(imagem, (249, 194, 76), (2, 3, 30, 34), 3, border_radius=7)
            pygame.draw.rect(imagem, (255, 247, 173), (5, 6, 24, 4), border_radius=2)
            fonte = pygame.font.Font(None, 29)
            sombra = fonte.render(letra, True, (32, 30, 50))
            texto = fonte.render(letra, True, (255, 246, 205))
            cx = imagem.get_width() // 2
            imagem.blit(sombra, sombra.get_rect(center=(cx + 1, 23)))
            imagem.blit(texto, texto.get_rect(center=(cx, 22)))
            self._imagens[letra] = imagem
        self.image = imagem
        self.rect = imagem.get_rect(center=(x, y))
        self._x_float = float(self.rect.x)

    def update(self, velocidade):
        self._x_float -= float(velocidade)
        self.rect.x = int(round(self._x_float))
        if self.rect.right < -8:
            self.kill()


class PalavraDaPartida:
    """Uma unica palavra por partida, letras em ordem e bonus unico."""
    def __init__(self):
        self.partidas = -1
        self.palavra = PALAVRAS[0]
        self.progresso = 0
        self.proximo_metro = 240
        self.ativo = None
        self.concluida = False
        self._hud_cache = {}

    def iniciar(self):
        if self.ativo is not None:
            self.ativo.kill()
        self.partidas += 1
        self.palavra = PALAVRAS[self.partidas % len(PALAVRAS)]
        self.progresso = 0
        self.proximo_metro = 240
        self.ativo = None
        self.concluida = False

    def tentar_spawn(self, metros, obstaculos, perigos, buracos, moedas,
                     grupo_todos, grupo_letras, largura, altura):
        if self.concluida:
            return False
        if self.ativo is not None:
            if self.ativo.alive():
                return False
            self.ativo = None
            self.proximo_metro = max(self.proximo_metro, int(metros) + 120)
        if int(metros) < self.proximo_metro:
            return False
        x = int(largura) + 78
        # Rotas acessiveis por pulo curto ou pela corrida; nunca exigir jetpack.
        for y in (int(altura)-163, int(altura)-203, int(altura)-143):
            area = pygame.Rect(x-22, y-26, 44, 52)
            if any(area.inflate(112, 65).colliderect(p.rect) for grupo in
                   (obstaculos, perigos, buracos) for p in grupo):
                continue
            if any(area.colliderect(m.rect) for m in moedas):
                continue
            letra = LetraColetavel(self.palavra[self.progresso], x, y)
            grupo_todos.add(letra)
            grupo_letras.add(letra)
            self.ativo = letra
            return True
        return False

    def coletar(self, jogador_hitbox, metros):
        letra = self.ativo
        if letra is None or not letra.alive() or not jogador_hitbox.colliderect(letra.rect):
            return (False, False, 0)
        letra.kill()
        self.ativo = None
        self.progresso += 1
        self.proximo_metro = int(metros) + 175
        if self.progresso == len(self.palavra):
            self.concluida = True
            return (True, True, BONUS_PALAVRA)
        return (True, False, 0)

    def desenhar_hud(self, tela, idioma="pt_BR"):
        if self.partidas < 0:
            return
        codigo = (self.palavra, self.progresso, str(idioma))
        imagem = self._hud_cache.get(codigo)
        if imagem is None:
            imagem = pygame.Surface((242, 36), pygame.SRCALPHA)
            pygame.draw.rect(imagem, (12, 27, 43, 231), (0, 0, 242, 36), border_radius=8)
            pygame.draw.rect(imagem, (77, 123, 149), (0, 0, 242, 36), 1, border_radius=8)
            pequena = (_i18n247.fonte_unicode(codigo[2], 18)
                       if codigo[2] in _i18n247.ARQUIVOS_FONTES else pygame.font.Font(None, 18))
            grande = pygame.font.Font(None, 23)
            rotulo = _i18n247.rotulo_palavra(codigo[2])
            imagem.blit(pequena.render(rotulo, True, (164, 203, 225)), (9, 4))
            inicio = 90
            for i, letra in enumerate(self.palavra):
                cor = (252, 220, 115) if i < self.progresso else (120, 152, 171)
                x = inicio + i*27
                pygame.draw.rect(imagem, (31, 52, 70), (x-3, 4, 23, 28), border_radius=4)
                imagem.blit(grande.render(letra if i < self.progresso else "·", True, cor), (x+2, 8))
            if self.concluida:
                pygame.draw.rect(imagem, (91, 222, 157), (0, 0, 242, 36), 2, border_radius=8)
            if len(self._hud_cache) >= 30:
                self._hud_cache.clear()
            self._hud_cache[codigo] = imagem
        tela.blit(imagem, (15, 186))
