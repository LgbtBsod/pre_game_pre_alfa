#!/usr/bin/env python3
"""
Система рисков и наград.
Вдохновлено Risk of Rain 2, Vampire Survivors, Darkest Dungeon.
Управляет динамическим балансом сложности и наград.
"""

import random
import math
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from .generational_memory_system import GenerationalMemorySystem, MemoryType
from .curse_blessing_system import CurseBlessingSystem, CurseType, BlessingType

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Уровни риска"""
    SAFE = "safe"           # Безопасно
    LOW = "low"             # Низкий риск
    MODERATE = "moderate"   # Умеренный риск
    HIGH = "high"           # Высокий риск
    EXTREME = "extreme"     # Экстремальный риск
    SUICIDAL = "suicidal"   # Самоубийственный риск


class RewardTier(Enum):
    """Уровни наград"""
    COMMON = "common"       # Обычные
    UNCOMMON = "uncommon"   # Необычные
    RARE = "rare"           # Редкие
    EPIC = "epic"           # Эпические
    LEGENDARY = "legendary" # Легендарные
    MYTHIC = "mythic"       # Мифические


@dataclass
class RiskFactor:
    """Фактор риска"""
    name: str
    description: str
    risk_multiplier: float
    duration: float
    stacks: int
    max_stacks: int
    
    def get_effective_multiplier(self) -> float:
        """Получение эффективного множителя риска"""
        return 1.0 + (self.risk_multiplier - 1.0) * min(self.stacks, self.max_stacks)


@dataclass
class RiskRewardEvent:
    """Событие риска/награды"""
    id: str
    name: str
    description: str
    risk_level: RiskLevel
    potential_rewards: List[str]
    risk_factors: List[str]
    success_rate: float
    failure_consequences: List[str]
    memory_impact: float
    emotional_impact: float


class RiskRewardSystem:
    """Система рисков и наград"""
    
    def __init__(self, memory_system: GenerationalMemorySystem,
                 curse_blessing_system: CurseBlessingSystem):
        self.memory_system = memory_system
        self.curse_blessing_system = curse_blessing_system
        
        # Текущий уровень риска
        self.current_risk_level: float = 1.0
        
        # Активные факторы риска
        self.active_risk_factors: Dict[str, RiskFactor] = {}
        
        # Множитель наград
        self.reward_multiplier: float = 1.0
        
        # История рисков
        self.risk_history: List[Dict[str, Any]] = []
        
        # Система адаптивной сложности
        self.adaptive_difficulty = AdaptiveDifficultySystem()
        
        # Система испытаний
        self.challenge_system = ChallengeSystem()
        
        # Инициализация событий
        self._init_risk_reward_events()
        
        logger.info("Система рисков и наград инициализирована")
    
    def calculate_current_risk(self) -> float:
        """Расчёт текущего уровня риска"""
        base_risk = self.current_risk_level
        
        # Влияние активных факторов риска
        for factor in self.active_risk_factors.values():
            base_risk *= factor.get_effective_multiplier()
        
        # Влияние проклятий
        curse_effects = self.curse_blessing_system.get_active_effects_summary()
        curse_count = len(curse_effects.get("curses", []))
        if curse_count > 0:
            base_risk *= (1.0 + curse_count * 0.2)
        
        # Влияние времени (как в Risk of Rain 2)
        time_factor = min(2.0, 1.0 + time.time() / 3600)  # Увеличение со временем
        base_risk *= time_factor
        
        return base_risk
    
    def calculate_reward_multiplier(self) -> float:
        """Расчёт множителя наград"""
        risk_level = self.calculate_current_risk()
        
        # Базовый множитель на основе риска
        base_multiplier = 1.0 + math.log(risk_level) * 0.5
        
        # Влияние благословений
        blessing_effects = self.curse_blessing_system.get_active_effects_summary()
        blessing_count = len(blessing_effects.get("blessings", []))
        if blessing_count > 0:
            base_multiplier *= (1.0 + blessing_count * 0.1)
        
        # Влияние памяти поколений
        memory_stats = self.memory_system.get_memory_statistics()
        generation_bonus = 1.0 + (memory_stats["current_generation"] - 1) * 0.05
        base_multiplier *= generation_bonus
        
        return max(1.0, base_multiplier)
    
    def add_risk_factor(self, name: str, description: str, multiplier: float,
                       duration: float = -1, max_stacks: int = 5):
        """Добавление фактора риска"""
        if name in self.active_risk_factors:
            # Увеличиваем стаки существующего фактора
            factor = self.active_risk_factors[name]
            factor.stacks = min(factor.max_stacks, factor.stacks + 1)
        else:
            # Создаём новый фактор
            factor = RiskFactor(
                name=name,
                description=description,
                risk_multiplier=multiplier,
                duration=duration,
                stacks=1,
                max_stacks=max_stacks
            )
            self.active_risk_factors[name] = factor
        
        # Обновляем общий уровень риска
        self.current_risk_level = self.calculate_current_risk()
        
        logger.info(f"Добавлен фактор риска: {name} (множитель: {multiplier})")
    
    def remove_risk_factor(self, name: str):
        """Удаление фактора риска"""
        if name in self.active_risk_factors:
            del self.active_risk_factors[name]
            self.current_risk_level = self.calculate_current_risk()
            logger.info(f"Удалён фактор риска: {name}")
    
    def trigger_risk_event(self, event_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Активация события риска"""
        risk_level = self.calculate_current_risk()
        reward_multiplier = self.calculate_reward_multiplier()
        
        # Выбор события на основе уровня риска
        event = self._select_risk_event(risk_level, event_type)
        if not event:
            return {"success": False, "reason": "No suitable event found"}
        
        # Расчёт шанса успеха
        success_chance = event.success_rate / risk_level
        success = random.random() < success_chance
        
        result = {
            "event_id": event.id,
            "event_name": event.name,
            "success": success,
            "risk_level": risk_level,
            "reward_multiplier": reward_multiplier,
            "rewards": [],
            "consequences": []
        }
        
        if success:
            # Успешное событие - даём награды
            for reward in event.potential_rewards:
                enhanced_reward = self._enhance_reward(reward, reward_multiplier)
                result["rewards"].append(enhanced_reward)
        else:
            # Неудачное событие - применяем последствия
            for consequence in event.failure_consequences:
                applied_consequence = self._apply_consequence(consequence, risk_level)
                result["consequences"].append(applied_consequence)
        
        # Запись в память
        self._record_risk_event(event, result, context)
        
        # Обновление адаптивной сложности
        self.adaptive_difficulty.update_difficulty(success, risk_level)
        
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
    
    def _init_risk_reward_events(self):
        """Инициализация событий риска/награды"""
        self.risk_events = [
            RiskRewardEvent(
                id="cursed_treasure",
                name="Проклятое сокровище",
                description="Сундук излучает тёмную ауру. Открыть?",
                risk_level=RiskLevel.HIGH,
                potential_rewards=["legendary_item", "curse_immunity", "dark_power"],
                risk_factors=["corruption", "curse_application"],
                success_rate=0.4,
                failure_consequences=["apply_curse", "lose_health", "corruption_spread"],
                memory_impact=0.8,
                emotional_impact=0.6
            ),
            RiskRewardEvent(
                id="boss_challenge",
                name="Вызов боссу",
                description="Бросить вызов могущественному боссу",
                risk_level=RiskLevel.EXTREME,
                potential_rewards=["boss_essence", "evolution_catalyst", "legendary_weapon"],
                risk_factors=["mortal_danger", "equipment_damage"],
                success_rate=0.2,
                failure_consequences=["severe_injury", "equipment_loss", "memory_trauma"],
                memory_impact=1.0,
                emotional_impact=0.9
            ),
            RiskRewardEvent(
                id="dimensional_rift",
                name="Измерительный разлом",
                description="Портал в неизвестное измерение",
                risk_level=RiskLevel.SUICIDAL,
                potential_rewards=["dimensional_artifact", "reality_shard", "cosmic_knowledge"],
                risk_factors=["dimensional_instability", "reality_distortion"],
                success_rate=0.1,
                failure_consequences=["dimensional_trap", "reality_fracture", "existence_threat"],
                memory_impact=1.2,
                emotional_impact=1.0
            ),
            RiskRewardEvent(
                id="evolution_gamble",
                name="Эволюционная азартная игра",
                description="Рискнуть текущей эволюцией ради большего прогресса",
                risk_level=RiskLevel.MODERATE,
                potential_rewards=["rapid_evolution", "genetic_stability", "adaptation_boost"],
                risk_factors=["evolution_instability", "genetic_damage"],
                success_rate=0.6,
                failure_consequences=["evolution_regression", "genetic_corruption", "adaptation_loss"],
                memory_impact=0.7,
                emotional_impact=0.5
            )
        ]
    
    def _select_risk_event(self, risk_level: float, event_type: str) -> Optional[RiskRewardEvent]:
        """Выбор события риска"""
        suitable_events = []
        
        for event in self.risk_events:
            # Фильтрация по типу события
            if event_type != "any" and event_type not in event.id:
                continue
            
            # Фильтрация по уровню риска
            event_risk_value = self._risk_level_to_value(event.risk_level)
            if abs(event_risk_value - risk_level) <= 1.0:
                suitable_events.append(event)
        
        return random.choice(suitable_events) if suitable_events else None
    
    def _risk_level_to_value(self, risk_level: RiskLevel) -> float:
        """Преобразование уровня риска в числовое значение"""
        mapping = {
            RiskLevel.SAFE: 0.5,
            RiskLevel.LOW: 1.0,
            RiskLevel.MODERATE: 2.0,
            RiskLevel.HIGH: 3.0,
            RiskLevel.EXTREME: 4.0,
            RiskLevel.SUICIDAL: 5.0
        }
        return mapping.get(risk_level, 1.0)
    
    def _enhance_reward(self, reward: str, multiplier: float) -> Dict[str, Any]:
        """Усиление награды"""
        base_value = 100  # Базовая ценность
        enhanced_value = base_value * multiplier
        
        # Определение уровня награды
        if enhanced_value >= 1000:
            tier = RewardTier.MYTHIC
        elif enhanced_value >= 500:
            tier = RewardTier.LEGENDARY
        elif enhanced_value >= 250:
            tier = RewardTier.EPIC
        elif enhanced_value >= 125:
            tier = RewardTier.RARE
        elif enhanced_value >= 75:
            tier = RewardTier.UNCOMMON
        else:
            tier = RewardTier.COMMON
        
        return {
            "type": reward,
            "tier": tier.value,
            "value": enhanced_value,
            "multiplier": multiplier
        }
    
    def _apply_consequence(self, consequence: str, risk_level: float) -> Dict[str, Any]:
        """Применение последствия"""
        severity = min(1.0, risk_level / 5.0)  # Нормализация к 0-1
        
        consequence_effects = {
            "apply_curse": {
                "action": "apply_random_curse",
                "intensity": severity,
                "description": f"Применено случайное проклятие (интенсивность: {severity:.1f})"
            },
            "lose_health": {
                "action": "health_damage",
                "value": severity * 50,
                "description": f"Потеря {severity * 50:.0f} здоровья"
            },
            "equipment_damage": {
                "action": "equipment_degradation",
                "value": severity * 0.3,
                "description": f"Повреждение снаряжения ({severity * 30:.0f}%)"
            },
            "memory_trauma": {
                "action": "memory_loss",
                "value": severity * 0.2,
                "description": f"Травматическая потеря памяти ({severity * 20:.0f}%)"
            }
        }
        
        return consequence_effects.get(consequence, {
            "action": "unknown",
            "description": f"Неизвестное последствие: {consequence}"
        })
    
    def _record_risk_event(self, event: RiskRewardEvent, result: Dict[str, Any],
                          context: Dict[str, Any]):
        """Запись события риска в память"""
        try:
            memory_content = {
                "event_id": event.id,
                "event_name": event.name,
                "success": result["success"],
                "risk_level": result["risk_level"],
                "reward_multiplier": result["reward_multiplier"],
                "rewards_count": len(result["rewards"]),
                "consequences_count": len(result["consequences"]),
                "context": context,
                "timestamp": time.time()
            }
            
            self.memory_system.add_memory(
                memory_type=MemoryType.RISK_ASSESSMENT,
                content=memory_content,
                intensity=event.memory_impact,
                emotional_impact=event.emotional_impact
            )
            
            # Добавляем в историю
            self.risk_history.append(memory_content)
            
        except Exception as e:
            logger.error(f"Ошибка записи события риска в память: {e}")
    
    def get_risk_statistics(self) -> Dict[str, Any]:
        """Получение статистики рисков"""
        return {
            "current_risk_level": self.calculate_current_risk(),
            "reward_multiplier": self.calculate_reward_multiplier(),
            "active_risk_factors": len(self.active_risk_factors),
            "total_events": len(self.risk_history),
            "success_rate": sum(1 for event in self.risk_history if event.get("success", False)) / max(1, len(self.risk_history)),
            "average_risk": sum(event.get("risk_level", 1.0) for event in self.risk_history) / max(1, len(self.risk_history))
        }


