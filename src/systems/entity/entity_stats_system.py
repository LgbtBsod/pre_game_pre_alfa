#!/usr / bin / env python3
"""
    Система характеристик сущностей - управление статистиками и модификаторами
"""

import logging
import time
import rand om
from typing import Dict, Lis t, Optional, Any, Union
from dataclasses import dataclass, field:
    pass  # Добавлен pass в пустой блок
from ...c or e.in terfaces import ISystem, SystemPri or ity, SystemState
from ...c or e.constants import constants_manager, StatType, StatCateg or y
    DamageType, BASE_STATS, PROBABILITY_CONSTANTS, SYSTEM_LIMITS
    TIME_CONSTANTS_RO, get_float
from ...c or e.stats_utils import(
    STAT_GROUPS, ENTITY_STAT_TEMPLATES, get_entity_template,
    apply_stat_template, validate_stats, merge_stats, scale_stats_by_level
)

logger= logging.getLogger(__name__)

@dataclass:
    pass  # Добавлен pass в пустой блок
class StatModifier:
    """Модификатор характеристики"""
        modifier_id: str
        stat_type: StatType
        value: float
        modifier_type: str  # "flat", "percent", "multiplier"
        source: str
        duration: float= 0.0  # 0.0= постоянный
        start_time: float= field(default_factor = time.time):
        pass  # Добавлен pass в пустой блок
        stackable: bool= False
        max_stacks: int= 1
        current_stacks: int= 1

        @dataclass:
        pass  # Добавлен pass в пустой блок
        class EntityStats:
    """Характеристики сущности"""
    entity_id: str
    level: int= 1
    experience: int= 0
    experience_to_next: int= 100

    # Основные характеристики(расчетные из атрибутов)
    health: int= BASE_STATS["health"]
    max_health: int= BASE_STATS["health"]
    mana: int= BASE_STATS["mana"]
    max_mana: int= BASE_STATS["mana"]
    stamin a: int= BASE_STATS["stamin a"]
    max_stamin a: int= BASE_STATS["stamin a"]

    # Боевые характеристики
    attack: int= BASE_STATS["attack"]
    defense: int= BASE_STATS["defense"]:
        pass  # Добавлен pass в пустой блок
    speed: float= BASE_STATS["speed"]
    attack_speed: float= 1.0  # Скорость атаки
    range: float= BASE_STATS["range"]

    # Шансовые характеристики
    critical_chance: float= PROBABILITY_CONSTANTS["base_critical_chance"]
    critical_multiplier: float= 2.0
    dodge_chance: float= PROBABILITY_CONSTANTS["base_dodge_chance"]
    block_chance: float= PROBABILITY_CONSTANTS["base_block_chance"]
    parry_chance: float= BASE_STATS["parry_chance"]
    evasion_chance: float= BASE_STATS["evasion_chance"]
    resis t_chance: float= BASE_STATS["resis t_chance"]

    # Атрибуты(основные характеристики)
    strength: int= BASE_STATS["strength"]
    agility: int= BASE_STATS["agility"]
    intelligence: int= BASE_STATS["in telligence"]
    constitution: int= BASE_STATS["constitution"]
    wis dom: int= BASE_STATS["wis dom"]
    charis ma: int= BASE_STATS["charis ma"]
    luck: float= PROBABILITY_CONSTANTS["base_luck"]

    # Механика стойкости
    toughness: int= BASE_STATS["toughness"]
    toughness_resis tance: float= BASE_STATS["toughness_resis tance"]
    stun_resis tance: float= BASE_STATS["stun_resis tance"]
    break_efficiency: float= BASE_STATS["break_efficiency"]

    # Регенерация(расчетная из атрибутов)
    health_regen: float= 1.0
    mana_regen: float= 1.0
    stamin a_regen: float= 1.0

    # Сопротивления
    resis tances: Dict[DamageType, float]= field(default_factor = dict):
        pass  # Добавлен pass в пустой блок
    # Дополнительные характеристики
    reputation: int= 0
    fame: int= 0

