"""
entities.py — Entidades do jogo: jogador, inimigos, orbes, baús e projéteis.

Cada classe cuida do próprio estado e movimento. A colisão e o dano são
orquestrados pelo World (world.py), que sabe quem pode bater em quem.
"""
import math
import random

import pygame
from pygame import Rect, Vector2

from . import settings


def clamp(value, low, high):
    return max(low, min(high, value))


# ===========================================================================
# Jogador
# ===========================================================================
class Player:
    """O herói controlado pelo teclado (movimento) e pelo mouse (mira)."""

    def __init__(self, assets):
        self.assets = assets
        self.reset()

    # ------------------------------------------------------------------
    # Estado inicial
    # ------------------------------------------------------------------
    def reset(self):
        center = Vector2(settings.WORLD_WIDTH / 2, settings.WORLD_HEIGHT / 2)
        self.pos = Vector2(center)           # centro do jogador no mundo
        self.vel = Vector2(0, 0)             # velocidade atual (px/s)
        self.aim_dir = Vector2(1, 0)         # direção da mira (mouse)

        self.base_max_health = settings.PLAYER_BASE_MAX_HEALTH
        self.health = self.base_max_health
        self.base_damage = 0                 # bônus fixo de dano dos upgrades
        self.damage_percent = 1.0            # multiplicador % de dano (upgrades)
        self.speed_mult = 1.0
        self.cooldown_mult = 1.0

        self.level = 1
        self.xp = 0

        self.alien_name = "Ben"
        self.energy = settings.ENERGY_MAX

        # Estado de movimento especial (dash, pulo, turbo)
        self.state = "normal"                # normal | dash | jump | boost
        self.state_timer = 0.0
        self.dash_dir = Vector2(1, 0)
        self.jump_target = Vector2()
        self.boost_timer = 0.0

        self.invincible_until = 0.0          # tempo (s) até ficar vulnerável
        self._dash_ready_at = 0.0            # cooldown do dash (resetado no restart)
        self.primary_cd = 0.0                # cooldown restante do ataque primário (clique)
        self.special_cd = 0.0                # cooldown restante do especial (X)
        self.events: list[str] = []          # eventos do frame (ex.: "jump_landed")
        # --- Grito do Omnitrix (especial do Ben): recarga de energia acelerada ---
        self.energy_boost_timer = 0.0        # segundos restantes do boost de recarga
        # --- Pancada carregada do Quatro Braços ---
        # Segurar o clique acumula charge (0..SMASH_CHARGE_TIME); a pancada usa
        # e zera. O World lê e reseta; o Game acumula enquanto segura o botão.
        self.smash_charge = 0.0

        # --- Fase 2: energia Prisma, fusões e power-ups ---
        self.prism = 0.0                     # barra de fusão (0..PRISM_MAX)
        self.fusion: str | None = None       # fusão ativa (nome do alien parceiro)
        self.fusion_partner: str | None = None  # parceiro sorteado (p/ ativar com F)
        self.fusion_timer = 0.0
        self.powerups: dict[str, float] = {} # power-up ativo -> segundos restantes
        self.shield_charges = 0              # Escudo Petrossápien (bloqueios)
        self.hangover_timer = 0.0            # ressaca pós-fusão / pós-Venom
        self.hangover_speed = 0.85           # multiplicador de velocidade da ressaca
        self.combo_count = 0                 # golpes na janela de combo
        self.combo_timer = 0.0
        self.combo_bonus_ready = False       # próximo golpe primário +50%
        self.last_form_change = -99.0        # p/ Troca Relâmpago (crítico)
        self.last_attack_alien: str | None = None  # p/ Combo Elemental
        self.last_attack_time = -99.0        # p/ Combo Elemental
        # --- Estados dos ESPECIAIS de fusão (X vira versão combinada) ---
        self.rush_dir = Vector2(1, 0)        # Investida Relâmpago (Ben+XLR8)
        self.rush_damage = 0.0               # dano por inimigo na investida
        self.rush_hit_ids: set[int] = set()  # inimigos já atingidos na investida
        self.gauntlets_timer = 0.0           # Manoplas de Cristal (Ben+Diamante)
        self.gauntlets_damage = 0.0
        self.double_jump_ready = False       # Pulmão Duplo (Quatro Braços+Ben)
        self.jump_barrage_stage = 0          # Saraivada de Pulmão (QB+XLR8)
        self.fusion_jump_cfg = None          # cfg do pulo de fusão ativo (p/ pouso)
        self.update_alien_stats()

    # ------------------------------------------------------------------
    # Estatísticas derivadas do alien atual
    # ------------------------------------------------------------------
    def update_alien_stats(self):
        stats = settings.ALIEN_DATA[self.alien_name]["stats"]
        self.max_health = int(self.base_max_health * stats["health_mult"])
        self.max_speed = settings.PLAYER_BASE_SPEED * self.speed_mult * stats["speed_mult"]
        if self.state == "boost":
            self.max_speed *= settings.ALIEN_DATA["XLR8"]["special"]["speed_mult"]
        self.health = min(self.health, self.max_health)

    # ------------------------------------------------------------------
    # Power-ups e fusões (Fase 2)
    # ------------------------------------------------------------------
    def powerup_mods(self) -> tuple[float, float, float]:
        """Retorna (velocidade, dano, cadência) multiplicadores dos power-ups."""
        speed = 1.0
        damage = 1.0
        fire_rate = 1.0
        for key in self.powerups:
            data = settings.POWERUP_DATA.get(key, {})
            kind = data.get("kind")
            if kind == "speed":
                speed *= data.get("speed_mult", 1.0)
            elif kind == "waybig":
                damage *= data.get("damage_mult", 1.0)
                speed *= data.get("speed_mult", 1.0)
            elif kind == "venom":
                mult = data.get("mult", 1.0)
                speed *= mult
                damage *= mult
                fire_rate *= mult
            elif kind == "waybig_fury":
                damage *= data.get("damage_mult", 1.0)
        if self.hangover_timer > 0:          # ressaca: -15% (fusão) / -20% (Venom)
            speed *= self.hangover_speed
        return speed, damage, fire_rate

    def powerup_speed_mult(self) -> float:
        return self.powerup_mods()[0]

    def powerup_damage_mult(self) -> float:
        return self.powerup_mods()[1]

    def powerup_fire_rate_mult(self) -> float:
        return self.powerup_mods()[2]

    def magnet_mult(self) -> float:
        """Multiplicador do raio de coleta (Ímã de Orbes Turbo)."""
        if "ima_turbo" in self.powerups:
            return settings.POWERUP_DATA["ima_turbo"]["mult"]
        return 1.0

    def lifesteal(self) -> float:
        """Fração do dano que volta como vida (Sanguessuga / Fome Voraz)."""
        total = 0.0
        for key in self.powerups:
            data = settings.POWERUP_DATA.get(key, {})
            if data.get("kind") == "lifesteal":
                total += data.get("frac", 0.0)
        return total

    def add_prism(self, amount: float) -> None:
        was_full = self.prism >= settings.PRISM_MAX
        self.prism = min(settings.PRISM_MAX, self.prism + amount)
        # quando a barra enche, sorteia o parceiro da fusão (mostrado no HUD)
        if not was_full and self.prism >= settings.PRISM_MAX and not self.fusion_partner:
            self.fusion_partner = self._draw_fusion_partner()

    def _draw_fusion_partner(self) -> str:
        """Sorteia o alien parceiro da fusão — NUNCA o alien ativo.

        A graça da fusão é fundir dois poderes DIFERENTES: são 5 bases x 4
        parceiros = 20 combinações, sem repetição.
        """
        options = [name for name in settings.ALIEN_ORDER if name != self.alien_name]
        return random.choice(options)

    def start_fusion(self, partner: str) -> None:
        """Ativa a fusão do Omnitrix: o parceiro empresta o traço dele.

        O alien atual não troca de corpo — só ganha o comportamento do traço
        no ataque primário enquanto durar a fusão. A fusão também RECARREGA
        100% da energia na ativação: vira ferramenta de gestão de energia
        (ficar transformado por mais tempo), com a ressaca como contrapeso.
        """
        self.fusion = partner
        self.fusion_partner = None
        self.fusion_timer = settings.FUSION_DURATION
        self.prism = 0.0
        if settings.FUSION_RESTORES_ENERGY:
            self.energy = settings.ENERGY_MAX

    # ------------------------------------------------------------------
    # Mira e movimento
    # ------------------------------------------------------------------
    def aim_towards(self, world_position) -> None:
        """Aponta o personagem para a posição do mouse no mundo."""
        delta = Vector2(world_position) - self.pos
        if delta.length_squared() > 1:
            self.aim_dir = delta.normalize()

    def update(self, dt: float, input_vec: Vector2) -> None:
        """Movimentação suave com aceleração e atrito (FPS-independente)."""
        self.state_timer = max(0.0, self.state_timer - dt)
        self.boost_timer = max(0.0, self.boost_timer - dt)
        self.primary_cd = max(0.0, self.primary_cd - dt)
        self.special_cd = max(0.0, self.special_cd - dt)
        if self.gauntlets_timer > 0:
            self.gauntlets_timer = max(0.0, self.gauntlets_timer - dt)
        if self.energy_boost_timer > 0:
            self.energy_boost_timer = max(0.0, self.energy_boost_timer - dt)
        self._update_powerups(dt)
        self._update_fusion(dt)
        self._update_combo(dt)

        if self.state == "dash":
            self._move_along(self.dash_dir, settings.DASH_SPEED, dt)
            if self.state_timer <= 0:
                self.state = "normal"

        elif self.state == "rush":
            # Investida Relâmpago (Ben+XLR8): avança reto e invencível
            self._move_along(self.rush_dir, settings.DASH_SPEED * 1.15, dt)
            if self.state_timer <= 0:
                self.state = "normal"

        elif self.state == "jump":
            self._move_along(self.jump_target - self.pos, 650.0, dt)
            if self.pos.distance_to(self.jump_target) < 12:
                self.state = "normal"
                self.events.append("jump_landed")

        elif self.state == "boost":
            self._move_along(input_vec, self.max_speed, dt)
            if self.boost_timer <= 0:
                self.state = "normal"
                self.invincible_until = 0.0   # volta a ser vulnerável
                self.update_alien_stats()
                self.events.append("boost_ended")

        else:  # controle normal
            if input_vec.length_squared() > 0:
                input_vec = input_vec.normalize()
            # acelera em direção à entrada, aplica atrito exponencial
            self.vel += input_vec * settings.PLAYER_ACCELERATION * dt
            self.vel *= math.exp(-settings.PLAYER_FRICTION * dt)
            if self.vel.length() > self.effective_max_speed():
                self.vel.scale_to_length(self.effective_max_speed())
            self.pos += self.vel * dt

        self._clamp_to_world()

    def _move_along(self, direction: Vector2, speed: float, dt: float) -> None:
        if direction.length_squared() > 1:
            direction = direction.normalize()
        self.pos += direction * speed * dt

    def effective_max_speed(self) -> float:
        """Velocidade máxima considerando power-ups (Botas, Venom, Way Big...)."""
        return self.max_speed * self.powerup_speed_mult()

    def _clamp_to_world(self) -> None:
        half = settings.PLAYER_SIZE / 2
        self.pos.x = clamp(self.pos.x, half, settings.WORLD_WIDTH - half)
        self.pos.y = clamp(self.pos.y, half, settings.WORLD_HEIGHT - half)

    def _update_powerups(self, dt: float) -> None:
        """Diminui os temporizadores dos power-ups ativos."""
        for key in list(self.powerups):
            self.powerups[key] -= dt
            if self.powerups[key] <= 0:
                del self.powerups[key]
                # Traje Venom termina com "ressaca" (-20% velocidade por 3s)
                if key == "traje_venom":
                    self.hangover_timer = max(
                        self.hangover_timer,
                        settings.POWERUP_DATA["traje_venom"].get("hangover", 3.0))
                    self.hangover_speed = 0.8
        if self.hangover_timer > 0:
            self.hangover_timer = max(0.0, self.hangover_timer - dt)
        # regeneração do Coração de Ben
        if "coracao_de_ben" in self.powerups:
            regen = settings.POWERUP_DATA["coracao_de_ben"].get("regen_pct", 0.01)
            self.health = min(self.max_health, self.health + self.max_health * regen * dt)

    def _update_fusion(self, dt: float) -> None:
        if self.fusion and self.fusion_timer > 0:
            self.fusion_timer -= dt
            if self.fusion_timer <= 0:
                self.fusion = None
                self.fusion_partner = None
                # limpa estados dos especiais de fusão (Manoplas, Pulmão Duplo...)
                self.gauntlets_timer = 0.0
                self.double_jump_ready = False
                self.jump_barrage_stage = 0
                self.fusion_jump_cfg = None
                # ressaca universal: qualquer fusão termina com -15% velocidade
                self.hangover_timer = max(self.hangover_timer, settings.FUSION_HANGOVER)
                # mantém a ressaca mais restritiva (0.8 do Venom) se estiver ativa
                self.hangover_speed = min(self.hangover_speed,
                                          settings.FUSION_HANGOVER_SLOW)
                self.events.append("fusion_ended")

    def _update_combo(self, dt: float) -> None:
        """Golpe Triplo: 3 acertos em 1,5s liberam +50% no próximo golpe."""
        if self.combo_count > 0 or self.combo_bonus_ready:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_count = 0
                self.combo_bonus_ready = False

    # ------------------------------------------------------------------
    # Combate
    # ------------------------------------------------------------------
    def take_damage(self, amount: float, now: float) -> bool:
        """Aplica dano se não estiver invencível. Retorna True se acertou."""
        if now < self.invincible_until:
            return False
        # Escudo Petrossápien bloqueia o golpe inteiro (e some)
        if self.shield_charges > 0:
            self.shield_charges -= 1
            self.invincible_until = now + settings.INVULNERABILITY_DURATION
            self.events.append("shield_blocked")
            return False
        # Passivo de fusão (terceira camada): Ben+Chama reduz o dano recebido
        # enquanto fundido ("pegando fogo mas controlando").
        if self.fusion:
            passive = settings.FUSION_PASSIVES.get((self.alien_name, self.fusion))
            if passive and passive.get("kind") == "damage_reduce":
                amount *= passive.get("mult", 1.0)
        self.health -= amount
        self.invincible_until = now + settings.INVULNERABILITY_DURATION
        if self.health <= 0:
            self.health = 0
        return True

    def start_dash(self, now: float, move_dir=None) -> bool:
        """Inicia o dash na direção do MOVIMENTO (WASD/setas).

        Se o jogador estiver parado (sem input de movimento), o dash cai para
        a direção da mira — nunca "corre na direção de nada".
        Retorna False se está em cooldown.
        """
        if self.state not in ("normal", "boost"):
            return False
        if now < getattr(self, "_dash_ready_at", 0.0):
            return False
        self._dash_ready_at = now + settings.DASH_COOLDOWN
        self.state = "dash"
        self.state_timer = settings.DASH_DURATION
        if move_dir is not None and move_dir.length_squared() > 0.01:
            self.dash_dir = Vector2(move_dir).normalize()   # direção do movimento
        else:
            # parado: fallback natural para a mira (não surpreende o jogador)
            self.dash_dir = self.aim_dir if self.aim_dir.length() > 0 else Vector2(1, 0)
        self.invincible_until = now + settings.DASH_INVULNERABILITY
        return True

    def start_jump(self, target: Vector2, now: float = 0.0) -> None:
        """Super Pulmão: salta até o alvo, invencível durante o salto."""
        self.state = "jump"
        self.jump_target = Vector2(target)
        if now > 0:
            self.invincible_until = now + 0.7

    def start_rush(self, direction: Vector2, distance: float, now: float = 0.0) -> None:
        """Investida Relâmpago (fusão Ben+XLR8): dash-ataque em linha reta.

        Avança na direção da mira perfurando tudo no caminho (o dano é
        aplicado pelo World, que verifica os inimigos na linha da investida).
        """
        self.state = "rush"
        self.rush_dir = Vector2(direction).normalize() if direction.length() > 0 else self.aim_dir
        self.rush_distance = distance          # alcance total da investida
        self.state_timer = distance / (settings.DASH_SPEED * 1.15)
        self.rush_hit_ids = set()
        if now > 0:
            self.invincible_until = now + self.state_timer + 0.1

    def primary_ready(self) -> bool:
        """True se o ataque primário do alien atual está pronto."""
        return self.primary_cd <= 0

    def special_ready(self) -> bool:
        """True se o especial (X) do alien atual está pronto."""
        return self.special_cd <= 0

    def start_boost(self, duration: float) -> None:
        self.state = "boost"
        self.boost_timer = duration
        self.invincible_until = self.boost_timer + 10 ** 9  # invencível durante o turbo
        self.update_alien_stats()

    # ------------------------------------------------------------------
    # Progressão
    # ------------------------------------------------------------------
    def add_xp(self, amount: float) -> bool:
        """Soma XP e retorna True se subiu de nível (pode subir mais de um)."""
        self.xp += amount
        leveled_up = False
        while self.xp >= settings.xp_needed(self.level):
            self.xp -= settings.xp_needed(self.level)
            self.level += 1
            leveled_up = True
        return leveled_up

    def increase_max_health(self, amount: int) -> None:
        self.base_max_health += amount
        self.update_alien_stats()
        self.health += amount

    def increase_max_health_percent(self, amount: float) -> None:
        """Vida máxima +X% (cura a diferença, como o upgrade fixo)."""
        old_max = self.max_health
        self.base_max_health = int(round(self.base_max_health * (1 + amount)))
        self.update_alien_stats()
        self.health = min(self.max_health, self.health + (self.max_health - old_max))

    def increase_speed(self, amount: float) -> None:
        self.speed_mult += amount
        self.update_alien_stats()

    def increase_base_damage(self, amount: float) -> None:
        self.base_damage += amount

    def increase_damage_percent(self, amount: float) -> None:
        """Todas as armas causam +X% de dano (acumulativo)."""
        self.damage_percent += amount

    def reduce_cooldowns(self, amount: float) -> None:
        self.cooldown_mult = max(0.1, self.cooldown_mult - amount)

    # ------------------------------------------------------------------
    # Omnitrix
    # ------------------------------------------------------------------
    def update_energy(self, dt: float) -> None:
        """Drena energia transformado, recarrega quando é o Ben.

        O Grito do Omnitrix acelera a recarga por alguns segundos (segunda
        "válvula de escape" além de voltar ao Ben): recarga até 2.5x enquanto
        o boost durar.
        """
        if self.alien_name != "Ben":
            self.energy = max(0.0, self.energy - settings.ENERGY_DRAIN_PER_SECOND * dt)
            if self.energy <= 0:
                self.change_form("Ben")
        else:
            recharge = settings.ENERGY_RECHARGE_PER_SECOND
            if self.energy_boost_timer > 0:
                recharge *= settings.OMNITRIX_ROAR_ENERGY_MULT
            self.energy = min(settings.ENERGY_MAX,
                              self.energy + recharge * dt)

    def change_form(self, new_name: str, now: float = -99.0) -> bool:
        """Troca de alien se houver energia suficiente. Retorna True se trocou.

        `now` alimenta o combo "Troca Relâmpago" (crítico se atacar rápido).
        """
        if new_name == self.alien_name:
            return False
        if new_name != "Ben" and self.energy < settings.ENERGY_COST_TO_TRANSFORM:
            return False
        # transformar de volta no Ben não custa energia
        if new_name != "Ben":
            self.energy = max(0.0, self.energy - settings.ENERGY_COST_TO_TRANSFORM)
        self.alien_name = new_name
        self.update_alien_stats()
        if now > 0:
            self.last_form_change = now
        return True

    # ------------------------------------------------------------------
    # Desenho
    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, world_offset, now: float) -> None:
        image = self.assets.get_player_image(self.alien_name)
        if now < self.invincible_until and self.state != "boost":
            # pisca enquanto invencível
            if int(now * 10) % 2 == 0:
                return
        # gira o sprite na direção da mira
        angle = -math.degrees(math.atan2(self.aim_dir.y, self.aim_dir.x))
        rotated = pygame.transform.rotate(image, angle)
        screen_pos = self.pos - world_offset
        # aura da fusão: anel pulsante na cor do traço + fragmentos orbitando
        if self.fusion:
            trait = settings.FUSION_TRAITS[self.fusion]
            pulse = 0.5 + 0.5 * math.sin(now * 9)
            radius = int(38 + pulse * 8)
            glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*trait["color"], 45), (radius, radius), radius)
            surface.blit(glow, glow.get_rect(center=screen_pos))
            pygame.draw.circle(surface, trait["color"], screen_pos, radius, 2)
            for index in range(5):
                orbit = now * 2.2 + index * (math.pi * 2 / 5)
                dot = screen_pos + Vector2(math.cos(orbit), math.sin(orbit)) * (radius + 9)
                pygame.draw.circle(surface, trait["color"], dot, 2)
        surface.blit(rotated, rotated.get_rect(center=screen_pos))

    @property
    def rect(self) -> Rect:
        """Retângulo de colisão aproximado (para colisões simples)."""
        half = settings.PLAYER_SIZE / 2 - 6
        return Rect(self.pos.x - half, self.pos.y - half, half * 2, half * 2)


