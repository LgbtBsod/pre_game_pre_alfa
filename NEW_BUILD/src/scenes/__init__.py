"""
Scenes module for AI-EVOLVE Enhanced Edition
Игровые сцены и их управление
"""

from .menu_scene import MenuScene
from .game_scene import GameScene
from .pause_scene import PauseScene

__all__ = [
    'MenuScene',
    'GameScene', 
    'PauseScene'
]
