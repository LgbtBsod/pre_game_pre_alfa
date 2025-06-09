# player/base_player.py

from ursina import Entity, Vec2, time, held_keys


class BasePlayer(Entity):
    def __init__(self, position=(0, 0), groups=None, obstacle_sprites=None, **kwargs):
        super().__init__(
            model='quad',
            texture=self.get_texture(),
            position=Vec2(*position),
            z=-1,
            collider='box'
        )

        # Статы (должны быть переопределены в подклассах)
        self.base_stats = {
            'health': 100,
            'energy': 60,
            'attack': 10,
            'magic': 2,
            'speed': 1,
            'strength': 2,
            'agility': 2,
            'stamina': 200,
            'hp_regen': 0.1,
            'crit_chance': 10,
            'crit_rate': 120
        }

        self.max_stats = {k: v * 3 if isinstance(v, (int, float)) else v for k, v in self.base_stats.items()}
        self.upgrade_cost = {stat: 100 for stat in self.base_stats}

        # Атрибуты для динамических статов
        self.current_stats = self.base_stats.copy()
        self.health = self.current_stats['health']
        self.energy = self.current_stats['energy']
        self.exp = 0

        # Оружие и магия
        self.weapon_index = 0
        self.can_switch_weapon = True
        self.switch_duration_cooldown = 0.2
        self.obstacle_sprites = obstacle_sprites

        # Анимация и движение
        self.status = 'down'
        self.direction = Vec2(0, 0)
        self.speed = self.current_stats['speed'] * self.current_stats['agility']

    def get_texture(self):
        return 'graphics/player/down_idle/down.png'

    def input(self):
        """Базовая логика ввода"""
        pass

    def move(self):
        """Базовое движение"""
        self.position += self.direction * self.speed * time.dt

    def update(self):
        """Обновление состояния игрока"""
        self.input()
        self.move()