#!/usr/bin/env python3
"""
Система генерации контента - процедурная генерация игрового контента
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

from ...core.interfaces import ISystem, SystemPriority, SystemState

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
    """Система генерации процедурного контента с использованием констант и продвинутого рандома"""
    
    def __init__(self, content_database=None, seed: int = None):
        self._system_name = "content_generator"
        self._system_priority = SystemPriority.NORMAL
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = ["content_database"]
        
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
            
            # Проверяем зависимости
            if not self.content_db:
                logger.error("База данных контента не инициализирована")
                self._system_state = SystemState.ERROR
                return False
            
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
            
            # Очищаем шаблоны
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
            'content_db_active': self.content_db is not None,
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
            if event_type == "generate_content":
                return self._handle_generate_content(event_data)
            elif event_type == "session_level_up":
                return self._handle_session_level_up(event_data)
            elif event_type == "content_requested":
                return self._handle_content_requested(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def _load_all_templates(self) -> None:
        """Загрузка всех шаблонов"""
        try:
            # Шаблоны уже загружены в конструкторе
            logger.debug("Все шаблоны загружены")
        except Exception as e:
            logger.warning(f"Не удалось загрузить все шаблоны: {e}")
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            # Обновляем общее количество сгенерированного контента
            total = (self.system_stats['weapons_generated'] + 
                    self.system_stats['armors_generated'] + 
                    self.system_stats['accessories_generated'] + 
                    self.system_stats['consumables_generated'] + 
                    self.system_stats['genes_generated'] + 
                    self.system_stats['skills_generated'] + 
                    self.system_stats['effects_generated'] + 
                    self.system_stats['materials_generated'] + 
                    self.system_stats['enemies_generated'] + 
                    self.system_stats['bosses_generated'])
            
            self.system_stats['total_generated'] = total
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_generate_content(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события генерации контента"""
        try:
            session_id = event_data.get('session_id')
            config = event_data.get('config', GenerationConfig())
            
            if session_id:
                return self.generate_session_content(session_id, config)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события генерации контента: {e}")
            return False
    
    def _handle_session_level_up(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события повышения уровня сессии"""
        try:
            session_id = event_data.get('session_id')
            new_level = event_data.get('new_level')
            
            if session_id and new_level:
                return self.generate_level_content(session_id, new_level)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события повышения уровня сессии: {e}")
            return False
    
    def _handle_content_requested(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события запроса контента"""
        try:
            content_type = event_data.get('content_type')
            session_id = event_data.get('session_id')
            level = event_data.get('level', 1)
            
            if content_type and session_id:
                if content_type == "enemy":
                    return self.generate_enemy(session_id, level) is not None
                elif content_type == "boss":
                    return self.generate_boss(session_id, level) is not None
                elif content_type == "item":
                    return self.generate_item(session_id, level) is not None
                else:
                    return False
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события запроса контента: {e}")
            return False
    
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
    
    def _load_skill_generation_templates(self) -> List[Dict[str, Any]]:
        """Загрузка шаблонов для генерации скиллов"""
        return [
            {
                'name': 'Огненный шар',
                'base_damage': 30,
                'damage_type': DamageType.FIRE,
                'mana_cost': 25,
                'cooldown': 3.0,
                'range': 8.0,
                'cast_time': 1.0,
                'skill_type': 'combat',
                'target_type': 'enemy',
                'effects': ['burn', 'explosion'],
                'rarity_weights': [0.6, 0.3, 0.1, 0.0],  # common, uncommon, rare, legendary
                'level_scaling': {'damage': 0.15, 'mana_cost': 0.1, 'cooldown': -0.05}
            },
            {
                'name': 'Исцеление',
                'base_heal': 40,
                'heal_type': 'magical',
                'mana_cost': 30,
                'cooldown': 8.0,
                'range': 5.0,
                'cast_time': 1.5,
                'skill_type': 'utility',
                'target_type': 'ally',
                'effects': ['heal', 'regeneration'],
                'rarity_weights': [0.7, 0.2, 0.1, 0.0],
                'level_scaling': {'heal': 0.2, 'mana_cost': 0.1, 'cooldown': -0.03}
            },
            {
                'name': 'Ледяная стрела',
                'base_damage': 25,
                'damage_type': DamageType.ICE,
                'mana_cost': 20,
                'cooldown': 2.5,
                'range': 10.0,
                'cast_time': 0.8,
                'skill_type': 'combat',
                'target_type': 'enemy',
                'effects': ['freeze', 'slow'],
                'rarity_weights': [0.5, 0.4, 0.1, 0.0],
                'level_scaling': {'damage': 0.12, 'mana_cost': 0.08, 'cooldown': -0.04}
            },
            {
                'name': 'Молния',
                'base_damage': 35,
                'damage_type': DamageType.LIGHTNING,
                'mana_cost': 35,
                'cooldown': 4.0,
                'range': 12.0,
                'cast_time': 1.2,
                'skill_type': 'combat',
                'target_type': 'enemy',
                'effects': ['shock', 'chain'],
                'rarity_weights': [0.4, 0.4, 0.2, 0.0],
                'level_scaling': {'damage': 0.18, 'mana_cost': 0.12, 'cooldown': -0.06}
            },
            {
                'name': 'Ядовитое облако',
                'base_damage': 15,
                'damage_type': DamageType.POISON,
                'mana_cost': 40,
                'cooldown': 6.0,
                'range': 6.0,
                'cast_time': 2.0,
                'skill_type': 'combat',
                'target_type': 'area',
                'effects': ['poison', 'area_damage'],
                'rarity_weights': [0.3, 0.5, 0.2, 0.0],
                'level_scaling': {'damage': 0.1, 'mana_cost': 0.15, 'cooldown': -0.08}
            }
        ]
    
    def _load_item_generation_templates(self) -> List[Dict[str, Any]]:
        """Загрузка шаблонов для генерации предметов"""
        return [
            {
                'name': 'Меч',
                'base_damage': 15,
                'attack_speed': 1.2,
                'item_type': 'weapon',
                'weapon_type': 'sword',
                'rarity_weights': [0.5, 0.3, 0.15, 0.05],
                'level_scaling': {'damage': 0.2, 'attack_speed': 0.05},
                'unique_properties': ['sharp', 'durable', 'balanced'],
                'enchantment_slots': 2
            },
            {
                'name': 'Кольчуга',
                'base_defense': 12,
                'weight': 8,
                'item_type': 'armor',
                'armor_type': 'medium',
                'rarity_weights': [0.6, 0.25, 0.12, 0.03],
                'level_scaling': {'defense': 0.15, 'weight': -0.02},
                'unique_properties': ['flexible', 'protective', 'lightweight'],
                'enchantment_slots': 1
            },
            {
                'name': 'Кольцо силы',
                'base_bonus': 3,
                'bonus_type': 'strength',
                'item_type': 'accessory',
                'accessory_type': 'ring',
                'rarity_weights': [0.4, 0.4, 0.15, 0.05],
                'level_scaling': {'bonus': 0.1},
                'unique_properties': ['enchanted', 'empowering', 'precious'],
                'enchantment_slots': 3
            },
            {
                'name': 'Зелье здоровья',
                'base_heal': 50,
                'duration': 0,
                'item_type': 'consumable',
                'consumable_type': 'potion',
                'rarity_weights': [0.7, 0.2, 0.08, 0.02],
                'level_scaling': {'heal': 0.25},
                'unique_properties': ['refreshing', 'potent', 'pure'],
                'stack_size': 10
            }
        ]
    
    def _load_unique_effect_templates(self) -> List[Dict[str, Any]]:
        """Загрузка шаблонов для генерации уникальных эффектов"""
        return [
            {
                'name': 'Воспламенение',
                'effect_type': 'damage_over_time',
                'base_damage': 8,
                'duration': 5,
                'damage_type': DamageType.FIRE,
                'rarity_weights': [0.6, 0.3, 0.1, 0.0],
                'unique_properties': ['stacking', 'spreading', 'intensifying'],
                'level_scaling': {'damage': 0.15, 'duration': 0.1}
            },
            {
                'name': 'Замедление времени',
                'effect_type': 'debuff',
                'base_effect': 0.3,
                'duration': 3,
                'effect_type_specific': 'slow',
                'rarity_weights': [0.3, 0.5, 0.15, 0.05],
                'unique_properties': ['temporal', 'controlling', 'mystical'],
                'level_scaling': {'effect': 0.1, 'duration': 0.15}
            },
            {
                'name': 'Божественная защита',
                'effect_type': 'buff',
                'base_effect': 20,
                'duration': 8,
                'effect_type_specific': 'defense',
                'rarity_weights': [0.2, 0.4, 0.3, 0.1],
                'unique_properties': ['holy', 'protective', 'blessed'],
                'level_scaling': {'effect': 0.25, 'duration': 0.2}
            }
        ]
    
    def generate_unique_skill(self, session_id: str, level: int, skill_type: str = None) -> ContentItem:
        """Генерация уникального скилла"""
        if skill_type is None:
            skill_type = self.random_generator.weighted_choice(['combat', 'utility', 'support'], [0.6, 0.25, 0.15])
        
        # Выбираем подходящий шаблон
        suitable_templates = [t for t in self.skill_generation_templates if t['skill_type'] == skill_type]
        if not suitable_templates:
            suitable_templates = self.skill_generation_templates
        
        template = self.random_generator.weighted_choice(suitable_templates, [1.0] * len(suitable_templates))
        
        # Определяем редкость на основе весов
        rarity = self._determine_rarity_from_weights(template['rarity_weights'])
        
        # Генерируем уникальные характеристики
        skill_data = self._generate_skill_data(template, level, rarity)
        
        # Создаем уникальное имя
        unique_name = self._generate_unique_name(template['name'], rarity, level)
        
        content_item = ContentItem(
            uuid=str(uuid.uuid4()),
            content_type=ContentType.SKILL,
            name=unique_name,
            description=skill_data['description'],
            rarity=rarity,
            level_requirement=level,
            session_id=session_id,
            generation_timestamp=time.time(),
            data=skill_data
        )
        
        return content_item
    
    def generate_unique_item(self, session_id: str, level: int, item_type: str = None) -> ContentItem:
        """Генерация уникального предмета"""
        if item_type is None:
            item_type = self.random_generator.weighted_choice(['weapon', 'armor', 'accessory', 'consumable'], [0.4, 0.3, 0.2, 0.1])
        
        # Выбираем подходящий шаблон
        suitable_templates = [t for t in self.item_generation_templates if t['item_type'] == item_type]
        if not suitable_templates:
            suitable_templates = self.item_generation_templates
        
        template = self.random_generator.weighted_choice(suitable_templates, [1.0] * len(suitable_templates))
        
        # Определяем редкость на основе весов
        rarity = self._determine_rarity_from_weights(template['rarity_weights'])
        
        # Генерируем уникальные характеристики
        item_data = self._generate_item_data(template, level, rarity)
        
        # Создаем уникальное имя
        unique_name = self._generate_unique_name(template['name'], rarity, level)
        
        content_item = ContentItem(
            uuid=str(uuid.uuid4()),
            content_type=ContentType.ITEM,
            name=unique_name,
            description=item_data['description'],
            rarity=rarity,
            level_requirement=level,
            session_id=session_id,
            generation_timestamp=time.time(),
            data=item_data
        )
        
        return content_item
    
    def _generate_skill_data(self, template: Dict[str, Any], level: int, rarity: ContentRarity) -> Dict[str, Any]:
        """Генерация данных скилла на основе шаблона"""
        rarity_multiplier = self._get_rarity_multiplier(rarity)
        
        # Базовые характеристики
        damage = int(template['base_damage'] * (1 + level * template['level_scaling']['damage']) * rarity_multiplier)
        mana_cost = int(template['mana_cost'] * (1 + level * template['level_scaling']['mana_cost']))
        cooldown = max(0.5, template['cooldown'] * (1 + level * template['level_scaling']['cooldown']))
        
        # Уникальные свойства
        unique_properties = self._generate_unique_properties(template, rarity)
        
        skill_data = {
            'template': template['name'],
            'damage': damage,
            'mana_cost': mana_cost,
            'cooldown': cooldown,
            'range': template['range'],
            'cast_time': template['cast_time'],
            'skill_type': template['skill_type'],
            'target_type': template['target_type'],
            'effects': template['effects'],
            'unique_properties': unique_properties,
            'rarity': rarity.value,
            'level': level
        }
        
        # Генерируем описание
        skill_data['description'] = self._generate_skill_description(skill_data)
        
        return skill_data
    
    def _generate_item_data(self, template: Dict[str, Any], level: int, rarity: ContentRarity) -> Dict[str, Any]:
        """Генерация данных предмета на основе шаблона"""
        rarity_multiplier = self._get_rarity_multiplier(rarity)
        
        # Базовые характеристики
        if 'base_damage' in template:
            damage = int(template['base_damage'] * (1 + level * template['level_scaling']['damage']) * rarity_multiplier)
        elif 'base_defense' in template:
            defense = int(template['base_defense'] * (1 + level * template['level_scaling']['defense']) * rarity_multiplier)
        elif 'base_bonus' in template:
            bonus = int(template['base_bonus'] * (1 + level * template['level_scaling']['bonus']) * rarity_multiplier)
        elif 'base_heal' in template:
            heal = int(template['base_heal'] * (1 + level * template['level_scaling']['heal']) * rarity_multiplier)
        
        # Уникальные свойства
        unique_properties = self._generate_unique_properties(template, rarity)
        
        item_data = {
            'template': template['name'],
            'item_type': template['item_type'],
            'rarity': rarity.value,
            'level': level,
            'unique_properties': unique_properties
        }
        
        # Добавляем специфичные характеристики
        if 'base_damage' in template:
            item_data['damage'] = damage
        if 'base_defense' in template:
            item_data['defense'] = defense
        if 'base_bonus' in template:
            item_data['bonus'] = bonus
            item_data['bonus_type'] = template['bonus_type']
        if 'base_heal' in template:
            item_data['heal'] = heal
        
        # Генерируем описание
        item_data['description'] = self._generate_item_description(item_data)
        
        return item_data
    
    def _generate_unique_properties(self, template: Dict[str, Any], rarity: ContentRarity) -> List[str]:
        """Генерация уникальных свойств предмета/скилла"""
        base_properties = template.get('unique_properties', [])
        rarity_bonus = self._get_rarity_property_bonus(rarity)
        
        # Выбираем случайные свойства
        selected_properties = self.random_generator.weighted_choice(
            base_properties, 
            [1.0] * len(base_properties),
            count=min(len(base_properties), rarity_bonus)
        )
        
        # Добавляем случайные уникальные свойства
        unique_properties = [
            'enchanted', 'ancient', 'corrupted', 'blessed', 'cursed',
            'elemental', 'temporal', 'spatial', 'ethereal', 'material'
        ]
        
        additional_properties = self.random_generator.weighted_choice(
            unique_properties,
            [0.1] * len(unique_properties),
            count=rarity_bonus - len(selected_properties)
        )
        
        return selected_properties + additional_properties
    
    def _generate_unique_name(self, base_name: str, rarity: ContentRarity, level: int) -> str:
        """Генерация уникального имени"""
        rarity_prefixes = {
            ContentRarity.COMMON: ['Обычный', 'Простой', 'Базовый'],
            ContentRarity.UNCOMMON: ['Улучшенный', 'Качественный', 'Надежный'],
            ContentRarity.RARE: ['Редкий', 'Мощный', 'Древний'],
            ContentRarity.LEGENDARY: ['Легендарный', 'Мифический', 'Божественный']
        }
        
        level_suffixes = {
            1: ['Новичка', 'Ученика'],
            5: ['Подмастерья', 'Опытного'],
            10: ['Мастера', 'Эксперта'],
            15: ['Великого', 'Легендарного'],
            20: ['Божественного', 'Мифического']
        }
        
        # Выбираем префикс и суффикс
        prefix = self.random_generator.weighted_choice(rarity_prefixes[rarity], [1.0] * len(rarity_prefixes[rarity]))
        
        # Определяем подходящий суффикс уровня
        suitable_levels = [l for l in level_suffixes.keys() if l <= level]
        if suitable_levels:
            level_key = max(suitable_levels)
            suffix = self.random_generator.weighted_choice(level_suffixes[level_key], [1.0] * len(level_suffixes[level_key]))
        else:
            suffix = 'Новичка'
        
        return f"{prefix} {base_name} {suffix}"
    
    def _generate_skill_description(self, skill_data: Dict[str, Any]) -> str:
        """Генерация описания скилла"""
        template = skill_data['template']
        damage = skill_data.get('damage', 0)
        effects = skill_data.get('effects', [])
        unique_properties = skill_data.get('unique_properties', [])
        
        description_parts = [f"Скилл {template}"]
        
        if damage > 0:
            description_parts.append(f"наносит {damage} урона")
        
        if effects:
            effect_descriptions = {
                'burn': 'поджигает цель',
                'freeze': 'замораживает цель',
                'shock': 'оглушает цель',
                'poison': 'отравляет цель',
                'heal': 'исцеляет союзника',
                'regeneration': 'восстанавливает здоровье со временем',
                'slow': 'замедляет цель',
                'chain': 'поражает несколько целей',
                'area_damage': 'наносит урон по области'
            }
            
            effect_texts = [effect_descriptions.get(effect, effect) for effect in effects if effect in effect_descriptions]
            if effect_texts:
                description_parts.append(f"и {', '.join(effect_texts)}")
        
        if unique_properties:
            property_descriptions = {
                'enchanted': 'зачарован',
                'ancient': 'древний',
                'corrupted': 'испорчен',
                'blessed': 'благословлен',
                'cursed': 'проклят',
                'elemental': 'стихийный',
                'temporal': 'временной',
                'spatial': 'пространственный',
                'ethereal': 'эфирный',
                'material': 'материальный'
            }
            
            property_texts = [property_descriptions.get(prop, prop) for prop in unique_properties if prop in property_descriptions]
            if property_texts:
                description_parts.append(f"Скилл {', '.join(property_texts)}")
        
        return '. '.join(description_parts) + '.'
    
    def _generate_item_description(self, item_data: Dict[str, Any]) -> str:
        """Генерация описания предмета"""
        template = item_data['template']
        item_type = item_data['item_type']
        unique_properties = item_data.get('unique_properties', [])
        
        description_parts = [f"{template} - {item_type}"]
        
        # Добавляем характеристики
        if 'damage' in item_data:
            description_parts.append(f"с уроном {item_data['damage']}")
        elif 'defense' in item_data:
            description_parts.append(f"с защитой {item_data['defense']}")
        elif 'bonus' in item_data:
            description_parts.append(f"даёт +{item_data['bonus']} к {item_data['bonus_type']}")
        elif 'heal' in item_data:
            description_parts.append(f"восстанавливает {item_data['heal']} здоровья")
        
        if unique_properties:
            property_descriptions = {
                'enchanted': 'зачарован',
                'ancient': 'древний',
                'corrupted': 'испорчен',
                'blessed': 'благословлен',
                'cursed': 'проклят',
                'elemental': 'стихийный',
                'temporal': 'временной',
                'spatial': 'пространственный',
                'ethereal': 'эфирный',
                'material': 'материальный'
            }
            
            property_texts = [property_descriptions.get(prop, prop) for prop in unique_properties if prop in property_descriptions]
            if property_texts:
                description_parts.append(f"Предмет {', '.join(property_texts)}")
        
        return '. '.join(description_parts) + '.'
    
    def _determine_rarity_from_weights(self, weights: List[float]) -> ContentRarity:
        """Определение редкости на основе весов"""
        rarity_values = [ContentRarity.COMMON, ContentRarity.UNCOMMON, ContentRarity.RARE, ContentRarity.LEGENDARY]
        return self.random_generator.weighted_choice(rarity_values, weights)
    
    def _get_rarity_multiplier(self, rarity: ContentRarity) -> float:
        """Получение множителя редкости"""
        rarity_multipliers = {
            ContentRarity.COMMON: 1.0,
            ContentRarity.UNCOMMON: 1.3,
            ContentRarity.RARE: 1.8,
            ContentRarity.LEGENDARY: 2.5
        }
        return rarity_multipliers.get(rarity, 1.0)
    
    def _get_rarity_property_bonus(self, rarity: ContentRarity) -> int:
        """Получение бонуса к количеству свойств на основе редкости"""
        rarity_bonuses = {
            ContentRarity.COMMON: 1,
            ContentRarity.UNCOMMON: 2,
            ContentRarity.RARE: 3,
            ContentRarity.LEGENDARY: 5
        }
        return rarity_bonuses.get(rarity, 1)
