"""Controlador de entradas Pixel Rush v3.171.0.

Dados de configuração e detecção de dedos independentes da lógica de jogo.
Funciona com Python 3.9+ e Pygame-ce; não realiza alocação por quadro.
"""
import pygame

MODO_CLASSICO = 'CLASSICO'
MODO_GESTOS = 'GESTOS'
MODO_BOTOES = 'BOTOES'
MODOS = (MODO_CLASSICO, MODO_GESTOS, MODO_BOTOES)
SENSIBILIDADES = (24, 30, 42)


def normalizar_modo(value):
    return value if value in MODOS else MODO_CLASSICO


def limiar(dados):
    try:
        value = int(dados.get('sensibilidade_toque', 30))
    except (TypeError, ValueError):
        value = 30
    return value if value in SENSIBILIDADES else 30


def botoes(dados):
    # Posição fixa na área dos polegares, fora dos controles de pausa / HUD.
    canhoto = bool(dados.get('controle_canhoto', False))
    # Ambos afastados do corredor (geralmente x≈70) e dos obstáculos centrais.
    pulo = pygame.Rect(132 if canhoto else 348, 616, 88, 76)
    baixo = pygame.Rect(232 if canhoto else 252, 616, 88, 76)
    return pulo, baixo


class DedosAtivos:
    """Mantém o dedo primário de gameplay, os auxiliares e evita toques duplicados."""
    def __init__(self):
        self.primary = None
        self.secondary = {}

    def reset(self):
        self.primary = None
        self.secondary.clear()

    def start(self, finger_id, pos, mode, jump_rect=None, down_rect=None, pause_rect=None):
        fid = int(finger_id)
        if fid == self.primary or fid in self.secondary:
            return 'duplicado'
        if pause_rect is not None and pause_rect.collidepoint(pos):
            self.secondary[fid] = 'pausa'
            return 'pausa'
        if mode == MODO_BOTOES:
            if jump_rect is not None and jump_rect.collidepoint(pos):
                self.secondary[fid] = 'pulo'
                return 'pulo'
            if down_rect is not None and down_rect.collidepoint(pos):
                self.secondary[fid] = 'baixo'
                return 'baixo'
            self.secondary[fid] = 'nada'
            return 'nada'
        if self.primary is None:
            self.primary = fid
            return 'primario'
        self.secondary[fid] = 'nada'
        return 'nada'

    def move(self, finger_id):
        return int(finger_id) == self.primary

    def end(self, finger_id):
        fid = int(finger_id)
        if fid == self.primary:
            self.primary = None
            return 'primario'
        return self.secondary.pop(fid, 'nada')

    def holding(self, action):
        return action in self.secondary.values()


_CACHE_BOTOES = {}


def desenhar_botoes(surface, dados, fonte, fase=0):
    if normalizar_modo(dados.get('controle_modo')) != MODO_BOTOES:
        return
    # Pré-computa os painéis translúcidos apenas uma vez por layout e fonte.
    canhoto = bool(dados.get('controle_canhoto', False))
    key = (canhoto, id(fonte))
    entries = _CACHE_BOTOES.get(key)
    if entries is None:
        rect_jump, rect_down = botoes(dados)
        entries = []
        for rect, texto, cor in ((rect_jump, 'PULAR', (97, 236, 223)),
                                 (rect_down, 'BAIXO', (239, 174, 104))):
            s = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(s, (20, 36, 61, 120), s.get_rect(), border_radius=18)
            pygame.draw.rect(s, (*cor, 200), s.get_rect().inflate(-2,-2), 2, border_radius=18)
            pygame.draw.line(s, (*cor, 65), (12, 11), (rect.w-12, 11), 1)
            txt = fonte.render(texto, True, (246, 250, 250))
            s.blit(txt,(rect.w//2-txt.get_width()//2,rect.h//2-txt.get_height()//2))
            entries.append((s,rect.topleft))
        _CACHE_BOTOES.clear()
        _CACHE_BOTOES[key] = entries
    for panel, pos in entries:
        surface.blit(panel,pos)

def desenhar_painel_controles(surface, dados, fonte, pequena, rects, frame=0):
    surface.fill((17, 29, 48))
    pygame.draw.rect(surface, (25, 43, 67), (32, 84, 386, 628), border_radius=18)
    pygame.draw.rect(surface, (92, 212, 232), (32, 84, 386, 628), 2, border_radius=18)
    en = dados.get('idioma') == 'en_US'
    title_text = 'CONTROL SETTINGS' if en else 'CONTROLES PRO'
    title = fonte.render(title_text, True, (245, 221, 141))
    surface.blit(title, (225 - title.get_width() // 2, 115))
    mode = normalizar_modo(dados.get('controle_modo'))
    options = (
        ('modo', 'Style' if en else 'Estilo',
         {'CLASSICO':('Classic' if en else 'Clássico'), 'GESTOS':('Gestures' if en else 'Gestos'),
          'BOTOES':('2 buttons' if en else '2 botões')}[mode]),
        ('sensibilidade', 'Sensitivity' if en else 'Sensibilidade', str(limiar(dados)) + ' px'),
        ('canhoto', 'Dominant hand' if en else 'Mão dominante',
         ('Left-handed' if en else 'Canhoto') if dados.get('controle_canhoto') else ('Right-handed' if en else 'Destro')),
        ('ajuda', 'Jump assistance' if en else 'Ajuda de pulo',
         ('On' if en else 'Ligada') if dados.get('ajuda_pulo', True) else ('Off' if en else 'Desligada')),
        ('gamepad', 'Gamepad' if en else 'Controle externo',
         ('On' if en else 'Ligado') if dados.get('gamepad_ativo', True) else ('Off' if en else 'Desligado')),
    )
    for key, name, value in options:
        rect = rects[key]
        pygame.draw.rect(surface, (38, 59, 82), rect, border_radius=10)
        pygame.draw.rect(surface, (86, 154, 185), rect, 1, border_radius=10)
        title = pequena.render(name, True, (171, 206, 224))
        val = pequena.render(value, True, (244, 248, 249))
        surface.blit(title, (rect.x + 13, rect.y + 9))
        surface.blit(val, (rect.right - 13 - val.get_width(), rect.y + 9))
    note = (('Tap: jump / drag: duck' if en else 'Toque: pular | Arrastar: agachar') if mode == MODO_CLASSICO else
            ('Swipe up/down' if en else 'Deslize para cima/baixo') if mode == MODO_GESTOS else
            ('Jump and duck with 2 thumbs' if en else 'Pule e agache com 2 polegares'))
    info = pequena.render(note, True, (170, 220, 211))
    surface.blit(info, (225 - info.get_width() // 2, 566))
    btn = rects['voltar']
    pygame.draw.rect(surface, (42, 143, 110), btn, border_radius=12)
    pygame.draw.rect(surface, (152, 239, 203), btn, 2, border_radius=12)
    txt = fonte.render('SAVE / BACK' if en else 'SALVAR / VOLTAR', True, (245, 249, 249))
    surface.blit(txt, (225 - txt.get_width() // 2, btn.centery - txt.get_height() // 2))
