#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СИСТЕМА ГЕНЕРАЦИИ КОНТЕНТА ДЛЯ РОГЛАЙК
Генерация предметов, врагов, скиллов и контента для каждой сессии
Соблюдает принцип единой ответственности
"""

import random
import time
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from utils.logging_system import get_logger, log_system_event

class ContentType(Enum):
    """Типы контента"""
    ITEM = "item"
    ENEMY = "enemy"
    BOSS = "boss"
    SKILL = "skill"
    TRAP = "trap"
    CHEST = "chest"
    LIGHTHOUSE = "lighthouse"

class ItemRarity(Enum):
    """Редкость предметов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class EnemyType(Enum):
    """Типы врагов"""
    BASIC = "basic"
    BOSS = "boss"
    CHIMERA = "chimera"

@dataclass
class GeneratedItem:
    """Сгенерированный предмет"""
    item_id: str
    name: str
    item_type: str
    rarity: ItemRarity
    base_stats: Dict[str, float] = field(default_factory=dict)
    special_effects: List[Dict[str, Any]] = field(default_factory=list)
    active_skills: List[str] = field(default_factory=list)
    trigger_skills: List[str] = field(default_factory=list)
    basic_attack_skill: str = ""
    requirements: Dict[str, int] = field(default_factory=dict)
    description: str = ""
    generated_at: float = field(default_factory=time.time)

@dataclass
class GeneratedEnemy:
    """Сгенерированный враг"""
    enemy_id: str
    name: str
    enemy_type: EnemyType
    base_stats: Dict[str, float] = field(default_factory=dict)
    resistances: Dict[str, float] = field(default_factory=dict)
    weaknesses: Dict[str, float] = field(default_factory=dict)
    skill_set: List[str] = field(default_factory=list)
    ai_behavior: str = "basic"
    learning_rate: float = 0.05
    phases: int = 1
    loot_table: List[str] = field(default_factory=list)
    generated_at: float = field(default_factory=time.time)

@dataclass
class GeneratedSkill:
    """Сгенерированный скилл"""
    skill_id: str
    name: str
    skill_type: str  # active, passive, trigger
    description: str
    effects: Dict[str, Any] = field(default_factory=dict)
    cooldown: float = 0.0
    mana_cost: int = 0
    requirements: Dict[str, int] = field(default_factory=dict)
    generated_at: float = field(default_factory=time.time)

@dataclass
class SessionContent:
    """Контент сессии"""
    session_id: str
    items: Dict[str, GeneratedItem] = field(default_factory=dict)
    enemies: Dict[str, GeneratedEnemy] = field(default_factory=dict)
    skills: Dict[str, GeneratedSkill] = field(default_factory=dict)
    lighthouse_location: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    generated_at: float = field(default_factory=time.time)

