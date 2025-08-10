"""
Обновленная система Entity с использованием кортежей данных
Вместо парсинга по имени используются структурированные данные
"""
import random
import math
import time
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from ai.memory import LearningController
from .effect import Effect
from core.data_types import data_manager, AttributeData, EffectData, ItemData, EntityData, DataType


class DamageType(Enum):
    PHYSICAL = "physical"
    MAGIC = "magic"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"


class CombatStyle(Enum):
    MELEE = "melee"
    RANGED = "ranged"
    MAGIC = "magic"


@dataclass
class AttributeTuple:
    """Кортеж атрибута: (текущее_значение, максимальное_значение, скорость_роста)"""
    current: float
    maximum: float
    growth: float
    
    def increase(self, amount: float = 1.0) -> bool:
        """Увеличить атрибут"""
        if self.current < self.maximum:
            self.current = min(self.current + amount, self.maximum)
            return True
        return False
    
    def set_base(self, value: float) -> None:
        """Установить базовое значение"""
        self.current = max(0, min(value, self.maximum))
    
    def set_max(self, value: float) -> None:
        """Установить максимальное значение"""
        self.maximum = max(0, value)
        self.current = min(self.current, self.maximum)


class Entity:
    def __init__(self, entity_id: str, entity_type: str, position: Tuple[float, float] = (0, 0)):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.position = list(position)
        self.alive = True
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        
        # Загружаем данные сущности из менеджера данных
        entity_data = data_manager.get_entity(entity_id)
        if entity_data:
            self._init_from_data(entity_data)
        else:
            self._init_default()
        
        # Система обучения
        self.learning_rate = 0.1
        self.learning_system = LearningController(self)
        self.memory = {}
        self.known_weaknesses = []
        
        # Активные эффекты и кулдауны умений
        self.active_effects: Dict[str, Effect] = {}
        self.skill_cooldowns: Dict[str, float] = {}
        
        # Боевые параметры
        self.attack_cooldown = 0
        self.last_attacker = None
        self.is_boss = False
        self.combat_style = CombatStyle.MELEE
        
        # Ссылки на других сущностей
        self.target = None
        self.owner = None
        self.minions = []
        
        # Обновляем производные характеристики
        self.update_derived_stats()
    
    def _init_from_data(self, entity_data: EntityData):
        """Инициализация из данных сущности"""
        self.name = entity_data.name
        self.description = entity_data.description
        self.level = entity_data.level
        self.experience = entity_data.experience
        self.experience_to_next = entity_data.experience_to_next
        
        # Инициализируем атрибуты из данных
        self.attributes = {}
        for attr_id, value in entity_data.attributes.items():
            attr_data = data_manager.get_attribute(attr_id)
            if attr_data:
                self.attributes[attr_id] = AttributeTuple(
                    current=value,
                    maximum=attr_data.max_value,
                    growth=attr_data.growth_rate
                )
        
        # Инициализируем боевые характеристики
        self.combat_stats = entity_data.combat_stats.copy()
        
        # Экипировка и инвентарь
        self.equipment = {slot: None for slot in entity_data.equipment_slots}
        self.inventory = []
        self.max_inventory_size = entity_data.inventory_size
        
        # Навыки
        self.skills = entity_data.skills.copy()
        
        # Дополнительные параметры для врагов
        if entity_data.type == "enemy":
            self.enemy_type = entity_data.enemy_type
            self.experience_reward = entity_data.experience_reward
            self.ai_behavior = entity_data.ai_behavior
            self.loot_table = entity_data.loot_table
            self.phases = entity_data.phases or []
        
        # Очки атрибутов
        self.attribute_points = 0
    
    def _init_default(self):
        """Инициализация по умолчанию"""
        self.name = "Unknown Entity"
        self.description = "Default entity"
        
        # Атрибуты по умолчанию
        self.attributes = {
            "str_001": AttributeTuple(10.0, 100.0, 1.0),
            "dex_001": AttributeTuple(10.0, 100.0, 1.0),
            "int_001": AttributeTuple(10.0, 100.0, 1.0),
            "vit_001": AttributeTuple(10.0, 100.0, 1.0),
            "end_001": AttributeTuple(10.0, 100.0, 1.0),
            "fai_001": AttributeTuple(10.0, 100.0, 1.0),
            "luc_001": AttributeTuple(10.0, 100.0, 1.0),
        }
        
        # Боевые характеристики по умолчанию
        self.combat_stats = {
            "health": 100.0,
            "max_health": 100.0,
            "mana": 50.0,
            "max_mana": 50.0,
            "stamina": 100.0,
            "max_stamina": 100.0,
            "damage_output": 10.0,
            "defense": 5.0,
            "movement_speed": 100.0,
            "attack_speed": 1.0,
            "critical_chance": 0.05,
            "critical_multiplier": 1.5,
            "all_resist": 0.0,
            "physical_resist": 0.0,
        }
        
        # Экипировка и инвентарь по умолчанию
        self.equipment = {
            "weapon": None,
            "shield": None,
            "armor": None,
            "helmet": None,
            "gloves": None,
            "boots": None,
            "accessory1": None,
            "accessory2": None
        }
        self.inventory = []
        self.max_inventory_size = 20
        
        # Навыки по умолчанию
        self.skills = []
        
        # Очки атрибутов
        self.attribute_points = 0
    
    def get_attribute(self, attr_id: str) -> Optional[AttributeTuple]:
        """Получить атрибут по ID"""
        return self.attributes.get(attr_id)
    
    def get_attribute_value(self, attr_id: str) -> float:
        """Получить текущее значение атрибута"""
        attr = self.get_attribute(attr_id)
        return attr.current if attr else 0.0
    
    def get_attribute_max(self, attr_id: str) -> float:
        """Получить максимальное значение атрибута"""
        attr = self.get_attribute(attr_id)
        return attr.maximum if attr else 0.0
    
    def get_attribute_growth(self, attr_id: str) -> float:
        """Получить скорость роста атрибута"""
        attr = self.get_attribute(attr_id)
        return attr.growth if attr else 0.0
    
    def set_attribute_base(self, attr_id: str, value: float) -> None:
        """Установить базовое значение атрибута"""
        attr = self.get_attribute(attr_id)
        if attr:
            attr.set_base(value)
            self.update_derived_stats()
    
    def set_attribute_max(self, attr_id: str, value: float) -> None:
        """Установить максимальное значение атрибута"""
        attr = self.get_attribute(attr_id)
        if attr:
            attr.set_max(value)
            self.update_derived_stats()
    
    def increase_attribute(self, attr_id: str, amount: float = 1.0) -> bool:
        """Увеличить атрибут"""
        attr = self.get_attribute(attr_id)
        if attr and attr.increase(amount):
            self.update_derived_stats()
            return True
        return False
    
    def invest_attribute_point(self, attr_id: str) -> bool:
        """Инвестировать очко атрибута"""
        if self.attribute_points > 0 and self.increase_attribute(attr_id, 1.0):
            self.attribute_points -= 1
            return True
        return False
    
    def gain_attribute_points(self, amount: int) -> None:
        """Получить очки атрибутов"""
        self.attribute_points += amount
    
    def update_derived_stats(self) -> None:
        """Обновить боевые характеристики на основе атрибутов и экипировки"""
        # Получаем значения атрибутов
        strength = self.get_attribute_value("str_001")
        dexterity = self.get_attribute_value("dex_001")
        intelligence = self.get_attribute_value("int_001")
        vitality = self.get_attribute_value("vit_001")
        endurance = self.get_attribute_value("end_001")
        
        # Ресурсы
        self.combat_stats["max_health"] = 100 + vitality * 10
        self.combat_stats["health"] = min(self.combat_stats["health"], self.combat_stats["max_health"])
        self.combat_stats["max_mana"] = 50 + intelligence * 5
        self.combat_stats["mana"] = min(self.combat_stats["mana"], self.combat_stats["max_mana"])
        self.combat_stats["max_stamina"] = 100 + endurance * 5
        self.combat_stats["stamina"] = min(self.combat_stats["stamina"], self.combat_stats["max_stamina"])
        
        # Урон и скорость атаки
        base_damage = 10 + strength * 2 + dexterity
        weapon_damage = 0.0
        weapon_attack_speed = None
        
        # Проверяем экипированное оружие
        weapon_item = self.equipment.get("weapon")
        if weapon_item:
            if isinstance(weapon_item, dict):
                weapon_damage = float(weapon_item.get("base_damage", 0) or 0)
                weapon_attack_speed = weapon_item.get("attack_speed")
            else:
                # Если это объект ItemData
                try:
                    if hasattr(weapon_item, "base_damage"):
                        weapon_damage = float(getattr(weapon_item, "base_damage", 0) or 0)
                    if hasattr(weapon_item, "attack_speed"):
                        weapon_attack_speed = float(getattr(weapon_item, "attack_speed", 1.0))
                except Exception:
                    pass
        
        self.combat_stats["damage_output"] = base_damage + weapon_damage
        attack_speed = self.combat_stats["attack_speed"]
        if weapon_attack_speed is not None:
            attack_speed = float(weapon_attack_speed)
        
        # Критический шанс
        self.combat_stats["critical_chance"] = 0.05 + dexterity * 0.01
        
        # Защита
        self.combat_stats["defense"] = 5 + endurance * 0.5
        
        # Скорость движения
        self.combat_stats["movement_speed"] = 100 + dexterity * 0.5
    
    def gain_experience(self, amount: int) -> None:
        """Получить опыт"""
        self.experience += amount
        while self.experience >= self.experience_to_next:
            self._level_up()
    
    def _level_up(self) -> None:
        """Повысить уровень"""
        self.experience -= self.experience_to_next
        self.level += 1
        self.experience_to_next = int(self.experience_to_next * 1.5)
        
        # Даем очки атрибутов
        self.gain_attribute_points(5)
        
        # Увеличиваем характеристики
        self._increase_stats_on_level_up()
    
    def _increase_stats_on_level_up(self) -> None:
        """Увеличить характеристики при повышении уровня"""
        # Увеличиваем здоровье и ману
        self.combat_stats["max_health"] += 20
        self.combat_stats["max_mana"] += 10
        self.combat_stats["max_stamina"] += 15
        
        # Восстанавливаем до максимума
        self.combat_stats["health"] = self.combat_stats["max_health"]
        self.combat_stats["mana"] = self.combat_stats["max_mana"]
        self.combat_stats["stamina"] = self.combat_stats["max_stamina"]
        
        # Обновляем производные характеристики
        self.update_derived_stats()
    
    def take_damage(self, damage: float, damage_type: str = "physical") -> float:
        """Получить урон"""
        # Применяем сопротивление
        resist_key = f"{damage_type}_resist"
        resistance = self.combat_stats.get(resist_key, 0.0)
        damage_reduction = 1.0 - min(resistance, 0.8)  # Максимум 80% сопротивления
        
        final_damage = damage * damage_reduction
        self.combat_stats["health"] = max(0, self.combat_stats["health"] - final_damage)
        
        # Проверяем смерть
        if self.combat_stats["health"] <= 0:
            self.die()
        
        return final_damage
    
    def heal(self, amount: float) -> float:
        """Восстановить здоровье"""
        old_health = self.combat_stats["health"]
        self.combat_stats["health"] = min(
            self.combat_stats["max_health"], 
            self.combat_stats["health"] + amount
        )
        return self.combat_stats["health"] - old_health
    
    def restore_mana(self, amount: float) -> float:
        """Восстановить ману"""
        old_mana = self.combat_stats["mana"]
        self.combat_stats["mana"] = min(
            self.combat_stats["max_mana"], 
            self.combat_stats["mana"] + amount
        )
        return self.combat_stats["mana"] - old_mana
    
    def restore_stamina(self, amount: float) -> float:
        """Восстановить выносливость"""
        old_stamina = self.combat_stats["stamina"]
        self.combat_stats["stamina"] = min(
            self.combat_stats["max_stamina"], 
            self.combat_stats["stamina"] + amount
        )
        return self.combat_stats["stamina"] - old_stamina
    
    def can_attack(self) -> bool:
        """Может ли атаковать"""
        return self.attack_cooldown <= 0 and self.combat_stats["stamina"] > 10
    
    def start_attack_cooldown(self) -> None:
        """Начать кулдаун атаки"""
        self.attack_cooldown = 1.0 / self.combat_stats["attack_speed"]
    
    def is_alive(self) -> bool:
        """Жив ли персонаж"""
        return self.combat_stats["health"] > 0
    
    def is_dead(self) -> bool:
        """Мертв ли персонаж"""
        return not self.is_alive()
    
    def add_to_inventory(self, item: Dict[str, Any]) -> bool:
        """Добавить предмет в инвентарь"""
        if len(self.inventory) < self.max_inventory_size:
            self.inventory.append(item)
            return True
        return False
    
    def remove_from_inventory(self, item: Dict[str, Any]) -> bool:
        """Убрать предмет из инвентаря"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def equip_item(self, item: Dict[str, Any], slot: str) -> bool:
        """Экипировать предмет"""
        if slot in self.equipment:
            # Снимаем предыдущий предмет
            if self.equipment[slot]:
                self.unequip_item(slot)
            
            # Экипируем новый предмет
            self.equipment[slot] = item
            
            # Применяем эффекты предмета
            self._apply_item_effects(item, True)
            
            # Обновляем характеристики
            self.update_derived_stats()
            return True
        return False
    
    def unequip_item(self, slot: str) -> Optional[Dict[str, Any]]:
        """Снять предмет из слота"""
        if slot in self.equipment and self.equipment[slot]:
            item = self.equipment[slot]
            
            # Убираем эффекты предмета
            self._apply_item_effects(item, False)
            
            # Снимаем предмет
            self.equipment[slot] = None
            
            # Обновляем характеристики
            self.update_derived_stats()
            return item
        return None
    
    def _apply_item_effects(self, item: Dict[str, Any], equip: bool):
        """Применить эффекты предмета"""
        if not item:
            return
        
        # Получаем данные предмета
        item_id = item.get("id")
        if not item_id:
            return
        
        item_data = data_manager.get_item(item_id)
        if not item_data:
            return
        
        # Применяем модификаторы
        multiplier = 1 if equip else -1
        for stat, value in item_data.modifiers.items():
            if stat in self.combat_stats:
                self.combat_stats[stat] += value * multiplier
        
        # Применяем эффекты
        for effect_id in item_data.effects:
            if equip:
                self.add_effect(effect_id, {}, 1)
            else:
                self.remove_effect(effect_id)
    
    def use_consumable(self, item: Dict[str, Any]) -> bool:
        """Использовать расходуемый предмет"""
        if not item or item.get("type") != "consumable":
            return False
        
        # Получаем данные предмета
        item_id = item.get("id")
        if not item_id:
            return False
        
        item_data = data_manager.get_item(item_id)
        if not item_data:
            return False
        
        # Применяем эффекты
        if item_data.heal_amount:
            self.heal(item_data.heal_amount)
        if item_data.mana_amount:
            self.restore_mana(item_data.mana_amount)
        
        # Убираем предмет из инвентаря
        self.remove_from_inventory(item)
        return True
    
    def has_effect_tag(self, tag: str) -> bool:
        """Есть ли эффект с определенным тегом"""
        for effect in self.active_effects.values():
            if hasattr(effect, 'tags') and tag in effect.tags:
                return True
        return False
    
    def add_effect(self, effect_id: str, effect_data: dict, stacks: int = 1) -> None:
        """Добавить эффект"""
        # Получаем данные эффекта
        effect_info = data_manager.get_effect(effect_id)
        if not effect_info:
            return
        
        # Создаем эффект
        effect = Effect(
            effect_id=effect_id,
            name=effect_info.name,
            description=effect_info.description,
            tags=effect_info.tags,
            modifiers=effect_info.modifiers,
            max_stacks=effect_info.max_stacks,
            duration=effect_info.duration,
            interval=effect_info.interval
        )
        
        # Добавляем эффект
        if effect_id in self.active_effects:
            # Увеличиваем стаки
            self.active_effects[effect_id].stacks = min(
                self.active_effects[effect_id].stacks + stacks,
                effect_info.max_stacks
            )
        else:
            effect.stacks = stacks
            self.active_effects[effect_id] = effect
    
    def remove_effect(self, effect_id: str) -> None:
        """Убрать эффект"""
        if effect_id in self.active_effects:
            del self.active_effects[effect_id]
    
    def update_effects(self, delta_time: float) -> None:
        """Обновить эффекты"""
        effects_to_remove = []
        
        for effect_id, effect in self.active_effects.items():
            effect.update(delta_time)
            
            # Проверяем, закончился ли эффект
            if effect.is_expired():
                effects_to_remove.append(effect_id)
        
        # Убираем закончившиеся эффекты
        for effect_id in effects_to_remove:
            self.remove_effect(effect_id)
    
    def use_skill(self, skill_id: str) -> None:
        """Использовать навык"""
        if skill_id in self.skills and skill_id not in self.skill_cooldowns:
            # Получаем данные навыка
            skill_data = data_manager.get_skill(skill_id)
            if skill_data:
                # Проверяем требования
                if self.combat_stats["mana"] >= skill_data.get("mana_cost", 0):
                    # Используем навык
                    self.combat_stats["mana"] -= skill_data.get("mana_cost", 0)
                    
                    # Устанавливаем кулдаун
                    self.skill_cooldowns[skill_id] = skill_data.get("cooldown", 0)
                    
                    # Применяем эффекты навыка
                    for effect_id in skill_data.get("effects", []):
                        self.add_effect(effect_id, {}, 1)
    
    def distance_to(self, target) -> float:
        """Расстояние до цели"""
        if hasattr(target, 'position'):
            return math.sqrt(
                (self.position[0] - target.position[0]) ** 2 +
                (self.position[1] - target.position[1]) ** 2
            )
        return float('inf')
    
    def move_towards(self, target_pos: Tuple[float, float], speed: float, delta_time: float):
        """Двигаться к цели"""
        if not self.is_alive():
            return
        
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Нормализуем вектор направления
            dx /= distance
            dy /= distance
            
            # Двигаемся
            move_distance = speed * delta_time
            self.position[0] += dx * move_distance
            self.position[1] += dy * move_distance
    
    def die(self) -> None:
        """Смерть сущности"""
        self.alive = False
        self.combat_stats["health"] = 0
        self._on_death()
    
    def _on_death(self) -> None:
        """Событие смерти"""
        # Убираем все эффекты
        self.active_effects.clear()
        
        # Сбрасываем кулдауны
        self.skill_cooldowns.clear()
    
    def respawn(self, position: Tuple[float, float]) -> None:
        """Возрождение"""
        self.position = list(position)
        self.alive = True
        
        # Восстанавливаем здоровье
        self.combat_stats["health"] = self.combat_stats["max_health"]
        self.combat_stats["mana"] = self.combat_stats["max_mana"]
        self.combat_stats["stamina"] = self.combat_stats["max_stamina"]
        
        # Убираем все эффекты
        self.active_effects.clear()
        
        # Сбрасываем кулдауны
        self.skill_cooldowns.clear()
    
    def update(self, delta_time: float) -> None:
        """Обновление сущности"""
        if not self.is_alive():
            return
        
        # Обновляем кулдауны
        for skill_id in list(self.skill_cooldowns.keys()):
            self.skill_cooldowns[skill_id] -= delta_time
            if self.skill_cooldowns[skill_id] <= 0:
                del self.skill_cooldowns[skill_id]
        
        # Обновляем кулдаун атаки
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
        
        # Обновляем эффекты
        self.update_effects(delta_time)
        
        # Обновляем производные характеристики
        self.update_derived_stats()
        
        # Вызываем пользовательское обновление
        self._on_update(delta_time)
    
    def render(self, canvas, camera_position: Tuple[float, float]) -> None:
        """Отрисовка сущности"""
        # Базовая отрисовка
        x = self.position[0] - camera_position[0]
        y = self.position[1] - camera_position[1]
        
        # Вызываем пользовательскую отрисовку
        self._on_render(canvas, (x, y))
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в словарь"""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "position": self.position.copy(),
            "alive": self.alive,
            "level": self.level,
            "experience": self.experience,
            "experience_to_next": self.experience_to_next,
            "attributes": {k: (v.current, v.maximum, v.growth) for k, v in self.attributes.items()},
            "combat_stats": self.combat_stats.copy(),
            "equipment": self.equipment.copy(),
            "inventory": self.inventory.copy(),
            "skills": self.skills.copy(),
            "attribute_points": self.attribute_points,
            "active_effects": {k: v.to_dict() for k, v in self.active_effects.items()},
            "skill_cooldowns": self.skill_cooldowns.copy()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Десериализация из словаря"""
        self.entity_id = data["entity_id"]
        self.entity_type = data["entity_type"]
        self.position = data["position"]
        self.alive = data["alive"]
        self.level = data["level"]
        self.experience = data["experience"]
        self.experience_to_next = data["experience_to_next"]
        
        # Восстанавливаем атрибуты
        for k, v in data["attributes"].items():
            if k in self.attributes:
                self.attributes[k].current = v[0]
                self.attributes[k].maximum = v[1]
                self.attributes[k].growth = v[2]
        
        self.combat_stats = data["combat_stats"]
        self.equipment = data["equipment"]
        self.inventory = data["inventory"]
        self.skills = data["skills"]
        self.attribute_points = data["attribute_points"]
        
        # Восстанавливаем эффекты
        self.active_effects = {}
        for k, v in data["active_effects"].items():
            effect = Effect.from_dict(v)
            self.active_effects[k] = effect
        
        self.skill_cooldowns = data["skill_cooldowns"]
        
        # Обновляем характеристики
        self.update_derived_stats()
    
    def _on_update(self, delta_time: float) -> None:
        """Пользовательское обновление (переопределяется в наследниках)"""
        pass
    
    def _on_render(self, canvas, position: Tuple[float, float]) -> None:
        """Пользовательская отрисовка (переопределяется в наследниках)"""
        pass
    
    @property
    def id(self) -> str:
        return self.entity_id
    
    @id.setter
    def id(self, value: str) -> None:
        self.entity_id = value
    
    @property
    def health(self) -> float:
        return self.combat_stats["health"]
    
    @health.setter
    def health(self, value: float) -> None:
        self.combat_stats["health"] = max(0, min(value, self.combat_stats["max_health"]))
    
    @property
    def max_health(self) -> float:
        return self.combat_stats["max_health"]
    
    @property
    def mana(self) -> float:
        return self.combat_stats["mana"]
    
    @mana.setter
    def mana(self, value: float) -> None:
        self.combat_stats["mana"] = max(0, min(value, self.combat_stats["max_mana"]))
    
    @property
    def max_mana(self) -> float:
        return self.combat_stats["max_mana"]
    
    @property
    def stamina(self) -> float:
        return self.combat_stats["stamina"]
    
    @stamina.setter
    def stamina(self, value: float) -> None:
        self.combat_stats["stamina"] = max(0, min(value, self.combat_stats["max_stamina"]))
    
    @property
    def max_stamina(self) -> float:
        return self.combat_stats["max_stamina"]
    
    @property
    def combat_stats(self) -> Dict[str, Any]:
        return self._combat_stats
    
    @combat_stats.setter
    def combat_stats(self, value: Dict[str, Any]) -> None:
        self._combat_stats = value
    
    @property
    def attack_cooldown(self) -> float:
        return self._attack_cooldown
    
    @attack_cooldown.setter
    def attack_cooldown(self, value: float) -> None:
        self._attack_cooldown = value
    
    @property
    def movement_speed(self) -> float:
        return self.combat_stats["movement_speed"]
    
    @movement_speed.setter
    def movement_speed(self, value: float) -> None:
        self.combat_stats["movement_speed"] = value
    
    @property
    def damage_output(self) -> float:
        return self.combat_stats["damage_output"]
    
    @damage_output.setter
    def damage_output(self, value: float) -> None:
        self.combat_stats["damage_output"] = value
    
    @property
    def defense(self) -> float:
        return self.combat_stats["defense"]
    
    @defense.setter
    def defense(self, value: float) -> None:
        self.combat_stats["defense"] = value
    
    @property
    def attack_speed(self) -> float:
        return self.combat_stats["attack_speed"]
    
    @attack_speed.setter
    def attack_speed(self, value: float) -> None:
        self.combat_stats["attack_speed"] = value
    
    @property
    def critical_chance(self) -> float:
        return self.combat_stats["critical_chance"]
    
    @critical_chance.setter
    def critical_chance(self, value: float) -> None:
        self.combat_stats["critical_chance"] = value
    
    @property
    def critical_multiplier(self) -> float:
        return self.combat_stats["critical_multiplier"]
    
    @critical_multiplier.setter
    def critical_multiplier(self, value: float) -> None:
        self.combat_stats["critical_multiplier"] = value
    
    @property
    def all_resist(self) -> float:
        return self.combat_stats["all_resist"]
    
    @all_resist.setter
    def all_resist(self, value: float) -> None:
        self.combat_stats["all_resist"] = value
    
    @property
    def physical_resist(self) -> float:
        return self.combat_stats["physical_resist"]
    
    @physical_resist.setter
    def physical_resist(self, value: float) -> None:
        self.combat_stats["physical_resist"] = value
