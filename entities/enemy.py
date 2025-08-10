"""
Враг - противник игрока с AI системами.
"""

from entities.base_entity import BaseEntity


class Enemy(BaseEntity):
    """Враг - противник игрока с AI"""

    def __init__(self, enemy_type: str, level: int = 1, position: tuple = (0, 0)):
        super().__init__(f"enemy_{enemy_type}", position)

        # Специфичные для врага параметры
        self.enemy_type = enemy_type
        self.level = level
        self.experience_reward = 10 * level
        self.ai_behavior = "aggressive"
        self.loot_table = []
        self.skills = []

        # Настройки врага
        self.aggro_range = 100.0
        from config.unified_settings import UnifiedSettings

        self.attack_range = UnifiedSettings.ATTACK_RANGE_BASE
        self.patrol_radius = 200.0
        self.return_to_spawn = True
        self.spawn_position = list(position)

        # Состояние ИИ
        self.target = None
        self.state = "idle"  # idle, patrol, chase, attack, return
        self.last_attack_time = 0.0

        # AI специфичные настройки
        from config.unified_settings import UnifiedSettings

        self.learning_rate = UnifiedSettings.LEARNING_RATE_ENEMY
        self.aggression_level = 0.7
        self.cowardice_threshold = 0.3
        self.retreat_health_threshold = 0.2

        # Обновляем характеристики для врага
        self.scale_for_level(level)
        self.update_derived_stats()

        # Инициализируем AI поведение
        self.initialize_ai_behavior()

    def initialize_ai_behavior(self):
        """Инициализирует AI поведение на основе типа врага"""
        behavior_configs = {
            "warrior": {
                "aggression_level": 0.8,
                "preferred_range": "melee",
                "tactics": ["charge", "defensive_stance"],
                "weapon_preferences": ["sword", "axe", "mace"],
            },
            "archer": {
                "aggression_level": 0.6,
                "preferred_range": "ranged",
                "tactics": ["kite", "cover_fire"],
                "weapon_preferences": ["bow", "crossbow"],
            },
            "mage": {
                "aggression_level": 0.5,
                "preferred_range": "ranged",
                "tactics": ["spell_spam", "debuff"],
                "weapon_preferences": ["staff", "wand"],
            },
            "assassin": {
                "aggression_level": 0.9,
                "preferred_range": "melee",
                "tactics": ["stealth", "backstab"],
                "weapon_preferences": ["dagger", "short_sword"],
            },
            "berserker": {
                "aggression_level": 1.0,
                "preferred_range": "melee",
                "tactics": ["rage", "reckless_attack"],
                "weapon_preferences": ["great_sword", "battle_axe"],
            },
        }

        config = behavior_configs.get(self.enemy_type, behavior_configs["warrior"])
        self.aggression_level = config["aggression_level"]
        self.preferred_range = config["preferred_range"]
        self.available_tactics = config["tactics"]
        self.weapon_preferences = config["weapon_preferences"]

    def scale_for_level(self, level: int):
        """Масштабирует характеристики под уровень"""
        # Базовые множители для уровня
        health_multiplier = 1.0 + (level - 1) * 0.5
        damage_multiplier = 1.0 + (level - 1) * 0.3
        defense_multiplier = 1.0 + (level - 1) * 0.2

        # Обновляем характеристики
        stats = self.combat_stats_manager.get_stats()
        # Используем метод для установки max_health
        new_max_health = stats.max_health * health_multiplier
        self.combat_stats_manager.set_max_health(new_max_health)
        self.combat_stats_manager.set_health(new_max_health)

        # Обновляем другие характеристики через update_stats
        self.combat_stats_manager.update_stats(
            {
                "damage_output": stats.damage_output * damage_multiplier,
                "defense": stats.defense * defense_multiplier,
            }
        )

        # Обновляем атрибуты
        for attr_name in [
            "strength",
            "dexterity",
            "intelligence",
            "vitality",
            "endurance",
        ]:
            current_value = self.attribute_manager.get_attribute_value(attr_name)
            self.attribute_manager.set_attribute_base(
                attr_name, current_value * (1.0 + (level - 1) * 0.1)
            )

    def update(self, delta_time: float):
        """Обновляет врага"""
        super().update(delta_time)

        # Обновляем ИИ
        self.update_ai(delta_time)

    def update_ai(self, delta_time: float):
        """Обновляет ИИ врага с учетом обучения"""
        if not self.alive:
            return

        # Ищем цель
        if not self.target or not self.target.alive:
            self.find_target()

        if self.target:
            distance = self.distance_to(self.target)

            # Принимаем решение на основе обучения
            decision = self.decision_maker.make_combat_decision(self.target, distance)

            if decision == "attack":
                self.state = "attack"
                if self.can_attack():
                    self.attack(self.target)
            elif decision == "chase":
                self.state = "chase"
                self.move_towards(self.target.position, self.movement_speed, delta_time)
            elif decision == "retreat":
                self.state = "return"
                self.return_to_spawn_point(delta_time)
            elif decision == "use_item":
                self.use_item_intelligently()
        else:
            # Нет цели - патрулируем или возвращаемся
            if self.state == "return":
                self.return_to_spawn_point(delta_time)
            else:
                self.patrol(delta_time)

    def find_target(self):
        """Ищет цель для атаки с учетом обучения"""
        # Здесь должна быть логика поиска игрока или других целей
        # Пока просто заглушка - в реальной игре здесь будет поиск ближайшего игрока
        pass

    def return_to_spawn_point(self, delta_time: float):
        """Возвращается к точке спавна"""
        distance_to_spawn = (
            (self.position[0] - self.spawn_position[0]) ** 2
            + (self.position[1] - self.spawn_position[1]) ** 2
        ) ** 0.5

        if distance_to_spawn > 10:
            self.move_towards(self.spawn_position, self.movement_speed, delta_time)
        else:
            self.state = "patrol"

    def patrol(self, delta_time: float):
        """Патрулирует территорию"""
        # Простое патрулирование - случайное движение
        import random
        import math

        if random.random() < 0.01:  # 1% шанс сменить направление
            angle = random.uniform(0, 2 * math.pi)
            self.patrol_direction = [math.cos(angle), math.sin(angle)]

        if hasattr(self, "patrol_direction"):
            target_x = (
                self.spawn_position[0] + self.patrol_direction[0] * self.patrol_radius
            )
            target_y = (
                self.spawn_position[1] + self.patrol_direction[1] * self.patrol_radius
            )
            self.move_towards(
                (target_x, target_y), self.movement_speed * 0.5, delta_time
            )

    def attack(self, target):
        """Атакует цель с учетом обучения и тактик"""
        if not self.can_attack() or not target.alive:
            return None

        # Выбираем тактику атаки
        tactic = self.select_attack_tactic(target)

        # Выбираем лучшее оружие
        best_weapon = self.select_best_weapon_for_target(target)

        # Вычисляем урон с учетом тактики
        base_damage = self.combat_stats_manager.get_stats().damage_output
        damage_bonus = self.get_learned_damage_bonus(target)
        tactic_bonus = self.get_tactic_damage_bonus(tactic)

        total_damage = base_damage + damage_bonus + tactic_bonus

        # Проверяем критический удар
        import random

        critical_chance = self.combat_stats_manager.get_stats().critical_chance
        critical_multiplier = self.combat_stats_manager.get_stats().critical_multiplier

        is_critical = random.random() < critical_chance
        damage_multiplier = critical_multiplier if is_critical else 1.0

        final_damage = total_damage * damage_multiplier

        # Создаем отчет об уроне
        damage_report = {
            "damage": final_damage,
            "damage_type": "physical",
            "is_critical": is_critical,
            "attacker": self,
            "attacker_type": self.__class__.__name__,
            "weapon_type": (
                best_weapon.get("type", "unknown") if best_weapon else "unknown"
            ),
            "learned_bonus": damage_bonus,
            "tactic": tactic,
            "tactic_bonus": tactic_bonus,
        }

        # Наносим урон цели
        target.take_damage(damage_report)

        # Начинаем кулдаун атаки
        self.start_attack_cooldown()

        # Учимся на атаке
        self.learn_from_attack(damage_report, target)

        return damage_report

    def select_attack_tactic(self, target) -> str:
        """Выбирает тактику атаки на основе ситуации"""
        health_percentage = self.get_health_percentage()
        target_health_percentage = target.get_health_percentage()

        # Агрессивные тактики при низком здоровье врага
        if target_health_percentage < 0.3:
            if "reckless_attack" in self.available_tactics:
                return "reckless_attack"

        # Защитные тактики при низком здоровье
        if health_percentage < self.retreat_health_threshold:
            if "defensive_stance" in self.available_tactics:
                return "defensive_stance"

        # Обычные тактики
        if "charge" in self.available_tactics:
            return "charge"

        return "normal_attack"

    def get_tactic_damage_bonus(self, tactic: str) -> float:
        """Получает бонус к урону от тактики"""
        tactic_bonuses = {
            "reckless_attack": 10.0,
            "charge": 5.0,
            "backstab": 15.0,
            "normal_attack": 0.0,
            "defensive_stance": -2.0,
        }
        return tactic_bonuses.get(tactic, 0.0)

    def die(self):
        """Смерть врага"""
        super().die()

        # Дроп предметов
        self.drop_loot()

        # Даем опыт игроку
        if self.target and hasattr(self.target, "kill_enemy"):
            self.target.kill_enemy(self)

    def drop_loot(self):
        """Дроп предметов на основе обучения"""
        # Здесь должна быть логика дропа предметов из loot_table
        # с учетом предпочтений игрока (если враг учился)
        pass

    def set_ai_behavior(self, behavior: str):
        """Устанавливает поведение ИИ"""
        valid_behaviors = ["aggressive", "defensive", "coward", "berserker"]
        if behavior in valid_behaviors:
            self.ai_behavior = behavior

    def set_loot_table(self, loot_items: list):
        """Устанавливает таблицу добычи"""
        self.loot_table = loot_items

    def add_skill(self, skill_id: str):
        """Добавляет умение"""
        if skill_id not in self.skills:
            self.skills.append(skill_id)

    def can_use_skill(self, skill_id: str) -> bool:
        """Проверяет, может ли использовать умение"""
        return skill_id in self.skills and skill_id not in self.skill_cooldowns

    def use_skill(self, skill_id: str, target=None):
        """Использует умение"""
        if not self.can_use_skill(skill_id):
            return False

        # Здесь должна быть логика использования умений
        # Пока просто устанавливаем кулдаун
        self.skill_cooldowns[skill_id] = 5.0  # 5 секунд кулдаун

        # Учимся использованию умения
        self.ai_memory.record_event(
            "skill_used", {"skill_id": skill_id, "target": target, "effectiveness": 1.0}
        )

        return True

    def learn_from_combat(self, combat_data: dict):
        """Учится на основе боевого опыта"""
        # Анализируем эффективность тактик
        tactic_used = combat_data.get("tactic", "normal_attack")
        damage_dealt = combat_data.get("damage", 0)
        target_type = combat_data.get("target_type", "unknown")

        # Обновляем предпочтения тактик
        if tactic_used not in self.item_preferences:
            self.item_preferences[tactic_used] = 0

        if damage_dealt > 15:
            self.item_preferences[tactic_used] += 1
        else:
            self.item_preferences[tactic_used] = max(
                0, self.item_preferences[tactic_used] - 1
            )

        # Сохраняем опыт
        self.ai_memory.record_event("combat_experience", combat_data)
