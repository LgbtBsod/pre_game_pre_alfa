#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import time
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum

class DialogueType(Enum):
    """Типы диалогов"""
    GREETING = "greeting"       # Приветствие
    QUEST = "quest"            # Квест
    TRADE = "trade"            # Торговля
    STORY = "story"            # История
    FLIRT = "flirt"            # Флирт
    THREAT = "threat"          # Угроза
    PERSUASION = "persuasion"  # Убеждение

class QuestType(Enum):
    """Типы квестов"""
    KILL = "kill"              # Убить врагов
    COLLECT = "collect"        # Собрать предметы
    DELIVER = "deliver"        # Доставить предмет
    ESCORT = "escort"          # Сопроводить NPC
    EXPLORE = "explore"        # Исследовать место
    CRAFT = "craft"            # Создать предмет
    SOCIAL = "social"          # Социальное взаимодействие

class QuestStatus(Enum):
    """Статусы квестов"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TradeType(Enum):
    """Типы торговли"""
    BUY = "buy"                # Покупка
    SELL = "sell"              # Продажа
    TRADE = "trade"            # Обмен
    REPAIR = "repair"          # Ремонт
    ENCHANT = "enchant"        # Зачарование

@dataclass
class DialogueOption:
    """Вариант ответа в диалоге"""
    option_id: str
    text: str
    next_dialogue: str
    requirements: Dict[str, Any] = field(default_factory=dict)
    consequences: Dict[str, Any] = field(default_factory=dict)
    reputation_change: int = 0

@dataclass
class Dialogue:
    """Диалог"""
    dialogue_id: str
    npc_id: str
    text: str
    options: List[DialogueOption]
    dialogue_type: DialogueType
    requirements: Dict[str, Any] = field(default_factory=dict)
    reputation_requirement: int = 0

@dataclass
class Quest:
    """Квест"""
    quest_id: str
    name: str
    description: str
    quest_type: QuestType
    objectives: List[Dict[str, Any]]
    rewards: Dict[str, Any]
    requirements: Dict[str, Any] = field(default_factory=dict)
    time_limit: float = -1.0  # -1 для квестов без ограничения времени
    reputation_reward: int = 0
    experience_reward: int = 0
    status: QuestStatus = QuestStatus.NOT_STARTED
    start_time: float = 0.0
    completion_time: float = 0.0

@dataclass
class TradeItem:
    """Торговый предмет"""
    item_id: str
    name: str
    description: str
    buy_price: int
    sell_price: int
    quantity: int = 1
    max_quantity: int = 999
    trade_type: TradeType = TradeType.BUY
    requirements: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NPC:
    """NPC"""
    npc_id: str
    name: str
    npc_type: str
    dialogues: Dict[str, Dialogue]
    quests: Dict[str, Quest]
    trade_items: Dict[str, TradeItem]
    reputation: int = 0
    max_reputation: int = 100
    min_reputation: int = -100
    location: Tuple[float, float, float] = (0, 0, 0)
    schedule: Dict[str, Any] = field(default_factory=dict)

class DialogueSystem:
    """Система диалогов"""
    
    def __init__(self):
        self.npcs: Dict[str, NPC] = {}
        self.active_dialogues: Dict[str, Dict[str, Any]] = {}
        self.dialogue_history: Dict[str, List[str]] = {}
        
        # Инициализация NPC и диалогов
        self._initialize_npcs()
    
    def _initialize_npcs(self):
        """Инициализация NPC"""
        # Торговец
        merchant = NPC(
            npc_id="merchant",
            name="Merchant",
            npc_type="merchant",
            dialogues={},
            quests={},
            trade_items={},
            reputation=0
        )
        
        # Создаем диалоги для торговца
        greeting_dialogue = Dialogue(
            dialogue_id="merchant_greeting",
            npc_id="merchant",
            text="Welcome to my shop! What can I help you with today?",
            options=[
                DialogueOption("trade", "I want to trade", "merchant_trade", reputation_change=0),
                DialogueOption("quest", "Do you have any work?", "merchant_quest", reputation_change=0),
                DialogueOption("goodbye", "Goodbye", "end", reputation_change=0)
            ],
            dialogue_type=DialogueType.GREETING
        )
        
        trade_dialogue = Dialogue(
            dialogue_id="merchant_trade",
            npc_id="merchant",
            text="I have many fine goods for sale. What interests you?",
            options=[
                DialogueOption("weapons", "Show me weapons", "merchant_weapons", reputation_change=0),
                DialogueOption("armor", "Show me armor", "merchant_armor", reputation_change=0),
                DialogueOption("potions", "Show me potions", "merchant_potions", reputation_change=0),
                DialogueOption("back", "Back to main menu", "merchant_greeting", reputation_change=0)
            ],
            dialogue_type=DialogueType.TRADE
        )
        
        merchant.dialogues["greeting"] = greeting_dialogue
        merchant.dialogues["trade"] = trade_dialogue
        
        # Квестодатель
        quest_giver = NPC(
            npc_id="quest_giver",
            name="Village Elder",
            npc_type="quest_giver",
            dialogues={},
            quests={},
            trade_items={},
            reputation=0
        )
        
        quest_dialogue = Dialogue(
            dialogue_id="quest_giver_greeting",
            npc_id="quest_giver",
            text="Greetings, young adventurer. Our village needs help.",
            options=[
                DialogueOption("quest", "I'm here to help", "quest_giver_available", reputation_change=5),
                DialogueOption("story", "Tell me about this place", "quest_giver_story", reputation_change=2),
                DialogueOption("goodbye", "I'll be going", "end", reputation_change=-1)
            ],
            dialogue_type=DialogueType.QUEST
        )
        
        quest_giver.dialogues["greeting"] = quest_dialogue
        
        self.npcs["merchant"] = merchant
        self.npcs["quest_giver"] = quest_giver
    
    def start_dialogue(self, player_id: str, npc_id: str, dialogue_id: str = "greeting") -> Optional[Dialogue]:
        """Начало диалога"""
        if npc_id not in self.npcs:
            return None
        
        npc = self.npcs[npc_id]
        if dialogue_id not in npc.dialogues:
            return None
        
        dialogue = npc.dialogues[dialogue_id]
        
        # Проверяем требования
        if not self._check_dialogue_requirements(player_id, dialogue):
            return None
        
        # Записываем активный диалог
        self.active_dialogues[player_id] = {
            'npc_id': npc_id,
            'dialogue_id': dialogue_id,
            'start_time': time.time()
        }
        
        # Записываем в историю
        if player_id not in self.dialogue_history:
            self.dialogue_history[player_id] = []
        self.dialogue_history[player_id].append(f"{npc_id}:{dialogue_id}")
        
        return dialogue
    
    def select_option(self, player_id: str, option_id: str) -> Optional[Dialogue]:
        """Выбор варианта ответа"""
        if player_id not in self.active_dialogues:
            return None
        
        active_dialogue = self.active_dialogue(player_id)
        if not active_dialogue:
            return None
        
        # Находим выбранный вариант
        selected_option = None
        for option in active_dialogue.options:
            if option.option_id == option_id:
                selected_option = option
                break
        
        if not selected_option:
            return None
        
        # Применяем последствия
        self._apply_dialogue_consequences(player_id, selected_option)
        
        # Проверяем, не закончился ли диалог
        if selected_option.next_dialogue == "end":
            self.end_dialogue(player_id)
            return None
        
        # Переходим к следующему диалогу
        npc_id = self.active_dialogues[player_id]['npc_id']
        return self.start_dialogue(player_id, npc_id, selected_option.next_dialogue)
    
    def active_dialogue(self, player_id: str) -> Optional[Dialogue]:
        """Получение активного диалога"""
        if player_id not in self.active_dialogues:
            return None
        
        dialogue_data = self.active_dialogues[player_id]
        npc_id = dialogue_data['npc_id']
        dialogue_id = dialogue_data['dialogue_id']
        
        if npc_id not in self.npcs:
            return None
        
        return self.npcs[npc_id].dialogues.get(dialogue_id)
    
    def end_dialogue(self, player_id: str):
        """Завершение диалога"""
        if player_id in self.active_dialogues:
            del self.active_dialogues[player_id]
    
    def _check_dialogue_requirements(self, player_id: str, dialogue: Dialogue) -> bool:
        """Проверка требований для диалога"""
        # Проверяем репутацию
        npc = self.npcs[dialogue.npc_id]
        if dialogue.reputation_requirement > npc.reputation:
            return False
        
        # Проверяем другие требования
        for req_type, req_value in dialogue.requirements.items():
            if req_type == "level":
                # Здесь должна быть проверка уровня игрока
                pass
            elif req_type == "quest_completed":
                # Здесь должна быть проверка завершенных квестов
                pass
        
        return True
    
    def _apply_dialogue_consequences(self, player_id: str, option: DialogueOption):
        """Применение последствий выбора"""
        # Изменяем репутацию
        if option.reputation_change != 0:
            npc_id = self.active_dialogue(player_id).npc_id
            npc = self.npcs[npc_id]
            npc.reputation = max(npc.min_reputation, 
                               min(npc.max_reputation, npc.reputation + option.reputation_change))
        
        # Применяем другие последствия
        for consequence_type, value in option.consequences.items():
            if consequence_type == "unlock_quest":
                # Разблокируем квест
                pass
            elif consequence_type == "unlock_trade":
                # Разблокируем торговлю
                pass

class QuestSystem:
    """Система квестов"""
    
    def __init__(self):
        self.player_quests: Dict[str, Dict[str, Quest]] = {}
        self.quest_templates: Dict[str, Quest] = {}
        
        # Инициализация шаблонов квестов
        self._initialize_quest_templates()
    
    def _initialize_quest_templates(self):
        """Инициализация шаблонов квестов"""
        # Квест на убийство
        kill_quest = Quest(
            quest_id="kill_goblins",
            name="Goblin Hunt",
            description="Eliminate 5 goblins that have been terrorizing the village",
            quest_type=QuestType.KILL,
            objectives=[
                {"type": "kill", "target": "goblin", "count": 5, "current": 0}
            ],
            rewards={
                "experience": 100,
                "gold": 50,
                "items": ["health_potion", "mana_potion"]
            },
            reputation_reward=10,
            experience_reward=100
        )
        self.quest_templates["kill_goblins"] = kill_quest
        
        # Квест на сбор
        collect_quest = Quest(
            quest_id="collect_herbs",
            name="Herb Collection",
            description="Collect 10 healing herbs for the village healer",
            quest_type=QuestType.COLLECT,
            objectives=[
                {"type": "collect", "item": "healing_herb", "count": 10, "current": 0}
            ],
            rewards={
                "experience": 80,
                "gold": 30,
                "items": ["healing_potion"]
            },
            reputation_reward=5,
            experience_reward=80
        )
        self.quest_templates["collect_herbs"] = collect_quest
        
        # Квест на доставку
        deliver_quest = Quest(
            quest_id="deliver_package",
            name="Package Delivery",
            description="Deliver a package to the merchant in the next town",
            quest_type=QuestType.DELIVER,
            objectives=[
                {"type": "deliver", "item": "merchant_package", "target": "merchant", "completed": False}
            ],
            rewards={
                "experience": 120,
                "gold": 75,
                "items": ["magic_scroll"]
            },
            reputation_reward=15,
            experience_reward=120
        )
        self.quest_templates["deliver_package"] = deliver_quest
    
    def initialize_player_quests(self, player_id: str):
        """Инициализация квестов для игрока"""
        self.player_quests[player_id] = {}
    
    def start_quest(self, player_id: str, quest_id: str) -> bool:
        """Начало квеста"""
        if player_id not in self.player_quests:
            self.initialize_player_quests(player_id)
        
        if quest_id not in self.quest_templates:
            return False
        
        # Проверяем, не взят ли уже квест
        if quest_id in self.player_quests[player_id]:
            return False
        
        # Создаем копию квеста
        template = self.quest_templates[quest_id]
        quest = Quest(
            quest_id=template.quest_id,
            name=template.name,
            description=template.description,
            quest_type=template.quest_type,
            objectives=template.objectives.copy(),
            rewards=template.rewards.copy(),
            requirements=template.requirements.copy(),
            time_limit=template.time_limit,
            reputation_reward=template.reputation_reward,
            experience_reward=template.experience_reward,
            status=QuestStatus.IN_PROGRESS,
            start_time=time.time()
        )
        
        self.player_quests[player_id][quest_id] = quest
        return True
    
    def update_quest_progress(self, player_id: str, quest_id: str, objective_type: str, 
                            target: str, amount: int = 1) -> bool:
        """Обновление прогресса квеста"""
        if player_id not in self.player_quests or quest_id not in self.player_quests[player_id]:
            return False
        
        quest = self.player_quests[player_id][quest_id]
        
        if quest.status != QuestStatus.IN_PROGRESS:
            return False
        
        # Обновляем цели
        for objective in quest.objectives:
            if objective["type"] == objective_type and objective.get("target") == target:
                if "current" in objective:
                    objective["current"] = min(objective["count"], objective["current"] + amount)
                elif "completed" in objective:
                    objective["completed"] = True
        
        # Проверяем завершение
        if self._check_quest_completion(quest):
            self.complete_quest(player_id, quest_id)
        
        return True
    
    def _check_quest_completion(self, quest: Quest) -> bool:
        """Проверка завершения квеста"""
        for objective in quest.objectives:
            if objective["type"] == "kill" or objective["type"] == "collect":
                if objective["current"] < objective["count"]:
                    return False
            elif objective["type"] == "deliver":
                if not objective.get("completed", False):
                    return False
        
        return True
    
    def complete_quest(self, player_id: str, quest_id: str) -> bool:
        """Завершение квеста"""
        if player_id not in self.player_quests or quest_id not in self.player_quests[player_id]:
            return False
        
        quest = self.player_quests[player_id][quest_id]
        quest.status = QuestStatus.COMPLETED
        quest.completion_time = time.time()
        
        # Выдаем награды
        self._give_quest_rewards(player_id, quest)
        
        return True
    
    def _give_quest_rewards(self, player_id: str, quest: Quest):
        """Выдача наград за квест"""
        # Здесь должна быть логика выдачи наград игроку
        print(f"Quest completed: {quest.name}")
        print(f"Rewards: {quest.rewards}")

class TradeSystem:
    """Система торговли"""
    
    def __init__(self):
        self.npc_trade_items: Dict[str, Dict[str, TradeItem]] = {}
        self.player_inventory: Dict[str, Dict[str, Any]] = {}
        
        # Инициализация торговых предметов
        self._initialize_trade_items()
    
    def _initialize_trade_items(self):
        """Инициализация торговых предметов"""
        # Оружие
        sword = TradeItem(
            item_id="iron_sword",
            name="Iron Sword",
            description="A basic iron sword",
            buy_price=100,
            sell_price=50,
            trade_type=TradeType.BUY
        )
        
        # Броня
        armor = TradeItem(
            item_id="leather_armor",
            name="Leather Armor",
            description="Light leather armor",
            buy_price=80,
            sell_price=40,
            trade_type=TradeType.BUY
        )
        
        # Зелья
        health_potion = TradeItem(
            item_id="health_potion",
            name="Health Potion",
            description="Restores 50 health",
            buy_price=25,
            sell_price=12,
            trade_type=TradeType.BUY
        )
        
        # Добавляем предметы торговцу
        self.npc_trade_items["merchant"] = {
            "iron_sword": sword,
            "leather_armor": armor,
            "health_potion": health_potion
        }
    
    def initialize_player_inventory(self, player_id: str):
        """Инициализация инвентаря игрока"""
        self.player_inventory[player_id] = {
            "gold": 100,
            "items": {}
        }
    
    def buy_item(self, player_id: str, npc_id: str, item_id: str, quantity: int = 1) -> bool:
        """Покупка предмета"""
        if player_id not in self.player_inventory:
            self.initialize_player_inventory(player_id)
        
        if npc_id not in self.npc_trade_items or item_id not in self.npc_trade_items[npc_id]:
            return False
        
        item = self.npc_trade_items[npc_id][item_id]
        total_cost = item.buy_price * quantity
        
        # Проверяем золото
        if self.player_inventory[player_id]["gold"] < total_cost:
            return False
        
        # Проверяем количество
        if item.quantity < quantity:
            return False
        
        # Выполняем покупку
        self.player_inventory[player_id]["gold"] -= total_cost
        item.quantity -= quantity
        
        # Добавляем предмет в инвентарь
        if item_id not in self.player_inventory[player_id]["items"]:
            self.player_inventory[player_id]["items"][item_id] = 0
        self.player_inventory[player_id]["items"][item_id] += quantity
        
        return True
    
    def sell_item(self, player_id: str, npc_id: str, item_id: str, quantity: int = 1) -> bool:
        """Продажа предмета"""
        if player_id not in self.player_inventory:
            return False
        
        if item_id not in self.player_inventory[player_id]["items"]:
            return False
        
        if self.player_inventory[player_id]["items"][item_id] < quantity:
            return False
        
        # Находим предмет у NPC для определения цены
        sell_price = 10  # Базовая цена продажи
        if npc_id in self.npc_trade_items and item_id in self.npc_trade_items[npc_id]:
            sell_price = self.npc_trade_items[npc_id][item_id].sell_price
        
        total_income = sell_price * quantity
        
        # Выполняем продажу
        self.player_inventory[player_id]["gold"] += total_income
        self.player_inventory[player_id]["items"][item_id] -= quantity
        
        if self.player_inventory[player_id]["items"][item_id] <= 0:
            del self.player_inventory[player_id]["items"][item_id]
        
        return True
    
    def get_player_inventory(self, player_id: str) -> Dict[str, Any]:
        """Получение инвентаря игрока"""
        return self.player_inventory.get(player_id, {"gold": 0, "items": {}})
    
    def get_npc_trade_items(self, npc_id: str) -> Dict[str, TradeItem]:
        """Получение торговых предметов NPC"""
        return self.npc_trade_items.get(npc_id, {})

class SocialSystem:
    """Объединенная социальная система"""
    
    def __init__(self):
        self.dialogue_system = DialogueSystem()
        self.quest_system = QuestSystem()
        self.trade_system = TradeSystem()
    
    def initialize_player_social(self, player_id: str):
        """Инициализация социальных систем для игрока"""
        self.quest_system.initialize_player_quests(player_id)
        self.trade_system.initialize_player_inventory(player_id)
    
    def start_dialogue(self, player_id: str, npc_id: str, dialogue_id: str = "greeting"):
        """Начало диалога"""
        return self.dialogue_system.start_dialogue(player_id, npc_id, dialogue_id)
    
    def select_dialogue_option(self, player_id: str, option_id: str):
        """Выбор варианта ответа"""
        return self.dialogue_system.select_option(player_id, option_id)
    
    def start_quest(self, player_id: str, quest_id: str):
        """Начало квеста"""
        return self.quest_system.start_quest(player_id, quest_id)
    
    def update_quest_progress(self, player_id: str, quest_id: str, objective_type: str, 
                            target: str, amount: int = 1):
        """Обновление прогресса квеста"""
        return self.quest_system.update_quest_progress(player_id, quest_id, objective_type, target, amount)
    
    def buy_item(self, player_id: str, npc_id: str, item_id: str, quantity: int = 1):
        """Покупка предмета"""
        return self.trade_system.buy_item(player_id, npc_id, item_id, quantity)
    
    def sell_item(self, player_id: str, npc_id: str, item_id: str, quantity: int = 1):
        """Продажа предмета"""
        return self.trade_system.sell_item(player_id, npc_id, item_id, quantity)
    
    def get_player_quests(self, player_id: str) -> Dict[str, Quest]:
        """Получение квестов игрока"""
        return self.quest_system.player_quests.get(player_id, {})
    
    def get_player_inventory(self, player_id: str) -> Dict[str, Any]:
        """Получение инвентаря игрока"""
        return self.trade_system.get_player_inventory(player_id)
    
    def get_npc_trade_items(self, npc_id: str) -> Dict[str, TradeItem]:
        """Получение торговых предметов NPC"""
        return self.trade_system.get_npc_trade_items(npc_id)
