"""QA Android v3.277.21: paridade de pixels e reuso de buffers no zoom."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from types import SimpleNamespace
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pygame

def pixels(surface):
    return pygame.image.tobytes(surface, 'RGBA')

def main():
    pygame.init()
    pygame.display.set_mode((450, 800))
    from pixelrush_gamefeel_v3152 import GameFeel
    from pixelrush_cinema_v3172 import CameraCinematica
    source = pygame.Surface((450, 800)).convert()
    for x in range(0, 450, 5):
        pygame.draw.line(source, ((x*29)%256, (x*71)%256, (x*3)%256), (x,0), (x,799), 3)
    feel = GameFeel()
    for zoom in (0.005, 0.009, 0.018, 0.022, 0.009):
        feel.zoom = zoom
        w = max(1, int(450*(1-zoom)))
        h = max(1, int(800*(1-zoom)))
        expected = pygame.Surface((450, 800)).convert()
        expected.fill((13,20,40))
        old_frame = pygame.transform.scale(source, (w,h))
        expected.blit(old_frame, ((450-w)//2,(800-h)//2))
        result = feel.acabamento_camera(source, True)
        assert pixels(result) == pixels(expected), ('gamefeel pixels', zoom)
        frame = feel._cache_zoom_quadro
        feel.acabamento_camera(source, True)
        assert feel._cache_zoom_quadro is frame, ('gamefeel realloc', zoom)
    assert feel.acabamento_camera(source, False) is source
    camera = CameraCinematica()
    player = SimpleNamespace(no_chao=True, rect=pygame.Rect(100,570,80,80))
    for zoom in (0.004, 0.013, 0.025, 0.034, 0.025):
        camera.zoom = zoom
        camera.foco_y = 0.0
        result = camera.aplicar(source, player, velocidade=8, momento=True)
        ex = max(1, int(450*camera.zoom))
        ey = max(1, int(800*camera.zoom))
        expected = pygame.transform.smoothscale(source,(450+2*ex,800+2*ey))
        expected = expected.subsurface((ex,ey,450,800))
        assert pixels(result) == pixels(expected), ('camera pixels', zoom)
        frame = camera._cache_zoom_expandido
        camera.zoom = zoom
        camera.aplicar(source, player, velocidade=8, momento=True)
        assert camera._cache_zoom_expandido is frame, ('camera realloc', zoom)
    assert camera.aplicar(source, None) is source
    pygame.quit()
    print('OK: zoom 10 casos, pixels identicos e reuso dos buffers')

if __name__ == '__main__':
    main()
