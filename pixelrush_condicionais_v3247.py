# -*- coding: utf-8 -*-
"""v3.247.0 — apresentação de estados condicionais de portais, chefes e marcos.
Sem modificar identificadores, RNG, salvamentos, regras ou entrada.
"""
from functools import lru_cache
import re
IDIOMAS = ('es_ES', 'ja_JP', 'fr_FR', 'de_DE', 'it_IT', 'tr_TR', 'pt_PT', 'hi_IN', 'zh_CN', 'ko_KR', 'ru_RU')
TITULOS = {'GRAVIDADE INVERTIDA': {'es_ES': 'GRAVEDAD INVERTIDA', 'ja_JP': '反転重力', 'fr_FR': 'GRAVITÉ INVERSÉE', 'de_DE': 'UMGEKEHRTE SCHWERKRAFT', 'it_IT': 'GRAVITÀ INVERTITA', 'tr_TR': 'TERS YERÇEKİMİ', 'pt_PT': 'GRAVIDADE INVERTIDA', 'hi_IN': 'उल्टा गुरुत्वाकर्षण', 'zh_CN': '反向重力', 'ko_KR': '역중력', 'ru_RU': 'ОБРАТНАЯ ГРАВИТАЦИЯ'}, 'DESAFIO FLAPPY': {'es_ES': 'RETO FLAPPY', 'ja_JP': 'フラッピーチャレンジ', 'fr_FR': 'DÉFI FLAPPY', 'de_DE': 'FLAPPY-HERAUSFORDERUNG', 'it_IT': 'SFIDA FLAPPY', 'tr_TR': 'FLAPPY GÖREVİ', 'pt_PT': 'DESAFIO FLAPPY', 'hi_IN': 'फ्लैपी चुनौती', 'zh_CN': '飞跃挑战', 'ko_KR': '플래피 도전', 'ru_RU': 'ИСПЫТАНИЕ FLAPPY'}, 'TÚNEL DE PRECISÃO': {'es_ES': 'TÚNEL DE PRECISIÓN', 'ja_JP': '精密トンネル', 'fr_FR': 'TUNNEL DE PRÉCISION', 'de_DE': 'PRÄZISIONSTUNNEL', 'it_IT': 'TUNNEL DI PRECISIONE', 'tr_TR': 'HASSAS TÜNEL', 'pt_PT': 'TÚNEL DE PRECISÃO', 'hi_IN': 'सटीक सुरंग', 'zh_CN': '精准隧道', 'ko_KR': '정밀 터널', 'ru_RU': 'ТОЧНЫЙ ТОННЕЛЬ'}, 'ABISMO AQUÁTICO': {'es_ES': 'ABISMO ACUÁTICO', 'ja_JP': '水の深淵', 'fr_FR': 'ABÎME AQUATIQUE', 'de_DE': 'WASSERABGRUND', 'it_IT': 'ABISSO ACQUATICO', 'tr_TR': 'SU UÇURUMU', 'pt_PT': 'ABISMO AQUÁTICO', 'hi_IN': 'जलमय खाई', 'zh_CN': '水之深渊', 'ko_KR': '수중 심연', 'ru_RU': 'ВОДНАЯ БЕЗДНА'}, 'FUGA DOS LASERS': {'es_ES': 'HUÍDA DE LÁSERES', 'ja_JP': 'レーザーからの脱出', 'fr_FR': 'FUITE DES LASERS', 'de_DE': 'LASERFLUCHT', 'it_IT': 'FUGA DAI LASER', 'tr_TR': 'LAZERLERDEN KAÇIŞ', 'pt_PT': 'FUGA DOS LASERS', 'hi_IN': 'लेज़र से बचाव', 'zh_CN': '激光逃脱', 'ko_KR': '레이저 탈출', 'ru_RU': 'ПОБЕГ ОТ ЛАЗЕРОВ'}, 'PORTAL DO TESOURO': {'es_ES': 'PORTAL DEL TESORO', 'ja_JP': '宝のポータル', 'fr_FR': 'PORTAIL DU TRÉSOR', 'de_DE': 'SCHATZPORTAL', 'it_IT': 'PORTALE DEL TESORO', 'tr_TR': 'HAZİNE PORTALI', 'pt_PT': 'PORTAL DO TESOURO', 'hi_IN': 'खज़ाने का द्वार', 'zh_CN': '宝藏传送门', 'ko_KR': '보물 포털', 'ru_RU': 'ПОРТАЛ СОКРОВИЩ'}, 'PORTAL DE REFLEXOS': {'es_ES': 'PORTAL DE REFLEJOS', 'ja_JP': '反射神経ポータル', 'fr_FR': 'PORTAIL DES RÉFLEXES', 'de_DE': 'REFLEXPORTAL', 'it_IT': 'PORTALE DEI RIFLESSI', 'tr_TR': 'REFLEKS PORTALI', 'pt_PT': 'PORTAL DE REFLEXOS', 'hi_IN': 'प्रतिक्रिया द्वार', 'zh_CN': '反应传送门', 'ko_KR': '반사 신경 포털', 'ru_RU': 'ПОРТАЛ РЕФЛЕКСОВ'}, 'FASE BÔNUS': {'es_ES': 'FASE EXTRA', 'ja_JP': 'ボーナスステージ', 'fr_FR': 'NIVEAU BONUS', 'de_DE': 'BONUSLEVEL', 'it_IT': 'LIVELLO BONUS', 'tr_TR': 'BONUS BÖLÜM', 'pt_PT': 'FASE BÓNUS', 'hi_IN': 'बोनस स्तर', 'zh_CN': '奖励关卡', 'ko_KR': '보너스 스테이지', 'ru_RU': 'БОНУСНЫЙ УРОВЕНЬ'}, 'SENTINELA URBANA': {'es_ES': 'CENTINELA URBANO', 'ja_JP': '都市の番人', 'fr_FR': 'SENTINELLE URBAINE', 'de_DE': 'STADTWÄCHTER', 'it_IT': 'SENTINELLA URBANA', 'tr_TR': 'ŞEHİR NÖBETÇİSİ', 'pt_PT': 'SENTINELA URBANA', 'hi_IN': 'शहरी प्रहरी', 'zh_CN': '都市哨兵', 'ko_KR': '도시 파수꾼', 'ru_RU': 'ГОРОДСКОЙ СТРАЖ'}, 'ESCORPIÃO MECÂNICO': {'es_ES': 'ESCORPIÓN MECÁNICO', 'ja_JP': '機械サソリ', 'fr_FR': 'SCORPION MÉCANIQUE', 'de_DE': 'MECHANISCHER SKORPION', 'it_IT': 'SCORPIONE MECCANICO', 'tr_TR': 'MEKANİK AKREP', 'pt_PT': 'ESCORPIÃO MECÂNICO', 'hi_IN': 'यांत्रिक बिच्छू', 'zh_CN': '机械蝎子', 'ko_KR': '기계 전갈', 'ru_RU': 'МЕХАНИЧЕСКИЙ СКОРПИОН'}, 'TITÃ GLACIAL': {'es_ES': 'TITÁN GLACIAL', 'ja_JP': '氷河の巨人', 'fr_FR': 'TITAN GLACIAL', 'de_DE': 'EISTITAN', 'it_IT': 'TITANO GLACIALE', 'tr_TR': 'BUZ TİTANI', 'pt_PT': 'TITÃ GLACIAL', 'hi_IN': 'हिम दैत्य', 'zh_CN': '冰川巨人', 'ko_KR': '빙하 거인', 'ru_RU': 'ЛЕДЯНОЙ ТИТАН'}, 'REI MAGMÁTICO': {'es_ES': 'REY DEL MAGMA', 'ja_JP': 'マグマの王', 'fr_FR': 'ROI DU MAGMA', 'de_DE': 'MAGMAKÖNIG', 'it_IT': 'RE DEL MAGMA', 'tr_TR': 'MAGMA KRALI', 'pt_PT': 'REI MAGMÁTICO', 'hi_IN': 'मैग्मा राजा', 'zh_CN': '岩浆之王', 'ko_KR': '마그마 왕', 'ru_RU': 'КОРОЛЬ МАГМЫ'}, 'NÚCLEO HOLOGRÁFICO': {'es_ES': 'NÚCLEO HOLOGRÁFICO', 'ja_JP': 'ホログラム核', 'fr_FR': 'NOYAU HOLOGRAPHIQUE', 'de_DE': 'HOLOGRAFISCHER KERN', 'it_IT': 'NUCLEO OLOGRAFICO', 'tr_TR': 'HOLOGRAFİK ÇEKİRDEK', 'pt_PT': 'NÚCLEO HOLOGRÁFICO', 'hi_IN': 'होलोग्राम कोर', 'zh_CN': '全息核心', 'ko_KR': '홀로그램 코어', 'ru_RU': 'ГОЛОГРАФИЧЕСКОЕ ЯДРО'}, 'JAGUAR ANCESTRAL': {'es_ES': 'JAGUAR ANCESTRAL', 'ja_JP': '古代ジャガー', 'fr_FR': 'JAGUAR ANCESTRAL', 'de_DE': 'UR-JAGUAR', 'it_IT': 'GIAGUARO ANCESTRALE', 'tr_TR': 'KADİM JAGUAR', 'pt_PT': 'JAGUAR ANCESTRAL', 'hi_IN': 'प्राचीन जगुआर', 'zh_CN': '远古美洲豹', 'ko_KR': '고대 재규어', 'ru_RU': 'ДРЕВНИЙ ЯГУАР'}, 'SERPENTE ABISSAL': {'es_ES': 'SERPIENTE ABISAL', 'ja_JP': '深淵の蛇', 'fr_FR': 'SERPENT ABYSSAL', 'de_DE': 'ABGRUNDSCHLANGE', 'it_IT': 'SERPENTE ABISSALE', 'tr_TR': 'UÇURUM YILANI', 'pt_PT': 'SERPENTE ABISSAL', 'hi_IN': 'गहरी खाई का सर्प', 'zh_CN': '深渊巨蛇', 'ko_KR': '심연의 뱀', 'ru_RU': 'БЕЗДОННЫЙ ЗМЕЙ'}, 'ÁGUIA DA TEMPESTADE': {'es_ES': 'ÁGUILA DE LA TORMENTA', 'ja_JP': '嵐の鷲', 'fr_FR': 'AIGLE DES TEMPÊTES', 'de_DE': 'STURMADLER', 'it_IT': 'AQUILA DELLA TEMPESTA', 'tr_TR': 'FIRTINA KARTALI', 'pt_PT': 'ÁGUIA DA TEMPESTADE', 'hi_IN': 'तूफ़ानी गरुड़', 'zh_CN': '风暴雄鹰', 'ko_KR': '폭풍 독수리', 'ru_RU': 'ГРОЗОВОЙ ОРЁЛ'}, 'CHEFE': {'es_ES': 'JEFE', 'ja_JP': 'ボス', 'fr_FR': 'BOSS', 'de_DE': 'BOSS', 'it_IT': 'BOSS', 'tr_TR': 'PATRON', 'pt_PT': 'CHEFE', 'hi_IN': 'बॉस', 'zh_CN': '首领', 'ko_KR': '보스', 'ru_RU': 'БОСС'}, 'ATAQUE À VISTA! DESVIE': {'es_ES': '¡ATAQUE! ¡ESQUIVA!', 'ja_JP': '攻撃！回避せよ', 'fr_FR': 'ATTAQUE ! ESQUIVEZ', 'de_DE': 'ANGRIFF! AUSWEICHEN', 'it_IT': 'ATTACCO! SCHIVA', 'tr_TR': 'SALDIRI! KAÇIN', 'pt_PT': 'ATAQUE À VISTA! DESVIE', 'hi_IN': 'हमला! बचें', 'zh_CN': '攻击！躲避', 'ko_KR': '공격! 피하세요', 'ru_RU': 'АТАКА! УКЛОНЯЙТЕСЬ'}, 'PONTOS': {'es_ES': 'PUNTOS', 'ja_JP': 'ポイント', 'fr_FR': 'POINTS', 'de_DE': 'PUNKTE', 'it_IT': 'PUNTI', 'tr_TR': 'PUAN', 'pt_PT': 'PONTOS', 'hi_IN': 'अंक', 'zh_CN': '得分', 'ko_KR': '점수', 'ru_RU': 'ОЧКИ'}, 'COMETA DOURADO': {'es_ES': 'COMETA DORADO', 'ja_JP': '黄金の彗星', 'fr_FR': 'COMÈTE DORÉE', 'de_DE': 'GOLDENER KOMET', 'it_IT': 'COMETA DORATA', 'tr_TR': 'ALTIN KUYRUKLU YILDIZ', 'pt_PT': 'COMETA DOURADO', 'hi_IN': 'सुनहरा धूमकेतु', 'zh_CN': '金色彗星', 'ko_KR': '황금 혜성', 'ru_RU': 'ЗОЛОТАЯ КОМЕТА'}, 'Nível': {'es_ES': 'Nivel', 'ja_JP': 'レベル', 'fr_FR': 'Niveau', 'de_DE': 'Stufe', 'it_IT': 'Livello', 'tr_TR': 'Seviye', 'pt_PT': 'Nível', 'hi_IN': 'स्तर', 'zh_CN': '等级', 'ko_KR': '레벨', 'ru_RU': 'Уровень'}, 'moedas': {'es_ES': 'monedas', 'ja_JP': 'コイン', 'fr_FR': 'pièces', 'de_DE': 'Münzen', 'it_IT': 'monete', 'tr_TR': 'altın', 'pt_PT': 'moedas', 'hi_IN': 'सिक्के', 'zh_CN': '金币', 'ko_KR': '코인', 'ru_RU': 'монет'}}
_PADROES = (
    (re.compile(r'^FASE (?P<tipo>INVERTIDO|FLAPPY|TUNEL|AQUATICO|LASERS|TESOURO|REFLEXOS)!$'), 'entrada_portal'),
    (re.compile(r'^FASE BÔNUS \+(?P<n>\d+)$'), 'premio_portal'),
    (re.compile(r'^COMETA DOURADO • (?P<n>\d+) m$'), 'cometa'),
    (re.compile(r'^(?P<n>\d+)s  •  PONTOS (?P<m>\d+)$'), 'pontos'),
    (re.compile(r'^(?P<boss>.+) • HP (?P<n>\d+)$'), 'boss'),
    (re.compile(r'^(?P<flag>[✓○]) Nível (?P<n>\d+): (?P<m>\d+) m • \+(?P<reward>\d+) moedas$'), 'marco'),
)
@lru_cache(maxsize=256)
def localizar_condicional(texto, idioma):
    if idioma not in IDIOMAS: return texto
    if texto in TITULOS: return TITULOS[texto][idioma]
    for regex, tipo in _PADROES:
        m=regex.fullmatch(texto)
        if not m: continue
        v=m.groupdict()
        if tipo=='entrada_portal':
            titulo={'INVERTIDO':'GRAVIDADE INVERTIDA','FLAPPY':'DESAFIO FLAPPY',
                    'TUNEL':'TÚNEL DE PRECISÃO','AQUATICO':'ABISMO AQUÁTICO',
                    'LASERS':'FUGA DOS LASERS','TESOURO':'PORTAL DO TESOURO',
                    'REFLEXOS':'PORTAL DE REFLEXOS'}[v['tipo']]
            return TITULOS[titulo][idioma] + '!'
        if tipo=='premio_portal':
            return f"{TITULOS['FASE BÔNUS'][idioma]} +{v['n']}"
        if tipo=='cometa': return f"{TITULOS['COMETA DOURADO'][idioma]} • {v['n']} m"
        if tipo=='pontos': return f"{v['n']}s • {TITULOS['PONTOS'][idioma]} {v['m']}"
        if tipo=='boss':
            nome=TITULOS.get(v['boss'])
            if nome: return f"{nome[idioma]} • HP {v['n']}"
        if tipo=='marco':
            return f"{v['flag']} {TITULOS['Nível'][idioma]} {v['n']}: {v['m']} m • +{v['reward']} {TITULOS['moedas'][idioma]}"
    return texto

def textos_unicode(idioma):
    return ''.join(t[idioma] for t in TITULOS.values()) if idioma in IDIOMAS else ''
