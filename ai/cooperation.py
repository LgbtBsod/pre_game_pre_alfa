from collections import defaultdict
import random
import math
import time


class AICoordinator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.groups = defaultdict(list)
            cls._instance.group_strategies = {}
            cls._instance.group_formations = {}
            cls._instance.group_relations = {}
            cls._instance.combat_log = []

            # Получаем настройки AI
            from config.unified_settings import get_ai_settings

            ai_settings = get_ai_settings()

            cls._instance.strategy_weights = {
                "FLANKING_MANEUVER": 0.3,
                "DEFENSIVE_FORMATION": 0.2,
                "STANDARD_ATTACK": 0.4,
                "AM_BUSH": 0.1,
            }
        return cls._instance

    def register_entity(self, entity, group_id="default"):
        if entity not in self.groups[group_id]:
            self.groups[group_id].append(entity)
            entity.group_id = group_id
            entity.role = "UNASSIGNED"

        # Инициализация отношений
        if group_id not in self.group_relations:
            self.group_relations[group_id] = {}
            for gid in self.groups.keys():
                if gid != group_id:
                    # По умолчанию все враги
                    self.group_relations[group_id][gid] = "ENEMY"

    def unregister_entity(self, entity):
        group_id = getattr(entity, "group_id", None)
        if group_id and group_id in self.groups and entity in self.groups[group_id]:
            self.groups[group_id].remove(entity)
            del entity.group_id

    def set_group_relation(self, group1, group2, relation):
        """Установить отношения между группами: 'ALLY', 'NEUTRAL', 'ENEMY'"""
        if group1 not in self.group_relations:
            self.group_relations[group1] = {}
        if group2 not in self.group_relations:
            self.group_relations[group2] = {}

        self.group_relations[group1][group2] = relation
        self.group_relations[group2][group1] = relation

    def get_relation(self, group1, group2):
        """Получить отношения между группами"""
        if group1 in self.group_relations and group2 in self.group_relations[group1]:
            return self.group_relations[group1][group2]
        return "ENEMY"  # По умолчанию враги

    def set_formation(self, group_id, formation_type):
        """Установить тактическое построение для группы"""
        formations = {
            "PHALANX": {
                "LEADER": "center",
                "DEFENDER": "front",
                "SUPPORT": "center",
                "ASSAULT": "flank",
            },
            "AM_BUSH": {
                "LEADER": "high_ground",
                "DEFENDER": "cover",
                "SUPPORT": "high_ground",
                "ASSAULT": "hidden",
            },
            "SKIRMISH": {
                "LEADER": "rear",
                "DEFENDER": "front",
                "SUPPORT": "scatter",
                "ASSAULT": "scatter",
            },
        }

        if formation_type in formations:
            self.group_formations[group_id] = formations[formation_type]
            return True
        return False

    def update_group_behavior(self, group_id):
        entities = self.groups[group_id]
        if not entities:
            return

        # Рассчет общей угрозы (учитываем только вражеские группы)
        total_threat = 0
        for entity in entities:
            # Учитываем угрозу от враждебных групп
            for gid, rel in self.group_relations.get(group_id, {}).items():
                if rel == "ENEMY" and gid in self.groups:
                    for enemy in self.groups[gid]:
                        if enemy.health > 0:
                            # Безопасная проверка атрибутов
                            combat_level = getattr(enemy, "combat_level", 1)
                            damage_output = getattr(enemy, "damage_output", 0)
                            threat_score = combat_level * (1.0 + damage_output / 100)

                            # Учет расстояния
                            distance = math.sqrt(
                                (entity.position[0] - enemy.position[0]) ** 2
                                + (entity.position[1] - enemy.position[1]) ** 2
                            )
                            distance_factor = max(0.1, 1.0 - distance / 50.0)
                            total_threat += threat_score * distance_factor

        avg_threat = total_threat / len(entities) if entities else 0

        # Выбор стратегии с учетом весов и предыдущего успеха
        available_strategies = [
            "FLANKING_MANEUVER",
            "DEFENSIVE_FORMATION",
            "STANDARD_ATTACK",
        ]
        if group_id in self.group_formations and "AM_BUSH" in GroupTactics.TACTICS:
            available_strategies.append("AM_BUSH")

        # Взвешенный случайный выбор
        strategy_weights = [self.strategy_weights[s] for s in available_strategies]
        total_weight = sum(strategy_weights)
        rand_val = random.uniform(0, total_weight)
        cumulative = 0
        selected_strategy = "STANDARD_ATTACK"

        for i, strategy in enumerate(available_strategies):
            cumulative += strategy_weights[i]
            if rand_val <= cumulative:
                selected_strategy = strategy
                break

        self.group_strategies[group_id] = selected_strategy

        # Определение лидера
        leader = max(entities, key=lambda e: e.level) if entities else None
        if leader:
            leader.role = "LEADER"

        # Распределение ролей (безопасные проверки)
        for entity in entities:
            if entity != leader:
                try:
                    health_ratio = float(entity.health) / max(
                        1.0, float(getattr(entity, "max_health", 100))
                    )
                except Exception:
                    health_ratio = 1.0
                damage_value = float(getattr(entity, "damage_output", 0))
                has_heal = bool(getattr(entity, "has_healing_abilities", False))
                if health_ratio > 0.8 and damage_value > 30:
                    entity.role = "ASSAULT"
                elif health_ratio > 0.5 and has_heal:
                    entity.role = "SUPPORT"
                else:
                    entity.role = "DEFENDER"

    def get_group_action(self, entity):
        strategy = self.group_strategies.get(entity.group_id, "STANDARD_ATTACK")
        return GroupTactics.get_action(strategy, entity.role)

    def log_combat_result(self, group_id, strategy, success):
        """Запись результатов боя для адаптации стратегий"""
        self.combat_log.append(
            {
                "group_id": group_id,
                "strategy": strategy,
                "success": success,
                "timestamp": time.time(),
            }
        )

        # Обновление весов стратегий
        if success:
            self.strategy_weights[strategy] = min(
                3.0, self.strategy_weights[strategy] * 1.2
            )
        else:
            self.strategy_weights[strategy] = max(
                0.2, self.strategy_weights[strategy] * 0.8
            )

    def request_support(self, requester, support_type):
        """Запрос поддержки у других групп"""
        for group_id, relation in self.group_relations[requester.group_id].items():
            if relation == "ALLY" and group_id in self.groups:
                # Найти ближайшую доступную группу
                closest_group = None
                min_distance = float("inf")

                for entity in self.groups[group_id]:
                    distance = math.sqrt(
                        (requester.position[0] - entity.position[0]) ** 2
                        + (requester.position[1] - entity.position[1]) ** 2
                    )
                    if distance < min_distance and entity.health > 0:
                        min_distance = distance
                        closest_group = entity.group_id

                if closest_group:
                    # Изменение стратегии группы поддержки
                    self.group_strategies[closest_group] = "SUPPORT_MISSION"
                    return f"Support from {closest_group} coming"
        return "No support available"


