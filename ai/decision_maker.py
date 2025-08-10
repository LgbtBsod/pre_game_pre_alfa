class DecisionMaker:
    def __init__(self, entity):
        self.entity = entity

    def make_decisions(self, delta_time):
        # Базовый метод, переопределяется в подклассах
        pass

    def make_combat_decision(self, target, distance):
        """Принимает решение в бою"""
        if not target or not target.alive:
            return "idle"

        # Простая логика принятия решений
        if distance <= 50:  # Ближний бой
            return "attack"
        elif distance <= 150:  # Средняя дистанция
            return "chase"
        elif self.entity.health < self.entity.max_health * 0.3:  # Низкое здоровье
            return "retreat"
        else:
            return "patrol"

    def update(self, delta_time):
        """Обновляет принятие решений"""
        self.make_decisions(delta_time)


class PlayerDecisionMaker(DecisionMaker):
    def make_decisions(self, delta_time):
        # Принятие решений для игрока
        self.decide_combat_strategy()
        self.decide_item_usage()
        self.decide_trap_placement()

    def decide_combat_strategy(self):
        # Выбор стратегии боя на основе знаний
        pass

    def decide_item_usage(self):
        # Решение об использовании предметов
        pass

    def decide_trap_placement(self):
        # Решение о размещении ловушек
        pass


class EnemyDecisionMaker(DecisionMaker):
    def make_decisions(self, delta_time):
        # Принятие решений для врагов
        self.adapt_combat_style()
        self.use_shared_knowledge()

    def adapt_combat_style(self):
        # Адаптация стиля боя на основе общей памяти
        # Используем общую память через entity
        if (
            hasattr(self.entity, "shared_knowledge")
            and "player_weaknesses" in self.entity.shared_knowledge
        ):
            weaknesses = self.entity.shared_knowledge["player_weaknesses"]
            # Выбор атак, использующих слабости игрока
            pass

    def use_shared_knowledge(self):
        # Использование знаний из общей памяти
        if (
            hasattr(self.entity, "shared_knowledge")
            and "effective_vs_player" in self.entity.shared_knowledge
        ):
            effective_attacks = self.entity.shared_knowledge["effective_vs_player"]
            # Предпочтение эффективных атак
            pass


class BossDecisionMaker(DecisionMaker):
    def make_decisions(self, delta_time):
        # Принятие решений для боссов
        self.phase_transition_check()
        self.develop_special_tactics()

    def phase_transition_check(self):
        # Проверка условий для смены фазы
        pass

    def develop_special_tactics(self):
        # Разработка специальных тактик против игрока
        pass


class UtilityDecisionMaker(DecisionMaker):
    def __init__(self, entity):
        super().__init__(entity)
        self.actions = []

    def add_action(self, action, utility_func):
        self.actions.append((action, utility_func))

    def make_decisions(self, delta_time):
        if not self.actions:
            return

        # Рассчитываем полезность для каждого действия
        scored_actions = []
        for action, utility_func in self.actions:
            score = utility_func(self.entity)
            scored_actions.append((score, action))

        # Выбираем действие с максимальной полезностью
        scored_actions.sort(key=lambda x: x[0], reverse=True)
        best_action = scored_actions[0][1]
        best_action(self.entity)
