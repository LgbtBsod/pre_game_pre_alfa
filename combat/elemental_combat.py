"""
Продвинутая система боя с элементами
Поддерживает комбинации стихий, цепные реакции и сложные эффекты
"""
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import random
import math


class ElementType(Enum):
    """Типы элементов"""
    NONE = "none"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    WATER = "water"
    EARTH = "earth"
    WIND = "wind"
    DARK = "dark"
    LIGHT = "light"


class DamageType(Enum):
    """Типы урона"""
    PHYSICAL = "physical"
    MAGIC = "magic"
    ELEMENTAL = "elemental"
    TRUE = "true"


@dataclass
class ElementalInteraction:
    """Взаимодействие между элементами"""
    source_element: ElementType
    target_element: ElementType
    damage_multiplier: float
    additional_effects: List[str]
    chance: float
    description: str


@dataclass
class ElementalCombo:
    """Комбинация элементов"""
    id: str
    name: str
    description: str
    elements: List[ElementType]
    effects: List[str]
    damage_multiplier: float
    duration: float
    chance: float
    requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CombatResult:
    """Результат боевого действия"""
    damage_dealt: float
    damage_type: DamageType
    element: ElementType
    critical: bool
    effects_applied: List[str]
    elemental_reactions: List[str]
    combo_triggered: Optional[str] = None
    chain_reactions: List[str] = field(default_factory=list)


