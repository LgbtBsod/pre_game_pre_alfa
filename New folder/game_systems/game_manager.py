#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from direct.task import Task

class GameManager:
    """Менеджер игровой логики"""
    
    def __init__(self, game):
        self.game = game
        self.player = None
        self.enemies = []
        self.game_time = 0
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 3.0
        self.max_enemies = 10
        self.saved_state = None
        self.is_paused = False
        
    def set_player(self, player):
        """Установка игрока"""
        self.player = player
        
    def spawn_enemy(self, enemy_type="basic"):
        """Спавн врага"""
        if len(self.enemies) >= self.max_enemies:
            return
            
        # Случайная позиция вокруг игрока
        spawn_distance = 150
        angle = random.uniform(0, 360)
        x = self.player.x + spawn_distance * random.uniform(-1, 1)
        y = self.player.y + spawn_distance * random.uniform(-1, 1)
        z = 1
        
        from enemy import Enemy
        enemy = Enemy(self.game, x, y, z, enemy_type)
        enemy.create_visual()
        self.enemies.append(enemy)
        
    def update(self, dt):
        """Обновление игровой логики"""
        if not self.player or not self.player.is_alive():
            return
            
        self.game_time += dt
        
        # Спавн врагов
        self.enemy_spawn_timer += dt
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.spawn_enemy()
            self.enemy_spawn_timer = 0
            
        # Обновление врагов
        for enemy in self.enemies[:]:  # Копия списка для безопасного удаления
            if enemy.is_alive():
                enemy.update_ai(self.player, dt)
            else:
                enemy.destroy()
                self.enemies.remove(enemy)
                
        # Обновление игрока
        self.player.update_cooldown(dt)
        
    def save_state(self):
        """Сохранение состояния игры"""
        if not self.player:
            return
            
        self.saved_state = {
            'player': {
                'x': self.player.x,
                'y': self.player.y,
                'z': self.player.z,
                'health': self.player.health,
                'max_health': self.player.max_health,
                'mana': self.player.mana,
                'max_mana': self.player.max_mana,
                'stamina': self.player.stamina,
                'max_stamina': self.player.max_stamina,
                'attack_cooldown': self.player.attack_cooldown
            },
            'enemies': [],
            'game_time': self.game_time
        }
        
        # Сохраняем состояние врагов
        for enemy in self.enemies:
            if enemy.is_alive():
                self.saved_state['enemies'].append({
                    'x': enemy.x,
                    'y': enemy.y,
                    'z': enemy.z,
                    'health': enemy.health,
                    'max_health': enemy.max_health,
                    'attack_cooldown': enemy.attack_cooldown,
                    'type': enemy.enemy_type
                })
    
    def restore_state(self):
        """Восстановление состояния игры"""
        if not self.saved_state:
            return
            
        # Восстанавливаем игрока
        if self.player and 'player' in self.saved_state:
            player_state = self.saved_state['player']
            self.player.x = player_state['x']
            self.player.y = player_state['y']
            self.player.z = player_state['z']
            self.player.health = player_state['health']
            self.player.max_health = player_state['max_health']
            self.player.mana = player_state['mana']
            self.player.max_mana = player_state['max_mana']
            self.player.stamina = player_state['stamina']
            self.player.max_stamina = player_state['max_stamina']
            self.player.attack_cooldown = player_state['attack_cooldown']
            
            # Обновляем позицию визуального представления
            if self.player.node:
                self.player.node.setPos(self.player.x, self.player.y, self.player.z)
        
        # Восстанавливаем врагов
        if 'enemies' in self.saved_state:
            for enemy_state in self.saved_state['enemies']:
                from enemy import Enemy
                enemy = Enemy(self.game, enemy_state['x'], enemy_state['y'], enemy_state['z'], enemy_state['type'])
                enemy.health = enemy_state['health']
                enemy.max_health = enemy_state['max_health']
                enemy.attack_cooldown = enemy_state['attack_cooldown']
                enemy.create_visual()
                self.enemies.append(enemy)
        
        # Восстанавливаем игровое время
        self.game_time = self.saved_state.get('game_time', 0)
        
    def clear_state(self):
        """Очистка сохраненного состояния"""
        self.saved_state = None
        self.is_paused = False
        
    def cleanup(self):
        """Очистка ресурсов"""
        for enemy in self.enemies:
            enemy.destroy()
        self.enemies.clear()
        self.player = None
