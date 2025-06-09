#weapon

from ursina import Entity, Vec2, destroy, time, load_texture
import os


class Weapon(Entity):
    def __init__(self, player, groups=None):
        super().__init__(
            model='quad',
            texture=self._get_weapon_texture(player),
            position=Vec2(0, 0),
            scale=(1, 1),
            parent=player,
            z=-0.1
        )

        self.player = player
        self.sprite_type = 'weapon'
        self.attack_time = time.time()
        self.attack_duration = 0.3  # Синхронизируем с длительностью анимации атаки

        # Смещения оружия
        self.offset = {
            'right': Vec2(0.5, 0),
            'left': Vec2(-0.5, 0),
            'up': Vec2(0, 0.5),
            'down': Vec2(0, -0.5)
        }

        # Анимация оружия
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frames = self._load_animation_frames()
        self.update_position()

    def update(self):
        if time.time() - self.attack_time > self.attack_duration:
            destroy(self)
            return

        # Синхронизация с анимацией игрока
        if self.player.attacking and len(self.frames) > 1:
            self.frame_index = self.player.frame_index % len(self.frames)
            self.texture = self.frames[int(self.frame_index)]

        self.update_position()

    def update_position(self):
        direction = self.player.status.split('_')[0]
        self.position = self.offset.get(direction, Vec2(0, 0))