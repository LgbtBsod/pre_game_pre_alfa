#!/usr/bin/env python3
"""
Система AI - управление искусственным интеллектом для игровых сущностей
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from ...core.interfaces import ISystem, SystemPriority, SystemState

logger = logging.getLogger(__name__)

class AIState(Enum):
    """Состояния AI"""
    IDLE = "idle"
    PATROLLING = "patrolling"
    CHASING = "chasing"
    ATTACKING = "attacking"
    FLEEING = "fleeing"
    SEARCHING = "searching"
    RESTING = "resting"

class AIBehavior(Enum):
    """Типы поведения AI"""
    PASSIVE = "passive"
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    CAUTIOUS = "cautious"
    BERSERK = "berserk"
    TACTICAL = "tactical"

class AIDifficulty(Enum):
    """Уровни сложности AI"""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"
    MASTER = "master"

@dataclass
class AIConfig:
    """Конфигурация AI"""
    behavior: AIBehavior = AIBehavior.AGGRESSIVE
    difficulty: AIDifficulty = AIDifficulty.NORMAL
    vision_range: float = 10.0
    hearing_range: float = 15.0
    attack_range: float = 2.0
    chase_speed: float = 1.2
    patrol_speed: float = 0.8
    decision_delay: float = 0.5
    memory_duration: float = 30.0
    group_coordination: bool = False

@dataclass
class AIMemory:
    """Память AI"""
    entity_id: str
    memory_type: str
    timestamp: float
    data: Dict[str, Any] = field(default_factory=dict)
    importance: float = 1.0

@dataclass
class AIDecision:
    """Решение AI"""
    decision_id: str
    entity_id: str
    action_type: str
    target_id: Optional[str] = None
    priority: float = 1.0
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)

class AISystem(ISystem):
    """Система управления искусственным интеллектом"""
    
    def __init__(self):
        self._system_name = "ai"
        self._system_priority = SystemPriority.NORMAL
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # AI сущности
        self.ai_entities: Dict[str, Dict[str, Any]] = {}
        
        # Конфигурации AI
        self.ai_configs: Dict[str, AIConfig] = {}
        
        # Память AI
        self.ai_memories: Dict[str, List[AIMemory]] = {}
        
        # Решения AI
        self.ai_decisions: Dict[str, List[AIDecision]] = {}
        
        # Группы AI
        self.ai_groups: Dict[str, List[str]] = {}
        
        # Настройки системы
        self.system_settings = {
            'max_ai_entities': 1000,
            'max_memory_per_entity': 100,
            'max_decisions_per_entity': 50,
            'decision_processing_rate': 10,  # решений в секунду
            'memory_cleanup_interval': 60.0,  # секунды
            'group_coordination_enabled': True
        }
        
        # Статистика системы
        self.system_stats = {
            'ai_entities_count': 0,
            'ai_groups_count': 0,
            'total_decisions_made': 0,
            'total_memories_stored': 0,
            'active_behaviors': {},
            'update_time': 0.0
        }
        
        logger.info("Система AI инициализирована")
    
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
        """Инициализация системы AI"""
        try:
            logger.info("Инициализация системы AI...")
            
            # Настраиваем систему
            self._setup_ai_system()
            
            self._system_state = SystemState.READY
            logger.info("Система AI успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы AI: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы AI"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем AI сущности
            self._update_ai_entities(delta_time)
            
            # Обрабатываем решения
            self._process_ai_decisions(delta_time)
            
            # Очищаем старую память
            self._cleanup_old_memories()
            
            # Обновляем статистику системы
            self._update_system_stats()
            
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы AI: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы AI"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система AI приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы AI: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы AI"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система AI возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы AI: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы AI"""
        try:
            logger.info("Очистка системы AI...")
            
            # Очищаем все данные
            self.ai_entities.clear()
            self.ai_configs.clear()
            self.ai_memories.clear()
            self.ai_decisions.clear()
            self.ai_groups.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'ai_entities_count': 0,
                'ai_groups_count': 0,
                'total_decisions_made': 0,
                'total_memories_stored': 0,
                'active_behaviors': {},
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система AI очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы AI: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'ai_entities': len(self.ai_entities),
            'ai_groups': len(self.ai_groups),
            'total_memories': sum(len(memories) for memories in self.ai_memories.values()),
            'total_decisions': sum(len(decisions) for decisions in self.ai_decisions.values()),
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "entity_destroyed":
                return self._handle_entity_destroyed(event_data)
            elif event_type == "ai_event":
                return self._handle_ai_event(event_data)
            elif event_type == "combat_event":
                return self._handle_combat_event(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def _setup_ai_system(self) -> None:
        """Настройка системы AI"""
        try:
            # Инициализируем базовые настройки
            logger.debug("Система AI настроена")
        except Exception as e:
            logger.warning(f"Не удалось настроить систему AI: {e}")
    
    def _update_ai_entities(self, delta_time: float) -> None:
        """Обновление AI сущностей"""
        try:
            current_time = time.time()
            
            for entity_id, ai_data in self.ai_entities.items():
                # Проверяем, не истекло ли время последнего решения
                if current_time - ai_data.get('last_decision_time', 0) >= ai_data.get('decision_delay', 1.0):
                    # Принимаем новое решение
                    decision = self._make_ai_decision(entity_id, ai_data)
                    if decision:
                        self._add_ai_decision(entity_id, decision)
                        ai_data['last_decision_time'] = current_time
                
                # Обновляем состояние AI
                self._update_ai_state(entity_id, ai_data, delta_time)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления AI сущностей: {e}")
    
    def _process_ai_decisions(self, delta_time: float) -> None:
        """Обработка решений AI"""
        try:
            # Ограничиваем количество обрабатываемых решений в секунду
            max_decisions = int(self.system_settings['decision_processing_rate'] * delta_time)
            processed = 0
            
            for entity_id, decisions in self.ai_decisions.items():
                if processed >= max_decisions:
                    break
                
                # Обрабатываем решения по приоритету
                sorted_decisions = sorted(decisions, key=lambda d: d.priority, reverse=True)
                
                for decision in sorted_decisions[:max_decisions - processed]:
                    if self._execute_ai_decision(entity_id, decision):
                        # Удаляем выполненное решение
                        decisions.remove(decision)
                        processed += 1
                        
                        if processed >= max_decisions:
                            break
                
        except Exception as e:
            logger.warning(f"Ошибка обработки решений AI: {e}")
    
    def _cleanup_old_memories(self) -> None:
        """Очистка старой памяти"""
        try:
            current_time = time.time()
            memory_duration = self.system_settings['memory_cleanup_interval']
            
            for entity_id, memories in self.ai_memories.items():
                # Удаляем старые воспоминания
                memories[:] = [mem for mem in memories 
                              if current_time - mem.timestamp < memory_duration]
                
        except Exception as e:
            logger.warning(f"Ошибка очистки старой памяти: {e}")
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            self.system_stats['ai_entities_count'] = len(self.ai_entities)
            self.system_stats['ai_groups_count'] = len(self.ai_groups)
            
            # Подсчитываем активные поведения
            behaviors = {}
            for ai_data in self.ai_entities.values():
                behavior = ai_data.get('behavior', 'unknown')
                behaviors[behavior] = behaviors.get(behavior, 0) + 1
            
            self.system_stats['active_behaviors'] = behaviors
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
            entity_id = event_data.get('entity_id')
            ai_config = event_data.get('ai_config')
            
            if entity_id and ai_config:
                return self.register_ai_entity(entity_id, ai_config)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания сущности: {e}")
            return False
    
    def _handle_entity_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения сущности"""
        try:
            entity_id = event_data.get('entity_id')
            
            if entity_id:
                return self.unregister_ai_entity(entity_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события уничтожения сущности: {e}")
            return False
    
    def _handle_ai_event(self, event_data: Dict[str, Any]) -> bool:
        """Обработка AI события"""
        try:
            entity_id = event_data.get('entity_id')
            event_type = event_data.get('event_type')
            event_data_dict = event_data.get('data', {})
            
            if entity_id and event_type:
                return self._process_ai_event(entity_id, event_type, event_data_dict)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки AI события: {e}")
            return False
    
    def _handle_combat_event(self, event_data: Dict[str, Any]) -> bool:
        """Обработка боевого события"""
        try:
            # Обрабатываем боевые события
            if event_type == "damage_taken":
                # AI получил урон - возможно, нужно убежать
                if entity_id in self.ai_entities:
                    ai_data = self.ai_entities[entity_id]
                    if ai_data['health'] < ai_data['max_health'] * 0.3:  # Меньше 30% здоровья
                        decision = AIDecision(
                            decision_id=f"flee_{int(time.time() * 1000)}",
                            entity_id=entity_id,
                            action_type="flee",
                            priority=0.9
                        )
                        self._add_ai_decision(entity_id, decision)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обработки боевого события: {e}")
            return False
    
    def register_ai_entity(self, entity_id: str, ai_config: Union[AIConfig, Dict[str, Any]]) -> bool:
        """Регистрация AI сущности"""
        try:
            if entity_id in self.ai_entities:
                logger.warning(f"AI сущность {entity_id} уже зарегистрирована")
                return False
            
            if len(self.ai_entities) >= self.system_settings['max_ai_entities']:
                logger.warning("Достигнут лимит AI сущностей")
                return False
            
            # Создаем конфигурацию AI
            if isinstance(ai_config, dict):
                config = AIConfig(**ai_config)
            else:
                config = ai_config
            
            # Создаем AI данные
            ai_data = {
                'id': entity_id,
                'config': config,
                'state': AIState.IDLE,
                'current_target': None,
                'last_decision_time': 0.0,
                'behavior': config.behavior.value,
                'difficulty': config.difficulty.value,
                'patrol_points': [],
                'current_patrol_index': 0,
                'health': 100,
                'max_health': 100,
                'position': {'x': 0, 'y': 0, 'z': 0},
                'last_known_player_position': None
            }
            
            self.ai_entities[entity_id] = ai_data
            self.ai_configs[entity_id] = config
            self.ai_memories[entity_id] = []
            self.ai_decisions[entity_id] = []
            
            logger.info(f"AI сущность {entity_id} зарегистрирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации AI сущности {entity_id}: {e}")
            return False
    
    def unregister_ai_entity(self, entity_id: str) -> bool:
        """Отмена регистрации AI сущности"""
        try:
            if entity_id in self.ai_entities:
                del self.ai_entities[entity_id]
            
            if entity_id in self.ai_configs:
                del self.ai_configs[entity_id]
            
            if entity_id in self.ai_memories:
                del self.ai_memories[entity_id]
            
            if entity_id in self.ai_decisions:
                del self.ai_decisions[entity_id]
            
            # Удаляем из групп
            for group_id, members in list(self.ai_groups.items()):
                if entity_id in members:
                    members.remove(entity_id)
                    if not members:
                        del self.ai_groups[group_id]
            
            logger.info(f"AI сущность {entity_id} удалена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления AI сущности {entity_id}: {e}")
            return False
    
    def _make_ai_decision(self, entity_id: str, ai_data: Dict[str, Any]) -> Optional[AIDecision]:
        """Принятие решения AI"""
        try:
            config = ai_data['config']
            current_state = ai_data['state']
            
            # Простая логика принятия решений
            if current_state == AIState.IDLE:
                # Проверяем, есть ли враги поблизости
                nearby_enemies = self._detect_nearby_enemies(entity_id, config.vision_range)
                if nearby_enemies:
                    return AIDecision(
                        decision_id=f"chase_{int(time.time() * 1000)}",
                        entity_id=entity_id,
                        action_type="chase",
                        target_id=nearby_enemies[0],
                        priority=0.8
                    )
                else:
                    # Патрулируем
                    return AIDecision(
                        decision_id=f"patrol_{int(time.time() * 1000)}",
                        entity_id=entity_id,
                        action_type="patrol",
                        priority=0.3
                    )
            
            elif current_state == AIState.CHASING:
                # Проверяем, можем ли атаковать
                if ai_data['current_target']:
                    target_distance = self._calculate_distance(entity_id, ai_data['current_target'])
                    if target_distance <= config.attack_range:
                        return AIDecision(
                            decision_id=f"attack_{int(time.time() * 1000)}",
                            entity_id=entity_id,
                            action_type="attack",
                            target_id=ai_data['current_target'],
                            priority=0.9
                        )
            
            elif current_state == AIState.ATTACKING:
                # Проверяем, не нужно ли отступить
                if ai_data['current_target']:
                    target_distance = self._calculate_distance(entity_id, ai_data['current_target'])
                    if target_distance > config.attack_range:
                        return AIDecision(
                            decision_id=f"chase_{int(time.time() * 1000)}",
                            entity_id=entity_id,
                            action_type="chase",
                            target_id=ai_data['current_target'],
                            priority=0.7
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка принятия решения AI для {entity_id}: {e}")
            return None
    
    def _execute_ai_decision(self, entity_id: str, decision: AIDecision) -> bool:
        """Выполнение решения AI"""
        try:
            if decision.action_type == "chase":
                return self._execute_chase_action(entity_id, decision)
            elif decision.action_type == "attack":
                return self._execute_attack_action(entity_id, decision)
            elif decision.action_type == "patrol":
                return self._execute_patrol_action(entity_id, decision)
            elif decision.action_type == "flee":
                return self._execute_flee_action(entity_id, decision)
            else:
                logger.warning(f"Неизвестный тип действия AI: {decision.action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка выполнения решения AI {decision.decision_id}: {e}")
            return False
    
    def _execute_chase_action(self, entity_id: str, decision: AIDecision) -> bool:
        """Выполнение действия преследования"""
        try:
            ai_data = self.ai_entities[entity_id]
            ai_data['state'] = AIState.CHASING
            ai_data['current_target'] = decision.target_id
            
            # Логируем действие
            logger.debug(f"AI {entity_id} преследует {decision.target_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выполнения действия преследования: {e}")
            return False
    
    def _execute_attack_action(self, entity_id: str, decision: AIDecision) -> bool:
        """Выполнение действия атаки"""
        try:
            ai_data = self.ai_entities[entity_id]
            ai_data['state'] = AIState.ATTACKING
            
            # Логируем действие
            logger.debug(f"AI {entity_id} атакует {decision.target_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выполнения действия атаки: {e}")
            return False
    
    def _execute_patrol_action(self, entity_id: str, decision: AIDecision) -> bool:
        """Выполнение действия патрулирования"""
        try:
            ai_data = self.ai_entities[entity_id]
            ai_data['state'] = AIState.PATROLLING
            
            # Логируем действие
            logger.debug(f"AI {entity_id} патрулирует")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выполнения действия патрулирования: {e}")
            return False
    
    def _execute_flee_action(self, entity_id: str, decision: AIDecision) -> bool:
        """Выполнение действия бегства"""
        try:
            ai_data = self.ai_entities[entity_id]
            ai_data['state'] = AIState.FLEEING
            ai_data['current_target'] = None
            
            # Логируем действие
            logger.debug(f"AI {entity_id} убегает")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выполнения действия бегства: {e}")
            return False
    
    def _update_ai_state(self, entity_id: str, ai_data: Dict[str, Any], delta_time: float) -> None:
        """Обновление состояния AI"""
        try:
            current_state = ai_data['state']
            
            if current_state == AIState.PATROLLING:
                self._update_patrol_state(entity_id, ai_data, delta_time)
            elif current_state == AIState.CHASING:
                self._update_chase_state(entity_id, ai_data, delta_time)
            elif current_state == AIState.ATTACKING:
                self._update_attack_state(entity_id, ai_data, delta_time)
            elif current_state == AIState.FLEEING:
                self._update_flee_state(entity_id, ai_data, delta_time)
                
        except Exception as e:
            logger.error(f"Ошибка обновления состояния AI {entity_id}: {e}")
    
    def _update_patrol_state(self, entity_id: str, ai_data: Dict[str, Any], delta_time: float) -> None:
        """Обновление состояния патрулирования"""
        try:
            # Простая логика патрулирования
            pass
        except Exception as e:
            logger.error(f"Ошибка обновления состояния патрулирования: {e}")
    
    def _update_chase_state(self, entity_id: str, ai_data: Dict[str, Any], delta_time: float) -> None:
        """Обновление состояния преследования"""
        try:
            # Простая логика преследования
            pass
        except Exception as e:
            logger.error(f"Ошибка обновления состояния преследования: {e}")
    
    def _update_attack_state(self, entity_id: str, ai_data: Dict[str, Any], delta_time: float) -> None:
        """Обновление состояния атаки"""
        try:
            # Простая логика атаки
            pass
        except Exception as e:
            logger.error(f"Ошибка обновления состояния атаки: {e}")
    
    def _update_flee_state(self, entity_id: str, ai_data: Dict[str, Any], delta_time: float) -> None:
        """Обновление состояния бегства"""
        try:
            # Простая логика бегства
            pass
        except Exception as e:
            logger.error(f"Ошибка обновления состояния бегства: {e}")
    
    def _detect_nearby_enemies(self, entity_id: str, vision_range: float) -> List[str]:
        """Обнаружение врагов поблизости"""
        try:
            # Упрощенная реализация - возвращаем пустой список
            return []
        except Exception as e:
            logger.error(f"Ошибка обнаружения врагов: {e}")
            return []
    
    def _calculate_distance(self, entity_id: str, target_id: str) -> float:
        """Расчет расстояния между сущностями"""
        try:
            # Упрощенная реализация - возвращаем случайное расстояние
            return random.uniform(1.0, 20.0)
        except Exception as e:
            logger.error(f"Ошибка расчета расстояния: {e}")
            return 10.0
    
    def _add_ai_decision(self, entity_id: str, decision: AIDecision) -> None:
        """Добавление решения AI"""
        try:
            if entity_id in self.ai_decisions:
                decisions = self.ai_decisions[entity_id]
                
                # Ограничиваем количество решений
                if len(decisions) >= self.system_settings['max_decisions_per_entity']:
                    # Удаляем самое старое решение с низким приоритетом
                    decisions.sort(key=lambda d: (d.priority, d.timestamp))
                    if decisions and decisions[0].priority < decision.priority:
                        decisions.pop(0)
                    else:
                        return  # Не добавляем новое решение
                
                decisions.append(decision)
                self.system_stats['total_decisions_made'] += 1
                
        except Exception as e:
            logger.error(f"Ошибка добавления решения AI: {e}")
    
    def _process_ai_event(self, entity_id: str, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Обработка AI события"""
        try:
            # Создаем память о событии
            memory = AIMemory(
                entity_id=entity_id,
                memory_type=event_type,
                timestamp=time.time(),
                data=event_data,
                importance=event_data.get('importance', 1.0)
            )
            
            if entity_id in self.ai_memories:
                memories = self.ai_memories[entity_id]
                
                # Ограничиваем количество воспоминаний
                if len(memories) >= self.system_settings['max_memory_per_entity']:
                    # Удаляем самое старое воспоминание с низкой важностью
                    memories.sort(key=lambda m: (m.importance, m.timestamp))
                    if memories and memories[0].importance < memory.importance:
                        memories.pop(0)
                    else:
                        return False
                
                memories.append(memory)
                self.system_stats['total_memories_stored'] += 1
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки AI события: {e}")
            return False
    
    def _process_combat_event(self, entity_id: str, event_type: str, combat_data: Dict[str, Any]) -> bool:
        """Обработка боевого события"""
        try:
            # Обрабатываем боевые события
            if event_type == "damage_taken":
                # AI получил урон - возможно, нужно убежать
                if entity_id in self.ai_entities:
                    ai_data = self.ai_entities[entity_id]
                    if ai_data['health'] < ai_data['max_health'] * 0.3:  # Меньше 30% здоровья
                        decision = AIDecision(
                            decision_id=f"flee_{int(time.time() * 1000)}",
                            entity_id=entity_id,
                            action_type="flee",
                            priority=0.9
                        )
                        self._add_ai_decision(entity_id, decision)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обработки боевого события: {e}")
            return False
    
    def get_ai_entity_info(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации об AI сущности"""
        try:
            if entity_id not in self.ai_entities:
                return None
            
            ai_data = self.ai_entities[entity_id]
            config = self.ai_configs.get(entity_id)
            
            return {
                'id': entity_id,
                'state': ai_data['state'].value,
                'behavior': ai_data['behavior'],
                'difficulty': ai_data['difficulty'],
                'current_target': ai_data['current_target'],
                'health': ai_data['health'],
                'max_health': ai_data['max_health'],
                'position': ai_data['position'],
                'config': {
                    'vision_range': config.vision_range,
                    'hearing_range': config.hearing_range,
                    'attack_range': config.attack_range,
                    'chase_speed': config.chase_speed,
                    'patrol_speed': config.patrol_speed
                } if config else {},
                'memories_count': len(self.ai_memories.get(entity_id, [])),
                'decisions_count': len(self.ai_decisions.get(entity_id, []))
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации об AI сущности {entity_id}: {e}")
            return None
    
    def update_ai_entity_health(self, entity_id: str, health: int, max_health: int) -> bool:
        """Обновление здоровья AI сущности"""
        try:
            if entity_id in self.ai_entities:
                self.ai_entities[entity_id]['health'] = health
                self.ai_entities[entity_id]['max_health'] = max_health
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка обновления здоровья AI сущности {entity_id}: {e}")
            return False
    
    def update_ai_entity_position(self, entity_id: str, position: Dict[str, float]) -> bool:
        """Обновление позиции AI сущности"""
        try:
            if entity_id in self.ai_entities:
                self.ai_entities[entity_id]['position'] = position
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка обновления позиции AI сущности {entity_id}: {e}")
            return False
