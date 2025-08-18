#!/usr/bin/env python3
"""
Расширенная система боевого ИИ для эволюционной адаптации.
Интегрирует навыки, оружие и изучение для создания умного боевого поведения.
"""

import random
import math
import json
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
from datetime import datetime

from .combat_learning_system import CombatLearningSystem, CombatAction, EnemyVulnerability
from .advanced_weapon_system import AdvancedWeapon, WeaponType, WeaponManager
from .skill_system import Skill, SkillManager, SkillLearningAI, SkillType, SkillElement
from .ai_system import AdaptiveAISystem, QLearningAgent

logger = logging.getLogger(__name__)


class CombatPhase(Enum):
    """Фазы боя"""
    PREPARATION = "preparation"      # Подготовка к бою
    ENGAGEMENT = "engagement"        # Вступление в бой
    EXECUTION = "execution"          # Выполнение действий
    ADAPTATION = "adaptation"        # Адаптация к ситуации
    RETREAT = "retreat"              # Отступление
    RECOVERY = "recovery"            # Восстановление


class CombatTactic(Enum):
    """Тактики боя"""
    AGGRESSIVE_RUSH = "aggressive_rush"      # Агрессивный натиск
    DEFENSIVE_STANCE = "defensive_stance"    # Оборонительная стойка
    TACTICAL_POSITIONING = "tactical_positioning"  # Тактическое позиционирование
    ELEMENTAL_EXPLOITATION = "elemental_exploitation"  # Использование элементов
    SKILL_COMBO_CHAIN = "skill_combo_chain"  # Цепочка комбинаций навыков
    WEAPON_SWITCHING = "weapon_switching"    # Переключение оружия
    SUPPORT_FOCUS = "support_focus"          # Фокус на поддержке
    ADAPTIVE_RESPONSE = "adaptive_response"  # Адаптивный ответ


@dataclass
class EnhancedCombatContext:
    """Расширенный контекст боя"""
    # Основная информация
    enemy_type: str
    enemy_health: float
    enemy_max_health: float
    enemy_distance: float
    enemy_behavior: str
    enemy_element: str
    enemy_resistances: Dict[str, float]
    
    # Собственное состояние
    own_health: float
    own_max_health: float
    own_stamina: float
    own_max_stamina: float
    own_mana: float
    own_max_mana: float
    
    # Доступные ресурсы
    available_weapons: List[str]
    available_skills: List[str]
    available_items: List[str]
    available_combos: List[str]
    
    # Окружение
    allies_nearby: int
    enemies_nearby: int
    terrain_type: str
    time_of_day: str
    weather: str
    
    # Боевая ситуация
    combat_phase: CombatPhase
    current_tactic: CombatTactic
    threat_level: float
    advantage_ratio: float
    
    # История боя
    recent_actions: List[str]
    successful_attacks: List[str]
    failed_attacks: List[str]
    damage_taken: float
    damage_dealt: float
    
    def calculate_threat_level(self) -> float:
        """Рассчитывает уровень угрозы"""
        health_ratio = self.own_health / max(self.own_max_health, 1.0)
        enemy_health_ratio = self.enemy_health / max(self.enemy_max_health, 1.0)
        
        # Базовый уровень угрозы
        threat = 1.0 - health_ratio
        
        # Учитываем количество врагов
        threat += min(self.enemies_nearby * 0.2, 1.0)
        
        # Учитываем расстояние до врага
        if self.enemy_distance < 2.0:
            threat += 0.3
        elif self.enemy_distance > 10.0:
            threat -= 0.2
        
        return max(0.0, min(1.0, threat))
    
    def calculate_advantage_ratio(self) -> float:
        """Рассчитывает соотношение преимуществ"""
        own_power = self.own_health + self.own_stamina + self.own_mana
        enemy_power = self.enemy_health
        
        if enemy_power == 0:
            return 1.0
        
        ratio = own_power / enemy_power
        return max(0.1, min(2.0, ratio))


@dataclass
class CombatDecision:
    """Решение о боевом действии"""
    action_type: str
    tactic: CombatTactic
    target: Optional[str] = None
    weapon: Optional[str] = None
    skill: Optional[str] = None
    item: Optional[str] = None
    combo: Optional[str] = None
    priority: float = 1.0
    reasoning: str = ""
    confidence: float = 0.5
    expected_outcome: str = ""
    
    def __str__(self) -> str:
        return f"{self.action_type} -> {self.target} (Tactic: {self.tactic.value}, Confidence: {self.confidence:.2f})"


