#!/usr/bin/env python3
"""
Расширенная система боевого обучения ИИ.
Вдохновлено механиками из Hades, Returnal, Dark Souls.
Включает адаптивные паттерны атак, контратаки и эволюцию тактик.
"""

import random
import math
import time
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np

from .generational_memory_system import GenerationalMemorySystem, MemoryType
from .emotional_ai_influence import EmotionalAIInfluenceSystem

logger = logging.getLogger(__name__)


class CombatPhase(Enum):
    """Фазы боя"""
    APPROACH = "approach"           # Приближение к цели
    ENGAGE = "engage"               # Вступление в бой
    COMBAT = "combat"               # Активный бой
    COUNTER = "counter"             # Контратака
    RETREAT = "retreat"             # Отступление
    RECOVER = "recover"             # Восстановление
    ADAPT = "adapt"                 # Адаптация тактики


class CombatTactic(Enum):
    """Тактики боя"""
    AGGRESSIVE_RUSH = "aggressive_rush"         # Агрессивный натиск
    DEFENSIVE_STANCE = "defensive_stance"       # Оборонительная стойка
    MOBILE_HARASSMENT = "mobile_harassment"     # Мобильное преследование
    COUNTER_ATTACK = "counter_attack"           # Контратака
    TRAP_AND_AMBUSH = "trap_and_ambush"        # Ловушка и засада
    PSYCHOLOGICAL_WARFARE = "psychological_warfare"  # Психологическая война
    ADAPTIVE_EVOLUTION = "adaptive_evolution"   # Адаптивная эволюция


class VulnerabilityType(Enum):
    """Типы уязвимостей"""
    PHYSICAL = "physical"           # Физическая уязвимость
    ELEMENTAL = "elemental"        # Элементальная уязвимость
    TEMPORAL = "temporal"          # Временная уязвимость
    POSITIONAL = "positional"      # Позиционная уязвимость
    PSYCHOLOGICAL = "psychological" # Психологическая уязвимость


@dataclass
class CombatPattern:
    """Боевой паттерн"""
    id: str
    name: str
    actions: List[str]
    success_rate: float
    usage_count: int
    last_used: float
    adaptation_factor: float
    emotional_triggers: List[str]
    
    def update_success_rate(self, success: bool):
        """Обновление показателя успешности"""
        if success:
            self.success_rate = min(1.0, self.success_rate + 0.1)
        else:
            self.success_rate = max(0.0, self.success_rate - 0.15)
        
        self.usage_count += 1
        self.last_used = time.time()


@dataclass
class CombatContext:
    """Контекст боя"""
    entity_id: str
    target_id: str
    current_phase: CombatPhase
    active_tactic: CombatTactic
    health_percent: float
    stamina_percent: float
    distance_to_target: float
    target_health_percent: float
    environmental_hazards: List[str]
    available_cover: List[str]
    emotional_state: str
    combat_duration: float
    pattern_success_history: List[bool]
    
    def get_combat_intensity(self) -> float:
        """Получение интенсивности боя"""
        return min(1.0, (1.0 - self.health_percent) + (1.0 - self.stamina_percent) * 0.5)


@dataclass
class CombatDecision:
    """Боевое решение"""
    action: str
    target: Optional[str]
    tactic: CombatTactic
    confidence: float
    reasoning: str
    emotional_influence: float
    memory_influence: float
    adaptation_level: float


