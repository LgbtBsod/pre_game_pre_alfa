#!/usr/bin/env python3
"""
Система искусственного интеллекта - управление AI сущностями
"""

import logging
import time
import random
import math
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field

from core.interfaces import ISystem, SystemPriority, SystemState
from core.constants import constants_manager, (
    AIState, AIBehavior, AIDifficulty, StatType,
    BASE_STATS, PROBABILITY_CONSTANTS, TIME_CONSTANTS, SYSTEM_LIMITS
)

logger = logging.getLogger(__name__)

@dataclass
class AIConfig:
    """Конфигурация AI"""
    behavior: AIBehavior = AIBehavior.AGGRESSIVE
    difficulty: AIDifficulty = AIDifficulty.NORMAL
    reaction_time: float = 0.5
    decision_frequency: float = 1.0
    memory_duration: float = 300.0  # 5 минут
    group_coordination: bool = False
    retreat_threshold: float = 0.2
    pursuit_range: float = 100.0
    patrol_radius: float = 50.0

@dataclass
class AIMemory:
    """Память AI"""
    entity_id: str
    last_seen: float
    last_position: Tuple[float, float, float]
    threat_level: float
    interaction_count: int = 0
    damage_dealt: float = 0.0
    damage_received: float = 0.0

@dataclass
class AIDecision:
    """Решение AI"""
    decision_type: str
    target_entity: Optional[str]
    action_data: Dict[str, Any]
    priority: float
    timestamp: float
    executed: bool = False

