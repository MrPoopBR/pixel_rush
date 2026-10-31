"""Pixel Rush v3.190.0 — acabamento do feedback existente (somente Pygame).

Sem novas ações/recompensas/temporizadores/sons: o sprite original do texto
mantém ciclo e trajetória, com moldura desenhada UMA VEZ na criação.
"""
import pygame


def categoria_feedback(texto):
    texto = str(texto).strip().upper()
    if texto.startswith(("QUASE COLIS", "NEAR MISS", "ESQUIVA PERFEITA", "PERFECT DODGE")):
        return "precisao"
    if texto.startswith("COMBO "):
        return "combo"
    if texto.startswith(("IMPULSO ATIVADO", "BOOST ACTIVATED")):
        return "impulso"
    if texto.startswith(("FEBRE", "FEVER")):
        return "febre"
    return None


def aprimorar_texto_flutuante(classe_original):
    """Subclasse transparente: altera apenas image e rect visual, não update/vida."""
    class TextoFlutuantePremium(classe_original):
        def __init__(self, x, y, texto, cor, tamanho="normal"):
            super().__init__(x, y, texto, cor, tamanho)
            categoria = categoria_feedback(texto)
            if not categoria:
                return
            original = self.image
            largura, altura = original.get_size()
            margem_x, margem_y = 7, 4
            largura_nova, altura_nova = largura + 2 * margem_x, altura + 2 * margem_y
            painel = pygame.Surface((largura_nova, altura_nova), pygame.SRCALPHA)
            # O fundo protege o texto contra cenários complexos sem bloom ou pós-processo.
            cores = {
                "precisao": (253, 217, 104),
                "combo": (100, 218, 250),
                "impulso": (105, 238, 202),
                "febre": (255, 157, 98),
            }
            acento = cores[categoria]
            pygame.draw.rect(painel, (12, 21, 35, 170),
                             pygame.Rect(1, 1, largura_nova - 2, altura_nova - 2), border_radius=3)
            pygame.draw.line(painel, (*acento, 215),
                             (4, altura_nova - 3), (largura_nova - 5, altura_nova - 3), 1)
            # Mini marcas internas estáticas; não adicionam partículas à partida.
            pygame.draw.line(painel, (*acento, 180), (3, 4), (3, altura_nova - 6), 1)
            pygame.draw.line(painel, (*acento, 180),
                             (largura_nova - 4, 4), (largura_nova - 4, altura_nova - 6), 1)
            painel.blit(original, (margem_x, margem_y))
            centro = self.rect.center
            self.image = painel
            self.rect = painel.get_rect(center=centro)
            self.y_popup = float(self.rect.y)

    TextoFlutuantePremium.__name__ = classe_original.__name__
    return TextoFlutuantePremium
