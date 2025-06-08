# weapon.py

from ursina import Entity, Vec2

class Weapon(Entity):
    def __init__(self, player, groups=None):
        super().__init__(
            model='quad',
            position=player.position,
            z=-0.1,
            scale=(1, 1),
            parent=player
        )

        self.sprite_type = 'weapon'
        self.player = player
        self.direction = player.status.split('_')[0]
        self.weapon = player.weapon

        # Загрузка текстуры
        full_path = f'graphics/weapons/{self.weapon}/{self.direction}.png'
        self.texture = full_path

        # Позиционирование оружия относительно игрока
        offset = {
            'right': (32, 0),
            'left': (-32, 0),
            'up': (0, 32),
            'down': (0, -32)
        }

        self.position = offset[self.direction]

    def update(self):
        if self.parent:
            self.rotation = self.parent.rotation