#!/usr/bin/env python3
"""Базовая сущность игры"""

import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from src.core.architecture import BaseComponent, ComponentType, Priority, LifecycleState
from src.core.constants import constants_manager, EntityType, EntityState, ToughnessType, StanceState
from src.core.state_manager import StateManager, StateType
from src.systems.attributes.attribute_system import AttributeSystem, AttributeSet, AttributeModifier, StatModifier, BaseAttribute, DerivedStat

logger = logging.getLogger(__name__)

@dataclass
class EntityStats:
    """Статистика сущности"""
    # Базовые атрибуты
    strength: float = 10.0
    agility: float = 10.0
    intelligence: float = 10.0
    vitality: float = 10.0
    wisdom: float = 10.0
    charisma: float = 10.0
    luck: float = 10.0
    endurance: float = 10.0
    
    # Производные характеристики (рассчитываются автоматически)
    health: float = 100.0
    mana: float = 50.0
    stamina: float = 100.0
    physical_damage: float = 10.0
    magical_damage: float = 5.0
    defense: float = 5.0
    attack_speed: float = 1.0
    skill_recovery_speed: float = 1.0
    health_regen: float = 1.0
    mana_regen: float = 2.0
    stamina_regen: float = 3.0
    critical_chance: float = 0.05
    critical_damage: float = 1.5
    dodge_chance: float = 0.05
    block_chance: float = 0.05
    magic_resistance: float = 0.0
    max_weight: float = 50.0
    movement_speed: float = 1.0
    
    # Стойкость
    toughness: float = 100.0
    max_toughness: float = 100.0
    toughness_recovery: float = 10.0
    toughness_type: ToughnessType = ToughnessType.PHYSICAL

@dataclass
class ToughnessData:
    """Данные стойкости"""
    current_toughness: float = 100.0
    stance_state: StanceState = StanceState.NORMAL
    recovery_rate: float = 10.0
    stun_end_time: float = 0.0
    last_break_time: float = 0.0
    break_count: int = 0

@dataclass
class EntityComponent:
    """Компонент сущности"""
    component_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    active: bool = True

