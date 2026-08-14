"""
effects.py — Efeitos visuais simples: partículas e textos flutuantes de dano.

Essas classes dão o "game feel": explosões de partículas ao acertar inimigos,
faíscas ao andar de XLR8 e os números de dano que sobem pela tela.
"""
import math
import random

import pygame
from pygame import Vector2


class ParticleSystem:
    """Conjunto de pequenas bolinhas que nascem, se movem e desaparecem."""

    def __init__(self):
        self.particles: list[dict] = []

    def burst(self, position, count: int, color, speed: float,
              lifetime: float, radius: int, spread: float = 6.28) -> None:
        """Cria `count` partículas espalhadas em volta de `position`."""
        for _ in range(count):
            angle = random.uniform(0, spread)
            self.particles.append({
                "pos": Vector2(position),
                "vel": Vector2(math.cos(angle), math.sin(angle)) * random.uniform(speed * 0.3, speed),
                "radius": random.uniform(radius * 0.5, radius),
                "lifetime": random.uniform(lifetime * 0.5, lifetime),
                "max_lifetime": lifetime,
                "color": color,
            })

    def update(self, dt: float) -> None:
        for particle in self.particles:
            particle["pos"] += particle["vel"] * dt
            particle["vel"] *= (1 - 2.0 * dt)          # resistência do ar
            particle["lifetime"] -= dt
        self.particles = [p for p in self.particles if p["lifetime"] > 0]

    def draw(self, surface: pygame.Surface, world_offset) -> None:
        for particle in self.particles:
            progress = particle["lifetime"] / particle["max_lifetime"]  # 1 -> 0
            radius = max(1, int(particle["radius"] * progress))
            position = particle["pos"] - world_offset
            pygame.draw.circle(surface, particle["color"], position, radius)


class FloatingTexts:
    """Números de dano / mensagens que sobem e somem na tela."""

    def __init__(self):
        self.font = pygame.font.Font(None, 22)
        self.texts: list[dict] = []

    def add(self, text: str, position, color, lifetime: float = 0.9) -> None:
        self.texts.append({
            "text": text,
            "pos": Vector2(position),
            "color": color,
            "lifetime": lifetime,
            "max_lifetime": lifetime,
        })

    def update(self, dt: float) -> None:
        for text in self.texts:
            text["pos"].y -= 40 * dt          # sobe suavemente
            text["lifetime"] -= dt
        self.texts = [t for t in self.texts if t["lifetime"] > 0]

    def draw(self, surface: pygame.Surface, world_offset) -> None:
        for text in self.texts:
            alpha = max(0, int(255 * text["lifetime"] / text["max_lifetime"]))
            rendered = self.font.render(text["text"], True, text["color"])
            rendered.set_alpha(alpha)
            position = text["pos"] - world_offset
            surface.blit(rendered, rendered.get_rect(center=position))
