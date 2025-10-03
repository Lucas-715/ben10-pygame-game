import pygame
import random
import os

# ==============================================================================
# 1. CONFIGURAÇÕES
# ==============================================================================
# --- Tela e Jogo ---
largura_tela = 1024
altura_tela = 768
FPS = 60
GAME_TITLE = "Ben 10 - A Ameaça Eterna 2D"

# --- Dimensões do Mundo ---
largura_mundo = 3000
altura_mundo = 2000

# --- Cores ---
COLORS = {
    'BRANCO': (255, 255, 255), 'PRETO': (0, 0, 0), 'VERDE': (0, 255, 0),
    'VERMELHO': (217, 30, 24), 'AZUL': (30, 139, 195), 'LARANJA': (244, 120, 37),
    'CYA': (27, 188, 155), 'CINZA': (128, 128, 128), 'AMARELO': (255, 255, 0),
    'ROXO': (155, 89, 182), 'VERDE_VIDA': (46, 204, 113), 'AMARELO_VIDA': (241, 196, 15),
    'VERMELHO_VIDA': (192, 57, 43), 'CINZA_FUNDO_VIDA': (44, 62, 80),
    'ROXO_FUNDO1': (25, 15, 35), 'ROXO_FUNDO2': (45, 25, 65),
    'OMNITRIX_GREEN': (0, 255, 120), 'XP_BLUE': (52, 152, 219)
}

# --- Configurações da UI ---
UI_FONT_SIZE = 28
TITLE_FONT_SIZE = 64
DAMAGE_TEXT_FONT_SIZE = 22

# --- Caminhos de Arquivos ---
PASTA_ASSETS = 'assets'
PASTA_SONS = os.path.join(PASTA_ASSETS, 'sounds')
PASTA_MUSICA = os.path.join(PASTA_ASSETS, 'sounds', 'music')
PASTA_IMAGENS = os.path.join(PASTA_ASSETS, 'images')

# ==============================================================================
# 2. CONFIGURAÇÕES DE GAMEPLAY
# ==============================================================================
# --- Jogador ---
PLAYER_SIZE = (50, 50)
PLAYER_SPEED_BASE = 4
PLAYER_MAX_HEALTH_BASE = 10
PLAYER_INVENCIVEL_DURATION = 1500

# --- Habilidade de Dash ---
DASH_SPEED = 25
DASH_DURATION = 150
DASH_COOLDOWN = 1000
DASH_INVENCIBILITY_DURATION = 200

# --- Sistema de XP e Níveis ---
XP_PER_KILL = { 'cavaleiro_n1': 10, 'cavaleiro_n2': 15 }
XP_PARA_PROXIMO_NIVEL = lambda nivel: 100 + (nivel - 1) * 50

# --- Inimigos ---
ENEMY_DAMAGE = 1
ENEMY_SPAWN_INTERVAL = 1800
ORBE_VIDA_CHANCE = 0.10
KILL_COUNT_WAVE_2 = 20
ENEMY_DATA = {
    'cavaleiro_n1': {'size': (45, 45), 'health': 2, 'speed': 1.5, 'image_file': 'cavaleiro_nivel1.png'},
    'cavaleiro_n2': {'size': (48, 48), 'health': 4, 'speed': 1.6, 'image_file': 'cavaleiro_nivel2.png'},
}

# --- Baús Mágicos ---
BAU_SIZE = (50, 50)
BAU_HEALTH = 5
BAU_SPAWN_INTERVAL = 15000

# --- Música e Efeitos ---
RAIO_COMBATE = 500
KILL_COUNT_FASE_2 = 50
CAMERA_SHAKE_INTENSITY = 10
CAMERA_SHAKE_DURATION = 200

# --- Sistema de dados dos aliens (NOVAS HABILIDADES) ---
ALIEN_DATA = {
    'Ben': {
        'stats': {'speed_mult': 1.0, 'max_health_mult': 1.0},
        'color': COLORS['VERDE'],
        'ataque_z': {'type': 'melee', 'damage': 1, 'size': (50, 50), 'cooldown': 450, 'duration': 150, 'color': COLORS['VERDE']},
        'ataque_x': None
    },
    'Quatro Braços': {
        'stats': {'speed_mult': 0.85, 'max_health_mult': 1.4},
        'color': COLORS['VERMELHO'],
        'ataque_z': {'type': 'ground_smash', 'damage': 2, 'cooldown': 1200, 'duration': 200, 'width': 150, 'length': 250, 'knockback': 40, 'color': (200, 200, 200, 100)},
        'ataque_x': {'type': 'super_pulo', 'damage': 2, 'cooldown': 3000, 'jump_speed': 15, 'jump_distance': 350, 'jump_invincible_duration': 600, 'damage_radius': 120, 'damage_duration': 200, 'color': COLORS['VERMELHO']}
    },
    'XLR8': {
        'stats': {'speed_mult': 1.5, 'max_health_mult': 0.9},
        'color': COLORS['AZUL'],
        'ataque_z': {'type': 'chain_dash_attack', 'damage': 1, 'cooldown': 1500, 'num_targets': 3, 'range': 350, 'color': COLORS['CYA']},
        'ataque_x': {'type': 'boost', 'cooldown': 7000, 'duration': 3000, 'speed_mult': 2.0, 'contact_damage': 999}
    },
    'Chama': {
        'stats': {'speed_mult': 1.0, 'max_health_mult': 1.0},
        'color': COLORS['LARANJA'],
        'ataque_z': {'type': 'chama_projétil', 'damage': 1, 'size': (25, 25), 'speed': 8, 'cooldown': 600, 'explosion_radius': 80, 'explosion_duration': 200, 'color': COLORS['LARANJA']},
        'ataque_x': {'type': 'supernova', 'damage': 3, 'radius': 180, 'cooldown': 5000, 'duration': 300, 'color': COLORS['LARANJA']}
    },
    'Diamante': {
        'stats': {'speed_mult': 0.95, 'max_health_mult': 1.2},
        'color': COLORS['CYA'],
        'ataque_z': {'type': 'diamante_projétil', 'damage': 1, 'size': (25, 25), 'speed': 12, 'cooldown': 700, 'color': COLORS['CYA']},
        'ataque_x': {'type': 'crystal_field', 'damage': 1, 'cooldown': 8000, 'duration': 4000, 'spawn_radius': 100, 'num_crystals': 8, 'rotation_speed': 20, 'color': COLORS['CYA']}
    }
}
ALL_FORMS = list(ALIEN_DATA.keys())

