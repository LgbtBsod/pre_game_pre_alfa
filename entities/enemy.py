import json
import random
import pickle
from entities.entity import Entity

class Enemy(Entity):
    def __init__(self, x, y, z=0, enemy_type="warrior"):
        super().__init__(x, y, z)
        
        # Загрузка данных из JSON
        with open("data/items.json") as f:
            self.data = json.load(f)
        
        # Тип врага и параметры
        self.enemy_type = enemy_type
        self._load_enemy_stats()
        
        # Состояние врага
        self.state = "patrol"
        self.target = None
        self.path = []
        
        # Дроп
        self.drop_table = {
            "health_potion": 0.3,
            "gold_coins": 0.5,
            "sword": 0.2,
            "bow": 0.1
        }
        
        # ИИ
        self.ai = None

    def _load_enemy_stats(self):
        """Загрузка параметров врага из JSON"""
        if self.enemy_type in self.data["enemy_types"]:
            stats = self.data["enemy_types"][self.enemy_type]
            self.health = stats.get("health", 100)
            self.max_health = stats.get("max_health", 100)
            self.attack_power = stats.get("attack_power", 10)
            self.speed = stats.get("speed", 1)
            self.currency_reward = stats.get("currency_reward", 50)
            self.resistances.update(stats.get("resistances", {}))
            self.weaknesses.update(stats.get("weaknesses", {}))
            self.effects.update(stats.get("effects", {}))
        else:
            # Базовые параметры по умолчанию
            self.health = 100
            self.max_health = 100
            self.attack_power = 10
            self.speed = 1
            self.currency_reward = 50

    def take_damage(self, amount, damage_type="physical"):
        """Получение урона с учетом сопротивления"""
        resistance = self.resistances.get(damage_type, 0)
        actual_damage = amount * (1 - resistance)
        
        # Применение слабости
        if damage_type in self.weaknesses:
            actual_damage *= 1.5
            
        self.health -= actual_damage
        print(f"{self.enemy_type} получил {actual_damage:.1f} урона ({damage_type}). Здоровье: {self.health:.1f}")
        
        # Обучение ИИ
        if self.ai:
            feedback = {
                "state": {"damage_type": damage_type, "damage_amount": actual_damage},
                "action": "take_damage",
                "reward": -actual_damage
            }
            self.ai.update_knowledge(feedback)
            
        return actual_damage

    def die(self):
        """Смерть врага с дропом"""
        print(f"{self.enemy_type} погиб!")
        
        # Генерация дропа
        drops = []
        for item_type, chance in self.drop_table.items():
            if random.random() < chance:
                drops.append(Item(self.x, self.y, item_type))
                
        # Добавление монет
        if random.random() < 0.7:
            gold_amount = random.randint(10, 50)
            drops.append(GoldCoin(self.x, self.y, gold_amount))
            
        print(f"Дроп: {[item.item_type for item in drops]}")
        
        # Обучение ИИ
        if self.ai:
            feedback = {
                "state": {"drops": len(drops)},
                "action": "die",
                "reward": self.currency_reward
            }
            self.ai.update_knowledge(feedback)
            
        return drops

    def update(self, player, enemies):
        """Обновление состояния врага"""
        # Обновление эффектов
        self.apply_effects()
        
        # Логика поведения
        if self.health <= 0:
            return
        
        if self.state == "patrol":
            self._patrol()
        elif self.state == "chase":
            self._chase(player)
        elif self.state == "attack":
            self._attack(player)
            
        # Проверка состояния
        if self.health <= self.max_health * 0.3 and self.effects.get("buff", 0) == 0:
            self._apply_buff()
            
        # Обучение ИИ
        if self.ai:
            state = self._get_ai_state(player, enemies)
            action = self.ai.decide_action(state)
            self._perform_action(action, player)

    def _patrol(self):
        """Патруль"""
        # Простая логика патруля
        if random.random() < 0.05:
            self.x += random.choice([-1, 0, 1])
            self.y += random.choice([-1, 0, 1])

    def _chase(self, player):
        """Преследование игрока"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx**2 + dy**2)**0.5
        
        if distance > 0:
            self.x += self.speed * dx / distance * 0.1
            self.y += self.speed * dy / distance * 0.1

    def _attack(self, player):
        """Атака игрока"""
        # Простая проверка дистанции
        if abs(self.x - player.x) < 1 and abs(self.y - player.y) < 1:
            player.take_damage(self.attack_power, "physical")

    def _apply_buff(self):
        """Применение баффа при низком здоровье"""
        self.effects["rage"] = 300  # 300 кадров баффа
        self.attack_power *= 1.5
        print(f"{self.enemy_type} вошел в ярость! Атака увеличена")

    def _get_ai_state(self, player, enemies):
        """Получение состояния для ИИ"""
        nearby_enemies = self.get_nearby_entities(enemies)
        return {
            "health_ratio": self.health / self.max_health,
            "player_distance": ((self.x - player.x)**2 + (self.y - player.y)**2)**0.5,
            "nearby_allies": len(nearby_enemies),
            "effects": self.effects.copy(),
            "knowledge": dict(self.knowledge)
        }

    def _perform_action(self, action, player):
        """Выполнение действия ИИ"""
        if action == "chase":
            self.state = "chase"
        elif action == "attack":
            self.state = "attack"
        elif action == "retreat":
            self.state = "retreat"
        elif action == "use_item":
            self._use_random_item()

    def _use_random_item(self):
        """Использование случайного предмета из инвентаря"""
        if self.inventory:
            item = random.choice(self.inventory)
            item.use(self)
            self.inventory.remove(item)

    def save(self):
        """Сохранение состояния врага"""
        state = {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "enemy_type": self.enemy_type,
            "health": self.health,
            "effects": self.effects.copy(),
            "knowledge": dict(self.knowledge)
        }
        return pickle.dumps(state)

    def load(self, data):
        """Загрузка состояния врага"""
        state = pickle.loads(data)
        self.x = state["x"]
        self.y = state["y"]
        self.z = state["z"]
        self.enemy_type = state["enemy_type"]
        self.health = state["health"]
        self.effects = state["effects"]
        
        # Восстановление знаний
        self.knowledge = defaultdict(lambda: defaultdict(lambda: 0.5))
        for category in state["knowledge"]:
            self.knowledge[category] = defaultdict(lambda: 0.5)
            for key, value in state["knowledge"][category].items():
                self.knowledge[category][key] = value

