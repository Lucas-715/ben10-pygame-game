"""
assets.py — Carregamento de imagens e sons.

Tudo é carregado de forma tolerante a falhas: se um arquivo não existir,
usamos um placeholder silencioso para o jogo nunca quebrar por causa de assets.
"""
import pygame

from . import settings


class DummySound:
    """Substituto silencioso usado quando um arquivo de som não existe."""

    def play(self, *args, **kwargs):
        pass

    def set_volume(self, volume):
        pass

    def fadeout(self, ms):
        pass


class AssetBank:
    """Banco central de imagens e efeitos sonoros do jogo."""

    def __init__(self):
        self.images: dict[str, pygame.Surface] = {}
        self.sounds: dict[str, object] = {}
        self._load_images()
        self._load_sounds()

    # ------------------------------------------------------------------
    # Imagens
    # ------------------------------------------------------------------
    def _load_images(self) -> None:
        self.images["player"] = {}
        for alien_name, file_name in settings.PLAYER_IMAGES.items():
            image = self._load_image(settings.IMAGES_DIR / "player" / file_name)
            if image is None:
                image = self._solid_square(settings.PLAYER_SIZE,
                                           settings.ALIEN_DATA[alien_name]["color"])
            self.images["player"][alien_name] = pygame.transform.scale(
                image, (settings.PLAYER_SIZE, settings.PLAYER_SIZE))

        self.images["enemy"] = {}
        for enemy_type, data in settings.ENEMY_DATA.items():
            image = self._load_image(settings.IMAGES_DIR / "enemies" / data["image"])
            if image is None:
                image = self._solid_square(data["size"][0], settings.COLORS["purple"])
            self.images["enemy"][enemy_type] = pygame.transform.scale(image, data["size"])

        self.images["ui"] = {
            "chest": self._load_image(settings.IMAGES_DIR / "objects" / "bau_magico.png"),
            "heart": self._load_image(settings.IMAGES_DIR / "ui" / "vida.png"),
            "shield": self._load_image(settings.IMAGES_DIR / "ui" / "escudo.png"),
            "diamond": self._load_image(settings.IMAGES_DIR / "ui" / "ataque_diamante.png"),
        }

        self.images["items"] = self._load_items()
        self.images["effects"] = self._load_effects()

    # ------------------------------------------------------------------
    # Itens de power-up (pixel arts: coxinha, poção, arruela, castelo...)
    # ------------------------------------------------------------------
    def _load_items(self) -> dict[str, pygame.Surface | None]:
        """Carrega as pixel arts de itens (assets/images/items).

        Tudo é tolerante a falhas: se faltar um arquivo, a chave fica None e
        o jogo usa o placeholder circular de sempre (nunca quebra).
        """
        items_dir = settings.IMAGES_DIR / "items"
        items: dict[str, pygame.Surface | None] = {}
        for key, file_name in settings.ITEM_IMAGES.items():
            image = self._load_image(items_dir / file_name)
            if image is None:
                items[key] = None
                continue
            target = settings.ITEM_SIZES.get(key)
            items[key] = pygame.transform.smoothscale(image, target) if target else image
        return items

    def get_item(self, key: str):
        """Retorna uma pixel art de item (ou None se faltar o asset)."""
        return self.images["items"].get(key)

    def resolve_icon(self, icon_key: str | None):
        """Resolve um campo 'icon' de power-up ("ui:xxx" / "item:xxx" / efeito).

        Centralizado aqui para que o HUD (ui.py) e o núcleo no chão (world.py)
        mostrem exatamente o mesmo sprite de cada power-up.
        """
        if not icon_key:
            return None
        if icon_key.startswith("ui:"):
            return self.get_ui(icon_key[3:])
        if icon_key.startswith("item:"):
            return self.get_item(icon_key[5:])
        return self.get_effects(icon_key)

    # ------------------------------------------------------------------
    # Efeitos visuais (pixel arts CC0/CC-BY — ver assets/images/effects/README.md)
    # ------------------------------------------------------------------
    def _load_effects(self) -> dict[str, object]:
        """Carrega os sprites de efeitos dos poderes (Bola de Fogo, explosões...).

        Tudo é tolerante a falhas: se um arquivo não existir, a chave fica vazia
        e o jogo desenha o placeholder circular de sempre (nunca quebra).
        """
        effects_dir = settings.IMAGES_DIR / "effects"

        def sheet_frames(relative_path, cols, rows, target=None):
            """Fatia uma sprite sheet em (cols x rows) quadros; opcionalmente redimensiona."""
            image = self._load_image(effects_dir / relative_path)
            if image is None:
                return []
            frame_w = image.get_width() // cols
            frame_h = image.get_height() // rows
            frames = []
            for row in range(rows):
                for col in range(cols):
                    frame = image.subsurface((col * frame_w, row * frame_h,
                                              frame_w, frame_h)).copy()
                    if target is not None:
                        frame = pygame.transform.scale(frame, target)
                    frames.append(frame)
            return frames

        def scaled(relative_path, target):
            image = self._load_image(effects_dir / relative_path)
            if image is None:
                return None
            return pygame.transform.scale(image, target)

        effects = {
            # Bola de Fogo da Chama: 3 quadros (32x16) — animação no voo
            "fireball_frames": sheet_frames("fire/Fireball.png", 3, 1, (36, 18)),
            # Explosão (Supernova, bolas de fogo, bombas): sheet 8x3 de 128x128
            "explosion_frames": sheet_frames("explosion/explosionframes.png", 8, 3),
            # Estilhaço de Diamante: cristal gelo pequeno girando
            "crystal_shard": scaled("crystal/crystal-icy.png", (16, 13)),
            # Cristal orbitando no Campo de Cristais
            "crystal_orb": scaled("crystal/crystal-icy.png", (20, 16)),
            # Raio da Cadeia do XLR8 (esticado entre os alvos)
            "lightning_bolt": scaled("lightning/Lightning_Yellow.png", (240, 60)),
            # Minigun do Sumo Sacerdote: 6 quadros (16x16) de orbe mágico
            "minigun_frames": sheet_frames("orbs/Magic Orb.png", 6, 1, (16, 16)),
        }
        # Mini-ícones do HUD: reutiliza o 1º quadro já carregado (sem reler o arquivo)
        def icon(frames_key):
            frames = effects.get(frames_key) or []
            frame = frames[0] if frames else None
            return pygame.transform.scale(frame, (18, 18)) if frame is not None else None

        effects["orb_icon"] = icon("minigun_frames")
        effects["fireball_icon"] = icon("fireball_frames")
        effects["explosion_icon"] = icon("explosion_frames")
        return effects

    @staticmethod
    def _load_image(path) -> pygame.Surface | None:
        """Carrega uma imagem ou retorna None (com aviso) se falhar."""
        try:
            return pygame.image.load(path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            print(f"[Aviso] Imagem não encontrada: '{path}'")
            return None

    @staticmethod
    def _solid_square(size: int, color) -> pygame.Surface:
        surface = pygame.Surface((size, size))
        surface.fill(color)
        return surface

    def get_player_image(self, alien_name: str) -> pygame.Surface:
        return self.images["player"][alien_name]

    def get_enemy_image(self, enemy_type: str) -> pygame.Surface:
        return self.images["enemy"][enemy_type]

    def get_ui(self, key: str):
        return self.images["ui"].get(key)

    def get_effects(self, key: str):
        """Retorna um sprite/frames de efeito (ou None/[] se o asset faltar)."""
        return self.images["effects"].get(key)

    # ------------------------------------------------------------------
    # Sons
    # ------------------------------------------------------------------
    def _load_sounds(self) -> None:
        # mapeamento: nome lógico -> arquivo em assets/sounds/sfx
        sound_files = {
            "transform": "omnitrix-transform.mp3",
            "select_alien": "escolhendo-alien.mp3",
            "melee": "attack_hit.mp3",
            "smash": "force_impact.ogg",
            "jump_land": "force_impact2.ogg",
            "fireball": "fire-attack.ogg",
            "nova": "fiery_explosion.ogg",
            "crystal": "atack_dimond.ogg",
            "crystal_field": "dimond_shield.ogg",
            "boost": "super_velocidade.ogg",
            "hit": "attack_hit.mp3",
            "dash": "electric_spark.ogg",  # pode não existir -> DummySound
            "level_up": "level-up.ogg",    # pode não existir -> DummySound
        }
        for name, file_name in sound_files.items():
            path = settings.SFX_DIR / file_name
            try:
                self.sounds[name] = pygame.mixer.Sound(str(path))
            except (pygame.error, FileNotFoundError):
                print(f"[Aviso] Som não encontrado: '{path}' (usando som silencioso)")
                self.sounds[name] = DummySound()

    def play(self, name: str) -> None:
        self.sounds.get(name, DummySound()).play()
