"""
Менеджер состояния игры.
Управляет сохранением, загрузкой и синхронизацией состояния игры.
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import threading
from datetime import datetime

from config.settings_manager import settings_manager
from core.data_manager import data_manager

logger = logging.getLogger(__name__)


@dataclass
class PlayerState:
    """Состояние игрока"""
    player_id: str
    name: str
    level: int
    experience: int
    experience_to_next: int
    position: Tuple[float, float]
    attributes: Dict[str, float]
    combat_stats: Dict[str, float]
    equipment: Dict[str, str]
    inventory: List[str]
    skills: List[str]
    effects: List[str]
    quests: List[str]
    achievements: List[str]
    playtime: int
    last_save: datetime


@dataclass
class GameState:
    """Состояние игры"""
    game_id: str
    save_name: str
    difficulty: str
    world_seed: int
    current_area: str
    player_state: PlayerState
    world_state: Dict[str, Any]
    game_time: int
    created_at: datetime
    last_modified: datetime


class GameStateManager:
    """Менеджер состояния игры"""
    
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        self._lock = threading.RLock()
        
        # База данных для сохранений
        self.db_path = self.save_dir / "saves.db"
        self._init_database()
        
        # Текущее состояние
        self.current_state: Optional[GameState] = None
        self.auto_save_enabled = True
        self.auto_save_interval = settings_manager.get_setting("auto_save_interval", 300)
        self.last_auto_save = 0
    
    def _init_database(self):
        """Инициализация базы данных сохранений"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица сохранений
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS saves (
                        id TEXT PRIMARY KEY,
                        save_name TEXT NOT NULL,
                        difficulty TEXT DEFAULT 'normal',
                        world_seed INTEGER,
                        current_area TEXT,
                        player_data TEXT,
                        world_state TEXT,
                        game_time INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица статистики
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS save_statistics (
                        save_id TEXT,
                        stat_name TEXT,
                        stat_value REAL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (save_id) REFERENCES saves (id)
                    )
                ''')
                
                conn.commit()
                logger.info("База данных сохранений инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации БД сохранений: {e}")
    
    def create_new_game(self, save_name: str, player_name: str, difficulty: str = "normal") -> str:
        """Создает новую игру"""
        try:
            import random
            
            game_id = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            world_seed = random.randint(1, 999999)
            
            # Создаем начальное состояние игрока
            player_state = PlayerState(
                player_id="player",
                name=player_name,
                level=1,
                experience=0,
                experience_to_next=100,
                position=(0.0, 0.0),
                attributes={
                    "strength": 10,
                    "dexterity": 10,
                    "intelligence": 10,
                    "vitality": 10,
                    "endurance": 10,
                    "faith": 10,
                    "luck": 10
                },
                combat_stats={
                    "health": 100,
                    "max_health": 100,
                    "mana": 50,
                    "max_mana": 50,
                    "stamina": 100,
                    "max_stamina": 100,
                    "damage_output": 10,
                    "defense": 5,
                    "movement_speed": 100.0,
                    "attack_speed": 1.0,
                    "critical_chance": 0.05,
                    "critical_multiplier": 1.5
                },
                equipment={},
                inventory=[],
                skills=[],
                effects=[],
                quests=[],
                achievements=[],
                playtime=0,
                last_save=datetime.now()
            )
            
            # Создаем состояние игры
            game_state = GameState(
                game_id=game_id,
                save_name=save_name,
                difficulty=difficulty,
                world_seed=world_seed,
                current_area="starting_area",
                player_state=player_state,
                world_state={
                    "discovered_areas": ["starting_area"],
                    "completed_quests": [],
                    "killed_enemies": {},
                    "collected_items": {},
                    "world_events": []
                },
                game_time=0,
                created_at=datetime.now(),
                last_modified=datetime.now()
            )
            
            # Сохраняем в БД
            self._save_to_database(game_state)
            
            # Устанавливаем как текущее состояние
            self.current_state = game_state
            
            logger.info(f"Создана новая игра: {save_name}")
            return game_id
            
        except Exception as e:
            logger.error(f"Ошибка создания новой игры: {e}")
            return ""
    
    def load_game(self, game_id: str) -> bool:
        """Загружает игру"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM saves WHERE id = ?', (game_id,))
                row = cursor.fetchone()
                
                if not row:
                    logger.warning(f"Сохранение {game_id} не найдено")
                    return False
                
                # Восстанавливаем состояние игры
                game_state = self._load_from_database_row(row)
                self.current_state = game_state
                
                logger.info(f"Загружена игра: {game_state.save_name}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка загрузки игры: {e}")
            return False
    
    def save_game(self, game_id: str = None) -> bool:
        """Сохраняет игру"""
        try:
            if not self.current_state:
                logger.warning("Нет активного состояния для сохранения")
                return False
            
            if game_id:
                self.current_state.game_id = game_id
            
            # Обновляем время последнего сохранения
            self.current_state.last_modified = datetime.now()
            self.current_state.player_state.last_save = datetime.now()
            
            # Сохраняем в БД
            success = self._save_to_database(self.current_state)
            
            if success:
                logger.info(f"Игра сохранена: {self.current_state.save_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка сохранения игры: {e}")
            return False
    
    def auto_save(self, current_time: int) -> bool:
        """Автосохранение"""
        if not self.auto_save_enabled or not self.current_state:
            return False
        
        if current_time - self.last_auto_save >= self.auto_save_interval:
            self.last_auto_save = current_time
            return self.save_game()
        
        return False
    
    def get_save_list(self) -> List[Dict[str, Any]]:
        """Получает список сохранений"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, save_name, difficulty, current_area, game_time, 
                           created_at, last_modified 
                    FROM saves 
                    ORDER BY last_modified DESC
                ''')
                rows = cursor.fetchall()
                
                saves = []
                for row in rows:
                    saves.append({
                        "game_id": row[0],
                        "save_name": row[1],
                        "difficulty": row[2],
                        "current_area": row[3],
                        "game_time": row[4],
                        "created_at": row[5],
                        "last_modified": row[6]
                    })
                
                return saves
                
        except Exception as e:
            logger.error(f"Ошибка получения списка сохранений: {e}")
            return []
    
    def delete_save(self, game_id: str) -> bool:
        """Удаляет сохранение"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM saves WHERE id = ?', (game_id,))
                cursor.execute('DELETE FROM save_statistics WHERE save_id = ?', (game_id,))
                conn.commit()
                
                logger.info(f"Сохранение удалено: {game_id}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка удаления сохранения: {e}")
            return False
    
    def update_player_state(self, player_data: Dict[str, Any]):
        """Обновляет состояние игрока"""
        if not self.current_state:
            return
        
        try:
            # Обновляем основные характеристики
            if "position" in player_data:
                self.current_state.player_state.position = tuple(player_data["position"])
            
            if "level" in player_data:
                self.current_state.player_state.level = player_data["level"]
            
            if "experience" in player_data:
                self.current_state.player_state.experience = player_data["experience"]
            
            if "attributes" in player_data:
                self.current_state.player_state.attributes.update(player_data["attributes"])
            
            if "combat_stats" in player_data:
                self.current_state.player_state.combat_stats.update(player_data["combat_stats"])
            
            if "equipment" in player_data:
                self.current_state.player_state.equipment.update(player_data["equipment"])
            
            if "inventory" in player_data:
                self.current_state.player_state.inventory = player_data["inventory"]
            
            if "skills" in player_data:
                self.current_state.player_state.skills = player_data["skills"]
            
            if "effects" in player_data:
                self.current_state.player_state.effects = player_data["effects"]
            
            if "quests" in player_data:
                self.current_state.player_state.quests = player_data["quests"]
            
            if "achievements" in player_data:
                self.current_state.player_state.achievements = player_data["achievements"]
            
            if "playtime" in player_data:
                self.current_state.player_state.playtime = player_data["playtime"]
            
            # Обновляем время последнего изменения
            self.current_state.last_modified = datetime.now()
            
        except Exception as e:
            logger.error(f"Ошибка обновления состояния игрока: {e}")
    
    def update_world_state(self, world_data: Dict[str, Any]):
        """Обновляет состояние мира"""
        if not self.current_state:
            return
        
        try:
            self.current_state.world_state.update(world_data)
            self.current_state.last_modified = datetime.now()
            
        except Exception as e:
            logger.error(f"Ошибка обновления состояния мира: {e}")
    
    def get_current_state(self) -> Optional[GameState]:
        """Получает текущее состояние игры"""
        return self.current_state
    
    def export_save(self, game_id: str, export_path: str) -> bool:
        """Экспортирует сохранение в файл"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM saves WHERE id = ?', (game_id,))
                row = cursor.fetchone()
                
                if not row:
                    return False
                
                game_state = self._load_from_database_row(row)
                
                # Сохраняем в JSON файл
                export_data = asdict(game_state)
                export_data["player_state"] = asdict(game_state.player_state)
                
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
                
                logger.info(f"Сохранение экспортировано: {export_path}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка экспорта сохранения: {e}")
            return False
    
    def import_save(self, import_path: str) -> bool:
        """Импортирует сохранение из файла"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Создаем состояние игры из импортированных данных
            player_state = PlayerState(**import_data["player_state"])
            game_state = GameState(
                game_id=import_data["game_id"],
                save_name=import_data["save_name"],
                difficulty=import_data["difficulty"],
                world_seed=import_data["world_seed"],
                current_area=import_data["current_area"],
                player_state=player_state,
                world_state=import_data["world_state"],
                game_time=import_data["game_time"],
                created_at=datetime.fromisoformat(import_data["created_at"]),
                last_modified=datetime.fromisoformat(import_data["last_modified"])
            )
            
            # Сохраняем в БД
            success = self._save_to_database(game_state)
            
            if success:
                logger.info(f"Сохранение импортировано: {import_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка импорта сохранения: {e}")
            return False
    
    def _save_to_database(self, game_state: GameState) -> bool:
        """Сохраняет состояние в базу данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO saves 
                    (id, save_name, difficulty, world_seed, current_area, player_data,
                     world_state, game_time, created_at, last_modified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    game_state.game_id,
                    game_state.save_name,
                    game_state.difficulty,
                    game_state.world_seed,
                    game_state.current_area,
                    json.dumps(asdict(game_state.player_state)),
                    json.dumps(game_state.world_state),
                    game_state.game_time,
                    game_state.created_at.isoformat(),
                    game_state.last_modified.isoformat()
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Ошибка сохранения в БД: {e}")
            return False
    
    def _load_from_database_row(self, row: tuple) -> GameState:
        """Загружает состояние из строки базы данных"""
        player_data = json.loads(row[5])
        world_state = json.loads(row[6])
        
        player_state = PlayerState(**player_data)
        
        return GameState(
            game_id=row[0],
            save_name=row[1],
            difficulty=row[2],
            world_seed=row[3],
            current_area=row[4],
            player_state=player_state,
            world_state=world_state,
            game_time=row[7],
            created_at=datetime.fromisoformat(row[8]),
            last_modified=datetime.fromisoformat(row[9])
        )


# Глобальный экземпляр менеджера состояния игры
game_state_manager = GameStateManager()
