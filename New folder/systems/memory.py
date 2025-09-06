#!/usr/bin/env python3
"""Система памяти - расширенная память с AI и эволюцией
Управление памятью сущностей, обучением и эволюционными изменениями"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import *
from typing import Dict, List, Optional, Any, Tuple, Callable
import logging
import math
import time
import random
import json
import pickle

logger = logging.getLogger(__name__)

# = ДОПОЛНИТЕЛЬНЫЕ ТИПЫ ПАМЯТИ

class MemoryType(Enum):
    """Типы памяти"""
    COMBAT = "combat"              # Боевые воспоминания
    MOVEMENT = "movement"          # Движение
    SKILL_USAGE = "skill_usage"    # Использование навыков
    ITEM_USAGE = "item_usage"      # Использование предметов
    ENVIRONMENT = "environment"    # Окружение
    SOCIAL = "social"              # Социальные взаимодействия
    SEMANTIC = "semantic"          # Семантическая память

class MemoryCategory(Enum):
    """Категории памяти"""
    COMBAT = "combat"              # Боевые воспоминания
    SOCIAL = "social"              # Социальные взаимодействия
    EXPLORATION = "exploration"    # Исследования
    LEARNING = "learning"          # Обучение
    SURVIVAL = "survival"          # Выживание
    EVOLUTION = "evolution"        # Эволюция

class MemoryStrength(Enum):
    """Сила памяти"""
    WEAK = "weak"                  # Слабая
    NORMAL = "normal"              # Обычная
    STRONG = "strong"              # Сильная
    INTENSE = "intense"            # Интенсивная

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class Memory:
    """Воспоминание"""
    memory_id: str
    entity_id: str
    memory_type: MemoryType
    category: MemoryCategory
    title: str
    description: str
    data: Dict[str, Any] = field(default_factory=dict)
    strength: MemoryStrength = MemoryStrength.NORMAL
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    emotional_value: float = 0.0
    importance: float = 0.5
    decay_rate: float = 0.01
    is_consolidated: bool = False

@dataclass
class MemoryPattern:
    """Паттерн памяти"""
    pattern_id: str
    name: str
    description: str
    memory_types: List[MemoryType] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    triggers: List[str] = field(default_factory=list)
    effects: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EntityMemory:
    """Память сущности"""
    entity_id: str
    short_term_memories: List[Memory] = field(default_factory=list)
    long_term_memories: List[Memory] = field(default_factory=list)
    memory_patterns: List[MemoryPattern] = field(default_factory=list)
    learning_rate: float = 1.0
    memory_capacity: int = 1000
    consolidation_threshold: float = 0.7
    last_consolidation: float = field(default_factory=time.time)

@dataclass
class SharedMemory:
    """Общая память"""
    memory_id: str
    title: str
    description: str
    contributors: List[str] = field(default_factory=list)
    memory_type: MemoryType = MemoryType.SEMANTIC
    category: MemoryCategory = MemoryCategory.LEARNING
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    access_count: int = 0

@dataclass
class EvolutionMemory:
    """Память эволюции"""
    entity_id: str
    evolution_stage: int
    mutations: List[Dict[str, Any]] = field(default_factory=list)
    adaptations: List[Dict[str, Any]] = field(default_factory=list)
    learning_curve: List[float] = field(default_factory=list)
    survival_rate: float = 0.0
    reproduction_rate: float = 0.0

class MemorySystem:
    """Система управления памятью"""
    
    def __init__(self):
        self.entities_memory: Dict[str, EntityMemory] = {}
        self.shared_memories: Dict[str, SharedMemory] = {}
        self.evolution_memories: Dict[str, EvolutionMemory] = {}
        self.memory_patterns: Dict[str, MemoryPattern] = {}
        self.consolidation_timer = 0.0
        self.consolidation_interval = 60.0  # секунды
        
        # Настройки памяти
        self.short_term_capacity = 50
        self.long_term_capacity = 1000
        self.consolidation_threshold = 0.7
        self.decay_rate = 0.01
        
        logger.info("MemorySystem initialized")
    
    def initialize_entity_memory(self, entity_id: str, learning_rate: float = 1.0):
        """Инициализация памяти для сущности"""
        if entity_id not in self.entities_memory:
            self.entities_memory[entity_id] = EntityMemory(
                entity_id=entity_id,
                learning_rate=learning_rate
            )
            logger.info(f"Initialized memory for entity {entity_id}")
    
    def add_memory(self, entity_id: str, memory_type: MemoryType, category: MemoryCategory,
                   title: str, description: str, data: Dict[str, Any] = None,
                   importance: float = 0.5, emotional_value: float = 0.0):
        """Добавление воспоминания"""
        if entity_id not in self.entities_memory:
            self.initialize_entity_memory(entity_id)
        
        memory = Memory(
            memory_id=f"{entity_id}_{int(time.time() * 1000)}",
            entity_id=entity_id,
            memory_type=memory_type,
            category=category,
            title=title,
            description=description,
            data=data or {},
            importance=importance,
            emotional_value=emotional_value
        )
        
        # Добавляем в краткосрочную память
        entity_memory = self.entities_memory[entity_id]
        entity_memory.short_term_memories.append(memory)
        
        # Ограничиваем размер краткосрочной памяти
        if len(entity_memory.short_term_memories) > self.short_term_capacity:
            entity_memory.short_term_memories.pop(0)
        
        logger.debug(f"Added memory '{title}' to entity {entity_id}")
        return memory.memory_id
    
    def get_memories(self, entity_id: str, memory_type: MemoryType = None,
                    category: MemoryCategory = None, limit: int = 10) -> List[Memory]:
        """Получение воспоминаний"""
        if entity_id not in self.entities_memory:
            return []
        
        entity_memory = self.entities_memory[entity_id]
        memories = entity_memory.short_term_memories + entity_memory.long_term_memories
        
        # Фильтрация
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]
        if category:
            memories = [m for m in memories if m.category == category]
        
        # Сортировка по важности и времени доступа
        memories.sort(key=lambda m: (m.importance, m.last_accessed), reverse=True)
        
        return memories[:limit]
    
    def consolidate_memories(self, entity_id: str):
        """Консолидация памяти (переход из краткосрочной в долгосрочную)"""
        if entity_id not in self.entities_memory:
            return
        
        entity_memory = self.entities_memory[entity_id]
        current_time = time.time()
        
        # Проверяем интервал консолидации
        if current_time - entity_memory.last_consolidation < self.consolidation_interval:
            return
        
        memories_to_consolidate = []
        
        for memory in entity_memory.short_term_memories:
            # Вычисляем силу памяти на основе важности и эмоциональной ценности
            memory_strength = (memory.importance + memory.emotional_value) / 2
            
            if memory_strength >= self.consolidation_threshold:
                memories_to_consolidate.append(memory)
        
        # Перемещаем важные воспоминания в долгосрочную память
        for memory in memories_to_consolidate:
            memory.is_consolidated = True
            entity_memory.long_term_memories.append(memory)
            entity_memory.short_term_memories.remove(memory)
        
        # Ограничиваем размер долгосрочной памяти
        if len(entity_memory.long_term_memories) > self.long_term_capacity:
            # Удаляем самые старые и менее важные воспоминания
            entity_memory.long_term_memories.sort(key=lambda m: (m.importance, m.created_at))
            entity_memory.long_term_memories = entity_memory.long_term_memories[-self.long_term_capacity:]
        
        entity_memory.last_consolidation = current_time
        logger.debug(f"Consolidated {len(memories_to_consolidate)} memories for entity {entity_id}")
    
    def decay_memories(self, entity_id: str, dt: float):
        """Распад воспоминаний со временем"""
        if entity_id not in self.entities_memory:
            return
        
        entity_memory = self.entities_memory[entity_id]
        
        for memory in entity_memory.short_term_memories + entity_memory.long_term_memories:
            # Уменьшаем важность со временем
            memory.importance -= memory.decay_rate * dt
            
            # Если важность стала слишком низкой, удаляем воспоминание
            if memory.importance <= 0.1:
                if memory in entity_memory.short_term_memories:
                    entity_memory.short_term_memories.remove(memory)
                elif memory in entity_memory.long_term_memories:
                    entity_memory.long_term_memories.remove(memory)
    
    def add_shared_memory(self, title: str, description: str, contributors: List[str],
                         memory_type: MemoryType = MemoryType.SEMANTIC,
                         category: MemoryCategory = MemoryCategory.LEARNING,
                         data: Dict[str, Any] = None):
        """Добавление общей памяти"""
        memory_id = f"shared_{int(time.time() * 1000)}"
        
        shared_memory = SharedMemory(
            memory_id=memory_id,
            title=title,
            description=description,
            contributors=contributors,
            memory_type=memory_type,
            category=category,
            data=data or {}
        )
        
        self.shared_memories[memory_id] = shared_memory
        logger.info(f"Added shared memory '{title}' with {len(contributors)} contributors")
        return memory_id
    
    def get_shared_memories(self, memory_type: MemoryType = None,
                           category: MemoryCategory = None) -> List[SharedMemory]:
        """Получение общих воспоминаний"""
        memories = list(self.shared_memories.values())
        
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]
        if category:
            memories = [m for m in memories if m.category == category]
        
        memories.sort(key=lambda m: m.last_updated, reverse=True)
        return memories
    
    def add_evolution_memory(self, entity_id: str, evolution_stage: int,
                            mutations: List[Dict[str, Any]] = None,
                            adaptations: List[Dict[str, Any]] = None):
        """Добавление памяти эволюции"""
        if entity_id not in self.evolution_memories:
            self.evolution_memories[entity_id] = EvolutionMemory(
                entity_id=entity_id,
                evolution_stage=evolution_stage
            )
        
        evolution_memory = self.evolution_memories[entity_id]
        evolution_memory.evolution_stage = evolution_stage
        
        if mutations:
            evolution_memory.mutations.extend(mutations)
        if adaptations:
            evolution_memory.adaptations.extend(adaptations)
        
        logger.info(f"Updated evolution memory for entity {entity_id} at stage {evolution_stage}")
    
    def get_evolution_memory(self, entity_id: str) -> Optional[EvolutionMemory]:
        """Получение памяти эволюции"""
        return self.evolution_memories.get(entity_id)
    
    def create_memory_pattern(self, pattern_id: str, name: str, description: str,
                            memory_types: List[MemoryType], conditions: Dict[str, Any],
                            triggers: List[str], effects: Dict[str, Any]):
        """Создание паттерна памяти"""
        pattern = MemoryPattern(
            pattern_id=pattern_id,
            name=name,
            description=description,
            memory_types=memory_types,
            conditions=conditions,
            triggers=triggers,
            effects=effects
        )
        
        self.memory_patterns[pattern_id] = pattern
        logger.info(f"Created memory pattern '{name}'")
    
    def apply_memory_pattern(self, entity_id: str, pattern_id: str, context: Dict[str, Any]):
        """Применение паттерна памяти"""
        if pattern_id not in self.memory_patterns:
            return False
        
        pattern = self.memory_patterns[pattern_id]
        
        # Проверяем условия
        for condition_key, condition_value in pattern.conditions.items():
            if context.get(condition_key) != condition_value:
                return False
        
        # Применяем эффекты
        for effect_key, effect_value in pattern.effects.items():
            if effect_key in context:
                context[effect_key] = effect_value
        
        logger.debug(f"Applied memory pattern '{pattern.name}' to entity {entity_id}")
        return True
    
    def update_memory_system(self, dt: float):
        """Обновление системы памяти"""
        current_time = time.time()
        
        # Обновляем все сущности
        for entity_id in list(self.entities_memory.keys()):
            # Консолидация памяти
            self.consolidate_memories(entity_id)
            
            # Распад воспоминаний
            self.decay_memories(entity_id, dt)
        
        # Обновляем таймер консолидации
        self.consolidation_timer += dt
        if self.consolidation_timer >= self.consolidation_interval:
            self.consolidation_timer = 0.0
    
    def get_memory_stats(self, entity_id: str) -> Dict[str, Any]:
        """Получение статистики памяти"""
        if entity_id not in self.entities_memory:
            return {}
        
        entity_memory = self.entities_memory[entity_id]
        
        return {
            "short_term_count": len(entity_memory.short_term_memories),
            "long_term_count": len(entity_memory.long_term_memories),
            "total_memories": len(entity_memory.short_term_memories) + len(entity_memory.long_term_memories),
            "learning_rate": entity_memory.learning_rate,
            "memory_capacity": entity_memory.memory_capacity,
            "last_consolidation": entity_memory.last_consolidation
        }
    
    def save_memory_data(self, filepath: str):
        """Сохранение данных памяти"""
        data = {
            "entities_memory": {
                entity_id: {
                    "entity_id": memory.entity_id,
                    "short_term_memories": [vars(m) for m in memory.short_term_memories],
                    "long_term_memories": [vars(m) for m in memory.long_term_memories],
                    "learning_rate": memory.learning_rate,
                    "memory_capacity": memory.memory_capacity,
                    "consolidation_threshold": memory.consolidation_threshold,
                    "last_consolidation": memory.last_consolidation
                }
                for entity_id, memory in self.entities_memory.items()
            },
            "shared_memories": {
                memory_id: vars(memory)
                for memory_id, memory in self.shared_memories.items()
            },
            "evolution_memories": {
                entity_id: vars(memory)
                for entity_id, memory in self.evolution_memories.items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved memory data to {filepath}")
    
    def load_memory_data(self, filepath: str):
        """Загрузка данных памяти"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Загружаем память сущностей
            for entity_id, memory_data in data.get("entities_memory", {}).items():
                entity_memory = EntityMemory(
                    entity_id=memory_data["entity_id"],
                    learning_rate=memory_data["learning_rate"],
                    memory_capacity=memory_data["memory_capacity"],
                    consolidation_threshold=memory_data["consolidation_threshold"],
                    last_consolidation=memory_data["last_consolidation"]
                )
                
                # Восстанавливаем краткосрочные воспоминания
                for mem_data in memory_data["short_term_memories"]:
                    memory = Memory(**mem_data)
                    entity_memory.short_term_memories.append(memory)
                
                # Восстанавливаем долгосрочные воспоминания
                for mem_data in memory_data["long_term_memories"]:
                    memory = Memory(**mem_data)
                    entity_memory.long_term_memories.append(memory)
                
                self.entities_memory[entity_id] = entity_memory
            
            # Загружаем общие воспоминания
            for memory_id, memory_data in data.get("shared_memories", {}).items():
                shared_memory = SharedMemory(**memory_data)
                self.shared_memories[memory_id] = shared_memory
            
            # Загружаем память эволюции
            for entity_id, memory_data in data.get("evolution_memories", {}).items():
                evolution_memory = EvolutionMemory(**memory_data)
                self.evolution_memories[entity_id] = evolution_memory
            
            logger.info(f"Loaded memory data from {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load memory data from {filepath}: {e}")
