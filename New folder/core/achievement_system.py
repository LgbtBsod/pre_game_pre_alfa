#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СИСТЕМА ДОСТИЖЕНИЙ
Централизованное управление достижениями и прогрессией
Соблюдает принцип единой ответственности
"""

import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from utils.logging_system import get_logger, log_system_event

class AchievementType(Enum):
    """Типы достижений"""
    COMBAT = "combat"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    CRAFTING = "crafting"
    COLLECTION = "collection"
    PROGRESSION = "progression"
    SPECIAL = "special"
    SECRET = "secret"

class AchievementRarity(Enum):
    """Редкость достижений"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class AchievementStatus(Enum):
    """Статус достижения"""
    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLAIMED = "claimed"

@dataclass
class AchievementCondition:
    """Условие достижения"""
    condition_type: str
    target_value: Any
    current_value: Any = 0
    description: str = ""

@dataclass
class Achievement:
    """Достижение"""
    achievement_id: str
    name: str
    description: str
    achievement_type: AchievementType
    rarity: AchievementRarity
    conditions: List[AchievementCondition]
    rewards: Dict[str, Any]
    prerequisites: List[str]
    hidden: bool = False
    repeatable: bool = False
    points: int = 0
    icon: str = ""
    created_at: float = 0.0

@dataclass
class PlayerAchievement:
    """Достижение игрока"""
    achievement: Achievement
    status: AchievementStatus
    progress: float = 0.0
    completed_at: float = 0.0
    claimed_at: float = 0.0
    progress_data: Dict[str, Any] = None

