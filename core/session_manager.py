"""
Система управления игровыми сессиями с поддержкой множественных слотов сохранения.
Обеспечивает изоляцию данных между сессиями и правильную генерацию контента.
"""

import uuid
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Состояния игровой сессии"""
    NEW = "new"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    SAVED = "saved"


@dataclass
class SaveSlot:
    """Слот сохранения"""
    slot_id: int
    session_uuid: str
    save_name: str
    created_at: datetime
    last_played: datetime
    player_level: int
    world_seed: int
    play_time: float
    is_active: bool = True


@dataclass
class SessionData:
    """Данные игровой сессии"""
    session_uuid: str
    slot_id: int
    state: SessionState
    created_at: datetime
    last_saved: datetime
    player_data: Dict[str, Any] = field(default_factory=dict)
    world_data: Dict[str, Any] = field(default_factory=dict)
    inventory_data: Dict[str, Any] = field(default_factory=dict)
    progress_data: Dict[str, Any] = field(default_factory=dict)
    generation_seed: int = 0
    current_level: int = 1


class SessionManager:
    """Менеджер игровых сессий"""
    
    def __init__(self, save_dir: str = "save", max_slots: int = 10):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        self.max_slots = max_slots
        
        # База данных сессий
        self.db_path = Path("data/game_data.db")
        self._init_session_database()
        
        # Активная сессия
        self.active_session: Optional[SessionData] = None
        self.active_slot: Optional[SaveSlot] = None
        
        logger.info(f"Менеджер сессий инициализирован: {self.save_dir}")
    
    def _init_session_database(self):
        """Инициализация базы данных сессий"""
        if not self.db_path.exists():
            logger.error(f"База данных не найдена: {self.db_path}")
            return
        
        logger.info("База данных сессий готова к использованию")
    
    def _is_slot_available(self, slot_id: int) -> bool:
        """Проверка доступности слота"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM save_slots WHERE slot_id = ? AND is_active = 1", (slot_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        return count == 0
    
    def _save_slot_to_db(self, save_slot: SaveSlot):
        """Сохранение слота в БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO save_slots 
            (slot_id, session_uuid, save_name, created_at, last_played, 
             player_level, world_seed, play_time, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            save_slot.slot_id, save_slot.session_uuid, save_slot.save_name,
            save_slot.created_at.isoformat(), save_slot.last_played.isoformat(),
            save_slot.player_level, save_slot.world_seed, save_slot.play_time,
            1 if save_slot.is_active else 0
        ))
        
        conn.commit()
        conn.close()
    
    def _save_session_to_db(self, session_data: SessionData):
        """Сохранение данных сессии в БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO session_data 
            (session_uuid, slot_id, state, created_at, last_saved, player_data, 
             world_data, inventory_data, progress_data, generation_seed, current_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_data.session_uuid, session_data.slot_id, session_data.state.value,
            session_data.created_at.isoformat(), session_data.last_saved.isoformat(),
            json.dumps(session_data.player_data), json.dumps(session_data.world_data),
            json.dumps(session_data.inventory_data), json.dumps(session_data.progress_data),
            session_data.generation_seed, session_data.current_level
        ))
        
        conn.commit()
        conn.close()
    
    def create_new_session(self, slot_id: int, save_name: str, world_seed: int = None) -> SessionData:
        """Создание новой игровой сессии"""
        try:
            # Проверяем доступность слота
            if not self._is_slot_available(slot_id):
                raise ValueError(f"Слот {slot_id} уже занят")
            
            # Генерируем UUID сессии
            session_uuid = str(uuid.uuid4())
            
            # Создаём слот сохранения
            save_slot = SaveSlot(
                slot_id=slot_id,
                session_uuid=session_uuid,
                save_name=save_name,
                created_at=datetime.now(),
                last_played=datetime.now(),
                player_level=1,
                world_seed=world_seed or 0,
                play_time=0.0,
                is_active=True
            )
            
            # Создаём данные сессии
            session_data = SessionData(
                session_uuid=session_uuid,
                slot_id=slot_id,
                state=SessionState.NEW,
                created_at=datetime.now(),
                last_saved=datetime.now(),
                generation_seed=world_seed or 0,
                current_level=1
            )
            
            # Сохраняем в БД
            self._save_slot_to_db(save_slot)
            self._save_session_to_db(session_data)
            
            # Устанавливаем как активную сессию
            self.active_session = session_data
            self.active_slot = save_slot
            
            logger.info(f"Создана новая сессия: {session_uuid} в слоте {slot_id}")
            return session_data
            
        except Exception as e:
            logger.error(f"Ошибка создания сессии: {e}")
            raise
    
    def load_session(self, slot_id: int) -> Optional[SessionData]:
        """Загрузка существующей сессии"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Получаем данные слота
            cursor.execute("""
                SELECT session_uuid, save_name, created_at, last_played, 
                       player_level, world_seed, play_time, is_active
                FROM save_slots WHERE slot_id = ? AND is_active = 1
            """, (slot_id,))
            
            slot_data = cursor.fetchone()
            if not slot_data:
                logger.warning(f"Слот {slot_id} не найден или неактивен")
                return None
            
            session_uuid, save_name, created_at, last_played, player_level, world_seed, play_time, is_active = slot_data
            
            # Получаем данные сессии
            cursor.execute("""
                SELECT state, created_at, last_saved, player_data, world_data, 
                       inventory_data, progress_data, generation_seed, current_level
                FROM session_data WHERE session_uuid = ?
            """, (session_uuid,))
            
            session_row = cursor.fetchone()
            if not session_row:
                logger.error(f"Данные сессии {session_uuid} не найдены")
                return None
            
            state, sess_created_at, last_saved, player_data, world_data, inventory_data, progress_data, generation_seed, current_level = session_row
            
            # Создаём объекты
            save_slot = SaveSlot(
                slot_id=slot_id,
                session_uuid=session_uuid,
                save_name=save_name,
                created_at=datetime.fromisoformat(created_at),
                last_played=datetime.fromisoformat(last_played),
                player_level=player_level,
                world_seed=world_seed,
                play_time=play_time,
                is_active=bool(is_active)
            )
            
            session_data = SessionData(
                session_uuid=session_uuid,
                slot_id=slot_id,
                state=SessionState(state),
                created_at=datetime.fromisoformat(sess_created_at),
                last_saved=datetime.fromisoformat(last_saved),
                player_data=json.loads(player_data) if player_data else {},
                world_data=json.loads(world_data) if world_data else {},
                inventory_data=json.loads(inventory_data) if inventory_data else {},
                progress_data=json.loads(progress_data) if progress_data else {},
                generation_seed=generation_seed,
                current_level=current_level
            )
            
            # Обновляем время последней игры
            save_slot.last_played = datetime.now()
            self._save_slot_to_db(save_slot)
            
            # Устанавливаем как активную сессию
            self.active_session = session_data
            self.active_slot = save_slot
            
            logger.info(f"Загружена сессия: {session_uuid} из слота {slot_id}")
            return session_data
            
        except Exception as e:
            logger.error(f"Ошибка загрузки сессии: {e}")
            return None
        finally:
            conn.close()
    
    def save_session(self, session_data: SessionData = None):
        """Сохранение текущей сессии"""
        if session_data is None:
            session_data = self.active_session
        
        if not session_data:
            logger.error("Нет активной сессии для сохранения")
            return False
        
        try:
            # Обновляем время сохранения
            session_data.last_saved = datetime.now()
            session_data.state = SessionState.SAVED
            
            # Сохраняем в БД
            self._save_session_to_db(session_data)
            
            # Обновляем слот
            if self.active_slot:
                self.active_slot.last_played = datetime.now()
                self._save_slot_to_db(self.active_slot)
            
            logger.info(f"Сессия {session_data.session_uuid} сохранена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения сессии: {e}")
            return False
    
    def add_session_content(self, content_type: str, content_data: Dict[str, Any]):
        """Добавление сгенерированного контента в сессию"""
        if not self.active_session:
            logger.error("Нет активной сессии для добавления контента")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            session_uuid = self.active_session.session_uuid
            
            if content_type == "items":
                cursor.execute("""
                    INSERT INTO session_items 
                    (session_uuid, item_id, name, item_type, rarity, effects, value, weight, icon, is_obtained, obtained_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_uuid, content_data.get("id"), content_data.get("name"),
                    content_data.get("item_type"), content_data.get("rarity"),
                    json.dumps(content_data.get("effects", [])), content_data.get("value", 0),
                    content_data.get("weight", 0.0), content_data.get("icon", ""),
                    0, None
                ))
            
            elif content_type == "enemies":
                cursor.execute("""
                    INSERT INTO session_enemies 
                    (session_uuid, enemy_id, name, enemy_type, biome, level, stats, 
                     resistances, weaknesses, abilities, appearance, behavior_pattern, is_defeated, defeated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_uuid, content_data.get("id"), content_data.get("name"),
                    content_data.get("enemy_type"), content_data.get("biome"),
                    content_data.get("level", 1), json.dumps(content_data.get("stats", {})),
                    json.dumps(content_data.get("resistances", {})), json.dumps(content_data.get("weaknesses", {})),
                    json.dumps(content_data.get("abilities", [])), json.dumps(content_data.get("appearance", {})),
                    content_data.get("behavior_pattern", ""), 0, None
                ))
            
            elif content_type == "weapons":
                cursor.execute("""
                    INSERT INTO session_weapons 
                    (session_uuid, weapon_id, name, weapon_type, tier, damage, effects, 
                     requirements, appearance, durability, is_obtained, obtained_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_uuid, content_data.get("id"), content_data.get("name"),
                    content_data.get("weapon_type"), content_data.get("tier", 1),
                    content_data.get("damage", 0.0), json.dumps(content_data.get("effects", [])),
                    json.dumps(content_data.get("requirements", {})), json.dumps(content_data.get("appearance", {})),
                    content_data.get("durability", 100), 0, None
                ))
            
            elif content_type == "skills":
                cursor.execute("""
                    INSERT INTO session_skills 
                    (session_uuid, skill_id, name, skill_type, element, target, base_damage, 
                     base_healing, mana_cost, cooldown, range, accuracy, critical_chance, 
                     critical_multiplier, is_learned, learned_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_uuid, content_data.get("id"), content_data.get("name"),
                    content_data.get("type"), content_data.get("element", "physical"),
                    content_data.get("target", "single_enemy"), content_data.get("base_damage", 0.0),
                    content_data.get("base_healing", 0.0), content_data.get("mana_cost", 0.0),
                    content_data.get("cooldown", 0.0), content_data.get("range", 1.0),
                    content_data.get("accuracy", 1.0), content_data.get("critical_chance", 0.05),
                    content_data.get("critical_multiplier", 1.5), 0, None
                ))
            
            elif content_type == "genes":
                cursor.execute("""
                    INSERT INTO session_genes 
                    (session_uuid, gene_id, name, gene_type, effect_type, value, rarity, 
                     description, is_obtained, obtained_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_uuid, content_data.get("id"), content_data.get("name"),
                    content_data.get("gene_type"), content_data.get("effect_type"),
                    content_data.get("value", 0.0), content_data.get("rarity", "common"),
                    content_data.get("description", ""), 0, None
                ))
            
            conn.commit()
            logger.debug(f"Добавлен {content_type}: {content_data.get('name', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления контента {content_type}: {e}")
            return False
        finally:
            conn.close()
    
    def get_session_content(self, content_type: str) -> List[Dict[str, Any]]:
        """Получение сгенерированного контента сессии"""
        if not self.active_session:
            logger.error("Нет активной сессии для получения контента")
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            session_uuid = self.active_session.session_uuid
            content = []
            
            if content_type == "items":
                cursor.execute("""
                    SELECT item_id, name, item_type, rarity, effects, value, weight, icon, is_obtained, obtained_at
                    FROM session_items WHERE session_uuid = ?
                """, (session_uuid,))
                
                for row in cursor.fetchall():
                    content.append({
                        "id": row[0], "name": row[1], "item_type": row[2], "rarity": row[3],
                        "effects": json.loads(row[4]) if row[4] else [], "value": row[5],
                        "weight": row[6], "icon": row[7], "is_obtained": bool(row[8]),
                        "obtained_at": row[9]
                    })
            
            elif content_type == "enemies":
                cursor.execute("""
                    SELECT enemy_id, name, enemy_type, biome, level, stats, resistances, 
                           weaknesses, abilities, appearance, behavior_pattern, is_defeated, defeated_at
                    FROM session_enemies WHERE session_uuid = ?
                """, (session_uuid,))
                
                for row in cursor.fetchall():
                    content.append({
                        "id": row[0], "name": row[1], "enemy_type": row[2], "biome": row[3],
                        "level": row[4], "stats": json.loads(row[5]) if row[5] else {},
                        "resistances": json.loads(row[6]) if row[6] else {},
                        "weaknesses": json.loads(row[7]) if row[7] else {},
                        "abilities": json.loads(row[8]) if row[8] else [],
                        "appearance": json.loads(row[9]) if row[9] else {},
                        "behavior_pattern": row[10], "is_defeated": bool(row[11]),
                        "defeated_at": row[12]
                    })
            
            elif content_type == "weapons":
                cursor.execute("""
                    SELECT weapon_id, name, weapon_type, tier, damage, effects, requirements, 
                           appearance, durability, is_obtained, obtained_at
                    FROM session_weapons WHERE session_uuid = ?
                """, (session_uuid,))
                
                for row in cursor.fetchall():
                    content.append({
                        "id": row[0], "name": row[1], "weapon_type": row[2], "tier": row[3],
                        "damage": row[4], "effects": json.loads(row[5]) if row[5] else [],
                        "requirements": json.loads(row[6]) if row[6] else {},
                        "appearance": json.loads(row[7]) if row[7] else {},
                        "durability": row[8], "is_obtained": bool(row[9]), "obtained_at": row[10]
                    })
            
            elif content_type == "skills":
                cursor.execute("""
                    SELECT skill_id, name, skill_type, element, target, base_damage, base_healing,
                           mana_cost, cooldown, range, accuracy, critical_chance, critical_multiplier,
                           is_learned, learned_at
                    FROM session_skills WHERE session_uuid = ?
                """, (session_uuid,))
                
                for row in cursor.fetchall():
                    content.append({
                        "id": row[0], "name": row[1], "type": row[2], "element": row[3],
                        "target": row[4], "base_damage": row[5], "base_healing": row[6],
                        "mana_cost": row[7], "cooldown": row[8], "range": row[9],
                        "accuracy": row[10], "critical_chance": row[11], "critical_multiplier": row[12],
                        "is_learned": bool(row[13]), "learned_at": row[14]
                    })
            
            elif content_type == "genes":
                cursor.execute("""
                    SELECT gene_id, name, gene_type, effect_type, value, rarity, description,
                           is_obtained, obtained_at
                    FROM session_genes WHERE session_uuid = ?
                """, (session_uuid,))
                
                for row in cursor.fetchall():
                    content.append({
                        "id": row[0], "name": row[1], "gene_type": row[2], "effect_type": row[3],
                        "value": row[4], "rarity": row[5], "description": row[6],
                        "is_obtained": bool(row[7]), "obtained_at": row[8]
                    })
            
            conn.close()
            return content
            
        except Exception as e:
            logger.error(f"Ошибка получения контента {content_type}: {e}")
            return []
    
    def get_available_slots(self) -> List[SaveSlot]:
        """Получение списка доступных слотов"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT slot_id, session_uuid, save_name, created_at, last_played,
                       player_level, world_seed, play_time, is_active
                FROM save_slots WHERE is_active = 1 ORDER BY slot_id
            """)
            
            slots = []
            for row in cursor.fetchall():
                slot = SaveSlot(
                    slot_id=row[0], session_uuid=row[1], save_name=row[2],
                    created_at=datetime.fromisoformat(row[3]),
                    last_played=datetime.fromisoformat(row[4]),
                    player_level=row[5], world_seed=row[6], play_time=row[7],
                    is_active=bool(row[8])
                )
                slots.append(slot)
            
            conn.close()
            return slots
            
        except Exception as e:
            logger.error(f"Ошибка получения слотов: {e}")
            return []
    
    def get_free_slot(self) -> Optional[int]:
        """Получение свободного слота"""
        used_slots = {slot.slot_id for slot in self.get_available_slots()}
        
        for slot_id in range(1, self.max_slots + 1):
            if slot_id not in used_slots:
                return slot_id
        
        return None
    
    def delete_session(self, slot_id: int) -> bool:
        """Удаление сессии"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Получаем UUID сессии
            cursor.execute("SELECT session_uuid FROM save_slots WHERE slot_id = ?", (slot_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"Слот {slot_id} не найден")
                return False
            
            session_uuid = result[0]
            
            # Удаляем все данные сессии
            cursor.execute("DELETE FROM session_items WHERE session_uuid = ?", (session_uuid,))
            cursor.execute("DELETE FROM session_enemies WHERE session_uuid = ?", (session_uuid,))
            cursor.execute("DELETE FROM session_weapons WHERE session_uuid = ?", (session_uuid,))
            cursor.execute("DELETE FROM session_skills WHERE session_uuid = ?", (session_uuid,))
            cursor.execute("DELETE FROM session_genes WHERE session_uuid = ?", (session_uuid,))
            cursor.execute("DELETE FROM session_data WHERE session_uuid = ?", (session_uuid,))
            cursor.execute("DELETE FROM save_slots WHERE slot_id = ?", (slot_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Сессия в слоте {slot_id} удалена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления сессии: {e}")
            return False
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Получение статистики сессий"""
        if not self.active_session:
            return {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            session_uuid = self.active_session.session_uuid
            
            stats = {
                "session_uuid": session_uuid,
                "slot_id": self.active_session.slot_id,
                "items_count": 0,
                "enemies_count": 0,
                "weapons_count": 0,
                "skills_count": 0,
                "genes_count": 0,
                "obtained_items": 0,
                "defeated_enemies": 0,
                "learned_skills": 0
            }
            
            # Подсчитываем контент
            for content_type in ["items", "enemies", "weapons", "skills", "genes"]:
                table_name = f"session_{content_type}"
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE session_uuid = ?", (session_uuid,))
                count = cursor.fetchone()[0]
                stats[f"{content_type}_count"] = count
                
                # Подсчитываем полученные/изученные
                if content_type == "items":
                    cursor.execute("SELECT COUNT(*) FROM session_items WHERE session_uuid = ? AND is_obtained = 1", (session_uuid,))
                    stats["obtained_items"] = cursor.fetchone()[0]
                elif content_type == "enemies":
                    cursor.execute("SELECT COUNT(*) FROM session_enemies WHERE session_uuid = ? AND is_defeated = 1", (session_uuid,))
                    stats["defeated_enemies"] = cursor.fetchone()[0]
                elif content_type == "skills":
                    cursor.execute("SELECT COUNT(*) FROM session_skills WHERE session_uuid = ? AND is_learned = 1", (session_uuid,))
                    stats["learned_skills"] = cursor.fetchone()[0]
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}


# Глобальный экземпляр менеджера сессий
session_manager = SessionManager()
