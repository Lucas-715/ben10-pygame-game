"""
game.py — O Game: liga tudo (assets, mundo, câmera, HUD) e roda o loop.

Estados possíveis (máquina de estados):
    title      -> tela inicial
    playing    -> o jogo em si
    level_up   -> escolha de upgrade (pausa o mundo)
    paused     -> pausa com ESC
    game_over  -> fim de jogo
"""
import json
import random
import sys

import pygame
from pygame import Vector2

from . import settings
from .assets import AssetBank
from .audio import MusicManager
from .camera import Camera
from .effects import FloatingTexts, ParticleSystem
from .entities import Player
from .ui import HUD
from .world import Chest, World, _banner_duration


class Game:
    """Classe principal: inicializa o Pygame, controla estados e o loop."""

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.font.init()
        pygame.mouse.set_visible(False)

        self.screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        pygame.display.set_caption(settings.GAME_TITLE)
        self.clock = pygame.time.Clock()

        self.assets = AssetBank()
        self.music = MusicManager()
        self.particles = ParticleSystem()
        self.floating_texts = FloatingTexts()

        self.camera = Camera((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT),
                             pygame.Rect(0, 0, settings.WORLD_WIDTH, settings.WORLD_HEIGHT))
        self.world = World(self.assets, self.particles, self.floating_texts)
        self.player = Player(self.assets)
        self.hud = HUD(self.assets)

        self.state = "title"
        self.now = 0.0                     # tempo de jogo em segundos
        self.mouse_pos = (settings.WINDOW_WIDTH / 2, settings.WINDOW_HEIGHT / 2)
        self.autofire = False              # botão esquerdo do mouse segurado
        self.upgrade_choices = []
        self.upgrade_rects = []
        self._last_level = 1
        self.selected_alien = None   # alien escolhido no Omnitrix (próxima transformação)
        self.mode = "arena"          # modo selecionado no título (1/2/3)
        self.scores = self._load_scores()
        self.new_record = False
        self.announcements: list[dict] = []   # banners arcade (power-ups/fusões)
        self.smoke_test = False
        self.running = True

        # estrelas do fundo (parallax)
        self.stars = [{
            "pos": Vector2(random.uniform(0, settings.WORLD_WIDTH),
                           random.uniform(0, settings.WORLD_HEIGHT)),
            "depth": random.uniform(0.1, 0.8),
        } for _ in range(400)]

    # ==================================================================
    # Inicialização / reset
    # ==================================================================
    def reset_game(self) -> None:
        """Reinicia uma partida do zero."""
        self.player.reset()
        self.world.reset()
        self.now = 0.0
        self._last_level = 1
        self.selected_alien = None
        self.announcements.clear()
        self.new_record = False
        self.state = "playing"

    # ------------------------------------------------------------------
    # Recordes da Arena (salvos em scores.json)
    # ------------------------------------------------------------------
    def _load_scores(self) -> list[dict]:
        try:
            with open(settings.SCORES_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return [r for r in data if isinstance(r, dict)]
        except (OSError, ValueError):
            return []

    def _save_score(self) -> None:
        """Registra a partida atual nas melhores marcas (top MAX_SCORES)."""
        record = {"time": round(self.world.elapsed, 1), "kills": self.world.kills}
        self.scores.append(record)
        self.scores.sort(key=lambda r: r["time"], reverse=True)
        self.scores = self.scores[:settings.MAX_SCORES]
        try:
            with open(settings.SCORES_FILE, "w", encoding="utf-8") as file:
                json.dump(self.scores, file, ensure_ascii=False, indent=2)
        except OSError:
            pass
        self.new_record = (self.scores and record["time"] >= self.scores[0]["time"]
                           and record["time"] > 0)

    # ==================================================================
    # Loop principal
    # ==================================================================
    def run(self, smoke_test: bool = False) -> None:
        """Loop infinito do jogo. Com smoke_test, roda alguns frames e sai."""
        self.smoke_test = smoke_test
        frame = 0
        max_frames = 900 if smoke_test else 10 ** 9
        while self.running and frame < max_frames:
            dt = self.clock.tick(settings.FPS) / 1000.0
            self.now += dt

            if smoke_test:
                self._smoke_drive(frame)

            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()
            frame += 1

        if smoke_test:
            print("SMOKE OK — jogo inicializou e rodou sem erros.")
        pygame.quit()
        sys.exit(0)

    # ==================================================================
    # Eventos
    # ==================================================================
    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pos = event.pos
                if event.button == 1:
                    self.autofire = True
                elif event.button in (4, 5):
                    # roda do mouse: escolhe o alien no Omnitrix
                    self._cycle_alien(1 if event.button == 5 else -1)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.autofire = False
                    self.player.smash_charge = 0.0   # soltou: carga da pancada zera

            elif event.type == pygame.KEYDOWN:
                self._on_key(event.key)

        # mouse ainda segurado mesmo se a janela perdeu o foco e voltou
        # (no smoke test o driver dummy sempre reporta o botão solto)
        if not self.smoke_test:
            self.autofire = self.autofire and pygame.mouse.get_pressed()[0]

    def _on_key(self, key: int) -> None:
        if self.state == "title":
            if key in (pygame.K_1, pygame.K_2, pygame.K_3):
                self._select_mode(key - pygame.K_1)
            elif key == pygame.K_RETURN:
                if self.mode == "arena":
                    self.reset_game()
                else:
                    self._announce("EM BREVE — ESCOLHA A ARENA (1)", "common")

        elif self.state == "game_over":
            if key == pygame.K_r:
                self.reset_game()

        elif self.state == "level_up":
            self._pick_upgrade(key - pygame.K_1)

        elif self.state == "paused":
            if key == pygame.K_ESCAPE:
                self.state = "playing"

        elif self.state == "playing":
            if key == pygame.K_ESCAPE:
                self.state = "paused"
            elif key == pygame.K_h:
                # alterna a seleção por hover (acessibilidade) com feedback claro
                settings.HOVER_TRANSFORM_ENABLED = not settings.HOVER_TRANSFORM_ENABLED
                status = "LIGADA" if settings.HOVER_TRANSFORM_ENABLED else "DESLIGADA"
                self._announce(f"Seleção por hover {status}", "common")
            elif key == pygame.K_LSHIFT or key == pygame.K_RSHIFT:
                self._try_dash()
            elif key == pygame.K_x:
                self.world.cast_special(self.player, self.now)
            elif key == pygame.K_f:
                self._try_fusion()
            elif key == pygame.K_COMMA:
                self._cycle_alien(-1)
            elif key == pygame.K_PERIOD:
                self._cycle_alien(1)
            elif key == pygame.K_RETURN:
                self._transform_to_selected()

    def _select_mode(self, index: int) -> None:
        """Troca o modo de jogo no título (1 Arena, 2 Campanha, 3 Duelo)."""
        if 0 <= index < len(settings.GAME_MODES):
            self.mode = settings.GAME_MODES[index][0]
            self.assets.play("select_alien")

    def _announce(self, text: str, rarity: str = "common") -> None:
        # tempo de leitura escala com o tamanho do texto (nomes longos ficam mais)
        duration = _banner_duration(text)
        self.announcements.append({"text": text.upper(), "rarity": rarity,
                                   "timer": duration, "max_timer": duration})

    def _try_fusion(self) -> None:
        """Ativa uma fusão do Omnitrix com a barra Prisma cheia (tecla F).

        O parceiro foi sorteado quando a barra encheu (mostrado no HUD). A
        fusão empresta o traço do parceiro ao alien atual — sem trocar de
        corpo. Consigo mesmo = traço amplificado.
        """
        player = self.player
        if player.fusion:
            return
        if player.prism < settings.PRISM_MAX:
            self._announce("Prisma ainda não está cheia", "common")
            return
        if not player.fusion_partner:
            self._announce("Fusão se preparando...", "common")
            return
        partner = player.fusion_partner
        player.start_fusion(partner)
        trait = settings.FUSION_TRAITS[partner]
        self._announce(f"FUSÃO: {player.alien_name} + {partner} ({trait['label']})!",
                       "legendary")
        self.assets.play("transform")
        self.particles.burst(player.pos, 26, trait["color"], 240, 0.5, 5)
        self.camera.shake(self.now, 8, 0.35)
        self.world.effects.append({
            "kind": "ring", "center": Vector2(player.pos), "radius": 140,
            "color": trait["color"], "lifetime": 0.4, "max_lifetime": 0.4,
        })

    def _pick_upgrade(self, index: int) -> None:
        if 0 <= index < len(self.upgrade_choices):
            self.upgrade_choices[index]["apply"](self.player, self.world)
            self.state = "playing"

    def _cycle_alien(self, direction: int) -> None:
        """Circula a seleção pelos 5 aliens (não só os vizinhos da forma atual).

        Antes girava SEMPRE a partir da forma atual — de Ben só dava pra
        alcançar Quatro Braços (roda pra cima) ou Diamante (roda pra baixo).
        Agora gira a partir da seleção atual, então TODOS os 5 são acessíveis.
        """
        base = self.selected_alien if self.selected_alien else self.player.alien_name
        index = settings.ALIEN_ORDER.index(base)
        self.selected_alien = settings.ALIEN_ORDER[(index + direction) % len(settings.ALIEN_ORDER)]
        self.assets.play("select_alien")

    def _transform_to_selected(self) -> None:
        """Transforma no alien escolhido no Omnitrix (tecla ENTER).

        Sem nada escolhido, o ENTER avança para o próximo alien — a troca
        nunca trava. Após transformar, a seleção é limpa (o HUD volta a
        ensinar o comando). Feedback claro quando falta energia.
        """
        player = self.player
        target = self.selected_alien
        if not target or target == player.alien_name:
            index = settings.ALIEN_ORDER.index(player.alien_name)
            target = settings.ALIEN_ORDER[(index + 1) % len(settings.ALIEN_ORDER)]
        if not self._apply_transform(target):
            self._announce(
                f"Energia insuficiente para {target} (precisa de {settings.ENERGY_COST_TO_TRANSFORM}%)",
                "common")
            return
        self.selected_alien = None   # limpa a seleção: o HUD volta a ensinar

    def _apply_transform(self, target: str) -> bool:
        """Transforma diretamente num alien (com efeitos do Omnitrix).

        Usado pelo ENTER e pelo hover de 3s. Retorna True se transformou;
        se faltar energia, anuncia o motivo (hover também recebe o feedback).
        """
        player = self.player
        if not player.change_form(target, self.now):
            self._announce(
                f"Energia insuficiente para {target} (precisa de {settings.ENERGY_COST_TO_TRANSFORM}%)",
                "common")
            return False
        self.assets.play("transform")
        # onda de choque do Omnitrix
        self.world.effects.append({
            "kind": "ring", "center": Vector2(player.pos), "radius": 120,
            "color": settings.COLORS["omnitrix_green"], "lifetime": 0.4, "max_lifetime": 0.4,
        })
        self.particles.burst(player.pos, 20, settings.COLORS["omnitrix_green"], 200, 0.4, 4)
        return True

    def _try_dash(self) -> None:
        # dash na direção do MOVIMENTO (WASD/setas); parado, cai para a mira
        move_dir = self._read_movement_input()
        if self.player.start_dash(self.now, move_dir):
            self.assets.play("dash")
            self.particles.burst(self.player.pos, 16, settings.COLORS["xlr8_blue"], 200, 0.3, 4)
            self.camera.shake(self.now, 4, 0.12)

    # ==================================================================
    # Atualização
    # ==================================================================
    def _update(self, dt: float) -> None:
        # banners arcade envelhecem em qualquer estado
        for announcement in self.announcements[:]:
            announcement["timer"] -= dt
            if announcement["timer"] <= 0:
                self.announcements.remove(announcement)

        if self.state in ("level_up", "game_over"):
            # o mundo fica congelado, mas partículas/textos continuam
            self.particles.update(dt)
            self.floating_texts.update(dt)
            return
        if self.state == "paused":
            return

        # mira: converte o mouse da tela para o mundo (compensa a inclinação)
        mouse_world = self.camera.screen_to_world(self.mouse_pos)
        self.player.aim_towards(mouse_world)
        self.camera.update(dt, self.now, self.player.pos, self.mouse_pos)

        if self.state == "playing":
            self._update_playing(dt)
        elif self.state == "title":
            self.particles.update(dt)

    def _update_playing(self, dt: float) -> None:
        # movimento
        input_vec = self._read_movement_input()
        self.player.update(dt, input_vec)
        self.player.update_energy(dt)

        # eventos do jogador (ex.: pouso do Super Pulmão, escudo, fim de fusão)
        for event in self.player.events:
            if event == "jump_landed":
                self.world.handle_jump_landing(self.player, self.now)
            elif event == "boost_ended":
                self.world.handle_boost_end(self.player, self.now)
            elif event == "shield_blocked":
                self.floating_texts.add("BLOQUEADO!", self.player.pos, settings.COLORS["diamond_cyan"])
            elif event == "fusion_ended":
                self._announce("Fusão terminou", "common")
        self.player.events.clear()

        # mundo (horda, projéteis, colisões, drops)
        self.world.update(dt, self.now, self.player, self.camera)

        # aplica os tremores de tela pedidos pelo mundo (explosões, golpes...)
        for intensity, duration in self.world.drain_shakes():
            self.camera.shake(self.now, intensity, duration)

        # banners arcade vindos do mundo (power-ups coletados)
        self.announcements.extend(self.world.drain_announcements())

        # hover no Omnitrix: 3s parado sobre um retrato transforma nele
        # (acessibilidade — desligável com H). O HUD devolve o alien pendente.
        self.hud.update_hover(dt, self.mouse_pos, self.player)
        pending = self.hud.consume_hover_transform()
        if pending:
            self._apply_transform(pending)

        # usa o poder do alien atual enquanto segura o botão do mouse
        if self.autofire:
            # Pancada carregada do Quatro Braços: segurar acumula carga (o
            # World lê player.smash_charge e zera a cada pancada usada). Só
            # acumula para o Quatro Braços — outros aliens ignoram a carga.
            is_smash = (self.player.alien_name == "Quatro Braços"
                        and "minigun" not in self.player.powerups
                        and "punhos_4x" not in self.player.powerups)
            if is_smash:
                self.player.smash_charge = min(settings.SMASH_CHARGE_TIME,
                                               self.player.smash_charge + dt)
            if self.player.primary_ready():
                self.world.attack(self.player, self.now)

        # partículas e textos
        self.particles.update(dt)
        self.floating_texts.update(dt)

        # música ambiente
        if self.world.kills >= 50:
            self.music.play("phase2")
        elif self.world.enemies:
            self.music.play("combat")
        else:
            self.music.play("suspense")

        # level up? (XP suficiente)
        if self.player.level > getattr(self, "_last_level", 1):
            self._last_level = self.player.level
            self._start_level_up()

        # morte: salva recorde e vai para o game over (não no smoke test)
        if self.player.health <= 0:
            self.state = "game_over"
            if not self.smoke_test:
                self._save_score()
            self.music.fadeout(2000)

    def _read_movement_input(self) -> Vector2:
        keys = pygame.key.get_pressed()
        vector = Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vector.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vector.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vector.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vector.y += 1
        return vector

    def _start_level_up(self) -> None:
        self.state = "level_up"
        self.upgrade_choices = random.sample(settings.UPGRADE_OPTIONS, 3)
        self.upgrade_rects = self._build_upgrade_rects()
        self.assets.play("level_up")
        self.floating_texts.add("LEVEL UP!", self.player.pos, settings.COLORS["gold"])

    def _build_upgrade_rects(self):
        rects = []
        for index in range(3):
            rect = pygame.Rect(settings.WINDOW_WIDTH / 2 - 220,
                               250 + index * 110, 440, 80)
            rects.append(rect)
        return rects

    # ==================================================================
    # Desenho
    # ==================================================================
    def _draw(self) -> None:
        if self.state == "title":
            self.hud.draw_title(self.screen, self.assets, self.mode, self.scores)
            self.hud.draw_announcements(self.screen, self.announcements)
            self.hud.draw_crosshair(self.screen, self.mouse_pos,
                                    settings.COLORS["omnitrix_green"])
            return

        # --- camada do mundo (a câmera inclina) ---
        world_surf = self.camera.surf
        world_offset = self.camera.world_offset(self.now)
        self.camera.record_drawn_offset(world_offset)  # mantém a mira precisa no shake
        self._draw_background(world_surf, world_offset)
        self.world.draw(world_surf, world_offset, self.now)
        # círculo sutil mostrando o alcance do poder do alien atual
        attack = settings.ALIEN_DATA[self.player.alien_name]["attack_z"]
        if attack is not None and "range" in attack:
            pygame.draw.circle(world_surf, (*attack["color"], 26),
                               self.player.pos - world_offset, attack["range"], width=2)
        self.player.draw(world_surf, world_offset, self.now)
        self.particles.draw(world_surf, world_offset)
        self.floating_texts.draw(world_surf, world_offset)
        self.camera.present(self.screen, self.now, self.player.pos)

        # --- HUD (não inclina) ---
        # TAB segurado: painel de atributos detalhado (dano/velocidade/energia/fusão)
        keys = pygame.key.get_pressed()
        show_stats = bool(keys[pygame.K_TAB])
        self.hud.draw_hud(self.screen, self.player, self.world.kills, self.world.elapsed,
                          next_alien=self.selected_alien,
                          mouse_pos=self.mouse_pos, show_stats=show_stats)
        cross_color = attack["color"] if attack else settings.COLORS["omnitrix_green"]
        self.hud.draw_crosshair(self.screen, self.mouse_pos, cross_color)
        self.hud.draw_announcements(self.screen, self.announcements)

        if self.state == "level_up":
            self.hud.draw_level_up(self.screen, self.upgrade_choices, self.upgrade_rects)
        elif self.state == "paused":
            self.hud.draw_pause(self.screen)
        elif self.state == "game_over":
            self.hud.draw_game_over(self.screen, self.world.kills,
                                    self.world.elapsed, self.player.level,
                                    scores=self.scores, new_record=self.new_record)

    def _draw_background(self, surface, world_offset) -> None:
        """Gradiente roxo + estrelas com parallax de profundidade."""
        for y in range(0, surface.get_height(), 20):
            ratio = y / surface.get_height()
            color = _lerp_color(settings.COLORS["bg_top"], settings.COLORS["bg_bottom"], ratio)
            pygame.draw.rect(surface, color, (0, y, surface.get_width(), 20))

        camera_center = self.camera.position
        for star in self.stars:
            depth = star["depth"]
            # parallax: estrelas distantes "andam" menos com a câmera
            parallax = camera_center * depth
            pos = Vector2(star["pos"]) - world_offset - camera_center * (1 - depth) + parallax
            if 0 <= pos.x <= surface.get_width() and 0 <= pos.y <= surface.get_height():
                value = int(255 * depth)
                pygame.draw.circle(surface, (value, value, value), pos, max(1, int(depth * 2)))

    # ==================================================================
    # Modo de teste (smoke test)
    # ==================================================================
    def _smoke_drive(self, frame: int) -> None:
        """Exercita as principais mecânicas para validar o jogo sem tela."""
        self.mouse_pos = (100 + (frame * 37) % 800, 100 + (frame * 53) % 500)
        if frame == 5:
            self.reset_game()
        if self.state == "playing":
            # ataca com o clique segurado, alternando liga/desliga
            if frame % 40 < 20:
                self.autofire = True
            else:
                self.autofire = False
            if frame % 30 == 0:
                self.world.spawn_enemy_near_camera(self.camera)
            if frame % 50 == 25:
                self._try_dash()
            # percorre todos os aliens para testar poderes e especiais
            if frame == 70:
                self.player.change_form("XLR8", self.now)            # cadeia + turbo
            if frame == 100:
                self.player.change_form("Chama", self.now)           # bola de fogo
            if frame == 135:
                self.player.change_form("Diamante", self.now)        # estilhaço
            if frame == 200:
                self.player.change_form("Quatro Braços", self.now)   # pancada
            if frame in (90, 120, 150, 210):
                self.world.cast_special(self.player, self.now)
            # --- Fase 2: power-ups, fusões e combos ---
            if frame == 60:
                self.world._apply_powerup(self.player, "minigun", self.now)
            if frame == 64:
                self.world._apply_powerup(self.player, "traje_venom", self.now)
            if frame == 68:
                self.world._apply_powerup(self.player, "punhos_4x", self.now)
            if frame == 72:
                self.world._apply_powerup(self.player, "nucleo_chama", self.now)
            if frame == 76:
                self.world._apply_powerup(self.player, "congelamento", self.now)
            if frame == 80:
                self.world._apply_powerup(self.player, "sombra_kevin", self.now)
            if frame == 84:
                self.world._apply_powerup(self.player, "waybig_furia", self.now)
            if frame == 88:
                self.world._apply_powerup(self.player, "sorte_omnitrix", self.now)
            if frame == 95:
                # fusão por traços: enche o Prisma (sorteia parceiro) e ativa
                self.player.add_prism(settings.PRISM_MAX)
                self._try_fusion()
            if frame == 105:
                # encerra a fusão anterior para poder fundir de novo
                self.player.fusion = None
                self.player.fusion_timer = 0.0
                self.player.add_prism(settings.PRISM_MAX)
                self._try_fusion()
            if frame == 110:
                # troca rápida (Troca Relâmpago) + combo (Golpe Triplo)
                self.player.last_form_change = self.now
                self.player.combo_count = 3
                self.player.combo_timer = settings.COMBO_WINDOW
                self.player.combo_bonus_ready = True
            if frame == 115:
                self.world.drop_powerup(self.player.pos)
            if frame == 118:
                # Bug 1: ENTER sem seleção avança para o próximo alien
                self.selected_alien = None
                self.player.energy = settings.ENERGY_MAX
                before = self.player.alien_name
                self._transform_to_selected()
                assert self.player.alien_name != before, "ENTER não trocou de alien"
            if frame == 120:
                # ciclo da seleção alcança TODOS os 5 aliens (bug antigo)
                self.selected_alien = None
                self._cycle_alien(1)
                self._cycle_alien(1)
                self._cycle_alien(1)
                self._cycle_alien(1)
                self._cycle_alien(1)
                assert self.selected_alien == self.player.alien_name, \
                    "5 cliques de roda deveriam voltar ao alien atual"
            if frame == 122:
                # Bug 2: baú perto do jogador leva dano do soco (síncrono)
                self.player.powerups.clear()   # nada de minigun/punhos no teste
                self.player.alien_name = "Ben"  # soco em arco acerta na hora
                self.player.update_alien_stats()
                self.player.primary_cd = 0.0
                self.player.aim_dir = Vector2(1, 0)  # mira no baú à direita
                self.world.chests.clear()
                self.world.chests.append(Chest(self.player.pos + Vector2(60, 0)))
                hp_before = self.world.chests[0].health
                self.world.attack(self.player, self.now)
                assert self.world.chests[0].health < hp_before, "baú não recebeu dano"
            if frame == 125:
                # dash usa a direção do MOVIMENTO (não a mira)
                self.player.state = "normal"
                self.player._dash_ready_at = 0.0
                self.player.aim_dir = Vector2(1, 0)
                started = self.player.start_dash(self.now, Vector2(0, -1))
                assert started, "dash não iniciou"
                assert self.player.dash_dir == Vector2(0, -1), \
                    "dash deveria usar a direção do movimento"
                # parado: cai para a mira (fallback natural)
                self.player.state = "normal"
                self.player._dash_ready_at = 0.0
                self.player.start_dash(self.now, Vector2(0, 0))
                assert self.player.dash_dir == Vector2(1, 0), \
                    "dash parado deveria usar a mira como fallback"
            if frame == 128:
                # fusão nunca sorteia o próprio alien (20 combinações)
                self.player.fusion = None
                self.player.fusion_partner = None
                self.player.prism = 0.0
                self.player.add_prism(settings.PRISM_MAX)
                assert self.player.fusion_partner != self.player.alien_name, \
                    "parceiro de fusão não pode ser o próprio alien"
            if frame == 130:
                # Grito do Omnitrix (especial do Ben) + parry existem
                self.player.alien_name = "Ben"
                self.player.update_alien_stats()
                self.player.special_cd = 0.0
                self.player.state = "normal"
                used = self.world.cast_special(self.player, self.now)
                assert used, "Grito do Omnitrix não foi usado"
                assert self.player.energy_boost_timer > 0, \
                    "Grito do Omnitrix não ativou o boost de recarga"
            if frame == 133:
                # fusão recarrega 100% da energia (regra revisada)
                self.player.energy = 10.0
                self.player.fusion = None
                self.player.fusion_partner = "XLR8"
                self.player.prism = settings.PRISM_MAX
                self.player.start_fusion("XLR8")
                assert self.player.energy == settings.ENERGY_MAX, \
                    "fusão deveria recarregar 100% de energia"
                # limpa para não vazar pro restante do teste
                self.player.fusion = None
                self.player.fusion_timer = 0.0
                self.player.fusion_partner = None
                self.player.prism = 0.0
            if frame == 160:
                # força level-up e game over para testar as telas
                self.player.level = 2
                self._start_level_up()
            if frame == 212:
                # TODAS as 20 fusões: cada base x cada parceiro (sem repetição)
                # com o especial combinado correspondente — cobertura determinística
                self.player.powerups.clear()
                self.player.fusion_timer = settings.FUSION_DURATION
                combos = 0
                for base in settings.ALIEN_ORDER:
                    for partner in settings.ALIEN_ORDER:
                        if partner == base:
                            continue
                        cfg = settings.FUSION_SPECIALS.get((base, partner))
                        assert cfg is not None, f"FUSION_SPECIALS sem {base}+{partner}"
                        self.player.alien_name = base
                        self.player.update_alien_stats()
                        self.player.fusion = partner
                        self.player.special_cd = 0.0
                        self.player.state = "normal"
                        used = self.world.cast_special(self.player, self.now)
                        assert used, f"especial de fusão {base}+{partner} não usado"
                        combos += 1
                assert combos == 20, f"esperava 20 combos, achei {combos}"
                # restaura o estado para o restante do teste (sem vazamento de
                # estado de pulo/investida das 20 fusões exercitadas acima)
                self.player.fusion = None
                self.player.fusion_timer = 0.0
                self.player.fusion_jump_cfg = None
                self.player.jump_barrage_stage = 0
                self.player.double_jump_ready = False
                self.player.gauntlets_timer = 0.0
                self.player.rush_hit_ids = set()
                self.player.invincible_until = 0.0   # turbos deixam invencibilidade alta
                self.player.state = "normal"
                self.player.special_cd = 0.0
            if frame == 220:
                # limpa a invencibilidade para conseguir morrer
                self.state = "playing"
                self.player.invincible_until = 0.0
                self.player.take_damage(999, self.now)
            if frame == 260:
                # reinicia a partida para testar o caminho completo
                self.reset_game()


def _lerp_color(color_a, color_b, ratio):
    return tuple(int(a + (b - a) * ratio) for a, b in zip(color_a, color_b))
