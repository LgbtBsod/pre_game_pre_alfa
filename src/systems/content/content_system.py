#!/usr/bin/env python3
"""Система контента - управление сессиями и процедурная генерация
Обеспечивает генерацию уникального контента для каждой сессии"""

import json
import logging
import os
import sqlite3
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from ...core.constants import (
    DamageType,
    EmotionType, GeneType, EvolutionType, constants_manager
)
from ..items.item_system import ItemType, ItemRarity
from ..skills.skill_system import SkillType
from ...core.constants_extended import (
    BiomeType, StructureType, EnemyType, BossPhase, QuestType,
    CONTENT_GENERATION_CONSTANTS, SESSION_GENERATION_CONSTANTS
)
from ...core.architecture import BaseComponent
from ...core.component_manager import ComponentType, Priority

logger = logging.getLogger(__name__)

@dataclass
class SessionData:
    """Данные сессии"""
    session_id: str
    name: str
    created_at: float
    last_accessed: float
    player_level: int
    world_seed: int
    content_hash: str
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentItem:
    """Элемент контента"""
    id: str
    session_id: str
    content_type: str
    name: str
    data: Dict[str, Any]
    created_at: float
    level_requirement: int
    evolution_requirement: int
    memory_requirement: int
    rarity: str
    is_unique: bool = True

@dataclass
class BossContent:
    """Контент босса"""
    name: str
    level: int
    health: int
    damage: int
    skills: List[Dict[str, Any]]
    phases: List[Dict[str, Any]]
    evolution_stage: int
    memory_capacity: int
    rewards: Dict[str, Any]
    behavior: Dict[str, Any]

@dataclass
class WeaponContent:
    """Контент оружия"""
    name: str
    weapon_type: str
    damage: int
    damage_type: str
    stats: Dict[str, int]
    skills: List[Dict[str, Any]]
    level_requirement: int
    rarity: str
    evolution_bonus: float
    memory_bonus: float

@dataclass
class JewelryContent:
    """Контент украшений"""
    name: str
    jewelry_type: str
    stats: Dict[str, int]
    effects: List[Dict[str, Any]]
    skills: List[Dict[str, Any]]
    level_requirement: int
    rarity: str
    evolution_bonus: float
    memory_bonus: float

@dataclass
class SkillContent:
    """Контент навыка"""
    name: str
    skill_type: str
    description: str
    base_power: int
    scaling: Dict[str, float]
    effects: List[Dict[str, Any]]
    cooldown: float
    mana_cost: int
    level_requirement: int
    evolution_requirement: int
    memory_requirement: int