class GroupTactics:
    TACTICS = {
        "FLANKING_MANEUVER": {
            "LEADER": "coordinate_flank",
            "ASSAULT": "flank_left",
            "SUPPORT": "suppressing_fire",
            "DEFENDER": "cover_flank",
        },
        "DEFENSIVE_FORMATION": {
            "LEADER": "call_reinforcements",
            "ASSAULT": "hold_position",
            "SUPPORT": "heal_allies",
            "DEFENDER": "protect_leader",
        },
        "STANDARD_ATTACK": {
            "LEADER": "direct_attack",
            "ASSAULT": "charge_enemy",
            "SUPPORT": "ranged_support",
            "DEFENDER": "guard_support",
        },
        "AM_BUSH": {
            "LEADER": "set_ambush",
            "ASSAULT": "hidden_attack",
            "SUPPORT": "disable_escape",
            "DEFENDER": "cover_ambush",
        },
        "SUPPORT_MISSION": {
            "LEADER": "move_to_support",
            "ASSAULT": "engage_threat",
            "SUPPORT": "support_allies",
            "DEFENDER": "protect_support",
        },
    }

    FORMATION_POSITIONS = {
        "PHALANX": {
            "center": lambda leader: leader.position,
            "front": lambda leader: (leader.position[0], leader.position[1] + 2),
            "flank": lambda leader: (leader.position[0] + 3, leader.position[1]),
        },
        "AM_BUSH": {
            "high_ground": lambda leader: (leader.position[0], leader.position[1] + 5),
            "cover": lambda leader: (leader.position[0] - 2, leader.position[1]),
            "hidden": lambda leader: (
                leader.position[0] + random.uniform(-3, 3),
                leader.position[1] + random.uniform(-3, 3),
            ),
        },
    }

    @classmethod
    def get_action(cls, strategy, role):
        return cls.TACTICS.get(strategy, {}).get(role, "idle")

    @classmethod
    def get_formation_position(cls, formation, position_type, leader):
        if formation in cls.FORMATION_POSITIONS:
            if position_type in cls.FORMATION_POSITIONS[formation]:
                return cls.FORMATION_POSITIONS[formation][position_type](leader)
        return leader.position

    @classmethod
    def execute_action(cls, action, entity):
        if action == "coordinate_flank":
            entity.command_group("Flank the enemy!")
            targets = entity.find_enemies_in_cone(45, 10)
            if targets:
                entity.assign_targets(targets)
        elif action == "flank_left":
            entity.move_to_flank_position("left")
        elif action == "suppressing_fire":
            entity.suppressive_fire()
        elif action == "cover_flank":
            entity.guard_position(entity.group_flank_position)
        elif action == "call_reinforcements":
            result = AICoordinator().request_support(entity, "COMBAT")
            entity.show_message(result)
        elif action == "hold_position":
            entity.hold_position()
        elif action == "heal_allies":
            entity.heal_nearby_allies()
        elif action == "protect_leader":
            leader = AICoordinator().groups[entity.group_id][0]
            entity.protect_target(leader)
        elif action == "direct_attack":
            entity.lead_attack()
        elif action == "charge_enemy":
            entity.charge_target()
        elif action == "ranged_support":
            entity.provide_ranged_support()
        elif action == "guard_support":
            support_units = [
                e
                for e in AICoordinator().groups[entity.group_id]
                if e.role == "SUPPORT"
            ]
            if support_units:
                entity.guard_target(support_units[0])
        elif action == "set_ambush":
            entity.set_ambush_zone()
        elif action == "hidden_attack":
            entity.hide()
            entity.prepare_ambush()
        elif action == "disable_escape":
            entity.disable_escape_routes()
        elif action == "cover_ambush":
            entity.guard_ambush_area()
        elif action == "move_to_support":
            support_target = entity.find_support_target()
            if support_target:
                entity.move_to(support_target.position)
        elif action == "engage_threat":
            threats = entity.find_threats_to_allies()
            if threats:
                entity.attack(threats[0])
        elif action == "support_allies":
            entity.support_nearby_allies()
        elif action == "protect_support":
            support_units = [
                e
                for e in AICoordinator().groups[entity.group_id]
                if e.role == "SUPPORT"
            ]
            if support_units:
                entity.protect_target(support_units[0])
        else:  # idle
            entity.idle_behavior()