class AchievementSystem:
    """Система достижений"""
    
    def __init__(self, achievements_directory: str = "data/achievements"):
        self.achievements_directory = Path(achievements_directory)
        self.achievements_directory.mkdir(parents=True, exist_ok=True)
        
        # Словари для хранения достижений
        self.achievements: Dict[str, Achievement] = {}
        self.player_achievements: Dict[str, PlayerAchievement] = {}
        
        # Статистика
        self.total_points = 0
        self.completed_count = 0
        self.claimed_count = 0
        
        # Callbacks для событий
        self.achievement_callbacks: List[Callable] = []
        self.progress_callbacks: List[Callable] = []
        
        self.logger = get_logger("achievement_system")
        
        # Настройки
        self.auto_save_interval = 60.0  # Автосохранение каждую минуту
        self.last_auto_save = time.time()
        self.notifications_enabled = True
        
        # Инициализация
        self._initialize_achievements()
        self._load_player_progress()
        
        log_system_event("achievement_system", "initialized")
    
    def _initialize_achievements(self):
        """Инициализация базовых достижений"""
        base_achievements = [
            # Боевые достижения
            {
                "achievement_id": "first_kill",
                "name": "Первая кровь",
                "description": "Убейте первого врага",
                "achievement_type": AchievementType.COMBAT,
                "rarity": AchievementRarity.COMMON,
                "conditions": [
                    AchievementCondition("enemies_killed", 1, 0, "Убито врагов")
                ],
                "rewards": {"experience": 100, "gold": 50},
                "prerequisites": [],
                "points": 10
            },
            {
                "achievement_id": "killer_100",
                "name": "Убийца",
                "description": "Убейте 100 врагов",
                "achievement_type": AchievementType.COMBAT,
                "rarity": AchievementRarity.UNCOMMON,
                "conditions": [
                    AchievementCondition("enemies_killed", 100, 0, "Убито врагов")
                ],
                "rewards": {"experience": 1000, "gold": 500, "item": "sword_rare"},
                "prerequisites": ["first_kill"],
                "points": 50
            },
            {
                "achievement_id": "critical_hit_master",
                "name": "Мастер критических ударов",
                "description": "Нанесите 50 критических ударов",
                "achievement_type": AchievementType.COMBAT,
                "rarity": AchievementRarity.RARE,
                "conditions": [
                    AchievementCondition("critical_hits", 50, 0, "Критических ударов")
                ],
                "rewards": {"experience": 2000, "skill_point": 1},
                "prerequisites": [],
                "points": 100
            },
            
            # Достижения исследования
            {
                "achievement_id": "explorer",
                "name": "Исследователь",
                "description": "Посетите 10 различных локаций",
                "achievement_type": AchievementType.EXPLORATION,
                "rarity": AchievementRarity.COMMON,
                "conditions": [
                    AchievementCondition("locations_visited", 10, 0, "Посещено локаций")
                ],
                "rewards": {"experience": 500, "map": "world_map"},
                "prerequisites": [],
                "points": 25
            },
            {
                "achievement_id": "treasure_hunter",
                "name": "Охотник за сокровищами",
                "description": "Найдите 25 сокровищ",
                "achievement_type": AchievementType.EXPLORATION,
                "rarity": AchievementRarity.RARE,
                "conditions": [
                    AchievementCondition("treasures_found", 25, 0, "Найдено сокровищ")
                ],
                "rewards": {"experience": 1500, "gold": 1000, "item": "treasure_map"},
                "prerequisites": ["explorer"],
                "points": 75
            },
            
            # Социальные достижения
            {
                "achievement_id": "social_butterfly",
                "name": "Социальная бабочка",
                "description": "Поговорите с 20 NPC",
                "achievement_type": AchievementType.SOCIAL,
                "rarity": AchievementRarity.COMMON,
                "conditions": [
                    AchievementCondition("npcs_talked", 20, 0, "Поговорено с NPC")
                ],
                "rewards": {"experience": 300, "reputation": 50},
                "prerequisites": [],
                "points": 20
            },
            {
                "achievement_id": "quest_master",
                "name": "Мастер квестов",
                "description": "Выполните 50 квестов",
                "achievement_type": AchievementType.SOCIAL,
                "rarity": AchievementRarity.EPIC,
                "conditions": [
                    AchievementCondition("quests_completed", 50, 0, "Выполнено квестов")
                ],
                "rewards": {"experience": 5000, "gold": 2000, "title": "Quest Master"},
                "prerequisites": ["social_butterfly"],
                "points": 200
            },
            
            # Достижения крафтинга
            {
                "achievement_id": "first_craft",
                "name": "Первый мастер",
                "description": "Создайте первый предмет",
                "achievement_type": AchievementType.CRAFTING,
                "rarity": AchievementRarity.COMMON,
                "conditions": [
                    AchievementCondition("items_crafted", 1, 0, "Создано предметов")
                ],
                "rewards": {"experience": 200, "materials": {"wood": 10, "stone": 5}},
                "prerequisites": [],
                "points": 15
            },
            {
                "achievement_id": "master_crafter",
                "name": "Мастер-ремесленник",
                "description": "Создайте 100 предметов",
                "achievement_type": AchievementType.CRAFTING,
                "rarity": AchievementRarity.LEGENDARY,
                "conditions": [
                    AchievementCondition("items_crafted", 100, 0, "Создано предметов")
                ],
                "rewards": {"experience": 3000, "gold": 1500, "recipe": "legendary_sword"},
                "prerequisites": ["first_craft"],
                "points": 150
            },
            
            # Достижения коллекционирования
            {
                "achievement_id": "collector",
                "name": "Коллекционер",
                "description": "Соберите 50 уникальных предметов",
                "achievement_type": AchievementType.COLLECTION,
                "rarity": AchievementRarity.UNCOMMON,
                "conditions": [
                    AchievementCondition("unique_items_collected", 50, 0, "Уникальных предметов")
                ],
                "rewards": {"experience": 800, "storage_upgrade": 1},
                "prerequisites": [],
                "points": 40
            },
            
            # Достижения прогрессии
            {
                "achievement_id": "level_10",
                "name": "Новичок",
                "description": "Достигните 10 уровня",
                "achievement_type": AchievementType.PROGRESSION,
                "rarity": AchievementRarity.COMMON,
                "conditions": [
                    AchievementCondition("player_level", 10, 0, "Уровень игрока")
                ],
                "rewards": {"experience": 500, "skill_point": 2},
                "prerequisites": [],
                "points": 30
            },
            {
                "achievement_id": "level_50",
                "name": "Опытный воин",
                "description": "Достигните 50 уровня",
                "achievement_type": AchievementType.PROGRESSION,
                "rarity": AchievementRarity.EPIC,
                "conditions": [
                    AchievementCondition("player_level", 50, 0, "Уровень игрока")
                ],
                "rewards": {"experience": 2000, "skill_point": 5, "title": "Veteran"},
                "prerequisites": ["level_10"],
                "points": 100
            },
            
            # Специальные достижения
            {
                "achievement_id": "speedrunner",
                "name": "Спидраннер",
                "description": "Пройдите игру менее чем за 2 часа",
                "achievement_type": AchievementType.SPECIAL,
                "rarity": AchievementRarity.MYTHIC,
                "conditions": [
                    AchievementCondition("game_completion_time", 7200, 0, "Время прохождения (секунды)")
                ],
                "rewards": {"experience": 10000, "gold": 5000, "title": "Speedrunner"},
                "prerequisites": [],
                "points": 500,
                "hidden": True
            }
        ]
        
        # Создаем достижения
        for achievement_data in base_achievements:
            achievement = Achievement(
                achievement_id=achievement_data["achievement_id"],
                name=achievement_data["name"],
                description=achievement_data["description"],
                achievement_type=achievement_data["achievement_type"],
                rarity=achievement_data["rarity"],
                conditions=achievement_data["conditions"],
                rewards=achievement_data["rewards"],
                prerequisites=achievement_data["prerequisites"],
                hidden=achievement_data.get("hidden", False),
                points=achievement_data["points"],
                created_at=time.time()
            )
            
            self.achievements[achievement.achievement_id] = achievement
            
            # Создаем запись игрока
            self.player_achievements[achievement.achievement_id] = PlayerAchievement(
                achievement=achievement,
                status=AchievementStatus.LOCKED,
                progress_data={}
            )
    
    def update_progress(self, condition_type: str, value: Any, player_data: Dict[str, Any] = None):
        """Обновление прогресса достижений"""
        try:
            updated_achievements = []
            
            for achievement_id, player_achievement in self.player_achievements.items():
                if player_achievement.status in [AchievementStatus.COMPLETED, AchievementStatus.CLAIMED]:
                    continue
                
                achievement = player_achievement.achievement
                updated = False
                
                # Проверяем условия
                for condition in achievement.conditions:
                    if condition.condition_type == condition_type:
                        # Обновляем значение
                        if isinstance(condition.current_value, (int, float)):
                            condition.current_value += value
                        else:
                            condition.current_value = value
                        
                        updated = True
                        
                        # Проверяем выполнение условия
                        if self._check_condition_completion(condition):
                            # Проверяем все условия достижения
                            if self._check_achievement_completion(achievement):
                                self._complete_achievement(achievement_id)
                                updated_achievements.append(achievement)
                
                # Обновляем прогресс
                if updated:
                    player_achievement.progress = self._calculate_progress(achievement)
                    
                    # Проверяем разблокировку
                    if player_achievement.status == AchievementStatus.LOCKED:
                        if self._check_prerequisites(achievement):
                            player_achievement.status = AchievementStatus.IN_PROGRESS
                            self._notify_achievement_unlocked(achievement)
            
            # Уведомляем о прогрессе
            if updated_achievements:
                self._notify_progress_update(condition_type, value, updated_achievements)
            
            # Автосохранение
            current_time = time.time()
            if current_time - self.last_auto_save > self.auto_save_interval:
                self.save_progress()
                self.last_auto_save = current_time
                
        except Exception as e:
            self.logger.error(f"Ошибка обновления прогресса: {e}")
    
    def _check_condition_completion(self, condition: AchievementCondition) -> bool:
        """Проверка выполнения условия"""
        if isinstance(condition.current_value, (int, float)) and isinstance(condition.target_value, (int, float)):
            return condition.current_value >= condition.target_value
        else:
            return condition.current_value == condition.target_value
    
    def _check_achievement_completion(self, achievement: Achievement) -> bool:
        """Проверка выполнения всех условий достижения"""
        return all(self._check_condition_completion(condition) for condition in achievement.conditions)
    
    def _check_prerequisites(self, achievement: Achievement) -> bool:
        """Проверка выполнения предварительных условий"""
        for prereq_id in achievement.prerequisites:
            if prereq_id not in self.player_achievements:
                return False
            
            prereq_status = self.player_achievements[prereq_id].status
            if prereq_status not in [AchievementStatus.COMPLETED, AchievementStatus.CLAIMED]:
                return False
        
        return True
    
    def _complete_achievement(self, achievement_id: str):
        """Завершение достижения"""
        try:
            player_achievement = self.player_achievements[achievement_id]
            player_achievement.status = AchievementStatus.COMPLETED
            player_achievement.completed_at = time.time()
            
            self.completed_count += 1
            self.total_points += player_achievement.achievement.points
            
            # Уведомляем о завершении
            self._notify_achievement_completed(player_achievement.achievement)
            
            log_system_event("achievement_system", "achievement_completed", {
                "achievement_id": achievement_id,
                "name": player_achievement.achievement.name,
                "points": player_achievement.achievement.points
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка завершения достижения {achievement_id}: {e}")
    
    def claim_achievement(self, achievement_id: str) -> bool:
        """Получение награды за достижение"""
        try:
            if achievement_id not in self.player_achievements:
                return False
            
            player_achievement = self.player_achievements[achievement_id]
            
            if player_achievement.status != AchievementStatus.COMPLETED:
                return False
            
            player_achievement.status = AchievementStatus.CLAIMED
            player_achievement.claimed_at = time.time()
            self.claimed_count += 1
            
            # Выдаем награды
            rewards = player_achievement.achievement.rewards
            self._give_rewards(rewards)
            
            log_system_event("achievement_system", "achievement_claimed", {
                "achievement_id": achievement_id,
                "rewards": rewards
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка получения награды {achievement_id}: {e}")
            return False
    
    def _give_rewards(self, rewards: Dict[str, Any]):
        """Выдача наград"""
        # Здесь должна быть интеграция с игровыми системами
        # Для демонстрации просто логируем
        self.logger.info(f"Выданы награды: {rewards}")
    
    def _calculate_progress(self, achievement: Achievement) -> float:
        """Вычисление прогресса достижения"""
        if not achievement.conditions:
            return 0.0
        
        total_progress = 0.0
        for condition in achievement.conditions:
            if isinstance(condition.current_value, (int, float)) and isinstance(condition.target_value, (int, float)):
                if condition.target_value > 0:
                    progress = min(condition.current_value / condition.target_value, 1.0)
                    total_progress += progress
        
        return total_progress / len(achievement.conditions)
    
    def _notify_achievement_completed(self, achievement: Achievement):
        """Уведомление о завершении достижения"""
        if self.notifications_enabled:
            for callback in self.achievement_callbacks:
                try:
                    callback("completed", achievement)
                except Exception as e:
                    self.logger.error(f"Ошибка в callback достижения: {e}")
    
    def _notify_achievement_unlocked(self, achievement: Achievement):
        """Уведомление о разблокировке достижения"""
        if self.notifications_enabled:
            for callback in self.achievement_callbacks:
                try:
                    callback("unlocked", achievement)
                except Exception as e:
                    self.logger.error(f"Ошибка в callback достижения: {e}")
    
    def _notify_progress_update(self, condition_type: str, value: Any, achievements: List[Achievement]):
        """Уведомление об обновлении прогресса"""
        for callback in self.progress_callbacks:
            try:
                callback(condition_type, value, achievements)
            except Exception as e:
                self.logger.error(f"Ошибка в callback прогресса: {e}")
    
    def register_achievement_callback(self, callback: Callable):
        """Регистрация callback для достижений"""
        self.achievement_callbacks.append(callback)
    
    def register_progress_callback(self, callback: Callable):
        """Регистрация callback для прогресса"""
        self.progress_callbacks.append(callback)
    
    def get_achievements_by_type(self, achievement_type: AchievementType) -> List[PlayerAchievement]:
        """Получение достижений по типу"""
        return [
            player_achievement for player_achievement in self.player_achievements.values()
            if player_achievement.achievement.achievement_type == achievement_type
        ]
    
    def get_achievements_by_status(self, status: AchievementStatus) -> List[PlayerAchievement]:
        """Получение достижений по статусу"""
        return [
            player_achievement for player_achievement in self.player_achievements.values()
            if player_achievement.status == status
        ]
    
    def get_visible_achievements(self) -> List[PlayerAchievement]:
        """Получение видимых достижений"""
        return [
            player_achievement for player_achievement in self.player_achievements.values()
            if not player_achievement.achievement.hidden or 
            player_achievement.status in [AchievementStatus.IN_PROGRESS, AchievementStatus.COMPLETED, AchievementStatus.CLAIMED]
        ]
    
    def save_progress(self) -> bool:
        """Сохранение прогресса"""
        try:
            save_data = {
                "player_achievements": {},
                "total_points": self.total_points,
                "completed_count": self.completed_count,
                "claimed_count": self.claimed_count,
                "timestamp": time.time()
            }
            
            for achievement_id, player_achievement in self.player_achievements.items():
                save_data["player_achievements"][achievement_id] = {
                    "status": player_achievement.status.value,
                    "progress": player_achievement.progress,
                    "completed_at": player_achievement.completed_at,
                    "claimed_at": player_achievement.claimed_at,
                    "progress_data": player_achievement.progress_data or {},
                    "conditions": [
                        {
                            "condition_type": condition.condition_type,
                            "current_value": condition.current_value,
                            "target_value": condition.target_value
                        }
                        for condition in player_achievement.achievement.conditions
                    ]
                }
            
            save_file = self.achievements_directory / "player_progress.json"
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            log_system_event("achievement_system", "progress_saved")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения прогресса: {e}")
            return False
    
    def _load_player_progress(self) -> bool:
        """Загрузка прогресса игрока"""
        try:
            save_file = self.achievements_directory / "player_progress.json"
            if not save_file.exists():
                return False
            
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Восстанавливаем статистику
            self.total_points = save_data.get("total_points", 0)
            self.completed_count = save_data.get("completed_count", 0)
            self.claimed_count = save_data.get("claimed_count", 0)
            
            # Восстанавливаем прогресс достижений
            for achievement_id, progress_data in save_data.get("player_achievements", {}).items():
                if achievement_id in self.player_achievements:
                    player_achievement = self.player_achievements[achievement_id]
                    
                    player_achievement.status = AchievementStatus(progress_data["status"])
                    player_achievement.progress = progress_data.get("progress", 0.0)
                    player_achievement.completed_at = progress_data.get("completed_at", 0.0)
                    player_achievement.claimed_at = progress_data.get("claimed_at", 0.0)
                    player_achievement.progress_data = progress_data.get("progress_data", {})
                    
                    # Восстанавливаем условия
                    for i, condition_data in enumerate(progress_data.get("conditions", [])):
                        if i < len(player_achievement.achievement.conditions):
                            condition = player_achievement.achievement.conditions[i]
                            condition.current_value = condition_data["current_value"]
            
            log_system_event("achievement_system", "progress_loaded")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки прогресса: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики системы достижений"""
        return {
            "total_achievements": len(self.achievements),
            "completed_achievements": self.completed_count,
            "claimed_achievements": self.claimed_count,
            "total_points": self.total_points,
            "achievements_by_type": {
                achievement_type.value: len(self.get_achievements_by_type(achievement_type))
                for achievement_type in AchievementType
            },
            "achievements_by_status": {
                status.value: len(self.get_achievements_by_status(status))
                for status in AchievementStatus
            },
            "achievements_by_rarity": {
                rarity.value: len([
                    pa for pa in self.player_achievements.values()
                    if pa.achievement.rarity == rarity
                ])
                for rarity in AchievementRarity
            }
        }
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.save_progress()
        self.achievement_callbacks.clear()
        self.progress_callbacks.clear()
        
        log_system_event("achievement_system", "cleanup_completed")
