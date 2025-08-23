#!/usr/bin/env python3
"""
Улучшенная система боевого обучения ИИ.
Объединяет тактическое мышление, адаптацию к стилю игрока и эволюционное обучение.
Вдохновлено механиками из Dark Souls, Bloodborne и Diablo.
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
    APPROACH = "approach"
    ENGAGEMENT = "engagement"
    SUSTAINED_COMBAT = "sustained_combat"
    RETREAT = "retreat"
    RECOVERY = "recovery"
    COUNTER_ATTACK = "counter_attack"


class CombatTactic(Enum):
    """Тактические подходы"""
    AGGRESSIVE_RUSH = "aggressive_rush"
    DEFENSIVE_STANCE = "defensive_stance"
    MOBILE_HARASSMENT = "mobile_harassment"
    AMBUSH_ATTACK = "ambush_attack"
    SUPPORT_ROLE = "support_role"
    TACTICAL_WITHDRAWAL = "tactical_withdrawal"


class PlayerStyle(Enum):
    """Стили игры игрока"""
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    TACTICAL = "tactical"
    MOBILE = "mobile"
    SUPPORT = "support"
    HYBRID = "hybrid"


@dataclass
class CombatContext:
    """Контекст боевой ситуации"""
    combat_phase: CombatPhase
    player_style: PlayerStyle
    player_health_percent: float
    player_stamina_percent: float
    player_weapon_type: str
    player_armor_type: str
    player_buffs: List[str]
    player_debuffs: List[str]
    enemy_count: int
    enemy_types: List[str]
    environmental_hazards: List[str]
    available_cover: List[str]
    escape_routes: List[str]
    tactical_advantages: List[str]


@dataclass
class CombatDecision:
    """Боевое решение ИИ"""
    action: str
    target: Optional[str]
    priority: float
    confidence: float
    reasoning: str
    expected_outcome: str
    risk_assessment: float
    adaptation_factor: float


@dataclass
class PlayerPattern:
    """Паттерн поведения игрока"""
    style: PlayerStyle
    preferred_weapons: List[str]
    preferred_tactics: List[str]
    aggression_level: float
    caution_level: float
    adaptability: float
    predictability: float
    learning_rate: float
    pattern_strength: float


class EnhancedCombatLearningAI:
    """Улучшенная система боевого обучения ИИ"""
    
    def __init__(self, memory_system: GenerationalMemorySystem, 
                 emotional_system: EmotionalAIInfluenceSystem):
        self.memory_system = memory_system
        self.emotional_system = emotional_system
        
        # Анализ стиля игрока
        self.player_patterns: Dict[str, PlayerPattern] = {}
        
        # Тактические базы данных
        self.tactical_database = self._init_tactical_database()
        
        # Система адаптации
        self.adaptation_rates = {
            "aggressive": 0.8,
            "defensive": 0.6,
            "tactical": 0.7,
            "mobile": 0.9,
            "support": 0.5
        }
        
        # Счетчики успешности тактик
        self.tactic_success_rates: Dict[str, float] = {}
        
        logger.info("Улучшенная система боевого обучения ИИ инициализирована")
    
    def analyze_player_style(self, combat_data: List[Dict[str, Any]]) -> PlayerPattern:
        """Анализ стиля игры игрока"""
        if not combat_data:
            return self._create_default_pattern()
        
        # Анализ агрессивности
        aggression_score = self._calculate_aggression_score(combat_data)
        
        # Анализ осторожности
        caution_score = self._calculate_caution_score(combat_data)
        
        # Анализ мобильности
        mobility_score = self._calculate_mobility_score(combat_data)
        
        # Определение основного стиля
        style = self._determine_player_style(aggression_score, caution_score, mobility_score)
        
        # Анализ предпочтений
        weapon_preferences = self._analyze_weapon_preferences(combat_data)
        tactical_preferences = self._analyze_tactical_preferences(combat_data)
        
        # Создание паттерна
        pattern = PlayerPattern(
            style=style,
            preferred_weapons=weapon_preferences,
            preferred_tactics=tactical_preferences,
            aggression_level=aggression_score,
            caution_level=caution_score,
            adaptability=self._calculate_adaptability(combat_data),
            predictability=self._calculate_predictability(combat_data),
            learning_rate=self._calculate_learning_rate(combat_data),
            pattern_strength=self._calculate_pattern_strength(combat_data)
        )
        
        # Добавляем mobility_score как дополнительный атрибут
        pattern.mobility_score = mobility_score
        
        return pattern
    
    def make_combat_decision(self, entity_id: str, context: CombatContext, 
                           available_actions: List[str], current_time: float) -> CombatDecision:
        """Принятие боевого решения"""
        # Получение релевантных воспоминаний
        relevant_memories = self._get_combat_memories(context)
        
        # Анализ контекста
        context_analysis = self._analyze_combat_context(context)
        
        # Применение эмоционального влияния
        emotional_weights = self.emotional_system.get_emotionally_influenced_actions(
            entity_id, available_actions, context_analysis, current_time
        )
        
        # Тактический анализ
        tactical_weights = self._calculate_tactical_weights(context, available_actions)
        
        # Адаптация к стилю игрока
        adaptation_weights = self._calculate_adaptation_weights(context, available_actions)
        
        # Объединение весов
        final_weights = self._combine_decision_weights(
            emotional_weights, tactical_weights, adaptation_weights
        )
        
        # Выбор действия
        best_action = max(final_weights.items(), key=lambda x: x[1])[0]
        
        # Создание решения
        decision = CombatDecision(
            action=best_action,
            target=self._select_target(best_action, context),
            priority=final_weights[best_action],
            confidence=self._calculate_confidence(final_weights, best_action),
            reasoning=self._generate_reasoning(best_action, context, relevant_memories),
            expected_outcome=self._predict_outcome(best_action, context),
            risk_assessment=self._assess_risk(best_action, context),
            adaptation_factor=self._calculate_adaptation_factor(context)
        )
        
        # Запись решения в память
        self._record_combat_decision(entity_id, decision, context, current_time)
        
        return decision
    
    def learn_from_combat_result(self, entity_id: str, decision: CombatDecision, 
                               context: CombatContext, result: Dict[str, Any]):
        """Обучение на основе результата боя"""
        # Анализ результата
        success = result.get("success", False)
        damage_dealt = result.get("damage_dealt", 0.0)
        damage_taken = result.get("damage_taken", 0.0)
        
        # Обновление статистики тактик
        tactic_key = f"{decision.action}_{context.combat_phase.value}"
        if tactic_key not in self.tactic_success_rates:
            self.tactic_success_rates[tactic_key] = 0.5
        
        # Обновление успешности
        if success:
            self.tactic_success_rates[tactic_key] = min(1.0, 
                self.tactic_success_rates[tactic_key] + 0.1)
        else:
            self.tactic_success_rates[tactic_key] = max(0.0, 
                self.tactic_success_rates[tactic_key] - 0.05)
        
        # Запись опыта в память поколений
        memory_content = {
            "action": decision.action,
            "context": context.__dict__,
            "result": result,
            "success": success,
            "damage_ratio": damage_dealt / max(1.0, damage_taken),
            "tactic_used": tactic_key
        }
        
        self.memory_system.add_memory(
            memory_type=MemoryType.COMBAT_EXPERIENCE,
            content=memory_content,
            intensity=0.7 if success else 0.9,
            emotional_impact=0.6 if success else 0.8
        )
        
        # Обновление паттерна игрока
        self._update_player_pattern(context, result)
        
        logger.debug(f"ИИ {entity_id} извлек урок из боевого решения: {decision.action}")
    
    def _init_tactical_database(self) -> Dict[str, Dict[str, Any]]:
        """Инициализация тактической базы данных"""
        return {
            "aggressive_rush": {
                "description": "Быстрая атака с максимальным уроном",
                "best_against": ["defensive", "support"],
                "worst_against": ["mobile", "tactical"],
                "phase_effectiveness": {
                    CombatPhase.APPROACH: 0.8,
                    CombatPhase.ENGAGEMENT: 0.9,
                    CombatPhase.SUSTAINED_COMBAT: 0.6,
                    CombatPhase.RETREAT: 0.2,
                    CombatPhase.RECOVERY: 0.3,
                    CombatPhase.COUNTER_ATTACK: 0.7
                },
                "required_resources": ["high_stamina", "high_health"],
                "risk_level": 0.8
            },
            "defensive_stance": {
                "description": "Защитная позиция с контр-атаками",
                "best_against": ["aggressive", "mobile"],
                "worst_against": ["tactical", "support"],
                "phase_effectiveness": {
                    CombatPhase.APPROACH: 0.4,
                    CombatPhase.ENGAGEMENT: 0.7,
                    CombatPhase.SUSTAINED_COMBAT: 0.8,
                    CombatPhase.RETREAT: 0.6,
                    CombatPhase.RECOVERY: 0.9,
                    CombatPhase.COUNTER_ATTACK: 0.8
                },
                "required_resources": ["medium_stamina", "high_health"],
                "risk_level": 0.4
            },
            "mobile_harassment": {
                "description": "Мобильная тактика с быстрыми ударами",
                "best_against": ["defensive", "tactical"],
                "worst_against": ["aggressive", "mobile"],
                "phase_effectiveness": {
                    CombatPhase.APPROACH: 0.9,
                    CombatPhase.ENGAGEMENT: 0.7,
                    CombatPhase.SUSTAINED_COMBAT: 0.5,
                    CombatPhase.RETREAT: 0.8,
                    CombatPhase.RECOVERY: 0.6,
                    CombatPhase.COUNTER_ATTACK: 0.7
                },
                "required_resources": ["high_stamina", "medium_health"],
                "risk_level": 0.6
            },
            "ambush_attack": {
                "description": "Внезапная атака из укрытия",
                "best_against": ["aggressive", "support"],
                "worst_against": ["defensive", "tactical"],
                "phase_effectiveness": {
                    CombatPhase.APPROACH: 0.9,
                    CombatPhase.ENGAGEMENT: 0.8,
                    CombatPhase.SUSTAINED_COMBAT: 0.4,
                    CombatPhase.RETREAT: 0.3,
                    CombatPhase.RECOVERY: 0.2,
                    CombatPhase.COUNTER_ATTACK: 0.5
                },
                "required_resources": ["medium_stamina", "medium_health"],
                "risk_level": 0.7
            },
            "support_role": {
                "description": "Поддерживающая роль с баффами",
                "best_against": ["tactical", "defensive"],
                "worst_against": ["aggressive", "mobile"],
                "phase_effectiveness": {
                    CombatPhase.APPROACH: 0.3,
                    CombatPhase.ENGAGEMENT: 0.5,
                    CombatPhase.SUSTAINED_COMBAT: 0.8,
                    CombatPhase.RETREAT: 0.7,
                    CombatPhase.RECOVERY: 0.9,
                    CombatPhase.COUNTER_ATTACK: 0.4
                },
                "required_resources": ["low_stamina", "medium_health"],
                "risk_level": 0.5
            }
        }
    
    def _calculate_aggression_score(self, combat_data: List[Dict[str, Any]]) -> float:
        """Расчёт агрессивности игрока"""
        if not combat_data:
            return 0.5
        
        aggression_indicators = []
        
        for data in combat_data:
            # Частота атак
            if "attack_frequency" in data:
                aggression_indicators.append(data["attack_frequency"])
            
            # Расстояние атаки
            if "attack_range" in data:
                range_score = min(1.0, data["attack_range"] / 10.0)
                aggression_indicators.append(range_score)
            
            # Использование агрессивных способностей
            if "aggressive_abilities_used" in data:
                aggression_indicators.append(data["aggressive_abilities_used"])
        
        if not aggression_indicators:
            return 0.5
        
        return sum(aggression_indicators) / len(aggression_indicators)
    
    def _calculate_caution_score(self, combat_data: List[Dict[str, Any]]) -> float:
        """Расчёт осторожности игрока"""
        if not combat_data:
            return 0.5
        
        caution_indicators = []
        
        for data in combat_data:
            # Частота блокирования
            if "block_frequency" in data:
                caution_indicators.append(data["block_frequency"])
            
            # Использование укрытий
            if "cover_usage" in data:
                caution_indicators.append(data["cover_usage"])
            
            # Расстояние до врагов
            if "maintained_distance" in data:
                distance_score = min(1.0, data["maintained_distance"] / 20.0)
                caution_indicators.append(distance_score)
        
        if not caution_indicators:
            return 0.5
        
        return sum(caution_indicators) / len(caution_indicators)
    
    def _calculate_mobility_score(self, combat_data: List[Dict[str, Any]]) -> float:
        """Расчёт мобильности игрока"""
        if not combat_data:
            return 0.5
        
        mobility_indicators = []
        
        for data in combat_data:
            # Частота перемещений
            if "movement_frequency" in data:
                mobility_indicators.append(data["movement_frequency"])
            
            # Использование мобильных способностей
            if "mobile_abilities_used" in data:
                mobility_indicators.append(data["mobile_abilities_used"])
            
            # Эффективность уклонений
            if "dodge_success_rate" in data:
                mobility_indicators.append(data["dodge_success_rate"])
        
        if not mobility_indicators:
            return 0.5
        
        return sum(mobility_indicators) / len(mobility_indicators)
    
    def _determine_player_style(self, aggression: float, caution: float, 
                               mobility: float) -> PlayerStyle:
        """Определение стиля игрока"""
        # Нормализация значений
        total = aggression + caution + mobility
        if total == 0:
            return PlayerStyle.HYBRID
        
        aggression_norm = aggression / total
        caution_norm = caution / total
        mobility_norm = mobility / total
        
        # Определение доминирующего стиля
        if aggression_norm > 0.4:
            return PlayerStyle.AGGRESSIVE
        elif caution_norm > 0.4:
            return PlayerStyle.DEFENSIVE
        elif mobility_norm > 0.4:
            return PlayerStyle.MOBILE
        elif caution_norm > 0.3 and mobility_norm > 0.3:
            return PlayerStyle.TACTICAL
        elif caution_norm > 0.3 and aggression_norm < 0.2:
            return PlayerStyle.SUPPORT
        else:
            return PlayerStyle.HYBRID
    
    def _analyze_weapon_preferences(self, combat_data: List[Dict[str, Any]]) -> List[str]:
        """Анализ предпочтений в оружии"""
        weapon_usage = {}
        
        for data in combat_data:
            if "weapon_used" in data:
                weapon = data["weapon_used"]
                weapon_usage[weapon] = weapon_usage.get(weapon, 0) + 1
        
        # Сортировка по частоте использования
        sorted_weapons = sorted(weapon_usage.items(), key=lambda x: x[1], reverse=True)
        
        # Возврат топ-3 предпочтений
        return [weapon for weapon, _ in sorted_weapons[:3]]
    
    def _analyze_tactical_preferences(self, combat_data: List[Dict[str, Any]]) -> List[str]:
        """Анализ тактических предпочтений"""
        tactic_usage = {}
        
        for data in combat_data:
            if "tactic_used" in data:
                tactic = data["tactic_used"]
                tactic_usage[tactic] = tactic_usage.get(tactic, 0) + 1
        
        # Сортировка по частоте использования
        sorted_tactics = sorted(tactic_usage.items(), key=lambda x: x[1], reverse=True)
        
        # Возврат топ-3 предпочтений
        return [tactic for tactic, _ in sorted_tactics[:3]]
    
    def _calculate_adaptability(self, combat_data: List[Dict[str, Any]]) -> float:
        """Расчёт адаптивности игрока"""
        if len(combat_data) < 2:
            return 0.5
        
        # Анализ изменения тактик
        tactic_changes = 0
        total_combats = len(combat_data) - 1
        
        for i in range(total_combats):
            if combat_data[i].get("tactic_used") != combat_data[i+1].get("tactic_used"):
                tactic_changes += 1
        
        adaptability = tactic_changes / total_combats
        return min(1.0, adaptability * 2)  # Масштабирование
    
    def _calculate_predictability(self, combat_data: List[Dict[str, Any]]) -> float:
        """Расчёт предсказуемости игрока"""
        if len(combat_data) < 2:
            return 0.5
        
        # Анализ повторяющихся паттернов
        pattern_repetitions = 0
        total_patterns = len(combat_data) - 1
        
        for i in range(total_patterns):
            if (combat_data[i].get("tactic_used") == combat_data[i+1].get("tactic_used") and
                combat_data[i].get("weapon_used") == combat_data[i+1].get("weapon_used")):
                pattern_repetitions += 1
        
        predictability = pattern_repetitions / total_patterns
        return predictability
    
    def _calculate_learning_rate(self, combat_data: List[Dict[str, Any]]) -> float:
        """Расчёт скорости обучения игрока"""
        if len(combat_data) < 3:
            return 0.5
        
        # Анализ улучшения эффективности
        early_performance = sum(data.get("success_rate", 0.5) 
                              for data in combat_data[:len(combat_data)//2])
        late_performance = sum(data.get("success_rate", 0.5) 
                             for data in combat_data[len(combat_data)//2:])
        
        early_avg = early_performance / (len(combat_data) // 2)
        late_avg = late_performance / (len(combat_data) // 2)
        
        improvement = (late_avg - early_avg) / max(early_avg, 0.1)
        return max(0.0, min(1.0, improvement))
    
    def _calculate_pattern_strength(self, combat_data: List[Dict[str, Any]]) -> float:
        """Расчёт силы паттерна"""
        if len(combat_data) < 2:
            return 0.5
        
        # Анализ консистентности поведения
        consistent_actions = 0
        total_actions = len(combat_data) - 1
        
        for i in range(total_actions):
            if (combat_data[i].get("action_type") == combat_data[i+1].get("action_type") and
                combat_data[i].get("target_type") == combat_data[i+1].get("target_type")):
                consistent_actions += 1
        
        pattern_strength = consistent_actions / total_actions
        return pattern_strength
    
    def _get_combat_memories(self, context: CombatContext) -> List[Any]:
        """Получение релевантных боевых воспоминаний"""
        memory_context = {
            "player_style": context.player_style.value,
            "combat_phase": context.combat_phase.value,
            "enemy_types": context.enemy_types,
            "weapon_type": context.player_weapon_type
        }
        
        return self.memory_system.get_relevant_memories(
            memory_context, 
            memory_types=[MemoryType.COMBAT_EXPERIENCE, MemoryType.ENEMY_PATTERNS],
            limit=5
        )
    
    def _analyze_combat_context(self, context: CombatContext) -> Dict[str, Any]:
        """Анализ боевого контекста"""
        return {
            "phase": context.combat_phase.value,
            "player_style": context.player_style.value,
            "player_health": context.player_health_percent,
            "player_stamina": context.player_stamina_percent,
            "enemy_count": context.enemy_count,
            "hazards_present": len(context.environmental_hazards) > 0,
            "cover_available": len(context.available_cover) > 0,
            "escape_possible": len(context.escape_routes) > 0
        }
    
    def _calculate_tactical_weights(self, context: CombatContext, 
                                  available_actions: List[str]) -> Dict[str, float]:
        """Расчёт тактических весов действий"""
        weights = {action: 1.0 for action in available_actions}
        
        # Применение тактической базы данных
        for action in available_actions:
            if action in self.tactical_database:
                tactic_data = self.tactical_database[action]
                
                # Эффективность в текущей фазе
                phase_effectiveness = tactic_data["phase_effectiveness"].get(
                    context.combat_phase, 0.5
                )
                
                # Соответствие стилю игрока
                style_effectiveness = self._calculate_style_effectiveness(
                    action, context.player_style
                )
                
                # Общий тактический вес
                weights[action] = (phase_effectiveness + style_effectiveness) / 2
        
        return weights
    
    def _calculate_style_effectiveness(self, action: str, player_style: PlayerStyle) -> float:
        """Расчёт эффективности действия против стиля игрока"""
        if action not in self.tactical_database:
            return 0.5
        
        tactic_data = self.tactical_database[action]
        
        # Проверка эффективности против стиля
        if player_style.value in tactic_data["best_against"]:
            return 0.9
        elif player_style.value in tactic_data["worst_against"]:
            return 0.3
        else:
            return 0.6
    
    def _calculate_adaptation_weights(self, context: CombatContext, 
                                    available_actions: List[str]) -> Dict[str, float]:
        """Расчёт весов адаптации к стилю игрока"""
        weights = {action: 1.0 for action in available_actions}
        
        # Адаптация к агрессивному стилю
        if context.player_style == PlayerStyle.AGGRESSIVE:
            if "defend" in weights:
                weights["defend"] *= 1.5
            if "retreat" in weights:
                weights["retreat"] *= 1.3
            if "counter_attack" in weights:
                weights["counter_attack"] *= 1.4
        
        # Адаптация к защитному стилю
        elif context.player_style == PlayerStyle.DEFENSIVE:
            if "aggressive_attack" in weights:
                weights["aggressive_attack"] *= 1.4
            if "flank" in weights:
                weights["flank"] *= 1.3
            if "debuff" in weights:
                weights["debuff"] *= 1.2
        
        # Адаптация к мобильному стилю
        elif context.player_style == PlayerStyle.MOBILE:
            if "area_attack" in weights:
                weights["area_attack"] *= 1.4
            if "trap" in weights:
                weights["trap"] *= 1.3
            if "predict_movement" in weights:
                weights["predict_movement"] *= 1.2
        
        return weights
    
    def _combine_decision_weights(self, emotional_weights: Dict[str, float],
                                 tactical_weights: Dict[str, float],
                                 adaptation_weights: Dict[str, float]) -> Dict[str, float]:
        """Объединение весов решений"""
        combined_weights = {}
        
        for action in emotional_weights.keys():
            emotional = emotional_weights.get(action, 1.0)
            tactical = tactical_weights.get(action, 1.0)
            adaptation = adaptation_weights.get(action, 1.0)
            
            # Взвешенное среднее
            combined_weights[action] = (
                emotional * 0.3 + 
                tactical * 0.4 + 
                adaptation * 0.3
            )
        
        return combined_weights
    
    def _select_target(self, action: str, context: CombatContext) -> Optional[str]:
        """Выбор цели для действия"""
        if not context.enemy_types:
            return None
        
        # Простая логика выбора цели
        if action in ["attack", "debuff", "focus_fire"]:
            # Выбор самого слабого врага
            return "weakest_enemy"
        elif action in ["area_attack", "debuff_area"]:
            # Выбор группы врагов
            return "enemy_group"
        elif action in ["support", "heal"]:
            # Выбор союзника
            return "ally"
        
        return None
    
    def _calculate_confidence(self, weights: Dict[str, float], 
                            selected_action: str) -> float:
        """Расчёт уверенности в решении"""
        if not weights:
            return 0.5
        
        selected_weight = weights.get(selected_action, 0.0)
        max_weight = max(weights.values())
        
        if max_weight == 0:
            return 0.5
        
        # Нормализованная уверенность
        confidence = selected_weight / max_weight
        
        # Дополнительная уверенность если вес значительно выше среднего
        avg_weight = sum(weights.values()) / len(weights)
        if selected_weight > avg_weight * 1.5:
            confidence = min(1.0, confidence + 0.2)
        
        return confidence
    
    def _generate_reasoning(self, action: str, context: CombatContext, 
                          memories: List[Any]) -> str:
        """Генерация объяснения решения"""
        reasoning_parts = []
        
        # Базовое объяснение
        reasoning_parts.append(f"Выбрано действие '{action}' в фазе {context.combat_phase.value}")
        
        # Тактическое обоснование
        if action in self.tactical_database:
            tactic_data = self.tactical_database[action]
            reasoning_parts.append(f"Тактика эффективна против стиля {context.player_style.value}")
        
        # Обоснование на основе памяти
        if memories:
            memory_count = len(memories)
            reasoning_parts.append(f"Учтено {memory_count} предыдущих боевых опытов")
        
        # Контекстуальное обоснование
        if context.enemy_count > 1:
            reasoning_parts.append("Множественные враги требуют тактического подхода")
        
        if context.environmental_hazards:
            reasoning_parts.append("Учтены опасности окружения")
        
        return ". ".join(reasoning_parts)
    
    def _predict_outcome(self, action: str, context: CombatContext) -> str:
        """Предсказание результата действия"""
        if action in self.tactical_database:
            tactic_data = self.tactical_database[action]
            risk_level = tactic_data["risk_level"]
            
            if risk_level > 0.7:
                return "Высокий риск, но потенциально высокая награда"
            elif risk_level > 0.4:
                return "Умеренный риск с хорошими шансами на успех"
            else:
                return "Низкий риск, стабильный результат"
        
        return "Стандартный результат"
    
    def _assess_risk(self, action: str, context: CombatContext) -> float:
        """Оценка риска действия"""
        base_risk = 0.5
        
        if action in self.tactical_database:
            tactic_data = self.tactical_database[action]
            base_risk = tactic_data["risk_level"]
        
        # Модификаторы риска
        risk_modifiers = 1.0
        
        # Риск увеличивается при низком здоровье
        if context.player_health_percent < 0.3:
            risk_modifiers *= 1.5
        
        # Риск увеличивается при множественных врагах
        if context.enemy_count > 2:
            risk_modifiers *= 1.3
        
        # Риск уменьшается при наличии укрытий
        if context.available_cover:
            risk_modifiers *= 0.8
        
        return min(1.0, base_risk * risk_modifiers)
    
    def _calculate_adaptation_factor(self, context: CombatContext) -> float:
        """Расчёт фактора адаптации"""
        # Базовый фактор
        base_factor = 0.5
        
        # Адаптация к стилю игрока
        style_adaptation = self.adaptation_rates.get(context.player_style.value, 0.5)
        
        # Адаптация к фазе боя
        phase_adaptation = {
            CombatPhase.APPROACH: 0.6,
            CombatPhase.ENGAGEMENT: 0.8,
            CombatPhase.SUSTAINED_COMBAT: 0.9,
            CombatPhase.RETREAT: 0.7,
            CombatPhase.RECOVERY: 0.5,
            CombatPhase.COUNTER_ATTACK: 0.8
        }.get(context.combat_phase, 0.5)
        
        # Общий фактор адаптации
        adaptation_factor = (base_factor + style_adaptation + phase_adaptation) / 3
        
        return adaptation_factor
    
    def _record_combat_decision(self, entity_id: str, decision: CombatDecision, 
                              context: CombatContext, current_time: float):
        """Запись боевого решения в память"""
        memory_content = {
            "entity_id": entity_id,
            "action": decision.action,
            "target": decision.target,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "context": context.__dict__,
            "timestamp": current_time
        }
        
        self.memory_system.add_memory(
            memory_type=MemoryType.COMBAT_EXPERIENCE,
            content=memory_content,
            intensity=decision.confidence,
            emotional_impact=0.5
        )
    
    def _update_player_pattern(self, context: CombatContext, result: Dict[str, Any]):
        """Обновление паттерна игрока"""
        # Здесь можно добавить логику для динамического обновления
        # понимания стиля игрока на основе результатов
        pass
    
    def _create_default_pattern(self) -> PlayerPattern:
        """Создание паттерна по умолчанию"""
        return PlayerPattern(
            style=PlayerStyle.HYBRID,
            preferred_weapons=[],
            preferred_tactics=[],
            aggression_level=0.5,
            caution_level=0.5,
            adaptability=0.5,
            predictability=0.5,
            learning_rate=0.5,
            pattern_strength=0.5
        )
    
    def get_ai_statistics(self, entity_id: str) -> Dict[str, Any]:
        """Получение статистики ИИ"""
        return {
            "tactic_success_rates": self.tactic_success_rates,
            "player_patterns": {k: v.__dict__ for k, v in self.player_patterns.items()},
            "total_decisions": len(self.tactic_success_rates),
            "average_success_rate": sum(self.tactic_success_rates.values()) / max(1, len(self.tactic_success_rates))
        }
