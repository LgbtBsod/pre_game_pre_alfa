# enemy.py
from ursina import Vec2, time, destroy, Animation
import random
from helper.settings import MONSTER_DATA

import os
from player.base_player import BasePlayer  # Импортируем базовый класс

class Enemy(BasePlayer):  # Наследуем от BasePlayer
    def __init__(self, name, position, groups, obstacle_sprites, 
                        damage_player, death_callback, add_exp, drops):
        # Инициализация базового класса
        super().__init__(
            position=position,
            groups=groups,
            obstacle_sprites=obstacle_sprites
        )
        
        # Уникальные свойства врага
        self.name = name
        self.damage_player = damage_player
        self.trigger_death_particles = death_callback
        self.add_exp = add_exp
        self.drops = drops
        self.animations = {}
        # Переопределяем текстуру для врага
        self.texture = self.get_texture(name, 'idle')
        
        # Статы монстра из MONSTER_DATA
        monster_info = MONSTER_DATA[self.name]
        self.base_stats = {
            'health': monster_info['health'],
            'attack': monster_info['damage'],
            'speed': monster_info.get('speed', 1),
            # Добавляем другие необходимые статы
        }
        self.current_stats = self.base_stats.copy()
        
        # Радиусы атаки и обнаружения
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']
        
        # Настройки атаки
        self.can_attack = True
        self.attack_time = 0
        self.attack_cooldown = 0.4
        
        # Загрузка анимаций
        self.import_graphics(name)
        self.status = 'idle'
        self.animation_speed = 0.15
        self.frame_index = 0

    def get_texture(self, name, status):
        return f'assets/graphics/monsters/{name}/{status}/0.png'

    def import_graphics(self, name):
        """Загрузка анимаций для врага"""
        self.animations = {'idle': [], 'move': [], 'attack': []}
        for animation in self.animations:
            folder_path = f'assets/graphics/monsters/{name}/{animation}'
            frames_count = len(os.listdir(folder_path))
            self.animations[animation] = [
                Animation(f'{folder_path}/{i}', autoplay=False, loop=False, fps=12, scale=1, enabled=False)
                for i in range(frames_count)
            ]

    def get_player_distance_direction(self, player):
        """Вычисляет расстояние и направление до игрока"""
        enemy_pos = Vec2(self.x, self.y)
        player_pos = Vec2(player.x, player.y)
        distance = (player_pos - enemy_pos).length()
        direction = (player_pos - enemy_pos).normalized() if distance > 0 else Vec2(0, 0)
        return distance, direction

    def get_status(self, player):
        """Обновляет статус врага на основе дистанции до игрока"""
        distance, direction = self.get_player_distance_direction(player)

        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
            return direction, True
        elif distance <= self.notice_radius:
            self.status = 'move'
            return direction, False
        else:
            self.status = 'idle'
            return Vec2(0, 0), False

    def cooldowns(self):
        current_time = time.time()

        if not self.can_attack and current_time - self.attack_time >= self.attack_cooldown:
            self.can_attack = True

        if not self.vulnerable and current_time - self.hurt_time >= self.invulnerability_duration:
            self.vulnerable = True

    def get_damage(self, player, attack_type):
        """Обработка получения урона"""
        if self.vulnerable:
            self.direction = self.get_player_distance_direction(player)[1]
            super().on_take_damage(player.get_full_weapon_damage(), attack_type)
            self.hurt_time = time.time()
            self.vulnerable = False

    def check_death(self):
        """Проверка смерти врага"""
        if self.current_stats['health'] <= 0:
            destroy(self)
            self.trigger_death_particles(self.position, self.name)
            item = random.choice(list(artifacts.keys()))
            self.add_exp(self.exp)
            self.drops(item)

    def update(self):
        """Обновление состояния врага"""
        if hasattr(self, 'parent') and self.parent:
            pass
        else:
            self.animate()
            self.move_towards_player(self.level.player)
            self.cooldowns()
            self.check_death()

    def move_towards_player(self, player):
        """Движение в сторону игрока"""
        direction, is_attacking = self.get_status(player)
        self.direction = direction
        
        if not is_attacking and self.status == 'move':
            self.position += self.direction * self.current_stats['speed'] * time.dt
        elif is_attacking:
            self.attack(player)

    def attack(self, player):
        """Атака игрока"""
        if self.can_attack:
            self.damage_player(self.current_stats['attack'], self.attack_type)
            self.can_attack = False
            self.attack_time = time.time()

    def animate(self):
        """Обновление анимации"""
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed * time.dt * 60

        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0

        animation[int(self.frame_index)].position = self.position
        animation[int(self.frame_index)].enabled = True
        self.texture = animation[int(self.frame_index)].texture