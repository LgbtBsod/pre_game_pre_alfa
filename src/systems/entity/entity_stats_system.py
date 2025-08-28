#!/usr/bin/env python3
"""
Система характеристик сущностей - управление статистиками и модификаторами
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.interfaces import ISystem, SystemPriority, SystemState
from ...core.constants import (
    StatType, StatCategory, DamageType, BASE_STATS,
    PROBABILITY_CONSTANTS, TIME_CONSTANTS, SYSTEM_LIMITS,
    STAT_CALCULATION_FORMULAS
)
from ...core.stats_utils import (
    STAT_GROUPS, ENTITY_STAT_TEMPLATES, get_entity_template,
    apply_stat_template, validate_stats, merge_stats, scale_stats_by_level
)

logger = logging.getLogger(__name__)

@dataclass
class StatModifier:
    """Модификатор характеристики"""
    modifier_id: str
    stat_type: StatType
    value: float
    modifier_type: str  # "flat", "percent", "multiplier"
    source: str
    duration: float = 0.0  # 0.0 = постоянный
    start_time: float = field(default_factory=time.time)
    stackable: bool = False
    max_stacks: int = 1
    current_stacks: int = 1

@dataclass
class EntityStats:
    """Характеристики сущности"""
    entity_id: str
    level: int = 1
    experience: int = 0
    experience_to_next: int = 100
    
    # Основные характеристики (расчетные из атрибутов)
    health: int = BASE_STATS["health"]
    max_health: int = BASE_STATS["health"]
    mana: int = BASE_STATS["mana"]
    max_mana: int = BASE_STATS["mana"]
    stamina: int = BASE_STATS["stamina"]
    max_stamina: int = BASE_STATS["stamina"]
    
    # Боевые характеристики
    attack: int = BASE_STATS["attack"]
    defense: int = BASE_STATS["defense"]
    speed: float = BASE_STATS["speed"]
    attack_speed: float = 1.0  # Скорость атаки
    range: float = BASE_STATS["range"]
    
    # Шансовые характеристики
    critical_chance: float = PROBABILITY_CONSTANTS["base_critical_chance"]
    critical_multiplier: float = 2.0
    dodge_chance: float = PROBABILITY_CONSTANTS["base_dodge_chance"]
    block_chance: float = PROBABILITY_CONSTANTS["base_block_chance"]
    parry_chance: float = BASE_STATS["parry_chance"]
    evasion_chance: float = BASE_STATS["evasion_chance"]
    resist_chance: float = BASE_STATS["resist_chance"]
    
    # Атрибуты (основные характеристики)
    strength: int = BASE_STATS["strength"]
    agility: int = BASE_STATS["agility"]
    intelligence: int = BASE_STATS["intelligence"]
    constitution: int = BASE_STATS["constitution"]
    wisdom: int = BASE_STATS["wisdom"]
    charisma: int = BASE_STATS["charisma"]
    luck: float = PROBABILITY_CONSTANTS["base_luck"]
    
    # Механика стойкости
    toughness: int = BASE_STATS["toughness"]
    toughness_resistance: float = BASE_STATS["toughness_resistance"]
    stun_resistance: float = BASE_STATS["stun_resistance"]
    break_efficiency: float = BASE_STATS["break_efficiency"]
    
    # Регенерация (расчетная из атрибутов)
    health_regen: float = 1.0
    mana_regen: float = 1.0
    stamina_regen: float = 1.0
    
    # Сопротивления
    resistances: Dict[DamageType, float] = field(default_factory=dict)
    
    # Дополнительные характеристики
    reputation: int = 0
    fame: int = 0

class EntityStatsSystem(ISystem):
    """Система управления характеристиками сущностей"""
    
    def __init__(self):
        self._system_name = "entity_stats"
        self._system_priority = SystemPriority.HIGH
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Характеристики сущностей
        self.entity_stats: Dict[str, EntityStats] = {}
        
        # Модификаторы характеристик
        self.stat_modifiers: Dict[str, List[StatModifier]] = {}
        
        # История изменений характеристик
        self.stats_history: List[Dict[str, Any]] = []
        
        # Настройки системы
        self.system_settings = {
            'max_level': SYSTEM_LIMITS["max_entity_level"],
            'experience_scaling': 1.5,
            'stats_per_level': 5,
            'modifier_cleanup_interval': TIME_CONSTANTS["modifier_cleanup_interval"],
            'auto_regen_enabled': True,
            'regen_interval': 1.0  # секунды
        }
        
        # Статистика системы
        self.system_stats = {
            'entities_count': 0,
            'total_modifiers': 0,
            'stats_updated_today': 0,
            'levels_gained_today': 0,
            'update_time': 0.0
        }
        
        logger.info("Система характеристик сущностей инициализирована")
    
    @property
    def system_name(self) -> str:
        return self._system_name
    
    @property
    def system_priority(self) -> SystemPriority:
        return self._system_priority
    
    @property
    def system_state(self) -> SystemState:
        return self._system_state
    
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    
    def initialize(self) -> bool:
        """Инициализация системы характеристик"""
        try:
            logger.info("Инициализация системы характеристик...")
            
            # Настраиваем систему
            self._setup_stats_system()
            
            self._system_state = SystemState.READY
            logger.info("Система характеристик успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы характеристик: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы характеристик"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем модификаторы
            self._update_stat_modifiers(delta_time)
            
            # Обновляем регенерацию
            if self.system_settings['auto_regen_enabled']:
                self._update_regeneration(delta_time)
            
            # Очищаем истекшие модификаторы
            self._cleanup_expired_modifiers()
            
            # Обновляем статистику системы
            self._update_system_stats()
            
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы характеристик: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы характеристик"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система характеристик приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы характеристик: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы характеристик"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система характеристик возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы характеристик: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы характеристик"""
        try:
            logger.info("Очистка системы характеристик...")
            
            # Очищаем все данные
            self.entity_stats.clear()
            self.stat_modifiers.clear()
            self.stats_history.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'entities_count': 0,
                'total_modifiers': 0,
                'stats_updated_today': 0,
                'levels_gained_today': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система характеристик очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы характеристик: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'entities_count': len(self.entity_stats),
            'total_modifiers': sum(len(modifiers) for modifiers in self.stat_modifiers.values()),
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "entity_destroyed":
                return self._handle_entity_destroyed(event_data)
            elif event_type == "experience_gained":
                return self._handle_experience_gained(event_data)
            elif event_type == "stats_modified":
                return self._handle_stats_modified(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def _setup_stats_system(self) -> None:
        """Настройка системы характеристик"""
        try:
            # Инициализируем базовые настройки
            logger.debug("Система характеристик настроена")
        except Exception as e:
            logger.warning(f"Не удалось настроить систему характеристик: {e}")
    
    def _update_stat_modifiers(self, delta_time: float) -> None:
        """Обновление модификаторов характеристик"""
        try:
            current_time = time.time()
            
            for entity_id, modifiers in self.stat_modifiers.items():
                for modifier in modifiers:
                    # Проверяем, не истек ли модификатор
                    if modifier.duration > 0 and current_time - modifier.start_time > modifier.duration:
                        # Модификатор истек, будет удален в cleanup
                        continue
                    
                    # Применяем модификатор к характеристикам
                    self._apply_modifier_to_stats(entity_id, modifier)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления модификаторов характеристик: {e}")
    
    def _update_regeneration(self, delta_time: float) -> None:
        """Обновление регенерации"""
        try:
            current_time = time.time()
            
            for entity_id, stats in self.entity_stats.items():
                # Проверяем, нужно ли обновлять регенерацию
                if hasattr(stats, '_last_regen_time'):
                    if current_time - stats._last_regen_time < self.system_settings['regen_interval']:
                        continue
                else:
                    stats._last_regen_time = current_time
                
                # Регенерация здоровья
                if stats.health < stats.max_health:
                    regen_amount = int(stats.constitution * 0.1) + 1
                    stats.health = min(stats.max_health, stats.health + regen_amount)
                
                # Регенерация маны
                if stats.mana < stats.max_mana:
                    regen_amount = int(stats.intelligence * 0.1) + 1
                    stats.mana = min(stats.max_mana, stats.mana + regen_amount)
                
                # Регенерация выносливости
                if stats.stamina < stats.max_stamina:
                    regen_amount = int(stats.agility * 0.1) + 1
                    stats.stamina = min(stats.max_stamina, stats.stamina + regen_amount)
                
                stats._last_regen_time = current_time
                
        except Exception as e:
            logger.warning(f"Ошибка обновления регенерации: {e}")
    
    def _cleanup_expired_modifiers(self) -> None:
        """Очистка истекших модификаторов"""
        try:
            current_time = time.time()
            
            for entity_id in list(self.stat_modifiers.keys()):
                if entity_id not in self.stat_modifiers:
                    continue
                
                # Удаляем истекшие модификаторы
                valid_modifiers = [
                    modifier for modifier in self.stat_modifiers[entity_id]
                    if modifier.duration == 0.0 or current_time - modifier.start_time <= modifier.duration
                ]
                
                if len(valid_modifiers) != len(self.stat_modifiers[entity_id]):
                    removed_count = len(self.stat_modifiers[entity_id]) - len(valid_modifiers)
                    self.stat_modifiers[entity_id] = valid_modifiers
                    logger.debug(f"Удалено {removed_count} истекших модификаторов у {entity_id}")
                
                # Удаляем пустые записи
                if not self.stat_modifiers[entity_id]:
                    del self.stat_modifiers[entity_id]
                
        except Exception as e:
            logger.warning(f"Ошибка очистки истекших модификаторов: {e}")
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            self.system_stats['entities_count'] = len(self.entity_stats)
            self.system_stats['total_modifiers'] = sum(len(modifiers) for modifiers in self.stat_modifiers.values())
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
            entity_id = event_data.get('entity_id')
            initial_stats = event_data.get('initial_stats', {})
            
            if entity_id:
                return self.create_entity_stats(entity_id, initial_stats)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания сущности: {e}")
            return False
    
    def _handle_entity_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения сущности"""
        try:
            entity_id = event_data.get('entity_id')
            
            if entity_id:
                return self.destroy_entity_stats(entity_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события уничтожения сущности: {e}")
            return False
    
    def _handle_experience_gained(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события получения опыта"""
        try:
            entity_id = event_data.get('entity_id')
            experience_amount = event_data.get('experience_amount', 0)
            
            if entity_id and experience_amount > 0:
                return self.add_experience(entity_id, experience_amount)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события получения опыта: {e}")
            return False
    
    def _handle_stats_modified(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события изменения характеристик"""
        try:
            entity_id = event_data.get('entity_id')
            stat_type = event_data.get('stat_type')
            value = event_data.get('value')
            modifier_type = event_data.get('modifier_type', 'flat')
            source = event_data.get('source', 'system')
            duration = event_data.get('duration', 0.0)
            
            if entity_id and stat_type and value is not None:
                return self.add_stat_modifier(entity_id, stat_type, value, modifier_type, source, duration)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события изменения характеристик: {e}")
            return False
    
    def create_entity_stats(self, entity_id: str, initial_stats: Dict[str, Any] = None) -> bool:
        """Создание характеристик для сущности"""
        try:
            if entity_id in self.entity_stats:
                logger.warning(f"Характеристики для сущности {entity_id} уже существуют")
                return False
            
            # Создаем базовые характеристики
            stats = EntityStats(entity_id=entity_id)
            
            # Применяем начальные характеристики
            if initial_stats:
                for key, value in initial_stats.items():
                    if hasattr(stats, key):
                        setattr(stats, key, value)
            
            # Рассчитываем характеристики из атрибутов
            attributes = {
                "strength": stats.strength,
                "agility": stats.agility,
                "intelligence": stats.intelligence,
                "constitution": stats.constitution,
                "wisdom": stats.wisdom,
                "charisma": stats.charisma,
                "luck": stats.luck
            }
            
            calculated_stats = calculate_stats_from_attributes(BASE_STATS, attributes)
            
            # Применяем рассчитанные характеристики
            stats.health = calculated_stats["health"]
            stats.max_health = calculated_stats["health"]
            stats.mana = calculated_stats["mana"]
            stats.max_mana = calculated_stats["mana"]
            stats.stamina = calculated_stats["stamina"]
            stats.max_stamina = calculated_stats["stamina"]
            
            # Инициализируем сопротивления
            stats.resistances = {
                DamageType.PHYSICAL: 0.0,
                DamageType.FIRE: 0.0,
                DamageType.ICE: 0.0,
                DamageType.LIGHTNING: 0.0,
                DamageType.POISON: 0.0,
                DamageType.HOLY: 0.0,
                DamageType.DARK: 0.0,
                DamageType.ARCANE: 0.0
            }
            
            # Добавляем характеристики
            self.entity_stats[entity_id] = stats
            self.stat_modifiers[entity_id] = []
            
            logger.info(f"Созданы характеристики для сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания характеристик для сущности {entity_id}: {e}")
            return False
    
    def destroy_entity_stats(self, entity_id: str) -> bool:
        """Уничтожение характеристик сущности"""
        try:
            if entity_id not in self.entity_stats:
                return False
            
            # Удаляем характеристики
            del self.entity_stats[entity_id]
            
            # Удаляем модификаторы
            if entity_id in self.stat_modifiers:
                del self.stat_modifiers[entity_id]
            
            logger.info(f"Уничтожены характеристики сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения характеристик сущности {entity_id}: {e}")
            return False
    
    def add_experience(self, entity_id: str, experience_amount: int) -> bool:
        """Добавление опыта сущности"""
        try:
            if entity_id not in self.entity_stats:
                logger.warning(f"Характеристики сущности {entity_id} не найдены")
                return False
            
            stats = self.entity_stats[entity_id]
            stats.experience += experience_amount
            
            # Проверяем повышение уровня
            while stats.experience >= stats.experience_to_next:
                if self._level_up(entity_id):
                    stats.experience -= stats.experience_to_next
                    stats.experience_to_next = int(stats.experience_to_next * self.system_settings['experience_scaling'])
                else:
                    break
            
            # Записываем в историю
            current_time = time.time()
            self.stats_history.append({
                'timestamp': current_time,
                'action': 'experience_gained',
                'entity_id': entity_id,
                'amount': experience_amount,
                'new_total': stats.experience
            })
            
            logger.debug(f"Сущность {entity_id} получила {experience_amount} опыта")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления опыта сущности {entity_id}: {e}")
            return False
    
    def _level_up(self, entity_id: str) -> bool:
        """Повышение уровня сущности"""
        try:
            if entity_id not in self.entity_stats:
                return False
            
            stats = self.entity_stats[entity_id]
            
            if stats.level >= self.system_settings['max_level']:
                logger.debug(f"Сущность {entity_id} достигла максимального уровня")
                return False
            
            old_level = stats.level
            stats.level += 1
            
            # Улучшаем характеристики
            stats_points = self.system_settings['stats_per_level']
            
            # Распределяем очки характеристик
            stats.strength += stats_points // 6
            stats.agility += stats_points // 6
            stats.intelligence += stats_points // 6
            stats.constitution += stats_points // 6
            stats.wisdom += stats_points // 6
            stats.charisma += stats_points // 6
            
            # Улучшаем основные характеристики
            stats.max_health += int(stats.constitution * 0.5)
            stats.max_mana += int(stats.intelligence * 0.3)
            stats.max_stamina += int(stats.agility * 0.2)
            
            # Восстанавливаем здоровье и ману
            stats.health = stats.max_health
            stats.mana = stats.max_mana
            stats.stamina = stats.max_stamina
            
            # Записываем в историю
            current_time = time.time()
            self.stats_history.append({
                'timestamp': current_time,
                'action': 'level_up',
                'entity_id': entity_id,
                'old_level': old_level,
                'new_level': stats.level
            })
            
            self.system_stats['levels_gained_today'] += 1
            logger.info(f"Сущность {entity_id} повысила уровень до {stats.level}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка повышения уровня сущности {entity_id}: {e}")
            return False
    
    def add_stat_modifier(self, entity_id: str, stat_type: StatType, value: float, 
                         modifier_type: str = 'flat', source: str = 'system', duration: float = 0.0) -> bool:
        """Добавление модификатора характеристики"""
        try:
            if entity_id not in self.entity_stats:
                logger.warning(f"Характеристики сущности {entity_id} не найдены")
                return False
            
            # Создаем модификатор
            modifier = StatModifier(
                modifier_id=f"{source}_{int(time.time() * 1000)}",
                stat_type=stat_type,
                value=value,
                modifier_type=modifier_type,
                source=source,
                duration=duration
            )
            
            # Добавляем модификатор
            if entity_id not in self.stat_modifiers:
                self.stat_modifiers[entity_id] = []
            
            self.stat_modifiers[entity_id].append(modifier)
            
            # Применяем модификатор
            self._apply_modifier_to_stats(entity_id, modifier)
            
            # Записываем в историю
            current_time = time.time()
            self.stats_history.append({
                'timestamp': current_time,
                'action': 'modifier_added',
                'entity_id': entity_id,
                'stat_type': stat_type.value,
                'value': value,
                'modifier_type': modifier_type,
                'source': source,
                'duration': duration
            })
            
            logger.debug(f"Добавлен модификатор {stat_type.value} для {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления модификатора для {entity_id}: {e}")
            return False
    
    def _apply_modifier_to_stats(self, entity_id: str, modifier: StatModifier) -> None:
        """Применение модификатора к характеристикам"""
        try:
            if entity_id not in self.entity_stats:
                return
            
            stats = self.entity_stats[entity_id]
            
            if modifier.modifier_type == 'flat':
                # Плоский модификатор
                if modifier.stat_type == StatType.HEALTH:
                    stats.health = max(0, min(stats.max_health, stats.health + int(modifier.value)))
                elif modifier.stat_type == StatType.MANA:
                    stats.mana = max(0, min(stats.max_mana, stats.mana + int(modifier.value)))
                elif modifier.stat_type == StatType.STAMINA:
                    stats.stamina = max(0, min(stats.max_stamina, stats.stamina + int(modifier.value)))
                elif modifier.stat_type == StatType.ATTACK:
                    stats.attack = max(0, stats.attack + int(modifier.value))
                elif modifier.stat_type == StatType.DEFENSE:
                    stats.defense = max(0, stats.defense + int(modifier.value))
                elif modifier.stat_type == StatType.SPEED:
                    stats.speed = max(0.1, stats.speed + modifier.value)
                elif modifier.stat_type == StatType.STRENGTH:
                    stats.strength = max(1, stats.strength + int(modifier.value))
                elif modifier.stat_type == StatType.AGILITY:
                    stats.agility = max(1, stats.agility + int(modifier.value))
                elif modifier.stat_type == StatType.INTELLIGENCE:
                    stats.intelligence = max(1, stats.intelligence + int(modifier.value))
                elif modifier.stat_type == StatType.CONSTITUTION:
                    stats.constitution = max(1, stats.constitution + int(modifier.value))
                elif modifier.stat_type == StatType.WISDOM:
                    stats.wisdom = max(1, stats.wisdom + int(modifier.value))
                elif modifier.stat_type == StatType.CHARISMA:
                    stats.charisma = max(1, stats.charisma + int(modifier.value))
            
            elif modifier.modifier_type == 'percent':
                # Процентный модификатор
                if modifier.stat_type == StatType.HEALTH:
                    stats.health = int(stats.health * (1 + modifier.value))
                elif modifier.stat_type == StatType.MANA:
                    stats.mana = int(stats.mana * (1 + modifier.value))
                elif modifier.stat_type == StatType.STAMINA:
                    stats.stamina = int(stats.stamina * (1 + modifier.value))
                elif modifier.stat_type == StatType.ATTACK:
                    stats.attack = int(stats.attack * (1 + modifier.value))
                elif modifier.stat_type == StatType.DEFENSE:
                    stats.defense = int(stats.defense * (1 + modifier.value))
                elif modifier.stat_type == StatType.SPEED:
                    stats.speed = stats.speed * (1 + modifier.value)
            
            elif modifier.modifier_type == 'multiplier':
                # Множительный модификатор
                if modifier.stat_type == StatType.HEALTH:
                    stats.health = int(stats.health * modifier.value)
                elif modifier.stat_type == StatType.MANA:
                    stats.mana = int(stats.mana * modifier.value)
                elif modifier.stat_type == StatType.STAMINA:
                    stats.stamina = int(stats.stamina * modifier.value)
                elif modifier.stat_type == StatType.ATTACK:
                    stats.attack = int(stats.attack * modifier.value)
                elif modifier.stat_type == StatType.DEFENSE:
                    stats.defense = int(stats.defense * modifier.value)
                elif modifier.stat_type == StatType.SPEED:
                    stats.speed = stats.speed * modifier.value
            
            # Обновляем максимальные значения
            if modifier.stat_type == StatType.HEALTH:
                stats.health = min(stats.health, stats.max_health)
            elif modifier.stat_type == StatType.MANA:
                stats.mana = min(stats.mana, stats.max_mana)
            elif modifier.stat_type == StatType.STAMINA:
                stats.stamina = min(stats.stamina, stats.max_stamina)
            
        except Exception as e:
            logger.error(f"Ошибка применения модификатора для {entity_id}: {e}")
    
    def get_entity_stats(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение характеристик сущности"""
        try:
            if entity_id not in self.entity_stats:
                return None
            
            stats = self.entity_stats[entity_id]
            
            return {
                'entity_id': stats.entity_id,
                'level': stats.level,
                'experience': stats.experience,
                'experience_to_next': stats.experience_to_next,
                'health': stats.health,
                'max_health': stats.max_health,
                'mana': stats.mana,
                'max_mana': stats.max_mana,
                'stamina': stats.stamina,
                'max_stamina': stats.max_stamina,
                'attack': stats.attack,
                'defense': stats.defense,
                'speed': stats.speed,
                'critical_chance': stats.critical_chance,
                'critical_multiplier': stats.critical_multiplier,
                'dodge_chance': stats.dodge_chance,
                'block_chance': stats.block_chance,
                'strength': stats.strength,
                'agility': stats.agility,
                'intelligence': stats.intelligence,
                'constitution': stats.constitution,
                'wisdom': stats.wisdom,
                'charisma': stats.charisma,
                'resistances': {damage_type.value: value for damage_type, value in stats.resistances.items()},
                'luck': stats.luck,
                'reputation': stats.reputation,
                'fame': stats.fame
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения характеристик сущности {entity_id}: {e}")
            return None
    
    def get_stat_modifiers(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение модификаторов сущности"""
        try:
            if entity_id not in self.stat_modifiers:
                return []
            
            modifiers_info = []
            
            for modifier in self.stat_modifiers[entity_id]:
                modifiers_info.append({
                    'modifier_id': modifier.modifier_id,
                    'stat_type': modifier.stat_type.value,
                    'value': modifier.value,
                    'modifier_type': modifier.modifier_type,
                    'source': modifier.source,
                    'duration': modifier.duration,
                    'start_time': modifier.start_time,
                    'stackable': modifier.stackable,
                    'max_stacks': modifier.max_stacks,
                    'current_stacks': modifier.current_stacks
                })
            
            return modifiers_info
            
        except Exception as e:
            logger.error(f"Ошибка получения модификаторов сущности {entity_id}: {e}")
            return []
    
    def remove_stat_modifier(self, entity_id: str, modifier_id: str) -> bool:
        """Удаление модификатора характеристики"""
        try:
            if entity_id not in self.stat_modifiers:
                return False
            
            modifiers = self.stat_modifiers[entity_id]
            modifier_to_remove = None
            
            for modifier in modifiers:
                if modifier.modifier_id == modifier_id:
                    modifier_to_remove = modifier
                    break
            
            if not modifier_to_remove:
                return False
            
            # Удаляем модификатор
            modifiers.remove(modifier_to_remove)
            
            # Удаляем пустые записи
            if not modifiers:
                del self.stat_modifiers[entity_id]
            
            logger.debug(f"Удален модификатор {modifier_id} у {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления модификатора {modifier_id} у {entity_id}: {e}")
            return False
    
    def set_stat_value(self, entity_id: str, stat_type: StatType, value: Any) -> bool:
        """Установка значения характеристики"""
        try:
            if entity_id not in self.entity_stats:
                logger.warning(f"Характеристики сущности {entity_id} не найдены")
                return False
            
            stats = self.entity_stats[entity_id]
            
            if hasattr(stats, stat_type.value):
                old_value = getattr(stats, stat_type.value)
                setattr(stats, stat_type.value, value)
                
                # Записываем в историю
                current_time = time.time()
                self.stats_history.append({
                    'timestamp': current_time,
                    'action': 'stat_set',
                    'entity_id': entity_id,
                    'stat_type': stat_type.value,
                    'old_value': old_value,
                    'new_value': value
                })
                
                self.system_stats['stats_updated_today'] += 1
                logger.debug(f"Характеристика {stat_type.value} сущности {entity_id} изменена с {old_value} на {value}")
                return True
            else:
                logger.warning(f"Характеристика {stat_type.value} не найдена")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка установки характеристики {stat_type.value} для {entity_id}: {e}")
            return False
    
    def calculate_damage(self, attacker_id: str, target_id: str, base_damage: int, 
                        damage_type: DamageType) -> int:
        """Расчет урона с учетом характеристик"""
        try:
            if attacker_id not in self.entity_stats or target_id not in self.entity_stats:
                return base_damage
            
            attacker_stats = self.entity_stats[attacker_id]
            target_stats = self.entity_stats[target_id]
            
            # Базовый урон
            final_damage = base_damage
            
            # Модификатор от атаки
            attack_modifier = attacker_stats.attack / 100.0
            final_damage = int(final_damage * (1 + attack_modifier))
            
            # Модификатор от защиты
            defense_modifier = target_stats.defense / 100.0
            final_damage = int(final_damage * (1 - defense_modifier))
            
            # Сопротивление к типу урона
            if damage_type in target_stats.resistances:
                resistance = target_stats.resistances[damage_type]
                final_damage = int(final_damage * (1 - resistance))
            
            # Критический удар
            if random.random() < attacker_stats.critical_chance:
                final_damage = int(final_damage * attacker_stats.critical_multiplier)
            
            # Уклонение
            if random.random() < target_stats.dodge_chance:
                final_damage = 0
            
            # Блок
            if random.random() < target_stats.block_chance:
                final_damage = int(final_damage * 0.5)
            
            return max(1, final_damage)
            
        except Exception as e:
            logger.error(f"Ошибка расчета урона: {e}")
            return base_damage
    
    def recalculate_stats_from_attributes(self, entity_id: str) -> bool:
        """Пересчет характеристик из атрибутов"""
        try:
            if entity_id not in self.entity_stats:
                return False
            
            stats = self.entity_stats[entity_id]
            
            # Собираем текущие атрибуты
            attributes = {
                "strength": stats.strength,
                "agility": stats.agility,
                "intelligence": stats.intelligence,
                "constitution": stats.constitution,
                "wisdom": stats.wisdom,
                "charisma": stats.charisma,
                "luck": stats.luck
            }
            
            # Рассчитываем новые характеристики
            calculated_stats = calculate_stats_from_attributes(BASE_STATS, attributes)
            
            # Применяем рассчитанные характеристики
            old_health = stats.health
            old_mana = stats.mana
            old_stamina = stats.stamina
            
            stats.max_health = calculated_stats["health"]
            stats.max_mana = calculated_stats["mana"]
            stats.max_stamina = calculated_stats["stamina"]
            
            # Сохраняем пропорции текущих значений
            if old_health > 0:
                health_ratio = old_health / stats.max_health
                stats.health = int(stats.max_health * health_ratio)
            
            if old_mana > 0:
                mana_ratio = old_mana / stats.max_mana
                stats.mana = int(stats.max_mana * mana_ratio)
            
            if old_stamina > 0:
                stamina_ratio = old_stamina / stats.max_stamina
                stats.stamina = int(stats.max_stamina * stamina_ratio)
            
            logger.debug(f"Пересчитаны характеристики для сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка пересчета характеристик для {entity_id}: {e}")
            return False

