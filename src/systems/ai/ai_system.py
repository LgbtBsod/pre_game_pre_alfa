#!/usr/bin/env python3
"""
Система AI - базовая система искусственного интеллекта
"""

import logging
import time
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from ...core.interfaces import ISystem, SystemPriority, SystemState, IAIEntity

logger = logging.getLogger(__name__)

class AIState(Enum):
    """Состояния AI"""
    IDLE = "idle"
    THINKING = "thinking"
    DECIDING = "deciding"
    ACTING = "acting"
    LEARNING = "learning"
    SLEEPING = "sleeping"

class AIType(Enum):
    """Типы AI"""
    PASSIVE = "passive"
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    SUPPORT = "support"
    EXPLORER = "explorer"
    TRADER = "trader"
    CRAFTER = "crafter"

@dataclass
class AIDecision:
    """Решение AI"""
    decision_id: str
    entity_id: str
    decision_type: str
    confidence: float
    reasoning: str
    actions: List[Dict[str, Any]]
    timestamp: float
    executed: bool = False

@dataclass
class AIMemory:
    """Память AI"""
    memory_id: str
    entity_id: str
    memory_type: str
    content: Dict[str, Any]
    importance: float
    timestamp: float
    last_accessed: float
    access_count: int = 0

@dataclass
class AIEmotion:
    """Эмоция AI"""
    emotion_type: str
    intensity: float
    duration: float
    source: str
    timestamp: float