class RoguelikeContentGenerator:
    """Генератор контента для роглайк"""
    
    def __init__(self, content_directory: str = "content/generated"):
        self.content_directory = Path(content_directory)
        self.content_directory.mkdir(parents=True, exist_ok=True)
        
        self.logger = get_logger(__name__)
        
        # Шаблоны для генерации
        self.item_templates = self._load_item_templates()
        self.enemy_templates = self._load_enemy_templates()
        self.skill_templates = self._load_skill_templates()
        
        # Настройки генерации
        self.items_per_session = 50
        self.enemies_per_session = 30
        self.skills_per_session = 20
        self.boss_count = 2
        self.chimera_count = 1
        
        log_system_event("roguelike_content_generator", "initialized")
    
    def generate_session_content(self, session_id: str, difficulty_level: int = 1) -> SessionContent:
        """Генерация контента для сессии"""
        try:
            self.logger.info(f"Generating content for session {session_id}")
            
            session_content = SessionContent(session_id=session_id)
            
            # Генерируем предметы
            session_content.items = self._generate_items(difficulty_level)
            
            # Генерируем врагов
            session_content.enemies = self._generate_enemies(difficulty_level)
            
            # Генерируем скиллы
            session_content.skills = self._generate_skills(difficulty_level)
            
            # Генерируем локацию маяка
            session_content.lighthouse_location = self._generate_lighthouse_location()
            
            # Сохраняем контент сессии
            self._save_session_content(session_content)
            
            log_system_event("roguelike_content_generator", "session_content_generated", {
                "session_id": session_id,
                "items_count": len(session_content.items),
                "enemies_count": len(session_content.enemies),
                "skills_count": len(session_content.skills)
            })
            
            return session_content
            
        except Exception as e:
            self.logger.error(f"Error generating session content: {e}")
            return SessionContent(session_id=session_id)
    
    def _generate_items(self, difficulty_level: int) -> Dict[str, GeneratedItem]:
        """Генерация предметов"""
        items = {}
        
        for i in range(self.items_per_session):
            item_id = f"item_{uuid.uuid4().hex[:8]}"
            
            # Выбираем тип предмета
            item_type = random.choice(["weapon", "armor", "consumable", "accessory"])
            
            # Генерируем редкость на основе сложности
            rarity = self._get_rarity_by_difficulty(difficulty_level)
            
            # Создаем предмет
            item = GeneratedItem(
                item_id=item_id,
                name=self._generate_item_name(item_type, rarity),
                item_type=item_type,
                rarity=rarity,
                base_stats=self._generate_item_stats(item_type, rarity, difficulty_level),
                special_effects=self._generate_item_effects(item_type, rarity),
                active_skills=self._generate_active_skills(item_type),
                trigger_skills=self._generate_trigger_skills(item_type),
                basic_attack_skill=self._generate_basic_attack_skill(item_type),
                requirements=self._generate_item_requirements(rarity, difficulty_level),
                description=self._generate_item_description(item_type, rarity)
            )
            
            items[item_id] = item
        
        return items
    
    def _generate_enemies(self, difficulty_level: int) -> Dict[str, GeneratedEnemy]:
        """Генерация врагов"""
        enemies = {}
        
        # Обычные враги
        basic_count = self.enemies_per_session - self.boss_count - self.chimera_count
        for i in range(basic_count):
            enemy_id = f"enemy_{uuid.uuid4().hex[:8]}"
            
            enemy = GeneratedEnemy(
                enemy_id=enemy_id,
                name=self._generate_enemy_name(),
                enemy_type=EnemyType.BASIC,
                base_stats=self._generate_enemy_stats(EnemyType.BASIC, difficulty_level),
                resistances=self._generate_resistances(),
                weaknesses=self._generate_weaknesses(),
                skill_set=self._generate_enemy_skills(EnemyType.BASIC),
                ai_behavior="basic",
                learning_rate=0.05,  # Низкая скорость обучения для обычных врагов
                phases=1,
                loot_table=self._generate_loot_table(EnemyType.BASIC)
            )
            
            enemies[enemy_id] = enemy
        
        # Боссы
        for i in range(self.boss_count):
            boss_id = f"boss_{uuid.uuid4().hex[:8]}"
            
            boss = GeneratedEnemy(
                enemy_id=boss_id,
                name=self._generate_boss_name(),
                enemy_type=EnemyType.BOSS,
                base_stats=self._generate_enemy_stats(EnemyType.BOSS, difficulty_level),
                resistances=self._generate_resistances(),
                weaknesses=self._generate_weaknesses(),
                skill_set=self._generate_enemy_skills(EnemyType.BOSS),
                ai_behavior="advanced",
                learning_rate=0.01,  # Еще более низкая скорость обучения для боссов
                phases=random.randint(2, 4),  # Многофазовые боссы
                loot_table=self._generate_loot_table(EnemyType.BOSS)
            )
            
            enemies[boss_id] = boss
        
        # Химеры
        for i in range(self.chimera_count):
            chimera_id = f"chimera_{uuid.uuid4().hex[:8]}"
            
            chimera = GeneratedEnemy(
                enemy_id=chimera_id,
                name=self._generate_chimera_name(),
                enemy_type=EnemyType.CHIMERA,
                base_stats=self._generate_enemy_stats(EnemyType.CHIMERA, difficulty_level),
                resistances=self._generate_resistances(),
                weaknesses=self._generate_weaknesses(),
                skill_set=self._generate_enemy_skills(EnemyType.CHIMERA),
                ai_behavior="adaptive",
                learning_rate=0.02,  # Средняя скорость обучения для химер
                phases=random.randint(2, 3),  # Многофазовые химеры
                loot_table=self._generate_loot_table(EnemyType.CHIMERA)
            )
            
            enemies[chimera_id] = chimera
        
        return enemies
    
    def _generate_skills(self, difficulty_level: int) -> Dict[str, GeneratedSkill]:
        """Генерация скиллов"""
        skills = {}
        
        for i in range(self.skills_per_session):
            skill_id = f"skill_{uuid.uuid4().hex[:8]}"
            
            skill_type = random.choice(["active", "passive", "trigger"])
            
            skill = GeneratedSkill(
                skill_id=skill_id,
                name=self._generate_skill_name(skill_type),
                skill_type=skill_type,
                description=self._generate_skill_description(skill_type),
                effects=self._generate_skill_effects(skill_type, difficulty_level),
                cooldown=random.uniform(1.0, 30.0) if skill_type == "active" else 0.0,
                mana_cost=random.randint(5, 50) if skill_type == "active" else 0,
                requirements=self._generate_skill_requirements(difficulty_level)
            )
            
            skills[skill_id] = skill
        
        return skills
    
    def _generate_lighthouse_location(self) -> Tuple[float, float, float]:
        """Генерация локации маяка"""
        # Маяк размещается в случайном месте на карте
        x = random.uniform(-50.0, 50.0)
        y = random.uniform(-50.0, 50.0)
        z = 0.0  # На уровне земли
        
        return (x, y, z)
    
    def _get_rarity_by_difficulty(self, difficulty_level: int) -> ItemRarity:
        """Получение редкости на основе сложности"""
        if difficulty_level <= 2:
            return random.choices(
                [ItemRarity.COMMON, ItemRarity.UNCOMMON, ItemRarity.RARE],
                weights=[70, 25, 5]
            )[0]
        elif difficulty_level <= 4:
            return random.choices(
                [ItemRarity.COMMON, ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.EPIC],
                weights=[50, 30, 15, 5]
            )[0]
        else:
            return random.choices(
                [ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY],
                weights=[40, 35, 20, 5]
            )[0]
    
    def _generate_item_name(self, item_type: str, rarity: ItemRarity) -> str:
        """Генерация названия предмета"""
        prefixes = {
            ItemRarity.COMMON: ["Simple", "Basic", "Rusty"],
            ItemRarity.UNCOMMON: ["Fine", "Quality", "Sturdy"],
            ItemRarity.RARE: ["Superior", "Masterwork", "Enchanted"],
            ItemRarity.EPIC: ["Legendary", "Mythic", "Divine"],
            ItemRarity.LEGENDARY: ["Ancient", "Primordial", "Transcendent"]
        }
        
        suffixes = {
            "weapon": ["Blade", "Sword", "Axe", "Mace", "Bow"],
            "armor": ["Armor", "Mail", "Plate", "Robe", "Cloak"],
            "consumable": ["Potion", "Elixir", "Scroll", "Crystal"],
            "accessory": ["Ring", "Amulet", "Bracelet", "Talisman"]
        }
        
        prefix = random.choice(prefixes[rarity])
        suffix = random.choice(suffixes[item_type])
        
        return f"{prefix} {suffix}"
    
    def _generate_item_stats(self, item_type: str, rarity: ItemRarity, difficulty_level: int) -> Dict[str, float]:
        """Генерация характеристик предмета"""
        base_multiplier = {
            ItemRarity.COMMON: 1.0,
            ItemRarity.UNCOMMON: 1.2,
            ItemRarity.RARE: 1.5,
            ItemRarity.EPIC: 2.0,
            ItemRarity.LEGENDARY: 3.0
        }[rarity]
        
        difficulty_multiplier = 1.0 + (difficulty_level - 1) * 0.2
        
        stats = {}
        
        if item_type == "weapon":
            stats = {
                "damage": random.uniform(10, 50) * base_multiplier * difficulty_multiplier,
                "attack_speed": random.uniform(0.8, 1.5),
                "critical_chance": random.uniform(0.05, 0.25) * base_multiplier
            }
        elif item_type == "armor":
            stats = {
                "defense": random.uniform(5, 30) * base_multiplier * difficulty_multiplier,
                "resistance": random.uniform(0.1, 0.4) * base_multiplier,
                "health_bonus": random.uniform(10, 100) * base_multiplier * difficulty_multiplier
            }
        elif item_type == "consumable":
            stats = {
                "healing": random.uniform(20, 100) * base_multiplier * difficulty_multiplier,
                "duration": random.uniform(10, 60)
            }
        elif item_type == "accessory":
            stats = {
                "mana_bonus": random.uniform(10, 50) * base_multiplier * difficulty_multiplier,
                "skill_cooldown_reduction": random.uniform(0.05, 0.2) * base_multiplier
            }
        
        return stats
    
    def _generate_item_effects(self, item_type: str, rarity: ItemRarity) -> List[Dict[str, Any]]:
        """Генерация специальных эффектов предмета"""
        effects = []
        
        if rarity in [ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY]:
            effect_count = {
                ItemRarity.RARE: 1,
                ItemRarity.EPIC: 2,
                ItemRarity.LEGENDARY: 3
            }[rarity]
            
            for _ in range(effect_count):
                effect = {
                    "type": random.choice(["damage_bonus", "healing_bonus", "speed_bonus", "resistance_bonus"]),
                    "value": random.uniform(0.1, 0.5),
                    "duration": random.uniform(5, 30)
                }
                effects.append(effect)
        
        return effects
    
    def _generate_active_skills(self, item_type: str) -> List[str]:
        """Генерация активных скиллов для предмета"""
        if item_type == "weapon":
            return [f"weapon_skill_{random.randint(1, 5)}"]
        return []
    
    def _generate_trigger_skills(self, item_type: str) -> List[str]:
        """Генерация триггерных скиллов для предмета"""
        if random.random() < 0.3:  # 30% шанс
            return [f"trigger_skill_{random.randint(1, 3)}"]
        return []
    
    def _generate_basic_attack_skill(self, item_type: str) -> str:
        """Генерация базового скилла атаки для оружия"""
        if item_type == "weapon":
            weapon_types = ["sword", "axe", "mace", "bow", "staff"]
            weapon_type = random.choice(weapon_types)
            return f"{weapon_type}_basic_attack"
        return ""
    
    def _generate_item_requirements(self, rarity: ItemRarity, difficulty_level: int) -> Dict[str, int]:
        """Генерация требований для предмета"""
        requirements = {}
        
        if rarity in [ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY]:
            requirements["level"] = random.randint(1, difficulty_level * 5)
            requirements["strength"] = random.randint(10, 50)
        
        return requirements
    
    def _generate_item_description(self, item_type: str, rarity: ItemRarity) -> str:
        """Генерация описания предмета"""
        descriptions = {
            "weapon": f"A {rarity.value} weapon with unique properties.",
            "armor": f"Protective {rarity.value} armor that enhances your abilities.",
            "consumable": f"A {rarity.value} consumable item with magical properties.",
            "accessory": f"An enchanted {rarity.value} accessory that provides various bonuses."
        }
        
        return descriptions.get(item_type, f"A {rarity.value} item.")
    
    def _generate_enemy_name(self) -> str:
        """Генерация имени врага"""
        prefixes = ["Dark", "Shadow", "Corrupted", "Ancient", "Feral"]
        suffixes = ["Beast", "Creature", "Monster", "Abomination", "Horror"]
        
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        
        return f"{prefix} {suffix}"
    
    def _generate_boss_name(self) -> str:
        """Генерация имени босса"""
        titles = ["Lord", "Master", "Overlord", "Tyrant", "Destroyer"]
        names = ["Malachar", "Zephyros", "Nyx", "Vortex", "Tempest"]
        
        title = random.choice(titles)
        name = random.choice(names)
        
        return f"{title} {name}"
    
    def _generate_chimera_name(self) -> str:
        """Генерация имени химеры"""
        prefixes = ["Fusion", "Hybrid", "Twisted", "Corrupted", "Mutated"]
        suffixes = ["Beast", "Abomination", "Horror", "Monster", "Creature"]
        
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        
        return f"{prefix} {suffix}"
    
    def _generate_enemy_stats(self, enemy_type: EnemyType, difficulty_level: int) -> Dict[str, float]:
        """Генерация характеристик врага"""
        base_stats = {
            EnemyType.BASIC: {"health": 50, "damage": 10, "speed": 1.0},
            EnemyType.BOSS: {"health": 500, "damage": 50, "speed": 0.8},
            EnemyType.CHIMERA: {"health": 300, "damage": 35, "speed": 1.2}
        }
        
        stats = base_stats[enemy_type].copy()
        difficulty_multiplier = 1.0 + (difficulty_level - 1) * 0.3
        
        for stat in stats:
            stats[stat] *= difficulty_multiplier
        
        return stats
    
    def _generate_resistances(self) -> Dict[str, float]:
        """Генерация сопротивлений врага"""
        damage_types = ["physical", "fire", "cold", "lightning", "acid", "poison"]
        resistances = {}
        
        for damage_type in damage_types:
            if random.random() < 0.3:  # 30% шанс сопротивления
                resistances[damage_type] = random.uniform(0.1, 0.5)
        
        return resistances
    
    def _generate_weaknesses(self) -> Dict[str, float]:
        """Генерация слабостей врага"""
        damage_types = ["physical", "fire", "cold", "lightning", "acid", "poison"]
        weaknesses = {}
        
        for damage_type in damage_types:
            if random.random() < 0.2:  # 20% шанс слабости
                weaknesses[damage_type] = random.uniform(0.1, 0.3)
        
        return weaknesses
    
    def _generate_enemy_skills(self, enemy_type: EnemyType) -> List[str]:
        """Генерация скиллов врага"""
        skill_count = {
            EnemyType.BASIC: 1,      # Минимальный набор скиллов
            EnemyType.BOSS: 5,       # Большой набор скиллов
            EnemyType.CHIMERA: 3     # Средний набор скиллов
        }[enemy_type]
        
        skills = []
        for i in range(skill_count):
            skills.append(f"enemy_skill_{random.randint(1, 10)}")
        
        return skills
    
    def _generate_loot_table(self, enemy_type: EnemyType) -> List[str]:
        """Генерация таблицы лута врага"""
        loot_count = {
            EnemyType.BASIC: 1,      # Минимальный лут
            EnemyType.BOSS: 5,       # Много лута
            EnemyType.CHIMERA: 3     # Средний лут
        }[enemy_type]
        
        loot = []
        for i in range(loot_count):
            loot.append(f"loot_item_{random.randint(1, 20)}")
        
        return loot
    
    def _generate_skill_name(self, skill_type: str) -> str:
        """Генерация названия скилла"""
        names = {
            "active": ["Fireball", "Lightning Strike", "Heal", "Shield", "Teleport"],
            "passive": ["Regeneration", "Resistance", "Speed Boost", "Damage Bonus"],
            "trigger": ["Counter Attack", "Auto Heal", "Reflect Damage", "Explosive Death"]
        }
        
        return random.choice(names[skill_type])
    
    def _generate_skill_description(self, skill_type: str) -> str:
        """Генерация описания скилла"""
        descriptions = {
            "active": "An active ability that can be used in combat.",
            "passive": "A passive ability that provides constant benefits.",
            "trigger": "An ability that triggers under specific conditions."
        }
        
        return descriptions[skill_type]
    
    def _generate_skill_effects(self, skill_type: str, difficulty_level: int) -> Dict[str, Any]:
        """Генерация эффектов скилла"""
        effects = {
            "type": skill_type,
            "power": random.uniform(1.0, 5.0) * (1.0 + difficulty_level * 0.2),
            "duration": random.uniform(1.0, 10.0),
            "range": random.uniform(1.0, 10.0)
        }
        
        return effects
    
    def _generate_skill_requirements(self, difficulty_level: int) -> Dict[str, int]:
        """Генерация требований для скилла"""
        requirements = {
            "level": random.randint(1, difficulty_level * 3),
            "mana": random.randint(10, 100)
        }
        
        return requirements
    
    def _save_session_content(self, session_content: SessionContent):
        """Сохранение контента сессии"""
        try:
            content_file = self.content_directory / f"{session_content.session_id}_content.json"
            
            # Конвертируем в словарь для JSON
            content_data = {
                "session_id": session_content.session_id,
                "items": {item_id: {
                    "item_id": item.item_id,
                    "name": item.name,
                    "item_type": item.item_type,
                    "rarity": item.rarity.value,
                    "base_stats": item.base_stats,
                    "special_effects": item.special_effects,
                    "active_skills": item.active_skills,
                    "trigger_skills": item.trigger_skills,
                    "basic_attack_skill": item.basic_attack_skill,
                    "requirements": item.requirements,
                    "description": item.description,
                    "generated_at": item.generated_at
                } for item_id, item in session_content.items.items()},
                "enemies": {enemy_id: {
                    "enemy_id": enemy.enemy_id,
                    "name": enemy.name,
                    "enemy_type": enemy.enemy_type.value,
                    "base_stats": enemy.base_stats,
                    "resistances": enemy.resistances,
                    "weaknesses": enemy.weaknesses,
                    "skill_set": enemy.skill_set,
                    "ai_behavior": enemy.ai_behavior,
                    "learning_rate": enemy.learning_rate,
                    "phases": enemy.phases,
                    "loot_table": enemy.loot_table,
                    "generated_at": enemy.generated_at
                } for enemy_id, enemy in session_content.enemies.items()},
                "skills": {skill_id: {
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "skill_type": skill.skill_type,
                    "description": skill.description,
                    "effects": skill.effects,
                    "cooldown": skill.cooldown,
                    "mana_cost": skill.mana_cost,
                    "requirements": skill.requirements,
                    "generated_at": skill.generated_at
                } for skill_id, skill in session_content.skills.items()},
                "lighthouse_location": session_content.lighthouse_location,
                "generated_at": session_content.generated_at
            }
            
            with open(content_file, 'w', encoding='utf-8') as f:
                json.dump(content_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved session content to {content_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving session content: {e}")
    
    def _load_item_templates(self) -> Dict[str, Any]:
        """Загрузка шаблонов предметов"""
        # В реальной реализации здесь была бы загрузка из файла
        return {
            "weapon": {"base_damage": 10, "base_speed": 1.0},
            "armor": {"base_defense": 5, "base_resistance": 0.1},
            "consumable": {"base_healing": 20, "base_duration": 10},
            "accessory": {"base_mana": 10, "base_cooldown_reduction": 0.05}
        }
    
    def _load_enemy_templates(self) -> Dict[str, Any]:
        """Загрузка шаблонов врагов"""
        # В реальной реализации здесь была бы загрузка из файла
        return {
            "basic": {"base_health": 50, "base_damage": 10},
            "elite": {"base_health": 100, "base_damage": 20},
            "boss": {"base_health": 500, "base_damage": 50}
        }
    
    def _load_skill_templates(self) -> Dict[str, Any]:
        """Загрузка шаблонов скиллов"""
        # В реальной реализации здесь была бы загрузка из файла
        return {
            "active": {"base_cooldown": 5.0, "base_mana_cost": 20},
            "passive": {"base_duration": 0.0, "base_mana_cost": 0},
            "trigger": {"base_chance": 0.1, "base_mana_cost": 0}
        }
