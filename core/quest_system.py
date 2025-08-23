#!/usr/bin/env python3
"""
Система квестов и достижений для эволюционной адаптации.
Управляет заданиями, наградами и прогрессом игрока.
"""

import random
import json
import time
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class QuestType(Enum):
    """Типы квестов"""
    KILL_ENEMIES = "kill_enemies"
    COLLECT_ITEMS = "collect_items"
    EXPLORE_AREA = "explore_area"
    EVOLVE_CYCLES = "evolve_cycles"
    LEARN_SKILLS = "learn_skills"
    DISCOVER_SECRETS = "discover_secrets"
    COMPLETE_CHALLENGES = "complete_challenges"
    SOCIAL_INTERACTIONS = "social_interactions"
    GENETIC_EXPERIMENTS = "genetic_experiments"
    AI_TRAINING = "ai_training"


class QuestRarity(Enum):
    """Редкость квестов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class QuestStatus(Enum):
    """Статус квеста"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class QuestObjective:
    """Цель квеста"""
    objective_type: str
    target: str
    required_amount: int
    current_amount: int = 0
    description: str = ""
    
    def update_progress(self, amount: int = 1) -> bool:
        """Обновление прогресса цели"""
        self.current_amount = min(self.current_amount + amount, self.required_amount)
        return self.is_completed()
    
    def is_completed(self) -> bool:
        """Проверка завершения цели"""
        return self.current_amount >= self.required_amount


@dataclass
class QuestReward:
    """Награда квеста"""
    reward_type: str
    amount: int
    item_id: Optional[str] = None
    effect_id: Optional[str] = None
    experience: int = 0
    gold: int = 0
    genetic_points: int = 0
    evolution_bonus: Optional[str] = None


@dataclass
class Quest:
    """Квест"""
    quest_id: str
    title: str
    description: str
    quest_type: QuestType
    rarity: QuestRarity
    objectives: List[QuestObjective]
    rewards: List[QuestReward]
    requirements: Dict[str, Any]
    time_limit: Optional[float] = None
    start_time: Optional[float] = None
    status: QuestStatus = QuestStatus.NOT_STARTED
    is_repeatable: bool = False
    repeat_cooldown: float = 0.0
    last_completed: Optional[float] = None
    
    def start_quest(self) -> bool:
        """Начало квеста"""
        if self.status == QuestStatus.NOT_STARTED:
            self.status = QuestStatus.IN_PROGRESS
            self.start_time = time.time()
            return True
        return False
    
    def update_objective(self, objective_type: str, target: str, amount: int = 1) -> bool:
        """Обновление цели квеста"""
        if self.status != QuestStatus.IN_PROGRESS:
            return False
        
        for objective in self.objectives:
            if (objective.objective_type == objective_type and 
                objective.target == target):
                if objective.update_progress(amount):
                    return self.check_completion()
        return False
    
    def check_completion(self) -> bool:
        """Проверка завершения квеста"""
        if all(obj.is_completed() for obj in self.objectives):
            self.status = QuestStatus.COMPLETED
            return True
        return False
    
    def is_expired(self) -> bool:
        """Проверка истечения времени квеста"""
        if self.time_limit and self.start_time:
            return time.time() - self.start_time > self.time_limit
        return False


@dataclass
class Achievement:
    """Достижение"""
    achievement_id: str
    title: str
    description: str
    category: str
    requirements: Dict[str, Any]
    rewards: List[QuestReward]
    is_hidden: bool = False
    is_completed: bool = False
    completion_date: Optional[float] = None
    progress: Dict[str, int] = field(default_factory=dict)


class QuestGenerator:
    """Генератор квестов"""
    
    def __init__(self):
        self.quest_templates = self._load_quest_templates()
        self.achievement_templates = self._load_achievement_templates()
    
    def _load_quest_templates(self) -> Dict[str, Dict]:
        """Загрузка шаблонов квестов"""
        return {
            "evolution_master": {
                "title": "Мастер эволюции",
                "description": "Завершите {cycles} эволюционных циклов",
                "type": QuestType.EVOLVE_CYCLES,
                "rarity": QuestRarity.RARE,
                "objectives": [{"type": "evolve_cycles", "target": "any", "amount": 5}],
                "rewards": [{"type": "evolution_bonus", "bonus": "extra_gene_slots"}]
            },
            "genetic_explorer": {
                "title": "Генетический исследователь",
                "description": "Откройте {genes} новых генов",
                "type": QuestType.GENETIC_EXPERIMENTS,
                "rarity": QuestRarity.UNCOMMON,
                "objectives": [{"type": "discover_genes", "target": "any", "amount": 10}],
                "rewards": [{"type": "genetic_points", "amount": 50}]
            },
            "ai_trainer": {
                "title": "Тренер ИИ",
                "description": "Обучите ИИ до уровня {level}",
                "type": QuestType.AI_TRAINING,
                "rarity": QuestRarity.EPIC,
                "objectives": [{"type": "ai_level", "target": "any", "amount": 10}],
                "rewards": [{"type": "ai_bonus", "bonus": "faster_learning"}]
            },
            "combat_expert": {
                "title": "Эксперт боя",
                "description": "Победите {enemies} врагов",
                "type": QuestType.KILL_ENEMIES,
                "rarity": QuestRarity.COMMON,
                "objectives": [{"type": "kill_enemies", "target": "any", "amount": 100}],
                "rewards": [{"type": "experience", "amount": 1000}]
            }
        }
    
    def _load_achievement_templates(self) -> Dict[str, Dict]:
        """Загрузка шаблонов достижений"""
        return {
            "first_evolution": {
                "title": "Первая эволюция",
                "description": "Завершите первый эволюционный цикл",
                "category": "evolution",
                "requirements": {"evolve_cycles": 1}
            },
            "genetic_pioneer": {
                "title": "Генетический пионер",
                "description": "Откройте 50 различных генов",
                "category": "genetics",
                "requirements": {"discovered_genes": 50}
            },
            "ai_master": {
                "title": "Мастер ИИ",
                "description": "Достигните максимального уровня ИИ",
                "category": "ai",
                "requirements": {"ai_level": 100}
            }
        }
    
    def generate_quest(self, quest_type: str, difficulty: float = 1.0) -> Quest:
        """Генерация квеста"""
        if quest_type not in self.quest_templates:
            raise ValueError(f"Неизвестный тип квеста: {quest_type}")
        
        template = self.quest_templates[quest_type]
        
        # Масштабирование сложности
        scaled_amount = int(template["objectives"][0]["amount"] * difficulty)
        
        objectives = [
            QuestObjective(
                objective_type=obj["type"],
                target=obj["target"],
                required_amount=scaled_amount,
                description=obj.get("description", "")
            )
            for obj in template["objectives"]
        ]
        
        rewards = [
            QuestReward(
                reward_type=reward["type"],
                amount=reward.get("amount", 0),
                item_id=reward.get("item_id"),
                effect_id=reward.get("effect_id")
            )
            for reward in template["rewards"]
        ]
        
        return Quest(
            quest_id=f"{quest_type}_{int(time.time())}",
            title=template["title"],
            description=template["description"].format(cycles=scaled_amount),
            quest_type=QuestType(template["type"]),
            rarity=QuestRarity(template["rarity"]),
            objectives=objectives,
            rewards=rewards,
            requirements={}
        )


