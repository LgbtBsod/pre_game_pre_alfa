from collections import defaultdict

class AICoordinator:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.groups = defaultdict(list)
            cls._instance.group_strategies = {}
            cls._instance.group_relations = {}  # Отношения между группами
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
        group_id = getattr(entity, 'group_id', None)
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
                            total_threat += enemy.ai.threat_level
        
        avg_threat = total_threat / len(entities) if entities else 0
        
        # Выбор стратегии
        if avg_threat > 15:
            strategy = "DEFENSIVE_FORMATION"
        elif avg_threat > 8:
            strategy = "FLANKING_MANEUVER"
        else:
            strategy = "STANDARD_ATTACK"
        
        self.group_strategies[group_id] = strategy
        
        # Определение лидера
        leader = max(entities, key=lambda e: e.level) if entities else None
        if leader:
            leader.role = "LEADER"
        
        # Распределение ролей
        for entity in entities:
            if entity != leader:
                if entity.health > 0.8 and entity.damage > 30:
                    entity.role = "ASSAULT"
                elif entity.health > 0.5 and entity.has_healing_abilities:
                    entity.role = "SUPPORT"
                else:
                    entity.role = "DEFENDER"
    
    def get_group_action(self, entity):
        strategy = self.group_strategies.get(entity.group_id, "STANDARD_ATTACK")
        return GroupTactics.get_action(strategy, entity.role)

class GroupTactics:
    TACTICS = {
        "FLANKING_MANEUVER": {
            "LEADER": "coordinate_flank",
            "ASSAULT": "flank_left",
            "SUPPORT": "suppressing_fire",
            "DEFENDER": "cover_flank"
        },
        "DEFENSIVE_FORMATION": {
            "LEADER": "call_reinforcements",
            "ASSAULT": "hold_position",
            "SUPPORT": "heal_allies",
            "DEFENDER": "protect_leader"
        },
        "STANDARD_ATTACK": {
            "LEADER": "direct_attack",
            "ASSAULT": "charge_enemy",
            "SUPPORT": "ranged_support",
            "DEFENDER": "guard_support"
        }
    }
    
    @classmethod
    def get_action(cls, strategy, role):
        return cls.TACTICS.get(strategy, {}).get(role, "idle")
    
    @classmethod
    def execute_action(cls, action, entity):
        if action == "coordinate_flank":
            entity.command_group("Flank the enemy!")
        elif action == "flank_left":
            entity.move_to_flank_position("left")
        elif action == "suppressing_fire":
            entity.suppressive_fire()
        elif action == "cover_flank":
            entity.guard_position(entity.group_flank_position)
        elif action == "call_reinforcements":
            entity.call_for_help()
        elif action == "hold_position":
            entity.hold_position()
        elif action == "heal_allies":
            entity.heal_nearby_allies()
        elif action == "protect_leader":
            entity.protect_leader()
        elif action == "direct_attack":
            entity.lead_attack()
        elif action == "charge_enemy":
            entity.charge_target()
        elif action == "ranged_support":
            entity.provide_ranged_support()
        elif action == "guard_support":
            entity.guard_teammates()