# player/player.py
from .base_player import BasePlayer
from helper.settings import WEAPON_DATA, MAGIC_DATA
from helper.support import import_folder, Animation
from ursina import Vec2, held_keys, time
import os
import random
from typing import Dict, List


class LikePlayer(BasePlayer):
    def __init__(self, position=(0, 0), groups=None, obstacle_sprites=None):
        super().__init__(
            position=position,
            groups=groups,
            obstacle_sprites=obstacle_sprites
        )

        # Инициализация характеристик
        self._init_stats()
        
        # Система уровней и опыта
        self.level = 1
        self.exp = 0
        self.exp_to_level = 1000
        self._init_upgrade_costs()
        
        # Система оружия
        self.weapon_index = 0
        self.weapon_cooldown = 0.2
        self.weapon_data = WEAPON_DATA
        self.weapon = list(WEAPON_DATA.keys())[self.weapon_index]
        
        # Система магии
        self.magic_index = 0
        self.magic_cooldown = 0.3
        self.magic_data = MAGIC_DATA
        self.magic = list(MAGIC_DATA.keys())[self.magic_index]
        
        # Анимации и графика
        self.status = 'down'
        self.animation_speed = 0.15
        self._init_animations()
        
        # Состояние игрока
        self.attacking = False
        self.attack_cooldown = 0
        self.last_attack_time = 0
        self.last_regen_time = time.time()

    def _init_stats(self):
        """Инициализация базовых характеристик"""
        self.base_stats = {
            'health': 150,
            'max_health': 150,
            'energy': 80,
            'max_energy': 80,
            'attack': 15,
            'magic': 4,
            'speed': 1,
            'strength': 3,
            'agility': 2,
            'stamina': 200,
            'hp_regen': 0.2,
            'mp_regen': 0.1,
            'crit_chance': 10,    # %
            'crit_rate': 1.2,     # множитель
            'defense': 5
        }
        self.current_stats = self.base_stats.copy()

    def _init_upgrade_costs(self):
        """Инициализация стоимости улучшений"""
        self.upgrade_cost = {
            'health': 100,
            'energy': 100,
            'attack': 150,
            'magic': 150,
            'speed': 200,
            'strength': 120,
            'agility': 120,
            'stamina': 80,
            'hp_regen': 150,
            'mp_regen': 150,
            'crit_chance': 200,
            'crit_rate': 250,
            'defense': 100
        }

    def _init_animations(self):
        """Загрузка анимаций игрока"""
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
            'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []
        }

        for animation in self.animations:
            folder_path = f'graphics/player/{animation}'
            if os.path.exists(folder_path):
                self.animations[animation] = import_folder(folder_path)
            else:
                print(f"Warning: Animation folder not found: {folder_path}")

    def input(self):
        """Обработка ввода игрока"""
        if not self.attacking:
            self._handle_movement_input()
            self._handle_attack_input()
            self._handle_magic_input()
            self._handle_weapon_switch()
            self._handle_magic_switch()

    def _handle_movement_input(self):
        """Обработка движения"""
        self.direction = Vec2(
            int(held_keys['d']) - int(held_keys['a']),
            int(held_keys['s']) - int(held_keys['w'])
        ).normalized() if any([
            held_keys['d'], held_keys['a'],
            held_keys['w'], held_keys['s']
        ]) else Vec2(0, 0)

    def _handle_attack_input(self):
        """Обработка атаки"""
        if held_keys['space'] and time.time() - self.last_attack_time > self.attack_cooldown:
            self.attacking = True
            self.last_attack_time = time.time()
            self.create_attack()
            self._trigger_attack_animation()

    def _handle_magic_input(self):
        """Обработка магии"""
        if held_keys['control left'] and self.current_stats['energy'] > 10:
            style = list(self.magic_data.keys())[self.magic_index]
            strength = self.magic_data[style]['strength'] + self.current_stats['magic']
            cost = self.magic_data[style]['cost']
            
            if self.current_stats['energy'] >= cost:
                self.create_magic(style, strength, cost)
                self.current_stats['energy'] -= cost
                self.attacking = True
                self.last_attack_time = time.time()

    def _handle_weapon_switch(self):
        """Переключение оружия"""
        if held_keys['q'] and time.time() - self.last_weapon_switch > self.weapon_cooldown:
            self.last_weapon_switch = time.time()
            self.weapon_index = (self.weapon_index + 1) % len(self.weapon_data)
            self.weapon = list(self.weapon_data.keys())[self.weapon_index]
            print(f"Switched to {self.weapon}")

    def _handle_magic_switch(self):
        """Переключение магии"""
        if held_keys['e'] and time.time() - self.last_magic_switch > self.magic_cooldown:
            self.last_magic_switch = time.time()
            self.magic_index = (self.magic_index + 1) % len(self.magic_data)
            self.magic = list(self.magic_data.keys())[self.magic_index]
            print(f"Switched to {self.magic}")

    def update(self):
        """Обновление состояния игрока"""
        super().update()
        self._handle_regen()
        self._update_animation()
        self._update_cooldowns()

    def _handle_regen(self):
        """Регенерация здоровья и маны"""
        current_time = time.time()
        if current_time - self.last_regen_time > 1.0:  # Раз в секунду
            self.last_regen_time = current_time
            
            # Регенерация здоровья
            if self.current_stats['health'] < self.current_stats['max_health']:
                self.current_stats['health'] = min(
                    self.current_stats['health'] + self.current_stats['hp_regen'],
                    self.current_stats['max_health']
                )
            
            # Регенерация энергии
            if self.current_stats['energy'] < self.current_stats['max_energy']:
                self.current_stats['energy'] = min(
                    self.current_stats['energy'] + self.current_stats['mp_regen'],
                    self.current_stats['max_energy']
                )

    def _update_animation(self):
        """Обновление анимации игрока"""
        if self.direction.x > 0:
            self.status = 'right'
        elif self.direction.x < 0:
            self.status = 'left'
        elif self.direction.y > 0:
            self.status = 'up'
        elif self.direction.y < 0:
            self.status = 'down'

        if self.attacking:
            self.status += '_attack'
        elif self.direction == Vec2(0, 0):
            self.status += '_idle'

        # Здесь должна быть логика смены кадров анимации
        # Например: self.frame_index += self.animation_speed * time.dt

    def _update_cooldowns(self):
        """Обновление времени перезарядки"""
        if self.attacking and time.time() - self.last_attack_time > self.attack_cooldown:
            self.attacking = False

    def get_damage(self, attack_type='physical') -> float:
        """Расчёт урона с учётом критов"""
        base_damage = self.current_stats['attack']
        weapon_bonus = self.weapon_data[self.weapon]['damage']
        
        total_damage = base_damage * weapon_bonus
        
        # Проверка на крит
        if random.random() * 100 < self.current_stats['crit_chance']:
            total_damage *= self.current_stats['crit_rate']
            print(f'CRITICAL HIT! {total_damage:.1f} damage')
            return total_damage
        
        return total_damage

    def get_magic_damage(self) -> float:
        """Расчёт магического урона"""
        base_damage = self.current_stats['magic']
        spell_damage = self.magic_data[self.magic]['strength']
        return base_damage * spell_damage

    def take_damage(self, amount: float):
        """Получение урона с учётом защиты"""
        defense_factor = max(0, 1 - self.current_stats['defense'] / 100)
        actual_damage = amount * defense_factor
        self.current_stats['health'] = max(0, self.current_stats['health'] - actual_damage)
        
        if self.current_stats['health'] <= 0:
            self.die()

    def die(self):
        """Обработка смерти игрока"""
        print("Player died!")
        # Здесь может быть анимация смерти, респавн и т.д.
        self.current_stats['health'] = self.current_stats['max_health'] * 0.3  # Частичное восстановление

    def gain_exp(self, amount: int):
        """Получение опыта и повышение уровня"""
        self.exp += amount
        while self.exp >= self.exp_to_level:
            self.exp -= self.exp_to_level
            self.level_up()
    
    def level_up(self):
        """Повышение уровня"""
        self.level += 1
        self.exp_to_level = int(self.exp_to_level * 1.2)
        print(f"Level up! Now level {self.level}")
        
        # Улучшение базовых характеристик
        for stat in ['max_health', 'max_energy', 'attack', 'defense']:
            self.base_stats[stat] = int(self.base_stats[stat] * 1.1)
        
        # Восстановление при повышении уровня
        self.current_stats['health'] = self.base_stats['max_health']
        self.current_stats['energy'] = self.base_stats['max_energy']

    def upgrade_stat(self, stat: str):
        """Улучшение характеристики"""
        if stat in self.base_stats and self.exp >= self.upgrade_cost[stat]:
            self.exp -= self.upgrade_cost[stat]
            self.base_stats[stat] = int(self.base_stats[stat] * 1.1)
            self.upgrade_cost[stat] = int(self.upgrade_cost[stat] * 1.5)
            self.current_stats = self.base_stats.copy()
            return True
        return False

    def create_magic(self, style: str, strength: float, cost: float):
        """Создание магического эффекта"""
        print(f'Casting {style} magic with power {strength} (cost: {cost} MP)')
        # Здесь должна быть логика создания визуального эффекта магии
        # Например: MagicProjectile.create(style=style, power=strength)