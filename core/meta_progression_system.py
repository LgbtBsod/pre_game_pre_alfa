#!/usr/bin/env python3
"""
Система мета-прогрессии.
Вдохновлено Hades, Rogue Legacy, Darkest Dungeon.
Обеспечивает долгосрочный прогресс между запусками игры.
"""

import random
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

from .generational_memory_system import GenerationalMemorySystem, MemoryType

logger = logging.getLogger(__name__)


class MetaUpgradeType(Enum):
    """Типы мета-улучшений"""
    # Боевые улучшения (Hades)
    WEAPON_MASTERY = "weapon_mastery"       # Мастерство оружия
    COMBAT_PROWESS = "combat_prowess"       # Боевое мастерство
    DEFENSIVE_TRAINING = "defensive_training" # Оборонительная подготовка
    CRITICAL_MASTERY = "critical_mastery"   # Мастерство критических ударов
    
    # Исследовательские улучшения
    EXPLORATION_EFFICIENCY = "exploration_efficiency" # Эффективность исследования
    TREASURE_SENSE = "treasure_sense"       # Чувство сокровищ
    SECRET_DETECTION = "secret_detection"   # Обнаружение секретов
    NAVIGATION_MASTERY = "navigation_mastery" # Мастерство навигации
    
    # Эволюционные улучшения
    EVOLUTION_SPEED = "evolution_speed"     # Скорость эволюции
    GENETIC_STABILITY = "genetic_stability" # Генетическая стабильность
    MUTATION_CONTROL = "mutation_control"   # Контроль мутаций
    ADAPTATION_RATE = "adaptation_rate"     # Скорость адаптации
    
    # Ментальные улучшения (Darkest Dungeon)
    STRESS_RESISTANCE = "stress_resistance" # Сопротивление стрессу
    MEMORY_RETENTION = "memory_retention"   # Удержание памяти
    EMOTIONAL_CONTROL = "emotional_control" # Эмоциональный контроль
    WISDOM_ACCUMULATION = "wisdom_accumulation" # Накопление мудрости
    
    # Социальные улучшения
    LEADERSHIP = "leadership"               # Лидерство
    DIPLOMACY = "diplomacy"                 # Дипломатия
    TRADE_MASTERY = "trade_mastery"         # Торговое мастерство
    ALLIANCE_BUILDING = "alliance_building" # Построение альянсов


class MetaCurrency(Enum):
    """Мета-валюты"""
    ESSENCE = "essence"                     # Эссенция (основная валюта)
    MEMORY_FRAGMENTS = "memory_fragments"   # Фрагменты памяти
    EVOLUTION_POINTS = "evolution_points"   # Очки эволюции
    WISDOM_CRYSTALS = "wisdom_crystals"     # Кристаллы мудрости
    ANCESTRAL_FAVOR = "ancestral_favor"     # Благосклонность предков
    DIMENSIONAL_SHARDS = "dimensional_shards" # Измерительные осколки


@dataclass
class MetaUpgrade:
    """Мета-улучшение"""
    id: str
    name: str
    description: str
    upgrade_type: MetaUpgradeType
    current_level: int
    max_level: int
    base_cost: int
    cost_multiplier: float
    currency_type: MetaCurrency
    
    # Эффекты улучшения
    stat_bonuses: Dict[str, float] = field(default_factory=dict)
    special_effects: List[str] = field(default_factory=list)
    unlock_requirements: Dict[str, Any] = field(default_factory=dict)
    
    def get_current_cost(self) -> int:
        """Получение стоимости следующего уровня"""
        if self.current_level >= self.max_level:
            return -1  # Максимальный уровень достигнут
        
        return int(self.base_cost * (self.cost_multiplier ** self.current_level))
    
    def get_total_bonus(self, stat: str) -> float:
        """Получение общего бонуса к характеристике"""
        if stat not in self.stat_bonuses:
            return 0.0
        
        return self.stat_bonuses[stat] * self.current_level
    
    def can_upgrade(self, available_currency: int) -> bool:
        """Проверка возможности улучшения"""
        if self.current_level >= self.max_level:
            return False
        
        return available_currency >= self.get_current_cost()


