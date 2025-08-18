#!/usr/bin/env python3
"""
Интегрированная система боевого ИИ для эволюционной адаптации.
Объединяет все системы для создания умного боевого ИИ.
"""

import random
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from .combat_learning_system import CombatLearningSystem, CombatAction
from .advanced_weapon_system import AdvancedWeapon, WeaponType, WeaponRarity, WeaponFactory
from .ai_system import AdaptiveAISystem, ActionType, AIState

logger = logging.getLogger(__name__)


class CombatStrategy(Enum):
    """Стратегии боя"""
    AGGRESSIVE = "aggressive"      # Агрессивная атака
    DEFENSIVE = "defensive"        # Оборона и контратака
    TACTICAL = "tactical"          # Тактический подход
    EVASIVE = "evasive"            # Уклонение и манёвры
    SUPPORT = "support"            # Поддержка союзников
    ADAPTIVE = "adaptive"          # Адаптивная стратегия


@dataclass
class CombatContext:
    """Контекст боя для принятия решений"""
    enemy_type: str
    enemy_health: float
    enemy_max_health: float
    enemy_distance: float
    enemy_behavior: str
    own_health: float
    own_max_health: float
    own_stamina: float
    own_max_stamina: float
    available_weapons: List[str]
    available_items: List[str]
    allies_nearby: int
    enemies_nearby: int
    terrain_type: str
    time_of_day: str
    weather: str
    
    def get_health_percentage(self) -> float:
        """Получение процента здоровья"""
        return self.own_health / self.own_max_health if self.own_max_health > 0 else 0.0
    
    def get_stamina_percentage(self) -> float:
        """Получение процента выносливости"""
        return self.own_stamina / self.own_max_stamina if self.own_max_stamina > 0 else 0.0
    
    def is_critical_health(self) -> bool:
        """Проверка критического здоровья"""
        return self.get_health_percentage() < 0.3
    
    def is_low_stamina(self) -> bool:
        """Проверка низкой выносливости"""
        return self.get_stamina_percentage() < 0.2


@dataclass
class CombatDecision:
    """Решение о боевом действии"""
    action: CombatAction
    target: Optional[str] = None
    weapon: Optional[str] = None
    item: Optional[str] = None
    priority: float = 1.0
    reasoning: str = ""
    confidence: float = 0.5
    
    def __str__(self):
        return f"{self.action.value} -> {self.reasoning} (уверенность: {self.confidence:.2f})"


