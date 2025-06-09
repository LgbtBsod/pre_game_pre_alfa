# player/base_player.py

from ursina import Entity, Vec2, time, held_keys
from effects.buff_manager import BuffManager


class BasePlayer(Entity):
    def __init__(self, position=(0, 0), groups=None, obstacle_sprites=None):
        super().__init__(
            model='quad',
            texture='assets/graphics/player/down_idle/down.png',
            position=Vec2(*position),
            z=-1,
            collider='box'
        )

        # Базовые статы
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

        self.current_stats = self.base_stats.copy()
        self.max_stats = {k: v * 3 for k, v in self.base_stats.items()}

        # Экипировка и баффы
        self.equip = []
        self.reactive_effects = {}
        self.active_effects = {}

        # Бафф менеджер
        self.buff_manager = BuffManager(self)

        # Состояние игрока
        self.attacking = False
        self.can_move = True
        self.vulnerable = True
        self.hurt_time = 0
        self.invulnerability_duration = 0.5

        # Движение
        self.direction = Vec2(0, 0)
        self.speed = self.current_stats['speed'] * self.current_stats['agility']
        self.obstacle_sprites = obstacle_sprites

    def move(self):
        """Движение персонажа"""
        if not self.can_move:
            return

        self.position += self.direction * self.speed * time.dt

    def on_take_damage(self, amount, attack_type):
        """Срабатывает при получении урона"""
        for name, func in self.reactive_effects.items():
            amount = func(player=self, amount=amount, attack_type=attack_type)

        self.current_stats['health'] = max(self.current_stats['health'] - amount, 0)
        print(f'[Урон] Получено: {amount}, осталось здоровья: {self.current_stats["health"]}')

        if not self.vulnerable:
            return

        self.vulnerable = False
        self.hurt_time = time.time()

    def update(self):
        """Обновление состояния игрока"""
        self.input()
        self.move()
        self.buff_manager.update(time.time)
               
    def to_dict(self):
        """Сохраняет текущее состояние игрока в словарь"""
        return {
            'position': list(self.position),
            'base_stats': self.base_stats,
            'current_stats': self.current_stats,
            'level': self.level,
            'exp': self.exp,
            'weapon_index': self.weapon_index,
            'magic_index': self.magic_index,
            'equip': self.equip
            }

    @classmethod
    def from_dict(cls, data):
        """Восстанавливает игрока из слота сохранения"""
        instance = cls(position=data['position'])
        instance.base_stats = data['base_stats']
        instance.current_stats = data['current_stats']
        instance.level = data['level']
        instance.exp = data['exp']
        instance.weapon_index = data.get('weapon_index', 0)
        instance.magic_index = data.get('magic_index', 0)
        for item in data.get('equip', []):
            instance.equipment.add_to_bag(item)
        return instance