@dataclass
class MetaAchievement:
    """Мета-достижение"""
    id: str
    name: str
    description: str
    requirements: Dict[str, Any]
    rewards: Dict[MetaCurrency, int]
    special_unlocks: List[str]
    completed: bool = False
    progress: Dict[str, float] = field(default_factory=dict)
    
    def check_completion(self, stats: Dict[str, Any]) -> bool:
        """Проверка выполнения достижения"""
        if self.completed:
            return True
        
        for requirement, target_value in self.requirements.items():
            current_value = stats.get(requirement, 0)
            if isinstance(target_value, dict):
                # Сложное требование
                if not self._check_complex_requirement(requirement, target_value, stats):
                    return False
            else:
                # Простое числовое требование
                if current_value < target_value:
                    return False
        
        self.completed = True
        return True
    
    def _check_complex_requirement(self, req_name: str, req_data: Dict[str, Any],
                                  stats: Dict[str, Any]) -> bool:
        """Проверка сложного требования"""
        req_type = req_data.get("type", "greater_than")
        target = req_data.get("value", 0)
        current = stats.get(req_name, 0)
        
        if req_type == "greater_than":
            return current >= target
        elif req_type == "less_than":
            return current <= target
        elif req_type == "equal":
            return current == target
        elif req_type == "between":
            min_val, max_val = target
            return min_val <= current <= max_val
        
        return False