class AIEntity(IAIEntity):
    """AI сущность"""
    
    def __init__(self, entity_id: str, ai_type: AIType, personality: Dict[str, Any] = None):
        self.entity_id = entity_id
        self.ai_type = ai_type
        self.personality = personality or self._generate_personality()
        
        # Состояние
        self.current_state = AIState.IDLE
        self.health = 100.0
        self.energy = 100.0
        self.mood = 0.5  # -1.0 до 1.0
        
        # Память и опыт
        self.memories: List[AIMemory] = []
        self.decisions: List[AIDecision] = []
        self.emotions: List[AIEmotion] = []
        
        # Навыки и способности
        self.skills: Dict[str, float] = {}
        self.knowledge: Dict[str, Any] = {}
        
        # Цели и мотивации
        self.goals: List[Dict[str, Any]] = []
        self.motivations: Dict[str, float] = {}
        
        # Взаимодействия
        self.relationships: Dict[str, Dict[str, Any]] = {}
        self.recent_actions: List[Dict[str, Any]] = []
        
        logger.info(f"AI Entity создана: {entity_id} ({ai_type.value})")
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Принятие решения"""
        try:
            # Анализируем контекст
            analysis = self._analyze_context(context)
            
            # Генерируем варианты действий
            options = self._generate_action_options(analysis)
            
            # Оцениваем варианты
            best_option = self._evaluate_options(options, context)
            
            # Создаем решение
            decision = AIDecision(
                decision_id=f"decision_{len(self.decisions)}",
                entity_id=self.entity_id,
                decision_type=best_option['type'],
                confidence=best_option['confidence'],
                reasoning=best_option['reasoning'],
                actions=best_option['actions'],
                timestamp=time.time()
            )
            
            self.decisions.append(decision)
            
            # Обновляем состояние
            self.current_state = AIState.DECIDING
            
            return {
                'decision_id': decision.decision_id,
                'action_type': best_option['type'],
                'confidence': best_option['confidence'],
                'reasoning': best_option['reasoning'],
                'actions': best_option['actions']
            }
            
        except Exception as e:
            logger.error(f"Ошибка принятия решения для {self.entity_id}: {e}")
            return {'error': str(e)}
    
    def update_emotion(self, stimulus: Dict[str, Any]) -> bool:
        """Обновление эмоций"""
        try:
            emotion_type = stimulus.get('emotion_type', 'neutral')
            intensity = stimulus.get('intensity', 0.1)
            source = stimulus.get('source', 'unknown')
            
            # Создаем новую эмоцию
            emotion = AIEmotion(
                emotion_type=emotion_type,
                intensity=intensity,
                duration=stimulus.get('duration', 10.0),
                source=source,
                timestamp=time.time()
            )
            
            self.emotions.append(emotion)
            
            # Обновляем настроение
            emotion_impact = self._calculate_emotion_impact(emotion)
            self.mood = max(-1.0, min(1.0, self.mood + emotion_impact))
            
            # Обновляем энергию
            energy_change = self._calculate_energy_change(emotion)
            self.energy = max(0.0, min(100.0, self.energy + energy_change))
            
            logger.debug(f"Эмоция обновлена для {self.entity_id}: {emotion_type} (интенсивность: {intensity})")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления эмоции для {self.entity_id}: {e}")
            return False
    
    def learn(self, experience: Dict[str, Any]) -> bool:
        """Обучение на опыте"""
        try:
            # Создаем память об опыте
            memory = AIMemory(
                memory_id=f"memory_{len(self.memories)}",
                entity_id=self.entity_id,
                memory_type=experience.get('type', 'general'),
                content=experience,
                importance=experience.get('importance', 0.5),
                timestamp=time.time(),
                last_accessed=time.time()
            )
            
            self.memories.append(memory)
            
            # Обновляем навыки
            if 'skill_gain' in experience:
                skill_name = experience['skill_gain']['skill']
                skill_value = experience['skill_gain']['value']
                current_skill = self.skills.get(skill_name, 0.0)
                self.skills[skill_name] = min(100.0, current_skill + skill_value)
            
            # Обновляем знания
            if 'knowledge' in experience:
                knowledge_key = experience['knowledge']['key']
                knowledge_value = experience['knowledge']['value']
                self.knowledge[knowledge_key] = knowledge_value
            
            # Обновляем отношения
            if 'relationship_change' in experience:
                target_id = experience['relationship_change']['target']
                change_value = experience['relationship_change']['value']
                if target_id not in self.relationships:
                    self.relationships[target_id] = {'trust': 0.0, 'respect': 0.0, 'fear': 0.0}
                
                for key, value in change_value.items():
                    if key in self.relationships[target_id]:
                        self.relationships[target_id][key] = max(-1.0, min(1.0, 
                            self.relationships[target_id][key] + value))
            
            logger.debug(f"Опыт усвоен для {self.entity_id}: {experience.get('type', 'general')}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обучения для {self.entity_id}: {e}")
            return False
    
    def get_memory(self) -> Dict[str, Any]:
        """Получение памяти"""
        try:
            # Сортируем память по важности и времени
            sorted_memories = sorted(self.memories, 
                                   key=lambda m: (m.importance, m.last_accessed), 
                                   reverse=True)
            
            # Возвращаем основные данные
            return {
                'entity_id': self.entity_id,
                'ai_type': self.ai_type.value,
                'current_state': self.current_state.value,
                'health': self.health,
                'energy': self.energy,
                'mood': self.mood,
                'memories_count': len(self.memories),
                'decisions_count': len(self.decisions),
                'emotions_count': len(self.emotions),
                'skills': self.skills,
                'knowledge_keys': list(self.knowledge.keys()),
                'goals_count': len(self.goals),
                'relationships_count': len(self.relationships),
                'recent_memories': [asdict(m) for m in sorted_memories[:5]],
                'recent_decisions': [asdict(d) for d in self.decisions[-5:]],
                'current_emotions': [asdict(e) for e in self.emotions[-3:]]
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения памяти для {self.entity_id}: {e}")
            return {'error': str(e)}
    
    def _generate_personality(self) -> Dict[str, Any]:
        """Генерация личности"""
        import random
        
        personality_traits = {
            'openness': random.uniform(0.3, 0.9),
            'conscientiousness': random.uniform(0.3, 0.9),
            'extraversion': random.uniform(0.2, 0.8),
            'agreeableness': random.uniform(0.3, 0.9),
            'neuroticism': random.uniform(0.1, 0.7),
            'curiosity': random.uniform(0.4, 0.9),
            'caution': random.uniform(0.2, 0.8),
            'social_need': random.uniform(0.1, 0.9),
            'achievement_drive': random.uniform(0.3, 0.9)
        }
        
        return personality_traits
    
    def _analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ контекста"""
        analysis = {
            'threats': [],
            'opportunities': [],
            'resources': [],
            'entities': [],
            'environment': {},
            'risk_level': 0.0
        }
        
        # Анализируем угрозы
        if 'enemies' in context:
            for enemy in context['enemies']:
                threat_level = self._assess_threat(enemy)
                if threat_level > 0.5:
                    analysis['threats'].append({
                        'entity': enemy,
                        'threat_level': threat_level
                    })
        
        # Анализируем возможности
        if 'resources' in context:
            for resource in context['resources']:
                opportunity_value = self._assess_opportunity(resource)
                if opportunity_value > 0.3:
                    analysis['opportunities'].append({
                        'resource': resource,
                        'value': opportunity_value
                    })
        
        # Оцениваем общий уровень риска
        analysis['risk_level'] = len(analysis['threats']) * 0.3 + (1.0 - self.health / 100.0) * 0.4
        
        return analysis
    
    def _generate_action_options(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Генерация вариантов действий"""
        options = []
        
        # Действия в зависимости от угроз
        if analysis['threats']:
            options.append({
                'type': 'defend',
                'confidence': 0.8,
                'reasoning': 'Обнаружены угрозы, необходимо защищаться',
                'actions': [{'action': 'defend', 'target': 'self'}]
            })
            
            if self.ai_type == AIType.AGGRESSIVE:
                options.append({
                    'type': 'attack',
                    'confidence': 0.6,
                    'reasoning': 'Агрессивный ответ на угрозу',
                    'actions': [{'action': 'attack', 'target': 'nearest_threat'}]
                })
        
        # Действия в зависимости от возможностей
        if analysis['opportunities']:
            options.append({
                'type': 'gather',
                'confidence': 0.7,
                'reasoning': 'Обнаружены ценные ресурсы',
                'actions': [{'action': 'gather', 'target': 'nearest_resource'}]
            })
        
        # Действия в зависимости от состояния
        if self.health < 30.0:
            options.append({
                'type': 'heal',
                'confidence': 0.9,
                'reasoning': 'Критически низкое здоровье',
                'actions': [{'action': 'heal', 'target': 'self'}]
            })
        
        if self.energy < 20.0:
            options.append({
                'type': 'rest',
                'confidence': 0.8,
                'reasoning': 'Низкая энергия, необходим отдых',
                'actions': [{'action': 'rest', 'target': 'self'}]
            })
        
        # Действия по умолчанию
        if not options:
            options.append({
                'type': 'explore',
                'confidence': 0.5,
                'reasoning': 'Нет явных угроз или возможностей',
                'actions': [{'action': 'explore', 'direction': 'random'}]
            })
        
        return options
    
    def _evaluate_options(self, options: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Оценка вариантов действий"""
        best_option = None
        best_score = -1.0
        
        for option in options:
            score = self._calculate_option_score(option, context)
            if score > best_score:
                best_score = score
                best_option = option
        
        if best_option:
            best_option['confidence'] = min(1.0, best_score)
        
        return best_option or options[0]
    
    def _calculate_option_score(self, option: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Расчет оценки варианта действия"""
        score = 0.0
        
        # Базовая оценка
        score += option.get('confidence', 0.5) * 0.3
        
        # Учитываем личность
        if option['type'] == 'attack' and self.personality.get('aggressiveness', 0.5) > 0.7:
            score += 0.2
        
        if option['type'] == 'explore' and self.personality.get('curiosity', 0.5) > 0.7:
            score += 0.2
        
        # Учитываем состояние
        if option['type'] == 'heal' and self.health < 50.0:
            score += 0.3
        
        if option['type'] == 'rest' and self.energy < 30.0:
            score += 0.3
        
        # Учитываем контекст
        if 'threats' in context and len(context['threats']) > 0:
            if option['type'] == 'defend':
                score += 0.4
        
        return score
    
    def _assess_threat(self, enemy: Dict[str, Any]) -> float:
        """Оценка угрозы"""
        threat_level = 0.0
        
        # Учитываем здоровье врага
        enemy_health = enemy.get('health', 100.0)
        if enemy_health > self.health:
            threat_level += 0.3
        
        # Учитываем атаку врага
        enemy_attack = enemy.get('attack', 10.0)
        if enemy_attack > 20.0:
            threat_level += 0.3
        
        # Учитываем расстояние
        distance = enemy.get('distance', 10.0)
        if distance < 5.0:
            threat_level += 0.4
        
        return min(1.0, threat_level)
    
    def _assess_opportunity(self, resource: Dict[str, Any]) -> float:
        """Оценка возможности"""
        opportunity_value = 0.0
        
        # Учитываем ценность ресурса
        resource_value = resource.get('value', 1.0)
        opportunity_value += resource_value * 0.3
        
        # Учитываем расстояние
        distance = resource.get('distance', 10.0)
        if distance < 5.0:
            opportunity_value += 0.3
        
        # Учитываем потребности
        if resource.get('type') == 'health' and self.health < 70.0:
            opportunity_value += 0.4
        
        if resource.get('type') == 'energy' and self.energy < 60.0:
            opportunity_value += 0.3
        
        return min(1.0, opportunity_value)
    
    def _calculate_emotion_impact(self, emotion: AIEmotion) -> float:
        """Расчет влияния эмоции на настроение"""
        base_impact = emotion.intensity * 0.5
        
        # Модификаторы в зависимости от типа эмоции
        emotion_modifiers = {
            'joy': 1.0,
            'sadness': -1.0,
            'anger': -0.5,
            'fear': -0.7,
            'surprise': 0.3,
            'disgust': -0.8,
            'trust': 0.6,
            'anticipation': 0.4
        }
        
        modifier = emotion_modifiers.get(emotion.emotion_type, 0.0)
        return base_impact * modifier
    
    def _calculate_energy_change(self, emotion: AIEmotion) -> float:
        """Расчет изменения энергии от эмоции"""
        energy_impact = 0.0
        
        # Энергозатратные эмоции
        if emotion.emotion_type in ['anger', 'fear', 'surprise']:
            energy_impact = -emotion.intensity * 0.1
        
        # Восстанавливающие эмоции
        elif emotion.emotion_type in ['joy', 'trust']:
            energy_impact = emotion.intensity * 0.05
        
        return energy_impact

class AISystem(ISystem):
    """Базовая система искусственного интеллекта"""
    
    def __init__(self):
        self._system_name = "ai"
        self._system_priority = SystemPriority.HIGH
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # AI сущности
        self.ai_entities: Dict[str, AIEntity] = {}
        
        # Настройки AI
        self.max_entities = 100
        self.thinking_interval = 1.0  # секунды
        self.memory_limit = 1000
        
        # Статистика
        self.ai_stats = {
            'entities_count': 0,
            'decisions_made': 0,
            'emotions_processed': 0,
            'learning_events': 0,
            'update_time': 0.0
        }
        
        # Время последнего обновления
        self.last_update_time = time.time()
        
        logger.info("Базовая AI система инициализирована")
    
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
            logger.info("Инициализация базовой AI системы...")
            
            # Создаем базовые AI сущности
            self._create_base_ai_entities()
            
            # Настраиваем обработчики событий
            self._setup_event_handlers()
            
            self._system_state = SystemState.READY
            logger.info("Базовая AI система успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации базовой AI системы: {e}")
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
            
            # Обрабатываем события
            self._process_ai_events()
            
            # Очищаем старые данные
            self._cleanup_old_data()
            
            # Обновляем статистику
            self.ai_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления базовой AI системы: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы AI"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Базовая AI система приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки базовой AI системы: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы AI"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Базовая AI система возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления базовой AI системы: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы AI"""
        try:
            logger.info("Очистка базовой AI системы...")
            
            # Сохраняем память AI
            self._save_ai_memory()
            
            # Очищаем AI сущности
            self.ai_entities.clear()
            
            # Сбрасываем статистику
            self.ai_stats = {
                'entities_count': 0,
                'decisions_made': 0,
                'emotions_processed': 0,
                'learning_events': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Базовая AI система очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки базовой AI системы: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'ai_entities_count': len(self.ai_entities),
            'max_entities': self.max_entities,
            'thinking_interval': self.thinking_interval,
            'memory_limit': self.memory_limit,
            'stats': self.ai_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "ai_entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "ai_entity_destroyed":
                return self._handle_entity_destroyed(event_data)
            elif event_type == "ai_stimulus":
                return self._handle_stimulus(event_data)
            elif event_type == "ai_learning":
                return self._handle_learning(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def create_ai_entity(self, entity_id: str, ai_type: str) -> IAIEntity:
        """Создание AI сущности"""
        try:
            if entity_id in self.ai_entities:
                logger.warning(f"AI сущность {entity_id} уже существует")
                return self.ai_entities[entity_id]
            
            if len(self.ai_entities) >= self.max_entities:
                logger.warning(f"Достигнут лимит AI сущностей ({self.max_entities})")
                return None
            
            # Создаем AI сущность
            ai_type_enum = AIType(ai_type)
            ai_entity = AIEntity(entity_id, ai_type_enum)
            
            self.ai_entities[entity_id] = ai_entity
            self.ai_stats['entities_count'] = len(self.ai_entities)
            
            logger.info(f"Создана AI сущность: {entity_id} ({ai_type})")
            return ai_entity
            
        except Exception as e:
            logger.error(f"Ошибка создания AI сущности {entity_id}: {e}")
            return None
    
    def update_ai_entities(self, delta_time: float) -> bool:
        """Обновление AI сущностей"""
        try:
            current_time = time.time()
            
            for entity_id, ai_entity in self.ai_entities.items():
                try:
                    # Проверяем, нужно ли обновлять сущность
                    if current_time - self.last_update_time >= self.thinking_interval:
                        # Обновляем состояние
                        self._update_entity_state(ai_entity, delta_time)
                        
                        # Принимаем решения
                        context = self._get_entity_context(ai_entity)
                        if context:
                            decision = ai_entity.make_decision(context)
                            if 'decision_id' in decision:
                                self.ai_stats['decisions_made'] += 1
                    
                except Exception as e:
                    logger.error(f"Ошибка обновления AI сущности {entity_id}: {e}")
            
            self.last_update_time = current_time
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления AI сущностей: {e}")
            return False
    
    def get_ai_entity(self, entity_id: str) -> Optional[IAIEntity]:
        """Получение AI сущности"""
        return self.ai_entities.get(entity_id)
    
    def destroy_ai_entity(self, entity_id: str) -> bool:
        """Уничтожение AI сущности"""
        try:
            if entity_id not in self.ai_entities:
                return False
            
            # Сохраняем память перед уничтожением
            ai_entity = self.ai_entities[entity_id]
            self._save_entity_memory(ai_entity)
            
            # Удаляем сущность
            del self.ai_entities[entity_id]
            self.ai_stats['entities_count'] = len(self.ai_entities)
            
            logger.info(f"AI сущность {entity_id} уничтожена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения AI сущности {entity_id}: {e}")
            return False
    
    def _create_base_ai_entities(self) -> None:
        """Создание базовых AI сущностей"""
        try:
            # Создаем несколько базовых AI сущностей для демонстрации
            base_entities = [
                ('player_1', 'passive'),
                ('npc_1', 'aggressive'),
                ('npc_2', 'defensive'),
                ('npc_3', 'support')
            ]
            
            for entity_id, ai_type in base_entities:
                self.create_ai_entity(entity_id, ai_type)
            
            logger.debug("Базовые AI сущности созданы")
            
        except Exception as e:
            logger.warning(f"Не удалось создать базовые AI сущности: {e}")
    
    def _setup_event_handlers(self) -> None:
        """Настройка обработчиков событий"""
        try:
            # Здесь можно добавить специфичные для AI обработчики событий
            pass
        except Exception as e:
            logger.warning(f"Не удалось настроить обработчики событий AI: {e}")
    
    def _update_ai_entities(self, delta_time: float) -> None:
        """Обновление AI сущностей"""
        try:
            # Обновляем каждую AI сущность
            for ai_entity in self.ai_entities.values():
                # Обновляем эмоции
                self._update_entity_emotions(ai_entity, delta_time)
                
                # Обновляем память
                self._update_entity_memory(ai_entity, delta_time)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления AI сущностей: {e}")
    
    def _process_ai_events(self) -> None:
        """Обработка AI событий"""
        try:
            # Здесь должна быть логика обработки специфичных для AI событий
            pass
        except Exception as e:
            logger.warning(f"Ошибка обработки AI событий: {e}")
    
    def _cleanup_old_data(self) -> None:
        """Очистка старых данных"""
        try:
            current_time = time.time()
            
            for ai_entity in self.ai_entities.values():
                # Очищаем старые эмоции
                ai_entity.emotions = [e for e in ai_entity.emotions 
                                    if current_time - e.timestamp < 300.0]  # 5 минут
                
                # Очищаем старые решения
                ai_entity.decisions = [d for d in ai_entity.decisions 
                                     if current_time - d.timestamp < 600.0]  # 10 минут
                
                # Ограничиваем количество воспоминаний
                if len(ai_entity.memories) > self.memory_limit:
                    # Оставляем самые важные
                    ai_entity.memories.sort(key=lambda m: m.importance, reverse=True)
                    ai_entity.memories = ai_entity.memories[:self.memory_limit]
                    
        except Exception as e:
            logger.warning(f"Ошибка очистки старых данных: {e}")
    
    def _update_entity_state(self, ai_entity: AIEntity, delta_time: float) -> None:
        """Обновление состояния AI сущности"""
        try:
            # Восстанавливаем энергию
            if ai_entity.current_state == AIState.SLEEPING:
                ai_entity.energy = min(100.0, ai_entity.energy + delta_time * 5.0)
            
            # Восстанавливаем здоровье
            if ai_entity.energy > 80.0 and ai_entity.health < 100.0:
                ai_entity.health = min(100.0, ai_entity.health + delta_time * 2.0)
            
            # Нормализуем настроение
            if abs(ai_entity.mood) > 0.1:
                ai_entity.mood *= 0.99  # Медленно возвращаемся к нейтральному
            
        except Exception as e:
            logger.warning(f"Ошибка обновления состояния AI сущности: {e}")
    
    def _get_entity_context(self, ai_entity: AIEntity) -> Optional[Dict[str, Any]]:
        """Получение контекста для AI сущности"""
        try:
            # Здесь должна быть логика получения контекста из игрового мира
            # Пока возвращаем базовый контекст
            context = {
                'health': ai_entity.health,
                'energy': ai_entity.energy,
                'mood': ai_entity.mood,
                'position': (0, 0, 0),  # Должно получаться из игрового мира
                'nearby_entities': [],
                'nearby_resources': [],
                'threats': [],
                'opportunities': []
            }
            
            return context
            
        except Exception as e:
            logger.warning(f"Ошибка получения контекста для AI сущности: {e}")
            return None
    
    def _update_entity_emotions(self, ai_entity: AIEntity, delta_time: float) -> None:
        """Обновление эмоций AI сущности"""
        try:
            current_time = time.time()
            
            # Уменьшаем интенсивность эмоций со временем
            for emotion in ai_entity.emotions:
                if current_time - emotion.timestamp > emotion.duration:
                    emotion.intensity *= 0.95
                
                # Удаляем очень слабые эмоции
                if emotion.intensity < 0.01:
                    ai_entity.emotions.remove(emotion)
                    
        except Exception as e:
            logger.warning(f"Ошибка обновления эмоций AI сущности: {e}")
    
    def _update_entity_memory(self, ai_entity: AIEntity, delta_time: float) -> None:
        """Обновление памяти AI сущности"""
        try:
            current_time = time.time()
            
            # Обновляем доступ к памяти
            for memory in ai_entity.memories:
                if current_time - memory.last_accessed > 60.0:  # 1 минута
                    memory.access_count += 1
                    memory.last_accessed = current_time
                    
        except Exception as e:
            logger.warning(f"Ошибка обновления памяти AI сущности: {e}")
    
    def _save_ai_memory(self) -> None:
        """Сохранение памяти AI"""
        try:
            # Создаем директорию для сохранений если её нет
            os.makedirs('saves/ai_memory', exist_ok=True)
            
            # Сохраняем память каждой AI сущности
            for entity_id, ai_entity in self.ai_entities.items():
                self._save_entity_memory(ai_entity)
                
            logger.info("Память AI сохранена в final_ai_memory")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения памяти AI: {e}")
    
    def _save_entity_memory(self, ai_entity: AIEntity) -> None:
        """Сохранение памяти конкретной AI сущности"""
        try:
            memory_data = ai_entity.get_memory()
            
            # Сохраняем в файл
            filename = f"saves/ai_memory/final_ai_memory_{ai_entity.entity_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Ошибка сохранения памяти AI сущности {ai_entity.entity_id}: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания AI сущности"""
        try:
            entity_id = event_data.get('entity_id')
            ai_type = event_data.get('ai_type', 'passive')
            
            if entity_id:
                return self.create_ai_entity(entity_id, ai_type) is not None
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания AI сущности: {e}")
            return False
    
    def _handle_entity_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения AI сущности"""
        try:
            entity_id = event_data.get('entity_id')
            if entity_id:
                return self.destroy_ai_entity(entity_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события уничтожения AI сущности: {e}")
            return False
    
    def _handle_stimulus(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события стимула"""
        try:
            entity_id = event_data.get('entity_id')
            if entity_id and entity_id in self.ai_entities:
                ai_entity = self.ai_entities[entity_id]
                return ai_entity.update_emotion(event_data)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события стимула: {e}")
            return False
    
    def _handle_learning(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события обучения"""
        try:
            entity_id = event_data.get('entity_id')
            if entity_id and entity_id in self.ai_entities:
                ai_entity = self.ai_entities[entity_id]
                success = ai_entity.learn(event_data)
                if success:
                    self.ai_stats['learning_events'] += 1
                return success
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события обучения: {e}")
            return False
