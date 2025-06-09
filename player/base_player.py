from ursina import Entity, Vec2, time, held_keys


class BasePlayer(Entity):
    def __init__(self, position=(0, 0), groups=None, obstacle_sprites=None):
        super().__init__(
            model='quad',
            texture='graphics/player/down_idle/down.png',
            position=Vec2(*position),
            z=-1,
            collider='box'
        )

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
        self.reactive_effects = {}
        self.active_effects = {}

    def input(self):
        """Обработка клавиш"""
        pass

    def move(self):
        """Логика движения"""
        pass

    def on_take_damage(self, amount, attack_type):
        """Вызывается при получении урона"""
        for name, func in self.reactive_effects.items():
            amount = func(player=self, amount=amount, attack_type=attack_type)
        return max(amount, 0)

    def try_activate_effect(self, effect_name):
        if effect_name in self.active_effects:
            self.active_effects[effect_name]()

    def update(self):
        self.input()
        self.move()