class ContentDatabase:
    """База данных контента"""
    
    def __init__(self, db_path: str = "content.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Инициализация базы данных"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Таблица сессий
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    last_accessed REAL NOT NULL,
                    player_level INTEGER NOT NULL,
                    world_seed INTEGER NOT NULL,
                    content_hash TEXT NOT NULL,
                    is_active INTEGER NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Таблица контента
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    level_requirement INTEGER NOT NULL,
                    evolution_requirement INTEGER NOT NULL,
                    memory_requirement INTEGER NOT NULL,
                    rarity TEXT NOT NULL,
                    is_unique INTEGER NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            ''')
            
            # Индексы для быстрого поиска
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_session ON content (session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_type ON content (content_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_level ON content (level_requirement)')
            
            conn.commit()
            conn.close()
            
            logger.info(f"База данных контента инициализирована: {self.db_path}")
    
    def save_session(self, session: SessionData) -> bool:
        """Сохранение сессии"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO sessions 
                    (session_id, name, created_at, last_accessed, player_level, 
                     world_seed, content_hash, is_active, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session.session_id, session.name, session.created_at,
                    session.last_accessed, session.player_level, session.world_seed,
                    session.content_hash, session.is_active, json.dumps(session.metadata)
                ))
                
                conn.commit()
                conn.close()
                return True
                
        except Exception as e:
            logger.error(f"Ошибка сохранения сессии: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[SessionData]:
        """Загрузка сессии"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT session_id, name, created_at, last_accessed, player_level,
                           world_seed, content_hash, is_active, metadata
                    FROM sessions WHERE session_id = ?
                ''', (session_id,))
                
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    return SessionData(
                        session_id=row[0],
                        name=row[1],
                        created_at=row[2],
                        last_accessed=row[3],
                        player_level=row[4],
                        world_seed=row[5],
                        content_hash=row[6],
                        is_active=bool(row[7]),
                        metadata=json.loads(row[8]) if row[8] else {}
                    )
                return None
                
        except Exception as e:
            logger.error(f"Ошибка загрузки сессии: {e}")
            return None
    
    def get_all_sessions(self) -> List[SessionData]:
        """Получение всех сессий"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT session_id, name, created_at, last_accessed, player_level,
                           world_seed, content_hash, is_active, metadata
                    FROM sessions WHERE is_active = 1
                    ORDER BY last_accessed DESC
                ''')
                
                sessions = []
                for row in cursor.fetchall():
                    sessions.append(SessionData(
                        session_id=row[0],
                        name=row[1],
                        created_at=row[2],
                        last_accessed=row[3],
                        player_level=row[4],
                        world_seed=row[5],
                        content_hash=row[6],
                        is_active=bool(row[7]),
                        metadata=json.loads(row[8]) if row[8] else {}
                    ))
                
                conn.close()
                return sessions
                
        except Exception as e:
            logger.error(f"Ошибка получения сессий: {e}")
            return []
    
    def save_content(self, content: ContentItem) -> bool:
        """Сохранение контента"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO content 
                    (id, session_id, content_type, name, data, created_at,
                     level_requirement, evolution_requirement, memory_requirement,
                     rarity, is_unique)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    content.id, content.session_id, content.content_type,
                    content.name, json.dumps(content.data), content.created_at,
                    content.level_requirement, content.evolution_requirement,
                    content.memory_requirement, content.rarity, content.is_unique
                ))
                
                conn.commit()
                conn.close()
                return True
                
        except Exception as e:
            logger.error(f"Ошибка сохранения контента: {e}")
            return False
    
    def load_session_content(self, session_id: str, content_type: Optional[str] = None) -> List[ContentItem]:
        """Загрузка контента сессии"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                if content_type:
                    cursor.execute('''
                        SELECT id, session_id, content_type, name, data, created_at,
                               level_requirement, evolution_requirement, memory_requirement,
                               rarity, is_unique
                        FROM content 
                        WHERE session_id = ? AND content_type = ?
                        ORDER BY created_at DESC
                    ''', (session_id, content_type))
                else:
                    cursor.execute('''
                        SELECT id, session_id, content_type, name, data, created_at,
                               level_requirement, evolution_requirement, memory_requirement,
                               rarity, is_unique
                        FROM content 
                        WHERE session_id = ?
                        ORDER BY created_at DESC
                    ''', (session_id,))
                
                content_items = []
                for row in cursor.fetchall():
                    content_items.append(ContentItem(
                        id=row[0],
                        session_id=row[1],
                        content_type=row[2],
                        name=row[3],
                        data=json.loads(row[4]),
                        created_at=row[5],
                        level_requirement=row[6],
                        evolution_requirement=row[7],
                        memory_requirement=row[8],
                        rarity=row[9],
                        is_unique=bool(row[10])
                    ))
                
                conn.close()
                return content_items
                
        except Exception as e:
            logger.error(f"Ошибка загрузки контента: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Удаление сессии и всего её контента"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Удаление контента сессии
                cursor.execute('DELETE FROM content WHERE session_id = ?', (session_id,))
                
                # Удаление сессии
                cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Сессия {session_id} удалена")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка удаления сессии: {e}")
            return False

class ContentGenerator:
    """Генератор контента"""
    
    def __init__(self):
        self.constants = constants_manager
        self.content_constants = CONTENT_GENERATION_CONSTANTS
        self.session_constants = SESSION_GENERATION_CONSTANTS
        
        # Кэш для оптимизации
        self._content_cache = {}
        self._cache_lock = threading.Lock()
        
        logger.info("Генератор контента инициализирован")
    
    def generate_session_content(self, session_id: str, player_level: int, 
                               world_seed: int, content_types: List[str]) -> List[ContentItem]:
        """Генерация контента для сессии"""
        try:
            content_items = []
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                
                for content_type in content_types:
                    if content_type == "bosses":
                        futures.append(
                            executor.submit(self._generate_bosses, session_id, player_level, world_seed)
                        )
                    elif content_type == "weapons":
                        futures.append(
                            executor.submit(self._generate_weapons, session_id, player_level, world_seed)
                        )
                    elif content_type == "jewelry":
                        futures.append(
                            executor.submit(self._generate_jewelry, session_id, player_level, world_seed)
                        )
                    elif content_type == "skills":
                        futures.append(
                            executor.submit(self._generate_skills, session_id, player_level, world_seed)
                        )
                
                # Сбор результатов
                for future in futures:
                    try:
                        result = future.result(timeout=self.session_constants["content_generation_timeout"])
                        content_items.extend(result)
                    except Exception as e:
                        logger.error(f"Ошибка генерации контента: {e}")
            
            logger.info(f"Сгенерировано {len(content_items)} элементов контента для сессии {session_id}")
            return content_items
            
        except Exception as e:
            logger.error(f"Ошибка генерации контента сессии: {e}")
            return []
    
    def _generate_bosses(self, session_id: str, player_level: int, world_seed: int) -> List[ContentItem]:
        """Генерация боссов"""
        import random
        random.seed(world_seed)
        
        bosses = []
        boss_count = random.randint(3, 8)
        
        for i in range(boss_count):
            boss = self._create_boss_content(session_id, player_level, world_seed + i)
            content_item = ContentItem(
                id=f"boss_{session_id}_{i}",
                session_id=session_id,
                content_type="boss",
                name=boss.name,
                data=asdict(boss),
                created_at=time.time(),
                level_requirement=boss.level,
                evolution_requirement=boss.evolution_stage,
                memory_requirement=boss.memory_capacity,
                rarity="rare" if boss.evolution_stage > 2 else "uncommon"
            )
            bosses.append(content_item)
        
        return bosses
    
    def _generate_weapons(self, session_id: str, player_level: int, world_seed: int) -> List[ContentItem]:
        """Генерация оружия"""
        import random
        random.seed(world_seed)
        
        weapons = []
        weapon_count = random.randint(10, 25)
        
        for i in range(weapon_count):
            weapon = self._create_weapon_content(session_id, player_level, world_seed + i)
            content_item = ContentItem(
                id=f"weapon_{session_id}_{i}",
                session_id=session_id,
                content_type="weapon",
                name=weapon.name,
                data=asdict(weapon),
                created_at=time.time(),
                level_requirement=weapon.level_requirement,
                evolution_requirement=0,
                memory_requirement=0,
                rarity=weapon.rarity
            )
            weapons.append(content_item)
        
        return weapons
    
    def _generate_jewelry(self, session_id: str, player_level: int, world_seed: int) -> List[ContentItem]:
        """Генерация украшений"""
        import random
        random.seed(world_seed)
        
        jewelry = []
        jewelry_count = random.randint(8, 20)
        
        for i in range(jewelry_count):
            jewelry_item = self._create_jewelry_content(session_id, player_level, world_seed + i)
            content_item = ContentItem(
                id=f"jewelry_{session_id}_{i}",
                session_id=session_id,
                content_type="jewelry",
                name=jewelry_item.name,
                data=asdict(jewelry_item),
                created_at=time.time(),
                level_requirement=jewelry_item.level_requirement,
                evolution_requirement=0,
                memory_requirement=0,
                rarity=jewelry_item.rarity
            )
            jewelry.append(content_item)
        
        return jewelry
    
    def _generate_skills(self, session_id: str, player_level: int, world_seed: int) -> List[ContentItem]:
        """Генерация навыков"""
        import random
        random.seed(world_seed)
        
        skills = []
        skill_count = random.randint(15, 30)
        
        for i in range(skill_count):
            skill = self._create_skill_content(session_id, player_level, world_seed + i)
            content_item = ContentItem(
                id=f"skill_{session_id}_{i}",
                session_id=session_id,
                content_type="skill",
                name=skill.name,
                data=asdict(skill),
                created_at=time.time(),
                level_requirement=skill.level_requirement,
                evolution_requirement=skill.evolution_requirement,
                memory_requirement=skill.memory_requirement,
                rarity="rare" if skill.evolution_requirement > 0 else "common"
            )
            skills.append(content_item)
        
        return skills
    
    def _create_boss_content(self, session_id: str, player_level: int, seed: int) -> BossContent:
        """Создание контента босса"""
        import random
        random.seed(seed)
        
        # Базовые параметры с вариацией
        base_health = player_level * 100
        base_damage = player_level * 20
        variation = 1.0 + random.uniform(-self.content_constants["boss_skills_variation"], 
                                       self.content_constants["boss_skills_variation"])
        
        boss_level = max(1, int(player_level * random.uniform(0.8, 1.5)))
        health = int(base_health * variation)
        damage = int(base_damage * variation)
        
        # Генерация навыков с вариацией
        skill_count = random.randint(3, 6)
        skills = []
        for i in range(skill_count):
            skill_variation = 1.0 + random.uniform(-0.3, 0.3)
            skills.append({
                "name": f"BossSkill_{session_id}_{i}",
                "power": int(50 * skill_variation),
                "cooldown": random.uniform(5.0, 15.0),
                "effects": ["damage", "debuff"],
                "evolution_bonus": random.uniform(0.1, 0.5)
            })
        
        # Фазы босса
        phases = [
            {"name": "normal", "health_threshold": 1.0, "damage_multiplier": 1.0},
            {"name": "enraged", "health_threshold": 0.5, "damage_multiplier": 1.5},
            {"name": "evolved", "health_threshold": 0.2, "damage_multiplier": 2.0}
        ]
        
        evolution_stage = random.randint(1, 5)
        memory_capacity = random.randint(100, 500)
        
        return BossContent(
            name=f"Boss_{session_id}_{random.randint(1000, 9999)}",
            level=boss_level,
            health=health,
            damage=damage,
            skills=skills,
            phases=phases,
            evolution_stage=evolution_stage,
            memory_capacity=memory_capacity,
            rewards={
                "experience": boss_level * 100,
                "evolution_points": evolution_stage * 10,
                "memory_points": memory_capacity // 2,
                "items": []
            },
            behavior={
                "aggression": random.uniform(0.3, 0.8),
                "intelligence": random.uniform(0.4, 0.9),
                "adaptability": random.uniform(0.2, 0.7)
            }
        )
    
    def _create_weapon_content(self, session_id: str, player_level: int, seed: int) -> WeaponContent:
        """Создание контента оружия"""
        import random
        random.seed(seed)
        
        weapon_types = ["sword", "axe", "bow", "staff", "dagger", "hammer", "spear"]
        weapon_type = random.choice(weapon_types)
        
        # Базовые статы с вариацией
        base_damage = player_level * 15
        variation = 1.0 + random.uniform(-self.content_constants["weapon_stats_variation"], 
                                       self.content_constants["weapon_stats_variation"])
        damage = int(base_damage * variation)
        
        # Случайные статы
        stats = {}
        stat_types = ["strength", "dexterity", "intelligence", "constitution"]
        for stat in random.sample(stat_types, random.randint(1, 3)):
            stats[stat] = random.randint(1, 10)
        
        # Навыки оружия
        skill_count = random.randint(0, 2)
        skills = []
        for i in range(skill_count):
            skills.append({
                "name": f"WeaponSkill_{session_id}_{i}",
                "effect": "damage_boost",
                "value": random.randint(10, 30),
                "trigger": "on_hit"
            })
        
        level_requirement = max(1, int(player_level * random.uniform(0.5, 1.2)))
        rarity = random.choice(["common", "uncommon", "rare", "epic"])
        
        return WeaponContent(
            name=f"{weapon_type.capitalize()}_{session_id}_{random.randint(100, 999)}",
            weapon_type=weapon_type,
            damage=damage,
            damage_type=random.choice(["physical", "fire", "cold", "lightning"]),
            stats=stats,
            skills=skills,
            level_requirement=level_requirement,
            rarity=rarity,
            evolution_bonus=random.uniform(0.0, 0.3),
            memory_bonus=random.uniform(0.0, 0.2)
        )
    
    def _create_jewelry_content(self, session_id: str, player_level: int, seed: int) -> JewelryContent:
        """Создание контента украшений"""
        import random
        random.seed(seed)
        
        jewelry_types = ["ring", "necklace", "belt", "cloak"]
        jewelry_type = random.choice(jewelry_types)
        
        # Случайные статы
        stats = {}
        stat_types = ["strength", "dexterity", "intelligence", "constitution", "wisdom", "charisma"]
        for stat in random.sample(stat_types, random.randint(1, 3)):
            stats[stat] = random.randint(1, 8)
        
        # Эффекты
        effect_count = random.randint(0, 2)
        effects = []
        for i in range(effect_count):
            effects.append({
                "name": f"JewelryEffect_{session_id}_{i}",
                "type": random.choice(["buff", "passive"]),
                "value": random.randint(5, 20),
                "duration": random.uniform(10.0, 60.0)
            })
        
        # Навыки
        skill_count = random.randint(0, 1)
        skills = []
        for i in range(skill_count):
            skills.append({
                "name": f"JewelrySkill_{session_id}_{i}",
                "effect": "utility",
                "value": random.randint(10, 25),
                "cooldown": random.uniform(30.0, 120.0)
            })
        
        level_requirement = max(1, int(player_level * random.uniform(0.3, 1.0)))
        rarity = random.choice(["common", "uncommon", "rare"])
        
        return JewelryContent(
            name=f"{jewelry_type.capitalize()}_{session_id}_{random.randint(100, 999)}",
            jewelry_type=jewelry_type,
            stats=stats,
            effects=effects,
            skills=skills,
            level_requirement=level_requirement,
            rarity=rarity,
            evolution_bonus=random.uniform(0.0, 0.2),
            memory_bonus=random.uniform(0.0, 0.3)
        )
    
    def _create_skill_content(self, session_id: str, player_level: int, seed: int) -> SkillContent:
        """Создание контента навыка"""
        import random
        random.seed(seed)
        
        skill_types = ["combat", "survival", "social", "crafting", "evolution", "memory"]
        skill_type = random.choice(skill_types)
        
        # Базовые параметры с вариацией
        base_power = player_level * 25
        variation = 1.0 + random.uniform(-self.content_constants["skill_stats_variation"], 
                                       self.content_constants["skill_stats_variation"])
        power = int(base_power * variation)
        
        # Масштабирование
        scaling = {}
        scaling_stats = ["strength", "intelligence", "evolution", "memory"]
        for stat in random.sample(scaling_stats, random.randint(1, 2)):
            scaling[stat] = random.uniform(0.5, 2.0)
        
        # Эффекты
        effect_count = random.randint(1, 3)
        effects = []
        for i in range(effect_count):
            effects.append({
                "name": f"SkillEffect_{session_id}_{i}",
                "type": random.choice(["damage", "heal", "buff", "debuff"]),
                "value": random.randint(20, 100),
                "duration": random.uniform(5.0, 30.0)
            })
        
        cooldown = random.uniform(5.0, 45.0)
        mana_cost = random.randint(10, 50)
        level_requirement = max(1, int(player_level * random.uniform(0.4, 1.1)))
        evolution_requirement = random.randint(0, 3)
        memory_requirement = random.randint(0, 100)
        
        return SkillContent(
            name=f"Skill_{session_id}_{random.randint(1000, 9999)}",
            skill_type=skill_type,
            description=f"A unique {skill_type} skill for session {session_id}",
            base_power=power,
            scaling=scaling,
            effects=effects,
            cooldown=cooldown,
            mana_cost=mana_cost,
            level_requirement=level_requirement,
            evolution_requirement=evolution_requirement,
            memory_requirement=memory_requirement
        )

class ContentSystem(BaseComponent):
    """Система контента"""
    
    def __init__(self):
        super().__init__(
            component_id="content_system",
            component_type=ComponentType.SYSTEM,
            priority=Priority.MEDIUM
        )
        self.database = ContentDatabase()
        self.generator = ContentGenerator()
        self.current_session_id: Optional[str] = None
        self.session_cache: Dict[str, SessionData] = {}
        
        logger.info("Система контента инициализирована")
    
    def initialize(self):
        """Инициализация системы"""
        try:
            # Загрузка существующих сессий в кэш
            sessions = self.database.get_all_sessions()
            for session in sessions:
                self.session_cache[session.session_id] = session
            
            logger.info(f"Загружено {len(sessions)} сессий")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы контента: {e}")
            return False
    
    def create_session(self, name: str, player_level: int = 1) -> Optional[str]:
        """Создание новой сессии"""
        try:
            session_id = str(uuid.uuid4())
            world_seed = int(time.time()) % 1000000
            
            # Генерация контента для сессии
            content_types = ["bosses", "weapons", "jewelry", "skills"]
            content_items = self.generator.generate_session_content(
                session_id, player_level, world_seed, content_types
            )
            
            # Сохранение контента
            for item in content_items:
                self.database.save_content(item)
            
            # Создание сессии
            session = SessionData(
                session_id=session_id,
                name=name,
                created_at=time.time(),
                last_accessed=time.time(),
                player_level=player_level,
                world_seed=world_seed,
                content_hash=str(hash(tuple(item.id for item in content_items))),
                is_active=True,
                metadata={
                    "content_count": len(content_items),
                    "content_types": content_types
                }
            )
            
            self.database.save_session(session)
            self.session_cache[session_id] = session
            
            logger.info(f"Создана сессия {session_id} с {len(content_items)} элементами контента")
            return session_id
            
        except Exception as e:
            logger.error(f"Ошибка создания сессии: {e}")
            return None
    
    def load_session(self, session_id: str) -> bool:
        """Загрузка сессии"""
        try:
            session = self.database.load_session(session_id)
            if session:
                session.last_accessed = time.time()
                self.database.save_session(session)
                self.current_session_id = session_id
                self.session_cache[session_id] = session
                
                logger.info(f"Загружена сессия {session_id}")
                return True
            else:
                logger.warning(f"Сессия {session_id} не найдена")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка загрузки сессии: {e}")
            return False
    
    def get_session_content(self, content_type: Optional[str] = None) -> List[ContentItem]:
        """Получение контента текущей сессии"""
        if not self.current_session_id:
            logger.warning("Нет активной сессии")
            return []
        
        try:
            return self.database.load_session_content(self.current_session_id, content_type)
        except Exception as e:
            logger.error(f"Ошибка получения контента сессии: {e}")
            return []
    
    def generate_level_content(self, level: int) -> List[ContentItem]:
        """Генерация дополнительного контента для уровня"""
        if not self.current_session_id:
            logger.warning("Нет активной сессии")
            return []
        
        try:
            session = self.session_cache.get(self.current_session_id)
            if not session:
                return []
            
            # Генерация дополнительного контента
            content_types = ["weapons", "jewelry", "skills"]
            new_content = self.generator.generate_session_content(
                self.current_session_id, level, session.world_seed + level, content_types
            )
            
            # Сохранение нового контента
            for item in new_content:
                self.database.save_content(item)
            
            # Обновление сессии
            session.player_level = level
            session.last_accessed = time.time()
            session.metadata["content_count"] = session.metadata.get("content_count", 0) + len(new_content)
            self.database.save_session(session)
            
            logger.info(f"Сгенерировано {len(new_content)} элементов контента для уровня {level}")
            return new_content
            
        except Exception as e:
            logger.error(f"Ошибка генерации контента уровня: {e}")
            return []
    
    def save_session_data(self, session_data: Dict[str, Any]) -> bool:
        """Сохранение данных сессии"""
        if not self.current_session_id:
            logger.warning("Нет активной сессии")
            return False
        
        try:
            session = self.session_cache.get(self.current_session_id)
            if session:
                session.metadata.update(session_data)
                session.last_accessed = time.time()
                self.database.save_session(session)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка сохранения данных сессии: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Удаление сессии"""
        try:
            success = self.database.delete_session(session_id)
            if success:
                self.session_cache.pop(session_id, None)
                if self.current_session_id == session_id:
                    self.current_session_id = None
                logger.info(f"Сессия {session_id} удалена")
            return success
            
        except Exception as e:
            logger.error(f"Ошибка удаления сессии: {e}")
            return False
    
    def get_all_sessions(self) -> List[SessionData]:
        """Получение всех сессий"""
        return list(self.session_cache.values())
    
    def cleanup_old_sessions(self) -> int:
        """Очистка старых сессий"""
        try:
            current_time = time.time()
            max_age = self.session_constants["max_session_age"]
            deleted_count = 0
            
            sessions_to_delete = []
            for session in self.session_cache.values():
                if current_time - session.last_accessed > max_age:
                    sessions_to_delete.append(session.session_id)
            
            for session_id in sessions_to_delete:
                if self.delete_session(session_id):
                    deleted_count += 1
            
            logger.info(f"Удалено {deleted_count} старых сессий")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Ошибка очистки сессий: {e}")
            return 0
    
    def update(self, delta_time: float):
        """Обновление системы"""
        try:
            # Периодическая очистка старых сессий
            if hasattr(self, '_last_cleanup'):
                if time.time() - self._last_cleanup > self.session_constants["session_cleanup_interval"]:
                    self.cleanup_old_sessions()
                    self._last_cleanup = time.time()
            else:
                self._last_cleanup = time.time()
                
        except Exception as e:
            logger.error(f"Ошибка обновления системы контента: {e}")

logger.info("Система контента загружена")