class EnhancedCombatLearningSystem:
    """Расширенная система боевого обучения"""
    
    def __init__(self, memory_system: GenerationalMemorySystem, 
                 emotional_system: EmotionalAIInfluenceSystem):
        self.memory_system = memory_system
        self.emotional_system = emotional_system
        
        # Боевые паттерны
        self.combat_patterns: Dict[str, CombatPattern] = {}
        
        # История боев
        self.combat_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Адаптивные тактики
        self.adaptive_tactics: Dict[str, Dict[str, float]] = {}
        
        # Система контратак
        self.counter_attack_system = CounterAttackSystem()
        
        # Система эволюции тактик
        self.tactic_evolution_system = TacticEvolutionSystem()
        
        # Инициализация базовых паттернов
        self._init_base_combat_patterns()
        
        logger.info("Расширенная система боевого обучения инициализирована")
    
    def make_combat_decision(self, entity_id: str, context: CombatContext) -> CombatDecision:
        """Принятие боевого решения"""
        # Анализ текущей ситуации
        situation_analysis = self._analyze_combat_situation(context)
        
        # Выбор тактики
        selected_tactic = self._select_combat_tactic(entity_id, context, situation_analysis)
        
        # Выбор действия
        selected_action = self._select_combat_action(entity_id, context, selected_tactic)
        
        # Расчёт уверенности
        confidence = self._calculate_decision_confidence(context, selected_action, selected_tactic)
        
        # Влияние эмоций и памяти
        emotional_influence = self._get_emotional_influence(entity_id, context)
        memory_influence = self._get_memory_influence(entity_id, context)
        
        # Уровень адаптации
        adaptation_level = self._get_adaptation_level(entity_id, context)
        
        return CombatDecision(
            action=selected_action,
            target=context.target_id,
            tactic=selected_tactic,
            confidence=confidence,
            reasoning=situation_analysis["reasoning"],
            emotional_influence=emotional_influence,
            memory_influence=memory_influence,
            adaptation_level=adaptation_level
        )
    
    def learn_from_combat_result(self, entity_id: str, context: CombatContext, 
                                decision: CombatDecision, result: Dict[str, Any]):
        """Обучение на основе результата боя"""
        # Обновление паттерна
        if decision.action in self.combat_patterns:
            pattern = self.combat_patterns[decision.action]
        success = result.get("success", False)
            pattern.update_success_rate(success)
        
        # Запись в память поколений
        combat_memory = {
            "context": {
                "phase": context.current_phase.value,
                "tactic": context.active_tactic.value,
                "health_percent": context.health_percent,
                "target_health_percent": context.target_health_percent,
                "distance": context.distance_to_target,
                "duration": context.combat_duration
            },
            "decision": {
            "action": decision.action,
                "tactic": decision.tactic.value,
                "confidence": decision.confidence
            },
            "result": result,
            "timestamp": time.time()
        }
        
        self.memory_system.add_memory(
            memory_type=MemoryType.COMBAT_EXPERIENCE,
            content=combat_memory,
            intensity=context.get_combat_intensity(),
            emotional_impact=decision.emotional_influence
        )
        
        # Обновление адаптивных тактик
        self._update_adaptive_tactics(entity_id, context, decision, result)
        
        # Эволюция тактик
        self.tactic_evolution_system.evolve_tactics(entity_id, context, result)
        
        logger.debug(f"Результат боя записан для {entity_id}: {result}")
    
    def _analyze_combat_situation(self, context: CombatContext) -> Dict[str, Any]:
        """Анализ боевой ситуации"""
        analysis = {
            "threat_level": "low",
            "advantage": "neutral",
            "recommended_phase": context.current_phase,
            "reasoning": []
        }
        
        # Оценка угрозы
        threat_factors = []
        if context.health_percent < 0.3:
            threat_factors.append("critical_health")
        if context.stamina_percent < 0.2:
            threat_factors.append("low_stamina")
        if context.target_health_percent > 0.8:
            threat_factors.append("strong_enemy")
        
        if len(threat_factors) >= 2:
            analysis["threat_level"] = "high"
            analysis["recommended_phase"] = CombatPhase.RETREAT
            analysis["reasoning"].append("Multiple threat factors detected")
        elif len(threat_factors) == 1:
            analysis["threat_level"] = "medium"
            analysis["reasoning"].append(f"Threat factor: {threat_factors[0]}")
        
        # Оценка преимущества
        if context.health_percent > 0.7 and context.stamina_percent > 0.6:
            if context.target_health_percent < 0.4:
                analysis["advantage"] = "high"
                analysis["recommended_phase"] = CombatPhase.ENGAGE
                analysis["reasoning"].append("Favorable combat conditions")
        
        return analysis
    
    def _select_combat_tactic(self, entity_id: str, context: CombatContext, 
                             analysis: Dict[str, Any]) -> CombatTactic:
        """Выбор боевой тактики"""
        available_tactics = list(CombatTactic)
        
        # Фильтрация по фазе
        phase_tactics = {
            CombatPhase.APPROACH: [CombatTactic.MOBILE_HARASSMENT, CombatTactic.TRAP_AND_AMBUSH],
            CombatPhase.ENGAGE: [CombatTactic.AGGRESSIVE_RUSH, CombatTactic.DEFENSIVE_STANCE],
            CombatPhase.COMBAT: [CombatTactic.AGGRESSIVE_RUSH, CombatTactic.COUNTER_ATTACK],
            CombatPhase.COUNTER: [CombatTactic.COUNTER_ATTACK, CombatTactic.PSYCHOLOGICAL_WARFARE],
            CombatPhase.RETREAT: [CombatTactic.DEFENSIVE_STANCE, CombatTactic.MOBILE_HARASSMENT],
            CombatPhase.RECOVER: [CombatTactic.DEFENSIVE_STANCE, CombatTactic.ADAPTIVE_EVOLUTION],
            CombatPhase.ADAPT: [CombatTactic.ADAPTIVE_EVOLUTION, CombatTactic.PSYCHOLOGICAL_WARFARE]
        }
        
        phase_appropriate = phase_tactics.get(context.current_phase, available_tactics)
        
        # Применение адаптивных весов
        tactic_weights = {}
        for tactic in phase_appropriate:
            weight = 1.0
            
            # Влияние успешности
            if entity_id in self.adaptive_tactics:
                if tactic.value in self.adaptive_tactics[entity_id]:
                    weight *= self.adaptive_tactics[entity_id][tactic.value]
            
            # Влияние угрозы
            if analysis["threat_level"] == "high":
                if tactic in [CombatTactic.DEFENSIVE_STANCE, CombatTactic.RETREAT]:
                    weight *= 1.5
                elif tactic in [CombatTactic.AGGRESSIVE_RUSH]:
                    weight *= 0.5
            
            tactic_weights[tactic] = weight
        
        # Выбор тактики с учётом весов
        total_weight = sum(tactic_weights.values())
        if total_weight > 0:
            rand_val = random.random() * total_weight
            current_weight = 0
            for tactic, weight in tactic_weights.items():
                current_weight += weight
                if rand_val <= current_weight:
                    return tactic
        
        return random.choice(phase_appropriate)
    
    def _select_combat_action(self, entity_id: str, context: CombatContext, 
                             tactic: CombatTactic) -> str:
        """Выбор боевого действия"""
        tactic_actions = {
            CombatTactic.AGGRESSIVE_RUSH: ["charge", "heavy_attack", "combo_attack"],
            CombatTactic.DEFENSIVE_STANCE: ["defend", "block", "counter_ready"],
            CombatTactic.MOBILE_HARASSMENT: ["dash", "quick_attack", "retreat"],
            CombatTactic.COUNTER_ATTACK: ["wait", "counter_attack", "parry"],
            CombatTactic.TRAP_AND_AMBUSH: ["hide", "set_trap", "ambush"],
            CombatTactic.PSYCHOLOGICAL_WARFARE: ["intimidate", "feint", "distract"],
            CombatTactic.ADAPTIVE_EVOLUTION: ["analyze", "adapt", "evolve"]
        }
        
        available_actions = tactic_actions.get(tactic, ["attack", "defend"])
        
        # Применение эмоционального влияния
        emotional_actions = self.emotional_system.get_emotionally_influenced_actions(
            entity_id, available_actions, context.__dict__, time.time()
        )
        
        # Выбор действия с учётом эмоций
        if emotional_actions:
            actions = list(emotional_actions.keys())
            weights = list(emotional_actions.values())
            return random.choices(actions, weights=weights)[0]
        
        return random.choice(available_actions)
    
    def _calculate_decision_confidence(self, context: CombatContext, 
                                     action: str, tactic: CombatTactic) -> float:
        """Расчёт уверенности в решении"""
        confidence = 0.5  # Базовая уверенность
        
        # Влияние здоровья
        if context.health_percent > 0.7:
            confidence += 0.2
        elif context.health_percent < 0.3:
            confidence -= 0.2
        
        # Влияние выносливости
        if context.stamina_percent > 0.6:
            confidence += 0.15
        elif context.stamina_percent < 0.2:
            confidence -= 0.15
        
        # Влияние истории успеха
        if context.pattern_success_history:
            recent_success_rate = sum(context.pattern_success_history[-5:]) / min(5, len(context.pattern_success_history[-5:]))
            confidence += (recent_success_rate - 0.5) * 0.3
        
        return max(0.0, min(1.0, confidence))
    
    def _get_emotional_influence(self, entity_id: str, context: CombatContext) -> float:
        """Получение влияния эмоций"""
        try:
            emotional_stats = self.emotional_system.get_emotional_statistics(entity_id)
            emotional_balance = emotional_stats.get("emotional_balance", 0.5)
            return emotional_balance
        except Exception as e:
            logger.warning(f"Ошибка получения эмоционального влияния: {e}")
            return 0.5
        
    def _get_memory_influence(self, entity_id: str, context: CombatContext) -> float:
        """Получение влияния памяти"""
        try:
            # Поиск похожих ситуаций в памяти
            similar_memories = self.memory_system.search_memories(
                memory_type=MemoryType.COMBAT_EXPERIENCE,
                search_criteria={
                    "entity_id": entity_id,
                    "phase": context.current_phase.value,
                    "health_range": (context.health_percent - 0.1, context.health_percent + 0.1)
                }
            )
            
            if similar_memories:
                # Расчёт влияния на основе успешности похожих ситуаций
                success_rate = sum(1 for mem in similar_memories if mem.get("result", {}).get("success", False)) / len(similar_memories)
                return success_rate
            
            return 0.5
        except Exception as e:
            logger.warning(f"Ошибка получения влияния памяти: {e}")
            return 0.5
        
    def _get_adaptation_level(self, entity_id: str, context: CombatContext) -> float:
        """Получение уровня адаптации"""
        if entity_id not in self.adaptive_tactics:
            return 0.5
        
        # Расчёт среднего успеха тактик
        tactic_successes = self.adaptive_tactics[entity_id].values()
        if tactic_successes:
            return sum(tactic_successes) / len(tactic_successes)
        
            return 0.5
        
    def _update_adaptive_tactics(self, entity_id: str, context: CombatContext, 
                                decision: CombatDecision, result: Dict[str, Any]):
        """Обновление адаптивных тактик"""
        if entity_id not in self.adaptive_tactics:
            self.adaptive_tactics[entity_id] = {}
        
        tactic_key = decision.tactic.value
        success = result.get("success", False)
        
        if tactic_key not in self.adaptive_tactics[entity_id]:
            self.adaptive_tactics[entity_id][tactic_key] = 0.5
        
        current_weight = self.adaptive_tactics[entity_id][tactic_key]
        
        # Обновление веса тактики
        if success:
            new_weight = min(1.0, current_weight + 0.1)
        else:
            new_weight = max(0.0, current_weight - 0.15)
        
        self.adaptive_tactics[entity_id][tactic_key] = new_weight
    
    def _init_base_combat_patterns(self):
        """Инициализация базовых боевых паттернов"""
        base_patterns = [
            CombatPattern(
                id="basic_attack",
                name="Basic Attack",
                actions=["attack"],
                success_rate=0.6,
                usage_count=0,
                last_used=0,
                adaptation_factor=0.1,
                emotional_triggers=["rage", "excitement"]
            ),
            CombatPattern(
                id="defensive_stance",
                name="Defensive Stance",
                actions=["defend", "block"],
                success_rate=0.7,
                usage_count=0,
                last_used=0,
                adaptation_factor=0.15,
                emotional_triggers=["fear", "calmness"]
            ),
            CombatPattern(
                id="mobile_combat",
                name="Mobile Combat",
                actions=["dash", "attack", "retreat"],
                success_rate=0.5,
                usage_count=0,
                last_used=0,
                adaptation_factor=0.2,
                emotional_triggers=["curiosity", "excitement"]
            )
        ]
        
        for pattern in base_patterns:
            self.combat_patterns[pattern.id] = pattern


