#!/usr/bin/env python3
"""
AI Entity - Базовая сущность для всех ИИ агентов
Включает систему памяти поколений и разную скорость обучения
"""

import logging
import json
import os
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import random
import math

from ...entities.base_entity import BaseEntity, EntityType as BaseEntityType

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Типы памяти"""
    COMBAT = "combat"
    MOVEMENT = "movement"
    SKILL_USAGE = "skill_usage"
    ITEM_USAGE = "item_usage"
    ENVIRONMENT = "environment"
    SOCIAL = "social"

@dataclass
class MemoryEntry:
    """Запись в памяти"""
    memory_type: MemoryType
    timestamp: float
    context: Dict[str, Any]
    action: str
    outcome: Dict[str, Any]
    success: bool
    learning_value: float  # Ценность для обучения (0.0 - 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        data['memory_type'] = MemoryType(data['memory_type'])
        return cls(**data)

@dataclass
class GenerationMemory:
    """Память поколения"""
    generation_id: int
    entity_id: str
    entity_type: BaseEntityType
    start_time: float
    end_time: Optional[float]
    total_experience: float
    memories: List[MemoryEntry]
    final_stats: Dict[str, Any]
    cause_of_death: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['entity_type'] = self.entity_type.value
        data['memories'] = [mem.to_dict() for mem in self.memories]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GenerationMemory':
        data['entity_type'] = BaseEntityType(data['entity_type'])
        data['memories'] = [MemoryEntry.from_dict(mem) for mem in data['memories']]
        return cls(**data)

class AIEntity(BaseEntity):
    """Базовая сущность для всех ИИ агентов - наследуется от BaseEntity"""
    
    def __init__(self, entity_id: str, entity_type: BaseEntityType, save_slot: str = "default"):
        # Инициализируем базовую сущность
        super().__init__(entity_id, entity_type)
        
        # Сохраняем слот для сохранения
        self.save_slot = save_slot
        
        # Параметры обучения
        self.learning_rate = self._get_learning_rate()
        self.memory_capacity = self._get_memory_capacity()
        self.generation_memory_capacity = self._get_generation_memory_capacity()
        
        # Текущая память поколений
        self.generation_memories: List[GenerationMemory] = []
        
        # Текущее поколение
        self.current_generation = 0
        self.generation_start_time = time.time()
        self.generation_experience = 0.0
        
        # Статистика
        self.stats = {
            'total_generations': 0,
            'total_experience': 0.0,
            'total_memories': 0,
            'successful_actions': 0,
            'failed_actions': 0,
            'combat_wins': 0,
            'combat_losses': 0,
            'skills_learned': 0,
            'items_used': 0
        }
        
        # Загружаем существующую память
        self._load_memory()
        
        logger.info(f"AI Entity создана: {entity_id} ({entity_type.value})")
    
    def _get_learning_rate(self) -> float:
        """Получение скорости обучения в зависимости от типа сущности"""
        if self.entity_type == BaseEntityType.PLAYER:
            return 0.8  # Игрок учится быстро
        elif self.entity_type == BaseEntityType.ENEMY:
            return 0.3  # Враги учатся медленно, но имеют общую память
        else:  # NPC
            return 0.5  # Средняя скорость обучения
    
    def _get_memory_capacity(self) -> int:
        """Получение емкости памяти"""
        if self.entity_type == BaseEntityType.PLAYER:
            return 1000  # Большая память для игрока
        elif self.entity_type == BaseEntityType.ENEMY:
            return 500   # Средняя память для врагов
        else:  # NPC
            return 300   # Небольшая память для NPC
    
    def _get_generation_memory_capacity(self) -> int:
        """Получение емкости памяти поколений"""
        if self.entity_type == BaseEntityType.PLAYER:
            return 50   # Много поколений для игрока
        elif self.entity_type == BaseEntityType.ENEMY:
            return 100  # Очень много поколений для врагов (общая память)
        else:  # NPC
            return 20   # Несколько поколений для NPC
    
    def add_memory(self, memory_type: MemoryType, context: Dict[str, Any], 
                   action: str, outcome: Dict[str, Any], success: bool):
        """Добавление новой записи в память"""
        # Вычисляем ценность для обучения
        learning_value = self._calculate_learning_value(memory_type, context, outcome, success)
        
        # Создаем запись памяти
        memory = MemoryEntry(
            memory_type=memory_type,
            timestamp=time.time(),
            context=context,
            action=action,
            outcome=outcome,
            success=success,
            learning_value=learning_value
        )
        
        # Добавляем в текущую память (используем базовую память)
        self.memory.memories.append(memory.to_dict())
        
        # Ограничиваем размер памяти
        if len(self.memory.memories) > self.memory_capacity:
            # Удаляем старые записи с низкой ценностью
            self.memory.memories.sort(key=lambda x: x.get('learning_value', 0))
            self.memory.memories = self.memory.memories[-self.memory_capacity:]
        
        # Обновляем статистику
        self.stats['total_memories'] += 1
        if success:
            self.stats['successful_actions'] += 1
        else:
            self.stats['failed_actions'] += 1
        
        # Добавляем опыт
        experience_gain = learning_value * self.learning_rate
        self.generation_experience += experience_gain
        self.stats['total_experience'] += experience_gain
        
        logger.debug(f"Добавлена память: {memory_type.value} - {action} (успех: {success}, ценность: {learning_value:.2f})")
    
    def _calculate_learning_value(self, memory_type: MemoryType, context: Dict[str, Any], 
                                 outcome: Dict[str, Any], success: bool) -> float:
        """Вычисление ценности записи для обучения"""
        base_value = 0.5
        
        # Множители в зависимости от типа памяти
        type_multipliers = {
            MemoryType.COMBAT: 1.5,
            MemoryType.SKILL_USAGE: 1.3,
            MemoryType.ITEM_USAGE: 1.2,
            MemoryType.MOVEMENT: 0.8,
            MemoryType.ENVIRONMENT: 0.7,
            MemoryType.SOCIAL: 0.6
        }
        
        base_value *= type_multipliers.get(memory_type, 1.0)
        
        # Множитель успеха/неудачи
        if success:
            base_value *= 1.2
        else:
            base_value *= 0.8  # Неудачи тоже важны для обучения
        
        # Дополнительные множители из контекста
        if 'damage_dealt' in outcome:
            damage = outcome['damage_dealt']
            if damage > 0:
                base_value *= min(1.0 + damage / 100.0, 2.0)
        
        if 'health_lost' in outcome:
            health_lost = outcome['health_lost']
            if health_lost > 0:
                base_value *= 1.1  # Потеря здоровья - важный опыт
        
        if 'skill_used' in context:
            base_value *= 1.1  # Использование скиллов важно
        
        if 'item_used' in context:
            base_value *= 1.05  # Использование предметов
        
        return min(base_value, 1.0)  # Ограничиваем максимальную ценность
    
    def get_relevant_memories(self, memory_type: MemoryType, context: Dict[str, Any], 
                            limit: int = 10) -> List[MemoryEntry]:
        """Получение релевантных записей памяти"""
        # Фильтруем по типу памяти
        relevant = [mem for mem in self.memory.memories if mem.get('memory_type') == memory_type.value]
        
        # Сортируем по релевантности (простая эвристика)
        def relevance_score(memory: Dict[str, Any]) -> float:
            score = memory.get('learning_value', 0)
            
            # Бонус за похожий контекст
            context_similarity = self._calculate_context_similarity(memory.get('context', {}), context)
            score += context_similarity * 0.3
            
            # Бонус за недавность
            time_diff = time.time() - memory.get('timestamp', 0)
            recency_bonus = max(0, 1.0 - time_diff / 3600.0)  # 1 час
            score += recency_bonus * 0.2
            
            return score
        
        relevant.sort(key=relevance_score, reverse=True)
        
        # Конвертируем обратно в MemoryEntry
        return [MemoryEntry.from_dict(mem) for mem in relevant[:limit]]
    
    def _calculate_context_similarity(self, context1: Dict[str, Any], context2: Dict[str, Any]) -> float:
        """Вычисление схожести контекстов"""
        if not context1 or not context2:
            return 0.0
        
        # Простая эвристика схожести
        common_keys = set(context1.keys()) & set(context2.keys())
        if not common_keys:
            return 0.0
        
        similarity = 0.0
        for key in common_keys:
            val1 = context1[key]
            val2 = context2[key]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Числовые значения
                max_val = max(abs(val1), abs(val2))
                if max_val > 0:
                    similarity += 1.0 - abs(val1 - val2) / max_val
            elif isinstance(val1, str) and isinstance(val2, str):
                # Строковые значения
                if val1 == val2:
                    similarity += 1.0
                elif val1 in val2 or val2 in val1:
                    similarity += 0.5
        
        return similarity / len(common_keys)
    
    def end_generation(self, cause_of_death: Optional[str] = None, final_stats: Optional[Dict[str, Any]] = None):
        """Завершение текущего поколения"""
        if not final_stats:
            final_stats = self.stats.copy()
        
        # Конвертируем память в MemoryEntry
        memories = []
        for mem_dict in self.memory.memories:
            try:
                memories.append(MemoryEntry.from_dict(mem_dict))
            except Exception as e:
                logger.warning(f"Ошибка конвертации памяти: {e}")
        
        # Создаем память поколения
        generation_memory = GenerationMemory(
            generation_id=self.current_generation,
            entity_id=self.entity_id,
            entity_type=self.entity_type,
            start_time=self.generation_start_time,
            end_time=time.time(),
            total_experience=self.generation_experience,
            memories=memories,
            final_stats=final_stats,
            cause_of_death=cause_of_death
        )
        
        # Добавляем в память поколений
        self.generation_memories.append(generation_memory)
        
        # Ограничиваем размер памяти поколений
        if len(self.generation_memories) > self.generation_memory_capacity:
            # Удаляем старые поколения с низким опытом
            self.generation_memories.sort(key=lambda x: x.total_experience)
            self.generation_memories = self.generation_memories[-self.generation_memory_capacity:]
        
        # Обновляем статистику
        self.stats['total_generations'] += 1
        
        # Сбрасываем текущее поколение
        self.current_generation += 1
        self.generation_start_time = time.time()
        self.generation_experience = 0.0
        
        # Сохраняем память
        self._save_memory()
        
        logger.info(f"Поколение {generation_memory.generation_id} завершено: {cause_of_death or 'естественная смерть'}")
    
    def get_learning_data(self) -> Dict[str, Any]:
        """Получение данных для обучения ИИ"""
        # Анализируем память для извлечения паттернов
        patterns = self._analyze_patterns()
        
        # Получаем статистику успешных действий
        successful_combat = [mem for mem in self.memory.memories 
                           if mem.get('memory_type') == MemoryType.COMBAT.value and mem.get('success', False)]
        failed_combat = [mem for mem in self.memory.memories 
                        if mem.get('memory_type') == MemoryType.COMBAT.value and not mem.get('success', True)]
        
        # Анализируем использование скиллов
        skill_usage = {}
        for mem in self.memory.memories:
            if mem.get('memory_type') == MemoryType.SKILL_USAGE.value:
                skill_name = mem.get('context', {}).get('skill_name', 'unknown')
                if skill_name not in skill_usage:
                    skill_usage[skill_name] = {'success': 0, 'total': 0}
                skill_usage[skill_name]['total'] += 1
                if mem.get('success', False):
                    skill_usage[skill_name]['success'] += 1
        
        return {
            'patterns': patterns,
            'combat_success_rate': len(successful_combat) / max(1, len(successful_combat) + len(failed_combat)),
            'skill_usage': skill_usage,
            'recent_memories': self.memory.memories[-10:],
            'generation_stats': {
                'current_generation': self.current_generation,
                'total_generations': self.stats['total_generations'],
                'total_experience': self.stats['total_experience']
            }
        }
    
    def _analyze_patterns(self) -> Dict[str, Any]:
        """Анализ паттернов в памяти"""
        patterns = {
            'preferred_actions': {},
            'successful_combinations': [],
            'avoided_situations': [],
            'optimal_ranges': {}
        }
        
        # Анализируем предпочитаемые действия
        action_counts = {}
        for mem in self.memory.memories:
            action = mem.get('action', '')
            if action not in action_counts:
                action_counts[action] = {'success': 0, 'total': 0}
            action_counts[action]['total'] += 1
            if mem.get('success', False):
                action_counts[action]['success'] += 1
        
        # Находим наиболее успешные действия
        for action, counts in action_counts.items():
            success_rate = counts['success'] / counts['total']
            if success_rate > 0.6:  # Успешность выше 60%
                patterns['preferred_actions'][action] = success_rate
        
        # Анализируем успешные комбинации действий
        recent_memories = self.memory.memories[-20:]  # Последние 20 действий
        for i in range(len(recent_memories) - 1):
            mem1 = recent_memories[i]
            mem2 = recent_memories[i + 1]
            if mem1.get('success', False) and mem2.get('success', False):
                combination = f"{mem1.get('action', '')} -> {mem2.get('action', '')}"
                if combination not in patterns['successful_combinations']:
                    patterns['successful_combinations'].append(combination)
        
        return patterns
    
    def _get_memory_file_path(self) -> str:
        """Получение пути к файлу памяти"""
        memory_dir = f"saves/ai_memory/{getattr(self, 'save_slot', 'default')}"
        os.makedirs(memory_dir, exist_ok=True)
        return f"{memory_dir}/{self.entity_id}_memory.json"
    
    def _save_memory(self):
        """Сохранение памяти в файл"""
        try:
            memory_data = {
                'entity_id': self.entity_id,
                'entity_type': self.entity_type.value,
                'save_slot': getattr(self, 'save_slot', 'default'),
                'stats': self.stats,
                'current_generation': self.current_generation,
                'generation_memories': [gen.to_dict() for gen in self.generation_memories]
            }
            
            with open(self._get_memory_file_path(), 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Память сохранена: {self.entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения памяти: {e}")
    
    def _load_memory(self):
        """Загрузка памяти из файла"""
        try:
            file_path = self._get_memory_file_path()
            if not os.path.exists(file_path):
                logger.debug(f"Файл памяти не найден: {file_path}")
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            # Загружаем статистику
            self.stats = memory_data.get('stats', self.stats)
            self.current_generation = memory_data.get('current_generation', 0)
            
            # Загружаем память поколений
            generation_data = memory_data.get('generation_memories', [])
            self.generation_memories = [GenerationMemory.from_dict(gen) for gen in generation_data]
            
            logger.info(f"Память загружена: {self.entity_id} ({len(self.generation_memories)} поколений)")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки памяти: {e}")
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Получение сводки памяти"""
        return {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type.value,
            'current_generation': self.current_generation,
            'total_generations': self.stats['total_generations'],
            'total_experience': self.stats['total_experience'],
            'current_memories': len(self.memory.memories),
            'generation_memories': len(self.generation_memories),
            'learning_rate': self.learning_rate,
            'success_rate': self.stats['successful_actions'] / max(1, self.stats['successful_actions'] + self.stats['failed_actions'])
        }
