"""
audio.py — Gerenciador de música ambiente.

Alterna as faixas conforme o momento do jogo (tela inicial, suspense,
combate, fase 2) sem reiniciar uma faixa que já está tocando.
"""
import pygame

from . import settings


class MusicManager:
    """Toca uma música por vez, de acordo com o "humor" atual do jogo."""

    TRACKS = {
        "intro": "intro.ogg",
        "suspense": "suspense.ogg",
        "combat": "first_phase_melody.ogg",
        "phase2": "second_phase_melody_alt.ogg",
    }

    def __init__(self):
        self.current: str | None = None
        self.failed: set[str] = set()

    def play(self, mood: str) -> None:
        """Troca a faixa se o humor pedido for diferente do que está tocando."""
        if mood == self.current or mood not in self.TRACKS:
            return
        if mood in self.failed:
            return
        path = settings.MUSIC_DIR / self.TRACKS[mood]
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1, fade_ms=1000)
            self.current = mood
        except (pygame.error, FileNotFoundError) as error:
            print(f"[Aviso] Música não encontrada: '{path}' ({error})")
            self.failed.add(mood)

    def fadeout(self, milliseconds: int = 2000) -> None:
        try:
            pygame.mixer.music.fadeout(milliseconds)
        except pygame.error:
            pass
        self.current = None