class MetaProgressionSystem:
    """Система мета-прогрессии"""
    
    def __init__(self, memory_system: GenerationalMemorySystem):
        self.memory_system = memory_system
        
        # Мета-валюты
        self.currencies: Dict[MetaCurrency, int] = {
            currency: 0 for currency in MetaCurrency
        }
        
        # Мета-улучшения
        self.upgrades: Dict[str, MetaUpgrade] = {}
        
        # Мета-достижения
        self.achievements: Dict[str, MetaAchievement] = {}
        
        # Статистика всех запусков
        self.lifetime_stats: Dict[str, Any] = {}
        
        # Система наследования (Rogue Legacy)
        self.inheritance_system = InheritanceSystem()
        
        # Система божественных благосклонностей (Hades)
        self.divine_favor_system = DivineFavorSystem()
        
        # Инициализация
        self._init_meta_upgrades()
        self._init_meta_achievements()
        self._load_meta_progress()
        
        logger.info("Система мета-прогрессии инициализирована")
    
    def award_currency(self, currency_type: MetaCurrency, amount: int,
                      source: str = "unknown"):
        """Начисление мета-валюты"""
        old_amount = self.currencies[currency_type]
        self.currencies[currency_type] += amount
        
        # Запись в память
        self._record_currency_award(currency_type, amount, source)
        
        logger.info(f"Начислено {amount} {currency_type.value} (было: {old_amount}, стало: {self.currencies[currency_type]})")
    
    def upgrade_meta_stat(self, upgrade_id: str) -> bool:
        """Улучшение мета-характеристики"""
        if upgrade_id not in self.upgrades:
            logger.warning(f"Неизвестное улучшение: {upgrade_id}")
            return False
        
        upgrade = self.upgrades[upgrade_id]
        cost = upgrade.get_current_cost()
        
        if cost == -1:
            logger.info(f"Улучшение {upgrade_id} уже на максимальном уровне")
            return False
        
        if not upgrade.can_upgrade(self.currencies[upgrade.currency_type]):
            logger.info(f"Недостаточно {upgrade.currency_type.value} для улучшения {upgrade_id}")
            return False
        
        # Тратим валюту и улучшаем
        self.currencies[upgrade.currency_type] -= cost
        upgrade.current_level += 1
        
        # Запись в память
        self._record_upgrade_purchase(upgrade)
        
        logger.info(f"Улучшение {upgrade_id} повышено до уровня {upgrade.current_level}")
        return True
    
    def calculate_run_rewards(self, run_stats: Dict[str, Any]) -> Dict[MetaCurrency, int]:
        """Расчёт наград за прохождение"""
        rewards = {currency: 0 for currency in MetaCurrency}
        
        # Базовые награды
        base_essence = run_stats.get("enemies_defeated", 0) * 2
        base_essence += run_stats.get("bosses_defeated", 0) * 50
        base_essence += run_stats.get("levels_completed", 0) * 25
        rewards[MetaCurrency.ESSENCE] = base_essence
        
        # Фрагменты памяти за важные события
        memory_fragments = 0
        memory_fragments += run_stats.get("secrets_found", 0) * 5
        memory_fragments += run_stats.get("perfect_battles", 0) * 3
        memory_fragments += run_stats.get("evolution_events", 0) * 10
        rewards[MetaCurrency.MEMORY_FRAGMENTS] = memory_fragments
        
        # Очки эволюции
        evolution_points = run_stats.get("evolution_stages", 0) * 15
        evolution_points += run_stats.get("successful_mutations", 0) * 8
        rewards[MetaCurrency.EVOLUTION_POINTS] = evolution_points
        
        # Кристаллы мудрости за выживание
        if run_stats.get("survived", False):
            wisdom_crystals = run_stats.get("survival_time", 0) // 300  # Каждые 5 минут
            wisdom_crystals += run_stats.get("generation_number", 1)
            rewards[MetaCurrency.WISDOM_CRYSTALS] = wisdom_crystals
        
        # Благосклонность предков за достижения
        ancestral_favor = len(run_stats.get("achievements", [])) * 3
        if run_stats.get("perfect_run", False):
            ancestral_favor += 20
        rewards[MetaCurrency.ANCESTRAL_FAVOR] = ancestral_favor
        
        # Измерительные осколки за экстремальные события
        dimensional_shards = run_stats.get("dimensional_events", 0) * 2
        dimensional_shards += run_stats.get("reality_breaks", 0) * 5
        rewards[MetaCurrency.DIMENSIONAL_SHARDS] = dimensional_shards
        
        # Применение мультипликаторов от улучшений
        self._apply_reward_multipliers(rewards)
        
        return rewards
    
    def check_achievements(self, run_stats: Dict[str, Any]):
        """Проверка выполнения достижений"""
        newly_completed = []
        
        # Обновляем общую статистику
        self._update_lifetime_stats(run_stats)
        
        for achievement in self.achievements.values():
            if achievement.check_completion(self.lifetime_stats):
                if not achievement.completed:
                    newly_completed.append(achievement)
                    
                    # Выдаём награды
                    for currency, amount in achievement.rewards.items():
                        self.award_currency(currency, amount, f"achievement_{achievement.id}")
                    
                    # Разблокируем специальные возможности
                    for unlock in achievement.special_unlocks:
                        self._unlock_special_feature(unlock)
        
        if newly_completed:
            logger.info(f"Выполнено достижений: {[a.name for a in newly_completed]}")
        
        return newly_completed
    
    def get_meta_bonuses(self) -> Dict[str, float]:
        """Получение всех мета-бонусов"""
        bonuses = {}
        
        for upgrade in self.upgrades.values():
            for stat, bonus in upgrade.stat_bonuses.items():
                if stat not in bonuses:
                    bonuses[stat] = 0.0
                bonuses[stat] += upgrade.get_total_bonus(stat)
        
        return bonuses
    
    def get_inheritance_traits(self) -> List[Dict[str, Any]]:
        """Получение наследственных черт"""
        return self.inheritance_system.generate_inheritance_traits(
            self.lifetime_stats, self.currencies
        )
    
    def _init_meta_upgrades(self):
        """Инициализация мета-улучшений"""
        upgrades_data = [
            # Боевые улучшения
            {
                "id": "weapon_mastery",
                "name": "Мастерство оружия",
                "description": "Увеличивает урон от всех видов оружия",
                "type": MetaUpgradeType.WEAPON_MASTERY,
                "max_level": 20,
                "base_cost": 100,
                "cost_multiplier": 1.2,
                "currency": MetaCurrency.ESSENCE,
                "bonuses": {"weapon_damage": 0.05}
            },
            {
                "id": "combat_prowess",
                "name": "Боевое мастерство",
                "description": "Увеличивает общую эффективность в бою",
                "type": MetaUpgradeType.COMBAT_PROWESS,
                "max_level": 15,
                "base_cost": 150,
                "cost_multiplier": 1.25,
                "currency": MetaCurrency.ESSENCE,
                "bonuses": {"combat_effectiveness": 0.03, "critical_chance": 0.01}
            },
            # Эволюционные улучшения
            {
                "id": "evolution_speed",
                "name": "Скорость эволюции",
                "description": "Ускоряет процессы эволюции",
                "type": MetaUpgradeType.EVOLUTION_SPEED,
                "max_level": 10,
                "base_cost": 200,
                "cost_multiplier": 1.3,
                "currency": MetaCurrency.EVOLUTION_POINTS,
                "bonuses": {"evolution_rate": 0.1}
            },
            {
                "id": "genetic_stability",
                "name": "Генетическая стабильность",
                "description": "Снижает риск негативных мутаций",
                "type": MetaUpgradeType.GENETIC_STABILITY,
                "max_level": 8,
                "base_cost": 300,
                "cost_multiplier": 1.4,
                "currency": MetaCurrency.EVOLUTION_POINTS,
                "bonuses": {"mutation_stability": 0.05, "genetic_integrity": 0.03}
            },
            # Ментальные улучшения
            {
                "id": "memory_retention",
                "name": "Удержание памяти",
                "description": "Улучшает сохранение памяти между поколениями",
                "type": MetaUpgradeType.MEMORY_RETENTION,
                "max_level": 12,
                "base_cost": 100,
                "cost_multiplier": 1.15,
                "currency": MetaCurrency.MEMORY_FRAGMENTS,
                "bonuses": {"memory_retention": 0.08, "knowledge_transfer": 0.05}
            },
            {
                "id": "wisdom_accumulation",
                "name": "Накопление мудрости",
                "description": "Увеличивает получение мудрости от опыта",
                "type": MetaUpgradeType.WISDOM_ACCUMULATION,
                "max_level": 15,
                "base_cost": 50,
                "cost_multiplier": 1.2,
                "currency": MetaCurrency.WISDOM_CRYSTALS,
                "bonuses": {"wisdom_gain": 0.1, "experience_efficiency": 0.04}
            }
        ]
        
        for data in upgrades_data:
            upgrade = MetaUpgrade(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                upgrade_type=data["type"],
                current_level=0,
                max_level=data["max_level"],
                base_cost=data["base_cost"],
                cost_multiplier=data["cost_multiplier"],
                currency_type=data["currency"],
                stat_bonuses=data["bonuses"]
            )
            self.upgrades[upgrade.id] = upgrade
    
    def _init_meta_achievements(self):
        """Инициализация мета-достижений"""
        achievements_data = [
            {
                "id": "first_steps",
                "name": "Первые шаги",
                "description": "Завершить первый запуск",
                "requirements": {"runs_completed": 1},
                "rewards": {MetaCurrency.ESSENCE: 100, MetaCurrency.MEMORY_FRAGMENTS: 10},
                "unlocks": ["basic_upgrades"]
            },
            {
                "id": "survivor",
                "name": "Выживший",
                "description": "Выжить в 10 запусках",
                "requirements": {"runs_survived": 10},
                "rewards": {MetaCurrency.WISDOM_CRYSTALS: 25, MetaCurrency.ANCESTRAL_FAVOR: 15},
                "unlocks": ["survival_bonuses"]
            },
            {
                "id": "evolution_master",
                "name": "Мастер эволюции",
                "description": "Достичь 50 стадий эволюции",
                "requirements": {"total_evolution_stages": 50},
                "rewards": {MetaCurrency.EVOLUTION_POINTS: 500, MetaCurrency.DIMENSIONAL_SHARDS: 5},
                "unlocks": ["advanced_evolution"]
            },
            {
                "id": "memory_keeper",
                "name": "Хранитель памяти",
                "description": "Накопить 1000 воспоминаний",
                "requirements": {"total_memories": 1000},
                "rewards": {MetaCurrency.MEMORY_FRAGMENTS: 200, MetaCurrency.ANCESTRAL_FAVOR: 50},
                "unlocks": ["memory_mastery"]
            },
            {
                "id": "dimensional_traveler",
                "name": "Путешественник измерений",
                "description": "Испытать 5 измерительных событий",
                "requirements": {"dimensional_events": 5},
                "rewards": {MetaCurrency.DIMENSIONAL_SHARDS: 20, MetaCurrency.WISDOM_CRYSTALS: 30},
                "unlocks": ["dimensional_abilities"]
            }
        ]
        
        for data in achievements_data:
            achievement = MetaAchievement(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                requirements=data["requirements"],
                rewards=data["rewards"],
                special_unlocks=data["unlocks"]
            )
            self.achievements[achievement.id] = achievement
    
    def _apply_reward_multipliers(self, rewards: Dict[MetaCurrency, int]):
        """Применение множителей наград от улучшений"""
        # Проверяем улучшения, которые влияют на награды
        for upgrade in self.upgrades.values():
            if "reward_multiplier" in upgrade.stat_bonuses:
                multiplier = 1.0 + upgrade.get_total_bonus("reward_multiplier")
                for currency in rewards:
                    rewards[currency] = int(rewards[currency] * multiplier)
    
    def _update_lifetime_stats(self, run_stats: Dict[str, Any]):
        """Обновление общей статистики"""
        # Инициализация, если необходимо
        if not self.lifetime_stats:
            self.lifetime_stats = {
                "runs_completed": 0,
                "runs_survived": 0,
                "total_enemies_defeated": 0,
                "total_bosses_defeated": 0,
                "total_evolution_stages": 0,
                "total_memories": 0,
                "total_playtime": 0.0,
                "dimensional_events": 0,
                "perfect_runs": 0
            }
        
        # Обновление статистики
        self.lifetime_stats["runs_completed"] += 1
        if run_stats.get("survived", False):
            self.lifetime_stats["runs_survived"] += 1
        if run_stats.get("perfect_run", False):
            self.lifetime_stats["perfect_runs"] += 1
        
        self.lifetime_stats["total_enemies_defeated"] += run_stats.get("enemies_defeated", 0)
        self.lifetime_stats["total_bosses_defeated"] += run_stats.get("bosses_defeated", 0)
        self.lifetime_stats["total_evolution_stages"] += run_stats.get("evolution_stages", 0)
        self.lifetime_stats["total_playtime"] += run_stats.get("playtime", 0.0)
        self.lifetime_stats["dimensional_events"] += run_stats.get("dimensional_events", 0)
        
        # Обновляем статистику памяти из системы памяти поколений
        memory_stats = self.memory_system.get_memory_statistics()
        self.lifetime_stats["total_memories"] = memory_stats["total_memories"]
    
    def _record_currency_award(self, currency_type: MetaCurrency, amount: int, source: str):
        """Запись начисления валюты в память"""
        try:
            memory_content = {
                "currency_type": currency_type.value,
                "amount": amount,
                "source": source,
                "total_after": self.currencies[currency_type],
                "timestamp": time.time()
            }
            
            self.memory_system.add_memory(
                memory_type=MemoryType.ITEM_USAGE,  # Используем как ближайший тип
                content=memory_content,
                intensity=min(1.0, amount / 100.0),
                emotional_impact=0.2
            )
            
        except Exception as e:
            logger.error(f"Ошибка записи начисления валюты: {e}")
    
    def _record_upgrade_purchase(self, upgrade: MetaUpgrade):
        """Запись покупки улучшения в память"""
        try:
            memory_content = {
                "upgrade_id": upgrade.id,
                "upgrade_name": upgrade.name,
                "new_level": upgrade.current_level,
                "cost_paid": upgrade.get_current_cost(),
                "currency_used": upgrade.currency_type.value,
                "timestamp": time.time()
            }
            
            self.memory_system.add_memory(
                memory_type=MemoryType.EVOLUTIONARY_SUCCESS,
                content=memory_content,
                intensity=0.6,
                emotional_impact=0.3
            )
            
        except Exception as e:
            logger.error(f"Ошибка записи покупки улучшения: {e}")
    
    def _unlock_special_feature(self, feature: str):
        """Разблокировка специальной возможности"""
        logger.info(f"Разблокирована специальная возможность: {feature}")
        # Здесь можно добавить логику разблокировки различных возможностей
    
    def _load_meta_progress(self):
        """Загрузка мета-прогресса"""
        # Здесь должна быть логика загрузки из файла
        pass
    
    def _save_meta_progress(self):
        """Сохранение мета-прогресса"""
        # Здесь должна быть логика сохранения в файл
        pass
    
    def get_meta_statistics(self) -> Dict[str, Any]:
        """Получение статистики мета-прогрессии"""
        return {
            "currencies": {currency.value: amount for currency, amount in self.currencies.items()},
            "upgrades": {
                upgrade_id: {
                    "level": upgrade.current_level,
                    "max_level": upgrade.max_level,
                    "next_cost": upgrade.get_current_cost()
                }
                for upgrade_id, upgrade in self.upgrades.items()
            },
            "achievements": {
                achievement_id: {
                    "completed": achievement.completed,
                    "progress": achievement.progress
                }
                for achievement_id, achievement in self.achievements.items()
            },
            "lifetime_stats": self.lifetime_stats.copy(),
            "total_bonuses": self.get_meta_bonuses()
        }


