from ursina import Ursina, camera, window, Vec2, held_keys, mouse
from ursina.prefabs.hot_reloader import HotReloader
from level import GameLevel
from UI.save_menu import SaveMenu
from UI.main_menu import MainMenu
from UI.load_menu import LoadMenu
from UI.InventoryUI import InventoryUI
from helper.settings import GAME_SETTINGS

class LikeRPG:
    def __init__(self):
        self.app = Ursina()
        self._setup_window()
        self._init_game()


    def _setup_window(self):
        """Настройки окна игры"""
        HotReloader().enabled = False
        camera.orthographic = True
        camera.fov = 10
        window.title = ' Like RPG'
        window.borderless = False
        window.fullscreen = False
        window.fps_counter.enabled = True
        window.exit_button.visible = True

    def _init_game(self):
        """Инициализация игрового уровня"""
        self.game = GameLevel(GAME_SETTINGS)
        
        # Инициализация меню (без автоматического запуска уровня)
        self.main_menu = MainMenu(self.game)
        self.load_menu = LoadMenu(self.game)
        self.save_menu = SaveMenu(self.game)
        
        # Показываем только главное меню сначала
        self.main_menu.enable()
        self.load_menu.disable()
        self.save_menu.disable()
        
        # Скрываем игровой UI
        if hasattr(self.game, 'ui'):
            self.game.ui.disable()
        
        # Инициализация геймпада
  
        self.gamepad = self._init_gamepad()
        
        
    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.save_menu = SaveMenu(self.game)
        self.main_menu = MainMenu(self.game)
        self.inventory = InventoryUI(player=self.game.player)
        self.inventory.enabled = False

    def _init_gamepad(self):
        """Инициализация геймпада"""
        if hasattr(self.app, 'gamepads') and len(self.app.gamepads) > 0:
            gamepad = self.app.gamepads[0]
            print(f"Connected gamepad: {gamepad}")
            return gamepad
        return None

    def _handle_keyboard_input(self, key):
        """Обработка ввода с клавиатуры"""
        if key == 'escape':
            self.save_menu.toggle()
        elif key == 'f5':
            self.game.save_game(slot=1)
        elif key == 'f9':
            self.game.load_game(slot=1)
        elif key == 'i':
            self.inventory.enabled = not self.inventory.enabled
            if self.inventory.enabled:
                self.inventory.update_inventory()

    def _handle_gamepad_input(self, key):
        """Обработка ввода с геймпада"""
        if key == 'gamepad start':
            self.save_menu.toggle()
        elif key == 'gamepad back':
            self.game.save_game(slot=1)
        elif key == 'gamepad a':
            print("Button A pressed")
        elif key == 'gamepad b':
            print("Button B pressed")

    def input(self, key):
        """Главный обработчик ввода"""
        self._handle_keyboard_input(key)
        
        if self.gamepad:
            self._handle_gamepad_input(key)

    def update(self):
        """Обновление состояния игры"""
        self._handle_gamepad_analog()
        self.game.update()

    def _handle_gamepad_analog(self):
        """Обработка аналоговых стиков и триггеров"""
        if not self.gamepad:
            return

        # Обработка движения
        left_x = self.gamepad.left_x
        left_y = self.gamepad.left_y
        
        deadzone = 0.2
        if abs(left_x) > deadzone or abs(left_y) > deadzone:
            movement = Vec2(left_x, -left_y)
            if hasattr(self.game.player, 'move'):
                self.game.player.move(movement)

        # Обработка действий
        if self.gamepad.right_trigger > 0.5:
            if hasattr(self.game.player, 'attack'):
                self.game.player.attack()

    def run(self):
        """Запуск игры"""
        self.app.run()

if __name__ == "__main__":
    game = LikeRPG()
    game.run()