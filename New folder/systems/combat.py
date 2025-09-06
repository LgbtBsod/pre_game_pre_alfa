#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import random
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

class AttackType(Enum):
    """Типы атак"""
    NORMAL = "normal"           # Обычная атака
    HEAVY = "heavy"             # Тяжелая атака
    QUICK = "quick"             # Быстрая атака
    SPECIAL = "special"         # Специальная атака
    COMBO = "combo"             # Комбо атака
    COUNTER = "counter"         # Контратака
    AOE = "aoe"                # Атака по области
    RANGED = "ranged"          # Дальняя атака

class DamageType(Enum):
    """Типы урона"""
    PHYSICAL = "physical"       # Физический урон
    MAGICAL = "magical"         # Магический урон
    FIRE = "fire"              # Огненный урон
    ICE = "ice"                # Ледяной урон
    LIGHTNING = "lightning"    # Электрический урон
    POISON = "poison"          # Ядовитый урон
    HOLY = "holy"              # Священный урон
    DARK = "dark"              # Темный урон

class CombatState(Enum):
    """Состояния в бою"""
    IDLE = "idle"              # Ожидание
    ATTACKING = "attacking"    # Атака
    DEFENDING = "defending"    # Защита
    DODGING = "dodging"        # Уклонение
    STUNNED = "stunned"        # Оглушен
    CHARGING = "charging"     # Зарядка
    COOLDOWN = "cooldown"     # Перезарядка

@dataclass
class Attack:
    """Атака"""
    attack_id: str
    name: str
    description: str
    attack_type: AttackType
    damage_type: DamageType
    base_damage: float
    damage_multiplier: float = 1.0
    accuracy: float = 0.9      # Точность атаки
    critical_chance: float = 0.05
    critical_multiplier: float = 2.0
    range: float = 1.0         # Дальность атаки
    cooldown: float = 0.0      # Время перезарядки
    stamina_cost: float = 0.0
    mana_cost: float = 0.0
    health_cost: float = 0.0
    combo_points: int = 0      # Очки комбо
    combo_requirement: int = 0 # Требуемые очки комбо
    effects: List[str] = field(default_factory=list)  # Эффекты атаки
    animation_duration: float = 0.5
    last_used: float = 0.0

@dataclass
class Combo:
    """Комбо атака"""
    combo_id: str
    name: str
    description: str
    attacks: List[str]         # Последовательность атак
    damage_bonus: float = 0.0  # Бонус к урону
    effects: List[str] = field(default_factory=list)
    unlock_requirement: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CombatStats:
    """Боевые характеристики"""
    attack_power: float = 0.0
    defense: float = 0.0
    magic_resistance: float = 0.0
    accuracy: float = 0.9
    dodge_chance: float = 0.05
    critical_chance: float = 0.05
    critical_damage: float = 2.0
    attack_speed: float = 1.0
    range: float = 1.0
    combo_multiplier: float = 1.0