class AdaptiveDifficultySystem:
    """Система адаптивной сложности"""
    
    def __init__(self):
        self.difficulty_level = 1.0
        self.success_history = []
        self.adjustment_rate = 0.1
    
    def update_difficulty(self, success: bool, risk_level: float):
        """Обновление сложности на основе результатов"""
        self.success_history.append(success)
        
        # Ограничиваем историю последними 20 событиями
        if len(self.success_history) > 20:
            self.success_history.pop(0)
        
        # Расчёт текущего коэффициента успеха
        if len(self.success_history) >= 5:
            success_rate = sum(self.success_history[-10:]) / min(10, len(self.success_history))
            
            # Корректировка сложности
            if success_rate > 0.7:  # Слишком легко
                self.difficulty_level += self.adjustment_rate
            elif success_rate < 0.3:  # Слишком сложно
                self.difficulty_level -= self.adjustment_rate
            
            # Ограничиваем диапазон сложности
            self.difficulty_level = max(0.5, min(3.0, self.difficulty_level))


class ChallengeSystem:
    """Система испытаний"""
    
    def __init__(self):
        self.active_challenges = []
        self.completed_challenges = []
    
    def generate_challenge(self, risk_level: float) -> Dict[str, Any]:
        """Генерация испытания"""
        challenges = [
            {
                "name": "Выживание без лечения",
                "description": "Пройди уровень не используя лечение",
                "risk_bonus": 1.5,
                "reward_bonus": 2.0,
                "conditions": ["no_healing"]
            },
            {
                "name": "Скоростной забег",
                "description": "Завершить за ограниченное время",
                "risk_bonus": 1.3,
                "reward_bonus": 1.8,
                "conditions": ["time_limit"]
            },
            {
                "name": "Минималист",
                "description": "Использовать только базовое оружие",
                "risk_bonus": 1.4,
                "reward_bonus": 1.9,
                "conditions": ["basic_weapon_only"]
            }
        ]
        
        suitable_challenges = [c for c in challenges if c["risk_bonus"] <= risk_level]
        return random.choice(suitable_challenges) if suitable_challenges else challenges[0]
