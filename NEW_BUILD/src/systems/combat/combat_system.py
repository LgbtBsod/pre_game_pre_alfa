#!/usr/bin/env python3
"""
Combat System - Система боя
Отвечает только за боевые взаимодействия между сущностями
"""

import logging
import random
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CombatState(Enum):
    """Состояния боя"""
    IDLE = "idle"           # Не в бою
    PREPARING = "preparing" # Подготовка к бою
    ATTACKING = "attacking" # Атака
    DEFENDING = "defending" # Защита
    STUNNED = "stunned"     # Оглушен
    RETREATING = "retreating" # Отступление

class AttackType(Enum):
    """Типы атак"""
    MELEE = "melee"         # Ближний бой
    RANGED = "ranged"       # Дальний бой
    MAGIC = "magic"         # Магическая атака
    SPECIAL = "special"     # Специальная атака

class DamageType(Enum):
    """Типы урона"""
    PHYSICAL = "physical"   # Физический
    MAGICAL = "magical"     # Магический
    FIRE = "fire"           # Огонь
    ICE = "ice"             # Лед
    LIGHTNING = "lightning" # Молния
    POISON = "poison"       # Яд

@dataclass
class CombatStats:
    """Боевая статистика"""
    attack: int = 10
    defense: int = 5
    critical_chance: float = 0.05
    critical_multiplier: float = 2.0
    dodge_chance: float = 0.1
    block_chance: float = 0.15
    resistance: Dict[DamageType, float] = None
    
    def __post_init__(self):
        if self.resistance is None:
            self.resistance = {
                DamageType.PHYSICAL: 0.0,
                DamageType.MAGICAL: 0.0,
                DamageType.FIRE: 0.0,
                DamageType.ICE: 0.0,
                DamageType.LIGHTNING: 0.0,
                DamageType.POISON: 0.0
            }

@dataclass
class AttackResult:
    """Результат атаки"""
    hit: bool = False
    damage: int = 0
    critical: bool = False
    blocked: bool = False
    dodged: bool = False
    damage_type: DamageType = DamageType.PHYSICAL
    effects: List[str] = None
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = []

@dataclass
class CombatAction:
    """Боевое действие"""
    attacker_id: str
    target_id: str
    action_type: AttackType
    damage_type: DamageType
    base_damage: int
    effects: List[str] = None
    cooldown: float = 0.0
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = []

class CombatSystem:
    """Система боя"""
    
    def __init__(self):
        self.combat_entities: Dict[str, Dict[str, Any]] = {}
        self.active_combats: Dict[str, Dict[str, Any]] = {}
        self.combat_history: List[Dict[str, Any]] = []
        self.attack_cooldowns: Dict[str, float] = {}
        
        logger.info("Система боя инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы боя"""
        try:
            logger.info("Система боя успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы боя: {e}")
            return False
    
    def register_entity(self, entity_id: str, entity_data: Dict[str, Any]):
        """Регистрация сущности в системе боя"""
        if entity_id in self.combat_entities:
            logger.warning(f"Сущность {entity_id} уже зарегистрирована в системе боя")
            return False
        
        # Создаем боевую статистику
        combat_stats = CombatStats(
            attack=entity_data.get("attack", 10),
            defense=entity_data.get("defense", 5),
            critical_chance=entity_data.get("critical_chance", 0.05),
            critical_multiplier=entity_data.get("critical_multiplier", 2.0),
            dodge_chance=entity_data.get("dodge_chance", 0.1),
            block_chance=entity_data.get("block_chance", 0.15)
        )
        
        # Устанавливаем сопротивления
        if "resistances" in entity_data:
            for damage_type, resistance in entity_data["resistances"].items():
                if damage_type in DamageType:
                    combat_stats.resistance[DamageType(damage_type)] = resistance
        
        combat_data = {
            "id": entity_id,
            "combat_state": CombatState.IDLE,
            "combat_stats": combat_stats,
            "current_target": None,
            "last_attack_time": 0.0,
            "stunned_until": 0.0,
            "combat_wins": 0,
            "combat_losses": 0,
            "total_damage_dealt": 0,
            "total_damage_taken": 0
        }
        
        self.combat_entities[entity_id] = combat_data
        logger.info(f"Сущность {entity_id} зарегистрирована в системе боя")
        return True
    
    def unregister_entity(self, entity_id: str):
        """Отмена регистрации сущности"""
        if entity_id in self.combat_entities:
            del self.combat_entities[entity_id]
        
        # Удаляем из активных боев
        for combat_id in list(self.active_combats.keys()):
            combat = self.active_combats[combat_id]
            if entity_id in [combat["attacker_id"], combat["target_id"]]:
                self._end_combat(combat_id)
        
        logger.info(f"Сущность {entity_id} удалена из системы боя")
    
    def start_combat(self, attacker_id: str, target_id: str) -> bool:
        """Начало боя между двумя сущностями"""
        if attacker_id not in self.combat_entities or target_id not in self.combat_entities:
            logger.error(f"Одна из сущностей не зарегистрирована в системе боя")
            return False
        
        # Проверяем, не в бою ли уже одна из сущностей
        if (self.combat_entities[attacker_id]["combat_state"] != CombatState.IDLE or
            self.combat_entities[target_id]["combat_state"] != CombatState.IDLE):
            logger.warning(f"Одна из сущностей уже в бою")
            return False
        
        # Создаем бой
        combat_id = f"combat_{attacker_id}_{target_id}_{random.randint(1000, 9999)}"
        combat = {
            "id": combat_id,
            "attacker_id": attacker_id,
            "target_id": target_id,
            "start_time": 0.0,
            "rounds": 0,
            "status": "active"
        }
        
        self.active_combats[combat_id] = combat
        
        # Обновляем состояния сущностей
        self.combat_entities[attacker_id]["combat_state"] = CombatState.PREPARING
        self.combat_entities[target_id]["combat_state"] = CombatState.PREPARING
        self.combat_entities[attacker_id]["current_target"] = target_id
        self.combat_entities[target_id]["current_target"] = attacker_id
        
        logger.info(f"Бой {combat_id} начался между {attacker_id} и {target_id}")
        return True
    
    def end_combat(self, combat_id: str):
        """Завершение боя"""
        if combat_id not in self.active_combats:
            return
        
        self._end_combat(combat_id)
    
    def _end_combat(self, combat_id: str):
        """Внутреннее завершение боя"""
        combat = self.active_combats[combat_id]
        attacker_id = combat["attacker_id"]
        target_id = combat["target_id"]
        
        # Сбрасываем состояния сущностей
        if attacker_id in self.combat_entities:
            self.combat_entities[attacker_id]["combat_state"] = CombatState.IDLE
            self.combat_entities[attacker_id]["current_target"] = None
        
        if target_id in self.combat_entities:
            self.combat_entities[target_id]["combat_state"] = CombatState.IDLE
            self.combat_entities[target_id]["current_target"] = None
        
        # Удаляем бой
        del self.active_combats[combat_id]
        
        logger.info(f"Бой {combat_id} завершен")
    
    def perform_attack(self, attacker_id: str, target_id: str, attack_type: AttackType = AttackType.MELEE) -> Optional[AttackResult]:
        """Выполнение атаки"""
        if attacker_id not in self.combat_entities or target_id not in self.combat_entities:
            logger.error(f"Одна из сущностей не зарегистрирована в системе боя")
            return None
        
        attacker = self.combat_entities[attacker_id]
        target = self.combat_entities[target_id]
        
        # Проверяем, может ли атакующий атаковать
        if not self._can_attack(attacker, target):
            return None
        
        # Создаем боевое действие
        action = CombatAction(
            attacker_id=attacker_id,
            target_id=target_id,
            action_type=attack_type,
            damage_type=self._get_damage_type(attack_type),
            base_damage=attacker["combat_stats"].attack,
            effects=self._get_attack_effects(attack_type)
        )
        
        # Выполняем атаку
        result = self._execute_attack(action, attacker, target)
        
        # Обновляем статистику
        if result.hit:
            attacker["total_damage_dealt"] += result.damage
            target["total_damage_taken"] += result.damage
        
        # Обновляем время последней атаки
        attacker["last_attack_time"] = 0.0  # Упрощенная реализация
        
        # Логируем атаку
        self._log_attack(action, result)
        
        return result
    
    def _can_attack(self, attacker: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Проверка возможности атаки"""
        # Проверяем состояние атакующего
        if attacker["combat_state"] == CombatState.STUNNED:
            return False
        
        # Проверяем, не оглушен ли атакующий
        if attacker["stunned_until"] > 0.0:
            return False
        
        # Проверяем состояние цели
        if target["combat_state"] == CombatState.IDLE:
            return False
        
        return True
    
    def _get_damage_type(self, attack_type: AttackType) -> DamageType:
        """Определение типа урона на основе типа атаки"""
        damage_type_map = {
            AttackType.MELEE: DamageType.PHYSICAL,
            AttackType.RANGED: DamageType.PHYSICAL,
            AttackType.MAGIC: DamageType.MAGICAL,
            AttackType.SPECIAL: DamageType.MAGICAL
        }
        
        return damage_type_map.get(attack_type, DamageType.PHYSICAL)
    
    def _get_attack_effects(self, attack_type: AttackType) -> List[str]:
        """Получение эффектов атаки"""
        effects_map = {
            AttackType.MELEE: ["bleeding"],
            AttackType.RANGED: ["piercing"],
            AttackType.MAGIC: ["burning", "freezing"],
            AttackType.SPECIAL: ["stunning", "poisoning"]
        }
        
        return effects_map.get(attack_type, [])
    
    def _execute_attack(self, action: CombatAction, attacker: Dict[str, Any], target: Dict[str, Any]) -> AttackResult:
        """Выполнение атаки"""
        result = AttackResult(damage_type=action.damage_type)
        
        # Проверяем уклонение
        if random.random() < target["combat_stats"].dodge_chance:
            result.dodged = True
            return result
        
        # Проверяем блок
        if random.random() < target["combat_stats"].block_chance:
            result.blocked = True
            result.damage = max(1, action.base_damage // 2)
            return result
        
        # Проверяем критический удар
        if random.random() < attacker["combat_stats"].critical_chance:
            result.critical = True
            result.damage = int(action.base_damage * attacker["combat_stats"].critical_multiplier)
        else:
            result.damage = action.base_damage
        
        # Применяем защиту цели
        defense_reduction = target["combat_stats"].defense
        result.damage = max(1, result.damage - defense_reduction)
        
        # Применяем сопротивление к типу урона
        resistance = target["combat_stats"].resistance.get(action.damage_type, 0.0)
        result.damage = int(result.damage * (1.0 - resistance))
        
        # Применяем эффекты
        for effect in action.effects:
            self._apply_effect(effect, target, result)
        
        result.hit = True
        return result
    
    def _apply_effect(self, effect: str, target: Dict[str, Any], result: AttackResult):
        """Применение эффекта атаки"""
        if effect == "stunning":
            # Оглушение на 2 секунды
            target["stunned_until"] = 2.0
            target["combat_state"] = CombatState.STUNNED
            result.effects.append("stunned")
        
        elif effect == "poisoning":
            # Отравление
            if "poisoned" not in target:
                target["poisoned"] = {"duration": 5.0, "damage_per_tick": 2}
            result.effects.append("poisoned")
        
        elif effect == "burning":
            # Горение
            if "burning" not in target:
                target["burning"] = {"duration": 3.0, "damage_per_tick": 3}
            result.effects.append("burning")
        
        elif effect == "freezing":
            # Заморозка
            if "frozen" not in target:
                target["frozen"] = {"duration": 2.0, "movement_penalty": 0.5}
            result.effects.append("frozen")
    
    def _log_attack(self, action: CombatAction, result: AttackResult):
        """Логирование атаки"""
        log_entry = {
            "timestamp": 0.0,  # Упрощенная реализация
            "attacker_id": action.attacker_id,
            "target_id": action.target_id,
            "action_type": action.action_type.value,
            "damage_type": action.damage_type.value,
            "base_damage": action.base_damage,
            "final_damage": result.damage,
            "hit": result.hit,
            "critical": result.critical,
            "blocked": result.blocked,
            "dodged": result.dodged,
            "effects": result.effects
        }
        
        self.combat_history.append(log_entry)
        
        # Ограничиваем историю
        if len(self.combat_history) > 1000:
            self.combat_history = self.combat_history[-1000:]
    
    def update_combat(self, delta_time: float):
        """Обновление системы боя"""
        # Обновляем кулдауны атак
        for entity_id in self.attack_cooldowns:
            self.attack_cooldowns[entity_id] = max(0.0, self.attack_cooldowns[entity_id] - delta_time)
        
        # Обновляем эффекты
        for entity_id, entity_data in self.combat_entities.items():
            self._update_entity_effects(entity_id, entity_data, delta_time)
        
        # Обновляем активные бои
        for combat_id in list(self.active_combats.keys()):
            combat = self.active_combats[combat_id]
            combat["start_time"] += delta_time
            combat["rounds"] += 1
            
            # Проверяем условия завершения боя
            if self._should_end_combat(combat):
                self._end_combat(combat_id)
    
    def _update_entity_effects(self, entity_id: str, entity_data: Dict[str, Any], delta_time: float):
        """Обновление эффектов сущности"""
        # Обновляем оглушение
        if entity_data["stunned_until"] > 0.0:
            entity_data["stunned_until"] = max(0.0, entity_data["stunned_until"] - delta_time)
            if entity_data["stunned_until"] <= 0.0:
                entity_data["combat_state"] = CombatState.IDLE
        
        # Обновляем отравление
        if "poisoned" in entity_data:
            poison = entity_data["poisoned"]
            poison["duration"] -= delta_time
            if poison["duration"] <= 0.0:
                del entity_data["poisoned"]
            else:
                # Наносим урон от отравления
                damage = poison["damage_per_tick"]
                entity_data["total_damage_taken"] += damage
        
        # Обновляем горение
        if "burning" in entity_data:
            burn = entity_data["burning"]
            burn["duration"] -= delta_time
            if burn["duration"] <= 0.0:
                del entity_data["burning"]
            else:
                # Наносим урон от горения
                damage = burn["damage_per_tick"]
                entity_data["total_damage_taken"] += damage
        
        # Обновляем заморозку
        if "frozen" in entity_data:
            freeze = entity_data["frozen"]
            freeze["duration"] -= delta_time
            if freeze["duration"] <= 0.0:
                del entity_data["frozen"]
    
    def _should_end_combat(self, combat: Dict[str, Any]) -> bool:
        """Проверка необходимости завершения боя"""
        # Бой длится слишком долго
        if combat["start_time"] > 60.0:  # 60 секунд
            return True
        
        # Одна из сущностей мертва или оглушена
        attacker_id = combat["attacker_id"]
        target_id = combat["target_id"]
        
        if (attacker_id not in self.combat_entities or 
            target_id not in self.combat_entities):
            return True
        
        attacker = self.combat_entities[attacker_id]
        target = self.combat_entities[target_id]
        
        # Проверяем здоровье (упрощенная реализация)
        if (attacker.get("health", 100) <= 0 or 
            target.get("health", 100) <= 0):
            return True
        
        return False
    
    def get_combat_info(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о боевой сущности"""
        if entity_id not in self.combat_entities:
            return None
        
        entity_data = self.combat_entities[entity_id]
        
        return {
            "id": entity_id,
            "combat_state": entity_data["combat_state"].value,
            "current_target": entity_data["current_target"],
            "combat_stats": {
                "attack": entity_data["combat_stats"].attack,
                "defense": entity_data["combat_stats"].defense,
                "critical_chance": entity_data["combat_stats"].critical_chance,
                "dodge_chance": entity_data["combat_stats"].dodge_chance,
                "block_chance": entity_data["combat_stats"].block_chance
            },
            "combat_record": {
                "wins": entity_data["combat_wins"],
                "losses": entity_data["combat_losses"],
                "damage_dealt": entity_data["total_damage_dealt"],
                "damage_taken": entity_data["total_damage_taken"]
            },
            "active_effects": self._get_active_effects(entity_data)
        }
    
    def _get_active_effects(self, entity_data: Dict[str, Any]) -> List[str]:
        """Получение активных эффектов"""
        effects = []
        
        if entity_data["stunned_until"] > 0.0:
            effects.append("stunned")
        if "poisoned" in entity_data:
            effects.append("poisoned")
        if "burning" in entity_data:
            effects.append("burning")
        if "frozen" in entity_data:
            effects.append("frozen")
        
        return effects
    
    def cleanup(self):
        """Очистка системы боя"""
        logger.info("Очистка системы боя...")
        self.combat_entities.clear()
        self.active_combats.clear()
        self.combat_history.clear()
        self.attack_cooldowns.clear()