class CounterAttackSystem:
    """Система контратак"""
    
    def __init__(self):
        self.counter_opportunities: Dict[str, List[Dict[str, Any]]] = {}
        self.counter_success_rate: Dict[str, float] = {}
    
    def detect_counter_opportunity(self, entity_id: str, context: CombatContext) -> bool:
        """Обнаружение возможности контратаки"""
        # Анализ действий противника
        if context.current_phase == CombatPhase.DEFEND:
            # Проверка уязвимости противника
            if context.target_health_percent < 0.5:
                return True
        
        return False
    
    def execute_counter_attack(self, entity_id: str, context: CombatContext) -> Dict[str, Any]:
        """Выполнение контратаки"""
        if not self.detect_counter_opportunity(entity_id, context):
            return {"success": False, "reason": "No counter opportunity"}
        
        # Расчёт успешности контратаки
        base_success = 0.6
        health_bonus = (1.0 - context.health_percent) * 0.2
        stamina_bonus = context.stamina_percent * 0.3
        
        success_rate = min(1.0, base_success + health_bonus + stamina_bonus)
        success = random.random() < success_rate
        
        result = {
            "success": success,
            "damage_multiplier": 1.5 if success else 0.5,
            "stamina_cost": 0.3,
            "counter_type": "defensive_counter"
        }
        
        # Обновление статистики
        self._update_counter_statistics(entity_id, success)
        
        return result
    
    def _update_counter_statistics(self, entity_id: str, success: bool):
        """Обновление статистики контратак"""
        if entity_id not in self.counter_success_rate:
            self.counter_success_rate[entity_id] = 0.5
        
        current_rate = self.counter_success_rate[entity_id]
        if success:
            new_rate = min(1.0, current_rate + 0.05)
            else:
            new_rate = max(0.0, current_rate - 0.1)
        
        self.counter_success_rate[entity_id] = new_rate


