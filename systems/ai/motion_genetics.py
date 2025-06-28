import random

class EmotionGeneticSynthesizer:
    def __init__(self, entity):
        self.entity = entity
        self.emotion_gene_triggers = {
            "RAGE": ["BERSERKER_GENE", "ADRENALINE_RUSH"],
            "FEAR": ["QUICK_ESCAPE", "PANIC_DODGE"],
            "CONFIDENCE": ["TACTICAL_INSIGHT", "LEADERSHIP_AURA"]
        }
        self.active_gene_effects = {}
        self.emotion_power = 1.0
    
    def update(self, delta_time):
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
        if random.random() < 0.1:  # 10% chance per second
            self.spread_emotion()
    
    def activate_gene(self, gene_id):
        if gene_id in self.active_gene_effects:
            return
        
        gene_data = self.entity.genetic_profile[gene_id]
        self.active_gene_effects[gene_id] = gene_data["effects"]
        
        # Применение немедленных эффектов
        for effect, value in gene_data["immediate_effects"].items():
            if effect == "heal":
                self.entity.health = min(1.0, self.entity.health + value)
            elif effect == "damage_boost":
                self.entity.add_damage_boost(value)
            elif effect == "mana_regen":
                self.entity.mana = min(self.entity.max_mana, self.entity.mana + value)
        
        # Начало длительных эффектов
        self.entity.add_effects(gene_data["effects"])
    
    def deactivate_gene(self, gene_id):
        if gene_id not in self.active_gene_effects:
            return
        
        # Удаление длительных эффектов
        self.entity.remove_effects(self.active_gene_effects[gene_id])
        del self.active_gene_effects[gene_id]
    
    def apply_emotion_modifiers(self, delta_time):
        # Модификация параметров эмоций на основе генов
        self.emotion_power = 1.0
        
        for gene_id in self.active_gene_effects:
            gene_data = self.entity.genetic_profile[gene_id]
            if "emotion_modifier" in gene_data:
                mod = gene_data["emotion_modifier"]
                if mod["emotion"] == self.entity.emotion:
                    self.emotion_power *= mod["multiplier"]
        
        # Усиление эффектов текущей эмоции
        self.entity.apply_emotion_effects(power=self.emotion_power)
    
    def spread_emotion(self):
        """Распространение эмоций на ближайших существ"""
        nearby_entities = self.entity.get_nearby_entities(radius=10.0)
        for entity in nearby_entities:
            if entity.team == self.entity.team:  # Только союзники
                if random.random() < 0.3 * self.emotion_power:  # Шанс заражения
                    entity.emotion = self.entity.emotion
                    # Усиление эмоции у цели
                    entity.ai.emotion_genetics.emotion_power = min(2.0, self.emotion_power * 1.2)