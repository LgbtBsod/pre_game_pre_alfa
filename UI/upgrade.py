# UI/upgrade.py

from ursina import Entity, Button, Text, color, Vec2, camera


class UpgradeMenu(Entity):
    def __init__(self, player):
        super().__init__(
            parent=camera,  # ← Изменено: было camera.ui
            model='quad',
            scale=(0.6, 0.8),
            position=Vec2(0.5, 0),
            color=color.rgba(30, 30, 30, 200)
        )

        self.player = player
        self.selection_index = 0
        self.can_move = True
        self.selection_time = None

        self.create_items()
        self.hide()

    def create_items(self):
        self.item_list = []
        self.stat_names = list(self.player.base.keys())
        self.max_values = list(self.player.max_stats.values())

        for i, stat in enumerate(self.stat_names):
            y_pos = 0.3 - i * 0.1
            bg = Entity(
                parent=self,
                model='quad',
                scale=(0.5, 0.07),
                position=(-0.1, y_pos),
                color=color.dark_gray
            )
            label = Text(
                parent=self,
                text=stat,
                position=Vec2(-0.09, y_pos + 0.02),
                scale=1,
                color=color.white
            )
            value = Text(
                parent=self,
                text='100',
                position=Vec2(0.2, y_pos + 0.02),
                scale=1,
                color=color.gold
            )
            button = Button(
                parent=self,
                model='quad',
                scale=(0.05, 0.05),
                position=Vec2(0.3, y_pos),
                text='+',
                color=color.green
            )
            self.item_list.append({'bg': bg, 'label': label, 'value': value, 'button': button})

    def input(self):
        if self.can_move:
            if held_keys['up arrow']:
                self.selection_index = max(0, self.selection_index - 1)
                self.can_move = False
                self.selection_time = time.time()
            elif held_keys['down arrow']:
                self.selection_index = min(len(self.item_list) - 1, self.selection_index + 1)
                self.can_move = False
                self.selection_time = time.time()

            if held_keys['space']:
                self.upgrade(self.selection_index)
                self.can_move = False
                self.selection_time = time.time()

        if not self.can_move and time.time() - self.selection_time > 0.3:
            self.can_move = True

        for i, item in enumerate(self.item_list):
            item['bg'].color = color.light_gray if i == self.selection_index else color.dark_gray

    def upgrade(self, index):
        stat_name = self.stat_names[index]
        cost = self.player.upgrade_cost[stat_name]
        if self.player.exp >= cost and self.player.base[stat_name] < self.player.max_stats[stat_name]:
            self.player.exp -= cost
            self.player.base[stat_name] *= 1.1
            self.player.upgrade_cost[stat_name] *= 1.1

    def show(self):
        self.enabled = True

    def hide(self):
        self.enabled = False

    def update(self):
        self.input()
        self.update_values()

    def update_values(self):
        for i, item in enumerate(self.item_list):
            stat = self.stat_names[i]
            value = int(self.player.base[stat])
            item['value'].text = str(value)