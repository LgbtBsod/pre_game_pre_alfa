import json
import os
from collections import defaultdict

def save_game(player, filename="game_save.json"):
    """
    Сохраняет состояние игрока в JSON-файл.
    
    :param player: объект Player
    :param filename: имя файла для сохранения
    """
    save_data = {
        "knowledge": {},
        "inventory": [],
        "level": player.level,
        "xp": player.xp
    }

    # Сохраняем знания (knowledge)
    for category, knowledge_dict in player.knowledge.items():
        save_data["knowledge"][category] = dict(knowledge_dict)

    # Сохраняем инвентарь
    for item in player.inventory:
        save_data["inventory"].append({
            "item_type": item.item_type,
            "power": item.power,
            "defense": item.defense,
            "effects": item.effects,
            "damage_type": item.damage_type,
            "weapon_type": item.weapon_type
        })

    # Сохраняем текущее состояние экипировки
    if player.equipped_weapon:
        save_data["equipped_weapon"] = {
            "item_type": player.equipped_weapon.item_type,
            "power": player.equipped_weapon.power,
            "damage_type": player.equipped_weapon.damage_type,
            "weapon_type": player.equipped_weapon.weapon_type
        }
    else:
        save_data["equipped_weapon"] = None

    if player.equipped_accessory:
        save_data["equipped_accessory"] = {
            "item_type": player.equipped_accessory.item_type,
            "defense": player.equipped_accessory.defense,
            "effects": player.equipped_accessory.effects
        }
    else:
        save_data["equipped_accessory"] = None

    # Сохраняем основные параметры игрока
    save_data["player_state"] = {
        "x": player.x,
        "y": player.y,
        "z": player.z,
        "health": player.health,
        "max_health": player.max_health,
        "attack_power": player.attack_power,
        "speed": player.speed
    }

    with open(filename, "w") as f:
        json.dump(save_data, f, indent=4)

def load_game(filename="game_save.json"):
    """
    Загружает игру из JSON-файла.
    
    :param filename: имя файла с сохранением
    :return: словарь с данными или None, если файл не найден
    """
    if not os.path.exists(filename):
        return None

    with open(filename, "r") as f:
        save_data = json.load(f)

    # Восстанавливаем знания
    knowledge = {}
    for category, values in save_data.get("knowledge", {}).items():
        knowledge[category] = defaultdict(float, values)

    # Восстанавливаем инвентарь
    from entities.item import Item
    inventory = []
    for item_data in save_data.get("inventory", []):
        item = Item(x=0, y=0, item_type=item_data["item_type"])
        item.power = item_data.get("power", 0)
        item.defense = item_data.get("defense", 0)
        item.effects = item_data.get("effects", {})
        item.damage_type = item_data.get("damage_type", "physical")
        item.weapon_type = item_data.get("weapon_type", "melee")
        inventory.append(item)

    # Восстанавливаем уровень и опыт
    player_level = save_data.get("level", 1)
    player_xp = save_data.get("xp", 0)

    # Восстанавливаем координаты игрока
    player_state = save_data.get("player_state", {})
    player_start = (
        player_state.get("x", 0),
        player_state.get("y", 0),
        player_state.get("z", 1)
    )

    return {
        "knowledge": knowledge,
        "inventory": inventory,
        "level": player_level,
        "xp": player_xp,
        "start_position": player_start
    }

def save_knowledge(knowledge, filename="knowledge.json"):
    """
    Сохраняет только знания ИИ в файл.
    
    :param knowledge: словарь знаний
    :param filename: имя файла
    """
    serializable_knowledge = {}
    for category, data in knowledge.items():
        serializable_knowledge[category] = dict(data)  # Преобразуем defaultdict в dict

    with open(filename, "w") as f:
        json.dump(serializable_knowledge, f, indent=4)

def load_knowledge(filename="knowledge.json"):
    """
    Загружает знания ИИ из файла.
    
    :param filename: имя файла
    :return: defaultdict знаний
    """
    if not os.path.exists(filename):
        return {}

    with open(filename, "r") as f:
        knowledge_data = json.load(f)

    knowledge = {}
    for category, values in knowledge_data.items():
        knowledge[category] = defaultdict(float, values)

    return knowledge

def save_inventory(inventory, filename="inventory.json"):
    """
    Сохраняет инвентарь в отдельный файл.
    
    :param inventory: список предметов
    :param filename: имя файла
    """
    inventory_data = []
    for item in inventory:
        inventory_data.append({
            "item_type": item.item_type,
            "power": item.power,
            "defense": item.defense,
            "effects": item.effects,
            "damage_type": item.damage_type,
            "weapon_type": item.weapon_type
        })

    with open(filename, "w") as f:
        json.dump(inventory_data, f, indent=4)

def load_inventory(filename="inventory.json"):
    """
    Загружает инвентарь из файла.
    
    :param filename: имя файла
    :return: список предметов
    """
    if not os.path.exists(filename):
        return []

    from entities.item import Item
    inventory = []
    with open(filename, "r") as f:
        items_data = json.load(f)

    for item_data in items_data:
        item = Item(x=0, y=0, item_type=item_data["item_type"])
        item.power = item_data.get("power", 0)
        item.defense = item_data.get("defense", 0)
        item.effects = item_data.get("effects", {})
        item.damage_type = item_data.get("damage_type", "physical")
        item.weapon_type = item_data.get("weapon_type", "melee")
        inventory.append(item)

    return inventory

def backup_save(data, filename="backup_save.json"):
    """
    Создаёт резервное копирование данных.
    
    :param data: данные для сохранения
    :param filename: имя файла
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_backup(filename="backup_save.json"):
    """
    Загружает резервную копию.
    
    :param filename: имя файла
    :return: данные из бэкапа
    """
    if not os.path.exists(filename):
        return None

    with open(filename, "r") as f:
        return json.load(f)