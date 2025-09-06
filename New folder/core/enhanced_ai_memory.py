#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
УЛУЧШЕННАЯ СИСТЕМА ПАМЯТИ ИИ
Интеграция с системой сохранений для роглайк механик
Поддержка общей памяти врагов и индивидуальной памяти игрока
"""

import time
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from utils.logging_system import get_logger, log_system_event

class MemoryType(Enum):
    """Типы памяти"""
    COMBAT = "combat"
    MOVEMENT = "movement"
    SKILL_USAGE = "skill_usage"
    ITEM_USAGE = "item_usage"
    ENVIRONMENT = "environment"
    SOCIAL = "social"
    LEARNING = "learning"
    EVOLUTION = "evolution"

class EntityType(Enum):
    """Типы сущностей"""
    PLAYER = "player"
    BASIC_ENEMY = "basic_enemy"
    BOSS = "boss"
    CHIMERA = "chimera"

@dataclass
class MemoryEntry:
    """Запись в памяти"""
    memory_id: str
    entity_id: str
    memory_type: MemoryType
    data: Dict[str, Any]
    importance: float = 1.0
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    decay_rate: float = 0.01
    is_consolidated: bool = False

@dataclass
class LearningPattern:
    """Паттерн обучения"""
    pattern_id: str
    entity_id: str
    pattern_type: str
    conditions: Dict[str, Any]
    actions: List[str]
    success_rate: float = 0.0
    usage_count: int = 0
    last_used: float = field(default_factory=time.time)

@dataclass
class EntityMemory:
    """Память сущности"""
    entity_id: str
    entity_type: EntityType
    short_term_memories: List[MemoryEntry] = field(default_factory=list)
    long_term_memories: List[MemoryEntry] = field(default_factory=list)
    learning_patterns: List[LearningPattern] = field(default_factory=list)
    learning_rate: float = 1.0
    memory_capacity: int = 1000
    consolidation_threshold: float = 0.7
    last_consolidation: float = field(default_factory=time.time)
    total_experience: float = 0.0
    evolution_stage: int = 1

@dataclass
class SharedEnemyMemory:
    """Общая память врагов"""
    memory_bank_id: str
    shared_memories: List[MemoryEntry] = field(default_factory=list)
    shared_patterns: List[LearningPattern] = field(default_factory=list)
    total_learning_experience: float = 0.0
    evolution_level: int = 1
    last_update: float = field(default_factory=time.time)

class EnhancedAIMemorySystem:
    """Улучшенная система памяти ИИ"""
    
    def __init__(self, memory_directory: str = "memory/ai"):
        self.memory_directory = Path(memory_directory)
        self.memory_directory.mkdir(parents=True, exist_ok=True)
        
        self.logger = get_logger(__name__)
        
        # Память сущностей
        self.entity_memories: Dict[str, EntityMemory] = {}
        self.shared_enemy_memory = SharedEnemyMemory(memory_bank_id="enemy_shared")
        
        # Настройки памяти
        self.short_term_capacity = 50
        self.long_term_capacity = 1000
        self.consolidation_interval = 60.0  # секунды
        self.decay_rate = 0.01
        
        # Настройки обучения
        self.player_learning_rate = 1.0
        self.basic_enemy_learning_rate = 0.05  # Низкая скорость обучения для обычных врагов
        self.boss_learning_rate = 0.01         # Еще более низкая для боссов
        self.chimera_learning_rate = 0.02      # Средняя для химер
        
        log_system_event("enhanced_ai_memory", "initialized")
    
    def initialize_entity_memory(self, entity_id: str, entity_type: EntityType) -> bool:
        """Инициализация памяти для сущности"""
        try:
            if entity_id in self.entity_memories:
                return True
            
            # Определяем скорость обучения
            learning_rate = self._get_learning_rate(entity_type)
            
            entity_memory = EntityMemory(
                entity_id=entity_id,
                entity_type=entity_type,
                learning_rate=learning_rate
            )
            
            self.entity_memories[entity_id] = entity_memory
            
            self.logger.info(f"Initialized memory for {entity_type.value} entity {entity_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing entity memory: {e}")
            return False
    
    def add_memory(self, entity_id: str, memory_type: MemoryType, data: Dict[str, Any],
                   importance: float = 1.0) -> str:
        """Добавление воспоминания"""
        try:
            if entity_id not in self.entity_memories:
                # Определяем тип сущности по ID
                entity_type = self._determine_entity_type(entity_id)
                self.initialize_entity_memory(entity_id, entity_type)
            
            memory_id = f"{entity_id}_{int(time.time() * 1000)}"
            
            memory = MemoryEntry(
                memory_id=memory_id,
                entity_id=entity_id,
                memory_type=memory_type,
                data=data,
                importance=importance
            )
            
            entity_memory = self.entity_memories[entity_id]
            entity_memory.short_term_memories.append(memory)
            
            # Ограничиваем размер краткосрочной памяти
            if len(entity_memory.short_term_memories) > self.short_term_capacity:
                entity_memory.short_term_memories.pop(0)
            
            # Обновляем общий опыт
            entity_memory.total_experience += importance
            
            # Если это враг, добавляем в общую память врагов
            if entity_memory.entity_type in [EntityType.BASIC_ENEMY, EntityType.BOSS, EntityType.CHIMERA]:
                self._add_to_shared_enemy_memory(memory, entity_memory.learning_rate)
            
            self.logger.debug(f"Added memory '{memory_type.value}' to entity {entity_id}")
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Error adding memory: {e}")
            return ""
    
    def get_memories(self, entity_id: str, memory_type: MemoryType = None,
                    limit: int = 10) -> List[MemoryEntry]:
        """Получение воспоминаний"""
        if entity_id not in self.entity_memories:
            return []
        
        entity_memory = self.entity_memories[entity_id]
        memories = entity_memory.short_term_memories + entity_memory.long_term_memories
        
        # Фильтрация по типу
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]
        
        # Сортировка по важности и времени доступа
        memories.sort(key=lambda m: (m.importance, m.last_access), reverse=True)
        
        # Обновляем счетчик доступа
        for memory in memories[:limit]:
            memory.access_count += 1
            memory.last_access = time.time()
        
        return memories[:limit]
    
    def get_shared_enemy_memories(self, memory_type: MemoryType = None,
                                 limit: int = 10) -> List[MemoryEntry]:
        """Получение общих воспоминаний врагов"""
        memories = self.shared_enemy_memory.shared_memories
        
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]
        
        memories.sort(key=lambda m: (m.importance, m.last_access), reverse=True)
        
        # Обновляем счетчик доступа
        for memory in memories[:limit]:
            memory.access_count += 1
            memory.last_access = time.time()
        
        return memories[:limit]
    
    def learn_from_experience(self, entity_id: str, experience_data: Dict[str, Any]) -> bool:
        """Обучение на основе опыта"""
        try:
            if entity_id not in self.entity_memories:
                return False
            
            entity_memory = self.entity_memories[entity_id]
            
            # Создаем паттерн обучения
            pattern = LearningPattern(
                pattern_id=f"pattern_{uuid.uuid4().hex[:8]}",
                entity_id=entity_id,
                pattern_type=experience_data.get("type", "unknown"),
                conditions=experience_data.get("conditions", {}),
                actions=experience_data.get("actions", []),
                success_rate=experience_data.get("success_rate", 0.0)
            )
            
            entity_memory.learning_patterns.append(pattern)
            
            # Ограничиваем количество паттернов
            if len(entity_memory.learning_patterns) > 100:
                entity_memory.learning_patterns = entity_memory.learning_patterns[-100:]
            
            # Обновляем общий опыт
            entity_memory.total_experience += experience_data.get("experience_gained", 0.0)
            
            # Проверяем эволюцию
            self._check_evolution(entity_id)
            
            self.logger.debug(f"Learned from experience for entity {entity_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error learning from experience: {e}")
            return False
    
    def consolidate_memories(self, entity_id: str) -> bool:
        """Консолидация памяти (переход из краткосрочной в долгосрочную)"""
        try:
            if entity_id not in self.entity_memories:
                return False
            
            entity_memory = self.entity_memories[entity_id]
            current_time = time.time()
            
            # Проверяем интервал консолидации
            if current_time - entity_memory.last_consolidation < self.consolidation_interval:
                return False
            
            memories_to_consolidate = []
            
            for memory in entity_memory.short_term_memories:
                # Вычисляем силу памяти на основе важности и доступа
                memory_strength = (memory.importance + memory.access_count * 0.1) / 2
                
                if memory_strength >= self.consolidation_threshold:
                    memories_to_consolidate.append(memory)
            
            # Перемещаем важные воспоминания в долгосрочную память
            for memory in memories_to_consolidate:
                memory.is_consolidated = True
                entity_memory.long_term_memories.append(memory)
                entity_memory.short_term_memories.remove(memory)
            
            # Ограничиваем размер долгосрочной памяти
            if len(entity_memory.long_term_memories) > self.long_term_capacity:
                entity_memory.long_term_memories.sort(key=lambda m: (m.importance, m.created_at))
                entity_memory.long_term_memories = entity_memory.long_term_memories[-self.long_term_capacity:]
            
            entity_memory.last_consolidation = current_time
            
            self.logger.debug(f"Consolidated {len(memories_to_consolidate)} memories for entity {entity_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error consolidating memories: {e}")
            return False
    
    def decay_memories(self, entity_id: str, dt: float) -> bool:
        """Распад воспоминаний со временем"""
        try:
            if entity_id not in self.entity_memories:
                return False
            
            entity_memory = self.entity_memories[entity_id]
            memories_to_remove = []
            
            for memory in entity_memory.short_term_memories + entity_memory.long_term_memories:
                # Уменьшаем важность со временем
                memory.importance -= memory.decay_rate * dt
                
                # Если важность стала слишком низкой, помечаем для удаления
                if memory.importance <= 0.1:
                    memories_to_remove.append(memory)
            
            # Удаляем устаревшие воспоминания
            for memory in memories_to_remove:
                if memory in entity_memory.short_term_memories:
                    entity_memory.short_term_memories.remove(memory)
                elif memory in entity_memory.long_term_memories:
                    entity_memory.long_term_memories.remove(memory)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error decaying memories: {e}")
            return False
    
    def get_memory_level(self, entity_id: str) -> int:
        """Получение уровня памяти для сущности"""
        if entity_id not in self.entity_memories:
            return 1
        
        entity_memory = self.entity_memories[entity_id]
        
        # Вычисляем уровень на основе общего опыта
        if entity_memory.entity_type == EntityType.PLAYER:
            return min(10, 1 + int(entity_memory.total_experience / 100))
        else:
            # Для врагов используем общую память
            return min(5, 1 + int(self.shared_enemy_memory.total_learning_experience / 500))
    
    def get_learning_rate(self, entity_id: str) -> float:
        """Получение скорости обучения для сущности"""
        if entity_id not in self.entity_memories:
            return 0.0
        
        return self.entity_memories[entity_id].learning_rate
    
    def save_memory_data(self, save_id: str) -> bool:
        """Сохранение данных памяти в сохранение"""
        try:
            memory_data = {
                "entity_memories": {},
                "shared_enemy_memory": {
                    "memory_bank_id": self.shared_enemy_memory.memory_bank_id,
                    "shared_memories": [
                        {
                            "memory_id": m.memory_id,
                            "entity_id": m.entity_id,
                            "memory_type": m.memory_type.value,
                            "data": m.data,
                            "importance": m.importance,
                            "timestamp": m.timestamp,
                            "access_count": m.access_count,
                            "last_access": m.last_access,
                            "decay_rate": m.decay_rate,
                            "is_consolidated": m.is_consolidated
                        }
                        for m in self.shared_enemy_memory.shared_memories
                    ],
                    "shared_patterns": [
                        {
                            "pattern_id": p.pattern_id,
                            "entity_id": p.entity_id,
                            "pattern_type": p.pattern_type,
                            "conditions": p.conditions,
                            "actions": p.actions,
                            "success_rate": p.success_rate,
                            "usage_count": p.usage_count,
                            "last_used": p.last_used
                        }
                        for p in self.shared_enemy_memory.shared_patterns
                    ],
                    "total_learning_experience": self.shared_enemy_memory.total_learning_experience,
                    "evolution_level": self.shared_enemy_memory.evolution_level,
                    "last_update": self.shared_enemy_memory.last_update
                }
            }
            
            # Сохраняем память каждой сущности
            for entity_id, entity_memory in self.entity_memories.items():
                memory_data["entity_memories"][entity_id] = {
                    "entity_id": entity_memory.entity_id,
                    "entity_type": entity_memory.entity_type.value,
                    "short_term_memories": [
                        {
                            "memory_id": m.memory_id,
                            "entity_id": m.entity_id,
                            "memory_type": m.memory_type.value,
                            "data": m.data,
                            "importance": m.importance,
                            "timestamp": m.timestamp,
                            "access_count": m.access_count,
                            "last_access": m.last_access,
                            "decay_rate": m.decay_rate,
                            "is_consolidated": m.is_consolidated
                        }
                        for m in entity_memory.short_term_memories
                    ],
                    "long_term_memories": [
                        {
                            "memory_id": m.memory_id,
                            "entity_id": m.entity_id,
                            "memory_type": m.memory_type.value,
                            "data": m.data,
                            "importance": m.importance,
                            "timestamp": m.timestamp,
                            "access_count": m.access_count,
                            "last_access": m.last_access,
                            "decay_rate": m.decay_rate,
                            "is_consolidated": m.is_consolidated
                        }
                        for m in entity_memory.long_term_memories
                    ],
                    "learning_patterns": [
                        {
                            "pattern_id": p.pattern_id,
                            "entity_id": p.entity_id,
                            "pattern_type": p.pattern_type,
                            "conditions": p.conditions,
                            "actions": p.actions,
                            "success_rate": p.success_rate,
                            "usage_count": p.usage_count,
                            "last_used": p.last_used
                        }
                        for p in entity_memory.learning_patterns
                    ],
                    "learning_rate": entity_memory.learning_rate,
                    "memory_capacity": entity_memory.memory_capacity,
                    "consolidation_threshold": entity_memory.consolidation_threshold,
                    "last_consolidation": entity_memory.last_consolidation,
                    "total_experience": entity_memory.total_experience,
                    "evolution_stage": entity_memory.evolution_stage
                }
            
            # Сохраняем в файл
            memory_file = self.memory_directory / f"{save_id}_memory.json"
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved memory data to {memory_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving memory data: {e}")
            return False
    
    def load_memory_data(self, save_id: str) -> bool:
        """Загрузка данных памяти из сохранения"""
        try:
            memory_file = self.memory_directory / f"{save_id}_memory.json"
            if not memory_file.exists():
                return False
            
            with open(memory_file, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            # Загружаем память сущностей
            self.entity_memories.clear()
            for entity_id, entity_data in memory_data.get("entity_memories", {}).items():
                entity_memory = EntityMemory(
                    entity_id=entity_data["entity_id"],
                    entity_type=EntityType(entity_data["entity_type"]),
                    learning_rate=entity_data["learning_rate"],
                    memory_capacity=entity_data["memory_capacity"],
                    consolidation_threshold=entity_data["consolidation_threshold"],
                    last_consolidation=entity_data["last_consolidation"],
                    total_experience=entity_data["total_experience"],
                    evolution_stage=entity_data["evolution_stage"]
                )
                
                # Восстанавливаем краткосрочные воспоминания
                for mem_data in entity_data["short_term_memories"]:
                    memory = MemoryEntry(
                        memory_id=mem_data["memory_id"],
                        entity_id=mem_data["entity_id"],
                        memory_type=MemoryType(mem_data["memory_type"]),
                        data=mem_data["data"],
                        importance=mem_data["importance"],
                        timestamp=mem_data["timestamp"],
                        access_count=mem_data["access_count"],
                        last_access=mem_data["last_access"],
                        decay_rate=mem_data["decay_rate"],
                        is_consolidated=mem_data["is_consolidated"]
                    )
                    entity_memory.short_term_memories.append(memory)
                
                # Восстанавливаем долгосрочные воспоминания
                for mem_data in entity_data["long_term_memories"]:
                    memory = MemoryEntry(
                        memory_id=mem_data["memory_id"],
                        entity_id=mem_data["entity_id"],
                        memory_type=MemoryType(mem_data["memory_type"]),
                        data=mem_data["data"],
                        importance=mem_data["importance"],
                        timestamp=mem_data["timestamp"],
                        access_count=mem_data["access_count"],
                        last_access=mem_data["last_access"],
                        decay_rate=mem_data["decay_rate"],
                        is_consolidated=mem_data["is_consolidated"]
                    )
                    entity_memory.long_term_memories.append(memory)
                
                # Восстанавливаем паттерны обучения
                for pattern_data in entity_data["learning_patterns"]:
                    pattern = LearningPattern(
                        pattern_id=pattern_data["pattern_id"],
                        entity_id=pattern_data["entity_id"],
                        pattern_type=pattern_data["pattern_type"],
                        conditions=pattern_data["conditions"],
                        actions=pattern_data["actions"],
                        success_rate=pattern_data["success_rate"],
                        usage_count=pattern_data["usage_count"],
                        last_used=pattern_data["last_used"]
                    )
                    entity_memory.learning_patterns.append(pattern)
                
                self.entity_memories[entity_id] = entity_memory
            
            # Загружаем общую память врагов
            shared_data = memory_data.get("shared_enemy_memory", {})
            self.shared_enemy_memory = SharedEnemyMemory(
                memory_bank_id=shared_data.get("memory_bank_id", "enemy_shared"),
                total_learning_experience=shared_data.get("total_learning_experience", 0.0),
                evolution_level=shared_data.get("evolution_level", 1),
                last_update=shared_data.get("last_update", time.time())
            )
            
            # Восстанавливаем общие воспоминания
            for mem_data in shared_data.get("shared_memories", []):
                memory = MemoryEntry(
                    memory_id=mem_data["memory_id"],
                    entity_id=mem_data["entity_id"],
                    memory_type=MemoryType(mem_data["memory_type"]),
                    data=mem_data["data"],
                    importance=mem_data["importance"],
                    timestamp=mem_data["timestamp"],
                    access_count=mem_data["access_count"],
                    last_access=mem_data["last_access"],
                    decay_rate=mem_data["decay_rate"],
                    is_consolidated=mem_data["is_consolidated"]
                )
                self.shared_enemy_memory.shared_memories.append(memory)
            
            # Восстанавливаем общие паттерны
            for pattern_data in shared_data.get("shared_patterns", []):
                pattern = LearningPattern(
                    pattern_id=pattern_data["pattern_id"],
                    entity_id=pattern_data["entity_id"],
                    pattern_type=pattern_data["pattern_type"],
                    conditions=pattern_data["conditions"],
                    actions=pattern_data["actions"],
                    success_rate=pattern_data["success_rate"],
                    usage_count=pattern_data["usage_count"],
                    last_used=pattern_data["last_used"]
                )
                self.shared_enemy_memory.shared_patterns.append(pattern)
            
            self.logger.info(f"Loaded memory data from {memory_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading memory data: {e}")
            return False
    
    def update_memory_system(self, dt: float):
        """Обновление системы памяти"""
        try:
            # Обновляем все сущности
            for entity_id in list(self.entity_memories.keys()):
                # Консолидация памяти
                self.consolidate_memories(entity_id)
                
                # Распад воспоминаний
                self.decay_memories(entity_id, dt)
            
            # Обновляем общую память врагов
            self._update_shared_enemy_memory(dt)
            
        except Exception as e:
            self.logger.error(f"Error updating memory system: {e}")
    
    def _get_learning_rate(self, entity_type: EntityType) -> float:
        """Получение скорости обучения для типа сущности"""
        learning_rates = {
            EntityType.PLAYER: self.player_learning_rate,
            EntityType.BASIC_ENEMY: self.basic_enemy_learning_rate,
            EntityType.BOSS: self.boss_learning_rate,
            EntityType.CHIMERA: self.chimera_learning_rate
        }
        
        return learning_rates.get(entity_type, 0.0)
    
    def _determine_entity_type(self, entity_id: str) -> EntityType:
        """Определение типа сущности по ID"""
        if entity_id.startswith("player"):
            return EntityType.PLAYER
        elif entity_id.startswith("boss"):
            return EntityType.BOSS
        elif entity_id.startswith("chimera"):
            return EntityType.CHIMERA
        else:
            return EntityType.BASIC_ENEMY
    
    def _add_to_shared_enemy_memory(self, memory: MemoryEntry, learning_rate: float):
        """Добавление в общую память врагов"""
        # Добавляем с учетом скорости обучения
        shared_memory = MemoryEntry(
            memory_id=memory.memory_id,
            entity_id="shared_enemy",
            memory_type=memory.memory_type,
            data=memory.data,
            importance=memory.importance * learning_rate,
            timestamp=memory.timestamp,
            access_count=memory.access_count,
            last_access=memory.last_access,
            decay_rate=memory.decay_rate,
            is_consolidated=memory.is_consolidated
        )
        
        self.shared_enemy_memory.shared_memories.append(shared_memory)
        
        # Обновляем общий опыт обучения
        self.shared_enemy_memory.total_learning_experience += memory.importance * learning_rate
        
        # Ограничиваем размер общей памяти
        if len(self.shared_enemy_memory.shared_memories) > self.long_term_capacity:
            self.shared_enemy_memory.shared_memories.sort(key=lambda m: (m.importance, m.timestamp))
            self.shared_enemy_memory.shared_memories = self.shared_enemy_memory.shared_memories[-self.long_term_capacity:]
    
    def _check_evolution(self, entity_id: str):
        """Проверка эволюции сущности"""
        if entity_id not in self.entity_memories:
            return
        
        entity_memory = self.entity_memories[entity_id]
        
        # Проверяем, нужно ли повысить стадию эволюции
        if entity_memory.entity_type == EntityType.PLAYER:
            new_stage = min(10, 1 + int(entity_memory.total_experience / 1000))
        else:
            new_stage = min(5, 1 + int(self.shared_enemy_memory.total_learning_experience / 2000))
        
        if new_stage > entity_memory.evolution_stage:
            entity_memory.evolution_stage = new_stage
            self.logger.info(f"Entity {entity_id} evolved to stage {new_stage}")
    
    def _update_shared_enemy_memory(self, dt: float):
        """Обновление общей памяти врагов"""
        # Распад общих воспоминаний
        memories_to_remove = []
        
        for memory in self.shared_enemy_memory.shared_memories:
            memory.importance -= memory.decay_rate * dt
            
            if memory.importance <= 0.1:
                memories_to_remove.append(memory)
        
        # Удаляем устаревшие воспоминания
        for memory in memories_to_remove:
            self.shared_enemy_memory.shared_memories.remove(memory)
        
        # Обновляем время последнего обновления
        self.shared_enemy_memory.last_update = time.time()
