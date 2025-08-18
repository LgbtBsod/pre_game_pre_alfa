# Zelda Game - Code Package
# This file makes the code directory a Python package

# Core systems
from .core.game_state import GameState, GameStateManager
from .core.event_manager import EventManager, EventType, GameEvent
from .core.input_manager import InputManager, InputAction
from .core.config import ConfigManager, GameConfig
from .core.logger import GameLogger, init_logger, get_logger, cleanup_logger
from .core.resource_manager import ResourceManager, ResourceType
from .core.audio_manager import AudioManager, AudioType, init_audio_manager, get_audio_manager
from .core.performance_monitor import PerformanceMonitor, PerformanceMetrics
from .core.game_data import GameDataManager, WeaponData, MagicData, EnemyData
from .core.game_manager import GameManager, get_game_manager, cleanup_game_manager

# Game entities
from .entity import Entity
from .player import Player
from .enemy import Enemy
from .weapon import Weapon
from .magic import MagicPlayer

# Game systems
from .level import Level
from .ui import UI
from .particles import AnimationPlayer
from .upgrade import Upgrade

# Utility modules
from .tile import Tile
from .support import import_csv_layout, import_folder

__version__ = "2.0.0"
__author__ = "Zelda Development Team"

# Export main classes and functions
__all__ = [
    # Core systems
    'GameState', 'GameStateManager',
    'EventManager', 'EventType', 'GameEvent',
    'InputManager', 'InputAction',
    'ConfigManager', 'GameConfig',
    'GameLogger', 'init_logger', 'get_logger', 'cleanup_logger',
    'ResourceManager', 'ResourceType',
    'AudioManager', 'AudioType', 'init_audio_manager', 'get_audio_manager',
    'PerformanceMonitor', 'PerformanceMetrics',
    'GameDataManager', 'WeaponData', 'MagicData', 'EnemyData',
    'GameManager', 'get_game_manager', 'cleanup_game_manager',
    
    # Game entities
    'Entity', 'Player', 'Enemy', 'Weapon', 'MagicPlayer',
    
    # Game systems
    'Level', 'UI', 'AnimationPlayer', 'Upgrade',
    
    # Utility modules
    'Tile', 'import_csv_layout', 'import_folder'
]
