"""
Core module for AI-EVOLVE Enhanced Edition
Основные компоненты игрового движка
"""

from .game_engine import GameEngine
from .config_manager import ConfigManager
from .game_state import GameState
from .scene_manager import SceneManager
from .resource_manager import ResourceManager
from .performance_manager import PerformanceManager

__all__ = [
    'GameEngine',
    'ConfigManager', 
    'GameState',
    'SceneManager',
    'ResourceManager',
    'PerformanceManager'
]
