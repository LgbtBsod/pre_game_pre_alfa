# buff_manager.py
import sqlite3
import json
import time
from typing import List, Dict, Optional, Union, Tuple
from enum import Enum, auto
from .stat_modifier import StatModifier, ModifierType

class BuffType(Enum):
    BUFF = auto()
    DEBUFF = auto()
    AURA = auto()

class BuffEffect:
    def __init__(
        self,
        stat: str,
        modifier: str,
        duration: float,
        buff_type: BuffType,
        source: str = None,
        is_permanent: bool = False
    ):
        self.stat = stat
        self.modifier = modifier
        self.duration = duration
        self.type = buff_type
        self.source = source
        self.is_permanent = is_permanent
        self.start_time = time.time()
        self.end_time = self.start_time + duration if duration > 0 and not is_permanent else None
        self.mod_value, self.mod_type = StatModifier.parse(modifier)
        
        # Для визуализации
        self.icon = self._get_icon()
        self.description = self._generate_description()

    def _get_icon(self) -> str:
        """Возвращает иконку в зависимости от типа баффа/дебафа"""
        icons = {
            (BuffType.BUFF, ModifierType.FLAT): "buff_flat",
            (BuffType.BUFF, ModifierType.PERCENT_ADD): "buff_percent",
            (BuffType.DEBUFF, ModifierType.FLAT): "debuff_flat",
            (BuffType.DEBUFF, ModifierType.PERCENT_ADD): "debuff_percent"
        }
        return icons.get((self.type, self.mod_type), "default_icon")

    def _generate_description(self) -> str:
        """Генерирует описание эффекта"""
        stat_names = {
            "health": "Здоровье",
            "attack": "Атака",
            "speed": "Скорость"
        }
        
        stat_name = stat_names.get(self.stat, self.stat)
        value_str = self.modifier.replace("*", "×").replace("%", "%%")
        
        if self.type == BuffType.BUFF:
            return f"+{value_str} к {stat_name}"
        else:
            return f"-{value_str} к {stat_name}"

    @property
    def time_left(self) -> Optional[float]:
        if self.is_permanent:
            return None
        return max(self.end_time - time.time(), 0) if self.end_time else None

    @property
    def is_active(self) -> bool:
        return self.is_permanent or (self.end_time and self.end_time > time.time())

