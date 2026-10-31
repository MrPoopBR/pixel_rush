"""QA v3.277.22: superfícies RGBA, preparo de atlas e render de combo."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import importlib.util
import random
import sys
import types
import zlib
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pygame

def pixels(surface):
    return pygame.image.tobytes(surface, "RGBA")

def teste_conversao():
    rng = random.Random(327722)
    for size in ((450, 800), (450, 240), (1, 1), (180, 160)):
        raw = rng.randbytes(size[0] * size[1] * 4)
        anterior = pygame.image.frombytes(raw, size, "RGBA").convert_alpha()
        novo = pygame.image.frombuffer(raw, size, "RGBA").convert_alpha()
        assert anterior.get_masks() == novo.get_masks()
        assert pixels(anterior) == pixels(novo), ("rgba alterado", size)
    print("OK: 4 tamanhos RGBA equivalentes")

def teste_combo():
    from pixelrush_gamefeel_v3129 import GameFeel
    feel = GameFeel()
    real = feel._fonte_combo
    class FonteContada:
        def __init__(self):
            self.chamadas = 0
        def render(self, *args):
            self.chamadas += 1
            return real.render(*args)
    contador = FonteContada()
    feel._fonte_combo = contador
    jogador = SimpleNamespace(rect=pygame.Rect(150, 550, 60, 80))
    for combo in (3, 3, 4, 3, 1000, 999):
        esperado = pygame.Surface((450, 800)).convert()
        atual = esperado.copy()
        x = max(24, min(450 - 72, jogador.rect.right + 12))
        y = max(175, jogador.rect.top - 7)
        pygame.draw.circle(esperado, (30, 44, 65), (int(x + 17), int(y)), 17)
        pygame.draw.circle(esperado, (245, 206, 85), (int(x + 17), int(y)), 16, 2)
        t = real.render(str(min(999, combo)), True, (255, 240, 172))
        esperado.blit(t, (int(x + 17 - t.get_width() / 2), int(y - t.get_height() / 2)))
        esperado.blit(feel._vinheta, (0, 0))
        feel.desenhar(atual, jogador, combo, "cidade")
        assert pixels(esperado) == pixels(atual), ("combo pixels", combo)
    assert contador.chamadas == 3, contador.chamadas
    for combo in range(3, 80):
        feel.desenhar(pygame.Surface((450, 800)), jogador, combo, "cidade")
    assert len(feel._cache_rotulos_combo) <= 32
    print("OK: rotulos identicos, 3 renders para 6 quadros, cache <=32")

def teste_buffers():
    # Importa a implementacao REAL sem acionar o motor completo de producao.
    # Os modulos substitutos limitam-se a dependencias na borda do teste.
    for name in ("pixelrush_atlas_prod_v32776", "pixelrush_world_v3185",
                 "pixelrush_world_prod_v32777", "pixelrush_buffers_prod_v32779"):
        sys.modules[name] = types.ModuleType(name)
    atlas = sys.modules["pixelrush_atlas_prod_v32776"]
    atlas.ModularBiomeScene = type("ModularBiomeScene", (), {})
    sys.modules["pixelrush_world_v3185"].ModularBiomeScene = atlas.ModularBiomeScene
    sys.modules["pixelrush_world_prod_v32777"].LivingWorld = type("LivingWorld", (), {})
    class Buffer:
        def __init__(self, raw, size):
            self.raw, self.size, self.surface = raw, size, None
    sys.modules["pixelrush_buffers_prod_v32779"]._Buffer = Buffer
    path = Path(__file__).resolve().parents[2] / "pixelrush_buffers_prod_v327710.py"
    spec = importlib.util.spec_from_file_location("_qa_buffers_v327722", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module._Manager._worker = lambda self: None
    manager = module._Manager()
    class Evento:
        def __init__(self):
            self.sinais = 0
        def set(self):
            self.sinais += 1
    ev = Evento()
    manager._event = ev
    manager.update(False, "cidade")
    assert ev.sinais == 1
    assert len(manager._requested) == 3
    manager.update(False, "cidade")
    assert ev.sinais == 1, "acordou worker sem tarefas novas"
    size = (45, 80)
    raw = random.Random(7).randbytes(size[0] * size[1] * 4)
    buffer = Buffer(zlib.compress(raw), size)
    manager._ready["neve"] = ({"biome": "neve", "sprite": buffer}, [buffer], 100)
    manager.update(False, "cidade")
    assert buffer.raw is None and buffer.surface is not None
    anterior = pygame.image.frombytes(raw, size, "RGBA").convert_alpha()
    assert pixels(anterior) == pixels(buffer.surface)
    cena = manager.get("neve", False)
    assert cena is not None and cena.sprite is buffer.surface
    assert pixels(cena.sprite) == pixels(anterior)
    print("OK: carga incremental pixel-identica e worker acorda somente com pedidos")

def main():
    pygame.init()
    pygame.display.set_mode((450, 800))
    teste_conversao()
    teste_combo()
    teste_buffers()
    pygame.quit()

if __name__ == "__main__":
    main()
