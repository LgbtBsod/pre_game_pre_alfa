#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
УНИФИЦИРОВАННЫЙ КЛАСС ВРАГА
Объединяет функционал enemy.py и game_objects/enemy.py
Наследуется от Character для единообразия
"""

import math
import random
from typing import Dict, List, Optional, Any, Tuple
from panda3d.core import CardMaker, Vec3, Vec4, TransparencyAttrib
from character import Character

class Enemy(Character):
    """Класс врага"""
    
    def __init__(self, game, x=0, y=0, z=0, enemy_type="basic", generated_data=None):
        # Цвета для разных типов врагов
        colors = {
            "basic": (0.8, 0.2, 0.2, 1),      # Красный
            "boss": (0.8, 0.8, 0.2, 1),       # Желтый
            "chimera": (0.8, 0.2, 0.8, 1)     # Фиолетовый
        }
        
        super().__init__(game, x, y, z, colors.get(enemy_type, colors["basic"]))
        self.enemy_type = enemy_type
        self.generated_data = generated_data  # Данные из генератора контента
        
        # Инициализация ИИ и обучения
        self.ai_learning_rate = self._get_learning_rate()
        self.learning_patterns = []
        self.combat_experience = 0
        self.phase = 1
        self.max_phases = 1
        
        self.setup_enemy_stats()
        self._initialize_ai_memory()
        
        # Инициализация инвентаря для врага
        self.inventory_id = f"enemy_{id(self)}"
        if hasattr(game, 'item_system'):
            game.item_system.create_inventory(self.inventory_id, max_slots=20, max_weight=50.0)
    
    def create_visual(self):
        """Совместимость с GameManager: обёртка для создания визуала"""
        return self.create_character()
    
    # === МЕТОДЫ ПРЕПЯТСТВОВАНИЯ ИГРОКУ ===
    
    def detect_player_near_lighthouse(self, player_position: Tuple[float, float, float]) -> bool:
        """Обнаружение игрока рядом с маяком"""
        if hasattr(self.game, 'lighthouse_system') and self.game.lighthouse_system.active_lighthouse:
            # Получаем позицию маяка
            lighthouse_pos = (
                self.game.lighthouse_system.active_lighthouse.location.x,
                self.game.lighthouse_system.active_lighthouse.location.y,
                self.game.lighthouse_system.active_lighthouse.location.z
            )
            
            # Вычисляем расстояние от игрока до маяка
            dx = player_position[0] - lighthouse_pos[0]
            dy = player_position[1] - lighthouse_pos[1]
            dz = player_position[2] - lighthouse_pos[2]
            distance_to_lighthouse = (dx*dx + dy*dy + dz*dz) ** 0.5
            
            # Вычисляем расстояние от врага до маяка
            enemy_dx = self.x - lighthouse_pos[0]
            enemy_dy = self.y - lighthouse_pos[1]
            enemy_dz = self.z - lighthouse_pos[2]
            enemy_distance_to_lighthouse = (enemy_dx*enemy_dx + enemy_dy*enemy_dy + enemy_dz*enemy_dz) ** 0.5
            
            # Враг обнаруживает игрока, если игрок близко к маяку, а враг тоже в зоне маяка
            detection_range = 150.0  # Радиус обнаружения
            return (distance_to_lighthouse < detection_range and 
                   enemy_distance_to_lighthouse < detection_range)
        
        return False
    
    def move_to_intercept_player(self, player_position: Tuple[float, float, float]) -> bool:
        """Движение к игроку для препятствования"""
        if hasattr(self.game, 'lighthouse_system') and self.game.lighthouse_system.active_lighthouse:
            # Получаем позицию маяка
            lighthouse_pos = (
                self.game.lighthouse_system.active_lighthouse.location.x,
                self.game.lighthouse_system.active_lighthouse.location.y,
                self.game.lighthouse_system.active_lighthouse.location.z
            )
            
            # Вычисляем расстояние до маяка
            dx = self.x - lighthouse_pos[0]
            dy = self.y - lighthouse_pos[1]
            dz = self.z - lighthouse_pos[2]
            distance_to_lighthouse = (dx*dx + dy*dy + dz*dz) ** 0.5
            
            # Если враг далеко от маяка, движется к маяку
            if distance_to_lighthouse > 200.0:
                # Движение к маяку
                move_speed = 2.0
                direction_x = (lighthouse_pos[0] - self.x) / distance_to_lighthouse
                direction_y = (lighthouse_pos[1] - self.y) / distance_to_lighthouse
                
                self.x += direction_x * move_speed
                self.y += direction_y * move_speed
                
                # Записываем в память ИИ
                if hasattr(self, 'entity_id') and hasattr(self.game, 'ai_memory_system'):
                    self.game.ai_memory_system.add_memory(
                        self.entity_id, "lighthouse_intercept", {
                            "action": "move_to_lighthouse",
                            "distance": distance_to_lighthouse
                        }, 0.7
                    )
                
                return True
            
            # Если враг близко к маяку, пытается перехватить игрока
            elif distance_to_lighthouse <= 200.0:
                # Вычисляем расстояние до игрока
                player_dx = player_position[0] - self.x
                player_dy = player_position[1] - self.y
                player_dz = player_position[2] - self.z
                distance_to_player = (player_dx*player_dx + player_dy*player_dy + player_dz*player_dz) ** 0.5
                
                if distance_to_player > 10.0:  # Если не вплотную к игроку
                    # Движение к игроку
                    move_speed = 1.5
                    direction_x = player_dx / distance_to_player
                    direction_y = player_dy / distance_to_player
                    
                    self.x += direction_x * move_speed
                    self.y += direction_y * move_speed
                    
                    # Записываем в память ИИ
                    if hasattr(self, 'entity_id') and hasattr(self.game, 'ai_memory_system'):
                        self.game.ai_memory_system.add_memory(
                            self.entity_id, "lighthouse_intercept", {
                                "action": "intercept_player",
                                "player_distance": distance_to_player,
                                "lighthouse_distance": distance_to_lighthouse
                            }, 0.8
                        )
                    
                    return True
        
        return False
    
    def block_lighthouse_access(self, player_position: Tuple[float, float, float]) -> bool:
        """Блокировка доступа к маяку"""
        if hasattr(self.game, 'lighthouse_system') and self.game.lighthouse_system.active_lighthouse:
            # Получаем позицию маяка
            lighthouse_pos = (
                self.game.lighthouse_system.active_lighthouse.location.x,
                self.game.lighthouse_system.active_lighthouse.location.y,
                self.game.lighthouse_system.active_lighthouse.location.z
            )
            
            # Вычисляем расстояние до маяка
            dx = self.x - lighthouse_pos[0]
            dy = self.y - lighthouse_pos[1]
            dz = self.z - lighthouse_pos[2]
            distance_to_lighthouse = (dx*dx + dy*dy + dz*dz) ** 0.5
            
            # Вычисляем расстояние до игрока
            player_dx = player_position[0] - self.x
            player_dy = player_position[1] - self.y
            player_dz = player_position[2] - self.z
            distance_to_player = (player_dx*player_dx + player_dy*player_dy + player_dz*player_dz) ** 0.5
            
            # Блокируем доступ, если враг между игроком и маяком
            if (distance_to_lighthouse < 50.0 and distance_to_player < 30.0):
                # Позиционируемся между игроком и маяком
                block_distance = 15.0
                direction_x = (lighthouse_pos[0] - player_position[0])
                direction_y = (lighthouse_pos[1] - player_position[1])
                direction_length = (direction_x*direction_x + direction_y*direction_y) ** 0.5
                
                if direction_length > 0:
                    direction_x /= direction_length
                    direction_y /= direction_length
                    
                    # Позиционируемся на пути к маяку
                    target_x = player_position[0] + direction_x * block_distance
                    target_y = player_position[1] + direction_y * block_distance
                    
                    # Плавное движение к позиции блокировки
                    move_speed = 1.0
                    self.x += (target_x - self.x) * move_speed * 0.1
                    self.y += (target_y - self.y) * move_speed * 0.1
                    
                    # Записываем в память ИИ
                    if hasattr(self, 'entity_id') and hasattr(self.game, 'ai_memory_system'):
                        self.game.ai_memory_system.add_memory(
                            self.entity_id, "lighthouse_block", {
                                "action": "block_access",
                                "player_distance": distance_to_player,
                                "lighthouse_distance": distance_to_lighthouse
                            }, 0.9
                        )
                    
                    return True
        
        return False
    
    def attack_player_near_lighthouse(self, player_position: Tuple[float, float, float]) -> bool:
        """Атака игрока рядом с маяком"""
        if hasattr(self.game, 'lighthouse_system') and self.game.lighthouse_system.active_lighthouse:
            # Получаем позицию маяка
            lighthouse_pos = (
                self.game.lighthouse_system.active_lighthouse.location.x,
                self.game.lighthouse_system.active_lighthouse.location.y,
                self.game.lighthouse_system.active_lighthouse.location.z
            )
            
            # Вычисляем расстояние до маяка
            dx = self.x - lighthouse_pos[0]
            dy = self.y - lighthouse_pos[1]
            dz = self.z - lighthouse_pos[2]
            distance_to_lighthouse = (dx*dx + dy*dy + dz*dz) ** 0.5
            
            # Вычисляем расстояние до игрока
            player_dx = player_position[0] - self.x
            player_dy = player_position[1] - self.y
            player_dz = player_position[2] - self.z
            distance_to_player = (player_dx*player_dx + player_dy*player_dy + player_dz*player_dz) ** 0.5
            
            # Атакуем, если близко к маяку и к игроку
            if (distance_to_lighthouse < 100.0 and distance_to_player < 20.0):
                # Выполняем атаку
                attack_damage = self.get_attack_damage()
                
                # Записываем в память ИИ
                if hasattr(self, 'entity_id') and hasattr(self.game, 'ai_memory_system'):
                    self.game.ai_memory_system.add_memory(
                        self.entity_id, "lighthouse_attack", {
                            "action": "attack_player",
                            "damage": attack_damage,
                            "player_distance": distance_to_player,
                            "lighthouse_distance": distance_to_lighthouse
                        }, 1.0
                    )
                
                return True
        
        return False
        
    def setup_enemy_stats(self):
        """Настройка характеристик врага в зависимости от типа"""
        from systems.attributes import AttributeSet
        
        if self.enemy_type == "basic":
            self.base_attributes = AttributeSet(
                strength=8.0, agility=6.0, intelligence=4.0, vitality=10.0,
                wisdom=5.0, charisma=3.0, luck=5.0, endurance=8.0
            )
        elif self.enemy_type == "boss":
            self.base_attributes = AttributeSet(
                strength=20.0, agility=8.0, intelligence=10.0, vitality=30.0,
                wisdom=8.0, charisma=5.0, luck=6.0, endurance=15.0
            )
        elif self.enemy_type == "chimera":
            self.base_attributes = AttributeSet(
                strength=15.0, agility=10.0, intelligence=8.0, vitality=20.0,
                wisdom=7.0, charisma=4.0, luck=7.0, endurance=12.0
            )
        
        # Обновляем характеристики на основе атрибутов
        self._update_derived_stats()
        
        # Устанавливаем текущие значения
        self.health = self.max_health
        self.mana = self.max_mana
        self.stamina = self.max_stamina
            
    def create_character(self):
        """Создание визуального представления врага"""
        from panda3d.core import CardMaker
        
        # Создаем врага как простую пирамиду
        enemy = self.game.render.attachNewNode("enemy")
        
        # Основание пирамиды
        self.create_visible_cube(enemy, "enemy_base", 0, 0, 0.2, 0.8, 0.8, 0.8, self.color)
        
        # Верхняя часть пирамиды
        top_color = (self.color[0] * 1.2, self.color[1] * 1.2, self.color[2] * 1.2, self.color[3])
        self.create_visible_cube(enemy, "enemy_top", 0, 0, 0.8, 0.4, 0.4, 0.4, top_color)
        
        # Добавляем глаза для врага
        cm = CardMaker("eye1")
        cm.setFrame(-0.05, 0.05, -0.05, 0.05)
        eye1 = enemy.attachNewNode(cm.generate())
        eye1.setPos(-0.2, 0.4, 0.6)
        eye1.setColor(1, 1, 1, 1)
        
        cm = CardMaker("eye2")
        cm.setFrame(-0.05, 0.05, -0.05, 0.05)
        eye2 = enemy.attachNewNode(cm.generate())
        eye2.setPos(0.2, 0.4, 0.6)
        eye2.setColor(1, 1, 1, 1)
        
        enemy.setPos(self.x, self.y, self.z)
        self.node = enemy
        return enemy
        
    def create_visible_cube(self, parent, name, x, y, z, width, height, depth, color):
        """Создание видимого куба с правильной ориентацией"""
        from panda3d.core import CardMaker
        
        # Создаем куб из 6 граней с правильной ориентацией
        cube = parent.attachNewNode(name)
        
        # Передняя грань (обращена к камере)
        cm = CardMaker(f"{name}_front")
        cm.setFrame(-width/2, width/2, -height/2, height/2)
        front = cube.attachNewNode(cm.generate())
        front.setPos(0, depth/2, 0)
        front.setColor(*color)
        
        # Задняя грань
        cm = CardMaker(f"{name}_back")
        cm.setFrame(-width/2, width/2, -height/2, height/2)
        back = cube.attachNewNode(cm.generate())
        back.setPos(0, -depth/2, 0)
        back.setHpr(0, 180, 0)
        back.setColor(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, color[3])
        
        # Левая грань
        cm = CardMaker(f"{name}_left")
        cm.setFrame(-depth/2, depth/2, -height/2, height/2)
        left = cube.attachNewNode(cm.generate())
        left.setPos(-width/2, 0, 0)
        left.setHpr(0, -90, 0)
        left.setColor(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8, color[3])
        
        # Правая грань
        cm = CardMaker(f"{name}_right")
        cm.setFrame(-depth/2, depth/2, -height/2, height/2)
        right = cube.attachNewNode(cm.generate())
        right.setPos(width/2, 0, 0)
        right.setHpr(0, 90, 0)
        right.setColor(color[0] * 0.6, color[1] * 0.6, color[2] * 0.6, color[3])
        
        # Верхняя грань
        cm = CardMaker(f"{name}_top")
        cm.setFrame(-width/2, width/2, -depth/2, depth/2)
        top = cube.attachNewNode(cm.generate())
        top.setPos(0, 0, height/2)
        top.setHpr(0, 0, -90)
        top.setColor(color[0] * 1.2, color[1] * 1.2, color[2] * 1.2, color[3])
        
        # Нижняя грань
        cm = CardMaker(f"{name}_bottom")
        cm.setFrame(-width/2, width/2, -depth/2, depth/2)
        bottom = cube.attachNewNode(cm.generate())
        bottom.setPos(0, 0, -height/2)
        bottom.setHpr(0, 0, 90)
        bottom.setColor(color[0] * 0.4, color[1] * 0.4, color[2] * 0.4, color[3])
        
        cube.setPos(x, y, z)
        return cube
        
    def create_simple_cube(self, parent, name, x, y, z, width, height, depth, color):
        """Создание простого куба"""
        from panda3d.core import CardMaker
        
        # Создаем куб из 6 граней
        cube = parent.attachNewNode(name)
        
        # Передняя грань
        cm = CardMaker(f"{name}_front")
        cm.setFrame(-width/2, width/2, -height/2, height/2)
        front = cube.attachNewNode(cm.generate())
        front.setPos(0, depth/2, 0)
        front.setColor(*color)
        
        # Задняя грань
        cm = CardMaker(f"{name}_back")
        cm.setFrame(-width/2, width/2, -height/2, height/2)
        back = cube.attachNewNode(cm.generate())
        back.setPos(0, -depth/2, 0)
        back.setHpr(0, 180, 0)
        back.setColor(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, color[3])
        
        # Левая грань
        cm = CardMaker(f"{name}_left")
        cm.setFrame(-depth/2, depth/2, -height/2, height/2)
        left = cube.attachNewNode(cm.generate())
        left.setPos(-width/2, 0, 0)
        left.setHpr(0, -90, 0)
        left.setColor(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8, color[3])
        
        # Правая грань
        cm = CardMaker(f"{name}_right")
        cm.setFrame(-depth/2, depth/2, -height/2, height/2)
        right = cube.attachNewNode(cm.generate())
        right.setPos(width/2, 0, 0)
        right.setHpr(0, 90, 0)
        right.setColor(color[0] * 0.6, color[1] * 0.6, color[2] * 0.6, color[3])
        
        # Верхняя грань
        cm = CardMaker(f"{name}_top")
        cm.setFrame(-width/2, width/2, -depth/2, depth/2)
        top = cube.attachNewNode(cm.generate())
        top.setPos(0, 0, height/2)
        top.setHpr(0, 0, -90)
        top.setColor(color[0] * 1.2, color[1] * 1.2, color[2] * 1.2, color[3])
        
        # Нижняя грань
        cm = CardMaker(f"{name}_bottom")
        cm.setFrame(-width/2, width/2, -depth/2, depth/2)
        bottom = cube.attachNewNode(cm.generate())
        bottom.setPos(0, 0, -height/2)
        bottom.setHpr(0, 0, 90)
        bottom.setColor(color[0] * 0.4, color[1] * 0.4, color[2] * 0.4, color[3])
        
        cube.setPos(x, y, z)
        return cube
        
    def create_cube_face(self, parent, name, x1, x2, y1, y2, px, py, pz, h, p, r, color):
        """Создание грани куба"""
        from panda3d.core import CardMaker
        cm = CardMaker(name)
        cm.setFrame(x1, x2, y1, y2)
        face = parent.attachNewNode(cm.generate())
        face.setPos(px, py, pz)
        face.setHpr(h, p, r)
        face.setColor(*color)
        return face
        
    def move_towards_player(self, player_x, player_y):
        """Движение к игроку"""
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0.1:  # Если не слишком близко
            # Нормализуем направление
            dx /= distance
            dy /= distance
            
            # Используем новый метод move_by с фиксированным dt
            dt = 0.016  # 60 FPS
            self.move_by(dx, dy, 0, dt)
            
    def attack_player(self, player):
        """Атака игрока"""
        if player and player.is_alive():
            damage = player.take_damage(self.physical_damage, "physical")
            
            # Записываем опыт боя для обучения
            self._record_combat_experience("attack", player, damage)
            return damage
        return False
    
    def _get_learning_rate(self):
        """Получение скорости обучения в зависимости от типа врага"""
        learning_rates = {
            "basic": 0.05,    # Низкая скорость обучения для обычных врагов
            "boss": 0.01,     # Минимальная для боссов
            "chimera": 0.02   # Средняя для химер
        }
        return learning_rates.get(self.enemy_type, 0.05)
    
    def _initialize_ai_memory(self):
        """Инициализация памяти ИИ для врага"""
        if hasattr(self.game, 'ai_memory_system'):
            from core.enhanced_ai_memory import EntityType
            import time
            entity_id = f"{self.enemy_type}_{int(time.time() * 1000)}"
            
            # Определяем тип сущности
            entity_type_map = {
                "basic": EntityType.BASIC_ENEMY,
                "boss": EntityType.BOSS,
                "chimera": EntityType.CHIMERA
            }
            
            entity_type = entity_type_map.get(self.enemy_type, EntityType.BASIC_ENEMY)
            self.game.ai_memory_system.initialize_entity_memory(entity_id, entity_type)
            self.entity_id = entity_id
    
    def _record_combat_experience(self, action_type, target, result):
        """Запись опыта боя для обучения"""
        if not hasattr(self, 'entity_id') or not hasattr(self.game, 'ai_memory_system'):
            return
        
        import time
        experience_data = {
            "action_type": action_type,
            "target_type": getattr(target, 'enemy_type', 'player'),
            "result": result,
            "distance": self.get_distance_to(target) if hasattr(target, 'getPos') else 0,
            "enemy_health_ratio": self.health / self.max_health if hasattr(self, 'max_health') else 1.0,
            "target_health_ratio": getattr(target, 'health', 100) / getattr(target, 'max_health', 100),
            "timestamp": time.time()
        }
        
        # Добавляем в память ИИ
        from core.enhanced_ai_memory import MemoryType
        self.game.ai_memory_system.add_memory(
            self.entity_id,
            MemoryType.COMBAT,
            experience_data,
            importance=1.0
        )
        
        # Обновляем опыт боя
        self.combat_experience += 1
        
        # Проверяем эволюцию
        self._check_evolution()
    
    def _check_evolution(self):
        """Проверка эволюции врага на основе опыта"""
        if not hasattr(self, 'entity_id') or not hasattr(self.game, 'ai_memory_system'):
            return
        
        # Получаем уровень памяти
        memory_level = self.game.ai_memory_system.get_memory_level(self.entity_id)
        
        # Проверяем, нужно ли повысить фазу (для боссов)
        if self.enemy_type == "boss" and memory_level > self.phase:
            self._evolve_to_phase(memory_level)
    
    def _evolve_to_phase(self, new_phase):
        """Эволюция врага в новую фазу"""
        if new_phase <= self.max_phases:
            self.phase = new_phase
            
            # Улучшаем характеристики
            self._improve_stats_for_phase()
            
            # Разблокируем новые способности
            self._unlock_phase_abilities()
            
            # Визуальные эффекты эволюции
            self._show_evolution_effects()
    
    def _improve_stats_for_phase(self):
        """Улучшение характеристик для новой фазы"""
        phase_multiplier = 1.0 + (self.phase - 1) * 0.3
        
        # Улучшаем базовые характеристики
        self.base_attributes.strength *= phase_multiplier
        self.base_attributes.vitality *= phase_multiplier
        self.base_attributes.agility *= phase_multiplier
        
        # Восстанавливаем здоровье
        if hasattr(self, 'max_health'):
            self.max_health = int(self.max_health * phase_multiplier)
            self.health = self.max_health
    
    def _unlock_phase_abilities(self):
        """Разблокировка способностей для новой фазы"""
        if hasattr(self, 'generated_data') and self.generated_data:
            # Используем данные из генератора контента
            skill_set = getattr(self.generated_data, 'skill_set', [])
            phases = getattr(self.generated_data, 'phases', 1)
            
            if self.phase <= phases and self.phase <= len(skill_set):
                new_skill = skill_set[self.phase - 1]
                if hasattr(self, 'skills'):
                    self.skills.append(new_skill)
    
    def _show_evolution_effects(self):
        """Показ визуальных эффектов эволюции"""
        # Изменение цвета в зависимости от фазы
        phase_colors = {
            1: (0.8, 0.8, 0.2, 1),    # Желтый
            2: (0.8, 0.4, 0.2, 1),    # Оранжевый
            3: (0.8, 0.2, 0.8, 1),    # Фиолетовый
            4: (0.2, 0.8, 0.8, 1)     # Голубой
        }
        
        if self.phase in phase_colors:
            self.setColor(*phase_colors[self.phase])
        
        # Увеличение размера
        scale_factor = 1.0 + (self.phase - 1) * 0.2
        self.setScale(scale_factor)
    
    def learn_from_shared_memory(self):
        """Обучение на основе общей памяти врагов"""
        if not hasattr(self, 'entity_id') or not hasattr(self.game, 'ai_memory_system'):
            return
        
        # Получаем общие воспоминания врагов
        from core.enhanced_ai_memory import MemoryType
        shared_memories = self.game.ai_memory_system.get_shared_enemy_memories(
            MemoryType.COMBAT, limit=5
        )
        
        for memory in shared_memories:
            # Анализируем успешные стратегии
            if memory.data.get("result", 0) > 0:  # Успешная атака
                self._adapt_strategy(memory.data)
    
    def _adapt_strategy(self, successful_data):
        """Адаптация стратегии на основе успешных данных"""
        # Простая адаптация - улучшаем характеристики, которые привели к успеху
        if successful_data.get("action_type") == "attack":
            # Улучшаем силу атаки
            self.base_attributes.strength *= 1.01
        
        # Записываем адаптацию
        import time
        adaptation_data = {
            "adapted_from": successful_data,
            "adaptation_type": "strategy_improvement",
            "timestamp": time.time()
        }
        
        from core.enhanced_ai_memory import MemoryType
        self.game.ai_memory_system.add_memory(
            self.entity_id,
            MemoryType.LEARNING,
            adaptation_data,
            importance=0.5
        )
        
    def get_attack_range(self):
        """Получение дальности атаки"""
        return 1.0  # Базовая дальность атаки

    def update_ai(self, player, dt: float):
        """Обновление ИИ врага для совместимости с GameManager."""
        if not self.is_alive():
            return
        if player and player.is_alive():
            # Преследуем игрока, если вне дальности атаки
            distance = self.get_distance_to(player)
            if distance > max(self.attack_range, self.get_attack_range()):
                self.move_towards_player(player.x, player.y)
            else:
                # Атакуем игрока
                self.attack_player(player)
