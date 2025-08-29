#!/usr/bin/env python3
"""
Класс Enemy - враги и враждебные сущности
"""

import logging
import time
import random
import math
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field

from core.constants import StatType, DamageType, AIState, EntityType
from .base_entity import BaseEntity, EntityType as BaseEntityType

logger = logging.getLogger(__name__)

@dataclass
class EnemyStats:
    """Дополнительные характеристики врага"""
    # Боевые характеристики
    threat_level: int = 1  # 1-10, где 10 - самый опасный
    aggression: float = 0.7  # 0.0 до 1.0
    intelligence: float = 0.5  # 0.0 до 1.0
    
    # Специальные способности
    special_abilities: List[str] = field(default_factory=list)
    immunities: List[DamageType] = field(default_factory=list)
    
    # Дроп и награды
    drop_chance: float = 0.3
    experience_reward: int = 50
    gold_reward: int = 10

@dataclass
class EnemyBehavior:
    """Поведение врага"""
    # Типы поведения
    behavior_type: str = "aggressive"  # aggressive, defensive, stealth, berserk
    patrol_radius: float = 10.0
    detection_range: float = 15.0
    attack_range: float = 2.0
    
    # Тактические предпочтения
    preferred_distance: float = 3.0
    retreat_health_threshold: float = 0.3
    call_for_help: bool = True
    
    # Временные параметры
    attack_cooldown: float = 2.0
    last_attack_time: float = 0.0

@dataclass
class EnemyMemory:
    """Память врага"""
    # Боевая память
    combat_history: List[Dict[str, Any]] = field(default_factory=list)
    defeated_enemies: List[str] = field(default_factory=list)
    retreat_count: int = 0
    
    # Тактическая память
    successful_tactics: List[str] = field(default_factory=list)
    failed_tactics: List[str] = field(default_factory=list)
    
    # Временные метки
    last_combat: float = 0.0
    last_retreat: float = 0.0