class QuestManager:
    """Менеджер квестов"""
    
    def __init__(self):
        self.active_quests: Dict[str, Quest] = {}
        self.completed_quests: Dict[str, Quest] = {}
        self.achievements: Dict[str, Achievement] = {}
        self.quest_generator = QuestGenerator()
        
        # Статистика
        self.total_quests_completed = 0
        self.total_achievements_unlocked = 0
        
        # Инициализация достижений
        self._init_achievements()
        
        logger.info("Система квестов инициализирована")
    
    def _init_achievements(self):
        """Инициализация достижений"""
        for achievement_id, template in self.quest_generator.achievement_templates.items():
            achievement = Achievement(
                achievement_id=achievement_id,
                title=template["title"],
                description=template["description"],
                category=template["category"],
                requirements=template["requirements"],
                rewards=[]
            )
            self.achievements[achievement_id] = achievement
    
    def start_quest(self, quest_type: str, difficulty: float = 1.0) -> Optional[Quest]:
        """Начало квеста"""
        try:
            quest = self.quest_generator.generate_quest(quest_type, difficulty)
            if quest.start_quest():
                self.active_quests[quest.quest_id] = quest
                logger.info(f"Начат квест: {quest.title}")
                return quest
        except Exception as e:
            logger.error(f"Ошибка начала квеста: {e}")
        return None
    
    def update_quest_progress(self, objective_type: str, target: str, amount: int = 1):
        """Обновление прогресса квестов"""
        completed_quests = []
        
        for quest in self.active_quests.values():
            if quest.update_objective(objective_type, target, amount):
                completed_quests.append(quest)
        
        # Обработка завершённых квестов
        for quest in completed_quests:
            self.complete_quest(quest)
    
    def complete_quest(self, quest: Quest):
        """Завершение квеста"""
        quest.status = QuestStatus.COMPLETED
        self.completed_quests[quest.quest_id] = quest
        del self.active_quests[quest.quest_id]
        
        self.total_quests_completed += 1
        
        # Выдача наград
        self._give_quest_rewards(quest)
        
        logger.info(f"Квест завершён: {quest.title}")
    
    def _give_quest_rewards(self, quest: Quest):
        """Выдача наград за квест"""
        for reward in quest.rewards:
            logger.info(f"Награда за квест {quest.title}: {reward.reward_type} x{reward.amount}")
    
    def check_achievements(self, player_stats: Dict[str, Any]):
        """Проверка достижений"""
        unlocked_achievements = []
        
        for achievement in self.achievements.values():
            if not achievement.is_completed():
                if self._check_achievement_requirements(achievement, player_stats):
                    achievement.is_completed = True
                    achievement.completion_date = time.time()
                    unlocked_achievements.append(achievement)
                    self.total_achievements_unlocked += 1
        
        for achievement in unlocked_achievements:
            logger.info(f"Достижение разблокировано: {achievement.title}")
    
    def _check_achievement_requirements(self, achievement: Achievement, 
                                      player_stats: Dict[str, Any]) -> bool:
        """Проверка требований достижения"""
        for requirement, required_value in achievement.requirements.items():
            if requirement not in player_stats:
                return False
            if player_stats[requirement] < required_value:
                return False
        return True
    
    def get_available_quests(self) -> List[Quest]:
        """Получение доступных квестов"""
        return list(self.active_quests.values())
    
    def get_completed_quests(self) -> List[Quest]:
        """Получение завершённых квестов"""
        return list(self.completed_quests.values())
    
    def get_achievements(self) -> List[Achievement]:
        """Получение достижений"""
        return list(self.achievements.values())
    
    def get_quest_statistics(self) -> Dict[str, Any]:
        """Получение статистики квестов"""
        return {
            "active_quests": len(self.active_quests),
            "completed_quests": self.total_quests_completed,
            "unlocked_achievements": self.total_achievements_unlocked,
            "total_achievements": len(self.achievements)
        }
