"""
Система здоровья - управление здоровьем, маной, энергией и состоянием сущностей
"""

import time
import random
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from src.core.architecture import BaseComponent, ComponentType, Priority


class HealthState(Enum):
    """Состояния здоровья"""
    ALIVE = "alive"            # Жив
    WOUNDED = "wounded"        # Ранен
    CRITICAL = "critical"      # Критическое состояние
    UNCONSCIOUS = "unconscious"  # Без сознания
    DEAD = "dead"              # Мертв


class ResourceType(Enum):
    """Типы ресурсов"""
    HEALTH = "health"          # Здоровье
    MANA = "mana"              # Мана
    ENERGY = "energy"          # Энергия
    STAMINA = "stamina"        # Выносливость
    ENDURANCE = "endurance"    # Стойкость
    SHIELD = "shield"          # Щит


@dataclass
class ResourcePool:
    """Пул ресурсов"""
    current: float = 0.0
    maximum: float = 100.0
    regeneration_rate: float = 1.0  # в секунду
    regeneration_delay: float = 5.0  # задержка после получения урона
    last_damage_time: float = 0.0
    
    def get_percentage(self) -> float:
        """Получить процент заполнения"""
        if self.maximum <= 0:
            return 0.0
        return (self.current / self.maximum) * 100.0
    
    def is_full(self) -> bool:
        """Проверить, полон ли пул"""
        return self.current >= self.maximum
    
    def is_empty(self) -> bool:
        """Проверить, пуст ли пул"""
        return self.current <= 0
    
    def can_regenerate(self) -> bool:
        """Проверить, может ли ресурс восстанавливаться"""
        return time.time() - self.last_damage_time >= self.regeneration_delay


@dataclass
class HealthStatus:
    """Статус здоровья сущности"""
    entity_id: str
    health: ResourcePool = field(default_factory=lambda: ResourcePool(100.0, 100.0))
    mana: ResourcePool = field(default_factory=lambda: ResourcePool(50.0, 50.0, 2.0))
    energy: ResourcePool = field(default_factory=lambda: ResourcePool(100.0, 100.0, 5.0))
    stamina: ResourcePool = field(default_factory=lambda: ResourcePool(100.0, 100.0, 3.0))
    shield: ResourcePool = field(default_factory=lambda: ResourcePool(0.0, 50.0, 0.0))
    
    # Состояние
    state: HealthState = HealthState.ALIVE
    is_poisoned: bool = False
    is_burning: bool = False
    is_frozen: bool = False
    is_stunned: bool = False
    
    # Временные эффекты
    temporary_effects: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # История изменений
    health_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_total_health_percentage(self) -> float:
        """Получить общий процент здоровья"""
        total_current = self.health.current + self.shield.current
        total_maximum = self.health.maximum + self.shield.maximum
        if total_maximum <= 0:
            return 0.0
        return (total_current / total_maximum) * 100.0
    
    def is_alive(self) -> bool:
        """Проверить, жива ли сущность"""
        return self.state != HealthState.DEAD
    
    def can_act(self) -> bool:
        """Проверить, может ли сущность действовать"""
        return (self.state != HealthState.DEAD and 
                self.state != HealthState.UNCONSCIOUS and 
                not self.is_stunned)


