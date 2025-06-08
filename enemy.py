# enemy.py

from ursina import Entity, Vec2, time, destroy, color
import random
from helper.settings import *
from equip.chance import chance
from equip.item_base import artifacts
import os  # ← Добавь этот импорт


class Enemy(Entity):
    def __init__(self, monster_name, position, groups=None, obstacle_sprites=None,
                 damage_player=None, trigger_death_particles=None, add_exp=None, drops=None):
        super().__init__(
            model='quad',
            texture=self.get_texture(monster_name, 'idle'),
            position=Vec2(position[0], position[1]),
            z=-1,
            collider='box'
        )

        # Графика и статус
        self.monster_name = monster_name
        self.status = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.15

        # Движение
        self.direction = Vec2(0, 0)
        self.speed = 100  # пикселей в секунду
        self.obstacle_sprites = obstacle_sprites

        # Статы
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.damage = monster_info['damage']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']

        # Взаимодействие с игроком
        self.can_attack = True
        self.attack_time = 0
        self.attack_cooldown = 0.4
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_exp = add_exp
        self.drops = drops

        # Уязвимость
        self.vulnerable = True
        self.hit_time = 0
        self.invincibility_duration = 0.3

        # Анимации
        self.import_graphics(monster_name)

    def get_texture(self, monster_name, status):
        return f'graphics/monsters/{monster_name}/{status}/0.png'

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'attack': []}
        for animation in self.animations:
            folder_path = f'graphics/monsters/{name}/{animation}'
            frames_count = len(os.listdir(folder_path))
            self.animations[animation] = [
                Animation(f'{folder_path}/{i}', autoplay=False, loop=False, fps=12, scale=1, enabled=False)
                for i in range(frames_count)
            ]