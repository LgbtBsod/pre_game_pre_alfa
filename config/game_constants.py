"""Константы и настройки игры.
Использует единые настройки из unified_settings для устранения дублирования.
"""

from config.unified_settings import (
    get_window_settings, get_map_settings, get_player_settings, get_enemy_settings,
    get_combat_settings, get_leveling_settings, get_ai_settings, get_movement_settings,
    get_fps_settings, get_audio_settings, get_gameplay_settings, get_ui_settings,
    get_inventory_settings, get_effect_settings, get_skill_settings, get_loot_settings
)

# Размеры окна по умолчанию (из unified_settings)
WINDOW_WIDTH = get_window_settings().WIDTH
WINDOW_HEIGHT = get_window_settings().HEIGHT
WIDTH = get_window_settings().WIDTH  # Для обратной совместимости
HEIGHT = get_window_settings().HEIGHT  # Для обратной совместимости
DEFAULT_WINDOW_WIDTH = get_window_settings().DEFAULT_WIDTH
DEFAULT_WINDOW_HEIGHT = get_window_settings().DEFAULT_HEIGHT

# Настройки карты (из unified_settings)
MAP_TILE_SIZE = get_map_settings().TILE_SIZE
TILE_SIZE = get_map_settings().TILE_SIZE  # Для обратной совместимости
MAP_WIDTH = get_map_settings().MAP_WIDTH
MAP_HEIGHT = get_map_settings().MAP_HEIGHT

# Настройки игрока (из unified_settings)
PLAYER_START_HEALTH = get_player_settings().START_HEALTH
PLAYER_BASE_HEALTH = get_player_settings().START_HEALTH  # Для обратной совместимости
PLAYER_START_MANA = get_player_settings().START_MANA
PLAYER_START_STAMINA = get_player_settings().START_STAMINA
PLAYER_MOVEMENT_SPEED = get_player_settings().MOVEMENT_SPEED
PLAYER_ATTACK_SPEED = get_player_settings().ATTACK_SPEED

# Настройки врагов (из unified_settings)
ENEMY_BASE_HEALTH = get_enemy_settings().BASE_HEALTH
ENEMY_BASE_MANA = get_enemy_settings().BASE_MANA
ENEMY_BASE_STAMINA = get_enemy_settings().BASE_STAMINA
ENEMY_MOVEMENT_SPEED = get_enemy_settings().MOVEMENT_SPEED
ENEMY_ATTACK_SPEED = get_enemy_settings().ATTACK_SPEED

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

# Настройки боя (из unified_settings)
ATTACK_RANGE = get_combat_settings().ATTACK_RANGE_BASE
CRITICAL_CHANCE_BASE = get_combat_settings().CRITICAL_CHANCE_BASE
CRITICAL_MULTIPLIER_BASE = get_combat_settings().CRITICAL_MULTIPLIER_BASE
CRITICAL_MULTIPLIER = get_combat_settings().CRITICAL_MULTIPLIER_BASE  # Для обратной совместимости
DAMAGE_REDUCTION_BASE = get_combat_settings().DAMAGE_REDUCTION_BASE
BASE_DAMAGE = get_combat_settings().BASE_DAMAGE  # Базовый урон

# Настройки опыта и уровней (из unified_settings)
XP_BASE = get_leveling_settings().XP_BASE
XP_MULTIPLIER = get_leveling_settings().XP_MULTIPLIER
LEVEL_CAP = get_leveling_settings().LEVEL_CAP

# Настройки ИИ (из unified_settings)
AI_UPDATE_FREQUENCY = get_ai_settings().AI_UPDATE_FREQUENCY  # секунды
AI_DECISION_DELAY = get_ai_settings().DECISION_DELAY
AI_MEMORY_DURATION = get_ai_settings().MEMORY_DURATION

# Настройки физики (из unified_settings)
GRAVITY = get_movement_settings().GRAVITY
FRICTION = get_movement_settings().FRICTION
COLLISION_TOLERANCE = get_movement_settings().COLLISION_TOLERANCE

# Настройки рендеринга (из unified_settings)
RENDER_FPS = get_fps_settings().RENDER_FPS
UPDATE_FPS = get_fps_settings().UPDATE_FPS
CAMERA_SMOOTHING = get_map_settings().CAMERA_SMOOTHING

# Настройки звука (из unified_settings)
SOUND_ENABLED = get_audio_settings().SOUND_ENABLED
MUSIC_ENABLED = get_audio_settings().MUSIC_ENABLED
SOUND_VOLUME = get_audio_settings().SFX_VOLUME
MUSIC_VOLUME = get_audio_settings().MUSIC_VOLUME

# Настройки сохранения (из unified_settings)
AUTO_SAVE_INTERVAL = get_gameplay_settings().AUTO_SAVE_INTERVAL  # секунды
MAX_SAVE_SLOTS = get_gameplay_settings().MAX_SAVE_SLOTS
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

# Цвета (из unified_settings)
COLORS = {
    "player": "#00ff00",
    "enemy": "#ff0000",
    "boss": "#ff00ff",
    "npc": "#0000ff",
    "item": "#ffff00",
    "projectile": "#ff8800",
    "effect": "#00ffff",
    "ui_background": "#1a1a1a",
    "ui_text": "#ffffff",
    "ui_button": "#444444",
    "ui_button_hover": "#666666"
}

# Основные цвета (из unified_settings)
BACKGROUND = (0, 0, 0)  # Черный фон
PLAYER_COLOR = (0, 255, 0)  # Зеленый цвет игрока
TEXT_COLOR = (255, 255, 255)  # Белый цвет текста

# Размеры UI элементов (из unified_settings)
UI_ELEMENT_HEIGHT = get_ui_settings().ELEMENT_HEIGHT
UI_PADDING = get_ui_settings().PADDING
UI_MARGIN = get_ui_settings().MARGIN
UI_FONT_SIZE = get_ui_settings().FONT_SIZE

# Настройки инвентаря (из unified_settings)
INVENTORY_SLOTS = get_inventory_settings().SLOTS
EQUIPMENT_SLOTS = get_inventory_settings().EQUIPMENT_SLOTS
STACK_SIZE_LIMIT = get_inventory_settings().STACK_SIZE_LIMIT

# Настройки эффектов (из unified_settings)
EFFECT_DURATION_BASE = get_effect_settings().DURATION_BASE
EFFECT_TICK_RATE = get_effect_settings().TICK_RATE
MAX_ACTIVE_EFFECTS = get_effect_settings().MAX_ACTIVE_EFFECTS

# Настройки способностей (из unified_settings)
SKILL_COOLDOWN_BASE = get_skill_settings().COOLDOWN_BASE
SKILL_MANA_COST_BASE = get_skill_settings().MANA_COST_BASE
SKILL_STAMINA_COST_BASE = get_skill_settings().STAMINA_COST_BASE

# Настройки лута (из unified_settings)
LOOT_DROP_CHANCE_BASE = get_loot_settings().DROP_CHANCE_BASE
LOOT_QUALITY_BASE = get_loot_settings().QUALITY_BASE
RARE_ITEM_CHANCE = get_loot_settings().RARE_ITEM_CHANCE
EPIC_ITEM_CHANCE = get_loot_settings().EPIC_ITEM_CHANCE
LEGENDARY_ITEM_CHANCE = get_loot_settings().LEGENDARY_ITEM_CHANCE