# --- Sistema de Energia do Omnitrix ---
OMNITRIX_MAX_ENERGY = 100
OMNITRIX_DRAIN_RATE = 5
OMNITRIX_RECHARGE_RATE = 10

# --- Opções de Upgrade ---
# Funções para os upgrades gerais
def increase_max_health(player):
    player.update_max_health(2)

def increase_speed_mult(player):
    player.update_speed_mult(0.1)

def increase_base_damage(player):
    player.update_base_damage(1)

def reduce_cooldown_mult(player):
    player.update_cooldown_mult(-0.1)

# Funções para os upgrades de aliens específicos
def upgrade_chama_explosion(player):
    player.upgrade_alien_attack('Chama', 'ataque_z', 'explosion_radius', 40)

def upgrade_4bracos_smash(player):
    player.upgrade_alien_attack('Quatro Braços', 'ataque_z', 'width', 50)

def upgrade_xlr8_chain(player):
    player.upgrade_alien_attack('XLR8', 'ataque_z', 'num_targets', 1)

def upgrade_diamante_field(player):
    player.upgrade_alien_attack('Diamante', 'ataque_x', 'duration', 2000)
    
UPGRADE_OPTIONS = {
    'health_up': {'title': "Vida Max +2", 'effect': increase_max_health},
    'speed_up': {'title': "Velocidade +10%", 'effect': increase_speed_mult},
    'damage_up': {'title': "Dano Base +1", 'effect': increase_base_damage},
    'cooldown_redux': {'title': "Cooldowns -10%", 'effect': reduce_cooldown_mult},
    'chama_z_up': {'title': "Explosão Chama Maior", 'effect': upgrade_chama_explosion},
    '4bracos_smash_up': {'title': "Smash + Largo", 'effect': upgrade_4bracos_smash},
    'xlr8_chain_up': {'title': "Ataque em Cadeia +1 Alvo", 'effect': upgrade_xlr8_chain},
    'diamante_field_up': {'title': "Campo de Cristal +2s", 'effect': upgrade_diamante_field},
}


# ==============================================================================
# 3. Inicializando
# ==============================================================================
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.font.init()

tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption(GAME_TITLE)
clock = pygame.time.Clock()
ui_font = pygame.font.Font(None, UI_FONT_SIZE)
title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
damage_font = pygame.font.Font(None, DAMAGE_TEXT_FONT_SIZE)

class DummySound:
    def play(self): pass
    def set_volume(self, vol): pass

sons_a_carregar = {
    'transformacao': 'omnitrix-transform.mp3', 'selecao_alien': 'escolhendo-alien.mp3',
    'chama_z': 'fire-attack.ogg', 'chama_x': 'fiery_explosion.ogg',
    '4bracos_z': 'force_impact.ogg', '4bracos_x': 'force_impact2.ogg',
    'diamante_z': 'atack_dimond.ogg', 'diamante_x': 'dimond_shield.ogg',
    'xlr8_z': 'attack_hit.mp3', 'xlr8_x': 'super_velocidade.ogg',
    'ben_z': 'attack_hit.mp3', 'dash_eletrico_sfx': 'electric_spark.ogg',
    'level_up': 'level-up.ogg'
}
sons_sfx = {}
for nome_som, nome_arquivo in sons_a_carregar.items():
    caminho_completo = os.path.join(PASTA_SONS, 'sfx', nome_arquivo)
    try:
        sons_sfx[nome_som] = pygame.mixer.Sound(caminho_completo)
    except (pygame.error, FileNotFoundError):
        print(f"Aviso: Arquivo de som não encontrado: '{caminho_completo}'. Um som falso será usado.")
        sons_sfx[nome_som] = DummySound()

enemy_images = {}
for enemy_type, data in ENEMY_DATA.items():
    caminho_completo = os.path.join(PASTA_IMAGENS, 'enemies', data['image_file'])
    try:
        img = pygame.image.load(caminho_completo).convert_alpha()
        enemy_images[enemy_type] = pygame.transform.scale(img, data['size'])
    except (pygame.error, FileNotFoundError):
        print(f"Aviso: Imagem de inimigo não encontrada: '{caminho_completo}'. Um placeholder será usado.")
        enemy_images[enemy_type] = pygame.Surface(data['size'])
        enemy_images[enemy_type].fill(COLORS['ROXO'])

player_images = {}
player_image_files = {
    'Ben': 'ben.png', 'Chama': 'chama.png', 'Quatro Braços': 'quatro_bracos.png',
    'Diamante': 'diamante.png', 'XLR8': 'xlr8.png'
}
for name, filename in player_image_files.items():
    caminho_completo = os.path.join(PASTA_IMAGENS, 'player', filename)
    try:
        img = pygame.image.load(caminho_completo).convert_alpha()
        player_images[name] = pygame.transform.scale(img, PLAYER_SIZE)
    except (pygame.error, FileNotFoundError):
        print(f"Aviso: Imagem de jogador não encontrada: '{caminho_completo}'. Uma cor será usada.")
        player_images = None
        break

try:
    bau_image = pygame.image.load(os.path.join(PASTA_IMAGENS, 'objects', 'bau_magico.png')).convert_alpha()
    bau_image = pygame.transform.scale(bau_image, BAU_SIZE)
    vida_orb_image = pygame.image.load(os.path.join(PASTA_IMAGENS, 'ui', 'vida.png')).convert_alpha()
    vida_orb_image = pygame.transform.scale(vida_orb_image, (25, 25))
    ataque_diamante_image = pygame.image.load(os.path.join(PASTA_IMAGENS, 'ui', 'ataque_diamante.png')).convert_alpha()
    ataque_diamante_image = pygame.transform.scale(ataque_diamante_image, (30, 30))
    vida_icon = vida_orb_image
except (pygame.error, FileNotFoundError) as e:
    print(f"Aviso: Falha ao carregar uma ou mais imagens de UI/Objetos: {e}")
    bau_image, vida_orb_image, ataque_diamante_image, vida_icon = None, None, None, None

def criar_particulas(posicao, numero, cor, vel_max, duracao, raio_max):
    for _ in range(numero):
        particulas.append({
            'pos': pygame.math.Vector2(posicao),
            'vel': pygame.math.Vector2(random.uniform(-vel_max, vel_max), random.uniform(-vel_max, vel_max)),
            'radius': random.randint(int(raio_max / 2), raio_max),
            'lifetime': random.randint(int(duracao / 2), duracao),
            'color': cor
        })

