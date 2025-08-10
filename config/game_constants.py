"""
Константы игры.
Содержит базовые значения, которые могут быть переопределены в конфигурации.
Все константы теперь хранятся в JSON файлах согласно требованию.
"""

from .config_manager import config_manager

# Размеры окна
WINDOW_WIDTH = config_manager.get('game', 'display.window_width', 1280)
WINDOW_HEIGHT = config_manager.get('game', 'display.window_height', 720)

# Частота кадров
RENDER_FPS = config_manager.get('game', 'display.render_fps', 60)
UPDATE_FPS = config_manager.get('game', 'display.update_fps', 120)

# Размер шрифта
FONT_SIZE_NORMAL = config_manager.get('game', 'display.font_size', 16)

# Базовые параметры боя
ATTACK_RANGE_BASE = config_manager.get('game', 'combat.attack_range', 2.0)
BASE_DAMAGE = config_manager.get('game', 'combat.base_damage', 10.0)

# Физика
GRAVITY = config_manager.get('game', 'physics.gravity', 9.81)
FRICTION = config_manager.get('game', 'physics.friction', 0.8)

# AI параметры
LEARNING_RATE_BASE = config_manager.get('ai', 'core.learning_rate', 0.1)
MEMORY_DECAY_RATE_BASE = config_manager.get('ai', 'core.memory_decay_rate', 0.05)
PATTERN_RECOGNITION_THRESHOLD = config_manager.get('ai', 'pattern_recognition.similarity_threshold', 0.7)

# Размеры карты
MAP_TILE_SIZE = config_manager.get('game', 'map.tile_size', 32)
MAP_WIDTH = config_manager.get('game', 'map.width', 100)
MAP_HEIGHT = config_manager.get('game', 'map.height', 100)

# Базовые характеристики игрока
PLAYER_START_HEALTH = config_manager.get('game', 'player.start_health', 100.0)
PLAYER_START_MANA = config_manager.get('game', 'player.start_mana', 50.0)
PLAYER_START_STAMINA = config_manager.get('game', 'player.start_stamina', 100.0)

# Базовые характеристики врагов
ENEMY_BASE_HEALTH = config_manager.get('game', 'enemy.base_health', 50.0)
ENEMY_BASE_MANA = config_manager.get('game', 'enemy.base_mana', 25.0)
ENEMY_BASE_STAMINA = config_manager.get('game', 'enemy.base_stamina', 50.0)

# Множители для боссов
BOSS_HEALTH_MULTIPLIER = config_manager.get('game', 'boss.health_multiplier', 5.0)
BOSS_DAMAGE_MULTIPLIER = config_manager.get('game', 'boss.damage_multiplier', 2.0)

# Базовые параметры боя
CRITICAL_CHANCE_BASE = config_manager.get('game', 'combat.critical_chance_base', 0.05)
CRITICAL_MULTIPLIER_BASE = config_manager.get('game', 'combat.critical_multiplier_base', 2.0)

# Система опыта
XP_BASE = config_manager.get('game', 'experience.base_xp', 100)
XP_MULTIPLIER = config_manager.get('game', 'experience.xp_multiplier', 1.5)
LEVEL_CAP = config_manager.get('game', 'experience.level_cap', 100)