class SquadTactics:
    """Тактики для малых групп (2-5 существ)"""

    @staticmethod
    def execute_cover_fire(attacker, supporter):
        """Тактика прикрытия огнем"""
        if attacker.health > 0.5 and supporter.has_ability("SUPPRESSIVE_FIRE"):
            supporter.use_ability("SUPPRESSIVE_FIRE", attacker.target)
            attacker.attack(attacker.target)
            return True
        return False

    @staticmethod
    def execute_flanking_pair(attacker1, attacker2, target):
        """Двойной охват цели"""
        if attacker1.distance_to(target) < 10 and attacker2.distance_to(target) < 10:
            pos1 = (target.position[0] + 3, target.position[1])
            pos2 = (target.position[0] - 3, target.position[1])

            attacker1.move_to(pos1)
            attacker2.move_to(pos2)

            if attacker1.distance_to(pos1) < 1 and attacker2.distance_to(pos2) < 1:
                attacker1.attack(target)
                attacker2.attack(target)
                return True
        return False

    @staticmethod
    def execute_heal_chain(healer, protector, patient):
        """Защищенное лечение"""
        if healer.has_ability("HEAL") and protector.health > 0.4:
            protector.guard_position(healer.position)
            healer.use_ability("HEAL", patient)
            return True
        return False


