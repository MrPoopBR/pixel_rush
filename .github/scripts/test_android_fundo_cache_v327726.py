"""QA pygame-ce: cache mobile desenha sprite/HUD novos a cada quadro."""
import os
import sys
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
pygame.init()
pygame.display.set_mode((450, 800))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from pixelrush_fundo_mobile_v327726 import CacheFundoMobile
cache=CacheFundoMobile()
display=pygame.Surface((450,800)).convert()
chave=('cidade','limpo',(100,120,140))
redesenhos=0
for frame in range(12):
    if not cache.reusar(display,chave,True):
        display.fill((14,31,46))
        redesenhos+=1
        cache.guardar(display,chave,True)
    pygame.draw.rect(display,(frame,220,88),(120,650,35,55))
    pygame.draw.rect(display,(210,frame,54),(12,22,90,30))
    assert display.get_at((5,5))[:3]==(14,31,46)
    assert display.get_at((122,655))[0]==frame
    assert display.get_at((15,26))[1]==frame
assert redesenhos==6 and cache.acertos==6
for chave in [('deserto','limpo',(100,120,140)),
              ('deserto','chuva',(100,120,140)),
              ('deserto','chuva',(90,110,120))]:
    assert not cache.reusar(display,chave,True)
    display.fill((42,51,63))
    cache.guardar(display,chave,True)
assert not cache.reusar(display,chave,False)
assert not cache.reusar(display,chave,True)
codigo=(Path(__file__).resolve().parents[2]/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text(encoding='utf8')
compile(codigo,'jogo','exec')
assert "E_ANDROID and estado == 'JOGANDO' and portal_tipo_ativo is None" in codigo
assert "not (tutorial_corrida and tutorial_corrida.ativo)" in codigo
assert 'MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15' in codigo
assert 'VERSAO = "v3.277.26-PROD-ANDROID-RC"' in codigo
for flag in ('PIXELRUSH_DEV_BUILD = False','LASERS_JETPACK_ATIVOS_PROD = False',
             'OBSTACULOS_QUE_AVANCAM_ATIVOS_PROD = False','API_ONLINE_ATIVA_PROD = False'):
    assert flag in codigo, flag
print('APROVADO: fundo 50% menos redesenhos; jogador/HUD 100%; flags OFF')
pygame.quit()
