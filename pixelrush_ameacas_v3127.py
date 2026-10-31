"""Pixel Rush 3.127.0 — 28 ameacas tematicas; sprites refinados, maiores e mais legiveis.

Integracao intencionalmente minima: o jogo continua responsavel por spawn,
colisao, combo, febre, movimento e renderizacao de sprites.
"""
import math
import random
import pygame
import numpy as np

# id: (bioma, nome, largura, altura, movimento)
AMEACAS = {
    'C1': ('cidade', 'Rato Urbano', 49, 30, 'disparada'),
    'C2': ('cidade', 'Pombo Atrapalhado', 54, 42, 'mergulho'),
    'C3': ('cidade', 'Cones de Construcao', 60, 42, 'parado'),
    'C4': ('cidade', 'Cavalete de Obras', 78, 60, 'parado'),
    'N1': ('neve', 'Pinguim Deslizante', 49, 35, 'deslizar'),
    'N2': ('neve', 'Coruja Invernal', 58, 46, 'ondular'),
    'N3': ('neve', 'Bloco de Gelo Rachado', 54, 54, 'parado'),
    'N4': ('neve', 'Tronco Nevado', 74, 38, 'parado'),
    'D1': ('deserto', 'Serpente das Dunas', 60, 39, 'serpente'),
    'D2': ('deserto', 'Besouro Rolador', 58, 39, 'rolar'),
    'D3': ('deserto', 'Coluna de Ruinas', 46, 64, 'parado'),
    'D4': ('deserto', 'Ossada Ancestral', 82, 47, 'parado'),
    'V1': ('vulcao', 'Salamandra Magmatica', 60, 36, 'saltar'),
    'V2': ('vulcao', 'Morcego Vulcanico', 64, 44, 'ondular'),
    'V3': ('vulcao', 'Rocha de Obsidiana', 56, 54, 'parado'),
    'V4': ('vulcao', 'Geiser de Vapor', 58, 74, 'geiser'),
    'F1': ('floresta', 'Caracol Blindado', 56, 42, 'lento'),
    'F2': ('floresta', 'Tucano Travesso', 58, 46, 'mergulho'),
    'F3': ('floresta', 'Tronco Oco', 76, 47, 'parado'),
    'F4': ('floresta', 'Galho Suspenso', 80, 34, 'parado_alto'),
    'CF1': ('cidade_futurista', 'Robo Patrulheiro', 57, 50, 'patrulhar'),
    'CF2': ('cidade_futurista', 'Drone Sentinela', 62, 40, 'ondular'),
    'CF3': ('cidade_futurista', 'Caixa Tecnologica', 56, 52, 'parado'),
    'CF4': ('cidade_futurista', 'Cabos Energizados', 86, 31, 'parado_alto'),
    'IC1': ('ilhas_celestes', 'Besouro Luminoso', 56, 42, 'saltar'),
    'IC2': ('ilhas_celestes', 'Arraia Celestial', 69, 40, 'ondular'),
    'IC3': ('ilhas_celestes', 'Cristal Gigante', 54, 66, 'parado'),
    'IC4': ('ilhas_celestes', 'Arco de Pedra', 86, 36, 'parado_alto'),
}
POR_BIOMA = {bioma: tuple(c for c,v in AMEACAS.items() if v[0] == bioma)
             for bioma in ('cidade','neve','deserto','vulcao','floresta','cidade_futurista','ilhas_celestes')}
_CACHE = {}
AMEACAS_AEREAS = {'C2', 'N2', 'V2', 'F2', 'IC2', 'CF2'}
AMEACAS_ALTAS = {'F4', 'CF4', 'IC4'}
AJUSTE_BASE = {'C3': 4, 'C4': 2, 'N3': 2, 'D3': 1, 'CF3': 2, 'V3': 1, 'IC3': 1, 'D4': 1, 'F3': 1}
_CONTORNO = (17, 22, 31, 255)


