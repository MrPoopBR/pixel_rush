"""Regressao isolada com pygame-ce: zero pontos no tutorial, contagem apos o fim."""
import ast
import copy
import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

pygame.init()
pygame.display.set_mode((64, 64))

codigo = Path("PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py").read_text(encoding="utf-8")
arvore = ast.parse(codigo)
simulacao = next(n for n in ast.walk(arvore) if isinstance(n, ast.FunctionDef)
                 and n.name == "atualizar_simulacao")
tutorial = next(n for n in simulacao.body if isinstance(n, ast.If)
                and "tutorial_corrida is not None" in ast.unparse(n.test)
                and "tutorial_corrida.ativo" in ast.unparse(n.test))
incremento_frame = next(n for n in simulacao.body if isinstance(n, ast.AugAssign)
                        and isinstance(n.target, ast.Name) and n.target.id == "frame_count")
normal = next(n for n in ast.walk(simulacao) if isinstance(n, ast.If)
              and ast.unparse(n.test) == "not jogador.morrendo"
              and any(isinstance(a, ast.AugAssign) and isinstance(a.target, ast.Name)
                      and a.target.id == "pontuacao" for a in ast.walk(n)))

# A licao usa o fluxo da producao e retorna antes do incremento NORMAL.
assert isinstance(tutorial.body[-1], ast.Return), "A licao precisa retornar ao fim"
assert not any(isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign))
               and any(isinstance(t, ast.Name) and t.id == "pontuacao"
                       for t in (n.targets if isinstance(n, ast.Assign)
                                 else [n.target]))
               for n in ast.walk(tutorial)), "Pontuacao alterada dentro do tutorial"

reiniciar = next(n for n in ast.walk(arvore) if isinstance(n, ast.FunctionDef)
                 and n.name == "reiniciar_jogo")
assert any(isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant)
           and n.value.value == 0 and any(isinstance(t, ast.Name) and
           t.id == "pontuacao" for t in n.targets) for n in reiniciar.body)

# Executa exatamente os nos AST originais dos dois caminhos de pontuacao;
# as demais dependencias recebem dublês e nao tocam no save do jogo.
globais = ["frame_count", "pontuacao", "moedas_coletadas", "palavra_hud_ate",
           "tutorial_concluido_ate", "palavra_festa_ate",
           "spawn_bloqueado_frames", "febre_turbo_distancia_restante",
           "febre_timer"]
metodo = ast.FunctionDef(name="tick_teste",
                         args=ast.arguments(posonlyargs=[], args=[], vararg=None,
                                            kwonlyargs=[], kw_defaults=[], kwarg=None,
                                            defaults=[]),
                         body=[ast.Global(names=globais), copy.deepcopy(incremento_frame),
                               copy.deepcopy(tutorial), copy.deepcopy(normal)],
                         decorator_list=[], returns=None, type_comment=None)
codigo_teste = compile(ast.fix_missing_locations(
    ast.Module(body=[metodo], type_ignores=[])), "<pontuacao-real-tutorial>", "exec")

class Licoes:
    ativo = True
    etapa = "pular"
    contagem_coletas = 0
    ganho = 0
    concluiu = False
    def atualizar(self, *args):
        if self.concluiu:
            self.ativo = False
        return self.ganho, self.concluiu

t = Licoes()
salvamentos = []
ns = {
    "frame_count": 0, "pontuacao": 0, "moedas_coletadas": 0,
    "palavra_hud_ate": 0, "tutorial_concluido_ate": 0,
    "palavra_festa_ate": 0, "spawn_bloqueado_frames": 0,
    "febre_turbo_distancia_restante": 0, "febre_timer": 0,
    "estado": "JOGANDO", "tutorial_corrida": t,
    "jogador": SimpleNamespace(morrendo=False, tempo_mult=0, tempo_ima=0,
                                tempo_turbo=0, rect=pygame.Rect(40, 650, 80, 80)),
    "bg_parallax": None, "todos_sprites": None, "letras_coletaveis": None,
    "palavra_partida": None, "particulas": None, "pool_manager": None,
    "gerenciador_sons": None, "dados": {"vol_sfx": 0.7},
    "salvar_dados": lambda dados: salvamentos.append(dict(dados)),
    "tempo_spawn_atual": 1500, "EVENTO_GERAR": pygame.USEREVENT + 2,
    "pygame": pygame, "criar_explosao_particulas": lambda *args: None,
}
exec(codigo_teste, ns)
tick = ns["tick_teste"]
etapas = ("pular", "pular_longo", "agachar", "swipe_down", "moedas", "letras")
for etapa in etapas:
    t.etapa = etapa
    for tentativa in range(75):
        t.ganho = 1 if etapa == "moedas" and tentativa == 0 else 0
        t.concluiu = etapa == "letras" and tentativa == 74
        if t.concluiu:
            t.ganho = 50
        tick()
        assert ns["pontuacao"] == 0, (
            f"A etapa {etapa} gerou pontos antes da corrida: {ns['pontuacao']}")
assert ns["moedas_coletadas"] == 51, "Moedas e bonus nao devem ser apagados"
assert t.ativo is False and len(salvamentos) == 1
assert salvamentos[0]["tutorial_inicial_concluido"] is True
assert ns["pontuacao"] == 0, "Nem o ultimo tick do tutorial deve pontuar"

tick()
assert ns["pontuacao"] == 2, "A corrida normal deve iniciar em dois pontos"
tick()
assert ns["pontuacao"] == 4, "O placar deve continuar a progredir normalmente"
ns["jogador"].tempo_mult = 10
tick()
assert ns["pontuacao"] == 8, "Multiplicador da corrida deve ser preservado"
print("APROVADO: 450 ticks/6 licoes em 0, recompensa preservada, corrida 2-4-8")
pygame.quit()
