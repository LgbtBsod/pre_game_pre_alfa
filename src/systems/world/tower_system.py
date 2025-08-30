#!/usr/bin/env python3
"""Система башен и испытаний для игрового мира
Включает процедурную генерацию башен, уровни сложности и награды"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
import logging
import random
import time
import math

from src.core.architecture import BaseComponent, ComponentType, Priority

# = ТИПЫ БАШЕН
class TowerType(Enum):
    """Типы башен"""
    TRIAL = "trial"           # Башня испытаний
    CHALLENGE = "challenge"   # Башня вызовов
    EVOLUTION = "evolution"   # Башня эволюции
    MASTERY = "mastery"       # Башня мастерства
    INFINITY = "infinity"     # Бесконечная башня
    LEGACY = "legacy"         # Башня наследия
    MYSTERY = "mystery"       # Башня тайн
    ASCENSION = "ascension"   # Башня вознесения

# = ТИПЫ ИСПЫТАНИЙ
class ChallengeType(Enum):
    """Типы испытаний"""
    COMBAT = "combat"         # Боевое испытание
    PUZZLE = "puzzle"         # Головоломка
    SURVIVAL = "survival"     # Выживание
    SPEED = "speed"           # Скорость
    STEALTH = "stealth"       # Скрытность
    EVOLUTION = "evolution"   # Эволюция
    ADAPTATION = "adaptation" # Адаптация
    MASTERY = "mastery"       # Мастерство

# = ТИПЫ НАГРАД
class RewardType(Enum):
    """Типы наград"""
    EXPERIENCE = "experience"     # Опыт
    EVOLUTION_POINTS = "evolution_points"  # Очки эволюции
    MUTATIONS = "mutations"       # Мутации
    ABILITIES = "abilities"       # Способности
    EQUIPMENT = "equipment"       # Снаряжение
    RESOURCES = "resources"       # Ресурсы
    KNOWLEDGE = "knowledge"       # Знания
    TITLES = "titles"             # Титулы

# = НАСТРОЙКИ БАШЕН
@dataclass
class TowerSettings:
    """Настройки башни"""
    tower_type: TowerType
    max_floors: int = 100
    floors_per_level: int = 10
    difficulty_scaling: float = 1.2
    reward_multiplier: float = 1.1
    time_limit_per_floor: int = 300  # секунды
    allow_retry: bool = True
    save_progress: bool = True
    adaptive_difficulty: bool = True

# = НАСТРОЙКИ ИСПЫТАНИЙ
@dataclass
class ChallengeSettings:
    """Настройки испытания"""
    challenge_type: ChallengeType
    difficulty: int = 1
    time_limit: int = 60
    required_score: int = 100
    enemy_count: int = 5
    puzzle_complexity: int = 3
    survival_duration: int = 120
    stealth_requirements: Dict[str, Any] = field(default_factory=dict)
    evolution_requirements: Dict[str, Any] = field(default_factory=dict)

# = НАСТРОЙКИ НАГРАД
@dataclass
class RewardSettings:
    """Настройки награды"""
    reward_type: RewardType
    base_amount: int = 100
    scaling_factor: float = 1.1
    rarity_multiplier: float = 1.0
    floor_bonus: float = 0.1
    completion_bonus: float = 0.5

# = СТРУКТУРЫ ДАННЫХ
@dataclass
class TowerFloor:
    """Этаж башни"""
    floor_number: int
    challenge: ChallengeSettings
    rewards: List[RewardSettings]
    completed: bool = False
    best_score: int = 0
    completion_time: float = 0.0
    attempts: int = 0
    unlocked: bool = False

@dataclass
class TowerLevel:
    """Уровень башни"""
    level_number: int
    floors: List[TowerFloor]
    completed: bool = False
    boss_floor: Optional[TowerFloor] = None
    level_reward: Optional[RewardSettings] = None

@dataclass
class GeneratedTower:
    """Сгенерированная башня"""
    tower_id: str
    tower_type: TowerType
    settings: TowerSettings
    levels: List[TowerLevel]
    current_floor: int = 1
    current_level: int = 1
    total_floors_completed: int = 0
    total_score: int = 0
    total_time: float = 0.0
    created_at: float = field(default_factory=time.time)

@dataclass
class TowerProgress:
    """Прогресс в башне"""
    tower_id: str
    character_id: str
    current_floor: int
    current_level: int
    completed_floors: Set[int]
    best_scores: Dict[int, int]
    completion_times: Dict[int, float]
    total_attempts: int
    total_score: int
    total_time: float
    last_attempt: float = 0.0

# = СИСТЕМА БАШЕН
class TowerSystem(BaseComponent):
    """Система башен и испытаний"""
    
    def __init__(self):
        super().__init__(
            component_id="TowerSystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Настройки системы
        self.tower_templates: Dict[TowerType, TowerSettings] = {}
        self.challenge_templates: Dict[ChallengeType, Dict[int, ChallengeSettings]] = {}
        self.reward_templates: Dict[RewardType, RewardSettings] = {}
        
        # Генерированные башни
        self.generated_towers: Dict[str, GeneratedTower] = {}
        self.tower_progress: Dict[str, TowerProgress] = {}
        
        # Кэши и статистика
        self.tower_cache: Dict[str, Any] = {}
        self.generation_stats = {
            "towers_created": 0,
            "floors_generated": 0,
            "challenges_created": 0,
            "rewards_generated": 0,
            "total_generation_time": 0.0
        }
        
        # Слушатели событий
        self.floor_completed_callbacks: List[callable] = []
        self.level_completed_callbacks: List[callable] = []
        self.tower_completed_callbacks: List[callable] = []
        
        self.logger = logging.getLogger(__name__)
    
    def _on_initialize(self) -> bool:
        """Инициализация системы башен"""
        try:
            self._initialize_tower_templates()
            self._initialize_challenge_templates()
            self._initialize_reward_templates()
            
            self.logger.info("TowerSystem инициализирован")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации TowerSystem: {e}")
            return False
    
    def _initialize_tower_templates(self):
        """Инициализация шаблонов башен"""
        self.tower_templates = {
            TowerType.TRIAL: TowerSettings(
                tower_type=TowerType.TRIAL,
                max_floors=50,
                floors_per_level=5,
                difficulty_scaling=1.1,
                reward_multiplier=1.0,
                time_limit_per_floor=180
            ),
            TowerType.CHALLENGE: TowerSettings(
                tower_type=TowerType.CHALLENGE,
                max_floors=100,
                floors_per_level=10,
                difficulty_scaling=1.3,
                reward_multiplier=1.2,
                time_limit_per_floor=240
            ),
            TowerType.EVOLUTION: TowerSettings(
                tower_type=TowerType.EVOLUTION,
                max_floors=200,
                floors_per_level=20,
                difficulty_scaling=1.15,
                reward_multiplier=1.5,
                time_limit_per_floor=300,
                adaptive_difficulty=True
            ),
            TowerType.MASTERY: TowerSettings(
                tower_type=TowerType.MASTERY,
                max_floors=500,
                floors_per_level=25,
                difficulty_scaling=1.25,
                reward_multiplier=2.0,
                time_limit_per_floor=600
            ),
            TowerType.INFINITY: TowerSettings(
                tower_type=TowerType.INFINITY,
                max_floors=9999,
                floors_per_level=100,
                difficulty_scaling=1.1,
                reward_multiplier=1.05,
                time_limit_per_floor=120,
                allow_retry=True
            ),
            TowerType.LEGACY: TowerSettings(
                tower_type=TowerType.LEGACY,
                max_floors=1000,
                floors_per_level=50,
                difficulty_scaling=1.4,
                reward_multiplier=3.0,
                time_limit_per_floor=900
            ),
            TowerType.MYSTERY: TowerSettings(
                tower_type=TowerType.MYSTERY,
                max_floors=300,
                floors_per_level=15,
                difficulty_scaling=1.2,
                reward_multiplier=1.8,
                time_limit_per_floor=400
            ),
            TowerType.ASCENSION: TowerSettings(
                tower_type=TowerType.ASCENSION,
                max_floors=10000,
                floors_per_level=1000,
                difficulty_scaling=1.05,
                reward_multiplier=5.0,
                time_limit_per_floor=3600
            )
        }
    
    def _initialize_challenge_templates(self):
        """Инициализация шаблонов испытаний"""
        for challenge_type in ChallengeType:
            self.challenge_templates[challenge_type] = {}
            
            for difficulty in range(1, 11):
                base_settings = ChallengeSettings(
                    challenge_type=challenge_type,
                    difficulty=difficulty
                )
                
                # Настройка параметров в зависимости от типа
                if challenge_type == ChallengeType.COMBAT:
                    base_settings.enemy_count = difficulty * 2
                    base_settings.required_score = difficulty * 50
                elif challenge_type == ChallengeType.PUZZLE:
                    base_settings.puzzle_complexity = difficulty
                    base_settings.time_limit = 120 - (difficulty * 5)
                elif challenge_type == ChallengeType.SURVIVAL:
                    base_settings.survival_duration = difficulty * 30
                    base_settings.enemy_count = difficulty
                elif challenge_type == ChallengeType.SPEED:
                    base_settings.time_limit = 60 - (difficulty * 3)
                    base_settings.required_score = difficulty * 100
                elif challenge_type == ChallengeType.STEALTH:
                    base_settings.stealth_requirements = {
                        "detection_threshold": 100 - (difficulty * 5),
                        "required_stealth_score": difficulty * 20
                    }
                elif challenge_type == ChallengeType.EVOLUTION:
                    base_settings.evolution_requirements = {
                        "required_mutations": difficulty,
                        "evolution_points": difficulty * 10
                    }
                
                self.challenge_templates[challenge_type][difficulty] = base_settings
    
    def _initialize_reward_templates(self):
        """Инициализация шаблонов наград"""
        self.reward_templates = {
            RewardType.EXPERIENCE: RewardSettings(
                reward_type=RewardType.EXPERIENCE,
                base_amount=100,
                scaling_factor=1.2
            ),
            RewardType.EVOLUTION_POINTS: RewardSettings(
                reward_type=RewardType.EVOLUTION_POINTS,
                base_amount=10,
                scaling_factor=1.1
            ),
            RewardType.MUTATIONS: RewardSettings(
                reward_type=RewardType.MUTATIONS,
                base_amount=1,
                scaling_factor=1.05,
                rarity_multiplier=2.0
            ),
            RewardType.ABILITIES: RewardSettings(
                reward_type=RewardType.ABILITIES,
                base_amount=1,
                scaling_factor=1.1,
                rarity_multiplier=3.0
            ),
            RewardType.EQUIPMENT: RewardSettings(
                reward_type=RewardType.EQUIPMENT,
                base_amount=1,
                scaling_factor=1.15,
                rarity_multiplier=1.5
            ),
            RewardType.RESOURCES: RewardSettings(
                reward_type=RewardType.RESOURCES,
                base_amount=50,
                scaling_factor=1.1
            ),
            RewardType.KNOWLEDGE: RewardSettings(
                reward_type=RewardType.KNOWLEDGE,
                base_amount=1,
                scaling_factor=1.2,
                rarity_multiplier=2.5
            ),
            RewardType.TITLES: RewardSettings(
                reward_type=RewardType.TITLES,
                base_amount=1,
                scaling_factor=1.0,
                rarity_multiplier=5.0
            )
        }
    
    def generate_tower(self, tower_type: TowerType, world_seed: int = None) -> GeneratedTower:
        """Генерация новой башни"""
        start_time = time.time()
        
        if world_seed is None:
            world_seed = int(time.time())
        
        random.seed(world_seed)
        
        # Получение настроек башни
        settings = self.tower_templates.get(tower_type)
        if not settings:
            raise ValueError(f"Неизвестный тип башни: {tower_type}")
        
        # Создание ID башни
        tower_id = f"tower_{tower_type.value}_{world_seed}"
        
        # Генерация уровней и этажей
        levels = []
        floor_number = 1
        
        for level_num in range(1, (settings.max_floors // settings.floors_per_level) + 1):
            level_floors = []
            
            # Генерация обычных этажей
            for floor_in_level in range(settings.floors_per_level):
                if floor_number > settings.max_floors:
                    break
                
                challenge = self._generate_challenge_for_floor(floor_number, settings)
                rewards = self._generate_rewards_for_floor(floor_number, settings)
                
                floor = TowerFloor(
                    floor_number=floor_number,
                    challenge=challenge,
                    rewards=rewards,
                    unlocked=(floor_number == 1)
                )
                
                level_floors.append(floor)
                floor_number += 1
            
            # Создание уровня
            level = TowerLevel(
                level_number=level_num,
                floors=level_floors
            )
            
            # Добавление босса на последний этаж уровня
            if level_floors and level_num % 5 == 0:  # Каждый 5-й уровень
                boss_challenge = self._generate_boss_challenge(level_num, settings)
                boss_rewards = self._generate_boss_rewards(level_num, settings)
                
                level.boss_floor = TowerFloor(
                    floor_number=floor_number,
                    challenge=boss_challenge,
                    rewards=boss_rewards,
                    unlocked=False
                )
                floor_number += 1
            
            levels.append(level)
        
        # Создание башни
        tower = GeneratedTower(
            tower_id=tower_id,
            tower_type=tower_type,
            settings=settings,
            levels=levels
        )
        
        self.generated_towers[tower_id] = tower
        
        # Обновление статистики
        generation_time = time.time() - start_time
        self.generation_stats["towers_created"] += 1
        self.generation_stats["floors_generated"] += sum(len(level.floors) for level in levels)
        self.generation_stats["total_generation_time"] += generation_time
        
        self.logger.info(f"Создана башня {tower_id}: {len(levels)} уровней, {sum(len(level.floors) for level in levels)} этажей")
        
        return tower
    
    def _generate_challenge_for_floor(self, floor_number: int, settings: TowerSettings) -> ChallengeSettings:
        """Генерация испытания для этажа"""
        # Выбор типа испытания
        challenge_types = list(ChallengeType)
        challenge_type = random.choice(challenge_types)
        
        # Расчет сложности
        base_difficulty = max(1, floor_number // 10)
        difficulty_variation = random.randint(-2, 2)
        difficulty = max(1, min(10, base_difficulty + difficulty_variation))
        
        # Получение базовых настроек
        challenge = self.challenge_templates[challenge_type][difficulty]
        
        # Применение масштабирования сложности
        scaling = settings.difficulty_scaling ** (floor_number // 10)
        
        # Создание нового экземпляра с масштабированными параметрами
        scaled_challenge = ChallengeSettings(
            challenge_type=challenge.challenge_type,
            difficulty=difficulty,
            time_limit=int(challenge.time_limit * scaling),
            required_score=int(challenge.required_score * scaling),
            enemy_count=int(challenge.enemy_count * scaling),
            puzzle_complexity=challenge.puzzle_complexity,
            survival_duration=int(challenge.survival_duration * scaling),
            stealth_requirements=challenge.stealth_requirements.copy(),
            evolution_requirements=challenge.evolution_requirements.copy()
        )
        
        return scaled_challenge
    
    def _generate_boss_challenge(self, level_number: int, settings: TowerSettings) -> ChallengeSettings:
        """Генерация босс-испытания"""
        # Босс всегда боевое испытание
        challenge_type = ChallengeType.COMBAT
        
        # Высокая сложность для босса
        difficulty = min(10, level_number // 5 + 5)
        
        # Получение базовых настроек
        challenge = self.challenge_templates[challenge_type][difficulty]
        
        # Усиление параметров для босса
        boss_challenge = ChallengeSettings(
            challenge_type=challenge.challenge_type,
            difficulty=difficulty,
            time_limit=challenge.time_limit * 2,
            required_score=challenge.required_score * 3,
            enemy_count=1,  # Один босс
            puzzle_complexity=challenge.puzzle_complexity,
            survival_duration=challenge.survival_duration,
            stealth_requirements=challenge.stealth_requirements.copy(),
            evolution_requirements=challenge.evolution_requirements.copy()
        )
        
        return boss_challenge
    
    def _generate_rewards_for_floor(self, floor_number: int, settings: TowerSettings) -> List[RewardSettings]:
        """Генерация наград для этажа"""
        rewards = []
        
        # Базовые награды
        base_rewards = [RewardType.EXPERIENCE, RewardType.EVOLUTION_POINTS]
        
        for reward_type in base_rewards:
            template = self.reward_templates[reward_type]
            
            # Расчет количества награды
            amount = int(template.base_amount * (template.scaling_factor ** (floor_number // 10)))
            amount = int(amount * settings.reward_multiplier)
            
            reward = RewardSettings(
                reward_type=template.reward_type,
                base_amount=amount,
                scaling_factor=template.scaling_factor,
                rarity_multiplier=template.rarity_multiplier,
                floor_bonus=template.floor_bonus,
                completion_bonus=template.completion_bonus
            )
            
            rewards.append(reward)
        
        # Случайные дополнительные награды
        if random.random() < 0.3:  # 30% шанс
            special_rewards = [rt for rt in RewardType if rt not in base_rewards]
            special_reward_type = random.choice(special_rewards)
            
            template = self.reward_templates[special_reward_type]
            amount = max(1, int(template.base_amount * (template.scaling_factor ** (floor_number // 20))))
            
            special_reward = RewardSettings(
                reward_type=template.reward_type,
                base_amount=amount,
                scaling_factor=template.scaling_factor,
                rarity_multiplier=template.rarity_multiplier,
                floor_bonus=template.floor_bonus,
                completion_bonus=template.completion_bonus
            )
            
            rewards.append(special_reward)
        
        return rewards
    
    def _generate_boss_rewards(self, level_number: int, settings: TowerSettings) -> List[RewardSettings]:
        """Генерация наград босса"""
        rewards = []
        
        # Увеличенные награды для босса
        boss_multiplier = 3.0
        
        for reward_type in RewardType:
            template = self.reward_templates[reward_type]
            
            # Расчет количества награды
            amount = int(template.base_amount * (template.scaling_factor ** (level_number // 5)))
            amount = int(amount * settings.reward_multiplier * boss_multiplier)
            
            reward = RewardSettings(
                reward_type=template.reward_type,
                base_amount=amount,
                scaling_factor=template.scaling_factor,
                rarity_multiplier=template.rarity_multiplier * 2,  # Увеличенная редкость
                floor_bonus=template.floor_bonus,
                completion_bonus=template.completion_bonus * 2
            )
            
            rewards.append(reward)
        
        return rewards
    
    def register_character_progress(self, tower_id: str, character_id: str) -> TowerProgress:
        """Регистрация прогресса персонажа в башне"""
        if tower_id not in self.generated_towers:
            raise ValueError(f"Башня {tower_id} не найдена")
        
        progress_key = f"{tower_id}_{character_id}"
        
        if progress_key not in self.tower_progress:
            progress = TowerProgress(
                tower_id=tower_id,
                character_id=character_id,
                current_floor=1,
                current_level=1,
                completed_floors=set(),
                best_scores={},
                completion_times={},
                total_attempts=0,
                total_score=0,
                total_time=0.0
            )
            
            self.tower_progress[progress_key] = progress
        
        return self.tower_progress[progress_key]
    
    def start_floor_challenge(self, tower_id: str, character_id: str, floor_number: int) -> bool:
        """Начало испытания на этаже"""
        progress_key = f"{tower_id}_{character_id}"
        
        if progress_key not in self.tower_progress:
            self.register_character_progress(tower_id, character_id)
        
        progress = self.tower_progress[progress_key]
        
        # Проверка доступности этажа
        tower = self.generated_towers[tower_id]
        floor = self._get_floor(tower, floor_number)
        
        if not floor or not floor.unlocked:
            return False
        
        # Обновление прогресса
        progress.current_floor = floor_number
        progress.current_level = (floor_number - 1) // tower.settings.floors_per_level + 1
        progress.total_attempts += 1
        progress.last_attempt = time.time()
        
        self.logger.info(f"Персонаж {character_id} начал испытание на этаже {floor_number} башни {tower_id}")
        
        return True
    
    def complete_floor_challenge(self, tower_id: str, character_id: str, floor_number: int, 
                                score: int, completion_time: float) -> bool:
        """Завершение испытания на этаже"""
        progress_key = f"{tower_id}_{character_id}"
        
        if progress_key not in self.tower_progress:
            return False
        
        progress = self.tower_progress[progress_key]
        tower = self.generated_towers[tower_id]
        floor = self._get_floor(tower, floor_number)
        
        if not floor:
            return False
        
        # Обновление прогресса
        progress.completed_floors.add(floor_number)
        progress.total_score += score
        progress.total_time += completion_time
        
        # Обновление лучших результатов
        if floor_number not in progress.best_scores or score > progress.best_scores[floor_number]:
            progress.best_scores[floor_number] = score
        
        if floor_number not in progress.completion_times or completion_time < progress.completion_times[floor_number]:
            progress.completion_times[floor_number] = completion_time
        
        # Отметка этажа как завершенного
        floor.completed = True
        floor.best_score = max(floor.best_score, score)
        floor.completion_time = min(floor.completion_time, completion_time) if floor.completion_time > 0 else completion_time
        floor.attempts += 1
        
        # Разблокировка следующего этажа
        next_floor = self._get_floor(tower, floor_number + 1)
        if next_floor:
            next_floor.unlocked = True
        
        # Проверка завершения уровня
        self._check_level_completion(tower, progress)
        
        # Уведомление о завершении этажа
        self._notify_floor_completed(tower_id, character_id, floor_number, score, completion_time)
        
        self.logger.info(f"Персонаж {character_id} завершил этаж {floor_number} башни {tower_id} с результатом {score}")
        
        return True
    
    def _get_floor(self, tower: GeneratedTower, floor_number: int) -> Optional[TowerFloor]:
        """Получение этажа по номеру"""
        for level in tower.levels:
            for floor in level.floors:
                if floor.floor_number == floor_number:
                    return floor
            
            if level.boss_floor and level.boss_floor.floor_number == floor_number:
                return level.boss_floor
        
        return None
    
    def _check_level_completion(self, tower: GeneratedTower, progress: TowerProgress):
        """Проверка завершения уровня"""
        current_level = progress.current_level
        
        if current_level > len(tower.levels):
            return
        
        level = tower.levels[current_level - 1]
        
        # Проверка завершения всех этажей уровня
        all_floors_completed = all(
            floor.floor_number in progress.completed_floors 
            for floor in level.floors
        )
        
        # Проверка завершения босса
        boss_completed = True
        if level.boss_floor:
            boss_completed = level.boss_floor.floor_number in progress.completed_floors
        
        if all_floors_completed and boss_completed:
            level.completed = True
            progress.current_level += 1
            
            # Уведомление о завершении уровня
            self._notify_level_completed(tower.tower_id, progress.character_id, current_level)
    
    def get_tower_progress(self, tower_id: str, character_id: str) -> Optional[TowerProgress]:
        """Получение прогресса персонажа в башне"""
        progress_key = f"{tower_id}_{character_id}"
        return self.tower_progress.get(progress_key)
    
    def get_available_towers(self, character_level: int = 1) -> List[GeneratedTower]:
        """Получение доступных башен для персонажа"""
        available_towers = []
        
        for tower in self.generated_towers.values():
            # Простая проверка по уровню персонажа
            if tower.tower_type in [TowerType.TRIAL, TowerType.CHALLENGE]:
                available_towers.append(tower)
            elif tower.tower_type in [TowerType.EVOLUTION, TowerType.MASTERY] and character_level >= 10:
                available_towers.append(tower)
            elif tower.tower_type in [TowerType.LEGACY, TowerType.MYSTERY] and character_level >= 20:
                available_towers.append(tower)
            elif tower.tower_type in [TowerType.INFINITY, TowerType.ASCENSION] and character_level >= 50:
                available_towers.append(tower)
        
        return available_towers
    
    def get_tower_statistics(self, tower_id: str) -> Dict[str, Any]:
        """Получение статистики башни"""
        if tower_id not in self.generated_towers:
            return {}
        
        tower = self.generated_towers[tower_id]
        
        # Подсчет статистики по прогрессу
        total_players = len([p for p in self.tower_progress.values() if p.tower_id == tower_id])
        completed_players = len([p for p in self.tower_progress.values() 
                               if p.tower_id == tower_id and p.completed_floors])
        
        # Статистика по этажам
        floor_stats = {}
        for level in tower.levels:
            for floor in level.floors:
                completed_count = len([p for p in self.tower_progress.values() 
                                     if p.tower_id == tower_id and floor.floor_number in p.completed_floors])
                
                floor_stats[floor.floor_number] = {
                    "completed_count": completed_count,
                    "completion_rate": completed_count / total_players if total_players > 0 else 0,
                    "average_score": sum(p.best_scores.get(floor.floor_number, 0) 
                                       for p in self.tower_progress.values() 
                                       if p.tower_id == tower_id) / completed_count if completed_count > 0 else 0
                }
        
        return {
            "tower_id": tower_id,
            "tower_type": tower.tower_type.value,
            "total_floors": sum(len(level.floors) for level in tower.levels),
            "total_levels": len(tower.levels),
            "total_players": total_players,
            "completed_players": completed_players,
            "completion_rate": completed_players / total_players if total_players > 0 else 0,
            "floor_statistics": floor_stats,
            "created_at": tower.created_at
        }
    
    def add_floor_completed_callback(self, callback: callable):
        """Добавление callback для завершения этажа"""
        self.floor_completed_callbacks.append(callback)
    
    def add_level_completed_callback(self, callback: callable):
        """Добавление callback для завершения уровня"""
        self.level_completed_callbacks.append(callback)
    
    def add_tower_completed_callback(self, callback: callable):
        """Добавление callback для завершения башни"""
        self.tower_completed_callbacks.append(callback)
    
    def _notify_floor_completed(self, tower_id: str, character_id: str, floor_number: int, 
                               score: int, completion_time: float):
        """Уведомление о завершении этажа"""
        for callback in self.floor_completed_callbacks:
            try:
                callback(tower_id, character_id, floor_number, score, completion_time)
            except Exception as e:
                self.logger.error(f"Ошибка в callback завершения этажа: {e}")
    
    def _notify_level_completed(self, tower_id: str, character_id: str, level_number: int):
        """Уведомление о завершении уровня"""
        for callback in self.level_completed_callbacks:
            try:
                callback(tower_id, character_id, level_number)
            except Exception as e:
                self.logger.error(f"Ошибка в callback завершения уровня: {e}")
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Получение статистики генерации"""
        return self.generation_stats.copy()
    
    def clear_cache(self):
        """Очистка кэша"""
        self.tower_cache.clear()
        self.logger.info("Кэш TowerSystem очищен")
    
    def _on_destroy(self):
        """Уничтожение системы башен"""
        self.generated_towers.clear()
        self.tower_progress.clear()
        self.tower_cache.clear()
        self.floor_completed_callbacks.clear()
        self.level_completed_callbacks.clear()
        self.tower_completed_callbacks.clear()
        
        self.logger.info("TowerSystem уничтожен")
