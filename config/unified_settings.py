"""
Единые настройки игры для устранения дублирования.
Все базовые константы и настройки централизованы здесь.
"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class WindowSettings:
    """Настройки окна"""
    WIDTH: int = 1200
    HEIGHT: int = 800
    DEFAULT_WIDTH: int = 1200
    DEFAULT_HEIGHT: int = 800
    MIN_WIDTH: int = 800
    MIN_HEIGHT: int = 600
    MAX_WIDTH: int = 1920
    MAX_HEIGHT: int = 1080


@dataclass
class FPSSettings:
    """Настройки FPS"""
    RENDER_FPS: int = 60
    UPDATE_FPS: int = 120
    MIN_FPS: int = 30
    MAX_FPS: int = 144
    VSYNC: bool = True


@dataclass
class ColorSettings:
    """Цветовые настройки"""
    BACKGROUND: Tuple[int, int, int] = (0, 0, 0)
    PLAYER_COLOR: Tuple[int, int, int] = (0, 255, 0)
    ENEMY_COLOR: Tuple[int, int, int] = (255, 0, 0)
    BOSS_COLOR: Tuple[int, int, int] = (255, 0, 255)
    NPC_COLOR: Tuple[int, int, int] = (0, 0, 255)
    ITEM_COLOR: Tuple[int, int, int] = (255, 255, 0)
    PROJECTILE_COLOR: Tuple[int, int, int] = (255, 136, 0)
    EFFECT_COLOR: Tuple[int, int, int] = (0, 255, 255)
    TEXT_COLOR: Tuple[int, int, int] = (255, 255, 255)
    UI_BACKGROUND: str = "#1a1a1a"
    UI_TEXT: str = "#ffffff"
    UI_BUTTON: str = "#444444"
    UI_BUTTON_HOVER: str = "#666666"


@dataclass
class AISettings:
    """Базовые AI настройки"""
    LEARNING_RATE_BASE: float = 0.1
    MEMORY_DECAY_RATE_BASE: float = 0.95
    PATTERN_RECOGNITION_THRESHOLD: float = 0.7
    EMOTION_SYNTHESIS_ENABLED: bool = True
    ADAPTIVE_DIFFICULTY: bool = True
    AI_UPDATE_FREQUENCY: float = 0.1
    DECISION_DELAY: float = 0.5
    MEMORY_DURATION: float = 30.0
    PERSONALITY_CHANGE_RATE: float = 0.02
    EXPERIENCE_THRESHOLD: int = 10
    ADAPTATION_SPEED: float = 0.05


@dataclass
class CombatSettings:
    """Базовые боевые настройки"""
    ATTACK_RANGE_BASE: float = 50.0
    BASE_DAMAGE: float = 10.0
    CRITICAL_MULTIPLIER_BASE: float = 2.0
    CRITICAL_CHANCE_BASE: float = 0.05
    DAMAGE_REDUCTION_BASE: float = 0.1
    BASE_ATTACK_COOLDOWN: float = 1.0
    BLOCK_CHANCE_CAP: float = 0.75
    DODGE_CHANCE_CAP: float = 0.5
    PARRY_CHANCE_CAP: float = 0.4
    DAMAGE_REDUCTION_CAP: float = 0.8


@dataclass
class MovementSettings:
    """Настройки движения"""
    BASE_MOVEMENT_SPEED: float = 100.0
    SPRINT_MULTIPLIER: float = 1.5
    CROUCH_MULTIPLIER: float = 0.6
    SWIM_MULTIPLIER: float = 0.7
    CLIMB_MULTIPLIER: float = 0.4
    GRAVITY: float = 0.0
    FRICTION: float = 0.8
    COLLISION_TOLERANCE: float = 2.0


@dataclass
class MapSettings:
    """Настройки карты"""
    TILE_SIZE: int = 32
    MAP_WIDTH: int = 50
    MAP_HEIGHT: int = 50
    CAMERA_SMOOTHING: float = 0.1


@dataclass
class PlayerSettings:
    """Настройки игрока"""
    START_HEALTH: int = 100
    START_MANA: int = 50
    START_STAMINA: int = 100
    MOVEMENT_SPEED: int = 150
    ATTACK_SPEED: float = 1.0
    LEARNING_RATE: float = 0.2


@dataclass
class EnemySettings:
    """Настройки врагов"""
    BASE_HEALTH: int = 80
    BASE_MANA: int = 30
    BASE_STAMINA: int = 80
    MOVEMENT_SPEED: int = 100
    ATTACK_SPEED: float = 0.8
    LEARNING_RATE: float = 0.15
    ATTACK_RANGE: float = 50.0


@dataclass
class UISettings:
    """Настройки UI"""
    ELEMENT_HEIGHT: int = 30
    PADDING: int = 10
    MARGIN: int = 5
    FONT_SIZE: int = 14
    UI_SCALE: float = 1.0
    SHOW_DAMAGE_NUMBERS: bool = True
    SHOW_HEALTH_BARS: bool = True
    SHOW_MINIMAP: bool = True


@dataclass
class AudioSettings:
    """Настройки звука"""
    MASTER_VOLUME: float = 1.0
    MUSIC_VOLUME: float = 0.8
    SFX_VOLUME: float = 1.0
    VOICE_VOLUME: float = 0.9
    AMBIENT_VOLUME: float = 0.6
    AUDIO_ENABLED: bool = True
    SOUND_ENABLED: bool = True
    MUSIC_ENABLED: bool = True


@dataclass
class GraphicsSettings:
    """Настройки графики"""
    FULLSCREEN: bool = False
    ANTIALIASING: str = "msaa_4x"
    TEXTURE_QUALITY: str = "high"
    SHADOW_QUALITY: str = "medium"
    PARTICLE_QUALITY: str = "high"
    RENDER_DISTANCE: int = 1000
    ENABLE_SHADOWS: bool = True
    ENABLE_BLOOM: bool = True
    ENABLE_MOTION_BLUR: bool = False
    ENABLE_DOF: bool = False
    ENABLE_SSAO: bool = True
    ENABLE_FXAA: bool = True


@dataclass
class GameplaySettings:
    """Настройки геймплея"""
    AUTO_SAVE_INTERVAL: int = 300
    MAX_SAVE_SLOTS: int = 10
    INVENTORY_SLOTS: int = 20
    EQUIPMENT_SLOTS: int = 8
    STACK_SIZE_LIMIT: int = 99
    WEIGHT_LIMIT_ENABLED: bool = True
    BASE_WEIGHT_LIMIT: float = 100.0
    LANGUAGE: str = "ru"


@dataclass
class LevelingSettings:
    """Настройки прокачки"""
    XP_BASE: int = 100
    XP_MULTIPLIER: float = 1.5
    LEVEL_CAP: int = 100


@dataclass
class InventorySettings:
    """Настройки инвентаря"""
    SLOTS: int = 20
    EQUIPMENT_SLOTS: int = 8
    STACK_SIZE_LIMIT: int = 99
    WEIGHT_LIMIT_ENABLED: bool = True
    BASE_WEIGHT_LIMIT: float = 100.0


@dataclass
class EffectSettings:
    """Настройки эффектов"""
    DURATION_BASE: float = 10.0
    TICK_RATE: float = 1.0
    MAX_ACTIVE_EFFECTS: int = 20


@dataclass
class SkillSettings:
    """Настройки способностей"""
    COOLDOWN_BASE: float = 1.0
    MANA_COST_BASE: int = 10
    STAMINA_COST_BASE: int = 15


@dataclass
class LootSettings:
    """Настройки лута"""
    DROP_CHANCE_BASE: float = 0.3
    QUALITY_BASE: float = 1.0
    RARE_ITEM_CHANCE: float = 0.1
    EPIC_ITEM_CHANCE: float = 0.05
    LEGENDARY_ITEM_CHANCE: float = 0.01


class UnifiedSettings:
    """
    Единый класс всех настроек игры.
    Централизует все константы и базовые значения.
    """
    
    def __init__(self):
        self.window = WindowSettings()
        self.fps = FPSSettings()
        self.colors = ColorSettings()
        self.ai = AISettings()
        self.combat = CombatSettings()
        self.movement = MovementSettings()
        self.map = MapSettings()
        self.player = PlayerSettings()
        self.enemy = EnemySettings()
        self.ui = UISettings()
        self.audio = AudioSettings()
        self.graphics = GraphicsSettings()
        self.gameplay = GameplaySettings()
        self.leveling = LevelingSettings()
        self.inventory = InventorySettings()
        self.effects = EffectSettings()
        self.skills = SkillSettings()
        self.loot = LootSettings()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Возвращает все настройки в виде словаря"""
        return {
            'window': self.window.__dict__,
            'fps': self.fps.__dict__,
            'colors': self.colors.__dict__,
            'ai': self.ai.__dict__,
            'combat': self.combat.__dict__,
            'movement': self.movement.__dict__,
            'map': self.map.__dict__,
            'player': self.player.__dict__,
            'enemy': self.enemy.__dict__,
            'ui': self.ui.__dict__,
            'audio': self.audio.__dict__,
            'graphics': self.graphics.__dict__,
            'gameplay': self.gameplay.__dict__,
            'leveling': self.leveling.__dict__,
            'inventory': self.inventory.__dict__,
            'effects': self.effects.__dict__,
            'skills': self.skills.__dict__,
            'loot': self.loot.__dict__
        }
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Получает значение настройки по категории и ключу"""
        if hasattr(self, category):
            category_obj = getattr(self, category)
            if hasattr(category_obj, key):
                return getattr(category_obj, key)
        return default
    
    def set_setting(self, category: str, key: str, value: Any) -> bool:
        """Устанавливает значение настройки"""
        try:
            if hasattr(self, category):
                category_obj = getattr(self, category)
                if hasattr(category_obj, key):
                    setattr(category_obj, key, value)
                    return True
            return False
        except Exception:
            return False


# Глобальный экземпляр единых настроек
unified_settings = UnifiedSettings()


# Функции для обратной совместимости
def get_window_settings() -> WindowSettings:
    """Возвращает настройки окна"""
    return unified_settings.window


def get_fps_settings() -> FPSSettings:
    """Возвращает настройки FPS"""
    return unified_settings.fps


def get_color_settings() -> ColorSettings:
    """Возвращает цветовые настройки"""
    return unified_settings.colors


def get_ai_settings() -> AISettings:
    """Возвращает AI настройки"""
    return unified_settings.ai


def get_combat_settings() -> CombatSettings:
    """Возвращает боевые настройки"""
    return unified_settings.combat


def get_movement_settings() -> MovementSettings:
    """Возвращает настройки движения"""
    return unified_settings.movement


def get_map_settings() -> MapSettings:
    """Возвращает настройки карты"""
    return unified_settings.map


def get_player_settings() -> PlayerSettings:
    """Возвращает настройки игрока"""
    return unified_settings.player


def get_enemy_settings() -> EnemySettings:
    """Возвращает настройки врагов"""
    return unified_settings.enemy


def get_ui_settings() -> UISettings:
    """Возвращает настройки UI"""
    return unified_settings.ui


def get_audio_settings() -> AudioSettings:
    """Возвращает настройки звука"""
    return unified_settings.audio


def get_graphics_settings() -> GraphicsSettings:
    """Возвращает графические настройки"""
    return unified_settings.graphics


def get_gameplay_settings() -> GameplaySettings:
    """Возвращает настройки геймплея"""
    return unified_settings.gameplay


def get_leveling_settings() -> LevelingSettings:
    """Возвращает настройки прокачки"""
    return unified_settings.leveling


def get_inventory_settings() -> InventorySettings:
    """Возвращает настройки инвентаря"""
    return unified_settings.inventory


def get_effect_settings() -> EffectSettings:
    """Возвращает настройки эффектов"""
    return unified_settings.effects


def get_skill_settings() -> SkillSettings:
    """Возвращает настройки способностей"""
    return unified_settings.skills


def get_loot_settings() -> LootSettings:
    """Возвращает настройки лута"""
    return unified_settings.loot
