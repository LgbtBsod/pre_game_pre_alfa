# UI/save_menu.py

from ursina import Entity, Button, Text, color, Vec2, camera


class SaveMenu(Entity):
    def __init__(self, game):
        super().__init__(
            parent=camera.ui,
            model='quad',
            scale=(0.4, 0.6),
            position=Vec2(0, 0),
            color=color.rgba(30, 30, 30, 200),
            enabled=False
        )

        self.game = game
        self.slots = 3
        self.buttons = []

        self.menu_title = Text(
            text='Save Menu',
            position=Vec2(0, 0.25),
            scale=2,
            color=color.gold,
            parent=self
        )

        for i in range(self.slots):
            y_pos = 0.1 - i * 0.1
            btn = Button(
                parent=self,
                text=f'Slot {i+1}',
                position=Vec2(-0.1, y_pos),
                scale=0.25,
                color=color.dark_gray
            )
            btn.on_click = lambda s=i+1: self.save_slot(s)
            self.buttons.append(btn)

        self.back_button = Button(
            parent=self,
            text='Back',
            position=Vec2(0.1, -0.2),
            scale=0.25,
            color=color.red
        )
        self.back_button.on_click = self.hide

    def toggle(self):
        self.enabled = not self.enabled

    def show(self):
        self.enabled = True

    def hide(self):
        self.enabled = False

    def save_slot(self, slot):
        """Сохраняет игру в указанный слот"""
        if hasattr(self.game, 'save_game'):
            self.game.save_game(slot=slot)
        else:
            print('[Ошибка] Метод save_game не найден в Level')
        self.hide()
    
    def update(self):
        pass