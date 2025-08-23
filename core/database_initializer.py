#!/usr/bin/env python3
"""
Система автоматической инициализации базы данных.
Объединяет создание и заполнение базы данных в единый процесс.
"""

import sqlite3
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Система инициализации базы данных"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = self.data_dir / "game_data.db"
        self.secure_db_path = self.data_dir / "secure_game_data.db"
        
        # Версия схемы базы данных
        self.schema_version = "1.0.0"
        
        # Статус инициализации
        self._initialized = False
        self._connection = None
    
    def initialize_database(self, force_recreate: bool = False) -> bool:
        """
        Инициализация базы данных
        
        Args:
            force_recreate: Принудительно пересоздать базу данных
            
        Returns:
            True если инициализация прошла успешно
        """
        try:
            logger.info("Начинаем инициализацию базы данных...")
            
            # Проверяем существование базы данных
            if self.db_path.exists() and not force_recreate:
                if self._check_database_integrity():
                    logger.info("База данных уже существует и корректна")
                    self._initialized = True
                    return True
                else:
                    logger.warning("База данных повреждена, пересоздаем...")
            
            # Создаем новую базу данных
            if self._create_database_schema():
                if self._populate_initial_data():
                    if self._create_secure_database():
                        self._initialized = True
                        logger.info("База данных успешно инициализирована")
                        return True
            
            logger.error("Ошибка инициализации базы данных")
            return False
            
        except Exception as e:
            logger.error(f"Критическая ошибка инициализации базы данных: {e}")
            return False
    
    def _create_database_schema(self) -> bool:
        """Создание схемы базы данных"""
        try:
            # Удаляем существующую базу данных
            if self.db_path.exists():
                try:
                    os.remove(self.db_path)
                    logger.info(f"Удалена существующая база данных: {self.db_path}")
                except PermissionError:
                    logger.warning(f"Не удалось удалить базу данных {self.db_path}, возможно она используется другим процессом")
                    # Пробуем создать новую базу данных с другим именем
                    import tempfile
                    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
                    temp_db.close()
                    self.db_path = Path(temp_db.name)
                    logger.info(f"Создана временная база данных: {self.db_path}")
            
            # Создаем новую базу данных
            self._connection = sqlite3.connect(self.db_path)
            cursor = self._connection.cursor()
            
            # Создаем таблицы
            self._create_save_slots_table(cursor)
            self._create_session_data_table(cursor)
            self._create_session_items_table(cursor)
            self._create_session_enemies_table(cursor)
            self._create_effects_table(cursor)
            self._create_skill_effects_table(cursor)
            self._create_enemy_types_table(cursor)
            self._create_weapons_table(cursor)
            self._create_items_table(cursor)
            self._create_skills_table(cursor)
            self._create_biomes_table(cursor)
            self._create_quests_table(cursor)
            self._create_achievements_table(cursor)
            self._create_schema_version_table(cursor)
            
            # Применяем изменения
            self._connection.commit()
            logger.info("Схема базы данных создана успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания схемы базы данных: {e}")
            if self._connection:
                self._connection.rollback()
            return False
    
    def _create_save_slots_table(self, cursor):
        """Создание таблицы слотов сохранения"""
        cursor.execute("""
            CREATE TABLE save_slots (
                slot_id INTEGER PRIMARY KEY,
                session_uuid TEXT UNIQUE NOT NULL,
                save_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_played TEXT NOT NULL,
                player_level INTEGER DEFAULT 1,
                world_seed INTEGER DEFAULT 0,
                play_time REAL DEFAULT 0.0,
                is_active INTEGER DEFAULT 1
            )
        """)
    
    def _create_session_data_table(self, cursor):
        """Создание таблицы данных сессий"""
        cursor.execute("""
            CREATE TABLE session_data (
                session_uuid TEXT PRIMARY KEY,
                slot_id INTEGER NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_saved TEXT NOT NULL,
                player_data TEXT,
                world_data TEXT,
                inventory_data TEXT,
                progress_data TEXT,
                generation_seed INTEGER DEFAULT 0,
                current_level INTEGER DEFAULT 1,
                FOREIGN KEY(slot_id) REFERENCES save_slots(slot_id)
            )
        """)
    
    def _create_session_items_table(self, cursor):
        """Создание таблицы предметов сессий"""
        cursor.execute("""
            CREATE TABLE session_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_uuid TEXT NOT NULL,
                item_id TEXT NOT NULL,
                name TEXT NOT NULL,
                item_type TEXT NOT NULL,
                rarity TEXT NOT NULL,
                effects TEXT,
                value INTEGER DEFAULT 0,
                weight REAL DEFAULT 0.0,
                icon TEXT DEFAULT '',
                is_obtained INTEGER DEFAULT 0,
                obtained_at TEXT,
                FOREIGN KEY(session_uuid) REFERENCES session_data(session_uuid)
            )
        """)
    
    def _create_session_enemies_table(self, cursor):
        """Создание таблицы врагов сессий"""
        cursor.execute("""
            CREATE TABLE session_enemies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_uuid TEXT NOT NULL,
                enemy_id TEXT NOT NULL,
                name TEXT NOT NULL,
                enemy_type TEXT NOT NULL,
                biome TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                stats TEXT NOT NULL,
                resistances TEXT,
                weaknesses TEXT,
                abilities TEXT,
                appearance TEXT,
                behavior_pattern TEXT,
                is_defeated INTEGER DEFAULT 0,
                defeated_at TEXT,
                FOREIGN KEY(session_uuid) REFERENCES session_data(session_uuid)
            )
        """)
    
    def _create_effects_table(self, cursor):
        """Создание таблицы эффектов"""
        cursor.execute("""
            CREATE TABLE effects (
                guid TEXT PRIMARY KEY,
                code TEXT NOT NULL,
                name TEXT NOT NULL,
                effect_type TEXT NOT NULL,
                attribute TEXT NOT NULL,
                value REAL NOT NULL,
                is_percent INTEGER DEFAULT 0,
                duration REAL DEFAULT 0.0,
                tick_interval REAL DEFAULT 0.0,
                max_stacks INTEGER DEFAULT 1,
                description TEXT,
                icon TEXT
            )
        """)
    
    def _create_skill_effects_table(self, cursor):
        """Создание таблицы эффектов навыков"""
        cursor.execute("""
            CREATE TABLE skill_effects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id TEXT NOT NULL,
                effect_type TEXT NOT NULL,
                value REAL NOT NULL,
                duration REAL DEFAULT 0.0,
                chance REAL DEFAULT 1.0,
                scaling TEXT DEFAULT 'linear',
                element TEXT DEFAULT 'physical'
            )
        """)
    
    def _create_enemy_types_table(self, cursor):
        """Создание таблицы типов врагов"""
        cursor.execute("""
            CREATE TABLE enemy_types (
                type_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                base_health REAL NOT NULL,
                base_damage REAL NOT NULL,
                speed REAL NOT NULL,
                defense REAL NOT NULL,
                behavior TEXT NOT NULL
            )
        """)
    
    def _create_weapons_table(self, cursor):
        """Создание таблицы оружия"""
        cursor.execute("""
            CREATE TABLE weapons (
                weapon_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                weapon_type TEXT NOT NULL,
                damage_type TEXT NOT NULL,
                rarity TEXT NOT NULL,
                base_damage REAL NOT NULL,
                attack_speed REAL NOT NULL,
                durability INTEGER DEFAULT 100,
                effects TEXT,
                icon TEXT
            )
        """)
    
    def _create_items_table(self, cursor):
        """Создание таблицы предметов"""
        cursor.execute("""
            CREATE TABLE items (
                item_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                item_type TEXT NOT NULL,
                rarity TEXT NOT NULL,
                effects TEXT,
                value INTEGER DEFAULT 0,
                weight REAL DEFAULT 0.0,
                icon TEXT,
                description TEXT
            )
        """)
    
    def _create_skills_table(self, cursor):
        """Создание таблицы навыков"""
        cursor.execute("""
            CREATE TABLE skills (
                skill_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                skill_type TEXT NOT NULL,
                mana_cost INTEGER DEFAULT 0,
                cooldown REAL DEFAULT 0.0,
                range REAL DEFAULT 1.0,
                description TEXT,
                icon TEXT
            )
        """)
    
    def _create_biomes_table(self, cursor):
        """Создание таблицы биомов"""
        cursor.execute("""
            CREATE TABLE biomes (
                biome_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                weather_patterns TEXT,
                enemy_spawn_rates TEXT,
                resource_spawn_rates TEXT,
                background_image TEXT
            )
        """)
    
    def _create_quests_table(self, cursor):
        """Создание таблицы квестов"""
        cursor.execute("""
            CREATE TABLE quests (
                quest_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                quest_type TEXT NOT NULL,
                requirements TEXT,
                rewards TEXT,
                is_repeatable INTEGER DEFAULT 0,
                icon TEXT
            )
        """)
    
    def _create_achievements_table(self, cursor):
        """Создание таблицы достижений"""
        cursor.execute("""
            CREATE TABLE achievements (
                achievement_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                requirements TEXT,
                rewards TEXT,
                icon TEXT
            )
        """)
    
    def _create_schema_version_table(self, cursor):
        """Создание таблицы версий схемы"""
        cursor.execute("""
            CREATE TABLE schema_version (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL,
                description TEXT
            )
        """)
        
        # Записываем текущую версию
        cursor.execute("""
            INSERT INTO schema_version (version, applied_at, description)
            VALUES (?, ?, ?)
        """, (self.schema_version, datetime.now().isoformat(), "Initial schema creation"))
    
    def _populate_initial_data(self) -> bool:
        """Заполнение начальными данными"""
        try:
            cursor = self._connection.cursor()
            
            # Заполняем таблицы данными
            self._populate_effects(cursor)
            self._populate_skill_effects(cursor)
            self._populate_enemy_types(cursor)
            self._populate_weapons(cursor)
            self._populate_items(cursor)
            self._populate_skills(cursor)
            self._populate_biomes(cursor)
            self._populate_quests(cursor)
            self._populate_achievements(cursor)
            
            # Применяем изменения
            self._connection.commit()
            logger.info("Начальные данные заполнены успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка заполнения начальных данных: {e}")
            if self._connection:
                self._connection.rollback()
            return False
    
    def _populate_effects(self, cursor):
        """Заполнение таблицы эффектов"""
        effects_data = [
            ("EFFECT_001", "STRENGTH_BOOST", "Увеличение силы", "buff", "strength", 10.0, 0, 30.0, 1.0, 1, "Временно увеличивает силу", ""),
            ("EFFECT_002", "WEAKNESS", "Слабость", "debuff", "strength", -5.0, 0, 20.0, 1.0, 1, "Временно уменьшает силу", ""),
            ("EFFECT_003", "HEALING", "Исцеление", "heal", "health", 25.0, 0, 0.0, 0.0, 1, "Восстанавливает здоровье", ""),
            ("EFFECT_004", "POISON", "Отравление", "dot", "health", -3.0, 0, 10.0, 2.0, 5, "Наносит урон от яда", ""),
            ("EFFECT_005", "BURN", "Горение", "dot", "health", -4.0, 0, 8.0, 1.5, 3, "Наносит урон от огня", ""),
            ("EFFECT_006", "FREEZE", "Заморозка", "debuff", "speed", -0.5, 0, 5.0, 1.0, 1, "Замедляет движение", ""),
            ("EFFECT_007", "STUN", "Оглушение", "debuff", "speed", -1.0, 0, 3.0, 0.0, 1, "Полностью останавливает", ""),
            ("EFFECT_008", "INVISIBILITY", "Невидимость", "buff", "stealth", 1.0, 0, 15.0, 1.0, 1, "Делает невидимым", ""),
            ("EFFECT_009", "REGENERATION", "Регенерация", "hot", "health", 2.0, 0, 20.0, 2.0, 1, "Постепенно восстанавливает здоровье", ""),
            ("EFFECT_010", "MANA_BOOST", "Увеличение маны", "buff", "mana", 20.0, 0, 25.0, 1.0, 1, "Временно увеличивает ману", "")
        ]
        
        cursor.executemany("""
            INSERT INTO effects (guid, code, name, effect_type, attribute, value, is_percent, 
                               duration, tick_interval, max_stacks, description, icon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, effects_data)
        
        logger.info(f"Добавлено {len(effects_data)} эффектов")
    
    def _populate_skill_effects(self, cursor):
        """Заполнение таблицы эффектов навыков"""
        effects_data = [
            ("basic_attack", "damage", 10.0, 0.0, 1.0, "linear", "physical"),
            ("fire_ball", "damage", 25.0, 0.0, 1.0, "linear", "fire"),
            ("fire_ball", "burn", 5.0, 3.0, 0.3, "linear", "fire"),
            ("ice_shard", "damage", 20.0, 0.0, 1.0, "linear", "ice"),
            ("ice_shard", "slow", 0.5, 2.0, 0.4, "linear", "ice"),
            ("heal", "healing", 30.0, 0.0, 1.0, "linear", "holy"),
            ("lightning_bolt", "damage", 30.0, 0.0, 1.0, "linear", "lightning"),
            ("lightning_bolt", "stun", 1.0, 1.0, 0.2, "linear", "lightning"),
            ("poison_dart", "damage", 15.0, 0.0, 1.0, "linear", "poison"),
            ("poison_dart", "poison", 8.0, 5.0, 0.6, "linear", "poison"),
            ("shield_bash", "damage", 18.0, 0.0, 1.0, "linear", "physical"),
            ("shield_bash", "stun", 0.5, 1.0, 0.3, "linear", "physical"),
            ("fire_nova", "damage", 35.0, 0.0, 1.0, "linear", "fire"),
            ("fire_nova", "burn", 8.0, 4.0, 0.5, "linear", "fire"),
            ("ice_wall", "defense", 15.0, 8.0, 1.0, "linear", "ice"),
            ("stealth", "stealth", 1.0, 0.0, 1.0, "linear", "none")
        ]
        
        cursor.executemany("""
            INSERT INTO skill_effects (skill_id, effect_type, value, duration, chance, scaling, element)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, effects_data)
        
        logger.info(f"Добавлено {len(effects_data)} эффектов навыков")
    
    def _populate_enemy_types(self, cursor):
        """Заполнение таблицы типов врагов"""
        enemy_types_data = [
            ("goblin", "Гоблин", 50.0, 8.0, 1.2, 3.0, "aggressive"),
            ("orc", "Орк", 120.0, 25.0, 0.8, 8.0, "aggressive"),
            ("troll", "Тролль", 200.0, 35.0, 0.6, 15.0, "aggressive"),
            ("dragon", "Дракон", 500.0, 80.0, 1.5, 25.0, "aggressive"),
            ("undead", "Нежить", 80.0, 15.0, 0.9, 5.0, "aggressive"),
            ("demon", "Демон", 300.0, 45.0, 1.1, 12.0, "aggressive"),
            ("angel", "Ангел", 250.0, 40.0, 1.3, 10.0, "balanced"),
            ("beast", "Зверь", 100.0, 20.0, 1.4, 6.0, "aggressive"),
            ("construct", "Конструкт", 150.0, 30.0, 0.7, 20.0, "defensive"),
            ("elemental", "Элементаль", 180.0, 35.0, 1.0, 8.0, "balanced")
        ]
        
        cursor.executemany("""
            INSERT INTO enemy_types (type_id, name, base_health, base_damage, speed, defense, behavior)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, enemy_types_data)
        
        logger.info(f"Добавлено {len(enemy_types_data)} типов врагов")
    
    def _populate_weapons(self, cursor):
        """Заполнение таблицы оружия"""
        weapons_data = [
            ("sword_common", "Обычный меч", "sword", "physical", "common", 25.0, 1.5),
            ("sword_rare", "Редкий меч", "sword", "physical", "rare", 40.0, 1.8),
            ("axe_common", "Обычный топор", "axe", "physical", "common", 35.0, 1.0),
            ("axe_rare", "Редкий топор", "axe", "physical", "rare", 55.0, 1.2),
            ("spear_common", "Обычное копье", "spear", "physical", "common", 30.0, 1.8),
            ("spear_rare", "Редкое копье", "spear", "physical", "rare", 45.0, 2.0),
            ("bow_common", "Обычный лук", "bow", "physical", "common", 20.0, 2.0),
            ("bow_rare", "Редкий лук", "bow", "physical", "rare", 35.0, 2.5),
            ("staff_common", "Обычный посох", "staff", "magical", "common", 15.0, 1.0),
            ("staff_rare", "Редкий посох", "staff", "magical", "rare", 30.0, 1.2)
        ]
        
        cursor.executemany("""
            INSERT INTO weapons (weapon_id, name, weapon_type, damage_type, rarity, base_damage, attack_speed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, weapons_data)
        
        logger.info(f"Добавлено {len(weapons_data)} видов оружия")
    
    def _populate_items(self, cursor):
        """Заполнение таблицы предметов"""
        items_data = [
            ("health_potion", "Зелье здоровья", "consumable", "common", "", 10, 0.5, "", "Восстанавливает здоровье"),
            ("mana_potion", "Зелье маны", "consumable", "common", "", 15, 0.5, "", "Восстанавливает ману"),
            ("strength_potion", "Зелье силы", "consumable", "rare", "", 25, 0.5, "", "Временно увеличивает силу"),
            ("gold_coin", "Золотая монета", "currency", "common", "", 1, 0.0, "", "Валюта игры"),
            ("gem_red", "Красный камень", "material", "rare", "", 50, 0.1, "", "Драгоценный камень")
        ]
        
        cursor.executemany("""
            INSERT INTO items (item_id, name, item_type, rarity, effects, value, weight, icon, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, items_data)
        
        logger.info(f"Добавлено {len(items_data)} предметов")
    
    def _populate_skills(self, cursor):
        """Заполнение таблицы навыков"""
        skills_data = [
            ("basic_attack", "Базовая атака", "physical", 0, 0.0, 1.0, "Обычная атака", ""),
            ("fire_ball", "Огненный шар", "magical", 15, 3.0, 5.0, "Магическая атака огнем", ""),
            ("ice_shard", "Ледяной осколок", "magical", 10, 2.0, 4.0, "Магическая атака льдом", ""),
            ("heal", "Исцеление", "healing", 20, 5.0, 3.0, "Восстанавливает здоровье", ""),
            ("lightning_bolt", "Молния", "magical", 25, 4.0, 6.0, "Электрическая атака", "")
        ]
        
        cursor.executemany("""
            INSERT INTO skills (skill_id, name, skill_type, mana_cost, cooldown, range, description, icon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, skills_data)
        
        logger.info(f"Добавлено {len(skills_data)} навыков")
    
    def _populate_biomes(self, cursor):
        """Заполнение таблицы биомов"""
        biomes_data = [
            ("forest", "Лес", "Зеленый лес с деревьями", '["clear", "rainy"]', '{"goblin": 0.3, "beast": 0.4}', '{"wood": 0.6, "herbs": 0.4}', "graphics/backgrounds/forest.png"),
            ("desert", "Пустыня", "Жаркая пустыня", '["clear", "stormy"]', '{"orc": 0.4, "construct": 0.2}', '{"sand": 0.8, "cactus": 0.3}', "graphics/backgrounds/sand.png"),
            ("ice", "Ледяные земли", "Холодные льды", '["clear", "foggy"]', '{"troll": 0.3, "elemental": 0.3}', '{"ice": 0.7, "crystal": 0.4}', "graphics/backgrounds/ice.png")
        ]
        
        cursor.executemany("""
            INSERT INTO biomes (biome_id, name, description, weather_patterns, enemy_spawn_rates, resource_spawn_rates, background_image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, biomes_data)
        
        logger.info(f"Добавлено {len(biomes_data)} биомов")
    
    def _populate_quests(self, cursor):
        """Заполнение таблицы квестов"""
        quests_data = [
            ("quest_001", "Первые шаги", "Достигните 5 уровня", "level", '{"level": 5}', '{"exp": 100, "gold": 50}', 0, ""),
            ("quest_002", "Охотник", "Победите 10 врагов", "combat", '{"enemies_defeated": 10}', '{"exp": 200, "item": "sword_common"}', 0, ""),
            ("quest_003", "Исследователь", "Исследуйте 3 биома", "exploration", '{"biomes_explored": 3}', '{"exp": 300, "skill": "heal"}', 0, "")
        ]
        
        cursor.executemany("""
            INSERT INTO quests (quest_id, name, description, quest_type, requirements, rewards, is_repeatable, icon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, quests_data)
        
        logger.info(f"Добавлено {len(quests_data)} квестов")
    
    def _populate_achievements(self, cursor):
        """Заполнение таблицы достижений"""
        achievements_data = [
            ("ach_001", "Новичок", "Достигните 1 уровня", '{"level": 1}', '{"title": "Новичок"}', ""),
            ("ach_002", "Ветеран", "Достигните 10 уровня", '{"level": 10}', '{"title": "Ветеран"}', ""),
            ("ach_003", "Победитель", "Победите 100 врагов", '{"enemies_defeated": 100}', '{"title": "Победитель"}', "")
        ]
        
        cursor.executemany("""
            INSERT INTO achievements (achievement_id, name, description, requirements, rewards, icon)
            VALUES (?, ?, ?, ?, ?, ?)
        """, achievements_data)
        
        logger.info(f"Добавлено {len(achievements_data)} достижений")
    
    def _create_secure_database(self) -> bool:
        """Создание защищенной базы данных для чувствительных данных"""
        try:
            if self.secure_db_path.exists():
                os.remove(self.secure_db_path)
            
            secure_conn = sqlite3.connect(self.secure_db_path)
            cursor = secure_conn.cursor()
            
            # Создаем таблицы для защищенных данных
            cursor.execute("""
                CREATE TABLE player_profiles (
                    profile_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at TEXT NOT NULL,
                    last_login TEXT,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            cursor.execute("""
                CREATE TABLE game_statistics (
                    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    stat_name TEXT NOT NULL,
                    stat_value REAL NOT NULL,
                    recorded_at TEXT NOT NULL,
                    FOREIGN KEY(profile_id) REFERENCES player_profiles(profile_id)
                )
            """)
            
            secure_conn.commit()
            secure_conn.close()
            
            logger.info("Защищенная база данных создана успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания защищенной базы данных: {e}")
            return False
    
    def _check_database_integrity(self) -> bool:
        """Проверка целостности базы данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Проверяем наличие основных таблиц
            required_tables = [
                'save_slots', 'session_data', 'effects', 'enemy_types',
                'weapons', 'items', 'skills', 'biomes', 'quests'
            ]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table in required_tables:
                if table not in existing_tables:
                    logger.warning(f"Отсутствует таблица: {table}")
                    return False
            
            # Проверяем версию схемы
            cursor.execute("SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1")
            result = cursor.fetchone()
            
            if not result:
                logger.warning("Отсутствует информация о версии схемы")
                return False
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки целостности базы данных: {e}")
            return False
    
    def get_connection(self) -> Optional[sqlite3.Connection]:
        """Получить соединение с базой данных"""
        if not self._initialized:
            logger.warning("База данных не инициализирована")
            return None
        
        if not self._connection:
            try:
                self._connection = sqlite3.connect(self.db_path)
            except Exception as e:
                logger.error(f"Ошибка подключения к базе данных: {e}")
                return None
        
        return self._connection
    
    def create_session(self, session_name: str) -> Optional[str]:
        """Создать новую сессию (для совместимости)"""
        try:
            import uuid
            session_uuid = str(uuid.uuid4())
            
            conn = self.get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO session_data (session_uuid, slot_id, state, created_at, last_saved)
                VALUES (?, 1, ?, ?, ?)
            """, (session_uuid, "active", time.time(), time.time()))
            
            conn.commit()
            logger.info(f"Создана сессия: {session_name} ({session_uuid})")
            return session_uuid
            
        except Exception as e:
            logger.error(f"Ошибка создания сессии: {e}")
            return None
    
    def save_session_data(self, session_uuid: str, data: Dict[str, Any]) -> bool:
        """Сохранить данные сессии (для совместимости)"""
        try:
            import json
            
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE session_data 
                SET player_data = ?, last_saved = ?
                WHERE session_uuid = ?
            """, (json.dumps(data), time.time(), session_uuid))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения данных сессии: {e}")
            return False
    
    def load_session_data(self, session_uuid: str) -> Optional[Dict[str, Any]]:
        """Загрузить данные сессии (для совместимости)"""
        try:
            import json
            
            conn = self.get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT player_data FROM session_data 
                WHERE session_uuid = ?
            """, (session_uuid,))
            
            result = cursor.fetchone()
            if result and result[0]:
                return json.loads(result[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка загрузки данных сессии: {e}")
            return None
    
    def close_connection(self):
        """Закрыть соединение с базой данных"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def __del__(self):
        """Деструктор для закрытия соединения"""
        self.close_connection()


# Глобальный экземпляр инициализатора
database_initializer = DatabaseInitializer()
