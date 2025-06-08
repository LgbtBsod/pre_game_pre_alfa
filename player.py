# player.py

from ursina import Entity, Vec2, time, destroy, held_keys, Animation
from helper.settings import *
from entity import EntityBase
from helper.support import import_folder
from equip.chance import chance
import math


class Player(EntityBase):
    def __init__(self, position=(0, 0), groups=None, obstacle_sprites=None,
                 create_attack=None, destroy_attack=None, create_magic=None):
        super().__init__(model='quad', texture='graphics/player/down_idle/down.png',
                         position=Vec2(position[0], position[1]), z=-1)

        # Графика
        self.import_player_assets()
        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15

        # Движение
        self.direction = Vec2(0, 0)
        self.speed = 200  # pixels per second
        self.obstacle_sprites = obstacle_sprites

        # Статы
        self.base = {
            'health': 100,
            'energy': 60,
            'attack': 0,
            'magic': 2,
            'speed': 1,
            'strength': 2,
            'agility': 2,
            'stamina': 200,
            'hp_regen': 0.1,
            'crit_chance': 10,
            'crit_rate': 120
        }

        self.current_stats = self.base.copy()
        self.max_stats = {
            'health': 300,
            'energy': 140,
            'attack': 20,
            'magic': 10,
            'speed': 10,
            'strength': 10,
            'agility':