def criar_texto_flutuante(texto, pos, cor):
    textos_flutuantes.append({'text': texto, 'pos': pygame.math.Vector2(pos), 'color': cor, 'timer': 45})

class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(largura_mundo / 2, altura_mundo / 2, PLAYER_SIZE[0], PLAYER_SIZE[1])
        self.direction_vec = pygame.math.Vector2(1, 0)
        self.level = 1
        self.xp = 0
        self.base_max_health = PLAYER_MAX_HEALTH_BASE
        self.base_damage = 0
        self.speed_mult = 1.0
        self.cooldown_mult = 1.0
        self.state = 'normal'
        self.invencivel_fim = 0
        self.target_pos = None
        self.active_alien_name = 'Ben'
        self.omnitrix_energy = OMNITRIX_MAX_ENERGY
        self.health = self.base_max_health
        self.update_stats_for_alien()

    def update_max_health(self, amount):
        self.base_max_health += amount
        self.update_stats_for_alien()
        self.health += amount

    def update_speed_mult(self, amount):
        self.speed_mult += amount
        self.update_stats_for_alien()

    def update_base_damage(self, amount):
        self.base_damage += amount

    def update_cooldown_mult(self, amount):
        self.cooldown_mult = max(0.1, self.cooldown_mult + amount)

    def upgrade_alien_attack(self, alien, attack_type, param, value_change):
        if alien in ALIEN_DATA and ALIEN_DATA[alien].get(attack_type):
            if param in ALIEN_DATA[alien][attack_type]:
                ALIEN_DATA[alien][attack_type][param] += value_change

    def add_xp(self, amount):
        self.xp += amount
        xp_necessario = XP_PARA_PROXIMO_NIVEL(self.level)
        if self.xp >= xp_necessario:
            self.level += 1
            self.xp -= xp_necessario
            sons_sfx['level_up'].play()
            criar_texto_flutuante("LEVEL UP!", self.rect.center, COLORS['AMARELO'])
            return True
        return False

    def update_stats_for_alien(self):
        stats = ALIEN_DATA[self.active_alien_name]['stats']
        self.max_health = int(self.base_max_health * stats['max_health_mult'])
        self.speed = PLAYER_SPEED_BASE * self.speed_mult * stats['speed_mult']
        self.health = min(self.max_health, self.health)

    def change_form(self, new_form_name):
        if self.active_alien_name == new_form_name: return
        if new_form_name != 'Ben' and self.omnitrix_energy < 10: return

        self.active_alien_name = new_form_name
        self.update_stats_for_alien()
        sons_sfx['transformacao'].play()
        ataques_ativos.append({
            'type': 'shockwave', 'visual': 'circle_outline', 'color': COLORS['OMNITRIX_GREEN'],
            'center': self.rect.center, 'rect': pygame.Rect(0, 0, 0, 0),
            'start_time': pygame.time.get_ticks(), 'end_time': pygame.time.get_ticks() + 400,
            'start_radius': 10, 'max_radius': 120, 'hit_enemies': {}, 'damage': 0
        })

def reset_game_state():
    global inimigos, orbes_vida, particulas, baus_magicos, ataques_ativos, textos_flutuantes
    global ultimo_spawn_tempo, ultimo_spawn_bau, camera_shake_fim, flash_dano_fim, cooldowns
    global current_selection_index, upgrade_choices, estado_jogo, inimigos_mortos_contador
    
    jogador.reset()
    inimigos, orbes_vida, particulas, baus_magicos, ataques_ativos, textos_flutuantes = [], [], [], [], [], []
    inimigos_mortos_contador = 0
    ultimo_spawn_tempo, ultimo_spawn_bau = 0, 0
    camera_shake_fim, flash_dano_fim = 0, 0
    cooldowns = {'z': 0, 'x': 0, 'dash': 0}
    current_selection_index = 0
    upgrade_choices = []
    estado_jogo = 'jogando'

def tocar_musica(nome_musica):
    global musica_atual
    if musica_atual == nome_musica or nome_musica in musicas_com_falha: return
    musica_atual = nome_musica
    caminho_completo = os.path.join(PASTA_MUSICA, nome_musica)
    try:
        pygame.mixer.music.load(caminho_completo)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1, fade_ms=1000)
    except (pygame.error, FileNotFoundError) as e:
        print(f"Erro ao carregar a música '{caminho_completo}': {e}")
        musicas_com_falha.add(nome_musica)
        musica_atual = None

