"""
world.py — O "mundo vivo" do jogo: inimigos, projéteis, orbes e baús.

Aqui mora toda a lógica de combate: spawn de inimigos (horda crescente),
ataques apontados pelo mouse (corpo a corpo, projéteis e especiais dos aliens),
drops de XP com magnetismo (inspirado em 20 Minutes Till Dawn) e colisões.
"""
import math
import random

import pygame
from pygame import Rect, Vector2

from . import settings
from .entities import Enemy, Player


# ===========================================================================
# Banner arcade: tempo de leitura escala com o tamanho do nome
# ===========================================================================
def _banner_duration(text: str) -> float:
    """Tempo do banner cresce com o nome ("DASH!" fica pouco, nomes longos mais)."""
    return min(2.6, max(1.4, 1.1 + len(text) * 0.035))


# ===========================================================================
# Pequenos itens do cenário
# ===========================================================================
class XPOrb:
    """Orbe de XP que o inimigo solta e que atrai para o jogador (ímã)."""

    def __init__(self, position: Vector2, value: float):
        self.pos = Vector2(position)
        self.value = value
        self.magnet_radius = settings.XP_ORB_MAGNET_RADIUS

    def update(self, dt: float, player_pos: Vector2) -> bool:
        """Atrai para o jogador quando perto. Retorna True se foi coletado."""
        to_player = player_pos - self.pos
        distance = to_player.length()
        if distance < 22:
            return True
        if distance < self.magnet_radius:
            self.pos += to_player.normalize() * 360 * dt
        return False

    def draw(self, surface: pygame.Surface, world_offset) -> None:
        pos = self.pos - world_offset
        pygame.draw.circle(surface, settings.COLORS["xp_blue"], pos, 7)
        pygame.draw.circle(surface, (180, 220, 255), pos, 3)


class HealthOrb:
    """Comida que recupera 1 de vida (coxa de frango — comer cura!).

    Em vez do orbe verde genérico, o jogador coleta uma coxinha de frango
    (pixel art de power-up), com um brilho verde ao redor para ler como cura.
    """

    def __init__(self, position: Vector2):
        self.pos = Vector2(position)

    def update(self, dt: float, player_pos: Vector2) -> bool:
        to_player = player_pos - self.pos
        distance = to_player.length()
        if distance < 26:
            return True
        if distance < self.magnet_radius:
            self.pos += to_player.normalize() * 260 * dt
        return False

    @property
    def magnet_radius(self):
        return settings.XP_ORB_MAGNET_RADIUS

    def draw(self, surface: pygame.Surface, world_offset, assets=None) -> None:
        pos = self.pos - world_offset
        sprite = assets.get_item("chickendrumstick") if assets else None
        if sprite is not None:
            # brilho verde de cura ao redor da comida
            pygame.draw.circle(surface, (60, 220, 120), pos, 14, 2)
            surface.blit(sprite, sprite.get_rect(center=pos))
        else:
            pygame.draw.circle(surface, settings.COLORS["health_green"], pos, 8)
            pygame.draw.circle(surface, (200, 255, 220), pos, 4)


class Chest:
    """Baú mágico: leva dano dos seus ataques e solta orbes de vida."""

    def __init__(self, position: Vector2):
        self.pos = Vector2(position)
        self.health = settings.CHEST_HEALTH
        self.max_health = settings.CHEST_HEALTH
        self.hit_flash = 0.0

    def apply_damage(self, amount: float) -> None:
        self.health -= amount
        self.hit_flash = 0.08

    def update(self, dt: float) -> None:
        self.hit_flash = max(0.0, self.hit_flash - dt)

    def draw(self, surface: pygame.Surface, world_offset, assets) -> None:
        image = assets.get_ui("chest")
        if image is None:
            pygame.draw.rect(surface, settings.COLORS["gold"],
                             Rect(0, 0, 50, 50).move(self.pos - world_offset - Vector2(25, 25)))
        else:
            surface.blit(image, image.get_rect(center=self.pos - world_offset))
        if self.hit_flash > 0:
            pygame.draw.rect(surface, (255, 255, 255),
                             Rect(0, 0, 50, 50).move(self.pos - world_offset - Vector2(25, 25)),
                             width=3)

    @property
    def rect(self) -> Rect:
        return Rect(0, 0, settings.CHEST_SIZE, settings.CHEST_SIZE) \
            .move(self.pos - Vector2(settings.CHEST_SIZE / 2, settings.CHEST_SIZE / 2))


class PowerUp:
    """Núcleo Instável: power-up que pulsa, atrai para o jogador e ativa ao tocar.

    A cor do anel indica a raridade (comum / raro / épico / lendário) e o
    centro mostra a pixel art do item que ele dá (bateria, despertador,
    poção...) — leitura instantânea do que vai cair.
    """

    def __init__(self, position: Vector2, key: str):
        self.pos = Vector2(position)
        self.key = key
        self.rarity = settings.POWERUP_DATA[key]["rarity"]
        self.color = settings.RARITY_COLORS[self.rarity]
        self.pulse = random.uniform(0, 6.28)

    def update(self, dt: float, player_pos: Vector2, magnet_mult: float = 1.0) -> bool:
        """Atrai quando perto. Retorna True se foi coletado."""
        to_player = player_pos - self.pos
        distance = to_player.length()
        if distance < 26:
            return True
        if distance < settings.XP_ORB_MAGNET_RADIUS * magnet_mult:
            self.pos += to_player.normalize() * 320 * dt
        return False

    def _item_sprite(self, assets):
        """Resolve a pixel art do item para este power-up (mesmo resolve do HUD)."""
        icon_key = settings.POWERUP_DATA[self.key].get("icon")
        return assets.resolve_icon(icon_key)

    def draw(self, surface: pygame.Surface, world_offset, assets=None) -> None:
        pos = self.pos - world_offset
        radius = int(9 + math.sin(self.pulse) * 2)
        pygame.draw.circle(surface, self.color, pos, radius + 4, 2)
        sprite = self._item_sprite(assets) if assets else None
        if sprite is not None:
            # escala para caber no núcleo (~22px), independente do tamanho do
            # asset original (o castelo é 96px para a decoração do mapa)
            scaled = pygame.transform.smoothscale(sprite, (22, 22))
            surface.blit(scaled, scaled.get_rect(center=pos))
        else:
            pygame.draw.circle(surface, self.color, pos, radius)
            pygame.draw.circle(surface, (255, 255, 255), pos, 4)


class Projectile:
    """Projétil disparado na direção do mouse (Bola de Fogo / Estilhaço)."""

    def __init__(self, position: Vector2, direction: Vector2, attack: dict,
                 damage: float, assets):
        self.pos = Vector2(position)
        self.dir = direction.normalize() if direction.length() > 0 else Vector2(1, 0)
        self.speed = attack["speed"]
        self.max_range = attack["range"]
        self.traveled = 0.0
        self.damage = damage
        self.pierce = attack.get("pierce", 0)   # 0 = some ao atingir o 1º inimigo
        self.radius = attack.get("radius", 7)
        self.color = attack["color"]
        self.assets = assets
        self.explosion_radius = 0.0     # >0 faz o projétil explodir ao atingir
        self.explosion_damage = 0.0
        self.knockback = 60.0       # recuo ao atingir (traço Força Bruta aumenta)
        self.glow_color = None      # cor do traço da fusão (aura visual)
        self.hit_ids: set[int] = set()  # inimigos já atingidos
        self.trail_timer = 0.0
        self.ricochet_left = 0     # Ricochete Diamante: salta p/ mais inimigos
        # sprites de efeito (Bola de Fogo animada, estilhaço de cristal...)
        self.anim_frames: list[pygame.Surface] = []  # >1 quadro = animação
        self.sprite: pygame.Surface | None = None    # sprite único (cristal)
        self.anim_timer = 0.0      # acumulador da animação
        # direção de arte das armas: identidade visual por projétil
        self.comet = False         # Bola de Fogo: cauda tipo cometa atrás
        self.sparkle = False       # Estilhaço: brilho de gema a cada ~3 frames
        self.kind = attack.get("type", "projectile")   # tipo (p/ fogueira, cascata)
        self.hit_any = False       # acertou algo? (fogueira só p/ bola que não acerta)

    def update(self, dt: float) -> bool:
        """Move o projétil. Retorna True se deve ser removido."""
        step = self.speed * dt
        self.pos += self.dir * step
        self.traveled += step
        self.anim_timer += dt      # avança a animação (se houver)
        return self.traveled >= self.max_range

    def draw(self, surface: pygame.Surface, world_offset) -> None:
        pos = self.pos - world_offset
        # brilho externo + núcleo brilhante
        glow = pygame.Surface((self.radius * 6, self.radius * 6), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 70), glow.get_rect().center, self.radius * 3)
        surface.blit(glow, glow.get_rect(center=pos))
        # aura da fusão: anel na cor do traço emprestado
        if self.glow_color is not None:
            pygame.draw.circle(surface, self.glow_color, pos, self.radius + 4, 2)
        # --- sprite animado (Bola de Fogo / Magic Orb da minigun) ---
        if self.anim_frames:
            if self.comet:
                # cauda tipo cometa: 3 rastros decrescentes atrás da bola
                for step in (1, 2, 3):
                    tail_pos = pos - self.dir * (step * 11)
                    tail_radius = max(2, int(self.radius * (1 - step * 0.22)))
                    shade = (255, 170, 70) if step == 1 else ((235, 120, 45) if step == 2 else (200, 80, 30))
                    pygame.draw.circle(surface, shade, tail_pos, tail_radius)
            index = int(self.anim_timer * 18) % len(self.anim_frames)
            frame = self.anim_frames[index]
            # gira o sprite para apontar na direção do voo
            angle = math.degrees(math.atan2(self.dir.y, self.dir.x))
            rotated = pygame.transform.rotate(frame, -angle)
            surface.blit(rotated, rotated.get_rect(center=pos))
            return
        # --- sprite único girando (estilhaço de Diamante) ---
        if self.sprite is not None:
            angle = self.anim_timer * 240   # gira no ar (efeito de cristal)
            rotated = pygame.transform.rotate(self.sprite, angle)
            surface.blit(rotated, rotated.get_rect(center=pos))
            if self.sparkle and int(self.anim_timer * 12) % 3 == 0:
                # "gem sparkle": brilho branco em estrela de 4 pontas
                star = pos + self.dir * 9
                pygame.draw.line(surface, (255, 255, 255), star - (4, 4), star + (4, 4), 2)
                pygame.draw.line(surface, (255, 255, 255), star + (4, -4), star + (-4, 4), 2)
                pygame.draw.circle(surface, (255, 255, 255), star, 2)
            return
        # --- placeholder circular (nenhum sprite disponível) ---
        pygame.draw.circle(surface, (255, 255, 255), pos, self.radius - 2)
        pygame.draw.circle(surface, self.color, pos, self.radius)


