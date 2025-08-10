"""Константы и настройки игры."""

# Размеры окна по умолчанию
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WIDTH = 1200  # Для обратной совместимости
HEIGHT = 800  # Для обратной совместимости
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800

# Настройки карты
MAP_TILE_SIZE = 32
TILE_SIZE = 32  # Для обратной совместимости
MAP_WIDTH = 50
MAP_HEIGHT = 50

# Настройки игрока
PLAYER_START_HEALTH = 100
PLAYER_BASE_HEALTH = 100  # Для обратной совместимости
PLAYER_START_MANA = 50
PLAYER_START_STAMINA = 100
PLAYER_MOVEMENT_SPEED = 150
PLAYER_ATTACK_SPEED = 1.0

# Настройки врагов
ENEMY_BASE_HEALTH = 80
ENEMY_BASE_MANA = 30
ENEMY_BASE_STAMINA = 80
ENEMY_MOVEMENT_SPEED = 100
ENEMY_ATTACK_SPEED = 0.8

# Количество и уровни врагов по сложности
ENEMY_COUNT_EASY = 3
ENEMY_COUNT_NORMAL = 5
ENEMY_COUNT_HARD = 7

ENEMY_LEVEL_MIN_EASY = 1
ENEMY_LEVEL_MAX_EASY = 3
ENEMY_LEVEL_MIN_NORMAL = 2
ENEMY_LEVEL_MAX_NORMAL = 5
ENEMY_LEVEL_MIN_HARD = 3
ENEMY_LEVEL_MAX_HARD = 8

# Настройки боссов
BOSS_HEALTH_MULTIPLIER = 5.0
BOSS_DAMAGE_MULTIPLIER = 2.0
BOSS_SPEED_MULTIPLIER = 0.7

# Уровни боссов по сложности
BOSS_LEVEL_EASY = 5
BOSS_LEVEL_NORMAL = 10
BOSS_LEVEL_HARD = 15

# Настройки боя
ATTACK_RANGE = 50
CRITICAL_CHANCE_BASE = 0.05
CRITICAL_MULTIPLIER_BASE = 2.0
CRITICAL_MULTIPLIER = 2.0  # Для обратной совместимости
DAMAGE_REDUCTION_BASE = 0.1
BASE_DAMAGE = 10  # Базовый урон

# Настройки опыта и уровней
XP_BASE = 100
XP_MULTIPLIER = 1.5
LEVEL_CAP = 100

# Настройки ИИ
AI_UPDATE_FREQUENCY = 0.1  # секунды
AI_DECISION_DELAY = 0.5
AI_MEMORY_DURATION = 30.0

# Настройки физики
GRAVITY = 0.0
FRICTION = 0.8
COLLISION_TOLERANCE = 2.0

# Настройки рендеринга
RENDER_FPS = 60
UPDATE_FPS = 120
CAMERA_SMOOTHING = 0.1

# Настройки звука
SOUND_ENABLED = True
MUSIC_ENABLED = True
SOUND_VOLUME = 0.7
MUSIC_VOLUME = 0.5

# Настройки сохранения
AUTO_SAVE_INTERVAL = 300  # секунды
MAX_SAVE_SLOTS = 10
SAVE_FILE_EXTENSION = ".sav"

# Настройки сложности
DIFFICULTY_SETTINGS = {
    "easy": {
        "enemy_health_multiplier": 0.8,
        "enemy_damage_multiplier": 0.7,
        "player_health_multiplier": 1.2,
        "player_damage_multiplier": 1.1,
        "xp_multiplier": 1.3
    },
    "normal": {
        "enemy_health_multiplier": 1.0,
        "enemy_damage_multiplier": 1.0,
        "player_health_multiplier": 1.0,
        "player_damage_multiplier": 1.0,
        "xp_multiplier": 1.0
    },
    "hard": {
        "enemy_health_multiplier": 1.3,
        "enemy_damage_multiplier": 1.4,
        "player_health_multiplier": 0.9,
        "player_damage_multiplier": 0.9,
        "xp_multiplier": 0.8
    }
}

# Цвета
COLORS = {
    "player": "#00ff00",
    "enemy": "#ff0000",
    "boss": "#ff00ff",
    "npc": "#0000ff",
    "item": "#ffff00",
    "projectile": "#ff8800",
    "effect": "#00ffff",
    "ui_background": "#000000",
    "ui_text": "#ffffff",
    "ui_button": "#444444",
    "ui_button_hover": "#666666"
}

# Основные цвета
BACKGROUND = (0, 0, 0)  # Черный фон
PLAYER_COLOR = (0, 255, 0)  # Зеленый цвет игрока
TEXT_COLOR = (255, 255, 255)  # Белый цвет текста

# Размеры UI элементов
UI_ELEMENT_HEIGHT = 30
UI_PADDING = 10
UI_MARGIN = 5
UI_FONT_SIZE = 14

# Настройки инвентаря
INVENTORY_SLOTS = 20
EQUIPMENT_SLOTS = 8
STACK_SIZE_LIMIT = 99

# Настройки эффектов
EFFECT_DURATION_BASE = 10.0
EFFECT_TICK_RATE = 1.0
MAX_ACTIVE_EFFECTS = 20

# Настройки способностей
SKILL_COOLDOWN_BASE = 1.0
SKILL_MANA_COST_BASE = 10
SKILL_STAMINA_COST_BASE = 15

# Настройки лута
LOOT_DROP_CHANCE_BASE = 0.3
LOOT_QUALITY_BASE = 1.0
RARE_ITEM_CHANCE = 0.1
EPIC_ITEM_CHANCE = 0.05
LEGENDARY_ITEM_CHANCE = 0.01
