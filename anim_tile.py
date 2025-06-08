# anim_tile.py

from ursina import Entity, Animation, time
from helper.support import import_folder


class AnimTile(Entity):
    def __init__(self, position, groups=None, sprite_type='lake', surface=None):
        super().__init__(
            model='quad',
            texture=None,
            position=(position[0], position[1], -1),
            collider='box'
        )

        self.sprite_type = sprite_type
        self.animation_speed = 0.15
        self.frame_index = 0

        # Загрузка анимации
        self.import_player_assets()
        self.animate()

    def import_player_assets(self):
        water_path = 'graphics/water/'

        self.animations = {
            'lake': []
        }

        for animation in self.animations:
            full_path = water_path + animation
            frames = import_folder(full_path)
            for frame in frames:
                self.animations[animation].append(frame)

    def animate(self):
        self.frame_index += self.animation_speed * 60 * time.dt
        if self.frame_index >= len(self.animations['lake']):
            self.frame_index = 0
        self.texture = self.animations['lake'][int(self.frame_index)]

    def update(self):
        self.animate()