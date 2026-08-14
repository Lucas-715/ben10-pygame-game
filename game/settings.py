"""
settings.py — Toda a configuração do jogo em um só lugar.

Tela, cores, balanceamento do jogador, inimigos, armas e aliens ficam aqui
para facilitar o ajuste fino sem precisar mexer na lógica do jogo.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Janela e ritmo do jogo
# ---------------------------------------------------------------------------
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60
GAME_TITLE = "Ben 10 - A Ameaça Eterna 2D"

# ---------------------------------------------------------------------------
# Mundo
# ---------------------------------------------------------------------------
WORLD_WIDTH = 3000
WORLD_HEIGHT = 2000

# ---------------------------------------------------------------------------
# Caminhos dos arquivos
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
MUSIC_DIR = ASSETS_DIR / "sounds" / "music"
SFX_DIR = ASSETS_DIR / "sounds" / "sfx"

# ---------------------------------------------------------------------------
# Paleta de cores (usada por toda a interface e efeitos)
# ---------------------------------------------------------------------------
COLORS = {
    "white":       (255, 255, 255),
    "black":       (0, 0, 0),
    "gray":        (128, 128, 128),
    "yellow":      (255, 255, 0),
    "gold":        (241, 196, 15),
    "purple":      (155, 89, 182),
    "health_green": (46, 204, 113),
    "health_red":  (192, 57, 43),
    "health_dark": (44, 62, 80),
    "xp_blue":     (52, 152, 219),
    "omnitrix_green": (0, 255, 120),
    "bg_top":      (25, 15, 35),
    "bg_bottom":   (45, 25, 65),
    "damage_red":  (217, 30, 24),
    # Cores dos aliens (para os placeholders, se faltar imagem)
    "ben_green":   (0, 255, 0),
    "four_red":    (217, 30, 24),
    "xlr8_blue":   (30, 139, 195),
    "fire_orange": (244, 120, 37),
    "diamond_cyan":(27, 188, 155),
}

# ---------------------------------------------------------------------------
# Jogador
# ---------------------------------------------------------------------------
PLAYER_SIZE = 50  # quadrado (as imagens são redimensionadas para 50x50)
PLAYER_BASE_SPEED = 230.0          # px/s
PLAYER_ACCELERATION = 1600.0       # px/s²  (aceleração suave ao pressionar tecla)
PLAYER_FRICTION = 9.0              # quanto maior, mais rápido o jogador para
PLAYER_BASE_MAX_HEALTH = 10
INVULNERABILITY_DURATION = 0.8     # segundos de "invencível" após levar dano

# --- Dash (esquiva) ---
DASH_SPEED = 780.0
DASH_DURATION = 0.13
DASH_COOLDOWN = 1.1
DASH_INVULNERABILITY = 0.28

# --- Seleção de alien por permanência (hover de 3s no Omnitrix) ---
# Atalho de acessibilidade: parar o mouse 3s sobre o retrato transforma nele
# (anel de progresso no retrato). Desligável (H no jogo) para quem prefere só
# o fluxo clássico roda/,. + ENTER.
HOVER_TRANSFORM_ENABLED = True
HOVER_TRANSFORM_TIME = 3.0        # segundos de hover para transformar
HOVER_ZONE_RADIUS = 20            # zona de detecção centrada em cada retrato

# --- Piso visual dos efeitos (não "piscar" rápido demais) ---
# Efeitos visuais ficam no mínimo ~150ms na tela, independente da duração de
# dano: o olho humano precisa registrar a imagem antes de ela sumir.
MIN_EFFECT_DISPLAY = 0.15
MIN_SPRITE_FRAME_TIME = 0.04      # mínimo por quadro de sprite sheet (~25 fps)
POWERUP_ICON_ENTRY = 0.15         # animação de entrada dos ícones no HUD

# --- Grito do Omnitrix (especial do Ben, fora de fusão) ---
OMNITRIX_ROAR_RADIUS = 220
OMNITRIX_ROAR_KNOCKBACK = 340
OMNITRIX_ROAR_ENERGY_BOOST = 2.0  # segundos de recarga de energia acelerada
OMNITRIX_ROAR_ENERGY_MULT = 2.5   # velocidade da recarga durante o boost
OMNITRIX_ROAR_COOLDOWN = 6.0

# --- Parry do Ben (contra-ataque cronometrado) ---
# Acertar o soco quando o inimigo está prestes a te acertar = dano triplo e
# cancela o dano que você receberia (janela curta, estilo "parry").
PARRY_RANGE = 46                  # distância do inimigo para contar como "prestes a acertar"
PARRY_DAMAGE_MULT = 3.0
PARRY_INVULNERABILITY = 0.35

# --- Pancada carregada do Quatro Braços ---
# Segurar o clique carrega a Pancada no Chão: a área cresce até um teto.
SMASH_CHARGE_TIME = 0.7           # segundos para carga total
SMASH_CHARGE_MAX_WIDTH = 1.8      # multiplicador máximo de largura
SMASH_CHARGE_MAX_RANGE = 1.35     # multiplicador máximo de alcance
SMASH_CHARGE_DAMAGE = 1.5         # multiplicador de dano na carga total

# --- Zona de lentidão do pouso (Super Pulmão deixa rachadura no chão) ---
SUPER_JUMP_SLOW_RADIUS = 130
SUPER_JUMP_SLOW_DURATION = 3.0
SUPER_JUMP_SLOW_MULT = 0.55       # inimigos dentro ficam 45% mais lentos

# --- Eco do XLR8 (turbo deixa um clone-fantasma correndo) ---
# Ao atropelar um inimigo no turbo, um eco continua correndo em linha reta
# por ~1s causando dano no caminho (efeito cascata, sem aumentar o turbo real).
TURBO_ECHO_DURATION = 1.0
TURBO_ECHO_SPEED = 520.0
TURBO_ECHO_DAMAGE_MULT = 0.6      # dano do eco em relação ao contato do turbo

# --- Atordoamento da Cadeia do XLR8 ---
# Atingir os MESMOS alvos repetidamente na janela de reforço atordoa (3º acerto).
CHAIN_STUN_HITS = 3
CHAIN_STUN_WINDOW = 4.0           # janela para "reforçar" o mesmo alvo
CHAIN_STUN_DURATION = 0.8

# --- Cratera incandescente da Supernova (Chama) ---
NOVA_CRATER_RADIUS_MULT = 0.75
NOVA_CRATER_DURATION = 2.5
NOVA_CRATER_DAMAGE_MULT = 0.25

# --- Fogueira residual da Bola de Fogo (Chama) ---
# Bola que não acerta ninguém e bate no limite do alcance deixa uma fogueira
# pequena no chão (valor residual para tiros "errados").
FIREBALL_CAMPFIRE_RADIUS = 42
FIREBALL_CAMPFIRE_DURATION = 2.0
FIREBALL_CAMPFIRE_DAMAGE_MULT = 0.4

# --- Muralha de cristais (Diamante) ---
# Os cristais do Campo de Cristais empurram os inimigos (obstáculo físico).
CRYSTAL_PUSH_STRENGTH = 130.0
CRYSTAL_PUSH_RADIUS = 40

# --- Estilhaço em cascata (Diamante) ---
# Estilhaço que perfura o teto de alvos e ainda tem alcance sobra um 2º menor.
SHARD_SPLIT_MIN_FRACTION = 0.35   # fração de alcance restante p/ dividir
SHARD_SPLIT_DAMAGE_MULT = 0.6
SHARD_SPLIT_PIERCE = 2
SHARD_SPLIT_RANGE_MULT = 0.7

# ---------------------------------------------------------------------------
# Sistema de XP e níveis
# ---------------------------------------------------------------------------
XP_BASE = 100
XP_STEP = 50


def xp_needed(level: int) -> int:
    """Quantidade de XP necessária para o próximo nível."""
    return XP_BASE + (level - 1) * XP_STEP


# ---------------------------------------------------------------------------
# Energia do Omnitrix
# ---------------------------------------------------------------------------
ENERGY_MAX = 100
ENERGY_DRAIN_PER_SECOND = 5.0   # gasta enquanto transformado
ENERGY_RECHARGE_PER_SECOND = 10.0
ENERGY_COST_TO_TRANSFORM = 10

# ---------------------------------------------------------------------------
# Observação: não existem "armas genéricas" — cada alien do Omnitrix tem seu
# próprio poder (ataque primário com o clique esquerdo + especial com X),
# todos apontados pelo mouse. Veja ALIEN_DATA logo abaixo.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Inimigos — cada tipo tem imagem própria e condições de desbloqueio
# ---------------------------------------------------------------------------
ENEMY_DATA = {
    "cavaleiro_n1": {
        "name": "Cavaleiro Nv.1",
        "image": "cavaleiro_nivel1.png",
        "size": (45, 45),
        "health": 2, "speed": 1.15, "damage": 1, "xp": 10,
        "unlock_kills": 0, "unlock_time": 0.0, "weight": 10,
    },
    "cavaleiro_n2": {
        "name": "Cavaleiro Nv.2",
        "image": "cavaleiro_nivel2.png",
        "size": (48, 48),
        "health": 4, "speed": 1.25, "damage": 1, "xp": 15,
        "unlock_kills": 20, "unlock_time": 0.0, "weight": 8,
    },
    "cavaleiro_n3": {
        "name": "Cavaleiro Nv.3",
        "image": "cavaleiro_nivel3.png",
        "size": (52, 52),
        "health": 9, "speed": 1.4, "damage": 1, "xp": 25,
        "unlock_kills": 60, "unlock_time": 0.0, "weight": 6,
    },
    "caveira": {
        "name": "Caveira",
        "image": "caveira.png",
        "size": (30, 30),
        "health": 1, "speed": 2.1, "damage": 1, "xp": 5,
        "unlock_kills": 0, "unlock_time": 120.0, "weight": 5,
    },
    "cavaleiro_magma": {
        "name": "Cavaleiro de Magma",
        "image": "cavaleiro_magma.png",
        "size": (55, 55),
        "health": 16, "speed": 0.85, "damage": 2, "xp": 40,
        "unlock_kills": 0, "unlock_time": 240.0, "weight": 3,
    },
}
ENEMY_DAMAGE_COOLDOWN = 0.0  # inimigos morrem ao tocar o jogador (causam dano)
ENEMY_SPAWN_INTERVAL_BASE = 1.8   # segundos entre spawns no início
ENEMY_SPAWN_INTERVAL_MIN = 0.35
ENEMY_SCALE_RATE = 0.008          # crescimento de vida por segundo (não mexe na velocidade)
ENEMY_SCALE_CAP = 2.2
# Velocidade dos inimigos: começa tranquila e acelera AOS POUCOS (Arena Infinita)
ENEMY_SPEED_MULT = 95            # px/s por unidade de "speed" dos dados
ENEMY_SPEED_GRACE = 35.0         # primeiros 35s na velocidade base (suave)
ENEMY_SPEED_RAMP = 0.006         # +0,6% de velocidade por segundo após a graça
ENEMY_SPEED_CAP = 1.8            # teto do multiplicador de velocidade

# --- Baús mágicos ---
CHEST_SIZE = 50
CHEST_HEALTH = 5
CHEST_SPAWN_INTERVAL = 15.0

# --- Orbes ---
XP_ORB_MAGNET_RADIUS = 130.0
HEALTH_ORB_CHANCE = 0.10

# ---------------------------------------------------------------------------
# Aliens (formas do Omnitrix) — estatísticas e habilidades especiais
# ---------------------------------------------------------------------------
ALIEN_DATA = {
    "Ben": {
        "stats": {"speed_mult": 1.0, "health_mult": 1.0, "damage_mult": 1.0},
        "color": COLORS["ben_green"],
        "attack_z": {
            "type": "melee", "name": "Soco",
            "range": 95, "arc_degrees": 120,
            "damage": 1.0, "cooldown": 0.25, "knockback": 120,
            "color": (110, 255, 150),
            "desc": "Soco em arco na direção da mira (rápido)",
        },
        "special": {
            "type": "omnitrix_roar", "name": "Grito do Omnitrix",
            "radius": OMNITRIX_ROAR_RADIUS, "knockback": OMNITRIX_ROAR_KNOCKBACK,
            "energy_boost": OMNITRIX_ROAR_ENERGY_BOOST,
            "energy_mult": OMNITRIX_ROAR_ENERGY_MULT,
            "cooldown": OMNITRIX_ROAR_COOLDOWN,
        },
    },
    "Quatro Braços": {
        "stats": {"speed_mult": 0.85, "health_mult": 1.4, "damage_mult": 1.2},
        "color": COLORS["four_red"],
        "attack_z": {
            "type": "ground_smash", "name": "Pancada no Chão",
            "range": 250, "width": 150,
            "damage": 2.0, "cooldown": 1.2, "knockback": 160,
            "color": (210, 210, 220),
            "desc": "Retângulo de pancada na direção da mira",
        },
        "special": {
            "type": "super_jump", "name": "Super Pulmão",
            "range": 350, "damage": 2, "radius": 120,
            "cooldown": 4.5,
        },
    },
    "XLR8": {
        "stats": {"speed_mult": 1.5, "health_mult": 0.9, "damage_mult": 0.9},
        "color": COLORS["xlr8_blue"],
        "attack_z": {
            "type": "chain_dash", "name": "Ataque em Cadeia",
            "range": 350, "num_targets": 3,
            "damage": 1.0, "cooldown": 1.4,
            "color": COLORS["diamond_cyan"],
            "desc": "Atinge os inimigos mais próximos em sequência",
        },
        "special": {
            "type": "boost", "name": "Super Velocidade",
            "duration": 3.0, "speed_mult": 2.0, "contact_damage": 999,
            "cooldown": 10.0,
        },
    },
    "Chama": {
        "stats": {"speed_mult": 1.0, "health_mult": 1.0, "damage_mult": 1.1},
        "color": COLORS["fire_orange"],
        "attack_z": {
            "type": "fireball", "name": "Bola de Fogo",
            "range": 420, "damage": 1.0, "cooldown": 0.45,
            "speed": 560.0, "explosion_radius": 80,
            "color": COLORS["fire_orange"],
            "desc": "Projétil de fogo que explode ao atingir",
        },
        "special": {
            "type": "nova", "name": "Supernova",
            "radius": 180, "damage": 3, "cooldown": 7.5,
        },
    },
    "Diamante": {
        "stats": {"speed_mult": 0.95, "health_mult": 1.2, "damage_mult": 1.0},
        "color": COLORS["diamond_cyan"],
        "attack_z": {
            "type": "diamond_shot", "name": "Estilhaço de Diamante",
            "range": 900, "damage": 2.0, "cooldown": 0.5,
            "speed": 820.0, "pierce": 4, "radius": 6,
            "color": COLORS["diamond_cyan"],
            "desc": "Estilhaço rápido e perfurante",
        },
        "special": {
            "type": "crystal_field", "name": "Campo de Cristais",
            "count": 8, "orbit_radius": 110, "duration": 4.0,
            "damage": 1, "cooldown": 12.0,
        },
    },
}
ALIEN_ORDER = list(ALIEN_DATA.keys())
PLAYER_IMAGES = {
    "Ben": "ben.png",
    "Chama": "chama.png",
    "Quatro Braços": "quatro_bracos.png",
    "Diamante": "diamante.png",
    "XLR8": "xlr8.png",
}

# ---------------------------------------------------------------------------
# Câmera — inclinação suave na direção do mouse
# ---------------------------------------------------------------------------
CAMERA_PADDING = 80          # margem extra para a rotação não revelar bordas
CAMERA_MAX_YAW = 3.5         # graus máximos de rotação
CAMERA_MAX_PITCH = 0.03      # "inclinação frontal" (compressão vertical)
CAMERA_MAX_PAN = 10.0        # desloca levemente o centro oposto à mira
CAMERA_FOLLOW_SPEED = 8.0    # velocidade do "lerp" de acompanhamento

# ---------------------------------------------------------------------------
# Upgrades escolhidos ao subir de nível
# ---------------------------------------------------------------------------
UPGRADE_OPTIONS = [
    {
        "title": "Vida Máx +2",
        "desc": "Aumenta a vida máxima em 2.",
        "apply": lambda player, world: player.increase_max_health(2),
    },
    {
        "title": "Vida Máx +30%",
        "desc": "Vida máxima +30% (cura a diferença).",
        "apply": lambda player, world: player.increase_max_health_percent(0.3),
    },
    {
        "title": "Velocidade +20%",
        "desc": "Anda 20% mais rápido.",
        "apply": lambda player, world: player.increase_speed(0.2),
    },
    {
        "title": "Dano Base +1",
        "desc": "Todas as armas causam +1 de dano.",
        "apply": lambda player, world: player.increase_base_damage(1),
    },
    {
        "title": "Dano +25%",
        "desc": "Todas as armas causam +25% de dano.",
        "apply": lambda player, world: player.increase_damage_percent(0.25),
    },
    {
        "title": "Dano +50%",
        "desc": "Todas as armas causam +50% de dano (acumula com outros).",
        "apply": lambda player, world: player.increase_damage_percent(0.5),
    },
    {
        "title": "Cadência +25%",
        "desc": "Ataca 25% mais rápido (mín. 10%).",
        "apply": lambda player, world: player.reduce_cooldowns(0.25),
    },
    {
        "title": "Cooldowns -10%",
        "desc": "Ataca mais rápido (mín. 10%).",
        "apply": lambda player, world: player.reduce_cooldowns(0.1),
    },
    {
        "title": "Explosão da Chama +40",
        "desc": "A Bola de Fogo explode em área maior.",
        "apply": lambda player, world: _upgrade_attack("Chama", "explosion_radius", 40),
    },
    {
        "title": "Pancada Mais Larga +50",
        "desc": "A Pancada no Chão do 4 Braços fica mais larga.",
        "apply": lambda player, world: _upgrade_attack("Quatro Braços", "width", 50),
    },
    {
        "title": "Cadeia do XLR8 +1 Alvo",
        "desc": "O Ataque em Cadeia atinge mais um inimigo.",
        "apply": lambda player, world: _upgrade_attack("XLR8", "num_targets", 1),
    },
    {
        "title": "Campo de Cristais +2s",
        "desc": "Os cristais do Diamante duram mais tempo.",
        "apply": lambda player, world: _upgrade_special("Diamante", "duration", 2.0),
    },
]


def _upgrade_attack(alien_name: str, attribute: str, value) -> None:
    """Aumenta um atributo do ataque primário de um alien (data-driven)."""
    attack = ALIEN_DATA[alien_name]["attack_z"]
    if attack and attribute in attack:
        attack[attribute] += value


def _upgrade_special(alien_name: str, attribute: str, value) -> None:
    """Aumenta um atributo da habilidade especial de um alien (data-driven)."""
    special = ALIEN_DATA[alien_name]["special"]
    if special and attribute in special:
        special[attribute] += value


# ===========================================================================
# FASE 2 — Power-ups, fusões, combos e Arena Infinita
# ===========================================================================

# ---------------------------------------------------------------------------
# Raridades dos Núcleos Instáveis (drops de power-up)
# ---------------------------------------------------------------------------
RARITY_ORDER = ["common", "rare", "epic", "legendary"]
RARITY_COLORS = {
    "common": (205, 210, 220),
    "rare": (80, 160, 255),
    "epic": (180, 90, 255),
    "legendary": (255, 190, 40),
}
RARITY_WEIGHTS = {"common": 50, "rare": 30, "epic": 15, "legendary": 5}
POWERUP_DROP_CHANCE = 0.06        # chance de um inimigo soltar um Núcleo
POWERUP_DROP_CHANCE_CHEST = 1.0   # baú sempre solta um Núcleo

# ---------------------------------------------------------------------------
# Catálogo de power-ups — tudo data-driven: o sorteio só escolhe por peso
# ---------------------------------------------------------------------------
POWERUP_DATA = {
    # ---------- Comuns (Nv. 1-2): sobrevivência, previsíveis ----------
    "coracao_de_ben": {
        "name": "Coração de Ben", "rarity": "common", "weight": 18, "duration": 10.0,
        "kind": "regen", "heal": 0.25, "regen_pct": 0.01,
        "desc": "Cura 25% + regenera 1%/s por 10s", "icon": "item:potion",
    },
    "botas_kevin": {
        "name": "Botas de Kevin 11", "rarity": "common", "weight": 16, "duration": 12.0,
        "kind": "speed", "speed_mult": 1.25,
        "desc": "+25% de velocidade de movimento por 12s", "icon": "item:steeringwheel",
    },
    "escudo_petrossapien": {
        "name": "Escudo Petrossápien", "rarity": "common", "weight": 14, "duration": None,
        "kind": "shield", "charges": 1,
        "desc": "Bloqueia o próximo golpe recebido", "icon": "item:shield",
    },
    "ima_turbo": {
        "name": "Ímã de Orbes Turbo", "rarity": "common", "weight": 12, "duration": 20.0,
        "kind": "magnet", "mult": 3.0,
        "desc": "Raio de coleta de XP triplicado por 20s", "icon": "item:lightbulb",
    },
    "recarga_rapida": {
        "name": "Recarga Rápida", "rarity": "common", "weight": 10, "duration": None,
        "kind": "reset_cooldowns",
        "desc": "Todos os cooldowns ativos são zerados instantaneamente", "icon": "item:battery",
    },
    # ---------- Raros (Nv. 3-4): mudam o estilo por um tempo ----------
    "minigun": {
        "name": "Minigun do Sumo Sacerdote", "rarity": "rare", "weight": 12, "duration": 15.0,
        "kind": "minigun", "bullet_damage": 0.5, "fire_rate": 0.08,
        "bullet_speed": 850.0, "bullet_range": 600,
        "desc": "O ataque primário vira disparo automático contínuo por 15s", "icon": "item:washer",
    },
    "sanguessuga": {
        "name": "Sanguessuga (Vampiro)", "rarity": "rare", "weight": 11, "duration": 15.0,
        "kind": "lifesteal", "frac": 0.15,
        "desc": "Todo golpe acertado recupera 15% do dano por 15s",
    },
    "sombra_kevin": {
        "name": "Sombra de Kevin", "rarity": "rare", "weight": 9, "duration": 12.0,
        "kind": "clone", "clones": 1, "clone_damage": 0.5, "smart": True,
        "desc": "Um clone copia seus ataques com 50% de dano por 12s",
    },
    "campo_gravidade": {
        "name": "Campo Anti-Gravidade", "rarity": "rare", "weight": 9, "duration": 8.0,
        "kind": "slow_field", "slow_mult": 0.6,
        "desc": "Inimigos ficam 40% mais lentos por 8s",
    },
    "waybig_mini": {
        "name": "Fúria do Way Big (mini)", "rarity": "rare", "weight": 8, "duration": 10.0,
        "kind": "waybig", "damage_mult": 1.3, "speed_mult": 0.8,
        "desc": "+30% de dano e -20% de velocidade por 10s",
    },
    "bomba_relogio": {
        "name": "Bomba Relógio", "rarity": "rare", "weight": 8, "duration": 12.0,
        "kind": "bomb_clock", "interval": 2.0, "radius": 100, "damage": 2,
        "desc": "Explode no seu local a cada 2s por 12s (só em inimigos)", "icon": "item:alarmclock",
    },
    # ---------- Épicos (Nv. 5-6): poderosos, arriscados, situacionais ----------
    "traje_venom": {
        "name": "Traje Venom (Triplo)", "rarity": "epic", "weight": 8, "duration": 8.0,
        "kind": "venom", "mult": 3.0, "hangover": 3.0,
        "desc": "3x dano, cadência e velocidade por 8s — sem especial; depois -20% por 3s",
    },
    "nucleo_chama": {
        "name": "Núcleo Instável de Chama", "rarity": "epic", "weight": 7, "duration": 12.0,
        "kind": "explosive", "radius": 55,
        "desc": "Todo golpe primário explode como Bola de Fogo por 12s", "icon": "fireball_icon",
    },
    "ricochete": {
        "name": "Ricochete Diamante", "rarity": "epic", "weight": 7, "duration": 15.0,
        "kind": "ricochet", "extra": 2,
        "desc": "Projéteis ricocheteiam em até 2 inimigos extras por 15s",
    },
    "fome_voraz": {
        "name": "Fome Voraz", "rarity": "epic", "weight": 6, "duration": 10.0,
        "kind": "lifesteal", "frac": 0.4, "orb_heal": 1,
        "desc": "Vampirismo de 40% + orbes curam 1 de vida por 10s", "icon": "item:chickendrumstick",
    },
    "congelamento": {
        "name": "Congelamento em Massa", "rarity": "epic", "weight": 6, "duration": None,
        "kind": "freeze", "freeze_time": 3.0,
        "desc": "Todos os inimigos na tela ficam paralisados por 3s", "icon": "item:trafficlight",
    },
    # ---------- Lendários: overpower, caóticos, o "UAU" da run ----------
    "punhos_4x": {
        "name": "Punhos de Quatro Braços x4", "rarity": "legendary", "weight": 4, "duration": 8.0,
        "kind": "quad_punch", "damage": 2.0, "fire_rate": 0.25, "knockback": 150,
        "desc": "4 socos/segundo com força de Quatro Braços por 8s", "icon": "item:rock",
    },
    "waybig_furia": {
        "name": "Modo Way Big Furioso", "rarity": "legendary", "weight": 3, "duration": 6.0,
        "kind": "waybig_fury", "stomp_radius": 520, "stomp_damage": 6, "damage_mult": 2.0,
        "desc": "Pisão de terremoto na tela + 100% de dano por 6s", "icon": "explosion_icon",
    },
    "caos_bau": {
        "name": "Caos do Baú Mágico", "rarity": "legendary", "weight": 3, "duration": 12.0,
        "kind": "chest_storm", "interval": 3.0,
        "desc": "Um baú extra cai a cada 3s por 12s", "icon": "item:castle",
    },
    "clone_baguncado": {
        "name": "Clone Bagunçado", "rarity": "legendary", "weight": 3, "duration": 10.0,
        "kind": "clone", "clones": (2, 4), "clone_damage": 0.4, "smart": False,
        "desc": "2 a 4 clones com IA aleatória cobrem a tela por 10s",
    },
    "furia_final": {
        "name": "Fúria Final", "rarity": "legendary", "weight": 3, "duration": 10.0,
        "kind": "enemy_wipe", "damage": 8, "hp_cut": 0.5,
        "desc": "Dano alto em todos; sobreviventes com -50% de vida", "icon": "explosion_icon",
    },
    "sorte_omnitrix": {
        "name": "Sorte do Omnitrix", "rarity": "legendary", "weight": 2, "duration": None,
        "kind": "lucky", "count": 2, "levels": ["common", "rare"],
        "desc": "Ativa 2 power-ups aleatórios de nível baixo/médio", "icon": "item:book",
    },
}

# ---------------------------------------------------------------------------
# Fusões do Omnitrix (Modo Prisma) — sistema de "traços" (20 combinações)
# ---------------------------------------------------------------------------
PRISM_MAX = 100.0
PRISM_GAIN_PER_HIT = 4.0     # ganho ao acertar golpes primários
PRISM_GAIN_PER_ORB = 1.0     # ganho ao coletar Núcleos
PRISM_GAIN_PER_XP = 0.5      # ganho pequeno ao coletar orbes de XP
PRISM_GAIN_PER_FRAME_CAP = 10.0  # teto por frame (não enche em 1 segundo)
FUSION_DURATION = 8.0
FUSION_HANGOVER = 3.0        # ressaca universal após a fusão (-15% velocidade)
FUSION_HANGOVER_SLOW = 0.85

# Cada alien "empresta" um traço ao alien ativo durante a fusão. O parceiro é
# sorteado quando a barra Prisma enche (e mostrado no HUD) e NUNCA é o próprio
# alien: a graça é fundir dois poderes DIFERENTES. São 5 bases x 4 parceiros
# = 20 combinações possíveis, sem lógica por par.
FUSION_TRAITS = {
    "Ben": {
        "kind": "cadence", "label": "Versatilidade",
        "color": (110, 255, 150),
        "desc": "O ataque primário fica mais rápido (cadência extra)",
    },
    "Quatro Braços": {
        "kind": "impact", "label": "Força Bruta",
        "color": (230, 90, 90),
        "desc": "Golpe primário com dano bônus, knockback extra e impacto em área",
    },
    "XLR8": {
        "kind": "burst", "label": "Velocidade",
        "color": (120, 190, 255),
        "desc": "O ataque primário dispara em rajada (2 a 4 golpes seguidos)",
    },
    "Chama": {
        "kind": "burn", "label": "Elemental",
        "color": (255, 150, 60),
        "desc": "Todo golpe primário explode em área ao acertar (queimadura)",
    },
    "Diamante": {
        "kind": "pierce", "label": "Perfuração",
        "color": (120, 220, 255),
        "desc": "Golpe primário perfura mais e ganha alcance estendido",
    },
}

# ---------------------------------------------------------------------------
# Fusões — o ESPECIAL (X) também vira uma versão combinada durante a fusão.
#
# Durante a fusão, o X deixa de ser o especial do alien base e vira um efeito
# ÚNICO nascido da mistura dos dois aliens (20 combinações, sem lógica por par:
# cada entrada é só "dados" — tipo + parâmetros). A chave é (base, parceiro).
# ---------------------------------------------------------------------------
FUSION_SPECIALS = {
    # ---------------- Ben como base (ele não tem especial: ganha um) -----
    ("Ben", "Quatro Braços"): {
        "name": "Salto de Impacto", "type": "impact_jump",
        "range": 240, "radius": 110, "damage": 2.0, "cooldown": 4.5,
    },
    ("Ben", "XLR8"): {
        "name": "Investida Relâmpago", "type": "rush",
        "distance": 340, "width": 90, "damage": 1.5, "cooldown": 5.0,
    },
    ("Ben", "Chama"): {
        "name": "Soco Solar", "type": "solar_punch",
        "range": 150, "arc_degrees": 140, "radius": 130, "damage": 3.0,
        "cooldown": 5.5,
    },
    ("Ben", "Diamante"): {
        "name": "Manoplas de Cristal", "type": "crystal_gauntlets",
        "duration": 4.0, "shard_damage": 1.0, "cooldown": 8.0,
    },
    # ---------------- Quatro Braços como base -----------------------------
    ("Quatro Braços", "Ben"): {
        "name": "Pulmão Duplo", "type": "double_jump",
        "range": 350, "radius": 120, "damage": 2.0, "cooldown": 4.5,
    },
    ("Quatro Braços", "XLR8"): {
        "name": "Saraivada de Pulmão", "type": "jump_barrage",
        "range": 300, "radius": 80, "big_radius": 150, "damage": 2.0,
        "cooldown": 6.0,
    },
    ("Quatro Braços", "Chama"): {
        "name": "Pouso Vulcânico", "type": "volcanic_landing",
        "range": 350, "radius": 120, "damage": 2.0, "burn": 2.5,
        "cooldown": 5.5,
    },
    ("Quatro Braços", "Diamante"): {
        "name": "Pouso Cristalino", "type": "crystal_landing",
        "range": 350, "radius": 120, "damage": 2.0, "shards": 4,
        "cooldown": 5.5,
    },
    # ---------------- XLR8 como base --------------------------------------
    ("XLR8", "Ben"): {
        "name": "Turbo Estável", "type": "stable_boost",
        "duration": 4.5, "cooldown": 10.0,
    },
    ("XLR8", "Quatro Braços"): {
        "name": "Rastro de Impacto", "type": "impact_trail",
        "duration": 3.0, "trail_damage": 1.0, "cooldown": 10.0,
    },
    ("XLR8", "Chama"): {
        "name": "Turbo em Chamas", "type": "fire_trail",
        "duration": 3.0, "trail_damage": 1.5, "cooldown": 10.0,
    },
    ("XLR8", "Diamante"): {
        "name": "Esteira de Cristais", "type": "crystal_boost",
        "duration": 3.0, "count": 4, "damage": 1.0, "cooldown": 10.0,
    },
    # ---------------- Chama como base -------------------------------------
    ("Chama", "Ben"): {
        "name": "Supernova Dupla", "type": "double_nova",
        "radius": 160, "damage": 2.5, "delay": 0.3, "cooldown": 7.0,
    },
    ("Chama", "Quatro Braços"): {
        "name": "Supernova de Impacto", "type": "impact_nova",
        "radius": 180, "damage": 3.0, "knockback": 320, "cooldown": 7.0,
    },
    ("Chama", "XLR8"): {
        "name": "Supernova em Cadeia", "type": "chain_nova",
        "radius": 150, "damage": 2.0, "delay": 0.15, "cooldown": 7.0,
    },
    ("Chama", "Diamante"): {
        "name": "Supernova Estilhaçada", "type": "shard_nova",
        "radius": 160, "damage": 2.5, "shards": 8, "cooldown": 7.0,
    },
    # ---------------- Diamante como base ----------------------------------
    ("Diamante", "Ben"): {
        "name": "Campo Ágil", "type": "agile_field",
        "count": 8, "orbit_radius": 110, "duration": 6.0, "spin": 3.4,
        "damage": 1.0, "cooldown": 12.0,
    },
    ("Diamante", "Quatro Braços"): {
        "name": "Campo Pesado", "type": "heavy_field",
        "count": 8, "orbit_radius": 120, "duration": 4.0, "size": 14,
        "knockback": 200, "damage": 1.5, "cooldown": 12.0,
    },
    ("Diamante", "XLR8"): {
        "name": "Campo Turbo", "type": "turbo_field",
        "count": 10, "orbit_radius": 120, "duration": 4.0, "spin": 6.5,
        "damage": 1.0, "cooldown": 12.0,
    },
    ("Diamante", "Chama"): {
        "name": "Campo em Chamas", "type": "fire_field",
        "count": 8, "orbit_radius": 110, "duration": 4.0, "damage": 1.5,
        "cooldown": 12.0,
    },
}

# Tipos de especial que envolvem pouso de pulo (usados pelo handle_jump_landing)
FUSION_JUMP_TYPES = ("impact_jump", "double_jump", "jump_barrage",
                     "volcanic_landing", "crystal_landing")

# Terceira camada da fusão: PASSIVO automático por combinação (sem botão).
# Enquanto fundido, cada par ganha um efeito constante que reforça a fantasia
# da mistura — "dados", não lógica por par. Tipos:
#   damage_reduce -> recebe menos dano (mini-resistência)
#   crystal_trail -> deixa fragmentos de cristal no chão (cosmético/de leitura)
#   smoke_aura    -> colunas de fumaça ao redor do jogador (cosmético)
FUSION_PASSIVES = {
    ("Ben", "Chama"): {"kind": "damage_reduce", "mult": 0.7},   # "pegando fogo mas controlando"
    ("XLR8", "Diamante"): {"kind": "crystal_trail"},             # Esteira de Cristais
    ("Quatro Braços", "Chama"): {"kind": "smoke_aura"},          # Pouso Vulcânico
}

# Quando ativa a fusão, o Omnitrix recarrega 100% da energia na hora: a fusão
# vira também ferramenta de gestão de energia (segunda "válvula de escape"
# além de voltar ao Ben). A ressaca pós-fusão continua como contrapeso.
FUSION_RESTORES_ENERGY = True

# Partículas modulares por traço: qualquer arma base ganha a "assinatura" do
# parceiro ao acertar (faísca elétrica, fagulha, lasca de cristal, pedra, afterimage).
FUSION_TRAIT_PARTICLES = {
    "cadence": (110, 255, 150),   # afterimage verde do Ben
    "impact":  (215, 200, 190),   # estilhaço de pedra do Quatro Braços
    "burst":   (140, 210, 255),   # faísca elétrica do XLR8
    "burn":    (255, 150, 60),    # fagulha de fogo da Chama
    "pierce":  (130, 230, 255),   # lasca de cristal do Diamante
}

# ---------------------------------------------------------------------------
# Itens (pixel arts de power-up) — assets/images/items/
# ---------------------------------------------------------------------------
# As imagens originais são enormes (3000-5000px); o pré-processamento reduz
# para 128px e remove o fundo (chroma-key) quando não há canal alfa. Aqui só
# mapeamos nome -> arquivo e o tamanho de exibição em jogo.
ITEM_IMAGES = {
    "chickendrumstick": "chickendrumstick.png",
    "potion": "potion.png",
    "book": "book.png",
    "washer": "washer.png",
    "shield": "shield.png",
    "rock": "rock.png",
    "lightbulb": "lightbulb.png",
    "battery": "battery.png",
    "castle": "castle.png",
    "alarmclock": "alarmclock.png",
    "trafficlight": "trafficlight.png",
    "steeringwheel": "steeringwheel.png",
}
ITEM_SIZES = {
    "chickendrumstick": (26, 26),   # health orb (comida cura!)
    "potion": (26, 26),             # Coração de Ben (poção de cura)
    "book": (26, 26),               # Sorte do Omnitrix (livro de magia)
    "washer": (20, 20),             # bala da minigun (arruela voando!)
    "shield": (28, 28),             # Escudo Petrossápien
    "rock": (26, 26),               # Fúria do Way Big / Punhos x4
    "lightbulb": (26, 26),          # Ímã de Orbes (lâmpada "atrai" orbes)
    "battery": (26, 26),            # Recarga Rápida (bateria!)
    "castle": (96, 96),             # decoração do mapa (HUD reduz no scale)
    "alarmclock": (26, 26),         # Bomba Relógio (despertador = bomba!)
    "trafficlight": (22, 22),       # Campo Anti-Gravidade (semáforo = parar)
    "steeringwheel": (26, 26),      # Botas de Kevin (volante = velocidade!)
}

# ---------------------------------------------------------------------------
# Combos (skill expression) — seção 1.2 do design
# ---------------------------------------------------------------------------
COMBO_WINDOW = 1.5          # janela para encadear ataques primários
COMBO_THRESHOLD = 3         # 3 acertos sem errar libera o bônus
COMBO_BONUS = 0.5           # próximo golpe primário +50%
QUICK_SWAP_WINDOW = 0.4     # trocar de alien + golpe rápido = crítico (2x)
ELEMENTAL_WINDOW = 2.0      # Chama -> Diamante em 2s = estilhaço em fogo

# ---------------------------------------------------------------------------
# Modos de jogo e recordes (Arena Infinita)
# ---------------------------------------------------------------------------
GAME_MODES = [
    ("arena", "Arena Infinita", "Sobreviva o máximo que conseguir"),
    ("campaign", "Campanha 1-10", "Em breve: níveis com objetivos e chefes"),
    ("duel", "Duelo Online", "Em breve: 1x1 contra outro jogador"),
]
SCORES_FILE = BASE_DIR / "scores.json"
MAX_SCORES = 5
