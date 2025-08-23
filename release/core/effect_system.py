"""
Система эффектов с поддержкой базы данных и кодовыми идентификаторами.
Управляет всеми эффектами в игре: генетическими, эмоциональными, экологическими.
"""

import sqlite3
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class EffectType(Enum):
    """Типы эффектов"""
    GENETIC = "genetic"
    EMOTIONAL = "emotional"
    ENVIRONMENTAL = "environmental"
    COMBAT = "combat"
    UTILITY = "utility"


class EffectCode(Enum):
    """Кодовые идентификаторы эффектов"""
    # Генетические эффекты
    HYPER_METABOLISM = "GENE_001"
    REGENERATION = "GENE_002"
    ACID_BLOOD = "GENE_003"
    ADAPTIVE_SKIN = "GENE_004"
    PHOTOSYNTHESIS = "GENE_005"
    ELECTRIC_ORGANS = "GENE_006"
    
    # Эмоциональные эффекты
    FEAR = "EMO_101"
    RAGE = "EMO_102"
    TRUST = "EMO_103"
    CURIOSITY = "EMO_104"
    CALMNESS = "EMO_105"
    EXCITEMENT = "EMO_106"
    
    # Комбинации эмоций
    PANIC = "COMBO_101"  # Страх + Гнев
    EXPLORATION_FERVOR = "COMBO_102"  # Доверие + Любопытство
    
    # Экологические эффекты
    RADIATION_RESISTANCE = "ENV_201"
    TOXIC_IMMUNITY = "ENV_202"
    EXTREME_TEMP = "ENV_203"
    
    # Боевые эффекты
    DAMAGE_BOOST = "COMBAT_301"
    DEFENSE_BOOST = "COMBAT_302"
    SPEED_BOOST = "COMBAT_303"
    
    # Базовые эффекты игрока
    PLAYER_BASE_BOOST = "PLAYER_BASE_BOOST"


@dataclass
class Effect:
    """Эффект с кодовым идентификатором"""
    guid: str
    code: str
    name: str
    effect_type: str
    attribute: str
    value: float
    is_percent: bool = False
    duration: float = 0.0
    tick_interval: float = 1.0
    max_stacks: int = 1
    description: str = ""
    icon: str = ""
    
    def __post_init__(self):
        if not self.guid:
            self.guid = str(uuid.uuid4())


