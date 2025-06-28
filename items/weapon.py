import random
from enum import Enum
import json
import trace

class WeaponType(Enum):
    SWORD = "Меч"
    DAGGER = "Кинжал"
    HAMMER = "Молот"
    AXE = "Топор"
    SPEAR = "Копье"
    HALBERD = "Алебарда"
    GREATSWORD = "Двуручный меч"
    GREATHAMMER = "Двуручный молот"
    BOW = "Лук"
    CROSSBOW = "Арбалет"
    MUSKET = "Мушкет"
    STAFF = "Посох"

class DamageType(Enum):
    PHYSICAL = "physical"
    SLASHING = "slashing"
    PIERCING = "piercing"
    BLUDGEONING = "bludgeoning"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"
    HOLY = "holy"
    DARK = "dark"

class Weapon:
    def __init__(self, weapon_id: str):
        self.id = weapon_id
        self.name: str = ""
        self.weapon_type: WeaponType = WeaponType.SWORD
        self.damage_types: list = []
        self.range: float = 1.0
        self.attack_speed: float = 1.0
        self.critical_chance: float = 0.05
        self.elemental_affinity: str = "none"
        self.requirements: dict = {}
        self.special_effects: list = []
        self.durability: int = 100
        self.equipment_slot = "weapon"
        
        # Правильные атрибуты для эффектов
        self.on_hit_effects: list = []  # Эффекты при попадании
        self.equip_effects: list = []   # Эффекты при экипировке
    
    def apply_effects(self, entity):
        """Применить эффекты экипировки к сущности"""
        for effect in self.equip_effects:
            entity.add_effect(effect['id'], effect['data'])
    
    def remove_effects(self, entity):
        """Удалить эффекты экипировки с сущности"""
        for effect in self.equip_effects:
            entity.remove_effect(effect['id'])
    
    def add_on_hit_effect(self, effect_id: str, effect_data: dict):
        """Добавить эффект при попадании"""
        self.on_hit_effects.append({
            'id': effect_id,
            'data': effect_data
        })
    
    def add_equip_effect(self, effect_id: str, effect_data: dict):
        """Добавить эффект при экипировке"""
        self.equip_effects.append({
            'id': effect_id,
            'data': effect_data
        })
    
    def use(self, entity):
        """Использование оружия в бою"""
        properties = self.get_properties()
        return properties
    
    def get_properties(self):
        return {
            "damage_types": self.damage_types,
            "range": self.range,
            "elemental_affinity": self.elemental_affinity,
            "on_hit_effects": [e['id'] for e in self.on_hit_effects],
            "equip_effects": [e['id'] for e in self.equip_effects]
        }
        
import json
import random
import traceback
import os

class WeaponGenerator:
    _effects_data = None
    
    @classmethod
    def _load_effects(cls):
        """Загрузить эффекты из JSON с обработкой ошибок"""
        if cls._effects_data is not None:
            return cls._effects_data
        
        file_path = "data/effects.json"
        
        try:
            # Проверка существования файла
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Файл {file_path} не найден")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                cls._effects_data = json.load(f)
            return cls._effects_data
        except Exception as e:
            print(f"Ошибка загрузки effects.json: {str(e)}")
            traceback.print_exc()
            
            # Возвращаем минимальный набор эффектов
            return {
                "bleed": {
                    "name": "Кровотечение",
                    "tags": ["dot"],
                    "modifiers": [
                        {
                            "attribute": "health",
                            "value": "-5/1",
                            "mode": "add",
                            "duration": 10,
                            "interval": 1
                        }
                    ]
                },
                "burn": {
                    "name": "Горение",
                    "tags": ["dot"],
                    "modifiers": [
                        {
                            "attribute": "health",
                            "value": "-3/1",
                            "mode": "add",
                            "duration": 5,
                            "interval": 1
                        }
                    ]
                }
            }
    
    @staticmethod
    def generate_weapon(level: int, enemy_type: str = None):
        """Генерация случайного оружия с эффектами"""
        weapon = Weapon(f"weapon_{random.randint(10000, 99999)}")
        
        # Базовые характеристики
        base_damage = 10 + level * 3
        weapon.range = 1.0 + (level * 0.1)
        weapon.attack_speed = max(0.5, 1.2 - (level * 0.05))
        weapon.critical_chance = min(0.3, 0.05 + (level * 0.01))
        
        # Типы урона
        damage_types = []
        physical_types = [DamageType.PHYSICAL, DamageType.SLASHING, 
                         DamageType.PIERCING, DamageType.BLUDGEONING]
        elemental_types = [DamageType.FIRE, DamageType.ICE, 
                          DamageType.LIGHTNING, DamageType.POISON]
        
        # Основной урон
        main_type = random.choice(physical_types)
        damage_types.append({"type": main_type, "value": base_damage * 0.8})
        
        # Дополнительный стихийный урон
        if random.random() > 0.5:
            element_type = random.choice(elemental_types)
            damage_types.append({"type": element_type, "value": base_damage * 0.4})
            weapon.elemental_affinity = element_type.value
        
        weapon.damage_types = damage_types
        
        # Название оружия
        prefixes = ["Старый", "Прочный", "Зачарованный", "Редкий", "Эпический"]
        suffixes = ["Разрушитель", "Гибель врагов", "Ярости", "Превосходства"]
        weapon.name = f"{random.choice(prefixes)} {weapon.weapon_type.value} {random.choice(suffixes)}"
        
        # Загружаем эффекты
        effects_data = WeaponGenerator._load_effects()
        
        # Простая защита на случай отсутствия эффектов
        if not effects_data:
            return weapon
        
        try:
            # Эффекты при попадании (40% шанс)
            if random.random() < 0.4:
                eligible_effects = [
                    eff_id for eff_id, eff_data in effects_data.items()
                    if any(tag in eff_data.get('tags', []) for tag in ['dot', 'debuff'])
                ]
                
                if eligible_effects:
                    effect_id = random.choice(eligible_effects)
                    weapon.add_on_hit_effect(effect_id, effects_data[effect_id])
                    weapon.special_effects.append(effects_data[effect_id].get('name', effect_id))
            
            # Эффекты при экипировке (30% шанс)
            if random.random() < 0.3:
                eligible_effects = [
                    eff_id for eff_id, eff_data in effects_data.items()
                    if any(tag in eff_data.get('tags', []) for tag in ['buff', 'enhancement'])
                ]
                
                if eligible_effects:
                    effect_id = random.choice(eligible_effects)
                    weapon.add_equip_effect(effect_id, effects_data[effect_id])
                    weapon.special_effects.append(effects_data[effect_id].get('name', effect_id))
        except Exception as e:
            print(f"Ошибка добавления эффектов к оружию: {str(e)}")
            traceback.print_exc()
        
        return weapon