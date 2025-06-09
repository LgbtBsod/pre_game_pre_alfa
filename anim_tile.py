# anim_tile.py

from ursina import Entity, time, Vec2
from helper.settings import TILESIZE
from helper.support import import_folder


class AnimTile(Entity):
    def __init__(self, position, groups=None, sprite_type='lake', surface=None):
        super().__init__(
            model='quad',
            position=Vec2(position[0], position[1]),
            z=-0.5,
            collider='box'
        )

        self.sprite_type = sprite_type
        self.animation_speed = 0.1
        self.frame_index = 0

        # Загрузка анимации
        self.animations = {}
        self.import_player_assets()

        self.texture = self.animations['lake'][0] if 'lake' in self.animations else None

    def import_player_assets(self):
        """Загружает анимацию воды"""
        water_path = 'graphics/water/'

        self.animations = {'lake': []}

        for animation in self.animations:
            full_path = water_path + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self):
        """Обновляет кадр анимации"""
        self.frame_index += self.animation_speed * time.dt * 60  # Адаптация скорости под FPS

        if self.frame_index >= len(self.animations['lake']):
            self.frame_index = 0

        self.texture = self.animations['lake'][int(self.frame_index)]

    def update(self):
        self.animate()