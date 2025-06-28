from systems.ai.advanced_controller import AdvancedAIController

class Spell:
    def __init__(self, name, cost, effect, damage=0, healing=0):
        self.name = name
        self.cost = cost
        self.effect = effect
        self.damage = damage
        self.healing = healing

class Inventory:
    def __init__(self):
        self.items = []
    
    def add_item(self, item):
        self.items.append(item)
    
    def has_consumable(self, item_type):
        return any(item.type == item_type for item in self.items)
    
    def use(self, item_id):
        for item in self.items:
            if item.id == item_id:
                item.use()
                if item.consumable:
                    self.items.remove(item)
                return True
        return False
    
    def get_best_healing_item(self):
        best_heal = None
        for item in self.items:
            if item.type == "HEAL" and (not best_heal or item.power > best_heal.power):
                best_heal = item
        return best_heal

class Entity:
    def __init__(self, entity_id, position=(0, 0)):
        self.id = entity_id
        self.position = position
        self.health = 1.0
        self.max_health = 1.0
        self.stamina = 1.0
        self.mana = 1.0
        self.max_mana = 1.0
        self.emotion = "NEUTRAL"
        self.genetic_profile = {}
        self.inventory = Inventory()
        self.effects = []
        self.spells = {}
        self.ai_controller = AdvancedAIController(self)
        self.combat_level = 1
        self.damage_output = 10
        self.last_health = self.health
        self.last_mana = self.mana
        self.nearby_enemies = []
        self.nearby_allies = []
        self.team = "NEUTRAL"
        self.is_player = False
        self.is_boss = False
        self.distance_to_player = float('inf')
        self.has_healing_abilities = False
    
    def update(self, delta_time):
        self.last_health = self.health
        self.last_mana = self.mana
        
        if self.ai_controller:
            self.ai_controller.update(delta_time)
        
        self._update_effects(delta_time)
        self._update_nearby_entities()
        self.distance_to_player = self._calculate_distance_to_player()
    
    def _update_effects(self, delta_time):
        for effect in self.effects[:]:
            effect["duration"] -= delta_time
            if effect["duration"] <= 0:
                self._remove_effect(effect)
    
    def _update_nearby_entities(self):
        self.nearby_enemies = self.get_nearby_entities(radius=15.0, enemy_only=True)
        self.nearby_allies = self.get_nearby_entities(radius=15.0, ally_only=True)
    
    def get_nearby_entities(self, radius, enemy_only=False, ally_only=False):
        # В реальной игре здесь будет пространственный запрос
        return []
    
    def _calculate_distance_to_player(self):
        return float('inf')
    
    def add_effect(self, effect):
        self.effects.append(effect)
    
    def _remove_effect(self, effect):
        if effect in self.effects:
            self.effects.remove(effect)
    
    def attack_nearest(self):
        if self.nearby_enemies:
            target = self.nearby_enemies[0]
            self.attack(target)
            self.last_action_success = random.random() > 0.3
    
    def attack(self, target):
        damage = self.damage_output
        # Применение модификаторов от эмоций и эффектов
        if self.emotion == "RAGE":
            damage *= 1.3
        target.take_damage(damage)
        self.last_action_success = True
        self.last_damage_dealt = damage
    
    def take_damage(self, amount):
        self.health = max(0, self.health - amount / self.max_health)
    
    def use_best_healing_item(self):
        best_heal = self.inventory.get_best_healing_item()
        if best_heal:
            self.use_item(best_heal.id)
    
    def use_item(self, item_id):
        # Реальная логика будет зависеть от предмета
        self.health = min(self.max_health, self.health + 0.2)
        self.last_action_success = True
    
    def cast_spell(self, spell_name):
        if spell_name in self.spells:
            spell = self.spells[spell_name]
            if self.mana >= spell.cost:
                self.mana -= spell.cost
                self.last_mana_used = spell.cost
                
                # Применение эффекта заклинания
                if spell.effect:
                    self.apply_spell_effect(spell)
                
                self.last_action_success = True
                return True
        self.last_action_success = False
        return False
    
    def apply_spell_effect(self, spell):
        if spell.damage > 0:
            # Поиск цели для атакующего заклинания
            target = self.find_nearest_enemy()
            if target:
                target.take_damage(spell.damage)
                self.last_damage_dealt = spell.damage
        
        if spell.healing > 0:
            # Лечение себя или союзников
            if self.health < self.max_health:
                self.health = min(self.max_health, self.health + spell.healing)
            else:
                # Лечение ближайшего союзника
                ally = self.find_injured_ally()
                if ally:
                    ally.health = min(ally.max_health, ally.health + spell.healing)
    
    def find_nearest_enemy(self):
        if self.nearby_enemies:
            return self.nearby_enemies[0]
        return None
    
    def find_injured_ally(self):
        for ally in self.nearby_allies:
            if ally.health < ally.max_health * 0.8:
                return ally
        return None
    
    def move_in_direction(self, direction):
        # Логика движения
        pass
    
    def apply_emotion_effects(self, power=1.0):
        # Применение эффектов эмоций
        if self.emotion == "RAGE":
            self.damage_output *= 1.0 + 0.2 * power
        elif self.emotion == "FEAR":
            self.move_speed *= 1.0 + 0.3 * power