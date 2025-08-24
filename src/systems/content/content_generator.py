#!/usr/bin/env python3
"""
Content Generator - Система процедурной генерации контента
"""

import logging
import random
import time
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from .content_database import (
    ContentDatabase, ContentItem, ContentType, ContentRarity,
    EnemyData, BossData, EnemyType, BossType, DamageType
)
from .content_constants import (
    ENEMY_CONSTANTS, BOSS_CONSTANTS, ITEM_CONSTANTS,
    RANDOM_GENERATOR, GenerationBiome, GenerationTime, GenerationWeather
)

from ...core.interfaces import ISystem

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

class ContentGenerator(ISystem):
    """Генератор процедурного контента с использованием констант и продвинутого рандома"""
    
    def __init__(self, content_database=None, seed: int = None):
        self.content_db = content_database
        self.random_generator = RANDOM_GENERATOR
        if seed is not None:
            from .content_constants import AdvancedRandomGenerator
            self.random_generator = AdvancedRandomGenerator(seed)
        
        # Шаблоны для генерации
        self.weapon_templates = self._load_weapon_templates()
        self.armor_templates = self._load_armor_templates()
        self.accessory_templates = self._load_accessory_templates()
        self.gene_templates = self._load_gene_templates()
        self.skill_templates = self._load_skill_templates()
        self.effect_templates = self._load_effect_templates()
        
        logger.info("Генератор контента инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация системы"""
        try:
            # Генератор уже инициализирован в конструкторе
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации ContentGenerator: {e}")
            return False
    
    def update(self, delta_time: float):
        """Обновление системы"""
        # Генератор не требует постоянного обновления
        pass
    
    def cleanup(self):
        """Очистка системы"""
        try:
            # Очищаем шаблоны
            self.weapon_templates.clear()
            self.armor_templates.clear()
            self.accessory_templates.clear()
            self.gene_templates.clear()
            self.skill_templates.clear()
            self.effect_templates.clear()
            logger.info("ContentGenerator очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки ContentGenerator: {e}")
    
    def _load_weapon_templates(self) -> List[Dict[str, Any]]:
        """Загрузка шаблонов оружия"""
        return [
            {
                'name': 'Меч',
                'base_damage': 15,
                'attack_speed': 1.2,
                'types': ['sword', 'melee', 'sharp'],
                'rarity_weights': ITEM_CONSTANTS.rarity_weights_by_type['weapon']
            },
            {
                'name': 'Топор',
                'base_damage': 20,
                'attack_speed': 0.8,
                'types': ['axe', 'melee', 'heavy'],
                'rarity_weights': ITEM_CONSTANTS.rarity_weights_by_type['weapon']
            },
            {
                'name': 'Лук',
                'base_damage': 12,
                'attack_speed': 1.5,
                'types': ['bow', 'ranged', 'piercing'],
                'rarity_weights': ITEM_CONSTANTS.rarity_weights_by_type['weapon']
            },
            {
                'name': 'Посох',
                'base_damage': 10,
                'attack_speed': 1.0,
                'types': ['staff', 'magic', 'elemental'],
                'rarity_weights': ITEM_CONSTANTS.rarity_weights_by_type['weapon']
            }
        ]
    
    def _load_armor_templates(self) -> List[Dict[str, Any]]:
        """Загрузка шаблонов брони"""
        return [
            {
                'name': 'Кожаная броня',
                'base_armor': 8,
                'weight': 2,
                'types': ['leather', 'light', 'agile'],
                'rarity_weights': ITEM_CONSTANTS.rarity_weights_by_type['armor']
            },
            {
                'name': 'Кольчужная броня',
                'base_armor': 15,
                'weight': 5,
                'types': ['chain', 'medium', 'balanced'],
                'rarity_weights': ITEM_CONSTANTS.rarity_weights_by_type['armor']
            },
            {
                'name': 'Латная броня',
                'base_armor': 25,
                'weight': 8,
                'types': ['plate', 'heavy', 'protective'],
                'rarity_weights': ITEM_CONSTANTS.rarity_weights_by_type['armor']
            }
        ]
    
    def _load_accessory_templates(self) -> List[Dict[str, Any]]:
        """Загрузка шаблонов аксессуаров"""
        return [
            {
                'name': 'Кольцо',
                'base_bonus': 5,
                'types': ['ring', 'magical', 'enhancement'],
                'rarity_weights': ITEM_CONSTANTS.rarity_weights_by_type['accessory']
            },
            {
                'name': 'Амулет',
                'base_bonus': 8,
                'types': ['amulet', 'protective', 'magical'],
                'rarity_weights': ITEM_CONSTANTS.rarity_weights_by_type['accessory']
            }
        ]
    
    def _load_gene_templates(self) -> List[Dict[str, Any]]:
        """Загрузка шаблонов генов"""
        return [
            {
                'name': 'Ген силы',
                'gene_type': GeneType.STRENGTH,
                'base_value': 0.1,
                'mutation_rate': 0.05,
                'rarity_weights': {'common': 0.4, 'uncommon': 0.3, 'rare': 0.2, 'epic': 0.08, 'legendary': 0.02}
            },
            {
                'name': 'Ген ловкости',
                'gene_type': GeneType.AGILITY,
                'base_value': 0.1,
                'mutation_rate': 0.06,
                'rarity_weights': {'common': 0.4, 'uncommon': 0.3, 'rare': 0.2, 'epic': 0.08, 'legendary': 0.02}
            },
            {
                'name': 'Ген интеллекта',
                'gene_type': GeneType.INTELLIGENCE,
                'base_value': 0.1,
                'mutation_rate': 0.05,
                'rarity_weights': {'common': 0.4, 'uncommon': 0.3, 'rare': 0.2, 'epic': 0.08, 'legendary': 0.02}
            },
            {
                'name': 'Ген жизнеспособности',
                'gene_type': GeneType.VITALITY,
                'base_value': 0.1,
                'mutation_rate': 0.04,
                'rarity_weights': {'common': 0.4, 'uncommon': 0.3, 'rare': 0.2, 'epic': 0.08, 'legendary': 0.02}
            }
        ]
    
    def _load_skill_templates(self) -> List[Dict[str, Any]]:
        """Загрузка шаблонов скиллов"""
        return [
            {
                'name': 'Атака',
                'skill_type': SkillType.COMBAT,
                'target_type': SkillTarget.ENEMY,
                'base_cooldown': 1.0,
                'types': ['attack', 'physical', 'basic'],
                'rarity_weights': {'common': 0.5, 'uncommon': 0.3, 'rare': 0.15, 'epic': 0.04, 'legendary': 0.01}
            },
            {
                'name': 'Защита',
                'skill_type': SkillType.COMBAT,
                'target_type': SkillTarget.SELF,
                'base_cooldown': 3.0,
                'types': ['defense', 'protective', 'buff'],
                'rarity_weights': {'common': 0.5, 'uncommon': 0.3, 'rare': 0.15, 'epic': 0.04, 'legendary': 0.01}
            },
            {
                'name': 'Лечение',
                'skill_type': SkillType.UTILITY,
                'target_type': SkillTarget.ALLY,
                'base_cooldown': 5.0,
                'types': ['healing', 'support', 'magical'],
                'rarity_weights': {'common': 0.4, 'uncommon': 0.35, 'rare': 0.2, 'epic': 0.04, 'legendary': 0.01}
            }
        ]
    
    def _load_effect_templates(self) -> List[Dict[str, Any]]:
        """Загрузка шаблонов эффектов"""
        return [
            {
                'name': 'Огненный урон',
                'effect_category': EffectCategory.DAMAGE,
                'damage_type': DamageType.FIRE,
                'base_value': 20,
                'types': ['fire', 'damage', 'elemental'],
                'rarity_weights': {'common': 0.4, 'uncommon': 0.3, 'rare': 0.2, 'epic': 0.08, 'legendary': 0.02}
            },
            {
                'name': 'Ледяной урон',
                'effect_category': EffectCategory.DAMAGE,
                'damage_type': DamageType.ICE,
                'base_value': 18,
                'types': ['ice', 'damage', 'elemental'],
                'rarity_weights': {'common': 0.4, 'uncommon': 0.3, 'rare': 0.2, 'epic': 0.08, 'legendary': 0.02}
            }
        ]
    
    def _select_rarity(self, rarity_weights: Dict[str, float]) -> ContentRarity:
        """Выбор редкости на основе весов"""
        return ContentRarity(self.random_generator.weighted_choice(
            list(rarity_weights.keys()),
            list(rarity_weights.values())
        ))
    
    def _calculate_level_requirement(self, rarity: ContentRarity, base_level: int = 1) -> int:
        """Расчет требуемого уровня на основе редкости"""
        rarity_multipliers = {
            ContentRarity.COMMON: 1,
            ContentRarity.UNCOMMON: 1.2,
            ContentRarity.RARE: 1.5,
            ContentRarity.EPIC: 2.0,
            ContentRarity.LEGENDARY: 3.0
        }
        
        return max(1, int(base_level * rarity_multipliers[rarity]))
    
    def generate_session_content(self, session_id: str, level: int, config: GenerationConfig = None) -> Dict[str, List[ContentItem]]:
        """Генерация контента для новой сессии или уровня"""
        if config is None:
            config = GenerationConfig()
        
        logger.info(f"Генерация контента для сессии {session_id} уровня {level}")
        
        generated_content = {}
        
        # Генерируем оружие
        generated_content['weapons'] = self._generate_weapons(session_id, level, config.weapon_count)
        
        # Генерируем броню
        generated_content['armors'] = self._generate_armors(session_id, level, config.armor_count)
        
        # Генерируем аксессуары
        generated_content['accessories'] = self._generate_accessories(session_id, level, config.accessory_count)
        
        # Генерируем расходники
        generated_content['consumables'] = self._generate_consumables(session_id, level, config.consumable_count)
        
        # Генерируем гены
        generated_content['genes'] = self._generate_genes(session_id, level, config.gene_count)
        
        # Генерируем скиллы
        generated_content['skills'] = self._generate_skills(session_id, level, config.skill_count)
        
        # Генерируем эффекты
        generated_content['effects'] = self._generate_effects(session_id, level, config.effect_count)
        
        # Генерируем материалы
        generated_content['materials'] = self._generate_materials(session_id, level, config.material_count)
        
        # Генерируем врагов
        generated_content['enemies'] = self._generate_enemies(session_id, level, config.enemy_count)
        
        # Генерируем боссов
        generated_content['bosses'] = self._generate_bosses(session_id, level, config.boss_count)
        
        # Сохраняем все в базу данных
        for content_list in generated_content.values():
            for content_item in content_list:
                self.content_db.add_content_item(content_item)
        
        logger.info(f"Сгенерировано {sum(len(content) for content in generated_content.values())} элементов контента")
        return generated_content
    
    def _generate_enemies(self, session_id: str, level: int, count: int) -> List[ContentItem]:
        """Генерация врагов с использованием констант"""
        enemies = []
        
        for i in range(count):
            # Выбираем тип врага
            enemy_type = self.random_generator.weighted_choice(
                list(ENEMY_CONSTANTS.base_stats_by_type.keys()),
                [1.0] * len(ENEMY_CONSTANTS.base_stats_by_type)  # Равные веса для всех типов
            )
            
            # Выбираем редкость на основе типа
            rarity_weights = ENEMY_CONSTANTS.rarity_weights_by_type[enemy_type]
            rarity = self._select_rarity({
                'common': rarity_weights.common,
                'uncommon': rarity_weights.uncommon,
                'rare': rarity_weights.rare,
                'epic': rarity_weights.epic,
                'legendary': rarity_weights.legendary
            })
            
            level_req = self._calculate_level_requirement(rarity, level)
            
            # Получаем базовые характеристики для типа
            base_stats = ENEMY_CONSTANTS.base_stats_by_type[enemy_type]
            
            # Генерируем уникальные характеристики с использованием продвинутого рандома
            health_modifier = self.random_generator.gaussian_modifier(1.0, 0.15, 0.8, 1.3)
            attack_modifier = self.random_generator.triangular_modifier(0.9, 1.2, 1.0)
            defense_modifier = self.random_generator.exponential_modifier(1.0, 0.3, 1.2)
            
            # Создаем данные врага
            enemy_data = EnemyData(
                enemy_type=EnemyType(enemy_type),
                base_health=int(base_stats['health'] * health_modifier * (1 + level * ENEMY_CONSTANTS.level_multipliers['health'])),
                base_mana=int(base_stats['mana'] * (1 + level * ENEMY_CONSTANTS.level_multipliers['mana'])),
                base_attack=int(base_stats['attack'] * attack_modifier * (1 + level * ENEMY_CONSTANTS.level_multipliers['attack'])),
                base_defense=int(base_stats['defense'] * defense_modifier * (1 + level * ENEMY_CONSTANTS.level_multipliers['defense'])),
                base_speed=base_stats['speed'] * self.random_generator.gaussian_modifier(1.0, 0.1, 0.9, 1.1),
                base_intelligence=base_stats['intelligence'] + self.random_generator.constrained_random_int(-2, 3, {'prefer_middle': True}),
                weaknesses=[DamageType(w) for w in ENEMY_CONSTANTS.type_weaknesses[enemy_type]],
                resistances=[DamageType(r) for r in ENEMY_CONSTANTS.type_resistances[enemy_type]],
                immunities=[DamageType(i) for i in ENEMY_CONSTANTS.type_immunities[enemy_type]],
                skills=[],  # Будет заполнено позже
                loot_table=[],  # Будет заполнено позже
                experience_reward=int(base_stats['health'] * 0.1 * (1 + level * 0.2)),
                gold_reward=int(base_stats['health'] * 0.05 * (1 + level * 0.15)),
                ai_behavior=ENEMY_CONSTANTS.ai_behavior_by_type[enemy_type],
                spawn_conditions=self._generate_spawn_conditions(ENEMY_CONSTANTS.spawn_conditions[enemy_type])
            )
            
            # Добавляем врага в базу данных
            enemy_uuid = str(uuid.uuid4())
            self.content_db.add_enemy(enemy_uuid, enemy_type.title(), EnemyType(enemy_type), level_req, session_id, enemy_data)
            
            # Создаем элемент контента
            content_item = ContentItem(
                uuid=enemy_uuid,
                content_type=ContentType.ENEMY,
                name=f"{enemy_type.title()} уровня {level_req}",
                description=f"Враг типа {enemy_type} с {enemy_data.base_health} HP",
                rarity=rarity,
                level_requirement=level_req,
                session_id=session_id,
                generation_timestamp=time.time(),
                data={
                    'enemy_type': enemy_type,
                    'base_health': enemy_data.base_health,
                    'base_attack': enemy_data.base_attack,
                    'weaknesses': [w.value for w in enemy_data.weaknesses],
                    'ai_behavior': enemy_data.ai_behavior
                }
            )
            
            enemies.append(content_item)
            
            # Записываем статистику генерации
            self.random_generator.record_generation(
                'enemy', rarity.value, level_req,
                {'health': enemy_data.base_health, 'attack': enemy_data.base_attack}
            )
        
        return enemies
    
    def _generate_bosses(self, session_id: str, level: int, count: int) -> List[ContentItem]:
        """Генерация боссов с использованием констант и поддержкой рейдж режима"""
        bosses = []
        
        for i in range(count):
            # Выбираем тип босса
            boss_type = self.random_generator.weighted_choice(
                list(BOSS_CONSTANTS.base_stats_by_type.keys()),
                [1.0] * len(BOSS_CONSTANTS.base_stats_by_type)
            )
            
            # Выбираем редкость на основе типа
            rarity_weights = BOSS_CONSTANTS.rarity_weights_by_type[boss_type]
            rarity = self._select_rarity({
                'common': rarity_weights.common,
                'uncommon': rarity_weights.uncommon,
                'rare': rarity_weights.rare,
                'epic': rarity_weights.epic,
                'legendary': rarity_weights.legendary
            })
            
            level_req = self._calculate_level_requirement(rarity, level)
            
            # Получаем базовые характеристики для типа
            base_stats = BOSS_CONSTANTS.base_stats_by_type[boss_type]
            
            # Генерируем уникальные характеристики с использованием продвинутого рандома
            health_modifier = self.random_generator.gaussian_modifier(1.0, 0.2, 0.9, 1.4)
            attack_modifier = self.random_generator.triangular_modifier(0.95, 1.25, 1.1)
            defense_modifier = self.random_generator.exponential_modifier(1.0, 0.25, 1.3)
            
            # Создаем данные босса
            boss_data = BossData(
                boss_type=BossType(boss_type),
                base_health=int(base_stats['health'] * health_modifier * (1 + level * BOSS_CONSTANTS.level_multipliers['health'])),
                base_mana=int(base_stats['mana'] * (1 + level * BOSS_CONSTANTS.level_multipliers['mana'])),
                base_attack=int(base_stats['attack'] * attack_modifier * (1 + level * BOSS_CONSTANTS.level_multipliers['attack'])),
                base_defense=int(base_stats['defense'] * defense_modifier * (1 + level * BOSS_CONSTANTS.level_multipliers['defense'])),
                base_speed=base_stats['speed'] * self.random_generator.gaussian_modifier(1.0, 0.15, 0.95, 1.15),
                base_intelligence=base_stats['intelligence'] + self.random_generator.constrained_random_int(-3, 4, {'prefer_middle': True}),
                weaknesses=[DamageType(w) for w in BOSS_CONSTANTS.type_weaknesses[boss_type]],
                resistances=[DamageType(r) for r in BOSS_CONSTANTS.type_resistances[boss_type]],
                immunities=[DamageType(i) for i in BOSS_CONSTANTS.type_immunities[boss_type]],
                skills=[],  # Будет заполнено позже
                special_abilities=[],  # Будет заполнено позже
                phases=BOSS_CONSTANTS.phases_by_type[boss_type],
                loot_table=[],  # Будет заполнено позже
                experience_reward=int(base_stats['health'] * 0.15 * (1 + level * 0.25)),
                gold_reward=int(base_stats['health'] * 0.08 * (1 + level * 0.2)),
                ai_behavior=BOSS_CONSTANTS.ai_behavior_by_type[boss_type],
                spawn_conditions=self._generate_spawn_conditions(BOSS_CONSTANTS.spawn_conditions[boss_type]),
                minion_spawns=BOSS_CONSTANTS.minion_spawns_by_type[boss_type]
            )
            
            # Добавляем босса в базу данных
            boss_uuid = str(uuid.uuid4())
            self.content_db.add_boss(boss_uuid, boss_type.replace('_', ' ').title(), BossType(boss_type), level_req, session_id, boss_data)
            
            # Создаем элемент контента
            content_item = ContentItem(
                uuid=boss_uuid,
                content_type=ContentType.BOSS,
                name=f"{boss_type.replace('_', ' ').title()} уровня {level_req}",
                description=f"Босс типа {boss_type} с {boss_data.base_health} HP и {len(boss_data.phases)} фазами",
                rarity=rarity,
                level_requirement=level_req,
                session_id=session_id,
                generation_timestamp=time.time(),
                data={
                    'boss_type': boss_type,
                    'base_health': boss_data.base_health,
                    'base_attack': boss_data.base_attack,
                    'phases': len(boss_data.phases),
                    'weaknesses': [w.value for w in boss_data.weaknesses],
                    'ai_behavior': boss_data.ai_behavior,
                    'rage_mode_threshold': 0.1,  # Рейдж режим при 10% HP
                    'rage_mode_bonuses': {
                        'attack_multiplier': 1.5,
                        'speed_multiplier': 1.3,
                        'duration': 60.0
                    }
                }
            )
            
            bosses.append(content_item)
            
            # Записываем статистику генерации
            self.random_generator.record_generation(
                'boss', rarity.value, level_req,
                {'health': boss_data.base_health, 'attack': boss_data.base_attack, 'phases': len(boss_data.phases)}
            )
        
        return bosses
    
    def _generate_spawn_conditions(self, base_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация условий появления на основе базовых"""
        conditions = base_conditions.copy()
        
        # Добавляем случайные вариации
        if 'biomes' in conditions:
            # Выбираем случайный биом из доступных
            conditions['biome'] = self.random_generator.weighted_choice(
                [b.value for b in conditions['biomes']],
                [1.0] * len(conditions['biomes'])
            )
        
        if 'time' in conditions:
            # Выбираем случайное время из доступных
            conditions['time_of_day'] = self.random_generator.weighted_choice(
                [t.value for t in conditions['time']],
                [1.0] * len(conditions['time'])
            )
        
        if 'weather' in conditions:
            # Выбираем случайную погоду из доступных
            conditions['weather_condition'] = self.random_generator.weighted_choice(
                [w.value for w in conditions['weather']],
                [1.0] * len(conditions['weather'])
            )
        
        # Добавляем случайные координаты
        conditions['position'] = {
            'x': self.random_generator.constrained_random_int(-100, 100),
            'y': self.random_generator.constrained_random_int(-100, 100),
            'z': 0
        }
        
        return conditions
    
    def _generate_weapons(self, session_id: str, level: int, count: int) -> List[ContentItem]:
        """Генерация оружия с использованием констант"""
        weapons = []
        
        for i in range(count):
            template = self.random_generator.weighted_choice(
                self.weapon_templates,
                [1.0] * len(self.weapon_templates)
            )
            
            rarity = self._select_rarity(template['rarity_weights'])
            level_req = self._calculate_level_requirement(rarity, level)
            
            # Генерируем уникальные характеристики с использованием продвинутого рандома
            damage_modifier = self.random_generator.gaussian_modifier(1.0, 0.15, 0.8, 1.2)
            speed_modifier = self.random_generator.triangular_modifier(0.9, 1.1, 1.0)
            
            weapon_data = {
                'template': template['name'],
                'damage': int(template['base_damage'] * damage_modifier * (1 + level * ITEM_CONSTANTS.level_multipliers['damage'])),
                'attack_speed': template['attack_speed'] * speed_modifier,
                'types': template['types'],
                'level': level_req,
                'durability': self.random_generator.constrained_random_int(80, 120, {'prefer_middle': True}),
                'weight': self.random_generator.gaussian_modifier(1.0, 0.1, 0.8, 1.2)
            }
            
            content_item = ContentItem(
                uuid=str(uuid.uuid4()),
                content_type=ContentType.WEAPON,
                name=f"{template['name']} уровня {level_req}",
                description=f"Мощное оружие с уроном {weapon_data['damage']}",
                rarity=rarity,
                level_requirement=level_req,
                session_id=session_id,
                generation_timestamp=time.time(),
                data=weapon_data
            )
            
            weapons.append(content_item)
            
            # Записываем статистику генерации
            self.random_generator.record_generation(
                'weapon', rarity.value, level_req,
                {'damage': weapon_data['damage'], 'attack_speed': weapon_data['attack_speed']}
            )
        
        return weapons
    
    def _generate_armors(self, session_id: str, level: int, count: int) -> List[ContentItem]:
        """Генерация брони с использованием констант"""
        armors = []
        
        for i in range(count):
            template = self.random_generator.weighted_choice(
                self.armor_templates,
                [1.0] * len(self.armor_templates)
            )
            
            rarity = self._select_rarity(template['rarity_weights'])
            level_req = self._calculate_level_requirement(rarity, level)
            
            # Генерируем уникальные характеристики
            armor_modifier = self.random_generator.gaussian_modifier(1.0, 0.15, 0.8, 1.2)
            weight_modifier = self.random_generator.triangular_modifier(0.9, 1.1, 1.0)
            
            armor_data = {
                'template': template['name'],
                'armor': int(template['base_armor'] * armor_modifier * (1 + level * ITEM_CONSTANTS.level_multipliers['armor_value'])),
                'weight': template['weight'] * weight_modifier,
                'types': template['types'],
                'level': level_req,
                'durability': self.random_generator.constrained_random_int(80, 120, {'prefer_middle': True}),
                'magic_resistance': self.random_generator.constrained_random_int(0, 10, {'prefer_low': True})
            }
            
            content_item = ContentItem(
                uuid=str(uuid.uuid4()),
                content_type=ContentType.ARMOR,
                name=f"{template['name']} уровня {level_req}",
                description=f"Защитная броня с защитой {armor_data['armor']}",
                rarity=rarity,
                level_requirement=level_req,
                session_id=session_id,
                generation_timestamp=time.time(),
                data=armor_data
            )
            
            armors.append(content_item)
        
        return armors
    
    def _generate_accessories(self, session_id: str, level: int, count: int) -> List[ContentItem]:
        """Генерация аксессуаров с использованием констант"""
        accessories = []
        
        for i in range(count):
            template = self.random_generator.weighted_choice(
                self.accessory_templates,
                [1.0] * len(self.accessory_templates)
            )
            
            rarity = self._select_rarity(template['rarity_weights'])
            level_req = self._calculate_level_requirement(rarity, level)
            
            # Генерируем уникальные характеристики
            bonus_modifier = self.random_generator.gaussian_modifier(1.0, 0.15, 0.8, 1.2)
            
            accessory_data = {
                'template': template['name'],
                'bonus': int(template['base_bonus'] * bonus_modifier * (1 + level * ITEM_CONSTANTS.level_multipliers['bonus'])),
                'types': template['types'],
                'level': level_req,
                'magical_power': self.random_generator.constrained_random_int(10, 50, {'prefer_middle': True})
            }
            
            content_item = ContentItem(
                uuid=str(uuid.uuid4()),
                content_type=ContentType.ACCESSORY,
                name=f"{template['name']} уровня {level_req}",
                description=f"Магический аксессуар с бонусом {accessory_data['bonus']}",
                rarity=rarity,
                level_requirement=level_req,
                session_id=session_id,
                generation_timestamp=time.time(),
                data=accessory_data
            )
            
            accessories.append(content_item)
        
        return accessories
    
    def _generate_consumables(self, session_id: str, level: int, count: int) -> List[ContentItem]:
        """Генерация расходников"""
        consumables = []
        
        consumable_types = ['Зелье здоровья', 'Зелье маны', 'Эликсир силы', 'Антидот']
        
        for i in range(count):
            consumable_type = self.random_generator.weighted_choice(consumable_types, [1.0] * len(consumable_types))
            rarity = ContentRarity.COMMON if self.random_generator.weighted_choice(['common', 'uncommon'], [0.7, 0.3]) == 'common' else ContentRarity.UNCOMMON
            level_req = max(1, level - 2)
            
            # Генерируем характеристики
            potency = self.random_generator.gaussian_modifier(1.0, 0.15, 0.8, 1.2) * (1 + level * ITEM_CONSTANTS.level_multipliers['potency'])
            
            consumable_data = {
                'type': consumable_type,
                'potency': potency,
                'duration': self.random_generator.constrained_random_int(30, 120, {'prefer_middle': True}),
                'stack_size': self.random_generator.constrained_random_int(1, 5, {'prefer_low': True})
            }
            
            content_item = ContentItem(
                uuid=str(uuid.uuid4()),
                content_type=ContentType.CONSUMABLE,
                name=f"{consumable_type} уровня {level_req}",
                description=f"Мощный расходник с эффективностью {potency:.1f}",
                rarity=rarity,
                level_requirement=level_req,
                session_id=session_id,
                generation_timestamp=time.time(),
                data=consumable_data
            )
            
            consumables.append(content_item)
        
        return consumables
    
    def _generate_genes(self, session_id: str, level: int, count: int) -> List[ContentItem]:
        """Генерация генов"""
        genes = []
        
        for i in range(count):
            template = self.random_generator.weighted_choice(
                self.gene_templates,
                [1.0] * len(self.gene_templates)
            )
            
            rarity = self._select_rarity(template['rarity_weights'])
            level_req = self._calculate_level_requirement(rarity, level)
            
            # Генерируем уникальные характеристики
            value_modifier = self.random_generator.gaussian_modifier(1.0, 0.15, 0.8, 1.2)
            mutation_modifier = self.random_generator.triangular_modifier(0.9, 1.1, 1.0)
            
            gene_data = {
                'template': template['name'],
                'gene_type': template['gene_type'].value,
                'value': template['base_value'] * value_modifier * (1 + level * 0.05),
                'mutation_rate': template['mutation_rate'] * mutation_modifier,
                'dominance': self.random_generator.weighted_choice(
                    [GeneDominance.DOMINANT, GeneDominance.RECESSIVE, GeneDominance.CODOMINANT],
                    [0.4, 0.4, 0.2]
                ).value,
                'level': level_req
            }
            
            content_item = ContentItem(
                uuid=str(uuid.uuid4()),
                content_type=ContentType.GENE,
                name=f"{template['name']} уровня {level_req}",
                description=f"Ген с силой {gene_data['value']:.2f}",
                rarity=rarity,
                level_requirement=level_req,
                session_id=session_id,
                generation_timestamp=time.time(),
                data=gene_data
            )
            
            genes.append(content_item)
        
        return genes
    
    def _generate_skills(self, session_id: str, level: int, count: int) -> List[ContentItem]:
        """Генерация скиллов"""
        skills = []
        
        for i in range(count):
            template = self.random_generator.weighted_choice(
                self.skill_templates,
                [1.0] * len(self.skill_templates)
            )
            
            rarity = self._select_rarity(template['rarity_weights'])
            level_req = self._calculate_level_requirement(rarity, level)
            
            # Генерируем уникальные характеристики
            cooldown_modifier = self.random_generator.gaussian_modifier(1.0, 0.15, 0.8, 1.2)
            
            skill_data = {
                'template': template['name'],
                'skill_type': template['skill_type'].value,
                'target_type': template['target_type'].value,
                'cooldown': template['base_cooldown'] * cooldown_modifier,
                'types': template['types'],
                'level': level_req,
                'mana_cost': self.random_generator.constrained_random_int(10, 50, {'prefer_middle': True}),
                'range': self.random_generator.gaussian_modifier(1.0, 0.5, 1.0, 5.0)
            }
            
            content_item = ContentItem(
                uuid=str(uuid.uuid4()),
                content_type=ContentType.SKILL,
                name=f"{template['name']} уровня {level_req}",
                description=f"Мощный скилл с перезарядкой {skill_data['cooldown']:.1f}с",
                rarity=rarity,
                level_requirement=level_req,
                session_id=session_id,
                generation_timestamp=time.time(),
                data=skill_data
            )
            
            skills.append(content_item)
        
        return skills
    
    def _generate_effects(self, session_id: str, level: int, count: int) -> List[ContentItem]:
        """Генерация эффектов"""
        effects = []
        
        for i in range(count):
            template = self.random_generator.weighted_choice(
                self.effect_templates,
                [1.0] * len(self.effect_templates)
            )
            
            rarity = self._select_rarity(template['rarity_weights'])
            level_req = self._calculate_level_requirement(rarity, level)
            
            # Генерируем уникальные характеристики
            value_modifier = self.random_generator.gaussian_modifier(1.0, 0.15, 0.8, 1.2)
            
            effect_data = {
                'template': template['name'],
                'effect_category': template['effect_category'].value,
                'damage_type': template['damage_type'].value,
                'value': int(template['base_value'] * value_modifier * (1 + level * 0.1)),
                'types': template['types'],
                'level': level_req,
                'duration': self.random_generator.constrained_random_int(5, 30, {'prefer_middle': True}),
                'range': self.random_generator.gaussian_modifier(1.0, 0.8, 1.0, 8.0)
            }
            
            content_item = ContentItem(
                uuid=str(uuid.uuid4()),
                content_type=ContentType.EFFECT,
                name=f"{template['name']} уровня {level_req}",
                description=f"Эффект с силой {effect_data['value']}",
                rarity=rarity,
                level_requirement=level_req,
                session_id=session_id,
                generation_timestamp=time.time(),
                data=effect_data
            )
            
            effects.append(content_item)
        
        return effects
    
    def _generate_materials(self, session_id: str, level: int, count: int) -> List[ContentItem]:
        """Генерация материалов"""
        materials = []
        
        material_types = ['Железо', 'Дерево', 'Камень', 'Ткань', 'Кожа', 'Кристалл']
        
        for i in range(count):
            material_type = self.random_generator.weighted_choice(material_types, [1.0] * len(material_types))
            rarity = ContentRarity.COMMON if self.random_generator.weighted_choice(['common', 'uncommon'], [0.8, 0.2]) == 'common' else ContentRarity.UNCOMMON
            level_req = max(1, level - 1)
            
            # Генерируем характеристики
            quality = self.random_generator.gaussian_modifier(1.0, 0.2, 0.7, 1.3)
            quantity = self.random_generator.constrained_random_int(1, 10, {'prefer_low': True})
            
            material_data = {
                'type': material_type,
                'quality': quality,
                'quantity': quantity,
                'crafting_value': int(quality * 10)
            }
            
            content_item = ContentItem(
                uuid=str(uuid.uuid4()),
                content_type=ContentType.MATERIAL,
                name=f"{material_type} уровня {level_req}",
                description=f"Материал качества {quality:.1f} в количестве {quantity}",
                rarity=rarity,
                level_requirement=level_req,
                session_id=session_id,
                generation_timestamp=time.time(),
                data=material_data
            )
            
            materials.append(content_item)
        
        return materials
    
    def get_content_for_entity(self, session_id: str, entity_level: int, content_types: List[ContentType] = None) -> Dict[str, List[ContentItem]]:
        """Получение доступного контента для сущности определенного уровня"""
        if content_types is None:
            content_types = list(ContentType)
        
        available_content = {}
        
        for content_type in content_types:
            content_items = self.content_db.get_content_by_level(session_id, entity_level, content_type)
            available_content[content_type.value] = content_items
        
        return available_content
    
    def get_enemies_for_level(self, session_id: str, level: int, enemy_type: Optional[EnemyType] = None) -> List[Dict[str, Any]]:
        """Получение врагов для определенного уровня"""
        return self.content_db.get_enemies_by_level(session_id, level, enemy_type)
    
    def get_bosses_for_level(self, session_id: str, level: int, boss_type: Optional[BossType] = None) -> List[Dict[str, Any]]:
        """Получение боссов для определенного уровня"""
        return self.content_db.get_bosses_by_level(session_id, level, boss_type)
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Получение статистики генерации"""
        return self.random_generator.get_generation_statistics()
    
    def cleanup_session_content(self, session_id: str):
        """Очистка несохраненного контента для сессии"""
        self.content_db.cleanup_unsaved_content(session_id)
        logger.info(f"Контент для сессии {session_id} очищен")