class CombatSystem:
    """Продвинутая боевая система"""
    
    def __init__(self):
        self.entity_combat: Dict[str, Dict[str, Any]] = {}
        self.attack_templates: Dict[str, Attack] = {}
        self.combo_templates: Dict[str, Combo] = {}
        self.active_combats: Dict[str, Dict[str, Any]] = {}
        
        # Инициализация шаблонов атак
        self._initialize_attack_templates()
        # Инициализация комбо
        self._initialize_combo_templates()
    
    def _initialize_attack_templates(self):
        """Инициализация шаблонов атак"""
        # Обычные атаки
        basic_attack = Attack(
            attack_id="basic_attack",
            name="Basic Attack",
            description="Базовая атака",
            attack_type=AttackType.NORMAL,
            damage_type=DamageType.PHYSICAL,
            base_damage=20.0,
            accuracy=0.9,
            critical_chance=0.05,
            range=1.0,
            cooldown=0.0,
            stamina_cost=5.0,
            combo_points=1
        )
        self.attack_templates["basic_attack"] = basic_attack
        
        heavy_attack = Attack(
            attack_id="heavy_attack",
            name="Heavy Attack",
            description="Мощная атака с высоким уроном",
            attack_type=AttackType.HEAVY,
            damage_type=DamageType.PHYSICAL,
            base_damage=40.0,
            damage_multiplier=1.5,
            accuracy=0.7,
            critical_chance=0.15,
            critical_multiplier=2.5,
            range=1.0,
            cooldown=2.0,
            stamina_cost=20.0,
            combo_points=2
        )
        self.attack_templates["heavy_attack"] = heavy_attack
        
        quick_attack = Attack(
            attack_id="quick_attack",
            name="Quick Attack",
            description="Быстрая атака с низким уроном",
            attack_type=AttackType.QUICK,
            damage_type=DamageType.PHYSICAL,
            base_damage=10.0,
            damage_multiplier=0.7,
            accuracy=0.95,
            critical_chance=0.02,
            range=1.0,
            cooldown=0.5,
            stamina_cost=2.0,
            combo_points=1
        )
        self.attack_templates["quick_attack"] = quick_attack
        
        # Магические атаки
        fireball = Attack(
            attack_id="fireball",
            name="Fireball",
            description="Огненный шар",
            attack_type=AttackType.RANGED,
            damage_type=DamageType.FIRE,
            base_damage=30.0,
            damage_multiplier=1.2,
            accuracy=0.8,
            critical_chance=0.1,
            range=5.0,
            cooldown=3.0,
            mana_cost=25.0,
            effects=["burn"],
            combo_points=3
        )
        self.attack_templates["fireball"] = fireball
        
        ice_shard = Attack(
            attack_id="ice_shard",
            name="Ice Shard",
            description="Ледяной осколок",
            attack_type=AttackType.RANGED,
            damage_type=DamageType.ICE,
            base_damage=25.0,
            accuracy=0.85,
            critical_chance=0.08,
            range=4.0,
            cooldown=2.5,
            mana_cost=20.0,
            effects=["freeze"],
            combo_points=2
        )
        self.attack_templates["ice_shard"] = ice_shard
        
        lightning_bolt = Attack(
            attack_id="lightning_bolt",
            name="Lightning Bolt",
            description="Удар молнии",
            attack_type=AttackType.RANGED,
            damage_type=DamageType.LIGHTNING,
            base_damage=35.0,
            damage_multiplier=1.3,
            accuracy=0.75,
            critical_chance=0.2,
            critical_multiplier=3.0,
            range=6.0,
            cooldown=4.0,
            mana_cost=30.0,
            effects=["stun"],
            combo_points=4
        )
        self.attack_templates["lightning_bolt"] = lightning_bolt
        
        # Специальные атаки
        whirlwind = Attack(
            attack_id="whirlwind",
            name="Whirlwind",
            description="Вихрь атак",
            attack_type=AttackType.AOE,
            damage_type=DamageType.PHYSICAL,
            base_damage=15.0,
            damage_multiplier=0.8,
            accuracy=0.7,
            critical_chance=0.05,
            range=3.0,
            cooldown=8.0,
            stamina_cost=40.0,
            combo_requirement=5,
            combo_points=5
        )
        self.attack_templates["whirlwind"] = whirlwind
        
        counter_strike = Attack(
            attack_id="counter_strike",
            name="Counter Strike",
            description="Контратака",
            attack_type=AttackType.COUNTER,
            damage_type=DamageType.PHYSICAL,
            base_damage=50.0,
            damage_multiplier=2.0,
            accuracy=0.9,
            critical_chance=0.25,
            critical_multiplier=3.0,
            range=1.0,
            cooldown=5.0,
            stamina_cost=30.0,
            combo_requirement=3,
            combo_points=3
        )
        self.attack_templates["counter_strike"] = counter_strike
    
    def _initialize_combo_templates(self):
        """Инициализация комбо атак"""
        # Простое комбо
        basic_combo = Combo(
            combo_id="basic_combo",
            name="Basic Combo",
            description="Простая комбинация атак",
            attacks=["basic_attack", "quick_attack", "basic_attack"],
            damage_bonus=0.2
        )
        self.combo_templates["basic_combo"] = basic_combo
        
        # Мощное комбо
        power_combo = Combo(
            combo_id="power_combo",
            name="Power Combo",
            description="Мощная комбинация",
            attacks=["heavy_attack", "basic_attack", "heavy_attack"],
            damage_bonus=0.5,
            effects=["stun"],
            unlock_requirement={"level": 10}
        )
        self.combo_templates["power_combo"] = power_combo
        
        # Магическое комбо
        magic_combo = Combo(
            combo_id="magic_combo",
            name="Magic Combo",
            description="Магическая комбинация",
            attacks=["fireball", "ice_shard", "lightning_bolt"],
            damage_bonus=0.8,
            effects=["burn", "freeze", "stun"],
            unlock_requirement={"level": 15, "intelligence": 20}
        )
        self.combo_templates["magic_combo"] = magic_combo
    
    def initialize_entity_combat(self, entity_id: str):
        """Инициализация боевой системы для сущности"""
        self.entity_combat[entity_id] = {
            'combat_stats': CombatStats(),
            'attacks': {},
            'combos': {},
            'combo_points': 0,
            'max_combo_points': 10,
            'combat_state': CombatState.IDLE,
            'last_attack_time': 0.0,
            'attack_chain': [],
            'defense_bonus': 0.0,
            'dodge_bonus': 0.0
        }
        
        # Копируем атаки
        for attack_id, template in self.attack_templates.items():
            attack = Attack(
                attack_id=template.attack_id,
                name=template.name,
                description=template.description,
                attack_type=template.attack_type,
                damage_type=template.damage_type,
                base_damage=template.base_damage,
                damage_multiplier=template.damage_multiplier,
                accuracy=template.accuracy,
                critical_chance=template.critical_chance,
                critical_multiplier=template.critical_multiplier,
                range=template.range,
                cooldown=template.cooldown,
                stamina_cost=template.stamina_cost,
                mana_cost=template.mana_cost,
                health_cost=template.health_cost,
                combo_points=template.combo_points,
                combo_requirement=template.combo_requirement,
                effects=template.effects.copy(),
                animation_duration=template.animation_duration
            )
            self.entity_combat[entity_id]['attacks'][attack_id] = attack
        
        # Копируем комбо
        for combo_id, template in self.combo_templates.items():
            combo = Combo(
                combo_id=template.combo_id,
                name=template.name,
                description=template.description,
                attacks=template.attacks.copy(),
                damage_bonus=template.damage_bonus,
                effects=template.effects.copy(),
                unlock_requirement=template.unlock_requirement.copy()
            )
            self.entity_combat[entity_id]['combos'][combo_id] = combo
    
    def perform_attack(self, attacker_id: str, target_id: str, attack_id: str, 
                      attacker_stats: Dict[str, Any], target_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение атаки"""
        if attacker_id not in self.entity_combat or attack_id not in self.entity_combat[attacker_id]['attacks']:
            return {'success': False, 'message': 'Attack not available'}
        
        combat_data = self.entity_combat[attacker_id]
        attack = combat_data['attacks'][attack_id]
        
        # Проверяем перезарядку
        current_time = time.time()
        if current_time - attack.last_used < attack.cooldown:
            return {'success': False, 'message': 'Attack on cooldown'}
        
        # Проверяем ресурсы
        if not self._check_resources(attacker_id, attack):
            return {'success': False, 'message': 'Insufficient resources'}
        
        # Проверяем требования комбо
        if attack.combo_requirement > 0 and combat_data['combo_points'] < attack.combo_requirement:
            return {'success': False, 'message': 'Insufficient combo points'}
        
        # Выполняем атаку
        result = self._execute_attack(attacker_id, target_id, attack, attacker_stats, target_stats)
        
        # Обновляем состояние
        attack.last_used = current_time
        combat_data['last_attack_time'] = current_time
        combat_data['attack_chain'].append(attack_id)
        
        # Добавляем очки комбо
        combat_data['combo_points'] = min(combat_data['max_combo_points'], 
                                        combat_data['combo_points'] + attack.combo_points)
        
        # Проверяем комбо
        self._check_combo(attacker_id, target_id, attacker_stats, target_stats)
        
        return result
    
    def _check_resources(self, entity_id: str, attack: Attack) -> bool:
        """Проверка ресурсов для атаки"""
        # Здесь должна быть проверка ресурсов сущности
        # Пока возвращаем True
        return True
    
    def _execute_attack(self, attacker_id: str, target_id: str, attack: Attack,
                       attacker_stats: Dict[str, Any], target_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение атаки"""
        # Рассчитываем урон
        base_damage = attack.base_damage * attack.damage_multiplier
        
        # Применяем боевые характеристики
        attack_power = attacker_stats.get('physical_damage', 0) if attack.damage_type == DamageType.PHYSICAL else attacker_stats.get('magical_damage', 0)
        base_damage += attack_power
        
        # Проверяем точность
        accuracy = attack.accuracy + attacker_stats.get('accuracy', 0.9) - 0.9
        if random.random() > accuracy:
            return {'success': True, 'hit': False, 'message': 'Attack missed'}
        
        # Проверяем уклонение
        dodge_chance = target_stats.get('dodge_chance', 0.05)
        if random.random() < dodge_chance:
            return {'success': True, 'hit': False, 'message': 'Attack dodged'}
        
        # Проверяем критический удар
        critical_chance = attack.critical_chance + attacker_stats.get('critical_chance', 0.05)
        is_critical = random.random() < critical_chance
        
        if is_critical:
            critical_multiplier = attack.critical_multiplier + attacker_stats.get('critical_damage', 2.0) - 2.0
            base_damage *= critical_multiplier
        
        # Применяем защиту
        defense = target_stats.get('defense', 0)
        if attack.damage_type == DamageType.PHYSICAL:
            final_damage = max(1, base_damage - defense)
        else:
            magic_resistance = target_stats.get('magic_resistance', 0)
            final_damage = max(1, base_damage * (1 - magic_resistance / 100))
        
        # Применяем бонус комбо
        combo_bonus = self.entity_combat[attacker_id]['combo_points'] * 0.1
        final_damage *= (1 + combo_bonus)
        
        return {
            'success': True,
            'hit': True,
            'damage': final_damage,
            'critical': is_critical,
            'damage_type': attack.damage_type.value,
            'effects': attack.effects,
            'combo_points_gained': attack.combo_points
        }
    
    def _check_combo(self, attacker_id: str, target_id: str, 
                    attacker_stats: Dict[str, Any], target_stats: Dict[str, Any]):
        """Проверка и выполнение комбо"""
        combat_data = self.entity_combat[attacker_id]
        attack_chain = combat_data['attack_chain']
        
        for combo_id, combo in combat_data['combos'].items():
            if len(attack_chain) >= len(combo.attacks):
                recent_attacks = attack_chain[-len(combo.attacks):]
                if recent_attacks == combo.attacks:
                    # Выполняем комбо
                    self._execute_combo(attacker_id, target_id, combo, attacker_stats, target_stats)
                    # Очищаем цепочку атак
                    combat_data['attack_chain'] = []
                    break
    
    def _execute_combo(self, attacker_id: str, target_id: str, combo: Combo,
                      attacker_stats: Dict[str, Any], target_stats: Dict[str, Any]):
        """Выполнение комбо атаки"""
        # Рассчитываем урон комбо
        base_damage = 30.0  # Базовый урон комбо
        damage_bonus = combo.damage_bonus
        
        # Применяем характеристики атакующего
        attack_power = attacker_stats.get('physical_damage', 0) + attacker_stats.get('magical_damage', 0)
        final_damage = (base_damage + attack_power) * (1 + damage_bonus)
        
        # Применяем защиту цели
        defense = target_stats.get('defense', 0)
        magic_resistance = target_stats.get('magic_resistance', 0)
        final_damage = max(1, final_damage - defense) * (1 - magic_resistance / 100)
        
        # Тратим очки комбо
        self.entity_combat[attacker_id]['combo_points'] = 0
        
        print(f"Combo executed: {combo.name} for {final_damage:.1f} damage!")
    
    def start_defense(self, entity_id: str):
        """Начало защиты"""
        if entity_id not in self.entity_combat:
            return False
        
        self.entity_combat[entity_id]['combat_state'] = CombatState.DEFENDING
        self.entity_combat[entity_id]['defense_bonus'] = 0.5
        return True
    
    def end_defense(self, entity_id: str):
        """Конец защиты"""
        if entity_id not in self.entity_combat:
            return False
        
        self.entity_combat[entity_id]['combat_state'] = CombatState.IDLE
        self.entity_combat[entity_id]['defense_bonus'] = 0.0
        return True
    
    def start_dodge(self, entity_id: str):
        """Начало уклонения"""
        if entity_id not in self.entity_combat:
            return False
        
        self.entity_combat[entity_id]['combat_state'] = CombatState.DODGING
        self.entity_combat[entity_id]['dodge_bonus'] = 0.3
        return True
    
    def end_dodge(self, entity_id: str):
        """Конец уклонения"""
        if entity_id not in self.entity_combat:
            return False
        
        self.entity_combat[entity_id]['combat_state'] = CombatState.IDLE
        self.entity_combat[entity_id]['dodge_bonus'] = 0.0
        return True
    
    def get_combat_stats(self, entity_id: str) -> Dict[str, Any]:
        """Получение боевых характеристик"""
        if entity_id not in self.entity_combat:
            return {}
        
        combat_data = self.entity_combat[entity_id]
        return {
            'combat_state': combat_data['combat_state'].value,
            'combo_points': combat_data['combo_points'],
            'max_combo_points': combat_data['max_combo_points'],
            'attack_chain': combat_data['attack_chain'],
            'defense_bonus': combat_data['defense_bonus'],
            'dodge_bonus': combat_data['dodge_bonus']
        }
    
    def get_available_attacks(self, entity_id: str) -> List[Attack]:
        """Получение доступных атак"""
        if entity_id not in self.entity_combat:
            return []
        
        current_time = time.time()
        available = []
        
        for attack in self.entity_combat[entity_id]['attacks'].values():
            if current_time - attack.last_used >= attack.cooldown:
                available.append(attack)
        
        return available
    
    def get_available_combos(self, entity_id: str) -> List[Combo]:
        """Получение доступных комбо"""
        if entity_id not in self.entity_combat:
            return []
        
        available = []
        combat_data = self.entity_combat[entity_id]
        
        for combo in combat_data['combos'].values():
            # Проверяем требования разблокировки
            can_use = True
            for req_type, req_value in combo.unlock_requirement.items():
                # Здесь должна быть проверка требований
                pass
            
            if can_use:
                available.append(combo)
        
        return available
    
    def reset_combo_points(self, entity_id: str):
        """Сброс очков комбо"""
        if entity_id in self.entity_combat:
            self.entity_combat[entity_id]['combo_points'] = 0
            self.entity_combat[entity_id]['attack_chain'] = []
    
    def decay_combo_points(self, entity_id: str, dt: float):
        """Уменьшение очков комбо со временем"""
        if entity_id in self.entity_combat:
            combat_data = self.entity_combat[entity_id]
            decay_rate = 2.0  # Очки в секунду
            
            combat_data['combo_points'] = max(0, combat_data['combo_points'] - decay_rate * dt)
            
            # Если очки комбо упали до 0, очищаем цепочку атак
            if combat_data['combo_points'] <= 0:
                combat_data['attack_chain'] = []
