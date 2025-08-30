"""
Система боя - консолидированная система для всех боевых механик
"""

import time
import random
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.core.architecture import BaseComponent, ComponentType, Priority


class CombatState(Enum):
    """Состояния боя"""
    IDLE = "idle"              # Бездействие
    IN_COMBAT = "in_combat"    # В бою
    STUNNED = "stunned"        # Оглушен
    FLEEING = "fleeing"        # Бегство
    DEAD = "dead"              # Мертв


class AttackType(Enum):
    """Типы атак"""
    MELEE = "melee"            # Ближний бой
    RANGED = "ranged"          # Дальний бой
    MAGIC = "magic"            # Магическая атака
    SPECIAL = "special"        # Специальная атака
    COUNTER = "counter"        # Контратака


class DefenseType(Enum):
    """Типы защиты"""
    BLOCK = "block"            # Блок
    DODGE = "dodge"            # Уклонение
    PARRY = "parry"            # Парирование
    ABSORB = "absorb"          # Поглощение
    REFLECT = "reflect"        # Отражение


@dataclass
class CombatStats:
    """Боевые характеристики"""
    attack_power: float = 0.0
    defense_power: float = 0.0
    critical_chance: float = 0.0
    critical_multiplier: float = 2.0
    dodge_chance: float = 0.0
    block_chance: float = 0.0
    parry_chance: float = 0.0
    attack_speed: float = 1.0
    movement_speed: float = 1.0
    range: float = 1.0


@dataclass
class CombatAction:
    """Боевое действие"""
    action_type: str
    source_id: str
    target_id: Optional[str] = None
    skill_id: Optional[str] = None
    item_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CombatResult:
    """Результат боевого действия"""
    action: CombatAction
    success: bool = False
    damage_dealt: float = 0.0
    damage_taken: float = 0.0
    effects_applied: List[str] = field(default_factory=list)
    critical_hit: bool = False
    blocked: bool = False
    dodged: bool = False
    parried: bool = False
    timestamp: float = field(default_factory=time.time)


