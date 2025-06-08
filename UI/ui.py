# UI/ui.py

from ursina import Entity, Text, color, scene


class UI(Entity):
    def __init__(self):
        super().__init__(parent=scene)

        # Общие настройки
        self.player = None

        # Полоски здоровья и энергии
        self.health_bar = self.create_bar(
            position=(-0.75, 0.45),
            scale=(0.3, 0.03),
            bar_color=color.red,
            label='Health'
        )
        self.energy_bar = self.create_bar(
            position=(-0.75, 0.4),
            scale=(0.2, 0.03),
            bar_color=color.blue,
            label='Energy'
        )

        # Текст опыта
        self.exp_text = Text(
            text='EXP: 0',
            position=(0.65, -0.45),
            scale=1,
            color=color.white,
            parent=self
        )

        # Иконки оружия и магии
        self.weapon_icon = Entity(
            model='quad',
            texture='graphics/weapons/sword/full.png',
            position=(-0.8, -0.4),
            scale=0.07,
            z=-1,
            parent=self
        )
        self.magic_icon = Entity(
            model='quad',
            texture='graphics/particles/heal/heal0.png',
            position=(-0.65, -0.4),
            scale=0.07,
            z=-1,
            parent=self
        )

    def create_bar(self, position, scale, bar_color, label='Bar'):
        bg = Entity(
            model='quad',
            color=(30, 30, 30, 255),  # Темно-серый фон
            position=position,
            scale=scale,
            z=-0.1,
            parent=self
        )
        bar = Entity(
            model='quad',
            color=bar_color,
            position=position,
            scale=(scale[0] * 0.95, scale[1] * 0.9),
            origin=(-0.5, 0),
            z=-0.1,
            parent=self
        )
        label_text = Text(
            text=label,
            position=position + (-0.05, 0.015),
            scale=0.8,
            color=color.white,
            parent=self
        )
        return {'bg': bg, 'bar': bar, 'label': label_text}

    def show_bar(self, current, max_amount, bar_obj, bar_color):
        ratio = current / max_amount
        bar_obj['bar'].scale_x = bar_obj['bg'].scale_x * ratio
        bar_obj['bar'].color = bar_color

    def show_exp(self, exp):
        self.exp_text.text = f'EXP: {int(exp)}'

    def weapon_overlay(self, weapon_index, has_switched):
        if weapon_index < len(weapon_data):
            weapon_name = list(weapon_data.keys())[weapon_index]
            path = f'graphics/weapons/{weapon_name}/full.png'
            self.weapon_icon.texture = path
            self.weapon_icon.color = color.gold if has_switched else color.white

    def magic_overlay(self, magic_index, has_switched):
        if magic_index < len(magic_data):
            magic_name = list(magic_data.keys())[magic_index]
            path = magic_data[magic_name]['graphic']
            self.magic_icon.texture = path
            self.magic_icon.color = color.gold if has_switched else color.white

    def display(self, player):
        self.player = player

        # Обновление полосок
        self.show_bar(player.health, player.current_stats['health'], self.health_bar, color.red)
        self.show_bar(player.energy, player.current_stats['energy'], self.energy_bar, color.blue)

        # Опыт
        self.show_exp(player.exp)

        # Иконки
        self.weapon_overlay(player.weapon_index, not player.can_switch_weapon)
        self.magic_overlay(player.magic_index, not player.can_switch_magic)