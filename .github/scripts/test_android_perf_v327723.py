"""PIXEL RUSH v3.277.23: regressao de FPS e teto de RAM para atlas."""
import ast
import importlib.util
import os
from pathlib import Path
import random
import sys
import types
import zlib

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

def testar_qualidade():
    origem = (RAIZ / "PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py").read_text(encoding="utf-8")
    arvore = ast.parse(origem)
    classe = next(n for n in arvore.body if isinstance(n, ast.ClassDef)
                  and n.name == "MonitorQualidadeVisual")
    for android in (True, False):
        ctx = {"E_ANDROID": android}
        exec(compile(ast.Module(body=[classe], type_ignores=[]), "<teste-qualidade>", "exec"), ctx)
        monitor = ctx["MonitorQualidadeVisual"]()
        alvo = 30 if android else 60
        for _ in range(240):
            monitor.atualizar(alvo, 1 / alvo, "auto", True)
        assert not monitor.reduzido, ("reduzido no FPS alvo", android)
        for _ in range(180):
            monitor.atualizar(alvo * .65, 1 / alvo, "auto", True)
        assert monitor.reduzido, ("nao reduziu com lentidao real", android)
        for _ in range(420 if android else 840):
            monitor.atualizar(alvo, 1 / alvo, "auto", True)
        assert not monitor.reduzido, ("nao recuperou qualidade", android)
        monitor.atualizar(alvo, 1 / alvo, "normal", True)
        assert not monitor.reduzido
    print("OK: modos Android 30 FPS e desktop 60 FPS, queda e recuperacao")

def testar_atlas():
    # Fakes exclusivamente na fronteira de import; codigo do manager e o REAL.
    for nome in ("pixelrush_atlas_prod_v32776","pixelrush_world_v3185",
                 "pixelrush_world_prod_v32777","pixelrush_buffers_prod_v32779"):
        sys.modules[nome] = types.ModuleType(nome)
    mundo = sys.modules["pixelrush_atlas_prod_v32776"]
    mundo.ModularBiomeScene = type("ModularBiomeScene", (), {})
    sys.modules["pixelrush_world_v3185"].ModularBiomeScene = mundo.ModularBiomeScene
    sys.modules["pixelrush_world_prod_v32777"].LivingWorld = type("LivingWorld", (), {})
    class Buffer:
        def __init__(self, raw, tamanho):
            self.raw=raw; self.size=tamanho; self.surface=None
    sys.modules["pixelrush_buffers_prod_v32779"]._Buffer=Buffer
    spec=importlib.util.spec_from_file_location("_qa_atlas_327723",RAIZ/"pixelrush_buffers_prod_v327710.py")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod._Manager._worker=lambda self: None
    m=mod._Manager()
    assert m._fraction == .56
    assert m._prepared_budget_bytes == 26*1048576
    tamanho=(256,256)
    dados=random.Random(327723).randbytes(tamanho[0]*tamanho[1]*4)
    entradas=[Buffer(zlib.compress(dados),tamanho) for _ in range(5)]
    estado={"biome":"neve","sprite":entradas[0]}
    m._quality=False
    m._ready["neve"]=(estado,entradas,0)
    class NoEvent:
        def set(self): pass
    m._event=NoEvent()
    # Simula ausencia de novas requisicoes pendentes, para testar somente preload.
    m._visited.update(("deserto","cidade_futurista"))
    for _ in range(10):
        m.update(False,"cidade")
    preparadas=[s for s in entradas if s.surface is not None]
    assert len(preparadas) == 3, len(preparadas)
    assert m._prepared_bytes == 3*256*256*4
    ref=pygame.image.frombytes(dados,tamanho,"RGBA").convert_alpha()
    for surface in preparadas:
        assert pygame.image.tobytes(surface.surface,"RGBA") == pygame.image.tobytes(ref,"RGBA")
    m._prepared_budget_bytes=m._prepared_bytes+1
    m.update(False,"cidade")
    assert len([s for s in entradas if s.surface is not None]) == 3
    cena=m.get("neve",False)
    assert cena is not None
    assert m._prepared_bytes == 0
    assert pygame.image.tobytes(cena.sprite,"RGBA")==pygame.image.tobytes(ref,"RGBA")
    print("OK: frac=56%, teto de RAM e ativacao byte a byte")

def main():
    pygame.init()
    pygame.display.set_mode((450,800))
    testar_qualidade()
    testar_atlas()
    pygame.quit()
if __name__=="__main__":
    main()
