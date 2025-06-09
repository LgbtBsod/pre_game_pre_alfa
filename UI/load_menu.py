# UI/load_menu.py

from ursina import Entity, Button, Text, color, Vec2, camera
from player.player import LikePlayer 
from save.save_load import load


class LoadMenu(Entity):
    def __init__(self, level):
        super().__init__(
            parent=camera.ui,
            model='quad',
            scale=(0.4, 0.6),
            position=Vec2(0, 0),
            color=color.rgba(30, 30, 30, 200),
            enabled=False
        )

        self.level = level
        self.slots = 3
        self.buttons = []
        
        self.menu_title = Text(
            text='Load Game',
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
            btn.on_click = lambda s=i+1: self.load_slot(s)
            self.buttons.append(btn)

        self.back_button = Button(
            parent=self,
            text='Back',
            position=Vec2(0.1, -0.2),
            scale=0.25,
            color=color.red
        )
        self.back_button.on_click = self.hide

    def load_slot(self, slot):
        from save.save_load import load
        data = load(slot=slot)
        
        if data and 'map' in data and 'player' in data:
            print(f'[Load] Загружаем слот {slot}')
            self.level.clear_level()
            self.level.load_player_data(data['player'])
            self.level.load_enemies_data(data.get('enemies', []))
            self.level.map_name = data.get('map', 'test')  # ← сохраняем имя карты
            self.level._load_map(self.level.map_name)  # ← загружаем по имени
        else:
            print(f'[Load] Слот {slot} пуст')
        self.hide()
        
    def hide(self):
        self.enabled = False

    def enable(self):
        self.enabled = True