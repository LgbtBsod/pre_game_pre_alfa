import random
import math
import time
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from ai.memory import LearningController
from .effect import Effect


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
class Attribute:
    value: int
    max_value: int = 100
    growth_rate: float = 1.0


class Entity:
    def __init__(self, entity_id: str, position: tuple = (0, 0)):
        self.entity_id = entity_id
        self.position = list(position)
        self.alive = True
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        
        # Характеристики
        self.attributes = {
            "strength": Attribute(10),
            "dexterity": Attribute(10),
            "intelligence": Attribute(10),
            "vitality": Attribute(10),
            "endurance": Attribute(10),
            "faith": Attribute(10),
            "luck": Attribute(10),
        }
        self.attribute_points = 0
        
        # Боевые характеристики
        self.combat_stats = {
            "health": 100,
            "max_health": 100,
            "mana": 50,
            "max_mana": 50,
            "stamina": 100,
            "max_stamina": 100,
            "damage_output": 10,
            "defense": 5,
            "movement_speed": 100.0,
            "attack_speed": 1.0,
            "critical_chance": 0.05,
            "critical_multiplier": 1.5,
            # Дополнительные параметры, используемые эффектами
            "all_resist": 0.0,
            "physical_resist": 0.0,
        }
        
        # Экипировка и инвентарь
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
        self.player_ref = None
        self.shared_knowledge = {}
        
        # Обновляем производные характеристики
        self.update_derived_stats()
    
    def update_derived_stats(self):
        """Обновление производных характеристик на основе базовых"""
        # Здоровье
        vitality = self.attributes["vitality"].value
        self.combat_stats["max_health"] = 100 + vitality * 10
        self.combat_stats["health"] = min(self.combat_stats["health"], self.combat_stats["max_health"])
        
        # Мана
        intelligence = self.attributes["intelligence"].value
        self.combat_stats["max_mana"] = 50 + intelligence * 5
        self.combat_stats["mana"] = min(self.combat_stats["mana"], self.combat_stats["max_mana"])
        
        # Выносливость
        endurance = self.attributes["endurance"].value
        self.combat_stats["max_stamina"] = 100 + endurance * 5
        self.combat_stats["stamina"] = min(self.combat_stats["stamina"], self.combat_stats["max_stamina"])
        
        # Урон
        strength = self.attributes["strength"].value
        dexterity = self.attributes["dexterity"].value
        base_damage = 10 + strength * 2 + dexterity
        
        # Учитываем экипировку (поддержка словарей и объектного оружия)
        weapon_damage = 0.0
        weapon_attack_speed = None
        weapon_item = self.equipment.get("weapon")
        if weapon_item:
            if isinstance(weapon_item, dict):
                weapon_damage = float(weapon_item.get("base_damage", 0) or 0)
                weapon_attack_speed = weapon_item.get("attack_speed")
            else:
                # Объектное оружие
                try:
                    if hasattr(weapon_item, "damage_types"):
                        for dmg in weapon_item.damage_types:
                            try:
                                if isinstance(dmg, dict):
                                    weapon_damage += float(dmg.get("value", 0) or 0)
                                else:
                                    weapon_damage += float(getattr(dmg, "value", 0) or 0)
                            except Exception:
                                pass
                    if hasattr(weapon_item, "attack_speed"):
                        weapon_attack_speed = float(getattr(weapon_item, "attack_speed", 1.0))
                except Exception:
                    pass
        
        self.combat_stats["damage_output"] = base_damage + weapon_damage
        
        # Защита
        defense = 5
        for slot, item in self.equipment.items():
            if not item:
                continue
            if isinstance(item, dict) and "defense" in item:
                defense += item["defense"]
            elif hasattr(item, "defense"):
                try:
                    defense += float(getattr(item, "defense", 0) or 0)
                except Exception:
                    pass
        self.combat_stats["defense"] = defense
        
        # Скорость атаки
        attack_speed = 1.0
        if weapon_attack_speed is not None:
            attack_speed *= weapon_attack_speed
        self.combat_stats["attack_speed"] = attack_speed
    
    def gain_experience(self, amount: int):
        """Получение опыта"""
        self.experience += amount
        while self.experience >= self.experience_to_next:
            self.level_up()
    
    def level_up(self):
        """Повышение уровня"""
        self.level += 1
        self.experience -= self.experience_to_next
        self.experience_to_next = int(self.experience_to_next * 1.2)
        self.attribute_points += 5
        
        # Улучшение характеристик
        self.update_derived_stats()
        
        # Обучение на основе опыта
        self.learning_system.process_experience()
    
    def distribute_attribute_points(self):
        """Распределить очки характеристик"""
        # Будет реализовано в подклассах
        pass
    
    def take_damage(self, damage_report: dict):
        """Получить урон"""
        total_damage = float(damage_report.get("total", 0) or 0)
        self.health -= total_damage
        
        if self.health <= 0:
            self.die()
        else:
            self.learn_from_damage(damage_report)
    
    def learn_from_damage(self, damage_report: dict):
        """Анализ полученного урона для обучения"""
        effective_types = []
        total_damage = float(damage_report.get("total", 0) or 0)
        for dmg_type, amount in damage_report.items():
            if dmg_type == "total":
                continue
            try:
                amount_val = float(amount)
            except (TypeError, ValueError):
                continue
            if amount_val > total_damage * 0.3:
                effective_types.append(dmg_type)
        
        if effective_types:
            if "effective_vs_me" not in self.memory:
                self.memory["effective_vs_me"] = []
            
            for dmg_type in effective_types:
                if dmg_type not in self.memory["effective_vs_me"]:
                    self.memory["effective_vs_me"].append(dmg_type)
    
    def die(self):
        """Обработка смерти сущности"""
        self.alive = False
        
        if self.last_attacker:
            exp_reward = self.level * 25
            if self.is_boss:
                exp_reward *= 10
            self.last_attacker.gain_experience(exp_reward)
    
    def attack(self, target):
        """Атаковать цель"""
        if self.attack_cooldown > 0 or not self.alive or not target.alive:
            return None
        
        # Расчет урона
        base_damage = self.combat_stats["damage_output"]
        
        # Критический удар
        is_critical = random.random() < self.combat_stats["critical_chance"]
        if is_critical:
            base_damage *= self.combat_stats["critical_multiplier"]
        
        # Случайный разброс
        final_damage = base_damage * random.uniform(0.8, 1.2)
        
        # Создание отчета об уроне
        damage_report = {
            "total": final_damage,
            "physical": final_damage,
            "source": self
        }
        
        # Применение урона
        target.take_damage(damage_report)
        target.last_attacker = self
        
        # Кулдаун атаки
        self.attack_cooldown = 1.0 / self.combat_stats["attack_speed"]
        
        return damage_report
    
    def update(self, delta_time: float):
        """Обновление сущности"""
        # Обновление кулдаунов
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
        
        # Обновление системы обучения
        if hasattr(self, 'learning_system'):
            self.learning_system.update(delta_time)
        
        # Обновление эффектов предметов
        self.update_item_effects(delta_time)
        
        # Обновление эффектов состояний
        self.update_effects(delta_time)

    # Совместимость: алиас id <-> entity_id
    @property
    def id(self) -> str:
        return self.entity_id

    @id.setter
    def id(self, value: str):
        self.entity_id = value
    
    def equip_item(self, item):
        """Экипировать предмет"""
        if not item:
            return False
        
        slot = None
        if hasattr(item, "equipment_slot"):
            slot = getattr(item, "equipment_slot")
        else:
            item_type = item.get("type", "unknown")
            slot = self.get_equipment_slot(item_type)
        
        if slot:
            # Снимаем предыдущий предмет
            if self.equipment[slot]:
                self.unequip_item(slot)
            
            # Экипируем новый
            self.equipment[slot] = item
            if hasattr(item, "apply_effects"):
                try:
                    item.apply_effects(self)
                except Exception:
                    pass
            self.update_derived_stats()
            return True
        
        return False
    
    def unequip_item(self, slot):
        """Снять предмет"""
        if slot in self.equipment and self.equipment[slot]:
            item = self.equipment[slot]
            self.equipment[slot] = None
            if hasattr(item, "remove_effects"):
                try:
                    item.remove_effects(self)
                except Exception:
                    pass
            self.update_derived_stats()
            return item
        return None
    
    def get_equipment_slot(self, item_type):
        """Определить слот для предмета"""
        slot_mapping = {
            "weapon": "weapon",
            "shield": "shield", 
            "armor": "armor",
            "helmet": "helmet",
            "gloves": "gloves",
            "boots": "boots",
            "amulet": "accessory1",
            "ring": "accessory2"
        }
        return slot_mapping.get(item_type)
    
    def add_to_inventory(self, item):
        """Добавить предмет в инвентарь"""
        if len(self.inventory) < self.max_inventory_size:
            self.inventory.append(item)
            return True
        return False
    
    def remove_from_inventory(self, item):
        """Удалить предмет из инвентаря"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def use_consumable(self, item):
        """Использовать расходуемый предмет"""
        if not item or "effects" not in item:
            return False
        
        effects = item["effects"]
        applied = False
        
        for effect_type, effect_value in effects.items():
            if effect_type == "heal":
                self.combat_stats["health"] = min(
                    self.combat_stats["max_health"],
                    self.combat_stats["health"] + effect_value
                )
                applied = True
            elif effect_type == "restore_mana":
                self.combat_stats["mana"] = min(
                    self.combat_stats["max_mana"],
                    self.combat_stats["mana"] + effect_value
                )
                applied = True
            elif effect_type == "xp_boost":
                self.gain_experience(effect_value)
                applied = True
        
        if applied:
            self.remove_from_inventory(item)
            return True
        
        return False
    
    def update_item_effects(self, delta_time: float):
        """Обновление эффектов предметов"""
        for slot, item in self.equipment.items():
            if not item:
                continue
            if isinstance(item, dict) and "effects" in item:
                effects = item["effects"]
                for effect in effects:
                    if effect == "regen_health":
                        regen_amount = 5 * delta_time
                        self.combat_stats["health"] = min(
                            self.combat_stats["max_health"],
                            self.combat_stats["health"] + regen_amount
                        )
                    elif effect == "boost_damage":
                        # Временное усиление урона
                        pass
    
    def has_consumable(self, effect_type: str = None):
        """Проверить наличие расходуемого предмета"""
        for item in self.inventory:
            if "effects" in item:
                if effect_type is None:
                    return True
                if effect_type in item["effects"]:
                    return True
        return False
    
    def use_best_healing_item(self):
        """Использовать лучший предмет лечения"""
        best_item = None
        best_heal = 0
        
        for item in self.inventory:
            if "effects" in item and "heal" in item["effects"]:
                heal_amount = item["effects"]["heal"]
                if heal_amount > best_heal:
                    best_heal = heal_amount
                    best_item = item
        
        if best_item:
            return self.use_consumable(best_item)
        return False
    
    @property
    def health(self):
        return self.combat_stats["health"]
    
    @health.setter
    def health(self, value):
        self.combat_stats["health"] = max(0, min(value, self.combat_stats["max_health"]))
    
    @property
    def max_health(self):
        return self.combat_stats["max_health"]
    
    @property
    def mana(self):
        return self.combat_stats["mana"]
    
    @mana.setter
    def mana(self, value):
        self.combat_stats["mana"] = max(0, min(value, self.combat_stats["max_mana"]))
    
    @property
    def max_mana(self):
        return self.combat_stats["max_mana"]
    
    @property
    def stamina(self):
        return self.combat_stats["stamina"]
    
    @stamina.setter
    def stamina(self, value):
        self.combat_stats["stamina"] = max(0, min(value, self.combat_stats["max_stamina"]))
    
    @property
    def max_stamina(self):
        return self.combat_stats["max_stamina"]
    
    def has_effect_tag(self, tag: str) -> bool:
        """Проверить наличие эффекта по тегу среди активных эффектов"""
        for eff in self.active_effects.values():
            if tag in getattr(eff, 'tags', []):
                return True
        return False
    
    def add_effect(self, effect_id: str, effect_data: dict, stacks: int = 1):
        """Добавить эффект к сущности"""
        if not effect_data:
            return
        if effect_id in self.active_effects:
            # Усиливаем стаки существующего эффекта
            self.active_effects[effect_id].stacks += max(1, int(stacks))
            return
        tags = effect_data.get("tags", [])
        modifiers = effect_data.get("modifiers", [])
        effect = Effect(effect_id, tags, modifiers)
        effect.stacks = max(1, int(stacks))
        # Применяем эффект немедленно
        effect.apply(self, True)
        self.active_effects[effect_id] = effect
    
    def remove_effect(self, effect_id: str):
        """Удалить эффект с сущности"""
        effect = self.active_effects.get(effect_id)
        if not effect:
            return
        # Отменяем модификаторы
        effect.apply(self, False)
        del self.active_effects[effect_id]
    
    def update_effects(self, delta_time: float):
        """Обновить состояние эффектов"""
        if not self.active_effects:
            return
        expired: List[str] = []
        for eff_id, eff in list(self.active_effects.items()):
            eff.process_tick(self, delta_time)
            if eff.is_expired():
                expired.append(eff_id)
        for eff_id in expired:
            self.remove_effect(eff_id)

    def use_skill(self, ability_id: str):
        """Базовое применение способности для сущностей.
        Поддерживает урон по цели и наложение эффекта на себя.
        """
        skills = getattr(self, "skills", {})
        if ability_id not in skills:
            return
        skill_data = skills[ability_id]
        # Нанесение урона цели, если есть ссылка на игрока
        target = getattr(self, "player_ref", None)
        damage = float(skill_data.get("damage", 0) or 0)
        if target and getattr(target, "alive", False) and damage > 0:
            target.take_damage({
                "total": damage,
                "physical": damage,
                "source": self,
            })
        # Эффект от способности
        effect_id = skill_data.get("apply_effect")
        if effect_id and hasattr(self, "effects_db") and effect_id in self.effects_db:
            self.add_effect(effect_id, self.effects_db[effect_id])
    
    def calculate_stat_with_effects(self, base_value: float, stat_name: str) -> float:
        """Рассчитать значение характеристики с учетом эффектов"""
        # Простая реализация без эффектов
        return base_value
    
    def distance_to(self, target) -> float:
        """Расчитать расстояние до цели"""
        dx = target.position[0] - self.position[0]
        dy = target.position[1] - self.position[1]
        return math.sqrt(dx*dx + dy*dy)
    
    def move_towards(self, target_pos: tuple, speed: float, delta_time: float):
        """Двигаться к целевой позиции"""
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 1:
            dx /= distance
            dy /= distance
            actual_speed = self.calculate_stat_with_effects(speed, "movement_speed")
            self.position[0] += dx * actual_speed * delta_time
            self.position[1] += dy * actual_speed * delta_time

    # Свойства-адаптеры для того, чтобы эффекты могли изменять combat_stats через getattr/setattr
    @property
    def movement_speed(self) -> float:
        return self.combat_stats.get("movement_speed", 100.0)

    @movement_speed.setter
    def movement_speed(self, value: float):
        self.combat_stats["movement_speed"] = float(value)

    @property
    def damage_output(self) -> float:
        return self.combat_stats.get("damage_output", 10.0)

    @damage_output.setter
    def damage_output(self, value: float):
        self.combat_stats["damage_output"] = float(value)

    @property
    def defense(self) -> float:
        return self.combat_stats.get("defense", 5.0)

    @defense.setter
    def defense(self, value: float):
        self.combat_stats["defense"] = float(value)

    @property
    def attack_speed(self) -> float:
        return self.combat_stats.get("attack_speed", 1.0)

    @attack_speed.setter
    def attack_speed(self, value: float):
        self.combat_stats["attack_speed"] = float(value)

    @property
    def critical_chance(self) -> float:
        return self.combat_stats.get("critical_chance", 0.05)

    @critical_chance.setter
    def critical_chance(self, value: float):
        self.combat_stats["critical_chance"] = float(value)

    @property
    def critical_multiplier(self) -> float:
        return self.combat_stats.get("critical_multiplier", 1.5)

    @critical_multiplier.setter
    def critical_multiplier(self, value: float):
        self.combat_stats["critical_multiplier"] = float(value)

    @property
    def all_resist(self) -> float:
        return self.combat_stats.get("all_resist", 0.0)

    @all_resist.setter
    def all_resist(self, value: float):
        self.combat_stats["all_resist"] = float(value)

    @property
    def physical_resist(self) -> float:
        return self.combat_stats.get("physical_resist", 0.0)

    @physical_resist.setter
    def physical_resist(self, value: float):
        self.combat_stats["physical_resist"] = float(value)