#!/usr/bin/env python3
"""
Система эффектов - управление игровыми эффектами и их применением
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.interfaces import ISystem, SystemPriority, SystemState
from ...core.constants import (
    EffectCategory, TriggerType, DamageType, StatType,
    BASE_STATS, PROBABILITY_CONSTANTS, TIME_CONSTANTS, SYSTEM_LIMITS
)

logger = logging.getLogger(__name__)

@dataclass
class Effect:
    """Игровой эффект"""
    effect_id: str
    name: str
    description: str
    category: EffectCategory
    trigger_type: TriggerType
    duration: float
    magnitude: float
    target_stats: List[StatType]
    damage_type: Optional[DamageType] = None
    special_effects: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    stackable: bool = False
    max_stacks: int = 1
    icon: str = ""
    sound: str = ""

@dataclass
class SpecialEffect:
    """Специальный эффект"""
    effect_id: str
    name: str
    effect_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    chance: float = 1.0

@dataclass
class ActiveEffect:
    """Активный эффект на сущности"""
    effect_id: str
    entity_id: str
    start_time: float
    end_time: float
    stacks: int = 1
    applied_by: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)

class EffectSystem(ISystem):
    """Система управления эффектами"""
    
    def __init__(self):
        self._system_name = "effects"
        self._system_priority = SystemPriority.HIGH
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Зарегистрированные эффекты
        self.registered_effects: Dict[str, Effect] = {}
        
        # Специальные эффекты
        self.special_effects: Dict[str, SpecialEffect] = {}
        
        # Активные эффекты на сущностях
        self.active_effects: Dict[str, List[ActiveEffect]] = {}
        
        # История применения эффектов
        self.effect_history: List[Dict[str, Any]] = []
        
        # Настройки системы
        self.system_settings = {
            'max_effects_per_entity': SYSTEM_LIMITS["max_effects_per_entity"],
            'max_special_effects': 100,
            'effect_cleanup_interval': TIME_CONSTANTS["effect_cleanup_interval"],
            'stacking_enabled': True,
            'effect_combining_enabled': True
        }
        
        # Статистика системы
        self.system_stats = {
            'registered_effects_count': 0,
            'special_effects_count': 0,
            'total_active_effects': 0,
            'effects_applied_today': 0,
            'effects_removed_today': 0,
            'update_time': 0.0
        }
        
        logger.info("Система эффектов инициализирована")
    
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
        """Инициализация системы эффектов"""
        try:
            logger.info("Инициализация системы эффектов...")
            
            # Регистрируем базовые эффекты
            self._register_base_effects()
            
            # Регистрируем специальные эффекты
            self._register_special_effects()
            
            self._system_state = SystemState.READY
            logger.info("Система эффектов успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы эффектов: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы эффектов"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем активные эффекты
            self._update_active_effects(delta_time)
            
            # Очищаем истекшие эффекты
            self._cleanup_expired_effects()
            
            # Обновляем статистику системы
            self._update_system_stats()
            
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы эффектов: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы эффектов"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система эффектов приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы эффектов: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы эффектов"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система эффектов возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы эффектов: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы эффектов"""
        try:
            logger.info("Очистка системы эффектов...")
            
            # Очищаем все данные
            self.registered_effects.clear()
            self.special_effects.clear()
            self.active_effects.clear()
            self.effect_history.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'registered_effects_count': 0,
                'special_effects_count': 0,
                'total_active_effects': 0,
                'effects_applied_today': 0,
                'effects_removed_today': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система эффектов очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы эффектов: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'registered_effects': len(self.registered_effects),
            'special_effects': len(self.special_effects),
            'entities_with_effects': len(self.active_effects),
            'total_active_effects': self.system_stats['total_active_effects'],
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "effect_applied":
                return self._handle_effect_applied(event_data)
            elif event_type == "effect_removed":
                return self._handle_effect_removed(event_data)
            elif event_type == "entity_died":
                return self._handle_entity_died(event_data)
            elif event_type == "combat_started":
                return self._handle_combat_started(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def _register_base_effects(self) -> None:
        """Регистрация базовых эффектов"""
        try:
            # Эффекты здоровья
            health_effects = [
                Effect(
                    effect_id="heal_small",
                    name="Малое исцеление",
                    description="Восстанавливает небольшое количество здоровья",
                    category=EffectCategory.HEALING,
                    trigger_type=TriggerType.INSTANT,
                    duration=0.0,
                    magnitude=20.0,
                    target_stats=[StatType.HEALTH],
                    icon="heal_small"
                ),
                Effect(
                    effect_id="heal_large",
                    name="Большое исцеление",
                    description="Восстанавливает большое количество здоровья",
                    category=EffectCategory.HEALING,
                    trigger_type=TriggerType.INSTANT,
                    duration=0.0,
                    magnitude=50.0,
                    target_stats=[StatType.HEALTH],
                    icon="heal_large"
                ),
                Effect(
                    effect_id="regeneration",
                    name="Регенерация",
                    description="Постепенно восстанавливает здоровье",
                    category=EffectCategory.HEALING,
                    trigger_type=TriggerType.PERIODIC,
                    duration=30.0,
                    magnitude=5.0,
                    target_stats=[StatType.HEALTH],
                    icon="regeneration"
                )
            ]
            
            # Эффекты урона
            damage_effects = [
                Effect(
                    effect_id="burn",
                    name="Ожог",
                    description="Наносит периодический огненный урон",
                    category=EffectCategory.DAMAGE,
                    trigger_type=TriggerType.PERIODIC,
                    duration=15.0,
                    magnitude=10.0,
                    target_stats=[StatType.HEALTH],
                    damage_type=DamageType.FIRE,
                    icon="burn"
                ),
                Effect(
                    effect_id="poison",
                    name="Яд",
                    description="Наносит периодический ядовитый урон",
                    category=EffectCategory.DAMAGE,
                    trigger_type=TriggerType.PERIODIC,
                    duration=20.0,
                    magnitude=8.0,
                    target_stats=[StatType.HEALTH],
                    damage_type=DamageType.POISON,
                    icon="poison"
                ),
                Effect(
                    effect_id="bleeding",
                    name="Кровотечение",
                    description="Наносит периодический физический урон",
                    category=EffectCategory.DAMAGE,
                    trigger_type=TriggerType.PERIODIC,
                    duration=25.0,
                    magnitude=12.0,
                    target_stats=[StatType.HEALTH],
                    damage_type=DamageType.PHYSICAL,
                    icon="bleeding"
                )
            ]
            
            # Эффекты усиления
            buff_effects = [
                Effect(
                    effect_id="strength_boost",
                    name="Усиление силы",
                    description="Увеличивает атаку",
                    category=EffectCategory.BUFF,
                    trigger_type=TriggerType.DURATION,
                    duration=60.0,
                    magnitude=15.0,
                    target_stats=[StatType.ATTACK],
                    icon="strength_boost"
                ),
                Effect(
                    effect_id="speed_boost",
                    name="Ускорение",
                    description="Увеличивает скорость",
                    category=EffectCategory.BUFF,
                    trigger_type=TriggerType.DURATION,
                    duration=45.0,
                    magnitude=0.5,
                    target_stats=[StatType.SPEED],
                    icon="speed_boost"
                ),
                Effect(
                    effect_id="defense_boost",
                    name="Усиление защиты",
                    description="Увеличивает защиту",
                    category=EffectCategory.BUFF,
                    trigger_type=TriggerType.DURATION,
                    duration=90.0,
                    magnitude=20.0,
                    target_stats=[StatType.DEFENSE],
                    icon="defense_boost"
                )
            ]
            
            # Эффекты ослабления
            debuff_effects = [
                Effect(
                    effect_id="weakness",
                    name="Слабость",
                    description="Уменьшает атаку",
                    category=EffectCategory.DEBUFF,
                    trigger_type=TriggerType.DURATION,
                    duration=40.0,
                    magnitude=-10.0,
                    target_stats=[StatType.ATTACK],
                    icon="weakness"
                ),
                Effect(
                    effect_id="slow",
                    name="Замедление",
                    description="Уменьшает скорость",
                    category=EffectCategory.DEBUFF,
                    trigger_type=TriggerType.DURATION,
                    duration=35.0,
                    magnitude=-0.3,
                    target_stats=[StatType.SPEED],
                    icon="slow"
                ),
                Effect(
                    effect_id="vulnerability",
                    name="Уязвимость",
                    description="Уменьшает защиту",
                    category=EffectCategory.DEBUFF,
                    trigger_type=TriggerType.DURATION,
                    duration=50.0,
                    magnitude=-15.0,
                    target_stats=[StatType.DEFENSE],
                    icon="vulnerability"
                )
            ]
            
            # Регистрируем все эффекты
            all_effects = health_effects + damage_effects + buff_effects + debuff_effects
            
            for effect in all_effects:
                self.registered_effects[effect.effect_id] = effect
            
            logger.info(f"Зарегистрировано {len(all_effects)} базовых эффектов")
            
        except Exception as e:
            logger.error(f"Ошибка регистрации базовых эффектов: {e}")
    
    def _register_special_effects(self) -> None:
        """Регистрация специальных эффектов"""
        try:
            special_effects = [
                SpecialEffect(
                    effect_id="stun",
                    name="Оглушение",
                    effect_type="stun",
                    parameters={'duration': 3.0},
                    duration=3.0,
                    chance=0.15
                ),
                SpecialEffect(
                    effect_id="silence",
                    name="Тишина",
                    effect_type="silence",
                    parameters={'duration': 5.0},
                    duration=5.0,
                    chance=0.10
                ),
                SpecialEffect(
                    effect_id="fear",
                    name="Страх",
                    effect_type="fear",
                    parameters={'duration': 8.0, 'movement_speed': -0.5},
                    duration=8.0,
                    chance=0.08
                ),
                SpecialEffect(
                    effect_id="charm",
                    name="Очарование",
                    effect_type="charm",
                    parameters={'duration': 6.0, 'control_duration': 4.0},
                    duration=6.0,
                    chance=0.05
                )
            ]
            
            for effect in special_effects:
                self.special_effects[effect.effect_id] = effect
            
            logger.info(f"Зарегистрировано {len(special_effects)} специальных эффектов")
            
        except Exception as e:
            logger.error(f"Ошибка регистрации специальных эффектов: {e}")
    
    def _update_active_effects(self, delta_time: float) -> None:
        """Обновление активных эффектов"""
        try:
            current_time = time.time()
            
            for entity_id, effects in self.active_effects.items():
                for effect in effects:
                    if effect.end_time <= current_time:
                        # Эффект истек
                        self._remove_effect_from_entity(entity_id, effect.effect_id)
                        continue
                    
                    # Обрабатываем периодические эффекты
                    if effect.effect_id in self.registered_effects:
                        registered_effect = self.registered_effects[effect.effect_id]
                        
                        if registered_effect.trigger_type == TriggerType.PERIODIC:
                            # Проверяем, нужно ли применить эффект
                            interval = 1.0  # Каждую секунду
                            if (current_time - effect.start_time) % interval < delta_time:
                                self._apply_periodic_effect(entity_id, effect, registered_effect)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления активных эффектов: {e}")
    
    def _cleanup_expired_effects(self) -> None:
        """Очистка истекших эффектов"""
        try:
            current_time = time.time()
            
            for entity_id in list(self.active_effects.keys()):
                if entity_id not in self.active_effects:
                    continue
                
                # Удаляем истекшие эффекты
                valid_effects = [
                    effect for effect in self.active_effects[entity_id]
                    if effect.end_time > current_time
                ]
                
                if len(valid_effects) != len(self.active_effects[entity_id]):
                    removed_count = len(self.active_effects[entity_id]) - len(valid_effects)
                    self.active_effects[entity_id] = valid_effects
                    self.system_stats['effects_removed_today'] += removed_count
                
                # Удаляем пустые записи
                if not self.active_effects[entity_id]:
                    del self.active_effects[entity_id]
                
        except Exception as e:
            logger.warning(f"Ошибка очистки истекших эффектов: {e}")
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            self.system_stats['registered_effects_count'] = len(self.registered_effects)
            self.system_stats['special_effects_count'] = len(self.special_effects)
            self.system_stats['total_active_effects'] = sum(len(effects) for effects in self.active_effects.values())
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_effect_applied(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события применения эффекта"""
        try:
            effect_id = event_data.get('effect_id')
            entity_id = event_data.get('entity_id')
            applied_by = event_data.get('applied_by')
            duration = event_data.get('duration', 0.0)
            
            if effect_id and entity_id:
                return self.apply_effect_to_entity(effect_id, entity_id, applied_by, duration)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события применения эффекта: {e}")
            return False
    
    def _handle_effect_removed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события удаления эффекта"""
        try:
            effect_id = event_data.get('effect_id')
            entity_id = event_data.get('entity_id')
            
            if effect_id and entity_id:
                return self.remove_effect_from_entity(entity_id, effect_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события удаления эффекта: {e}")
            return False
    
    def _handle_entity_died(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события смерти сущности"""
        try:
            entity_id = event_data.get('entity_id')
            
            if entity_id:
                # Удаляем все эффекты с мертвой сущности
                if entity_id in self.active_effects:
                    removed_count = len(self.active_effects[entity_id])
                    del self.active_effects[entity_id]
                    self.system_stats['effects_removed_today'] += removed_count
                    logger.debug(f"Удалено {removed_count} эффектов с мертвой сущности {entity_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события смерти сущности: {e}")
            return False
    
    def _handle_combat_started(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события начала боя"""
        try:
            # Некоторые эффекты могут активироваться в бою
            combat_id = event_data.get('combat_id')
            participants = event_data.get('participants')
            
            if combat_id and participants:
                # Проверяем эффекты, которые активируются в бою
                for participant_id in participants:
                    if participant_id in self.active_effects:
                        for effect in self.active_effects[participant_id]:
                            if effect.effect_id in self.registered_effects:
                                registered_effect = self.registered_effects[effect.effect_id]
                                if registered_effect.trigger_type == TriggerType.COMBAT_START:
                                    self._apply_combat_trigger_effect(participant_id, effect, registered_effect)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события начала боя: {e}")
            return False
    
    def apply_effect_to_entity(self, effect_id: str, entity_id: str, applied_by: Optional[str] = None, duration: Optional[float] = None) -> bool:
        """Применение эффекта к сущности"""
        try:
            if effect_id not in self.registered_effects:
                logger.warning(f"Эффект {effect_id} не найден")
                return False
            
            effect = self.registered_effects[effect_id]
            current_time = time.time()
            
            # Проверяем лимит эффектов на сущности
            if entity_id in self.active_effects:
                if len(self.active_effects[entity_id]) >= self.system_settings['max_effects_per_entity']:
                    logger.warning(f"Достигнут лимит эффектов для сущности {entity_id}")
                    return False
            
            # Создаем активный эффект
            active_effect = ActiveEffect(
                effect_id=effect_id,
                entity_id=entity_id,
                start_time=current_time,
                end_time=current_time + (duration or effect.duration),
                stacks=1,
                applied_by=applied_by
            )
            
            # Инициализируем список эффектов для сущности, если нужно
            if entity_id not in self.active_effects:
                self.active_effects[entity_id] = []
            
            # Проверяем, можно ли стакать эффект
            if effect.stackable and self.system_settings['stacking_enabled']:
                existing_effect = self._find_existing_effect(entity_id, effect_id)
                if existing_effect and existing_effect.stacks < effect.max_stacks:
                    # Увеличиваем стаки
                    existing_effect.stacks += 1
                    existing_effect.end_time = active_effect.end_time
                    logger.debug(f"Увеличены стаки эффекта {effect_id} для {entity_id}: {existing_effect.stacks}")
                    return True
            
            # Добавляем новый эффект
            self.active_effects[entity_id].append(active_effect)
            
            # Применяем мгновенный эффект
            if effect.trigger_type == TriggerType.INSTANT:
                self._apply_instant_effect(entity_id, effect)
            
            # Записываем в историю
            self.effect_history.append({
                'timestamp': current_time,
                'action': 'applied',
                'effect_id': effect_id,
                'entity_id': entity_id,
                'applied_by': applied_by,
                'duration': duration or effect.duration
            })
            
            self.system_stats['effects_applied_today'] += 1
            logger.debug(f"Эффект {effect_id} применен к {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка применения эффекта {effect_id} к {entity_id}: {e}")
            return False
    
    def remove_effect_from_entity(self, entity_id: str, effect_id: str) -> bool:
        """Удаление эффекта с сущности"""
        try:
            if entity_id not in self.active_effects:
                return False
            
            effects = self.active_effects[entity_id]
            removed_effects = [e for e in effects if e.effect_id == effect_id]
            
            if not removed_effects:
                return False
            
            # Удаляем эффекты
            for effect in removed_effects:
                effects.remove(effect)
                
                # Применяем эффект удаления, если есть
                if effect.effect_id in self.registered_effects:
                    registered_effect = self.registered_effects[effect.effect_id]
                    self._apply_removal_effect(entity_id, effect, registered_effect)
            
            # Удаляем пустые записи
            if not effects:
                del self.active_effects[entity_id]
            
            # Записываем в историю
            current_time = time.time()
            self.effect_history.append({
                'timestamp': current_time,
                'action': 'removed',
                'effect_id': effect_id,
                'entity_id': entity_id
            })
            
            self.system_stats['effects_removed_today'] += 1
            logger.debug(f"Эффект {effect_id} удален с {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления эффекта {effect_id} с {entity_id}: {e}")
            return False
    
    def _find_existing_effect(self, entity_id: str, effect_id: str) -> Optional[ActiveEffect]:
        """Поиск существующего эффекта"""
        try:
            if entity_id not in self.active_effects:
                return None
            
            for effect in self.active_effects[entity_id]:
                if effect.effect_id == effect_id:
                    return effect
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка поиска существующего эффекта: {e}")
            return None
    
    def _apply_instant_effect(self, entity_id: str, effect: Effect) -> None:
        """Применение мгновенного эффекта"""
        try:
            # Здесь должна быть интеграция с системой характеристик
            # Пока просто логируем
            logger.debug(f"Применен мгновенный эффект {effect.effect_id} к {entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка применения мгновенного эффекта {effect.effect_id}: {e}")
    
    def _apply_periodic_effect(self, entity_id: str, active_effect: ActiveEffect, effect: Effect) -> None:
        """Применение периодического эффекта"""
        try:
            # Здесь должна быть интеграция с системой характеристик
            # Пока просто логируем
            logger.debug(f"Применен периодический эффект {effect.effect_id} к {entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка применения периодического эффекта {effect.effect_id}: {e}")
    
    def _apply_combat_trigger_effect(self, entity_id: str, active_effect: ActiveEffect, effect: Effect) -> None:
        """Применение эффекта, активируемого началом боя"""
        try:
            # Здесь должна быть интеграция с системой характеристик
            # Пока просто логируем
            logger.debug(f"Активирован боевой эффект {effect.effect_id} для {entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка активации боевого эффекта {effect.effect_id}: {e}")
    
    def _apply_removal_effect(self, entity_id: str, active_effect: ActiveEffect, effect: Effect) -> None:
        """Применение эффекта при удалении"""
        try:
            # Здесь должна быть интеграция с системой характеристик
            # Пока просто логируем
            logger.debug(f"Применен эффект удаления {effect.effect_id} для {entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка применения эффекта удаления {effect.effect_id}: {e}")
    
    def get_entity_effects(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение эффектов сущности"""
        try:
            if entity_id not in self.active_effects:
                return []
            
            effects_info = []
            current_time = time.time()
            
            for effect in self.active_effects[entity_id]:
                if effect.effect_id in self.registered_effects:
                    registered_effect = self.registered_effects[effect.effect_id]
                    
                    effects_info.append({
                        'effect_id': effect.effect_id,
                        'name': registered_effect.name,
                        'description': registered_effect.description,
                        'category': registered_effect.category.value,
                        'trigger_type': registered_effect.trigger_type.value,
                        'duration': registered_effect.duration,
                        'magnitude': registered_effect.magnitude,
                        'damage_type': registered_effect.damage_type.value if registered_effect.damage_type else None,
                        'stacks': effect.stacks,
                        'time_remaining': max(0, effect.end_time - current_time),
                        'applied_by': effect.applied_by,
                        'icon': registered_effect.icon
                    })
            
            return effects_info
            
        except Exception as e:
            logger.error(f"Ошибка получения эффектов сущности {entity_id}: {e}")
            return []
    
    def get_effect_info(self, effect_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации об эффекте"""
        try:
            if effect_id not in self.registered_effects:
                return None
            
            effect = self.registered_effects[effect_id]
            
            return {
                'effect_id': effect.effect_id,
                'name': effect.name,
                'description': effect.description,
                'category': effect.category.value,
                'trigger_type': effect.trigger_type.value,
                'duration': effect.duration,
                'magnitude': effect.magnitude,
                'target_stats': [stat.value for stat in effect.target_stats],
                'damage_type': effect.damage_type.value if effect.damage_type else None,
                'special_effects': effect.special_effects,
                'stackable': effect.stackable,
                'max_stacks': effect.max_stacks,
                'icon': effect.icon,
                'sound': effect.sound
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации об эффекте {effect_id}: {e}")
            return None

    # --- Расширение API для интеграции со сценой ---
    def trigger_effect(self, trigger_type: str, source_entity: Any, target_entity: Any = None, context: Dict[str, Any] = None) -> bool:
        """Примитивная обработка триггера эффекта. Заглушка для интеграции со сценой."""
        try:
            current_time = time.time()
            self.effect_history.append({
                'timestamp': current_time,
                'action': 'trigger',
                'trigger_type': trigger_type,
                'source': getattr(source_entity, 'id', getattr(source_entity, 'name', 'unknown')) if source_entity is not None else None,
                'target': getattr(target_entity, 'id', getattr(target_entity, 'name', None)) if target_entity is not None else None,
                'context': context or {}
            })
            return True
        except Exception as e:
            logger.error(f"Ошибка обработки триггера эффекта {trigger_type}: {e}")
            return False

    def register_item_effects(self, item: Any) -> bool:
        """Регистрация эффектов, приходящих из предмета. Заглушка для совместимости со сценой."""
        try:
            effects = None
            if hasattr(item, 'effects'):
                effects = getattr(item, 'effects')
            elif isinstance(item, dict):
                effects = item.get('effects')
            if not effects:
                return True
            for eff in effects:
                if isinstance(eff, Effect) and eff.effect_id not in self.registered_effects:
                    self.registered_effects[eff.effect_id] = eff
            return True
        except Exception as e:
            logger.warning(f"Не удалось зарегистрировать эффекты предмета: {e}")
            return False
    
    def register_custom_effect(self, effect: Effect) -> bool:
        """Регистрация пользовательского эффекта"""
        try:
            if effect.effect_id in self.registered_effects:
                logger.warning(f"Эффект {effect.effect_id} уже зарегистрирован")
                return False
            
            self.registered_effects[effect.effect_id] = effect
            logger.info(f"Зарегистрирован пользовательский эффект {effect.effect_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации пользовательского эффекта {effect.effect_id}: {e}")
            return False
    
    def register_custom_special_effect(self, effect: SpecialEffect) -> bool:
        """Регистрация пользовательского специального эффекта"""
        try:
            if effect.effect_id in self.special_effects:
                logger.warning(f"Специальный эффект {effect.effect_id} уже зарегистрирован")
                return False
            
            if len(self.special_effects) >= self.system_settings['max_special_effects']:
                logger.warning("Достигнут лимит специальных эффектов")
                return False
            
            self.special_effects[effect.effect_id] = effect
            logger.info(f"Зарегистрирован пользовательский специальный эффект {effect.effect_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации пользовательского специального эффекта {effect.effect_id}: {e}")
            return False
    
    def get_effects_by_category(self, category: EffectCategory) -> List[Dict[str, Any]]:
        """Получение эффектов по категории"""
        try:
            effects = []
            
            for effect in self.registered_effects.values():
                if effect.category == category:
                    effects.append({
                        'effect_id': effect.effect_id,
                        'name': effect.name,
                        'description': effect.description,
                        'magnitude': effect.magnitude,
                        'duration': effect.duration,
                        'icon': effect.icon
                    })
            
            return effects
            
        except Exception as e:
            logger.error(f"Ошибка получения эффектов по категории {category.value}: {e}")
            return []
    
    def get_effects_by_trigger(self, trigger_type: TriggerType) -> List[Dict[str, Any]]:
        """Получение эффектов по типу триггера"""
        try:
            effects = []
            
            for effect in self.registered_effects.values():
                if effect.trigger_type == trigger_type:
                    effects.append({
                        'effect_id': effect.effect_id,
                        'name': effect.name,
                        'description': effect.description,
                        'magnitude': effect.magnitude,
                        'duration': effect.duration,
                        'icon': effect.icon
                    })
            
            return effects
            
        except Exception as e:
            logger.error(f"Ошибка получения эффектов по типу триггера {trigger_type.value}: {e}")
            return []
