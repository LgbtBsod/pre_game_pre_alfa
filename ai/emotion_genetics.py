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
        # Безопасная проверка атрибута emotion
        if not hasattr(self.entity, 'emotion'):
            # Если атрибута нет, создаем базовую эмоцию
            self.entity.emotion = "NEUTRAL"
        
        current_emotion = self.entity.emotion
        
        # Безопасная проверка genetic_profile
        if not hasattr(self.entity, 'genetic_profile'):
            self.entity.genetic_profile = {}
        
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
        
        gene_data = self.entity.genetic_profile.get(gene_id, {})
        if not gene_data:
            return
            
        effects = gene_data.get("effects", [])
        self.active_gene_effects[gene_id] = effects
        
        # Применение немедленных эффектов
        immediate_effects = gene_data.get("immediate_effects", {})
        for effect, value in immediate_effects.items():
            if effect == "heal":
                if hasattr(self.entity, 'health') and hasattr(self.entity, 'max_health'):
                    self.entity.health = min(self.entity.max_health, self.entity.health + value)
            elif effect == "damage_boost":
                if hasattr(self.entity, 'add_damage_boost'):
                    self.entity.add_damage_boost(value)
            elif effect == "mana_regen":
                if hasattr(self.entity, 'mana') and hasattr(self.entity, 'max_mana'):
                    self.entity.mana = min(self.entity.max_mana, self.entity.mana + value)
        
        # Начало длительных эффектов
        if hasattr(self.entity, 'add_effect') and effects:
            self.entity.add_effect(effects)
    
    def deactivate_gene(self, gene_id: str):
        if gene_id not in self.active_gene_effects:
            return
        
        # Удаление длительных эффектов
        effects = self.active_gene_effects[gene_id]
        if hasattr(self.entity, 'remove_effect') and effects:
            self.entity.remove_effect(effects)
        del self.active_gene_effects[gene_id]
    
    def apply_emotion_modifiers(self, delta_time: float):
        # Модификация параметров эмоций на основе генов
        self.emotion_power = 1.0
        
        for gene_id in self.active_gene_effects:
            gene_data = self.entity.genetic_profile.get(gene_id, {})
            if "emotion_modifier" in gene_data:
                mod = gene_data["emotion_modifier"]
                if mod.get("emotion") == self.entity.emotion:
                    self.emotion_power *= mod.get("multiplier", 1.0)
        
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