class EnhancedCombatAI:
    """Расширенная система боевого ИИ"""
    
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        
        # Основные системы
        self.combat_learning = CombatLearningSystem(entity_id)
        self.weapon_manager = WeaponManager()
        self.skill_manager = SkillManager()
        self.skill_learning = SkillLearningAI(entity_id)
        self.base_ai = AdaptiveAISystem(entity_id, None)
        
        # Боевые параметры
        self.combat_phase = CombatPhase.PREPARATION
        self.current_tactic = CombatTactic.ADAPTIVE_RESPONSE
        self.aggression_level = 0.5
        self.caution_level = 0.5
        self.adaptability = 0.7
        
        # История решений
        self.decision_history: List[CombatDecision] = []
        self.last_decision_time = 0.0
        self.successful_tactics: Dict[CombatTactic, int] = {tactic: 0 for tactic in CombatTactic}
        
        # Q-learning для тактик
        self.tactic_q_table: Dict[str, Dict[CombatTactic, float]] = {}
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        
        # Инициализация
        self._initialize_tactics()
    
    def _initialize_tactics(self):
        """Инициализация тактик"""
        for tactic in CombatTactic:
            if tactic.value not in self.tactic_q_table:
                self.tactic_q_table[tactic.value] = {tactic: 0.0}
    
    def analyze_combat_situation(self, context: EnhancedCombatContext) -> CombatPhase:
        """Анализирует боевую ситуацию и определяет фазу"""
        
        # Обновляем контекст
        context.threat_level = context.calculate_threat_level()
        context.advantage_ratio = context.calculate_advantage_ratio()
        
        # Определяем фазу боя
        if context.own_health < context.own_max_health * 0.3:
            if context.enemies_nearby > 1:
                return CombatPhase.RETREAT
            else:
                return CombatPhase.RECOVERY
        elif context.own_health < context.own_max_health * 0.6:
            return CombatPhase.ADAPTATION
        elif context.enemy_distance > 8.0:
            return CombatPhase.PREPARATION
        elif context.advantage_ratio > 1.5:
            return CombatPhase.ENGAGEMENT
        else:
            return CombatPhase.ENGAGEMENT
    
    def select_combat_tactic(self, context: EnhancedCombatContext) -> CombatTactic:
        """Выбирает тактику боя"""
        
        # Анализируем ситуацию
        threat_level = context.threat_level
        advantage_ratio = context.advantage_ratio
        available_skills = len(context.available_skills)
        available_weapons = len(context.available_weapons)
        
        # Определяем подходящие тактики
        suitable_tactics = []
        
        if threat_level > 0.7:
            suitable_tactics.extend([
                CombatTactic.DEFENSIVE_STANCE,
                CombatTactic.TACTICAL_POSITIONING,
                CombatTactic.SUPPORT_FOCUS
            ])
        elif advantage_ratio > 1.3:
            suitable_tactics.extend([
                CombatTactic.AGGRESSIVE_RUSH,
                CombatTactic.TACTICAL_POSITIONING,
                CombatTactic.SKILL_COMBO_CHAIN
            ])
        
        if available_skills > 3:
            suitable_tactics.append(CombatTactic.SKILL_COMBO_CHAIN)
        
        if available_weapons > 2:
            suitable_tactics.append(CombatTactic.WEAPON_SWITCHING)
        
        # Всегда добавляем адаптивный ответ
        suitable_tactics.append(CombatTactic.ADAPTIVE_RESPONSE)
        
        # Выбираем лучшую тактику с помощью Q-learning
        best_tactic = None
        best_value = float('-inf')
        
        for tactic in suitable_tactics:
            q_value = self.tactic_q_table.get(context.combat_phase.value, {}).get(tactic, 0.0)
            
            # Добавляем элемент исследования
            if random.random() < self.exploration_rate:
                q_value += random.uniform(0.0, 0.1)
            
            if q_value > best_value:
                best_value = q_value
                best_tactic = tactic
        
        return best_tactic or CombatTactic.ADAPTIVE_RESPONSE
    
    def make_combat_decision(self, context: EnhancedCombatContext) -> CombatDecision:
        """Принимает решение о боевом действии"""
        
        # Обновляем фазу боя
        context.combat_phase = self.analyze_combat_situation(context)
        
        # Выбираем тактику
        tactic = self.select_combat_tactic(context)
        context.current_tactic = tactic
        
        # Принимаем решение на основе тактики
        decision = self._execute_tactic(tactic, context)
        
        # Обновляем историю
        self.decision_history.append(decision)
        self.last_decision_time = datetime.now().timestamp()
        
        return decision
    
    def _execute_tactic(self, tactic: CombatTactic, context: EnhancedCombatContext) -> CombatDecision:
        """Выполняет выбранную тактику"""
        
        if tactic == CombatTactic.AGGRESSIVE_RUSH:
            return self._aggressive_rush_tactic(context)
        elif tactic == CombatTactic.DEFENSIVE_STANCE:
            return self._defensive_stance_tactic(context)
        elif tactic == CombatTactic.SKILL_COMBO_CHAIN:
            return self._skill_combo_chain_tactic(context)
        elif tactic == CombatTactic.WEAPON_SWITCHING:
            return self._weapon_switching_tactic(context)
        elif tactic == CombatTactic.ELEMENTAL_EXPLOITATION:
            return self._elemental_exploitation_tactic(context)
        else:
            return self._adaptive_response_tactic(context)
    
    def _aggressive_rush_tactic(self, context: EnhancedCombatContext) -> CombatDecision:
        """Тактика агрессивного натиска"""
        
        # Ищем лучший навык для атаки
        if context.available_skills:
            best_skill = self.skill_learning.choose_best_skill(
                context.available_skills, 
                context.enemy_type, 
                "aggressive_attack"
            )
            
            if best_skill:
                skill = self.skill_manager.get_skill(best_skill)
                if skill and skill.base_damage > 0:
                    return CombatDecision(
                        action_type="skill_attack",
                        target=context.enemy_type,
                        skill=best_skill,
                        tactic=CombatTactic.AGGRESSIVE_RUSH,
                        priority=0.9,
                        reasoning="Агрессивная атака навыком",
                        confidence=0.8,
                        expected_outcome="Высокий урон"
                    )
        
        # Если нет навыков, используем оружие
        if context.available_weapons:
            best_weapon = self.combat_learning.get_best_weapon_against(
                context.enemy_type
            )
            if best_weapon and best_weapon in context.available_weapons:
                return CombatDecision(
                    action_type="weapon_attack",
                    target=context.enemy_type,
                    weapon=best_weapon,
                    tactic=CombatTactic.AGGRESSIVE_RUSH,
                    priority=0.8,
                    reasoning="Агрессивная атака оружием",
                    confidence=0.7,
                    expected_outcome="Средний урон"
                )
            
            if best_weapon:
                return CombatDecision(
                    action_type="weapon_attack",
                    target=context.enemy_type,
                    weapon=best_weapon,
                    tactic=CombatTactic.AGGRESSIVE_RUSH,
                    priority=0.8,
                    reasoning="Агрессивная атака оружием",
                    confidence=0.7,
                    expected_outcome="Средний урон"
                )
        
        # Базовая атака
        return CombatDecision(
            action_type="basic_attack",
            target=context.enemy_type,
            tactic=CombatTactic.AGGRESSIVE_RUSH,
            priority=0.6,
            reasoning="Базовая атака",
            confidence=0.5,
            expected_outcome="Низкий урон"
        )
    
    def _defensive_stance_tactic(self, context: EnhancedCombatContext) -> CombatDecision:
        """Тактика оборонительной стойки"""
        
        # Ищем навыки защиты или исцеления
        defensive_skills = [
            skill_id for skill_id in context.available_skills
            if self.skill_manager.get_skill(skill_id) and self.skill_manager.get_skill(skill_id).skill_type == SkillType.SUPPORT
        ]
        
        if defensive_skills and context.own_health < context.own_max_health * 0.7:
            best_skill = random.choice(defensive_skills)
            return CombatDecision(
                action_type="defensive_skill",
                target="self",
                skill=best_skill,
                tactic=CombatTactic.DEFENSIVE_STANCE,
                priority=0.9,
                reasoning="Защитный навык",
                confidence=0.8,
                expected_outcome="Восстановление здоровья"
            )
        
        # Используем предметы для защиты
        if context.available_items:
            return CombatDecision(
                action_type="use_item",
                target="self",
                item=random.choice(context.available_items),
                tactic=CombatTactic.DEFENSIVE_STANCE,
                priority=0.7,
                reasoning="Использование защитного предмета",
                confidence=0.6,
                expected_outcome="Улучшение защиты"
            )
        
        # Базовая защита
        return CombatDecision(
            action_type="defend",
            target="self",
            tactic=CombatTactic.DEFENSIVE_STANCE,
            priority=0.5,
            reasoning="Базовая защита",
            confidence=0.5,
            expected_outcome="Снижение получаемого урона"
        )
    
    def _skill_combo_chain_tactic(self, context: EnhancedCombatContext) -> CombatDecision:
        """Тактика цепочки комбинаций навыков"""
        
        # Ищем доступные комбинации
        if context.available_combos:
            best_combo = self.skill_learning.choose_skill_combo(
                context.available_combos,
                context.enemy_type,
                "combo_attack"
            )
            
            if best_combo:
                return CombatDecision(
                    action_type="skill_combo",
                    target=context.enemy_type,
                    combo=best_combo,
                    tactic=CombatTactic.SKILL_COMBO_CHAIN,
                    priority=0.95,
                    reasoning="Комбинация навыков",
                    confidence=0.9,
                    expected_outcome="Максимальный урон"
                )
        
        # Если нет комбинаций, используем последовательность навыков
        if len(context.available_skills) >= 2:
            # Выбираем два навыка для последовательного использования
            skill1, skill2 = random.sample(context.available_skills, 2)
            return CombatDecision(
                action_type="skill_sequence",
                target=context.enemy_type,
                skill=skill1,
                tactic=CombatTactic.SKILL_COMBO_CHAIN,
                priority=0.8,
                reasoning="Последовательность навыков",
                confidence=0.7,
                expected_outcome="Комбинированный урон"
            )
        
        # Обычная атака навыком
        if context.available_skills:
            best_skill = random.choice(context.available_skills)
            return CombatDecision(
                action_type="skill_attack",
                target=context.enemy_type,
                skill=best_skill,
                tactic=CombatTactic.SKILL_COMBO_CHAIN,
                priority=0.7,
                reasoning="Атака навыком",
                confidence=0.6,
                expected_outcome="Урон навыком"
            )
        
        # Fallback
        return self._adaptive_response_tactic(context)
    
    def _weapon_switching_tactic(self, context: EnhancedCombatContext) -> CombatDecision:
        """Тактика переключения оружия"""
        
        # Анализируем эффективность текущего оружия
        if context.available_weapons:
            # Ищем лучшее оружие против текущего врага
            best_weapon = self.combat_learning.get_best_weapon_against(
                context.enemy_type
            )
            
            if best_weapon and best_weapon in context.available_weapons:
                return CombatDecision(
                    action_type="weapon_attack",
                    target=context.enemy_type,
                    weapon=best_weapon,
                    tactic=CombatTactic.WEAPON_SWITCHING,
                    priority=0.85,
                    reasoning="Оптимальное оружие против врага",
                    confidence=0.8,
                    expected_outcome="Повышенный урон"
                )
        
        # Fallback
        return self._adaptive_response_tactic(context)
    
    def _elemental_exploitation_tactic(self, context: EnhancedCombatContext) -> CombatDecision:
        """Тактика использования элементов"""
        
        # Анализируем уязвимости врага
        enemy_resistances = context.enemy_resistances
        
        # Ищем навыки с элементами, к которым враг уязвим
        for skill_id in context.available_skills:
            skill = self.skill_manager.get_skill(skill_id)
            if skill and skill.element != SkillElement.NONE:
                element_key = skill.element.value
                resistance = enemy_resistances.get(element_key, 0.0)
                
                # Если враг уязвим к элементу
                if resistance < 0.0:
                    return CombatDecision(
                        action_type="elemental_skill",
                        target=context.enemy_type,
                        skill=skill_id,
                        tactic=CombatTactic.ELEMENTAL_EXPLOITATION,
                        priority=0.9,
                        reasoning=f"Использование уязвимости к {element_key}",
                        confidence=0.85,
                        expected_outcome="Критический урон"
                    )
        
        # Fallback
        return self._adaptive_response_tactic(context)
    
    def _adaptive_response_tactic(self, context: EnhancedCombatContext) -> CombatDecision:
        """Адаптивная тактика ответа"""
        
        # Анализируем текущую ситуацию
        if context.threat_level > 0.6:
            # Высокая угроза - защищаемся
            return self._defensive_stance_tactic(context)
        elif context.advantage_ratio > 1.2:
            # Преимущество - атакуем
            return self._aggressive_rush_tactic(context)
        else:
            # Баланс - используем смешанную тактику
            if random.random() < 0.5:
                return self._aggressive_rush_tactic(context)
            else:
                return self._defensive_stance_tactic(context)
    
    def learn_from_combat_result(self, decision: CombatDecision, 
                                success: bool, outcome: Dict[str, Any]):
        """Учится на результате боя"""
        
        # Обновляем эффективность тактики
        tactic = decision.tactic
        if success:
            self.successful_tactics[tactic] += 1
        
        # Обновляем Q-таблицу тактик
        context_key = f"{decision.action_type}_{decision.target or 'unknown'}"
        if context_key not in self.tactic_q_table:
            self.tactic_q_table[context_key] = {}
        
        current_q = self.tactic_q_table[context_key].get(tactic, 0.0)
        reward = 1.0 if success else -0.5
        
        # Учитываем результат
        if "damage_dealt" in outcome:
            damage_bonus = min(outcome["damage_dealt"] / 100.0, 1.0)
            reward += damage_bonus
        
        new_q = current_q + self.learning_rate * (reward - current_q)
        self.tactic_q_table[context_key][tactic] = new_q
        
        # Обновляем другие системы
        if decision.skill:
            self.skill_learning.update_skill_effectiveness(
                decision.skill,
                decision.target or "unknown",
                success,
                outcome.get("damage_dealt", 0.0)
            )
        
        if decision.weapon:
            self.combat_learning.update_weapon_effectiveness(
                decision.weapon,
                decision.target or "unknown",
                success,
                outcome.get("damage_dealt", 0.0)
            )
    
    def get_combat_ai_state(self) -> Dict[str, Any]:
        """Получает состояние боевого ИИ"""
        return {
            "entity_id": self.entity_id,
            "combat_phase": self.combat_phase.value,
            "current_tactic": self.current_tactic.value,
            "aggression_level": self.aggression_level,
            "caution_level": self.caution_level,
            "adaptability": self.adaptability,
            "successful_tactics": self.successful_tactics.copy(),
            "decision_history_length": len(self.decision_history),
            "skill_learning_progress": self.skill_learning.get_learning_progress(),
            "combat_learning_progress": self.combat_learning.get_learning_report()
        }
    
    def save_combat_ai_state(self, filename: str):
        """Сохраняет состояние боевого ИИ"""
        state = {
            "entity_id": self.entity_id,
            "combat_phase": self.combat_phase.value,
            "current_tactic": self.current_tactic.value,
            "aggression_level": self.aggression_level,
            "caution_level": self.caution_level,
            "adaptability": self.adaptability,
            "successful_tactics": self.successful_tactics,
            "tactic_q_table": self.tactic_q_table,
            "decision_history": [
                {
                    "action_type": d.action_type,
                    "target": d.target,
                    "tactic": d.tactic.value,
                    "success": True  # Упрощенно
                }
                for d in self.decision_history[-100:]  # Последние 100 решений
            ]
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.info(f"Состояние боевого ИИ сохранено в {filename}")
        except Exception as e:
            logger.error(f"Ошибка сохранения состояния боевого ИИ: {e}")
    
    def load_combat_ai_state(self, filename: str):
        """Загружает состояние боевого ИИ"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.combat_phase = CombatPhase(state.get("combat_phase", "preparation"))
            self.current_tactic = CombatTactic(state.get("current_tactic", "adaptive_response"))
            self.aggression_level = state.get("aggression_level", 0.5)
            self.caution_level = state.get("caution_level", 0.5)
            self.adaptability = state.get("adaptability", 0.7)
            self.successful_tactics = state.get("successful_tactics", {})
            self.tactic_q_table = state.get("tactic_q_table", {})
            
            logger.info(f"Состояние боевого ИИ загружено из {filename}")
        except Exception as e:
            logger.error(f"Ошибка загрузки состояния боевого ИИ: {e}")
