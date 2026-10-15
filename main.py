import pygame
import random
import sys
import json
import os
import math
import array
from collections import OrderedDict
from pygame.sprite import Sprite

# --- SUPORTE A VIBRAÇÃO (ANDROID / PLYER) ---
try:
    from plyer import vibrator

    SUPORTE_VIBRADOR = True
except Exception:
    SUPORTE_VIBRADOR = False


def disparar_vibracao(duracao=0.2, vibracao_ligada=True):
    if not vibracao_ligada:
        return
    if SUPORTE_VIBRADOR:
        try:
            vibrator.vibrate(duracao)
        except Exception:
            pass


# --- INICIALIZAÇÃO E MIXER DE ÁUDIO BLINDADO PARA EMULADORES ---
pygame.init()


def init_audio():
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
    except Exception:
        try:
            pygame.mixer.init()
        except Exception:
            pass


init_audio()

# Versão do Jogo
VERSAO = "v3.4.0"

# Resolução lógica interna do jogo (Proporção Vertical 450x800)
LARGURA_VIRTUAL = 450
ALTURA_VIRTUAL = 800

# Detecção de plataforma (Android vs PC)
E_ANDROID = (sys.platform == 'android' or 'ANDROID_ARGUMENT' in os.environ)

# Inicialização de vídeo otimizada e blindada contra falhas de driver em emuladores
try:
    if E_ANDROID:
        tela = pygame.display.set_mode((LARGURA_VIRTUAL, ALTURA_VIRTUAL))
    else:
        info_tela = pygame.display.Info()
        LARGURA_TELA = info_tela.current_w
        ALTURA_TELA = info_tela.current_h
        if LARGURA_TELA <= 0 or ALTURA_TELA <= 0:
            LARGURA_TELA, ALTURA_TELA = 450, 800
        try:
            tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.FULLSCREEN)
        except Exception:
            tela = pygame.display.set_mode((LARGURA_VIRTUAL, ALTURA_VIRTUAL))
except Exception:
    tela = pygame.display.set_mode((450, 800))

# Atualiza dimensões reais garantidas
LARGURA_TELA, ALTURA_TELA = tela.get_size()
# Superficie logica no mesmo formato de pixels da tela: reduz conversoes em blits.
try:
    display_surface = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL)).convert()
except Exception:
    display_surface = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL))

# Superficies translúcidas pré-criadas. Criá-las por frame força a alocar/limpar
# 360 mil pixels em cada pausa, Game Over ou frame de câmera lenta.
OVERLAY_SLOW = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL)).convert()
OVERLAY_SLOW.fill((30, 180, 60))
OVERLAY_SLOW.set_alpha(45)
OVERLAY_PAUSA = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL)).convert()
OVERLAY_PAUSA.fill((0, 0, 0))
OVERLAY_PAUSA.set_alpha(185)
OVERLAY_GAMEOVER = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL)).convert()
OVERLAY_GAMEOVER.fill((20, 0, 0))
OVERLAY_GAMEOVER.set_alpha(200)

pygame.display.set_caption(f"Corrida Infinita 2D - {VERSAO}")
relogio = pygame.time.Clock()

# Cores
CINZA_CHAO = (90, 90, 90)
VERDE_GRAMA = (34, 139, 34)
VERMELHO_OBSTACULO = (210, 40, 40)
VERDE_CACTO = (46, 150, 70)
VERDE_CACTO_ESCURO = (25, 100, 45)
VERDE_CACTO_CLARO = (180, 230, 140)
ROXO_VOADOR = (160, 50, 240)
AMARELO_NEON = (255, 255, 0)
AMARELO_MOEDA = (255, 215, 0)
AZUL_IMA = (0, 191, 255)
LARANJA_TURBO = (255, 140, 0)
CIANO_ESCUDO = (0, 230, 230)
ROSA_MULT = (255, 20, 147)
VERDE_SLOW = (173, 255, 47)
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
CINZA_PAINEL = (30, 32, 45)
CINZA_BOTAO = (70, 70, 90)

COR_DIA = [135, 206, 235]
COR_NOITE = [18, 24, 50]

# --- EVENTOS DE CICLO DE VIDA DO ANDROID ---
APP_WILLENTERBACKGROUND = getattr(pygame, 'APP_WILLENTERBACKGROUND', None)
APP_DIDENTERBACKGROUND = getattr(pygame, 'APP_DIDENTERBACKGROUND', None)
APP_WILLENTERFOREGROUND = getattr(pygame, 'APP_WILLENTERFOREGROUND', None)
APP_DIDENTERFOREGROUND = getattr(pygame, 'APP_DIDENTERFOREGROUND', None)

# --- DICIONÁRIO DE IDIOMAS (i18n) ---
TEXTOS = {
    "en_US": {
        "titulo": "PIXEL RUSH",
        "jogar": "PLAY",
        "loja_skins": "SKIN SHOP",
        "loja_upgrades": "UPGRADES SHOP",
        "configuracoes": "SETTINGS",
        "recorde": "Highscore",
        "moedas_banco": "Total Coins",
        "missoes_partida": "MATCH MISSIONS:",
        "pausa_titulo": "GAME PAUSED",
        "estatisticas": "CURRENT STATS:",
        "distancia": "Distance Covered",
        "moedas_partida": "Coins this Match",
        "continuar": "RESUME",
        "menu_principal": "MAIN MENU",
        "gameover": "GAME OVER",
        "novo_recorde": "NEW HIGHSCORE!",
        "jogar_novamente": "PLAY AGAIN",
        "voltar_menu": "BACK TO MENU",
        "equipada": "EQUIPPED",
        "equipar": "EQUIP",
        "maximo": "MAX",
        "idioma": "Language",
        "vibracao": "Vibration",
        "ligado": "ON",
        "desligado": "OFF",
        "vol_musica": "Music Volume",
        "vol_sfx": "SFX Volume",
        "salvar": "SAVE & BACK",
        "alerta_laser": "LASER WARNING",
        "limpeza_total": "TOTAL CLEAR!",
        "escudo_ativo": "SHIELD!",
        "missao_completa": "MISSION COMPLETE!",
        "moedas_hud": "Coins",
        "metros": "Meters",
        "m_unit": "m",
        "missao_moedas": "Collect {} coins",
        "missao_distancia": "Run {}m in 1 run",
        "missao_quebrar": "Break {} cacti",
        "missao_pulos": "Make {} jumps",
        "missao_powerups": "Get {} power-ups",
        "missao_slow": "Use Slow Motion {} times",
        "skin_azul": "Ninja (Default)",
        "skin_verde": "Dinosaur",
        "skin_rosa": "Cute Bunny",
        "skin_dourado": "Flex Rapper",
        "up_ima": "Coin Magnet",
        "up_turbo": "Turbo Mode",
        "up_escudo": "Shield Barrier",
        "up_mult": "2x Multiplier",
        "up_slow": "Slow Motion"
    },
    "pt_BR": {
        "titulo": "PIXEL RUSH",
        "jogar": "JOGAR",
        "loja_skins": "LOJA DE SKINS",
        "loja_upgrades": "LOJA DE UPGRADES",
        "configuracoes": "CONFIGURAÇÕES",
        "recorde": "Recorde",
        "moedas_banco": "Moedas Banco",
        "missoes_partida": "MISSÕES DA PARTIDA:",
        "pausa_titulo": "JOGO PAUSADO",
        "estatisticas": "ESTATÍSTICAS ATUAIS:",
        "distancia": "Distância Percorrida",
        "moedas_partida": "Moedas nesta Partida",
        "continuar": "CONTINUAR",
        "menu_principal": "MENU PRINCIPAL",
        "gameover": "GAME OVER",
        "novo_recorde": "NOVO RECORDE!",
        "jogar_novamente": "JOGAR NOVAMENTE",
        "voltar_menu": "VOLTAR AO MENU",
        "equipada": "EQUIPADA",
        "equipar": "EQUIPAR",
        "maximo": "MÁXIMO",
        "idioma": "Idioma",
        "vibracao": "Vibração",
        "ligado": "LIGADO",
        "desligado": "DESLIGADO",
        "vol_musica": "Vol. Trilha",
        "vol_sfx": "Vol. Efeitos",
        "salvar": "SALVAR E VOLTAR",
        "alerta_laser": "ALERTA LASER",
        "limpeza_total": "LIMPEZA TOTAL!",
        "escudo_ativo": "ESCUDO!",
        "missao_completa": "MISSÃO COMPLETA!",
        "moedas_hud": "Moedas",
        "metros": "Metros",
        "m_unit": "m",
        "missao_moedas": "Colete {} moedas",
        "missao_distancia": "Corra {}m numa vida",
        "missao_quebrar": "Quebre {} cactos",
        "missao_pulos": "Faça {} pulos",
        "missao_powerups": "Coletar {} power-ups",
        "missao_slow": "Usar Câmera Lenta {}x",
        "skin_azul": "Ninja (Padrão)",
        "skin_verde": "Dinossauro",
        "skin_rosa": "Coelho Fofo",
        "skin_dourado": "Rapper Ostentação",
        "up_ima": "Ímã de Moedas",
        "up_turbo": "Modo Turbo",
        "up_escudo": "Escudo Protetor",
        "up_mult": "Multiplicador 2x",
        "up_slow": "Câmera Lenta"
    }
}


def t(chave, dados):
    lang = dados.get("idioma", "pt_BR")
    return TEXTOS.get(lang, TEXTOS["pt_BR"]).get(chave, chave)


# Skins com preços
SKINS = {
    "AZUL": {"cor": (30, 30, 30), "nome_key": "skin_azul", "preco": 0},
    "VERDE": {"cor": (46, 204, 113), "nome_key": "skin_verde", "preco": 3000},
    "ROSA": {"cor": (255, 182, 193), "nome_key": "skin_rosa", "preco": 6000},
    "DOURADO": {"cor": (255, 215, 0), "nome_key": "skin_dourado", "preco": 12000}
}

# Upgrades
UPGRADES_CONFIG = {
    "IMA": {"nome_key": "up_ima", "cor": AZUL_IMA, "duracao_base": 360, "bonus_por_nivel": 60, "max_nivel": 5,
            "preco_base": 1800, "preco_multiplicador": 1200},
    "TURBO": {"nome_key": "up_turbo", "cor": LARANJA_TURBO, "duracao_base": 300, "bonus_por_nivel": 60, "max_nivel": 5,
              "preco_base": 2400, "preco_multiplicador": 1800},
    "ESCUDO": {"nome_key": "up_escudo", "cor": CIANO_ESCUDO, "impactos_base": 1, "bonus_por_nivel": 1, "max_nivel": 4,
               "preco_base": 3600, "preco_multiplicador": 2400},
    "MULT_2X": {"nome_key": "up_mult", "cor": ROSA_MULT, "duracao_base": 300, "bonus_por_nivel": 60, "max_nivel": 5,
                "preco_base": 3000, "preco_multiplicador": 1800},
    "SLOW": {"nome_key": "up_slow", "cor": VERDE_SLOW, "duracao_base": 240, "bonus_por_nivel": 60, "max_nivel": 3,
             "preco_base": 4200, "preco_multiplicador": 3000}
}

# Fontes
# No Windows, mantemos Arial exatamente como antes.
# No Android, pygame.font.SysFont() tenta executar fc-list, o que pode falhar
# no ambiente Android/Buildozer. O Android 9 associa Arial à família sans-serif
# (Roboto); por isso carregamos diretamente o arquivo de peso correspondente.
def carregar_fonte(nome, tamanho, bold=False, italic=False):
    if E_ANDROID and nome.strip().lower() == "arial":
        if bold and italic:
            candidatos = ["/system/fonts/Roboto-BoldItalic.ttf"]
        elif bold:
            candidatos = ["/system/fonts/Roboto-Bold.ttf"]
        elif italic:
            candidatos = ["/system/fonts/Roboto-Italic.ttf"]
        else:
            candidatos = ["/system/fonts/Roboto-Regular.ttf"]

        for caminho_fonte in candidatos:
            if os.path.isfile(caminho_fonte):
                try:
                    return pygame.font.Font(caminho_fonte, tamanho)
                except Exception:
                    pass

        # Fallback para evitar que a inicialização falhe se o sistema não expuser
        # o arquivo Roboto esperado. Não usa SysFont aqui porque ele chama fc-list.
        fonte_fallback = pygame.font.Font(None, tamanho)
        if italic:
            fonte_fallback.set_italic(True)
        return fonte_fallback

    return pygame.font.SysFont(nome, tamanho, bold=bold, italic=italic)


fonte = carregar_fonte("Arial", 20, bold=True)
fonte_pequena = carregar_fonte("Arial", 13, bold=True)
fonte_missoes = carregar_fonte("Arial", 15, bold=True)
fonte_grande = carregar_fonte("Arial", 30, bold=True)
fonte_alerta = carregar_fonte("Arial", 24, bold=True)


# --- CACHE LIMITADO DE TEXTO (MUITO IMPORTANTE PARA ANDROID) ---
# Font.render() e alocacoes repetidas sao caras em varios builds do Pygame/SDL.
# Cacheamos a superficie pelo texto, fonte e cor; as superficies nunca sao alteradas.
_CACHE_TEXTOS = OrderedDict()
_LIMITE_CACHE_TEXTOS = 1536


def render_texto_cacheado(fonte_obj, texto, cor):
    texto = str(texto)
    cor = tuple(cor)
    chave = (id(fonte_obj), texto, cor)
    superficie = _CACHE_TEXTOS.get(chave)
    if superficie is not None:
        _CACHE_TEXTOS.move_to_end(chave)
        return superficie

    superficie = fonte_obj.render(texto, True, cor)
    _CACHE_TEXTOS[chave] = superficie
    if len(_CACHE_TEXTOS) > _LIMITE_CACHE_TEXTOS:
        _CACHE_TEXTOS.popitem(last=False)
    return superficie


# --- HELPER: DESENHAR TEXTO SOMBREADO CENTRALIZADO ---
def desenhar_texto_centralizado(surface, texto, fonte_obj, cor_texto, cor_sombra, y_pos):
    surf_sombra = render_texto_cacheado(fonte_obj, texto, cor_sombra)
    surf_texto = render_texto_cacheado(fonte_obj, texto, cor_texto)
    x_pos = (LARGURA_VIRTUAL - surf_texto.get_width()) // 2
    surface.blit(surf_sombra, (x_pos + 2, y_pos + 2))
    surface.blit(surf_texto, (x_pos, y_pos))


def desenhar_texto_com_sombra(superficie, texto, fonte_obj, cor_texto, cor_sombra, pos):
    surf_sombra = render_texto_cacheado(fonte_obj, texto, cor_sombra)
    surf_texto = render_texto_cacheado(fonte_obj, texto, cor_texto)
    superficie.blit(surf_sombra, (pos[0] + 2, pos[1] + 2))
    superficie.blit(surf_texto, pos)