class HealthSystem(BaseComponent):
    """
    Система здоровья
    Управляет здоровьем, маной, энергией и состоянием всех сущностей
    """
    
    def __init__(self):
        super().__init__(
            name="HealthSystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Статусы здоровья сущностей
        self.health_statuses: Dict[str, HealthStatus] = {}
        
        # Обработчики событий
        self.damage_handlers: Dict[str, Callable] = {}
        self.healing_handlers: Dict[str, Callable] = {}
        self.death_handlers: Dict[str, Callable] = {}
        
        # Система регенерации
        self.regeneration_timers: Dict[str, float] = {}
        
        # Настройки
        self.max_health_history = 100
        self.regeneration_interval = 1.0  # секунды
        
    def _on_initialize(self) -> bool:
        """Инициализация системы здоровья"""
        try:
            # Регистрация обработчиков событий
            self._register_event_handlers()
            
            # Настройка системы регенерации
            self._setup_regeneration_system()
            
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации HealthSystem: {e}")
            return False
    
    def _register_event_handlers(self):
        """Регистрация обработчиков событий"""
        # Обработчики урона
        self.damage_handlers["physical"] = self._handle_physical_damage
        self.damage_handlers["magical"] = self._handle_magical_damage
        self.damage_handlers["poison"] = self._handle_poison_damage
        self.damage_handlers["burn"] = self._handle_burn_damage
        
        # Обработчики лечения
        self.healing_handlers["direct"] = self._handle_direct_healing
        self.healing_handlers["over_time"] = self._handle_over_time_healing
        self.healing_handlers["percentage"] = self._handle_percentage_healing
        
        # Обработчики смерти
        self.death_handlers["default"] = self._handle_death
    
    def _setup_regeneration_system(self):
        """Настройка системы регенерации"""
        self.regeneration_interval = 1.0
    
    # Управление сущностями
    def register_entity(self, entity_id: str, health: float = 100.0, mana: float = 50.0, 
                       energy: float = 100.0, stamina: float = 100.0) -> HealthStatus:
        """Зарегистрировать сущность в системе здоровья"""
        if entity_id in self.health_statuses:
            return self.health_statuses[entity_id]
        
        status = HealthStatus(
            entity_id=entity_id,
            health=ResourcePool(health, health),
            mana=ResourcePool(mana, mana, 2.0),
            energy=ResourcePool(energy, energy, 5.0),
            stamina=ResourcePool(stamina, stamina, 3.0)
        )
        
        self.health_statuses[entity_id] = status
        self.regeneration_timers[entity_id] = time.time()
        
        return status
    
    def unregister_entity(self, entity_id: str) -> bool:
        """Отменить регистрацию сущности"""
        if entity_id not in self.health_statuses:
            return False
        
        del self.health_statuses[entity_id]
        if entity_id in self.regeneration_timers:
            del self.regeneration_timers[entity_id]
        
        return True
    
    def get_health_status(self, entity_id: str) -> Optional[HealthStatus]:
        """Получить статус здоровья сущности"""
        return self.health_statuses.get(entity_id)
    
    # Управление здоровьем
    def take_damage(self, entity_id: str, damage: float, damage_type: str = "physical", 
                   source_id: Optional[str] = None) -> bool:
        """Получить урон"""
        status = self.get_health_status(entity_id)
        if not status or not status.is_alive():
            return False
        
        # Обрабатываем урон по типу
        if damage_type in self.damage_handlers:
            handler = self.damage_handlers[damage_type]
            final_damage = handler(damage, status, source_id)
        else:
            final_damage = damage
        
        # Применяем урон
        if final_damage > 0:
            self._apply_damage(status, final_damage, damage_type, source_id)
        
        return True
    
    def heal(self, entity_id: str, amount: float, healing_type: str = "direct", 
             source_id: Optional[str] = None) -> bool:
        """Вылечить сущность"""
        status = self.get_health_status(entity_id)
        if not status or not status.is_alive():
            return False
        
        # Обрабатываем лечение по типу
        if healing_type in self.healing_handlers:
            handler = self.healing_handlers[healing_type]
            final_healing = handler(amount, status, source_id)
        else:
            final_healing = amount
        
        # Применяем лечение
        if final_healing > 0:
            self._apply_healing(status, final_healing, healing_type, source_id)
        
        return True
    
    def restore_resource(self, entity_id: str, resource_type: ResourceType, amount: float) -> bool:
        """Восстановить ресурс"""
        status = self.get_health_status(entity_id)
        if not status:
            return False
        
        # Определяем пул ресурса
        if resource_type == ResourceType.HEALTH:
            pool = status.health
        elif resource_type == ResourceType.MANA:
            pool = status.mana
        elif resource_type == ResourceType.ENERGY:
            pool = status.energy
        elif resource_type == ResourceType.STAMINA:
            pool = status.stamina
        elif resource_type == ResourceType.SHIELD:
            pool = status.shield
        else:
            return False
        
        # Восстанавливаем ресурс
        old_value = pool.current
        pool.current = min(pool.maximum, pool.current + amount)
        restored_amount = pool.current - old_value
        
        # Записываем в историю
        if restored_amount > 0:
            self._add_to_history(status, "restore", {
                "resource_type": resource_type.value,
                "amount": restored_amount,
                "old_value": old_value,
                "new_value": pool.current
            })
        
        return restored_amount > 0
    
    def consume_resource(self, entity_id: str, resource_type: ResourceType, amount: float) -> bool:
        """Потратить ресурс"""
        status = self.get_health_status(entity_id)
        if not status:
            return False
        
        # Определяем пул ресурса
        if resource_type == ResourceType.HEALTH:
            pool = status.health
        elif resource_type == ResourceType.MANA:
            pool = status.mana
        elif resource_type == ResourceType.ENERGY:
            pool = status.energy
        elif resource_type == ResourceType.STAMINA:
            pool = status.stamina
        elif resource_type == ResourceType.SHIELD:
            pool = status.shield
        else:
            return False
        
        # Проверяем, достаточно ли ресурса
        if pool.current < amount:
            return False
        
        # Тратим ресурс
        old_value = pool.current
        pool.current = max(0, pool.current - amount)
        consumed_amount = old_value - pool.current
        
        # Записываем в историю
        self._add_to_history(status, "consume", {
            "resource_type": resource_type.value,
            "amount": consumed_amount,
            "old_value": old_value,
            "new_value": pool.current
        })
        
        return True
    
    # Обработчики урона
    def _handle_physical_damage(self, damage: float, status: HealthStatus, source_id: Optional[str]) -> float:
        """Обработка физического урона"""
        # Урон сначала идет на щит
        if status.shield.current > 0:
            shield_damage = min(damage, status.shield.current)
            status.shield.current -= shield_damage
            damage -= shield_damage
        
        return max(0, damage)
    
    def _handle_magical_damage(self, damage: float, status: HealthStatus, source_id: Optional[str]) -> float:
        """Обработка магического урона"""
        # Магический урон игнорирует щит
        return damage
    
    def _handle_poison_damage(self, damage: float, status: HealthStatus, source_id: Optional[str]) -> float:
        """Обработка ядовитого урона"""
        status.is_poisoned = True
        return damage * 0.5  # Яд наносит меньше урона, но длительно
    
    def _handle_burn_damage(self, damage: float, status: HealthStatus, source_id: Optional[str]) -> float:
        """Обработка огненного урона"""
        status.is_burning = True
        return damage * 1.2  # Огонь наносит больше урона
    
    # Обработчики лечения
    def _handle_direct_healing(self, amount: float, status: HealthStatus, source_id: Optional[str]) -> float:
        """Обработка прямого лечения"""
        return amount
    
    def _handle_over_time_healing(self, amount: float, status: HealthStatus, source_id: Optional[str]) -> float:
        """Обработка лечения по времени"""
        return amount * 0.8  # Лечение по времени менее эффективно
    
    def _handle_percentage_healing(self, percentage: float, status: HealthStatus, source_id: Optional[str]) -> float:
        """Обработка процентного лечения"""
        return (status.health.maximum * percentage) / 100.0
    
    # Применение изменений
    def _apply_damage(self, status: HealthStatus, damage: float, damage_type: str, source_id: Optional[str]):
        """Применить урон"""
        old_health = status.health.current
        status.health.current = max(0, status.health.current - damage)
        status.health.last_damage_time = time.time()
        
        # Обновляем состояние
        self._update_health_state(status)
        
        # Записываем в историю
        self._add_to_history(status, "damage", {
            "damage_type": damage_type,
            "amount": damage,
            "old_health": old_health,
            "new_health": status.health.current,
            "source_id": source_id
        })
        
        # Проверяем смерть
        if status.health.current <= 0:
            self._handle_death(status, source_id)
    
    def _apply_healing(self, status: HealthStatus, amount: float, healing_type: str, source_id: Optional[str]):
        """Применить лечение"""
        old_health = status.health.current
        status.health.current = min(status.health.maximum, status.health.current + amount)
        
        # Обновляем состояние
        self._update_health_state(status)
        
        # Записываем в историю
        self._add_to_history(status, "healing", {
            "healing_type": healing_type,
            "amount": amount,
            "old_health": old_health,
            "new_health": status.health.current,
            "source_id": source_id
        })
    
    def _update_health_state(self, status: HealthStatus):
        """Обновить состояние здоровья"""
        health_percentage = status.health.get_percentage()
        
        if health_percentage <= 0:
            status.state = HealthState.DEAD
        elif health_percentage <= 10:
            status.state = HealthState.CRITICAL
        elif health_percentage <= 25:
            status.state = HealthState.WOUNDED
        else:
            status.state = HealthState.ALIVE
    
    def _handle_death(self, status: HealthStatus, source_id: Optional[str]):
        """Обработка смерти"""
        status.state = HealthState.DEAD
        
        # Вызываем обработчики смерти
        for handler in self.death_handlers.values():
            try:
                handler(status, source_id)
            except Exception as e:
                self.logger.error(f"Ошибка в обработчике смерти: {e}")
        
        # Записываем в историю
        self._add_to_history(status, "death", {
            "source_id": source_id,
            "timestamp": time.time()
        })
    
    # Система регенерации
    def update_regeneration(self, delta_time: float):
        """Обновить регенерацию ресурсов"""
        current_time = time.time()
        
        for entity_id, status in self.health_statuses.items():
            if not status.is_alive():
                continue
            
            # Проверяем, нужно ли обновлять регенерацию
            if current_time - self.regeneration_timers.get(entity_id, 0) < self.regeneration_interval:
                continue
            
            # Обновляем регенерацию
            self._regenerate_resources(status, delta_time)
            self.regeneration_timers[entity_id] = current_time
    
    def _regenerate_resources(self, status: HealthStatus, delta_time: float):
        """Регенерировать ресурсы"""
        # Регенерация здоровья
        if status.health.can_regenerate() and not status.health.is_full():
            old_health = status.health.current
            status.health.current = min(
                status.health.maximum,
                status.health.current + status.health.regeneration_rate * delta_time
            )
            if status.health.current > old_health:
                self._update_health_state(status)
        
        # Регенерация маны
        if status.mana.can_regenerate() and not status.mana.is_full():
            status.mana.current = min(
                status.mana.maximum,
                status.mana.current + status.mana.regeneration_rate * delta_time
            )
        
        # Регенерация энергии
        if status.energy.can_regenerate() and not status.energy.is_full():
            status.energy.current = min(
                status.energy.maximum,
                status.energy.current + status.energy.regeneration_rate * delta_time
            )
        
        # Регенерация выносливости
        if status.stamina.can_regenerate() and not status.stamina.is_full():
            status.stamina.current = min(
                status.stamina.maximum,
                status.stamina.current + status.stamina.regeneration_rate * delta_time
            )
        
        # Регенерация щита
        if status.shield.can_regenerate() and not status.shield.is_full():
            status.shield.current = min(
                status.shield.maximum,
                status.shield.current + status.shield.regeneration_rate * delta_time
            )
    
    # История и статистика
    def _add_to_history(self, status: HealthStatus, event_type: str, data: Dict[str, Any]):
        """Добавить событие в историю"""
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data
        }
        
        status.health_history.append(event)
        
        # Ограничиваем размер истории
        if len(status.health_history) > self.max_health_history:
            status.health_history.pop(0)
    
    def get_health_history(self, entity_id: str, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получить историю здоровья"""
        status = self.get_health_status(entity_id)
        if not status:
            return []
        
        if event_type:
            return [e for e in status.health_history if e["event_type"] == event_type]
        
        return status.health_history.copy()
    
    def get_health_statistics(self, entity_id: str) -> Dict[str, Any]:
        """Получить статистику здоровья"""
        status = self.get_health_status(entity_id)
        if not status:
            return {}
        
        return {
            "health_percentage": status.health.get_percentage(),
            "mana_percentage": status.mana.get_percentage(),
            "energy_percentage": status.energy.get_percentage(),
            "stamina_percentage": status.stamina.get_percentage(),
            "shield_percentage": status.shield.get_percentage(),
            "total_health_percentage": status.get_total_health_percentage(),
            "state": status.state.value,
            "is_alive": status.is_alive(),
            "can_act": status.can_act(),
            "is_poisoned": status.is_poisoned,
            "is_burning": status.is_burning,
            "is_frozen": status.is_frozen,
            "is_stunned": status.is_stunned
        }
    
    # Публичные методы
    def set_max_health(self, entity_id: str, max_health: float) -> bool:
        """Установить максимальное здоровье"""
        status = self.get_health_status(entity_id)
        if not status:
            return False
        
        old_max = status.health.maximum
        status.health.maximum = max_health
        
        # Пропорционально изменяем текущее здоровье
        if old_max > 0:
            ratio = status.health.current / old_max
            status.health.current = max_health * ratio
        
        return True
    
    def set_max_mana(self, entity_id: str, max_mana: float) -> bool:
        """Установить максимальную ману"""
        status = self.get_health_status(entity_id)
        if not status:
            return False
        
        old_max = status.mana.maximum
        status.mana.maximum = max_mana
        
        # Пропорционально изменяем текущую ману
        if old_max > 0:
            ratio = status.mana.current / old_max
            status.mana.current = max_mana * ratio
        
        return True
    
    def add_temporary_effect(self, entity_id: str, effect_id: str, effect_data: Dict[str, Any]):
        """Добавить временный эффект"""
        status = self.get_health_status(entity_id)
        if not status:
            return
        
        status.temporary_effects[effect_id] = {
            "data": effect_data,
            "start_time": time.time()
        }
    
    def remove_temporary_effect(self, entity_id: str, effect_id: str):
        """Убрать временный эффект"""
        status = self.get_health_status(entity_id)
        if not status:
            return
        
        if effect_id in status.temporary_effects:
            del status.temporary_effects[effect_id]
    
    def clear_all_effects(self, entity_id: str):
        """Очистить все временные эффекты"""
        status = self.get_health_status(entity_id)
        if not status:
            return
        
        status.temporary_effects.clear()
        status.is_poisoned = False
        status.is_burning = False
        status.is_frozen = False
        status.is_stunned = False
