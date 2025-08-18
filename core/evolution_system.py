"""
Система эволюционных циклов с наследованием характеристик и эволюционными бонусами.
Управляет переходами между циклами и развитием персонажа.
"""

import random
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

from .effect_system import EffectCode, EffectDatabase
from .genetic_system import AdvancedGeneticSystem
from .content_generator import ContentGenerator, GeneratedWorld

logger = logging.getLogger(__name__)


class EvolutionStage(Enum):
    """Стадии эволюции"""
    BEGINNING = "beginning"
    GROWTH = "growth"
    MATURATION = "maturation"
    TRANSFORMATION = "transformation"
    TRANSCENDENCE = "transcendence"


class EvolutionBonus(Enum):
    """Типы эволюционных бонусов"""
    GENE_SLOTS = "gene_slots"
    MUTATION_RESISTANCE = "mutation_resistance"
    STARTING_EFFECTS = "starting_effects"
    STAT_BOOSTS = "stat_boosts"
    ABILITY_UNLOCKS = "ability_unlocks"
    COSMIC_INSIGHT = "cosmic_insight"


@dataclass
class EvolutionData:
    """Данные эволюции"""
    cycle_number: int
    completion_time: float
    achievements: List[str]
    genes_unlocked: List[str]
    enemies_defeated: int
    exploration_percent: float
    genetic_stability: float
    emotional_balance: float
    ai_performance: float
    world_seed: int
    world_name: str


@dataclass
class EvolutionBonus:
    """Эволюционный бонус"""
    bonus_type: str
    value: Any
    description: str
    requirements: Dict[str, Any]
    is_permanent: bool = True


@dataclass
class EvolutionPath:
    """Путь эволюции"""
    id: str
    name: str
    description: str
    stages: List[EvolutionStage]
    requirements: Dict[str, Any]
    rewards: List[EvolutionBonus]
    is_completed: bool = False