class ElementalCombatSystem:
    """Система элементарного боя"""
    
    def __init__(self):
        self.elemental_interactions: Dict[Tuple[ElementType, ElementType], ElementalInteraction] = {}
        self.elemental_combos: Dict[str, ElementalCombo] = {}
        self.active_combos: Dict[str, Dict[str, Any]] = {}
        self.chain_reaction_history: List[str] = []
        
        self._initialize_elemental_interactions()
        self._initialize_elemental_combos()
    
    def _initialize_elemental_interactions(self):
        """Инициализация взаимодействий между элементами"""
        
        # Огонь + Лед = Пар
        self.elemental_interactions[(ElementType.FIRE, ElementType.ICE)] = ElementalInteraction(
            source_element=ElementType.FIRE,
            target_element=ElementType.ICE,
            damage_multiplier=1.5,
            additional_effects=["steam", "blind"],
            chance=0.4,
            description="Огонь и лед создают обжигающий пар"
        )
        
        # Огонь + Вода = Пар
        self.elemental_interactions[(ElementType.FIRE, ElementType.WATER)] = ElementalInteraction(
            source_element=ElementType.FIRE,
            target_element=ElementType.WATER,
            damage_multiplier=1.3,
            additional_effects=["steam", "slow"],
            chance=0.6,
            description="Огонь испаряет воду, создавая пар"
        )
        
        # Молния + Вода = Электропроводность
        self.elemental_interactions[(ElementType.LIGHTNING, ElementType.WATER)] = ElementalInteraction(
            source_element=ElementType.LIGHTNING,
            target_element=ElementType.WATER,
            damage_multiplier=2.0,
            additional_effects=["stun", "chain_damage"],
            chance=0.8,
            description="Вода проводит электричество"
        )
        
        # Молния + Лед = Электрошок
        self.elemental_interactions[(ElementType.LIGHTNING, ElementType.ICE)] = ElementalInteraction(
            source_element=ElementType.LIGHTNING,
            target_element=ElementType.ICE,
            damage_multiplier=1.7,
            additional_effects=["stun", "ice_break"],
            chance=0.5,
            description="Молния разрушает лед"
        )
        
        # Земля + Огонь = Лава
        self.elemental_interactions[(ElementType.EARTH, ElementType.FIRE)] = ElementalInteraction(
            source_element=ElementType.EARTH,
            target_element=ElementType.FIRE,
            damage_multiplier=1.4,
            additional_effects=["burn", "armor_break"],
            chance=0.3,
            description="Земля и огонь создают лаву"
        )
        
        # Ветер + Огонь = Огненная буря
        self.elemental_interactions[(ElementType.WIND, ElementType.FIRE)] = ElementalInteraction(
            source_element=ElementType.WIND,
            target_element=ElementType.FIRE,
            damage_multiplier=1.6,
            additional_effects=["burn", "area_damage"],
            chance=0.4,
            description="Ветер раздувает огонь"
        )
        
        # Свет + Тьма = Взрыв
        self.elemental_interactions[(ElementType.LIGHT, ElementType.DARK)] = ElementalInteraction(
            source_element=ElementType.LIGHT,
            target_element=ElementType.DARK,
            damage_multiplier=2.5,
            additional_effects=["explosion", "stun", "area_damage"],
            chance=0.2,
            description="Свет и тьма создают мощный взрыв"
        )
    
    def _initialize_elemental_combos(self):
        """Инициализация комбинаций элементов"""
        
        # Тройная комбинация: Огонь + Молния + Вода
        self.elemental_combos["fire_lightning_water"] = ElementalCombo(
            id="fire_lightning_water",
            name="Электрическая буря",
            description="Комбинация огня, молнии и воды создает мощную электрическую бурю",
            elements=[ElementType.FIRE, ElementType.LIGHTNING, ElementType.WATER],
            effects=["stun", "chain_damage", "burn", "area_damage"],
            damage_multiplier=2.5,
            duration=8.0,
            chance=0.15,
            requirements={"min_level": 10, "mana_cost": 50}
        )
        
        # Двойная комбинация: Лед + Ветер
        self.elemental_combos["ice_wind"] = ElementalCombo(
            id="ice_wind",
            name="Ледяная буря",
            description="Лед и ветер создают ледяную бурю",
            elements=[ElementType.ICE, ElementType.WIND],
            effects=["freeze", "slow", "area_damage"],
            damage_multiplier=1.8,
            duration=6.0,
            chance=0.25,
            requirements={"min_level": 5, "mana_cost": 30}
        )
        
        # Четверная комбинация: Все элементы
        self.elemental_combos["all_elements"] = ElementalCombo(
            id="all_elements",
            name="Хаос стихий",
            description="Все элементы вместе создают хаотический взрыв",
            elements=[ElementType.FIRE, ElementType.ICE, ElementType.LIGHTNING, ElementType.WATER, ElementType.EARTH],
            effects=["explosion", "stun", "area_damage", "elemental_chaos"],
            damage_multiplier=4.0,
            duration=10.0,
            chance=0.05,
            requirements={"min_level": 20, "mana_cost": 100, "special_item": "chaos_crystal"}
        )
    
    def calculate_damage(self, base_damage: float, attacker_element: ElementType, 
                        target_element: ElementType, target_resistances: Dict[ElementType, float]) -> CombatResult:
        """Расчет урона с учетом элементов"""
        
        # Базовый урон
        final_damage = base_damage
        damage_type = DamageType.PHYSICAL if attacker_element == ElementType.NONE else DamageType.ELEMENTAL
        
        # Проверка критического удара
        critical = random.random() < 0.1  # 10% шанс крита
        
        if critical:
            final_damage *= 1.5
        
        # Применение сопротивлений
        if attacker_element != ElementType.NONE:
            resistance = target_resistances.get(attacker_element, 0.0)
            final_damage *= (1.0 - resistance)
        
        # Проверка элементарных взаимодействий
        interaction = self.elemental_interactions.get((attacker_element, target_element))
        effects_applied = []
        elemental_reactions = []
        
        if interaction and random.random() < interaction.chance:
            final_damage *= interaction.damage_multiplier
            effects_applied.extend(interaction.additional_effects)
            elemental_reactions.append(interaction.description)
        
        # Проверка комбинаций элементов
        combo_triggered = self._check_elemental_combos(attacker_element, target_element)
        if combo_triggered:
            combo = self.elemental_combos[combo_triggered]
            final_damage *= combo.damage_multiplier
            effects_applied.extend(combo.effects)
            elemental_reactions.append(f"Комбинация: {combo.name}")
        
        return CombatResult(
            damage_dealt=max(0, final_damage),
            damage_type=damage_type,
            element=attacker_element,
            critical=critical,
            effects_applied=effects_applied,
            elemental_reactions=elemental_reactions,
            combo_triggered=combo_triggered
        )
    
    def _check_elemental_combos(self, source_element: ElementType, target_element: ElementType) -> Optional[str]:
        """Проверка возможности комбинации элементов"""
        
        for combo_id, combo in self.elemental_combos.items():
            if combo_id in self.active_combos:
                continue  # Комбинация уже активна
            
            # Проверяем, есть ли элементы комбинации в активных эффектах
            if self._can_trigger_combo(combo, source_element, target_element):
                if random.random() < combo.chance:
                    self.active_combos[combo_id] = {
                        "start_time": 0.0,  # Время начала
                        "duration": combo.duration,
                        "effects": combo.effects.copy()
                    }
                    return combo_id
        
        return None
    
    def _can_trigger_combo(self, combo: ElementalCombo, source_element: ElementType, 
                          target_element: ElementType) -> bool:
        """Проверка возможности активации комбинации"""
        
        # Простая логика: если у нас есть хотя бы 2 элемента из комбинации
        available_elements = {source_element, target_element}
        required_elements = set(combo.elements)
        
        return len(available_elements.intersection(required_elements)) >= 2
    
    def apply_elemental_effects(self, target, effects: List[str], duration: float):
        """Применение элементарных эффектов к цели"""
        
        for effect_name in effects:
            effect_data = self._get_effect_data(effect_name)
            if effect_data:
                self._apply_single_effect(target, effect_data, duration)
    
    def _get_effect_data(self, effect_name: str) -> Optional[Dict[str, Any]]:
        """Получение данных эффекта"""
        
        effect_database = {
            "stun": {
                "type": "control",
                "modifiers": {"can_move": False, "can_attack": False, "can_cast": False},
                "visual_effect": "stun_aura"
            },
            "burn": {
                "type": "damage_over_time",
                "modifiers": {"fire_damage_per_tick": 5.0},
                "visual_effect": "fire_particles"
            },
            "freeze": {
                "type": "control",
                "modifiers": {"can_move": False, "can_attack": False, "can_cast": False},
                "visual_effect": "ice_crystal"
            },
            "slow": {
                "type": "movement",
                "modifiers": {"movement_speed": -0.3, "attack_speed": -0.2},
                "visual_effect": "slow_aura"
            },
            "chain_damage": {
                "type": "special",
                "modifiers": {"chain_radius": 3.0, "chain_damage": 0.7},
                "visual_effect": "lightning_chain"
            },
            "area_damage": {
                "type": "area",
                "modifiers": {"area_radius": 4.0, "damage_falloff": 0.8},
                "visual_effect": "explosion"
            }
        }
        
        return effect_database.get(effect_name)
    
    def _apply_single_effect(self, target, effect_data: Dict[str, Any], duration: float):
        """Применение одного эффекта к цели"""
        
        # Здесь должна быть логика применения эффекта к конкретной цели
        # Это зависит от структуры класса цели
        pass
    
    def process_chain_reactions(self, initial_target, initial_effect: str) -> List[str]:
        """Обработка цепных реакций"""
        
        chain_reactions = []
        processed_targets = {initial_target}
        targets_to_process = [(initial_target, initial_effect, 0)]
        
        while targets_to_process:
            current_target, current_effect, chain_level = targets_to_process.pop(0)
            
            if chain_level >= 3:  # Максимум 3 уровня цепной реакции
                continue
            
            # Поиск ближайших целей для цепной реакции
            nearby_targets = self._find_nearby_targets(current_target, radius=3.0)
            
            for nearby_target in nearby_targets:
                if nearby_target in processed_targets:
                    continue
                
                # Проверка возможности цепной реакции
                if self._can_chain_react(current_effect, nearby_target):
                    chain_reactions.append(f"Цепная реакция {chain_level + 1}: {current_effect} -> {nearby_target}")
                    processed_targets.add(nearby_target)
                    targets_to_process.append((nearby_target, current_effect, chain_level + 1))
        
        return chain_reactions
    
    def _find_nearby_targets(self, source_target, radius: float) -> List:
        """Поиск ближайших целей"""
        
        # Здесь должна быть логика поиска целей в радиусе
        # Это зависит от структуры игры
        return []
    
    def _can_chain_react(self, effect: str, target) -> bool:
        """Проверка возможности цепной реакции"""
        
        # Простая логика: некоторые эффекты могут передаваться
        chainable_effects = {"burn", "poison", "lightning", "ice"}
        return effect in chainable_effects
    
    def update_active_combos(self, current_time: float):
        """Обновление активных комбинаций"""
        
        expired_combos = []
        
        for combo_id, combo_data in self.active_combos.items():
            if current_time - combo_data["start_time"] >= combo_data["duration"]:
                expired_combos.append(combo_id)
        
        for combo_id in expired_combos:
            del self.active_combos[combo_id]
    
    def get_elemental_bonus(self, element: ElementType, target_resistances: Dict[ElementType, float]) -> float:
        """Получение бонуса к урону от элемента"""
        
        if element == ElementType.NONE:
            return 1.0
        
        resistance = target_resistances.get(element, 0.0)
        if resistance > 0:
            return 0.5  # Сопротивление уменьшает урон
        elif resistance < 0:
            return 1.5  # Уязвимость увеличивает урон
        else:
            return 1.0  # Нейтрально
    
    def calculate_elemental_synergy(self, elements: List[ElementType]) -> float:
        """Расчет синергии между элементами"""
        
        if len(elements) < 2:
            return 1.0
        
        synergy_bonus = 1.0
        
        # Проверка синергетических пар
        synergistic_pairs = [
            (ElementType.FIRE, ElementType.LIGHTNING),
            (ElementType.ICE, ElementType.WATER),
            (ElementType.EARTH, ElementType.WIND),
            (ElementType.LIGHT, ElementType.DARK)
        ]
        
        for pair in synergistic_pairs:
            if all(elem in elements for elem in pair):
                synergy_bonus += 0.2
        
        # Бонус за количество элементов
        synergy_bonus += (len(elements) - 1) * 0.1
        
        return min(synergy_bonus, 2.0)  # Максимум 2x бонус


# Глобальный экземпляр системы
elemental_combat_system = ElementalCombatSystem()