class InheritanceSystem:
    """Система наследования (Rogue Legacy)"""
    
    def generate_inheritance_traits(self, lifetime_stats: Dict[str, Any],
                                   currencies: Dict[MetaCurrency, int]) -> List[Dict[str, Any]]:
        """Генерация наследственных черт"""
        traits = []
        
        # Черты на основе статистики
        if lifetime_stats.get("total_bosses_defeated", 0) > 10:
            traits.append({
                "name": "Убийца боссов",
                "description": "+20% урона боссам",
                "effect": {"boss_damage": 0.2}
            })
        
        if lifetime_stats.get("runs_survived", 0) > 5:
            traits.append({
                "name": "Выживший",
                "description": "+15% к максимальному здоровью",
                "effect": {"max_health": 0.15}
            })
        
        return traits


class DivineFavorSystem:
    """Система божественных благосклонностей (Hades)"""
    
    def __init__(self):
        self.favor_levels = {
            "combat_deity": 0,      # Божество войны
            "wisdom_deity": 0,      # Божество мудрости
            "evolution_deity": 0,   # Божество эволюции
            "memory_deity": 0       # Божество памяти
        }
    
    def increase_favor(self, deity: str, amount: int):
        """Увеличение благосклонности божества"""
        if deity in self.favor_levels:
            self.favor_levels[deity] += amount
            logger.info(f"Благосклонность {deity} увеличена на {amount}")
    
    def get_divine_bonuses(self) -> Dict[str, float]:
        """Получение божественных бонусов"""
        bonuses = {}
        
        # Бонусы от боевого божества
        combat_level = self.favor_levels["combat_deity"]
        if combat_level > 0:
            bonuses["divine_damage"] = combat_level * 0.02
        
        # Бонусы от божества мудрости
        wisdom_level = self.favor_levels["wisdom_deity"]
        if wisdom_level > 0:
            bonuses["experience_gain"] = wisdom_level * 0.03
        
        return bonuses
