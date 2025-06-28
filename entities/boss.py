import json
import random
import pickle
from entities.enemy import Enemy

class Boss(Enemy):
    def __init__(self, x, y, z=0, boss_type="dragon"):
        super().__init__(x, y, z, boss_type)
        
        # Загрузка данных из JSON
        with open("data/items.json") as f:
            self.data = json.load(f)
        
        # Специфичные для босса параметры
        self.boss_type = boss_type
        self._load_boss_stats()
        
        # Фазы боя
        self.phase = 1
        self.phase_thresholds = {
            2: 0.6,  # 60% здоровья для второй фазы
            3: 0.3   # 30% здоровья для третьей фазы
        }
        
        # Спецспособности
        self.special_abilities = {
            1: self.phase_1_skill,
            2: self.phase_2_skill,
            3: self.phase_3_skill
        }
        
        # Таймеры
        self.ability_cooldown = 0
        self.cooldown_duration = 300  # 5 секунд при 60 FPS

    def _load_boss_stats(self):
        """Загрузка параметров босса из JSON"""
        if self.boss_type in self.data["boss_types"]:
            stats = self.data["boss_types"][self.boss_type]
            self.health = stats.get("health", 500)
            self.max_health = stats.get("max_health", 500)
            self.attack_power = stats.get("attack_power", 25)
            self.speed = stats.get("speed", 0.5)
            self.currency_reward = stats.get("currency_reward", 500)
            self.resistances.update(stats.get("resistances", {}))
            self.weaknesses.update(stats.get("weaknesses", {}))
            self.effects.update(stats.get("effects", {}))
        else:
            # Базовые параметры по умолчанию
            self.health = 500
            self.max_health = 500
            self.attack_power = 25
            self.speed = 0.5
            self.currency_reward = 500

    def update(self, player, enemies):
        """Обновление состояния босса"""
        # Обновление эффектов
        self.apply_effects()
        
        # Проверка смены фаз
        self._check_phase_change()
        
        # Логика поведения
        if self.health <= 0:
            return
            
        # Использование спецспособности
        if self.ability_cooldown <= 0:
            self.special_abilities[self.phase]()
            self.ability_cooldown = self.cooldown_duration
        else:
            self.ability_cooldown -= 1
            
        # Обычная атака или преследование
        if self.distance_to(player) > 2:
            self._chase(player)
        else:
            self._attack(player)

    def _check_phase_change(self):
        """Проверка необходимости смены фазы"""
        health_ratio = self.health / self.max_health
        
        for phase in sorted(self.phase_thresholds.keys()):
            if health_ratio <= self.phase_thresholds[phase] and phase > self.phase:
                self.phase = phase
                print(f"{self.boss_type} перешел в фазу {self.phase}!")
                self._on_phase_change()

    def _on_phase_change(self):
        """Действия при смене фазы"""
        if self.phase == 2:
            self.attack_power *= 1.5
            self.speed *= 1.3
        elif self.phase == 3:
            self.attack_power *= 2
            self.speed *= 1.5
            self.effects["rage"] = 600  # 600 кадров ярости

    def phase_1_skill(self):
        """Спецспособность в фазе 1"""
        print(f"{self.boss_type} использует огненный взрыв!")
        # Создание огненных ловушек вокруг босса
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if abs(dx) + abs(dy) <= 1:
                    from entities.trap import Trap
                    trap = Trap(self.x + dx, self.y + dy, "fire")
                    trap.damage = 15
                    self.spawned_traps.append(trap)

    def phase_2_skill(self):
        """Спецспособность в фазе 2"""
        print(f"{self.boss_type} вызывает миньонов!")
        # Вызов 2-х миньонов
        for _ in range(2):
            from entities.enemy import Enemy
            enemy_type = random.choice(["warrior", "archer"])
            enemy = Enemy(self.x + random.uniform(-1, 1), 
                         self.y + random.uniform(-1, 1), 
                         enemy_type)
            enemy.health = int(enemy.health * 1.5)
            enemy.attack_power = int(enemy.attack_power * 1.5)
            self.summoned_enemies.append(enemy)

    def phase_3_skill(self):
        """Спецспособность в фазе 3"""
        print(f"{self.boss_type} активирует защитное поле!")
        # Увеличение сопротивлений
        self.resistances["physical"] = 0.5
        self.resistances["magic"] = 0.3
        # Восстановление здоровья
        self.health = min(self.max_health, self.health + self.max_health * 0.2)

    def die(self):
        """Смерть босса с уникальным дропом"""
        print(f"{self.boss_type} погиб!")
        
        # Генерация уникального дропа
        drops = []
        
        # Уникальное оружие
        unique_weapons = ["dragon_sword", "shadow_bow", "phoenix_staff"]
        if random.random() < 0.7:
            from items.weapon import Weapon
            weapon = Weapon(random.choice(unique_weapons))
            drops.append(weapon)
            
        # Эпические аксессуары
        if random.random() < 0.5:
            from items.accessory import Accessory
            accessories = ["dragon_ring", "phoenix_amulet", "shadow_cloak"]
            accessory = Accessory(random.choice(accessories))
            drops.append(accessory)
            
        # Большое количество монет
        gold_amount = random.randint(200, 500)
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

    def spawn_traps(self, game_map):
        """Создание ловушек вокруг босса"""
        for trap in self.spawned_traps:
            game_map.add_entity(trap)
        self.spawned_traps.clear()

    def summon_enemies(self, game_map):
        """Вызов миньонов"""
        for enemy in self.summoned_enemies:
            game_map.add_entity(enemy)
        self.summoned_enemies.clear()

    def save(self):
        """Сохранение состояния босса"""
        state = {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "boss_type": self.boss_type,
            "health": self.health,
            "effects": self.effects.copy(),
            "knowledge": dict(self.knowledge),
            "phase": self.phase
        }
        return pickle.dumps(state)

    def load(self, data):
        """Загрузка состояния босса"""
        state = pickle.loads(data)
        self.x = state["x"]
        self.y = state["y"]
        self.z = state["z"]
        self.boss_type = state["boss_type"]
        self.health = state["health"]
        self.effects = state["effects"]
        self.phase = state["phase"]
        
        # Восстановление знаний
        self.knowledge = defaultdict(lambda: defaultdict(lambda: 0.5))
        for category in state["knowledge"]:
            self.knowledge[category] = defaultdict(lambda: 0.5)
            for key, value in state["knowledge"][category].items():
                self.knowledge[category][key] = value
