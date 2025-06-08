# tile.py

from ursina import Entity, color
from helper.settings import TILESIZE


class Tile(Entity):
    def __init__(self, position, groups=None, sprite_type='invisible', surface=None):
        super().__init__(
            model='quad',
            texture=surface,
            position=(position[0], position[1], 0),
            collider='box'
        )

        self.sprite_type = sprite_type
        self.hitbox = self.get_hitbox(position)

    def get_hitbox(self, pos):
        # Создаём невидимую сущность для hitbox
        offset = {
            'object': (-0, -TILESIZE),
            'tree': (0, -32),
            'invisible': (0, 0)
        }.get(self.sprite_type, (0, 0))

        return Entity(
            model='wireframe_cube',
            color=color.clear,  # ← Используем цвет напрямую
            scale=(TILESIZE, TILESIZE, 1),
            position=(pos[0] + offset[0], pos[1] + offset[1], -1),
            collider='box',
            parent=self
        )