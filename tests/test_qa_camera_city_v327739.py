# -*- coding: utf-8 -*-
"""QA 3.277.39: equivalencia real da animacao 2.5D, camera e gate GLES."""
import math
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
import sys
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame


def rgba(s):
    return pygame.image.tobytes(s,"RGBA")


def trecho_original(scene,target,variant,flip,x,frame,night,climate,phase,map_kind="image",only_sprites=False):
    """Formula EXATA da _render_chunk anterior da cidade v3118."""
    from pixelrush_city2_v3115 import WIDTH,SCENE_W,SCENE_H,SCALE
    if not only_sprites:
        tex=scene._scaled_surface(variant,map_kind)
        r=pygame.Rect(max(0,-x),0,min(SCENE_W,WIDTH-x)-max(0,-x),SCENE_H)
        if r.w>0:target.blit(tex,(max(0,x),0),r)
    for sp in variant.sprites:
        asset=scene.lib.assets.get(sp.kind)
        if asset is None:continue
        tex=getattr(asset,map_kind)
        width=tex.get_width()
        wind=1.5 if climate in ("vento","tempestade","nevasca") else 1.
        dx=int(round(math.sin(frame*.025+sp.phase)*sp.sway*wind))
        px=x+sp.x*SCALE+dx
        if px>=WIDTH+2 or px+width<=-2:continue
        scene._draw_sprite(target,sp.kind,px,sp.y*SCALE,frame,night,climate,map_kind,False)


class TestQA739(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_cidade_camera_passe_exact_rgba(self):
        from pixelrush_city2_v3118 import CityPilotScene
        import pixelrush_city2_v3115 as constantes
        imagem=pygame.Surface((900,500),pygame.SRCALPHA)
        imagem.fill((0,0,0,0))
        for j in range(60):
            pygame.draw.rect(imagem,(j*3%255,j*9%255,j*15%255,j*13%255),
                             (j*13%850,j*17%440,40,35))
        asset=pygame.Surface((23,35),pygame.SRCALPHA)
        pygame.draw.circle(asset,(230,185,104,183),(11,17),11)
        assets={'sinal':SimpleNamespace(image=asset,normal=asset)}
        sprites=[SimpleNamespace(kind="sinal",x=(i*83)%920,y=20+i*11,
                 phase=i*.62,sway=2+i%5) for i in range(16)]
        sprites.append(SimpleNamespace(kind="ausente",x=30,y=44,phase=.1,sway=1))
        variant=SimpleNamespace(sprites=sprites)
        scene=CityPilotScene.__new__(CityPilotScene)
        scene.lib=SimpleNamespace(assets=assets)
        scene._scaled_surface=lambda variant,map_kind: imagem
        scene._draw_sprite=lambda target,kind,x,y,frame,night,climate,map_kind,flip: target.blit(asset,(x,y))
        for flags in (0,pygame.SRCALPHA):
            for frame in (0,1,91,92,377):
                for climate in ("limpo","vento","tempestade","nevasca","chuva"):
                    for kind in ("image","normal"):
                        original=pygame.Surface((450,800),flags)
                        original.fill((21,35,57,139) if flags else (21,35,57))
                        novo=original.copy()
                        for x in (-1150,-500,-65,15,410,900):
                            trecho_original(scene,original,variant,False,x,frame,.4,climate,.6,kind)
                            scene._render_chunk(novo,variant,False,x,frame,.4,climate,.6,kind)
                        self.assertEqual(rgba(original),rgba(novo),(flags,frame,climate,kind))
                        self.assertLessEqual(len(scene._qa_movimentos_cache),1)

    def test_camera_original_pixeis_formatos_zoom_foco(self):
        from pixelrush_cinema_v3172 import CameraCinematica
        for flags in (0,pygame.SRCALPHA):
            src=pygame.Surface((450,800),flags)
            for y in range(800):
                pygame.draw.line(src,(y*13%255,y*7%255,y*5%255,y*11%255)
                    if flags else (y*13%255,y*7%255,y*5%255),
                    (0,y),(449,y))
            for zoom in (.0,.001,.004,.016,.029):
                camera=CameraCinematica()
                camera.zoom=zoom
                camera.foco_y=-3.5
                jogador=SimpleNamespace(no_chao=False,rect=pygame.Rect(180,600,48,70))
                resultado=camera.aplicar(src,jogador,10.5,False,True)
                novo_zoom=zoom+(min(.025,max(0.,(10.5-8.)*.0018))-zoom)*.045
                foco=-3.5+(max(-10.,min(10.,(jogador.rect.centery-600)*.06))+3.5)*.065
                if novo_zoom<.002:
                    self.assertIs(resultado,src)
                else:
                    w,h=src.get_size()
                    ex=max(1,int(w*novo_zoom));ey=max(1,int(h*novo_zoom))
                    sx=ex;sy=max(0,min(2*ey,ey+int(foco)))
                    esperado=pygame.transform.smoothscale(src,(w+2*ex,h+2*ey))
                    self.assertEqual(rgba(resultado),
                                     rgba(esperado.subsurface((sx,sy,w,h))))

    def test_gles_pendente_sem_ativar(self):
        from pixelrush_qa_gles_exact_v327736 import gate_integracao,shaders
        for backend in ("GENERIC","SSE2","NEON"):
            for api in ("GLES2","GLES3"):
                vert,fragment=shaders(api,backend,(450,800))
                self.assertIn("void main",vert)
                self.assertIn("void main",fragment)
        claims=dict(igualdade_total=True,ganho_estavel_fps_android=True,
                    egl_android_aprovado=True,sem_regressoes_saves_fisica=True)
        self.assertFalse(gate_integracao(claims,False))
        for key in tuple(claims):
            testa=dict(claims);testa[key]=False
            self.assertFalse(gate_integracao(testa,True))
        import main
        self.assertFalse(hasattr(main,"GLES2DirectPresenterQA"))


if __name__=="__main__":
    unittest.main(verbosity=2)
