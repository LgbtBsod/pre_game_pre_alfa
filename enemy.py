# enemy.py

from ursina import Entity, Vec2, time, destroy, Animation
import random
from helper.settings import monster_data
from equip.chance import chance
from helper.support import convert_to_num
import os

class Enemy(Entity):
    def __init__(self, monster_name, position, groups=None, obstacle_sprites=None,
                 damage_player=None, trigger_death_particles=None, add_exp=None, drops=None):
        if groups is None:
            groups = []

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

        # Статы монстра
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.damage = monster_info['damage']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']

        # Атака
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

    def get_texture(self, name, status):
        return f'graphics/monsters/{name}/{status}/0.png'

    def import_graphics(self, name):
        """Загрузка анимаций"""
        self.animations = {'idle': [], 'move': [], 'attack': []}
        for animation in self.animations:
            folder_path = f'graphics/monsters/{name}/{animation}'
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

    def animate(self):
        """Обновляет кадр анимации"""
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed * time.dt * 60

        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0

        animation[int(self.frame_index)].position = self.position
        animation[int(self.frame_index)].enabled = True
        self.texture = animation[int(self.frame_index)].texture

    def cooldowns(self):
        current_time = time.time()

        if not self.can_attack and current_time - self.attack_time >= self.attack_cooldown:
            self.can_attack = True

        if not self.vulnerable and current_time - self.hit_time >= self.invincibility_duration:
            self.vulnerable = True

    def get_damage(self, player, attack_type):
        if self.vulnerable:
            self.direction = self.get_player_distance_direction(player)[1]
            self.health -= player.get_full_weapon_damage()
            self.hit_time = time.time()
            self.vulnerable = False

    def check_death(self):
        if self.health <= 0:
            destroy(self)
            self.trigger_death_particles(self.position, self.monster_name)
            item = random.choice(list(artifacts.keys()))
            self.add_exp(self.exp)
            self.drops(item)

    def hit_reaction(self):
        if not self.vulnerable:
            self.direction *= -1

    def update(self):
        if hasattr(self, 'parent') and self.parent:
            pass
        else:
            self.animate()
            self.move_towards_player(self.level.player)
            self.cooldowns()
            self.check_death()

    def move_towards_player(self, player):
        """Движение в сторону игрока"""
        self.direction = self.get_status(player)[0]
        self.position += self.direction * self.speed * time.dt