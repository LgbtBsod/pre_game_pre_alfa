# equipment.py

from ursina import Entity, color, Text, camera, Vec3
from equip.chance import chance
from helper.settings import artifacts
from helper.support import convert_to_num


class Equipment(Entity):
    def __init__(self, player):
        super().__init__(
            model='quad',
            texture=None,
            scale=(0.1, 0.1),
            position=(-0.75, -0.4),
            z=-0.2,
            parent=camera
        )

        self.player = player
        self.equip = ['Brave Heart']  # Начальный предмет для теста
        self.equip_stat = {
            'health': 0,
            'attack': 0,
            'magic': 0,
            'agility': 0,
            'hp_regen': 0,
            'speed': 0,
            'stamina': 0,
            'energy': 0,
            'strength': 0,
            'crit_chance': 0,
            'crit_rate': 0
        }

        # Текст для отладки (показывает активные баффы)
        self.buff_text = Text(
            text='',
            position=Vec3(-0.85, 0.3, -1),
            scale=0.8,
            color=color.gold
        )

    def add_to_bag(self, item):
        if item in self.equip:
            print(f'{item} уже в инвентаре')
            return

        print(f'Получен: {item}')
        self.equip.append(item)
        self.get_equip_stat()
        self.show_buffs()

    def get_equip_stat(self):
        """Считает бонусы со всех экипированных предметов"""
        self.equip_stat = {stat: 0 for stat in self.equip_stat}

        for item in self.equip:
            if item not in artifacts:
                continue

            artifact = artifacts[item]
            for stat in artifact['stats']:
                value = artifact['stats'][stat]

                if stat in ['crit_rate', 'crit_chance']:
                    self.equip_stat[stat] = value
                else:
                    self.equip_stat[stat] += value

        # Применяем к игроку
        self.current_stats(self.equip_stat)

    def current_stats(self, stats):
        """Применяет статы к игроку"""
        base = self.player.base

        for stat in stats:
            if stat in ['crit_rate', 'crit_chance']:
                base[stat] = stats[stat] + self.player.current_stats[stat]
            else:
                if '%' in str(stats[stat]):
                    percent = convert_to_num(stats[stat])
                    base[stat] *= (1 + percent)
                else:
                    base[stat] += stats[stat]

        self.player.current_stats = base.copy()

    def show_buffs(self):
        """Отображает активные баффы в UI"""
        buffs = []
        for stat in self.equip_stat:
            value = self.equip_stat[stat]
            if value != 0:
                buffs.append(f"{stat}: {value}")

        self.buff_text.text = '\n'.join(buffs)