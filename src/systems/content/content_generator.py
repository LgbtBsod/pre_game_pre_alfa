#!/usr/bin/env python3
"""
Система генерации контента - процедурная генерация игрового контента
"""

import logging
import random
import time
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from core.interfaces import ISystem, SystemPriority, SystemState
from core.constants import constants_manager, (
    ItemType, ItemRarity, WeaponType, ArmorType, AccessoryType, ConsumableType,
    DamageType, StatType, SkillType, SkillCategory, GeneType, GeneRarity, EffectCategory,
    EnemyType, BossType, ContentType, ContentRarity,
    BASE_STATS, ITEM_STATS, TOUGHNESS_MECHANICS, ENEMY_WEAKNESSES,
    PROBABILITY_CONSTANTS, TIME_CONSTANTS, SYSTEM_LIMITS,
    SKILL_GENERATION_TEMPLATES, SKILL_POWER_MULTIPLIERS
)

logger = logging.getLogger(__name__)

@dataclass
class GenerationConfig:
    """Конфигурация генерации контента"""
    weapon_count: int = 5
    armor_count: int = 3
    accessory_count: int = 2
    consumable_count: int = 4
    gene_count: int = 8
    skill_count: int = 6
    effect_count: int = 4
    material_count: int = 10
    enemy_count: int = 15
    boss_count: int = 3

@dataclass
class ContentItem:
    """Элемент контента"""
    item_id: str
    name: str
    description: str
    content_type: ContentType
    rarity: ContentRarity
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    level_requirement: int = 1
    session_id: str = ""
    generation_time: float = field(default_factory=time.time)
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EnemyData:
    """Данные врага"""
    enemy_id: str
    name: str
    enemy_type: EnemyType
    level: int = 1
    health: int = 100
    attack: int = 20
    defense: int = 10
    speed: float = 1.0
    experience: int = 50
    loot_table: List[str] = field(default_factory=list)
    abilities: List[str] = field(default_factory=list)

@dataclass
class BossData:
    """Данные босса"""
    boss_id: str
    name: str
    boss_type: BossType
    level: int = 10
    health: int = 1000
    attack: int = 100
    defense: int = 50
    speed: float = 1.5
    experience: int = 500
    phases: List[Dict[str, Any]] = field(default_factory=list)
    special_abilities: List[str] = field(default_factory=list)
    loot_table: List[str] = field(default_factory=list)

