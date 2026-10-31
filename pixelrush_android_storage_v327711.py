"""Pasta persistente SDL2 para saves no Android. Sem efeito no desktop.

Usa SDL_GetPrefPath por meio de pygame-ce; em Android, o SDL usa o
armazenamento privado persistente da aplicação. Nenhuma migração automática
é executada, para evitar perda de dados sem teste em aparelho real.
"""
from pathlib import Path


def resolver_save(nome: str, *, android: bool = False) -> str:
    if not android:
        return str(nome)  # Comportamento original da PROD no desktop.
    import pygame
    # SDL_GetPrefPath cria uma pasta gravável e persistente no Android.
    diretorio = pygame.system.get_pref_path("PixelRush", "PixelRush")
    if not diretorio:
        raise OSError("SDL_GetPrefPath nao retornou pasta persistente")
    pasta = Path(diretorio)
    pasta.mkdir(parents=True, exist_ok=True)
    if not pasta.is_dir():
        raise OSError("Pasta de saves do Android indisponivel")
    return str(pasta / Path(nome).name)