def _aplicar_contorno(img, cor=_CONTORNO):
    mascara = pygame.mask.from_surface(img)
    base = mascara.to_surface(setcolor=cor, unsetcolor=(0, 0, 0, 0)).convert_alpha()
    saida = pygame.Surface(img.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
        saida.blit(base, (dx, dy))
    saida.blit(img, (0, 0))
    return saida


def _aplicar_toque_final(img, codigo):
    img = _aplicar_contorno(img)
    w, h = img.get_size()
    if codigo not in AMEACAS_AEREAS and codigo not in AMEACAS_ALTAS:
        pygame.draw.ellipse(img, (0, 0, 0, 52), (max(2, w//8), h - 7, max(10, int(w * 0.64)), 5))
    # brilho leve para integrar melhor com os novos biomas.
    if codigo.startswith('CF'):
        pygame.draw.rect(img, (74, 235, 244, 80), (2, 2, w - 4, 3))
    elif codigo.startswith('IC'):
        pygame.draw.ellipse(img, (190, 248, 246, 55), (4, 4, w - 8, max(6, h // 4)))
    elif codigo.startswith('V'):
        pygame.draw.rect(img, (255, 157, 84, 48), (6, 4, max(6, w - 12), 3))
    elif codigo.startswith('F'):
        pygame.draw.rect(img, (201, 231, 136, 36), (6, 6, max(6, w - 12), 2))
    return img


def _pintar(codigo, fase):
    """Desenha pixel art uma vez por fase — sem transformacoes por tick."""
    img = pygame.Surface((64,64), pygame.SRCALPHA)
    q = lambda color, xywh: pygame.draw.rect(img, color, xywh)
    e = lambda color, xywh: pygame.draw.ellipse(img, color, xywh)
    c = lambda color, center, radius: pygame.draw.circle(img, color, center, radius)
    l = lambda color, a, b, w=2: pygame.draw.line(img, color, a, b, w)
    p = lambda color, vertices: pygame.draw.polygon(img, color, vertices)
    esc = (38,43,62); olho=(19,29,40); branco=(255,251,232)
    # Poses animadas são visuais; usam deslocamentos pequenos.
    bat = ((-4,0,4)[fase]); asa = ((8,3,-2)[fase]); passo=((0,3,-1)[fase])
    if codigo == 'C1':
        l((188,144,147),(13,45),(3,38),3); l((188,144,147),(3,38),(6,31),2)
        e((94,103,114),(10,29,44,24));e((158,162,173),(29,31,26,19))
        c((140,135,151),(40,29),10);c((140,135,151),(24,29),8)
        c((228,169,181),(40,29),5);q(olho,(49,36,3,3));c((244,147,155),(57,42),4)
        l(esc,(19,52),(18+passo,59),3);l(esc,(43,51),(43-passo,59),3)
    elif codigo in ('C2','N2','V2','F2','IC2'):
        corpo={'C2':(157,171,204),'N2':(227,234,243),'V2':(113,64,94),'F2':(42,78,87),'IC2':(93,184,205)}[codigo]
        asa_cor={'C2':(111,135,191),'N2':(172,188,208),'V2':(206,91,77),'F2':(47,156,129),'IC2':(103,227,221)}[codigo]
        if codigo == 'V2':
            p(asa_cor,[(31,37),(6,8+asa),(7,35),(14,28),(20,42)])
            p(asa_cor,[(33,37),(59,10+asa),(58,35),(51,30),(46,42)])
            e(corpo,(21,23,24,26));p((238,132,91),[(22,24),(27,12),(31,22)])
            p((238,132,91),[(36,24),(42,11),(46,28)])
            c((255,210,105),(28,33),3);c((255,210,105),(39,33),3)
        elif codigo == 'IC2':
            p(asa_cor,[(32,25),(3,16+asa//3),(19,45),(31,42),(48,45),(61,16+asa//3)])
            e(corpo,(21,19,25,26));p((134,112,220),[(33,27),(31,58),(37,42)])
            c((236,250,255),(27,29),3);c((236,250,255),(40,29),3)
            l((173,255,245),(18,37),(7,42),2);l((173,255,245),(47,37),(56,42),2)
        else:
            p(asa_cor,[(29,33),(7,12+asa),(4,37),(17,44),(31,40)])
            p(asa_cor,[(35,33),(57,11+asa),(62,38),(48,44),(33,40)])
            e(corpo,(20,25,28,25))
            c(corpo,(40,28),11)
            if codigo=='N2':
                p(corpo,[(26,24),(23,10),(35,18)]);p(corpo,[(39,20),(50,10),(48,29)])
                e((250,225,178),(23,28,24,14));c((49,70,89),(30,29),3);c((49,70,89),(42,29),3)
                p((221,163,71),[(40,35),(50,38),(40,41)])
            elif codigo=='F2':
                p((248,187,55),[(39,26),(62,31),(46,39)])
                e((254,203,97),(20,31,24,12));c(branco,(38,28),4);c(olho,(39,28),2)
            else:
                p((238,183,103),[(41,34),(60,37),(43,41)]);e((215,227,246),(23,29,16,9));c(olho,(42,29),2)
        l(esc,(29,49),(31,54),2)
    elif codigo == 'C3':
        for dx in (0,22):
            x=5+dx; p((227,112,58),[(x+4,60),(x+12,11),(x+21,60)])
            p((255,235,176),[(x+9,34),(x+15,34),(x+18,42),(x+7,42)])
            q((66,72,92),(x,58,28,5));q((255,190,103),(x+4,49,18,4))
            q((255,140,79),(x+7,24,10,3))
        pygame.draw.ellipse(img, (0,0,0,32), (10,58,44,4))
    elif codigo == 'C4':
        q((233,164,72),(9,17,48,8));q((240,199,121),(12,18,42,4))
        q((69,76,91),(6,13,55,5));l((139,146,155),(12,22),(10,60),5);l((139,146,155),(52,22),(55,60),5)
        q((47,53,68),(8,58,50,3))
        for x in (15,33,51):p((206,105,71),[(x,19),(x+7,19),(x+2,25),(x-5,25)])
    elif codigo == 'N1':
        e((57,81,108),(10,20,37,39));e((242,248,255),(20,29,22,30))
        c((66,87,109),(30,21),13);c((250,249,239),(35,24),7)
        p((237,171,82),[(41,29),(57,35),(42,38)])
        q((248,170,80),(18,56,11,4));q((248,170,80),(35,56,11,4))
        c(olho,(39,24),2)
    elif codigo == 'N3':
        p((85,148,182),[(8,56),(11,16),(20,7),(54,9),(56,53),(43,60)])
        p((152,220,240),[(12,54),(14,17),(20,12),(29,16),(25,53)])
        p((205,246,255),[(31,14),(52,12),(51,42),(39,34)])
        l((80,132,171),(35,19),(29,34),3);l((80,132,171),(29,34),(38,46),2)
        l(branco,(16,21),(21,17),2)
    elif codigo in ('N4','F3'):
        cor=(93,71,61) if codigo=='F3' else (129,93,71)
        q(cor,(7,29,51,26));e((64,50,48),(44,24,17,34));e((176,135,103),(47,29,10,21))
        e((47,36,33),(50,32,6,15));l((57,48,38),(10,41),(41,41),4)
        if codigo=='N4':
            p((225,244,253),[(5,31),(15,19),(29,22),(40,18),(60,30),(56,36),(41,27),(24,30),(11,35)])
            q(branco,(13,26,8,4));q(branco,(35,23,8,4))
        else:
            q((77,145,77),(8,23,13,7));q((128,183,89),(25,22,19,5));q((56,113,65),(47,21,8,5))
            c((242,163,194),(24,23),3)
    elif codigo == 'D1':
        for x,y in ((15,43),(27,40),(39,43)):
            e((132,166,101),(x,y,19,11))
            l((77,95,76),(x+4,y+4),(x+10,y+5),2)
        l((135,164,94),(44,45),(47,23),8);e((135,164,94),(39,18,19,16))
        c(olho,(51,25),3);p((219,137,120),[(57,31),(63,35),(56,34)])
        l((119,67,74),(61,35),(62,41),2)
    elif codigo == 'D2':
        c((175,133,75),(18,37),16);c((227,187,117),(14,31),11)
        l((131,89,59),(7,34),(25,43),2);e((67,114,109),(30,26,26,24));
        l((42,74,78),(35,29),(47,47),2);c((243,224,134),(45,33),3)
        for x in (30,39,49):l((77,89,66),(x,45),(x-4+passo,56),3)
    elif codigo == 'D3':
        q((130,86,60),(13,10,40,50));q((201,150,95),(17,12,32,42))
        q((235,196,125),(7,7,52,10));q((151,102,68),(8,55,48,7))
        q((174,124,83),(24,22,5,24));q((174,124,83),(37,22,5,24))
        l((105,69,54),(35,16),(29,29),2);l((105,69,54),(29,29),(34,36),2)
    elif codigo=='D4':
        l((233,213,169),(8,55),(52,48),6)
        for x,tip in ((14,21),(25,14),(36,17),(47,24)):
            l((233,213,169),(x,50),(x,tip),5);l((201,173,131),(x,tip),(x+7,34),3)
        c((230,210,178),(10,54),5)
    elif codigo=='V1':
        p((93,56,68),[(7,48),(25,31),(50,32),(59,48),(40,55),(19,53)])
        p((233,105,65),[(13,47),(25,35),(51,37),(51,46)])
        for x in (21,33,43):p((255,179,75),[(x,32),(x+3,24+passo),(x+7,36)])
        c((255,232,139),(51,37),3);l((83,51,54),(19,52),(16+passo,60),4)
        l((83,51,54),(45,52),(49-passo,60),4)
    elif codigo=='V3':
        p((50,39,57),[(6,56),(12,25),(25,12),(34,23),(45,6),(56,38),(58,58)])
        p((89,64,92),[(14,50),(25,20),(32,29),(23,55)])
        l((242,89,51),(43,16),(39,33),4);l((255,172,65),(39,33),(47,54),4)
        l((250,108,57),(20,44),(27,57),3)
    elif codigo=='V4':
        # 1/3 do ciclo apenas fresta, 2/3 coluna de vapor com aviso.
        e((73,58,66),(4,50,56,12));e((243,110,49),(18,52,28,5))
        if fase == 0:
            c((255,176,67),(32,50),5)
        else:
            largura=(22 if fase==1 else 28)
            p((185,199,209),[(32-largura//2,55),(21,40),(26,23),(20,12),(31,4),(43,17),(39,30),(48,49),(32+largura//2,54)])
            p((232,240,238),[(25,54),(28,36),(26,25),(33,12),(38,26),(34,38),(42,54)])
    elif codigo=='F1':
        l((95,138,93),(42,37),(53,29),6);c((124,177,103),(52,26),9)
        e((142,107,132),(12,19,39,38));e((185,151,176),(16,24,30,26));
        e((82,64,99),(21,28,20,18));c((222,187,203),(29,34),6);c((111,83,139),(29,34),3)
        e((116,183,112),(8,44,49,15));c(olho,(57,27),2)
    elif codigo=='F4':
        # Ramo inteiramente preso ao topo da copa do cenario.
        q((75,54,39),(0,10,64,18));q((111,78,51),(0,8,60,9));
        for x in (12,32,50):
            p((58,126,73),[(x,17),(x-8,35),(x+6,25)])
        l((103,163,96),(4,21),(59,21),2)
    elif codigo=='CF1':
        q((53,68,100),(14,21,40,33));q((101,153,192),(18,15,32,34))
        q((51,60,88),(10,49,46,8));c((42,42,62),(20,55),7);c((42,42,62),(47,55),7)
        q((132,255,238),(22,25,25,8));q((34,47,67),(27,29,4,3));q((34,47,67),(41,29,4,3))
        l((121,199,225),(35,15),(35,6),2);c((255,127,163),(35,6),4)
    elif codigo=='CF2':
        p((73,83,124),[(10,34),(25,18),(43,18),(58,34),(40,51),(24,48)])
        q((113,166,212),(20,21,29,25));q((91,235,239),(22,29,24,8))
        c((243,139,222),(34,33),5);l((122,159,220),(9,33),(2,25+passo),4)
        l((122,159,220),(56,33),(62,25+passo),4)
    elif codigo=='CF3':
        q((43,55,79),(9,9,48,49));q((95,113,145),(12,11,42,43));
        q((66,82,104),(17,16,30,33));q((70,239,247),(14,18,5,33));q((70,239,247),(45,18,5,33))
        q((224,94,194),(26,28,13,9));q((45,61,87),(28,30,9,5))
        for x in (12,52):q((33,43,63),(x,52,5,9))
    elif codigo=='CF4':
        q((42,51,81),(2,7,60,13));q((94,212,244),(2,16,60,5));
        for x in range(8,60,12):
            l((202,87,233),(x,19),(x+4,37),3);l((69,221,249),(x+4,37),(x+9,18),2)
        q((56,70,95),(0,4,8,25));q((56,70,95),(56,4,8,25))
    elif codigo=='IC1':
        e((80,165,160),(12,27,42,29));e((113,236,195),(19,31,30,17))
        p((166,124,232),[(18,34),(10,16+asa),(29,27)])
        p((119,174,249),[(36,27),(53,14+asa),(49,36)])
        for x in (17,29,42):c((230,252,166),(x,35),3)
        c(olho,(51,40),3);l((62,144,137),(19,50),(17+passo,59),3)
    elif codigo=='IC3':
        p((52,93,137),[(6,57),(19,22),(34,13),(55,56)])
        p((85,214,239),[(14,51),(27,14),(35,6),(43,40),(35,56)])
        p((188,245,251),[(27,14),(35,6),(35,47)])
        p((128,91,214),[(41,55),(53,22),(61,49),(57,57)])
        l(branco,(24,27),(27,17),2)
    elif codigo=='IC4':
        # Arco preso ao teto da ilha, obstaculo obrigatoriamente alto.
        q((89,101,138),(0,0,64,12));q((126,145,174),(4,4,56,7));
        q((99,116,143),(6,10,13,46));q((99,116,143),(46,10,13,46));
        q((55,70,104),(20,12,25,11));q((112,172,159),(0,9,10,4));
        for x in (13,52):q((123,222,154),(x,14,3,6))
    # Unifica acabamento pixelado e contraste sem nenhuma operacao por frame.
    return img





# Materiais e microtexturas V3.127: executados apenas na construção dos 84 frames.
# A silhueta externa de cada sprite é mantida pixel a pixel; hitboxes intactas.
_MATERIAL_POR_TIPO = {
 'C1':'pelagem','C2':'penas','C3':'sinal','C4':'metal',
 'N1':'pelagem','N2':'penas','N3':'gelo','N4':'madeira',
 'D1':'escamas','D2':'casco','D3':'pedra','D4':'osso',
 'V1':'lava','V2':'asas','V3':'obsidiana','V4':'vapor',
 'F1':'casco','F2':'penas','F3':'madeira','F4':'madeira',
 'CF1':'metal','CF2':'metal','CF3':'metal','CF4':'energia',
 'IC1':'casco','IC2':'asas','IC3':'cristal','IC4':'pedra',
}
_PALETAS_MATERIAL = {
 # destaque/sombra/preenchimento (o terceiro é frequência para granulação discreta)
 'pelagem':((220,190,176),(56,54,78),7),
 'penas':((245,229,193),(71,90,121),8),
 'escamas':((207,208,129),(76,107,81),7),
 'casco':((250,207,140),(61,76,92),6),
 'madeira':((227,184,140),(65,49,57),8),
 'pedra':((243,202,145),(96,68,75),9),
 'osso':((255,245,214),(134,105,96),10),
 'gelo':((252,253,255),(77,151,202),7),
 'obsidiana':((164,155,218),(46,29,60),9),
 'lava':((255,225,102),(84,40,56),6),
 'vapor':((252,253,255),(112,128,154),10),
 'asas':((251,179,170),(54,47,102),8),
 'cristal':((238,254,255),(71,112,186),10),
 'sinal':((255,247,185),(83,65,74),10),
 'metal':((221,239,253),(53,57,93),9),
 'energia':((251,207,255),(57,43,119),7),
}


def _detalhar_ameaca(img, codigo, fase):
    """Aprofunda pixels por material sem alterar a área opaca de nenhuma pose.

    Padrões determinísticos de textura e relevo reforçam identidades (escamas,
    veios, placas, penas), mantendo olho/bico/alertas existentes intactos.
    """
    mat = _MATERIAL_POR_TIPO[codigo]
    clear, shade, grid = _PALETAS_MATERIAL[mat]
    rgb = pygame.surfarray.pixels3d(img)
    alpha = pygame.surfarray.pixels_alpha(img)
    data = rgb.astype(np.int16)
    x = np.arange(img.get_width(), dtype=np.int16)[:, None]
    y = np.arange(img.get_height(), dtype=np.int16)[None, :]
    hi = np.max(data, axis=2)
    lo = np.min(data, axis=2)
    eligible = (alpha > 0) & (hi > 62) & (hi < 230) & ((hi-lo) > 12)
    if mat in ('pelagem','penas','escamas','casco','asas'):
        detail = ((x*3 + y*5 + (x//grid)*7) % (grid*3 + 11) < 3)
        shadow = ((x//7 + y//5 + x//13) % 6 == 0)
    elif mat in ('gelo','cristal','obsidiana'):
        detail = ((x*2 - y + sum(ord(c) for c in codigo) % 11) % (grid*3+8) == 0)
        shadow = ((x+y//2)%17 == 2)
    elif mat in ('madeira','osso'):
        detail = ((y//2 + (x//9)*3)%11==0)
        shadow = ((x+y*2)%23 == 0)
    else:
        detail = ((x//5 + y//grid*3) % 8 == 1)
        shadow = ((x*5 + y*3) % 31 == 0)
    lightpix = eligible & detail
    darkpix = eligible & shadow & ~lightpix
    if np.any(lightpix):
        data[lightpix] = (data[lightpix]*3 + np.asarray(clear, dtype=np.int16))//4
    if np.any(darkpix):
        data[darkpix] = (data[darkpix]*4 + np.asarray(shade, dtype=np.int16))//5
    # iluminação em pixels ao redor dos limites OPACOS internos.
    opaque = alpha > 0
    above = np.zeros_like(opaque)
    above[:,1:] = opaque[:,:-1]
    left = np.zeros_like(opaque)
    left[1:,:] = opaque[:-1,:]
    below = np.zeros_like(opaque)
    below[:,:-1] = opaque[:,1:]
    topr = eligible & ((~above)|(~left))
    botr = eligible & (~below) & ~topr
    data[topr] = np.minimum(255, data[topr]+15)
    data[botr] = np.maximum(0, data[botr]-14)
    rgb[opaque] = np.clip(data[opaque],0,255).astype(np.uint8)
    del rgb, alpha

    # Detalhes identificadores em posições existentes dentro da silhueta.
    # O 'overlay' nunca altera a transparência do desenho original.
    ov = pygame.Surface(img.get_size(),pygame.SRCALPHA)
    line = pygame.draw.line
    rect = pygame.draw.rect
    circ = pygame.draw.circle
    if codigo in ('C1','N1'):
        for n in range(3):
            line(ov,(250,225,182,140),(18+n*8,37+n%2*3),(23+n*8,36+n%2*3),2)
    elif codigo in ('C2','N2','F2'):
        for off in (0,7,14):
            line(ov,(254,241,206,140),(12+off,24),(19+off,31),1)
            line(ov,(70,109,166,125),(50-off,23),(48-off,30),1)
    elif codigo in ('D1',):
        for off in range(15,49,8):
            rect(ov,(230,216,137,160),(off,43,4,2))
    elif codigo in ('D2','F1','IC1'):
        for off in (18,27,36):
            line(ov,(246,219,171,145),(off,28),(off-2,37),1)
    elif codigo in ('V1','V2'):
        for off in (18,29,42):
            line(ov,(255,210,104,175),(off,42),(off+3,39),2)
    elif codigo in ('CF1','CF2','CF3','CF4'):
        for off in (0,12,24):
            rect(ov,(141,246,249,155),(20+off,35,5,2))
            rect(ov,(42,67,98,160),(20+off,39,5,1))
    elif codigo in ('IC2',):
        for off in (0,9,18):
            line(ov,(229,248,253,155),(17+off,29),(20+off,35),1)
    elif mat in ('gelo','cristal','obsidiana'):
        for sx,sy in ((23,24),(33,39),(45,26)):
            line(ov,(246,252,255,175),(sx,sy),(sx+3,sy-6),1)
            line(ov,(92,137,194,155),(sx+2,sy+1),(sx+6,sy+3),1)
    elif mat in ('madeira','pedra','osso'):
        for sx,sy in ((15,32),(30,40),(43,29)):
            line(ov,(246,209,159,155),(sx,sy),(sx+7,sy+1),1)
            rect(ov,(83,62,71,120),(sx+2,sy+3,4,1))
    else:
        for sx in (18,32,45):
            rect(ov,(255,239,174,130),(sx,32,5,2))
    paint = pygame.surfarray.pixels3d(ov)
    paint_alpha = pygame.surfarray.pixels_alpha(ov)
    dst = pygame.surfarray.pixels3d(img)
    dst_alpha = pygame.surfarray.pixels_alpha(img)
    # blend sob máscara; nunca modifica alpha/colisão.
    affected = (paint_alpha>0)&(dst_alpha>0)
    if np.any(affected):
        mix=paint_alpha[affected].astype(np.int16)[:,None]
        dst[affected] = ((dst[affected].astype(np.int16)*(255-mix)+paint[affected].astype(np.int16)*mix)//255).astype(np.uint8)
    del dst, dst_alpha, paint, paint_alpha
    return img


def _reforcar_cores_sem_mudar_silhueta(img):
    """Contraste e saturacao calculados uma vez com NumPy vetorizado.

    Preserve alfa, formas e pixels transparentes. A vetorizacao evita uma
    iteracao Python por pixel no primeiro spawn (importante no Android).
    """
    rgb = pygame.surfarray.pixels3d(img)
    alpha = pygame.surfarray.pixels_alpha(img)
    valores = rgb.astype(np.float32)
    alto = np.max(valores, axis=2)
    baixo = np.min(valores, axis=2)
    meio = (alto + baixo) * .5
    alvo = 23.0 + (meio / 255.0) * 215.0 + (meio - 128.0) * .065
    fator = np.where((alto - baixo) >= 26.0, 1.19, 1.11)
    novo = np.clip(alvo[:, :, None] +
                   (valores - meio[:, :, None]) * fator[:, :, None], 0, 255)
    opacos = alpha > 0
    rgb[opacos] = novo[opacos].astype(np.uint8)
    del rgb, alpha
    return img


def _sinalizar_perigo(img, codigo, fase):
    """Acento âmbar APENAS dentro da silhueta opaca do sprite.

    Nenhum pixel transparente vira perigo: evita marcas flutuando e preserva
    a area visual/colidivel da pintura original.
    """
    w, h = img.get_size()
    mascara = pygame.mask.from_surface(img, 120)
    movimento = AMEACAS[codigo][4]
    if codigo in AMEACAS_AEREAS:
        alvo_y = h // 2
    elif codigo in AMEACAS_ALTAS:
        alvo_y = max(2, h // 5)
    elif movimento == 'parado':
        alvo_y = max(2, h // 4)
    else:
        alvo_y = h // 2
    # Busca ate 8 pixels na vertical uma faixa util ja preenchida.
    melhor = None
    for desvio in (0, -2, 2, -4, 4, -6, 6, 8):
        y = max(0, min(h-1, alvo_y + desvio))
        colunas = [x for x in range(max(2, w//2-10), min(w-2, w//2+11))
                   if mascara.get_at((x, y))]
        if len(colunas) >= 5:
            melhor = (y, colunas)
            break
    if melhor is not None:
        y, colunas = melhor
        centra = colunas[len(colunas)//2]
        for x in range(max(0, centra-4), min(w, centra+5)):
            if mascara.get_at((x, y)):
                img.set_at((x, y), (255, 218, 95, img.get_at((x, y)).a))
    return img


def imagem_ameaca(codigo, fase=0):
    chave=(codigo,fase)
    imagem=_CACHE.get(chave)
    if imagem is None:
        _,_,w,h,_=AMEACAS[codigo]
        imagem=pygame.transform.scale(_detalhar_ameaca(_pintar(codigo,fase),codigo,fase),(w,h)).convert_alpha()
        imagem = _reforcar_cores_sem_mudar_silhueta(imagem)
        imagem = _sinalizar_perigo(imagem, codigo, fase)
        imagem = _aplicar_toque_final(imagem, codigo)
        if codigo == 'C2':
            imagem = pygame.transform.flip(imagem, True, False)
        _CACHE[chave]=imagem
    return imagem


class AmeacaBioma(pygame.sprite.Sprite):
    """Inimigo/obstaculo padrao: participa dos mesmos grupos e regras do jogo."""
    def __init__(self,x,codigo):
        super().__init__()
        bioma,nome,w,h,mov=AMEACAS[codigo]
        self.tipo='novo_'+codigo
        self.codigo=codigo
        self.bioma=bioma
        self.nome=nome
        self.movimento=mov
        self.qtd_cactos=0
        self.image=imagem_ameaca(codigo,0)
        self.rect=self.image.get_rect()
        self.rect.left=int(x)
        self._x=float(x)
        self.chao=730
        self._ajuste_base = AJUSTE_BASE.get(codigo, 0)
        if mov=='parado_alto':
            self.rect.bottom=688
        elif mov in ('mergulho','ondular'):
            self.rect.bottom=691 if codigo not in ('IC2','V2') else 694
        else:
            self.rect.bottom=self.chao + self._ajuste_base
        self._base_y=self.rect.top
        self.ticks=0
        self._fase=0
        self._hitboxes_precisas_v342=(pygame.Rect(max(4, w//8), max(4, h//9), max(8, w - max(8, w//4)), max(8, h - max(7, h//5))),)
        self._colisao_ativa=(mov!='geiser')
        self._giro=random.randint(0,29)

    def update(self,velocidade_jogo):
        self.ticks+=1
        mov=self.movimento
        extra={'disparada':(2.0 if self.ticks%115<31 else 0.15),
               'deslizar':0.7,'rolar':1.15,'patrulhar':0.5,'lento':-1.8}.get(mov,0)
        self._x-=max(0.1,float(velocidade_jogo)+extra)
        self.rect.left=int(self._x)
        if mov in ('ondular','mergulho'):
            # O mergulho é discreto e só acontece depois de visivel.
            ampl=8 if mov=='ondular' else 11
            if mov=='mergulho':
                ciclo=self.ticks%120
                delta=0 if ciclo<38 else max(0,math.sin((ciclo-38)/82.0*math.pi))*ampl
            else:
                delta=math.sin(self.ticks*0.075+self._giro)*ampl
            self.rect.top=self._base_y+round(delta)
        elif mov=='saltar':
            ciclo=(self.ticks+self._giro)%100
            altura=17*math.sin(math.pi*(ciclo-60)/39) if ciclo>=60 else 0
            self.rect.top=self._base_y-round(max(0,altura))
        elif mov=='serpente':
            # Aviso com cabeca baixa antes do bote. Corpo permanece visivel.
            self.rect.top=self._base_y-round(3+4*max(0,math.sin(self.ticks*0.08)))
        elif mov=='geiser':
            # Antes de a coluna surgir, há rachadura laranja visivel no chão.
            ciclo=self.ticks%116
            fase=0 if ciclo<38 else 1 if ciclo<79 else 2
            self._colisao_ativa=fase!=0
            if fase!=self._fase:
                self._fase=fase
                self.image=imagem_ameaca(self.codigo,fase)
        if mov!='geiser' and mov not in ('parado','parado_alto'):
            indice=(self.ticks//9)%3
            if indice!=self._fase:
                self._fase=indice
                self.image=imagem_ameaca(self.codigo,indice)
        if self.rect.right < -90:
            self.kill()


def risco_colisao_ativo(obs):
    return getattr(obs,'_colisao_ativa',True)
