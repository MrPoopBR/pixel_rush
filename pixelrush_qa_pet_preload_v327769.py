# -*- coding: utf-8 -*-
"""QA769: antecipacao SOMENTE dos quadros de compatibilidade dos pets.

Pets permanecem COMING SOON: PetStudioPlayer da producao fornece quadros
transparentes por tamanho. Reutilizar as Surfaces reais do proprio Studio,
sem construir novos pets, alterar saves, sprites, inventario ou RNG.
Executar apenas pelo preloader QA de menu, nunca no loop da corrida.
"""

TAMANHOS_PET_COMPAT = ((52, 46), (210, 170))


def preparar_pet_compativel(pet_id, original_preload, obter_quadros):
    """Prepara os dois tamanhos usados: HUD/corrida e popup da loja.

    A rotina do jogo original continua sendo chamada primeiro. O retorno
    indica apenas sucesso do prewarm de compatibilidade, NAO pet ativo.
    Excecoes devem ser tratadas pelo agendador existente e preservam lazy.
    """
    original_preload(pet_id)
    for tamanho in TAMANHOS_PET_COMPAT:
        quadros = obter_quadros(pet_id, 'ESPERA', tamanho)
        if not quadros:
            return False
    return True
