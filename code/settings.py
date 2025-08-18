# Game settings and configuration

# Display settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TILESIZE = 64

# Player settings
PLAYER_SPEED = 5
PLAYER_HEALTH = 100
PLAYER_ENERGY = 60
PLAYER_ATTACK = 10
PLAYER_MAGIC = 4
PLAYER_SPEED_UPGRADE = 1
PLAYER_HEALTH_UPGRADE = 20
PLAYER_ENERGY_UPGRADE = 15
PLAYER_ATTACK_UPGRADE = 4
PLAYER_MAGIC_UPGRADE = 2

# Weapon settings
WEAPON_DATA = {
    'sword': {'cooldown': 100, 'damage': 15, 'graphic': 'graphics/weapons/sword/full.png'},
    'lance': {'cooldown': 400, 'damage': 30, 'graphic': 'graphics/weapons/lance/full.png'},
    'axe': {'cooldown': 300, 'damage': 20, 'graphic': 'graphics/weapons/axe/full.png'},
    'rapier': {'cooldown': 50, 'damage': 8, 'graphic': 'graphics/weapons/rapier/full.png'},
    'sai': {'cooldown': 80, 'damage': 10, 'graphic': 'graphics/weapons/sai/full.png'}
}

# Magic settings
MAGIC_DATA = {
    'flame': {'strength': 5, 'cost': 20, 'graphic': 'graphics/particles/flame/fire.png'},
    'heal': {'strength': 20, 'cost': 10, 'graphic': 'graphics/particles/heal/heal.png'}
}

# Monster settings
monster_data = {
    'squid': {'health': 100, 'exp': 100, 'damage': 20, 'attack_type': 'slash', 'attack_sound': 'audio/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 80, 'notice_radius': 360},
    'raccoon': {'health': 300, 'exp': 250, 'damage': 40, 'attack_type': 'claw', 'attack_sound': 'audio/claw.wav', 'speed': 2, 'resistance': 3, 'attack_radius': 120, 'notice_radius': 400},
    'spirit': {'health': 100, 'exp': 110, 'damage': 8, 'attack_type': 'thunder', 'attack_sound': 'audio/fireball.wav', 'speed': 4, 'resistance': 3, 'attack_radius': 60, 'notice_radius': 350},
    'bamboo': {'health': 70, 'exp': 120, 'damage': 6, 'attack_type': 'leaf_attack', 'attack_sound': 'audio/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 50, 'notice_radius': 300}
}

# UI settings
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
ITEM_BOX_SIZE = 80
UI_FONT_SIZE = 18
UI_FONT = 'graphics/font/joystix.ttf'

# General colors
WATER_COLOR = '#71ddee'
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'
HEALTH_COLOR = 'red'
ENERGY_COLOR = 'blue'
UI_BORDER_COLOR_ACTIVE = 'gold'

# Upgrade menu
TEXT_COLOR_SELECTED = '#111111'
BAR_COLOR = '#EEEEEE'
BAR_COLOR_SELECTED = '#111111'
UPGRADE_BG_COLOR_SELECTED = '#EEEEEE'

# Particles
ANIMATION_TYPES = ['leaf1', 'leaf2', 'leaf3', 'leaf4', 'leaf5', 'leaf6', 'leaf7', 'leaf8', 'leaf9', 'leaf10', 'leaf11', 'leaf12', 'leaf13', 'leaf14', 'leaf15', 'leaf16', 'leaf17', 'leaf18', 'leaf19', 'leaf20']

# Audio
MUSIC_VOLUME = 0.7
SFX_VOLUME = 0.8
