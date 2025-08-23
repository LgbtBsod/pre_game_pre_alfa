#!/usr/bin/env python3
"""
Система рисков и наград из Spelunky и Hades.
Управляет динамическим балансом сложности и вознаграждений.
"""

import time
import random
import math
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Уровни риска"""
    MINIMAL = "minimal"      # 0.5x награды, 0.7x сложность
    LOW = "low"              # 0.8x награды, 0.9x сложность
    NORMAL = "normal"        # 1.0x награды, 1.0x сложность
    HIGH = "high"            # 1.3x награды, 1.2x сложность
    EXTREME = "extreme"      # 1.8x награды, 1.5x сложность
    NIGHTMARE = "nightmare"  # 2.5x награды, 2.0x сложность


class RiskCategory(Enum):
    """Категории рисков"""
    COMBAT = "combat"              # Боевые риски
    EXPLORATION = "exploration"    # Исследовательские риски
    TIME_PRESSURE = "time_pressure" # Временные ограничения
    RESOURCE_SCARCITY = "resource_scarcity" # Нехватка ресурсов
    ENVIRONMENTAL = "environmental" # Экологические опасности
    CURSE = "curse"               # Проклятия
    SACRIFICE = "sacrifice"       # Жертвоприношения
    GAMBLE = "gamble"             # Азартные игры


@dataclass
class RiskFactor:
    """Фактор риска"""
    factor_id: str
    name: str
    description: str
    category: RiskCategory
    risk_multiplier: float  # Множитель риска (1.0 = нейтральный)
    reward_multiplier: float  # Множитель награды
    duration: float = -1  # Длительность в секундах (-1 = постоянный)
    start_time: float = field(default_factory=time.time)
    stacks: int = 1
    
    # Условия активации и деактивации
    activation_conditions: Dict[str, Any] = field(default_factory=dict)
    deactivation_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Дополнительные эффекты
    special_effects: List[str] = field(default_factory=list)
    
    def is_expired(self) -> bool:
        """Проверка истечения фактора риска"""
        if self.duration < 0:
            return False
        return time.time() - self.start_time >= self.duration
    
    def get_effective_risk_multiplier(self) -> float:
        """Получение эффективного множителя риска с учётом стаков"""
        base_multiplier = self.risk_multiplier
        
        if self.stacks > 1:
            # Убывающая отдача от стаков
            stack_bonus = (self.stacks - 1) * 0.2
            return base_multiplier * (1.0 + stack_bonus)
        
        return base_multiplier
    
    def get_effective_reward_multiplier(self) -> float:
        """Получение эффективного множителя награды с учётом стаков"""
        base_multiplier = self.reward_multiplier
        
        if self.stacks > 1:
            # Убывающая отдача от стаков
            stack_bonus = (self.stacks - 1) * 0.15
            return base_multiplier * (1.0 + stack_bonus)
        
        return base_multiplier


@dataclass
class RiskRewardEvent:
    """Событие риска и награды"""
    event_id: str
    event_type: str
    risk_level: RiskLevel
    potential_rewards: List[Dict[str, Any]]
    risk_factors: List[str]  # ID факторов риска
    timestamp: float = field(default_factory=time.time)
    completed: bool = False
    success: bool = False
    actual_rewards: List[Dict[str, Any]] = field(default_factory=list)


class RiskRewardSystem:
    """Система рисков и наград"""
    
    def __init__(self, memory_system, curse_blessing_system):
        self.memory_system = memory_system
        self.curse_blessing_system = curse_blessing_system
        
        # Активные факторы риска
        self.active_risk_factors: Dict[str, RiskFactor] = {}
        
        # История событий
        self.event_history: List[RiskRewardEvent] = []
        
        # Статистика
        self.total_risks_taken = 0
        self.total_rewards_earned = 0
        self.successful_risk_events = 0
        self.failed_risk_events = 0
        
        # Конфигурация
        self._initialize_risk_configs()
        
        # Текущий уровень риска
        self._current_risk_level = RiskLevel.NORMAL
        
        logger.info("🎯 Система рисков и наград инициализирована")
    
    def calculate_current_risk(self) -> float:
        """Расчёт текущего уровня риска"""
        if not self.active_risk_factors:
            return 1.0
        
        total_risk = 1.0
        
        for factor in self.active_risk_factors.values():
            total_risk *= factor.get_effective_risk_multiplier()
        
        return total_risk
    
    def calculate_reward_multiplier(self) -> float:
        """Расчёт множителя награды"""
        if not self.active_risk_factors:
            return 1.0
        
        total_reward = 1.0
        
        for factor in self.active_risk_factors.values():
            total_reward *= factor.get_effective_reward_multiplier()
        
        return total_reward
    
    def add_risk_factor(self, name: str, description: str = None, 
                       multiplier: float = 1.2, duration: float = 300.0,
                       category: RiskCategory = RiskCategory.COMBAT) -> str:
        """Добавление фактора риска"""
        factor_id = str(uuid.uuid4())
        
        factor = RiskFactor(
            factor_id=factor_id,
            name=name,
            description=description or f"Фактор риска: {name}",
            category=category,
            risk_multiplier=multiplier,
            reward_multiplier=1.0,
            duration=duration
        )
        
        self.active_risk_factors[factor_id] = factor
        self._update_risk_level()
        
        logger.info(f"Добавлен фактор риска: {name} (множитель: {multiplier})")
        return factor_id
    
    def remove_risk_factor(self, factor_id: str):
        """Удаление фактора риска"""
        if factor_id in self.active_risk_factors:
            del self.active_risk_factors[factor_id]
            self._update_risk_level()
            logger.info(f"Удалён фактор риска: {factor_id}")
    
    def trigger_risk_event(self, event_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Активация события риска"""
        # Поиск подходящего события
        suitable_events = self._find_suitable_events(event_type)
        
        if not suitable_events:
            return {"success": False, "reason": "No suitable events"}
        
        # Выбор случайного события
        event = random.choice(suitable_events)
        
        # Расчёт шанса успеха
        base_success_rate = 0.5
        risk_modifier = self.calculate_current_risk()
        final_success_rate = max(0.1, min(0.9, base_success_rate / risk_modifier))
        
        # Определение результата
        success = random.random() < final_success_rate
        
        # Расчёт наград
        if success:
            reward_multiplier = self.calculate_reward_multiplier()
            enhanced_rewards = []
            
            for reward in event.potential_rewards:
                enhanced_reward = self._enhance_reward(reward, reward_multiplier)
                enhanced_rewards.append(enhanced_reward)
            
            result = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "success": True,
                "rewards": enhanced_rewards,
                "risk_level": event.risk_level.value
            }
        else:
            result = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "success": False,
                "risk_level": event.risk_level.value
            }
        
        # Запись в память
        self._record_risk_event(event, result, context)
        
        # Обновление уровня риска
        self._update_risk_level()
        
        return result
    
    def suggest_risk_opportunities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Предложение возможностей риска"""
        current_risk = self.calculate_current_risk()
        opportunities = []
        
        # Анализ памяти для поиска успешных паттернов
        successful_risks = self.memory_system.search_memories(
            memory_type=MemoryType.RISK_ASSESSMENT,
            search_criteria={"success": True}
        )
        
        # Предложения на основе успешного опыта
        for memory in successful_risks[-5:]:  # Последние 5 успешных рисков
            if memory.content.get("risk_level", 1.0) <= current_risk * 1.2:
                opportunities.append({
                    "type": "memory_based",
                    "description": f"Повторить успешную стратегию: {memory.content.get('event_name', 'Unknown')}",
                    "expected_success": memory.content.get("success_rate", 0.5) * 1.1,
                    "potential_reward": memory.content.get("reward_value", 1.0) * self.calculate_reward_multiplier()
                })
        
        # Предложения на основе текущих условий
        if current_risk > 2.0:
            opportunities.append({
                "type": "high_risk_high_reward",
                "description": "Экстремальный вызов с легендарными наградами",
                "expected_success": 0.3,
                "potential_reward": 5.0 * self.calculate_reward_multiplier()
            })
        
        if len(self.active_risk_factors) == 0:
            opportunities.append({
                "type": "safe_exploration",
                "description": "Безопасное исследование с гарантированными наградами",
                "expected_success": 0.9,
                "potential_reward": 1.2 * self.calculate_reward_multiplier()
            })
        
        return opportunities
    
    def _initialize_risk_configs(self):
        """Инициализация конфигураций рисков"""
        self.risk_events = [
            RiskRewardEvent(
                event_id="cursed_treasure",
                event_type="treasure",
                risk_level=RiskLevel.HIGH,
                potential_rewards=[{"type": "legendary_item", "value": 1000}],
                risk_factors=["corruption", "curse_application"]
            ),
            RiskRewardEvent(
                event_id="boss_challenge",
                event_type="boss",
                risk_level=RiskLevel.EXTREME,
                potential_rewards=[{"type": "boss_essence", "value": 2000}],
                risk_factors=["mortal_danger", "equipment_damage"]
            ),
            RiskRewardEvent(
                event_id="dimensional_rift",
                event_type="rift",
                risk_level=RiskLevel.NIGHTMARE,
                potential_rewards=[{"type": "dimensional_artifact", "value": 1500}],
                risk_factors=["dimensional_instability", "reality_distortion"]
            ),
            RiskRewardEvent(
                event_id="evolution_gamble",
                event_type="gamble",
                risk_level=RiskLevel.HIGH,
                potential_rewards=[{"type": "rapid_evolution", "value": 800}],
                risk_factors=["evolution_instability", "genetic_damage"]
            )
        ]
    
    def _find_suitable_events(self, event_type: str) -> List[RiskRewardEvent]:
        """Поиск подходящих событий"""
        suitable_events = []
        
        for event in self.risk_events:
            # Фильтрация по типу события
            if event_type != "any" and event_type not in event.event_type:
                continue
            
            # Проверка уровня риска
            if event.risk_level.value <= self._current_risk_level.value:
                suitable_events.append(event)
        
        return suitable_events
    
    def _risk_level_to_value(self, risk_level: RiskLevel) -> float:
        """Преобразование уровня риска в числовое значение"""
        mapping = {
            RiskLevel.MINIMAL: 0.5,
            RiskLevel.LOW: 0.8,
            RiskLevel.NORMAL: 1.0,
            RiskLevel.HIGH: 1.3,
            RiskLevel.EXTREME: 1.8,
            RiskLevel.NIGHTMARE: 2.5
        }
        return mapping.get(risk_level, 1.0)
    
    def _enhance_reward(self, reward: Dict[str, Any], multiplier: float) -> Dict[str, Any]:
        """Усиление награды"""
        base_value = reward.get("value", 100)
        enhanced_value = base_value * multiplier
        
        # Определение уровня награды
        if enhanced_value < 200:
            tier = "common"
        elif enhanced_value < 500:
            tier = "uncommon"
        elif enhanced_value < 1000:
            tier = "rare"
        elif enhanced_value < 2000:
            tier = "epic"
        elif enhanced_value < 5000:
            tier = "legendary"
        else:
            tier = "mythic"
        
        return {
            "type": reward["type"],
            "tier": tier,
            "value": enhanced_value,
            "original_value": base_value,
            "multiplier": multiplier
        }
    
    def _record_risk_event(self, event: RiskRewardEvent, result: Dict[str, Any], 
                          context: Dict[str, Any]):
        """Запись события риска в память"""
        try:
            memory_content = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "success": result["success"],
                "risk_level": event.risk_level.value,
                "context": context
            }
            
            # Добавляем в историю
            self.event_history.append(event)
            
        except Exception as e:
            logger.error(f"Ошибка записи события риска: {e}")
    
    def _update_risk_level(self):
        """Обновление текущего уровня риска"""
        current_risk = self.calculate_current_risk()
        self._current_risk_level = self._calculate_risk_level(current_risk)
    
    def _calculate_risk_level(self, risk_value: float) -> RiskLevel:
        """Расчёт уровня риска по значению"""
        if risk_value < 0.8:
            return RiskLevel.MINIMAL
        elif risk_value < 1.1:
            return RiskLevel.LOW
        elif risk_value < 1.3:
            return RiskLevel.NORMAL
        elif risk_value < 1.7:
            return RiskLevel.HIGH
        elif risk_value < 2.2:
            return RiskLevel.EXTREME
        else:
            return RiskLevel.NIGHTMARE
    
    def get_risk_statistics(self) -> Dict[str, Any]:
        """Получение статистики рисков"""
        return {
            "current_risk_level": self._current_risk_level.value,
            "risk_multiplier": self.calculate_current_risk(),
            "reward_multiplier": self.calculate_reward_multiplier(),
            "active_risk_factors": len(self.active_risk_factors),
            "total_events": len(self.event_history),
            "success_rate": sum(1 for event in self.event_history if event.success) / max(1, len(self.event_history)),
            "average_risk": sum(self._risk_level_to_value(event.risk_level) for event in self.event_history) / max(1, len(self.event_history))
        }
