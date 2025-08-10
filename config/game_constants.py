"""Константы и настройки игры.
Использует единые настройки из unified_settings для устранения дублирования.
"""

from config.unified_settings import UnifiedSettings

# Размеры окна по умолчанию (из unified_settings)
WINDOW_WIDTH = UnifiedSettings.WINDOW_WIDTH
WINDOW_HEIGHT = UnifiedSettings.WINDOW_HEIGHT
WIDTH = UnifiedSettings.WINDOW_WIDTH  # Для обратной совместимости
HEIGHT = UnifiedSettings.WINDOW_HEIGHT  # Для обратной совместимости
DEFAULT_WINDOW_WIDTH = UnifiedSettings.DEFAULT_WINDOW_WIDTH
DEFAULT_WINDOW_HEIGHT = UnifiedSettings.DEFAULT_WINDOW_HEIGHT

# Настройки карты (из unified_settings)
MAP_TILE_SIZE = UnifiedSettings.TILE_SIZE
TILE_SIZE = UnifiedSettings.TILE_SIZE  # Для обратной совместимости
MAP_WIDTH = UnifiedSettings.MAP_WIDTH
MAP_HEIGHT = UnifiedSettings.MAP_HEIGHT

# Настройки игрока (из unified_settings)
PLAYER_START_HEALTH = UnifiedSettings.BASE_HEALTH
PLAYER_BASE_HEALTH = UnifiedSettings.BASE_HEALTH  # Для обратной совместимости
PLAYER_START_MANA = 50
PLAYER_START_STAMINA = 100
PLAYER_MOVEMENT_SPEED = 2.0
PLAYER_ATTACK_SPEED = 1.0

# Настройки врагов (из unified_settings)
ENEMY_BASE_HEALTH = UnifiedSettings.BASE_HEALTH * 0.8
ENEMY_BASE_MANA = 30
ENEMY_BASE_STAMINA = 80
ENEMY_MOVEMENT_SPEED = 1.8
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

# Настройки боя (из unified_settings)
ATTACK_RANGE = UnifiedSettings.ATTACK_RANGE_BASE
CRITICAL_CHANCE_BASE = UnifiedSettings.CRITICAL_CHANCE_BASE
CRITICAL_MULTIPLIER_BASE = UnifiedSettings.CRITICAL_MULTIPLIER_BASE
CRITICAL_MULTIPLIER = (
    UnifiedSettings.CRITICAL_MULTIPLIER_BASE
)  # Для обратной совместимости
DAMAGE_REDUCTION_BASE = 0.1
BASE_DAMAGE = UnifiedSettings.BASE_DAMAGE  # Базовый урон

# Настройки опыта и уровней (из unified_settings)
XP_BASE = 100
XP_MULTIPLIER = 1.5
LEVEL_CAP = 100

# Настройки ИИ (из unified_settings)
AI_UPDATE_FREQUENCY = 0.1  # секунды
AI_DECISION_DELAY = 0.5
AI_MEMORY_DURATION = 30.0

# Настройки физики (из unified_settings)
GRAVITY = 0.0
FRICTION = 0.8
COLLISION_TOLERANCE = 2.0

# Настройки рендеринга (из unified_settings)
RENDER_FPS = UnifiedSettings.RENDER_FPS
UPDATE_FPS = UnifiedSettings.UPDATE_FPS
CAMERA_SMOOTHING = 0.1

# Настройки звука (из unified_settings)
SOUND_ENABLED = True
MUSIC_ENABLED = True
SOUND_VOLUME = 1.0
MUSIC_VOLUME = 0.8

# Настройки сохранения (из unified_settings)
AUTO_SAVE_INTERVAL = 300  # секунды
MAX_SAVE_SLOTS = 10
SAVE_FILE_EXTENSION = ".sav"

# Цветовые константы (из unified_settings)
BACKGROUND = UnifiedSettings.BACKGROUND
PLAYER_COLOR = UnifiedSettings.PLAYER_COLOR
ENEMY_COLOR = UnifiedSettings.ENEMY_COLOR
TEXT_COLOR = UnifiedSettings.TEXT_COLOR
UI_BACKGROUND = UnifiedSettings.BACKGROUND_DARK
UI_BORDER = UnifiedSettings.BUTTON_COLOR
UI_HIGHLIGHT = UnifiedSettings.BUTTON_HOVER_COLOR

# Цвета здоровья
HEALTH_FULL = UnifiedSettings.HEALTH_COLOR
HEALTH_MEDIUM = UnifiedSettings.HEALTH_LOW_COLOR
HEALTH_LOW = UnifiedSettings.HEALTH_CRITICAL_COLOR

# Цвета эффектов (используем базовые цвета)
DAMAGE_COLOR = (255, 0, 0)
HEAL_COLOR = (0, 255, 0)
BUFF_COLOR = (0, 255, 255)
DEBUFF_COLOR = (255, 0, 255)

# Настройки инвентаря
INVENTORY_SLOTS = 20
EQUIPMENT_SLOTS = 8
STACK_SIZE_LIMIT = 99
WEIGHT_LIMIT_ENABLED = True
BASE_WEIGHT_LIMIT = 100.0

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

# Системные настройки
LOG_LEVEL = UnifiedSettings.LOG_LEVEL
LOG_FORMAT = UnifiedSettings.LOG_FORMAT

# Настройки базы данных
DB_FILE = UnifiedSettings.GAME_DATA_FILE
DB_BACKUP_INTERVAL = UnifiedSettings.BACKUP_INTERVAL

# Настройки производительности
MAX_ENTITIES = 1000
MAX_EFFECTS = 500
CLEANUP_INTERVAL = 60
