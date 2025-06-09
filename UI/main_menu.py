# UI/main_menu.py

from ursina import Entity, Button, Text, color, Vec2, camera, application 


class MainMenu(Entity):
    def __init__(self, game):
        super().__init__(
            parent=camera.ui,
            enabled=False  # По умолчанию скрыто
        )
        self.game = game
        self._init_ui()

    def _init_ui(self):
        # Фоновое изображение
        self.background = Entity(
            parent=self,
            model='quad',
            texture='assets/textures/menu_bg',
            scale=(2, 1),
            z=1
        )
        
        # Кнопки
        self.new_game_btn = Button(
            text='Новая игра',
            position=(0, 0.1),
            on_click=self.start_new_game
        )
        
        self.load_game_btn = Button(
            text='Загрузить',
            position=(0, -0.1),
            on_click=self.show_load_menu
        )

    def start_new_game(self):
        print("[Меню] Новая игра")
        self.disable()  # Скрываем меню
        self.game.start_level('test')  # Запускаем уровень
        self.game.ui.enable()  # Показываем игровой UI

    def show_load_menu(self):
        print("[Меню] Загрузить")
        self.disable()
        self.game.show_menu('load')

    def enable(self):
        super().enable()
        # При показе меню скрываем игровой UI
        if hasattr(self.game, 'ui'):
            self.game.ui.disable()

    def disable(self):
        super().disable()