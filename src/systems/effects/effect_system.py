#!/usr/bin/env python3
"""
Система эффектов - управление игровыми эффектами и их применением
Интегрирована с новой модульной архитектурой
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.system_interfaces import BaseGameSystem
from ...core.architecture import Priority, LifecycleState
from ...core.state_manager import StateManager, StateType, StateScope
from ...core.repository import RepositoryManager, DataType, StorageType
from ...core.constants import (
    EffectCategory, TriggerType, DamageType, StatType,
    BASE_STATS, PROBABILITY_CONSTANTS, SYSTEM_LIMITS,
    TIME_CONSTANTS_RO, get_float, normalize_trigger, normalize_ui_event
)
from ...core.entity_registry import get_entity

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

class EffectSystem(BaseGameSystem):
    """Система управления эффектами - интегрирована с новой архитектурой"""
    
    def __init__(self):
        super().__init__("effects", Priority.HIGH)
        
        # Интеграция с новой архитектурой
        self.state_manager: Optional[StateManager] = None
        self.repository_manager: Optional[RepositoryManager] = None
        self.event_bus = None
        
        # Зарегистрированные эффекты (теперь управляются через RepositoryManager)
        self.registered_effects: Dict[str, Effect] = {}
        
        # Специальные эффекты (теперь управляются через RepositoryManager)
        self.special_effects: Dict[str, SpecialEffect] = {}
        
        # Активные эффекты на сущностях (теперь управляются через RepositoryManager)
        self.active_effects: Dict[str, List[ActiveEffect]] = {}
        
        # История применения эффектов (теперь управляется через RepositoryManager)
        self.effect_history: List[Dict[str, Any]] = []
        
        # Настройки системы (теперь управляются через StateManager)
        self.system_settings = {
            'max_effects_per_entity': SYSTEM_LIMITS["max_effects_per_entity"],
            'max_special_effects': 100,
            'effect_cleanup_interval': get_float(TIME_CONSTANTS_RO, "effect_cleanup_interval", 60.0),
            'stacking_enabled': True,
            'effect_combining_enabled': True
        }
        
        # Статистика системы (теперь управляется через StateManager)
        self.system_stats = {
            'registered_effects_count': 0,
            'special_effects_count': 0,
            'total_active_effects': 0,
            'effects_applied_today': 0,
            'effects_removed_today': 0,
            'update_time': 0.0
        }
        
        logger.info("Система эффектов инициализирована с новой архитектурой")
    
    def initialize(self) -> bool:
        """Инициализация системы эффектов с новой архитектурой"""
        try:
            logger.info("Инициализация системы эффектов...")
            
            # Инициализация базового компонента
            if not super().initialize():
                return False
            
            # Настраиваем систему
            self._setup_effect_system()
            
            # Загружаем базовые эффекты
            self._load_base_effects()
            
            # Регистрируем состояния в StateManager
            self._register_system_states()
            
            # Регистрируем репозитории в RepositoryManager
            self._register_system_repositories()

            # Подписки на события для интеграции
            try:
                if self.event_bus:
                    self.event_bus.on("apply_effect", self._on_apply_effect_event)
                    self.event_bus.on("remove_effect", self._on_remove_effect_event)
            except Exception:
                pass
            
            logger.info("Система эффектов успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы эффектов: {e}")
            return False
    
    def start(self) -> bool:
        """Запуск системы эффектов"""
        try:
            if not super().start():
                return False
            
            # Восстанавливаем данные из репозиториев
            self._restore_from_repositories()
            
            logger.info("Система эффектов запущена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска системы эффектов: {e}")
            return False
    
    def stop(self) -> bool:
        """Остановка системы эффектов"""
        try:
            # Сохраняем данные в репозитории
            self._save_to_repositories()
            
            return super().stop()
            
        except Exception as e:
            logger.error(f"Ошибка остановки системы эффектов: {e}")
            return False
    
    def destroy(self) -> bool:
        """Уничтожение системы эффектов"""
        try:
            # Сохраняем финальные данные
            self._save_to_repositories()
            
            # Очищаем все данные
            self.registered_effects.clear()
            self.special_effects.clear()
            self.active_effects.clear()
            self.effect_history.clear()
            
            return super().destroy()
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения системы эффектов: {e}")
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы эффектов"""
        try:
            if not super().update(delta_time):
                return False
            
            start_time = time.time()
            
            # Троттлинг обновления согласно конфигу
            if not hasattr(self, '_accumulated_time'):
                self._accumulated_time = 0.0
            self._accumulated_time += delta_time
            if self._accumulated_time < get_float(TIME_CONSTANTS_RO, "effect_update_interval", 0.1):
                return True
            throttle_dt = self._accumulated_time
            self._accumulated_time = 0.0
            
            # Обновляем активные эффекты
            self._update_active_effects(throttle_dt)
            
            # Очищаем истекшие эффекты
            self._cleanup_expired_effects()
            
            # Обновляем статистику системы
            self._update_system_stats()
            
            # Обновляем состояния в StateManager
            self._update_states()
            
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы эффектов: {e}")
            return False
    
    def _register_system_states(self) -> None:
        """Регистрация состояний системы (единый источник)"""
        if not self.state_manager:
            return
        
        self.state_manager.register_container(
            "effect_system_settings",
            StateType.CONFIGURATION,
            StateScope.SYSTEM,
            self.system_settings
        )
        
        self.state_manager.register_container(
            "effect_system_stats",
            StateType.STATISTICS,
            StateScope.SYSTEM,
            self.system_stats
        )
        
        self.state_manager.register_container(
            "active_effects",
            StateType.DATA,
            StateScope.GLOBAL,
            {}
        )
        
        logger.info("Состояния системы эффектов зарегистрированы")

    # Сохранение обратной совместимости
    def _register_states(self) -> None:
        self._register_system_states()
    
    def _register_system_repositories(self) -> None:
        """Регистрация репозиториев системы (единый источник)"""
        if not self.repository_manager:
            return
        
        self.repository_manager.register_repository(
            "registered_effects",
            DataType.CONFIGURATION,
            StorageType.MEMORY,
            self.registered_effects
        )
        self.repository_manager.register_repository(
            "special_effects",
            DataType.CONFIGURATION,
            StorageType.MEMORY,
            self.special_effects
        )
        self.repository_manager.register_repository(
            "active_effects",
            DataType.DYNAMIC_DATA,
            StorageType.MEMORY,
            self.active_effects
        )
        self.repository_manager.register_repository(
            "effect_history",
            DataType.HISTORY,
            StorageType.MEMORY,
            self.effect_history
        )
        
        logger.info("Репозитории системы эффектов зарегистрированы")

    # Сохранение обратной совместимости
    def _register_repositories(self) -> None:
        self._register_system_repositories()
    
    def _restore_from_repositories(self) -> None:
        """Восстановление данных из репозиториев"""
        if not self.repository_manager:
            return
        
        try:
            # Восстанавливаем зарегистрированные эффекты
            effects_repo = self.repository_manager.get_repository("registered_effects")
            if effects_repo:
                self.registered_effects = effects_repo.get_all()
            
            # Восстанавливаем специальные эффекты
            special_repo = self.repository_manager.get_repository("special_effects")
            if special_repo:
                self.special_effects = special_repo.get_all()
            
            # Восстанавливаем активные эффекты
            active_repo = self.repository_manager.get_repository("active_effects")
            if active_repo:
                self.active_effects = active_repo.get_all()
            
            # Восстанавливаем историю
            history_repo = self.repository_manager.get_repository("effect_history")
            if history_repo:
                self.effect_history = history_repo.get_all()
            
            logger.info("Данные системы эффектов восстановлены из репозиториев")
            
        except Exception as e:
            logger.error(f"Ошибка восстановления данных из репозиториев: {e}")
    
    def _save_to_repositories(self) -> None:
        """Сохранение данных в репозитории"""
        if not self.repository_manager:
            return
        
        try:
            # Сохраняем зарегистрированные эффекты
            effects_repo = self.repository_manager.get_repository("registered_effects")
            if effects_repo:
                effects_repo.clear()
                for effect_id, effect in self.registered_effects.items():
                    effects_repo.create(effect_id, effect)
            
            # Сохраняем специальные эффекты
            special_repo = self.repository_manager.get_repository("special_effects")
            if special_repo:
                special_repo.clear()
                for effect_id, effect in self.special_effects.items():
                    special_repo.create(effect_id, effect)
            
            # Сохраняем активные эффекты
            active_repo = self.repository_manager.get_repository("active_effects")
            if active_repo:
                active_repo.clear()
                for entity_id, effects in self.active_effects.items():
                    active_repo.create(entity_id, effects)
            
            # Сохраняем историю
            history_repo = self.repository_manager.get_repository("effect_history")
            if history_repo:
                history_repo.clear()
                for i, record in enumerate(self.effect_history):
                    history_repo.create(f"history_{i}", record)
            
            logger.info("Данные системы эффектов сохранены в репозитории")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения данных в репозитории: {e}")
    
    def _update_states(self) -> None:
        """Обновление состояний в StateManager"""
        if not self.state_manager:
            return
        
        try:
            # Обновляем статистику системы
            self.state_manager.set_state_value("effect_system_stats", self.system_stats)
            
            # Обновляем активные эффекты
            self.state_manager.set_state_value("active_effects", self.active_effects)
            
        except Exception as e:
            logger.error(f"Ошибка обновления состояний: {e}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        return {
            **self.system_stats,
            'registered_effects': len(self.registered_effects),
            'special_effects': len(self.special_effects),
            'entities_with_effects': len(self.active_effects),
            'system_name': self.system_name,
            'system_state': self.system_state.value,
            'system_priority': self.system_priority.value
        }
    
    def reset_stats(self) -> None:
        """Сброс статистики системы"""
        self.system_stats = {
            'registered_effects_count': 0,
            'special_effects_count': 0,
            'total_active_effects': 0,
            'effects_applied_today': 0,
            'effects_removed_today': 0,
            'update_time': 0.0
        }
            
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий - интеграция с новой архитектурой"""
        try:
            if isinstance(event_type, str):
                norm_tr = normalize_trigger(event_type)
                event_type = norm_tr.value if norm_tr else normalize_ui_event(event_type)
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
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'registered_effects': len(self.registered_effects),
            'special_effects': len(self.special_effects),
            'entities_with_effects': len(self.active_effects),
            'total_active_effects': self.system_stats['total_active_effects'],
            'stats': self.system_stats
        }
    
    def _setup_effect_system(self) -> None:
        """Настройка системы эффектов"""
        try:
            # Получаем настройки из StateManager
            settings_container = self.state_manager.get_container("effect_system_settings")
            if settings_container:
                self.system_settings.update(settings_container.data)
                logger.info(f"Настройки системы эффектов обновлены: {self.system_settings}")
            
            # Получаем статистику из StateManager
            stats_container = self.state_manager.get_container("effect_system_stats")
            if stats_container:
                self.system_stats.update(stats_container.data)
                logger.info(f"Статистика системы эффектов обновлена: {self.system_stats}")
            
        except Exception as e:
            logger.error(f"Ошибка настройки системы эффектов: {e}")
    
    def _load_base_effects(self) -> None:
        """Загрузка базовых эффектов из RepositoryManager"""
        try:
            # Получаем зарегистрированные эффекты из репозитория
            effects_repo = self.repository_manager.get_repository("registered_effects")
            if effects_repo:
                self.registered_effects = effects_repo.get_all()
                logger.info(f"Загружено {len(self.registered_effects)} базовых эффектов")
            
            # Получаем специальные эффекты из репозитория
            special_repo = self.repository_manager.get_repository("special_effects")
            if special_repo:
                self.special_effects = special_repo.get_all()
                logger.info(f"Загружено {len(self.special_effects)} специальных эффектов")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки базовых эффектов: {e}")
    
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
                                if registered_effect.trigger_type == TriggerType.ON_ENTER_COMBAT:
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

    # --- Event bus integration ---
    def _on_apply_effect_event(self, data: Dict[str, Any]) -> None:
        try:
            effect_id = data.get('effect_id')
            target = data.get('target')
            target_id = data.get('target_id') or data.get('entity_id')
            applied_by = data.get('applied_by') or data.get('source_id')
            if target is None and target_id:
                target = get_entity(target_id)
            duration = data.get('duration')
            if effect_id and (target_id or target is not None):
                # В системе эффектов активные эффекты хранятся по entity_id, но используем id, если объект известен
                resolved_target_id = target_id
                if resolved_target_id is None and target is not None:
                    resolved_target_id = getattr(target, 'id', getattr(target, 'entity_id', None))
                if resolved_target_id:
                    self.apply_effect_to_entity(effect_id, resolved_target_id, applied_by, duration)
        except Exception:
            pass

    def _on_remove_effect_event(self, data: Dict[str, Any]) -> None:
        try:
            effect_id = data.get('effect_id')
            target_id = data.get('target_id') or data.get('entity_id')
            if effect_id and target_id:
                self.remove_effect_from_entity(target_id, effect_id)
        except Exception:
            pass

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

    def combine_effects(self, effect1: Effect, effect2: Effect) -> Optional[Effect]:
        """Комбинирование двух эффектов для создания нового эффекта"""
        try:
            # Проверяем, можно ли комбинировать эффекты
            if not self.system_settings['effect_combining_enabled']:
                return None
            
            # Создаем комбинированный эффект
            combined_effect = Effect(
                effect_id=f"combined_{effect1.effect_id}_{effect2.effect_id}",
                name=f"Комбинированный: {effect1.name} + {effect2.name}",
                description=f"Комбинация эффектов {effect1.name} и {effect2.name}",
                category=EffectCategory.COMBINED,
                trigger_type=TriggerType.ON_COMBINE,
                duration=max(effect1.duration, effect2.duration),
                magnitude=(effect1.magnitude + effect2.magnitude) * 0.8,  # Небольшое ослабление
                target_stats=list(set(effect1.target_stats + effect2.target_stats)),
                damage_type=effect1.damage_type or effect2.damage_type,
                special_effects=effect1.special_effects + effect2.special_effects,
                stackable=False,
                max_stacks=1
            )
            
            logger.info(f"Создан комбинированный эффект: {combined_effect.name}")
            return combined_effect
            
        except Exception as e:
            logger.error(f"Ошибка комбинирования эффектов: {e}")
            return None
