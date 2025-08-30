#!/usr/bin/env python3
"""Система динамических квестов
Генерирует квесты на лету, адаптирует сложность и предоставляет множественные решения"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
import logging
import random
import time
import json
import math
from pathlib import Path

from src.core.architecture import BaseComponent, ComponentType, Priority

# = ТИПЫ КВЕСТОВ
class QuestType(Enum):
    """Типы квестов"""
    GATHERING = "gathering"           # Сбор предметов
    ELIMINATION = "elimination"       # Уничтожение врагов
    EXPLORATION = "exploration"       # Исследование
    ESCORT = "escort"                # Сопровождение
    DELIVERY = "delivery"            # Доставка
    INVESTIGATION = "investigation"  # Расследование
    CRAFTING = "crafting"            # Крафтинг
    SOCIAL = "social"                # Социальные взаимодействия
    SURVIVAL = "survival"            # Выживание
    STORY = "story"                  # Сюжетные квесты

class QuestDifficulty(Enum):
    """Сложность квестов"""
    TRIVIAL = "trivial"
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"
    MASTER = "master"
    LEGENDARY = "legendary"

class QuestStatus(Enum):
    """Статусы квестов"""
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class QuestRewardType(Enum):
    """Типы наград"""
    EXPERIENCE = "experience"
    GOLD = "gold"
    ITEMS = "items"
    REPUTATION = "reputation"
    SKILL_POINTS = "skill_points"
    UNIQUE_ABILITIES = "unique_abilities"
    RELATIONSHIP = "relationship"

# = СТРУКТУРЫ ДАННЫХ
@dataclass
class QuestObjective:
    """Цель квеста"""
    objective_id: str
    description: str
    target_type: str
    target_id: Optional[str] = None
    target_count: int = 1
    current_count: int = 0
    location: Optional[Tuple[float, float, float]] = None
    time_limit: Optional[float] = None
    is_optional: bool = False
    is_hidden: bool = False
    conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QuestReward:
    """Награда квеста"""
    reward_type: QuestRewardType
    amount: int
    item_id: Optional[str] = None
    skill_id: Optional[str] = None
    reputation_faction: Optional[str] = None
    relationship_target: Optional[str] = None
    conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QuestChoice:
    """Выбор в квесте"""
    choice_id: str
    description: str
    consequences: Dict[str, Any] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)
    morality_impact: float = 0.0
    reputation_impact: Dict[str, float] = field(default_factory=dict)
    relationship_impact: Dict[str, float] = field(default_factory=dict)

@dataclass
class QuestTemplate:
    """Шаблон квеста"""
    template_id: str
    quest_type: QuestType
    base_difficulty: QuestDifficulty
    title: str
    description: str
    objectives: List[QuestObjective] = field(default_factory=list)
    rewards: List[QuestReward] = field(default_factory=list)
    choices: List[QuestChoice] = field(default_factory=list)
    time_limit: Optional[float] = None
    level_requirement: int = 1
    skill_requirements: Dict[str, int] = field(default_factory=dict)
    faction_requirements: Dict[str, int] = field(default_factory=dict)
    prerequisites: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    generation_weights: Dict[str, float] = field(default_factory=dict)

@dataclass
class DynamicQuest:
    """Динамический квест"""
    quest_id: str
    template: QuestTemplate
    player_id: str
    quest_giver_id: str
    status: QuestStatus
    difficulty: QuestDifficulty
    objectives: List[QuestObjective] = field(default_factory=list)
    rewards: List[QuestReward] = field(default_factory=list)
    choices: List[QuestChoice] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    time_limit: Optional[float] = None
    player_choices: List[str] = field(default_factory=list)
    progress_data: Dict[str, Any] = field(default_factory=dict)
    adaptation_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QuestGenerationContext:
    """Контекст генерации квеста"""
    player_level: int
    player_skills: Dict[str, int]
    player_reputation: Dict[str, float]
    player_location: Tuple[float, float, float]
    available_npcs: List[str]
    available_locations: List[str]
    world_state: Dict[str, Any]
    player_preferences: Dict[str, Any]
    recent_quests: List[str] = field(default_factory=list)

# = НАСТРОЙКИ КВЕСТОВ
@dataclass
class QuestSettings:
    """Настройки системы квестов"""
    max_active_quests: int = 10
    max_quest_history: int = 100
    quest_expiration_time: float = 86400  # 24 часа
    difficulty_adaptation_rate: float = 0.1
    reward_scaling_factor: float = 1.0
    enable_dynamic_scaling: bool = True
    enable_choice_consequences: bool = True
    enable_reputation_impact: bool = True
    enable_relationship_evolution: bool = True
    generation_creativity: float = 0.7

# = СИСТЕМА ДИНАМИЧЕСКИХ КВЕСТОВ
class DynamicQuestSystem(BaseComponent):
    """Система динамических квестов"""
    
    def __init__(self):
        super().__init__(
            component_id="DynamicQuestSystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Настройки системы
        self.settings = QuestSettings()
        
        # Шаблоны квестов
        self.quest_templates: Dict[str, QuestTemplate] = {}
        
        # Активные квесты
        self.active_quests: Dict[str, DynamicQuest] = {}
        
        # История квестов
        self.quest_history: Dict[str, List[DynamicQuest]] = {}
        
        # Данные адаптации
        self.player_adaptation_data: Dict[str, Dict[str, Any]] = {}
        
        # Статистика
        self.stats = {
            "total_quests_generated": 0,
            "total_quests_completed": 0,
            "total_quests_failed": 0,
            "difficulty_adjustments": 0,
            "choice_consequences": 0,
            "reputation_changes": 0,
            "relationship_evolutions": 0
        }
        
        # Callbacks
        self.quest_callbacks: List[callable] = []
        self.choice_callbacks: List[callable] = []
        self.completion_callbacks: List[callable] = []
        
        self.logger = logging.getLogger(__name__)
    
    def _on_initialize(self) -> bool:
        """Инициализация системы квестов"""
        try:
            # Загрузка шаблонов квестов
            self._load_quest_templates()
            
            # Инициализация базовых шаблонов
            self._initialize_base_templates()
            
            self.logger.info("DynamicQuestSystem инициализирован")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации DynamicQuestSystem: {e}")
            return False
    
    def _load_quest_templates(self):
        """Загрузка шаблонов квестов"""
        try:
            # Базовые шаблоны для разных типов квестов
            self._create_gathering_templates()
            self._create_elimination_templates()
            self._create_exploration_templates()
            self._create_social_templates()
            
            self.logger.info("Шаблоны квестов загружены")
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки шаблонов квестов: {e}")
    
    def _create_gathering_templates(self):
        """Создание шаблонов квестов сбора"""
        # Сбор трав
        herb_gathering = QuestTemplate(
            template_id="herb_gathering",
            quest_type=QuestType.GATHERING,
            base_difficulty=QuestDifficulty.EASY,
            title="Сбор целебных трав",
            description="Соберите редкие травы для местного алхимика",
            objectives=[
                QuestObjective(
                    objective_id="collect_herbs",
                    description="Соберите {count} редких трав",
                    target_type="item",
                    target_id="rare_herb",
                    target_count=5
                )
            ],
            rewards=[
                QuestReward(reward_type=QuestRewardType.EXPERIENCE, amount=100),
                QuestReward(reward_type=QuestRewardType.GOLD, amount=50)
            ],
            tags=["gathering", "herbs", "alchemy"],
            generation_weights={"frequency": 0.8, "complexity": 0.3}
        )
        
        self.quest_templates["herb_gathering"] = herb_gathering
    
    def _create_elimination_templates(self):
        """Создание шаблонов квестов уничтожения"""
        # Охота на монстров
        monster_hunt = QuestTemplate(
            template_id="monster_hunt",
            quest_type=QuestType.ELIMINATION,
            base_difficulty=QuestDifficulty.NORMAL,
            title="Охота на монстров",
            description="Уничтожьте опасных монстров, угрожающих поселению",
            objectives=[
                QuestObjective(
                    objective_id="kill_monsters",
                    description="Уничтожьте {count} монстров",
                    target_type="enemy",
                    target_count=3
                )
            ],
            rewards=[
                QuestReward(reward_type=QuestRewardType.EXPERIENCE, amount=200),
                QuestReward(reward_type=QuestRewardType.GOLD, amount=100),
                QuestReward(reward_type=QuestRewardType.REPUTATION, amount=10)
            ],
            choices=[
                QuestChoice(
                    choice_id="spare_young",
                    description="Пощадить молодых монстров",
                    consequences={"reputation": 5, "experience": -50},
                    morality_impact=0.2
                ),
                QuestChoice(
                    choice_id="kill_all",
                    description="Уничтожить всех монстров",
                    consequences={"reputation": -5, "experience": 50},
                    morality_impact=-0.1
                )
            ],
            tags=["combat", "monsters", "hunting"],
            generation_weights={"frequency": 0.6, "complexity": 0.7}
        )
        
        self.quest_templates["monster_hunt"] = monster_hunt
    
    def _create_exploration_templates(self):
        """Создание шаблонов квестов исследования"""
        # Исследование руин
        ruins_exploration = QuestTemplate(
            template_id="ruins_exploration",
            quest_type=QuestType.EXPLORATION,
            base_difficulty=QuestDifficulty.HARD,
            title="Тайны древних руин",
            description="Исследуйте древние руины и найдите артефакты",
            objectives=[
                QuestObjective(
                    objective_id="explore_ruins",
                    description="Исследуйте руины",
                    target_type="location",
                    target_id="ancient_ruins"
                ),
                QuestObjective(
                    objective_id="find_artifact",
                    description="Найдите древний артефакт",
                    target_type="item",
                    target_id="ancient_artifact",
                    target_count=1
                )
            ],
            rewards=[
                QuestReward(reward_type=QuestRewardType.EXPERIENCE, amount=300),
                QuestReward(reward_type=QuestRewardType.ITEMS, amount=1, item_id="ancient_artifact"),
                QuestReward(reward_type=QuestRewardType.REPUTATION, amount=15)
            ],
            choices=[
                QuestChoice(
                    choice_id="preserve_ruins",
                    description="Сохранить руины нетронутыми",
                    consequences={"reputation": 10, "gold": -50},
                    morality_impact=0.3
                ),
                QuestChoice(
                    choice_id="loot_ruins",
                    description="Разграбить руины",
                    consequences={"reputation": -10, "gold": 100},
                    morality_impact=-0.2
                )
            ],
            tags=["exploration", "ruins", "artifacts"],
            generation_weights={"frequency": 0.4, "complexity": 0.8}
        )
        
        self.quest_templates["ruins_exploration"] = ruins_exploration
    
    def _create_social_templates(self):
        """Создание шаблонов социальных квестов"""
        # Посредничество
        mediation = QuestTemplate(
            template_id="mediation",
            quest_type=QuestType.SOCIAL,
            base_difficulty=QuestDifficulty.NORMAL,
            title="Посредник в споре",
            description="Помогите разрешить конфликт между двумя торговцами",
            objectives=[
                QuestObjective(
                    objective_id="talk_to_merchant1",
                    description="Поговорите с первым торговцем",
                    target_type="npc",
                    target_id="merchant_1"
                ),
                QuestObjective(
                    objective_id="talk_to_merchant2",
                    description="Поговорите со вторым торговцем",
                    target_type="npc",
                    target_id="merchant_2"
                ),
                QuestObjective(
                    objective_id="resolve_conflict",
                    description="Разрешите конфликт",
                    target_type="interaction",
                    target_id="conflict_resolution"
                )
            ],
            rewards=[
                QuestReward(reward_type=QuestRewardType.EXPERIENCE, amount=150),
                QuestReward(reward_type=QuestRewardType.REPUTATION, amount=20),
                QuestReward(reward_type=QuestRewardType.RELATIONSHIP, amount=1)
            ],
            choices=[
                QuestChoice(
                    choice_id="favor_merchant1",
                    description="Поддержать первого торговца",
                    consequences={"reputation_merchant1": 10, "reputation_merchant2": -5},
                    morality_impact=0.0
                ),
                QuestChoice(
                    choice_id="favor_merchant2",
                    description="Поддержать второго торговца",
                    consequences={"reputation_merchant1": -5, "reputation_merchant2": 10},
                    morality_impact=0.0
                ),
                QuestChoice(
                    choice_id="compromise",
                    description="Найти компромисс",
                    consequences={"reputation_merchant1": 5, "reputation_merchant2": 5},
                    morality_impact=0.1
                )
            ],
            tags=["social", "mediation", "conflict"],
            generation_weights={"frequency": 0.5, "complexity": 0.6}
        )
        
        self.quest_templates["mediation"] = mediation
    
    def _initialize_base_templates(self):
        """Инициализация базовых шаблонов"""
        # Здесь можно добавить дополнительные шаблоны
        pass
    
    def generate_dynamic_quest(self, player_id: str, quest_giver_id: str, 
                             context: QuestGenerationContext) -> Optional[DynamicQuest]:
        """Генерация динамического квеста"""
        try:
            # Выбор подходящего шаблона
            template = self._select_quest_template(context)
            if not template:
                return None
            
            # Адаптация сложности
            adapted_difficulty = self._adapt_quest_difficulty(template, context)
            
            # Создание квеста
            quest = DynamicQuest(
                quest_id=f"quest_{player_id}_{int(time.time())}",
                template=template,
                player_id=player_id,
                quest_giver_id=quest_giver_id,
                status=QuestStatus.AVAILABLE,
                difficulty=adapted_difficulty
            )
            
            # Адаптация целей
            quest.objectives = self._adapt_quest_objectives(template.objectives, context)
            
            # Адаптация наград
            quest.rewards = self._adapt_quest_rewards(template.rewards, context)
            
            # Адаптация выборов
            quest.choices = self._adapt_quest_choices(template.choices, context)
            
            # Установка временных ограничений
            if template.time_limit:
                quest.time_limit = template.time_limit * self._get_difficulty_multiplier(adapted_difficulty)
            
            # Сохранение данных адаптации
            quest.adaptation_data = {
                "player_level": context.player_level,
                "difficulty_adjustment": adapted_difficulty.value,
                "generation_context": context.__dict__
            }
            
            self.stats["total_quests_generated"] += 1
            
            self.logger.info(f"Сгенерирован квест {quest.quest_id} для игрока {player_id}")
            return quest
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации квеста: {e}")
            return None
    
    def _select_quest_template(self, context: QuestGenerationContext) -> Optional[QuestTemplate]:
        """Выбор подходящего шаблона квеста"""
        try:
            available_templates = []
            
            for template in self.quest_templates.values():
                # Проверка требований уровня
                if template.level_requirement > context.player_level:
                    continue
                
                # Проверка требований навыков
                if not self._check_skill_requirements(template, context.player_skills):
                    continue
                
                # Проверка требований фракций
                if not self._check_faction_requirements(template, context.player_reputation):
                    continue
                
                # Проверка предварительных условий
                if not self._check_prerequisites(template, context.recent_quests):
                    continue
                
                available_templates.append(template)
            
            if not available_templates:
                return None
            
            # Взвешенный выбор на основе весов генерации
            weights = [template.generation_weights.get("frequency", 0.5) for template in available_templates]
            total_weight = sum(weights)
            
            if total_weight == 0:
                return random.choice(available_templates)
            
            # Нормализация весов
            normalized_weights = [w / total_weight for w in weights]
            
            # Выбор шаблона
            selected_template = random.choices(available_templates, weights=normalized_weights)[0]
            
            return selected_template
            
        except Exception as e:
            self.logger.error(f"Ошибка выбора шаблона квеста: {e}")
            return None
    
    def _check_skill_requirements(self, template: QuestTemplate, player_skills: Dict[str, int]) -> bool:
        """Проверка требований навыков"""
        for skill_id, required_level in template.skill_requirements.items():
            if player_skills.get(skill_id, 0) < required_level:
                return False
        return True
    
    def _check_faction_requirements(self, template: QuestTemplate, player_reputation: Dict[str, float]) -> bool:
        """Проверка требований фракций"""
        for faction_id, required_reputation in template.faction_requirements.items():
            if player_reputation.get(faction_id, 0) < required_reputation:
                return False
        return True
    
    def _check_prerequisites(self, template: QuestTemplate, recent_quests: List[str]) -> bool:
        """Проверка предварительных условий"""
        for prerequisite in template.prerequisites:
            if prerequisite not in recent_quests:
                return False
        return True
    
    def _adapt_quest_difficulty(self, template: QuestTemplate, 
                               context: QuestGenerationContext) -> QuestDifficulty:
        """Адаптация сложности квеста"""
        try:
            base_difficulty = template.base_difficulty
            
            # Получение данных адаптации игрока
            player_data = self.player_adaptation_data.get(context.player_level, {})
            success_rate = player_data.get("success_rate", 0.5)
            
            # Корректировка сложности на основе успешности
            if success_rate > 0.8:
                # Игрок успешен - увеличиваем сложность
                difficulty_change = 1
            elif success_rate < 0.3:
                # Игрок неуспешен - уменьшаем сложность
                difficulty_change = -1
            else:
                difficulty_change = 0
            
            # Применение изменения сложности
            difficulties = list(QuestDifficulty)
            current_index = difficulties.index(base_difficulty)
            new_index = max(0, min(len(difficulties) - 1, current_index + difficulty_change))
            
            adapted_difficulty = difficulties[new_index]
            
            if adapted_difficulty != base_difficulty:
                self.stats["difficulty_adjustments"] += 1
            
            return adapted_difficulty
            
        except Exception as e:
            self.logger.error(f"Ошибка адаптации сложности: {e}")
            return template.base_difficulty
    
    def _get_difficulty_multiplier(self, difficulty: QuestDifficulty) -> float:
        """Получение множителя сложности"""
        multipliers = {
            QuestDifficulty.TRIVIAL: 0.5,
            QuestDifficulty.EASY: 0.8,
            QuestDifficulty.NORMAL: 1.0,
            QuestDifficulty.HARD: 1.3,
            QuestDifficulty.EXPERT: 1.7,
            QuestDifficulty.MASTER: 2.2,
            QuestDifficulty.LEGENDARY: 3.0
        }
        return multipliers.get(difficulty, 1.0)
    
    def _adapt_quest_objectives(self, base_objectives: List[QuestObjective], 
                               context: QuestGenerationContext) -> List[QuestObjective]:
        """Адаптация целей квеста"""
        adapted_objectives = []
        
        for objective in base_objectives:
            # Создание копии цели
            adapted_objective = QuestObjective(
                objective_id=objective.objective_id,
                description=objective.description,
                target_type=objective.target_type,
                target_id=objective.target_id,
                target_count=objective.target_count,
                current_count=objective.current_count,
                location=objective.location,
                time_limit=objective.time_limit,
                is_optional=objective.is_optional,
                is_hidden=objective.is_hidden,
                conditions=objective.conditions.copy()
            )
            
            # Адаптация количества на основе уровня игрока
            if objective.target_type in ["enemy", "item"]:
                level_multiplier = 1.0 + (context.player_level - 1) * 0.1
                adapted_objective.target_count = max(1, int(objective.target_count * level_multiplier))
                
                # Обновление описания
                adapted_objective.description = objective.description.replace(
                    "{count}", str(adapted_objective.target_count)
                )
            
            # Адаптация локации
            if objective.location is None and context.available_locations:
                adapted_objective.location = random.choice(context.available_locations)
            
            adapted_objectives.append(adapted_objective)
        
        return adapted_objectives
    
    def _adapt_quest_rewards(self, base_rewards: List[QuestReward], 
                           context: QuestGenerationContext) -> List[QuestReward]:
        """Адаптация наград квеста"""
        adapted_rewards = []
        
        for reward in base_rewards:
            # Создание копии награды
            adapted_reward = QuestReward(
                reward_type=reward.reward_type,
                amount=reward.amount,
                item_id=reward.item_id,
                skill_id=reward.skill_id,
                reputation_faction=reward.reputation_faction,
                relationship_target=reward.relationship_target,
                conditions=reward.conditions.copy()
            )
            
            # Масштабирование наград на основе уровня игрока
            level_multiplier = 1.0 + (context.player_level - 1) * 0.2
            adapted_reward.amount = int(adapted_reward.amount * level_multiplier * self.settings.reward_scaling_factor)
            
            adapted_rewards.append(adapted_reward)
        
        return adapted_rewards
    
    def _adapt_quest_choices(self, base_choices: List[QuestChoice], 
                           context: QuestGenerationContext) -> List[QuestChoice]:
        """Адаптация выборов в квесте"""
        adapted_choices = []
        
        for choice in base_choices:
            # Создание копии выбора
            adapted_choice = QuestChoice(
                choice_id=choice.choice_id,
                description=choice.description,
                consequences=choice.consequences.copy(),
                requirements=choice.requirements.copy(),
                morality_impact=choice.morality_impact,
                reputation_impact=choice.reputation_impact.copy(),
                relationship_impact=choice.relationship_impact.copy()
            )
            
            # Адаптация последствий на основе уровня игрока
            if "experience" in adapted_choice.consequences:
                level_multiplier = 1.0 + (context.player_level - 1) * 0.1
                adapted_choice.consequences["experience"] = int(
                    adapted_choice.consequences["experience"] * level_multiplier
                )
            
            adapted_choices.append(adapted_choice)
        
        return adapted_choices
    
    def accept_quest(self, quest_id: str, player_id: str) -> bool:
        """Принятие квеста"""
        try:
            if quest_id not in self.active_quests:
                return False
            
            quest = self.active_quests[quest_id]
            
            if quest.status != QuestStatus.AVAILABLE:
                return False
            
            if quest.player_id != player_id:
                return False
            
            # Проверка лимита активных квестов
            player_active_quests = [q for q in self.active_quests.values() 
                                  if q.player_id == player_id and q.status == QuestStatus.ACTIVE]
            
            if len(player_active_quests) >= self.settings.max_active_quests:
                return False
            
            # Активация квеста
            quest.status = QuestStatus.ACTIVE
            quest.started_at = time.time()
            
            # Инициализация истории квестов игрока
            if player_id not in self.quest_history:
                self.quest_history[player_id] = []
            
            self.logger.info(f"Квест {quest_id} принят игроком {player_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка принятия квеста: {e}")
            return False
    
    def update_quest_progress(self, quest_id: str, objective_id: str, 
                            progress: int = 1) -> bool:
        """Обновление прогресса квеста"""
        try:
            if quest_id not in self.active_quests:
                return False
            
            quest = self.active_quests[quest_id]
            
            if quest.status != QuestStatus.ACTIVE:
                return False
            
            # Поиск цели
            for objective in quest.objectives:
                if objective.objective_id == objective_id:
                    objective.current_count = min(objective.current_count + progress, objective.target_count)
                    
                    # Проверка завершения цели
                    if objective.current_count >= objective.target_count:
                        self._check_quest_completion(quest)
                    
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления прогресса квеста: {e}")
            return False
    
    def _check_quest_completion(self, quest: DynamicQuest):
        """Проверка завершения квеста"""
        try:
            # Проверка всех обязательных целей
            for objective in quest.objectives:
                if not objective.is_optional and objective.current_count < objective.target_count:
                    return
            
            # Квест завершен
            quest.status = QuestStatus.COMPLETED
            quest.completed_at = time.time()
            
            # Выдача наград
            self._grant_quest_rewards(quest)
            
            # Обновление статистики
            self.stats["total_quests_completed"] += 1
            
            # Обновление данных адаптации
            self._update_player_adaptation_data(quest)
            
            # Уведомление о завершении
            self._notify_quest_completion(quest)
            
            self.logger.info(f"Квест {quest.quest_id} завершен")
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки завершения квеста: {e}")
    
    def _grant_quest_rewards(self, quest: DynamicQuest):
        """Выдача наград квеста"""
        try:
            for reward in quest.rewards:
                # Здесь должна быть логика выдачи наград
                # Интеграция с другими системами (опыт, золото, предметы и т.д.)
                pass
            
        except Exception as e:
            self.logger.error(f"Ошибка выдачи наград: {e}")
    
    def _update_player_adaptation_data(self, quest: DynamicQuest):
        """Обновление данных адаптации игрока"""
        try:
            player_id = quest.player_id
            player_level = quest.adaptation_data.get("player_level", 1)
            
            if player_level not in self.player_adaptation_data:
                self.player_adaptation_data[player_level] = {
                    "total_quests": 0,
                    "completed_quests": 0,
                    "failed_quests": 0,
                    "success_rate": 0.5,
                    "average_completion_time": 0.0
                }
            
            data = self.player_adaptation_data[player_level]
            data["total_quests"] += 1
            
            if quest.status == QuestStatus.COMPLETED:
                data["completed_quests"] += 1
            
            # Обновление успешности
            data["success_rate"] = data["completed_quests"] / data["total_quests"]
            
            # Обновление среднего времени завершения
            if quest.completed_at and quest.started_at:
                completion_time = quest.completed_at - quest.started_at
                if data["average_completion_time"] == 0:
                    data["average_completion_time"] = completion_time
                else:
                    data["average_completion_time"] = (data["average_completion_time"] + completion_time) / 2
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления данных адаптации: {e}")
    
    def make_quest_choice(self, quest_id: str, choice_id: str) -> Dict[str, Any]:
        """Совершение выбора в квесте"""
        try:
            if quest_id not in self.active_quests:
                return {"success": False, "error": "Квест не найден"}
            
            quest = self.active_quests[quest_id]
            
            if quest.status != QuestStatus.ACTIVE:
                return {"success": False, "error": "Квест не активен"}
            
            # Поиск выбора
            selected_choice = None
            for choice in quest.choices:
                if choice.choice_id == choice_id:
                    selected_choice = choice
                    break
            
            if not selected_choice:
                return {"success": False, "error": "Выбор не найден"}
            
            # Применение последствий
            consequences = self._apply_choice_consequences(selected_choice, quest)
            
            # Сохранение выбора
            quest.player_choices.append(choice_id)
            
            # Обновление статистики
            self.stats["choice_consequences"] += 1
            
            # Уведомление о выборе
            self._notify_quest_choice(quest, selected_choice, consequences)
            
            return {
                "success": True,
                "choice": selected_choice,
                "consequences": consequences
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка совершения выбора: {e}")
            return {"success": False, "error": str(e)}
    
    def _apply_choice_consequences(self, choice: QuestChoice, quest: DynamicQuest) -> Dict[str, Any]:
        """Применение последствий выбора"""
        consequences = {}
        
        try:
            # Применение базовых последствий
            for key, value in choice.consequences.items():
                consequences[key] = value
            
            # Применение влияния на репутацию
            for faction, change in choice.reputation_impact.items():
                consequences[f"reputation_{faction}"] = change
                self.stats["reputation_changes"] += 1
            
            # Применение влияния на отношения
            for target, change in choice.relationship_impact.items():
                consequences[f"relationship_{target}"] = change
                self.stats["relationship_evolutions"] += 1
            
            return consequences
            
        except Exception as e:
            self.logger.error(f"Ошибка применения последствий выбора: {e}")
            return consequences
    
    def get_player_quests(self, player_id: str) -> List[DynamicQuest]:
        """Получение квестов игрока"""
        return [quest for quest in self.active_quests.values() if quest.player_id == player_id]
    
    def get_quest_statistics(self) -> Dict[str, Any]:
        """Получение статистики квестов"""
        return {
            "total_quests_generated": self.stats["total_quests_generated"],
            "total_quests_completed": self.stats["total_quests_completed"],
            "total_quests_failed": self.stats["total_quests_failed"],
            "difficulty_adjustments": self.stats["difficulty_adjustments"],
            "choice_consequences": self.stats["choice_consequences"],
            "reputation_changes": self.stats["reputation_changes"],
            "relationship_evolutions": self.stats["relationship_evolutions"],
            "active_quests": len(self.active_quests),
            "quest_templates": len(self.quest_templates),
            "player_adaptation_data": len(self.player_adaptation_data)
        }
    
    def add_quest_callback(self, callback: callable):
        """Добавление callback для квестов"""
        self.quest_callbacks.append(callback)
    
    def add_choice_callback(self, callback: callable):
        """Добавление callback для выборов"""
        self.choice_callbacks.append(callback)
    
    def add_completion_callback(self, callback: callable):
        """Добавление callback для завершения"""
        self.completion_callbacks.append(callback)
    
    def _notify_quest_completion(self, quest: DynamicQuest):
        """Уведомление о завершении квеста"""
        for callback in self.completion_callbacks:
            try:
                callback(quest)
            except Exception as e:
                self.logger.error(f"Ошибка в callback завершения квеста: {e}")
    
    def _notify_quest_choice(self, quest: DynamicQuest, choice: QuestChoice, 
                           consequences: Dict[str, Any]):
        """Уведомление о выборе в квесте"""
        for callback in self.choice_callbacks:
            try:
                callback(quest, choice, consequences)
            except Exception as e:
                self.logger.error(f"Ошибка в callback выбора квеста: {e}")
    
    def _on_destroy(self):
        """Уничтожение системы квестов"""
        self.quest_templates.clear()
        self.active_quests.clear()
        self.quest_history.clear()
        self.player_adaptation_data.clear()
        self.quest_callbacks.clear()
        self.choice_callbacks.clear()
        self.completion_callbacks.clear()
        
        self.logger.info("DynamicQuestSystem уничтожен")