class EffectDatabase:
    """База данных эффектов в SQLite"""
    
    def __init__(self, db_path: str = "data/game_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self._load_standard_effects()
    
    def _init_database(self):
        """Инициализация базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Создание таблицы эффектов
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS effects (
                        guid TEXT PRIMARY KEY,
                        code TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        effect_type TEXT NOT NULL,
                        attribute TEXT NOT NULL,
                        value REAL NOT NULL,
                        is_percent INTEGER DEFAULT 0,
                        duration REAL DEFAULT 0.0,
                        tick_interval REAL DEFAULT 1.0,
                        max_stacks INTEGER DEFAULT 1,
                        description TEXT DEFAULT '',
                        icon TEXT DEFAULT ''
                    )
                """)
                
                # Создание индексов для быстрого поиска
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_effects_code ON effects(code)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_effects_type ON effects(effect_type)")
                
                conn.commit()
                logger.info("База данных эффектов инициализирована")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации БД эффектов: {e}")
            raise
    
    def _load_standard_effects(self):
        """Загрузка стандартных эффектов"""
        standard_effects = [
            # Генетические эффекты
            Effect("", EffectCode.HYPER_METABOLISM.value, "Гиперметаболизм", 
                  EffectType.GENETIC.value, "stamina", 50.0, True, 0.0, 1.0, 1,
                  "Увеличивает восстановление выносливости на 50%"),
            
            Effect("", EffectCode.REGENERATION.value, "Регенерация", 
                  EffectType.GENETIC.value, "health", 10.0, False, 0.0, 1.0, 1,
                  "Восстанавливает 10 HP каждую секунду"),
            
            Effect("", EffectCode.ACID_BLOOD.value, "Кислотная кровь", 
                  EffectType.GENETIC.value, "damage", 25.0, True, 0.0, 1.0, 1,
                  "Увеличивает урон на 25%"),
            
            Effect("", EffectCode.ADAPTIVE_SKIN.value, "Адаптивная кожа", 
                  EffectType.GENETIC.value, "defense", 30.0, True, 0.0, 1.0, 1,
                  "Увеличивает защиту на 30%"),
            
            # Эмоциональные эффекты
            Effect("", EffectCode.FEAR.value, "Страх", 
                  EffectType.EMOTIONAL.value, "speed", -20.0, True, 10.0, 1.0, 1,
                  "Снижает скорость на 20% на 10 секунд"),
            
            Effect("", EffectCode.RAGE.value, "Гнев", 
                  EffectType.EMOTIONAL.value, "damage", 40.0, True, 15.0, 1.0, 1,
                  "Увеличивает урон на 40% на 15 секунд"),
            
            Effect("", EffectCode.TRUST.value, "Доверие", 
                  EffectType.EMOTIONAL.value, "defense", 15.0, True, 20.0, 1.0, 1,
                  "Увеличивает защиту на 15% на 20 секунд"),
            
            Effect("", EffectCode.CURIOSITY.value, "Любопытство", 
                  EffectType.EMOTIONAL.value, "exploration", 25.0, True, 0.0, 1.0, 1,
                  "Увеличивает скорость исследования на 25%"),
            
            # Комбинации эмоций
            Effect("", EffectCode.PANIC.value, "Паника", 
                  EffectType.EMOTIONAL.value, "damage", 30.0, True, 8.0, 1.0, 1,
                  "Страх + Гнев: +30% урон, -30% защита на 8 секунд"),
            
            Effect("", EffectCode.EXPLORATION_FERVOR.value, "Исследовательский азарт", 
                  EffectType.EMOTIONAL.value, "exploration", 50.0, True, 30.0, 1.0, 1,
                  "Доверие + Любопытство: +50% скорость исследования на 30 секунд"),
            
            # Экологические эффекты
            Effect("", EffectCode.RADIATION_RESISTANCE.value, "Радиационная устойчивость", 
                  EffectType.ENVIRONMENTAL.value, "radiation_resistance", 80.0, True, 0.0, 1.0, 1,
                  "Снижает урон от радиации на 80%"),
            
            Effect("", EffectCode.TOXIC_IMMUNITY.value, "Токсический иммунитет", 
                  EffectType.ENVIRONMENTAL.value, "poison_resistance", 100.0, True, 0.0, 1.0, 1,
                  "Полный иммунитет к ядам"),
            
            Effect("", EffectCode.EXTREME_TEMP.value, "Экстремальные температуры", 
                  EffectType.ENVIRONMENTAL.value, "temperature_resistance", 60.0, True, 0.0, 1.0, 1,
                  "Снижает урон от экстремальных температур на 60%"),
            
            # Боевые эффекты
            Effect("", EffectCode.DAMAGE_BOOST.value, "Усиление урона", 
                  EffectType.COMBAT.value, "damage", 25.0, True, 20.0, 1.0, 1,
                  "Увеличивает урон на 25% на 20 секунд"),
            
            Effect("", EffectCode.DEFENSE_BOOST.value, "Усиление защиты", 
                  EffectType.COMBAT.value, "defense", 30.0, True, 20.0, 1.0, 1,
                  "Увеличивает защиту на 30% на 20 секунд"),
            
            Effect("", EffectCode.SPEED_BOOST.value, "Ускорение", 
                  EffectType.COMBAT.value, "speed", 40.0, True, 15.0, 1.0, 1,
                  "Увеличивает скорость на 40% на 15 секунд"),
            
            # Базовые эффекты игрока
            Effect("", EffectCode.PLAYER_BASE_BOOST.value, "Базовое усиление игрока", 
                  EffectType.UTILITY.value, "all_stats", 10.0, True, 0.0, 1.0, 1,
                  "Базовое увеличение всех характеристик на 10%"),
        ]
        
        for effect in standard_effects:
            self.add_effect(effect)
    
    def add_effect(self, effect: Effect) -> bool:
        """Добавление эффекта в базу данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO effects 
                    (guid, code, name, effect_type, attribute, value, is_percent, 
                     duration, tick_interval, max_stacks, description, icon)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    effect.guid, effect.code, effect.name, effect.effect_type,
                    effect.attribute, effect.value, effect.is_percent,
                    effect.duration, effect.tick_interval, effect.max_stacks,
                    effect.description, effect.icon
                ))
                
                conn.commit()
                logger.info(f"Эффект {effect.code} добавлен в БД")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка добавления эффекта {effect.code}: {e}")
            return False
    
    def get_effect_by_code(self, code: str) -> Optional[Effect]:
        """Получение эффекта по коду"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM effects WHERE code = ?", (code,))
                row = cursor.fetchone()
                
                if row:
                    return Effect(
                        guid=row[0], code=row[1], name=row[2], effect_type=row[3],
                        attribute=row[4], value=row[5], is_percent=bool(row[6]),
                        duration=row[7], tick_interval=row[8], max_stacks=row[9],
                        description=row[10], icon=row[11]
                    )
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения эффекта {code}: {e}")
            return None
    
    def get_effects_by_type(self, effect_type: str) -> List[Effect]:
        """Получение всех эффектов определенного типа"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM effects WHERE effect_type = ?", (effect_type,))
                rows = cursor.fetchall()
                
                effects = []
                for row in rows:
                    effect = Effect(
                        guid=row[0], code=row[1], name=row[2], effect_type=row[3],
                        attribute=row[4], value=row[5], is_percent=bool(row[6]),
                        duration=row[7], tick_interval=row[8], max_stacks=row[9],
                        description=row[10], icon=row[11]
                    )
                    effects.append(effect)
                
                return effects
                
        except Exception as e:
            logger.error(f"Ошибка получения эффектов типа {effect_type}: {e}")
            return []
    
    def search_effects(self, query: str) -> List[Effect]:
        """Поиск эффектов по названию или описанию"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM effects 
                    WHERE name LIKE ? OR description LIKE ?
                """, (f"%{query}%", f"%{query}%"))
                rows = cursor.fetchall()
                
                effects = []
                for row in rows:
                    effect = Effect(
                        guid=row[0], code=row[1], name=row[2], effect_type=row[3],
                        attribute=row[4], value=row[5], is_percent=bool(row[6]),
                        duration=row[7], tick_interval=row[8], max_stacks=row[9],
                        description=row[10], icon=row[11]
                    )
                    effects.append(effect)
                
                return effects
                
        except Exception as e:
            logger.error(f"Ошибка поиска эффектов: {e}")
            return []
    
    def get_all_effects(self) -> List[Effect]:
        """Получение всех эффектов"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM effects")
                rows = cursor.fetchall()
                
                effects = []
                for row in rows:
                    effect = Effect(
                        guid=row[0], code=row[1], name=row[2], effect_type=row[3],
                        attribute=row[4], value=row[5], is_percent=bool(row[6]),
                        duration=row[7], tick_interval=row[8], max_stacks=row[9],
                        description=row[10], icon=row[11]
                    )
                    effects.append(effect)
                
                return effects
                
        except Exception as e:
            logger.error(f"Ошибка получения всех эффектов: {e}")
            return []
    
    def delete_effect(self, code: str) -> bool:
        """Удаление эффекта по коду"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM effects WHERE code = ?", (code,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Эффект {code} удален из БД")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Ошибка удаления эффекта {code}: {e}")
            return False


class ActiveEffect:
    """Активный эффект на сущности"""
    
    def __init__(self, effect: Effect, source: str = "unknown"):
        self.effect = effect
        self.source = source
        self.stacks = 1
        self.time_remaining = effect.duration
        self.last_tick = 0.0
        self.is_active = True
    
    def update(self, delta_time: float) -> bool:
        """Обновление эффекта"""
        if not self.is_active:
            return False
        
        self.time_remaining -= delta_time
        self.last_tick += delta_time
        
        # Применение эффекта по интервалу
        if self.last_tick >= self.effect.tick_interval:
            self.last_tick = 0.0
            # Здесь будет логика применения эффекта
        
        # Проверка истечения времени
        if self.time_remaining <= 0 and self.effect.duration > 0:
            self.is_active = False
            return False
        
        return True
    
    def add_stack(self) -> bool:
        """Добавление стека эффекта"""
        if self.stacks < self.effect.max_stacks:
            self.stacks += 1
            self.time_remaining = self.effect.duration  # Обновление времени
            return True
        return False
    
    def remove_stack(self) -> bool:
        """Удаление стека эффекта"""
        if self.stacks > 1:
            self.stacks -= 1
            return True
        else:
            self.is_active = False
            return False


class EffectSystem:
    """Система управления эффектами для сущности"""
    
    def __init__(self, effect_db: EffectDatabase):
        self.effect_db = effect_db
        self.active_effects: Dict[str, ActiveEffect] = {}
        self.effect_history: List[Dict[str, Any]] = []
    
    def apply_effect(self, effect_code: str, source: str = "unknown") -> bool:
        """Применение эффекта по коду"""
        effect = self.effect_db.get_effect_by_code(effect_code)
        if not effect:
            logger.warning(f"Эффект {effect_code} не найден")
            return False
        
        # Проверка существующего эффекта
        if effect.code in self.active_effects:
            active_effect = self.active_effects[effect.code]
            if active_effect.add_stack():
                logger.info(f"Добавлен стек эффекта {effect_code}")
                return True
        
        # Создание нового активного эффекта
        active_effect = ActiveEffect(effect, source)
        self.active_effects[effect.code] = active_effect
        
        # Запись в историю
        self.effect_history.append({
            "effect_code": effect.code,
            "source": source,
            "timestamp": 0.0,  # Здесь будет время игры
            "action": "applied"
        })
        
        logger.info(f"Применен эффект {effect_code} от {source}")
        return True
    
    def remove_effect(self, effect_code: str) -> bool:
        """Удаление эффекта"""
        if effect_code in self.active_effects:
            active_effect = self.active_effects[effect_code]
            if active_effect.remove_stack():
                return True
            else:
                del self.active_effects[effect_code]
                
                # Запись в историю
                self.effect_history.append({
                    "effect_code": effect_code,
                    "source": active_effect.source,
                    "timestamp": 0.0,
                    "action": "removed"
                })
                
                logger.info(f"Удален эффект {effect_code}")
                return True
        return False
    
    def update(self, delta_time: float):
        """Обновление всех активных эффектов"""
        expired_effects = []
        
        for effect_code, active_effect in self.active_effects.items():
            if not active_effect.update(delta_time):
                expired_effects.append(effect_code)
        
        # Удаление истекших эффектов
        for effect_code in expired_effects:
            del self.active_effects[effect_code]
            logger.info(f"Истек эффект {effect_code}")
    
    def get_active_effects(self) -> List[ActiveEffect]:
        """Получение всех активных эффектов"""
        return list(self.active_effects.values())
    
    def has_effect(self, effect_code: str) -> bool:
        """Проверка наличия эффекта"""
        return effect_code in self.active_effects
    
    def get_effect_stacks(self, effect_code: str) -> int:
        """Получение количества стеков эффекта"""
        if effect_code in self.active_effects:
            return self.active_effects[effect_code].stacks
        return 0
    
    def clear_all_effects(self):
        """Очистка всех эффектов"""
        self.active_effects.clear()
        logger.info("Все эффекты очищены")
    
    def get_effects_by_type(self, effect_type: str) -> List[ActiveEffect]:
        """Получение эффектов определенного типа"""
        return [
            active_effect for active_effect in self.active_effects.values()
            if active_effect.effect.effect_type == effect_type
        ]