# --- DESENHADOR DE TÍTULO EM PIXEL ART ESTILIZADO COM DEGRADÊ ---
TITULO_PIXEL_MAP = {
    'P': ["11110", "10001", "11110", "10000", "10000", "10000"],
    'I': ["11111", "00100", "00100", "00100", "00100", "11111"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001"],
    'E': ["11111", "10000", "11110", "10000", "10000", "11111"],
    'L': ["10000", "10000", "10000", "10000", "10000", "11111"],
    ' ': ["00", "00", "00", "00", "00", "00"],
    'R': ["11110", "10001", "11110", "10100", "10010", "10001"],
    'U': ["10001", "10001", "10001", "10001", "10001", "01110"],
    'S': ["01111", "10000", "11110", "00001", "00001", "11110"],
    'H': ["10001", "10001", "11111", "10001", "10001", "10001"]
}
_TITULO_PIXEL_BASE = None
_TITULO_PIXEL_METRICAS = None
_TITULO_PIXEL_FRAMES = None


def desenhar_titulo_pixel_art(surface, centro_x, pos_y, tempo_anim=0):
    global _TITULO_PIXEL_BASE, _TITULO_PIXEL_METRICAS, _TITULO_PIXEL_FRAMES
    texto = "PIXEL RUSH"
    tam_block = 6

    if _TITULO_PIXEL_BASE is None:
        total_cols = sum(len(TITULO_PIXEL_MAP[c][0]) + 1 for c in texto if c in TITULO_PIXEL_MAP) - 1
        largura_total = total_cols * tam_block
        tamanho = (largura_total + 16, tam_block * 6 + 12)
        base = pygame.Surface(tamanho, pygame.SRCALPHA)
        base.fill((0, 0, 0, 0))

        # A sombra e o contorno sao estaticos e sao rasterizados apenas uma vez.
        curr_x = 4
        for char in texto:
            if char in TITULO_PIXEL_MAP:
                matriz = TITULO_PIXEL_MAP[char]
                w_char = len(matriz[0])
                for r in range(6):
                    for c in range(w_char):
                        if matriz[r][c] == '1':
                            bx = curr_x + c * tam_block
                            by = 2 + r * tam_block
                            pygame.draw.rect(base, (15, 10, 25),
                                             (bx + 4, by + 5, tam_block + 2, tam_block + 2))
                curr_x += (w_char + 1) * tam_block

        curr_x = 4
        for char in texto:
            if char in TITULO_PIXEL_MAP:
                matriz = TITULO_PIXEL_MAP[char]
                w_char = len(matriz[0])
                for r in range(6):
                    for c in range(w_char):
                        if matriz[r][c] == '1':
                            bx = curr_x + c * tam_block
                            by = 2 + r * tam_block
                            pygame.draw.rect(base, PRETO, (bx - 2, by - 2, tam_block + 4, tam_block + 4))
                curr_x += (w_char + 1) * tam_block

        # Pre-renderiza os 125 estados do gradiente uma unica vez; em runtime e apenas um blit.
        quadros = []
        for frame_idx in range(125):
            quadro = pygame.Surface(tamanho, pygame.SRCALPHA)
            quadro.fill((0, 0, 0, 0))
            quadro.blit(base, (0, 0))
            curr_x = 4
            col_global = 0
            for char in texto:
                if char in TITULO_PIXEL_MAP:
                    matriz = TITULO_PIXEL_MAP[char]
                    w_char = len(matriz[0])
                    for r in range(6):
                        for c in range(w_char):
                            if matriz[r][c] == '1':
                                bx = curr_x + c * tam_block
                                by = 2 + r * tam_block
                                prog_col = (col_global + c) / float(total_cols)
                                prog_row = r / 6.0
                                ratio = (prog_col * 0.75 + prog_row * 0.25 + frame_idx * 0.008) % 1.0
                                if ratio < 0.33:
                                    f = ratio / 0.33
                                    cor = (int(255 * f), int(230 - 180 * f), int(255 - 60 * f))
                                elif ratio < 0.66:
                                    f = (ratio - 0.33) / 0.33
                                    cor = (255, int(50 + 170 * f), int(195 - 195 * f))
                                else:
                                    f = (ratio - 0.66) / 0.34
                                    cor = (255, int(220 - 80 * f), int(40 * f))
                                pygame.draw.rect(quadro, cor, (bx, by, tam_block, tam_block))
                                if r == 0 or (r > 0 and matriz[r - 1][c] == '0'):
                                    pygame.draw.rect(quadro, BRANCO, (bx, by, tam_block, 2))
                    curr_x += (w_char + 1) * tam_block
                    col_global += w_char + 1
            quadros.append(quadro)

        _TITULO_PIXEL_BASE = base
        _TITULO_PIXEL_METRICAS = (total_cols, largura_total)
        _TITULO_PIXEL_FRAMES = quadros

    _, largura_total = _TITULO_PIXEL_METRICAS
    start_x = int(centro_x - largura_total / 2)
    start_y = int(pos_y)
    pos = (start_x - 4, start_y - 2)
    if _TITULO_PIXEL_FRAMES:
        surface.blit(_TITULO_PIXEL_FRAMES[int(tempo_anim) % len(_TITULO_PIXEL_FRAMES)], pos)
    else:
        surface.blit(_TITULO_PIXEL_BASE, pos)


# --- SINTETIZADOR DE ÁUDIO EM TEMPO REAL BLINDADO ---
def criar_som_sintetico(frequencia_inicio, frequencia_fim, duracao, tipo="sine", volume=0.5):
    try:
        sample_rate = 22050
        num_samples = int(sample_rate * duracao)
        buf = array.array('h')
        for i in range(num_samples):
            t_sample = i / num_samples
            freq = frequencia_inicio + (frequencia_fim - frequencia_inicio) * t_sample
            time_sec = i / sample_rate

            if tipo == "sine":
                val = math.sin(2 * math.pi * freq * time_sec)
            elif tipo == "square":
                val = 0.8 if math.sin(2 * math.pi * freq * time_sec) >= 0 else -0.8
            elif tipo == "saw":
                val = 2.0 * (time_sec * freq - math.floor(0.5 + time_sec * freq))
            elif tipo == "noise":
                val = random.uniform(-0.8, 0.8)
            elif tipo == "soft_wind":
                val = 0.35 * random.uniform(-0.5, 0.5) + 0.65 * math.sin(2 * math.pi * freq * time_sec)
            else:
                val = math.sin(2 * math.pi * freq * time_sec)

            fade = 1.0 - t_sample
            sample = int(val * 32767 * volume * fade)
            sample = max(-32768, min(32767, sample))
            buf.append(sample)
            buf.append(sample)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None


def criar_som_arpejo(notas, duracao_nota=0.1, tipo="sine", volume=0.5):
    try:
        sample_rate = 22050
        buf = array.array('h')
        for freq in notas:
            num_samples = int(sample_rate * duracao_nota)
            for i in range(num_samples):
                t_sample = i / num_samples
                time_sec = i / sample_rate
                if tipo == "sine":
                    val = math.sin(2 * math.pi * freq * time_sec)
                elif tipo == "square":
                    val = 0.7 if math.sin(2 * math.pi * freq * time_sec) >= 0 else -0.7
                elif tipo == "saw":
                    val = 1.5 * (time_sec * freq - math.floor(0.5 + time_sec * freq))
                else:
                    val = math.sin(2 * math.pi * freq * time_sec)
                fade = 1.0 - (t_sample * 0.4)
                sample = int(val * 32767 * volume * fade)
                sample = max(-32768, min(32767, sample))
                buf.append(sample)
                buf.append(sample)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None


def gerar_trilha_sonora(grave=False):
    try:
        sample_rate = 22050
        duracao_total = 4.0
        num_samples = int(sample_rate * duracao_total)
        buf = array.array('h')

        fator = 0.5 if grave else 1.0
        notas_baixo = [130.81, 130.81, 146.83, 164.81, 110.00, 110.00, 123.47, 130.81]
        notas_melodia = [523.25, 587.33, 659.25, 783.99, 659.25, 587.33, 523.25, 440.00]

        for i in range(num_samples):
            t_sec = i / sample_rate
            beat_idx = int((t_sec / duracao_total) * 8) % 8
            t_in_beat = (t_sec % 0.5) / 0.5

            freq_b = notas_baixo[beat_idx] * fator
            freq_m = notas_melodia[beat_idx] * fator

            val_b = 0.25 * (1.0 if math.sin(2 * math.pi * freq_b * t_sec) >= 0 else -1.0)
            val_m = 0.2 * math.sin(2 * math.pi * freq_m * t_sec)
            val_k = 0.25 * math.sin(2 * math.pi * (100 * (1 - t_in_beat)) * t_sec) if t_in_beat < 0.1 else 0

            mix = (val_b + val_m + val_k) * (1.0 - t_in_beat * 0.25)
            sample = int(mix * 32767 * 0.35)
            sample = max(-32768, min(32767, sample))
            buf.append(sample)
            buf.append(sample)

        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None


class GerenciadorSons:
    def __init__(self):
        self.sons = {}
        self.canal_musica = None
        self.trilha_normal = None
        self.trilha_lenta = None
        self.musica_tocando = None
        self.carregar_sons()

    def carregar_sons(self):
        try:
            if pygame.mixer.get_init():
                self.canal_musica = pygame.mixer.Channel(0)
            self.sons["pulo"] = criar_som_sintetico(180, 450, 0.14, "sine", 0.4)
            self.sons["swipe"] = criar_som_sintetico(260, 90, 0.12, "soft_wind", 0.25)
            self.sons["swipe_down"] = criar_som_sintetico(260, 90, 0.12, "soft_wind", 0.25)
            self.sons["moeda"] = criar_som_sintetico(980, 1320, 0.08, "sine", 0.3)
            self.sons["powerup"] = criar_som_sintetico(320, 750, 0.18, "square", 0.35)
            self.sons["quebrar"] = criar_som_sintetico(220, 60, 0.16, "noise", 0.5)
            self.sons["turbo"] = criar_som_sintetico(150, 320, 0.22, "saw", 0.35)
            self.sons["ima"] = criar_som_sintetico(480, 520, 0.15, "sine", 0.3)

            self.sons["gameover"] = criar_som_arpejo([300, 240, 180, 120], 0.15, "saw", 0.45)
            self.sons["novo_recorde"] = criar_som_arpejo([523, 659, 784, 1046], 0.12, "sine", 0.5)
            self.sons["missao"] = criar_som_arpejo([659, 880], 0.1, "sine", 0.5)
            self.sons["clique"] = criar_som_sintetico(900, 1100, 0.04, "sine", 0.35)
            self.sons["alerta_laser"] = criar_som_arpejo([1000, 1200, 1000, 1200], 0.06, "square", 0.35)
            self.sons["contagem_laser"] = criar_som_sintetico(880, 880, 0.05, "sine", 0.4)
            self.sons["contagem_laser_high"] = criar_som_sintetico(1200, 1200, 0.06, "square", 0.45)
            self.sons["disparo_laser"] = criar_som_sintetico(1600, 200, 0.22, "saw", 0.45)
            self.sons["eletricidade"] = criar_som_sintetico(700, 900, 0.1, "square", 0.2)
            self.sons["chamas"] = criar_som_sintetico(180, 320, 0.12, "noise", 0.3)

            self.sons["pulo_slow"] = criar_som_sintetico(90, 225, 0.22, "sine", 0.4)
            self.sons["swipe_slow"] = criar_som_sintetico(130, 45, 0.18, "soft_wind", 0.25)
            self.sons["swipe_down_slow"] = criar_som_sintetico(130, 45, 0.18, "soft_wind", 0.25)
            self.sons["moeda_slow"] = criar_som_sintetico(490, 660, 0.14, "sine", 0.3)
            self.sons["powerup_slow"] = criar_som_sintetico(160, 375, 0.28, "square", 0.35)
            self.sons["quebrar_slow"] = criar_som_sintetico(110, 30, 0.25, "noise", 0.5)

            self.trilha_normal = gerar_trilha_sonora(grave=False)
            self.trilha_lenta = gerar_trilha_sonora(grave=True)
        except Exception:
            pass

    def tocar_som(self, nome, e_slow=False, vol_sfx=1.0):
        if vol_sfx <= 0: return
        key = f"{nome}_slow" if (e_slow and f"{nome}_slow" in self.sons) else nome
        s = self.sons.get(key) or self.sons.get(nome)
        if s:
            try:
                s.set_volume(vol_sfx)
                s.play()
            except Exception:
                pass

    def atualizar_musica(self, estado, e_slow, vol_musica):
        if not self.canal_musica: return
        try:
            self.canal_musica.set_volume(vol_musica)
            if estado in ["JOGANDO", "PAUSA"]:
                trilha_alvo = self.trilha_lenta if e_slow else self.trilha_normal
                if self.musica_tocando != trilha_alvo:
                    if trilha_alvo:
                        self.canal_musica.play(trilha_alvo, loops=-1)
                    self.musica_tocando = trilha_alvo
            elif estado in ["INICIO", "CONFIG", "LOJA", "UPGRADES"]:
                if self.musica_tocando != self.trilha_normal:
                    if self.trilha_normal:
                        self.canal_musica.play(self.trilha_normal, loops=-1)
                    self.musica_tocando = self.trilha_normal
            else:
                if self.musica_tocando is not None:
                    self.canal_musica.stop()
                    self.musica_tocando = None
        except Exception:
            pass


# --- SISTEMA DE SALVAMENTO ---
ARQUIVO_SAVE = "savegame.json"


def carregar_dados():
    dados_padrao = {
        "recorde": 0, "moedas_totais": 0, "skin_equipada": "AZUL", "skins_desbloqueadas": ["AZUL"],
        "upgrades": {"IMA": 0, "TURBO": 0, "ESCUDO": 0, "MULT_2X": 0, "SLOW": 0},
        "vol_sfx": 0.7, "vol_musica": 0.5, "idioma": "pt_BR", "vibracao": True
    }
    if os.path.exists(ARQUIVO_SAVE):
        try:
            with open(ARQUIVO_SAVE, "r") as f:
                dados = json.load(f)
                for k, v in dados_padrao.items():
                    if k not in dados: dados[k] = v
                for key_up in dados_padrao["upgrades"]:
                    if key_up not in dados["upgrades"]:
                        dados["upgrades"][key_up] = 0
                return dados
        except Exception:
            return dados_padrao
    return dados_padrao


def salvar_dados(dados):
    try:
        with open(ARQUIVO_SAVE, "w") as f:
            json.dump(dados, f, indent=4)
    except Exception:
        pass


# --- DESENHADOR DE ÍCONES DE POWER-UPS ---
def desenhar_icone_powerup(surface, tipo, x, y):
    if tipo == "IMA":
        rect_u = pygame.Rect(x - 8, y - 8, 16, 16)
        pygame.draw.arc(surface, BRANCO, rect_u, math.pi, 2 * math.pi, 3)
        pygame.draw.line(surface, BRANCO, (x - 8, y), (x - 8, y - 6), 3)
        pygame.draw.line(surface, BRANCO, (x + 8, y), (x + 8, y - 6), 3)
        pygame.draw.line(surface, VERMELHO_OBSTACULO, (x - 8, y - 6), (x - 8, y - 8), 3)
        pygame.draw.line(surface, VERMELHO_OBSTACULO, (x + 8, y - 6), (x + 8, y - 8), 3)
    elif tipo == "TURBO":
        pts = [(x + 2, y - 9), (x - 6, y + 1), (x - 1, y + 1), (x - 3, y + 9), (x + 6, y - 1), (x + 1, y - 1)]
        pygame.draw.polygon(surface, BRANCO, pts)
    elif tipo == "ESCUDO":
        pts = [(x, y - 9), (x + 8, y - 5), (x + 6, y + 3), (x, y + 9), (x - 6, y + 3), (x - 8, y - 5)]
        pygame.draw.polygon(surface, BRANCO, pts, 2)
    elif tipo == "SLOW":
        pygame.draw.circle(surface, BRANCO, (x, y), 9, 2)
        pygame.draw.line(surface, BRANCO, (x, y), (x, y - 5), 2)
        pygame.draw.line(surface, BRANCO, (x, y), (x + 4, y), 2)
    elif tipo == "MULT_2X":
        txt = render_texto_cacheado(fonte_pequena, "2X", BRANCO)
        surface.blit(txt, (x - txt.get_width() // 2, y - txt.get_height() // 2))


# --- DESENHADOR DE PREVIEWS DE SKINS ---
_CACHE_MINI_SKINS = {}

def desenhar_mini_skin(surface, skin_nome, cx, cy):
    mini_surf = _CACHE_MINI_SKINS.get(skin_nome)
    if mini_surf is not None:
        surface.blit(mini_surf, (cx - 20, cy - 20))
        return

    cor_base = SKINS.get(skin_nome, SKINS["AZUL"])["cor"]
    mini_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    CORPO_RECT = (11, 7, 18, 25)

    if skin_nome == "AZUL":
        pygame.draw.line(mini_surf, PRETO, (16, 33), (16, 38), 6)
        pygame.draw.line(mini_surf, (15, 15, 15), (16, 33), (16, 38), 4)
        pygame.draw.line(mini_surf, PRETO, (24, 33), (24, 38), 6)
        pygame.draw.line(mini_surf, (15, 15, 15), (24, 33), (24, 38), 4)
        pygame.draw.rect(mini_surf, PRETO, (9, 5, 22, 29), border_radius=6)
        pygame.draw.rect(mini_surf, cor_base, CORPO_RECT, border_radius=5)
        pygame.draw.rect(mini_surf, (200, 20, 20), (11, 11, 18, 4), border_radius=2)
        pygame.draw.rect(mini_surf, BRANCO, (14, 12, 4, 2), border_radius=1)
        pygame.draw.rect(mini_surf, BRANCO, (22, 12, 4, 2), border_radius=1)
    elif skin_nome == "ROSA":
        pygame.draw.rect(mini_surf, PRETO, (13, -1, 6, 10), border_radius=3)
        pygame.draw.rect(mini_surf, BRANCO, (14, 0, 4, 8), border_radius=2)
        pygame.draw.rect(mini_surf, PRETO, (21, -1, 6, 10), border_radius=3)
        pygame.draw.rect(mini_surf, BRANCO, (22, 0, 4, 8), border_radius=2)
        pygame.draw.line(mini_surf, PRETO, (16, 33), (16, 38), 6)
        pygame.draw.line(mini_surf, cor_base, (16, 33), (16, 38), 4)
        pygame.draw.line(mini_surf, PRETO, (24, 33), (24, 38), 6)
        pygame.draw.line(mini_surf, cor_base, (24, 33), (24, 38), 4)
        pygame.draw.rect(mini_surf, PRETO, (9, 5, 22, 29), border_radius=6)
        pygame.draw.rect(mini_surf, cor_base, CORPO_RECT, border_radius=5)
        pygame.draw.ellipse(mini_surf, BRANCO, (14, 19, 12, 12))
        pygame.draw.rect(mini_surf, PRETO, (15, 14, 3, 4), border_radius=1)
        pygame.draw.rect(mini_surf, PRETO, (22, 14, 3, 4), border_radius=1)
    elif skin_nome == "VERDE":
        pygame.draw.polygon(mini_surf, PRETO, [(11, 21), (-1, 30), (11, 33)])
        pygame.draw.polygon(mini_surf, cor_base, [(11, 23), (1, 30), (11, 31)])
        pygame.draw.line(mini_surf, PRETO, (16, 33), (16, 38), 6)
        pygame.draw.line(mini_surf, cor_base, (16, 33), (16, 38), 4)
        pygame.draw.line(mini_surf, PRETO, (24, 33), (24, 38), 6)
        pygame.draw.line(mini_surf, cor_base, (24, 33), (24, 38), 4)
        pygame.draw.rect(mini_surf, PRETO, (9, 5, 22, 29), border_radius=6)
        pygame.draw.rect(mini_surf, cor_base, CORPO_RECT, border_radius=5)
        pygame.draw.rect(mini_surf, (241, 196, 15), (20, 17, 9, 15), border_radius=3)
        pygame.draw.rect(mini_surf, PRETO, (23, 10, 3, 3), border_radius=1)
    elif skin_nome == "DOURADO":
        pygame.draw.line(mini_surf, PRETO, (16, 33), (16, 38), 6)
        pygame.draw.line(mini_surf, cor_base, (16, 33), (16, 38), 4)
        pygame.draw.line(mini_surf, PRETO, (24, 33), (24, 38), 6)
        pygame.draw.line(mini_surf, cor_base, (24, 33), (24, 38), 4)
        pygame.draw.rect(mini_surf, PRETO, (9, 5, 22, 29), border_radius=6)
        pygame.draw.rect(mini_surf, cor_base, CORPO_RECT, border_radius=5)
        pygame.draw.rect(mini_surf, (20, 20, 20), (11, 5, 18, 6), border_radius=2)
        pygame.draw.rect(mini_surf, PRETO, (16, 12, 14, 7), border_radius=2)
        pygame.draw.rect(mini_surf, (255, 215, 0), (15, 11, 16, 9), 1, border_radius=2)

    _CACHE_MINI_SKINS[skin_nome] = mini_surf
    surface.blit(mini_surf, (cx - 20, cy - 20))


CHAVE_TRANSPARENCIA_SPRITES = (255, 0, 255)

# --- SISTEMA DE OBJECT POOLING ---
class Particula(Sprite):
    """Particula reaproveitavel; alpha global evita preencher RGBA a cada frame."""
    def __init__(self, x=0, y=0, cor=(255, 255, 255), vx=None, vy=None, vida=25, tamanho=5):
        super().__init__()
        self.pool_manager = None
        self._pool_livre = False
        self._imagens_por_tamanho = {}
        self.image = None
        self.reset(x, y, cor, vx, vy, vida, tamanho)

    def kill(self):
        super().kill()
        manager = self.pool_manager
        if manager is not None and not self._pool_livre:
            self.ativo = False
            self._pool_livre = True
            manager.particulas_disponiveis.append(self)

    def reset(self, x, y, cor, vx=None, vy=None, vida=25, tamanho=5):
        self.cor = tuple(cor[:3])
        self.vida_max = max(1, int(vida))
        self.vida = int(vida)
        self.tamanho = int(tamanho)
        self.vx = vx if vx is not None else random.uniform(-4, 4)
        self.vy = vy if vy is not None else random.uniform(-4, 4)

        chave = (self.tamanho, self.tamanho)
        imagem = self._imagens_por_tamanho.get(chave)
        if imagem is None:
            try:
                imagem = pygame.Surface(chave).convert()
            except Exception:
                imagem = pygame.Surface(chave)
            self._imagens_por_tamanho[chave] = imagem
        imagem.fill(self.cor)
        imagem.set_alpha(255)
        self.image = imagem
        self.rect = self.image.get_rect(center=(x, y))
        self.ativo = True

    def update(self, *args):
        if not self.ativo:
            return
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vida -= 1
        if self.vida <= 0:
            self.ativo = False
            self.kill()
        else:
            self.image.set_alpha(max(0, min(255, int((self.vida / self.vida_max) * 255))))


class Moeda(Sprite):
    # Todas as moedas usam a mesma imagem imutavel; cada uma mantem seu proprio rect.
    _imagem_compartilhada = None

    def __init__(self, x_pos=0, y_pos=0):
        super().__init__()
        self.pool_manager = None
        self._pool_livre = False
        if Moeda._imagem_compartilhada is None:
            imagem = pygame.Surface((22, 22)).convert()
            imagem.fill(CHAVE_TRANSPARENCIA_SPRITES)
            pygame.draw.circle(imagem, AMARELO_MOEDA, (11, 11), 11)
            pygame.draw.circle(imagem, PRETO, (11, 11), 11, 2)
            imagem.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
            Moeda._imagem_compartilhada = imagem
        self.image = Moeda._imagem_compartilhada
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.ativo = True

    def kill(self):
        super().kill()
        manager = self.pool_manager
        if manager is not None and not self._pool_livre:
            self.ativo = False
            self._pool_livre = True
            manager.moedas_disponiveis.append(self)

    def reset(self, x_pos, y_pos):
        self.rect.center = (x_pos, y_pos)
        self.ativo = True

    def update(self, velocidade_jogo, jogador=None):
        if not self.ativo:
            return
        if jogador and jogador.tempo_ima > 0 and not jogador.morrendo:
            dx = jogador.rect.centerx - self.rect.centerx
            dy = jogador.rect.centery - self.rect.centery
            distancia_quadrada = dx * dx + dy * dy
            if 0 < distancia_quadrada < (220 * 220):
                distancia = math.sqrt(distancia_quadrada)
                self.rect.x += int((dx / distancia) * 12)
                self.rect.y += int((dy / distancia) * 12)
        self.rect.x -= velocidade_jogo
        if self.rect.x < -50:
            self.ativo = False
            self.kill()


class PoolManager:
    def __init__(self):
        self.particulas_pool = [Particula() for _ in range(250)]
        self.particulas_disponiveis = list(self.particulas_pool)
        for p in self.particulas_pool:
            p.pool_manager = self
            p.ativo = False
            p._pool_livre = True

        self.moedas_pool = [Moeda() for _ in range(120)]
        self.moedas_disponiveis = list(self.moedas_pool)
        for m in self.moedas_pool:
            m.pool_manager = self
            m.ativo = False
            m._pool_livre = True

    def obter_particula(self, x, y, cor, vx=None, vy=None, vida=25, tamanho=5):
        if self.particulas_disponiveis:
            p = self.particulas_disponiveis.pop()
            p._pool_livre = False
            p.reset(x, y, cor, vx, vy, vida, tamanho)
        else:
            p = Particula(x, y, cor, vx, vy, vida, tamanho)
            p.pool_manager = self
            p._pool_livre = False
            self.particulas_pool.append(p)
        return p

    def obter_moeda(self, x_pos, y_pos):
        if self.moedas_disponiveis:
            m = self.moedas_disponiveis.pop()
            m._pool_livre = False
            m.reset(x_pos, y_pos)
        else:
            m = Moeda(x_pos, y_pos)
            m.pool_manager = self
            m._pool_livre = False
            self.moedas_pool.append(m)
        return m


def criar_explosao_particulas(x, y, cor, quantidade, grupo_sprites, pool_manager):
    for _ in range(quantidade):
        p = pool_manager.obter_particula(x, y, cor, random.uniform(-6, 6), random.uniform(-7, 4),
                                         vida=random.randint(20, 40), tamanho=random.randint(4, 8))
        grupo_sprites.add(p)


def criar_rastro_turbo(x, y, grupo_sprites, pool_manager):
    p = pool_manager.obter_particula(x, y, LARANJA_TURBO, random.uniform(-6, -2), random.uniform(-1.5, 1.5), vida=15,
                                     tamanho=random.randint(5, 8))
    grupo_sprites.add(p)


# --- TEXTOS FLUTUANTES COM ANIMAÇÃO SUAVE ---
class TextoFlutuante(Sprite):
    def __init__(self, x, y, texto, cor, tamanho="normal"):
        super().__init__()
        fnt = fonte_grande if tamanho == "grande" else fonte
        texto = str(texto)
        surf_sombra = fnt.render(texto, True, (0, 0, 0))
        surf_texto = fnt.render(texto, True, cor)
        # Rasteriza uma vez; a animacao so altera alpha global e posicao.
        self.image = pygame.Surface(surf_texto.get_size(), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.image.blit(surf_sombra, (2, 2))
        self.image.blit(surf_texto, (0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.vida_max = 50
        self.vida = self.vida_max
        self.vy = -1.8

    def update(self, *args):
        self.rect.y += self.vy
        self.vida -= 1
        if self.vida <= 0:
            self.kill()
        else:
            self.image.set_alpha(max(0, min(255, int((self.vida / float(self.vida_max)) * 255))))


# --- PARALLAX BACKGROUND ---
class ParallaxBackground:
    """Fundo com camadas repetiveis em tiles e sem blits RGBA grandes por frame."""
    CHAVE_TRANSPARENCIA = (255, 0, 255)  # cor-chave, nao usada na arte do jogo
    Y_MONTANHAS = 480
    H_MONTANHAS = ALTURA_VIRTUAL - Y_MONTANHAS
    Y_PREDIOS = 550
    H_PREDIOS = ALTURA_VIRTUAL - Y_PREDIOS

    def __init__(self):
        self.camada_longe = 0.0
        self.camada_perto = 0.0
        self.tempo_animacao = 0
        self.nuvens = [
            {"x": random.randint(0, LARGURA_VIRTUAL), "y": random.randint(20, 200),
             "vel": random.uniform(0.15, 0.45), "tam": random.randint(20, 45)}
            for _ in range(6)
        ]
        self.estrelas = [
            {"x": random.randint(0, LARGURA_VIRTUAL), "y": random.randint(0, 350),
             "blink": random.uniform(0.02, 0.08), "offset": random.uniform(0, math.pi * 2)}
            for _ in range(40)
        ]
        self.predios = ((20, 600, 60, 200), (120, 650, 40, 150),
                        (200, 550, 80, 250), (320, 620, 70, 180))
        self.janelas_por_predio = {}
        for bx, by, bw, bh in self.predios:
            janelas = []
            for wy in range(by + 10, ALTURA_VIRTUAL - 15, 25):
                for wx_local in range(10, bw - 10, 15):
                    if ((bx + wy + wx_local) % 7) < 4:
                        janelas.append((wx_local, wy))
            self.janelas_por_predio[(bx, by, bw, bh)] = janelas

        self._cache_montanhas_key = None
        self._cache_montanhas = None
        self._cache_predios_key = None
        self._cache_predios = None

    def update(self, velocidade_jogo=1.0):
        self.tempo_animacao += 1
        self.camada_longe -= velocidade_jogo * 0.1
        if self.camada_longe <= -LARGURA_VIRTUAL:
            self.camada_longe += LARGURA_VIRTUAL
        self.camada_perto -= velocidade_jogo * 0.3
        if self.camada_perto <= -LARGURA_VIRTUAL:
            self.camada_perto += LARGURA_VIRTUAL
        for nuvem in self.nuvens:
            nuvem["x"] -= nuvem["vel"] + (velocidade_jogo * 0.05)
            if nuvem["x"] < -80:
                nuvem["x"] = LARGURA_VIRTUAL + 40
                nuvem["y"] = random.randint(20, 200)

    def _obter_tile_montanhas(self, cor_ceu):
        cor_montanha = (max(30, cor_ceu[0] // 2 - 10),
                        max(40, cor_ceu[1] // 2), max(60, cor_ceu[2] // 2 + 10))
        if self._cache_montanhas is not None and self._cache_montanhas_key == cor_montanha:
            return self._cache_montanhas

        tile = pygame.Surface((LARGURA_VIRTUAL * 2, self.H_MONTANHAS)).convert()
        chave = self.CHAVE_TRANSPARENCIA
        tile.fill(chave)
        y_base_local = ALTURA_VIRTUAL - self.Y_MONTANHAS
        for i in range(2):
            x_base = i * LARGURA_VIRTUAL
            for x_offset, w, h in ((-50, 200, 300), (100, 240, 240), (280, 220, 320)):
                x = x_base + x_offset
                top_y = ALTURA_VIRTUAL - h
                pts_montanha = [(x, y_base_local), (x + w // 2, top_y - self.Y_MONTANHAS),
                                (x + w, y_base_local)]
                pygame.draw.polygon(tile, cor_montanha, pts_montanha)
                sn_h = h * 0.25
                py = top_y - self.Y_MONTANHAS
                px = x + w // 2
                lx = px - int((w // 2) * (sn_h / h))
                rx = px + int((w // 2) * (sn_h / h))
                pts_neve = [(px, py), (lx, py + sn_h), (px - 10, py + sn_h + 10),
                            (px + 10, py + sn_h + 5), (rx, py + sn_h)]
                pygame.draw.polygon(tile, BRANCO, pts_neve)
        tile.set_colorkey(chave)
        self._cache_montanhas = tile
        self._cache_montanhas_key = cor_montanha
        return tile

    def _obter_tile_predios(self, cor_ceu, e_noite):
        cor_perto = (max(20, cor_ceu[0] // 3), max(20, cor_ceu[1] // 3), max(30, cor_ceu[2] // 3))
        luz_cor = (255, 255, 120) if e_noite else (160, 200, 240)
        chave_cache = (cor_perto, luz_cor)
        if self._cache_predios is not None and self._cache_predios_key == chave_cache:
            return self._cache_predios

        tile = pygame.Surface((LARGURA_VIRTUAL * 2, self.H_PREDIOS)).convert()
        chave = self.CHAVE_TRANSPARENCIA
        tile.fill(chave)
        for i in range(2):
            x_base = i * LARGURA_VIRTUAL
            for bx, by, bw, bh in self.predios:
                real_x = x_base + bx
                y_local = by - self.Y_PREDIOS
                pygame.draw.rect(tile, cor_perto, (real_x, y_local, bw, bh))
                for wx_local, wy in self.janelas_por_predio[(bx, by, bw, bh)]:
                    pygame.draw.rect(tile, luz_cor,
                                     (real_x + wx_local, wy - self.Y_PREDIOS, 8, 12))
        tile.set_colorkey(chave)
        self._cache_predios = tile
        self._cache_predios_key = chave_cache
        return tile

    def draw(self, superficie, cor_ceu, e_noite):
        superficie.fill(cor_ceu)
        intensidade_noite = max(0, 255 - cor_ceu[0] * 2)
        if intensidade_noite > 0:
            for est in self.estrelas:
                alpha = int(100 + 100 * math.sin(self.tempo_animacao * est["blink"] + est["offset"]))
                alpha = min(255, max(0, alpha)) * (intensidade_noite / 255.0)
                if alpha > 10:
                    pygame.draw.circle(superficie, (255, 255, 255, int(alpha)),
                                       (int(est["x"]), int(est["y"])), 1)
                    if alpha > 150:
                        pygame.draw.circle(superficie, (255, 255, 255, int(alpha // 2)),
                                           (int(est["x"]), int(est["y"])), 2)

        if cor_ceu[0] > 60:
            for nuvem in self.nuvens:
                x, y, t = int(nuvem["x"]), int(nuvem["y"]), nuvem["tam"]
                cor_nuvem = (min(255, cor_ceu[0] + 100), min(255, cor_ceu[1] + 100),
                             min(255, cor_ceu[2] + 100))
                pygame.draw.circle(superficie, cor_nuvem, (x, y), t)
                pygame.draw.circle(superficie, cor_nuvem, (int(x + t // 1.2), int(y + t // 3)), int(t // 1.2))
                pygame.draw.circle(superficie, cor_nuvem, (int(x - t // 1.2), int(y + t // 3)), int(t // 1.2))

        # As montanhas comecam abaixo da area das nuvens/estrelas. Tiles com color-key
        # evitam o custo de alpha blending de superficies transparentes grandes.
        tile_montanhas = self._obter_tile_montanhas(cor_ceu)
        offset_longe = int(-self.camada_longe) % LARGURA_VIRTUAL
        superficie.blit(tile_montanhas, (0, self.Y_MONTANHAS),
                        (offset_longe, 0, LARGURA_VIRTUAL, self.H_MONTANHAS))

        tile_predios = self._obter_tile_predios(cor_ceu, e_noite)
        offset_perto = int(-self.camada_perto) % LARGURA_VIRTUAL
        superficie.blit(tile_predios, (0, self.Y_PREDIOS),
                        (offset_perto, 0, LARGURA_VIRTUAL, self.H_PREDIOS))


# --- JOGADOR ---
class Jogador(Sprite):
    def __init__(self, skin_nome, cor_base, upgrades):
        super().__init__()
        self.skin_nome = skin_nome
        self.cor_base = cor_base
        self.upgrades = upgrades

        self.base_w, self.base_h = 80, 80
        self.w_atual, self.h_atual = self.base_w, self.base_h

        self.image_original = pygame.Surface((self.base_w, self.base_h), pygame.SRCALPHA)
        self.image = self.image_original.copy()
        self._scaled_image_cache = {}
        self._visual_cor_atual = cor_base
        self._visual_dirty = True

        self.rect = self.image.get_rect()
        self.rect.x = 40
        self.chao_y = ALTURA_VIRTUAL - 70
        self.rect.bottom = self.chao_y

        self.velocidade_y = 0
        self.gravidade_normal = 1.0
        self.no_chao = True
        self.descida_rapida = False
        self.agachado = False

        self.anim_pernas = 0

        # Power-ups
        self.tempo_ima = 0
        self.tempo_turbo = 0
        self.tempo_mult = 0
        self.tempo_slow = 0
        self.escudo_hits = 0
        self.escudo_max = 0

        # Estatísticas
        self.pulos_na_rodada = 0
        self.powerups_coletados = 0
        self.slow_ativados = 0

        # Morte
        self.morrendo = False
        self.angulo_rotacao = 0
        self.tempo_morte = 0

    def obter_hitbox(self):
        if self.agachado and self.no_chao:
            body_w = self.rect.width * (52 / 80)
            body_h = self.rect.height * (38 / 80)
            body_x = self.rect.left + self.rect.width * (14 / 80)
            body_y = self.rect.bottom - body_h
            return pygame.Rect(int(body_x), int(body_y), int(body_w), int(body_h))
        else:
            body_w = self.rect.width * (36 / 80)
            body_h = self.rect.height * (50 / 80)
            body_x = self.rect.left + self.rect.width * (22 / 80)
            body_y = self.rect.top + self.rect.height * (14 / 80)
            return pygame.Rect(int(body_x), int(body_y), int(body_w), int(body_h))

    def desenhar_pernas(self, surf, cor):
        if self.agachado and self.no_chao:
            fase = self.anim_pernas * 1.4
            dx1 = math.cos(fase) * 8
            dx2 = math.cos(fase + math.pi) * 8
            pygame.draw.line(surf, cor, (28, 64), (20 + dx1, 75), 7)
            pygame.draw.line(surf, cor, (44, 64), (50 + dx2, 75), 7)
            pygame.draw.circle(surf, cor, (int(20 + dx1), 75), 4)
            pygame.draw.circle(surf, cor, (int(50 + dx2), 75), 4)
            return

        ancora_y = 66
        if self.no_chao and not self.morrendo:
            dx1 = math.cos(self.anim_pernas) * 5
            dx2 = math.cos(self.anim_pernas + math.pi) * 5
            dy1 = max(0, -math.sin(self.anim_pernas) * 4)
            dy2 = max(0, -math.sin(self.anim_pernas + math.pi) * 4)
        else:
            dx1, dy1 = -3, -3
            dx2, dy2 = 3, -5
            if self.descida_rapida:
                dx1, dy1 = -2, -6
                dx2, dy2 = 2, -6

        pygame.draw.line(surf, cor, (32, ancora_y), (32 + dx1, 74 - dy1), 8)
        pygame.draw.line(surf, cor, (48, ancora_y), (48 + dx2, 74 - dy2), 8)
        pygame.draw.circle(surf, cor, (int(32 + dx1), int(74 - dy1)), 4)
        pygame.draw.circle(surf, cor, (int(48 + dx2), int(74 - dy2)), 4)

    def desenhar_raios_ima(self, surf, frame_contador):
        cx, cy = 40, 40
        raio = 38
        pontos_raio = []
        qtd_segmentos = 8
        for i in range(qtd_segmentos):
            angulo = (math.pi * 2 / qtd_segmentos) * i
            r_offset = raio + int(math.sin(frame_contador * 0.4 + i * 1.5) * 6)
            px = cx + math.cos(angulo) * r_offset
            py = cy + math.sin(angulo) * r_offset
            pontos_raio.append((px, py))

        if len(pontos_raio) > 2:
            pygame.draw.polygon(surf, AZUL_IMA, pontos_raio, 2)
            pygame.draw.polygon(surf, BRANCO, pontos_raio, 1)

    def aplicar_visual_skin(self, cor_corpo, frame_contador=0):
        surf = self.image_original
        nome = self.skin_nome

        if self.agachado and self.no_chao:
            self.desenhar_pernas(surf, (15, 15, 15) if nome == "AZUL" else cor_corpo)

            pts_corpo_inclinado = [(20, 58), (34, 38), (68, 48), (54, 68)]
            pygame.draw.polygon(surf, cor_corpo, pts_corpo_inclinado)

            if nome == "AZUL":
                pygame.draw.polygon(surf, (200, 20, 20), [(36, 40), (62, 48), (60, 53), (34, 45)])
                pygame.draw.polygon(surf, BRANCO, [(48, 43), (56, 46), (54, 49), (46, 46)])
                pygame.draw.circle(surf, PRETO, (52, 47), 2)
            elif nome == "ROSA":
                pygame.draw.polygon(surf, BRANCO, [(24, 36), (10, 20), (16, 18), (28, 34)])
                pygame.draw.polygon(surf, BRANCO, [(32, 38), (18, 22), (24, 20), (36, 36)])
                pygame.draw.ellipse(surf, BRANCO, (34, 46, 22, 20))
                pygame.draw.circle(surf, PRETO, (52, 48), 3)
                pygame.draw.circle(surf, BRANCO, (53, 47), 1)
            elif nome == "VERDE":
                pygame.draw.polygon(surf, cor_corpo, [(20, 58), (4, 64), (18, 68)])
                pygame.draw.polygon(surf, (241, 196, 15), [(42, 52), (64, 58), (56, 68), (38, 62)])
                pygame.draw.circle(surf, PRETO, (54, 46), 3)
            elif nome == "DOURADO":
                pygame.draw.polygon(surf, (20, 20, 20), [(30, 36), (58, 44), (55, 49), (28, 41)])
                pygame.draw.polygon(surf, PRETO, [(42, 44), (58, 49), (55, 55), (40, 50)])
                pygame.draw.polygon(surf, (255, 215, 0), [(41, 43), (59, 48), (56, 56), (39, 51)], 1)
                pygame.draw.line(surf, (218, 165, 32), (32, 60), (48, 66), 3)

            if self.tempo_ima > 0 and not self.morrendo:
                self.desenhar_raios_ima(surf, frame_contador)
            return

        CORPO_RECT = (22, 14, 36, 50)

        if nome == "AZUL":
            self.desenhar_pernas(surf, (15, 15, 15))
            mv = math.sin(self.anim_pernas) * 4
            mv2 = math.cos(self.anim_pernas) * 4
            pygame.draw.line(surf, (200, 20, 20), (22, 26), (6 + mv, 18 + mv2), 4)
            pygame.draw.line(surf, (200, 20, 20), (22, 28), (4 + mv2, 34 + mv), 4)

            pygame.draw.rect(surf, cor_corpo, CORPO_RECT, border_radius=10)
            pygame.draw.rect(surf, (200, 20, 20), (22, 22, 36, 8), border_radius=4)
            pygame.draw.polygon(surf, BRANCO, [(30, 24), (36, 26), (36, 30), (30, 30)])
            pygame.draw.polygon(surf, BRANCO, [(44, 26), (50, 24), (50, 30), (44, 30)])
            pygame.draw.rect(surf, PRETO, (33, 27, 2, 2), border_radius=1)
            pygame.draw.rect(surf, PRETO, (45, 27, 2, 2), border_radius=1)

        elif nome == "ROSA":
            self.desenhar_pernas(surf, cor_corpo)
            pygame.draw.circle(surf, BRANCO, (20, 56), 6)
            pygame.draw.rect(surf, BRANCO, (28, 0, 8, 18), border_radius=4)
            pygame.draw.rect(surf, (255, 105, 180), (30, 2, 4, 14), border_radius=2)
            pygame.draw.rect(surf, BRANCO, (44, 0, 8, 18), border_radius=4)
            pygame.draw.rect(surf, (255, 105, 180), (46, 2, 4, 14), border_radius=2)

            pygame.draw.rect(surf, cor_corpo, CORPO_RECT, border_radius=10)
            pygame.draw.ellipse(surf, BRANCO, (28, 39, 24, 25))
            pygame.draw.rect(surf, PRETO, (30, 28, 6, 8), border_radius=2)
            pygame.draw.rect(surf, BRANCO, (32, 28, 4, 4), border_radius=1)
            pygame.draw.rect(surf, PRETO, (44, 28, 6, 8), border_radius=2)
            pygame.draw.rect(surf, BRANCO, (46, 28, 4, 4), border_radius=1)
            pygame.draw.rect(surf, (255, 105, 180), (38, 36, 4, 3), border_radius=1)

        elif nome == "VERDE":
            self.desenhar_pernas(surf, cor_corpo)
            pygame.draw.polygon(surf, cor_corpo, [(22, 46), (2, 60), (22, 62)])
            pygame.draw.rect(surf, cor_corpo, CORPO_RECT, border_radius=10)
            pygame.draw.rect(surf, (241, 196, 15), (40, 34, 18, 30), border_radius=6)
            for i in range(16, 56, 12):
                pygame.draw.polygon(surf, (34, 139, 34), [(22, i), (14, i + 6), (22, i + 12)])
            pygame.draw.polygon(surf, cor_corpo, [(58, 36), (68, 40), (66, 44), (58, 42)])
            pygame.draw.rect(surf, (34, 180, 90), (58, 22, 12, 10), border_radius=3)
            pygame.draw.rect(surf, PRETO, (46, 20, 6, 6), border_radius=2)
            pygame.draw.rect(surf, BRANCO, (48, 20, 2, 2), border_radius=1)
            pygame.draw.line(surf, PRETO, (44, 18), (52, 22), 2)

        elif nome == "DOURADO":
            self.desenhar_pernas(surf, cor_corpo)
            pygame.draw.rect(surf, cor_corpo, CORPO_RECT, border_radius=10)
            pygame.draw.rect(surf, (20, 20, 20), (22, 10, 36, 12), border_radius=4)
            pygame.draw.rect(surf, (200, 30, 30), (6, 18, 16, 4), border_radius=2)
            pygame.draw.rect(surf, (255, 0, 0), (32, 20, 36, 22), 2, border_radius=4)
            pygame.draw.rect(surf, PRETO, (36, 24, 28, 14), border_radius=3)
            pygame.draw.rect(surf, (255, 215, 0), (34, 22, 32, 18), 2, border_radius=3)
            pygame.draw.line(surf, BRANCO, (38, 26), (42, 34), 2)
            pygame.draw.line(surf, BRANCO, (44, 26), (46, 30), 2)
            pygame.draw.line(surf, (255, 215, 0), (48, 24), (50, 24), 2)
            pygame.draw.lines(surf, (218, 165, 32), False, [(28, 42), (40, 56), (52, 42)], 3)
            pygame.draw.rect(surf, (218, 165, 32), (38, 56, 6, 8), border_radius=2)

        if self.tempo_ima > 0 and not self.morrendo:
            self.desenhar_raios_ima(surf, frame_contador)

    def ativar_powerup(self, tipo, gerenciador_sons=None, vol_sfx=1.0, vibracao_ligada=True):
        if self.morrendo: return
        self.powerups_coletados += 1
        self._visual_dirty = True
        nivel = self.upgrades.get(tipo, 0)
        config = UPGRADES_CONFIG.get(tipo)
        if tipo == "ESCUDO":
            self.escudo_hits = config["impactos_base"] + (nivel * config["bonus_por_nivel"])
            self.escudo_max = self.escudo_hits
        else:
            duracao = config["duracao_base"] + (nivel * config["bonus_por_nivel"])
            if tipo == "IMA":
                self.tempo_ima = duracao
                disparar_vibracao(0.2, vibracao_ligada)
            elif tipo == "TURBO":
                self.tempo_turbo = duracao
                disparar_vibracao(0.4, vibracao_ligada)
            elif tipo == "MULT_2X":
                self.tempo_mult = duracao
            elif tipo == "SLOW":
                self.tempo_slow = duracao
                self.slow_ativados += 1

        if gerenciador_sons:
            gerenciador_sons.tocar_som("powerup", self.tempo_slow > 0, vol_sfx)
            if tipo == "TURBO":
                gerenciador_sons.tocar_som("turbo", self.tempo_slow > 0, vol_sfx)
            elif tipo == "IMA":
                gerenciador_sons.tocar_som("ima", self.tempo_slow > 0, vol_sfx)

    def pular(self, gerenciador_sons=None, vol_sfx=1.0):
        if self.morrendo: return
        if self.no_chao:
            self.velocidade_y = -13.5
            self.no_chao = False
            self.descida_rapida = False
            self.agachado = False
            self.w_atual, self.h_atual = 58, 96
            self._visual_dirty = True
            self.pulos_na_rodada += 1
            if gerenciador_sons:
                gerenciador_sons.tocar_som("pulo", self.tempo_slow > 0, vol_sfx)

    def iniciar_descida_rapida(self, gerenciador_sons=None, vol_sfx=1.0):
        if self.morrendo: return
        if not self.no_chao:
            if not self.descida_rapida and gerenciador_sons:
                gerenciador_sons.tocar_som("swipe_down", self.tempo_slow > 0, vol_sfx)
            self.descida_rapida = True
            self.velocidade_y = max(self.velocidade_y, 18.0)
            self.w_atual, self.h_atual = 53, 99
            self._visual_dirty = True

    def agachar(self, ativacao, gerenciador_sons=None, vol_sfx=1.0):
        if self.morrendo: return
        estava_agachado = self.agachado
        if self.no_chao:
            self.agachado = ativacao
            if self.agachado != estava_agachado:
                self._visual_dirty = True
            if ativacao and not estava_agachado and gerenciador_sons:
                gerenciador_sons.tocar_som("swipe_down", self.tempo_slow > 0, vol_sfx)
        else:
            self.agachado = False
            if ativacao:
                self.iniciar_descida_rapida(gerenciador_sons, vol_sfx)

    def iniciar_morte(self):
        self.morrendo = True
        self.velocidade_y = -12
        self.tempo_morte = 60
        self.tempo_turbo = 0
        self.escudo_hits = 0
        self.agachado = False
        self._visual_dirty = True

    def update_morte(self, particulas, pool_manager):
        # Apenas atualiza a simulacao. A rotacao real da imagem e feita uma vez
        # por frame renderizado, nunca em cada passo de recuperacao.
        self.velocidade_y += 0.8
        self.rect.y += self.velocidade_y
        self.rect.x -= 2
        self.angulo_rotacao += 18
        self.tempo_morte -= 1
        centro = self.rect.center
        rad = math.radians(self.angulo_rotacao % 360)
        w0, h0 = self.image_original.get_size()
        w_rot = max(1, int(abs(w0 * math.cos(rad)) + abs(h0 * math.sin(rad))))
        h_rot = max(1, int(abs(h0 * math.cos(rad)) + abs(w0 * math.sin(rad))))
        self.rect.size = (w_rot, h_rot)
        self.rect.center = centro
        self._visual_dirty = True

        if random.random() < 0.5:
            criar_explosao_particulas(self.rect.centerx, self.rect.centery, self.cor_base, 2, particulas, pool_manager)

    def renderizar_visual(self, frame_contador=0):
        """Atualiza a imagem do jogador uma vez por frame visivel, nao por tick."""
        if not self._visual_dirty:
            return
        centro_x = self.rect.centerx
        base_bottom = self.rect.bottom
        if self.morrendo:
            self.image = pygame.transform.rotate(self.image_original, self.angulo_rotacao)
            self.rect = self.image.get_rect(center=self.rect.center)
            self._visual_dirty = False
            return

        self.image_original.fill((0, 0, 0, 0))
        self.aplicar_visual_skin(self._visual_cor_atual, frame_contador)
        tamanho_imagem = (max(1, int(self.w_atual)), max(1, int(self.h_atual)))
        imagem_escalada = self._scaled_image_cache.get(tamanho_imagem)
        if imagem_escalada is None:
            imagem_escalada = pygame.Surface(tamanho_imagem, pygame.SRCALPHA)
            self._scaled_image_cache[tamanho_imagem] = imagem_escalada
        pygame.transform.scale(self.image_original, tamanho_imagem, imagem_escalada)
        self.image = imagem_escalada
        self.rect = self.image.get_rect()
        self.rect.centerx = centro_x
        self.rect.bottom = base_bottom
        self._visual_dirty = False

    def update(self, vel_jogo, frame_contador=0, segurando_pulo=False, segurando_baixo=False, particulas=None,
               pool_manager=None, gerenciador_sons=None, vol_sfx=1.0):
        if self.morrendo:
            self.update_morte(particulas, pool_manager)
            return

        self.agachar(segurando_baixo, gerenciador_sons, vol_sfx)
        self.anim_pernas += vel_jogo * 0.08

        if self.tempo_ima > 0: self.tempo_ima -= 1
        if self.tempo_turbo > 0: self.tempo_turbo -= 1
        if self.tempo_mult > 0: self.tempo_mult -= 1
        if self.tempo_slow > 0: self.tempo_slow -= 1

        if self.tempo_turbo > 0:
            self._visual_cor_atual = LARANJA_TURBO
        elif self.tempo_slow > 0:
            self._visual_cor_atual = VERDE_SLOW
        elif self.tempo_ima > 0:
            self._visual_cor_atual = AZUL_IMA
        elif self.tempo_mult > 0:
            self._visual_cor_atual = ROSA_MULT
        else:
            self._visual_cor_atual = self.cor_base
        self._visual_dirty = True

        if self.descida_rapida:
            self.velocidade_y += 2.2
            self.rect.y += self.velocidade_y
        else:
            if not self.no_chao and segurando_pulo and self.velocidade_y < 0:
                g = self.gravidade_normal * 0.45
            else:
                g = self.gravidade_normal

            if self.tempo_slow > 0:
                self.rect.y += self.velocidade_y * 0.5
                self.velocidade_y += g * 0.5
            else:
                self.rect.y += self.velocidade_y
                self.velocidade_y += g

        w_alvo, h_alvo = self.base_w, self.base_h
        if self.agachado and self.no_chao:
            w_alvo, h_alvo = 80, 80
        elif not self.no_chao:
            if not self.descida_rapida:
                w_alvo, h_alvo = 71, 86

        if self.rect.bottom >= self.chao_y:
            if not self.no_chao and not self.agachado:
                self.w_atual, self.h_atual = 100, 65
            self.rect.bottom = self.chao_y
            self.velocidade_y = 0
            self.no_chao = True
            self.descida_rapida = False

        self.w_atual += (w_alvo - self.w_atual) * 0.25
        self.h_atual += (h_alvo - self.h_atual) * 0.25

        # Atualiza apenas a hitbox retangular durante a simulacao. A imagem so e
        # rasterizada/redimensionada uma vez antes do desenho da tela.
        centro_x = self.rect.centerx
        base_bottom = self.rect.bottom
        tamanho_imagem = (max(1, int(self.w_atual)), max(1, int(self.h_atual)))
        self.rect.size = tamanho_imagem
        self.rect.centerx = centro_x
        self.rect.bottom = base_bottom


_CACHE_VISUAIS_VOADORES = {}

# --- OBSTÁCULOS E ITENS ---
class ObstaculoTerrestre(Sprite):
    def __init__(self, x_pos, qtd_cactos=1):
        super().__init__()
        self.qtd_cactos = qtd_cactos
        self.cactos_info = []
        largura_total = 0
        for _ in range(qtd_cactos):
            w = random.randint(26, 38)
            h = random.randint(45, 80)
            self.cactos_info.append((largura_total, w, h))
            largura_total += w

        self.largura = max(28, largura_total)
        self.altura = max(h for _, _, h in self.cactos_info)
        self.image = pygame.Surface((self.largura, self.altura)).convert()
        self.image.fill(CHAVE_TRANSPARENCIA_SPRITES)
        self.image.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.bottom = ALTURA_VIRTUAL - 70
        self.desenhar_grupo_cactos()

    def desenhar_grupo_cactos(self):
        for rel_x, w, h in self.cactos_info:
            y_offset = self.altura - h
            tronco_w = max(10, w // 2)
            tronco_x = rel_x + (w - tronco_w) // 2
            pygame.draw.rect(self.image, VERDE_CACTO, (tronco_x, y_offset, tronco_w, h),
                             border_top_left_radius=tronco_w // 2, border_top_right_radius=tronco_w // 2)
            pygame.draw.rect(self.image, VERDE_CACTO_ESCURO, (tronco_x + 2, y_offset + 2, max(2, tronco_w - 4), h - 2),
                             border_top_left_radius=tronco_w // 2, border_top_right_radius=tronco_w // 2)

            if h > 50:
                arm_y = y_offset + int(h * 0.4)
                pygame.draw.rect(self.image, VERDE_CACTO, (rel_x, arm_y, tronco_x - rel_x, 8), border_top_left_radius=4)
                pygame.draw.rect(self.image, VERDE_CACTO, (rel_x, arm_y - 12, 7, 15), border_top_left_radius=4,
                                 border_top_right_radius=4)

                arm_y2 = y_offset + int(h * 0.25)
                right_x = tronco_x + tronco_w
                pygame.draw.rect(self.image, VERDE_CACTO, (right_x, arm_y2, rel_x + w - right_x, 8),
                                 border_top_right_radius=4)
                pygame.draw.rect(self.image, VERDE_CACTO, (rel_x + w - 7, arm_y2 - 12, 7, 15), border_top_left_radius=4,
                                 border_top_right_radius=4)

            for sy in range(y_offset + 10, y_offset + h - 10, 12):
                pygame.draw.line(self.image, VERDE_CACTO_CLARO, (tronco_x + 2, sy), (tronco_x + tronco_w - 2, sy), 1)

    def update(self, velocidade_jogo):
        self.rect.x -= velocidade_jogo
        if self.rect.x < -150: self.kill()


class ObstaculoVoador(Sprite):
    def __init__(self, x_pos):
        super().__init__()
        self.largura = 84
        self.altura = 56
        self.image = pygame.Surface((self.largura, self.altura)).convert()
        self.image.fill(CHAVE_TRANSPARENCIA_SPRITES)
        self.image.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = random.choice([ALTURA_VIRTUAL - 130, ALTURA_VIRTUAL - 180, ALTURA_VIRTUAL - 240])
        self.anim_frame = 0
        self.e_noite = False

    def update(self, velocidade_jogo, e_noite=False, e_slow=False):
        fator_vel = 0.6 if e_slow else 1.2
        self.rect.x -= (velocidade_jogo + fator_vel)
        self.anim_frame += 0.1 if e_slow else 0.2
        self.e_noite = bool(e_noite)
        if self.rect.x < -120:
            self.kill()

    def renderizar_visual(self):
        asa_offset = int(math.sin(self.anim_frame) * 14)
        chave = (self.e_noite, asa_offset)
        imagem = _CACHE_VISUAIS_VOADORES.get(chave)
        if imagem is None:
            imagem = pygame.Surface((self.largura, self.altura)).convert()
            imagem.fill(CHAVE_TRANSPARENCIA_SPRITES)
            imagem.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
            cor_ptero = ROXO_VOADOR
            if self.e_noite:
                pygame.draw.ellipse(imagem, CIANO_ESCUDO, (16, 12, 52, 28))
                pygame.draw.circle(imagem, AMARELO_NEON, (22, 24), 6)
            pygame.draw.ellipse(imagem, cor_ptero, (20, 16, 44, 24))
            pygame.draw.polygon(imagem, cor_ptero, [(20, 24), (0, 30), (20, 34)])
            pygame.draw.polygon(imagem, cor_ptero, [(40, 24), (20, 8 + asa_offset), (60, 8 + asa_offset)])
            pygame.draw.polygon(imagem, BRANCO, [(40, 24), (20, 8 + asa_offset), (25, 8 + asa_offset)], 2)
            cor_olho = AMARELO_NEON if self.e_noite else PRETO
            pygame.draw.circle(imagem, cor_olho, (18, 24), 3)
            _CACHE_VISUAIS_VOADORES[chave] = imagem
        self.image = imagem


class ObstaculoPulaPula(Sprite):
    def __init__(self, x_pos):
        super().__init__()
        self.image = pygame.Surface((35, 35))
        self.image.fill(ROXO_VOADOR)
        pygame.draw.rect(self.image, BRANCO, (5, 5, 25, 25), 2)
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.chao_y = ALTURA_VIRTUAL - 70
        self.rect.bottom = self.chao_y
        self.velocidade_y = -10

    def update(self, velocidade_jogo, e_slow=False):
        self.rect.x -= (velocidade_jogo * 0.8)
        gravidade = 0.35 * 0.5 if e_slow else 0.35
        fator_mov = 0.5 if e_slow else 1.0

        self.velocidade_y += gravidade
        self.rect.y += self.velocidade_y * fator_mov

        if self.rect.bottom >= self.chao_y:
            self.rect.bottom = self.chao_y
            self.velocidade_y = random.choice([-15, -17, -19])
        if self.rect.x < -100: self.kill()


class AvisoLaser(Sprite):
    _imagens_aviso = {}
    _imagem_disparo = None

    @classmethod
    def _obter_imagem_aviso(cls, alpha):
        imagem = cls._imagens_aviso.get(alpha)
        if imagem is None:
            imagem = pygame.Surface((LARGURA_VIRTUAL, 28), pygame.SRCALPHA)
            pygame.draw.rect(imagem, (255, 0, 0, alpha), (0, 0, LARGURA_VIRTUAL, 28))
            pygame.draw.rect(imagem, AMARELO_NEON, (0, 0, LARGURA_VIRTUAL, 28), 2)
            cls._imagens_aviso[alpha] = imagem
        return imagem

    @classmethod
    def _obter_imagem_disparo(cls):
        if cls._imagem_disparo is None:
            imagem = pygame.Surface((LARGURA_VIRTUAL, 28), pygame.SRCALPHA)
            pygame.draw.rect(imagem, (255, 30, 30, 255), (0, 0, LARGURA_VIRTUAL, 28))
            pygame.draw.rect(imagem, BRANCO, (0, 4, LARGURA_VIRTUAL, 20))
            pygame.draw.rect(imagem, CIANO_ESCUDO, (0, 10, LARGURA_VIRTUAL, 8))
            cls._imagem_disparo = imagem
        return cls._imagem_disparo

    def __init__(self, y_pos, delay_warning):
        super().__init__()
        self.altura_total = 28
        self.image = self._obter_imagem_aviso(60)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = y_pos
        self.timer = delay_warning
        self.timer_max = delay_warning
        self.ativo = False
        self.som_disparo_tocado = False

    def update(self, velocidade_jogo, gerenciador_sons=None, e_slow=False, vol_sfx=1.0):
        self.timer -= 1
        if self.timer > 0:
            if gerenciador_sons and self.timer in [150, 120, 90, 60, 45, 30, 15]:
                if self.timer <= 30:
                    gerenciador_sons.tocar_som("contagem_laser_high", e_slow, vol_sfx)
                else:
                    gerenciador_sons.tocar_som("contagem_laser", e_slow, vol_sfx)
            freq_pisca = 6 if self.timer < 60 else 12
            alpha = 200 if (self.timer // freq_pisca) % 2 == 0 else 60
            self.image = self._obter_imagem_aviso(alpha)
        elif self.timer > -15:
            if not self.som_disparo_tocado and gerenciador_sons:
                gerenciador_sons.tocar_som("disparo_laser", e_slow, vol_sfx)
                self.som_disparo_tocado = True
            self.ativo = True
            self.image = self._obter_imagem_disparo()
        else:
            self.kill()


class PowerUp(Sprite):
    def __init__(self, x_pos, y_pos, tipo):
        super().__init__()
        self.tipo = tipo
        self.image = pygame.Surface((34, 34)).convert()
        self.image.fill(CHAVE_TRANSPARENCIA_SPRITES)
        self.image.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
        cor = UPGRADES_CONFIG[tipo]["cor"]
        pygame.draw.circle(self.image, cor, (17, 17), 16)
        pygame.draw.circle(self.image, BRANCO, (17, 17), 16, 2)
        desenhar_icone_powerup(self.image, tipo, 17, 17)
        self.rect = self.image.get_rect(center=(x_pos, y_pos))

    def update(self, velocidade_jogo):
        self.rect.x -= velocidade_jogo
        if self.rect.x < -50: self.kill()


# --- SISTEMA DE MISSÕES ---
def gerar_missoes_rodada():
    banco_missoes = [
        {"tipo": "MOEDAS", "key": "missao_moedas", "alvo": random.randint(200, 500), "atual": 0, "recompensa": 100,
         "concluida": False},
        {"tipo": "DISTANCIA", "key": "missao_distancia", "alvo": random.randint(1200, 3000), "atual": 0,
         "recompensa": 350, "concluida": False},
        {"tipo": "QUEBRAR", "key": "missao_quebrar", "alvo": random.randint(15, 30), "atual": 0, "recompensa": 150,
         "concluida": False},
        {"tipo": "PULOS", "key": "missao_pulos", "alvo": random.randint(150, 400), "atual": 0, "recompensa": 80,
         "concluida": False},
        {"tipo": "POWERUPS", "key": "missao_powerups", "alvo": random.randint(10, 30), "atual": 0, "recompensa": 100,
         "concluida": False},
        {"tipo": "SLOW", "key": "missao_slow", "alvo": random.randint(5, 12), "atual": 0, "recompensa": 50,
         "concluida": False}
    ]
    return random.sample(banco_missoes, 3)


# --- GERADOR DE PADRÕES EXPANDIDO DE MOEDAS (32 FORMATOS) ---
def gerar_padrao_moedas(x_base, y_base, formato, todos_sprites, moedas, pool_manager):
    y_limite_chao = ALTURA_VIRTUAL - 95
    y_limite_topo = ALTURA_VIRTUAL - 260
    offsets = []

    if formato == "MOEDA_UNICA":
        offsets = [(0, 0)]
    elif formato == "PAR_HORIZONTAL":
        offsets = [(0, 0), (28, 0)]
    elif formato == "PAR_VERTICAL":
        offsets = [(0, 0), (0, -28)]
    elif formato == "TRIO_HORIZONTAL":
        offsets = [(0, 0), (28, 0), (56, 0)]
    elif formato == "TRIO_VERTICAL":
        offsets = [(0, 0), (0, -28), (0, -56)]
    elif formato == "DIAGONAL_SUBINDO":
        offsets = [(0, 0), (25, -22), (50, -44)]
    elif formato == "DIAGONAL_DESCENDO":
        offsets = [(0, -44), (25, -22), (50, 0)]
    elif formato == "SMILEY":
        offsets = [(0, -30), (30, -30), (15, 0)]
    elif formato == "LINHA":
        for i in range(random.choice([4, 5, 6])): offsets.append((i * 28, 0))
    elif formato == "V":
        offsets = [(0, -40), (28, -20), (56, 0), (84, -20), (112, -40)]
    elif formato == "V_INVERTIDO":
        offsets = [(0, 0), (28, -22), (56, -44), (84, -22), (112, 0)]
    elif formato == "ESCADA":
        for i in range(4): offsets.append((i * 28, -i * 22))
    elif formato == "ESCADA_DESCENDENTE":
        for i in range(4): offsets.append((i * 28, -(3 - i) * 22))
    elif formato == "QUADRADO":
        for col in range(3):
            for lin in range(2): offsets.append((col * 28, -lin * 28))
    elif formato == "QUADRADO_PEQUENO":
        for col in range(2):
            for lin in range(2): offsets.append((col * 28, -lin * 28))
    elif formato == "ARCO":
        for i in range(6):
            ang = math.radians(180 * i / 5)
            offsets.append((i * 26, -math.sin(ang) * 45))
    elif formato == "CIRCULO":
        raio = 30
        for i in range(6):
            ang = math.radians(i * 60)
            offsets.append((math.cos(ang) * raio, math.sin(ang) * raio))
    elif formato == "DIAMANTE":
        offsets = [(0, 0), (25, -25), (50, 0), (25, 25)]
    elif formato == "ONDA":
        for i in range(6): offsets.append((i * 26, math.sin(i * 0.8) * 28))
    elif formato == "COLUNA":
        for i in range(random.choice([3, 4])): offsets.append((0, -i * 28))
    elif formato == "COLUNA_DUPLA":
        for col in range(2):
            for lin in range(3): offsets.append((col * 30, -lin * 28))
    elif formato == "TRIANGULO":
        offsets = [(0, 0), (28, -28), (56, 0), (28, 0)]
    elif formato == "ZIGZAG":
        offsets = [(0, 0), (25, -30), (50, 0), (75, -30), (100, 0)]
    elif formato == "MEGACRUZ":
        for i in range(-3, 4):
            offsets.append((i * 26, 0))
            if i != 0: offsets.append((0, i * 26))
    elif formato == "MEGAGRID_4X3":
        for col in range(5):
            for lin in range(3): offsets.append((col * 28, -lin * 26))
    elif formato == "MEGASERPENTE":
        for i in range(12):
            offsets.append((i * 24, math.sin(i * 0.6) * 35))
    elif formato == "CHUVA_DE_MOEDAS":
        for col in range(6):
            for lin in range(2):
                offsets.append((col * 28 + (lin * 14), -lin * 35))
    elif formato == "PIRAMIDE_GIGANTE":
        offsets = [(0, 0), (28, 0), (56, 0), (84, 0), (112, 0),
                   (14, -28), (42, -28), (70, -28), (98, -28),
                   (28, -56), (56, -56), (84, -56),
                   (42, -84), (70, -84), (56, -112)]
    elif formato == "MEGA_ANEL":
        raio = 45
        for i in range(12):
            ang = math.radians(i * 30)
            offsets.append((math.cos(ang) * raio, math.sin(ang) * raio))
    elif formato == "MATRIZ_DENSA":
        for col in range(4):
            for lin in range(4): offsets.append((col * 26, -lin * 26))
    elif formato == "ONDA_DUPLA_GIGANTE":
        for i in range(8):
            offsets.append((i * 26, math.sin(i * 0.7) * 30))
            offsets.append((i * 26, math.sin(i * 0.7) * 30 - 35))
    elif formato == "X_GIGANTE":
        for i in range(-3, 4):
            offsets.append((i * 25, i * 25))
            offsets.append((i * 25, -i * 25))

    if offsets:
        min_dy = min(dy for _, dy in offsets)
        max_dy = max(dy for _, dy in offsets)

        if y_base + min_dy < y_limite_topo:
            y_base = y_limite_topo - min_dy
        if y_base + max_dy > y_limite_chao:
            y_base = y_limite_chao - max_dy

    for dx, dy in offsets:
        px = x_base + dx
        py = y_base + dy
        if y_limite_topo <= py <= y_limite_chao:
            m = pool_manager.obter_moeda(px, py)
            todos_sprites.add(m)
            moedas.add(m)


cooldown_laser = 0


def gerar_padrao(todos_sprites, obstaculos, perigos_especiais, moedas, powerups, metros, pool_manager):
    global cooldown_laser
    x_inicial = LARGURA_VIRTUAL + 20

    if cooldown_laser > 0:
        cooldown_laser -= 1

    for obs in list(obstaculos) + list(perigos_especiais):
        if obs.rect.right > LARGURA_VIRTUAL - 140:
            return

    if len(obstaculos) + len(perigos_especiais) >= 3:
        return

    if metros >= 600 and cooldown_laser <= 0 and random.random() < 0.15:
        faixa_y = random.choice([ALTURA_VIRTUAL - 110, ALTURA_VIRTUAL - 160])
        laser = AvisoLaser(faixa_y, delay_warning=150)
        todos_sprites.add(laser)
        perigos_especiais.add(laser)
        cooldown_laser = 12
        return

    opcoes = ["normal"]
    if metros >= 200: opcoes.append("agrupado_colado")
    if metros >= 200: opcoes.append("voador")
    if metros >= 600: opcoes.append("pulador")

    tipo_obs = random.choice(opcoes)

    if tipo_obs == "voador":
        obs = ObstaculoVoador(x_inicial)
        todos_sprites.add(obs);
        obstaculos.add(obs)
    elif tipo_obs == "pulador":
        obs = ObstaculoPulaPula(x_inicial)
        todos_sprites.add(obs);
        obstaculos.add(obs)
    elif tipo_obs == "agrupado_colado":
        qtd_cactos = random.randint(2, 4)
        obs = ObstaculoTerrestre(x_inicial, qtd_cactos=qtd_cactos)
        todos_sprites.add(obs);
        obstaculos.add(obs)
    else:
        obs = ObstaculoTerrestre(x_inicial, qtd_cactos=1)
        todos_sprites.add(obs);
        obstaculos.add(obs)

    if random.random() < 0.07:
        tipo_powerup = random.choice(list(UPGRADES_CONFIG.keys()))
        p = PowerUp(x_inicial + 160, random.choice([ALTURA_VIRTUAL - 140, ALTURA_VIRTUAL - 220]), tipo_powerup)
        todos_sprites.add(p);
        powerups.add(p)

    formato_moeda = random.choice([
        "MOEDA_UNICA", "PAR_HORIZONTAL", "PAR_VERTICAL", "TRIO_HORIZONTAL", "TRIO_VERTICAL",
        "DIAGONAL_SUBINDO", "DIAGONAL_DESCENDO", "SMILEY", "LINHA", "V", "V_INVERTIDO",
        "ESCADA", "ESCADA_DESCENDENTE", "QUADRADO", "QUADRADO_PEQUENO", "ARCO", "CIRCULO",
        "DIAMANTE", "ONDA", "COLUNA", "COLUNA_DUPLA", "TRIANGULO", "ZIGZAG", "MEGACRUZ",
        "MEGAGRID_4X3", "MEGASERPENTE", "CHUVA_DE_MOEDAS", "PIRAMIDE_GIGANTE", "MEGA_ANEL",
        "MATRIZ_DENSA", "ONDA_DUPLA_GIGANTE", "X_GIGANTE"
    ])
    y_moeda = random.choice([
        ALTURA_VIRTUAL - 120, ALTURA_VIRTUAL - 150, ALTURA_VIRTUAL - 180,
        ALTURA_VIRTUAL - 210, ALTURA_VIRTUAL - 230
    ])
    gerar_padrao_moedas(x_inicial + 180, y_moeda, formato_moeda, todos_sprites, moedas, pool_manager)


# --- LOOP PRINCIPAL (SIMULACAO FIXA 60 HZ + RENDERIZACAO INDEPENDENTE) ---
def main():
    dados = carregar_dados()
    estado = "INICIO"
    estado_anterior = None
    anim_menu_tempo = 0

    gerenciador_sons = GerenciadorSons()
    pool_manager = PoolManager()

    todos_sprites = pygame.sprite.Group()
    obstaculos = pygame.sprite.Group()
    perigos_especiais = pygame.sprite.Group()
    moedas = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    textos_flut = pygame.sprite.Group()
    particulas = pygame.sprite.Group()

    bg_parallax = ParallaxBackground()
    missoes_atuais = gerar_missoes_rodada()

    jogador = None
    pontuacao = 0
    moedas_coletadas = 0
    novo_recorde_alcançado = False
    frame_count = 0
    cache_telas_estaticas = {}

    shake_timer = 0
    shake_intensidade = 0

    touch_start_pos = None
    touch_current_pos = None
    toque_ativo = False
    segurando_baixo_touch = False
    input_pulo_ativo = False
    input_baixo_ativo = False
    input_mouse_ativo = False
    ultimo_clique_tempo = 0

    cor_atual_ceu = list(COR_DIA)

    def aplicar_shake(frames, intensidade):
        nonlocal shake_timer, shake_intensidade
        shake_timer = frames
        shake_intensidade = intensidade

    EVENTO_GERAR = pygame.USEREVENT + 1
    tempo_spawn_atual = 1500
    superficies_escala = {}

    # Botões Centralizados do Menu Inicial
    btn_jogar = pygame.Rect(75, 390, 300, 50)
    btn_loja = pygame.Rect(75, 455, 300, 50)
    btn_upgrades = pygame.Rect(75, 520, 300, 50)
    btn_config = pygame.Rect(75, 585, 300, 50)

    btn_voltar = pygame.Rect(75, 710, 300, 50)
    btn_reiniciar = pygame.Rect(75, 540, 300, 50)
    btn_menu_gameover = pygame.Rect(75, 610, 300, 50)

    btn_pausa = pygame.Rect(LARGURA_VIRTUAL - 55, 15, 40, 40)
    btn_continuar = pygame.Rect(75, 530, 300, 50)
    btn_menu_pausa = pygame.Rect(75, 600, 300, 50)

    # UI Configurações
    btn_musica_menos = pygame.Rect(75, 180, 60, 45)
    btn_musica_mais = pygame.Rect(315, 180, 60, 45)
    btn_sfx_menos = pygame.Rect(75, 275, 60, 45)
    btn_sfx_mais = pygame.Rect(315, 275, 60, 45)
    btn_vibracao = pygame.Rect(75, 370, 300, 50)
    btn_lang = pygame.Rect(75, 445, 300, 50)
    btn_voltar_config = pygame.Rect(75, 580, 300, 50)

    def reiniciar_jogo():
        nonlocal jogador, pontuacao, moedas_coletadas, novo_recorde_alcançado, missoes_atuais, cor_atual_ceu, tempo_spawn_atual, estado
        # Mate os sprites, em vez de apenas esvaziar os grupos. Moedas e
        # particulas devolvem-se assim aos seus pools para serem reutilizadas
        # nas partidas seguintes, sem acumular objetos abandonados.
        for grupo in (todos_sprites, obstaculos, perigos_especiais, moedas, powerups, textos_flut, particulas):
            for sprite_antigo in grupo.sprites():
                sprite_antigo.kill()
        todos_sprites.empty()
        obstaculos.empty()
        perigos_especiais.empty()
        moedas.empty()
        powerups.empty()
        textos_flut.empty()
        particulas.empty()

        skin_nome_atual = dados["skin_equipada"]
        cor_jogador = SKINS.get(skin_nome_atual, SKINS["AZUL"])["cor"]
        jogador = Jogador(skin_nome_atual, cor_jogador, dados["upgrades"])
        todos_sprites.add(jogador)

        pontuacao = 0
        moedas_coletadas = 0
        novo_recorde_alcançado = False
        missoes_atuais = gerar_missoes_rodada()
        cor_atual_ceu = list(COR_DIA)
        tempo_spawn_atual = 1500
        pygame.time.set_timer(EVENTO_GERAR, tempo_spawn_atual)
        estado = "JOGANDO"

    def processar_clique_ui(pos):
        nonlocal estado, ultimo_clique_tempo
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - ultimo_clique_tempo < 300:
            return
        ultimo_clique_tempo = tempo_atual

        gerenciador_sons.tocar_som("clique", False, dados["vol_sfx"])
        if estado == "INICIO":
            if btn_jogar.collidepoint(pos):
                reiniciar_jogo()
            elif btn_loja.collidepoint(pos):
                estado = "LOJA"
            elif btn_upgrades.collidepoint(pos):
                estado = "UPGRADES"
            elif btn_config.collidepoint(pos):
                estado = "CONFIG"

        elif estado == "CONFIG":
            if btn_voltar_config.collidepoint(pos):
                salvar_dados(dados)
                estado = "INICIO"
            elif btn_musica_menos.collidepoint(pos):
                dados["vol_musica"] = max(0.0, round(dados["vol_musica"] - 0.1, 1))
                gerenciador_sons.atualizar_musica(estado, False, dados["vol_musica"])
                salvar_dados(dados)
            elif btn_musica_mais.collidepoint(pos):
                dados["vol_musica"] = min(1.0, round(dados["vol_musica"] + 0.1, 1))
                gerenciador_sons.atualizar_musica(estado, False, dados["vol_musica"])
                salvar_dados(dados)
            elif btn_sfx_menos.collidepoint(pos):
                dados["vol_sfx"] = max(0.0, round(dados["vol_sfx"] - 0.1, 1))
                salvar_dados(dados)
            elif btn_sfx_mais.collidepoint(pos):
                dados["vol_sfx"] = min(1.0, round(dados["vol_sfx"] + 0.1, 1))
                salvar_dados(dados)
            elif btn_vibracao.collidepoint(pos):
                dados["vibracao"] = not dados.get("vibracao", True)
                disparar_vibracao(0.15, dados["vibracao"])
                salvar_dados(dados)
            elif btn_lang.collidepoint(pos):
                dados["idioma"] = "pt_BR" if dados.get("idioma") == "en_US" else "en_US"
                salvar_dados(dados)

        elif estado == "JOGANDO":
            if btn_pausa.collidepoint(pos):
                estado = "PAUSA"

        elif estado == "PAUSA":
            if btn_continuar.collidepoint(pos):
                estado = "JOGANDO"
            elif btn_menu_pausa.collidepoint(pos):
                estado = "INICIO"

        elif estado == "GAMEOVER":
            if btn_reiniciar.collidepoint(pos):
                reiniciar_jogo()
            elif btn_menu_gameover.collidepoint(pos):
                estado = "INICIO"

        elif estado in ["LOJA", "UPGRADES"]:
            if btn_voltar.collidepoint(pos):
                estado = "INICIO"
            else:
                y_base = 135 if estado == "LOJA" else 125
                if estado == "LOJA":
                    for nome, info in SKINS.items():
                        rect_item = pygame.Rect(40, y_base, 370, 68)
                        if rect_item.collidepoint(pos):
                            if nome in dados["skins_desbloqueadas"]:
                                dados["skin_equipada"] = nome
                                salvar_dados(dados)
                            elif dados["moedas_totais"] >= info["preco"]:
                                dados["moedas_totais"] -= info["preco"]
                                dados["skins_desbloqueadas"].append(nome)
                                dados["skin_equipada"] = nome
                                salvar_dados(dados)
                        y_base += 78
                elif estado == "UPGRADES":
                    for chave, conf in UPGRADES_CONFIG.items():
                        rect_item = pygame.Rect(40, y_base, 370, 62)
                        if rect_item.collidepoint(pos):
                            nivel_atual = dados["upgrades"].get(chave, 0)
                            if nivel_atual < conf["max_nivel"]:
                                custo = conf["preco_base"] + (nivel_atual * conf["preco_multiplicador"])
                                if dados["moedas_totais"] >= custo:
                                    dados["moedas_totais"] -= custo
                                    dados["upgrades"][chave] = nivel_atual + 1
                                    salvar_dados(dados)
                        y_base += 70

    def atualizar_simulacao():
        nonlocal frame_count, pontuacao, moedas_coletadas, novo_recorde_alcançado, estado
        nonlocal anim_menu_tempo, metros_atuais, e_slow, cor_jogador, e_noite, alvo_ceu, cor_ceu_tupla, shake_timer

        frame_count += 1
        if shake_timer > 0:
            shake_timer -= 1
        if estado in ["INICIO", "LOJA", "UPGRADES", "CONFIG"]:
            anim_menu_tempo = min(45, anim_menu_tempo + 1)
        skin_nome_atual = dados["skin_equipada"]
        cor_jogador = SKINS.get(skin_nome_atual, SKINS["AZUL"])["cor"]
        metros_atuais = pontuacao // 10
        e_slow = (jogador.tempo_slow > 0) if jogador else False
        e_noite = (metros_atuais >= 500 and (metros_atuais // 300) % 2 == 1)
        alvo_ceu = COR_NOITE if e_noite else COR_DIA
        for i in range(3):
            if cor_atual_ceu[i] < alvo_ceu[i]:
                cor_atual_ceu[i] = min(cor_atual_ceu[i] + 1.2, alvo_ceu[i])
            elif cor_atual_ceu[i] > alvo_ceu[i]:
                cor_atual_ceu[i] = max(cor_atual_ceu[i] - 1.2, alvo_ceu[i])
        cor_ceu_tupla = (int(cor_atual_ceu[0]), int(cor_atual_ceu[1]), int(cor_atual_ceu[2]))

        if estado == "JOGANDO":
            vel_base = min(20.0, 6.0 + (metros_atuais / 35.0) * 0.35)
            if jogador.tempo_slow > 0:
                vel_jogo = vel_base * 0.5
            elif jogador.tempo_turbo > 0:
                vel_jogo = vel_base + 8.0
            else:
                vel_jogo = vel_base

            if not jogador.morrendo:
                pontuacao += 2 if jogador.tempo_mult > 0 else 1

                if jogador.tempo_ima > 0 and frame_count % 18 == 0:
                    gerenciador_sons.tocar_som("eletricidade", e_slow, dados["vol_sfx"])
                if jogador.tempo_turbo > 0 and frame_count % 12 == 0:
                    gerenciador_sons.tocar_som("chamas", e_slow, dados["vol_sfx"])

            bg_parallax.update(vel_jogo)

            segurando_pulo = input_pulo_ativo or input_mouse_ativo or (
                toque_ativo and not segurando_baixo_touch)
            segurando_baixo = input_baixo_ativo or segurando_baixo_touch

            prev_slow = jogador.tempo_slow
            prev_turbo = jogador.tempo_turbo

            jogador.update(vel_jogo, frame_count, segurando_pulo, segurando_baixo, particulas, pool_manager,
                           gerenciador_sons, dados["vol_sfx"])

            if (prev_slow > 0 and jogador.tempo_slow == 0) or (prev_turbo > 0 and jogador.tempo_turbo == 0):
                aplicar_shake(20, 10)
                textos_flut.add(
                    TextoFlutuante(LARGURA_VIRTUAL // 2, ALTURA_VIRTUAL // 2, t("limpeza_total", dados), AMARELO_NEON,
                                   "grande"))
                for obs in list(obstaculos):
                    criar_explosao_particulas(obs.rect.centerx, obs.rect.centery, VERDE_CACTO, 15, particulas,
                                              pool_manager)
                    obs.kill()
                for perigo in list(perigos_especiais):
                    perigo.kill()

            if jogador.tempo_turbo > 0 and not jogador.morrendo:
                if frame_count % 2 == 0:
                    criar_rastro_turbo(jogador.rect.left, jogador.rect.centery + random.randint(-10, 10), particulas,
                                       pool_manager)

            for m in missoes_atuais:
                if m["tipo"] == "DISTANCIA":
                    m["atual"] = metros_atuais
                elif m["tipo"] == "PULOS":
                    m["atual"] = jogador.pulos_na_rodada
                elif m["tipo"] == "POWERUPS":
                    m["atual"] = jogador.powerups_coletados
                elif m["tipo"] == "SLOW":
                    m["atual"] = jogador.slow_ativados

            for s in todos_sprites.sprites():
                if s != jogador:
                    if isinstance(s, Moeda):
                        s.update(vel_jogo, jogador)
                    elif isinstance(s, ObstaculoVoador):
                        s.update(vel_jogo, e_noite, e_slow)
                    elif isinstance(s, ObstaculoPulaPula):
                        s.update(vel_jogo, e_slow)
                    elif isinstance(s, AvisoLaser):
                        s.update(vel_jogo, gerenciador_sons, e_slow, dados["vol_sfx"])
                    else:
                        s.update(vel_jogo)

            textos_flut.update()
            particulas.update()

            if not jogador.morrendo:
                hitbox_jogador = jogador.obter_hitbox()

                for m in list(moedas):
                    if hitbox_jogador.colliderect(m.rect):
                        m.ativo = False
                        m.kill()
                        moedas_coletadas += (2 if jogador.tempo_mult > 0 else 1)
                        gerenciador_sons.tocar_som("moeda", jogador.tempo_slow > 0, dados["vol_sfx"])
                        criar_explosao_particulas(m.rect.centerx, m.rect.centery, AMARELO_MOEDA, 10, particulas,
                                                  pool_manager)
                        for missao in missoes_atuais:
                            if missao["tipo"] == "MOEDAS": missao["atual"] += 1

                for p in list(powerups):
                    if hitbox_jogador.colliderect(p.rect):
                        p.kill()
                        jogador.ativar_powerup(p.tipo, gerenciador_sons, dados["vol_sfx"], dados.get("vibracao", True))
                        nome_p = t(UPGRADES_CONFIG[p.tipo]["nome_key"], dados)
                        textos_flut.add(TextoFlutuante(jogador.rect.centerx, jogador.rect.top - 15, f"+ {nome_p}!",
                                                       UPGRADES_CONFIG[p.tipo]["cor"]))

                hit_obs = [obs for obs in obstaculos if hitbox_jogador.colliderect(obs.rect)]
                hit_laser = [l for l in perigos_especiais if
                             hasattr(l, 'ativo') and l.ativo and hitbox_jogador.colliderect(l.rect)]
                todos_hits = hit_obs + hit_laser

                if todos_hits:
                    if jogador.tempo_turbo > 0:
                        for h in hit_obs:
                            criar_explosao_particulas(h.rect.centerx, h.rect.centery, VERDE_CACTO, 16, particulas,
                                                      pool_manager)
                            h.kill()
                            gerenciador_sons.tocar_som("quebrar", jogador.tempo_slow > 0, dados["vol_sfx"])
                            aplicar_shake(10, 5)
                            cactos_destruidos = getattr(h, 'qtd_cactos', 1)
                            for missao in missoes_atuais:
                                if missao["tipo"] == "QUEBRAR": missao["atual"] += cactos_destruidos
                    elif jogador.escudo_hits > 0:
                        jogador.escudo_hits -= 1
                        disparar_vibracao(0.3, dados.get("vibracao", True))  # Vibração de quebra de escudo
                        textos_flut.add(TextoFlutuante(jogador.rect.centerx, jogador.rect.top - 20,
                                                       f"-1 {t('escudo_ativo', dados)}", CIANO_ESCUDO, "grande"))
                        aplicar_shake(15, 8)
                        gerenciador_sons.tocar_som("quebrar", jogador.tempo_slow > 0, dados["vol_sfx"])
                        for h in hit_obs:
                            criar_explosao_particulas(h.rect.centerx, h.rect.centery, VERDE_CACTO, 16, particulas,
                                                      pool_manager)
                            h.kill()
                            cactos_destruidos = getattr(h, 'qtd_cactos', 1)
                            for missao in missoes_atuais:
                                if missao["tipo"] == "QUEBRAR": missao["atual"] += cactos_destruidos
                        for h in hit_laser: h.kill()
                    else:
                        disparar_vibracao(0.5, dados.get("vibracao", True))  # Vibração de colisão / game over
                        aplicar_shake(25, 15)
                        criar_explosao_particulas(jogador.rect.centerx, jogador.rect.centery, cor_jogador, 30,
                                                  particulas, pool_manager)
                        jogador.iniciar_morte()
            else:
                if jogador.tempo_morte <= 0 or jogador.rect.top > ALTURA_VIRTUAL:
                    if estado != "GAMEOVER":
                        estado = "GAMEOVER"
                        dados["moedas_totais"] += moedas_coletadas
                        if metros_atuais > dados["recorde"]:
                            dados["recorde"] = metros_atuais
                            novo_recorde_alcançado = True
                            gerenciador_sons.tocar_som("novo_recorde", False, dados["vol_sfx"])
                        else:
                            gerenciador_sons.tocar_som("gameover", False, dados["vol_sfx"])
                        salvar_dados(dados)
                        pygame.time.set_timer(EVENTO_GERAR, 0)

            for m in missoes_atuais:
                if not m["concluida"] and m["atual"] >= m["alvo"]:
                    m["concluida"] = True
                    dados["moedas_totais"] += m["recompensa"]
                    gerenciador_sons.tocar_som("missao", False, dados["vol_sfx"])
                    textos_flut.add(
                        TextoFlutuante(LARGURA_VIRTUAL // 2, 250, t("missao_completa", dados), AMARELO_MOEDA, "grande"))
                    textos_flut.add(
                        TextoFlutuante(LARGURA_VIRTUAL // 2, 280, f"+{m['recompensa']} {t('moedas_hud', dados)}",
                                       BRANCO))
        elif estado in ["INICIO", "LOJA", "UPGRADES", "CONFIG"]:
            bg_parallax.update(1.2)

    # A simulacao usa passo fixo de 60 Hz; a imagem e renderizada separadamente.
    PASSO_FIXO = 1.0 / 60.0
    MAX_TEMPO_ACUMULADO = 0.25
    MAX_PASSOS_POR_FRAME = 15
    sim_acumulado = 0.0
    ultimo_tempo_loop_ms = pygame.time.get_ticks()

    rodando = True
    while rodando:
        agora_loop_ms = pygame.time.get_ticks()
        tempo_decorrido = max(0.0, min((agora_loop_ms - ultimo_tempo_loop_ms) / 1000.0,
                                      MAX_TEMPO_ACUMULADO))
        ultimo_tempo_loop_ms = agora_loop_ms
        sim_acumulado = min(sim_acumulado + tempo_decorrido, MAX_TEMPO_ACUMULADO)

        largura_atual_tela, altura_atual_tela = tela.get_size()

        if E_ANDROID:
            largura_render = largura_atual_tela
            altura_render = altura_atual_tela
            offset_x = 0
            offset_y = 0
        else:
            escala = min(largura_atual_tela / LARGURA_VIRTUAL, altura_atual_tela / ALTURA_VIRTUAL)
            largura_render = int(LARGURA_VIRTUAL * escala)
            altura_render = int(ALTURA_VIRTUAL * escala)
            offset_x = (largura_atual_tela - largura_render) // 2
            offset_y = (altura_atual_tela - altura_render) // 2

        def screen_to_virtual(px, py):
            if E_ANDROID:
                vx = (px / largura_atual_tela) * LARGURA_VIRTUAL
                vy = (py / altura_atual_tela) * ALTURA_VIRTUAL
                return int(vx), int(vy)
            else:
                vx = (px - offset_x) / (largura_render / LARGURA_VIRTUAL)
                vy = (py - offset_y) / (altura_render / ALTURA_VIRTUAL)
                return int(vx), int(vy)

        if estado != estado_anterior:
            if estado in ["INICIO", "LOJA", "UPGRADES", "CONFIG"]:
                anim_menu_tempo = 0
            # Invalida cenas congeladas ao entrar/sair de qualquer estado.
            cache_telas_estaticas.clear()
            estado_anterior = estado

        skin_nome_atual = dados["skin_equipada"]
        cor_jogador = SKINS.get(skin_nome_atual, SKINS["AZUL"])["cor"]
        metros_atuais = pontuacao // 10

        e_slow = (jogador.tempo_slow > 0) if jogador else False
        gerenciador_sons.atualizar_musica(estado, e_slow, dados["vol_musica"])

        if estado == "JOGANDO":
            novo_tempo_spawn = max(750, 1500 - (metros_atuais // 100) * 50)
            if novo_tempo_spawn != tempo_spawn_atual:
                tempo_spawn_atual = novo_tempo_spawn
                pygame.time.set_timer(EVENTO_GERAR, tempo_spawn_atual)

        e_noite = (metros_atuais >= 500 and (metros_atuais // 300) % 2 == 1)
        alvo_ceu = COR_NOITE if e_noite else COR_DIA

        cor_ceu_tupla = (int(cor_atual_ceu[0]), int(cor_atual_ceu[1]), int(cor_atual_ceu[2]))

        # Executa os ticks acumulados antes de aplicar os eventos recem-chegados,
        # para nao aplicar um toque novo retroativamente ao tempo anterior.
        passos_simulacao = 0
        while sim_acumulado + 1e-9 >= PASSO_FIXO and passos_simulacao < MAX_PASSOS_POR_FRAME and rodando:
            atualizar_simulacao()
            sim_acumulado -= PASSO_FIXO
            passos_simulacao += 1

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if (APP_WILLENTERBACKGROUND and evento.type == APP_WILLENTERBACKGROUND) or \
                    (APP_DIDENTERBACKGROUND and evento.type == APP_DIDENTERBACKGROUND) or \
                    (evento.type == pygame.ACTIVEEVENT and hasattr(evento, 'gain') and evento.gain == 0):
                if estado == "JOGANDO":
                    estado = "PAUSA"
                salvar_dados(dados)
                if gerenciador_sons and gerenciador_sons.canal_musica:
                    try:
                        gerenciador_sons.canal_musica.pause()
                    except Exception:
                        pass

            elif (APP_WILLENTERFOREGROUND and evento.type == APP_WILLENTERFOREGROUND) or \
                    (APP_DIDENTERFOREGROUND and evento.type == APP_DIDENTERFOREGROUND) or \
                    (evento.type == pygame.ACTIVEEVENT and hasattr(evento, 'gain') and evento.gain == 1):
                if gerenciador_sons and gerenciador_sons.canal_musica and estado in ["JOGANDO", "PAUSA", "INICIO",
                                                                                     "CONFIG", "LOJA", "UPGRADES"]:
                    try:
                        gerenciador_sons.canal_musica.unpause()
                    except Exception:
                        pass

            elif evento.type == pygame.FINGERDOWN:
                if E_ANDROID:
                    pos_touch = (evento.x * LARGURA_VIRTUAL, evento.y * ALTURA_VIRTUAL)
                else:
                    px = evento.x * largura_atual_tela
                    py = evento.y * altura_atual_tela
                    pos_touch = screen_to_virtual(px, py)

                touch_start_pos = pos_touch
                touch_current_pos = pos_touch
                toque_ativo = True

                if estado == "JOGANDO" and jogador:
                    if btn_pausa.collidepoint(pos_touch):
                        processar_clique_ui(pos_touch)

            elif evento.type == pygame.FINGERMOTION:
                if toque_ativo:
                    if E_ANDROID:
                        touch_current_pos = (evento.x * LARGURA_VIRTUAL, evento.y * ALTURA_VIRTUAL)
                    else:
                        px = evento.x * largura_atual_tela
                        py = evento.y * altura_atual_tela
                        touch_current_pos = screen_to_virtual(px, py)

            elif evento.type == pygame.FINGERUP:
                toque_ativo = False
                if touch_start_pos and jogador:
                    if E_ANDROID:
                        end_x = evento.x * LARGURA_VIRTUAL
                        end_y = evento.y * ALTURA_VIRTUAL
                    else:
                        px = evento.x * largura_atual_tela
                        py = evento.y * altura_atual_tela
                        end_x, end_y = screen_to_virtual(px, py)

                    dy = end_y - touch_start_pos[1]
                    dx = end_x - touch_start_pos[0]

                    if estado == "JOGANDO" and not btn_pausa.collidepoint(touch_start_pos):
                        if dy < -40:
                            jogador.pular(gerenciador_sons, dados["vol_sfx"])
                        elif dy > 40:
                            jogador.iniciar_descida_rapida(gerenciador_sons, dados["vol_sfx"])
                        elif abs(dx) < 30 and abs(dy) < 30:
                            jogador.pular(gerenciador_sons, dados["vol_sfx"])
                    else:
                        if abs(dx) < 30 and abs(dy) < 30:
                            processar_clique_ui((end_x, end_y))
                elif touch_start_pos and estado != "JOGANDO":
                    if E_ANDROID:
                        end_x = evento.x * LARGURA_VIRTUAL
                        end_y = evento.y * ALTURA_VIRTUAL
                    else:
                        px = evento.x * largura_atual_tela
                        py = evento.y * altura_atual_tela
                        end_x, end_y = screen_to_virtual(px, py)
                    processar_clique_ui((end_x, end_y))

                touch_start_pos = None
                touch_current_pos = None

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if not touch_start_pos:
                    vx, vy = screen_to_virtual(evento.pos[0], evento.pos[1])
                    if estado == "JOGANDO" and jogador and not btn_pausa.collidepoint((vx, vy)):
                        jogador.pular(gerenciador_sons, dados["vol_sfx"])
                    else:
                        processar_clique_ui((vx, vy))

            elif evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_p, pygame.K_ESCAPE, getattr(pygame, "K_AC_BACK", pygame.K_ESCAPE)):
                    if estado == "JOGANDO":
                        estado = "PAUSA"
                    elif estado == "PAUSA":
                        estado = "JOGANDO"
                    elif estado in ["LOJA", "UPGRADES", "CONFIG"]:
                        estado = "INICIO"

                if jogador and estado == "JOGANDO":
                    if evento.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        jogador.pular(gerenciador_sons, dados["vol_sfx"])

            if evento.type == EVENTO_GERAR and estado == "JOGANDO":
                gerar_padrao(todos_sprites, obstaculos, perigos_especiais, moedas, powerups, metros_atuais,
                             pool_manager)

        # Guarda o estado atual dos controles para os proximos ticks fixos.
        teclas_atuais = pygame.key.get_pressed()
        botoes_mouse_atuais = pygame.mouse.get_pressed()
        input_pulo_ativo = bool(teclas_atuais[pygame.K_SPACE] or teclas_atuais[pygame.K_UP] or
                                teclas_atuais[pygame.K_w])
        input_baixo_ativo = bool(teclas_atuais[pygame.K_DOWN] or teclas_atuais[pygame.K_s])
        input_mouse_ativo = bool(botoes_mouse_atuais[0])
        segurando_baixo_touch = False
        if toque_ativo and touch_start_pos and touch_current_pos:
            dy = touch_current_pos[1] - touch_start_pos[1]
            if dy > 30:
                segurando_baixo_touch = True

        # A renderizacao acontece uma vez por frame visivel, independentemente dos ticks executados.

        # Pausa e Game Over congelam o mundo. Depois do fim da transição de céu,
        # reutilizamos a imagem pronta em vez de redesenhar o fundo, sprites e UI.
        chave_tela_estatica = (estado, cor_ceu_tupla)
        if estado in ("PAUSA", "GAMEOVER") and chave_tela_estatica in cache_telas_estaticas:
            display_surface.blit(cache_telas_estaticas[chave_tela_estatica], (0, 0))
        else:
            # --- RENDERIZAÇÃO NA TELA VIRTUAL ---
            # Todas as telas chamam bg_parallax.draw(), que já preenche o céu;
            # evitamos um segundo fill da superfície completa em todos os frames.
            if estado in ["JOGANDO", "PAUSA", "GAMEOVER"]:
                bg_parallax.draw(display_surface, cor_ceu_tupla, e_noite)
                pygame.draw.rect(display_surface, CINZA_CHAO, (0, ALTURA_VIRTUAL - 70, LARGURA_VIRTUAL, 70))
                pygame.draw.rect(display_surface, VERDE_GRAMA, (0, ALTURA_VIRTUAL - 70, LARGURA_VIRTUAL, 10))

                if jogador is not None and estado in ("JOGANDO", "PAUSA", "GAMEOVER"):
                    jogador.renderizar_visual(frame_count)
                for sprite_visual in todos_sprites:
                    if isinstance(sprite_visual, ObstaculoVoador):
                        sprite_visual.renderizar_visual()

                todos_sprites.draw(display_surface)
                particulas.draw(display_surface)
                textos_flut.draw(display_surface)

                if jogador and jogador.tempo_slow > 0 and estado in ["JOGANDO", "PAUSA"]:
                    display_surface.blit(OVERLAY_SLOW, (0, 0))

                for perigo in perigos_especiais:
                    if isinstance(perigo, AvisoLaser) and perigo.timer > 0:
                        seg_restantes = (perigo.timer / 60.0)
                        if jogador and not jogador.morrendo:
                            txt_alerta = f"⚠️ ATENÇÃO: LASER EM {seg_restantes:.1f}s! ⚠️"
                            pos_y_alerta = max(10, perigo.rect.y - 28)
                            desenhar_texto_centralizado(display_surface, txt_alerta, fonte_alerta, VERMELHO_OBSTACULO,
                                                        AMARELO_NEON, pos_y_alerta)

                if jogador and jogador.escudo_hits > 0 and estado in ["JOGANDO", "PAUSA"] and not jogador.morrendo:
                    pygame.draw.circle(display_surface, CIANO_ESCUDO, jogador.rect.center, 42, 3)

                    bar_w = 50
                    bar_h = 7
                    bar_x = jogador.rect.centerx - bar_w // 2
                    bar_y = jogador.rect.top - 24

                    pygame.draw.rect(display_surface, CINZA_PAINEL, (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2),
                                     border_radius=4)
                    max_hits = max(1, jogador.escudo_max)
                    pct_escudo = jogador.escudo_hits / float(max_hits)
                    w_preenchido = int(bar_w * pct_escudo)
                    if w_preenchido > 0:
                        pygame.draw.rect(display_surface, CIANO_ESCUDO, (bar_x, bar_y, w_preenchido, bar_h),
                                         border_radius=3)
                    pygame.draw.rect(display_surface, BRANCO, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)

                    surf_esc_num = render_texto_cacheado(fonte_pequena, f"{jogador.escudo_hits}/{max_hits}", BRANCO)
                    display_surface.blit(surf_esc_num, (jogador.rect.centerx - surf_esc_num.get_width() // 2, bar_y - 14))

            if estado == "JOGANDO":
                rect_hud = pygame.Rect(15, 15, 190, 68)
                pygame.draw.rect(display_surface, (20, 20, 30, 220), rect_hud, border_radius=12)
                pygame.draw.rect(display_surface, CIANO_ESCUDO, rect_hud, 2, border_radius=12)

                desenhar_texto_com_sombra(display_surface, f"{metros_atuais} {t('m_unit', dados)}", fonte_grande,
                                          AMARELO_NEON, PRETO, (25, 20))
                desenhar_texto_com_sombra(display_surface, f"{t('moedas_hud', dados)}: {moedas_coletadas}", fonte,
                                          AMARELO_NEON, PRETO, (25, 52))

                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_pausa, border_radius=8)
                pygame.draw.rect(display_surface, BRANCO, btn_pausa, 2, border_radius=8)
                pygame.draw.rect(display_surface, BRANCO, (LARGURA_VIRTUAL - 45, 23, 6, 24))
                pygame.draw.rect(display_surface, BRANCO, (LARGURA_VIRTUAL - 33, 23, 6, 24))

                rect_missoes_hud = pygame.Rect(15, 90, 240, 115)
                pygame.draw.rect(display_surface, (20, 20, 30, 200), rect_missoes_hud, border_radius=10)
                pygame.draw.rect(display_surface, CIANO_ESCUDO, rect_missoes_hud, 1, border_radius=10)

                desenhar_texto_com_sombra(display_surface, t("missoes_partida", dados), fonte_missoes, AMARELO_NEON, PRETO,
                                          (22, 96))

                y_m = 120
                for m in missoes_atuais:
                    txt_m = t(m["key"], dados).format(m["alvo"])
                    st = "OK!" if m["concluida"] else f"{m['atual']}/{m['alvo']}"
                    cor_m = VERDE_SLOW if m["concluida"] else BRANCO
                    desenhar_texto_com_sombra(display_surface, f"• {txt_m} ({st})", fonte_missoes, cor_m, PRETO, (22, y_m))
                    y_m += 25

                py_pup = 212
                for pup_key, pup_conf in UPGRADES_CONFIG.items():
                    tempo_restante = 0
                    if pup_key == "IMA":
                        tempo_restante = jogador.tempo_ima
                    elif pup_key == "TURBO":
                        tempo_restante = jogador.tempo_turbo
                    elif pup_key == "MULT_2X":
                        tempo_restante = jogador.tempo_mult
                    elif pup_key == "SLOW":
                        tempo_restante = jogador.tempo_slow

                    if tempo_restante > 0:
                        dur_max = pup_conf["duracao_base"] + (
                                    dados["upgrades"].get(pup_key, 0) * pup_conf["bonus_por_nivel"])
                        pct = tempo_restante / float(dur_max)
                        pygame.draw.rect(display_surface, CINZA_PAINEL, (15, py_pup, 130, 20), border_radius=5)
                        pygame.draw.rect(display_surface, pup_conf["cor"], (15, py_pup, int(130 * pct), 20),
                                         border_radius=5)
                        pygame.draw.rect(display_surface, BRANCO, (15, py_pup, 130, 20), 1, border_radius=5)
                        desenhar_icone_powerup(display_surface, pup_key, 27, py_pup + 10)
                        py_pup += 25

            if estado == "INICIO":
                t_anim = anim_menu_tempo / 45.0
                ease_out = 1.0 - (1.0 - t_anim) ** 3

                bg_parallax.draw(display_surface, cor_ceu_tupla, False)

                offset_y_titulo = int((1.0 - ease_out) * -220)
                float_y = math.sin(frame_count * 0.05) * 4
                pos_y_titulo = 95 + offset_y_titulo + float_y
                desenhar_titulo_pixel_art(display_surface, LARGURA_VIRTUAL // 2, pos_y_titulo, frame_count)

                card1_x = 35 - int((1.0 - ease_out) * 320)
                card2_x = 240 + int((1.0 - ease_out) * 320)
                card_y = 210

                rect_c1 = pygame.Rect(card1_x, card_y, 175, 70)
                pygame.draw.rect(display_surface, CINZA_PAINEL, rect_c1, border_radius=12)
                pygame.draw.rect(display_surface, AMARELO_NEON, rect_c1, 2, border_radius=12)
                desenhar_texto_com_sombra(display_surface, t("recorde", dados), fonte_pequena, AMARELO_NEON, PRETO,
                                          (card1_x + 15, card_y + 12))
                desenhar_texto_com_sombra(display_surface, f"{dados['recorde']} {t('m_unit', dados)}", fonte_grande, BRANCO,
                                          PRETO, (card1_x + 15, card_y + 30))

                rect_c2 = pygame.Rect(card2_x, card_y, 175, 70)
                pygame.draw.rect(display_surface, CINZA_PAINEL, rect_c2, border_radius=12)
                pygame.draw.rect(display_surface, AMARELO_MOEDA, rect_c2, 2, border_radius=12)
                desenhar_texto_com_sombra(display_surface, t("moedas_banco", dados), fonte_pequena, AMARELO_MOEDA, PRETO,
                                          (card2_x + 15, card_y + 12))
                desenhar_texto_com_sombra(display_surface, f"{dados['moedas_totais']}", fonte_grande, BRANCO, PRETO,
                                          (card2_x + 15, card_y + 30))

                botoes_menu = [
                    (btn_jogar, t("jogar", dados), (46, 204, 113)),
                    (btn_loja, t("loja_skins", dados), (52, 152, 219)),
                    (btn_upgrades, t("loja_upgrades", dados), (155, 89, 182)),
                    (btn_config, t("configuracoes", dados), (241, 196, 15))
                ]

                for idx, (btn_rect, texto_btn, cor_btn) in enumerate(botoes_menu):
                    t_btn = max(0.0, min(1.0, (anim_menu_tempo - idx * 4) / 28.0))
                    e_btn = 1.0 - (1.0 - t_btn) ** 3
                    offset_y = int((1.0 - e_btn) * 450)

                    rect_desenhado = btn_rect.move(0, offset_y)

                    pygame.draw.rect(display_surface, (30, 30, 40), rect_desenhado.move(0, 4), border_radius=12)
                    pygame.draw.rect(display_surface, cor_btn, rect_desenhado, border_radius=12)
                    pygame.draw.rect(display_surface, BRANCO, rect_desenhado, 2, border_radius=12)

                    surf_txt = render_texto_cacheado(fonte, texto_btn, PRETO if cor_btn == (241, 196, 15) else BRANCO)
                    display_surface.blit(surf_txt, (rect_desenhado.centerx - surf_txt.get_width() // 2,
                                                    rect_desenhado.centery - surf_txt.get_height() // 2))

                desenhar_texto_centralizado(display_surface, f"{VERSAO} - PIXEL RUSH", fonte_pequena, BRANCO, PRETO,
                                            ALTURA_VIRTUAL - 30)

            elif estado == "LOJA":
                t_anim = anim_menu_tempo / 35.0
                ease_out = 1.0 - (1.0 - t_anim) ** 3
                bg_parallax.draw(display_surface, cor_ceu_tupla, False)

                off_top = int((1.0 - ease_out) * -150)
                desenhar_texto_centralizado(display_surface, t("loja_skins", dados), fonte_grande, AMARELO_NEON, PRETO,
                                            40 + off_top)
                desenhar_texto_centralizado(display_surface, f"{t('moedas_hud', dados)}: {dados['moedas_totais']}", fonte,
                                            AMARELO_MOEDA, PRETO, 85 + off_top)

                y_base = 135
                for nome_skin, info in SKINS.items():
                    rect_item = pygame.Rect(40, y_base, 370, 68)
                    pygame.draw.rect(display_surface, CINZA_PAINEL, rect_item, border_radius=10)

                    sta_equipada = (dados["skin_equipada"] == nome_skin)
                    desbloqueada = (nome_skin in dados["skins_desbloqueadas"])

                    if sta_equipada:
                        cor_borda = VERDE_GRAMA
                    elif desbloqueada:
                        cor_borda = AZUL_IMA
                    else:
                        cor_borda = AMARELO_MOEDA

                    pygame.draw.rect(display_surface, cor_borda, rect_item, 2, border_radius=10)
                    desenhar_mini_skin(display_surface, nome_skin, 75, y_base + 34)

                    nome_str = t(info["nome_key"], dados)
                    desenhar_texto_com_sombra(display_surface, nome_str, fonte, BRANCO, PRETO, (115, y_base + 12))

                    if sta_equipada:
                        desenhar_texto_com_sombra(display_surface, t("equipada", dados), fonte_pequena, VERDE_GRAMA, PRETO,
                                                  (115, y_base + 38))
                    elif desbloqueada:
                        desenhar_texto_com_sombra(display_surface, t("equipar", dados), fonte_pequena, AZUL_IMA, PRETO,
                                                  (115, y_base + 38))
                    else:
                        desenhar_texto_com_sombra(display_surface, f"${info['preco']}", fonte_pequena, AMARELO_MOEDA, PRETO,
                                                  (115, y_base + 38))

                    y_base += 78

                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_voltar, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_voltar, 2, border_radius=10)
                surf_v = render_texto_cacheado(fonte, t("voltar_menu", dados), BRANCO)
                display_surface.blit(surf_v, (
                btn_voltar.centerx - surf_v.get_width() // 2, btn_voltar.centery - surf_v.get_height() // 2))

            elif estado == "UPGRADES":
                t_anim = anim_menu_tempo / 35.0
                ease_out = 1.0 - (1.0 - t_anim) ** 3
                bg_parallax.draw(display_surface, cor_ceu_tupla, False)

                off_top = int((1.0 - ease_out) * -150)
                desenhar_texto_centralizado(display_surface, t("loja_upgrades", dados), fonte_grande, AMARELO_NEON, PRETO,
                                            35 + off_top)
                desenhar_texto_centralizado(display_surface, f"{t('moedas_hud', dados)}: {dados['moedas_totais']}", fonte,
                                            AMARELO_MOEDA, PRETO, 80 + off_top)

                y_base = 125
                for chave, conf in UPGRADES_CONFIG.items():
                    rect_item = pygame.Rect(40, y_base, 370, 62)
                    pygame.draw.rect(display_surface, CINZA_PAINEL, rect_item, border_radius=10)
                    pygame.draw.rect(display_surface, conf["cor"], rect_item, 2, border_radius=10)

                    desenhar_icone_powerup(display_surface, chave, 65, y_base + 31)

                    nome_str = t(conf["nome_key"], dados)
                    desenhar_texto_com_sombra(display_surface, nome_str, fonte, BRANCO, PRETO, (95, y_base + 10))

                    nv_atual = dados["upgrades"].get(chave, 0)
                    max_nv = conf["max_nivel"]

                    for bx in range(max_nv):
                        cor_bar = conf["cor"] if bx < nv_atual else (70, 70, 80)
                        pygame.draw.rect(display_surface, cor_bar, (95 + bx * 18, y_base + 36, 14, 12), border_radius=2)
                        pygame.draw.rect(display_surface, BRANCO, (95 + bx * 18, y_base + 36, 14, 12), 1, border_radius=2)

                    if nv_atual >= max_nv:
                        desenhar_texto_com_sombra(display_surface, t("maximo", dados), fonte_pequena, VERDE_GRAMA, PRETO,
                                                  (270, y_base + 20))
                    else:
                        custo = conf["preco_base"] + (nv_atual * conf["preco_multiplicador"])
                        desenhar_texto_com_sombra(display_surface, f"${custo}", fonte_pequena, AMARELO_MOEDA, PRETO,
                                                  (270, y_base + 20))

                    y_base += 70

                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_voltar, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_voltar, 2, border_radius=10)
                surf_v = render_texto_cacheado(fonte, t("voltar_menu", dados), BRANCO)
                display_surface.blit(surf_v, (
                btn_voltar.centerx - surf_v.get_width() // 2, btn_voltar.centery - surf_v.get_height() // 2))

            elif estado == "CONFIG":
                t_anim = anim_menu_tempo / 35.0
                ease_out = 1.0 - (1.0 - t_anim) ** 3
                bg_parallax.draw(display_surface, cor_ceu_tupla, False)

                off_top = int((1.0 - ease_out) * -150)
                desenhar_texto_centralizado(display_surface, t("configuracoes", dados), fonte_grande, AMARELO_NEON, PRETO,
                                            35 + off_top)

                # Trilha Sonora
                desenhar_texto_com_sombra(display_surface, t("vol_musica", dados), fonte, BRANCO, PRETO, (75, 145))
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_musica_menos, border_radius=8)
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_musica_mais, border_radius=8)
                desenhar_texto_com_sombra(display_surface, "-", fonte_grande, BRANCO, PRETO,
                                          (btn_musica_menos.centerx - 6, btn_musica_menos.centery - 15))
                desenhar_texto_com_sombra(display_surface, "+", fonte_grande, BRANCO, PRETO,
                                          (btn_musica_mais.centerx - 8, btn_musica_mais.centery - 15))

                pct_m = int(dados["vol_musica"] * 100)
                pygame.draw.rect(display_surface, CINZA_PAINEL, (145, 180, 160, 45), border_radius=8)
                desenhar_texto_com_sombra(display_surface, f"{pct_m}%", fonte, AMARELO_NEON, PRETO, (205, 190))

                # Efeitos Sonoros
                desenhar_texto_com_sombra(display_surface, t("vol_sfx", dados), fonte, BRANCO, PRETO, (75, 240))
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_sfx_menos, border_radius=8)
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_sfx_mais, border_radius=8)
                desenhar_texto_com_sombra(display_surface, "-", fonte_grande, BRANCO, PRETO,
                                          (btn_sfx_menos.centerx - 6, btn_sfx_menos.centery - 15))
                desenhar_texto_com_sombra(display_surface, "+", fonte_grande, BRANCO, PRETO,
                                          (btn_sfx_mais.centerx - 8, btn_sfx_mais.centery - 15))

                pct_s = int(dados["vol_sfx"] * 100)
                pygame.draw.rect(display_surface, CINZA_PAINEL, (145, 275, 160, 45), border_radius=8)
                desenhar_texto_com_sombra(display_surface, f"{pct_s}%", fonte, AMARELO_NEON, PRETO, (205, 285))

                # Vibração (Ligado / Desligado)
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_vibracao, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_vibracao, 2, border_radius=10)
                vib_status = t("ligado", dados) if dados.get("vibracao", True) else t("desligado", dados)
                surf_vib = render_texto_cacheado(fonte, f"{t('vibracao', dados)}: {vib_status}", BRANCO)
                display_surface.blit(surf_vib, (
                btn_vibracao.centerx - surf_vib.get_width() // 2, btn_vibracao.centery - surf_vib.get_height() // 2))

                # Idioma
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_lang, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_lang, 2, border_radius=10)
                lang_str = "Português (BR)" if dados.get("idioma") == "pt_BR" else "English (US)"
                surf_l = render_texto_cacheado(fonte, f"{t('idioma', dados)}: {lang_str}", BRANCO)
                display_surface.blit(surf_l, (
                btn_lang.centerx - surf_l.get_width() // 2, btn_lang.centery - surf_l.get_height() // 2))

                # Salvar e Voltar
                pygame.draw.rect(display_surface, (46, 204, 113), btn_voltar_config, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_voltar_config, 2, border_radius=10)
                surf_voltar_config = render_texto_cacheado(fonte, t("salvar", dados), BRANCO)
                display_surface.blit(surf_voltar_config, (btn_voltar_config.centerx - surf_voltar_config.get_width() // 2,
                                                          btn_voltar_config.centery - surf_voltar_config.get_height() // 2))

            elif estado == "PAUSA":
                display_surface.blit(OVERLAY_PAUSA, (0, 0))

                desenhar_texto_centralizado(display_surface, t("pausa_titulo", dados), fonte_grande, AMARELO_NEON, PRETO,
                                            150)

                rect_pausa_box = pygame.Rect(45, 210, 360, 290)
                pygame.draw.rect(display_surface, CINZA_PAINEL, rect_pausa_box, border_radius=12)
                pygame.draw.rect(display_surface, CIANO_ESCUDO, rect_pausa_box, 2, border_radius=12)

                desenhar_texto_com_sombra(display_surface, t("estatisticas", dados), fonte, AMARELO_NEON, PRETO, (65, 225))
                desenhar_texto_com_sombra(display_surface, f"{t('distancia', dados)}: {metros_atuais} {t('m_unit', dados)}",
                                          fonte_pequena, BRANCO, PRETO, (65, 260))
                desenhar_texto_com_sombra(display_surface, f"{t('moedas_partida', dados)}: {moedas_coletadas}",
                                          fonte_pequena, AMARELO_MOEDA, PRETO, (65, 282))

                pygame.draw.line(display_surface, CINZA_BOTAO, (65, 308), (385, 308), 2)

                desenhar_texto_com_sombra(display_surface, t("missoes_partida", dados), fonte_missoes, CIANO_ESCUDO, PRETO,
                                          (65, 318))
                y_m = 345
                for m in missoes_atuais:
                    txt_m = t(m["key"], dados).format(m["alvo"])
                    st = "OK!" if m["concluida"] else f"{m['atual']}/{m['alvo']}"
                    cor_m = VERDE_SLOW if m["concluida"] else BRANCO
                    desenhar_texto_com_sombra(display_surface, f"• {txt_m} ({st})", fonte_missoes, cor_m, PRETO, (70, y_m))
                    y_m += 26

                pygame.draw.rect(display_surface, (46, 204, 113), btn_continuar, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_continuar, 2, border_radius=10)
                surf_c = render_texto_cacheado(fonte, t("continuar", dados), BRANCO)
                display_surface.blit(surf_c, (
                btn_continuar.centerx - surf_c.get_width() // 2, btn_continuar.centery - surf_c.get_height() // 2))

                pygame.draw.rect(display_surface, VERMELHO_OBSTACULO, btn_menu_pausa, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_menu_pausa, 2, border_radius=10)
                surf_menu_pausa = render_texto_cacheado(fonte, t("menu_principal", dados), BRANCO)
                display_surface.blit(surf_menu_pausa, (btn_menu_pausa.centerx - surf_menu_pausa.get_width() // 2,
                                                       btn_menu_pausa.centery - surf_menu_pausa.get_height() // 2))

            elif estado == "GAMEOVER":
                display_surface.blit(OVERLAY_GAMEOVER, (0, 0))

                txt_go = t("novo_recorde", dados) if novo_recorde_alcançado else t("gameover", dados)
                cor_go = AMARELO_NEON if novo_recorde_alcançado else VERMELHO_OBSTACULO
                desenhar_texto_centralizado(display_surface, txt_go, fonte_grande, cor_go, PRETO, 150)

                rect_stats = pygame.Rect(45, 210, 360, 290)
                pygame.draw.rect(display_surface, CINZA_PAINEL, rect_stats, border_radius=12)
                borda_go = AMARELO_NEON if novo_recorde_alcançado else VERMELHO_OBSTACULO
                pygame.draw.rect(display_surface, borda_go, rect_stats, 2, border_radius=12)

                desenhar_texto_com_sombra(display_surface, t("estatisticas", dados), fonte, AMARELO_NEON, PRETO, (65, 225))
                desenhar_texto_com_sombra(display_surface, f"{t('distancia', dados)}: {metros_atuais} {t('m_unit', dados)}",
                                          fonte, BRANCO, PRETO, (65, 260))
                desenhar_texto_com_sombra(display_surface, f"{t('moedas_partida', dados)}: {moedas_coletadas}", fonte,
                                          AMARELO_MOEDA, PRETO, (65, 290))

                pygame.draw.line(display_surface, CINZA_BOTAO, (65, 322), (385, 322), 2)

                desenhar_texto_com_sombra(display_surface, t("missoes_partida", dados), fonte_missoes, CIANO_ESCUDO, PRETO,
                                          (65, 330))
                y_m = 358
                for m in missoes_atuais:
                    txt_m = t(m["key"], dados).format(m["alvo"])
                    st = "OK!" if m["concluida"] else f"{m['atual']}/{m['alvo']}"
                    cor_m = VERDE_SLOW if m["concluida"] else BRANCO
                    desenhar_texto_com_sombra(display_surface, f"• {txt_m} ({st})", fonte_missoes, cor_m, PRETO, (70, y_m))
                    y_m += 26

                pygame.draw.rect(display_surface, (46, 204, 113), btn_reiniciar, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_reiniciar, 2, border_radius=10)
                surf_r = render_texto_cacheado(fonte, t("jogar_novamente", dados), BRANCO)
                display_surface.blit(surf_r, (
                btn_reiniciar.centerx - surf_r.get_width() // 2, btn_reiniciar.centery - surf_r.get_height() // 2))

                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_menu_gameover, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_menu_gameover, 2, border_radius=10)
                surf_mg = render_texto_cacheado(fonte, t("voltar_menu", dados), BRANCO)
                display_surface.blit(surf_mg, (btn_menu_gameover.centerx - surf_mg.get_width() // 2,
                                               btn_menu_gameover.centery - surf_mg.get_height() // 2))

            if estado in ("PAUSA", "GAMEOVER") and cor_ceu_tupla == tuple(alvo_ceu):
                cache_telas_estaticas[chave_tela_estatica] = display_surface.copy()

        ox, oy = 0, 0
        if shake_timer > 0:
            ox = random.randint(-shake_intensidade, shake_intensidade)
            oy = random.randint(-shake_intensidade, shake_intensidade)

        if E_ANDROID:
            tamanho_final = (LARGURA_TELA, ALTURA_TELA)
            pos_final = (ox, oy)
        else:
            tela.fill(cor_ceu_tupla)
            tamanho_final = (largura_render, altura_render)
            pos_final = (offset_x + ox, offset_y + oy)

        if tamanho_final == display_surface.get_size():
            superficie_final = display_surface
        else:
            superficie_final = superficies_escala.get(tamanho_final)
            if superficie_final is None:
                try:
                    superficie_final = pygame.Surface(tamanho_final).convert()
                except Exception:
                    superficie_final = pygame.Surface(tamanho_final)
                superficies_escala[tamanho_final] = superficie_final
            pygame.transform.scale(display_surface, tamanho_final, superficie_final)

        tela.blit(superficie_final, pos_final)
        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
