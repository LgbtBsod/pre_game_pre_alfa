#!/usr/bin/env python3
"""
Система процедурной генерации ловушек, препятствий и сундуков.
Создает уникальные испытания для каждой игровой сессии.
Вдохновлено механиками из Binding of Isaac и Darkest Dungeon.
"""

import random
import uuid
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


class HazardType(Enum):
    """Типы опасностей"""
    TRAP = "trap"
    ENVIRONMENTAL = "environmental"
    POISON = "poison"
    RADIATION = "radiation"
    ELECTRIC = "electric"
    FIRE = "fire"
    ICE = "ice"
    ACID = "acid"
    GRAVITY = "gravity"
    TIME = "time"


class TrapType(Enum):
    """Типы ловушек"""
    SPIKE = "spike"
    PITFALL = "pitfall"
    ARROW = "arrow"
    EXPLOSIVE = "explosive"
    POISON_DART = "poison_dart"
    ELECTRIC_SHOCK = "electric_shock"
    FREEZING = "freezing"
    BURNING = "burning"
    TELEPORT = "teleport"
    ILLUSION = "illusion"


class ChestType(Enum):
    """Типы сундуков"""
    WOODEN = "wooden"
    IRON = "iron"
    GOLDEN = "golden"
    MAGICAL = "magical"
    CURSED = "cursed"
    TIMED = "timed"
    PUZZLE = "puzzle"
    MIMIC = "mimic"


class HazardDifficulty(Enum):
    """Сложность опасности"""
    TRIVIAL = 0.1
    EASY = 0.3
    NORMAL = 0.5
    HARD = 0.7
    DEADLY = 0.9
    IMPOSSIBLE = 1.0


@dataclass
class HazardPattern:
    """Паттерн опасности"""
    id: str
    hazard_type: HazardType
    trap_type: Optional[TrapType]
    difficulty: HazardDifficulty
    damage: float
    duration: float
    radius: float
    activation_conditions: List[str]
    deactivation_conditions: List[str]
    visual_effects: List[str]
    audio_effects: List[str]
    ai_behavior_modifiers: Dict[str, float]


@dataclass
class GeneratedHazard:
    """Сгенерированная опасность"""
    guid: str
    pattern: HazardPattern
    position: Tuple[float, float, float]
    is_active: bool
    activation_time: float
    last_triggered: float
    trigger_count: int
    victims: List[str]
    custom_properties: Dict[str, Any]
    
    def can_trigger(self, entity_id: str, current_time: float) -> bool:
        """Проверка возможности срабатывания"""
        if not self.is_active:
            return False
        
        # Проверка времени перезарядки
        cooldown = self.pattern.duration * 0.5
        if current_time - self.last_triggered < cooldown:
            return False
        
        # Проверка, не является ли сущность жертвой
        if entity_id in self.victims:
            return False
        
        return True


@dataclass
class ChestReward:
    """Награда сундука"""
    item_type: str
    rarity: str
    quantity: int
    quality: float
    special_properties: List[str]
    evolution_bonus: Optional[str]


@dataclass
class GeneratedChest:
    """Сгенерированный сундук"""
    guid: str
    chest_type: ChestType
    position: Tuple[float, float, float]
    is_locked: bool
    lock_difficulty: float
    trap_difficulty: float
    rewards: List[ChestReward]
    required_keys: List[str]
    puzzle_requirements: Dict[str, Any]
    is_mimic: bool
    mimic_difficulty: float
    custom_properties: Dict[str, Any]


