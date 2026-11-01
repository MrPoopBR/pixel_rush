"""QA pygame-ce real (SDL dummy) das tres correcoes isoladas da v3.277.17."""
import ast
import os
import random
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.display.init()
pygame.display.set_mode((450, 800))

def classe_ast(caminho, nome):
    modulo = ast.parse(Path(caminho).read_text(encoding="utf-8"), filename=caminho)
    return next(n for n in modulo.body if isinstance(n, ast.ClassDef) and n.name == nome)

def compilar_classe(no, ambiente, arquivo):
    codigo = compile(ast.fix_missing_locations(ast.Module(body=[no], type_ignores=[])),
                     arquivo, "exec")
    exec(codigo, ambiente)
    return ambiente[no.name]

# Utilizar diretamente a funcao real de hitbox do Jogador, sem carregar o
# jogo inteiro, que inicializa serviços/sistema de janela ao importar.
jogador_ast = classe_ast("PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py", "Jogador")
obter_hitbox = next(n for n in jogador_ast.body
                    if isinstance(n, ast.FunctionDef) and n.name == "obter_hitbox")
escopo_hitbox = {"pygame": pygame}
exec(compile(ast.fix_missing_locations(ast.Module(body=[obter_hitbox], type_ignores=[])),
             "<hitbox-real-do-jogador>", "exec"), escopo_hitbox)

class JogadorTeste:
    obter_hitbox = escopo_hitbox["obter_hitbox"]
    def __init__(self):
        self.rect = pygame.Rect(40, 650, 80, 80)
        self.chao_y = 730
        self.base_h = 80
        self.agachado = False
        self.no_chao = True
        self.morrendo = False
        self.descida_rapida = False
        self.velocidade_y = 0
        self.tempo_morte = 0
        self.coyote_ticks = 0
        self.buffer_pulo_ticks = 0
    def iniciar_descida_rapida(self, som=None, volume=1.0):
        if not self.morrendo and not self.no_chao:
            self.descida_rapida = True
            self.velocidade_y = max(self.velocidade_y, 18.0)
    def pular(self, som=None, volume=1.0):
        if self.no_chao:
            self.no_chao = False

# Dimensoes reais do pombo no catalogo original, nao uma retangulo arbitrario.
origem = ast.parse(Path("pixelrush_ameacas_v3127.py").read_text(encoding="utf-8"))
definicao = next(n.value for n in origem.body
                 if isinstance(n, ast.Assign) and any(
                     isinstance(t, ast.Name) and t.id == "AMEACAS" for t in n.targets))
catalogo = ast.literal_eval(definicao)
_, _, w_pombo, h_pombo, movimento = catalogo["C2"]
assert movimento == "mergulho" and (w_pombo, h_pombo) == (54, 42)