def draw_elements():
    cam_center_offset = pygame.math.Vector2(camera_rect.center)
    for y in range(0, altura_tela, 20):
        ratio = y / altura_tela
        cor = (int(COLORS['ROXO_FUNDO1'][0] * (1 - ratio) + COLORS['ROXO_FUNDO2'][0] * ratio),
               int(COLORS['ROXO_FUNDO1'][1] * (1 - ratio) + COLORS['ROXO_FUNDO2'][1] * ratio),
               int(COLORS['ROXO_FUNDO1'][2] * (1 - ratio) + COLORS['ROXO_FUNDO2'][2] * ratio))
        pygame.draw.rect(tela, cor, (0, y, largura_tela, 20))

    for star in estrelas:
        pos_x = (star['pos'][0] - cam_center_offset.x * star['depth']) % largura_mundo
        pos_y = (star['pos'][1] - cam_center_offset.y * star['depth']) % altura_mundo
        screen_x = pos_x - camera_rect.left + cam_center_offset.x * star['depth']
        screen_y = pos_y - camera_rect.top + cam_center_offset.y * star['depth']
        if 0 < screen_x < largura_tela and 0 < screen_y < altura_tela:
            color_val = int(255 * star['depth'])
            pygame.draw.circle(tela, (color_val, color_val, color_val), (screen_x, screen_y), 2 * star['depth'])

    for p in particulas:
        pos_desenho = p['pos'] - pygame.math.Vector2(camera_rect.topleft)
        pygame.draw.circle(tela, p['color'], pos_desenho, int(p['radius']))

    for orbe in orbes_vida:
        rect_desenho = orbe.move(-camera_rect.x, -camera_rect.y)
        if vida_orb_image:
            tela.blit(vida_orb_image, vida_orb_image.get_rect(center=rect_desenho.center))
        else:
            pygame.draw.circle(tela, COLORS['VERDE_VIDA'], rect_desenho.center, 10)

    for bau in baus_magicos:
        rect_desenho = bau['rect'].move(-camera_rect.x, -camera_rect.y)
        if bau_image:
            if bau['hit_flash_timer'] > 0:
                bau['hit_flash_timer'] -= 1
                imagem_branca = bau_image.copy()
                imagem_branca.fill(COLORS['BRANCO'], special_flags=pygame.BLEND_RGB_ADD)
                tela.blit(imagem_branca, rect_desenho)
            else:
                tela.blit(bau_image, rect_desenho)
        else:
            pygame.draw.rect(tela, COLORS['AMARELO'], rect_desenho)
        if bau['health'] < bau['max_health']:
            largura_barra_fundo = bau['rect'].width
            largura_barra_vida = (bau['health'] / bau['max_health']) * largura_barra_fundo
            pos_barra = (rect_desenho.x, rect_desenho.top - 10)
            pygame.draw.rect(tela, COLORS['VERMELHO_VIDA'], (pos_barra[0], pos_barra[1], largura_barra_fundo, 5))
            pygame.draw.rect(tela, COLORS['VERDE_VIDA'], (pos_barra[0], pos_barra[1], largura_barra_vida, 5))

    for inimigo in inimigos:
        rect_desenho = inimigo['rect'].move(-camera_rect.x, -camera_rect.y)
        imagem_inimigo = enemy_images[inimigo['type']]
        if inimigo['hit_flash_timer'] > 0:
            inimigo['hit_flash_timer'] -= 1
            imagem_branca = imagem_inimigo.copy()
            imagem_branca.fill(COLORS['BRANCO'], special_flags=pygame.BLEND_RGB_ADD)
            tela.blit(imagem_branca, rect_desenho)
        else:
            tela.blit(imagem_inimigo, rect_desenho)
        if inimigo['health'] < inimigo['max_health']:
            largura_barra_fundo = inimigo['rect'].width
            largura_barra_vida = (inimigo['health'] / inimigo['max_health']) * largura_barra_fundo
            pos_barra = (rect_desenho.x, rect_desenho.top - 10)
            pygame.draw.rect(tela, COLORS['VERMELHO_VIDA'], (pos_barra[0], pos_barra[1], largura_barra_fundo, 5))
            pygame.draw.rect(tela, COLORS['VERDE_VIDA'], (pos_barra[0], pos_barra[1], largura_barra_vida, 5))

    for ataque in ataques_ativos:
        if ataque.get('visual') == 'none': continue
        
        if 'rect' in ataque:
            rect_desenho = ataque['rect'].move(-camera_rect.x, -camera_rect.y)
        
        if ataque['visual'] == 'rect':
            if ataque['type'] == 'ground_smash':
                s = pygame.Surface(rect_desenho.size, pygame.SRCALPHA)
                s.fill(ataque['color'])
                tela.blit(s, rect_desenho)
            else:
                pygame.draw.rect(tela, ataque['color'], rect_desenho)
        elif ataque['visual'] == 'circle':
            pygame.draw.circle(tela, ataque['color'], rect_desenho.center, rect_desenho.width / 2)
        elif ataque['visual'] == 'circle_outline':
            draw_radius = max(5, int(ataque.get('current_radius', 0)))
            pygame.draw.circle(tela, ataque['color'], rect_desenho.center, draw_radius, 4)
        elif ataque['visual'] == 'image':
            img = ataque.get('image')
            if img:
                rotated_image = pygame.transform.rotate(img, -ataque.get('angle', 0))
                tela.blit(rotated_image, rotated_image.get_rect(center=rect_desenho.center))
        elif ataque['visual'] == 'line_trail':
            start_pos_screen = pygame.math.Vector2(ataque['start']) - pygame.math.Vector2(camera_rect.topleft)
            end_pos_screen = pygame.math.Vector2(ataque['end']) - pygame.math.Vector2(camera_rect.topleft)
            pygame.draw.line(tela, ataque['color'], start_pos_screen, end_pos_screen, 4)
    
    rect_desenho = jogador.rect.move(-camera_rect.x, -camera_rect.y)
    if player_images:
        agora = pygame.time.get_ticks()
        if agora < jogador.invencivel_fim and int(agora / 150) % 2 == 0:
            pass
        else:
            tela.blit(player_images[jogador.active_alien_name], rect_desenho)
    else:
        pygame.draw.rect(tela, ALIEN_DATA[jogador.active_alien_name]['color'], rect_desenho)

    for texto in textos_flutuantes[:]:
        texto['timer'] -= 1
        if texto['timer'] <= 0:
            textos_flutuantes.remove(texto)
        else:
            alpha = max(0, 255 * (texto['timer'] / 45))
            texto['pos'].y -= 0.5
            surface = damage_font.render(texto['text'], True, texto['color'])
            surface.set_alpha(alpha)
            pos_desenho = (texto['pos'].x - camera_rect.x, texto['pos'].y - camera_rect.y)
            tela.blit(surface, surface.get_rect(center=pos_desenho))

    nome_alien_selecionado = ALL_FORMS[current_selection_index]
    selection_surface = ui_font.render(f"Selecionado: {nome_alien_selecionado}", True, COLORS['BRANCO'])
    tela.blit(selection_surface, (15, 15))

    contador_surface = ui_font.render(f"Derrotados: {inimigos_mortos_contador}", True, COLORS['BRANCO'])
    tela.blit(contador_surface, contador_surface.get_rect(topright=(largura_tela - 15, 15)))

    pos_y_vida = 50
    pos_x_barra = 15
    if vida_icon:
        tela.blit(vida_icon, (15, pos_y_vida))
        pos_x_barra = 50

    if jogador.max_health > 0:
        health_ratio = jogador.health / jogador.max_health
        if health_ratio > 0.6: cor_vida = COLORS['VERDE_VIDA']
        elif health_ratio > 0.3: cor_vida = COLORS['AMARELO_VIDA']
        else: cor_vida = COLORS['VERMELHO_VIDA']
        largura_barra_fundo = 200
        largura_barra_vida = health_ratio * largura_barra_fundo
        pygame.draw.rect(tela, COLORS['CINZA_FUNDO_VIDA'], (pos_x_barra, pos_y_vida, largura_barra_fundo, 25))
        if largura_barra_vida > 0: pygame.draw.rect(tela, cor_vida, (pos_x_barra, pos_y_vida, largura_barra_vida, 25))

    xp_necessario = XP_PARA_PROXIMO_NIVEL(jogador.level)
    largura_barra_xp = (jogador.xp / xp_necessario) * 200 if xp_necessario > 0 else 0
    pygame.draw.rect(tela, COLORS['CINZA_FUNDO_VIDA'], (pos_x_barra, pos_y_vida + 30, 200, 15))
    if largura_barra_xp > 0: pygame.draw.rect(tela, COLORS['XP_BLUE'], (pos_x_barra, pos_y_vida + 30, largura_barra_xp, 15))
    
    largura_barra_energia = (jogador.omnitrix_energy / OMNITRIX_MAX_ENERGY) * 200
    pygame.draw.rect(tela, COLORS['CINZA_FUNDO_VIDA'], (pos_x_barra, pos_y_vida + 50, 200, 15))
    if largura_barra_energia > 0: pygame.draw.rect(tela, COLORS['OMNITRIX_GREEN'], (pos_x_barra, pos_y_vida + 50, largura_barra_energia, 15))

    agora = pygame.time.get_ticks()
    if agora < flash_dano_fim:
        flash_surface = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        flash_surface.fill((255, 0, 0, 100))
        tela.blit(flash_surface, (0,0))
    
    if estado_jogo == 'level_up':
        overlay = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        tela.blit(overlay, (0, 0))
        titulo_surf = title_font.render("NOVO NÍVEL!", True, COLORS['AMARELO'])
        tela.blit(titulo_surf, titulo_surf.get_rect(center=(largura_tela / 2, altura_tela / 2 - 150)))
        for i, upgrade in enumerate(upgrade_choices):
            texto = f"[{i + 1}] {upgrade['title']}"
            upgrade_surf = ui_font.render(texto, True, COLORS['BRANCO'])
            tela.blit(upgrade_surf, upgrade_surf.get_rect(center=(largura_tela / 2, altura_tela / 2 - 50 + i * 50)))

