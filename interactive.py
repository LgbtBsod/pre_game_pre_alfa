# interactive.py

from ursina import Entity, Vec2


class UseSprite(Entity):
    def __init__(self, position=(0, 0), groups=None):
        super().__init__(
            model='quad',
            collider='box',
            scale=(TILESIZE / 64, TILESIZE / 64),
            z=-0.5,
            position=Vec2(position[0], position[1])
        )

        self.sprite_type = 'interactive'
        self.obstacle_sprites = []

    def get_distance(self, player):
        """Возвращает расстояние до игрока"""
        player_vec = Vec2(player.x, player.y)
        this_vec = Vec2(self.x, self.y)
        return (player_vec - this_vec).length()