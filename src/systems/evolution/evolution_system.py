#!/usr/bin/env python3
"""
Система эволюции и мутаций AI-EVOLVE
Генетические алгоритмы для развития персонажей
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
import random
import math
import time
from src.core.architecture import BaseComponent, ComponentType, Priority, Event, create_event


# ============================================================================
# ОСНОВНЫЕ ТИПЫ И ПЕРЕЧИСЛЕНИЯ
# ============================================================================

class GeneType(Enum):
    """Типы генов"""
    PHYSICAL = "physical"      # Физические характеристики
    MENTAL = "mental"          # Умственные способности
    SOCIAL = "social"          # Социальные навыки
    SPECIAL = "special"        # Специальные способности
    COMBAT = "combat"          # Боевые навыки
    MAGIC = "magic"            # Магические способности

class MutationType(Enum):
    """Типы мутаций"""
    SPONTANEOUS = "spontaneous"    # Спонтанные
    INDUCED = "induced"            # Индуцированные
    ADAPTIVE = "adaptive"          # Адаптивные
    COMBINATIONAL = "combinational" # Комбинационные
    CASCADE = "cascade"            # Каскадные

class EvolutionPath(Enum):
    """Пути эволюции"""
    PHYSICAL_STRENGTH = "physical_strength"     # Физическая сила
    PHYSICAL_AGILITY = "physical_agility"       # Физическая ловкость
    PHYSICAL_ENDURANCE = "physical_endurance"   # Физическая выносливость
    MENTAL_INTELLIGENCE = "mental_intelligence" # Умственная интеллектуальность
    MENTAL_WISDOM = "mental_wisdom"             # Умственная мудрость
    MENTAL_CHARISMA = "mental_charisma"         # Умственная харизма
    SOCIAL_LEADERSHIP = "social_leadership"     # Социальное лидерство
    SOCIAL_DIPLOMACY = "social_diplomacy"       # Социальная дипломатия
    SPECIAL_TECHNOLOGY = "special_technology"   # Специальные технологии
    COMBAT_MELEE = "combat_melee"               # Ближний бой
    COMBAT_RANGED = "combat_ranged"             # Дальний бой
    MAGIC_ELEMENTAL = "magic_elemental"         # Стихийная магия
    MAGIC_ILLUSION = "magic_illusion"           # Иллюзорная магия

class EvolutionStage(Enum):
    """Стадии эволюции"""
    BASIC = "basic"           # Базовая
    ENHANCED = "enhanced"     # Улучшенная
    ADVANCED = "advanced"     # Продвинутая
    MASTER = "master"         # Мастерская
    LEGENDARY = "legendary"   # Легендарная
    MYTHICAL = "mythical"     # Мифическая


# ============================================================================
# ДАТАКЛАССЫ И СТРУКТУРЫ ДАННЫХ
# ============================================================================

@dataclass
class Gene:
    """Ген - базовая единица эволюции"""
    gene_id: str
    gene_type: GeneType
    name: str
    description: str
    base_value: float
    current_value: float
    max_value: float
    mutation_chance: float
    evolution_cost: int
    requirements: List[str] = field(default_factory=list)
    effects: Dict[str, float] = field(default_factory=dict)
    visual_effects: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.current_value is None:
            self.current_value = self.base_value

@dataclass
class Mutation:
    """Мутация - изменение гена"""
    mutation_id: str
    gene_id: str
    mutation_type: MutationType
    name: str
    description: str
    value_change: float
    duration: Optional[float] = None  # None = постоянная
    trigger_conditions: List[str] = field(default_factory=list)
    visual_effects: List[str] = field(default_factory=list)
    side_effects: Dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class EvolutionTree:
    """Дерево эволюции - путь развития"""
    tree_id: str
    name: str
    description: str
    gene_type: GeneType
    stages: List[EvolutionStage]
    requirements: Dict[EvolutionStage, List[str]] = field(default_factory=dict)
    rewards: Dict[EvolutionStage, Dict[str, Any]] = field(default_factory=dict)
    visual_representation: str = ""

@dataclass
class EvolutionProgress:
    """Прогресс эволюции персонажа"""
    character_id: str
    evolution_points: int
    current_stage: EvolutionStage
    completed_paths: List[str] = field(default_factory=list)
    active_mutations: List[str] = field(default_factory=list)
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)
    last_evolution: float = 0.0

@dataclass
class GeneticCombination:
    """Генетическая комбинация - взаимодействие генов"""
    combination_id: str
    name: str
    description: str
    required_genes: List[str]
    effects: Dict[str, float]
    visual_effects: List[str]
    activation_chance: float
    duration: Optional[float] = None


# ============================================================================
# ОСНОВНАЯ СИСТЕМА ЭВОЛЮЦИИ
# ============================================================================

class EvolutionSystem(BaseComponent):
    """
    Основная система эволюции и мутаций
    Управляет развитием персонажей через генетические алгоритмы
    """
    
    def __init__(self):
        super().__init__(
            component_id="EvolutionSystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Основные данные
        self.genes_registry: Dict[str, Gene] = {}
        self.mutations_registry: Dict[str, Mutation] = {}
        self.evolution_trees: Dict[str, EvolutionTree] = {}
        self.character_progress: Dict[str, EvolutionProgress] = {}
        self.genetic_combinations: Dict[str, GeneticCombination] = {}
        
        # Системные параметры
        self.mutation_rate = 0.01
        self.evolution_cost_multiplier = 1.0
        self.max_mutations_per_gene = 5
        self.cascade_mutation_chance = 0.1
        
        # Обработчики событий
        self.mutation_handlers: Dict[str, List[Callable]] = {}
        self.evolution_handlers: Dict[str, List[Callable]] = {}
        
    def _on_initialize(self) -> bool:
        """Инициализация системы эволюции"""
        try:
            self._logger.info("Инициализация системы эволюции...")
            
            # Создаем базовые гены
            self._create_base_genes()
            
            # Создаем эволюционные деревья
            self._create_evolution_trees()
            
            # Создаем генетические комбинации
            self._create_genetic_combinations()
            
            # Регистрируем обработчики событий
            self._register_event_handlers()
            
            self._logger.info("Система эволюции инициализирована успешно")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка инициализации системы эволюции: {e}")
            return False
    
    def _create_base_genes(self):
        """Создание базовых генов для всех типов"""
        try:
            # Физические гены
            self._add_gene(Gene(
                gene_id="gene_strength",
                gene_type=GeneType.PHYSICAL,
                name="Ген силы",
                description="Определяет физическую силу персонажа",
                base_value=10.0,
                current_value=10.0,
                max_value=100.0,
                mutation_chance=0.05,
                evolution_cost=10,
                effects={"damage": 1.0, "carry_weight": 2.0}
            ))
            
            self._add_gene(Gene(
                gene_id="gene_agility",
                gene_type=GeneType.PHYSICAL,
                name="Ген ловкости",
                description="Определяет физическую ловкость персонажа",
                base_value=10.0,
                current_value=10.0,
                max_value=100.0,
                mutation_chance=0.05,
                evolution_cost=10,
                effects={"dodge_chance": 0.5, "movement_speed": 1.0}
            ))
            
            # Умственные гены
            self._add_gene(Gene(
                gene_id="gene_intelligence",
                gene_type=GeneType.MENTAL,
                name="Ген интеллекта",
                description="Определяет умственные способности персонажа",
                base_value=10.0,
                current_value=10.0,
                max_value=100.0,
                mutation_chance=0.03,
                evolution_cost=15,
                effects={"magic_power": 1.5, "skill_learning": 2.0}
            ))
            
            # Социальные гены
            self._add_gene(Gene(
                gene_id="gene_charisma",
                gene_type=GeneType.SOCIAL,
                name="Ген харизмы",
                description="Определяет социальные навыки персонажа",
                base_value=10.0,
                current_value=10.0,
                max_value=100.0,
                mutation_chance=0.04,
                evolution_cost=12,
                effects={"persuasion": 1.0, "leadership": 1.5}
            ))
            
            # Боевые гены
            self._add_gene(Gene(
                gene_id="gene_combat_instinct",
                gene_type=GeneType.COMBAT,
                name="Ген боевого инстинкта",
                description="Определяет боевые способности персонажа",
                base_value=10.0,
                current_value=10.0,
                max_value=100.0,
                mutation_chance=0.06,
                evolution_cost=8,
                effects={"critical_chance": 0.3, "initiative": 1.0}
            ))
            
            # Магические гены
            self._add_gene(Gene(
                gene_id="gene_magic_affinity",
                gene_type=GeneType.MAGIC,
                name="Ген магической склонности",
                description="Определяет магические способности персонажа",
                base_value=10.0,
                current_value=10.0,
                max_value=100.0,
                mutation_chance=0.02,
                evolution_cost=20,
                effects={"magic_resistance": 1.0, "spell_power": 2.0}
            ))
            
            self._logger.info(f"Создано {len(self.genes_registry)} базовых генов")
            
        except Exception as e:
            self._logger.error(f"Ошибка создания базовых генов: {e}")
            raise
    
    def _create_evolution_trees(self):
        """Создание эволюционных деревьев"""
        try:
            # Дерево физической силы
            self._add_evolution_tree(EvolutionTree(
                tree_id="tree_physical_strength",
                name="Дерево физической силы",
                description="Путь развития физической силы и мощи",
                gene_type=GeneType.PHYSICAL,
                stages=[EvolutionStage.BASIC, EvolutionStage.ENHANCED, 
                       EvolutionStage.ADVANCED, EvolutionStage.MASTER,
                       EvolutionStage.LEGENDARY, EvolutionStage.MYTHICAL],
                requirements={
                    EvolutionStage.ENHANCED: ["gene_strength:20"],
                    EvolutionStage.ADVANCED: ["gene_strength:40", "evolution_points:50"],
                    EvolutionStage.MASTER: ["gene_strength:60", "evolution_points:100"],
                    EvolutionStage.LEGENDARY: ["gene_strength:80", "evolution_points:200"],
                    EvolutionStage.MYTHICAL: ["gene_strength:95", "evolution_points:500"]
                },
                rewards={
                    EvolutionStage.ENHANCED: {"damage_bonus": 2.0, "health_bonus": 50},
                    EvolutionStage.ADVANCED: {"damage_bonus": 4.0, "health_bonus": 100},
                    EvolutionStage.MASTER: {"damage_bonus": 8.0, "health_bonus": 200},
                    EvolutionStage.LEGENDARY: {"damage_bonus": 16.0, "health_bonus": 500},
                    EvolutionStage.MYTHICAL: {"damage_bonus": 32.0, "health_bonus": 1000}
                }
            ))
            
            # Дерево магической склонности
            self._add_evolution_tree(EvolutionTree(
                tree_id="tree_magic_affinity",
                name="Дерево магической склонности",
                description="Путь развития магических способностей",
                gene_type=GeneType.MAGIC,
                stages=[EvolutionStage.BASIC, EvolutionStage.ENHANCED, 
                       EvolutionStage.ADVANCED, EvolutionStage.MASTER,
                       EvolutionStage.LEGENDARY, EvolutionStage.MYTHICAL],
                requirements={
                    EvolutionStage.ENHANCED: ["gene_magic_affinity:20"],
                    EvolutionStage.ADVANCED: ["gene_magic_affinity:40", "evolution_points:60"],
                    EvolutionStage.MASTER: ["gene_magic_affinity:60", "evolution_points:120"],
                    EvolutionStage.LEGENDARY: ["gene_magic_affinity:80", "evolution_points:250"],
                    EvolutionStage.MYTHICAL: ["gene_magic_affinity:95", "evolution_points:600"]
                },
                rewards={
                    EvolutionStage.ENHANCED: {"spell_power_bonus": 2.0, "mana_bonus": 50},
                    EvolutionStage.ADVANCED: {"spell_power_bonus": 4.0, "mana_bonus": 100},
                    EvolutionStage.MASTER: {"spell_power_bonus": 8.0, "mana_bonus": 200},
                    EvolutionStage.LEGENDARY: {"spell_power_bonus": 16.0, "mana_bonus": 500},
                    EvolutionStage.MYTHICAL: {"spell_power_bonus": 32.0, "mana_bonus": 1000}
                }
            ))
            
            self._logger.info(f"Создано {len(self.evolution_trees)} эволюционных деревьев")
            
        except Exception as e:
            self._logger.error(f"Ошибка создания эволюционных деревьев: {e}")
            raise
    
    def _create_genetic_combinations(self):
        """Создание генетических комбинаций"""
        try:
            # Комбинация силы и ловкости
            self._add_genetic_combination(GeneticCombination(
                combination_id="combo_strength_agility",
                name="Комбинация силы и ловкости",
                description="Синергия между физической силой и ловкостью",
                required_genes=["gene_strength", "gene_agility"],
                effects={"damage": 1.5, "critical_chance": 0.2, "dodge_chance": 0.3},
                visual_effects=["muscle_definition", "graceful_movement"],
                activation_chance=0.3
            ))
            
            # Комбинация интеллекта и магической склонности
            self._add_genetic_combination(GeneticCombination(
                combination_id="combo_intelligence_magic",
                name="Комбинация интеллекта и магии",
                description="Синергия между интеллектом и магическими способностями",
                required_genes=["gene_intelligence", "gene_magic_affinity"],
                effects={"spell_power": 2.0, "magic_resistance": 1.5, "mana_regeneration": 2.0},
                visual_effects=["magical_aura", "intelligent_eyes"],
                activation_chance=0.25
            ))
            
            self._logger.info(f"Создано {len(self.genetic_combinations)} генетических комбинаций")
            
        except Exception as e:
            self._logger.error(f"Ошибка создания генетических комбинаций: {e}")
            raise
    
    def _register_event_handlers(self):
        """Регистрация обработчиков событий"""
        try:
            # Обработчики мутаций
            self.mutation_handlers["mutation_triggered"] = []
            self.mutation_handlers["mutation_expired"] = []
            self.mutation_handlers["cascade_mutation"] = []
            
            # Обработчики эволюции
            self.evolution_handlers["evolution_completed"] = []
            self.evolution_handlers["evolution_failed"] = []
            self.evolution_handlers["stage_unlocked"] = []
            
            self._logger.info("Обработчики событий зарегистрированы")
            
        except Exception as e:
            self._logger.error(f"Ошибка регистрации обработчиков событий: {e}")
            raise
    
    def _add_gene(self, gene: Gene):
        """Добавление гена в реестр"""
        self.genes_registry[gene.gene_id] = gene
    
    def _add_evolution_tree(self, tree: EvolutionTree):
        """Добавление эволюционного дерева"""
        self.evolution_trees[tree.tree_id] = tree
    
    def _add_genetic_combination(self, combination: GeneticCombination):
        """Добавление генетической комбинации"""
        self.genetic_combinations[combination.combination_id] = combination
    
    def register_character(self, character_id: str) -> bool:
        """Регистрация персонажа в системе эволюции"""
        try:
            if character_id in self.character_progress:
                self._logger.warning(f"Персонаж {character_id} уже зарегистрирован")
                return False
            
            # Создаем прогресс эволюции
            progress = EvolutionProgress(
                character_id=character_id,
                evolution_points=0,
                current_stage=EvolutionStage.BASIC
            )
            
            self.character_progress[character_id] = progress
            
            # Инициализируем гены для персонажа
            self._initialize_character_genes(character_id)
            
            self._logger.info(f"Персонаж {character_id} зарегистрирован в системе эволюции")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка регистрации персонажа {character_id}: {e}")
            return False
    
    def _initialize_character_genes(self, character_id: str):
        """Инициализация генов для персонажа"""
        try:
            # Копируем базовые гены для персонажа
            for gene_id, base_gene in self.genes_registry.items():
                character_gene = Gene(
                    gene_id=f"{character_id}_{gene_id}",
                    gene_type=base_gene.gene_type,
                    name=base_gene.name,
                    description=base_gene.description,
                    base_value=base_gene.base_value,
                    current_value=base_gene.base_value,
                    max_value=base_gene.max_value,
                    mutation_chance=base_gene.mutation_chance,
                    evolution_cost=base_gene.evolution_cost,
                    requirements=base_gene.requirements.copy(),
                    effects=base_gene.effects.copy(),
                    visual_effects=base_gene.visual_effects.copy()
                )
                
                # Сохраняем ген персонажа
                self.genes_registry[f"{character_id}_{gene_id}"] = character_gene
            
            self._logger.info(f"Гены инициализированы для персонажа {character_id}")
            
        except Exception as e:
            self._logger.error(f"Ошибка инициализации генов для персонажа {character_id}: {e}")
            raise
    
    def trigger_mutation(self, character_id: str, gene_id: str, 
                        mutation_type: MutationType = MutationType.SPONTANEOUS) -> Optional[Mutation]:
        """Запуск мутации гена"""
        try:
            full_gene_id = f"{character_id}_{gene_id}"
            if full_gene_id not in self.genes_registry:
                self._logger.warning(f"Ген {full_gene_id} не найден")
                return None
            
            gene = self.genes_registry[full_gene_id]
            
            # Проверяем шанс мутации
            if random.random() > gene.mutation_chance:
                return None
            
            # Создаем мутацию
            mutation = Mutation(
                mutation_id=f"mutation_{character_id}_{gene_id}_{int(time.time())}",
                gene_id=full_gene_id,
                mutation_type=mutation_type,
                name=f"Мутация {gene.name}",
                description=f"Спонтанная мутация гена {gene.name}",
                value_change=random.uniform(-5.0, 10.0),
                duration=None,  # Постоянная мутация
                visual_effects=["gene_glow", "mutation_particles"]
            )
            
            # Применяем мутацию
            self._apply_mutation(mutation)
            
            # Проверяем каскадные мутации
            if random.random() < self.cascade_mutation_chance:
                self._trigger_cascade_mutations(character_id, gene_id)
            
            # Уведомляем о мутации
            self._notify_mutation_triggered(mutation)
            
            self._logger.info(f"Мутация {mutation.mutation_id} применена к гену {full_gene_id}")
            return mutation
            
        except Exception as e:
            self._logger.error(f"Ошибка запуска мутации для персонажа {character_id}: {e}")
            return None
    
    def _apply_mutation(self, mutation: Mutation):
        """Применение мутации к гену"""
        try:
            gene = self.genes_registry[mutation.gene_id]
            
            # Применяем изменение значения
            new_value = gene.current_value + mutation.value_change
            gene.current_value = max(0.0, min(gene.max_value, new_value))
            
            # Сохраняем мутацию
            self.mutations_registry[mutation.mutation_id] = mutation
            
            # Обновляем прогресс персонажа
            character_id = mutation.gene_id.split('_')[0]
            if character_id in self.character_progress:
                progress = self.character_progress[character_id]
                progress.active_mutations.append(mutation.mutation_id)
                
                # Добавляем в историю
                progress.evolution_history.append({
                    "type": "mutation",
                    "mutation_id": mutation.mutation_id,
                    "timestamp": time.time(),
                    "description": f"Мутация {mutation.name}"
                })
            
        except Exception as e:
            self._logger.error(f"Ошибка применения мутации {mutation.mutation_id}: {e}")
            raise
    
    def _trigger_cascade_mutations(self, character_id: str, source_gene_id: str):
        """Запуск каскадных мутаций"""
        try:
            # Находим связанные гены
            related_genes = self._find_related_genes(source_gene_id)
            
            for gene_id in related_genes:
                if random.random() < self.cascade_mutation_chance:
                    self.trigger_mutation(character_id, gene_id, MutationType.CASCADE)
            
            # Уведомляем о каскадных мутациях
            self._notify_cascade_mutations(character_id, source_gene_id)
            
        except Exception as e:
            self._logger.error(f"Ошибка запуска каскадных мутаций: {e}")
    
    def _find_related_genes(self, gene_id: str) -> List[str]:
        """Поиск связанных генов"""
        try:
            related = []
            base_gene_id = gene_id.split('_', 1)[1] if '_' in gene_id else gene_id
            
            # Ищем гены того же типа
            for gid in self.genes_registry:
                if gid != gene_id and base_gene_id in gid:
                    related.append(gid)
            
            return related
            
        except Exception as e:
            self._logger.error(f"Ошибка поиска связанных генов: {e}")
            return []
    
    def evolve_gene(self, character_id: str, gene_id: str, 
                    evolution_points: int) -> bool:
        """Эволюция гена персонажа"""
        try:
            full_gene_id = f"{character_id}_{gene_id}"
            if full_gene_id not in self.genes_registry:
                self._logger.warning(f"Ген {full_gene_id} не найден")
                return False
            
            gene = self.genes_registry[full_gene_id]
            progress = self.character_progress[character_id]
            
            # Проверяем достаточно ли очков эволюции
            if progress.evolution_points < evolution_points:
                self._logger.warning(f"Недостаточно очков эволюции для {character_id}")
                return False
            
            # Проверяем можно ли эволюционировать
            if gene.current_value >= gene.max_value:
                self._logger.warning(f"Ген {full_gene_id} уже максимально развит")
                return False
            
            # Применяем эволюцию
            evolution_bonus = evolution_points * self.evolution_cost_multiplier
            gene.current_value = min(gene.max_value, gene.current_value + evolution_bonus)
            
            # Тратим очки эволюции
            progress.evolution_points -= evolution_points
            
            # Обновляем историю
            progress.evolution_history.append({
                "type": "evolution",
                "gene_id": full_gene_id,
                "points_spent": evolution_points,
                "timestamp": time.time(),
                "description": f"Эволюция гена {gene.name}"
            })
            
            # Проверяем разблокировку новых стадий
            self._check_evolution_stages(character_id)
            
            # Уведомляем об эволюции
            self._notify_evolution_completed(character_id, full_gene_id, evolution_bonus)
            
            self._logger.info(f"Ген {full_gene_id} эволюционирован на {evolution_bonus}")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка эволюции гена {gene_id} для персонажа {character_id}: {e}")
            return False
    
    def _check_evolution_stages(self, character_id: str):
        """Проверка разблокировки новых стадий эволюции"""
        try:
            progress = self.character_progress[character_id]
            
            for tree_id, tree in self.evolution_trees.items():
                for stage in tree.stages:
                    if stage == progress.current_stage:
                        continue
                    
                    if self._can_unlock_stage(character_id, tree_id, stage):
                        self._unlock_evolution_stage(character_id, tree_id, stage)
            
        except Exception as e:
            self._logger.error(f"Ошибка проверки стадий эволюции: {e}")
    
    def _can_unlock_stage(self, character_id: str, tree_id: str, 
                          stage: EvolutionStage) -> bool:
        """Проверка возможности разблокировки стадии"""
        try:
            tree = self.evolution_trees[tree_id]
            if stage not in tree.requirements:
                return False
            
            requirements = tree.requirements[stage]
            progress = self.character_progress[character_id]
            
            for requirement in requirements:
                if ":" in requirement:
                    req_type, req_value = requirement.split(":")
                    req_value = float(req_value)
                    
                    if req_type == "evolution_points":
                        if progress.evolution_points < req_value:
                            return False
                    else:
                        # Проверяем значение гена
                        gene_id = f"{character_id}_{req_type}"
                        if gene_id in self.genes_registry:
                            gene = self.genes_registry[gene_id]
                            if gene.current_value < req_value:
                                return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка проверки возможности разблокировки стадии: {e}")
            return False
    
    def _unlock_evolution_stage(self, character_id: str, tree_id: str, 
                                stage: EvolutionStage):
        """Разблокировка стадии эволюции"""
        try:
            progress = self.character_progress[character_id]
            tree = self.evolution_trees[tree_id]
            
            # Обновляем текущую стадию
            if tree.stages.index(stage) > tree.stages.index(progress.current_stage):
                progress.current_stage = stage
            
            # Добавляем в историю
            progress.evolution_history.append({
                "type": "stage_unlocked",
                "tree_id": tree_id,
                "stage": stage.value,
                "timestamp": time.time(),
                "description": f"Разблокирована стадия {stage.value} в дереве {tree.name}"
            })
            
            # Применяем награды
            if stage in tree.rewards:
                self._apply_evolution_rewards(character_id, tree.rewards[stage])
            
            # Уведомляем о разблокировке
            self._notify_stage_unlocked(character_id, tree_id, stage)
            
            self._logger.info(f"Стадия {stage.value} разблокирована для персонажа {character_id}")
            
        except Exception as e:
            self._logger.error(f"Ошибка разблокировки стадии эволюции: {e}")
    
    def _apply_evolution_rewards(self, character_id: str, rewards: Dict[str, Any]):
        """Применение наград за эволюцию"""
        try:
            # Здесь будет логика применения наград
            # Например, увеличение характеристик, разблокировка способностей и т.д.
            self._logger.info(f"Применены награды эволюции для персонажа {character_id}: {rewards}")
            
        except Exception as e:
            self._logger.error(f"Ошибка применения наград эволюции: {e}")
    
    def get_character_evolution_status(self, character_id: str) -> Dict[str, Any]:
        """Получение статуса эволюции персонажа"""
        try:
            if character_id not in self.character_progress:
                return {}
            
            progress = self.character_progress[character_id]
            status = {
                "character_id": character_id,
                "evolution_points": progress.evolution_points,
                "current_stage": progress.current_stage.value,
                "completed_paths": progress.completed_paths,
                "active_mutations": len(progress.active_mutations),
                "evolution_history": progress.evolution_history[-10:],  # Последние 10 записей
                "last_evolution": progress.last_evolution
            }
            
            # Добавляем информацию о генах
            genes_info = {}
            for gene_id, gene in self.genes_registry.items():
                if gene_id.startswith(character_id):
                    base_gene_id = gene_id.split('_', 1)[1]
                    genes_info[base_gene_id] = {
                        "name": gene.name,
                        "current_value": gene.current_value,
                        "max_value": gene.max_value,
                        "type": gene.gene_type.value
                    }
            
            status["genes"] = genes_info
            return status
            
        except Exception as e:
            self._logger.error(f"Ошибка получения статуса эволюции для персонажа {character_id}: {e}")
            return {}
    
    def add_evolution_points(self, character_id: str, points: int) -> bool:
        """Добавление очков эволюции персонажу"""
        try:
            if character_id not in self.character_progress:
                self._logger.warning(f"Персонаж {character_id} не найден")
                return False
            
            progress = self.character_progress[character_id]
            progress.evolution_points += points
            
            # Обновляем историю
            progress.evolution_history.append({
                "type": "points_earned",
                "points": points,
                "timestamp": time.time(),
                "description": f"Получено {points} очков эволюции"
            })
            
            self._logger.info(f"Персонажу {character_id} добавлено {points} очков эволюции")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка добавления очков эволюции: {e}")
            return False
    
    def _notify_mutation_triggered(self, mutation: Mutation):
        """Уведомление о запуске мутации"""
        try:
            event = create_event(
                event_type="mutation_triggered",
                data={"mutation": mutation},
                source="EvolutionSystem"
            )
            
            # Отправляем событие через EventBus
            if hasattr(self, 'event_bus') and self.event_bus:
                self.event_bus.publish("mutation_triggered", event.data)
            
        except Exception as e:
            self._logger.error(f"Ошибка уведомления о мутации: {e}")
    
    def _notify_cascade_mutations(self, character_id: str, source_gene_id: str):
        """Уведомление о каскадных мутациях"""
        try:
            event = create_event(
                event_type="cascade_mutations",
                data={"character_id": character_id, "source_gene_id": source_gene_id},
                source="EvolutionSystem"
            )
            
            if hasattr(self, 'event_bus') and self.event_bus:
                self.event_bus.publish("cascade_mutations", event.data)
            
        except Exception as e:
            self._logger.error(f"Ошибка уведомления о каскадных мутациях: {e}")
    
    def _notify_evolution_completed(self, character_id: str, gene_id: str, bonus: float):
        """Уведомление о завершении эволюции"""
        try:
            event = create_event(
                event_type="evolution_completed",
                data={"character_id": character_id, "gene_id": gene_id, "bonus": bonus},
                source="EvolutionSystem"
            )
            
            if hasattr(self, 'event_bus') and self.event_bus:
                self.event_bus.publish("evolution_completed", event.data)
            
        except Exception as e:
            self._logger.error(f"Ошибка уведомления об эволюции: {e}")
    
    def _notify_stage_unlocked(self, character_id: str, tree_id: str, stage: EvolutionStage):
        """Уведомление о разблокировке стадии"""
        try:
            event = create_event(
                event_type="stage_unlocked",
                data={"character_id": character_id, "tree_id": tree_id, "stage": stage.value},
                source="EvolutionSystem"
            )
            
            if hasattr(self, 'event_bus') and self.event_bus:
                self.event_bus.publish("stage_unlocked", event.data)
            
        except Exception as e:
            self._logger.error(f"Ошибка уведомления о разблокировке стадии: {e}")
    
    def update(self, delta_time: float):
        """Обновление системы эволюции"""
        try:
            # Проверяем спонтанные мутации
            self._check_spontaneous_mutations()
            
            # Обновляем временные мутации
            self._update_temporary_mutations(delta_time)
            
            # Проверяем генетические комбинации
            self._check_genetic_combinations()
            
        except Exception as e:
            self._logger.error(f"Ошибка обновления системы эволюции: {e}")
    
    def _check_spontaneous_mutations(self):
        """Проверка спонтанных мутаций"""
        try:
            for character_id in self.character_progress:
                for gene_id, gene in self.genes_registry.items():
                    if gene_id.startswith(character_id):
                        if random.random() < gene.mutation_chance * self.mutation_rate:
                            self.trigger_mutation(character_id, gene_id.split('_', 1)[1])
            
        except Exception as e:
            self._logger.error(f"Ошибка проверки спонтанных мутаций: {e}")
    
    def _update_temporary_mutations(self, delta_time: float):
        """Обновление временных мутаций"""
        try:
            current_time = time.time()
            expired_mutations = []
            
            for mutation_id, mutation in self.mutations_registry.items():
                if mutation.duration and (current_time - mutation.timestamp) > mutation.duration:
                    expired_mutations.append(mutation_id)
            
            # Удаляем истекшие мутации
            for mutation_id in expired_mutations:
                self._remove_mutation(mutation_id)
                
        except Exception as e:
            self._logger.error(f"Ошибка обновления временных мутаций: {e}")
    
    def _remove_mutation(self, mutation_id: str):
        """Удаление мутации"""
        try:
            if mutation_id in self.mutations_registry:
                mutation = self.mutations_registry[mutation_id]
                
                # Откатываем изменение гена
                gene = self.genes_registry[mutation.gene_id]
                gene.current_value -= mutation.value_change
                gene.current_value = max(0.0, min(gene.max_value, gene.current_value))
                
                # Удаляем из реестра
                del self.mutations_registry[mutation_id]
                
                # Удаляем из прогресса персонажа
                character_id = mutation.gene_id.split('_')[0]
                if character_id in self.character_progress:
                    progress = self.character_progress[character_id]
                    if mutation_id in progress.active_mutations:
                        progress.active_mutations.remove(mutation_id)
                
                self._logger.info(f"Мутация {mutation_id} удалена")
                
        except Exception as e:
            self._logger.error(f"Ошибка удаления мутации {mutation_id}: {e}")
    
    def _check_genetic_combinations(self):
        """Проверка генетических комбинаций"""
        try:
            for character_id in self.character_progress:
                for combination_id, combination in self.genetic_combinations.items():
                    if self._can_activate_combination(character_id, combination):
                        if random.random() < combination.activation_chance:
                            self._activate_genetic_combination(character_id, combination)
            
        except Exception as e:
            self._logger.error(f"Ошибка проверки генетических комбинаций: {e}")
    
    def _can_activate_combination(self, character_id: str, 
                                 combination: GeneticCombination) -> bool:
        """Проверка возможности активации комбинации"""
        try:
            for required_gene in combination.required_genes:
                gene_id = f"{character_id}_{required_gene}"
                if gene_id not in self.genes_registry:
                    return False
                
                gene = self.genes_registry[gene_id]
                if gene.current_value < 20.0:  # Минимальное значение для активации
                    return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка проверки возможности активации комбинации: {e}")
            return False
    
    def _activate_genetic_combination(self, character_id: str, 
                                     combination: GeneticCombination):
        """Активация генетической комбинации"""
        try:
            # Создаем временную мутацию с эффектами комбинации
            mutation = Mutation(
                mutation_id=f"combo_{combination.combination_id}_{character_id}_{int(time.time())}",
                gene_id=f"{character_id}_combo",
                mutation_type=MutationType.COMBINATIONAL,
                name=combination.name,
                description=combination.description,
                value_change=0.0,  # Комбинация не изменяет значения генов
                duration=combination.duration or 300.0,  # 5 минут по умолчанию
                visual_effects=combination.visual_effects,
                side_effects=combination.side_effects
            )
            
            # Применяем комбинацию
            self._apply_mutation(mutation)
            
            self._logger.info(f"Генетическая комбинация {combination.combination_id} активирована для персонажа {character_id}")
            
        except Exception as e:
            self._logger.error(f"Ошибка активации генетической комбинации: {e}")
    
    def get_evolution_summary(self) -> Dict[str, Any]:
        """Получение сводки по системе эволюции"""
        try:
            summary = {
                "total_characters": len(self.character_progress),
                "total_genes": len(self.genes_registry),
                "total_mutations": len(self.mutations_registry),
                "total_evolution_trees": len(self.evolution_trees),
                "total_genetic_combinations": len(self.genetic_combinations),
                "mutation_rate": self.mutation_rate,
                "cascade_mutation_chance": self.cascade_mutation_chance
            }
            
            # Статистика по персонажам
            character_stats = []
            for character_id, progress in self.character_progress.items():
                stats = {
                    "character_id": character_id,
                    "evolution_points": progress.evolution_points,
                    "current_stage": progress.current_stage.value,
                    "active_mutations": len(progress.active_mutations),
                    "completed_paths": len(progress.completed_paths)
                }
                character_stats.append(stats)
            
            summary["character_stats"] = character_stats
            return summary
            
        except Exception as e:
            self._logger.error(f"Ошибка получения сводки по системе эволюции: {e}")
            return {}
    