class EvolutionCycleSystem:
    """Система эволюционных циклов"""
    
    def __init__(self, effect_db: EffectDatabase):
        self.effect_db = effect_db
        self.current_cycle = 1
        self.total_cycles = 0
        self.evolution_history: List[EvolutionData] = []
        self.available_bonuses: List[EvolutionBonus] = []
        self.evolution_paths: List[EvolutionPath] = []
        
        # Инициализация эволюционных путей
        self._init_evolution_paths()
        
        # Инициализация доступных бонусов
        self._init_evolution_bonuses()
        
        logger.info("Система эволюционных циклов инициализирована")
    
    def _init_evolution_paths(self):
        """Инициализация путей эволюции"""
        self.evolution_paths = [
            EvolutionPath(
                id="PATH_001",
                name="Генетический Мастер",
                description="Путь генетического совершенства",
                stages=[
                    EvolutionStage.BEGINNING,
                    EvolutionStage.GROWTH,
                    EvolutionStage.MATURATION,
                    EvolutionStage.TRANSFORMATION,
                    EvolutionStage.TRANSCENDENCE
                ],
                requirements={
                    "genes_unlocked": 20,
                    "genetic_stability": 0.8,
                    "cycles_completed": 5
                },
                rewards=[
                    EvolutionBonus("gene_slots", 3, "Дополнительные слоты для генов", {}),
                    EvolutionBonus("mutation_resistance", 0.3, "Повышенная устойчивость к мутациям", {}),
                    EvolutionBonus("cosmic_insight", "genetic_mastery", "Мастерство генетической инженерии", {})
                ]
            ),
            EvolutionPath(
                id="PATH_002",
                name="Эмоциональный Мудрец",
                description="Путь эмоционального просветления",
                stages=[
                    EvolutionStage.BEGINNING,
                    EvolutionStage.GROWTH,
                    EvolutionStage.MATURATION
                ],
                requirements={
                    "emotional_balance": 0.9,
                    "cycles_completed": 3,
                    "dialogue_success_rate": 0.8
                },
                rewards=[
                    EvolutionBonus("emotional_stability", 0.5, "Повышенная эмоциональная стабильность", {}),
                    EvolutionBonus("dialogue_mastery", "emotional_insight", "Интуитивное понимание эмоций", {}),
                    EvolutionBonus("starting_effects", ["EMO_103", "EMO_104"], "Стартовые эмоциональные эффекты", {})
                ]
            ),
            EvolutionPath(
                id="PATH_003",
                name="ИИ Синергетик",
                description="Путь слияния с искусственным интеллектом",
                stages=[
                    EvolutionStage.BEGINNING,
                    EvolutionStage.GROWTH,
                    EvolutionStage.TRANSFORMATION
                ],
                requirements={
                    "ai_performance": 0.9,
                    "cycles_completed": 4,
                    "ai_adaptation_level": 0.8
                },
                rewards=[
                    EvolutionBonus("ai_synergy", 0.4, "Синергия с ИИ", {}),
                    EvolutionBonus("learning_acceleration", 2.0, "Ускоренное обучение", {}),
                    EvolutionBonus("cosmic_insight", "ai_transcendence", "Трансцендентное понимание ИИ", {})
                ]
            )
        ]
    
    def _init_evolution_bonuses(self):
        """Инициализация эволюционных бонусов"""
        self.available_bonuses = [
            EvolutionBonus("gene_slots", 1, "Дополнительный слот для генов", {"cycles_completed": 1}),
            EvolutionBonus("mutation_resistance", 0.1, "Устойчивость к мутациям", {"cycles_completed": 2}),
            EvolutionBonus("starting_effects", ["GENE_001"], "Стартовый ген", {"cycles_completed": 1}),
            EvolutionBonus("stat_boosts", {"health": 20, "stamina": 15}, "Улучшение характеристик", {"cycles_completed": 1}),
            EvolutionBonus("ability_unlocks", "genetic_manipulation", "Манипуляция генами", {"cycles_completed": 3}),
            EvolutionBonus("cosmic_insight", "evolution_understanding", "Понимание эволюции", {"cycles_completed": 5})
        ]
    
    def complete_cycle(self, player, world) -> Dict[str, Any]:
        """Завершение эволюционного цикла"""
        try:
            # Сбор данных о завершённом цикле
            cycle_data = self._collect_cycle_data(player, world)
            
            # Расчёт эволюционных бонусов
            bonuses = self._calculate_evolution_bonuses(cycle_data)
            
            # Проверка достижения новых путей эволюции
            new_paths = self._check_new_evolution_paths(cycle_data)
            
            # Запись в историю
            evolution_data = EvolutionData(
                cycle_number=self.current_cycle,
                completion_time=cycle_data.get("completion_time", 0.0),
                achievements=cycle_data.get("achievements", []),
                genes_unlocked=cycle_data.get("genes_unlocked", []),
                enemies_defeated=cycle_data.get("enemies_defeated", 0),
                exploration_percent=cycle_data.get("exploration_percent", 0.0),
                genetic_stability=cycle_data.get("genetic_stability", 0.0),
                emotional_balance=cycle_data.get("emotional_balance", 0.0),
                ai_performance=cycle_data.get("ai_performance", 0.0),
                world_seed=cycle_data.get("world_seed", 0),
                world_name=cycle_data.get("world_name", "Unknown")
            )
            
            self.evolution_history.append(evolution_data)
            
            # Увеличение счётчика циклов
            self.current_cycle += 1
            self.total_cycles += 1
            
            result = {
                "cycle_completed": True,
                "cycle_number": self.current_cycle - 1,
                "bonuses": bonuses,
                "new_paths": new_paths,
                "evolution_data": evolution_data
            }
            
            logger.info(f"Эволюционный цикл {self.current_cycle - 1} завершён")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка завершения эволюционного цикла: {e}")
            return {"cycle_completed": False, "error": str(e)}
    
    def _collect_cycle_data(self, player, world) -> Dict[str, Any]:
        """Сбор данных о завершённом цикле"""
        cycle_data = {}
        
        try:
            # Время завершения
            cycle_data["completion_time"] = getattr(player, 'play_time', 0.0)
            
            # Достижения
            cycle_data["achievements"] = getattr(player, 'achievements', [])
            
            # Генетические данные
            if hasattr(player, 'genetic_system'):
                cycle_data["genes_unlocked"] = player.genetic_system.unlocked_genes
                cycle_data["genetic_stability"] = player.genetic_system.get_gene_stability("overall")
            
            # Статистика боя
            cycle_data["enemies_defeated"] = getattr(player, 'enemies_defeated', 0)
            
            # Процент исследования
            cycle_data["exploration_percent"] = self._calculate_exploration_percent(world)
            
            # Эмоциональный баланс
            if hasattr(player, 'emotion_system'):
                cycle_data["emotional_balance"] = player.emotion_system.current_state.get_emotional_balance()
            
            # Производительность ИИ
            if hasattr(player, 'ai_system'):
                cycle_data["ai_performance"] = player.ai_system._calculate_performance()
            
            # Данные мира
            cycle_data["world_seed"] = getattr(world, 'seed', 0)
            cycle_data["world_name"] = getattr(world, 'name', "Unknown")
            
        except Exception as e:
            logger.error(f"Ошибка сбора данных цикла: {e}")
            cycle_data = {}
        
        return cycle_data
    
    def _calculate_exploration_percent(self, world) -> float:
        """Расчёт процента исследования мира"""
        try:
            if hasattr(world, 'explored_areas') and hasattr(world, 'total_areas'):
                return world.explored_areas / world.total_areas
            elif hasattr(world, 'explored_percent'):
                return world.explored_percent
            else:
                return random.uniform(0.3, 0.8)  # Случайное значение по умолчанию
        except:
            return 0.5
    
    def _calculate_evolution_bonuses(self, cycle_data: Dict[str, Any]) -> List[EvolutionBonus]:
        """Расчёт эволюционных бонусов"""
        bonuses = []
        
        try:
            # Базовые бонусы за завершение цикла
            base_bonuses = [
                EvolutionBonus("gene_slots", 1, "Базовый слот для генов", {}),
                EvolutionBonus("mutation_resistance", 0.05, "Базовая устойчивость к мутациям", {})
            ]
            
            bonuses.extend(base_bonuses)
            
            # Бонусы за достижения
            if cycle_data.get("enemies_defeated", 0) > 50:
                bonuses.append(EvolutionBonus("stat_boosts", {"damage": 10}, "Боевой опыт", {}))
            
            if cycle_data.get("exploration_percent", 0.0) > 0.8:
                bonuses.append(EvolutionBonus("starting_effects", ["EXPLORATION_BOOST"], "Знание местности", {}))
            
            if cycle_data.get("genetic_stability", 0.0) > 0.8:
                bonuses.append(EvolutionBonus("mutation_resistance", 0.1, "Генетическая стабильность", {}))
            
            if cycle_data.get("emotional_balance", 0.0) > 0.7:
                bonuses.append(EvolutionBonus("emotional_stability", 0.2, "Эмоциональное равновесие", {}))
            
            # Бонусы за количество циклов
            cycle_bonuses = self._get_cycle_bonuses(self.total_cycles + 1)
            bonuses.extend(cycle_bonuses)
            
        except Exception as e:
            logger.error(f"Ошибка расчёта эволюционных бонусов: {e}")
        
        return bonuses
    
    def _get_cycle_bonuses(self, cycle_number: int) -> List[EvolutionBonus]:
        """Получение бонусов за количество циклов"""
        bonuses = []
        
        if cycle_number >= 5:
            bonuses.append(EvolutionBonus("cosmic_insight", "evolution_mastery", "Мастерство эволюции", {}))
        
        if cycle_number >= 10:
            bonuses.append(EvolutionBonus("gene_slots", 2, "Дополнительные слоты для генов", {}))
        
        if cycle_number >= 15:
            bonuses.append(EvolutionBonus("mutation_resistance", 0.2, "Высокая устойчивость к мутациям", {}))
        
        if cycle_number >= 20:
            bonuses.append(EvolutionBonus("cosmic_insight", "transcendence", "Трансцендентность", {}))
        
        return bonuses
    
    def _check_new_evolution_paths(self, cycle_data: Dict[str, Any]) -> List[str]:
        """Проверка новых путей эволюции"""
        new_paths = []
        
        for path in self.evolution_paths:
            if not path.is_completed and self._check_path_requirements(path, cycle_data):
                path.is_completed = True
                new_paths.append(path.id)
                logger.info(f"Открыт новый путь эволюции: {path.name}")
        
        return new_paths
    
    def _check_path_requirements(self, path: EvolutionPath, cycle_data: Dict[str, Any]) -> bool:
        """Проверка требований пути эволюции"""
        try:
            for requirement, value in path.requirements.items():
                if requirement == "genes_unlocked":
                    if len(cycle_data.get("genes_unlocked", [])) < value:
                        return False
                elif requirement == "genetic_stability":
                    if cycle_data.get("genetic_stability", 0.0) < value:
                        return False
                elif requirement == "cycles_completed":
                    if self.total_cycles < value:
                        return False
                elif requirement == "emotional_balance":
                    if cycle_data.get("emotional_balance", 0.0) < value:
                        return False
                elif requirement == "dialogue_success_rate":
                    # Здесь должна быть логика проверки успешности диалогов
                    pass
                elif requirement == "ai_performance":
                    if cycle_data.get("ai_performance", 0.0) < value:
                        return False
                elif requirement == "ai_adaptation_level":
                    # Здесь должна быть логика проверки уровня адаптации ИИ
                    pass
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки требований пути: {e}")
            return False
    
    def start_new_cycle(self, player, previous_cycle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Начало нового эволюционного цикла"""
        try:
            # Генерация нового мира
            content_generator = ContentGenerator(seed=random.randint(1, 999999))
            new_world = content_generator.generate_world()
            
            # Создание потомка игрока
            new_player = self._create_offspring(player, previous_cycle_data)
            
            # Применение эволюционных бонусов
            self._apply_evolution_bonuses(new_player, previous_cycle_data.get("bonuses", []))
            
            # Обновление эволюционных путей
            self._update_evolution_paths(new_player)
            
            result = {
                "world": new_world,
                "player": new_player,
                "cycle_number": self.current_cycle,
                "seed": new_world.seed
            }
            
            logger.info(f"Начат новый эволюционный цикл {self.current_cycle}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка начала нового цикла: {e}")
            raise
    
    def _create_offspring(self, parent_player, cycle_data: Dict[str, Any]):
        """Создание потомка игрока"""
        try:
            # Создание нового игрока с наследуемыми характеристиками
            offspring = type(parent_player)()  # Создание экземпляра того же класса
            
            # Наследование базовых характеристик
            if hasattr(parent_player, 'base_stats'):
                offspring.base_stats = parent_player.base_stats.copy()
                # Небольшие случайные изменения
                for stat in offspring.base_stats:
                    if random.random() < 0.3:  # 30% шанс изменения
                        change = random.uniform(-0.1, 0.1)
                        offspring.base_stats[stat] = max(1, offspring.base_stats[stat] * (1 + change))
            
            # Наследование генетических данных
            if hasattr(parent_player, 'genetic_system') and hasattr(offspring, 'genetic_system'):
                offspring.genetic_system.unlocked_genes = parent_player.genetic_system.unlocked_genes.copy()
                offspring.genetic_system.generation = parent_player.genetic_system.generation + 1
            
            # Наследование опыта и знаний
            if hasattr(parent_player, 'experience'):
                offspring.experience = int(parent_player.experience * 0.1)  # 10% от опыта родителя
            
            # Сброс временных характеристик
            if hasattr(offspring, 'current_health'):
                offspring.current_health = offspring.base_stats.get('health', 100)
            
            if hasattr(offspring, 'current_stamina'):
                offspring.current_stamina = offspring.base_stats.get('stamina', 100)
            
            logger.info("Создан потомок игрока с наследуемыми характеристиками")
            return offspring
            
        except Exception as e:
            logger.error(f"Ошибка создания потомка: {e}")
            # Возврат копии родителя в случае ошибки
            return parent_player
    
    def _apply_evolution_bonuses(self, player, bonuses: List[EvolutionBonus]):
        """Применение эволюционных бонусов"""
        try:
            for bonus in bonuses:
                if bonus.bonus_type == "gene_slots":
                    if hasattr(player, 'genetic_system'):
                        player.genetic_system.gene_slots += bonus.value
                
                elif bonus.bonus_type == "mutation_resistance":
                    if hasattr(player, 'genetic_system'):
                        player.genetic_system.mutation_resistance += bonus.value
                
                elif bonus.bonus_type == "starting_effects":
                    if hasattr(player, 'effect_system'):
                        for effect_code in bonus.value:
                            player.effect_system.apply_effect(effect_code, "evolution_bonus")
                
                elif bonus.bonus_type == "stat_boosts":
                    if hasattr(player, 'base_stats'):
                        for stat, boost in bonus.value.items():
                            if stat in player.base_stats:
                                player.base_stats[stat] += boost
                
                elif bonus.bonus_type == "ability_unlocks":
                    if hasattr(player, 'abilities'):
                        player.abilities.append(bonus.value)
                
                elif bonus.bonus_type == "cosmic_insight":
                    if hasattr(player, 'cosmic_knowledge'):
                        player.cosmic_knowledge.append(bonus.value)
                
                logger.info(f"Применён эволюционный бонус: {bonus.description}")
                
        except Exception as e:
            logger.error(f"Ошибка применения эволюционных бонусов: {e}")
    
    def _update_evolution_paths(self, player):
        """Обновление путей эволюции"""
        try:
            for path in self.evolution_paths:
                if not path.is_completed:
                    # Проверка прогресса по пути
                    progress = self._calculate_path_progress(path, player)
                    if progress > 0.8:  # 80% прогресса
                        logger.info(f"Прогресс по пути эволюции {path.name}: {progress:.1%}")
                        
        except Exception as e:
            logger.error(f"Ошибка обновления путей эволюции: {e}")
    
    def _calculate_path_progress(self, path: EvolutionPath, player) -> float:
        """Расчёт прогресса по пути эволюции"""
        try:
            total_requirements = len(path.requirements)
            met_requirements = 0
            
            for requirement, value in path.requirements.items():
                if self._check_single_requirement(requirement, value, player):
                    met_requirements += 1
            
            return met_requirements / total_requirements if total_requirements > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Ошибка расчёта прогресса пути: {e}")
            return 0.0
    
    def _check_single_requirement(self, requirement: str, value: Any, player) -> bool:
        """Проверка отдельного требования"""
        try:
            if requirement == "genes_unlocked":
                return len(player.genetic_system.unlocked_genes) >= value
            elif requirement == "genetic_stability":
                return player.genetic_system.get_gene_stability("overall") >= value
            elif requirement == "emotional_balance":
                return player.emotion_system.current_state.get_emotional_balance() >= value
            elif requirement == "ai_performance":
                return player.ai_system._calculate_performance() >= value
            else:
                return False
                
        except Exception as e:
            logger.error(f"Ошибка проверки требования {requirement}: {e}")
            return False
    
    def get_evolution_summary(self) -> Dict[str, Any]:
        """Получение сводки по эволюции"""
        try:
            summary = {
                "total_cycles": self.total_cycles,
                "current_cycle": self.current_cycle,
                "evolution_paths": [path.name for path in self.evolution_paths if path.is_completed],
                "total_bonuses": len(self.available_bonuses),
                "evolution_history": []
            }
            
            # Сводка по последним циклам
            for evolution_data in self.evolution_history[-5:]:  # Последние 5 циклов
                summary["evolution_history"].append({
                    "cycle": evolution_data.cycle_number,
                    "world": evolution_data.world_name,
                    "achievements": len(evolution_data.achievements),
                    "genes_unlocked": len(evolution_data.genes_unlocked),
                    "enemies_defeated": evolution_data.enemies_defeated,
                    "exploration": f"{evolution_data.exploration_percent:.1%}"
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Ошибка получения сводки по эволюции: {e}")
            return {}
    
    def save_evolution_state(self, filepath: str) -> bool:
        """Сохранение состояния эволюции"""
        try:
            evolution_state = {
                "current_cycle": self.current_cycle,
                "total_cycles": self.total_cycles,
                "evolution_history": [
                    {
                        "cycle_number": data.cycle_number,
                        "completion_time": data.completion_time,
                        "achievements": data.achievements,
                        "genes_unlocked": data.genes_unlocked,
                        "enemies_defeated": data.enemies_defeated,
                        "exploration_percent": data.exploration_percent,
                        "genetic_stability": data.genetic_stability,
                        "emotional_balance": data.emotional_balance,
                        "ai_performance": data.ai_performance,
                        "world_seed": data.world_seed,
                        "world_name": data.world_name
                    }
                    for data in self.evolution_history
                ],
                "evolution_paths": [
                    {
                        "id": path.id,
                        "name": path.name,
                        "is_completed": path.is_completed
                    }
                    for path in self.evolution_paths
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(evolution_state, f, indent=2)
            
            logger.info(f"Состояние эволюции сохранено в {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения состояния эволюции: {e}")
            return False
    
    def load_evolution_state(self, filepath: str) -> bool:
        """Загрузка состояния эволюции"""
        try:
            with open(filepath, 'r') as f:
                evolution_state = json.load(f)
            
            # Восстановление состояния
            self.current_cycle = evolution_state.get("current_cycle", 1)
            self.total_cycles = evolution_state.get("total_cycles", 0)
            
            # Восстановление истории эволюции
            self.evolution_history.clear()
            for data in evolution_state.get("evolution_history", []):
                evolution_data = EvolutionData(
                    cycle_number=data["cycle_number"],
                    completion_time=data["completion_time"],
                    achievements=data["achievements"],
                    genes_unlocked=data["genes_unlocked"],
                    enemies_defeated=data["enemies_defeated"],
                    exploration_percent=data["exploration_percent"],
                    genetic_stability=data["genetic_stability"],
                    emotional_balance=data["emotional_balance"],
                    ai_performance=data["ai_performance"],
                    world_seed=data["world_seed"],
                    world_name=data["world_name"]
                )
                self.evolution_history.append(evolution_data)
            
            # Восстановление путей эволюции
            for path_data in evolution_state.get("evolution_paths", []):
                for path in self.evolution_paths:
                    if path.id == path_data["id"]:
                        path.is_completed = path_data["is_completed"]
                        break
            
            logger.info(f"Состояние эволюции загружено из {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки состояния эволюции: {e}")
            return False
    
    def reset_evolution(self):
        """Сброс системы эволюции"""
        try:
            self.current_cycle = 1
            self.total_cycles = 0
            self.evolution_history.clear()
            
            for path in self.evolution_paths:
                path.is_completed = False
            
            logger.info("Система эволюции сброшена")
            
        except Exception as e:
            logger.error(f"Ошибка сброса системы эволюции: {e}")
    
    def get_available_bonuses(self) -> List[EvolutionBonus]:
        """Получение доступных бонусов"""
        return self.available_bonuses.copy()
    
    def add_custom_bonus(self, bonus: EvolutionBonus):
        """Добавление пользовательского бонуса"""
        self.available_bonuses.append(bonus)
        logger.info(f"Добавлен пользовательский бонус: {bonus.description}")
    
    def get_evolution_paths(self) -> List[EvolutionPath]:
        """Получение путей эволюции"""
        return self.evolution_paths.copy()