class ContentGenerator(ISystem):
    """Система генерации процедурного контента с использованием централизованных констант"""
    
    def __init__(self, content_database=None, seed: int = None):
        self._system_name = "content_generator"
        self._system_priority = SystemPriority.NORMAL
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = ["content_database"]
        
        self.content_db = content_database
        self.random_generator = random.Random(seed) if seed is not None else random
        
        # Шаблоны для генерации
        self.weapon_templates = self._load_weapon_templates()
        self.armor_templates = self._load_armor_templates()
        self.accessory_templates = self._load_accessory_templates()
        self.gene_templates = self._load_gene_templates()
        self.skill_templates = self._load_skill_templates()
        self.effect_templates = self._load_effect_templates()
        
        # Шаблоны предметов (перенесены из constants.py)
        self.item_templates = self._load_item_templates()
        
        # Расширенные шаблоны для уникальной генерации
        self.skill_generation_templates = self._load_skill_generation_templates()
        self.item_generation_templates = self._load_item_generation_templates()
        self.unique_effect_templates = self._load_unique_effect_templates()
        
        # Статистика системы
        self.system_stats = {
            'weapons_generated': 0,
            'armors_generated': 0,
            'accessories_generated': 0,
            'consumables_generated': 0,
            'genes_generated': 0,
            'skills_generated': 0,
            'effects_generated': 0,
            'materials_generated': 0,
            'enemies_generated': 0,
            'bosses_generated': 0,
            'total_generated': 0,
            'generation_time': 0.0,
            'update_time': 0.0
        }
        
        logger.info("Система генерации контента инициализирована")
    
    @property
    def system_name(self) -> str:
        return self._system_name
    
    @property
    def system_priority(self) -> SystemPriority:
        return self._system_priority
    
    @property
    def system_state(self) -> SystemState:
        return self._system_state
    
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    
    def initialize(self) -> bool:
        """Инициализация системы генерации контента"""
        try:
            logger.info("Инициализация системы генерации контента...")
            
            # Настраиваем систему
            self._setup_content_generator()
            
            # Загружаем шаблоны
            self._load_all_templates()
            
            self._system_state = SystemState.READY
            logger.info("Система генерации контента успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы генерации контента: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы генерации контента"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем статистику системы
            self._update_system_stats()
            
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы генерации контента: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы генерации контента"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система генерации контента приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы генерации контента: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы генерации контента"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система генерации контента возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы генерации контента: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы генерации контента"""
        try:
            logger.info("Очистка системы генерации контента...")
            
            # Очищаем все данные
            self.weapon_templates.clear()
            self.armor_templates.clear()
            self.accessory_templates.clear()
            self.gene_templates.clear()
            self.skill_templates.clear()
            self.effect_templates.clear()
            self.skill_generation_templates.clear()
            self.item_generation_templates.clear()
            self.unique_effect_templates.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'weapons_generated': 0,
                'armors_generated': 0,
                'accessories_generated': 0,
                'consumables_generated': 0,
                'genes_generated': 0,
                'skills_generated': 0,
                'effects_generated': 0,
                'materials_generated': 0,
                'enemies_generated': 0,
                'bosses_generated': 0,
                'total_generated': 0,
                'generation_time': 0.0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система генерации контента очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы генерации контента: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'templates_loaded': {
                'weapons': len(self.weapon_templates),
                'armors': len(self.armor_templates),
                'accessories': len(self.accessory_templates),
                'genes': len(self.gene_templates),
                'skills': len(self.skill_templates),
                'effects': len(self.effect_templates)
            },
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "content_generation_requested":
                return self._handle_content_generation_requested(event_data)
            elif event_type == "template_updated":
                return self._handle_template_updated(event_data)
            elif event_type == "generation_config_changed":
                return self._handle_generation_config_changed(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def _setup_content_generator(self) -> None:
        """Настройка системы генерации контента"""
        try:
            # Инициализируем базовые настройки
            logger.debug("Система генерации контента настроена")
        except Exception as e:
            logger.warning(f"Не удалось настроить систему генерации контента: {e}")
    
    def _load_all_templates(self) -> None:
        """Загрузка всех шаблонов"""
        try:
            # Загружаем базовые шаблоны
            self.weapon_templates = self._load_weapon_templates()
            self.armor_templates = self._load_armor_templates()
            self.accessory_templates = self._load_accessory_templates()
            self.gene_templates = self._load_gene_templates()
            self.skill_templates = self._load_skill_templates()
            self.effect_templates = self._load_effect_templates()
            
            # Загружаем шаблоны предметов
            self.item_templates = self._load_item_templates()
            
            # Загружаем расширенные шаблоны
            self.skill_generation_templates = self._load_skill_generation_templates()
            self.item_generation_templates = self._load_item_generation_templates()
            self.unique_effect_templates = self._load_unique_effect_templates()
            
            logger.info("Все шаблоны загружены")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов: {e}")
    
    def _load_weapon_templates(self) -> Dict[str, Any]:
        """Загрузка шаблонов оружия"""
        try:
            templates = {
                'sword': {
                    'base_damage': BASE_STATS['attack'],
                    'damage_type': DamageType.PHYSICAL,
                    'requirements': {'level': 1, 'strength': 5},
                    'scaling': {'strength': 1.5, 'agility': 0.5}
                },
                'axe': {
                    'base_damage': int(BASE_STATS['attack'] * 1.2),
                    'damage_type': DamageType.PHYSICAL,
                    'requirements': {'level': 1, 'strength': 8},
                    'scaling': {'strength': 2.0, 'agility': 0.3}
                },
                'bow': {
                    'base_damage': int(BASE_STATS['attack'] * 0.8),
                    'damage_type': DamageType.PHYSICAL,
                    'requirements': {'level': 1, 'agility': 6},
                    'scaling': {'agility': 1.8, 'strength': 0.2}
                },
                'staff': {
                    'base_damage': int(BASE_STATS['attack'] * 0.7),
                    'damage_type': DamageType.ARCANE,
                    'requirements': {'level': 1, 'intelligence': 7},
                    'scaling': {'intelligence': 2.2, 'wisdom': 0.8}
                }
            }
            
            logger.debug(f"Загружено {len(templates)} шаблонов оружия")
            return templates
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов оружия: {e}")
            return {}
    
    def _load_armor_templates(self) -> Dict[str, Any]:
        """Загрузка шаблонов брони"""
        try:
            templates = {
                'light_armor': {
                    'base_defense': int(BASE_STATS['defense'] * 0.8),
                    'requirements': {'level': 1, 'agility': 4},
                    'scaling': {'agility': 1.2, 'vitality': 0.8}
                },
                'medium_armor': {
                    'base_defense': BASE_STATS['defense'],
                    'requirements': {'level': 1, 'strength': 6, 'agility': 3},
                    'scaling': {'strength': 1.0, 'agility': 1.0, 'vitality': 1.0}
                },
                'heavy_armor': {
                    'base_defense': int(BASE_STATS['defense'] * 1.3),
                    'requirements': {'level': 1, 'strength': 8},
                    'scaling': {'strength': 1.5, 'vitality': 1.2}
                }
            }
            
            logger.debug(f"Загружено {len(templates)} шаблонов брони")
            return templates
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов брони: {e}")
            return {}
    
    def _load_accessory_templates(self) -> Dict[str, Any]:
        """Загрузка шаблонов аксессуаров"""
        try:
            templates = {
                'ring': {
                    'base_stats': {'mana': 20, 'health': 15},
                    'requirements': {'level': 1},
                    'scaling': {'intelligence': 0.5, 'vitality': 0.5}
                },
                'amulet': {
                    'base_stats': {'mana': 30, 'health': 25},
                    'requirements': {'level': 1},
                    'scaling': {'wisdom': 0.8, 'vitality': 0.7}
                },
                'belt': {
                    'base_stats': {'stamina': 25, 'defense': 5},
                    'requirements': {'level': 1, 'strength': 3},
                    'scaling': {'strength': 0.6, 'vitality': 0.8}
                }
            }
            
            logger.debug(f"Загружено {len(templates)} шаблонов аксессуаров")
            return templates
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов аксессуаров: {e}")
            return {}
    
    def _load_gene_templates(self) -> Dict[str, Any]:
        """Загрузка шаблонов генов"""
        try:
            templates = {
                'strength_gene': {
                    'gene_type': GeneType.STRENGTH,
                    'rarity': GeneRarity.COMMON,
                    'base_effect': {'strength': 2},
                    'scaling': {'level': 0.5}
                },
                'agility_gene': {
                    'gene_type': GeneType.AGILITY,
                    'rarity': GeneRarity.COMMON,
                    'base_effect': {'agility': 2},
                    'scaling': {'level': 0.5}
                },
                'intelligence_gene': {
                    'gene_type': GeneType.INTELLIGENCE,
                    'rarity': GeneRarity.COMMON,
                    'base_effect': {'intelligence': 2},
                    'scaling': {'level': 0.5}
                },
                'vitality_gene': {
                    'gene_type': GeneType.VITALITY,
                    'rarity': GeneRarity.COMMON,
                    'base_effect': {'vitality': 2},
                    'scaling': {'level': 0.5}
                }
            }
            
            logger.debug(f"Загружено {len(templates)} шаблонов генов")
            return templates
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов генов: {e}")
            return {}
    
    def _load_skill_templates(self) -> Dict[str, Any]:
        """Загрузка шаблонов навыков"""
        try:
            templates = {
                'basic_attack': {
                    'skill_type': SkillType.ATTACK,
                    'category': SkillCategory.COMBAT,
                    'base_damage': 25,
                    'damage_type': DamageType.PHYSICAL,
                    'requirements': {'level': 1},
                    'scaling': {'strength': 1.0, 'agility': 0.5}
                },
                'fireball': {
                    'skill_type': SkillType.ATTACK,
                    'category': SkillCategory.MAGIC,
                    'base_damage': 30,
                    'damage_type': DamageType.FIRE,
                    'requirements': {'level': 3, 'intelligence': 8},
                    'scaling': {'intelligence': 1.5, 'wisdom': 0.8}
                },
                'heal': {
                    'skill_type': SkillType.SUPPORT,
                    'category': SkillCategory.HEALING,
                    'base_healing': 40,
                    'requirements': {'level': 2, 'wisdom': 6},
                    'scaling': {'wisdom': 1.8, 'intelligence': 0.7}
                }
            }
            
            logger.debug(f"Загружено {len(templates)} шаблонов навыков")
            return templates
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов навыков: {e}")
            return {}
    
    def _load_effect_templates(self) -> Dict[str, Any]:
        """Загрузка шаблонов эффектов"""
        try:
            templates = {
                'poison': {
                    'effect_category': EffectCategory.DEBUFF,
                    'base_damage': 5,
                    'damage_type': DamageType.POISON,
                    'duration': 10.0,
                    'scaling': {'intelligence': 0.3}
                },
                'regeneration': {
                    'effect_category': EffectCategory.BUFF,
                    'base_healing': 8,
                    'duration': 15.0,
                    'scaling': {'wisdom': 0.4}
                },
                'speed_boost': {
                    'effect_category': EffectCategory.BUFF,
                    'base_boost': 0.2,
                    'duration': 20.0,
                    'scaling': {'agility': 0.1}
                }
            }
            
            logger.debug(f"Загружено {len(templates)} шаблонов эффектов")
            return templates
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов эффектов: {e}")
            return {}
    
    def _load_skill_generation_templates(self) -> Dict[str, Any]:
        """Загрузка шаблонов генерации навыков"""
        try:
            templates = {
                'combat_skill': {
                    'skill_type': SkillType.ATTACK,
                    'category': SkillCategory.COMBAT,
                    'damage_types': [DamageType.PHYSICAL, DamageType.FIRE, DamageType.ICE],
                    'scaling_stats': ['strength', 'agility', 'intelligence']
                },
                'magic_skill': {
                    'skill_type': SkillType.ATTACK,
                    'category': SkillCategory.MAGIC,
                    'damage_types': [DamageType.FIRE, DamageType.ICE, DamageType.LIGHTNING, DamageType.ARCANE],
                    'scaling_stats': ['intelligence', 'wisdom']
                },
                'support_skill': {
                    'skill_type': SkillType.SUPPORT,
                    'category': SkillCategory.HEALING,
                    'effect_types': ['healing', 'buff', 'debuff'],
                    'scaling_stats': ['wisdom', 'intelligence']
                }
            }
            
            logger.debug(f"Загружено {len(templates)} шаблонов генерации навыков")
            return templates
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов генерации навыков: {e}")
            return {}
    
    def _load_item_generation_templates(self) -> Dict[str, Any]:
        """Загрузка шаблонов генерации предметов"""
        try:
            templates = {
                'weapon': {
                    'item_type': ItemType.WEAPON,
                    'categories': [WeaponType.SWORD, WeaponType.AXE, WeaponType.BOW, WeaponType.STAFF],
                    'rarity_weights': {
                        ItemRarity.COMMON: 0.6,
                        ItemRarity.UNCOMMON: 0.25,
                        ItemRarity.RARE: 0.1,
                        ItemRarity.EPIC: 0.04,
                        ItemRarity.LEGENDARY: 0.01
                    }
                },
                'armor': {
                    'item_type': ItemType.ARMOR,
                    'categories': [ArmorType.HELMET, ArmorType.CHESTPLATE, ArmorType.GREAVES],
                    'rarity_weights': {
                        ItemRarity.COMMON: 0.6,
                        ItemRarity.UNCOMMON: 0.25,
                        ItemRarity.RARE: 0.1,
                        ItemRarity.EPIC: 0.04,
                        ItemRarity.LEGENDARY: 0.01
                    }
                },
                'accessory': {
                    'item_type': ItemType.ACCESSORY,
                    'categories': [AccessoryType.RING, AccessoryType.AMULET, AccessoryType.BELT],
                    'rarity_weights': {
                        ItemRarity.COMMON: 0.5,
                        ItemRarity.UNCOMMON: 0.3,
                        ItemRarity.RARE: 0.15,
                        ItemRarity.EPIC: 0.04,
                        ItemRarity.LEGENDARY: 0.01
                    }
                }
            }
            
            logger.debug(f"Загружено {len(templates)} шаблонов генерации предметов")
            return templates
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов генерации предметов: {e}")
            return {}
    
    def _load_unique_effect_templates(self) -> Dict[str, Any]:
        """Загрузка шаблонов уникальных эффектов"""
        try:
            templates = {
                'elemental_mastery': {
                    'effect_category': EffectCategory.BUFF,
                    'damage_boost': 0.3,
                    'affected_types': [DamageType.FIRE, DamageType.ICE, DamageType.LIGHTNING],
                    'requirements': {'level': 10, 'intelligence': 15}
                },
                'battle_fury': {
                    'effect_category': EffectCategory.BUFF,
                    'attack_boost': 0.4,
                    'speed_boost': 0.2,
                    'requirements': {'level': 8, 'strength': 12}
                },
                'shadow_step': {
                    'effect_category': EffectCategory.BUFF,
                    'stealth_duration': 5.0,
                    'damage_multiplier': 2.0,
                    'requirements': {'level': 12, 'agility': 18}
                }
            }
            
            logger.debug(f"Загружено {len(templates)} шаблонов уникальных эффектов")
            return templates
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов уникальных эффектов: {e}")
            return {}
    
    def _load_item_templates(self) -> Dict[str, Any]:
        """Загрузка шаблонов предметов (перенесено из constants.py)"""
        try:
            templates = {
                "weapon": {
                    "sword": {
                        "name": "Меч",
                        "base_multipliers": {
                            "attack": 1.2,
                            "speed": 1.0,
                            "critical_chance": 1.1,
                            "toughness_damage": 0.8,
                            "break_efficiency": 1.0,
                        },
                        "preferred_damage_types": [DamageType.PHYSICAL, DamageType.PIERCING],
                        "skill_requirements": ["strength", "agility"],
                    },
                    "axe": {
                        "name": "Топор",
                        "base_multipliers": {
                            "attack": 1.5,
                            "speed": 0.8,
                            "critical_multiplier": 1.3,
                            "toughness_damage": 1.2,
                            "break_efficiency": 1.5,
                        },
                        "preferred_damage_types": [DamageType.PHYSICAL],
                        "skill_requirements": ["strength"],
                    },
                    "bow": {
                        "name": "Лук",
                        "base_multipliers": {
                            "attack": 1.0,
                            "speed": 1.5,
                            "range": 3.0,
                            "critical_chance": 1.3,
                            "toughness_damage": 0.6,
                            "break_efficiency": 0.8,
                        },
                        "preferred_damage_types": [DamageType.PHYSICAL, DamageType.PIERCING],
                        "skill_requirements": ["agility", "dexterity"],
                    },
                    "staff": {
                        "name": "Посох",
                        "base_multipliers": {
                            "attack": 0.8,
                            "mana": 1.5,
                            "intelligence": 1.2,
                            "magic_resistance": 1.1,
                            "toughness_damage": 0.5,
                            "break_efficiency": 0.7,
                        },
                        "preferred_damage_types": [DamageType.MAGIC, DamageType.ARCANE],
                        "skill_requirements": ["intelligence", "wisdom"],
                    },
                },
                "armor": {
                    "plate": {
                        "name": "Пластинчатая броня",
                        "base_multipliers": {
                            "defense": 2.0,
                            "health": 1.5,
                            "weight": 2.0,
                            "movement_penalty": 1.5,
                            "toughness_resistance": 1.8,
                            "stun_resistance": 1.5,
                        },
                        "preferred_resistances": [DamageType.PHYSICAL, DamageType.PIERCING],
                        "skill_requirements": ["strength", "constitution"],
                    },
                    "leather": {
                        "name": "Кожаная броня",
                        "base_multipliers": {
                            "defense": 0.8,
                            "speed": 1.3,
                            "agility": 1.2,
                            "weight": 0.6,
                            "movement_penalty": 0.8,
                            "toughness_resistance": 0.7,
                            "stun_resistance": 0.9,
                        },
                        "preferred_resistances": [DamageType.PHYSICAL],
                        "skill_requirements": ["agility", "dexterity"],
                    },
                    "cloth": {
                        "name": "Тканевая броня",
                        "base_multipliers": {
                            "defense": 0.5,
                            "mana": 1.8,
                            "intelligence": 1.3,
                            "magic_resistance": 1.5,
                            "weight": 0.3,
                            "movement_penalty": 0.5,
                            "toughness_resistance": 0.5,
                            "stun_resistance": 0.7,
                        },
                        "preferred_resistances": [DamageType.MAGIC, DamageType.ARCANE],
                        "skill_requirements": ["intelligence", "wisdom"],
                    },
                },
                "accessory": {
                    "ring": {
                        "name": "Кольцо",
                        "base_multipliers": {
                            "intelligence": 1.2,
                            "strength": 1.2,
                            "agility": 1.2,
                            "constitution": 1.2,
                            "wisdom": 1.2,
                            "charisma": 1.2,
                            "luck": 1.3,
                        },
                        "socket_count": 1,
                        "set_bonus": None,
                    },
                    "necklace": {
                        "name": "Ожерелье",
                        "base_multipliers": {
                            "intelligence": 1.5,
                            "wisdom": 1.3,
                            "charisma": 1.4,
                            "mana": 1.2,
                        },
                        "socket_count": 2,
                        "set_bonus": None,
                    },
                    "amulet": {
                        "name": "Амулет",
                        "base_multipliers": {
                            "strength": 1.5,
                            "constitution": 1.3,
                            "health": 1.2,
                            "stamina": 1.2,
                        },
                        "socket_count": 1,
                        "set_bonus": None,
                    },
                },
            }
            
            logger.debug(f"Загружено {len(templates)} шаблонов предметов")
            return templates
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов предметов: {e}")
            return {}
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            # Обновляем общее количество сгенерированных элементов
            self.system_stats['total_generated'] = (
                self.system_stats['weapons_generated'] +
                self.system_stats['armors_generated'] +
                self.system_stats['accessories_generated'] +
                self.system_stats['consumables_generated'] +
                self.system_stats['genes_generated'] +
                self.system_stats['skills_generated'] +
                self.system_stats['effects_generated'] +
                self.system_stats['materials_generated'] +
                self.system_stats['enemies_generated'] +
                self.system_stats['bosses_generated']
            )
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_content_generation_requested(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события запроса генерации контента"""
        try:
            content_type = event_data.get('content_type')
            count = event_data.get('count', 1)
            level = event_data.get('level', 1)
            
            if content_type:
                # Генерируем контент
                generated_items = self.generate_content(content_type, count, level)
                
                # Отправляем событие о завершении генерации
                # Здесь должна быть логика отправки событий
                
                logger.info(f"Сгенерировано {len(generated_items)} элементов типа {content_type}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события запроса генерации контента: {e}")
            return False
    
    def _handle_template_updated(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события обновления шаблона"""
        try:
            template_type = event_data.get('template_type')
            template_id = event_data.get('template_id')
            template_data = event_data.get('template_data')
            
            if template_type and template_id and template_data:
                # Обновляем соответствующий шаблон
                if template_type == 'weapon':
                    self.weapon_templates[template_id] = template_data
                elif template_type == 'armor':
                    self.armor_templates[template_id] = template_data
                elif template_type == 'skill':
                    self.skill_templates[template_id] = template_data
                # ... другие типы
                
                logger.debug(f"Обновлен шаблон {template_id} типа {template_type}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события обновления шаблона: {e}")
            return False
    
    def _handle_generation_config_changed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события изменения конфигурации генерации"""
        try:
            new_config = event_data.get('new_config')
            
            if new_config:
                # Обновляем настройки системы
                self.system_settings.update(new_config)
                
                logger.info("Обновлена конфигурация генерации контента")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события изменения конфигурации генерации: {e}")
            return False
    
    def generate_content(self, content_type: str, count: int = 1, level: int = 1) -> List[ContentItem]:
        """Генерация контента указанного типа"""
        try:
            generated_items = []
            
            for i in range(count):
                if content_type == 'weapon':
                    item = self._generate_weapon(level)
                elif content_type == 'armor':
                    item = self._generate_armor(level)
                elif content_type == 'accessory':
                    item = self._generate_accessory(level)
                elif content_type == 'gene':
                    item = self._generate_gene(level)
                elif content_type == 'skill':
                    item = self._generate_skill(level)
                elif content_type == 'effect':
                    item = self._generate_effect(level)
                elif content_type == 'enemy':
                    item = self._generate_enemy(level)
                elif content_type == 'boss':
                    item = self._generate_boss(level)
                else:
                    logger.warning(f"Неизвестный тип контента: {content_type}")
                    continue
                
                if item:
                    generated_items.append(item)
            
            # Обновляем статистику
            self._update_generation_stats(content_type, len(generated_items))
            
            return generated_items
            
        except Exception as e:
            logger.error(f"Ошибка генерации контента типа {content_type}: {e}")
            return []
    
    def _generate_weapon(self, level: int) -> Optional[ContentItem]:
        """Генерация оружия с улучшенной уникальностью"""
        try:
            # Выбираем случайный шаблон
            template_name = self.random_generator.choice(list(self.weapon_templates.keys()))
            template = self.weapon_templates[template_name]
            
            # Генерируем уникальный ID с временной меткой
            weapon_id = f"weapon_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            # Генерируем уникальное имя
            weapon_name = self._generate_unique_name(template_name, level)
            
            # Генерируем уникальные свойства
            base_damage = template['base_damage'] + (level - 1) * 5
            damage_variation = self.random_generator.uniform(0.8, 1.2)
            final_damage = int(base_damage * damage_variation)
            
            # Генерируем характеристики стойкости
            toughness_damage = max(10, final_damage // 2) + (level - 1) * 2
            break_efficiency = min(2.0, 1.0 + (level - 1) * 0.1)
            
            # Генерируем уникальные эффекты
            unique_effects = self._generate_unique_effects(level)
            
            # Создаем предмет с полными характеристиками
            weapon = ContentItem(
                item_id=weapon_id,
                name=weapon_name,
                description=self._generate_unique_description(template_name, level, unique_effects),
                content_type=ContentType.WEAPON,
                rarity=self._generate_rarity(),
                level_requirement=level,
                properties={
                    'base_damage': final_damage,
                    'damage_type': template['damage_type'].value,
                    'requirements': template['requirements'],
                    'scaling': template['scaling'],
                    'unique_effects': unique_effects,
                    'generation_seed': self.random_generator.randint(1, 1000000),
                    # Новые характеристики стойкости
                    'toughness_damage': toughness_damage,
                    'break_efficiency': break_efficiency,
                    'attack': final_damage // 2,
                    'speed': 1.0 + (level - 1) * 0.05,
                    'critical_chance': min(0.25, 0.05 + (level - 1) * 0.02),
                    'critical_multiplier': min(3.0, 2.0 + (level - 1) * 0.1)
                }
            )
            
            self.system_stats['weapons_generated'] += 1
            return weapon
            
        except Exception as e:
            logger.error(f"Ошибка генерации оружия: {e}")
            return None
    
    def _generate_skill_name(self, skill_type: str, level: int) -> str:
        """Генерация уникального имени для скилла"""
        prefixes = {
            "physical": ["Мощный", "Быстрый", "Смертоносный", "Точный", "Разрушительный"],
            "magical": ["Мистический", "Древний", "Запрещенный", "Священный", "Темный"],
            "free": ["Уникальный", "Редкий", "Легендарный", "Божественный", "Загадочный"]
        }
        
        suffixes = {
            "physical": ["Удар", "Атака", "Техника", "Прием", "Комбо"],
            "magical": ["Заклинание", "Ритуал", "Проклятие", "Благословение", "Чары"],
            "free": ["Дар", "Сила", "Способность", "Талант", "Мастерство"]
        }
        
        prefix = self.random_generator.choice(prefixes.get(skill_type, ["Мощный"]))
        suffix = self.random_generator.choice(suffixes.get(skill_type, ["Удар"]))
        
        return f"{prefix} {suffix} +{level}"
    
    def _generate_unique_name(self, base_name: str, level: int) -> str:
        """Генерация уникального имени"""
        prefixes = ['Ancient', 'Mystic', 'Shadow', 'Light', 'Dark', 'Elemental', 'Crystal', 'Obsidian']
        suffixes = ['Blade', 'Sword', 'Axe', 'Hammer', 'Staff', 'Wand', 'Bow', 'Crossbow']
        
        prefix = self.random_generator.choice(prefixes)
        suffix = self.random_generator.choice(suffixes)
        
        return f"{prefix} {base_name.title()} {suffix} +{level}"
    
    def _generate_unique_description(self, base_name: str, level: int, effects: list) -> str:
        """Генерация уникального описания"""
        descriptions = [
            f"Легендарное оружие, созданное древними мастерами. Уровень {level}.",
            f"Мистический артефакт, излучающий мощную энергию. Уровень {level}.",
            f"Оружие, закаленное в боях тысячелетий. Уровень {level}.",
            f"Священный клинок, благословленный богами. Уровень {level}."
        ]
        
        base_desc = self.random_generator.choice(descriptions)
        effects_desc = ""
        
        if effects:
            effects_desc = f" Особые свойства: {', '.join(effects)}."
        
        return base_desc + effects_desc
    
    def _generate_unique_effects(self, level: int) -> list:
        """Генерация уникальных эффектов"""
        effects = []
        effect_pool = [
            'Critical Strike', 'Life Steal', 'Mana Steal', 'Poison Damage',
            'Fire Damage', 'Ice Damage', 'Lightning Damage', 'Holy Damage',
            'Shadow Damage', 'Armor Penetration', 'Magic Penetration'
        ]
        
        # Количество эффектов зависит от уровня
        num_effects = min(level // 5 + 1, 3)
        
        for _ in range(num_effects):
            if self.random_generator.random() < 0.3:  # 30% шанс эффекта
                effect = self.random_generator.choice(effect_pool)
                if effect not in effects:
                    effects.append(effect)
        
        return effects
    
    def _generate_armor(self, level: int) -> Optional[ContentItem]:
        """Генерация брони"""
        try:
            # Выбираем случайный шаблон
            template_name = self.random_generator.choice(list(self.armor_templates.keys()))
            template = self.armor_templates[template_name]
            
            # Генерируем уникальный ID
            armor_id = f"armor_{uuid.uuid4().hex[:8]}"
            
            # Генерируем характеристики стойкости
            base_defense = template['base_defense'] + (level - 1) * 3
            toughness_resistance = min(0.5, 0.1 + (level - 1) * 0.05)
            stun_resistance = min(0.3, 0.05 + (level - 1) * 0.03)
            
            # Создаем предмет с полными характеристиками
            armor = ContentItem(
                item_id=armor_id,
                name=f"{template_name.title()} Level {level}",
                description=f"Сгенерированная броня типа {template_name}",
                content_type=ContentType.ARMOR,
                rarity=self._generate_rarity(),
                level_requirement=level,
                properties={
                    'base_defense': base_defense,
                    'requirements': template['requirements'],
                    'scaling': template['scaling'],
                    # Новые характеристики стойкости
                    'defense': base_defense,
                    'health': 20 + (level - 1) * 5,
                    'mana': 10 + (level - 1) * 3,
                    'stamina': 15 + (level - 1) * 4,
                    'toughness_resistance': toughness_resistance,
                    'stun_resistance': stun_resistance,
                    'resistance': {
                        'physical': min(0.3, 0.1 + (level - 1) * 0.02),
                        'fire': min(0.25, 0.05 + (level - 1) * 0.02),
                        'ice': min(0.25, 0.05 + (level - 1) * 0.02),
                        'lightning': min(0.25, 0.05 + (level - 1) * 0.02)
                    }
                }
            )
            
            self.system_stats['armors_generated'] += 1
            return armor
            
        except Exception as e:
            logger.error(f"Ошибка генерации брони: {e}")
            return None
    
    def _generate_accessory(self, level: int) -> Optional[ContentItem]:
        """Генерация аксессуара"""
        try:
            # Выбираем случайный шаблон
            template_name = self.random_generator.choice(list(self.accessory_templates.keys()))
            template = self.accessory_templates[template_name]
            
            # Генерируем уникальный ID
            accessory_id = f"accessory_{uuid.uuid4().hex[:8]}"
            
            # Генерируем характеристики
            stat_bonus = 2 + (level - 1) * 1
            special_effects = self._generate_accessory_effects(level)
            
            # Создаем предмет с полными характеристиками
            accessory = ContentItem(
                item_id=accessory_id,
                name=f"{template_name.title()} Level {level}",
                description=f"Сгенерированный аксессуар типа {template_name}",
                content_type=ContentType.ACCESSORY,
                rarity=self._generate_rarity(),
                level_requirement=level,
                properties={
                    'base_stats': template['base_stats'],
                    'requirements': template['requirements'],
                    'scaling': template['scaling'],
                    # Новые характеристики
                    'intelligence': stat_bonus,
                    'strength': stat_bonus,
                    'agility': stat_bonus,
                    'constitution': stat_bonus,
                    'wisdom': stat_bonus,
                    'charisma': stat_bonus,
                    'luck': stat_bonus,
                    'special_effects': special_effects
                }
            )
            
            self.system_stats['accessories_generated'] += 1
            return accessory
            
        except Exception as e:
            logger.error(f"Ошибка генерации аксессуара: {e}")
            return None
    
    def _generate_accessory_effects(self, level: int) -> list:
        """Генерация эффектов для аксессуаров"""
        effects = []
        effect_pool = [
            'Health Regeneration', 'Mana Regeneration', 'Stamina Regeneration',
            'Experience Boost', 'Gold Boost', 'Drop Rate Boost',
            'Movement Speed', 'Attack Speed', 'Cast Speed'
        ]
        
        # Количество эффектов зависит от уровня
        num_effects = min(level // 3 + 1, 2)
        
        for _ in range(num_effects):
            if self.random_generator.random() < 0.4:  # 40% шанс эффекта
                effect = self.random_generator.choice(effect_pool)
                if effect not in effects:
                    effects.append(effect)
        
        return effects
    
    def _generate_gene(self, level: int) -> Optional[ContentItem]:
        """Генерация гена"""
        try:
            # Выбираем случайный шаблон
            template_name = self.random_generator.choice(list(self.gene_templates.keys()))
            template = self.gene_templates[template_name]
            
            # Генерируем уникальный ID
            gene_id = f"gene_{uuid.uuid4().hex[:8]}"
            
            # Создаем предмет
            gene = ContentItem(
                item_id=gene_id,
                name=f"{template_name.title()} Level {level}",
                description=f"Сгенерированный ген типа {template_name}",
                content_type=ContentType.GENE,
                rarity=self._generate_rarity(),
                level_requirement=level,
                properties={
                    'gene_type': template['gene_type'].value,
                    'rarity': template['rarity'].value,
                    'base_effect': template['base_effect'],
                    'scaling': template['scaling']
                }
            )
            
            self.system_stats['genes_generated'] += 1
            return gene
            
        except Exception as e:
            logger.error(f"Ошибка генерации гена: {e}")
            return None
    
    def _generate_skill(self, level: int) -> Optional[ContentItem]:
        """Генерация навыка с использованием новых шаблонов"""
        try:
            # Выбираем случайный тип скилла
            skill_type = self.random_generator.choice(list(SKILL_GENERATION_TEMPLATES.keys()))
            template = SKILL_GENERATION_TEMPLATES[skill_type]
            
            # Генерируем уникальный ID
            skill_id = f"skill_{uuid.uuid4().hex[:8]}"
            
            # Определяем источники затрат
            if skill_type == "physical":
                cost_sources = ["stamina"]
                base_cost = template["base_cost"]
            elif skill_type == "magical":
                # Магические скиллы могут тратить несколько ресурсов
                cost_sources = self.random_generator.sample(template["cost_sources"], 
                                                         self.random_generator.randint(1, len(template["cost_sources"])))
                base_cost = template["base_cost"]
            else:  # free
                cost_sources = []
                base_cost = 0
            
            # Рассчитываем мощность скилла на основе источников затрат
            power_multiplier = 1.0
            if cost_sources:
                if len(cost_sources) == 1:
                    power_multiplier = SKILL_POWER_MULTIPLIERS["single_cost"]
                elif len(cost_sources) == 2:
                    power_multiplier = SKILL_POWER_MULTIPLIERS["dual_cost"]
                elif len(cost_sources) >= 3:
                    power_multiplier = SKILL_POWER_MULTIPLIERS["triple_cost"]
            else:
                power_multiplier = SKILL_POWER_MULTIPLIERS["no_cost"]
            
            # Генерируем характеристики скилла
            base_damage = int(template["base_cost"] * power_multiplier * level * 0.5)
            damage_type = self.random_generator.choice(template["damage_types"])
            
            # Генерируем уникальное имя
            skill_name = self._generate_skill_name(skill_type, level)
            
            # Создаем предмет
            skill = ContentItem(
                item_id=skill_id,
                name=skill_name,
                description=f"Сгенерированный {skill_type} навык уровня {level}",
                content_type=ContentType.SKILL,
                rarity=self._generate_rarity(),
                level_requirement=level,
                properties={
                    'skill_type': skill_type,
                    'cost_sources': cost_sources,
                    'base_cost': base_cost,
                    'power_multiplier': power_multiplier,
                    'base_damage': base_damage,
                    'damage_type': damage_type,
                    'preferred_stats': template["preferred_stats"],
                    'level': level
                }
            )
            
            self.system_stats['skills_generated'] += 1
            return skill
            
        except Exception as e:
            logger.error(f"Ошибка генерации навыка: {e}")
            return None
    
    def _generate_effect(self, level: int) -> Optional[ContentItem]:
        """Генерация эффекта"""
        try:
            # Выбираем случайный шаблон
            template_name = self.random_generator.choice(list(self.effect_templates.keys()))
            template = self.effect_templates[template_name]
            
            # Генерируем уникальный ID
            effect_id = f"effect_{uuid.uuid4().hex[:8]}"
            
            # Создаем предмет
            effect = ContentItem(
                item_id=effect_id,
                name=f"{template_name.title()} Level {level}",
                description=f"Сгенерированный эффект типа {template_name}",
                content_type=ContentType.EFFECT,
                rarity=self._generate_rarity(),
                level_requirement=level,
                properties={
                    'effect_category': template['effect_category'].value,
                    'base_damage': template.get('base_damage', 0),
                    'damage_type': template.get('damage_type', DamageType.PHYSICAL).value,
                    'duration': template['duration'],
                    'scaling': template['scaling']
                }
            )
            
            self.system_stats['effects_generated'] += 1
            return effect
            
        except Exception as e:
            logger.error(f"Ошибка генерации эффекта: {e}")
            return None
    
    def _generate_enemy(self, level: int) -> Optional[ContentItem]:
        """Генерация врага"""
        try:
            # Генерируем уникальный ID
            enemy_id = f"enemy_{uuid.uuid4().hex[:8]}"
            
            # Создаем предмет
            enemy = ContentItem(
                item_id=enemy_id,
                name=f"Enemy Level {level}",
                description=f"Сгенерированный враг уровня {level}",
                content_type=ContentType.ENEMY,
                rarity=self._generate_rarity(),
                level_requirement=level,
                properties={
                    'enemy_type': EnemyType.NORMAL.value,
                    'health': BASE_STATS['health'] + (level - 1) * 20,
                    'attack': BASE_STATS['attack'] + (level - 1) * 5,
                    'defense': BASE_STATS['defense'] + (level - 1) * 3,
                    'experience': 50 + (level - 1) * 25
                }
            )
            
            self.system_stats['enemies_generated'] += 1
            return enemy
            
        except Exception as e:
            logger.error(f"Ошибка генерации врага: {e}")
            return None
    
    def _generate_boss(self, level: int) -> Optional[ContentItem]:
        """Генерация босса"""
        try:
            # Генерируем уникальный ID
            boss_id = f"boss_{uuid.uuid4().hex[:8]}"
            
            # Создаем предмет
            boss = ContentItem(
                item_id=boss_id,
                name=f"Boss Level {level}",
                description=f"Сгенерированный босс уровня {level}",
                content_type=ContentType.BOSS,
                rarity=self._generate_rarity(),
                level_requirement=level,
                properties={
                    'boss_type': BossType.MINIBOSS.value,
                    'health': (BASE_STATS['health'] * 5) + (level - 1) * 100,
                    'attack': (BASE_STATS['attack'] * 2) + (level - 1) * 15,
                    'defense': (BASE_STATS['defense'] * 2) + (level - 1) * 10,
                    'experience': 500 + (level - 1) * 100
                }
            )
            
            self.system_stats['bosses_generated'] += 1
            return boss
            
        except Exception as e:
            logger.error(f"Ошибка генерации босса: {e}")
            return None
    
    def _generate_rarity(self) -> ContentRarity:
        """Генерация редкости"""
        try:
            # Используем веса для разных редкостей
            rarity_weights = {
                ContentRarity.COMMON: 0.6,
                ContentRarity.UNCOMMON: 0.25,
                ContentRarity.RARE: 0.1,
                ContentRarity.EPIC: 0.04,
                ContentRarity.LEGENDARY: 0.01
            }
            
            # Генерируем случайное число
            rand_value = self.random_generator.random()
            
            # Определяем редкость на основе весов
            cumulative_weight = 0.0
            for rarity, weight in rarity_weights.items():
                cumulative_weight += weight
                if rand_value <= cumulative_weight:
                    return rarity
            
            # По умолчанию возвращаем обычную редкость
            return ContentRarity.COMMON
            
        except Exception as e:
            logger.error(f"Ошибка генерации редкости: {e}")
            return ContentRarity.COMMON
    
    def _update_generation_stats(self, content_type: str, count: int) -> None:
        """Обновление статистики генерации"""
        try:
            # Обновляем соответствующий счетчик
            if content_type == 'weapon':
                self.system_stats['weapons_generated'] += count
            elif content_type == 'armor':
                self.system_stats['armors_generated'] += count
            elif content_type == 'accessory':
                self.system_stats['accessories_generated'] += count
            elif content_type == 'gene':
                self.system_stats['genes_generated'] += count
            elif content_type == 'skill':
                self.system_stats['skills_generated'] += count
            elif content_type == 'effect':
                self.system_stats['effects_generated'] += count
            elif content_type == 'enemy':
                self.system_stats['enemies_generated'] += count
            elif content_type == 'boss':
                self.system_stats['bosses_generated'] += count
            
            # Обновляем общее время генерации
            self.system_stats['generation_time'] = time.time()
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики генерации: {e}")
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Получение статистики генерации"""
        try:
            return self.system_stats.copy()
        except Exception as e:
            logger.error(f"Ошибка получения статистики генерации: {e}")
            return {}
    
    def apply_item_template(self, item_type: str, template_name: str, level: int = 1, rarity: str = "common") -> dict:
        """Применение шаблона предмета к базовым характеристикам"""
        if item_type not in self.item_templates or template_name not in self.item_templates[item_type]:
            return ITEM_STATS[item_type].copy()
        
        template = self.item_templates[item_type][template_name]
        item_stats = ITEM_STATS[item_type].copy()
        
        # Применяем множители из шаблона
        for stat, multiplier in template["base_multipliers"].items():
            if stat in item_stats:
                if isinstance(item_stats[stat], (int, float)):
                    item_stats[stat] = int(item_stats[stat] * multiplier * level)
        
        # Добавляем информацию о шаблоне
        item_stats["template_name"] = template_name
        item_stats["template_display_name"] = template["name"]
        item_stats["preferred_damage_types"] = template.get("preferred_damage_types", [])
        item_stats["preferred_resistances"] = template.get("preferred_resistances", [])
        item_stats["skill_requirements"] = template.get("skill_requirements", [])
        item_stats["socket_count"] = template.get("socket_count", 0)
        item_stats["set_bonus"] = template.get("set_bonus")
        
        # Применяем множитель редкости
        rarity_multipliers = {
            "common": 1.0,
            "uncommon": 1.2,
            "rare": 1.5,
            "epic": 2.0,
            "legendary": 3.0,
            "mythic": 4.0,
            "divine": 5.0,
        }
        
        rarity_mult = rarity_multipliers.get(rarity, 1.0)
        for stat in ["attack", "defense", "health", "mana", "stamina"]:
            if stat in item_stats and isinstance(item_stats[stat], (int, float)):
                item_stats[stat] = int(item_stats[stat] * rarity_mult)
        
        return item_stats
    
    def generate_session_content(self, session_id: str, config: GenerationConfig = None) -> Dict[str, List[ContentItem]]:
        """Генерация контента для сессии (до 100 объектов каждого типа)"""
        try:
            if config is None:
                config = GenerationConfig()
            
            # Ограничиваем количество объектов согласно лимитам сессии
            session_limits = SYSTEM_LIMITS["session_content_limits"]
            
            session_content = {}
            
            # Генерируем оружие
            weapon_count = min(config.weapon_count, session_limits["weapons"])
            session_content["weapons"] = self.generate_content("weapon", weapon_count, 1)
            
            # Генерируем броню
            armor_count = min(config.armor_count, session_limits["armors"])
            session_content["armors"] = self.generate_content("armor", armor_count, 1)
            
            # Генерируем аксессуары
            accessory_count = min(config.accessory_count, session_limits["accessories"])
            session_content["accessories"] = self.generate_content("accessory", accessory_count, 1)
            
            # Генерируем расходники
            consumable_count = min(config.consumable_count, session_limits["consumables"])
            session_content["consumables"] = self.generate_content("consumable", consumable_count, 1)
            
            # Генерируем гены
            gene_count = min(config.gene_count, session_limits["genes"])
            session_content["genes"] = self.generate_content("gene", gene_count, 1)
            
            # Генерируем скиллы
            skill_count = min(config.skill_count, session_limits["skills"])
            session_content["skills"] = self.generate_content("skill", skill_count, 1)
            
            # Генерируем эффекты
            effect_count = min(config.effect_count, session_limits["effects"])
            session_content["effects"] = self.generate_content("effect", effect_count, 1)
            
            # Генерируем материалы
            material_count = min(config.material_count, session_limits["materials"])
            session_content["materials"] = self.generate_content("material", material_count, 1)
            
            # Генерируем врагов
            enemy_count = min(config.enemy_count, session_limits["enemies"])
            session_content["enemies"] = self.generate_content("enemy", enemy_count, 1)
            
            # Генерируем боссов
            boss_count = min(config.boss_count, session_limits["bosses"])
            session_content["bosses"] = self.generate_content("boss", boss_count, 1)
            
            # Добавляем session_id ко всем элементам
            for content_type, items in session_content.items():
                for item in items:
                    item.session_id = session_id
            
            logger.info(f"Сгенерирован контент для сессии {session_id}: {sum(len(items) for items in session_content.values())} объектов")
            return session_content
            
        except Exception as e:
            logger.error(f"Ошибка генерации контента для сессии {session_id}: {e}")
            return {}
    
    def get_template_info(self, template_type: str) -> Dict[str, Any]:
        """Получение информации о шаблонах"""
        try:
            if template_type == 'weapon':
                return {'count': len(self.weapon_templates), 'templates': list(self.weapon_templates.keys())}
            elif template_type == 'armor':
                return {'count': len(self.armor_templates), 'templates': list(self.armor_templates.keys())}
            elif template_type == 'accessory':
                return {'count': len(self.accessory_templates), 'templates': list(self.accessory_templates.keys())}
            elif template_type == 'gene':
                return {'count': len(self.gene_templates), 'templates': list(self.gene_templates.keys())}
            elif template_type == 'skill':
                return {'count': len(self.skill_templates), 'templates': list(self.skill_templates.keys())}
            elif template_type == 'effect':
                return {'count': len(self.effect_templates), 'templates': list(self.effect_templates.keys())}
            else:
                return {'count': 0, 'templates': []}
                
        except Exception as e:
            logger.error(f"Ошибка получения информации о шаблонах типа {template_type}: {e}")
            return {'count': 0, 'templates': []}
    
    def generate_effect_combinations(self, session_id: str, count: int = 10) -> List[ContentItem]:
        """Генерация комбинаций эффектов для сессии"""
        try:
            combinations = []
            
            # Базовые эффекты для комбинирования
            base_effects = [
                {'name': 'Огненный урон', 'type': 'fire', 'magnitude': 15, 'duration': 5.0},
                {'name': 'Ледяной урон', 'type': 'cold', 'magnitude': 12, 'duration': 6.0},
                {'name': 'Электрический урон', 'type': 'lightning', 'magnitude': 18, 'duration': 4.0},
                {'name': 'Кислотный урон', 'type': 'acid', 'magnitude': 10, 'duration': 8.0},
                {'name': 'Ядовитый урон', 'type': 'poison', 'magnitude': 8, 'duration': 10.0},
                {'name': 'Психический урон', 'type': 'psychic', 'magnitude': 20, 'duration': 3.0},
                {'name': 'Генетический урон', 'type': 'genetic', 'magnitude': 25, 'duration': 7.0},
                {'name': 'Эмоциональный урон', 'type': 'emotional', 'magnitude': 22, 'duration': 4.0}
            ]
            
            for i in range(count):
                # Выбираем два случайных базовых эффекта
                effect1 = self.random_generator.choice(base_effects)
                effect2 = self.random_generator.choice(base_effects)
                
                if effect1 == effect2:
                    continue
                
                # Создаем комбинированный эффект
                combo_name = f"Комбинация: {effect1['name']} + {effect2['name']}"
                combo_description = f"Синергия эффектов {effect1['name']} и {effect2['name']}"
                
                # Рассчитываем параметры комбинации
                combo_magnitude = (effect1['magnitude'] + effect2['magnitude']) * 0.8
                combo_duration = max(effect1['duration'], effect2['duration'])
                
                # Создаем элемент контента
                combo_item = ContentItem(
                    item_id=f"effect_combo_{uuid.uuid4().hex[:8]}",
                    name=combo_name,
                    description=combo_description,
                    content_type=ContentType.DAMAGE_COMBINATION,
                    rarity=self._generate_rarity(),
                    level_requirement=1,
                    session_id=session_id,
                    properties={
                        'effect1': effect1,
                        'effect2': effect2,
                        'combo_magnitude': combo_magnitude,
                        'combo_duration': combo_duration,
                        'generation_time': time.time()
                    }
                )
                
                combinations.append(combo_item)
                self.system_stats['effects_generated'] += 1
            
            logger.info(f"Сгенерировано {len(combinations)} комбинаций эффектов для сессии {session_id}")
            return combinations
            
        except Exception as e:
            logger.error(f"Ошибка генерации комбинаций эффектов: {e}")
            return []
