# buff_manager.py
import sqlite3
import json
import time
from typing import List, Dict, Optional, Union
from enum import Enum, auto


class BuffType(Enum):
    PERCENT = auto()
    FLAT = auto()
    MULTIPLY = auto()


class BuffEffect:
    def __init__(self, stat: str, value: float, duration: float, buff_type: BuffType):
        self.stat = stat
        self.value = value
        self.duration = duration
        self.type = buff_type
        self.start_time = time.time()
        self.end_time = self.start_time + duration if duration > 0 else None


class BuffManager:
    def __init__(self, player, db_path: str = 'assets/items.db'):
        self.player = player
        self.db_path = db_path
        self.active_buffs: List[BuffEffect] = []
        self.expired_buffs: List[BuffEffect] = []
        self._last_cleanup_time = 0

    def load_passive_effects(self, item_name: str) -> bool:
        """Загружает и применяет пассивные баффы из БД"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT effect FROM artifacts WHERE name=?", (item_name,))
                result = cursor.fetchone()

            if not result or not result[0]:
                return False

            effect_data = json.loads(result[0])
            for buff in effect_data.get('buffs', []):
                self.apply_buff(buff)
            return True

        except json.JSONDecodeError as e:
            print(f'Ошибка парсинга эффекта для {item_name}: {e}')
            return False
        except sqlite3.Error as e:
            print(f'Ошибка БД при загрузке эффектов: {e}')
            return False

    def apply_buff(self, buff_data: Dict) -> bool:
        """Применяет один бафф из словаря данных"""
        try:
            stat = buff_data['stat']
            if stat not in self.player.base_stats:
                print(f"Характеристика {stat} не найдена в base_stats")
                return False

            buff_type = BuffType[buff_data['type'].upper()]
            value = float(buff_data['value'])
            duration = float(buff_data.get('duration', 0))

            buff = BuffEffect(stat, value, duration, buff_type)
            self._apply_buff_effect(buff)
            self.active_buffs.append(buff)
            return True

        except KeyError as e:
            print(f"Неверный формат баффа: отсутствует ключ {e}")
            return False
        except ValueError as e:
            print(f"Ошибка значения в баффе: {e}")
            return False

    def _apply_buff_effect(self, buff: BuffEffect):
        """Применяет эффект баффа к игроку"""
        from .effects import apply_flat_buff, apply_multiply_buff, apply_percent_buff, reset_stat

        if buff.type == BuffType.PERCENT:
            apply_percent_buff(self.player, buff.stat, buff.value, buff.duration)
        elif buff.type == BuffType.FLAT:
            apply_flat_buff(self.player, buff.stat, buff.value, buff.duration)
        elif buff.type == BuffType.MULTIPLY:
            apply_multiply_buff(self.player, buff.stat, buff.value, buff.duration)

        print(f"[BUFF] Применён {buff.type.name} бафф {buff.stat}: {buff.value} на {buff.duration or '∞'} сек")

    def cleanup_expired_buffs(self):
        """Очищает завершившиеся баффы"""
        current_time = time.time()
        if current_time - self._last_cleanup_time < 1.0:  # Оптимизация: не проверять каждый кадр
            return

        self._last_cleanup_time = current_time
        new_active_buffs = []
        
        for buff in self.active_buffs:
            if buff.end_time is None or buff.end_time > current_time:
                new_active_buffs.append(buff)
            else:
                self.expired_buffs.append(buff)
                print(f"[BUFF] Закончился бафф {buff.stat}")

        self.active_buffs = new_active_buffs

    def get_active_buffs(self) -> List[Dict]:
        """Возвращает список активных баффов в виде словарей"""
        self.cleanup_expired_buffs()
        return [{
            'stat': buff.stat,
            'type': buff.type.name.lower(),
            'value': buff.value,
            'time_left': buff.end_time - time.time() if buff.end_time else None
        } for buff in self.active_buffs]

    def update(self):
        """Обновляет состояние баффов, вызывается каждый кадр"""
        self.cleanup_expired_buffs()
        self._process_periodic_effects()

    def _process_periodic_effects(self):
        """Обрабатывает периодические эффекты (регенерация и т.д.)"""
        # Пример: регенерация здоровья, если есть соответствующий бафф
        regen_buffs = [b for b in self.active_buffs if b.stat == 'health_regen']
        if regen_buffs:
            total_regen = sum(b.value for b in regen_buffs)
            self.player.current_stats['health'] = min(
                self.player.current_stats['health'] + total_regen * time.dt,
                self.player.current_stats['max_health']
            )

    def has_buff(self, stat: str, min_value: Optional[float] = None) -> bool:
        """Проверяет, есть ли активный бафф для указанной характеристики"""
        self.cleanup_expired_buffs()
        for buff in self.active_buffs:
            if buff.stat == stat and (min_value is None or buff.value >= min_value):
                return True
        return False

    def get_combined_buff_value(self, stat: str) -> float:
        """Возвращает суммарное значение всех активных баффов для характеристики"""
        self.cleanup_expired_buffs()
        total = 0.0
        for buff in self.active_buffs:
            if buff.stat == stat:
                if buff.type == BuffType.FLAT:
                    total += buff.value
                elif buff.type == BuffType.PERCENT:
                    total += buff.value * self.player.base_stats[stat]
        return total
    
    def save_active_buffs(self):
        """Сохраняет активные баффы в JSON"""
        active = [{
            'stat': b.stat,
            'type': b.type.name.lower(),
            'value': b.value,
            'duration_left': max(b.end_time - time.time(), 0) if b.end_time else None
        } for b in self.active_buffs]

        with open('saves/active_buffs.json', 'w') as f:
            json.dump(active, f, indent=4)
            
    def load_saved_buffs(self):
        try:
            with open('saves/active_buffs.json', 'r') as f:
                buffs = json.load(f)
            for b in buffs:
                self.apply_buff({
                    'type': b['type'],
                    'stat': b['stat'],
                    'value': b['value'],
                    'duration': b['duration_left']
                })
        except Exception as e:
            print(f'Не удалось загрузить баффы: {e}')