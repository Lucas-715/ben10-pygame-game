"""
ui.py — Interface do jogo: HUD (vida, XP, energia, armas, cronômetro),
crosshair do mouse e as telas de menu (início, level-up e game over).
"""
import math

import pygame
from pygame import Rect, Vector2

from . import settings


class HUD:
    """Desenha todas as informações sobrepostas ao mundo (não inclinam)."""

    def __init__(self, assets):
        self.assets = assets
        self.font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 64)
        # estado do hover no Omnitrix (seleção por permanência de 3s)
        self.hover_alien: str | None = None
        self.hover_timer = 0.0
        self._pending_transform: str | None = None

    # ------------------------------------------------------------------
    # HUD durante o jogo
    # ------------------------------------------------------------------
    def draw_hud(self, surface, player, kills, elapsed, next_alien=None,
                 mouse_pos=None, show_stats=False) -> None:
        self._draw_bars(surface, player)
        self._draw_alien_attacks(surface, player)
        self._draw_counters(surface, kills, elapsed, player.alien_name, next_alien)
        self._draw_omnitrix_strip(surface, player, next_alien, mouse_pos)
        self._draw_prism(surface, player)
        self._draw_powerups(surface, player)
        self._draw_combo(surface, player)
        if show_stats:
            self._draw_stats_panel(surface, player)

    # ------------------------------------------------------------------
    # Hover no Omnitrix (seleção por permanência — acessibilidade)
    # ------------------------------------------------------------------
    def update_hover(self, dt: float, mouse_pos, player) -> None:
        """Acumula o tempo de hover sobre um retrato do Omnitrix.

        Parar o mouse 3s sobre o mesmo retrato pede a transformação (o Game
        consome via consume_hover_transform). Sair do retrato esvazia o anel
        de forma suave (drain) em vez de cortar seco.
        """
        if not settings.HOVER_TRANSFORM_ENABLED:
            self.hover_alien = None
            self.hover_timer = 0.0
            return
        hovered = self._hovered_portrait(mouse_pos)
        if hovered is None:
            # drain animado: o anel esvazia em vez de sumir num corte seco
            if self.hover_timer > 0:
                self.hover_timer = max(0.0, self.hover_timer - dt * 2.2)
                if self.hover_timer <= 0:
                    self.hover_alien = None
            return
        if hovered == player.alien_name:
            # já é o alien atual: hover não faz nada (sem anel, sem banner falso)
            self.hover_alien = hovered
            self.hover_timer = 0.0
            return
        if hovered != self.hover_alien:
            self.hover_alien = hovered
            self.hover_timer = 0.0
            return
        self.hover_timer += dt
        if self.hover_timer >= settings.HOVER_TRANSFORM_TIME:
            self._pending_transform = hovered
            self.hover_timer = 0.0   # só dispara uma vez por hover

    def consume_hover_transform(self) -> str | None:
        """Devolve o alien pendente do hover (e limpa o pedido)."""
        pending = self._pending_transform
        self._pending_transform = None
        return pending

    def _hovered_portrait(self, mouse_pos):
        """Qual retrato do Omnitrix está sob o mouse (zona pequena e centrada)."""
        if mouse_pos is None:
            return None
        for name, x, y in self._strip_positions():
            if (Vector2(mouse_pos) - (x, y)).length() <= settings.HOVER_ZONE_RADIUS:
                return name
        return None

    def _strip_positions(self):
        """Posições (nome, x, y) dos 5 retratos na faixa do Omnitrix."""
        spacing = 38
        start_x = settings.WINDOW_WIDTH / 2 - (len(settings.ALIEN_ORDER) - 1) * spacing / 2
        y = 130
        positions = []
        for index, name in enumerate(settings.ALIEN_ORDER):
            positions.append((name, int(start_x + index * spacing), y))
        return positions

    def _draw_bars(self, surface, player) -> None:
        """Barras de vida, XP e energia no canto superior esquerdo."""
        x, y = 18, 22
        # ícone de vida + barra
        heart = self.assets.get_ui("heart")
        if heart is not None:
            heart = pygame.transform.scale(heart, (24, 24))
            surface.blit(heart, (x, y))
            bar_x = x + 30
        else:
            bar_x = x
        self._bar(surface, bar_x, y, 200, 22,
                  player.health / player.max_health,
                  settings.COLORS["health_green"],
                  settings.COLORS["health_dark"])
        self._draw_text(surface, self.small_font, (bar_x + 4, y + 4),
                        f"{max(0, int(player.health))}/{player.max_health}")
        # barra de XP
        progress = player.xp / settings.xp_needed(player.level)
        self._bar(surface, bar_x, y + 28, 200, 14, progress,
                  settings.COLORS["xp_blue"], settings.COLORS["health_dark"])
        self._draw_text(surface, self.small_font, (bar_x + 4, y + 30),
                        f"Nível {player.level}")
        # energia do Omnitrix
        self._bar(surface, bar_x, y + 48, 200, 14,
                  player.energy / settings.ENERGY_MAX,
                  settings.COLORS["omnitrix_green"], settings.COLORS["health_dark"])
        self._draw_text(surface, self.small_font, (bar_x + 4, y + 50),
                        f"Energia {int(player.energy)}%")
        # escudos Petrossápien (ícone + quantidade) abaixo da energia
        if player.shield_charges > 0:
            shield = self.assets.get_ui("shield")
            if shield is not None:
                shield = pygame.transform.scale(shield, (18, 18))
                surface.blit(shield, (bar_x, y + 68))
                self._draw_text(surface, self.small_font, (bar_x + 22, y + 70),
                                f"x{player.shield_charges}", settings.COLORS["omnitrix_green"])
        # faixa de PERIGO da energia: pulsando quando está abaixo de ~15% —
        # aviso visual antes do retorno forçado ao Ben em pleno combate
        if player.alien_name != "Ben" and player.energy < settings.ENERGY_MAX * 0.15:
            pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 120)
            danger = (int(255 * (0.4 + 0.6 * pulse)), 40, 40)
            pygame.draw.rect(surface, danger, (bar_x - 2, y + 46, 204, 18), 2)
            self._draw_text(surface, self.small_font, (bar_x + 4, y + 50),
                            f"Energia {int(player.energy)}% (volta ao Ben!)", danger)

    @staticmethod
    def _draw_text(surface, font, position, text, color=(255, 255, 255)) -> None:
        surface.blit(font.render(text, True, color), position)

    def _draw_alien_attacks(self, surface, player) -> None:
        """Mostra o poder primário e o especial do alien atual (com cooldown)."""
        data = settings.ALIEN_DATA[player.alien_name]
        attack = data["attack_z"]
        special = data["special"]
        center_x = surface.get_width() / 2

        # power-up que substitui o ataque (Minigun / Punhos x4)
        if "minigun" in player.powerups:
            attack_label = "Minigun (rajada contínua)"
            atk_cd, atk_total, atk_color = (player.primary_cd, 0.1, (255, 230, 120))
        elif "punhos_4x" in player.powerups:
            attack_label = "Punhos x4 (4 golpes/s)"
            atk_cd, atk_total, atk_color = (player.primary_cd, 0.25, (230, 90, 90))
        elif player.fusion:
            trait = settings.FUSION_TRAITS[player.fusion]
            attack_label = f"Fusão: +{player.fusion} ({trait['label']})"
            # cadência (traço do Ben) encurta o cooldown real — a barra reflete isso
            total = attack["cooldown"] if attack else 0.5
            if trait["kind"] == "cadence":
                total *= 0.65
            atk_cd, atk_total, atk_color = (player.primary_cd, total, trait["color"])
        elif attack is not None:
            attack_label = f"Clique: {attack['name']}"
            atk_cd, atk_total, atk_color = (player.primary_cd, attack["cooldown"], attack["color"])
        else:
            attack_label, atk_cd, atk_total, atk_color = "", 0.0, 1.0, (255, 255, 255)

        if attack_label:
            self._attack_bar(surface, center_x, surface.get_height() - 88,
                             attack_label, atk_cd, atk_total, atk_color)
        # o especial exibido: com fusão, o X vira a versão COMBINADA dos dois
        fusion_cfg = None
        if player.fusion:
            fusion_cfg = settings.FUSION_SPECIALS.get((player.alien_name, player.fusion))
        shown_special = fusion_cfg or special
        if shown_special is not None:
            venom_blocked = "traje_venom" in player.powerups
            if fusion_cfg:
                sp_color = settings.FUSION_TRAITS[player.fusion]["color"]
            else:
                sp_color = settings.COLORS["gold"]
            if venom_blocked:
                sp_color = settings.COLORS["purple"]
            label = f"X: {shown_special['name']}"
            if venom_blocked:
                label += " (VENOM bloqueia)"
            self._attack_bar(surface, center_x, surface.get_height() - 46,
                             label, player.special_cd,
                             shown_special["cooldown"], sp_color)

    def _draw_omnitrix_strip(self, surface, player, next_alien=None, mouse_pos=None) -> None:
        """Os 5 aliens do Omnitrix em faixa: o atual acende, o escolhido doura.

        Cada alien mostra o próprio retrato (sprite tingido na cor dele), deixando
        claro que QUALQUER um pode ser escolhido com a roda do mouse / , .
        O retrato sob o mouse ganha um ANEL DE PROGRESSO preenchendo no sentido
        horário — o hover de 3s transforma nele (seleção por permanência).
        """
        positions = self._strip_positions()
        hover_ratio = 0.0
        if settings.HOVER_TRANSFORM_ENABLED and self.hover_alien and self.hover_timer > 0:
            hover_ratio = min(1.0, self.hover_timer / settings.HOVER_TRANSFORM_TIME)
        for index, (name, x, y) in enumerate(positions):
            active = (name == player.alien_name)
            chosen = (name == next_alien)
            color = settings.ALIEN_DATA[name]["color"]
            # fundo do ícone + retrato do alien (sprite tingido)
            pygame.draw.circle(surface, (20, 20, 40), (x, y), 14)
            # indicação de que o hover está ativo (ajuda o jogador a entender
            # por que o anel está enchendo em volta de um retrato qualquer)
            if settings.HOVER_TRANSFORM_ENABLED and name == self.hover_alien \
                    and self.hover_timer > 0:
                pygame.draw.circle(surface, (255, 255, 255), (x, y), 12, 1)
            portrait = self.assets.get_player_image(name)
            if portrait is not None:
                thumb = pygame.transform.scale(portrait, (22, 22))
                if not (active or chosen):
                    # escurece sem apagar: multiplicar por cinza (preto zeraria tudo)
                    thumb = thumb.copy()
                    thumb.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_MULT)
                surface.blit(thumb, thumb.get_rect(center=(x, y)))
            else:
                letter = name[0].upper()
                letter_color = (255, 255, 255) if (active or chosen) else (190, 190, 210)
                text = self.small_font.render(letter, True, letter_color)
                surface.blit(text, text.get_rect(center=(x, y)))
            if active:
                pygame.draw.circle(surface, settings.COLORS["omnitrix_green"], (x, y), 14, 3)
            elif chosen:
                pygame.draw.circle(surface, settings.COLORS["gold"], (x, y), 14, 3)
            # anel de progresso do hover (enche no sentido horário)
            if hover_ratio > 0 and name == self.hover_alien:
                rect = pygame.Rect(x - 16, y - 16, 32, 32)
                start = -math.pi / 2
                end = start + 2 * math.pi * hover_ratio
                pygame.draw.arc(surface, settings.COLORS["omnitrix_green"],
                                rect, start, end, 3)
                if hover_ratio >= 1.0:
                    pygame.draw.circle(surface, settings.COLORS["gold"], (x, y), 17, 2)

    def _draw_prism(self, surface, player) -> None:
        """Barra de Energia Prisma (fusões) no canto superior direito."""
        width = 190
        x = surface.get_width() - width - 18
        y = 52
        ratio = player.prism / settings.PRISM_MAX
        full = ratio >= 1.0
        color = settings.COLORS["gold"] if full else (150, 120, 255)
        pygame.draw.rect(surface, (30, 30, 55), (x, y, width, 16), border_radius=6)
        if ratio > 0:
            pygame.draw.rect(surface, color, (x + 2, y + 2, max(3, int((width - 4) * ratio)), 12),
                             border_radius=5)
        self._draw_text(surface, self.small_font, (x, y - 16), "PRISMA", color)
        # status abaixo da barra: fusão ativa ou pronta (parceiro sorteado)
        if player.fusion:
            trait = settings.FUSION_TRAITS[player.fusion]
            self._draw_text(surface, self.small_font, (x, y + 20),
                            f"FUSÃO: +{player.fusion} {player.fusion_timer:.0f}s",
                            trait["color"])
        elif full and player.fusion_partner:
            self._draw_text(surface, self.small_font, (x, y + 20),
                            f"PRISMA CHEIA — Fusão: + {player.fusion_partner} (F)",
                            settings.COLORS["gold"])
        elif full:
            self._draw_text(surface, self.small_font, (x, y + 20),
                            "PRISMA CHEIA — pressione F", settings.COLORS["gold"])

    def _draw_powerups(self, surface, player) -> None:
        """Ícones dos power-ups ativos com contagem regressiva (círculo esvaziando).

        O ícone tem uma animação de ENTRADA (~150ms crescendo de 0 a 100%) para
        o jogador perceber que algo novo surgiu — nada de "piscar" instantâneo.
        """
        x = surface.get_width() - 30
        y = 96
        for key in list(player.powerups)[:8]:
            data = settings.POWERUP_DATA.get(key, {})
            color = settings.RARITY_COLORS.get(data.get("rarity", "common"), (255, 255, 255))
            total = data.get("duration", 1.0) or 1.0
            remaining = max(0.0, player.powerups[key])
            # animação de entrada: idade = quanto tempo o efeito já está ativo.
            # entry começa em ~0 no frame de coleta mas o ícone já aparece (com
            # tamanho mínimo) — nada de pular o primeiro frame inteiro.
            age = max(0.0, total - remaining)
            entry = min(1.0, 0.15 + age / settings.POWERUP_ICON_ENTRY)
            pygame.draw.circle(surface, (20, 20, 40), (x, y), 11)
            pygame.draw.circle(surface, color, (x, y), 11, 2)
            # arco de contagem (esvazia no sentido horário)
            rect = pygame.Rect(x - 11, y - 11, 22, 22)
            if total > 0:
                start = -math.pi / 2
                end = start + 2 * math.pi * (remaining / total)
                pygame.draw.arc(surface, color, rect, start, end, 3)
            # ícone de sprite do power-up cresce na entrada (fallback: letra)
            icon = self._powerup_icon(data)
            if icon is not None:
                size = max(3, int(18 * (0.3 + 0.7 * entry)))
                icon = pygame.transform.scale(icon, (size, size))
                surface.blit(icon, icon.get_rect(center=(x, y)))
            else:
                letter = data.get("name", "?")[0].upper()
                self._draw_text(surface, self.small_font, (x - 5, y - 10), letter, color)
            # nome do power-up persistente (fica visível enquanto o efeito durar)
            name = data.get("name", "?")
            rendered = self.small_font.render(name, True, color)
            rendered.set_alpha(int(255 * entry))
            surface.blit(rendered, rendered.get_rect(right=x - 15, centery=y))
            y += 26

    def _powerup_icon(self, data: dict):
        """Resolve o sprite do ícone de um power-up (data['icon'] ou None).

        "ui:xxx" busca em assets de UI, "item:xxx" nas pixel arts de itens
        (cozinha, poção, arruela...) e qualquer outra chave nos efeitos.
        """
        return self.assets.resolve_icon(data.get("icon"))

    def _draw_combo(self, surface, player) -> None:
        """Contador de combo (Golpe Triplo) ao lado do cronômetro."""
        if player.combo_bonus_ready:
            text = self.font.render("COMBO PRONTO! +50%", True, settings.COLORS["gold"])
            surface.blit(text, text.get_rect(center=(surface.get_width() / 2 - 110, 24)))
        elif player.combo_count >= 2:
            text = self.font.render(f"x{player.combo_count}", True, (255, 220, 120))
            surface.blit(text, text.get_rect(center=(surface.get_width() / 2 - 110, 24)))

    # ------------------------------------------------------------------
    # Painel de atributos (TAB segurado)
    # ------------------------------------------------------------------
    def _draw_stats_panel(self, surface, player) -> None:
        """Painel lateral com os atributos consolidados do personagem.

        Mostra dano (base + todos os multiplicadores somados, bônus em ouro),
        velocidade atual, HP, energia com tempo restante de transformação e o
        status completo da fusão (Prisma, parceiro, traço, ressaca).
        """
        panel_w = 320
        panel_x = surface.get_width() - panel_w - 14
        panel_y = 22
        panel = pygame.Surface((panel_w, 268), pygame.SRCALPHA)
        panel.fill((12, 14, 28, 235))
        surface.blit(panel, (panel_x, panel_y))
        pygame.draw.rect(surface, settings.COLORS["omnitrix_green"],
                         (panel_x, panel_y, panel_w, 268), 2, border_radius=8)

        title = self.small_font.render("ATRIBUTOS", True,
                                       settings.COLORS["omnitrix_green"])
        surface.blit(title, (panel_x + 12, panel_y + 8))
        y = panel_y + 30
        gold = settings.COLORS["gold"]

        # --- Dano consolidado: base do alien + upgrades + power-ups + fusão ---
        data = settings.ALIEN_DATA[player.alien_name]
        attack = data["attack_z"]
        special = data["special"]
        base = (attack["damage"] if attack else 0.0) + player.base_damage
        base *= data["stats"]["damage_mult"]
        # multiplicadores % (upgrades de dano + power-ups) e o bônus FIXO da
        # Força Bruta da fusão (espelha o cálculo do world.attack)
        percent = player.damage_percent * player.powerup_damage_mult()
        impact_bonus = 0.0
        if player.fusion and settings.FUSION_TRAITS[player.fusion]["kind"] == "impact":
            impact_bonus = 1.5 * player.damage_percent
        total = base * percent + impact_bonus
        if attack:
            self._draw_text(surface, self.small_font, (panel_x + 12, y),
                            f"Dano: {total:.1f}")
            if percent > 1.01 or impact_bonus > 0.01:
                bonus_parts = []
                if percent > 1.01:
                    bonus_parts.append(f"×{percent:.2f}")
                if impact_bonus > 0.01:
                    bonus_parts.append(f"+{impact_bonus:.1f} Força Bruta")
                self._draw_text(surface, self.small_font, (panel_x + 12 + 96, y),
                                f"({base:.1f} {' '.join(bonus_parts)} ⇡)", gold)
            y += 20

        # --- Velocidade atual ---
        speed = player.effective_max_speed()
        self._draw_text(surface, self.small_font, (panel_x + 12, y),
                        f"Velocidade: {speed:.0f} px/s")
        y += 20

        # --- Vida ---
        self._draw_text(surface, self.small_font, (panel_x + 12, y),
                        f"Vida: {max(0, int(player.health))}/{player.max_health}")
        y += 20

        # --- Energia + tempo restante de transformação ---
        if player.alien_name != "Ben":
            seconds = player.energy / settings.ENERGY_DRAIN_PER_SECOND
            self._draw_text(surface, self.small_font, (panel_x + 12, y),
                            f"Energia: {int(player.energy)}%  ({seconds:.0f}s restantes)")
        else:
            boost = " (boost ativo!)" if player.energy_boost_timer > 0 else ""
            self._draw_text(surface, self.small_font, (panel_x + 12, y),
                            f"Energia: recarregando{boost}")
        y += 20

        # --- Status da fusão ---
        prism_ratio = player.prism / settings.PRISM_MAX
        if player.fusion:
            trait_data = settings.FUSION_TRAITS[player.fusion]
            special_cfg = settings.FUSION_SPECIALS.get((player.alien_name, player.fusion))
            self._draw_text(surface, self.small_font, (panel_x + 12, y),
                            f"FUSÃO: +{player.fusion} ({trait_data['label']})",
                            trait_data["color"])
            y += 18
            if special_cfg:
                self._draw_text(surface, self.small_font, (panel_x + 12, y),
                                f"  Especial: {special_cfg['name']}",
                                trait_data["color"])
                y += 18
            self._draw_text(surface, self.small_font, (panel_x + 12, y),
                            f"  {player.fusion_timer:.1f}s restantes")
            y += 18
        else:
            if prism_ratio >= 1.0:
                if player.fusion_partner:
                    self._draw_text(surface, self.small_font, (panel_x + 12, y),
                                    f"PRISMA CHEIA — F para fundir +{player.fusion_partner}",
                                    settings.COLORS["gold"])
                else:
                    self._draw_text(surface, self.small_font, (panel_x + 12, y),
                                    "PRISMA CHEIA — pressione F", settings.COLORS["gold"])
            else:
                self._draw_text(surface, self.small_font, (panel_x + 12, y),
                                f"Prisma: {int(prism_ratio * 100)}%")
            y += 20

        # --- Ressaca (se ativa) ---
        if player.hangover_timer > 0:
            self._draw_text(surface, self.small_font, (panel_x + 12, y),
                            f"Ressaca: -{(1 - player.hangover_speed) * 100:.0f}% vel "
                            f"({player.hangover_timer:.1f}s)",
                            (255, 140, 140))
            y += 20

        # --- Especial do alien atual ---
        if special:
            cd_left = max(0.0, player.special_cd)
            self._draw_text(surface, self.small_font, (panel_x + 12, y),
                            f"Especial {special['name']}: {'pronto' if cd_left <= 0 else f'{cd_left:.1f}s'}")

    def _attack_bar(self, surface, center_x, y, label, remaining, total, color) -> None:
        """Caixa com o nome do poder e uma barrinha de recarga que se enche."""
        box = Rect(center_x - 170, y, 340, 38)
        pygame.draw.rect(surface, (30, 30, 55), box, border_radius=8)
        pygame.draw.rect(surface, color, box, width=2, border_radius=8)
        self._draw_text(surface, self.small_font, (box.x + 10, box.y + 4), label)
        # barra de recarga embaixo: cheia enquanto o cooldown está rolando
        pygame.draw.rect(surface, (10, 10, 20), (box.x + 10, box.y + 24, box.width - 20, 8),
                         border_radius=4)
        if total > 0:
            fill = int((box.width - 20) * max(0.0, min(1.0, remaining / total)))
            pygame.draw.rect(surface, color, (box.x + 10, box.y + 24, fill, 8), border_radius=4)

    def _draw_counters(self, surface, kills, elapsed, alien_name, next_alien=None) -> None:
        """Cronômetro no topo e contador de abates à direita."""
        minutes = int(elapsed) // 60
        seconds = int(elapsed) % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        rendered = self.font.render(time_text, True, (255, 255, 255))
        surface.blit(rendered, rendered.get_rect(center=(surface.get_width() / 2, 24)))

        kills_text = self.font.render(f"Abates: {kills}", True, (255, 255, 255))
        surface.blit(kills_text, kills_text.get_rect(topright=(surface.get_width() - 18, 18)))

        # linha central: mostra a forma atual e qual alien está escolhido no
        # Omnitrix (também ensina o comando quando ainda não escolheu)
        center_x = surface.get_width() / 2
        if next_alien is None:
            hint = self.small_font.render(
                f"Forma: {alien_name}  —  escolha o próximo com , / . ou a roda do mouse",
                True, settings.COLORS["gold"])
        else:
            hint = self.small_font.render(
                f"Forma: {alien_name}  ->  {next_alien}  (ENTER p/ transformar)",
                True, settings.COLORS["omnitrix_green"])
        # y=92 fica abaixo das barras de vida/XP/energia (que terminam em ~82)
        surface.blit(hint, hint.get_rect(center=(center_x, 92)))

    # ------------------------------------------------------------------
    # Anúncios arcade (power-ups ativados)
    # ------------------------------------------------------------------
    def draw_announcements(self, surface, announcements) -> None:
        """Texto grande estilo arcade quando um power-up é ativado."""
        for announcement in announcements:
            text = announcement.get("text", "")
            rarity = announcement.get("rarity", "common")
            timer = announcement.get("timer", 1.0)
            max_timer = announcement.get("max_timer", 1.0)
            color = settings.RARITY_COLORS.get(rarity, (255, 255, 255))
            progress = 1 - timer / max_timer   # 0 -> 1
            # leve zoom-in nos primeiros 15%
            scale = 0.8 + 0.25 * min(1.0, progress / 0.15)
            font = pygame.font.Font(None, int(56 * scale))
            rendered = font.render(text, True, color)
            alpha = 255
            if timer < 0.4:
                alpha = int(255 * timer / 0.4)
            rendered.set_alpha(alpha)
            center = (surface.get_width() / 2, surface.get_height() / 2 - 40)
            # sombra para legibilidade
            shadow = font.render(text, True, (0, 0, 0))
            shadow.set_alpha(alpha)
            surface.blit(shadow, shadow.get_rect(center=(center[0] + 3, center[1] + 3)))
            surface.blit(rendered, rendered.get_rect(center=center))

    # ------------------------------------------------------------------
    # Crosshair
    # ------------------------------------------------------------------
    def draw_crosshair(self, surface, position, weapon_color) -> None:
        center = Vector2(position)
        # círculo externo com quatros traços, gira lentamente
        angle = pygame.time.get_ticks() / 1000
        pygame.draw.circle(surface, weapon_color, center, 14, 2)
        for offset in (0, 90, 180, 270):
            direction = Vector2(1, 0).rotate(offset + angle * 20)
            start = center + direction * 8
            end = center + direction * 18
            pygame.draw.line(surface, weapon_color, start, end, 2)
        pygame.draw.circle(surface, weapon_color, center, 3)

    # ------------------------------------------------------------------
    # Menus
    # ------------------------------------------------------------------
    def draw_title(self, surface, assets, mode="arena", scores=None) -> None:
        self._fill_background(surface)
        title = self.title_font.render(settings.GAME_TITLE, True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(surface.get_width() / 2, 120)))

        controls = [
            "WASD / Setas .......... mover",
            "Mouse ................ mirar (o personagem gira para o cursor)",
            "Clique esq. (segurar) . poder do alien atual",
            "X .................... habilidade especial do alien",
            "F .................... ativar fusão (recarrega 100% de energia)",
            "SHIFT ................ dash na direção do movimento (ou da mira se parado)",
            ", / . ou roda do mouse . escolher alien no Omnitrix",
            "ENTER ................ transformar no alien escolhido",
            "HOVER 3s ............. parar o mouse no retrato transforma (H liga/desliga)",
            "TAB (segurar) ........ painel de atributos detalhados",
            "ESC .................. pausar",
            "",
            "Pegue Núcleos Instáveis: cada cor é uma raridade!",
        ]
        for index, line in enumerate(controls):
            rendered = self.font.render(line, True, (230, 230, 240))
            surface.blit(rendered, rendered.get_rect(
                center=(surface.get_width() / 2, 228 + index * 26)))

        # seleção de modos
        mode_y = 228 + len(controls) * 26 + 12
        label = self.font.render("MODO DE JOGO (1/2/3):", True, settings.COLORS["gold"])
        surface.blit(label, label.get_rect(center=(surface.get_width() / 2, mode_y)))
        for index, (key, name, desc) in enumerate(settings.GAME_MODES):
            active = (key == mode)
            color = settings.COLORS["omnitrix_green"] if active else (200, 200, 210)
            line = f"[{index + 1}] {name} — {desc}" + ("  <=" if active else "")
            rendered = self.font.render(line, True, color)
            surface.blit(rendered, rendered.get_rect(
                center=(surface.get_width() / 2, mode_y + 28 + index * 26)))

        # recordes da Arena (máx. 4 linhas para caber em 768px)
        if scores:
            y = mode_y + 28 + 3 * 26 + 18
            head = self.small_font.render("MELHORES MARCAS (Arena)", True,
                                          settings.COLORS["omnitrix_green"])
            surface.blit(head, head.get_rect(center=(surface.get_width() / 2, y)))
            for index, record in enumerate(scores[:4]):
                line = f"{index + 1}. {record['time']:.0f}s • {record['kills']} abates"
                rendered = self.small_font.render(line, True, (220, 220, 230))
                surface.blit(rendered, rendered.get_rect(
                    center=(surface.get_width() / 2, y + 22 + index * 19)))

    def draw_level_up(self, surface, options, option_rects) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        title = self.title_font.render("NOVO NÍVEL!", True, settings.COLORS["gold"])
        surface.blit(title, title.get_rect(center=(surface.get_width() / 2, 180)))

        for index, option in enumerate(options):
            rect = option_rects[index]
            pygame.draw.rect(surface, (40, 40, 70), rect, border_radius=12)
            pygame.draw.rect(surface, settings.COLORS["gold"], rect, width=2, border_radius=12)
            title = self.font.render(f"[{index + 1}] {option['title']}", True, (255, 255, 255))
            surface.blit(title, (rect.x + 20, rect.y + 16))
            description = self.small_font.render(option["desc"], True, (200, 200, 210))
            surface.blit(description, (rect.x + 20, rect.y + 46))

    def draw_game_over(self, surface, kills, elapsed, level, scores=None, new_record=False) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))
        title = self.title_font.render("GAME OVER", True, settings.COLORS["damage_red"])
        surface.blit(title, title.get_rect(center=(surface.get_width() / 2, 160)))

        lines = [
            f"Tempo sobrevivido: {int(elapsed) // 60:02d}:{int(elapsed) % 60:02d}",
            f"Inimigos derrotados: {kills}",
            f"Nível alcançado: {level}",
        ]
        for index, line in enumerate(lines):
            rendered = self.font.render(line, True, (255, 255, 255))
            surface.blit(rendered, rendered.get_rect(center=(surface.get_width() / 2, 240 + index * 40)))

        if new_record:
            rec = self.font.render("★ NOVO RECORDE! ★", True, settings.COLORS["gold"])
            surface.blit(rec, rec.get_rect(center=(surface.get_width() / 2, 380)))

        if scores:
            y = 430
            head = self.small_font.render("MELHORES MARCAS", True,
                                          settings.COLORS["omnitrix_green"])
            surface.blit(head, head.get_rect(center=(surface.get_width() / 2, y)))
            for index, record in enumerate(scores[:5]):
                line = f"{index + 1}. {record['time']:.0f}s • {record['kills']} abates"
                rendered = self.small_font.render(line, True, (220, 220, 230))
                surface.blit(rendered, rendered.get_rect(
                    center=(surface.get_width() / 2, y + 26 + index * 22)))

        hint = self.font.render("Pressione R para reiniciar", True, (255, 255, 255))
        surface.blit(hint, hint.get_rect(center=(surface.get_width() / 2, 570)))

    def draw_pause(self, surface) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))
        text = self.font.render("PAUSADO — ESC para continuar", True, (255, 255, 255))
        surface.blit(text, text.get_rect(center=(surface.get_width() / 2, surface.get_height() / 2)))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _fill_background(self, surface) -> None:
        """Fundo em gradiente roxo (usado nas telas de menu)."""
        for y in range(0, surface.get_height(), 20):
            ratio = y / surface.get_height()
            color = _lerp_color(settings.COLORS["bg_top"], settings.COLORS["bg_bottom"], ratio)
            pygame.draw.rect(surface, color, (0, y, surface.get_width(), 20))

    def _bar(self, surface, x, y, width, height, ratio, fill_color, bg_color) -> None:
        pygame.draw.rect(surface, bg_color, (x, y, width, height))
        if ratio > 0:
            pygame.draw.rect(surface, fill_color, (x, y, max(2, int(width * ratio)), height))


def _lerp_color(color_a, color_b, ratio):
    return tuple(int(a + (b - a) * ratio) for a, b in zip(color_a, color_b))