class BaseEntity(BaseComponent):
    """Базовая сущность игры"""
    
    def __init__(self, entity_id: str, entity_type: EntityType, name: str = ""):
        super().__init__(
            component_id=f"entity_{entity_id}",
            component_type=ComponentType.ENTITY,
            priority=Priority.MEDIUM
        )
        
        # Основные свойства
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.name = name or f"{entity_type.value}_{entity_id}"
        
        # Архитектурные компоненты
        self.state_manager: Optional[StateManager] = None
        self.attribute_system: Optional[AttributeSystem] = None
        
        # Состояние сущности
        self.entity_state = EntityState.ALIVE
        self.position = (0.0, 0.0, 0.0)
        self.rotation = (0.0, 0.0, 0.0)
        self.scale = (1.0, 1.0, 1.0)
        
        # Статистика и характеристики
        self.entity_stats = EntityStats()
        self.toughness_data = ToughnessData()
        
        # Модификаторы
        self.attribute_modifiers: List[AttributeModifier] = []
        self.stat_modifiers: List[StatModifier] = []
        
        # Компоненты
        self.components: Dict[str, EntityComponent] = {}
        
        # Настройки сущности
        self.entity_settings = {
            'toughness_enabled': True,
            'auto_regen_enabled': True,
            'component_system_enabled': True,
            'attribute_system_enabled': True
        }
        
        # Статистика сущности
        self.entity_stats_tracking = {
            'damage_dealt': 0.0,
            'damage_taken': 0.0,
            'healing_received': 0.0,
            'critical_hits': 0,
            'dodges': 0,
            'blocks': 0,
            'toughness_damage_dealt': 0.0,
            'toughness_breaks_caused': 0,
            'toughness_damage_taken': 0.0,
            'toughness_breaks_suffered': 0,
            'total_stun_time': 0.0,
            'creation_time': time.time(),
            'last_update_time': time.time()
        }
    
    def set_architecture_components(self, state_manager: StateManager, attribute_system: AttributeSystem):
        """Установка архитектурных компонентов"""
        self.state_manager = state_manager
        self.attribute_system = attribute_system
        logger.info(f"Архитектурные компоненты установлены в {self.name}")
    
    def _register_entity_states(self):
        """Регистрация состояний сущности"""
        if self.state_manager:
            self.state_manager.set_state(
                f"{self.component_id}_stats",
                self.entity_stats.__dict__,
                StateType.ENTITY_STATS
            )
            
            self.state_manager.set_state(
                f"{self.component_id}_toughness",
                self.toughness_data.__dict__,
                StateType.ENTITY_STATE
            )
            
            self.state_manager.set_state(
                f"{self.component_id}_tracking",
                self.entity_stats_tracking,
                StateType.STATISTICS
            )
    
    def initialize(self) -> bool:
        """Инициализация сущности"""
        try:
            logger.info(f"Инициализация сущности {self.name}...")
            
            # Инициализация стойкости
            self._initialize_toughness()
            
            # Создание компонентов
            self._create_default_components()
            
            # Регистрация состояний
            self._register_entity_states()
            
            # Расчет начальных характеристик
            self._recalculate_stats()
            
            self.system_state = LifecycleState.READY
            logger.info(f"Сущность {self.name} инициализирована успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сущности {self.name}: {e}")
            self.system_state = LifecycleState.ERROR
            return False
    
    def start(self) -> bool:
        """Запуск сущности"""
        try:
            logger.info(f"Запуск сущности {self.name}...")
            
            if self.system_state != LifecycleState.READY:
                logger.error(f"Сущность {self.name} не готова к запуску")
                return False
            
            self.system_state = LifecycleState.RUNNING
            logger.info(f"Сущность {self.name} запущена успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска сущности {self.name}: {e}")
            self.system_state = LifecycleState.ERROR
            return False
    
    def update(self, delta_time: float):
        """Обновление сущности"""
        if self.system_state != LifecycleState.RUNNING:
            return
        
        try:
            start_time = time.time()
            
            # Обновление стойкости
            self._update_toughness(delta_time)
            
            # Обновление регенерации
            if self.entity_settings['auto_regen_enabled']:
                self._update_regeneration(delta_time)
            
            # Обновление компонентов
            if self.entity_settings['component_system_enabled']:
                self._update_components(delta_time)
            
            # Обновление статистики
            self._update_stats(delta_time)
            
            # Обновление состояний в менеджере состояний
            if self.state_manager:
                self.state_manager.set_state(
                    f"{self.system_name}_stats",
                    self.entity_stats.__dict__,
                    StateType.ENTITY_STATS
                )
                
                self.state_manager.set_state(
                    f"{self.system_name}_toughness",
                    self.toughness_data.__dict__,
                    StateType.ENTITY_STATE
                )
                
        except Exception as e:
            logger.error(f"Ошибка обновления сущности {self.name}: {e}")
    
    def stop(self) -> bool:
        """Остановка сущности"""
        try:
            logger.info(f"Остановка сущности {self.name}...")
            
            self.system_state = LifecycleState.STOPPED
            logger.info(f"Сущность {self.name} остановлена успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка остановки сущности {self.name}: {e}")
            return False
    
    def destroy(self) -> bool:
        """Уничтожение сущности"""
        try:
            logger.info(f"Уничтожение сущности {self.name}...")
            
            # Очистка компонентов
            self.components.clear()
            
            # Очистка модификаторов
            self.attribute_modifiers.clear()
            self.stat_modifiers.clear()
            
            self.system_state = LifecycleState.DESTROYED
            logger.info(f"Сущность {self.name} уничтожена успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения сущности {self.name}: {e}")
            return False
    
    def _initialize_toughness(self):
        """Инициализация стойкости"""
        if not self.entity_settings['toughness_enabled']:
            return
        
        toughness_constants = constants_manager.get_toughness_constants()
        base_toughness = toughness_constants['base_toughness'].get(self.entity_type.value, 100)
        
        # Устанавливаем базовую стойкость
        self.toughness_data.current_toughness = base_toughness
        self.entity_stats.max_toughness = base_toughness
        self.entity_stats.toughness = base_toughness
        
        # Определяем тип стойкости на основе типа сущности
        if self.entity_type == EntityType.BOSS:
            self.entity_stats.toughness_type = ToughnessType.UNIVERSAL
        elif self.entity_type == EntityType.ENEMY:
            # Случайный тип стойкости для врагов
            import random
            toughness_types = list(ToughnessType)
            self.entity_stats.toughness_type = random.choice(toughness_types)
        else:
            self.entity_stats.toughness_type = ToughnessType.PHYSICAL
    
    def _update_toughness(self, delta_time: float):
        """Обновление стойкости"""
        if not self.entity_settings['toughness_enabled']:
            return
        
        # Восстановление стойкости
        self._recover_toughness(delta_time)
        
        # Проверка окончания стана
        if self.toughness_data.stun_end_time > 0 and time.time() >= self.toughness_data.stun_end_time:
            self._end_stun()
    
    def _recover_toughness(self, delta_time: float):
        """Восстановление стойкости"""
        if self.toughness_data.current_toughness >= self.entity_stats.max_toughness:
            return
        
        toughness_constants = constants_manager.get_toughness_constants()
        recovery_multiplier = toughness_constants['recovery_multipliers'].get(
            self.toughness_data.stance_state.value, 1.0
        )
        
        recovery_amount = self.entity_stats.toughness_recovery * recovery_multiplier * delta_time
        self.toughness_data.current_toughness = min(
            self.entity_stats.max_toughness,
            self.toughness_data.current_toughness + recovery_amount
        )
        
        # Обновляем стойкость в статистике
        self.entity_stats.toughness = self.toughness_data.current_toughness
    
    def _create_default_components(self):
        """Создание компонентов по умолчанию"""
        if not self.entity_settings['component_system_enabled']:
            return
        
        # Компонент стойкости
        self.components["toughness"] = EntityComponent(
            component_type="toughness",
            data={
                "enabled": self.entity_settings['toughness_enabled'],
                "type": self.entity_stats.toughness_type.value,
                "stance_state": self.toughness_data.stance_state.value
            }
        )
        
        # Компонент атрибутов
        self.components["attributes"] = EntityComponent(
            component_type="attributes",
            data={
                "enabled": self.entity_settings['attribute_system_enabled'],
                "base_stats": self.entity_stats.__dict__
            }
        )
    
    def _update_components(self, delta_time: float):
        """Обновление компонентов"""
        for component in self.components.values():
            if component.active:
                # Здесь можно добавить логику обновления компонентов
                pass
    
    def _update_regeneration(self, delta_time: float):
        """Обновление регенерации"""
        # Регенерация здоровья
        if self.entity_stats.health < self._get_max_health():
            self.entity_stats.health = min(
                self._get_max_health(),
                self.entity_stats.health + self.entity_stats.health_regen * delta_time
            )
        
        # Регенерация маны
        if self.entity_stats.mana < self._get_max_mana():
            self.entity_stats.mana = min(
                self._get_max_mana(),
                self.entity_stats.mana + self.entity_stats.mana_regen * delta_time
            )
        
        # Регенерация стамины
        if self.entity_stats.stamina < self._get_max_stamina():
            self.entity_stats.stamina = min(
                self._get_max_stamina(),
                self.entity_stats.stamina + self.entity_stats.stamina_regen * delta_time
            )
    
    def _update_stats(self, delta_time: float):
        """Обновление статистики"""
        current_time = time.time()
        self.entity_stats_tracking['last_update_time'] = current_time
        
        # Обновляем время в стане
        if self.entity_state == EntityState.STUNNED:
            self.entity_stats_tracking['total_stun_time'] += delta_time
    
    def _recalculate_stats(self):
        """Пересчет характеристик"""
        if not self.attribute_system or not self.entity_settings['attribute_system_enabled']:
            return
        
        # Создаем набор базовых атрибутов
        base_attributes = AttributeSet(
            strength=self.entity_stats.strength,
            agility=self.entity_stats.agility,
            intelligence=self.entity_stats.intelligence,
            vitality=self.entity_stats.vitality,
            wisdom=self.entity_stats.wisdom,
            charisma=self.entity_stats.charisma,
            luck=self.entity_stats.luck,
            endurance=self.entity_stats.endurance
        )
        
        # Рассчитываем характеристики
        calculated_stats = self.attribute_system.calculate_stats_for_entity(
            entity_id=self.entity_id,
            base_attributes=base_attributes,
            attribute_modifiers=self.attribute_modifiers,
            stat_modifiers=self.stat_modifiers
        )
        
        # Обновляем характеристики
        for stat_name, value in calculated_stats.items():
            if hasattr(self.entity_stats, stat_name):
                setattr(self.entity_stats, stat_name, value)
    
    def _get_max_health(self) -> float:
        """Получение максимального здоровья"""
        return self.attribute_system.calculate_stats_for_entity(
            entity_id=self.entity_id,
            base_attributes=AttributeSet(
                strength=self.entity_stats.strength,
                agility=self.entity_stats.agility,
                intelligence=self.entity_stats.intelligence,
                vitality=self.entity_stats.vitality,
                wisdom=self.entity_stats.wisdom,
                charisma=self.entity_stats.charisma,
                luck=self.entity_stats.luck,
                endurance=self.entity_stats.endurance
            ),
            attribute_modifiers=self.attribute_modifiers,
            stat_modifiers=self.stat_modifiers
        ).get('health', 100.0)
    
    def _get_max_mana(self) -> float:
        """Получение максимальной маны"""
        return self.attribute_system.calculate_stats_for_entity(
            entity_id=self.entity_id,
            base_attributes=AttributeSet(
                strength=self.entity_stats.strength,
                agility=self.entity_stats.agility,
                intelligence=self.entity_stats.intelligence,
                vitality=self.entity_stats.vitality,
                wisdom=self.entity_stats.wisdom,
                charisma=self.entity_stats.charisma,
                luck=self.entity_stats.luck,
                endurance=self.entity_stats.endurance
            ),
            attribute_modifiers=self.attribute_modifiers,
            stat_modifiers=self.stat_modifiers
        ).get('mana', 50.0)
    
    def _get_max_stamina(self) -> float:
        """Получение максимальной стамины"""
        return self.attribute_system.calculate_stats_for_entity(
            entity_id=self.entity_id,
            base_attributes=AttributeSet(
                strength=self.entity_stats.strength,
                agility=self.entity_stats.agility,
                intelligence=self.entity_stats.intelligence,
                vitality=self.entity_stats.vitality,
                wisdom=self.entity_stats.wisdom,
                charisma=self.entity_stats.charisma,
                luck=self.entity_stats.luck,
                endurance=self.entity_stats.endurance
            ),
            attribute_modifiers=self.attribute_modifiers,
            stat_modifiers=self.stat_modifiers
        ).get('stamina', 100.0)
    
    # = ПУБЛИЧНЫЕ МЕТОДЫ ДЛЯ СТОЙКОСТИ
    
    def get_toughness(self) -> float:
        """Получение текущей стойкости"""
        return self.toughness_data.current_toughness
    
    def get_max_toughness(self) -> float:
        """Получение максимальной стойкости"""
        return self.entity_stats.max_toughness
    
    def get_toughness_type(self) -> ToughnessType:
        """Получение типа стойкости"""
        return self.entity_stats.toughness_type
    
    def get_stance_state(self) -> StanceState:
        """Получение состояния стойкости"""
        return self.toughness_data.stance_state
    
    def is_stunned(self) -> bool:
        """Проверка, находится ли сущность в стане"""
        return self.entity_state == EntityState.STUNNED
    
    def get_break_damage_multiplier(self) -> float:
        """Получение множителя урона при пробитии"""
        return constants_manager.get_break_damage_multiplier(self.toughness_data.stance_state)
    
    def take_toughness_damage(self, damage: float, damage_type: ToughnessType) -> bool:
        """Получение урона по стойкости"""
        if not self.entity_settings['toughness_enabled']:
            return False
        
        # Рассчитываем эффективность урона
        effectiveness = constants_manager.get_toughness_effectiveness(
            damage_type, self.entity_stats.toughness_type
        )
        
        effective_damage = damage * effectiveness
        
        # Применяем урон
        self.toughness_data.current_toughness = max(0, self.toughness_data.current_toughness - effective_damage)
        self.entity_stats.toughness = self.toughness_data.current_toughness
        
        # Обновляем статистику
        self.entity_stats_tracking['toughness_damage_taken'] += effective_damage
        
        # Проверяем пробитие стойкости
        if self.toughness_data.current_toughness <= 0:
            self._break_toughness()
            return True
        
        return False
    
    def _break_toughness(self):
        """Пробитие стойкости"""
        self.toughness_data.break_count += 1
        self.entity_stats_tracking['toughness_breaks_suffered'] += 1
        
        # Изменяем состояние стойкости
        if self.toughness_data.stance_state == StanceState.NORMAL:
            self._change_stance_state(StanceState.WEAKENED)
        elif self.toughness_data.stance_state == StanceState.WEAKENED:
            self._change_stance_state(StanceState.BROKEN)
        else:
            self._change_stance_state(StanceState.BROKEN)
        
        # Применяем стан
        stun_duration = constants_manager.get_break_stun_duration(self.toughness_data.stance_state)
        if stun_duration > 0:
            self.toughness_data.stun_end_time = time.time() + stun_duration
            self.entity_state = EntityState.STUNNED
        
        # Обновляем компонент стойкости
        if "toughness" in self.components:
            self.components["toughness"].data["stance_state"] = self.toughness_data.stance_state.value
    
    def _change_stance_state(self, new_state: StanceState):
        """Изменение состояния стойкости"""
        self.toughness_data.stance_state = new_state
        logger.debug(f"Сущность {self.name} изменила состояние стойкости на {new_state.value}")
    
    def _end_stun(self):
        """Окончание стана"""
        self.toughness_data.stun_end_time = 0.0
        self.entity_state = EntityState.ALIVE
        logger.debug(f"Сущность {self.name} вышла из стана")
    
    # = МЕТОДЫ ДЛЯ МОДИФИКАТОРОВ
    
    def add_attribute_modifier(self, modifier: AttributeModifier):
        """Добавление модификатора атрибута"""
        self.attribute_modifiers.append(modifier)
        self._recalculate_stats()
        logger.debug(f"Добавлен модификатор атрибута {modifier.attribute.value} к {self.name}")
    
    def remove_attribute_modifier(self, modifier_id: str):
        """Удаление модификатора атрибута"""
        self.attribute_modifiers = [m for m in self.attribute_modifiers if m.modifier_id != modifier_id]
        self._recalculate_stats()
        logger.debug(f"Удален модификатор атрибута {modifier_id} из {self.name}")
    
    def add_stat_modifier(self, modifier: StatModifier):
        """Добавление модификатора характеристики"""
        self.stat_modifiers.append(modifier)
        self._recalculate_stats()
        logger.debug(f"Добавлен модификатор характеристики {modifier.stat.value} к {self.name}")
    
    def remove_stat_modifier(self, modifier_id: str):
        """Удаление модификатора характеристики"""
        self.stat_modifiers = [m for m in self.stat_modifiers if m.modifier_id != modifier_id]
        self._recalculate_stats()
        logger.debug(f"Удален модификатор характеристики {modifier_id} из {self.name}")
    
    # = МЕТОДЫ ДЛЯ КОМПОНЕНТОВ
    
    def add_component(self, component: EntityComponent):
        """Добавление компонента"""
        self.components[component.component_type] = component
        logger.debug(f"Добавлен компонент {component.component_type} к {self.name}")
    
    def remove_component(self, component_type: str):
        """Удаление компонента"""
        if component_type in self.components:
            del self.components[component_type]
            logger.debug(f"Удален компонент {component_type} из {self.name}")
    
    def get_component(self, component_type: str) -> Optional[EntityComponent]:
        """Получение компонента"""
        return self.components.get(component_type)
    
    def has_component(self, component_type: str) -> bool:
        """Проверка наличия компонента"""
        return component_type in self.components
    
    # = ИНФОРМАЦИОННЫЕ МЕТОДЫ
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о сущности"""
        return {
            'name': self.name,
            'entity_id': self.entity_id,
            'entity_type': self.entity_type.value,
            'state': self.system_state.value,
            'entity_state': self.entity_state.value,
            'position': self.position,
            'components_count': len(self.components),
            'attribute_modifiers_count': len(self.attribute_modifiers),
            'stat_modifiers_count': len(self.stat_modifiers),
            'toughness_data': {
                'current_toughness': self.toughness_data.current_toughness,
                'max_toughness': self.entity_stats.max_toughness,
                'stance_state': self.toughness_data.stance_state.value,
                'toughness_type': self.entity_stats.toughness_type.value,
                'is_stunned': self.is_stunned()
            },
            'stats_tracking': self.entity_stats_tracking
        }
    
    def reset_stats(self):
        """Сброс статистики"""
        self.entity_stats_tracking = {
            'damage_dealt': 0.0,
            'damage_taken': 0.0,
            'healing_received': 0.0,
            'critical_hits': 0,
            'dodges': 0,
            'blocks': 0,
            'toughness_damage_dealt': 0.0,
            'toughness_breaks_caused': 0,
            'toughness_damage_taken': 0.0,
            'toughness_breaks_suffered': 0,
            'total_stun_time': 0.0,
            'creation_time': self.entity_stats_tracking['creation_time'],
            'last_update_time': time.time()
        }
