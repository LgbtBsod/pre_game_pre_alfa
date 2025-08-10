from .entity import Entity
import random

class NPCEnemy(Entity):
    def __init__(self, entity_id, position, group_id=None):
        super().__init__(entity_id, position)
        self.team = "ENEMY"
        self.group_id = group_id or f"group_{random.randint(1, 3)}"
        self.role = "ASSAULT"
        self.is_boss = False
        self.personality = self._generate_enemy_personality()
        self.has_healing_abilities = random.random() > 0.7
        self.damage = random.randint(20, 50)
        self.level = random.randint(1, 10)
        self._init_spells()
    
    def _generate_enemy_personality(self):
        return {
            "aggression": random.uniform(0.5, 0.95),
            "caution": random.uniform(0.1, 0.4),
            "intelligence": random.uniform(0.3, 0.7)
        }
    
    def _init_spells(self):
        if random.random() > 0.5:
            self.spells["Fireball"] = {"name": "Fireball", "mana_cost": 20, "type": "damage", "damage": 40}
        if self.has_healing_abilities:
            self.spells["Heal"] = {"name": "Heal", "mana_cost": 15, "type": "healing", "healing": 30}

class BossEnemy(NPCEnemy):
    def __init__(self, entity_id, position):
        super().__init__(entity_id, position, group_id="boss")
        self.is_boss = True
        self.phase = 1
        self.phase_transitions = {
            1: lambda: self.health < 0.7,
            2: lambda: self.health < 0.4
        }
        self.level = 20
        self.damage = 100
        self._init_boss_spells()
    
    def _init_boss_spells(self):
        self.spells["Meteor"] = {"name": "Meteor", "mana_cost": 40, "type": "damage", "damage": 80}
        self.spells["Shield"] = {"name": "Shield", "mana_cost": 30, "type": "defense"}
        self.spells["MassHeal"] = {"name": "MassHeal", "mana_cost": 50, "type": "healing", "healing": 50}
    
    def update(self, delta_time):
        if self.phase in self.phase_transitions:
            if self.phase_transitions[self.phase]():
                self._enter_next_phase()
        
        super().update(delta_time)
    
    def _enter_next_phase(self):
        self.phase += 1
        # GameState.trigger_event("BOSS_PHASE_CHANGE", {"boss_id": self.id, "phase": self.phase})
        
        if self.phase == 2:
            self.ai_controller.behavior_tree = self._create_phase2_behavior()
        elif self.phase == 3:
            self.ai_controller.behavior_tree = self._create_phase3_behavior()
    
    def _create_phase2_behavior(self):
        from ai.behavior_tree import Selector, Sequence, CheckLowHealth, UseHealingItem, AttackNearestEnemy
        return Selector([
            Sequence([
                CheckLowHealth(0.4),
                UseHealingItem()
            ]),
            AttackNearestEnemy()
        ])
    
    def _create_phase3_behavior(self):
        from ai.behavior_tree import Selector, Sequence, CheckLowHealth, UseHealingItem, AttackNearestEnemy
        return Selector([
            CheckLowHealth(0.3),
            UseHealingItem(),
            AttackNearestEnemy()
        ])

class PlayerEntity(Entity):
    def __init__(self, entity_id, position=(0, 0)):
        super().__init__(entity_id, position)
        self.is_player = True
        self.team = "PLAYER"
        self.spells["Firebolt"] = {"name": "Firebolt", "mana_cost": 10, "type": "damage", "damage": 25}
        self.spells["Heal"] = {"name": "Heal", "mana_cost": 15, "type": "healing", "healing": 30}