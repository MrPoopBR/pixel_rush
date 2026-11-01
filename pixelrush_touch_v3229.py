"""Normalizacao leve de distancias do Jetpack em eventos touch/mouse.

Os tres niveis e a distancia de 30 px por faixa ja existiam. Uma unica
notificacao SDL pode acumular deslocamento de mais de uma faixa.
Python 3.9+, sem estados globais e sem alocacoes por frame.
"""


def passos_jetpack(delta_y, limite=30):
    """Retorna -2..2 passos conforme o deslocamento; positivo significa descer."""
    valor = int(abs(delta_y) // limite)
    if valor > 2:
        valor = 2
    return (-valor if delta_y < 0 else valor)


def ancorar_jetpack(y_anterior, y_atual, passos, limite=30):
    """Consome passos inteiros e conserva resto; ignora excesso de evento agregado."""
    if abs(y_atual - y_anterior) >= 3 * limite:
        return y_atual
    return y_anterior + passos * limite