class TacticEvolutionSystem:
    """Система эволюции тактик"""
    
    def __init__(self):
        self.tactic_mutations: Dict[str, List[Dict[str, Any]]] = {}
        self.evolution_history: Dict[str, List[str]] = {}
    
    def evolve_tactics(self, entity_id: str, context: CombatContext, 
                      result: Dict[str, Any]):
        """Эволюция тактик на основе результатов"""
        if entity_id not in self.evolution_history:
            self.evolution_history[entity_id] = []
        
        # Анализ результата для эволюции
        if result.get("success", False):
            # Успешная тактика - улучшение
            self._improve_successful_tactic(entity_id, context)
        else:
            # Неудачная тактика - мутация
            self._mutate_failed_tactic(entity_id, context)
    
    def _improve_successful_tactic(self, entity_id: str, context: CombatContext):
        """Улучшение успешной тактики"""
        tactic = context.active_tactic.value
        
        if entity_id not in self.tactic_mutations:
            self.tactic_mutations[entity_id] = []
        
        improvement = {
            "tactic": tactic,
            "type": "improvement",
            "timestamp": time.time(),
            "context": context.__dict__
        }
        
        self.tactic_mutations[entity_id].append(improvement)
        self.evolution_history[entity_id].append(f"Improved {tactic}")
        
        logger.debug(f"Тактика {tactic} улучшена для {entity_id}")
    
    def _mutate_failed_tactic(self, entity_id: str, context: CombatContext):
        """Мутация неудачной тактики"""
        tactic = context.active_tactic.value
        
        if entity_id not in self.tactic_mutations:
            self.tactic_mutations[entity_id] = []
        
        # Создание мутированной версии тактики
        mutation = {
            "tactic": tactic,
            "type": "mutation",
            "timestamp": time.time(),
            "context": context.__dict__,
            "mutation_factor": random.uniform(0.1, 0.3)
        }
        
        self.tactic_mutations[entity_id].append(mutation)
        self.evolution_history[entity_id].append(f"Mutated {tactic}")
        
        logger.debug(f"Тактика {tactic} мутирована для {entity_id}")
