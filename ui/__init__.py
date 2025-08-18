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
    from .render_manager import RenderManager
except ImportError:
    RenderManager = None

try:
    from .main_window import MainWindow
except ImportError:
    MainWindow = None

__all__ = ["Button", "GameMenu", "RenderManager", "MainWindow"]