class IntegratedCombatAI:
    """Интегрированная система боевого ИИ"""
    
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        
        # Основные системы
        self.combat_learning = CombatLearningSystem(entity_id)
        self.weapon_manager = WeaponManager()
        self.base_ai = AdaptiveAISystem(entity_id, None)
        
        # Боевые настройки
        self.combat_strategy = CombatStrategy.ADAPTIVE
        self.aggression_level = 0.5  # 0.0 - пассивный, 1.0 - агрессивный
        self.caution_level = 0.5     # 0.0 - безрассудный, 1.0 - осторожный
        
        # История боевых решений
        self.decision_history: List[CombatDecision] = []
        self.last_decision_time = 0.0
        
        # Адаптивные параметры
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        
        logger.info(f"Интегрированная система боевого ИИ инициализирована для {entity_id}")
    
    def make_combat_decision(self, context: CombatContext) -> CombatDecision:
        """Принятие боевого решения на основе контекста"""
        try:
            # Анализ ситуации
            situation_analysis = self._analyze_combat_situation(context)
            
            # Выбор стратегии
            strategy = self._select_combat_strategy(context, situation_analysis)
            
            # Принятие решения
            decision = self._make_strategic_decision(context, strategy, situation_analysis)
            
            # Обучение на основе решения
            self._learn_from_decision(decision, context)
            
            # Запись в историю
            self.decision_history.append(decision)
            self.last_decision_time = time.time()
            
            logger.info(f"Принято боевое решение: {decision}")
            return decision
            
        except Exception as e:
            logger.error(f"Ошибка принятия боевого решения: {e}")
            # Возврат безопасного решения по умолчанию
            return CombatDecision(
                action=CombatAction.DEFEND,
                reasoning="Ошибка ИИ, переход в защиту",
                confidence=0.1
            )
    
    def _analyze_combat_situation(self, context: CombatContext) -> Dict[str, Any]:
        """Анализ боевой ситуации"""
        analysis = {
            "threat_level": self._calculate_threat_level(context),
            "advantage_ratio": self._calculate_advantage_ratio(context),
            "terrain_advantage": self._calculate_terrain_advantage(context),
            "weapon_effectiveness": self._calculate_weapon_effectiveness(context),
            "item_priority": self._calculate_item_priority(context),
            "tactical_position": self._calculate_tactical_position(context)
        }
        
        return analysis
    
    def _calculate_threat_level(self, context: CombatContext) -> float:
        """Расчёт уровня угрозы"""
        threat = 0.0
        
        # Угроза от врага
        if context.enemy_health > 0:
            enemy_health_ratio = context.enemy_health / context.enemy_max_health
            threat += (1.0 - enemy_health_ratio) * 0.4  # Раненый враг менее опасен
        
        # Расстояние до врага
        if context.enemy_distance < 2.0:
            threat += 0.3  # Близкий враг опасен
        elif context.enemy_distance > 10.0:
            threat += 0.1  # Дальний враг менее опасен
        
        # Количество врагов
        threat += min(0.3, context.enemies_nearby * 0.1)
        
        return min(1.0, threat)
    
    def _calculate_advantage_ratio(self, context: CombatContext) -> float:
        """Расчёт соотношения сил"""
        own_health_ratio = context.get_health_percentage()
        enemy_health_ratio = context.enemy_health / context.enemy_max_health
        
        # Положительное значение = преимущество, отрицательное = недостаток
        advantage = (own_health_ratio - enemy_health_ratio) * 0.5
        
        # Учёт союзников
        if context.allies_nearby > 0:
            advantage += 0.2
        
        return max(-1.0, min(1.0, advantage))
    
    def _calculate_terrain_advantage(self, context: CombatContext) -> float:
        """Расчёт преимущества от местности"""
        terrain_advantages = {
            "forest": 0.2,      # Лес даёт укрытие
            "mountain": 0.1,    # Горы дают позиционное преимущество
            "water": -0.1,      # Вода ограничивает манёвренность
            "urban": 0.0,       # Городская местность нейтральна
            "open": -0.1        # Открытая местность опасна
        }
        
        return terrain_advantages.get(context.terrain_type, 0.0)
    
    def _calculate_weapon_effectiveness(self, context: CombatContext) -> Dict[str, float]:
        """Расчёт эффективности доступного оружия"""
        effectiveness = {}
        
        for weapon_id in context.available_weapons:
            weapon = self.weapon_manager.get_weapon(weapon_id)
            if weapon:
                effectiveness[weapon_id] = weapon.get_effectiveness_against(context.enemy_type)
        
        return effectiveness
    
    def _calculate_item_priority(self, context: CombatContext) -> Dict[str, float]:
        """Расчёт приоритета использования предметов"""
        priorities = {}
        
        for item_id in context.available_items:
            priority = 0.0
            
            # Приоритет лечения при низком здоровье
            if context.is_critical_health():
                if "heal" in item_id.lower() or "potion" in item_id.lower():
                    priority += 0.8
            
            # Приоритет восстановления выносливости
            if context.is_low_stamina():
                if "stamina" in item_id.lower() or "energy" in item_id.lower():
                    priority += 0.6
            
            # Приоритет баффов при хорошем состоянии
            if context.get_health_percentage() > 0.7:
                if "buff" in item_id.lower() or "enhance" in item_id.lower():
                    priority += 0.4
            
            priorities[item_id] = priority
        
        return priorities
    
    def _calculate_tactical_position(self, context: CombatContext) -> str:
        """Определение тактической позиции"""
        if context.get_health_percentage() < 0.3:
            return "defensive"
        elif context.get_health_percentage() > 0.7 and context.enemy_distance > 5.0:
            return "offensive"
        elif context.allies_nearby > 0:
            return "support"
        else:
            return "balanced"
    
    def _select_combat_strategy(self, context: CombatContext, analysis: Dict[str, Any]) -> CombatStrategy:
        """Выбор боевой стратегии"""
        threat_level = analysis["threat_level"]
        advantage_ratio = analysis["advantage_ratio"]
        tactical_position = analysis["tactical_position"]
        
        # Адаптивная стратегия на основе анализа
        if threat_level > 0.8:
            return CombatStrategy.DEFENSIVE
        elif threat_level < 0.3 and advantage_ratio > 0.5:
            return CombatStrategy.AGGRESSIVE
        elif tactical_position == "support":
            return CombatStrategy.SUPPORT
        elif advantage_ratio < -0.5:
            return CombatStrategy.EVASIVE
        else:
            return CombatStrategy.TACTICAL
    
    def _make_strategic_decision(self, context: CombatContext, strategy: CombatStrategy, 
                                analysis: Dict[str, Any]) -> CombatDecision:
        """Принятие стратегического решения"""
        
        if strategy == CombatStrategy.DEFENSIVE:
            return self._make_defensive_decision(context, analysis)
        elif strategy == CombatStrategy.AGGRESSIVE:
            return self._make_aggressive_decision(context, analysis)
        elif strategy == CombatStrategy.TACTICAL:
            return self._make_tactical_decision(context, analysis)
        elif strategy == CombatStrategy.EVASIVE:
            return self._make_evasive_decision(context, analysis)
        elif strategy == CombatStrategy.SUPPORT:
            return self._make_support_decision(context, analysis)
        else:
            return self._make_adaptive_decision(context, analysis)
    
    def _make_defensive_decision(self, context: CombatContext, analysis: Dict[str, Any]) -> CombatDecision:
        """Принятие оборонительного решения"""
        # Приоритет лечения
        if context.is_critical_health():
            best_item = self.combat_learning.get_best_item_for_situation("low_health")
            if best_item and best_item in context.available_items:
                return CombatDecision(
                    action=CombatAction.USE_ITEM,
                    item=best_item,
                    priority=0.9,
                    reasoning="Критическое здоровье, использование лечебного предмета",
                    confidence=0.8
                )
        
        # Защита
        return CombatDecision(
            action=CombatAction.DEFEND,
            priority=0.7,
            reasoning="Оборонительная стратегия, защита от атак",
            confidence=0.6
        )
    
    def _make_aggressive_decision(self, context: CombatContext, analysis: Dict[str, Any]) -> CombatDecision:
        """Принятие агрессивного решения"""
        # Выбор лучшего оружия
        weapon_effectiveness = analysis["weapon_effectiveness"]
        if weapon_effectiveness:
            best_weapon = max(weapon_effectiveness.keys(), key=lambda w: weapon_effectiveness[w])
            
            return CombatDecision(
                action=CombatAction.ATTACK_MELEE,
                weapon=best_weapon,
                priority=0.8,
                reasoning="Агрессивная атака лучшим оружием",
                confidence=0.7
            )
        
        # Атака по умолчанию
        return CombatDecision(
            action=CombatAction.ATTACK_MELEE,
            priority=0.6,
            reasoning="Агрессивная атака",
            confidence=0.5
        )
    
    def _make_tactical_decision(self, context: CombatContext, analysis: Dict[str, Any]) -> CombatDecision:
        """Принятие тактического решения"""
        # Анализ уязвимостей врага
        vulnerabilities = self.combat_learning.get_enemy_vulnerabilities(context.enemy_type)
        
        if vulnerabilities:
            best_vulnerability = max(vulnerabilities, key=lambda v: v.confidence * v.vulnerability_multiplier)
            
            # Выбор оружия на основе уязвимости
            if best_vulnerability.damage_type == "physical":
                action = CombatAction.ATTACK_MELEE
            elif best_vulnerability.damage_type in ["fire", "ice", "lightning"]:
                action = CombatAction.ATTACK_MAGIC
            else:
                action = CombatAction.ATTACK_RANGED
            
            return CombatDecision(
                action=action,
                priority=0.8,
                reasoning=f"Использование уязвимости врага к {best_vulnerability.damage_type}",
                confidence=best_vulnerability.confidence
            )
        
        # Тактическое отступление при необходимости
        if context.get_health_percentage() < 0.5:
            return CombatDecision(
                action=CombatAction.RETREAT,
                priority=0.6,
                reasoning="Тактическое отступление для восстановления",
                confidence=0.5
            )
        
        # Балансированная атака
        return CombatDecision(
            action=CombatAction.ATTACK_MELEE,
            priority=0.5,
            reasoning="Балансированная тактическая атака",
            confidence=0.4
        )
    
    def _make_evasive_decision(self, context: CombatContext, analysis: Dict[str, Any]) -> CombatDecision:
        """Принятие решения об уклонении"""
        # Уклонение от атак
        if context.enemy_distance < 3.0:
            return CombatDecision(
                action=CombatAction.DODGE,
                priority=0.8,
                reasoning="Уклонение от близкого врага",
                confidence=0.7
            )
        
        # Отступление
        return CombatDecision(
            action=CombatAction.RETREAT,
            priority=0.7,
            reasoning="Отступление для перегруппировки",
            confidence=0.6
        )
    
    def _make_support_decision(self, context: CombatContext, analysis: Dict[str, Any]) -> CombatDecision:
        """Принятие решения о поддержке"""
        # Поддержка союзников
        if context.allies_nearby > 0:
            return CombatDecision(
                action=CombatAction.BUFF,
                priority=0.7,
                reasoning="Поддержка союзников",
                confidence=0.6
            )
        
        # Переход к тактической стратегии
        return self._make_tactical_decision(context, analysis)
    
    def _make_adaptive_decision(self, context: CombatContext, analysis: Dict[str, Any]) -> CombatDecision:
        """Принятие адаптивного решения"""
        # Использование машинного обучения для выбора действия
        recommended_action = self.combat_learning.recommend_combat_action(
            context.enemy_type,
            context.get_health_percentage(),
            context.available_weapons,
            context.available_items
        )
        
        return CombatDecision(
            action=recommended_action,
            priority=0.6,
            reasoning="Адаптивное решение на основе машинного обучения",
            confidence=0.5
        )
    
    def _learn_from_decision(self, decision: CombatDecision, context: CombatContext):
        """Обучение на основе принятого решения"""
        # Здесь будет логика обучения на основе результатов решения
        # Пока что просто логируем
        logger.debug(f"Обучение на основе решения: {decision}")
    
    def update_combat_knowledge(self, combat_result: Dict[str, Any]):
        """Обновление боевых знаний на основе результата"""
        self.combat_learning.learn_from_combat(combat_result)
        
        # Адаптация параметров на основе результата
        if combat_result.get("victory", False):
            self.aggression_level = min(1.0, self.aggression_level + 0.05)
            self.caution_level = max(0.0, self.caution_level - 0.03)
        else:
            self.aggression_level = max(0.0, self.aggression_level - 0.05)
            self.caution_level = min(1.0, self.caution_level + 0.03)
    
    def get_combat_ai_report(self) -> Dict[str, Any]:
        """Получение отчёта о работе боевого ИИ"""
        return {
            "entity_id": self.entity_id,
            "combat_strategy": self.combat_strategy.value,
            "aggression_level": self.aggression_level,
            "caution_level": self.caution_level,
            "learning_rate": self.learning_rate,
            "exploration_rate": self.exploration_rate,
            "decisions_made": len(self.decision_history),
            "combat_learning_report": self.combat_learning.get_learning_report(),
            "weapon_collection_stats": self.weapon_manager.get_collection_stats()
        }
    
    def save_combat_ai_state(self, filepath: str) -> bool:
        """Сохранение состояния боевого ИИ"""
        try:
            # Сохранение боевых знаний
            combat_knowledge_path = filepath.replace(".json", "_combat.json")
            self.combat_learning.save_combat_knowledge(combat_knowledge_path)
            
            # Сохранение состояния ИИ
            ai_state = {
                "combat_strategy": self.combat_strategy.value,
                "aggression_level": self.aggression_level,
                "caution_level": self.caution_level,
                "learning_rate": self.learning_rate,
                "exploration_rate": self.exploration_rate,
                "decision_history_length": len(self.decision_history)
            }
            
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(ai_state, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Состояние боевого ИИ сохранено в {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения состояния боевого ИИ: {e}")
            return False
    
    def load_combat_ai_state(self, filepath: str) -> bool:
        """Загрузка состояния боевого ИИ"""
        try:
            # Загрузка боевых знаний
            combat_knowledge_path = filepath.replace(".json", "_combat.json")
            self.combat_learning.load_combat_knowledge(combat_knowledge_path)
            
            # Загрузка состояния ИИ
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                ai_state = json.load(f)
            
            # Восстановление параметров
            self.combat_strategy = CombatStrategy(ai_state.get("combat_strategy", "adaptive"))
            self.aggression_level = ai_state.get("aggression_level", 0.5)
            self.caution_level = ai_state.get("caution_level", 0.5)
            self.learning_rate = ai_state.get("learning_rate", 0.1)
            self.exploration_rate = ai_state.get("exploration_rate", 0.2)
            
            logger.info(f"Состояние боевого ИИ загружено из {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки состояния боевого ИИ: {e}")
            return False
