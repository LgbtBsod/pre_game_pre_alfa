import random

class EmotionGeneticSynthesizer:
    def __init__(self, entity, genetic_profiles, abilities, effects):
        self.entity = entity
        self.genetic_profiles = genetic_profiles
        self.abilities = abilities
        self.effects = effects
        self.emotion_gene_triggers = {
            "RAGE": ["BERSERKER_GENE", "ADRENALINE_RUSH"],
            "FEAR": ["QUICK_ESCAPE", "PANIC_DODGE"],
            "CONFIDENCE": ["TACTICAL_INSIGHT", "LEADERSHIP_AURA"]
        }
        self.active_gene_effects = {}
        self.emotion_power = 1.0
    
    def update(self, delta_time: float):
        current_emotion = self.entity.emotion
        
        # Активация генов на основе эмоций
        for gene_id in self.emotion_gene_triggers.get(current_emotion, []):
            if gene_id in self.entity.genetic_profile:
                self.activate_gene(gene_id)
        
        # Деактивация генов, не соответствующих текущей эмоции
        for gene_id in list(self.active_gene_effects.keys()):
            if gene_id not in self.emotion_gene_triggers.get(current_emotion, []):
                self.deactivate_gene(gene_id)
        
        # Применение генетических эффектов к эмоциям
        self.apply_emotion_modifiers(delta_time)
        
        # Распространение эмоций
        if random.random() < 0.1 * delta_time:  # Шанс с учетом времени
            self.spread_emotion()
    
    def activate_gene(self, gene_id: str):
        if gene_id in self.active_gene_effects:
            return
        
        gene_data = self.entity.genetic_profile[gene_id]
        self.active_gene_effects[gene_id] = gene_data["effects"]
        
        # Применение немедленных эффектов
        for effect, value in gene_data["immediate_effects"].items():
            if effect == "heal":
                self.entity.health = min(self.entity.max_health, self.entity.health + value)
            elif effect == "damage_boost":
                if hasattr(self.entity, 'add_damage_boost'):
                    self.entity.add_damage_boost(value)
            elif effect == "mana_regen":
                self.entity.mana = min(self.entity.max_mana, self.entity.mana + value)
        
        # Начало длительных эффектов
        self.entity.add_effect(gene_data["effects"])
    
    def deactivate_gene(self, gene_id: str):
        if gene_id not in self.active_gene_effects:
            return
        
        # Удаление длительных эффектов
        self.entity.remove_effect(self.active_gene_effects[gene_id])
        del self.active_gene_effects[gene_id]
    
    def apply_emotion_modifiers(self, delta_time: float):
        # Модификация параметров эмоций на основе генов
        self.emotion_power = 1.0
        
        for gene_id in self.active_gene_effects:
            gene_data = self.entity.genetic_profile[gene_id]
            if "emotion_modifier" in gene_data:
                mod = gene_data["emotion_modifier"]
                if mod["emotion"] == self.entity.emotion:
                    self.emotion_power *= mod["multiplier"]
        
        # Усиление эффектов текущей эмоции
        if hasattr(self.entity, 'apply_emotion_effects'):
            self.entity.apply_emotion_effects(power=self.emotion_power)
    
    def spread_emotion(self):
        """Распространение эмоций на ближайших существ"""
        if not hasattr(self.entity, 'get_nearby_entities'):
            return
            
        nearby_entities = self.entity.get_nearby_entities(radius=10.0)
        for entity in nearby_entities:
            if hasattr(entity, 'team') and entity.team == self.entity.team:
                if random.random() < 0.3 * self.emotion_power:
                    entity.emotion = self.entity.emotion
                    # Усиление эмоции у цели
                    if hasattr(entity, 'ai') and hasattr(entity.ai, 'emotion_genetics'):
                        entity.ai.emotion_genetics.emotion_power = min(2.0, self.emotion_power * 1.2)
                        
    def add_emotion_synergy(self, emotion1, emotion2, synergy_effect):
        """Система синергии эмоций между сущностями"""
        if emotion1 not in self.emotion_synergies:
            self.emotion_synergies[emotion1] = {}
        self.emotion_synergies[emotion1][emotion2] = synergy_effect
        
    def apply_emotion_synergy(self):
        """Применить эффекты синергии"""
        for entity in self.entity.get_nearby_allies():
            if entity.emotion in self.emotion_synergies.get(self.entity.emotion, {}):
                effect = self.emotion_synergies[self.entity.emotion][entity.emotion]
                entity.apply_effect(effect)