# ===========================================================================
# Inimigos
# ===========================================================================
class Enemy:
    """Cavaleiro (ou caveira) que persegue o jogador até encostar."""

    def __init__(self, enemy_type: str, position: Vector2, scale: float = 1.0,
                 speed_mult: float = 1.0):
        data = settings.ENEMY_DATA[enemy_type]
        self.type = enemy_type
        self.size = data["size"]
        self.pos = Vector2(position)
        self.max_health = max(1, int(data["health"] * scale))
        self.health = self.max_health
        # velocidade separada da vida: começa suave e acelera aos poucos
        self.speed = data["speed"] * settings.ENEMY_SPEED_MULT * speed_mult
        self.damage = data["damage"]
        self.xp = data["xp"]
        self.hit_flash = 0.0
        self.knockback = Vector2(0, 0)
        # Fase 2: efeitos de status (power-ups e fusões)
        self.slow_timer = 0.0          # tempo restante de lentidão
        self.slow_mult = 1.0           # 0.6 = 40% mais lento
        self.frozen_timer = 0.0        # Congelamento em Massa: não se move
        self.weak_until = 0.0          # Fúria Final: -50% de vida máxima
        self.weak_original_max = self.max_health
        self.weak_applied = False
        # Atordoamento da Cadeia do XLR8: "reforçar" o mesmo alvo (3 acertos
        # dentro da janela) atordoa. Contador + timestamp do último acerto.
        self.chain_hits = 0
        self.last_chain_hit = -99.0

    def apply_damage(self, amount: float, knockback_dir: Vector2 | None = None,
                     knockback_strength: float = 0.0) -> None:
        self.health -= amount
        self.hit_flash = 0.08
        # evita normalizar vetor zero (inimigo exatamente em cima do jogador)
        if (knockback_dir is not None and knockback_strength > 0
                and knockback_dir.length_squared() > 1):
            self.knockback += knockback_dir.normalize() * knockback_strength

    def apply_slow(self, duration: float, slow_mult: float = 0.5) -> None:
        """Deixa o inimigo mais lento por um tempo (Fúria Congelante)."""
        self.slow_timer = max(self.slow_timer, duration)
        self.slow_mult = min(self.slow_mult, slow_mult)

    def apply_freeze(self, duration: float) -> None:
        self.frozen_timer = max(self.frozen_timer, duration)

    def apply_weak(self, hp_cut: float, duration: float) -> None:
        """Fúria Final: -50% de vida máxima temporariamente."""
        if self.weak_applied:
            return
        self.weak_applied = True
        self.weak_until = duration
        self.weak_original_max = self.max_health
        self.max_health = max(1, int(self.max_health * hp_cut))
        self.health = min(self.health, self.max_health)

    def update(self, dt: float, player_pos: Vector2, now: float = 0.0) -> None:
        self.hit_flash = max(0.0, self.hit_flash - dt)
        # recuo do knockback vai sumindo
        self.knockback *= math.exp(-8 * dt)
        self.pos += self.knockback * dt
        # timers de status
        self.slow_timer = max(0.0, self.slow_timer - dt)
        self.frozen_timer = max(0.0, self.frozen_timer - dt)
        if self.weak_applied:
            self.weak_until -= dt
            if self.weak_until <= 0:   # restaura a vida máxima original
                self.max_health = self.weak_original_max
                self.health = min(self.health, self.max_health)
                self.weak_applied = False
        # congelado: não persegue
        if self.frozen_timer > 0:
            return
        # persegue o jogador (com lentidão aplicada)
        to_player = player_pos - self.pos
        if to_player.length_squared() > 1:
            speed = self.speed * (self.slow_mult if self.slow_timer > 0 else 1.0)
            self.pos += to_player.normalize() * speed * dt

    def draw(self, surface: pygame.Surface, world_offset, assets) -> None:
        image = assets.get_enemy_image(self.type)
        if self.hit_flash > 0:
            image = image.copy()
            image.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
        surface.blit(image, image.get_rect(center=self.pos - world_offset))
        # barra de vida (só aparece quando ferido)
        if self.health < self.max_health:
            width = self.size[0]
            bar_y = self.pos.y - world_offset.y - self.size[1] / 2 - 10
            pygame.draw.rect(surface, settings.COLORS["health_dark"],
                             (self.pos.x - world_offset.x - width / 2, bar_y, width, 5))
            pygame.draw.rect(surface, settings.COLORS["health_green"],
                             (self.pos.x - world_offset.x - width / 2, bar_y,
                              width * (self.health / self.max_health), 5))

    @property
    def rect(self) -> Rect:
        return Rect(0, 0, self.size[0], self.size[1])
