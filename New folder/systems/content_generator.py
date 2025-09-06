#!/usr/bin/env python3
"""Система генерации контента - управление сессиями и процедурная генерация
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
import random
import hashlib

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
class QuestContent:
    """Контент квеста"""
    quest_id: str
    name: str
    description: str
    quest_type: str
    level_requirement: int
    objectives: List[Dict[str, Any]]
    rewards: Dict[str, Any]
    time_limit: float = -1.0
    is_repeatable: bool = False

@dataclass
class WorldContent:
    """Контент мира"""
    world_id: str
    name: str
    biome_type: str
    weather_patterns: List[Dict[str, Any]]
    enemy_spawns: List[Dict[str, Any]]
    resource_nodes: List[Dict[str, Any]]
    landmarks: List[Dict[str, Any]]
    difficulty: float = 1.0

class ContentGenerator:
    """Система генерации контента"""
    
    def __init__(self, database_path: str = "content.db"):
        self.database_path = database_path
        self.sessions: Dict[str, SessionData] = {}
        self.content_cache: Dict[str, Any] = {}
        self.generation_rules: Dict[str, Dict[str, Any]] = {}
        self.content_templates: Dict[str, Dict[str, Any]] = {}
        
        # Настройки генерации
        self.max_cache_size = 1000
        self.generation_threads = 4
        self.cache_ttl = 3600  # секунды
        
        # Инициализация базы данных
        self._init_database()
        
        # Загрузка шаблонов
        self._load_content_templates()
        
        logger.info("ContentGenerator initialized")
    
    def _init_database(self):
        """Инициализация базы данных"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Создаем таблицы
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
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_items (
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
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_templates (
                    template_id TEXT PRIMARY KEY,
                    content_type TEXT NOT NULL,
                    template_data TEXT NOT NULL,
                    rarity_weights TEXT NOT NULL,
                    level_scaling TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    def _load_content_templates(self):
        """Загрузка шаблонов контента"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT template_id, content_type, template_data FROM content_templates")
            templates = cursor.fetchall()
            
            for template_id, content_type, template_data in templates:
                self.content_templates[template_id] = {
                    "content_type": content_type,
                    "template_data": json.loads(template_data)
                }
            
            conn.close()
            
            # Создаем базовые шаблоны если их нет
            if not templates:
                self._create_default_templates()
            
            logger.info(f"Loaded {len(templates)} content templates")
            
        except Exception as e:
            logger.error(f"Failed to load content templates: {e}")
    
    def _create_default_templates(self):
        """Создание базовых шаблонов контента"""
        default_templates = {
            "weapon_sword": {
                "content_type": "weapon",
                "template_data": {
                    "name_patterns": ["{material} Sword", "Blade of {material}", "{adjective} {material} Sword"],
                    "materials": ["Iron", "Steel", "Silver", "Gold", "Mithril", "Adamantium"],
                    "adjectives": ["Sharp", "Mighty", "Ancient", "Legendary", "Cursed", "Blessed"],
                    "base_damage": {"min": 10, "max": 50},
                    "damage_types": ["physical", "magical", "fire", "ice", "lightning"],
                    "rarity_weights": {"common": 0.5, "uncommon": 0.3, "rare": 0.15, "epic": 0.04, "legendary": 0.01}
                }
            },
            "enemy_goblin": {
                "content_type": "enemy",
                "template_data": {
                    "name_patterns": ["{adjective} Goblin", "Goblin {warrior_type}", "{color} Goblin"],
                    "adjectives": ["Angry", "Cunning", "Fierce", "Sneaky", "Brutal"],
                    "warrior_types": ["Warrior", "Archer", "Mage", "Scout", "Berserker"],
                    "colors": ["Green", "Red", "Blue", "Yellow", "Purple"],
                    "base_health": {"min": 20, "max": 100},
                    "base_damage": {"min": 5, "max": 25},
                    "behavior_types": ["aggressive", "defensive", "cowardly", "tactical"]
                }
            },
            "quest_kill": {
                "content_type": "quest",
                "template_data": {
                    "name_patterns": ["Kill {enemy_type}", "Hunt {enemy_type}", "Eliminate {enemy_type}"],
                    "enemy_types": ["Goblins", "Orcs", "Trolls", "Dragons", "Undead"],
                    "objective_types": ["kill_count", "collect_items", "explore_area", "escort_npc"],
                    "reward_types": ["experience", "gold", "items", "reputation"]
                }
            }
        }
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            for template_id, template_data in default_templates.items():
                cursor.execute('''
                    INSERT INTO content_templates 
                    (template_id, content_type, template_data, rarity_weights, level_scaling, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    template_id,
                    template_data["content_type"],
                    json.dumps(template_data["template_data"]),
                    json.dumps(template_data["template_data"].get("rarity_weights", {})),
                    json.dumps({"min_level": 1, "max_level": 100, "scaling_factor": 1.0}),
                    time.time()
                ))
            
            conn.commit()
            conn.close()
            
            logger.info("Created default content templates")
            
        except Exception as e:
            logger.error(f"Failed to create default templates: {e}")
    
    def create_session(self, session_name: str, player_level: int, world_seed: int = None) -> str:
        """Создание новой сессии"""
        session_id = str(uuid.uuid4())
        world_seed = world_seed or random.randint(1, 1000000)
        
        session = SessionData(
            session_id=session_id,
            name=session_name,
            created_at=time.time(),
            last_accessed=time.time(),
            player_level=player_level,
            world_seed=world_seed,
            content_hash=self._generate_content_hash(session_id, world_seed)
        )
        
        self.sessions[session_id] = session
        self._save_session_to_db(session)
        
        logger.info(f"Created session {session_name} with ID {session_id}")
        return session_id
    
    def generate_content(self, session_id: str, content_type: str, level: int = None, 
                        rarity: str = None, count: int = 1) -> List[ContentItem]:
        """Генерация контента для сессии"""
        if session_id not in self.sessions:
            logger.error(f"Session {session_id} not found")
            return []
        
        session = self.sessions[session_id]
        session.last_accessed = time.time()
        
        # Обновляем сессию в базе данных
        self._update_session_in_db(session)
        
        generated_content = []
        
        for i in range(count):
            # Генерируем уникальный контент на основе хеша сессии
            content_seed = hash(f"{session.content_hash}_{content_type}_{i}_{time.time()}")
            random.seed(content_seed)
            
            # Выбираем подходящий шаблон
            template = self._select_template(content_type, level, rarity)
            if not template:
                logger.warning(f"No template found for content type {content_type}")
                continue
            
            # Генерируем контент
            content_data = self._generate_from_template(template, level, rarity, session)
            
            content_item = ContentItem(
                id=f"{content_type}_{session_id}_{i}_{int(time.time() * 1000)}",
                session_id=session_id,
                content_type=content_type,
                name=content_data["name"],
                data=content_data["data"],
                created_at=time.time(),
                level_requirement=content_data.get("level_requirement", 1),
                evolution_requirement=content_data.get("evolution_requirement", 0),
                memory_requirement=content_data.get("memory_requirement", 0),
                rarity=content_data.get("rarity", "common"),
                is_unique=content_data.get("is_unique", True)
            )
            
            generated_content.append(content_item)
            
            # Сохраняем в базу данных
            self._save_content_to_db(content_item)
        
        logger.info(f"Generated {len(generated_content)} {content_type} items for session {session_id}")
        return generated_content
    
    def generate_weapon(self, session_id: str, level: int = None, rarity: str = None) -> WeaponContent:
        """Генерация оружия"""
        content_items = self.generate_content(session_id, "weapon", level, rarity, 1)
        if not content_items:
            return None
        
        content_data = content_items[0].data
        
        weapon = WeaponContent(
            name=content_items[0].name,
            weapon_type=content_data.get("weapon_type", "sword"),
            damage=content_data.get("damage", 10),
            damage_type=content_data.get("damage_type", "physical"),
            stats=content_data.get("stats", {}),
            skills=content_data.get("skills", []),
            level_requirement=content_items[0].level_requirement,
            rarity=content_items[0].rarity,
            evolution_bonus=content_data.get("evolution_bonus", 0.0),
            memory_bonus=content_data.get("memory_bonus", 0.0)
        )
        
        return weapon
    
    def generate_enemy(self, session_id: str, level: int = None, enemy_type: str = None) -> BossContent:
        """Генерация врага"""
        content_items = self.generate_content(session_id, "enemy", level, None, 1)
        if not content_items:
            return None
        
        content_data = content_items[0].data
        
        enemy = BossContent(
            name=content_items[0].name,
            level=content_data.get("level", level or 1),
            health=content_data.get("health", 50),
            damage=content_data.get("damage", 10),
            skills=content_data.get("skills", []),
            phases=content_data.get("phases", []),
            evolution_stage=content_data.get("evolution_stage", 0),
            memory_capacity=content_data.get("memory_capacity", 10),
            rewards=content_data.get("rewards", {}),
            behavior=content_data.get("behavior", {})
        )
        
        return enemy
    
    def generate_quest(self, session_id: str, level: int = None, quest_type: str = None) -> QuestContent:
        """Генерация квеста"""
        content_items = self.generate_content(session_id, "quest", level, None, 1)
        if not content_items:
            return None
        
        content_data = content_items[0].data
        
        quest = QuestContent(
            quest_id=content_items[0].id,
            name=content_items[0].name,
            description=content_data.get("description", ""),
            quest_type=content_data.get("quest_type", "kill"),
            level_requirement=content_items[0].level_requirement,
            objectives=content_data.get("objectives", []),
            rewards=content_data.get("rewards", {}),
            time_limit=content_data.get("time_limit", -1.0),
            is_repeatable=content_data.get("is_repeatable", False)
        )
        
        return quest
    
    def generate_world(self, session_id: str, biome_type: str = None) -> WorldContent:
        """Генерация мира"""
        content_items = self.generate_content(session_id, "world", None, None, 1)
        if not content_items:
            return None
        
        content_data = content_items[0].data
        
        world = WorldContent(
            world_id=content_items[0].id,
            name=content_items[0].name,
            biome_type=content_data.get("biome_type", biome_type or "forest"),
            weather_patterns=content_data.get("weather_patterns", []),
            enemy_spawns=content_data.get("enemy_spawns", []),
            resource_nodes=content_data.get("resource_nodes", []),
            landmarks=content_data.get("landmarks", []),
            difficulty=content_data.get("difficulty", 1.0)
        )
        
        return world
    
    def _generate_content_hash(self, session_id: str, world_seed: int) -> str:
        """Генерация хеша контента для сессии"""
        content_string = f"{session_id}_{world_seed}_{time.time()}"
        return hashlib.md5(content_string.encode()).hexdigest()
    
    def _select_template(self, content_type: str, level: int = None, rarity: str = None) -> Dict[str, Any]:
        """Выбор подходящего шаблона"""
        available_templates = []
        
        for template_id, template in self.content_templates.items():
            if template["content_type"] == content_type:
                available_templates.append((template_id, template))
        
        if not available_templates:
            return None
        
        # Выбираем случайный шаблон
        template_id, template = random.choice(available_templates)
        return template["template_data"]
    
    def _generate_from_template(self, template: Dict[str, Any], level: int = None, 
                               rarity: str = None, session: SessionData = None) -> Dict[str, Any]:
        """Генерация контента из шаблона"""
        generated_data = {}
        
        # Генерируем имя
        if "name_patterns" in template:
            name_pattern = random.choice(template["name_patterns"])
            generated_data["name"] = self._fill_name_pattern(name_pattern, template)
        else:
            generated_data["name"] = f"Generated {template.get('content_type', 'item')}"
        
        # Генерируем характеристики
        if "base_damage" in template:
            damage_range = template["base_damage"]
            base_damage = random.randint(damage_range["min"], damage_range["max"])
            if level:
                base_damage = int(base_damage * (1 + level * 0.1))
            generated_data["damage"] = base_damage
        
        if "base_health" in template:
            health_range = template["base_health"]
            base_health = random.randint(health_range["min"], health_range["max"])
            if level:
                base_health = int(base_health * (1 + level * 0.15))
            generated_data["health"] = base_health
        
        # Генерируем редкость
        if "rarity_weights" in template:
            rarity_weights = template["rarity_weights"]
            if rarity:
                generated_data["rarity"] = rarity
            else:
                generated_data["rarity"] = random.choices(
                    list(rarity_weights.keys()),
                    weights=list(rarity_weights.values())
                )[0]
        
        # Генерируем дополнительные данные
        generated_data["level_requirement"] = level or 1
        generated_data["evolution_requirement"] = random.randint(0, level or 1)
        generated_data["memory_requirement"] = random.randint(0, 10)
        generated_data["is_unique"] = random.random() < 0.1  # 10% уникальных предметов
        
        # Добавляем специфичные данные для разных типов контента
        if template.get("content_type") == "weapon":
            generated_data["weapon_type"] = random.choice(template.get("weapon_types", ["sword"]))
            generated_data["damage_type"] = random.choice(template.get("damage_types", ["physical"]))
            generated_data["evolution_bonus"] = random.uniform(0.0, 0.5)
            generated_data["memory_bonus"] = random.uniform(0.0, 0.3)
        
        elif template.get("content_type") == "enemy":
            generated_data["behavior"] = random.choice(template.get("behavior_types", ["aggressive"]))
            generated_data["evolution_stage"] = random.randint(0, 3)
            generated_data["memory_capacity"] = random.randint(5, 20)
            generated_data["rewards"] = {
                "experience": random.randint(10, 100),
                "gold": random.randint(5, 50),
                "items": []
            }
        
        elif template.get("content_type") == "quest":
            generated_data["quest_type"] = random.choice(template.get("objective_types", ["kill_count"]))
            generated_data["objectives"] = [{"type": "kill", "target": "enemy", "count": random.randint(1, 10)}]
            generated_data["rewards"] = {
                "experience": random.randint(20, 200),
                "gold": random.randint(10, 100)
            }
            generated_data["time_limit"] = random.randint(300, 3600)  # 5-60 минут
        
        return generated_data
    
    def _fill_name_pattern(self, pattern: str, template: Dict[str, Any]) -> str:
        """Заполнение шаблона имени"""
        filled_name = pattern
        
        # Заменяем плейсхолдеры
        if "{material}" in pattern and "materials" in template:
            filled_name = filled_name.replace("{material}", random.choice(template["materials"]))
        
        if "{adjective}" in pattern and "adjectives" in template:
            filled_name = filled_name.replace("{adjective}", random.choice(template["adjectives"]))
        
        if "{enemy_type}" in pattern and "enemy_types" in template:
            filled_name = filled_name.replace("{enemy_type}", random.choice(template["enemy_types"]))
        
        if "{warrior_type}" in pattern and "warrior_types" in template:
            filled_name = filled_name.replace("{warrior_type}", random.choice(template["warrior_types"]))
        
        if "{color}" in pattern and "colors" in template:
            filled_name = filled_name.replace("{color}", random.choice(template["colors"]))
        
        return filled_name
    
    def _save_session_to_db(self, session: SessionData):
        """Сохранение сессии в базу данных"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sessions 
                (session_id, name, created_at, last_accessed, player_level, world_seed, content_hash, is_active, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.session_id,
                session.name,
                session.created_at,
                session.last_accessed,
                session.player_level,
                session.world_seed,
                session.content_hash,
                1 if session.is_active else 0,
                json.dumps(session.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save session to database: {e}")
    
    def _update_session_in_db(self, session: SessionData):
        """Обновление сессии в базе данных"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions 
                SET last_accessed = ?, player_level = ?, metadata = ?
                WHERE session_id = ?
            ''', (
                session.last_accessed,
                session.player_level,
                json.dumps(session.metadata),
                session.session_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update session in database: {e}")
    
    def _save_content_to_db(self, content: ContentItem):
        """Сохранение контента в базу данных"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO content_items 
                (id, session_id, content_type, name, data, created_at, level_requirement, 
                 evolution_requirement, memory_requirement, rarity, is_unique)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                content.id,
                content.session_id,
                content.content_type,
                content.name,
                json.dumps(content.data),
                content.created_at,
                content.level_requirement,
                content.evolution_requirement,
                content.memory_requirement,
                content.rarity,
                1 if content.is_unique else 0
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save content to database: {e}")
    
    def get_session_content(self, session_id: str, content_type: str = None) -> List[ContentItem]:
        """Получение контента сессии"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            if content_type:
                cursor.execute('''
                    SELECT id, session_id, content_type, name, data, created_at, level_requirement,
                           evolution_requirement, memory_requirement, rarity, is_unique
                    FROM content_items 
                    WHERE session_id = ? AND content_type = ?
                    ORDER BY created_at DESC
                ''', (session_id, content_type))
            else:
                cursor.execute('''
                    SELECT id, session_id, content_type, name, data, created_at, level_requirement,
                           evolution_requirement, memory_requirement, rarity, is_unique
                    FROM content_items 
                    WHERE session_id = ?
                    ORDER BY created_at DESC
                ''', (session_id,))
            
            content_items = []
            for row in cursor.fetchall():
                content_item = ContentItem(
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
                )
                content_items.append(content_item)
            
            conn.close()
            return content_items
            
        except Exception as e:
            logger.error(f"Failed to get session content: {e}")
            return []
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Очистка старых сессий"""
        try:
            cutoff_time = time.time() - (max_age_hours * 3600)
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Удаляем старые сессии
            cursor.execute("DELETE FROM sessions WHERE last_accessed < ?", (cutoff_time,))
            deleted_sessions = cursor.rowcount
            
            # Удаляем связанный контент
            cursor.execute("DELETE FROM content_items WHERE session_id NOT IN (SELECT session_id FROM sessions)")
            deleted_content = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_sessions} old sessions and {deleted_content} content items")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Получение статистики генерации"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Статистика сессий
            cursor.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE is_active = 1")
            active_sessions = cursor.fetchone()[0]
            
            # Статистика контента
            cursor.execute("SELECT COUNT(*) FROM content_items")
            total_content = cursor.fetchone()[0]
            
            cursor.execute("SELECT content_type, COUNT(*) FROM content_items GROUP BY content_type")
            content_by_type = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "total_content": total_content,
                "content_by_type": content_by_type,
                "templates_count": len(self.content_templates)
            }
            
        except Exception as e:
            logger.error(f"Failed to get generation stats: {e}")
            return {}
