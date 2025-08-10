import random


class LearningSystem:
    def __init__(self, entity):
        self.entity = entity

        # Получаем настройки обучения
        from config.unified_settings import get_ai_settings

        ai_settings = get_ai_settings()

        self.weakness_discovery_chance = 0.1  # Базовое значение

    def process_experience(self):
        # Базовый метод, переопределяется в подклассах
        pass

    def update(self, delta_time):
        """Обновляет систему обучения"""
        self.process_experience()


class PlayerLearning(LearningSystem):
    def process_experience(self):
        # Игрок быстро учится на любом опыте
        self.discover_weaknesses()
        self.experiment_with_items()

    def discover_weaknesses(self):
        # Высокая вероятность обнаружения слабостей
        if random.random() < self.weakness_discovery_chance * self.entity.learning_rate:
            # Логика обнаружения слабостей
            pass

    def experiment_with_items(self):
        # Частые эксперименты с предметами
        from config.unified_settings import get_ai_settings

        ai_settings = get_ai_settings()

        if random.random() < 0.05 * self.entity.learning_rate:  # Базовое значение
            # Логика экспериментов
            pass


class EnemyLearning(LearningSystem):
    def process_experience(self):
        # Враги учатся медленнее
        if random.random() < self.entity.learning_rate:
            self.share_knowledge()
            self.adapt_to_player()

    def share_knowledge(self):
        # Обмен знаниями с другими врагами через общую память
        for key, value in self.entity.memory.items():
            if (
                hasattr(self.entity, "shared_knowledge")
                and key not in self.entity.shared_knowledge
            ):
                self.entity.shared_knowledge[key] = value

    def adapt_to_player(self):
        # Адаптация к стилю игры игрока
        from config.unified_settings import get_ai_settings

        ai_settings = get_ai_settings()

        if "effective_vs_me" in self.entity.memory:
            effective_attacks = self.entity.memory["effective_vs_me"]
            # Увеличиваем сопротивление к эффективным типам атак
            for attack_type in effective_attacks:
                resist_stat = f"{attack_type}_resist"
                if resist_stat in self.entity.combat_stats:
                    self.entity.combat_stats[resist_stat] = min(
                        0.8,  # MAX_RESISTANCE
                        self.entity.combat_stats[resist_stat]
                        + 0.05,  # RESISTANCE_GAIN_PER_ADAPTATION
                    )


class BossLearning(LearningSystem):
    def process_experience(self):
        # Боссы учатся очень медленно, но основательно
        from config.unified_settings import get_ai_settings

        ai_settings = get_ai_settings()

        if (
            random.random() < self.entity.learning_rate * 0.5
        ):  # BOSS_LEARNING_MULTIPLIER
            self.analyze_player_patterns()
            self.develop_counter_strategies()

    def analyze_player_patterns(self):
        # Анализ паттернов поведения игрока
        pass

    def develop_counter_strategies(self):
        # Разработка контрстратегий против игрока
        from config.unified_settings import get_ai_settings

        ai_settings = get_ai_settings()

        if (
            hasattr(self.entity, "shared_knowledge")
            and "player_combat_style" in self.entity.shared_knowledge
        ):
            style = self.entity.shared_knowledge["player_combat_style"]
            if style == "melee":
                # Увеличиваем шанс парирования
                self.entity.combat_stats["parry_chance"] = min(
                    0.4,  # MAX_PARRY_CHANCE
                    self.entity.combat_stats["parry_chance"]
                    + 0.02,  # PARRY_CHANCE_GAIN
                )
            elif style == "ranged":
                # Увеличиваем сопротивление снарядам
                self.entity.combat_stats["physical_resist"] = min(
                    0.8,  # MAX_PHYSICAL_RESISTANCE
                    self.entity.combat_stats["physical_resist"]
                    + 0.05,  # PHYSICAL_RESISTANCE_GAIN
                )
