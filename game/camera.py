"""
camera.py — A câmera "de cima" com inclinação suave na direção do mouse.

Técnica usada (pseudo-3D):
  1. O mundo é desenhado em um surface um pouco maior que a tela.
  2. Esse surface é ROTACIONADO um pouco (até ~3.5°) e levemente "achatado"
     na vertical, conforme a posição do mouse em relação ao centro.
  3. O resultado é colocado na tela de forma que o jogador continue no centro
     (com um pequeno pan oposto à mira, dando sensação de a câmera "se inclinar").

O método `screen_to_world` inverte essa transformação para que a mira do
mouse continue precisa, mesmo com a tela inclinada.
"""
import math
import random

import pygame
from pygame import Rect, Vector2

from . import settings


class Camera:
    def __init__(self, view_size, world_rect: Rect):
        self.view_w, self.view_h = view_size
        self.world_rect = world_rect
        self.padding = settings.CAMERA_PADDING

        # centro da visão no mundo (segue o jogador)
        self.position = Vector2(world_rect.center)

        # tremida de tela
        self.shake_until = 0.0
        self.shake_intensity = 0.0

        # inclinação atual (calculada a cada frame pela posição do mouse)
        self.yaw = 0.0
        self.pitch = 0.0
        self.aim_dir = Vector2(1, 0)
        self.anchor_screen = Vector2(self.view_w / 2, self.view_h / 2)

        # surface do mundo (tela + margem para a rotação não expor bordas)
        self.surf_w = self.view_w + 2 * self.padding
        self.surf_h = self.view_h + 2 * self.padding
        self.surf = pygame.Surface((self.surf_w, self.surf_h), pygame.SRCALPHA)

        # dados da última renderização (para inverter a transformação)
        self._blit_pos = Vector2(0, 0)
        self._rot_center = Vector2(0, 0)
        self._pitch_center = Vector2(0, 0)
        self._pitch_scale_y = 1.0
        self._pitch_applied = False
        self._last_offset = Vector2(world_rect.center) - Vector2(view_size[0] / 2,
                                                                 view_size[1] / 2) \
            - Vector2(self.padding, self.padding)

    # ------------------------------------------------------------------
    # Atualização
    # ------------------------------------------------------------------
    def update(self, dt: float, now: float, target_pos, mouse_screen) -> None:
        # segue o alvo com suavidade (lerp exponencial, FPS-independente)
        lerp = 1 - math.exp(-settings.CAMERA_FOLLOW_SPEED * dt)
        self.position = self.position.lerp(Vector2(target_pos), lerp)

        # trava a câmera nos limites do mundo: a borda do mapa é a borda da tela
        half_w, half_h = self.view_w / 2, self.view_h / 2
        self.position.x = max(half_w, min(self.world_rect.width - half_w, self.position.x))
        self.position.y = max(half_h, min(self.world_rect.height - half_h, self.position.y))

        # inclinação a partir do mouse: -1..1 em cada eixo
        center = Vector2(self.view_w / 2, self.view_h / 2)
        dx = (mouse_screen[0] - center.x) / center.x
        dy = (mouse_screen[1] - center.y) / center.y
        self.yaw = max(-1.0, min(1.0, dx)) * settings.CAMERA_MAX_YAW
        self.pitch = -max(-1.0, min(1.0, dy)) * settings.CAMERA_MAX_PITCH

        # direção da mira para o "pan" (câmera mostra mais o lado do mouse)
        aim = Vector2(mouse_screen) - center
        if aim.length_squared() > 1:
            aim = aim.normalize()
            self.aim_dir = aim
        self.anchor_screen = center - aim * settings.CAMERA_MAX_PAN

    def shake(self, now: float, intensity: float = 10.0, duration: float = 0.2) -> None:
        self.shake_until = now + duration
        self.shake_intensity = intensity

    def is_shaking(self, now: float) -> bool:
        return now < self.shake_until

    @property
    def view_rect(self) -> Rect:
        """Retângulo visível no mundo (usado para spawnar inimigos nas bordas)."""
        return Rect(self.position.x - self.view_w / 2,
                    self.position.y - self.view_h / 2,
                    self.view_w, self.view_h)

    def world_offset(self, now: float) -> Vector2:
        """Converte coordenada do mundo -> coordenada do surface de render."""
        top_left = self.position - Vector2(self.view_w / 2, self.view_h / 2)
        if now < self.shake_until:
            top_left += Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) \
                        * self.shake_intensity
        return top_left - Vector2(self.padding, self.padding)

    def record_drawn_offset(self, offset: Vector2) -> None:
        """Guarda o offset usado ao desenhar o mundo neste frame.

        A mira (screen_to_world) usa exatamente esse offset, então o mouse
        continua batendo no que está na tela mesmo durante o screen shake.
        """
        self._last_offset = Vector2(offset)

    # ------------------------------------------------------------------
    # Renderização com inclinação
    # ------------------------------------------------------------------
    def present(self, surface: pygame.Surface, now: float, player_pos=None) -> None:
        """Aplica rotação + pitch no surface do mundo e desenha na tela.

        O jogador fica preso em `anchor_screen` (centro da tela com um leve pan
        oposto à mira), e o mundo gira ao redor dele.
        """
        center = Vector2(self.surf_w / 2, self.surf_h / 2)
        # posição do jogador dentro do surface (mundo - offset de render)
        world_offset = self.world_offset(now)
        player_in_surf = (Vector2(player_pos) - world_offset) if player_pos is not None \
            else Vector2(center)

        # caminho rápido: quase sem inclinação, blita direto a área visível
        if abs(self.yaw) < 0.08 and abs(self.pitch) < 0.002:
            view_area = Rect(self.padding, self.padding, self.view_w, self.view_h)
            surface.blit(self.surf, (0, 0), area=view_area)
            self._blit_pos = -Vector2(self.padding, self.padding)
            self._rot_center = center
            self._pitch_center = center
            self._pitch_scale_y = 1.0
            self._pitch_applied = False
            return

        rotated = pygame.transform.rotate(self.surf, self.yaw)
        rot_center = Vector2(rotated.get_width() / 2, rotated.get_height() / 2)
        p_rot = rot_center + (player_in_surf - center).rotate(self.yaw)

        pitched, pitch_center, p_pitch, scale_y = rotated, rot_center, p_rot, 1.0
        if abs(self.pitch) > 0.002:
            new_height = max(1, int(rotated.get_height() * (1 + self.pitch)))
            pitched = pygame.transform.scale(rotated, (rotated.get_width(), new_height))
            pitch_center = Vector2(pitched.get_width() / 2, pitched.get_height() / 2)
            scale_y = new_height / rotated.get_height()
            p_pitch = pitch_center + Vector2((p_rot.x - rot_center.x),
                                             (p_rot.y - rot_center.y) * scale_y)

        blit_pos = self.anchor_screen - p_pitch
        surface.blit(pitched, blit_pos)

        # guarda para inverter a transformação na mira
        self._blit_pos = Vector2(blit_pos)
        self._rot_center = rot_center
        self._pitch_center = pitch_center
        self._pitch_scale_y = scale_y
        self._pitch_applied = True

    # ------------------------------------------------------------------
    # Mira precisa (inverte a inclinação)
    # ------------------------------------------------------------------
    def screen_to_world(self, screen_pos) -> Vector2:
        """Converte posição do mouse na tela -> posição no mundo, compensando o tilt."""
        point = Vector2(screen_pos) - self._blit_pos
        # desfaz o pitch (se foi aplicado)
        if self._pitch_applied:
            point = self._pitch_center + Vector2(
                point.x - self._pitch_center.x,
                (point.y - self._pitch_center.y) / self._pitch_scale_y)
        # desfaz a rotação
        point = self._rot_center + (point - self._rot_center).rotate(-self.yaw)
        return point + self._last_offset
