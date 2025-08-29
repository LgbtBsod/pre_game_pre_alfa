#!/usr/bin/env python3
"""
Структуры данных для системы квестов
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from .quest_types import QuestType, QuestStatus, QuestRewardType, QuestDifficulty, QuestCategory

@dataclass
class QuestObjective:
    """Цель квеста"""
    objective_id: str
    description: str
    objective_type: str  # kill, collect, reach, interact, etc.
    target: str  # target entity, item, location
    required_amount: int = 1
    current_amount: int = 0
    completed: bool = False
    optional: bool = False
    hidden: bool = False
    
    def update_progress(self, amount: int = 1) -> bool:
        """Обновить прогресс цели"""
        if not self.completed:
            self.current_amount = min(self.current_amount + amount, self.required_amount)
            if self.current_amount >= self.required_amount:
                self.completed = True
                return True
        return False
    
    def get_progress_percentage(self) -> float:
        """Получить процент выполнения"""
        if self.required_amount == 0:
            return 100.0
        return min(100.0, (self.current_amount / self.required_amount) * 100.0)

@dataclass
class QuestReward:
    """Награда за квест"""
    reward_type: QuestRewardType
    reward_id: str
    amount: int = 1
    quality: float = 1.0
    rarity: str = "common"
    description: str = ""
    special_effects: List[str] = field(default_factory=list)

@dataclass
class QuestPrerequisite:
    """Предварительные требования для квеста"""
    prerequisite_type: str  # level, quest, item, reputation, etc.
    target: str
    required_value: Any
    current_value: Any = None
    met: bool = False
    
    def check_prerequisite(self, current_value: Any) -> bool:
        """Проверить выполнение предварительного требования"""
        self.current_value = current_value
        if isinstance(self.required_value, (int, float)):
            self.met = current_value >= self.required_value
        else:
            self.met = current_value == self.required_value
        return self.met

@dataclass
class Quest:
    """Квест"""
    quest_id: str
    title: str
    description: str
    quest_type: QuestType
    category: QuestCategory
    difficulty: QuestDifficulty
    status: QuestStatus = QuestStatus.NOT_STARTED
    
    # Цели и награды
    objectives: List[QuestObjective] = field(default_factory=list)
    rewards: List[QuestReward] = field(default_factory=list)
    prerequisites: List[QuestPrerequisite] = field(default_factory=list)
    
    # Временные ограничения
    time_limit: Optional[float] = None  # в секундах
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    # Дополнительная информация
    quest_giver: Optional[str] = None
    quest_target: Optional[str] = None
    location: Optional[str] = None
    level_requirement: int = 1
    
    # Флаги
    repeatable: bool = False
    hidden: bool = False
    epic: bool = False
    chain_quest: bool = False
    next_quest_id: Optional[str] = None
    
    # Статистика
    completion_count: int = 0
    failure_count: int = 0
    average_completion_time: float = 0.0
    
    def start_quest(self) -> bool:
        """Начать квест"""
        if self.status == QuestStatus.NOT_STARTED and self._check_prerequisites():
            self.status = QuestStatus.IN_PROGRESS
            self.start_time = time.time()
            return True
        return False
    
    def complete_quest(self) -> bool:
        """Завершить квест"""
        if self.status == QuestStatus.IN_PROGRESS and self._check_objectives():
            self.status = QuestStatus.COMPLETED
            self.end_time = time.time()
            self.completion_count += 1
            if self.start_time and self.end_time:
                completion_time = self.end_time - self.start_time
                self.average_completion_time = (
                    (self.average_completion_time * (self.completion_count - 1) + completion_time) 
                    / self.completion_count
                )
            return True
        return False
    
    def fail_quest(self) -> bool:
        """Провалить квест"""
        if self.status == QuestStatus.IN_PROGRESS:
            self.status = QuestStatus.FAILED
            self.end_time = time.time()
            self.failure_count += 1
            return True
        return False
    
    def abandon_quest(self) -> bool:
        """Отказаться от квеста"""
        if self.status == QuestStatus.IN_PROGRESS:
            self.status = QuestStatus.ABANDONED
            self.end_time = time.time()
            return True
        return False
    
    def _check_prerequisites(self) -> bool:
        """Проверить предварительные требования"""
        return all(prereq.met for prereq in self.prerequisites)
    
    def _check_objectives(self) -> bool:
        """Проверить выполнение всех обязательных целей"""
        required_objectives = [obj for obj in self.objectives if not obj.optional]
        return all(obj.completed for obj in required_objectives)
    
    def get_progress_percentage(self) -> float:
        """Получить общий процент выполнения квеста"""
        if not self.objectives:
            return 100.0 if self.status == QuestStatus.COMPLETED else 0.0
        
        total_progress = sum(obj.get_progress_percentage() for obj in self.objectives)
        return total_progress / len(self.objectives)
    
    def is_expired(self) -> bool:
        """Проверить, истек ли срок квеста"""
        if self.time_limit and self.start_time:
            return time.time() - self.start_time > self.time_limit
        return False
    
    def get_remaining_time(self) -> Optional[float]:
        """Получить оставшееся время"""
        if self.time_limit and self.start_time:
            remaining = self.time_limit - (time.time() - self.start_time)
            return max(0, remaining)
        return None
