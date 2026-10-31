"""Regras compartilhadas dos chunks originais e do parallax experimental.

Todas as camadas usam a mesma sequencia e mesmo stride. A geometria original
nao muda: o objetivo e evitar desalinhamento entre plano base e sprites,
sem gerar novos obstaculos, hitboxes ou biomas.
"""
CHUNK_SIZE = 900
CHUNK_OVERLAP = 48
CHUNK_STEP = CHUNK_SIZE - CHUNK_OVERLAP
CHUNK_MIRRORS = (False, True, False, False, True, True, False, True, True, False, True, False)
CHUNK_PERIOD = CHUNK_STEP * len(CHUNK_MIRRORS)


def visible_chunks(travel, speed, view_width):
    """Itera apenas trechos na viewport, inclusive quando travel > 1e9."""
    offset = int(max(0., float(travel)) * float(speed)) % CHUNK_PERIOD
    first = max(0, (offset - CHUNK_SIZE) // CHUNK_STEP)
    last = min(len(CHUNK_MIRRORS) + 1, (offset + int(view_width)) // CHUNK_STEP + 1)
    for index in range(first, last + 1):
        x = index * CHUNK_STEP - offset
        if x <= view_width and x + CHUNK_SIZE >= 0:
            yield index, bool(CHUNK_MIRRORS[index % len(CHUNK_MIRRORS)]), x