class BuffManager:
    def __init__(self, player, db_path: str = 'assets/items.db'):
        self.player = player
        self.db_path = db_path
        self.active_effects: List[BuffEffect] = []
        self._last_cleanup_time = 0
        self._stat_cache = {}  # Кеш для оптимизации
        
        # Группировка эффектов по характеристикам
        self._stat_effects: Dict[str, List[BuffEffect]] = {}

    def _update_stat_cache(self, stat: str):
        """Обновляет кеш для указанной характеристики"""
        if stat not in self._stat_effects:
            self._stat_effects[stat] = []
        
        active_effects = [e for e in self.active_effects if e.stat == stat and e.is_active]
        self._stat_effects[stat] = active_effects
        
        # Пересчитываем итоговое значение
        modifiers = [e.modifier for e in active_effects]
        base_value = self.player.base_stats.get(stat, 0)
        self._stat_cache[stat] = StatModifier.apply_multiple(base_value, modifiers)

    def _apply_to_player(self):
        """Применяет все активные эффекты к игроку"""
        for stat in self._stat_effects.keys():
            if stat in self.player.current_stats:
                self.player.current_stats[stat] = self._stat_cache.get(stat, self.player.base_stats[stat])

    def load_passive_effects(self, item_name: str) -> bool:
        """Загружает пассивные эффекты из базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT effect, is_buff FROM artifacts WHERE name=?",
                    (item_name,)
                )
                result = cursor.fetchone()

            if not result:
                return False

            effect_data, is_buff = result
            if not effect_data:
                return False

            effect_type = BuffType.BUFF if is_buff else BuffType.DEBUFF
            effects = json.loads(effect_data)
            
            for effect in effects.get('effects', []):
                self.add_effect(
                    stat=effect['stat'],
                    modifier=effect['modifier'],
                    duration=effect.get('duration', 0),
                    buff_type=effect_type,
                    source=item_name,
                    is_permanent=effect.get('is_permanent', False)
                )
            return True

        except Exception as e:
            print(f"Ошибка загрузки эффектов для {item_name}: {e}")
            return False

    def add_effect(
        self,
        stat: str,
        modifier: str,
        duration: float = 0,
        buff_type: BuffType = BuffType.BUFF,
        source: str = None,
        is_permanent: bool = False
    ) -> bool:
        """Добавляет новый эффект (бафф или дебаф)"""
        if stat not in self.player.base_stats:
            print(f"Характеристика {stat} не найдена")
            return False

        # Проверяем уникальность эффекта от источника
        if source:
            existing = next(
                (e for e in self.active_effects 
                 if e.source == source and e.stat == stat),
                None
            )
            if existing:
                self.remove_effect(existing)

        effect = BuffEffect(stat, modifier, duration, buff_type, source, is_permanent)
        self.active_effects.append(effect)
        self._update_stat_cache(stat)
        self._apply_to_player()
        
        print(f"[EFFECT] {'+' if buff_type == BuffType.BUFF else '-'} "
              f"{stat}: {modifier} ({duration or 'permanent'})")
        return True

    def remove_effect(self, effect: BuffEffect) -> bool:
        """Удаляет указанный эффект"""
        if effect in self.active_effects:
            self.active_effects.remove(effect)
            self._update_stat_cache(effect.stat)
            self._apply_to_player()
            return True
        return False

    def remove_effects_by_source(self, source: str) -> int:
        """Удаляет все эффекты от указанного источника"""
        removed = 0
        for effect in list(self.active_effects):
            if effect.source == source:
                if self.remove_effect(effect):
                    removed += 1
        return removed

    def cleanup_expired(self):
        """Очищает завершившиеся временные эффекты"""
        current_time = time.time()
        if current_time - self._last_cleanup_time < 1.0:  # Оптимизация
            return

        self._last_cleanup_time = current_time
        needs_update = False

        for effect in list(self.active_effects):
            if not effect.is_permanent and not effect.is_active:
                self.active_effects.remove(effect)
                needs_update = True
                print(f"[EFFECT] Закончился эффект {effect.stat}")

        if needs_update:
            self._update_all_stats()

    def _update_all_stats(self):
        """Обновляет все характеристики"""
        stats_to_update = {e.stat for e in self.active_effects}
        for stat in stats_to_update:
            self._update_stat_cache(stat)
        self._apply_to_player()

    def get_active_effects(self, stat: str = None) -> List[BuffEffect]:
        """Возвращает активные эффекты для характеристики или все"""
        self.cleanup_expired()
        if stat:
            return [e for e in self.active_effects if e.stat == stat and e.is_active]
        return [e for e in self.active_effects if e.is_active]

    def get_effect_value(self, stat: str) -> float:
        """Возвращает текущее значение характеристики с учетом эффектов"""
        return self._stat_cache.get(stat, self.player.base_stats.get(stat, 0))

    def update(self, dt: float):
        """Обновляет состояние менеджера"""
        self.cleanup_expired()
        self._process_periodic_effects(dt)

    def _process_periodic_effects(self, dt: float):
        """Обрабатывает периодические эффекты (регенерация и т.д.)"""
        # Пример: регенерация здоровья
        if 'health_regen' in self._stat_cache:
            regen_value = self._stat_cache['health_regen']
            max_health = self.get_effect_value('max_health')
            current_health = self.player.current_stats['health']
            self.player.current_stats['health'] = min(
                current_health + regen_value * dt,
                max_health
            )

    def save_state(self, filepath: str = 'saves/buffs.json'):
        """Сохраняет текущее состояние эффектов"""
        state = {
            'effects': [{
                'stat': e.stat,
                'modifier': e.modifier,
                'type': e.type.name,
                'source': e.source,
                'duration_left': e.time_left,
                'is_permanent': e.is_permanent
            } for e in self.active_effects if e.is_permanent or e.time_left]
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения эффектов: {e}")
            return False

    def load_state(self, filepath: str = 'saves/buffs.json'):
        """Загружает сохраненное состояние эффектов"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.clear_effects()
            
            for effect_data in state.get('effects', []):
                self.add_effect(
                    stat=effect_data['stat'],
                    modifier=effect_data['modifier'],
                    duration=effect_data.get('duration_left', 0),
                    buff_type=BuffType[effect_data['type']],
                    source=effect_data.get('source'),
                    is_permanent=effect_data.get('is_permanent', False)
                )
            return True
        except Exception as e:
            print(f"Ошибка загрузки эффектов: {e}")
            return False

    def clear_effects(self):
        """Очищает все эффекты"""
        self.active_effects.clear()
        self._stat_cache.clear()
        self._stat_effects.clear()
        self._apply_to_player()