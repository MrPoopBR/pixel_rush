"""v3.152.0 — mais folga visual entre perigos, sem alterar intervalo em metros.

Reutiliza todas as regras da v3.124.0, ampliando apenas a margem
horizontal de tela entre encontros (220 -> 250 px).
"""
from pixelrush_spawn_v3124 import EspacamentoPorDistancia as Anterior


class EspacamentoPorDistancia(Anterior):
    FOLGA_VISUAL = 250

    def pode_gerar(self, metros, obstaculos, perigos, buracos, largura):
        if not super().pode_gerar(metros, obstaculos, perigos, buracos, largura):
            return False
        # Não iniciar a próxima situação enquanto o perigo anterior ainda
        # ocupa a área em que o jogador precisa identificar o comando.
        limite = largura - self.FOLGA_VISUAL
        return not any(getattr(obj, 'rect', None) is not None and obj.rect.right >= limite
                       for grupo in (obstaculos, perigos, buracos) for obj in grupo)
