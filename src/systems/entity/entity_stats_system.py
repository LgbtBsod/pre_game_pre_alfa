#!/usr/bin/env python3
"""
Система характеристик сущностей - управление статистиками и характеристиками
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
class StatType(Enum):
from ...core.interfaces import ISystem, SystemPriority, SystemState

logger = logging.getLogger(__name__)


    """Типы характеристик"""
    HEALTH = "health"
    MANA = "mana"
    STAMINA = "stamina"
    STRENGTH = "strength"
    AGILITY = "agility"
    INTELLIGENCE = "intelligence"
    VITALITY = "vitality"
    WISDOM = "wisdom"
    CHARISMA = "charisma"
    LUCK = "luck"

class StatCategory(Enum):
    """Категории характеристик"""
    PRIMARY = "primary"      # Основные характеристики
    SECONDARY = "secondary"  # Вторичные характеристики
    DERIVED = "derived"      # Производные характеристики
    TEMPORARY = "temporary"  # Временные характеристики

@dataclass
class StatModifier:
    """Модификатор характеристики"""
    modifier_id: str
    stat_type: StatType
    value: float
    modifier_type: str  # 'flat', 'percentage', 'multiplier'
    source: str
    duration: float  # -1 для постоянных
    timestamp: float
    active: bool = True

@dataclass
class EntityStats:
    """Характеристики сущности"""
    entity_id: str
    base_stats: Dict[StatType, float]
    current_stats: Dict[StatType, float]
    max_stats: Dict[StatType, float]
    stat_modifiers: List[StatModifier]
    level: int
    experience: int
    experience_to_next: int
    last_update: float

class EntityStatsSystem(ISystem):
    """Система характеристик сущностей"""
    
    def __init__(self):
        self._system_name = "entity_stats"
        self._system_priority = SystemPriority.NORMAL
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Характеристики сущностей
        self.entity_stats: Dict[str, EntityStats] = {}
        
        # Шаблоны характеристик по уровням
        self.level_templates: Dict[int, Dict[StatType, float]] = {}
        
        # Формулы расчета производных характеристик
        self.derived_stat_formulas: Dict[StatType, str] = {}
        
        # Настройки системы
        self.max_level = 100
        self.base_experience = 100
        self.experience_multiplier = 1.5
        
        # Статистика системы
        self.system_stats = {
            'entities_count': 0,
            'stats_updated': 0,
            'modifiers_applied': 0,
            'levels_gained': 0,
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
        """Инициализация системы характеристик сущностей"""
        try:
            logger.info("Инициализация системы характеристик сущностей...")
            
            # Инициализируем шаблоны уровней
            self._initialize_level_templates()
            
            # Настраиваем формулы производных характеристик
            self._setup_derived_stat_formulas()
            
            # Создаем базовые характеристики
            self._create_base_stats()
            
            self._system_state = SystemState.READY
            logger.info("Система характеристик сущностей успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы характеристик сущностей: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы характеристик сущностей"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем характеристики всех сущностей
            self._update_all_entity_stats(delta_time)
            
            # Обрабатываем истекшие модификаторы
            self._process_expired_modifiers()
            
            # Обновляем статистику системы
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы характеристик сущностей: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы характеристик сущностей"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система характеристик сущностей приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы характеристик сущностей: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы характеристик сущностей"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система характеристик сущностей возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы характеристик сущностей: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы характеристик сущностей"""
        try:
            logger.info("Очистка системы характеристик сущностей...")
            
            # Очищаем характеристики сущностей
            self.entity_stats.clear()
            
            # Очищаем шаблоны
            self.level_templates.clear()
            
            # Очищаем формулы
            self.derived_stat_formulas.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'entities_count': 0,
                'stats_updated': 0,
                'modifiers_applied': 0,
                'levels_gained': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система характеристик сущностей очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы характеристик сущностей: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'entities_count': len(self.entity_stats),
            'max_level': self.max_level,
            'base_experience': self.base_experience,
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_stats_created":
                return self._handle_stats_created(event_data)
            elif event_type == "entity_stats_updated":
                return self._handle_stats_updated(event_data)
            elif event_type == "entity_stats_destroyed":
                return self._handle_stats_destroyed(event_data)
            elif event_type == "stat_modifier_applied":
                return self._handle_modifier_applied(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def create_entity_stats(self, entity_id: str, base_stats: Dict[str, Any]) -> bool:
        """Создание характеристик сущности"""
        try:
            if entity_id in self.entity_stats:
                logger.warning(f"Характеристики для сущности {entity_id} уже существуют")
                return False
            
            # Конвертируем строковые ключи в StatType
            converted_base_stats = {}
            for stat_key, stat_value in base_stats.items():
                try:
                    stat_type = StatType(stat_key)
                    converted_base_stats[stat_type] = float(stat_value)
                except ValueError:
                    logger.warning(f"Неизвестный тип характеристики: {stat_key}")
                    continue
            
            # Создаем базовые характеристики
            entity_stats = EntityStats(
                entity_id=entity_id,
                base_stats=converted_base_stats,
                current_stats=converted_base_stats.copy(),
                max_stats=converted_base_stats.copy(),
                stat_modifiers=[],
                level=1,
                experience=0,
                experience_to_next=self.base_experience,
                last_update=time.time()
            )
            
            # Добавляем в систему
            self.entity_stats[entity_id] = entity_stats
            self.system_stats['entities_count'] = len(self.entity_stats)
            
            logger.info(f"Созданы характеристики для сущности: {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания характеристик для сущности {entity_id}: {e}")
            return False
    
    def modify_entity_stats(self, entity_id: str, stat_modifications: Dict[str, Any]) -> bool:
        """Модификация характеристик сущности"""
        try:
            if entity_id not in self.entity_stats:
                logger.warning(f"Характеристики для сущности {entity_id} не найдены")
                return False
            
            entity_stats = self.entity_stats[entity_id]
            
            # Применяем модификации
            for stat_key, modification in stat_modifications.items():
                try:
                    stat_type = StatType(stat_key)
                    
                    if 'value' in modification:
                        # Прямое изменение базовой характеристики
                        old_value = entity_stats.base_stats.get(stat_type, 0.0)
                        new_value = old_value + modification['value']
                        entity_stats.base_stats[stat_type] = max(0.0, new_value)
                        
                        # Обновляем текущие и максимальные значения
                        entity_stats.current_stats[stat_type] = entity_stats.base_stats[stat_type]
                        entity_stats.max_stats[stat_type] = entity_stats.base_stats[stat_type]
                    
                    if 'modifier' in modification:
                        # Применяем модификатор
                        modifier_data = modification['modifier']
                        modifier = StatModifier(
                            modifier_id=f"mod_{len(entity_stats.stat_modifiers)}",
                            stat_type=stat_type,
                            value=modifier_data.get('value', 0.0),
                            modifier_type=modifier_data.get('type', 'flat'),
                            source=modifier_data.get('source', 'unknown'),
                            duration=modifier_data.get('duration', -1.0),
                            timestamp=time.time()
                        )
                        
                        entity_stats.stat_modifiers.append(modifier)
                        self.system_stats['modifiers_applied'] += 1
                        
                except ValueError:
                    logger.warning(f"Неизвестный тип характеристики: {stat_key}")
                    continue
            
            # Пересчитываем производные характеристики
            self._recalculate_derived_stats(entity_stats)
            
            # Обновляем время последнего изменения
            entity_stats.last_update = time.time()
            
            logger.debug(f"Характеристики сущности {entity_id} модифицированы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка модификации характеристик сущности {entity_id}: {e}")
            return False
    
    def get_entity_stats(self, entity_id: str) -> Dict[str, Any]:
        """Получение характеристик сущности"""
        try:
            if entity_id not in self.entity_stats:
                return {}
            
            entity_stats = self.entity_stats[entity_id]
            
            # Конвертируем StatType в строки для JSON
            stats_data = {
                'entity_id': entity_stats.entity_id,
                'level': entity_stats.level,
                'experience': entity_stats.experience,
                'experience_to_next': entity_stats.experience_to_next,
                'base_stats': {stat.value: value for stat, value in entity_stats.base_stats.items()},
                'current_stats': {stat.value: value for stat, value in entity_stats.current_stats.items()},
                'max_stats': {stat.value: value for stat, value in entity_stats.max_stats.items()},
                'modifiers_count': len(entity_stats.stat_modifiers),
                'last_update': entity_stats.last_update
            }
            
            return stats_data
            
        except Exception as e:
            logger.error(f"Ошибка получения характеристик сущности {entity_id}: {e}")
            return {}
    
    def calculate_derived_stats(self, entity_id: str) -> Dict[str, Any]:
        """Расчет производных характеристик"""
        try:
            if entity_id not in self.entity_stats:
                return {}
            
            entity_stats = self.entity_stats[entity_id]
            
            # Пересчитываем производные характеристики
            self._recalculate_derived_stats(entity_stats)
            
            # Возвращаем обновленные характеристики
            return self.get_entity_stats(entity_id)
            
        except Exception as e:
            logger.error(f"Ошибка расчета производных характеристик для сущности {entity_id}: {e}")
            return {}
    
    def add_experience(self, entity_id: str, experience_amount: int) -> bool:
        """Добавление опыта сущности"""
        try:
            if entity_id not in self.entity_stats:
                return False
            
            entity_stats = self.entity_stats[entity_id]
            
            # Добавляем опыт
            entity_stats.experience += experience_amount
            
            # Проверяем повышение уровня
            while entity_stats.experience >= entity_stats.experience_to_next:
                if self._level_up(entity_stats):
                    self.system_stats['levels_gained'] += 1
                else:
                    break
            
            logger.debug(f"Добавлен опыт {experience_amount} для сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления опыта для сущности {entity_id}: {e}")
            return False
    
    def _initialize_level_templates(self) -> None:
        """Инициализация шаблонов уровней"""
        try:
            for level in range(1, self.max_level + 1):
                # Базовые характеристики для уровня
                level_stats = {
                    StatType.STRENGTH: 10 + level * 2,
                    StatType.AGILITY: 10 + level * 1.5,
                    StatType.INTELLIGENCE: 10 + level * 1.8,
                    StatType.VITALITY: 10 + level * 2.2,
                    StatType.WISDOM: 10 + level * 1.3,
                    StatType.CHARISMA: 10 + level * 1.0,
                    StatType.LUCK: 5 + level * 0.5
                }
                
                self.level_templates[level] = level_stats
                
            logger.debug("Шаблоны уровней инициализированы")
            
        except Exception as e:
            logger.warning(f"Не удалось инициализировать шаблоны уровней: {e}")
    
    def _setup_derived_stat_formulas(self) -> None:
        """Настройка формул производных характеристик"""
        try:
            # Формулы для расчета производных характеристик
            self.derived_stat_formulas = {
                StatType.HEALTH: "vitality * 10 + strength * 5",
                StatType.MANA: "intelligence * 8 + wisdom * 4",
                StatType.STAMINA: "vitality * 6 + agility * 3"
            }
            
            logger.debug("Формулы производных характеристик настроены")
            
        except Exception as e:
            logger.warning(f"Не удалось настроить формулы производных характеристик: {e}")
    
    def _create_base_stats(self) -> None:
        """Создание базовых характеристик"""
        try:
            # Здесь можно создать базовые характеристики для разных типов сущностей
            pass
        except Exception as e:
            logger.warning(f"Не удалось создать базовые характеристики: {e}")
    
    def _update_all_entity_stats(self, delta_time: float) -> None:
        """Обновление характеристик всех сущностей"""
        try:
            for entity_stats in self.entity_stats.values():
                self._update_entity_stats(entity_stats, delta_time)
                self.system_stats['stats_updated'] += 1
                
        except Exception as e:
            logger.warning(f"Ошибка обновления характеристик сущностей: {e}")
    
    def _update_entity_stats(self, entity_stats: EntityStats, delta_time: float) -> None:
        """Обновление характеристик конкретной сущности"""
        try:
            # Восстанавливаем характеристики со временем
            if entity_stats.current_stats.get(StatType.HEALTH, 0) < entity_stats.max_stats.get(StatType.HEALTH, 0):
                recovery_rate = entity_stats.base_stats.get(StatType.VITALITY, 10) * 0.1 * delta_time
                current_health = entity_stats.current_stats.get(StatType.HEALTH, 0)
                max_health = entity_stats.max_stats.get(StatType.HEALTH, 0)
                entity_stats.current_stats[StatType.HEALTH] = min(max_health, current_health + recovery_rate)
            
            if entity_stats.current_stats.get(StatType.MANA, 0) < entity_stats.max_stats.get(StatType.MANA, 0):
                recovery_rate = entity_stats.base_stats.get(StatType.INTELLIGENCE, 10) * 0.05 * delta_time
                current_mana = entity_stats.current_stats.get(StatType.MANA, 0)
                max_mana = entity_stats.max_stats.get(StatType.MANA, 0)
                entity_stats.current_stats[StatType.MANA] = min(max_mana, current_mana + recovery_rate)
            
            if entity_stats.current_stats.get(StatType.STAMINA, 0) < entity_stats.max_stats.get(StatType.STAMINA, 0):
                recovery_rate = entity_stats.base_stats.get(StatType.VITALITY, 10) * 0.15 * delta_time
                current_stamina = entity_stats.current_stats.get(StatType.STAMINA, 0)
                max_stamina = entity_stats.max_stats.get(StatType.STAMINA, 0)
                entity_stats.current_stats[StatType.STAMINA] = min(max_stamina, current_stamina + recovery_rate)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления характеристик сущности {entity_stats.entity_id}: {e}")
    
    def _process_expired_modifiers(self) -> None:
        """Обработка истекших модификаторов"""
        try:
            current_time = time.time()
            
            for entity_stats in self.entity_stats.values():
                # Удаляем истекшие модификаторы
                expired_modifiers = []
                for modifier in entity_stats.stat_modifiers:
                    if modifier.duration > 0 and current_time - modifier.timestamp > modifier.duration:
                        expired_modifiers.append(modifier)
                        modifier.active = False
                
                # Удаляем истекшие модификаторы
                for modifier in expired_modifiers:
                    entity_stats.stat_modifiers.remove(modifier)
                
                # Пересчитываем характеристики если были удалены модификаторы
                if expired_modifiers:
                    self._recalculate_derived_stats(entity_stats)
                    
        except Exception as e:
            logger.warning(f"Ошибка обработки истекших модификаторов: {e}")
    
    def _recalculate_derived_stats(self, entity_stats: EntityStats) -> None:
        """Пересчет производных характеристик"""
        try:
            # Применяем все активные модификаторы
            for modifier in entity_stats.stat_modifiers:
                if modifier.active:
                    self._apply_modifier(entity_stats, modifier)
            
            # Пересчитываем производные характеристики
            for stat_type, formula in self.derived_stat_formulas.items():
                value = self._evaluate_formula(formula, entity_stats.base_stats)
                entity_stats.base_stats[stat_type] = value
                entity_stats.current_stats[stat_type] = value
                entity_stats.max_stats[stat_type] = value
            
            # Ограничиваем текущие значения максимальными
            for stat_type in entity_stats.current_stats:
                max_value = entity_stats.max_stats.get(stat_type, 0)
                current_value = entity_stats.current_stats.get(stat_type, 0)
                entity_stats.current_stats[stat_type] = min(max_value, current_value)
                
        except Exception as e:
            logger.warning(f"Ошибка пересчета производных характеристик: {e}")
    
    def _apply_modifier(self, entity_stats: EntityStats, modifier: StatModifier) -> None:
        """Применение модификатора"""
        try:
            stat_type = modifier.stat_type
            
            if modifier.modifier_type == 'flat':
                # Плоское изменение
                entity_stats.base_stats[stat_type] += modifier.value
                
            elif modifier.modifier_type == 'percentage':
                # Процентное изменение
                base_value = entity_stats.base_stats.get(stat_type, 0)
                entity_stats.base_stats[stat_type] += base_value * modifier.value * 0.01
                
            elif modifier.modifier_type == 'multiplier':
                # Множитель
                base_value = entity_stats.base_stats.get(stat_type, 0)
                entity_stats.base_stats[stat_type] *= modifier.value
                
        except Exception as e:
            logger.warning(f"Ошибка применения модификатора: {e}")
    
    def _evaluate_formula(self, formula: str, base_stats: Dict[StatType, float]) -> float:
        """Вычисление формулы"""
        try:
            # Простая замена переменных в формуле
            result = formula
            for stat_type, value in base_stats.items():
                result = result.replace(stat_type.value, str(value))
            
            # Безопасное вычисление
            try:
                return eval(result)
            except:
                return 0.0
                
        except Exception as e:
            logger.warning(f"Ошибка вычисления формулы {formula}: {e}")
            return 0.0
    
    def _level_up(self, entity_stats: EntityStats) -> bool:
        """Повышение уровня сущности"""
        try:
            if entity_stats.level >= self.max_level:
                return False
            
            # Увеличиваем уровень
            entity_stats.level += 1
            
            # Вычитаем потраченный опыт
            entity_stats.experience -= entity_stats.experience_to_next
            
            # Рассчитываем опыт для следующего уровня
            entity_stats.experience_to_next = int(self.base_experience * 
                                               (self.experience_multiplier ** (entity_stats.level - 1)))
            
            # Применяем характеристики нового уровня
            if entity_stats.level in self.level_templates:
                level_stats = self.level_templates[entity_stats.level]
                for stat_type, stat_value in level_stats.items():
                    if stat_type in entity_stats.base_stats:
                        entity_stats.base_stats[stat_type] = stat_value
            
            # Пересчитываем производные характеристики
            self._recalculate_derived_stats(entity_stats)
            
            logger.info(f"Сущность {entity_stats.entity_id} повысила уровень до {entity_stats.level}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка повышения уровня для сущности {entity_stats.entity_id}: {e}")
            return False
    
    def _handle_stats_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания характеристик"""
        try:
            entity_id = event_data.get('entity_id')
            base_stats = event_data.get('base_stats', {})
            
            if entity_id and base_stats:
                return self.create_entity_stats(entity_id, base_stats)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания характеристик: {e}")
            return False
    
    def _handle_stats_updated(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события обновления характеристик"""
        try:
            entity_id = event_data.get('entity_id')
            modifications = event_data.get('modifications', {})
            
            if entity_id and modifications:
                return self.modify_entity_stats(entity_id, modifications)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события обновления характеристик: {e}")
            return False
    
    def _handle_stats_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения характеристик"""
        try:
            entity_id = event_data.get('entity_id')
            
            if entity_id and entity_id in self.entity_stats:
                del self.entity_stats[entity_id]
                self.system_stats['entities_count'] = len(self.entity_stats)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события уничтожения характеристик: {e}")
            return False
    
    def _handle_modifier_applied(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события применения модификатора"""
        try:
            entity_id = event_data.get('entity_id')
            stat_type = event_data.get('stat_type')
            modifier_data = event_data.get('modifier', {})
            
            if entity_id and stat_type and modifier_data:
                modifications = {
                    stat_type: {'modifier': modifier_data}
                }
                return self.modify_entity_stats(entity_id, modifications)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события применения модификатора: {e}")
            return False