class SiegeTactics:
    """Тактики для осадных ситуаций"""

    @staticmethod
    def execute_gate_breach(breacher, archers, gate):
        """Прорыв ворот"""
        if breacher.has_ability("BREACH") and all(
            a.has_ability("COVER_FIRE") for a in archers
        ):
            for archer in archers:
                archer.use_ability("COVER_FIRE", gate.position)
            breacher.use_ability("BREACH", gate)
            return True
        return False

    @staticmethod
    def execute_tower_defense(defenders, siege_weapons):
        """Оборона башни"""
        if len(defenders) >= 3 and any(sw.health > 0 for sw in siege_weapons):
            positions = SiegeTactics._calculate_defense_positions(defenders[0].position)
            for i, defender in enumerate(defenders):
                if i < len(positions):
                    defender.move_to(positions[i])
                    defender.use_ability("TOWER_DEFENSE")
            return True
        return False

    @staticmethod
    def _calculate_defense_positions(tower_position):
        return [
            (tower_position[0] + 2, tower_position[1]),
            (tower_position[0] - 2, tower_position[1]),
            (tower_position[0], tower_position[1] + 2),
        ]


class TacticalAnalyzer:
    """Анализ и адаптация тактик"""

    def __init__(self):
        self.tactic_success_rates = {}
        self.player_tendencies = {
            "aggression": 0.5,
            "defense": 0.5,
            "flanking": 0.3,
            "ranged": 0.4,
        }

    def update_tactic_success(self, tactic_name, success):
        if tactic_name not in self.tactic_success_rates:
            self.tactic_success_rates[tactic_name] = {"success": 0, "total": 0}

        self.tactic_success_rates[tactic_name]["total"] += 1
        if success:
            self.tactic_success_rates[tactic_name]["success"] += 1

    def get_success_rate(self, tactic_name):
        if tactic_name in self.tactic_success_rates:
            total = self.tactic_success_rates[tactic_name]["total"]
            if total > 0:
                return self.tactic_success_rates[tactic_name]["success"] / total
        return 0.5  # Значение по умолчанию

    def adapt_to_player_style(self, player_actions):
        # Анализ действий игрока
        action_counts = {
            "attack": sum(1 for a in player_actions if a.startswith("ATTACK")),
            "defend": sum(1 for a in player_actions if a.startswith("DEFEND")),
            "move": sum(1 for a in player_actions if a.startswith("MOVE")),
            "ability": sum(1 for a in player_actions if a.startswith("ABILITY")),
        }

        total_actions = max(1, sum(action_counts.values()))

        # Обновление тенденций
        self.player_tendencies["aggression"] = action_counts["attack"] / total_actions
        self.player_tendencies["defense"] = action_counts["defend"] / total_actions
        self.player_tendencies["flanking"] = (
            sum(1 for a in player_actions if "FLANK" in a) / total_actions
        )
        self.player_tendencies["ranged"] = (
            sum(1 for a in player_actions if "RANGED" in a) / total_actions
        )

    def recommend_counter_strategy(self):
        """Рекомендовать стратегию против игрока"""
        if self.player_tendencies["aggression"] > 0.7:
            return "DEFENSIVE_FORMATION"
        elif self.player_tendencies["defense"] > 0.6:
            return "FLANKING_MANEUVER"
        elif self.player_tendencies["ranged"] > 0.5:
            return "AM_BUSH"
        elif self.player_tendencies["flanking"] > 0.4:
            return "PHALANX"
        return "STANDARD_ATTACK"


class DynamicFormationSystem:
    """Динамическая система построений"""

    def __init__(self):
        self.formations = {}
        self.active_formations = {}

    def create_formation(self, name, positions):
        """Создать кастомное построение"""
        self.formations[name] = positions

    def activate_formation(self, group_id, formation_name, leader):
        """Активировать построение для группы"""
        if formation_name in self.formations:
            positions = {}
            for role, offset in self.formations[formation_name].items():
                positions[role] = (
                    leader.position[0] + offset[0],
                    leader.position[1] + offset[1],
                )

            self.active_formations[group_id] = {
                "formation": formation_name,
                "positions": positions,
                "leader_id": leader.id,
            }
            return True
        return False

    def update_formation_positions(self, leader):
        """Обновить позиции построения при движении лидера"""
        for group_id, data in self.active_formations.items():
            if data["leader_id"] == leader.id:
                for role, offset in self.formations[data["formation"]].items():
                    data["positions"][role] = (
                        leader.position[0] + offset[0],
                        leader.position[1] + offset[1],
                    )

    def get_position_for_role(self, group_id, role):
        """Получить позицию для роли в построении"""
        if group_id in self.active_formations:
            return self.active_formations[group_id]["positions"].get(role)
        return None
