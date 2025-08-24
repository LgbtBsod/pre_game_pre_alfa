#!/usr/bin/env python3
"""
Мастер-система Enhanced Edition.
Интегрирует все улучшенные системы из культовых игр.
Координирует взаимодействие между всеми компонентами.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Импорт всех расширенных систем
from .generational_memory_system import GenerationalMemorySystem
from .emotional_ai_influence import EmotionalAIInfluenceSystem
from .enhanced_combat_learning import EnhancedCombatLearningSystem
from .enhanced_content_generator import EnhancedContentGenerator
from .enhanced_skill_system import SkillManager, SkillLearningAI
from .curse_blessing_system import CurseBlessingSystem, CurseType, BlessingType
from .risk_reward_system import RiskRewardSystem, RiskLevel
from .meta_progression_system import MetaProgressionSystem, MetaCurrency
from .enhanced_inventory_system import EnhancedInventorySystem
from .enhanced_ui_system import EnhancedUISystem, UIState
from .emotion_system import AdvancedEmotionSystem, EmotionCode

logger = logging.getLogger(__name__)


class GamePhase(Enum):
    """Фазы игры"""
    INITIALIZATION = "initialization"
    MAIN_MENU = "main_menu"
    CHARACTER_CREATION = "character_creation"
    GAMEPLAY = "gameplay"
    EVOLUTION = "evolution"
    DEATH = "death"
    META_PROGRESSION = "meta_progression"
    CREDITS = "credits"


class DifficultyMode(Enum):
    """Режимы сложности"""
    STORY = "story"           # Сюжетный режим
    NORMAL = "normal"         # Обычный
    HARD = "hard"             # Сложный
    NIGHTMARE = "nightmare"   # Кошмар
    HELL = "hell"             # Ад
    CUSTOM = "custom"         # Пользовательский


@dataclass
class GameSession:
    """Игровая сессия"""
    session_id: str
    start_time: float
    current_phase: GamePhase
    difficulty: DifficultyMode
    player_stats: Dict[str, Any] = field(default_factory=dict)
    run_statistics: Dict[str, Any] = field(default_factory=dict)
    achievements_earned: List[str] = field(default_factory=list)
    
    def get_playtime(self) -> float:
        """Получение времени игры"""
        return time.time() - self.start_time


class EnhancedGameMaster:
    """Мастер-система Enhanced Edition"""
    
    def __init__(self, screen_width: int = 1600, screen_height: int = 900):
        logger.info("🎮 Инициализация Enhanced Game Master...")
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Текущая сессия
        self.current_session: Optional[GameSession] = None
        
        # Основные системы
        self.memory_system = GenerationalMemorySystem()
        self.emotional_ai_system = EmotionalAIInfluenceSystem(self.memory_system)
        self.emotion_system = AdvancedEmotionSystem(None)  # effect_db будет инициализирован позже
        
        # Системы проклятий и рисков
        self.curse_blessing_system = CurseBlessingSystem(self.memory_system)
        self.risk_reward_system = RiskRewardSystem(self.memory_system, self.curse_blessing_system)
        
        # Боевые системы
        self.combat_learning_system = EnhancedCombatLearningSystem(
            self.memory_system,
            self.emotional_ai_system,
            self.curse_blessing_system,
            self.risk_reward_system
        )
        
        # Системы контента и навыков
        self.content_generator = EnhancedContentGenerator(self.memory_system)
        self.skill_manager = SkillManager(self.memory_system, self.emotional_ai_system)
        self.skill_learning_ai = SkillLearningAI(self.skill_manager, None)
        
        # Системы прогрессии и инвентаря
        self.meta_progression_system = MetaProgressionSystem(self.memory_system)
        self.inventory_system = EnhancedInventorySystem(self.memory_system)
        
        # Система интерфейса
        self.ui_system = EnhancedUISystem(screen_width, screen_height)
        
        # Интеграционные системы
        self.event_coordinator = EventCoordinator()
        self.synergy_manager = SynergyManager()
        self.balance_controller = BalanceController()
        
        # Статистика и аналитика
        self.analytics_system = AnalyticsSystem()
        
        logger.info("✅ Enhanced Game Master инициализирован")
    
    def start_new_session(self, difficulty: DifficultyMode = DifficultyMode.NORMAL) -> str:
        """Начало новой игровой сессии"""
        session_id = f"session_{int(time.time())}"
        
        self.current_session = GameSession(
            session_id=session_id,
            start_time=time.time(),
            current_phase=GamePhase.CHARACTER_CREATION,
            difficulty=difficulty
        )
        
        # Инициализация сессии
        self._initialize_session()
        
        logger.info(f"🎯 Начата новая сессия: {session_id} (сложность: {difficulty.value})")
        return session_id
    
    def update(self, delta_time: float, input_events: List[Any]) -> Dict[str, Any]:
        """Основной цикл обновления"""
        if not self.current_session:
            return {"status": "no_session"}
        
        # Обновление основных систем
        self._update_core_systems(delta_time)
        
        # Обновление UI
        self.ui_system.update(delta_time, input_events)
        
        # Координация событий
        events = self.event_coordinator.process_events(delta_time)
        
        # Обработка событий системами
        self._process_system_events(events)
        
        # Проверка синергий
        self.synergy_manager.update(delta_time)
        
        # Балансировка сложности
        self.balance_controller.update(delta_time)
        
        # Аналитика
        self.analytics_system.record_frame_data(delta_time)
        
        return {
            "status": "running",
            "phase": self.current_session.current_phase.value,
            "playtime": self.current_session.get_playtime(),
            "events": events
        }
    
    def trigger_evolution_event(self, entity_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Активация события эволюции"""
        logger.info(f"🧬 Событие эволюции для {entity_id}")
        
        # Проверка условий эволюции
        evolution_ready = self._check_evolution_conditions(entity_id, context)
        if not evolution_ready:
            return {"success": False, "reason": "Evolution conditions not met"}
        
        # Генерация эволюционных вариантов
        evolution_options = self._generate_evolution_options(entity_id, context)
        
        # Влияние памяти поколений на эволюцию
        memory_influence = self.memory_system.influence_decision(
            context, [opt["id"] for opt in evolution_options]
        )
        
        # Эмоциональное влияние
        emotional_state = self.emotion_system.current_state
        emotional_influence = self._calculate_emotional_evolution_influence(emotional_state)
        
        # Применение эволюции
        selected_option = self._select_evolution_option(
            evolution_options, memory_influence, emotional_influence
        )
        
        evolution_result = self._apply_evolution(entity_id, selected_option, context)
        
        # Запись в память поколений
        self.memory_system.add_memory(
            memory_type="evolutionary_success",
            content={
                "entity_id": entity_id,
                "evolution_option": selected_option,
                "result": evolution_result,
                "context": context
            },
            intensity=0.8,
            emotional_impact=0.6
        )
        
        # Обновление мета-прогрессии
        self.meta_progression_system.award_currency(
            MetaCurrency.EVOLUTION_POINTS, 
            evolution_result.get("evolution_points", 10),
            "evolution_event"
        )
        
        return evolution_result
    
    def trigger_combat_encounter(self, enemy_data: Dict[str, Any], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Активация боевого столкновения"""
        logger.info(f"⚔️ Боевое столкновение: {enemy_data.get('name', 'Unknown')}")
        
        # Генерация врага с учётом контекста
        enemy = self.content_generator.generate_enemy(
            enemy_data["biome"], enemy_data["level"], context
        )
        
        # Применение модификаторов сложности
        risk_level = self.risk_reward_system.calculate_current_risk()
        enemy = self._apply_risk_modifiers_to_enemy(enemy, risk_level)
        
        # Инициализация боевого контекста
        combat_context = self.combat_learning_system.CombatContext(
            entity_id="player",
            target_id=enemy.guid,
            current_phase=self.combat_learning_system.CombatPhase.ENGAGE,
            active_tactic=self.combat_learning_system.CombatTactic.AGGRESSIVE_RUSH,
            health_percent=context.get("player_health", 1.0),
            stamina_percent=context.get("player_stamina", 1.0),
            distance_to_target=context.get("distance", 100.0),
            target_health_percent=1.0,
            environmental_hazards=context.get("hazards", []),
            available_cover=context.get("cover", []),
            emotional_state=self.emotion_system.current_state.get_dominant_emotion() or "neutral",
            combat_duration=0.0,
            pattern_success_history=[]
        )
        
        # Принятие боевого решения ИИ
        combat_decision = self.combat_learning_system.make_combat_decision("player", combat_context)
        
        # Выполнение боя
        combat_result = self._execute_combat(enemy, combat_context, combat_decision)
        
        # Обучение на результате
        self.combat_learning_system.learn_from_combat_result(
            "player", combat_context, combat_decision, combat_result
        )
        
        # Обработка результатов боя
        self._process_combat_results(combat_result, context)
        
        return combat_result
    
    def trigger_item_discovery(self, item_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Активация обнаружения предмета"""
        logger.info(f"💎 Обнаружен предмет: {item_type}")
        
        # Генерация предмета с учётом рисков и наград
        reward_multiplier = self.risk_reward_system.calculate_reward_multiplier()
        
        # Добавление в инвентарь
        item_added = self.inventory_system.add_item(item_type, {
            "reward_multiplier": reward_multiplier,
            "context": context
        })
        
        if item_added:
            # Проверка синергий
            suggestions = self.inventory_system.suggest_item_combinations()
            
            # Уведомление UI
            self.ui_system.show_notification(
                f"Найден предмет: {item_type}",
                "item_discovery",
                3.0
            )
            
            return {
                "success": True,
                "item_type": item_type,
                "reward_multiplier": reward_multiplier,
                "synergy_suggestions": suggestions
            }
        
        return {"success": False, "reason": "Could not add item"}
    
    def trigger_curse_blessing_event(self, event_type: str, 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Активация события проклятия/благословения"""
        logger.info(f"✨ Событие проклятия/благословения: {event_type}")
        
        if event_type.startswith("curse_"):
            curse_type = getattr(CurseType, event_type.replace("curse_", "").upper(), None)
            if curse_type:
                effect_id = self.curse_blessing_system.apply_curse(
                    curse_type, 
                    context.get("intensity", 1.0),
                    context.get("duration", -1),
                    context.get("source", "event")
                )
                
                return {
                    "success": True,
                    "type": "curse",
                    "effect_id": effect_id,
                    "curse_type": curse_type.value
                }
        
        elif event_type.startswith("blessing_"):
            blessing_type = getattr(BlessingType, event_type.replace("blessing_", "").upper(), None)
            if blessing_type:
                effect_id = self.curse_blessing_system.apply_blessing(
                    blessing_type,
                    context.get("intensity", 1.0),
                    context.get("duration", -1),
                    context.get("source", "event")
                )
                
                return {
                    "success": True,
                    "type": "blessing",
                    "effect_id": effect_id,
                    "blessing_type": blessing_type.value
                }
        
        return {"success": False, "reason": "Unknown event type"}
    
    def end_session(self, reason: str = "player_quit") -> Dict[str, Any]:
        """Завершение игровой сессии"""
        if not self.current_session:
            return {"success": False, "reason": "No active session"}
        
        logger.info(f"🏁 Завершение сессии: {reason}")
        
        # Сбор статистики сессии
        session_stats = self._collect_session_statistics()
        
        # Расчёт наград
        rewards = self.meta_progression_system.calculate_run_rewards(session_stats)
        
        # Начисление валют
        for currency, amount in rewards.items():
            self.meta_progression_system.award_currency(currency, amount, "session_end")
        
        # Проверка достижений
        new_achievements = self.meta_progression_system.check_achievements(session_stats)
        
        # Переход поколения
        if reason == "death" or reason == "completed":
            survival_rate = 1.0 if reason == "completed" else 0.0
            self.memory_system.advance_generation(
                survival_rate, 
                [ach.id for ach in new_achievements]
            )
        
        # Очистка временных эффектов
        self.curse_blessing_system.cleanup_expired_effects()
        
        # Сохранение прогресса
        self._save_session_progress()
        
        session_summary = {
            "session_id": self.current_session.session_id,
            "playtime": self.current_session.get_playtime(),
            "reason": reason,
            "statistics": session_stats,
            "rewards": rewards,
            "new_achievements": [ach.name for ach in new_achievements],
            "generation": self.memory_system.current_generation
        }
        
        self.current_session = None
        
        return session_summary
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получение состояния всех систем"""
        return {
            "memory_system": self.memory_system.get_memory_statistics(),
            "risk_reward": self.risk_reward_system.get_risk_statistics(),
            "curse_blessing": self.curse_blessing_system.get_active_effects_summary(),
            "meta_progression": self.meta_progression_system.get_meta_statistics(),
            "inventory": len(self.inventory_system.inventory),
            "ui_state": self.ui_system.current_state.value,
            "session": {
                "active": self.current_session is not None,
                "phase": self.current_session.current_phase.value if self.current_session else None,
                "playtime": self.current_session.get_playtime() if self.current_session else 0
            }
        }
    
    def _initialize_session(self):
        """Инициализация новой сессии"""
        # Применение мета-бонусов
        meta_bonuses = self.meta_progression_system.get_meta_bonuses()
        
        # Получение наследственных черт
        inheritance_traits = self.meta_progression_system.get_inheritance_traits()
        
        # Инициализация статистики
        self.current_session.run_statistics = {
            "enemies_defeated": 0,
            "bosses_defeated": 0,
            "items_found": 0,
            "evolution_events": 0,
            "deaths": 0,
            "secrets_found": 0,
            "meta_bonuses": meta_bonuses,
            "inheritance_traits": inheritance_traits
        }
        
        # Установка начального состояния UI
        self.ui_system.change_state(UIState.IN_GAME)
    
    def _update_core_systems(self, delta_time: float):
        """Обновление основных систем"""
        # Обновление эмоциональной системы
        self.emotion_system.update(delta_time)
        
        # Очистка истёкших эффектов
        self.curse_blessing_system.cleanup_expired_effects()
        
        # Очистка устаревших воспоминаний
        if random.random() < 0.001:  # 0.1% шанс каждый кадр
            self.memory_system.cleanup_expired_memories()
    
    def _process_system_events(self, events: List[Dict[str, Any]]):
        """Обработка системных событий"""
        for event in events:
            event_type = event.get("type")
            
            if event_type == "emotion_trigger":
                self.emotion_system.trigger_emotion(
                    event["emotion_code"],
                    event.get("intensity", 1.0),
                    event.get("source", "system")
                )
            
            elif event_type == "risk_factor_added":
                self.risk_reward_system.add_risk_factor(
                    event["factor_name"],
                    event["description"],
                    event["multiplier"]
                )
            
            elif event_type == "skill_learned":
                self.skill_manager.learn_skill(
                    event["skill_id"],
                    event["entity_id"],
                    event.get("context", {})
                )
    
    def _check_evolution_conditions(self, entity_id: str, context: Dict[str, Any]) -> bool:
        """Проверка условий эволюции"""
        # Базовые условия
        required_experience = context.get("required_experience", 100)
        current_experience = context.get("current_experience", 0)
        
        if current_experience < required_experience:
            return False
        
        # Проверка эмоционального состояния
        emotional_state = self.emotion_system.current_state
        if emotional_state.emotional_stability < 0.3:
            return False  # Слишком нестабильное состояние
        
        return True
    
    def _generate_evolution_options(self, entity_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Генерация вариантов эволюции"""
        # Базовые варианты эволюции
        base_options = [
            {
                "id": "combat_evolution",
                "name": "Боевая эволюция",
                "description": "Улучшение боевых характеристик",
                "bonuses": {"attack": 10, "defense": 5},
                "requirements": {"combat_experience": 50}
            },
            {
                "id": "mental_evolution",
                "name": "Ментальная эволюция",
                "description": "Улучшение интеллекта и памяти",
                "bonuses": {"intelligence": 15, "memory_capacity": 20},
                "requirements": {"learning_points": 30}
            },
            {
                "id": "adaptive_evolution",
                "name": "Адаптивная эволюция",
                "description": "Улучшение адаптивности и выживаемости",
                "bonuses": {"adaptability": 20, "survival_instinct": 10},
                "requirements": {"survival_time": 1800}  # 30 минут
            }
        ]
        
        # Фильтрация по требованиям
        available_options = []
        for option in base_options:
            requirements_met = True
            for req, value in option["requirements"].items():
                if context.get(req, 0) < value:
                    requirements_met = False
                    break
            
            if requirements_met:
                available_options.append(option)
        
        return available_options or base_options[:1]  # Минимум один вариант
    
    def _calculate_emotional_evolution_influence(self, emotional_state) -> Dict[str, float]:
        """Расчёт эмоционального влияния на эволюцию"""
        influence = {}
        
        dominant_emotion = emotional_state.get_dominant_emotion()
        if dominant_emotion:
            if dominant_emotion in ["rage", "excitement"]:
                influence["combat_bias"] = 0.3
            elif dominant_emotion in ["curiosity", "trust"]:
                influence["mental_bias"] = 0.3
            elif dominant_emotion in ["fear", "calmness"]:
                influence["adaptive_bias"] = 0.3
        
        return influence
    
    def _select_evolution_option(self, options: List[Dict[str, Any]], 
                                memory_influence: Dict[str, float],
                                emotional_influence: Dict[str, float]) -> Dict[str, Any]:
        """Выбор варианта эволюции"""
        if not options:
            return {}
        
        # Простой выбор на основе весов
        weights = []
        for option in options:
            weight = 1.0
            
            # Влияние памяти
            if option["id"] in memory_influence:
                weight *= memory_influence[option["id"]]
            
            # Эмоциональное влияние
            option_type = option["id"].split("_")[0]
            bias_key = f"{option_type}_bias"
            if bias_key in emotional_influence:
                weight += emotional_influence[bias_key]
            
            weights.append(weight)
        
        # Взвешенный случайный выбор
        return random.choices(options, weights=weights)[0]
    
    def _apply_evolution(self, entity_id: str, evolution_option: Dict[str, Any], 
                        context: Dict[str, Any]) -> Dict[str, Any]:
        """Применение эволюции"""
        bonuses = evolution_option.get("bonuses", {})
        
        # Применение бонусов (в реальной игре это бы изменило характеристики сущности)
        applied_bonuses = {}
        for bonus_type, value in bonuses.items():
            applied_bonuses[bonus_type] = value
        
        return {
            "success": True,
            "evolution_id": evolution_option["id"],
            "evolution_name": evolution_option["name"],
            "applied_bonuses": applied_bonuses,
            "evolution_points": sum(bonuses.values())
        }
    
    def _apply_risk_modifiers_to_enemy(self, enemy, risk_level: float):
        """Применение модификаторов риска к врагу"""
        # Увеличение характеристик врага на основе уровня риска
        multiplier = 1.0 + (risk_level - 1.0) * 0.5
        
        # Получаем статистику врага или создаем пустую
        enemy_stats = getattr(enemy, 'stats', {})
        if not enemy_stats:
            enemy_stats = {"health": 100, "damage": 20, "speed": 1.0}
        
        # Применяем модификаторы
        for stat in enemy_stats:
            enemy_stats[stat] *= multiplier
        
        return enemy
    
    def _execute_combat(self, enemy, combat_context, combat_decision) -> Dict[str, Any]:
        """Выполнение боя"""
        # Упрощённая логика боя
        player_power = 100  # Базовая сила игрока
        enemy_power = getattr(enemy, 'power_level', 50)  # Получаем силу врага или используем значение по умолчанию
        
        # Влияние решения ИИ
        decision_confidence = getattr(combat_decision, 'confidence', 0.5)
        decision_modifier = decision_confidence * 0.5 + 0.5
        effective_player_power = player_power * decision_modifier
        
        # Определение результата
        success = effective_player_power > enemy_power * 0.8
        
        return {
            "success": success,
            "player_power": effective_player_power,
            "enemy_power": enemy_power,
            "decision_quality": decision_confidence,
            "experience_gained": int(enemy_power * 0.1),
            "damage_dealt": int(effective_player_power * 0.8),
            "damage_taken": int(enemy_power * 0.3) if not success else 0
        }
    
    def _process_combat_results(self, combat_result: Dict[str, Any], context: Dict[str, Any]):
        """Обработка результатов боя"""
        if combat_result["success"]:
            # Успешный бой
            self.current_session.run_statistics["enemies_defeated"] += 1
            
            # Начисление опыта
            experience = combat_result.get("experience_gained", 0)
            
            # Эмоциональная реакция на победу
            self.emotion_system.trigger_emotion(
                "joy", 0.6, "combat_victory"
            )
            
        else:
            # Поражение
            self.current_session.run_statistics["deaths"] += 1
            
            # Эмоциональная реакция на поражение
            self.emotion_system.trigger_emotion(
                "fear", 0.8, "combat_defeat"
            )
    
    def _collect_session_statistics(self) -> Dict[str, Any]:
        """Сбор статистики сессии"""
        if not self.current_session:
            return {}
        
        stats = self.current_session.run_statistics.copy()
        stats.update({
            "playtime": self.current_session.get_playtime(),
            "phase": self.current_session.current_phase.value,
            "difficulty": self.current_session.difficulty.value,
            "survived": self.current_session.current_phase != GamePhase.DEATH
        })
        
        return stats
    
    def _save_session_progress(self):
        """Сохранение прогресса сессии"""
        # В реальной реализации здесь был бы код сохранения в файл
        logger.info("💾 Прогресс сессии сохранён")


class EventCoordinator:
    """Координатор событий между системами"""
    
    def __init__(self):
        self.pending_events: List[Dict[str, Any]] = []
        self.event_history: List[Dict[str, Any]] = []
    
    def process_events(self, delta_time: float) -> List[Dict[str, Any]]:
        """Обработка событий"""
        processed_events = self.pending_events.copy()
        self.pending_events.clear()
        
        # Добавление в историю
        self.event_history.extend(processed_events)
        
        # Ограничение истории
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-500:]
        
        return processed_events
    
    def queue_event(self, event: Dict[str, Any]):
        """Добавление события в очередь"""
        event["timestamp"] = time.time()
        self.pending_events.append(event)


class SynergyManager:
    """Менеджер синергий между системами"""
    
    def __init__(self):
        self.active_synergies: List[str] = []
        self.synergy_effects: Dict[str, Dict[str, Any]] = {}
    
    def update(self, delta_time: float):
        """Обновление синергий"""
        # Проверка активных синергий
        pass
    
    def check_synergy(self, systems: List[str]) -> Optional[str]:
        """Проверка синергии между системами"""
        # Логика проверки синергий
        return None


class BalanceController:
    """Контроллер баланса игры"""
    
    def __init__(self):
        self.difficulty_adjustments: Dict[str, float] = {}
        self.balance_history: List[Dict[str, Any]] = []
    
    def update(self, delta_time: float):
        """Обновление баланса"""
        # Анализ сложности и корректировка
        pass
    
    def adjust_difficulty(self, system: str, adjustment: float):
        """Корректировка сложности"""
        self.difficulty_adjustments[system] = adjustment


class AnalyticsSystem:
    """Система аналитики и метрик"""
    
    def __init__(self):
        self.frame_data: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, float] = {}
    
    def record_frame_data(self, delta_time: float):
        """Запись данных кадра"""
        self.frame_data.append({
            "timestamp": time.time(),
            "delta_time": delta_time,
            "fps": 1.0 / delta_time if delta_time > 0 else 0
        })
        
        # Ограничение истории
        if len(self.frame_data) > 1000:
            self.frame_data = self.frame_data[-500:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Получение сводки производительности"""
        if not self.frame_data:
            return {}
        
        recent_fps = [frame["fps"] for frame in self.frame_data[-60:]]  # Последние 60 кадров
        
        return {
            "average_fps": sum(recent_fps) / len(recent_fps),
            "min_fps": min(recent_fps),
            "max_fps": max(recent_fps),
            "frame_count": len(self.frame_data)
        }
