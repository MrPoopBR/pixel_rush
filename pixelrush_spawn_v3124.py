"""Spawn por distancia da v3.124.0; não modifica a física."""
class EspacamentoPorDistancia:
    def __init__(self):
        self.ultimo_metro = None
        self.ultimo_observado = None

    @staticmethod
    def intervalo(metros):
        # 34m nos primeiros trechos, redução gradual até 27m após 1800m.
        return max(27, 34 - max(0, int(metros)) // 300)

    def pode_gerar(self, metros, obstaculos, perigos, buracos, largura):
        metros = max(0, int(metros))
        if self.ultimo_observado is not None and metros < self.ultimo_observado:
            self.ultimo_metro = None   # nova partida após reset de pontuação
        self.ultimo_observado = metros
        if self.ultimo_metro is not None and metros-self.ultimo_metro < self.intervalo(metros):
            return False
        grupos = (obstaculos, perigos, buracos)
        if sum(len(g) for g in grupos) >= 2:
            return False
        # Mínimo de 220px livres à frente da borda de nascimento.
        for grupo in grupos:
            for obj in grupo:
                rect = getattr(obj, 'rect', None)
                if rect is not None and rect.right >= largura - 220:
                    return False
        return True

    def registrar(self, metros):
        self.ultimo_metro = max(0, int(metros))
