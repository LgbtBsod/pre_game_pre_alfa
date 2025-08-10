"""
Базовый класс сущности.
Объединяет все системы: атрибуты, боевые характеристики, инвентарь, эффекты, AI.
"""

import math
import time
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from core.attributes import AttributeManager
from core.combat_stats import CombatStatsManager
from core.inventory import InventoryManager
from entities.effect import Effect

# AI системы
from ai.memory import AIMemory, LearningController
from ai.decision_maker import DecisionMaker
from ai.pattern_recognizer import PatternRecognizer
from ai.learning import LearningSystem


class DamageType(Enum):
    """Типы урона"""
    PHYSICAL = "physical"
    MAGIC = "magic"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"


class CombatStyle(Enum):
    """Стили боя"""
    MELEE = "melee"
    RANGED = "ranged"
    MAGIC = "magic"


class BaseEntity:
    """Базовая сущность с основными системами и AI"""
    
    def __init__(self, entity_id: str, position: tuple = (0, 0)):
        self.entity_id = entity_id
        self.name = entity_id  # Default name is the entity_id
        self.position = list(position)
        self.alive = True
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        self.playtime = 0.0
        
        # Системы сущности
        self.attribute_manager = AttributeManager()
        self.combat_stats_manager = CombatStatsManager()
        self.inventory_manager = InventoryManager()
        
        # AI системы
        self.ai_memory = AIMemory()
        self.learning_controller = LearningController(self)
        self.decision_maker = DecisionMaker(self)
        self.pattern_recognizer = PatternRecognizer()
        self.learning_system = LearningSystem(self)
        
        # Инициализация систем
        self.attribute_manager.initialize_default_attributes()
        
        # Активные эффекты и кулдауны
        self.active_effects: Dict[str, Effect] = {}
        self.skill_cooldowns: Dict[str, float] = {}
        
        # Боевые параметры
        self.attack_cooldown = 0.0
        self.last_attacker = None
        self.is_boss = False
        self.combat_style = CombatStyle.MELEE
        
        # Система обучения
        self.learning_rate = 0.1
        self.memory = {}
        self.known_weaknesses = []
        self.learned_tactics = []
        self.item_preferences = {}
        self.weapon_affinities = {}
        
        # Обновляем производные характеристики
        self.update_derived_stats()
    
    def update_derived_stats(self):
        """Обновляет производные характеристики на основе атрибутов"""
        # Получаем атрибуты
        strength = self.attribute_manager.get_attribute_value("strength")
        dexterity = self.attribute_manager.get_attribute_value("dexterity")
        intelligence = self.attribute_manager.get_attribute_value("intelligence")
        vitality = self.attribute_manager.get_attribute_value("vitality")
        endurance = self.attribute_manager.get_attribute_value("endurance")
        
        # Базовые характеристики
        base_health = 50 + (vitality * 10)
        base_mana = 20 + (intelligence * 5)
        base_stamina = 50 + (endurance * 5)
        base_damage = 5 + (strength * 0.5)
        base_defense = 2 + (strength * 0.2)
        base_speed = 80 + (dexterity * 2)
        
        # Получаем бонусы от экипировки
        equipment_bonuses = self.inventory_manager.get_equipment_bonuses()
        
        # Обновляем боевые характеристики
        stats = self.combat_stats_manager.get_stats()
        stats.max_health = base_health + equipment_bonuses.get("max_health", 0)
        stats.max_mana = base_mana + equipment_bonuses.get("max_mana", 0)
        stats.max_stamina = base_stamina + equipment_bonuses.get("max_stamina", 0)
        stats.damage_output = base_damage + equipment_bonuses.get("damage", 0)
        stats.defense = base_defense + equipment_bonuses.get("defense", 0)
        stats.movement_speed = base_speed + equipment_bonuses.get("movement_speed", 0)
        
        # Восстанавливаем здоровье/ману/выносливость до максимума при обновлении
        if stats.health > stats.max_health:
            stats.health = stats.max_health
        if stats.mana > stats.max_mana:
            stats.mana = stats.max_mana
        if stats.stamina > stats.max_stamina:
            stats.stamina = stats.max_stamina
    
    def gain_experience(self, amount: int):
        """Получает опыт"""
        self.experience += amount
        while self.experience >= self.experience_to_next:
            self.level_up()
    
    def level_up(self):
        """Повышает уровень"""
        self.experience -= self.experience_to_next
        self.level += 1
        self.experience_to_next = int(self.experience_to_next * 1.2)
        
        # Даем очки атрибутов
        self.attribute_manager.add_attribute_points(5)
        
        # Обновляем характеристики
        self.update_derived_stats()
        
        # Улучшаем AI с уровнем
        self.improve_ai_with_level()
    
    def improve_ai_with_level(self):
        """Улучшает AI с повышением уровня"""
        # Увеличиваем скорость обучения
        self.learning_rate = min(1.0, self.learning_rate + 0.05)
        
        # Улучшаем память
        self.ai_memory.improve_capacity()
        
        # Разблокируем новые тактики
        if self.level >= 5:
            self.learned_tactics.append("defensive_stance")
        if self.level >= 10:
            self.learned_tactics.append("counter_attack")
        if self.level >= 15:
            self.learned_tactics.append("weapon_switching")
    
    def take_damage(self, damage_report: dict):
        """Получает урон"""
        damage = damage_report.get("damage", 0)
        damage_type = damage_report.get("damage_type", "physical")
        
        # Вычисляем финальный урон с учетом защиты
        final_damage = self.combat_stats_manager.calculate_final_damage(damage, damage_type)
        
        # Применяем урон
        actual_damage = self.combat_stats_manager.take_damage(final_damage)
        
        # Обновляем отчет об уроне
        damage_report["final_damage"] = actual_damage
        damage_report["damage_reduction"] = damage - actual_damage
        
        # Проверяем смерть
        if self.combat_stats_manager.is_dead():
            self.die()
        
        # Учимся на уроне
        self.learn_from_damage(damage_report)
    
    def learn_from_damage(self, damage_report: dict):
        """Учится на полученном уроне"""
        damage_type = damage_report.get("damage_type", "physical")
        attacker_type = damage_report.get("attacker_type", "unknown")
        attacker_weapon = damage_report.get("weapon_type", "unknown")
        
        # Запоминаем слабости
        if damage_report.get("final_damage", 0) > 10:
            weakness_key = f"{attacker_type}_{damage_type}"
            if weakness_key not in self.known_weaknesses:
                self.known_weaknesses.append(weakness_key)
            
            # Учимся на типах оружия
            if attacker_weapon != "unknown":
                self.learn_weapon_effectiveness(attacker_weapon, damage_type, damage_report.get("final_damage", 0))
        
        # Сохраняем в память
        self.ai_memory.record_event("damage_taken", damage_report)
        
        # Анализируем паттерны
        self.pattern_recognizer.analyze_damage_pattern(damage_report)
    
    def learn_weapon_effectiveness(self, weapon_type: str, damage_type: str, damage_amount: float):
        """Учится эффективности оружия"""
        if weapon_type not in self.weapon_affinities:
            self.weapon_affinities[weapon_type] = {}
        
        if damage_type not in self.weapon_affinities[weapon_type]:
            self.weapon_affinities[weapon_type][damage_type] = []
        
        self.weapon_affinities[weapon_type][damage_type].append(damage_amount)
        
        # Ограничиваем историю
        if len(self.weapon_affinities[weapon_type][damage_type]) > 10:
            self.weapon_affinities[weapon_type][damage_type] = self.weapon_affinities[weapon_type][damage_type][-10:]
    
    def attack(self, target):
        """Атакует цель с учетом обучения"""
        if not self.can_attack() or not target.alive:
            return None
        
        # Выбираем лучшее оружие для цели
        best_weapon = self.select_best_weapon_for_target(target)
        
        # Вычисляем урон
        base_damage = self.combat_stats_manager.get_stats().damage_output
        critical_chance = self.combat_stats_manager.get_stats().critical_chance
        critical_multiplier = self.combat_stats_manager.get_stats().critical_multiplier
        
        # Применяем бонусы от обучения
        damage_bonus = self.get_learned_damage_bonus(target)
        base_damage += damage_bonus
        
        # Проверяем критический удар
        import random
        is_critical = random.random() < critical_chance
        damage_multiplier = critical_multiplier if is_critical else 1.0
        
        final_damage = base_damage * damage_multiplier
        
        # Создаем отчет об уроне
        damage_report = {
            "damage": final_damage,
            "damage_type": "physical",
            "is_critical": is_critical,
            "attacker": self,
            "attacker_type": self.__class__.__name__,
            "weapon_type": best_weapon.get("type", "unknown") if best_weapon else "unknown",
            "learned_bonus": damage_bonus
        }
        
        # Наносим урон цели
        target.take_damage(damage_report)
        
        # Начинаем кулдаун атаки
        self.start_attack_cooldown()
        
        # Учимся на атаке
        self.learn_from_attack(damage_report, target)
        
        return damage_report
    
    def select_best_weapon_for_target(self, target) -> Optional[dict]:
        """Выбирает лучшее оружие для цели на основе обучения"""
        equipped_weapon = self.inventory_manager.equipment.get_equipped_item("weapon")
        if not equipped_weapon:
            return None
        
        # Проверяем, есть ли данные об эффективности оружия против этого типа врага
        target_type = getattr(target, 'enemy_type', 'unknown')
        weapon_type = getattr(equipped_weapon, 'item_type', 'unknown')
        
        if target_type in self.weapon_affinities and weapon_type in self.weapon_affinities[target_type]:
            # Используем обученные данные
            avg_damage = sum(self.weapon_affinities[target_type][weapon_type]) / len(self.weapon_affinities[target_type][weapon_type])
            if avg_damage > 15:  # Порог эффективности
                return {"type": weapon_type, "effectiveness": avg_damage}
        
        return {"type": weapon_type, "effectiveness": 10}  # Базовое значение
    
    def get_learned_damage_bonus(self, target) -> float:
        """Получает бонус к урону на основе обучения"""
        target_type = getattr(target, 'enemy_type', 'unknown')
        
        # Проверяем известные слабости
        for weakness in self.known_weaknesses:
            if target_type in weakness:
                return 5.0  # Бонус за знание слабости
        
        return 0.0
    
    def learn_from_attack(self, damage_report: dict, target):
        """Учится на атаке"""
        # Сохраняем опыт атаки
        self.ai_memory.record_event("attack_performed", damage_report)
        
        # Анализируем эффективность
        damage_dealt = damage_report.get("damage", 0)
        weapon_type = damage_report.get("weapon_type", "unknown")
        target_type = getattr(target, 'enemy_type', 'unknown')
        
        # Обновляем предпочтения оружия
        if weapon_type not in self.item_preferences:
            self.item_preferences[weapon_type] = 0
        
        if damage_dealt > 10:
            self.item_preferences[weapon_type] += 1
        else:
            self.item_preferences[weapon_type] = max(0, self.item_preferences[weapon_type] - 1)
    
    def use_item_intelligently(self):
        """Интеллектуально использует предметы"""
        # Проверяем здоровье
        health_percentage = self.get_health_percentage()
        if health_percentage < 0.3:
            # Ищем лечебные предметы
            consumables = self.inventory_manager.inventory.get_consumables()
            for item in consumables:
                if hasattr(item, 'effects') and 'heal' in item.effects:
                    self.use_consumable(item)
                    self.learn_item_usage(item, "healing")
                    break
        
        # Проверяем ману
        mana_percentage = self.get_mana_percentage()
        if mana_percentage < 0.2:
            # Ищем предметы для восстановления маны
            for item in self.inventory_manager.inventory.items:
                if hasattr(item, 'effects') and 'restore_mana' in item.effects:
                    self.use_consumable(item)
                    self.learn_item_usage(item, "mana_restoration")
                    break
    
    def learn_item_usage(self, item, usage_type: str):
        """Учится использованию предметов"""
        item_type = getattr(item, 'item_type', 'unknown')
        
        if item_type not in self.item_preferences:
            self.item_preferences[item_type] = 0
        
        # Увеличиваем предпочтение к этому типу предметов
        self.item_preferences[item_type] += 1
        
        # Сохраняем опыт использования
        self.ai_memory.record_event("item_used", {
            "item_type": item_type,
            "usage_type": usage_type,
            "effectiveness": 1.0
        })
    
    def can_attack(self) -> bool:
        """Может ли атаковать"""
        return self.attack_cooldown <= 0.0
    
    def start_attack_cooldown(self):
        """Начинает кулдаун атаки"""
        attack_speed = self.combat_stats_manager.get_stats().attack_speed
        self.attack_cooldown = 1.0 / attack_speed if attack_speed > 0 else 1.0
    
    def update(self, delta_time: float):
        """Обновляет сущность"""
        self.playtime += delta_time
        
        # Обновляем кулдаун атаки
        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0, self.attack_cooldown - delta_time)
        
        # Обновляем эффекты
        self.update_effects(delta_time)
        
        # Восстанавливаем ресурсы
        self.restore_resources(delta_time)
        
        # Обновляем AI
        self.update_ai(delta_time)
    
    def update_ai(self, delta_time: float):
        """Обновляет AI системы"""
        # Обновляем память
        self.ai_memory.update(delta_time)
        
        # Обновляем контроллер обучения
        self.learning_controller.update(delta_time)
        
        # Принимаем решения
        self.decision_maker.update(delta_time)
        
        # Анализируем паттерны
        self.pattern_recognizer.update(delta_time)
        
        # Обновляем систему обучения
        self.learning_system.update(delta_time)
    
    def update_effects(self, delta_time: float):
        """Обновляет активные эффекты"""
        expired_effects = []
        
        for effect_id, effect in self.active_effects.items():
            effect.update(delta_time)
            if effect.is_expired():
                expired_effects.append(effect_id)
        
        # Удаляем истекшие эффекты
        for effect_id in expired_effects:
            self.remove_effect(effect_id)
    
    def restore_resources(self, delta_time: float):
        """Восстанавливает ресурсы со временем"""
        # Восстановление выносливости
        stamina_regen = 10.0 * delta_time  # 10 в секунду
        self.combat_stats_manager.restore_stamina(stamina_regen)
        
        # Восстановление маны
        mana_regen = 5.0 * delta_time  # 5 в секунду
        self.combat_stats_manager.restore_mana(mana_regen)
    
    def add_effect(self, effect_id: str, effect_data: dict, stacks: int = 1):
        """Добавляет эффект"""
        if effect_id in self.active_effects:
            # Увеличиваем стаки существующего эффекта
            self.active_effects[effect_id].add_stacks(stacks)
        else:
            # Создаем новый эффект
            effect = Effect(effect_id, effect_data, self)
            effect.stacks = stacks
            self.active_effects[effect_id] = effect
    
    def remove_effect(self, effect_id: str):
        """Удаляет эффект"""
        if effect_id in self.active_effects:
            del self.active_effects[effect_id]
    
    def has_effect_tag(self, tag: str) -> bool:
        """Проверяет наличие эффекта с тегом"""
        return any(effect.has_tag(tag) for effect in self.active_effects.values())
    
    def distance_to(self, target) -> float:
        """Вычисляет расстояние до цели"""
        dx = self.position[0] - target.position[0]
        dy = self.position[1] - target.position[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def move_towards(self, target_pos: tuple, speed: float, delta_time: float):
        """Двигается к цели"""
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Нормализуем вектор направления
            dx /= distance
            dy /= distance
            
            # Вычисляем расстояние для движения
            move_distance = speed * delta_time
            
            # Ограничиваем движение расстоянием до цели
            if move_distance > distance:
                move_distance = distance
            
            # Обновляем позицию
            self.position[0] += dx * move_distance
            self.position[1] += dy * move_distance
    
    def die(self):
        """Смерть сущности"""
        self.alive = False
        # Сохраняем опыт смерти
        self.ai_memory.record_event("death", {"cause": "combat", "level": self.level})
    
    def use_consumable(self, item):
        """Использует расходник"""
        if hasattr(item, 'effects'):
            # Применяем эффекты предмета
            for effect_name, effect_value in item.effects.items():
                if effect_name == "heal":
                    self.combat_stats_manager.heal(effect_value)
                elif effect_name == "restore_mana":
                    self.combat_stats_manager.restore_mana(effect_value)
                elif effect_name == "restore_stamina":
                    self.combat_stats_manager.restore_stamina(effect_value)
            
            # Удаляем предмет из инвентаря
            self.inventory_manager.remove_item_from_inventory(item)
            
            # Учимся использованию предмета
            self.learn_item_usage(item, "consumable")
            return True
        return False
    
    # Свойства для удобного доступа к характеристикам
    @property
    def health(self) -> float:
        return self.combat_stats_manager.get_stats().health
    
    @health.setter
    def health(self, value: float):
        self.combat_stats_manager.get_stats().health = value
    
    @property
    def max_health(self) -> float:
        return self.combat_stats_manager.get_stats().max_health
    
    @property
    def mana(self) -> float:
        return self.combat_stats_manager.get_stats().mana
    
    @mana.setter
    def mana(self, value: float):
        self.combat_stats_manager.get_stats().mana = value
    
    @property
    def max_mana(self) -> float:
        return self.combat_stats_manager.get_stats().max_mana
    
    @property
    def stamina(self) -> float:
        return self.combat_stats_manager.get_stats().stamina
    
    @stamina.setter
    def stamina(self, value: float):
        self.combat_stats_manager.get_stats().stamina = value
    
    @property
    def max_stamina(self) -> float:
        return self.combat_stats_manager.get_stats().max_stamina
    
    @property
    def movement_speed(self) -> float:
        return self.combat_stats_manager.get_stats().movement_speed
    
    @movement_speed.setter
    def movement_speed(self, value: float):
        self.combat_stats_manager.get_stats().movement_speed = value
    
    @property
    def damage_output(self) -> float:
        return self.combat_stats_manager.get_stats().damage_output
    
    @damage_output.setter
    def damage_output(self, value: float):
        self.combat_stats_manager.get_stats().damage_output = value
    
    @property
    def defense(self) -> float:
        return self.combat_stats_manager.get_stats().defense
    
    @defense.setter
    def defense(self, value: float):
        self.combat_stats_manager.get_stats().defense = value
    
    def get_health_percentage(self) -> float:
        """Возвращает процент здоровья"""
        return self.combat_stats_manager.get_health_percentage()
    
    def get_mana_percentage(self) -> float:
        """Возвращает процент маны"""
        return self.combat_stats_manager.get_mana_percentage()
    
    def get_stamina_percentage(self) -> float:
        """Возвращает процент выносливости"""
        return self.combat_stats_manager.get_stamina_percentage()
