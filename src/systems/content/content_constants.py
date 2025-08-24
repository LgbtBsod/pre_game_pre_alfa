#!/usr/bin/env python3
"""
Content Constants - Константы для процедурной генерации контента
"""

import random
from typing import Dict, List, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import time

class GenerationRarity(Enum):
    """Редкость генерации"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class GenerationBiome(Enum):
    """Биомы для генерации"""
    FOREST = "forest"
    CAVE = "cave"
    DUNGEON = "dungeon"
    SWAMP = "swamp"
    MOUNTAIN = "mountain"
    DESERT = "desert"
    OCEAN = "ocean"
    VOLCANO = "volcano"
    ARCTIC = "arctic"
    JUNGLE = "jungle"

class GenerationTime(Enum):
    """Время суток для генерации"""
    DAWN = "dawn"
    DAY = "day"
    DUSK = "dusk"
    NIGHT = "night"
    ANY = "any"

class GenerationWeather(Enum):
    """Погодные условия для генерации"""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    SNOW = "snow"
    FOG = "fog"
    ANY = "any"

@dataclass
class GenerationWeights:
    """Веса для генерации"""
    common: float = 0.5
    uncommon: float = 0.3
    rare: float = 0.15
    epic: float = 0.04
    legendary: float = 0.01

@dataclass
class EnemyGenerationConstants:
    """Константы генерации врагов"""
    
    # Базовые характеристики по типам
    base_stats_by_type: Dict[str, Dict[str, int]] = None
    
    # Модификаторы уровня
    level_multipliers: Dict[str, float] = None
    
    # Веса редкости по типам
    rarity_weights_by_type: Dict[str, GenerationWeights] = None
    
    # Слабости и сопротивления по типам
    type_weaknesses: Dict[str, List[str]] = None
    type_resistances: Dict[str, List[str]] = None
    type_immunities: Dict[str, List[str]] = None
    
    # Поведение AI по типам
    ai_behavior_by_type: Dict[str, str] = None
    
    # Условия появления
    spawn_conditions: Dict[str, Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.base_stats_by_type is None:
            self.base_stats_by_type = {
                'melee': {
                    'health': 100, 'mana': 30, 'attack': 25, 'defense': 12,
                    'speed': 1.2, 'intelligence': 8
                },
                'ranged': {
                    'health': 80, 'mana': 50, 'attack': 20, 'defense': 8,
                    'speed': 1.4, 'intelligence': 12
                },
                'magic': {
                    'health': 70, 'mana': 120, 'attack': 15, 'defense': 8,
                    'speed': 1.1, 'intelligence': 25
                },
                'flying': {
                    'health': 90, 'mana': 40, 'attack': 22, 'defense': 6,
                    'speed': 1.8, 'intelligence': 10
                },
                'undead': {
                    'health': 60, 'mana': 40, 'attack': 20, 'defense': 5,
                    'speed': 0.8, 'intelligence': 15
                },
                'beast': {
                    'health': 150, 'mana': 20, 'attack': 30, 'defense': 15,
                    'speed': 1.3, 'intelligence': 6
                },
                'human': {
                    'health': 100, 'mana': 60, 'attack': 20, 'defense': 10,
                    'speed': 1.0, 'intelligence': 18
                },
                'demon': {
                    'health': 200, 'mana': 80, 'attack': 35, 'defense': 20,
                    'speed': 1.1, 'intelligence': 22
                }
            }
        
        if self.level_multipliers is None:
            self.level_multipliers = {
                'health': 0.15,
                'mana': 0.1,
                'attack': 0.12,
                'defense': 0.1,
                'speed': 0.05,
                'intelligence': 0.08
            }
        
        if self.rarity_weights_by_type is None:
            self.rarity_weights_by_type = {
                'melee': GenerationWeights(0.6, 0.3, 0.08, 0.015, 0.005),
                'ranged': GenerationWeights(0.5, 0.35, 0.12, 0.025, 0.005),
                'magic': GenerationWeights(0.4, 0.4, 0.15, 0.04, 0.01),
                'flying': GenerationWeights(0.55, 0.3, 0.12, 0.025, 0.005),
                'undead': GenerationWeights(0.5, 0.35, 0.12, 0.025, 0.005),
                'beast': GenerationWeights(0.6, 0.3, 0.08, 0.015, 0.005),
                'human': GenerationWeights(0.5, 0.35, 0.12, 0.025, 0.005),
                'demon': GenerationWeights(0.3, 0.4, 0.2, 0.08, 0.02)
            }
        
        if self.type_weaknesses is None:
            self.type_weaknesses = {
                'melee': ['fire', 'lightning'],
                'ranged': ['physical', 'ice'],
                'magic': ['physical', 'arcane'],
                'flying': ['lightning', 'ice'],
                'undead': ['holy', 'fire'],
                'beast': ['fire', 'poison'],
                'human': ['poison', 'dark'],
                'demon': ['holy', 'lightning']
            }
        
        if self.type_resistances is None:
            self.type_resistances = {
                'melee': ['physical', 'poison'],
                'ranged': ['fire', 'lightning'],
                'magic': ['arcane', 'fire'],
                'flying': ['physical', 'poison'],
                'undead': ['poison', 'dark'],
                'beast': ['physical', 'poison'],
                'human': ['fire', 'lightning'],
                'demon': ['dark', 'poison']
            }
        
        if self.type_immunities is None:
            self.type_immunities = {
                'melee': [],
                'ranged': [],
                'magic': ['ice'],
                'flying': [],
                'undead': ['ice'],
                'beast': [],
                'human': [],
                'demon': ['arcane']
            }
        
        if self.ai_behavior_by_type is None:
            self.ai_behavior_by_type = {
                'melee': 'aggressive',
                'ranged': 'cautious',
                'magic': 'strategic',
                'flying': 'hit_and_run',
                'undead': 'persistent',
                'beast': 'berserker',
                'human': 'adaptive',
                'demon': 'ruthless'
            }
        
        if self.spawn_conditions is None:
            self.spawn_conditions = {
                'melee': {
                    'biomes': [GenerationBiome.FOREST, GenerationBiome.CAVE, GenerationBiome.DUNGEON],
                    'time': [GenerationTime.ANY],
                    'weather': [GenerationWeather.ANY]
                },
                'ranged': {
                    'biomes': [GenerationBiome.FOREST, GenerationBiome.MOUNTAIN, GenerationBiome.DESERT],
                    'time': [GenerationTime.DAY, GenerationTime.DAWN],
                    'weather': [GenerationWeather.CLEAR, GenerationWeather.CLOUDY]
                },
                'magic': {
                    'biomes': [GenerationBiome.DUNGEON, GenerationBiome.VOLCANO, GenerationBiome.ARCTIC],
                    'time': [GenerationTime.NIGHT, GenerationTime.DUSK],
                    'weather': [GenerationWeather.STORM, GenerationWeather.FOG]
                },
                'flying': {
                    'biomes': [GenerationBiome.MOUNTAIN, GenerationBiome.OCEAN, GenerationBiome.JUNGLE],
                    'time': [GenerationTime.DAY, GenerationTime.DAWN],
                    'weather': [GenerationWeather.CLEAR, GenerationWeather.CLOUDY]
                },
                'undead': {
                    'biomes': [GenerationBiome.CAVE, GenerationBiome.DUNGEON, GenerationBiome.SWAMP],
                    'time': [GenerationTime.NIGHT, GenerationTime.DUSK],
                    'weather': [GenerationWeather.FOG, GenerationWeather.RAIN]
                },
                'beast': {
                    'biomes': [GenerationBiome.FOREST, GenerationBiome.JUNGLE, GenerationBiome.MOUNTAIN],
                    'time': [GenerationTime.ANY],
                    'weather': [GenerationWeather.ANY]
                },
                'human': {
                    'biomes': [GenerationBiome.FOREST, GenerationBiome.DESERT, GenerationBiome.ARCTIC],
                    'time': [GenerationTime.DAY, GenerationTime.DAWN],
                    'weather': [GenerationWeather.CLEAR, GenerationWeather.CLOUDY]
                },
                'demon': {
                    'biomes': [GenerationBiome.VOLCANO, GenerationBiome.DUNGEON, GenerationBiome.SWAMP],
                    'time': [GenerationTime.NIGHT, GenerationTime.DUSK],
                    'weather': [GenerationWeather.STORM, GenerationWeather.FOG]
                }
            }

@dataclass
class BossGenerationConstants:
    """Константы генерации боссов"""
    
    # Базовые характеристики по типам
    base_stats_by_type: Dict[str, Dict[str, int]] = None
    
    # Модификаторы уровня (боссы растут быстрее)
    level_multipliers: Dict[str, float] = None
    
    # Веса редкости по типам
    rarity_weights_by_type: Dict[str, GenerationWeights] = None
    
    # Слабости и сопротивления по типам
    type_weaknesses: Dict[str, List[str]] = None
    type_resistances: Dict[str, List[str]] = None
    type_immunities: Dict[str, List[str]] = None
    
    # Поведение AI по типам
    ai_behavior_by_type: Dict[str, str] = None
    
    # Фазы боя по типам
    phases_by_type: Dict[str, List[Dict[str, Any]]] = None
    
    # Спавн миньонов по типам
    minion_spawns_by_type: Dict[str, List[Dict[str, Any]]] = None
    
    # Условия появления
    spawn_conditions: Dict[str, Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.base_stats_by_type is None:
            self.base_stats_by_type = {
                'mini_boss': {
                    'health': 800, 'mana': 150, 'attack': 80, 'defense': 40,
                    'speed': 1.2, 'intelligence': 20
                },
                'area_boss': {
                    'health': 2500, 'mana': 400, 'attack': 150, 'defense': 80,
                    'speed': 1.0, 'intelligence': 35
                },
                'dungeon_boss': {
                    'health': 4000, 'mana': 800, 'attack': 200, 'defense': 120,
                    'speed': 1.1, 'intelligence': 50
                },
                'world_boss': {
                    'health': 8000, 'mana': 1500, 'attack': 300, 'defense': 200,
                    'speed': 0.9, 'intelligence': 70
                },
                'final_boss': {
                    'health': 15000, 'mana': 3000, 'attack': 500, 'defense': 300,
                    'speed': 1.3, 'intelligence': 100
                }
            }
        
        if self.level_multipliers is None:
            self.level_multipliers = {
                'health': 0.2,
                'mana': 0.15,
                'attack': 0.18,
                'defense': 0.15,
                'speed': 0.08,
                'intelligence': 0.12
            }
        
        if self.rarity_weights_by_type is None:
            self.rarity_weights_by_type = {
                'mini_boss': GenerationWeights(0.3, 0.4, 0.25, 0.04, 0.01),
                'area_boss': GenerationWeights(0.2, 0.35, 0.3, 0.12, 0.03),
                'dungeon_boss': GenerationWeights(0.1, 0.25, 0.4, 0.2, 0.05),
                'world_boss': GenerationWeights(0.05, 0.15, 0.4, 0.3, 0.1),
                'final_boss': GenerationWeights(0.0, 0.1, 0.3, 0.4, 0.2)
            }
        
        if self.type_weaknesses is None:
            self.type_weaknesses = {
                'mini_boss': ['fire', 'holy'],
                'area_boss': ['ice', 'lightning'],
                'dungeon_boss': ['holy', 'lightning'],
                'world_boss': ['holy', 'arcane'],
                'final_boss': ['holy', 'lightning', 'fire']
            }
        
        if self.type_resistances is None:
            self.type_resistances = {
                'mini_boss': ['poison', 'physical'],
                'area_boss': ['fire', 'physical'],
                'dungeon_boss': ['dark', 'poison'],
                'world_boss': ['dark', 'poison', 'physical'],
                'final_boss': ['dark', 'poison', 'physical', 'arcane']
            }
        
        if self.type_immunities is None:
            self.type_immunities = {
                'mini_boss': [],
                'area_boss': ['poison'],
                'dungeon_boss': ['arcane'],
                'world_boss': ['ice', 'arcane'],
                'final_boss': ['ice', 'arcane', 'poison']
            }
        
        if self.ai_behavior_by_type is None:
            self.ai_behavior_by_type = {
                'mini_boss': 'boss_aggressive',
                'area_boss': 'boss_dragon',
                'dungeon_boss': 'boss_dark_lord',
                'world_boss': 'boss_ancient',
                'final_boss': 'boss_legendary'
            }
        
        if self.phases_by_type is None:
            self.phases_by_type = {
                'mini_boss': [
                    {'health_threshold': 0.5, 'behavior': 'enraged', 'special_ability': 'summon_minions'}
                ],
                'area_boss': [
                    {'health_threshold': 0.75, 'behavior': 'aerial_combat', 'special_ability': 'fire_breath'},
                    {'health_threshold': 0.25, 'behavior': 'grounded_rage', 'special_ability': 'earthquake'}
                ],
                'dungeon_boss': [
                    {'health_threshold': 0.8, 'behavior': 'shadow_form', 'special_ability': 'shadow_step'},
                    {'health_threshold': 0.5, 'behavior': 'necromancer', 'special_ability': 'raise_dead'},
                    {'health_threshold': 0.2, 'behavior': 'final_form', 'special_ability': 'dark_apocalypse'}
                ],
                'world_boss': [
                    {'health_threshold': 0.9, 'behavior': 'awakening', 'special_ability': 'time_slow'},
                    {'health_threshold': 0.7, 'behavior': 'elemental_form', 'special_ability': 'elemental_storm'},
                    {'health_threshold': 0.4, 'behavior': 'berserker', 'special_ability': 'reality_break'},
                    {'health_threshold': 0.1, 'behavior': 'final_stand', 'special_ability': 'world_end'}
                ],
                'final_boss': [
                    {'health_threshold': 0.95, 'behavior': 'testing', 'special_ability': 'power_test'},
                    {'health_threshold': 0.8, 'behavior': 'serious', 'special_ability': 'dimension_shift'},
                    {'health_threshold': 0.6, 'behavior': 'awakened', 'special_ability': 'reality_control'},
                    {'health_threshold': 0.3, 'behavior': 'transcended', 'special_ability': 'existence_erase'},
                    {'health_threshold': 0.1, 'behavior': 'true_form', 'special_ability': 'creation_destroy'}
                ]
            }
        
        if self.minion_spawns_by_type is None:
            self.minion_spawns_by_type = {
                'mini_boss': [
                    {'enemy_type': 'goblin', 'count': 3, 'health_threshold': 0.3}
                ],
                'area_boss': [
                    {'enemy_type': 'dragon_spawn', 'count': 2, 'health_threshold': 0.5}
                ],
                'dungeon_boss': [
                    {'enemy_type': 'shadow_warrior', 'count': 4, 'health_threshold': 0.7},
                    {'enemy_type': 'undead_knight', 'count': 2, 'health_threshold': 0.4}
                ],
                'world_boss': [
                    {'enemy_type': 'elemental_guardian', 'count': 6, 'health_threshold': 0.8},
                    {'enemy_type': 'time_wraith', 'count': 3, 'health_threshold': 0.6},
                    {'enemy_type': 'reality_shard', 'count': 2, 'health_threshold': 0.3}
                ],
                'final_boss': [
                    {'enemy_type': 'creation_fragment', 'count': 8, 'health_threshold': 0.9},
                    {'enemy_type': 'existence_shard', 'count': 5, 'health_threshold': 0.7},
                    {'enemy_type': 'reality_echo', 'count': 3, 'health_threshold': 0.5},
                    {'enemy_type': 'true_form_manifestation', 'count': 2, 'health_threshold': 0.2}
                ]
            }
        
        if self.spawn_conditions is None:
            self.spawn_conditions = {
                'mini_boss': {
                    'biomes': [GenerationBiome.FOREST, GenerationBiome.CAVE],
                    'requirements': ['defeat_enemies'],
                    'time_limit': 300
                },
                'area_boss': {
                    'biomes': [GenerationBiome.MOUNTAIN, GenerationBiome.VOLCANO],
                    'requirements': ['explore_area', 'collect_items'],
                    'time_limit': 600
                },
                'dungeon_boss': {
                    'biomes': [GenerationBiome.DUNGEON, GenerationBiome.SWAMP],
                    'requirements': ['defeat_mini_bosses', 'collect_artifacts'],
                    'time_limit': 900
                },
                'world_boss': {
                    'biomes': [GenerationBiome.ARCTIC, GenerationBiome.OCEAN],
                    'requirements': ['complete_quests', 'gather_power'],
                    'time_limit': 1800
                },
                'final_boss': {
                    'biomes': [GenerationBiome.VOLCANO, GenerationBiome.DUNGEON],
                    'requirements': ['complete_all_content', 'achieve_transcendence'],
                    'time_limit': 3600
                }
            }

@dataclass
class ItemGenerationConstants:
    """Константы генерации предметов"""
    
    # Базовые характеристики по типам
    base_stats_by_type: Dict[str, Dict[str, Any]] = None
    
    # Модификаторы уровня
    level_multipliers: Dict[str, float] = None
    
    # Веса редкости по типам
    rarity_weights_by_type: Dict[str, GenerationWeights] = None
    
    # Префиксы и суффиксы по типам
    prefixes_by_type: Dict[str, List[str]] = None
    suffixes_by_type: Dict[str, List[str]] = None
    
    # Модификаторы характеристик по редкости
    stat_modifiers_by_rarity: Dict[str, Dict[str, float]] = None
    
    def __post_init__(self):
        if self.base_stats_by_type is None:
            self.base_stats_by_type = {
                'weapon': {
                    'damage': 15, 'attack_speed': 1.2, 'durability': 100,
                    'weight': 1.0, 'range': 1.0
                },
                'armor': {
                    'armor_value': 8, 'weight': 2, 'durability': 100,
                    'magic_resistance': 0
                },
                'accessory': {
                    'bonus': 5, 'magical_power': 20
                },
                'consumable': {
                    'potency': 1.0, 'duration': 60, 'stack_size': 3
                }
            }
        
        if self.level_multipliers is None:
            self.level_multipliers = {
                'damage': 0.1,
                'armor_value': 0.1,
                'bonus': 0.05,
                'potency': 0.05
            }
        
        if self.rarity_weights_by_type is None:
            self.rarity_weights_by_type = {
                'weapon': GenerationWeights(0.4, 0.3, 0.2, 0.08, 0.02),
                'armor': GenerationWeights(0.5, 0.3, 0.15, 0.04, 0.01),
                'accessory': GenerationWeights(0.3, 0.4, 0.25, 0.04, 0.01),
                'consumable': GenerationWeights(0.7, 0.25, 0.04, 0.01, 0.0)
            }
        
        if self.prefixes_by_type is None:
            self.prefixes_by_type = {
                'weapon': ['Sharp', 'Heavy', 'Swift', 'Mighty', 'Ancient', 'Mystic'],
                'armor': ['Sturdy', 'Light', 'Reinforced', 'Enchanted', 'Blessed', 'Cursed'],
                'accessory': ['Magical', 'Protective', 'Enhancing', 'Mystical', 'Divine', 'Infernal'],
                'consumable': ['Pure', 'Enhanced', 'Concentrated', 'Blessed', 'Cursed', 'Legendary']
            }
        
        if self.suffixes_by_type is None:
            self.suffixes_by_type = {
                'weapon': ['of Power', 'of Speed', 'of Destruction', 'of the Warrior', 'of the Mage'],
                'armor': ['of Protection', 'of Agility', 'of the Guardian', 'of the Sage', 'of the Hero'],
                'accessory': ['of Wisdom', 'of Strength', 'of the Mind', 'of the Soul', 'of the Ancients'],
                'consumable': ['of Healing', 'of Power', 'of Restoration', 'of the Gods', 'of Eternity']
            }
        
        if self.stat_modifiers_by_rarity is None:
            self.stat_modifiers_by_rarity = {
                'common': {'multiplier': 1.0, 'bonus': 0},
                'uncommon': {'multiplier': 1.2, 'bonus': 2},
                'rare': {'multiplier': 1.5, 'bonus': 5},
                'epic': {'multiplier': 2.0, 'bonus': 10},
                'legendary': {'multiplier': 3.0, 'bonus': 20}
            }

class AdvancedRandomGenerator:
    """Продвинутый генератор случайных чисел с весами и ограничениями"""
    
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        self.generation_history = []
    
    def weighted_choice(self, choices: List[Any], weights: List[float]) -> Any:
        """Выбор элемента с учетом весов"""
        if len(choices) != len(weights):
            raise ValueError("Количество элементов и весов должно совпадать")
        
        total_weight = sum(weights)
        if total_weight <= 0:
            return random.choice(choices)
        
        rand = random.uniform(0, total_weight)
        cumulative = 0
        
        for choice, weight in zip(choices, weights):
            cumulative += weight
            if rand <= cumulative:
                return choice
        
        return choices[-1]
    
    def weighted_choice_with_rarity(self, choices: List[Any], rarity_weights: GenerationWeights) -> Tuple[Any, str]:
        """Выбор элемента с учетом редкости"""
        weights = [
            rarity_weights.common,
            rarity_weights.uncommon,
            rarity_weights.rare,
            rarity_weights.epic,
            rarity_weights.legendary
        ]
        
        rarity_names = ['common', 'uncommon', 'rare', 'epic', 'legendary']
        chosen_rarity = self.weighted_choice(rarity_names, weights)
        
        # Фильтруем выборы по редкости
        filtered_choices = [c for c in choices if getattr(c, 'rarity', 'common') == chosen_rarity]
        
        if not filtered_choices:
            filtered_choices = choices
        
        chosen_item = random.choice(filtered_choices)
        return chosen_item, chosen_rarity
    
    def gaussian_modifier(self, mean: float = 1.0, std: float = 0.1, min_val: float = 0.5, max_val: float = 1.5) -> float:
        """Генерация модификатора по нормальному распределению"""
        modifier = random.gauss(mean, std)
        return max(min_val, min(max_val, modifier))
    
    def exponential_modifier(self, base: float = 1.0, rate: float = 0.5, max_val: float = 2.0) -> float:
        """Генерация модификатора по экспоненциальному распределению"""
        modifier = base * (1 + random.expovariate(rate))
        return min(max_val, modifier)
    
    def triangular_modifier(self, low: float = 0.8, high: float = 1.2, mode: float = 1.0) -> float:
        """Генерация модификатора по треугольному распределению"""
        return random.triangular(low, high, mode)
    
    def constrained_random_int(self, min_val: int, max_val: int, constraints: Dict[str, Any] = None) -> int:
        """Генерация случайного целого с ограничениями"""
        if constraints is None:
            return random.randint(min_val, max_val)
        
        # Применяем ограничения
        if 'prefer_low' in constraints and constraints['prefer_low']:
            # Предпочитаем низкие значения
            weights = [1.0 / (i + 1) for i in range(max_val - min_val + 1)]
            return self.weighted_choice(range(min_val, max_val + 1), weights)
        
        if 'prefer_high' in constraints and constraints['prefer_high']:
            # Предпочитаем высокие значения
            weights = [i + 1 for i in range(max_val - min_val + 1)]
            return self.weighted_choice(range(min_val, max_val + 1), weights)
        
        if 'prefer_middle' in constraints and constraints['prefer_middle']:
            # Предпочитаем средние значения
            middle = (min_val + max_val) // 2
            weights = [1.0 / (abs(i - middle) + 1) for i in range(min_val, max_val + 1)]
            return self.weighted_choice(range(min_val, max_val + 1), weights)
        
        return random.randint(min_val, max_val)
    
    def generate_name(self, base_name: str, prefix_chance: float = 0.3, suffix_chance: float = 0.3) -> str:
        """Генерация имени предмета с префиксом и суффиксом"""
        name_parts = [base_name]
        
        if random.random() < prefix_chance:
            # Здесь можно добавить логику выбора префикса
            pass
        
        if random.random() < suffix_chance:
            # Здесь можно добавить логику выбора суффикса
            pass
        
        return ' '.join(name_parts)
    
    def record_generation(self, item_type: str, rarity: str, level: int, stats: Dict[str, Any]):
        """Запись информации о генерации для анализа"""
        self.generation_history.append({
            'type': item_type,
            'rarity': rarity,
            'level': level,
            'stats': stats,
            'timestamp': time.time()
        })
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Получение статистики генерации"""
        if not self.generation_history:
            return {}
        
        stats = {}
        for item in self.generation_history:
            item_type = item['type']
            rarity = item['rarity']
            
            if item_type not in stats:
                stats[item_type] = {}
            
            if rarity not in stats[item_type]:
                stats[item_type][rarity] = 0
            
            stats[item_type][rarity] += 1
        
        return stats

# Глобальные экземпляры констант
ENEMY_CONSTANTS = EnemyGenerationConstants()
BOSS_CONSTANTS = BossGenerationConstants()
ITEM_CONSTANTS = ItemGenerationConstants()

# Глобальный генератор случайных чисел
RANDOM_GENERATOR = AdvancedRandomGenerator()