# ==============================================================================
# 4. LOOP PRINCIPAL
# ==============================================================================
jogador = Player()
inimigos, orbes_vida, particulas, baus_magicos, ataques_ativos, textos_flutuantes = [], [], [], [], [], []
inimigos_mortos_contador = 0
ultimo_spawn_tempo, ultimo_spawn_bau = 0, 0
camera_rect = pygame.Rect(0, 0, largura_tela, altura_tela)
mundo_rect = pygame.Rect(0, 0, largura_mundo, altura_mundo)
estado_jogo = 'tela_inicial'
musica_atual, musicas_com_falha = None, set()
camera_shake_fim, flash_dano_fim = 0, 0
cooldowns = {'z': 0, 'x': 0, 'dash': 0}
current_selection_index = 0
upgrade_choices = []
estrelas = [{'pos': [random.randint(0, largura_mundo), random.randint(0, altura_mundo)],
             'depth': random.uniform(0.1, 0.8)} for _ in range(400)]

rodando = True
while rodando:
    agora = pygame.time.get_ticks()
    clock.tick(FPS)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        
        if estado_jogo == 'tela_inicial':
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                reset_game_state()
        
        elif estado_jogo == 'game_over':
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
                reset_game_state()

        elif estado_jogo == 'level_up':
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_1, pygame.K_KP_1) and len(upgrade_choices) > 0:
                    upgrade_choices[0]['effect'](jogador)
                    estado_jogo = 'jogando'
                elif evento.key in (pygame.K_2, pygame.K_KP_2) and len(upgrade_choices) > 1:
                    upgrade_choices[1]['effect'](jogador)
                    estado_jogo = 'jogando'
                elif evento.key in (pygame.K_3, pygame.K_KP_3) and len(upgrade_choices) > 2:
                    upgrade_choices[2]['effect'](jogador)
                    estado_jogo = 'jogando'
        
        elif estado_jogo == 'jogando':
            if evento.type == pygame.KEYDOWN:
                dados_alien_ativo = ALIEN_DATA[jogador.active_alien_name]
                if evento.key == pygame.K_z:
                    ataque_info = dados_alien_ativo.get('ataque_z')
                    if ataque_info and agora > cooldowns['z']:
                        cooldowns['z'] = agora + ataque_info['cooldown'] * jogador.cooldown_mult
                        
                        if ataque_info['type'] == 'melee':
                            sons_sfx['ben_z'].play()
                            pos = jogador.rect.center + jogador.direction_vec * (PLAYER_SIZE[0] / 2 + 15)
                            ataque_rect = pygame.Rect(0, 0, ataque_info['size'][0], ataque_info['size'][1])
                            ataque_rect.center = pos
                            ataques_ativos.append({'rect': ataque_rect, 'end_time': agora + ataque_info['duration'], 'type': 'melee', 'damage': ataque_info['damage'], 'visual': 'rect', 'color': ataque_info['color'], 'hit_enemies': {}})
                        
                        elif ataque_info['type'] == 'ground_smash':
                            sons_sfx['4bracos_z'].play()
                            camera_shake_fim = agora + CAMERA_SHAKE_DURATION
                            direcao = jogador.direction_vec

                            # CORREÇÃO: Verifica a direção para criar o retângulo na orientação correta
                            if abs(direcao.x) > abs(direcao.y): # Ataque é mais horizontal
                                largura_smash = ataque_info['length']
                                altura_smash = ataque_info['width']
                            else: # Ataque é mais vertical
                                largura_smash = ataque_info['width']
                                altura_smash = ataque_info['length']

                            smash_rect = pygame.Rect(0, 0, largura_smash, altura_smash)
                            smash_rect.center = jogador.rect.center + direcao * (ataque_info['length'] / 2)
                            
                            ataques_ativos.append({'rect': smash_rect, 'end_time': agora + ataque_info['duration'], 'type': 'ground_smash', 'damage': ataque_info['damage'], 'visual': 'rect', 'color': ataque_info['color'], 'knockback': ataque_info['knockback'], 'hit_enemies': {}})
                            
                        elif ataque_info['type'] == 'chain_dash_attack':
                            sons_sfx['xlr8_z'].play()
                            alvos_potenciais = [i for i in inimigos if pygame.math.Vector2(i['rect'].center).distance_to(jogador.rect.center) < ataque_info['range']]
                            alvos_potenciais.sort(key=lambda i: pygame.math.Vector2(i['rect'].center).distance_to(jogador.rect.center))
                            alvos = alvos_potenciais[:ataque_info['num_targets']]

                            if alvos:
                                pos_anterior = jogador.rect.center
                                for i, alvo in enumerate(alvos):
                                    dano = ataque_info['damage'] + jogador.base_damage
                                    alvo['health'] -= dano
                                    criar_texto_flutuante(str(int(dano)), alvo['rect'].center, COLORS['BRANCO'])
                                    alvo['hit_flash_timer'] = 5
                                    criar_particulas(alvo['rect'].center, 10, ataque_info['color'], 3, 15, 4)
                                    ataques_ativos.append({'type': 'line_trail', 'visual': 'line_trail', 'start': pos_anterior, 'end': alvo['rect'].center, 'color': ataque_info['color'], 'end_time': agora + 200})
                                    pos_anterior = alvo['rect'].center
                                    if i == len(alvos) - 1:
                                        jogador.rect.center = alvo['rect'].center

                        elif ataque_info['type'] == 'chama_projétil':
                            sons_sfx['chama_z'].play()
                            ataque_rect = pygame.Rect(0,0, ataque_info['size'][0], ataque_info['size'][1])
                            ataque_rect.center = jogador.rect.center
                            ataques_ativos.append({'rect': ataque_rect, 'end_time': agora + 5000, 'type': 'chama_projétil', 'damage': ataque_info['damage'], 'dir_vec': jogador.direction_vec.copy(), 'speed': ataque_info['speed'], 'visual': 'rect', 'color': ataque_info['color'], 'hit_enemies': {}})
                        
                        elif ataque_info['type'] == 'diamante_projétil' and ataque_diamante_image:
                            sons_sfx['diamante_z'].play()
                            proj_image_scaled = pygame.transform.scale(ataque_diamante_image, ALIEN_DATA['Diamante']['ataque_z']['size'])
                            ataque_rect = proj_image_scaled.get_rect(center=jogador.rect.center)
                            ataques_ativos.append({'rect': ataque_rect, 'end_time': agora + 5000, 'type': 'diamante_projétil', 'damage': ataque_info['damage'], 'dir_vec': jogador.direction_vec.copy(), 'speed': ataque_info['speed'], 'visual': 'image', 'image': proj_image_scaled, 'hit_enemies': {}, 'angle': jogador.direction_vec.angle_to(pygame.math.Vector2(1,0))})

                if evento.key == pygame.K_x:
                    ataque_info = dados_alien_ativo.get('ataque_x')
                    if ataque_info and agora > cooldowns['x']:
                        cooldowns['x'] = agora + ataque_info['cooldown'] * jogador.cooldown_mult
                        
                        if ataque_info['type'] == 'super_pulo':
                            jogador.state = 'super_pulo_saltando'
                            jogador.invencivel_fim = agora + ataque_info['jump_invincible_duration']
                            jogador.target_pos = pygame.math.Vector2(jogador.rect.center) + jogador.direction_vec * ataque_info['jump_distance']
                        
                        elif ataque_info['type'] == 'boost':
                            sons_sfx['xlr8_x'].play()
                            jogador.state = 'boost_xlr8'
                            jogador.speed = PLAYER_SPEED_BASE * jogador.speed_mult * ALIEN_DATA['XLR8']['stats']['speed_mult'] * ataque_info['speed_mult']
                            jogador.invencivel_fim = agora + ataque_info['duration']
                        
                        elif ataque_info['type'] == 'supernova':
                            sons_sfx['chama_x'].play()
                            camera_shake_fim = agora + CAMERA_SHAKE_DURATION
                            ataques_ativos.append({'rect': jogador.rect.inflate(ataque_info['radius']*2, ataque_info['radius']*2), 'end_time': agora + ataque_info['duration'], 'type': 'explosion', 'damage': ataque_info['damage'], 'visual': 'circle', 'color': ataque_info['color'], 'hit_enemies': {}})
                        
                        elif ataque_info['type'] == 'crystal_field' and ataque_diamante_image:
                            sons_sfx['diamante_x'].play()
                            camera_shake_fim = agora + int(CAMERA_SHAKE_DURATION / 2)
                            for i in range(ataque_info['num_crystals']):
                                angle = (360 / ataque_info['num_crystals']) * i
                                offset = pygame.math.Vector2(ataque_info['spawn_radius'], 0).rotate(angle)
                                initial_pos = jogador.rect.center + offset
                                ataque_rect = ataque_diamante_image.get_rect(center=initial_pos)
                                ataques_ativos.append({'rect': ataque_rect, 'end_time': agora + ataque_info['duration'], 'type': 'crystal_field_piece', 'damage': ataque_info['damage'], 'visual': 'image', 'image': ataque_diamante_image, 'hit_enemies': {}, 'start_time': agora, 'spawn_radius': ataque_info['spawn_radius'], 'angle_offset': angle, 'rot_speed': ataque_info['rotation_speed']})

                if evento.key == pygame.K_LSHIFT and agora > cooldowns['dash']:
                    if jogador.state == 'normal':
                        cooldowns['dash'] = agora + DASH_COOLDOWN
                        jogador.state = 'electric_dash'
                        jogador.invencivel_fim = agora + DASH_INVENCIBILITY_DURATION
                        jogador.target_pos = jogador.rect.center + jogador.direction_vec * 200
                        sons_sfx['dash_eletrico_sfx'].play()
                        criar_particulas(jogador.rect.center, 20, COLORS['AZUL'], 5, 20, 5)

                if evento.key == pygame.K_RETURN:
                    jogador.change_form(ALL_FORMS[current_selection_index])
                if evento.key == pygame.K_COMMA:
                    current_selection_index = (current_selection_index - 1) % len(ALL_FORMS)
                    sons_sfx['selecao_alien'].play()
                if evento.key == pygame.K_PERIOD:
                    current_selection_index = (current_selection_index + 1) % len(ALL_FORMS)
                    sons_sfx['selecao_alien'].play()

    if estado_jogo == 'jogando':
        if agora - ultimo_spawn_tempo > ENEMY_SPAWN_INTERVAL:
            ultimo_spawn_tempo = agora
            possible_spawns = ['cavaleiro_n1']
            if inimigos_mortos_contador > KILL_COUNT_WAVE_2: possible_spawns.append('cavaleiro_n2')
            tipo_inimigo = random.choice(possible_spawns)
            dados_inimigo = ENEMY_DATA[tipo_inimigo]
            spawn_margin = 50
            lado = random.choice(['top', 'bottom', 'left', 'right'])
            if lado == 'top': x, y = random.randint(camera_rect.left, camera_rect.right), camera_rect.top - spawn_margin
            elif lado == 'bottom': x, y = random.randint(camera_rect.left, camera_rect.right), camera_rect.bottom + spawn_margin
            elif lado == 'left': x, y = camera_rect.left - spawn_margin, random.randint(camera_rect.top, camera_rect.bottom)
            else: x, y = camera_rect.right + spawn_margin, random.randint(camera_rect.top, camera_rect.bottom)
            inimigos.append({'rect': pygame.Rect(x, y, dados_inimigo['size'][0], dados_inimigo['size'][1]),'health': dados_inimigo['health'], 'max_health': dados_inimigo['health'],'speed': dados_inimigo['speed'], 'type': tipo_inimigo, 'hit_flash_timer': 0})
        
        if agora - ultimo_spawn_bau > BAU_SPAWN_INTERVAL:
            ultimo_spawn_bau = agora
            x = random.randint(100, largura_mundo - 100)
            y = random.randint(100, altura_mundo - 100)
            baus_magicos.append({'rect': pygame.Rect(x, y, BAU_SIZE[0], BAU_SIZE[1]), 'health': BAU_HEALTH, 'max_health': BAU_HEALTH, 'hit_flash_timer': 0})

        for orbe in orbes_vida[:]:
            if jogador.rect.colliderect(orbe):
                orbes_vida.remove(orbe)
                jogador.health = min(jogador.max_health, jogador.health + 1)

        for p in particulas[:]:
            p['pos'] += p['vel']
            p['lifetime'] -= 1
            p['radius'] -= 0.2
            if p['lifetime'] <= 0 or p['radius'] <= 0: particulas.remove(p)
        
        if jogador.state in ['normal', 'boost_xlr8']:
            keys = pygame.key.get_pressed()
            mov_vec = pygame.math.Vector2(0, 0)
            if keys[pygame.K_LEFT]: mov_vec.x -= 1
            if keys[pygame.K_RIGHT]: mov_vec.x += 1
            if keys[pygame.K_UP]: mov_vec.y -= 1
            if keys[pygame.K_DOWN]: mov_vec.y += 1
            if mov_vec.length() > 0:
                mov_vec.normalize_ip()
                jogador.direction_vec = mov_vec.copy()
                jogador.rect.move_ip(mov_vec * jogador.speed)
            if jogador.state == 'boost_xlr8' and agora > jogador.invencivel_fim:
                jogador.state = 'normal'
                jogador.update_stats_for_alien()
        
        elif jogador.state == 'super_pulo_saltando':
            ataque_info = ALIEN_DATA['Quatro Braços']['ataque_x']
            jump_speed = ataque_info['jump_speed']
            direcao_pulo = jogador.target_pos - pygame.math.Vector2(jogador.rect.center)
            if direcao_pulo.length() < jump_speed:
                jogador.state = 'normal'
                sons_sfx['4bracos_x'].play()
                camera_shake_fim = agora + CAMERA_SHAKE_DURATION
                criar_particulas(jogador.rect.center, 30, COLORS['CINZA'], 4, 20, 8)
                ataques_ativos.append({'rect': pygame.Rect(0,0,ataque_info['damage_radius']*2, ataque_info['damage_radius']*2), 'end_time': agora + ataque_info['damage_duration'], 'type': 'explosion', 'damage': ataque_info['damage'], 'visual': 'circle', 'color': ataque_info['color'], 'hit_enemies': {}})
                ataques_ativos[-1]['rect'].center = jogador.rect.center
            else:
                direcao_pulo.normalize_ip()
                jogador.rect.move_ip(direcao_pulo * jump_speed)

        elif jogador.state == 'electric_dash':
            direcao_dash = jogador.target_pos - pygame.math.Vector2(jogador.rect.center)
            if direcao_dash.length() < DASH_SPEED:
                jogador.rect.center = jogador.target_pos
                jogador.state = 'normal'
            else:
                direcao_dash.normalize_ip()
                jogador.rect.move_ip(direcao_dash * DASH_SPEED)
                if agora % 2 == 0:
                    criar_particulas(jogador.rect.center, 1, COLORS['CYA'], 1, 15, 3)

        jogador.rect.clamp_ip(mundo_rect)

        if jogador.active_alien_name != 'Ben':
            jogador.omnitrix_energy -= OMNITRIX_DRAIN_RATE * (1/FPS)
            if jogador.omnitrix_energy <= 0:
                jogador.omnitrix_energy = 0
                jogador.change_form('Ben')
        else:
            jogador.omnitrix_energy = min(OMNITRIX_MAX_ENERGY, jogador.omnitrix_energy + OMNITRIX_RECHARGE_RATE * (1/FPS))

        for inimigo in inimigos[:]:
            direcao_para_player = pygame.math.Vector2(jogador.rect.center) - pygame.math.Vector2(inimigo['rect'].center)
            if direcao_para_player.length() > 0:
                direcao_para_player.normalize_ip()
                inimigo['rect'].move_ip(direcao_para_player * inimigo['speed'])
            if jogador.rect.colliderect(inimigo['rect']):
                if jogador.state == 'boost_xlr8':
                    dano = ALIEN_DATA['XLR8']['ataque_x']['contact_damage']
                    inimigo['health'] -= dano
                    criar_texto_flutuante(str(dano), inimigo['rect'].center, COLORS['AMARELO'])
                    criar_particulas(inimigo['rect'].center, 20, COLORS['AMARELO'], 4, 20, 6)
                elif agora > jogador.invencivel_fim:
                    jogador.health -= ENEMY_DAMAGE
                    flash_dano_fim = agora + 200
                    jogador.invencivel_fim = agora + PLAYER_INVENCIVEL_DURATION
                    if inimigo in inimigos: inimigos.remove(inimigo)
                    if jogador.health <= 0:
                        jogador.health = 0
                        estado_jogo = 'game_over'
                        pygame.mixer.music.fadeout(2000)

        for ataque in ataques_ativos[:]:
            if ataque.get('speed', 0) > 0:
                ataque['rect'].move_ip(ataque['dir_vec'] * ataque['speed'])
            elif ataque['type'] == 'shockwave' and ataque['end_time'] > ataque['start_time']:
                progress = (agora - ataque['start_time']) / (ataque['end_time'] - ataque['start_time'])
                ataque['current_radius'] = ataque['start_radius'] + (ataque['max_radius'] - ataque['start_radius']) * progress
                ataque['rect'] = pygame.Rect(0,0, int(ataque['current_radius'] * 2), int(ataque['current_radius'] * 2))
                ataque['rect'].center = ataque['center']
            elif ataque['type'] == 'crystal_field_piece':
                time_elapsed = agora - ataque['start_time']
                current_angle = ataque['angle_offset'] + (time_elapsed * ataque['rot_speed'] / 100)
                offset = pygame.math.Vector2(ataque['spawn_radius'], 0).rotate(current_angle)
                ataque['rect'].center = jogador.rect.center + offset
                ataque['angle'] = current_angle
            
            # CORREÇÃO: Pular a lógica de colisão para ataques que não têm 'rect'
            if 'rect' not in ataque:
                if agora > ataque.get('end_time', 0):
                    if ataque in ataques_ativos: ataques_ativos.remove(ataque)
                continue
            
            for inimigo in inimigos[:]:
                if id(inimigo) in ataque.get('hit_enemies', {}): continue
                colidiu = ataque['rect'].colliderect(inimigo['rect'])
                if colidiu:
                    dano_causado = ataque.get('damage', 0) + jogador.base_damage
                    if dano_causado > 0:
                        inimigo['health'] -= dano_causado
                        inimigo['hit_flash_timer'] = 5
                        criar_texto_flutuante(str(int(dano_causado)), inimigo['rect'].center, COLORS['BRANCO'])
                    
                    if ataque.get('type') == 'ground_smash':
                        knockback_vec = (pygame.math.Vector2(inimigo['rect'].center) - pygame.math.Vector2(jogador.rect.center)).normalize()
                        inimigo['rect'].move_ip(knockback_vec * ataque['knockback'])
                    
                    ataque['hit_enemies'][id(inimigo)] = agora + 200
                    if inimigo['health'] <= 0:
                        if jogador.add_xp(XP_PER_KILL.get(inimigo['type'], 10)):
                            estado_jogo = 'level_up'
                            opcoes_disponiveis = list(UPGRADE_OPTIONS.keys())
                            random.shuffle(opcoes_disponiveis)
                            upgrade_choices = [UPGRADE_OPTIONS[key] for key in opcoes_disponiveis[:3]]
                        if random.random() < ORBE_VIDA_CHANCE: orbes_vida.append(inimigo['rect'].copy())
                        if inimigo in inimigos: inimigos.remove(inimigo)
                        inimigos_mortos_contador += 1
                    
                    if ataque['type'] == 'chama_projétil':
                        info = ALIEN_DATA['Chama']['ataque_z']
                        explosao_rect = pygame.Rect(0,0,info['explosion_radius']*2, info['explosion_radius']*2)
                        explosao_rect.center = inimigo['rect'].center
                        ataques_ativos.append({'rect': explosao_rect, 'end_time': agora + info['explosion_duration'], 'type': 'explosion', 'damage': info['damage'], 'visual': 'circle', 'color': info['color'], 'hit_enemies': {}})
                        if ataque in ataques_ativos: ataques_ativos.remove(ataque)
                        break
            
            for bau in baus_magicos[:]:
                if ataque['rect'].colliderect(bau['rect']):
                    bau['health'] -= ataque.get('damage', 1) + jogador.base_damage
                    bau['hit_flash_timer'] = 5
                    if bau['health'] <= 0:
                        baus_magicos.remove(bau)
                        for _ in range(3):
                            orbe_rect = bau['rect'].copy()
                            orbe_rect.x += random.randint(-15, 15)
                            orbe_rect.y += random.randint(-15, 15)
                            orbes_vida.append(orbe_rect)
                    if ataque in ataques_ativos and ataque['type'] not in ['crystal_field_piece']:
                         ataques_ativos.remove(ataque)
                    break
            
            if agora > ataque.get('end_time', 0):
                if ataque in ataques_ativos: ataques_ativos.remove(ataque)

        camera_rect.center = pygame.math.Vector2(camera_rect.center).lerp(jogador.rect.center, 0.1)
        
        if agora < camera_shake_fim:
            offset_x = random.randint(-CAMERA_SHAKE_INTENSITY, CAMERA_SHAKE_INTENSITY)
            offset_y = random.randint(-CAMERA_SHAKE_INTENSITY, CAMERA_SHAKE_INTENSITY)
            camera_rect.move_ip(offset_x, offset_y)
        camera_rect.clamp_ip(mundo_rect)
        
        inimigos_proximos = any(pygame.math.Vector2(jogador.rect.center).distance_to(i['rect'].center) < RAIO_COMBATE for i in inimigos)
        if inimigos_mortos_contador >= KILL_COUNT_FASE_2: tocar_musica('second_phase_melody_alt.ogg')
        elif inimigos_proximos: tocar_musica('first_phase_melody.ogg')
        else: tocar_musica('suspense.ogg')

    if estado_jogo == 'tela_inicial':
        tocar_musica('intro.ogg')
        for y in range(0, altura_tela, 20):
            ratio = y / altura_tela
            cor = (int(COLORS['ROXO_FUNDO1'][0] * (1 - ratio) + COLORS['ROXO_FUNDO2'][0] * ratio),
                int(COLORS['ROXO_FUNDO1'][1] * (1 - ratio) + COLORS['ROXO_FUNDO2'][1] * ratio),
                int(COLORS['ROXO_FUNDO1'][2] * (1 - ratio) + COLORS['ROXO_FUNDO2'][2] * ratio))
            pygame.draw.rect(tela, cor, (0, y, largura_tela, 20))
        titulo_surface = title_font.render(GAME_TITLE, True, COLORS['BRANCO'])
        instrucao_surface = ui_font.render("Pressione ENTER para começar", True, COLORS['BRANCO'])
        tela.blit(titulo_surface, titulo_surface.get_rect(center=(largura_tela / 2, altura_tela / 2 - 50)))
        tela.blit(instrucao_surface, instrucao_surface.get_rect(center=(largura_tela / 2, altura_tela / 2 + 50)))
    
    elif estado_jogo in ['jogando', 'game_over', 'level_up']:
        draw_elements()

    if estado_jogo == 'game_over':
        overlay = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        tela.blit(overlay, (0,0))
        game_over_surface = title_font.render("GAME OVER", True, COLORS['VERMELHO_VIDA'])
        score_surface = ui_font.render(f"Inimigos Derrotados: {inimigos_mortos_contador}", True, COLORS['BRANCO'])
        restart_surface = ui_font.render("Pressione 'R' para reiniciar", True, COLORS['BRANCO'])
        tela.blit(game_over_surface, game_over_surface.get_rect(center=(largura_tela / 2, altura_tela / 2 - 60)))
        tela.blit(score_surface, score_surface.get_rect(center=(largura_tela / 2, altura_tela / 2 + 10)))
        tela.blit(restart_surface, restart_surface.get_rect(center=(largura_tela / 2, altura_tela / 2 + 50)))

    pygame.display.flip()

pygame.quit()