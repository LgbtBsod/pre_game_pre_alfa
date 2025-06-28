import json
import random
import pickle
from collections import defaultdict

class Item:
    def __init__(self, x, y, item_type="health", rarity=None):
        # Координаты
        self.x, self.y, self.z = x, y, 0.5
        
        # Базовые атрибуты
        self.item_type = item_type
        self.power = 0
        self.defense = 0
        self.effects = {}
        self.cost = 0
        self.rarity = rarity if rarity is not None else 1
        self.stackable = False
        
        # Загрузка данных из JSON
        with open("data/items.json") as f:
            data = json.load(f)
        
        # Инициализация из JSON
        self._load_from_data(data)

    def _load_from_data(self, data):
        """Загрузка параметров из JSON"""
        # Поиск в weapon_types
        for weapon_category in data["weapon_types"]:
            if self.item_type in data["weapon_types"][weapon_category]:
                stats = data["weapon_types"][weapon_category][self.item_type]
                self.power = stats.get("base_damage", 0)
                self.effects = stats.get("effects", {})
                self.cost = stats.get("cost", 0)
                self.rarity = stats.get("rarity", 1)
                self.element = stats.get("element", "none")
                self.damage_type = stats.get("damage_type", "physical")
                self.resist_mod = stats.get("resist_mod", {})
                self.weakness_mod = stats.get("weakness_mod", {})
                return
        
        # Поиск в accessory_types
        for accessory_type in data["accessory_types"]:
            if self.item_type in data["accessory_types"][accessory_type]:
                stats = data["accessory_types"][accessory_type][self.item_type]
                self.defense = stats.get("defense", 0)
                self.effects = stats.get("effects", {})
                self.cost = stats.get("cost", 0)
                self.rarity = stats.get("rarity", 1)
                return
        
        # Поиск в consumable_types
        for consumable_type in data["consumable_types"]:
            if self.item_type in data["consumable_types"][consumable_type]:
                stats = data["consumable_types"][consumable_type][self.item_type]
                self.effects = stats.get("effects", {})
                self.cost = stats.get("cost", 0)
                self.rarity = stats.get("rarity", 1)
                self.stackable = True
                return
        
        # По умолчанию (золото)
        if self.item_type == "gold_coins":
            self.effects = {"currency": random.randint(5, 20)}
            self.cost = self.effects["currency"]
            self.rarity = 1
            self.stackable = True

    def use(self, user):
        """Использование предмета"""
        print(f"Использовано {self.item_type}")
        
        # Применение эффектов
        for effect, value in self.effects.items():
            if effect == "heal":
                user.health = min(user.max_health, user.health + value)
                print(f"Здоровье восстановлено на {value}. Теперь: {user.health}")
            elif effect == "currency":
                user.gain_currency(value)
            elif effect == "regen_health":
                user.effects["regen_health"] = 300  # 5 секунд регена
            elif effect == "boost_damage":
                user.attack_power *= 1.2
                user.effects["boost_damage"] = 200  # 3 секунды буста
        
        return True

    @staticmethod
    def generate_gold(x, y, amount=10):
        """Генерация золотых монет"""
        gold = Item(x, y, "gold_coins")
        gold.effects["currency"] = amount
        gold.cost = amount
        gold.rarity = 1
        gold.stackable = True
        return gold

    @staticmethod
    def generate_random_item(rarity="common"):
        """Генерация случайного предмета"""
        rarity_weights = {
            "common": [1, 1, 1],
            "uncommon": [1, 2, 1],
            "epic": [1, 1, 2]
        }
        item_types = ["sword", "bow", "axe", "staff", "shield", "amulet", "ring", "health", "xp"]
        return Item(0, 0, random.choice(item_types))

    @staticmethod
    def generate_random_weapon(rarity="uncommon"):
        """Генерация случайного оружия"""
        with open("data/items.json") as f:
            data = json.load(f)
        
        weapon_types = []
        for category in data["weapon_types"]:
            weapon_types.extend(data["weapon_types"][category].keys())
        
        weapon_type = random.choice(weapon_types)
        return Item(0, 0, weapon_type)

    def save(self):
        """Сохранение состояния предмета"""
        state = {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "item_type": self.item_type,
            "power": self.power,
            "defense": self.defense,
            "effects": self.effects,
            "cost": self.cost,
            "rarity": self.rarity
        }
        return pickle.dumps(state)

    def load(self, data):
        """Загрузка состояния предмета"""
        state = pickle.loads(data)
        self.x = state["x"]
        self.y = state["y"]
        self.z = state["z"]
        self.item_type = state["item_type"]
        self.power = state["power"]
        self.defense = state["defense"]
        self.effects = state["effects"]
        self.cost = state["cost"]
        self.rarity = state["rarity"]

