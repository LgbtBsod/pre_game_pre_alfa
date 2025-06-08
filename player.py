# player.py

from ursina import Entity, Vec2, time, destroy, held_keys, Animation 
from helper.settings import *
from helper.support import import_folder, convert_to_num
from equip.chance import chance
import os

class Player(Entity):
    def __init__(self, position=(0, 0), groups=None, obstacle_sprites=None,
                 create_attack=None, destroy_attack=None, create_magic=None):
        super().__init__(
            model='quad',
            texture='graphics/player/down_idle/down.png',
            position=Vec2(position[0], position[1]),
            z=-1,
            collider='box'
        )

        # Добавлено для работы с UI
        self.weapon_index = 0
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 0.2
        
        # Графика
        self.import_player_assets()
        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15

        # Движение
        self.direction = Vec2(0, 0)
        self.speed = 200  # пикселей в секунду
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
            'agility': 10,
            'stamina': 500,
            'hp_regen': 0.5,
            'crit_chance': 30,
            'crit_rate': 250
        }

        self.upgrade_cost = {stat: 100 for stat in self.base}

        self.health = self.current_stats['health']
        self.energy = self.current_stats['energy']
        self.exp = 900000000
        self.strength = self.current_stats['strength']
        self.agility = self.current_stats['agility']
        self.stamina = self.current_stats['stamina']
        self.power = self.current_stats['magic']
        self.hp_regen = self.current_stats['hp_regen']
        self.crit_rate = self.current_stats['crit_rate']
        self.crit_chance = self.current_stats['crit_chance']

        self.speed = self.current_stats['speed'] * self.current_stats['agility']

        # Атака
        self.attacking = False
        self.attack_cooldown = 0.4
        self.attack_time = 0
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack

        # Магия
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = 0
        self.switch_duration_cooldown = 0.2

        # Уязвимость
        self.vulnerable = True
        self.hurt_time = 0
        self.invulnerability_duration = 0.5

    def import_player_assets(self):
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
            'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []
        }

        for animation in self.animations:
            folder_path = f'graphics/player/{animation}'
            frames_count = len(os.listdir(folder_path))
            self.animations[animation] = [
                Animation(f'{folder_path}/{i}', autoplay=False, loop=False, fps=12, scale=1, enabled=False)
                for i in range(frames_count)
            ]

    def input(self):
        if not self.attacking:
            self.direction = Vec2(
                int(held_keys['d']) - int(held_keys['a']),
                int(held_keys['s']) - int(held_keys['w'])
            )

            if self.direction.length() > 0:
                self.direction = self.direction.normalized()

            if self.direction.x == 0 and self.direction.y == 0:
                if 'idle' not in self.status and not 'attack' in self.status:
                    if 'attack' in self.status:
                        self.status = self.status.replace('_attack', '_idle')
                    else:
                        self.status += '_idle'

            elif 'idle' in self.status or 'attack' in self.status:
                self.status = self.status.replace('_idle', '').replace('_attack', '')

            if held_keys['space']:
                self.attacking = True
                self.attack_time = time.time()
                self.create_attack()

            if held_keys['control left']:
                self.attacking = True
                self.attack_time = time.time()
                style = list(magic_data.keys())[self.magic_index]
                strength = list(magic_data.values())[self.magic_index]['strength'] + self.current_stats['magic']
                cost = list(magic_data.values())[self.magic_index]['cost']
                self.create_magic(style, strength, cost)

            if held_keys['q'] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = time.time()
                self.weapon_index = (self.weapon_index + 1) % len(weapon_data)
                self.weapon = list(weapon_data.keys())[self.weapon_index]

            if held_keys['e'] and self.can_switch_magic:
                self.can_switch_magic = False
                self.magic_switch_time = time.time()
                self.magic_index = (self.magic_index + 1) % len(magic_data)
                self.magic = list(magic_data.keys())[self.magic_index]

    def get_status(self):
        pass  # Обработано в input()

    def cooldowns(self):
        current_time = time.time()

        if self.attacking and current_time - self.attack_time >= self.attack_cooldown:
            self.attacking = False
            self.destroy_attack()

        if not self.can_switch_weapon and current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
            self.can_switch_weapon = True

        if not self.can_switch_magic and current_time - self.magic_switch_time >= self.switch_duration_cooldown:
            self.can_switch_magic = True

        if not self.vulnerable and current_time - self.hurt_time >= self.invulnerability_duration:
            self.vulnerable = True

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed * time.dt * 60

        if self.frame_index >= len(animation):
            self.frame_index = 0

        for anim in animation:
            anim.enabled = False
        animation[int(self.frame_index)].enabled = True
        self.texture = animation[int(self.frame_index)].texture

    def move(self):
        self.position += self.direction * self.speed * time.dt

    def get_full_weapon_damage(self):
        weapon_damage = weapon_data[self.weapon]['damage']
        damage = weapon_damage * self.current_stats['strength']

        if chance(self.current_stats['crit_chance']):
            modify = convert_to_num(self.current_stats['crit_rate'])
            print('Crit!', damage * modify)
            return damage * modify
        else:
            return damage

    def get_full_magic_damage(self):
        base_damage = self.current_stats['magic']
        spell_damage = magic_data[self.magic]['strength']
        return spell_damage * self.power

    def energy_recovery(self):
        if self.energy < self.current_stats['energy']:
            self.energy += 0.01 * self.current_stats['magic']
        else:
            self.energy = self.current_stats['energy']

    def hp_recovery(self):
        if self.health < self.current_stats['health']:
            self.health += 0.1 * self.current_stats['hp_regen']
        else:
            self.health = self.current_stats['health']

    def update(self):
        self.input()
        self.cooldowns()
        self.animate()
        self.move()
        self.energy_recovery()
        self.hp_recovery()

        # Камера следует за игроком
        camera.position = self.position + (0, 0, -20)