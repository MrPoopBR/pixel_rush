from pixelrush_repro_v3205 import (executar_com_repro as _rep_executar, iniciar_relogio as _rep_relogio, inicio_quadro as _rep_inicio, tempo as _rep_tempo, eventos as _rep_eventos, entradas as _rep_entradas, fim_quadro as _rep_fim)
from pixelrush_profiler_v3204 import (executar_com_profiler as _pro_executar, iniciar as _pro_inicio, marcar as _pro_marcar, sub_inicio as _pro_sub_inicio, sub_fim as _pro_sub_fim, fim as _pro_fim)
from pixelrush_forense_v3203 import executar_com_forense as _forense_executar, checkpoint as _forense_quadro, solicitar_saida as _forense_quit
import pygame
from pixelrush_i18n_v3246 import traduzir as _traduzir_v3246
import pixelrush_traducoes_v3247 as _i18n247
# Fonte CJK completa do dispositivo quando disponível, sem bundlar fontes novas.
from pixelrush_fontes_prod_v32771 import fonte_unicode as _fonte_unicode_prod
_i18n247.fonte_unicode = _fonte_unicode_prod
import random
import sys
import json
import os
# R11: marcadores QA isolados; em producao/DEV sao funcoes vazias.
if os.environ.get('PIXELRUSH_QA_ANDROID') == '1':
    _r11_sub_inicio = _pro_sub_inicio
    _r11_sub_fim = _pro_sub_fim
else:
    def _r11_sub_inicio(_nome): pass
    def _r11_sub_fim(): pass
import math
import array
import base64
import io
from datetime import date, timedelta
from collections import OrderedDict
from contextlib import nullcontext
from pygame.sprite import Sprite
from pixelrush_inimigos_v3221 import AMEACAS, POR_BIOMA, AmeacaBioma, escorpiao_frame, cor_aviso_ameaca
from pixelrush_hidrante_cidade_v3276 import HidranteCidade
from pixelrush_variantes_v3238 import ObstaculoMovel, escolher as escolher_movel
from pixelrush_reflexos_v3223 import DiretorReflexos, criar_reflexo
from pixelrush_aereo_v3224 import LaserJetpackAvancado, corredor_avancado, faixa_moeda_jetpack
from pixelrush_fase_b_visuais_v3276 import (desenhar_profundidade_bioma, desenhar_legibilidade_jetpack, desenhar_legibilidade_corredor, desenhar_alerta_moveis)
from pixelrush_rotas_v3225 import DiretorRotasBioma, formato_aberto, premiar_pos_perigo
from pixelrush_touch_v3229 import passos_jetpack, ancorar_jetpack
from pixelrush_visual_premium_v3127 import acabamento_legado
from pixelrush_spawn_v3152 import EspacamentoPorDistancia
from pixelrush_saves_v3253 import ler_save_protegido, salvar_save_protegido
import pixelrush_cenarios_v398 as visuais397
from pixelrush_ceu_v3233 import desenhar_gradiente as _ceu_gradiente_v3233
from pixelrush_world_prod_v32777 import LivingWorld
from pixelrush_luz_skins_v3184 import integrar_skin as _v3183_integrar_skin
from pixelrush_skins_v3188 import refinar_atlas as _v3188_refinar_atlas, escolher_quadro as _v3188_escolher_quadro
from pixelrush_contornos_v3230 import ContornosLegiveis
from pixelrush_diagnostico_v3154 import MonitorDiagnostico
from pixelrush_hud_v3133 import desenhar_hud_compacto, HUD_PAUSA_AREA
from pixelrush_percursos_v3140 import DiretorSequencias
from pixelrush_sequencias_v3206 import DiretorAutorais
from pixelrush_desafios_percurso_v3212 import DesafioPercurso, codigo_diario
from pixelrush_aprendizado_v3208 import AprendizadoContextual
from pixelrush_percursos_v3191 import AuditorVariedade
from pixelrush_profissional_v3108 import OclusaoAcustica2D
from pixelrush_fisica_audio_v3109 import ReverbConvolucional, esculpir_obstaculo, colide_sdf_com_rect
from pixelrush_audio_v3110 import criar_stems_pygame
from pixelrush_mixagem_v3209 import MixagemContextual
from pixelrush_moderngl_v3107 import GpuPostProcessor
from pixelrush_gamefeel_v3152 import GameFeel, criar_variantes_pitch, criar_camada_ritmica

# --- SUPORTE A VIBRAÇÃO (ANDROID / PLYER) ---
try:
    from plyer import vibrator

    SUPORTE_VIBRADOR = True
except Exception:
    SUPORTE_VIBRADOR = False


def disparar_vibracao(duracao=0.2, vibracao_ligada=True):
    """Dispara uma vibracao curta; no Android tenta primeiro a API nativa."""
    if not vibracao_ligada:
        return
    try:
        duracao = max(0.01, min(float(duracao), 2.0))
    except (TypeError, ValueError):
        duracao = 0.2

    # O Plyer pode estar instalado mas falhar silenciosamente em algumas builds.
    # PyJNIus acessa diretamente o servico Vibrator do Android.
    if E_ANDROID:
        try:
            import importlib
            autoclass = importlib.import_module("jnius").autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            BuildVersion = autoclass('android.os.Build$VERSION')
            atividade = PythonActivity.mActivity
            servico_vibracao = atividade.getSystemService(Context.VIBRATOR_SERVICE)
            if servico_vibracao is not None and servico_vibracao.hasVibrator():
                duracao_ms = int(duracao * 1000)
                if int(BuildVersion.SDK_INT) >= 26:
                    VibrationEffect = autoclass('android.os.VibrationEffect')
                    efeito = VibrationEffect.createOneShot(
                        duracao_ms, VibrationEffect.DEFAULT_AMPLITUDE
                    )
                    servico_vibracao.vibrate(efeito)
                else:
                    servico_vibracao.vibrate(duracao_ms)
                return
        except Exception:
            # Continua para o Plyer como alternativa.
            pass

    # Plyer não implementa vibração no Windows; evitar traceback em desktop.
    if SUPORTE_VIBRADOR and E_ANDROID:
        try:
            vibrator.vibrate(time=duracao)
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

# Histórico da versão do jogo
# v3.33.0: corrigida a descontinuidade da cabeca/corpo das nove skins.
# Animações agora usam rig 2D com cabeça fixa ao tronco, pernas com joelhos,
# botas e braços articulados: correr, pular, swipe-down, agachar e morte.
# Corrigida a antiga "animacao" que apenas deslocava fatias da imagem inteira.
# Novos quadros ficam em cache como antes; mantidas arte aprovada e identidade.
# Preservados fisica, colisoes, controles, habilidades, progresso e menus.
# v3.32.0: as nove skins do jogador receberam personagens chibi coloridos
# extraidos da arte Pixel Rush aprovada e incorporados no proprio arquivo Python.
# Cinco animacoes visuais independentes: correr (6 quadros), pular (3),
# swipe-down (3), agachar (3) e morrer (6); miniaturas da loja e pre-visualizacao
# usam os mesmos personagens. Quadros gerados sob demanda e mantidos em cache.
# Preservados física, hitboxes, poderes, economia, controles, saves e demais sistemas.
# v3.31.0: arte pixel-art exclusiva para os 9 pets ativos; animação de movimento
# (4 quadros) e de morte (6 quadros, sincronizada com a morte do jogador).
# Bolha, Raposa Turbo, Fantasma roxo assustado, Tartaruga Abissal, Dragão Neon,
# Golem de Basalto, Beija-flor Prisma, Dragãozinho de Plasma e Abelha Magnética.
# A mesma arte aparece na loja e na pré-visualização; sprites são gerados e
# armazenados em cache (sem carregamento externo nem alocação a cada frame).
# Habilidades, colisões, economia, desbloqueios e física não foram alterados.
# v3.29.0: removidos integralmente a classe/sistema de perseguidores e o obstáculo Maleza;
# removidos também seus pontos de geração, atualização, recompensas e referências de estado.
# v3.20.0: porcentagem da febre com 2 casas; avisos de moedas/combos menos frequentes; validação de objetivos no resgate de skins/pets; mensagens explicativas para eventos de corrida; correções mantêm o passo fixo e a física existentes.
# v3.19.5:
# - Relíquias ancestrais: cards compactados/organizados e navegação Anterior/Próximo (5 por página).
# - Loja: moedas, nível e XP separados das abas; título muda para LOJA DE PETS com animação de entrada.
# - Recordes por bioma: rótulos e distâncias centralizados dentro de cada card, com espaçamento ajustado.
# - Loja: pop-up central com prévia ampliada da skin/pet e botões Voltar e Comprar/Equipar.
# - Compra segura: primeiro toque solicita confirmação; segundo confirma; cancelar/fechar descarta a pendência.
# - Itens comprados continuam no save e passam a oferecer Equipar; objetivos de desbloqueio existentes foram mantidos.
# v3.19.6: prévias com o renderizador real das skins e ilustrações completas de pets; estágios visuais navegáveis; setas de biomas, detalhes de maestria e correção de escopo do bioma lendário.
# v3.34.0: salto visual com impulso/subida/ápice/queda vinculados à trajetória real;
# corrida de 8 quadros, agachamento caminhando de 6 quadros, efeitos de partículas
# animados por quadro, miniaturas enquadradas e prévia ociosa animada na loja.
# Física, hitboxes, habilidades, preços e controles inalterados.
# v3.35.0: salto revisado com poses aéreas estáveis, agachamento andando,
# pop-up de skins mais lento, remoção da evolução visual/estilos alternativos,
# refinamento das skins ROXO/CHAMA e melhoria artística em moeda, pterodáctilo,
# obstáculos e cenários.
# v3.36.0: segunda passada artística com refinamento de obstáculos, inimigos,
# cenários por bioma e acabamento premium nos cards/pop-up da loja.
# v3.37.0: identidade visual própria para vulcão, floresta e cidade futurista;
# acabamento adicional em deserto, gelo e cidades; criaturas e itens refinados;
# interface premium harmonizada em toda a loja, sem alterações na jogabilidade.
# Restaurado enquadramento de sprites ausente desde a v3.35.0 (corrige loja).
# v3.40.0: reposicionados apenas os cards de recorde e moedas no menu
# principal, com espaçamento adequado em relação ao palco e ao botão JOGAR.
# v3.38.0: pets retrabalhados com mais detalhes, expressões, partículas e
# animações premium; menu inicial cinematográfico, HUD/loja mais sofisticados,
# efeitos de aterrissagem por bioma, feedback visual de desbloqueio/equipar,
# identidade sonora por cenário e novo modo gráfico Leve/Completo.
# v3.39.0: cinco pacotes premium (HUD, loja cinematográfica, pets com
# personalidade, biomas cinematográficos e resultados animados); raridades,
# clima e detalhes de cenário, distintivos cosméticos de maestria e rastros
# selecionáveis. Mantidas física, hitboxes, preços, regras e progressão.
# v3.41.0: acabamento visual unificado nos menus, loja, configurações,
# resultados e HUD; textos de missões limitados ao painel, sprites refinados
# e detalhes por bioma pré-renderizados no parallax. Preservados passo fixo,
# física, controles, colisões, preços, habilidades, saves e progressão.
# v3.42.0: contraste branco em Configurações, menu verticalmente equilibrado
# e colisões precisas/mais justas por tipo de obstáculo, sem mudar física,
# posições dos sprites, IA dos inimigos ou regras de progressão.
# v3.43.0: modo de hitboxes F8 para desenvolvimento; avisos antecipados e sombra
# de inimigos voadores; coyote time/jump buffer configuraveis; pouso animado;
# sprites com paleta de acabamento consistente; qualidade automatica por FPS
# com histerese; efeitos visuais de prioridades e caches para Android.
# v3.47.0: pacote premium 2 dos pets e polimento visual do HUD/loja,
# acompanhamento interpolado, reações e poderes visíveis; cantinho dos pets,
# afeto, vínculo, lembranças e melhorias visuais por nível. Sistema de duplas
# removido integralmente, com migração segura de saves anteriores.
# v3.48.0: animações reativas dos pets (pouso, curiosidade e alívio),
# palco do menu com acabamento premium, Game Over e conquistas refinados.
# Preservados controles, física, hitboxes, habilidades, progressão e economia.
# v3.49.0: corrigido IndexError ao exibir pet recém-equipado no menu,
# selecionando quadros pelo tamanho real das animações (sono/festa/ocioso).
# Vibração via Plyer desativada no Windows, mantida no Android.
# v3.51.0: desbloqueio real dos power-ups, Febre/Turbo invencíveis,
# objetos visíveis na Febre, remoção de TERRENO, solo sincronizado
# com obstáculos terrestres e parallax renovado do deserto.
# v3.52.0: febre com carga 3x mais lenta; pets terrestres ancorados no chão;
# Pets Premium 3.0: pipeline híbrido estável, animações com quadros cacheados
# por estado, pets terrestres e voadores reagindo ao jogador (correr, pular,
# agachar/swipe-down, queda e morte), sem recortes travando nem sprites cortados.
# v3.131.0: HUD compacto informativo, trechos com intenção no Deserto,
# sequências de perigo/moedas seguras com um terço de encontros clássicos.
# Preservados comandos, física, hitboxes, economia, saves e ferramentas DEV.
# Variante isolada da linha DEV v3.277.0. Nunca atualizar a linha DEV daqui.
VERSAO = "v3.277.78-QA-ANDROID-RC"
PRODUCAO_APENAS = True
SKINS_ATIVAS_PROD = frozenset(("AZUL", "VERDE", "ROSA"))
BIOMAS_ATIVOS_PROD = ("cidade", "cidade_futurista", "neve", "deserto")
LASERS_JETPACK_ATIVOS_PROD = False
OBSTACULOS_QUE_AVANCAM_ATIVOS_PROD = False
API_ONLINE_ATIVA_PROD = False

PIXELRUSH_DEV_BUILD = False
FEBRE_DIFICULDADE = 3.0

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
CINZA_TEXTO = (155, 160, 175)
VERDE_GRAMA = (34, 139, 34)
VERMELHO_OBSTACULO = (210, 40, 40)
VERDE_CACTO = (54, 183, 66)
VERDE_CACTO_ESCURO = (17, 88, 35)
VERDE_CACTO_CLARO = (191, 245, 126)
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


def _suavizar_intervalo(inicio, fim, valor):
    """Smoothstep barato para transicoes graduais do ciclo dia/noite."""
    if fim <= inicio:
        return 1.0 if valor >= fim else 0.0
    x = max(0.0, min(1.0, (valor - inicio) / float(fim - inicio)))
    return x * x * (3.0 - 2.0 * x)


def calcular_ciclo_ceu(metros):
    """Retorna fase, cor do ceu, peso da noite e indicador noturno.

    O ciclo foi refinado para destacar melhor amanhecer, manhã clara, tarde
    dourada, por do sol, noite profunda e a volta da alvorada em pixel-art.
    """
    fase = (max(0, int(metros)) % 5600) / 5600.0
    paleta = (
        (0.00, (108, 126, 182)),  # madrugada fria
        (0.08, (146, 118, 176)),  # pre-amanhecer violeta
        (0.14, (246, 152, 105)),  # amanhecer quente
        (0.20, (255, 204, 138)),  # sol nascendo
        (0.28, (147, 204, 236)),  # manha viva
        (0.40, (112, 188, 234)),  # meio da manha
        (0.56, (103, 176, 226)),  # tarde clara
        (0.66, (245, 189, 130)),  # tarde dourada
        (0.74, (255, 142, 89)),   # por do sol
        (0.80, (163, 104, 145)),  # crepusculo rosa/violeta
        (0.87, (65, 77, 131)),    # inicio da noite
        (0.94, (24, 31, 66)),     # noite profunda
        (1.00, (108, 126, 182)),  # retorno para a madrugada
    )
    cor = paleta[0][1]
    for idx in range(len(paleta) - 1):
        p0, c0 = paleta[idx]
        p1, c1 = paleta[idx + 1]
        if p0 <= fase <= p1:
            t = _suavizar_intervalo(p0, p1, fase)
            cor = tuple(int(c0[ch] + (c1[ch] - c0[ch]) * t) for ch in range(3))
            break

    entrada_noite = _suavizar_intervalo(0.80, 0.91, fase)
    saida_noite = 1.0 - _suavizar_intervalo(0.97, 1.00, fase)
    madrugada = _suavizar_intervalo(0.00, 0.04, fase) * (1.0 - _suavizar_intervalo(0.16, 0.22, fase))
    intensidade_noite = max(0.0, min(1.0, max(entrada_noite * saida_noite, madrugada)))
    return fase, cor, intensidade_noite, intensidade_noite >= 0.5


def desenhar_nuvem_pixel_art(superficie, x, y, escala, cor_preenchimento, cor_sombra, cor_luz):
    """Mesmo estilo de nuvem usado pelo ciclo dia/noite e pela meteorologia."""
    visuais397.nuvem_pixel(superficie, x, y, escala, cor_preenchimento, cor_sombra, cor_luz)


def sortear_proximo_cenario(cenario_atual):
    """Sorteio uniforme dos outros 3 biomas da edição de publicação."""
    return random.choice([b for b in BIOMAS_ATIVOS_PROD if b != cenario_atual])


def nome_cenario(cenario):
    return {"cidade": "CIDADE", "deserto": "DESERTO", "neve": "CIDADE NEVADA", "vulcao": "VULCÃO", "cidade_futurista": "CIDADE FUTURISTA", "floresta": "FLORESTA DENSA", "ilhas_celestes": "ILHAS CELESTES"}.get(cenario, "CIDADE")


def saturar_cor(cor, fator=1.1):
    media = sum(cor) / 3.0
    return tuple(max(0, min(255, int(media + (c - media) * fator))) for c in cor)


def misturar_cores(cor_a, cor_b, proporcao):
    """Mistura duas cores RGB sem superfícies alpha (compatível com SDL/Android)."""
    t = max(0.0, min(1.0, float(proporcao)))
    return tuple(max(0, min(255, int(cor_a[i] + (cor_b[i] - cor_a[i]) * t))) for i in range(3))


class SistemaClima:
    """Clima aleatorio com janelas longas, céu reativo e custo visual limitado."""
    def __init__(self):
        self.cenario = "cidade"
        self.tipo = "limpo"
        self.timer = random.randint(35, 65) * 60  # pausa seca longa antes do primeiro evento
        self.tempo = 0
        self.particulas = []
        self.cooldown_raio = random.randint(240, 480)
        self.raio_timer = 0
        self.flash_timer = 0
        self.raio_pontos = []
        self._overlay_flash = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL)).convert()
        self._overlay_flash.fill((232, 244, 255))
        self._overlay_flash.set_alpha(0)
        self._overlay_areia = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL)).convert()
        self._overlay_areia.fill((197, 137, 61))
        self._overlay_areia.set_alpha(0)
        self._criar_particulas()

    def _criar_particulas(self):
        # Pool fixo: não aloca sprites durante o jogo e funciona bem em Android antigo.
        self.particulas = []
        for _ in range(64):
            self.particulas.append({
                "x": random.uniform(0, LARGURA_VIRTUAL),
                "y": random.uniform(0, ALTURA_VIRTUAL),
                "vel": random.uniform(8.0, 16.0),
                "deriva": random.uniform(-2.4, 2.4),
                "tam": random.choice((1, 1, 2, 2, 3)),
                "comprimento": random.randint(12, 22),
            })

    def trocar_cenario(self, cenario, inicial=False):
        if cenario == "reino_submerso":
            cenario = "ilhas_celestes"
        if cenario == self.cenario and not inicial:
            return
        self.cenario = "ilhas_celestes" if cenario == "reino_submerso" else cenario
        # O clima anterior não é transferido de forma instantânea ao novo bioma.
        self.tipo = "limpo"
        self.timer = random.randint(32, 58) * 60
        self.cooldown_raio = random.randint(240, 480)
        self.raio_timer = 0
        self.flash_timer = 0
        self.raio_pontos = []
        self._criar_particulas()

    def _sortear_clima(self):
        # Tempestades são menos comuns, mas todo bioma pode ter um evento extremo.
        if self.cenario == "cidade":
            return random.choices(("chuva", "tempestade"), weights=(76, 24), k=1)[0]
        if self.cenario == "deserto":
            return random.choices(("areia", "tempestade_areia"), weights=(75, 25), k=1)[0]
        if self.cenario == "neve":
            return random.choices(("neve", "nevasca"), weights=(75, 25), k=1)[0]
        if self.cenario == "vulcao":
            return random.choices(("cinzas", "chuva_meteoros"), weights=(68, 32), k=1)[0]
        if self.cenario == "cidade_futurista":
            return random.choices(("vento_neon", "chuva_acida"), weights=(58, 42), k=1)[0]
        if self.cenario == "reino_submerso":
            return random.choices(("bolhas", "correnteza"), weights=(65, 35), k=1)[0]
        if self.cenario == "ilhas_celestes":
            return random.choices(("brisa_celeste", "tempestade_vento"), weights=(65, 35), k=1)[0]
        return random.choices(("polen", "vento_folhas"), weights=(62, 38), k=1)[0]

    def aplicar_ceu(self, cor_base):
        """Deixa o céu visivelmente nublado/empoeirado conforme a meteorologia atual."""
        ajustes = {
            "chuva": ((85, 108, 132), 0.48),
            "tempestade": ((49, 61, 82), 0.72),
            "areia": ((197, 147, 79), 0.40),
            "tempestade_areia": ((154, 104, 48), 0.68),
            "neve": ((142, 166, 189), 0.43),
            "nevasca": ((87, 111, 143), 0.67),
        }
        ajuste = ajustes.get(self.tipo)
        if ajuste is None:
            return cor_base
        cor_clima, peso = ajuste
        return misturar_cores(cor_base, cor_clima, peso)

    def _preparar_raio(self, x_inicio, y_fim):
        pontos = [(int(x_inicio), -6)]
        x = int(x_inicio)
        y = 0
        while y < y_fim:
            y = min(y_fim, y + random.randint(24, 43))
            x = max(8, min(LARGURA_VIRTUAL - 8, x + random.randint(-22, 22)))
            pontos.append((x, y))
        self.raio_pontos = pontos
        self.raio_timer = 10
        self.flash_timer = 2

    def update(self, obstaculos, rect_jogador=None):
        """Atualiza clima; retorna eventual obstáculo atingido por raio."""
        self.tempo += 1
        if self.raio_timer > 0:
            self.raio_timer -= 1
        if self.flash_timer > 0:
            self.flash_timer -= 1

        if self.tipo == "limpo":
            self.timer -= 1
            if self.timer <= 0:
                # A checagem ocorre somente depois de uma pausa longa; falhar a rolagem
                # adiciona outro intervalo aleatório, não uma alternância chuva/seco rápida.
                if random.random() < 0.78:
                    self.tipo = self._sortear_clima()
                    self.timer = random.randint(22, 40) * 60
                    self.cooldown_raio = random.randint(240, 480)
                    for part in self.particulas:
                        part["x"] = random.uniform(0, LARGURA_VIRTUAL)
                        part["y"] = random.uniform(-ALTURA_VIRTUAL, 0)
                else:
                    self.timer = random.randint(35, 65) * 60
        else:
            self.timer -= 1
            if self.timer <= 0:
                self.tipo = "limpo"
                self.timer = random.randint(35, 70) * 60
                self.raio_timer = 0
                self.raio_pontos = []

        # As partículas têm quantidade fixa e comprimento/velocidade variáveis por clima.
        for part in self.particulas:
            if self.tipo in ("chuva", "tempestade"):
                intens = 1.0 if self.tipo == "chuva" else 1.45
                part["x"] -= (2.8 + part["deriva"] * 0.3) * intens
                part["y"] += (part["vel"] + 4.0) * intens
                if part["y"] > ALTURA_VIRTUAL + 24 or part["x"] < -24:
                    part["x"] = random.uniform(0, LARGURA_VIRTUAL + 30)
                    part["y"] = random.uniform(-100, -8)
            elif self.tipo in ("areia", "tempestade_areia"):
                intens = 1.0 if self.tipo == "areia" else 1.8
                part["x"] -= part["vel"] * (0.9 if intens == 1.0 else 1.5)
                part["y"] += part["deriva"] * intens
                if part["x"] < -24:
                    part["x"] = LARGURA_VIRTUAL + random.randint(0, 35)
                    part["y"] = random.randint(30, ALTURA_VIRTUAL - 80)
                if part["y"] < 20 or part["y"] > ALTURA_VIRTUAL - 70:
                    part["y"] = random.randint(30, ALTURA_VIRTUAL - 80)
            elif self.tipo in ("neve", "nevasca"):
                fator = 1.0 if self.tipo == "neve" else 1.75
                part["y"] += max(1.4, part["vel"] * 0.42) * fator
                part["x"] += math.sin((self.tempo + part["y"]) * 0.025) * (1.2 if fator == 1.0 else 3.0)
                if part["y"] > ALTURA_VIRTUAL + 8:
                    part["y"] = random.uniform(-80, -8)
                    part["x"] = random.uniform(0, LARGURA_VIRTUAL)
            elif self.tipo in ("cinzas", "chuva_meteoros", "chuva_acida", "vento_neon", "polen", "vento_folhas"):
                part["x"] -= part["vel"] * (1.25 if self.tipo in ("chuva_meteoros", "vento_neon", "vento_folhas") else 0.62)
                part["y"] += part["deriva"] + (part["vel"] * 0.38 if self.tipo in ("cinzas", "chuva_acida", "polen") else 0.8)
                if part["x"] < -30 or part["y"] > ALTURA_VIRTUAL + 12 or part["y"] < -12:
                    part["x"] = random.uniform(LARGURA_VIRTUAL * 0.55, LARGURA_VIRTUAL + 35)
                    part["y"] = random.uniform(-20, ALTURA_VIRTUAL - 60)

        alvo_raio = None
        if self.tipo == "tempestade":
            self.cooldown_raio -= 1
            if self.cooldown_raio <= 0:
                self.cooldown_raio = random.randint(240, 480)
                candidatos = []
                limite_x = rect_jogador.right + 24 if rect_jogador else 30
                for obs in obstaculos:
                    if obs.rect.centerx > limite_x and obs.rect.left < LARGURA_VIRTUAL - 8:
                        candidatos.append(obs)
                if candidatos and random.random() < 0.68:
                    alvo_raio = random.choice(candidatos)
                    alvo_x = alvo_raio.rect.centerx
                    alvo_y = max(90, alvo_raio.rect.top + 2)
                else:
                    alvo_x = random.randint(45, LARGURA_VIRTUAL - 45)
                    alvo_y = random.randint(390, 690)
                self._preparar_raio(alvo_x, alvo_y)
        return alvo_raio

    def _desenhar_nuvens_clima(self, superficie, cor_base):
        """Nuvens de clima no mesmo padrao visual do novo ceu."""
        if self.tipo == "chuva":
            sombra, preenchimento, luz = (58, 74, 95), (93, 114, 136), (145, 169, 190)
        elif self.tipo == "tempestade":
            sombra, preenchimento, luz = (24, 34, 52), (45, 58, 80), (79, 94, 117)
        elif self.tipo in ("areia", "tempestade_areia"):
            if self.tipo == "areia":
                sombra, preenchimento, luz = (115, 81, 44), (163, 118, 70), (205, 156, 96)
            else:
                sombra, preenchimento, luz = (85, 56, 28), (124, 86, 45), (165, 118, 65)
        elif self.tipo in ("cinzas", "chuva_meteoros"):
            if self.tipo == "cinzas":
                sombra, preenchimento, luz = (82, 48, 45), (132, 77, 66), (176, 111, 88)
            else:
                sombra, preenchimento, luz = (43, 31, 48), (92, 49, 57), (147, 79, 75)
        elif self.tipo in ("chuva_acida", "vento_neon"):
            if self.tipo == "chuva_acida":
                sombra, preenchimento, luz = (33, 56, 63), (61, 105, 93), (133, 214, 122)
            else:
                sombra, preenchimento, luz = (24, 44, 79), (41, 88, 138), (92, 207, 231)
        elif self.tipo in ("polen", "vento_folhas"):
            if self.tipo == "polen":
                sombra, preenchimento, luz = (42, 74, 48), (71, 117, 67), (145, 198, 111)
            else:
                sombra, preenchimento, luz = (29, 57, 40), (50, 88, 54), (109, 163, 95)
        else:
            if self.tipo == "neve":
                sombra, preenchimento, luz = (104, 129, 154), (173, 194, 214), (226, 240, 252)
            else:
                sombra, preenchimento, luz = (62, 84, 112), (102, 130, 160), (171, 196, 223)
        drift = int((self.tempo // 4) % (LARGURA_VIRTUAL + 190))
        bases = ((-70, 24, 1), (70, 52, 1), (190, 34, 1), (310, 27, 1), (450, 45, 1))
        for idx, (base_x, base_y, escala) in enumerate(bases):
            x = ((base_x - drift + 95) % (LARGURA_VIRTUAL + 190)) - 95
            y = base_y + ((idx % 2) * 4)
            desenhar_nuvem_pixel_art(superficie, x, y, escala, preenchimento, sombra, luz)

    def draw(self, superficie, reduzir_flash=False):
        tempo_chuvoso = self.tipo in ("chuva", "tempestade")
        # Nuvens ja foram desenhadas sob os sprites na passagem de fundo.
        if tempo_chuvoso:
            tempestade = self.tipo == "tempestade"
            cor = (178, 218, 248) if not tempestade else (220, 236, 255)
            limite = 48 if not tempestade else 64
            tamanho_min = 15 if not tempestade else 20
            for part in self.particulas[:limite]:
                x, y = int(part["x"]), int(part["y"])
                comprimento = max(tamanho_min, int(part["comprimento"] * (1.0 if not tempestade else 1.35)))
                pygame.draw.line(superficie, cor, (x, y), (x - 7, y + comprimento), 2 if tempestade else 1)
                if tempestade and part.get("tam", 1) >= 2:
                    pygame.draw.line(superficie, (245, 250, 255), (x, y), (x - 4, y + max(8, comprimento // 2)), 1)
        elif self.tipo in ("areia", "tempestade_areia"):
            tempestade = self.tipo == "tempestade_areia"
            self._overlay_areia.set_alpha(28 if not tempestade else 48)
            superficie.blit(self._overlay_areia, (0, 0))
            cor = (231, 187, 119) if not tempestade else (244, 202, 135)
            for part in self.particulas[:38 if not tempestade else 64]:
                x, y = int(part["x"]), int(part["y"])
                pygame.draw.line(superficie, cor, (x, y), (x - (8 if tempestade else 5), y + 1), 2 if tempestade else 1)
        elif self.tipo in ("neve", "nevasca"):
            nevasca = self.tipo == "nevasca"
            cor = (225, 240, 255) if not nevasca else (250, 253, 255)
            for part in self.particulas[:38 if not nevasca else 64]:
                x, y = int(part["x"]), int(part["y"])
                tam = 2 if part["tam"] > 1 else 1
                pygame.draw.rect(superficie, cor, (x, y, tam, tam))
                if nevasca and part["tam"] >= 2:
                    pygame.draw.line(superficie, cor, (x - 3, y + 1), (x + 4, y + 1), 1)
                    pygame.draw.line(superficie, cor, (x, y - 2), (x, y + 4), 1)
        elif self.tipo in ("cinzas", "chuva_meteoros", "chuva_acida", "vento_neon", "polen", "vento_folhas", "bolhas", "correnteza", "brisa_celeste", "tempestade_vento"):
            paleta = {"cinzas": (255, 112, 52), "chuva_meteoros": (255, 75, 35),
                      "chuva_acida": (125, 255, 112), "vento_neon": (70, 245, 255),
                      "polen": (180, 235, 110), "vento_folhas": (85, 190, 100),
                      "bolhas": (90, 220, 255), "correnteza": (35, 170, 230),
                      "brisa_celeste": (205, 240, 255), "tempestade_vento": (125, 185, 255)}
            cor = paleta[self.tipo]
            if self.tipo in ("cinzas", "chuva_acida"):
                self._overlay_areia.set_alpha(18 if self.tipo == "cinzas" else 12)
                superficie.blit(self._overlay_areia, (0, 0))
            for part in self.particulas[:48]:
                x, y = int(part["x"]), int(part["y"])
                if self.tipo == "chuva_meteoros":
                    pygame.draw.line(superficie, cor, (x, y), (x - 13, y + 9), 2)
                    pygame.draw.rect(superficie, (255, 220, 110), (x - 2, y - 2, 4, 4))
                elif self.tipo in ("polen", "vento_folhas"):
                    pygame.draw.rect(superficie, cor, (x, y, 3, 2 if self.tipo == "polen" else 4))
                elif self.tipo == "bolhas":
                    pygame.draw.circle(superficie, cor, (x, y), max(2, int(part["tam"])), 1)
                elif self.tipo in ("correnteza", "brisa_celeste", "tempestade_vento"):
                    pygame.draw.line(superficie, cor, (x, y), (x - (14 if self.tipo == "tempestade_vento" else 8), y + 2), 2 if self.tipo == "tempestade_vento" else 1)
                else:
                    pygame.draw.rect(superficie, cor, (x, y, 2, 3))

        if self.flash_timer > 0 and not reduzir_flash:
            self._overlay_flash.set_alpha(105 if self.flash_timer == 2 else 65)
            superficie.blit(self._overlay_flash, (0, 0))
        if self.raio_timer > 0 and len(self.raio_pontos) >= 2:
            pygame.draw.lines(superficie, (83, 167, 255), False, self.raio_pontos, 6)
            pygame.draw.lines(superficie, (245, 251, 255), False, self.raio_pontos, 2)

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
        "loja_pets": "PET SHOP",
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
        "modo_grafico": "Graphics Mode",
        "graficos_completos": "Complete",
        "graficos_leves": "Light",
        "graficos_auto": "Automatic",
        "ajuda_pulo": "Jump assistance",
        "rastro_visual": "Visual Trail",
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
        "combo": "COMBO",
        "melhor_combo": "Best combo",
        "quase_colisao": "NEAR MISS",
        "metros": "Meters",
        "m_unit": "m",
        "missao_moedas": "Collect {} coins",
        "missao_distancia": "Run {}m in 1 run",
        "missao_quebrar": "Break {} cacti",
        "missao_pulos": "Make {} jumps",
        "missao_powerups": "Get {} power-ups",
        "missao_slow": "Use Slow Motion {} times",
        "missao_combo": "Reach combo {}", "missao_baus": "Open {} secret chests",
        "missao_febre": "Activate fever {}x", "missao_quase": "Get {} near misses",
        "skin_azul": "Ninja (Default)",
        "skin_verde": "Dinosaur",
        "skin_rosa": "Cute Bunny",
        "skin_dourado": "Flex Rapper",
        "skin_roxo": "Galaxy Phantom",
        "skin_robo": "Robo Runner",
        "skin_chama": "Inferno Dash",
        "skin_neon": "Neon Specter",
        "up_ima": "Coin Magnet",
        "up_turbo": "Turbo Mode",
        "up_escudo": "Shield Barrier",
        "up_mult": "2x Multiplier",
        "up_slow": "Slow Motion",
        "up_jetpack": "Jetpack",
        "up_clone": "Clone Squad",
        "clone_perdido": "CLONE LOST!",
        "clones_restantes": "CLONES LEFT",
        "conquistas": "ACHIEVEMENTS",
        "recordes_pessoais": "PERSONAL PROGRESS",
        "voltar": "BACK",
        "bau_aberto": "SECRET CHEST!",
        "febre": "FEVER MODE!",
        "febre_carga": "FEVER",
        "bau": "SECRET CHEST",
        "conquista_desbloqueada": "ACHIEVEMENT UNLOCKED!",
        "ach_dist_titulo": "Distance Runner",
        "ach_dist_desc": "Run 1,000 meters in total",
        "ach_moedas_titulo": "Coin Collector",
        "ach_moedas_desc": "Collect 100 coins in total",
        "ach_quase_titulo": "Daredevil",
        "ach_quase_desc": "Make 10 near misses",
        "ach_bau_titulo": "Treasure Hunter",
        "ach_bau_desc": "Open 3 secret chests",
        "ach_febre_titulo": "Fever Pitch",
        "ach_febre_desc": "Activate Fever 3 times",
        "ach_combo_titulo": "Combo Master",
        "ach_combo_desc": "Reach a combo of 20",
        "ach_partidas_titulo": "Persistent Runner",
        "ach_partidas_desc": "Play 10 runs"
    },
    "pt_BR": {
        "titulo": "PIXEL RUSH",
        "jogar": "JOGAR",
        "loja_skins": "LOJA DE SKINS",
        "loja_pets": "LOJA DE PETS",
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
        "modo_grafico": "Modo Gráfico",
        "graficos_completos": "Completo",
        "graficos_leves": "Leve",
        "graficos_auto": "Automático",
        "ajuda_pulo": "Ajuda de pulo",
        "rastro_visual": "Rastro Visual",
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
        "combo": "COMBO",
        "melhor_combo": "Melhor combo",
        "quase_colisao": "QUASE COLISÃO",
        "metros": "Metros",
        "m_unit": "m",
        "missao_moedas": "Colete {} moedas",
        "missao_distancia": "Corra {}m numa vida",
        "missao_quebrar": "Quebre {} cactos",
        "missao_pulos": "Faça {} pulos",
        "missao_powerups": "Coletar {} power-ups",
        "missao_slow": "Usar Câmera Lenta {}x",
        "missao_combo": "Alcance combo {}", "missao_baus": "Abra {} baús secretos",
        "missao_febre": "Ative a febre {}x", "missao_quase": "Faça {} quase colisões",
        "skin_azul": "Ninja (Padrão)",
        "skin_verde": "Dinossauro",
        "skin_rosa": "Coelho Fofo",
        "skin_dourado": "Rapper Ostentação",
        "skin_roxo": "Fantasma Galáctico",
        "skin_robo": "Corredor Robô",
        "skin_chama": "Corrida Infernal",
        "skin_neon": "Espectro Neon",
        "up_ima": "Ímã de Moedas",
        "up_turbo": "Modo Turbo",
        "up_escudo": "Escudo Protetor",
        "up_mult": "Multiplicador 2x",
        "up_slow": "Câmera Lenta",
        "up_jetpack": "Jetpack",
        "up_clone": "Esquadrão de Clones",
        "clone_perdido": "CLONE PERDIDO!",
        "clones_restantes": "CLONES RESTANTES",
        "conquistas": "CONQUISTAS",
        "recordes_pessoais": "PROGRESSO PESSOAL",
        "voltar": "VOLTAR",
        "bau_aberto": "BAÚ SECRETO!",
        "febre": "MODO FEBRE!",
        "febre_carga": "FEBRE",
        "bau": "BAÚ SECRETO",
        "conquista_desbloqueada": "CONQUISTA DESBLOQUEADA!",
        "ach_dist_titulo": "Corredor Incansável",
        "ach_dist_desc": "Corra 1.000 metros no total",
        "ach_moedas_titulo": "Colecionador de Moedas",
        "ach_moedas_desc": "Colete 100 moedas no total",
        "ach_quase_titulo": "No Limite",
        "ach_quase_desc": "Faça 10 quase colisões",
        "ach_bau_titulo": "Caçador de Tesouros",
        "ach_bau_desc": "Abra 3 baús secretos",
        "ach_febre_titulo": "Febre Total",
        "ach_febre_desc": "Ative o modo febre 3 vezes",
        "ach_combo_titulo": "Mestre dos Combos",
        "ach_combo_desc": "Alcance um combo de 20",
        "ach_partidas_titulo": "Corredor Persistente",
        "ach_partidas_desc": "Jogue 10 partidas"
    }
}

# Registra os catálogos incrementais sem substituir pt_BR/en_US.
_i18n247.registrar_todos(TEXTOS)


def t(chave, dados):
    # v3.246: mesmo catálogo original, fallback por chave e extensibilidade i18n.
    return _traduzir_v3246(chave, dados, TEXTOS)


# Nomes de exibição temáticos; IDs internos permanecem iguais para compatibilidade dos saves.
SKINS_NOMES = {
    "AZUL": "Corredor Clássico", "VERDE": "Guardião da Selva", "ROSA": "Aurora Encantada",
    "DOURADO": "Rei Midas", "ROXO": "Oráculo Arcano", "ROBO": "Sentinela Mecânico",
    "CHAMA": "Incendiário",
    "COSMICA": "Viajante Cósmico", "PLATINA": "Cavaleiro de Prata",
}

# Skins com preços
SKINS = {
    "AZUL": {"cor": (30, 30, 30), "nome_key": "skin_azul", "preco": 0},
    "VERDE": {"cor": (46, 204, 113), "nome_key": "skin_verde", "preco": 3000},
    "ROSA": {"cor": (255, 182, 193), "nome_key": "skin_rosa", "preco": 6000},
    "DOURADO": {"cor": (255, 215, 0), "nome_key": "skin_dourado", "preco": 12000},
    "ROXO": {"cor": (160, 90, 255), "nome_key": "skin_roxo", "preco": 15000},
    "ROBO": {"cor": (150, 205, 220), "nome_key": "skin_robo", "preco": 18000},
    "CHAMA": {"cor": (255, 95, 35), "nome_key": "skin_chama", "preco": 22000},
    "COSMICA": {"cor": (185, 105, 255), "nome_key": "skin_cosmica", "preco": 55000},
    "PLATINA": {"cor": (185, 225, 230), "nome_key": "skin_platina", "preco": 70000},
}

# Economia da variante de publicação: valores de compra mais exigentes,
# sem multiplicar recompensas, moedas coletadas ou alterar a física.
for _id_skin, _info_skin in SKINS.items():
    if _info_skin["preco"]:
        _info_skin["preco"] = int(_info_skin["preco"] * 8)

# --- PERSONAGENS CHIBI PIXEL ART (BASEADOS NA ARTE ORIGINAL DA LOJA) ---
# Os nove retratos foram recortados diretamente da ilustração Pixel Rush
# aprovada, com fundo removido, e codificados em PNG no próprio .py.
# Não requer arquivos externos, bibliotecas de imagem ou acesso à internet.
_SKIN_ART_PNG = {
    "AZUL": (
        'iBL{Q4GJ0x0000DNk~Le0000`0000`2nGNE0FDvztpETQ|4BqaRCwC$oO_gAcXi)C`}a8K+}FJIepr$%TfzhfFm@q!Y3iDU0?7&`D~ngsMbgqzr=?I>',
        '2_X$EL(*gs+7eiRZJ@6tv|xzA0n?BYa03`akTJGwge_aL9;4T2=DyE4zu)d3=gdeXP7wwPlQny-tGV~iz4zSnJ^S(9-',
        '@Qk$YOA(ttF~&ZwrZ=kYOA(ttF~&ZwrZ=kYOA(ttF~&ZwrZ=kYOA(t=hx&({{?NLVl37tpb;aAh=2kps)10HXju@cpMG4kKmyi60O<Wd&fPspantJR3',
        'e&UOF<4Z=Sx1s2C;~)6fHD+>Vn`Xrl;xN_9}`1~s-',
        'gr?1+Aeq3KT$O+jIYgKJxkZ$=^u;=dO4qp`TMO^%x8fVK5kDQ9sFsZCmg*!}_#FS}Ke*Vhm)d$2!4c5n~V$tn*lFun0c$Sex^a|Na(SlBl${P%Jzoe<',
        'wm%?6jh=<;okFf8ZVx+aqWXqhPE>)ncq=X3ZQE6CK3*%DGUYDjFk=MgwC65reZ9u?A;600tp#csk9D7#3K+WsVQs@(1Kg$H~h81o;sLFx9!|yoKHaca',
        'bmc2MuT}aH%Cp8W>x7Q$%Sr+H~4Yl12;XGDNE1A?C~(X?1oYQY8a9^PGw>GdaubRFhUinOVD*k9_oI9^1DEFhFt6xY#F$>t#Ckytl*AgLIGF2O6t$H4',
        'x*F7$Rx2O_n6gt(zmuGRhD*dgu^S)6+FT1~D~Q2qJ<JK~T^t6{1Rvkr)HLevkQ+r&u`A<)ZcL8IE(7hKq~_ebDl)KT;lO{H!*1zJTF_Uq&UXpAGe`1Y',
        'mmY7TV1g#u~hHgcwmGRuY=+7N`MJfhe`B#i;d3)*x1O8;!C4saT(2iBJ^0;Afu4ZJ+vM?*GcCiRXxo`5}`iwR6|2x%$`W@4c)3$~j7bQdHGbsv<G$cQ',
        'JJy1A{RRBMD-JL4SZq<#nPUnA$6=&{aT1LG(;`*L6OY1wo;7p82E4=$#%Cf#?4E9s1<=KqG3W{~>l}3*q6<5w*@^nA(Q~L_jP;L8moMXL^Qavx5T02(',
        'k98W^1C(ci(wZTF0-h+~Uf8w0doI2*>1fn_U-gVPdMqJAdbfbHd2{u)|jYo!pAVE<zt+gy<MUfoO>kA(lue@mYds04+cZVyJ#^P(m>xlw(4f6GKjn1t',
        'Av1SQ52FwE!(a0}v5H_1T2V(__KX=_T%e;8FU+9HjLlzyqTaPyRXa)SsUfR(~B~4`K*vSvYo*o}^r|<LL|)LX3>dF+~W>&a8(R2{p-',
        '95tJ$)O6{ehmA9>ALtS<+MFpZ-4$seX`K}G;>|5Vc2v5z<su_)WmMdr?EC5R-',
        '42sAQC{!sFas;bF8k8gCk9&;wOkSnW8ymbvB4Y+VVl*Nu7y)aAEPxFT<09%Tu^}uOc-',
        'R!|^(E>phaxQGkhp|VgaWBUR2TpQ6$U}cRml}XU1C%sBcnvI709tf)e`c8>1ofs`}P9E?~2hm1NiUeHfmuEFR`AhpT8R&M_j2GO`*uEf~f%(2QU&e7>',
        '+EA_;mLaZ(2Ccv2sz)I;j3h=UO%m2ON?B-',
        'huUXqOY#Jh~iafs9;dWDqPlyv{R+CwE<IA^3t+E)YR`&2ujrySJlIaIYVbwyw99z@#=@90&Rh(&A{voq$v*_Imzx{|0sb5F)qpz3SkkeJ0;`Ib`n3;#',
        'yc>37Em!n>nSPFP*DSk5nDvMi#aqBPM?l!W`Z|2Q|`;w=q-',
        'Iu=<gLHLK;d25*d1rjR}PcYP1Tq71j%VH8=q)9!85K#$pB~49luW*C8u)rPbQQDzua+5RKIBu&(gSl?tE{yn!ybVZ!L4F_b0csK@p-',
        '8AOQ0@1uxlU_hkTReYm~m<C!TNa-',
        'L~$Rmsj7=`Mwc#KPlrR6|Z@k@cL28PQ|<h)tnifpYaLZXhAPS6+&P7N*!HX5u75<#M1B1DBeDmyZ0m@2OkK(r#v%OtsCc7m>SB!U=&Vj!BzBaw;*Ek6',
        '!|;E-',
        'G}YS3OF+dIH~Y9Ecp48}Dpj#$YzPrQf(QSwr;22=%1?Ijv9L?kt+HK_5FMc~w8iC1X4z+zEyOiR2N`hzZ4Vz>u`rVdRyv`V2LBd$*Lm7~<0O$9|68<?',
        '@+#*vUydAyOc>P`)2{qIVmh-cG2soTBE6RGc4fXf-r)Pf=eOcV$ft%>{-',
        '22g>h5n~*O7X#}Wruw?3@&cPV`U?Yk<C3L*z&pqBo>G=2d8q^~F(RA_BOYMPZr_1IIaZE1I9MXFo`&@+VJoVfVRKdQ>rw9N54ke+WM-KR3(GWd8MWp6',
        'RS~Hl>zVu~oc%hfa_;gARnbtrR|X}F#*j8@_{#5-',
        '#)w7Igl{Y^a9uKobp{Oqi4hg}!*A{76B=lWVL>B((<C9{oZ;onF%^~FW|A#9mKcBrQe(MvayySM9Y$@edkn$W-',
        'NbV1RVDnAr6{QPXv`6nD(5b<;FWS%fgyDfLIshytRbA0*9D}aE@z00ATc6QVO&(XBgl8HvgZU~M6kwkaZD+OV}|{Rnu4CS^p}*@+BSDA&d~4~w$Uc0v',
        'oxmKocQMdWbMu?xc+bt8^(ySj3*)-fuw|`UXMf)N-',
        'fAGRQV59sEjHEL)D=WYd#o=ArPeiW6=o4fLH@Ys+(ArNnWKDYF%W`&W}}(tO|sP)N+`FfM`K%H=v9^AR-',
        '+Dy(BQ%H}sF^NNN~GVgEGzg9CejK<9=}(|z~Tgl_eg?m^i4wp{<$Tek6WT|hLga%O*w;Ms4x%;^v{CAl#~EEyJW45G^&Z&f60R73*7IC4?SQwy9P_Sv',
        '>=BStJ3uwpS0tQT;m@*rYWFo=AI8!m@#jD#4gcCd^{8K5jl${bnh!(>MMeu?y&m)@oqwH;r*`31C0n})<n7BYccbNbU))0~^e|NJ{SedALe_w!~Y)g0',
        'kpGs`aVye=N*1Ublh(Bo9})>MR61i{wX4}yl3V&P~2LP@@omkf~NnE=*c@EFus`o<863?i7i{~ZCb2G5~P2yCLFl(x>Rg)`U^c35F<U7I%_J`OSg`uI',
        'HXd+J2mulk&(9glS>0mx4uWst2Uyyxo2{hX_kY5kRa4PWLo&owg)Rq5-1*K-hnbw7JM^S8ZFq_JI9lj_TesYQfkDPV+-',
        '1~jMF(8?xAl8hK4^9S#u<vOGqxO1w_=It3y4MrRX9-Zgqr-nRg5{AA-S>_eZ(W(!z8VOo*MV4~QY{Hx<p|G4NBCj}kiq4CFgD-vLH_r*9@2MB=eefrx',
        'caE?92{)tfjyq_!9DhIA$k!H*ksIi!J*zgknrf!C1XXKXXAx<U6l`R}+U>O3m3TVnEnrQDW;V%XrpdaEIgPu%Sv3_gaxp{x;*x9lufqXv9VLu3uLOl!',
        'KyXBYMm}stY`N(V(7AO)nPK90-',
        '^Lq1a~HqwFS@Wpr42@OxpmJ(*lk;UV)s*cbYDRpq2pl6W}J>W9n)IjXJ)0&o*}AQS7BW)u&P+!uJWQ*gCgfrj5r3voT-TxnGr-Ij0>bFArsUl<dTDPm',
        '{_%UA{K~PQ8p4O$^rc3i;*H?V!+SMaapU$c+{_xLp;9#T5)>s&gZaoBEcAN8jw*WERNXwtwpANi>66%){%!18(fQ<^uWsdz35-',
        '7^=Bx_GBsAM<`*IsW2>ImTFaKT7m=y3Ep?C|gQ!T7g0WyD)`E2&r;Un9)>4+nfEQ&wf!W==P~#9=BF12?u%^+V-',
        'Av9@a`gNu(!pko7Kc~~m>@`D5!b}8nc|{L=9p-',
        'wsEyor^cYSI1zrB?8813>0qW7D;Hlf2x;4`?lVPznXbIL@tdU9}FrMffO%ZHAN5>^GRvse}OdiScG@5OE(!lyAlC<#I1dY}tlkFyr&IH(c6c8h7EUg%',
        '5rm;?a_WXKaVhtOHIbZwsW9-',
        'b@G!u{Jkyu2u2o%ww(Xt~EUJ)MUtF1XMe&_o+cI_>KNmP?YeHj}_7@_qf!a%JYo3kctm9!7wyl3naL?LqurAJkXTJbs4>!ahqQj&sC$!u2j&{FZsgh0',
        '#oD7}yZY7OK8l9U9)*ql9cE6*Q*{>oSJ3kUAxz+;c_@UEX=u{XqJNfi<vPUR*4cIjaTWtaWWc^O6A&OO&!S?*qony4BAVWkg?XALbXwOC_`5Qs5g#9+',
        'l>#9~CT4%GOSDI6#a`VdA?2!)ST4ivM}8b$(9>rU$IVDy&gJSK)ZIL-O>!2VzUC;0-9VH7(=J4zV~@P;_H9AS}97YhJvy84$Gzw^2kN?=-',
        '3j32qJdeB(|i-',
        '+q@td^XrxmlIB>fEIoD^F4=B$C*KOaq#vh%=ZN(GXxfCTb)t%j!~ST$zo45=<b(up)d>ln^8Ml9Bb5u4(N5PlWlwR^hpy`&A}B`Q9p58G{mu0rGOpvt',
        'IfR<hp;tJTu>!KfCjC^6q!4*h!V`KZUvXL&Oj(`H8rqtf*G~n24Y;fVCK7X|y{mEp!>AC9#=Q`!LNGF$HH8nMirGOscT~aV7jklu`pnv4rjt0gyC7(g',
        'b{DL4+cVK?=krXnBFAa+4Q5Q*En_c!wHGh!BTM%>LZFc;t7ldfelzd(&t1#CzUIw&hxi)AJNZz5&+MqsdqYawN@KBx%aJxh=FNIv6!TN#cdk!{6eL<_',
        'XsMAv79Qn`RsQ`-3@u)Lus!4IzNmTMHr)k$@V{L)l@9@k#7t3Wcz=l=9)}E4XR%4(|K253=bO-^-',
        '!*|GZof0KY#vg!<jT!RY>*F@74sRcgsHjgSa2u=(Q4=rpH@L9xzZjRj}$?KX+6#9u2VCMuaROlO`fafmS>iWMsTQWX<Rj*km^{gP2smI^~in~cT<2fu',
        'kMgQ17f;qQvilLEl2-',
        'tjs8>Tmv2(z$CWPR%2dQH~E{v_Pc<%1YRb2C)gdE`LVVJB!5_k28X^LgFoncUWUEMzFRb&$29<#;P#IPzecnnWI4|ivl%<v2C$;&#m;sn5o?_<<#Bp{',
        '?Pz%dA)-$LX0Ju`^O-W;gLO97g1BqhK;o-',
        '!n%z+=(K0C*4DDUt5!PdO@x(3P^9v>T5&dF&**^~DMN`+A^}RqoE$B2>Y*>vdG;&l{PKTh|0|LwA%KD+890N8LCX@s)P=9!vQh)-',
        'W;z?6PVc~jh#3KS&2kE?^Q_-',
        '`8Le!B5CWKLf6$m^9UH_{9#;w1l^$p+;jjW(tMO+U0^$wB{3s87{SH*yT>Acpc<`UEm2*3t3%rPM=@l==BpF}{QAnCCVje&T9NB*#`FN3GZ@#L+Dx}j',
        '-#U@h};~rsj8qpHf66b_+JYf5-s}W-',
        'nF&J9`xeTIeRe`BzETRUnm0YGkvy*c8(1RS__jNGP*!66tp85+M`tUEGGcFfwGvVJ{e5u|!nxdPRM8=G|L)LEIK@l9rff|d%gz3498TF5#SfV;cr|$<',
        '17~4XP0g7rOXWL}$1}9G*V4^jRb&e=f^|r>=o@S63h&o<bnKJ^;dNg(HyZe6=${~K|k0WKq#lQ0zzVRZF?=7ItgWZ0t)cG+ie*G)F?q{#%*E(x?b(r8',
        'Un=Rfx*TC5pChbsY6W{7kj{A&<L&{=Ex3|d2$L<74$Xb_>k4I#US-daE7xyBuWT54l9)EeryR0%RNG;m~6?c4`6IGyj*-',
        'zuJEIs(A7jDJ(HJ>lk2&4|Y7rdz?sG^LF3!w}-y|H3Dfe-',
        'w>2|l~~a<(3Y#0Xh)k~f%=JyUJQxkqsfMqQ2_Izl!zN0xeyA9@JlV}K*;T+aGUmr&#*Mxz`XPw~uhkvA<YViU*lL>Ssg8%KNWIgwdz=xpZH{2q$oX%x',
        '8rjtAI3KSatDEgYe=6-_e2!>`#Y-+xMf0(QxN8)+25SRwI-wpYYejd~VKiagLO7TEK$9ei!$Wz2N@G}0Eiqy%Sq?P!5JTN5Nq;(WoW`G*;emWX8!Xkv',
        'YXBwIs1%-',
        'OhQH_c|sa5Q4jKS|o2;<<6mn@=C1(ePLz35s~n{i)$+`cw1|e+7*_6lkxznBM$D=PlPip&TeNV#J^kx}(U}jWA;al3GwWayT%RR%F;ap^;d6y)L;fkv',
        'h-IyE(V_dQ8tOa`eDHj7^Cl2U3h_g3i#$W-z8lqm^N;XL`29nzd^&-',
        'g9rS&$ms^b!!v)&hW7lfzOpNpQdoSON>2ct>+iF@8G6y?_=GwU#Rn6x?Ro>sdxhR!3T3~riLs9=U`JJOnJcqEg9pT@*f`<@moK>iF<bLVs12M`d43xf',
        'By5(aln_0yz(`#<JNokk&j1+n;?{3U<R9Q#<`S6tHspBG(PoYS))>0tkf$S)%F#G5@Sk20-ARz%fKU#J;-',
        '43+q|i@iB~o~yI%7=+*@xV0NdVp2ao*TPs<P81AqH&VH}lM^Q<%xnhqvgka>$yVU#pz?0OFWqddU+-',
        'f3>=K1lh9r)*AR2YY$o$UOh@#v8f*S(|y`buTArUqu|9Ldy}&i4L=~6Cf6ABF<G?1j}lSYOKcaO#qM8K=2K+B;uC#^V!BlBzexZD=(thxrUR6KSg`pE',
        'Uo6X2u7=wqaPxG!A7DAYOCF%!B|-+;b;!25i$)-rzJo3jz8rc&(GM<Z1B1b33~Vd*_y)~`9Jq?@9{;x`i3{~$*1fhMj={DS?1U*Ve#~FoLDAi<_JK)-',
        'y>@@Ye`QrVyZ!Sy?KucA$oe_qpVd!t1Q^GVVd+;t|hK(k)GU(U4IQx14;{)hu1$W0N19<%%rfc35kzvp0*?wf*70=T8Sl1;EUf<*5ACJ&%f=Z$g6L{)',
        'j1=>6J3V)mV^5bqZ$dr0-JgWCC$z(X{Uv1iDJ=EGVJ$A8!2Kc60EUWKzGIyVh-N$$T#ldz8%-lJ@5c?EswY%OsvNwLy)XuK2E=z$ozu^@ITyNDk>O-',
        ')Ie$?i50xndYj5&tW*uXfy@h&NmV=!OyqRet>Gnq_9Z@Wso<=~XA_KuDTS`XO-',
        'zt4-it_vZ%+{W3oDCE!)~8scB%rZ)`mxeVWm@tk}PfDQ^)=Heu+zWUdE9F_mea-',
        'UNpatSL>K(Y)I%IE3i8g?!M(#K0bddF$l@JOUMuJxo`k}=37dXSj}x+HMYzWXjzzR31d~90c#bEA#sY6Y9;Q_lF(R_aoekJq-hi0o^Io}hGR_Y5~T2G',
        'J|N<-rh)1<qIB`;kl|7nH<wZ5MJ3@|OVm)c5h!Vr;ho2*<>}A7hWqw>p26@0ufFkp-1K`l^1e9a^=sR-',
        '=z^T!$k_2;K5;+k#ZTv{fAkgZzEUo172futo~pQNaoY%~6=o)dUSHWX35^Vf<4TBcC5EXC+Ft3EaPXeJ{Kda|CY`9fD{keV*@T#FK#f2wFfvBzp=C~I',
        '=POva|5lQ$`eHGbY}~R9D{f^$$k?jaO`J!J0}--z6S9PRzVOHV*ehSphS?E+_1^cg-',
        'g^3F&ZDCdTVDGvHvQDg`20U=$_1w}+ivcvO%lpbZ4Edtlqi`MNCj(^ZLP?Lwxu+J3y`>+J-',
        '6S<m*0B50DLriiVmaUmvjM1)&L$cf)j(A+RpIsryv?s0~0&1r~BAJ&;gbbH31?Ri4<i{qcO>b4LdMm@kxRaSE()y%Qx@(7}mCU?Z<BAE2EMVrxWHz!W',
        'V9M_Icrf=Tt;?ZcJFrl`D5xIvx(5g3B+mWTlcA=p=#(mZ=n+hnv4t@bTwo@|_1#rV@h`IcN`&42e}i2)(03O>mk6!s5f9#iSdV+I$J!V~;{PLTn&}G1',
        'e;iaDn{~-',
        'OJW(yATZC)%$$~XjIB@f=}P_A@2K=51e<k>2C$_E&B@1jHO>zp<_+e_X;q(84?jDGr<caQsu!Qf{Bso<Zq4xZH%}OSf7tsk}myb#9^zds!L34dj{Qyz',
        'lf6KcU?=7b~yd*uVM0lF-j~8qE`B0lC{ZF%c+G^%uYM<L4j{&Jbkdhd$w=Dbv)O6>Z2D(-',
        'n>BeMR%DF#BzCOE3Y~AfBE>|@+bFK{PrjH>K9(eO;2me#I>(d--',
        'Ij$GqsM#{_q`WR758cvCOXB2C>QHWQ$@n=J(A}UUJ}@Px}AHVAWP_)mClQR&CXO5cdB7vtDy{+=~^L00000NkvXXu0mjf',
    ),
    "VERDE": (
        'iBL{Q4GJ0x0000DNk~Le0000`0000`2nGNE0FDvztpETS{7FPXRCwC$oO_U6S9RupYwvx|ef3MNZoSo(jPV0wjGvfbo3aA|1LhINyk8X$P$9)@fS6*K',
        '03qQ$Ktd8=%w$4>1Ic)TfpTmZV;f@=Y?t4*EL)Z=$!e+9lKOdH=bXLwnm^9%ZW#h070Y&cdR5)3t3LPMbI*6awbu8oy{}+7mSZ`VV>y;%IhJENmSZ`V',
        'V>y;%IhJENmSZ{oe+hXqf4TXetkLAucaWw{L@dFbf^alO6qw^(ul;?#`j0!F&}(o{W&mq0BW8Oc&Jj9$(ZLLLgQ#pq%n;Si_%Z|kwa|a6YFIaf`T~>9',
        'qCOx`JB3gKqX$rRu=>+D+dy>;iFYIEn`N1S3-O4@S8}8lu*N{5__;@*J_1rf-6#ejFE$Zk3p4k`G0{93@rwm?w@i^xpuvGUn3^WucRyivKgJz`$@k-',
        '0Z^M{rWawm6uh*-;`6^vzAW%d_JVY-b5wJ)E(^W`T5W5kJLE{>XX@D7KcHd>3aO%2c1_DSFC_uE1P)D?aMM!D}GdqJGoB-',
        '2@jgOEVd^I*q&{%OCYlf$vx&U_bUD|9H+G?q`+N#aA>Rd~8&ri<Npa0Eqk4nA7Ix3Y4#Vs?mZ*JqKswfRqYuNo=*ww~(3*8QQ(Ds99*odw;m+t<LYeP',
        'hzaw+Vlf0u-;EO6q$Rv<Z#`WYW(WcVY$z(9~tr>zE4N$4K3q>^GPfKiIv5D!ft&JayR?VV_Smi)di(oT<|r7BMu0OxnTQ*C}7hAGrL#MV)lg3FNF2-',
        'xSLtBzvs*1NR07vk-nJMIcxH@u3G!AQS1(2ivLGuj56SnA%<zE99fWWeRrDwoqI1!)qwci*0;Ruf74HxcffKsFe#DVP~l2Ee9B_IaXyhjeZS)tcwh?*',
        '@uE!1wwa{Af=dw&&mh^<ZkCb+8tUh3G*osDS2>7tjeXKJ(N9Fm^i7ObCy(VL+i$;Nuj@v9BY4=rSs`CdZ$h^T4EI>?1FuIb6e4QdX;{Qi<3;3l-',
        '?b0^e@&y7M<e27T6&I;Cm@hJcL)F=S|-fqGS2Ay`NgOMl|1)eM8yQZbG}8yPZ|<Lw&GIPWjG?fO}H(gG-1M$Ev39N*56kqQz5^EdrHAN;6r)AmUB-EU',
        '!ZzD+Bw(4A>gtte^3QDEpQNOY{*T%qpj%ydA!XNH0p1Cc<C9`OaL8Ac+B0V7?EwWKzZNW@x$Q$<9uMoHCj;o25&fB)IscKwx4Vg^p$Nt~T04k*SdzTL',
        '$;!}NZ*erII7F+e=HAFU@yHv_SB+MZ6wqp4CvkEP9V8#l75Cgiy%Mo-',
        'j;5)oAtL2(3xs9H)OQEafN3W9(NqFTOB6{TRjdw}<x_cZp*d`Pv(sMQlj8ec{*48Q7Y9Qy9X@`MA(9e0v89KIWoptR?euU%f_Bi}99{P7o4-E;z-',
        'hqi*GSOq0wfM_G)9HT1?=bk%2o(I$ze9VX{_!v-)5S2hc6c7O|9ljvMSOSSIsTwimOCp9nofZ$v7~h|oWMk@h;h^JVUwR33SLc#<U;N}?-',
        '~}Hm_}B%8=bfLTStM#?+UK~z0j64x*252Bt5qZlC6}akp%!akWR1{mE6znir;AH0Su00s6;uL2OTbk?R4^*#^Tkn#f=CZnLA3-',
        'B%Kr3ccWt5K>I^3pI<~=E-',
        'g+E<O1K1}GIG3T2k)0B#WY6$PoKujW8dHb&#||Dmu)}1oFo+_mh3bddjJY*peWkB@I^I@F(83&o%V62nq8_@$Ls&^$CxYTS-WO{Ac{c{491k7pa4>$r',
        'H5T<38JDXAp{6ugT>kk^KHk6P8(t4Y@KIq{xtNBKyyN#6i(#hA8sN^gn^Z;_{^8t^OI|-',
        'ro9@b5r_~=#iAinv%;ohQV_*!K_}0+duA^a#Vix^Gqkm!R;>^`7z9LmgH}+K!*aP-1ItX-UOKA^28+WoBz0;tIh|G{?dzvL*5Gficm;p+t@9C#n#yW@',
        '!kx$`wjm$b7F8;aFxaIyG)H0_MgyuK0W>HYBBDa2+Tw(xYjm_g6eMx{@%?{=kAVck$Y8x}A}A&TR(dtCECf9yd(>MX(ZaE^R9G=M11oRX&s{&<&oLi7',
        'ksm%dNhI=;(^j)KIIOK92I7-',
        'pm~h7bunb;v4|6;3N3ak|2AWuA8z>S%qvBOCYI<pBuo0{X6(d+#@O#SqOpC0WqhSfNrTQnR$l~7@7`XUcAQ&jlALGRLoQkYT*_Cw|Z*`d_A#t|6v*Mo',
        '|<E#gEd(!c3*i=#Rs6@<RHA)cFlnfLR#Fo}gRFJYu5Ep7>uedb^>xeNJS?CvLvA9QBq~W8A{zAiEXfP8rk@bR&79&C-',
        '5pR+n(26YFoyQx%?!?P9pKrkIjXZe6B&UDaLgFx~#U>HKpgxwReW7e&%BypN7_e%}%oHgRk+NKt7A_!5eY=N>EP`WtweIj%xyVq;bdO~_!H59?-',
        '@B2WsCZFA44B6oK+RvM8X_@19l|8Vj)P3)1}Z7)EF^-M9w0^*b(&ZKTLNg(2#H_{>4{+_$Px@9pjMZ_F{Vc-eH7nBbn*R5rBQpjaUqu}9gT*vIvSYwk',
        '$j=6h5X0^sQWi*vGNAA^L1i&3({?%>;^N82}(OyaE7QtvQYecX}H9ovb<vqCK14vpDo(!o+ZoDssn3qSkQ?2fLEog2a0ld>Mk%+dgm&2A_j~a5-',
        'UWfn5Y;pbc&o1m2N1A3&e|$gOJYee}v-nD#@O2Vv<SlLr75YE0K=H$Gl`*mO-',
        'AQu}ndF;`UJmN_!HnmtvqLQxRNhx%CS-G4Y*UrC?5l;peX81)sTqR?K_2EeM%k{NVCd87Xg4QgdAOf$vjH<Tx(`ue|>6Uc-',
        'UVf?zQwJbn{tDZt1qCeERGK=W97(hw+Sm1bL@n<L!}lVwQm!7Id`=rELx!z^58?D^gDxREmLUBfcJeHL-O=90s~A5HS`?YjwuM-Nkhi#KEOOD^3AfS3',
        'l_*G%KLcFDGN$nR^h``!t>F(k&2I{i0MddwJT3W1oTMFg=BLP`B@PM#^Pu7M&z?$Hns>%jD6iz(AY7g9|WB$oeHB?6*~h+WiVMh%g;D2%=78QotXTxm',
        'x1(Vk1nHmp*L_eZ5@Qob-zFwQL*=pzlFt*3D45{w6&K?sPC5Hmz0iyc6E&Y{Gp2VN;BM6?H5uVfw8bQjCND$z$Y^qkAWwG{^KHIVW?ES>N0E-',
        'hM0pr`?p87O*<WDzR^8i}DmWADQ?9{CgwTO!@7Za|v}BnI_>I5Z>>1(&$;OS%NLJ<lpjK0y|}*1}L_srWBQVT}QNL<5WIy)+q6eDI54iIkn%m@@Tc5y',
        ';XyYV584QCi1^&oL348YukI-BCUA41C2`EGMq3^YM$?gef7Z^e!-',
        'q^i@(CmQu!4DyVg6FD(`s*PH605miIf9x)e{UMxklmd>Q~e@o3)ts$rqRm&!Ud2|hwrHPFggT!+9z%OWRQG;O0p_-',
        '9jI)20eyz>5*TzP+s&;1zUH=Kq;5Sx)uv!rRH55Oj+Kz8OZ0bCY$T|jfeZfQhg*%D08yBZO!2*%mP3tPZ2F$vO}$tYSf>@X|5c)s3qW5K5Ou$p)nRvI',
        'a^02;mH_VE?c=0AG@@ZYFucif_C8Hk~*gX+uFwpy}4m&mlBZVw|?X{8X1LJ*G=yT~vlE|$8=KozGJQG=@XCNxW>@UY&25rc}s^%{mr?cxb5#$rQ3Vf;',
        'c@D@FPfF-',
        '&;&ySnVYy@~T(8eJ(@(j=6tYSt`1#2Uo*YL!t;uX_dpK|E1C79~+j5(Qf|n52eF8YI<z#3rP*3aL%7#$x3#I;k#|Fnu(bruRCr2`24550R8eG=V6te5',
        'G|yj2FH)S2^i>86V!#r$0QDV@MFq%TzN9jX^n#d}Xl@Wu1x$q5+Ta?6zT7RS2R~)(p|6g=oZTgy5<7r&v*p>8*>%f+94JVqq!H%Sn#$6-',
        'Wg2zEn;?^I(pgSZCfTUWQp5BtDVTn9po$%6~esu6JxHFda_}5%IB<H$9=eu$-',
        'YR+2a&TVGXa`n)9}59W^PBOiXg#d(Ps9KM*>Z;;mp)Lt2k$Py%t$7ccsl!`w-',
        'E9z|lL*=%yr4=*BkkBiC~ts(wk)i8S>+0M53AeCpW>+O_?j~{?}=Oj&BlQ@$i-XgoZ%-',
        '*$wt@nE_zt2<MaU<PUfmC8y#d>mM@nH<=1T{jvV!3$#3eNKmMX_3C6N5CTn*3~S!C-',
        '$NH|3nLTL_7DNbqzC#Hb5>d$GAlZvrDCrMyvr5ku9~5K*@6I|zwo{idg}+HYn`XO<kyk*tAlzo1XGc#UfDM=Ifc_*)MU@7syLcNg75bC5VjS2~=Hbnm',
        '|p?MsP?#Z}zmDjBg%XN?inhzUX(EO&JbVyYaNf}PER`+dfBLm7!iY>fC=@ajs&r}`}yw+goYbOI;UMG3T!w%Y5o#t2S?B$igt^g3*jM<)6QdF76r*Z<',
        'vC8mj|!w=kBFBMG4B@4dv~+c`!4Y=m)a&0(a9!;o}ZRI<QG)$_F%*RkKbj_S^R#8!*u&OPOth%x0ODjEV>L_$ZQYnUtwd^J!X67K3N_~+FvcBeUs>Ee',
        'CHIYxO|T^UOYp8t$0vkxnAw#`UISz8kln~@k8N(_S)%TU!(w@Pbnx@=lKccU5^R^h!z314~nT0%RgV#~dWi+b?Lq_DESHG{3pp)-',
        'F1d+vbxYQzRYt3!U!(;Ww<bKY{Q=j~T3{Nr_)H$0zW?I@XoNi6tKN{=EEVos-Hx%%3NdChZ1xa?4i>6&5&QkphW2t3<(&L4vfK9GBdu>~3nPM@7auHM',
        'Vd4|Zq_I^OZ7rxR?Idk?mm>J|)$uzC>ee1|L<BClG!Q?Sa@LzkDVPiVI5G-',
        'sQTCg3VitwU%2h%IaC)K`U}a~o(f3~nRR*+x7R$aiLRr@BmTZ*a$5O+Iu>VDjiq`0eAEp(^Pc&czUjgM);;iwz*g5hY-fNTXUXHk$CtqbnFI)J(zAYY',
        'eBShgjFB;ky>F7$blyYh7QRaz(x8VY3J(DF*^#%VWI>v-',
        '%F0$e~Wgp>CTEQAuK*q;C1ykN0x(c#Dtx?I>(Kh3tke%YPI={T1)i=|6*^V;ynLCd}qj2|v05jH5dZyS92x{O?No{EfsFb<*ECf$VcXMkkxZ2-',
        'X;qlaHc!!Ew0ITkW<APEq4oJ5uMOV-qA%a!FaAclgj5k*wvgE-',
        'y8o8Z`EHYKcMB95&(awRdaF;R6cdkr;{51EG9vevsJdpy>*<uR(Rq_kJUMexnpV7NZa71wdr(!Tk&#cl+X`QgGz+fnq8k?H%~rA40rka<}lu-',
        '*=pJPD<tEe)Q;+m_YmU*TBA6SW$%t!6t-',
        'V<JdbZ$iy6S!Y2IYek3tq9OLbr|FsQjRl}E_G0B;uIm!rWJs{DPV>1HkJuyb2ro`yVsfsDfyeteXMaz+Yj39v+A`pnd5Q>zVgBQH<cB)ka)j{aa{>Qg',
        '=y!JSw-?@4{-RT;(K8888h1vTq;)-',
        'u>;cZ{srcRY_U1xdknn>tGjC1&w=ZY;gE@LIFyA}8HO@zFKe)cw!=d2}t^D|j_(rVU?S!SD&sp*_zyJzape~#@wfL(hUnnawG4yD;Dn4QYlu{xvCYIE',
        'Oy4<^tFDPBE@FsO#U1Xk7}^+Xs*m5Ms5))PgE5el`07{Ln~lx`=-',
        'ha8O#n>wVH@za~9dYt?XTj;Od99gUDZ*LA<`Hh6m;Cd>f8<4@@qL}(Qdf5$p>hdaodP_!Ka;86<vUN9n>stlmqFldvh{^Z88oD#YYwkwtmM}ia$XlLC',
        'qpv}q5zanym?(w=(-}A2HcxZf!UGfJ<Fjz)MmRV}nD5|*1{vtDFxK)!Uto=v!%&}7CBvIQzcHj0!(E3GCbk@c?Ncz>UK&f2los;vA)(6B8fTJ1mf_C-',
        '0RGxf{>A|QS_Xz9Ct%5aK&ST+x9`NRxQRqkq~Z8)Z}MEd6K+3XD7t<8*UP4uIPF>NerAoSnLvJUlB8pZH|~U5!m7VKpJ#0vW_`urV_>GOSQ9XKPCd2C',
        'O*eM2qkUvQ+lhPrW|GaTkW^?M?D7xi9^e^|>;>xyQkrFlV11;B79oO5c{mfcKHKw&zsi{D7%~O2K&Y-qOck`iBq>H9T89`{f@xDEWK_<1KeN|<@-',
        'f;U7y`x_D%MkJ`f}CFS7>RSG;cBeK*8>*fK?d#N{jTo4dgG_Kr*s|zGlMQzIpuDuVVC7XEM8eH&r}CRYNOR)RbE}=6z0{N7~(t;XX?<H%RWOJ1u=~%=',
        'zf)EuItiQ(qC0R6(+yFm@0ust$<>L7_&<StIj&A`=R0$nzW<mCD=xlJ-|#`foC;`-',
        '$PlZiA&N+`J8*^U8$5hLRfCv@UYt$+H~2Ub*OdhW<C6MD4smrhf7;(=E?YqkYr|43ksy#DBOEJ<vi=U&YJccRaV<yp@BKeGINlDRNJq1+pj{+S_4pq{',
        '{AhU%{#uoQ4&lUQdVtUNo?eOP)SWF`FZ6hrm|Q{^wwl3~i31zKiwc{y?#jN?WmOg%GCkQF!ZZC-',
        'd#!z88P#OOMPB++TTM!;t=$TP|XLa*FvWPc|2b(;1<Y;Z=yylOHe~^@_6yE0y_9o5{Hu4n8!+zR4~j8>ao???R)GflvPyg9DLMH(7rFj8Sfwn&wlVxr',
        'YHez{YddvFnOmH1C-tjh3M|okTk1FqMS5c<w&?0koUo)}I1{?;vI^#0es8B<AIKES6;~s-?B{tMskO7&-b5^7SjQA2=1)-',
        '^Z(7w1MF)<#X%4SPphW@tADw`;`n-E8MbYnq&sn4307|T)~ccj1yc^Axc1FWXHjAI!z%e*t)Q0^Dx^U7-',
        'yhfE`Bpm0T)TChJm4e4rEPM#DX9F#f!M`!tb-co6x#)Cw8;~C$Ax_?WfV_5TmT^9whH7m31efg~Nmgu<3?!jVIR7*eC%+d&?<ps-tVz|KQJPb|E=qly',
        '25#FtOwld#J8R_}boAaO)Mj`RjMxq52pYiC>e#2{&D{pV2jg3=F1pS{a#zZnGfInn;X<Py!u{!HVPIduOQU38tvygM&1MBtaXFm;`q3E%0N5Y*<xiVs',
        '1Zcq{^Nvx5Mf_8m~MBJJyF0L#3LMB*L3l1X63U5{ZqIh}{7s%@I@Sbyb6s^k#PDhNKXW=L_%s0fjou+7ugws#BuNdEnqA&)8gJ_wI<P)(PGAkz*iU(R',
        'M!vZk^}nI!lt|5Mkv&6)^!(j~I&-P)RH+2L`zHzH#~n2BD?6iY@n)%r*%#o_&)Y+H2t3_xIE1TD<h6QC!VJUk&@NbLh-_s#rz`>-',
        '1GTLq6ler#BEc3}FZfGe|N3w!i#+NN;mUspc(eYWU`ZG^cJS-',
        '3V+^bht(cN`J#JkSde28L3OLNe)??Bbvgizcj)Aw+^9si}vxaC2!```YcIaU^Jq!+;<$Jkar6nZ0)65A11T~p+f7x9Om59VEiEQpLUX*Jwh{dnP^1%H',
        'mu{~m;Z0<gBj*oPs5M5s18<1vVt@!Tdv&67!_`wI>?L9UIXjSLUb508LCO?am8SIn<+&CAw=@_ZZ7@it^E15mfGp-',
        '>GZF_rUhm|Njl2NU_UzBPfaF%?MmBY0^t7FSTQ4;)UH1cwQEU=y|ngD(<z!bb%;wbHbHDctQgP)0bB~wb_DOyjjM12eRQw7iIL5t_`ZzRKw#eu_rkwS',
        '6P%E27(gxfxfWx`46=50#!(ln=DIK3&6ZVde&@N0?*2MvXap+9pzgd<yJ@*sP_TeUV`-',
        '!J9x&L{;kO+ky|RjX*(!>eCbDjTV@8K~_3#w{^qu)SnzwxC$aUdg@FXe})Zh0eiu4e5<H&oz!H62cEv@qsm6%5~_7)=*B!_tY&BWci%ZaeFXe}ju-',
        'RVS0sE-Wc(!l9w)-csB(PXUXZ?L&yx$}Mh%vGOHh-L(>jAB-v3U&>cfpWo9BPuOIKF>opf18*8-VXNWC!yUP_|)*cFQ3nf!D)_O)nG-',
        'O=a0_1k?P8g48G@Q?El!tBiTeAHK-TsM3YHReI#(;n^#eL&zmSZT{O$lZjK}t<1A_gD&PV{mzKM*s!Dp{SxD<77^sn7el0RwC)k9fmLgWrs$wdNvk6I',
        '>qLRWuovW{Da&L15$F6E1m6b@b6Df9<%bhj=gJje9AcI3}*<P^Y5d`k(ZPQ5fr*HiM8Y9jC&XJCt!^%(ogz>kUBP(NmsV4sEE@azxn7H&0kphx!lN3g',
        'AJ`kd(dfY0ai%9B75*QmBV9Q<e<r$(-M8Wh`30Z+zIfUQ3hrV-8z{ea-',
        '8W;<CwDczl&RGn?BQrUloqGq*J^gZ;ci$m8Sy4Y<K@1pM5Tg=wj{4jV{_tY>{I#7&OR-',
        'o;a>~Ujl^U!#io|&8W9L0);QhM*9KU2t09L*I>pHk%o^4<FAoS{vG{8Oo_4v?1QlZu_#DNYvRG{4&5*30eEtii_tH69l^Y3q@_PeK|qlToG@X($^xUp',
        'e|T>@gUQMl)US;A27OU&#en@T|)R&tzl=vIZF-#o;n2P4q=C18r%{^#P~a-j7XJCT3)NPqIucgke%`NluFSM!ytnf<{f%)I-',
        'r5nDwq%xhpDAl59D#l>y$(pxk_VeFl6WY0bSLb`D++7(C>Y~tufkI8z!g-asEL@7C9t4%GDa(i5!VfuyjukO-(=+Kk;KM-',
        '1u<yem8SdQgbjw2EO4>zMBW${U{Pyhe`07*qoM6N<$f&',
    ),
    "ROSA": (
        'iBL{Q4GJ0x0000DNk~Le0000`0000`2nGNE0FDvztpETYZAnByRCwC$oOzgLWqIa*&-',
        '<R`TdS(8tE#KJtGl5aXh1+^5f>0Kih{{#G|}LoQ9(0tlBg4n#?eG$l8K`+#JD6nh+!};(P&f%DuRj#$kISV(_lBfZ`HNex18^s_kExF<9rQfW@5lJi`',
        'Uifb@g9eb-r`%?|!!Xeon!WbL1R3N6wLR<QzFi&XIHE9668r$dlzpI^W!-z1@=xo%d82vY`F{us{k_Ktz7-',
        '`*k0=NAqlf>N}nV5#WFVFhC4+K$?&K`q7gGKzneOfzc)SyLTcrgCa;|K`bgtun_K_Q?q{P=K@iu3X+i;e)9t0kRpIsLJTxwWTe7(j(Ly1aLb>{FBAjw',
        '8|E}@-AB@FLTV9us0&~~#Udglh_NR$>-6SkXq<oSqq^_nO}DA}<ztaCfyE5OqbLYSB%p?n80^|%wA00`Z9L-',
        'Zn<pB;#T&Q6?ly=44XCwHj}dPuw$GApn?ia4$s$Z-i3bKLwk+tQVu`hgC?tY3BE&=(5{xE@sUS853;E_r^r+e|RtVeuIa-TQ*Z(>@1wGA}@AYUrZ3Lx',
        'Y&!=u7xqq68551D8k-*|3$1ne{o0VFDrV5Ft`?XCx_=7tcI{zd@0-',
        'YP~r?+{U^?&>tWV`}Se!&0?f_Ol+4BdH0<poEPu1?WT0g++!4Jr9YZbm~OgqUcg^2l?awfIU-',
        'Q~?Gp#lb}y$4xNt2j>uiXQ4X8u6wRWXL^|78pi*k6%iA_SX2a!1><sLtO8abvPf#EuU$eGDHug60<}ke+Y%fSLYePGh@zD0Q27PuqQf>*T;U)Kpa#`P',
        'dHYW|e$}XKQDW^Ejz9?daES{*-BJXH<^`H7^d31)LNABhLs!v7PlzoV2_X*<z*ZaN5~F=6<QEM<szOLSp;t0RI}SR&3}--',
        'n03Xnz2fZ8<8)y}e{Q6mr$qJb7p>sLG3(^zBDddV|5Lp9pgx2FnPk<*HzpdBb#@t=|2nX9}*Pul}7aSC!Y^D{0Q+&4|^pv3B3-',
        '^ex|HZF=ifpb$SZtwjidJH@@PHs{k)B6Ffp)qu+k@IK7=X9le<x8CBPJrW0@AFPAsYU5vucgtgJ6a$NF#m3*Z<A=PYY2OQNdQCa_UfrSc3tA>*0KXtR',
        'KYhUqo-1`o#k9;=O+-#%1jK$_B!HyU@*3@ZfBTn)iSb3NVR4FQ@gF*R$`PSF+*6cl^w3m1h@fkzK62KKvTJ;_`RV-MIrrDJnviWvElM2Vq5>GwyjO`R',
        'POK+;kV_xucJ&k9k6>u>a6KiZd|RX6L2{xbh2M;3>~|8r8`POB#ddrdi@=tw2Ugrb!%8NFa$Tm|D!9J@bTM=)G@)N@@{eG|F-',
        '92bufIA2If~ZDj5aLNbQfE~^rQFIp5?PLP86nHln%rqJmYZfBd24$#@ZmpiZh(UV(DXn*`}wIRl|0%8Qe;3(!7xZ#>>Xf7MUXB~z$X7w=><WWR2+@!T',
        '*7ryHd?+H=BCYIm>q3E*u<u8ZCqFGM+tJk2}bu@l=8*;{eWYD2@3>kVS;w=xHbS10b{eJHH^mphMN-|U-D-',
        '81oX4tZGFSm8}@g@K5C#RU8+r7Gd^XP4RFixNvp*_Xc4X&th+B2U`Tn+4fa1Wop?sL5Nm^ag&oJ9-',
        'A_&KK{12tqQF2x07%BDL5T!lc7e5l9F;ua=;X(v2oFQNhFb7VBIxR6s%D=ba65q<q5oO!`Iw0bIPmZPIhwto4C?4I1smlnVMbCKzBVPJ919>s%cIp_s',
        'gbR`Jh;M+Z>Hrz++V2iO6hVg@ShQ^xMwPVnzqFD=qfm|WBfG?XhF|<DXyEI<EiDG%1?&dm;6&_jFL8=ifIH=W-quxf4RZPC@O^p5SvtYD>-',
        'dsn*tI*?4L?#9>xdB%oXN^9&7`XWPdo*g+(1i?JSWG1XjnE;B&gOI<+(!~8bmzMaAH57ytx##!aNc2t60jcPdI?&uhxBr^aNsg%CfKzt^6qYu<5v)$T',
        '8FF-voq+mF<kATnWDWfB5%8Zv8(<k#@&Rnl5oqnFn50+^Ma@2^DeHIA_L8zZxDDa0c;En6YuFF3q9~Xw40$6sPnjPm$@C2WV@#sn^;L>bbv~ujvc9yo',
        'Uj720__E~bqjP}2&a4$J>ydJ%qjetmTX8^Oh?G4$6<Sl^lH!;LRL@UuQRy%2)&Em3zz+f-VgR+Yy<Y+hS+U{+`^DY^KW93E!bV#A-',
        '8m=TYC2^KBZ3z2D-',
        '2A*6vRZQhCiuNH?eW)`M6N+A0X$9{JuyA`6w_CJaPK)uO3j)+|9o4=MT?#_xqQ459NiOw>d6UW46U!>;%!i}4bAy_n{hMfcAmtE#AtkjNr_oTv@@$!k',
        'b{`T3|!A@vyiG`%9lty`e_v<H#tJ3y9TI_rsxh!fuP>$tbQOrx{L<Ou_?^Qrq)Ge=yDasRRz4S_gH(Vj=DmN=yB+juuCo_ZX<=%UVJmyZxXbr~#82pi',
        'hSKoyD}vh2n1FQ3C4Jr1Mm(B4{PcnIwz_+Aa8O~SrO{A^4V&q3W`UbGZ<SsOn7O_*H3y#3YCx}l6Worg}7bZ|G!--',
        '}X*^aOPGG@1;e%Pjfbd!JYaM)e5EbFc=JQ>q-kKwW{~*JkR*9gM7935^N@q-',
        'Pz4+k23(<p69;FpU_p0<jL=BS`(T=#)j;Z6uDMlVK_`u`Z)w*5Rje%wS5G7R=lNaz;inHVPBN=u?g+<kw<mcA$Hg5Yh&Iei(D&*|5Pvbvf$lkQr=L;B',
        '!mm8LJ<9mZR;EcF+A7`>(x79v1++-`l4g?3RWN20b*B3E({H112w}C8<TFqtmpQB~>H{>Ou1WRv{PgIXFeFA-',
        '{7E@v1R2>!Lwv46nrW9Bz~1S~C>gj3wtKP?>{MVsu4>7TdwrklqjrpQzKKL7F!S?UhKf3e^Bbz@!#>1=12iVhOXVA7A=HKEg)S$m7RAoiCv9ef=%;C8',
        '<)Xa)l#mHc5wSxZDv(0c$PY+aDx7dh{U$2306L5**qsB`jIi;GR!@h1x(93`B86WQ3|jnB*8Dna0)T(Pw$gk^@k0qkaZsA0*t{CBN$_ENq&9x*?N-',
        '?7R0<waYQ%4b%u4dGG@J=V18|G6W&6;EOIlOC&t(0Gh>ea7RPG#w!?sP9U@kqUHcLO8U)kK<b7lt&|{(A_5w;ylH3A%pvn#+<`gPpLaI#@Dd~vG&P6~',
        '1OlNJVTLTzw|ocR+mFtJaT(&bqn!irnNhksj$-',
        'B8Ux8*B!5bEC+5+FWj%3+Um=(k1<0<Ld5hO|IS1?QzQ7@pd@#6zve#1fKCkHXsmP85xL;#^Txkzi{eirs@V#Tp*Q3<6c=adk@=pp$^5kMtEV`2X5*Hc',
        '^Q(wUrQ;FV`%Rxd$fffzKVY_4NL>q2GwNn}?ZB#E2Id<T<uk!XZq*OQ)pDw-Nd8mLk1@-',
        'cdwHxV}v(7k(>+BxUoTp)@p>iUAMji?c^U~7*(fccFF)GYSUibXw0=&QR<0Yg$BKsvjK0?46pEGXhUq7mj$m`I<A0eTy^Q0$u}I`eo2R-',
        'b~MSVE8hMoYszGN={A8l(seKmQaK>cZ50_h2Tf7^gV3EPLfkiF;iz79zpKmik!}=;`BR-`kAo%rW!+ud?K|=c3CRXthiwK^+l_GmkL?-',
        'R1?Ag&tCPLS)Ma^!=QIDJ{#wVr`1Yq8QYGSX25O)}Ufb@It_6U8L>ld~E}2yO?LJf*L5Hv?m25GH4{_XPHobhJ%4KPG;b=lfjirHa>vMQ5&IFz#7C@F',
        'p!HN$1G$2jazBP3G-jLktJ_Fuk?(8LX|EBIqtCo&~NIf4n)xQkoz)XEg*s#!R?x-',
        'vuBn@GQ_rfA7FItIARqsQfhpWAaThI0F4d1KlpV9dWP!pV+_6Gw6YQ#Ay~o321GEnG~LaiDzBx-Ax`?KpnoGG<x{Hm3tB*30l^a~=*lXq-',
        '}M62TP8nz12b>EjH5pGTacIIcaI(pe|Q0${r;5J$17N|n07&N%??c6BEcdEdWa>)l1z*drwzhnk6=L33d9B@pmG1<jCokr5Mk-',
        '6anhc}oVE@v3M7Ic9+nP3kwGZX*kX*7Pw4@#h#p$0DVbm9QYi}=Ql<@CszD%_LQ#|AI|W*gX?HwB%_fpYXb5;I^Rcth;RDcrdrGM%gxjVGMGmRK8iN#',
        '4CcZ;?Ov})0-',
        '?p7<t&WW<RI3TbQih$BOcE&rMgvIy@r_0VABZQ0a8X7`4bgC&^xRXaq%lSn>m2J>tl;I(c^?1mlDDEoz`A|`GL&{+zkmg6@Kzvq+<E(LT=c%TGvhm0v',
        '5bo4?=SrXC#*Z3rB5BlZJdN^3|2|3p(-(wR1c4suz2-O_1zY1oxzI7rcqfeVpBGxDi8N?Sm;8kRd5kuCL=Zpwof%9il~+iwdoT?q<rXVjJE-',
        'e7427B4W3v7X;7?Je4Ox;nOUyA>#oucwdSGglqQOR6(lkcTS6^HtClT`yIHgaaZ=9A`+SC0BW$%&ettzT6@$c<*u+E#8l{Jaf!35c1Y^qH&h*1YEo2@',
        '{K)nGA#kK|XK#wS`;HSG~7^%T1-~x)EE+CO9t92hpwTh{xgkFx+3`8+RAhyIL7YIgB?{P&@785)ow&a7+KC|WjkvmmE(}-',
        'SBdchO$B>>i7;s`6A5b;nxPKdBbS*#9=oaF=R4ka3WC})9`E}HMN$|i)_9#LE&bR0eec5Hr-tko%-',
        '>`+c8>Oj5r8~y(Ej6Bq${PaIDLO^gn;6s1A3L%n+5XzQFwVyiBhb++&wNQTX!IL{r+c~@#f;?1$P-6)F-#-',
        'L=P+$JKHHU|R>L_(O0a8;|P_zt{G$LdLWQzOoBuS-',
        ')>v=Rpps;`EBylL{bUM_#jj|^zLfHtr@bE&VK=8iIV@bK*LBDESWAM^14<e`rOi;iho>IyeP%#g!7^o^5%KR6K90@sra^gAknN|a01tS6VMcIM{$b6e',
        'j9VE%&0Z?*q`xlY8f~h88LqB1AR1DIyFx4d<sG=>8NiChlZYgmsbU5yW)ht~yf+-',
        '9^JW}*~MSa)=R)OHkPF$__`@Aw;Bqk!$fU4q6AOdo6$Y`aXUmRjAVx)gxAX=sl5eu22Hqt1o@lOL_1sfZ%0YjO?$vt_|C6fYgio*k7>#EHRtr@`%#Ym',
        '^$AOngmjiTMtNG1@)XynK<j~z@|oL-=3GupkJ(L-S+C94kgjOBF{^-',
        'Ab31S#4dOiC6F#xc$Q&*YRsgpC9<R4pS<O&P|fT*{Q64oQiSP*AVNMEx8dd<ml$i^Nesj0F`z0=OV_1gt6k%~twR0r=-',
        '%{tzF&_=6Ptrw|oH%Yj>LSvZXCS5fc5Tjuxg2P{5w_#%{ywf+8248;8$XC5BmjJ0(4PE#GIV^mP@ke~!(SQ><?E4w8%WuG@1Oj&7(N~V=x1N|njAEy>',
        '1!Z=4_48uX`<sPqs0lXD75khJR5=!?kfNCh$sO2yTs+YFDE0_ND>2%+4lO~D9w{u8s8G#On9!}(WtA{v)rl2OUe0-',
        'E(ET$fTm{RJhlr09LrSL#N)G#zL%Km${GT;?ak0Bsw%u~d3PGcOS5L-',
        '_YN6d{hATrp(_s2ZbulR?i$OI9C!JyU>xxgD6qYT9fks5BF+sA+jWs@HntXQNG!J!@yi#5sNHI-icwYT!Q8@^36vV@TL&~6S{PRLz30!_79JTQk3J-',
        '%|&HN5NUKV|vYGL{Yx5JVt~(8!hqF_fX~6<i?fX_0T8WYwF_BXkx^H!ja1D61=j3^eOB>Q$=s8kq^KJ>@t|V#+-',
        '13qovRcsVk*8kVjgqzM`vCY1784JFkcBWXfCvZNG9@E{Ij1RDZcOUkV=v%sv+N$p`4RKGuSi+q3P7Jha0nW|BYt$J)V#@afrm9ubgfjAO;&vWzKz1$V',
        '{Gd#8oj4Rm@8?Y8tCHR6sf>8(>Fj>F`i?M<_*PpGG&~5YIzy3w`-',
        'n)s#=>@zL)Rrz~{TpA0&hA2d1_LAb#%S3PYf;Y210%?QV10q?+0GdkzKY{cKa*Ym^bLkjKb<#R@FKkHpffYrdQ7k5;Kw@%8wZ%`9pL1*e3M)M>I^yTV',
        '!|2Cm+G7EzLI0dS2K8Ukyjjh4!vR@Mg)tc$Q2VSi@l5%j@Ck(!Ic9PAxE<UQ?KB5FA~~4l2yaF!4A<e17*Hf>4$kgKgNQoTjEO0n&&+aS-uRK1DK*sX',
        'it}gqE^RO1~ERMS{4mO2&O<xKqNv7Mby$b_83ln_dD@LhHK3rL6IQTR*f>%x`*_NJE)8;V?L^}XC^#0rqZp8|17uWV;arC3DF1_RnO;O)@E*TmPPH6x',
        's2I7W6^lLiMe#cKd}D3F<yS|`Q=uW8pu77x0vm1^!O&e5F#nri5RG-$iyHt6PTPsT#nzp7xfOazFv-xCW2ZM#bWS;jdwx2h2~k={Y<Qcwa0@A*zqy6a',
        '2W3)>tO|usI33CLUi(4w(j{yjBaM)IAJml#QzRN|1mkMH!17h{59=-',
        '?)^OHn{Q$+a?F`J<LjP7oP)!o%hwTwqxk!sKjs<fQZ8KbYs_q$r0J^ItejPQMWC{Dh)@Vcw}nq@NK!=;LAwDRsbWSzYgKFrP_34=R!Y@a%aVzpNGHP-',
        '1$4S-',
        '3}NRs?7EXsJfvw~s<)8#=Z)N<;%I&M0XjdLq!SF6&Ftn2*MEi4ms~=&=8VT@H)h%TOSA}cgqGtOzwsyNT!t}%@i~!Lwp{xcY~6b;P479?9?Ml1{|(F(',
        'm?Wat?UEOPXdogvW(=7-h(<XQ2kdK4g5?eH9vK-yoa=)Z5DjSPYjsMQS6dy#7yUucK$0N!0T6?>rV%{qOVuWL!G;(*8JpgC1(P>Va{M_@<Kqup&tE)n',
        'H)HR)ioJh2A&-',
        'kMY=8OHG+Q(5`SNGD>zd1u%;S6)UzD;}ueF)nWaN^vpEh5*`P+=e0}Lez$FDdMi9FVVF1E2Y!8=zfEVU+@rbwrS1Xu3Kprr|=p=|e%(k2jt3=W}UFxZ',
        'DQ!4Mpx9$a3|)dYf5)FkY^{5q<gz|4+m_T(M>)*ak3xr0?N|9!UoJK#Mg+gV2~IaiNu3u}j$F=PiBiL2P$Qj09MaJ+xt6|`v6Aw#g#DA;xJ)%02(muJ',
        'K#LJ|cVh@wD9Jkfxs^70dqryt!H9{S>dl&r(VWwUIevhZjLYN>SysvhmkBHoqC4PXYALK`OEaV5L1yp;!v88%44{YQ`Sy@3%He*D2FX0_v^%b(A$oc~',
        'g?*$fjy`@jMO$M)Sj`1Hmvv7VUAUiDGDsZg!Pq^afOSA3H1w(nsn75?C?*D<<u9Frt8ZIv`KOl{r6%87AkJ0v!xu4OF5DcA%g{+Y}W3^bQQ$iWpbwa9',
        'hHzm}o;IA(8$R1{lD`Ow0x#B*m;Z2sUQCe~qRVDbJ<ns1&Z8L7~jZL?!$2bcfgD;!f>M$)vr{@s`0NeB|qnHF|(fytlj;J$4;n4OttdUBEiPY)&Y4mF',
        '0FR0%f6#t=-',
        '&Ae%xY79&cqrI?XBPjHT#@&`$6N^C7@h_S(AVnaQtkaTlWO^{B;ZaPfm8H>KhJ@F~*&#!*s_XB(P?<I;Niv2mR(c=SGe~>A<eB^C!W_q$94>{@jrN~$',
        'l794upZbrKmmJY7NjwF2SZ!YE4XTJokBsi~VVu|7esm289S6rj0EftlZrSM=8Lg8uDg>PK`-',
        ')Y+}Vl9L~v1|>&R_U0CP^;6^96MG;8sntntD!bXJh2u&d^JxPfcXbDs%bm?beCd2qo{gbdHFl|<BNWeXTRVq++3T%R~&;$JSGc-',
        'u1ChJ$kIXL<Et!QznNrkDP02TK$RqIkS-fSp0yUcvWdTa5^(|bu54d8^hzvXERrUubL_io17ni%+!bdM4aR(8!?ir~l6UZ#_niHhY~%ii0qp+M9<@_B',
        'cB)sZyKzKM9c|+%=y2!l8+p!|&xLu#?(5>37RhpgD8^W_+jo+lc|3pq<-g(lQ_o>M86j^M3>-U*Y1HBAP1=hs>c4jk{^m){z2#z2nD1b!6+{F-',
        'J&!bF%<4h%4IL5{&Oi1v65HgsWuu(;o)-h6Njy$o>^rPL{!B4JcdO2S_JMzMvnKo4y_)RnU|ON?D_Dw!g0|22&CkA--',
        '+%gl=C@w?8x+$EkQm%;dtlQ(CNI05z5n|TbWfZ1?pf~q^cPrCUBbb=3tV{7ud?LW3CwU4CWaw*)K6Uj3iixVy2U(U*kUg^flzaVs>lA}(=e}DOE_tOg',
        'A0qqY06I?+)mS4&N<<ET>i3mar0k)iPx`O!qBQ;(#M5??purMx6D#Ic_nURTeV^k4P-a$#MCOpJrDCac!Ly*wmtc-S#TcjJ^PtuWN10`VoVaDQH-oi=',
        '&g>3W>%2SWNf_jpZU)9-',
        '(jI*Isc?*^VFvwM^vp7uN^_Phn%|%M*cNnYHvEZl>HT=*B%QR2t`5r>bt3*vW^1}K0u!JSUogOV{ibW%d0NB0BP2E!Pzh8sC&N4pX?gYE(`LQ0_bnr4',
        'V@10X)6Io2p+nQYSb*XzXcDjbmO!eP#?&qJ5;I_QlAjWNuvrO1mfX3YC&GShU#EU?VPn-aq3&xecx72UGo%HuRNAjM~`8tVwP0Vyo;PXh87v7GEf>&@',
        '^IfE2<DLIfk0wu{OW16KXDT-^PIHg7}l*>i}3-wWEu9vH53)N;61<1-',
        'YduX=w0uia^clF`?(9`F$>{Dlzcuz4`i_4VW$MsvdBVSGA}5opeksmz(`DWs7cl>NYb=yl&zu!{Cqh9gzxVM0t#I4)(gQ#Y}~n>HLF*HOE9%^$&z{%k',
        '{B8>At)gPRKr6%E6T&328X<4z_#ZYJ9><f${0l}qiA`|i%&oo0@5ys@=~R)+X{Ag#bcWT<&RI4yRX?$zEjrmXckK5VM<$4Z23ZTWC(eIdXEntNexCVB',
        'Q%JuA@b#mf>N<iwYVF1;P<wf*?o|qW`pGu6ZlXro14f$5M-bMqs?;5^`{IV>AP(Izg8LG-s^7UzWX-OOe^Ip5;j2L%0DcTJJjWv6e=dB5+#p)5qZvz-',
        ';r>zAnfl@?3u-',
        'FpP~54EXDn^6c5bew#?ynx1bQ*T&Hi+SVRmzxbVxo@2da7?Hg{vR_o|uz>E(QSC_K;onPh4AN>p?11osx*)OD0i?Q`4c4P=?<+T6gi-',
        'b?zjO_1}iw4R=%zM}&4}BvEyav1~-',
        '@W4&zP5KW&s=u`Gh6o&iZ<?!ZRq|v?9>9;5AWc>*6qxCPo*>a__Q$#_w0qinEGJS7db7)M12#dRE^OH^#xg{z>3A0fbRxgbK<Mf+;GR||ABhFPVWmTG',
        'gCYG<WIiNgc;>^&pnekvqbeKGByayD#)5T>4`7FtR2E%wFT2W203nN$;7^!r-uZD{={olG3|_XC#~QE*Wb;Bw_U-T^>|)-',
        '>^SwrKoOz6oWJ|vC%OFKy{vfmHOwA;8vNbk0N{tNznpEYNiKiaU!gN?3_XGuT-',
        ')P|fOGyKTUUGxu|b?r1kdS5pT$gjmd|beM;^$wV2NqbW1fuv@{*U)v_nLL188g!D-bD6RFUOFgj&LZxBM-',
        '`opY%C*}0{`9v*&=Sm}!d8n813UpVe%e6KdeQ~&Tv?)c{C`P#wzkX;?J_x>-',
        '^(Ggnt3|Ad^fZ1~|#*M9K%j?Zyslxy6MNV1sCjIrsFu%0^8TeL<@%l1`q6Sf~+_F*?1WV9RDj@=eE6T)g6&1x;gV!AC7K{uu_^TgW!M$!9AOE#?k+>@',
        'HvL>=-2$~jcc+4}GqJtIORa<C%e-',
        'o9lLE;x4hnW~Gi;VZ>9<>#;9a#9*kNN9A`T*}=xbdOqiI+ZG2ip&lpe(A88pC`MarCD)@xU7zhpm}@#231F<aIje93#UkdGVUFpwogpux9l-',
        'OmS#ywDfE9yj%JaQd*4~D0f;MRE=TIKEMUv`XgRB`b^&UpWcpL+QbZ3p=OcgF|3K<gwgV)!M5_5kze8B-oHq=b-',
        '$8WNMfWH(5ZREJLE<G_FpnO{*#%8I6@PH_Ihl2V^toPM*9CgmrZ?EetpgF=-vZcxog)>io)^KRqJ`<$?J(b<$_<iZxWEyq8bQF>GZ3XW|IbfxaG(E-',
        'nPGFNtE!Ek@eiN@g|;i+H=c&m7XD_F|u|H*)>O4*1!(cn37f*w)@(+;S>ou@j#7hf9qqMxAiZ7CLo)CyYiU6k@~1+;eXumF?s%n7d7p6STdBbd&BK~<',
        'nlKV(IC<oLrf$F)dXjRpyftVK*&*YTX0X<&0d}2*5Cd%e)BXx+I$y!vLIcDL@5*yZry=hRmE!{zhw`Tp-g<6{_Gz(pgDOvr&%OC^XzBAR-VxFAO3cJ^',
        'USwslno&$Q4nIUIB!_Yq3awOhTI4py0i+%o`HQ#ZT>uym;8`uOP8dYV+R^UV+}-',
        'doSi2=cOBk>Ic1FNKKl*Md+$Y0nm^O`m<y_p=4^k_Kk1JqZ{z67a-RN-',
        'GqK|-vTgw1D~Og=_>GsG%|90h$jP3x03JC<&XIHE963kMk@G~I{{y<)u&E?-1hD`B002ovPDHLkV1f',
    ),
    "DOURADO": (
        'iBL{Q4GJ0x0000DNk~Le0000`0000`2nGNE0FDvztpETYAxT6*RCwC$n|ZutRdwgTYwvxAJG{AuR}%$Q48@=zv#5w6Dkw%Usc7i58Wn@K5s9sK)6qC~',
        '#3+eL&>#*WCW?s|oI)5(L<JQY!%$GvNKLPXS8ux08TMZN$GMQiFlYi+b$6{l>Q&XfpYzWCoi+T{Z><9d?0_Ax19rd;*a16W2W)?}vU`nc_<_z(M4#?!',
        'yZ_h0o1HsfyZ%U;41>2odBCH7F7JD2RLjZ#uEF1<>+iTy|Gzo7-g>xBZ-2M8bccTAZOPAda6hq1Ta&+{?JdWt-',
        '!!6OV!4)+XKP+~^?pXb{^j>PZ9tk|G%$Jib3JK@r#?WtMZD%ZqMcXpyki&r%-',
        '5g3<22PQqvp1g77ru710f)~9ov2}h97e1A<0ue1bw5v_eJbq9$Q?sNZYr+R=vMk|NPR!p77?jzHe0hUk|CjW>||KF4uhOLRH<Pt6wtkqz9V##)!5bK1',
        'q8UmT0kYk%qOXf5@tTctFD=%hhih(PHj*HE2*()eGKy`r}@&d?3=!hF?`x)sJ8DOS<29VA-kRZ@QY<>8*5Tdr$bi)?Am6d(;Qi8$$bsz-Bsov#0n48B',
        'sKe^)rZc2|+OR1e2CX(m{q(OmREvzYI(<viJ7KPaj=@?nd%Z(wW)2|AcVJVnh<8?BUBNd$5XXfRKaaKn}Ff?8z%=BQ3DDhtU!#3(%CiFNa${Zu#M*C6',
        'ixkA-#?0%wH1xPq^Tc4?aF93iuLZz=!>a#&og<X`Vrrv2*H)!LXqRJ|>hNEi$B-',
        '0?G>1Cvv{;4QSTO@ZKR}@MVGa>ip=VJ!(lr*GFu!bDVp%N8=lDXUt>q;)UFI$5ndF39plXeXVY$U^)nvsX5($0BrdI(ypT0CwR_+$N$y4zj&ce-',
        '~CxY&|ndO;DM!#&NIN{gJ^97O$>t2-eg(#{XjEQUNKl_{$N79`gpoGd>203BRw)9$hU}&JB6~-{`a}MfXK{(pJjHYv;Tx}DJc>;*tCw-Z-',
        '2+*d+8il8)MQGBZ7#-;0Qdzp$qCy62F6x#)uK7Z-aaODC3bUdMp|mKx)JEZkZyvyG8uzdzrp_1=&Y>n2|1NnEQ8^lDb7GL3_-$v;D^d#TH-',
        '`d&l>gi<gjJ^HMd#XQL`8b#~0uY2AM{sZCHDW26KdFfOLpxSIEW<x<}Nl~iE_7<()?LX%?KrKGbnn54uulzOV9dBC`cU>)+vdenfw_s6hiE!j##Jra&',
        'MMNnO<@Ku=3A=^smewDJ<#29@dhu=2<Mph9uP>bknSwp^ag6ya>C?@a6uDy-IIhqZnB*FwmjmLx%4Kdb6ghxIIb_tk8cyl@u9ztB3V8)=g8HpqCph2+',
        '#2vSvntRRU8nEjpClHPeM$y7v(0KUX`*P_Ms5TAxL$1%-G!j@|xZh~<{(S8J=^H78aN}x8qgH9P>uz_?UOp;+;K?sVdC6qnX`l_1x0`UqafNmh9C*c-',
        'ejJB^pcD)~ym#D<3Ya(P&h6+Frnw6-vcn!E_iVigB<(|S>2pvo)VdkT#P0`#Dw1=^l5N09dr15@KL^MEIMtJd*!4Qm)-',
        'T#l!*@~^$3#g(BsDM`9BpN^z^@>P<><;|i%P`qjK^3fp>I$G9DXQqUWmR+31Q5_~-',
        'Hg?Y$VK!Vpd|zaZ=kURNgCj%ptT7!ph0o69|4$m3qoO0aZERlC+R$l?7R!CQW}R5#RzDy5CSTS`hbK2wTg&Tz{()T&O*K!Bn1oV`&`op@@~woET`!VJ',
        '`ea%Adym=E>H@Bv)I7|EdqjvFpJKvM`{P7SsN%3b@<>>vHMRI&N5FYPnerC>|XNgWQV>Cr){i&7>hVTtwBXlXDY8V0%H0e7K2L=(?z1AK?V^QgH16}g',
        'gA?~d&G;CLtY)R=#3E%b*7o?%~6zHurSx`vTKD9mRSffY7FX@qb!7CGom|D0;(R=B2NL}FVq8lVKF(V4<vL6TkpZT8l_mAwTQFOr?kez_!5j%|D__(K',
        'a9v;Fk2C$Xoz_%%F+>J*Jj3_RWSA}!5ZaLmn$o+C7&xu_I5etQzvuyZ$A&_u0`i|SD`(8F}C@eu<dX#29qml6k`J7_ahpkCW5jDCSuS`Ae~*9)R5Q+V',
        ';y4q`O15Yt-',
        '?2mM_gXTiW7(ueEd?3abUWLOHg%Hmtqxj$O`=K&B)#imB7m98HUDklKF~G8oGKHx@Q}{J%xz`5g_~kxDXvV9Z60^vth#Atr+8(o9R6{HTy*Z`1#kLtx',
        'H??g0bYHSW(0ZSckI$7&Me<5y;9mY1C!e;a~?#66Y|6ip#|@!Fp`riA+?5yLy5aXaPPC7;kW{VBYgfq+yZzVx&HVPVb;~SC_eMHG*}xBp`7@5m{25!P',
        'FvD>p1DMrFAqHedu;>esEUy3jhIDk0)9;FpvtVgPN^?bSPjbgQ4_735Zpe4tbi15*vst80%3dr~wH90ZI(HLhwo%1QS3?OHzkdeb%CTN?5Q6>Z9!X(K',
        'c?nWD+wH6G|l}&`bi6tLl>#C3InT2i|wTWAkh-',
        '`;7+zTz{@rTdO11W5p3UFjlcfu^4h6D1*g2u%_hDXBk|xgG(a<Al9I2C^TRKAOTTDC18W6mnQ7|ahI80FtO9%f<g{yD!2&9199DQ(CJO0x>9rlQEd>H',
        '*1-#c!Ipt!@lkyGuco==OE=4YHB@@mDvNOrv4S;16dObWLPcQ;FNl^jkE>I5yU39aQx62|F|ol!ieMm^>hTu_as?XrxoMiK4kw<yo3Rl?H-',
        'q++kTk(0LIeyB!HP3S7(4$QaK}Kors9Fo8DIv08E8F(Z+?i^t-',
        '6^@zI4X^Q$+6g;w5VD`xp`xkFhAPASw_*e2JoT3T3d>!Dxx?CP0E2Uk%L{LexgJ2B8B|K=2jq>5V~g1+JYjyx1_fAY$Gzg3k?cYOr-Bkl^SL7A?j<_!',
        'pQXZw4JhcfSisBN#gyoqd2XwGLCCWWjLu)ZNuD62OVS`2;PXEV@KC5DGZ#gaO9J8?^WKfPg9(3y48&gi0M@2FgYF9sh*&{qBQDI~G&@J1FAjp;HcX%7',
        'qxah{&Y)?z8b`6pcMLWFV7>t0DfoXlNla593x6MlOcXK!(o24MDzb6{dbBMZQPRK6Mp0-ML5h34pC$S8MGXVd_3ib32qRNK2@-2)hT_@uh#_=4-',
        'ZKhf)qZRIv4cv5tU2tV3M&Q`>)q^=&XI7(un-',
        'j1oMEf&tMSiZ1N>az(z4!<rb&GDwChk99c`GKdPayaO#gum#z54l*<h{>6lWcO%6ll5fODL(FNi?>sPUzM8#veT7=mB_1%Cp#W(N`8wpdA2a%j_i*Ad',
        'n|SaG-(&AwO49_QL<s~`3?c?4sczLIi1Db#RZpw}#-bhs0W4DGf~xV>qWWppBQn%)#`~<h=RtS(-MtA>3i%wEZ$REaoT8xvlu+jT4#2H{_AW-pEM0`m',
        '3L*u)yku~2hV<ai;f4kodhsV&eAf$@SfA0fhP(vPfD%>h6b7t8gH)|a=(l$oz*nt`Vk)T&c}%sg)a<efaqU(=y;h$X?SC#Hp#n-',
        'A5HRL;d=g{wHjtBteV7B&dQ7Q~U<6Z^poVtg7--fgu6ZxX%ie{g%Ncq0Fneb+w(Xc=bfoe;!Gc5}9_1iHD3N>(TIPLWL8}Rnu^@t?U<Gm^6b`LBwA%$',
        '!B4M`Q3igjIrXubll_En2HNMKjGxvat2)SYj6eiwx0G2_BLPV)0E*MY?rKQLXXh|F$f@(zltRGOD{ax1l#oy5w>L1W3Dh3T8wFPXsc^%!mdUShA5XA#',
        'U@MKW6WCH5ISwU>VNzbp*o(xRvFxWJZ2#}VDv8c1SREgpYYlWm{2o6*{Nzy~}Kx4QASYj9L!z$d@)hdSxRTzdU`a}ioJP6%?Ak1whlARco*l2}FB?%H',
        'V;M^>K^X0Yt<R>Mq3^El0kOw8QO5K9BLRVl<?(qcV$~LVI%=U!Dz<?7p3K)cX1gTM?1Y)t2P6)QT&p0-',
        'WXu(&$m;gDkk$neXQ7X<>L|OV_<~0y7U<K*jjCQwT%6m!j34%2wsUX%?{7wbD&?|Fv*?g|~`W7^VD)(b>0<p80V6Z_bMJXf@f}%)OR8ZzT?D3#kU$lJ',
        '`01@n?5iNp>VqM9~VW1fSN|M(09e}<pC?tmd)3wGB2p9!10ug9Bh~xv*n!Bi_V5ASW2$+CUfP_j*?H329LQv)4I=uSOKyb=bNBPcHWm~W6rOO}`q3^~',
        '&wdNxIKQjSm1FnF`R85HrBt}sJLQE|-',
        '`w+n3QB^c3ID_KB2*wzYO0X2Irgf1maT+kjf;EV7VEUC+Eb3zDw|tR<b`EbiHsYOsxf+?j8n%Cty|?@$3*IurXd-',
        'lSMTz>`1!W(@fVF~i4wDt^zVjS9_17c2ujI&=+(=s$XAM@M^5K3;*;k6R`ab0l(-%qw>jKtQ)ia2qWedt4svZ%+Y6ULpz{Fr2#->QE0s83W3@Ds-',
        'LQJpuD%$qtbeDdC`SXRy3&9wiGZi(F7$ij`Mofa@D1znWd5|9Z8<>UXQPh5erAvm%y<m(ZD-FIEfE?rYA&n7nU>ssftWjcDMU$awAhbJ$%!{CyA&m;k',
        'LUE=~EsUa%4vT0awoXNvwaSf9<<U@L2sr6cnt=0;%tsZ?k+h;bqW==g60oku%JDte+7U!OrA)_2U4+<(5R|-',
        'ttOQ37XM6h&KqG>425}baN|G3y6N;?F2_&P-kec$n-`j?-84Br#IY20&^bmQ1jsklh%U>eZ-',
        ';9aCE2iH^_dMhXrmXfE=uh|rd5r5Al*A2?)~7+ns<dEg)M`!QS`YFr0SKkT=Na}%rt8mqE0+W99z=>y3cBjCc}}CLxVl4ZfjFVpiI~_K7^!)%4z$wwB',
        'vi!%i7`fgsuXB{=%ZCghk)YnfT7=A&?nE262<-',
        '_sFXjch`NG^#TtXNjz=3qG(yD@n|)YBvJ1b<qV3nwn7t3_tp_uQab3i;u{Oj1!&+{;d6xAvh8LU=F%$)gA`r@=-?oLm#|;q2!ypD@D&-',
        'hakO;w|fM^$~CqTFQTuW4KKXM;!^Ar`qBXoTLX`pyQ=paV0cvQ5aNg+if#l>#l0eI?3N6BaZ?iO9NX&v)tcT@BVLg*sF<Gs-',
        'C7UV_5ydlHn?vjzEmLjiK-$Xr%102E_sSM&`hXz9#1SqIkMdpnXk{B(<@X<VA3M+=7+MlfZK8*<|LO|%2IdSd@45J3D&B(Ko;1!jaI4-',
        'eHai;U6>m9!kJ@BFnUdIZZ=2g)ivWCMrh!R7hRkj-+v%KV_6l*NL@YE!LNfFz{I9pZW;ug+5Yd$Y{`IUU>vP-',
        '$*nk`uIeDl^ejraaC^A=lB%aykbVh!YlM}w*QW6DZ9>?<~kVDc#*?A7@CuQWLF)K%QIeH)uMw>js9%XsbUpTj}spGj7{5KIU5Wex=BOs*q6?bmtx|9%',
        'Zq-+mtx8#Yh~SoOrUh@nASwRr^M$PlMB%(5l;%?~2I7Suh`x`}z?^BHa~=Zr(Pa^KM<^Nn)p4|@E;k0Vr-qVxo&K@Gn2)pE>Z?}cbT7kW^Gis$<qa&F',
        '#e8Mx_T#6fGW#mWVHIOF9@2-',
        '_cop*IlnjVv9^_W4jr=N)_+%ZCHUm?{3p$y1cQF1BWHu>l)!#uG<E94Xd9pk(Z%LCU<u9wA6g5h>7tG4lGG5PLD!b@{~ap2y|atf$-',
        'UQDh}$=<A63C=q@v^*vg4`Umgt*{G+;mEZc+I+uMcB?*FGd?Vs+!{7Es;^Qvj!*9Ks_kM1N>@yD>eACw{_Uzz+>n_3_vYb_~IUVl(5t|>GCO4*^-',
        'wkC5IDvX(C?tivPMB(A=Ss9JpdP`@6lUsDG`fK>|5Q#nb~$TW$I$7tX!m-',
        'Qc}XvT_)4)b62O24523{S9IpyRpj+f@*|e3piQSxgoWX6}0SB*wFocFxw5AQCW<4MI+>ZTctcfv72%L3r#IHRk;kpM33Lo&|xa>Sf;*@5yPHK8|XSzg',
        'bOyiV6?DCS3b)cpYEF=X)f-GK-2?^K~<ncCG`-',
        'KGagvb5LXWqvV(;w$qXZDcsqsWK<j>O)``%k@yTe>mdS=*8QW~><*0~YSy6<B*yhfQ;#pP~!?XkdgvTT*Kpx_gw`P!rz^bk=of)?;KOLc1MQ3rGZ0cz',
        'm{%UO0k4hG-',
        '!8s?urz;{<DMf1|6w(n3v&7CFWy6{QKvd9Qp9GdFsSjS0CT))DkRzI{*N4m!{LVEz1s<J!uFA{1m=;uS&}Xa<MDGN+y{p1qpU^EtC2P#Ew|n1>Pv*jv',
        'J(Lxx7vARXnOKD-QV&ERSlOrVH7cA157A!r8^ccE_4Wq%5fe1dZ1LNq!V@#A0{s4<u@0e%fO?GUnCaHd2#4l{5Pgu_s(HI8D_`S|G{5TuEXYfQIC_`;',
        '{w@V7V2a`!}dW&k{D(U1<edz?grKYsQL@!K=VEumGQxhKOii}GOJ!V~&3QHvD^&GF{#Tev?9yn2P<-',
        'RD=H;u?mIjoCQix#F*KrgtgNT@{fPff?_3(P4&Tm*gxvr-@mV16_y$a`=Vl`p?7AA_60bTaK1vsMe6Q4NQS?P-K-hsMRv2x}z{|A^F3X6CT`w&Wlh@k',
        'y828S3A7#i!(nHHa{PL;uIR3*)-gA&I({0CM><pb2wWg%L1)d$&AmK4zM@#?C=Fa16E+8>+<P*1Mhkfj5G?~^d6x->xd6oNU#H_pP`tUVdi_Y-',
        '1c3=+piab6UOVpE01q*?kNR+IAW#<<YkTul&PUCOH4f?sym`uo!BLaI8>lLBZN4jC_G*rr8kHb#Ki30F~Jc_y8QMfv#g)`S7Km10^My-FM!L^`Fig;%',
        'P}&*z_cUmnnkmSq6MK1tzJnkLd$qUfQce!2Fu#AM~bIzQhwjBWd}W`ZW<?wXNjZv*xC*lj9~mjl>S5{I+p1>o{PJ46N`VRhY<L+RW%;jld~-',
        'g%;icq7djd!AG>|+iv&W9sVEA9?{gO`B^?YdQ6eJ*4_Oxe4Gac@+8T=BmOY<x({(=+HcweZQqa$z^<2(mkmjx)frv8mh^gVlLShI-',
        'i9v{rVRKUOr9IP(TA`Kq=-HBob&eU6bHR&heBcs`j^~6$t1$KVAn{qy{S3O}y+n&oM59;Z{4Pe0PUz8Myq-|bdH!s*W%;-',
        '=Fb^`X^Z@Ubc1x(+81EulS;|buq7raMnBLW4bhyW^IN{6>XT1FIgz;g+eVYn?wAJv&OE2QK-nndAa6IL##fF3gPaFrfUL5nZc;IQxG5zGq<2X`!xIAD',
        '*kRbG?GKxZIw_&yv{@Dr}y{8+O^a_Z4HLI;T<qyhxC?xQvlWV-',
        '=xj9<53@%j$T|sU2r=W2LrgJ96y)BBl4zvOnyxVZ~M#oV@2`?Dz@t$)XDuKl(DKr8y8et9|Cwn-jcl}mu0;&eVAwdZekOqW9gok%Fc)`VU?EbQ&wlJq',
        'xBn+LMp#cUh%=-',
        'U$EqFo?v@X`)N{9H9=3?yjT^N&8i#)NT^Z_w3A_beB(y7(BqczKnDviuyRVWcmUy>>nj#(z0b3)+WHQ;SddAnuVK*VuJe}d*gpW*Xw+`(_YTUh^K!cX',
        'oj_~B-F#X!PI2PGW4%p$=vwlv_D8yILoT7xJiJ>uEaPriq|Y(cQ(-4?#R8#8?)>Bt1$-p0&duVo-',
        '|Y}*i6iUTpc`rrm{d4GdHydp!>RB!msPKy6PQGG%HRb$#7ip*Awo`71xw@T(T@JJb0(rECF&Q3a}ppbw8yjH^_(W;T!;@jjJI9P<2y;#W4oyWw(ZT4<',
        'zF?+vf%hxusu{Xp`6Lpq<JLiL6Q`T)&Rt?wrr6mo<wBX=jhtC5=a8QpS%^(;=6x9S@8^y^0hCnpB0OSZ}H>@RIv5H=AhIJ3zO9+;Y8<gP`dUF|n_O=m',
        '5U$cx8PJJa;|NTu||J}U|z2YjJx%PZ{S^z|ZL9wJ_@MVNpkdTrEVN=oJ=B$9uUb?2*N74SugvVo4FxJu4lB;wRH@!3E^p_ZBCWV2;11vu8ml+>C3!5y',
        'YxbyRT>@DBq+Pgg)b_x$nmW;>3Va~B~z;V>!gG7xs^N*-',
        'wPaPuIt=Kq)WB`ms8gm#&rMzfgc?l8C@ez94UxUqSeET0AZ+@=jkOj)*lydax1NcKNMScWs@w51~)r-',
        'lb!+*QzeEJI`KQo9=D79LIAyJ4D+VvE*b>2F)fp@fa@X>r1Ka^SSwmpJc$^Z_F!{EdciAB`#pzNmS;iMG-zq7#BB4nV6&04rH0_73J$6d(>FMSVhdCf',
        '80zN26+_k8Z<%Q$0Y#PP?}uyIa(+~F4*Ok)N+YSB!=M3AOXgnv<_ZS^{YR|sy1&@J%0p<7yxYIfPUwcwbS)(Hb8QWQi?VBHPaTFM0%o(Mn^!|)~R^gr',
        ')`20VedRBExI98j*AoMx|1kZ2_o6~IDb-fE9#+E*=EB!-',
        'x3fIBEL*no@)K_P7@q1{2O!Po_O8u<2Y4AgGpl1rY=Wmn&c0AKz71g|=M5rvs$U{L8~EmCJNsi3nSGZdrRg3_ZlRIhiDBEj`vT)G`?eTG`p;FBK^?wR',
        'g!+;YRliGX%8%242j2SHQF??rrzD4uw9kpg3jry&OlOcw!73@1$7&pMOAl9v%(a2fGv!BA%gpB1FneT3it(YJV^UBZiGDS7B(#SjJIg)+wVem7TME}U',
        '>ghvS|%$6%zeV1%&qa?FC?VEWd#lZ<v?W*C6+#PWfQS23|;1}~oJGBC6>B3>3#mL)QH5F(=xZ$-',
        'is5;}y37bEkR0Vh$;T!$nvHVVwP>%8;&DH{C|z`#OBYgdL^klr+AQ4990Cv>;LyakUP+|5lq4LLCH(UQO&#a@PN%D|zgl8qfseN>oy`(ZNs(~?JOsC!',
        '|)9b~dQhe)9Gfw$VFeCF2meDUm*pWIb&=J*`NKi`WV-A1zD`&{^rO<cQHQMQt}YE@%mVv<5V#u}o;v1jiz!wW{qXJ@d(ufz_%7D-',
        'm1(;p_R{{VL0q3Cpi$jwko30Vu>I>RG79U46C5ZE%8^0}V~$2{9tuR+uVGrf*-',
        'Y8pE<#<45z0^`VQ^YHQD&)%Fp(Fdpe!42BF>}_nF+)T@k;)@+m_}xSP*6Y;ooyqh=-v!_k(aCh^5d*5i8Z*gF`A&{p0$+chhk=M_q>gWteBt8-',
        'e{w_4B*KXc4cBch_`qo+oV`k@4_K^$s9BH<=FES-A!>A?5eQ}kyKps9djsS>)Qu8mKF``e{Up0eXm>1c_|t;U%GY8Rj52fcrx{8-',
        'd%ohC*s9DQO|XZg<lVr-lTD6ay#sg13mARpH<@_bu>7Yz@W=o2B?8bOR*9axVcEFaN<VF?0?sO?6iTDG;5gJJv~8W)Ea$3kDp4JV8iCeC&YDR}Qg=jq',
        'b3Srj!ul%%*KI6#=}|Q#RJmMx2GW#bS4p%aMn)2hZNv1JQPV(MU9@>3Mg5mpdG3u|^eYc=*S0_>hOv{+qB!zodK-',
        '6=@A?+sxW3Kyy%0AXqp2{{@qF{{IdtGi8pr<^LhwJIJn&RsSbF)iHj{`4-',
        '_&@@?~c9Z4|Va%`Ph&B4$G54211GthRn2>b3N8%U3P0xy%S<!vBc!QU{|hu^^J9oh&qJ95mtYCmj8P4JYIjYp_BE95@-',
        '&UXw<<jEwM`@r0y|wgSau|pby}8{w2laE|R5-IeF2|Jd#weIhZBSXJ-BP9=rD_7PZ!5)jzsHN4u+x|AlA!>+R1?q@NK*T1eGONl?$DbFuK~JVL7Vved',
        'xA0&D(y5!>!>6FMD6hLl<oVGo_pX&3BfrB&W~_9#azgKlRQljaO97m|SjyS(r6i(=5_=)^kwloF15E*x|^_(`_ke;+H3zm20WzKZ)V`%M8De#dt-',
        'F7{IP+5{q8Z5Ze3O#JbS<Ue-SXUOJV)ln}Viy^hutUqh!_>aGV$y=}G+wVMxGgr>CYt0Oifhek$9S0T<kau9iTDWgh!9U#VsW%&Z^364J-',
        'y$Rh(THFM!PFHQEYTT*w0rmf`kbR+>@>98hH39*=&(C!YXn8-89D1SCh6~aU0t5!v8frUqoaGNrGY}E3P%f}*CU@3md^8xH9Xy1`0ektx$Z+9PFpM-w',
        'IE<)CA4#%J6>&p?Aqoy??MMdCAPB-',
        '7T!v*N@;~wb`}@B{vkel)mr|q0`MtkBaIjzH=y1nb%Eyd6Mpp34xM4k;Jm<C3R`y@{(fB`^BLRQhHE##*VZej;kbpC=N)BPI4`hxvC^LM)EXdz^YAm%',
        'coj5lK)#N>J7%7_?KAeFz5AST{m?}{#1?e7l{8mcmcO{m*0%ne`&#;`^*T@=LGdJmh8<U4LUilrc+07l(In<&t9q4ElL+px24=B95}4kR@Xr4=$KT!-',
        '(QeP})3YA119rd;*a16W2khy#{{uJ$YHvKiL>&MC002ovPDHLkV1f',
    ),
    "ROXO": (
        'iBL{Q4GJ0x0000DNk~Le0000`0000`2nGNE0FDvztpETU6-h)vRCwC$n|YXBWtFer^?iHqGu5eit_+nq1c)IK5it-',
        '@a6oO*Mo_Vps3?l!EZS<T4NkN+-gZDll%}<v8o8*bD1(S1GsKt>2#}&uNouY-Rj1B5d++aC_m5N1-',
        'uvA4HkzQ%bL*`?>UqwoXAi$xYwhp*t+io+1r}Iffdv*=V1We|SYUw#7Fb|`1r}Iffdv*=V1We|SYUw#7Wglbr|LxSI`T37-',
        '0zmixyv5X&<3Q{3d>h5B9I7|deX$;5`(5nt>$>)mWb92yz@K%N)$Nmo7_WlM;ErS6K6cCo;0nI_!#FMi6*Ex6vat`qNpfdJ)kIpBSld_Pz43_iSHHEG',
        'xOl5<gZG=k8PaQp^*_{DPyf-B_I^bvi@$23jvFFpdN6bDhP@Ljyf#h=(U1#aMH#9%*@<gnid~URBR%3H5@6<Ih;CDJSug85)wQf6_4WUKdN{fJT9PDM',
        'C1tp!Q&OC9{k6@4go)Y%#_a7W|^L;;!O-',
        'bK`@9Hx>|cFX7k_$0Yo0Z6h#yS0RtY7Amp0@Uid8V)1J+joJWOmRvz{eVrTH;Kq0~7aHuGWq&Q9S;_*0C9SWrCP#iM<PeSVvs625IjP3l;Usk~PA2Fu',
        'oxP<rf7bOmi#Tr4=8qOsw>s^hw`3ul`Bp@Itg4FLt1Y-n@VvJx?Fshui$#T>7d->GQFUPeO>0I;-m`_iyeqPKJM@niODJf19RFza~n7VY-',
        'b9nyT2u2L5uy4n^{&E7oZTT+sVoBBEQ;*k_N;*v`9me|%E4x?H(YA=Ji!l0lHR1^Y4f84dgn(MVNCOR_5E`%^Ha)|W?RGrv?dP(5)$_?_io_bDswf_(',
        '9w(mI#KgpSQd9+}HB=R(eq7`0w=ZG{ynw=^51jYZ3;4dZd$m?8F_+ZP0FpET!1<I}H$p8=P!-',
        'npuA>li(NrkbPb`WNMU1Hjs|ZHxsqE`z3Fa%5B_$hLtT8l2%93R;P@CZ0-',
        '}neYwn*=)=a8f^Dhe1fK}gA$sYsPn6I48jCKy#jz<WgigTWHg7x!^wrj0ND?&w1+;OCF6>GX7o$OpKZAtq(UjT1}4<lH19)!pQ?J&>l9{3xvr%}kfdS',
        'R1ms^KkN}jn;-{Y%m{nR_p02V2vRFL_E%cSHXKoQ^EO!FbIibM=tb4Ic44YfSz8%)_-',
        '^}L+y<$Zat2gOCS)OI%4BUB_&aZC#lyzWWEO0e;YA`KEpHPO<ek;e(WlFQkn!$R=_wBCTGX!Y3`z0j<I<mt(F*`DUo<bL#Bt(=`rSXk~zDdnK(;(W)+',
        'qIbwVwzQLfEVw1xTTs;8<L!KxAncxnWaA@=i;=u&1SMa&o<{LYnFikPsI&%Nbu&}|`Kzu;56{0kr9_q)E$+QVK+q6$W^VsJ8F-',
        'vBfqRGE(&gS8g%!pdw9&s^Sz3H_7Kz9%i<To|%%Vv@n(L1tu<Od&&*6;dA{#!{}#5(QZvs{9t?m6Z)=U^PUnA`+4Ml=1QeLDrHFvxpJID1kUKA+)Zzm',
        'BTmO!}y-',
        'f+;+!NOicg`bHSJYiFmj|Bqh`vXsPnzb0Wka4i9&6M#C$)G`W_E={sre+=6upMm%0p&>E;k)nmM1Wj^`{Fe0?sB85~@2VXgMPTzD}UJiK;JbTeSx_fv',
        'VVFa^&8sh^jA?lPV-N$bCO<vIV1zg!<j1mSyU(-576mi0$-',
        'VTfk85@$eJV0a95N2#W*_OQ&?L#!K+ryndTgyAH`Y}{1#JL<8hY3?qgIbH)#kjN;8}%~&<!AGWi)Og0bP3Ns{?*LZEDldhO6=>49C`ft;p_D_KrkAR^',
        ';wor_i)9<{m9D?aSA`qp5k^U=Jv6OBd|#cNfb1tA|+C((iknmRb#wWL><|%2{8^Mkjq85*df-E_WYi=fAzBv!Z*%b!^C6*6Y)yk__<$k+$kl}$pCU0u',
        'KD6PMyiz3gw$p*nV29O)7&#iTVa4_ZQa1B-!`1R@l%|7#XC6i*>9zm!~`yjV(S882*jYKo~lL-Mg$SV{)S0jdcnk@PvOV8Y3JVw!0&+*+P<qK;BCsi@',
        'kc>Nc=3{JsZ1&+tkM$o(B063S`T8#W&?~-yeg-?>PDEE<L)bt!6y^E;p2A`6n23-',
        'fEM?&_ueAoZj9G_`cZ6{$4eEj3Zw*Ph$ssuuP?G`S&c2<J)P0(hH20B(>&uC3j>@FiO8~gd5(brM`#2`g13tGDR{-',
        'E7V8X2&irNe!X|82V_G08kj_592e(f0qkq4Kj$DSo)M(H2(UNT?%0yU!rfiWg%;GWFG^SFSf^d?LTzVBQm!fu@-',
        '4811;1H*OGG<_+K%B&2>N{GznP0yJI1)s`i)H#d%PICQr(EczXTvYpxZ!1_W<5b<G1ia~Lul%CFBRd{>xz`h5n%{U4Tx~gSMyIz3jZNK857SK)By52w',
        'Yx+v^mt;N*6@<ze1cB`%3*~QkAH-',
        '1w;qQ#9%DS&#$mGV0A6M&m6{+F*1zI9lGK47PKd`E3*Mn(Kn;k&Xcja;H6fB#7N0)M+Tswm?0hY%HD+c8XzX4O&SK{4UEo6kYpIpt=_{H^LLrGE1+0a',
        'gU-TNM@U-',
        ')dJY@p@A<LJY$;6(A2&4+$f=MxeCm~J)o^#UGobd7rw_kG{NwLPdXa0m&y!~JC(|P<%!Wr*6z=6>jgbg&BK8y$|DPB{YPf;A!gjhnX7O)b52r4zOlRQ',
        'ug8T|fkCTBj%Pe1uB&c5Q8Y+Um^#2b8K$%mHZ*$n5tu7#0ZDgScWD6_MMtkk!7-ed^6;-@wO|C0uN0iR&o<j)8tz={PtQJAS0Yg6T}n_t1MTO-',
        'Qyd*bnjIQ`W>K_{BXWUGAft9fqOmM1UGv`8LH1gdy-IAS~=rw&m|WCH>U7>x*suw=k3#b;+Y{(>R)zWe}l<1s#kTsA_}kmk0CEz6tO+;4f{Zsni9wwF',
        'c;SkhFa+eK)$N-',
        '8;ak11P=)B4fR6<PAeKOTt(O+d+aXx?wYJ5NXv!C|Q{X7Lb&7Gpuf6e}Tbe)|=4_aDF~5to0l%xI;7E3aR}A_RlOXaG{**Lq3n5lG#h5)rJo1Y`-',
        'wVaZ@L1Twg|l@XohyyI?QLw}yY&5{W+s4uW)QNXiLv|Rr8F@po6tSuHes=t+WYb-1O0kTUXetx*4H`l<g9~<L6Z=2$>Q>XQuA2-',
        'P%7f@@CC|tt+%448{s6mX7ItV1hip44z^*n9;qjYzSk@13Pp3h%z$+;D@`)&+^NZrr#QukFHF^-',
        'tJgzkwwY$ydX+CWGiu%JObPSw$Co=ZCZ7?O+;#~IYYilvsh35aTzAPw2Fp_P1Ah@CR}h^K$KrDdI<gThhW?c6jpNIa`gO$xv5`46!F&OHp5_YlmlSVc',
        '0d?tD77A_Q~LzxqL%%@8km&DG4#6-',
        'dWwEI!@Pr^nLfduTUpWWx}`x?FSd92GZ5S;wi!EGaQgJ%S}9qLEITY&(HwPz+T~sA`N+*f$0lEn?#ln&TX=cwWT%e&HWqU8a~#dETma@?Pj$C9M3kps',
        'wyxKmEG~Got+Lbi<b7Vz%v?;f$t1{m%4aIb;GZ>pw@wwhuB@9YUo_F4II))I~?O3s+H$56A_xY}xRAR&Ux*S#sR+A2DzH_EOsXQVN=<K^iGa8%-',
        '=GNVCMYg3nYaB@-NQj}Z8AYFfdIC(r@~X`;<8rz7eiqKKFZ)3r&a+!QUkh-sAnIXFbtS1}%H3D`)<1vSDnV9k0<c16mvcN@I-',
        'NFa5?7f3UnO@C+T+M_)3y?|0JIFu1+baU`#2KNt9(+UmQ425hH&Dj=kU{cGJDf5wYKTW=47V(B;sD;sJ1yK;wk~Y%dTj&ZGv-ORuIQo(RF@VW)VgDSN',
        '$vhQT1{_8roH+8@Op#W4?F!B~x5$#s!hy$feCLBoTuX@3CX|4jG$Txr%|f;T!mMDeC3Ja~J_lyns;J2!zV1OPiWo30hH#~4ai^f)Ge~-',
        '9QdpsZPplcCl2+N7-i6pIOPaS}ok3HNdd2xE$~r=}v5d9_4DSkg(^XaO-+6#W-',
        '%g7xW>K(;HSJ4iS!2;ezzQaW4?UXalI0MO_2H`t0W+uyMY`#XI(gqsjdX4jTneqJrT^2dFzGRI79$xV$$@D=vmOZ{$Uqnxj4`B6i5eqJFu(gSbpdgpu',
        '`oAlnBE3)S(vLFWC3ju=-JQP$>O0thDRq!ZHZ_0okCy?&U>7ssCwd9`0R%-',
        '!d4QT86&fD6Y1ClH|`jw*%$Go<fK3`(@0}$L_;fecV^yf#X~3|1<ewWCsai+6m1K6Q=sy&pc@2()(yqffLIc(yU;N)Ri>E`<=Puk)^!G)@<z)|U#oEW',
        '$3jjz#>3PceJ?7YP9Im1;UCPg<10Dt7<825S!!wJ;0m~Q^|`E!`*?8hF`~Q>V(Uv53&sk>7FEF$AmfgB)=)U@ShB0WLt{1z+JoSMWWKrMpKzWZ@0y`n',
        'ccukYEWX~kK!~tDATj|)^$&KWiuih?$m6jd)TC&lR5FgK*ph2iayg;qJ(7CDd_a1iFx@{#(-',
        'C<Dn7+3{={H%D3XIRjRNOSPe`Lq|qy^08dh`{IpWv~b`^h(ih#E51V6y=uGov&Xn(#JZq<nyx#30iSTM6-#W29Q4lH>@m7!6TU90{p+#B-',
        '3A=Jhl6oDzYc5EB_gE+}Bq`Xz@!gf$k&9|$Ol%|aAsu^2Ko#JUVFummlJB!t&pUgeu_%aJcQE`HxESN$MIUq{HRD-ru*M_{0-G0S~-',
        'EB79#G07}PZRq4%x3nC*bzopKw6|s$dT^4tu)a1kfgz1kDsjx%^nRLJ@=TV8shWs*S`j?qXbo#aL>mbxVkN?0QH{~m;j8mYxj%F`L<uusY*;Vyq8Jq-',
        '8)74Q;twBhOGXh0IYd%&5|OnzNMmRY@D9Q@%R9I3<rDAeqis>lOV5h<?&mz;{H~>~+YkY9tlYD^#8fTivP(MAtmnPA9K;$Jm<)xk5Q9>Rr%7yzctxD4',
        'hmP@#PK{!X%=b4GXAL9<B*1Hkd%V@AVZAx7DPdUuXuhRX?>c(H0yUqI`gne_z)<t9{(VLMGl6y9cy=C<3ZY901S*uN1>jQ%qmaXnZp6io3%}5eZLV?M',
        '7w6c$A08gbq27?H($tzTHaSI5X(M-zJ-A!BsnRZa-IaNL$B}oEK3c6iyz+R9vfkOXgcuP*ikMtT9*f3VUbUfx?fWV`I5Ntd>m)0As**BmD{R|8NW(uj',
        'a>iM0Xe`)3xaOrbMjnHac#K({Akiv<Wjyty<u(r7wwV62LR?LW8ijo$j%hu>xZjUt_R?Td);<3XI24x&nf=o7Jgg&p<XZ_}`socMzMXU4+rs1lp>vJJ',
        '$6zx;qi>+){7%W8e~A3R=40NhcE=tTMbBbUWg|YCsV@P1fRzZL?(`bX6N=@6ldomfaZ}`?G9UlOKK^ZciLpvQ4bn=7^wTA4Xx0u^M5}4B&4f{eCuN)p',
        '<8#C8^Lr?}iFzX(A!`a0OcUL@nocPoHY9M$E&i7b+ef%?%R1h7{nr`Pm}h?a+eFov?w)|(pSOl<-',
        '*Ympxs;8cc@%Tn)!hBBEq|6L`X@bwr*6MgjG)u{Gd3;0jr;a(r=z$CjMg{)#^b#s?;{+RFZ}FO-kMy^il@!-',
        '@pG2)p@Ohz>poI%nT$s<G>}S4UUN*z7=aoRpE6r5Q*m?5GDhO(P*TKL5}C#MDpm{3nq~rLsitKn8R4+z8HV>cW{M4LKJ%T#)hhQ~`F7@pAK<ke-PpLs',
        ')KtRG@-',
        'WpuQ@n%XNZYVWI~vxKt*oXkJ%U^|B#Entbu^hJL==cjhBO`F;xn(ONhWAJs>WbjCm;R9Hh!?Pl}46PWHD_lr)XP&ltf}`u0*0$oRm?Y&JP}0tb|y}k<',
        'm_+kN|LD!g)uGkQ6L8PaNPEjcZwR@{76ay35&MZsD?1dI)XI37@>3u@sK`%+37h-',
        'G2oF0`xxj3LXFDhp8pwK$Rn!K0shHWNOVcB+V>p=qG1{zV<;1<pZ2?`aTN1gESr2&ek_<=h{bG!KGwfKh5+L7{L?cHAXd^AHxVh3=WII*Jo~&x({fS4',
        ';<UTBh@|JGO&+Fy4KRM`PGc?`3;qOF5_EA3yog5bRglH&R5dC@o%{2pZX8Vy&u%s7#lXIx+>nM^9OI{ImItiOuA_+<e*$4%~m*WSxis=E}nPnPJ&}2&',
        'N=^H+B)-Gb<;Y6qz$igh^--1>SGuRsn3B}L@cUG#U-=^-',
        'IUTQ&&es5ow%5$pZ*W<CC>iFFi{s={?etK+1J8n*N1$4dx=kuXK6m|N*=r7sDpOj2jxKBja$^kt60}{DveVSGc#3I9M;8EJ6=Mn02YJel*Yg3MT-',
        'J9ciuzW>N#?@N-',
        'nQxuMn*bd1Nr)O&5C(lyW?+H)Uz2#Eh##+Ru+4gwqb2qR`Yyhn?Z2%QN(DnSqHJuKHe;t+(7y7%ic<ZyEart|k<C;rdOy%SD*Jlvmy{N%hpvvH!}K9M',
        'qusvkz9_L_K-UXIPax64e^ju{pjpw1v<*7Q0h8`^Zn@=M2NMLtHcRe#Z13Hgzl37YMY#$@yN6Z7;F7E2VQ$h7s38o2=sA(LOeR_e6X$$c|U-',
        'rE$@(Xix4S-',
        '?NxU?;Yd(n<g00GJ7gZQEg{=^D6enw=z}U!w+BhYbH7;dFRzH<}DrVT=>YttULFI?D*122YsCHPkIXX<WEpnS;f|kmm<?C<F!c!OMCDYL%De`4JO37k',
        'T)FnVX|3R+8fe$ppX4`ypB0u#+{=VVrd}I9QTh-Gdp1MD3%sxzB0hrtxLIY_$+SOoO0MYhwd1rq1?brZkWci6Qzx3G`#?3;k3+|bQU_feD+PeWW%|<s',
        '{J@FyyY^EY-=ZoJGiRULw?y&heW(TS-',
        '{1;TY2rqvoLd>?ZXw45P~3&i{QFF&*y?Id#Oy$Ff}_%cLBEVh<SKyC#}s9!w1Stx)Ob|kv6lO)`oUkvQ4;j2C@cMx|n?LUKUNx(6nKWV&C2Pk$rscS5',
        '>k>6=>wh=sa|$ol}-<CYggu)-yAHA0xY_`1)_}<{6zwbH>w7<;82x=c3<T$k6!r57`Lwe_O!!9(JP^+M2*Zpgp*8D8)+8vMi5{&EjLvXmURp)4{Hh`-',
        'o=}rqi8lT)C9bUw=9+g$=CAyn^4?uA#^(dSnxAg%*lIJ6$bHsZ?eWQ{~3%*3gy7@wfl<Z&XHxn4Ubq^<$@?%|}t2`94RQ*HEj~u%^WCMz;|qmSr7F5d',
        'us#Cdo|DA)9G*2_O9Fl?*ih8dn~F>IJ<1t*S}hQ}Zx34slgUW}&=4q0nHNOFTm(Wg1!nyitsem<V>#Zck*%L^BO-',
        '4pUvtz`eUUw*6FY8@qu!%O9glUPhlBMa~vUQ&`b|EZHPSwkhK9B||*-OGT!x-',
        'pBVpFv++y)7ocfZd%Q)ci&0M6cIu!j+)LeS{)!SS;85Es$*w(JB4yPtuxEG?V(13!VdON-9p&1o_O-WQ!C)@-`ht2N$YT8Fj*)x7+k2-',
        'N|wnfPc=#K;ux7q5DVU?OjQRk4$N#w6cjk)S%=em%5%B$Q!U&!_H&e&rRE4iD|EMaQ#2jeT1XTHWCAFJWpqzU^V4Hqbj%oP=P<s7i?-',
        '&NWeljX&+ee$HlpguNR4WcaC7M*g3z$Hd^4e0!UlaI+mn6#wsH+hOgwp)JmnF%O~*N6UyYU{a_mL10n|JcT7_zCNMnaJ0h*MVoEpbq=#bTvi;pm62WW',
        'Bq{AOo~cw`S(Ph2x^hPIJ24HTnxLZ4%zGRtB85t15mfzZ)%BW83d?|skNv^KW!p{w4Hn1mVUnUfhXFvPDQxEbS%M0C@TD>ADO@VDJPT(o{EhyCQ&{Cj',
        'dbG9Y-<4F1r*%JE+c_`T7SWMJ&ybknVQUipsG7&j@VU<gBDc2-',
        '!mIM2g7tJp%3$>{^s(hBW*G<QvZma)tOJTrVf4<`{}JkHINKPGFJvO&+sOBvBT>y|x(=GK79oWTZ$u&Q(xZewt46H^^4iRU~?HA~c7Wk#xa;}8w-',
        '$&3Ije&fYjC^qrn=U>aFrWQVQOo6lSd>HB4K<|fsO3ry~cQd<AKeVsH{LzQV9eS1=dH!SiyW1ZnQ_RzSWM_S(w@aycp&_54R!!*X=wN(&KXEzbWy`<8',
        'Jp*6kKZehQ;kvtLrGcZGUQczZ##lPdT=E-s>{!FH6+JXHg+xxsw3lc(uZ>+dE@QehL!}}(Zy|-',
        'UR_EV53aF0(!N6DFDgZ6nf?oUlPQJQhn%nj~O4qAC%+On!p0YQv{-',
        '00buU)c4e%bUjT_HKnaL;G)VJ$S~l_0cKvoKk+WNS^dh{tDZ6q5qaKJijMdh0kVyH}D<wNs3{5ZBBRol6O(Bf^%1pO1f@sRvGF&GKVd+q#D{zVZv)M2',
        'YQb3lHzx#nNIk=`7HkLDCqdGT$fp-<htKS@f+PNDz>M41H@WPbL4YWz6pB*UN68@y4%c_2-',
        '@!oxGJL{Q*n5ElWBr5@+z*fMz_ooZ(eht>^e&&k320+)&*_C^=jrlr*KMsgd?z1-',
        't!qJXrfVBef56eD3o|?&V0dpO1X(9IA0QZ#d!v!n6ji4Ogv!PSq{v|8uks!~>)$e+iz{LV951VxpN@?%#VqgS!Jv2*w&B2}mV_<ZE1g*QHc~J*;e9#^',
        '$vH{CezId?la|HbA0`ma5F<M`^TuOeObn|DzYszEYqvL_9D@C9M#KqrCa_K_+&`WDBhvzHWlsZm+@|e|0=50q?l;g#vIZu(tP;ny)1IjHeP=ssw0aIP',
        'S`SVf)rgNkYi=8P0#fZ)u-c#jOvm;Jk<4i!oJJM9*fjb{ANo>PC6iPdv5qe%73|4OdGEB1bqqPI;n@y<xz+-',
        'nWn5FYn_WKMW{q`d203AuG1o;&N@1DrfbFT=(!KL*<wmV@YihF$uml{(n2SW&;RqGvj~1fyu@-',
        'R5av@n|{efKY4(@<3Gh?H@sW;{{@jiL(l+Juqunr{iCyDVk6Dxvs%nIYJADbTDs&V8eesSb~XgM`rY497Fb|`1r}Iffd!u6e*pp-',
        'zC$Nuv8n(7002ovPDHLkV1f',
    ),
    "ROBO": (
        'iBL{Q4GJ0x0000DNk~Le0000`0000`2nGNE0FDvztpETa*-',
        '1n}RCwC$oOhIEWtH}S@B5x`L)}}sx;p0oO=FXDXoARyN{}QVj)S6(X;4H5KON&RhH)4i1EZpdzz74vCn6}INRk|yhNg3@s_w3M;|cG(zdz3H9{s|6I?',
        '%wZ)qAa4wd&rxPM!0d9iIK{eJ<>=J+{a8*dE(sdu)&Gu|2lO{%ljP#6ir`O9e?$zK;OP7_|05d58%SoxQGckR&K=uv?zPq#JO<t8mdMS_{g6Mp|d4Py',
        '$XAAb<n4^MnP3L!1K(qIBy_G<X3@d1&L2R7da@pGouio7C$XK)flURf?oz__I&MOx>Tv85AJmgE4@@4-',
        '_gWqLK>DUw;xY9$IUR_Ogpdp%kDrMmfZ#q}Gw9DT06qD*FJ+WT1%%;v6FG|9)ygfi$kaz5&$XWV!G?ALQ7h59TB9xsY0A7<Jqiu#F~&MjH?9D#VX}8=',
        '`TP7Mv>cjh{Y2kp^M~=PWpd??c+Gaq3C?&{6hLO5+4n=G!}+6Qx?OD1~zl=Nuw}a~Y7H=dot}8ou<UFLA?<uitF|dN20?esPk_n0Fv^`WA5fF~`wNK`',
        '95?!|4E}HFo(;=wuBfW4!%S-(}LIKA!*eBe;nXCR~C-',
        'p_M`ekdVkKe*eryNG*pPFqa@S<UEb>G+Kk&b>9W&1m!?W7U>F&=X*G7nKNTHAN}A*x#7px^ST94oW<9QAn*vZMw~*l#%P0X%b{NUEq3@Z`VV;vGrFhq',
        'h8YJ@2sMk|K7(enjxq}0*W_{@p@E|ho6Ghc6Fm3a2AqalfB7_1`nuU~$yBCJD(;FIk)0kWC@p|N5VQj0Wgsf0Si1BLq)94P9AOZs*ByX}MUmpH%|a1}',
        '#V7O??ui?Sw>|>E#UJ@9W9zq)H0v~+p-C&$lq0Fd>@$BVwdw@8n9h>VaYxU`I^mAHo@AoxQ>nJ|!dRWTbGrdZQ-_E}oMfK6^K@E;Mk~-',
        'dyE#sTG)<Y9sL7A6`2ipL$cNPH20&*M(zr>~Y+%LWBq1;kdH&x?1|Q=e?_5t09-Gz;VFE>?*`(IUyw-',
        'S{zz0oASBKA}o_?YzMJccrv{IaP>LJt{mK$z)m>IMBsWuvv+jI2ybs)}yWQ9lT3=^$dRa<F9geVrm0CHi-lN$%P@ZEpOd*64ltlO}GMGNM?Y#{Z^z6C',
        'BJYBp)q8#Ln-8>c9vv0I*`fAL9};fU2QtszdEcuJ!U7^86toH&vsVaBvF^}0iZUDZ@tWup;Ug3u@LX;!_kg~8zpVJ^t3uLx+#D)-',
        'LQ!DXb!Ijj?$6`~|1jbk=Uq&)oG7AoTtbaiyRA|9w;eh!SOG{#x^;`7}9tGj^|m!>qM3Saoz_ZS}?CiHxa5{yw84O+M82b%V>$C3NbrK6k!0q4NEjGA',
        'P>A#Ns|aq1zQd-jn$`Se<D{rOWwQA#69Q0P`!-pL)aV&nkp1S^gtb~Iv(Ddx$w74dR;I=VU$>*SJ;T_Ue-',
        '5kaVSE+Bu|M=|rez=cFn9e_0}SCdm3>u80QfF`S&CM!UVi8?`Os5hH{&cab;0E5~^OVZd8MUH&nQEfCCuSA47!I&2H7S|%&3MUpPfXje&o}uO$);H?R',
        '>k6qiB79Hd=W{Gsvh=m}K!2|j34i%h)-37gTZMr0s@u5e7ry}t?AW>vm!?@bS(jau%{&aJIcVRhocXpx7#ppl&}gk%<h#{-h-',
        '5!5bCN=!xbW<w7#*2l^`>Epfku0+{HH*0B$AR?OKL4nSsa#z(R}U2aq<P9_MDHkj%u|@k|ez2+_M=T8I{+>1HG^)Nwp2_gee|Woa51Im2#vo%42xjHo',
        'Ci~!p^QlJCw^J&i52aqX{m>^L939|KZi_Y~lXk(v;Fzu|zgyW8GuTiaO0OqUu3YfkWZ2D5nq+(gd6mMx$-4s6}WU@a6-0kyJ=hn-OpkhDSzTgAi7ENu',
        'wI`ZoHbciSU^6>2)bxJ~X@g!7DI4I!L`XLbD;1+S^f9<9iyT6=9%pVhO{LBu%q?Cz1i}TDbjT@2eCFp<ZwD(Th%I-',
        'M}be5d=$99Q8E830P4G3ZpfC!C;KRZ_m>ml;{pMHc1cxYlTf)M(FA&Fr}~W4_h-',
        'a)89<G=?=A90qnWrS{lm^Wqn6G`KcZv(3{h^*fLsbNAi6PY}&|Uci%~S|0Lde=DX?c>PIQT(_oaM5heJZAx_gQdx^p#D9OSxgG{x4XN5tbz$NsQe0th',
        '*SP`6ch=hm}TnlWYvuba2mRFrpnL}HL70LLc6Y7nGTD4B4T9tDzIFGw-yB&12dp%HV#0xa_soj_uYy>?;#T2DjU4;=pkMr6YQyz_Iocfv#-',
        '1V~@eo*GrGtb53av0^P)h*Rpgech+y1OWes4Vxj{#KcsgV`C%R<c|mg4S8cidJY*D6KInd)rBiXt!vOYf+mlO*m|tRr}Bnu&HgSMzVVW6ci@Np#mSO4',
        'ihLWaN{EprD=-',
        'sVbFzcMu(a#yzn#RQbjtjg0+v|%|j2(;>g1fB_HGnLJv_Ig#(e6mq?4_WvWZY3tJ+BQ@EDQl}TMKz?DL0RU`}hohcMDuXI@f6QR|)w7Th*vf~+p@jR?',
        '3FafA=_X4PbJXYs$fgvyov6coJrvgTwY$Esm9yb=_l0mkQ*75UsieVe|kwMnK^eD$3e<(rVBVvgY!8dMK<yEb_uZ_bqK8gUe&O%oNQ6L7qrjODF<?J7',
        'HACdv71=Z?A#0hEZZQJVklx~5p6rNES?V(W^ZNLvPvVAuf5ifwq5yap%9ih<-d}TFiM-8lC-nR^W*$Mb#FnYq<@Mg^C<ahoB|N6Q2bHV8+^QDiU#-',
        'Yca&pGE`M7<G_3lv%_v;t+o_Y9uVytH~9AG`Du_<kPa70}x3>U{&_<NJ^c4S~^U?XqKNg{O7qfy!iku-%yoyj>bzM&wgI{DJqdXyJkuKNXA!(dH-',
        'UJo85~deen!_W-Col3J6Zrziy}GxB*J3ES~LIiJqSFtj{H)e@|=uwXypH80THQ)1<YAx6e)fKM95L`lMErAco`h_;}#!WYNAzkQH@`R0}AAjhhen=nB',
        'U6SgBd0PQ2BC>ujsMO+;v2}qiCBABd{ikFof$?}~-5MxkcGc_A<sbjq1F=^5qzVX$M(AC+-vBw_4-',
        'FN*8Np@!lJBPQeM);|xXl{&nB55Lf&&BT(`eMsx_SJlNNa1%H;y3J#Y}m*hH$BY$vpWfLAq}#`AIAxmN}cwij~0h#6m6kTqh4XvsuhUoK*DLbjv3H38',
        '*4&T&veoNOw@#-4ame6h-;{{j!4Q*3aPXP6`(vHF#*mL5igI@StX`9fnVFo!;h`wl=F@yiiL8%z-',
        '<rShNlJ5Za0Rob=dI+jam&U7toay<z<cigcDA;!VfzXD>cNCphWOH+VI0%cJc^HXG(J>ivEWr@B2A&g*<6u5$Djwc3f@}%-',
        'IhqwxegxfZ7<+sA3a`YE}^&qn*jhv~yW;R+_9$$w9t^6#Aj77rYR$7TuhHfjsHh5SSd+T8vR>ZCce|?>+!+9MgE<=j3{irtZ&yzy}j!t);198<qoo#Y',
        '#Y>J}&Xe<x4~jhsrWI+VfDYyhp2jvsMTKk7gr6sQ`2d{9Y(eBkt*j1=ElN`p|9Dkj)K{Ow}>Nd8iH`NrG~5)-Q?%okQ|v?4-',
        'S5(p2z#m^~G?)nUU{m=Z$W;N{E2af}H(;>2bEYP0(Q?0(lRj9z;oY<dxn`zF+DnYd{kq36-',
        'eE&**p$_4yVf$f_%Q0^{aonVYd5a!W<?`M@TqaBLC_lS}RWqP4~F7z+LEm?{=dnx+x4vb_T&AxdWV{@RC$3Ev_hCEbSL+YbQ5}~w1f)MGP4&`p}bA(s',
        'E1??xOz{4%CVn2TmO!n|fC5+BALua%6h?m=a01p4)O-cpb(uh_O)J8GJN5?5Hqo-65);Nt-4pD-',
        'R8pMq{+ea+cS<spw%wseJMrVqOQYh^(en8;+5cZ&poru;bG^$a-*b<?iQ5x$UrL(6{dAc2*-',
        '+*nO0+lgT>`+q8gqZe8(A^K^GX4jTL`btjk~s2H^HlelgBK<E`2vC>2n&CplH_-9FD&t}5{2ks2g;v}-',
        'a1B<7`CFg+=C5`l%|)$zz{~&k*G!_36jPrm*9B;T5FWjD4jKHT4_8_qm@SK08t?lhN#{yR0x3xfe0RgC`Af1I&;{0vte};l?zcSMk+3o#PaQkA3$FRZ',
        'cz#2X^ayB6rm4Q<3W1|D)c}>;CpB#Xu$LRS3wU{9=V{6M!tyMK8)VsV<qADp@oSQwKhQ>dH_GCAc+Xe?f51jb`Ilt8LuN#Ka~P)R0gW&BPs;HfGd=d_',
        'BM17WB>!6WG!6-h4Kv)O3>AZ)T>Co3Mr`2ARRsEnbVQEvnUoc%_ti>Ilw9f+TofJ@gG+1ovM)cDgdZe0iA5e^8)P15blIe;mw?iD*H%t47Y9-',
        'UVS~feJ|3e%JSd-9OWXM7?NfKr3`UwapKS|6-JZgIHeRAACt?I20j=MU%+#Upd~7J2ss1w{!Z-',
        'p5F`;QU&w&bpxQei%%K89Ub0D(cA4yzrWP7aT%$>x2+k&%j@X*^Y0d5ju=~@GGJ4(LV%Oe9+p$*=cJ^YMBY26!4@11EvuTEH#7>c?hISPWKkh6JJ?wa',
        'TyF0PY5~q;F8TBxpBDF&593m;=62$Yt1SsW`Q;I-ks*P3(FUy9RENm472Js9!_8<trFCuO27(W1|@BvYRl}ry*Mi6BYQ8=fF(*&`tz8kmu0o?w%MGC-',
        'Io-',
        'p(bX=zexrlCmUCdOH`f^tE#eZ`|Bjd2#u+naK!oytTL<7<+{(Toy|R(MX6rk2zSVw*rS8_!wQn)~kR|97c37NBXfIY68Z+0hy$3a2vCENR9HoE4JRMu',
        'P@uCNMId@j?ZSM)N=TpI>;D=E6Ykpo^$Kdl%X{N{de>u^!5SpH4tpp}u`Pv*yj`oO7?B+}20E5s|vAVms@w&Z02bos%>Nkb;YmxCYg6XoNIdgD4O1ML',
        '=s}&qpd17_Xq>8bo!ZSpm<$cpGY>9k(N(>iROWsRd)fkA<inLvsX4nrNd*npKp}dN^bBs|R4^(eEf)^mXK^?*L(TXp=1tg<+1KMQ1?JOEq$!45C!liK',
        't!6SfDb`Xf#u#CC$6BL3sR0()vP%^?artk_ROyqZxQ`f@Ea`tJkB32a!e%8e@>wTB4f;u}C#S?U;d-eY_OPo~9ZBjVhR!qJc&uV*Bt2r32qjVd-BGxm',
        'OXuT`KjtKc&`e65V<cVS68!|Kq(>b_|jWb2Q=+oK-',
        'l<=!&%&<5ybI)>Z)PK!YC!9COrx4Av5^`^g>HVF%GT$OIA^#%3?Z6G0~_Y>nVo55d@Ws0^WOgfuFUMu>5cHc`aTY+ye&ggWC0>a)A3K01h6u@${z8#H',
        'R1d+Zzz+@}xig-rS6(`^3YUVrky{S^gp#|>wxY}DsVP8S&-',
        'A0e(csn(i!o<fY^c_5aIu4v8kt4Da~iFLf|^n+1K*gP=Kq5JL4{(H|M8Xo4yxBL!QtAUH5-',
        'lV!>HIzCa=fm(07+eR{QKUHnaRjajPCzRp2#^s6v5>k5uDJuLBzPr-',
        '9vNXuTZ5&?F5s~F1qy|Bn)MnI1h2t<;QwY_@A#nvD}IIyyhN#IZ<f97Vxp*manRFUAQuLBCX?(%3AJjCv);4>iz6TA2z;0}xt*t1ZKcwzbJJZ9al<vY',
        'BgGEV!W1NE&*ZCS4U!5Z5hOKmf)a~hGR@M<L9PIPF%uR71uiCZVAnpw``>pepZ(Z5)RL5$Q~JrzJ(kj`SF!Eu`@A+DxYI_ie^*N}*W&PyP*I<#lQb=j',
        'W&@+3trXB+DrS7n_&oLER{Fb3OzHQq0&CU}GjCcqNQr0q+mY%ZuC^7_MwBiiMz<Jm3bv*3qY(V;s&>AXB;e|xEIJ0?2ul`D=FunaCP^(v9C|WOJn;a8',
        'Gbx?$nLi7>-',
        'R6Ni?XVACC(qq*Ikl0EAi|=9&ST*lmSy5WYU%6kB?x@9QfRRl<9O#82h)rrG@2mvD76LnVaPpCtYE?PZl3C&!DX>WIaG{Wo9(?s7Fq)#P>659_aX0NO',
        'xCq@L~zW;F_u=V98iSg_UT~N=3!1g;{pZ-',
        '2AKTmU$Wtnd4Dz@yA?nkc8etADCH1QOj~deC!PH<DkC*Y9o=}51*7m$7?UYTd(H19=fi$W=R!+W@_bFc5a1;ZzT6D?SHF$@I~<#>qLBy_R!CZNWo+7-',
        '92&GS8TmE}KN7y>YMj{V;~9^YtJiVJA%~&EK2q(GjIQ`EVetwB=u4s4k02zrNn6h}{9-',
        'rt$|&_6Yms>Dk3N0M+doICX9~r98^%*;EtJb`Se5XGz2_ie>Fg*GrwMz_>!&|w`P=avKWQ)GjWnq>1*tZnQAfuqA`Y<@k!%A3(THa-',
        'g@E>vi0^lgvuMU7R<GQ^1@C_^WA!@z<b7$pc>8}DhgT{GiU|VR+NN^oN#|lzo}NkV%-',
        'j25R4$|%H)#aIRUdo@UTpy9608$``LnN)rkXIwF=Nq@9RKFCNNkGd!|><?e$FG_krLzrR&CfpZf*xTrzkaGnt{%|qK6O(HMz)v5_~kVK*b6sFf8f}nO',
        'RWOMz(X_vNP~}k7hF>mWcBC-z3*IoyLo|zc$-',
        'ho)?HU{cLNj$8SX3bp3T)e(66lbMaz&JCCNPy^X{7oy@H1B_7{2PT~8v^3U%*llsVN7VdKjE0_Nqt$pIO%9b_1<H37!<O>DL<uU{P9fY|8#?#<yMEl$',
        'u2+i(34)2}Lv=FA`a!fIXqL&h?fY@ZI!dZhe*_g7F<|!v3|MrWUv8qBECnS=mc*tL2+h?)$tB1U-',
        'D12D}UbeQ%96#aS<?ET3^H{v_ApY$K|G+!W{~)KIe-',
        ';}zOkk|fqS<ARnA^qL!Eq){na;YA)#$K4TZnXq{f>GkJ2tIg!>Wg<O$?#5LR_|txpV8liULVn<4A?rC~M9Be@(w`t%f*9`)S{!>%bGK)Ga%{G)HmY6|',
        'c>Tufi9vIGrE<?Uxu{w}F5C?q}&N=IB0P9xj>9y5W^9+5c!x`^&FVsl{xpCOox#J1@L2O47)72TkY!ndVmNm`Qi{6c#R8$c;bz2Gt!~(4V}MNDFB^ik',
        'cXOi3wCPk&P`=LDjaS*FQsPVignHH{fi9HVUOZ(m3T!-',
        '+F`<k3U1R+>ck?f*16%@mr^<@mpWntp8^NsQlTo&+pc<;@s01efS~r#h43@IEAZk`yr<;nM-Iq#_BaLc*oh?a{Kk1a={1q{!dpkFg!vi30u~`fI_i;#',
        'iJNq#JZSLX9t1AOrAN7j`m($b%Kd<53aX8Q$_p)$pgN?cmg|`uz47ndL-',
        'u8p91A)i<ANq$9R5`yFYv^F0JlXmhopVSZcppuv@9F9zZo?Y(2uo5Ox;$+Gqa>KlHH9;dzG6No95nZe;zcRczljz~JUBRBFSBoj~h=s5XN3b3j6SIZw',
        'G*ps&45k{ZUU7Ed*^hd+u!aG+tY!#(C75-{i3B0VQ|z@by{ddlcR510ULa-fPVIq7^{s!(Z@c^7?8b~k{3mIoes;Xl#6U@FU>d=?rhbWf&IucF&>y!6',
        '<8Tz%V}tbcwJU;fNrqk<0lX3b%IY>-',
        'V)+{ei9Mm9bF>s{*>B4ZTFbJ=Uj+vsR7GiO>qGbR_g@7^Dgh9P?$^?uaR=i`0uIQ~bUZ~($4?eSd0vQla8+rJ(6tw)%9;4-',
        '$o_#2GrBwy}k`kbX)cHbu%c<df7yYwPnPXNkc%Z_2RHo~&~=i!}u7<Cfv*;r+G$5x70f04^Cem~RqIgAV5_ii42ekIEvyqVQcwox4$L{t;s&l5MBEvY',
        'J|y8Q{JPdW>%(AiyN$9TkCrFdz>2zwuX2rI|8;GW#VXA;ZDPM^zT<BsJkh2}&AgCVn2js8yXb8RHeCP5f5v~E4i*N$=8@ke8f2Zc%EDqCJ3k9tXUJ7H',
        '~vCGGRrcQQn=;`CYF{6=;2&lmq5?Kg=gCiwN8w{z`RKZiC#gv*{L!r)R(d&fc+ANWSvJEze*se?dkY}_C;KJ#Yvp;FEK-ZBsV%Y~eJ`7e3kXD{MSZR1',
        '~R0WP1%G#qRjrTv9x`OF7T;o^6mfk>TPA)q$8m0ERzM;>^Rd#`(mQn3@4PSEfJamtXyjaMAVKj(mQ*;V%;l`-',
        '}^;xOiPS%RWZTi&Ou%aGOuV_?614`y&+3&j&ZOn%uJ%x>%Fp^K;C2W`w)a11&%?6dT6+Iza`D3!?P6ifD*gKrdz7tbQ+D-',
        's8u=kUUSrw1nZ*>6@eEIE?EqtiF^b++-=V3hkGe}vC}`EnF7%4?(8(L+>?Y1T(sFn2C-',
        'LoxHDQ<!$(eyn`*eqOlwTC9a;W&3OMq*5b_2}!7I8>3@ZAElzEv!jSjV!}WnVmarci@EB{pTmiv;ul#z9OI$so3t;-',
        'yzNrb@y%dU+DjqDd`Nd+iCh?Bj8MquFv?=%lrRWUI1ZX#=9s@an9vwJPhkX9U>M#w#Bp!?Fu8miQQ~pHVQ=NxNA5zKh+?6gw&E=2UHmSdYvk#8>meL+',
        '+8bH^+b1!jD`+cBmg>-edey7&wzW^O;iboj>NW2D)k;RURj5@PEMLByx4-2qwrt*vgk2=c5OkLCb%<K?02YsJ121sr4WH-t_uodfK1?oGLX1KyhsDuW',
        'EE0HN$%gI5m@MoQL!~Z^)*Yh_OT`KI|LPfT_~}ic3dBiPte?F9c5n$c(HwNp5p?YPCiLtX?E9Aa{LgED#T{4Q%=1s*!*{>=Z5GX%jp^x^S386Oq<6|Z',
        'K5)smNvd@YJ$x36=JoTHulzkXUiWXDaLl2s-',
        'n@esmOsNjS3bbn8^1#J;hzu|r%)<SB5I6LuZ)w%5tF9O;qB*K!lETJ2#n9+2QQ`&dN`*r&XUh7tWzW+q$oV2@jWoUrYjc_7CQ;&pT_*-',
        'PU6KMejF?qFQBh?0j1u#^nU!)jE-z)`87Y~nw$TQv-',
        '=A;F^HrT3I$5#BK2w=C%n3?ocKAcm*SN?D$NEP26oV>H>g&(aoZg~M`&lk4<2XI!s)F2=am>QByJ2aTptDJT2D~I@U|Bj+VKK=d2^^mG0(0Y#QB=%I@',
        ')-kvq<C&Dl&LZ(4JyR)39i`!ot!7L(i?s&gH0gv$0vjN)vGwWeV(f$)#)=QoOLa$@u2Ygq<Nfp4>ol**wC6!P)HLovQQk{2cw)G-',
        'T^}>eW$WrvGFs^3e5s@uMea(XSMk9Qcm@ORlB+t#8I{OL^g}9`%x^B$w|b$aQhryZ(m3b(>f)Zx%-$ynr}u^6-',
        'QA^S!IT&dt~U1HX7?gpEUWwv`Kfv&SQzTBKiP-',
        '<L2Fxop@zmNK=zo*#Vs+x+I<Uy;lAAhYKKRU}UF!VZ)Px%=~%(sTR=uqP}e**M64doO0c89i(otf8e&SIMV1HQ#Dm+@HF|_R0Xb>AWe~o$6mI#Zo)Au',
        '??46Y;%OJ#Y=hq*p6Ly()WreXP7$UKqgIDL`QiVlRCRO^sxOX<UBfaIqtvz9)<@;xcohD;X_yaJIzFxx5aVHOhsSfhzzXEYo3aPH<dlY;ceV}<4-',
        '7cl+b}f#s-OxIf&Vp-ol0}KZ>{pVn-NW^El?Hlc6%mw4j6PNF7}Z2y!87H;l2YyE7YV8ShWsqkPpBX$f*6XMXs*bb295YxbTun*$G+#*E2rl-hhGbrg',
        'yPa)koEZ}{>x53-',
        '>&g#nxAnZ5G#w?XVI6&#1DkUN(xqcO6Hp`j7H_Gy&6LMGO4X4V&OB%XZ$o%MCB`0fu#p7=2{KYlgUy$@#M?=R!9efMGUjOiSA#3I_-',
        'N{CkUOf7T#;Y+EH?qJr<DQiyuuZOUHrIGWEkvAOu4n$9)ROqETUT5yCsT_6WTna&e=VfcOp6?MyF%La-Kh=pE58iYW%~e||Z{5y5_iv|o?+E1wtMvTn',
        'DV})iTiCYlDMp7U_}q7{;|u@vJ$`fVT`W5IP_}*jeBxWaLTRr#oOt~=plcqRzW!dKFI~u9Cmhd$$=w9Tv2Noa&1QoyeC?|owci4Ai;raPH=ci4;O&;F',
        '+=97B)7yU#Gxqig{XB*49%jv*O0^Qx)0M*sc%H&0;II_hih!_TU?pnPbA(|I-',
        'vbXJbp~(Klic^{FDdsf<e+75=h>$=@#epn%;?x4`yF{aW3}xJ{^Dw8zw0BcT0hPK*Wb;StFK__)+-r(q>ELP3M8>(U~np%Hh1vYJ-',
        '0$sp>+6py!4SpFFOKXF#we|f>_@8#=qq0Z6l1;Eh&~_v5g%A<II`fPPG=HB*D{=3j%7@3AT-lgHk;D;B7qeyMND~xMt^<?X<$gD==&ENo*gAsM#t%y6',
        'suQ+DkZbY~8R4R~;gL_5qfhcnYhB#_2rgBW!zN1rtW`yE|_{DaFG^gZ9x~bFl-',
        '%YV8%L^IGu0|D53zrtpbRU(a)Ehj{FXI~aKCPX6YL*H8)#b7yw3?8v?GeT(m9Q@GE6_VZkO-',
        'L;IXGNpz4(l%{6VZKPD6`OCk3R1`XH+>x2tT6iY{q*hiHneX@0-',
        'wJ=cPZ~X^H{94JoVg*oN(MRq<HuTo=f``S2B2*Q2^cNd`!gn7%#wCp?JU<Z2X(0ub(fS_#*^W$hMjDX*3KI(gtj&QH$_xo^@-sGcx)xodus-',
        'b(AyDI+}-m|6A(g+nM}@8`yN&32O9@m0R(`4x}&(FIQu9=ql=sY2>FbpslZ;bsHO4o6u-',
        'P?6YtI=bU*WKl;%v_=At{0uNyL#;^YoSi{$S;k8wy|1)Q{X@eWe{dfnKX*=x*dfb)#^72p6O@%o#_F~zLWAO?OD-',
        '{;bU&0vO%zW1mS%29H|EEVtf^AmN(RMaI{#y=Ob_x3)aVXPzeBOM@!R$Y`mo!Pqg^pq|&+nHHA=;3PjqqyPD+r(<Nrkvula||PXh@9*r(MLBUthzM-',
        '}?kNUlV5ErDey_z}|oNYo7nR#s9BxQl``=D{uJ(fA!_xFurOv?LiI?gO@~X9T=s*uY~WnF2PGd8Pv;V#;+BC{U5rPkzZUzeDX91O4+u&j-',
        'Z+1q6u`6M<ij+;b-7?&tzgK`Om-uAgydvfZTfJhj_zb=g>2`k8+n!sgNfKH6q{#Aq)38hz)C2;P*_X_n=eRdix9i{Qw-',
        'i>YW)F?Oj4t&z5hM&Yr(5lt2ae0#gruC-;Bl#6LNS&v@e}7`pd6G{-i9UW`tflyi=P=g`VhZ&X?R{NwZ-',
        'aw-S@kMHw~Q@Yiw>4C56KYKa0@0TAJ8%KosfU!oMG)+hv4F=Y}M9C=1dmqJ?&mZ*P=6d$n9@}GkY>(}+J@#_#e*u_56l#ZDzO4WN002ovPDHLkV1f',
    ),
    "CHAMA": (
        'iBL{Q4GJ0x0000DNk~Le0000`0000`2nGNE0FDvztpETWqe(<TRCwC$oOiTjRh9og`<xppysDS__3PXXO$VT9XmXAYh=@o~Nk4%h=nzF212_VTX%<Rw',
        'L}x@qhbRaFA_7W_<eWMXI??HM_v?PS(!KYb{rjU@e#4rdGfH&E{;pMP)vBs{?mgeT_degf_qhd|unC*637fD9o3II+unC*637fD9o3II+unC*637hag',
        '6U&zM>hk4l^`KqP(GySpu|E3r3LPIDrmwFU)I08&r!8h5{cE~j`D?k5E%N(nYc8gfkj=_@MyhoT224nnIik2grclou#zxcw&q$gwckRvcH%;J_^1+((',
        '8L?~NopL~HE4fr@2&gFDff`F-0-',
        'P#|3MrNW$r$trHLpA}bdUT^5;&pw0nJ%Mw+|Uz8Ni`@EQrXgK~(VK!Fv>lq>gx{76?O{V|5g>pgzp71UMV>SoOE^H%DO7NYxnOm0vx~^sgU_8^{RL5w',
        'da}+65CCOk98<hZ+x=MX6!x0`mu1a_)tUKJi>~<syL*Okhw|j4|>zLE!F_PSPl}Y?<`&z5ct=_B?h%0HX(?43vN{55|CcKp{=wb&FK1ROgoYWoah2jN',
        '5|92B<_hJegDOT=<jsWNyLx>cZs~A`#l-kmrU+!-',
        'j;mULn!ROo<1`ALC(^$D05@HbYdQ)xi>nO`)zawMHwOSI056z66ciSY9eqmxNPi{Dc1Jl^@9eY70Di*4dgjhEWobrGhm|R<AQz*K_*%d&#CL@uASjDf',
        '!b{AQiMQ$lAY8>FTRv78Xbw1$rnkv11(@)`VQv{ZV|7BQb^n;M)0D$^RM)JZ#IeGz6?Dp%Jc|ccq**`!k9trJQ1o5Jmw~FCbw?m{^Q+MExFo348(r5#',
        '8TxrT>R(C}tVq@(L4zVY0gN5-sfF=d)b4W^IroBjDt1&e0#gbj7<yqIoX~jEo^No}7i)2%p~eEDgm2DdHQ5)-k3|S2lopkBJP3AR>Sws))~nX0-',
        'joXzb;aNcL+%3VDLIn0>cz@R81ij9b2tmcS8<C2#)+xNu{~oO%?ja^>=!d9XN>UoX1)O=BOu?dP=QJ!5q_=x8dT#akf|LoRdd+_#AC$~qcaXG*$`@mr',
        '_RnZxf;V<gLHJ$DkC)KT#e0un%_hV;bfT@8|_hKZd4mofZ!iPb?1H*R?dLn<WB(NH1vLIXnz-1g$-',
        '@>k=+LjwkrIT8Xoi=M!_H+}!{Z9k`Z5!!H^F#AOwS}=vz?Pk<Xgi%i%dUoh}fp#4vnOvhB<se@GW051ap}bihh8KYaU%C=UKasf((q%|zhW}7X{E4yf',
        '$ssfzrZ}z2xMdAyu6~lI#_mAuGeQ%RStV2<c?TWu9U-u5QT0FE%||(W{MP#2(R=Bm-',
        'P;jhh{(vPWxv7;O#b{3lNLWuHg|yUKD`r04YA3HM2W1BJEe%u8G}^&p(aRf0P1T{lOY{@VC_~YEnxP-',
        '*U!XM79s_~OFw$!1Z2z@IA|di%`@6JXz_Kd2u2KnuQ8=qVP0(vC(b!n>mF`;;W7cJe6UTkB&GF%ioCCj$g?|7Q&!)D$%Q-',
        '}%pvefC_;c^buyN@r+GRy%kk)IlPE-BEEL3%M(v;(KFZK!2-',
        '7|UvmNAXNRUBsH&hP8`4~iTu7K!v(7gs372t<A$7D~zKn_}!*f;_e+AV~EWm0#I{kGkJ>+hrGsT}ucH)QaMZO_w84KJ>{8Iz?z<^5TOKe6TMdb*v<jM',
        'mj;QO1P>#}W%z6A%hSs`Q!(Bv}XPGR0W~K10M~@Kj7lBdHQ60ohQEuqB1aB7p%@CJnDc@fgi$20@E-',
        'd=B5=O*(KB;pA({mQE+YB2hrGXdo_74!{W5;e^88HSAWi+5ec|@xaIjX%J$KAQ&$5A0@RRaOwL);P;l^OzTHIwll*#AJdX=11ngkSR6UcfCg2QBF-',
        'S{u-',
        '0G|JceasCg2urp!3^(ly*zuQ=rBp(KwtbV{L}2M<qrGK`iPGw4O#>J_pzMHrBKu1Y}Dayt*!6WY#!ZJvdVO`vdxZlj0wEk`4K>_=+N$VKG=$LQxWL-',
        'X9rr%r56^$)=ccjOoe~Pt7qpRpKBZ7YcD;h>Q@SSoH)rLL&sC7(A+;)g5iDm_D7<#pr7x3>sM6kH7mRj15uWhx!6mLX5E(5d=j56~Xw0m~uNqm-Nyoc',
        '2VDcHzb$Gst4x?BFp{1?dI`^C-',
        'X@EG@N%>Q34S{BSZw8TKPTeXN=KvwmwncQwt1HtWj(bAezDWj5C(sfO!@u34YQrwZWLV?8lmx7$+fK1PK&XP*q$e^b|@=Y@5pRMGKhntr$1jQ<wyeC+',
        '9)iL9|VuMsUnEh@XNA8_8?F{QYxjyi_N9p~!11Aeq%gGUUiq@gjIUE*G)78dFhE!5SJOL;yyJO~9(gICjq#@|EG+*=Oeu>k&`>O5PI!vmii|1a(#LDH',
        'IH{moW5@!RZL)!xJKLY<0;iv`n1B;$j=A$uMF7!C2@ST*KJz3YWgJ7!3_OEQYpa%Ip;>#d1HkBVy@2eM~dkBViFF0;!>ypgF_Zudk-',
        '><pK{@p%B!_KXoT9V`f0xWE>W2Evg11P0NqOBVs`uVj!pRa%nojy8CH6+;RBGqwwT=Af!*&`^#F4207~Yx3Y8B2>DYpGytrifp5B6&H)xABfGK0l4r;',
        'B{G6$zxez6wXTwV7&VQVXPng7vE=$2S2*U=19>$a)4#9<}6WmCO^9CVAF(4LeM$qzjWU#ME?zCz2_m1$plkO!6VB)kL*-',
        '#jdGmc6o)O^4Qc~Z5AHHZ<4(jXw@^ue3qyejFViv3*+|JwcmPJjA(dDkrPg4gFVv407bY=k(A!8(u(1JrFo_>rwJo9&I>a2?hO!I3aE9iiU4j)AR5v2',
        'f))k`+t%`L%nJe_;W>W)M8igG7dOO)t@I+n}`}@E#il7zI&46~%+kk@dWe8o^7Q$ac{_qmxhc&4pZ<8|+LPagnYa4<-',
        'pL>J+pNCLpJt$&C?a*PkG+wWHGq$#!jlN{G9^!OTUA-rYr{;X-^cNcmtvwoD)}5E?uQ@ku*i^6Sy{k72frX-qV*mx1;gx&9UWVZrm<^6Wwm-',
        '62mr+zY9}IuBkUu&63_+$j9e$i_e?=*IA_I8+^~8K`3O1xzkSC;=>7f_dRd+@jy$yl0<p?Mp(9a$F${Jdw>Pn~YXpXY<BV=DhqU9c~R~#}(*DEFefng',
        'f)f<r0;GFO!GqEQi5$9jA=(Z62uw6A=-',
        '<Y8jQLDau;By#rPNRfWIr#F<htTwGmF<rpU~{>%=Y{Mgj{0f=6R81w%4xGQrw4kcO~v!9hVxvuA=A)L29epr}|hHb_eWp7<%e^b<xOeG&T%r@VIalay',
        'MwC1~#?Y<R31cJ+_pMm3;Q$n7zR>`)>o3e;147fhP*8vW07Yx~-@@~#j#j77yklH#WqFxy2))B-',
        '^sjX#Z)DnL7wK9Au+bgP$1pY7qFpXukS7xssFD{+qwVh~gmrCEJ3(>l@00O7Rh_%-VhQB(w+A{JcSKx-*hN+>id)<!TWK50OIN-',
        '}CIqC<Xwz55`he&H9`;9Oq3sfRJ6Iti>0s3L6*f>SIqCqlaev^*7-',
        'y$Jms_#{QP3W=Y27hSj~%Cl~@pglsC8k7j{J$|?b@k|I$!dL?`2Ctt$3b(O_omre_)NX$U_sANgk>RrxO*3#AUNc;^h8iJz-',
        '~l8{L7Tb{YXE~(K}^(qk8j39=kb|C6UA3Eg4Y*PyL=Z|nZVL(Xq_^Sq1tk!UMH4}qICpQ0?gKJxUK>^?l7|Q(J*>6a#V=DPSKeOQLXXr5%^-qY*tU-',
        '4W2Og$9iDy0ND$Jc+Ft=^WZK=y`UQ6k`^$dxbO1&88C*pTtsUDUIDMDYqmXzBTSZ|8IXFsDi}pP%>_ij*aFtaO;Wvr101OH;1oRI43W*@GY@mGXY}5a',
        '7`ICo*FSg%`2eg-(PDtz<4Ek}??HGbh9RVL4pc3EeS$%7-v8wUZrHQ!4K@DM{#&aaJn{dl&cE@{*X8PIhw`<K3s`dBZt%@K_PZ5i{s1EVNO~7K_-',
        'W83n6QRldlQfMWIXWH;WS>XLTEv>8QYA<TZic`B0)gV)xtsNujJEbyh{IdujA_;-',
        '*AvP!~q`Ed(<oH9qK&dK~$PILIe@h{9HgExrtobM`UC2`5dOTgtT^{tCvEs6V`5lgr`EhJG6`<SZEmfVZuUb|H}y+aq%1PcY0vH$UQ6mq!zmR?k`AfY',
        'QWRQv3LogQNnz!0VHU$2F(qkjZ1JVK87y*F_pxSHP#cT0tp!1C_zAtpn-',
        'r5!5Zc{&m$IGHDKV$3ObVE5}J9iZ<5#~>yN5d5d&fbF%~4i<nz=AEWfyD5w0ai!zya?G{TU<#dD~CaWO2p0cqqgs<`LA2<_XW^A%U?;+CC``^#71$&a',
        'o5i$u0HMP`olkPHb~MJer`;a3j8$N*+kjpURKm_01DdKc>xN3CZyIqwm#WRhZR4ouTxB#Ke*5a+2T4ll|sFAZW}7-',
        'aw3l>Iv_M}27ql6q7fV*XhA2aIWEIAZW(338U9=a%t>ANOJt&w+Dl^sBPQmZ;b3^l2AejqTZD<aKo58;E-',
        'qa~=4F*YM&a?abZvWWN5u#cxkYfAO%3G#c#TtH1x(KRHmv=DB^FLum{yWA@sGqz^oW{JM%U2CZy>@iTd?eRtN$Dh9Y0N$bs^MT(y?4qNoNCBp<xo9UH',
        'q{2EVy5Iav%;Z?8nto5uscRru}##nsNh6xnSeABJfH)E=?Xg=i&=geb+6H*KzP|KiKl|B>GuO1|3y=`O4XRjsFI$BAQbrJQ!knL;hgt-',
        '^LeI59<l~*AGU;QtBbHxp(%X!CLr4P1_<++w3GlDLru2@OF(obU|EZc5-',
        'oGmiqN8y1er)bz*MdM{d$abU2>@b=sZ&V7zU<||xvw%qkVuXq+y%=u!+B&wJvYxhyArlUq2$@G|${g*;IPR3!D4S-S5-',
        'W@V13|=Uf!;!n!OWv!fW#5Ml(Q&jLl|kWq^r!jFoZiUdi&LwZ2M{IKATd#Apq9>*P=SBQx6glVZp@ltQs?(Kp_YO6AD2nB#nfTPzb|}#O6>Mpo;Gq0&',
        'fuYO(N7l(lmH$4d+FM8HY_KOxCmR-Vq)ihF5CJBQJZ#uFN=X#t@m$V?)cskM!|_XZjf<hHbp(?0wo;`04=P?}2*c7_x>9rO{Nf0UQP|ur3J5w1ql`%W',
        'wG1pB=vbTLP^#NXFF&>+ZiDOcAUP5$o{Yk%&hu*o_NBYJ|iDG)yy(#TeL_wV)Q20L_x-',
        '_6;X^G1MG*Yv?daZkIgq8CNjj<EL=Uh8*92u*Qfe3r3WW{Yx)3b*L&ifewMqv79tECi&HUWL-Ov8EDuHZw)TY<H9;lHmaUfaSDn2zdq<^KmJ8MwdEnU',
        'yylU&9s{*eBh1$@XF~mzvc5WE_|@KrbN-!g-g|P+C$7-r9=?DHmu$swsg+xA+>26}BBErzS(QO86_kM#)H`T2An;%<exQL7j~WBcLFVvj^AwSXme>-',
        'Gn@pB{7<<!7%)r(B{p>HZbbZJzs?^n!Zk*6I77lF<*!}|+cgZ!l+>Yc8I1e@Na7NHLhvs9vdYt#v1LdeS_t7$MDOYWr)ArGPGC%OviwQs5?|5}S!Q=v',
        '%9uRz}#>@#reCD<5_~9WZzeyK{tCrDOF|@=(jEt0M7>gL!bV;jt?{TRoaT#^5B&i}kL%eIIZwSViX4T7DumQ#xia-HHtieQiECC`3+WI-ltFNRzmyol',
        '96^KwGfi5x3vKju0Z=h3-',
        '#sD^ef)R`ZD}ply9|$J01W`aE2<X@_$oT)zi9i0jyJVYd=gV6nFq>J@kFB|x27{1`z!~K9iG)8NOJh{Pv9I3DqdOn)28owGe3{(8$KNyWl6I2sIX?RP',
        'pHmoeh$fiKVKR?NQmV;Nvk+Ozlc<LvLXoBz&U|y#_JY_Lf&c|VQPy~<Kk^zTN<i~X9ViFjiUtp4A|$G0B80h!YOK)y4@e^e4?|TbS|M&grU6;dJh#{Y',
        '5kp6iqg`6b&sqP@^hDIBaBvIxA5H+@fFMD)Iv(HMMfoJ9a9%63qLptt=F@jyF7>Uav*X}gW_^AEdo5T<%LYe2Q95f0<JWKCpxzOVYYq6&AuDOwc@ioH',
        'k2G^x-+bXSG^?Q~!$5!LxU0XxQ&+r1?elv8ok(tgq0P5qa6nn*996G05UL78Nk(6Pgx+%srV!xwH&kQ8>?sk$E9)d-',
        'E56ZahL)^Zkv?$k3yd`{QuyIShIiZJ?e|19Gq_R!V+W9Y2pvaJOXg54DSBKx{twR+*TVmF+}y%;>?SvpWXhNo^EqT_1w;M41g1tY4?$<1Gl~(%4QKr3',
        'uBCi%_esdAUcAdtZKia|f?lGT-I$>&$@eF+)0b9rO#>ct$_1A#V$@Y3)+-MumM2ws)fj5xQE7JA?noT-GvTPCZlcRv&r7KxKP6z-',
        'y+W?JrOJVaAI?bC5lF_Ekr579{O?TF75Fg~bfu76wVowgZmF9uT=>>|BAzzPGK>3_CpatzYA6&A!|Nf4u1B7nLh8%^>9_$2NSzQ2Im}O%BF59P-',
        'ayr23nkol>&!8EUY?xejNkR~n`h?p-E+p_7gw<e>LIWe1}e}NBSQ@y{ilg!IClG|)f|;Mf=08b;4p|7tQWxGa2vBbWx0oEjiHl}eGAG3*X+O@-',
        '<nVBo_lf2&zk#U?my(Sy3a#bVtzIbd><Sz3A<tqX)R*n=nZ`4=zr78Z#wO*#lYN>)pA$)ES6qB7A^09M%|$E(fapEe|a!jWg^$?eZhY^Zr9!?7;dx@S',
        '3_)3Fl~YkdD41{k4G?L1=E%%Nrj{H!m16*HeX%^qgtpBr>M_x&f^Cv&3rbDk*GjvOo=K=e+FxuXQlV7Q_lt*>rKW6<5(}yE6O^c7wE_Fiue4}Z+61Gu',
        '!>urGu(R5@82L~=e2iYzSM?}t&r_|7E=B+jf&z=GWcSRE&CR~{if1gANaT)&~rc0wKLFZ;~@<3UtLK2?HAs3?75%0R6l>;#dLPYgq=atf-',
        'W|YPtdMbe8C~%5L}ibvpT7MX9LB}3cQ{s9CAm>dJDBo`0buC(`V$!<pgz>)OboWI`H<7T|6LjO%n`bAm7{utO8lmltA?g1PXNvtpXb|%I7a(Sp6H<e9',
        '2et(DNTS3%zqID9^yl(TMNIxYuzHeF1kv$Zcy+<k(+-N8Xl@KJ>Rgm%eFb4Zr;i8a|29fTuRU0C?d|zuRMGNbn<%-',
        '6F<Yk14hS8FU(4`|<dpXE22nbNtI>5B5?#Gs1qd#;9UQhqbil4V9YX_l*{ozue#>d$v&>bR;AFB=h@d-Mj_oGrVNrJs1yCYqmC<ZNO%u-',
        '76xB^fg$rIL~I=6q$0#z?;YeXrv8Bs)k~`6Sy5PVTzYB-tLA}^VDAP9Q){Z<ZWBvpWPcNL~4%dLS_#kqe8qYX1@|Xwba}=;wiV|lYb?2tC;(hKk$L?F',
        '5tLHCBA-',
        'i%$*OFxUIL1kvPxO3!fzyIGi)6MjY0i;spj8j^4zRY!u~zfyg#{A*znVH+Me72rc=DX$9q)C7$s!wq?;PPyESwuKmzNZ9Sro=!EML8<8A+1OxS*>Av$',
        '1e-',
        '=0I7=c;7p#CE{>>(9&a)3IAnG}M_Ba?5S(a4dyt%&p<MwL(JsgD<UWJ!*z7KLm*Z7NUojxbWG)3f0PygD}P+?)+V{j_O?Rar_g3^A%0uUH$9iBNWRUi',
        'TS!V@WeZuA>bXl__;~W1VO9g2(^c`Q32tm-',
        'XnqucEQVRHS<x?0YY{1@%9hmv@Z7q*zivMG3D?$tD#Dj7Pf$z&esf4`{@SXMVtedtSuddl%@Q(8kvuZsU~<UKt5lQ(r|rX^Pl#+(n^vEL-Uymy8)AR|',
        '+^{*%q|tx**6SCZO6kk83v{WY@=+HLER>CpURBD$5qUryJ+rvE5k%)jDk}L(+>Z*~DRjuM{wS+o5Tlpz|>@C#+cT7=<Wc%A69}#HsB3`g#^Wvx;>|hD',
        'YcsjU%!-BoInL#D!a1cIs9#O__Ig12Z8dA;R~?#CKV~c<&%BLClz`yV6-Mux<Nl!m*oacIdfGnL3TInn6~_)*769_VMypP2lZ!-',
        'p|oz9zo%?l&s>Ql7d@@6m$4=2@=erd&Xp<zz~ikn0i0Qeq(EnTiKxW$>n$rXm4qyT5W&|J9P@9Bah?)g1!OlQP<)dhR9DQtv^iR>5I6&r-',
        'o?2#M)Yp%`2yTtPIoJk$ukQ>f63Yv27H!hEVt6yJmrJsVnz~?e|lCqC>B}>6>q)JfAvrU%7F|V=%b}@dpb~F=)f%t089f;V^PC6XY4Rt_&@$lV94y`h',
        'R}}p6SDjCp0N*hc-',
        '}d4X`d_kCuqaKuW!*4jLo#t|qEHL_Yfk`Fk&8(aHhTgp|Bv$Du(^+O9_0v!2w{v9^VoqZcxzyp+w_)>3Wh=GRw#^<8;P_AfH);q&&>(xr0+VBor`y7K',
        'W!jG5Fz5_GesYb<NKHfP`C&%y>ZWP->3WCFe;#l$7t$OxvbMEz;yQ-`ghR%>v=0TC~+R-',
        'W$<Arx*}UZ=g#LVH|f&(?O%*g9oK*h^$Q)ue{WDVn4NZ6&5%*Pz!qCbSgza+LAO6Gju1hPiESo$stJa_cSI(pR5F-',
        '^f_@J@7pF(G_3S`zC&r8(!X#VA%6;{WSKv?Cn2<^OgsA>B#eR)zVcg`{-',
        '!|70cNA%LMrvTB)(eZ+=9swwB<eB09|@Ho<SGll3VSJo{W6(IqLvVwu<;FutMeHwMakZpH53f1Yt|qnKJQvrCKc0W-*M+XPruoOK*^UzNxDh8gjKU-l',
        't(*!3P}nNC8fk+ulacNxQ(=a<Qc6*dfP#^Ut{QCp{UUUv;YJoQ5U@xHs6w(Nd>y2ZCR@%zWh`xXPY`NgHplRtYS0QcN{yZYfO>k9$D3QytaYyO$^ni^',
        ')jVkS2r%1BegORvD9N{!$CpNLC;S711GjKmQ$w(Vrx7J`z}Gdx6hzMVhxr7X^bQJc5$`nn4BC}c5?*;6}t<ki*mELz4h^R{5hgjXoH<rrmRPTZ$Vo?(',
        'n>!v+bR#Rd~zd5P<`_!vJr@(B6SA183{vG2VL|0z5@{|CCmw7aSG<;Zu>=GS+0krZdL+lLRPOda1T3}?zBD}1sy&x@b3xYvgH$ERDUm5SsfrM)4Xy-',
        '&!iiQ~XK1}PNElsdZbVTh(suk=zG9OmG0n^VY_xZrbL%s%xF&fGJ{x37&c5+Iop1O>#0kjvBaVmqs!_&av~>V@x`w0Xw{{_(B1Yit@s`GlmnHOKG0g8',
        '+Qvd%xC^H7iNNfVP1}eCJ;-WBFN%8BxT>9CV#<^hDThLY@ij%H*G~g*b-',
        '9ZEToZByN_k#uq!761S4KWxlXSKbwEBhm+5*^KU<!&A5ppNLIxNRQvL*S+@oAsvqXaPk!oM)rIfF)0!oH?zEWVNJ=5_<l9>4ymIZv?FCBrgw43%ikmq',
        '5$X(>>Up}Wn*usg2Op{#Hu3L7DW}J;VXXnxEz2kE3TinA<4>vgZOLq~p^s&L0sn;XcHZ1FGJKsEc&intk>y1CVUP<eu)e(Z)5Rq@-',
        'd_dnI)G9FSa)>BpO&JqZ86DM-48klUtU7GkAg3v*wIsP3S-Of3{c;(`81lIyDIs-',
        '=46pjrY1f74{Zuc$^aQ|g^%j#kWLC<U?FT7eSY^wZv$){M^N4~WtPY|+BQ_0+B|})q69k5^wUt6KA_z)k#3Ye0<jV~C0GG31Blh282l=b8z%QQhQ*8^',
        'Iy~0{Ux%l5s{HytAkpIyx9FILp8$Gv5IN?b32yW%AfAP5sV-',
        'HlK2qi~glr(kJSN>7}g0V-bYJ!&x!8NzAngC3IUw-@l>YKO;o3II+unC*+w~7A?r8ofZzW4zA00000NkvXXu0mjf',
    ),
    "COSMICA": (
        'iBL{Q4GJ0x0000DNk~Le0000`0000`2nGNE0FDvztpETY$4Nv%RCwC$n|HjWReA5f&suNW?esFez|1fM2n;O{kVK@Y5u&1q<!WMy1@4V0ALS}0qF7?o',
        'YY$4)iy9SUA)taF8Ug7dGL#vH>HVBJZJ*uVvet9|*vF_zL~|JkG4uO;-p}Xk@~(Z>?|u67EI5dRIEaHdh=VwYgE)wTIEaHdh=cg=1^I2;kT$-',
        'hN&*rB5$N0&Z2%?!DT5dw!e{#lD#yxyD*`ut_;g+L^h0pHYq0a4j^cp?(E=Nnz%E4{D2l2_@IVISAT@*#w1WcPXUO<hY3&H<KjjVbTScI|>s@M2csWV',
        '|x(^WnXHjc`HcAe}2o1DQNIOV<KiPd-',
        '8QYdZs*rl{ii$_2fWo4ZlY2#S*tc;fCw=k^BsmOx0XhirD4N!>Wkuw;U&~MMlp$>TDn%Rwy$~%z%`AB_4t@%xh5Efnx{GZexf9dr;l9nQXcq(IB}?W)',
        'rt^r24onq?vZ)bJPc6A9g@OXA3WdQ?5aO{e<m4p{_WbY79DZz_s_#$<geVHBowf+wdFOu(33ToTE%F-5e5~IAI)-',
        '(VxEt?h`#mLEzK=#bX4`DRo|%vbCzLJq5);0HD`KRqs9F?{N{Uy=#A6J2uOJ>o5miJ5C@`wsw_QM>2_i}mK#XO`CL9))dBZ99a_IXnd1^{v(YQgiyb2',
        '?;xZC~#85!lSk9QbcUSjhO$9*@)WNXgm=7%yAPb+nFf&$eXXEMBZq`nQb&=wdgT`7|S)T2f)SWFn9>M?X}BHF#2&Pk3faMD0T5Myu{vQTM+J#5;x<f$',
        'ovnfs~I*@Iyh=>uEnJTQ-se$(=Ba}k?&ZzDI3AT-Q2r`f#ys~95);3@Fx0QWOGK)Rox0-_)WV-',
        'qAOV}d?L4|^p(>kvi;P4lip@i~GZbF_*Wj4^}~P!1w`OvwDO#u5!Vq-PJWx%QRvpH5)bxlJ`X6yt7Y{d>MoUhCuTTP%&9QND2pOqU(4jv=XZm~CvMDC',
        '#uE_tKcT@fTJxfbE7LDs(NI1BzeyyEZ-q6ISuAK~g=E;pNZ8s8X~#7;6wCSYt895=lT}BYJ}p14Il25d*fu+C>j>{*`|s2TX;v^KRXDbCY>zz311G-',
        '*!J#$;yPXnIF9TtGGi3`0S6K$>t8EE~UN0<0@?$*=~x~I<{`O4)v{nx&IXxk5S*>CdngAWJwCaiy&D};T*o>$VmyS(9@e?Y=a~Ws8nN?AC~aPFF6I5?',
        'f{flwwJwZA#Y7Fu<Ue7$qAUkqDJsyP;0;lg(?}ITnkcZfmRNz4fMhD89wTBznWmZO`EeR<ywpOo%eFrRXyDDV4FMY&thy#g91b5Qwkhu8*I-',
        'o_4S{n)w%-#PI><4>8bn<ZfuC%H&w`750MB)l%%^yC~~~>7!C1xPRl7Pj;&y<L!GBo1#2x=eDtS;gN|w?<O3i40C(K-',
        '1)$FOgP*5oaf_if{{uHOO%Mp;Evg2uN-myGk<s=M)ggP}Y@lnrM1A}L+}P(C|6Yy7ue|7&?l1h;)OXr!|H5we-',
        '8RTWlYLyhv!9t#i<Vak>5zHF`5dQ^POoSG&My=9EaMM9{&gPu{1z%btEjIxL@k5qfX^M;?hwa<xDH}0bP9Yvi}M{y6)=RjEF+YH-',
        'eiQZC=(|Ux$#I8AtgBG)DlOW0b6%8887bSgYW%I^2{;+_>0jrpd=7^r6h)`7<$A|(;i-Y)?Utf$IA|k3j5AUn9?9--',
        'YXbharw_xb?@6WsrB>yOYUaJzGeLQzQfojN?l{7Lr1O-hoiuwB6Nso%{)M3_ca`P?DH92{bKI8&J)&FQ=e3#Qh-',
        'kdu}z9*lh_u_Ho&5!`8Wf$m@J!MLVwK6)GiPql7*};ttE1UB-TONp<0Si=P{{a+s$oyIsp^nIpcy;xuS9s@z6M9>#t_v+Lz&`J(vQ#pkh!1BA)y2aR)',
        '{M{rEFfhOR|50W3QCHZ<M_w{KwA_9OY$R}N!+XP6n&&s1utyPQm*gTYBbVLb()VwsxQ&i)OT651m<|2;SG@Sc#VrX`;+n37_RQ1gP_RiG0Y+4c$I1iY',
        'W2-Fg^bG$`^Wp^dr{U<yhyz~XQ@^QuenX+RQN#0WttMg-z8q}*f4W6yEt35$;lXai@Qv5LGf9D4G_RDG3_hpLU}F#-',
        'Ky#9%(btIq#1hhF%%^8ZC(G4VE)$|A%qh0?PT6cs@lSEErAag%iJe-zs@kEsV8fBAuh?4wG<XB0r{g+dB)tK=liOy0`W#w&Q%Yrf3#<<I2CdqSH1G4&',
        'C6=4)W>Qsv>ju;FT9>T3njY)&}cV0LO9K79z|LK3l11XwY|K0<wo6BixJ(%veKrjVzOI1=K(VoZRw0kxh8XN87y$g&nIf2RUNhEIO_61GimpwTw;#)m',
        'T6dm?>NK+OcKkbPY8VN2<#SN_LUIG=c~O6hlz=pv8=q7adv2c*7y2H<ekVb^ZMZT-ItuWhnWd)OOPaVUlNcu~AM6i;RYe6o}3f~V8z9Lx8AXla*1>Vu',
        'v?dY5IuDU+#k*buD4kr_~RWX&l$okuXP&5_Fw=h00YiLFJQ;7!EgOHO3>*eu7a8er<tCSej`T|s}fgz*-^5afc-;LJDY9C3b)%P-',
        '97>=54ij<?ZHrg`BrPNp5)$AXhihxR1L4b1ST9~>oK^ZdsYGV?2$ZFyw;Cy03fkpi^n#$I!|rC{)CFwz70F2u}|-',
        '#11cRWWn%ni!cAa>03_Xgy4G+g+UStk*F(+Dm&pB&#dSo-Qo+o-wbK14F%T(Mf@JK|0gKyKyw1C9;NE5D^%Is-mKxLaSY;k#@NE;c;waaYc>|44QfZ6',
        '|4tM6-}XJ0-OSQL358Xy}Ltir9_d}all|7oOg82`RDR$$$Lx!W$|}J#$w!#i;?19Fe&OY1VwO&1Xyd(_Ls2ZpC;Zn%T-',
        '@Hjj3cIp($ZZ8Idy9l(14Fst&X7fy>D=&(zk#*t#wx&J4^zR2BAh9M23Ki$dWOe<d`2Y$!J;D9a9-',
        'jayKeAn%NE_ro_M1uU#AAu%ylV9)+NBo#|5w@goGh_M)Fpb&~WNL#1`-',
        'Rq9aLcaGV&&=Hk@vLF@PkP9vYkd4GKcIifO76e!3NCncz_QoB{x|Xu<}p7!;foUNJQUygG_DXl9h^^5EY3NUS#<0xJo2Lx_&=AQ&wY)fPzi~Gkk~|oL',
        '4*wwj4jjd?1Ex~|M}jl38v@Ke8?fKj8fs)^j*iUPRMO(#NT}qj_LKVbDDJOQ5yRmA}9(H%2c9$`t1Ox%|C&QpZ-inbPXfb1yoBViaf*l4jOpc?UXnUK',
        'rQW7LDq55C^+pDWyw6c4<`ZFg!WE&_>O|}&V3paJDW^RZl)di-',
        '#9Y)wPB2$@;S+;UZ_d{0wU|7emACiCSFs5{)pYXhG_aBGRg4b5%C0AJVJpZhzHoW?yrHEO1K6;(<VxrP#D4@A^c8>O*PNPTyVF0Cbmrx6cePg+i~eQ{',
        'qYids4y&jbew0$M9#PF*+Xx+22#S5EMA35Tmpq6P{wDQ44D!^7?7#QsbMzFv9V=#+~5O<JhYmIjkkw9e2(Qun{MK?)z4$-',
        'm<xYn0?lvqttiCE6lVG_F!fI%*=_jxcMv+LYf;6MWlB*%;R~Gin8IO-',
        '0^>Yc*d}f5LCi3NeKm@SoKhTP5u&1?Hr1qkWt04yDdF}yGCfN%y`R?X76Q!(eGN$mIP<u}IcC{1daDCWxQr+<BuR<DM8shPc)am+a>tBIX(v!bijN(W',
        ')^X461$*}i5_vLJQm3?L1m6}~P0#oKVJ{c_#UBwy!fAi_RXrdQ2%vT)>VJZrc^HWfg=T^2--_x2d?TZ$*hA4?*;S)l@I|-',
        'YW?X@Dbu@aAK$IY=u;b<?dz*Jt%W9NLqZr>0aR6C>F##^kC|XmbvWwB`D*D4^xEW6p#(e*-',
        '36i)<62@2&f_TnH89_aWDykr%AR5r7pxhfEb7hB}?Tj7!b4(D>u+VBjJAh^$lTO3oCl2!cD`qf3K~_v0xN=sS{)HA}8O61`*}E>G2udtHx=C`*D6ZH+',
        '6dc8y&OMTuN<yblGUsSJ!6nL__q~^y>2*Mj5{ppIBF2-Ekr+ogJdytRR5b8-v8eGhTKCh;?`Lsz6g4-',
        'D$qS;WOs&*UHA#q~fFQO=(9IfL;Zd*PJvi;=%j$?NR6>gpp~w|62JbD-',
        '3hgi=Lr4QpRuY=lF>r|Rf>#%u|I9;3s)IBqHy)URYIIK>eQ1CpU&*RZJ|As0n7!&I_IzrZkz)+*&^EX-mJsWdo+#pm+ux4pE_$P-',
        'eC7jtnAcyUuLeZ}w$}@o7jW(cFQt`UPaF;twwFPap`ig%Trq=<6nuwJVk+elVH6PcRjBkwU@Tt2t3s|6odQieSSuJWh;)mrP3I61q9nq5@KHc!Exr`u',
        '6^vDEEL5X_W~0r5C1s-',
        'C`E+KsapdV&=mXz>tvqf5|LiSiV2U38^vr;bmp;PK;hu$qgP6gE<i!+Iw|GuDewt2DX49iWbN)Q^*3Fc{5k7UvHQfCT!=7a=TCD;r5ih+oq?LKD`t;x',
        'O@P_TY`y>C0A$cQZjw6UFG}CE}SR##yO+qE<Ar5MkDt&~tgj5AJ1|KNicmiu653$VvZDw=>JxAdj#s&m|B_}{CN*aR<1V|*5L+~ni3(i0hS<=i9*M>=',
        'FcA}ac7#sNETVE^yAG+h`@9n+j>pHTwg0?4#qZ;SF>NtF-L!3qQ4xh&ICC5`qkDz^jOg_`%`fpAWL|`;w-pW2sd`Zm8mBU<j-',
        '460%kbQiH)zu?tI!op<N-{tqH9{#9+a4-',
        'WAIVUHsR%E*#IWip2xB470zUs~&z5yURu2(t(M}GzVnk5&coSe_OBNTHB{9K}CF*r77*^sqWa9?K6`m{%Xm<o_ZMO#Q4-kR>9_F2Up1kQ<-',
        '_@$Eapu|%Cq3^rN~;F>{y%M`NsCLKbp`oYiR-SL#%WA%wFg&Z7>)SK$M&*gQ$J^4RN+r9{2iYC!s~hQ%T6E*w$f}b0S$=4A(CK_SgX`}d#KHe2#1B^&',
        '+{C8f*~*<##4<8&UqnRK5OZ0w|ETN2nm}8lR5AXXDxZfAWKU45rc~hKKj=Y?T!+M!uEXy_v|oScLPkfz-JxQySWy^6WCPx@bza4z-',
        '8YCE`v8d>)U$M`tPEoY~0$%?5;MGS)Dkp(CIV?6NAk{d=c>QBh#E6RuL4N78vHSb^LvdjJy{qda;Ei2y2w03Z>qN+5$^9A71?O09SN9uQ3KCX2nwFZ!',
        'U$`zujXZLtzcx3eqx2uJ|~>EVi`!6zTJP>@5+hN)&ao)5Rl(pG<h75tuC$bq+!1CKwJx9QYgJlh^-',
        '&Y}opBL0fpQG_npE(@b{uaPsRTUjL=}OwXj)AZO?L8SeUKlTt}puvmD_3*L#f784g(O>o{5CqkTfqLNS=5|V}8{Ms0>=I1elF>~R|0+3<wHE_K`(Qk0',
        'W5zMm`WrL|0D#H-',
        'v+I<KBMlse9$3p+GbcxR$##oT(iIu>|s9oc+bc!~)>yUPY>LI=C8h71pm^xG)Lkj}tFY$DmP<RUzSl`XIyX6Xth{Z<=gAgvAi@pApUlb9H2)+G~6^hT',
        'm&IqOr&KroplswTqA?g=Iv>SALKnxxwSI9+aWJ>OG6hZBO8iAn3ka~|-rK1@ujz|a{G-',
        '*)w892|jhlI(GIu^{c%uaMrZ=mpqq<9>z5DF_GmSO<f$uC5&@{4_#ZkbJbmAHVs0bZG_9w{VXYC<$0Y@dN3$7_MO0FQJ_ZwhU%v{msgN7X$>zwZem&_',
        'p8&2A|dO1r#0%3`wQT6>nM3K)ILDS{ym5DYIh{*)*iv6<05CbR`qxQ7zEI;H^PL@J7J=tdur4sv+H1Ub~Tt3j|`&q^o@zfic~3rj!*^0uw@j?XF{fxz',
        'X;7kfXRFM_u;Bdf|T$<!BjcXBJNrao`I<onS)Gp8M-`l7OgWNz(#{lC>Ri5YU`d(nbgH7_WE*QP-',
        '`0tH%M}LAO7q|0ap@@Gm5)>pnQs6<oxC1axhuKwuOj2CvdB4of!$6w$efEzlwdEl@3<Tqp9@vu|PT$b~?O-',
        'YSSDSQFwL#6g)>JE!nDHi!@+B=)o#jx<*Y1R)~O2q8uYx&sFWO!RZRr;m}3>YV3Pgv^5%MXjJB1VML1FqFAF#305ZVi4&%C6D6f9*M%-=-',
        'iV;;KfVZI`z{6GqntuV9UO3EF3LUu8cwulRF`Go_4O}V(>wTsKwNTZJTG<u<K6HDz>N*P$H0oAW(wP6D5il#i-',
        '5=Wc;!X>`GQwdWzKJ((ZRvx~ZN5&O`2@aQaJ6LIkV`k?sCHHV)o3yEK~M$szEy)d`(w&aipM78b+{m><8EPu%@{ez5sUPFOvkFiEIqIUUW&gC-3(#-',
        'c+P(JCCd5%O}*w$8l>eUMkMrh=Lf4FWU(@0741XiNB2H72Lva`1HsGQl_j6;#0&ig!xUQqolajr1D8`tBu0=B8V1cUs|zCh+Y??$Sx!&ECdtTwIXPW}',
        'Mh_HX`e}zy2N`*nKPg)gcxvoR1F-t-',
        'Q^eBMxW&@;>U#oJTfKv#GP6qUd8q?J|63$nzG)f;X1JTZ#ruKjdj_P<EtBu1ev2cYF;cQ(<>5n1*0dffPs;;~-',
        'G!_C;Dku~TV{%@Nlf8blDRHMG1Csv!y>tS&@snaGxZ?f&iKC2(hB**gYh9v+AKuI(@~M5TH%OGcl~4O=hZPyhHbHf`C@>NSUQ%+nU*h-',
        'tPxt~cWP`~R9p_kMyvMzPspBykmqnq*8MzCtPJrPESOV9-=px62caSQhmfj1jCAK69J$ogXTVF-WHsT7qO<u@n*TUG?;Z62^uf?#>xlXqg|ujE67W4x',
        '6?r!?l19oPRWFYab`R`wnK^5cPX6zw`;6&MJq`&<jufEI+<|H-UEJzXHI;ND^~P{URLeSvmA_UiG}cq2p2-',
        '4tDO$cwqNUJow0;V{{Qi=1nBBh%o6zC8d)+NLZAaS3aDI9U%^d`N!9AgG#X6po^gtbtTC=XiqDh7LbCk3vmwZPKJgMT1y-',
        'Vl$Ed_k|80k3Q<{z92kZAUdL(AGF))%k>u$VX=m?m#LeR-aOsI3)E#%fm6fBHv%ENl+1Y7=FecI(Vhw3N&P2F_ZS|{Yuny>eNdd)#$51=^V#51lLLU>',
        'E7&TQYwF>Rd7EEglT$w|LPsY!7=$ls~US>$vL`W6N6~RlFz${fd9dIorG={X{S$VFd(@<u1LwmDgqONBS6Gh5~FcG9s!c;lraM-',
        'o2;3Jo=Anch>d*Yrahrli>8iWhcVi&)A*q!v|BQRND10_lg-Z~y^U&F@i-9Qud1~oaQ{u7!1=hra%MZq=qk+j+vUm~_Wlt&=j^$_iu-IT*YM#Fhjqdw',
        'w+3Nk++UJwzM3?TxA&P}L-%e!hT2yJ|Ki&ltiH{kA${(8ci5E&uqRqE?gZod1gOiaC>(we7HdCq&-_>L7%CV@X&&8SEXq1*cG&Xxus9-',
        '{?P{XHt@y^qTLc?1vK&W>wegi6Sg7p!CXNz2*wr5T#DmQZrEISb7RB<*1Hl)x1%sx4>P^2N+#1=44UdJJJGL~5{sc4r4s41#CQ19wdz5_Ge=pQRl=1K',
        'rSN_fK{+o^9c$jc>7c(}!5~@^A9U7ti^Pc{!j2E<Wo@ZOzQm*z?b*%fR|>cn}rXc!+TA>)8LLr~k`uR+c|c+q<tvTnUl^g5(*je&gSfZ3&oNKT8s%Wc',
        '3`IDeRaaDVlgvqA+9Og5|V3)684AlA+!jVwAZVNd%8KbLE=3yxDsY2So<;{T-',
        'Tlow%omY#Dt0s)eA_EO_a)?Eca@{~=DE0_Q~fb!5f!nb>(V;!|wA7{U`+ebM`|;~|ozWP2R4b(W&uBnXxE#4Zfb+p`oK4^c7!Hi0mNAP`DM2}KBfw_J',
        'r2@=iwDD#&v~kO<%1@*0BBQ?Q3wsj=juPq6)cEB?cL{HG9TENX`Skkv<CN>6Div+HsKw~JPG2aoRm8$?2EWdJQ2*kqV;<%RTiPG)rU2z(UJP1rj^XYc',
        '~n2@(KdH@PnbkR(t7yy<%CMgi?couUIp1h?F?6psZaSaZ=&c=+RM|7)C73M!*|{P|yI;{GFP?Mg6p$HLwi+n%AFPqMA}EHlMTc-',
        '?_eL$Tl^JSjp8Ly9Nuo?s%M%LU9Y526#yT``ytV;!C*NIIv-4pC+8`*w2gn-',
        '@GT4xa3DB3gB8Fk{D1Y!qr@`RK<={L@#JyKb4rI;aJs)U(C(hpzz%DMfv_ypPD{n30^^OyTV~UOI^H;JiihGTwV|mejRqjDG-',
        '326$w}8JM6z5+#U7h^q@o`i7|W&wt$HJt-1c>V2AaW*!0=;$>&wMm#;h=DT)K9v)%yzMPe-XW6qaW?%C<YJCxp?Eet>UPjF8sD?ub0V_w3;)E50u)M`',
        'Xb<3V9D8dk{mbO!7>q2Ly!*E}Ppa!?!m|$#(wf*GTo+osV=7}b7c**&wlu=a<s~$pYOHR#11l}_^lyTc5o0ybc?04T_)5J%~{TLNHNXb?x#Syh~Laah',
        'h#dFa+`*_zo%Pd@C80e4b8wlv_i&(x&c=ov#O%#nC5aD%{B7YK0(i69IkM>ngXWkL7V#foYp*LDdx=E?nh`t4b?8x`>`)7?XdE+co?Hg#h`>5GtnP0m',
        'A*Y2Sf&8HIdk%S3HtQlqKX-Z`X`sM{(`I#DDzuqxE2E7By%bp!FF=;vB{DP5T3xpiL_Py+T^j0QjKB-Tn#ywsF^<Rs#2hM%bc51DdzR@18zv)Ma2$kR',
        '%8hbNJCBtcdR_3$|R`TFOvs`xNUt(>_nvqY?-',
        'fxMT25YOtrk{cSVR{Dwj(etX_Jsy3;8YN=yy#5RJy@87QgGM0jD@E(xb5BZkQjE|`y)<1{@tv6?k8v#%GLk$1}5+Sj6xw#83O08c@F2C{!Yd>XM`q3f',
        'yuqQ;MP7iPW%*O0xG>Z-gk&hiG5=keWL{@omZt@$~f`FeqcXQFhG4~Kh^R|0yjWUwM5xgNs=;ajxW&$B>si^-',
        'Q4*(^$>*JmgYcWcyQfaU<~tzU&n&|&tqcUHkvzg<{j2Y|B=sQa^0sH{$x|f-%ydK1cAb0etP2&HCsjU0PAx?M%g~Q1y{-',
        'Oc@u3I`f4v_=j=^1Y8Npz+2pft?x8q-mYD5Wvy|TW6lP~{W;(l-',
        'W9GjdpH^{2#H!<~4D>4HnqmDto>j+qY$!MdGuL7APKn}>Yi>+Q_umNWSrDCtOCwgFw2&36%M|L^AoD>25=ovqDm>k?MEM<TpY9_G1fvesSyWS8?z%IA',
        '1q_(qCAIf(?d;){<aBQPas~VCN12&=kiq0d9DmrmnA*C5d&jS2<L<9BSUrk?@Gz$K4ikApeWw!FgyE%zo?aykltMiiC5at>{}Ia<uDu&Je394)+jm^U',
        'ir}?$_7{v#XWV?}HEig740`)WVs}6Zd|U<9eCF;;8^t~Ea59Loi!pf}BcN(faflbZc)Uw7=4j%<QJSsK)A1W9+)hfmlvT;Av8^hld<B<$?mT{Y(*`DI',
        '*Av^Nw5ANZb~q{nG0pwL#`PITpB|D}0juPx=hC+-',
        'djt61)i1_1rYJNe)meIaj%8o*6SlkC*u494^7?(OxuMC1=LHAU20s49dVf!4W((Efa|r9b3`eI><QZzZ=W`1RC?Jc*+0%G0FvfFEx{1A8Cn$H8VYN)V',
        'o^a_c%h|tshLI(`oPE+Car)}l(cZq0{=pJG)e;NWR2Uf*maP?bZc)a@3;KI4WBcJlSN39p4)ZU5lwFrCm%-',
        '{eI?=hddonfyqB4uVHO|hnD)Q6|V`hFR3Ur#^&_Y&Iu3SKUW)`s-q6)SH(nmeI9$|u`PQ98v_ZT{^OwJhM4dwW7X4{@K{-Bp{+$|h-',
        ';?w!(AHRZA2d`&h*EGq>0mil#7*l2HyM{Pc(x&jKtG-ROHOfm*9p{ev``P^NX8<tKxK@TQ`=LrTrxL~Fy@x*`<Q>qsX!O}{(cY8J=h1h(nlR}@F&IL;',
        'I-',
        'DQFyY;9mIP*E<G=BUjX=55GVr(Qhsj+W(h$EldOQWyMt(TpGm5nT2_8FpLlqBzEq<;Zb+fSH)nv4hce20DG|IDh&IV`H4z>D9WaNZlAi*YyNvnMade?',
        'opJS^XmQd1J2KXb>#Ljvqii%kMvDig24_a`U5jokT-VFnTDR`DGaDuxIlJnRw`%kdOa6D-X~e7aw3z_!dTLL-Yqr80}xd$WX#jpEJB_RYKpHFJ$`0uR',
        'SRwJ|US%XZ=6QuME7aRm^C>=<-2wH_f)4SMtcZ7ZL7R48;U_I>Bjw-',
        '(VoDu<Q0~n4O(MqJ*C1%em{XP69j3K;;#TrVB}m66Lr|qyf{dCV%(df4~6wo^gIFQR!cz-3n)-m|lgdVtUj>6*V@}%HmUX-qCN=WB+>WSDw)@@hXMG_',
        '2k|M^|b!`^kqj)=_O~Wo^{f<wQ}fkm7$gTf=^B9e`ytdEJQua)G6H~3dVx51Yv^CPIBah_jB+2`XBp$ibs@mj3s?<#-',
        'uUz_8xMk=x{Z;3HisJZC<oM<hPc<1A(<~pH{I25(>U-utghJH0g^2e(>kZg@ZVVgE)wTIEaJzZ-D;?6P;U2ScH^v00000NkvXXu0mjf',
    ),
    "PLATINA": (
        'iBL{Q4GJ0x0000DNk~Le0000`0000`2nGNE0FDvztpETS;7LS5RCwC$oOzU8Rh{oYd+&439c!Lam8wcA1B47fm=a|QV1NLIK_*e7*dl`{;B0HFhzg=D',
        'bkhrU0fM5owAenLf~1XxIe|a|nMgwB)I3++`3(E_{<s0@ZgIVSOu<**weDJXt$Wtp`+V<j`2K#seJ)I30uz|P1ST+n2~1!D6PUmRCNO~sOke^Nn7{-',
        'kFoAaf)Z4c5HY=<vz(EEKC|6L{B1WLW#Yq?fKLp2ckfRWUU7;pS8}<J^ft8Q>Vv~^H=U|IKWFd@DScDL&G;}CXf;+{b&KQ<?mQ7mmXjaI7<e#t)eC~i',
        'CQomITIgb@2vAiIYy8^L}rnJ$)8B;iUg(_+&8Kmf-$26*2;HeO{huEQz{#?YJ!<N-',
        'U5!yJ&F{gl;Ce;hCmH6a^(lTwneE;r0%HUW*zW$Xj$={>}npJ@?22uh_4hbt19|0mktU`2zh=r(xu8TpNK^+azkcCMRs$N4%p(P^PT7a__6JrmlRGKf',
        '}_%j?L-',
        'h1ldbTn6%Z%irmw_}0Nlq7oI$Bu^BafRJ%$*r_RE<}#Px}ZD<$8+(j(s<$#>oS=8G~S?#5eMl9Is<sN7jr^0Zs9r3JMFzZ{rDr4f+9f}@w??4*}SD20',
        '1**|dDE@YdDDNPoh6ZN5hOLL0Q5%4PK{0qb}WKI1lC}!Mp7E<fl&&r!BG)v7l;TdEl4TElVN-',
        'v@XdezDN9dT#LCB>BPb;at&eX4wr(HekXe%m1D}zxL8_~2-',
        'q{4oPKD}qv5zV61Qa+4kiG!jxeq%w3|<08N1?V6aUH@~6{@KgU1yMPjav();Sg5bN$|w?xaRM_%~>ZLOH+LnGiS`Ed)+RqSct$)$632}ABWCsBIYRa*',
        ')d6`tJFI(2DS`|_^U(4H*11T8Wjl=fs7YnU<Bo6kR5Bmi$iuCRaJv_v&indut6`{3y3)bgkb>*En=a&w;P-',
        '!2^V_%Gh}nnKbGOir?;X+aE(W6YZGTLo=G|t10sST<lcMl<BBUjs@^d%(7YJQ@Lf6bJ!SV)o<&8VyRtarS#&Xj?AZ;T2T_EsPD1Yk=-',
        'szqOB=!NMEo%po^$~<H627Dtl7Su`q~=8Vv*kd93mReQ&cA$+FPnfC0&$(J$pLYv9%Yi6^`SQ9ryY8<(INy(`I=`xUgC^Akp3;G9E*P3hjeQf=MZ4*b',
        't0lv0a-WVZkq<91WefBc&G!$Z-8_f25)+MN}MSJX_%L<-g{f4_rY!au^xSQz!-~txy7v5h_w1^ADfKgAYE3m+(-IX3o*mC>Bekk{*5-(9<)>l-',
        'AaFh6}4l`$ckT)EW<6GPnlpZov*(qP@G2(SB6iNAi2o{(ab?NAS{39Cq|FPB{5!L?RNN=9hQgN@wp5ikV$xGdY4l=ouIX6vk06%N4ZJScKtBk!POWfk',
        'YP1jdSWLhcUe^O}<d1vulX<$@Pd5Zu{rk_`(-HuMS)b3|&MNQWT<?pvD1#FyljE43!QclfzU0fn--B<oV3ke!<XaA44OfI5wcKFv8bv{tWF+E#!*<U4',
        '0qC$YQMprBIPZ84UuW1y?DmQ!x<1aUD!NMonE38%21ILljwt$MRHFB)RswYuVE~D7W8ovpOJSpdGO=E}$YPMTimviyG@iOA(dJkZ7-',
        'g(FbXny?~qUdX&Apx04;tP#DWFn(g876~Ce~R>P5p&tzz19Fzu8W%5u6U?YnlU?CDA7IOfhREiiK8s+|fUx%O(rBF(f%@pbC9$<8MoFK3VrVE=*k?4#',
        'NEC&^W+7^NWH86}G86)c7gXeA`?7N2xKk*SNbUoU-',
        'jOB}11H0EPCz~DP>Q8=_>C+~m1ln8c2*e^bLJ0_<jYd(fmz7rK8xdHup_`t*aiTz|O2zru2am)G3=L-}6+^Vq7_F$QOEEAwKzm!edfP0}tPLc-',
        'yiWkUPG8c!p~#wu;7LFk&>9)^VN8%*j&P(GRZ+y|SK*p|E;#c7@|lQS-ltH?v*P|A^S%q0^7CKb!_u=CvT0jC8@F{5Mgmq4D_F{emH8?sRf&Ws6v9ZT',
        'uB{~SBSI^T<x1@9%_At1$v8%XqZO`WaEwDs%Vb1E-',
        'aZTb!m#K#;A(7b0&)gz4dewP(0PS)N626i#`d9$Be3slM7chWIPM@8E;yTK*KT2aY@Adq;L59)QCV5VhUYtptR)tYVa1}X&wGwPm}Jty7>&{zV-',
        '%XQOIvGEMzeR%9)7>#Dek)cCO&@6t<*M7Vrp9*7o9a1qZMZ@y?~`>oW+F~oI|QAiDL|Y5D<^W)!UOqMin+0L&aPOHQFeM1SJabA=+6$xenH7$mdYXqO',
        '*@7q42dEma}sC(|qv#=Wz7GnIvK^FTAjajT?IKqcR~u2<gfc<KqG2`4Y*bA+my!5X40^xUR<9h}xPe4w<n4fMhC-',
        '@eHn~aSiM@SRQ?31tX(<jEoI)%{5mcRzPXOpd^kPQ*S+iKdMn&o);5D;AtcTv_g#uvZH`X#IgN3ln%fKh!d0p7}eyhA=HLFdpa2!$>2IJ3WZgI<7kZ0',
        'Xao6d4lm{q1|eE2L`A%?VH<q|S(H+=G`BH-?j)kf2f*{<fFhnu5sMj=kyjion;GS~XV>5teLnfgD~QJv6iY=$bJ@2~#+X0;Bf8-',
        'v!m0BiEK3SX8l?=9DWN<M+4B-AT}?dyTME`AQQ5>@|8fU=w{HV1VW?<rZDsn*X>?4P3Z4P0&|0A!gAh?yTY*->(lZycZ{IEwsT8?vjt^aR7YmQ-',
        '!1G=m&V{N}1zLbGDk}pU0^k?RL<hc)N+r4R+c)y@D=vHc2#mJ>gNn9;GiOj_EQ=n`V(9=0A+(?ca>FosAH|_tdH3RFw6@RU_(jLFVE$#;pos4mxbjoC',
        'pmxP*nLG(wRKyZ-upn5F5D^d?5h)AGP$-',
        'tLHo`Fmlt%rRd>DlRc;0^P7!ifxE97deUrC=gedjw|e&xsCejy#+S^r85@lNlPAdHno?(iVE1~QMLlqO#^q*G~PZj4eXq%!U@=b$F8|I#v6Jhhoko3_',
        ')|){1gmlu}q5qKF7Agpr_?0wT1E0SecRVH}O)=$HF|hzQwy26US7aZAbfF)s%~6rSUt&8x0|9l7*PsYF8UpsbH%HpAKvg6+gKoq#RCjo<h@Pp;p_k5_',
        'C#t<TX=8K*h7njc($4pTcOaoLsMBs1L45ett;DG;$3UA8piDpK({#+dyIEJiBnVKgYEUy(K<phXBnizo-JHO4UjxG@*UG3b}C7fTcb2Nr?y!VTcnfr&',
        '$^o#f%4Bmej{N_%P9*sa(XR4~?FPyh78*roy+_dpn0rcY@i6idF41qo5cU?|tRj$`m#RW8#UhcGP5H?1|+f_+)eNxA2U2ugub8jav+vtRgXwE6RG+sG',
        '0|;ekb9#iEljRuJtGYdep=o2ILm1NmsNNFh_AZ{A#@Rz+dh!eEO3wR|m$-aQB7IEb~lj)UW9lq!>y@C-',
        '3mA+~H`<#g_&u$26W;8j+n_Lp@r*AR0Jj%(nR5s6^*pW~(08j0+IMd0|)m;S||qHKvU2(W&MQc@B67DYe_MQ2|TKNMWo!$yME3S$&T>6c4jl-',
        '88O5Jd1immmN?$Rj{xHA-',
        'o`SRBvua2*$|HA+*iqxW}iqA0|13`(i;OKV=w{OL_^>HjC!20|O6tR^{7WF%BLHXvpc>Dn~8YymIs5*9*?F1sGef>^NNIW8Z*^eVP)-',
        '^m|;{{VG$^|Us{iMuW~6586QV6EU7gG4^sNg&n|g%QfpG&D941|j)u0UL(2OrDJAxHzu&&LB_$Ht<1w+8=!e+cpIgcbGiZOR=VgKds(NQ$synd;7{=7',
        'gf%>Hd4fsF2!QR`_8!#k%;R)aV=VFVxGrP|1e(6<H6rPf|Zaku<Y5>%~&C#GNA~<h$sx$wq+{<7;Q*bq}jD|2VofDA81MBui2o{nqp>*IyZ*t>7?j69',
        'MNJZj+USTG9yKDnIf(Oh%M_sgx&jws7N?Cu8T1WH|7yD3gZ}B>l;v5jL{T}B_tB+Yg1%085)}#%UUsth{xk7r5G3-p;+2)<qDMZPH|xilV-Hz`#A>p_',
        'A#qoqa8&<g&|$%vU_tEoqc_rvGh!enLP1$0%ZiHG^?K7hU2-',
        '!DpI%(Bn%`RhowvAlZd&vFOyJ}eASB0uX<m0Q!7wgSIh9=Fn(Ab=GWI%9rz~`UirlmjdJuU7jVf%my#dN;1gmc;NClbiE)H^^B152Lqu3AqHREJLpAs',
        'O_y%loh#)x|>JC9>%|`X@L+{y$jBP?IRh}PXDObN`c`V97;vOi$=8GsBVMWo{d<aARJBWgEyS(D0&oRF8yXpXUVNmTSvb$%LPks1!jN6Ja36v-',
        'no_;37{bQt)X|%FvEYl9|D0f<_D+!7t*vMjzI-cOv_jB_#3mHWC+1`krdD9Ua{8`=zpcF=V5PBrXc3^<<#4H?lm{?^yr=D{OPcOfpZQEB-ciK15(-',
        '*?Z?{dHs7;OEO>H*wjwJcitQS#$iDk|f|<CRREdN9hC<wf8})YMkc(>20z3+J$BcR&An-*5QNL+co9OwuF~H6C<7H-',
        'K(kiXGaAvST1c5C?P&Q8D7PPa%4_b3E-tN?ng}-',
        'IuTDlw%HOyzeD;Y+uFD@~^6Qj0?Yv%Ee!mBO6;NWO`|7no81xglEvYY(zmAa@@i>WU@tOv^6nzRs$6^37%fJo+Tf-',
        '1LxfL5cT&V8?(^24rPlF`6w|6E_i7a3Z0KoZ4Hpr9DDKtR^D_m#mG{Xo<>j_=8#X{%jWN&`{ona@XVM*DVIPDHniYJlw2Xa<4<t=+5c}FNX(X)9maDj',
        'xZo4tLP`NfMSu`RmUt{qLt`zK6>$!3uj8<Jt+chIa2n3R^EAFrB3TcKDM)zecqP=<fzsIFK^PiF7bA%JvHln~e2QY|^W@6sIBUt7gf>sbvR^UslcjGw',
        'fvRf0r0;o-',
        'ShG(i>ryHR1W~!xj4a9uBn3$;h$~dBkGb>)q7C<>7T<*Z&HMkaHWj;Qg(SAzPiFHksjjXg<}`B3c^|<q23Tz&(#)MRoz~_C8tRj@HpFRbt|giF2tAhy',
        '8<LD%{2;=L!6=0bI1wZV;QK*_b30-b0?X!&TiCs48(;szSLmXRsW(5w)(<3KmlysO0*@E(!;g_VJVaU@Ml!bC-',
        '*Z3(0!ksumaC+aj~wP=hJYqZbnLkhp9)<+`p@6rewUb;N1)>=oW=_L2QI>9x8XP`2)mFdB#NM=<q*cR!pY}-',
        '6yrHmRo7A1SW9bl1yd$h5KlPh$P!OGbW|oeMz=7Y3<yzZPnSzLUvaBnWMOWEP1|0gRCFlVKCb=vWk{@s#AVAFz4@Tm9l~Cl!1TMtx%df`4iU#7(-',
        'cviAo2a>RiyWKJpdb_;}#kBk(i4+OB3Aq5UOh!<yNAi5Se~1l8m7X8PY*7nO`r#`dygRR2E;bjH*Nu6@_fuw2rk;{sPx^sBN6b@OYlZ7k-',
        'NILXj!04IFw%JATfmxh{#L6;qnhJm5Dl)>_GUF2E0bM8V(b90!Htj7!8LPrb<BfAMmVJk9UBk#xsGwtaWe8xsFto518kkuz6<5tIe2E@v_aa0C$t6i6',
        '+o`35vdNl<Y?M)OEz9MvD;)Oxs`ny^c--6QCS=QH<|vzaxsj%AlF<Hj5Aq_Mt^pZ(w(GTDHCxc(Om4tMdZdv8V=L821i;COMwMCecxOVp4`RqStgTa?',
        'yBkp)`<0zwJF3XTJTRpfI6I5U<}arEg7+;jdLnmEmCGdt<)%=l2bCJn$%C6LG=3I&zRVZ#_EZqbgy7BnWN&`P0l8i`yO6JjxqT@z4R+eh^DYP`%ZDGm',
        'OfFMjVwoPWk*I(H8dukzTnuah7z9CKs`>B=<YS>f@O{~M(|>KYDa!SR<fT(E?RS%`7)eM=!fLOwG{K08V-',
        'J3t}dPoXeGp_IcfX7Ga?`Fuc7br2H9nEc`I(S6&=Z@B7sZ5^nK7$vBn2$d;<pH4y<!RR7Z1NsD_qrQu7pMp2;V|vSvD&Q!rg;Jy`4F}NcL!>a3efV2$',
        ';+6+Cu<iM+G*`RKo7=|eCr;-VRfeZGY{2S>q3#@hR4mUfFxUucTc(oQIgY;QtK_G71l1ulTU4bBx;%N4;Q-T<BRppcqCzAxRJ6??vv;)u*!}Ip-',
        'n0hEU;ZF|n8+E=pdX%t<3Y>S_uv%Az%{rHRlNAcQ&1d+L^b8^u?i3+<${+Gq5_adF$QD+mpR8SVsvPjLdIw2ytyp9<PuIi?hu-',
        ')Q=EOt=cs9Jr)O^`d$z72KibV9N1VwqC!RoMRXahD<VOz<VVey8via1VUduFVNm|Pb35St~x^OzXh^{#sj6?IRLpkfLQ~BXHu6tAUuJhW3e*s<P5<lw',
        'Q#Ky+h{mtY4`zAV05lT}~#WBzUII4W4Lwr;i?LUqIMr|P)`By6AlNk*LaZQ1}8=v4`Zrwpg%k@0DXAf0Qfro#78xoCzL_}6o+tA4N^*cG`%o)r-',
        'q=C;|F`FYl{Ro47{lwiG7Fj5X=1-62@a}t*@aJE_i-BugK6b%U7M;9+AAX~fLqBx6tiSiW>MgZE0OB<=<F>VIzpUdgUS}HSNHpT2r`&|ikAoZEf5<05',
        '#K#bUHqiZfF8;`usi}{1;RUDC(N;lIU7G%`Zk|}RhHqT|Ew*fZ9<dRpo_{@s@e%6l>WL+jG&DBT+TP5Wr_QAihP1a<@Se{<#QISU@f4(MIPG027Vmt9',
        'zyI1*DCJR|o<`9Rh&z=eXEbyD7cZp0e~fS6eiy?VR;#xr1_BgE)b`6dUVA1yuu194Bg9r!p`sGRJP6(Wu3SQbJlb<XE3})yb3LX`tzoEll!od!RW(&C',
        'S#mN?+;H*x&L@-rWfG*ST>@*Ua#OUm)}XM&97P}+*9y<yb`E|hNLcP}k7jeMaw-YKB8`nx7#eyJ$D7Q-',
        '2Oq)HtL`D2%dlflAD_MQ69DqAhXz=6M#BMez_PssJ#Yi6?PeI=g+w8ULc$_S?-$?71MxvStX;K(sjZcGj$vf9NKJJW=PX@97?uD?C*mk9$+*Y#DUH-',
        's$MHjj=V;t8!gUOVl0|HY^#hXe7+YW3#cj9#5K)lL4--WJZBu7)<;Ok%z`y_Y5xV!~8S3w$t8X8N&TDwXEbw(7u(TV0r);zf<vxb3C_rflf-EZNMHxj',
        'DX>7&C3=9tAt2nFIZsPZUTF<8KJ)C&b*(^HoObiBX6iUJUcVEY@7uQkW)WDXVJ?!lqC351d+tJ6Gfecv<1r5G&@MB4ez&C&VD^@=9ES0lQM%*fJ(|rC',
        '5-{jXT*K+W&*D$GJDpy~%l<L}QVyTL9ZU3mqfnk9F-7l)J`>OJWD&|7sJeYJG#A`97A~yRj9{$~z;Qsa8c*kQn*5|qByLi{JC$eeXYSI-oEPdZ6nAUb',
        'M&#ZcqC!V?&D|tF*znisNI;jqlY#6lcs;{APnol;+^la!tjf^t>(g-',
        'W=z8PowF^p|kp;~7ylH<?)J4XG0!Tu4@KEp$K(y16h(Wg`@Te@f7iWvAmOi1&VZ<h_H%|LlmQT0nv!@G&L{2pQoWhQ~s%PrSmizq`F76=L%Tt`#LjdS',
        '#Z(@3ULeBeXp)8BJ7XTA4inp+Mg-Oxf^I>q9JlOXMIWR*sg3y0Q|+mz$D>#in|Oyf+ML$G}nojcbv)bk?k4YR1OucNiPjh$UX{KxM$ql12`51m%-',
        '{43~s)3fmFfP3&_QBDAf3gY!O#M`D}617ykw1!<P{*8`9Pp2@_&8#`cFz=8fX=-',
        'WVn8Ri;X>y$Q$u<1&C;!IxzjYJos;L}#=4G6H#zF=QMcOJ9o)_cx&wPp%Pdv=rW6vPnWLPsaN_yJy^xXXw1<*e87}@*MGaS3*Q=E9xB2w`rcl_Xb_HB',
        'Kd+3O-U9HtK3Q~Kr3^B-Q>pbw1if8PVd((Q8S2^SHw<4D#LsyM}hW&Y7^#63+emtof2ISdZ%rFlv#+t>er)hbUea!4Fi&&^-D5##rA+G!VZ-',
        'X$O4gUjB-L9>rwAoIId*55ZgLSph^balPJ-',
        '9KE3=XrGR>!k7QYYBXN;3Sd%@q${(>6d;PjpCUV%Mn{dl);UA{N!h=d1}pWip7vWuKWYaXr5p5IBWiJFS&$IvL(g64?j-',
        '#=w@2yokaDVli5+KAn*%p+q{<VU3oFF=Bee$$k0ow(Dj1az5Y@9c5YzrmglHD@qBuI^L@4D=r``E_qV*IuR)Gp`e|BP=5fKr@8Rx$yqorp4r-',
        'g5NLN=;+g{6$Zu}%0*FMLzB_9RjlFj7_#)b*AqvT$AkOfOV%+x7IQCC+(YsWM`dUgjfH%4V;8snu%PCJ(Dt32RMoie`VQ#qv=9T{TAQEe1e6|)wd#Ez',
        'FX@zbwff-xS=t(ENFzJ*!W+|HJNy6V4?5U-',
        'pp(`Fuv_yO90Cd7%kq~qzbtO`p+I`NjCws<=rFE9RTG3Lh7%(&`KUcBYv*W6dK<9Km${hV>pr>U<=GpVtO3zt+7M*Yk_=)Kf0_z*LeT+QmQFZkQEK!8',
        'K9xPxM0jL`a61mnc0m^6iCT?bEn_Nc#l<M~~WD^opH`Ug767viXBlwUkJLTAr<bgY887k-&XJ~Qip`e%;`Oke^Nn7{-k@Mhru04-',
        'YaoJ?Oq@Bjb+07*qoM6N<$f&',
    ),
}
_SKIN_FRAMES = {}
_SKIN_MINIATURAS = {}
_SKIN_POPUP_OCIOSO = {}


# Paleta dos membros e pontos de corte da cabeça, específicos de cada skin.
# Os rostos/chapéus/orelhas continuam sendo os da ilustração aprovada.
# Cada personagem possui um ESQUELETO VISUAL: cabeça conectada, torso,
# dois braços e duas pernas que mudam de posição em quadros pré-renderizados.
# Os valores não alteram posição, hitbox, velocidade ou física do Jogador.
_SKIN_RIG = {
    #                 corte cab  dx cab  corpo       detalhe      botas      luvas
    'AZUL':    (57, -5, (22, 28, 46), (221, 45, 63), (22, 26, 45), (211, 56, 59)),
    'VERDE':   (58, -9, (36, 166, 80), (251, 213, 80), (18, 118, 59), (77, 200, 76)),
    'ROSA':    (59,-12, (245, 133, 186), (255, 237, 245), (201, 92, 162), (255, 202, 226)),
    'DOURADO': (57, -9, (224, 155, 26), (255, 247, 119), (144, 90, 16), (255, 221, 70)),
    'ROXO':    (60, -7, (93, 49, 179), (255, 196, 90), (58, 25, 124), (157, 112, 228)),
    'ROBO':    (49, -6, (184, 209, 230), (50, 225, 246), (53, 104, 149), (232, 247, 253)),
    'CHAMA':   (57, -5, (247, 105, 36), (255, 208, 54), (94, 33, 31), (255, 153, 43)),
    'COSMICA': (55, -7, (98, 59, 204), (232, 226, 255), (55, 24, 150), (161, 112, 252)),
    'PLATINA': (54, -8, (163, 192, 213), (59, 222, 254), (62, 100, 134), (218, 242, 249)),
}


# Paleta coesa: contorno escuro + brilho pontual + sombra por família visual.
PALETAS_SPRITES_PREMIUM = {
    'frio': ((34, 49, 85), (183, 247, 255), (70, 170, 205)),
    'quente': ((87, 44, 49), (255, 234, 150), (219, 112, 68)),
    'magico': ((55, 39, 102), (242, 211, 255), (166, 112, 239)),
    'natureza': ((35, 82, 64), (205, 255, 166), (95, 200, 120)),
}


def familia_visual_pet(pet_id):
    if pet_id in ('RAPOSA', 'GOLEM', 'ABELHA_MAGNETICA'):
        return 'quente'
    if pet_id in ('FANTASMA', 'DRAGAO'):
        return 'magico'
    if pet_id in ('TARTARUGA', 'BEIJA_FLOR'):
        return 'natureza'
    return 'frio'


def _criar_quadros_skin(nome):
    """Cria quadros ARTICULADOS, sem modificar a imagem original nem a hitbox."""
    dados = _SKIN_RIG.get(nome, _SKIN_RIG['AZUL'])
    corte, dx_cabeca, cor_corpo, detalhe, bota, luva = dados
    contorno = (24, 25, 50) if nome not in ('VERDE', 'DOURADO', 'CHAMA') else (48, 44, 48)
    png = ''.join(_SKIN_ART_PNG.get(nome, _SKIN_ART_PNG['AZUL']))
    fonte = pygame.image.load(io.BytesIO(base64.b85decode(png)), 'skin.png').convert_alpha()

    ajuste_cabeca_y = {'ROXO': 2, 'CHAMA': 1}.get(nome, 0)
    ajuste_corpo_y = {'ROXO': 1, 'CHAMA': 1}.get(nome, 0)
    ajuste_centro_x = {'ROXO': -1, 'CHAMA': 0}.get(nome, 0)
    xc = 41 + ajuste_centro_x

    def apagar_base_suja(img, y_limite=72):
        w, h = img.get_size()
        for y in range(y_limite, h):
            for x in range(10, w - 10):
                r, g, b, a = img.get_at((x, y))
                if a and (max(r, g, b) < 220 or (r > 200 and g > 140)):
                    img.set_at((x, y), (0, 0, 0, 0))

    if nome in ('ROXO', 'CHAMA'):
        apagar_base_suja(fonte)

    cabeca = pygame.Surface((80, 80), pygame.SRCALPHA)
    cabeca.blit(fonte, (0, 0), (0, 0, 80, corte))

    def segmento(tela, pontos, cor, largura):
        pontos = [(int(x), int(y)) for x, y in pontos]
        pygame.draw.lines(tela, contorno, False, pontos, largura + 3)
        for pt in pontos[1:-1]:
            pygame.draw.circle(tela, contorno, pt, (largura + 3) // 2)
        pygame.draw.lines(tela, cor, False, pontos, largura)
        for pt in pontos[1:-1]:
            pygame.draw.circle(tela, cor, pt, largura // 2)

    def perna(tela, quadril, pe_x, pe_y, levantar=False, quadril_y=63, joelho_y=None):
        quadril_y += ajuste_corpo_y
        knee_x = int(quadril + (pe_x - quadril) * 0.6)
        if joelho_y is None:
            joelho_y = int(quadril_y + 4 + (pe_y - 75) * 0.36 + (2 if levantar else 0))
        else:
            joelho_y += ajuste_corpo_y
        segmento(tela, ((quadril, quadril_y), (knee_x, joelho_y), (pe_x, pe_y - 3)), cor_corpo, 6)
        pygame.draw.rect(tela, contorno, (int(pe_x - 6), int(pe_y - 5), 13, 7), border_radius=2)
        pygame.draw.rect(tela, bota, (int(pe_x - 5), int(pe_y - 4), 11, 5), border_radius=2)
        pygame.draw.rect(tela, detalhe, (int(pe_x + 1), int(pe_y - 4), 3, 2))

    def braco(tela, lado, mao_x, mao_y, ombro_y=54):
        ombro_y += ajuste_corpo_y
        ombro = xc - 11 if lado == 'esq' else xc + 10
        meio_x = (ombro + mao_x) // 2
        segmento(tela, ((ombro, ombro_y), (meio_x, ombro_y + 4), (mao_x, mao_y)), cor_corpo, 5)
        pygame.draw.circle(tela, contorno, (int(mao_x), int(mao_y)), 5)
        pygame.draw.circle(tela, luva, (int(mao_x), int(mao_y)), 3)
        pygame.draw.circle(tela, detalhe, (int(mao_x - 1), int(mao_y - 1)), 1)

    def torso(tela, y=0):
        y += ajuste_corpo_y
        pygame.draw.rect(tela, contorno, (xc - 13, 49 + y, 27, 20), border_radius=8)
        pygame.draw.rect(tela, cor_corpo, (xc - 11, 51 + y, 23, 16), border_radius=6)
        pygame.draw.ellipse(tela, detalhe, (xc - 5, 55 + y, 12, 10))
        pygame.draw.rect(tela, contorno, (xc - 3, 63 + y, 9, 3))
        if nome in ('ROBO', 'PLATINA', 'COSMICA'):
            pygame.draw.rect(tela, (231, 249, 255), (xc - 2, 56 + y, 5, 4), border_radius=1)
        elif nome == 'ROSA':
            pygame.draw.rect(tela, (255, 248, 251), (xc - 3, 54 + y, 7, 7), border_radius=2)
        elif nome == 'VERDE':
            pygame.draw.ellipse(tela, (255, 231, 126), (xc - 4, 56 + y, 10, 11))
        elif nome == 'AZUL':
            pygame.draw.line(tela, (239, 48, 63), (xc - 8, 53 + y), (xc + 8, 53 + y), 3)

    def cauda(tela, dy=0):
        if nome == 'VERDE':
            pygame.draw.polygon(tela, contorno, [(32, 60 + dy), (25, 66 + dy), (16, 68 + dy), (24, 72 + dy), (34, 68 + dy)])
            pygame.draw.polygon(tela, (31, 161, 80), [(31, 62 + dy), (25, 67 + dy), (19, 69 + dy), (33, 67 + dy)])
            pygame.draw.polygon(tela, (250, 216, 75), [(20, 64 + dy), (25, 61 + dy), (25, 65 + dy)])
        elif nome in ('ROXO', 'COSMICA', 'DOURADO', 'PLATINA', 'ROSA'):
            capes = {'ROXO': (113, 63, 174), 'COSMICA': (83, 35, 174),
                     'DOURADO': (217, 38, 77), 'PLATINA': (21, 158, 245), 'ROSA': (249, 103, 171)}
            col = capes[nome]
            pygame.draw.polygon(tela, contorno, [(32, 54 + dy), (30, 64 + dy), (15, 70 + dy), (33, 68 + dy), (39, 58 + dy)])
            pygame.draw.polygon(tela, col, [(31, 56 + dy), (31, 63 + dy), (17, 68 + dy), (34, 65 + dy), (38, 57 + dy)])
        elif nome == 'AZUL':
            pygame.draw.line(tela, (54, 199, 246), (21, 64 + dy), (34, 63 + dy), 3)
            pygame.draw.line(tela, (120, 229, 255), (15, 68 + dy), (27, 68 + dy), 2)

    def fogo_animado(tela, fase_idx, dy=0):
        if nome != 'CHAMA':
            return
        alturas = (8, 11, 14, 10, 13, 9, 12, 10)
        h1 = alturas[fase_idx % len(alturas)]
        h2 = alturas[(fase_idx + 3) % len(alturas)]
        base_y = 25 + dy
        pygame.draw.polygon(tela, (255, 123, 35), [(18, base_y + 11), (15, base_y + 2), (20, base_y - h1), (25, base_y + 1), (22, base_y + 12)])
        pygame.draw.polygon(tela, (255, 210, 74), [(19, base_y + 9), (18, base_y + 3), (20, base_y - max(4, h1 - 5)), (22, base_y + 4), (21, base_y + 10)])
        pygame.draw.polygon(tela, (255, 123, 35), [(58, base_y + 10), (55, base_y + 1), (60, base_y - h2), (65, base_y + 2), (61, base_y + 11)])
        pygame.draw.polygon(tela, (255, 210, 74), [(59, base_y + 8), (58, base_y + 2), (60, base_y - max(4, h2 - 5)), (62, base_y + 3), (61, base_y + 9)])
        h_top = alturas[(fase_idx + 5) % len(alturas)]
        pygame.draw.polygon(tela, (255, 96, 28), [(34, 9 + dy), (37, 1 + dy), (41, 8 - h_top // 2 + dy), (46, 3 + dy), (47, 13 + dy)])
        pygame.draw.polygon(tela, (255, 214, 92), [(37, 10 + dy), (39, 4 + dy), (41, 8 - h_top // 3 + dy), (43, 6 + dy), (43, 12 + dy)])


    def ornamento_premium(tela, acao, fase, y_shift=0):
        # efeitos pequenos e leves; apenas visuais
        if nome == 'CHAMA':
            for dx, dy, col in ((-12, 10, (255, 188, 72)), (12, 9, (255, 137, 49)), (0, 4, (255, 217, 108))):
                px = xc + dx + ((fase % 2) if dx >= 0 else -(fase % 2))
                py = 41 + dy + y_shift - (fase % 3)
                pygame.draw.circle(tela, col, (px, py), 2)
                pygame.draw.circle(tela, (95, 42, 23), (px, py), 2, 1)
        elif nome == 'COSMICA':
            ang = fase * 0.8 + (0.3 if acao in ('CORRER','SUBINDO') else 0.0)
            sx = int(xc + math.cos(ang) * 15)
            sy = int(21 + y_shift + math.sin(ang) * 5)
            estrela = [(sx, sy-4), (sx+2, sy-1), (sx+5, sy), (sx+2, sy+1), (sx, sy+4), (sx-2, sy+1), (sx-5, sy), (sx-2, sy-1)]
            pygame.draw.polygon(tela, (255, 244, 125), estrela)
            pygame.draw.polygon(tela, (93, 54, 165), estrela, 1)
            for dx,dy in ((-12,-2),(-6,4),(8,-3)):
                pygame.draw.circle(tela, (191, 154, 255), (sx+dx//2, sy+dy//2), 1)
        elif nome == 'PLATINA':
            # brilho de visor/capacete
            pygame.draw.line(tela, (226, 252, 255), (xc-6, 18+y_shift), (xc+7, 15+y_shift), 2)
            pygame.draw.line(tela, (104, 232, 255), (xc-4, 20+y_shift), (xc+5, 17+y_shift), 1)
            for sx,sy in ((xc-14, 24+y_shift),(xc+15, 20+y_shift)):
                pygame.draw.line(tela, (240, 252, 255), (sx-2, sy), (sx+2, sy), 1)
                pygame.draw.line(tela, (240, 252, 255), (sx, sy-2), (sx, sy+2), 1)


    def acabamento_gameplay_skin(tela, acao, fase):
        """Detalhes pequenos sobre as poses já articuladas. Sem mudar hitbox/escala."""
        deslocamento = 9 if acao == 'AGACHAR' else (3 if acao == 'SWIPE_DOWN' else 0)
        # Trama frontal da roupa (base em dois tons e pontos de conexão no tronco).
        if acao not in ('MORRER', 'SWIPE_DOWN'):
            pygame.draw.line(tela, detalhe, (xc-7, 55+deslocamento),
                             (xc+7, 55+deslocamento), 1)
            pygame.draw.rect(tela, luva, (xc-10, 57+deslocamento, 2, 2))
            pygame.draw.rect(tela, luva, (xc+8, 57+deslocamento, 2, 2))
        if nome == 'CHAMA':
            # Chamas já existentes permanecem: aqui apenas brasas secundárias.
            for j, (bx, by) in enumerate(((xc-14,34),(xc+13,32),(xc-11,17))):
                py = by - ((fase+j*2) % 5)
                pygame.draw.rect(tela, (255,112,37), (bx, py, 2, 3))
                pygame.draw.rect(tela, (255,220,99), (bx, py, 1, 1))
        elif nome == 'COSMICA':
            # Reflexos do traje na mesma escala de pixels da skin original.
            for k,(bx,by) in enumerate(((xc-8,59+deslocamento),(xc+7,62+deslocamento))):
                pygame.draw.line(tela, (224,207,255), (bx,by), (bx+2,by-2), 1)
                if (fase+k)%2 == 0:
                    pygame.draw.rect(tela, (255,255,255), (bx+1,by-3,2,1))
        elif nome == 'PLATINA':
            # Rebites e reflexos metálicos, sem recriar capacete ou rosto.
            for px in (xc-8,xc+8):
                pygame.draw.rect(tela, (74,151,191), (px,57+deslocamento,3,3))
                pygame.draw.rect(tela, (235,254,255), (px,57+deslocamento,2,1))
            if acao in ('CORRER','OCIOSO','SUBINDO'):
                hx = xc+11 + (fase%3)
                pygame.draw.line(tela, (240,253,255), (hx,23), (hx+3,23), 1)

    def desenhar_pose(acao, fase):
        s = pygame.Surface((80, 80), pygame.SRCALPHA)
        if acao == 'CORRER':
            angulo = 2 * math.pi * fase / 10
            passo = math.sin(angulo)
            passo_oposto = -passo
            lev_e = max(0, math.cos(angulo)) * 7
            lev_d = max(0, -math.cos(angulo)) * 7
            flexao = 1 if fase in (1, 2, 6, 7) else 0
            cauda(s, int(2 * math.sin(angulo + 0.8)))
            perna(s, xc - 6, round(34 + passo * 8), round(75 - lev_e), lev_e > 1)
            perna(s, xc + 6, round(49 + passo_oposto * 8), round(75 - lev_d), lev_d > 1)
            braco(s, 'esq', round(26 - passo * 5), round(58 + passo * 3))
            torso(s, flexao)
            braco(s, 'dir', round(57 + passo * 5), round(57 - passo * 3))
            if nome == 'CHAMA':
                fogo_animado(s, fase, -1)
            s.blit(cabeca, (dx_cabeca, -3 + flexao + ajuste_cabeca_y))
        elif acao == 'IMPULSO':
            agachar = (6, 4, 0)[fase]
            cauda(s, agachar // 2)
            perna(s, xc - 6, (30, 30, 33)[fase], (76, 72, 69)[fase], True, 63 + agachar, 69 + agachar)
            perna(s, xc + 6, (52, 52, 50)[fase], (76, 72, 69)[fase], True, 63 + agachar, 69 + agachar)
            torso(s, agachar)
            braco(s, 'esq', 23, (62, 49, 39)[fase], 54 + agachar)
            braco(s, 'dir', 61, (61, 49, 39)[fase], 54 + agachar)
            fogo_animado(s, fase, agachar - 2)
            s.blit(cabeca, (dx_cabeca, -3 + agachar + ajuste_cabeca_y))
        elif acao == 'SUBINDO':
            cauda(s, -2 - fase)
            perna(s, xc - 6, 31 - fase, 71 - fase, True, 62, 66 - fase)
            perna(s, xc + 6, 51 + fase, 70 - fase, True, 62, 65 - fase)
            braco(s, 'esq', 24 - fase, 44 - fase * 2)
            torso(s, -2)
            braco(s, 'dir', 61 + fase, 41 - fase * 2)
            fogo_animado(s, fase, -1)
            s.blit(cabeca, (dx_cabeca, -5 + ajuste_cabeca_y))
        elif acao == 'PULAR':
            cauda(s, -4)
            perna(s, xc - 6, 31, 65, True, 61, 63)
            perna(s, xc + 6, 53, 65, True, 61, 63)
            braco(s, 'esq', 22, 39)
            torso(s, -3)
            braco(s, 'dir', 62, 39)
            fogo_animado(s, fase + 2, -2)
            s.blit(cabeca, (dx_cabeca, -6 + ajuste_cabeca_y))
        elif acao == 'CAINDO':
            cauda(s, 1 + fase)
            perna(s, xc - 6, 30 - fase, 67 + fase * 3, fase < 1, 62 + fase, 66 + fase)
            perna(s, xc + 6, 52 + fase, 67 + fase * 3, fase < 1, 62 + fase, 66 + fase)
            braco(s, 'esq', 20 - fase, 45 + fase * 3)
            torso(s, 1 + fase // 2)
            braco(s, 'dir', 62 + fase, 46 + fase * 3)
            fogo_animado(s, fase + 4, 0)
            s.blit(cabeca, (dx_cabeca, -2 + fase // 2 + ajuste_cabeca_y))
        elif acao == 'SWIPE_DOWN':
            cauda(s, 2 + fase)
            perna(s, xc - 6, 19 + fase * 2, 68 + (fase & 1), True)
            perna(s, xc + 6, 27 + fase * 2, 74 - (fase & 1), True)
            torso(s, 3)
            braco(s, 'esq', 62, 51 + fase)
            braco(s, 'dir', 65, 61 + fase)
            fogo_animado(s, fase + 1, 3)
            s.blit(cabeca, (dx_cabeca + 3, 2 + ajuste_cabeca_y))
            inclinacao = (-12, -18, -23, -27)[fase]
            giro = pygame.transform.rotate(s, inclinacao)
            s = pygame.Surface((80, 80), pygame.SRCALPHA)
            s.blit(giro, ((80 - giro.get_width()) // 2, (80 - giro.get_height()) // 2))
            for z in range(2):
                y = 28 + 10 * z + (fase % 2) * 3
                pygame.draw.line(s, (125, 218, 255), (3, y), (13, y), 2)
        elif acao == 'AGACHAR':
            angulo = 2 * math.pi * fase / 6
            passo = math.sin(angulo) * 9
            lev_e = max(0, math.cos(angulo)) * 5
            lev_d = max(0, -math.cos(angulo)) * 5
            bob = 1 if fase in (1, 4) else 0
            cauda(s, 5 + bob)
            perna(s, xc - 7, int(28 + passo), int(77 - lev_e), True, 71 + bob, 75)
            perna(s, xc + 7, int(52 - passo), int(77 - lev_d), True, 71 + bob, 75)
            torso(s, 9 + bob)
            braco(s, 'esq', int(21 - passo / 3), 69 + bob, 63 + bob)
            braco(s, 'dir', int(61 + passo / 3), 69 + bob, 63 + bob)
            fogo_animado(s, fase + 2, 7)
            s.blit(cabeca, (dx_cabeca, 7 + bob + ajuste_cabeca_y))
        elif acao == 'OCIOSO':
            respirar = (0, 0, 1, 1, 2, 1, 1, 0)[fase]
            gesto = (-1, 0, 1, 2, 1, 0, -1, -2)[fase]
            cauda(s, gesto)
            perna(s, xc - 6, 33, 76, False)
            perna(s, xc + 6, 49, 76, False)
            braco(s, 'esq', 24 - gesto, 57 + respirar)
            torso(s, respirar)
            braco(s, 'dir', 59 + gesto, 55 - (fase & 1))
            fogo_animado(s, fase, -1 + respirar)
            s.blit(cabeca, (dx_cabeca, -3 + respirar + ajuste_cabeca_y))
        else:
            cauda(s, 3)
            perna(s, xc - 6, 28 - fase, 72 - min(fase, 3), True)
            perna(s, xc + 6, 54 + fase, 73 - min(fase, 3), True)
            torso(s, min(fase, 4))
            braco(s, 'esq', 19 + fase, 50 - min(fase, 4))
            braco(s, 'dir', 65 - fase, 47 - min(fase, 4))
            fogo_animado(s, fase + 3, min(fase, 4) - 2)
            s.blit(cabeca, (dx_cabeca, min(fase, 4) - 3 + ajuste_cabeca_y))
            if fase > 0:
                giro = pygame.transform.rotate(s, (0, -9, -16, -23, -35, -46)[fase])
                if fase >= 4:
                    giro = pygame.transform.scale(giro,
                        (max(1, int(giro.get_width() * (1 - 0.09 * (fase - 3)))),
                         max(1, int(giro.get_height() * (1 - 0.13 * (fase - 3))))))
                sf = pygame.Surface((80, 80), pygame.SRCALPHA)
                sf.blit(giro, ((80 - giro.get_width()) // 2,
                               (80 - giro.get_height()) // 2 + 3 * (fase >= 3)))
                s = sf
            if fase >= 3:
                pygame.draw.circle(s, detalhe, (17 + fase, 16), 2)
                pygame.draw.line(s, detalhe, (59, 16), (65, 20), 2)
        temas = {
            'AZUL': ((99, 220, 255), 2),
            'ROSA': ((255, 176, 239), 2),
            'DOURADO': ((255, 236, 92), 3),
            'ROXO': ((183, 105, 255), 3),
            'ROBO': ((92, 238, 255), 2),
            'CHAMA': ((255, 197, 56), 4),
            'COSMICA': ((254, 229, 119), 4),
            'PLATINA': ((109, 232, 255), 2),
        }
        if nome in temas:
            cor, total = temas[nome]
            for i in range(total):
                f = (fase * 3 + i * 7 + len(acao))
                x = (15 + f * 11) % 64 + 7
                y = (5 + f * 7) % 43 + 4
                tamanho = 1 + ((fase + i) % 3 == 0)
                pygame.draw.rect(s, cor, (x, y, tamanho + 1, tamanho + 1))
                if nome in ('CHAMA', 'COSMICA', 'ROXO', 'DOURADO') and (i + fase) % 2 == 0:
                    pygame.draw.line(s, cor, (x - 2, y + 1), (x + 3, y + 1), 1)
        # Acabamento comum em 2 tons: mesmo tamanho de pixel em todas as skins.
        luz = PALETAS_SPRITES_PREMIUM[
            'quente' if nome in ('CHAMA', 'DOURADO') else
            'natureza' if nome == 'VERDE' else
            'magico' if nome in ('ROXO', 'COSMICA', 'ROSA') else 'frio'
        ][1]
        if acao not in ('MORRER', 'SWIPE_DOWN'):
            pygame.draw.rect(s, luz, (xc + 5, 53 + (2 if acao == 'AGACHAR' else 0), 3, 2))
        ornamento_premium(s, acao, fase, 2 if acao == 'AGACHAR' else 0)
        acabamento_gameplay_skin(s, acao, fase)
        return s

    formatos = {
        'CORRER': 10, 'IMPULSO': 3, 'SUBINDO': 4,
        'PULAR': 3, 'CAINDO': 4, 'SWIPE_DOWN': 4,
        'AGACHAR': 6, 'OCIOSO': 8, 'MORRER': 6,
    }
    quadros = {acao: tuple(desenhar_pose(acao, i) for i in range(qtd))
               for acao, qtd in formatos.items()}
    pousos = []
    for fase in range(3):
        # Pernas quietas na aterrissagem; a corrida recomeça só depois.
        original = desenhar_pose('CORRER', 0)
        altura = (72, 76, 80)[fase]
        mini = pygame.transform.scale(original, (80, altura))
        tela = pygame.Surface((80, 80), pygame.SRCALPHA)
        tela.blit(mini, (0, 80 - altura))
        pousos.append(tela)
    quadros['POUSO'] = tuple(pousos)
    return quadros


def _quadros_skin(nome):
    atual = _SKIN_FRAMES.get(nome)
    if atual is None:
        atual = _criar_quadros_skin(nome)
        _SKIN_FRAMES[nome] = atual
    return atual


def _estado_skin_jogador(jogador, frame_contador):
    if jogador.morrendo:
        tempo_total = 70 if jogador.morte_por_buraco else 60
        return 'MORRER', min(5, max(0, tempo_total - jogador.tempo_morte) // 10)
    if jogador.descida_rapida and not jogador.no_chao:
        return 'SWIPE_DOWN', (frame_contador // 3) % 4
    if jogador.jetpack_fase is not None:
        if jogador.jetpack_fase == 'subindo':
            return 'SUBINDO', min(3, max(0, int((jogador.jetpack_subida_duracao - jogador.jetpack_transicao_timer) / 12)))
        if jogador.jetpack_fase == 'descendo':
            return 'CAINDO', min(3, max(0, int((jogador.jetpack_descida_duracao - jogador.jetpack_transicao_timer) / 12)))
        return 'PULAR', 1
    if not jogador.no_chao:
        duracao = getattr(jogador, 'anim_pulo_frames', 0)
        vy = float(getattr(jogador, 'velocidade_y', 0.0))
        if duracao <= 4 and vy < -6.0:
            return 'IMPULSO', min(2, duracao // 2)
        if vy < -2.4:
            return 'SUBINDO', min(3, max(0, int(abs(vy + 2.4) * 0.45)))
        if vy <= 2.0:
            return 'PULAR', 1
        return 'CAINDO', min(3, max(0, int((vy - 2.0) * 0.35)))
    if jogador.agachado:
        return 'AGACHAR', (frame_contador // 2) % 6
    if getattr(jogador, 'anim_pouso_ticks', 0) > 0:
        return 'POUSO', min(2, max(0, 3 - jogador.anim_pouso_ticks))
    return 'CORRER', (frame_contador // 2) % 10


from functools import lru_cache as _qa_lru_skins_enquadradas


@_qa_lru_skins_enquadradas(maxsize=96)
def _sprite_skin_enquadrado(nome, estado, indice, largura, altura, margem=0):
    """Enquadra a silhueta visível inteira sem cortar cabeça, capa ou pés."""
    origem = _quadros_skin(nome)[estado][indice]
    visivel = origem.get_bounding_rect(min_alpha=12)
    if not visivel.width or not visivel.height:
        return pygame.Surface((largura, altura), pygame.SRCALPHA)
    # Reduz margem externa, sem distorção; pixels permanecem nítidos.
    recorte = origem.subsurface(visivel)
    limite_w = max(1, largura - 2 * margem)
    limite_h = max(1, altura - 2 * margem)
    escala = min(limite_w / visivel.width, limite_h / visivel.height)
    tam = (max(1, round(visivel.width * escala)), max(1, round(visivel.height * escala)))
    sprite = pygame.transform.scale(recorte, tam)
    tela = pygame.Surface((largura, altura), pygame.SRCALPHA)
    tela.blit(sprite, ((largura - tam[0]) // 2, (altura - tam[1]) // 2))
    return tela


def _popup_skin_animado(nome, frame_contador):
    """Personagem na loja respirando e gesticulando, sem cache de quadro único."""
    quadros = _SKIN_POPUP_OCIOSO.get(nome)
    if quadros is None:
        quadros = tuple(_sprite_skin_enquadrado(nome, 'OCIOSO', i, 180, 180, 10)
                       for i in range(8))
        _SKIN_POPUP_OCIOSO[nome] = quadros
    ritmo = 12 if nome in ('ROSA', 'ROXO', 'CHAMA') else 9
    return quadros[(frame_contador // ritmo) % 8]


# Upgrades
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
             "preco_base": 4200, "preco_multiplicador": 3000},
    "JETPACK": {"nome_key": "up_jetpack", "cor": (255, 135, 35), "duracao_base": 480, "bonus_por_nivel": 120,
                "max_nivel": 4, "preco_base": 5250, "preco_multiplicador": 3750},
    "CLONE": {"nome_key": "up_clone", "cor": (115, 225, 255), "clones_base": 3, "bonus_por_nivel": 1,
              "max_nivel": 5, "preco_base": 4800, "preco_multiplicador": 3200},
}

# Seis vezes os custos-base e incrementais, preservada a progressão por nível.
for _config_prod in UPGRADES_CONFIG.values():
    _config_prod['preco_base'] = int(_config_prod['preco_base'] * 6)
    _config_prod['preco_multiplicador'] = int(_config_prod['preco_multiplicador'] * 6)

def powerup_desbloqueado(dados_jogo, tipo):
    """Só deixa um power-up surgir/ser coletado após compra do nível 1."""
    if tipo not in UPGRADES_CONFIG or not isinstance(dados_jogo, dict):
        return False
    try:
        return int(dados_jogo.get("upgrades", {}).get(tipo, 0)) >= 1
    except (ValueError, TypeError, AttributeError):
        return False


def jogador_invencivel_por_velocidade(jogador, febre_timer=0, febre_metros=0.0):
    """Febre e Turbo protegem contra terreno, buracos, lasers e inimigos."""
    return bool(jogador and not jogador.morrendo and (
        febre_timer > 0 or febre_metros > 0 or
        jogador.tempo_turbo > 0 or jogador.tempo_turbo_fantasma > 0
    ))


def destruir_perigos_no_caminho(jogador, obstaculos, perigos_especiais, vel_jogo=0.0, sdf=False):
    """Remove perigos só ao alcançar o herói, sem esvaziar o cenário distante.

    Não remove moedas, power-ups ou buracos: eles continuam visíveis e os buracos
    são atravessados com o chão protegido pela invencibilidade.
    """
    if jogador is None or jogador.morrendo:
        return ()
    margem = max(12, int(max(0.0, vel_jogo)) + 5)
    inicio = jogador.rect.left - margem
    fim = jogador.rect.right + margem
    destruidos = []
    for obs in tuple(obstaculos):
        if obs.rect.right >= inicio and obs.rect.left <= fim:
            if getattr(obs, '_sdf_atingido_v3109', False):
                continue
            # Recorta a peça estática com SDF. Inimigos animados continuam com
            # sua destruição original porque redesenham a imagem a cada tick.
            pode_recortar = sdf and getattr(obs, 'movimento', 'parado') in ('parado', 'parado_alto')
            if pode_recortar:
                try:
                    resiste = esculpir_obstaculo(obs, jogador.rect.centerx,
                        jogador.rect.centery, raio=max(28, obs.rect.height // 2))
                except (ValueError, ImportError, pygame.error):
                    resiste = False
                if not resiste:
                    obs.kill()
            else:
                obs.kill()
            destruidos.append(obs)
    for laser in tuple(perigos_especiais):
        if getattr(laser, 'ativo', False) and laser.rect.right >= inicio and laser.rect.left <= fim:
            destruidos.append(laser)
            laser.kill()
    return tuple(destruidos)



def calcular_custo_upgrade(chave, nivel_atual):
    """Custo consistente para a loja; jetpack custa 25% acima do upgrade mais caro por nível."""
    nivel_atual = max(0, int(nivel_atual))
    if chave == "JETPACK":
        # Em cada tier, custa exatamente 25% acima do upgrade mais caro ainda
        # disponível nesse mesmo tier entre os demais power-ups.
        custos_disponiveis = [conf["preco_base"] + nivel_atual * conf["preco_multiplicador"]
                              for nome, conf in UPGRADES_CONFIG.items()
                              if nome != "JETPACK" and nivel_atual < conf["max_nivel"]]
        base_mais_cara = max(custos_disponiveis) if custos_disponiveis else 4200
        return int(base_mais_cara * 1.25)
    conf = UPGRADES_CONFIG[chave]
    return conf["preco_base"] + nivel_atual * conf["preco_multiplicador"]


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

# Fontes antigas preservadas para pt_BR/en_US; fontes internacionais sob demanda.
_FONTES_ORIGINAIS_I18N = (fonte, fonte_pequena, fonte_missoes, fonte_grande, fonte_alerta)
_IDIOMA_ATUAL_I18N = "pt_BR"


class _FonteHindiComFallback:
    """Mescla trechos Devanagari e latinos para preservar nomes/números sem fontes enormes."""
    __slots__ = ("deva", "latina")

    def __init__(self, deva, latina):
        self.deva, self.latina = deva, latina

    def _partes(self, texto):
        if not texto:
            return []
        grupos = []
        atual = ""
        indice = None
        for caractere in texto:
            deva = '\u0900' <= caractere <= '\u097f'
            if atual and deva != indice:
                grupos.append((atual, indice))
                atual = ""
            atual += caractere
            indice = deva
        grupos.append((atual, indice))
        return grupos

    def size(self, texto):
        partes = self._partes(str(texto))
        larguras = [ (self.deva if d else self.latina).size(t) for t, d in partes ]
        return (sum(w for w, h in larguras), max((h for w, h in larguras), default=self.latina.get_height()))

    def render(self, texto, antialias, cor):
        import pygame
        partes = [(self.deva if d else self.latina).render(t, antialias, cor)
                  for t, d in self._partes(str(texto))]
        largura = sum(s.get_width() for s in partes)
        altura = max((s.get_height() for s in partes), default=self.latina.get_height())
        superficie = pygame.Surface((max(1, largura), max(1, altura)), pygame.SRCALPHA)
        x = 0
        for segmento in partes:
            superficie.blit(segmento, (x, max(0, (altura-segmento.get_height()) // 2)))
            x += segmento.get_width()
        return superficie

    def get_height(self):
        return max(self.deva.get_height(), self.latina.get_height())

    def get_linesize(self):
        return max(self.deva.get_linesize(), self.latina.get_linesize())


def aplicar_fontes_localizadas(dados):
    """Executado na inicialização e na alteração de idioma, nunca no loop."""
    global _IDIOMA_ATUAL_I18N, fonte, fonte_pequena, fonte_missoes, fonte_grande, fonte_alerta
    from pixelrush_i18n_v3246 import normalizar_idioma
    codigo = normalizar_idioma(dados.get('idioma', 'pt_BR'))
    if codigo == _IDIOMA_ATUAL_I18N:
        return
    _IDIOMA_ATUAL_I18N = codigo
    fontes = _FONTES_ORIGINAIS_I18N
    if codigo in _i18n247.ARQUIVOS_FONTES:
        tamanhos = (20, 13, 15, 30, 24)
        fontes_novas = tuple(_i18n247.fonte_unicode(codigo, tamanho) for tamanho in tamanhos)
        if codigo == 'hi_IN':
            fontes = tuple(_FonteHindiComFallback(deva, latina)
                           for deva, latina in zip(fontes_novas, _FONTES_ORIGINAIS_I18N))
        else:
            fontes = fontes_novas
    fonte, fonte_pequena, fonte_missoes, fonte_grande, fonte_alerta = fontes
    _CACHE_TEXTOS.clear()
    _HUD_TEXTOS_AJUSTADOS.clear()
    _PROXY_FONTES_SECUNDARIAS.clear()


# Camada de apresentação para painéis legados que chamam font.render() diretamente.
# Somente fontes existentes, nenhum objeto criado no loop após cache inicial.
_PROXY_FONTES_SECUNDARIAS = {}

class _FontePainelLocalizado:
    __slots__ = ('original', 'idioma')

    def __init__(self, original, idioma):
        self.original = original
        self.idioma = idioma

    def _traduzir(self, texto):
        return _i18n247.localizar_literal(str(texto), self.idioma)

    def size(self, texto):
        return self.original.size(self._traduzir(texto))

    def render(self, texto, antialias, cor, *args, **kwargs):
        txt = self._traduzir(texto)
        imagem = self.original.render(txt, antialias, cor, *args, **kwargs)
        # Evita cortes nos painéis de 450px sem recriar fontes.
        if imagem.get_width() > 402:
            import pygame
            imagem = pygame.transform.smoothscale(imagem, (402, imagem.get_height()))
        return imagem

    def __getattr__(self, nome):
        return getattr(self.original, nome)


def _fonte_painel_localizado(original):
    if _IDIOMA_ATUAL_I18N in ('pt_BR', 'en_US'):
        return original
    chave = (_IDIOMA_ATUAL_I18N, id(original))
    fonte_tela = _PROXY_FONTES_SECUNDARIAS.get(chave)
    if fonte_tela is None:
        fonte_tela = _FontePainelLocalizado(original, _IDIOMA_ATUAL_I18N)
        _PROXY_FONTES_SECUNDARIAS[chave] = fonte_tela
    return fonte_tela

# --- CACHE LIMITADO DE TEXTO (MUITO IMPORTANTE PARA ANDROID) ---
# Font.render() e alocacoes repetidas sao caras em varios builds do Pygame/SDL.
# Cacheamos a superficie pelo texto, fonte e cor; as superficies nunca sao alteradas.
_CACHE_TEXTOS = OrderedDict()
_LIMITE_CACHE_TEXTOS = 1536


def render_texto_cacheado(fonte_obj, texto, cor):
    texto = str(texto)
    if _IDIOMA_ATUAL_I18N not in ('pt_BR', 'en_US'):
        texto = _i18n247.localizar_literal(texto, _IDIOMA_ATUAL_I18N)
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
    if _IDIOMA_ATUAL_I18N not in ('pt_BR', 'en_US'):
        texto = _i18n247.localizar_literal(str(texto), _IDIOMA_ATUAL_I18N)
        texto = texto_ajustado_hud(texto, fonte_obj, LARGURA_VIRTUAL - 18)
    surf_sombra = render_texto_cacheado(fonte_obj, texto, cor_sombra)
    surf_texto = render_texto_cacheado(fonte_obj, texto, cor_texto)
    x_pos = (LARGURA_VIRTUAL - surf_texto.get_width()) // 2
    surface.blit(surf_sombra, (x_pos + 2, y_pos + 2))
    surface.blit(surf_texto, (x_pos, y_pos))


from functools import lru_cache as _qa_lru_cache_rotulos


@_qa_lru_cache_rotulos(maxsize=64)
def _qa_cache_escala_rotulo(fonte_surface, tamanho):
    """QA 3.277.32: escala idêntica para texto estático em botões."""
    return pygame.transform.smoothscale(fonte_surface, tamanho)


def desenhar_rotulo_botao(superficie, texto, fonte_obj, cor_texto, cor_sombra, rect):
    """Desenha um rótulo centralizado horizontal e verticalmente dentro de um botão."""
    if _IDIOMA_ATUAL_I18N not in ('pt_BR', 'en_US'):
        texto = _i18n247.localizar_literal(str(texto), _IDIOMA_ATUAL_I18N)
    largura = max(1, rect.width - 14)
    altura = max(1, rect.height - 8)
    # Os 13 idiomas usam a mesma medição e seleção de fonte, inclusive PT/EN.
    if fonte_obj.size(texto)[0] > largura or fonte_obj.get_height() > altura:
        for candidata in (fonte_missoes, fonte_pequena):
            if candidata.size(texto)[0] <= largura and candidata.get_height() <= altura:
                fonte_obj = candidata
                break
        else:
            # Diminuir somente o rótulo desenhado: botões e áreas clicáveis
            # mantêm as dimensões originais, sem truncar traduções longas.
            melhor = min((fonte_obj, fonte_missoes, fonte_pequena),
                         key=lambda ft: ft.size(texto)[0])
            fonte_obj = melhor
    surf_sombra = render_texto_cacheado(fonte_obj, texto, cor_sombra)
    surf_texto = render_texto_cacheado(fonte_obj, texto, cor_texto)
    if surf_texto.get_width() > largura or surf_texto.get_height() > altura:
        fator = min(largura / max(1, surf_texto.get_width()),
                    altura / max(1, surf_texto.get_height()))
        tamanho = (max(1, int(surf_texto.get_width() * fator)),
                   max(1, int(surf_texto.get_height() * fator)))
        surf_texto = _qa_cache_escala_rotulo(surf_texto, tamanho)
        surf_sombra = _qa_cache_escala_rotulo(surf_sombra, tamanho)
    x = rect.centerx - surf_texto.get_width() // 2
    y = rect.centery - surf_texto.get_height() // 2
    superficie.blit(surf_sombra, (x + 1, y + 1))
    superficie.blit(surf_texto, (x, y))


def desenhar_texto_com_sombra(superficie, texto, fonte_obj, cor_texto, cor_sombra, pos):
    if _IDIOMA_ATUAL_I18N not in ('pt_BR', 'en_US'):
        texto = _i18n247.localizar_literal(str(texto), _IDIOMA_ATUAL_I18N)
        if pos[0] >= 0 and superficie.get_width() - pos[0] > 22:
            texto = texto_ajustado_hud(texto, fonte_obj, superficie.get_width() - pos[0] - 8)
    surf_sombra = render_texto_cacheado(fonte_obj, texto, cor_sombra)
    surf_texto = render_texto_cacheado(fonte_obj, texto, cor_texto)
    superficie.blit(surf_sombra, (pos[0] + 2, pos[1] + 2))
    superficie.blit(surf_texto, pos)


class MonitorQualidadeVisual:
    """Histerese evita flicker ao alternar detalhes, sem mudar o passo fixo."""
    def __init__(self):
        self.reduzido = False
        self.fps_suavizado = 30.0 if E_ANDROID else 60.0
        self.tempo_baixo = 0.0
        self.tempo_recuperacao = 0.0

    def atualizar(self, fps, dt, modo, jogando):
        if modo != 'auto':
            self.reduzido = False
            self.tempo_baixo = self.tempo_recuperacao = 0.0
            return
        if not jogando or fps < 1:
            self.tempo_baixo = self.tempo_recuperacao = 0.0
            return
        dt = max(0.0, min(0.12, float(dt)))
        self.fps_suavizado += (fps - self.fps_suavizado) * min(1.0, dt * 3.0)
        fps = self.fps_suavizado
        # Proporcao identica dos limiares 49/55 FPS de desktop,
        # mas sobre alvo de apresentacao 30 FPS no Android.
        alvo_fps = 30.0 if E_ANDROID else 60.0
        if fps < alvo_fps * (49.0 / 60.0):
            self.tempo_baixo += dt
            self.tempo_recuperacao = 0.0
        elif fps > alvo_fps * (55.0 / 60.0):
            self.tempo_recuperacao += dt
            self.tempo_baixo = 0.0
        else:
            self.tempo_baixo = max(0.0, self.tempo_baixo - dt * 0.25)
            self.tempo_recuperacao = max(0.0, self.tempo_recuperacao - dt * 0.5)
        if not self.reduzido and self.tempo_baixo >= 2.0:
            self.reduzido = True
            self.tempo_baixo = 0.0
        elif self.reduzido and self.tempo_recuperacao >= 12.0:
            self.reduzido = False
            self.tempo_recuperacao = 0.0


MONITOR_QUALIDADE_VISUAL = MonitorQualidadeVisual()
PARTICULAS_VISUAIS_LIMITADAS = False


def modo_grafico_leve(dados):
    """Perfil grafico unico COMPLETO, inclusive em saves migrados."""
    return False


# Raridades usadas apenas na apresentação, sem alterar chances/preços.
RARIDADE_CORES = {
    'Comum': (115, 201, 233), 'Raro': (78, 151, 255),
    'Épico': (194, 112, 255), 'Lendário': (255, 200, 91),
}
RASTROS_COSMETICOS = ('DESLIGADO', 'NEON', 'FOGO', 'GELO', 'ESTRELAS', 'ENERGIA')
SUBTITULOS_BIOMAS = {
    'cidade': 'NOVOS CAMINHOS, NOVAS AVENTURAS',
    'deserto': 'AS DUNAS GUARDAM SEGREDOS',
    'neve': 'UM MUNDO DE GELO E BRILHO',
    'vulcao': 'CORAGEM ENTRE CHAMAS',
    'cidade_futurista': 'O FUTURO É VELOCIDADE',
    'floresta': 'A FLORESTA ESTÁ VIVA',
        'ilhas_celestes': 'UMA AVENTURA NAS NUVENS',
}
SUBTITULOS_BIOMAS_EN = {
    'cidade': 'NEW STREETS, NEW ADVENTURES',
    'deserto': 'SECRETS AMONG THE DUNES',
    'neve': 'A WORLD OF ICE AND SPARKLE',
    'vulcao': 'COURAGE THROUGH THE FLAMES',
    'cidade_futurista': 'THE FUTURE IS FAST',
    'floresta': 'THE FOREST IS ALIVE',
        'ilhas_celestes': 'AN ADVENTURE ABOVE THE CLOUDS',
}
COR_BIOMAS_UI = {
    'cidade': (102, 213, 253), 'deserto': (255, 206, 109),
    'neve': (183, 235, 255), 'vulcao': (255, 123, 76),
    'cidade_futurista': (104, 248, 243), 'floresta': (113, 233, 132),
    'reino_submerso': (80, 224, 255), 'ilhas_celestes': (221, 208, 255),
}


# Paleta de interface consistente: sem transparências temporárias ou shaders.
UI_FUNDO = (20, 29, 49)
UI_TOPO = (37, 53, 78)
UI_CONTORNO = (91, 130, 162)
UI_BRANCO = (241, 250, 255)
UI_MUTED = (174, 208, 227)
UI_CIANO = (99, 225, 247)


def desenhar_painel_identidade(surface, rect, destaque=UI_CIANO, cabecalho=False, discreto=False):
    """Painel comum à interface; custo O(1), desenhos diretos na Surface-alvo."""
    r = pygame.Rect(rect)
    raio = 9 if r.height <= 60 else 12
    pygame.draw.rect(surface, (12, 18, 30), r.move(0, 3), border_radius=raio)
    pygame.draw.rect(surface, UI_FUNDO, r, border_radius=raio)
    alto = min(14, max(6, r.height // 4))
    pygame.draw.rect(surface, UI_TOPO, (r.x + 2, r.y + 2, r.width - 4, alto),
                     border_top_left_radius=max(4,raio-2), border_top_right_radius=max(4,raio-2))
    pygame.draw.rect(surface, destaque if not discreto else UI_CONTORNO, r, 2 if not discreto else 1, border_radius=raio)
    if cabecalho and r.width > 80:
        pygame.draw.line(surface, misturar_cores(destaque, UI_BRANCO, 0.40),
                         (r.x + 14, r.y + alto + 3), (r.right - 14, r.y + alto + 3), 1)
    if r.width > 45 and r.height > 32:
        # Cantos pixelados: assinatura visual repetida em todas as telas.
        pygame.draw.rect(surface, destaque, (r.x + 9, r.bottom - 7, 4, 2))
        pygame.draw.rect(surface, destaque, (r.right - 13, r.bottom - 7, 4, 2))


_HUD_TEXTOS_AJUSTADOS = OrderedDict()


def texto_ajustado_hud(texto, fonte_obj, largura_max):
    """Evita invadir os painéis vizinhos; cache limitado para não crescer em corridas longas."""
    chave = (texto, id(fonte_obj), int(largura_max))
    resultado = _HUD_TEXTOS_AJUSTADOS.get(chave)
    if resultado is not None:
        return resultado
    if fonte_obj.size(texto)[0] <= largura_max:
        resultado = texto
    else:
        # Busca binária no comprimento, barata, sem renderizar Surface temporária.
        baixo, alto = 0, len(texto)
        while baixo < alto:
            meio = (baixo + alto + 1) // 2
            if fonte_obj.size(texto[:meio] + '…')[0] <= largura_max:
                baixo = meio
            else:
                alto = meio - 1
        resultado = texto[:baixo].rstrip() + '…' if baixo else '…'
    if len(_HUD_TEXTOS_AJUSTADOS) >= 128:
        _HUD_TEXTOS_AJUSTADOS.popitem(last=False)
    _HUD_TEXTOS_AJUSTADOS[chave] = resultado
    return resultado


def raridade_de_skin(ident):
    if ident in ('COSMICA', 'PLATINA', 'CHAMA'):
        return 'Lendário'
    if ident in ('ROXO', 'ROBO', 'DOURADO'):
        return 'Épico'
    return 'Raro' if ident in ('VERDE', 'ROSA') else 'Comum'


def desenhar_moldura_raridade(superficie, rect, raridade, frame, destaque=False, leve=False):
    cor = RARIDADE_CORES.get(raridade, RARIDADE_CORES['Comum'])
    esp = 3 if raridade == 'Lendário' and destaque else 2
    pygame.draw.rect(superficie, cor, rect, esp, border_radius=12)
    recuo = 10 if rect.width >= 120 else 5
    pygame.draw.line(superficie, misturar_cores(cor, BRANCO, 0.35),
                     (rect.left + recuo, rect.top + 4), (rect.left + min(rect.width - recuo, 60), rect.top + 4), 1)
    if not leve and (destaque or raridade in ('Épico', 'Lendário')):
        quantidade = 7 if destaque else 3
        for i in range(quantidade):
            fx = rect.left + 9 + ((frame // (8 + i % 3) + i * 31) % max(12, rect.width - 18))
            fy = rect.top + 7 if i % 2 else rect.bottom - 8
            if (frame // 12 + i) % 3 != 0:
                continue
            pygame.draw.line(superficie, cor, (fx - 2, fy), (fx + 2, fy), 1)
            pygame.draw.line(superficie, cor, (fx, fy - 2), (fx, fy + 2), 1)


def desenhar_rastro_cosmetico(superficie, x, y, estilo, frame, leve=False, quantidade=None):
    if estilo == 'DESLIGADO':
        return
    paletas = {
        'NEON': ((78, 244, 255), (205, 92, 255)),
        'FOGO': ((255, 99, 45), (255, 214, 100)),
        'GELO': ((200, 246, 255), (96, 182, 247)),
        'ESTRELAS': ((255, 235, 133), (254, 183, 244)),
        'ENERGIA': ((94, 255, 187), (63, 176, 255)),
    }
    cores = paletas.get(estilo, paletas['ESTRELAS'])
    total = quantidade if quantidade is not None else (3 if leve else 7)
    for i in range(total):
        px = int(x - 7 - i * 7 + math.sin(frame * .08 + i * 1.7) * 2)
        py = int(y + math.sin(frame * .17 + i * 1.4) * (3 + i))
        if px < 2 or py < 3 or px >= LARGURA_VIRTUAL - 2 or py >= ALTURA_VIRTUAL - 2:
            continue
        cor = cores[(i + frame // 15) % 2]
        lado = 3 if i % 3 == 0 else 2
        if estilo == 'ESTRELAS':
            pygame.draw.line(superficie, cor, (px - 2, py), (px + 2, py), 1)
            pygame.draw.line(superficie, cor, (px, py - 2), (px, py + 2), 1)
        elif estilo == 'FOGO':
            pygame.draw.polygon(superficie, cor, [(px - 2, py + 2), (px, py - 4), (px + lado, py + 2)])
        elif estilo == 'GELO':
            pygame.draw.rect(superficie, cor, (px, py, lado + 1, lado + 1))
            if i % 2 == 0:
                pygame.draw.line(superficie, cores[0], (px + 1, py - 2), (px + 1, py + 4), 1)
        elif estilo == 'ENERGIA':
            pygame.draw.lines(superficie, cor, False,
                              ((px - 4, py - 2), (px, py + 1), (px + 3, py - 3)), 1)
        else:
            pygame.draw.rect(superficie, cor, (px, py, lado + 3, 2))


def desenhar_selo_maestria(superficie, dados, cx, cy, frame):
    # Distintivo de biomas: não é evolução de skin nem concede qualquer bônus.
    niveis = dados.get('maestria_biomas', {})
    qtd = 0
    for item in niveis.values():
        try:
            nivel = int(item.get('nivel', 0) if isinstance(item, dict) else item or 0)
        except (ValueError, TypeError):
            nivel = 0
        qtd += int(nivel >= 3)
    if qtd == 0:
        return
    cor = (255, 204, 93) if qtd >= 3 else (119, 228, 255)
    raio = 13 + (int((math.sin(frame * .07) + 1) * 1) if qtd >= 3 else 0)
    pygame.draw.circle(superficie, (20, 29, 49), (cx, cy), raio + 3)
    pygame.draw.circle(superficie, cor, (cx, cy), raio, 2)
    pygame.draw.polygon(superficie, cor,
                        [(cx, cy - 8), (cx + 3, cy - 2), (cx + 9, cy - 2),
                         (cx + 4, cy + 2), (cx + 5, cy + 8), (cx, cy + 5),
                         (cx - 5, cy + 8), (cx - 4, cy + 2),
                         (cx - 9, cy - 2), (cx - 3, cy - 2)])
    if qtd >= 3:
        pygame.draw.circle(superficie, BRANCO, (cx - 2, cy - 3), 2)


def desenhar_faixa_bioma_premium(superficie, bioma, titulo, progresso, frame, leve=False, idioma='pt_BR'):
    # Mantém a faixa estável no centro por tempo suficiente para leitura.
    if progresso < 0.14 or progresso > 0.90:
        return
    t_entrada = min(1.0, max(0.0, (progresso - .14) / .15))
    t_saida = min(1.0, max(0.0, (.90 - progresso) / .15))
    suave = min(t_entrada, t_saida)
    y = int(279 - 42 * suave)
    cor = COR_BIOMAS_UI.get(bioma, (123, 225, 245))
    rect = pygame.Rect(18, y, 414, 120)
    pygame.draw.rect(superficie, (11, 18, 36), rect.move(0, 4), border_radius=15)
    pygame.draw.rect(superficie, (28, 39, 69), rect, border_radius=15)
    pygame.draw.rect(superficie, cor, rect, 3, border_radius=15)
    pygame.draw.line(superficie, misturar_cores(cor, BRANCO, .40),
                     (rect.left + 22, rect.top + 7), (rect.right - 22, rect.top + 7), 2)
    if not leve:
        for i in range(5):
            x = 48 + i * 83 + int(math.sin(frame * .045 + i) * 5)
            yy = y + 17 + (i % 2) * 8
            pygame.draw.line(superficie, cor, (x - 3, yy), (x + 3, yy), 1)
            pygame.draw.line(superficie, cor, (x, yy - 3), (x, yy + 3), 1)
    desenhar_texto_centralizado(superficie, titulo, fonte_grande, BRANCO, PRETO, y + 28)
    subtitulos = SUBTITULOS_BIOMAS_EN if idioma == 'en_US' else SUBTITULOS_BIOMAS
    sub = subtitulos.get(bioma, 'EXPLORE PIXEL RUSH')
    desenhar_texto_centralizado(superficie, sub, fonte_pequena, cor, PRETO, y + 74)
    pygame.draw.rect(superficie, (11, 18, 34), (84, y + 99, 282, 4), border_radius=2)
    pygame.draw.rect(superficie, cor, (84, y + 99, max(1, int(282 * progresso)), 4), border_radius=2)


def desenhar_clima_premium(superficie, bioma, frame):
    # Detalhes de tempo pré-decimados: poucos desenhos, nenhuma Surface nova.
    if bioma in ('neve', 'ilhas_celestes'):
        for i in range(7):
            x = (i * 71 + frame // 3) % LARGURA_VIRTUAL
            y = (i * 79 + frame // 2) % (ALTURA_VIRTUAL - 118) + 115
            pygame.draw.line(superficie, (218, 241, 255), (x - 2, y), (x + 2, y), 1)
            pygame.draw.line(superficie, (218, 241, 255), (x, y - 2), (x, y + 2), 1)
    elif bioma == 'floresta':
        for i in range(5):
            x = (i * 97 + int(math.sin(frame * .02 + i) * 18)) % LARGURA_VIRTUAL
            y = 348 + (i * 41) % 205 + int(math.sin(frame * .06 + i) * 5)
            pygame.draw.circle(superficie, (247, 249, 149), (x, y), 2)
    elif bioma == 'vulcao':
        for i in range(5):
            x = (i * 105 + frame // 5) % LARGURA_VIRTUAL
            y = 365 + (i * 43 - frame // 3) % 176
            pygame.draw.rect(superficie, (255, 163, 73), (x, y, 2, 3))
    elif bioma == 'cidade_futurista':
        for i in range(4):
            x = (i * 115 + (frame // 3) * (1 + i % 2)) % LARGURA_VIRTUAL
            y = 375 + i * 41
            pygame.draw.line(superficie, (113, 237, 255), (x, y), (x + 12, y), 1)
    elif bioma == 'reino_submerso':
        for i in range(6):
            x = (i * 73 + int(math.sin(frame * .05 + i) * 7)) % LARGURA_VIRTUAL
            y = 370 + (i * 66 - frame // 3) % 212
            pygame.draw.circle(superficie, (168, 240, 255), (x, y), 3, 1)
    elif bioma == 'deserto':
        for i in range(5):
            x = (i * 101 + frame // 2) % LARGURA_VIRTUAL
            y = 400 + i * 39
            pygame.draw.line(superficie, (241, 208, 141), (x, y), (x + 12, y - 2), 1)
    else:
        if (frame // 80) % 2:
            for x, y in ((65, 412), (212, 477), (379, 429)):
                pygame.draw.rect(superficie, (232, 244, 255), (x, y, 3, 2))


def desenhar_hud_premium(superficie, frame, combo, febre, febre_timer, missoes, leve=False):
    # Molduras, divisores e indicadores claros; valores continuam na UI original.
    pygame.draw.line(superficie, (126, 237, 255), (28, 20), (190, 20), 1)
    pygame.draw.circle(superficie, (255, 221, 116), (191, 63), 5)
    pygame.draw.circle(superficie, (255, 246, 181), (189, 61), 2)
    pygame.draw.line(superficie, (68, 171, 220), (24, 115), (245, 115), 1)
    completadas = sum(bool(item.get('concluida')) for item in missoes)
    total = max(1, len(missoes))
    pygame.draw.rect(superficie, (38, 59, 83), (25, 195, 216, 3), border_radius=2)
    if completadas:
        pygame.draw.rect(superficie, (80, 222, 156),
                         (25, 195, int(216 * completadas / total), 3), border_radius=2)
    for i in range(total):
        cor_ponto = (102, 225, 166) if i < completadas else (70, 86, 110)
        pygame.draw.circle(superficie, cor_ponto, (30 + i * 11, 188), 3)
    cor_combo = (255, 226, 100) if combo >= 10 else (99, 225, 255)
    if combo >= 6:
        pygame.draw.line(superficie, cor_combo, (267, 88), (429, 88), 1)
    if combo >= 10 and not leve and (frame // 10) % 2 == 0:
        for dx, dy in ((272, 102), (428, 101), (273, 145), (428, 147)):
            pygame.draw.line(superficie, cor_combo, (dx - 2, dy), (dx + 2, dy), 1)
            pygame.draw.line(superficie, cor_combo, (dx, dy - 2), (dx, dy + 2), 1)
    if febre >= 65:
        brilho = (255, 176, 107) if febre < 90 else (255, 225, 120)
        pygame.draw.line(superficie, brilho, (266, 210), (429, 210), 1)
    if febre >= 90 and febre_timer <= 0:
        pygame.draw.rect(superficie, (255, 229, 121), (272, 187, 156, 16), 1, border_radius=5)
        if (frame // 16) % 2 == 0:
            txt = render_texto_cacheado(fonte_pequena, 'PRONTA', (255, 235, 151))
            superficie.blit(txt, (364 - txt.get_width() // 2, 188))


def desenhar_palco_menu_premium(superficie, frame, leve=False):
    """Cenografia simples do menu, sem texturas nem superfícies temporárias."""
    cx = LARGURA_VIRTUAL // 2
    palco = pygame.Rect(143, 145, 164, 76)
    pygame.draw.ellipse(superficie, (17, 30, 52), (133, 200, 184, 26))
    pygame.draw.ellipse(superficie, (68, 162, 207), (145, 207, 160, 11), 1)
    pygame.draw.rect(superficie, (16, 26, 44), palco.move(0, 4), border_radius=17)
    pygame.draw.rect(superficie, (30, 54, 83), palco, border_radius=17)
    pygame.draw.rect(superficie, (101, 220, 248), palco, 2, border_radius=17)
    pygame.draw.line(superficie, (152, 235, 251), (162, 151), (287, 151), 1)
    for shift in (-1, 1):
        px = cx + shift * 86
        pygame.draw.circle(superficie, (63, 130, 175), (px, 180), 7, 1)
        pygame.draw.circle(superficie, (143, 241, 253), (px, 180), 2)
    if not leve:
        for i in range(4):
            px = 158 + i * 43
            py = 155 + int(math.sin(frame * 0.044 + i * 1.6) * 5)
            pygame.draw.line(superficie, (111, 207, 244), (px - 2, py), (px + 2, py), 1)
            pygame.draw.line(superficie, (111, 207, 244), (px, py - 2), (px, py + 2), 1)
    # Filete entre o palco e os cards (y=236); os botões não se movem.
    pygame.draw.line(superficie, (67, 143, 181), (179, 228), (271, 228), 1)
    pygame.draw.circle(superficie, (232, 215, 117), (cx, 228), 2)


def desenhar_acabamento_card_menu(superficie, rect, frame, acento, leve=False):
    pygame.draw.line(superficie, misturar_cores(acento, BRANCO, 0.32),
                     (rect.x + 14, rect.y + 7), (rect.x + 62, rect.y + 7), 2)
    if not leve:
        x = rect.right - 16
        y = rect.y + 17 + int(math.sin(frame * 0.052) * 2)
        pygame.draw.circle(superficie, misturar_cores(acento, BRANCO, 0.40), (x, y), 3)
        pygame.draw.circle(superficie, BRANCO, (x - 1, y - 1), 1)


def desenhar_progresso_conquistas(superficie, concluidas, total):
    """Barra geral discreta acima da lista, sem modificar prêmios ou saves."""
    total = max(1, total)
    progresso = max(0.0, min(1.0, concluidas / total))
    pygame.draw.rect(superficie, (18, 28, 45), (34, 103, 377, 10), border_radius=5)
    if progresso:
        pygame.draw.rect(superficie, (103, 224, 179), (35, 104, int(375 * progresso), 8), border_radius=4)
    pygame.draw.rect(superficie, (103, 179, 205), (34, 103, 377, 10), 1, border_radius=5)
    txt = f"{concluidas}/{total} CONQUISTAS" if concluidas < total else "COLEÇÃO COMPLETA!"
    desenhar_texto_centralizado(superficie, txt, fonte_pequena,
                                (178, 239, 223), PRETO, 82)


def desenhar_resultados_premium(superficie, frame, inicio, metros, moedas, combo,
                                recorde, missoes, leve=False, dados=None):
    """Cards animados da corrida; camada independente do cache do Game Over."""
    idade = max(0, frame - inicio)
    progresso = min(1.0, idade / 56.0)
    chegada = 1.0 - (1.0 - progresso) ** 3
    idioma = (dados or {}).get("idioma", "pt_BR")
    textos = (
        ("DISTANCE", "COINS", "COMBO") if idioma == "en_US" else
        ("DISTÂNCIA", "MOEDAS", "COMBO")
    )
    valores = (
        f"{int(metros * chegada)} m",
        str(int(moedas * min(1.0, max(0, idade - 9) / 46.0))),
        str(int(combo * min(1.0, max(0, idade - 13) / 36.0))),
    )
    cores = ((136, 225, 250), (255, 218, 114), (184, 170, 249))
    for i, (label, value, cor) in enumerate(zip(textos, valores, cores)):
        x, y, w, h = 62 + i * 111, 250, 104, 82
        pygame.draw.rect(superficie, (10, 17, 30), (x, y + 3, w, h), border_radius=11)
        pygame.draw.rect(superficie, (29, 42, 63), (x, y, w, h), border_radius=11)
        pygame.draw.rect(superficie, cor, (x, y, w, h), 1, border_radius=11)
        pygame.draw.rect(superficie, misturar_cores(cor, BRANCO, .40), (x + 10, y + 8, w - 20, 2), border_radius=1)
        label_surface = render_texto_cacheado(fonte_pequena, label, (193, 213, 232))
        superficie.blit(label_surface, (x + (w - label_surface.get_width()) // 2, y + 19))
        valor_surf = render_texto_cacheado(fonte_missoes, value, cor)
        if valor_surf.get_width() > w - 8:
            valor_surf = pygame.transform.scale(valor_surf, (w - 8, valor_surf.get_height()))
        superficie.blit(valor_surf, (x + (w - valor_surf.get_width()) // 2, y + 45))
    # Barra da missão já concluída mantém a posição da tela anterior.
    concluidas = sum(bool(m.get("concluida")) for m in missoes)
    pct = concluidas / max(1, len(missoes))
    pygame.draw.rect(superficie, (17, 27, 45), (67, 477, 314, 9), border_radius=4)
    if pct:
        pygame.draw.rect(superficie, (96, 226, 171), (68, 478, int(312 * pct * chegada), 7), border_radius=3)
    pygame.draw.rect(superficie, (82, 151, 174), (67, 477, 314, 9), 1, border_radius=4)
    if recorde > 0 and metros >= recorde and not leve:
        for i in range(4):
            x = 75 + i * 96
            y = 195 + int(math.sin(frame * .07 + i) * 3)
            pygame.draw.line(superficie, (255, 223, 126), (x - 3, y), (x + 3, y), 1)
            pygame.draw.line(superficie, (255, 223, 126), (x, y - 3), (x, y + 3), 1)


def desenhar_botao_premium(superficie, rect, texto, fonte_obj, cor_fundo, cor_texto, frame_contador, ativo=False):
    brilho = 12 + int((math.sin(frame_contador * 0.09) + 1) * 6) if ativo else 8
    sombra = rect.move(0, 4)
    pygame.draw.rect(superficie, (14, 18, 28), sombra, border_radius=12)
    pygame.draw.rect(superficie, cor_fundo, rect, border_radius=12)
    pygame.draw.rect(superficie, BRANCO, rect, 2, border_radius=12)
    pygame.draw.rect(superficie, misturar_cores(cor_fundo, BRANCO, 0.38), (rect.x + 4, rect.y + 4, rect.w - 8, 8), border_radius=6)
    if ativo:
        pygame.draw.rect(superficie, misturar_cores(cor_fundo, BRANCO, 0.58), rect.inflate(brilho, brilho), 1, border_radius=14)
    desenhar_rotulo_botao(superficie, texto, fonte_obj, cor_texto, PRETO, rect)


def desenhar_fx_pet(superficie, pet_id, centro, frame_contador, escala=1.0, leve=False):
    cx, cy = centro
    fase = frame_contador / 6.0
    # Aura/trilha leve e barata: só primitivas, sem custo alto de surfaces.
    if not leve:
        for i in range(3):
            atraso = i * 8
            ox = int(cx - 14 - i * 8 - ((frame_contador + atraso) % 10) * 0.8)
            oy = int(cy + 10 + math.sin((frame_contador + atraso) * 0.18) * 2)
            cor_aura = (46, 84, 126) if pet_id not in ("DRAGAO", "DRAGAO_PLASMA") else (56, 88, 150)
            pygame.draw.ellipse(superficie, cor_aura, (ox, oy, int(12 * escala), int(5 * escala)))
    particulas = []
    if pet_id == "BOLHA":
        particulas = [((cx - 18 + (fase * 3) % 14), cy - 12 - ((fase + i * 5) % 10), (120, 240, 255), 2) for i in range(3)]
        if not leve:
            for i in range(2):
                pygame.draw.circle(superficie, (195, 250, 255), (int(cx - 6 + i * 10), int(cy - 14 - ((fase * 1.8 + i * 4) % 8))), max(1, int(2 * escala)), 1)
    elif pet_id == "RAPOSA":
        particulas = [((cx - 24 - ((fase + i * 6) % 12), cy + 10 - i * 5), (255, 199, 74), 2) for i in range(3)]
        for i in range(3 if not leve else 2):
            x0 = int(cx - 10 - i * 8)
            pygame.draw.line(superficie, (255, 171, 71), (x0, int(cy + 6 - i * 2)), (x0 - 8, int(cy + 8 - i * 2)), 2 if i == 0 else 1)
    elif pet_id == "FANTASMA":
        particulas = [((cx - 14 + i * 8, cy - 18 + ((fase + i * 4) % 10)), (208, 146, 255), 2) for i in range(3)]
        if not leve:
            for i in range(3):
                pygame.draw.arc(superficie, (196, 135, 255), (int(cx - 22 + i * 10), int(cy - 6 + i * 2), 10, 16), math.pi * 0.2, math.pi * 1.15, 1)
    elif pet_id == "TARTARUGA":
        particulas = [((cx - 20 + i * 10, cy - 16 + ((fase + i * 3) % 8)), (80, 230, 255), 2) for i in range(3)]
        if not leve:
            for i in range(2):
                pygame.draw.circle(superficie, (145, 246, 255), (int(cx - 10 + i * 10), int(cy - 6 - ((fase + i * 3) % 4))), max(1, int(1 * escala)), 1)
    elif pet_id in ("DRAGAO", "DRAGAO_PLASMA"):
        cor = (255, 110, 235) if pet_id == "DRAGAO" else (118, 245, 255)
        cor_sec = (255, 182, 245) if pet_id == "DRAGAO" else (196, 253, 255)
        particulas = [((cx - 28 - ((fase + i * 4) % 16), cy - 8 + i * 7), cor, 2 + (i == 1)) for i in range(4)]
        for i in range(3 if not leve else 2):
            bx = int(cx - 18 - i * 9)
            by = int(cy - 5 + i * 5)
            pygame.draw.line(superficie, cor, (bx, by), (bx - 7, by - 3), 2 if i == 0 else 1)
            if not leve:
                pygame.draw.circle(superficie, cor_sec, (bx - 8, by - 3), 1 + (i == 0))
    elif pet_id == "GOLEM":
        particulas = [((cx - 18 + i * 10, cy + 12 - ((fase + i * 2) % 6)), (255, 157, 64), 2) for i in range(3)]
        for i in range(3):
            pygame.draw.rect(superficie, (255, 193, 112), (int(cx - 16 + i * 8), int(cy + 6 - ((fase + i * 2) % 4)), 2, 2))
    elif pet_id == "BEIJA_FLOR":
        cores = ((255, 125, 244), (104, 248, 255), (246, 222, 108))
        particulas = [((cx - 26 - ((fase + i * 6) % 18), cy - 12 + i * 8), cores[i % 3], 2) for i in range(4)]
        if not leve:
            pygame.draw.arc(superficie, (214, 250, 255), (int(cx - 18), int(cy - 20), 18, 12), math.pi * 0.15, math.pi * 0.92, 1)
            pygame.draw.arc(superficie, (255, 185, 242), (int(cx - 6), int(cy - 18), 18, 12), math.pi * 0.15, math.pi * 0.92, 1)
    elif pet_id == "ABELHA_MAGNETICA":
        particulas = [((cx - 12 + i * 9, cy - 18 + ((fase + i * 4) % 9)), (112, 244, 255), 2) for i in range(3)]
        for i in range(2 if leve else 3):
            pygame.draw.arc(superficie, (251, 216, 81), (int(cx - 18 - i * 2), int(cy - 14 + i * 2), 18, 18), math.pi * 0.2, math.pi * 0.95, 1)
    for part in particulas:
        if len(part) == 4:
            px, py, cor, raio = part
        else:
            (px, py), cor, raio = part
        pygame.draw.circle(superficie, cor, (int(px), int(py)), max(1, int(raio * escala)))


def gerar_fx_pouso_bioma(x, y, bioma, grupo_sprites, pool_manager, leve=False):
    paletas = {
        "cidade": ((170, 170, 190), (120, 120, 145)),
        "deserto": ((232, 194, 112), (188, 144, 88)),
        "neve": ((232, 248, 255), (154, 210, 245)),
        "vulcao": ((255, 126, 72), (255, 205, 86)),
        "cidade_futurista": ((88, 240, 255), (199, 116, 255)),
        "floresta": ((114, 214, 94), (76, 168, 82)),
        "reino_submerso": ((86, 220, 255), (117, 171, 255)),
        "ilhas_celestes": ((255, 255, 255), (172, 224, 255)),
    }
    cores = paletas.get(bioma, paletas["cidade"])
    quantidade = 4 if leve else 8
    for i in range(quantidade):
        ang = -math.pi * 0.85 + (i / max(1, quantidade - 1)) * math.pi * 0.7
        vx = math.cos(ang) * random.uniform(1.3, 3.8)
        vy = math.sin(ang) * random.uniform(1.2, 2.8) - random.uniform(1.4, 3.4)
        cor = cores[i % len(cores)]
        p = pool_manager.obter_particula(x + random.randint(-8, 8), y - random.randint(0, 4), cor, vx, vy, vida=16 if leve else 22, tamanho=3 if leve else 4)
        if p:
            grupo_sprites.add(p)


# Painel de apresentação criado sob demanda uma vez por premiação.
_RECOMPENSA_VEIL = None


def desenhar_animacao_recompensa(superficie, anim, frame_contador, leve=False):
    """Revelação cinematográfica, não bloqueia compra nem modifica save."""
    global _RECOMPENSA_VEIL
    if not anim:
        return False
    idade = max(0, frame_contador - anim.get('inicio', 0))
    duracao = max(1, int(anim.get('duracao', 95)))
    if idade >= duracao:
        return False
    if _RECOMPENSA_VEIL is None:
        _RECOMPENSA_VEIL = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL), pygame.SRCALPHA)
        _RECOMPENSA_VEIL.fill((6, 10, 23, 170))
    if not leve:
        superficie.blit(_RECOMPENSA_VEIL, (0, 0))
    cor = anim.get('cor', (95, 235, 220))
    tipo = anim.get('tipo', '')
    ident = anim.get('id', '')
    raridade = anim.get('raridade', 'Épico')
    painel = pygame.Rect(34, 189, 382, 430)
    pygame.draw.rect(superficie, (6, 12, 24), painel.move(0, 7), border_radius=21)
    pygame.draw.rect(superficie, (24, 32, 54), painel, border_radius=21)
    pygame.draw.rect(superficie, (47, 59, 90), (painel.x + 3, painel.y + 3, painel.w - 6, 60), border_radius=18)
    desenhar_moldura_raridade(superficie, painel, raridade, frame_contador, True, leve)
    titulo = anim.get('titulo', 'ITEM DESBLOQUEADO!')
    desenhar_texto_centralizado(superficie, titulo, fonte_grande, BRANCO, PRETO, 216)
    brilho = misturar_cores(cor, BRANCO, 0.35)
    centro = (LARGURA_VIRTUAL // 2, 410)
    if tipo == 'SKIN' and ident in SKINS:
        sprite = _popup_skin_animado(ident, frame_contador)
        superficie.blit(sprite, sprite.get_rect(center=centro))
    elif tipo == 'PET' and ident in PETS_CONFIG:
        sprite = _popup_pet_animado(ident, frame_contador)
        superficie.blit(sprite, sprite.get_rect(center=centro))
    else:
        pygame.draw.circle(superficie, brilho, centro, 40, 4)
    pygame.draw.ellipse(superficie, (13, 20, 36), (115, 500, 220, 18))
    pygame.draw.ellipse(superficie, brilho, (128, 503, 194, 12), 1)
    if not leve:
        for i in range(12):
            ang = i * (math.tau / 12) + frame_contador * 0.023
            raio = 130 + (i % 3) * 13
            x = int(centro[0] + math.cos(ang) * raio)
            y = int(centro[1] + math.sin(ang) * raio)
            if painel.collidepoint(x, y):
                pygame.draw.line(superficie, brilho, (x - 3, y), (x + 3, y), 1)
                pygame.draw.line(superficie, brilho, (x, y - 3), (x, y + 3), 1)
    sub = str(anim.get('sub', ''))
    legenda = render_texto_cacheado(fonte, sub, BRANCO)
    superficie.blit(legenda, legenda.get_rect(center=(225, 557)))
    pygame.draw.rect(superficie, (16, 22, 38), (78, 589, 294, 7), border_radius=3)
    progresso = max(1, int(292 * (1 - idade / duracao)))
    pygame.draw.rect(superficie, brilho, (79, 590, progresso, 5), border_radius=3)
    return True


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


def gerar_trilha_bioma(indice):
    """Loop musical compacto e sintetizado por bioma; sem arquivos externos."""
    try:
        sample_rate = 11025
        duracao = 2.4
        notas_base = [110.0, 130.81, 146.83, 164.81, 98.0, 123.47]
        escalas = [
            [523.25, 659.25, 783.99, 659.25], [392.0, 440.0, 523.25, 587.33],
            [293.66, 349.23, 440.0, 392.0], [130.81, 164.81, 196.0, 164.81],
            [587.33, 698.46, 880.0, 1046.5], [329.63, 392.0, 493.88, 392.0],
        ]
        base = notas_base[indice % len(notas_base)]
        escala = escalas[indice % len(escalas)]
        buf = array.array('h')
        total = int(sample_rate * duracao)
        for i in range(total):
            ts = i / sample_rate
            beat = int((ts / 0.3)) % len(escala)
            env = 0.78 + 0.22 * math.sin(ts * math.pi * 2 / duracao)
            bass = 0.20 if math.sin(2 * math.pi * base * ts) >= 0 else -0.20
            lead = 0.18 * math.sin(2 * math.pi * escala[beat] * ts)
            pulse = 0.08 * math.sin(2 * math.pi * (base * 2) * ts) if (ts % 0.6) < 0.08 else 0.0
            sample = int(max(-0.7, min(0.7, (bass + lead + pulse) * env)) * 32767)
            buf.append(sample); buf.append(sample)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None



def criar_stems_ambientais_v3107():
    """Duas camadas instrumentais de 120 BPM e 4 s/compasso x2.

    Fontes sintéticas produzidas uma única vez, sem arquivos comerciais.
    Mesma grade de 8 semínimas usada pela trilha principal.
    Os canais do mixer são iniciados na mesma atualização; isso não é
    agendamento de áudio sample-accurate.
    """
    try:
        sample_rate = 22050
        total = sample_rate * 4
        baixo, textura = array.array('h'), array.array('h')
        frequencias = (65.41, 65.41, 73.42, 82.41, 55.0, 55.0, 61.74, 65.41)
        notas = (261.63, 329.63, 392.0, 329.63, 220.0, 261.63, 293.66, 261.63)
        for i in range(total):
            seg = i / float(sample_rate)
            beat = int(seg * 2) % 8
            beat_phase = (seg * 2.0) % 1.0
            envelope = (min(1., beat_phase * 8.) * min(1., (1. - beat_phase) * 4.))
            bass = (math.sin(2 * math.pi * frequencias[beat] * seg) * .58
                    + math.sin(2 * math.pi * frequencias[beat] * 2 * seg) * .11)
            pad = (math.sin(2 * math.pi * notas[beat] * seg) * .33
                   + math.sin(2 * math.pi * notas[beat] * .5 * seg) * .23)
            v1 = max(-32768, min(32767, int(bass * envelope * 32767 * .20)))
            v2 = max(-32768, min(32767, int(pad * 32767 * .19)))
            baixo.extend((v1, v1)); textura.extend((v2, v2))
        return pygame.mixer.Sound(buffer=baixo), pygame.mixer.Sound(buffer=textura)
    except (ValueError, pygame.error, TypeError, MemoryError):
        return None, None


class GerenciadorSons:
    def __init__(self):
        self.sons = {}
        self.canal_musica = None
        self.canal_ambiente = None
        self.trilha_normal = None
        self.trilha_lenta = None
        self.musica_tocando = None
        self.trilhas_bioma = {}
        self.chave_musica = None
        self.proximo_ambiente_frame = 0
        self.variacoes_pitch = {}
        self.canal_ritmo = None
        self.camada_ritmo = None
        self.canais_stems = []
        self.sons_stems = []
        self.oclusao_audio = OclusaoAcustica2D()
        self.reverb_audio = ReverbConvolucional()
        self.mixagem_contextual = MixagemContextual()
        self.carregar_sons()

    def carregar_sons(self):
        try:
            if pygame.mixer.get_init():
                self.canal_musica = pygame.mixer.Channel(0)
                if pygame.mixer.get_num_channels() > 6:
                    self.canal_ambiente = pygame.mixer.Channel(6)
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

            # Variações pré-calculadas: repetição sonora menos artificial.
            for nome_efeito in ("pulo", "moeda", "swipe_down", "powerup", "quebrar", "turbo", "ima"):
                if self.sons.get(nome_efeito):
                    self.variacoes_pitch[nome_efeito] = criar_variantes_pitch(self.sons[nome_efeito])
            if pygame.mixer.get_init() and pygame.mixer.get_num_channels() >= 8:
                self.canal_ritmo = pygame.mixer.Channel(7)
                self.camada_ritmo = criar_camada_ritmica()
                if self.canal_ritmo:
                    self.canal_ritmo.set_volume(0.0)
            if pygame.mixer.get_init():
                try:
                    pygame.mixer.set_num_channels(max(12, pygame.mixer.get_num_channels()))
                    self.canais_stems = [pygame.mixer.Channel(k) for k in (8, 9, 10, 11)]
                    self.sons_stems = list(criar_stems_pygame())
                except (pygame.error, ValueError):
                    self.canais_stems = []
                    self.sons_stems = []
            self.trilha_normal = gerar_trilha_sonora(grave=False)
            self.trilha_lenta = gerar_trilha_sonora(grave=True)
            self.trilhas_bioma = {nome: gerar_trilha_bioma(i) for i, nome in enumerate(("cidade", "deserto", "neve", "vulcao", "cidade_futurista", "floresta"))}
            self.sons["amb_cidade"] = criar_som_arpejo([523, 659, 784], 0.05, "square", 0.12)
            self.sons["amb_deserto"] = criar_som_sintetico(340, 220, 0.12, "soft_wind", 0.10)
            self.sons["amb_neve"] = criar_som_arpejo([880, 1174, 988], 0.04, "sine", 0.12)
            self.sons["amb_vulcao"] = criar_som_sintetico(140, 85, 0.14, "noise", 0.15)
            self.sons["amb_cidade_futurista"] = criar_som_arpejo([880, 1046, 1318], 0.05, "square", 0.11)
            self.sons["amb_floresta"] = criar_som_arpejo([659, 784, 988], 0.05, "sine", 0.11)
            self.sons["amb_reino_submerso"] = criar_som_sintetico(460, 620, 0.12, "sine", 0.11)
            self.sons["amb_ilhas_celestes"] = criar_som_arpejo([784, 988, 1174], 0.05, "sine", 0.11)
        except Exception:
            pass

    def tocar_som(self, nome, e_slow=False, vol_sfx=1.0):
        if vol_sfx <= 0: return
        key = f"{nome}_slow" if (e_slow and f"{nome}_slow" in self.sons) else nome
        opcoes = self.variacoes_pitch.get(nome) if key == nome else None
        s = random.choice(opcoes) if opcoes else (self.sons.get(key) or self.sons.get(nome))
        if s:
            try:
                s.set_volume(vol_sfx)
                if not self.mixagem_contextual.tocar_prioritario(nome, s):
                    s.play()
                    self.mixagem_contextual.avisar(nome)
            except Exception:
                pass

    def tocar_ambiente_bioma(self, cenario, clima_tipo, vol_sfx, frame_contador, pos_x=None, oclusao=0.0):
        if vol_sfx <= 0 or frame_contador < self.proximo_ambiente_frame:
            return
        chave = f"amb_{cenario}"
        if clima_tipo == "tempestade":
            chave = "amb_cidade_futurista"
        elif clima_tipo in ("nevasca",):
            chave = "amb_neve"
        elif clima_tipo in ("tempestade_areia",):
            chave = "amb_deserto"
        som = self.sons.get(chave)
        if som:
            try:
                # Obstruções artísticas no mapa geométrico filtram agudos e
                # atenuam ambiente sem alterar trilha musical ou game feel.
                oclusao = max(0.0, min(0.9, float(oclusao)))
                som = self.oclusao_audio.som_filtrado(som, oclusao)
                som = self.reverb_audio.aplicar(som, cenario, oclusao)
                ganho = max(0.0, min(0.35, vol_sfx * 0.32)) * (1.0 - oclusao * 0.56)
                if self.canal_ambiente is not None:
                    # Áudio posicional leve no canal ambiental, independente da trilha.
                    pan = 0.5 if pos_x is None else max(0.0, min(1.0, float(pos_x) / LARGURA_VIRTUAL))
                    self.canal_ambiente.set_volume(ganho * (1.0 - 0.65 * pan),
                                                  ganho * (0.35 + 0.65 * pan))
                    self.canal_ambiente.play(som)
                else:
                    som.set_volume(ganho)
                    som.play()
            except (pygame.error, ValueError, TypeError):
                pass
        self.proximo_ambiente_frame = frame_contador + random.randint(165, 255)


    def atualizar_musica(self, estado, e_slow, vol_musica, cenario="cidade", clima_tipo="limpo", perigo=False):
        """Eventos meteorologicos alteram somente SFX; a faixa nao recomeça."""
        if not self.canal_musica:
            return
        try:
            self.canal_musica.set_volume(vol_musica)
            if estado in ("JOGANDO", "PAUSA"):
                # Mudanca de clima NAO entra na identidade da musica.
                # v3.172: a base musical permanece contínua; tensão/slow são
                # expressos pelo volume dos stems em vez de reiniciar o loop.
                trilha = self.trilha_normal
                chave = ("gameplay",)
            elif estado in ("INICIO", "CONFIG", "CONFIG_CONTROLES", "CONFIG_ACESSIBILIDADE", "LOJA", "UPGRADES", "DESAFIOS", "RANKING", "RELIQUIAS", "CONQUISTAS", "RECORDES"):
                trilha = self.trilha_normal
                chave = ("menu",)
            else:
                trilha = None
                chave = None
            if trilha is None:
                if self.musica_tocando is not None:
                    self.canal_musica.stop()
                if self.canal_ritmo:
                    self.canal_ritmo.stop()
                for canal in self.canais_stems:
                    canal.stop()
                self.musica_tocando = None
                self.chave_musica = None
            elif trilha is not self.musica_tocando:
                self.canal_musica.play(trilha, loops=-1)
                # Camada percussiva inicia junto ao ciclo da trilha; clima não reinicia.
                if self.canal_ritmo and self.camada_ritmo:
                    self.canal_ritmo.play(self.camada_ritmo, loops=-1)
                for canal, stem in zip(self.canais_stems, self.sons_stems):
                    if stem is not None:
                        canal.play(stem, loops=-1)
                self.musica_tocando = trilha
                self.chave_musica = chave
            else:
                self.chave_musica = chave
            if self.canal_ritmo:
                ganho = 0.0 if estado != "JOGANDO" else min(0.16, vol_musica * (0.055 + (0.035 if perigo else 0) + (0.03 if e_slow else 0)))
                self.canal_ritmo.set_volume(ganho)
            if self.canais_stems:
                jogando = estado == "JOGANDO"
                # A música base não reinicia com clima/bioma/noite.
                intensidade = 1.0 if (perigo or clima_tipo in ("tempestade", "nevasca", "tempestade_areia")) else .62
                ganho_bass = min(.16, vol_musica * (.055 + .05 * intensidade)) if jogando else .0
                ganho_pad = min(.15, vol_musica * (.03 + .035 * (1.0 if cenario in ("floresta", "ilhas_celestes") else .6))) if jogando else .0
                ganhos=(ganho_bass, ganho_pad,
                        min(.15,vol_musica * (.034 + .05 * intensidade)) if jogando else 0.,
                        min(.13,vol_musica * (.026 + .025 * float(perigo))) if jogando else 0.)
                for canal,ganho in zip(self.canais_stems,ganhos):
                    canal.set_volume(ganho)
        except Exception:
            pass


# --- SISTEMA DE SALVAMENTO ---
from pixelrush_android_storage_v327711 import resolver_save
ARQUIVO_SAVE = resolver_save("savegame_DEV.json" if PIXELRUSH_DEV_BUILD else "savegame.json", android=E_ANDROID)


# Conquistas de longo prazo: objetivos acumulativos e recompensas únicas.
CONQUISTAS_CONFIG = [
    ("distancia_v2", "ach_dist_titulo", "ach_dist_desc", "distancia_total", 25000, 250),
    ("moedas_v2", "ach_moedas_titulo", "ach_moedas_desc", "moedas_coletadas", 10000, 300),
    ("quase_v2", "ach_quase_titulo", "ach_quase_desc", "quase_colisoes", 250, 400),
    ("bau_v2", "ach_bau_titulo", "ach_bau_desc", "bau_abertos", 75, 500),
    ("febre_v2", "ach_febre_titulo", "ach_febre_desc", "febres", 100, 600),
    ("combo_v2", "ach_combo_titulo", "ach_combo_desc", "melhor_combo", 75, 500),
    ("partidas_v2", "ach_partidas_titulo", "ach_partidas_desc", "partidas", 250, 750),
    ("diarios", "Rotina de Campeão", "Conclua 30 desafios diários", "desafios_diarios", 30, 700),
    ("semanais", "Lenda Semanal", "Conclua 12 desafios semanais", "desafios_semanais", 12, 900),
    ("pets", "Melhor Amigo", "Desbloqueie 5 pets", "pets_desbloqueados", 5, 500),
    ("skins", "Estilista Supremo", "Desbloqueie 12 skins", "skins_desbloqueadas", 12, 650),
    ("bioma_cidade", "Rei da Cidade", "Percorra 10000 m na cidade", "cidade_total", 10000, 500),
    ("bioma_deserto", "Dono das Dunas", "Percorra 10000 m no deserto", "deserto_total", 10000, 500),
    ("bioma_neve", "Lenda do Gelo", "Percorra 10000 m na neve", "neve_total", 10000, 500),
    ("powerups", "Colecionador de Poder", "Colete 1000 power-ups", "powerups", 1000, 600),
    ("febre_rodada", "Febre Absoluta", "Ative 5 febres em uma corrida", "recorde_febres_rodada", 5, 800),
    ("combo_lendario", "Combo Lendário", "Alcance combo de 150 ações", "melhor_combo", 150, 1000),
    ("bau_lendario", "Caçador de Tesouros", "Abra 500 baús secretos", "bau_abertos", 500, 1200),
    ("corridas_500", "Veterano Imortal", "Participe de 1000 corridas", "partidas", 1000, 1500),
]

PATENTES_CONFIG = [
    ("BRONZE", 50, (190, 120, 75)),
    ("PRATA", 150, (190, 205, 220)),
    ("OURO", 300, (255, 205, 55)),
    ("PLATINA", 500, (95, 235, 220)),
]

PETS_CONFIG = {
    "BOLHA": {"nome": "Bolha", "cor": (80, 205, 255), "preco": 1200, "habilidade": "Cada 5 moedas coletadas dão +1 moeda extra.", "tipo": "MOEDAS", "raridade": "Comum", "objetivo": None},
    "RAPOSA": {"nome": "Raposa Turbo", "cor": (255, 150, 65), "preco": 4500, "habilidade": "Começa cada corrida com um escudo extra.", "tipo": "ESCUDO", "raridade": "Raro", "objetivo": None},
    "FANTASMA": {"nome": "Fantasma", "cor": (195, 160, 255), "preco": 0, "habilidade": "Uma vez por corrida, salva de uma colisão fatal.", "tipo": "SALVA_VIDA", "raridade": "Épico", "objetivo": "Sobreviva a 100 corridas"},
    "TARTARUGA": {"nome": "Tartaruga Abissal", "cor": (65, 225, 175), "preco": 0, "habilidade": "Recompensas de portal aumentadas em 20%.", "tipo": "PORTAL", "raridade": "Épico", "objetivo": "Conclua 25 portais aquáticos"},
    "DRAGAO": {"nome": "Dragão Neon", "cor": (255, 80, 110), "preco": 0, "habilidade": "A barra de febre carrega 25% mais rápido.", "tipo": "FEBRE", "raridade": "Lendário", "objetivo": "Alcance combo 100 e 100 febres"},
    "GOLEM": {"nome": "Golem de Basalto", "cor": (180, 100, 75), "preco": 0, "habilidade": "Começa a corrida com dois escudos extras.", "tipo": "ESCUDO_FORTE", "raridade": "Lendário", "objetivo": "Derrote 10 chefes de portal"},
    "BEIJA_FLOR": {"nome": "Beija-flor Prisma", "cor": (90, 245, 190), "preco": 22000, "habilidade": "A barra de febre carrega 12% mais rápido.", "tipo": "FEBRE_RAPIDA", "raridade": "Épico", "objetivo": None},
    "DRAGAO_PLASMA": {"nome": "Dragãozinho de Plasma", "cor": (70, 210, 255), "preco": 0, "habilidade": "Destrói periodicamente um obstáculo comum à frente.", "tipo": "RAJADA", "raridade": "Lendário", "objetivo": "Destrua 250 obstáculos"},
    "ABELHA_MAGNETICA": {"nome": "Abelha Magnética", "cor": (255, 205, 70), "preco": 16000, "habilidade": "Atrai moedas próximas em pulsos periódicos.", "tipo": "IMA_PULSO", "raridade": "Épico", "objetivo": None},
}

# Preço dos pets adquiríveis; pets de objetivo continuam por objetivo.
for _config_pet_prod in PETS_CONFIG.values():
    if _config_pet_prod['preco']:
        _config_pet_prod['preco'] = int(_config_pet_prod['preco'] * 8)

SKINS_OBJETIVOS = {
    "ROXO": ("Alcance combo 25", "melhor_combo", 25),
    "ROBO": ("Colete 500 power-ups", "powerups", 500),
    "CHAMA": ("Alcance combo 75", "melhor_combo", 75),
    "COSMICA": ("Conclua 100 desafios diários", "desafios_diarios", 100),
    "PLATINA": ("Alcance a patente Platina", "partidas", 500),
}


def objetivo_pet_concluido(pet_id, dados):
    """Mantém os critérios de desbloqueio dos pets já usados pela loja."""
    stats = dados.get("estatisticas_permanentes", {})
    stats_novas = dados.get("estatisticas_novas", {})
    if pet_id == "FANTASMA":
        return int(stats.get("partidas", 0)) >= 100
    if pet_id == "TARTARUGA":
        return int(stats.get("portais_aquaticos", 0)) >= 25
    if pet_id == "DRAGAO":
        return int(stats.get("melhor_combo", 0)) >= 100 and int(stats.get("febres", 0)) >= 100
    if pet_id == "GOLEM":
        return int(stats_novas.get("chefes_derrotados", 0)) >= 10
    if pet_id == "DRAGAO_PLASMA":
        return int(stats.get("obstaculos_destruidos", 0)) >= 250
    if pet_id == "GATO_FANTASMA":
        return int(stats.get("partidas", 0)) >= 50
    return True


def obter_acao_preview_loja(tipo, item_id, dados, confirmar=False):
    """Retorna o rótulo e a ação possível no botão da pré-visualização."""
    if tipo == "SKIN":
        if item_id not in SKINS_ATIVAS_PROD:
            return "EM BREVE", "indisponivel"
        info = SKINS[item_id]
        desbloqueadas = dados.get("skins_desbloqueadas", ["AZUL"])
        if item_id in desbloqueadas:
            return ("EQUIPADA", "equipada") if dados.get("skin_equipada") == item_id else ("EQUIPAR", "equipar")
        objetivo = SKINS_OBJETIVOS.get(item_id)
        if objetivo:
            stats = dados.get("estatisticas_permanentes", {})
            pronto = int(stats.get(objetivo[1], 0)) >= objetivo[2]
            return ("DESBLOQUEAR", "desbloquear") if pronto else ("OBJETIVO PENDENTE", "objetivo_pendente")
        if int(dados.get("moedas_totais", 0)) < int(info["preco"]):
            return "MOEDAS INSUFICIENTES", "sem_moedas"
        return ("CONFIRMAR COMPRA", "comprar_confirmado") if confirmar else ("COMPRAR", "comprar")

    pet = PETS_CONFIG[item_id]
    desbloqueados = dados.get("pets_desbloqueados", [])
    if item_id in desbloqueados:
        equipado = item_id == dados.get("pet_equipado", "")
        return ("EQUIPADO", "equipado") if equipado else ("EQUIPAR", "equipar")
    if pet.get("objetivo"):
        return ("DESBLOQUEAR", "desbloquear") if objetivo_pet_concluido(item_id, dados) else ("OBJETIVO PENDENTE", "objetivo_pendente")
    if int(dados.get("moedas_totais", 0)) < int(pet["preco"]):
        return "MOEDAS INSUFICIENTES", "sem_moedas"
    return ("CONFIRMAR COMPRA", "comprar_confirmado") if confirmar else ("COMPRAR", "comprar")

# Evolução visual da skin equipada: os níveis dependem do XP permanente, sem alterar hitboxes.
SKINS_EVOLUCAO = {
    1: {"xp": 0, "aura": 0},
}

def nivel_visual_skin(dados):
    # Sistema de evolução visual/estilos alternativos removido.
    return 1

# Eventos sazonais locais, definidos pelo mês; sem rede ou relógios em segundo plano.
EVENTOS_SAZONAIS = {
    1: ("Festival das Estrelas", "COSMICA", "Colete 300 moedas durante janeiro", 300, "moedas"),
    2: ("Carnaval Neon", "HOLOGRAFICA", "Percorra 2500 m durante fevereiro", 2500, "distancia"),
    3: ("Despertar da Floresta", "GUARDIAO_VERDE", "Percorra 3000 m durante março", 3000, "distancia"),
    4: ("Chuva de Cristais", "ABISSAL", "Colete 400 moedas durante abril", 400, "moedas"),
    5: ("Festival das Chamas", "MAGMA", "Derrote 3 chefes durante maio", 3, "chefes"),
    6: ("Solstício Dourado", "DOURADO", "Ative 8 modos Febre durante junho", 8, "febres"),
    7: ("Corrida Cósmica", "COMETA", "Percorra 4000 m durante julho", 4000, "distancia"),
    8: ("Desafio Holográfico", "HOLOGRAFICA", "Colete 500 moedas durante agosto", 500, "moedas"),
    9: ("Colheita Prisma", "VERDE", "Percorra 3000 m durante setembro", 3000, "distancia"),
    10: ("Noite dos Fantasmas", "ROXO", "Sobreviva a 10 corridas durante outubro", 10, "partidas"),
    11: ("Festival das Relíquias", "PLATINA", "Derrote 3 chefes durante novembro", 3, "chefes"),
    12: ("Cometa de Inverno", "PLATINA", "Percorra 5000 m durante dezembro", 5000, "distancia"),
}

def preparar_evento_sazonal(dados, hoje=None):
    hoje = hoje or date.today()
    titulo, premio_skin, descricao, alvo, metrica = EVENTOS_SAZONAIS[hoje.month]
    ev = dados.setdefault("evento_sazonal", {})
    chave = f"{hoje.year}-{hoje.month:02d}"
    if ev.get("periodo") != chave:
        ev.update({"periodo": chave, "progresso": 0, "concluido": False, "recompensa_resgatada": False})
    ev.update({"titulo": titulo, "skin": premio_skin, "descricao": descricao, "alvo": alvo, "metrica": metrica})
    return ev

# Novos sistemas v3.14.0: progressão de pets, relíquias e ranking offline.
PETS_EVOLUCAO_MAX = 5
RELIQUIAS_CONFIG = {
    "IMÃ_ANCESTRAL": {"nome": "Ímã Ancestral", "descricao": "+5% moedas em portais", "desbloqueio": "Colete 500 moedas", "stat": "moedas_coletadas", "alvo": 500, "bonus": "MOEDAS", "cor": (90, 210, 255)},
    "CORACAO_FENIX": {"nome": "Coração da Fênix", "descricao": "Uma proteção extra a cada 3 níveis", "desbloqueio": "Sobreviva a 25 corridas", "stat": "partidas", "alvo": 25, "bonus": "ESCUDO", "cor": (255, 115, 65)},
    "NUCLEO_TITAN": {"nome": "Núcleo Titã", "descricao": "+1 ponto de vida contra chefes", "desbloqueio": "Derrote 5 chefes", "stat": "chefes_derrotados", "alvo": 5, "bonus": "CHEFE", "cor": (190, 125, 255)},
    "PEROLA_ABISSAL": {"nome": "Pérola Abissal", "descricao": "+15% recompensas de biomas lendários", "desbloqueio": "Visite 3 biomas lendários", "stat": "biomas_lendarios", "alvo": 3, "bonus": "BIOMA", "cor": (70, 245, 205)},
    "AMPULHETA": {"nome": "Ampulheta do Eco", "descricao": "+10% XP permanente", "desbloqueio": "Alcance 10.000 m totais", "stat": "distancia_total", "alvo": 10000, "bonus": "XP", "cor": (255, 220, 95)},
    "MAPA_ABISSAL": {"nome": "Mapa Abissal", "descricao": "+8% de moedas em rotas arriscadas", "desbloqueio": "Reúna 8 fragmentos de relíquia", "stat": "fragmentos_reliquia", "alvo": 8, "bonus": "MOEDAS", "cor": (70, 205, 255)},
    "ROSA_DOS_VENTOS": {"nome": "Rosa dos Ventos", "descricao": "+8% de XP permanente", "desbloqueio": "Reúna 16 fragmentos de relíquia", "stat": "fragmentos_reliquia", "alvo": 16, "bonus": "XP", "cor": (150, 230, 180)},
}
BIOMAS_LENDARIOS = {
    "CRISTAL": {"nome": "Vale de Cristal", "cor": (90, 235, 255), "recompensa": 1.30, "descricao": "Cristais brilhantes e recompensa aumentada"},
    "LAVA": {"nome": "Reino de Lava", "cor": (255, 100, 45), "recompensa": 1.40, "descricao": "Calor extremo e recompensas maiores"},
    "COSMICO": {"nome": "Vazio Cósmico", "cor": (205, 120, 255), "recompensa": 1.50, "descricao": "Estrelas antigas e bônus lendário"},
}

BIOMAS_RECORDES_UI = (
    ("cidade", "CIDADE"),
    ("deserto", "DESERTO"),
    ("neve", "NEVE"),
    ("cidade_futurista", "CIDADE FUTURISTA"),
)



def nivel_pet(dados, pet_id):
    return max(1, min(PETS_EVOLUCAO_MAX, int(dados.get("evolucao_pets", {}).get(pet_id, {}).get("nivel", 1))))


def adicionar_xp_pet(dados, quantidade):
    pet_id = dados.get("pet_equipado", "")
    if pet_id not in PETS_CONFIG:
        return 0
    evolucoes = dados.setdefault("evolucao_pets", {})
    prog = evolucoes.setdefault(pet_id, {"nivel": 1, "xp": 0})
    prog["xp"] = int(prog.get("xp", 0)) + max(0, int(quantidade))
    niveis_ganhos = 0
    while int(prog.get("nivel", 1)) < PETS_EVOLUCAO_MAX and prog["xp"] >= int(prog.get("nivel", 1)) * 500:
        prog["xp"] -= int(prog.get("nivel", 1)) * 500
        prog["nivel"] = int(prog.get("nivel", 1)) + 1
        niveis_ganhos += 1
    return niveis_ganhos


# Sistema independente de afeto; progressão cosmética, sem efeitos nas habilidades.
LEMBRANCAS_PETS = ((25, "ESTRELINHA", "Estrelinha"),
                  (60, "LACINHO", "Lacinho da Amizade"),
                  (100, "MEDALHA", "Medalha de Companheiro"))


def registro_pet(dados, pet_id):
    if pet_id not in PETS_CONFIG:
        return None
    registros = dados.setdefault("pet_vinculos", {})
    registro = registros.setdefault(pet_id, {"pontos": 0, "data": "", "carinhos": 0,
                                           "brincadeiras": 0, "lembrancas": []})
    for chave, padrao in (("pontos", 0), ("data", ""), ("carinhos", 0),
                          ("brincadeiras", 0), ("lembrancas", [])):
        registro.setdefault(chave, [] if chave == "lembrancas" else padrao)
    hoje = date.today().isoformat()
    if registro["data"] != hoje:
        registro["data"] = hoje
        registro["carinhos"] = 0
        registro["brincadeiras"] = 0
    registro["pontos"] = max(0, min(100, int(registro["pontos"])))
    return registro


def atualizar_vinculo_pet(dados, pet_id, pontos):
    registro = registro_pet(dados, pet_id)
    if registro is None:
        return []
    registro["pontos"] = min(100, registro["pontos"] + max(0, int(pontos)))
    novidades = []
    for alvo, codigo, _rotulo in LEMBRANCAS_PETS:
        if registro["pontos"] >= alvo and codigo not in registro["lembrancas"]:
            registro["lembrancas"].append(codigo)
            novidades.append(codigo)
    return novidades


def interagir_com_pet(dados, pet_id, interacao):
    if pet_id not in dados.get("pets_desbloqueados", []):
        return False, "Desbloqueie este pet na loja."
    registro = registro_pet(dados, pet_id)
    limites = {"carinho": ("carinhos", 3, 4), "brincar": ("brincadeiras", 3, 6)}
    if interacao not in limites:
        return False, "Interação indisponível."
    chave, limite, ganho = limites[interacao]
    if registro[chave] >= limite:
        return True, "O pet já recebeu bastante atenção hoje!"
    registro[chave] += 1
    premios = atualizar_vinculo_pet(dados, pet_id, ganho)
    if premios:
        return True, "Nova lembrança: " + next(n for _a, c, n in LEMBRANCAS_PETS if c == premios[-1])
    return True, ("Carinho recebido!" if interacao == "carinho" else "Hora da brincadeira!") + f" +{ganho} vínculo"


def vinculo_por_corrida(dados, distancia, moedas, febres):
    pet_id = dados.get("pet_equipado", "")
    if pet_id not in PETS_CONFIG:
        return []
    ganho = min(10, 2 + max(0, int(distancia)) // 500 + max(0, int(moedas)) // 100 + min(2, int(febres)))
    return atualizar_vinculo_pet(dados, pet_id, ganho)


def nivel_cosmetico_pet(dados, pet_id):
    """Reusa o nível de XP já existente; não altera as regras de evolução."""
    return nivel_pet(dados, pet_id)


def atualizar_ranking_local(dados, entrada):
    """Guarda somente recordes locais; não usa rede nem dados externos."""
    ranking = dados.setdefault("ranking_local", [])
    ranking.append({k: int(v) for k, v in entrada.items() if k in ("distancia", "moedas", "combo", "chefes", "reliquias")})
    ranking.sort(key=lambda r: (r.get("distancia", 0), r.get("chefes", 0), r.get("combo", 0)), reverse=True)
    del ranking[10:]
    return ranking


DESAFIOS_DIARIOS = [
    ("distancia", "Percorra 1200 metros", "distancia", 1200, 120),
    ("moedas", "Colete 250 moedas", "moedas", 250, 150),
    ("quase", "Faça 8 quase colisões", "quase", 8, 180),
    ("combo", "Alcance combo de 25", "combo", 25, 200),
    ("explorador", "Visite 2 biomas na mesma corrida", "biomas", 2, 180),
]
DESAFIOS_SEMANAIS = [
    ("distancia", "Percorra 12000 metros", "distancia", 12000, 900),
    ("moedas", "Colete 2500 moedas", "moedas", 2500, 1100),
    ("corridas", "Jogue 20 corridas", "corridas", 20, 1200),
    ("quase", "Faça 100 quase colisões", "quase", 100, 1300),
    ("exploracao", "Visite os 4 cenários disponíveis", "biomas", 4, 1600),
]


def chave_periodo_semanal(hoje=None):
    hoje = hoje or date.today()
    iso = hoje.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def preparar_desafios(dados, hoje=None):
    hoje = hoje or date.today()
    dia_key = hoje.isoformat()
    semana_key = chave_periodo_semanal(hoje)
    desafios = dados.setdefault("desafios_periodicos", {})
    if desafios.get("dia") != dia_key:
        idx = (hoje.toordinal() * 7) % len(DESAFIOS_DIARIOS)
        item = DESAFIOS_DIARIOS[idx]
        desafios["dia"] = dia_key
        desafios["diario"] = {"id": item[0], "titulo": item[1], "metrica": item[2], "alvo": item[3], "recompensa": item[4], "progresso": 0, "concluido": False, "resgatado": False}
    if desafios.get("semana") != semana_key:
        idx = (hoje.isocalendar().week * 3) % len(DESAFIOS_SEMANAIS)
        item = DESAFIOS_SEMANAIS[idx]
        desafios["semana"] = semana_key
        desafios["semanal"] = {"id": item[0], "titulo": item[1], "metrica": item[2], "alvo": item[3], "recompensa": item[4], "progresso": 0, "concluido": False, "resgatado": False}
    # Saves antigos podem conter a missão impossível de 5 biomas.
    for _periodo in ('diario','semanal'):
        _desafio = desafios.get(_periodo, {})
        if _desafio.get('id') == 'exploracao' and _desafio.get('alvo',0) > 4:
            _desafio['alvo'] = 4
            _desafio['titulo'] = 'Visite os 4 cenários disponíveis'
    return desafios


def atualizar_desafios_apos_corrida(dados, metricas):
    desafios = preparar_desafios(dados)
    recompensa_total = 0
    for chave in ("diario", "semanal"):
        desafio = desafios[chave]
        metrica = desafio["metrica"]
        desafio["progresso"] = int(desafio.get("progresso", 0)) + int(metricas.get(metrica, 0))
        if not desafio.get("concluido") and desafio["progresso"] >= desafio["alvo"]:
            desafio["concluido"] = True
        if desafio.get("concluido") and not desafio.get("resgatado"):
            desafio["resgatado"] = True
            recompensa_total += int(desafio["recompensa"])
            stats = dados.setdefault("estatisticas_permanentes", {})
            stat = "desafios_diarios" if chave == "diario" else "desafios_semanais"
            stats[stat] = int(stats.get(stat, 0)) + 1
    if recompensa_total:
        dados["moedas_totais"] = int(dados.get("moedas_totais", 0)) + recompensa_total
    return recompensa_total



def carregar_dados():
    dados_padrao = {
        "recorde": 0, "moedas_totais": 0, "skin_equipada": "AZUL", "skins_desbloqueadas": ["AZUL"],
        "upgrades": {"IMA": 0, "TURBO": 0, "ESCUDO": 0, "MULT_2X": 0, "SLOW": 0, "JETPACK": 0, "CLONE": 0, "PRISMA": 0, "CRONO": 0, "TURBO_FANTASMA": 0},
        "vol_sfx": 0.7, "vol_musica": 0.5, "idioma": "pt_BR", "vibracao": True, "modo_grafico": "completo", "acess_contraste": False, "acess_sinais": False, "acess_reduzir_efeitos": False, "ajuda_pulo": True, "rastro_visual": "DESLIGADO", "controle_modo": "CLASSICO", "sensibilidade_toque": 30, "controle_canhoto": False, "gamepad_ativo": True,
        "conquistas_desbloqueadas": [], "skins_compradas_confirmadas": [],
        "recordes_biomas": {"cidade": 0, "deserto": 0, "neve": 0, "vulcao": 0, "cidade_futurista": 0, "floresta": 0, "reino_submerso": 0, "ilhas_celestes": 0},
        "recompensas_biomas": [],
        "pets_desbloqueados": [], "pet_equipado": "",
        "evento_sazonal": {}, "cosmeticos_sazonais": [], "desafios_periodicos": {}, "patente_corridas": 0,
        "evolucao_pets": {}, "pet_vinculos": {}, "reliquias_desbloqueadas": [], "reliquia_equipada": "", "ranking_local": [], "desafios_ranking_concluidos": [],
        "estatisticas_novas": {"chefes_derrotados": 0, "biomas_lendarios": 0, "fragmentos_reliquia": 0},
        "maestria_biomas": {},
        "base_corredor": {"nivel": 1, "trofeus": [], "decoracao": 0, "mecanicas_descobertas": []},
        "estatisticas_permanentes": {
            "partidas": 0, "distancia_total": 0, "moedas_coletadas": 0,
            "quase_colisoes": 0, "bau_abertos": 0, "febres": 0,
            "melhor_combo": 0, "powerups": 0, "fases_bonus": 0,
            "portais_aquaticos": 0, "portais_lasers": 0, "desafios_diarios": 0,
            "desafios_semanais": 0, "pets_desbloqueados": 0, "skins_desbloqueadas": 1,
            "cidade_total": 0, "deserto_total": 0, "neve_total": 0, "vulcao_total": 0, "cidade_futurista_total": 0, "floresta_total": 0, "reino_submerso_total": 0, "ilhas_celestes_total": 0,
            "eventos_vulcao": 0, "febres_cometa": 0,
            "recorde_febres_rodada": 0, "obstaculos_destruidos": 0
        }
    }
    if any(os.path.exists(ARQUIVO_SAVE + s) for s in ("", ".bak", ".bak.1", ".bak.2")):
        try:
            with nullcontext(ler_save_protegido(ARQUIVO_SAVE)) as dados:
                for k, v in dados_padrao.items():
                    if k not in dados: dados[k] = v
                for key_up in dados_padrao["upgrades"]:
                    if key_up not in dados["upgrades"]:
                        dados["upgrades"][key_up] = 0
                for chave, valor in dados_padrao.items():
                    if isinstance(valor, dict):
                        dados.setdefault(chave, {})
                        if isinstance(dados[chave], dict):
                            for subchave, subvalor in valor.items():
                                dados[chave].setdefault(subchave, subvalor)
                dados.setdefault("conquistas_desbloqueadas", [])
                dados.setdefault("recordes_biomas", {"cidade": 0, "deserto": 0, "neve": 0})
                dados.setdefault("recompensas_biomas", [])
                for biome, valor in {"cidade": 0, "deserto": 0, "neve": 0, "vulcao": 0, "cidade_futurista": 0, "floresta": 0, "reino_submerso": 0, "ilhas_celestes": 0}.items():
                    dados["recordes_biomas"].setdefault(biome, valor)
                for chave_stat, valor_stat in {"vulcao_total": 0, "cidade_futurista_total": 0, "floresta_total": 0, "eventos_vulcao": 0, "febres_cometa": 0, "obstaculos_destruidos": 0, "reino_submerso_total": 0, "ilhas_celestes_total": 0}.items():
                    dados["estatisticas_permanentes"].setdefault(chave_stat, valor_stat)
                dados.setdefault("pets_desbloqueados", [])
                dados.setdefault("pet_equipado", "")
                # Saves antigos: o pet secundário não existe mais.
                dados.pop("pet_secundario", None)
                dados.setdefault("evento_sazonal", {})
                dados.setdefault("cosmeticos_sazonais", [])
                dados.setdefault("desafios_periodicos", {})
                dados["modo_grafico"] = "completo"
                dados.setdefault("ajuda_pulo", True)
                dados["rastro_visual"] = "DESLIGADO"
                dados.setdefault("evolucao_pets", {})
                dados.setdefault("pet_vinculos", {})
                dados.setdefault("reliquias_desbloqueadas", [])
                dados.setdefault("reliquia_equipada", "")
                dados.setdefault("ranking_local", [])
                dados.setdefault("desafios_ranking_concluidos", [])
                dados.setdefault("estatisticas_novas", {"chefes_derrotados": 0, "biomas_lendarios": 0})
                dados.setdefault("maestria_biomas", {})
                dados.setdefault("base_corredor", {"nivel": 1, "trofeus": [], "decoracao": 0, "mecanicas_descobertas": []})
                for chave_base, valor_base in {"nivel": 1, "trofeus": [], "decoracao": 0, "mecanicas_descobertas": []}.items():
                    dados["base_corredor"].setdefault(chave_base, valor_base)
                for chave_nova, valor_novo in {"chefes_derrotados": 0, "biomas_lendarios": 0, "fragmentos_reliquia": 0}.items():
                    dados["estatisticas_novas"].setdefault(chave_nova, valor_novo)
                dados.setdefault("patente_corridas", int(dados.get("estatisticas_permanentes", {}).get("partidas", 0)))
                for chave, valor in dados_padrao["estatisticas_permanentes"].items():
                    dados["estatisticas_permanentes"].setdefault(chave, valor)
                # Uma edição antiga concedia VERDE/ROSA/DOURADO automaticamente
                # pelo XP, registrando essas concessões nesta lista. Removemos
                # apenas concessões COM PROVENIÊNCIA, nunca a compra comprovada.
                progresso_legado = dados.pop("colecao_skins", {})
                recebidas_xp = (progresso_legado.get("desbloqueadas_progressao", [])
                                if isinstance(progresso_legado, dict) else [])
                compras = dados.setdefault("skins_compradas_confirmadas", [])
                desbloqueadas = dados.setdefault("skins_desbloqueadas", ["AZUL"])
                for skin_auto in recebidas_xp:
                    # A lista antiga registrava também skins de objetivo dadas
                    # automaticamente no Game Over, sem resgate na loja.
                    if skin_auto in SKINS and skin_auto != "AZUL" and skin_auto not in compras and skin_auto in desbloqueadas:
                        desbloqueadas.remove(skin_auto)
                if dados.get("skin_equipada") not in desbloqueadas:
                    dados["skin_equipada"] = "AZUL"
                dados["skins_desbloqueadas"] = list(dict.fromkeys(["AZUL"] + [k for k in desbloqueadas if k in SKINS]))
                dados["estatisticas_permanentes"]["skins_desbloqueadas"] = len(dados["skins_desbloqueadas"])
                dados.pop("xp_permanente", None)
                dados.pop("nivel_jogador", None)
                preparar_desafios(dados)
                return dados
        except Exception:
            return dados_padrao
    return dados_padrao


def salvar_dados(dados):
    try:
        salvar_save_protegido(ARQUIVO_SAVE, dados)
    except Exception:
        pass



def dev_desbloquear_colecao_completa(dados):
    """Somente edição DEV: habilita coleção para testes no save isolado."""
    if not PIXELRUSH_DEV_BUILD:
        return False
    dados["skins_desbloqueadas"] = list(SKINS.keys())
    dados["pets_desbloqueados"] = list(PETS_CONFIG.keys())
    dados["skins_compradas_confirmadas"] = list(SKINS.keys())
    stats = dados.setdefault("estatisticas_permanentes", {})
    stats["skins_desbloqueadas"] = len(SKINS)
    stats["pets_desbloqueados"] = len(PETS_CONFIG)
    salvar_dados(dados)
    return True


def processar_conquistas(dados):
    """Desbloqueia cada conquista uma única vez e entrega a recompensa permanente."""
    desbloqueadas = dados.setdefault("conquistas_desbloqueadas", [])
    estatisticas = dados.setdefault("estatisticas_permanentes", {})
    novas = []
    for ident, titulo_key, descricao_key, stat_key, alvo, recompensa in CONQUISTAS_CONFIG:
        if ident not in desbloqueadas and int(estatisticas.get(stat_key, 0)) >= alvo:
            desbloqueadas.append(ident)
            dados["moedas_totais"] = int(dados.get("moedas_totais", 0)) + recompensa
            novas.append((ident, recompensa))
    return novas


# --- DESENHADOR DE ÍCONES DE POWER-UPS ---
_ICONES_POWERUP_V397 = {}


def _criar_icone_powerup_v397(tipo):
    """Emblemas pixel-art compactos com contorno, realces e cores por poder."""
    t = pygame.Surface((28, 28), pygame.SRCALPHA)
    esc = (20, 26, 49)
    paleta = {
        "IMA": ((255, 105, 120), (105, 233, 255)),
        "TURBO": ((255, 192, 75), (255, 105, 64)),
        "ESCUDO": ((83, 231, 242), (80, 130, 238)),
        "SLOW": ((167, 241, 129), (80, 188, 186)),
        "MULT_2X": ((255, 121, 203), (181, 91, 241)),
        "JETPACK": ((255, 184, 86), (248, 102, 69)),
        "CLONE": ((167, 234, 248), (103, 151, 248)),
        "PRISMA": ((235, 169, 255), (87, 238, 250)),
        "CRONO": ((180, 236, 255), (102, 166, 244)),
        "TURBO_FANTASMA": ((229, 223, 255), (128, 134, 245)),
    }
    brilho, segundo = paleta.get(tipo, ((245,246,250),(144,176,208)))
    pygame.draw.rect(t, (0,0,0,42), (4, 5, 20, 20), border_radius=6)
    pygame.draw.rect(t, brilho, (1,1,26,26), border_radius=7)
    pygame.draw.rect(t, esc, (2,2,24,24), border_radius=6)
    pygame.draw.rect(t, segundo, (3,3,22,22), border_radius=5)
    pygame.draw.rect(t, (237,247,255,110), (6,5,16,2))
    pygame.draw.rect(t, (255,255,255,36), (4,20,20,3), border_radius=2)
    cx,cy=14,14
    if tipo == "IMA":
        pygame.draw.arc(t, esc, (7,7,14,15), math.pi, 2*math.pi, 6)
        pygame.draw.arc(t, (240,244,251), (7,7,14,15), math.pi, 2*math.pi, 3)
        pygame.draw.rect(t, (250,95,101), (7,8,5,6));pygame.draw.rect(t, (95,222,251), (16,8,5,6))
    elif tipo in ("TURBO", "TURBO_FANTASMA"):
        pygame.draw.polygon(t, esc, ((16,5),(8,15),(13,15),(10,23),(21,12),(16,12)))
        pygame.draw.polygon(t, brilho, ((15,6),(10,14),(15,14),(12,21),(19,12),(14,12)))
    elif tipo in ("ESCUDO", "PRISMA"):
        pygame.draw.polygon(t, esc, ((14,4),(23,9),(21,18),(14,24),(7,18),(5,9)))
        pygame.draw.polygon(t, brilho, ((14,7),(20,10),(19,18),(14,21),(9,17),(8,10)))
        pygame.draw.polygon(t, (244,252,255), ((14,7),(17,11),(14,16),(11,11)))
    elif tipo in ("SLOW", "CRONO"):
        pygame.draw.circle(t, esc, (14,14), 10)
        pygame.draw.circle(t, brilho, (14,14), 8)
        pygame.draw.circle(t, (255,255,255), (14,14), 6, 2)
        pygame.draw.line(t, esc, (14,14), (14,9), 2)
        pygame.draw.line(t, esc, (14,14), (18,16), 2)
        pygame.draw.rect(t, (255,255,255), (12,4,4,2))
    elif tipo == "MULT_2X":
        pygame.draw.rect(t, esc, (5,8,18,12), border_radius=3)
        f = pygame.font.Font(None, 19)
        tt = f.render('2x', True, (250,247,255))
        t.blit(tt, (14-tt.get_width()//2,14-tt.get_height()//2))
    elif tipo == "JETPACK":
        pygame.draw.rect(t, esc, (8,6,12,15), border_radius=2)
        pygame.draw.rect(t, (236,248,253), (10,7,8,11))
        pygame.draw.rect(t, (244,106,70), (11,9,6,7))
        pygame.draw.polygon(t, (255,235,137), ((11,20),(14,26),(17,20)))
        pygame.draw.polygon(t, (255,129,57), ((12,20),(14,24),(16,20)))
    elif tipo == "CLONE":
        for dx,dy in ((8,12),(15,7),(19,15)):
            pygame.draw.rect(t, esc, (dx-4,dy-4,8,7))
            pygame.draw.rect(t, brilho, (dx-3,dy-3,6,5))
            pygame.draw.rect(t, segundo, (dx-5,dy+3,10,6))
    pygame.draw.rect(t, (255,255,255,160), (6,5,5,2))
    return t.convert_alpha()


def desenhar_icone_powerup(surface, tipo, x, y):
    icone = _ICONES_POWERUP_V397.get(tipo)
    if icone is None:
        icone = _criar_icone_powerup_v397(tipo)
        _ICONES_POWERUP_V397[tipo] = icone
    surface.blit(icone, (int(x)-14,int(y)-14))


# --- SPRITES PIXEL-ART ANIMADOS DOS 9 PETS (v3.31.0) ---
# Arte desenhada em superficies pequenas e cacheada uma unica vez por pet.
# Nenhum arquivo externo, filtro suave, rotacao ou Surface nova por frame.
_PET_SPRITES_CACHE = {}
_PET_CORRIDA_CACHE = {}
_PET_MINI_CACHE = {}
_PET_PREVIEW_CACHE = {}
_PET_TAMANHO = (64, 56)


def _criar_quadro_pet(pet_id, fase):
    """Desenha um quadro original com silhueta, olhos e aderecos da especie."""
    s = pygame.Surface(_PET_TAMANHO, pygame.SRCALPHA)
    esc = (17, 23, 46)
    branco = (244, 251, 255)
    brilho = (178, 251, 255)
    fase %= 4
    balanco = (0, -1, 0, 1)[fase]
    pata = (0, 2, 0, -2)[fase]
    asa = (-5, 0, 5, -1)[fase]

    def r(x, y, w, h, cor):
        pygame.draw.rect(s, cor, (x, y + balanco, w, h))

    def c(x, y, raio, cor):
        pygame.draw.circle(s, cor, (x, y + balanco), raio)

    def e(x, y, w, h, cor):
        pygame.draw.ellipse(s, cor, (x, y + balanco, w, h))

    def p(pontos, cor):
        pygame.draw.polygon(s, cor, [(x, y + balanco) for x, y in pontos])

    def l(pontos, cor, largura=2):
        pygame.draw.lines(s, cor, False, [(x, y + balanco) for x, y in pontos], largura)

    def olho(x, y, tamanho=4, cor_iris=(31, 36, 67)):
        e(x - tamanho, y - tamanho, tamanho * 2 + 1, tamanho * 2 + 2, esc)
        e(x - tamanho + 1, y - tamanho + 1, tamanho * 2 - 1, tamanho * 2, branco)
        r(x, y - 1, max(2, tamanho - 1), tamanho + 1, cor_iris)
        r(x, y - 2, 2, 2, branco)

    def estrela(x, y, cor):
        r(x - 1, y - 4, 2, 8, cor)
        r(x - 4, y - 1, 8, 2, cor)

    if pet_id == 'BOLHA':
        azul = (28, 168, 241)
        claro = (115, 236, 255)
        c(16 + fase % 2, 12, 5, (18, 100, 190))
        c(16 + fase % 2, 12, 3, claro)
        c(50, 40 - fase % 2 * 2, 4, (30, 147, 221))
        c(50, 40 - fase % 2 * 2, 2, branco)
        c(32, 29, 21, esc)
        c(32, 28, 19, (11, 119, 220))
        c(31, 26, 16, azul)
        e(18, 10, 17, 12, claro)
        r(21, 11, 7, 3, branco)
        olho(26, 29, 3)
        olho(39, 29, 3)
        l([(30, 37), (34, 39), (38, 36)], (20, 88, 159), 2)
        r(45, 15, 4, 5, claro)
        estrela(13, 37, (139, 235, 255))
    elif pet_id == 'RAPOSA':
        laranja = (252, 123, 35)
        fogo = (255, 199, 74)
        # Cauda volumosa, ponta branca, pernas alternando e corpo alongado.
        p([(24, 38), (8, 42 - pata), (3, 34 - pata), (6, 23 - pata), (15, 30), (22, 27), (31, 35)], esc)
        p([(23, 36), (9, 39 - pata), (6, 33 - pata), (9, 26 - pata), (17, 32), (24, 30)], laranja)
        p([(9, 28 - pata), (6, 34 - pata), (10, 39 - pata), (16, 39 - pata), (14, 32 - pata)], branco)
        e(23, 29, 27, 16, esc)
        e(25, 30, 23, 13, laranja)
        r(27, 41 + pata, 8, 7, esc)
        r(28, 41 + pata, 6, 5, laranja)
        r(41, 41 - pata, 8, 7, esc)
        r(42, 41 - pata, 6, 5, laranja)
        p([(35, 21), (37, 8), (45, 16), (53, 7), (55, 25)], esc)
        p([(37, 22), (39, 12), (45, 20), (51, 12), (52, 24)], laranja)
        r(40, 14, 3, 6, (255, 169, 174))
        r(50, 13, 3, 7, (255, 169, 174))
        e(34, 18, 23, 22, esc)
        e(36, 19, 20, 19, laranja)
        p([(39, 31), (48, 28), (59, 31), (54, 39), (44, 40)], branco)
        olho(47, 26, 3)
        r(56, 32, 4, 3, esc)
        r(35, 34, 6, 3, fogo)
        if fase in (1, 3):
            r(3, 27, 4, 2, fogo)
            r(7, 20, 4, 2, (255, 101, 38))
    elif pet_id == 'FANTASMA':
        roxo = (154, 78, 246)
        lavanda = (212, 147, 255)
        # Rastro flutuante com borda violeta e rosto de susto (boca O).
        p([(18, 24), (8, 29), (15, 35), (7, 41), (22, 43), (30, 48), (40, 44), (48, 46), (50, 35)], esc)
        p([(18, 25), (12, 29), (20, 34), (13, 40), (24, 40), (31, 45), (40, 41), (46, 43), (47, 34)], roxo)
        e(18, 9, 33, 36, esc)
        e(20, 11, 29, 32, roxo)
        e(24, 13, 20, 19, lavanda)
        r(27, 14, 11, 4, (235, 194, 255))
        e(26, 24, 8, 12, branco)
        e(39, 24, 8, 12, branco)
        r(30, 28, 3, 5, esc)
        r(43, 28, 3, 5, esc)
        e(34, 35, 8, 10, esc)
        r(37, 38, 2, 3, (71, 28, 111))
        c(12, 15, 3, lavanda)
        estrela(54, 17 + fase % 2, lavanda)
        r(14, 45, 3, 3, (128, 54, 218))
    elif pet_id == 'TARTARUGA':
        turq = (44, 205, 208)
        casco = (68, 59, 174)
        e(9, 36 + pata, 15, 10, esc)
        e(11, 37 + pata, 12, 7, turq)
        e(29, 37 - pata, 16, 10, esc)
        e(31, 38 - pata, 12, 7, turq)
        p([(12, 27), (6, 25), (12, 19), (18, 24)], turq)
        e(12, 15, 37, 30, esc)
        e(15, 16, 32, 26, casco)
        p([(20, 19), (31, 16), (42, 24), (34, 31), (19, 27)], (37, 161, 207))
        p([(21, 31), (33, 30), (43, 32), (35, 39), (17, 37)], (40, 111, 170))
        l([(29, 19), (32, 29), (25, 38)], (137, 245, 235), 2)
        l([(18, 29), (41, 30)], (179, 111, 254), 2)
        p([(40, 27), (49, 24), (57, 27), (59, 33), (56, 40), (44, 39)], esc)
        p([(42, 28), (50, 26), (56, 29), (57, 34), (54, 38), (43, 37)], turq)
        olho(52, 31, 3)
        r(53, 38, 4, 2, (24, 116, 151))
        c(9, 12, 4, (39, 180, 240))
        c(9, 12, 2, brilho)
        c(51, 11 + fase % 2, 3, (123, 238, 255))
    elif pet_id == 'GOLEM':
        rocha = (65, 60, 81)
        grafite = (36, 39, 58)
        lava = (255, 137, 38)
        e(10, 22, 16, 24, esc)
        e(13, 22, 14, 21, rocha)
        e(40, 22, 16, 24, esc)
        e(40, 24, 13, 19, rocha)
        r(18, 36 + pata, 12, 13, esc)
        r(20, 38 + pata, 9, 9, grafite)
        r(37, 36 - pata, 12, 13, esc)
        r(39, 38 - pata, 9, 9, grafite)
        p([(20, 21), (16, 13), (28, 8), (36, 12), (46, 9), (52, 19), (50, 41), (18, 41)], esc)
        p([(21, 20), (20, 15), (28, 11), (36, 16), (45, 13), (49, 20), (48, 39), (21, 39)], rocha)
        p([(25, 13), (29, 9), (35, 14), (43, 10), (46, 16), (39, 20), (28, 19)], (92, 84, 98))
        l([(24, 25), (30, 28), (27, 35), (34, 38)], lava, 2)
        l([(46, 22), (40, 27), (44, 34)], lava, 2)
        l([(15, 29), (20, 34)], (255, 203, 55), 2)
        r(26, 23, 7, 6, esc)
        r(39, 23, 7, 6, esc)
        r(28, 24, 5, 4, (255, 214, 72))
        r(40, 24, 5, 4, (255, 214, 72))
        r(30, 25, 3, 3, branco)
        r(42, 25, 3, 3, branco)
        r(8, 42, 4, 2, lava)
    elif pet_id == 'BEIJA_FLOR':
        # Bico longo, corpo aerodinamico fino, cauda e asas de plumagem prisma.
        p([(24, 30), (5, 44), (15, 39), (8, 50), (28, 37)], esc)
        p([(24, 31), (9, 43), (19, 39), (14, 45), (28, 35)], (176, 83, 238))
        p([(25, 30), (12, 47), (27, 37)], (42, 202, 241))
        p([(23, 28), (12, 18 + asa), (19, 7 + asa), (33, 23)], esc)
        p([(24, 28), (15, 18 + asa), (20, 10 + asa), (31, 23)], (139, 86, 251))
        p([(24, 27), (17, 21 + asa), (23, 12 + asa), (32, 26)], (58, 227, 247))
        p([(31, 28), (28, 10 - asa), (39, 8 - asa), (43, 22)], esc)
        p([(32, 28), (31, 13 - asa), (38, 12 - asa), (41, 25)], (246, 92, 218))
        p([(32, 26), (34, 16 - asa), (39, 16 - asa), (40, 24)], (150, 252, 255))
        e(22, 27, 27, 15, esc)
        e(24, 28, 24, 12, (30, 191, 221))
        p([(29, 35), (39, 30), (48, 35), (38, 40)], (236, 244, 255))
        e(38, 20, 15, 16, esc)
        e(40, 22, 12, 12, (57, 224, 232))
        p([(49, 27), (63, 30), (49, 32)], esc)
        p([(50, 28), (62, 30), (50, 30)], (252, 215, 108))
        olho(47, 26, 2)
        r(36, 23, 3, 3, (236, 116, 255))
        estrela(11, 9 + (fase % 2 * 2), (104, 255, 241))
    elif pet_id in ('DRAGAO', 'DRAGAO_PLASMA'):
        plasma = pet_id == 'DRAGAO_PLASMA'
        corpo = (38, 161, 242) if plasma else (58, 49, 170)
        claro = (92, 245, 255) if plasma else (206, 75, 246)
        asa_a = (38, 235, 255) if plasma else (194, 55, 255)
        asa_b = (85, 106, 255) if plasma else (31, 212, 245)
        # Asa superior ampla (e articulada), borda recortada e membrana brilhante.
        p([(30, 29), (16, 10 + asa), (12, 18 + asa), (4, 12 + asa), (10, 36), (20, 28), (22, 37)], esc)
        p([(29, 28), (16, 13 + asa), (14, 22 + asa), (7, 17 + asa), (12, 33), (21, 26), (24, 34)], asa_a)
        l([(15, 15 + asa), (22, 29), (9, 18 + asa)], asa_b, 2)
        p([(36, 26), (34, 4 - asa), (43, 13 - asa), (49, 4 - asa), (52, 30), (43, 39)], esc)
        p([(37, 26), (36, 9 - asa), (43, 16 - asa), (48, 9 - asa), (49, 30), (42, 35)], asa_b)
        l([(43, 15 - asa), (42, 32)], asa_a, 2)
        # Cauda com cristas neon.
        p([(25, 37), (14, 41), (8, 37), (11, 46), (22, 49), (34, 41)], esc)
        p([(23, 38), (15, 43), (12, 41), (15, 46), (25, 46), (35, 41)], corpo)
        p([(13, 42), (7, 35), (19, 38)], claro)
        # Pernas alternadas e torso.
        r(29, 40 + pata, 8, 9, esc)
        r(31, 41 + pata, 6, 7, corpo)
        r(42, 40 - pata, 9, 9, esc)
        r(43, 41 - pata, 6, 7, corpo)
        e(24, 25, 28, 20, esc)
        e(26, 27, 25, 17, corpo)
        p([(36, 34), (48, 31), (49, 44), (35, 42)], claro)
        # Cristas espinhosas e chifres.
        p([(34, 25), (27, 16), (39, 22)], claro)
        p([(42, 23), (40, 11), (49, 20)], asa_a)
        e(40, 18, 16, 18, esc)
        e(42, 19, 13, 16, corpo)
        p([(48, 28), (62, 29), (60, 39), (52, 39), (48, 36)], esc)
        p([(49, 29), (60, 31), (58, 36), (51, 36)], corpo)
        # Dentes afiados visiveis, expressao forte e brilho de plasma.
        p([(51, 36), (54, 41), (56, 36)], branco)
        p([(57, 36), (59, 40), (60, 35)], branco)
        olho(50, 27, 3, (242, 94, 253) if plasma else (30, 228, 247))
        r(56, 32, 3, 2, claro)
        if plasma:
            l([(5, 29), (12, 25), (8, 21), (17, 17)], (151, 250, 255), 2)
            l([(53, 8), (59, 12), (55, 16), (62, 20)], (85, 247, 255), 2)
            estrela(8, 7 + fase % 2, (167, 255, 255))
            r(28, 35, 3, 3, (247, 129, 255))
        else:
            estrela(11, 7 + fase % 2, (248, 86, 255))
            r(30, 37, 3, 3, (103, 236, 255))
    elif pet_id == 'ABELHA_MAGNETICA':
        amarelo = (255, 212, 56)
        mel = (255, 156, 27)
        # Imã em ferradura com polos coloridos.
        r(7, 32, 4, 8, (255, 86, 102))
        r(7, 36, 13, 5, (45, 213, 245))
        r(16, 32, 4, 8, (255, 86, 102))
        r(9, 33, 3, 5, amarelo)
        r(15, 33, 3, 5, amarelo)
        c(13, 27, 2, (117, 245, 255))
        # Asas rapidas com dois angulos alternados.
        e(27, 13 + asa, 16, 19, esc)
        e(29, 14 + asa, 13, 16, (126, 226, 249))
        e(38, 9 - asa, 16, 23, esc)
        e(40, 11 - asa, 13, 19, branco)
        r(42, 14 - asa, 6, 3, (181, 243, 255))
        # Corpo abelha listrado e cabeca sorridente.
        p([(15, 33), (12, 37), (16, 41), (22, 35)], esc)
        e(16, 25, 35, 20, esc)
        e(18, 27, 32, 16, amarelo)
        r(23, 27, 7, 16, esc)
        r(36, 26, 6, 18, esc)
        r(25, 30, 3, 6, (84, 65, 53))
        e(42, 23, 17, 20, esc)
        e(43, 25, 15, 17, amarelo)
        r(46, 28, 3, 3, mel)
        olho(52, 31, 3)
        r(55, 38, 3, 2, (136, 68, 34))
        l([(46, 25), (43, 18), (40, 16)], esc, 2)
        l([(54, 24), (56, 17), (58, 15)], esc, 2)
        c(40, 16, 3, (98, 244, 255))
        c(58, 15, 3, (98, 244, 255))
        estrela(9, 14 + (fase % 2 * 2), (114, 243, 255))
        r(29, 48, 3, 2, mel)
    else:
        # Fallback futuro sem criar dependencia ou quebrar a loja.
        c(32, 28, 18, esc)
        c(32, 27, 16, (80, 205, 255))
        olho(27, 27, 3)
        olho(39, 27, 3)
    return s


def _criar_quadro_pet_animado(pet_id, fase, modo="andar"):
    """Aplica acabamento premium sobre a arte base: sombra, expressão e leve acting."""
    fase8 = fase % 8
    base = _criar_quadro_pet(pet_id, fase8 % 4).copy()
    tela = pygame.Surface(_PET_TAMANHO, pygame.SRCALPHA)
    if modo == "ocioso":
        off_y = (0, 0, -1, -1, -2, -1, -1, 0)[fase8]
        off_x = (-1, 0, 1, 1, 0, -1, -1, 0)[fase8] if pet_id in ("RAPOSA", "BEIJA_FLOR", "DRAGAO", "DRAGAO_PLASMA") else 0
    elif modo == "reacao":
        off_y = (0, -2, -1, 0, 1, 0, -1, -2)[fase8]
        off_x = (0, 1, 0, -1, 0, 1, 0, -1)[fase8]
    else:
        off_y = (0, -1, 0, 1, 0, -1, 0, 1)[fase8]
        off_x = 0
    pygame.draw.ellipse(tela, (0, 0, 0, 75), (12, 44 + max(-1, off_y // 2), 38, 7))
    tela.blit(base, (off_x, off_y))

    rosto = {
        "BOLHA": (32, 30), "RAPOSA": (47, 28), "FANTASMA": (36, 30), "TARTARUGA": (52, 32),
        "GOLEM": (36, 26), "BEIJA_FLOR": (47, 27), "DRAGAO": (50, 28), "DRAGAO_PLASMA": (50, 28),
        "ABELHA_MAGNETICA": (52, 32),
    }
    cheeks = {
        "BOLHA": ((24, 33), (40, 33)), "RAPOSA": ((41, 31), (54, 31)), "FANTASMA": ((28, 34), (44, 34)),
        "TARTARUGA": ((47, 35), (57, 35)), "BEIJA_FLOR": ((42, 30), (51, 30)), "ABELHA_MAGNETICA": ((47, 36), (57, 36))
    }
    if pet_id in cheeks:
        for cx, cy in cheeks[pet_id]:
            pygame.draw.ellipse(tela, (255, 182, 204, 110), (cx - 3 + off_x, cy - 2 + off_y, 7, 5))

    if pet_id in rosto and ((modo == "ocioso" and fase8 == 5) or (modo == "reacao" and fase8 in (1, 5))):
        rx, ry = rosto[pet_id]
        if pet_id in ("GOLEM", "DRAGAO", "DRAGAO_PLASMA"):
            pygame.draw.line(tela, (255, 240, 140), (rx - 9 + off_x, ry - 1 + off_y), (rx - 4 + off_x, ry + 1 + off_y), 2)
            pygame.draw.line(tela, (255, 240, 140), (rx + 3 + off_x, ry + 1 + off_y), (rx + 8 + off_x, ry - 1 + off_y), 2)
        else:
            pygame.draw.line(tela, (40, 44, 70), (rx - 8 + off_x, ry + off_y), (rx - 3 + off_x, ry + 1 + off_y), 2)
            pygame.draw.line(tela, (40, 44, 70), (rx + 2 + off_x, ry + 1 + off_y), (rx + 7 + off_x, ry + off_y), 2)
            pygame.draw.arc(tela, (60, 80, 100), (rx - 5 + off_x, ry + 4 + off_y, 10, 6), 0.2, math.pi - 0.2, 1)

    brilho_cor = {
        "BOLHA": (178, 251, 255), "RAPOSA": (255, 208, 118), "FANTASMA": (218, 167, 255), "TARTARUGA": (114, 238, 252),
        "GOLEM": (255, 171, 82), "BEIJA_FLOR": (123, 255, 239), "DRAGAO": (255, 118, 245), "DRAGAO_PLASMA": (138, 250, 255),
        "ABELHA_MAGNETICA": (146, 248, 255),
    }.get(pet_id, (220, 220, 220))
    for i in range(2 + (modo == "reacao")):
        bx = 8 + ((fase8 * 7 + i * 17 + len(pet_id)) % 48)
        by = 8 + ((fase8 * 5 + i * 11) % 32)
        pygame.draw.line(tela, brilho_cor, (bx, by), (bx + 2, by), 1)
        pygame.draw.line(tela, brilho_cor, (bx + 1, by - 1), (bx + 1, by + 1), 1)
    # Microdetalhes de espécie: todos ficam embutidos nos quadros já cacheados.
    if pet_id == 'BOLHA':
        pygame.draw.circle(tela, (216, 251, 255), (22+off_x, 18+off_y), 4, 1)
        pygame.draw.rect(tela, (255, 255, 255), (19+off_x, 14+off_y, 2, 2))
    elif pet_id == 'RAPOSA':
        pygame.draw.line(tela, (255, 234, 176), (24+off_x, 19+off_y), (27+off_x, 17+off_y), 2)
    elif pet_id == 'FANTASMA':
        pygame.draw.circle(tela, (249, 217, 255), (29+off_x, 16+off_y), 2)
    elif pet_id == 'TARTARUGA':
        pygame.draw.rect(tela, (152, 252, 229), (25+off_x, 21+off_y, 4, 3))
    elif pet_id == 'GOLEM':
        pygame.draw.line(tela, (255, 185, 82), (27+off_x, 20+off_y), (31+off_x, 24+off_y), 2)
    elif pet_id == 'BEIJA_FLOR':
        pygame.draw.line(tela, (235, 255, 202), (29+off_x, 18+off_y), (40+off_x, 12+off_y), 1)
    elif pet_id in ('DRAGAO', 'DRAGAO_PLASMA'):
        linha = (255, 151, 241) if pet_id == 'DRAGAO' else (125, 250, 255)
        pygame.draw.line(tela, linha, (22+off_x, 21+off_y), (27+off_x, 16+off_y), 1)
    elif pet_id == 'ABELHA_MAGNETICA':
        pygame.draw.arc(tela, (129, 246, 255), (22+off_x, 11+off_y, 21, 16), 0.3, 2.6, 1)
    # O acabamento é aplicado durante a geração dos quadros (nunca no loop da corrida).
    _, luz, sombra = PALETAS_SPRITES_PREMIUM[familia_visual_pet(pet_id)]
    brilho = {'BOLHA': (25, 14), 'RAPOSA': (44, 15), 'FANTASMA': (34, 17),
              'TARTARUGA': (31, 20), 'DRAGAO': (45, 19), 'GOLEM': (30, 13),
              'BEIJA_FLOR': (41, 19), 'DRAGAO_PLASMA': (46, 19),
              'ABELHA_MAGNETICA': (46, 20)}.get(pet_id, (31, 18))
    pygame.draw.rect(tela, luz, (brilho[0] + off_x, brilho[1] + off_y, 3, 2))
    pygame.draw.rect(tela, sombra, (brilho[0] + off_x + 1, brilho[1] + off_y + 3, 2, 1))
    return tela



# --- FOLHAS EXTERNAS DE SPRITES DOS PETS ---
# Usa exatamente as artes aprovadas pelo usuário. Sem redrawing: o jogo passa a
# recortar e reaproveitar as folhas completas de sprites com transparência.
_PET_SPRITE_SHEET_CACHE = {}
_PET_SPRITE_SHEET_FRAMES = {}

PET_SPRITE_SHEETS = {
    "BOLHA": ("sheet_pets_1.png", 0),
    "RAPOSA": ("sheet_pets_1.png", 1),
    "FANTASMA": ("sheet_pets_1.png", 2),
    "TARTARUGA": ("sheet_pets_2.png", 0),
    "DRAGAO": ("sheet_pets_2.png", 1),
    "GOLEM": ("sheet_pets_2.png", 2),
    "BEIJA_FLOR": ("sheet_pets_3.png", 0),
    "DRAGAO_PLASMA": ("sheet_pets_3.png", 1),
    "ABELHA_MAGNETICA": ("sheet_pets_3.png", 2),
}

# Recortes calibrados a partir das folhas 1448x1086 aprovadas na conversa.
PET_SHEET_ROW_RANGES = (
    (109, 354),   # linha 1
    (421, 699),   # linha 2
    (764, 1055),  # linha 3
)
PET_SHEET_X_RANGES = {
    "PORTRAIT": (8, 214),
    "IDLE": (224, 331),
    "CORRER": (333, 463),
    "PULO": (474, 582),
    "QUEDA": (584, 698),
    "AGACHAR": (709, 812),
    "ALERTA": (823, 920),
    "HABILIDADE": (925, 1076),
    "FELIZ": (1088, 1190),
    "DORMIR": (1201, 1312),
    "MORTE": (1322, 1432),
}

# Cada folha tem colunas ligeiramente diferentes. A corrida tem DOIS
# quadros lado a lado por linha (seis ao todo), não um quadro duplo.
# A calibração preserva a pintura original sem incluir sprites vizinhos.
PET_SHEET_X_RANGES_POR_FOLHA = {
    "sheet_pets_1.png": {
        "PORTRAIT": (4, 213), "IDLE": (220, 324), "CORRER": (325, 465),
        "PULO": (466, 580), "QUEDA": (582, 690), "AGACHAR": (693, 799),
        "ALERTA": (799, 906), "HABILIDADE": (907, 1055), "FELIZ": (1057, 1170),
        "DORMIR": (1172, 1287), "MORTE": (1289, 1400),
    },
    "sheet_pets_2.png": {
        "PORTRAIT": (2, 252), "IDLE": (252, 353), "CORRER": (354, 478),
        "PULO": (479, 582), "QUEDA": (585, 697), "AGACHAR": (699, 800),
        "ALERTA": (802, 904), "HABILIDADE": (905, 1065), "FELIZ": (1067, 1170),
        "DORMIR": (1172, 1286), "MORTE": (1288, 1404),
    },
    "sheet_pets_3.png": {
        "PORTRAIT": (2, 254), "IDLE": (254, 357), "CORRER": (358, 490),
        "PULO": (492, 599), "QUEDA": (600, 707), "AGACHAR": (708, 817),
        "ALERTA": (818, 919), "HABILIDADE": (920, 1072), "FELIZ": (1073, 1172),
        "DORMIR": (1173, 1284), "MORTE": (1285, 1404),
    },
}


def _pet_sheet_search_paths(nome_arquivo):
    base = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    candidatos = [
        os.path.join(base, nome_arquivo),
        os.path.join('/mnt/data', nome_arquivo),
    ]
    return candidatos


def _carregar_folha_pet(nome_arquivo):
    folha = _PET_SPRITE_SHEET_CACHE.get(nome_arquivo)
    if folha is not None:
        return folha
    for caminho in _pet_sheet_search_paths(nome_arquivo):
        if os.path.exists(caminho):
            try:
                folha = pygame.image.load(caminho).convert_alpha()
                _PET_SPRITE_SHEET_CACHE[nome_arquivo] = folha
                return folha
            except Exception:
                pass
    return None


def _copiar_recorte(surf, rect):
    novo = pygame.Surface((max(1, rect.width), max(1, rect.height)), pygame.SRCALPHA)
    novo.blit(surf, (0, 0), rect)
    return novo.convert_alpha()


def _aparar_alpha(surf, pad=1):
    if surf is None:
        return pygame.Surface((2, 2), pygame.SRCALPHA).convert_alpha()
    mask = pygame.mask.from_surface(surf, 8)
    componentes = mask.connected_components()
    if componentes:
        maior = max(componentes, key=lambda comp: comp.count())
        rects = maior.get_bounding_rects()
        bbox = rects[0] if rects else maior.get_rect()
        # infla um pouco para preservar partículas/acessórios próximos do sprite principal
        bbox.inflate_ip(max(6, pad * 6), max(6, pad * 6))
    else:
        try:
            bbox = surf.get_bounding_rect(min_alpha=8)
        except TypeError:
            bbox = surf.get_bounding_rect()
    if bbox.width <= 0 or bbox.height <= 0:
        return pygame.Surface((2, 2), pygame.SRCALPHA).convert_alpha()
    bbox.x = max(0, bbox.x)
    bbox.y = max(0, bbox.y)
    bbox.width = min(surf.get_width() - bbox.x, bbox.width)
    bbox.height = min(surf.get_height() - bbox.y, bbox.height)
    return _copiar_recorte(surf, bbox)


def _ajustar_sequencia_animacao(seq, minimo=4):
    if not seq:
        return tuple()
    if len(seq) >= minimo:
        return tuple(frame.convert_alpha() for frame in seq)
    if len(seq) == 1:
        base = [seq[0], seq[0], seq[0], seq[0]]
    elif len(seq) == 2:
        base = [seq[0], seq[1], seq[0], seq[1]]
    else:
        base = [seq[0], seq[1], seq[2], seq[1]]
    return tuple(frame.convert_alpha() for frame in base)



def _extrair_estado_vertical(surf, nome_estado, x_ranges=None):
    x0, x1 = (x_ranges or PET_SHEET_X_RANGES)[nome_estado]
    zona = _copiar_recorte(surf, pygame.Rect(x0, 0, x1 - x0, surf.get_height()))
    frames = []
    por_linha = 2 if nome_estado == "CORRER" else 1
    for i in range(3):
        top = int(i * zona.get_height() / 3)
        bottom = int((i + 1) * zona.get_height() / 3)
        faixa = _copiar_recorte(zona, pygame.Rect(0, top, zona.get_width(), max(1, bottom - top)))
        mask = pygame.mask.from_surface(faixa, 8)
        componentes = list(mask.connected_components())
        caixas = []
        for comp in componentes:
            rects = comp.get_bounding_rects()
            if not rects:
                continue
            rect = rects[0]
            # ignora brilhos minúsculos/ruído da folha
            if rect.width * rect.height < 90:
                continue
            caixas.append(rect)
        if caixas:
            # seleciona os maiores corpos/poses e ordena da esquerda para a direita
            caixas = sorted(caixas, key=lambda r: r.width * r.height, reverse=True)[:por_linha]
            caixas = sorted(caixas, key=lambda r: r.x)
            for rect in caixas:
                pad = 4 if nome_estado == "CORRER" else 3
                rect.inflate_ip(pad * 2, pad * 2)
                rect.x = max(0, rect.x)
                rect.y = max(0, rect.y)
                rect.width = min(faixa.get_width() - rect.x, rect.width)
                rect.height = min(faixa.get_height() - rect.y, rect.height)
                frames.append(_aparar_alpha(_copiar_recorte(faixa, rect), 1))
        else:
            # fallback antigo caso a detecção por componentes falhe
            colunas = por_linha
            for col in range(colunas):
                x_ini = int(col * faixa.get_width() / colunas)
                x_fim = int((col + 1) * faixa.get_width() / colunas)
                cell = _copiar_recorte(faixa, pygame.Rect(x_ini, 0,
                                                         max(1, x_fim - x_ini),
                                                         faixa.get_height()))
                frames.append(_aparar_alpha(cell, 1))
    return tuple(frame.convert_alpha() for frame in frames)


def _frames_pet_folha(pet_id):
    atual = _PET_SPRITE_SHEET_FRAMES.get(pet_id)
    if atual is not None:
        return atual
    info = PET_SPRITE_SHEETS.get(pet_id)
    if not info:
        _PET_SPRITE_SHEET_FRAMES[pet_id] = None
        return None
    nome_arquivo, indice_linha = info
    folha = _carregar_folha_pet(nome_arquivo)
    if folha is None:
        _PET_SPRITE_SHEET_FRAMES[pet_id] = None
        return None
    y0, y1 = PET_SHEET_ROW_RANGES[indice_linha]
    linha = _copiar_recorte(folha, pygame.Rect(0, y0, folha.get_width(), y1 - y0))
    extraidos = {}
    x_ranges = PET_SHEET_X_RANGES_POR_FOLHA.get(nome_arquivo, PET_SHEET_X_RANGES)
    # Portrait grande, usado na loja/cantinho para manter a arte aprovada.
    px0, px1 = x_ranges["PORTRAIT"]
    if pet_id == "RAPOSA":
        # O rosto ultrapassa a antiga coluna 214. A componente alfa evita
        # pegar sprites vizinhos e mantém o focinho e as duas orelhas inteiros.
        px1 = 243
    # Uma sombra do cabeçalho da segunda folha invade o retrato do Dragão Neon.
    # Descarta somente essa faixa transparente/de letreiro, sem alterar a arte.
    margem_topo = 14 if pet_id == "DRAGAO" else 0
    extraidos["PORTRAIT"] = (_aparar_alpha(_copiar_recorte(
        linha, pygame.Rect(px0, margem_topo, px1 - px0, linha.get_height() - margem_topo)), 2),)
    for estado in ("IDLE", "CORRER", "PULO", "QUEDA", "AGACHAR", "ALERTA", "HABILIDADE", "FELIZ", "DORMIR", "MORTE"):
        extraidos[estado] = _extrair_estado_vertical(linha, estado, x_ranges)
    _PET_SPRITE_SHEET_FRAMES[pet_id] = extraidos
    return extraidos



def _quadros_pet(pet_id):
    """Retorna corrida, morte, ocioso e reação do pet.

    Quando as folhas premium estão presentes, elas têm prioridade total para que o
    jogo use exatamente as artes aprovadas. Se algum arquivo não estiver presente,
    cai automaticamente no desenho procedural antigo.
    """
    cache = _PET_SPRITES_CACHE.get(pet_id)
    if cache is not None:
        return cache
    externos = _frames_pet_folha(pet_id)
    if externos is not None:
        andando = _ajustar_sequencia_animacao(externos.get("CORRER", externos.get("IDLE", ())))
        ocioso = _ajustar_sequencia_animacao(externos.get("IDLE", ()))
        reacao = _ajustar_sequencia_animacao(externos.get("FELIZ", externos.get("ALERTA", ocioso)))
        morrendo = _ajustar_sequencia_animacao(externos.get("MORTE", ()), minimo=3)
        cache = (andando, morrendo, ocioso, reacao)
        _PET_SPRITES_CACHE[pet_id] = cache
        return cache
    andando = tuple(_criar_quadro_pet_animado(pet_id, quadro, "andar").convert_alpha() for quadro in range(8))
    ocioso = tuple(_criar_quadro_pet_animado(pet_id, quadro, "ocioso").convert_alpha() for quadro in range(8))
    reacao = tuple(_criar_quadro_pet_animado(pet_id, quadro, "reacao").convert_alpha() for quadro in range(8))
    morrendo = []
    for fase in range(6):
        base = andando[min((fase * 2), 7)]
        if fase == 0:
            imagem = base.copy()
        else:
            angulos = (0, 13, 30, 57, 85, 105)
            larguras = (64, 62, 60, 52, 45, 34)
            alturas = (56, 54, 47, 38, 27, 17)
            mini = pygame.transform.scale(base, (larguras[fase], alturas[fase]))
            mini = pygame.transform.rotate(mini, -angulos[fase])
            imagem = pygame.Surface(_PET_TAMANHO, pygame.SRCALPHA)
            imagem.blit(mini, mini.get_rect(center=(32, 29 + fase)))
            imagem.set_alpha((255, 245, 218, 175, 105, 45)[fase])
        morrendo.append(imagem.convert_alpha())
    cache = (andando, tuple(morrendo), ocioso, reacao)
    _PET_SPRITES_CACHE[pet_id] = cache
    return cache


# Animações adicionais geradas uma vez por pet, sem arquivos externos.
_PET_PERSONALIDADE_CACHE = {}




_PET_MENU_OCIOSO_CACHE = {}







def _sprite_base_transformavel_pet(base, tamanho, margem=0.12):
    if base is None:
        return pygame.Surface((max(2, tamanho[0] // 2), max(2, tamanho[1] // 2)), pygame.SRCALPHA).convert_alpha()
    sw, sh = max(1, base.get_width()), max(1, base.get_height())
    limite_w = max(1, int(tamanho[0] * (1.0 - margem * 2)))
    limite_h = max(1, int(tamanho[1] * (1.0 - margem * 2)))
    escala = min(limite_w / sw, limite_h / sh)
    nw = max(1, int(sw * escala))
    nh = max(1, int(sh * escala))
    return pygame.transform.smoothscale(base, (nw, nh)).convert_alpha()


def _montar_quadro_transformado_pet(sprite, tamanho, dx=0.0, dy=0.0, sx=1.0, sy=1.0, angulo=0.0,
                                    alpha=255, sombra=True, pulso_sombra=1.0):
    tela = pygame.Surface(tamanho, pygame.SRCALPHA)
    if sprite is None:
        return tela.convert_alpha()
    if sombra:
        sw = max(10, int(sprite.get_width() * 0.72 * pulso_sombra * sx))
        sh = max(4, int(6 * pulso_sombra))
        sombra_surf = pygame.Surface((sw + 6, sh + 6), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra_surf, (12, 16, 26, 80), (3, 3, sw, sh))
        tela.blit(sombra_surf, sombra_surf.get_rect(center=(tamanho[0] // 2 + int(dx * 0.35), tamanho[1] - 5)))
    nw = max(1, int(sprite.get_width() * sx))
    nh = max(1, int(sprite.get_height() * sy))
    corpo = pygame.transform.smoothscale(sprite, (nw, nh)).convert_alpha()
    if abs(angulo) > 0.01:
        corpo = pygame.transform.rotate(corpo, angulo).convert_alpha()
    if alpha != 255:
        corpo.set_alpha(alpha)
    rect = corpo.get_rect(midbottom=(tamanho[0] // 2 + int(dx), tamanho[1] - 4 + int(dy)))
    tela.blit(corpo, rect)
    return tela.convert_alpha()







def _desenhar_efeitos_personalizados_pet(quadro, pet_id, estado, tamanho, fase):
    w, h = tamanho
    ativo = estado in ('CORRER', 'ESPERA', 'HABILIDADE', 'FESTA', 'ALERTA', 'CARINHO', 'BRINCAR', 'CURIOSO')
    if not ativo:
        return
    pulso = math.sin(fase * 1.8)
    if pet_id == 'BOLHA':
        for idx in range(3):
            ang = fase * (1.0 + idx * 0.18) + idx * 1.9
            px = int(w//2 + math.cos(ang) * (10 + idx * 2))
            py = int(h//2 - 2 + math.sin(ang * 1.15) * (9 - idx))
            r = 2 + (idx % 2)
            pygame.draw.circle(quadro, (208, 248, 255), (px, py), r)
            pygame.draw.circle(quadro, (85, 210, 255), (px, py), r, 1)
    elif pet_id == 'RAPOSA':
        if estado in ('CORRER', 'BRINCAR', 'HABILIDADE'):
            for idx in range(2):
                x = int(8 + idx * 5 + abs(pulso) * 2)
                y = int(h - 17 - idx * 4)
                pygame.draw.line(quadro, (255, 225, 176), (x, y), (x + 7, y), 1)
    elif pet_id == 'FANTASMA':
        for idx in range(3):
            px = int(w//2 - 10 + idx * 10 + math.sin(fase + idx) * 2)
            py = int(h - 13 + math.sin(fase * 1.3 + idx) * 2)
            pygame.draw.circle(quadro, (235, 205, 255, 120), (px, py), 2)
    elif pet_id == 'TARTARUGA':
        for idx in range(4):
            px = int(w//2 - 10 + idx * 6)
            py = int(h//2 - 3 + math.sin(fase * 1.5 + idx * 0.8) * 2)
            pygame.draw.circle(quadro, (188, 255, 252), (px, py), 1)
            pygame.draw.circle(quadro, (97, 230, 210), (px, py), 1)
    elif pet_id == 'DRAGAO':
        for idx in range(3):
            px = int(w - 12 - idx * 6)
            py = int(11 + math.sin(fase * 1.7 + idx) * 3)
            pygame.draw.line(quadro, (255, 174, 242), (px - 2, py), (px + 2, py), 1)
            pygame.draw.line(quadro, (255, 174, 242), (px, py - 2), (px, py + 2), 1)
    elif pet_id == 'GOLEM':
        for idx in range(3):
            px = int(w//2 - 8 + idx * 8)
            py = int(h - 12 - abs(math.sin(fase * 1.4 + idx)) * 4)
            pygame.draw.circle(quadro, (255, 184, 96), (px, py), 2)
    elif pet_id == 'BEIJA_FLOR':
        for idx in range(3):
            px = int(w//2 + math.cos(fase * 1.7 + idx * 2.1) * 12)
            py = int(h//2 - 2 + math.sin(fase * 2.2 + idx) * 7)
            pygame.draw.circle(quadro, (196, 255, 230), (px, py), 1)
            pygame.draw.circle(quadro, (255, 246, 158), (px + 1, py), 1)
    elif pet_id == 'DRAGAO_PLASMA':
        for idx in range(3):
            ox = int(w//2 + math.sin(fase * 2.5 + idx) * (8 + idx * 2))
            oy = int(h//2 - 4 + math.cos(fase * 2.8 + idx * 1.3) * 8)
            pygame.draw.line(quadro, (115, 238, 255), (ox - 2, oy - 1), (ox + 2, oy + 1), 1)
            pygame.draw.line(quadro, (205, 250, 255), (ox - 1, oy + 1), (ox + 2, oy - 2), 1)
    elif pet_id == 'ABELHA_MAGNETICA':
        for idx in range(2):
            ang = fase * 1.7 + idx * math.pi
            px = int(w//2 + math.cos(ang) * 11)
            py = int(h//2 + math.sin(ang * 1.3) * 7)
            pygame.draw.circle(quadro, (255, 226, 86), (px, py), 2)
            pygame.draw.circle(quadro, (92, 112, 148), (px, py), 2, 1)


def _desenhar_apendices_pet(quadro, pet_id, estado, tamanho, fase):
    """Adiciona movimento visível de patas, pernas, braços, asas e cauda."""
    if estado not in ('CORRER', 'AGACHAR', 'ESPERA', 'HABILIDADE', 'BRINCAR', 'IMPULSO', 'SUBINDO', 'CAINDO', 'POUSO', 'APICE'):
        return
    w, h = tamanho
    passo = math.sin(fase * 2.0)
    passo_inv = math.sin(fase * 2.0 + math.pi)
    if pet_id == 'RAPOSA':
        # quatro patas alternadas + cauda volumosa para dar leitura clara de corrida terrestre
        bases = [(w//2 - 13, h - 18), (w//2 - 6, h - 19), (w//2 + 4, h - 19), (w//2 + 11, h - 18)]
        elevs = [max(0.0, passo_inv), max(0.0, passo), max(0.0, passo_inv), max(0.0, passo)]
        tons = [((108, 49, 32), (255, 176, 98)), ((96, 40, 24), (243, 156, 82)), ((108, 49, 32), (255, 176, 98)), ((96, 40, 24), (243, 156, 82))]
        for (bx, by), el, cols in zip(bases, elevs, tons):
            px = int(bx + (passo * 2.8 if bx >= w//2 else -passo * 2.8))
            py = int(h - 5 - el * 5 + (2 if estado == 'AGACHAR' else 0))
            pygame.draw.line(quadro, cols[0], (bx, by), (px, py - 2), 3)
            pygame.draw.ellipse(quadro, cols[1], (px - 4, py - 4, 8, 4))
            pygame.draw.ellipse(quadro, cols[0], (px - 5, py - 4, 10, 5), 1)
        cauda = pygame.Surface((w, h), pygame.SRCALPHA)
        sway = math.sin(fase * 1.8) * 7
        pts = [(w//2 - 15, h//2 + 3), (w//2 - 24, h//2 + int(sway) - 3), (w//2 - 18, h//2 + 11), (w//2 - 10, h//2 + 6)]
        pygame.draw.polygon(cauda, (255, 155, 76, 170), pts)
        pygame.draw.polygon(cauda, (255, 238, 199, 150), [(pts[1][0]+2, pts[1][1]+2), (pts[1][0]+8, pts[1][1]+3), (pts[2][0]+1, pts[2][1]-1)])
        quadro.blit(cauda, (0, 0))
        return
    if pet_id == 'TARTARUGA':
        for bx, by, shift in ((w//2 - 13, h - 18, passo_inv), (w//2 + 11, h - 18, passo), (w//2 - 7, h - 11, passo), (w//2 + 7, h - 11, passo_inv)):
            rx = int(bx + shift * 3)
            ry = int(by + abs(shift) * 2)
            pygame.draw.ellipse(quadro, (55, 185, 210), (rx - 5, ry - 3, 10, 6))
            pygame.draw.ellipse(quadro, (180, 250, 255), (rx - 2, ry - 1, 4, 2))
        return
    if pet_id == 'GOLEM':
        for bx, by, shift in ((w//2 - 13, h - 18, passo), (w//2 + 13, h - 18, passo_inv)):
            ex = int(bx + shift * 2)
            ey = int(h - 6 - abs(shift) * 2)
            pygame.draw.line(quadro, (82, 54, 40), (bx, by), (ex, ey), 4)
            pygame.draw.circle(quadro, (255, 156, 72), (ex, ey), 4)
        for bx, by, shift in ((w//2 - 18, h - 26, passo_inv), (w//2 + 18, h - 26, passo)):
            ex = int(bx + shift * 2)
            ey = int(by + abs(shift) * 2)
            pygame.draw.line(quadro, (73, 48, 37), (bx, by), (ex, ey), 4)
            pygame.draw.circle(quadro, (201, 115, 56), (ex, ey), 4)
        return
    if pet_id == 'BOLHA':
        # pequenas nadadeiras e elasticidade para parecer um organismo de água
        for bx, side in ((w//2 - 12, -1), (w//2 + 12, 1)):
            flap = math.sin(fase * 2.2 + (0 if side < 0 else math.pi))
            pygame.draw.line(quadro, (78, 222, 255), (bx, h - 20), (int(bx + flap * 5), h - 16), 2)
            pygame.draw.line(quadro, (78, 222, 255), (w//2 + side * 8, h - 22), (int(w//2 + side * 13 + flap * 3), h - 24), 2)
        return
    if pet_id == 'FANTASMA':
        pontos = []
        for idx in range(6):
            x = 8 + idx * max(1, (w - 16) // 5)
            y = h - 8 + int(math.sin(fase * 2.3 + idx * 0.85) * 2)
            pontos.append((x, y))
        pygame.draw.lines(quadro, (220, 180, 255), False, pontos, 2)
        pygame.draw.line(quadro, (234, 215, 255), (w//2 - 10, h//2 + 2), (w//2 - 16, h//2 + 6), 2)
        pygame.draw.line(quadro, (234, 215, 255), (w//2 + 10, h//2 + 2), (w//2 + 16, h//2 + 6), 2)
        return
    if pet_id in ('DRAGAO', 'DRAGAO_PLASMA'):
        cor_asa = (255, 138, 241, 118) if pet_id == 'DRAGAO' else (92, 225, 255, 118)
        cor_linha = (255, 206, 244) if pet_id == 'DRAGAO' else (196, 248, 255)
        asa = pygame.Surface((w, h), pygame.SRCALPHA)
        abertura = int(9 + abs(math.sin(fase * (2.0 if pet_id == 'DRAGAO' else 2.4))) * 9)
        esquerda = ((w//2 - 6, h//2 - 7), (w//2 - 26, h//2 - abertura), (w//2 - 14, h//2 + 3))
        direita = ((w//2 + 4, h//2 - 7), (w//2 + 24, h//2 - abertura), (w//2 + 12, h//2 + 3))
        pygame.draw.polygon(asa, cor_asa, esquerda)
        pygame.draw.polygon(asa, cor_asa, direita)
        pygame.draw.lines(asa, cor_linha, False, esquerda, 1)
        pygame.draw.lines(asa, cor_linha, False, direita, 1)
        quadro.blit(asa, (0, 0))
        for bx, by, shift in ((w//2 - 7, h - 16, passo), (w//2 + 7, h - 16, passo_inv)):
            pygame.draw.line(quadro, (70, 34, 98) if pet_id == 'DRAGAO' else (36, 94, 120), (bx, by), (int(bx + shift * 2), h - 7), 2)
        # cauda curta com ponta brilhante
        pygame.draw.line(quadro, cor_linha, (w//2 - 15, h//2 + 6), (w//2 - 22, h//2 + 10 + int(math.sin(fase * 1.7) * 3)), 2)
        pygame.draw.circle(quadro, cor_linha, (w//2 - 22, h//2 + 10 + int(math.sin(fase * 1.7) * 3)), 2)
        return
    if pet_id == 'BEIJA_FLOR':
        asa = pygame.Surface((w, h), pygame.SRCALPHA)
        abertura = int(11 + abs(math.sin(fase * 6.0)) * 9)
        pygame.draw.ellipse(asa, (150, 255, 228, 96), (w//2 - 22, h//2 - abertura, 15, abertura + 6))
        pygame.draw.ellipse(asa, (150, 255, 228, 96), (w//2 + 7, h//2 - abertura, 15, abertura + 6))
        pygame.draw.line(asa, (199, 255, 240), (w//2 - 2, h//2 - 4), (w//2 - 16, h//2 - abertura + 7), 1)
        pygame.draw.line(asa, (199, 255, 240), (w//2 + 2, h//2 - 4), (w//2 + 16, h//2 - abertura + 7), 1)
        quadro.blit(asa, (0, 0))
        return
    if pet_id == 'ABELHA_MAGNETICA':
        asa = pygame.Surface((w, h), pygame.SRCALPHA)
        abertura = int(9 + abs(math.sin(fase * 5.5)) * 8)
        pygame.draw.ellipse(asa, (255, 250, 220, 112), (w//2 - 20, h//2 - abertura, 12, abertura + 5))
        pygame.draw.ellipse(asa, (255, 250, 220, 112), (w//2 + 8, h//2 - abertura, 12, abertura + 5))
        quadro.blit(asa, (0, 0))
        for bx in (w//2 - 10, w//2 - 2, w//2 + 6):
            pygame.draw.line(quadro, (92, 76, 24), (bx, h - 19), (int(bx + passo * 1.5), h - 10), 1)
        pygame.draw.line(quadro, (74, 90, 126), (w//2 - 6, h//2 - 8), (w//2 - 10, h//2 - 14 + int(math.sin(fase * 2.0) * 2)), 1)
        pygame.draw.line(quadro, (74, 90, 126), (w//2 + 6, h//2 - 8), (w//2 + 10, h//2 - 14 + int(math.cos(fase * 2.0) * 2)), 1)
        return


def _gerar_animacao_transformada_pet(pet_id, base, estado, tamanho=(52, 46)):
    perfil = _perfil_refino_pet(pet_id)
    voador = perfil.get('tipo') == 'voador'
    cor = _PET_CORES_ENERGIA.get(pet_id, (180, 230, 255))
    sprite = _sprite_base_transformavel_pet(base, tamanho, margem=0.10 if voador else 0.12)
    contagens = {
        'CORRER': 18, 'ESPERA': 20, 'SONO': 18, 'FESTA': 16, 'ALERTA': 12, 'HABILIDADE': 16,
        'AGACHAR': 12, 'IMPULSO': 10, 'SUBINDO': 10, 'APICE': 8, 'CAINDO': 10, 'POUSO': 10,
        'CURIOSO': 14, 'ALIVIO': 12, 'CARINHO': 16, 'BRINCAR': 16, 'MORRER': 10
    }
    total = contagens.get(estado, 12)
    quadros = []
    for i in range(total):
        p = 0.0 if total <= 1 else i / float(total - 1)
        a = p * math.tau
        dx = dy = 0.0
        sx = sy = 1.0
        ang = 0.0
        sombra = True
        pulso_sombra = 1.0
        alpha = 255
        adornos = []
        if estado == 'CORRER':
            if pet_id == 'BOLHA':
                passadas = math.sin(a * 1.7)
                dx = passadas * 1.3
                dy = -1.2 + math.sin(a * 2.2) * 1.3
                ang = math.sin(a * 1.1) * 2.4
                sx = 1.0 + 0.05 * math.sin(a * 2.0)
                sy = 1.0 - 0.06 * math.sin(a * 2.0)
                pulso_sombra = 0.94
            elif pet_id == 'RAPOSA':
                passadas = math.sin(a * 2.25)
                dx = passadas * 2.2
                dy = -abs(passadas) * 0.85
                ang = passadas * 4.8
                sx = 1.0 + 0.03 * math.cos(a * 2.25)
                sy = 1.0 - 0.02 * math.cos(a * 2.25)
                pulso_sombra = 1.0 - abs(dy) * 0.04
            elif pet_id == 'FANTASMA':
                dx = math.sin(a * 1.35) * 1.0
                dy = -2.6 + math.sin(a * 1.55 - 0.4) * 1.9
                ang = math.sin(a * 1.2) * 3.4
                sx = 1.0 + 0.02 * math.cos(a * 1.2)
                sy = 1.0 - 0.02 * math.cos(a * 1.2)
                pulso_sombra = 0.90
            elif pet_id == 'TARTARUGA':
                passadas = math.sin(a * 1.18)
                dx = passadas * 0.9
                dy = -abs(passadas) * 0.35
                ang = math.sin(a * 1.18) * 1.8
                sx = 1.0 + 0.012 * math.cos(a * 1.2)
                sy = 1.0 - 0.01 * math.cos(a * 1.2)
            elif pet_id == 'DRAGAO':
                dx = math.sin(a * 1.6) * 1.4
                dy = -1.8 + math.sin(a * 1.55 - 0.4) * 1.7
                ang = math.sin(a * 1.55) * 4.2
                sx = 1.0 + 0.02 * math.cos(a * 1.55)
                sy = 1.0 - 0.018 * math.cos(a * 1.55)
                pulso_sombra = 0.93
            elif pet_id == 'GOLEM':
                passadas = math.sin(a * 1.45)
                dx = passadas * 1.0
                dy = -abs(passadas) * 0.55
                ang = math.sin(a * 1.45) * 2.2
                sx = 1.0 + 0.016 * math.cos(a * 1.45)
                sy = 1.0 - 0.01 * math.cos(a * 1.45)
            elif pet_id == 'BEIJA_FLOR':
                dx = math.sin(a * 2.0) * 0.8
                dy = -2.8 + math.sin(a * 3.4 - 0.5) * 2.0
                ang = math.sin(a * 2.2) * 2.4
                sx = 1.0 + 0.015 * math.cos(a * 3.2)
                sy = 1.0 - 0.015 * math.cos(a * 3.2)
                pulso_sombra = 0.88
            elif pet_id == 'DRAGAO_PLASMA':
                dx = math.sin(a * 1.85) * 1.4
                dy = -2.0 + math.sin(a * 2.1 - 0.4) * 1.9
                ang = math.sin(a * 1.95) * 4.6
                sx = 1.0 + 0.022 * math.cos(a * 1.9)
                sy = 1.0 - 0.019 * math.cos(a * 1.9)
                pulso_sombra = 0.90
            elif pet_id == 'ABELHA_MAGNETICA':
                dx = math.sin(a * 2.3) * 1.1
                dy = -2.2 + math.sin(a * 3.0 - 0.4) * 1.7
                ang = math.sin(a * 2.1) * 2.8
                sx = 1.0 + 0.014 * math.cos(a * 3.0)
                sy = 1.0 - 0.014 * math.cos(a * 3.0)
                pulso_sombra = 0.89
            else:
                passadas = math.sin(a * (1.35 if voador else 2.0))
                dx = passadas * (1.0 if voador else 1.8)
                dy = (-1.5 + math.sin(a * 1.35 - 0.5) * 1.4) if voador else abs(passadas) * -1.1
                ang = math.sin(a * (1.35 if voador else 2.0)) * (4 if voador else 5)
                sx = 1.0 + (0.02 if voador else 0.04) * math.cos(a * (1.35 if voador else 2.0))
                sy = 1.0 - (sx - 1.0) * 0.72
                pulso_sombra = 1.0 - abs(dy) * 0.03
        elif estado == 'ESPERA':
            if pet_id == 'RAPOSA':
                dy = math.sin(a * 1.05) * 0.7
                ang = math.sin(a * 0.6) * 1.2
            elif pet_id == 'TARTARUGA':
                dy = math.sin(a * 0.6) * 0.5
                ang = math.sin(a * 0.45) * 0.8
            elif voador:
                dy = -1.2 + math.sin(a * 1.15) * 1.4
                ang = math.sin(a * 0.65) * 1.8
                pulso_sombra = 0.94
            else:
                dy = math.sin(a) * 0.9
                sx = 1.0 + math.sin(a) * 0.012
                sy = 1.0 - math.sin(a) * 0.015
                ang = math.sin(a * 0.5) * 1.4
        elif estado == 'SONO':
            dy = math.sin(a * 0.5) * 0.8
            sx = 1.0 + math.sin(a * 0.5) * 0.01
            sy = 1.0 - math.sin(a * 0.5) * 0.02
            adornos.append(('z', cor, i))
        elif estado == 'FESTA':
            dy = -abs(math.sin(a)) * (2.4 if pet_id == 'TARTARUGA' else 3.0)
            ang = math.sin(a * 1.5) * (3.6 if pet_id == 'GOLEM' else 5.0)
            sx = 1.0 + abs(math.sin(a)) * 0.03
            sy = 1.0 - abs(math.sin(a)) * 0.03
            adornos.append(('spark', cor, i))
        elif estado == 'ALERTA':
            dx = math.sin(a * 3.0) * (0.8 if pet_id == 'TARTARUGA' else 1.2)
            ang = math.sin(a * 3.0) * 3.0
            adornos.append(('alerta', cor, i))
        elif estado == 'HABILIDADE':
            if pet_id in ('DRAGAO', 'DRAGAO_PLASMA', 'BEIJA_FLOR', 'ABELHA_MAGNETICA', 'FANTASMA'):
                dy = -1.8 + math.sin(a * 2.0) * 1.7
                pulso_sombra = 0.91
            else:
                dy = math.sin(a * 2.0) * 1.2
            sx = 1.0 + 0.03 * math.sin(a * 2.0)
            sy = 1.0 - 0.03 * math.sin(a * 2.0)
            adornos.append(('aura', cor, i))
        elif estado == 'AGACHAR':
            dy = 5 + abs(math.sin(a)) * 1.0
            sx = 1.03 + math.sin(a * 2.0) * 0.01
            sy = 0.80 + abs(math.cos(a)) * 0.04
            dx = math.sin(a * 2.0) * (1.1 if pet_id == 'TARTARUGA' else 1.5)
        elif estado == 'IMPULSO':
            dy = 3 - p * (7.0 if pet_id != 'TARTARUGA' else 5.8)
            sx = 1.06 - p * 0.08
            sy = 0.82 + p * 0.24
            ang = -2.0 - p * (4.0 if not voador else 2.6)
        elif estado == 'SUBINDO':
            dy = -4.0 - p * (5.0 if not voador else 3.8)
            sx = 0.97
            sy = 1.07
            ang = -7.0 if not voador else -3.8
            pulso_sombra = 0.88
        elif estado == 'APICE':
            dy = -7.0 + math.sin(a) * 0.7
            sx = 0.99
            sy = 1.03
            ang = math.sin(a) * 1.5
            pulso_sombra = 0.86
        elif estado == 'CAINDO':
            dy = -6.0 + p * (6.0 if not voador else 4.5)
            sx = 1.02
            sy = 0.96
            ang = 6.0 if not voador else 2.8
            pulso_sombra = 0.90 + p * 0.08
        elif estado == 'POUSO':
            curvas = [(1.08, 0.84, 1.0), (1.10, 0.82, 2.0), (1.06, 0.88, 1.0), (1.02, 0.96, 0.0),
                      (1.0, 1.0, -0.5), (1.0, 1.0, 0.0), (1.0, 1.0, 0.0), (1.0, 1.0, 0.0)]
            sx, sy, dy = curvas[i]
        elif estado == 'CURIOSO':
            ang = (-5, -3, -1, 1, 4, 5, 2, -2, -4, 0)[i]
            dx = (-2, -1, 0, 1, 2, 1, 0, -1, -2, 0)[i]
            dy = (-1, -1, -2, -2, -1, -1, 0, 0, -1, -1)[i]
            adornos.append(('spark', (252, 227, 130), i))
        elif estado == 'ALIVIO':
            dy = (0, -2, -4, -2, 0, -1, 0, 0, -1, 0)[i]
            ang = (0, -2, -3, -1, 0, 2, 1, 0, -1, 0)[i]
            adornos.append(('spark', cor, i))
        elif estado == 'CARINHO':
            dy = math.sin(a * 1.4) * 1.2
            ang = math.sin(a) * 1.8
            adornos.append(('coracao', (255, 129, 183), i))
        elif estado == 'BRINCAR':
            dx = math.sin(a * 2.0) * (1.3 if pet_id == 'TARTARUGA' else 2.0)
            dy = -abs(math.sin(a * 2.0)) * (1.6 if pet_id == 'GOLEM' else 2.5)
            ang = math.sin(a * 2.0) * 5.0
            adornos.append(('spark', cor, i))
        elif estado == 'MORRER':
            ang = p * 88.0
            dy = p * 7.0
            sx = max(0.55, 1.0 - p * 0.28)
            sy = max(0.38, 1.0 - p * 0.62)
            alpha = max(40, int(255 * (1.0 - p * 0.72)))
            pulso_sombra = max(0.5, 1.0 - p * 0.35)
        quadro = _montar_quadro_transformado_pet(sprite, tamanho, dx, dy, sx, sy, ang, alpha, sombra, pulso_sombra)
        _desenhar_apendices_pet(quadro, pet_id, estado, tamanho, a)
        for tipo, cor_ad, fase in adornos:
            if tipo == 'z':
                zx = tamanho[0] - 11 + (fase % 3)
                zy = 6 - (fase % 2)
                pygame.draw.lines(quadro, (194, 231, 255), False, ((zx, zy), (zx + 4, zy), (zx, zy + 4), (zx + 4, zy + 4)), 1)
            elif tipo == 'spark':
                for j in range(2):
                    px = 8 + ((fase * 5) + j * 17) % max(10, tamanho[0] - 10)
                    py = 8 + ((fase * 3) + j * 9) % max(10, tamanho[1] - 16)
                    pygame.draw.line(quadro, cor_ad, (px - 2, py), (px + 2, py), 1)
                    pygame.draw.line(quadro, cor_ad, (px, py - 2), (px, py + 2), 1)
            elif tipo == 'alerta':
                pygame.draw.circle(quadro, (255, 243, 134), (tamanho[0] - 7, 7), 4)
                pygame.draw.line(quadro, (60, 55, 75), (tamanho[0] - 7, 5), (tamanho[0] - 7, 8), 2)
                pygame.draw.circle(quadro, (60, 55, 75), (tamanho[0] - 7, 10), 1)
            elif tipo == 'aura':
                pygame.draw.arc(quadro, cor_ad, (3, 5, tamanho[0] - 6, tamanho[1] - 10), 0.2, 2.9, 1)
            elif tipo == 'coracao':
                hx = tamanho[0] - 11 + (fase % 3)
                hy = 9 - (fase % 2)
                pygame.draw.circle(quadro, cor_ad, (hx, hy), 2)
                pygame.draw.circle(quadro, cor_ad, (hx + 3, hy), 2)
                pygame.draw.polygon(quadro, cor_ad, ((hx - 1, hy + 1), (hx + 5, hy + 1), (hx + 2, hy + 5)))
        _desenhar_efeitos_personalizados_pet(quadro, pet_id, estado, tamanho, a)
        quadros.append(quadro.convert_alpha())
    return tuple(quadros)



def _misturar_superficies(surf_a, surf_b, alpha_b=128):
    """Cria um quadro intermediário entre duas superfícies do mesmo tamanho."""
    w = max(surf_a.get_width(), surf_b.get_width())
    h = max(surf_a.get_height(), surf_b.get_height())
    base = pygame.Surface((w, h), pygame.SRCALPHA)
    ra = surf_a.get_rect(center=(w // 2, h // 2))
    rb = surf_b.get_rect(center=(w // 2, h // 2))
    base.blit(surf_a, ra)
    temp = pygame.Surface((w, h), pygame.SRCALPHA)
    temp.blit(surf_b, rb)
    temp.set_alpha(alpha_b)
    base.blit(temp, (0, 0))
    return base.convert_alpha()


def _suavizar_sequencia_pet(quadros, forcar_minimo=6):
    """Insere quadros intermediários para deixar corrida/idle mais fluidos."""
    if not quadros:
        return tuple()
    if len(quadros) == 1:
        return tuple(quadros[0].copy().convert_alpha() for _ in range(max(2, forcar_minimo)))
    suavizados = []
    n = len(quadros)
    for i, quadro in enumerate(quadros):
        prox = quadros[(i + 1) % n]
        suavizados.append(quadro.convert_alpha())
        suavizados.append(_misturar_superficies(quadro, prox, 96))
    while len(suavizados) < forcar_minimo:
        suavizados.extend(list(suavizados))
    return tuple(suavizados[:max(len(suavizados), forcar_minimo)])




def _mapa_estado_folha_pet(estado):
    """Mapeia estados visuais do jogo para as colunas reais das folhas dos pets."""
    mapa = {
        'CORRER': 'CORRER',
        'ESPERA': 'IDLE',
        'SONO': 'DORMIR',
        'FESTA': 'FELIZ',
        'ALERTA': 'ALERTA',
        'HABILIDADE': 'HABILIDADE',
        'AGACHAR': 'AGACHAR',
        'IMPULSO': 'PULO',
        'SUBINDO': 'PULO',
        'APICE': 'PULO',
        'CAINDO': 'QUEDA',
        'POUSO': 'QUEDA',
        'CURIOSO': 'IDLE',
        'ALIVIO': 'FELIZ',
        'CARINHO': 'FELIZ',
        'BRINCAR': 'CORRER',
        'MORRER': 'MORTE',
    }
    return mapa.get(estado, 'IDLE')



def _montar_quadro_pet_de_folha(frame_base, tamanho, estado, indice, total, pet_id):
    """Reconstrói um quadro suave usando os quadros reais das folhas premium.

    Mantém a arte desenhada e aplica apenas um deslocamento/escala leve, agora com
    personalidade individual por pet para que cada um pareça mais vivo.
    """
    w, h = tamanho
    canvas = pygame.Surface((w, h), pygame.SRCALPHA)
    p = 0.0 if total <= 1 else indice / float(total - 1)
    a = p * math.tau
    perfil = _perfil_refino_pet(pet_id)
    voador = perfil.get('tipo') == 'voador'
    dx = dy = 0.0
    ang = 0.0
    esc_x = esc_y = 1.0
    if estado == 'CORRER':
        if pet_id == 'RAPOSA':
            dx = math.sin(a * 1.9) * 1.4
            dy = -abs(math.sin(a * 2.1)) * 0.8
            ang = math.sin(a * 2.0) * 2.4
        elif pet_id == 'TARTARUGA':
            dx = math.sin(a * 1.0) * 0.8
            dy = -abs(math.sin(a * 1.2)) * 0.25
            ang = math.sin(a * 1.0) * 1.0
        elif pet_id == 'GOLEM':
            dx = math.sin(a * 1.2) * 1.0
            dy = -abs(math.sin(a * 1.4)) * 0.45
            ang = math.sin(a * 1.2) * 1.4
        elif voador:
            dx = math.sin(a * 1.35) * 0.95
            dy = -1.3 + math.sin(a * 1.6 - 0.7) * 1.4
            ang = math.sin(a * 1.4) * 2.4
        else:
            dx = math.sin(a * 1.85) * 1.1
            dy = math.sin(a * 2.1 - 0.7) * 0.55
            ang = math.sin(a * 1.95) * 2.0
    elif estado in ('ESPERA', 'CURIOSO'):
        if voador:
            dy = -1.0 + math.sin(a) * 1.5
            ang = math.sin(a * 0.6) * 1.5
        elif pet_id == 'TARTARUGA':
            dy = math.sin(a * 0.55) * 0.45
            ang = math.sin(a * 0.35) * 0.8
        else:
            dy = math.sin(a) * 0.85
            ang = math.sin(a * 0.5) * 1.2
    elif estado == 'SONO':
        dy = math.sin(a * 0.5) * 0.8
    elif estado in ('FESTA', 'ALIVIO', 'CARINHO'):
        dy = -abs(math.sin(a)) * (1.2 if pet_id == 'TARTARUGA' else 1.6)
        ang = math.sin(a * 1.2) * (1.5 if pet_id == 'GOLEM' else 2.2)
    elif estado == 'ALERTA':
        dx = math.sin(a * 3.0) * 0.7
        ang = math.sin(a * 3.0) * 1.5
    elif estado == 'HABILIDADE':
        dy = (-1.0 if voador else 0.0) + math.sin(a * 2.0) * 1.2
        esc_x = 1.0 + 0.02 * math.sin(a * 2.0)
        esc_y = 1.0 - 0.02 * math.sin(a * 2.0)
    elif estado == 'AGACHAR':
        dy = 3.0 + abs(math.sin(a)) * 0.8
        esc_y = 0.94
        esc_x = 1.02
    elif estado in ('IMPULSO', 'SUBINDO', 'APICE'):
        dy = -2.5 - math.sin(p * math.pi) * (1.8 if voador else 2.4)
        ang = -1.5 if voador else -2.0
    elif estado in ('CAINDO', 'POUSO'):
        dy = -1.0 + p * (1.4 if voador else 2.0)
        ang = 1.2 if voador else 2.0
    elif estado == 'BRINCAR':
        dx = math.sin(a * 2.0) * 1.4
        dy = -abs(math.sin(a * 2.0)) * 1.2
        ang = math.sin(a * 2.0) * 2.2
    elif estado == 'MORRER':
        ang = p * 80.0
        dy = p * 6.0
        esc_x = max(0.60, 1.0 - p * 0.22)
        esc_y = max(0.48, 1.0 - p * 0.42)

    base = _encaixar_sprite(frame_base, (max(1, w - 2), max(1, h - 2)), margem=0.04 if voador else 0.03)
    bw, bh = base.get_size()
    tw = max(1, int(bw * esc_x))
    th = max(1, int(bh * esc_y))
    if tw != bw or th != bh:
        base = pygame.transform.smoothscale(base, (tw, th)).convert_alpha()
    if abs(ang) > 0.01:
        base = pygame.transform.rotozoom(base, ang, 1.0).convert_alpha()
    if estado == 'MORRER':
        base.set_alpha(max(40, int(255 * (1.0 - p * 0.65))))
    sombra = pygame.Surface((w, h), pygame.SRCALPHA)
    sw = max(10, int((18 if voador else 22) - abs(dy) * 1.1))
    sh = max(4, int((5 if voador else 7) - abs(dy) * 0.28))
    sy = h - 7 if voador else h - 5
    pygame.draw.ellipse(sombra, (10, 12, 20, 66 if voador else 84), (w // 2 - sw // 2, sy, sw, sh))
    canvas.blit(sombra, (0, 0))
    rect = base.get_rect(center=(w // 2 + int(dx), h // 2 + int(dy)))
    canvas.blit(base, rect)
    _desenhar_efeitos_personalizados_pet(canvas, pet_id, estado, tamanho, a)
    return canvas.convert_alpha()









def _encaixar_sprite(base, tamanho, margem=0.08):
    """Escala e centraliza o sprite dentro de uma área, preservando proporção."""
    destino_w, destino_h = tamanho
    tela = pygame.Surface((destino_w, destino_h), pygame.SRCALPHA)
    if base is None:
        return tela.convert_alpha()
    sw, sh = max(1, base.get_width()), max(1, base.get_height())
    limite_w = max(1, int(destino_w * (1.0 - margem * 2)))
    limite_h = max(1, int(destino_h * (1.0 - margem * 2)))
    escala = min(limite_w / sw, limite_h / sh)
    nw = max(1, int(sw * escala))
    nh = max(1, int(sh * escala))
    sprite = pygame.transform.smoothscale(base, (nw, nh)).convert_alpha()
    tela.blit(sprite, sprite.get_rect(center=(destino_w // 2, destino_h // 2)))
    return tela.convert_alpha()


def _desenhar_selo_mini_pet(superficie, rect, cor):
    sombra = rect.move(0, 2)
    pygame.draw.rect(superficie, (8, 12, 22), sombra, border_radius=12)
    base = misturar_cores(cor, (28, 32, 48), 0.42)
    brilho = misturar_cores(cor, BRANCO, 0.24)
    pygame.draw.rect(superficie, base, rect, border_radius=12)
    pygame.draw.rect(superficie, brilho, rect, 2, border_radius=12)
    pygame.draw.rect(superficie, (255, 255, 255), (rect.x + 5, rect.y + 5, rect.w - 10, 1), border_radius=4)









# Pets Premium 2.0: estados adicionais são gerados sob demanda, uma vez por pet.
# Se as folhas externas estiverem presentes, os estados usam os quadros dessas folhas.
_PET_ESTADOS_CACHE = {}
_PET_PREVIA_CANTINHO_CACHE = {}
_PET_CORES_ENERGIA = {
    "BOLHA": (142, 240, 255), "RAPOSA": (255, 198, 102),
    "FANTASMA": (210, 156, 255), "TARTARUGA": (106, 236, 222),
    "DRAGAO": (255, 122, 241), "GOLEM": (255, 177, 86),
    "BEIJA_FLOR": (135, 255, 232), "DRAGAO_PLASMA": (92, 225, 255),
    "ABELHA_MAGNETICA": (255, 220, 91),
}





def desenhar_evolucao_pet(superficie, pet_id, x, y, dados, frame, tamanho=(52,46), leve=False):
    """Acessórios discretos por nível e vínculo; não modificam sprite físico/hitbox."""
    if pet_id not in PETS_CONFIG:
        return
    nivel = nivel_cosmetico_pet(dados, pet_id)
    registro = dados.get("pet_vinculos", {}).get(pet_id, {})
    pontos = int(registro.get("pontos", 0))
    cor = _PET_CORES_ENERGIA[pet_id]
    esc = tamanho[0] / 52
    cx = int(x)
    cy = int(y)
    if nivel >= 2:
        pygame.draw.circle(superficie, cor, (cx-11,cy-12), max(1,int(2*esc)))
    if nivel >= 3:
        pygame.draw.line(superficie, cor, (cx+6,cy-16),(cx+9,cy-20), max(1,int(esc)))
    if nivel >= 4 and not leve:
        pygame.draw.arc(superficie, cor, (cx-22,cy-23,44,40), 0.25, 2.7, 1)
    if nivel >= 5 and not leve and (frame//12)%2==0:
        pygame.draw.line(superficie, cor, (cx-3,cy-26),(cx+3,cy-26), 2)
        pygame.draw.line(superficie, cor, (cx,cy-29),(cx,cy-23), 2)
    if pontos >= 25:
        pygame.draw.circle(superficie, (255,222,139), (cx+17,cy-14), 2)
    if pontos >= 60:
        pygame.draw.line(superficie, (255,144,197), (cx-17,cy-16),(cx-11,cy-19), 2)
    if pontos >= 100 and (frame//16)%2==0:
        pygame.draw.circle(superficie, (255,239,170), (cx+18,cy-24), 2)


def desenhar_recarga_pet(superficie, pet_id, pos, frame, salvo=False, leve=False):
    # Somente poderes de recarga e proteção têm indicador. Nunca altera o cooldown.
    tempos = {"DRAGAO_PLASMA": 150, "ABELHA_MAGNETICA": 90}
    if pet_id not in tempos and pet_id != "FANTASMA":
        return
    progresso = (frame % tempos[pet_id]) / tempos[pet_id] if pet_id in tempos else (0.0 if salvo else 1.0)
    cor = _PET_CORES_ENERGIA[pet_id]
    x, y = int(pos[0]), int(pos[1])
    pygame.draw.circle(superficie, (27,32,54), (x,y), 7)
    pygame.draw.circle(superficie, (160,170,200), (x,y), 7, 1)
    if progresso > 0:
        # Quatro arcos discretos; renderiza sem surfaces ou transformações extras.
        n = max(1,int(progresso*8))
        for i in range(n):
            a = 6.28 * i / 8 - 1.57
            b = 6.28 * (i+0.65) / 8 - 1.57
            pygame.draw.arc(superficie, cor, (x-5,y-5,10,10), a,b,2)
    if not leve:
        pygame.draw.circle(superficie, (235,243,255), (x,y), 2)


def humor_pet_visual(dados, pet_id):
    reg = registro_pet(dados, pet_id)
    if not reg:
        return "Desconhecido", (180, 190, 210)
    pontos = int(reg.get("pontos", 0))
    carinho = int(reg.get("carinhos", 0))
    brincar = int(reg.get("brincadeiras", 0))
    if pontos >= 90:
        return "Radiante", (255, 228, 128)
    if brincar >= 2:
        return "Brincalhão", (115, 231, 255)
    if carinho >= 2:
        return "Carinhoso", (255, 178, 222)
    if pontos >= 45:
        return "Tranquilo", (151, 239, 197)
    if pontos >= 15:
        return "Curioso", (171, 215, 255)
    return "Tímido", (180, 190, 210)


def desenhar_capsula_info(superficie, rect, rotulo, valor, cor):
    pygame.draw.rect(superficie, (18, 26, 42), rect.move(0, 2), border_radius=10)
    pygame.draw.rect(superficie, (27, 38, 57), rect, border_radius=10)
    pygame.draw.rect(superficie, misturar_cores(cor, BRANCO, 0.28), rect, 1, border_radius=10)
    desenhar_texto_com_sombra(superficie, rotulo, fonte_pequena, (174, 200, 220), PRETO, (rect.x + 9, rect.y + 6))
    desenhar_texto_com_sombra(superficie, valor, fonte_missoes, cor, PRETO, (rect.x + 9, rect.y + 24))


def desenhar_selo_status_loja(superficie, x, y, texto, cor_fundo, cor_texto=BRANCO):
    surf = render_texto_cacheado(fonte_pequena, texto, cor_texto)
    rect = pygame.Rect(x, y, max(42, surf.get_width() + 14), 16)
    pygame.draw.rect(superficie, (9, 14, 24), rect.move(0, 2), border_radius=8)
    pygame.draw.rect(superficie, cor_fundo, rect, border_radius=8)
    pygame.draw.rect(superficie, misturar_cores(cor_fundo, BRANCO, 0.35), rect, 1, border_radius=8)
    superficie.blit(surf, (rect.centerx - surf.get_width() // 2, rect.y + 2))


_CANTINHO_PETS_MINIS = {}


PET_ESTADO_PRIORIDADE = {
    'MORRER': 100, 'HABILIDADE': 95, 'IMPULSO': 90, 'SUBINDO': 88, 'APICE': 86, 'CAINDO': 84,
    'POUSO': 80, 'AGACHAR': 70, 'FESTA': 65, 'ALERTA': 60, 'ALIVIO': 55, 'CURIOSO': 45,
    'BRINCAR': 42, 'CARINHO': 40, 'ESPERA': 20, 'CORRER': 10
}
PET_ESTADO_DURACAO_MIN = {
    'MORRER': 9999, 'HABILIDADE': 16, 'IMPULSO': 8, 'SUBINDO': 6, 'APICE': 5, 'CAINDO': 6,
    'POUSO': 8, 'AGACHAR': 6, 'FESTA': 14, 'ALERTA': 10, 'ALIVIO': 10, 'CURIOSO': 14,
    'BRINCAR': 14, 'CARINHO': 14, 'ESPERA': 18, 'CORRER': 0
}



def _alvo_visual_pet_corrida(jogador, pet_id, frame_count):
    """Aterramento visual exato, independente dos fps (sem alterar hitbox).

    Baseline dos PNGs é 70/76px de altura. No solo os pés coincidem com
    jogador.chao_y; no ar seguem a trajetória vertical do jogador.
    """
    voador=pet_eh_voador(pet_id)
    px=max(26.0 if voador else 23.0,
           float(jogador.rect.left-(38 if voador else 43)))
    if voador:
        # Voo natural: asas produzem movimento, não o tronco inteiro oscilando.
        py=float(jogador.rect.centery-5)
        if not jogador.no_chao:
            py-=7
        if jogador.agachado and jogador.no_chao:
            py+=7
        py+=0.35*math.sin(frame_count*0.12)
        return px,py
    # 44x40 de exibição: (baseline 70/76)*40 - 20 = +16,84px
    centro_no_chao=float(jogador.chao_y-17)
    if jogador.no_chao or jogador.morrendo:
        return px,centro_no_chao
    deslocamento=float(jogador.rect.bottom-jogador.chao_y)
    # Durante pulo/queda segue o personagem com atraso pequeno e arcada própria.
    py=centro_no_chao + max(-160.0,min(0.0,deslocamento*0.82))
    return px,py



def atualizar_estado_visual_pet(frame_count, estado_atual, estado_desde, estado_travado_ate, memoria,
                                jogador, perigo_proximo, moedas_proximas, febre_timer, pet_reacao_ate,
                                pet_habilidade_ate, pet_pouso_ate, pet_alivio_ate):
    memoria = memoria or {}
    if jogador is None:
        return 'ESPERA', frame_count, frame_count, memoria

    desejado = 'CORRER'
    if jogador.morrendo:
        desejado = 'MORRER'
    elif not jogador.no_chao and getattr(jogador, "descida_rapida", False):
        desejado = "SWIPE_DOWN"
    elif not jogador.no_chao:
        vy_pet = float(jogador.velocidade_y)
        if getattr(jogador, 'anim_pulo_frames', 0) < 5 and vy_pet < -3:
            desejado = 'IMPULSO'
        elif vy_pet < -2:
            desejado = 'SUBINDO'
        elif vy_pet > 2:
            desejado = 'CAINDO'
        else:
            desejado = 'APICE'
    elif frame_count < pet_pouso_ate:
        desejado = 'POUSO'
    elif jogador.agachado:
        desejado = 'AGACHAR'
    elif frame_count < pet_habilidade_ate:
        desejado = 'HABILIDADE'
    elif febre_timer > 0 or frame_count < pet_reacao_ate:
        desejado = 'FESTA'
    elif perigo_proximo:
        desejado = 'ALERTA'
    elif frame_count < pet_alivio_ate:
        desejado = 'ALIVIO'
    else:
        cool_curioso = int(memoria.get('cool_curioso', 0))
        if moedas_proximas and frame_count >= cool_curioso:
            desejado = 'CURIOSO'
            memoria['cool_curioso'] = frame_count + 42
        elif frame_count >= int(memoria.get('cool_ocioso', 0)) and (frame_count // 210) % 5 == 4:
            desejado = 'CURIOSO'
            memoria['cool_ocioso'] = frame_count + 150
        else:
            desejado = 'CORRER'

    if estado_atual == "SWIPE_DOWN" and jogador.no_chao:
        estado_travado_ate = frame_count
    if estado_atual != desejado:
        prio_atual = PET_ESTADO_PRIORIDADE.get(estado_atual, 0)
        prio_desejado = PET_ESTADO_PRIORIDADE.get(desejado, 0)
        travado = frame_count < estado_travado_ate
        # Estado fisico do jogador prevalece sobre efeitos visuais temporarios.
        estados_fisicos = ('MORRER', 'SWIPE_DOWN', 'IMPULSO', 'SUBINDO', 'APICE',
                           'CAINDO', 'POUSO', 'AGACHAR')
        if (not travado) or (prio_desejado >= prio_atual) or desejado in estados_fisicos:
            estado_atual = desejado
            estado_desde = frame_count
            estado_travado_ate = frame_count + PET_ESTADO_DURACAO_MIN.get(desejado, 0)
    else:
        minimo = PET_ESTADO_DURACAO_MIN.get(estado_atual, 0)
        if minimo > 0 and estado_travado_ate < frame_count + minimo // 3:
            estado_travado_ate = max(estado_travado_ate, frame_count + minimo // 3)

    if estado_atual == 'CURIOSO' and not (moedas_proximas or (frame_count - estado_desde) < 10):
        if frame_count >= estado_travado_ate:
            estado_atual = 'CORRER'
            estado_desde = frame_count
            estado_travado_ate = frame_count
    return estado_atual, estado_desde, estado_travado_ate, memoria


def desenhar_cantinho_pets(superficie, dados, pet_atual, frame, acao, acao_ate, mensagem, mensagem_ate, leve=False):
    """Tela premium leve: coleção, vínculo e interações sem afetar a jogabilidade."""
    pygame.draw.rect(superficie, (12, 20, 37), (16, 13, 418, 776), border_radius=16)
    pygame.draw.rect(superficie, (94, 215, 238), (16, 13, 418, 776), 2, border_radius=16)
    pygame.draw.rect(superficie, (28, 42, 68), (24, 21, 402, 94), border_radius=12)
    pygame.draw.line(superficie, (170, 236, 251), (40, 98), (400, 98), 1)
    desbloqueados = set(dados.get("pets_desbloqueados", []))
    total_desbloq = len(desbloqueados)
    equip_nome = PETS_CONFIG.get(dados.get("pet_equipado", ""), {}).get("nome", "Nenhum")
    desenhar_texto_centralizado(superficie, "CANTINHO DOS PETS", fonte_grande, (255, 228, 131), PRETO, 31)
    desenhar_texto_centralizado(superficie, f"Desbloqueados {total_desbloq}/{len(PETS_CONFIG)}  •  Equipado: {equip_nome}", fonte_missoes,
                                (171, 236, 251), PRETO, 79)
    for i, (pid, pet) in enumerate(PETS_CONFIG.items()):
        x, y = 12 + (i % 3) * 142, 144 + (i // 3) * 94
        carta = pygame.Rect(x, y, 134, 84)
        selecionado = pet_atual == pid
        aberto = pid in desbloqueados
        cor = pet["cor"] if aberto else (83, 96, 113)
        pygame.draw.rect(superficie, (24, 34, 52) if aberto else (20, 28, 41), carta.move(0, 3), border_radius=11)
        pygame.draw.rect(superficie, (28, 38, 59) if aberto else (22, 29, 43), carta, border_radius=11)
        pygame.draw.rect(superficie, cor if selecionado else (62, 93, 116), carta, 3 if selecionado else 1, border_radius=11)
        if selecionado and not leve:
            pygame.draw.rect(superficie, misturar_cores(cor, BRANCO, 0.3), carta.inflate(4, 4), 1, border_radius=12)
        pygame.draw.rect(superficie, misturar_cores(cor, BRANCO, 0.35), (x + 12, y + 10, 48, 1), border_radius=1)
        if aberto:
            mini = _CANTINHO_PETS_MINIS.get(pid)
            if mini is None:
                mini = _quadros_pet_estado(pid, "ESPERA", (64, 55))[0]
                _CANTINHO_PETS_MINIS[pid] = mini
            superficie.blit(mini, (x + 8, y + 5))
            desenhar_selo_status_loja(superficie, x + 83, y + 9, "EQUI." if dados.get("pet_equipado") == pid else "LIVRE", (58, 135, 138) if dados.get("pet_equipado") == pid else (61, 100, 138))
        else:
            pygame.draw.circle(superficie, (73, 84, 104), (x + 37, y + 32), 17)
            pygame.draw.rect(superficie, (164, 172, 190), (x + 30, y + 26, 14, 15), 2, border_radius=3)
            pygame.draw.arc(superficie, (164, 172, 190), (x + 32, y + 18, 10, 14), 0, math.pi, 2)
            desenhar_selo_status_loja(superficie, x + 84, y + 9, "LOCK", (75, 86, 106))
        texto = pet["nome"] if len(pet["nome"]) <= 16 else pet["nome"][:15] + "…"
        surf_nome = render_texto_cacheado(fonte_pequena, texto, BRANCO if aberto else (139, 150, 172))
        superficie.blit(surf_nome, (x + 67 - surf_nome.get_width() // 2, y + 61))

    detalhe = pygame.Rect(23, 438, 404, 187)
    pygame.draw.rect(superficie, (31, 43, 65), detalhe, border_radius=14)
    pygame.draw.rect(superficie, (93, 154, 188), detalhe, 2, border_radius=14)
    if pet_atual not in PETS_CONFIG:
        return
    pet = PETS_CONFIG[pet_atual]
    aberto = pet_atual in desbloqueados
    cor = pet["cor"]
    pygame.draw.ellipse(superficie, (17, 26, 43), (42, 579, 130, 18))
    pygame.draw.ellipse(superficie, (27, 44, 66), (54, 460, 108, 108))
    if aberto:
        estado = acao if frame < acao_ate else "ESPERA"
        quadros = _quadros_pet_estado(pet_atual, estado, (126, 110))
        img = quadros[(frame // (7 if estado in ("BRINCAR", "CARINHO") else 11)) % len(quadros)]
        superficie.blit(img, (42, 455))
        desenhar_evolucao_pet(superficie, pet_atual, 105, 510, dados, frame, tamanho=(126, 110), leve=leve)
        if not leve:
            desenhar_fx_pet(superficie, pet_atual, (106, 515), frame, 0.7, leve)
    else:
        pygame.draw.circle(superficie, (84, 100, 120), (107, 509), 35)
        desenhar_texto_centralizado(superficie, "PET BLOQUEADO", fonte_missoes, (182, 190, 208), PRETO, 500)

    titulo = render_texto_cacheado(fonte_missoes, pet["nome"], cor if aberto else (175, 184, 199))
    if titulo.get_width() > 218:
        titulo = pygame.transform.scale(titulo, (215, titulo.get_height()))
    superficie.blit(titulo, (184, 452))
    reg = registro_pet(dados, pet_atual) if aberto else {"pontos": 0, "lembrancas": [], "carinhos": 0, "brincadeiras": 0}
    pontos = reg["pontos"]
    nivel = nivel_pet(dados, pet_atual) if aberto else 1
    xp = dados.get("evolucao_pets", {}).get(pet_atual, {}).get("xp", 0)
    humor, cor_humor = humor_pet_visual(dados, pet_atual) if aberto else ("Bloqueado", (170, 180, 196))
    desenhar_texto_com_sombra(superficie, f"NÍVEL {nivel}/5  •  XP {xp}", fonte_pequena, BRANCO, PRETO, (184, 480))
    desenhar_selo_status_loja(superficie, 331, 451, "EQUIPADO" if dados.get("pet_equipado") == pet_atual and aberto else ("DISPONÍVEL" if aberto else "BLOQ."),
                              (53, 157, 112) if dados.get("pet_equipado") == pet_atual and aberto else ((72, 118, 166) if aberto else (80, 89, 105)))
    desenhar_texto_com_sombra(superficie, f"Humor: {humor}", fonte_pequena, cor_humor, PRETO, (184, 501))
    pygame.draw.rect(superficie, (15, 23, 41), (183, 522, 222, 13), border_radius=6)
    if pontos > 0:
        pygame.draw.rect(superficie, (100, 222, 189), (185, 524, max(1, int(218 * pontos / 100)), 9), border_radius=5)
    pygame.draw.rect(superficie, (122, 175, 196), (183, 522, 222, 13), 1, border_radius=6)
    desenhar_texto_com_sombra(superficie, f"Vínculo {pontos}/100", fonte_pequena, (255, 222, 158), PRETO, (184, 538))
    desenhar_capsula_info(superficie, pygame.Rect(184, 558, 72, 47), "Carinhos", f"{reg.get('carinhos', 0)}/3", (255, 183, 224))
    desenhar_capsula_info(superficie, pygame.Rect(261, 558, 72, 47), "Brincar", f"{reg.get('brincadeiras', 0)}/3", (118, 232, 255))
    desenhar_capsula_info(superficie, pygame.Rect(338, 558, 72, 47), "Memórias", f"{len(reg.get('lembrancas', []))}/3", (255, 222, 120))
    for i, (minimo, code, nome) in enumerate(LEMBRANCAS_PETS):
        lx = 188 + i * 74
        conquistou = code in reg["lembrancas"]
        col = (255, 211, 105) if conquistou else (78, 91, 111)
        pygame.draw.circle(superficie, col, (lx + 15, 555), 10)
        if conquistou:
            pygame.draw.line(superficie, BRANCO, (lx + 12, 554), (lx + 18, 554), 2)
            pygame.draw.line(superficie, BRANCO, (lx + 15, 551), (lx + 15, 557), 2)
    msg = mensagem if frame < mensagem_ate else ("Carinho: {}/3  •  Brincar: {}/3".format(reg["carinhos"], reg["brincadeiras"]) if aberto else "Visite a loja para desbloquear")
    texto_msg = render_texto_cacheado(fonte_pequena, msg, (184, 247, 217))
    if texto_msg.get_width() > 370:
        texto_msg = pygame.transform.scale(texto_msg, (370, texto_msg.get_height()))
    pygame.draw.rect(superficie, (20, 29, 46), (28, 613, 394, 23), border_radius=8)
    superficie.blit(texto_msg, (225 - texto_msg.get_width() // 2, 617))
    for rect, rotulo in ((pygame.Rect(24, 643, 124, 48), "CARINHO"),
                         (pygame.Rect(163, 643, 124, 48), "BRINCAR"),
                         (pygame.Rect(302, 643, 124, 48), "EQUIPAR")):
        cor_b = (58, 135, 138) if aberto else (68, 75, 89)
        pygame.draw.rect(superficie, (16, 24, 39), rect.move(0, 3), border_radius=9)
        pygame.draw.rect(superficie, cor_b, rect, border_radius=9)
        pygame.draw.rect(superficie, (198, 233, 245), rect, 1, border_radius=9)
        if not leve and aberto and (frame // 24) % 2 == 0 and rotulo != "EQUIPAR":
            pygame.draw.rect(superficie, misturar_cores(cor_b, BRANCO, 0.18), (rect.x + 8, rect.y + 6, rect.w - 16, 6), border_radius=4)
        desenhar_rotulo_botao(superficie, rotulo, fonte_missoes, BRANCO, PRETO, rect)
    voltar = pygame.Rect(75, 710, 300, 48)
    pygame.draw.rect(superficie, (55, 72, 96), voltar, border_radius=10)
    pygame.draw.rect(superficie, BRANCO, voltar, 2, border_radius=10)
    desenhar_rotulo_botao(superficie, "VOLTAR À LOJA", fonte, BRANCO, PRETO, voltar)


# --- MINIATURAS DOS MESMOS PERSONAGENS USADOS NA CORRIDA ---
def desenhar_mini_skin(surface, skin_nome, cx, cy):
    mini = _SKIN_MINIATURAS.get(skin_nome)
    if mini is None:
        mini = _sprite_skin_enquadrado(skin_nome, 'OCIOSO', 0, 44, 48, 1)
        _SKIN_MINIATURAS[skin_nome] = mini
    surface.blit(mini, (cx - 22, cy - 24))


CHAVE_TRANSPARENCIA_SPRITES = (255, 0, 255)
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
    # Variantes leves para evitar repeticao visual sem custo por frame.
    _imagens_variantes = None

    @staticmethod
    def _criar_variantes():
        variantes = []
        for estilo in range(4):
            imagem = pygame.Surface((24, 24)).convert()
            imagem.fill(CHAVE_TRANSPARENCIA_SPRITES)
            cor_brilho = (255, 243, 161)
            cor_sombra = (209, 155, 22)
            pygame.draw.circle(imagem, cor_sombra, (12, 12), 11)
            pygame.draw.circle(imagem, AMARELO_MOEDA, (11, 11), 10)
            pygame.draw.circle(imagem, (255, 236, 115), (11, 11), 8)
            pygame.draw.circle(imagem, PRETO, (11, 11), 11, 2)
            pygame.draw.circle(imagem, cor_brilho, (8, 8), 3)
            pygame.draw.circle(imagem, (230, 180, 35), (11, 11), 4, 1)
            pygame.draw.rect(imagem, (255, 249, 205), (7, 5, 3, 2))
            pygame.draw.line(imagem, (255, 228, 90), (11, 8), (11, 14), 1)
            pygame.draw.rect(imagem, (217, 150, 27), (17, 15, 3, 2))
            if estilo == 1:
                pygame.draw.line(imagem, cor_brilho, (16, 2), (16, 7), 1)
                pygame.draw.line(imagem, cor_brilho, (13, 4), (19, 4), 1)
            elif estilo == 2:
                pygame.draw.circle(imagem, (255, 250, 223), (15, 6), 2)
                pygame.draw.circle(imagem, (255, 236, 115), (16, 16), 2)
            elif estilo == 3:
                pygame.draw.rect(imagem, cor_brilho, (15, 3, 4, 3))
                pygame.draw.line(imagem, cor_brilho, (17, 1), (17, 7), 1)
                pygame.draw.line(imagem, cor_brilho, (14, 4), (20, 4), 1)
            else:
                pygame.draw.rect(imagem, cor_brilho, (16, 4, 3, 3))
                pygame.draw.line(imagem, cor_brilho, (17, 1), (17, 6), 1)
                pygame.draw.line(imagem, cor_brilho, (14, 4), (20, 4), 1)
            imagem.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
            variantes.append(imagem)
        return variantes

    def __init__(self, x_pos=0, y_pos=0):
        super().__init__()
        self.pool_manager = None
        self._pool_livre = False
        if Moeda._imagens_variantes is None:
            Moeda._imagens_variantes = Moeda._criar_variantes()
        self.image = random.choice(Moeda._imagens_variantes)
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self._x_float = float(self.rect.x)
        self._y_float = float(self.rect.y)
        self.ativo = True

    def kill(self):
        super().kill()
        manager = self.pool_manager
        if manager is not None and not self._pool_livre:
            self.ativo = False
            self._pool_livre = True
            manager.moedas_disponiveis.append(self)

    def reset(self, x_pos, y_pos):
        if Moeda._imagens_variantes is not None:
            self.image = random.choice(Moeda._imagens_variantes)
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self._x_float = float(self.rect.x)
        self._y_float = float(self.rect.y)
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
                self._x_float += (dx / distancia) * 12.0
                self._y_float += (dy / distancia) * 12.0
        self._x_float -= float(velocidade_jogo)
        self.rect.x = int(round(self._x_float))
        self.rect.y = int(round(self._y_float))
        if self.rect.right < -50:
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
    # Em dispositivos lentos a acao ocorre igual, mas somente a decoracao e reduzida.
    if PARTICULAS_VISUAIS_LIMITADAS:
        quantidade = max(2, int(quantidade * 0.45))
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
        # v3.247.0: localizar SOMENTE a imagem do popup, sem mudar mensagem,
        # bonus, regras ou identificadores gravados. Renderizado uma vez por popup.
        if _IDIOMA_ATUAL_I18N not in ('pt_BR', 'en_US'):
            texto = _i18n247.localizar_literal(texto, _IDIOMA_ATUAL_I18N)
            if fnt.size(texto)[0] > LARGURA_VIRTUAL - 16:
                fnt = fonte
            texto = texto_ajustado_hud(texto, fnt, LARGURA_VIRTUAL - 16)
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
        # Popup com pequena trajetória balística (apenas visual).
        self.vy = -2.7
        self.gravidade_popup = 0.047
        self.y_popup = float(self.rect.y)

    def update(self, *args):
        self.y_popup += self.vy
        self.vy += self.gravidade_popup
        self.rect.y = int(round(self.y_popup))
        self.vida -= 1
        if self.vida <= 0:
            self.kill()
        else:
            self.image.set_alpha(max(0, min(255, int((self.vida / float(self.vida_max)) * 255))))


from pixelrush_feedback_v3190 import aprimorar_texto_flutuante
TextoFlutuante = aprimorar_texto_flutuante(TextoFlutuante)

# --- PARALLAX BACKGROUND ---
def desenhar_detalhes_bioma_cacheado(tile, bioma, camada):
    """Arte adicional rasterizada SOMENTE na criação de tiles (sem custo por frame)."""
    frente = camada == 'predios'
    for sec in range(2):
        xb = sec * LARGURA_VIRTUAL
        if bioma == 'cidade':
            if frente:
                for x, y in ((62, 58), (252, 27), (383, 78)):
                    pygame.draw.line(tile, (117, 155, 182), (xb+x, y+20), (xb+x, y), 2)
                    pygame.draw.rect(tile, (250, 203, 108), (xb+x-2, y-3, 5, 3))
            else:
                for x, y in ((20, 274), (205, 282), (354, 267)):
                    pygame.draw.line(tile, (171, 199, 219), (xb+x, y), (xb+x+20, y-3), 1)
        elif bioma == 'deserto':
            if frente:
                for x in (74, 291):
                    pygame.draw.polygon(tile, (139, 104, 72), [(xb+x-14, 230), (xb+x, 194), (xb+x+16, 230)])
                    pygame.draw.polygon(tile, (222, 171, 92), [(xb+x, 194), (xb+x+16,230), (xb+x,230)])
            else:
                # Dunas desenhadas com pontos espaçados para não competirem com perigos.
                for x in (45, 206, 368):
                    pygame.draw.line(tile, (236, 202, 143), (xb+x, 294), (xb+x+19, 291), 2)
        elif bioma == 'neve':
            if frente:
                for x in (65, 275):
                    pygame.draw.polygon(tile, (73, 120, 149), [(xb+x, 211),(xb+x-17,240),(xb+x+17,240)])
                    pygame.draw.polygon(tile, (137, 194, 221), [(xb+x, 222),(xb+x-21,254),(xb+x+21,254)])
                    pygame.draw.line(tile, (235, 248, 254), (xb+x, 214), (xb+x-5,226), 2)
            else:
                for x in (91, 251, 386):
                    pygame.draw.line(tile, (232, 247, 255), (xb+x, 260), (xb+x+20, 254), 2)
        elif bioma == 'vulcao':
            if frente:
                for x, y in ((58, 196),(222,160),(406,188)):
                    pygame.draw.line(tile, (255, 124, 59), (xb+x, y+17), (xb+x+5, y), 2)
                    pygame.draw.rect(tile, (255, 222, 95), (xb+x+4, y-2, 4, 3))
            else:
                for x, y in ((44, 244), (252, 221), (409, 254)):
                    pygame.draw.rect(tile, (255, 155, 65), (xb+x, y, 3, 4))
        elif bioma == 'cidade_futurista':
            if frente:
                for x, y in ((49, 66), (212, 43), (389, 77)):
                    pygame.draw.line(tile, (94, 238, 249), (xb+x, y),(xb+x+18,y), 2)
                    pygame.draw.line(tile, (185, 105, 242), (xb+x+10, y),(xb+x+10,y+12), 1)
            else:
                for x, y in ((93, 211),(332, 202)):
                    pygame.draw.line(tile, (76, 218, 247), (xb+x, y),(xb+x+44,y), 1)
        elif bioma == 'floresta':
            if frente:
                for x, y in ((66,198), (248,211),(392,194)):
                    pygame.draw.line(tile, (104, 171, 97), (xb+x,y+18),(xb+x,y), 2)
                    pygame.draw.ellipse(tile, (140, 208, 112), (xb+x-9,y-4,18,12))
                    pygame.draw.rect(tile, (247, 234, 137), (xb+x+2,y+2,2,2))
            else:
                for x, y in ((74,240), (212,269), (395,245)):
                    pygame.draw.circle(tile, (235, 242, 145), (xb+x,y), 2)
        elif bioma == 'reino_submerso':
            if frente:
                for x, y in ((75,205),(284,197),(412,213)):
                    pygame.draw.line(tile, (54, 171, 168), (xb+x,y+28),(xb+x,y), 2)
                    pygame.draw.line(tile, (96, 224, 202), (xb+x,y+15),(xb+x-9,y+3), 2)
                    pygame.draw.circle(tile, (174, 241, 252), (xb+x+12,y-10), 3, 1)
            else:
                for x, y in ((89,257),(320,224)):
                    pygame.draw.circle(tile, (122, 229, 238), (xb+x,y), 5, 1)
        elif bioma == 'ilhas_celestes':
            if frente:
                for x, y in ((62,160),(228,148),(393,166)):
                    pygame.draw.line(tile, (237, 250, 255), (xb+x,y), (xb+x+13,y-7), 2)
                    pygame.draw.line(tile, (237, 250, 255), (xb+x+13,y-7), (xb+x+30,y-7), 1)
            else:
                for x, y in ((57,210),(293,174)):
                    pygame.draw.line(tile, (232, 249, 255), (xb+x,y), (xb+x+37,y), 1)


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
            {"x": random.randint(4, LARGURA_VIRTUAL - 4), "y": random.randint(12, 355),
             "blink": random.uniform(0.035, 0.095), "offset": random.uniform(0, math.pi * 2),
             "brilho": random.uniform(0.68, 1.0), "tamanho": random.choice((1, 1, 2))}
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
        self._cache_chao = {}
        self.desloc_chao = 0.0
        self.fase_ciclo = 0.0
        self.peso_noite = 0.0
        self.cenario = "cidade"
        # v3.93: apenas uma faixa artística de bioma em memoria por vez.
        # Cenarios pre-renderizados offline, sem geracao em tempo de corrida.
        self._arte_externa = None
        self._arte_externa_fundo = None
        self._arte_externa_meio = None
        self._arte_bioma_carregado = None
        self._desloc_arte = 0.0
        self._desloc_arte_fundo = 0.0
        self._overlay_arte_noite = pygame.Surface((LARGURA_VIRTUAL, 500)).convert()
        self._overlay_arte_noite.fill((13, 19, 43))
        self._overlay_arte_noite.set_alpha(0)
        self._particulas_ambiente = []
        self.clima_tipo = "limpo"
        self._usa_bioma_vivo = True
        self._mundo_cenario = 0.0
        self.world = LivingWorld(self.cenario, lightweight=bool(E_ANDROID and self.cenario in ('cidade','neve','deserto','floresta','vulcao','cidade_futurista','ilhas_celestes')))
        self._reiniciar_particulas_ambiente()

    def set_cenario(self, cenario):
        if cenario == self.cenario:
            return
        self.cenario = cenario
        self._cache_montanhas_key = None
        self._cache_predios_key = None
        self._cache_montanhas = None
        self._cache_predios = None
        self._arte_externa = None
        self._arte_externa_fundo = None
        self._arte_externa_meio = None
        self._arte_bioma_carregado = None
        self._desloc_arte = 0.0
        self._desloc_arte_fundo = 0.0
        self._mundo_cenario = 0.0
        self.world.switch(cenario)
        self.world.lightweight = bool(E_ANDROID and cenario in ('cidade','neve','deserto','floresta','vulcao','cidade_futurista','ilhas_celestes'))
        self._reiniciar_particulas_ambiente()

    def tem_arte_externa(self):
        """Indica que existe cenario novo (sprites ou faixa antiga)."""
        return self._bioma_spriteado_ativo() or self._arte_externa is not None

    def _obter_arte_externa(self):
        """Carregamento tardio e unico: evita manter sete fundos grandes em RAM.
        v3.99: biomas principais usam renderização viva/procedural em vez de faixa PNG.
        """
        if self._usa_bioma_vivo and self.cenario in (
                'cidade', 'neve', 'deserto', 'vulcao',
                'cidade_futurista', 'floresta', 'ilhas_celestes'):
            self._arte_bioma_carregado = self.cenario
            self._arte_externa = None
            self._arte_externa_fundo = None
            self._arte_externa_meio = None
            return None
        if self._arte_bioma_carregado == self.cenario:
            return self._arte_externa
        self._arte_bioma_carregado = self.cenario
        self._arte_externa = None
        if self.cenario not in (
                'cidade', 'neve', 'deserto', 'vulcao',
                'cidade_futurista', 'floresta', 'ilhas_celestes'):
            return None
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'pixelrush_biomas_v3.97', self.cenario + '.png')
        if os.path.isfile(caminho):
            try:
                self._arte_externa = pygame.image.load(caminho).convert_alpha()
                self._arte_externa_fundo = None
                self._arte_externa_meio = None
            except (pygame.error, OSError, ValueError):
                self._arte_externa = None
                self._arte_externa_fundo = None
                self._arte_externa_meio = None
        return self._arte_externa

    def update(self, velocidade_jogo=1.0, metros_atuais=None):
        self.tempo_animacao += 1
        if metros_atuais is not None:
            self.fase_ciclo, _cor_alvo, self.peso_noite, _noite = calcular_ciclo_ceu(metros_atuais)
        self.camada_longe -= velocidade_jogo * 0.08
        if self.camada_longe <= -LARGURA_VIRTUAL:
            self.camada_longe += LARGURA_VIRTUAL
        # Parallax artistico com duas velocidades para separar melhor profundidade.
        vel_base = max(0.0, float(velocidade_jogo))
        self._mundo_cenario += vel_base
        self.world.update(vel_base, self.peso_noite, self.clima_tipo, self.fase_ciclo)
        self._desloc_arte_fundo = (self._desloc_arte_fundo + vel_base * 0.06) % 2700.0
        self._desloc_arte = (self._desloc_arte + vel_base * 0.19) % 2700.0
        self.camada_perto -= velocidade_jogo * 0.24
        if self.camada_perto <= -LARGURA_VIRTUAL:
            self.camada_perto += LARGURA_VIRTUAL
        self._atualizar_particulas_ambiente(vel_base)
        # O piso representa o mesmo plano dos obstaculos terrestres: deve deslizar
        # exatamente na mesma velocidade horizontal para parecer parte do mundo,
        # e nao uma animacao independente. O tile mais comprido reduz repeticoes visiveis.
        self.desloc_chao = (self.desloc_chao + max(0.0, float(velocidade_jogo))) % 900.0
        for nuvem in self.nuvens:
            nuvem["x"] -= nuvem["vel"] + (velocidade_jogo * 0.05)
            if nuvem["x"] < -80:
                nuvem["x"] = LARGURA_VIRTUAL + 40
                nuvem["y"] = random.randint(20, 200)

    def _reiniciar_particulas_ambiente(self):
        cfg = {
            "cidade": ((170, 206, 234), (226, 198, 120), 8),
            "neve": ((238, 246, 255), (192, 221, 240), 14),
            "deserto": ((240, 210, 160), (214, 170, 116), 9),
            "vulcao": ((255, 149, 82), (247, 205, 123), 8),
            "floresta": ((157, 217, 124), (245, 235, 146), 8),
            "cidade_futurista": ((94, 238, 249), (206, 108, 255), 9),
            "ilhas_celestes": ((226, 248, 255), (152, 240, 206), 8),
            "reino_submerso": ((122, 229, 238), (174, 241, 252), 9),
        }
        cores = cfg.get(self.cenario, ((196, 210, 224), (235, 240, 245), 8))
        rng = random.Random(7000 + sum(ord(c) for c in self.cenario))
        self._particulas_ambiente = []
        for i in range(cores[2]):
            self._particulas_ambiente.append({
                "x": rng.uniform(0, LARGURA_VIRTUAL),
                "y": rng.uniform(190, 560),
                "vx": rng.uniform(0.04, 0.22),
                "vy": rng.uniform(-0.03, 0.03),
                "tam": rng.choice((1, 1, 2, 2, 3 if self.cenario in ("neve", "cidade_futurista") else 2)),
                "fase": rng.uniform(0.0, math.tau),
                "cor_a": cores[0],
                "cor_b": cores[1],
            })

    def _atualizar_particulas_ambiente(self, velocidade_base):
        if not self._particulas_ambiente:
            return
        drift_x = 0.14 if self.cenario != "deserto" else 0.24
        drift_y = 0.05 if self.cenario in ("neve", "ilhas_celestes", "reino_submerso") else 0.025
        for p in self._particulas_ambiente:
            p["x"] -= (p["vx"] + velocidade_base * drift_x)
            p["fase"] += 0.035
            p["y"] += math.sin(p["fase"]) * drift_y + p["vy"]
            if p["x"] < -12:
                p["x"] = LARGURA_VIRTUAL + 10
                p["y"] = random.uniform(190, 560)
            if p["y"] < 180:
                p["y"] = 180
            elif p["y"] > 570:
                p["y"] = 570

    def _desenhar_particulas_ambiente(self, superficie):
        if not self._particulas_ambiente:
            return
        for p in self._particulas_ambiente:
            brilho = (math.sin(p["fase"]) + 1.0) * 0.5
            cor = misturar_cores(p["cor_a"], p["cor_b"], brilho * 0.55)
            x = int(p["x"])
            y = int(p["y"])
            tam = int(p["tam"])
            if self.cenario == "neve":
                pygame.draw.rect(superficie, cor, (x, y, tam, tam))
                if tam > 1:
                    pygame.draw.line(superficie, cor, (x - 1, y), (x + tam, y), 1)
            elif self.cenario == "deserto":
                pygame.draw.line(superficie, cor, (x, y), (x + tam + 1, y - 1), 1)
            elif self.cenario == "vulcao":
                pygame.draw.rect(superficie, cor, (x, y, tam, tam))
            elif self.cenario == "cidade_futurista":
                pygame.draw.rect(superficie, cor, (x, y, tam + 1, 1))
                pygame.draw.rect(superficie, p["cor_b"], (x, y + 1, tam, 1))
            elif self.cenario == "floresta":
                pygame.draw.circle(superficie, cor, (x, y), max(1, tam - 1))
            else:
                pygame.draw.rect(superficie, cor, (x, y, tam, tam))

    def _desenhar_faixa_loop(self, superficie, arte, deslocamento, destino_y, area_origem):
        if arte is None:
            return
        largura_total = arte.get_width()
        altura = area_origem.height
        desloc = int(deslocamento) % largura_total
        largura_visivel = min(LARGURA_VIRTUAL, largura_total - desloc)
        superficie.blit(arte, (0, destino_y), (desloc, area_origem.y, largura_visivel, altura))
        if largura_visivel < LARGURA_VIRTUAL:
            superficie.blit(arte, (largura_visivel, destino_y), (0, area_origem.y, LARGURA_VIRTUAL - largura_visivel, altura))

    def _desenhar_arte_externa_em_camadas(self, superficie):
        if self._arte_externa is None:
            return
        arte = self._arte_externa
        h = arte.get_height()
        src_fundo = pygame.Rect(0, 0, arte.get_width(), max(120, min(h, int(h * 0.60))))
        src_meio_y = max(0, int(h * 0.12))
        src_meio = pygame.Rect(0, src_meio_y, arte.get_width(), max(110, min(h - src_meio_y, int(h * 0.56))))
        self._desenhar_faixa_loop(superficie, self._arte_externa_fundo or arte, self._desloc_arte_fundo, 176, src_fundo)
        self._desenhar_faixa_loop(superficie, self._arte_externa_meio or arte, self._desloc_arte, 232, src_meio)

    def _desenhar_nevoa_foco(self, superficie, cor_ceu):
        if self.cenario == "vulcao":
            alvo = (255, 190, 132)
        elif self.cenario == "cidade_futurista":
            alvo = (196, 214, 255)
        elif self.cenario == "deserto":
            alvo = (243, 217, 179)
        elif self.cenario == "floresta":
            alvo = (214, 228, 188)
        else:
            alvo = (236, 241, 248)
        for y, altura, peso in ((470, 14, 0.015), (528, 18, 0.028)):
            cor = misturar_cores(cor_ceu, alvo, peso)
            pygame.draw.rect(superficie, cor, (0, y, LARGURA_VIRTUAL, altura))

    def _obter_tile_montanhas(self, cor_ceu):
        # Quantizar ligeiramente a cor evita recriar o tile a cada mudanca minima
        # do ciclo dia/noite, poupando CPU em aparelhos mais antigos.
        ceu_q = tuple(max(0, min(255, (int(c) // 12) * 12)) for c in cor_ceu)
        cor_montanha = (max(24, ceu_q[0] // 2 - 10),
                        max(32, ceu_q[1] // 2), max(48, ceu_q[2] // 2 + 10))
        chave_cache = (self.cenario, cor_montanha)
        if self._cache_montanhas is not None and self._cache_montanhas_key == chave_cache:
            return self._cache_montanhas

        tile = pygame.Surface((LARGURA_VIRTUAL * 2, self.H_MONTANHAS)).convert()
        chave = self.CHAVE_TRANSPARENCIA
        tile.fill(chave)
        y_base_local = ALTURA_VIRTUAL - self.Y_MONTANHAS

        # V3.37: biomas com silhuetas próprias, pré-renderizadas no tile em cache.
        # Nenhum desenho extra é feito por frame durante o parallax.
        if self.cenario in ("vulcao", "floresta", "cidade_futurista"):
            for repeticao in range(2):
                xb = repeticao * LARGURA_VIRTUAL
                if self.cenario == "vulcao":
                    sombra_distante = misturar_cores(cor_montanha, (62, 53, 75), 0.70)
                    rocha = misturar_cores(cor_montanha, (87, 47, 66), 0.78)
                    face_rocha = misturar_cores(rocha, (43, 34, 57), 0.58)
                    lava = (255, 117, 50)
                    lava_clara = (255, 213, 95)
                    pygame.draw.polygon(tile, sombra_distante,
                        [(xb - 40, 320), (xb + 66, 155), (xb + 115, 230),
                         (xb + 205, 119), (xb + 291, 248), (xb + 385, 144), (xb + 490, 320)])
                    # Crateras com coroas recortadas e rios de lava.
                    for vx, topo, largura in ((102, 144, 170), (327, 121, 195)):
                        px = xb + vx
                        pygame.draw.polygon(tile, rocha,
                            [(px - largura // 2, 320), (px - 27, topo + 34),
                             (px - 19, topo + 16), (px - 8, topo + 20),
                             (px, topo + 12), (px + 9, topo + 21),
                             (px + 21, topo + 16), (px + 30, topo + 35),
                             (px + largura // 2, 320)])
                        pygame.draw.polygon(tile, face_rocha,
                            [(px + 5, topo + 20), (px + 30, topo + 35),
                             (px + largura // 2, 320), (px + 12, 320)])
                        pygame.draw.polygon(tile, (173, 64, 56),
                            [(px - 20, topo + 18), (px - 7, topo + 25),
                             (px + 8, topo + 25), (px + 21, topo + 18),
                             (px + 13, topo + 32), (px - 12, topo + 32)])
                        pygame.draw.line(tile, lava, (px - 9, topo + 29), (px + 1, topo + 72), 5)
                        pygame.draw.lines(tile, lava, False,
                            [(px + 1, topo + 72), (px - 11, topo + 115),
                             (px + 5, topo + 163), (px - 2, min(319, topo + 210))], 4)
                        pygame.draw.line(tile, lava_clara, (px, topo + 37), (px + 3, topo + 63), 2)
                        for sd, yy in ((-21, 54), (25, 86), (-39, 138)):
                            if topo + yy < 315:
                                pygame.draw.line(tile, (130, 79, 96),
                                    (px + sd, topo + yy), (px + sd + 13, topo + yy + 12), 2)
                        for sx, sy, rad in ((-16, -5, 9), (3, -17, 12), (15, -28, 9)):
                            pygame.draw.circle(tile, misturar_cores(cor_ceu, (173, 133, 151), 0.46),
                                (px + sx, topo + sy), rad)
                elif self.cenario == "floresta":
                    colina_longe = misturar_cores(cor_montanha, (68, 153, 126), 0.71)
                    colina_perto = misturar_cores(cor_montanha, (45, 122, 87), 0.75)
                    arvore_escura = misturar_cores(cor_montanha, (24, 83, 65), 0.78)
                    arvore_clara = misturar_cores(cor_montanha, (79, 180, 101), 0.76)
                    pygame.draw.polygon(tile, colina_longe,
                        [(xb - 25, 320), (xb + 48, 207), (xb + 105, 231),
                         (xb + 187, 166), (xb + 283, 260), (xb + 383, 180),
                         (xb + 485, 320)])
                    pygame.draw.polygon(tile, colina_perto,
                        [(xb - 25, 320), (xb + 65, 261), (xb + 140, 288),
                         (xb + 246, 215), (xb + 325, 282), (xb + 421, 249),
                         (xb + 485, 320)])
                    for tx, altura, raio in ((38, 126, 26), (132, 165, 35),
                                             (238, 150, 30), (356, 181, 39), (432, 133, 26)):
                        px, base = xb + tx, 310
                        pygame.draw.rect(tile, (53, 96, 72), (px - 4, base - altura // 2, 8, altura // 2 + 10))
                        pygame.draw.polygon(tile, arvore_escura,
                            [(px, base - altura), (px - raio, base - altura // 2),
                             (px - raio // 2, base - altura // 2 + 3),
                             (px - raio - 8, base - altura // 3),
                             (px + raio + 8, base - altura // 3),
                             (px + raio // 2, base - altura // 2 + 3),
                             (px + raio, base - altura // 2)])
                        pygame.draw.line(tile, arvore_clara,
                            (px, base - altura + 5), (px - raio // 2, base - altura // 2), 2)
                        pygame.draw.rect(tile, (148, 210, 137),
                            (px - raio // 2, base - altura // 2 + 11, 3, 3))
                    # Vagalumes pequenos, já rasterizados.
                    for tx, ty in ((81, 199), (183, 238), (300, 191), (399, 233)):
                        pygame.draw.rect(tile, (255, 235, 137), (xb + tx, ty, 2, 2))
                else:  # cidade_futurista
                    longo = misturar_cores(cor_montanha, (53, 75, 133), 0.77)
                    perto = misturar_cores(cor_montanha, (30, 45, 91), 0.78)
                    borda_neon = (75, 217, 238)
                    janela = (146, 138, 251)
                    pygame.draw.rect(tile, longo, (xb, 288, LARGURA_VIRTUAL, 32))
                    for px, alt, largura in ((19, 94, 45), (88, 148, 58),
                                              (181, 115, 48), (266, 180, 68),
                                              (374, 127, 58)):
                        rx = xb + px
                        ry = 317 - alt
                        pygame.draw.rect(tile, longo, (rx, ry, largura, alt + 4))
                        pygame.draw.rect(tile, perto, (rx + largura - 12, ry + 9, 12, alt - 5))
                        pygame.draw.line(tile, borda_neon, (rx + 3, ry + 5),
                                         (rx + largura - 9, ry + 5), 2)
                        if largura > 50:
                            pygame.draw.polygon(tile, perto,
                                [(rx + 13, ry), (rx + largura // 2, ry - 17),
                                 (rx + largura - 13, ry)])
                        for yy in range(ry + 21, 302, 20):
                            for xx in range(rx + 9, rx + largura - 9, 14):
                                if (xx + yy) % 4 != 0:
                                    pygame.draw.rect(tile, janela, (xx, yy, 5, 7))
                    pygame.draw.line(tile, (216, 126, 242),
                                     (xb + 10, 296), (xb + 444, 296), 2)
            desenhar_detalhes_bioma_cacheado(tile, self.cenario, 'montanhas')
            tile.set_colorkey(chave)
            self._cache_montanhas = tile
            self._cache_montanhas_key = chave_cache
            return tile

        if self.cenario == "deserto":
            # Mesas rochosas de arenito e dunas ocre: as bases encostam no solo.
            # As duas camadas são geradas no cache; custo mínimo durante a corrida.
            areia_longe = misturar_cores(cor_montanha, (190, 127, 76), 0.80)
            areia_perto = misturar_cores(cor_montanha, (218, 157, 89), 0.87)
            duna_sombra = misturar_cores(areia_perto, (145, 83, 55), 0.60)
            rocha = misturar_cores(cor_montanha, (165, 88, 69), 0.86)
            rocha_luz = misturar_cores(cor_montanha, (244, 167, 97), 0.87)
            rocha_escura = misturar_cores(rocha, (92, 55, 57), 0.55)
            base = self.H_MONTANHAS - 1
            for i in range(2):
                xb = i * LARGURA_VIRTUAL
                # Duna traseira e primeira linha de montanhas, em contato com o terreno.
                pygame.draw.polygon(tile, areia_longe,
                    [(xb, base), (xb, 161), (xb+67, 141), (xb+141, 166),
                     (xb+238, 126), (xb+344, 171), (xb+450, 146), (xb+450, base)])
                pygame.draw.polygon(tile, areia_perto,
                    [(xb, base), (xb, 220), (xb+66, 200), (xb+132, 226),
                     (xb+231, 181), (xb+310, 216), (xb+397, 195), (xb+450, 215), (xb+450, base)])
                # Falésias de arenito: platôs largos, base sempre no y do solo.
                for rx, largura, topo in ((41, 105, 68), (199, 114, 94), (358, 87, 78)):
                    x0 = xb + rx
                    y1 = base
                    silhueta = [(x0-14, y1), (x0-6, topo+28), (x0+8, topo+22),
                                 (x0+13, topo+7), (x0+largura-22, topo+7),
                                 (x0+largura-10, topo+26), (x0+largura+10, y1)]
                    pygame.draw.polygon(tile, rocha_escura, silhueta)
                    pygame.draw.polygon(tile, rocha,
                        [(x0-6,y1), (x0+10,topo+16), (x0+largura-18,topo+16),
                         (x0+largura-4,y1)])
                    pygame.draw.polygon(tile, rocha_luz,
                        [(x0-3,y1), (x0+10,topo+16), (x0+largura//2,topo+17),
                         (x0+largura//2-8,y1)])
                    pygame.draw.rect(tile, rocha_luz, (x0+4, topo+5, largura-15, 10))
                    pygame.draw.line(tile, rocha_escura, (x0+7,topo+15), (x0+largura-16,topo+15), 2)
                    for strata in (38, 60, 85, 113):
                        yy = topo + strata
                        if yy < base - 7:
                            pygame.draw.line(tile, rocha_escura,
                                (x0+10, yy), (x0+largura-24, yy+2), 2)
                            pygame.draw.line(tile, rocha_luz,
                                (x0+13, yy+5), (x0+largura//2-8, yy+5), 1)
                    for ox, oy in ((15,26),(34,48),(largura-36,35),(largura-24,72)):
                        if topo+oy < base - 6:
                            pygame.draw.rect(tile, rocha_escura, (x0+ox, topo+oy, 5, 3))
                # Areia em primeiro plano cobre a junção das bases sem apagar as texturas.
                pygame.draw.polygon(tile, areia_perto,
                    [(xb,base), (xb,base-15), (xb+73,base-9), (xb+162,base-19),
                     (xb+260,base-11), (xb+352,base-21), (xb+450,base-14), (xb+450,base)])
                for x,yy,ww in ((20,297,44),(150,307,53),(287,303,35),(376,311,48)):
                    pygame.draw.line(tile, duna_sombra, (xb+x,yy), (xb+x+ww,yy+1), 2)
            desenhar_detalhes_bioma_cacheado(tile, self.cenario, 'montanhas')
            tile.set_colorkey(chave)
            self._cache_montanhas = tile
            self._cache_montanhas_key = chave_cache
            return tile

        if self.cenario in ("reino_submerso", "ilhas_celestes"):
            for i in range(2):
                xb = i * LARGURA_VIRTUAL
                if self.cenario == "reino_submerso":
                    cor_ruina = (max(8, cor_montanha[0] - 5), max(45, cor_montanha[1] + 15), max(75, cor_montanha[2] + 35))
                    pygame.draw.polygon(tile, cor_ruina, [(xb + 20, y_base_local), (xb + 48, 175), (xb + 85, 175), (xb + 105, y_base_local)])
                    pygame.draw.rect(tile, cor_ruina, (xb + 50, 190, 38, y_base_local - 190))
                    pygame.draw.polygon(tile, (65, 190, 200), [(xb + 5, y_base_local), (xb + 32, 240), (xb + 58, y_base_local)])
                    pygame.draw.polygon(tile, (65, 190, 200), [(xb + 300, y_base_local), (xb + 338, 220), (xb + 372, y_base_local)])
                else:
                    ilha_cor = (max(50, cor_montanha[0] + 15), max(85, cor_montanha[1] + 20), max(120, cor_montanha[2] + 20))
                    pygame.draw.ellipse(tile, ilha_cor, (xb + 20, 205, 125, 36))
                    pygame.draw.polygon(tile, ilha_cor, [(xb + 48, 230), (xb + 70, 286), (xb + 92, 230)])
                    pygame.draw.ellipse(tile, cor_distante if 'cor_distante' in locals() else cor_montanha, (xb + 240, 155, 145, 34))
                    pygame.draw.polygon(tile, ilha_cor, [(xb + 278, 180), (xb + 310, 242), (xb + 338, 180)])
            desenhar_detalhes_bioma_cacheado(tile, self.cenario, 'montanhas')
            tile.set_colorkey(chave)
            self._cache_montanhas = tile
            self._cache_montanhas_key = chave_cache
            return tile

        # Cordilheira distante: cria profundidade sem sprites ou trabalho por frame.
        cor_distante = (max(18, cor_montanha[0] - 18),
                        max(24, cor_montanha[1] - 17), max(38, cor_montanha[2] - 10))
        for i in range(2):
            xb = i * LARGURA_VIRTUAL
            pygame.draw.polygon(tile, cor_distante,
                                [(xb - 35, y_base_local), (xb + 72, 105),
                                 (xb + 142, 235), (xb + 230, 130),
                                 (xb + 300, 250), (xb + 390, 150),
                                 (xb + 475, y_base_local)])

        # Montanhas principais com face sombreada, contorno e detalhes de neve.
        cor_face = (max(12, cor_montanha[0] - 22),
                    max(18, cor_montanha[1] - 20), max(30, cor_montanha[2] - 14))
        cor_crista = (min(255, cor_montanha[0] + 24),
                      min(255, cor_montanha[1] + 24), min(255, cor_montanha[2] + 20))
        for i in range(2):
            x_base = i * LARGURA_VIRTUAL
            for x_offset, w, h in ((-50, 200, 300), (100, 240, 240), (280, 220, 320)):
                x = x_base + x_offset
                top_y = ALTURA_VIRTUAL - h
                py = top_y - self.Y_MONTANHAS
                px = x + w // 2
                base_pts = [(x, y_base_local), (px, py), (x + w, y_base_local)]
                pygame.draw.polygon(tile, cor_montanha, base_pts)
                # Face direita mais escura para dar volume em estilo low-poly.
                pygame.draw.polygon(tile, cor_face,
                                    [(px, py), (x + w, y_base_local), (px + int(w * 0.12), y_base_local)])
                pygame.draw.line(tile, cor_crista, (x + 8, y_base_local - 1), (px, py + 3), 2)

                sn_h = max(18, int(h * 0.25))
                lx = px - int((w // 2) * (sn_h / h))
                rx = px + int((w // 2) * (sn_h / h))
                pts_neve = [(px, py), (lx, py + sn_h), (px - 10, py + sn_h + 10),
                            (px + 10, py + sn_h + 5), (rx, py + sn_h)]
                pygame.draw.polygon(tile, (226, 239, 248), pts_neve)
                pygame.draw.polygon(tile, (174, 202, 222),
                                    [(px, py + 1), (px + 10, py + sn_h + 5),
                                     (rx, py + sn_h), (px + 5, py + sn_h // 2)])
                # Pequenas fendas rochosas fixas, rasterizadas apenas quando o tile muda.
                pygame.draw.line(tile, cor_face, (px - 24, py + sn_h + 24),
                                 (px - 12, py + sn_h + 42), 2)
                pygame.draw.line(tile, cor_face, (px + 28, py + sn_h + 42),
                                 (px + 18, py + sn_h + 58), 2)

        desenhar_detalhes_bioma_cacheado(tile, self.cenario, 'montanhas')
        tile.set_colorkey(chave)
        self._cache_montanhas = tile
        self._cache_montanhas_key = chave_cache
        return tile

    def _obter_tile_predios(self, cor_ceu, e_noite):
        ceu_q = tuple(max(0, min(255, (int(c) // 12) * 12)) for c in cor_ceu)
        cor_perto = (max(14, ceu_q[0] // 3), max(18, ceu_q[1] // 3), max(26, ceu_q[2] // 3))
        luz_cor = (255, 218, 112) if e_noite else (176, 218, 246)
        chave_cache = (self.cenario, cor_perto, luz_cor, bool(e_noite))
        if self._cache_predios is not None and self._cache_predios_key == chave_cache:
            return self._cache_predios

        tile = pygame.Surface((LARGURA_VIRTUAL * 2, self.H_PREDIOS)).convert()
        chave = self.CHAVE_TRANSPARENCIA
        tile.fill(chave)
        cor_lateral = (max(8, cor_perto[0] - 16), max(10, cor_perto[1] - 17), max(16, cor_perto[2] - 15))
        cor_borda = (min(255, cor_perto[0] + 25), min(255, cor_perto[1] + 24), min(255, cor_perto[2] + 26))
        cor_telhado = (max(12, cor_perto[0] - 6), max(16, cor_perto[1] - 6), max(22, cor_perto[2] - 4))

        # V3.37: primeiro plano único por bioma, em tile cacheado e repetível.
        if self.cenario in ("vulcao", "floresta", "cidade_futurista"):
            for repeticao in range(2):
                xb = repeticao * LARGURA_VIRTUAL
                if self.cenario == "vulcao":
                    rocha = misturar_cores(cor_perto, (81, 53, 66), 0.68)
                    sombra = misturar_cores(rocha, (29, 28, 44), 0.58)
                    vermelho = (255, 96, 55) if not e_noite else (255, 133, 61)
                    for rx, alto, largura in ((-17, 133, 91), (111, 93, 70),
                                               (215, 163, 104), (371, 117, 94)):
                        px = xb + rx
                        pygame.draw.polygon(tile, rocha,
                            [(px - 12, 250), (px, 250 - alto + 25),
                             (px + largura // 3, 250 - alto),
                             (px + largura // 2, 250 - alto + 21),
                             (px + largura, 250 - alto + 7),
                             (px + largura + 14, 250)])
                        pygame.draw.polygon(tile, sombra,
                            [(px + largura // 2, 250 - alto + 21),
                             (px + largura, 250 - alto + 7),
                             (px + largura + 14, 250),
                             (px + largura // 2, 250)])
                        pygame.draw.line(tile, vermelho,
                            (px + largura // 3, 250 - alto + 32),
                            (px + largura // 3 + 11, 250 - alto + 62), 3)
                        for off in (21, 53, 76):
                            yy = 250 - alto + off
                            if 8 <= yy < 246:
                                pygame.draw.rect(tile, (146, 92, 87),
                                                 (px + 12 + off // 4, yy, 9, 2))
                    for x in (27, 174, 347):
                        pygame.draw.rect(tile, (255, 201, 96),
                                         (xb + x, 240, 10, 3))
                        pygame.draw.rect(tile, vermelho, (xb + x - 5, 245, 21, 4))
                elif self.cenario == "floresta":
                    madeira = (62, 96, 68)
                    casca = (45, 69, 57)
                    copa = misturar_cores(cor_perto, (54, 136, 84), 0.77)
                    copa_clara = misturar_cores(copa, (106, 205, 108), 0.43)
                    for px, topo, raio in ((46, 91, 42), (170, 132, 48),
                                            (296, 96, 47), (427, 151, 42)):
                        x = xb + px
                        pygame.draw.rect(tile, madeira, (x - 8, topo + 37, 16, 213 - topo))
                        pygame.draw.rect(tile, casca, (x + 2, topo + 41, 5, 205 - topo))
                        pygame.draw.line(tile, copa, (x, topo + 75), (x - 24, topo + 57), 6)
                        pygame.draw.line(tile, copa, (x, topo + 83), (x + 26, topo + 55), 6)
                        pygame.draw.circle(tile, copa, (x, topo + raio // 2), raio)
                        pygame.draw.circle(tile, copa_clara, (x - 15, topo + 8), max(9, raio - 14))
                        pygame.draw.circle(tile, copa, (x + 19, topo + 13), raio // 2)
                        for off, sy in ((-22, 19), (-7, 0), (16, 29)):
                            pygame.draw.rect(tile, (170, 226, 138),
                                             (x + off, topo + sy, 3, 3))
                    for x in (88, 249, 378):
                        pygame.draw.rect(tile, (220, 132, 93),
                                         (xb + x, 232, 8, 10))
                        pygame.draw.ellipse(tile, (244, 92, 117),
                                            (xb + x - 6, 225, 20, 12))
                        pygame.draw.rect(tile, (255, 237, 184),
                                         (xb + x, 229, 2, 2))
                else:  # cidade_futurista
                    predio = misturar_cores(cor_perto, (29, 41, 83), 0.75)
                    lateral = misturar_cores(predio, (12, 25, 53), 0.65)
                    brilho = (80, 232, 255) if e_noite else (104, 215, 241)
                    roxo = (225, 100, 255) if e_noite else (162, 128, 240)
                    for px, topo, largura in ((5, 68, 94), (121, 96, 75),
                                              (229, 32, 104), (356, 81, 101)):
                        x = xb + px
                        pygame.draw.rect(tile, (13, 23, 48),
                                         (x + 5, topo + 6, largura, 244 - topo))
                        pygame.draw.rect(tile, predio, (x, topo, largura, 250 - topo))
                        pygame.draw.rect(tile, lateral, (x + largura - 12, topo + 4,
                                                        12, 246 - topo))
                        pygame.draw.rect(tile, brilho, (x, topo, largura, 3))
                        pygame.draw.rect(tile, roxo,
                                         (x + 5, topo + 12, largura - 18, 2))
                        for yy in range(topo + 29, 240, 22):
                            for xx in range(x + 12, x + largura - 15, 18):
                                if (xx // 6 + yy // 5) % 3 != 0:
                                    pygame.draw.rect(tile, brilho, (xx, yy, 7, 9))
                                    pygame.draw.rect(tile, (211, 248, 255),
                                                     (xx + 1, yy + 1, 2, 3))
                        pygame.draw.rect(tile, roxo,
                                         (x + largura // 2 - 8, 232, 16, 18))
                    for x in (91, 211, 347):
                        pygame.draw.line(tile, brilho,
                            (xb + x, 116), (xb + x + 20, 116), 2)
                        pygame.draw.rect(tile, roxo,
                            (xb + x + 10, 108, 4, 8))
            desenhar_detalhes_bioma_cacheado(tile, self.cenario, 'predios')
            tile.set_colorkey(chave)
            self._cache_predios = tile
            self._cache_predios_key = chave_cache
            return tile

        if self.cenario == "deserto":
            # Rochas avermelhadas com face, estratos e base ancorada no chão.
            # NENHUM elemento flutua: todos terminam no fundo da camada próxima.
            terra = misturar_cores(cor_ceu, (185, 116, 69), 0.84)
            sombra = misturar_cores(terra, (107, 65, 53), 0.68)
            luz = misturar_cores(terra, (246, 177, 101), 0.68)
            face = misturar_cores(terra, (220, 135, 81), 0.58)
            base = self.H_PREDIOS - 1
            for i in range(2):
                xb = i * LARGURA_VIRTUAL
                pygame.draw.rect(tile, misturar_cores(terra, (230, 181, 108), 0.5),
                                 (xb, base - 14, LARGURA_VIRTUAL, 15))
                mesas = ((9, 72, 114), (136, 112, 74), (231, 65, 121), (373, 100, 82))
                for rx, topo, rw in mesas:
                    xx = xb + rx
                    pygame.draw.polygon(tile, sombra,
                        [(xx-8,base), (xx,topo+30), (xx+13,topo+10),
                         (xx+rw-9,topo+10), (xx+rw+9,base)])
                    pygame.draw.polygon(tile, terra,
                        [(xx,base), (xx+10,topo+19), (xx+rw-17,topo+19), (xx+rw,base)])
                    pygame.draw.polygon(tile, face,
                        [(xx+12,topo+18), (xx+rw//2,topo+19), (xx+rw//2-7,base),
                         (xx,base)])
                    pygame.draw.rect(tile, luz, (xx+7,topo+8,rw-18,11))
                    pygame.draw.line(tile, (255,215,142), (xx+10,topo+8), (xx+rw-17,topo+8), 2)
                    for estrato in (33, 53, 78, 112, 146):
                        y = topo + estrato
                        if y < base-8:
                            pygame.draw.line(tile, sombra, (xx+13,y), (xx+rw-15,y+2), 2)
                            pygame.draw.line(tile, luz, (xx+18,y+5), (xx+rw//2,y+5), 1)
                    for a,b in ((15,23),(rw-27,45),(rw//2,65)):
                        if topo+b < base-12:
                            pygame.draw.rect(tile, sombra,(xx+a,topo+b,5,3))
                # Pequenos cactos ancorados à mesma linha de chão.
                for cx, h in ((80,28),(191,23),(321,31),(428,22)):
                    px = xb+cx
                    pygame.draw.rect(tile,(48,126,68),(px-4,base-h,8,h))
                    pygame.draw.rect(tile,(115,185,95),(px-3,base-h+3,2,h-6))
                    pygame.draw.rect(tile,(48,126,68),(px-11,base-h+10,7,5))
                    pygame.draw.rect(tile,(48,126,68),(px-11,base-h+4,4,10))
                    pygame.draw.rect(tile,(48,126,68),(px+4,base-h+14,7,5))
                    pygame.draw.rect(tile,(48,126,68),(px+7,base-h+9,4,10))
                for dx in (22,125,219,350,414):
                    pygame.draw.line(tile,sombra,(xb+dx,base-4),(xb+dx+15,base-3),1)
            desenhar_detalhes_bioma_cacheado(tile, self.cenario, 'predios')
            tile.set_colorkey(chave)
            self._cache_predios = tile
            self._cache_predios_key = chave_cache
            return tile

        if self.cenario in ("reino_submerso", "ilhas_celestes"):
            tile.fill(chave)
            rng = random.Random(6412 if self.cenario == "reino_submerso" else 7126)
            for i in range(2):
                xb = i * LARGURA_VIRTUAL
                if self.cenario == "reino_submerso":
                    for cx, basey, altura in ((35, 265, 58), (92, 280, 42), (205, 255, 75), (340, 272, 55), (430, 260, 65)):
                        cx += xb
                        pygame.draw.rect(tile, (15, 80, 112), (cx - 8, basey - altura, 16, altura))
                        pygame.draw.rect(tile, (45, 145, 160), (cx - 11, basey - altura, 22, 6))
                        pygame.draw.rect(tile, (30, 110, 140), (cx - 4, basey - altura + 12, 3, 10))
                        pygame.draw.rect(tile, (30, 110, 140), (cx + 3, basey - altura + 12, 3, 10))
                    for cx, basey in ((130, 285), (390, 290)):
                        pygame.draw.line(tile, (35, 170, 155), (cx + xb, basey), (cx + xb - 8, basey - 32), 4)
                        pygame.draw.line(tile, (35, 170, 155), (cx + xb, basey), (cx + xb + 10, basey - 26), 4)
                    for sx, sy in ((58, 210), (250, 198), (418, 214)):
                        pygame.draw.circle(tile, (118, 229, 226), (xb + sx, sy), 3)
                        pygame.draw.circle(tile, (194, 248, 245), (xb + sx, sy), 1)
                else:
                    for cx, yy, largura in ((45, 255, 88), (190, 218, 110), (355, 270, 94)):
                        cx += xb
                        pygame.draw.ellipse(tile, (120, 185, 220), (cx, yy, largura, 22))
                        pygame.draw.polygon(tile, (75, 140, 190), [(cx + 18, yy + 18), (cx + largura // 2, yy + 58), (cx + largura - 12, yy + 18)])
                    # Pequeno dirigível estático em silhueta, parte do tile cacheado.
                    pygame.draw.ellipse(tile, (85, 115, 165), (xb + 240, 145, 64, 20))
                    pygame.draw.line(tile, (85, 115, 165), (xb + 272, 165), (xb + 272, 176), 2)
                    pygame.draw.ellipse(tile, (255, 255, 255), (xb + 58, 170, 44, 12))
                    pygame.draw.ellipse(tile, (236, 245, 255), (xb + 72, 160, 52, 14))
            desenhar_detalhes_bioma_cacheado(tile, self.cenario, 'predios')
            tile.set_colorkey(chave)
            self._cache_predios = tile
            self._cache_predios_key = chave_cache
            return tile

        if self.cenario == "neve":
            cor_perto = (42, 61, 86) if e_noite else (83, 105, 128)
            cor_lateral = (31, 46, 67)
            cor_borda = (135, 165, 190)
            cor_telhado = (202, 226, 241)
            luz_cor = (255, 226, 144) if e_noite else (196, 224, 244)

        for i in range(2):
            x_base = i * LARGURA_VIRTUAL
            for predio_idx, (bx, by, bw, bh) in enumerate(self.predios):
                real_x = x_base + bx
                y_local = by - self.Y_PREDIOS
                # Sombra, fachada, lateral e telhado em degraus.
                pygame.draw.rect(tile, (12, 15, 23), (real_x + 4, y_local + 4, bw, bh))
                pygame.draw.rect(tile, cor_perto, (real_x, y_local, bw, bh))
                pygame.draw.rect(tile, cor_lateral, (real_x + bw - 5, y_local + 2, 5, bh - 2))
                pygame.draw.rect(tile, cor_borda, (real_x, y_local, 3, bh))
                pygame.draw.rect(tile, cor_telhado, (real_x - 3, y_local, bw + 6, 7))
                pygame.draw.line(tile, cor_borda, (real_x + 4, y_local + 9),
                                (real_x + bw - 7, y_local + 9), 1)

                # Faixas de concreto e juntas verticais da fachada.
                for yy in range(y_local + 22, y_local + bh - 5, 42):
                    pygame.draw.line(tile, cor_lateral, (real_x + 4, yy), (real_x + bw - 6, yy), 1)
                if bw >= 55:
                    pygame.draw.line(tile, cor_lateral, (real_x + bw // 2, y_local + 12),
                                    (real_x + bw // 2, y_local + bh - 5), 1)

                for wx_local, wy in self.janelas_por_predio[(bx, by, bw, bh)]:
                    # A janela permanece dentro do predio; o cache original incluia
                    # algumas posicoes abaixo do pe-direito em edificios baixos.
                    if wy < by + bh - 9:
                        wx = real_x + wx_local
                        wy_local = wy - self.Y_PREDIOS
                        pygame.draw.rect(tile, cor_lateral, (wx - 1, wy_local - 1, 10, 14))
                        pygame.draw.rect(tile, luz_cor, (wx, wy_local, 7, 10))
                        pygame.draw.line(tile, cor_perto, (wx + 3, wy_local), (wx + 3, wy_local + 9), 1)
                        pygame.draw.line(tile, cor_perto, (wx, wy_local + 5), (wx + 6, wy_local + 5), 1)

                # Detalhes de telhado variam por predio, sem animacao/custo por frame.
                if predio_idx in (0, 2):
                    pygame.draw.rect(tile, cor_lateral, (real_x + 8, y_local - 8, 12, 8))
                    pygame.draw.line(tile, cor_borda, (real_x + 14, y_local - 18),
                                     (real_x + 14, y_local - 8), 2)
                if predio_idx == 2:
                    pygame.draw.rect(tile, cor_lateral, (real_x + bw - 21, y_local - 13, 10, 13))
                # Base e pequena entrada/porta.
                pygame.draw.rect(tile, cor_lateral, (real_x + bw // 2 - 5, y_local + bh - 18, 10, 18))
                pygame.draw.rect(tile, cor_borda, (real_x + bw // 2 - 4, y_local + bh - 17, 2, 16))
                # Toldos, plantas e letreiros mantêm a cidade acolhedora.
                if self.cenario == "cidade":
                    if predio_idx in (0, 2):
                        pygame.draw.rect(tile, (231, 110, 116),
                            (real_x + 6, y_local + bh - 34, min(25, bw - 10), 5))
                        pygame.draw.rect(tile, (253, 197, 119),
                            (real_x + 9, y_local + bh - 32, min(18, bw - 15), 2))
                    else:
                        pygame.draw.rect(tile, (98, 181, 117),
                            (real_x + 7, y_local + 10, 12, 5))
                        pygame.draw.rect(tile, (182, 229, 157),
                            (real_x + 10, y_local + 7, 6, 3))
                if self.cenario == "neve":
                    # Beiral de neve sobre cada telhado e pequenas acumulações.
                    pygame.draw.rect(tile, (218, 237, 248), (real_x - 4, y_local - 2, bw + 8, 5))
                    pygame.draw.rect(tile, (174, 204, 224), (real_x + bw - 10, y_local + 2, 10, 4))

            if self.cenario == "neve":
                # Pinheiros estilizados, 2D e baratos, na linha do horizonte.
                for tx, base_y, h in ((62, 178, 55), (172, 180, 43), (282, 177, 62), (422, 179, 48)):
                    tx += x_base
                    topo = base_y - h
                    pygame.draw.rect(tile, (82, 64, 48), (tx - 2, base_y - 10, 4, 12))
                    for nivel in range(3):
                        yy = topo + nivel * 15
                        largura = 16 - nivel * 3
                        pygame.draw.polygon(tile, (30, 91, 77),
                                            [(tx, yy), (tx - largura, yy + 22), (tx + largura, yy + 22)])
                        pygame.draw.line(tile, (211, 235, 246), (tx, yy + 1), (tx - largura + 4, yy + 18), 2)

        desenhar_detalhes_bioma_cacheado(tile, self.cenario, 'predios')
        tile.set_colorkey(chave)
        self._cache_predios = tile
        self._cache_predios_key = chave_cache
        return tile

    def _cor_ceu_na_altura(self, cor_ceu, y):
        """Retorna a cor aproximada do gradiente de fundo na altura do astro."""
        faixa = max(0, min(7, int(y) // (ALTURA_VIRTUAL // 8)))
        fator = 0.78 + faixa * 0.035
        return tuple(max(0, min(255, int(c * fator))) for c in cor_ceu)

    def _desenhar_sol(self, superficie, x, y, cor_ceu):
        """Sol pixel-art com brilho em camadas; sem alpha blending nem assets."""
        centro = (int(x), int(y))
        cor_glow = misturar_cores(cor_ceu, (255, 135, 48), 0.24)
        cor_glow_interno = misturar_cores(cor_ceu, (255, 171, 61), 0.46)
        pygame.draw.circle(superficie, cor_glow, centro, 39)
        pygame.draw.circle(superficie, cor_glow_interno, centro, 29)
        pygame.draw.circle(superficie, (255, 183, 63), centro, 20)

        # Raios curtos com variacao sutil, como pixels pulsantes.
        pulso = (self.tempo_animacao // 7) % 2
        for angulo in range(0, 360, 45):
            rad = math.radians(angulo)
            raio_in = 23
            raio_out = 30 + pulso
            p1 = (int(x + math.cos(rad) * raio_in), int(y + math.sin(rad) * raio_in))
            p2 = (int(x + math.cos(rad) * raio_out), int(y + math.sin(rad) * raio_out))
            pygame.draw.line(superficie, (255, 218, 112), p1, p2, 2)

        pygame.draw.circle(superficie, (255, 221, 103), centro, 15)
        pygame.draw.circle(superficie, (255, 243, 184), (int(x - 4), int(y - 4)), 8)
        pygame.draw.rect(superficie, (255, 255, 224), (int(x - 7), int(y - 6), 5, 2))
        pygame.draw.rect(superficie, (255, 249, 210), (int(x + 1), int(y + 2), 4, 2))

    def _desenhar_lua(self, superficie, x, y, cor_ceu, intensidade):
        """Lua crescente luminosa em pixel art, com halo e crateras discretas."""
        if intensidade <= 0.03:
            return
        centro = (int(x), int(y))
        halo_ext = misturar_cores(cor_ceu, (146, 184, 255), 0.18 * intensidade)
        halo_int = misturar_cores(cor_ceu, (184, 209, 255), 0.35 * intensidade)
        pygame.draw.circle(superficie, halo_ext, centro, 34)
        pygame.draw.circle(superficie, halo_int, centro, 25)
        pygame.draw.circle(superficie, (224, 237, 255), centro, 17)
        # O recorte escuro produz uma crescente sem texturas nem mascaras caras.
        pygame.draw.circle(superficie, cor_ceu, (int(x + 7), int(y - 4)), 15)
        cor_cratera = misturar_cores(cor_ceu, (161, 188, 225), 0.48 * intensidade)
        pygame.draw.rect(superficie, cor_cratera, (int(x - 8), int(y - 2), 3, 3))
        pygame.draw.rect(superficie, cor_cratera, (int(x - 3), int(y + 5), 2, 2))
        # Brilho em cruz aparece e desaparece discretamente, nao fica congelado.
        if (self.tempo_animacao // 9) % 3 != 0:
            cor_brilho = misturar_cores(cor_ceu, (255, 255, 255), 0.78 * intensidade)
            pygame.draw.rect(superficie, cor_brilho, (int(x + 17), int(y - 17), 2, 6))
            pygame.draw.rect(superficie, cor_brilho, (int(x + 15), int(y - 15), 6, 2))


    def _bioma_spriteado_ativo(self):
        return self._usa_bioma_vivo and self.cenario in (
            "cidade", "neve", "deserto", "vulcao", "floresta", "cidade_futurista", "ilhas_celestes"
        )

    def _desenhar_halo_luz(self, superficie, x, y, cor, raio=8, intensidade=1.0):
        if intensidade <= 0.02:
            return
        misto = misturar_cores((255, 255, 255), cor, 0.55)
        pygame.draw.circle(superficie, misturar_cores(cor, (255, 255, 255), 0.15), (int(x), int(y)), max(2, int(raio * 1.55)), 1)
        pygame.draw.circle(superficie, misto, (int(x), int(y)), max(1, int(raio * 0.55)))

    def _iterar_segmentos_sprite(self, velocidade, largura_segmento, sobra=2):
        mundo = self._mundo_cenario * velocidade
        primeiro = int(math.floor(mundo / largura_segmento)) - 1
        resto = mundo - math.floor(mundo / largura_segmento) * largura_segmento
        total = int(math.ceil(LARGURA_VIRTUAL / largura_segmento)) + sobra
        for ordem in range(total):
            indice = primeiro + ordem
            x = int(ordem * largura_segmento - resto)
            yield indice, x

    def _rng_segmento(self, camada, indice):
        chave = f"{self.cenario}:{camada}:{indice}"
        seed = 0
        for i, ch in enumerate(chave):
            seed = (seed + (i + 1) * ord(ch) * 97) & 0xffffffff
        return random.Random(seed)

    def _desenhar_cenario_spriteado(self, superficie, cor_ceu, e_noite):
        """Renderização profissional por sprites/props proceduralmente gerados.
        Não usa PNG nos biomas principais. Cada camada é desenhada como um
        conjunto de sprites pequenos/segmentos, com velocidades diferentes,
        animações leves e reação a clima e ciclo dia/noite.
        """
        noite = max(0.0, min(1.0, self.peso_noite))
        clima = getattr(self, "clima_tipo", "limpo")
        t_anim = self.tempo_animacao * 0.08
        vento = 1.0 if clima in ("vento", "vento_folhas", "tempestade_vento", "brisa_celeste", "areia", "tempestade_areia", "nevasca") else 0.0
        chuvoso = clima in ("chuva", "tempestade", "chuva_acida")
        poeira = clima in ("areia", "tempestade_areia")
        quente = self.cenario in ("deserto", "vulcao")

        # Camada 1: silhueta distante.
        for seg, base_x in self._iterar_segmentos_sprite(0.10, 150):
            rng = self._rng_segmento("dist", seg)
            if self.cenario in ("cidade", "neve"):
                x = base_x
                while x < base_x + 150:
                    larg = rng.randint(22, 40)
                    alt = rng.randint(60, 155)
                    topo = 540 - alt
                    corpo = (86, 107, 132) if self.cenario == "cidade" else (96, 116, 148)
                    corpo = misturar_cores(corpo, (40, 45, 70), noite * 0.45)
                    pygame.draw.rect(superficie, corpo, (x, topo, larg, alt))
                    pygame.draw.rect(superficie, misturar_cores(corpo, (180, 210, 230), 0.12), (x, topo, larg, 3))
                    if self.cenario == "neve":
                        pygame.draw.rect(superficie, (226, 236, 246), (x - 1, topo - 2, larg + 2, 4))
                    x += larg + rng.randint(4, 10)
            elif self.cenario == "deserto":
                for i in range(2):
                    cx = base_x + i * 72 + rng.randint(-8, 8)
                    alt = rng.randint(70, 130)
                    pts = [(cx - 42, 540), (cx - 18, 540 - alt // 2), (cx + 4, 540 - alt), (cx + 48, 540)]
                    pygame.draw.polygon(superficie, (145, 110, 79), pts)
                    pygame.draw.polygon(superficie, (188, 144, 96), [(cx + 4, 540 - alt), (cx + 48, 540), (cx + 12, 540)])
            elif self.cenario == "vulcao":
                cx = base_x + 75
                alt = rng.randint(90, 160)
                pygame.draw.polygon(superficie, (69, 45, 58), [(cx - 70, 545), (cx, 545 - alt), (cx + 70, 545)])
                pygame.draw.line(superficie, (190, 81, 55), (cx - 4, 545 - alt + 18), (cx + 4, 545 - alt + 54), 2)
                for puff in range(3):
                    px = cx + int(math.sin(t_anim * 0.55 + puff + seg) * (4 + puff * 2))
                    py = 545 - alt - puff * 11 - int((self.tempo_animacao * 0.20 + puff * 4) % 10)
                    pygame.draw.circle(superficie, (96, 88, 98), (px, py), 5 + puff * 2)
            elif self.cenario == "floresta":
                for i in range(2):
                    cx = base_x + i * 78 + rng.randint(-5, 7)
                    sway = int(math.sin(t_anim * (0.9 + vento * 0.4) + cx * 0.03) * (2 + vento * 2))
                    pygame.draw.line(superficie, (42, 83, 63), (cx, 545), (cx + sway, 490), 4)
                    pygame.draw.ellipse(superficie, (57, 133, 88), (cx - 24 + sway, 458, 48, 28))
            elif self.cenario == "cidade_futurista":
                for i in range(3):
                    x = base_x + i * 46 + rng.randint(-3, 4)
                    alt = rng.randint(80, 165)
                    w = rng.randint(18, 30)
                    corpo = misturar_cores((36, 51, 94), (25, 31, 67), 0.25)
                    pygame.draw.rect(superficie, corpo, (x, 548 - alt, w, alt))
                    neon = (86, 236, 245) if i % 2 == 0 else (220, 126, 255)
                    pygame.draw.rect(superficie, neon, (x, 548 - alt, w, 2))
            elif self.cenario == "ilhas_celestes":
                for i in range(2):
                    x = base_x + i * 68 + rng.randint(-8, 8)
                    y = 485 + (i % 2) * 20 + int(math.sin(t_anim * 0.9 + seg + i) * 3)
                    pygame.draw.ellipse(superficie, (141, 190, 221), (x, y, 62, 14))
                    pygame.draw.polygon(superficie, (88, 145, 193), [(x + 10, y + 12), (x + 32, y + 38), (x + 53, y + 12)])
                    pygame.draw.line(superficie, (214, 250, 255), (x + 31, y + 14), (x + 31, y + 46), 1)

        # Camada 2: objetos médios vivos + props animados.
        for seg, base_x in self._iterar_segmentos_sprite(0.22, 120):
            rng = self._rng_segmento("meio", seg)
            if self.cenario in ("cidade", "neve"):
                for i in range(2):
                    x = base_x + i * 54 + rng.randint(-4, 4)
                    w = rng.randint(28, 42)
                    h = rng.randint(70, 125)
                    y = 612 - h
                    corpo = (64, 76, 95) if self.cenario == "cidade" else (82, 96, 126)
                    pygame.draw.rect(superficie, corpo, (x, y, w, h))
                    pygame.draw.rect(superficie, (116, 140, 168), (x, y, w, 3))
                    if self.cenario == "neve":
                        pygame.draw.rect(superficie, (238, 244, 252), (x - 1, y - 2, w + 2, 4))
                    for wy in range(y + 10, y + h - 12, 16):
                        for wx in range(x + 6, x + w - 8, 12):
                            acesa = ((wx + wy + seg) % 3) != 0
                            cor_j = (255, 220, 132) if noite > 0.08 and acesa else (120, 158, 193)
                            cor_j = (cor_j if noite > 0.08 else misturar_cores(cor_j, (203, 224, 241), 0.35))
                            pygame.draw.rect(superficie, cor_j, (wx, wy, 6, 8))
                    if noite > 0.08:
                        self._desenhar_halo_luz(superficie, x + w // 2, y + 10, (255, 221, 150), 5, noite)
                # postes e pedestres
                for i in range(2):
                    px = base_x + 26 + i * 48
                    pygame.draw.rect(superficie, (66, 74, 86), (px, 615, 3, 32))
                    if noite > 0.08:
                        self._desenhar_halo_luz(superficie, px + 1, 614, (255, 225, 168), 7, noite)
                    elif self.cenario == "cidade":
                        pygame.draw.circle(superficie, (216, 229, 241), (px + 1, 614), 3)
                if rng.random() < 0.6:
                    ped_x = base_x + 12 + (self.tempo_animacao // 3 + seg * 5) % 86
                    ped_y = 642
                    pygame.draw.rect(superficie, (52, 61, 75), (ped_x, ped_y, 3, 9))
                    pygame.draw.rect(superficie, (227, 197, 156), (ped_x, ped_y - 3, 3, 3))
                    pygame.draw.line(superficie, (52, 61, 75), (ped_x, ped_y + 8), (ped_x - 1, ped_y + 12 + ((self.tempo_animacao // 5) % 2)), 1)
                    pygame.draw.line(superficie, (52, 61, 75), (ped_x + 2, ped_y + 8), (ped_x + 3, ped_y + 12 + (((self.tempo_animacao // 5) + 1) % 2)), 1)
                # carros de fundo
                car_x = base_x + int((self.tempo_animacao * 0.9 + seg * 27) % 130) - 16
                car_y = 650 if self.cenario == "cidade" else 654
                car_cor = (194, 82, 94) if (seg % 2 == 0) else (94, 159, 204)
                pygame.draw.rect(superficie, car_cor, (car_x, car_y, 16, 6), border_radius=2)
                pygame.draw.rect(superficie, (232, 240, 247), (car_x + 2, car_y + 1, 4, 2))
            elif self.cenario == "deserto":
                x = base_x + 16
                for i in range(2):
                    px = x + i * 50 + rng.randint(-3, 3)
                    sway = int(math.sin(t_anim * (1.0 + vento * 0.5) + px * 0.05) * (2 + vento * 3))
                    pygame.draw.line(superficie, (90, 74, 46), (px, 640), (px + sway, 613), 3)
                    for dx in (-9, -4, 3, 8):
                        pygame.draw.line(superficie, (76, 126, 62), (px + sway, 616), (px + sway + dx, 605 + abs(dx) // 3), 2)
                if poeira:
                    for i in range(3):
                        sx = base_x + i * 34
                        sy = 590 + (i % 2) * 18
                        pygame.draw.line(superficie, (226, 185, 120), (sx, sy), (sx + 16, sy), 1)
            elif self.cenario == "vulcao":
                for i in range(2):
                    px = base_x + i * 58 + rng.randint(-3, 3)
                    pygame.draw.polygon(superficie, (82, 55, 61), [(px - 18, 646), (px, 594), (px + 20, 646)])
                    brilho = 0.45 + 0.45 * (0.5 + 0.5 * math.sin(t_anim * 1.5 + px * 0.03))
                    cor = misturar_cores((196, 82, 49), (255, 205, 118), brilho + noite * 0.1)
                    pygame.draw.rect(superficie, cor, (px - 2, 603, 5, 32))
                    pygame.draw.rect(superficie, (255, 238, 175), (px - 1, 612, 2, 10))
            elif self.cenario == "floresta":
                for i in range(2):
                    px = base_x + i * 55 + rng.randint(-4, 4)
                    sway = int(math.sin(t_anim * (1.15 + vento * 0.55) + px * 0.04) * (4 + vento * 5))
                    pygame.draw.line(superficie, (60, 96, 62), (px, 646), (px + sway, 595), 4)
                    pygame.draw.ellipse(superficie, (70, 162, 95), (px - 18 + sway, 565, 36, 20))
                    pygame.draw.ellipse(superficie, (153, 218, 124), (px - 6 + sway, 569, 13, 6))
                water_x = base_x + 86
                for j in range(6):
                    y0 = 556 + j * 14
                    wave = int(math.sin(t_anim * 1.8 + j + seg) * 2)
                    pygame.draw.line(superficie, (124, 212, 228), (water_x + wave, y0), (water_x + 4 + wave, y0 + 11), 2)
                    pygame.draw.line(superficie, (236, 250, 255), (water_x + 1 + wave, y0 + 3), (water_x + 1 + wave, y0 + 8), 1)
                if noite > 0.08:
                    for orb in range(2):
                        ox = base_x + 20 + orb * 38
                        oy = 592 + orb * 18
                        brilho = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t_anim * 1.5 + orb + seg))
                        self._desenhar_halo_luz(superficie, ox, oy, misturar_cores((146, 184, 84), (255, 255, 178), brilho), 4, noite)
            elif self.cenario == "cidade_futurista":
                for i in range(2):
                    px = base_x + i * 52 + rng.randint(-2, 4)
                    h = rng.randint(82, 132)
                    w = rng.randint(20, 30)
                    y = 640 - h
                    corpo = (22, 34, 66)
                    pygame.draw.rect(superficie, corpo, (px, y, w, h))
                    neon = (86, 232, 248) if i % 2 == 0 else (224, 124, 255)
                    pygame.draw.rect(superficie, neon, (px, y, w, 2))
                    for yy in range(y + 10, y + h - 8, 16):
                        pygame.draw.rect(superficie, neon, (px + 4, yy, w - 10, 2))
                        if noite > 0.04:
                            self._desenhar_halo_luz(superficie, px + w // 2, yy + 1, neon, 4, 0.55 + noite * 0.35)
                hover_x = base_x + int((self.tempo_animacao * 1.4 + seg * 17) % 130) - 20
                hover_y = 595 + int(math.sin(t_anim * 2.0 + seg) * 4)
                pygame.draw.rect(superficie, (84, 232, 244), (hover_x, hover_y, 18, 5), border_radius=2)
                pygame.draw.rect(superficie, (239, 132, 255), (hover_x - 8, hover_y + 2, 7, 2), border_radius=1)
                pygame.draw.rect(superficie, (240, 248, 255), (hover_x + 4, hover_y + 1, 4, 2))
            elif self.cenario == "ilhas_celestes":
                for i in range(2):
                    px = base_x + i * 58 + rng.randint(-3, 3)
                    py = 612 + (i % 2) * 15 + int(math.sin(t_anim + seg + i) * 4)
                    pygame.draw.ellipse(superficie, (119, 184, 214), (px, py, 70, 16))
                    pygame.draw.polygon(superficie, (80, 136, 188), [(px + 14, py + 14), (px + 35, py + 40), (px + 58, py + 14)])
                    pygame.draw.line(superficie, (215, 249, 255), (px + 36, py + 15), (px + 36, py + 53), 2)
                    pygame.draw.line(superficie, (242, 255, 255), (px + 37, py + 20), (px + 37, py + 47), 1)
                    for orb in range(3):
                        brilho = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t_anim * 1.2 + orb + seg))
                        self._desenhar_halo_luz(superficie, px + 12 + orb * 16, py + 8 + (orb % 2) * 4,
                                                misturar_cores((94, 198, 159), (236, 255, 243), brilho), 4, 0.25 + noite * 0.7)

        # Camada 3: detalhes frontais bem suaves para não poluir.
        for seg, base_x in self._iterar_segmentos_sprite(0.42, 90):
            rng = self._rng_segmento("frente", seg)
            if self.cenario in ("cidade", "neve"):
                for i in range(2):
                    px = base_x + 12 + i * 38
                    pygame.draw.rect(superficie, (52, 61, 74), (px, 677, 2, 19))
                    if self.cenario == "cidade":
                        pygame.draw.rect(superficie, (71, 136, 73), (px - 5, 688, 12, 8))
                        pygame.draw.rect(superficie, (92, 167, 94), (px - 2, 684, 6, 5))
                    else:
                        pygame.draw.rect(superficie, (236, 244, 250), (px - 5, 688, 12, 8))
            elif self.cenario == "deserto":
                for i in range(2):
                    px = base_x + 14 + i * 34
                    pygame.draw.arc(superficie, (178, 136, 83), (px, 686, 16, 7), math.radians(200), math.radians(340), 1)
                    pygame.draw.rect(superficie, (219, 183, 113), (px + 6, 688, 3, 1))
            elif self.cenario == "vulcao":
                for i in range(2):
                    px = base_x + 10 + i * 36
                    pygame.draw.polygon(superficie, (71, 51, 58), [(px, 697), (px + 7, 686), (px + 16, 697)])
                    if i == 0:
                        pygame.draw.rect(superficie, (254, 120, 56), (px + 5, 690, 3, 2))
            elif self.cenario == "floresta":
                for i in range(2):
                    px = base_x + 12 + i * 35
                    sway = int(math.sin(t_anim + px * 0.05) * 2)
                    pygame.draw.line(superficie, (91, 152, 82), (px, 697), (px + sway, 689), 1)
                    pygame.draw.line(superficie, (112, 177, 96), (px + 4, 697), (px + 4 + sway, 688), 1)
            elif self.cenario == "cidade_futurista":
                for i in range(2):
                    px = base_x + 11 + i * 34
                    pygame.draw.line(superficie, (86, 232, 244), (px, 692), (px + 10, 692), 1)
                    pygame.draw.line(superficie, (224, 128, 255), (px + 12, 695), (px + 18, 695), 1)
            elif self.cenario == "ilhas_celestes":
                for i in range(2):
                    px = base_x + 12 + i * 34
                    pygame.draw.line(superficie, (185, 236, 220), (px, 694), (px + 7, 688), 1)
                    pygame.draw.line(superficie, (217, 252, 237), (px + 3, 697), (px + 10, 691), 1)

        # Clima reforça a sensação de integração do cenário.
        if chuvoso:
            for i in range(0, LARGURA_VIRTUAL, 54):
                y = 590 + (i % 3) * 16
                pygame.draw.line(superficie, (180, 208, 232), (i, y), (i + 16, y + 1), 1)
        elif quente and not poeira:
            for i in range(0, LARGURA_VIRTUAL, 88):
                y = 575 + (i % 2) * 10
                pygame.draw.line(superficie, misturar_cores(cor_ceu, (245, 212, 160), 0.24), (i, y), (i + 20, y), 1)

    def _desenhar_chao_vivo(self, superficie):
        clima = getattr(self, "clima_tipo", "limpo")
        t_anim = self.tempo_animacao * 0.12
        if self.cenario == "cidade":
            for x in range(-20, LARGURA_VIRTUAL + 40, 54):
                px = int((x - self.desloc_chao * 1.0) % (LARGURA_VIRTUAL + 54)) - 20
                pygame.draw.line(superficie, (114, 132, 150), (px, 741), (px + 20, 741), 1)
            if clima in ("chuva", "tempestade", "chuva_acida"):
                for x in range(0, LARGURA_VIRTUAL, 64):
                    y = 734 + (x % 3)
                    pygame.draw.line(superficie, (168, 188, 210), (x, y), (x + 14, y + 1), 1)
        elif self.cenario == "neve":
            for x in range(10, LARGURA_VIRTUAL, 70):
                pygame.draw.arc(superficie, (235, 246, 255), (x, 726 + (x % 2) * 3, 24, 8), math.radians(180), math.radians(360), 1)
        elif self.cenario == "deserto":
            for x in range(0, LARGURA_VIRTUAL, 58):
                yy = 736 + int(math.sin(t_anim + x * 0.02) * 1)
                pygame.draw.line(superficie, (225, 188, 110), (x, yy), (x + 18, yy), 1)
        elif self.cenario == "vulcao":
            for x in range(4, LARGURA_VIRTUAL, 64):
                pulso = int((0.5 + 0.5 * math.sin(t_anim * 1.4 + x)) * 2)
                pygame.draw.rect(superficie, (255, 121, 56), (x, 738 + pulso, 5, 2))
        elif self.cenario == "floresta":
            # detalhes vivos do piso: grama baixa e pequenos brilhos orgânicos.
            for x in range(8, LARGURA_VIRTUAL, 44):
                sway = int(math.sin(t_anim + x * 0.16) * 1)
                base_y = 738 + (x % 3 == 0)
                pygame.draw.line(superficie, (92, 150, 81), (x, base_y), (x + sway, 732), 1)
                if (x // 44) % 2 == 0:
                    pygame.draw.line(superficie, (139, 188, 101), (x + 5, 739), (x + 7 + sway, 734), 1)
            for x in range(20, LARGURA_VIRTUAL, 96):
                shimmer = 1 if math.sin(t_anim * 1.4 + x) > 0.2 else 0
                pygame.draw.line(superficie, (156, 125, 86), (x, 747), (x + 8, 746 + shimmer), 1)
        elif self.cenario == "cidade_futurista":
            for x in range(0, LARGURA_VIRTUAL, 56):
                pygame.draw.line(superficie, (74, 224, 244), (x, 739), (x + 16, 739), 1)
        elif self.cenario == "ilhas_celestes":
            for x in range(8, LARGURA_VIRTUAL, 62):
                pygame.draw.line(superficie, (185, 236, 220), (x, 739), (x + 12, 739), 1)

    def draw(self, superficie, cor_ceu, e_noite):
        # v3.97: os sete biomas novos EXCLUEM completamente os tiles antigos.
        # Uma unica faixa artistica continua se movendo inteira (sem cortes em Y).
        arte_nova = self._obter_arte_externa()
        if arte_nova is not None:
            visuais397.desenhar_ceu(superficie, cor_ceu, self.fase_ciclo,
                                   self.peso_noite, self.cenario, self.estrelas,
                                   self.tempo_animacao, self.nuvens)
            visuais397.desenhar_animacoes_fundo(superficie, self.cenario, self.tempo_animacao,
                                                self._desloc_arte_fundo, self._desloc_arte,
                                                self.fase_ciclo, self.peso_noite)
            visuais397.desenhar_panorama(superficie, arte_nova, self._desloc_arte, 230)
            visuais397.desenhar_emenda_panorama(superficie, cor_ceu, self.cenario, self.peso_noite, 230)
            # Escurece o panorama ao anoitecer, sem afetar objetos ou HUD.
            noite = max(0.0, min(1.0, self.peso_noite))
            if noite > .02:
                self._overlay_arte_noite.set_alpha(int(114 * noite))
                superficie.blit(self._overlay_arte_noite, (0, 230))
            visuais397.desenhar_animacoes_frente(superficie, self.cenario, self.tempo_animacao,
                                                 self._desloc_arte_fundo, self._desloc_arte,
                                                 self.fase_ciclo, noite)
            visuais397.desenhar_reacao_noturna(superficie, self.cenario, noite,
                                               self.tempo_animacao, self._desloc_arte)
            self._desenhar_particulas_ambiente(superficie)
            visuais397.desenhar_foco_pista(superficie, self.cenario, noite)
            visuais397.desenhar_acabamento_proximo(superficie, self.cenario,
                                                   self._desloc_arte * 2.8, noite)
            return
        # Fallback preservado apenas para biomas sem arte nova.
        # Ramo legado mantido apenas para o bioma sem arte nova.
        # Gradiente em mais faixas para dar um ceu mais rico sem custo alto.
        _pro_sub_inicio("qa_ceu_2d")
        fase = self.fase_ciclo
        peso_noite = max(0.0, min(1.0, self.peso_noite))
        cor_ceu_sat = saturar_cor(cor_ceu, 1.10)
        _ceu_gradiente_v3233(superficie, cor_ceu_sat, fase, peso_noite,
                             self.cenario, self.world.lightweight)

        # Faixas quentes e frias no horizonte durante transicoes, do amanhecer ao anoitecer.
        peso_por_sol = max(0.0, 1.0 - abs(fase - 0.74) / 0.11)
        peso_amanhecer = max(0.0, 1.0 - abs(fase - 0.16) / 0.09)
        peso_crepusculo = max(peso_por_sol, peso_amanhecer)
        if peso_crepusculo > 0.01:
            cor_horizonte = (255, 138, 84)
            cor_secundaria = (255, 208, 136)
            for y, altura, fator in ((330, 18, 0.10), (350, 20, 0.16), (374, 24, 0.22), (402, 22, 0.17), (426, 18, 0.10)):
                cor_faixa = misturar_cores(cor_ceu, cor_horizonte, peso_crepusculo * fator)
                pygame.draw.rect(superficie, cor_faixa, (0, y, LARGURA_VIRTUAL, altura))
            for y, altura, fator in ((312, 10, 0.10), (444, 12, 0.08)):
                cor_faixa = misturar_cores(cor_ceu, cor_secundaria, peso_crepusculo * fator)
                pygame.draw.rect(superficie, cor_faixa, (0, y, LARGURA_VIRTUAL, altura))

        # Sol percorre o ceu durante o dia completo, com amanhecer e por do sol destacados.
        if 0.10 <= fase <= 0.82:
            u = max(0.0, min(1.0, (fase - 0.10) / 0.72))
            sun_x = -24 + (LARGURA_VIRTUAL + 48) * u
            sun_y = 314 - math.sin(math.pi * u) * 178
            self._desenhar_sol(superficie, sun_x, sun_y, self._cor_ceu_na_altura(cor_ceu, sun_y))

        # Lua cruza o ceu do fim da tarde ate a madrugada.
        if fase >= 0.78 or fase <= 0.18:
            if fase >= 0.78:
                u = (fase - 0.78) / 0.22
            else:
                u = 1.0 + (fase / 0.18)
                u /= 2.0
            moon_x = -34 + (LARGURA_VIRTUAL + 68) * u
            moon_y = 172 - math.sin(math.pi * u) * 68
            self._desenhar_lua(superficie, moon_x, moon_y, self._cor_ceu_na_altura(cor_ceu, moon_y), max(0.26, peso_noite))

        # Estrelas com brilho graduado e twinkle de pixel; aparecem ao anoitecer.
        if peso_noite > 0.015:
            for est in self.estrelas:
                osc = (math.sin(self.tempo_animacao * est["blink"] + est["offset"]) + 1.0) * 0.5
                brilho = (0.42 + 0.58 * osc) * est["brilho"] * peso_noite
                if brilho < 0.10:
                    continue
                cor_estrela = misturar_cores(cor_ceu, (218, 235, 255), min(0.96, brilho))
                px, py = int(est["x"]), int(est["y"])
                tam = est["tamanho"] if brilho > 0.48 else 1
                pygame.draw.rect(superficie, cor_estrela, (px, py, tam, tam))
                if brilho > 0.74 and osc > 0.78:
                    # Pequenos reflexos cruzados em algumas estrelas mais fortes.
                    pygame.draw.line(superficie, cor_estrela, (px - 2, py), (px + 3, py), 1)
                    pygame.draw.line(superficie, cor_estrela, (px, py - 2), (px, py + 3), 1)

        # Nuvens do ceu principal seguem a mesma linguagem pixel-art dos eventos climaticos.
        visibilidade_nuvens = max(0.16, 1.0 - peso_noite * 0.76)
        cor_base_nuvem = (239, 244, 252) if peso_noite < 0.25 else (104, 120, 160)
        if peso_crepusculo > 0.01:
            cor_base_nuvem = misturar_cores(cor_base_nuvem, (255, 190, 150), peso_crepusculo * 0.72)
        cor_nuvem = misturar_cores(cor_ceu, cor_base_nuvem, 0.66 * visibilidade_nuvens)
        cor_sombra_nuvem = misturar_cores(cor_ceu, (112, 129, 164) if peso_noite < 0.45 else (37, 45, 80), 0.74 * visibilidade_nuvens)
        cor_luz_nuvem = misturar_cores(cor_nuvem, (255, 251, 236), 0.35 + peso_crepusculo * 0.20)
        if visibilidade_nuvens > 0.10:
            for idx, nuvem in enumerate(self.nuvens):
                x, y, t = int(nuvem["x"]), int(nuvem["y"]), nuvem["tam"]
                escala = 1 if t < 28 else 2
                largura_aprox = 64 * escala
                pos_x = x - largura_aprox // 2
                pos_y = y - (20 * escala)
                desenhar_nuvem_pixel_art(superficie, pos_x, pos_y, escala, cor_nuvem, cor_sombra_nuvem, cor_luz_nuvem)
                if peso_crepusculo > 0.06 and idx % 2 == 0:
                    reflexo = misturar_cores(cor_luz_nuvem, (255, 214, 162), min(0.65, peso_crepusculo * 0.90))
                    pygame.draw.rect(superficie, reflexo, (pos_x + 10 * escala, pos_y + 10 * escala, 18 * escala, 3 * escala), border_radius=escala)

        _pro_sub_fim()  # qa_ceu_2d
        if self._bioma_spriteado_ativo():
            self.world.night = self.peso_noite
            self.world.climate = self.clima_tipo
            _pro_sub_inicio("qa_world_draw")
            self.world.draw(superficie)
            _pro_sub_fim()
            _pro_sub_inicio("qa_particulas_mundo")
            self._desenhar_particulas_ambiente(superficie)
            _pro_sub_fim()
            return

        tile_montanhas = self._obter_tile_montanhas(cor_ceu)
        offset_longe = int(-self.camada_longe) % LARGURA_VIRTUAL
        superficie.blit(tile_montanhas, (0, self.Y_MONTANHAS),
                        (offset_longe, 0, LARGURA_VIRTUAL, self.H_MONTANHAS))

        tile_predios = self._obter_tile_predios(cor_ceu, e_noite)
        offset_perto = int(-self.camada_perto) % LARGURA_VIRTUAL
        superficie.blit(tile_predios, (0, self.Y_PREDIOS),
                        (offset_perto, 0, LARGURA_VIRTUAL, self.H_PREDIOS))
        self._desenhar_bioma_vivo(superficie, cor_ceu, e_noite)

        # v3.93: recortes aprovados de arte pixelada, em faixa circular pre-composta.
        # HUD, personagens e chao nao estao nos assets. Sem escalonamento por frame.
        faixa_arte = self._obter_arte_externa()
        if faixa_arte is not None:
            self._desenhar_arte_externa_em_camadas(superficie)

        # Atmosfera sutil para deixar os biomas vivos sem roubar foco da jogabilidade.
        self._desenhar_particulas_ambiente(superficie)
        self._desenhar_nevoa_foco(superficie, cor_ceu)

    def _obter_tile_chao(self):
        """Textura de piso por bioma, gerada uma vez e reaproveitada."""
        tile_pronto = self._cache_chao.get(self.cenario)
        if tile_pronto is not None:
            return tile_pronto

        # Tile longo para reduzir o padrao repetitivo sem custo por frame significativo.
        largura_tile = 900
        altura_chao = 70
        tile = pygame.Surface((largura_tile, altura_chao)).convert()
        rng = random.Random(6138 if self.cenario == "cidade" else (9152 if self.cenario == "deserto" else 3721))

        if self.cenario == "deserto":
            tile.fill((173, 120, 54))
            pygame.draw.rect(tile, (194, 143, 66), (0, 0, largura_tile, 22))
            pygame.draw.rect(tile, (211, 158, 76), (0, 0, largura_tile, 14))
            pygame.draw.line(tile, (238, 193, 105), (0, 1), (largura_tile - 1, 1), 2)
            pygame.draw.rect(tile, (155, 101, 48), (0, 20, largura_tile, 3))
            pygame.draw.rect(tile, (126, 90, 49), (0, 24, largura_tile, 46))
            pygame.draw.rect(tile, (143, 103, 54), (0, 25, largura_tile, 25))
            for idx in range(largura_tile // 7):
                x = rng.randrange(2, largura_tile - 2)
                y = rng.randrange(5, altura_chao - 2)
                cor = rng.choice(((226, 179, 91), (191, 137, 65), (117, 83, 47), (234, 192, 116)))
                pygame.draw.rect(tile, cor, (x, y, rng.choice((2, 3, 5)), 1))
            for x, y in ((28, 31), (94, 47), (146, 36)):
                pygame.draw.line(tile, (232, 190, 112), (x, y), (x + 10, y - 2), 1)
                pygame.draw.line(tile, (110, 78, 47), (x + 8, y - 1), (x + 16, y + 2), 1)
            # Tufos secos esparsos para manter a silhueta de pixel art.
            for x in (18, 72, 127, 164):
                pygame.draw.line(tile, (81, 111, 49), (x, 17), (x - 3, 11), 1)
                pygame.draw.line(tile, (98, 130, 56), (x, 17), (x + 3, 10), 1)
            for x in range(26, largura_tile - 20, 96):
                pygame.draw.arc(tile, (132, 94, 55), (x, 28, 18, 8), math.radians(200), math.radians(340), 1)
                pygame.draw.rect(tile, (238, 196, 108), (x + 3, 24, 2, 2))
                pygame.draw.rect(tile, (184, 132, 70), (x + 10, 31, 3, 1))

        elif self.cenario == "neve":
            tile.fill((112, 133, 151))
            pygame.draw.rect(tile, (169, 190, 205), (0, 0, largura_tile, 20))
            pygame.draw.rect(tile, (224, 238, 247), (0, 0, largura_tile, 13))
            pygame.draw.line(tile, (248, 252, 255), (0, 0), (largura_tile - 1, 0), 2)
            pygame.draw.line(tile, (128, 162, 185), (0, 15), (largura_tile - 1, 15), 2)
            pygame.draw.rect(tile, (67, 87, 108), (0, 21, largura_tile, 49))
            pygame.draw.rect(tile, (81, 105, 126), (0, 24, largura_tile, 24))
            pygame.draw.line(tile, (140, 168, 188), (0, 25), (largura_tile - 1, 25), 1)
            pygame.draw.line(tile, (46, 64, 83), (0, 68), (largura_tile - 1, 68), 2)
            for idx in range(largura_tile // 18):
                x = rng.randrange(2, largura_tile - 12)
                y = rng.randrange(27, 67)
                cor = rng.choice(((130, 158, 178), (58, 78, 99), (177, 202, 220)))
                pygame.draw.line(tile, cor, (x, y), (min(largura_tile - 1, x + rng.randrange(3, 12)), y - 1), 1)
            for x in (31, 83, 143):
                pygame.draw.rect(tile, (226, 241, 250), (x, 7, 5, 2))
                pygame.draw.rect(tile, (190, 219, 237), (x + 3, 9, 4, 2))
            for x in range(20, largura_tile - 24, 92):
                pygame.draw.arc(tile, (235, 247, 255), (x, 4, 28, 10), math.radians(180), math.radians(360), 1)
                pygame.draw.rect(tile, (255, 255, 255), (x + 12, 6, 2, 2))
                pygame.draw.line(tile, (162, 190, 208), (x + 9, 33), (x + 20, 30), 1)

        elif self.cenario == "vulcao":
            tile.fill((53, 35, 39))
            pygame.draw.rect(tile, (93, 43, 39), (0, 0, largura_tile, 19))
            pygame.draw.rect(tile, (42, 33, 40), (0, 19, largura_tile, 51))
            pygame.draw.line(tile, (255, 93, 38), (0, 1), (largura_tile - 1, 1), 2)
            for x in range(8, largura_tile, 53):
                pygame.draw.rect(tile, (255, 115, 40), (x, rng.randint(25, 62), rng.choice((3, 5, 8)), 2))
                pygame.draw.rect(tile, (122, 56, 43), (x + 12, rng.randint(28, 60), 7, 3))
            for x in range(18, largura_tile - 24, 76):
                pygame.draw.line(tile, (255, 136, 64), (x, 22), (x + 10, 30), 1)
                pygame.draw.line(tile, (255, 136, 64), (x + 10, 30), (x + 18, 24), 1)
                pygame.draw.rect(tile, (255, 202, 107), (x + 8, 29, 2, 2))
        elif self.cenario == "cidade_futurista":
            tile.fill((20, 30, 62))
            pygame.draw.rect(tile, (28, 38, 74), (0, 0, largura_tile, 20))
            pygame.draw.rect(tile, (12, 18, 42), (0, 20, largura_tile, 50))
            pygame.draw.line(tile, (63, 241, 255), (0, 1), (largura_tile - 1, 1), 2)
            pygame.draw.line(tile, (201, 75, 255), (0, 18), (largura_tile - 1, 18), 2)
            for x in range(12, largura_tile, 38):
                pygame.draw.rect(tile, (60, 220, 255), (x, 29, 12, 2))
                pygame.draw.rect(tile, (148, 70, 230), (x + 17, 49, 8, 2))
            for x in range(24, largura_tile - 28, 88):
                pygame.draw.rect(tile, (62, 241, 255), (x, 10, 24, 2))
                pygame.draw.line(tile, (210, 112, 255), (x + 10, 12), (x + 10, 21), 1)
                pygame.draw.line(tile, (62, 241, 255), (x + 10, 21), (x + 24, 24), 1)
        elif self.cenario == "reino_submerso":
            tile.fill((12, 65, 104))
            pygame.draw.rect(tile, (20, 105, 140), (0, 0, largura_tile, 18))
            pygame.draw.rect(tile, (8, 45, 82), (0, 18, largura_tile, 52))
            pygame.draw.line(tile, (75, 225, 235), (0, 1), (largura_tile - 1, 1), 2)
            for x in range(12, largura_tile, 34):
                pygame.draw.rect(tile, (40, 150, 170), (x, rng.randint(25, 57), 5, 11))
                pygame.draw.rect(tile, (75, 205, 200), (x - 4, rng.randint(30, 60), 3, 7))
            for x in range(20, largura_tile - 20, 82):
                pygame.draw.circle(tile, (255, 185, 121), (x, 31), 3)
                pygame.draw.circle(tile, (255, 218, 152), (x + 10, 39), 2)
                pygame.draw.line(tile, (38, 181, 152), (x + 20, 26), (x + 17, 16), 2)
                pygame.draw.line(tile, (58, 212, 176), (x + 20, 26), (x + 25, 18), 2)
        elif self.cenario == "ilhas_celestes":
            tile.fill((82, 145, 195))
            pygame.draw.rect(tile, (135, 195, 220), (0, 0, largura_tile, 18))
            pygame.draw.rect(tile, (65, 115, 175), (0, 18, largura_tile, 52))
            pygame.draw.line(tile, (225, 250, 255), (0, 1), (largura_tile - 1, 1), 2)
            for x in range(8, largura_tile, 42):
                pygame.draw.rect(tile, (190, 220, 235), (x, rng.randint(27, 56), 15, 3))
                pygame.draw.rect(tile, (100, 165, 205), (x + 5, rng.randint(38, 62), 8, 4))
            for x in range(30, largura_tile - 28, 96):
                pygame.draw.arc(tile, (246, 250, 255), (x, 4, 32, 8), math.radians(180), math.radians(360), 1)
                pygame.draw.rect(tile, (255, 235, 162), (x + 13, 7, 3, 3))
                pygame.draw.line(tile, (158, 212, 112), (x + 15, 18), (x + 12, 12), 1)
        elif self.cenario == "floresta":
            # v3.141: pista premium da Floresta, mais rica e coerente com o bioma.
            tile.fill((36, 53, 33))
            # faixa de grama viva / borda superior do solo
            pygame.draw.rect(tile, (68, 110, 58), (0, 0, largura_tile, 8))
            pygame.draw.rect(tile, (92, 145, 72), (0, 0, largura_tile, 4))
            pygame.draw.line(tile, (170, 212, 110), (0, 1), (largura_tile - 1, 1), 1)
            pygame.draw.line(tile, (58, 97, 49), (0, 8), (largura_tile - 1, 8), 2)
            # trilha de terra principal da corrida
            pygame.draw.rect(tile, (116, 84, 57), (0, 10, largura_tile, 25))
            pygame.draw.rect(tile, (98, 71, 49), (0, 35, largura_tile, 35))
            pygame.draw.line(tile, (151, 112, 77), (0, 12), (largura_tile - 1, 12), 1)
            pygame.draw.line(tile, (74, 54, 39), (0, 35), (largura_tile - 1, 35), 1)
            # manchas de desgaste / terra batida
            for x in range(10, largura_tile - 18, 41):
                y = 15 + ((x // 17) % 12)
                comp = 10 + ((x // 23) % 9)
                pygame.draw.line(tile, (133, 97, 66), (x, y), (x + comp, y - (x % 2)), 1)
                pygame.draw.line(tile, (89, 65, 45), (x + 3, y + 9), (x + comp - 2, y + 8), 1)
            # pedrinhas e folhas secas discretas, sem roubar leitura
            for idx in range(largura_tile // 18):
                x = (idx * 19 + 7) % (largura_tile - 6)
                y = 18 + ((idx * 7) % 45)
                if idx % 4 == 0:
                    pygame.draw.rect(tile, (74, 88, 61), (x, y, 2, 1))
                    pygame.draw.rect(tile, (132, 156, 93), (x + 2, y - 1, 1, 1))
                elif idx % 4 == 1:
                    pygame.draw.rect(tile, (88, 67, 48), (x, y, 2, 2))
                elif idx % 4 == 2:
                    pygame.draw.line(tile, (176, 136, 89), (x, y), (x + 3, y + 1), 1)
                else:
                    pygame.draw.line(tile, (108, 143, 76), (x, y), (x + 2, y - 2), 1)
            # pequenos tufos laterais e raízes rasas na borda superior
            for x in range(20, largura_tile - 24, 74):
                pygame.draw.line(tile, (89, 147, 72), (x, 9), (x - 3, 4), 1)
                pygame.draw.line(tile, (124, 181, 91), (x, 9), (x + 3, 3), 1)
                pygame.draw.line(tile, (85, 61, 42), (x + 10, 16), (x + 17, 13), 1)
                pygame.draw.line(tile, (74, 54, 39), (x + 10, 17), (x + 16, 15), 1)
        else:
            tile.fill((43, 47, 57))
            # Cidade: pista integralmente asfaltada, guia de concreto sem grama.
            pygame.draw.rect(tile, (38, 42, 52), (0, 0, largura_tile, 70))
            pygame.draw.rect(tile, (85, 87, 94), (0, 0, largura_tile, 4))
            pygame.draw.line(tile, (176, 176, 168), (0, 4), (largura_tile-1, 4), 1)
            pygame.draw.rect(tile, (47, 51, 61), (0, 5, largura_tile, 64))
            pygame.draw.rect(tile, (40, 44, 54), (0, 48, largura_tile, 21))
            pygame.draw.line(tile, (79, 82, 90), (0, 23), (largura_tile-1, 23), 1)
            for xx in range(26, largura_tile-8, 125):
                pygame.draw.rect(tile, (194, 183, 122), (xx, 38, 48, 3), border_radius=1)
                pygame.draw.rect(tile, (91, 92, 96), (xx+1, 41, 45, 1))
            for xx in range(12, largura_tile, 47):
                yy=10+((xx*7)%51)
                pygame.draw.line(tile, (60, 64, 72), (xx, yy), (xx+5, yy), 1)
            for idx in range(largura_tile // 45):
                x = (idx * 47 + 13) % (largura_tile - 12)
                py = 23 + ((idx * 17) % 43)
                cor_pedra = (77, 81, 91) if idx % 2 else (29, 33, 42)
                pygame.draw.rect(tile, cor_pedra, (x, py, 2 + (idx % 3), 1 + (idx % 2)))
                if idx % 3 == 0:
                    pygame.draw.line(tile, (29, 33, 42), (x + 3, py + 5), (x + 8, py + 4), 1)
                    pygame.draw.line(tile, (57, 61, 70), (x + 4, py + 6), (x + 7, py + 5), 1)
            for _ in range(largura_tile // 70):
                x = rng.randrange(8, largura_tile - 22)
                y = rng.choice((28, 34, 41, 49, 56, 63))
                comprimento = rng.randint(4, 10)
                pygame.draw.rect(tile, (62, 66, 76), (x, y, comprimento, 1))
                pygame.draw.rect(tile, (31, 35, 43), (x + 2, y + 1, max(2, comprimento - 2), 1))
                if rng.random() < 0.35:
                    pygame.draw.rect(tile, (82, 86, 96), (x + 4, y + 3, 2, 1))

        acabamento_chao = {
            "cidade": ((87, 90, 96), (55, 59, 68), (174, 174, 166)),
            "neve": ((236, 246, 252), (138, 178, 205), (255, 255, 255)),
            "deserto": ((228, 184, 116), (145, 100, 47), (245, 212, 146)),
            "vulcao": ((255, 133, 57), (95, 42, 38), (255, 204, 113)),
            "cidade_futurista": ((68, 241, 255), (27, 55, 86), (211, 110, 255)),
            "ilhas_celestes": ((224, 241, 248), (87, 145, 187), (174, 232, 199)),
            "floresta": ((117, 188, 86), (43, 76, 41), (202, 229, 134)),
            "reino_submerso": ((96, 224, 219), (15, 77, 104), (181, 240, 230)),
        }.get(self.cenario, ((92, 184, 96), (40, 74, 46), (214, 229, 148)))
        pygame.draw.rect(tile, acabamento_chao[0], (0, 0, largura_tile, 4))
        pygame.draw.line(tile, acabamento_chao[1], (0, 4), (largura_tile - 1, 4), 2)
        for x in range(18, largura_tile - 10, 74):
            comprimento = 7 + ((x // 37) % 8)
            y_rastro = 7 + ((x // 29) % 6)
            pygame.draw.line(tile, acabamento_chao[2], (x, y_rastro), (x + comprimento, max(5, y_rastro - 1)), 1)

        self._cache_chao[self.cenario] = tile
        return tile

    def draw_foreground(self, superficie):
        if self._bioma_spriteado_ativo():
            self.world.draw_foreground(superficie)

    def draw_chao(self, superficie):
        """Desenha o piso rolando junto dos obstaculos, como um plano de mundo coerente."""
        y = ALTURA_VIRTUAL - 70
        tile = self._obter_tile_chao()
        largura_tile = tile.get_width()
        # pygame.Rect converte x flutuante para pixel inteiro; usar ceil aqui faz
        # o padrao do piso alinhar com o deslocamento visivel dos sprites terrestres.
        desloc = int(math.ceil(self.desloc_chao - 0.0000001)) % largura_tile
        x = -desloc
        while x < LARGURA_VIRTUAL:
            superficie.blit(tile, (x, y))
            x += largura_tile
        self._desenhar_chao_vivo(superficie)


def desenhar_cenario_jetpack(superficie, cor_ceu, fase_ciclo, peso_noite, frame, estrelas):
    """Fundo exclusivo do voo: apenas camadas de céu, nuvens e astros, sem chão/cidade."""
    base = tuple(max(0, min(255, int(c))) for c in cor_ceu)
    for faixa in range(10):
        fator = 0.76 + faixa * 0.032
        cor_faixa = tuple(max(0, min(255, int(c * fator))) for c in base)
        y0 = faixa * (ALTURA_VIRTUAL // 10)
        y1 = (faixa + 1) * (ALTURA_VIRTUAL // 10)
        pygame.draw.rect(superficie, cor_faixa, (0, y0, LARGURA_VIRTUAL, y1 - y0 + 1))

    noite = max(0.0, min(1.0, float(peso_noite)))
    # Faixa luminosa distante, mantida também durante o crepúsculo.
    quente = max(0.0, 1.0 - abs(float(fase_ciclo) - 0.45) / 0.16)
    if quente > 0.01:
        cor_horizonte = misturar_cores(base, (255, 122, 65), 0.45 * quente)
        pygame.draw.rect(superficie, cor_horizonte, (0, 535, LARGURA_VIRTUAL, 90))
        pygame.draw.rect(superficie, misturar_cores(base, (255, 177, 104), 0.22 * quente),
                         (0, 565, LARGURA_VIRTUAL, 44))

    # Sol pixelado a acompanhar o ciclo existente.
    fase = float(fase_ciclo) % 1.0
    sol_visivel = fase < 0.49 or fase > 0.94
    if sol_visivel and noite < 0.82:
        if fase < 0.42:
            u = fase / 0.42
            sx = int(24 + (LARGURA_VIRTUAL - 48) * u)
            sy = int(205 - math.sin(math.pi * u) * 118)
        else:
            u = (fase - 0.42) / 0.08 if fase <= 0.50 else (fase - 0.94) / 0.06
            sx = int(LARGURA_VIRTUAL - 20 + 46 * u) if fase <= 0.50 else int(-18 + 48 * u)
            sy = int(205 + 125 * u) if fase <= 0.50 else int(330 - 120 * u)
        brilho = misturar_cores(base, (255, 199, 76), 0.90)
        pygame.draw.rect(superficie, misturar_cores(base, (255, 142, 35), 0.5), (sx - 18, sy - 18, 36, 36))
        pygame.draw.rect(superficie, brilho, (sx - 13, sy - 13, 26, 26))
        pygame.draw.rect(superficie, (255, 245, 173), (sx - 8, sy - 8, 16, 16))
        pygame.draw.rect(superficie, (255, 255, 223), (sx - 4, sy - 4, 8, 8))
        if frame % 16 < 8:
            pygame.draw.rect(superficie, (255, 218, 111), (sx - 2, sy - 24, 4, 8))
            pygame.draw.rect(superficie, (255, 218, 111), (sx - 2, sy + 16, 4, 8))
            pygame.draw.rect(superficie, (255, 218, 111), (sx - 24, sy - 2, 8, 4))
            pygame.draw.rect(superficie, (255, 218, 111), (sx + 16, sy - 2, 8, 4))

    # Lua pixelada; o recorte usa a cor local aproximada do céu.
    if noite > 0.16:
        u = max(0.0, min(1.0, (fase - 0.48) / 0.44))
        mx = int(-8 + (LARGURA_VIRTUAL + 16) * u)
        my = int(168 - math.sin(math.pi * u) * 66)
        lum = misturar_cores(base, (222, 237, 255), 0.88 * noite)
        pygame.draw.circle(superficie, misturar_cores(base, (157, 192, 255), 0.42 * noite), (mx, my), 24)
        pygame.draw.circle(superficie, lum, (mx, my), 17)
        pygame.draw.circle(superficie, base, (mx + 7, my - 5), 14)
        pygame.draw.rect(superficie, (238, 246, 255), (mx - 10, my - 4, 4, 3))
        pygame.draw.rect(superficie, (205, 224, 249), (mx - 2, my + 5, 3, 2))

    # Estrelas reutilizam a lista já criada no cenário principal.
    if noite > 0.025:
        for estrela in estrelas:
            brilho = (math.sin(frame * estrela["blink"] + estrela["offset"]) + 1.0) * 0.5
            intensidade = (0.22 + brilho * 0.78) * estrela["brilho"] * noite
            if intensidade < 0.08:
                continue
            cor = misturar_cores(base, (231, 243, 255), min(0.98, intensidade))
            x, y = int(estrela["x"]), int(estrela["y"])
            tam = max(1, int(estrela["tamanho"])) if intensidade > 0.55 else 1
            pygame.draw.rect(superficie, cor, (x, y, tam, tam))
            if intensidade > 0.78 and brilho > 0.7:
                pygame.draw.line(superficie, cor, (x - 3, y), (x + 3, y), 1)
                pygame.draw.line(superficie, cor, (x, y - 3), (x, y + 3), 1)

    # Nuvens em camadas pixeladas, deslizando em velocidades distintas.
    for idx, (base_x, y, escala) in enumerate(((-30, 145, 1.0), (88, 252, 0.82),
                                                (240, 185, 0.94), (365, 380, 1.12),
                                                (20, 555, 0.72), (280, 625, 0.9))):
        largura = int(92 * escala)
        x = int((base_x - frame * (0.24 + idx * 0.035)) % (LARGURA_VIRTUAL + 130) - 65)
        sombra = misturar_cores(base, (65, 82, 116) if noite > 0.3 else (94, 129, 164), 0.64)
        luz = misturar_cores(base, (117, 142, 177) if noite > 0.3 else (220, 235, 246), 0.60)
        pygame.draw.rect(superficie, sombra, (x + 8, y + 13, largura, 18))
        pygame.draw.rect(superficie, sombra, (x + 22, y + 2, int(22 * escala), 28))
        pygame.draw.rect(superficie, sombra, (x + 47, y - 4, int(30 * escala), 35))
        pygame.draw.rect(superficie, luz, (x + 14, y + 12, largura - 14, 7))
        pygame.draw.rect(superficie, luz, (x + 25, y + 4, int(18 * escala), 7))
        pygame.draw.rect(superficie, luz, (x + 52, y, int(23 * escala), 8))


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
        # Somente temporizador VISUAL, sem impacto na velocidade do pulo.
        self.anim_pulo_frames = 0
        self.anim_pouso_ticks = 0
        # Tolerâncias de entrada, em ticks de 60 Hz; são opcionais no menu.
        self.ajuda_pulo = True
        self.coyote_ticks = 0
        self.buffer_pulo_ticks = 0

        # Power-ups
        self.tempo_ima = 0
        self.tempo_turbo = 0
        self.tempo_mult = 0
        self.tempo_slow = 0
        self.tempo_jetpack = 0
        self.tempo_crono = 0
        self.tempo_turbo_fantasma = 0
        self.tempo_impulso = 0
        self.carga_impulso = 0
        self.prisma_hits = 0
        # Power-up CLONE: cada impacto consome um clone, sem temporizador.
        self.clones_ativos = 0
        self.clones_maximos = 0
        self.jetpack_pousando = 0
        self.jetpack_fase = None  # subindo, voando, descendo
        self.jetpack_transicao_timer = 0
        self.jetpack_subida_duracao = 45
        self.jetpack_descida_duracao = 48
        self.jetpack_bottom_origem = self.chao_y
        self.jetpack_nivel = 1  # 0 baixa, 1 media, 2 alta
        self.jetpack_indice_moeda = 0
        self.morte_por_buraco = False
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
        """Área central do corpo: ignora pontas decorativas, aura e pernas soltas.

        A base é proporcional à imagem real da pose. O rect visual e a física
        permanecem intactos; apenas a área usada para testar danos é reduzida.
        """
        largura, altura = self.rect.size
        if self.agachado and self.no_chao:
            # Corpo abaixado: a cabeça fica mais baixa e o personagem ocupa
            # menos altura. A ponta da capa/pés não causa colisões fantasma.
            return pygame.Rect(
                self.rect.left + round(largura * 0.25),
                self.rect.bottom - round(altura * 0.37),
                max(1, round(largura * 0.50)),
                max(1, round(altura * 0.35)),
            )
        if not self.no_chao:
            # Durante o salto, braços, capas e partículas não contam como corpo.
            return pygame.Rect(
                self.rect.left + round(largura * 0.31),
                self.rect.top + round(altura * 0.24),
                max(1, round(largura * 0.38)),
                max(1, round(altura * 0.55)),
            )
        return pygame.Rect(
            self.rect.left + round(largura * 0.29),
            self.rect.top + round(altura * 0.22),
            max(1, round(largura * 0.42)),
            max(1, round(altura * 0.58)),
        )

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
        """Mesmo personagem da arte aprovada, com quadros próprios para cada ação."""
        estado, indice = _estado_skin_jogador(self, frame_contador)
        self.image_original.blit(_v3188_escolher_quadro(
            _quadros_skin(self.skin_nome), self.skin_nome, estado, indice,
            frame_contador, getattr(self, "_v3188_modo_leve", False)), (0, 0))

        # O jetpack e o imã são sobreposições existentes; seus efeitos continuam.
        if self.tempo_jetpack > 0 or self.jetpack_pousando > 0:
            surf = self.image_original
            pygame.draw.rect(surf, (30, 36, 48), (7, 27, 16, 29), border_radius=3)
            pygame.draw.rect(surf, (215, 225, 232), (10, 30, 10, 19), 2, border_radius=2)
            pygame.draw.rect(surf, (238, 112, 31), (12, 34, 6, 12), border_radius=1)
            chama = 4 + (frame_contador % 3) * 2
            pygame.draw.polygon(surf, (255, 116, 25), [(12, 55), (20, 55), (18, 55 + chama), (14, 55 + chama)])
            pygame.draw.polygon(surf, (255, 225, 95), [(14, 55), (18, 55), (17, 55 + chama // 2), (15, 55 + chama // 2)])
        if self._visual_cor_atual != self.cor_base:
            # Preserva a indicação visual de poder ativo, sem apagar as cores do traje.
            brilho = self._visual_cor_atual
            for dx, dy in ((11, 24), (70, 37), (57, 9)):
                y_animado = dy + (frame_contador % 4) - 2
                pygame.draw.rect(self.image_original, brilho, (dx, y_animado, 3, 3))
        if self.tempo_ima > 0 and not self.morrendo:
            self.desenhar_raios_ima(self.image_original, frame_contador)

    def ativar_powerup(self, tipo, gerenciador_sons=None, vol_sfx=1.0, vibracao_ligada=True):
        if self.morrendo: return
        self.powerups_coletados += 1
        self._visual_dirty = True
        nivel = self.upgrades.get(tipo, 0)
        config = UPGRADES_CONFIG.get(tipo)
        if tipo == "ESCUDO":
            self.escudo_hits = config["impactos_base"] + (nivel * config["bonus_por_nivel"])
            self.escudo_max = self.escudo_hits
        elif tipo == "PRISMA":
            self.prisma_hits = 1 + (nivel // 2)
        elif tipo == "CRONO":
            self.tempo_crono = config["duracao_base"] + nivel * config["bonus_por_nivel"]
        elif tipo == "TURBO_FANTASMA":
            self.tempo_turbo_fantasma = config["duracao_base"] + nivel * config["bonus_por_nivel"]
        elif tipo == "CLONE":
            # Nível inicial: 3 clones. Cada melhoria permanente adiciona +1.
            self.clones_maximos = config["clones_base"] + (nivel * config["bonus_por_nivel"])
            self.clones_ativos = self.clones_maximos
            disparar_vibracao(0.25, vibracao_ligada)
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
            elif tipo == "JETPACK":
                self.tempo_jetpack = duracao
                self.jetpack_pousando = 0
                self.jetpack_fase = "subindo"
                self.jetpack_transicao_timer = self.jetpack_subida_duracao
                self.jetpack_bottom_origem = self.rect.bottom
                self.jetpack_nivel = 1
                self.jetpack_indice_moeda = 0
                self.no_chao = False
                self.descida_rapida = False
                self.agachado = False
                self.velocidade_y = 0
                self._visual_dirty = True
                disparar_vibracao(0.25, vibracao_ligada)

        if gerenciador_sons:
            gerenciador_sons.tocar_som("powerup", self.tempo_slow > 0, vol_sfx)
            if tipo == "TURBO":
                gerenciador_sons.tocar_som("turbo", self.tempo_slow > 0, vol_sfx)
            elif tipo == "IMA":
                gerenciador_sons.tocar_som("ima", self.tempo_slow > 0, vol_sfx)

    def mover_jetpack(self, direcao):
        """No trecho de voo, direcao -1 sobe e +1 desce uma faixa."""
        if self.jetpack_fase != "voando" or self.morrendo:
            return
        if direcao < 0:
            self.jetpack_nivel = min(2, self.jetpack_nivel + 1)
        elif direcao > 0:
            self.jetpack_nivel = max(0, self.jetpack_nivel - 1)
        self._visual_dirty = True

    def obter_bottom_jetpack(self, nivel=None):
        """Posição inferior do personagem nas três faixas do céu."""
        if nivel is None:
            nivel = self.jetpack_nivel
        bottoms = (self.chao_y - 175, self.chao_y - 295, self.chao_y - 415)
        return bottoms[max(0, min(2, int(nivel)))]

    def obter_y_moeda_jetpack(self, nivel=None):
        """Centro das moedas na mesma altura das três faixas de voo."""
        return int(self.obter_bottom_jetpack(nivel) - self.base_h / 2)

    def pular(self, gerenciador_sons=None, vol_sfx=1.0):
        if self.morrendo or self.jetpack_fase is not None:
            return
        # Coyote só é válido após sair do chão sem pular. Não permite salto duplo.
        pode_coyote = (self.ajuda_pulo and self.coyote_ticks > 0 and
                       not self.no_chao and self.velocidade_y >= 0 and
                       not self.descida_rapida)
        if self.no_chao or pode_coyote:
            self.velocidade_y = -13.5
            self.anim_pulo_frames = 0
            self.anim_pouso_ticks = 0
            self.coyote_ticks = 0
            self.buffer_pulo_ticks = 0
            self.no_chao = False
            self.descida_rapida = False
            self.agachado = False
            self.w_atual, self.h_atual = 58, 96
            self._visual_dirty = True
            self.pulos_na_rodada += 1
            if gerenciador_sons:
                gerenciador_sons.tocar_som("pulo", self.tempo_slow > 0, vol_sfx)
        elif self.ajuda_pulo and self.velocidade_y >= 0 and not self.descida_rapida:
            # Pressionou pouco antes de pousar: executa 1 vez após contato real.
            self.buffer_pulo_ticks = 6

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

    def iniciar_morte(self, por_buraco=False):
        self.morrendo = True
        self.buffer_pulo_ticks = self.coyote_ticks = 0
        self.anim_pouso_ticks = 0
        self.morte_por_buraco = bool(por_buraco)
        self.velocidade_y = 1.5 if por_buraco else -12
        self.tempo_morte = 70 if por_buraco else 60
        self.tempo_turbo = 0
        self.tempo_jetpack = 0
        self.jetpack_pousando = 0
        self.jetpack_fase = None
        self.jetpack_transicao_timer = 0
        self.escudo_hits = 0
        self.agachado = False
        self._visual_dirty = True

    def update_morte(self, particulas, pool_manager):
        # Queda em buraco: o personagem cai para baixo, em vez da animação de ser atingido.
        if self.morte_por_buraco:
            self.velocidade_y += 0.72
            self.rect.y += self.velocidade_y
            self.angulo_rotacao += 5
            self.tempo_morte -= 1
            self._visual_dirty = True
            return
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
            # Usa os seis quadros de morte; mantém a rotação e a trajetória física.
            self.image_original.fill((0, 0, 0, 0))
            estado_morte, indice_morte = _estado_skin_jogador(self, frame_contador)
            self.image_original.blit(_quadros_skin(self.skin_nome)[estado_morte][indice_morte], (0, 0))
            self.image = pygame.transform.rotate(self.image_original, self.angulo_rotacao)
            self.rect = self.image.get_rect(center=self.rect.center)
            self._visual_dirty = False
            return

        self.image_original.fill((0, 0, 0, 0))
        self.aplicar_visual_skin(self._visual_cor_atual, frame_contador)
        # Estilos alternativos mudam o desenho do corpo/roupa, não apenas partículas.
        estilo = max(1, min(8, int(getattr(self, "estilo_visual", 1))))
        if estilo >= 2:
            if estilo == 2:
                pygame.draw.polygon(self.image_original, (235, 245, 255), [(25, 18), (34, 14), (43, 18), (39, 34), (29, 34)])
                pygame.draw.line(self.image_original, (30, 40, 65), (29, 38), (53, 51), 4)
            elif estilo == 3:
                pygame.draw.polygon(self.image_original, (255, 205, 70), [(21, 17), (30, 8), (39, 17), (36, 28), (25, 28)])
                pygame.draw.line(self.image_original, (255, 245, 170), (25, 40), (55, 53), 5)
                pygame.draw.rect(self.image_original, (40, 30, 70), (29, 49, 23, 8), border_radius=3)
            elif estilo == 4:
                pygame.draw.polygon(self.image_original, (25, 30, 48), [(20, 20), (29, 11), (42, 18), (38, 34), (25, 33)])
                pygame.draw.line(self.image_original, (70, 245, 255), (24, 39), (55, 52), 5)
                pygame.draw.line(self.image_original, (255, 70, 150), (26, 46), (51, 58), 3)
                pygame.draw.rect(self.image_original, (225, 245, 255), (34, 23, 13, 4), border_radius=2)
            elif estilo == 5:  # Gelo
                pygame.draw.polygon(self.image_original, (170, 245, 255), [(29, 11), (37, 24), (29, 37), (21, 24)])
                pygame.draw.line(self.image_original, (215, 250, 255), (24, 40), (55, 52), 5)
                pygame.draw.circle(self.image_original, (80, 205, 255), (36, 25), 5, 2)
            elif estilo == 6:  # Fogo
                pygame.draw.polygon(self.image_original, (255, 95, 35), [(22, 34), (20, 20), (29, 27), (33, 8), (40, 25), (48, 18), (45, 37)])
                pygame.draw.line(self.image_original, (255, 220, 70), (24, 43), (55, 53), 5)
            elif estilo == 7:  # Dourado
                pygame.draw.polygon(self.image_original, (255, 205, 55), [(20, 20), (29, 11), (42, 18), (38, 34), (25, 33)])
                pygame.draw.rect(self.image_original, (255, 240, 155), (25, 40, 29, 7), border_radius=2)
                pygame.draw.line(self.image_original, (150, 95, 25), (25, 47), (53, 55), 3)
            else:  # Prismático
                pygame.draw.polygon(self.image_original, (255, 75, 150), [(20, 20), (29, 11), (42, 18), (38, 34), (25, 33)])
                pygame.draw.line(self.image_original, (80, 245, 255), (24, 39), (55, 52), 5)
                pygame.draw.line(self.image_original, (255, 235, 95), (25, 47), (51, 58), 3)
                pygame.draw.circle(self.image_original, (235, 245, 255), (36, 25), 5)
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
               pool_manager=None, gerenciador_sons=None, vol_sfx=1.0, pode_pousar=True):
        if self.ajuda_pulo and self.no_chao and self.jetpack_fase is None:
            self.coyote_ticks = 5
        elif self.coyote_ticks > 0:
            self.coyote_ticks -= 1
        if self.buffer_pulo_ticks > 0:
            self.buffer_pulo_ticks -= 1
        if self.anim_pouso_ticks > 0 and self.no_chao:
            self.anim_pouso_ticks -= 1
        if self.morrendo:
            self.update_morte(particulas, pool_manager)
            return

        if self.jetpack_fase is None and self.no_chao and not pode_pousar:
            if self.ajuda_pulo and self.coyote_ticks > 0:
                # Primeiros ticks após sair da borda: ainda pode saltar.
                self.no_chao = False
                self.velocidade_y = max(0.0, self.velocidade_y)
            else:
                self.iniciar_morte(por_buraco=True)
                self.update_morte(particulas, pool_manager)
                return

        if self.jetpack_fase is None:
            self.agachar(segurando_baixo, gerenciador_sons, vol_sfx)
        else:
            self.agachado = False
        self.anim_pernas += vel_jogo * 0.08
        if not self.no_chao and self.jetpack_fase is None:
            self.anim_pulo_frames += 1

        if self.tempo_ima > 0: self.tempo_ima -= 1
        if self.tempo_turbo > 0: self.tempo_turbo -= 1
        if self.tempo_mult > 0: self.tempo_mult -= 1
        if self.tempo_slow > 0: self.tempo_slow -= 1
        if self.tempo_crono > 0: self.tempo_crono -= 1
        if self.tempo_turbo_fantasma > 0: self.tempo_turbo_fantasma -= 1
        if self.tempo_impulso > 0: self.tempo_impulso -= 1

        if self.tempo_turbo_fantasma > 0:
            self._visual_cor_atual = (180, 225, 255)
        elif self.tempo_crono > 0:
            self._visual_cor_atual = (100, 235, 220)
        elif self.tempo_turbo > 0:
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

        if self.jetpack_fase == "subindo":
            # O personagem ganha altitude enquanto o fundo é gradualmente trocado pelo céu.
            self.no_chao = False
            self.descida_rapida = False
            self.jetpack_transicao_timer = max(0, self.jetpack_transicao_timer - 1)
            progresso = 1.0 - self.jetpack_transicao_timer / float(max(1, self.jetpack_subida_duracao))
            suave = progresso * progresso * (3.0 - 2.0 * progresso)
            destino = self.obter_bottom_jetpack(1)
            self.rect.bottom = int(self.jetpack_bottom_origem + (destino - self.jetpack_bottom_origem) * suave)
            self.velocidade_y = 0
            if self.jetpack_transicao_timer <= 0:
                self.jetpack_fase = "voando"
                self.rect.bottom = destino

        elif self.jetpack_fase == "voando":
            self.no_chao = False
            self.descida_rapida = False
            self.tempo_jetpack = max(0, self.tempo_jetpack - 1)
            destino = self.obter_bottom_jetpack(self.jetpack_nivel)
            diferenca = destino - self.rect.bottom
            if diferenca:
                # Arredondamento a zero podia deixar o personagem parado a 3-4 px
                # da faixa pretendida. Conserva a suavizacao sem perder 1 px/tick.
                passo = max(1, int(abs(diferenca) * 0.22))
                self.rect.bottom += (1 if diferenca > 0 else -1) * min(abs(diferenca), passo)
            self.velocidade_y = 0
            if self.tempo_jetpack <= 0:
                self.jetpack_fase = "descendo"
                self.jetpack_pousando = self.jetpack_descida_duracao
                self.jetpack_transicao_timer = self.jetpack_descida_duracao
                self.jetpack_bottom_origem = self.rect.bottom

        elif self.jetpack_fase == "descendo":
            self.no_chao = False
            self.descida_rapida = False
            self.jetpack_pousando = max(0, self.jetpack_pousando - 1)
            self.jetpack_transicao_timer = max(0, self.jetpack_transicao_timer - 1)
            progresso = 1.0 - self.jetpack_transicao_timer / float(max(1, self.jetpack_descida_duracao))
            suave = progresso * progresso * (3.0 - 2.0 * progresso)
            self.rect.bottom = int(self.jetpack_bottom_origem + (self.chao_y - self.jetpack_bottom_origem) * suave)
            self.velocidade_y = 0
            if self.jetpack_transicao_timer <= 0:
                self.rect.bottom = self.chao_y
                self.jetpack_pousando = 0
                self.jetpack_fase = None
                self.no_chao = True
                self.velocidade_y = 0

        elif self.descida_rapida:
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
        elif self.jetpack_fase is not None or self.jetpack_pousando > 0:
            w_alvo, h_alvo = 80, 80
        elif not self.no_chao:
            if not self.descida_rapida:
                w_alvo, h_alvo = 71, 86

        if self.jetpack_fase is None and self.rect.bottom >= self.chao_y:
            if not pode_pousar:
                if not (self.ajuda_pulo and self.coyote_ticks > 0):
                    self.rect.bottom = self.chao_y
                    self.iniciar_morte(por_buraco=True)
                    self.update_morte(particulas, pool_manager)
                    return
                # Janela de coyote somente sobre a borda; após expirar,
                # a queda volta a ter o comportamento original.
                self.no_chao = False
            else:
                pousou_agora = not self.no_chao
                if pousou_agora and not self.agachado:
                    self.w_atual, self.h_atual = 84, 78
                self.rect.bottom = self.chao_y
                self.velocidade_y = 0
                self.no_chao = True
                self.descida_rapida = False
                self.anim_pulo_frames = 0
                if pousou_agora:
                    self.anim_pouso_ticks = 3
                    # O buffer só dispara após um pouso real, uma única vez.
                    if (self.ajuda_pulo and self.buffer_pulo_ticks > 0 and
                            not self.morrendo and self.jetpack_fase is None):
                        self.pular(gerenciador_sons, vol_sfx)

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


class Buraco(Sprite):
    """Fenda no terreno com paredes em perspectiva e bordas de terra texturizadas."""
    LARGURAS = {
        "pequeno": (48, 66),
        "medio": (92, 122),
        "grande": (154, 196),
    }

    def __init__(self, x_pos, cenario="cidade", tamanho="pequeno"):
        super().__init__()
        self.cenario = cenario
        self.tamanho = tamanho
        self.largura = random.randint(*self.LARGURAS.get(tamanho, self.LARGURAS["pequeno"]))
        altura = 82
        self.image = pygame.Surface((self.largura, altura)).convert()
        self.image.fill(CHAVE_TRANSPARENCIA_SPRITES)
        self.image.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
        w = self.largura
        mid = w // 2

        if cenario == "deserto":
            # Areia quebrada no topo e camadas ocre/vermelhas nas paredes.
            contorno = (93, 57, 31)
            aro_sombra = (122, 77, 39)
            aro_luz = (241, 190, 103)
            parede = (127, 78, 43)
            parede_luz = (174, 113, 58)
            fenda = (61, 42, 31)
            fundo = (43, 35, 31)
            detalhe = (218, 157, 78)
        elif cenario == "neve":
            # Crosta de neve irregular envolvendo uma fenda de rocha/gelada.
            contorno = (37, 57, 75)
            aro_sombra = (72, 101, 125)
            aro_luz = (238, 249, 255)
            parede = (54, 82, 107)
            parede_luz = (117, 156, 184)
            fenda = (31, 47, 66)
            fundo = (19, 31, 49)
            detalhe = (189, 222, 242)
        else:
            # Asfalto rachado, terra exposta e pequenas raizes na borda.
            contorno = (22, 25, 31)
            aro_sombra = (52, 56, 61)
            aro_luz = (112, 139, 78)
            parede = (103, 66, 48)
            parede_luz = (146, 94, 64)
            fenda = (52, 40, 38)
            fundo = (31, 30, 38)
            detalhe = (180, 121, 79)

        # A boca tem recortes e assimetria. As bordas inferiores convergem para
        # o centro, criando uma leitura de profundidade em vez de um retangulo preto.
        silhueta = [
            (1, 9), (w // 8, 5), (w // 4, 7), (w // 3, 3),
            (mid - 5, 6), (mid + w // 5, 3), (w - w // 5, 6),
            (w - 8, 4), (w - 1, 10), (w - 4, 20), (w - 10, 31),
            (mid + max(7, w // 5), 51), (mid + max(4, w // 7), 75),
            (mid - max(4, w // 7), 75), (mid - max(7, w // 5), 51),
            (10, 31), (4, 20)
        ]
        pygame.draw.polygon(self.image, contorno, silhueta)

        aro = [
            (3, 9), (w // 8 + 2, 7), (w // 4, 9), (w // 3, 6),
            (mid - 3, 8), (mid + w // 5 - 2, 6), (w - w // 5, 8),
            (w - 7, 7), (w - 3, 11), (w - 7, 19), (w - 13, 30),
            (mid + max(5, w // 5 - 2), 50), (mid + max(3, w // 7 - 2), 72),
            (mid - max(3, w // 7 - 2), 72), (mid - max(5, w // 5 - 2), 50),
            (13, 30), (7, 19)
        ]
        pygame.draw.polygon(self.image, aro_sombra, aro)

        # Faixas da parede interna, ligeiramente assimetricas.
        parede_pts = [
            (6, 12), (w // 5, 13), (w // 3, 11), (w - w // 4, 12),
            (w - 7, 12), (w - 14, 29), (mid + max(4, w // 6), 49),
            (mid + max(2, w // 9), 69), (mid - max(2, w // 9), 69),
            (mid - max(4, w // 6), 49), (14, 29)
        ]
        pygame.draw.polygon(self.image, parede, parede_pts)

        # Faces iluminadas nas laterais dão a sensação de um buraco que desce.
        pygame.draw.polygon(self.image, parede_luz, [
            (7, 13), (w // 4, 14), (mid - max(5, w // 7), 42),
            (mid - max(2, w // 10), 67), (mid - max(6, w // 5), 52), (13, 29)
        ])
        pygame.draw.polygon(self.image, fenda, [
            (w - 9, 13), (w - w // 4, 14), (mid + max(5, w // 7), 42),
            (mid + max(2, w // 10), 67), (mid + max(6, w // 5), 52), (w - 13, 29)
        ])

        cavidade = [
            (12, 17), (w // 4, 18), (mid, 19), (w - w // 4, 18),
            (w - 12, 17), (w - 17, 31), (mid + max(5, w // 7), 49),
            (mid + max(2, w // 12), 68), (mid - max(2, w // 12), 68),
            (mid - max(5, w // 7), 49), (17, 31)
        ]
        pygame.draw.polygon(self.image, fenda, cavidade)
        fundo_pts = [
            (mid - max(3, w // 8), 55), (mid + max(3, w // 8), 55),
            (mid + max(2, w // 12), 68), (mid - max(2, w // 12), 68)
        ]
        pygame.draw.polygon(self.image, fundo, fundo_pts)

        # Estratos pixelados e fragmentos nas paredes: nunca se usa preto puro.
        for idx, y in enumerate((30, 39, 48, 57)):
            margem = max(10, w // 5 + idx * 2)
            cor_estrato = parede_luz if idx % 2 == 0 else contorno
            if margem < mid - 4:
                pygame.draw.line(self.image, cor_estrato,
                                 (margem, y), (max(margem, mid - 9 - idx), y + 2), 2)
                pygame.draw.line(self.image, contorno,
                                 (min(w - margem, mid + 8 + idx), y + 3), (w - margem, y + 1), 2)

        # Boca superior irregular com reflexos curtos, rachaduras e material do bioma.
        pygame.draw.line(self.image, aro_luz, (5, 8), (max(8, w // 4), 8), 2)
        pygame.draw.line(self.image, aro_luz, (w // 2 + 5, 7), (w - 12, 8), 1)
        pygame.draw.line(self.image, contorno, (8, 12), (12, 17), 2)
        pygame.draw.line(self.image, contorno, (w - 9, 12), (w - 14, 18), 2)
        pygame.draw.rect(self.image, detalhe, (w // 4, 10, max(2, w // 12), 2))
        pygame.draw.rect(self.image, detalhe, (w - w // 3, 11, max(2, w // 14), 1))

        # Pedaços de terra, grama ou gelo desprendidos na borda, determinísticos por buraco.
        rng = random.Random((w * 31) + (7 if cenario == "cidade" else 13 if cenario == "deserto" else 19))
        for _ in range(max(3, w // 18)):
            px = rng.choice((rng.randint(3, max(4, w // 6)), rng.randint(max(3, w - w // 6), w - 4)))
            py = rng.randint(3, 12)
            tam = rng.choice((1, 2, 3))
            pygame.draw.rect(self.image, detalhe, (px, py, tam, 1))
        if cenario == "cidade":
            # Alguns tufos curtos permanecem apenas na borda superior do terreno.
            pygame.draw.line(self.image, (44, 119, 43), (8, 6), (6, 2), 2)
            pygame.draw.line(self.image, (71, 158, 57), (11, 7), (13, 3), 2)
            pygame.draw.line(self.image, (44, 119, 43), (w - 8, 6), (w - 6, 2), 2)
        elif cenario == "neve":
            pygame.draw.rect(self.image, (255, 255, 255), (5, 5, 6, 2))
            pygame.draw.rect(self.image, (220, 241, 252), (w - 12, 6, 7, 2))

        # Desenha a borda próxima por último para separar claramente terreno e queda.
        pygame.draw.line(self.image, contorno, (2, 10), (5, 18), 2)
        pygame.draw.line(self.image, aro_luz, (5, 9), (max(8, w // 5), 10), 1)

        self.rect = self.image.get_rect()
        self.rect.x = int(x_pos)
        # Desloca só alguns pixels para cima para que a borda se sobreponha à superfície
        # do terreno. A largura do rect permanece a mesma, sem alterar a área horizontal.
        self.rect.y = ALTURA_VIRTUAL - 75
        self._posicao_mundo_x = float(x_pos)

    def update(self, velocidade_jogo):
        # Base no solo + deslocamento comum de câmera: nenhuma deriva horizontal.
        self._posicao_mundo_x -= max(0.0, float(velocidade_jogo))
        self.rect.x = int(math.floor(self._posicao_mundo_x))
        if self.rect.right < -10:
            self.kill()

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
        self._posicao_mundo_x = float(x_pos)
        self.desenhar_grupo_cactos()

    def desenhar_grupo_cactos(self):
        # Visual mais polido: base sombreada, volume, flores e espinhos suaves.
        for idx, (rel_x, w, h) in enumerate(self.cactos_info):
            y_offset = self.altura - h
            tronco_w = max(12, w // 2)
            tronco_x = rel_x + (w - tronco_w) // 2
            base_cor = (35, 83, 41)
            brilho_cor = (114, 192, 92)
            meio_cor = (65, 151, 61)
            sombra_cor = (38, 110, 46)
            sombra_forte = (24, 79, 34)
            espinho_cor = (230, 242, 193)

            pygame.draw.ellipse(self.image, (23, 68, 33), (rel_x + 1, self.altura - 8, max(10, w - 1), 8))
            pygame.draw.ellipse(self.image, (77, 116, 52), (rel_x + 3, self.altura - 6, max(8, w - 5), 5))
            pygame.draw.ellipse(self.image, (107, 155, 74), (rel_x + 7, self.altura - 5, max(7, w - 14), 3))

            pygame.draw.rect(self.image, base_cor, (tronco_x - 1, y_offset, tronco_w + 2, h),
                             border_top_left_radius=tronco_w // 2, border_top_right_radius=tronco_w // 2)
            pygame.draw.rect(self.image, meio_cor, (tronco_x, y_offset + 1, tronco_w, h - 1),
                             border_top_left_radius=max(4, tronco_w // 2 - 1), border_top_right_radius=max(4, tronco_w // 2 - 1))
            pygame.draw.rect(self.image, sombra_cor,
                             (tronco_x + max(2, tronco_w // 2), y_offset + 2,
                              max(2, tronco_w - max(2, tronco_w // 2)), max(1, h - 3)),
                             border_top_right_radius=max(2, tronco_w // 4))
            pygame.draw.line(self.image, brilho_cor, (tronco_x + 3, y_offset + 6),
                             (tronco_x + 3, y_offset + h - 8), 2)
            pygame.draw.line(self.image, sombra_forte, (tronco_x + tronco_w - 3, y_offset + 7),
                             (tronco_x + tronco_w - 3, y_offset + h - 8), 1)

            if h > 50:
                arm_y = y_offset + int(h * 0.42)
                arm_alt = 8
                pygame.draw.rect(self.image, base_cor, (rel_x, arm_y, tronco_x - rel_x + 2, arm_alt), border_top_left_radius=4)
                pygame.draw.rect(self.image, meio_cor, (rel_x + 1, arm_y + 1, max(6, tronco_x - rel_x), arm_alt - 1), border_top_left_radius=4)
                pygame.draw.rect(self.image, meio_cor, (rel_x + 1, arm_y - 13, 7, 16), border_top_left_radius=4, border_top_right_radius=4)
                pygame.draw.line(self.image, brilho_cor, (rel_x + 2, arm_y - 10), (rel_x + 2, arm_y + 4), 1)

                arm_y2 = y_offset + int(h * 0.24)
                right_x = tronco_x + tronco_w
                braco_w = max(7, rel_x + w - right_x)
                pygame.draw.rect(self.image, base_cor, (right_x - 1, arm_y2, braco_w + 1, arm_alt), border_top_right_radius=4)
                pygame.draw.rect(self.image, meio_cor, (right_x, arm_y2 + 1, braco_w, arm_alt - 1), border_top_right_radius=4)
                pygame.draw.rect(self.image, meio_cor, (rel_x + w - 8, arm_y2 - 13, 7, 16), border_top_left_radius=4, border_top_right_radius=4)
                pygame.draw.line(self.image, brilho_cor, (rel_x + w - 3, arm_y2 - 10), (rel_x + w - 3, arm_y2 + 4), 1)

            for sy in range(y_offset + 10, y_offset + h - 8, 10):
                pygame.draw.line(self.image, (86, 170, 75), (tronco_x + 2, sy), (tronco_x + tronco_w - 3, sy), 1)
                if (sy // 10 + idx) % 2 == 0:
                    pygame.draw.line(self.image, espinho_cor, (tronco_x - 2, sy + 2), (tronco_x + 1, sy + 1), 1)
                    pygame.draw.line(self.image, espinho_cor, (tronco_x + tronco_w - 1, sy + 5), (tronco_x + tronco_w + 2, sy + 4), 1)

            if h > 60:
                centro_flor = (tronco_x + tronco_w // 2, y_offset + 7)
                petalas = ((-3, 0), (3, 0), (0, -3), (0, 3))
                for dx, dy in petalas:
                    pygame.draw.rect(self.image, (255, 191, 95), (centro_flor[0] + dx - 1, centro_flor[1] + dy - 1, 3, 3))
                pygame.draw.rect(self.image, (255, 234, 146), (centro_flor[0] - 1, centro_flor[1] - 1, 3, 3))
            elif idx % 2 == 0 and h > 48:
                pygame.draw.rect(self.image, (255, 205, 111), (tronco_x + tronco_w // 2 - 1, y_offset + 5, 3, 3))

        self.image = acabamento_legado(self.image, "cacto")

    def update(self, velocidade_jogo):
        # Obstáculo fixo no terreno; apenas a câmera avança pelo mundo.
        self._posicao_mundo_x -= max(0.0, float(velocidade_jogo))
        self.rect.x = int(math.floor(self._posicao_mundo_x))
        if self.rect.x < -150: self.kill()


class ObstaculoVoador(Sprite):
    def __init__(self, x_pos, cenario="cidade"):
        super().__init__()
        self.cenario = cenario
        self.largura = 96
        self.altura = 64
        self.image = pygame.Surface((self.largura, self.altura)).convert()
        self.image.fill(CHAVE_TRANSPARENCIA_SPRITES)
        self.image.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = random.choice([ALTURA_VIRTUAL - 140, ALTURA_VIRTUAL - 190, ALTURA_VIRTUAL - 235])
        self.anim_frame = 0
        self.e_noite = False

    def update(self, velocidade_jogo, e_noite=False, e_slow=False):
        fator_vel = 0.6 if e_slow else 1.25
        self.rect.x -= (velocidade_jogo + fator_vel)
        self.anim_frame += 0.1 if e_slow else 0.22
        self.e_noite = bool(e_noite)
        if self.rect.x < -140:
            self.kill()

    def renderizar_visual(self):
        asa_offset = int(math.sin(self.anim_frame) * 10)
        chave = (self.cenario, self.e_noite, asa_offset)
        imagem = _CACHE_VISUAIS_VOADORES.get(chave)
        if imagem is None:
            imagem = pygame.Surface((self.largura, self.altura)).convert()
            imagem.fill(CHAVE_TRANSPARENCIA_SPRITES)
            imagem.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
            if self.cenario in ("cidade", "cidade_futurista"):
                cor_casco = (80, 108, 152) if self.cenario == "cidade" else (91, 93, 148)
                cor_neon = (108, 236, 248) if not self.e_noite else (178, 246, 255)
                cor_rosa = (245, 118, 224)
                pygame.draw.ellipse(imagem, (40, 48, 71), (18, 28, 55, 14))
                pygame.draw.rect(imagem, cor_casco, (24, 20, 40, 17), border_radius=7)
                pygame.draw.rect(imagem, misturar_cores(cor_casco, BRANCO, 0.35), (29, 16, 28, 11), border_radius=5)
                pygame.draw.rect(imagem, cor_neon, (30, 24, 15, 5), border_radius=2)
                pygame.draw.rect(imagem, cor_rosa, (50, 24, 9, 5), border_radius=2)
                pygame.draw.rect(imagem, cor_neon, (15, 24 + asa_offset // 5, 12, 3), border_radius=2)
                pygame.draw.rect(imagem, cor_neon, (63, 24 - asa_offset // 5, 15, 3), border_radius=2)
                pygame.draw.line(imagem, cor_rosa, (25, 34), (13, 40 + asa_offset // 6), 3)
                pygame.draw.line(imagem, cor_rosa, (61, 34), (77, 40 - asa_offset // 6), 3)
                pygame.draw.circle(imagem, cor_neon, (41, 22), 2)
                pygame.draw.circle(imagem, cor_neon, (54, 22), 2)
            else:
                cor_ptero = (168, 104, 239)
                cor_asa = (126, 73, 212)
                cor_luz = (232, 212, 255)
                cor_bico = (255, 214, 112)
                cor_pe = (94, 54, 115)
                cor_barriga = (210, 181, 250)
                if self.e_noite:
                    pygame.draw.ellipse(imagem, (78, 225, 246), (17, 10, 50, 28))
                pygame.draw.ellipse(imagem, (88, 47, 146), (23, 19, 37, 19))
                pygame.draw.ellipse(imagem, cor_ptero, (23, 17, 34, 19))
                pygame.draw.ellipse(imagem, cor_barriga, (29, 24, 17, 8))
                pygame.draw.polygon(imagem, cor_ptero, [(12, 19), (14, 10), (19, 15), (23, 9), (27, 18)])
                pygame.draw.circle(imagem, cor_ptero, (20, 23), 8)
                pygame.draw.polygon(imagem, cor_bico, [(11, 22), (1, 24), (10, 27), (15, 26)])
                pygame.draw.line(imagem, (232, 188, 88), (4, 24), (10, 24), 1)
                pygame.draw.rect(imagem, (255, 255, 242), (8, 27, 2, 2))
                pygame.draw.rect(imagem, (255, 255, 242), (12, 27, 2, 2))
                pygame.draw.polygon(imagem, (90, 54, 153), [(36, 24), (17, 7 + asa_offset), (38, 12 + asa_offset), (59, 6 + asa_offset), (55, 25)])
                pygame.draw.polygon(imagem, cor_asa, [(38, 22), (20, 10 + asa_offset), (59, 10 + asa_offset), (49, 22)])
                pygame.draw.polygon(imagem, cor_luz, [(38, 22), (24, 12 + asa_offset), (45, 18), (54, 12 + asa_offset)], 1)
                pygame.draw.line(imagem, (197, 146, 255), (35, 21), (28, 13 + asa_offset), 1)
                pygame.draw.line(imagem, (197, 146, 255), (41, 20), (42, 12 + asa_offset), 1)
                pygame.draw.polygon(imagem, (152, 92, 224), [(35, 26), (16, 18 + asa_offset // 2), (42, 17 + asa_offset // 2), (46, 25)])
                pygame.draw.polygon(imagem, cor_ptero, [(54, 24), (76, 19), (61, 31)])
                pygame.draw.polygon(imagem, cor_asa, [(60, 23), (74, 20), (63, 27)])
                pygame.draw.ellipse(imagem, cor_luz, (27, 18, 14, 6))
                pygame.draw.circle(imagem, (255, 156, 206), (29, 27), 2)
                pygame.draw.circle(imagem, (255, 156, 206), (45, 27), 2)
                pygame.draw.line(imagem, cor_pe, (34, 33), (32, 40), 2)
                pygame.draw.line(imagem, cor_pe, (43, 33), (45, 40), 2)
                pygame.draw.line(imagem, cor_pe, (31, 40), (35, 40), 1)
                pygame.draw.line(imagem, cor_pe, (44, 40), (48, 40), 1)
                cor_olho = AMARELO_NEON if self.e_noite else PRETO
                pygame.draw.circle(imagem, cor_olho, (18, 22), 2)
                pygame.draw.circle(imagem, BRANCO, (19, 21), 1)
                pygame.draw.rect(imagem, (255, 166, 209), (13, 27, 3, 2))
                pygame.draw.line(imagem, (208, 159, 250), (54, 25), (67, 22), 1)
            imagem = acabamento_legado(imagem, "voador")
            _CACHE_VISUAIS_VOADORES[chave] = imagem
        self.image = imagem



class ObstaculoPulaPula(Sprite):
    def __init__(self, x_pos):
        super().__init__()
        self.image = pygame.Surface((35, 35)).convert()
        self.image.fill(CHAVE_TRANSPARENCIA_SPRITES)
        self.image.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
        pygame.draw.ellipse(self.image, (54, 30, 82), (2, 25, 31, 8))
        pygame.draw.rect(self.image, (110, 62, 170), (14, 12, 7, 15), border_radius=2)
        for yy in range(13, 25, 4):
            pygame.draw.line(self.image, (231, 214, 255), (14, yy), (20, yy + 2), 1)
        pygame.draw.ellipse(self.image, (180, 103, 245), (4, 5, 27, 15))
        pygame.draw.ellipse(self.image, (236, 208, 255), (7, 7, 20, 9))
        pygame.draw.ellipse(self.image, (255, 236, 173), (12, 10, 6, 4))
        # Rostinho: olhos expressivos, sardas e sorriso brincalhão.
        pygame.draw.rect(self.image, (56, 37, 98), (10, 12, 2, 3))
        pygame.draw.rect(self.image, (56, 37, 98), (22, 12, 2, 3))
        pygame.draw.rect(self.image, (255, 255, 255), (10, 12, 1, 1))
        pygame.draw.rect(self.image, (255, 255, 255), (22, 12, 1, 1))
        pygame.draw.rect(self.image, (255, 150, 189), (7, 15, 3, 2))
        pygame.draw.rect(self.image, (255, 150, 189), (25, 15, 3, 2))
        pygame.draw.line(self.image, (93, 44, 128), (14, 17), (20, 17), 1)
        self.image = acabamento_legado(self.image, "pulador")
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


class ObstaculoDeBioma(Sprite):
    """Obstaculos decorados por bioma; compartem la colision basica del runner."""
    def __init__(self, x_pos, cenario, tipo):
        super().__init__()
        self.cenario = cenario
        self.tipo = tipo
        self.qtd_cactos = 0  # no cuenta para la mision exclusiva de cactos
        self.anim = 0
        self.frames = []
        self._salto_timer = random.randint(70, 150) if tipo == "escorpiao" else 0
        self._salto_fase = 0
        self._salto_base_y = None
        if tipo == "escorpiao":
            self.largura, self.altura = 60, 32
            for fase in range(2):
                img = pygame.Surface((60, 32)).convert()
                img.fill(CHAVE_TRANSPARENCIA_SPRITES)
                img.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
                # Patas articuladas e pinças fofas.
                for i in range(4):
                    off = 2 if ((i + fase) % 2) else -1
                    x = 14 + i * 8
                    pygame.draw.line(img, (84, 46, 40), (x, 22), (x - 4, 28 + off), 2)
                    pygame.draw.line(img, (84, 46, 40), (x + 2, 22), (x + 6, 28 - off), 2)
                pygame.draw.ellipse(img, (95, 45, 39), (10, 13, 34, 12))
                pygame.draw.ellipse(img, (192, 99, 63), (14, 14, 24, 8))
                pygame.draw.circle(img, (250, 226, 170), (18, 18), 4)
                pygame.draw.circle(img, (250, 226, 170), (37, 18), 4)
                pygame.draw.circle(img, PRETO, (18, 18), 2)
                pygame.draw.circle(img, PRETO, (37, 18), 2)
                pygame.draw.rect(img, (255, 255, 255), (17, 16, 2, 2))
                pygame.draw.rect(img, (255, 255, 255), (36, 16, 2, 2))
                pygame.draw.rect(img, (248, 144, 130), (11, 21, 4, 2))
                pygame.draw.rect(img, (248, 144, 130), (42, 21, 4, 2))
                pygame.draw.arc(img, (91, 46, 37), (24, 18, 8, 5),
                                math.pi * 0.12, math.pi * 0.88, 1)
                # Pinças
                pygame.draw.line(img, (97, 49, 41), (12, 18), (5, 14 + fase), 3)
                pygame.draw.line(img, (97, 49, 41), (12, 20), (6, 24 - fase), 3)
                pygame.draw.line(img, (97, 49, 41), (44, 18), (52, 14 + fase), 3)
                pygame.draw.line(img, (97, 49, 41), (44, 20), (52, 24 - fase), 3)
                pygame.draw.circle(img, (224, 112, 69), (5, 14 + fase), 2)
                pygame.draw.circle(img, (224, 112, 69), (6, 24 - fase), 2)
                pygame.draw.circle(img, (224, 112, 69), (52, 14 + fase), 2)
                pygame.draw.circle(img, (224, 112, 69), (52, 24 - fase), 2)
                # Cauda segmentada
                pygame.draw.lines(img, (103, 53, 43), False, [(41, 15), (47, 10), (50, 6), (49, 3), (45, 2)], 3)
                pygame.draw.circle(img, (237, 102, 58), (45, 2), 3)
                # Barriguinha clara
                pygame.draw.ellipse(img, (219, 141, 91), (22, 18, 10, 4))
                self.frames.append(img)
            self.image = self.frames[0]
            self.rect = self.image.get_rect()
            self.rect.bottom = ALTURA_VIRTUAL - 70
        elif tipo == "espinho_gelo":
            self.largura, self.altura = 48, 58
            self.image = pygame.Surface((48, 58)).convert()
            self.image.fill(CHAVE_TRANSPARENCIA_SPRITES)
            self.image.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
            pygame.draw.ellipse(self.image, (105, 145, 173), (2, 48, 44, 8))
            pygame.draw.polygon(self.image, (82, 139, 184), [(2, 56), (10, 31), (17, 42), (24, 6), (31, 37), (39, 24), (46, 56)])
            pygame.draw.polygon(self.image, (192, 232, 252), [(2, 56), (10, 31), (17, 42), (24, 6), (24, 56)])
            pygame.draw.polygon(self.image, (233, 248, 255), [(24, 6), (31, 37), (39, 24), (46, 56), (24, 56)])
            pygame.draw.line(self.image, (255, 255, 255), (24, 9), (18, 35), 2)
            pygame.draw.line(self.image, (220, 241, 252), (28, 18), (35, 30), 1)
            pygame.draw.rect(self.image, (255, 255, 255), (15, 25, 2, 2))
            pygame.draw.rect(self.image, (255, 255, 255), (34, 17, 2, 2))
            self.rect = self.image.get_rect()
            self.rect.bottom = ALTURA_VIRTUAL - 70
        else:  # bola de neve cruzando a pista
            self.largura, self.altura = 40, 36
            self.image = pygame.Surface((40, 36)).convert()
            self.image.fill(CHAVE_TRANSPARENCIA_SPRITES)
            self.image.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
            pygame.draw.ellipse(self.image, (91, 123, 152), (1, 9, 38, 25))
            pygame.draw.circle(self.image, (198, 229, 247), (20, 18), 15)
            pygame.draw.circle(self.image, (246, 251, 255), (15, 12), 7)
            pygame.draw.circle(self.image, (228, 243, 252), (25, 21), 5)
            pygame.draw.arc(self.image, (170, 202, 225), (8, 10, 23, 17),
                            math.radians(210), math.radians(335), 2)
            pygame.draw.circle(self.image, (61, 104, 138), (15, 18), 2)
            pygame.draw.circle(self.image, (61, 104, 138), (24, 18), 2)
            pygame.draw.rect(self.image, (255, 255, 255), (14, 17, 1, 1))
            pygame.draw.rect(self.image, (255, 255, 255), (23, 17, 1, 1))
            pygame.draw.arc(self.image, (61, 104, 138), (17, 19, 6, 5),
                            math.radians(15), math.radians(165), 1)
            pygame.draw.rect(self.image, (255, 255, 255), (11, 14, 2, 2))
            pygame.draw.rect(self.image, (255, 255, 255), (28, 18, 2, 2))
            self.rect = self.image.get_rect()
            self.rect.y = random.choice((ALTURA_VIRTUAL - 245, ALTURA_VIRTUAL - 210, ALTURA_VIRTUAL - 175, ALTURA_VIRTUAL - 140, ALTURA_VIRTUAL - 110))
        if self.frames:
            self.frames = ([acabamento_legado(frame, "escorpiao") for frame in self.frames]
                           if os.environ.get("PIXELRUSH_ARTE_CLASSICA") == "1" else
                           [escorpiao_frame(frame.get_size(), i) for i, frame in enumerate(self.frames)])
            self.image = self.frames[0]
        else:
            self.image = acabamento_legado(self.image, "gelo")
        self.rect.x = x_pos
        self._posicao_mundo_x = float(x_pos)
        self._y_base = self.rect.y
        if tipo == "escorpiao":
            self._salto_base_y = self.rect.y

    def update(self, velocidade_jogo):
        self._posicao_mundo_x -= velocidade_jogo + (0.45 if self.tipo in ("escorpiao", "bola_neve") else 0.0)
        self.rect.x = int(math.floor(self._posicao_mundo_x))
        self.anim += 1
        if self.tipo == "escorpiao" and self.frames:
            self.image = self.frames[(self.anim // 4) % len(self.frames)]
        if self.tipo == "escorpiao":
            self._salto_timer -= 1
            if self._salto_timer <= 0 and self._salto_fase == 0:
                self._salto_fase = 24
                self._salto_timer = random.randint(75, 135)
            if self._salto_fase > 0:
                progresso = (24 - self._salto_fase) / 23.0
                self.rect.y = self._salto_base_y - int(math.sin(progresso * math.pi) * 34)
                self._salto_fase -= 1
            else:
                self.rect.y = self._salto_base_y
        elif self.tipo == "bola_neve":
            self.rect.y = self._y_base + int(math.sin(self.anim * 0.12) * 3)
        if self.rect.right < -60:
            self.kill()


# --- HITBOXES PREMIUM (v3.42.0) ---
# Geometria pré-calculada em coordenadas relativas ao sprite; por frame apenas
# translada retângulos pequenos (sem máscaras, scan de pixels ou superfícies).
def _hitboxes_locais_obstaculo(obs):
    if isinstance(obs, AmeacaBioma) and not obs._colisao_ativa:
        return ()
    areas = getattr(obs, "_hitboxes_precisas_v342", None)
    if areas is not None:
        return areas

    if isinstance(obs, ObstaculoTerrestre):
        # O retângulo do grupo inteiro englobava o espaço vazio acima dos cactos
        # menores. Cada caule e seus braços ganham hitboxes independentes.
        locais = []
        for rel_x, w, h in obs.cactos_info:
            y = obs.altura - h
            tw = max(12, w // 2)
            tx = rel_x + (w - tw) // 2
            locais.append(pygame.Rect(tx + 1, y + 3, max(3, tw - 2), max(3, h - 7)))
            if h > 50:
                arm_left_y = y + int(h * 0.42)
                locais.append(pygame.Rect(rel_x + 3, arm_left_y - 10,
                                          max(3, tx - rel_x - 2), 16))
                arm_right_y = y + int(h * 0.24)
                locais.append(pygame.Rect(tx + tw - 1, arm_right_y - 10,
                                          max(3, rel_x + w - tx - tw - 2), 16))
        areas = tuple(locais)
    elif isinstance(obs, ObstaculoVoador):
        # Asa, crista e cauda são decorativas; colisão no dinossaurinho central.
        areas = (pygame.Rect(18, 18, 50, 24),)
    elif isinstance(obs, ObstaculoPulaPula):
        areas = (pygame.Rect(6, 6, 24, 24),)
    elif isinstance(obs, ObstaculoDeBioma):
        tipo = obs.tipo
        if tipo == "escorpiao":
            areas = (pygame.Rect(10, 10, max(28, obs.rect.width - 18), max(14, obs.rect.height - 18)),)
        elif tipo == "espinho_gelo":
            # Pontas estreitas: retângulo menor que o espaço transparente do PNG.
            areas = (pygame.Rect(14, 14, 22, 39),)
        elif tipo == "bola_neve":
            areas = (pygame.Rect(6, 7, 28, 25),)
        else:
            areas = (pygame.Rect(3, 3, max(1, obs.rect.width - 6),
                                 max(1, obs.rect.height - 6)),)
    else:
        # Segurança caso apareça outro obstáculo em uma futura atualização.
        areas = (pygame.Rect(3, 3, max(1, obs.rect.width - 6),
                             max(1, obs.rect.height - 6)),)
    obs._hitboxes_precisas_v342 = areas
    return areas


def obter_hitboxes_obstaculo(obs):
    """Retângulos de dano em coordenadas da tela (sem custo de rasterização)."""
    ox, oy = obs.rect.topleft
    return tuple(pygame.Rect(ox + area.x, oy + area.y, area.w, area.h)
                 for area in _hitboxes_locais_obstaculo(obs))


def obstaculo_encosta_jogador(hitbox_jogador, obs):
    # Após um corte SDF a geometria E a colisão usam os mesmos pixels.
    sdf_hit = colide_sdf_com_rect(obs, hitbox_jogador)
    if sdf_hit is not None:
        return sdf_hit
    if not hitbox_jogador.colliderect(obs.rect):
        return False
    return any(hitbox_jogador.colliderect(area)
               for area in obter_hitboxes_obstaculo(obs))


def hitbox_disparo_laser(laser):
    # O brilho vermelho da borda não deve matar sem contato com o feixe central.
    return pygame.Rect(laser.rect.left, laser.rect.top + 5,
                       laser.rect.width, max(1, laser.rect.height - 10))



# v3.152: mesmas silhuetas aprovadas, pré-renderizadas em cache para Android.
_CONTORNOS_3152 = ContornosLegiveis(LARGURA_VIRTUAL, ALTURA_VIRTUAL)

def desenhar_silhuetas_perigos(superficie, obstaculos, frame_contador=0, bioma_atual=None):
    _CONTORNOS_3152.desenhar(superficie, obstaculos, frame_contador, bioma_atual)


def desenhar_avisos_obstaculos(superficie, jogador, grupo_obstaculos, frame_contador, leve=False):
    """Avisos de leitura antecipada; nunca mudam spawn, dano ou movimento."""
    if jogador is None or jogador.morrendo:
        return
    inicio = jogador.obter_hitbox().right
    contagem = 0
    for obs in grupo_obstaculos:
        r = obs.rect
        # Avisos antigos continuam com a mesma janela de distância. Somente os
        # veículos/objetos móveis têm sinal mais cedo, incluindo fora da tela.
        if isinstance(obs, ObstaculoMovel) or getattr(obs, '_reflexo_comando', None):
            if not (inicio + 16 < r.left < min(820, inicio + 690)):
                continue
        elif not (inicio + 16 < r.left < min(448, inicio + 210)):
            continue
        if r.bottom < 225 or r.top > ALTURA_VIRTUAL - 68:
            continue
        if getattr(obs, '_reflexo_comando', None):
            cor = (255, 221, 122)
        elif isinstance(obs, ObstaculoMovel):
            # Cor única e dois traços indicam movimento de aproximação.
            cor = (255, 174, 83)
        elif isinstance(obs, ObstaculoVoador):
            # Marca onde o inimigo esta voando e desenha sombra no solo.
            pygame.draw.ellipse(superficie, (50, 70, 105),
                                (r.centerx - 19, ALTURA_VIRTUAL - 86, 38, 7), 1)
            cor = (202, 167, 255)
        elif isinstance(obs, AmeacaBioma) and (obs.movimento in ('parado', 'parado_alto') or obs.codigo == 'V4'):
            # v3.187: reaproveita o aviso triangular ja existente, com a paleta
            # do obstaculo/estado atual; nenhum novo tempo ou marcador.
            cor = cor_aviso_ameaca(obs)
        elif isinstance(obs, ObstaculoDeBioma) and obs.tipo == 'espinho_gelo':
            cor = (160, 233, 255)
        else:
            cor = (255, 216, 109)
        if leve and contagem >= 1:
            break
        x = max(12, min(LARGURA_VIRTUAL - 12, r.centerx))
        y = max(226, min(ALTURA_VIRTUAL - 130, r.top - 16))
        pulso = 1 if frame_contador % 22 < 11 else 0
        pygame.draw.polygon(superficie, (39, 42, 65),
                            ((x, y - 9), (x - 8, y + 6), (x + 8, y + 6)))
        pygame.draw.polygon(superficie, cor,
                            ((x, y - 8), (x - 7, y + 5), (x + 7, y + 5)), 2)
        pygame.draw.line(superficie, cor, (x, y - 3), (x, y + 1 + pulso), 2)
        pygame.draw.circle(superficie, cor, (x, y + 3), 1)
        if isinstance(obs, ObstaculoMovel):
            pygame.draw.line(superficie, cor, (x + 13, y - 4), (x + 9, y), 2)
            pygame.draw.line(superficie, cor, (x + 13, y + 4), (x + 9, y), 2)
        if getattr(obs, '_reflexo_comando', None) is not None:
            # Apenas novas ameacas de reflexo: gesto legivel e compacto.
            rotulos = {'REFLEXO_CURTO': 'PULO', 'REFLEXO_LONGO': 'SEGURE PULO',
                       'REFLEXO_BAIXO': 'ABAIXE'}
            legenda = rotulos[obs._reflexo_comando]
            # A fonte pequena ja e cacheada pelo jogo; nao cria fontes por frame.
            sinal = render_texto_cacheado(fonte_pequena, legenda, (255, 221, 122))
            superficie.blit(sinal, (max(2, min(LARGURA_VIRTUAL - sinal.get_width() - 2,
                                           x - sinal.get_width() // 2)), y - 27))
        contagem += 1
        if contagem >= 3:
            break


def desenhar_hitboxes_debug(superficie, jogador, obstaculos, perigos, frame_contador, buracos=()):
    """F8: traça somente as hitboxes usadas de verdade pelo sistema de dano."""
    if jogador is not None:
        pygame.draw.rect(superficie, (86, 255, 137), jogador.obter_hitbox(), 2)
    for obs in obstaculos:
        for area in obter_hitboxes_obstaculo(obs):
            pygame.draw.rect(superficie, (255, 212, 64), area, 1)
    for perigo in perigos:
        if isinstance(perigo, AvisoLaser) and getattr(perigo, 'ativo', False):
            pygame.draw.rect(superficie, (255, 96, 116), hitbox_disparo_laser(perigo), 2)
    for buraco in buracos:
        # Buracos verificam o centro horizontal do personagem, não um rect de dano.
        pygame.draw.line(superficie, (255, 109, 207),
                         (buraco.rect.left, ALTURA_VIRTUAL - 73),
                         (buraco.rect.right, ALTURA_VIRTUAL - 73), 2)
    pygame.draw.rect(superficie, (12, 20, 34), (260, 12, 127, 23), border_radius=4)
    pygame.draw.rect(superficie, (125, 243, 177), (260, 12, 127, 23), 1, border_radius=4)
    legenda = render_texto_cacheado(fonte_pequena, 'HITBOX  F8', (179, 255, 203))
    superficie.blit(legenda, (268, 15))


def distancia_quadrada_hitboxes(hitbox_jogador, obs):
    """Quase-colisões usam a mesma geometria que pode causar dano."""
    if not hitbox_jogador.colliderect(obs.rect.inflate(36, 36)):
        return float("inf")
    menor = float("inf")
    for area in obter_hitboxes_obstaculo(obs):
        dx = max(area.left - hitbox_jogador.right,
                 hitbox_jogador.left - area.right, 0)
        dy = max(area.top - hitbox_jogador.bottom,
                 hitbox_jogador.top - area.bottom, 0)
        d2 = dx * dx + dy * dy
        if d2 < menor:
            menor = d2
    return menor


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


class BauSecreto(Sprite):
    """Baú raro coletável; não participa da colisão com obstáculos."""
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.image = pygame.Surface((40, 34)).convert()
        self.image.fill(CHAVE_TRANSPARENCIA_SPRITES)
        self.image.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
        pygame.draw.rect(self.image, (104, 54, 25), (2, 10, 36, 22), border_radius=4)
        pygame.draw.rect(self.image, (190, 111, 40), (2, 10, 36, 22), 2, border_radius=4)
        pygame.draw.rect(self.image, (226, 174, 62), (2, 5, 36, 11), border_radius=3)
        pygame.draw.rect(self.image, (255, 221, 104), (2, 5, 36, 11), 2, border_radius=3)
        pygame.draw.rect(self.image, (255, 236, 145), (17, 8, 6, 23))
        pygame.draw.circle(self.image, AMARELO_NEON, (20, 18), 3)
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.anim = 0

    def update(self, velocidade_jogo):
        self.rect.x -= velocidade_jogo
        self.anim += 1
        if self.rect.right < -10:
            self.kill()


portal_proximo_metro = 700


class PortalBonus(Sprite):
    """Portal de fase bônus; desenho procedural leve, sem assets externos."""
    TIPOS = ("INVERTIDO", "FLAPPY", "TUNEL", "AQUATICO", "TESOURO")
    CORES = {"INVERTIDO": (180, 95, 255), "FLAPPY": (80, 235, 155), "TUNEL": (70, 205, 255),
             "AQUATICO": (35, 170, 245), "LASERS": (255, 55, 90), "TESOURO": (255, 205, 65), "REFLEXOS": (190, 90, 255)}

    def __init__(self, x_pos, y_pos, tipo=None):
        super().__init__()
        self.tipo = tipo or random.choice(self.TIPOS)
        self.image = pygame.Surface((94, 132)).convert()
        self.image.fill(CHAVE_TRANSPARENCIA_SPRITES)
        self.image.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
        cor = self.CORES[self.tipo]
        # Portal tipo buraco negro: centro escuro, anéis brilhantes e partículas orbitais.
        pygame.draw.ellipse(self.image, tuple(max(0, c // 4) for c in cor), (3, 2, 88, 126))
        pygame.draw.ellipse(self.image, (2, 3, 15), (13, 12, 68, 108))
        pygame.draw.ellipse(self.image, cor, (7, 6, 80, 118), 5)
        pygame.draw.ellipse(self.image, (230, 250, 255), (17, 16, 60, 98), 2)
        pygame.draw.ellipse(self.image, (0, 0, 0), (24, 23, 46, 84))
        for i in range(12):
            ang = i * math.tau / 12
            px = 47 + int(math.cos(ang) * 39)
            py = 66 + int(math.sin(ang) * 56)
            pygame.draw.circle(self.image, (245, 250, 255) if i % 3 == 0 else cor, (px, py), 2 if i % 2 else 3)
        self.rect = self.image.get_rect(midbottom=(x_pos, y_pos))
        self.anim = 0

    def update(self, velocidade_jogo):
        self.rect.x -= velocidade_jogo
        self.anim += 1
        if self.anim % 5 == 0:
            # Pulso de escala discreto, mantendo custo baixo em aparelhos fracos.
            base = 1.0 + 0.035 * math.sin(self.anim * 0.18)
            largura, altura = int(94 * base), int(132 * base)
            imagem = pygame.Surface((largura, altura)).convert()
            imagem.fill(CHAVE_TRANSPARENCIA_SPRITES)
            imagem.set_colorkey(CHAVE_TRANSPARENCIA_SPRITES)
            cor = self.CORES[self.tipo]
            pygame.draw.ellipse(imagem, tuple(max(0, c // 4) for c in cor), (2, 2, largura-4, altura-4))
            pygame.draw.ellipse(imagem, (2, 3, 15), (largura//7, altura//10, largura*5//7, altura*8//10))
            pygame.draw.ellipse(imagem, cor, (4, 4, largura-8, altura-8), 4)
            pygame.draw.ellipse(imagem, (235, 250, 255), (largura//5, altura//8, largura*3//5, altura*3//4), 2)
            self.image = imagem
            self.rect = self.image.get_rect(center=self.rect.center)
        if self.rect.right < -10:
            self.kill()


# --- SISTEMA DE MISSÕES ---
def gerar_missoes_rodada():
    """Gera 3 missões variadas; alvos equilibrados para corridas curtas e longas."""
    banco_missoes = [
        {"tipo": "MOEDAS", "key": "missao_moedas", "alvo": random.randint(90, 220), "atual": 0, "recompensa": 100, "concluida": False},
        {"tipo": "DISTANCIA", "key": "missao_distancia", "alvo": random.randint(700, 1600), "atual": 0, "recompensa": 180, "concluida": False},
        {"tipo": "QUEBRAR", "key": "missao_quebrar", "alvo": random.randint(8, 18), "atual": 0, "recompensa": 130, "concluida": False},
        {"tipo": "PULOS", "key": "missao_pulos", "alvo": random.randint(25, 70), "atual": 0, "recompensa": 90, "concluida": False},
        {"tipo": "POWERUPS", "key": "missao_powerups", "alvo": random.randint(3, 8), "atual": 0, "recompensa": 120, "concluida": False},
        {"tipo": "SLOW", "key": "missao_slow", "alvo": random.randint(2, 5), "atual": 0, "recompensa": 80, "concluida": False},
        {"tipo": "COMBO", "key": "missao_combo", "alvo": random.choice((12, 18, 25)), "atual": 0, "recompensa": 140, "concluida": False},
        {"tipo": "BAUS", "key": "missao_baus", "alvo": random.choice((1, 2, 3)), "atual": 0, "recompensa": 150, "concluida": False},
        {"tipo": "FEBRE", "key": "missao_febre", "alvo": 1, "atual": 0, "recompensa": 160, "concluida": False},
        {"tipo": "QUASE", "key": "missao_quase", "alvo": random.randint(3, 8), "atual": 0, "recompensa": 120, "concluida": False},
    ]
    # Não sortear missão que depende de power-up ainda bloqueado ou evento
    # suspenso na edição de produção; somente objetivos possíveis para todos.
    banco_missoes = [m for m in banco_missoes
                     if m['tipo'] not in ('QUEBRAR', 'POWERUPS', 'SLOW')]
    return random.sample(banco_missoes, 3)


from pixelrush_moedas_v3245 import PADROES_GEOMETRICOS_3245 as PADROES_GEOMETRICOS_3216, variar_formato
from pixelrush_corredores_v3245 import gerar_corredor

# --- GERADOR DE PADRÕES EXPANDIDO DE MOEDAS (32 FORMATOS) ---
def gerar_padrao_moedas(x_base, y_base, formato, todos_sprites, moedas, pool_manager):
    y_limite_chao = ALTURA_VIRTUAL - 110
    y_limite_topo = ALTURA_VIRTUAL - 250
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
    elif formato == "CORREDOR_GIGANTE":
        for i in range(14):
            offsets.append((i * 26, 0))
    elif formato == "CORREDOR_DUPLO":
        for i in range(14):
            offsets.append((i * 26, 0))
            offsets.append((i * 26, -28))
    elif formato == "JET_ARCO":
        for i in range(12):
            offsets.append((i * 28, -math.sin(i / 11.0 * math.pi) * 34))
    elif formato == "JET_SERPENTE":
        for i in range(12):
            offsets.append((i * 24, math.sin(i * 0.72) * 22))
    elif formato == "JET_ESCADA":
        for i in range(10):
            offsets.append((i * 25, -min(66, i * 8)))

    # v3.216: dados imutaveis, ja calculados ao carregar o modulo.
    # O posicionamento seguro e o pool abaixo continuam os originais.
    if formato in PADROES_GEOMETRICOS_3216:
        offsets = PADROES_GEOMETRICOS_3216[formato]

    if offsets:
        min_dy = min(dy for _, dy in offsets)
        max_dy = max(dy for _, dy in offsets)

        if y_base + min_dy < y_limite_topo:
            y_base = y_limite_topo - min_dy
        if y_base + max_dy > y_limite_chao:
            y_base = y_limite_chao - max_dy

    for dx, dy in offsets:
        px = int(x_base + dx)
        py = int(y_base + dy)
        if y_limite_topo <= py <= y_limite_chao:
            m = pool_manager.obter_moeda(px, py)
            todos_sprites.add(m)
            moedas.add(m)


cooldown_laser = 0


def _criar_obstaculo_base_bioma(x_inicial, cenario, agrupado=False):
    if cenario == "deserto":
        return ObstaculoTerrestre(x_inicial, qtd_cactos=random.randint(2, 4) if agrupado else 1)
    if cenario == "neve":
        if random.random() < 0.35:
            return ObstaculoDeBioma(x_inicial, cenario, "espinho_gelo")
        return AmeacaBioma(x_inicial, random.choice(("N3", "N4")))
    if cenario == "cidade":
        return AmeacaBioma(x_inicial, random.choice(("C3", "C4", "C1" if agrupado else "C3")))
    if cenario == "vulcao":
        return AmeacaBioma(x_inicial, random.choice(("V1", "V3", "V4" if agrupado else "V3")))
    if cenario == "floresta":
        return AmeacaBioma(x_inicial, random.choice(("F1", "F3", "F4" if agrupado else "F3")))
    if cenario == "cidade_futurista":
        return AmeacaBioma(x_inicial, random.choice(("CF1", "CF3", "CF4" if agrupado else "CF3")))
    if cenario == "ilhas_celestes":
        return AmeacaBioma(x_inicial, random.choice(("IC1", "IC3", "IC4" if agrupado else "IC3")))
    return ObstaculoTerrestre(x_inicial, qtd_cactos=1)


def gerar_padrao(todos_sprites, obstaculos, perigos_especiais, moedas, powerups, metros, pool_manager,
                 cenario="cidade", buracos=None, baus=None, portais=None, dados_jogo=None, diretor=None):
    global cooldown_laser
    if buracos is None:
        buracos = pygame.sprite.Group()
    x_inicial = LARGURA_VIRTUAL + 20

    if cooldown_laser > 0:
        cooldown_laser -= 1

    for obs in list(obstaculos) + list(perigos_especiais) + list(buracos):
        if obs.rect.right > LARGURA_VIRTUAL - 140:
            return

    if len(obstaculos) + len(perigos_especiais) + len(buracos) >= 2:
        return

    # v3.131: encontros legíveis; um único perigo por evento e o mesmo
    # espaçamento já validado da v3.124. Sem combinar saltos às cegas.
    sequencia = diretor.proxima(metros, cenario) if diretor is not None else None
    rota_bioma = getattr(diretor, "rota_atual", None)
    # As novas sequências mantêm uma chance independente de power-up,
    # sem contornar a compra obrigatória de nível 1. O gerador clássico
    # segue com seu próprio sorteio inalterado no restante da função.
    if sequencia is not None and random.random() < 0.060:
        desbloqueados = [tipo for tipo in UPGRADES_CONFIG
                         if powerup_desbloqueado(dados_jogo, tipo)]
        if desbloqueados:
            pesos = {'JETPACK': 1.4, 'CLONE': .75, 'PRISMA': .65,
                     'CRONO': .75, 'TURBO_FANTASMA': .55}
            escolhido = random.choices(
                desbloqueados, weights=[pesos.get(tipo, 1.0) for tipo in desbloqueados], k=1)[0]
            p = PowerUp(x_inicial + 175,
                        random.choice((ALTURA_VIRTUAL - 140, ALTURA_VIRTUAL - 200,
                                       ALTURA_VIRTUAL - 225)), escolhido)
            todos_sprites.add(p)
            powerups.add(p)
    if sequencia == 'DESCANSO':
        gerar_padrao_moedas(x_inicial + 55, ALTURA_VIRTUAL - 144,
                            formato_aberto(rota_bioma, descanso=True), todos_sprites, moedas, pool_manager)
        return True  # A pausa também consome o espaçamento, evitando chuva de moedas.
    if sequencia == 'TRILHA':
        # Passagem aberta com moedas escalonadas: ritmo sem perigo adicional.
        gerar_padrao_moedas(x_inicial + 55, ALTURA_VIRTUAL - 157,
                            formato_aberto(rota_bioma), todos_sprites, moedas, pool_manager)
        return True
    # v3.223: tres gestos encadeados em encontros de acao JA aprovados pelo
    # diretor original. Mesmo grupo, mesmo timer e uma unica ameaca por passo.
    if sequencia in ('REFLEXO_CURTO', 'REFLEXO_LONGO', 'REFLEXO_BAIXO'):
        # Mesmo criterio de antecipacao dos moveis v3.222, com folga para
        # o vento rapido e sem acelerar fisica, gerador ou controles.
        velocidade_teorica = min(16.0, 6.0 + max(0, metros) * 0.0018)
        distancia_reacao = (velocidade_teorica * 1.08 + 0.8) * 38
        x_reflexo = max(x_inicial, int(115 + distancia_reacao))
        obs = criar_reflexo(sequencia, cenario, x_reflexo, ObstaculoVoador,
                            ALTURA_VIRTUAL)
        todos_sprites.add(obs)
        obstaculos.add(obs)
        premiar_pos_perigo(rota_bioma, obs, ALTURA_VIRTUAL, todos_sprites, moedas, pool_manager)
        return True
    # v3.222: substitui ocasionalmente UM encontro existente, nunca acrescenta
    # spawn paralelo. O diretor, a distância e a auditoria antigos permanecem donos
    # do ritmo. Entra somente após o primeiro setor de aprendizagem (850 m).
    tipo_movel = (escolher_movel(cenario, sequencia, metros, random)
                  if OBSTACULOS_QUE_AVANCAM_ATIVOS_PROD else None)
    if tipo_movel is not None:
        # Garantia de >= 35 ticks de viagem até o jogador em velocidade normal
        # (a forma final de Febre/Turbo preserva a invencibilidade preexistente).
        velocidade_teorica = min(16.0, 6.0 + max(0, metros) * 0.0018)
        adicional = max(0, int((velocidade_teorica + 1.8) * 36 - (x_inicial - 115)))
        obs = ObstaculoMovel(x_inicial + adicional, tipo_movel)
        todos_sprites.add(obs)
        obstaculos.add(obs)
        premiar_pos_perigo(rota_bioma, obs, ALTURA_VIRTUAL, todos_sprites, moedas, pool_manager)
        return True
    if sequencia == 'SALTO':
        obs = _criar_obstaculo_base_bioma(x_inicial, cenario, agrupado=False)
        todos_sprites.add(obs)
        obstaculos.add(obs)
        if metros >= 500:
            gerar_corredor('SALTO', obs, ALTURA_VIRTUAL, metros, cenario,
                           todos_sprites, moedas, pool_manager)
        else:
            gerar_padrao_moedas(x_inicial + 6, ALTURA_VIRTUAL - 175, 'ARCO',
                                todos_sprites, moedas, pool_manager)
        return True
    if sequencia == 'ESCOLHA':
        # Passar por baixo é seguro; uma trajetória aérea dá mais moedas.
        obs = ObstaculoVoador(x_inicial, cenario)
        obs.rect.y = ALTURA_VIRTUAL - 235
        todos_sprites.add(obs)
        obstaculos.add(obs)
        if metros >= 500:
            gerar_corredor('ESCOLHA', obs, ALTURA_VIRTUAL, metros, cenario,
                           todos_sprites, moedas, pool_manager)
        else:
            gerar_padrao_moedas(x_inicial + 105, ALTURA_VIRTUAL - 213, 'ESCADA',
                                todos_sprites, moedas, pool_manager)
        return True
    if sequencia == 'PASSAGEM':
        # Sobre a hitbox do agachamento e dentro da área do jogador em pé.
        # A física e a caixa de colisão atuais permanecem inalteradas.
        obs = ObstaculoVoador(x_inicial, cenario)
        obs.rect.y = ALTURA_VIRTUAL - 157
        todos_sprites.add(obs)
        obstaculos.add(obs)
        if metros >= 500:
            gerar_corredor('PASSAGEM', obs, ALTURA_VIRTUAL, metros, cenario,
                           todos_sprites, moedas, pool_manager)
        else:
            gerar_padrao_moedas(x_inicial + 133, ALTURA_VIRTUAL - 128, 'PAR_HORIZONTAL',
                                todos_sprites, moedas, pool_manager)
        return True

    # v3.124: padrões triplos removidos para assegurar distância de reação.
    if metros >= 700 and random.random() < 0.030:
        obs = _criar_obstaculo_base_bioma(x_inicial, cenario, agrupado=True)
        todos_sprites.add(obs)
        obstaculos.add(obs)
        gerar_padrao_moedas(x_inicial - 4, ALTURA_VIRTUAL - 220, "JET_ARCO", todos_sprites, moedas, pool_manager)
        gerar_padrao_moedas(x_inicial + 120, ALTURA_VIRTUAL - 150, "CORREDOR_GIGANTE", todos_sprites, moedas, pool_manager)
        return

    if metros >= 350 and random.random() < 0.070:
        obs = _criar_obstaculo_base_bioma(x_inicial, cenario, agrupado=random.random() < 0.45)
        todos_sprites.add(obs)
        obstaculos.add(obs)
        y_rota = ALTURA_VIRTUAL - random.choice((185, 200, 220))
        gerar_padrao_moedas(x_inicial - 6, y_rota, random.choice(("ARCO", "V", "ESCADA", "CORREDOR_DUPLO")),
                            todos_sprites, moedas, pool_manager)
        gerar_padrao_moedas(x_inicial + 135, ALTURA_VIRTUAL - 145, random.choice(("DIAGONAL_DESCENDO", "JET_SERPENTE")),
                            todos_sprites, moedas, pool_manager)
        return

    if LASERS_JETPACK_ATIVOS_PROD and metros >= 600 and cooldown_laser <= 0 and cenario in ("cidade", "cidade_futurista") and random.random() < 0.10:
        faixa_y = random.choice([ALTURA_VIRTUAL - 110, ALTURA_VIRTUAL - 160])
        laser = AvisoLaser(faixa_y, delay_warning=150)
        todos_sprites.add(laser)
        perigos_especiais.add(laser)
        cooldown_laser = 14
        return

    obstaculo_chao_proximo = any(abs(obs.rect.centerx - x_inicial) < 300 for obs in obstaculos)
    buraco_proximo = any(abs(b.rect.centerx - x_inicial) < 360 for b in buracos)
    if cenario == "deserto" and metros >= 120 and random.random() < 0.18 and not obstaculo_chao_proximo and not buraco_proximo:
        tamanho_buraco = random.choices(("pequeno", "medio", "grande"), weights=(4, 4, 2), k=1)[0]
        buraco = Buraco(x_inicial, cenario, tamanho_buraco)
        zona_buraco = pygame.Rect(x_inicial - 35, ALTURA_VIRTUAL - 190, buraco.largura + 70, 190)
        if not any(zona_buraco.colliderect(obs.rect) for obs in obstaculos):
            buracos.add(buraco)
            if random.random() < 0.58:
                qtd = max(5, min(11, buraco.largura // 18 + 4))
                span = buraco.largura + 42
                inicio = x_inicial - 18
                y_base = ALTURA_VIRTUAL - 150
                for idx in range(qtd):
                    proporcao = idx / float(max(1, qtd - 1))
                    x_moeda = inicio + int(span * proporcao)
                    y_moeda = int(y_base - math.sin(math.pi * proporcao) * 46)
                    moeda_arco = pool_manager.obter_moeda(x_moeda, y_moeda)
                    todos_sprites.add(moeda_arco)
                    moedas.add(moeda_arco)
            return

    opcoes = []
    def add(tipo, peso):
        opcoes.append((tipo, peso))

    add("normal", 5.0)
    if metros >= 200:
        add("agrupado_colado", 0.55)
        add("voador", 0.9 if cenario not in ("cidade", "cidade_futurista") else 1.1)
    if metros >= 600:
        add("pulador", 0.7 if cenario not in ("cidade_futurista", "ilhas_celestes") else 0.55)
    if cenario == "cidade":
        add("hidrante_cidade", 0.55)  # v3.276: obstáculo novo exclusivo da Cidade
    if cenario == "deserto":
        add("escorpiao", 1.4)
    elif cenario == "neve":
        add("espinho_gelo", 1.25)
        add("bola_neve", 0.95)
    elif cenario == "ilhas_celestes":
        add("voador", 1.3)
        add("pulador", 0.85)

    if metros >= 150:
        for codigo in POR_BIOMA.get(cenario, ()):
            peso = 1.05
            if codigo.endswith('2') or codigo.endswith('4'):
                peso = 0.75
            if codigo in ('CF2', 'IC2', 'F2', 'N2', 'V2', 'C2'):
                peso = 0.65
            if codigo in ('C3', 'C4', 'CF3', 'N3', 'N4', 'V3', 'F3', 'IC3', 'D3', 'D4'):
                peso = 1.15
            add(codigo, peso)

    tipo_obs = random.choices([t for t,_ in opcoes], weights=[p for _,p in opcoes], k=1)[0]

    if tipo_obs in AMEACAS:
        obs = AmeacaBioma(x_inicial, tipo_obs)
        todos_sprites.add(obs)
        obstaculos.add(obs)
    elif tipo_obs in ("escorpiao", "espinho_gelo", "bola_neve"):
        obs = ObstaculoDeBioma(x_inicial, cenario, tipo_obs)
        todos_sprites.add(obs)
        obstaculos.add(obs)
    elif tipo_obs == "voador":
        obs = ObstaculoVoador(x_inicial, cenario)
        todos_sprites.add(obs)
        obstaculos.add(obs)
    elif tipo_obs == "hidrante_cidade" and cenario == "cidade":
        obs = HidranteCidade(x_inicial)
        todos_sprites.add(obs)
        obstaculos.add(obs)
    elif tipo_obs == "pulador":
        obs = ObstaculoPulaPula(x_inicial)
        todos_sprites.add(obs)
        obstaculos.add(obs)
    elif tipo_obs == "agrupado_colado":
        obs = _criar_obstaculo_base_bioma(x_inicial, cenario, agrupado=True)
        todos_sprites.add(obs)
        obstaculos.add(obs)
    else:
        obs = _criar_obstaculo_base_bioma(x_inicial, cenario, agrupado=False)
        todos_sprites.add(obs)
        obstaculos.add(obs)

    if random.random() < 0.060:
        tipos_powerup = [tipo for tipo in UPGRADES_CONFIG if powerup_desbloqueado(dados_jogo, tipo)]
        pesos_powerup = {"IMA": 1.0, "TURBO": 1.0, "ESCUDO": 1.0, "MULT_2X": 1.0,
                         "SLOW": 1.0, "JETPACK": 1.4, "CLONE": 0.75, "PRISMA": 0.65, "CRONO": 0.75, "TURBO_FANTASMA": 0.55}
        if tipos_powerup:
            tipo_powerup = random.choices(tipos_powerup, weights=[pesos_powerup.get(tipo, 1.0) for tipo in tipos_powerup], k=1)[0]
            p = PowerUp(x_inicial + 160, random.choice([ALTURA_VIRTUAL - 140, ALTURA_VIRTUAL - 200, ALTURA_VIRTUAL - 225]), tipo_powerup)
            todos_sprites.add(p)
            powerups.add(p)

    formato_moeda = random.choice([
        "MOEDA_UNICA", "PAR_HORIZONTAL", "PAR_VERTICAL", "TRIO_HORIZONTAL", "TRIO_VERTICAL",
        "DIAGONAL_SUBINDO", "DIAGONAL_DESCENDO", "SMILEY", "LINHA", "V", "V_INVERTIDO",
        "ESCADA", "ESCADA_DESCENDENTE", "QUADRADO", "QUADRADO_PEQUENO", "ARCO", "CIRCULO",
        "DIAMANTE", "ONDA", "COLUNA", "COLUNA_DUPLA", "TRIANGULO", "ZIGZAG", "MEGACRUZ",
        "MEGAGRID_4X3", "MEGASERPENTE", "CHUVA_DE_MOEDAS", "PIRAMIDE_GIGANTE", "MEGA_ANEL",
        "MATRIZ_DENSA", "ONDA_DUPLA_GIGANTE", "X_GIGANTE", "CORREDOR_GIGANTE", "CORREDOR_DUPLO",
        "JET_ARCO", "JET_SERPENTE", "JET_ESCADA",
        "HELICE_DUPLA", "OITO_DUPLO", "RAMPA_MERGULHO", "TUNEL_COLETA",
        "PONTE_INTERROMPIDA", "ONDA_TRIPLA", "ESPIRAL_ACHATADA", "LOSANGOS_ENCADEADOS"
    ])
    formato_moeda = variar_formato(formato_moeda, metros, cenario)
    y_moeda = random.choice([ALTURA_VIRTUAL - 125, ALTURA_VIRTUAL - 150, ALTURA_VIRTUAL - 180, ALTURA_VIRTUAL - 205, ALTURA_VIRTUAL - 228])
    gerar_padrao_moedas(x_inicial + 180, y_moeda, formato_moeda, todos_sprites, moedas, pool_manager)

    if baus is not None and len(baus) == 0 and metros >= 150 and random.random() < 0.055:
        bau = BauSecreto(x_inicial + 300, ALTURA_VIRTUAL - 112)
        todos_sprites.add(bau)
        baus.add(bau)


# --- LOOP PRINCIPAL (SIMULACAO FIXA 60 HZ + RENDERIZACAO INDEPENDENTE) ---


# =========================
# PETS PREMIUM 4.0 - v3.57.0
# Sistema avançado de animação por partes do corpo.
# Cada pet passa a ser montado por partes independentes (cabeça, corpo,
# pernas/patas, asas, cauda, braços etc.) com quadros cacheados.
# =========================

_PET_ESTADOS_CACHE = {}
_PET_MENU_OCIOSO_CACHE = {}
_PET_PERSONALIDADE_CACHE = {}
_PET_PREVIEW_CACHE = {}
_PET_MINI_CACHE = {}
_PET_CORRIDA_CACHE = {}
_V357_PARTS_CACHE = {}


def _v357_surface(size=(64, 56)):
    return pygame.Surface((int(size[0]), int(size[1])), pygame.SRCALPHA).convert_alpha()


def _v357_rect(s, color, rect, radius=0, border=0):
    pygame.draw.rect(s, color, pygame.Rect(int(rect[0]), int(rect[1]), max(1, int(rect[2])), max(1, int(rect[3]))), int(border), border_radius=max(0, int(radius)))


def _v357_ellipse(s, color, rect, border=0):
    pygame.draw.ellipse(s, color, pygame.Rect(int(rect[0]), int(rect[1]), max(1, int(rect[2])), max(1, int(rect[3]))), int(border))


def _v357_circle(s, color, pos, r, border=0):
    pygame.draw.circle(s, color, (int(pos[0]), int(pos[1])), max(1, int(r)), int(border))


def _v357_poly(s, color, pts, border=0):
    pygame.draw.polygon(s, color, [(int(x), int(y)) for x, y in pts], int(border))


def _v357_line(s, color, a, b, w=1):
    pygame.draw.line(s, color, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), max(1, int(w)))


def _v357_blit_center(dest, src, center, angle=0.0, scale=1.0):
    img = pygame.transform.rotozoom(src, float(angle), float(scale))
    dest.blit(img, img.get_rect(center=(int(center[0]), int(center[1]))))


def _v357_shadow(dest, center, size, alpha=60):
    w, h = int(size[0]), int(size[1])
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, int(alpha)), (0, 0, w, h))
    dest.blit(sh, sh.get_rect(center=(int(center[0]), int(center[1]))))


def _v357_mix(a, b, t):
    t = max(0.0, min(1.0, float(t)))
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def _v357_pet_specs():
    return {
        'BOLHA': {'tipo': 'voador', 'nome': 'Bolha', 'body': (103, 214, 255), 'accent': (219, 248, 255), 'detail': (72, 164, 221), 'energy': (199, 247, 255)},
        'RAPOSA': {'tipo': 'terrestre', 'nome': 'Raposa Turbo', 'body': (255, 150, 72), 'accent': (255, 236, 216), 'detail': (209, 97, 44), 'energy': (255, 218, 152)},
        'FANTASMA': {'tipo': 'voador', 'nome': 'Fantasma', 'body': (214, 186, 255), 'accent': (247, 240, 255), 'detail': (159, 120, 228), 'energy': (241, 212, 255)},
        'TARTARUGA': {'tipo': 'terrestre', 'nome': 'Tartaruga Abissal', 'body': (94, 219, 170), 'accent': (205, 255, 232), 'detail': (47, 135, 118), 'energy': (164, 248, 224)},
        'DRAGAO': {'tipo': 'voador', 'nome': 'Dragão Neon', 'body': (255, 110, 165), 'accent': (255, 214, 236), 'detail': (160, 61, 103), 'energy': (255, 173, 224)},
        'GOLEM': {'tipo': 'terrestre', 'nome': 'Golem de Basalto', 'body': (178, 130, 101), 'accent': (224, 203, 176), 'detail': (92, 62, 49), 'energy': (255, 195, 132)},
        'BEIJA_FLOR': {'tipo': 'voador', 'nome': 'Beija-flor Prisma', 'body': (90, 238, 194), 'accent': (210, 255, 241), 'detail': (68, 124, 132), 'energy': (154, 255, 224)},
        'DRAGAO_PLASMA': {'tipo': 'voador', 'nome': 'Dragãozinho de Plasma', 'body': (71, 189, 255), 'accent': (206, 241, 255), 'detail': (67, 108, 220), 'energy': (172, 238, 255)},
        'ABELHA_MAGNETICA': {'tipo': 'voador', 'nome': 'Abelha Magnética', 'body': (255, 209, 76), 'accent': (255, 243, 197), 'detail': (71, 54, 42), 'energy': (255, 232, 122)},
    }







# --- PIXEL RUSH v3.88.0: suporte a sprite sheets aprovadas do Dragão Neon ---
_PET_SHEET_FRAME_CACHE = {}


def _v388_pet_sheet_base_dir():
    try:
        return os.path.join(os.path.dirname(__file__), 'pet_sheet_frames_v3.88')
    except Exception:
        return 'pet_sheet_frames_v3.88'


def _v388_dragon_sheet_clip(state):
    if state == 'CORRER':
        return 'RUN'
    if state in ('IMPULSO', 'SUBINDO', 'APICE', 'CAINDO', 'POUSO', 'HABILIDADE'):
        return 'FLY'
    return 'IDLE'


def _v388_load_pet_sheet_frame(pet_id, clip, frame_number):
    idx = max(1, min(6, int(frame_number)))
    key = (pet_id, clip, idx)
    cached = _PET_SHEET_FRAME_CACHE.get(key)
    if cached is not None:
        return cached
    path = os.path.join(_v388_pet_sheet_base_dir(), pet_id, f'{clip}_{idx}.png')
    if not os.path.exists(path):
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        _PET_SHEET_FRAME_CACHE[key] = img
        return img
    except Exception:
        return None


def _v388_try_pet_sheet_frame(pet_id, state, idx, total):
    if pet_id not in ('DRAGAO', 'DRAGAO_PLASMA'):
        return None
    clip = _v388_dragon_sheet_clip(state)
    total = max(1, int(total))
    frame_number = 1 + int((idx % total) * 6 / total)
    frame = _v388_load_pet_sheet_frame(pet_id, clip, frame_number)
    if frame is None:
        return None
    surf = _v357_surface((64, 56))
    rect = frame.get_rect(center=(32, 29 if clip == 'FLY' else 31))
    surf.blit(frame, rect)
    return surf


def _v357_state_total(state):
    return {
        'CORRER': 20, 'ESPERA': 16, 'SONO': 16, 'FESTA': 16, 'ALERTA': 14,
        'HABILIDADE': 16, 'AGACHAR': 14, 'IMPULSO': 10, 'SUBINDO': 10,
        'APICE': 8, 'CAINDO': 10, 'POUSO': 10, 'CURIOSO': 12, 'ALIVIO': 12,
        'CARINHO': 14, 'BRINCAR': 16, 'MORRER': 16,
    }.get(state, 12)


def _v357_state_profile(state, idx, total, voador=False, ritmo=1.0):
    total = max(1, int(total))
    t = idx / float(total)
    cyc = math.sin(t * math.tau * ritmo)
    cyc2 = math.sin(t * math.tau * ritmo * 2.0)
    p = {
        't': t,
        'cyc': cyc,
        'cyc2': cyc2,
        'bounce': 0.0,
        'tilt': 0.0,
        'head_tilt': 0.0,
        'tail': cyc * 8.0,
        'ear': cyc * 3.0,
        'wing': cyc * 24.0,
        'arm': cyc * 12.0,
        'legA': cyc * 14.0,
        'legB': -cyc * 14.0,
        'blink': idx in (0, total - 1) and state in ('ESPERA', 'SONO'),
        'mood': 'smile',
        'dead': False,
        'scale_y': 1.0,
        'scale_x': 1.0,
        'hover': 0.0,
    }
    if state == 'CORRER':
        p['bounce'] = -abs(cyc) * (2.0 if not voador else 1.0)
        p['tilt'] = cyc * 1.8
    elif state == 'ESPERA':
        p['bounce'] = math.sin(t * math.tau) * 0.8
        p['tilt'] = cyc * 0.8
        p['legA'] = p['legB'] = cyc * 3.0
    elif state == 'SONO':
        p['bounce'] = math.sin(t * math.tau) * 0.35
        p['blink'] = True
        p['mood'] = 'sleep'
        p['legA'] = p['legB'] = 0
        p['wing'] = 0
    elif state == 'FESTA':
        p['bounce'] = math.sin(t * math.tau * 2.0) * 1.9
        p['tilt'] = cyc * 7.0
        p['arm'] = cyc * 24.0
        p['mood'] = 'joy'
    elif state == 'ALERTA':
        p['bounce'] = abs(cyc) * 0.5
        p['head_tilt'] = -4.0
        p['mood'] = 'surprise'
    elif state == 'HABILIDADE':
        p['bounce'] = -abs(cyc2) * 2.0
        p['tail'] = cyc2 * 14.0
        p['wing'] = cyc2 * 30.0
        p['arm'] = cyc2 * 14.0
        p['mood'] = 'power'
    elif state == 'AGACHAR':
        p['bounce'] = 1.5
        p['scale_y'] = 0.88
        p['scale_x'] = 1.08
        p['legA'] = cyc * 9.0
        p['legB'] = -cyc * 9.0
    elif state == 'IMPULSO':
        p['bounce'] = 1.0 - t * 6.0
        p['tilt'] = -8.0
        p['scale_y'] = 0.92
        p['scale_x'] = 1.05
        p['legA'] = p['legB'] = -8.0
        p['tail'] = -10.0
        p['wing'] = -18.0
    elif state == 'SUBINDO':
        p['bounce'] = -3.0 - abs(cyc) * 1.6
        p['tilt'] = -9.0
        p['legA'] = p['legB'] = -6.0
        p['wing'] = -12.0
        p['tail'] = -6.0
    elif state == 'APICE':
        p['bounce'] = -5.0
        p['tilt'] = -2.0
        p['legA'] = p['legB'] = -2.0
        p['wing'] = 0.0
    elif state == 'CAINDO':
        p['bounce'] = -1.0 + abs(cyc) * 1.2
        p['tilt'] = 6.0
        p['legA'] = p['legB'] = 7.0
        p['wing'] = 16.0
        p['tail'] = 8.0
    elif state == 'POUSO':
        p['bounce'] = 2.0 * abs(math.sin(t * math.pi))
        p['scale_y'] = 0.85
        p['scale_x'] = 1.10
        p['legA'] = p['legB'] = 10.0
    elif state == 'CURIOSO':
        p['head_tilt'] = cyc * 7.0
        p['mood'] = 'surprise'
        p['bounce'] = math.sin(t * math.tau) * 0.5
    elif state == 'ALIVIO':
        p['bounce'] = math.sin(t * math.tau) * 0.4
        p['mood'] = 'smile'
    elif state == 'CARINHO':
        p['bounce'] = math.sin(t * math.tau * 1.4) * 0.5
        p['mood'] = 'heart'
        p['tail'] = cyc2 * 12.0
    elif state == 'BRINCAR':
        p['bounce'] = -abs(cyc2) * 2.2
        p['tilt'] = cyc * 10.0
        p['mood'] = 'joy'
    elif state == 'MORRER':
        p['bounce'] = min(5.0, t * 4.5)
        p['tilt'] = 12.0
        p['scale_y'] = max(0.8, 1.0 - t * 0.18)
        p['scale_x'] = 1.0 + t * 0.16
        p['mood'] = 'dead'
        p['dead'] = True
        p['legA'] = p['legB'] = 10.0
        p['wing'] = 8.0
    if voador:
        p['hover'] = math.sin(t * math.tau * ritmo) * 1.6 + p['bounce']
    return p


def _v357_draw_eye(surface, pos, blink=False, dead=False, angry=False):
    x, y = int(pos[0]), int(pos[1])
    if dead:
        _v357_line(surface, (36, 20, 24), (x - 2, y - 2), (x + 2, y + 2), 1)
        _v357_line(surface, (36, 20, 24), (x + 2, y - 2), (x - 2, y + 2), 1)
    elif blink:
        _v357_line(surface, (24, 28, 36), (x - 2, y), (x + 2, y), 1)
    else:
        _v357_circle(surface, (24, 28, 36), (x, y), 2)
        _v357_circle(surface, (255, 255, 255), (x - 1, y - 1), 1)
        if angry:
            _v357_line(surface, (74, 28, 28), (x - 3, y - 3), (x + 1, y - 4), 1)


def _v357_draw_mouth(surface, pos, mood='smile'):
    x, y = int(pos[0]), int(pos[1])
    if mood == 'sleep':
        _v357_line(surface, (22, 24, 32), (x - 2, y), (x + 2, y), 1)
    elif mood == 'surprise':
        _v357_circle(surface, (22, 24, 32), (x, y), 1)
    elif mood == 'dead':
        _v357_line(surface, (92, 50, 50), (x - 2, y + 1), (x + 2, y + 1), 1)
    elif mood in ('joy', 'heart', 'power'):
        _v357_line(surface, (22, 24, 32), (x - 3, y), (x - 1, y + 2), 1)
        _v357_line(surface, (22, 24, 32), (x - 1, y + 2), (x + 1, y + 2), 1)
        _v357_line(surface, (22, 24, 32), (x + 1, y + 2), (x + 3, y), 1)
    else:
        _v357_line(surface, (22, 24, 32), (x - 2, y), (x, y + 1), 1)
        _v357_line(surface, (22, 24, 32), (x, y + 1), (x + 2, y), 1)


def _v357_emit_particles(dest, center, state, color, frame_idx):
    if state not in ('FESTA', 'HABILIDADE', 'CARINHO', 'ALERTA'):
        return
    cx, cy = center
    if state == 'CARINHO':
        for i in range(2):
            px = cx - 8 + i * 16
            py = cy - 15 - ((frame_idx + i * 2) % 3)
            _v357_circle(dest, (255, 146, 183), (px, py), 2)
    else:
        for i in range(3):
            ang = frame_idx * 0.25 + i * 2.1
            px = cx + math.cos(ang) * 14
            py = cy - 2 + math.sin(ang * 1.15) * 9
            _v357_circle(dest, color, (px, py), 2)


def _v357_part_cache(pet_id, name, maker):
    key = (pet_id, name)
    if key not in _V357_PARTS_CACHE:
        _V357_PARTS_CACHE[key] = maker().convert_alpha()
    return _V357_PARTS_CACHE[key]


def _v357_parts_raposa(spec):
    def body():
        s = _v357_surface((26, 16)); _v357_ellipse(s, spec['body'], (1, 2, 24, 12)); _v357_ellipse(s, spec['accent'], (6, 8, 12, 5)); return s
    def head():
        s = _v357_surface((18, 18)); _v357_circle(s, spec['body'], (8, 10), 7); _v357_circle(s, spec['accent'], (10, 12), 4)
        _v357_poly(s, spec['body'], [(2, 8), (4, 0), (8, 6)]); _v357_poly(s, spec['body'], [(9, 6), (13, 0), (15, 8)])
        _v357_poly(s, spec['accent'], [(4, 6), (5, 3), (7, 6)]); _v357_poly(s, spec['accent'], [(10, 6), (12, 3), (13, 6)])
        _v357_draw_eye(s, (6, 10)); _v357_draw_eye(s, (11, 10)); _v357_draw_mouth(s, (11, 14)); _v357_circle(s, spec['detail'], (15, 12), 1); return s
    def tail():
        s = _v357_surface((18, 12)); _v357_poly(s, spec['detail'], [(16, 6), (6, 0), (1, 4), (7, 10)]); _v357_poly(s, spec['body'], [(14, 6), (6, 2), (5, 8)]); return s
    def leg():
        s = _v357_surface((6, 14)); _v357_rect(s, spec['body'], (1, 1, 4, 11), 1); _v357_rect(s, spec['detail'], (0, 11, 6, 2), 1); return s
    return {'body': body(), 'head': head(), 'tail': tail(), 'leg': leg()}


def _v357_parts_tartaruga(spec):
    def shell():
        s = _v357_surface((24, 16)); _v357_ellipse(s, spec['detail'], (1, 1, 22, 14)); _v357_ellipse(s, spec['body'], (4, 4, 16, 8)); return s
    def head():
        s = _v357_surface((12, 10)); _v357_circle(s, spec['body'], (5, 5), 4); _v357_draw_eye(s, (5, 4)); _v357_draw_mouth(s, (8, 7)); return s
    def leg():
        s = _v357_surface((6, 8)); _v357_rect(s, spec['body'], (1, 1, 4, 5), 1); _v357_rect(s, spec['detail'], (0, 5, 6, 2), 1); return s
    def tail():
        s = _v357_surface((8, 6)); _v357_poly(s, spec['body'], [(6, 2), (0, 0), (0, 5)]); return s
    return {'shell': shell(), 'head': head(), 'leg': leg(), 'tail': tail()}


def _v357_parts_golem(spec):
    def torso():
        s = _v357_surface((20, 20)); _v357_rect(s, spec['body'], (2, 4, 16, 13), 2); _v357_rect(s, spec['detail'], (2, 4, 16, 13), 2, 1)
        _v357_line(s, spec['detail'], (6, 7), (10, 10), 1); _v357_line(s, spec['detail'], (10, 10), (8, 14), 1); return s
    def head():
        s = _v357_surface((14, 14)); _v357_rect(s, spec['accent'], (1, 1, 12, 11), 2); _v357_rect(s, spec['detail'], (1, 1, 12, 11), 2, 1)
        _v357_draw_eye(s, (5, 5)); _v357_draw_eye(s, (9, 5)); _v357_draw_mouth(s, (7, 9)); return s
    def limb():
        s = _v357_surface((8, 14)); _v357_rect(s, spec['body'], (2, 1, 4, 10), 1); _v357_rect(s, spec['detail'], (1, 11, 6, 2), 1); return s
    return {'torso': torso(), 'head': head(), 'limb': limb()}


def _v357_parts_dragon(spec):
    def body():
        s = _v357_surface((22, 14)); _v357_ellipse(s, spec['body'], (2, 3, 18, 9)); return s
    def head():
        s = _v357_surface((16, 16)); _v357_circle(s, spec['accent'], (8, 9), 6); _v357_poly(s, spec['body'], [(4, 5), (5, 0), (8, 5)]); _v357_poly(s, spec['body'], [(9, 5), (12, 0), (13, 6)]); _v357_draw_eye(s, (6, 8)); _v357_draw_eye(s, (10, 8)); _v357_draw_mouth(s, (10, 12)); return s
    def wing():
        s = _v357_surface((18, 14)); _v357_poly(s, spec['body'], [(15, 12), (5, 1), (1, 12)]); _v357_poly(s, spec['accent'], [(12, 10), (6, 3), (4, 10)]); return s
    def tail():
        s = _v357_surface((16, 8)); _v357_poly(s, spec['detail'], [(15, 4), (4, 0), (0, 2), (4, 7)]); return s
    def leg():
        s = _v357_surface((6, 10)); _v357_rect(s, spec['body'], (1, 1, 4, 7), 1); _v357_rect(s, spec['detail'], (0, 8, 6, 2), 1); return s
    return {'body': body(), 'head': head(), 'wing': wing(), 'tail': tail(), 'leg': leg()}


def _v357_parts_beijaflor(spec):
    def body():
        s = _v357_surface((16, 10)); _v357_ellipse(s, spec['body'], (3, 2, 10, 6)); return s
    def head():
        s = _v357_surface((14, 8)); _v357_circle(s, spec['accent'], (5, 4), 3); _v357_poly(s, spec['detail'], [(8, 4), (13, 3), (8, 5)]); _v357_draw_eye(s, (5, 4)); return s
    def wing():
        s = _v357_surface((18, 8)); _v357_poly(s, (225, 247, 255), [(16, 4), (2, 0), (0, 4), (2, 8)]); return s
    def tail():
        s = _v357_surface((10, 8)); _v357_poly(s, spec['accent'], [(9, 4), (1, 0), (2, 4), (1, 7)]); return s
    return {'body': body(), 'head': head(), 'wing': wing(), 'tail': tail()}


def _v357_parts_abelha(spec):
    def body():
        s = _v357_surface((18, 12)); _v357_ellipse(s, spec['body'], (2, 2, 14, 8)); _v357_rect(s, spec['detail'], (6, 2, 2, 8)); _v357_rect(s, spec['detail'], (10, 2, 2, 8)); return s
    def head():
        s = _v357_surface((12, 10)); _v357_circle(s, spec['accent'], (5, 5), 4); _v357_draw_eye(s, (4, 4)); _v357_draw_eye(s, (7, 4)); return s
    def wing():
        s = _v357_surface((14, 8)); _v357_poly(s, (225, 245, 255), [(12, 4), (2, 0), (0, 4), (2, 7)]); return s
    def leg():
        s = _v357_surface((8, 8)); _v357_line(s, spec['detail'], (1, 1), (6, 6), 1); return s
    return {'body': body(), 'head': head(), 'wing': wing(), 'leg': leg()}


def _v357_parts_fantasma(spec):
    def body():
        s = _v357_surface((28, 26)); _v357_ellipse(s, spec['body'], (2, 1, 22, 18));
        _v357_poly(s, spec['body'], [(2, 12), (4, 24), (8, 18), (12, 24), (16, 18), (20, 24), (24, 18), (24, 10)])
        _v357_ellipse(s, spec['accent'], (6, 4, 10, 7)); _v357_draw_eye(s, (10, 11)); _v357_draw_eye(s, (16, 11)); _v357_draw_mouth(s, (13, 16)); return s
    def arm():
        s = _v357_surface((8, 12)); _v357_rect(s, spec['body'], (2, 1, 4, 9), 2); return s
    return {'body': body(), 'arm': arm()}


def _v357_parts_bolha(spec):
    def bubble():
        s = _v357_surface((24, 24)); _v357_circle(s, spec['body'], (12, 12), 10); _v357_circle(s, spec['accent'], (8, 8), 5); _v357_circle(s, spec['detail'], (18, 17), 2)
        _v357_draw_eye(s, (9, 11)); _v357_draw_eye(s, (15, 11)); _v357_draw_mouth(s, (12, 16)); return s
    def orb():
        s = _v357_surface((8, 8)); _v357_circle(s, spec['accent'], (4, 4), 3); _v357_circle(s, spec['detail'], (4, 4), 3, 1); return s
    return {'body': bubble(), 'orb': orb()}


def _v357_get_parts(pet_id, spec):
    if pet_id == 'RAPOSA':
        return {
            'body': _v357_part_cache(pet_id, 'body', lambda: _v357_parts_raposa(spec)['body']),
            'head': _v357_part_cache(pet_id, 'head', lambda: _v357_parts_raposa(spec)['head']),
            'tail': _v357_part_cache(pet_id, 'tail', lambda: _v357_parts_raposa(spec)['tail']),
            'leg': _v357_part_cache(pet_id, 'leg', lambda: _v357_parts_raposa(spec)['leg']),
        }
    if pet_id == 'TARTARUGA':
        return {
            'shell': _v357_part_cache(pet_id, 'shell', lambda: _v357_parts_tartaruga(spec)['shell']),
            'head': _v357_part_cache(pet_id, 'head', lambda: _v357_parts_tartaruga(spec)['head']),
            'tail': _v357_part_cache(pet_id, 'tail', lambda: _v357_parts_tartaruga(spec)['tail']),
            'leg': _v357_part_cache(pet_id, 'leg', lambda: _v357_parts_tartaruga(spec)['leg']),
        }
    if pet_id == 'GOLEM':
        return {
            'torso': _v357_part_cache(pet_id, 'torso', lambda: _v357_parts_golem(spec)['torso']),
            'head': _v357_part_cache(pet_id, 'head', lambda: _v357_parts_golem(spec)['head']),
            'limb': _v357_part_cache(pet_id, 'limb', lambda: _v357_parts_golem(spec)['limb']),
        }
    if pet_id in ('DRAGAO', 'DRAGAO_PLASMA'):
        return {
            'body': _v357_part_cache(pet_id, 'body', lambda: _v357_parts_dragon(spec)['body']),
            'head': _v357_part_cache(pet_id, 'head', lambda: _v357_parts_dragon(spec)['head']),
            'wing': _v357_part_cache(pet_id, 'wing', lambda: _v357_parts_dragon(spec)['wing']),
            'tail': _v357_part_cache(pet_id, 'tail', lambda: _v357_parts_dragon(spec)['tail']),
            'leg': _v357_part_cache(pet_id, 'leg', lambda: _v357_parts_dragon(spec)['leg']),
        }
    if pet_id == 'BEIJA_FLOR':
        return {
            'body': _v357_part_cache(pet_id, 'body', lambda: _v357_parts_beijaflor(spec)['body']),
            'head': _v357_part_cache(pet_id, 'head', lambda: _v357_parts_beijaflor(spec)['head']),
            'wing': _v357_part_cache(pet_id, 'wing', lambda: _v357_parts_beijaflor(spec)['wing']),
            'tail': _v357_part_cache(pet_id, 'tail', lambda: _v357_parts_beijaflor(spec)['tail']),
        }
    if pet_id == 'ABELHA_MAGNETICA':
        return {
            'body': _v357_part_cache(pet_id, 'body', lambda: _v357_parts_abelha(spec)['body']),
            'head': _v357_part_cache(pet_id, 'head', lambda: _v357_parts_abelha(spec)['head']),
            'wing': _v357_part_cache(pet_id, 'wing', lambda: _v357_parts_abelha(spec)['wing']),
            'leg': _v357_part_cache(pet_id, 'leg', lambda: _v357_parts_abelha(spec)['leg']),
        }
    if pet_id == 'FANTASMA':
        return {
            'body': _v357_part_cache(pet_id, 'body', lambda: _v357_parts_fantasma(spec)['body']),
            'arm': _v357_part_cache(pet_id, 'arm', lambda: _v357_parts_fantasma(spec)['arm']),
        }
    if pet_id == 'BOLHA':
        return {
            'body': _v357_part_cache(pet_id, 'body', lambda: _v357_parts_bolha(spec)['body']),
            'orb': _v357_part_cache(pet_id, 'orb', lambda: _v357_parts_bolha(spec)['orb']),
        }
    return {}


def _v357_draw_raposa(dest, p, spec):
    parts = _v357_get_parts('RAPOSA', spec)
    cx, cy = 32, 30 + p['bounce']
    _v357_shadow(dest, (cx, 46), (38, 8), 68)
    _v357_blit_center(dest, parts['tail'], (18, cy - 1), p['tail'] - 12)
    for ox, ph in ((-9, p['legA']), (-3, p['legB']), (5, p['legB']), (11, p['legA'])):
        _v357_blit_center(dest, parts['leg'], (cx + ox, cy + 12), ph)
    _v357_blit_center(dest, parts['body'], (cx, cy), p['tilt'], p['scale_x'])
    _v357_blit_center(dest, parts['head'], (cx + 12, cy - 4), p['head_tilt'] + p['tilt'] * 0.4)
    _v357_emit_particles(dest, (cx, cy), 'HABILIDADE' if p['mood'] == 'power' else ('CARINHO' if p['mood']=='heart' else ('FESTA' if p['mood']=='joy' else '')),
                         spec['energy'], int(p['t'] * 100))


def _v357_draw_tartaruga(dest, p, spec):
    parts = _v357_get_parts('TARTARUGA', spec)
    cx, cy = 31, 31 + p['bounce']
    _v357_shadow(dest, (cx, 46), (38, 8), 64)
    _v357_blit_center(dest, parts['tail'], (cx - 13, cy + 1), p['tail'] * 0.2)
    for ox, ph in ((-8, p['legA'] * 0.35), (-2, p['legB'] * 0.35), (4, p['legB'] * 0.35), (10, p['legA'] * 0.35)):
        _v357_blit_center(dest, parts['leg'], (cx + ox, cy + 8), ph)
    _v357_blit_center(dest, parts['shell'], (cx, cy), p['tilt'] * 0.3, p['scale_x'])
    _v357_blit_center(dest, parts['head'], (cx + 16, cy + 1), p['head_tilt'])
    _v357_emit_particles(dest, (cx, cy), 'FESTA' if p['mood']=='joy' else '', spec['energy'], int(p['t'] * 100))


def _v357_draw_golem(dest, p, spec):
    parts = _v357_get_parts('GOLEM', spec)
    cx, cy = 31, 30 + p['bounce']
    _v357_shadow(dest, (cx, 46), (40, 9), 72)
    for ox, ang in ((-10, p['arm']), (10, -p['arm'])):
        _v357_blit_center(dest, parts['limb'], (cx + ox, cy + 1), ang * 0.6)
    for ox, ang in ((-5, p['legA'] * 0.45), (5, p['legB'] * 0.45)):
        _v357_blit_center(dest, parts['limb'], (cx + ox, cy + 13), ang)
    _v357_blit_center(dest, parts['torso'], (cx, cy + 2), p['tilt'] * 0.4, p['scale_x'])
    _v357_blit_center(dest, parts['head'], (cx + 9, cy - 10), p['head_tilt'])
    if p['mood'] in ('power', 'joy'):
        _v357_emit_particles(dest, (cx, cy), 'HABILIDADE' if p['mood']=='power' else 'FESTA', spec['energy'], int(p['t'] * 100))


def _v357_draw_dragon(dest, p, spec, plasma=False):
    pet_id = 'DRAGAO_PLASMA' if plasma else 'DRAGAO'
    parts = _v357_get_parts(pet_id, spec)
    cx, cy = 30, 28 + p['hover']
    _v357_shadow(dest, (cx, 46), (34, 7), 52)
    _v357_blit_center(dest, parts['tail'], (cx - 12, cy + 2), p['tail'])
    _v357_blit_center(dest, parts['wing'], (cx - 2, cy - 5), -p['wing'])
    _v357_blit_center(dest, pygame.transform.flip(parts['wing'], False, True), (cx, cy + 5), p['wing'])
    for ox, ang in ((-3, p['legA'] * 0.35), (4, p['legB'] * 0.35)):
        _v357_blit_center(dest, parts['leg'], (cx + ox, cy + 11), ang)
    _v357_blit_center(dest, parts['body'], (cx, cy), p['tilt'] * 0.5, p['scale_x'])
    _v357_blit_center(dest, parts['head'], (cx + 12, cy - 3), p['head_tilt'] + p['tilt'] * 0.4)
    _v357_emit_particles(dest, (cx, cy), 'HABILIDADE' if p['mood']=='power' else ('FESTA' if p['mood']=='joy' else ''), spec['energy'], int(p['t'] * 100))


def _v357_draw_beijaflor(dest, p, spec):
    parts = _v357_get_parts('BEIJA_FLOR', spec)
    cx, cy = 32, 27 + p['hover']
    _v357_shadow(dest, (cx, 46), (28, 6), 42)
    _v357_blit_center(dest, parts['wing'], (cx - 4, cy - 3), -p['wing'])
    _v357_blit_center(dest, pygame.transform.flip(parts['wing'], False, True), (cx - 2, cy + 4), p['wing'])
    _v357_blit_center(dest, parts['tail'], (cx - 10, cy + 1), p['tail'] * 0.5)
    _v357_blit_center(dest, parts['body'], (cx, cy), p['tilt'] * 0.3)
    _v357_blit_center(dest, parts['head'], (cx + 9, cy - 1), p['head_tilt'])
    _v357_emit_particles(dest, (cx, cy), 'HABILIDADE' if p['mood']=='power' else ('FESTA' if p['mood']=='joy' else ''), spec['energy'], int(p['t'] * 100))


def _v357_draw_abelha(dest, p, spec):
    parts = _v357_get_parts('ABELHA_MAGNETICA', spec)
    cx, cy = 31, 28 + p['hover']
    _v357_shadow(dest, (cx, 46), (28, 6), 44)
    _v357_blit_center(dest, parts['wing'], (cx - 2, cy - 4), -p['wing'])
    _v357_blit_center(dest, pygame.transform.flip(parts['wing'], False, True), (cx + 1, cy - 1), p['wing'])
    _v357_blit_center(dest, parts['body'], (cx - 1, cy), p['tilt'] * 0.3)
    _v357_blit_center(dest, parts['head'], (cx + 10, cy), p['head_tilt'])
    _v357_blit_center(dest, parts['leg'], (cx - 2, cy + 7), p['legA'] * 0.2)
    _v357_blit_center(dest, parts['leg'], (cx + 2, cy + 8), p['legB'] * 0.2)
    _v357_emit_particles(dest, (cx, cy), 'HABILIDADE' if p['mood']=='power' else ('FESTA' if p['mood']=='joy' else ''), spec['energy'], int(p['t'] * 100))


def _v357_draw_fantasma(dest, p, spec):
    parts = _v357_get_parts('FANTASMA', spec)
    cx, cy = 31, 27 + p['hover']
    _v357_shadow(dest, (cx, 46), (32, 7), 48)
    _v357_blit_center(dest, parts['arm'], (cx - 12, cy + 2), p['arm'] * 0.35)
    _v357_blit_center(dest, parts['arm'], (cx + 13, cy + 2), -p['arm'] * 0.35)
    _v357_blit_center(dest, parts['body'], (cx, cy), p['tilt'] * 0.3, p['scale_x'])
    _v357_emit_particles(dest, (cx, cy), 'CARINHO' if p['mood']=='heart' else ('FESTA' if p['mood']=='joy' else ('HABILIDADE' if p['mood']=='power' else '')), spec['energy'], int(p['t'] * 100))


def _v357_draw_bolha(dest, p, spec):
    parts = _v357_get_parts('BOLHA', spec)
    cx, cy = 31, 28 + p['hover']
    _v357_shadow(dest, (cx, 46), (28, 6), 38)
    _v357_blit_center(dest, parts['body'], (cx, cy), p['tilt'] * 0.2, p['scale_x'])
    for i, ang in enumerate((0, 2.1, 4.2)):
        ax = cx + math.cos(p['t'] * math.tau + ang) * 13
        ay = cy + math.sin(p['t'] * math.tau * 1.2 + ang) * 7
        _v357_blit_center(dest, parts['orb'], (ax, ay), 0)
    _v357_emit_particles(dest, (cx, cy), 'CARINHO' if p['mood']=='heart' else ('FESTA' if p['mood']=='joy' else ('HABILIDADE' if p['mood']=='power' else '')), spec['energy'], int(p['t'] * 100))


def _v357_draw_pet_frame(pet_id, state, idx, total, tamanho=(64, 56)):
    frame_sheet = _v388_try_pet_sheet_frame(pet_id, state, idx, total)
    if frame_sheet is not None:
        return frame_sheet
    spec = _v357_pet_specs().get(pet_id)
    if spec is None:
        return _v357_surface(tamanho)
    surf = _v357_surface((64, 56))
    perfil = _perfil_refino_pet(pet_id)
    p = _v357_state_profile(state, idx, total, voador=(spec['tipo'] == 'voador'), ritmo=perfil['ritmo'])
    if pet_id == 'RAPOSA':
        _v357_draw_raposa(surf, p, spec)
    elif pet_id == 'TARTARUGA':
        _v357_draw_tartaruga(surf, p, spec)
    elif pet_id == 'GOLEM':
        _v357_draw_golem(surf, p, spec)
    elif pet_id == 'DRAGAO':
        _v357_draw_dragon(surf, p, spec, plasma=False)
    elif pet_id == 'DRAGAO_PLASMA':
        _v357_draw_dragon(surf, p, spec, plasma=True)
    elif pet_id == 'BEIJA_FLOR':
        _v357_draw_beijaflor(surf, p, spec)
    elif pet_id == 'ABELHA_MAGNETICA':
        _v357_draw_abelha(surf, p, spec)
    elif pet_id == 'FANTASMA':
        _v357_draw_fantasma(surf, p, spec)
    elif pet_id == 'BOLHA':
        _v357_draw_bolha(surf, p, spec)
    if tuple(tamanho) != surf.get_size():
        surf = pygame.transform.smoothscale(surf, (int(tamanho[0]), int(tamanho[1]))).convert_alpha()
    return surf


def _v357_render_sequence(pet_id, state, tamanho=(52, 46)):
    total = _v357_state_total(state)
    return tuple(_v357_draw_pet_frame(pet_id, state, i, total, tamanho).convert_alpha() for i in range(total))






















def exportar_sprites_pets_v357(base_dir):
    from pathlib import Path
    estados = ['CORRER', 'ESPERA', 'AGACHAR', 'IMPULSO', 'SUBINDO', 'APICE', 'CAINDO', 'POUSO', 'MORRER', 'HABILIDADE', 'FESTA', 'ALERTA']
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)
    for pet_id in PETS_CONFIG.keys():
        for estado in estados:
            frames = _quadros_pet_estado(pet_id, estado, (128, 112))
            pasta = base / pet_id / estado.lower()
            pasta.mkdir(parents=True, exist_ok=True)
            for i, frame in enumerate(frames):
                pygame.image.save(frame, str(pasta / f'{estado.lower()}_{i:03d}.png'))




# =============================================================
# ANIMATION ENGINE 5.0 - PILHA VISUAL (v3.59.0)
# A movimentacao do corpo nao e interrompida por reacoes.
# 30 quadros PRE-RENDERIZADOS por estado, somente blits em jogo.
# =============================================================
PET5_FREQUENCIAS = {
    'RAPOSA': 2.7, 'TARTARUGA': 1.35, 'GOLEM': 1.65, 'BOLHA': 2.0,
    'FANTASMA': 1.6, 'DRAGAO': 2.35, 'DRAGAO_PLASMA': 2.65,
    'BEIJA_FLOR': 4.8, 'ABELHA_MAGNETICA': 6.2,
}
PET5_ESTADOS_FISICOS = frozenset((
    'MORRER','SWIPE_DOWN','IMPULSO','SUBINDO','APICE','CAINDO',
    'POUSO','AGACHAR'
))
PET5_ESTADOS_REACAO = frozenset((
    'FESTA','ALERTA','HABILIDADE','CURIOSO','ALIVIO','CARINHO','BRINCAR'
))
PET5_DURACOES = {
    'IMPULSO': 6, 'SUBINDO': 13, 'APICE': 8, 'CAINDO': 12,
    'SWIPE_DOWN': 9, 'POUSO': 11, 'MORRER': 36
}
PET5_ESTADOS_TESTE = (
    'CORRER','ESPERA','AGACHAR','IMPULSO','SUBINDO','APICE',
    'CAINDO','SWIPE_DOWN','POUSO','HABILIDADE','ALERTA',
    'FESTA','CARINHO','SONO','MORRER'
)


def pet5_escolher_canais(jogador, estado_reacao, em_corrida=True):
    """Canal A: locomocao fisica; B: expressao; C: efeito. Sem substituir corrida por festa."""
    if jogador is not None:
        if jogador.morrendo:
            return 'MORRER', '', ''
        if not jogador.no_chao:
            if getattr(jogador, 'descida_rapida', False):
                locomocao = 'SWIPE_DOWN'
            elif estado_reacao in ('IMPULSO','SUBINDO','APICE','CAINDO'):
                locomocao = estado_reacao
            elif float(jogador.velocidade_y) < -2:
                locomocao = 'SUBINDO'
            elif float(jogador.velocidade_y) > 2:
                locomocao = 'CAINDO'
            else:
                locomocao = 'APICE'
        elif jogador.agachado:
            locomocao = 'AGACHAR'
        elif estado_reacao == 'POUSO':
            locomocao = 'POUSO'
        else:
            locomocao = 'CORRER'
    else:
        locomocao = 'ESPERA'
    expressao = estado_reacao if estado_reacao in PET5_ESTADOS_REACAO else ''
    efeito = expressao if expressao in ('FESTA','ALERTA','HABILIDADE','CARINHO') else ''
    return locomocao, expressao, efeito


def pet5_indice_quadro(pet_id, estado, frame_count, desde=0, n=30):
    """Relogio derivado do timestep fixo de 60 Hz; nao reinicia a marcha com reacoes."""
    if n <= 1: return 0
    if estado in PET5_DURACOES:
        elapsed = max(0,int(frame_count-desde))
        dur = PET5_DURACOES[estado]
        return min(n-1,int(elapsed*(n-1)/max(1,dur-1)))
    freq=PET5_FREQUENCIAS.get(pet_id,2.0)
    if estado in ('ESPERA','SONO'): freq *= 0.24
    elif estado=='AGACHAR': freq *= 0.75
    elif estado in ('BRINCAR','FESTA'): freq *= 0.90
    # Ciclo global e continuo. Nao depende do inicio do alerta/febre.
    return int(max(0,frame_count)*freq*n/60.0)%n

_PET5_PRECARREGADO = set()
def pet5_precarregar(pet_id):
    """Chamada ao INICIAR a corrida, antes do loop de renderizacao."""
    if pet_id not in PETS_CONFIG:
        return
    # Reconfere o LRU mesmo para pets ja usados: a loja pode ter desalojado seus quadros.
    tamanho=(68,58) if pet_eh_voador(pet_id) else (58,52)
    for estado in ('CORRER','AGACHAR','SWIPE_DOWN','IMPULSO','SUBINDO',
                   'APICE','CAINDO','POUSO','MORRER'):
        _quadros_pet_estado(pet_id,estado,tamanho)
    _PET5_PRECARREGADO.add(pet_id)


def pet5_desenhar_efeito_leve(superficie, efeito, x, y, tick, cor):
    """Efeitos sutis fora do corpo; nunca substituem a animacao das asas/patas."""
    if efeito not in ('FESTA','ALERTA','HABILIDADE','CARINHO'):
        return
    if efeito=='ALERTA':
        xx,yy=int(x+17),int(y-28)
        pygame.draw.circle(superficie,(255,227,115),(xx,yy),4)
        pygame.draw.line(superficie,(48,42,54),(xx,yy-2),(xx,yy),1)
        return
    cx,cy=int(x),int(y)
    for j in range(2 if efeito!='HABILIDADE' else 3):
        ang=(tick*0.11+j*2.45)
        xx=int(cx+math.cos(ang)*23)
        yy=int(cy-8+math.sin(ang)*15)
        tom=(255,146,193) if efeito=='CARINHO' else (255,235,153) if efeito=='FESTA' else cor
        pygame.draw.line(superficie,tom,(xx-2,yy),(xx+2,yy),1)
        pygame.draw.line(superficie,tom,(xx,yy-2),(xx,yy+2),1)


def pet5_quadro(pet_id, estado, tick, desde=0, tamanho=(52,46)):
    quadros=_quadros_pet_estado(pet_id,estado,tamanho)
    return quadros[pet5_indice_quadro(pet_id,estado,tick,desde,len(quadros))]


def pet5_previa_popup(pet_id, frame_contador):
    # Loja: respiracao lenta + festa pontual; sem recortes ou escala dentro do frame.
    estado = 'FESTA' if (frame_contador//210)%6==5 else 'ESPERA'
    return pet5_quadro(pet_id,estado,frame_contador,0,(210,170))






# ============================================================
# ANIMATION ENGINE 8.0 - RIG RIGIDO / QUADROS PRECOMPILADOS
# Render de corrida: apenas quadros PNG, sem calcular ossos.
# Editor DEV: rotacao de articulacoes reais, visivel em tempo real.
# ============================================================
PET6_ESTADOS = PET5_ESTADOS_TESTE
PET5_FREQUENCIAS.update({
    'RAPOSA': 2.45, 'TARTARUGA': 1.30, 'GOLEM': 1.45, 'BOLHA': 1.85,
    'FANTASMA': 1.65, 'DRAGAO': 2.10, 'DRAGAO_PLASMA': 2.40,
    'BEIJA_FLOR': 4.20, 'ABELHA_MAGNETICA': 4.70,
})

# ENGINE 8.0 - cadências medidas em ciclos por segundo em passo fixo.
# Referência: apoio/suspensão quadrúpede e downstroke/recovery de asas.
PET5_FREQUENCIAS.update({
    'RAPOSA':2.75, 'TARTARUGA':1.55, 'GOLEM':1.65, 'BOLHA':1.40,
    'FANTASMA':1.45, 'DRAGAO':1.85, 'DRAGAO_PLASMA':2.15,
    'BEIJA_FLOR':3.65, 'ABELHA_MAGNETICA':4.25,
})
PET6_ESTADOS = (
    'CORRER','ESPERA','AGACHAR','SWIPE_DOWN','IMPULSO','SUBINDO',
    'APICE','CAINDO','POUSO','MORRER','HABILIDADE','FESTA','ALERTA',
    'ALIVIO','CURIOSO','BRINCAR','CARINHO','SONO',
)

# Necessarias somente para o editor DEV; nunca para a corrida ou a loja.
_PET6_EDITOR_RIG_CACHE = {}

def pet6_carregar_rig(pet_id):
    """Pivos de REFERENCIA para o visualizador DEV, sem carregar PNG/RIG.

    No modo procedural, o corpo inteiro e desenhado em codigo. Os pivos
    aqui servem somente como marcadores de inspecao e anotacoes DEV.
    """
    if pet_id in _PET6_EDITOR_RIG_CACHE:
        return _PET6_EDITOR_RIG_CACHE[pet_id]
    tipos = {
        'RAPOSA': [('cauda',(26,49)),('pata_traseira',(44,61)),
                   ('pata_dianteira',(74,61)),('orelha',(84,30))],
        'TARTARUGA':[('pata_tras',(32,60)),('pata_frente',(70,60)),('cabeca',(78,42))],
        'GOLEM':[('braco_tras',(33,42)),('braco_frente',(80,42)),
                 ('perna_tras',(49,60)),('perna_frente',(70,60))],
        'BEIJA_FLOR':[('asa_tras',(57,40)),('asa_frente',(62,42)),('cauda',(39,55))],
        'DRAGAO':[('asa_tras',(60,42)),('asa_frente',(62,42)),('cauda',(34,51)),
                  ('pata_tras',(53,61)),('pata_frente',(75,61))],
        'DRAGAO_PLASMA':[('asa_tras',(60,42)),('asa_frente',(62,42)),
                         ('cauda',(34,51)),('pata_tras',(53,61)),('pata_frente',(75,61))],
        'ABELHA_MAGNETICA':[('asa_tras',(58,40)),('asa_frente',(65,42)),
                            ('antena',(85,40))],
        'FANTASMA':[('braco_tras',(30,51)),('braco_frente',(81,52))],
        'BOLHA':[('bolha_tras',(23,26)),('bolha_frente',(87,30))],
    }
    coords=tipos.get(pet_id,[('centro',(56,48))])
    ossos=[{'nome':nome,'pivo':(int(px*84/112),int(py*76/96)),
            'angulo_max':20,'fase':i*90,'camada':'back'}
           for i,(nome,(px,py)) in enumerate(coords)]
    data={'ossos':ossos,'modo':'procedural','escala_base':(112,96)}
    _PET6_EDITOR_RIG_CACHE[pet_id]=data
    return data


def pet6_rotacionar_pivo(dest, sprite, pivo, angulo, deslocamento=(0,0)):
    """Rotacao rigida com pivo especifico; altera somente o editor, nao a corrida."""
    cx,cy = sprite.get_width()*0.5, sprite.get_height()*0.5
    x,y = float(pivo[0]),float(pivo[1])
    v = pygame.Vector2(x-cx, y-cy)
    mov = v.rotate(-angulo)
    centro = (cx+v.x-mov.x+deslocamento[0], cy+v.y-mov.y+deslocamento[1])
    img=pygame.transform.rotate(sprite, angulo)
    dest.blit(img,img.get_rect(center=(int(centro[0]),int(centro[1]))))


def pet6_editor_angulo(bone, estado, tick, velocidade):
    """Visualização DEV de apoio real e ciclo de batida em pivôs rígidos.

    A versão LIMPA usa APENAS os PNGs pré-compilados, sem cálculos de ossos.
    """
    t=(float(tick)*float(velocidade)/60.0)%1.0
    fase=float(bone.get('fase',0))/360.0
    nome=bone['nome']
    amplitude=float(bone['angulo_max'])
    if 'asa' in nome:
        c=(t+fase)%1.0
        if estado=='SONO':return -7.0
        if estado=='MORRER':return 11.0
        if c<0.39:
            fase_asa=-math.cos(math.pi*c/0.39)
        else:
            fase_asa=math.cos(math.pi*(c-0.39)/0.61)
        fator=0.5 if estado in ('AGACHAR','SWIPE_DOWN') else 1.0
        return amplitude*fator*fase_asa
    if any(x in nome for x in ('pata','perna')):
        if estado in ('CORRER','AGACHAR','BRINCAR'):
            c=(t+fase)%1.0
            if c<0.57:
                p=c/0.57
                return max(-20,min(20,(-4.5+9*p)*3.0))
            p=(c-0.57)/0.43
            return max(-20,min(20,(4.5-9*(p*p*(3-2*p)))*3.0))
        if estado in ('IMPULSO','SUBINDO','APICE'):return -12.0
        if estado in ('CAINDO','SWIPE_DOWN','POUSO'):return 10.0
        return 0.0
    if estado=='SONO':return 0.0
    if estado=='MORRER':return amplitude*0.3
    return min(amplitude,10.0)*math.sin(math.tau*(t-0.18+fase))*0.6



def pet6_montar_preview(pet_id, estado, tick, velocidade, alteracoes):
    # v3.64: editor mostra o PNG FINAL usado no jogo, sem cortes reconstrutivos
    # em tempo real. Ajustes de ossos exigem compilar sprites novamente offline.
    quadros = _quadros_pet_estado(pet_id, estado, (84, 76))
    frame = pet8_indice(pet_id, estado, tick, total=len(quadros), intensidade=1.0)
    return quadros[frame].copy()


def pet6_montar_preview_legado(pet_id, estado, tick, velocidade, alteracoes):
    # Mantem compatibilidade sem carregar partes de imagens antigas.
    return pet6_montar_preview(pet_id, estado, tick, velocidade, alteracoes)


def pet6_escrever_pose_dev(pet_id, estado, alteracoes, velocidade):
    # Os ajustes salvos sao para autoria/teste, NAO alteram o jogo LIMPA.
    local=os.path.join(os.path.dirname(os.path.abspath(__file__)),'poses_rig_DEV.json')
    dados={}
    if os.path.exists(local):
        try:
            with open(local,'r',encoding='utf-8') as arq: dados=json.load(arq)
        except (ValueError,OSError): dados={}
    dados.setdefault(pet_id,{})[estado]={
        'ajustes_graus': dict(alteracoes), 'velocidade_previa': float(velocidade)}
    with open(local,'w',encoding='utf-8') as arq:
        json.dump(dados,arq,ensure_ascii=False,indent=2)
    return local




# ============================================================================
# ANIMATION ENGINE 8.0 (v3.87.0) - UNICO CONTROLADOR ATIVO NA CORRIDA
# Estados fisicos tem prioridade; efeitos e reacoes permanecem separados.
# TODOS os membros e o foot-lock sao gerados OFFLINE no compilador dos PNGs.
# No jogo: apenas selecao, blit e uma transicao curta quando troca de estado.
# ============================================================================
PET8_FREQUENCIAS = {
    'RAPOSA': 2.65, 'TARTARUGA': 1.45, 'GOLEM': 1.55, 'BOLHA': 1.25,
    'FANTASMA': 1.45, 'DRAGAO': 1.75, 'DRAGAO_PLASMA': 2.10,
    'BEIJA_FLOR': 3.15, 'ABELHA_MAGNETICA': 3.55,
}
# Frequencias reduzidas para manter >= 16 poses do bater de asas em 60Hz.
PET8_DURACOES = {
    'IMPULSO': 6, 'SUBINDO': 15, 'APICE': 8, 'CAINDO': 14,
    'SWIPE_DOWN': 11, 'POUSO': 11, 'MORRER': 42,
}
PET8_LOOPS = frozenset(('CORRER','ESPERA','AGACHAR','SONO','HABILIDADE',
                        'FESTA','ALERTA','CARINHO','BRINCAR','CURIOSO','ALIVIO'))
PET8_GAIT = {
    'RAPOSA':(0.00,0.12,0.53,0.66),
    'TARTARUGA':(0.00,0.50,0.72,0.22),
    'GOLEM':(0.00,0.50),
}








def pet8_apoio_preview(pet_id,estado,tick,multiplicador=1.0):
    """DEV: mostra quais membros estão em stance (pé plantado)."""
    if pet_id not in PET8_GAIT:
        return ()
    if estado not in ('CORRER','AGACHAR','BRINCAR'):
        return tuple(True for _ in PET8_GAIT[pet_id])
    hz=PET8_FREQUENCIAS.get(pet_id,1.0)*multiplicador
    fase=((max(0,tick)/60.0)*hz)%1.0
    return tuple(((fase+offset)%1.0) < 0.56 for offset in PET8_GAIT[pet_id])



# ==========================================================================
# PIXEL RUSH v3.87.0 — Animation Engine 9.0 / Expressões independentes
# Corpo e asas continuam renderizados OFFLINE. Apenas pequenas expressões
# cosméticas em overlay, com clocks que não reiniciam corrida e voo.
# ==========================================================================
PET9_ANCHOR_OLHOS = {
    'RAPOSA': ((63,45),), 'TARTARUGA': ((67,46),),
    'GOLEM': ((56,49),(66,49)), 'BOLHA': ((35,44),(59,44)),
    'FANTASMA': ((49,36),(67,36)), 'DRAGAO': ((69,43),),
    'DRAGAO_PLASMA': ((64,45),), 'BEIJA_FLOR': ((50,43),),
    'ABELHA_MAGNETICA': ((65,53),),
}
PET9_CORES_PALPEBRA = {
    'RAPOSA': (243,233,224), 'TARTARUGA': (78,79,171),
    'GOLEM': (72,57,56), 'BOLHA': (60,201,245),
    'FANTASMA': (222,139,246), 'DRAGAO': (144,70,202),
    'DRAGAO_PLASMA': (114,230,245), 'BEIJA_FLOR': (147,223,252),
    'ABELHA_MAGNETICA': (250,233,196),
}


def pet9_desenhar_expressao(superficie, pet_id, tick, pos, tamanho,
                            estado_fisico, reacao='', leve=False):
    """Piscar/olhar/reagir sem interromper o movimento principal.

    Custo de 0-3 primitivas quando inativo. Nenhuma superfície do tamanho da
    tela, nenhum acesso a disco e nenhum cálculo de esqueleto por frame.
    """
    if estado_fisico in ('MORRER','SONO'):
        return
    w,h = tamanho
    # Piscadas e olhos ja fazem parte do desenho procedural por estado.
    # Overlay do atlas antigo foi removido para nao pintar fora do rosto.
    if not reacao or leve:
        return
    cx,cy=int(pos[0]+w*0.31),int(pos[1]-h*0.42)
    # Reações não controlam o frame de locomoção. O canal de efeito é independente.
    if reacao == 'CARINHO':
        cy -= (int(tick)//9)%3
        pygame.draw.circle(superficie,(255,145,197),(cx-3,cy),2)
        pygame.draw.circle(superficie,(255,145,197),(cx+2,cy),2)
        pygame.draw.polygon(superficie,(255,145,197),[(cx-5,cy),(cx+4,cy),(cx,cy+5)])
    elif reacao == 'ALERTA':
        pygame.draw.line(superficie,(255,237,132),(cx,cy-5),(cx,cy+1),2)
        pygame.draw.circle(superficie,(255,237,132),(cx,cy+5),1)
    elif reacao in ('FESTA','HABILIDADE'):
        fase=(int(tick)//6)%4
        px=cx+(2 if fase%2 else -3)
        py=cy+(-2 if fase//2 else 1)
        pygame.draw.line(superficie,(170,247,255),(px-2,py),(px+2,py),1)
        pygame.draw.line(superficie,(170,247,255),(px,py-2),(px,py+2),1)
    elif reacao == 'CURIOSO':
        pygame.draw.arc(superficie,(188,240,255),(cx-3,cy-4,7,7),0.3,2.9,1)
        pygame.draw.circle(superficie,(188,240,255),(cx,cy+5),1)



# ===============================================================
# PIXEL RUSH v3.87.0 - CHARACTER BUILDER: ARTE INTEGRAL / POSES MANUAIS
# Fonte UNICA de tempo/cache/renderizacao. Pillow monta os pets a partir das bases aprovadas
# e o Pygame faz cache/renderizacao das animacoes.
# ===============================================================
# Pets temporariamente indisponíveis: compatibilidade sem atlases ou bibliotecas.
# O ID salvo é preservado; render de pet é transparente enquanto COMING SOON.
class SpriteCatalogError(RuntimeError):
    pass

def _studio9_preview_index(*args, **kwargs):
    return 0

class PetStudioPlayer:
    def __init__(self, *args, **kwargs):
        self._transparentes = {}
    def frames(self, pet_id, estado, tamanho=(52, 46)):
        chave = (max(1, int(tamanho[0])), max(1, int(tamanho[1])))
        if chave not in self._transparentes:
            self._transparentes[chave] = (pygame.Surface(chave, pygame.SRCALPHA),)
        return self._transparentes[chave]
    def preload(self, *args, **kwargs):
        return None
    def index(self, *args, **kwargs):
        return 0
    def render(self, *args, **kwargs):
        return self.frames(None, None, kwargs.get('tamanho', (52, 46)))[0]
_PET_STUDIO9 = PetStudioPlayer(
    None,  # v3.87.0: bases dos pets ficam em pet_bases_v3.87.0/.
    budget_bytes=16*1024*1024,
    strict=False,
)

def _quadros_pet_estado(pet_id, estado, tamanho=(52, 46)):
    return _PET_STUDIO9.frames(pet_id, estado, tamanho)

def pet_eh_voador(pet_id):
    return pet_id in ('FANTASMA','DRAGAO','BEIJA_FLOR','DRAGAO_PLASMA','ABELHA_MAGNETICA')

def pet5_precarregar(pet_id):
    if pet_id in PETS_CONFIG:
        _PET_STUDIO9.preload(pet_id,airborne=pet_eh_voador(pet_id))

def pet8_indice(pet_id,estado,tick,inicio=0,total=30,intensidade=1.0):
    return _studio9_preview_index(pet_id,estado,tick-inicio,total,intensidade)

def pet8_obter_quadros(pet_id,estado,tick,memoria,tamanho,intensidade=1.0):
    frames=_PET_STUDIO9.frames(pet_id,estado,tamanho)
    n=_PET_STUDIO9.index(pet_id,estado,tick,memoria,len(frames),intensidade)
    return frames[n], None, 255

def pet8_desenhar(superficie,pet_id,estado,tick,memoria,tamanho,pos,intensidade=1.0):
    return _PET_STUDIO9.render(superficie,pet_id,estado,tick,memoria,tamanho,pos,intensidade)

def _popup_pet_animado(pet_id, frame_contador):
    estado='FESTA' if (frame_contador//90)%6==5 else 'ESPERA'
    frames=_quadros_pet_estado(pet_id,estado,(210,170))
    return frames[_studio9_preview_index(pet_id,estado,frame_contador,len(frames),1.0)]

def desenhar_preview_pet_popup(superficie,pet_id,frame_contador,rect_destino):
    w,h=max(16,rect_destino.w-24),max(16,rect_destino.h-18)
    estado='FESTA' if (frame_contador//90)%6==5 else 'ESPERA'
    frames=_quadros_pet_estado(pet_id,estado,(w,h))
    img=frames[_studio9_preview_index(pet_id,estado,frame_contador,len(frames))]
    superficie.blit(img,img.get_rect(center=(rect_destino.centerx,rect_destino.centery-2)))

def _quadros_pet_personalidade(pet_id,estado,tamanho=(52,46)):
    mapper={'OCIOSO':'ESPERA','SURPRESA':'ALERTA'}
    return _quadros_pet_estado(pet_id,mapper.get(estado,estado),tamanho)

def _quadros_pet_menu_ocioso(pet_id):
    return _quadros_pet_estado(pet_id,'ESPERA',(54,48))

def _quadros_pet_corrida(pet_id):
    return tuple(_quadros_pet_estado(pet_id,state,(52,46))
                 for state in ('CORRER','MORRER','ESPERA','HABILIDADE'))

def _sprite_base_pet_animacao(pet_id):
    return _quadros_pet_estado(pet_id,'ESPERA',(52,46))[0].copy()

def _sequencia_estado_folha_pet(pet_id,estado,tamanho=(52,46)):
    return _quadros_pet_estado(pet_id,estado,tamanho)

def desenhar_mini_pet(superficie,pet_id,cor,x,y):
    selo=pygame.Rect(x-2,y-2,44,44)
    _desenhar_selo_mini_pet(superficie,selo,cor)
    superficie.blit(_quadros_pet_estado(pet_id,'ESPERA',(40,40))[0],(x,y))

def desenhar_pet_detalhado(superficie,pet_id,cor):
    superficie.blit(_quadros_pet_estado(pet_id,'ESPERA',(180,158))[0],(0,12))



def desenhar_pets_em_breve(superficie, btn_voltar):
    """Área suspensa: desenho estático, sem carregar ou animar pets."""
    superficie.fill((43, 43, 43))
    pygame.draw.rect(superficie, (70, 70, 70), (17, 10, 416, 115), border_radius=14)
    desenhar_texto_centralizado(superficie, "LOJA DE PETS", fonte, (185,185,185), (25,25,25), 38)
    for x, label in ((35,"SKINS"),(230,"PETS")):
        rect=pygame.Rect(x,130,185,34)
        pygame.draw.rect(superficie,(77,77,77),rect,border_radius=8)
        desenhar_rotulo_botao(superficie,label,fonte_missoes,(145,145,145),(40,40,40),rect)
    for row, pet in enumerate(list(PETS_CONFIG.values())[:5]):
        rect=pygame.Rect(28,175+row*91,394,82)
        pygame.draw.rect(superficie,(61,61,61),rect,border_radius=10)
        pygame.draw.rect(superficie,(90,90,90),rect,1,border_radius=10)
        pygame.draw.rect(superficie,(82,82,82),(40,rect.y+13,54,54),border_radius=9)
        label=render_texto_cacheado(fonte_missoes,pet['nome'],(134,134,134))
        superficie.blit(label,(108,rect.y+17))
        label=render_texto_cacheado(fonte_pequena,"INDISPONIVEL",(113,113,113))
        superficie.blit(label,(108,rect.y+45))
    faixa=pygame.Rect(0,325,LARGURA_VIRTUAL,128)
    pygame.draw.rect(superficie,(26,26,26),faixa)
    pygame.draw.line(superficie,(175,175,175),(0,325),(LARGURA_VIRTUAL,325),3)
    pygame.draw.line(superficie,(175,175,175),(0,453),(LARGURA_VIRTUAL,453),3)
    desenhar_texto_centralizado(superficie,"COMING SOON",fonte,(235,235,235),(0,0,0),367)
    desenhar_texto_centralizado(superficie,"Pets em breve",fonte_missoes,(165,165,165),(0,0,0),411)
    pygame.draw.rect(superficie,(82,82,82),btn_voltar,border_radius=10)
    pygame.draw.rect(superficie,(190,190,190),btn_voltar,2,border_radius=10)
    desenhar_rotulo_botao(superficie,"VOLTAR",fonte,(235,235,235),(25,25,25),btn_voltar)


from pixelrush_polimento_v3171 import painel_menu, brilho_coletaveis, acabamento_hud
from pixelrush_cinema_v3192 import profundidade_cinematografica
from pixelrush_sombras_v3234 import sombra_contato
from pixelrush_controles_v3171 import (DedosAtivos, MODO_CLASSICO, MODO_GESTOS, MODO_BOTOES, MODOS, SENSIBILIDADES, normalizar_modo, limiar, botoes, desenhar_botoes, desenhar_painel_controles)
from pixelrush_cinema_v3172 import (DiretorMusical, AuditorJustica, EsquivaPerfeita, MovimentoExpressivo, CameraCinematica, CenasCinematograficas)
from pixelrush_cenas_v3213 import CenasMemoraveis
from pixelrush_preparacao_prod_v32778 import instalar as _instalar_preparacao_2778
from pixelrush_extras_v3174 import (ReplayCinematografico,
                                    PaisagemSonora, HarmonizadorFrames)
# QA v3.277.50: contrato unico de camera e apresentacao; nao muda main/DEV.
from pixelrush_qa_unified_post_v327750 import finalizar_quadro as _qa_finalizar_quadro
_QA_PIPELINE_750 = (os.environ.get('PIXELRUSH_QA_ANDROID','0') == '1'
                    and os.environ.get('PIXELRUSH_QA_POST_PIPELINE','1') == '1')

# Reaproveita os quadros das skins sem duplicar renderizadores de personagem.
_v3173_quadros_skin_originais = _quadros_skin
_v3173_harmonia_skins = HarmonizadorFrames(limite=320)
_v3173_skins_prontas = {}

def _quadros_skin(nome):
    cached = _v3173_skins_prontas.get(nome)
    if cached is None:
        orig = _v3173_quadros_skin_originais(nome)
        cached = {estado: tuple(_v3173_harmonia_skins.processar(q, 'skin') for q in frames)
                  for estado, frames in orig.items()}
        _v3173_skins_prontas[nome] = cached
    return cached


# v3.178.0 — arte aprovada preservada, pixels internos refinados por skin/estado.
from pixelrush_personagens_v3176 import refinar_atlas as _v3176_refinar_atlas, MovimentoExpressivoPremium
from pixelrush_polimento_atores_prod_v32772 import refinar_atlas_personagem as _prod_refinar_atlas_personagem
_v3176_atlas_anterior = _quadros_skin
_v3176_atlas = {}

def _quadros_skin(nome):
    atlas = _v3176_atlas.get(nome)
    if atlas is None:
        atlas = _v3188_refinar_atlas(
            _v3176_refinar_atlas(_v3176_atlas_anterior(nome),nome),nome)
        # v3.277.2-PROD: RGB pré-processado nas 3 skins ativas; alfa, pose,
        # ordem e cadência permanecem idênticos à v3.277.1-PROD.
        atlas = _prod_refinar_atlas_personagem(atlas, nome)
        _v3176_atlas[nome] = atlas
    return atlas

# Usa o executor de poses atual, com ajuste subpixel imperceptível no rect.
MovimentoExpressivo = MovimentoExpressivoPremium


# v3.178.0 — iluminação e materiais premium (Plano D / etapa 3).
# Integra sobre a arte atual; não modifica sprites, física, colisões ou interface.
from pixelrush_luz_materiais_v3177 import iluminar_panorama as _v3177_panorama, acabamento_tile_chao as _v3177_piso
_v3177_draw_anterior = ParallaxBackground.draw
_v3177_tile_anterior = ParallaxBackground._obter_tile_chao

def _v3177_draw(self, superficie, cor_ceu, e_noite):
    _v3177_draw_anterior(self, superficie, cor_ceu, e_noite)
    if self._bioma_spriteado_ativo():
        _v3177_panorama(superficie, self.cenario, self.peso_noite,
                        self.fase_ciclo, self.clima_tipo)

def _v3177_obter_tile_chao(self):
    tile = _v3177_tile_anterior(self)
    return _v3177_piso(tile, self.cenario)

ParallaxBackground.draw = _v3177_draw
ParallaxBackground._obter_tile_chao = _v3177_obter_tile_chao

# v3.178.0 — HUD e menus premium (Plano D / etapa 4).
# Mantém os retângulos de clique, os estados e os valores da interface originais.
import pixelrush_hud_v3133 as _v3178_hud_atual
from pixelrush_ui_v3178 import (
    instalar_hud as _v3178_instalar_hud,
    painel_identidade as _v3178_painel,
    botao as _v3178_botao,
    palco_menu as _v3178_palco,
    card_menu as _v3178_card_menu,
    controles as _v3178_controles,
    acabamento_config as _v3178_acabamento_config,
    acabamento_hud as _v3178_acabamento_hud,
    gameover as _v3178_gameover,
)
_v3178_instalar_hud(_v3178_hud_atual)
_v3178_palco_antigo = desenhar_palco_menu_premium
_v3178_controles_antigos = desenhar_painel_controles
_v3178_resultados_antigos = desenhar_resultados_premium

def desenhar_painel_identidade(surface, rect, destaque=UI_CIANO, cabecalho=False, discreto=False):
    return _v3178_painel(surface, rect, destaque, cabecalho, discreto)

def desenhar_botao_premium(surface, rect, texto, fonte_obj, cor_fundo, cor_texto, frame_contador, ativo=False):
    return _v3178_botao(surface, rect, texto, fonte_obj, cor_fundo, cor_texto, frame_contador, ativo, desenhar_rotulo_botao)

def desenhar_palco_menu_premium(surface, frame, leve=False):
    return _v3178_palco(surface, frame, leve, _v3178_palco_antigo)

def desenhar_acabamento_card_menu(surface, rect, frame, acento, leve=False):
    return _v3178_card_menu(surface, rect, frame, acento, leve)

def desenhar_painel_controles(surface, dados, fonte_obj, fonte_pequena_obj, rects, frame=0):
    return _v3178_controles(surface, dados, fonte_obj, fonte_pequena_obj, rects, frame, _v3178_controles_antigos)

def desenhar_resultados_premium(surface, frame, inicio, metros, moedas, combo, recorde, missoes, leve=False, dados=None):
    return _v3178_gameover(surface, frame, inicio, metros, moedas, combo, recorde, missoes, leve, _v3178_resultados_antigos, dados)

acabamento_hud = _v3178_acabamento_hud

from pixelrush_acessibilidade_v3210 import desenhar_painel as desenhar_acessibilidade, desenhar_sinais as desenhar_sinais_acessiveis
from pixelrush_letras_v3218 import PalavraDaPartida
from pixelrush_fuga_v3242 import DiretorPerseguidores
from pixelrush_avisos_raros_i18n_v3247 import DiretorEventosRaros
from pixelrush_metricas_v3250 import criar_coletor  # P19: opt-in, sem hooks por quadro
from pixelrush_perf_biomas_v3251 import criar_monitor as criar_monitor_biomas  # QA opcional


def main():
    global portal_proximo_metro
    from pixelrush_apresentacao_v3273 import precisa_tutorial, qa_sem_abertura
    from pixelrush_tutorial_guia_prod_v327724 import TutorialCorrida
    from pixelrush_fundo_mobile_v327726 import CacheFundoMobile
    from pixelrush_producao_fx_v32771 import (desenhar_fx_palavra as _prod_fx_palavra,
                                             desenhar_mensagem_tutorial as _prod_mensagem_tutorial,
                                             desenhar_entrada as _prod_banner_entrada,
                                             desenhar_transicao as _prod_fx_transicao)
    dados = carregar_dados()
    dados["modo_grafico"] = "completo"
    if dados.get('skin_equipada') not in SKINS_ATIVAS_PROD:
        dados['skin_equipada'] = 'AZUL'
    dados['rastro_visual'] = 'DESLIGADO'
    metricas_corrida = criar_coletor(VERSAO, "DEV" if PIXELRUSH_DEV_BUILD else "LIMPA")
    perf_biomas = criar_monitor_biomas(VERSAO, "DEV" if PIXELRUSH_DEV_BUILD else "LIMPA")
    aplicar_fontes_localizadas(dados)
    preparar_desafios(dados)
    estado = "INICIO"
    estado_anterior = None
    anim_menu_tempo = 0

    gerenciador_sons = GerenciadorSons()
    pool_manager = PoolManager()
    diretor_sequencias = DiretorRotasBioma(DiretorReflexos(DiretorAutorais(AuditorVariedade(DiretorSequencias()))))
    diretor_perseguidores = DiretorPerseguidores()
    diretor_eventos_raros = DiretorEventosRaros(lambda: dados.get('idioma', 'pt_BR'))
    musica_diretor = DiretorMusical()
    camera_cinematica = CameraCinematica()
    cenas_epicas = CenasMemoraveis()
    replay_morte = ReplayCinematografico()
    aprendizado_contextual = AprendizadoContextual()
    desafio_compartilhado = DesafioPercurso()
    palavra_partida = PalavraDaPartida()
    codigo_editavel = codigo_diario()[3:]
    _instalar_preparacao_2778()
    from pixelrush_buffers_prod_v327710 import instalar as _instalar_buffers_prod_2779
    _instalar_buffers_prod_2779()
    paisagem_sonora = PaisagemSonora()

    todos_sprites = pygame.sprite.Group()
    obstaculos = pygame.sprite.Group()
    perigos_especiais = pygame.sprite.Group()
    buracos = pygame.sprite.Group()
    moedas = pygame.sprite.Group()
    letras_coletaveis = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    baus_secretos = pygame.sprite.Group()
    portais_bonus = pygame.sprite.Group()
    textos_flut = pygame.sprite.Group()
    particulas = pygame.sprite.Group()

    # QA766: utiliza o pool original da engine; apenas extras ja mortos
    # sao descartados, e ambiente reutiliza dicionarios entre biomas.
    if E_ANDROID and os.environ.get('PIXELRUSH_QA_ANDROID','0')=='1':
        from pixelrush_qa_particle_reuse_v327766 import instalar as instalar_pool_particulas_qa
        instalar_pool_particulas_qa(ParallaxBackground,Particula)
    bg_parallax = ParallaxBackground()
    gamefeel = GameFeel()
    gpu_processor = GpuPostProcessor(LARGURA_VIRTUAL, ALTURA_VIRTUAL,
                                     mode=os.environ.get("PIXELRUSH_GPU", "off"))
    # Máscaras de materiais para efeitos espaciais. Não tocam na lógica/física.
    # Só reservar ~7 MB de máscaras quando o backend GPU realmente estiver ativo.
    # O caminho Pygame (padrão em Android/MEmu) não usa estas superfícies.
    if gpu_processor.enabled:
        gpu_fxmask = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL)).convert()
        gpu_normal = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL)).convert()
        gpu_material = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL)).convert()
        gpu_flow = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL)).convert()
        gpu_geometry = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL)).convert()
    else:
        gpu_fxmask = gpu_normal = gpu_material = gpu_flow = gpu_geometry = None
    clima = SistemaClima()
    clima_tipo_anterior = clima.tipo
    eventos_vulcao_rodada = 0
    cenario_atual = "cidade"
    cenario_tempo_restante = random.randint(80, 140) * 60
    transicao_cenario_timer = 0
    cenario_transicao_nome = "CIDADE"
    overlay_transicao = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL)).convert()
    overlay_transicao.fill((10, 14, 27))
    portal_transition_surface = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL), pygame.SRCALPHA)
    missoes_atuais = gerar_missoes_rodada()

    jogador = None
    tutorial_corrida = None  # Uma só corrida normal, primeira partida obrigatória
    palavra_hud_ate = 0
    palavra_festa_ate = 0
    tutorial_concluido_ate = 0
    entrada_corrida_ate = 0
    pontuacao = 0
    # Valores iniciais seguros antes do primeiro tick fixo da corrida.
    vel_base = 6.0
    vel_jogo = 6.0
    moedas_coletadas = 0
    novo_recorde_alcançado = False
    # Combo: janela de 3 s a 60 Hz, melhor sequência e estatísticas da rodada.
    combo_contagem = 0
    combo_timer = 0
    combo_melhor = 0
    combo_quase_colisoes = 0
    esquivas_perfeitas = 0
    efeito_esquiva_ate = 0
    febre_carga = 0
    febre_timer = 0
    febre_turbo_distancia_restante = 0
    febre_ativacoes_rodada = 0
    baus_abertos_rodada = 0
    portal_tipo_ativo = None
    portal_proximo_metro = 700
    portal_transicao_timer = 0
    portal_transicao_tipo = "ENTRANDO"
    portal_timer = 0
    portal_y = ALTURA_VIRTUAL - 180
    portal_vy = 0.0
    portal_pontos = 0
    portal_pipes = []
    portal_pipe_spawn = 0
    portal_falhou = False
    portal_chefe_ativo = False
    portal_chefe_hp = 0
    portal_chefe_ataque = 0
    portal_chefe_faixa = 0
    portal_chefe_fase = 1
    portal_chefe_avisos = 0
    chefes_derrotados_rodada = 0
    bioma_lendario_ativo = None
    bioma_lendario_timer = 0
    biomas_lendarios_rodada = 0
    reliquia_escudo_usada = False
    fases_bonus_rodada = 0
    bioma_metros_rodada = {"cidade": 0, "deserto": 0, "neve": 0, "vulcao": 0, "cidade_futurista": 0, "floresta": 0, "reino_submerso": 0, "ilhas_celestes": 0}
    pet_salvou_vida_rodada = False
    moedas_pet_contador = 0
    obstaculos_destruidos_rodada = 0
    portal_tipo_contagem_rodada = {"AQUATICO": 0, "LASERS": 0}
    desafio_laser_ativo = False
    desafio_laser_timer = 0
    desafio_laser_cooldown = 420
    desafio_laser_spawn = 0
    desafio_laser_y = float(ALTURA_VIRTUAL - 180)
    desafio_laser_vy = 0.0
    desafio_laser_faixas = []
    desafio_laser_etapa = 0
    jetpack_laser_avancado = LaserJetpackAvancado(LARGURA_VIRTUAL)
    aba_loja = "SKINS"
    frame_count = 0
    pet_inicio_morte_frame = None  # animação apenas visual, em ticks da simulação fixa
    pet_pouso_ate = 0
    pet_alivio_ate = 0
    pet_alerta_anterior = False
    pet_pos_visual = None   # Seguimento suave, atualizado no tick fixo (não no render)
    pet_estado_animado = "ESPERA"
    pet_estado_animado_desde = 0
    pet_estado_animado_travado_ate = 0
    pet_anim_memoria = {}
    pet_habilidade_ate = 0
    pet_cantinho_selecionado = dados.get("pet_equipado") if dados.get("pet_equipado") in PETS_CONFIG else "BOLHA"
    pet_cantinho_acao = "ESPERA"
    pet_cantinho_acao_ate = 0
    pet_cantinho_mensagem = "Toque em um pet para conhecê-lo!"
    pet_cantinho_mensagem_ate = 0
    cache_telas_estaticas = {}
    # Um frame completo durante o gesto congelado evita recalcular 2.5D/FX
    # dezenas de vezes sem movimento (somente tutorial). Maximo 450x800 RGB.
    cache_tutorial_congelado = None
    # QA Android: reutiliza o pano de fundo; fisica/HUD/sprites continuam atuais.
    if E_ANDROID:
        from pixelrush_qa_ultraleve_v327730 import CacheFundoUltraQA, FundoMenusUltraQA
        # QA778: amortizar o passe 2.5D no Android, sem tocar na simulacao.
        # 8 quadros: menos reconstrucoes pesadas; a textura de fundo pode
        # avancar em passos temporais maiores. Rollback: PIXELRUSH_QA_FUNDO_PERIODO=5.
        periodo_fundo_qa = 5 if os.environ.get('PIXELRUSH_QA_FUNDO_PERIODO') == '5' else 8
        cache_fundo_mobile = CacheFundoUltraQA(periodo=periodo_fundo_qa)
        cache_menus_qa = FundoMenusUltraQA(periodo=5)
    else:
        cache_fundo_mobile = CacheFundoMobile()
        cache_menus_qa = None
    evento_corrida = None
    evento_corrida_x = LARGURA_VIRTUAL + 80
    evento_corrida_timer = 0
    evento_corrida_cooldown = 360
    eventos_corrida_superados = 0
    alerta_furtivo = 0
    alerta_detector_timer = 0
    interruptor_ativado = False
    modo_desenvolvedor = PIXELRUSH_DEV_BUILD
    dev_menu_anterior = "INICIO"
    mostrar_hitboxes = False  # Disponível somente na edição DEV (F8)
    dev_imortalidade = False
    dev_dinheiro_infinito = False
    dev_spawn_portal = False
    dev_spawn_metros = 180

    shake_timer = 0
    shake_intensidade = 0

    touch_start_pos = None
    touch_current_pos = None
    touch_jetpack_anchor = None
    toque_ativo = False
    controle_dedos = DedosAtivos()
    gamepad_pulo = False
    gamepad_baixo = False
    # Toque parado por alguns ticks inicia o pulo sem esperar o dedo ser solto.
    # Isso permite que o Android aplique o mesmo pulo longo do teclado no PC,
    # sem confundir imediatamente um swipe para baixo com um comando de pulo.
    touch_hold_frames = 0
    touch_jump_started = False
    touch_gesture_moved = False
    jetpack_gesto_usado = False
    mouse_drag_active = False
    mouse_drag_anchor_pos = None
    mouse_jetpack_gesto_usado = False
    # Mouse segue o mesmo reconhecimento de toque: toque curto pula, segurar pula
    # alto e arrastar para baixo agacha/desce rapidamente.
    mouse_start_pos = None
    mouse_current_pos = None
    mouse_hold_frames = 0
    mouse_jump_started = False
    mouse_gesture_moved = False
    mouse_gameplay_press = False
    mouse_input_ignored = False
    # Um swipe para baixo curto também precisa ter tempo de produzir o agachamento
    # mesmo quando DOWN/MOTION/UP chegam no mesmo lote de eventos.
    gesto_agachar_frames = 0
    spawn_bloqueado_frames = 0
    segurando_baixo_touch = False
    input_pulo_ativo = False
    input_baixo_ativo = False
    input_mouse_ativo = False
    ultimo_clique_tempo = 0

    cor_atual_ceu = list(COR_DIA)

    def aplicar_shake(frames, intensidade):
        nonlocal shake_timer, shake_intensidade
        # Vetor oposto ao impacto, retorno por mola amortecida.
        shake_timer = frames
        shake_intensidade = intensidade
        gamefeel.impacto(intensidade, direcao_x=-1.0, direcao_y=-0.23,
                         congelar=(estado == "JOGANDO"))

    def multiplicador_combo():
        if combo_contagem >= 15:
            return 5
        if combo_contagem >= 10:
            return 4
        if combo_contagem >= 6:
            return 3
        if combo_contagem >= 3:
            return 2
        return 1

    def registrar_acao_combo(tipo, x, y):
        nonlocal combo_contagem, combo_timer, combo_melhor
        nonlocal moedas_coletadas, febre_carga, febre_timer, febre_turbo_distancia_restante, febre_ativacoes_rodada
        nonlocal pet_reacao_ate, pet_habilidade_ate

        if tipo == "MOEDA" and dados.get("pet_equipado") in PETS_CONFIG:
            pet_reacao_ate = frame_count + 38
        combo_contagem += 1
        # Feedback de coleta por marco: não vibra a câmera a cada moeda.
        if tipo == "MOEDA":
            gamefeel.registrar_coleta(x, y)
            if combo_contagem % 10 == 0:
                gamefeel.impacto(1.5, direcao_x=0.4, direcao_y=-0.4, congelar=False)
        combo_timer = 180  # 3 segundos sem uma nova ação quebram a sequência.
        combo_melhor = max(combo_melhor, combo_contagem)
        mult = multiplicador_combo()
        # Barra de impulso independente da Febre: habilidade consistente carrega uma arrancada curta.
        if jogador is not None and jogador.tempo_impulso <= 0:
            jogador.carga_impulso = min(100, jogador.carga_impulso + (22 if tipo == "QUASE" else 12))
            if jogador.carga_impulso >= 100:
                jogador.carga_impulso = 0
                jogador.tempo_impulso = 120
                textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 265, "IMPULSO ATIVADO!", (100, 235, 220), "grande"))
                disparar_vibracao(0.08, dados.get("vibracao", True))

        # Cada ação relevante alimenta a barra; cheia, ativa a febre-cometa por 500 m.
        carga_pet = (1.25 + 0.05 * (nivel_pet(dados, "DRAGAO") - 1)) if dados.get("pet_equipado") == "DRAGAO" else 1.0
        if dados.get("pet_equipado") == "BEIJA_FLOR":
            carga_pet *= 1.12
        # v3.30.0: carga moderada por ações para que a Febre funcione com qualquer pet.
        # Quase-colisões recompensam mais, sem tornar a ativação imediata.
        febre_carga = min(100.0, febre_carga + (1.2 if tipo == "QUASE" else 0.75) * carga_pet / FEBRE_DIFICULDADE)
        if febre_carga >= 100 and febre_timer <= 0:
            if dados.get("pet_equipado") in ("DRAGAO", "BEIJA_FLOR"):
                pet_habilidade_ate = frame_count + 64
            febre_carga = 0
            febre_timer = 900  # 15 s de segurança; o fim real é controlado pelos 500 m do cometa.
            febre_turbo_distancia_restante = 500.0
            febre_ativacoes_rodada += 1
            textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 235, t("febre", dados), AMARELO_NEON, "grande"))
            disparar_vibracao(0.12, dados.get("vibracao", True))
            gerenciador_sons.tocar_som("novo_recorde", False, dados["vol_sfx"])
            gerenciador_sons.tocar_som("chamas", False, min(1.0, dados["vol_sfx"] * 1.15))

        if tipo == "QUASE":
            bonus_quase = max(1, mult - 1)
            moedas_coletadas += bonus_quase
            textos_flut.add(TextoFlutuante(x, y - 22, f"{t('quase_colisao', dados)} +{bonus_quase}",
                                           AMARELO_NEON, "grande"))
        elif tipo == "MOEDA" and combo_contagem % 3 == 0 and mult > 1:
            # O multiplicador recompensa a coleta contínua sem alterar a pontuação de distância.
            bonus_coleta = mult - 1
            moedas_coletadas += bonus_coleta
            # O bônus é contabilizado silenciosamente para não poluir a corrida com textos repetidos.

        if combo_contagem in (10, 20, 30, 50) and combo_contagem > 0:
            textos_flut.add(TextoFlutuante(x, y - 42, f"COMBO {combo_contagem}x!", CIANO_ESCUDO, "normal"))

        # Marcos de combo concedem moedas extras, sem alterar a distância/pontuação.
        if combo_contagem >= 5 and combo_contagem % 5 == 0:
            bonus_marco = 2 + combo_contagem // 10
            moedas_coletadas += bonus_marco
            # Os bônus de marcos são adicionados ao total sem um novo aviso a cada marco.

    EVENTO_GERAR = pygame.USEREVENT + 1
    tempo_spawn_atual = 1500
    espacamento_ameacas = EspacamentoPorDistancia()
    # Máximo de três resoluções em cache: evita acúmulo ao redimensionar no PC/MEmu.
    superficies_escala = OrderedDict()
    jetpack_bg_surface = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL)).convert()

    # Menu principal compacto: todos os botões ficam centralizados e dentro da tela.
    btn_jogar = pygame.Rect(65, 352, 320, 44)
    btn_loja = pygame.Rect(65, 410, 320, 44)
    btn_upgrades = pygame.Rect(65, 468, 320, 44)
    btn_config = pygame.Rect(65, 526, 320, 44)
    btn_recordes = pygame.Rect(65, 584, 320, 44)  # Progresso Pessoal
    btn_desafios = pygame.Rect(65, 642, 320, 44)
    btn_menu_dev = pygame.Rect(65, 708, 320, 40) if PIXELRUSH_DEV_BUILD else None
    opcoes_dev = (
        ("LIBERAR SKINS/PETS", "colecao"),
        ("MOEDAS +100.000", "moedas"),
        ("IMORTALIDADE", "imortal"),
        ("ATIVAR FEBRE", "febre"),
        ("ATIVAR TURBO", "turbo"),
        ("POWER-UPS NIVEL 1", "upgrades"),
        ("TROCAR BIOMA", "bioma"),
        ("TROCAR CLIMA", "clima"),
        ("MOSTRAR HITBOXES", "hitboxes"),
        ("INICIAR CORRIDA", "jogar"),
    ) if PIXELRUSH_DEV_BUILD else ()
    btn_dev_voltar = pygame.Rect(85, 651, 280, 48)
    btn_ranking = pygame.Rect(28, 585, 394, 42)  # Acesso dentro de Progresso Pessoal
    btn_reliquias = pygame.Rect(300, 530, 122, 44)  # Acesso dentro de Progresso Pessoal
    # Conquistas e Base do Corredor ficam dentro de Progresso Pessoal.
    btn_conquistas = pygame.Rect(28, 555, 116, 44)
    btn_base_corredor = pygame.Rect(152, 555, 140, 44)
    btn_progress_reliquias = pygame.Rect(300, 555, 122, 44)
    btn_progress_ranking = pygame.Rect(28, 610, 394, 42)
    btn_voltar_progresso = pygame.Rect(75, 610, 300, 50)
    btn_voltar_base = pygame.Rect(75, 710, 300, 50)
    btn_progress_conquistas = btn_conquistas
    btn_progress_base = btn_base_corredor
    btn_loja_pagina_ant = pygame.Rect(45, 665, 150, 32)
    btn_loja_pagina_prox = pygame.Rect(255, 665, 150, 32)
    loja_pagina = 0
    btn_aba_skins = pygame.Rect(35, 128, 180, 34)
    btn_aba_pets = pygame.Rect(235, 128, 180, 34)
    RELIQUIAS_POR_PAGINA = 5
    pagina_reliquias = 0
    btn_reliquia_ant = pygame.Rect(45, 665, 150, 32)
    btn_reliquia_prox = pygame.Rect(255, 665, 150, 32)
    item_preview_tipo = None
    item_preview_id = None
    item_preview_confirmar = False
    item_preview_surface = None
    item_preview_estilo = 1
    animacao_recompensa = None
    inicio_tela_resultados = None
    pet_reacao_ate = 0
    rect_preview_popup = pygame.Rect(24, 112, 402, 566)
    btn_preview_voltar = pygame.Rect(40, 614, 170, 44)
    btn_preview_compra = pygame.Rect(240, 614, 170, 44)
    btn_preview_estilo_ant = pygame.Rect(54, 246, 48, 48)
    btn_preview_estilo_prox = pygame.Rect(348, 246, 48, 48)
    pagina_recordes_biomas = 0
    bioma_recorde_popup = None
    btn_recorde_bioma_ant = pygame.Rect(282, 453, 36, 30)
    btn_recorde_bioma_prox = pygame.Rect(323, 453, 36, 30)
    rect_recorde_bioma_popup = pygame.Rect(24, 138, 402, 520)
    btn_recorde_bioma_fechar = pygame.Rect(140, 601, 170, 40)
    btn_ach_ant = pygame.Rect(45, 625, 150, 34)
    btn_ach_prox = pygame.Rect(255, 625, 150, 34)
    pagina_conquistas = 0
    pagina_upgrades = 0
    UPGRADES_POR_PAGINA = 4
    btn_upgrade_ant = pygame.Rect(35, 625, 175, 38)
    btn_upgrade_prox = pygame.Rect(240, 625, 175, 38)
    PETS_POR_PAGINA = 5
    btn_cantinho_pets = pygame.Rect(75, 616, 300, 40)
    btn_cantinho_voltar = pygame.Rect(75, 710, 300, 48)
    btn_cantinho_carinho = pygame.Rect(24, 643, 124, 48)
    btn_cantinho_brincar = pygame.Rect(163, 643, 124, 48)
    btn_cantinho_equipar = pygame.Rect(302, 643, 124, 48)

    # Tela opcional de desafio de percurso — sem alterar missões existentes.
    btn_percurso_abrir = pygame.Rect(60, 550, 330, 57)
    btn_percurso_diario = pygame.Rect(55, 201, 340, 57)
    btn_percurso_codigo = pygame.Rect(55, 474, 340, 58)
    btn_percurso_voltar = pygame.Rect(75, 680, 300, 54)
    digitos_percurso = [pygame.Rect(42 + i*62, 334, 54, 65) for i in range(6)]

    btn_voltar = pygame.Rect(75, 710, 300, 50)
    btn_reiniciar = pygame.Rect(75, 540, 300, 50)
    btn_menu_gameover = pygame.Rect(75, 610, 300, 50)

    btn_pausa = pygame.Rect(HUD_PAUSA_AREA)
    btn_continuar = pygame.Rect(75, 530, 300, 50)
    btn_menu_pausa = pygame.Rect(75, 600, 300, 50)

    # UI Configurações
    btn_musica_menos = pygame.Rect(75, 180, 60, 45)
    btn_musica_mais = pygame.Rect(315, 180, 60, 45)
    btn_sfx_menos = pygame.Rect(75, 275, 60, 45)
    btn_sfx_mais = pygame.Rect(315, 275, 60, 45)
    btn_vibracao = pygame.Rect(75, 355, 300, 50)
    btn_lang = pygame.Rect(75, 425, 300, 50)
    btn_modo_grafico = pygame.Rect(75, 495, 300, 50)
    btn_rastro_visual = pygame.Rect(75, 555, 300, 50)
    btn_ajuda_pulo = pygame.Rect(57, 408, 336, 56)  # v3.171: painel de controles
    btn_config_controles = pygame.Rect(75, 610, 300, 34)
    controles_rects = {
        'modo': pygame.Rect(57, 192, 336, 56),
        'sensibilidade': pygame.Rect(57, 258, 336, 56),
        'canhoto': pygame.Rect(57, 324, 336, 56),
        'ajuda': btn_ajuda_pulo,
        'gamepad': pygame.Rect(57, 484, 336, 56),
        'voltar': pygame.Rect(75, 632, 300, 58),
    }
    btn_voltar_config = pygame.Rect(75, 525, 300, 50)
    btn_acessibilidade = pygame.Rect(75, 712, 300, 43)
    acess_rects = {
        'acess_contraste': pygame.Rect(52, 192, 346, 72),
        'acess_sinais': pygame.Rect(52, 281, 346, 72),
        'acess_reduzir_efeitos': pygame.Rect(52, 370, 346, 72),
        'voltar': pygame.Rect(75, 650, 300, 56),
    }

    def reiniciar_jogo():
        nonlocal tutorial_corrida, palavra_hud_ate, palavra_festa_ate, tutorial_concluido_ate, entrada_corrida_ate
        tutorial_corrida = None
        palavra_hud_ate = palavra_festa_ate = tutorial_concluido_ate = 0
        entrada_corrida_ate = frame_count + 70
        global portal_proximo_metro
        portal_proximo_metro = 700
        gamefeel.reiniciar()
        replay_morte.limpar()
        aprendizado_contextual.limpar()
        nonlocal jogador, pontuacao, moedas_coletadas, novo_recorde_alcançado, missoes_atuais, cor_atual_ceu, tempo_spawn_atual, estado
        nonlocal combo_contagem, combo_timer, combo_melhor, combo_quase_colisoes
        nonlocal febre_carga, febre_timer, febre_turbo_distancia_restante, febre_ativacoes_rodada, baus_abertos_rodada
        nonlocal portal_tipo_ativo, portal_timer, portal_y, portal_vy, portal_pontos, portal_pipes, portal_pipe_spawn, portal_falhou
        nonlocal portal_chefe_ativo, portal_chefe_hp, portal_chefe_ataque, portal_chefe_faixa, portal_chefe_fase, portal_chefe_avisos, chefes_derrotados_rodada
        nonlocal bioma_lendario_ativo, bioma_lendario_timer, biomas_lendarios_rodada, reliquia_escudo_usada
        nonlocal fases_bonus_rodada, bioma_metros_rodada
        nonlocal cenario_atual, cenario_tempo_restante, transicao_cenario_timer, cenario_transicao_nome, spawn_bloqueado_frames
        nonlocal pet_salvou_vida_rodada, moedas_pet_contador, portal_tipo_contagem_rodada, obstaculos_destruidos_rodada
        nonlocal clima_tipo_anterior, eventos_vulcao_rodada, pet_reacao_ate
        nonlocal pet_pos_visual, pet_estado_animado, pet_habilidade_ate
        nonlocal pet_pouso_ate, pet_alivio_ate, pet_alerta_anterior
        nonlocal pet_estado_animado_desde, pet_estado_animado_travado_ate, pet_anim_memoria
        nonlocal desafio_laser_ativo, desafio_laser_timer, desafio_laser_cooldown, desafio_laser_spawn
        nonlocal desafio_laser_y, desafio_laser_vy, desafio_laser_faixas, desafio_laser_etapa
        # Um corredor iniciado na corrida anterior nao pode continuar em outra.
        desafio_laser_ativo = False
        desafio_laser_timer = 0
        desafio_laser_cooldown = 420
        desafio_laser_spawn = 0
        desafio_laser_y = float(ALTURA_VIRTUAL - 180)
        desafio_laser_vy = 0.0
        desafio_laser_faixas = []
        desafio_laser_etapa = 0
        jetpack_laser_avancado.reiniciar()
        pet_pouso_ate = 0
        pet_alivio_ate = 0
        pet_alerta_anterior = False
        pet_pos_visual = None
        pet_estado_animado = "ESPERA"
        pet_estado_animado_desde = 0
        pet_estado_animado_travado_ate = 0
        pet_anim_memoria = {}
        pet_habilidade_ate = 0
        pet_reacao_ate = 0
        # Mate os sprites, em vez de apenas esvaziar os grupos. Moedas e
        # particulas devolvem-se assim aos seus pools para serem reutilizadas
        # nas partidas seguintes, sem acumular objetos abandonados.
        for grupo in (todos_sprites, obstaculos, perigos_especiais, buracos, moedas, letras_coletaveis, powerups, baus_secretos,
                      portais_bonus, textos_flut, particulas):
            for sprite_antigo in grupo.sprites():
                sprite_antigo.kill()
        todos_sprites.empty()
        obstaculos.empty()
        perigos_especiais.empty()
        buracos.empty()
        moedas.empty()
        letras_coletaveis.empty()
        powerups.empty()
        baus_secretos.empty()
        portais_bonus.empty()
        textos_flut.empty()
        particulas.empty()

        skin_nome_atual = dados["skin_equipada"]
        cor_jogador = SKINS.get(skin_nome_atual, SKINS["AZUL"])["cor"]
        jogador = Jogador(skin_nome_atual, cor_jogador, dados["upgrades"])
        jogador.ajuda_pulo = bool(dados.get('ajuda_pulo', True))
        jogador.estilo_visual = 1
        todos_sprites.add(jogador)

        pontuacao = 0
        moedas_coletadas = 0
        palavra_partida.iniciar()
        novo_recorde_alcançado = False
        combo_contagem = 0
        combo_timer = 0
        combo_melhor = 0
        combo_quase_colisoes = 0
        esquivas_perfeitas = 0
        efeito_esquiva_ate = 0
        febre_carga = 0
        febre_timer = 0
        febre_turbo_distancia_restante = 0
        febre_ativacoes_rodada = 0
        baus_abertos_rodada = 0
        portal_tipo_ativo = None
        portal_timer = 0
        portal_y = ALTURA_VIRTUAL - 180
        portal_vy = 0.0
        portal_pontos = 0
        portal_pipes = []
        portal_pipe_spawn = 0
        portal_falhou = False
        portal_chefe_ativo = False
        portal_chefe_hp = 0
        portal_chefe_ataque = 0
        portal_chefe_faixa = 0
        portal_chefe_fase = 1
        portal_chefe_avisos = 0
        chefes_derrotados_rodada = 0
        bioma_lendario_ativo = None
        bioma_lendario_timer = 0
        biomas_lendarios_rodada = 0
        reliquia_escudo_usada = False
        fases_bonus_rodada = 0
        bioma_metros_rodada = {"cidade": 0, "deserto": 0, "neve": 0, "vulcao": 0, "cidade_futurista": 0, "floresta": 0, "reino_submerso": 0, "ilhas_celestes": 0}
        pet_salvou_vida_rodada = False
        moedas_pet_contador = 0
        obstaculos_destruidos_rodada = 0
        portal_tipo_contagem_rodada = {"AQUATICO": 0, "LASERS": 0}
        pet_inicio_id = dados.get("pet_equipado", "")
        if pet_inicio_id == "RAPOSA":
            jogador.escudo_hits += 1 + (nivel_pet(dados, "RAPOSA") - 1) // 2
            pet_habilidade_ate = frame_count + 65
        elif pet_inicio_id == "GOLEM":
            jogador.escudo_hits += 2 + (nivel_pet(dados, "GOLEM") - 1) // 2
            pet_habilidade_ate = frame_count + 65
        if dados.get("reliquia_equipada") == "CORACAO_FENIX" and int(dados.get("estatisticas_permanentes", {}).get("partidas", 0)) % 3 == 2:
            jogador.escudo_hits += 1
        # Opt-in: só desafios escolhidos reinicializam a semente global.
        desafio_compartilhado.preparar_corrida()
        missoes_atuais = gerar_missoes_rodada()
        diretor_sequencias.reiniciar()
        diretor_perseguidores.reiniciar(random.getstate())
        diretor_eventos_raros.reiniciar(random.getstate())
        cor_atual_ceu = list(COR_DIA)
        cenario_atual = "cidade"
        cenario_tempo_restante = random.randint(80, 140) * 60
        bg_parallax.set_cenario(cenario_atual)
        clima.trocar_cenario(cenario_atual, inicial=True)
        clima_tipo_anterior = clima.tipo
        eventos_vulcao_rodada = 0
        transicao_cenario_timer = 0
        cenario_transicao_nome = nome_cenario(cenario_atual)
        tempo_spawn_atual = 1500
        spawn_bloqueado_frames = 150 if tutorial_corrida is not None else 70
        pet5_precarregar(dados.get('pet_equipado'))
        pygame.time.set_timer(EVENTO_GERAR, tempo_spawn_atual)
        estado = "JOGANDO"
        metricas_corrida.iniciar(skin=skin_nome_atual, pet=pet_inicio_id, bioma=cenario_atual, quadro=frame_count)

    def iniciar_desafio_laser():
        nonlocal desafio_laser_ativo, desafio_laser_timer, desafio_laser_cooldown, desafio_laser_spawn
        nonlocal desafio_laser_y, desafio_laser_vy, desafio_laser_faixas, spawn_bloqueado_frames
        desafio_laser_ativo = True
        desafio_laser_timer = random.randint(300, 420)
        desafio_laser_cooldown = random.randint(900, 1320)
        desafio_laser_spawn = 12
        desafio_laser_y = float(max(ALTURA_VIRTUAL - 250, min(ALTURA_VIRTUAL - 150, jogador.rect.centery)))
        desafio_laser_vy = 0.0
        desafio_laser_faixas = []
        spawn_bloqueado_frames = max(spawn_bloqueado_frames, desafio_laser_timer + 45)
        for grupo_limpeza in (obstaculos, perigos_especiais, buracos, powerups):
            for item_limpeza in list(grupo_limpeza):
                item_limpeza.kill()
        textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 205, "CORREDOR LASER!", (120, 240, 255), "grande"))

    def encerrar_desafio_laser(sucesso=True):
        nonlocal desafio_laser_ativo, desafio_laser_timer, desafio_laser_spawn, desafio_laser_vy, desafio_laser_faixas
        desafio_laser_ativo = False
        desafio_laser_timer = 0
        desafio_laser_spawn = 0
        desafio_laser_vy = 0.0
        desafio_laser_faixas = []
        if sucesso:
            textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 205, "CORREDOR CONCLUÍDO!", (255, 225, 120), "normal"))

    def processar_clique_ui(pos):
        nonlocal tutorial_corrida
        nonlocal codigo_editavel
        nonlocal estado, ultimo_clique_tempo, aba_loja, loja_pagina, pagina_conquistas, pagina_upgrades
        nonlocal dev_menu_anterior, dev_imortalidade, dev_dinheiro_infinito, mostrar_hitboxes
        nonlocal febre_carga, febre_timer, febre_turbo_distancia_restante, cenario_atual, cenario_tempo_restante
        nonlocal transicao_cenario_timer, cenario_transicao_nome, bioma_lendario_ativo
        nonlocal pagina_reliquias, item_preview_tipo, item_preview_id, item_preview_confirmar, item_preview_surface, item_preview_estilo, anim_menu_tempo, animacao_recompensa
        nonlocal pagina_recordes_biomas, bioma_recorde_popup
        nonlocal pet_cantinho_selecionado, pet_cantinho_acao, pet_cantinho_acao_ate
        nonlocal pet_cantinho_mensagem, pet_cantinho_mensagem_ate
        # v3.92.0: nenhuma ação de pet pode atravessar a tela de suspensão.
        if estado == "LOJA" and aba_loja == "PETS":
            if btn_voltar.collidepoint(pos):
                estado = "INICIO"
            return
        tempo_atual = _rep_tempo(pygame.time.get_ticks())
        if tempo_atual - ultimo_clique_tempo < 300:
            return
        ultimo_clique_tempo = tempo_atual

        gerenciador_sons.tocar_som("clique", False, dados["vol_sfx"])
        if PIXELRUSH_DEV_BUILD and estado == "DEV_MENU":
            if btn_dev_voltar.collidepoint(pos):
                estado = dev_menu_anterior
                return
            for indice, (rotulo, acao) in enumerate(opcoes_dev):
                coluna, linha = indice % 2, indice // 2
                rect_acao = pygame.Rect(25 + coluna * 208, 247 + linha * 67, 191, 49)
                if not rect_acao.collidepoint(pos):
                    continue
                if acao == "colecao":
                    dev_desbloquear_colecao_completa(dados)
                elif acao == "moedas":
                    dados["moedas_totais"] = int(dados.get("moedas_totais", 0)) + 100000
                    salvar_dados(dados)
                elif acao == "imortal":
                    dev_imortalidade = not dev_imortalidade
                elif acao == "febre":
                    if jogador is None:
                        reiniciar_jogo()
                        estado = "DEV_MENU"
                    febre_carga = 0
                    febre_timer = 900
                    febre_turbo_distancia_restante = 500.0
                    if jogador is not None:
                        jogador.morrendo = False
                elif acao == "turbo":
                    if jogador is None:
                        reiniciar_jogo()
                        estado = "DEV_MENU"
                    if jogador is not None:
                        jogador.tempo_turbo = 600
                        jogador.morrendo = False
                elif acao == "upgrades":
                    for nome in UPGRADES_CONFIG:
                        dados.setdefault("upgrades", {})[nome] = max(1, int(dados.get("upgrades", {}).get(nome, 0)))
                    salvar_dados(dados)
                elif acao == "bioma":
                    biomas = ["cidade", "deserto", "neve", "vulcao", "cidade_futurista", "floresta", "ilhas_celestes"]
                    indice_b = biomas.index(cenario_atual) if cenario_atual in biomas else -1
                    cenario_atual = biomas[(indice_b + 1) % len(biomas)]
                    bg_parallax.set_cenario(cenario_atual)
                    clima.trocar_cenario(cenario_atual)
                    cenario_tempo_restante = 999999
                    transicao_cenario_timer = 90
                    cenario_transicao_nome = nome_cenario(cenario_atual)
                    bioma_lendario_ativo = None
                elif acao == "clima":
                    climas = ("limpo", "chuva", "vento", "tempestade", "neve")
                    indice_c = climas.index(clima.tipo) if clima.tipo in climas else -1
                    clima.tipo = climas[(indice_c + 1) % len(climas)]
                elif acao == "hitboxes":
                    mostrar_hitboxes = not mostrar_hitboxes
                    cache_telas_estaticas.clear()
                elif acao == "jogar":
                    if jogador is None or jogador.morrendo:
                        reiniciar_jogo()
                    estado = "JOGANDO"
                return
            return
        if estado == "INICIO":
            if PIXELRUSH_DEV_BUILD and btn_menu_dev.collidepoint(pos):
                dev_menu_anterior = "INICIO"
                estado = "DEV_MENU"
                return
            if btn_jogar.collidepoint(pos):
                # Primeira partida: tutorial NO MESMO estado JOGANDO, sem tela
                # intermediária, com o Jogador/cenário/itens existentes.
                # Nenhuma tecla/gesto pula etapa ou marca save prematuramente.
                desafio_compartilhado.cancelar()
                reiniciar_jogo()
                if not qa_sem_abertura() and precisa_tutorial(dados):
                    tutorial_corrida = TutorialCorrida(
                        jogador, LARGURA_VIRTUAL, ALTURA_VIRTUAL,
                        classe_terrestre=ObstaculoTerrestre,
                        classe_voador=ObstaculoVoador, classe_moeda=Moeda,
                        classe_cidade=AmeacaBioma, classe_hidrante=HidranteCidade,
                        idioma=dados.get('idioma','pt_BR'))
            elif btn_loja.collidepoint(pos):
                estado = "LOJA"
            elif btn_upgrades.collidepoint(pos):
                estado = "UPGRADES"
            elif btn_config.collidepoint(pos):
                estado = "CONFIG"
            elif btn_recordes.collidepoint(pos):
                estado = "RECORDES"
            elif btn_desafios.collidepoint(pos):
                estado = "DESAFIOS"


        elif estado == "CANTINHO_PETS":
            if btn_cantinho_voltar.collidepoint(pos):
                estado = "LOJA"
                aba_loja = "PETS"
                loja_pagina = 0
            else:
                id_escolhido = None
                for i_pet, pet_id in enumerate(PETS_CONFIG):
                    rect_carta = pygame.Rect(12+(i_pet%3)*142, 144+(i_pet//3)*94, 134, 84)
                    if rect_carta.collidepoint(pos):
                        id_escolhido = pet_id
                        break
                if id_escolhido:
                    pet_cantinho_selecionado = id_escolhido
                    pet_cantinho_acao = "ESPERA"
                    pet_cantinho_mensagem = ("Pronto para brincar!" if id_escolhido in dados.get("pets_desbloqueados", [])
                                           else "Desbloqueie este pet na loja!")
                    pet_cantinho_mensagem_ate = frame_count + 160
                elif btn_cantinho_carinho.collidepoint(pos) or btn_cantinho_brincar.collidepoint(pos):
                    interacao = "carinho" if btn_cantinho_carinho.collidepoint(pos) else "brincar"
                    sucesso, pet_cantinho_mensagem = interagir_com_pet(dados, pet_cantinho_selecionado, interacao)
                    pet_cantinho_acao = "CARINHO" if interacao == "carinho" else "BRINCAR"
                    pet_cantinho_acao_ate = frame_count + 110
                    pet_cantinho_mensagem_ate = frame_count + 155
                    if sucesso:
                        salvar_dados(dados)
                elif btn_cantinho_equipar.collidepoint(pos):
                    if pet_cantinho_selecionado in dados.get("pets_desbloqueados", []):
                        dados["pet_equipado"] = pet_cantinho_selecionado
                        salvar_dados(dados)
                        pet_cantinho_mensagem = "Companheiro equipado!"
                    else:
                        pet_cantinho_mensagem = "Desbloqueie este pet na loja!"
                    pet_cantinho_mensagem_ate = frame_count + 140

        elif estado == "DESAFIO_PERCURSO":
            if btn_percurso_voltar.collidepoint(pos):
                estado = "DESAFIOS"
            elif btn_percurso_diario.collidepoint(pos):
                desafio_compartilhado.escolher(codigo_diario())
                reiniciar_jogo()
            elif btn_percurso_codigo.collidepoint(pos):
                desafio_compartilhado.escolher('PR-' + codigo_editavel)
                reiniciar_jogo()
            else:
                for idx, caixa in enumerate(digitos_percurso):
                    if caixa.collidepoint(pos):
                        codigo_editavel = (codigo_editavel[:idx] + str((int(codigo_editavel[idx])+1) % 10)
                                          + codigo_editavel[idx+1:])
                        break

        elif estado in ("CONQUISTAS", "RECORDES", "DESAFIOS", "RANKING"):
            if estado == "RECORDES" and bioma_recorde_popup is not None:
                if btn_recorde_bioma_fechar.collidepoint(pos) or not rect_recorde_bioma_popup.collidepoint(pos):
                    bioma_recorde_popup = None
            elif estado == "RECORDES" and btn_recorde_bioma_ant.collidepoint(pos):
                pagina_recordes_biomas = max(0, pagina_recordes_biomas - 1)
            elif estado == "RECORDES" and btn_recorde_bioma_prox.collidepoint(pos):
                max_paginas_biomas = (len(BIOMAS_RECORDES_UI) + 2) // 3
                pagina_recordes_biomas = min(max_paginas_biomas - 1, pagina_recordes_biomas + 1)
            elif estado == "RECORDES" and any(
                    pygame.Rect(28 + indice_bioma * 134, 489, 126, 58).collidepoint(pos)
                    for indice_bioma, _ in enumerate(
                        BIOMAS_RECORDES_UI[pagina_recordes_biomas * 3:(pagina_recordes_biomas + 1) * 3])):
                visiveis_biomas = BIOMAS_RECORDES_UI[pagina_recordes_biomas * 3:(pagina_recordes_biomas + 1) * 3]
                for indice_bioma, (id_bioma, rotulo_bioma) in enumerate(visiveis_biomas):
                    rect_card_bioma = pygame.Rect(28 + indice_bioma * 134, 489, 126, 58)
                    if rect_card_bioma.collidepoint(pos):
                        bioma_recorde_popup = id_bioma
                        break
            elif estado == "CONQUISTAS" and btn_ach_ant.collidepoint(pos):
                pagina_conquistas = max(0, pagina_conquistas - 1)
            elif estado == "CONQUISTAS" and btn_ach_prox.collidepoint(pos):
                pagina_conquistas = min((len(CONQUISTAS_CONFIG) - 1) // 5, pagina_conquistas + 1)
            elif estado == "RECORDES" and btn_voltar_progresso.collidepoint(pos):
                estado = "INICIO"
            elif estado == "DESAFIOS" and btn_percurso_abrir.collidepoint(pos):
                codigo_editavel = codigo_diario()[3:]
                estado = "DESAFIO_PERCURSO"
            elif btn_voltar.collidepoint(pos):
                estado = "RECORDES" if estado == "RANKING" else "INICIO"

        elif estado == "BASE_CORREDOR":
            if btn_voltar_base.collidepoint(pos):
                estado = "INICIO"
            else:
                # A Base evolui apenas visualmente; não concede bônus de atributos.
                base = dados.setdefault("base_corredor", {"nivel": 1, "trofeus": [], "decoracao": 0, "mecanicas_descobertas": []})
                base["nivel"] = max(1, min(5, 1 + int(dados.get("estatisticas_permanentes", {}).get("partidas", 0)) // 10))
                base["decoracao"] = max(0, min(4, base["nivel"] - 1))
                salvar_dados(dados)

        elif estado == "RELIQUIAS":
            total_paginas_rel = (len(RELIQUIAS_CONFIG) + RELIQUIAS_POR_PAGINA - 1) // RELIQUIAS_POR_PAGINA
            if btn_voltar.collidepoint(pos):
                estado = "RECORDES"
            elif btn_reliquia_ant.collidepoint(pos):
                pagina_reliquias = max(0, pagina_reliquias - 1)
            elif btn_reliquia_prox.collidepoint(pos):
                pagina_reliquias = min(total_paginas_rel - 1, pagina_reliquias + 1)
            else:
                stats_rel = dados.get("estatisticas_permanentes", {})
                stats_extra = dados.get("estatisticas_novas", {})
                reliquias_visiveis = list(RELIQUIAS_CONFIG.items())[pagina_reliquias * RELIQUIAS_POR_PAGINA:(pagina_reliquias + 1) * RELIQUIAS_POR_PAGINA]
                y_rel = 112
                for rid, info_rel in reliquias_visiveis:
                    rect_rel = pygame.Rect(28, y_rel, 394, 94)
                    if rect_rel.collidepoint(pos):
                        progresso_rel = int(stats_extra.get(info_rel["stat"], stats_rel.get(info_rel["stat"], 0)))
                        if rid not in dados.setdefault("reliquias_desbloqueadas", []) and progresso_rel >= info_rel["alvo"]:
                            dados["reliquias_desbloqueadas"].append(rid)
                        if rid in dados.get("reliquias_desbloqueadas", []):
                            dados["reliquia_equipada"] = rid
                            salvar_dados(dados)
                        break
                    y_rel += 101

        elif estado == "CONFIG_ACESSIBILIDADE":
            if acess_rects['voltar'].collidepoint(pos):
                salvar_dados(dados)
                estado = 'CONFIG'
            else:
                for chave_acess in ('acess_contraste', 'acess_sinais', 'acess_reduzir_efeitos'):
                    if acess_rects[chave_acess].collidepoint(pos):
                        dados[chave_acess] = not dados.get(chave_acess, False)
                        salvar_dados(dados)
                        break

        elif estado == "CONFIG_CONTROLES":
            if controles_rects['voltar'].collidepoint(pos):
                salvar_dados(dados)
                estado = 'CONFIG'
            elif controles_rects['modo'].collidepoint(pos):
                atual = normalizar_modo(dados.get('controle_modo', 'CLASSICO'))
                dados['controle_modo'] = MODOS[(MODOS.index(atual)+1) % len(MODOS)]
                controle_dedos.reset()
                salvar_dados(dados)
            elif controles_rects['sensibilidade'].collidepoint(pos):
                atual = limiar(dados)
                dados['sensibilidade_toque'] = SENSIBILIDADES[(SENSIBILIDADES.index(atual)+1) % len(SENSIBILIDADES)]
                salvar_dados(dados)
            elif controles_rects['canhoto'].collidepoint(pos):
                dados['controle_canhoto'] = not dados.get('controle_canhoto', False)
                salvar_dados(dados)
            elif controles_rects['ajuda'].collidepoint(pos):
                dados['ajuda_pulo'] = not dados.get('ajuda_pulo', True)
                if jogador is not None:
                    jogador.ajuda_pulo = dados['ajuda_pulo']
                    if not jogador.ajuda_pulo:
                        jogador.coyote_ticks = jogador.buffer_pulo_ticks = 0
                salvar_dados(dados)
            elif controles_rects['gamepad'].collidepoint(pos):
                dados['gamepad_ativo'] = not dados.get('gamepad_ativo', True)
                salvar_dados(dados)

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
                dados["idioma"] = _i18n247.proximo_idioma(dados.get("idioma", "pt_BR"))
                aplicar_fontes_localizadas(dados)
                salvar_dados(dados)
            # Opção de rastro removida da interface desta edição.

        elif estado == "JOGANDO":
            if btn_pausa.collidepoint(pos):
                estado = "PAUSA"

        elif estado == "PAUSA":
            if btn_continuar.collidepoint(pos):
                estado = "JOGANDO"
            elif btn_menu_pausa.collidepoint(pos):
                estado = "INICIO"

        elif estado == "GAMEOVER":
            if replay_morte.ativo:
                replay_morte.pular()
                return
            if pygame.Rect(124, 683, 202, 45).collidepoint(pos):
                replay_morte.iniciar()
                return
            if btn_reiniciar.collidepoint(pos):
                reiniciar_jogo()
            elif btn_menu_gameover.collidepoint(pos):
                desafio_compartilhado.cancelar()
                replay_morte.limpar()
                paisagem_sonora.parar()
                estado = "INICIO"

        elif estado in ["LOJA", "UPGRADES"]:
            if estado == "LOJA" and item_preview_tipo:
                # O pop-up bloqueia interações com os elementos que ficam atrás dele.
                if btn_preview_voltar.collidepoint(pos) or not rect_preview_popup.collidepoint(pos):
                    item_preview_tipo = None
                    item_preview_id = None
                    item_preview_confirmar = False
                    item_preview_surface = None
                    item_preview_estilo = 1
                elif False and item_preview_tipo == "SKIN" and btn_preview_estilo_ant.collidepoint(pos):
                    item_preview_estilo = max(1, item_preview_estilo - 1)
                    item_preview_surface = None
                elif False and item_preview_tipo == "SKIN" and btn_preview_estilo_prox.collidepoint(pos):
                    item_preview_estilo = min(8, item_preview_estilo + 1)
                    item_preview_surface = None
                elif btn_preview_compra.collidepoint(pos):
                    # Cada estilo alternativo é uma compra independente da skin base.
                    if (False and item_preview_tipo == "SKIN" and item_preview_estilo > 1
                            and item_preview_id in dados.get("skins_desbloqueadas", ["AZUL"])):
                        estilos = dados.setdefault("estilos_skins_comprados", {})
                        comprados = estilos.setdefault(item_preview_id, [1])
                        custo_estilo = 500 * item_preview_estilo
                        objetivos_estilo = {
                            2: ("ROBÔ: destrua 100 obstáculos", int(dados.get("estatisticas_permanentes", {}).get("obstaculos_destruidos", 0)) >= 100),
                            3: ("ZUMBI: sobreviva a 30 corridas", int(dados.get("estatisticas_permanentes", {}).get("partidas", 0)) >= 30),
                            4: ("NEON: percorra 5.000 m", int(dados.get("estatisticas_permanentes", {}).get("distancia_total", 0)) >= 5000),
                            5: ("GELO: conclua 10 portais", int(dados.get("estatisticas_permanentes", {}).get("fases_bonus", 0)) >= 10),
                            6: ("FOGO: alcance combo 50", int(dados.get("estatisticas_permanentes", {}).get("melhor_combo", 0)) >= 50),
                            7: ("DOURADO: colete 10.000 moedas", int(dados.get("estatisticas_permanentes", {}).get("moedas_coletadas", 0)) >= 10000),
                            8: ("PRISMÁTICO: alcance 20.000 m totais", int(dados.get("estatisticas_permanentes", {}).get("distancia_total", 0)) >= 20000),
                        }
                        if item_preview_estilo in objetivos_estilo and not objetivos_estilo[item_preview_estilo][1]:
                            item_preview_confirmar = False
                            textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 250, "OBJETIVO: " + objetivos_estilo[item_preview_estilo][0], (255, 210, 90), "grande"))
                            return
                        if item_preview_estilo in comprados:
                            dados.setdefault("estilo_skin_equipado", {})[item_preview_id] = item_preview_estilo
                            salvar_dados(dados)
                            item_preview_confirmar = False
                            item_preview_surface = None
                        elif int(dados.get("moedas_totais", 0)) >= custo_estilo:
                            if not item_preview_confirmar:
                                item_preview_confirmar = True
                            else:
                                dados["moedas_totais"] -= custo_estilo
                                comprados.append(item_preview_estilo)
                                dados.setdefault("estilo_skin_equipado", {})[item_preview_id] = item_preview_estilo
                                salvar_dados(dados)
                                item_preview_confirmar = False
                                item_preview_surface = None
                        # A compra de estilo não executa também a compra da skin base.
                        return
                    rotulo_acao, acao_preview = obter_acao_preview_loja(
                        item_preview_tipo, item_preview_id, dados, item_preview_confirmar)
                    if acao_preview == "equipar":
                        if item_preview_tipo == "SKIN":
                            dados["skin_equipada"] = item_preview_id
                            animacao_recompensa = {"titulo": "SKIN EQUIPADA!", "sub": SKINS_NOMES.get(item_preview_id, item_preview_id), "cor": SKINS[item_preview_id]["cor"], "inicio": frame_count, "duracao": 92, "tipo": "SKIN", "id": item_preview_id, "raridade": raridade_de_skin(item_preview_id)}
                        else:
                            pet_id = item_preview_id
                            dados["pet_equipado"] = pet_id
                            animacao_recompensa = {"titulo": "PET EQUIPADO!", "sub": PETS_CONFIG[pet_id]["nome"], "cor": PETS_CONFIG[pet_id]["cor"], "inicio": frame_count, "duracao": 92, "tipo": "PET", "id": pet_id, "raridade": PETS_CONFIG[pet_id]["raridade"]}
                        salvar_dados(dados)
                        item_preview_tipo = None
                        item_preview_id = None
                        item_preview_confirmar = False
                        item_preview_surface = None
                        item_preview_estilo = 1
                    elif acao_preview == "desbloquear":
                        # Revalida os requisitos no instante do toque para impedir desbloqueio indevido.
                        requisito_ok = False
                        if item_preview_tipo == "SKIN":
                            objetivo_skin = SKINS_OBJETIVOS.get(item_preview_id)
                            if objetivo_skin:
                                stats_validacao = dados.get("estatisticas_permanentes", {})
                                requisito_ok = int(stats_validacao.get(objetivo_skin[1], 0)) >= int(objetivo_skin[2])
                            else:
                                requisito_ok = item_preview_id in dados.get("skins_desbloqueadas", ["AZUL"])
                            if requisito_ok:
                                desbloqueadas_validacao = dados.setdefault("skins_desbloqueadas", ["AZUL"])
                                if item_preview_id not in desbloqueadas_validacao:
                                    desbloqueadas_validacao.append(item_preview_id)
                                dados["skin_equipada"] = item_preview_id
                        else:
                            requisito_ok = objetivo_pet_concluido(item_preview_id, dados)
                            if requisito_ok:
                                pet_id = item_preview_id
                                desbloqueados = dados.setdefault("pets_desbloqueados", [])
                                if pet_id not in desbloqueados:
                                    desbloqueados.append(pet_id)
                                dados["pet_equipado"] = pet_id
                                dados.setdefault("estatisticas_permanentes", {})["pets_desbloqueados"] = len(desbloqueados)
                        if requisito_ok:
                            if item_preview_tipo == "SKIN":
                                animacao_recompensa = {"titulo": "SKIN DESBLOQUEADA!", "sub": SKINS_NOMES.get(item_preview_id, item_preview_id), "cor": SKINS[item_preview_id]["cor"], "inicio": frame_count, "duracao": 102, "tipo": "SKIN", "id": item_preview_id, "raridade": raridade_de_skin(item_preview_id)}
                            else:
                                animacao_recompensa = {"titulo": "PET DESBLOQUEADO!", "sub": PETS_CONFIG[item_preview_id]["nome"], "cor": PETS_CONFIG[item_preview_id]["cor"], "inicio": frame_count, "duracao": 102, "tipo": "PET", "id": item_preview_id, "raridade": PETS_CONFIG[item_preview_id]["raridade"]}
                            salvar_dados(dados)
                        else:
                            # Não altera moedas, desbloqueios nem equipamento se o requisito não foi atingido.
                            item_preview_confirmar = False
                        item_preview_tipo = None
                        item_preview_id = None
                        item_preview_confirmar = False
                        item_preview_surface = None
                        item_preview_estilo = 1
                    elif acao_preview == "comprar":
                        # Primeiro toque apenas arma a confirmação; não desconta moedas.
                        item_preview_confirmar = True
                    elif acao_preview == "comprar_confirmado":
                        # O saldo é validado novamente no segundo toque antes da compra.
                        if item_preview_tipo == "SKIN":
                            info_compra = SKINS[item_preview_id]
                            if int(dados.get("moedas_totais", 0)) >= int(info_compra["preco"]):
                                dados["moedas_totais"] -= int(info_compra["preco"])
                                desbloqueadas = dados.setdefault("skins_desbloqueadas", ["AZUL"])
                                if item_preview_id not in desbloqueadas:
                                    desbloqueadas.append(item_preview_id)
                                dados.setdefault("skins_compradas_confirmadas", []).append(item_preview_id)
                                dados["skins_compradas_confirmadas"] = list(dict.fromkeys(dados["skins_compradas_confirmadas"]))
                                dados.setdefault("estatisticas_permanentes", {})["skins_desbloqueadas"] = len(desbloqueadas)
                                animacao_recompensa = {"titulo": "NOVA SKIN!", "sub": SKINS_NOMES.get(item_preview_id, item_preview_id), "cor": SKINS[item_preview_id]["cor"], "inicio": frame_count, "duracao": 108, "tipo": "SKIN", "id": item_preview_id, "raridade": raridade_de_skin(item_preview_id)}
                                item_preview_confirmar = False
                                salvar_dados(dados)
                            else:
                                item_preview_confirmar = False
                        else:
                            info_compra = PETS_CONFIG[item_preview_id]
                            if int(dados.get("moedas_totais", 0)) >= int(info_compra["preco"]):
                                dados["moedas_totais"] -= int(info_compra["preco"])
                                desbloqueados = dados.setdefault("pets_desbloqueados", [])
                                if item_preview_id not in desbloqueados:
                                    desbloqueados.append(item_preview_id)
                                dados.setdefault("estatisticas_permanentes", {})["pets_desbloqueados"] = len(desbloqueados)
                                animacao_recompensa = {"titulo": "NOVO PET!", "sub": PETS_CONFIG[item_preview_id]["nome"], "cor": PETS_CONFIG[item_preview_id]["cor"], "inicio": frame_count, "duracao": 108, "tipo": "PET", "id": item_preview_id, "raridade": PETS_CONFIG[item_preview_id]["raridade"]}
                                item_preview_confirmar = False
                                salvar_dados(dados)
                            else:
                                item_preview_confirmar = False
            elif btn_voltar.collidepoint(pos):
                estado = "INICIO"
            elif estado == "LOJA" and aba_loja == "PETS" and btn_cantinho_pets.collidepoint(pos):
                estado = "CANTINHO_PETS"
                pet_cantinho_selecionado = (dados.get("pet_equipado") if dados.get("pet_equipado") in PETS_CONFIG
                                            else next(iter(PETS_CONFIG)))
                pet_cantinho_acao = "ESPERA"
            elif estado == "LOJA" and btn_aba_skins.collidepoint(pos):
                aba_loja = "SKINS"
                loja_pagina = 0
                item_preview_confirmar = False
                anim_menu_tempo = 0
            elif estado == "LOJA" and btn_aba_pets.collidepoint(pos):
                aba_loja = "PETS"
                loja_pagina = 0
                item_preview_confirmar = False
                anim_menu_tempo = 0
            elif estado == "LOJA" and aba_loja in ("SKINS", "PETS") and btn_loja_pagina_ant.collidepoint(pos):
                loja_pagina = max(0, loja_pagina - 1)
            elif estado == "LOJA" and aba_loja in ("SKINS", "PETS") and btn_loja_pagina_prox.collidepoint(pos):
                total_paginas_loja = (len(SKINS) + 6) // 7 if aba_loja == "SKINS" else (len(PETS_CONFIG) + PETS_POR_PAGINA - 1) // PETS_POR_PAGINA
                loja_pagina = min(total_paginas_loja - 1, loja_pagina + 1)
            else:
                y_base = 170 if estado == "LOJA" else 125
                if estado == "LOJA" and aba_loja == "SKINS":
                    skins_visiveis = list(SKINS.items())[loja_pagina * 7:(loja_pagina + 1) * 7]
                    for nome, info in skins_visiveis:
                        rect_item = pygame.Rect(35, y_base, 380, 55)
                        if rect_item.collidepoint(pos) and nome in SKINS_ATIVAS_PROD:
                            item_preview_tipo = "SKIN"
                            item_preview_id = nome
                            item_preview_confirmar = False
                            item_preview_surface = None
                            item_preview_estilo = nivel_visual_skin(dados)
                            break
                        y_base += 62
                elif estado == "LOJA" and aba_loja == "PETS":
                    pets_visiveis = list(PETS_CONFIG.items())[loja_pagina * PETS_POR_PAGINA:(loja_pagina + 1) * PETS_POR_PAGINA]
                    for pet_id, pet in pets_visiveis:
                        rect_item = pygame.Rect(28, y_base, 394, 82)
                        if rect_item.collidepoint(pos):
                            item_preview_tipo = "PET"
                            item_preview_id = pet_id
                            item_preview_confirmar = False
                            item_preview_surface = None
                            item_preview_estilo = nivel_visual_skin(dados)
                            break
                        y_base += 88
                elif estado == "UPGRADES":
                    if btn_upgrade_ant.collidepoint(pos):
                        pagina_upgrades = max(0, pagina_upgrades - 1)
                    elif btn_upgrade_prox.collidepoint(pos):
                        pagina_upgrades = min((len(UPGRADES_CONFIG) - 1) // UPGRADES_POR_PAGINA, pagina_upgrades + 1)
                    else:
                        upgrades_visiveis = list(UPGRADES_CONFIG.items())[pagina_upgrades * UPGRADES_POR_PAGINA:(pagina_upgrades + 1) * UPGRADES_POR_PAGINA]
                        for chave, conf in upgrades_visiveis:
                            rect_item = pygame.Rect(40, y_base, 370, 54)
                            if rect_item.collidepoint(pos):
                                nivel_atual = dados["upgrades"].get(chave, 0)
                                if nivel_atual < conf["max_nivel"]:
                                    custo = calcular_custo_upgrade(chave, nivel_atual)
                                    if dados["moedas_totais"] >= custo:
                                        dados["moedas_totais"] -= custo
                                        dados["upgrades"][chave] = nivel_atual + 1
                                        salvar_dados(dados)
                            y_base += 62
    def atualizar_simulacao():
        global portal_proximo_metro
        nonlocal frame_count, pontuacao, moedas_coletadas, novo_recorde_alcançado, estado, bioma_lendario_ativo, bioma_lendario_timer
        nonlocal evento_corrida, evento_corrida_x, evento_corrida_timer, evento_corrida_cooldown, eventos_corrida_superados, alerta_furtivo, alerta_detector_timer, interruptor_ativado
        nonlocal clima_tipo_anterior, eventos_vulcao_rodada
        nonlocal anim_menu_tempo, metros_atuais, e_slow, cor_jogador, e_noite, alvo_ceu, cor_ceu_tupla, shake_timer
        nonlocal cenario_atual, cenario_tempo_restante, transicao_cenario_timer, cenario_transicao_nome, spawn_bloqueado_frames
        nonlocal touch_hold_frames, touch_jump_started, touch_gesture_moved
        nonlocal mouse_hold_frames, mouse_jump_started, mouse_gesture_moved
        nonlocal gesto_agachar_frames
        nonlocal combo_contagem, combo_timer, combo_quase_colisoes, esquivas_perfeitas, efeito_esquiva_ate
        nonlocal febre_carga, febre_timer, febre_turbo_distancia_restante, febre_ativacoes_rodada, baus_abertos_rodada
        nonlocal portal_tipo_ativo, portal_timer, portal_y, portal_vy, portal_pontos, portal_pipes, portal_pipe_spawn, portal_falhou
        nonlocal portal_chefe_ativo, portal_chefe_hp, portal_chefe_ataque, portal_chefe_faixa, portal_chefe_fase, portal_chefe_avisos
        nonlocal fases_bonus_rodada, bioma_metros_rodada
        nonlocal biomas_lendarios_rodada, chefes_derrotados_rodada
        nonlocal pet_salvou_vida_rodada, moedas_pet_contador, portal_tipo_contagem_rodada, obstaculos_destruidos_rodada
        nonlocal pet_pos_visual, pet_estado_animado, pet_habilidade_ate
        nonlocal pet_pouso_ate, pet_alivio_ate, pet_alerta_anterior
        nonlocal pet_estado_animado_desde, pet_estado_animado_travado_ate, pet_anim_memoria
        nonlocal desafio_laser_ativo, desafio_laser_timer, desafio_laser_cooldown, desafio_laser_spawn
        nonlocal desafio_laser_y, desafio_laser_vy, desafio_laser_faixas, desafio_laser_etapa
        nonlocal palavra_hud_ate, palavra_festa_ate, tutorial_concluido_ate

        if estado == "JOGANDO" and gamefeel.tick_congelado():
            # Pausa curtíssima apenas da simulação após impacto; sem alterar o FPS.
            return
        frame_count += 1
        if estado == "JOGANDO" and tutorial_corrida is not None and tutorial_corrida.ativo:
            # O mundo é o MESMO da partida. Os sprites didáticos não entram no
            # grupo de colisões e não há morte ou spawn natural antes do aceite.
            letras_antes = tutorial_corrida.contagem_coletas if tutorial_corrida.etapa == 'letras' else 0
            ganho_tutorial, terminou_tutorial = tutorial_corrida.atualizar(
                jogador, bg_parallax, todos_sprites, letras_coletaveis,
                palavra_partida, particulas, pool_manager, gerenciador_sons,
                dados.get("vol_sfx", 0.7), frame_count)
            moedas_coletadas += ganho_tutorial
            if tutorial_corrida.contagem_coletas > letras_antes and (tutorial_corrida.etapa == 'letras' or terminou_tutorial):
                palavra_hud_ate = frame_count + 300
                criar_explosao_particulas(jogador.rect.centerx + 22, jogador.rect.y, (255, 220, 85), 12, particulas, pool_manager)
            # Durante as seis licoes a pontuacao permanece em zero.
            # Apenas a corrida normal, no bloco abaixo, passa a contar pontos.
            if terminou_tutorial:
                dados["tutorial_inicial_concluido"] = True
                tutorial_concluido_ate = frame_count + 150
                palavra_festa_ate = frame_count + 150
                palavra_hud_ate = frame_count + 300
                spawn_bloqueado_frames = max(spawn_bloqueado_frames, 150)
                salvar_dados(dados)
                # Inicia a cadência normal do gerador nesta mesma corrida.
                pygame.time.set_timer(EVENTO_GERAR, tempo_spawn_atual)
            return
        # Sistemas de corrida inéditos: eventos curtos, com aviso e poucos objetos.
        if alerta_detector_timer > 0:
            alerta_detector_timer -= 1
        if febre_turbo_distancia_restante > 0:
            alerta_furtivo = 0
        if estado == "JOGANDO" and portal_tipo_ativo is None:
            if desafio_laser_cooldown > 0:
                desafio_laser_cooldown -= 1
            if (LASERS_JETPACK_ATIVOS_PROD and not desafio_laser_ativo and desafio_laser_cooldown <= 0 and cenario_atual in ("cidade", "cidade_futurista")
                    and metros_atuais >= 450 and random.random() < 0.0035 and jogador.jetpack_fase is None and not jogador.morrendo):
                iniciar_desafio_laser()
            if evento_corrida_cooldown > 0:
                evento_corrida_cooldown -= 1
            if evento_corrida:
                evento_corrida_x -= max(3.0, min(16.0, 6.0 + metros_atuais / 100.0 * 0.18))
                evento_corrida_timer -= 1
                if evento_corrida == "INTERRUPTOR" and not interruptor_ativado and abs(evento_corrida_x - jogador.rect.centerx) < 44:
                    if not jogador.no_chao:
                        interruptor_ativado = True
                        moedas_coletadas += 5
                        eventos_corrida_superados += 1
                        textos_flut.add(TextoFlutuante(jogador.rect.centerx, jogador.rect.y - 28, "INTERRUPTOR! +5", (90, 255, 190), "grande"))
                if evento_corrida == "PLATAFORMA" and abs(evento_corrida_x - jogador.rect.centerx) < 24 and jogador.no_chao:
                    moedas_coletadas = max(0, moedas_coletadas - 4)
                    evento_corrida_timer = min(evento_corrida_timer, 1)
                    textos_flut.add(TextoFlutuante(jogador.rect.centerx, jogador.rect.y - 25, "OBSTÁCULO MECÂNICO: -4 MOEDAS", (255, 150, 90)))
                if False and evento_corrida == "INFILTRACAO" and 90 < (evento_corrida_x - jogador.rect.centerx) < 240 and alerta_detector_timer <= 0:
                    alerta_detector_timer = 75
                    gerenciador_sons.tocar_som("alerta_laser", False, dados["vol_sfx"])
                if False and evento_corrida == "INFILTRACAO" and abs(evento_corrida_x - jogador.rect.centerx) < 35:
                    sensor_ativo = (frame_count // 18) % 2 == 0
                    furtivo = bool(getattr(jogador, "agachado", False)) or not jogador.no_chao
                    if sensor_ativo and not furtivo and alerta_furtivo <= 0 and febre_turbo_distancia_restante <= 0:
                        alerta_furtivo = 90
                        moedas_coletadas = max(0, moedas_coletadas - 3)
                        textos_flut.add(TextoFlutuante(jogador.rect.centerx, jogador.rect.y - 35, "SENSOR DETECTOU VOCÊ: -3 MOEDAS", (255, 90, 100), "grande"))
                if evento_corrida_x < -70 or evento_corrida_timer <= 0:
                    if evento_corrida == "PLATAFORMA" and abs(evento_corrida_x - jogador.rect.centerx) < 38 and jogador.no_chao:
                        # A máquina móvel cruza a faixa baixa: quem não saltou recebe penalidade leve.
                        moedas_coletadas = max(0, moedas_coletadas - 4)
                        textos_flut.add(TextoFlutuante(jogador.rect.centerx, jogador.rect.y - 25, "OBSTÁCULO MECÂNICO: -4 MOEDAS", (255, 150, 90)))
                    evento_corrida = None
                    evento_corrida_cooldown = random.randint(420, 660)
                    salvar_dados(dados)
            if alerta_furtivo > 0:
                alerta_furtivo -= 1
        if gesto_agachar_frames > 0:
            gesto_agachar_frames -= 1
        if shake_timer > 0:
            shake_timer -= 1
        if estado in ["INICIO", "LOJA", "UPGRADES", "CONFIG", "CONFIG_CONTROLES", "CONFIG_ACESSIBILIDADE", "CONQUISTAS", "RECORDES", "DESAFIOS", "DESAFIO_PERCURSO", "RANKING", "RELIQUIAS", "BASE_CORREDOR", "CANTINHO_PETS"]:
            anim_menu_tempo = min(45, anim_menu_tempo + 1)
        preparar_desafios(dados)
        skin_nome_atual = dados["skin_equipada"]
        cor_jogador = SKINS.get(skin_nome_atual, SKINS["AZUL"])["cor"]
        metros_atuais = pontuacao // 10
        if estado == "JOGANDO":
            if (dados.get("pet_equipado") == "DRAGAO_PLASMA") and frame_count % 150 == 0 and obstaculos:
                alvo_pet = min((o for o in obstaculos if o.rect.centerx > jogador.rect.right), key=lambda o: o.rect.centerx, default=None)
                if alvo_pet is not None:
                    pet_habilidade_ate = frame_count + 33
                    criar_explosao_particulas(alvo_pet.rect.centerx, alvo_pet.rect.centery, (70, 210, 255), 10, particulas, pool_manager)
                    obstaculos_destruidos_rodada += max(1, int(getattr(alvo_pet, "qtd_cactos", 1)))
                    alvo_pet.kill()
            if febre_timer > 0:
                febre_timer -= 1
            if combo_timer > 0:
                combo_timer -= 1
                if combo_timer <= 0:
                    combo_contagem = 0
            if spawn_bloqueado_frames > 0:
                spawn_bloqueado_frames -= 1
            cenario_tempo_restante -= 1
            if bioma_lendario_timer > 0:
                bioma_lendario_timer -= 1
                if bioma_lendario_timer <= 0:
                    bioma_lendario_ativo = None
            bioma_metros_rodada[cenario_atual] = bioma_metros_rodada.get(cenario_atual, 0) + 2
            if cenario_tempo_restante <= 0:
                # Sorteio independente da distância, com intervalo de segurança longo.
                cenario_desejado = sortear_proximo_cenario(cenario_atual)
                # Bioma lendário é um evento temporário sobre o bioma-base; mantém
                # intactas as estatísticas e os geradores dos sete biomas oficiais.
                if False:
                    bioma_lendario_ativo = random.choice(tuple(BIOMAS_LENDARIOS.keys()))
                    bioma_lendario_timer = 900
                    biomas_lendarios_rodada += 1
                    textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 245,
                        "BIOMA LENDÁRIO: " + BIOMAS_LENDARIOS[bioma_lendario_ativo]["nome"],
                        BIOMAS_LENDARIOS[bioma_lendario_ativo]["cor"], "grande"))
                else:
                    bioma_lendario_ativo = None
                    bioma_lendario_timer = 0
                cenario_atual = cenario_desejado
                bg_parallax.set_cenario(cenario_atual)
                clima.trocar_cenario(cenario_atual)
                cenario_transicao_nome = nome_cenario(cenario_atual)
                transicao_cenario_timer = 105  # cerca de 1,75 s a 60 Hz
                # Descanso de spawn apenas durante a entrada em um novo bioma.
                # Não remove perigos já na pista nem altera qualquer hitbox.
                from pixelrush_rotacao_biomas_v3261 import QUADROS_PROTECAO_TRANSICAO
                spawn_bloqueado_frames = max(spawn_bloqueado_frames, QUADROS_PROTECAO_TRANSICAO)
                if not modo_grafico_leve(dados):
                    gerenciador_sons.tocar_som(f"amb_{cenario_atual}", False, min(0.25, dados.get('vol_sfx', 0.7) * 0.38))
                cenario_tempo_restante = random.randint(80, 140) * 60
        if transicao_cenario_timer > 0:
            transicao_cenario_timer -= 1
        e_slow = (jogador.tempo_slow > 0) if jogador else False
        fase_ciclo, cor_objetivo_ceu, peso_noite, e_noite = calcular_ciclo_ceu(metros_atuais)
        alvo_ceu = list(cor_objetivo_ceu)
        for i in range(3):
            if cor_atual_ceu[i] < alvo_ceu[i]:
                cor_atual_ceu[i] = min(cor_atual_ceu[i] + 1.2, alvo_ceu[i])
            elif cor_atual_ceu[i] > alvo_ceu[i]:
                cor_atual_ceu[i] = max(cor_atual_ceu[i] - 1.2, alvo_ceu[i])
        cor_ceu_tupla = (int(cor_atual_ceu[0]), int(cor_atual_ceu[1]), int(cor_atual_ceu[2]))

        if estado == "JOGANDO":
            # Aceleração mais suave; o teto mais baixo aumenta a duração média das partidas.
            vel_base = min(16.0, 6.0 + (metros_atuais / 100.0) * 0.18)
            if jogador.tempo_crono > 0:
                vel_jogo = vel_base * 0.62
            elif jogador.tempo_slow > 0:
                vel_jogo = vel_base * 0.5
            elif jogador.tempo_turbo_fantasma > 0:
                vel_jogo = vel_base + 5.0
            elif jogador.tempo_turbo > 0:
                vel_jogo = vel_base + 8.0
            else:
                vel_jogo = vel_base
            # A febre vira um turbo-cometa: 3x a velocidade do power-up TURBO.
            if febre_turbo_distancia_restante > 0:
                vel_jogo = (vel_base + 8.0) * 3.0
            elif clima.tipo == "vento_neon":
                vel_jogo *= 1.08  # rajadas favoráveis aceleram o avanço
            elif clima.tipo in ("cinzas", "chuva_acida"):
                vel_jogo *= 0.94  # clima hostil reduz um pouco o avanço
            # Plano K 13 — eventos raros independentes, sem mexer no spawn.
            _perigos_rare_proximos = OBSTACULOS_QUE_AVANCAM_ATIVOS_PROD and any(
                obj.rect.left < jogador.rect.right + 215
                and obj.rect.right > jogador.rect.left - 20
                for grupo in (obstaculos, perigos_especiais, buracos)
                for obj in grupo)
            _evento_raro_permitido = (
                not jogador.morrendo and portal_tipo_ativo is None
                and not desafio_laser_ativo and not desafio_laser_faixas
                and jogador.jetpack_fase is None
                and febre_turbo_distancia_restante <= 0
                and evento_corrida is None and transicao_cenario_timer <= 0
                and not diretor_perseguidores.ativo)
            _pro_sub_inicio("qa_sim_diretores")
            diretor_eventos_raros.atualizar(
                metros_atuais, cenario_atual,
                permitido=(_evento_raro_permitido and OBSTACULOS_QUE_AVANCAM_ATIVOS_PROD),
                perigo_proximo=_perigos_rare_proximos)
            diretor_perseguidores.atualizar(
                metros_atuais, cenario_atual,
                permitido=(OBSTACULOS_QUE_AVANCAM_ATIVOS_PROD and not jogador.morrendo
                           and portal_tipo_ativo is None
                           and not desafio_laser_ativo and not desafio_laser_faixas
                           and jogador.jetpack_fase is None
                           and febre_turbo_distancia_restante <= 0
                           and evento_corrida is None and transicao_cenario_timer <= 0
                           and not diretor_eventos_raros.ativo),
                jogador_x=jogador.rect.left, velocidade_jogador=vel_jogo,
                perigos_proximos=any(
                    obj.rect.left < jogador.rect.right + 180
                    and obj.rect.right > jogador.rect.left - 15
                    for grupo in (obstaculos, perigos_especiais, buracos)
                    for obj in grupo))
            _pro_sub_fim()  # qa_sim_diretores
            gamefeel.atualizar(vel_jogo, vel_base,
                               turbo=bool(febre_turbo_distancia_restante > 0 or jogador.tempo_turbo > 0))

            if not jogador.morrendo:
                # A distância do cometa avança a 3x a velocidade do turbo convencional.
                if febre_turbo_distancia_restante > 0:
                    pontuacao += 6  # +0,6 m por tick, exatamente 3x os +0,2 m normais.
                    febre_turbo_distancia_restante = max(0.0, febre_turbo_distancia_restante - 0.6)
                    if frame_count % 2 == 0:
                        criar_explosao_particulas(jogador.rect.left + 4, jogador.rect.centery + random.randint(-14, 14),
                                                  (255, 205, 55), 3, particulas, pool_manager)
                    if febre_turbo_distancia_restante <= 0:
                        febre_timer = 0
                        textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 245, "COMETA CONCLUÍDO! +500 m", (255, 220, 80), "grande"))
                else:
                    pontuacao += 4 if jogador.tempo_mult > 0 else 2

                if jogador.tempo_ima > 0 and frame_count % 18 == 0:
                    gerenciador_sons.tocar_som("eletricidade", e_slow, dados["vol_sfx"])
                if jogador.tempo_turbo > 0 and frame_count % 12 == 0:
                    gerenciador_sons.tocar_som("chamas", e_slow, dados["vol_sfx"])

            _pro_sub_inicio("qa_sim_parallax")
            bg_parallax.update(vel_jogo, metros_atuais)
            _pro_sub_fim()
            for buraco in list(buracos):
                buraco.update(vel_jogo)

            centro_pe_jogador = jogador.rect.centerx
            pode_pousar = (jogador_invencivel_por_velocidade(jogador, febre_timer,
                                                             febre_turbo_distancia_restante) or
                           not any(b.rect.left <= centro_pe_jogador <= b.rect.right for b in buracos))

            # Toque parado passa a ser um comando de pulo após 8 ticks (~133 ms).
            # Se o dedo descer, o gesto fica reservado para agachar/descida rapida.
            if (toque_ativo and touch_start_pos and touch_current_pos and
                    not touch_jump_started and not touch_gesture_moved and
                    not btn_pausa.collidepoint(touch_start_pos) and
                    jogador.jetpack_fase is None):
                touch_dx = touch_current_pos[0] - touch_start_pos[0]
                touch_dy = touch_current_pos[1] - touch_start_pos[1]
                if abs(touch_dx) > limiar(dados) or abs(touch_dy) > limiar(dados):
                    touch_gesture_moved = True
                else:
                    touch_hold_frames += 1
                    if (touch_hold_frames >= 6 and
                            normalizar_modo(dados.get('controle_modo')) == MODO_CLASSICO):
                        jogador.pular(gerenciador_sons, dados["vol_sfx"])
                        touch_jump_started = True

            # Mouse: mesmo limiar do touch para distinguir clique/pulo de swipe.
            if (mouse_drag_active and mouse_gameplay_press and not mouse_input_ignored and
                    mouse_start_pos and mouse_current_pos and not mouse_jump_started and
                    not mouse_gesture_moved and jogador.jetpack_fase is None and
                    not btn_pausa.collidepoint(mouse_start_pos)):
                mouse_dx = mouse_current_pos[0] - mouse_start_pos[0]
                mouse_dy = mouse_current_pos[1] - mouse_start_pos[1]
                if abs(mouse_dx) > 30 or abs(mouse_dy) > 30:
                    mouse_gesture_moved = True
                else:
                    mouse_hold_frames += 1
                    if mouse_hold_frames >= 8:
                        jogador.pular(gerenciador_sons, dados["vol_sfx"])
                        mouse_jump_started = True

            mouse_baixo = bool(
                mouse_drag_active and mouse_gameplay_press and not mouse_input_ignored and
                mouse_start_pos and mouse_current_pos and jogador.jetpack_fase is None and
                mouse_current_pos[1] - mouse_start_pos[1] > 30)
            modo_touch_rodada = normalizar_modo(dados.get('controle_modo', 'CLASSICO'))
            segurando_pulo = (input_pulo_ativo or gamepad_pulo or controle_dedos.holding('pulo') or
                               (input_mouse_ativo and not mouse_baixo) or
                               (toque_ativo and modo_touch_rodada == MODO_CLASSICO and not segurando_baixo_touch))
            segurando_baixo = (input_baixo_ativo or gamepad_baixo or controle_dedos.holding('baixo') or
                               segurando_baixo_touch or mouse_baixo or
                               (gesto_agachar_frames > 0 and jogador.no_chao))

            prev_slow = jogador.tempo_slow
            prev_turbo = jogador.tempo_turbo
            estava_no_chao = bool(jogador.no_chao)

            _pro_sub_inicio("fisica_jogador")
            jogador.update(vel_jogo, frame_count, segurando_pulo, segurando_baixo, particulas, pool_manager,
                           gerenciador_sons, dados["vol_sfx"], pode_pousar=pode_pousar)
            _pro_sub_fim()
            # Plano K 12: aproveita ações já executadas pelo jogador (sem novos controles).
            diretor_perseguidores.registrar_manuobra(
                no_chao=jogador.no_chao, agachado=jogador.agachado,
                subindo=jogador.velocidade_y < 0)
            # Colisão exclusiva dos novos eventos. Nunca altera hitbox antiga.
            diretor_eventos_raros.detectar_colisao(jogador)
            diretor_eventos_raros.resolver_impacto(
                jogador,
                protegido=jogador_invencivel_por_velocidade(
                    jogador, febre_timer, febre_turbo_distancia_restante),
                imortal=bool(modo_desenvolvedor and dev_imortalidade))
            diretor_perseguidores.resolver_captura(
                jogador,
                protegido=jogador_invencivel_por_velocidade(
                    jogador, febre_timer, febre_turbo_distancia_restante),
                imortal=bool(modo_desenvolvedor and dev_imortalidade))
            if jogador.morrendo and jogador.morte_por_buraco:
                aprendizado_contextual.registrar("buraco")
            if (not estava_no_chao and jogador.no_chao and not jogador.morrendo and portal_tipo_ativo is None
                    and jogador.jetpack_fase is None):
                gamefeel.impacto(3.2, direcao_x=0.0, direcao_y=0.5, congelar=False)
                gerar_fx_pouso_bioma(jogador.rect.centerx, jogador.rect.bottom - 2, cenario_atual, particulas, pool_manager, modo_grafico_leve(dados))
                bg_parallax.world.register_landing(jogador.rect.centerx, 1.0)
                if dados.get("pet_equipado") in PETS_CONFIG:
                    pet_pouso_ate = frame_count + 11  # Animação somente visual.
            if desafio_laser_ativo and not jogador.morrendo and portal_tipo_ativo is None:
                desafio_laser_timer -= 1
                desafio_laser_spawn -= 1
                # Quando termina a duracao, deixe somente as barreiras ja
                # geradas sairem. Antes o timer ficava negativo, mas surgiam
                # novas faixas indefinidamente, impedindo a conclusao.
                if desafio_laser_timer > 0 and desafio_laser_spawn <= 0:
                    padrao = random.choice(("reto", "alto", "baixo", "zigzag"))
                    gap_h = random.choice((112, 122, 132, 142))
                    if desafio_laser_faixas:
                        ultimo_gap = desafio_laser_faixas[-1]["gap_y"]
                    else:
                        ultimo_gap = ALTURA_VIRTUAL - 330
                    if padrao == "alto":
                        gap_y = ALTURA_VIRTUAL - random.choice((410, 395, 380))
                    elif padrao == "baixo":
                        gap_y = ALTURA_VIRTUAL - random.choice((295, 280, 265))
                    elif padrao == "zigzag":
                        gap_y = ALTURA_VIRTUAL - (280 if ultimo_gap < ALTURA_VIRTUAL - 330 else 400)
                    else:
                        gap_y = random.choice((ALTURA_VIRTUAL - 410, ALTURA_VIRTUAL - 360, ALTURA_VIRTUAL - 315, ALTURA_VIRTUAL - 275))
                    if desafio_laser_etapa % 3 == 2:
                        # A cada tres portais, acrescenta UM desenho seguro
                        # no mesmo corredor existente, sem outro gerador.
                        gap_y, gap_h, padrao = corredor_avancado(
                            desafio_laser_etapa, ultimo_gap, ALTURA_VIRTUAL, random)
                        warning = 28
                        intervalo = random.randint(40, 48)
                    else:
                        warning = 22
                        intervalo = random.randint(32, 44)
                    desafio_laser_faixas.append({"x": float(LARGURA_VIRTUAL + 24), "gap_y": int(gap_y), "gap_h": int(gap_h), "warning": warning, "passed": False, "padrao": padrao})
                    desafio_laser_spawn = intervalo
                    desafio_laser_etapa += 1
                    for i in range(7):
                        m = pool_manager.obter_moeda(LARGURA_VIRTUAL + 62 + i * 24, int(gap_y + math.sin(i * 0.55) * 10))
                        todos_sprites.add(m)
                        moedas.add(m)
                if segurando_pulo:
                    desafio_laser_vy -= 0.72
                elif segurando_baixo:
                    desafio_laser_vy += 0.82
                else:
                    desafio_laser_vy += 0.34
                desafio_laser_vy = max(-6.3, min(6.3, desafio_laser_vy))
                desafio_laser_y = max(ALTURA_VIRTUAL - 445, min(ALTURA_VIRTUAL - 120, desafio_laser_y + desafio_laser_vy))
                jogador.rect.centery = int(desafio_laser_y)
                jogador.no_chao = False
                jogador.velocidade_y = 0
                for faixa in list(desafio_laser_faixas):
                    faixa["x"] -= vel_jogo + 3.0
                    if faixa["warning"] > 0:
                        faixa["warning"] -= 1
                    if faixa["x"] < -50:
                        desafio_laser_faixas.remove(faixa)
                if desafio_laser_timer <= 0 and not desafio_laser_faixas:
                    encerrar_desafio_laser(True)
            # Seguidor com inércia visual em ticks fixos. A hitbox do jogador não muda.
            if dados.get("pet_equipado") in PETS_CONFIG:
                pet_id_alvo = dados.get("pet_equipado", "")
                pet_voador = pet_eh_voador(pet_id_alvo)
                alvo_px, alvo_py = _alvo_visual_pet_corrida(jogador, pet_id_alvo, frame_count)
                if pet_pos_visual is None:
                    pet_pos_visual = [alvo_px, alvo_py]
                else:
                    pet_pos_visual[0] += max(-5.2, min(5.2, (alvo_px - pet_pos_visual[0]) * 0.24))
                    if pet_voador:
                        pet_pos_visual[1] += max(-7.5, min(7.5, (alvo_py - pet_pos_visual[1]) * 0.28))
                    elif jogador.no_chao or jogador.morrendo:
                        # Sem amortecimento vertical no solo: não deixa pets flutuando.
                        pet_pos_visual[1] = alvo_py
                    else:
                        pet_pos_visual[1] += max(-12.0, min(12.0, (alvo_py - pet_pos_visual[1]) * 0.45))
                # Reações do pet são APENAS visuais. Prioriza movimento aéreo e
                # habilidades; só observa obstáculos dentro de uma faixa curta.
                perigo_proximo = any(
                    0 < obs.rect.left - jogador.rect.right < 140
                    for obs in obstaculos
                )
                if pet_alerta_anterior and not perigo_proximo and jogador.no_chao:
                    pet_alivio_ate = frame_count + 24
                pet_alerta_anterior = perigo_proximo
                moedas_proximas = any(
                    0 < moeda.rect.left - jogador.rect.right < 95
                    for moeda in moedas
                )
                pet_estado_animado, pet_estado_animado_desde, pet_estado_animado_travado_ate, pet_anim_memoria = atualizar_estado_visual_pet(
                    frame_count, pet_estado_animado, pet_estado_animado_desde, pet_estado_animado_travado_ate, pet_anim_memoria,
                    jogador, perigo_proximo, moedas_proximas, febre_timer, pet_reacao_ate,
                    pet_habilidade_ate, pet_pouso_ate, pet_alivio_ate
                )
            else:
                pet_pos_visual = None
            origem_ambiente_x = bg_parallax.world.ambient_x()
            bloqueio_sonoro = (bg_parallax.world.ambient_occlusion(origem_ambiente_x)
                               if frame_count >= gerenciador_sons.proximo_ambiente_frame else 0.0)
            gerenciador_sons.tocar_ambiente_bioma(cenario_atual, clima.tipo, dados["vol_sfx"], frame_count,
                                                    pos_x=origem_ambiente_x, oclusao=bloqueio_sonoro)
            paisagem_sonora.atualizar(cenario_atual, 'JOGANDO', dados['vol_sfx'], clima.tipo)

            # As fases bônus substituem temporariamente a gravidade normal por física própria.
            if portal_tipo_ativo is not None and not jogador.morrendo:
                portal_timer = max(0, portal_timer - 1)
                portal_pipe_spawn -= 1
                # Tesouros são coletáveis desenhados no cenário e não concedem moedas automaticamente.
                if portal_chefe_ativo:
                    portal_chefe_ataque += 1
                    # Cada bioma usa um padrão de chefe distinto, com aviso visual antes do ataque.
                    padroes_chefe = {
                        "cidade": (72, (190, 310, 430, 550), (255, 95, 115)),
                        "deserto": (62, (150, 270, 390, 510), (255, 185, 70)),
                        "neve": (82, (220, 340, 460, 580), (120, 220, 255)),
                        "vulcao": (54, (170, 290, 410, 530), (255, 95, 35)),
                        "cidade_futurista": (48, (130, 250, 370, 490), (80, 255, 230)),
                        "floresta": (68, (200, 320, 440, 560), (120, 235, 105)),
                        "reino_submerso": (58, (155, 275, 395, 515), (70, 220, 255)),
                        "ilhas_celestes": (52, (135, 255, 375, 495), (185, 225, 255)),
                    }
                    intervalo_chefe, faixas_chefe, cor_chefe_bioma = padroes_chefe.get(cenario_atual, padroes_chefe["cidade"])
                    if portal_chefe_ataque % intervalo_chefe == 1:
                        portal_chefe_fase = 1 + ((portal_chefe_ataque // intervalo_chefe) % 3)
                        if cenario_atual == "vulcao":
                            portal_chefe_faixa = random.choice(faixas_chefe[:2] if portal_chefe_fase == 1 else faixas_chefe[2:])
                        elif cenario_atual == "cidade_futurista":
                            portal_chefe_faixa = faixas_chefe[(portal_chefe_ataque // intervalo_chefe) % len(faixas_chefe)]
                        elif cenario_atual == "floresta":
                            portal_chefe_faixa = random.choice(faixas_chefe)
                        elif cenario_atual == "reino_submerso":
                            portal_chefe_faixa = faixas_chefe[0] if portal_chefe_fase in (1, 3) else faixas_chefe[-1]
                        elif cenario_atual == "ilhas_celestes":
                            portal_chefe_faixa = faixas_chefe[(portal_chefe_ataque // intervalo_chefe) % len(faixas_chefe)]
                        else:
                            portal_chefe_faixa = random.choice(faixas_chefe)
                        portal_chefe_avisos = 8
                    if portal_chefe_avisos > 0:
                        portal_chefe_avisos -= 1
                    elif portal_chefe_ataque % intervalo_chefe in (9, 10, 11, 12, 13, 14):
                        # Ataque largo no vulcão; rajada rápida na cidade futurista; demais em faixa.
                        tolerancia = 70 if cenario_atual == "vulcao" else 42 if cenario_atual == "cidade_futurista" else 56 if cenario_atual == "reino_submerso" else 34 if cenario_atual == "ilhas_celestes" else 48
                        if abs(jogador.rect.centery - portal_chefe_faixa) < tolerancia:
                            if jogador.escudo_hits > 0:
                                jogador.escudo_hits -= 1
                            else:
                                portal_falhou = True
                    if portal_chefe_ataque % (58 if cenario_atual == "cidade_futurista" else 80) == 0:
                        portal_chefe_hp -= 1
                        textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 205, "CHEFE ATINGIDO!", (255, 220, 90), "grande"))
                    if portal_chefe_hp <= 0:
                        portal_chefe_ativo = False
                        portal_chefe_hp = -1  # Sentinel: impede iniciar o mesmo chefe novamente.
                        chefes_derrotados_rodada += 1
                        stats_frag = dados.setdefault("estatisticas_novas", {}).get("fragmentos_reliquia", 0)
                        dados["estatisticas_novas"]["fragmentos_reliquia"] = int(stats_frag) + 2
                        textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 235, "+2 FRAGMENTOS DE RELÍQUIA", (190, 220, 255), "normal"))
                        portal_timer = 0
                    elif portal_chefe_ataque >= 300:
                        portal_chefe_ativo = False
                        portal_falhou = True
                        portal_timer = 0
                if portal_chefe_ativo:
                    if segurando_pulo:
                        portal_y -= 5.5
                    elif segurando_baixo:
                        portal_y += 5.5
                    portal_y = max(65, min(ALTURA_VIRTUAL - 75, portal_y))
                    jogador.rect.centery = int(portal_y)
                    jogador.no_chao = False
                if portal_tipo_ativo == "INVERTIDO" and not portal_chefe_ativo:
                    # Gravidade invertida: o personagem é puxado para o teto; pulo/toque empurra para baixo.
                    if segurando_pulo:
                        portal_vy += 0.72
                    else:
                        portal_vy -= 0.48
                    portal_vy = max(-9.0, min(9.0, portal_vy))
                    portal_y += portal_vy
                    if portal_y < 55:
                        portal_y = 55
                        portal_vy = 2.0
                    if portal_y > ALTURA_VIRTUAL - 105:
                        portal_y = ALTURA_VIRTUAL - 105
                        portal_vy = -2.0
                    jogador.rect.centery = int(portal_y)
                    jogador.no_chao = False
                elif portal_tipo_ativo == "FLAPPY" and not portal_chefe_ativo:
                    if portal_timer > 540:
                        jogador.rect.centery = int(portal_y)
                        jogador.no_chao = False
                    elif segurando_pulo and frame_count % 8 == 0:
                        portal_vy = -8.5
                    portal_vy = min(8.0, portal_vy + 0.42)
                    portal_y += portal_vy
                    if portal_y < 48 or portal_y > ALTURA_VIRTUAL - 65:
                        portal_falhou = True
                        portal_timer = 0
                    jogador.rect.centery = int(portal_y)
                    jogador.no_chao = False
                    if portal_timer <= 540 and portal_pipe_spawn <= 0:
                        gap_y = random.randint(245, 485)
                        portal_pipes.append({"x": LARGURA_VIRTUAL + 30, "gap_y": gap_y, "passou": False})
                        portal_pipe_spawn = 92
                    for pipe in portal_pipes:
                        pipe["x"] -= max(3.0, vel_jogo * 0.72)
                        gap = 178
                        cima = pygame.Rect(int(pipe["x"]), 0, 58, int(pipe["gap_y"] - gap // 2))
                        baixo = pygame.Rect(int(pipe["x"]), int(pipe["gap_y"] + gap // 2), 58,
                                            ALTURA_VIRTUAL - int(pipe["gap_y"] + gap // 2))
                        if jogador.obter_hitbox().colliderect(cima) or jogador.obter_hitbox().colliderect(baixo):
                            portal_falhou = True
                            portal_timer = 0
                        if not pipe["passou"] and pipe["x"] + 58 < jogador.rect.left:
                            pipe["passou"] = True
                            portal_pontos += 1
                            moedas_coletadas += 8
                    portal_pipes = [pipe for pipe in portal_pipes if pipe["x"] > -70]
                elif portal_tipo_ativo == "TUNEL" and not portal_chefe_ativo:
                    # Túnel de precisão: alternância vertical suave e bônus por sobreviver.
                    if segurando_pulo:
                        portal_vy -= 0.62
                    elif segurando_baixo:
                        portal_vy += 0.62
                    else:
                        portal_vy += (ALTURA_VIRTUAL * 0.52 - portal_y) * 0.012
                    portal_vy = max(-6.5, min(6.5, portal_vy))
                    portal_y += portal_vy
                    if portal_y < 95 or portal_y > ALTURA_VIRTUAL - 120:
                        portal_falhou = True
                        portal_timer = 0
                    jogador.rect.centery = int(portal_y)
                    jogador.no_chao = False
                elif portal_tipo_ativo == "AQUATICO" and not portal_chefe_ativo:
                    # Pequena janela de reação antes de iniciar a física do nado.
                    if portal_timer > 540:
                        portal_y = ALTURA_VIRTUAL * 0.52
                        portal_vy = 0
                    # Nado: toque/pulo dá impulso para cima; soltar faz o personagem afundar.
                    elif segurando_pulo:
                        portal_vy -= 0.82
                    elif segurando_baixo:
                        portal_vy += 0.85
                    else:
                        portal_vy += 0.20
                    portal_vy = max(-7.0, min(7.0, portal_vy))
                    portal_y += portal_vy
                    if portal_y < 70 or portal_y > ALTURA_VIRTUAL - 80:
                        portal_falhou = True
                        portal_timer = 0
                    jogador.rect.centery = int(portal_y)
                    jogador.no_chao = False
                    if portal_pipe_spawn <= 0:
                        portal_pipes.append({"x": LARGURA_VIRTUAL + 20, "y": random.randint(160, 610), "passou": False, "tipo": "MINA"})
                        portal_pipe_spawn = 48
                    for perigo_agua in portal_pipes:
                        perigo_agua["x"] -= 4.5
                        mina_rect = pygame.Rect(int(perigo_agua["x"]), int(perigo_agua["y"]), 34, 34)
                        if jogador.obter_hitbox().colliderect(mina_rect):
                            portal_falhou = True
                            portal_timer = 0
                        if not perigo_agua["passou"] and perigo_agua["x"] + 34 < jogador.rect.left:
                            perigo_agua["passou"] = True
                            portal_pontos += 1
                    portal_pipes = [q for q in portal_pipes if q["x"] > -50]
                elif portal_tipo_ativo in ("LASERS", "REFLEXOS") and not portal_chefe_ativo:
                    # Reflexos usa sequências de laser mais ritmadas; ambos reutilizam o mesmo sistema leve.
                    if portal_pipe_spawn <= 0:
                        if portal_tipo_ativo == "REFLEXOS":
                            padrao_reflexos = (170, 350, 530, 260, 440, 620)
                            faixa_y = padrao_reflexos[(portal_pontos + len(portal_pipes)) % len(padrao_reflexos)]
                        else:
                            faixa_y = random.choice([170, 260, 350, 440, 530, 620])
                        portal_pipes.append({"x": LARGURA_VIRTUAL - 12, "y": faixa_y, "aviso": 42 if portal_tipo_ativo == "REFLEXOS" else 36, "ativo": False})
                        portal_pipe_spawn = random.randint(42, 54) if portal_tipo_ativo == "REFLEXOS" else random.randint(48, 68)
                    for laser in portal_pipes:
                        laser["aviso"] = max(0, laser["aviso"] - 1)
                        laser["ativo"] = laser["aviso"] <= 0
                        laser["x"] -= 5.5
                        if laser["ativo"]:
                            laser_rect = pygame.Rect(int(laser["x"]), int(laser["y"]), 330, 12)
                            if jogador.obter_hitbox().colliderect(laser_rect):
                                portal_falhou = True
                                portal_timer = 0
                            if not laser.get("passou") and laser["x"] + 330 < jogador.rect.left:
                                laser["passou"] = True
                                portal_pontos += 1
                    portal_pipes = [q for q in portal_pipes if q["x"] > -340]
                    if segurando_pulo:
                        portal_vy -= 0.58
                    elif segurando_baixo:
                        portal_vy += 0.58
                    else:
                        portal_vy += (ALTURA_VIRTUAL * 0.53 - portal_y) * 0.015
                    portal_vy = max(-6.0, min(6.0, portal_vy))
                    portal_y += portal_vy
                    if portal_y < 65 or portal_y > ALTURA_VIRTUAL - 75:
                        portal_falhou = True
                        portal_timer = 0
                    jogador.rect.centery = int(portal_y)
                    jogador.no_chao = False
                # Congela obstáculos normais durante o desafio; a rolagem de fundo continua.
                for grupo_bonus in (obstaculos, perigos_especiais, buracos):
                    for item_bonus in list(grupo_bonus):
                        item_bonus.kill()
                if portal_timer <= 0 and not portal_chefe_ativo and portal_chefe_hp == 0 and not portal_falhou:
                    # Todo portal termina com um chefe. Relíquia Núcleo Titã concede
                    # um golpe extra, tornando o confronto mais curto sem automatizar vitória.
                    portal_chefe_ativo = True
                    hp_bioma = {"cidade": 3, "deserto": 4, "neve": 3, "vulcao": 4, "cidade_futurista": 4, "floresta": 3, "reino_submerso": 4, "ilhas_celestes": 4}.get(cenario_atual, 3)
                    if dados.get("reliquia_equipada") == "NUCLEO_TITAN": hp_bioma = max(2, hp_bioma - 1)
                    portal_chefe_hp = hp_bioma
                    portal_chefe_ataque = 0
                    portal_chefe_fase = 1
                    portal_chefe_avisos = 8
                    portal_chefe_faixa = random.choice((190, 310, 430, 550))
                    portal_timer = 300
                    textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 220, "CHEFE DO PORTAL! DESVIE!", (255, 90, 110), "grande"))
                if portal_timer <= 0 and not portal_chefe_ativo:
                    tipo_portal_concluido = portal_tipo_ativo
                    portal_transicao_timer = 72
                    portal_transicao_tipo = "SAINDO"
                    if not portal_falhou and portal_tipo_ativo == "TESOURO":
                        dados.setdefault("estatisticas_novas", {})["fragmentos_reliquia"] = int(dados.get("estatisticas_novas", {}).get("fragmentos_reliquia", 0)) + 3
                        textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 245, "+3 FRAGMENTOS DE RELÍQUIA", (255, 220, 90), "grande"))
                    if portal_tipo_ativo == "FLAPPY":
                        recompensa_portal = 120 + portal_pontos * 12
                    elif portal_tipo_ativo == "INVERTIDO":
                        recompensa_portal = 180
                    elif portal_tipo_ativo == "AQUATICO":
                        recompensa_portal = 160 + portal_pontos * 10
                        if not portal_falhou: portal_tipo_contagem_rodada["AQUATICO"] += 1
                    elif portal_tipo_ativo == "LASERS":
                        recompensa_portal = 180 + portal_pontos * 12
                        if not portal_falhou: portal_tipo_contagem_rodada["LASERS"] += 1
                    else:
                        recompensa_portal = 150
                    if dados.get("pet_equipado") == "TARTARUGA":
                        recompensa_portal = int(recompensa_portal * (1.2 + 0.05 * (nivel_pet(dados, "TARTARUGA") - 1)))
                        pet_habilidade_ate = frame_count + 54
                    if portal_falhou:
                        recompensa_portal = max(30, recompensa_portal // 3)
                    if dados.get("reliquia_equipada") == "IMÃ_ANCESTRAL":
                        recompensa_portal = int(recompensa_portal * 1.05)
                    if dados.get("reliquia_equipada") == "PEROLA_ABISSAL" and bioma_lendario_ativo:
                        recompensa_portal = int(recompensa_portal * 1.15)
                    moedas_coletadas += recompensa_portal
                    if not portal_falhou:
                        fases_bonus_rodada += 1
                    textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 230, f"FASE BÔNUS +{recompensa_portal}", AMARELO_NEON, "grande"))
                    portal_tipo_ativo = None
                    portal_transicao_timer = 72
                    portal_transicao_tipo = "SAINDO"
                    portal_proximo_metro = max(portal_proximo_metro, int(metros_atuais + 5000))
                    portal_chefe_ativo = False
                    portal_chefe_hp = 0
                    portal_chefe_ataque = 0
                    portal_pipes = []
                    portal_vy = 0.0
                    portal_falhou = False
                    jogador.rect.bottom = jogador.chao_y
                    jogador.velocidade_y = 0
                    jogador.no_chao = True
                    spawn_bloqueado_frames = 100
                    pygame.time.set_timer(EVENTO_GERAR, tempo_spawn_atual)
                    salvar_dados(dados)

            # Rota extensa de moedas em zigue-zague durante a fase de voo no céu.
            if jogador.jetpack_fase == "voando" and frame_count % 8 == 0:
                # Mesma moeda, pool e cadencia; tres trajetorias compactas.
                nivel_moeda = faixa_moeda_jetpack(jogador.jetpack_indice_moeda)
                moeda_jetpack = pool_manager.obter_moeda(
                    LARGURA_VIRTUAL + 24, jogador.obter_y_moeda_jetpack(nivel_moeda))
                todos_sprites.add(moeda_jetpack)
                moedas.add(moeda_jetpack)
                jogador.jetpack_indice_moeda += 1

            # Aereo integrado ao mesmo tick fixo do Jetpack. Nao altera a
            # imunidade a obstaculos terrestres nem o tempo do power-up.
            jetpack_laser_avancado.atualizar(
                jogador, vel_jogo,
                permitido=(LASERS_JETPACK_ATIVOS_PROD and portal_tipo_ativo is None and not desafio_laser_ativo
                           and not jogador_invencivel_por_velocidade(
                               jogador, febre_timer, febre_turbo_distancia_restante)))

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

            if febre_turbo_distancia_restante > 0 and not jogador.morrendo:
                if frame_count % 1 == 0:
                    criar_explosao_particulas(jogador.rect.left, jogador.rect.centery + random.randint(-13, 13),
                                              (255, random.choice((190, 215, 240)), 65), 2, particulas, pool_manager)
            elif jogador.tempo_turbo > 0 and not jogador.morrendo:
                if frame_count % 2 == 0:
                    criar_rastro_turbo(jogador.rect.left, jogador.rect.centery + random.randint(-10, 10), particulas,
                                       pool_manager)

            for m in missoes_atuais:
                if m["tipo"] == "DISTANCIA": m["atual"] = metros_atuais
                elif m["tipo"] == "PULOS": m["atual"] = jogador.pulos_na_rodada
                elif m["tipo"] == "POWERUPS": m["atual"] = jogador.powerups_coletados
                elif m["tipo"] == "SLOW": m["atual"] = jogador.slow_ativados
                elif m["tipo"] == "COMBO": m["atual"] = combo_melhor
                elif m["tipo"] == "BAUS": m["atual"] = baus_abertos_rodada
                elif m["tipo"] == "PORTAIS": m["atual"] = fases_bonus_rodada
                elif m["tipo"] == "FEBRE": m["atual"] = febre_ativacoes_rodada
                elif m["tipo"] == "CHEFE": m["atual"] = chefes_derrotados_rodada
                elif m["tipo"] == "QUASE": m["atual"] = combo_quase_colisoes

            _pro_sub_inicio("inimigos_objetos")
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

            _pro_sub_fim()
            if (not jogador.morrendo and portal_tipo_ativo is None and
                    jogador.jetpack_fase is None and not desafio_laser_ativo):
                palavra_partida.tentar_spawn(metros_atuais, obstaculos, perigos_especiais,
                    buracos, moedas, todos_sprites, letras_coletaveis,
                    LARGURA_VIRTUAL, ALTURA_VIRTUAL)
            _pro_sub_inicio("particulas_update")
            textos_flut.update()
            particulas.update()
            _pro_sub_fim()

            # Clima de baixa sobrecarga. Raios em tempestades podem remover um
            # obstaculo adiante, sem tocar na hitbox ou na fisica do jogador.
            _pro_sub_inicio("qa_sim_clima")
            alvo_raio = None if portal_tipo_ativo is not None else clima.update(obstaculos, jogador.rect if not jogador.morrendo else None)
            _pro_sub_fim()
            if portal_tipo_ativo is None and clima.tipo != clima_tipo_anterior:
                if cenario_atual == "vulcao" and clima.tipo in ("cinzas", "chuva_meteoros"):
                    eventos_vulcao_rodada += 1
                    gerenciador_sons.tocar_som("chamas", False, dados["vol_sfx"] * 0.65)
                elif cenario_atual == "cidade_futurista" and clima.tipo in ("vento_neon", "chuva_acida"):
                    gerenciador_sons.tocar_som("eletricidade", False, dados["vol_sfx"] * 0.55)
                elif cenario_atual == "floresta" and clima.tipo in ("polen", "vento_folhas"):
                    gerenciador_sons.tocar_som("swipe_slow", False, dados["vol_sfx"] * 0.45)
                clima_tipo_anterior = clima.tipo
            if portal_tipo_ativo is None and clima.tipo == "chuva_meteoros" and frame_count % 90 == 0 and obstaculos:
                meteorito_alvo = min(list(obstaculos), key=lambda o: o.rect.left)
                criar_explosao_particulas(meteorito_alvo.rect.centerx, meteorito_alvo.rect.centery,
                                          (255, 105, 45), 12, particulas, pool_manager)
                meteorito_alvo.kill()
                gerenciador_sons.tocar_som("disparo_laser", e_slow, dados["vol_sfx"] * 0.45)
            if portal_tipo_ativo is None and clima.tipo == "polen" and frame_count % 60 == 0:
                febre_carga = min(100.0, febre_carga + 0.15 / FEBRE_DIFICULDADE)
            if portal_tipo_ativo is None and alvo_raio is not None and alvo_raio.alive():
                raio_x, raio_y = alvo_raio.rect.centerx, alvo_raio.rect.centery
                quantidade_cactos = max(0, getattr(alvo_raio, "qtd_cactos", 0))
                alvo_raio.kill()
                criar_explosao_particulas(raio_x, raio_y, (174, 224, 255), 10, particulas, pool_manager)
                gerenciador_sons.tocar_som("disparo_laser", e_slow, dados["vol_sfx"])
                for missao in missoes_atuais:
                    if missao["tipo"] == "QUEBRAR":
                        missao["atual"] += quantidade_cactos

            # Febre/Turbo: invulnerabilidade e destruição somente quando o herói chega.
            # Itens e perigos mais à frente continuam visíveis em cena.
            if jogador_invencivel_por_velocidade(jogador, febre_timer,
                                                  febre_turbo_distancia_restante):
                eliminados = destruir_perigos_no_caminho(jogador, obstaculos,
                                                           perigos_especiais, vel_jogo,
                                                           sdf=bool(jogador.tempo_turbo > 0 and
                                                                    febre_timer <= 0 and
                                                                    febre_turbo_distancia_restante <= 0))
                for perigo in eliminados:
                    unidades = max(0, int(getattr(perigo, "qtd_cactos", 0)))
                    if isinstance(perigo, ObstaculoTerrestre):
                        obstaculos_destruidos_rodada += max(1, unidades)
                    elif not isinstance(perigo, AvisoLaser):
                        obstaculos_destruidos_rodada += 1
                    for missao_cometa in missoes_atuais:
                        if missao_cometa["tipo"] == "QUEBRAR":
                            missao_cometa["atual"] += unidades
                    if frame_count % 3 == 0:
                        criar_explosao_particulas(perigo.rect.centerx, perigo.rect.centery,
                                                  (255, 207, 93), 3, particulas, pool_manager)
                if febre_turbo_distancia_restante > 0 and frame_count % 4 == 0:
                    criar_explosao_particulas(jogador.rect.left, jogador.rect.centery,
                                              (255, 230, 120), 3, particulas, pool_manager)

            if not jogador.morrendo:
                hitbox_jogador = jogador.obter_hitbox()
                if (jogador.jetpack_fase == 'voando' and
                        jetpack_laser_avancado.colide(hitbox_jogador)):
                    if jogador_invencivel_por_velocidade(
                            jogador, febre_timer, febre_turbo_distancia_restante):
                        jetpack_laser_avancado.consumir()
                    elif jogador.escudo_hits > 0:
                        jogador.escudo_hits -= 1
                        jetpack_laser_avancado.consumir()
                    else:
                        jetpack_laser_avancado.consumir()
                        aprendizado_contextual.registrar('laser_corredor')
                        jogador.iniciar_morte()
                # Auditoria v3.226.0: Turbo/Febre tambem protege do corredor laser.
                # Mantem o mesmo teste de invencibilidade usado nos demais perigos.
                if (desafio_laser_ativo and not jogador_invencivel_por_velocidade(
                        jogador, febre_timer, febre_turbo_distancia_restante)):
                    for faixa in list(desafio_laser_faixas):
                        if faixa.get("warning", 0) > 0:
                            continue
                        x_fx = int(faixa["x"])
                        gap_y = int(faixa["gap_y"])
                        gap_h = int(faixa["gap_h"])
                        rect_cima = pygame.Rect(x_fx + 3, 0, 28, max(0, gap_y - gap_h // 2))
                        rect_baixo = pygame.Rect(x_fx + 3, gap_y + gap_h // 2, 28, ALTURA_VIRTUAL - (gap_y + gap_h // 2))
                        if hitbox_jogador.colliderect(rect_cima) or hitbox_jogador.colliderect(rect_baixo):
                            if jogador.escudo_hits > 0:
                                jogador.escudo_hits -= 1
                                faixa["warning"] = 999
                                faixa["x"] = -100
                                criar_explosao_particulas(jogador.rect.centerx, jogador.rect.centery, (120, 240, 255), 16, particulas, pool_manager)
                            else:
                                disparar_vibracao(0.5, dados.get("vibracao", True))
                                aplicar_shake(25, 15)
                                criar_explosao_particulas(jogador.rect.centerx, jogador.rect.centery, cor_jogador, 30, particulas, pool_manager)
                                aprendizado_contextual.registrar("laser_corredor")
                                jogador.iniciar_morte()
                                encerrar_desafio_laser(False)
                                break

                # Quase colisão: distância mínima entre hitboxes sem sobreposição.
                # A marca por obstáculo impede contar a mesma passagem em vários ticks.
                em_voo_jetpack = jogador.tempo_jetpack > 0 or jogador.jetpack_pousando > 0
                if not em_voo_jetpack:
                    for obs in list(obstaculos):
                        if getattr(obs, "_combo_quase_processada", False):
                            continue
                        if obstaculo_encosta_jogador(hitbox_jogador, obs):
                            obs._perfeita_colidiu = True
                            continue
                        dist_quase_d2 = distancia_quadrada_hitboxes(hitbox_jogador, obs)
                        EsquivaPerfeita.observar(obs, dist_quase_d2)
                        if dist_quase_d2 <= 18 * 18:
                            # Guarda a aproximação, mas só premia quando o perigo já passou.
                            # Assim, uma colisão no tick seguinte não vira um falso bônus.
                            obs._combo_quase_candidato = True
                        if (getattr(obs, "_combo_quase_candidato", False) and
                                obs.rect.right <= hitbox_jogador.left):
                            obs._combo_quase_processada = True
                            combo_quase_colisoes += 1
                            registrar_acao_combo("QUASE", obs.rect.centerx, obs.rect.centery)
                            if EsquivaPerfeita.concluiu(obs):
                                # É um grau superior da QUASE existente, sem duplicar combo.
                                esquivas_perfeitas += 1
                                moedas_coletadas += 3
                                efeito_esquiva_ate = frame_count + 70
                                textos_flut.add(TextoFlutuante(
                                    jogador.rect.centerx + 40, max(135, jogador.rect.y - 34),
                                    'ESQUIVA PERFEITA! +3', (255, 231, 130), 'grande'))

                if portal_tipo_ativo is None:
                    for portal in list(portais_bonus):
                        if portal.alive() and hitbox_jogador.colliderect(portal.rect):
                            portal_tipo_ativo = portal.tipo
                            portal_proximo_metro = int(metros_atuais + 5000)
                            portal_transicao_timer = 72
                            portal_transicao_tipo = "ENTRANDO"
                            portal_timer = 600
                            portal_y = float(jogador.rect.centery)
                            portal_vy = 0.0
                            portal_pontos = 0
                            portal_pipe_spawn = 1
                            portal_falhou = False
                            portal_chefe_ativo = False
                            portal_chefe_hp = 0
                            portal_chefe_ataque = 0
                            portal_pipes = []
                            portal.kill()
                            textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 220, f"FASE {portal_tipo_ativo}!", PortalBonus.CORES[portal_tipo_ativo], "grande"))
                            gerenciador_sons.tocar_som("novo_recorde", False, dados["vol_sfx"])
                            for grupo_limpeza in (obstaculos, perigos_especiais, buracos):
                                for item_limpeza in list(grupo_limpeza):
                                    item_limpeza.kill()

                if (dados.get("pet_equipado") == "ABELHA_MAGNETICA") and frame_count % 90 == 0:
                    pet_habilidade_ate = frame_count + 27
                    # Pulso limitado: move apenas moedas próximas, sem varrer grupos em todos os frames.
                    for moeda_pulso in list(moedas):
                        if 0 < moeda_pulso.rect.centerx - jogador.rect.centerx < 180 and abs(moeda_pulso.rect.centery - jogador.rect.centery) < 170:
                            moeda_pulso.rect.x -= min(24, max(6, (moeda_pulso.rect.centerx - jogador.rect.centerx) // 5))
                for m in list(moedas):
                    if hitbox_jogador.colliderect(m.rect):
                        m.ativo = False
                        m.kill()
                        moedas_base = (2 if jogador.tempo_mult > 0 else 1) * (2 if febre_timer > 0 else 1)
                        multiplicador_bioma = BIOMAS_LENDARIOS.get(bioma_lendario_ativo, {}).get("recompensa", 1.0)
                        if dados.get("reliquia_equipada") == "MAPA_ABISSAL" and (m.rect.centery < ALTURA_VIRTUAL - 190):
                            multiplicador_bioma *= 1.08
                        if dados.get("reliquia_equipada") == "PEROLA_ABISSAL" and bioma_lendario_ativo:
                            multiplicador_bioma *= 1.15
                        moedas_coletadas += max(1, int(moedas_base * multiplicador_bioma))
                        if dados.get("pet_equipado") == "BOLHA":
                            moedas_pet_contador += 1
                            intervalo_pet = max(2, 6 - nivel_pet(dados, "BOLHA"))
                            if moedas_pet_contador >= intervalo_pet:
                                moedas_coletadas += 1
                                moedas_pet_contador = 0
                                pet_habilidade_ate = frame_count + 30
                        registrar_acao_combo("MOEDA", m.rect.centerx, m.rect.centery)
                        gerenciador_sons.tocar_som("moeda", jogador.tempo_slow > 0, dados["vol_sfx"])
                        criar_explosao_particulas(m.rect.centerx, m.rect.centery, AMARELO_MOEDA,
                                                  4 if modo_grafico_leve(dados) else 10, particulas, pool_manager)
                        for missao in missoes_atuais:
                            if missao["tipo"] == "MOEDAS": missao["atual"] += 1

                letra_pega, palavra_completa, bonus_letras = palavra_partida.coletar(hitbox_jogador, metros_atuais)
                if letra_pega:
                    palavra_hud_ate = frame_count + 300
                    criar_explosao_particulas(jogador.rect.centerx + 25, jogador.rect.y - 8,
                                              (255, 220, 100), 18, particulas, pool_manager)
                    gerenciador_sons.tocar_som("moeda", False, dados["vol_sfx"])
                    if palavra_completa:
                        palavra_festa_ate = frame_count + 180
                        criar_explosao_particulas(LARGURA_VIRTUAL // 2, 145,
                                                  (255, 232, 103), 46, particulas, pool_manager)
                        moedas_coletadas += bonus_letras
                        textos_flut.add(TextoFlutuante(jogador.rect.centerx, jogador.rect.top - 36,
                            f"{palavra_partida.palavra}! +{bonus_letras}", AMARELO_MOEDA, "grande"))
                        gerenciador_sons.tocar_som("novo_recorde", False, dados["vol_sfx"])
                for bau in list(baus_secretos):
                    if bau.alive() and hitbox_jogador.colliderect(bau.rect):
                        bau.kill()
                        baus_abertos_rodada += 1
                        recompensa_bau = random.randint(25, 60)
                        moedas_coletadas += recompensa_bau
                        febre_carga = min(100.0, febre_carga + 1.0 / FEBRE_DIFICULDADE)
                        textos_flut.add(TextoFlutuante(bau.rect.centerx, bau.rect.centery - 25,
                                                       f"{t('bau_aberto', dados)} +{recompensa_bau}",
                                                       AMARELO_MOEDA, "grande"))
                        criar_explosao_particulas(bau.rect.centerx, bau.rect.centery, AMARELO_MOEDA, 18,
                                                  particulas, pool_manager)
                        gerenciador_sons.tocar_som("missao", False, dados["vol_sfx"])

                for p in list(powerups):
                    if p.alive() and not powerup_desbloqueado(dados, p.tipo):
                        p.kill()  # segurança para objetos oriundos de saves/testes antigos
                        continue
                    if p.alive() and hitbox_jogador.colliderect(p.rect):
                        p.kill()
                        jogador.ativar_powerup(p.tipo, gerenciador_sons, dados["vol_sfx"], dados.get("vibracao", True))
                        gamefeel.impacto(4.0, direcao_x=-0.4, direcao_y=-0.3, congelar=False)
                        if p.tipo == "JETPACK":
                            # Libera a pista e garante alguns segundos sem novos perigos após o pouso.
                            spawn_bloqueado_frames = (jogador.tempo_jetpack + jogador.jetpack_subida_duracao +
                                                       jogador.jetpack_descida_duracao + 180)
                            for obs in list(obstaculos):
                                obs.kill()
                            for perigo in list(perigos_especiais):
                                perigo.kill()
                            for buraco in list(buracos):
                                buraco.kill()
                            for moeda_antiga in list(moedas):
                                moeda_antiga.kill()
                            for powerup_antigo in list(powerups):
                                powerup_antigo.kill()
                        nome_p = t(UPGRADES_CONFIG[p.tipo]["nome_key"], dados)
                        textos_flut.add(TextoFlutuante(jogador.rect.centerx, jogador.rect.top - 15, f"+ {nome_p}!",
                                                       UPGRADES_CONFIG[p.tipo]["cor"]))

                em_voo_jetpack = jogador.tempo_jetpack > 0 or jogador.jetpack_pousando > 0
                if (desafio_laser_ativo or em_voo_jetpack or portal_tipo_ativo is not None or
                        jogador_invencivel_por_velocidade(jogador, febre_timer,
                                                          febre_turbo_distancia_restante)):
                    hit_obs = []
                    hit_laser = []
                else:
                    hit_obs = [obs for obs in obstaculos if obstaculo_encosta_jogador(hitbox_jogador, obs)]
                    hit_laser = [l for l in perigos_especiais if
                                 hasattr(l, 'ativo') and l.ativo and hitbox_jogador.colliderect(hitbox_disparo_laser(l))]
                todos_hits = hit_obs + hit_laser

                if todos_hits:
                    if jogador.tempo_impulso > 0:
                        obstaculos_destruidos_rodada += len(hit_obs)
                        for h in todos_hits:
                            criar_explosao_particulas(h.rect.centerx, h.rect.centery, (100, 235, 220), 12, particulas, pool_manager)
                            h.kill()
                        textos_flut.add(TextoFlutuante(jogador.rect.centerx, jogador.rect.top - 22, "IMPULSO!", (100, 235, 220), "normal"))
                    elif jogador.prisma_hits > 0:
                        jogador.prisma_hits -= 1
                        obstaculos_destruidos_rodada += len(hit_obs)
                        for h in todos_hits:
                            criar_explosao_particulas(h.rect.centerx, h.rect.centery, (190, 120, 255), 16, particulas, pool_manager)
                            h.kill()
                        for obs in list(obstaculos):
                            if abs(obs.rect.centerx - jogador.rect.centerx) < 95:
                                obs.kill()
                        textos_flut.add(TextoFlutuante(jogador.rect.centerx, jogador.rect.top - 25, "ESCUDO PRISMÁTICO!", (190, 120, 255), "grande"))
                    elif jogador.tempo_turbo_fantasma > 0:
                        obstaculos_destruidos_rodada += len(hit_obs)
                        for h in todos_hits:
                            criar_explosao_particulas(h.rect.centerx, h.rect.centery, (180, 225, 255), 12, particulas, pool_manager)
                            h.kill()
                    elif jogador.tempo_turbo > 0:
                        for h in hit_obs:
                            criar_explosao_particulas(h.rect.centerx, h.rect.centery, VERDE_CACTO, 16, particulas,
                                                      pool_manager)
                            # Turbo abre um corte real na geometria SDF; a máscara
                            # de colisão remanescente acompanha o sprite.
                            try:
                                ainda_existe = esculpir_obstaculo(
                                    h, hitbox_jogador.centerx, hitbox_jogador.centery,
                                    raio=max(25, min(52, h.rect.width // 2 + 8)))
                            except (ImportError, ValueError, pygame.error):
                                ainda_existe = False
                            if not ainda_existe:
                                h.kill()
                            gerenciador_sons.tocar_som("quebrar", jogador.tempo_slow > 0, dados["vol_sfx"])
                            aplicar_shake(10, 5)
                            cactos_destruidos = getattr(h, 'qtd_cactos', 1)
                            for missao in missoes_atuais:
                                if missao["tipo"] == "QUEBRAR": missao["atual"] += cactos_destruidos
                    elif jogador.clones_ativos > 0:
                        obstaculos_destruidos_rodada += len(hit_obs)
                        # Um clone absorve o impacto inicial e desencadeia uma cadeia
                        # limitada de destruição à frente. O processamento só ocorre
                        # durante uma colisão, evitando custo extra no loop normal.
                        jogador.clones_ativos -= 1
                        disparar_vibracao(0.18, dados.get("vibracao", True))
                        aplicar_shake(8, 4)
                        unidades_destruidas = 0
                        ultimo_x = max(h.rect.centerx for h in todos_hits)
                        ultimo_y = sum(h.rect.centery for h in todos_hits) // len(todos_hits)

                        for h in todos_hits:
                            cor_impacto = (120, 235, 255) if h in hit_laser else VERDE_CACTO
                            criar_explosao_particulas(h.rect.centerx, h.rect.centery, cor_impacto, 14, particulas, pool_manager)
                            h.kill()
                            unidades = max(1, int(getattr(h, 'qtd_cactos', 1))) if h in hit_obs else 1
                            unidades_destruidas += unidades
                            if h in hit_obs:
                                for missao in missoes_atuais:
                                    if missao["tipo"] == "QUEBRAR":
                                        missao["atual"] += unidades

                        # Cada nível do upgrade amplia a cadeia em um alvo; o nível
                        # base já pode destruir até dois perigos adicionais próximos.
                        nivel_clone = max(0, int(jogador.upgrades.get("CLONE", 0)))
                        limite_cadeia = 2 + nivel_clone
                        alvos_cadeia = 0
                        perigos_disponiveis = list(obstaculos) + [
                            l for l in perigos_especiais if getattr(l, 'ativo', False)
                        ]
                        perigos_disponiveis.sort(key=lambda alvo: alvo.rect.left)
                        while alvos_cadeia < limite_cadeia:
                            candidato = None
                            for alvo in perigos_disponiveis:
                                if not getattr(alvo, 'alive', lambda: True)():
                                    continue
                                dx = alvo.rect.centerx - ultimo_x
                                dy = abs(alvo.rect.centery - ultimo_y)
                                if 0 <= dx <= 210 and dy <= 145:
                                    candidato = alvo
                                    break
                            if candidato is None:
                                break

                            perigos_disponiveis.remove(candidato)
                            ultimo_x, ultimo_y = candidato.rect.centerx, candidato.rect.centery
                            era_obstaculo = candidato in obstaculos
                            cor_cadeia = (255, 218, 90) if era_obstaculo else (120, 235, 255)
                            criar_explosao_particulas(candidato.rect.centerx, candidato.rect.centery,
                                                      cor_cadeia, 12, particulas, pool_manager)
                            unidades = max(1, int(getattr(candidato, 'qtd_cactos', 1))) if era_obstaculo else 1
                            candidato.kill()
                            unidades_destruidas += unidades
                            alvos_cadeia += 1
                            if era_obstaculo:
                                for missao in missoes_atuais:
                                    if missao["tipo"] == "QUEBRAR":
                                        missao["atual"] += unidades
                            # A busca continua a partir do alvo destruído, criando
                            # uma sequência espacial em vez de limpar a tela inteira.

                        # Bônus cresce com cada unidade destruída: 2 moedas por alvo
                        # equivalente e +1 por elo de cadeia além do primeiro.
                        bonus_moedas_clone = unidades_destruidas * 2 + max(0, alvos_cadeia - 1)
                        if bonus_moedas_clone > 0:
                            moedas_coletadas += bonus_moedas_clone
                            textos_flut.add(TextoFlutuante(
                                jogador.rect.centerx + 18, jogador.rect.top - 58,
                                f"CADEIA x{unidades_destruidas}! +{bonus_moedas_clone} {t('moedas_hud', dados)}",
                                (255, 215, 90), "grande"))
                        textos_flut.add(TextoFlutuante(
                            jogador.rect.centerx, jogador.rect.top - 28,
                            f"{t('clone_perdido', dados)} {jogador.clones_ativos} {t('clones_restantes', dados)}",
                            (120, 235, 255), "grande"))
                        if gerenciador_sons:
                            gerenciador_sons.tocar_som("quebrar", jogador.tempo_slow > 0, dados["vol_sfx"])
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
                    elif (dados.get("pet_equipado") == "FANTASMA") and not pet_salvou_vida_rodada:
                        pet_salvou_vida_rodada = True
                        pet_habilidade_ate = frame_count + 65
                        jogador.escudo_hits = max(jogador.escudo_hits, nivel_pet(dados, "FANTASMA") // 2)
                        for h in todos_hits:
                            h.kill()
                        jogador.rect.bottom = jogador.chao_y
                        jogador.velocidade_y = 0
                        jogador.no_chao = True
                        pet_salvador = "FANTASMA"
                        cor_pet_salva = PETS_CONFIG["FANTASMA"]["cor"]
                        criar_explosao_particulas(jogador.rect.centerx, jogador.rect.centery, cor_pet_salva, 22, particulas, pool_manager)
                        textos_flut.add(TextoFlutuante(jogador.rect.centerx, jogador.rect.top - 30,
                            "FANTASMA SALVOU VOCÊ!", cor_pet_salva, "grande"))
                    else:
                        disparar_vibracao(0.5, dados.get("vibracao", True))  # Vibração de colisão / game over
                        aplicar_shake(25, 15)
                        criar_explosao_particulas(jogador.rect.centerx, jogador.rect.centery, cor_jogador, 30,
                                                  particulas, pool_manager)
                        if hit_obs:
                            aprendizado_contextual.registrar("obstaculo", hit_obs[0])
                        elif hit_laser:
                            aprendizado_contextual.registrar("laser_perigo")
                        jogador.iniciar_morte()
            else:
                if (not (modo_desenvolvedor and dev_imortalidade) and
                        (jogador.tempo_morte <= 0 or jogador.rect.top > ALTURA_VIRTUAL)):
                    if estado != "GAMEOVER":
                        estado = "GAMEOVER"
                        metricas_corrida.encerrar(
                            quadro=frame_count, bioma=cenario_atual, distancia_m=metros_atuais,
                            moedas=moedas_coletadas, maior_combo=combo_melhor,
                            quase_colisoes=combo_quase_colisoes, esquivas=esquivas_perfeitas,
                            powerups=getattr(jogador, "powerups_coletados", 0),
                            obstaculos_destruidos=obstaculos_destruidos_rodada,
                            fases_bonus=fases_bonus_rodada, chefes=chefes_derrotados_rodada,
                            portais=portal_tipo_contagem_rodada, febres=febre_ativacoes_rodada,
                            baus=baus_abertos_rodada)
                        # Apenas recorde local do código; sem recompensas extras.
                        desafio_compartilhado.registrar_morte(dados, metros_atuais)
                        dados["moedas_totais"] = 999999999 if (modo_desenvolvedor and dev_dinheiro_infinito) else dados["moedas_totais"] + moedas_coletadas
                        stats = dados.setdefault("estatisticas_permanentes", {})
                        stats["partidas"] = int(stats.get("partidas", 0)) + 1
                        stats_extra = dados.setdefault("estatisticas_novas", {"chefes_derrotados": 0, "biomas_lendarios": 0})
                        stats_extra["chefes_derrotados"] = int(stats_extra.get("chefes_derrotados", 0)) + chefes_derrotados_rodada
                        stats_extra["biomas_lendarios"] = int(stats_extra.get("biomas_lendarios", 0)) + biomas_lendarios_rodada
                        stats["eventos_vulcao"] = int(stats.get("eventos_vulcao", 0)) + eventos_vulcao_rodada
                        stats["febres_cometa"] = int(stats.get("febres_cometa", 0)) + febre_ativacoes_rodada
                        adicionar_xp_pet(dados, max(1, int(metros_atuais // 10) + fases_bonus_rodada * 30 + chefes_derrotados_rodada * 100))
                        vinculo_por_corrida(dados, metros_atuais, moedas_coletadas, febre_ativacoes_rodada)
                        atualizar_ranking_local(dados, {"distancia": int(metros_atuais), "moedas": int(moedas_coletadas), "combo": int(combo_melhor), "chefes": int(chefes_derrotados_rodada), "reliquias": len(dados.get("reliquias_desbloqueadas", []))})
                        desafios_rank = dados.setdefault("desafios_ranking_concluidos", [])
                        objetivos_rank = (("DISTANCIA_500", metros_atuais >= 500, 100),
                                          ("COMBO_30", combo_melhor >= 30, 150),
                                          ("CHEFE_1", chefes_derrotados_rodada >= 1, 250),
                                          ("MOEDAS_500", moedas_coletadas >= 500, 200))
                        for id_rank, cumpriu_rank, premio_rank in objetivos_rank:
                            if cumpriu_rank and id_rank not in desafios_rank:
                                desafios_rank.append(id_rank)
                                dados["moedas_totais"] += premio_rank
                        stats["distancia_total"] = int(stats.get("distancia_total", 0)) + metros_atuais
                        stats["moedas_coletadas"] = int(stats.get("moedas_coletadas", 0)) + moedas_coletadas
                        stats["quase_colisoes"] = int(stats.get("quase_colisoes", 0)) + combo_quase_colisoes
                        stats["bau_abertos"] = int(stats.get("bau_abertos", 0)) + baus_abertos_rodada
                        stats["febres"] = int(stats.get("febres", 0)) + febre_ativacoes_rodada
                        stats["melhor_combo"] = max(int(stats.get("melhor_combo", 0)), combo_melhor)
                        stats["powerups"] = int(stats.get("powerups", 0)) + int(getattr(jogador, "powerups_coletados", 0))
                        stats["obstaculos_destruidos"] = int(stats.get("obstaculos_destruidos", 0)) + obstaculos_destruidos_rodada
                        stats["fases_bonus"] = int(stats.get("fases_bonus", 0)) + fases_bonus_rodada
                        stats["recorde_febres_rodada"] = max(int(stats.get("recorde_febres_rodada", 0)), febre_ativacoes_rodada)
                        for tipo_portal, qtd_portal in portal_tipo_contagem_rodada.items():
                            chave_stat_portal = "portais_aquaticos" if tipo_portal == "AQUATICO" else "portais_lasers"
                            stats[chave_stat_portal] = int(stats.get(chave_stat_portal, 0)) + int(qtd_portal)
                        recordes = dados.setdefault("recordes_biomas", {"cidade": 0, "deserto": 0, "neve": 0})
                        recompensas_biomas = dados.setdefault("recompensas_biomas", [])
                        for bioma_nome, ticks_bioma in bioma_metros_rodada.items():
                            distancia_bioma = int(ticks_bioma // 10)
                            stats[bioma_nome + "_total"] = int(stats.get(bioma_nome + "_total", 0)) + distancia_bioma
                            recordes[bioma_nome] = max(int(recordes.get(bioma_nome, 0)), distancia_bioma)
                            marcos_atingidos = distancia_bioma // 250
                            # Maestria permanente: 3 patamares por bioma, com recompensa única.
                            maestrias = dados.setdefault("maestria_biomas", {})
                            distancia_total_bioma = int(stats.get(bioma_nome + "_total", 0))
                            nivel_maestria = 3 if distancia_total_bioma >= 10000 else 2 if distancia_total_bioma >= 4000 else 1 if distancia_total_bioma >= 1000 else 0
                            progresso_maestria = maestrias.setdefault(bioma_nome, {"nivel": 0, "recompensas": []})
                            if nivel_maestria > int(progresso_maestria.get("nivel", 0)):
                                premio_maestria = {1: 100, 2: 250, 3: 500}[nivel_maestria]
                                dados["moedas_totais"] += premio_maestria
                                progresso_maestria["nivel"] = nivel_maestria
                                progresso_maestria.setdefault("recompensas", []).append(nivel_maestria)
                                textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 265, f"MAESTRIA {nome_cenario(bioma_nome)} NIVEL {nivel_maestria} +{premio_maestria}", (125, 230, 255), "grande"))
                            for marco in range(1, marcos_atingidos + 1):
                                chave_recompensa = f"{bioma_nome}_{marco}"
                                if chave_recompensa in recompensas_biomas:
                                    continue
                                recompensas_biomas.append(chave_recompensa)
                                bonus_base = {"cidade": 75, "deserto": 100, "neve": 125, "vulcao": 150, "cidade_futurista": 160, "floresta": 145, "reino_submerso": 170, "ilhas_celestes": 175}.get(bioma_nome, 75)
                                bonus_bioma = bonus_base + (marco - 1) * 25
                                dados["moedas_totais"] += bonus_bioma
                        # Skins nunca são liberadas automaticamente no fim da corrida.
                        # Compráveis: compra na loja; de objetivo: resgate manual na loja.
                        stats["skins_desbloqueadas"] = len(dados["skins_desbloqueadas"])
                        if int(stats.get("partidas", 0)) >= 100 and "FANTASMA" not in dados["pets_desbloqueados"]:
                            pass  # Pets de objetivo são resgatados na aba Pets após atingir o requisito.
                        # Desbloqueios por objetivos são permanentes e não exigem moedas.
                        stats["pets_desbloqueados"] = len(dados.get("pets_desbloqueados", []))
                        for pet_id, pet_info in PETS_CONFIG.items():
                            if pet_id in dados.get("pets_desbloqueados", []):
                                continue
                            requisito = pet_info.get("objetivo") or ""
                            requisito_ok = ((pet_id == "FANTASMA" and stats.get("partidas", 0) >= 100) or
                                            (pet_id == "TARTARUGA" and stats.get("portais_aquaticos", 0) >= 25) or
                                            (pet_id == "DRAGAO" and stats.get("melhor_combo", 0) >= 100 and stats.get("febres", 0) >= 100) or
                                            (pet_id == "GOLEM" and dados.get("estatisticas_novas", {}).get("chefes_derrotados", 0) >= 10) or
                                            (pet_id == "DRAGAO_PLASMA" and stats.get("obstaculos_destruidos", 0) >= 250) or
                                            (pet_id == "GATO_FANTASMA" and stats.get("partidas", 0) >= 50))
                            if requisito_ok:
                                dados.setdefault("pets_desbloqueados", []).append(pet_id)
                        stats["pets_desbloqueados"] = len(dados.get("pets_desbloqueados", []))
                        stats_extra = dados.setdefault("estatisticas_novas", {"chefes_derrotados": 0, "biomas_lendarios": 0})
                        stats_extra["fragmentos_reliquia"] = int(stats_extra.get("fragmentos_reliquia", 0))
                        for rid, info_rel in RELIQUIAS_CONFIG.items():
                            progresso_rel = int(stats_extra.get(info_rel["stat"], stats.get(info_rel["stat"], 0)))
                            if progresso_rel >= info_rel["alvo"] and rid not in dados.setdefault("reliquias_desbloqueadas", []):
                                dados["reliquias_desbloqueadas"].append(rid)
                        novas_conquistas = processar_conquistas(dados)
                        for _, recompensa_conquista in novas_conquistas:
                            textos_flut.add(TextoFlutuante(LARGURA_VIRTUAL // 2, 200,
                                                           f"{t('conquista_desbloqueada', dados)} +{recompensa_conquista}",
                                                           AMARELO_NEON, "grande"))
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
        elif estado in ["INICIO", "LOJA", "UPGRADES", "CONFIG", "CONFIG_CONTROLES", "CONFIG_ACESSIBILIDADE", "CONQUISTAS", "RECORDES", "DESAFIOS", "DESAFIO_PERCURSO", "RANKING", "RELIQUIAS", "BASE_CORREDOR", "CANTINHO_PETS"]:
            if bg_parallax.cenario != "cidade":
                bg_parallax.set_cenario("cidade")
            bg_parallax.update(1.2)

    global PARTICULAS_VISUAIS_LIMITADAS
    # A simulacao usa passo fixo de 60 Hz; a imagem e renderizada separadamente.
    PASSO_FIXO = 1.0 / 60.0
    MAX_TEMPO_ACUMULADO = 0.25
    # Android: limitar o custo de quadros de recuperacao sem alterar a fisica
    # de cada passo fixo (60 Hz) nem os temporizadores da corrida.
    # A 10 FPS sao 6 ticks de 60 Hz por quadro: 4 desacelerava a corrida.
    # Preservar o passo fixo, hitboxes e velocidade; permitir recuperacao de 8.
    MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15
    FPS_RENDER = 30 if E_ANDROID else 60
    sim_acumulado = 0.0

    # Gera a arte animada do titulo antes do primeiro frame visivel. Em celulares
    # lentos, o cache inicial de 125 quadros podia consumir tanto tempo que a
    # animacao do menu ja terminava antes de aparecer. Os quadros continuam cacheados.
    try:
        superficie_preparacao_titulo = pygame.Surface(
            (LARGURA_VIRTUAL, ALTURA_VIRTUAL), pygame.SRCALPHA
        )
        desenhar_titulo_pixel_art(
            superficie_preparacao_titulo, LARGURA_VIRTUAL // 2, 95, 0
        )
        del superficie_preparacao_titulo
    except Exception:
        # Se a pre-renderizacao nao estiver disponivel, o titulo ainda desenha sob demanda.
        pass

    ultimo_tempo_loop_ms = _rep_relogio(pygame.time.get_ticks())
    # Diagnóstico 100% opt-in: desativado não cria buffers nem grava arquivos.
    monitor_diag = (MonitorDiagnostico.from_environment()
                    if os.environ.get('PIXELRUSH_DIAGNOSTICO', '0') == '1' else None)

    # Fechamento 32 #22: pré-carregar somente arte já autorizada,
    # na tela de menu, em microtarefas independentes. Não antecipar
    # animação do gameplay, compras, dados salvos ou sorteio.
    _qa_precarga_visuais = None
    if E_ANDROID and os.environ.get('PIXELRUSH_QA_ANDROID','0')=='1' and (
            os.environ.get('PIXELRUSH_QA_PRELOAD_VISUAL','1')=='1'):
        from pixelrush_qa_precarregamento_visual_v327757 import PrecargaVisuaisQA
        from pixelrush_qa_pet_preload_v327769 import preparar_pet_compativel

        def _qa_preparar_pet_menu(pet_id):
            # Studio real ainda e COMING SOON: preparar SOMENTE as
            # Surfaces transparentes usadas na corrida e no popup.
            # Nao reativa pets nem altera sprites, saves, estados ou RNG.
            return preparar_pet_compativel(
                pet_id, pet5_precarregar, _quadros_pet_estado)

        _qa_precarga_visuais = PrecargaVisuaisQA(
            dados.get('skin_equipada','AZUL'), SKINS_ATIVAS_PROD,
            dados.get('pet_equipado'), _quadros_skin, _qa_preparar_pet_menu,
            aquecer_tiles=True)

    # QA771: preflight da camera antes do loop, apenas Android QA.
    # Nao altera zoom, jogo ou render caso nao haja ganho pixel-identico.
    if (E_ANDROID and os.environ.get('PIXELRUSH_QA_ANDROID','0')=='1'
            and os.environ.get('PIXELRUSH_QA_CAMERA_AUTOTUNE','1')=='1'):
        try:
            from pixelrush_qa_camera_v327733 import preparar_fora_do_frame as _qa_camera_boot_bench
            os.environ.setdefault('PIXELRUSH_QA_CAMERA_AUTOTUNE','1')
            _qa_w,_qa_h=display_surface.get_size()
            _qa_camera_boot_bench(display_surface,(_qa_w+18,_qa_h+32))
        except (pygame.error,ValueError,MemoryError,RuntimeError,OSError):
            # Fallback seguro: nao impedir o tutorial por falha QA.
            pass

    rodando = True
    while rodando:
        if _qa_precarga_visuais is not None and estado in ('INICIO','LOJA','CONFIG','UPGRADES'):
            _qa_precarga_visuais.passo(estado)
        # Somente rótulo de telemetria: replay não executa a simulação da corrida.
        # Fisica, eventos, sorteio, renderizacao e replay permanecem intocados.
        _qa_estado = ("JOGANDO_TUTORIAL_QA" if
                      estado == "JOGANDO" and tutorial_corrida and tutorial_corrida.ativo
                      else "GAMEOVER_REPLAY_QA" if
                      estado == "GAMEOVER" and
                      (replay_morte.ativo or
                       (not replay_morte.congelado and bool(replay_morte.buffer)))
                      else estado)
        _pro_inicio(_qa_estado, cenario_atual)
        perf_biomas.iniciar(estado, cenario_atual)
        _forense_quadro(estado, cenario_atual, pontuacao // 10,
                        'leve' if PARTICULAS_VISUAIS_LIMITADAS else 'normal')
        if monitor_diag is not None:
            monitor_diag.iniciar_quadro()
        agora_loop_ms = _rep_inicio(pygame.time.get_ticks())
        tempo_decorrido = max(0.0, min((agora_loop_ms - ultimo_tempo_loop_ms) / 1000.0,
                                      MAX_TEMPO_ACUMULADO))
        ultimo_tempo_loop_ms = agora_loop_ms
        sim_acumulado = min(sim_acumulado + tempo_decorrido, MAX_TEMPO_ACUMULADO)
        MONITOR_QUALIDADE_VISUAL.atualizar(relogio.get_fps(), tempo_decorrido,
                                           dados.get('modo_grafico', 'auto'), estado == 'JOGANDO')
        PARTICULAS_VISUAIS_LIMITADAS = modo_grafico_leve(dados)

        largura_atual_tela, altura_atual_tela = tela.get_size()

        if E_ANDROID:
            largura_render = largura_atual_tela
            altura_render = altura_atual_tela
            offset_x = 0
            offset_y = 0
        else:
            escala = min(largura_atual_tela / LARGURA_VIRTUAL, altura_atual_tela / ALTURA_VIRTUAL)
            # Protege janelas transitórias de 0/1 px em troca de resolução/emulador.
            largura_render = max(1, int(LARGURA_VIRTUAL * escala))
            altura_render = max(1, int(ALTURA_VIRTUAL * escala))
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
            if estado in ["INICIO", "LOJA", "UPGRADES", "CONFIG", "CONFIG_CONTROLES", "CONFIG_ACESSIBILIDADE", "CONQUISTAS", "RECORDES", "DESAFIOS", "DESAFIO_PERCURSO", "RANKING", "RELIQUIAS", "BASE_CORREDOR", "CANTINHO_PETS"]:
                anim_menu_tempo = 0
            # Invalida cenas congeladas ao entrar/sair de qualquer estado.
            cache_telas_estaticas.clear()
            estado_anterior = estado

        skin_nome_atual = dados["skin_equipada"]
        cor_jogador = SKINS.get(skin_nome_atual, SKINS["AZUL"])["cor"]
        metros_atuais = pontuacao // 10

        e_slow = (jogador.tempo_slow > 0) if jogador else False
        _pro_marcar("audio")
        gerenciador_sons.atualizar_musica(estado, e_slow, dados["vol_musica"], cenario_atual, clima.tipo, portal_chefe_ativo)
        musica_diretor.atualizar(gerenciador_sons, estado, dados['vol_musica'], vel_jogo,
                                combo_contagem, portal_chefe_ativo or e_slow, cenario_atual,
                                novo_recorde_alcançado)
        gerenciador_sons.mixagem_contextual.atualizar(gerenciador_sons, estado)

        if estado == "JOGANDO":
            novo_tempo_spawn = max(900, 1500 - (metros_atuais // 300) * 25)
            if novo_tempo_spawn != tempo_spawn_atual and not (tutorial_corrida and tutorial_corrida.ativo):
                tempo_spawn_atual = novo_tempo_spawn
                pygame.time.set_timer(EVENTO_GERAR, tempo_spawn_atual)

        fase_ciclo, cor_objetivo_ceu, peso_noite, e_noite = calcular_ciclo_ceu(metros_atuais)
        alvo_ceu = list(cor_objetivo_ceu)
        bg_parallax.fase_ciclo = fase_ciclo
        bg_parallax.peso_noite = peso_noite
        bg_parallax.clima_tipo = clima.tipo

        cor_ceu_tupla = (int(cor_atual_ceu[0]), int(cor_atual_ceu[1]), int(cor_atual_ceu[2]))

        _pro_marcar("simulacao")
        # Executa os ticks acumulados antes de aplicar os eventos recem-chegados,
        # para nao aplicar um toque novo retroativamente ao tempo anterior.
        passos_simulacao = 0
        _pro_sub_inicio("qa_simulacao_ticks")
        while sim_acumulado + 1e-9 >= PASSO_FIXO and passos_simulacao < MAX_PASSOS_POR_FRAME and rodando:
            atualizar_simulacao()
            sim_acumulado -= PASSO_FIXO
            passos_simulacao += 1
        _pro_sub_fim()
        if E_ANDROID and passos_simulacao == MAX_PASSOS_POR_FRAME:
            # Descartar backlog antigo evita a espiral de travamentos quando
            # o celular nao consegue processar quinze ticks antes de desenhar.
            sim_acumulado = min(sim_acumulado, PASSO_FIXO)

        _pro_marcar("entrada")
        for evento in _rep_eventos(pygame.event.get()):
            # O clique em JOGAR não pode transformar o MOUSEBUTTONUP residual
            # em um pulo no primeiro quadro da nova corrida.
            if (estado == 'JOGANDO' and frame_count < entrada_corrida_ate - 57
                    and evento.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP,
                                        pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN)):
                continue
            if (estado == "JOGANDO" and tutorial_corrida is not None and tutorial_corrida.ativo
                    and evento.type not in (pygame.QUIT, pygame.ACTIVEEVENT,
                                            APP_WILLENTERBACKGROUND, APP_DIDENTERBACKGROUND,
                                            APP_WILLENTERFOREGROUND, APP_DIDENTERFOREGROUND)):
                # Todos os controles passam pelo roteiro: não é possível pular,
                # interromper ou acionar comandos de gameplay durante as lições.
                tutorial_corrida.processar_evento(
                    evento, lambda pos: screen_to_virtual(*pos), gerenciador_sons,
                    dados.get("vol_sfx", 0.7))
                continue
            if evento.type == pygame.QUIT:
                _forense_quit("pygame.QUIT")
                rodando = False

            if (APP_WILLENTERBACKGROUND and evento.type == APP_WILLENTERBACKGROUND) or \
                    (APP_DIDENTERBACKGROUND and evento.type == APP_DIDENTERBACKGROUND) or \
                    (evento.type == pygame.ACTIVEEVENT and hasattr(evento, 'gain') and evento.gain == 0):
                if estado == "JOGANDO":
                    estado = "PAUSA"
                mouse_drag_active = False
                mouse_start_pos = None
                mouse_current_pos = None
                mouse_hold_frames = 0
                mouse_jump_started = False
                mouse_gesture_moved = False
                mouse_gameplay_press = False
                mouse_input_ignored = False
                controle_dedos.reset()
                toque_ativo = False
                gamepad_pulo = gamepad_baixo = False
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
                                                                                     "CONFIG", "CONFIG_CONTROLES", "CONFIG_ACESSIBILIDADE", "LOJA", "UPGRADES"]:
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

                modo_touch = normalizar_modo(dados.get('controle_modo', 'CLASSICO')) if estado == 'JOGANDO' else MODO_CLASSICO
                r_pulo, r_baixo = botoes(dados)
                acao_dedo = controle_dedos.start(getattr(evento, 'finger_id', 0), pos_touch, modo_touch,
                                                  r_pulo, r_baixo, btn_pausa if estado == 'JOGANDO' else None)
                if acao_dedo != 'primario':
                    if estado == 'JOGANDO' and jogador:
                        if acao_dedo == 'pausa':
                            processar_clique_ui(pos_touch)
                        elif acao_dedo == 'pulo':
                            jogador.pular(gerenciador_sons, dados['vol_sfx'])
                        elif acao_dedo == 'baixo':
                            if jogador.no_chao:
                                gesto_agachar_frames = max(gesto_agachar_frames, 12)
                            else:
                                jogador.iniciar_descida_rapida(gerenciador_sons, dados['vol_sfx'])
                    continue
                touch_start_pos = pos_touch
                touch_current_pos = pos_touch
                touch_jetpack_anchor = pos_touch
                toque_ativo = True
                touch_hold_frames = 0
                touch_jump_started = False
                touch_gesture_moved = bool(
                    estado == "JOGANDO" and jogador and jogador.jetpack_fase is not None)
                jetpack_gesto_usado = False


            elif evento.type == pygame.FINGERMOTION:
                if controle_dedos.move(getattr(evento, 'finger_id', 0)) and toque_ativo:
                    pos_anterior_touch = touch_current_pos
                    if E_ANDROID:
                        touch_current_pos = (evento.x * LARGURA_VIRTUAL, evento.y * ALTURA_VIRTUAL)
                    else:
                        px = evento.x * largura_atual_tela
                        py = evento.y * altura_atual_tela
                        touch_current_pos = screen_to_virtual(px, py)
                    # Durante o voo, o ponto-âncora é atualizado a cada gesto para permitir
                    # subir e descer várias vezes sem soltar o dedo.
                    if (estado == "JOGANDO" and jogador and jogador.jetpack_fase == "voando" and
                            touch_jetpack_anchor is not None):
                        dy_jet = touch_current_pos[1] - touch_jetpack_anchor[1]
                        passos_jet = passos_jetpack(dy_jet)
                        if passos_jet:
                            for _ in range(abs(passos_jet)):
                                jogador.mover_jetpack(-1 if passos_jet < 0 else 1)
                            touch_jetpack_anchor = (touch_current_pos[0], ancorar_jetpack(
                                touch_jetpack_anchor[1], touch_current_pos[1], passos_jet))
                            jetpack_gesto_usado = True
                    elif (estado == 'JOGANDO' and jogador and touch_start_pos and
                          normalizar_modo(dados.get('controle_modo')) == MODO_GESTOS):
                        dy_gesto = touch_current_pos[1] - touch_start_pos[1]
                        if (dy_gesto < -(limiar(dados) + 10) and
                                not touch_jump_started and not touch_gesture_moved):
                            jogador.pular(gerenciador_sons, dados['vol_sfx'])
                            touch_jump_started = True
                            touch_gesture_moved = True
                        elif dy_gesto > limiar(dados) + 10 and not touch_gesture_moved:
                            if jogador.no_chao:
                                gesto_agachar_frames = max(gesto_agachar_frames, 12)
                            else:
                                jogador.iniciar_descida_rapida(gerenciador_sons, dados['vol_sfx'])
                            touch_gesture_moved = True

            elif evento.type == pygame.FINGERUP:
                acao_fim = controle_dedos.end(getattr(evento, 'finger_id', 0))
                if acao_fim != 'primario':
                    continue
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
                        if jogador.jetpack_fase is not None:
                            # Swipe vertical controla altitude durante o voo; não aciona salto.
                            if jogador.jetpack_fase == "voando" and not jetpack_gesto_usado:
                                passos_jet = passos_jetpack(dy)
                                for _ in range(abs(passos_jet)):
                                    jogador.mover_jetpack(-1 if passos_jet < 0 else 1)
                        elif dy < -(limiar(dados) + 10):
                            if (not touch_jump_started and not (
                                    touch_gesture_moved and
                                    normalizar_modo(dados.get('controle_modo')) == MODO_GESTOS)):
                                jogador.pular(gerenciador_sons, dados["vol_sfx"])
                        elif (dy > limiar(dados) + 10 and
                              not (touch_gesture_moved and normalizar_modo(dados.get('controle_modo')) == MODO_GESTOS)):
                            # No chao, um swipe curto tambem gera agachamento; no ar,
                            # interrompe o pulo longo e inicia a descida rapida.
                            if jogador.no_chao:
                                gesto_agachar_frames = max(gesto_agachar_frames, 12)
                            else:
                                jogador.iniciar_descida_rapida(gerenciador_sons, dados["vol_sfx"])
                        elif abs(dx) < limiar(dados) and abs(dy) < limiar(dados):
                            # O modo GESTOS só reage a deslizamentos; o clássico mantém toque.
                            if (not touch_jump_started and
                                    normalizar_modo(dados.get('controle_modo')) == MODO_CLASSICO):
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
                touch_jetpack_anchor = None
                touch_hold_frames = 0
                touch_jump_started = False
                touch_gesture_moved = False
                jetpack_gesto_usado = False

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    vx, vy = screen_to_virtual(evento.pos[0], evento.pos[1])
                    mouse_drag_active = True
                    mouse_start_pos = (vx, vy)
                    mouse_current_pos = (vx, vy)
                    mouse_drag_anchor_pos = (vx, vy)
                    mouse_hold_frames = 0
                    mouse_jump_started = False
                    mouse_gesture_moved = False
                    mouse_jetpack_gesto_usado = False
                    # SDL pode sintetizar eventos de mouse para o mesmo toque no Android;
                    # quando touch está ativo, apenas o caminho FINGER trata o gesto.
                    mouse_input_ignored = bool(
                        (E_ANDROID and estado == "JOGANDO") or touch_start_pos is not None)
                    mouse_gameplay_press = bool(
                        estado == "JOGANDO" and jogador and not mouse_input_ignored and
                        not btn_pausa.collidepoint((vx, vy)))
                    if estado == "JOGANDO" and jogador and btn_pausa.collidepoint((vx, vy)):
                        mouse_gesture_moved = True
                        mouse_gameplay_press = False
                        if not mouse_input_ignored:
                            processar_clique_ui((vx, vy))
                    elif estado != "JOGANDO":
                        # Menus continuam respondendo ao clique exatamente como antes.
                        mouse_gesture_moved = True
                        mouse_gameplay_press = False
                        if not mouse_input_ignored:
                            processar_clique_ui((vx, vy))

            elif evento.type == pygame.MOUSEMOTION:
                if mouse_drag_active:
                    mx, my = screen_to_virtual(evento.pos[0], evento.pos[1])
                    mouse_current_pos = (mx, my)
                    if (not mouse_input_ignored and estado == "JOGANDO" and jogador and
                            mouse_gameplay_press):
                        if jogador.jetpack_fase == "voando":
                            # Jetpack mantém o controle contínuo: cada movimento ultrapassando
                            # o limiar muda uma faixa e reposiciona a âncora sem soltar o mouse.
                            if hasattr(evento, "buttons") and evento.buttons and evento.buttons[0]:
                                if mouse_drag_anchor_pos is not None:
                                    dy_mouse = my - mouse_drag_anchor_pos[1]
                                    passos_mouse_jet = passos_jetpack(dy_mouse)
                                    if passos_mouse_jet:
                                        for _ in range(abs(passos_mouse_jet)):
                                            jogador.mover_jetpack(-1 if passos_mouse_jet < 0 else 1)
                                        mouse_drag_anchor_pos = (mx, ancorar_jetpack(
                                            mouse_drag_anchor_pos[1], my, passos_mouse_jet))
                                        mouse_jetpack_gesto_usado = True
                        elif (abs(mx - mouse_start_pos[0]) > 30 or
                              abs(my - mouse_start_pos[1]) > 30):
                            mouse_gesture_moved = True

            elif evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1:
                    if (mouse_drag_active and mouse_gameplay_press and not mouse_input_ignored and
                            estado == "JOGANDO" and jogador and mouse_start_pos):
                        end_x, end_y = screen_to_virtual(evento.pos[0], evento.pos[1])
                        mouse_current_pos = (end_x, end_y)
                        dx_mouse = end_x - mouse_start_pos[0]
                        dy_mouse = end_y - mouse_start_pos[1]
                        if jogador.jetpack_fase is None and not btn_pausa.collidepoint(mouse_start_pos):
                            if dy_mouse < -40:
                                if not mouse_jump_started:
                                    jogador.pular(gerenciador_sons, dados["vol_sfx"])
                            elif dy_mouse > 40:
                                # Arrastar para baixo interrompe o pulo longo; no ar desce
                                # rapidamente e no chão mantém um agachamento curto.
                                if jogador.no_chao:
                                    gesto_agachar_frames = max(gesto_agachar_frames, 12)
                                else:
                                    jogador.iniciar_descida_rapida(gerenciador_sons, dados["vol_sfx"])
                            elif abs(dx_mouse) < 30 and abs(dy_mouse) < 30:
                                # Clique curto pula; segurar já pode ter iniciado o pulo longo.
                                if not mouse_jump_started:
                                    jogador.pular(gerenciador_sons, dados["vol_sfx"])
                    mouse_drag_active = False
                    mouse_drag_anchor_pos = None
                    mouse_jetpack_gesto_usado = False
                    mouse_start_pos = None
                    mouse_current_pos = None
                    mouse_hold_frames = 0
                    mouse_jump_started = False
                    mouse_gesture_moved = False
                    mouse_gameplay_press = False
                    mouse_input_ignored = False

            elif evento.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
                if dados.get('gamepad_ativo', True):
                    pressed = evento.type == pygame.JOYBUTTONDOWN
                    if evento.button in (0, 2):
                        gamepad_pulo = pressed
                        if pressed and estado == 'JOGANDO' and jogador:
                            jogador.pular(gerenciador_sons, dados['vol_sfx'])
                    elif evento.button in (1, 3):
                        gamepad_baixo = pressed
                        if pressed and estado == 'JOGANDO' and jogador and not jogador.no_chao:
                            jogador.iniciar_descida_rapida(gerenciador_sons, dados['vol_sfx'])
                    elif evento.button in (7, 9) and pressed:
                        if estado == 'JOGANDO':
                            estado = 'PAUSA'
                        elif estado == 'PAUSA':
                            estado = 'JOGANDO'

            elif evento.type == pygame.KEYDOWN:
                if estado == 'GAMEOVER' and replay_morte.ativo:
                    replay_morte.pular()
                    continue
                if PIXELRUSH_DEV_BUILD and not E_ANDROID and evento.key == pygame.K_F8:
                    mostrar_hitboxes = not mostrar_hitboxes
                    cache_telas_estaticas.clear()
                if PIXELRUSH_DEV_BUILD and evento.key == pygame.K_F12:
                    if estado == "DEV_MENU":
                        estado = dev_menu_anterior
                    else:
                        dev_menu_anterior = estado
                        estado = "DEV_MENU"
                    touch_start_pos = None
                    touch_current_pos = None
                    toque_ativo = False
                    mouse_drag_active = False
                    mouse_gameplay_press = False
                if evento.key in (pygame.K_p, pygame.K_ESCAPE, getattr(pygame, "K_AC_BACK", pygame.K_ESCAPE)):
                    if PIXELRUSH_DEV_BUILD and estado == "DEV_MENU":
                        estado = dev_menu_anterior
                    elif estado == "LOJA" and item_preview_tipo:
                        item_preview_tipo = None
                        item_preview_id = None
                        item_preview_confirmar = False
                        item_preview_surface = None
                        item_preview_estilo = 1
                    elif estado == "RECORDES" and bioma_recorde_popup is not None:
                        bioma_recorde_popup = None
                    elif estado == "CONFIG_ACESSIBILIDADE":
                        estado = "CONFIG"
                    elif estado == "CANTINHO_PETS":
                        estado = "LOJA"
                        aba_loja = "PETS"
                    elif estado == "JOGANDO":
                        estado = "PAUSA"
                    elif estado == "PAUSA":
                        estado = "JOGANDO"
                    elif estado in ["LOJA", "UPGRADES", "CONFIG", "CONFIG_CONTROLES", "CONFIG_ACESSIBILIDADE", "RANKING", "RELIQUIAS", "BASE_CORREDOR", "CANTINHO_PETS"]:
                        estado = "INICIO"

                if jogador and estado == "JOGANDO":
                    if jogador.jetpack_fase == "voando":
                        if evento.key == pygame.K_UP:
                            jogador.mover_jetpack(-1)
                        elif evento.key == pygame.K_DOWN:
                            jogador.mover_jetpack(1)
                    elif evento.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        jogador.pular(gerenciador_sons, dados["vol_sfx"])

            if (evento.type == EVENTO_GERAR and estado == "JOGANDO" and spawn_bloqueado_frames <= 0 and
                    portal_tipo_ativo is None and not desafio_laser_ativo and not (jogador and jogador.jetpack_fase is not None)):
                if espacamento_ameacas.pode_gerar(metros_atuais, obstaculos, perigos_especiais, buracos,
                                                  LARGURA_VIRTUAL):
                    antes = len(obstaculos) + len(perigos_especiais) + len(buracos)
                    gerou_sequencia = gerar_padrao(todos_sprites, obstaculos, perigos_especiais, moedas, powerups, metros_atuais,
                                 pool_manager, cenario_atual, buracos=buracos, baus=baus_secretos, portais=portais_bonus, dados_jogo=dados,
                                 diretor=diretor_sequencias)
                    depois = len(obstaculos) + len(perigos_especiais) + len(buracos)
                    if depois > antes or gerou_sequencia:
                        espacamento_ameacas.registrar(metros_atuais)

        # Guarda o estado atual dos controles para os proximos ticks fixos.
        teclas_atuais = pygame.key.get_pressed()
        botoes_mouse_atuais = pygame.mouse.get_pressed()
        teclas_atuais, botoes_mouse_atuais = _rep_entradas(teclas_atuais, botoes_mouse_atuais)
        input_pulo_ativo = bool(teclas_atuais[pygame.K_SPACE] or teclas_atuais[pygame.K_UP] or
                                teclas_atuais[pygame.K_w] or gamepad_pulo)
        input_baixo_ativo = bool(teclas_atuais[pygame.K_DOWN] or teclas_atuais[pygame.K_s] or gamepad_baixo)
        input_mouse_ativo = bool(botoes_mouse_atuais[0])
        segurando_baixo_touch = False
        if toque_ativo and touch_start_pos and touch_current_pos:
            dy = touch_current_pos[1] - touch_start_pos[1]
            if (dy > limiar(dados) and not (
                    normalizar_modo(dados.get('controle_modo')) == MODO_GESTOS and
                    touch_jump_started)):
                segurando_baixo_touch = True

        _pro_marcar("renderizacao_e_ui")
        # A renderizacao acontece uma vez por frame visivel, independentemente dos ticks executados.

        # Pausa e Game Over congelam o mundo. Depois do fim da transição de céu,
        # reutilizamos a imagem pronta em vez de redesenhar o fundo, sprites e UI.
        chave_tela_estatica = (estado, cor_ceu_tupla)
        if (estado == "JOGANDO" and tutorial_corrida and tutorial_corrida.ativo
                and getattr(tutorial_corrida, "_pausa_comando", False)
                and cache_tutorial_congelado is not None):
            display_surface.blit(cache_tutorial_congelado, (0, 0))
        elif estado in ("PAUSA", "GAMEOVER") and chave_tela_estatica in cache_telas_estaticas:
            display_surface.blit(cache_telas_estaticas[chave_tela_estatica], (0, 0))
        else:
            # --- RENDERIZAÇÃO NA TELA VIRTUAL ---
            # Todas as telas chamam bg_parallax.draw(), que já preenche o céu;
            # evitamos um segundo fill da superfície completa em todos os frames.
            if estado in ["JOGANDO", "PAUSA", "GAMEOVER"]:
                # v3.277.26: cache apenas do FUNDO quando Android esta sobrecarregado.
                # Personagem, objetos, HUD e eventos sao desenhados em todo quadro.
                _cache_fundo_mobile_ativo = (
                    E_ANDROID and estado == 'JOGANDO' and portal_tipo_ativo is None
                )
                bg_parallax.world.lightweight = modo_grafico_leve(dados)
                _chave_fundo_mobile = (
                    cenario_atual, bg_parallax.cenario, clima.tipo,
                    bool(e_noite), bool(tutorial_corrida and tutorial_corrida.ativo),
                    bool(bg_parallax.world.lightweight), display_surface.get_size()
                )
                _pro_sub_inicio("qa_fundo_cache_chao")
                if cache_fundo_mobile.reusar(
                        display_surface, _chave_fundo_mobile, _cache_fundo_mobile_ativo):
                    pass
                else:
                    cor_ceu_render = clima.aplicar_ceu(cor_ceu_tupla) if estado in ("JOGANDO", "PAUSA", "GAMEOVER") else cor_ceu_tupla
                    bg_parallax.world.lightweight = modo_grafico_leve(dados)
                    _pro_sub_inicio("mundo_2_5d")
                    bg_parallax.draw(display_surface, cor_ceu_render, e_noite)
                    _pro_sub_fim()
                    _pro_sub_inicio("profundidade_fundo")
                    profundidade_cinematografica(display_surface, cenario_atual, peso_noite,
                                                  modo_grafico_leve(dados))
                    # Fase B: plano atmosférico leve atrás do chão, riscos e HUD.
                    desenhar_profundidade_bioma(display_surface, cenario_atual,
                                                 bg_parallax.world.travel, peso_noite,
                                                 modo_grafico_leve(dados) or dados.get("acess_reduzir_efeitos", False),
                                                 clima.tipo)
                    _pro_sub_fim()
                    # Nuvens de clima sao fundo do mundo, nunca cobrem o HUD/jogador.
                    if clima.tipo != "limpo" and estado in ("JOGANDO", "PAUSA", "GAMEOVER"):
                        clima._desenhar_nuvens_clima(display_surface, cor_ceu_render)
                    if estado in ('JOGANDO', 'PAUSA') and portal_tipo_ativo is None:
                        cenas_epicas.desenhar(display_surface, cenario_atual,
                                             bg_parallax.world.travel, frame_count, peso_noite,
                                             leve=(modo_grafico_leve(dados) or dados.get('acess_reduzir_efeitos', False)))
                    cache_fundo_mobile.guardar(
                        display_surface, _chave_fundo_mobile, _cache_fundo_mobile_ativo)
                # O piso rola em todos os quadros, mesmo com fundo em cache.
                # Sao exatamente os mesmos pixels e a mesma ordem de sobreposicao.
                bg_parallax.draw_chao(display_surface)
                _pro_sub_fim()  # qa_fundo_cache_chao
                _pro_sub_inicio("qa_render_antes_sprites")
                if estado == 'JOGANDO' and not modo_grafico_leve(dados):
                    desenhar_clima_premium(display_surface, cenario_atual, frame_count)
                if estado in ("JOGANDO", "PAUSA") and evento_corrida:
                    ex = int(evento_corrida_x)
                    if evento_corrida == "PLATAFORMA":
                        py = 560 + int(math.sin(frame_count * 0.08) * 30)
                        pygame.draw.rect(display_surface, (70, 155, 205), (ex - 32, py, 64, 14), border_radius=3)
                        pygame.draw.rect(display_surface, (160, 235, 255), (ex - 26, py + 3, 52, 3))
                        pygame.draw.rect(display_surface, (35, 75, 105), (ex - 20, py + 14, 8, 25))
                        pygame.draw.rect(display_surface, (35, 75, 105), (ex + 12, py + 14, 8, 25))
                    elif evento_corrida == "INFILTRACAO":
                        sensor_on = (frame_count // 18) % 2 == 0
                        zoom = 1.0 + (0.24 * (0.5 + 0.5 * math.sin(frame_count * 0.38))) if alerta_detector_timer > 0 else 1.0
                        raio_sensor = int(8 * zoom)
                        pygame.draw.rect(display_surface, (55, 60, 80), (ex - 7, 300, 14, 210))
                        pygame.draw.circle(display_surface, (255, 65, 80) if sensor_on else (80, 230, 160), (ex, 315), raio_sensor)
                        pygame.draw.circle(display_surface, (255, 235, 235), (ex, 315), raio_sensor + 5, 2)
                        if sensor_on:
                            pygame.draw.polygon(display_surface, (120, 35, 55), [(ex, 325), (ex - 48, 610), (ex + 48, 610)])
                        if alerta_detector_timer > 0:
                            # Efeito de lente focaliza brevemente o sensor sem pausar a simulação.
                            pygame.draw.circle(display_surface, (255, 75, 85), (ex, 315), 46 + int(4 * math.sin(frame_count * .5)), 2)
                            pygame.draw.rect(display_surface, (12, 8, 22), (18, 86, LARGURA_VIRTUAL - 36, 74), border_radius=12)
                            pygame.draw.rect(display_surface, (255, 65, 85), (18, 86, LARGURA_VIRTUAL - 36, 74), 3, border_radius=12)
                            desenhar_texto_centralizado(display_surface, "AGACHE-SE! SENSOR À FRENTE", fonte_missoes, (255, 105, 115), PRETO, 106)
                            desenhar_texto_centralizado(display_surface, "SEGURE / DESLIZE PARA BAIXO", fonte_pequena, BRANCO, PRETO, 137)
                    elif evento_corrida == "INTERRUPTOR":
                        pygame.draw.rect(display_surface, (45, 75, 85), (ex - 13, ALTURA_VIRTUAL - 120, 26, 42), border_radius=4)
                        pygame.draw.rect(display_surface, (70, 255, 180) if interruptor_ativado else (255, 195, 65), (ex - 8, ALTURA_VIRTUAL - 112, 16, 14), border_radius=3)
                        pygame.draw.rect(display_surface, (255, 90, 90), (min(LARGURA_VIRTUAL - 8, ex + 45), ALTURA_VIRTUAL - 190, 8, 110))
                if (estado in ("JOGANDO", "PAUSA") and portal_tipo_ativo is None and
                        cenario_atual not in ("cidade", "neve", "deserto", "vulcao", "floresta", "cidade_futurista", "ilhas_celestes") and
                        not bg_parallax.tem_arte_externa()):
                    if cenario_atual == "vulcao":
                        pygame.draw.polygon(display_surface, (72, 35, 42), [(0, 380), (65, 245), (125, 330), (205, 185), (286, 325), (370, 235), (450, 350), (450, 465), (0, 465)])
                        pygame.draw.polygon(display_surface, (255, 86, 35), [(169, 248), (187, 218), (202, 231), (220, 211), (236, 255), (205, 273), (180, 267)])
                        pygame.draw.rect(display_surface, (255, 150, 45), (193, 265, 7, 12))
                    elif cenario_atual == "cidade_futurista":
                        for nx, nh in ((12, 128), (76, 174), (145, 105), (232, 156), (319, 128), (390, 185)):
                            pygame.draw.rect(display_surface, (20, 31, 70), (nx, 300 - nh // 2, 35, nh))
                            pygame.draw.rect(display_surface, (65, 240, 255), (nx + 6, 307 - nh // 2, 5, max(8, nh - 22)), 1)
                            for wy in range(315 - nh // 2, 295, 19):
                                pygame.draw.rect(display_surface, (70, 245, 255), (nx + 8, wy, 5, 7))
                                pygame.draw.rect(display_surface, (205, 95, 255), (nx + 21, wy + 5, 5, 5))
                    elif cenario_atual == "floresta":
                        for tx, th in ((5, 136), (76, 166), (157, 120), (248, 157), (345, 139), (412, 173)):
                            pygame.draw.rect(display_surface, (58, 53, 37), (tx + 10, 300 - th // 2, 9, th))
                            pygame.draw.polygon(display_surface, (24, 82, 50), [(tx - 15, 300 - th // 2 + 40), (tx + 14, 300 - th // 2 - 28), (tx + 42, 300 - th // 2 + 40)])
                            pygame.draw.polygon(display_surface, (38, 115, 61), [(tx - 12, 300 - th // 2 + 65), (tx + 14, 300 - th // 2 - 5), (tx + 39, 300 - th // 2 + 65)])

                em_cena_jetpack = bool(jogador and jogador.jetpack_fase is not None and estado in ("JOGANDO", "PAUSA"))
                if em_cena_jetpack:
                    desenhar_cenario_jetpack(jetpack_bg_surface, cor_ceu_render, bg_parallax.fase_ciclo,
                                              bg_parallax.peso_noite, frame_count, bg_parallax.estrelas)
                    if jogador.jetpack_fase == "subindo":
                        progresso_fundo = 1.0 - jogador.jetpack_transicao_timer / float(max(1, jogador.jetpack_subida_duracao))
                        alpha_fundo = int(255 * max(0.0, min(1.0, progresso_fundo)) ** 1.15)
                    elif jogador.jetpack_fase == "descendo":
                        progresso_fundo = jogador.jetpack_transicao_timer / float(max(1, jogador.jetpack_descida_duracao))
                        alpha_fundo = int(255 * max(0.0, min(1.0, progresso_fundo)) ** 1.15)
                    else:
                        alpha_fundo = 255
                    jetpack_bg_surface.set_alpha(max(0, min(255, alpha_fundo)))
                    display_surface.blit(jetpack_bg_surface, (0, 0))
                    jetpack_bg_surface.set_alpha(None)
                else:
                    buracos.draw(display_surface)
                    # Placa de perigo ao lado de cada buraco: desenho procedural leve.
                    for buraco_aviso in buracos:
                        bx = buraco_aviso.rect.centerx
                        by = ALTURA_VIRTUAL - 105
                        placa_x = bx + buraco_aviso.rect.width // 2 + 7
                        if placa_x > LARGURA_VIRTUAL - 22:
                            placa_x = bx - buraco_aviso.rect.width // 2 - 7
                        pygame.draw.line(display_surface, (65, 48, 37),
                                         (placa_x, by + 22), (placa_x, ALTURA_VIRTUAL - 76), 3)
                        pygame.draw.polygon(display_surface, (255, 190, 35),
                                            [(placa_x, by), (placa_x - 14, by + 23),
                                             (placa_x + 14, by + 23)])
                        pygame.draw.polygon(display_surface, (45, 35, 28),
                                            [(placa_x, by + 4), (placa_x - 10, by + 21),
                                             (placa_x + 10, by + 21)], 2)
                        pygame.draw.line(display_surface, (45, 35, 28),
                                         (placa_x, by + 9), (placa_x, by + 16), 3)
                        pygame.draw.circle(display_surface, (45, 35, 28),
                                           (placa_x, by + 19), 1)

                # No modo de teste, cancela qualquer morte acionada por colisão ou queda.
                if modo_desenvolvedor and dev_imortalidade and jogador is not None and jogador.morrendo:
                    jogador.morrendo = False
                    jogador.tempo_morte = 0
                    jogador.morte_por_buraco = False
                    jogador.velocidade_y = 0
                    jogador.rect.bottom = ALTURA_VIRTUAL - 75

                # Fundos dedicados das novas fases, desenhados antes dos sprites
                # para manter personagem, bolhas e lasers sempre visíveis.
                if estado == "JOGANDO" and portal_tipo_ativo is not None:
                    # Cada portal recebe um cenário próprio, desenhado proceduralmente e sem assets pesados.
                    if portal_tipo_ativo == "INVERTIDO":
                        display_surface.fill((10, 4, 28))
                        for i in range(12):
                            yy = (i * 78 + frame_count * 3) % ALTURA_VIRTUAL
                            pygame.draw.line(display_surface, (85, 45, 145), (0, yy), (LARGURA_VIRTUAL, yy - 55), 2)
                    elif portal_tipo_ativo == "FLAPPY":
                        display_surface.fill((95, 190, 245))
                        for i in range(6):
                            xx = (i * 95 - frame_count * 2) % (LARGURA_VIRTUAL + 90)
                            pygame.draw.ellipse(display_surface, (225, 250, 255), (xx, 90 + (i % 3) * 75, 64, 24))
                        pygame.draw.rect(display_surface, (60, 175, 90), (0, ALTURA_VIRTUAL - 90, LARGURA_VIRTUAL, 90))
                    elif portal_tipo_ativo == "TUNEL":
                        display_surface.fill((5, 12, 30))
                        pygame.draw.rect(display_surface, (20, 45, 65), (0, ALTURA_VIRTUAL - 82, LARGURA_VIRTUAL, 82))
                        pygame.draw.line(display_surface, (40, 190, 240), (0, ALTURA_VIRTUAL - 82), (LARGURA_VIRTUAL, ALTURA_VIRTUAL - 82), 3)
                        for i in range(1, 9):
                            inset = (i * 25 + frame_count * 2) % 180
                            pygame.draw.rect(display_surface, (40, 155, 220), (inset, inset + 70, LARGURA_VIRTUAL - inset * 2, ALTURA_VIRTUAL - inset * 2 - 70), 2)
                    elif portal_tipo_ativo == "TESOURO":
                        display_surface.fill((34, 17, 8))
                        pygame.draw.rect(display_surface, (88, 48, 24), (0, ALTURA_VIRTUAL - 92, LARGURA_VIRTUAL, 92))
                        pygame.draw.line(display_surface, (255, 190, 65), (0, ALTURA_VIRTUAL - 92), (LARGURA_VIRTUAL, ALTURA_VIRTUAL - 92), 4)
                        for i in range(12):
                            xx = (i * 43 - frame_count * 4) % LARGURA_VIRTUAL
                            yy = ALTURA_VIRTUAL - 130 - (i * 47) % 390
                            pygame.draw.circle(display_surface, (255, 195, 55), (xx, yy), 9)
                            pygame.draw.circle(display_surface, (255, 245, 170), (xx - 2, yy - 2), 3)
                    elif portal_tipo_ativo == "REFLEXOS":
                        display_surface.fill((18, 8, 42))
                        for i in range(9):
                            yy = (i * 90 + frame_count * 2) % ALTURA_VIRTUAL
                            pygame.draw.line(display_surface, (195, 75, 255), (0, yy), (LARGURA_VIRTUAL, ALTURA_VIRTUAL - yy), 2)
                if estado == "JOGANDO" and portal_tipo_ativo == "AQUATICO":
                    display_surface.fill((5, 35, 88))
                    for faixa_agua in range(9):
                        xx = faixa_agua * 58 + int(math.sin(frame_count * 0.025 + faixa_agua) * 12)
                        pygame.draw.line(display_surface, (12, 82, 145), (xx, 0), (xx - 35, ALTURA_VIRTUAL), 3)
                    pygame.draw.rect(display_surface, (35, 155, 210), (0, 72, LARGURA_VIRTUAL, 4))
                elif estado == "JOGANDO" and portal_tipo_ativo == "LASERS":
                    display_surface.fill((18, 8, 32))
                    pygame.draw.rect(display_surface, (30, 24, 48), (0, ALTURA_VIRTUAL - 78, LARGURA_VIRTUAL, 78))
                    pygame.draw.line(display_surface, (110, 65, 180), (0, ALTURA_VIRTUAL - 78), (LARGURA_VIRTUAL, ALTURA_VIRTUAL - 78), 3)
                    for gx in range(0, LARGURA_VIRTUAL, 45):
                        pygame.draw.line(display_surface, (43, 20, 65), (gx, 0), (gx, ALTURA_VIRTUAL), 1)
                    for gy in range(0, ALTURA_VIRTUAL, 45):
                        pygame.draw.line(display_surface, (43, 20, 65), (0, gy), (LARGURA_VIRTUAL, gy), 1)

                if estado in ("JOGANDO", "PAUSA") and bioma_lendario_ativo in BIOMAS_LENDARIOS:
                    cor_lendaria = BIOMAS_LENDARIOS[bioma_lendario_ativo]["cor"]
                    # Overlay discreto e barato, sem superfícies novas por frame.
                    pygame.draw.rect(display_surface, cor_lendaria, (0, 0, LARGURA_VIRTUAL, ALTURA_VIRTUAL), 2)
                    for estrela_i in range(8):
                        estrela_x = (estrela_i * 67 + frame_count * (1 + estrela_i % 2)) % LARGURA_VIRTUAL
                        estrela_y = (estrela_i * 97 + frame_count // 3) % ALTURA_VIRTUAL
                        pygame.draw.circle(display_surface, cor_lendaria, (estrela_x, estrela_y), 2)
                if jogador is not None and estado in ("JOGANDO", "PAUSA", "GAMEOVER"):
                    jogador._v3188_modo_leve = modo_grafico_leve(dados)
                    jogador.renderizar_visual(frame_count)
                    if estado == 'JOGANDO':
                        MovimentoExpressivo.aplicar_pose(jogador, frame_count)
                    # v3.183: tonalidade contextual somente na imagem exibida.
                    # Menus, atlas, jogo fisico, HUD e power-ups inalterados.
                    if portal_tipo_ativo is None:
                        _v3183_integrar_skin(jogador, cenario_atual, peso_noite,
                                            clima.tipo, modo_grafico_leve(dados))
                for sprite_visual in obstaculos:
                    if isinstance(sprite_visual, ObstaculoVoador):
                        sprite_visual.renderizar_visual()

                # Pequeno balanço vertical apenas visual durante a corrida no chão.
                # O rect é restaurado imediatamente: colisões e física permanecem intactas.
                jogador_y_fisico = None
                if (jogador is not None and estado == "JOGANDO" and not jogador.morrendo
                        and jogador.no_chao and jogador.jetpack_fase is None and not jogador.agachado):
                    jogador_y_fisico = jogador.rect.y
                    jogador.rect.y += int(round(math.sin(jogador.anim_pernas * 2.0) * 1.8))
                # Ecos visuais dos clones: até três silhuetas leves, sem sprites persistentes.
                # A quantidade real pode ser maior; a contagem completa aparece no HUD.
                if jogador is not None and jogador.clones_ativos > 0 and estado in ("JOGANDO", "PAUSA") and not jogador.morrendo:
                    # Reutiliza o sprite já renderizado, sem criar superfícies novas a cada frame.
                    offsets_clones = ((-18, -12), (-30, 10), (-12, 28))
                    # Clones são cópias visuais opacas; o escudo pertence somente ao jogador.
                    alpha_original = jogador.image.get_alpha()
                    jogador.image.set_alpha(255)
                    for off_x, off_y in offsets_clones[:min(3, jogador.clones_ativos)]:
                        display_surface.blit(jogador.image, jogador.rect.move(off_x, off_y))
                    jogador.image.set_alpha(alpha_original)
                if (False and jogador is not None and estado == "JOGANDO" and not jogador.morrendo
                        and dados.get('rastro_visual', 'DESLIGADO') != 'DESLIGADO'):
                    desenhar_rastro_cosmetico(display_surface, jogador.rect.left,
                                             jogador.rect.centery, dados.get('rastro_visual', 'ESTRELAS'),
                                             frame_count, modo_grafico_leve(dados))
                if estado == 'JOGANDO' and portal_tipo_ativo is None:
                    desenhar_silhuetas_perigos(display_surface, obstaculos, frame_count, cenario_atual)
                if estado == 'JOGANDO' and portal_tipo_ativo is None:
                    sombra_contato(display_surface, jogador, cenario_atual, modo_grafico_leve(dados), peso_noite)
                if estado == "JOGANDO" and jogador is not None:
                    diretor_eventos_raros.desenhar(
                        display_surface, modo_grafico_leve(dados))
                    diretor_perseguidores.desenhar(
                        display_surface, jogador.rect.left, modo_grafico_leve(dados))
                _pro_sub_fim()  # qa_render_antes_sprites
                _pro_sub_inicio("sprites_render")
                _prod_dx_entrada = 0
                if (estado == 'JOGANDO' and jogador is not None and frame_count < entrada_corrida_ate
                        and not (tutorial_corrida and tutorial_corrida.ativo)):
                    # Tutorial: sprite e hitbox devem iniciar na MESMA coordenada.
                    # A entrada cosmetica continua intacta nas corridas sem tutorial.
                    _prod_t = max(0.0, min(1.0, (entrada_corrida_ate - frame_count) / 70.0))
                    _prod_dx_entrada = int(250 * (_prod_t ** 2))
                    jogador.rect.x -= _prod_dx_entrada
                todos_sprites.draw(display_surface)
                if _prod_dx_entrada:
                    jogador.rect.x += _prod_dx_entrada
                _pro_sub_fim()
                _pro_sub_inicio("qa_render_apos_sprites")
                _r11_sub_inicio("r11_post_alertas")
                if estado == 'JOGANDO' and frame_count < entrada_corrida_ate:
                    _prod_banner_entrada(display_surface, frame_count, entrada_corrida_ate)
                if estado == "JOGANDO" and tutorial_corrida and tutorial_corrida.ativo:
                    tutorial_corrida.desenhar(display_surface)
                if estado == "JOGANDO" and jogador is not None and portal_tipo_ativo is None:
                    desenhar_alerta_moveis(display_surface, obstaculos, jogador, frame_count,
                                          modo_grafico_leve(dados) or dados.get("acess_reduzir_efeitos", False))
                if estado == 'JOGANDO' and jogador is not None and not em_cena_jetpack:
                    MovimentoExpressivo.desenhar(display_surface, jogador, frame_count, cor_jogador)
                    if frame_count < efeito_esquiva_ate:
                        intensidade = (efeito_esquiva_ate - frame_count) / 70.
                        largura = int(34 + 18 * (1 - intensidade))
                        pygame.draw.arc(display_surface, (255, 225, 126),
                                        (jogador.rect.centerx - largura, jogador.rect.y - 16,
                                         largura * 2, jogador.rect.h + 30),
                                        -.55, .55, 2)
                if estado == 'JOGANDO':
                    brilho_coletaveis(display_surface, moedas, powerups, frame_count,
                                       modo_grafico_leve(dados))
                if (estado == 'JOGANDO' and portal_tipo_ativo is None and
                        jogador is not None and jogador.jetpack_fase is None and
                        febre_turbo_distancia_restante <= 0):
                    desenhar_avisos_obstaculos(display_surface, jogador, obstaculos,
                                               frame_count, modo_grafico_leve(dados))
                if estado == 'JOGANDO' and portal_tipo_ativo is None:
                    if dados.get('acess_contraste', False) or dados.get('acess_sinais', False):
                        desenhar_sinais_acessiveis(display_surface, jogador, obstaculos,
                                                  buracos, dados, modo_grafico_leve(dados))
                _r11_sub_fim()
                _r11_sub_inicio("r11_post_pets")
                # Pets Premium 2.0: estado ligado à corrida, sprite cacheado e seguimento suave.
                if jogador is not None and estado in ("JOGANDO", "PAUSA"):
                    pet_id_seguindo = dados.get("pet_equipado", "")
                    if pet_id_seguindo in PETS_CONFIG:
                        px, py = (pet_pos_visual if pet_pos_visual is not None else
                                  (max(27, jogador.rect.left-24), jogador.rect.centery-5))
                        voador = pet_eh_voador(pet_id_seguindo)
                        # Mantém asas, caudas e patas dentro da área visível.
                        pet_x = max(36 if voador else 30, int(px))
                        pet_y = int(py)
                        if jogador.morrendo:
                            if pet_inicio_morte_frame is None:
                                pet_inicio_morte_frame = frame_count
                            acao_base, expressao, efeito = ('MORRER','','')
                            desde_pet = pet_inicio_morte_frame
                        else:
                            pet_inicio_morte_frame = None
                            acao_base, expressao, efeito = pet5_escolher_canais(
                                jogador,pet_estado_animado,estado == 'JOGANDO'
                            )
                            desde_pet = pet_estado_animado_desde
                        tamanho_pet=(68,58) if voador else (58,52)
                        if not modo_grafico_leve(dados) and not jogador.morrendo:
                            desenhar_fx_pet(display_surface, pet_id_seguindo, (pet_x, pet_y), frame_count, 0.85, modo_grafico_leve(dados))
                        if efeito and not modo_grafico_leve(dados):
                            pet5_desenhar_efeito_leve(display_surface, efeito, pet_x, pet_y,
                                frame_count, PETS_CONFIG[pet_id_seguindo]['cor'])
                        # Ciclo proprio do pet sincronizado com a velocidade da corrida.
                        # Não altera a física do jogador nem a posição dos obstáculos.
                        razao_anim=1.0
                        if estado == 'JOGANDO' and not jogador.morrendo:
                            razao_anim=max(0.8,min(1.25,vel_jogo/max(6.0,vel_base)))
                        sprite_pet=pet8_desenhar(
                            display_surface,pet_id_seguindo,acao_base,frame_count,
                            pet_anim_memoria,tamanho_pet,(pet_x,pet_y),razao_anim)
                        pet9_desenhar_expressao(
                            display_surface,pet_id_seguindo,frame_count,(pet_x,pet_y),
                            tamanho_pet,acao_base,expressao,modo_grafico_leve(dados))
                        desenhar_evolucao_pet(display_surface, pet_id_seguindo, pet_x,pet_y,
                                              dados, frame_count, leve=modo_grafico_leve(dados))
                        if estado == "JOGANDO" and not jogador.morrendo:
                            desenhar_recarga_pet(display_surface, pet_id_seguindo,
                                                  (pet_x+25,pet_y-26), frame_count,
                                                  pet_salvou_vida_rodada, modo_grafico_leve(dados))
                _r11_sub_fim()
                _r11_sub_inicio("r11_post_efeitos_portais")
                # Contador do grupo de clones; é apenas visual e não afeta colisões.
                if jogador is not None and jogador.clones_ativos > 0 and estado in ("JOGANDO", "PAUSA"):
                    texto_clones = render_texto_cacheado(
                        fonte_pequena, f"{t('clones_restantes', dados)}: {jogador.clones_ativos}", (120, 235, 255))
                    display_surface.blit(texto_clones, (jogador.rect.x, max(8, jogador.rect.y - 26)))
                # Evolução visual puramente cosmética: aura pixelada fora da hitbox do jogador.
                nivel_skin_visual = nivel_visual_skin(dados)
                if jogador is not None and nivel_skin_visual >= 2 and not jogador.morrendo:
                    cor_skin_visual = SKINS.get(dados.get("skin_equipada", "AZUL"), SKINS["AZUL"])["cor"]
                    cx_skin, cy_skin = jogador.rect.center
                    raio_skin = 34 + nivel_skin_visual * 3 + (frame_count % 4)
                    # Estágio 2/4 recebe uma moldura de aura; os estágios seguintes
                    # acrescentam os traços horizontais e as partículas já existentes.
                    pygame.draw.rect(display_surface, cor_skin_visual,
                                     (cx_skin - raio_skin, cy_skin - raio_skin,
                                      raio_skin * 2, raio_skin * 2), 1)
                    if nivel_skin_visual >= 3:
                        pygame.draw.rect(display_surface, cor_skin_visual, (cx_skin - raio_skin, cy_skin - raio_skin, raio_skin * 2, 3), 1)
                        pygame.draw.rect(display_surface, cor_skin_visual, (cx_skin - raio_skin, cy_skin + raio_skin - 3, raio_skin * 2, 3), 1)
                    if nivel_skin_visual >= 4 and frame_count % 8 < 4:
                        for off in (-1, 1):
                            px_skin = cx_skin + off * (raio_skin - 5)
                            py_skin = cy_skin + ((frame_count * 3) % 31) - 15
                            pygame.draw.rect(display_surface, (255, 245, 160), (px_skin, py_skin, 4, 4))
                if portal_tipo_ativo == "FLAPPY":
                    for pipe in portal_pipes:
                        gap = 178
                        y_gap = int(pipe["gap_y"])
                        rect_cima = pygame.Rect(int(pipe["x"]), 0, 58, max(0, y_gap - gap // 2))
                        rect_baixo = pygame.Rect(int(pipe["x"]), y_gap + gap // 2, 58,
                                                ALTURA_VIRTUAL - (y_gap + gap // 2))
                        pygame.draw.rect(display_surface, (40, 180, 90), rect_cima)
                        pygame.draw.rect(display_surface, (130, 255, 150), (rect_cima.x, rect_cima.bottom - 8, 58, 8))
                        pygame.draw.rect(display_surface, (40, 180, 90), rect_baixo)
                        pygame.draw.rect(display_surface, (130, 255, 150), (rect_baixo.x, rect_baixo.y, 58, 8))
                elif portal_tipo_ativo == "AQUATICO":
                    for onda in range(8):
                        yy = 100 + onda * 82 + int(math.sin(frame_count * 0.05 + onda) * 9)
                        pygame.draw.line(display_surface, (20, 120, 190), (0, yy), (LARGURA_VIRTUAL, yy), 2)
                    for bolha in portal_pipes:
                        pygame.draw.circle(display_surface, (70, 220, 255), (int(bolha["x"] + 17), int(bolha["y"] + 17)), 16, 3)
                        pygame.draw.circle(display_surface, (220, 255, 255), (int(bolha["x"] + 11), int(bolha["y"] + 10)), 4)
                elif portal_tipo_ativo in ("LASERS", "REFLEXOS"):
                    # Lasers são sobrepostos à cena sem limpar a superfície inteira.
                    for laser in portal_pipes:
                        cor_laser = (255, 45, 75) if laser.get("ativo") else (255, 180, 65)
                        espessura = 9 if laser.get("ativo") else 2
                        pygame.draw.line(display_surface, cor_laser, (int(laser["x"]), int(laser["y"])),
                                         (min(LARGURA_VIRTUAL, int(laser["x"] + 330)), int(laser["y"])), espessura)
                        if not laser.get("ativo"):
                            pygame.draw.line(display_surface, (255, 230, 160), (max(0, int(laser["x"])), int(laser["y"] - 10)),
                                             (min(LARGURA_VIRTUAL, int(laser["x"] + 330)), int(laser["y"] - 10)), 1)
                if desafio_laser_ativo:
                    for faixa in desafio_laser_faixas:
                        x_fx = int(faixa["x"])
                        gap_y = int(faixa["gap_y"])
                        gap_h = int(faixa["gap_h"])
                        warning = faixa.get("warning", 0)
                        pulso = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(frame_count * 0.28 + x_fx * 0.03))
                        cor = (255, 185, 92) if warning > 0 else (255, 56, 108)
                        brilho = (255, 242, 210) if warning > 0 else (255, 230, 245)
                        rect_cima = pygame.Rect(x_fx, 0, 34, max(0, gap_y - gap_h // 2))
                        rect_baixo = pygame.Rect(x_fx, gap_y + gap_h // 2, 34, ALTURA_VIRTUAL - (gap_y + gap_h // 2))
                        halo = pygame.Rect(x_fx - 5, 0, 44, ALTURA_VIRTUAL)
                        pygame.draw.rect(display_surface, misturar_cores(cor, PRETO, 0.22), halo, 1)
                        pygame.draw.rect(display_surface, cor, rect_cima)
                        pygame.draw.rect(display_surface, cor, rect_baixo)
                        pygame.draw.rect(display_surface, brilho, (rect_cima.x + 8, max(0, rect_cima.bottom - 8), 18, 4))
                        pygame.draw.rect(display_surface, brilho, (rect_baixo.x + 8, rect_baixo.y + 4, 18, 4))
                        pygame.draw.rect(display_surface, misturar_cores(cor, BRANCO, 0.45 + 0.35 * pulso), (x_fx + 14, 0, 6, rect_cima.height))
                        pygame.draw.rect(display_surface, misturar_cores(cor, BRANCO, 0.45 + 0.35 * pulso), (x_fx + 14, rect_baixo.y, 6, rect_baixo.height))
                        pygame.draw.rect(display_surface, (48, 62, 82), (x_fx - 3, max(0, gap_y - gap_h // 2 - 14), 40, 10), border_radius=2)
                        pygame.draw.rect(display_surface, (48, 62, 82), (x_fx - 3, min(ALTURA_VIRTUAL - 10, gap_y + gap_h // 2 + 4), 40, 10), border_radius=2)
                        if warning > 0:
                            pygame.draw.rect(display_surface, (255, 245, 180), (x_fx - 8, gap_y - gap_h // 2 - 7, 50, 3))
                            pygame.draw.rect(display_surface, (255, 245, 180), (x_fx - 8, gap_y + gap_h // 2 + 4, 50, 3))
                            pygame.draw.rect(display_surface, (255, 206, 96), (x_fx + 9, gap_y - 8, 16, 2))
                        else:
                            pygame.draw.line(display_surface, (255, 214, 235), (x_fx + 16, max(0, gap_y - gap_h // 2)), (x_fx + 16, min(ALTURA_VIRTUAL, gap_y + gap_h // 2)), 2)
                    desenhar_texto_centralizado(display_surface, "CORREDOR LASER", fonte, BRANCO, PRETO, 112)
                    desenhar_texto_centralizado(display_surface, "Segure para subir / solte para descer", fonte_pequena, (215, 235, 255), PRETO, 132)
                    pygame.draw.rect(display_surface, (38, 58, 84), (LARGURA_VIRTUAL//2 - 74, 146, 148, 10), border_radius=4)
                    progresso_laser = 0 if not desafio_laser_timer else max(0, min(144, int(144 * (1.0 - (desafio_laser_timer / 420.0)))))
                    pygame.draw.rect(display_surface, (92, 232, 255), (LARGURA_VIRTUAL//2 - 72, 148, progresso_laser, 6), border_radius=3)
                    desenhar_legibilidade_corredor(display_surface, desafio_laser_faixas, frame_count,
                                                     modo_grafico_leve(dados))
                if em_cena_jetpack:
                    jetpack_laser_avancado.desenhar(display_surface, modo_grafico_leve(dados))
                    desenhar_legibilidade_jetpack(display_surface, jetpack_laser_avancado,
                                                   frame_count, modo_grafico_leve(dados))
                _r11_sub_fim()
                _r11_sub_inicio("r11_post_particulas")
                if jogador_y_fisico is not None:
                    jogador.rect.y = jogador_y_fisico
                if modo_grafico_leve(dados):
                    for particula_visivel in particulas.sprites()[:65]:
                        display_surface.blit(particula_visivel.image, particula_visivel.rect)
                else:
                    particulas.draw(display_surface)
                textos_flut.draw(display_surface)
                _r11_sub_fim()
                _r11_sub_inicio("r11_post_frente_gamefeel")
                if portal_tipo_ativo is None and estado == "JOGANDO" and not em_cena_jetpack:
                    bg_parallax.draw_foreground(display_surface)
                    if estado == "JOGANDO" and jogador is not None:
                        _r11_sub_inicio("r11_post_gamefeel")
                        gamefeel.desenhar(display_surface, jogador, combo_contagem, cenario_atual)
                        _r11_sub_fim()
                _r11_sub_fim()
                _r11_sub_inicio("r11_post_clima_transicoes")
                if portal_tipo_ativo is None:
                    if not modo_grafico_leve(dados):
                        _pro_sub_inicio("clima_render")
                        clima.draw(display_surface, bool(dados.get("acess_reduzir_efeitos", False)))
                        _pro_sub_fim()

                if estado == "JOGANDO" and portal_transicao_timer > 0:
                    progresso_portal = 1.0 - (portal_transicao_timer / 72.0)
                    # Cortina de teletransporte de baixo custo: centro escuro, anéis e partículas.
                    centro_portal = (LARGURA_VIRTUAL // 2, ALTURA_VIRTUAL // 2)
                    raio_portal = int(24 + 230 * math.sin(math.pi * max(0.0, min(1.0, progresso_portal))))
                    alpha_portal = int(210 * math.sin(math.pi * max(0.0, min(1.0, progresso_portal))))
                    camada_portal = portal_transition_surface
                    camada_portal.fill((0, 0, 0, 0))
                    pygame.draw.circle(camada_portal, (2, 3, 12, alpha_portal), centro_portal, max(8, raio_portal))
                    pygame.draw.circle(camada_portal, (45, 15, 90, min(255, alpha_portal + 25)), centro_portal,
                                       max(10, raio_portal), max(2, 4))
                    pygame.draw.circle(camada_portal, (90, 220, 255, min(255, alpha_portal + 25)), centro_portal,
                                       max(12, int(raio_portal * 0.72)), 3)
                    pygame.draw.circle(camada_portal, (255, 125, 235, min(255, alpha_portal + 15)), centro_portal,
                                       max(10, int(raio_portal * 0.88)), 2)
                    for indice_particula in range(30):
                        angulo_particula = indice_particula * math.tau / 30 + frame_count * (0.12 if indice_particula % 2 else -0.09)
                        distancia_particula = max(12, raio_portal + int(math.sin(frame_count * 0.2 + indice_particula) * 18))
                        px_particula = centro_portal[0] + int(math.cos(angulo_particula) * distancia_particula)
                        py_particula = centro_portal[1] + int(math.sin(angulo_particula) * distancia_particula)
                        pygame.draw.circle(camada_portal, (130, 210, 255, min(255, alpha_portal + 35)),
                                           (px_particula, py_particula), 2 if indice_particula % 3 else 3)
                    display_surface.blit(camada_portal, (0, 0))
                    texto_portal = "TELETRANSPORTE..." if portal_transicao_tipo == "ENTRANDO" else "RETORNANDO À CORRIDA"
                    rotulo_portal = render_texto_cacheado(fonte_grande, texto_portal, BRANCO)
                    display_surface.blit(rotulo_portal, (LARGURA_VIRTUAL // 2 - rotulo_portal.get_width() // 2,
                                                         ALTURA_VIRTUAL // 2 + 120))
                    portal_transicao_timer -= 1

                if estado == "JOGANDO" and transicao_cenario_timer > 0:
                    progresso_transicao = 1.0 - (transicao_cenario_timer / 105.0)
                    desenhar_faixa_bioma_premium(display_surface, cenario_atual, cenario_transicao_nome,
                                                 progresso_transicao, frame_count, modo_grafico_leve(dados), dados.get('idioma', 'pt_BR'))
                    _prod_fx_transicao(display_surface, cenario_atual, progresso_transicao, frame_count)

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

            if mostrar_hitboxes and estado in ('JOGANDO', 'PAUSA') and not E_ANDROID:
                desenhar_hitboxes_debug(display_surface, jogador, obstaculos,
                                        perigos_especiais, frame_count, buracos)

            _r11_sub_fim()
            _pro_sub_fim()  # qa_render_apos_sprites
            if estado == "JOGANDO":
                _pro_sub_inicio("qa_hud_corrida")
                if jogador and febre_turbo_distancia_restante > 0:
                    # Aura de cometa estilizada: arcos orbitais, chamas e faíscas; fora da hitbox.
                    px, py = jogador.rect.centerx, jogador.rect.centery
                    fase_cometa = frame_count * 0.12
                    pulso = 2 + int((math.sin(frame_count * 0.22) + 1) * 2)
                    pygame.draw.ellipse(display_surface, (255, 125, 35),
                                        (px - 34 - pulso, py - 39 - pulso, 68 + pulso * 2, 78 + pulso * 2), 3)
                    pygame.draw.arc(display_surface, (255, 230, 100),
                                    (px - 39, py - 43, 78, 86), fase_cometa, fase_cometa + 4.2, 3)
                    pygame.draw.arc(display_surface, (255, 75, 35),
                                    (px - 29, py - 35, 58, 70), -fase_cometa, -fase_cometa + 3.7, 2)
                    # Pequenas chamas triangulares em órbita, determinísticas e baratas por frame.
                    for i in range(8):
                        ang = fase_cometa + i * (math.tau / 8)
                        rx = px + int(math.cos(ang) * 35)
                        ry = py + int(math.sin(ang) * 42)
                        tamanho = 4 + (i % 3)
                        ponta = (rx + int(math.cos(ang) * tamanho * 1.8),
                                 ry + int(math.sin(ang) * tamanho * 1.8))
                        base1 = (rx + int(math.cos(ang + 2.3) * tamanho),
                                 ry + int(math.sin(ang + 2.3) * tamanho))
                        base2 = (rx + int(math.cos(ang - 2.3) * tamanho),
                                 ry + int(math.sin(ang - 2.3) * tamanho))
                        pygame.draw.polygon(display_surface, (255, 185 + (i % 2) * 45, 55),
                                            (ponta, base1, base2))
                # v3.153: COMBO/FEBRE ao lado da distância; pausa embaixo à direita.
                # HUD e hitbox do botão compartilham HUD_PAUSA_AREA.
                if not (tutorial_corrida and tutorial_corrida.ativo):
                    # Tutorial usa um unico cartao de instrucao; HUD normal fica
                    # intocado em toda corrida depois das seis licoes.
                    desenhar_hud_compacto(
                        display_surface, metros=metros_atuais, moedas=moedas_coletadas,
                        missoes=missoes_atuais, jogador=jogador, combo=combo_contagem,
                        multiplicador=multiplicador_combo() if combo_contagem > 0 else 1,
                        combo_timer=combo_timer, febre=febre_carga, febre_timer=febre_timer,
                        febre_turbo_restante=febre_turbo_distancia_restante,
                        idioma=dados.get('idioma', 'pt_BR'), frame=frame_count,
                        fonte_grande=fonte_grande, fonte_missoes=fonte_missoes,
                        fonte_pequena=fonte_pequena, render=render_texto_cacheado,
                        botao_pausa=btn_pausa)
                    acabamento_hud(display_surface, frame_count, modo_grafico_leve(dados))
                    if frame_count < palavra_hud_ate and ((frame_count // 13) % 4 != 3 or frame_count < palavra_festa_ate):
                        palavra_partida.desenhar_hud(display_surface, dados.get("idioma", "pt_BR"))
                    if frame_count < palavra_festa_ate:
                        _prod_fx_palavra(display_surface, frame_count, palavra_festa_ate, fonte_grande)
                    if frame_count < tutorial_concluido_ate:
                        _prod_mensagem_tutorial(display_surface, dados.get('idioma','pt_BR'), frame_count)
                    desenhar_botoes(display_surface, dados, fonte_missoes, frame_count)
                if febre_timer > 0:
                    if febre_turbo_distancia_restante > 0:
                        pygame.draw.rect(display_surface, (255, 215, 70), (0, 0, LARGURA_VIRTUAL, 6))
                        pygame.draw.rect(display_surface, (255, 145, 35), (0, 6, LARGURA_VIRTUAL, 2))
                        desenhar_texto_centralizado(display_surface, f"COMETA DOURADO • {int(math.ceil(febre_turbo_distancia_restante))} m", fonte_missoes, (255, 225, 105), PRETO, 218)
                    else:
                        pygame.draw.rect(display_surface, (255, 80, 20), (0, 0, LARGURA_VIRTUAL, 5))
                if portal_tipo_ativo is not None:
                    cor_portal = PortalBonus.CORES[portal_tipo_ativo]
                    pygame.draw.rect(display_surface, (18, 20, 34), (90, 225, 270, 52), border_radius=10)
                    pygame.draw.rect(display_surface, cor_portal, (90, 225, 270, 52), 2, border_radius=10)
                    titulo_portal = {"INVERTIDO": "GRAVIDADE INVERTIDA", "FLAPPY": "DESAFIO FLAPPY", "TUNEL": "TÚNEL DE PRECISÃO", "AQUATICO": "ABISMO AQUÁTICO", "LASERS": "FUGA DOS LASERS", "TESOURO": "PORTAL DO TESOURO", "REFLEXOS": "PORTAL DE REFLEXOS"}.get(portal_tipo_ativo, "FASE BÔNUS")
                    desenhar_texto_centralizado(display_surface, titulo_portal, fonte_missoes, cor_portal, PRETO, 234)
                    desenhar_texto_centralizado(display_surface, f"{portal_timer // 60 + 1}s  •  PONTOS {portal_pontos}", fonte_pequena, BRANCO, PRETO, 254)
                    if portal_chefe_ativo:
                        cores_chefe = {"cidade": (255, 95, 115), "deserto": (255, 185, 70), "neve": (120, 220, 255), "vulcao": (255, 95, 35), "cidade_futurista": (80, 255, 230), "floresta": (120, 235, 105), "reino_submerso": (70, 220, 255), "ilhas_celestes": (185, 225, 255)}
                        nomes_chefe = {"cidade": "SENTINELA URBANA", "deserto": "ESCORPIÃO MECÂNICO", "neve": "TITÃ GLACIAL", "vulcao": "REI MAGMÁTICO", "cidade_futurista": "NÚCLEO HOLOGRÁFICO", "floresta": "JAGUAR ANCESTRAL", "reino_submerso": "SERPENTE ABISSAL", "ilhas_celestes": "ÁGUIA DA TEMPESTADE"}
                        cor_boss = cores_chefe.get(cenario_atual, (255, 95, 115))
                        # Chefe procedural em pixel-art, com silhueta e detalhes por bioma.
                        bx, by = LARGURA_VIRTUAL // 2, 315
                        pygame.draw.ellipse(display_surface, (8, 10, 24), (bx - 54, by - 44, 108, 94))
                        pygame.draw.rect(display_surface, cor_boss, (bx - 34, by - 30, 68, 58), border_radius=8)
                        pygame.draw.rect(display_surface, (25, 20, 35), (bx - 26, by - 20, 52, 36), border_radius=5)
                        pygame.draw.rect(display_surface, (255, 230, 130), (bx - 21, by - 12, 12, 8))
                        pygame.draw.rect(display_surface, (255, 230, 130), (bx + 9, by - 12, 12, 8))
                        pygame.draw.polygon(display_surface, cor_boss, [(bx - 30, by - 28), (bx - 46, by - 45), (bx - 12, by - 33)])
                        pygame.draw.polygon(display_surface, cor_boss, [(bx + 30, by - 28), (bx + 46, by - 45), (bx + 12, by - 33)])
                        pygame.draw.rect(display_surface, cor_boss, (bx - 48, by + 20, 18, 15))
                        pygame.draw.rect(display_surface, cor_boss, (bx + 30, by + 20, 18, 15))
                        desenhar_texto_centralizado(display_surface, f"{nomes_chefe.get(cenario_atual, 'CHEFE')} • HP {portal_chefe_hp}", fonte_missoes, cor_boss, PRETO, 370)
                        pygame.draw.rect(display_surface, (60, 25, 35), (55, 395, 340, 12), border_radius=5)
                        hp_max_boss = {"cidade": 3, "deserto": 4, "neve": 3, "vulcao": 4, "cidade_futurista": 4, "floresta": 3, "reino_submerso": 4, "ilhas_celestes": 4}.get(cenario_atual, 3)
                        pygame.draw.rect(display_surface, cor_boss, (55, 395, int(340 * max(0, portal_chefe_hp) / hp_max_boss), 12), border_radius=5)
                        if portal_chefe_avisos > 0:
                            aviso_y = max(90, min(ALTURA_VIRTUAL - 90, portal_chefe_faixa))
                            pygame.draw.rect(display_surface, (40, 18, 30), (LARGURA_VIRTUAL // 2 - 105, aviso_y - 16, 210, 32), border_radius=8)
                            pygame.draw.rect(display_surface, (255, 220, 80), (LARGURA_VIRTUAL // 2 - 105, aviso_y - 16, 210, 32), 2, border_radius=8)
                            desenhar_texto_centralizado(display_surface, "ATAQUE À VISTA! DESVIE", fonte_pequena, (255, 220, 80), PRETO, aviso_y - 8)

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
                    elif pup_key == "JETPACK":
                        tempo_restante = jogador.tempo_jetpack
                        if jogador.jetpack_fase == "subindo":
                            tempo_restante += jogador.jetpack_transicao_timer
                        elif jogador.jetpack_fase == "descendo":
                            tempo_restante = jogador.jetpack_pousando
                    elif pup_key == "CRONO":
                        tempo_restante = jogador.tempo_crono
                    elif pup_key == "TURBO_FANTASMA":
                        tempo_restante = jogador.tempo_turbo_fantasma

                    if pup_key == "PRISMA" and jogador.prisma_hits > 0:
                        tempo_restante = 1
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
                _pro_sub_fim()  # qa_hud_corrida

            if estado == "INICIO":
                t_anim = anim_menu_tempo / 45.0
                ease_out = 1.0 - (1.0 - t_anim) ** 3

                (cache_menus_qa.desenhar(display_surface, bg_parallax, cor_ceu_tupla, estado)
                 if cache_menus_qa is not None else bg_parallax.draw(display_surface, cor_ceu_tupla, False))
                # Menu e corrida usam o mesmo piso do cenario; nao estava no fundo cacheado.
                bg_parallax.draw_chao(display_surface)

                offset_y_titulo = int((1.0 - ease_out) * -220)
                float_y = math.sin(frame_count * 0.05) * 4
                pos_y_titulo = 95 + offset_y_titulo + float_y
                desenhar_titulo_pixel_art(display_surface, LARGURA_VIRTUAL // 2, pos_y_titulo, frame_count)

                # Palco mais definido, com fundo leve e os mesmos limites clicáveis.
                desenhar_palco_menu_premium(display_surface, frame_count, modo_grafico_leve(dados))
                painel_menu(display_surface, frame_count, modo_grafico_leve(dados))
                skin_menu_id = dados.get("skin_equipada", "AZUL")
                skin_menu = _sprite_skin_enquadrado(skin_menu_id, 'OCIOSO', (frame_count // 9) % 8, 70, 82, 4)
                display_surface.blit(skin_menu, (190, 125))
                pet_menu_id = dados.get("pet_equipado", "")
                if pet_menu_id in PETS_CONFIG:
                    fase_menu = (frame_count // 180) % 4
                    modo_pet_menu = 'SONO' if fase_menu == 2 else 'FESTA' if fase_menu == 3 else 'OCIOSO'
                    if modo_pet_menu == 'OCIOSO':
                        # A quantidade de quadros varia conforme o pet e o estado.
                        if (frame_count // 75) % 4 == 3:
                            quadros_menu = _quadros_pet_personalidade(pet_menu_id, 'SONO', (54, 48))
                            intervalo_pet = 5
                        else:
                            quadros_menu = _quadros_pet_menu_ocioso(pet_menu_id)
                            intervalo_pet = 3
                    else:
                        quadros_menu = _quadros_pet_personalidade(pet_menu_id, modo_pet_menu, (54, 48))
                        intervalo_pet = 3
                    pet_menu = quadros_menu[(frame_count // intervalo_pet) % len(quadros_menu)]
                    if not modo_grafico_leve(dados):
                        desenhar_fx_pet(display_surface, pet_menu_id, (165, 182), frame_count, 0.9, modo_grafico_leve(dados))
                    display_surface.blit(pet_menu, pet_menu.get_rect(center=(165, 182 + int(math.sin(frame_count * 0.12) * 2))))
                    if fase_menu == 3 and (frame_count // 17) % 2 == 0:
                        pygame.draw.circle(display_surface, (255, 146, 183), (170, 145), 4)
                        pygame.draw.circle(display_surface, BRANCO, (169, 144), 1)
                desenhar_selo_maestria(display_surface, dados, 282, 158, frame_count)

                card1_x = 35 - int((1.0 - ease_out) * 320)
                card2_x = 240 + int((1.0 - ease_out) * 320)
                card_y = 236  # Espaço de 22 px abaixo do palco e 14 px acima do botão JOGAR.

                rect_c1 = pygame.Rect(card1_x, card_y, 175, 70)
                desenhar_painel_identidade(display_surface, rect_c1, UI_CIANO)
                desenhar_acabamento_card_menu(display_surface, rect_c1, frame_count, UI_CIANO, modo_grafico_leve(dados))
                desenhar_texto_com_sombra(display_surface, t("recorde", dados), fonte_pequena, AMARELO_NEON, PRETO,
                                          (card1_x + 15, card_y + 12))
                desenhar_texto_com_sombra(display_surface, f"{dados['recorde']} {t('m_unit', dados)}", fonte_grande, BRANCO,
                                          PRETO, (card1_x + 15, card_y + 30))

                rect_c2 = pygame.Rect(card2_x, card_y, 175, 70)
                desenhar_painel_identidade(display_surface, rect_c2, AMARELO_MOEDA)
                desenhar_acabamento_card_menu(display_surface, rect_c2, frame_count, AMARELO_MOEDA, modo_grafico_leve(dados))
                desenhar_texto_com_sombra(display_surface, t("moedas_banco", dados), fonte_pequena, AMARELO_MOEDA, PRETO,
                                          (card2_x + 15, card_y + 12))
                desenhar_texto_com_sombra(display_surface, f"{dados['moedas_totais']}", fonte_grande, BRANCO, PRETO,
                                          (card2_x + 15, card_y + 30))

                botoes_menu = [
                    (btn_jogar, t("jogar", dados), (46, 204, 113)),
                    (btn_loja, t("loja_skins", dados), (52, 152, 219)),
                    (btn_upgrades, t("loja_upgrades", dados), (155, 89, 182)),
                    (btn_config, t("configuracoes", dados), (241, 196, 15)),
                    (btn_recordes, t("recordes_pessoais", dados), (26, 188, 156)),
                    (btn_desafios, "DESAFIOS DIÁRIOS / SEMANAIS", (115, 85, 210))
                ]

                for idx, (btn_rect, texto_btn, cor_btn) in enumerate(botoes_menu):
                    if _IDIOMA_ATUAL_I18N not in ('pt_BR', 'en_US'):
                        texto_btn = _i18n247.localizar_literal(texto_btn, _IDIOMA_ATUAL_I18N)
                    t_btn = max(0.0, min(1.0, (anim_menu_tempo - idx * 4) / 28.0))
                    e_btn = 1.0 - (1.0 - t_btn) ** 3
                    offset_y = int((1.0 - e_btn) * 450)
                    rect_desenhado = btn_rect  # Área clicável idêntica ao desenho.
                    fonte_menu = fonte_missoes if fonte.size(texto_btn)[0] > btn_rect.w - 20 else fonte
                    texto_menu = texto_ajustado_hud(texto_btn, fonte_menu, btn_rect.w - 20)
                    desenhar_botao_premium(display_surface, rect_desenhado, texto_menu, fonte_menu, cor_btn, BRANCO,
                                           frame_count, idx == 0 and (frame_count // 20) % 2 == 0)

                if PIXELRUSH_DEV_BUILD:
                    pygame.draw.rect(display_surface, (42, 107, 127), btn_menu_dev, border_radius=10)
                    pygame.draw.rect(display_surface, (182, 241, 255), btn_menu_dev, 2, border_radius=10)
                    desenhar_rotulo_botao(display_surface, "DEV - MENU DE TESTES (F12)", fonte_missoes,
                                          BRANCO, PRETO, btn_menu_dev)
                desenhar_texto_centralizado(display_surface, f"{VERSAO} - PIXEL RUSH" + (" DEV" if PIXELRUSH_DEV_BUILD else ""),
                                            fonte_pequena, BRANCO, PRETO,
                                            ALTURA_VIRTUAL - 30)

            elif estado == "CANTINHO_PETS":
                (cache_menus_qa.desenhar(display_surface, bg_parallax, cor_ceu_tupla, estado)
                 if cache_menus_qa is not None else bg_parallax.draw(display_surface, cor_ceu_tupla, False))
                desenhar_cantinho_pets(display_surface, dados, pet_cantinho_selecionado,
                                       frame_count, pet_cantinho_acao,
                                       pet_cantinho_acao_ate, pet_cantinho_mensagem,
                                       pet_cantinho_mensagem_ate, modo_grafico_leve(dados))

            elif estado == "BASE_CORREDOR":
                (cache_menus_qa.desenhar(display_surface, bg_parallax, cor_ceu_tupla, estado)
                 if cache_menus_qa is not None else bg_parallax.draw(display_surface, cor_ceu_tupla, False))
                base = dados.setdefault("base_corredor", {"nivel": 1, "trofeus": [], "decoracao": 0, "mecanicas_descobertas": []})
                partidas_base = int(dados.get("estatisticas_permanentes", {}).get("partidas", 0))
                base["nivel"] = max(1, min(5, 1 + partidas_base // 10))
                base["decoracao"] = max(0, base["nivel"] - 1)
                desenhar_texto_centralizado(display_surface, "BASE DO CORREDOR", fonte_grande, AMARELO_NEON, PRETO, 52)
                desenhar_texto_centralizado(display_surface, f"NÍVEL {base['nivel']}  •  PARTIDAS {partidas_base}", fonte, BRANCO, PRETO, 94)
                # Base decorativa leve: formas simples, sem imagens ou superfícies novas.
                pygame.draw.rect(display_surface, (28, 38, 58), (25, 145, 400, 300), border_radius=12)
                pygame.draw.rect(display_surface, (70, 210, 220), (25, 145, 400, 300), 2, border_radius=12)
                pygame.draw.rect(display_surface, (65, 75, 95), (55, 335, 340, 75), border_radius=6)
                pygame.draw.rect(display_surface, (115, 135, 155), (70, 315, 70, 20))
                pygame.draw.rect(display_surface, (115, 135, 155), (310, 315, 70, 20))
                for i in range(base["decoracao"]):
                    cor_decor = ((255, 205, 70), (75, 220, 170), (170, 120, 255), (255, 110, 120))[i % 4]
                    pygame.draw.rect(display_surface, cor_decor, (90 + i * 65, 250 - (i % 2) * 18, 34, 45), border_radius=4)
                    pygame.draw.rect(display_surface, BRANCO, (90 + i * 65, 250 - (i % 2) * 18, 34, 45), 1)
                desenhar_texto_com_sombra(display_surface, "TROFÉUS DE CHEFES", fonte, AMARELO_MOEDA, PRETO, (45, 470))
                trofeus = int(dados.get("estatisticas_novas", {}).get("chefes_derrotados", 0))
                desenhar_texto_com_sombra(display_surface, f"Chefes derrotados: {trofeus}", fonte_pequena, BRANCO, PRETO, (45, 505))
                desenhar_texto_com_sombra(display_surface, f"Biomas dominados: {sum(1 for v in dados.get('maestria_biomas', {}).values() if int(v.get('nivel', 0) if isinstance(v, dict) else v or 0) >= 3)}", fonte_pequena, BRANCO, PRETO, (45, 530))
                desenhar_texto_com_sombra(display_surface, "Sua base exibe troféus e lembranças da coleção.", fonte_missoes, CIANO_ESCUDO, PRETO, (35, 585))
                desenhar_texto_com_sombra(display_surface, "Decorações são cosméticas; não alteram atributos.", fonte_missoes, CINZA_TEXTO, PRETO, (35, 610))
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_voltar_base, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_voltar_base, 2, border_radius=10)
                desenhar_rotulo_botao(display_surface, t("voltar", dados), fonte, BRANCO, PRETO, btn_voltar_base)

            elif estado == "LOJA" and aba_loja == "PETS":
                desenhar_pets_em_breve(display_surface, btn_voltar)

            elif estado == "LOJA":
                t_anim = max(0.0, min(1.0, anim_menu_tempo / 35.0))
                ease_out = 1.0 - (1.0 - t_anim) ** 3
                (cache_menus_qa.desenhar(display_surface, bg_parallax, cor_ceu_tupla, estado)
                 if cache_menus_qa is not None else bg_parallax.draw(display_surface, cor_ceu_tupla, False))
                # Faixas premium sem novos recursos externos ou superfícies por frame.
                desenhar_painel_identidade(display_surface, pygame.Rect(17, 10, 416, 115),
                                           UI_CIANO, cabecalho=True)
                pygame.draw.rect(display_surface, (39, 60, 91), (24, 16, 402, 42), border_radius=12)
                pygame.draw.line(display_surface, (120, 203, 235), (36, 60), (414, 60), 1)
                pygame.draw.rect(display_surface, (12, 19, 36), (25, 125, 400, 42), border_radius=12)
                pygame.draw.rect(display_surface, (55, 87, 118), (25, 125, 400, 42), 2, border_radius=12)

                off_top = int((1.0 - ease_out) * -150)
                titulo_loja = t("loja_skins", dados) if aba_loja == "SKINS" else t("loja_pets", dados)
                desenhar_texto_centralizado(display_surface, titulo_loja, fonte_grande, AMARELO_NEON, PRETO,
                                            28 + off_top)
                desenhar_texto_centralizado(display_surface, f"{t('moedas_hud', dados)}: {dados['moedas_totais']}", fonte,
                                            AMARELO_MOEDA, PRETO, 66 + off_top)
                qtd_skins = len(set(dados.get("skins_desbloqueadas", ["AZUL"])) & set(SKINS))
                desenhar_texto_centralizado(display_surface, f"COLEÇÃO: {qtd_skins}/{len(SKINS)} SKINS", fonte_pequena,
                                            CIANO_ESCUDO, PRETO, 93 + off_top)
                pygame.draw.rect(display_surface, (6, 13, 27),
                                 (82, 112 + off_top, 286, 9), border_radius=4)
                pygame.draw.rect(display_surface, (73, 116, 145),
                                 (85, 114 + off_top, 280, 5), border_radius=3)
                progresso_colecao = int(280 * qtd_skins / max(1, len(SKINS)))
                if progresso_colecao > 0:
                    pygame.draw.rect(display_surface, (93, 227, 241),
                                     (85, 114 + off_top, progresso_colecao, 5), border_radius=3)

                cor_skins = (49, 129, 179) if aba_loja == "SKINS" else (39, 48, 70)
                cor_pets = (49, 129, 179) if aba_loja == "PETS" else (39, 48, 70)
                pygame.draw.rect(display_surface, (9, 15, 27), btn_aba_skins.move(0, 3), border_radius=9)
                pygame.draw.rect(display_surface, cor_skins, btn_aba_skins, border_radius=9)
                pygame.draw.rect(display_surface, (225, 245, 255) if aba_loja == "SKINS" else (128, 151, 178),
                                 btn_aba_skins, 2, border_radius=9)
                if aba_loja == "SKINS":
                    pygame.draw.rect(display_surface, (167, 239, 255),
                                     (btn_aba_skins.x + 18, btn_aba_skins.bottom - 5,
                                      btn_aba_skins.w - 36, 3), border_radius=1)
                desenhar_rotulo_botao(display_surface, "SKINS", fonte, BRANCO, PRETO, btn_aba_skins)
                pygame.draw.rect(display_surface, (9, 15, 27), btn_aba_pets.move(0, 3), border_radius=9)
                pygame.draw.rect(display_surface, cor_pets, btn_aba_pets, border_radius=9)
                pygame.draw.rect(display_surface, (225, 245, 255) if aba_loja == "PETS" else (128, 151, 178),
                                 btn_aba_pets, 2, border_radius=9)
                if aba_loja == "PETS":
                    pygame.draw.rect(display_surface, (167, 239, 255),
                                     (btn_aba_pets.x + 18, btn_aba_pets.bottom - 5,
                                      btn_aba_pets.w - 36, 3), border_radius=1)
                desenhar_rotulo_botao(display_surface, "PETS", fonte, BRANCO, PRETO, btn_aba_pets)
                if aba_loja == "SKINS":
                    stats_loja = dados.get("estatisticas_permanentes", {})
                    y_base = 170
                    skins_visiveis = list(SKINS.items())[loja_pagina * 7:(loja_pagina + 1) * 7]
                    for nome_skin, info in skins_visiveis:
                        rect_item = pygame.Rect(35, y_base, 380, 55)
                        sta_equipada = dados["skin_equipada"] == nome_skin
                        desbloqueada = nome_skin in dados["skins_desbloqueadas"]
                        cor_borda_item = VERDE_GRAMA if sta_equipada else (AZUL_IMA if desbloqueada else AMARELO_MOEDA)
                        pygame.draw.rect(display_surface, (10, 14, 24), rect_item.move(0, 3), border_radius=10)
                        desenhar_painel_identidade(display_surface, rect_item, cor_borda_item)
                        pygame.draw.rect(display_surface, cor_borda_item, (rect_item.x + 10, rect_item.y + 9, 48, 2))
                        pygame.draw.rect(display_surface, (18, 24, 38), (rect_item.x + 8, rect_item.y + 8, 44, 39), border_radius=8)
                        pygame.draw.rect(display_surface, (255, 255, 255), (rect_item.x + 8, rect_item.y + 8, 44, 39), 1, border_radius=8)
                        desenhar_moldura_raridade(display_surface, rect_item, raridade_de_skin(nome_skin),
                                                 frame_count, sta_equipada, modo_grafico_leve(dados))
                        desenhar_mini_skin(display_surface, nome_skin, 62, y_base + 28)
                        if nome_skin not in SKINS_ATIVAS_PROD:
                            pygame.draw.rect(display_surface, (18, 24, 36), (95, y_base + 22, 258, 24), border_radius=6)
                            pygame.draw.rect(display_surface, (255, 213, 102), (95, y_base + 22, 258, 24), 2, border_radius=6)
                            desenhar_rotulo_botao(display_surface, 'EM BREVE', fonte_missoes, (255, 227, 140), PRETO,
                                                  pygame.Rect(95, y_base + 22, 258, 24))
                        if nome_skin in SKINS_ATIVAS_PROD and (sta_equipada or desbloqueada):
                            cor_selo = (53, 157, 112) if sta_equipada else (52, 133, 175)
                            pygame.draw.rect(display_surface, cor_selo,
                                (374, y_base + 7, 31, 14), border_radius=6)
                            if sta_equipada:
                                pygame.draw.lines(display_surface, BRANCO, False,
                                    [(382, y_base + 14), (386, y_base + 18),
                                     (394, y_base + 10)], 2)
                            else:
                                pygame.draw.circle(display_surface, BRANCO,
                                                   (389, y_base + 14), 3)
                        desenhar_selo_status_loja(display_surface, 316, y_base + 7, "EQUIPADA" if sta_equipada else ("LIVRE" if desbloqueada else "BLOQ."),
                                                  (53, 157, 112) if sta_equipada else ((52, 133, 175) if desbloqueada else (120, 97, 52)))
                        desenhar_texto_com_sombra(display_surface, SKINS_NOMES.get(nome_skin, nome_skin), fonte_pequena, BRANCO, PRETO, (92, y_base + 5))
                        objetivo = SKINS_OBJETIVOS.get(nome_skin)
                        if nome_skin not in SKINS_ATIVAS_PROD: status_skin = "EM BREVE"
                        elif sta_equipada: status_skin = "EQUIPADA"
                        elif desbloqueada: status_skin = "TOQUE PARA EQUIPAR"
                        elif objetivo:
                            ok_obj = int(stats_loja.get(objetivo[1], 0)) >= objetivo[2]
                            status_skin = "OBJETIVO CONCLUÍDO - TOQUE" if ok_obj else f"{objetivo[0]} ({stats_loja.get(objetivo[1], 0)}/{objetivo[2]})"
                        else: status_skin = f"{info['preco']} moedas"
                        if nome_skin in SKINS_ATIVAS_PROD:
                            desenhar_texto_com_sombra(display_surface, status_skin[:42], fonte_missoes, AMARELO_MOEDA if not desbloqueada else CIANO_ESCUDO, PRETO, (92, y_base + 29))
                        y_base += 62
                    pygame.draw.rect(display_surface, (12, 19, 33), btn_loja_pagina_ant.move(0, 3), border_radius=9)
                    pygame.draw.rect(display_surface, (47, 61, 87), btn_loja_pagina_ant, border_radius=9)
                    pygame.draw.rect(display_surface, (124, 179, 205), btn_loja_pagina_ant, 1, border_radius=9)
                    pygame.draw.rect(display_surface, (12, 19, 33), btn_loja_pagina_prox.move(0, 3), border_radius=9)
                    pygame.draw.rect(display_surface, (47, 61, 87), btn_loja_pagina_prox, border_radius=9)
                    pygame.draw.rect(display_surface, (124, 179, 205), btn_loja_pagina_prox, 1, border_radius=9)
                    desenhar_rotulo_botao(display_surface, "◀ ANTERIOR", fonte_missoes, BRANCO, PRETO, btn_loja_pagina_ant)
                    desenhar_rotulo_botao(display_surface, f"PRÓXIMA ▶  {loja_pagina + 1}/{(len(SKINS) + 6) // 7}", fonte_missoes, BRANCO, PRETO, btn_loja_pagina_prox)
                else:
                    desbloq_pets = dados.setdefault("pets_desbloqueados", [])
                    y_base = 170
                    pets_visiveis = list(PETS_CONFIG.items())[loja_pagina * PETS_POR_PAGINA:(loja_pagina + 1) * PETS_POR_PAGINA]
                    for pet_id, pet in pets_visiveis:
                        rect_pet = pygame.Rect(28, y_base, 394, 82)
                        equip = dados.get("pet_equipado") == pet_id
                        desbloq = pet_id in desbloq_pets
                        cor_borda_pet = VERDE_GRAMA if equip else (CIANO_ESCUDO if desbloq else pet["cor"])
                        pygame.draw.rect(display_surface, (9, 13, 23), rect_pet.move(0, 3), border_radius=11)
                        desenhar_painel_identidade(display_surface, rect_pet, cor_borda_pet)
                        pygame.draw.rect(display_surface, cor_borda_pet, (rect_pet.x + 14, rect_pet.y + 10, 60, 2))
                        pygame.draw.rect(display_surface, (17, 23, 37), (rect_pet.x + 8, rect_pet.y + 10, 54, 54), border_radius=10)
                        pygame.draw.rect(display_surface, (255, 255, 255), (rect_pet.x + 8, rect_pet.y + 10, 54, 54), 1, border_radius=10)
                        # Miniatura com silhueta pixel-art própria para cada espécie.
                        desenhar_moldura_raridade(display_surface, rect_pet, pet['raridade'],
                                                 frame_count, equip, modo_grafico_leve(dados))
                        desenhar_mini_pet(display_surface, pet_id, pet["cor"], 34, y_base + 12)
                        if equip:
                            pygame.draw.circle(display_surface, (68, 224, 146),
                                               (409, y_base + 12), 5)
                            pygame.draw.circle(display_surface, BRANCO,
                                               (408, y_base + 11), 2)
                        desenhar_selo_status_loja(display_surface, 319, y_base + 10, "EQUIPADO" if equip else ("LIVRE" if desbloq else "BLOQ."),
                                                  (53, 157, 112) if equip else ((66, 122, 170) if desbloq else (125, 101, 60)))
                        desenhar_texto_com_sombra(display_surface, f"{pet['nome']} • {pet['raridade']}", fonte_missoes, pet["cor"], PRETO, (76, y_base + 4))
                        nivel_pet_atual = nivel_pet(dados, pet_id)
                        prog_pet = dados.get("evolucao_pets", {}).get(pet_id, {"xp": 0})
                        desenhar_texto_com_sombra(display_surface, pet["habilidade"][:44], fonte_missoes, BRANCO, PRETO, (76, y_base + 22))
                        if equip: status_pet = f"NÍVEL {nivel_pet_atual}/{PETS_EVOLUCAO_MAX} • XP {int(prog_pet.get('xp', 0))} • EQUIPADO"
                        elif desbloq: status_pet = f"NÍVEL {nivel_pet_atual}/{PETS_EVOLUCAO_MAX} • XP {int(prog_pet.get('xp', 0))} • TOQUE PARA EQUIPAR"
                        elif pet["objetivo"]:
                            stats_pet = dados.get("estatisticas_permanentes", {})
                            if pet_id == "FANTASMA":
                                status_pet = f"OBJETIVO: CORRIDAS {stats_pet.get('partidas', 0)}/100"
                            elif pet_id == "TARTARUGA":
                                status_pet = f"OBJETIVO: PORTAIS AQUÁTICOS {stats_pet.get('portais_aquaticos', 0)}/25"
                            elif pet_id == "DRAGAO":
                                status_pet = f"OBJETIVO: COMBO {stats_pet.get('melhor_combo', 0)}/100 + FEBRES {stats_pet.get('febres', 0)}/100"
                            elif pet_id == "GOLEM":
                                status_pet = f"OBJETIVO: CHEFES {dados.get('estatisticas_novas', {}).get('chefes_derrotados', 0)}/10"
                            else:
                                status_pet = pet["objetivo"]
                        else: status_pet = f"{pet['preco']} moedas"
                        if pet_id == "DRAGAO_PLASMA" and not desbloq:
                            stats_pet = dados.get("estatisticas_permanentes", {})
                            status_pet = f"OBJETIVO: OBSTÁCULOS {stats_pet.get('obstaculos_destruidos', 0)}/250"
                        elif pet_id == "GATO_FANTASMA" and not desbloq:
                            stats_pet = dados.get("estatisticas_permanentes", {})
                            status_pet = f"OBJETIVO: CORRIDAS {stats_pet.get('partidas', 0)}/50"
                        desenhar_texto_com_sombra(display_surface, status_pet[:47], fonte_missoes, AMARELO_MOEDA if not desbloq else CIANO_ESCUDO, PRETO, (76, y_base + 54))
                        y_base += 88
                    desenhar_botao_premium(display_surface, btn_cantinho_pets,
                                            "CANTINHO DOS PETS", fonte_missoes,
                                            (63, 111, 166), BRANCO, frame_count, True)
                    total_paginas_pets = (len(PETS_CONFIG) + PETS_POR_PAGINA - 1) // PETS_POR_PAGINA
                    pygame.draw.rect(display_surface, (12, 19, 33), btn_loja_pagina_ant.move(0, 3), border_radius=9)
                    pygame.draw.rect(display_surface, (47, 61, 87), btn_loja_pagina_ant, border_radius=9)
                    pygame.draw.rect(display_surface, (124, 179, 205), btn_loja_pagina_ant, 1, border_radius=9)
                    pygame.draw.rect(display_surface, (12, 19, 33), btn_loja_pagina_prox.move(0, 3), border_radius=9)
                    pygame.draw.rect(display_surface, (47, 61, 87), btn_loja_pagina_prox, border_radius=9)
                    pygame.draw.rect(display_surface, (124, 179, 205), btn_loja_pagina_prox, 1, border_radius=9)
                    desenhar_rotulo_botao(display_surface, "◀ ANTERIOR", fonte_missoes, BRANCO, PRETO, btn_loja_pagina_ant)
                    desenhar_rotulo_botao(display_surface, f"PRÓXIMA ▶ {loja_pagina + 1}/{total_paginas_pets}", fonte_missoes, BRANCO, PRETO, btn_loja_pagina_prox)
                    # Indicador de rolagem/página para listas longas.
                    pygame.draw.rect(display_surface, (35, 45, 70), (427, 170, 5, 486), border_radius=3)
                    altura_cursor = max(35, int(486 * PETS_POR_PAGINA / len(PETS_CONFIG)))
                    cursor_y = 170 + int((486 - altura_cursor) * loja_pagina / max(1, total_paginas_pets - 1))
                    pygame.draw.rect(display_surface, CIANO_ESCUDO, (427, cursor_y, 5, altura_cursor), border_radius=3)

                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_voltar, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_voltar, 2, border_radius=10)
                surf_v = render_texto_cacheado(fonte, t("voltar_menu", dados), BRANCO)
                display_surface.blit(surf_v, (
                btn_voltar.centerx - surf_v.get_width() // 2, btn_voltar.centery - surf_v.get_height() // 2))

                # Pré-visualização ampliada: a superfície do personagem é criada uma vez por seleção.
                if item_preview_tipo and item_preview_id:
                    display_surface.blit(OVERLAY_PAUSA, (0, 0))
                    cor_preview = (70, 205, 255)
                    if item_preview_tipo == "SKIN":
                        cor_preview = SKINS[item_preview_id]["cor"]
                        nome_preview = SKINS_NOMES.get(item_preview_id, item_preview_id)
                        subtitulo_preview = "PRÉ-VISUALIZAÇÃO DE SKIN"
                    else:
                        pet_preview = PETS_CONFIG[item_preview_id]
                        cor_preview = pet_preview["cor"]
                        nome_preview = pet_preview["nome"]
                        subtitulo_preview = f"PET • {pet_preview['raridade']}"
                    pygame.draw.rect(display_surface, (6, 10, 18), rect_preview_popup.move(0, 5), border_radius=18)
                    desenhar_painel_identidade(display_surface, rect_preview_popup, UI_CONTORNO,
                                              cabecalho=True)
                    pygame.draw.rect(display_surface, (40, 52, 82), (rect_preview_popup.x + 2, rect_preview_popup.y + 2, rect_preview_popup.w - 4, 56), border_radius=18)
                    cor_preview_borda = misturar_cores(cor_preview, BRANCO, 0.48)
                    pygame.draw.rect(display_surface, cor_preview_borda,
                                     rect_preview_popup, 3, border_radius=18)
                    pygame.draw.rect(display_surface, (255, 255, 255), (rect_preview_popup.x + 12, rect_preview_popup.y + 14, rect_preview_popup.w - 24, 1))
                    pygame.draw.rect(display_surface, (15, 20, 34),
                                     (76, 188, 298, 194), border_radius=18)
                    pygame.draw.rect(display_surface, (64, 80, 111),
                                     (76, 188, 298, 194), 1, border_radius=18)
                    for x_estrela, y_estrela in ((96, 208), (338, 228), (108, 310), (347, 332)):
                        pygame.draw.line(display_surface, cor_preview_borda,
                            (x_estrela - 3, y_estrela), (x_estrela + 3, y_estrela), 1)
                        pygame.draw.line(display_surface, cor_preview_borda,
                            (x_estrela, y_estrela - 3), (x_estrela, y_estrela + 3), 1)
                    pygame.draw.ellipse(display_surface, (14, 18, 31),
                                        (122, 349, 205, 21))
                    pygame.draw.ellipse(display_surface, cor_preview_borda,
                                        (138, 350, 172, 12), 1)
                    pygame.draw.rect(display_surface, (17, 23, 39), (54, 404, 342, 92), border_radius=14)
                    pygame.draw.rect(display_surface, (255, 255, 255), (54, 404, 342, 92), 1, border_radius=14)
                    desenhar_texto_centralizado(display_surface, nome_preview,
                                                  fonte_grande, BRANCO, PRETO, 128)
                    desenhar_texto_centralizado(display_surface, subtitulo_preview,
                                                  fonte_missoes, BRANCO, PRETO, 164)
                    pygame.draw.line(display_surface, cor_preview_borda,
                                     (90, 174), (360, 174), 1)

                    raridade_preview = raridade_de_skin(item_preview_id) if item_preview_tipo == 'SKIN' else PETS_CONFIG[item_preview_id]['raridade']
                    desenhar_moldura_raridade(display_surface, pygame.Rect(76, 188, 298, 194),
                                             raridade_preview, frame_count, True, modo_grafico_leve(dados))
                    if item_preview_tipo == "SKIN":
                        # O personagem respira e gesticula enquanto espera ser equipado.
                        # O recorte usa a silhueta visível, sem cortar cabeça nem pernas.
                        display_surface.blit(_popup_skin_animado(item_preview_id, frame_count), (135, 180))
                    else:
                        desenhar_fx_pet(display_surface, item_preview_id, (225, 257), frame_count, 1.3 if not modo_grafico_leve(dados) else 0.9, modo_grafico_leve(dados))
                        desenhar_preview_pet_popup(display_surface, item_preview_id, frame_count, pygame.Rect(120, 196, 210, 170))
                    if False and item_preview_tipo == "SKIN":
                        estilos_comprados_ui = dados.get("estilos_skins_comprados", {}).get(item_preview_id, [1])
                        custo_ui = 500 * item_preview_estilo
                        if item_preview_estilo == 1:
                            texto_estilo_ui = "ESTILO BASE"
                            acao_ui = "EQUIPAR SKIN / COMPRAR"
                        elif item_preview_estilo in estilos_comprados_ui:
                            texto_estilo_ui = f"ESTILO {item_preview_estilo}/8 • ADQUIRIDO"
                            acao_ui = "EQUIPAR ESTILO"
                        else:
                            texto_estilo_ui = f"ESTILO {item_preview_estilo}/8 • {custo_ui} MOEDAS"
                            acao_ui = "CONFIRMAR COMPRA" if item_preview_confirmar else "COMPRAR ESTILO"
                        desenhar_texto_centralizado(display_surface, texto_estilo_ui, fonte_pequena, (255, 220, 95), PRETO, 414)
                        if item_preview_estilo > 1 and item_preview_estilo not in estilos_comprados_ui:
                            pygame.draw.rect(display_surface, (35, 55, 90), btn_preview_compra, border_radius=9)
                            pygame.draw.rect(display_surface, (255, 205, 75), btn_preview_compra, 2, border_radius=9)
                            desenhar_texto_centralizado(display_surface, acao_ui, fonte_pequena, BRANCO, PRETO, btn_preview_compra.centery)


                    if item_preview_tipo == "SKIN":
                        objetivo_preview = SKINS_OBJETIVOS.get(item_preview_id)
                        if objetivo_preview:
                            stats_preview = dados.get("estatisticas_permanentes", {})
                            progresso_preview = int(stats_preview.get(objetivo_preview[1], 0))
                            linha_info = f"Objetivo: {objetivo_preview[0]} ({min(progresso_preview, objetivo_preview[2])}/{objetivo_preview[2]})"
                        else:
                            linha_info = f"Preço: {SKINS[item_preview_id]['preco']} moedas"
                        desenhar_texto_centralizado(display_surface, linha_info, fonte_missoes, AMARELO_MOEDA, PRETO, 424)
                        # Sistema de estilos alternativos temporariamente desativado.
                        # Mantém somente a skin base na prévia da loja.
                        objetivos_estilo_ui = {
                            2: ("Destrua 100 obstáculos", "obstaculos_destruidos", 100),
                            3: ("Sobreviva a 30 corridas", "partidas", 30),
                            4: ("Percorra 5.000 m", "distancia_total", 5000),
                            5: ("Conclua 10 fases bônus", "fases_bonus", 10),
                            6: ("Alcance combo 50", "melhor_combo", 50),
                            7: ("Colete 10.000 moedas", "moedas_coletadas", 10000),
                            8: ("Percorra 20.000 m", "distancia_total", 20000),
                        }
                        if item_preview_estilo in objetivos_estilo_ui:
                            obj_nome, obj_chave, obj_meta = objetivos_estilo_ui[item_preview_estilo]
                            obj_valor = int(dados.get("estatisticas_permanentes", {}).get(obj_chave, 0))
                            desenhar_texto_centralizado(display_surface, f"Objetivo: {obj_nome} ({min(obj_valor, obj_meta)}/{obj_meta})", fonte_pequena, AMARELO_MOEDA, PRETO, 449)
                        for rect_seta, rotulo_seta, habilitada in () :
                            cor_seta = CINZA_BOTAO if habilitada else (45, 48, 62)
                            pygame.draw.rect(display_surface, cor_seta, rect_seta, border_radius=8)
                            pygame.draw.rect(display_surface, cor_preview if habilitada else CINZA_TEXTO,
                                             rect_seta, 2, border_radius=8)
                            desenhar_rotulo_botao(display_surface, rotulo_seta, fonte, BRANCO, PRETO, rect_seta)
                    else:
                        pet_preview = PETS_CONFIG[item_preview_id]
                        habilidade = pet_preview["habilidade"]
                        palavras_hab = habilidade.split()
                        linhas_hab = []
                        linha_hab = ""
                        largura_hab = 360
                        for palavra_hab in palavras_hab:
                            teste_hab = f"{linha_hab} {palavra_hab}".strip()
                            if linha_hab and render_texto_cacheado(fonte_missoes, teste_hab, BRANCO).get_width() > largura_hab:
                                linhas_hab.append(linha_hab)
                                linha_hab = palavra_hab
                            else:
                                linha_hab = teste_hab
                        if linha_hab:
                            linhas_hab.append(linha_hab)
                        for indice_hab, texto_hab in enumerate(linhas_hab[:3]):
                            surf_hab = render_texto_cacheado(fonte_missoes, texto_hab, BRANCO)
                            display_surface.blit(surf_hab, (225 - surf_hab.get_width() // 2, 414 + indice_hab * 18))
                        if pet_preview.get("objetivo"):
                            stats_pet_preview = dados.get("estatisticas_permanentes", {})
                            if item_preview_id == "FANTASMA":
                                progresso_pet_preview = f"Corridas: {min(int(stats_pet_preview.get('partidas', 0)), 100)}/100"
                            elif item_preview_id == "TARTARUGA":
                                progresso_pet_preview = f"Portais aquáticos: {min(int(stats_pet_preview.get('portais_aquaticos', 0)), 25)}/25"
                            elif item_preview_id == "DRAGAO":
                                progresso_pet_preview = f"Combo: {min(int(stats_pet_preview.get('melhor_combo', 0)), 100)}/100 • Febres: {min(int(stats_pet_preview.get('febres', 0)), 100)}/100"
                            elif item_preview_id == "GOLEM":
                                progresso_pet_preview = f"Chefes: {min(int(dados.get('estatisticas_novas', {}).get('chefes_derrotados', 0)), 10)}/10"
                            elif item_preview_id == "DRAGAO_PLASMA":
                                progresso_pet_preview = f"Obstáculos: {min(int(stats_pet_preview.get('obstaculos_destruidos', 0)), 250)}/250"
                            else:
                                progresso_pet_preview = f"Corridas: {min(int(stats_pet_preview.get('partidas', 0)), 50)}/50"
                            desenhar_texto_centralizado(display_surface, f"Objetivo: {pet_preview['objetivo']}", fonte_pequena, AMARELO_MOEDA, PRETO, 463)
                            desenhar_texto_centralizado(display_surface, progresso_pet_preview, fonte_pequena, CIANO_ESCUDO, PRETO, 481)
                        else:
                            desenhar_texto_centralizado(display_surface, f"Preço: {pet_preview['preco']} moedas", fonte_missoes, AMARELO_MOEDA, PRETO, 463)

                    pygame.draw.rect(display_surface, (14, 18, 30), btn_preview_voltar.move(0, 2), border_radius=10)
                    pygame.draw.rect(display_surface, CINZA_BOTAO, btn_preview_voltar, border_radius=10)
                    pygame.draw.rect(display_surface, BRANCO, btn_preview_voltar, 2, border_radius=10)
                    desenhar_rotulo_botao(display_surface, "VOLTAR", fonte, BRANCO, PRETO, btn_preview_voltar)
                    rotulo_preview, acao_preview = obter_acao_preview_loja(
                        item_preview_tipo, item_preview_id, dados, item_preview_confirmar)
                    cor_botao_preview = AMARELO_MOEDA if acao_preview in ("comprar", "comprar_confirmado", "desbloquear") else CIANO_ESCUDO
                    if acao_preview in ("objetivo_pendente", "sem_moedas"):
                        cor_botao_preview = (115, 120, 135)
                    pygame.draw.rect(display_surface, (14, 18, 30), btn_preview_compra.move(0, 2), border_radius=10)
                    pygame.draw.rect(display_surface, cor_botao_preview, btn_preview_compra, border_radius=10)
                    pygame.draw.rect(display_surface, BRANCO, btn_preview_compra, 2, border_radius=10)
                    fonte_botao_preview = fonte_pequena if len(rotulo_preview) > 16 else fonte_missoes
                    desenhar_rotulo_botao(display_surface, rotulo_preview, fonte_botao_preview, BRANCO, PRETO, btn_preview_compra)

            elif estado == "UPGRADES":
                t_anim = anim_menu_tempo / 35.0
                ease_out = 1.0 - (1.0 - t_anim) ** 3
                (cache_menus_qa.desenhar(display_surface, bg_parallax, cor_ceu_tupla, estado)
                 if cache_menus_qa is not None else bg_parallax.draw(display_surface, cor_ceu_tupla, False))

                off_top = int((1.0 - ease_out) * -150)
                desenhar_texto_centralizado(display_surface, t("loja_upgrades", dados), fonte_grande, AMARELO_NEON, PRETO,
                                            35 + off_top)
                desenhar_texto_centralizado(display_surface, f"{t('moedas_hud', dados)}: {dados['moedas_totais']}", fonte,
                                            AMARELO_MOEDA, PRETO, 80 + off_top)

                y_base = 125
                upgrades_visiveis = list(UPGRADES_CONFIG.items())[pagina_upgrades * UPGRADES_POR_PAGINA:(pagina_upgrades + 1) * UPGRADES_POR_PAGINA]
                for chave, conf in upgrades_visiveis:
                    rect_item = pygame.Rect(40, y_base, 370, 54)
                    pygame.draw.rect(display_surface, CINZA_PAINEL, rect_item, border_radius=10)
                    pygame.draw.rect(display_surface, conf["cor"], rect_item, 2, border_radius=10)

                    desenhar_icone_powerup(display_surface, chave, 65, y_base + 27)

                    nome_str = t(conf["nome_key"], dados)
                    desenhar_texto_com_sombra(display_surface, nome_str, fonte, BRANCO, PRETO, (95, y_base + 10))

                    nv_atual = dados["upgrades"].get(chave, 0)
                    max_nv = conf["max_nivel"]
                    nivel_visual = nv_atual + 1 if chave == "CLONE" else nv_atual
                    max_visual = max_nv + 1 if chave == "CLONE" else max_nv

                    for bx in range(max_visual):
                        cor_bar = conf["cor"] if bx < nivel_visual else (70, 70, 80)
                        pygame.draw.rect(display_surface, cor_bar, (95 + bx * 18, y_base + 31, 14, 12), border_radius=2)
                        pygame.draw.rect(display_surface, BRANCO, (95 + bx * 18, y_base + 31, 14, 12), 1, border_radius=2)

                    if nv_atual >= max_nv:
                        desenhar_texto_com_sombra(display_surface, t("maximo", dados), fonte_pequena, VERDE_GRAMA, PRETO,
                                                  (270, y_base + 18))
                    else:
                        custo = calcular_custo_upgrade(chave, nv_atual)
                        desenhar_texto_com_sombra(display_surface, f"${custo}", fonte_pequena, AMARELO_MOEDA, PRETO,
                                                  (270, y_base + 18))

                    y_base += 62

                total_paginas_upgrades = (len(UPGRADES_CONFIG) + UPGRADES_POR_PAGINA - 1) // UPGRADES_POR_PAGINA
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_upgrade_ant, border_radius=8)
                pygame.draw.rect(display_surface, BRANCO, btn_upgrade_ant, 2, border_radius=8)
                desenhar_rotulo_botao(display_surface, "◀ ANTERIOR", fonte_missoes, BRANCO, PRETO, btn_upgrade_ant)
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_upgrade_prox, border_radius=8)
                pygame.draw.rect(display_surface, BRANCO, btn_upgrade_prox, 2, border_radius=8)
                desenhar_rotulo_botao(display_surface, f"PRÓXIMA ▶ {pagina_upgrades + 1}/{total_paginas_upgrades}", fonte_missoes, BRANCO, PRETO, btn_upgrade_prox)
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_voltar, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_voltar, 2, border_radius=10)
                surf_v = render_texto_cacheado(fonte, t("voltar_menu", dados), BRANCO)
                display_surface.blit(surf_v, (
                btn_voltar.centerx - surf_v.get_width() // 2, btn_voltar.centery - surf_v.get_height() // 2))

            elif estado == "CONFIG_ACESSIBILIDADE":
                desenhar_acessibilidade(display_surface, dados,
                                         tuple(_fonte_painel_localizado(f) for f in
                                               (fonte, fonte_pequena, fonte_grande)), acess_rects)

            elif estado == "CONFIG_CONTROLES":
                desenhar_painel_controles(display_surface, dados,
                                         _fonte_painel_localizado(fonte),
                                         _fonte_painel_localizado(fonte_missoes),
                                         controles_rects, frame_count)

            elif estado == "CONFIG":
                t_anim = anim_menu_tempo / 35.0
                ease_out = 1.0 - (1.0 - t_anim) ** 3
                (cache_menus_qa.desenhar(display_surface, bg_parallax, cor_ceu_tupla, estado)
                 if cache_menus_qa is not None else bg_parallax.draw(display_surface, cor_ceu_tupla, False))
                desenhar_painel_identidade(display_surface, pygame.Rect(35, 114, 380, 475),
                                           UI_CIANO, discreto=True)

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
                legenda_vib = f"{t('vibracao', dados)}: {vib_status}"
                fonte_vib = (fonte_missoes if _IDIOMA_ATUAL_I18N not in ('pt_BR','en_US')
                             and fonte.size(legenda_vib)[0] > btn_vibracao.width - 16 else fonte)
                surf_vib = render_texto_cacheado(fonte_vib, texto_ajustado_hud(legenda_vib, fonte_vib, btn_vibracao.width-16), BRANCO)
                display_surface.blit(surf_vib, (
                btn_vibracao.centerx - surf_vib.get_width() // 2, btn_vibracao.centery - surf_vib.get_height() // 2))

                # Idioma
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_lang, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_lang, 2, border_radius=10)
                lang_str = _i18n247.nome_idioma(dados.get('idioma', 'pt_BR'))
                rotulo_idioma = f"{t('idioma', dados)}: {lang_str}"
                fonte_lang = (fonte_missoes if _IDIOMA_ATUAL_I18N not in ('pt_BR','en_US')
                              and fonte.size(rotulo_idioma)[0] > btn_lang.width - 16 else fonte)
                rotulo_idioma = texto_ajustado_hud(rotulo_idioma, fonte_lang, btn_lang.width - 14)
                surf_l = render_texto_cacheado(fonte_lang, rotulo_idioma, BRANCO)
                display_surface.blit(surf_l, (
                btn_lang.centerx - surf_l.get_width() // 2, btn_lang.centery - surf_l.get_height() // 2))

                # Salvar e Voltar
                pygame.draw.rect(display_surface, (46, 204, 113), btn_voltar_config, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_voltar_config, 2, border_radius=10)
                surf_voltar_config = render_texto_cacheado(fonte, t("salvar", dados), BRANCO)
                display_surface.blit(surf_voltar_config, (btn_voltar_config.centerx - surf_voltar_config.get_width() // 2,
                                                          btn_voltar_config.centery - surf_voltar_config.get_height() // 2))
                _v3178_acabamento_config(display_surface)

            elif estado == "CONQUISTAS":
                (cache_menus_qa.desenhar(display_surface, bg_parallax, cor_ceu_tupla, estado)
                 if cache_menus_qa is not None else bg_parallax.draw(display_surface, cor_ceu_tupla, False))
                desenhar_texto_centralizado(display_surface, t("conquistas", dados), fonte_grande,
                                            AMARELO_NEON, PRETO, 47)
                stats = dados.get("estatisticas_permanentes", {})
                ids_desbloqueados = set(dados.get("conquistas_desbloqueadas", []))
                configuracoes = CONQUISTAS_CONFIG
                concluidas = sum(1 for item in configuracoes if item[0] in ids_desbloqueados)
                desenhar_progresso_conquistas(display_surface, concluidas, len(configuracoes))
                y_ach = 125
                conquistas_por_pagina = 5  # Mesmo número de cards; navegação original.
                total_paginas_conquistas = (len(configuracoes) + conquistas_por_pagina - 1) // conquistas_por_pagina
                visiveis = configuracoes[pagina_conquistas * conquistas_por_pagina:
                                         (pagina_conquistas + 1) * conquistas_por_pagina]
                for ident, titulo_key, descricao_key, stat_key, alvo, recompensa in visiveis:
                    concluida = ident in ids_desbloqueados
                    rect_ach = pygame.Rect(28, y_ach, 394, 78)
                    cor_ach = (103, 222, 162) if concluida else (96, 176, 229)
                    pygame.draw.rect(display_surface, (10, 17, 29), rect_ach.move(0, 3), border_radius=11)
                    pygame.draw.rect(display_surface, (29, 40, 60), rect_ach, border_radius=11)
                    pygame.draw.rect(display_surface, cor_ach, rect_ach, 2 if concluida else 1, border_radius=11)
                    pygame.draw.rect(display_surface, misturar_cores(cor_ach, BRANCO, .36),
                                     (rect_ach.x + 13, rect_ach.y + 6, 62, 2), border_radius=1)
                    titulo = texto_ajustado_hud(t(titulo_key, dados), fonte_missoes, 256)
                    desenhar_texto_com_sombra(display_surface, titulo, fonte_missoes,
                                              BRANCO, PRETO, (40, y_ach + 7))
                    desc = (t(descricao_key, dados) if (titulo_key in TEXTOS.get(dados.get("idioma", "pt_BR"), {})
                        or dados.get("idioma") in _i18n247.CATALOGOS_NOVOS) else descricao_key)
                    desc = texto_ajustado_hud(str(desc), fonte_pequena, 344)
                    desenhar_texto_com_sombra(display_surface, desc, fonte_pequena,
                                              (183, 208, 229), PRETO, (40, y_ach + 30))
                    progresso = min(max(1, alvo), max(0, int(stats.get(stat_key, 0))))
                    pct = 1.0 if concluida else progresso / max(1, alvo)
                    label = "OK" if concluida else f"{progresso}/{alvo}"
                    selo = pygame.Rect(330, y_ach + 7, 78, 20)
                    pygame.draw.rect(display_surface, (41, 113, 85) if concluida else (42, 78, 115),
                                     selo, border_radius=9)
                    pygame.draw.rect(display_surface, cor_ach, selo, 1, border_radius=9)
                    texto_selo = render_texto_cacheado(fonte_pequena, label, BRANCO)
                    display_surface.blit(texto_selo, texto_selo.get_rect(center=selo.center))
                    moeda_texto = ("REWARD" if dados.get("idioma") == "en_US" else "RECOMPENSA")
                    desenhar_texto_com_sombra(display_surface, f"{moeda_texto}: +{recompensa}", fonte_pequena,
                                              AMARELO_MOEDA, PRETO, (40, y_ach + 53))
                    pygame.draw.rect(display_surface, (17, 28, 44), (198, y_ach + 60, 209, 6), border_radius=3)
                    if pct:
                        pygame.draw.rect(display_surface, cor_ach,
                                         (199, y_ach + 61, max(1, int(207 * pct)), 4), border_radius=2)
                    y_ach += 94
                # Paginação e botão voltar seguem exatamente os retângulos existentes.
                for b in (btn_ach_ant, btn_ach_prox):
                    pygame.draw.rect(display_surface, (12, 20, 36), b.move(0, 3), border_radius=9)
                    pygame.draw.rect(display_surface, (48, 66, 92), b, border_radius=9)
                    pygame.draw.rect(display_surface, (119, 187, 215), b, 1, border_radius=9)
                desenhar_rotulo_botao(display_surface, "◀ ANTERIOR", fonte_missoes, BRANCO, PRETO, btn_ach_ant)
                desenhar_rotulo_botao(display_surface, f"PRÓXIMA ▶ {pagina_conquistas + 1}/{total_paginas_conquistas}",
                                     fonte_missoes, BRANCO, PRETO, btn_ach_prox)
                pygame.draw.rect(display_surface, (35, 45, 70), (427, 125, 5, 475), border_radius=3)
                altura_cursor_ach = max(35, int(475 * conquistas_por_pagina / len(configuracoes)))
                cursor_y_ach = 125 + int((475 - altura_cursor_ach) * pagina_conquistas /
                                         max(1, total_paginas_conquistas - 1))
                pygame.draw.rect(display_surface, CIANO_ESCUDO,
                                 (427, cursor_y_ach, 5, altura_cursor_ach), border_radius=3)
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_voltar, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_voltar, 2, border_radius=10)
                desenhar_rotulo_botao(display_surface, t("voltar", dados), fonte, BRANCO, PRETO, btn_voltar)

            elif estado == "DESAFIOS":
                (cache_menus_qa.desenhar(display_surface, bg_parallax, cor_ceu_tupla, estado)
                 if cache_menus_qa is not None else bg_parallax.draw(display_surface, cor_ceu_tupla, False))
                desenhar_texto_centralizado(display_surface, "DESAFIOS DIÁRIOS / SEMANAIS", fonte, AMARELO_NEON, PRETO, 48)
                desafios_ui = preparar_desafios(dados)
                for idx, chave in enumerate(("diario", "semanal")):
                    d = desafios_ui[chave]
                    yy = 130 + idx * 185
                    cor_d = (90, 205, 255) if chave == "diario" else (200, 130, 255)
                    pygame.draw.rect(display_surface, CINZA_PAINEL, (25, yy, 400, 155), border_radius=12)
                    pygame.draw.rect(display_surface, cor_d, (25, yy, 400, 155), 3, border_radius=12)
                    rotulo = "DESAFIO DIÁRIO" if chave == "diario" else "DESAFIO SEMANAL"
                    desenhar_texto_com_sombra(display_surface, rotulo, fonte, cor_d, PRETO, (42, yy + 12))
                    desenhar_texto_com_sombra(display_surface, d["titulo"], fonte_pequena, BRANCO, PRETO, (42, yy + 43))
                    progresso = min(int(d["alvo"]), int(d.get("progresso", 0)))
                    pygame.draw.rect(display_surface, (45, 48, 65), (42, yy + 72, 350, 12), border_radius=6)
                    pygame.draw.rect(display_surface, cor_d, (42, yy + 72, int(350 * progresso / max(1, d["alvo"])), 12), border_radius=6)
                    status = "CONCLUÍDO • RECOMPENSA RESGATADA" if d.get("resgatado") else f"{progresso}/{d['alvo']}  •  RECOMPENSA {d['recompensa']} MOEDAS"
                    desenhar_texto_com_sombra(display_surface, status, fonte_missoes, AMARELO_MOEDA, PRETO, (42, yy + 97))
                    periodo = desafios_ui["dia"] if chave == "diario" else desafios_ui["semana"]
                    desenhar_texto_com_sombra(display_surface, f"Período: {periodo}", fonte_missoes, BRANCO, PRETO, (42, yy + 123))
                pygame.draw.rect(display_surface, (35, 52, 83), btn_percurso_abrir, border_radius=10)
                pygame.draw.rect(display_surface, (120, 218, 235), btn_percurso_abrir, 2, border_radius=10)
                desenhar_rotulo_botao(display_surface, "DESAFIOS POR CODIGO", fonte_pequena, BRANCO, PRETO, btn_percurso_abrir)
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_voltar, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_voltar, 2, border_radius=10)
                desenhar_rotulo_botao(display_surface, t("voltar", dados), fonte, BRANCO, PRETO, btn_voltar)

            elif estado == "DESAFIO_PERCURSO":
                (cache_menus_qa.desenhar(display_surface, bg_parallax, cor_ceu_tupla, estado)
                 if cache_menus_qa is not None else bg_parallax.draw(display_surface, cor_ceu_tupla, False))
                desenhar_texto_centralizado(display_surface, "DESAFIO DE PERCURSO", fonte, AMARELO_NEON, PRETO, 62)
                desenhar_texto_centralizado(display_surface, "Mesmo codigo e mesma semente inicial", fonte_pequena, BRANCO, PRETO, 113)
                hoje_codigo = codigo_diario()
                pygame.draw.rect(display_surface, CINZA_PAINEL, (30, 156, 390, 110), border_radius=12)
                desenhar_texto_centralizado(display_surface, "HOJE  " + hoje_codigo, fonte, (125, 225, 240), PRETO, 171)
                pygame.draw.rect(display_surface, (38, 76, 90), btn_percurso_diario, border_radius=10)
                desenhar_rotulo_botao(display_surface, "JOGAR DESAFIO DO DIA", fonte_pequena, BRANCO, PRETO, btn_percurso_diario)
                desenhar_texto_centralizado(display_surface, "CODIGO: TOQUE NUM DIGITO PARA MUDAR", fonte_pequena, BRANCO, PRETO, 293)
                for i, caixa in enumerate(digitos_percurso):
                    pygame.draw.rect(display_surface, (38, 49, 76), caixa, border_radius=7)
                    pygame.draw.rect(display_surface, (113, 189, 216), caixa, 2, border_radius=7)
                    desenhar_rotulo_botao(display_surface, codigo_editavel[i], fonte, BRANCO, PRETO, caixa)
                pygame.draw.rect(display_surface, (43, 78, 92), btn_percurso_codigo, border_radius=10)
                desenhar_rotulo_botao(display_surface, "JOGAR PR-" + codigo_editavel, fonte_pequena, BRANCO, PRETO, btn_percurso_codigo)
                melhor = desafio_compartilhado.recorde(dados, 'PR-' + codigo_editavel)
                desenhar_texto_centralizado(display_surface, "SEU RECORDE: %d m" % melhor, fonte_pequena, AMARELO_MOEDA, PRETO, 556)
                desenhar_texto_centralizado(display_surface, "Compartilhe o codigo manualmente", fonte_pequena, BRANCO, PRETO, 596)
                desenhar_texto_centralizado(display_surface, "Sem ranking online; percursos podem variar", fonte_pequena, BRANCO, PRETO, 624)
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_percurso_voltar, border_radius=10)
                desenhar_rotulo_botao(display_surface, t("voltar", dados), fonte, BRANCO, PRETO, btn_percurso_voltar)

            elif estado == "RECORDES":
                (cache_menus_qa.desenhar(display_surface, bg_parallax, cor_ceu_tupla, estado)
                 if cache_menus_qa is not None else bg_parallax.draw(display_surface, cor_ceu_tupla, False))
                desenhar_texto_centralizado(display_surface, t("recordes_pessoais", dados), fonte_grande, AMARELO_NEON, PRETO, 52)
                stats = dados.get("estatisticas_permanentes", {})
                recordes = dados.get("recordes_biomas", {})
                corridas_patente = int(stats.get("partidas", 0))
                patente_atual = "RECRUTA"
                proxima_patente = ("BRONZE", 50)
                for nome_patente, alvo_patente, cor_patente in PATENTES_CONFIG:
                    if corridas_patente >= alvo_patente:
                        patente_atual = nome_patente
                    elif proxima_patente[0] == "BRONZE" or alvo_patente < proxima_patente[1]:
                        proxima_patente = (nome_patente, alvo_patente)
                cards = [
                    ("PATENTE / CORRIDAS", f"{patente_atual} • {corridas_patente} corridas", (255, 205, 55)),
                    ("COLEÇÃO DE SKINS", f"{len(dados.get('skins_desbloqueadas', ['AZUL']))}/{len(SKINS)} skins", CIANO_ESCUDO),
                    ("RECORDE GERAL", f"{dados.get('recorde', 0)} m", AMARELO_NEON),
                    ("DISTÂNCIA TOTAL", f"{stats.get('distancia_total', 0)} m", BRANCO),
                    ("MOEDAS COLETADAS", str(stats.get("moedas_coletadas", 0)), AMARELO_MOEDA),
                    ("MELHOR COMBO", str(stats.get("melhor_combo", 0)), (255, 120, 210)),
                ]
                y_card = 105
                for titulo_card, valor_card, cor_card in cards:
                    rect_card = pygame.Rect(28, y_card, 394, 52)
                    pygame.draw.rect(display_surface, CINZA_PAINEL, rect_card, border_radius=8)
                    pygame.draw.rect(display_surface, cor_card, rect_card, 2, border_radius=8)
                    desenhar_texto_com_sombra(display_surface, titulo_card, fonte_pequena, cor_card, PRETO, (40, y_card + 5))
                    surf_valor = render_texto_cacheado(fonte, valor_card, BRANCO)
                    display_surface.blit(surf_valor, (405 - surf_valor.get_width(), y_card + 25))
                    y_card += 60
                desenhar_texto_com_sombra(display_surface, "RECORDES POR BIOMA", fonte, AMARELO_NEON, PRETO, (36, 463))
                total_paginas_biomas = (len(BIOMAS_RECORDES_UI) + 2) // 3
                for rect_seta_bioma, rotulo_seta_bioma, habilitada_bioma in (
                    (btn_recorde_bioma_ant, "◀", pagina_recordes_biomas > 0),
                    (btn_recorde_bioma_prox, "▶", pagina_recordes_biomas < total_paginas_biomas - 1),
                ):
                    cor_seta_bioma = CINZA_BOTAO if habilitada_bioma else (45, 48, 62)
                    pygame.draw.rect(display_surface, cor_seta_bioma, rect_seta_bioma, border_radius=7)
                    pygame.draw.rect(display_surface, BRANCO if habilitada_bioma else CINZA_TEXTO,
                                     rect_seta_bioma, 1, border_radius=7)
                    desenhar_rotulo_botao(display_surface, rotulo_seta_bioma, fonte_missoes, BRANCO, PRETO, rect_seta_bioma)
                desenhar_texto_com_sombra(display_surface, f"{pagina_recordes_biomas + 1}/{total_paginas_biomas}",
                                          fonte_pequena, BRANCO, PRETO, (365, 459))
                biomas_visiveis_records = BIOMAS_RECORDES_UI[pagina_recordes_biomas * 3:(pagina_recordes_biomas + 1) * 3]
                for idx, (id_bioma, rotulo) in enumerate(biomas_visiveis_records):
                    xx = 28 + idx * 134
                    rect_bioma = pygame.Rect(xx, 489, 126, 58)
                    pygame.draw.rect(display_surface, CINZA_PAINEL, rect_bioma, border_radius=8)
                    pygame.draw.rect(display_surface, (100, 190, 255), rect_bioma, 2, border_radius=8)
                    surf_rotulo_bioma = render_texto_cacheado(fonte_pequena, rotulo, BRANCO)
                    display_surface.blit(surf_rotulo_bioma, (rect_bioma.centerx - surf_rotulo_bioma.get_width() // 2, rect_bioma.y + 6))
                    surf_recorde_bioma = render_texto_cacheado(fonte_pequena, f"{int(recordes.get(id_bioma, 0))} m", BRANCO)
                    display_surface.blit(surf_recorde_bioma, (rect_bioma.centerx - surf_recorde_bioma.get_width() // 2, rect_bioma.y + 31))
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_voltar_progresso, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_voltar_progresso, 2, border_radius=10)
                surf_voltar_rec = render_texto_cacheado(fonte, t("voltar", dados), BRANCO)
                display_surface.blit(surf_voltar_rec, (btn_voltar_progresso.centerx - surf_voltar_rec.get_width() // 2,
                                                       btn_voltar_progresso.centery - surf_voltar_rec.get_height() // 2))
                if bioma_recorde_popup is not None:
                    display_surface.blit(OVERLAY_PAUSA, (0, 0))
                    pygame.draw.rect(display_surface, (22, 28, 48), rect_recorde_bioma_popup, border_radius=16)
                    pygame.draw.rect(display_surface, (100, 190, 255), rect_recorde_bioma_popup, 3, border_radius=16)
                    nome_bioma_popup = dict(BIOMAS_RECORDES_UI).get(bioma_recorde_popup, bioma_recorde_popup.upper())
                    desenhar_texto_centralizado(display_surface, nome_bioma_popup, fonte_grande, AMARELO_NEON, PRETO, 160)
                    desenhar_texto_centralizado(display_surface, "RECORDES E PROGRESSO DO BIOMA", fonte_pequena, BRANCO, PRETO, 198)
                    metros_recorde_popup = int(recordes.get(bioma_recorde_popup, 0))
                    distancia_total_popup = int(stats.get(bioma_recorde_popup + "_total", 0))
                    maestrias_bioma = dados.get("maestria_biomas", {}).get(bioma_recorde_popup, {})
                    if isinstance(maestrias_bioma, dict):
                        nivel_maestria_popup = int(maestrias_bioma.get("nivel", 0))
                        recompensas_maestria_popup = maestrias_bioma.get("recompensas", [])
                    else:
                        nivel_maestria_popup = int(maestrias_bioma or 0)
                        recompensas_maestria_popup = []
                    for linha_popup, yy_popup, cor_linha_popup in (
                        (f"Recorde em uma corrida: {metros_recorde_popup} m", 247, CIANO_ESCUDO),
                        (f"Distância acumulada: {distancia_total_popup} m", 281, BRANCO),
                        (f"Maestria atual: nível {nivel_maestria_popup}/3", 315, AMARELO_MOEDA),
                    ):
                        surf_linha_popup = render_texto_cacheado(fonte_missoes, linha_popup, cor_linha_popup)
                        display_surface.blit(surf_linha_popup, (rect_recorde_bioma_popup.centerx - surf_linha_popup.get_width() // 2, yy_popup))
                    desenhar_texto_com_sombra(display_surface, "MARCOS DE MAESTRIA", fonte_missoes, AMARELO_NEON, PRETO, (54, 356))
                    marcos_maestria_popup = ((1, 1000, 100), (2, 4000, 250), (3, 10000, 500))
                    for idx_marco, (nivel_marco, alvo_marco, premio_marco) in enumerate(marcos_maestria_popup):
                        yy_marco = 385 + idx_marco * 47
                        concluido_marco = distancia_total_popup >= alvo_marco or nivel_maestria_popup >= nivel_marco
                        progresso_marco = min(distancia_total_popup, alvo_marco)
                        texto_marco = f"{'✓' if concluido_marco else '○'} Nível {nivel_marco}: {alvo_marco} m • +{premio_marco} moedas"
                        cor_marco = VERDE_GRAMA if concluido_marco else BRANCO
                        surf_marco = render_texto_cacheado(fonte_pequena, texto_marco, cor_marco)
                        display_surface.blit(surf_marco, (rect_recorde_bioma_popup.centerx - surf_marco.get_width() // 2, yy_marco))
                        pygame.draw.rect(display_surface, (55, 60, 80), (55, yy_marco + 19, 340, 6), border_radius=3)
                        pygame.draw.rect(display_surface, cor_marco,
                                         (55, yy_marco + 19, int(340 * progresso_marco / max(1, alvo_marco)), 6), border_radius=3)
                    pygame.draw.rect(display_surface, CINZA_BOTAO, btn_recorde_bioma_fechar, border_radius=9)
                    pygame.draw.rect(display_surface, BRANCO, btn_recorde_bioma_fechar, 2, border_radius=9)
                    desenhar_rotulo_botao(display_surface, "FECHAR", fonte, BRANCO, PRETO, btn_recorde_bioma_fechar)

            elif estado == "RANKING":
                (cache_menus_qa.desenhar(display_surface, bg_parallax, cor_ceu_tupla, estado)
                 if cache_menus_qa is not None else bg_parallax.draw(display_surface, cor_ceu_tupla, False))
                desenhar_texto_centralizado(display_surface, "RANKING LOCAL", fonte_grande, AMARELO_NEON, PRETO, 52)
                desenhar_texto_centralizado(display_surface, "Melhores corridas salvas neste dispositivo", fonte_pequena, BRANCO, PRETO, 88)
                ranking = dados.get("ranking_local", [])
                if not ranking:
                    desenhar_texto_centralizado(display_surface, "Jogue uma partida para registrar seu primeiro resultado.", fonte_missoes, BRANCO, PRETO, 220)
                for idx, item in enumerate(ranking[:8]):
                    yy = 112 + idx * 38
                    rect_rank = pygame.Rect(28, yy, 394, 34)
                    pygame.draw.rect(display_surface, CINZA_PAINEL, rect_rank, border_radius=8)
                    cor_rank = (255, 210, 75) if idx == 0 else (150, 220, 255)
                    pygame.draw.rect(display_surface, cor_rank, rect_rank, 2, border_radius=8)
                    texto_rank = f"#{idx + 1}  {item.get('distancia', 0)} m  •  {item.get('moedas', 0)} moedas"
                    desenhar_texto_com_sombra(display_surface, texto_rank, fonte_pequena, BRANCO, PRETO, (40, yy + 2))
                    desenhar_texto_com_sombra(display_surface, f"Combo {item.get('combo', 0)} • Chefes {item.get('chefes', 0)} • Relíquias {item.get('reliquias', 0)}", fonte_missoes, cor_rank, PRETO, (40, yy + 18))
                # Painel de contraste restrito aos rótulos internacionais da lista;
                # sem mudar áreas clicáveis, bioma, coordenadas ou mecânicas.
                if _IDIOMA_ATUAL_I18N not in ('pt_BR', 'en_US'):
                    pygame.draw.rect(display_surface, (20, 29, 47), (26, 417, 398, 175), border_radius=9)
                    pygame.draw.rect(display_surface, (70, 143, 185), (26, 417, 398, 175), 1, border_radius=9)
                desenhar_texto_com_sombra(display_surface, "DESAFIOS LOCAIS (recompensa única)", fonte, AMARELO_NEON, PRETO, (34, 430))
                nomes_desafios_rank = (("DISTANCIA_500", "Percorra 500 m", 100), ("COMBO_30", "Alcance combo 30", 150), ("CHEFE_1", "Derrote um chefe", 250), ("MOEDAS_500", "Consiga 500 moedas em uma corrida", 200))
                concluidos_rank = set(dados.get("desafios_ranking_concluidos", []))
                for ir, (idr, nome_r, premio_r) in enumerate(nomes_desafios_rank):
                    status_r = "CONCLUÍDO" if idr in concluidos_rank else f"+{premio_r} moedas"
                    desenhar_texto_com_sombra(display_surface, f"{'✓' if idr in concluidos_rank else '○'} {nome_r} — {status_r}", fonte_missoes, VERDE_GRAMA if idr in concluidos_rank else BRANCO, PRETO, (38, 460 + ir * 31))
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_voltar, border_radius=10)
                desenhar_rotulo_botao(display_surface, t("voltar", dados), fonte, BRANCO, PRETO, btn_voltar)

            elif estado == "RELIQUIAS":
                (cache_menus_qa.desenhar(display_surface, bg_parallax, cor_ceu_tupla, estado)
                 if cache_menus_qa is not None else bg_parallax.draw(display_surface, cor_ceu_tupla, False))
                desenhar_texto_centralizado(display_surface, "RELIQUIAS ANCESTRAIS", fonte_grande, AMARELO_NEON, PRETO, 52)
                stats_rel = dados.get("estatisticas_permanentes", {})
                stats_extra = dados.get("estatisticas_novas", {})
                desbloq_rel = dados.setdefault("reliquias_desbloqueadas", [])
                reliquias_visiveis = list(RELIQUIAS_CONFIG.items())[pagina_reliquias * RELIQUIAS_POR_PAGINA:(pagina_reliquias + 1) * RELIQUIAS_POR_PAGINA]
                y_rel = 112
                for rid, info_rel in reliquias_visiveis:
                    rect_rel = pygame.Rect(28, y_rel, 394, 94)
                    pygame.draw.rect(display_surface, CINZA_PAINEL, rect_rel, border_radius=10)
                    equipado_rel = dados.get("reliquia_equipada") == rid
                    desbloqueada_rel = rid in desbloq_rel
                    pygame.draw.rect(display_surface, VERDE_GRAMA if equipado_rel else info_rel["cor"], rect_rel, 2, border_radius=10)
                    desenhar_texto_com_sombra(display_surface, info_rel["nome"], fonte, info_rel["cor"], PRETO, (42, y_rel + 6))
                    desenhar_texto_com_sombra(display_surface, info_rel["descricao"], fonte_missoes, BRANCO, PRETO, (42, y_rel + 30))
                    progresso_rel = int(stats_extra.get(info_rel["stat"], stats_rel.get(info_rel["stat"], 0)))
                    status_rel = "EQUIPADA" if equipado_rel else ("DESBLOQUEADA • TOQUE PARA EQUIPAR" if desbloqueada_rel else f"{info_rel['desbloqueio']} ({min(progresso_rel, info_rel['alvo'])}/{info_rel['alvo']})")
                    desenhar_texto_com_sombra(display_surface, (status_rel if _IDIOMA_ATUAL_I18N not in ('pt_BR', 'en_US') else status_rel[:46]), fonte_missoes, AMARELO_MOEDA if not desbloqueada_rel else CIANO_ESCUDO, PRETO, (42, y_rel + 58))
                    y_rel += 101
                total_paginas_rel = (len(RELIQUIAS_CONFIG) + RELIQUIAS_POR_PAGINA - 1) // RELIQUIAS_POR_PAGINA
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_reliquia_ant, border_radius=7)
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_reliquia_prox, border_radius=7)
                desenhar_rotulo_botao(display_surface, "◀ ANTERIOR", fonte_missoes, BRANCO, PRETO, btn_reliquia_ant)
                desenhar_rotulo_botao(display_surface, f"PRÓXIMO ▶ {pagina_reliquias + 1}/{total_paginas_rel}", fonte_missoes, BRANCO, PRETO, btn_reliquia_prox)
                pygame.draw.rect(display_surface, CINZA_BOTAO, btn_voltar, border_radius=10)
                pygame.draw.rect(display_surface, BRANCO, btn_voltar, 2, border_radius=10)
                desenhar_rotulo_botao(display_surface, t("voltar", dados), fonte, BRANCO, PRETO, btn_voltar)

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
                desenhar_texto_com_sombra(display_surface,
                                          f"{t('melhor_combo', dados)}: {combo_melhor} | {t('quase_colisao', dados)}: {combo_quase_colisoes}",
                                          fonte_missoes, CIANO_ESCUDO, PRETO, (65, 304))

                pygame.draw.line(display_surface, CINZA_BOTAO, (65, 329), (385, 329), 2)

                desenhar_texto_com_sombra(display_surface, t("missoes_partida", dados), fonte_missoes, CIANO_ESCUDO, PRETO,
                                          (65, 337))
                y_m = 362
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
                desenhar_selo_maestria(display_surface, dados, 388, 170, frame_count)

                rect_stats = pygame.Rect(45, 210, 360, 290)
                borda_go = AMARELO_NEON if novo_recorde_alcançado else (255, 125, 128)
                desenhar_painel_identidade(display_surface, rect_stats, borda_go, cabecalho=True)

                desenhar_texto_com_sombra(display_surface, t("estatisticas", dados), fonte, AMARELO_NEON, PRETO, (65, 225))
                pygame.draw.line(display_surface, (123, 196, 221), (256, 240), (385, 240), 1)
                # Distância, moedas e combo são desenhados uma única vez nos
                # três cards animados de desenhar_resultados_premium().

                pygame.draw.line(display_surface, CINZA_BOTAO, (65, 337), (385, 337), 2)

                desenhar_texto_com_sombra(display_surface, t("missoes_partida", dados), fonte_missoes, CIANO_ESCUDO, PRETO,
                                          (65, 345))
                y_m = 373
                for m in missoes_atuais:
                    txt_m = t(m["key"], dados).format(m["alvo"])
                    st = "OK!" if m["concluida"] else f"{m['atual']}/{m['alvo']}"
                    cor_m = VERDE_SLOW if m["concluida"] else BRANCO
                    linha_m = texto_ajustado_hud(f"• {txt_m} ({st})", fonte_missoes, 314)
                    desenhar_texto_com_sombra(display_surface, linha_m, fonte_missoes, cor_m, PRETO, (70, y_m))
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

            if animacao_recompensa and not desenhar_animacao_recompensa(display_surface, animacao_recompensa,
                                                                         frame_count, modo_grafico_leve(dados)):
                animacao_recompensa = None

            if estado in ("PAUSA", "GAMEOVER") and cor_ceu_tupla == tuple(alvo_ceu):
                cache_telas_estaticas[chave_tela_estatica] = display_surface.copy()

        if estado == 'GAMEOVER':
            if inicio_tela_resultados is None:
                inicio_tela_resultados = frame_count
            desenhar_resultados_premium(display_surface, frame_count, inicio_tela_resultados,
                                        metros_atuais, moedas_coletadas, combo_melhor,
                                        int(dados.get('recorde', 0)), missoes_atuais,
                                        modo_grafico_leve(dados), dados)
            aprendizado_contextual.desenhar(display_surface, dados.get("idioma", "pt_BR"))
        else:
            inicio_tela_resultados = None

        ox, oy = gamefeel.deslocamento() if estado == "JOGANDO" else (0, 0)

        if E_ANDROID:
            tamanho_final = (LARGURA_TELA, ALTURA_TELA)
            pos_final = (ox, oy)
        else:
            tela.fill(cor_ceu_tupla)
            tamanho_final = (largura_render, altura_render)
            pos_final = (offset_x + ox, offset_y + oy)

        if PIXELRUSH_DEV_BUILD and estado == "DEV_MENU":
            display_surface.fill((12, 19, 33))
            pygame.draw.rect(display_surface, (25, 38, 59), (15, 16, 420, 765), border_radius=16)
            pygame.draw.rect(display_surface, (82, 213, 230), (15, 16, 420, 765), 2, border_radius=16)
            desenhar_texto_centralizado(display_surface, "PIXEL RUSH - DEV", fonte_grande,
                                        (255, 223, 123), PRETO, 35)
            desenhar_texto_centralizado(display_surface, "MENU DE TESTES", fonte,
                                        (145, 233, 255), PRETO, 76)
            desenhar_texto_centralizado(display_surface, "F12 fecha  •  savegame_DEV.json", fonte_pequena,
                                        BRANCO, PRETO, 112)
            info1 = "SKINS {}/{}   PETS {}/{}".format(
                len(dados.get("skins_desbloqueadas", [])), len(SKINS),
                len(dados.get("pets_desbloqueados", [])), len(PETS_CONFIG))
            desenhar_texto_centralizado(display_surface, info1, fonte_missoes,
                                        (170, 240, 204), PRETO, 147)
            desenhar_texto_centralizado(display_surface, "IMORTAL: {}  •  HITBOX: {}".format(
                "ON" if dev_imortalidade else "OFF", "ON" if mostrar_hitboxes else "OFF"),
                fonte_pequena, BRANCO, PRETO, 181)
            for indice, (rotulo, acao) in enumerate(opcoes_dev):
                coluna, linha = indice % 2, indice // 2
                caixa = pygame.Rect(25 + coluna * 208, 247 + linha * 67, 191, 49)
                cor = (55, 125, 142) if acao in ("colecao", "jogar", "febre") else (59, 80, 118)
                pygame.draw.rect(display_surface, (9, 13, 25), caixa.move(0, 3), border_radius=10)
                pygame.draw.rect(display_surface, cor, caixa, border_radius=10)
                pygame.draw.rect(display_surface, (183, 234, 246), caixa, 1, border_radius=10)
                rot = texto_ajustado_hud(rotulo, fonte_pequena, caixa.w - 12)
                desenhar_rotulo_botao(display_surface, rot, fonte_pequena, BRANCO, PRETO, caixa)
            pygame.draw.rect(display_surface, (75, 89, 117), btn_dev_voltar, border_radius=10)
            pygame.draw.rect(display_surface, BRANCO, btn_dev_voltar, 2, border_radius=10)
            desenhar_rotulo_botao(display_surface, "VOLTAR", fonte, BRANCO, PRETO, btn_dev_voltar)
            desenhar_texto_centralizado(display_surface, "Somente testes - progresso isolado", fonte_pequena,
                                        (189, 211, 226), PRETO, 727)

        # Replay visual de seis segundos: nunca reexecuta física, spawn nem saves.
        if estado == 'JOGANDO' and jogador is not None:
            _pro_sub_inicio("qa_replay_captura")
            replay_morte.capturar(display_surface, frame_count)
            _pro_sub_fim()
        elif estado == 'GAMEOVER':
            if not replay_morte.congelado:
                replay_morte.iniciar()  # automático, pode ser pulado por toque/tecla
            if replay_morte.ativo:
                replay_morte.desenhar(display_surface)
            else:
                replay_morte.desenhar_botao(display_surface)
        else:
            paisagem_sonora.atualizar(cenario_atual, estado, dados['vol_sfx'], clima.tipo)

        # Captura somente o primeiro frame congelado; gestos e progresso
        # invalidam o cache instantaneamente e redesenham o mundo real.
        if (estado == "JOGANDO" and tutorial_corrida and tutorial_corrida.ativo
                and getattr(tutorial_corrida, "_pausa_comando", False)):
            if cache_tutorial_congelado is None:
                cache_tutorial_congelado = display_surface.copy()
        else:
            cache_tutorial_congelado = None
        _pro_marcar("posprocessamento")
        _pro_sub_inicio('camera_gamefeel')
        tela_gamefeel = (display_surface if dados.get('acess_reduzir_efeitos', False)
                          else gamefeel.acabamento_camera(display_surface, estado == "JOGANDO"))
        _pro_sub_fim()
        if gpu_processor.enabled and estado == "JOGANDO" and not dados.get('acess_reduzir_efeitos', False):
            gpu_fxmask.fill((0, 0, 0))
            gpu_normal.fill((128, 128, 255))
            gpu_material.fill((180, 245, 90))
            gpu_flow.fill((0, 0, 0))
            gpu_geometry.fill((0, 0, 0))
            bg_parallax.world.draw_effect_mask(gpu_fxmask)
            bg_parallax.world.draw_normal_map(gpu_normal)
            bg_parallax.world.draw_material_map(gpu_material)
            bg_parallax.world.draw_flow_map(gpu_flow)
            bg_parallax.world.draw_geometry_map(gpu_geometry)
            tela_gamefeel = gpu_processor.process(
                tela_gamefeel, gpu_fxmask, gpu_normal, frame_count,
                bg_parallax.peso_noite, bg_parallax.cenario, clima.tipo, vel_jogo,
                material=gpu_material, flow=gpu_flow, geometry=gpu_geometry,
                travel=bg_parallax.world.travel)
        # QA750: caminho integrado no frame real, com rollback para o bloco
        # original INTACTO se o operador desativar a flag de QA.
        if _QA_PIPELINE_750:
            _qa_usa_camera = (estado == 'JOGANDO' and portal_tipo_ativo is None
                and not modo_grafico_leve(dados)
                and not dados.get('acess_reduzir_efeitos', False))
            _qa_finalizar_quadro(
                tela_gamefeel, tela, tamanho_final, pos_final, superficies_escala,
                camera_cinematica, jogador, vel_jogo,
                cenas_epicas.momento(bg_parallax.world.travel) if _qa_usa_camera else False,
                _qa_usa_camera, _pro_sub_inicio, _pro_sub_fim, _pro_marcar)
        else:
            # O enquadramento é pós-processamento visual; o mundo físico fica intacto.
            if estado == 'JOGANDO' and portal_tipo_ativo is None and not modo_grafico_leve(dados) and not dados.get('acess_reduzir_efeitos', False):
                _pro_sub_inicio("camera_smoothscale")
                tela_gamefeel = camera_cinematica.aplicar(
                    tela_gamefeel, jogador, vel_jogo,
                    cenas_epicas.momento(bg_parallax.world.travel), True)
                _pro_sub_fim()
            _pro_marcar("apresentacao")
            if tamanho_final == tela_gamefeel.get_size():
                superficie_final = tela_gamefeel
            else:
                _pro_sub_inicio("apresentacao_escala_final")
                superficie_final = superficies_escala.get(tamanho_final)
                if superficie_final is None:
                    try:
                        superficie_final = pygame.Surface(tamanho_final).convert()
                    except Exception:
                        superficie_final = pygame.Surface(tamanho_final)
                    superficies_escala[tamanho_final] = superficie_final
                    if len(superficies_escala) > 3:
                        superficies_escala.popitem(last=False)
                else:
                    superficies_escala.move_to_end(tamanho_final)
                pygame.transform.scale(tela_gamefeel, tamanho_final, superficie_final)
                _pro_sub_fim()
    
            _pro_sub_inicio("apresentacao_blit_final")
            tela.blit(superficie_final, pos_final)
            _pro_sub_fim()
            _pro_sub_inicio("apresentacao_swap")
            pygame.display.flip()
            _pro_sub_fim()
        _pro_marcar("limitador_fps")
        if monitor_diag is not None:
            monitor_diag.registrar_quadro(estado, cenario_atual, largura_render, altura_render,
                                            'leve' if PARTICULAS_VISUAIS_LIMITADAS else 'normal')
        _rep_fim(estado, cenario_atual, pontuacao // 10, frame_count, jogador)
        perf_biomas.antes_limitador()
        relogio.tick(FPS_RENDER)
        _pro_fim()
        perf_biomas.fim()

    if monitor_diag is not None:
        monitor_diag.salvar()
    perf_biomas.salvar()
    gpu_processor.close()
    pygame.quit()




# --- v3.173.0: piso premium global e leitura reforçada de todos os biomas ---
def _v3166_paleta_piso(cenario):
    return {
        'cidade': {
            'top':(94,97,104),'lane_a':(44,48,58),'lane_b':(52,56,67),'deep':(36,40,49),
            'line':(193,185,126),'accent':(128,134,144),'spark':(214,219,225),'seed':6138},
        'neve': {
            'top':(238,247,252),'lane_a':(110,133,158),'lane_b':(92,116,143),'deep':(78,98,125),
            'line':(252,252,255),'accent':(186,214,232),'spark':(255,255,255),'seed':3721},
        'deserto': {
            'top':(235,191,122),'lane_a':(198,144,90),'lane_b':(182,130,80),'deep':(146,99,58),
            'line':(244,212,146),'accent':(210,166,105),'spark':(255,231,173),'seed':9152},
        'vulcao': {
            'top':(255,139,66),'lane_a':(77,46,49),'lane_b':(93,54,58),'deep':(54,33,37),
            'line':(255,204,113),'accent':(160,87,72),'spark':(255,227,158),'seed':9715},
        'floresta': {
            'top':(117,188,86),'lane_a':(121,88,58),'lane_b':(103,74,51),'deep':(76,55,40),
            'line':(202,229,134),'accent':(145,117,81),'spark':(217,236,152),'seed':4311},
        'cidade_futurista': {
            'top':(72,241,255),'lane_a':(18,30,62),'lane_b':(24,37,71),'deep':(13,20,43),
            'line':(211,110,255),'accent':(91,209,232),'spark':(231,183,255),'seed':8127},
        'ilhas_celestes': {
            'top':(226,244,249),'lane_a':(111,165,196),'lane_b':(95,149,183),'deep':(73,121,158),
            'line':(174,232,199),'accent':(205,234,225),'spark':(246,252,255),'seed':5484},
        'reino_submerso': {
            'top':(96,224,219),'lane_a':(18,82,115),'lane_b':(14,70,100),'deep':(10,52,77),
            'line':(181,240,230),'accent':(68,175,172),'spark':(236,250,246),'seed':9921},
    }.get(cenario, {
        'top':(117,188,86),'lane_a':(121,88,58),'lane_b':(103,74,51),'deep':(76,55,40),
        'line':(202,229,134),'accent':(145,117,81),'spark':(217,236,152),'seed':3333})


def _v3166_obter_tile_chao(self):
    tile_pronto = self._cache_chao.get(self.cenario)
    if tile_pronto is not None:
        return tile_pronto
    cfg = _v3166_paleta_piso(self.cenario)
    rng = random.Random(cfg['seed'])
    largura_tile = 900
    altura_chao = 70
    tile = pygame.Surface((largura_tile, altura_chao)).convert()
    tile.fill(cfg['lane_a'])
    pygame.draw.rect(tile, cfg['top'], (0, 0, largura_tile, 6))
    pygame.draw.rect(tile, cfg['lane_b'], (0, 6, largura_tile, 22))
    pygame.draw.rect(tile, cfg['lane_a'], (0, 28, largura_tile, 20))
    pygame.draw.rect(tile, cfg['deep'], (0, 48, largura_tile, 22))
    pygame.draw.line(tile, cfg['accent'], (0, 6), (largura_tile - 1, 6), 2)
    pygame.draw.line(tile, misturar_cores(cfg['lane_b'], cfg['deep'], 0.50), (0, 28), (largura_tile - 1, 28), 1)
    pygame.draw.line(tile, misturar_cores(cfg['lane_a'], cfg['deep'], 0.65), (0, 48), (largura_tile - 1, 48), 1)

    # faixa central mais legível, com materiais ricos porém limpos.
    for x in range(0, largura_tile, 36):
        y = 11 + ((x // 18) % 11)
        comp = 9 + ((x // 27) % 8)
        pygame.draw.line(tile, misturar_cores(cfg['accent'], cfg['lane_b'], 0.35), (x + 8, y), (x + 8 + comp, y - (x % 2)), 1)
        if (x // 36) % 2 == 0:
            pygame.draw.line(tile, misturar_cores(cfg['deep'], cfg['line'], 0.22), (x + 5, y + 12), (x + 12, y + 11), 1)
    for x in range(16, largura_tile - 12, 57):
        py = 14 + ((x // 19) % 31)
        cor = misturar_cores(cfg['lane_a'], cfg['deep'], 0.28 if (x // 57) % 2 else 0.17)
        pygame.draw.rect(tile, cor, (x, py, 2 + (x // 57) % 3, 1 + (x // 114) % 2))
        if (x // 57) % 3 == 0:
            pygame.draw.rect(tile, misturar_cores(cfg['spark'], cfg['accent'], 0.58), (x + 3, py + 2, 2, 1))

    # Ombros laterais e marcações temáticas por bioma.
    if self.cenario == 'cidade':
        for x in range(24, largura_tile - 28, 120):
            pygame.draw.rect(tile, cfg['line'], (x, 38, 48, 3), border_radius=1)
            pygame.draw.rect(tile, cfg['accent'], (x + 1, 41, 45, 1))
        for x in range(18, largura_tile, 54):
            pygame.draw.line(tile, (64, 68, 76), (x, 58), (x + 12, 58), 1)
    elif self.cenario == 'neve':
        for x in range(8, largura_tile, 40):
            pygame.draw.arc(tile, (248, 251, 255), (x, 12, 24, 7), math.radians(180), math.radians(360), 1)
            pygame.draw.rect(tile, (183, 212, 230), (x + 4, 47, 11, 2))
    elif self.cenario == 'deserto':
        for x in range(14, largura_tile, 42):
            pygame.draw.arc(tile, (224, 184, 116), (x, 16, 22, 7), math.radians(180), math.radians(360), 1)
        for x in range(26, largura_tile - 18, 84):
            pygame.draw.line(tile, (180, 129, 78), (x, 53), (x + 20, 50), 1)
            pygame.draw.line(tile, (240, 211, 150), (x + 2, 54), (x + 12, 53), 1)
    elif self.cenario == 'vulcao':
        for x in range(12, largura_tile - 16, 64):
            pygame.draw.rect(tile, (255, 123, 58), (x, 37 + ((x // 64) % 2), 5, 2))
            pygame.draw.line(tile, (93, 47, 47), (x - 3, 51), (x + 9, 51), 1)
        for x in range(28, largura_tile - 30, 88):
            pygame.draw.line(tile, (255, 199, 109), (x, 20), (x + 9, 21), 1)
    elif self.cenario == 'floresta':
        for x in range(20, largura_tile - 24, 74):
            pygame.draw.line(tile, (89, 147, 72), (x, 9), (x - 3, 4), 1)
            pygame.draw.line(tile, (124, 181, 91), (x, 9), (x + 3, 3), 1)
            pygame.draw.line(tile, (87, 64, 44), (x + 10, 16), (x + 18, 14), 1)
        for x in range(12, largura_tile - 16, 53):
            pygame.draw.line(tile, (168, 132, 86), (x, 51), (x + 8, 50), 1)
    elif self.cenario == 'cidade_futurista':
        for x in range(14, largura_tile - 12, 38):
            pygame.draw.line(tile, (70, 238, 255), (x, 18), (x + 14, 18), 1)
            pygame.draw.line(tile, (204, 90, 255), (x + 18, 39), (x + 25, 39), 1)
        for x in range(28, largura_tile - 30, 88):
            pygame.draw.rect(tile, (68, 240, 255), (x, 53, 22, 2))
            pygame.draw.line(tile, (207, 115, 255), (x + 10, 55), (x + 10, 62), 1)
    elif self.cenario == 'ilhas_celestes':
        for x in range(18, largura_tile - 18, 62):
            pygame.draw.line(tile, (188, 236, 221), (x, 18), (x + 8, 12), 1)
            pygame.draw.line(tile, (219, 252, 238), (x + 3, 20), (x + 11, 14), 1)
        for x in range(30, largura_tile - 22, 92):
            pygame.draw.arc(tile, (247, 250, 255), (x, 46, 22, 5), math.radians(180), math.radians(360), 1)
            pygame.draw.rect(tile, (255, 238, 167), (x + 10, 48, 2, 2))
    elif self.cenario == 'reino_submerso':
        for x in range(12, largura_tile - 18, 40):
            pygame.draw.rect(tile, (48, 155, 176), (x, 18 + ((x // 40) % 14), 5, 10))
        for x in range(24, largura_tile - 20, 80):
            pygame.draw.circle(tile, (255, 185, 121), (x, 53), 3)
            pygame.draw.line(tile, (40, 181, 152), (x + 14, 52), (x + 10, 44), 2)

    # acabamento superior inteligente e contínuo.
    pygame.draw.rect(tile, cfg['top'], (0, 0, largura_tile, 4))
    pygame.draw.line(tile, misturar_cores(cfg['deep'], cfg['accent'], 0.55), (0, 4), (largura_tile - 1, 4), 2)
    for x in range(18, largura_tile - 10, 74):
        comprimento = 7 + ((x // 37) % 8)
        y_rastro = 7 + ((x // 29) % 6)
        pygame.draw.line(tile, cfg['line'], (x, y_rastro), (x + comprimento, max(5, y_rastro - 1)), 1)
    self._cache_chao[self.cenario] = tile
    return tile


def _v3166_desenhar_chao_vivo(self, superficie):
    clima = getattr(self, 'clima_tipo', 'limpo')
    t_anim = self.tempo_animacao * 0.12
    noite = max(0.0, min(1.0, getattr(self, 'peso_noite', 0.0)))
    if self.cenario == 'cidade':
        for x in range(-20, LARGURA_VIRTUAL + 40, 52):
            px = int((x - self.desloc_chao * 1.0) % (LARGURA_VIRTUAL + 52)) - 20
            pygame.draw.line(superficie, (122, 140, 158), (px, 741), (px + 20, 741), 1)
        if clima in ('chuva', 'tempestade', 'chuva_acida'):
            for x in range(0, LARGURA_VIRTUAL, 64):
                y = 734 + (x % 3)
                pygame.draw.line(superficie, (176, 196, 216), (x, y), (x + 14, y + 1), 1)
    elif self.cenario == 'neve':
        for x in range(10, LARGURA_VIRTUAL, 68):
            pygame.draw.arc(superficie, (240, 248, 255), (x, 726 + (x % 2) * 3, 24, 8), math.radians(180), math.radians(360), 1)
            if math.sin(t_anim * 1.3 + x) > 0.55:
                pygame.draw.rect(superficie, (255,255,255), (x + 9, 736, 1, 1))
    elif self.cenario == 'deserto':
        for x in range(0, LARGURA_VIRTUAL, 58):
            yy = 736 + int(math.sin(t_anim + x * 0.02) * 1)
            pygame.draw.line(superficie, (225, 188, 110), (x, yy), (x + 18, yy), 1)
            if (x // 58) % 2 == 0:
                pygame.draw.line(superficie, (245, 210, 145), (x + 8, yy + 7), (x + 16, yy + 6), 1)
    elif self.cenario == 'vulcao':
        for x in range(4, LARGURA_VIRTUAL, 62):
            pulso = int((0.5 + 0.5 * math.sin(t_anim * 1.4 + x)) * 2)
            pygame.draw.rect(superficie, (255, 121, 56), (x, 738 + pulso, 5, 2))
            pygame.draw.line(superficie, (255, 205, 116), (x + 1, 739 + pulso), (x + 3, 739 + pulso), 1)
    elif self.cenario == 'floresta':
        for x in range(8, LARGURA_VIRTUAL, 42):
            sway = int(math.sin(t_anim + x * 0.16) * 1)
            base_y = 738 + (x % 3 == 0)
            pygame.draw.line(superficie, (92, 150, 81), (x, base_y), (x + sway, 732), 1)
            if (x // 42) % 2 == 0:
                pygame.draw.line(superficie, (139, 188, 101), (x + 5, 739), (x + 7 + sway, 734), 1)
        for x in range(20, LARGURA_VIRTUAL, 96):
            shimmer = 1 if math.sin(t_anim * 1.4 + x) > 0.2 else 0
            pygame.draw.line(superficie, (156, 125, 86), (x, 747), (x + 8, 746 + shimmer), 1)
    elif self.cenario == 'cidade_futurista':
        for x in range(0, LARGURA_VIRTUAL, 56):
            brilho = 2 if math.sin(t_anim * 1.8 + x * 0.07) > 0 else 0
            pygame.draw.line(superficie, (74, 224, 244), (x, 739), (x + 16, 739), 1)
            pygame.draw.line(superficie, (224, 128, 255), (x + 8, 744 + brilho), (x + 14, 744 + brilho), 1)
    elif self.cenario == 'ilhas_celestes':
        for x in range(8, LARGURA_VIRTUAL, 60):
            pygame.draw.line(superficie, (185, 236, 220), (x, 739), (x + 12, 739), 1)
            if math.sin(t_anim * 1.15 + x * 0.06) > 0.15:
                pygame.draw.line(superficie, (226, 252, 240), (x + 2, 745), (x + 8, 741), 1)
    elif self.cenario == 'reino_submerso':
        for x in range(0, LARGURA_VIRTUAL, 62):
            yy = 738 + int(math.sin(t_anim * 1.3 + x * 0.05))
            pygame.draw.line(superficie, (96, 224, 219), (x, yy), (x + 14, yy), 1)

    # reação global sutil ao clima/noite, útil para todos os biomas.
    if clima in ('chuva', 'tempestade', 'chuva_acida'):
        for x in range(14, LARGURA_VIRTUAL, 82):
            y = 746 + (x % 2)
            pygame.draw.line(superficie, (192, 214, 233), (x, y), (x + 12, y + 1), 1)
    if noite > 0.25 and self.cenario in ('cidade','cidade_futurista','ilhas_celestes','vulcao'):
        for x in range(20, LARGURA_VIRTUAL, 90):
            pygame.draw.line(superficie, (255, 240, 200, int(35 + noite * 30)), (x, 732), (x + 10, 732), 1)


ParallaxBackground._obter_tile_chao = _v3166_obter_tile_chao
ParallaxBackground._desenhar_chao_vivo = _v3166_desenhar_chao_vivo



# --- v3.173.0: refino premium exclusivo da Cidade Futurista ---
_v3167_old_obter_tile_chao = ParallaxBackground._obter_tile_chao
_v3167_old_desenhar_chao_vivo = ParallaxBackground._desenhar_chao_vivo

def _v3167_obter_tile_chao(self):
    if self.cenario != 'cidade_futurista':
        return _v3167_old_obter_tile_chao(self)
    cache_key = self.cenario + '_v3167'
    tile_pronto = self._cache_chao.get(cache_key)
    if tile_pronto is not None:
        return tile_pronto
    largura_tile = 960
    altura_chao = 70
    tile = pygame.Surface((largura_tile, altura_chao)).convert()
    deep=(12, 20, 43); lane_a=(22, 34, 67); lane_b=(28, 43, 79); line=(79, 239, 255)
    spark=(228, 118, 255); alt=(184, 236, 243); top=(95, 230, 247)
    tile.fill(lane_a)
    pygame.draw.rect(tile, top, (0,0,largura_tile,4))
    pygame.draw.rect(tile, (70, 101, 148), (0,4,largura_tile,7))
    pygame.draw.rect(tile, lane_b, (0,11,largura_tile,18))
    pygame.draw.rect(tile, lane_a, (0,29,largura_tile,18))
    pygame.draw.rect(tile, deep, (0,47,largura_tile,23))
    pygame.draw.line(tile, alt, (0,4), (largura_tile-1,4), 1)
    pygame.draw.line(tile, misturar_cores(line, lane_b, 0.18), (0,11), (largura_tile-1,11), 1)
    pygame.draw.line(tile, misturar_cores(spark, lane_a, 0.18), (0,29), (largura_tile-1,29), 1)
    pygame.draw.line(tile, misturar_cores(deep, alt, 0.40), (0,47), (largura_tile-1,47), 1)

    # faixa de rolamento central mais premium e legível
    for x in range(0, largura_tile, 24):
        pygame.draw.line(tile, (54, 81, 129), (x, 11), (x, 47), 1)
    for x in range(12, largura_tile - 12, 46):
        pygame.draw.line(tile, line, (x, 18), (x + 14, 18), 1)
        pygame.draw.line(tile, spark, (x + 8, 36), (x + 15, 36), 1)
        pygame.draw.line(tile, alt, (x + 2, 23), (x + 6, 23), 1)
    for x in range(20, largura_tile - 18, 72):
        pygame.draw.rect(tile, (42, 63, 101), (x, 52, 18, 2))
        pygame.draw.line(tile, line, (x + 3, 53), (x + 8, 53), 1)
        pygame.draw.line(tile, spark, (x + 10, 53), (x + 14, 53), 1)
        pygame.draw.line(tile, (58, 86, 128), (x + 8, 54), (x + 8, 62), 1)
    for x in range(8, largura_tile - 8, 56):
        pygame.draw.line(tile, (100, 123, 176), (x, 8), (x + 12, 8), 1)
        pygame.draw.line(tile, (72, 239, 255), (x + 3, 42), (x + 11, 42), 1)
    self._cache_chao[cache_key] = tile
    return tile


def _v3167_desenhar_chao_vivo(self, superficie):
    _v3167_old_desenhar_chao_vivo(self, superficie)
    if self.cenario != 'cidade_futurista':
        return
    clima = getattr(self, 'clima_tipo', 'limpo')
    noite = max(0.0, min(1.0, getattr(self, 'peso_noite', 0.0)))
    t = self.tempo_animacao * 0.14
    # trilhas neon laterais e reflexos animados
    for x in range(0, LARGURA_VIRTUAL, 54):
        off = int(math.sin(t + x * 0.05) * 1)
        pygame.draw.line(superficie, (72, 236, 252), (x, 739 + off), (x + 15, 739 + off), 1)
        pygame.draw.line(superficie, (228, 120, 255), (x + 11, 745 - off), (x + 18, 745 - off), 1)
        if (x // 54) % 2 == 0:
            pygame.draw.line(superficie, (191, 236, 241), (x + 4, 733), (x + 9, 733), 1)
    for x in range(22, LARGURA_VIRTUAL, 88):
        pulso = 1 if math.sin(t * 1.7 + x * 0.06) > 0 else 0
        pygame.draw.rect(superficie, (44, 66, 101), (x, 752, 20, 2))
        pygame.draw.line(superficie, (80, 240, 255), (x + 3, 752 + pulso), (x + 8, 752 + pulso), 1)
        pygame.draw.line(superficie, (238, 121, 255), (x + 11, 752), (x + 15, 752), 1)
    if clima in ('chuva', 'tempestade', 'chuva_acida'):
        for x in range(12, LARGURA_VIRTUAL, 70):
            y = 734 + (x % 3)
            pygame.draw.line(superficie, (102, 218, 234), (x, y), (x + 10, y + 1), 1)
            pygame.draw.line(superficie, (210, 132, 247), (x + 3, y + 8), (x + 9, y + 8), 1)
    if noite > 0.2:
        for x in range(18, LARGURA_VIRTUAL, 96):
            pygame.draw.line(superficie, (255, 240, 211), (x, 731), (x + 8, 731), 1)


ParallaxBackground._obter_tile_chao = _v3167_obter_tile_chao
ParallaxBackground._desenhar_chao_vivo = _v3167_desenhar_chao_vivo



# --- v3.173.0: passe fino premium para todos os demais biomas ---
_v3168_old_obter_tile_chao = ParallaxBackground._obter_tile_chao
_v3168_old_desenhar_chao_vivo = ParallaxBackground._desenhar_chao_vivo

def _v3168_paleta_chao(cenario):
    paletas = {
        'neve': {
            'top': (231, 244, 252), 'mid1': (196, 219, 239), 'mid2': (166, 193, 222), 'base': (114, 145, 187),
            'line1': (255,255,255), 'line2': (207, 231, 246), 'accent': (184, 220, 243), 'shadow': (92, 124, 166),
        },
        'deserto': {
            'top': (242, 199, 131), 'mid1': (226, 177, 111), 'mid2': (199, 145, 92), 'base': (148, 104, 69),
            'line1': (254, 222, 164), 'line2': (239, 190, 126), 'accent': (214, 166, 108), 'shadow': (126, 87, 59),
        },
        'floresta': {
            'top': (137, 185, 105), 'mid1': (101, 146, 76), 'mid2': (76, 113, 58), 'base': (52, 76, 44),
            'line1': (188, 224, 148), 'line2': (133, 188, 104), 'accent': (106, 156, 86), 'shadow': (44, 63, 37),
        },
        'vulcao': {
            'top': (118, 77, 73), 'mid1': (93, 58, 56), 'mid2': (70, 43, 47), 'base': (43, 29, 35),
            'line1': (255, 171, 84), 'line2': (255, 214, 117), 'accent': (151, 88, 72), 'shadow': (34, 23, 28),
        },
        'ilhas_celestes': {
            'top': (221, 240, 245), 'mid1': (187, 215, 226), 'mid2': (151, 185, 204), 'base': (108, 144, 171),
            'line1': (247, 253, 252), 'line2': (170, 234, 201), 'accent': (136, 196, 222), 'shadow': (92, 124, 151),
        },
        'cidade_futurista': {
            'top': (95, 230, 247), 'mid1': (70, 101, 148), 'mid2': (28, 43, 79), 'base': (12, 20, 43),
            'line1': (79, 239, 255), 'line2': (228, 118, 255), 'accent': (184, 236, 243), 'shadow': (34, 48, 82),
        },
    }
    return paletas.get(cenario)

def _v3168_obter_tile_chao(self):
    pal = _v3168_paleta_chao(self.cenario)
    if pal is None:
        return _v3168_old_obter_tile_chao(self)
    cache_key = self.cenario + '_v3168'
    tile_pronto = self._cache_chao.get(cache_key)
    if tile_pronto is not None:
        return tile_pronto
    largura_tile = 960
    altura_chao = 70
    tile = pygame.Surface((largura_tile, altura_chao)).convert()
    tile.fill(pal['mid1'])
    pygame.draw.rect(tile, pal['top'], (0, 0, largura_tile, 4))
    pygame.draw.rect(tile, pal['mid1'], (0, 4, largura_tile, 9))
    pygame.draw.rect(tile, pal['mid2'], (0, 13, largura_tile, 18))
    pygame.draw.rect(tile, misturar_cores(pal['mid2'], pal['base'], 0.35), (0, 31, largura_tile, 18))
    pygame.draw.rect(tile, pal['base'], (0, 49, largura_tile, 21))
    pygame.draw.line(tile, pal['line1'], (0, 4), (largura_tile-1, 4), 1)
    pygame.draw.line(tile, pal['accent'], (0, 13), (largura_tile-1, 13), 1)
    pygame.draw.line(tile, pal['line2'], (0, 31), (largura_tile-1, 31), 1)
    pygame.draw.line(tile, pal['shadow'], (0, 49), (largura_tile-1, 49), 1)

    if self.cenario == 'neve':
        for x in range(0, largura_tile, 22):
            pygame.draw.line(tile, (176, 204, 224), (x, 15), (x + 2, 28), 1)
        for x in range(14, largura_tile - 14, 52):
            pygame.draw.line(tile, pal['line1'], (x, 21), (x + 12, 21), 1)
            pygame.draw.line(tile, pal['line2'], (x + 5, 38), (x + 10, 38), 1)
        for x in range(18, largura_tile - 18, 78):
            pygame.draw.rect(tile, misturar_cores(pal['mid1'], pal['base'], 0.22), (x, 54, 16, 2))
            pygame.draw.line(tile, pal['line1'], (x + 3, 55), (x + 7, 55), 1)
    elif self.cenario == 'deserto':
        for x in range(0, largura_tile, 24):
            pygame.draw.arc(tile, pal['accent'], (x, 18, 16, 6), math.radians(180), math.radians(360), 1)
        for x in range(10, largura_tile - 10, 50):
            pygame.draw.line(tile, pal['line1'], (x, 20), (x + 13, 20), 1)
            pygame.draw.line(tile, pal['line2'], (x + 7, 36), (x + 14, 36), 1)
        for x in range(20, largura_tile - 20, 82):
            pygame.draw.line(tile, pal['shadow'], (x, 52), (x + 4, 60), 1)
            pygame.draw.line(tile, pal['accent'], (x + 4, 60), (x + 8, 56), 1)
    elif self.cenario == 'floresta':
        for x in range(0, largura_tile, 26):
            pygame.draw.line(tile, pal['shadow'], (x, 16), (x + 1, 30), 1)
        for x in range(14, largura_tile - 14, 44):
            pygame.draw.line(tile, pal['line1'], (x, 19), (x + 10, 19), 1)
            pygame.draw.line(tile, pal['line2'], (x + 3, 35), (x + 8, 35), 1)
        for x in range(16, largura_tile - 20, 72):
            pygame.draw.line(tile, pal['accent'], (x, 54), (x + 2, 48), 1)
            pygame.draw.line(tile, pal['accent'], (x + 2, 50), (x + 5, 53), 1)
    elif self.cenario == 'vulcao':
        for x in range(0, largura_tile, 22):
            pygame.draw.line(tile, (84, 53, 55), (x, 15), (x + 1, 28), 1)
        for x in range(12, largura_tile - 12, 46):
            pygame.draw.line(tile, pal['line1'], (x, 19), (x + 9, 19), 1)
            pygame.draw.line(tile, pal['line2'], (x + 2, 20), (x + 6, 20), 1)
            pygame.draw.line(tile, pal['line1'], (x + 8, 37), (x + 14, 37), 1)
        for x in range(16, largura_tile - 16, 64):
            pygame.draw.line(tile, (93, 58, 57), (x, 53), (x + 7, 60), 1)
            pygame.draw.line(tile, pal['line1'], (x + 3, 57), (x + 8, 57), 1)
    elif self.cenario == 'ilhas_celestes':
        for x in range(0, largura_tile, 24):
            pygame.draw.line(tile, misturar_cores(pal['accent'], pal['shadow'], 0.30), (x, 15), (x + 2, 28), 1)
        for x in range(14, largura_tile - 14, 48):
            pygame.draw.line(tile, pal['line1'], (x, 19), (x + 11, 19), 1)
            pygame.draw.line(tile, pal['line2'], (x + 4, 36), (x + 10, 36), 1)
        for x in range(18, largura_tile - 18, 78):
            pygame.draw.rect(tile, misturar_cores(pal['mid1'], pal['base'], 0.20), (x, 54, 18, 2))
            pygame.draw.line(tile, pal['line2'], (x + 4, 55), (x + 9, 55), 1)
    elif self.cenario == 'cidade_futurista':
        for x in range(0, largura_tile, 24):
            pygame.draw.line(tile, (54, 81, 129), (x, 13), (x, 49), 1)
        for x in range(12, largura_tile - 12, 46):
            pygame.draw.line(tile, pal['line1'], (x, 20), (x + 14, 20), 1)
            pygame.draw.line(tile, pal['line2'], (x + 8, 38), (x + 15, 38), 1)
            pygame.draw.line(tile, pal['accent'], (x + 2, 25), (x + 6, 25), 1)
        for x in range(20, largura_tile - 18, 72):
            pygame.draw.rect(tile, (42, 63, 101), (x, 54, 18, 2))
            pygame.draw.line(tile, pal['line1'], (x + 3, 55), (x + 8, 55), 1)
            pygame.draw.line(tile, pal['line2'], (x + 10, 55), (x + 14, 55), 1)
    self._cache_chao[cache_key] = tile
    return tile


def _v3168_desenhar_chao_vivo(self, superficie):
    _v3168_old_desenhar_chao_vivo(self, superficie)
    pal = _v3168_paleta_chao(self.cenario)
    if pal is None:
        return
    clima = getattr(self, 'clima_tipo', 'limpo')
    noite = max(0.0, min(1.0, getattr(self, 'peso_noite', 0.0)))
    t = self.tempo_animacao * 0.14
    for x in range(0, LARGURA_VIRTUAL, 56):
        off = int(math.sin(t + x * 0.04) * 1)
        pygame.draw.line(superficie, pal['line1'], (x, 739 + off), (x + 14, 739 + off), 1)
        pygame.draw.line(superficie, pal['line2'], (x + 8, 745 - off), (x + 14, 745 - off), 1)
    for x in range(20, LARGURA_VIRTUAL, 88):
        pulso = 1 if math.sin(t * 1.6 + x * 0.05) > 0 else 0
        pygame.draw.rect(superficie, misturar_cores(pal['mid2'], pal['base'], 0.25), (x, 752, 20, 2))
        pygame.draw.line(superficie, pal['accent'], (x + 3, 752 + pulso), (x + 8, 752 + pulso), 1)
        pygame.draw.line(superficie, pal['line2'], (x + 11, 752), (x + 15, 752), 1)
    if self.cenario == 'neve':
        for x in range(15, LARGURA_VIRTUAL, 70):
            pygame.draw.line(superficie, (247, 252, 255), (x, 734), (x + 9, 734), 1)
    elif self.cenario == 'deserto':
        for x in range(10, LARGURA_VIRTUAL, 72):
            pygame.draw.line(superficie, (234, 194, 128), (x, 734), (x + 8, 735), 1)
    elif self.cenario == 'floresta':
        for x in range(10, LARGURA_VIRTUAL, 70):
            pygame.draw.line(superficie, (118, 178, 93), (x, 734), (x + 3, 730), 1)
            pygame.draw.line(superficie, (153, 206, 118), (x + 3, 730), (x + 5, 734), 1)
    elif self.cenario == 'vulcao':
        for x in range(14, LARGURA_VIRTUAL, 68):
            pygame.draw.line(superficie, (255, 149, 71), (x, 734), (x + 5, 734), 1)
            pygame.draw.line(superficie, (255, 214, 118), (x + 1, 735), (x + 4, 735), 1)
    elif self.cenario == 'ilhas_celestes':
        for x in range(12, LARGURA_VIRTUAL, 74):
            pygame.draw.line(superficie, (171, 237, 203), (x, 734), (x + 7, 734), 1)
            pygame.draw.line(superficie, (132, 198, 224), (x + 2, 730), (x + 5, 733), 1)
    elif self.cenario == 'cidade_futurista':
        for x in range(18, LARGURA_VIRTUAL, 96):
            if noite > 0.2:
                pygame.draw.line(superficie, (255, 240, 211), (x, 731), (x + 8, 731), 1)
    if clima in ('chuva', 'tempestade', 'chuva_acida'):
        for x in range(12, LARGURA_VIRTUAL, 70):
            y = 734 + (x % 3)
            pygame.draw.line(superficie, pal['accent'], (x, y), (x + 10, y + 1), 1)
            pygame.draw.line(superficie, pal['line2'], (x + 3, y + 8), (x + 9, y + 8), 1)


ParallaxBackground._obter_tile_chao = _v3168_obter_tile_chao
ParallaxBackground._desenhar_chao_vivo = _v3168_desenhar_chao_vivo



# --- v3.173.0: auditoria de obstáculos por bioma + polimento final global ---
_v3169_old_criar_obstaculo_base_bioma = _criar_obstaculo_base_bioma
_v3169_old_voador_init = ObstaculoVoador.__init__
_v3169_old_desenhar_chao_vivo = ParallaxBackground._desenhar_chao_vivo

_V3169_GROUND_COMPAT = {
    'deserto': ('CACTO',),
    'neve': ('espinho_gelo', 'N3', 'N4'),
    'cidade': ('C1', 'C3', 'C4'),
    'vulcao': ('V1', 'V3', 'V4'),
    'floresta': ('F1', 'F3', 'F4'),
    'cidade_futurista': ('CF1', 'CF3', 'CF4'),
    'ilhas_celestes': ('IC1', 'IC3', 'IC4'),
}
_V3169_VOADOR_ALTURAS = {
    'cidade': (ALTURA_VIRTUAL - 145, ALTURA_VIRTUAL - 188, ALTURA_VIRTUAL - 228),
    'cidade_futurista': (ALTURA_VIRTUAL - 150, ALTURA_VIRTUAL - 192, ALTURA_VIRTUAL - 234),
    'deserto': (ALTURA_VIRTUAL - 154, ALTURA_VIRTUAL - 196, ALTURA_VIRTUAL - 232),
    'neve': (ALTURA_VIRTUAL - 150, ALTURA_VIRTUAL - 192, ALTURA_VIRTUAL - 228),
    'floresta': (ALTURA_VIRTUAL - 156, ALTURA_VIRTUAL - 198, ALTURA_VIRTUAL - 232),
    'vulcao': (ALTURA_VIRTUAL - 160, ALTURA_VIRTUAL - 202, ALTURA_VIRTUAL - 236),
    'ilhas_celestes': (ALTURA_VIRTUAL - 152, ALTURA_VIRTUAL - 194, ALTURA_VIRTUAL - 230),
}
_V3169_GROUND_HUD = {
    'cidade': ((223, 226, 234), (111, 139, 181), (79, 96, 120)),
    'deserto': ((248, 216, 161), (219, 170, 108), (133, 95, 63)),
    'neve': ((248, 253, 255), (205, 232, 246), (122, 155, 192)),
    'floresta': ((185, 225, 144), (122, 177, 95), (60, 88, 51)),
    'vulcao': ((255, 208, 114), (255, 146, 72), (79, 47, 49)),
    'cidade_futurista': ((110, 241, 251), (244, 119, 224), (39, 59, 92)),
    'ilhas_celestes': ((224, 249, 242), (170, 236, 203), (108, 144, 171)),
}

def _v3169_escolher_ameaca_bioma(cenario, agrupado=False):
    opcoes = _V3169_GROUND_COMPAT.get(cenario)
    if not opcoes:
        return None
    if cenario == 'deserto':
        return 'CACTO'
    pref = {
        'neve': ('N4', 'N3') if agrupado else ('N3', 'N4', 'espinho_gelo'),
        'cidade': ('C4', 'C1', 'C3') if agrupado else ('C3', 'C4', 'C1'),
        'vulcao': ('V4', 'V1', 'V3') if agrupado else ('V3', 'V1', 'V4'),
        'floresta': ('F4', 'F1', 'F3') if agrupado else ('F3', 'F1', 'F4'),
        'cidade_futurista': ('CF4', 'CF1', 'CF3') if agrupado else ('CF3', 'CF1', 'CF4'),
        'ilhas_celestes': ('IC4', 'IC1', 'IC3') if agrupado else ('IC3', 'IC1', 'IC4'),
    }
    lista = pref.get(cenario, opcoes)
    return random.choice(lista)


def _criar_obstaculo_base_bioma(x_inicial, cenario, agrupado=False):
    escolha = _v3169_escolher_ameaca_bioma(cenario, agrupado=agrupado)
    if escolha == 'CACTO':
        return ObstaculoTerrestre(x_inicial, qtd_cactos=random.randint(2, 4) if agrupado else 1)
    if escolha == 'espinho_gelo':
        return ObstaculoDeBioma(x_inicial, cenario, 'espinho_gelo')
    if escolha is not None:
        return AmeacaBioma(x_inicial, escolha)
    return _v3169_old_criar_obstaculo_base_bioma(x_inicial, cenario, agrupado=agrupado)


def _v3169_voador_init(self, x_pos, cenario='cidade'):
    _v3169_old_voador_init(self, x_pos, cenario)
    alturas = _V3169_VOADOR_ALTURAS.get(cenario, _V3169_VOADOR_ALTURAS['cidade'])
    self.rect.y = random.choice(alturas)
    self._faixas_altura = alturas


def _v3169_desenhar_chao_vivo(self, superficie):
    _v3169_old_desenhar_chao_vivo(self, superficie)
    pal = _V3169_GROUND_HUD.get(self.cenario)
    if pal is None:
        return
    bright, accent, shadow = pal
    tempo = self.tempo_animacao * 0.12
    # Ombros laterais: ajudam a enquadrar a pista sem poluição no centro.
    for y in range(728, 761, 8):
        pygame.draw.line(superficie, (*shadow, 120) if len(shadow)==4 else shadow, (0, y), (32, y), 1)
        pygame.draw.line(superficie, (*shadow, 120) if len(shadow)==4 else shadow, (LARGURA_VIRTUAL - 33, y), (LARGURA_VIRTUAL - 1, y), 1)
    # Micro marcadores vivos por bioma.
    for x in range(16, LARGURA_VIRTUAL, 92):
        pulso = 1 if math.sin(tempo + x * 0.05) > 0 else 0
        pygame.draw.line(superficie, bright, (x, 734 + pulso), (x + 7, 734 + pulso), 1)
        pygame.draw.line(superficie, accent, (x + 2, 748 - pulso), (x + 6, 748 - pulso), 1)
    # Miolo levemente unificado para destacar obstáculos.
    pygame.draw.line(superficie, misturar_cores(accent, shadow, 0.45), (52, 739), (LARGURA_VIRTUAL - 53, 739), 1)
    pygame.draw.line(superficie, misturar_cores(bright, shadow, 0.62), (68, 751), (LARGURA_VIRTUAL - 69, 751), 1)


ObstaculoVoador.__init__ = _v3169_voador_init
ParallaxBackground._desenhar_chao_vivo = _v3169_desenhar_chao_vivo


# v3.173.0 — pisa no conjunto de overlays móveis redundantes das v166-v169;
# mantém intacto o tile já otimizado e a mecânica de scrolling.
from pixelrush_pista_v3170 import desenhar_pista_legivel as _v3170_pista
ParallaxBackground._desenhar_chao_vivo = _v3170_pista

# v3.193.0 — Plano G: somente limpeza da apresentacao da pista.
from pixelrush_pista_v3193 import instalar_limpeza_pista
instalar_limpeza_pista(ParallaxBackground)

# v3.194.0 — acabamento dos materiais e da face visual do piso; apos v3.193.
from pixelrush_pisos_v3194 import instalar_pisos_premium
instalar_pisos_premium(ParallaxBackground)

# Plano H v3.203: apenas observacao externa, preservando a funcao main original.
_main_v3202 = main
def main():
    return _pro_executar(lambda: _forense_executar(lambda: _rep_executar(_main_v3202, VERSAO, "LIMPA"), VERSAO, "LIMPA"), VERSAO, "LIMPA")

if __name__ == "__main__":
    main()