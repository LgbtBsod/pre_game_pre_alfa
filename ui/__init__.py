"""Модуль пользовательского интерфейса."""

# Условные импорты для совместимости
try:
    from .buttons import Button
except ImportError:
    Button = None

try:
    from .game_menu import GameMenu
except ImportError:
    GameMenu = None

try:
    from .game_interface import GameInterface
except ImportError:
    GameInterface = None

__all__ = ["Button", "GameMenu", "GameInterface"]
