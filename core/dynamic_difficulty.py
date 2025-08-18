"""
Система динамической сложности.
Автоматически адаптирует сложность игры под уровень игрока.
"""

import random
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from collections import deque

logger = logging.getLogger(__name__)


class DifficultyLevel(Enum):
    """Уровни сложности"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    VERY_HARD = "very_hard"
    EXTREME = "extreme"
    NIGHTMARE = "nightmare"


class DifficultyFactor(Enum):
    """Факторы сложности"""
    ENEMY_DAMAGE = "enemy_damage"
    ENEMY_HP = "enemy_hp"
    ENEMY_SPEED = "enemy_speed"
    ENEMY_ACCURACY = "enemy_accuracy"
    ENEMY_AI = "enemy_ai"
    RESOURCE_ABUNDANCE = "resource_abundance"
    ITEM_RARITY = "item_rarity"
    WEATHER_SEVERITY = "weather_severity"
    EVENT_FREQUENCY = "event_frequency"
    MUTATION_RATE = "mutation_rate"
    EMOTIONAL_INTENSITY = "emotional_intensity"
    AI_LEARNING_SPEED = "ai_learning_speed"


@dataclass
class DifficultyParameter:
    """Параметр сложности"""
    name: str
    base_value: float
    current_value: float
    min_value: float
    max_value: float
    adjustment_rate: float
    target_value: float = None
    
    def adjust_towards_target(self, target: float, delta_time: float):
        """Плавная корректировка к целевому значению"""
        if target is None:
            return
        
        difference = target - self.current_value
        if abs(difference) > 0.01:
            adjustment = difference * self.adjustment_rate * delta_time
            self.current_value = max(self.min_value, min(self.max_value, self.current_value + adjustment))
    
    def get_multiplier(self) -> float:
        """Получение множителя сложности"""
        return self.current_value / self.base_value


@dataclass
class PlayerPerformance:
    """Производительность игрока"""
    timestamp: float
    success_rate: float
    survival_time: float
    enemies_defeated: int
    damage_dealt: float
    damage_taken: float
    exploration_progress: float
    genetic_stability: float
    emotional_balance: float
    ai_adaptation: float
    
    def get_overall_score(self) -> float:
        """Расчёт общего балла производительности"""
        # Взвешенная сумма различных метрик
        weights = {
            'success_rate': 0.25,
            'survival_time': 0.15,
            'enemies_defeated': 0.20,
            'damage_ratio': 0.15,
            'exploration_progress': 0.10,
            'genetic_stability': 0.05,
            'emotional_balance': 0.05,
            'ai_adaptation': 0.05
        }
        
        damage_ratio = 0.0
        if self.damage_taken > 0:
            damage_ratio = min(1.0, self.damage_dealt / self.damage_taken)
        
        score = (
            self.success_rate * weights['success_rate'] +
            min(1.0, self.survival_time / 3600.0) * weights['survival_time'] +
            min(1.0, self.enemies_defeated / 100.0) * weights['enemies_defeated'] +
            damage_ratio * weights['damage_ratio'] +
            self.exploration_progress * weights['exploration_progress'] +
            self.genetic_stability * weights['genetic_stability'] +
            self.emotional_balance * weights['emotional_balance'] +
            self.ai_adaptation * weights['ai_adaptation']
        )
        
        return max(0.0, min(1.0, score))


@dataclass
class DifficultyProfile:
    """Профиль сложности"""
    name: str
    description: str
    parameters: Dict[str, DifficultyParameter]
    target_performance: float
    adaptation_speed: float
    
    def get_parameter(self, name: str) -> Optional[DifficultyParameter]:
        """Получение параметра по имени"""
        return self.parameters.get(name)


class DynamicDifficultySystem:
    """Система динамической сложности"""
    
    def __init__(self):
        # Профили сложности
        self.difficulty_profiles: Dict[str, DifficultyProfile] = {}
        
        # Текущий профиль
        self.current_profile: Optional[DifficultyProfile] = None
        
        # Производительность игрока
        self.performance_history: deque = deque(maxlen=100)
        self.current_performance: Optional[PlayerPerformance] = None
        
        # Настройки системы
        self.performance_check_interval = 30.0  # Проверка каждые 30 секунд
        self.last_performance_check = 0.0
        self.adaptation_cooldown = 60.0  # Минимальный интервал между изменениями
        self.last_adaptation = 0.0
        
        # Статистика
        self.total_adaptations = 0
        self.difficulty_changes = 0
        
        # Инициализация профилей сложности
        self._initialize_difficulty_profiles()
        
        logger.info("Система динамической сложности инициализирована")
    
    def _initialize_difficulty_profiles(self):
        """Инициализация профилей сложности"""
        try:
            # Профиль "Очень легко"
            very_easy_params = {
                DifficultyFactor.ENEMY_DAMAGE.value: DifficultyParameter(
                    name="enemy_damage", base_value=1.0, current_value=0.5, min_value=0.3, max_value=0.8, adjustment_rate=0.1
                ),
                DifficultyFactor.ENEMY_HP.value: DifficultyParameter(
                    name="enemy_hp", base_value=1.0, current_value=0.6, min_value=0.4, max_value=0.9, adjustment_rate=0.1
                ),
                DifficultyFactor.ENEMY_SPEED.value: DifficultyParameter(
                    name="enemy_speed", base_value=1.0, current_value=0.7, min_value=0.5, max_value=0.9, adjustment_rate=0.1
                ),
                DifficultyFactor.RESOURCE_ABUNDANCE.value: DifficultyParameter(
                    name="resource_abundance", base_value=1.0, current_value=1.5, min_value=1.2, max_value=2.0, adjustment_rate=0.1
                ),
                DifficultyFactor.ITEM_RARITY.value: DifficultyParameter(
                    name="item_rarity", base_value=1.0, current_value=1.3, min_value=1.1, max_value=1.6, adjustment_rate=0.1
                )
            }
            
            self.difficulty_profiles["very_easy"] = DifficultyProfile(
                name="Очень легко",
                description="Идеально для новичков",
                parameters=very_easy_params,
                target_performance=0.3,
                adaptation_speed=0.05
            )
            
            # Профиль "Легко"
            easy_params = {
                DifficultyFactor.ENEMY_DAMAGE.value: DifficultyParameter(
                    name="enemy_damage", base_value=1.0, current_value=0.7, min_value=0.5, max_value=1.0, adjustment_rate=0.1
                ),
                DifficultyFactor.ENEMY_HP.value: DifficultyParameter(
                    name="enemy_hp", base_value=1.0, current_value=0.8, min_value=0.6, max_value=1.1, adjustment_rate=0.1
                ),
                DifficultyFactor.ENEMY_SPEED.value: DifficultyParameter(
                    name="enemy_speed", base_value=1.0, current_value=0.8, min_value=0.6, max_value=1.0, adjustment_rate=0.1
                ),
                DifficultyFactor.RESOURCE_ABUNDANCE.value: DifficultyParameter(
                    name="resource_abundance", base_value=1.0, current_value=1.2, min_value=1.0, max_value=1.5, adjustment_rate=0.1
                ),
                DifficultyFactor.ITEM_RARITY.value: DifficultyParameter(
                    name="item_rarity", base_value=1.0, current_value=1.1, min_value=1.0, max_value=1.3, adjustment_rate=0.1
                )
            }
            
            self.difficulty_profiles["easy"] = DifficultyProfile(
                name="Легко",
                description="Подходит для начинающих игроков",
                parameters=easy_params,
                target_performance=0.4,
                adaptation_speed=0.08
            )
            
            # Профиль "Нормально"
            normal_params = {
                DifficultyFactor.ENEMY_DAMAGE.value: DifficultyParameter(
                    name="enemy_damage", base_value=1.0, current_value=1.0, min_value=0.8, max_value=1.2, adjustment_rate=0.1
                ),
                DifficultyFactor.ENEMY_HP.value: DifficultyParameter(
                    name="enemy_hp", base_value=1.0, current_value=1.0, min_value=0.8, max_value=1.2, adjustment_rate=0.1
                ),
                DifficultyFactor.ENEMY_SPEED.value: DifficultyParameter(
                    name="enemy_speed", base_value=1.0, current_value=1.0, min_value=0.8, max_value=1.2, adjustment_rate=0.1
                ),
                DifficultyFactor.RESOURCE_ABUNDANCE.value: DifficultyParameter(
                    name="resource_abundance", base_value=1.0, current_value=1.0, min_value=0.8, max_value=1.2, adjustment_rate=0.1
                ),
                DifficultyFactor.ITEM_RARITY.value: DifficultyParameter(
                    name="item_rarity", base_value=1.0, current_value=1.0, min_value=0.8, max_value=1.2, adjustment_rate=0.1
                )
            }
            
            self.difficulty_profiles["normal"] = DifficultyProfile(
                name="Нормально",
                description="Сбалансированная сложность",
                parameters=normal_params,
                target_performance=0.5,
                adaptation_speed=0.1
            )
            
            # Профиль "Сложно"
            hard_params = {
                DifficultyFactor.ENEMY_DAMAGE.value: DifficultyParameter(
                    name="enemy_damage", base_value=1.0, current_value=1.3, min_value=1.1, max_value=1.6, adjustment_rate=0.1
                ),
                DifficultyFactor.ENEMY_HP.value: DifficultyParameter(
                    name="enemy_hp", base_value=1.0, current_value=1.2, min_value=1.0, max_value=1.5, adjustment_rate=0.1
                ),
                DifficultyFactor.ENEMY_SPEED.value: DifficultyParameter(
                    name="enemy_speed", base_value=1.0, current_value=1.2, min_value=1.0, max_value=1.5, adjustment_rate=0.1
                ),
                DifficultyFactor.RESOURCE_ABUNDANCE.value: DifficultyParameter(
                    name="resource_abundance", base_value=1.0, current_value=0.8, min_value=0.6, max_value=1.0, adjustment_rate=0.1
                ),
                DifficultyFactor.ITEM_RARITY.value: DifficultyParameter(
                    name="item_rarity", base_value=1.0, current_value=0.9, min_value=0.7, max_value=1.1, adjustment_rate=0.1
                )
            }
            
            self.difficulty_profiles["hard"] = DifficultyProfile(
                name="Сложно",
                description="Для опытных игроков",
                parameters=hard_params,
                target_performance=0.6,
                adaptation_speed=0.12
            )
            
            # Профиль "Очень сложно"
            very_hard_params = {
                DifficultyFactor.ENEMY_DAMAGE.value: DifficultyParameter(
                    name="enemy_damage", base_value=1.0, current_value=1.6, min_value=1.3, max_value=2.0, adjustment_rate=0.1
                ),
                DifficultyFactor.ENEMY_HP.value: DifficultyParameter(
                    name="enemy_hp", base_value=1.0, current_value=1.5, min_value=1.2, max_value=1.8, adjustment_rate=0.1
                ),
                DifficultyFactor.ENEMY_SPEED.value: DifficultyParameter(
                    name="enemy_speed", base_value=1.0, current_value=1.4, min_value=1.1, max_value=1.7, adjustment_rate=0.1
                ),
                DifficultyFactor.RESOURCE_ABUNDANCE.value: DifficultyParameter(
                    name="resource_abundance", base_value=1.0, current_value=0.6, min_value=0.4, max_value=0.8, adjustment_rate=0.1
                ),
                DifficultyFactor.ITEM_RARITY.value: DifficultyParameter(
                    name="item_rarity", base_value=1.0, current_value=0.7, min_value=0.5, max_value=0.9, adjustment_rate=0.1
                )
            }
            
            self.difficulty_profiles["very_hard"] = DifficultyProfile(
                name="Очень сложно",
                description="Для мастеров игры",
                parameters=very_hard_params,
                target_performance=0.7,
                adaptation_speed=0.15
            )
            
            # Профиль "Экстрим"
            extreme_params = {
                DifficultyFactor.ENEMY_DAMAGE.value: DifficultyParameter(
                    name="enemy_damage", base_value=1.0, current_value=2.0, min_value=1.6, max_value=2.5, adjustment_rate=0.1
                ),
                DifficultyFactor.ENEMY_HP.value: DifficultyParameter(
                    name="enemy_hp", base_value=1.0, current_value=1.8, min_value=1.5, max_value=2.2, adjustment_rate=0.1
                ),
                DifficultyFactor.ENEMY_SPEED.value: DifficultyParameter(
                    name="enemy_speed", base_value=1.0, current_value=1.7, min_value=1.4, max_value=2.0, adjustment_rate=0.1
                ),
                DifficultyFactor.RESOURCE_ABUNDANCE.value: DifficultyParameter(
                    name="resource_abundance", base_value=1.0, current_value=0.4, min_value=0.2, max_value=0.6, adjustment_rate=0.1
                ),
                DifficultyFactor.ITEM_RARITY.value: DifficultyParameter(
                    name="item_rarity", base_value=1.0, current_value=0.5, min_value=0.3, max_value=0.7, adjustment_rate=0.1
                )
            }
            
            self.difficulty_profiles["extreme"] = DifficultyProfile(
                name="Экстрим",
                description="Предельная сложность",
                parameters=extreme_params,
                target_performance=0.8,
                adaptation_speed=0.18
            )
            
            # Профиль "Кошмар"
            nightmare_params = {
                DifficultyFactor.ENEMY_DAMAGE.value: DifficultyParameter(
                    name="enemy_damage", base_value=1.0, current_value=2.5, min_value=2.0, max_value=3.0, adjustment_rate=0.1
                ),
                DifficultyFactor.ENEMY_HP.value: DifficultyParameter(
                    name="enemy_hp", base_value=1.0, current_value=2.2, min_value=1.8, max_value=2.6, adjustment_rate=0.1
                ),
                DifficultyFactor.ENEMY_SPEED.value: DifficultyParameter(
                    name="enemy_speed", base_value=1.0, current_value=2.0, min_value=1.7, max_value=2.3, adjustment_rate=0.1
                ),
                DifficultyFactor.RESOURCE_ABUNDANCE.value: DifficultyParameter(
                    name="resource_abundance", base_value=1.0, current_value=0.2, min_value=0.1, max_value=0.4, adjustment_rate=0.1
                ),
                DifficultyFactor.ITEM_RARITY.value: DifficultyParameter(
                    name="item_rarity", base_value=1.0, current_value=0.3, min_value=0.1, max_value=0.5, adjustment_rate=0.1
                )
            }
            
            self.difficulty_profiles["nightmare"] = DifficultyProfile(
                name="Кошмар",
                description="Невозможная сложность",
                parameters=nightmare_params,
                target_performance=0.9,
                adaptation_speed=0.2
            )
            
            # Установка профиля по умолчанию
            self.set_difficulty_profile("normal")
            
            logger.info(f"Инициализировано {len(self.difficulty_profiles)} профилей сложности")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации профилей сложности: {e}")
    
    def set_difficulty_profile(self, profile_name: str) -> bool:
        """Установка профиля сложности"""
        try:
            if profile_name in self.difficulty_profiles:
                self.current_profile = self.difficulty_profiles[profile_name]
                logger.info(f"Установлен профиль сложности: {self.current_profile.name}")
                return True
            else:
                logger.error(f"Профиль сложности не найден: {profile_name}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка установки профиля сложности: {e}")
            return False
    
    def update(self, delta_time: float, player_data: Dict[str, Any], world_state: Dict[str, Any]):
        """Обновление системы сложности"""
        try:
            current_time = time.time()
            
            # Проверка производительности каждые N секунд
            if current_time - self.last_performance_check >= self.performance_check_interval:
                self._update_player_performance(player_data, world_state)
                self.last_performance_check = current_time
            
            # Адаптация сложности
            if current_time - self.last_adaptation >= self.adaptation_cooldown:
                self._adapt_difficulty(delta_time)
                self.last_adaptation = current_time
            
            # Плавная корректировка параметров
            self._smooth_parameter_adjustments(delta_time)
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы сложности: {e}")
    
    def _update_player_performance(self, player_data: Dict[str, Any], world_state: Dict[str, Any]):
        """Обновление производительности игрока"""
        try:
            # Создание объекта производительности
            performance = PlayerPerformance(
                timestamp=time.time(),
                success_rate=player_data.get("success_rate", 0.5),
                survival_time=player_data.get("survival_time", 0.0),
                enemies_defeated=player_data.get("enemies_defeated", 0),
                damage_dealt=player_data.get("damage_dealt", 0.0),
                damage_taken=player_data.get("damage_taken", 0.0),
                exploration_progress=world_state.get("exploration_percent", 0.0),
                genetic_stability=player_data.get("genetic_stability", 1.0),
                emotional_balance=player_data.get("emotional_balance", 1.0),
                ai_adaptation=player_data.get("ai_adaptation", 0.5)
            )
            
            # Сохранение производительности
            self.current_performance = performance
            self.performance_history.append(performance)
            
            # Ограничение истории
            if len(self.performance_history) > 100:
                self.performance_history.popleft()
                
        except Exception as e:
            logger.error(f"Ошибка обновления производительности игрока: {e}")
    
    def _adapt_difficulty(self, delta_time: float):
        """Адаптация сложности"""
        try:
            if not self.current_profile or not self.current_performance:
                return
            
            # Расчёт средней производительности за последние 10 измерений
            recent_performances = list(self.performance_history)[-10:]
            if len(recent_performances) < 3:
                return
            
            avg_performance = sum(p.get_overall_score() for p in recent_performances) / len(recent_performances)
            target_performance = self.current_profile.target_performance
            
            # Определение направления адаптации
            performance_diff = avg_performance - target_performance
            
            if abs(performance_diff) < 0.05:  # В пределах допустимого отклонения
                return
            
            # Адаптация параметров
            adaptation_factor = self.current_profile.adaptation_speed
            
            if performance_diff > 0:  # Игрок слишком успешен - увеличиваем сложность
                self._increase_difficulty(adaptation_factor, delta_time)
            else:  # Игроку слишком сложно - уменьшаем сложность
                self._decrease_difficulty(adaptation_factor, delta_time)
            
            self.total_adaptations += 1
            
        except Exception as e:
            logger.error(f"Ошибка адаптации сложности: {e}")
    
    def _increase_difficulty(self, factor: float, delta_time: float):
        """Увеличение сложности"""
        try:
            if not self.current_profile:
                return
            
            for param_name, parameter in self.current_profile.parameters.items():
                # Увеличение параметров сложности
                if "damage" in param_name or "hp" in param_name or "speed" in param_name:
                    target_increase = parameter.current_value * (1.0 + factor)
                    parameter.target_value = min(parameter.max_value, target_increase)
                
                # Уменьшение параметров доступности
                elif "abundance" in param_name or "rarity" in param_name:
                    target_decrease = parameter.current_value * (1.0 - factor)
                    parameter.target_value = max(parameter.min_value, target_decrease)
            
            self.difficulty_changes += 1
            logger.info("Сложность увеличена")
            
        except Exception as e:
            logger.error(f"Ошибка увеличения сложности: {e}")
    
    def _decrease_difficulty(self, factor: float, delta_time: float):
        """Уменьшение сложности"""
        try:
            if not self.current_profile:
                return
            
            for param_name, parameter in self.current_profile.parameters.items():
                # Уменьшение параметров сложности
                if "damage" in param_name or "hp" in param_name or "speed" in param_name:
                    target_decrease = parameter.current_value * (1.0 - factor)
                    parameter.target_value = max(parameter.min_value, target_decrease)
                
                # Увеличение параметров доступности
                elif "abundance" in param_name or "rarity" in param_name:
                    target_increase = parameter.current_value * (1.0 + factor)
                    parameter.target_value = min(parameter.max_value, target_increase)
            
            self.difficulty_changes += 1
            logger.info("Сложность уменьшена")
            
        except Exception as e:
            logger.error(f"Ошибка уменьшения сложности: {e}")
    
    def _smooth_parameter_adjustments(self, delta_time: float):
        """Плавная корректировка параметров"""
        try:
            if not self.current_profile:
                return
            
            for parameter in self.current_profile.parameters.values():
                if parameter.target_value is not None:
                    parameter.adjust_towards_target(parameter.target_value, delta_time)
                    
        except Exception as e:
            logger.error(f"Ошибка плавной корректировки параметров: {e}")
    
    def get_difficulty_multiplier(self, factor: str) -> float:
        """Получение множителя сложности для конкретного фактора"""
        try:
            if not self.current_profile:
                return 1.0
            
            parameter = self.current_profile.parameters.get(factor)
            if parameter:
                return parameter.get_multiplier()
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Ошибка получения множителя сложности: {e}")
            return 1.0
    
    def get_current_difficulty_level(self) -> str:
        """Получение текущего уровня сложности"""
        try:
            if not self.current_profile:
                return "unknown"
            
            return self.current_profile.name
            
        except Exception as e:
            logger.error(f"Ошибка получения уровня сложности: {e}")
            return "unknown"
    
    def get_difficulty_stats(self) -> Dict[str, Any]:
        """Получение статистики сложности"""
        try:
            if not self.current_profile:
                return {"error": "Профиль сложности не установлен"}
            
            stats = {
                "current_profile": self.current_profile.name,
                "target_performance": self.current_profile.target_performance,
                "adaptation_speed": self.current_profile.adaptation_speed,
                "total_adaptations": self.total_adaptations,
                "difficulty_changes": self.difficulty_changes,
                "parameters": {}
            }
            
            # Статистика по параметрам
            for param_name, parameter in self.current_profile.parameters.items():
                stats["parameters"][param_name] = {
                    "current_value": parameter.current_value,
                    "base_value": parameter.base_value,
                    "multiplier": parameter.get_multiplier(),
                    "min_value": parameter.min_value,
                    "max_value": parameter.max_value,
                    "target_value": parameter.target_value
                }
            
            # Статистика по производительности
            if self.current_performance:
                stats["current_performance"] = {
                    "overall_score": self.current_performance.get_overall_score(),
                    "success_rate": self.current_performance.success_rate,
                    "survival_time": self.current_performance.survival_time,
                    "enemies_defeated": self.current_performance.enemies_defeated
                }
            
            # История производительности
            if self.performance_history:
                recent_scores = [p.get_overall_score() for p in list(self.performance_history)[-10:]]
                stats["performance_history"] = {
                    "recent_scores": recent_scores,
                    "average_score": sum(recent_scores) / len(recent_scores),
                    "trend": "increasing" if len(recent_scores) > 1 and recent_scores[-1] > recent_scores[0] else "decreasing"
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики сложности: {e}")
            return {"error": str(e)}
    
    def force_difficulty_change(self, profile_name: str) -> bool:
        """Принудительное изменение профиля сложности"""
        try:
            if profile_name in self.difficulty_profiles:
                old_profile = self.current_profile.name if self.current_profile else "none"
                self.set_difficulty_profile(profile_name)
                
                if old_profile != profile_name:
                    self.difficulty_changes += 1
                    logger.info(f"Принудительно изменён профиль сложности с {old_profile} на {profile_name}")
                
                return True
            else:
                logger.error(f"Профиль сложности не найден: {profile_name}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка принудительного изменения сложности: {e}")
            return False
    
    def reset_difficulty(self) -> bool:
        """Сброс сложности к базовым значениям"""
        try:
            if not self.current_profile:
                return False
            
            for parameter in self.current_profile.parameters.values():
                parameter.current_value = parameter.base_value
                parameter.target_value = None
            
            self.difficulty_changes += 1
            logger.info("Сложность сброшена к базовым значениям")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сброса сложности: {e}")
            return False
    
    def save_difficulty_state(self, filepath: str) -> bool:
        """Сохранение состояния системы сложности"""
        try:
            import json
            
            save_data = {
                "current_profile": self.current_profile.name if self.current_profile else None,
                "total_adaptations": self.total_adaptations,
                "difficulty_changes": self.difficulty_changes,
                "performance_history": [
                    {
                        "timestamp": p.timestamp,
                        "success_rate": p.success_rate,
                        "survival_time": p.survival_time,
                        "enemies_defeated": p.enemies_defeated,
                        "damage_dealt": p.damage_dealt,
                        "damage_taken": p.damage_taken,
                        "exploration_progress": p.exploration_progress,
                        "genetic_stability": p.genetic_stability,
                        "emotional_balance": p.emotional_balance,
                        "ai_adaptation": p.ai_adaptation
                    }
                    for p in self.performance_history
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            logger.info(f"Состояние системы сложности сохранено в {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения состояния системы сложности: {e}")
            return False
    
    def load_difficulty_state(self, filepath: str) -> bool:
        """Загрузка состояния системы сложности"""
        try:
            import json
            
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            # Восстановление профиля
            profile_name = save_data.get("current_profile")
            if profile_name and profile_name in self.difficulty_profiles:
                self.set_difficulty_profile(profile_name)
            
            # Восстановление статистики
            self.total_adaptations = save_data.get("total_adaptations", 0)
            self.difficulty_changes = save_data.get("difficulty_changes", 0)
            
            # Восстановление истории производительности
            self.performance_history.clear()
            for perf_data in save_data.get("performance_history", []):
                performance = PlayerPerformance(
                    timestamp=perf_data["timestamp"],
                    success_rate=perf_data["success_rate"],
                    survival_time=perf_data["survival_time"],
                    enemies_defeated=perf_data["enemies_defeated"],
                    damage_dealt=perf_data["damage_dealt"],
                    damage_taken=perf_data["damage_taken"],
                    exploration_progress=perf_data["exploration_progress"],
                    genetic_stability=perf_data["genetic_stability"],
                    emotional_balance=perf_data["emotional_balance"],
                    ai_adaptation=perf_data["ai_adaptation"]
                )
                self.performance_history.append(performance)
            
            logger.info(f"Состояние системы сложности загружено из {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки состояния системы сложности: {e}")
            return False