class AISystem(ISystem):
    """Система управления искусственным интеллектом"""
    
    def __init__(self):
        self._system_name = "ai"
        self._system_priority = SystemPriority.HIGH
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # AI сущности
        self.ai_entities: Dict[str, Dict[str, Any]] = {}
        
        # Конфигурации AI
        self.ai_configs: Dict[str, AIConfig] = {}
        
        # Память AI
        self.ai_memories: Dict[str, Dict[str, AIMemory]] = {}
        
        # Решения AI
        self.ai_decisions: Dict[str, List[AIDecision]] = {}
        
        # Группы AI
        self.ai_groups: Dict[str, List[str]] = {}
        
        # Настройки системы
        self.system_settings = {
            'max_ai_entities': SYSTEM_LIMITS["max_ai_entities"],
            'max_memory_per_entity': 100,
            'decision_queue_size': 50,
            'update_frequency': 0.1,  # 10 раз в секунду
            'pathfinding_enabled': True,
            'group_behavior_enabled': True
        }
        
        # Статистика системы
        self.system_stats = {
            'ai_entities_count': 0,
            'total_decisions_made': 0,
            'total_actions_executed': 0,
            'average_reaction_time': 0.0,
            'memory_usage': 0,
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
            
            # Обновляем память
            self._update_ai_memory(delta_time)
            
            # Координируем группы
            if self.system_settings['group_behavior_enabled']:
                self._coordinate_ai_groups(delta_time)
            
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
            
            # Очищаем все AI сущности
            self.ai_entities.clear()
            self.ai_configs.clear()
            self.ai_memories.clear()
            self.ai_decisions.clear()
            self.ai_groups.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'ai_entities_count': 0,
                'total_decisions_made': 0,
                'total_actions_executed': 0,
                'average_reaction_time': 0.0,
                'memory_usage': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система AI очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы AI: {e}")
            return False

    # --- Interface shims for AISystemManager compatibility ---
    def register_entity(self, entity_id: str, entity_data: Dict[str, Any], memory_group: str = "default") -> bool:
        try:
            # Minimal registration using available fields
            pos = (
                float(entity_data.get('x', 0.0)),
                float(entity_data.get('y', 0.0)),
                float(entity_data.get('z', 0.0)),
            )
            config = AIConfig()  # default config
            created = self.create_ai_entity(entity_id, config, pos)
            # seed minimal memory group holder if needed
            if created and entity_id not in self.ai_memories:
                self.ai_memories[entity_id] = {}
            return created
        except Exception as e:
            logger.error(f"register_entity shim failed: {e}")
            return False

    def get_decision(self, entity_id: str, context: Dict[str, Any]):
        try:
            # Trigger decision making on demand
            if entity_id in self.ai_entities:
                self._make_ai_decision(entity_id, self.ai_entities[entity_id])
                # Return latest pending decision if any
                decisions = self.ai_decisions.get(entity_id, [])
                for d in reversed(decisions):
                    if not d.executed:
                        # Provide a minimal object compatible with callers that check attributes
                        class _ShimDecision:
                            def __init__(self, dtype, target):
                                self.action_type = type('Action', (), {'value': dtype})
                                self.target = target
                                self.parameters = {}
                                self.confidence = 0.5
                        return _ShimDecision(d.decision_type, d.target_entity)
            return None
        except Exception as e:
            logger.error(f"get_decision shim failed: {e}")
            return None
    
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
            if event_type == "ai_entity_created":
                return self._handle_ai_entity_created(event_data)
            elif event_type == "ai_entity_destroyed":
                return self._handle_ai_entity_destroyed(event_data)
            elif event_type == "entity_detected":
                return self._handle_entity_detected(event_data)
            elif event_type == "combat_started":
                return self._handle_combat_started(event_data)
            elif event_type == "combat_ended":
                return self._handle_combat_ended(event_data)
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
            
            for entity_id, entity_data in self.ai_entities.items():
                if entity_data['state'] == AIState.DEAD:
                    continue
                
                # Проверяем, нужно ли принимать решение
                if current_time - entity_data['last_decision_time'] >= entity_data['config'].decision_frequency:
                    self._make_ai_decision(entity_id, entity_data)
                    entity_data['last_decision_time'] = current_time
                
                # Обновляем поведение
                self._update_ai_behavior(entity_id, entity_data, delta_time)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления AI сущностей: {e}")
    
    def _process_ai_decisions(self, delta_time: float) -> None:
        """Обработка решений AI"""
        try:
            current_time = time.time()
            
            for entity_id, decisions in self.ai_decisions.items():
                if entity_id not in self.ai_entities:
                    continue
                
                # Фильтруем невыполненные решения
                pending_decisions = [d for d in decisions if not d.executed]
                
                # Сортируем по приоритету
                pending_decisions.sort(key=lambda x: x.priority, reverse=True)
                
                # Выполняем решение с наивысшим приоритетом
                if pending_decisions:
                    decision = pending_decisions[0]
                    if self._execute_ai_decision(entity_id, decision):
                        decision.executed = True
                        self.system_stats['total_actions_executed'] += 1
                
                # Очищаем старые решения
                self.ai_decisions[entity_id] = [d for d in decisions if 
                                               current_time - d.timestamp < 60.0]
                
        except Exception as e:
            logger.warning(f"Ошибка обработки решений AI: {e}")
    
    def _update_ai_memory(self, delta_time: float) -> None:
        """Обновление памяти AI"""
        try:
            current_time = time.time()
            
            for entity_id, memories in self.ai_memories.items():
                # Удаляем устаревшие воспоминания
                valid_memories = {}
                for target_id, memory in memories.items():
                    if current_time - memory.last_seen > memory.threat_level * 300.0:  # 5 минут * threat_level
                        valid_memories[target_id] = memory
                
                self.ai_memories[entity_id] = valid_memories
                
        except Exception as e:
            logger.warning(f"Ошибка обновления памяти AI: {e}")
    
    def _coordinate_ai_groups(self, delta_time: float) -> None:
        """Координация групп AI"""
        try:
            for group_id, members in self.ai_groups.items():
                if len(members) < 2:
                    continue
                
                # Простая координация - лидер группы
                leader = members[0]
                if leader in self.ai_entities:
                    leader_data = self.ai_entities[leader]
                    
                    # Члены группы следуют за лидером
                    for member_id in members[1:]:
                        if member_id in self.ai_entities:
                            member_data = self.ai_entities[member_id]
                            self._follow_leader(member_id, member_data, leader, leader_data)
                
        except Exception as e:
            logger.warning(f"Ошибка координации групп AI: {e}")
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            self.system_stats['ai_entities_count'] = len(self.ai_entities)
            self.system_stats['memory_usage'] = sum(len(memories) for memories in self.ai_memories.values())
            
            # Среднее время реакции
            if self.system_stats['total_actions_executed'] > 0:
                total_reaction_time = sum(
                    entity_data['config'].reaction_time 
                    for entity_data in self.ai_entities.values()
                )
                self.system_stats['average_reaction_time'] = total_reaction_time / len(self.ai_entities)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_ai_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания AI сущности"""
        try:
            entity_id = event_data.get('entity_id')
            ai_config = event_data.get('ai_config')
            position = event_data.get('position', (0.0, 0.0, 0.0))
            
            if entity_id and ai_config:
                return self.create_ai_entity(entity_id, ai_config, position)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания AI сущности: {e}")
            return False
    
    def _handle_ai_entity_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения AI сущности"""
        try:
            entity_id = event_data.get('entity_id')
            
            if entity_id:
                return self.destroy_ai_entity(entity_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события уничтожения AI сущности: {e}")
            return False
    
    def _handle_entity_detected(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события обнаружения сущности"""
        try:
            detector_id = event_data.get('detector_id')
            detected_id = event_data.get('detected_id')
            position = event_data.get('position', (0.0, 0.0, 0.0))
            threat_level = event_data.get('threat_level', 1.0)
            
            if detector_id and detected_id:
                return self.update_ai_memory(detector_id, detected_id, position, threat_level)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события обнаружения сущности: {e}")
            return False
    
    def _handle_combat_started(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события начала боя"""
        try:
            combat_id = event_data.get('combat_id')
            participants = event_data.get('participants')
            
            if combat_id and participants:
                # AI сущности переходят в состояние боя
                for participant_id in participants:
                    if participant_id in self.ai_entities:
                        self.ai_entities[participant_id]['state'] = AIState.IN_COMBAT
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события начала боя: {e}")
            return False
    
    def _handle_combat_ended(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события окончания боя"""
        try:
            combat_id = event_data.get('combat_id')
            result = event_data.get('result')
            participants = event_data.get('participants')
            
            if combat_id and participants:
                # AI сущности возвращаются к обычному состоянию
                for participant_id in participants:
                    if participant_id in self.ai_entities:
                        if result == "victory":
                            self.ai_entities[participant_id]['state'] = AIState.IDLE
                        else:
                            self.ai_entities[participant_id]['state'] = AIState.RETREATING
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события окончания боя: {e}")
            return False
    
    def create_ai_entity(self, entity_id: str, ai_config: AIConfig, position: Tuple[float, float, float]) -> bool:
        """Создание AI сущности"""
        try:
            if entity_id in self.ai_entities:
                logger.warning(f"AI сущность {entity_id} уже существует")
                return False
            
            if len(self.ai_entities) >= self.system_settings['max_ai_entities']:
                logger.warning("Достигнут лимит AI сущностей")
                return False
            
            # Создаем AI сущность
            entity_data = {
                'id': entity_id,
                'config': ai_config,
                'position': position,
                'state': AIState.IDLE,
                'last_decision_time': time.time(),
                'current_target': None,
                'patrol_points': [],
                'group_id': None
            }
            
            self.ai_entities[entity_id] = entity_data
            self.ai_configs[entity_id] = ai_config
            self.ai_memories[entity_id] = {}
            self.ai_decisions[entity_id] = []
            
            # Генерируем точки патрулирования
            try:
                patrol_enum = getattr(AIBehavior, 'PATROL', None)
            except Exception:
                patrol_enum = None
            if patrol_enum is not None and ai_config.behavior == patrol_enum:
                self._generate_patrol_points(entity_id, position, ai_config.patrol_radius)
            
            logger.info(f"AI сущность {entity_id} создана")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания AI сущности {entity_id}: {e}")
            return False
    
    def destroy_ai_entity(self, entity_id: str) -> bool:
        """Уничтожение AI сущности"""
        try:
            if entity_id not in self.ai_entities:
                return False
            
            # Удаляем из группы
            if entity_id in self.ai_groups:
                del self.ai_groups[entity_id]
            
            # Очищаем данные
            del self.ai_entities[entity_id]
            del self.ai_configs[entity_id]
            del self.ai_memories[entity_id]
            del self.ai_decisions[entity_id]
            
            logger.info(f"AI сущность {entity_id} уничтожена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения AI сущности {entity_id}: {e}")
            return False
    
    def update_ai_memory(self, entity_id: str, target_id: str, position: Tuple[float, float, float], threat_level: float) -> bool:
        """Обновление памяти AI"""
        try:
            if entity_id not in self.ai_memories:
                return False
            
            current_time = time.time()
            
            # Создаем или обновляем воспоминание
            memory = AIMemory(
                entity_id=target_id,
                last_seen=current_time,
                last_position=position,
                threat_level=threat_level
            )
            
            # Если воспоминание уже существует, обновляем счетчики
            if target_id in self.ai_memories[entity_id]:
                old_memory = self.ai_memories[entity_id][target_id]
                memory.interaction_count = old_memory.interaction_count + 1
                memory.damage_dealt = old_memory.damage_dealt
                memory.damage_received = old_memory.damage_received
            
            self.ai_memories[entity_id][target_id] = memory
            
            # Ограничиваем количество воспоминаний
            if len(self.ai_memories[entity_id]) > self.system_settings['max_memory_per_entity']:
                # Удаляем самое старое воспоминание
                oldest_memory = min(
                    self.ai_memories[entity_id].values(),
                    key=lambda x: x.last_seen
                )
                del self.ai_memories[entity_id][oldest_memory.entity_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления памяти AI: {e}")
            return False
    
    def _make_ai_decision(self, entity_id: str, entity_data: Dict[str, Any]) -> None:
        """Принятие решения AI"""
        try:
            config = entity_data['config']
            current_state = entity_data['state']
            
            # Анализируем окружение
            threats = self._analyze_threats(entity_id)
            opportunities = self._analyze_opportunities(entity_id)
            
            # Принимаем решение на основе поведения и состояния
            if current_state == AIState.IDLE:
                if threats and config.behavior != AIBehavior.PASSIVE:
                    decision = AIDecision(
                        decision_type="engage",
                        target_entity=threats[0]['entity_id'],
                        action_data={'action': 'attack'},
                        priority=threats[0]['threat_level'],
                        timestamp=time.time()
                    )
                elif opportunities and config.behavior == AIBehavior.AGGRESSIVE:
                    decision = AIDecision(
                        decision_type="hunt",
                        target_entity=opportunities[0]['entity_id'],
                        action_data={'action': 'pursue'},
                        priority=opportunities[0]['value'],
                        timestamp=time.time()
                    )
                elif config.behavior == AIBehavior.PATROL:
                    decision = AIDecision(
                        decision_type="patrol",
                        target_entity=None,
                        action_data={'action': 'move_to_patrol_point'},
                        priority=0.1,
                        timestamp=time.time()
                    )
                else:
                    return
            
            elif current_state == AIState.IN_COMBAT:
                if threats:
                    decision = AIDecision(
                        decision_type="combat",
                        target_entity=threats[0]['entity_id'],
                        action_data={'action': 'attack'},
                        priority=threats[0]['threat_level'] * 2,
                        timestamp=time.time()
                    )
                else:
                    decision = AIDecision(
                        decision_type="return_to_idle",
                        target_entity=None,
                        action_data={'action': 'idle'},
                        priority=0.5,
                        timestamp=time.time()
                    )
            
            elif current_state == AIState.RETREATING:
                decision = AIDecision(
                    decision_type="retreat",
                    target_entity=None,
                    action_data={'action': 'move_away'},
                    priority=1.0,
                    timestamp=time.time()
                )
            
            else:
                return
            
            # Добавляем решение в очередь
            self.ai_decisions[entity_id].append(decision)
            self.system_stats['total_decisions_made'] += 1
            
            # Ограничиваем размер очереди
            if len(self.ai_decisions[entity_id]) > self.system_settings['decision_queue_size']:
                self.ai_decisions[entity_id] = self.ai_decisions[entity_id][-self.system_settings['decision_queue_size']:]
            
        except Exception as e:
            logger.error(f"Ошибка принятия решения AI для {entity_id}: {e}")
    
    def _analyze_threats(self, entity_id: str) -> List[Dict[str, Any]]:
        """Анализ угроз для AI сущности"""
        try:
            threats = []
            
            if entity_id not in self.ai_memories:
                return threats
            
            current_time = time.time()
            
            for target_id, memory in self.ai_memories[entity_id].items():
                # Проверяем, не устарело ли воспоминание
                if current_time - memory.last_seen > memory.threat_level * 300.0:
                    continue
                
                # Рассчитываем уровень угрозы
                threat_level = memory.threat_level
                if memory.damage_received > 0:
                    threat_level *= 1.5
                
                threats.append({
                    'entity_id': target_id,
                    'threat_level': threat_level,
                    'position': memory.last_position,
                    'last_seen': memory.last_seen
                })
            
            # Сортируем по уровню угрозы
            threats.sort(key=lambda x: x['threat_level'], reverse=True)
            return threats
            
        except Exception as e:
            logger.error(f"Ошибка анализа угроз для {entity_id}: {e}")
            return []
    
    def _analyze_opportunities(self, entity_id: str) -> List[Dict[str, Any]]:
        """Анализ возможностей для AI сущности"""
        try:
            opportunities = []
            
            if entity_id not in self.ai_memories:
                return opportunities
            
            current_time = time.time()
            
            for target_id, memory in self.ai_memories[entity_id].items():
                # Проверяем, не устарело ли воспоминание
                if current_time - memory.last_seen > memory.threat_level * 300.0:
                    continue
                
                # Рассчитываем ценность цели
                value = 1.0 / memory.threat_level  # Чем слабее цель, тем ценнее
                if memory.damage_dealt > 0:
                    value *= 1.2
                
                opportunities.append({
                    'entity_id': target_id,
                    'value': value,
                    'position': memory.last_position,
                    'last_seen': memory.last_seen
                })
            
            # Сортируем по ценности
            opportunities.sort(key=lambda x: x['value'], reverse=True)
            return opportunities
            
        except Exception as e:
            logger.error(f"Ошибка анализа возможностей для {entity_id}: {e}")
            return []
    
    def _execute_ai_decision(self, entity_id: str, decision: AIDecision) -> bool:
        """Выполнение решения AI"""
        try:
            if entity_id not in self.ai_entities:
                return False
            
            entity_data = self.ai_entities[entity_id]
            
            if decision.decision_type == "engage":
                return self._execute_engage_action(entity_id, entity_data, decision)
            elif decision.decision_type == "hunt":
                return self._execute_hunt_action(entity_id, entity_data, decision)
            elif decision.decision_type == "patrol":
                return self._execute_patrol_action(entity_id, entity_data, decision)
            elif decision.decision_type == "combat":
                return self._execute_combat_action(entity_id, entity_data, decision)
            elif decision.decision_type == "retreat":
                return self._execute_retreat_action(entity_id, entity_data, decision)
            elif decision.decision_type == "return_to_idle":
                return self._execute_return_to_idle_action(entity_id, entity_data, decision)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Ошибка выполнения решения AI для {entity_id}: {e}")
            return False
    
    def _execute_engage_action(self, entity_id: str, entity_data: Dict[str, Any], decision: AIDecision) -> bool:
        """Выполнение действия атаки"""
        try:
            target_id = decision.target_entity
            if not target_id:
                return False
            
            # Переходим в состояние боя
            entity_data['state'] = AIState.IN_COMBAT
            entity_data['current_target'] = target_id
            
            # Двигаемся к цели
            if target_id in self.ai_memories[entity_id]:
                target_position = self.ai_memories[entity_id][target_id].last_position
                self._move_to_position(entity_id, target_position)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выполнения действия атаки для {entity_id}: {e}")
            return False
    
    def _execute_hunt_action(self, entity_id: str, entity_data: Dict[str, Any], decision: AIDecision) -> bool:
        """Выполнение действия охоты"""
        try:
            target_id = decision.target_entity
            if not target_id:
                return False
            
            # Двигаемся к цели
            if target_id in self.ai_memories[entity_id]:
                target_position = self.ai_memories[entity_id][target_id].last_position
                self._move_to_position(entity_id, target_position)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выполнения действия охоты для {entity_id}: {e}")
            return False
    
    def _execute_patrol_action(self, entity_id: str, entity_data: Dict[str, Any], decision: AIDecision) -> bool:
        """Выполнение действия патрулирования"""
        try:
            if not entity_data['patrol_points']:
                return False
            
            # Двигаемся к следующей точке патрулирования
            next_point = entity_data['patrol_points'][0]
            self._move_to_position(entity_id, next_point)
            
            # Перемещаем точку в конец списка
            entity_data['patrol_points'] = entity_data['patrol_points'][1:] + [next_point]
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выполнения действия патрулирования для {entity_id}: {e}")
            return False
    
    def _execute_combat_action(self, entity_id: str, entity_data: Dict[str, Any], decision: AIDecision) -> bool:
        """Выполнение боевого действия"""
        try:
            target_id = decision.target_entity
            if not target_id:
                return False
            
            # Выполняем атаку
            # Здесь должна быть интеграция с системой боя
            logger.debug(f"AI {entity_id} атакует {target_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выполнения боевого действия для {entity_id}: {e}")
            return False
    
    def _execute_retreat_action(self, entity_id: str, entity_data: Dict[str, Any], decision: AIDecision) -> bool:
        """Выполнение действия отступления"""
        try:
            # Двигаемся в противоположном направлении от текущей позиции
            current_pos = entity_data['position']
            retreat_direction = (-current_pos[0], -current_pos[1], -current_pos[2])
            retreat_position = tuple(p * 10.0 for p in retreat_direction)
            
            self._move_to_position(entity_id, retreat_position)
            
            # Через некоторое время возвращаемся к обычному состоянию
            if random.random() < 0.1:  # 10% шанс
                entity_data['state'] = AIState.IDLE
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выполнения действия отступления для {entity_id}: {e}")
            return False
    
    def _execute_return_to_idle_action(self, entity_id: str, entity_data: Dict[str, Any], decision: AIDecision) -> bool:
        """Выполнение действия возврата к обычному состоянию"""
        try:
            entity_data['state'] = AIState.IDLE
            entity_data['current_target'] = None
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выполнения действия возврата к обычному состоянию для {entity_id}: {e}")
            return False
    
    def _update_ai_behavior(self, entity_id: str, entity_data: Dict[str, Any], delta_time: float) -> None:
        """Обновление поведения AI"""
        try:
            config = entity_data['config']
            
            # Обновляем позицию
            if entity_data['state'] == AIState.IDLE and config.behavior == AIBehavior.PATROL:
                # Простое патрулирование
                pass
            
            # Проверяем условия отступления
            if entity_data['state'] == AIState.IN_COMBAT:
                # Проверяем здоровье и другие факторы
                pass
                
        except Exception as e:
            logger.error(f"Ошибка обновления поведения AI для {entity_id}: {e}")
    
    def _move_to_position(self, entity_id: str, target_position: Tuple[float, float, float]) -> None:
        """Движение AI к позиции"""
        try:
            if entity_id not in self.ai_entities:
                return
            
            entity_data = self.ai_entities[entity_id]
            current_pos = entity_data['position']
            
            # Простое движение - линейная интерполяция
            # В реальной игре здесь должна быть система навигации
            entity_data['position'] = target_position
            
        except Exception as e:
            logger.error(f"Ошибка движения AI {entity_id}: {e}")
    
    def _generate_patrol_points(self, entity_id: str, center_position: Tuple[float, float, float], radius: float) -> None:
        """Генерация точек патрулирования"""
        try:
            if entity_id not in self.ai_entities:
                return
            
            patrol_points = []
            num_points = random.randint(3, 6)
            
            for i in range(num_points):
                angle = (i / num_points) * 2 * math.pi
                distance = random.uniform(radius * 0.5, radius)
                
                x = center_position[0] + distance * math.cos(angle)
                z = center_position[2] + distance * math.sin(angle)
                y = center_position[1]  # Высота остается той же
                
                patrol_points.append((x, y, z))
            
            self.ai_entities[entity_id]['patrol_points'] = patrol_points
            
        except Exception as e:
            logger.error(f"Ошибка генерации точек патрулирования для {entity_id}: {e}")
    
    def _follow_leader(self, follower_id: str, follower_data: Dict[str, Any], leader_id: str, leader_data: Dict[str, Any]) -> None:
        """Следование за лидером группы"""
        try:
            leader_pos = leader_data['position']
            follower_pos = follower_data['position']
            
            # Двигаемся к лидеру, но с небольшим отступом
            offset = 2.0
            target_pos = (
                leader_pos[0] + random.uniform(-offset, offset),
                leader_pos[1],
                leader_pos[2] + random.uniform(-offset, offset)
            )
            
            self._move_to_position(follower_id, target_pos)
            
        except Exception as e:
            logger.error(f"Ошибка следования за лидером для {follower_id}: {e}")
    
    def create_ai_group(self, group_id: str, member_ids: List[str]) -> bool:
        """Создание группы AI"""
        try:
            if group_id in self.ai_groups:
                logger.warning(f"Группа AI {group_id} уже существует")
                return False
            
            # Проверяем, что все участники существуют
            valid_members = [mid for mid in member_ids if mid in self.ai_entities]
            
            if len(valid_members) < 2:
                logger.warning(f"Недостаточно участников для группы {group_id}")
                return False
            
            self.ai_groups[group_id] = valid_members
            
            # Устанавливаем групповую координацию
            for member_id in valid_members:
                if member_id in self.ai_entities:
                    self.ai_entities[member_id]['group_id'] = group_id
            
            logger.info(f"Группа AI {group_id} создана с {len(valid_members)} участниками")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания группы AI {group_id}: {e}")
            return False
    
    def destroy_ai_group(self, group_id: str) -> bool:
        """Уничтожение группы AI"""
        try:
            if group_id not in self.ai_groups:
                return False
            
            # Убираем групповую координацию
            for member_id in self.ai_groups[group_id]:
                if member_id in self.ai_entities:
                    self.ai_entities[member_id]['group_id'] = None
            
            del self.ai_groups[group_id]
            
            logger.info(f"Группа AI {group_id} уничтожена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения группы AI {group_id}: {e}")
            return False
    
    def get_ai_entity_info(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации об AI сущности"""
        try:
            if entity_id not in self.ai_entities:
                return None
            
            entity_data = self.ai_entities[entity_id]
            config = entity_data['config']
            
            return {
                'id': entity_id,
                'behavior': config.behavior.value,
                'difficulty': config.difficulty.value,
                'state': entity_data['state'].value,
                'position': entity_data['position'],
                'current_target': entity_data['current_target'],
                'group_id': entity_data['group_id'],
                'patrol_points_count': len(entity_data['patrol_points']),
                'memories_count': len(self.ai_memories.get(entity_id, {})),
                'pending_decisions': len(self.ai_decisions.get(entity_id, []))
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации об AI сущности {entity_id}: {e}")
            return None
    
    def update_ai_config(self, entity_id: str, new_config: AIConfig) -> bool:
        """Обновление конфигурации AI"""
        try:
            if entity_id not in self.ai_entities:
                return False
            
            self.ai_configs[entity_id] = new_config
            self.ai_entities[entity_id]['config'] = new_config
            
            logger.info(f"Конфигурация AI для {entity_id} обновлена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления конфигурации AI для {entity_id}: {e}")
            return False
