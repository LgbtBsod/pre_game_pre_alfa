"""
Game constants and configuration values
"""

# Display constants
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
FPS = 60

# Tile constants
TILESIZE = 64
HITBOX_OFFSET = {
    'player': 6,
    'object': -10,
    'grass': -10,
    'invisible': 0
}

# Player constants
PLAYER_SPEED = 5
PLAYER_HEALTH = 100
PLAYER_ENERGY = 60
PLAYER_ATTACK = 10
PLAYER_MAGIC = 4

# Weapon constants
WEAPON_DATA = {
    'sword': {'cooldown': 400, 'damage': 10},
    'lance': {'cooldown': 350, 'damage': 15},
    'axe': {'cooldown': 500, 'damage': 20},
    'rapier': {'cooldown': 300, 'damage': 8},
    'sai': {'cooldown': 400, 'damage': 12}
}

# Magic constants
MAGIC_DATA = {
    'heal': {'cost': 20, 'strength': 20},
    'flame': {'cost': 16, 'strength': 15},
    'claw': {'cost': 12, 'strength': 10},
    'thunder': {'cost': 23, 'strength': 25}
}

# Enemy constants
ENEMY_DATA = {
    'bamboo': {
        'health': 70,
        'exp': 120,
        'damage': 6,
        'attack_type': 'leaf_attack',
        'attack_sound': 'audio/attack/slash.wav',
        'speed': 3,
        'resistance': 3,
        'attack_radius': 50,
        'notice_radius': 300
    },
    'raccoon': {
        'health': 300,
        'exp': 250,
        'damage': 40,
        'attack_type': 'claw',
        'attack_sound': 'audio/attack/claw.wav',
        'speed': 2,
        'resistance': 3,
        'attack_radius': 120,
        'notice_radius': 400
    },
    'squid': {
        'health': 100,
        'exp': 100,
        'damage': 20,
        'attack_type': 'slash',
        'attack_sound': 'audio/attack/slash.wav',
        'speed': 3,
        'resistance': 3,
        'attack_radius': 80,
        'notice_radius': 360
    },
    'spirit': {
        'health': 100,
        'exp': 110,
        'damage': 8,
        'attack_type': 'thunder',
        'attack_sound': 'audio/attack/fireball.wav',
        'speed': 4,
        'resistance': 3,
        'attack_radius': 60,
        'notice_radius': 350
    }
}

# UI constants
UI_FONT_SIZE = 18
UI_PADDING = 10
UI_BAR_HEIGHT = 20
UI_BAR_WIDTH = 200

# Audio constants
MUSIC_VOLUME = 0.4
SFX_VOLUME = 0.7

# Animation constants
ANIMATION_SPEED = 0.15
PARTICLE_LIFETIME = 400

# Game states
class GameStates:
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"

# Input actions
class InputActions:
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    ATTACK = "attack"
    USE_MAGIC = "use_magic"
    SWITCH_WEAPON = "switch_weapon"
    SWITCH_MAGIC = "switch_magic"
    PAUSE = "pause"
    QUICK_SAVE = "quick_save"
    QUICK_LOAD = "quick_load"
    INTERACT = "interact"

# Resource types
class ResourceTypes:
    IMAGE = "image"
    SOUND = "sound"
    MUSIC = "music"
    FONT = "font"
    DATA = "data"

# File paths
class Paths:
    GRAPHICS = "graphics/"
    AUDIO = "audio/"
    MAPS = "map/"
    SAVES = "save/"
    FONTS = "graphics/font/"
    
    # Specific asset paths
    PLAYER_SPRITES = "graphics/player/"
    ENEMY_SPRITES = "graphics/monsters/"
    WEAPON_SPRITES = "graphics/weapons/"
    PARTICLE_SPRITES = "graphics/particles/"
    TILEMAP_SPRITES = "graphics/tilemap/"
    OBJECT_SPRITES = "graphics/objects/"
    GRASS_SPRITES = "graphics/grass/"
