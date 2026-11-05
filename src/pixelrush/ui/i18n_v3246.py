# -*- coding: utf-8 -*-
"""Pixel Rush v3.246.0: infraestrutura i18n incremental e leve.

Reutiliza o dicionário TEXTOS dos executáveis, sem reproduzir traduções.
Não lê arquivos nem cria superfícies no loop. Português brasileiro como fallback.
Catálogos complementares de novas línguas serão registrados na etapa 17.
"""
from string import Formatter
from types import MappingProxyType

IDIOMA_PADRAO = "pt_BR"
_CATALOGOS_ADICIONAIS = {}
_FORMATADOR = Formatter()


def normalizar_idioma(valor):
    """Normaliza identificadores sem alterar a opção persistida no save."""
    if not isinstance(valor, str) or len(valor) > 16:
        return IDIOMA_PADRAO
    codigo = valor.strip().replace("-", "_")
    partes = codigo.split("_")
    if len(partes) == 2 and len(partes[0]) in (2, 3) and len(partes[1]) in (2, 4):
        if partes[0].isalpha() and partes[1].isalpha() and partes[0].isascii() and partes[1].isascii():
            return partes[0].lower() + "_" + partes[1].upper()
    return IDIOMA_PADRAO


def chaves_formato(texto):
    """Identifica campos formatáveis para conferir traduções futuras."""
    campos = []
    for _, campo, spec, conversao in _FORMATADOR.parse(texto):
        if campo is not None:
            campos.append((campo, spec, conversao))
    return tuple(campos)


def registrar_catalogo(codigo, entradas, catalogos_base):
    """Registra traduções opcionais após validar chaves e placeholders.

    Não altera o catálogo original, sprites, fontes, HUD ou o save.
    A etapa 17 poderá usar esta API para registrar os outros idiomas.
    """
    idioma = normalizar_idioma(codigo)
    if idioma == IDIOMA_PADRAO or idioma != codigo.replace("-", "_").split("_")[0].lower() + "_" + codigo.replace("-", "_").split("_")[-1].upper():
        raise ValueError("Código de idioma inválido ou reservado")
    if not isinstance(entradas, dict):
        raise TypeError("O catálogo deve ser um dicionário")
    referencia = catalogos_base[IDIOMA_PADRAO]
    novo = {}
    for chave, texto in entradas.items():
        if not isinstance(chave, str) or chave not in referencia:
            raise ValueError("Chave de tradução desconhecida: " + str(chave))
        if not isinstance(texto, str) or not texto.strip() or len(texto) > 2048:
            raise ValueError("Texto traduzido vazio ou inválido: " + chave)
        if chaves_formato(texto) != chaves_formato(referencia[chave]):
            raise ValueError("Placeholders incompatíveis: " + chave)
        novo[chave] = texto
    _CATALOGOS_ADICIONAIS[idioma] = MappingProxyType(novo)
    return idioma


def idiomas_disponiveis(catalogos_base):
    """Idiomas habilitados no catálogo, sem mostrar traduções não instaladas."""
    return tuple(dict.fromkeys(tuple(catalogos_base) + tuple(_CATALOGOS_ADICIONAIS)))


def traduzir(chave, dados, catalogos_base):
    """Compatível com t(chave, dados); fallback por chave para pt_BR.

    As traduções do dicionário legadas en_US/pt_BR têm prioridade e
    mantém exatamente as strings da v3.245.0, inclusive a opção de idioma.
    """
    codigo = normalizar_idioma(dados.get("idioma", IDIOMA_PADRAO)) if isinstance(dados, dict) else IDIOMA_PADRAO
    catalogo = _CATALOGOS_ADICIONAIS.get(codigo)
    if catalogo is None:
        catalogo = catalogos_base.get(codigo)
    if catalogo is not None and chave in catalogo:
        return catalogo[chave]
    return catalogos_base[IDIOMA_PADRAO].get(chave, chave)


def traduzir_formatado(chave, dados, catalogos_base, *args, **kwargs):
    """Formata strings dinâmicas, com fallback seguro para pt_BR."""
    texto = traduzir(chave, dados, catalogos_base)
    try:
        return texto.format(*args, **kwargs)
    except (ValueError, KeyError, IndexError, AttributeError, TypeError):
        texto = catalogos_base[IDIOMA_PADRAO].get(chave, chave)
        try:
            return texto.format(*args, **kwargs)
        except (ValueError, KeyError, IndexError, AttributeError, TypeError):
            return texto


def auditar_catalogos(catalogos_base):
    """Relatório puro: lacunas e incompatibilidades de placeholders."""
    base = catalogos_base[IDIOMA_PADRAO]
    resultado = {}
    for codigo, entradas in list(catalogos_base.items()) + list(_CATALOGOS_ADICIONAIS.items()):
        faltantes = sorted(set(base) - set(entradas))
        extras = sorted(set(entradas) - set(base))
        erros = []
        for chave, texto in entradas.items():
            if chave in base:
                try:
                    if chaves_formato(texto) != chaves_formato(base[chave]):
                        erros.append(chave)
                except ValueError:
                    erros.append(chave)
        resultado[codigo] = {"total": len(entradas), "faltantes": faltantes,
                             "extras": extras, "placeholders_invalidos": erros}
    return resultado