class TrapAndHazardSystem:
    """Система ловушек и опасностей"""
    
    def __init__(self, world_seed: int = None):
        self.world_seed = world_seed or random.randint(1, 999999)
        random.seed(self.world_seed)
        
        # Генерированные опасности
        self.hazards: Dict[str, GeneratedHazard] = {}
        
        # Генерированные сундуки
        self.chests: Dict[str, GeneratedChest] = {}
        
        # Паттерны опасностей
        self.hazard_patterns = self._init_hazard_patterns()
        
        # Паттерны сундуков
        self.chest_patterns = self._init_chest_patterns()
        
        # Система обнаружения
        self.detection_system = self._init_detection_system()
        
        logger.info(f"Система ловушек и опасностей инициализирована (seed: {self.world_seed})")
    
    def generate_world_hazards(self, world_size: Tuple[int, int], 
                              hazard_density: float = 0.1) -> List[GeneratedHazard]:
        """Генерация опасностей для мира"""
        hazards = []
        world_area = world_size[0] * world_size[1]
        target_hazards = int(world_area * hazard_density)
        
        for _ in range(target_hazards):
            hazard = self._generate_random_hazard(world_size)
            if hazard:
                hazards.append(hazard)
                self.hazards[hazard.guid] = hazard
        
        logger.info(f"Сгенерировано {len(hazards)} опасностей")
        return hazards
    
    def generate_world_chests(self, world_size: Tuple[int, int], 
                             chest_density: float = 0.05) -> List[GeneratedChest]:
        """Генерация сундуков для мира"""
        chests = []
        world_area = world_size[0] * world_size[1]
        target_chests = int(world_area * chest_density)
        
        for _ in range(target_chests):
            chest = self._generate_random_chest(world_size)
            if chest:
                chests.append(chest)
                self.chests[chest.guid] = chest
        
        logger.info(f"Сгенерировано {len(chests)} сундуков")
        return chests
    
    def check_hazard_collision(self, entity_position: Tuple[float, float, float], 
                              entity_id: str, current_time: float) -> Optional[GeneratedHazard]:
        """Проверка столкновения с опасностью"""
        for hazard in self.hazards.values():
            if not hazard.is_active:
                continue
            
            distance = math.sqrt(
                (entity_position[0] - hazard.position[0]) ** 2 +
                (entity_position[1] - hazard.position[1]) ** 2
            )
            
            if distance <= hazard.pattern.radius:
                if hazard.can_trigger(entity_id, current_time):
                    return hazard
        
        return None
    
    def trigger_hazard(self, hazard: GeneratedHazard, entity_id: str, 
                      current_time: float) -> Dict[str, Any]:
        """Срабатывание опасности"""
        hazard.last_triggered = current_time
        hazard.trigger_count += 1
        hazard.victims.append(entity_id)
        
        # Расчёт урона
        damage = self._calculate_hazard_damage(hazard, entity_id)
        
        # Применение эффектов
        effects = self._apply_hazard_effects(hazard, entity_id)
        
        # Обновление статистики
        self._update_hazard_statistics(hazard)
        
        logger.debug(f"Опасность {hazard.guid} сработала для {entity_id}")
        
        return {
            "damage": damage,
            "effects": effects,
            "hazard_type": hazard.pattern.hazard_type.value,
            "trap_type": hazard.pattern.trap_type.value if hazard.pattern.trap_type else None
        }
    
    def attempt_chest_interaction(self, chest: GeneratedChest, entity_id: str,
                                entity_skills: Dict[str, float]) -> Dict[str, Any]:
        """Попытка взаимодействия с сундуком"""
        if chest.is_mimic:
            return self._handle_mimic_chest(chest, entity_id, entity_skills)
        
        if chest.is_locked:
            return self._attempt_chest_unlock(chest, entity_id, entity_skills)
        
        # Проверка ловушки
        if chest.trap_difficulty > 0:
            trap_result = self._check_chest_trap(chest, entity_id, entity_skills)
            if not trap_result["success"]:
                return trap_result
        
        # Открытие сундука
        rewards = self._generate_chest_rewards(chest)
        
        # Удаление сундука после открытия
        if chest.guid in self.chests:
            del self.chests[chest.guid]
        
        return {
            "success": True,
            "rewards": rewards,
            "chest_type": chest.chest_type.value,
            "message": "Сундук успешно открыт!"
        }
    
    def _generate_random_hazard(self, world_size: Tuple[int, int]) -> Optional[GeneratedHazard]:
        """Генерация случайной опасности"""
        # Выбор паттерна
        pattern = random.choice(self.hazard_patterns)
        
        # Генерация позиции
        position = (
            random.uniform(0, world_size[0]),
            random.uniform(0, world_size[1]),
            random.uniform(0, 10)  # Высота
        )
        
        # Проверка на перекрытие с существующими опасностями
        if self._check_hazard_overlap(position, pattern.radius):
            return None
        
        # Создание опасности
        hazard = GeneratedHazard(
            guid=str(uuid.uuid4()),
            pattern=pattern,
            position=position,
            is_active=True,
            activation_time=0.0,
            last_triggered=0.0,
            trigger_count=0,
            victims=[],
            custom_properties=self._generate_custom_properties(pattern)
        )
        
        return hazard
    
    def _generate_random_chest(self, world_size: Tuple[int, int]) -> Optional[GeneratedChest]:
        """Генерация случайного сундука"""
        # Выбор типа сундука
        chest_type = random.choices(
            list(ChestType),
            weights=[0.4, 0.3, 0.15, 0.1, 0.03, 0.01, 0.005, 0.005]
        )[0]
        
        # Генерация позиции
        position = (
            random.uniform(0, world_size[0]),
            random.uniform(0, world_size[1]),
            0.0
        )
        
        # Проверка на перекрытие
        if self._check_chest_overlap(position):
            return None
        
        # Создание сундука
        chest = GeneratedChest(
            guid=str(uuid.uuid4()),
            chest_type=chest_type,
            position=position,
            is_locked=chest_type in [ChestType.IRON, ChestType.GOLDEN, ChestType.MAGICAL],
            lock_difficulty=self._calculate_lock_difficulty(chest_type),
            trap_difficulty=self._calculate_trap_difficulty(chest_type),
            rewards=self._generate_chest_rewards_pattern(chest_type),
            required_keys=self._generate_required_keys(chest_type),
            puzzle_requirements=self._generate_puzzle_requirements(chest_type),
            is_mimic=chest_type == ChestType.MIMIC,
            mimic_difficulty=random.uniform(0.6, 0.9),
            custom_properties=self._generate_chest_custom_properties(chest_type)
        )
        
        return chest
    
    def _init_hazard_patterns(self) -> List[HazardPattern]:
        """Инициализация паттернов опасностей"""
        patterns = []
        
        # Ловушки-шипы
        patterns.append(HazardPattern(
            id="spike_trap_01",
            hazard_type=HazardType.TRAP,
            trap_type=TrapType.SPIKE,
            difficulty=HazardDifficulty.NORMAL,
            damage=25.0,
            duration=5.0,
            radius=1.5,
            activation_conditions=["pressure_plate", "proximity"],
            deactivation_conditions=["time", "reset"],
            visual_effects=["spike_animation", "blood_splatter"],
            audio_effects=["spike_sound", "scream"],
            ai_behavior_modifiers={"fear": 0.3, "caution": 0.5}
        ))
        
        # Ямы-ловушки
        patterns.append(HazardPattern(
            id="pitfall_01",
            hazard_type=HazardType.ENVIRONMENTAL,
            trap_type=TrapType.PITFALL,
            difficulty=HazardDifficulty.HARD,
            damage=50.0,
            duration=10.0,
            radius=2.0,
            activation_conditions=["weight", "proximity"],
            deactivation_conditions=["escape", "rescue"],
            visual_effects=["pit_animation", "falling"],
            audio_effects=["falling_sound", "impact"],
            ai_behavior_modifiers={"fear": 0.6, "caution": 0.8}
        ))
        
        # Стрелы-ловушки
        patterns.append(HazardPattern(
            id="arrow_trap_01",
            hazard_type=HazardType.TRAP,
            trap_type=TrapType.ARROW,
            difficulty=HazardDifficulty.EASY,
            damage=15.0,
            duration=3.0,
            radius=3.0,
            activation_conditions=["tripwire", "motion"],
            deactivation_conditions=["time", "ammo_depletion"],
            visual_effects=["arrow_animation", "projectile"],
            audio_effects=["bow_string", "arrow_whistle"],
            ai_behavior_modifiers={"fear": 0.2, "caution": 0.4}
        ))
        
        # Взрывные ловушки
        patterns.append(HazardPattern(
            id="explosive_trap_01",
            hazard_type=HazardType.TRAP,
            trap_type=TrapType.EXPLOSIVE,
            difficulty=HazardDifficulty.DEADLY,
            damage=75.0,
            duration=2.0,
            radius=4.0,
            activation_conditions=["pressure", "timer", "remote"],
            deactivation_conditions=["defuse", "explosion"],
            visual_effects=["explosion", "fire", "smoke"],
            audio_effects=["explosion", "debris"],
            ai_behavior_modifiers={"fear": 0.8, "panic": 0.7}
        ))
        
        # Ядовитые дротики
        patterns.append(HazardPattern(
            id="poison_dart_01",
            hazard_type=HazardType.POISON,
            trap_type=TrapType.POISON_DART,
            difficulty=HazardDifficulty.NORMAL,
            damage=20.0,
            duration=15.0,
            radius=2.5,
            activation_conditions=["pressure", "motion"],
            deactivation_conditions=["time", "antidote"],
            visual_effects=["dart_animation", "poison_effect"],
            audio_effects=["dart_sound", "poison_hiss"],
            ai_behavior_modifiers={"fear": 0.4, "caution": 0.6}
        ))
        
        # Электрические ловушки
        patterns.append(HazardPattern(
            id="electric_trap_01",
            hazard_type=HazardType.ELECTRIC,
            trap_type=TrapType.ELECTRIC_SHOCK,
            difficulty=HazardDifficulty.HARD,
            damage=40.0,
            duration=8.0,
            radius=2.0,
            activation_conditions=["conductivity", "proximity"],
            deactivation_conditions=["insulation", "power_depletion"],
            visual_effects=["electric_arc", "sparks"],
            audio_effects=["electric_crackle", "zap"],
            ai_behavior_modifiers={"fear": 0.5, "caution": 0.7}
        ))
        
        # Замораживающие ловушки
        patterns.append(HazardPattern(
            id="freezing_trap_01",
            hazard_type=HazardType.ICE,
            trap_type=TrapType.FREEZING,
            difficulty=HazardDifficulty.NORMAL,
            damage=30.0,
            duration=12.0,
            radius=2.5,
            activation_conditions=["temperature", "proximity"],
            deactivation_conditions=["heat", "time"],
            visual_effects=["ice_formation", "frost"],
            audio_effects=["freezing_sound", "ice_crack"],
            ai_behavior_modifiers={"fear": 0.3, "caution": 0.5}
        ))
        
        # Кислотные ловушки
        patterns.append(HazardPattern(
            id="acid_trap_01",
            hazard_type=HazardType.ACID,
            trap_type=None,
            difficulty=HazardDifficulty.DEADLY,
            damage=60.0,
            duration=20.0,
            radius=3.0,
            activation_conditions=["container_break", "timer"],
            deactivation_conditions=["neutralization", "drainage"],
            visual_effects=["acid_bubble", "corrosion"],
            audio_effects=["acid_bubble", "corrosion_hiss"],
            ai_behavior_modifiers={"fear": 0.7, "panic": 0.6}
        ))
        
        return patterns
    
    def _init_chest_patterns(self) -> Dict[ChestType, Dict[str, Any]]:
        """Инициализация паттернов сундуков"""
        return {
            ChestType.WOODEN: {
                "lock_difficulty": 0.0,
                "trap_difficulty": 0.1,
                "reward_quality": 0.3,
                "evolution_bonus_chance": 0.05
            },
            ChestType.IRON: {
                "lock_difficulty": 0.4,
                "trap_difficulty": 0.3,
                "reward_quality": 0.6,
                "evolution_bonus_chance": 0.15
            },
            ChestType.GOLDEN: {
                "lock_difficulty": 0.7,
                "trap_difficulty": 0.6,
                "reward_quality": 0.8,
                "evolution_bonus_chance": 0.3
            },
            ChestType.MAGICAL: {
                "lock_difficulty": 0.8,
                "trap_difficulty": 0.7,
                "reward_quality": 0.9,
                "evolution_bonus_chance": 0.5
            },
            ChestType.CURSED: {
                "lock_difficulty": 0.5,
                "trap_difficulty": 0.8,
                "reward_quality": 0.7,
                "evolution_bonus_chance": 0.2
            },
            ChestType.TIMED: {
                "lock_difficulty": 0.6,
                "trap_difficulty": 0.5,
                "reward_quality": 0.75,
                "evolution_bonus_chance": 0.25
            },
            ChestType.PUZZLE: {
                "lock_difficulty": 0.9,
                "trap_difficulty": 0.4,
                "reward_quality": 0.85,
                "evolution_bonus_chance": 0.4
            },
            ChestType.MIMIC: {
                "lock_difficulty": 0.0,
                "trap_difficulty": 0.9,
                "reward_quality": 0.95,
                "evolution_bonus_chance": 0.6
            }
        }
    
    def _init_detection_system(self) -> Dict[str, float]:
        """Инициализация системы обнаружения"""
        return {
            "visual_detection": 0.7,
            "audio_detection": 0.5,
            "magic_detection": 0.8,
            "trap_detection": 0.6,
            "illusion_detection": 0.4
        }
    
    def _check_hazard_overlap(self, position: Tuple[float, float, float], 
                             radius: float) -> bool:
        """Проверка перекрытия опасностей"""
        for hazard in self.hazards.values():
            distance = math.sqrt(
                (position[0] - hazard.position[0]) ** 2 +
                (position[1] - hazard.position[1]) ** 2
            )
            if distance < (radius + hazard.pattern.radius):
                return True
        return False
    
    def _check_chest_overlap(self, position: Tuple[float, float, float]) -> bool:
        """Проверка перекрытия сундуков"""
        for chest in self.chests.values():
            distance = math.sqrt(
                (position[0] - chest.position[0]) ** 2 +
                (position[1] - chest.position[1]) ** 2
            )
            if distance < 3.0:  # Минимальное расстояние между сундуками
                return True
        return False
    
    def _calculate_lock_difficulty(self, chest_type: ChestType) -> float:
        """Расчёт сложности замка"""
        pattern = self.chest_patterns[chest_type]
        base_difficulty = pattern["lock_difficulty"]
        
        # Добавление случайности
        variation = random.uniform(-0.1, 0.1)
        return max(0.0, min(1.0, base_difficulty + variation))
    
    def _calculate_trap_difficulty(self, chest_type: ChestType) -> float:
        """Расчёт сложности ловушки"""
        pattern = self.chest_patterns[chest_type]
        base_difficulty = pattern["trap_difficulty"]
        
        # Добавление случайности
        variation = random.uniform(-0.1, 0.1)
        return max(0.0, min(1.0, base_difficulty + variation))
    
    def _generate_chest_rewards_pattern(self, chest_type: ChestType) -> List[ChestReward]:
        """Генерация паттерна наград сундука"""
        pattern = self.chest_patterns[chest_type]
        rewards = []
        
        # Количество наград
        num_rewards = random.randint(1, 3)
        
        for _ in range(num_rewards):
            reward = ChestReward(
                item_type=random.choice(["weapon", "armor", "consumable", "material", "artifact"]),
                rarity=self._generate_rarity(chest_type),
                quantity=random.randint(1, 5),
                quality=pattern["reward_quality"] + random.uniform(-0.1, 0.1),
                special_properties=self._generate_special_properties(chest_type),
                evolution_bonus=self._generate_evolution_bonus(pattern["evolution_bonus_chance"])
            )
            rewards.append(reward)
        
        return rewards
    
    def _generate_rarity(self, chest_type: ChestType) -> str:
        """Генерация редкости предмета"""
        rarity_weights = {
            ChestType.WOODEN: {"common": 0.7, "uncommon": 0.25, "rare": 0.05},
            ChestType.IRON: {"common": 0.4, "uncommon": 0.4, "rare": 0.15, "epic": 0.05},
            ChestType.GOLDEN: {"uncommon": 0.3, "rare": 0.4, "epic": 0.2, "legendary": 0.1},
            ChestType.MAGICAL: {"rare": 0.3, "epic": 0.4, "legendary": 0.2, "mythic": 0.1}
        }
        
        weights = rarity_weights.get(chest_type, rarity_weights[ChestType.WOODEN])
        return random.choices(list(weights.keys()), weights=list(weights.values()))[0]
    
    def _generate_special_properties(self, chest_type: ChestType) -> List[str]:
        """Генерация специальных свойств"""
        properties = []
        property_pool = [
            "fire_resistant", "ice_resistant", "poison_resistant", "electric_resistant",
            "enhanced_damage", "enhanced_defense", "enhanced_speed", "enhanced_health",
            "stealth_bonus", "detection_bonus", "crafting_bonus", "evolution_bonus"
        ]
        
        num_properties = random.randint(0, 2)
        if chest_type in [ChestType.GOLDEN, ChestType.MAGICAL]:
            num_properties += 1
        
        selected_properties = random.sample(property_pool, min(num_properties, len(property_pool)))
        properties.extend(selected_properties)
        
        return properties
    
    def _generate_evolution_bonus(self, chance: float) -> Optional[str]:
        """Генерация эволюционного бонуса"""
        if random.random() < chance:
            bonuses = [
                "gene_slot", "mutation_resistance", "evolution_speed", "genetic_stability",
                "emotional_balance", "ai_learning_rate", "memory_capacity", "skill_mastery"
            ]
            return random.choice(bonuses)
        return None
    
    def _generate_required_keys(self, chest_type: ChestType) -> List[str]:
        """Генерация требуемых ключей"""
        if chest_type == ChestType.WOODEN:
            return []
        elif chest_type == ChestType.IRON:
            return ["iron_key"] if random.random() < 0.3 else []
        elif chest_type == ChestType.GOLDEN:
            return ["golden_key"] if random.random() < 0.6 else []
        elif chest_type == ChestType.MAGICAL:
            return ["magical_key", "essence"] if random.random() < 0.8 else ["magical_key"]
        else:
            return []
    
    def _generate_puzzle_requirements(self, chest_type: ChestType) -> Dict[str, Any]:
        """Генерация требований головоломки"""
        if chest_type != ChestType.PUZZLE:
            return {}
        
        puzzle_types = ["sequence", "pattern", "math", "logic", "color"]
        puzzle_type = random.choice(puzzle_types)
        
        if puzzle_type == "sequence":
            return {
                "type": "sequence",
                "sequence": [random.randint(1, 9) for _ in range(random.randint(3, 6))],
                "attempts_allowed": 3
            }
        elif puzzle_type == "pattern":
            return {
                "type": "pattern",
                "pattern": random.choice(["circle", "square", "triangle", "star"]),
                "complexity": random.randint(1, 5)
            }
        elif puzzle_type == "math":
            return {
                "type": "math",
                "equation": f"{random.randint(1, 20)} + {random.randint(1, 20)} * {random.randint(1, 5)}",
                "solution": random.randint(1, 100)
            }
        
        return {"type": "simple", "difficulty": random.uniform(0.3, 0.7)}
    
    def _generate_custom_properties(self, pattern: HazardPattern) -> Dict[str, Any]:
        """Генерация пользовательских свойств"""
        properties = {}
        
        # Случайные модификаторы
        if random.random() < 0.3:
            properties["elemental_affinity"] = random.choice(["fire", "ice", "lightning", "poison"])
        
        if random.random() < 0.2:
            properties["time_delay"] = random.uniform(0.5, 3.0)
        
        if random.random() < 0.25:
            properties["chain_reaction"] = True
        
        if random.random() < 0.15:
            properties["illusion"] = True
        
        return properties
    
    def _generate_chest_custom_properties(self, chest_type: ChestType) -> Dict[str, Any]:
        """Генерация пользовательских свойств сундука"""
        properties = {}
        
        # Специальные свойства для разных типов
        if chest_type == ChestType.TIMED:
            properties["time_limit"] = random.randint(30, 300)
            properties["explosion_damage"] = random.uniform(50, 150)
        
        elif chest_type == ChestType.CURSED:
            properties["curse_type"] = random.choice(["health_drain", "skill_penalty", "luck_reduction"])
            properties["curse_duration"] = random.randint(60, 600)
        
        elif chest_type == ChestType.MIMIC:
            properties["mimic_type"] = random.choice(["aggressive", "stealthy", "intelligent"])
            properties["escape_chance"] = random.uniform(0.1, 0.4)
        
        return properties
    
    def _calculate_hazard_damage(self, hazard: GeneratedHazard, entity_id: str) -> float:
        """Расчёт урона от опасности"""
        base_damage = hazard.pattern.damage
        
        # Модификаторы
        damage_multiplier = 1.0
        
        # Случайная вариация
        variation = random.uniform(0.8, 1.2)
        
        # Модификаторы из пользовательских свойств
        if "elemental_affinity" in hazard.custom_properties:
            # Здесь можно добавить проверку сопротивления сущности
            pass
        
        return base_damage * damage_multiplier * variation
    
    def _apply_hazard_effects(self, hazard: GeneratedHazard, entity_id: str) -> List[str]:
        """Применение эффектов опасности"""
        effects = []
        
        # Базовые эффекты по типу
        if hazard.pattern.hazard_type == HazardType.POISON:
            effects.extend(["poisoned", "health_drain"])
        elif hazard.pattern.hazard_type == HazardType.ELECTRIC:
            effects.extend(["shocked", "stunned"])
        elif hazard.pattern.hazard_type == HazardType.FIRE:
            effects.extend(["burning", "fire_damage"])
        elif hazard.pattern.hazard_type == HazardType.ICE:
            effects.extend(["frozen", "movement_slow"])
        
        # Эффекты из пользовательских свойств
        if hazard.custom_properties.get("chain_reaction"):
            effects.append("chain_reaction_risk")
        
        if hazard.custom_properties.get("illusion"):
            effects.append("illusion_effect")
        
        return effects
    
    def _update_hazard_statistics(self, hazard: GeneratedHazard):
        """Обновление статистики опасности"""
        # Здесь можно добавить логику для отслеживания эффективности опасностей
        pass
    
    def _handle_mimic_chest(self, chest: GeneratedChest, entity_id: str,
                           entity_skills: Dict[str, float]) -> Dict[str, Any]:
        """Обработка мимика-сундука"""
        # Проверка обнаружения
        detection_chance = entity_skills.get("detection", 0.0) * self.detection_system["illusion_detection"]
        
        if random.random() < detection_chance:
            return {
                "success": True,
                "mimic_detected": True,
                "message": "Вы обнаружили мимика!",
                "rewards": self._generate_mimic_rewards(chest)
            }
        
        # Атака мимика
        mimic_damage = random.uniform(30, 80)
        
        return {
            "success": False,
            "mimic_detected": False,
            "damage": mimic_damage,
            "message": "Сундук оказался мимиком!",
            "effects": ["mimic_attack", "surprise"]
        }
    
    def _attempt_chest_unlock(self, chest: GeneratedChest, entity_id: str,
                             entity_skills: Dict[str, float]) -> Dict[str, Any]:
        """Попытка открытия замка сундука"""
        lockpicking_skill = entity_skills.get("lockpicking", 0.0)
        
        if lockpicking_skill >= chest.lock_difficulty:
            chest.is_locked = False
            return {
                "success": True,
                "lock_opened": True,
                "message": "Замок успешно открыт!"
            }
        
        return {
            "success": False,
            "lock_opened": False,
            "message": "Не удалось открыть замок",
            "required_skill": chest.lock_difficulty
        }
    
    def _check_chest_trap(self, chest: GeneratedChest, entity_id: str,
                          entity_skills: Dict[str, float]) -> Dict[str, Any]:
        """Проверка ловушки сундука"""
        trap_detection = entity_skills.get("trap_detection", 0.0) * self.detection_system["trap_detection"]
        
        if random.random() < trap_detection:
            return {
                "success": True,
                "trap_detected": True,
                "message": "Ловушка обнаружена и обезврежена!"
            }
        
        # Срабатывание ловушки
        trap_damage = random.uniform(20, 60)
        
        return {
            "success": False,
            "trap_detected": False,
            "damage": trap_damage,
            "message": "Ловушка сработала!",
            "effects": ["trap_damage", "surprise"]
        }
    
    def _generate_chest_rewards(self, chest: GeneratedChest) -> List[Dict[str, Any]]:
        """Генерация наград сундука"""
        rewards = []
        
        for reward in chest.rewards:
            reward_data = {
                "type": reward.item_type,
                "rarity": reward.rarity,
                "quantity": reward.quantity,
                "quality": reward.quality,
                "special_properties": reward.special_properties
            }
            
            if reward.evolution_bonus:
                reward_data["evolution_bonus"] = reward.evolution_bonus
            
            rewards.append(reward_data)
        
        return rewards
    
    def _generate_mimic_rewards(self, chest: GeneratedChest) -> List[Dict[str, Any]]:
        """Генерация наград за победу над мимиком"""
        # Мимики дают лучшие награды
        return [{
            "type": "artifact",
            "rarity": "legendary",
            "quantity": 1,
            "quality": 0.95,
            "special_properties": ["mimic_slayer", "enhanced_detection"],
            "evolution_bonus": "mimic_mastery"
        }]
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        return {
            "total_hazards": len(self.hazards),
            "total_chests": len(self.chests),
            "active_hazards": len([h for h in self.hazards.values() if h.is_active]),
            "locked_chests": len([c for c in self.chests.values() if c.is_locked]),
            "mimic_chests": len([c for c in self.chests.values() if c.is_mimic]),
            "world_seed": self.world_seed
        }
