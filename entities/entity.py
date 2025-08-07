from typing import List, Tuple, Optional, Dict, Any
import random
import math
import time
from .effect import Effect

class Entity:
    def __init__(self, entity_id: str, position: Tuple[float, float] = (0, 0)):
        self.id = entity_id
        self.position = list(position)
        self.priority = 5
        self.level: int = 1
        self.experience: int = 0
        self.exp_to_next_level: int = 100
        self.attribute_points: int = 0
        self.currency: int = 0
        self.combat_style: str = "balanced"
        
        # Основные характеристики
        self.attributes: Dict[str, int] = {
            "strength": 10,     # Сила - увеличивает физический урон
            "dexterity": 10,    # Ловкость - увеличивает шанс крита и точность
            "intelligence": 10, # Интеллект - увеличивает магический урон
            "faith": 10,        # Вера - увеличивает силу священных/темных заклинаний
            "vitality": 10,     # Живучесть - увеличивает максимальное здоровье
            "endurance": 10,    # Выносливость - увеличивает максимальную стамину
            "luck": 10          # Удача - влияет на качество дропа, торговлю и редкие события
        }
        
        # Боевые характеристики
        self.combat_stats: Dict[str, float] = {
            # Базовые характеристики
            "physical_resist": 0.0,
            "fire_resist": 0.0,
            "ice_resist": 0.0,
            "lightning_resist": 0.0,
            "poison_resist": 0.0,
            "holy_resist": 0.0,
            "dark_resist": 0.0,
            
            # Шансы
            "parry_chance": 0.05,
            "block_chance": 0.1,
            "critical_chance": 0.05,
            "critical_damage": 1.5,  # Множитель критического урона
            
            # Проникающая способность
            "physical_penetration": 0.0,
            "fire_penetration": 0.0,
            "ice_penetration": 0.0,
            "lightning_penetration": 0.0,
            "poison_penetration": 0.0,
            "holy_penetration": 0.0,
            "dark_penetration": 0.0,
            
            # Модификаторы урона
            "physical_damage_mod": 1.0,
            "fire_damage_mod": 1.0,
            "ice_damage_mod": 1.0,
            "lightning_damage_mod": 1.0,
            "poison_damage_mod": 1.0,
            "holy_damage_mod": 1.0,
            "dark_damage_mod": 1.0,
            
            # Другие параметры
            "attack_range": 50.0,
            "movement_speed": 100.0,
            "life_steal": 0.0,  # Вампиризм - % урона в здоровье
            "mana_steal": 0.0   # % урона в ману
        }
        
        # Экипировка
        self.equipment: Dict[str, Optional[object]] = {
            "weapon": None,
            "shield": None,
            "head": None,
            "chest": None,
            "hands": None,
            "legs": None,
            "ring1": None,
            "ring2": None,
            "amulet": None
        }
        
        self.inventory: [List[object]] = []
        self.known_weaknesses: Dict[str, List[str]] = {}
        self.item_knowledge: Dict[str, Dict] = {}
        self.active_skills: List[str] = []
        self.passive_skills: List[str] = []
        
        # Ресурсы
        self.health: float = 100.0
        self.max_health: float = 100.0
        self.mana: float = 50.0
        self.max_mana: float = 50.0
        self.stamina: float = 100.0
        self.max_stamina: float = 100.0
        
        # Состояние
        self.alive: bool = True
        self.team: str = "NEUTRAL"
        self.elemental_affinity: str = "none"
        self.learning_rate: float = 1.0
        self.memory: Dict[str, Any] = {}
        self.target = None
        self.attack_cooldown: float = 0.0
        self.last_attacker = None
        self.skill_cooldowns: Dict[str, float] = {}
        
        # Система эффектов
        self.active_effects: Dict[str, Effect] = {}
        self.effect_tags: Dict[str, List[str]] = {}
        self.last_effect_update = time.time()
        
        # Расширенные атрибуты
        self.emotion = "NEUTRAL"
        self.genetic_profile = {}
        self.group_id = None
        self.role = "SOLO"
        self.combat_level = 1
        self.damage_output = 10
        self.ai_controller = None
        self.skills: Dict[str, Dict] = {}
        self.spells: Dict[str, Dict] = {}
        self.last_action_success = False
        self.last_health = self.max_health
        self.last_mana_used = 0
        self.last_damage_dealt = 0
        self.distance_to_player = float('inf')
        self.is_player = False
        self.is_boss = False
    
    # ========================
    # Основные методы
    # ========================
    
    def move_towards(self, target_pos: Tuple[float, float], speed: float, delta_time: float):
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
    
    def distance_to(self, target) -> float:
        """Расчитать расстояние до цели"""
        dx = target.position[0] - self.position[0]
        dy = target.position[1] - self.position[1]
        return math.sqrt(dx*dx + dy*dy)
    
    def learn_weakness(self, enemy_type: str, weakness: str):
        """Выучить слабость типа врага"""
        if enemy_type not in self.known_weaknesses:
            self.known_weaknesses[enemy_type] = []
        if weakness not in self.known_weaknesses[enemy_type]:
            self.known_weaknesses[enemy_type].append(weakness)
    
    def learn_item(self, item_id: str, properties: dict):
        """Запомнить свойства предмета"""
        self.item_knowledge[item_id] = properties
    
    def use_item(self, item):
        """Использовать предмет"""
        if item.id not in self.item_knowledge:
            properties = item.use(self)
            self.learn_item(item.id, properties)
        else:
            item.optimal_use(self, self.item_knowledge[item.id])
    
    def equip_item(self, item):
        """Экипировать предмет"""
        slot = item.equipment_slot
        if slot in self.equipment and self.equipment[slot]:
            self.unequip_item(slot)
        self.equipment[slot] = item
        item.apply_effects(self)
    
    def unequip_item(self, slot: str):
        """Снять предмет"""
        if slot in self.equipment and self.equipment[slot]:
            self.equipment[slot].remove_effects(self)
            self.equipment[slot] = None
    
    def update_derived_stats(self):
        """Обновить производные характеристики"""
        # Характеристики здоровья и ресурсов
        vitality = self.attributes["vitality"]
        endurance = self.attributes["endurance"]
        intelligence = self.attributes["intelligence"]
        
        self.max_health = 100 + vitality * 10
        self.max_stamina = 100 + endurance * 5
        self.max_mana = 50 + intelligence * 3
        
        # Рассчет с учетом эффектов
        self.health = min(self.calculate_stat_with_effects(self.max_health, "max_health"), self.health)
        self.stamina = min(self.calculate_stat_with_effects(self.max_stamina, "max_stamina"), self.stamina)
        self.mana = min(self.calculate_stat_with_effects(self.max_mana, "max_mana"), self.mana)
        
        # Боевые характеристики
        dexterity = self.attributes["dexterity"]
        luck = self.attributes["luck"]
        
        # Критический урон и шанс
        self.combat_stats["critical_chance"] = 0.05 + dexterity * 0.005
        self.combat_stats["critical_damage"] = 1.5 + luck * 0.01
        
        # Дальность атаки
        self.combat_stats["attack_range"] = 50.0 + dexterity * 0.2
        
        # Удача влияет на различные аспекты
        self.loot_quality_bonus = 1.0 + luck * 0.05
        self.gold_find_bonus = 1.0 + luck * 0.03
        self.merchant_prices_mod = 1.0 - min(0.5, luck * 0.01)  # Лучшие цены у торговцев
        
        # Сопротивления и проникновение (базовые значения)
        for element in ["fire", "ice", "lightning", "poison", "holy", "dark"]:
            self.combat_stats[f"{element}_resist"] = 0.0
            self.combat_stats[f"{element}_penetration"] = 0.0
            self.combat_stats[f"{element}_damage_mod"] = 1.0
    
    def gain_experience(self, amount: int):
        """Получить опыт"""
        # Удача влияет на получаемый опыт
        luck_bonus = self.attributes["luck"] * 0.02
        actual_amount = int(amount * (1.0 + luck_bonus))
        
        self.experience += actual_amount
        while self.experience >= self.exp_to_next_level:
            self.level_up()
    
    def level_up(self):
        """Повысить уровень"""
        self.level += 1
        self.experience -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        
        if self.is_player:
            self.attribute_points += 10
        elif self.is_boss:
            self.attribute_points += 10
        else:
            self.attribute_points += 5
        
        self.update_derived_stats()
    
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
        
        weapon = self.equipment.get("weapon")
        if not weapon:
            return None
        
        from combat.damage_system import DamageSystem
        if self.distance_to(target) <= self.combat_stats["attack_range"]:
            damage_report = DamageSystem.calculate_damage(self, target, weapon)
            target.take_damage(damage_report)
            target.last_attacker = self
            self.attack_cooldown = 1.0 / weapon.attack_speed
            
            # Вампиризм
            self.apply_life_steal(damage_report["total"])
            
            # Обучение на основе атаки
            if hasattr(self, 'learning_system'):
                self.learning_system.on_attack(target, damage_report)
            
            return damage_report
        return None
    
    def apply_life_steal(self, damage_amount: float):
        """Применить эффект вампиризма"""
        life_steal = self.combat_stats["life_steal"]
        if life_steal > 0:
            heal_amount = damage_amount * life_steal
            self.health = min(self.max_health, self.health + heal_amount)
        
        mana_steal = self.combat_stats["mana_steal"]
        if mana_steal > 0:
            restore_amount = damage_amount * mana_steal
            self.mana = min(self.max_mana, self.mana + restore_amount)
    
    # ========================
    # Методы для эффектов
    # ========================
    
    def add_effect(self, effect_id: str, effect_data: Dict[str, Any], stacks: int = 1):
        """Добавить эффект к сущности"""
        from .effect import Effect
        
        if effect_id in self.active_effects:
            # Увеличиваем стаки или обновляем время
            effect = self.active_effects[effect_id]
            max_stacks = effect_data.get('max_stacks', 1)
            effect.stacks = min(max_stacks, effect.stacks + stacks)
            effect.start_time = time.time()
        else:
            # Создаем новый эффект
            effect = Effect(effect_id, effect_data.get('tags', []), effect_data.get('modifiers', []))
            effect.stacks = min(effect_data.get('max_stacks', 1), stacks)
            effect.apply(self, True)
            self.active_effects[effect_id] = effect
            
            # Обновляем теги
            for tag in effect.tags:
                if tag not in self.effect_tags:
                    self.effect_tags[tag] = []
                self.effect_tags[tag].append(effect_id)
    
    def remove_effect(self, effect_id: str):
        """Удалить эффект с сущности"""
        if effect_id in self.active_effects:
            effect = self.active_effects[effect_id]
            effect.apply(self, False)
            del self.active_effects[effect_id]
            
            # Обновляем теги
            for tag in effect.tags:
                if tag in self.effect_tags and effect_id in self.effect_tags[tag]:
                    self.effect_tags[tag].remove(effect_id)
                    if not self.effect_tags[tag]:
                        del self.effect_tags[tag]
    
    def has_effect_tag(self, tag: str) -> bool:
        """Проверить наличие эффекта по тегу"""
        return tag in self.effect_tags
    
    def update_effects(self, delta_time: float):
        """Обновить состояние эффектов"""
        current_time = time.time()
        to_remove = []
        
        for effect_id, effect in list(self.active_effects.items()):
            # Проверка истечения времени
            if effect.is_expired():
                to_remove.append(effect_id)
            else:
                # Обработка периодических эффектов
                effect.process_tick(self, delta_time)
        
        for effect_id in to_remove:
            self.remove_effect(effect_id)
    
    def calculate_stat_with_effects(self, base_value: float, stat_name: str) -> float:
        """Рассчитать значение характеристики с учетом эффектов"""
        value = base_value
        
        # Применяем аддитивные модификаторы
        for effect in self.active_effects.values():
            for modifier in effect.modifiers:
                if modifier['attribute'] == stat_name and modifier['mode'] == 'add':
                    value += modifier['value'] * effect.stacks
        
        # Применяем мультипликативные модификаторы
        multiplier = 1.0
        for effect in self.active_effects.values():
            for modifier in effect.modifiers:
                if modifier['attribute'] == stat_name and modifier['mode'] == 'multiply':
                    multiplier *= modifier['value']
        
        return value * multiplier
    
    # ========================
    # Методы для лута и торговли
    # ========================
    
    def calculate_loot_quality(self, base_quality: float) -> float:
        """Рассчитать качество лута с учетом удачи"""
        luck = self.attributes["luck"]
        quality_mod = 1.0 + luck * 0.05
        return base_quality * quality_mod
    
    def calculate_gold_amount(self, base_amount: int) -> int:
        """Рассчитать количество золота с учетом удачи"""
        luck = self.attributes["luck"]
        gold_mod = 1.0 + luck * 0.03
        return int(base_amount * gold_mod)
    
    def get_merchant_price_modifier(self) -> float:
        """Получить модификатор цен у торговцев"""
        luck = self.attributes["luck"]
        return max(0.5, 1.0 - luck * 0.01)
    
    def find_rare_item(self, item_pool: list) -> Optional[object]:
        """Найти редкий предмет в пуле с учетом удачи"""
        luck = self.attributes["luck"]
        
        # Шанс найти редкий предмет
        rare_chance = min(0.3, 0.01 + luck * 0.005)
        
        if random.random() < rare_chance:
            # Фильтруем редкие предметы
            rare_items = [item for item in item_pool if item.rarity == "RARE"]
            if rare_items:
                return random.choice(rare_items)
        
        # Если редкий предмет не найден, возвращаем случайный обычный
        return random.choice(item_pool) if item_pool else None
    
    # ========================
    # Методы для ИИ и способностей
    # ========================
    
    def get_nearby_entities(self, radius: float, enemy_only: bool = False) -> List['Entity']:
        """Получить ближайшие сущности в радиусе"""
        # Заглушка - в реальной игре будет пространственное разбиение
        return []
    
    def attack_nearest(self):
        """Атаковать ближайшего врага"""
        nearest = self.find_nearest_enemy()
        if nearest:
            self.attack(nearest)
    
    def find_nearest_enemy(self) -> Optional['Entity']:
        """Найти ближайшего врага"""
        enemies = self.get_nearby_entities(radius=20.0, enemy_only=True)
        if not enemies:
            return None
        return min(enemies, key=lambda e: self.distance_to(e))
    
    def defend(self):
        """Перейти в защитную стойку"""
        # Добавляем эффект защиты
        if not self.has_effect_tag("defending"):
            self.add_effect("defense_stance", {
                "tags": ["defense", "buff"],
                "modifiers": [
                    {
                        "attribute": "physical_resist",
                        "value": 0.3,
                        "mode": "add"
                    },
                    {
                        "attribute": "movement_speed",
                        "value": 0.7,
                        "mode": "multiply"
                    }
                ],
                "duration": 5.0
            })
    
    def use_best_healing_item(self):
        """Использовать лучший лечащий предмет"""
        healing_items = [item for item in self.inventory if "heal" in item.tags]
        if healing_items:
            best_item = max(healing_items, key=lambda item: item.heal_power)
            self.use_item(best_item)
    
    def flee_from_danger(self):
        """Бежать от опасности"""
        # Добавляем эффект бегства
        self.add_effect("fleeing", {
            "tags": ["movement", "buff"],
            "modifiers": [
                {
                    "attribute": "movement_speed",
                    "value": 1.3,
                    "mode": "multiply"
                },
                {
                    "attribute": "physical_resist",
                    "value": -0.2,
                    "mode": "add"
                }
            ],
            "duration": 10.0
        })
    
    def cast_spell(self, spell_name: str):
        """Произнести заклинание"""
        if spell_name in self.spells:
            spell_data = self.spells[spell_name]
            mana_cost = spell_data.get('mana_cost', 0)
            
            if self.mana >= mana_cost:
                self.mana -= mana_cost
                self.last_mana_used = mana_cost
                
                # Применение эффектов заклинания
                for effect_id in spell_data.get('effects', []):
                    self.add_effect(effect_id, spell_data['effects'][effect_id])
                
                # Установка перезарядки
                cooldown = spell_data.get('cooldown', 0)
                if cooldown > 0:
                    self.skill_cooldowns[spell_name] = time.time() + cooldown
    
    def has_healing_abilities(self) -> bool:
        """Имеет ли целительные способности"""
        return "HEAL" in self.skills or "RESTORE" in self.spells
    
    def use_skill(self, skill_name: str):
        """Использовать способность"""
        if skill_name in self.skills:
            skill_data = self.skills[skill_name]
            stamina_cost = skill_data.get('stamina_cost', 0)
            
            if self.stamina >= stamina_cost:
                self.stamina -= stamina_cost
                
                # Применение эффектов способности
                for effect_id in skill_data.get('effects', []):
                    self.add_effect(effect_id, skill_data['effects'][effect_id])
                
                # Установка перезарядки
                cooldown = skill_data.get('cooldown', 0)
                if cooldown > 0:
                    self.skill_cooldowns[skill_name] = time.time() + cooldown
    
    def move_in_direction(self, direction: Tuple[float, float]):
        """Двигаться в заданном направлении"""
        dx, dy = direction
        distance = max(0.1, math.sqrt(dx*dx + dy*dy))
        dx /= distance
        dy /= distance
        
        actual_speed = self.calculate_stat_with_effects(
            self.combat_stats["movement_speed"], 
            "movement_speed"
        )
        
        self.position[0] += dx * actual_speed * 0.1
        self.position[1] += dy * actual_speed * 0.1
    
    def calculate_elemental_damage(self, base_damage: float, element: str) -> float:
        """Рассчитать урон с учетом стихийных модификаторов"""
        damage_mod = self.combat_stats.get(f"{element}_damage_mod", 1.0)
        return base_damage * damage_mod
    
    def get_elemental_penetration(self, element: str) -> float:
        """Получить значение проникновения для стихии"""
        return self.combat_stats.get(f"{element}_penetration", 0.0)