class Enemy(BaseEntity):
    """Класс врага - наследуется от BaseEntity"""
    
    def __init__(self, enemy_id: str, name: str, enemy_type: str = "basic"):
        # Инициализируем базовую сущность
        super().__init__(enemy_id, BaseEntityType.ENEMY, name)
        
        # Дополнительные характеристики врага
        self.enemy_stats = EnemyStats()
        self.behavior = EnemyBehavior()
        self.enemy_memory = EnemyMemory()
        
        # Специфичные для врага настройки
        self.inventory.max_slots = 10  # Меньше слотов инвентаря
        self.inventory.max_weight = 50.0  # Меньше веса
        self.memory.max_memories = 80  # Меньше памяти
        self.memory.learning_rate = 0.3  # Медленнее учится
        
        # Боевые параметры
        self.threat_level = 1
        self.aggression = 0.7
        self.intelligence = 0.5
        
        # Состояние боя
        self.is_retreating = False
        self.retreat_target: Optional[Tuple[float, float, float]] = None
        self.retreat_start_time = 0.0
        self.retreat_duration = 10.0  # секунды
        
        # Способности
        self.abilities: List[str] = []
        self.ability_cooldowns: Dict[str, float] = {}
        self.last_ability_use: Dict[str, float] = {}
        
        # Патрулирование
        self.patrol_points: List[Tuple[float, float, float]] = []
        self.current_patrol_index = 0
        self.patrol_wait_time = 0.0
        
        # Дроп
        self.drop_table: List[Dict[str, Any]] = []
        self.guaranteed_drops: List[str] = []
        
        logger.info(f"Создан враг: {name} ({enemy_type})")
    
    def update(self, delta_time: float):
        """Обновление состояния врага"""
        try:
            # Обновляем базовую сущность
            super().update(delta_time)
            
            # Обновляем поведение
            self._update_behavior(delta_time)
            
            # Обновляем патрулирование
            self._update_patrol(delta_time)
            
            # Обновляем отступление
            self._update_retreat(delta_time)
            
            # Обновляем способности
            self._update_abilities(delta_time)
            
        except Exception as e:
            logger.error(f"Ошибка обновления врага {self.entity_id}: {e}")
    
    def _update_behavior(self, delta_time: float):
        """Обновление поведения врага"""
        try:
            current_time = time.time()
            
            # Обновляем время перезарядки атаки
            if self.behavior.last_attack_time > 0:
                self.behavior.last_attack_time -= delta_time
                self.behavior.last_attack_time = max(0, self.behavior.last_attack_time)
            
            # Обновляем перезарядки способностей
            for ability in self.ability_cooldowns:
                if self.ability_cooldowns[ability] > 0:
                    self.ability_cooldowns[ability] -= delta_time
                    self.ability_cooldowns[ability] = max(0, self.ability_cooldowns[ability])
            
            # Проверяем необходимость отступления
            if (self.stats.health / self.stats.max_health) <= self.behavior.retreat_health_threshold:
                if not self.is_retreating:
                    self._start_retreat()
            
        except Exception as e:
            logger.error(f"Ошибка обновления поведения врага {self.entity_id}: {e}")
    
    def _update_patrol(self, delta_time: float):
        """Обновление патрулирования"""
        try:
            if not self.patrol_points or self.is_in_combat or self.is_retreating:
                return
            
            current_time = time.time()
            
            # Ждем в точке патруля
            if self.patrol_wait_time > 0:
                self.patrol_wait_time -= delta_time
                return
            
            # Переходим к следующей точке
            if self.current_patrol_index < len(self.patrol_points):
                target_point = self.patrol_points[self.current_patrol_index]
                
                # Простое движение к точке (здесь должна быть логика движения)
                distance = self._calculate_distance(self.position, target_point)
                if distance < 1.0:  # Достигли точки
                    self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
                    self.patrol_wait_time = random.uniform(2.0, 5.0)  # Ждем в точке
            
        except Exception as e:
            logger.error(f"Ошибка обновления патрулирования врага {self.entity_id}: {e}")
    
    def _update_retreat(self, delta_time: float):
        """Обновление отступления"""
        try:
            if not self.is_retreating:
                return
            
            current_time = time.time()
            
            # Проверяем время отступления
            if current_time - self.retreat_start_time >= self.retreat_duration:
                self._end_retreat()
                return
            
            # Двигаемся к точке отступления
            if self.retreat_target:
                distance = self._calculate_distance(self.position, self.retreat_target)
                if distance < 2.0:  # Достигли точки отступления
                    self._end_retreat()
            
        except Exception as e:
            logger.error(f"Ошибка обновления отступления врага {self.entity_id}: {e}")
    
    def _update_abilities(self, delta_time: float):
        """Обновление способностей"""
        try:
            current_time = time.time()
            
            # Проверяем возможность использования способностей
            for ability in self.abilities:
                if (ability not in self.ability_cooldowns or 
                    self.ability_cooldowns[ability] <= 0):
                    # Способность готова к использованию
                    if self.is_in_combat and self.current_target:
                        # Используем способность в бою
                        self._use_ability(ability)
            
        except Exception as e:
            logger.error(f"Ошибка обновления способностей врага {self.entity_id}: {e}")
    
    def attack(self, target: str, attack_type: str = "basic") -> bool:
        """Атака цели"""
        try:
            if not self.is_alive or self.is_retreating:
                return False
            
            # Проверяем перезарядку атаки
            if self.behavior.last_attack_time > 0:
                return False
            
            # Рассчитываем урон
            base_damage = self.stats.attack
            if attack_type == "strong":
                base_damage *= 1.5
            elif attack_type == "weak":
                base_damage *= 0.7
            
            # Добавляем случайность
            damage = int(base_damage * random.uniform(0.8, 1.2))
            
            # Устанавливаем перезарядку
            self.behavior.last_attack_time = self.behavior.attack_cooldown
            
            # Записываем атаку в память
            self.add_memory('combat', {
                'action': 'attack',
                'target': target,
                'attack_type': attack_type,
                'damage': damage
            }, 'attack', {
                'target': target,
                'damage_dealt': damage,
                'attack_type': attack_type
            }, True)
            
            # Обновляем время последнего боя
            self.enemy_memory.last_combat = time.time()
            
            logger.debug(f"Враг {self.entity_id} атаковал {target} с уроном {damage}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка атаки врага {self.entity_id}: {e}")
            return False
    
    def use_ability(self, ability_name: str, target: str = None) -> bool:
        """Использование способности"""
        try:
            if not self.is_alive or ability_name not in self.abilities:
                return False
            
            # Проверяем перезарядку
            if (ability_name in self.ability_cooldowns and 
                self.ability_cooldowns[ability_name] > 0):
                return False
            
            # Проверяем стоимость способности
            if not self._can_use_ability(ability_name):
                return False
            
            # Используем способность
            success = self._execute_ability(ability_name, target)
            
            if success:
                # Устанавливаем перезарядку
                cooldown = self._get_ability_cooldown(ability_name)
                self.ability_cooldowns[ability_name] = cooldown
                self.last_ability_use[ability_name] = time.time()
                
                # Записываем использование в память
                self.add_memory('combat', {
                    'action': 'ability_used',
                    'ability': ability_name,
                    'target': target
                }, 'ability_used', {
                    'ability': ability_name,
                    'success': True
                }, True)
                
                logger.debug(f"Враг {self.entity_id} использовал способность {ability_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка использования способности врагом {self.entity_id}: {e}")
            return False
    
    def _can_use_ability(self, ability_name: str) -> bool:
        """Проверка возможности использования способности"""
        try:
            # Проверяем стоимость маны
            mana_cost = self._get_ability_mana_cost(ability_name)
            if self.stats.mana < mana_cost:
                return False
            
            # Проверяем стоимость выносливости
            stamina_cost = self._get_ability_stamina_cost(ability_name)
            if self.stats.stamina < stamina_cost:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки способности {ability_name}: {e}")
            return False
    
    def _get_ability_mana_cost(self, ability_name: str) -> int:
        """Получение стоимости маны способности"""
        # Базовые стоимости способностей
        costs = {
            'fireball': 20,
            'heal': 15,
            'buff': 10,
            'debuff': 12,
            'teleport': 25
        }
        return costs.get(ability_name, 0)
    
    def _get_ability_stamina_cost(self, ability_name: str) -> int:
        """Получение стоимости выносливости способности"""
        # Базовые стоимости способностей
        costs = {
            'charge': 30,
            'dash': 20,
            'block': 15,
            'counter': 25
        }
        return costs.get(ability_name, 0)
    
    def _get_ability_cooldown(self, ability_name: str) -> float:
        """Получение перезарядки способности"""
        # Базовые перезарядки способностей
        cooldowns = {
            'fireball': 5.0,
            'heal': 10.0,
            'buff': 15.0,
            'debuff': 8.0,
            'teleport': 20.0,
            'charge': 3.0,
            'dash': 2.0,
            'block': 1.0,
            'counter': 5.0
        }
        return cooldowns.get(ability_name, 5.0)
    
    def _execute_ability(self, ability_name: str, target: str = None) -> bool:
        """Выполнение способности"""
        try:
            # Тратим ресурсы
            mana_cost = self._get_ability_mana_cost(ability_name)
            stamina_cost = self._get_ability_stamina_cost(ability_name)
            
            self.stats.mana -= mana_cost
            self.stats.stamina -= stamina_cost
            
            # Здесь должна быть логика выполнения конкретной способности
            # Пока просто возвращаем успех
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выполнения способности {ability_name}: {e}")
            return False
    
    def _use_ability(self, ability_name: str):
        """Автоматическое использование способности"""
        try:
            if self.current_target:
                self.use_ability(ability_name, self.current_target)
            
        except Exception as e:
            logger.error(f"Ошибка автоматического использования способности {ability_name}: {e}")
    
    def _start_retreat(self):
        """Начало отступления"""
        try:
            if self.is_retreating:
                return
            
            self.is_retreating = True
            self.retreat_start_time = time.time()
            
            # Находим позицию для отступления
            self.retreat_target = self._find_retreat_position()
            
            # Обновляем состояние
            self.current_state = AIState.FLEEING
            
            # Записываем отступление в память
            self.add_memory('combat', {
                'action': 'retreat_started',
                'reason': 'low_health'
            }, 'retreat_started', {
                'health_percentage': self.stats.health / self.stats.max_health
            }, True)
            
            # Обновляем статистику
            self.enemy_memory.retreat_count += 1
            self.enemy_memory.last_retreat = time.time()
            
            logger.info(f"Враг {self.entity_id} начал отступление")
            
        except Exception as e:
            logger.error(f"Ошибка начала отступления врага {self.entity_id}: {e}")
    
    def _end_retreat(self):
        """Завершение отступления"""
        try:
            if not self.is_retreating:
                return
            
            self.is_retreating = False
            self.retreat_target = None
            
            # Восстанавливаем здоровье после отступления
            heal_amount = int(self.stats.max_health * 0.3)
            self.heal(heal_amount, "retreat")
            
            # Возвращаемся к патрулированию
            self.current_state = AIState.IDLE
            
            # Записываем завершение отступления в память
            self.add_memory('combat', {
                'action': 'retreat_ended',
                'heal_amount': heal_amount
            }, 'retreat_ended', {
                'heal_amount': heal_amount,
                'new_health': self.stats.health
            }, True)
            
            logger.info(f"Враг {self.entity_id} завершил отступление")
            
        except Exception as e:
            logger.error(f"Ошибка завершения отступления врага {self.entity_id}: {e}")
    
    def _find_retreat_position(self) -> Optional[Tuple[float, float, float]]:
        """Поиск позиции для отступления"""
        try:
            # Простая логика - отступаем в противоположную сторону от текущей позиции
            if self.current_target:
                # Здесь должна быть логика поиска безопасной позиции
                # Пока возвращаем случайную позицию в радиусе
                angle = random.uniform(0, 2 * 3.14159)
                distance = random.uniform(10, 20)
                
                x = self.position[0] + distance * math.cos(angle)
                y = self.position[1] + distance * math.sin(angle)
                z = self.position[2]
                
                return (x, y, z)
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка поиска позиции отступления: {e}")
            return None
    
    def _call_for_help(self) -> bool:
        """Призыв помощи"""
        try:
            if not self.behavior.call_for_help:
                return False
            
            # Здесь должна быть логика призыва других врагов
            # Пока просто записываем в память
            self.add_memory('combat', {
                'action': 'help_called',
                'reason': 'overwhelmed'
            }, 'help_called', {
                'success': True
            }, True)
            
            logger.debug(f"Враг {self.entity_id} призвал помощь")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка призыва помощи врагом {self.entity_id}: {e}")
            return False
    
    def _calculate_distance(self, pos1: Tuple[float, float, float], 
                          pos2: Tuple[float, float, float]) -> float:
        """Расчет расстояния между точками"""
        try:
            dx = pos1[0] - pos2[0]
            dy = pos1[1] - pos2[1]
            dz = pos1[2] - pos2[2]
            return math.sqrt(dx*dx + dy*dy + dz*dz)
            
        except Exception as e:
            logger.error(f"Ошибка расчета расстояния: {e}")
            return 0.0
    
    def _record_combat_memory(self, action: str, target: str, success: bool, 
                            details: Dict[str, Any] = None):
        """Запись боевой памяти"""
        try:
            combat_record = {
                'action': action,
                'target': target,
                'success': success,
                'timestamp': time.time(),
                'health_percentage': self.stats.health / self.stats.max_health,
                'details': details or {}
            }
            
            self.enemy_memory.combat_history.append(combat_record)
            
            # Ограничиваем размер истории
            if len(self.enemy_memory.combat_history) > 50:
                self.enemy_memory.combat_history = self.enemy_memory.combat_history[-50:]
            
        except Exception as e:
            logger.error(f"Ошибка записи боевой памяти: {e}")
    
    def enter_combat(self, target: str):
        """Вход в бой"""
        try:
            if not self.is_alive:
                return
            
            self.is_in_combat = True
            self.current_target = target
            self.current_state = AIState.COMBAT
            
            # Записываем в память
            self.add_memory('combat', {
                'action': 'combat_started',
                'target': target
            }, 'combat_started', {
                'target': target
            }, True)
            
            # Обновляем время последнего боя
            self.enemy_memory.last_combat = time.time()
            
            logger.debug(f"Враг {self.entity_id} вступил в бой с {target}")
            
        except Exception as e:
            logger.error(f"Ошибка входа в бой врагом {self.entity_id}: {e}")
    
    def exit_combat(self):
        """Выход из боя"""
        try:
            if not self.is_in_combat:
                return
            
            self.is_in_combat = False
            self.current_target = None
            self.current_state = AIState.IDLE
            
            # Записываем в память
            self.add_memory('combat', {
                'action': 'combat_ended',
                'reason': 'target_defeated'
            }, 'combat_ended', {
                'health_percentage': self.stats.health / self.stats.max_health
            }, True)
            
            logger.debug(f"Враг {self.entity_id} вышел из боя")
            
        except Exception as e:
            logger.error(f"Ошибка выхода из боя врагом {self.entity_id}: {e}")
    
    def add_ability(self, ability_name: str) -> bool:
        """Добавление способности"""
        try:
            if ability_name not in self.abilities:
                self.abilities.append(ability_name)
                self.ability_cooldowns[ability_name] = 0.0
                self.last_ability_use[ability_name] = 0.0
                
                logger.debug(f"Способность {ability_name} добавлена врагу {self.entity_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка добавления способности {ability_name}: {e}")
            return False
    
    def set_patrol_route(self, patrol_points: List[Tuple[float, float, float]]):
        """Установка маршрута патрулирования"""
        try:
            self.patrol_points = patrol_points
            self.current_patrol_index = 0
            self.patrol_wait_time = 0.0
            
            logger.debug(f"Маршрут патрулирования установлен для врага {self.entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка установки маршрута патрулирования: {e}")
    
    def add_drop_item(self, item_id: str, chance: float = 0.1, guaranteed: bool = False):
        """Добавление предмета в дроп"""
        try:
            drop_entry = {
                'item_id': item_id,
                'chance': chance,
                'guaranteed': guaranteed
            }
            
            if guaranteed:
                self.guaranteed_drops.append(item_id)
            else:
                self.drop_table.append(drop_entry)
            
            logger.debug(f"Предмет {item_id} добавлен в дроп врага {self.entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка добавления предмета в дроп: {e}")
    
    def get_enemy_data(self) -> Dict[str, Any]:
        """Получение данных врага"""
        base_data = super().get_entity_data()
        
        # Добавляем специфичные для врага данные
        enemy_data = {
            **base_data,
            'enemy_stats': {
                'threat_level': self.enemy_stats.threat_level,
                'aggression': self.enemy_stats.aggression,
                'intelligence': self.enemy_stats.intelligence,
                'special_abilities': self.enemy_stats.special_abilities,
                'immunities': [immunity.value for immunity in self.enemy_stats.immunities],
                'drop_chance': self.enemy_stats.drop_chance,
                'experience_reward': self.enemy_stats.experience_reward,
                'gold_reward': self.enemy_stats.gold_reward
            },
            'behavior': {
                'behavior_type': self.behavior.behavior_type,
                'patrol_radius': self.behavior.patrol_radius,
                'detection_range': self.behavior.detection_range,
                'attack_range': self.behavior.attack_range,
                'preferred_distance': self.behavior.preferred_distance,
                'retreat_health_threshold': self.behavior.retreat_health_threshold,
                'call_for_help': self.behavior.call_for_help,
                'attack_cooldown': self.behavior.attack_cooldown,
                'last_attack_time': self.behavior.last_attack_time
            },
            'enemy_memory': {
                'combat_history_count': len(self.enemy_memory.combat_history),
                'defeated_enemies_count': len(self.enemy_memory.defeated_enemies),
                'retreat_count': self.enemy_memory.retreat_count,
                'successful_tactics': self.enemy_memory.successful_tactics,
                'failed_tactics': self.enemy_memory.failed_tactics,
                'last_combat': self.enemy_memory.last_combat,
                'last_retreat': self.enemy_memory.last_retreat
            },
            'combat_state': {
                'is_retreating': self.is_retreating,
                'retreat_target': self.retreat_target,
                'retreat_start_time': self.retreat_start_time,
                'retreat_duration': self.retreat_duration
            },
            'abilities': {
                'abilities': self.abilities,
                'ability_cooldowns': self.ability_cooldowns,
                'last_ability_use': self.last_ability_use
            },
            'patrol': {
                'patrol_points': self.patrol_points,
                'current_patrol_index': self.current_patrol_index,
                'patrol_wait_time': self.patrol_wait_time
            },
            'drops': {
                'drop_table': self.drop_table,
                'guaranteed_drops': self.guaranteed_drops
            }
        }
        
        return enemy_data
    
    def get_info(self) -> str:
        """Получение информации о враге"""
        base_info = super().get_info()
        
        enemy_info = (f"\n--- Враг ---\n"
                     f"Уровень угрозы: {self.enemy_stats.threat_level} | "
                     f"Агрессия: {self.enemy_stats.aggression:.2f}\n"
                     f"Поведение: {self.behavior.behavior_type} | "
                     f"Отступление: {'Да' if self.is_retreating else 'Нет'}\n"
                     f"Способности: {len(self.abilities)} | "
                     f"Патрульные точки: {len(self.patrol_points)}\n"
                     f"Боевая история: {len(self.enemy_memory.combat_history)} | "
                     f"Отступлений: {self.enemy_memory.retreat_count}\n"
                     f"Награда: {self.enemy_stats.experience_reward} опыта, "
                     f"{self.enemy_stats.gold_reward} золота")
        
        return base_info + enemy_info
