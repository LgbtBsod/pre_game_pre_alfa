from collections import defaultdict
import random

class Entity:
    def __init__(self, x, y, learning_rate=0.01):
        self.x = x
        self.y = y
        self.z = 0.5  # высота по умолчанию
        self.learning_rate = learning_rate

        # Система знаний
        self.knowledge = {
            "enemies": defaultdict(float),
            "traps": defaultdict(float),
            "items": defaultdict(float),
            "weapon_effect": defaultdict(float),
            "damage_resist": defaultdict(float)
        }

        self.inventory = []

    def learn(self, category, entity_type, value):
        if category not in self.knowledge:
            self.knowledge[category] = defaultdict(float)
        self.knowledge[category][entity_type] += self.learning_rate * value
        self.knowledge[category][entity_type] = max(0.0, min(1.0, self.knowledge[category][entity_type]))

    def add_item(self, item):
        """Добавляет предмет в инвентарь"""
        self.inventory.append(item)

    def use_item(self):
        """Использует первый подходящий предмет из инвентаря"""
        for item in self.inventory:
            if item.can_use():
                result = item.use(self)
                if result:
                    self.inventory.remove(item)
                return True
        return False

    def drop_items(self):
        """Возвращает список выпавших предметов при смерти"""
        return []

    def distance_to(self, other):
        """Вычисляет расстояние до другой сущности"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, learning_rate=1.0)

        # Характеристики игрока
        self.health = 100
        self.max_health = 100
        self.attack_power = 10
        self.speed = 0.05
        self.level = 1
        self.xp = 0
        self.xp_to_level = 100
        self.equipped_weapon = None
        self.equipped_accessory = None

        # Статусные эффекты
        self.cooldown = 0
        self.poisoned = 0
        self.buffed = 0

    def equip_best(self):
        """Автоматически экипирует лучшее оружие и аксессуар"""
        weapon_types = ["sword", "bow", "axe", "staff"]
        accessory_types = ["shield", "amulet", "ring"]

        for item in self.inventory:
            if item.item_type in weapon_types and (
                not self.equipped_weapon or item.power > self.equipped_weapon.power
            ):
                self.equipped_weapon = item
            elif item.item_type in accessory_types and (
                not self.equipped_accessory or item.defense > self.equipped_accessory.defense
            ):
                self.equipped_accessory = item

    def gain_xp(self, amount):
        """Получение опыта и повышение уровня"""
        self.xp += amount
        while self.xp >= self.xp_to_level:
            self.level_up()

    def level_up(self):
        """Повышение уровня"""
        self.level += 1
        self.xp -= self.xp_to_level
        self.xp_to_level = int(self.xp_to_level * 1.5)
        self.max_health += 20
        self.health = self.max_health
        self.attack_power += 5

    def take_damage(self, amount, damage_type="physical"):
        """Получение урона с учётом защиты и сопротивления"""
        resistance = self.knowledge["damage_resist"].get(damage_type, 0)
        actual_damage = amount * (1 - resistance)

        self.health -= actual_damage
        return self.health <= 0


class Enemy(Entity):
    def __init__(self, x, y, enemy_type="warrior"):
        super().__init__(x, y, learning_rate=0.01)

        # Базовые параметры
        self.enemy_type = enemy_type
        self.health = 50
        self.damage = 5
        self.speed = 0.03
        self.resistances = {}
        self.weaknesses = {}

        # Инициализация характеристик по типу
        if enemy_type == "warrior":
            self.health = 70
            self.damage = 8
            self.resistances["physical"] = 0.3
            self.weaknesses["magic"] = 0.5
            self.add_item(Item("health_potion"))
        elif enemy_type == "mage":
            self.health = 40
            self.damage = 10
            self.resistances["magic"] = 0.6
            self.weaknesses["physical"] = 0.4
            self.add_item(Item("mana_potion"))

    def update(self, player, enemies):
        """Логика обновления врага"""
        dist = self.distance_to(player)
        if dist < 1.5 and self.cooldown == 0:
            player.take_damage(self.damage, "physical")
            self.cooldown = 30

        if self.health < self.max_health * 0.3:
            self.use_item()

    def take_damage(self, amount, damage_type="physical"):
        """Нанесение урона с учетом сопротивления/слабостей"""
        resistance = self.resistances.get(damage_type, 0)
        weakness = self.weaknesses.get(damage_type, 0)
        actual_damage = amount * (1 - resistance) * (1 + weakness)
        self.health -= actual_damage
        return self.health <= 0

    def drop_items(self):
        """Выпадение случайного предмета при смерти"""
        drops = []
        if random.random() < 0.5:
            item_types = ["health_potion", "xp_potion", "minor_attack_boost"]
            drops.append(Item(random.choice(item_types)))
        return drops


class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, enemy_type="boss")
        self.learning_rate = 0.001
        self.phase = 1
        self.health = 200
        self.damage = 15
        self.speed = 0.02
        self.resistances = {"physical": 0.4, "magic": 0.3}
        self.weaknesses = {"fire": 0.5}

    def update(self, player):
        """Сложная логика босса с фазами и обучением"""
        health_ratio = self.health / 200
        distance = self.distance_to(player)

        # Фазы
        if self.health < 150 and self.phase == 1:
            self.phase = 2
            self.speed *= 1.5
        elif self.health < 75 and self.phase == 2:
            self.phase = 3
            self.damage *= 1.5

        # Простое ИИ решение
        if health_ratio < 0.5:
            self.take_damage(1)  # Тестовое действие — можно заменить на AI
        else:
            self.x += (player.x - self.x) * self.speed
            self.y += (player.y - self.y) * self.speed

    def drop_items(self):
        """Выпадение редких предметов при смерти босса"""
        drops = [
            Item("legendary_sword", power=20, effects={"buff": 300}),
            Item("ancient_amulet", defense=0.4, effects={"resistance": {"physical": 0.3}})
        ]
        if random.random() < 0.3:
            drops.append(Item("rare_artifact", effects={"xp_gain": 2}))
        return drops


class Item:
    def __init__(self, item_type, power=0, defense=0, effects=None):
        self.item_type = item_type
        self.power = power
        self.defense = defense
        self.effects = effects or {}

    def can_use(self):
        """Можно ли использовать этот предмет"""
        return self.item_type in ["health_potion", "mana_potion", "buff_potion"]

    def use(self, user):
        """Применяет эффект предмета к пользователю"""
        if self.item_type == "health_potion":
            user.health = min(user.max_health, user.health + 30)
        elif self.item_type == "mana_potion":
            user.mana = getattr(user, "mana", 0) + 50
        elif self.item_type == "buff_potion":
            user.buffed = getattr(user, "buffed", 0) + 300  # 5 секунд
        elif "attack" in self.effects:
            user.attack_power += self.effects["attack"]
        elif "resistance" in self.effects:
            for dmg_type, value in self.effects["resistance"].items():
                current = user.knowledge["damage_resist"].get(dmg_type, 0)
                user.knowledge["damage_resist"][dmg_type] = min(0.8, current + value)
        else:
            return False
        return True