# -*- coding: utf-8 -*-
"""Objetivos curtos do tutorial PROD, sem comandos da outra plataforma.

Reutiliza as 13 traduções originais das dicas para evitar divergência de
controles. Nenhuma alteração ao catálogo do ramo de desenvolvimento.
"""
from pixelrush_i18n_v3246 import normalizar_idioma

# Pular cone, pular cone/hidrante, desviar do pombo e usar descida no ar.
_OBJETIVOS = {
 'pt_BR': ('Salte o cone.', 'Passe sobre o cone e o hidrante.', 'Passe sob o pombo.', 'Desça rápido durante o salto.', 'TOQUE'),
 'pt_PT': ('Salta o cone.', 'Passa por cima do cone e da boca de incêndio.', 'Passa por baixo do pombo.', 'Desce depressa durante o salto.', 'TOQUE'),
 'en_US': ('Jump over the cone.', 'Clear the cone and hydrant.', 'Pass under the pigeon.', 'Descend quickly while airborne.', 'TOUCH'),
 'es_ES': ('Salta sobre el cono.', 'Supera el cono y el hidrante.', 'Pasa bajo la paloma.', 'Baja rápido en el aire.', 'TOQUE'),
 'fr_FR': ('Sautez le cône.', 'Franchissez le cône et la borne.', 'Passez sous le pigeon.', 'Descendez vite dans les airs.', 'TACTILE'),
 'de_DE': ('Springe über den Kegel.', 'Überwinde Kegel und Hydrant.', 'Laufe unter der Taube durch.', 'Sinke in der Luft schnell ab.', 'TOUCH'),
 'it_IT': ('Salta sopra il cono.', 'Supera il cono e l’idrante.', 'Passa sotto il piccione.', 'Scendi in fretta in aria.', 'TOCCO'),
 'tr_TR': ('Koninin üzerinden atla.', 'Koniyi ve hidrantı aş.', 'Güvercinin altından geç.', 'Havada hızlıca aşağı in.', 'DOKUNMA'),
 'ru_RU': ('Перепрыгни конус.', 'Перепрыгни конус и гидрант.', 'Пройди под голубем.', 'Быстро опустись в воздухе.', 'КАСАНИЕ'),
 'ja_JP': ('コーンを飛び越えよう。', 'コーンと消火栓を飛び越えよう。', 'ハトの下を通ろう。', '空中で素早く降りよう。', 'タッチ'),
 'ko_KR': ('콘을 뛰어넘으세요.', '콘과 소화전을 뛰어넘으세요.', '비둘기 아래로 지나가세요.', '공중에서 빠르게 내려오세요.', '터치'),
 'zh_CN': ('跳过路锥。', '跳过路锥和消防栓。', '从鸽子下方通过。', '在空中快速下降。', '触摸'),
 'hi_IN': ('कोन के ऊपर कूदें।', 'कोन और हाइड्रेंट पार करें।', 'कबूतर के नीचे से जाएँ।', 'हवा में तेज़ी से नीचे आएँ।', 'स्पर्श'),
}
_ETAPAS = ('pular', 'pular_longo', 'agachar', 'swipe_down')

def instrucoes_plataforma(idioma, etapa, toque, ui):
    codigo = normalizar_idioma(idioma)
    objetivos = _OBJETIVOS.get(codigo, _OBJETIVOS['pt_BR'])
    if etapa == 'etiqueta_toque':
        return objetivos[4]
    if etapa not in _ETAPAS:
        return ui['textos'][etapa][1]
    i = _ETAPAS.index(etapa)
    dica = ui['dicas'][etapa][1 if toque else 0]
    # Uma única plataforma por vez: descrição e barra falam do mesmo gesto.
    return f"{dica}. {objetivos[i]}"

# Feedback de tentativa do tutorial, igualmente exclusivo do idioma atual.
_REPETIR = {
 'pt_BR':'TENTE NOVAMENTE!', 'pt_PT':'TENTA NOVAMENTE!',
 'en_US':'TRY AGAIN!', 'es_ES':'¡INTÉNTALO DE NUEVO!',
 'fr_FR':'RÉESSAYEZ !', 'de_DE':'VERSUCH ES NOCHMAL!',
 'it_IT':'RIPROVA!', 'tr_TR':'TEKRAR DENE!',
 'ru_RU':'ПОПРОБУЙ ЕЩЁ РАЗ!', 'ja_JP':'もう一度！',
 'ko_KR':'다시 도전!', 'zh_CN':'再试一次！', 'hi_IN':'फिर से कोशिश करें!'
}

def mensagem_repetir(idioma):
    return _REPETIR.get(normalizar_idioma(idioma), _REPETIR['pt_BR'])
