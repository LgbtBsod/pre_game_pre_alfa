#!/usr/bin/env python3
"""
Система квестов - управление заданиями и миссиями
Интегрирована с новой модульной архитектурой
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.system_interfaces import BaseGameSystem
from ...core.architecture import Priority, LifecycleState
from ...core.state_manager import StateManager, StateType, StateScope
from ...core.repository import RepositoryManager, DataType, StorageType
from ...core.constants import constants_manager, QuestType, QuestStatus, QuestRewardType, QuestDifficulty, QuestCategory, PROBABILITY_CONSTANTS, SYSTEM_LIMITS, TIME_CONSTANTS_RO, get_float

from .quest_data import Quest, QuestObjective, QuestReward, QuestPrerequisite

logger = logging.getLogger(__name__)

@dataclass
class QuestProgress:
    """Прогресс квеста для сущности"""
    entity_id: str
    quest_id: str
    objectives_progress: Dict[str, int] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
    completed_objectives: List[str] = field(default_factory=list)

@dataclass
class QuestChain:
    """Цепочка квестов"""
    chain_id: str
    name: str
    description: str
    quests: List[str] = field(default_factory=list)  # quest_ids
    current_quest_index: int = 0
    completed: bool = False
    rewards_multiplier: float = 1.0

class QuestSystem(BaseGameSystem):
    """Система управления квестами - интегрирована с новой архитектурой"""
    
    def __init__(self, state_manager: Optional[StateManager] = None, repository_manager: Optional[RepositoryManager] = None, event_bus=None):
        super().__init__("quest", Priority.NORMAL)
        
        # Интеграция с новой архитектурой
        self.state_manager: Optional[StateManager] = state_manager
        self.repository_manager: Optional[RepositoryManager] = repository_manager
        self.event_bus = event_bus
        
        # Квесты (теперь управляются через RepositoryManager)
        self.available_quests: Dict[str, Quest] = {}
        self.active_quests: Dict[str, Dict[str, QuestProgress]] = {}  # entity_id -> quest_id -> progress
        self.completed_quests: Dict[str, List[str]] = {}  # entity_id -> list of completed quest_ids
        
        # Цепочки квестов (теперь управляются через RepositoryManager)
        self.quest_chains: Dict[str, QuestChain] = {}
        self.entity_quest_chains: Dict[str, Dict[str, QuestChain]] = {}  # entity_id -> chain_id -> chain
        
        # Шаблоны квестов (теперь управляются через RepositoryManager)
        self.quest_templates: Dict[str, Dict[str, Any]] = {}
        
        # История квестов (теперь управляется через RepositoryManager)
        self.quest_history: List[Dict[str, Any]] = []
        
        # Настройки системы (теперь управляются через StateManager)
        self.system_settings = {
            'max_active_quests': SYSTEM_LIMITS["max_active_quests"],
            'max_daily_quests': SYSTEM_LIMITS["max_daily_quests"],
            'quest_expiration_time': get_float(TIME_CONSTANTS_RO, "quest_expiration_time", 86400.0),
            'quest_chain_bonus': 1.5,
            'hidden_quest_chance': PROBABILITY_CONSTANTS["hidden_quest_chance"],
            'epic_quest_chance': PROBABILITY_CONSTANTS["epic_quest_chance"]
        }
        
        # Статистика системы (теперь управляется через StateManager)
        self.system_stats = {
            'total_quests_created': 0,
            'total_quests_completed': 0,
            'total_quests_failed': 0,
            'active_quests_count': 0,
            'quest_chains_completed': 0,
            'average_completion_time': 0.0,
            'update_time': 0.0
        }
        
        logger.info("Система квестов инициализирована с новой архитектурой")
    
    def initialize(self, state_manager: StateManager = None, repository_manager: RepositoryManager = None, event_bus=None) -> bool:
        """Инициализация системы"""
        try:
            if state_manager is not None:
                self.state_manager = state_manager
            if repository_manager is not None:
                self.repository_manager = repository_manager
            if event_bus is not None:
                self.event_bus = event_bus
            
            if not self.state_manager or not self.repository_manager:
                logger.warning("QuestSystem: отсутствуют state_manager или repository_manager — работаем в локальном режиме")
            
            # Регистрация состояний системы
            self._register_system_states()
            
            # Регистрация репозиториев
            self._register_system_repositories()
            
            # Загрузка шаблонов квестов
            self._load_quest_templates()
            
            # Создание базовых квестов
            self._create_basic_quests()
            
            self.state = LifecycleState.INITIALIZED
            logger.info("Система квестов успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы квестов: {e}")
            return False
    
    def _register_system_states(self):
        """Регистрация состояний системы"""
        if self.state_manager:
            self.state_manager.register_state(
                "quest_system_settings",
                self.system_settings,
                StateType.CONFIGURATION,
                StateScope.SYSTEM
            )
            self.state_manager.register_state(
                "quest_system_stats",
                self.system_stats,
                StateType.DYNAMIC_DATA,
                StateScope.SYSTEM
            )
    
    def _register_system_repositories(self):
        """Регистрация репозиториев системы"""
        if self.repository_manager:
            self.repository_manager.create_repository(
                "quests",
                DataType.ENTITY_DATA,
                StorageType.MEMORY
            )
            self.repository_manager.create_repository(
                "quest_progress",
                DataType.ENTITY_DATA,
                StorageType.MEMORY
            )
            self.repository_manager.create_repository(
                "quest_chains",
                DataType.SYSTEM_DATA,
                StorageType.MEMORY
            )
            self.repository_manager.create_repository(
                "quest_templates",
                DataType.CONFIGURATION,
                StorageType.MEMORY
            )
            self.repository_manager.create_repository(
                "quest_history",
                DataType.HISTORY,
                StorageType.MEMORY
            )
    
    def _load_quest_templates(self):
        """Загрузка шаблонов квестов"""
        # Базовые шаблоны квестов
        self.quest_templates = {
            "exploration_basic": {
                "title": "Исследование территории",
                "description": "Исследуйте указанную территорию",
                "quest_type": QuestType.EXPLORATION_QUEST,
                "category": QuestCategory.EXPLORATION,
                "difficulty": QuestDifficulty.EASY,
                "objectives": [
                    {"type": "explore", "target": "area", "amount": 1}
                ],
                "rewards": [
                    {"type": QuestRewardType.EXPERIENCE, "amount": 100},
                    {"type": QuestRewardType.GOLD, "amount": 50}
                ]
            },
            "combat_basic": {
                "title": "Устранение угрозы",
                "description": "Победите указанных врагов",
                "quest_type": QuestType.COMBAT_QUEST,
                "category": QuestCategory.COMBAT,
                "difficulty": QuestDifficulty.NORMAL,
                "objectives": [
                    {"type": "kill", "target": "enemy", "amount": 5}
                ],
                "rewards": [
                    {"type": QuestRewardType.EXPERIENCE, "amount": 200},
                    {"type": QuestRewardType.EVOLUTION_POINTS, "amount": 10}
                ]
            },
            "evolution_basic": {
                "title": "Эволюционный скачок",
                "description": "Достигните новой стадии эволюции",
                "quest_type": QuestType.EVOLUTION_QUEST,
                "category": QuestCategory.EVOLUTION,
                "difficulty": QuestDifficulty.HARD,
                "objectives": [
                    {"type": "evolve", "target": "stage", "amount": 1}
                ],
                "rewards": [
                    {"type": QuestRewardType.EVOLUTION_POINTS, "amount": 50},
                    {"type": QuestRewardType.GENE_FRAGMENTS, "amount": 25}
                ]
            }
        }
    
    def _create_basic_quests(self):
        """Создание базовых квестов"""
        for template_id, template in self.quest_templates.items():
            quest = self._create_quest_from_template(template_id, template)
            if quest:
                self.available_quests[quest.quest_id] = quest
                self.system_stats['total_quests_created'] += 1
    
    def _create_quest_from_template(self, template_id: str, template: Dict[str, Any]) -> Optional[Quest]:
        """Создание квеста из шаблона"""
        try:
            quest_id = f"{template_id}_{int(time.time())}"
            
            # Создание целей
            objectives = []
            for obj_data in template.get("objectives", []):
                objective = QuestObjective(
                    objective_id=f"{quest_id}_obj_{len(objectives)}",
                    description=obj_data.get("description", ""),
                    objective_type=obj_data["type"],
                    target=obj_data["target"],
                    required_amount=obj_data.get("amount", 1)
                )
                objectives.append(objective)
            
            # Создание наград
            rewards = []
            for reward_data in template.get("rewards", []):
                reward = QuestReward(
                    reward_type=reward_data["type"],
                    reward_id=f"{quest_id}_reward_{len(rewards)}",
                    amount=reward_data.get("amount", 1)
                )
                rewards.append(reward)
            
            quest = Quest(
                quest_id=quest_id,
                title=template["title"],
                description=template["description"],
                quest_type=template["quest_type"],
                category=template["category"],
                difficulty=template["difficulty"],
                objectives=objectives,
                rewards=rewards
            )
            
            return quest
            
        except Exception as e:
            logger.error(f"Ошибка создания квеста из шаблона {template_id}: {e}")
            return None
    
    def start_quest(self, entity_id: str, quest_id: str) -> bool:
        """Начать квест для сущности"""
        try:
            if quest_id not in self.available_quests:
                logger.warning(f"Квест {quest_id} не найден")
                return False
            
            quest = self.available_quests[quest_id]
            
            # Проверка ограничений
            if not self._can_start_quest(entity_id, quest):
                return False
            
            # Создание прогресса квеста
            progress = QuestProgress(
                entity_id=entity_id,
                quest_id=quest_id
            )
            
            # Инициализация прогресса целей
            for objective in quest.objectives:
                progress.objectives_progress[objective.objective_id] = 0
            
            # Добавление в активные квесты
            if entity_id not in self.active_quests:
                self.active_quests[entity_id] = {}
            self.active_quests[entity_id][quest_id] = progress
            
            # Обновление статистики
            self.system_stats['active_quests_count'] += 1
            
            logger.info(f"Квест {quest_id} начат для сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка начала квеста {quest_id} для {entity_id}: {e}")
            return False
    
    def _can_start_quest(self, entity_id: str, quest: Quest) -> bool:
        """Проверка возможности начала квеста"""
        # Проверка уровня
        # TODO: Получить уровень сущности из системы сущностей
        entity_level = 1  # Временное значение
        
        if entity_level < quest.level_requirement:
            logger.warning(f"Недостаточный уровень для квеста {quest.quest_id}")
            return False
        
        # Проверка количества активных квестов
        active_count = len(self.active_quests.get(entity_id, {}))
        if active_count >= self.system_settings['max_active_quests']:
            logger.warning(f"Достигнут лимит активных квестов для {entity_id}")
            return False
        
        # Проверка предварительных требований
        for prerequisite in quest.prerequisites:
            if not prerequisite.met:
                logger.warning(f"Не выполнено предварительное требование для квеста {quest.quest_id}")
                return False
        
        return True
    
    def update_quest_progress(self, entity_id: str, quest_id: str, objective_id: str, amount: int = 1) -> bool:
        """Обновить прогресс квеста"""
        try:
            if entity_id not in self.active_quests or quest_id not in self.active_quests[entity_id]:
                return False
            
            progress = self.active_quests[entity_id][quest_id]
            quest = self.available_quests[quest_id]
            
            # Поиск цели
            objective = None
            for obj in quest.objectives:
                if obj.objective_id == objective_id:
                    objective = obj
                    break
            
            if not objective:
                return False
            
            # Обновление прогресса
            if objective_id not in progress.objectives_progress:
                progress.objectives_progress[objective_id] = 0
            
            progress.objectives_progress[objective_id] += amount
            
            # Проверка завершения цели
            if progress.objectives_progress[objective_id] >= objective.required_amount:
                objective.completed = True
                if objective_id not in progress.completed_objectives:
                    progress.completed_objectives.append(objective_id)
            
            progress.last_update = time.time()
            
            # Проверка завершения квеста
            if self._check_quest_completion(entity_id, quest_id):
                self.complete_quest(entity_id, quest_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления прогресса квеста: {e}")
            return False
    
    def _check_quest_completion(self, entity_id: str, quest_id: str) -> bool:
        """Проверка завершения квеста"""
        if entity_id not in self.active_quests or quest_id not in self.active_quests[entity_id]:
            return False
        
        quest = self.available_quests[quest_id]
        required_objectives = [obj for obj in quest.objectives if not obj.optional]
        
        return all(obj.completed for obj in required_objectives)
    
    def complete_quest(self, entity_id: str, quest_id: str) -> bool:
        """Завершить квест"""
        try:
            if entity_id not in self.active_quests or quest_id not in self.active_quests[entity_id]:
                return False
            
            quest = self.available_quests[quest_id]
            progress = self.active_quests[entity_id][quest_id]
            
            # Выдача наград
            self._give_quest_rewards(entity_id, quest)
            
            # Обновление статистики
            self.system_stats['total_quests_completed'] += 1
            self.system_stats['active_quests_count'] -= 1
            
            # Перемещение в завершенные квесты
            if entity_id not in self.completed_quests:
                self.completed_quests[entity_id] = []
            self.completed_quests[entity_id].append(quest_id)
            
            # Удаление из активных квестов
            del self.active_quests[entity_id][quest_id]
            
            # Обновление времени завершения
            completion_time = time.time() - progress.start_time
            self.system_stats['average_completion_time'] = (
                (self.system_stats['average_completion_time'] * (self.system_stats['total_quests_completed'] - 1) + completion_time)
                / self.system_stats['total_quests_completed']
            )
            
            logger.info(f"Квест {quest_id} завершен для сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка завершения квеста: {e}")
            return False
    
    def _give_quest_rewards(self, entity_id: str, quest: Quest):
        """Выдача наград за квест"""
        try:
            for reward in quest.rewards:
                # TODO: Интеграция с другими системами для выдачи наград
                logger.info(f"Выдана награда {reward.reward_type.value} x{reward.amount} для {entity_id}")
                
                # Отправка события о награде
                if self.event_bus:
                    self.event_bus.emit("quest_reward_given", {
                        "entity_id": entity_id,
                        "quest_id": quest.quest_id,
                        "reward_type": reward.reward_type.value,
                        "amount": reward.amount
                    })
                    
        except Exception as e:
            logger.error(f"Ошибка выдачи наград: {e}")
    
    def get_available_quests(self, entity_id: str) -> List[Quest]:
        """Получить доступные квесты для сущности"""
        available = []
        
        for quest in self.available_quests.values():
            if self._can_start_quest(entity_id, quest):
                available.append(quest)
        
        return available
    
    def get_active_quests(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получить активные квесты сущности"""
        if entity_id not in self.active_quests:
            return []
        
        active_quests = []
        for quest_id, progress in self.active_quests[entity_id].items():
            quest = self.available_quests[quest_id]
            quest_info = {
                "quest": quest,
                "progress": progress,
                "completion_percentage": quest.get_progress_percentage()
            }
            active_quests.append(quest_info)
        
        return active_quests
    
    def get_completed_quests(self, entity_id: str) -> List[str]:
        """Получить завершенные квесты сущности"""
        return self.completed_quests.get(entity_id, [])
    
    def update(self, delta_time: float) -> None:
        """Обновление системы"""
        try:
            current_time = time.time()
            
            # Проверка истечения времени квестов
            self._check_quest_expiration(current_time)
            
            # Обновление статистики
            self.system_stats['update_time'] = current_time
            
            # Обновление состояний в StateManager
            if self.state_manager:
                self.state_manager.update_state("quest_system_stats", self.system_stats)
                
        except Exception as e:
            logger.error(f"Ошибка обновления системы квестов: {e}")
    
    def _check_quest_expiration(self, current_time: float):
        """Проверка истечения времени квестов"""
        expired_quests = []
        
        for entity_id, quests in self.active_quests.items():
            for quest_id, progress in quests.items():
                quest = self.available_quests[quest_id]
                if quest.is_expired():
                    expired_quests.append((entity_id, quest_id))
        
        # Удаление истекших квестов
        for entity_id, quest_id in expired_quests:
            self.fail_quest(entity_id, quest_id)
    
    def fail_quest(self, entity_id: str, quest_id: str) -> bool:
        """Провалить квест"""
        try:
            if entity_id not in self.active_quests or quest_id not in self.active_quests[entity_id]:
                return False
            
            # Обновление статистики
            self.system_stats['total_quests_failed'] += 1
            self.system_stats['active_quests_count'] -= 1
            
            # Удаление из активных квестов
            del self.active_quests[entity_id][quest_id]
            
            logger.info(f"Квест {quest_id} провален для сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка провала квеста: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получить информацию о системе"""
        return {
            "system_name": "QuestSystem",
            "state": self.state.value,
            "settings": self.system_settings,
            "stats": self.system_stats,
            "available_quests_count": len(self.available_quests),
            "active_quests_count": self.system_stats['active_quests_count'],
            "quest_chains_count": len(self.quest_chains)
        }
