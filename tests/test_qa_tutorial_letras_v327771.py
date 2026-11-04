import ast,os,random,unittest
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
from pixelrush_letras_v3218 import PalavraDaPartida,LetraColetavel
BASE=Path(__file__).resolve().parents[1]
ETAPAS=('pular','pular_longo','agachar','swipe_down','moedas','letras')
def classe_tutorial():
    path=BASE/'pixelrush_tutorial_corrida_v3274.py'
    cls=next(x for x in ast.parse(path.read_text('utf8')).body
             if isinstance(x,ast.ClassDef) and x.name=='TutorialCorrida')
    ns={'pygame':pygame,'random':random,'ETAPAS':ETAPAS,'LetraColetavel':LetraColetavel}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[cls],type_ignores=[])),str(path),'exec'),ns)
    return ns['TutorialCorrida']
class Jogador:
    rect=pygame.Rect(120,662,40,68)
    chao_y=730
    base_h=68
    no_chao=True
    def update(self,*a,**k):pass
class Fundo:
    def update(self,*a):pass
class Letras771(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):pygame.quit()
    def test_coleta_cinco_letras_e_continua_mesma_corrida(self):
        jogador=Jogador()
        palavra=PalavraDaPartida();palavra.iniciar()
        self.assertEqual(palavra.palavra,'PIXEL')
        t=classe_tutorial()(jogador);t.etapa_indice=5
        todos=pygame.sprite.Group();letras=pygame.sprite.Group()
        ganho=0;final=False
        for frame in range(1,320):
            g,final=t.atualizar(jogador,Fundo(),todos,letras,palavra,
                pygame.sprite.Group(),None,None,.7,frame)
            ganho+=g
            if frame%10==0 or final:
                palavra.desenhar_hud(pygame.Surface((450,800),pygame.SRCALPHA))
            if final:break
        self.assertTrue(final)
        self.assertEqual(palavra.progresso,5)
        self.assertTrue(palavra.concluida)
        self.assertEqual(t.contagem_coletas,5)
        self.assertEqual(ganho,50)
        self.assertFalse(t.ativo)
        self.assertTrue(t.corrida_continua)
    def test_roteiro_original_sem_mudancas(self):
        s=(BASE/'pixelrush_tutorial_corrida_v3274.py').read_text('utf8')
        self.assertIn('self.contagem_coletas+=1;ganho+=bonus',s)
        self.assertIn('self.corrida_continua=True',s)
if __name__=='__main__':unittest.main(verbosity=2)