class PomboCidade(pygame.sprite.Sprite):
    def __init__(self, x, codigo):
        super().__init__()
        self.codigo = codigo
        self.chao = 730
        self.rect = pygame.Rect(int(x), 691 - h_pombo, w_pombo, h_pombo)
        self._base_y = self.rect.y
        self._x = float(x)
        self._hitboxes_precisas_v342 = (
            pygame.Rect(max(4, w_pombo // 8), max(4, h_pombo // 9),
                        max(8, w_pombo - max(8, w_pombo // 4)),
                        max(8, h_pombo - max(7, h_pombo // 5))),)
    def update(self, velocidade):
        self._x -= float(velocidade)
        self.rect.x = int(self._x)

class HidranteTeste(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.rect = pygame.Rect(x, 670, 51, 60)

base_ns = {"pygame": pygame, "random": random, "ETAPAS":
           ("pular", "pular_longo", "agachar", "swipe_down", "moedas", "letras")}
base = compilar_classe(classe_ast("pixelrush_tutorial_corrida_v3274.py",
                                  "TutorialCorrida"), base_ns, "<tutorial-v3274>")
city_ns = {"_Anterior": base, "pygame": pygame, "ETAPAS": base_ns["ETAPAS"],
           "ROTAS_CIDADE": {"pular": ("C3",),
                            "pular_longo": ("C3", "HIDRANTE"),
                            "agachar": ("C2",), "swipe_down": ("C2",)},
           "AmeacaBioma": PomboCidade, "HidranteCidade": HidranteTeste}
city = compilar_classe(classe_ast("pixelrush_tutorial_corrida_v3276.py",
                                  "TutorialCorrida"), city_ns, "<tutorial-v3276>")
prod_ns = {"_TutorialBase": city, "_USAR_GESTOS": True, "pygame": pygame}
prod = compilar_classe(classe_ast("pixelrush_tutorial_prod_v32771.py",
                                  "TutorialCorrida"), prod_ns, "<tutorial-prod>")

# Lição 3: o C2 volta à altura real da Cidade. Sua hitbox real atinge
# um jogador em pe, mas permite passar agachado.
jogador = JogadorTeste()
t = prod(jogador, classe_cidade=PomboCidade, classe_hidrante=HidranteTeste)
t.etapa_indice = 2
grupo = pygame.sprite.Group()
t._preparar(grupo, None, None)
assert len(t.objetos) == 1
pombo = t.objetos[0]
assert pombo.rect.bottom == 691 and pombo._base_y == 649
pombo.rect.centerx = jogador.rect.centerx
assert t._atingiu_corpo(jogador.obter_hitbox(), pombo), "Em pe deve haver contato"
jogador.agachado = True
assert not t._atingiu_corpo(jogador.obter_hitbox(), pombo), "Agachado deve passar"
jogador.agachado = False

# Licao 4 conserva a altura anterior: nao modificar indevidamente swipe-down.
t.etapa_indice = 3
t._preparar(grupo, None, None)
assert t.objetos[0].rect.y == jogador.chao_y - 118

# Liberacao sem FINGERMOTION deve reconhecer swipe, mesmo quando o SDL
# interpola eventos de mouse entre FINGERDOWN e FINGERUP.
jogador.no_chao = False
t.processar_evento(pygame.event.Event(pygame.FINGERDOWN, {"x": .2, "y": .3, "finger_id": 1}))
t.processar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                     {"button": 1, "pos": (90, 250)}))
t.processar_evento(pygame.event.Event(pygame.MOUSEBUTTONUP,
                                     {"button": 1, "pos": (90, 250)}))
t.processar_evento(pygame.event.Event(pygame.FINGERUP, {"x": .2, "y": .45, "finger_id": 1}))
assert t.swipe_feito and jogador.descida_rapida, "FINGERUP deve registrar descida"
assert not t.toque_ativo and t.swipe_iniciado is None

# Um swipe insuficiente ou liberado no solo nao pode contar como sucesso.
for no_chao, y_final in ((False, .34), (True, .48)):
    jogador.no_chao = no_chao
    jogador.descida_rapida = False
    t.swipe_feito = False
    t.processar_evento(pygame.event.Event(pygame.FINGERDOWN, {"x": .2, "y": .3, "finger_id": 2}))
    t.processar_evento(pygame.event.Event(pygame.FINGERUP,
                                         {"x": .2, "y": y_final, "finger_id": 2}))
    assert not t.swipe_feito and not jogador.descida_rapida

# Inspeciona a condicao REAL de desenho da entrada: permitir animacao nas
# corridas normais, impedir deslocamento visual durante qualquer tutorial ativo.
arvore = ast.parse(Path("PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py").read_text(encoding="utf-8"))
candidatos = [n for n in ast.walk(arvore) if isinstance(n, ast.If) and any(
    isinstance(child, ast.Assign) and any(
        isinstance(target, ast.Name) and target.id == "_prod_t"
        for target in child.targets)
    for child in n.body)]
assert len(candidatos) == 1
condicao = compile(ast.Expression(candidatos[0].test), "<entrada-visual>", "eval")
ctx = {"estado": "JOGANDO", "jogador": jogador, "frame_count": 10,
       "entrada_corrida_ate": 70, "tutorial_corrida": SimpleNamespace(ativo=True)}
assert not eval(condicao, {}, ctx), "No tutorial, render deve acompanhar a hitbox"
ctx["tutorial_corrida"].ativo = False
assert eval(condicao, {}, ctx), "Fora do tutorial, a animacao existente permanece"
print("APROVADO: pombo real em pe/agachado, swipe FINGERUP, mouse SDL, entrada sincronizada")