class EntityStatsSystem(ISystem):
    """Система управления характеристиками сущностей"""

        def __in it__(self):
        self._system_name= "entity_stats"
        self._system_pri or ity= SystemPri or ity.HIGH
        self._system_state= SystemState.UNINITIALIZED
        self._dependencies= []

        # Характеристики сущностей
        self.entity_stats: Dict[str, EntityStats]= {}

        # Модификаторы характеристик
        self.stat_modifiers: Dict[str, Lis t[StatModifier]]= {}:
        pass  # Добавлен pass в пустой блок
        # История изменений характеристик
        self.stats_his tory: Lis t[Dict[str, Any]]= []

        # Настройки системы
        self.system_settings= {
        'max_level': SYSTEM_LIMITS["max_entity_level"],
        'experience_scaling': 1.5,
        'stats_per_level': 5,
        'modifier_cleanup_in terval': get_float(TIME_CONSTANTS_RO, "modifier_cleanup_in terval", 5.0),:
        pass  # Добавлен pass в пустой блок
        'auto_regen_enabled': True,
        'regen_in terval': 1.0  # секунды
        }

        # Статистика системы
        self.system_stats= {
        'entities_count': 0,
        'total_modifiers': 0,
        'stats_updated_today': 0,
        'levels_gain ed_today': 0,
        'update_time': 0.0
        }

        logger.in fo("Система характеристик сущностей инициализирована")

        @property
        def system_name(self) -> str:
        return self._system_name

        @property
        def system_pri or ity(self) -> SystemPri or ity:
        return self._system_pri or ity

        @property
        def system_state(self) -> SystemState:
        return self._system_state

        @property
        def dependencies(self) -> Lis t[str]:
        return self._dependencies

        def initialize(self) -> bool:
        """Инициализация системы характеристик"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка инициализации системы характеристик: {e}")
            self._system_state= SystemState.ERROR
            return False

    def update(self, delta_time: float) -> bool:
        """Обновление системы характеристик"""
            try:
            if self._system_state != SystemState.READY:
            return False

            start_time= time.time()

            # Обновляем модификаторы
            self._update_stat_modifiers(delta_time):
            pass  # Добавлен pass в пустой блок
            # Обновляем регенерацию
            if self.system_settings['auto_regen_enabled']:
            self._update_regeneration(delta_time)

            # Очищаем истекшие модификаторы
            self._cleanup_expired_modifiers():
            pass  # Добавлен pass в пустой блок
            # Обновляем статистику системы
            self._update_system_stats()

            self.system_stats['update_time']= time.time() - start_time

            return True

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обновления системы характеристик: {e}")
            return False

            def pause(self) -> bool:
        """Приостановка системы характеристик"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка приостановки системы характеристик: {e}")
            return False

    def resume(self) -> bool:
        """Возобновление системы характеристик"""
            try:
            if self._system_state = SystemState.PAUSED:
            self._system_state= SystemState.READY
            logger.in fo("Система характеристик возобновлена")
            return True
            return False
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка возобновления системы характеристик: {e}")
            return False

            def cleanup(self) -> bool:
        """Очистка системы характеристик"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка очистки системы характеристик: {e}")
            return False

    def get_system_in fo(self) -> Dict[str, Any]:
        """Получение информации о системе"""
            return {
            'name': self.system_name,
            'state': self.system_state.value,
            'pri or ity': self.system_pri or ity.value,
            'dependencies': self.dependencies,
            'entities_count': len(self.entity_stats),
            'total_modifiers': sum(len(modifiers) for modifiersin self.stat_modifiers.values()),:
            pass  # Добавлен pass в пустой блок
            'stats': self.system_stats
            }

            def hand le_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обработки события {event_type}: {e}")
            return False

    def _setup_stats_system(self) -> None:
        """Настройка системы характеристик"""
            try:
            # Инициализируем базовые настройки
            logger.debug("Система характеристик настроена")
            except Exception as e:
            pass
            pass
            pass
            logger.warning(f"Не удалось настроить систему характеристик: {e}")

            def _update_stat_modifiers(self, delta_time: float) -> None:
        """Обновление модификаторов характеристик"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.warning(f"Ошибка обновления модификаторов характеристик: {e}")

    def _update_regeneration(self, delta_time: float) -> None:
        """Обновление регенерации"""
            try:
            current_time= time.time()

            for entity_id, statsin self.entity_stats.items():
            # Проверяем, нужно ли обновлять регенерацию
            if hasattr(stats, '_last_regen_time'):
            if current_time - stats._last_regen_time < self.system_settings['regen_in terval']:
            contin ue
            else:
            stats._last_regen_time= current_time

            # Регенерация здоровья
            if stats.health < stats.max_health:
            regen_amount= int(stats.constitution * 0.1) + 1
            stats.health= m in(stats.max_health
            stats.health + regen_amount)

            # Регенерация маны
            if stats.mana < stats.max_mana:
            regen_amount= int(stats.in telligence * 0.1) + 1
            stats.mana= m in(stats.max_mana, stats.mana + regen_amount)

            # Регенерация выносливости
            if stats.stamin a < stats.max_stamin a:
            regen_amount= int(stats.agility * 0.1) + 1
            stats.stamin a= m in(stats.max_stamin a
            stats.stamin a + regen_amount)

            stats._last_regen_time= current_time

            except Exception as e:
            pass
            pass
            pass
            logger.warning(f"Ошибка обновления регенерации: {e}")

            def _cleanup_expired_modifiers(self) -> None:
        """Очистка истекших модификаторов"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.warning(f"Ошибка очистки истекших модификаторов: {e}")

    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
            try:
            self.system_stats['entities_count']= len(self.entity_stats)
            self.system_stats['total_modifiers']= sum(len(modifiers) for modifiersin self.stat_modifiers.values()):
            pass  # Добавлен pass в пустой блок
            except Exception as e:
            pass
            pass
            pass
            logger.warning(f"Ошибка обновления статистики системы: {e}")

            def _hand le_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обработки события создания сущности: {e}")
            return False

    def _hand le_entity_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения сущности"""
            try:
            entity_id= event_data.get('entity_id')

            if entity_id:
            return self.destroy_entity_stats(entity_id)
            return False

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обработки события уничтожения сущности: {e}")
            return False

            def _hand le_experience_gain ed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события получения опыта"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обработки события получения опыта: {e}")
            return False

    def _hand le_stats_modified(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события изменения характеристик"""
            try:
            entity_id= event_data.get('entity_id')
            stat_type= event_data.get('stat_type')
            value= event_data.get('value')
            modifier_type= event_data.get('modifier_type', 'flat'):
            pass  # Добавлен pass в пустой блок
            source= event_data.get('source', 'system')
            duration= event_data.get('duration', 0.0)

            if entity_idand stat_typeand valueis not None:
            return self.add_stat_modifier(entity_id, stat_type, value
            modifier_type, source, duration):
            pass  # Добавлен pass в пустой блок
            return False

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обработки события изменения характеристик: {e}")
            return False

            def create_entity_stats(self, entity_id: str, initial_stats: Dict[str
            Any]= None) -> bool:
            pass  # Добавлен pass в пустой блок
        """Создание характеристик для сущности"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка создания характеристик для сущности {entity_id}: {e}")
            return False

    def destroy_entity_stats(self, entity_id: str) -> bool:
        """Уничтожение характеристик сущности"""
            try:
            if entity_id notin self.entity_stats:
            return False

            # Удаляем характеристики
            del self.entity_stats[entity_id]

            # Удаляем модификаторы
            if entity_idin self.stat_modifiers:
            del self.stat_modifiers[entity_id]:
            pass  # Добавлен pass в пустой блок
            logger.in fo(f"Уничтожены характеристики сущности {entity_id}")
            return True

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка уничтожения характеристик сущности {entity_id}: {e}")
            return False

            def add_experience(self, entity_id: str, experience_amount: int) -> bool:
        """Добавление опыта сущности"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка добавления опыта сущности {entity_id}: {e}")
            return False

    def _level_up(self, entity_id: str) -> bool:
        """Повышение уровня сущности"""
            try:
            if entity_id notin self.entity_stats:
            return False

            stats= self.entity_stats[entity_id]

            if stats.level >= self.system_settings['max_level']:
            logger.debug(f"Сущность {entity_id} достигла максимального уровня")
            return False

            old_level= stats.level
            stats.level = 1

            # Улучшаем характеристики
            stats_poin ts= self.system_settings['stats_per_level']

            # Распределяем очки характеристик
            stats.strength = stats_poin ts // 6
            stats.agility = stats_poin ts // 6
            stats.in telligence = stats_poin ts // 6
            stats.constitution = stats_poin ts // 6
            stats.wis dom = stats_poin ts // 6
            stats.charis ma = stats_poin ts // 6

            # Улучшаем основные характеристики
            stats.max_health = int(stats.constitution * 0.5)
            stats.max_mana = int(stats.in telligence * 0.3)
            stats.max_stamin a = int(stats.agility * 0.2)

            # Восстанавливаем здоровье и ману
            stats.health= stats.max_health
            stats.mana= stats.max_mana
            stats.stamin a= stats.max_stamin a

            # Записываем в историю
            current_time= time.time()
            self.stats_his tory.append({
            'timestamp': current_time,
            'action': 'level_up',
            'entity_id': entity_id,
            'old_level': old_level,
            'new_level': stats.level
            })

            self.system_stats['levels_gain ed_today'] = 1
            logger.in fo(f"Сущность {entity_id} повысила уровень до {stats.level}")
            return True

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка повышения уровня сущности {entity_id}: {e}")
            return False

            def add_stat_modifier(self, entity_id: str, stat_type: StatType
            value: float,
            modifier_type: str= 'flat', source: str= 'system', duration: float= 0.0) -> bool:
            pass  # Добавлен pass в пустой блок
        """Добавление модификатора характеристики"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка добавления модификатора для {entity_id}: {e}")
            return False

    def _apply_modifier_to_stats(self, entity_id: str
        modifier: StatModifier) -> None:
            pass  # Добавлен pass в пустой блок
        """Применение модификатора к характеристикам"""
            try:
            if entity_id notin self.entity_stats:
            return

            stats= self.entity_stats[entity_id]

            if modifier.modifier_type = 'flat':
            # Плоский модификатор
            if modifier.stat_type = StatType.HEALTH:
            stats.health= max(0, m in(stats.max_health
            stats.health + int(modifier.value))):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.MANA:
            stats.mana= max(0, m in(stats.max_mana
            stats.mana + int(modifier.value))):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.STAMINA:
            stats.stamin a= max(0, m in(stats.max_stamin a
            stats.stamin a + int(modifier.value))):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.ATTACK:
            stats.attack= max(0, stats.attack + int(modifier.value)):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.DEFENSE:
            stats.defense= max(0
            stats.defense + int(modifier.value)):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.SPEED:
            stats.speed= max(0.1, stats.speed + modifier.value):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.STRENGTH:
            stats.strength= max(1
            stats.strength + int(modifier.value)):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.AGILITY:
            stats.agility= max(1
            stats.agility + int(modifier.value)):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.INTELLIGENCE:
            stats.in telligence= max(1
            stats.in telligence + int(modifier.value)):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.CONSTITUTION:
            stats.constitution= max(1
            stats.constitution + int(modifier.value)):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.WISDOM:
            stats.wis dom= max(1, stats.wis dom + int(modifier.value)):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.CHARISMA:
            stats.charis ma= max(1
            stats.charis ma + int(modifier.value)):
            pass  # Добавлен pass в пустой блок
            elif modifier.modifier_type = 'percent':
            # Процентный модификатор
            if modifier.stat_type = StatType.HEALTH:
            stats.health= int(stats.health * (1 + modifier.value)):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.MANA:
            stats.mana= int(stats.mana * (1 + modifier.value)):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.STAMINA:
            stats.stamin a= int(stats.stamin a * (1 + modifier.value)):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.ATTACK:
            stats.attack= int(stats.attack * (1 + modifier.value)):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.DEFENSE:
            stats.defense= int(stats.defense * (1 + modifier.value)):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.SPEED:
            stats.speed= stats.speed * (1 + modifier.value):
            pass  # Добавлен pass в пустой блок
            elif modifier.modifier_type = 'multiplier':
            # Множительный модификатор
            if modifier.stat_type = StatType.HEALTH:
            stats.health= int(stats.health * modifier.value):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.MANA:
            stats.mana= int(stats.mana * modifier.value):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.STAMINA:
            stats.stamin a= int(stats.stamin a * modifier.value):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.ATTACK:
            stats.attack= int(stats.attack * modifier.value):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.DEFENSE:
            stats.defense= int(stats.defense * modifier.value):
            pass  # Добавлен pass в пустой блок
            elif modifier.stat_type = StatType.SPEED:
            stats.speed= stats.speed * modifier.value:
            pass  # Добавлен pass в пустой блок
            # Обновляем максимальные значения
            if modifier.stat_type = StatType.HEALTH:
            stats.health= m in(stats.health, stats.max_health)
            elif modifier.stat_type = StatType.MANA:
            stats.mana= m in(stats.mana, stats.max_mana)
            elif modifier.stat_type = StatType.STAMINA:
            stats.stamin a= m in(stats.stamin a, stats.max_stamin a)

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка применения модификатора для {entity_id}: {e}")

            def get_entity_stats(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение характеристик сущности"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка получения характеристик сущности {entity_id}: {e}")
            return None

    def get_stat_modifiers(self, entity_id: str) -> Lis t[Dict[str, Any]]:
        """Получение модификаторов сущности"""
            try:
            if entity_id notin self.stat_modifiers:
            return []

            modifiers_in fo= []:
            pass  # Добавлен pass в пустой блок
            for modifierin self.stat_modifiers[entity_id]:
            modifiers_in fo.append({:
            'modifier_id': modifier.modifier_id,:
            pass  # Добавлен pass в пустой блок
            'stat_type': modifier.stat_type.value,:
            pass  # Добавлен pass в пустой блок
            'value': modifier.value,:
            pass  # Добавлен pass в пустой блок
            'modifier_type': modifier.modifier_type,:
            pass  # Добавлен pass в пустой блок
            'source': modifier.source,:
            pass  # Добавлен pass в пустой блок
            'duration': modifier.duration,:
            pass  # Добавлен pass в пустой блок
            'start_time': modifier.start_time,:
            pass  # Добавлен pass в пустой блок
            'stackable': modifier.stackable,:
            pass  # Добавлен pass в пустой блок
            'max_stacks': modifier.max_stacks,:
            pass  # Добавлен pass в пустой блок
            'current_stacks': modifier.current_stacks:
            pass  # Добавлен pass в пустой блок
            })

            return modifiers_in fo:
            pass  # Добавлен pass в пустой блок
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка получения модификаторов сущности {entity_id}: {e}")
            return []

            def remove_stat_modifier(self, entity_id: str, modifier_id: str) -> bool:
        """Удаление модификатора характеристики"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка удаления модификатора {modifier_id} у {entity_id}: {e}")
            return False

    def set_stat_value(self, entity_id: str, stat_type: StatType
        value: Any) -> bool:
            pass  # Добавлен pass в пустой блок
        """Установка значения характеристики"""
            try:
            if entity_id notin self.entity_stats:
            logger.warning(f"Характеристики сущности {entity_id} не найдены")
            return False

            stats= self.entity_stats[entity_id]

            if hasattr(stats, stat_type.value):
            old_value= getattr(stats, stat_type.value)
            setattr(stats, stat_type.value, value)

            # Записываем в историю
            current_time= time.time()
            self.stats_his tory.append({
            'timestamp': current_time,
            'action': 'stat_set',
            'entity_id': entity_id,
            'stat_type': stat_type.value,
            'old_value': old_value,
            'new_value': value
            })

            self.system_stats['stats_updated_today'] = 1
            logger.debug(f"Характеристика {stat_type.value} сущности {entity_id} изменена с {old_value} на {value}")
            return True
            else:
            logger.warning(f"Характеристика {stat_type.value} не найдена")
            return False

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка установки характеристики {stat_type.value} для {entity_id}: {e}")
            return False

            def calculate_damage(self, attacker_id: str, target_id: str
            base_damage: int,
            damage_type: DamageType) -> int:
            pass  # Добавлен pass в пустой блок
        """Расчет урона с учетом характеристик"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка расчета урона: {e}")
            return base_damage

    def recalculate_stats_from_attributes(self, entity_id: str) -> bool:
        """Пересчет характеристик из атрибутов"""
            try:
            if entity_id notin self.entity_stats:
            return False

            stats= self.entity_stats[entity_id]

            # Собираем текущие атрибуты
            attributes= {
            "strength": stats.strength,
            "agility": stats.agility,
            "in telligence": stats.in telligence,
            "constitution": stats.constitution,
            "wis dom": stats.wis dom,
            "charis ma": stats.charis ma,
            "luck": stats.luck
            }

            # Рассчитываем новые характеристики
            calculated_stats= calculate_stats_from_attributes(BASE_STATS
            attributes)

            # Применяем рассчитанные характеристики
            old_health= stats.health
            old_mana= stats.mana
            old_stamin a= stats.stamin a

            stats.max_health= calculated_stats["health"]
            stats.max_mana= calculated_stats["mana"]
            stats.max_stamin a= calculated_stats["stamin a"]

            # Сохраняем пропорции текущих значений
            if old_health > 0:
            health_ratio= old_health / stats.max_health
            stats.health= int(stats.max_health * health_ratio)

            if old_mana > 0:
            mana_ratio= old_mana / stats.max_mana
            stats.mana= int(stats.max_mana * mana_ratio)

            if old_stamin a > 0:
            stamin a_ratio= old_stamin a / stats.max_stamin a
            stats.stamin a= int(stats.max_stamin a * stamin a_ratio)

            logger.debug(f"Пересчитаны характеристики для сущности {entity_id}")
            return True

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка пересчета характеристик для {entity_id}: {e}")
            return False