class CombatSystem(BaseComponent):
    """
    Консолидированная боевая система
    Управляет всеми аспектами боя в игре
    """
    
    def __init__(self):
        super().__init__(
            name="CombatSystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Боевые состояния сущностей
        self.combat_states: Dict[str, CombatState] = {}
        self.combat_stats: Dict[str, CombatStats] = {}
        
        # Активные бои
        self.active_combats: Dict[str, Dict[str, Any]] = {}
        self.combat_history: List[CombatAction] = []
        
        # Система инициативы
        self.initiative_order: List[str] = []
        self.initiative_timers: Dict[str, float] = {}
        
        # Система позиционирования
        self.entity_positions: Dict[str, Tuple[float, float, float]] = {}
        self.attack_ranges: Dict[str, float] = {}
        
        # Настройки
        self.max_combat_history = 1000
        self.initiative_base = 100.0
        
    def _on_initialize(self) -> bool:
        """Инициализация боевой системы"""
        try:
            # Регистрация базовых боевых механик
            self._register_combat_mechanics()
            
            # Настройка системы инициативы
            self._setup_initiative_system()
            
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации CombatSystem: {e}")
            return False
    
    def _register_combat_mechanics(self):
        """Регистрация базовых боевых механик"""
        # TODO: Регистрация механик атак, защиты, движения
        pass
    
    def _setup_initiative_system(self):
        """Настройка системы инициативы"""
        self.initiative_base = 100.0
    
    # Управление боевыми состояниями
    def enter_combat(self, entity_id: str, target_id: str) -> bool:
        """Войти в бой"""
        if entity_id in self.combat_states and self.combat_states[entity_id] == CombatState.DEAD:
            return False
    
        # Устанавливаем состояние боя
        self.combat_states[entity_id] = CombatState.IN_COMBAT
        
        # Создаем или обновляем активный бой
        combat_id = f"combat_{int(time.time() * 1000)}"
        if entity_id not in self.active_combats:
            self.active_combats[entity_id] = {
                'combat_id': combat_id,
                'targets': [target_id],
                'start_time': time.time(),
                'actions': []
            }
        
        # Добавляем цель в бой
        if target_id not in self.active_combats[entity_id]['targets']:
            self.active_combats[entity_id]['targets'].append(target_id)
        
        # Обновляем инициативу
        self._update_initiative(entity_id)
        
        return True
    
    def exit_combat(self, entity_id: str) -> bool:
        """Выйти из боя"""
        if entity_id not in self.combat_states:
            return False
    
        # Убираем из активных боев
        if entity_id in self.active_combats:
            del self.active_combats[entity_id]
        
        # Возвращаем в обычное состояние
        self.combat_states[entity_id] = CombatState.IDLE
        
        # Убираем из инициативы
        if entity_id in self.initiative_order:
            self.initiative_order.remove(entity_id)
        if entity_id in self.initiative_timers:
            del self.initiative_timers[entity_id]
            
            return True
            
    def is_in_combat(self, entity_id: str) -> bool:
        """Проверить, находится ли сущность в бою"""
        return (entity_id in self.combat_states and 
                self.combat_states[entity_id] == CombatState.IN_COMBAT)
    
    # Боевые действия
    def perform_attack(self, attacker_id: str, target_id: str, skill_id: Optional[str] = None, item_id: Optional[str] = None) -> CombatResult:
        """Выполнить атаку"""
        # Проверяем возможность атаки
        if not self._can_attack(attacker_id, target_id):
            return CombatResult(
                action=CombatAction("attack", attacker_id, target_id, skill_id, item_id),
                success=False
            )
        
        # Создаем действие
        action = CombatAction("attack", attacker_id, target_id, skill_id, item_id)
        
        # Рассчитываем результат атаки
        result = self._calculate_attack_result(action)
        
        # Применяем результат
        self._apply_combat_result(result)
        
        # Сохраняем в историю
        self._add_to_history(action)
        
        return result
    
    def perform_defense(self, defender_id: str, attack_action: CombatAction) -> CombatResult:
        """Выполнить защиту"""
        # Создаем действие защиты
        defense_action = CombatAction("defense", defender_id, attack_action.source_id)
        
        # Рассчитываем результат защиты
        result = self._calculate_defense_result(defense_action, attack_action)
        
        # Применяем результат
        self._apply_combat_result(result)
        
        return result
    
    def perform_movement(self, entity_id: str, new_position: Tuple[float, float, float]) -> bool:
        """Выполнить движение"""
        if not self._can_move(entity_id, new_position):
            return False
        
        # Обновляем позицию
        old_position = self.entity_positions.get(entity_id, (0, 0, 0))
        self.entity_positions[entity_id] = new_position
        
        # Проверяем, не вышли ли из зоны атаки
        self._check_attack_range(entity_id, old_position, new_position)
        
        return True
    
    # Расчет результатов
    def _calculate_attack_result(self, action: CombatAction) -> CombatResult:
        """Рассчитать результат атаки"""
        attacker_id = action.source_id
        target_id = action.target_id
        
        # Получаем характеристики
        attacker_stats = self.combat_stats.get(attacker_id, CombatStats())
        target_stats = self.combat_stats.get(target_id, CombatStats())
        
        # Базовый урон
        base_damage = attacker_stats.attack_power
        
        # Модификаторы от навыка
        if action.skill_id:
            base_damage = self._apply_skill_modifiers(base_damage, action.skill_id)
        
        # Модификаторы от предмета
        if action.item_id:
            base_damage = self._apply_item_modifiers(base_damage, action.item_id)
        
        # Критический удар
        critical_hit = random.random() < attacker_stats.critical_chance
        if critical_hit:
            base_damage *= attacker_stats.critical_multiplier
        
        # Защита цели
        final_damage = self._apply_target_defense(base_damage, target_stats)
        
        # Создаем результат
        result = CombatResult(
            action=action,
            success=True,
            damage_dealt=final_damage,
            critical_hit=critical_hit
        )
        
        return result
    
    def _calculate_defense_result(self, defense_action: CombatAction, attack_action: CombatAction) -> CombatResult:
        """Рассчитать результат защиты"""
        defender_id = defense_action.source_id
        defender_stats = self.combat_stats.get(defender_id, CombatStats())
        
        # Определяем тип защиты
        defense_type = self._determine_defense_type(defender_stats)
        
        # Рассчитываем эффективность защиты
        defense_effectiveness = self._calculate_defense_effectiveness(defense_type, defender_stats)
        
        # Создаем результат
        result = CombatResult(
            action=defense_action,
            success=True,
            blocked=(defense_type == DefenseType.BLOCK),
            dodged=(defense_type == DefenseType.DODGE),
            parried=(defense_type == DefenseType.PARRY)
        )
        
        return result
    
    def _apply_target_defense(self, damage: float, target_stats: CombatStats) -> float:
        """Применить защиту цели"""
        final_damage = damage
        
        # Уклонение
        if random.random() < target_stats.dodge_chance:
            return 0.0
        
        # Блок
        if random.random() < target_stats.block_chance:
            final_damage *= 0.5
        
        # Парирование
        if random.random() < target_stats.parry_chance:
            final_damage *= 0.3
        
        # Защита
        final_damage = max(1, final_damage - target_stats.defense_power)
        
        return final_damage
    
    def _determine_defense_type(self, stats: CombatStats) -> DefenseType:
        """Определить тип защиты"""
        # Простая логика выбора защиты
        if stats.dodge_chance > stats.block_chance and stats.dodge_chance > stats.parry_chance:
            return DefenseType.DODGE
        elif stats.block_chance > stats.parry_chance:
            return DefenseType.BLOCK
        else:
            return DefenseType.PARRY
    
    def _calculate_defense_effectiveness(self, defense_type: DefenseType, stats: CombatStats) -> float:
        """Рассчитать эффективность защиты"""
        if defense_type == DefenseType.DODGE:
            return stats.dodge_chance
        elif defense_type == DefenseType.BLOCK:
            return stats.block_chance
        elif defense_type == DefenseType.PARRY:
            return stats.parry_chance
        else:
            return 0.0
    
    # Модификаторы
    def _apply_skill_modifiers(self, base_damage: float, skill_id: str) -> float:
        """Применить модификаторы от навыка"""
        # TODO: Интеграция с системой навыков
        return base_damage
    
    def _apply_item_modifiers(self, base_damage: float, item_id: str) -> float:
        """Применить модификаторы от предмета"""
        # TODO: Интеграция с системой инвентаря
        return base_damage
    
    # Проверки
    def _can_attack(self, attacker_id: str, target_id: str) -> bool:
        """Проверить возможность атаки"""
        # Проверяем состояние
        if attacker_id not in self.combat_states or self.combat_states[attacker_id] == CombatState.DEAD:
                return False
            
        if target_id not in self.combat_states or self.combat_states[target_id] == CombatState.DEAD:
            return False
    
        # Проверяем дистанцию
        if not self._is_in_range(attacker_id, target_id):
            return False
            
        # Проверяем инициативу
        if not self._can_act(attacker_id):
            return False
    
        return True
    
    def _can_move(self, entity_id: str, new_position: Tuple[float, float, float]) -> bool:
        """Проверить возможность движения"""
        # Проверяем состояние
        if entity_id not in self.combat_states or self.combat_states[entity_id] == CombatState.DEAD:
            return False
            
        # Проверяем инициативу
        if not self._can_act(entity_id):
            return False
    
        return True
    
    def _is_in_range(self, attacker_id: str, target_id: str) -> bool:
        """Проверить, находится ли цель в зоне атаки"""
        attacker_pos = self.entity_positions.get(attacker_id, (0, 0, 0))
        target_pos = self.entity_positions.get(target_id, (0, 0, 0))
        
        # Рассчитываем дистанцию
        dx = attacker_pos[0] - target_pos[0]
        dy = attacker_pos[1] - target_pos[1]
        dz = attacker_pos[2] - target_pos[2]
        distance = (dx*dx + dy*dy + dz*dz) ** 0.5
        
        # Проверяем дальность атаки
        attack_range = self.attack_ranges.get(attacker_id, 1.0)
        return distance <= attack_range
    
    def _can_act(self, entity_id: str) -> bool:
        """Проверить, может ли сущность действовать"""
        if entity_id not in self.initiative_timers:
            return True
        
        return time.time() >= self.initiative_timers[entity_id]
    
    # Система инициативы
    def _update_initiative(self, entity_id: str):
        """Обновить инициативу сущности"""
        if entity_id not in self.initiative_order:
            self.initiative_order.append(entity_id)
        
        # Рассчитываем время следующего действия
        stats = self.combat_stats.get(entity_id, CombatStats())
        action_delay = self.initiative_base / stats.attack_speed
        self.initiative_timers[entity_id] = time.time() + action_delay
        
        # Сортируем по времени
        self.initiative_order.sort(key=lambda x: self.initiative_timers.get(x, 0))
    
    def get_next_actor(self) -> Optional[str]:
        """Получить следующего действующего"""
        current_time = time.time()
        
        for entity_id in self.initiative_order:
            if entity_id in self.initiative_timers:
                if current_time >= self.initiative_timers[entity_id]:
                    return entity_id
        
                return None
            
    # Позиционирование
    def set_entity_position(self, entity_id: str, position: Tuple[float, float, float]):
        """Установить позицию сущности"""
        self.entity_positions[entity_id] = position
    
    def get_entity_position(self, entity_id: str) -> Tuple[float, float, float]:
        """Получить позицию сущности"""
        return self.entity_positions.get(entity_id, (0, 0, 0))
    
    def set_attack_range(self, entity_id: str, range_value: float):
        """Установить дальность атаки сущности"""
        self.attack_ranges[entity_id] = range_value
    
    def _check_attack_range(self, entity_id: str, old_position: Tuple[float, float, float], new_position: Tuple[float, float, float]):
        """Проверить, не вышла ли сущность из зоны атаки"""
        # TODO: Логика проверки выхода из зоны атаки
        pass
    
    # Применение результатов
    def _apply_combat_result(self, result: CombatResult):
        """Применить результат боя"""
        if not result.success:
            return
        
        # Применяем урон
        if result.damage_dealt > 0:
            self._apply_damage(result.action.target_id, result.damage_dealt)
        
        # Применяем эффекты
        for effect_id in result.effects_applied:
            self._apply_effect(result.action.target_id, effect_id)
        
        # Обновляем инициативу
        self._update_initiative(result.action.source_id)
    
    def _apply_damage(self, target_id: str, damage: float):
        """Применить урон"""
        # TODO: Интеграция с системой здоровья
        pass
    
    def _apply_effect(self, target_id: str, effect_id: str):
        """Применить эффект"""
        # TODO: Интеграция с системой эффектов
        pass
    
    # История и статистика
    def _add_to_history(self, action: CombatAction):
        """Добавить действие в историю"""
        self.combat_history.append(action)
        
        # Ограничиваем размер истории
        if len(self.combat_history) > self.max_combat_history:
            self.combat_history.pop(0)
    
    def get_combat_history(self, entity_id: Optional[str] = None) -> List[CombatAction]:
        """Получить историю боя"""
        if entity_id:
            return [a for a in self.combat_history if a.source_id == entity_id or a.target_id == entity_id]
        return self.combat_history.copy()
    
    def get_combat_statistics(self, entity_id: str) -> Dict[str, Any]:
        """Получить боевую статистику сущности"""
        entity_actions = [a for a in self.combat_history if a.source_id == entity_id]
        
        if not entity_actions:
            return {}
        
        attacks = [a for a in entity_actions if a.action_type == "attack"]
        defenses = [a for a in entity_actions if a.action_type == "defense"]
        
        return {
            'total_actions': len(entity_actions),
            'attacks_performed': len(attacks),
            'defenses_performed': len(defenses),
            'combat_time': time.time() - min(a.timestamp for a in entity_actions) if entity_actions else 0
        }
    
    # Публичные методы
    def register_combat_stats(self, entity_id: str, stats: CombatStats):
        """Зарегистрировать боевые характеристики"""
        self.combat_stats[entity_id] = stats
    
    def get_combat_stats(self, entity_id: str) -> Optional[CombatStats]:
        """Получить боевые характеристики"""
        return self.combat_stats.get(entity_id)
    
    def clear_combat_history(self):
        """Очистить историю боя"""
        self.combat_history.clear()
    
    def get_active_combats(self) -> Dict[str, Dict[str, Any]]:
        """Получить активные бои"""
        return self.active_combats.copy()
    
    def force_exit_combat(self, entity_id: str):
        """Принудительно вывести из боя"""
        self.exit_combat(entity_id)
