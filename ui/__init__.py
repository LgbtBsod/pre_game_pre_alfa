"""Модуль пользовательского интерфейса."""

# Импорты UI компонентов
try:
    from .buttons import Button, ButtonGroup, ToggleButton
except ImportError:
    Button = None
    ButtonGroup = None
    ToggleButton = None

try:
    from .game_menu import GameMenu
except ImportError:
    GameMenu = None

try:
    from .game_interface import GameInterface
except ImportError:
    GameInterface = None

try:
    from .hud import StatusHUD, InventoryHUD, GeneticsHUD, AILearningHUD, DebugHUD
except ImportError:
    StatusHUD = None
    InventoryHUD = None
    GeneticsHUD = None
    AILearningHUD = None
    DebugHUD = None

try:
    from .camera import Camera
except ImportError:
    Camera = None

try:
    from .renderer import GameRenderer
except ImportError:
    GameRenderer = None

try:
    from .menu_scene import MenuScene
except ImportError:
    MenuScene = None

try:
    from .pause_scene import PauseScene
except ImportError:
    PauseScene = None

__all__ = [
    "Button", "ButtonGroup", "ToggleButton",
    "GameMenu", "GameInterface",
    "StatusHUD", "InventoryHUD", "GeneticsHUD", "AILearningHUD", "DebugHUD",
    "Camera", "GameRenderer", "MenuScene", "PauseScene"
]
