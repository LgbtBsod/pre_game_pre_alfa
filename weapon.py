# weapon.py

from ursina import Entity, Vec2, destroy, time


class Weapon(Entity):
    def __init__(self, player, groups=None):
        super().__init__(
            model='quad',
            texture=f'assets/graphics/weapons/{player.weapon}/{player.status.split("_")[0]}.png',
            position=Vec2(0, 0),
            scale=(1, 1),
            parent=player,
            z=-0.1
        )

        self.player = player
        self.sprite_type = 'weapon'
        self.attack_time = time.time()
        self.attack_duration = 0.2  # длительность жизни атаки

        # Смещение относительно игрока
        self.offset = {
            'right': Vec2(32, 0),
            'left': Vec2(-32, 0),
            'up': Vec2(0, 32),
            'down': Vec2(0, -32)
        }

        self.position = self.offset.get(self.player.status.split('_')[0], Vec2(0, 0))

    def update(self):
        """Обновляет атаку"""
        if not self.parent:
            destroy(self)
            return

        # Автоматическое уничтожение после окончания действия
        if time.time() - self.attack_time > self.attack_duration:
            destroy(self)
            return

        # Вращение вместе с игроком (если нужно)
        if hasattr(self.parent, 'rotation'):
            self.rotation = self.parent.rotation