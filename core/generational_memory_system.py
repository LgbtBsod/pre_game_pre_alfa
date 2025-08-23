#!/usr/bin/env python3
"""
Система памяти поколений для ИИ.
Хранит опыт предыдущих игровых сессий и влияет на принятие решений.
Вдохновлено механиками из Darkest Dungeon и Diablo.
"""

import random
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Типы памяти"""
    COMBAT_EXPERIENCE = "combat_experience"
    ENEMY_PATTERNS = "enemy_patterns"
    ITEM_USAGE = "item_usage"
    ENVIRONMENTAL_HAZARDS = "environmental_hazards"
    SOCIAL_INTERACTIONS = "social_interactions"
    EMOTIONAL_TRAUMA = "emotional_trauma"
    EVOLUTIONARY_SUCCESS = "evolutionary_success"
    SURVIVAL_STRATEGIES = "survival_strategies"


class MemoryIntensity(Enum):
    """Интенсивность памяти"""
    FAINT = 0.1      # Едва заметная
    WEAK = 0.3       # Слабая
    MODERATE = 0.5   # Умеренная
    STRONG = 0.7     # Сильная
    INTENSE = 0.9    # Интенсивная
    TRAUMATIC = 1.0  # Травматическая


@dataclass
class GenerationalMemory:
    """Память поколения"""
    id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    intensity: float
    generation: int
    created_at: float
    last_accessed: float
    access_count: int
    emotional_impact: float
    survival_value: float
    
    def update_intensity(self, new_intensity: float):
        """Обновление интенсивности памяти"""
        self.intensity = min(1.0, max(0.0, new_intensity))
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class MemoryCluster:
    """Кластер связанных воспоминаний"""
    id: str
    theme: str
    memories: List[str]  # ID воспоминаний
    strength: float
    influence_radius: float
    emotional_resonance: float


class GenerationalMemorySystem:
    """Система памяти поколений"""
    
    def __init__(self, save_directory: str = "save"):
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(exist_ok=True)
        
        # Память текущего поколения
        self.current_generation: int = 1
        self.memories: Dict[str, GenerationalMemory] = {}
        self.memory_clusters: Dict[str, MemoryCluster] = {}
        
        # Настройки системы
        self.memory_decay_rate = 0.01
        self.max_memories_per_type = 100
        self.memory_fusion_threshold = 0.8
        
        # Загрузка существующей памяти
        self._load_generational_memory()
        
        logger.info("Система памяти поколений инициализирована")
    
    def add_memory(self, memory_type: MemoryType, content: Dict[str, Any], 
                   intensity: float, emotional_impact: float = 0.0) -> str:
        """Добавление нового воспоминания"""
        memory_id = str(uuid.uuid4())
        
        # Создание воспоминания
        memory = GenerationalMemory(
            id=memory_id,
            memory_type=memory_type,
            content=content,
            intensity=intensity,
            generation=self.current_generation,
            created_at=time.time(),
            last_accessed=time.time(),
            access_count=1,
            emotional_impact=emotional_impact,
            survival_value=self._calculate_survival_value(content, memory_type)
        )
        
        # Добавление в систему
        self.memories[memory_id] = memory
        
        # Проверка лимитов
        self._enforce_memory_limits(memory_type)
        
        # Попытка слияния с существующими воспоминаниями
        self._attempt_memory_fusion(memory_id)
        
        logger.debug(f"Добавлено воспоминание: {memory_type.value} (ID: {memory_id})")
        return memory_id
    
    def get_relevant_memories(self, context: Dict[str, Any], 
                            memory_types: Optional[List[MemoryType]] = None,
                            limit: int = 10) -> List[GenerationalMemory]:
        """Получение релевантных воспоминаний для контекста"""
        if memory_types is None:
            memory_types = list(MemoryType)
        
        relevant_memories = []
        
        for memory in self.memories.values():
            if memory.memory_type not in memory_types:
                continue
            
            relevance_score = self._calculate_relevance(memory, context)
            if relevance_score > 0.3:  # Минимальный порог релевантности
                relevant_memories.append((memory, relevance_score))
        
        # Сортировка по релевантности и интенсивности
        relevant_memories.sort(key=lambda x: (x[1], x[0].intensity), reverse=True)
        
        return [memory for memory, _ in relevant_memories[:limit]]
    
    def influence_decision(self, context: Dict[str, Any], 
                          available_actions: List[str]) -> Dict[str, float]:
        """Влияние памяти на принятие решений"""
        relevant_memories = self.get_relevant_memories(context)
        
        action_weights = {action: 1.0 for action in available_actions}
        
        for memory in relevant_memories:
            influence = memory.intensity * memory.survival_value
            
            # Применение влияния к действиям
            if memory.memory_type == MemoryType.COMBAT_EXPERIENCE:
                self._apply_combat_memory_influence(memory, action_weights, influence)
            elif memory.memory_type == MemoryType.ENEMY_PATTERNS:
                self._apply_enemy_pattern_influence(memory, action_weights, influence)
            elif memory.memory_type == MemoryType.EMOTIONAL_TRAUMA:
                self._apply_emotional_trauma_influence(memory, action_weights, influence)
        
        # Нормализация весов
        total_weight = sum(action_weights.values())
        if total_weight > 0:
            action_weights = {action: weight / total_weight 
                            for action, weight in action_weights.items()}
        
        return action_weights
    
    def advance_generation(self, survival_rate: float, achievements: List[str]):
        """Переход к следующему поколению"""
        logger.info(f"Переход к поколению {self.current_generation + 1}")
        
        # Сохранение текущего поколения
        self._save_generation_data()
        
        # Эволюция памяти
        self._evolve_memories(survival_rate)
        
        # Создание новых кластеров
        self._create_memory_clusters()
        
        # Переход к новому поколению
        self.current_generation += 1
        
        # Сохранение обновленной системы
        self._save_generational_memory()
        
        logger.info(f"Поколение {self.current_generation} активировано")
    
    def _calculate_survival_value(self, content: Dict[str, Any], 
                                memory_type: MemoryType) -> float:
        """Расчёт ценности воспоминания для выживания"""
        base_value = 0.5
        
        if memory_type == MemoryType.COMBAT_EXPERIENCE:
            # Боевой опыт высоко ценится
            base_value = 0.8
            if content.get("victory", False):
                base_value += 0.2
            if content.get("critical_situation", False):
                base_value += 0.1
        
        elif memory_type == MemoryType.ENEMY_PATTERNS:
            # Паттерны врагов критически важны
            base_value = 0.9
            if content.get("enemy_type") == "boss":
                base_value += 0.1
        
        elif memory_type == MemoryType.EMOTIONAL_TRAUMA:
            # Травматические воспоминания влияют на осторожность
            base_value = 0.7
            if content.get("near_death", False):
                base_value += 0.3
        
        return min(1.0, base_value)
    
    def _calculate_relevance(self, memory: GenerationalMemory, 
                           context: Dict[str, Any]) -> float:
        """Расчёт релевантности воспоминания для контекста"""
        relevance = 0.0
        
        # Временная релевантность (недавние воспоминания важнее)
        time_factor = 1.0 / (1.0 + (time.time() - memory.last_accessed) / 3600)
        relevance += time_factor * 0.3
        
        # Контекстуальная релевантность
        if memory.memory_type == MemoryType.COMBAT_EXPERIENCE:
            if "enemy_type" in context and "enemy_type" in memory.content:
                if context["enemy_type"] == memory.content["enemy_type"]:
                    relevance += 0.4
        
        # Эмоциональная релевантность
        if "emotional_state" in context:
            emotional_similarity = 1.0 - abs(
                context["emotional_state"] - memory.emotional_impact
            )
            relevance += emotional_similarity * 0.3
        
        return min(1.0, relevance)
    
    def _apply_combat_memory_influence(self, memory: GenerationalMemory, 
                                      action_weights: Dict[str, float], 
                                      influence: float):
        """Применение влияния боевого опыта"""
        content = memory.content
        
        if content.get("successful_action"):
            action = content["successful_action"]
            if action in action_weights:
                action_weights[action] += influence * 0.5
        
        if content.get("failed_action"):
            action = content["failed_action"]
            if action in action_weights:
                action_weights[action] -= influence * 0.3
    
    def _apply_enemy_pattern_influence(self, memory: GenerationalMemory, 
                                     action_weights: Dict[str, float], 
                                     influence: float):
        """Применение влияния паттернов врагов"""
        content = memory.content
        
        if content.get("effective_counter"):
            action = content["effective_counter"]
            if action in action_weights:
                action_weights[action] += influence * 0.6
    
    def _apply_emotional_trauma_influence(self, memory: GenerationalMemory, 
                                        action_weights: Dict[str, float], 
                                        influence: float):
        """Применение влияния эмоциональной травмы"""
        content = memory.content
        
        if content.get("dangerous_action"):
            action = content["dangerous_action"]
            if action in action_weights:
                action_weights[action] -= influence * 0.4
        
        # Травма увеличивает осторожность
        if "defend" in action_weights:
            action_weights["defend"] += influence * 0.3
    
    def _enforce_memory_limits(self, memory_type: MemoryType):
        """Ограничение количества воспоминаний по типу"""
        type_memories = [m for m in self.memories.values() 
                        if m.memory_type == memory_type]
        
        if len(type_memories) > self.max_memories_per_type:
            # Удаляем самые слабые воспоминания
            type_memories.sort(key=lambda x: x.intensity)
            memories_to_remove = type_memories[:len(type_memories) - self.max_memories_per_type]
            
            for memory in memories_to_remove:
                del self.memories[memory.id]
    
    def _attempt_memory_fusion(self, new_memory_id: str):
        """Попытка слияния воспоминаний"""
        new_memory = self.memories[new_memory_id]
        
        for existing_memory in self.memories.values():
            if existing_memory.id == new_memory_id:
                continue
            
            if existing_memory.memory_type != new_memory.memory_type:
                continue
            
            # Проверка схожести
            similarity = self._calculate_memory_similarity(new_memory, existing_memory)
            
            if similarity > self.memory_fusion_threshold:
                self._fuse_memories(new_memory, existing_memory)
                break
    
    def _calculate_memory_similarity(self, memory1: GenerationalMemory, 
                                   memory2: GenerationalMemory) -> float:
        """Расчёт схожести между воспоминаниями"""
        similarity = 0.0
        
        # Схожесть по типу
        if memory1.memory_type == memory2.memory_type:
            similarity += 0.3
        
        # Схожесть по содержанию
        content1 = memory1.content
        content2 = memory2.content
        
        common_keys = set(content1.keys()) & set(content2.keys())
        if common_keys:
            content_similarity = sum(
                1.0 for key in common_keys 
                if content1[key] == content2[key]
            ) / len(common_keys)
            similarity += content_similarity * 0.4
        
        # Временная схожесть
        time_diff = abs(memory1.created_at - memory2.created_at)
        if time_diff < 3600:  # В пределах часа
            similarity += 0.3
        
        return similarity
    
    def _fuse_memories(self, memory1: GenerationalMemory, memory2: GenerationalMemory):
        """Слияние двух воспоминаний"""
        # Создание усиленного воспоминания
        fused_content = {**memory1.content, **memory2.content}
        fused_intensity = max(memory1.intensity, memory2.intensity) * 1.2
        fused_emotional_impact = (memory1.emotional_impact + memory2.emotional_impact) / 2
        
        fused_memory = GenerationalMemory(
            id=str(uuid.uuid4()),
            memory_type=memory1.memory_type,
            content=fused_content,
            intensity=min(1.0, fused_intensity),
            generation=self.current_generation,
            created_at=time.time(),
            last_accessed=time.time(),
            access_count=memory1.access_count + memory2.access_count,
            emotional_impact=fused_emotional_impact,
            survival_value=max(memory1.survival_value, memory2.survival_value)
        )
        
        # Замена старых воспоминаний
        self.memories[fused_memory.id] = fused_memory
        del self.memories[memory1.id]
        del self.memories[memory2.id]
        
        logger.debug(f"Воспоминания объединены: {memory1.id} + {memory2.id} -> {fused_memory.id}")
    
    def _evolve_memories(self, survival_rate: float):
        """Эволюция воспоминаний между поколениями"""
        for memory in list(self.memories.values()):
            # Усиление важных воспоминаний
            if memory.survival_value > 0.8:
                memory.intensity = min(1.0, memory.intensity * 1.1)
            
            # Ослабление слабых воспоминаний
            elif memory.intensity < 0.3:
                memory.intensity *= 0.9
            
            # Случайные мутации
            if random.random() < 0.1:
                mutation = random.choice([-0.1, 0.1])
                memory.intensity = max(0.0, min(1.0, memory.intensity + mutation))
    
    def _create_memory_clusters(self):
        """Создание кластеров связанных воспоминаний"""
        # Группировка по типам
        type_groups = {}
        for memory in self.memories.values():
            if memory.memory_type not in type_groups:
                type_groups[memory.memory_type] = []
            type_groups[memory.memory_type].append(memory)
        
        # Создание кластеров для групп с достаточным количеством воспоминаний
        for memory_type, memories in type_groups.items():
            if len(memories) >= 3:
                cluster_id = str(uuid.uuid4())
                cluster = MemoryCluster(
                    id=cluster_id,
                    theme=memory_type.value,
                    memories=[m.id for m in memories],
                    strength=sum(m.intensity for m in memories) / len(memories),
                    influence_radius=len(memories) * 0.1,
                    emotional_resonance=sum(m.emotional_impact for m in memories) / len(memories)
                )
                self.memory_clusters[cluster_id] = cluster
    
    def _save_generation_data(self):
        """Сохранение данных поколения"""
        generation_file = self.save_directory / f"generation_{self.current_generation}.json"
        
        # Преобразование в сериализуемый формат
        serializable_memories = []
        for memory in self.memories.values():
            memory_dict = {}
            for key, value in memory.__dict__.items():
                if isinstance(value, (int, float, str, bool, list, dict)):
                    memory_dict[key] = value
                else:
                    memory_dict[key] = str(value)
            serializable_memories.append(memory_dict)
        
        serializable_clusters = []
        for cluster in self.memory_clusters.values():
            cluster_dict = {}
            for key, value in cluster.__dict__.items():
                if isinstance(value, (int, float, str, bool, list, dict)):
                    cluster_dict[key] = value
                else:
                    cluster_dict[key] = str(value)
            serializable_clusters.append(cluster_dict)
        
        generation_data = {
            "generation": self.current_generation,
            "memories": serializable_memories,
            "clusters": serializable_clusters,
            "timestamp": time.time()
        }
        
        with open(generation_file, 'w', encoding='utf-8') as f:
            json.dump(generation_data, f, indent=2, ensure_ascii=False)
    
    def _save_generational_memory(self):
        """Сохранение всей системы памяти"""
        memory_file = self.save_directory / "generational_memory.json"
        
        memory_data = {
            "current_generation": self.current_generation,
            "memory_ids": list(self.memories.keys()),
            "cluster_ids": list(self.memory_clusters.keys()),
            "last_updated": time.time()
        }
        
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, indent=2, ensure_ascii=False)
    
    def _load_generational_memory(self):
        """Загрузка системы памяти"""
        memory_file = self.save_directory / "generational_memory.json"
        
        if memory_file.exists():
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                
                self.current_generation = memory_data.get("current_generation", 1)
                
                # Загрузка последнего поколения
                generation_file = self.save_directory / f"generation_{self.current_generation}.json"
                if generation_file.exists():
                    with open(generation_file, 'r', encoding='utf-8') as f:
                        generation_data = json.load(f)
                    
                    # Восстановление воспоминаний
                    for memory_dict in generation_data.get("memories", []):
                        memory = GenerationalMemory(**memory_dict)
                        self.memories[memory.id] = memory
                    
                    # Восстановление кластеров
                    for cluster_dict in generation_data.get("clusters", []):
                        cluster = MemoryCluster(**cluster_dict)
                        self.memory_clusters[cluster.id] = cluster
                
                logger.info(f"Загружена память поколения {self.current_generation}")
                
            except Exception as e:
                logger.error(f"Ошибка загрузки памяти: {e}")
                logger.info("Создана новая система памяти")
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Получение статистики системы памяти"""
        return {
            "total_memories": len(self.memories),
            "current_generation": self.current_generation,
            "memory_types": {mem_type.value: len([m for m in self.memories.values() 
                                                 if m.memory_type == mem_type])
                            for mem_type in MemoryType},
            "total_clusters": len(self.memory_clusters),
            "average_intensity": sum(m.intensity for m in self.memories.values()) / max(1, len(self.memories)),
            "total_emotional_impact": sum(m.emotional_impact for m in self.memories.values())
        }
