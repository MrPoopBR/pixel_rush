"""Regressao isolada de movimento e repeticao tutorial v3.277.16 (pygame dummy)."""
import ast
import os
from pathlib import Path
import pygame

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
pygame.display.init()
pygame.display.set_mode((64, 64))

class Perigo(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.rect = pygame.Rect(x, 680, 40, 45)
        self._x = float(x)
        self.movimentos = 0

    def update(self, velocidade):
        self._x -= float(velocidade)
        self.rect.x = int(self._x)
        self.movimentos += 1
        if self.rect.right < -60:
            self.kill()

class Jogador:
    def __init__(self):
        self.rect = pygame.Rect(40, 650, 80, 80)
        self.chao_y = 730
        self.no_chao = True
        self.morrendo = False
        self.velocidade_y = 0
        self.agachado = False
        self.descida_rapida = False
        self.tempo_morte = 0
        self.coyote_ticks = 0
        self.buffer_pulo_ticks = 0

    def obter_hitbox(self):
        return pygame.Rect(self.rect.x + 20, self.rect.y + 20, 40, 55)

class Base:
    def __init__(self, jogador, *args, **kwargs):
        self.jogador = jogador
        self.ativo = True
        self.etapa = 'pular'
        self.ticks = 0
        self.ticks_etapa = 0
        self.sucesso = False
        self.tempo_confirmacao = 0
        self.objetos = []
        self._etapa_preparada = False
        self.passo_obstaculo = 6

    def _preparar(self, todos, letras, palavra):
        for obj in self.objetos:
            obj.kill()
        self.objetos = [Perigo(self.jogador.rect.right + 165)]
        todos.add(self.objetos[0])
        self._etapa_preparada = True
        self.sucesso = False
        self.tempo_confirmacao = 0
        self.ticks_etapa = 0

    def atualizar(self, jogador, fundo, todos, letras, palavra, particulas,
                  pool, som, volume, frame):
        self.ticks += 1
        self.ticks_etapa += 1
        if self.sucesso:
            for obj in self.objetos:
                obj.rect.x -= int(self.passo_obstaculo)
            if all(obj.rect.right < jogador.rect.left - 35 for obj in self.objetos):
                self.tempo_confirmacao += 1
            if self.tempo_confirmacao >= 16:
                self.etapa = 'pular_longo'
                self._etapa_preparada = False
        return 0, False

classe = next(x for x in ast.parse(Path('pixelrush_tutorial_prod_v32771.py').read_text()).body
              if isinstance(x, ast.ClassDef) and x.name == 'TutorialCorrida')
escopo = {'_TutorialBase': Base, '_USAR_GESTOS': False, 'pygame': pygame}
exec(compile(ast.Module(body=[classe], type_ignores=[]), '<tutorial-producao>', 'exec'), escopo)
Tutorial = escopo['TutorialCorrida']

def passo(tutorial, todos):
    return tutorial.atualizar(tutorial.jogador, None, todos, None, None, None,
                             None, None, 1.0, tutorial.ticks)

jogador = Jogador()
todos = pygame.sprite.Group()
t = Tutorial(jogador)
passo(t, todos)
inicio = t.objetos[0].rect.x
for _ in range(5):
    passo(t, todos)
assert t.objetos[0].rect.x == inicio - 30, 'perigo deve andar 6 px por passo sem gesto'
for _ in range(120):
    passo(t, todos)
    if t.tentativas >= 2:
        break
assert t.tentativas >= 2 and t.etapa == 'pular' and jogador.no_chao
assert not jogador.morrendo, 'tutorial nunca gera game over'
assert t.objetos[0].rect.x == jogador.rect.right + 165, 'deve rebobinar o desafio'

jogador = Jogador()
todos = pygame.sprite.Group()
t = Tutorial(jogador)
passo(t, todos)
jogador.rect.bottom = 500
jogador.no_chao = False
t.sucesso = True
inicio = t.objetos[0].rect.x
passo(t, todos)
assert t.objetos[0].rect.x == inicio - 6, 'nao deslocar duas vezes apos acerto'
for _ in range(90):
    passo(t, todos)
    if t.etapa == 'pular_longo':
        break
assert t.etapa == 'pular_longo' and t.tentativas == 0
print('OK: movimento, retry infinito, rewind, sem morte e sem deslocamento duplo')