# ===========================================================================
# O mundo
# ===========================================================================
class World:
    def __init__(self, assets, particles, floating_texts):
        self.assets = assets
        self.particles = particles
        self.floating_texts = floating_texts
        self.enemies: list[Enemy] = []
        self.projectiles: list[Projectile] = []
        self.xp_orbs: list[XPOrb] = []
        self.health_orbs: list[HealthOrb] = []
        self.chests: list[Chest] = []
        self.effects: list[dict] = []          # efeitos temporários (arcos, anéis...)
        self.crystals: list[dict] = []         # cristais do Diamante orbitando
        self.powerups: list[PowerUp] = []      # Núcleos Instáveis no chão
        self.clones: list[dict] = []           # clones (Sombra de Kevin / Bagunçado)
        self.announcements: list[dict] = []    # banners de power-up (drenados pelo Game)
        self.bomb_timer = 0.0                  # Bomba Relógio
        self.chest_timer = 0.0                 # Caos do Baú Mágico
        self.fusion_pulse = 0.0                # pulso visual da fusão (anel)
        self._prism_gained = 0.0               # ganho de Prisma no frame atual (cap)
        self.player_ref: Player | None = None  # referência para efeitos on-hit
        self.kills = 0
        self.elapsed = 0.0
        self._last_spawn = 0.0
        self._last_chest = 0.0
        self.shake_queue: list[tuple[float, float]] = []  # (intensidade, duração)
        # --- Sistemas dos especiais de fusão (Fase 2) ---
        self.pending_explosions: list[dict] = []   # explosões atrasadas (Supernova Dupla/Cadeia)
        self.burn_zones: list[dict] = []           # anel de fogo residual (Pouso Vulcânico)
        self.slow_zones: list[dict] = []           # rachadura de lentidão (Super Pulmão)
        self.trails: list[dict] = []               # rastros de turbo (Rastro de Impacto / Chamas)
        self.echoes: list[dict] = []               # ecos do turbo (XLR8: clone-fantasma)
        self.boost_trail_cfg = None                # config do rastro do turbo ativo
        self._boost_line_timer = 0.0               # linhas de velocidade do turbo
        self.decorations: list[dict] = []          # castelos/pedras de decoração do mapa
        self._generate_decorations()

    # ------------------------------------------------------------------
    # Limpeza / dificuldade
    # ------------------------------------------------------------------
    def reset(self) -> None:
        self.enemies.clear()
        self.projectiles.clear()
        self.xp_orbs.clear()
        self.health_orbs.clear()
        self.chests.clear()
        self.effects.clear()
        self.crystals.clear()
        self.powerups.clear()
        self.clones.clear()
        self.announcements.clear()
        self.shake_queue.clear()
        self.bomb_timer = 0.0
        self.chest_timer = 0.0
        self.fusion_pulse = 0.0
        self._prism_gained = 0.0
        self.player_ref = None
        self.kills = 0
        self.elapsed = 0.0
        self._last_spawn = 0.0
        self._last_chest = 0.0
        self.pending_explosions.clear()
        self.burn_zones.clear()
        self.slow_zones.clear()
        self.trails.clear()
        self.echoes.clear()
        self.boost_trail_cfg = None
        self._boost_line_timer = 0.0
        self.decorations.clear()
        self._generate_decorations()

    def _generate_decorations(self) -> None:
        """Espalha pixel arts de castelo/pedra pelo mundo como decoração.

        São puramente visuais (não colidem nem bloqueiam) e dão personalidade
        ao mapa vazio — castelos ao fundo, como ruínas de um reino esquecido.
        As superfícies já vêm pré-escaladas (sem smoothscale por frame).
        """
        margin = 180
        # evita nascer em cima do spawn do jogador (centro do mundo)
        def random_far_pos():
            while True:
                pos = Vector2(random.uniform(margin, settings.WORLD_WIDTH - margin),
                              random.uniform(margin, settings.WORLD_HEIGHT - margin))
                if pos.distance_to((settings.WORLD_WIDTH / 2, settings.WORLD_HEIGHT / 2)) > 320:
                    return pos

        for _ in range(6):
            pos = random_far_pos()
            size = random.choice((70, 84, 96))
            self.decorations.append({"kind": "castle", "pos": pos, "image": self._deco_sprite("castle", size)})
        for _ in range(10):
            pos = random_far_pos()
            size = random.choice((22, 28, 34))
            self.decorations.append({"kind": "rock", "pos": pos, "image": self._deco_sprite("rock", size)})

    def _deco_sprite(self, key: str, size: int):
        """Pré-escala a pixel art da decoração uma única vez (cache por tamanho)."""
        sprite = self.assets.get_item(key)
        if sprite is None:
            return None
        return pygame.transform.smoothscale(sprite, (size, size))

    def enemy_scale(self) -> float:
        """Vida dos inimigos cresce com o tempo (até um limite)."""
        return min(settings.ENEMY_SCALE_CAP, 1 + self.elapsed * settings.ENEMY_SCALE_RATE)

    def enemy_speed_mult(self) -> float:
        """Velocidade começa tranquila e acelera AOS POUCOS (depois da graça)."""
        if self.elapsed <= settings.ENEMY_SPEED_GRACE:
            return 1.0
        ramp = 1 + (self.elapsed - settings.ENEMY_SPEED_GRACE) * settings.ENEMY_SPEED_RAMP
        return min(settings.ENEMY_SPEED_CAP, ramp)

    # ------------------------------------------------------------------
    # Spawn de inimigos (horda nas bordas da câmera)
    # ------------------------------------------------------------------
    def choose_enemy_type(self) -> str:
        """Escolhe um tipo de inimigo liberado até o momento, ponderado por peso."""
        options = []
        for enemy_type, data in settings.ENEMY_DATA.items():
            if data["unlock_kills"] and self.kills < data["unlock_kills"]:
                continue
            if data["unlock_time"] and self.elapsed < data["unlock_time"]:
                continue
            options.extend([enemy_type] * data["weight"])
        return random.choice(options)

    def spawn_enemy_near_camera(self, camera, player_pos=None) -> None:
        """Cria um inimigo LONGE do jogador, fora da visão da câmera (se possível).

        Os inimigos nascem distantes e andam até o personagem — nada de surgir
        do nada dentro da tela, mesmo com a câmera travada na borda do mundo.
        """
        center = Vector2(player_pos) if player_pos is not None else camera.position
        view = camera.view_rect.inflate(90, 90)
        chosen = None
        for _ in range(14):
            angle = random.uniform(0, math.tau)
            distance = random.uniform(430, 560)
            pos = center + Vector2(math.cos(angle), math.sin(angle)) * distance
            pos.x = max(30, min(settings.WORLD_WIDTH - 30, pos.x))
            pos.y = max(30, min(settings.WORLD_HEIGHT - 30, pos.y))
            chosen = pos
            if not view.collidepoint(pos):
                break
        # em cantos do mundo pode não existir ponto fora da tela: afasta do jogador
        if chosen is not None and chosen.distance_to(center) < 180:
            chosen = Vector2(center)
            chosen.x = 30 if center.x < settings.WORLD_WIDTH / 2 else settings.WORLD_WIDTH - 30
            chosen.y = 30 if center.y < settings.WORLD_HEIGHT / 2 else settings.WORLD_HEIGHT - 30
        self.enemies.append(Enemy(self.choose_enemy_type(), chosen, self.enemy_scale(),
                                  self.enemy_speed_mult()))

    def spawn_chest(self) -> None:
        pos = Vector2(random.uniform(150, settings.WORLD_WIDTH - 150),
                      random.uniform(150, settings.WORLD_HEIGHT - 150))
        self.chests.append(Chest(pos))

    def spawn_chest_near(self, position) -> None:
        """Caos do Baú Mágico: baú extra perto do jogador."""
        pos = Vector2(position) + Vector2(random.uniform(-180, 180),
                                          random.uniform(-180, 180))
        pos.x = max(60, min(settings.WORLD_WIDTH - 60, pos.x))
        pos.y = max(60, min(settings.WORLD_HEIGHT - 60, pos.y))
        self.chests.append(Chest(pos))

    # ------------------------------------------------------------------
    # Ataque primário de cada alien (clique esquerdo, apontado pelo mouse)
    # ------------------------------------------------------------------
    def attack(self, player: Player, now: float) -> bool:
        """Dispara o poder primário do alien atual na direção da mira.

        Cada alien tem o seu: Ben soca, o Quatro Braços bate no chão, o XLR8
        faz um ataque em cadeia, a Chama lança bola de fogo e o Diamante
        dispara estilhaços. Power-ups (Minigun, Punhos x4) e fusões (traços
        emprestados pelo parceiro) podem substituir ou modificar o ataque.
        Retorna True se o ataque foi usado.
        """
        self.player_ref = player
        data = settings.ALIEN_DATA[player.alien_name]
        attack = data["attack_z"]
        trait = self._fusion_trait(player)

        # --- Power-up MINIGUN: ataque primário vira rajada automática ---
        if "minigun" in player.powerups:
            return self.minigun_attack(player, now)
        # --- Power-up PUNHOS x4: 4 socos/segundo com força de Quatro Braços ---
        if "punhos_4x" in player.powerups:
            return self.quad_punch_attack(player, now)

        if attack is None or not player.primary_ready():
            return False
        player.primary_cd = (attack["cooldown"] * player.cooldown_mult
                             / player.powerup_fire_rate_mult())
        # traço Versatilidade (Ben): cadência extra — ataca mais rápido
        if trait == "cadence":
            player.primary_cd *= 0.65

        damage = (attack["damage"] + player.base_damage) * data["stats"]["damage_mult"]
        damage *= player.powerup_damage_mult() * player.damage_percent
        # traço Força Bruta (Quatro Braços): dano bônus fixo (escala com upgrades)
        if trait == "impact":
            damage += 1.5 * player.damage_percent

        # Combo Elemental: Chama -> Diamante em 2s = estilhaço em fogo
        if attack["type"] == "fireball":
            player.last_attack_alien = "Chama"
            player.last_attack_time = now
        if attack["type"] == "diamond_shot":
            fiery = (player.last_attack_alien == "Chama"
                     and now - player.last_attack_time <= settings.ELEMENTAL_WINDOW)
        else:
            fiery = False

        kind = attack["type"]
        if kind == "melee":
            self.melee_attack(player, attack, damage, now, trait=trait)
        elif kind == "ground_smash":
            self.smash_attack(player, attack, damage, now, trait=trait)
        elif kind == "chain_dash":
            self.chain_dash_attack(player, attack, damage, now, trait=trait)
        elif kind == "fireball":
            self.spawn_fireball(player, attack, damage, trait=trait)
        elif kind == "diamond_shot":
            self.spawn_diamond_shot(player, attack, damage, fiery=fiery, trait=trait)
        return True

    def _fusion_trait(self, player: Player) -> str | None:
        """Traço emprestado pelo parceiro da fusão (None = sem fusão)."""
        if not player.fusion:
            return None
        return settings.FUSION_TRAITS[player.fusion]["kind"]

    def _burst_count(self, attack: dict) -> int:
        """Rajada do traço Velocidade (XLR8): 2-4 golpes conforme o 'peso' do poder."""
        cooldown = max(0.2, attack.get("cooldown", 0.5))
        return max(2, min(4, round(1.4 / cooldown)))

    def melee_attack(self, player: Player, attack: dict, damage: float, now: float,
                     trait: str | None = None) -> None:
        """Soco (do Ben ou de fusão): golpe em arco na direção da mira.

        Aplica os traços de fusão (perfuração = alcance maior, rajada = golpes
        em sequência, elemental/força = explosão ao acertar) e também acerta
        baús no arco do golpe.
        """
        half_angle = math.radians(attack["arc_degrees"] / 2)
        aim = player.aim_dir
        reach = attack["range"]
        if trait == "pierce":
            reach += 70                    # Perfuração: alcance estendido
        burst = self._burst_count(attack) if trait == "burst" else 1
        extra_knock = 80 if trait == "impact" else 0.0
        # o arco do golpe ganha a cor do traço emprestado (visual de fusão)
        arc_color = settings.FUSION_TRAITS[player.fusion]["color"] if trait else attack["color"]
        hit_any = False
        # Parry do Ben: soco no instante em que o inimigo está prestes a te
        # acertar = dano triplo e cancela o dano recebido (janela curta).
        parry_ok = player.alien_name == "Ben" and trait is None
        for enemy in self.enemies:
            to_enemy = enemy.pos - player.pos
            distance = to_enemy.length()
            if distance > reach + enemy.size[0] * 0.4:
                continue
            if distance > 1 and aim.dot(to_enemy / distance) < math.cos(half_angle):
                continue  # fora do arco do golpe
            parry = False
            if parry_ok and distance <= settings.PARRY_RANGE:
                parry = True
                player.invincible_until = now + settings.PARRY_INVULNERABILITY
                self.floating_texts.add("PARRY!", player.pos, settings.COLORS["gold"])
                self.particles.burst(enemy.pos, 14, settings.COLORS["gold"], 240, 0.35, 4)
            for _ in range(burst):
                per_punch = damage * (0.65 if burst > 1 else 1.0)
                if parry:
                    per_punch *= settings.PARRY_DAMAGE_MULT
                final = self._apply_combos(player, per_punch, now)
                enemy.apply_damage(final, to_enemy, attack["knockback"] + extra_knock
                                   + (160 if parry else 0.0))
                self._on_enemy_hit(enemy, int(final), now)
            self._maybe_explode_on_hit(player, enemy, damage, now, trait=trait)
            hit_any = True
        # baús também levam dano do soco (mesmo arco)
        for chest in self.chests:
            to_chest = chest.pos - player.pos
            distance = to_chest.length()
            if distance > reach + settings.CHEST_SIZE * 0.4:
                continue
            if distance > 1 and aim.dot(to_chest / distance) < math.cos(half_angle):
                continue
            self.damage_chest(chest, damage, now)
        # Manoplas de Cristal (fusão Ben+Diamante): cada soco também perfura
        # à frente como um mini-estilhaço corpo a corpo
        if player.gauntlets_timer > 0:
            self._spawn_crystal_shard(player, aim, player.gauntlets_damage, now)
        # efeito visual: arco desenhado na direção da mira (com afterimage)
        start_angle = math.degrees(math.atan2(aim.y, aim.x))
        self.effects.append({
            "kind": "arc", "center": player.pos, "radius": reach,
            "start_angle": start_angle, "arc_degrees": attack["arc_degrees"],
            "color": arc_color, "lifetime": 0.14, "max_lifetime": 0.14,
        })
        self.assets.play("melee")
        if hit_any:
            self.request_shake(5, 0.12)

    def smash_attack(self, player: Player, attack: dict, damage: float, now: float,
                     trait: str | None = None) -> None:
        """Pancada no chão do Quatro Braços: retângulo na direção da mira.

        Pancada CARREGADA: segurar o clique acumula player.smash_charge (até
        SMASH_CHARGE_TIME); a área e o dano crescem proporcionalmente. A carga
        é consumida a cada pancada (Game acumula e zera no uso).
        """
        aim = player.aim_dir
        charge = max(0.0, min(1.0, player.smash_charge / settings.SMASH_CHARGE_TIME))
        player.smash_charge = 0.0     # consome a carga acumulada
        length = attack["range"] * (1 + charge * (settings.SMASH_CHARGE_MAX_RANGE - 1))
        width = attack["width"] * (1 + charge * (settings.SMASH_CHARGE_MAX_WIDTH - 1))
        if trait == "pierce":
            width += 40                        # Perfuração: área mais larga
        if charge > 0:
            damage *= 1 + charge * (settings.SMASH_CHARGE_DAMAGE - 1)
        burst = self._burst_count(attack) if trait == "burst" else 1
        extra_knock = 90 if trait == "impact" else 0.0
        rect_color = settings.FUSION_TRAITS[player.fusion]["color"] if trait else attack["color"]
        hit_any = False
        for enemy in self.enemies:
            delta = enemy.pos - player.pos
            forward = delta.dot(aim)              # ao longo da mira
            lateral = abs(delta.cross(aim))       # perpendicular à mira
            if (0 <= forward <= length + enemy.size[0] * 0.3
                    and lateral <= width / 2 + enemy.size[0] * 0.4):
                for _ in range(burst):
                    per_hit = damage * (0.7 if burst > 1 else 1.0)
                    final = self._apply_combos(player, per_hit, now)
                    enemy.apply_damage(final, delta, attack["knockback"] + extra_knock)
                    self._on_enemy_hit(enemy, int(final), now)
                self._maybe_explode_on_hit(player, enemy, damage, now, trait=trait)
                hit_any = True
        # baús também levam dano da pancada
        for chest in self.chests:
            delta = chest.pos - player.pos
            forward = delta.dot(aim)
            lateral = abs(delta.cross(aim))
            if (0 <= forward <= length + settings.CHEST_SIZE * 0.3
                    and lateral <= width / 2 + settings.CHEST_SIZE * 0.4):
                self.damage_chest(chest, damage, now)
        # visual: retângulo translúcido rotacionado na direção da mira
        rect_surface = pygame.Surface((int(length), int(width)), pygame.SRCALPHA)
        rect_surface.fill((*rect_color, 90))
        angle = -math.degrees(math.atan2(aim.y, aim.x))
        image = pygame.transform.rotate(rect_surface, angle)
        self.effects.append({
            "kind": "rect", "image": image,
            "center": player.pos + aim * (length / 2),
            "lifetime": 0.18, "max_lifetime": 0.18,
        })
        # onda de pressão cinética no ponto de impacto (força bruta, não fogo).
        # shake=0: o tremor vem do hit_any abaixo (evita shake duplicado)
        impact_point = player.pos + aim * (length * 0.45)
        self._shockwave_impact(impact_point, width * 0.9, 0.0, now,
                               color=rect_color, shake=0)
        # rachaduras pixeladas que ficam ~1.6s: a "cicatriz" do impacto
        self.effects.append({
            "kind": "cracks", "center": Vector2(impact_point),
            "radius": width * 0.8, "color": (185, 185, 195),
            "lifetime": 1.6, "max_lifetime": 1.6,
            "seed": random.uniform(0, math.tau),
        })
        # pedras voando do impacto (pixel art de item) — força bruta arremessa
        # detritos para os lados, como se o chão tivesse quebrado de verdade
        rock = self.assets.get_item("rock")
        if rock is not None:
            self.effects.append({
                "kind": "rock_debris", "center": Vector2(impact_point),
                "sprite": rock, "count": 5,
                "lifetime": 0.55, "max_lifetime": 0.55,
                "seed": random.uniform(0, math.tau),
                "spread": width * 0.6,
            })
        self.assets.play("smash")
        if hit_any:
            self.request_shake(6, 0.15)

    def chain_dash_attack(self, player: Player, attack: dict, damage: float, now: float,
                          trait: str | None = None) -> None:
        """Ataque em cadeia do XLR8: atinge os inimigos mais próximos em sequência."""
        num_targets = attack["num_targets"]
        if trait == "burst":
            num_targets *= 2                     # Velocidade: encadeia mais alvos
        reach = attack["range"]
        if trait == "pierce":
            reach += 60
        extra_knock = 70 if trait == "impact" else 0.0
        line_color = settings.FUSION_TRAITS[player.fusion]["color"] if trait else attack["color"]
        candidates = [e for e in self.enemies
                      if e.pos.distance_to(player.pos) <= reach]
        candidates.sort(key=lambda e: e.pos.distance_to(player.pos))
        targets = candidates[:num_targets]
        if not targets:
            self._chain_chest(player, reach, damage, now)
            return
        previous = player.pos
        for target in targets:
            final = self._apply_combos(player, damage, now)
            target.apply_damage(final, target.pos - player.pos, 60 + extra_knock)
            self._on_enemy_hit(target, int(final), now)
            self._maybe_explode_on_hit(player, target, damage, now, trait=trait)
            # Atordoamento por REFORÇO: atingir o mesmo alvo repetidamente
            # dentro da janela acumula; no 3º acerto o alvo é atordoado.
            if now - target.last_chain_hit > settings.CHAIN_STUN_WINDOW:
                target.chain_hits = 0
            target.chain_hits += 1
            target.last_chain_hit = now
            if target.chain_hits >= settings.CHAIN_STUN_HITS:
                target.chain_hits = 0
                target.apply_freeze(settings.CHAIN_STUN_DURATION)
                self.floating_texts.add("ATORDADO!", target.pos, settings.COLORS["gold"])
            self.effects.append({
                "kind": "bolt", "start": previous, "end": target.pos,
                "color": line_color, "lifetime": 0.18, "max_lifetime": 0.18,
                "seed": random.uniform(0, math.tau),
            })
            previous = target.pos
        player.pos = targets[-1].pos
        player.invincible_until = now + 0.5  # invencível rapidinho ao atravessar
        # um baú no caminho da cadeia também é atingido
        self._chain_chest(player, reach, damage, now)
        self.assets.play("melee")
        self.request_shake(4, 0.12)

    def _chain_chest(self, player: Player, reach: float, damage: float, now: float) -> None:
        """A cadeia do XLR8 acerta o baú mais próximo dentro do alcance."""
        chests = [c for c in self.chests if c.pos.distance_to(player.pos) <= reach]
        if chests:
            closest = min(chests, key=lambda c: c.pos.distance_to(player.pos))
            self.damage_chest(closest, damage, now)

    def spawn_fireball(self, player: Player, attack: dict, damage: float,
                       trait: str | None = None) -> None:
        """Bola de fogo da Chama: explode ao atingir um inimigo.

        Traços: Velocidade dispara em rajada; Elemental/Força Bruta aumentam
        a área da explosão.
        """
        burst = self._burst_count(attack) if trait == "burst" else 1
        radius = attack["explosion_radius"]
        if trait in ("burn", "impact"):
            radius = int(radius * 1.35)
        max_range = attack["range"]
        if trait == "pierce":
            max_range += 100                  # Perfuração: bola voa mais longe
        glow_color = settings.FUSION_TRAITS[player.fusion]["color"] if trait else None
        for index in range(burst):
            spread = (index - (burst - 1) / 2) * 0.16
            direction = player.aim_dir
            if burst > 1:
                direction = player.aim_dir.rotate(math.degrees(spread))
            origin = player.pos + direction * 28
            fire = {"type": "fireball", "speed": attack["speed"], "range": max_range,
                    "color": attack["color"], "radius": 7}
            projectile = Projectile(origin, direction, fire, damage, self.assets)
            projectile.glow_color = glow_color
            projectile.explosion_radius = radius
            projectile.explosion_damage = damage
            projectile.anim_frames = self.assets.get_effects("fireball_frames") or []
            projectile.comet = True   # cauda tipo cometa atrás da bola
            self.projectiles.append(projectile)
        self.assets.play("fireball")

    def spawn_diamond_shot(self, player: Player, attack: dict, damage: float,
                           fiery: bool = False, trait: str | None = None) -> None:
        """Estilhaço do Diamante: projétil rápido e perfurante na direção da mira."""
        burst = self._burst_count(attack) if trait == "burst" else 1
        pierce = attack.get("pierce", 0) + (2 if trait == "pierce" else 0)
        knockback = 140 if trait == "impact" else 60
        glow_color = settings.FUSION_TRAITS[player.fusion]["color"] if trait else None
        for index in range(burst):
            spread = (index - (burst - 1) / 2) * 0.14
            direction = player.aim_dir
            if burst > 1:
                direction = player.aim_dir.rotate(math.degrees(spread))
            origin = player.pos + direction * 28
            shard = {"type": "diamond_shot", "speed": attack["speed"], "range": attack["range"],
                     "color": attack["color"], "radius": 6, "pierce": pierce}
            projectile = Projectile(origin, direction, shard, damage, self.assets)
            projectile.glow_color = glow_color
            projectile.knockback = knockback
            projectile.sprite = self.assets.get_effects("crystal_shard")
            projectile.sparkle = True   # brilho de gema a cada ~3 frames
            if fiery:   # Combo Elemental: estilhaço em chamas (explode ao acertar)
                projectile.explosion_radius = 46
                projectile.explosion_damage = damage * 0.5
            if trait == "burn":
                projectile.explosion_radius = max(projectile.explosion_radius, 55)
                projectile.explosion_damage = damage * 0.5
            self._apply_projectile_powerups(projectile, player)
            self.projectiles.append(projectile)
        self.assets.play("crystal")

    def _apply_projectile_powerups(self, projectile: Projectile, player: Player) -> None:
        """Núcleo Instável (explosivo) e Ricochete aplicados a projéteis novos."""
        if "nucleo_chama" in player.powerups:
            cfg = settings.POWERUP_DATA["nucleo_chama"]
            projectile.explosion_radius = max(projectile.explosion_radius, cfg["radius"])
            projectile.explosion_damage = projectile.damage * 0.5
        if "ricochete" in player.powerups:
            projectile.ricochet_left = settings.POWERUP_DATA["ricochete"]["extra"]

    # ------------------------------------------------------------------
    # Ataques vindos de power-ups e fusões (Fase 2)
    # ------------------------------------------------------------------
    def minigun_attack(self, player: Player, now: float) -> bool:
        """Minigun do Sumo Sacerdote: rajada contínua enquanto segura o clique."""
        cfg = settings.POWERUP_DATA["minigun"]
        if not player.primary_ready():
            return False
        player.primary_cd = cfg["fire_rate"] / player.powerup_fire_rate_mult()
        damage = (cfg["bullet_damage"] + player.base_damage * 0.2)
        damage *= player.powerup_damage_mult() * player.damage_percent
        attack = {"type": "minigun", "speed": cfg["bullet_speed"], "range": cfg["bullet_range"],
                  "color": (255, 230, 120), "radius": 4}
        origin = player.pos + player.aim_dir * 26
        projectile = Projectile(origin, player.aim_dir, attack, damage, self.assets)
        # a minigun atira ARRUELAS de metal (pixel art de item) girando no ar
        washer = self.assets.get_item("washer")
        if washer is not None:
            projectile.sprite = washer
        else:
            projectile.anim_frames = self.assets.get_effects("minigun_frames") or []
        self.projectiles.append(projectile)
        self.assets.play("fireball")
        return True

    def quad_punch_attack(self, player: Player, now: float) -> bool:
        """Punhos de Quatro Braços x4: 4 socos/seg com força e knockback."""
        cfg = settings.POWERUP_DATA["punhos_4x"]
        if not player.primary_ready():
            return False
        player.primary_cd = cfg["fire_rate"] / player.powerup_fire_rate_mult()
        attack = {"type": "melee", "name": "Punhos x4", "range": 135,
                  "arc_degrees": 140, "knockback": cfg["knockback"],
                  "color": (230, 90, 90)}
        damage = (cfg["damage"] + player.base_damage)
        damage *= player.powerup_damage_mult() * player.damage_percent
        self.melee_attack(player, attack, damage, now)
        return True

    # ------------------------------------------------------------------
    # Combos (Golpe Triplo + Troca Relâmpago) e explosivos on-hit
    # ------------------------------------------------------------------
    def _apply_combos(self, player: Player, damage: float, now: float) -> float:
        """Aplica Golpe Triplo (+50%) e Troca Relâmpago (crítico 2x)."""
        # Troca Relâmpago: atacar até 0,4s depois de transformar = crítico
        if now - player.last_form_change <= settings.QUICK_SWAP_WINDOW:
            damage *= 2.0
            player.last_form_change = -999.0   # consome o bônus
            self.floating_texts.add("CRÍTICO!", player.pos, settings.COLORS["gold"])
        # Golpe Triplo: 3 acertos em 1,5s liberam +50% NO PRÓXIMO golpe
        player.combo_count += 1
        player.combo_timer = settings.COMBO_WINDOW
        if player.combo_bonus_ready:
            damage *= 1 + settings.COMBO_BONUS
            player.combo_bonus_ready = False
            self.floating_texts.add("COMBO +50%!", player.pos, settings.COLORS["gold"])
        if player.combo_count >= settings.COMBO_THRESHOLD:
            player.combo_count = 0
            player.combo_bonus_ready = True
            player.combo_timer = settings.COMBO_WINDOW  # bônus expira se demorar
        return damage

    def _maybe_explode_on_hit(self, player: Player, enemy: Enemy,
                              damage: float, now: float,
                              trait: str | None = None) -> None:
        """Explosões ao acertar: Núcleo de Chama + traço Elemental (fogo)
        e onda de pressão cinética do traço Força Bruta (sem fogo)."""
        radius, explode_damage = 0.0, 0.0
        if "nucleo_chama" in player.powerups:
            cfg = settings.POWERUP_DATA["nucleo_chama"]
            radius = max(radius, cfg["radius"])
            explode_damage += damage * 0.4
        if trait == "burn":
            radius = max(radius, 55)
            explode_damage += damage * 0.5
        if trait == "impact":
            # Força Bruta: onda de pressão cinética (força, não fogo)
            self._shockwave_impact(enemy.pos, 70, damage * 0.35, now,
                                   color=(225, 225, 235), shake=3)
        if radius > 0:
            color = settings.COLORS["fire_orange"]
            self._explosion(enemy.pos, radius, explode_damage, now, color=color, shake=3)

    # ------------------------------------------------------------------
    # Habilidades especiais dos aliens (tecla X)
    # ------------------------------------------------------------------
    def request_shake(self, intensity: float, duration: float) -> None:
        """Pede um tremor de tela (aplicado pelo Game, que conhece a câmera)."""
        self.shake_queue.append((intensity, duration))

    def drain_shakes(self) -> list[tuple[float, float]]:
        shakes = list(self.shake_queue)
        self.shake_queue.clear()
        return shakes

    def cast_special(self, player: Player, now: float) -> bool:
        """Executa a habilidade especial (tecla X).

        Com fusão ativa, o X vira a versão COMBINADA dos dois aliens — as 20
        combinações de FUSION_SPECIALS — em vez do especial do alien base.
        Retorna True se foi usada.
        """
        self.player_ref = player
        # Traje Venom bloqueia o especial
        if "traje_venom" in player.powerups:
            self.floating_texts.add("SEM ESPECIAL (VENOM)", player.pos, settings.COLORS["purple"])
            return False
        # --- Fusão: especial combinado (X vira a mistura dos dois aliens) ---
        if player.fusion:
            cfg = settings.FUSION_SPECIALS.get((player.alien_name, player.fusion))
            if cfg is not None:
                return self._cast_fusion_special(player, now, cfg)
        special = settings.ALIEN_DATA[player.alien_name]["special"]
        if special is None or not player.special_ready():
            return False
        player.special_cd = special["cooldown"] * player.cooldown_mult

        kind = special["type"]
        if kind == "super_jump":
            target = player.pos + player.aim_dir * special["range"]
            player.start_jump(target, now)
            self.assets.play("smash")
        elif kind == "boost":
            player.start_boost(special["duration"])
            self.assets.play("boost")
        elif kind == "omnitrix_roar":
            # Grito do Omnitrix (Ben): não causa dano, empurra tudo e acelera
            # a recarga de energia por alguns segundos — o "alien de respiro".
            player.energy_boost_timer = max(player.energy_boost_timer,
                                            special["energy_boost"])
            self.effects.append({
                "kind": "shockwave", "center": Vector2(player.pos),
                "radius": special["radius"], "color": settings.COLORS["omnitrix_green"],
                "lifetime": 0.4, "max_lifetime": 0.4,
                "seed": random.uniform(0, math.tau),
            })
            self.particles.burst(player.pos, 26, settings.COLORS["omnitrix_green"],
                                 260, 0.45, 5)
            for enemy in self.enemies:
                delta = enemy.pos - player.pos
                if delta.length() <= special["radius"] + enemy.size[0] / 2:
                    direction = delta.normalize() if delta.length() > 1 else player.aim_dir
                    enemy.knockback += direction * special["knockback"]
            self.request_shake(6, 0.25)
            self.assets.play("nova")
        elif kind == "nova":
            damage = (special["damage"] + player.base_damage) * player.damage_percent
            self._explosion(player.pos, special["radius"], damage, now,
                            color=settings.COLORS["fire_orange"], shake=12,
                            flame_ring=True)
            # cratera incandescente: o chão continua queimando quem pisar
            self.burn_zones.append({
                "pos": Vector2(player.pos),
                "radius": special["radius"] * settings.NOVA_CRATER_RADIUS_MULT,
                "damage": damage * settings.NOVA_CRATER_DAMAGE_MULT,
                "timer": settings.NOVA_CRATER_DURATION,
                "interval": 0.4,
                "color": (255, 150, 60),
            })
            self.assets.play("nova")
        elif kind == "crystal_field":
            for index in range(special["count"]):
                # fases levemente dessincronizadas (não parece carrossel)
                phase = math.tau * index / special["count"] + random.uniform(-0.25, 0.25)
                self.crystals.append({
                    "angle": phase,
                    "orbit_radius": special["orbit_radius"],
                    "duration": special["duration"],
                    "damage": (special["damage"] + player.base_damage) * player.damage_percent,
                    "spin": 2.2 * random.uniform(0.9, 1.15),   # rotação dessincronizada
                    "size": 10,
                    "knockback": 40,
                    "fire": False,
                    "hit_ids": set(),
                })
            self.assets.play("crystal_field")
        return True

    def _announce_special(self, player: Player, name: str, color) -> None:
        """Banner arcade + texto flutuante quando um especial de fusão é usado."""
        duration = _banner_duration(f"ESPECIAL: {name}")
        self.announcements.append({"text": f"ESPECIAL: {name}", "rarity": "epic",
                                   "timer": duration, "max_timer": duration})
        self.floating_texts.add(name, player.pos, color, lifetime=1.2)

    def _spawn_crystal_shard(self, player: Player, direction, damage: float,
                             now: float) -> None:
        """Estilhaço de cristal perfurante (Pouso Cristalino / Supernova Estilhaçada)."""
        attack = {"type": "diamond_shot", "speed": 620, "range": 480,
                  "color": settings.COLORS["diamond_cyan"], "radius": 6, "pierce": 4}
        projectile = Projectile(player.pos + direction * 30, direction, attack,
                                damage, self.assets)
        projectile.sprite = self.assets.get_effects("crystal_shard")
        self.projectiles.append(projectile)

    def _cast_fusion_special(self, player: Player, now: float, cfg: dict) -> bool:
        """Executa o especial COMBINADO da fusão (as 20 combinações)."""
        kind = cfg["type"]
        if not player.special_ready():
            return False
        trait_color = settings.FUSION_TRAITS[player.fusion]["color"]

        # ================= Pulos combinados =================
        if kind in ("impact_jump", "double_jump", "jump_barrage",
                    "volcanic_landing", "crystal_landing"):
            if kind == "double_jump":
                # Pulmão Duplo: 1º uso com cooldown curto, 2º com o total
                if player.double_jump_ready:
                    player.double_jump_ready = False
                    player.special_cd = cfg["cooldown"] * player.cooldown_mult
                else:
                    player.double_jump_ready = True
                    player.special_cd = 0.6 * player.cooldown_mult
            elif kind == "jump_barrage":
                player.jump_barrage_stage = 1
                player.special_cd = cfg["cooldown"] * player.cooldown_mult
            else:
                player.special_cd = cfg["cooldown"] * player.cooldown_mult
            # guarda a cfg no jogador: o POUSO usa ela, mesmo se a forma mudar
            player.fusion_jump_cfg = cfg
            target = player.pos + player.aim_dir * cfg["range"]
            player.start_jump(target, now)
            self.assets.play("smash")
            self._announce_special(player, cfg["name"], trait_color)
            return True

        # ================= Investida Relâmpago (Ben+XLR8) =================
        if kind == "rush":
            player.special_cd = cfg["cooldown"] * player.cooldown_mult
            player.start_rush(player.aim_dir, cfg["distance"], now)
            player.rush_damage = (cfg["damage"] + player.base_damage) * player.damage_percent
            self.assets.play("boost")
            self._announce_special(player, cfg["name"], trait_color)
            return True

        # ================= Soco Solar (Ben+Chama) =================
        if kind == "solar_punch":
            player.special_cd = cfg["cooldown"] * player.cooldown_mult
            damage = (cfg["damage"] + player.base_damage) * player.damage_percent
            attack = {"type": "melee", "name": "Soco Solar", "range": cfg["range"],
                      "arc_degrees": cfg["arc_degrees"], "damage": cfg["damage"],
                      "cooldown": cfg["cooldown"], "knockback": 140,
                      "color": settings.COLORS["fire_orange"]}
            self.melee_attack(player, attack, damage, now, trait=None)
            # explosão na ponta do punho (mini-Supernova centrada no soco)
            impact = player.pos + player.aim_dir * (cfg["range"] * 0.8)
            self._explosion(impact, cfg["radius"], damage, now,
                            color=settings.COLORS["fire_orange"], shake=8,
                            flame_ring=True)
            self._announce_special(player, cfg["name"], trait_color)
            return True

        # ================= Manoplas de Cristal (Ben+Diamante) =================
        if kind == "crystal_gauntlets":
            player.special_cd = cfg["cooldown"] * player.cooldown_mult
            player.gauntlets_timer = cfg["duration"]
            player.gauntlets_damage = ((cfg["shard_damage"] + player.base_damage)
                                       * player.damage_percent)
            self.particles.burst(player.pos, 20, settings.COLORS["diamond_cyan"],
                                 200, 0.5, 4)
            self._announce_special(player, cfg["name"], trait_color)
            return True

        # ================= Turbos do XLR8 (boost + variações) =================
        if kind in ("stable_boost", "impact_trail", "fire_trail", "crystal_boost"):
            player.special_cd = cfg["cooldown"] * player.cooldown_mult
            duration = cfg.get("duration", 3.0)
            if kind == "stable_boost":
                duration += 1.5   # Turbo Estável: dura mais (e estoura no fim)
            player.start_boost(duration)
            if kind in ("impact_trail", "fire_trail"):
                self.boost_trail_cfg = {
                    "type": kind,
                    "damage": (cfg["trail_damage"] + player.base_damage * 0.3)
                               * player.damage_percent,
                    "timer": 0.0,
                    "color": trait_color,
                }
            elif kind == "crystal_boost":
                for index in range(cfg["count"]):
                    self.crystals.append({
                        "angle": math.tau * index / cfg["count"],
                        "orbit_radius": 60, "duration": duration + 0.6,
                        "damage": (cfg["damage"] + player.base_damage) * player.damage_percent,
                        "spin": 3.2, "size": 8, "knockback": 40, "fire": False,
                        "hit_ids": set(),
                    })
            self.assets.play("boost")
            self._announce_special(player, cfg["name"], trait_color)
            return True

        # ================= Supernovas da Chama (explosões combinadas) =================
        if kind in ("double_nova", "chain_nova", "impact_nova", "shard_nova"):
            player.special_cd = cfg["cooldown"] * player.cooldown_mult
            damage = (cfg["damage"] + player.base_damage) * player.damage_percent
            if kind in ("double_nova", "chain_nova"):
                self._explosion(player.pos, cfg["radius"], damage, now,
                                color=settings.COLORS["fire_orange"], shake=10,
                                flame_ring=True)
                # 2º pulso atrasado (fila de explosões pendentes)
                self.pending_explosions.append({
                    "time": now + cfg["delay"], "pos": Vector2(player.pos),
                    "radius": cfg["radius"] * 0.8, "damage": damage * 0.8,
                    "color": settings.COLORS["fire_orange"], "shake": 8,
                })
            else:
                self._explosion(player.pos, cfg["radius"], damage, now,
                                color=settings.COLORS["fire_orange"], shake=12,
                                knockback=cfg.get("knockback", 180), flame_ring=True)
                if kind == "shard_nova":
                    for index in range(cfg["shards"]):
                        direction = Vector2(1, 0).rotate(360 / cfg["shards"] * index)
                        self._spawn_crystal_shard(player, direction, damage * 0.6, now)
            self.assets.play("nova")
            self._announce_special(player, cfg["name"], trait_color)
            return True

        # ================= Campos de cristais do Diamante (variações) =================
        if kind in ("agile_field", "heavy_field", "turbo_field", "fire_field"):
            player.special_cd = cfg["cooldown"] * player.cooldown_mult
            for index in range(cfg["count"]):
                phase = math.tau * index / cfg["count"] + random.uniform(-0.3, 0.3)
                self.crystals.append({
                    "angle": phase,
                    "orbit_radius": cfg["orbit_radius"],
                    "duration": cfg["duration"],
                    "damage": (cfg["damage"] + player.base_damage) * player.damage_percent,
                    "spin": cfg.get("spin", 2.2) * random.uniform(0.9, 1.15),
                    "size": cfg.get("size", 10),
                    "knockback": cfg.get("knockback", 40),
                    "fire": kind == "fire_field",
                    "hit_ids": set(),
                })
            self.assets.play("crystal_field")
            self._announce_special(player, cfg["name"], trait_color)
            return True

        return False

    def _explosion(self, position: Vector2, radius: float, damage: float, now: float,
                   color=None, shake: float = 0.0, knockback: float = 180.0,
                   flame_ring: bool = False) -> None:
        """Explosão (Supernova, bola de fogo, pouso do Super Pulmão).

        Usa a sprite sheet de explosão (24 quadros) quando disponível; o anel
        colorido fica como reforço visual por cima. `flame_ring` troca o anel
        liso por um anel de fogo com "línguas" irregulares (visual de Supernova).
        `knockback` controla a força do empurrão (Supernova de Impacto).
        """
        color = color or settings.COLORS["fire_orange"]
        frames = self.assets.get_effects("explosion_frames") or []
        if frames:
            # redimensiona os quadros conforme o raio da explosão (teto de 320px
            # para não alocar dezenas de MB em explosões gigantes — o anel
            # colorido por cima reforça o tamanho real do raio)
            size = max(24, min(int(radius * 2), 320))
            scaled_frames = [pygame.transform.scale(f, (size, size)) for f in frames]
            self.effects.append({
                "kind": "explosion", "center": Vector2(position),
                "frames": scaled_frames, "lifetime": 0.45, "max_lifetime": 0.45,
            })
        if flame_ring:
            self.effects.append({
                "kind": "flame_ring", "center": Vector2(position), "radius": radius,
                "color": color, "lifetime": 0.32, "max_lifetime": 0.32,
                "seed": random.uniform(0, math.tau),
            })
        else:
            self.effects.append({
                "kind": "ring", "center": Vector2(position), "radius": radius,
                "color": color, "lifetime": 0.3, "max_lifetime": 0.3,
            })
        self.particles.burst(position, 30, color, 260, 0.4, 6)
        for enemy in self.enemies:
            if enemy.pos.distance_to(position) <= radius + enemy.size[0] / 2:
                enemy.apply_damage(damage, enemy.pos - position, knockback)
                self._on_enemy_hit(enemy, int(damage), now)
        # explosões também abrem baús (Bola de Fogo, Supernova, bombas...)
        for chest in self.chests:
            if chest.pos.distance_to(position) <= radius + settings.CHEST_SIZE / 2:
                self.damage_chest(chest, damage, now)
        if shake > 0:
            self.request_shake(shake, 0.25)

    def _shockwave_impact(self, position: Vector2, radius: float, damage: float,
                          now: float, color=None, shake: float = 0.0) -> None:
        """Onda de pressão CINÉTICA (Quatro Braços) — choque de força pura.

        Visual 100% procedural: anel irregular de pressão expandindo + raios de
        velocidade radiais + poeira/detritos. Nada de sprite de fogo — o
        impacto é "explosão por pressão", como uma onda de choque no chão.
        """
        color = color or (215, 215, 225)
        self.effects.append({
            "kind": "shockwave", "center": Vector2(position), "radius": radius,
            "color": color, "lifetime": 0.35, "max_lifetime": 0.35,
            "seed": random.uniform(0, math.tau),
        })
        # poeira/detritos cinza-claros (força bruta) + clarão branco
        self.particles.burst(position, 24, (200, 200, 210), 240, 0.45, 5)
        self.particles.burst(position, 8, (255, 255, 255), 320, 0.3, 3)
        if damage > 0:
            for enemy in self.enemies:
                if enemy.pos.distance_to(position) <= radius + enemy.size[0] / 2:
                    enemy.apply_damage(damage, enemy.pos - position, 200)
                    self._on_enemy_hit(enemy, int(damage), now)
            for chest in self.chests:
                if chest.pos.distance_to(position) <= radius + settings.CHEST_SIZE / 2:
                    self.damage_chest(chest, damage, now)
        if shake > 0:
            self.request_shake(shake, 0.25)

    def handle_boost_end(self, player: Player, now: float) -> None:
        """Fim do turbo (evento boost_ended). Turbo Estável termina com estouro."""
        if player.fusion:
            cfg = settings.FUSION_SPECIALS.get((player.alien_name, player.fusion))
            if cfg and cfg["type"] == "stable_boost":
                color = settings.FUSION_TRAITS[player.fusion]["color"]
                self.particles.burst(player.pos, 22, color, 260, 0.45, 4)
                self.effects.append({"kind": "ring", "center": Vector2(player.pos),
                                     "radius": 60, "color": color,
                                     "lifetime": 0.3, "max_lifetime": 0.3})
                self.request_shake(3, 0.15)
        self.boost_trail_cfg = None

    def handle_jump_landing(self, player: Player, now: float) -> None:
        # --- Fusão: o pouso pertence ao especial combinado (Salto de Impacto,
        # Pulmão Duplo, Saraivada, Pouso Vulcânico, Pouso Cristalino) ---
        # usa a cfg GUARDADA no pulo (robusto mesmo se trocar de alien entre
        # os pulos da Saraivada, ou se a fusão terminar no meio do salto)
        cfg = getattr(player, "fusion_jump_cfg", None)
        if cfg and cfg["type"] in settings.FUSION_JUMP_TYPES:
            self._fusion_jump_landing(player, now, cfg)
            return
        special = settings.ALIEN_DATA[player.alien_name].get("special")
        if not special:
            return
        # pouso do Super Pulmão: onda de choque cinética (força bruta, não fogo)
        self._shockwave_impact(player.pos, special["radius"],
                               (special["damage"] + player.base_damage) * player.damage_percent,
                               now, color=settings.COLORS["four_red"], shake=10)
        # rachaduras que ficam como cicatriz do pouso
        self.effects.append({
            "kind": "cracks", "center": Vector2(player.pos),
            "radius": special["radius"] * 0.7, "color": (190, 170, 175),
            "lifetime": 1.6, "max_lifetime": 1.6,
            "seed": random.uniform(0, math.tau),
        })
        # a rachadura vira zona de LENTIDÃO: inimigos que pisam nela andam
        # devagar (controle de território, não só dano pontual)
        self.slow_zones.append({
            "pos": Vector2(player.pos),
            "radius": settings.SUPER_JUMP_SLOW_RADIUS,
            "timer": settings.SUPER_JUMP_SLOW_DURATION,
            "slow_mult": settings.SUPER_JUMP_SLOW_MULT,
            "color": (190, 170, 175),
        })
        # pedras voando do pouso (pixel art de item) — o chão quebra
        rock = self.assets.get_item("rock")
        if rock is not None:
            self.effects.append({
                "kind": "rock_debris", "center": Vector2(player.pos),
                "sprite": rock, "count": 6,
                "lifetime": 0.6, "max_lifetime": 0.6,
                "seed": random.uniform(0, math.tau),
                "spread": special["radius"] * 0.8,
            })
        self.assets.play("jump_land")

    def _fusion_jump_landing(self, player: Player, now: float, cfg: dict) -> None:
        """Pouso dos especiais de fusão que são pulos (FUSION_JUMP_TYPES)."""
        kind = cfg["type"]
        color = settings.FUSION_TRAITS[player.fusion]["color"]
        damage = (cfg.get("damage", 2.0) + player.base_damage) * player.damage_percent

        if kind == "jump_barrage":
            # Saraivada de Pulmão: 1º pouso pequeno, 2º pouso grande
            stage = player.jump_barrage_stage
            if stage == 1:
                self._shockwave_impact(player.pos, cfg["radius"], damage * 0.6, now,
                                       color=color, shake=5)
                player.jump_barrage_stage = 2
                target = player.pos + player.aim_dir * cfg["range"]
                player.start_jump(target, now)
            else:
                self._shockwave_impact(player.pos, cfg["big_radius"], damage, now,
                                       color=color, shake=12)
                player.jump_barrage_stage = 0
                player.fusion_jump_cfg = None   # saraivada concluída
            self.assets.play("jump_land")
            return

        if kind == "volcanic_landing":
            # Pouso Vulcânico: onda de pressão + anel de fogo que queima 2-3s
            self._shockwave_impact(player.pos, cfg["radius"], damage, now,
                                   color=color, shake=10)
            self.burn_zones.append({
                "pos": Vector2(player.pos),
                "radius": cfg["radius"] * 0.9,
                "damage": damage * 0.3,
                "timer": cfg.get("burn", 2.5),
                "interval": 0.4,
                "color": (255, 150, 60),
            })
            self.assets.play("jump_land")
            return

        if kind == "crystal_landing":
            # Pouso Cristalino: onda + estilhaços voando em 4 direções
            self._shockwave_impact(player.pos, cfg["radius"], damage, now,
                                   color=color, shake=10)
            for index in range(cfg.get("shards", 4)):
                direction = Vector2(1, 0).rotate(360 / cfg["shards"] * index)
                self._spawn_crystal_shard(player, direction, damage * 0.5, now)
            self.assets.play("jump_land")
            return

        # impact_jump (Ben+QB) e double_jump (QB+Ben): onda de pressão padrão
        self._shockwave_impact(player.pos, cfg["radius"], damage, now,
                               color=color, shake=10)
        player.fusion_jump_cfg = None
        self.assets.play("jump_land")

    # ------------------------------------------------------------------
    # Aplicação de dano em inimigo (compartilhada por todos os ataques)
    # ------------------------------------------------------------------
    def _on_enemy_hit(self, enemy: Enemy, damage: int, now: float) -> None:
        self.floating_texts.add(str(damage), enemy.pos, settings.COLORS["white"])
        self.particles.burst(enemy.pos, 8, settings.COLORS["white"], 160, 0.25, 3)
        # partículas modulares do traço da fusão (assinatura visual do parceiro)
        player = self.player_ref
        if player is not None and player.fusion:
            trait = settings.FUSION_TRAITS[player.fusion]["kind"]
            trait_color = settings.FUSION_TRAIT_PARTICLES.get(trait)
            if trait_color:
                self.particles.burst(enemy.pos, 5, trait_color, 180, 0.3, 3)
        if player is not None:
            lifesteal = player.lifesteal()
            if lifesteal > 0:
                player.health = min(player.max_health, player.health + damage * lifesteal)
            if player.state == "boost":
                pass  # turbo já mata por contato
            elif self._prism_gained < settings.PRISM_GAIN_PER_FRAME_CAP:
                gain = min(settings.PRISM_GAIN_PER_HIT,
                           settings.PRISM_GAIN_PER_FRAME_CAP - self._prism_gained)
                player.add_prism(gain)
                self._prism_gained += gain

    def _kill_enemy(self, enemy: Enemy) -> None:
        """Remove o inimigo e solta os drops (XP, vida, Núcleos Instáveis)."""
        self.particles.burst(enemy.pos, 14, settings.COLORS["purple"], 200, 0.35, 4)
        self.xp_orbs.append(XPOrb(enemy.pos + Vector2(random.uniform(-8, 8),
                                                     random.uniform(-8, 8)), enemy.xp))
        if random.random() < settings.HEALTH_ORB_CHANCE:
            self.health_orbs.append(HealthOrb(enemy.pos))
        if random.random() < settings.POWERUP_DROP_CHANCE:
            self.drop_powerup(enemy.pos)
        self.kills += 1

    def roll_powerup_key(self) -> str:
        """Sorteia um power-up: primeiro a raridade, depois o item (por peso)."""
        rarity = random.choices(settings.RARITY_ORDER,
                                weights=[settings.RARITY_WEIGHTS[r] for r in settings.RARITY_ORDER])[0]
        pool = [k for k, d in settings.POWERUP_DATA.items() if d["rarity"] == rarity]
        weights = [settings.POWERUP_DATA[k]["weight"] for k in pool]
        return random.choices(pool, weights=weights)[0]

    def drop_powerup(self, position) -> None:
        self.powerups.append(PowerUp(position, self.roll_powerup_key()))

    def _apply_powerup(self, player: Player, key: str, now: float) -> str:
        """Aplica o efeito de um Núcleo Instável. Retorna o nome exibido."""
        data = settings.POWERUP_DATA[key]
        kind = data["kind"]
        rarity = data["rarity"]

        if kind == "regen":   # Coração de Ben: cura imediata + regen
            player.health = min(player.max_health,
                                player.health + player.max_health * data["heal"])
            player.powerups[key] = data["duration"]
        elif kind == "shield":
            player.shield_charges = min(3, player.shield_charges + data["charges"])
        elif kind == "reset_cooldowns":
            player.primary_cd = 0.0
            player.special_cd = 0.0
            player._dash_ready_at = 0.0
        elif kind == "freeze":
            for enemy in self.enemies:
                enemy.apply_freeze(data["freeze_time"])
        elif kind == "enemy_wipe":
            wipe_damage = data["damage"] * player.damage_percent
            for enemy in self.enemies[:]:
                enemy.apply_damage(wipe_damage)
                if enemy.health > 0:
                    enemy.apply_weak(data["hp_cut"], data["duration"])
            self.request_shake(8, 0.3)
        elif kind == "waybig_fury":   # pisão na tela + buff
            self._explosion(player.pos, data["stomp_radius"],
                            (data["stomp_damage"] + player.base_damage) * player.damage_percent,
                            now, color=settings.RARITY_COLORS["legendary"], shake=14)
            player.powerups[key] = data["duration"]
        elif kind == "lucky":
            pool = [k for k, d in settings.POWERUP_DATA.items()
                    if d["rarity"] in data["levels"]]
            for _ in range(data["count"]):
                self._apply_powerup(player, random.choice(pool), now)
        elif kind == "clone":
            self._spawn_clones(player, data)
            player.powerups[key] = data["duration"]
        elif kind == "bomb_clock":
            player.powerups[key] = data["duration"]
            self.bomb_timer = data["interval"]   # primeira bomba depois de 1 intervalo
        elif kind == "chest_storm":
            player.powerups[key] = data["duration"]
            self.chest_timer = data["interval"]
        else:   # buffs de duração simples (speed, waybig, venom, lifesteal, magnet, explosivo, ricochete, minigun, quad_punch)
            player.powerups[key] = data["duration"]

        # anúncio arcade + tremor para raridades altas
        # tempo de leitura escala com o tamanho do nome (nomes longos ficam mais)
        duration = _banner_duration(data["name"])
        self.announcements.append({"text": data["name"].upper(), "rarity": rarity,
                                   "timer": duration, "max_timer": duration})
        if rarity in ("epic", "legendary"):
            self.request_shake(5 if rarity == "epic" else 8, 0.25)
        return data["name"]

    def drain_announcements(self) -> list[dict]:
        """Entrega os banners pendentes para o Game desenhar (e esvazia a fila)."""
        announcements = list(self.announcements)
        self.announcements.clear()
        return announcements

    def _spawn_clones(self, player: Player, data: dict) -> None:
        """Cria os clones (Sombra de Kevin / Clone Bagunçado)."""
        count = data["clones"]
        if isinstance(count, (tuple, list)):
            count = random.randint(*count)
        for _ in range(count):
            self.clones.append({
                "pos": Vector2(player.pos) + Vector2(random.uniform(-80, 80),
                                                     random.uniform(-80, 80)),
                "timer": data["duration"],
                "fire_cd": random.uniform(0.3, 1.0),
                "damage_mult": data["clone_damage"],
                "smart": data.get("smart", True),
                "vel": Vector2(random.uniform(-60, 60), random.uniform(-60, 60)),
            })

    def _update_clones(self, dt: float, now: float, player: Player) -> None:
        for clone in self.clones[:]:
            clone["timer"] -= dt
            if clone["timer"] <= 0:
                self.clones.remove(clone)
                continue
            clone["pos"] += clone["vel"] * dt
            if not clone["smart"]:
                if random.random() < 0.02:
                    clone["vel"] = Vector2(random.uniform(-90, 90), random.uniform(-90, 90))
            clone["fire_cd"] -= dt
            if clone["fire_cd"] <= 0:
                clone["fire_cd"] = 1.1
                target = None
                if clone["smart"] and self.enemies:
                    target = min(self.enemies, key=lambda e: e.pos.distance_to(clone["pos"]))
                direction = (target.pos - clone["pos"]) if target else \
                    Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                if direction.length_squared() > 1:
                    attack = {"type": "clone", "speed": 560, "range": 420,
                              "color": (170, 110, 255), "radius": 5}
                    damage = (1.0 + player.base_damage) * clone["damage_mult"]
                    damage *= player.damage_percent
                    self.projectiles.append(Projectile(clone["pos"], direction,
                                                       attack, damage, self.assets))

    # ------------------------------------------------------------------
    # Atualização
    # ------------------------------------------------------------------
    def update(self, dt: float, now: float, player: Player, camera) -> None:
        self.elapsed += dt
        self.player_ref = player
        self._prism_gained = 0.0   # o Prisma enche devagar: cap por frame

        # spawn de horda — fica mais rápida com o tempo (sempre longe do jogador)
        interval = max(settings.ENEMY_SPAWN_INTERVAL_MIN,
                       settings.ENEMY_SPAWN_INTERVAL_BASE - self.elapsed * 0.004)
        if now - self._last_spawn >= interval:
            self._last_spawn = now
            self.spawn_enemy_near_camera(camera, player.pos)

        if now - self._last_chest >= settings.CHEST_SPAWN_INTERVAL:
            self._last_chest = now
            self.spawn_chest()

        # inimigos perseguem o jogador
        for enemy in self.enemies:
            enemy.update(dt, player.pos, now)

        # projéteis (iteramos uma cópia porque eles podem ser removidos)
        for projectile in self.projectiles[:]:
            if projectile.update(dt):
                # Bola de Fogo que NÃO acertou ninguém e bateu no limite do
                # alcance deixa uma fogueira residual no chão (valor dos tiros
                # "errados" — semear fogo no caminho da horda). Se acertou,
                # a explosão de impacto já aconteceu (hit_any = True).
                if projectile.kind == "fireball" and not projectile.hit_any:
                    self.burn_zones.append({
                        "pos": Vector2(projectile.pos),
                        "radius": settings.FIREBALL_CAMPFIRE_RADIUS,
                        "damage": projectile.damage * settings.FIREBALL_CAMPFIRE_DAMAGE_MULT,
                        "timer": settings.FIREBALL_CAMPFIRE_DURATION,
                        "interval": 0.4,
                        "color": (255, 150, 60),
                    })
                self.projectiles.remove(projectile)
                continue
            # rastro de luz (na cor da fusão, se o projétil tiver traço)
            projectile.trail_timer -= dt
            if projectile.trail_timer <= 0:
                projectile.trail_timer = 0.03
                trail_color = projectile.glow_color or projectile.color
                self.particles.burst(projectile.pos, 1, trail_color, 30, 0.2, 2)
            # colisão com inimigos
            for enemy in self.enemies:
                if id(enemy) in projectile.hit_ids:
                    continue
                if projectile.pos.distance_to(enemy.pos) < enemy.size[0] / 2 + projectile.radius:
                    final = self._apply_combos(player, projectile.damage, now)
                    enemy.apply_damage(final, projectile.dir, projectile.knockback)
                    self._on_enemy_hit(enemy, int(final), now)
                    projectile.hit_ids.add(id(enemy))
                    projectile.hit_any = True
                    projectile.pierce -= 1
                    # bola de fogo: explode ao atingir (dano em área)
                    if projectile.explosion_radius > 0:
                        self._explosion(projectile.pos, projectile.explosion_radius,
                                        projectile.explosion_damage, now,
                                        color=projectile.color, shake=5)
                        projectile.traveled = projectile.max_range
                        break
                    # Ricochete Diamante: pula para o inimigo mais próximo
                    if projectile.ricochet_left > 0:
                        others = [e for e in self.enemies if id(e) not in projectile.hit_ids]
                        if others:
                            nxt = min(others, key=lambda e: e.pos.distance_to(projectile.pos))
                            projectile.dir = (nxt.pos - projectile.pos).normalize()
                            projectile.ricochet_left -= 1
                            continue
                    if projectile.pierce < 0:
                        # Estilhaço em CASCATA: perfurou o teto de alvos e ainda
                        # tem alcance -> sobra um 2º estilhaço menor continuando
                        remaining = 1 - projectile.traveled / projectile.max_range
                        if (projectile.kind == "diamond_shot"
                                and remaining >= settings.SHARD_SPLIT_MIN_FRACTION
                                and not projectile.explosion_radius):
                            child_attack = {"type": "diamond_shot",
                                             "speed": projectile.speed,
                                             "range": projectile.max_range
                                                       * settings.SHARD_SPLIT_RANGE_MULT,
                                             "color": projectile.color,
                                             "radius": max(3, projectile.radius - 2),
                                             "pierce": settings.SHARD_SPLIT_PIERCE}
                            child = Projectile(projectile.pos, projectile.dir,
                                               child_attack,
                                               projectile.damage
                                               * settings.SHARD_SPLIT_DAMAGE_MULT,
                                               self.assets)
                            child.sprite = self.assets.get_effects("crystal_shard")
                            child.hit_ids = set(projectile.hit_ids)
                            self.projectiles.append(child)
                            self.particles.burst(projectile.pos, 6,
                                                 settings.COLORS["diamond_cyan"],
                                                 140, 0.3, 3)
                        projectile.traveled = projectile.max_range  # some no próximo frame
                        break
            # colisão com baús
            for chest in self.chests[:]:
                if projectile.pos.distance_to(chest.pos) < 40:
                    self.damage_chest(chest, projectile.damage, now)
                    projectile.traveled = projectile.max_range
                    break

        # inimigo encosta no jogador: causa dano e morre
        for enemy in self.enemies[:]:
            if player.rect.collidepoint(enemy.pos):
                self._enemy_touches_player(enemy, player, now)

        # cristais orbitando (Diamante) — rotação e tamanho por cristal
        for crystal in self.crystals[:]:
            crystal["duration"] -= dt
            if crystal["duration"] <= 0:
                self.crystals.remove(crystal)
                continue
            spin = crystal.get("spin", 2.2)
            crystal["angle"] += dt * spin
            crystal["pos"] = player.pos + Vector2(math.cos(crystal["angle"]),
                                                  math.sin(crystal["angle"])) * crystal["orbit_radius"]
            hit_radius = crystal.get("size", 10) * 0.7
            knock = crystal.get("knockback", 40)
            if crystal.get("fire"):
                # Campo em Chamas: rastro de fogo + queimadura em quem encostar
                self.particles.burst(crystal["pos"], 1, (255, 150, 60), 40, 0.4, 3)
            # Muralha de cristal: empurra inimigos próximos (obstáculo físico)
            for enemy in self.enemies:
                delta = enemy.pos - crystal["pos"]
                if delta.length() < settings.CRYSTAL_PUSH_RADIUS + enemy.size[0] / 2:
                    if delta.length_squared() > 1:
                        enemy.knockback += delta.normalize() \
                            * settings.CRYSTAL_PUSH_STRENGTH * dt
            for enemy in self.enemies:
                if id(enemy) in crystal["hit_ids"]:
                    continue
                if enemy.pos.distance_to(crystal["pos"]) < enemy.size[0] / 2 + hit_radius:
                    enemy.apply_damage(crystal["damage"], enemy.pos - player.pos, knock)
                    self._on_enemy_hit(enemy, int(crystal["damage"]), now)
                    crystal["hit_ids"].add(id(enemy))
                    color = (255, 150, 60) if crystal.get("fire") else settings.COLORS["diamond_cyan"]
                    self.particles.burst(crystal["pos"], 6, color, 120, 0.3, 3)
                    if crystal.get("fire"):
                        enemy.apply_damage(crystal["damage"] * 0.4)   # queimadura extra
            # cristais também quebram baús no caminho (uma vez por cristal)
            for chest in self.chests:
                if id(chest) in crystal["hit_ids"]:
                    continue
                if chest.pos.distance_to(crystal["pos"]) < settings.CHEST_SIZE / 2 + hit_radius:
                    self.damage_chest(chest, crystal["damage"], now)
                    crystal["hit_ids"].add(id(chest))

        # orbes de XP e vida (ímã + coleta)
        player_pos = player.pos
        for orb in self.xp_orbs[:]:
            if orb.update(dt, player_pos):
                self.xp_orbs.remove(orb)
                player.add_xp(orb.value)
                player.add_prism(settings.PRISM_GAIN_PER_XP)  # orbes dão um pouco de Prisma
        for orb in self.health_orbs[:]:
            if orb.update(dt, player_pos):
                self.health_orbs.remove(orb)
                player.health = min(player.max_health, player.health + 1)
                if "fome_voraz" in player.powerups:
                    player.health = min(player.max_health, player.health + 1)

        # Núcleos Instáveis no chão (ímã + coleta instantânea)
        magnet = player.magnet_mult()
        for core in self.powerups[:]:
            if core.update(dt, player_pos, magnet):
                self.powerups.remove(core)
                self._apply_powerup(player, core.key, now)
                player.add_prism(settings.PRISM_GAIN_PER_ORB)
                self.assets.play("level_up")

        # Bomba Relógio: explosão periódica no jogador (não machuca ele)
        if "bomba_relogio" in player.powerups:
            data = settings.POWERUP_DATA["bomba_relogio"]
            self.bomb_timer -= dt
            if self.bomb_timer <= 0:
                self.bomb_timer = data["interval"]
                self._explosion(player.pos, data["radius"],
                                (data["damage"] + player.base_damage) * player.damage_percent,
                                now, color=(255, 140, 40), shake=4)

        # Caos do Baú Mágico: baús extras caindo
        if "caos_bau" in player.powerups:
            data = settings.POWERUP_DATA["caos_bau"]
            self.chest_timer -= dt
            if self.chest_timer <= 0:
                self.chest_timer = data["interval"]
                self.spawn_chest_near(player.pos)

        # Campo Anti-Gravidade: inimigos próximos ficam lentos
        if "campo_gravidade" in player.powerups:
            data = settings.POWERUP_DATA["campo_gravidade"]
            for enemy in self.enemies:
                if enemy.pos.distance_to(player.pos) < 520:
                    enemy.apply_slow(0.2, data["slow_mult"])

        # clones (Sombra de Kevin / Clone Bagunçado)
        self._update_clones(dt, now, player)

        # zonas de lentidão (rachadura do Super Pulmão) e ecos do turbo (XLR8)
        self._update_slow_zones(dt, now)
        self._update_echoes(dt, now)

        # passivos de fusão (terceira camada): efeitos automáticos por par
        if player.fusion:
            passive = settings.FUSION_PASSIVES.get((player.alien_name, player.fusion))
            if passive:
                kind = passive.get("kind")
                if kind == "crystal_trail":
                    # Esteira de Cristais: fragmentos no chão que somem em 1s
                    if random.random() < dt * 14:
                        self.effects.append({
                            "kind": "crystal_trail",
                            "center": player.pos + Vector2(random.uniform(-30, 30),
                                                           random.uniform(-30, 30)),
                            "lifetime": 0.9, "max_lifetime": 0.9,
                        })
                elif kind == "smoke_aura":
                    # Pouso Vulcânico: colunas de fumaça ao redor
                    if random.random() < dt * 6:
                        offset = Vector2(random.uniform(-40, 40), random.uniform(-40, 40))
                        self.particles.burst(player.pos + offset, 2, (120, 115, 125),
                                             40, 0.8, 2)

        # linhas de velocidade do turbo (XLR8): rastro "Sonic/Flash" atrás
        if player.state == "boost":
            self._boost_line_timer -= dt
            if self._boost_line_timer <= 0:
                self._boost_line_timer = 0.045
                back = player.pos - player.aim_dir * 34
                self.effects.append({
                    "kind": "line", "start": back - player.aim_dir * 26,
                    "end": back - player.aim_dir * 12,
                    "color": (140, 200, 255), "lifetime": 0.16, "max_lifetime": 0.16,
                })

        # pulso visual da fusão: anel que "respira" na cor do traço emprestado
        if player.fusion:
            self.fusion_pulse -= dt
            if self.fusion_pulse <= 0:
                self.fusion_pulse = 1.1
                trait_color = settings.FUSION_TRAITS[player.fusion]["color"]
                self.effects.append({
                    "kind": "ring", "center": Vector2(player.pos), "radius": 50,
                    "color": trait_color, "lifetime": 0.5, "max_lifetime": 0.5,
                })
                self.particles.burst(player.pos, 6, trait_color, 80, 0.4, 3)

        # baús e efeitos temporários
        for chest in self.chests:
            chest.update(dt)
        # piso visual: efeitos não "piscam" em 1 frame — só são removidos depois
        # de MIN_EFFECT_DISPLAY na tela, mesmo que a vida do efeito já tenha
        # acabado. Efeitos longos (rachaduras, explosões) não são estendidos.
        for effect in self.effects[:]:
            effect["age"] = effect.get("age", 0.0) + dt
            effect["lifetime"] -= dt
            if effect["lifetime"] <= 0 and effect["age"] >= settings.MIN_EFFECT_DISPLAY:
                self.effects.remove(effect)

        # inimigos mortos viram drops de XP (e contam como abates)
        for enemy in self.enemies[:]:
            if enemy.health <= 0:
                self.enemies.remove(enemy)
                self._kill_enemy(enemy)

        # --- Sistemas dos especiais de fusão (Fase 2) ---
        self._update_pending_explosions(now)
        self._update_burn_zones(dt, now)
        self._update_trails(dt, now)
        self._update_rush(player, now)

    def _update_pending_explosions(self, now: float) -> None:
        """Explosões atrasadas (Supernova Dupla / Supernova em Cadeia)."""
        for pending in self.pending_explosions[:]:
            if now >= pending["time"]:
                self._explosion(pending["pos"], pending["radius"], pending["damage"],
                                now, color=pending["color"], shake=pending.get("shake", 8),
                                flame_ring=True)
                self.pending_explosions.remove(pending)

    def _update_burn_zones(self, dt: float, now: float) -> None:
        """Anel de fogo residual (Pouso Vulcânico): queima inimigos por um tempo."""
        for zone in self.burn_zones[:]:
            zone["timer"] -= dt
            if zone["timer"] <= 0:
                self.burn_zones.remove(zone)
                continue
            zone.setdefault("interval_cd", 0.0)
            zone["interval_cd"] -= dt
            if zone["interval_cd"] <= 0:
                zone["interval_cd"] = zone["interval"]
                for enemy in self.enemies:
                    if enemy.pos.distance_to(zone["pos"]) <= zone["radius"]:
                        enemy.apply_damage(zone["damage"], enemy.pos - zone["pos"], 60)
                        self._on_enemy_hit(enemy, int(zone["damage"]), now)
                self.particles.burst(zone["pos"], 5, zone["color"], 80, 0.4, 4)

    def _update_slow_zones(self, dt: float, now: float) -> None:
        """Zonas de lentidão (rachadura do Super Pulmão): inimigos dentro ficam lentos."""
        for zone in self.slow_zones[:]:
            zone["timer"] -= dt
            if zone["timer"] <= 0:
                self.slow_zones.remove(zone)
                continue
            for enemy in self.enemies:
                if enemy.pos.distance_to(zone["pos"]) <= zone["radius"]:
                    enemy.apply_slow(0.15, zone["slow_mult"])

    def _update_echoes(self, dt: float, now: float) -> None:
        """Ecos do turbo (XLR8): correm em linha reta e atropelam inimigos."""
        for echo in self.echoes[:]:
            echo["timer"] -= dt
            if echo["timer"] <= 0:
                self.echoes.remove(echo)
                continue
            echo["pos"] += echo["dir"] * settings.TURBO_ECHO_SPEED * dt
            for enemy in self.enemies:
                if id(enemy) in echo["hit_ids"]:
                    continue
                if enemy.pos.distance_to(echo["pos"]) < 30 + enemy.size[0] / 2:
                    enemy.apply_damage(echo["damage"], echo["dir"], 120)
                    self._on_enemy_hit(enemy, int(echo["damage"]), now)
                    echo["hit_ids"].add(id(enemy))
                    self.particles.burst(enemy.pos, 6, settings.COLORS["xlr8_blue"],
                                         200, 0.3, 3)

    def _update_trails(self, dt: float, now: float) -> None:
        """Rastros de turbo (Rastro de Impacto / Turbo em Chamas)."""
        player = self.player_ref
        # o rastro pertence à fusão: se ela acabar no meio do turbo, para de soltar
        if (player is not None and player.fusion
                and player.state == "boost" and self.boost_trail_cfg):
            # solta um pedaço do rastro a cada 0.06s durante o turbo
            self.boost_trail_cfg.setdefault("timer", 0.0)
            self.boost_trail_cfg["timer"] -= dt
            if self.boost_trail_cfg["timer"] <= 0:
                self.boost_trail_cfg["timer"] = 0.06
                self.trails.append({
                    "pos": Vector2(player.pos),
                    "damage": self.boost_trail_cfg["damage"],
                    "fire": self.boost_trail_cfg["type"] == "fire_trail",
                    "color": self.boost_trail_cfg["color"],
                    "lifetime": 0.9, "max_lifetime": 0.9,
                    "hit_ids": set(),
                })
        else:
            self.boost_trail_cfg = None
        # pedaços existentes: empurram/danificam quem passar por cima
        for trail in self.trails[:]:
            trail["lifetime"] -= dt
            if trail["lifetime"] <= 0:
                self.trails.remove(trail)
                continue
            for enemy in self.enemies:
                if id(enemy) in trail["hit_ids"]:
                    continue
                if enemy.pos.distance_to(trail["pos"]) < 46:
                    enemy.apply_damage(trail["damage"], enemy.pos - trail["pos"], 140)
                    self._on_enemy_hit(enemy, int(trail["damage"]), now)
                    trail["hit_ids"].add(id(enemy))
                    if trail["fire"]:
                        self.particles.burst(enemy.pos, 6, (255, 150, 60), 140, 0.4, 3)

    def _update_rush(self, player: Player, now: float) -> None:
        """Investida Relâmpago (Ben+XLR8): danifica inimigos na linha do dash."""
        if player.state != "rush":
            return
        damage = getattr(player, "rush_damage", 0.0)
        if damage <= 0:
            return
        # danifica inimigos perto da linha de avanço (uma vez por investida)
        # o corredor cobre a DISTÂNCIA TOTAL do dash (não apenas parte dele)
        reach = getattr(player, "rush_distance", 340)
        for enemy in self.enemies:
            if id(enemy) in player.rush_hit_ids:
                continue
            to_enemy = enemy.pos - player.pos
            lateral = abs(to_enemy.cross(player.rush_dir))
            forward = to_enemy.dot(player.rush_dir)
            if -30 <= forward <= reach + 20 and lateral <= 70 + enemy.size[0] * 0.4:
                enemy.apply_damage(damage, player.rush_dir, 240)
                self._on_enemy_hit(enemy, int(damage), now)
                player.rush_hit_ids.add(id(enemy))
                self.particles.burst(enemy.pos, 8, settings.COLORS["xlr8_blue"], 220, 0.3, 3)

    def _enemy_touches_player(self, enemy: Enemy, player: Player, now: float) -> None:
        if player.state == "boost":
            damage = settings.ALIEN_DATA["XLR8"]["special"]["contact_damage"]
            damage *= player.damage_percent
            enemy.apply_damage(damage)
            self._on_enemy_hit(enemy, damage, now)
            self.floating_texts.add(str(damage), enemy.pos, settings.COLORS["yellow"])
            # Eco do turbo: um clone-fantasma continua correndo reto por ~1s
            # causando dano no caminho (efeito cascata, sem turbo mais longo).
            direction = player.vel if player.vel.length() > 40 else player.aim_dir
            if direction.length_squared() > 1:
                self.echoes.append({
                    "pos": Vector2(player.pos),
                    "dir": direction.normalize(),
                    "timer": settings.TURBO_ECHO_DURATION,
                    "damage": damage * settings.TURBO_ECHO_DAMAGE_MULT,
                    "hit_ids": set(),
                })
        elif player.take_damage(enemy.damage, now):
            self.floating_texts.add(f"-{enemy.damage}", player.pos, settings.COLORS["damage_red"])
            self.particles.burst(player.pos, 12, settings.COLORS["damage_red"], 180, 0.3, 4)
        # o inimigo morre ao encostar (evita empilhamento sobre o jogador)
        self.enemies.remove(enemy)
        self._kill_enemy(enemy)

    def damage_chest(self, chest: Chest, damage: float, now: float) -> None:
        chest.apply_damage(damage)
        if chest.health <= 0:
            self.chests.remove(chest)
            for _ in range(3):
                self.health_orbs.append(HealthOrb(chest.pos + Vector2(random.uniform(-15, 15),
                                                                      random.uniform(-15, 15))))
            self.drop_powerup(chest.pos)   # baú sempre solta um Núcleo Instável

    # ------------------------------------------------------------------
    # Desenho (no surface do mundo, que depois a câmera inclina)
    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, world_offset, now: float) -> None:
        # decorações do mapa (castelos/pedras ao fundo — puramente visuais)
        for decoration in self.decorations:
            sprite = decoration.get("image")
            if sprite is not None:
                surface.blit(sprite, sprite.get_rect(center=decoration["pos"] - world_offset))
        for chest in self.chests:
            chest.draw(surface, world_offset, self.assets)
        for enemy in self.enemies:
            enemy.draw(surface, world_offset, self.assets)
        for orb in self.xp_orbs:
            orb.draw(surface, world_offset)
        for orb in self.health_orbs:
            orb.draw(surface, world_offset, self.assets)
        for core in self.powerups:
            core.draw(surface, world_offset, self.assets)
        # clones (Sombra de Kevin / Clone Bagunçado)
        for clone in self.clones:
            pos = clone["pos"] - world_offset
            pygame.draw.circle(surface, (170, 110, 255), pos, 14)
            pygame.draw.circle(surface, (230, 210, 255), pos, 7)
        for projectile in self.projectiles:
            projectile.draw(surface, world_offset)
        # cristais orbitando (posição calculada no update) — tamanho por cristal
        crystal_img = self.assets.get_effects("crystal_orb")
        for crystal in self.crystals:
            pos = crystal.get("pos", crystal.get("center", Vector2())) - world_offset
            size = crystal.get("size", 10)
            color = (255, 160, 70) if crystal.get("fire") else settings.COLORS["diamond_cyan"]
            if crystal.get("fire"):
                pygame.draw.circle(surface, (255, 120, 40), pos, int(size * 1.4), 2)
            if crystal_img is not None:
                scaled = pygame.transform.scale(crystal_img, (size * 2, size * 2))
                surface.blit(scaled, scaled.get_rect(center=pos))
            else:
                pygame.draw.circle(surface, color, pos, size)
                pygame.draw.circle(surface, (220, 255, 255), pos, size // 2)
        # efeitos temporários (arcos, retângulos, raios, explosões e anéis)
        for effect in self.effects:
            if effect["kind"] == "arc":
                self._draw_arc(surface, world_offset, effect)
            elif effect["kind"] == "rect":
                image = effect["image"]
                surface.blit(image, image.get_rect(center=effect["center"] - world_offset))
            elif effect["kind"] == "bolt":
                self._draw_bolt(surface, world_offset, effect)
            elif effect["kind"] == "explosion":
                self._draw_explosion(surface, world_offset, effect)
            elif effect["kind"] == "shockwave":
                self._draw_shockwave(surface, world_offset, effect)
            elif effect["kind"] == "flame_ring":
                self._draw_flame_ring(surface, world_offset, effect)
            elif effect["kind"] == "cracks":
                self._draw_cracks(surface, world_offset, effect)
            elif effect["kind"] == "rock_debris":
                self._draw_rock_debris(surface, world_offset, effect)
            elif effect["kind"] == "line":
                pygame.draw.line(surface, effect["color"],
                                 effect["start"] - world_offset,
                                 effect["end"] - world_offset, 4)
            elif effect["kind"] == "ring":
                progress = 1 - effect["lifetime"] / effect["max_lifetime"]
                radius = effect["radius"] * progress
                pygame.draw.circle(surface, effect["color"],
                                   effect["center"] - world_offset, int(radius), 3)
            elif effect["kind"] == "crystal_trail":
                # Esteira de Cristais (passivo XLR8+Diamante): fragmentos no chão
                progress = 1 - effect["lifetime"] / effect["max_lifetime"]
                pos = effect["center"] - world_offset
                size = max(1, int(3 * progress))
                pygame.draw.circle(surface, (150, 230, 255), pos, size)
                pygame.draw.circle(surface, (220, 250, 255), pos, max(1, size // 2))
        # rastros de turbo (Rastro de Impacto / Turbo em Chamas)
        for trail in self.trails:
            self._draw_trail(surface, world_offset, trail)
        # zonas de fogo residuais (Pouso Vulcânico)
        for zone in self.burn_zones:
            self._draw_burn_zone(surface, world_offset, zone)
        # zonas de lentidão (rachadura do Super Pulmão)
        for zone in self.slow_zones:
            self._draw_slow_zone(surface, world_offset, zone)
        # ecos do turbo (XLR8: clone-fantasma correndo)
        for echo in self.echoes:
            self._draw_echo(surface, world_offset, echo)

    def _draw_shockwave(self, surface: pygame.Surface, world_offset, effect: dict) -> None:
        """Onda de pressão cinética: anel irregular expandindo + raios de velocidade.

        Desenhada em um overlay pequeno (SRCALPHA) ao redor do centro, com
        jitter procedural para parecer uma frente de choque "quebrada".
        """
        center = effect["center"] - world_offset
        progress = 1 - effect["lifetime"] / effect["max_lifetime"]
        radius = effect["radius"] * (0.25 + 0.75 * progress)
        alpha = int(170 * (1 - progress))
        color = effect["color"]
        seed = effect["seed"]
        if radius < 4:
            return
        margin = int(radius) + 24
        overlay = pygame.Surface((margin * 2, margin * 2), pygame.SRCALPHA)
        origin = Vector2(margin, margin)
        steps = 18
        # frente de choque: polígono irregular (jitter procedural estável)
        points = []
        for index in range(steps):
            angle = math.tau * index / steps + seed
            jitter = 1 + 0.14 * math.sin(seed * 13 + index * 2.7)
            jitter += 0.07 * math.sin(seed * 7 + index * 1.3)
            points.append(origin + Vector2(math.cos(angle), math.sin(angle))
                          * (radius * jitter))
        pygame.draw.polygon(overlay, (*color, alpha), points, 3)
        # raios de velocidade radiais (do choque para fora)
        for index in range(0, steps, 2):
            angle = math.tau * index / steps + seed
            direction = Vector2(math.cos(angle), math.sin(angle))
            jitter = 1 + 0.14 * math.sin(seed * 13 + index * 2.7)
            inner = origin + direction * (radius * jitter - 8)
            outer = origin + direction * (radius * jitter + 14)
            pygame.draw.line(overlay, (*color, alpha), inner, outer, 2)
        # núcleo claro (ponto do impacto)
        pygame.draw.circle(overlay, (255, 255, 255, alpha), origin,
                           max(2, int(radius * 0.12)), 2)
        surface.blit(overlay, overlay.get_rect(center=center))

    def _draw_bolt(self, surface: pygame.Surface, world_offset, effect: dict) -> None:
        """Cadeia do XLR8: raio em zigue-zague ("zzzt") + sprite de raio.

        O zigue-zague dá a leitura de garras eletrizadas riscando o ar, e o
        traço tracejado reforça a velocidade entre os golpes da cadeia.
        """
        start = effect["start"] - world_offset
        end = effect["end"] - world_offset
        delta = end - start
        length = delta.length()
        if length < 8:
            return
        seed = effect.get("seed", 0.0)
        # linha de fusão fina por baixo (cor do traço emprestado)
        pygame.draw.line(surface, effect["color"], start, end, 2)
        # zigue-zague "zzzt": pontos com desvio perpendicular determinado por seed
        steps = 8
        jagged = [start]
        for step in range(1, steps):
            t = step / steps
            base = start + delta * t
            jitter = math.sin(seed * 13 + step * 2.7) * min(14, length * 0.1)
            perp = Vector2(-delta.y, delta.x)
            if perp.length_squared() > 1:
                perp = perp.normalize()
            jagged.append(base + perp * jitter)
        jagged.append(end)
        pygame.draw.lines(surface, (235, 250, 255), False, jagged, 2)
        # faíscas nas pontas do salto
        self.particles.burst(effect["start"], 3, (180, 230, 255), 140, 0.25, 2)
        self.particles.burst(effect["end"], 3, (180, 230, 255), 140, 0.25, 2)
        # sprite de raio esticado e rotacionado entre os dois pontos
        bolt = self.assets.get_effects("lightning_bolt")
        if bolt is None:
            pygame.draw.line(surface, (255, 230, 120), start, end, 4)
            return
        angle = math.degrees(math.atan2(delta.y, delta.x))
        scaled = pygame.transform.scale(bolt, (int(length), max(4, int(bolt.get_height()))))
        rotated = pygame.transform.rotate(scaled, -angle)
        surface.blit(rotated, rotated.get_rect(center=(start + end) / 2))

    def _draw_explosion(self, surface: pygame.Surface, world_offset, effect: dict) -> None:
        """Animação da sprite sheet de explosão (progresso 0..1 -> quadro).

        O número de quadros EXIBIDOS é limitado pelo tempo mínimo por quadro
        (MIN_SPRITE_FRAME_TIME): uma explosão de 24 quadros em 0.45s daria
        ~19ms/quadro — rápido demais para o olho registrar como sequência.
        Mostra no máximo max_lifetime / min_frame_time quadros.
        """
        frames = effect["frames"]
        if not frames:
            return
        progress = 1 - effect["lifetime"] / effect["max_lifetime"]
        max_shown = max(1, min(len(frames),
                               int(effect["max_lifetime"] / settings.MIN_SPRITE_FRAME_TIME)))
        index = min(max_shown - 1, int(progress * max_shown))
        image = frames[index]
        surface.blit(image, image.get_rect(center=effect["center"] - world_offset))

    def _draw_arc(self, surface: pygame.Surface, world_offset, effect: dict) -> None:
        """Desenha o golpe em arco (soco do Ben) com afterimage de velocidade.

        O arco principal vem com 2 fantasmas menores atrás (na direção oposta
        ao golpe), dando a leitura de "punho atravessando o ar" — silhueta
        primeiro, detalhe depois, como manda a direção de arte das armas.
        """
        center = effect["center"] - world_offset
        progress = effect["lifetime"] / effect["max_lifetime"]
        color = effect["color"]
        # fantasmas (afterimage): arcos menores, mais transparentes, atrás
        if effect.get("afterimage", True):
            for ghost_scale, ghost_alpha in ((0.55, 40), (0.75, 80)):
                radius = max(6, effect["radius"] * ghost_scale)
                back = -0.22 * effect["radius"] * (1 - ghost_scale)
                self._draw_arc_shape(surface, center + Vector2(math.cos(math.radians(effect["start_angle"])),
                                                              math.sin(math.radians(effect["start_angle"]))) * back,
                                     radius, effect["start_angle"], effect["arc_degrees"],
                                     color, int(ghost_alpha * progress))
        self._draw_arc_shape(surface, center, effect["radius"], effect["start_angle"],
                             effect["arc_degrees"], color, int(150 * progress))

    def _draw_arc_shape(self, surface, center, radius, start_angle, arc_degrees,
                        color, alpha) -> None:
        """Desenha um único arco (polígono de fatia) em overlay PEQUENO.

        Overlay do tamanho do arco (bounded) em vez de um full-screen — o soco
        do Ben é o ataque mais rápido do jogo, então alocar 3 overlays de tela
        inteira por golpe era caro demais.
        """
        if alpha <= 0 or radius <= 4:
            return
        start = math.radians(start_angle - arc_degrees / 2)
        end = math.radians(start_angle + arc_degrees / 2)
        steps = 14
        size = int(radius * 2) + 10
        overlay = pygame.Surface((size, size), pygame.SRCALPHA)
        origin = Vector2(size / 2, size / 2)
        points = [origin]
        for step in range(steps + 1):
            angle = start + (end - start) * step / steps
            points.append(origin + Vector2(math.cos(angle), math.sin(angle)) * radius)
        pygame.draw.polygon(overlay, (*color, alpha), points)
        # borda luminosa da "lâmina" do golpe (silhueta primeiro, detalhe depois)
        edge = []
        for step in range(steps + 1):
            angle = start + (end - start) * step / steps
            edge.append(origin + Vector2(math.cos(angle), math.sin(angle)) * radius)
        if len(edge) > 2:
            pygame.draw.lines(overlay, (*color, min(255, alpha + 60)), False, edge, 3)
        surface.blit(overlay, overlay.get_rect(center=center))

    def _draw_flame_ring(self, surface: pygame.Surface, world_offset, effect: dict) -> None:
        """Anel de fogo da Supernova: línguas irregulares saindo para fora.

        Em vez de um círculo liso, 9 picos assimétricos (determinados por seed)
        que expandem — a leitura clássica de "supernova" em pixel art.
        """
        center = effect["center"] - world_offset
        progress = 1 - effect["lifetime"] / effect["max_lifetime"]
        radius = max(6, effect["radius"] * (0.35 + 0.65 * progress))
        alpha = int(170 * (1 - progress))
        seed = effect["seed"]
        color = effect["color"]
        margin = int(radius * 1.3) + 24
        overlay = pygame.Surface((margin * 2, margin * 2), pygame.SRCALPHA)
        origin = Vector2(margin, margin)
        tongues = 9
        points = []
        for index in range(tongues * 2):
            angle = math.pi * index / tongues + seed
            if index % 2 == 0:
                rr = radius * (0.8 + 0.15 * math.sin(seed * 5 + index))
            else:
                # língua de fogo: ponta comprida e assimétrica
                rr = radius * (1.15 + 0.3 * abs(math.sin(seed * 7 + index * 1.9)))
            points.append(origin + Vector2(math.cos(angle), math.sin(angle)) * rr)
        pygame.draw.polygon(overlay, (*color, alpha), points)
        # núcleo quente branco-amarelado
        pygame.draw.circle(overlay, (255, 240, 190, int(alpha * 0.8)),
                           origin, int(radius * 0.45))
        surface.blit(overlay, overlay.get_rect(center=center))

    def _draw_cracks(self, surface: pygame.Surface, world_offset, effect: dict) -> None:
        """Rachaduras pixeladas no chão (Quatro Braços): cicatriz do impacto.

        Ficam por ~1.6s após a pancada/pouso, com linhas quebradas irradiando
        do ponto de impacto — o "golpe de força bruta" deixando marca.
        """
        center = effect["center"] - world_offset
        progress = 1 - effect["lifetime"] / effect["max_lifetime"]
        radius = effect["radius"]
        alpha = int(150 * (1 - progress))
        seed = effect["seed"]
        color = effect["color"]
        if radius < 8:
            return
        margin = int(radius) + 24
        overlay = pygame.Surface((margin * 2, margin * 2), pygame.SRCALPHA)
        origin = Vector2(margin, margin)
        branches = 7
        for branch in range(branches):
            angle = math.tau * branch / branches + seed
            points = [origin]
            segments = 4
            for seg in range(1, segments + 1):
                length = radius * seg / segments
                jitter_angle = angle + math.sin(seed * 11 + branch * 3 + seg) * 0.5
                point = origin + Vector2(math.cos(jitter_angle), math.sin(jitter_angle)) * length
                points.append(point)
            pygame.draw.lines(overlay, (*color, alpha), False, points, 2)
        surface.blit(overlay, overlay.get_rect(center=center))

    def _draw_rock_debris(self, surface: pygame.Surface, world_offset, effect: dict) -> None:
        """Pedras voando do impacto da pancada (pixel art de item).

        Detritos arremessados para os lados como se o chão tivesse quebrado
        de verdade — a força bruta do Quatro Braços jogando pedras.
        """
        sprite = effect.get("sprite")
        if sprite is None:
            return
        center = effect["center"] - world_offset
        progress = 1 - effect["lifetime"] / effect["max_lifetime"]
        seed = effect["seed"]
        spread = effect.get("spread", 90)
        count = effect.get("count", 5)
        for index in range(count):
            angle = seed + math.tau * index / count
            distance = spread * (0.25 + 0.75 * progress)
            size = 14 + (index % 3) * 4
            rock = pygame.transform.scale(sprite, (size, size))
            rotated = pygame.transform.rotate(rock, progress * 300 + index * 40)
            pos = center + Vector2(math.cos(angle), math.sin(angle)) * distance
            surface.blit(rotated, rotated.get_rect(center=pos))

    def _draw_trail(self, surface: pygame.Surface, world_offset, trail: dict) -> None:
        """Pedaço do rastro de turbo: círculo que encolhe e some."""
        pos = trail["pos"] - world_offset
        progress = trail["lifetime"] / trail["max_lifetime"]
        radius = int(18 * progress)
        if radius < 2:
            return
        color = (255, 150, 60) if trail.get("fire") else trail["color"]
        pygame.draw.circle(surface, color, pos, radius, 2)
        pygame.draw.circle(surface, (*color, 60), pos, max(2, radius - 3))

    def _draw_burn_zone(self, surface: pygame.Surface, world_offset, zone: dict) -> None:
        """Anel de fogo residual (Pouso Vulcânico) queimando no chão."""
        pos = zone["pos"] - world_offset
        pulse = 0.7 + 0.3 * math.sin(self.elapsed * 6 + zone["pos"].x * 0.01)
        radius = int(zone["radius"] * pulse)
        pygame.draw.circle(surface, (255, 120, 40), pos, radius, 2)
        pygame.draw.circle(surface, (255, 200, 90), pos, max(2, int(radius * 0.5)), 2)

    def _draw_slow_zone(self, surface: pygame.Surface, world_offset, zone: dict) -> None:
        """Rachadura de lentidão (Super Pulmão): zona cinza pulsando no chão."""
        pos = zone["pos"] - world_offset
        pulse = 0.7 + 0.3 * math.sin(self.elapsed * 4 + zone["pos"].x * 0.02)
        radius = int(zone["radius"] * pulse)
        pygame.draw.circle(surface, zone["color"], pos, radius, 2)
        pygame.draw.circle(surface, (120, 120, 135), pos, max(2, int(radius * 0.35)), 1)

    def _draw_echo(self, surface: pygame.Surface, world_offset, echo: dict) -> None:
        """Eco do turbo do XLR8: fantasma azul translúcido correndo."""
        pos = echo["pos"] - world_offset
        ghost = pygame.Surface((26, 26), pygame.SRCALPHA)
        ghost.fill((140, 200, 255, 70))
        surface.blit(ghost, ghost.get_rect(center=pos))
        pygame.draw.circle(surface, (140, 200, 255), pos, 11, 2)
        # linhas de velocidade atrás do fantasma
        back = pos - echo["dir"] * 20
        pygame.draw.line(surface, (120, 180, 240), back, pos, 2)
