"""
Игрок - основная управляемая сущность с AI системами.
"""

from entities.base_entity import BaseEntity


class Player(BaseEntity):
    """Игрок - управляемая сущность с AI"""
    
    def __init__(self, position: tuple = (0, 0)):
        super().__init__("player", position)
        
        # Специфичные для игрока параметры
        self.name = "Герой"
        self.gold = 100
        self.kills = 0
        self.deaths = 0
        
        # Настройки игрока
        self.auto_heal = True
        self.auto_use_potions = True
        self.auto_equip_better_items = True
        self.auto_learn_combat = True
        
        # AI специфичные настройки для игрока
        self.learning_rate = 0.2  # Игрок учится быстрее врагов
        self.combat_style_preference = "balanced"
        self.weapon_mastery = {}
        self.combat_experience = {}
        
        # Обновляем характеристики для игрока
        self.update_derived_stats()
        
        # Инициализируем AI для игрока
        self.initialize_player_ai()
    
    def initialize_player_ai(self):
        """Инициализирует AI системы для игрока"""
        # Настраиваем предпочтения оружия
        self.weapon_mastery = {
            "sword": 1.0,
            "axe": 1.0,
            "mace": 1.0,
            "bow": 1.0,
            "staff": 1.0,
            "dagger": 1.0
        }
        
        # Настраиваем опыт в бою
        self.combat_experience = {
            "melee": 0,
            "ranged": 0,
            "magic": 0,
            "defensive": 0,
            "aggressive": 0
        }
    
    def gain_experience(self, amount: int):
        """Получает опыт с дополнительной логикой для игрока"""
        super().gain_experience(amount)
        
        # Улучшаем AI с опытом
        self.improve_ai_with_experience(amount)
        
        # Здесь можно добавить уведомления, звуки и т.д.
    
    def improve_ai_with_experience(self, experience_gained: int):
        """Улучшает AI на основе полученного опыта"""
        # Увеличиваем мастерство в использованном оружии
        equipped_weapon = self.inventory_manager.equipment.get_equipped_item("weapon")
        if equipped_weapon:
            weapon_type = getattr(equipped_weapon, 'item_type', 'unknown')
            if weapon_type in self.weapon_mastery:
                self.weapon_mastery[weapon_type] += 0.1
        
        # Увеличиваем опыт в текущем стиле боя
        if self.combat_style_preference in self.combat_experience:
            self.combat_experience[self.combat_style_preference] += experience_gained
    
    def level_up(self):
        """Повышение уровня игрока"""
        super().level_up()
        
        # Разблокируем новые способности AI
        self.unlock_ai_abilities()
        
        # Здесь можно добавить уведомления, звуки, эффекты и т.д.
    
    def unlock_ai_abilities(self):
        """Разблокирует новые способности AI с уровнем"""
        if self.level >= 3:
            self.auto_equip_better_items = True
        if self.level >= 5:
            self.auto_learn_combat = True
        if self.level >= 10:
            # Разблокируем продвинутые тактики
            self.learned_tactics.extend(["weapon_switching", "tactical_retreat"])
        if self.level >= 15:
            # Разблокируем экспертные тактики
            self.learned_tactics.extend(["counter_attack", "defensive_stance"])
    
    def die(self):
        """Смерть игрока"""
        super().die()
        self.deaths += 1
        
        # Анализируем причины смерти для обучения
        self.analyze_death_cause()
        
        # Здесь можно добавить логику респауна, потери опыта и т.д.
    
    def analyze_death_cause(self):
        """Анализирует причину смерти для обучения"""
        # Получаем последние события из памяти
        recent_events = self.ai_memory.get_recent_events("damage_taken", 5)
        
        if recent_events:
            # Анализируем паттерны
            damage_types = [event.get("damage_type", "unknown") for event in recent_events]
            attacker_types = [event.get("attacker_type", "unknown") for event in recent_events]
            
            # Учимся на ошибках
            self.learn_from_death(damage_types, attacker_types)
    
    def learn_from_death(self, damage_types: list, attacker_types: list):
        """Учится на смерти"""
        # Увеличиваем предпочтение к защитным предметам
        for item_type in ["armor", "shield", "potion"]:
            if item_type not in self.item_preferences:
                self.item_preferences[item_type] = 0
            self.item_preferences[item_type] += 2
        
        # Сохраняем опыт смерти
        self.ai_memory.record_event("death_analysis", {
            "damage_types": damage_types,
            "attacker_types": attacker_types,
            "level": self.level
        })
    
    def kill_enemy(self, enemy):
        """Убивает врага"""
        self.kills += 1
        
        # Получаем опыт от врага
        if hasattr(enemy, 'experience_reward'):
            self.gain_experience(enemy.experience_reward)
        
        # Учимся на успешном убийстве
        self.learn_from_kill(enemy)
    
    def learn_from_kill(self, enemy):
        """Учится на успешном убийстве врага"""
        enemy_type = getattr(enemy, 'enemy_type', 'unknown')
        
        # Увеличиваем опыт против этого типа врага
        if enemy_type not in self.combat_experience:
            self.combat_experience[enemy_type] = 0
        self.combat_experience[enemy_type] += 1
        
        # Анализируем эффективность использованного оружия
        equipped_weapon = self.inventory_manager.equipment.get_equipped_item("weapon")
        if equipped_weapon:
            weapon_type = getattr(equipped_weapon, 'item_type', 'unknown')
            if weapon_type in self.weapon_mastery:
                self.weapon_mastery[weapon_type] += 0.05
        
        # Сохраняем опыт
        self.ai_memory.record_event("successful_kill", {
            "enemy_type": enemy_type,
            "weapon_used": getattr(equipped_weapon, 'item_type', 'unknown') if equipped_weapon else "none",
            "level": self.level
        })
    
    def use_consumable(self, item):
        """Использует расходник с обучением"""
        success = super().use_consumable(item)
        
        if success:
            # Анализируем эффективность использования
            item_type = getattr(item, 'item_type', 'unknown')
            effects = getattr(item, 'effects', {})
            
            # Учимся на использовании предмета
            self.learn_item_effectiveness(item_type, effects)
        
        return success
    
    def learn_item_effectiveness(self, item_type: str, effects: dict):
        """Учится эффективности предметов"""
        # Анализируем эффекты предмета
        healing_value = effects.get("heal", 0)
        mana_value = effects.get("restore_mana", 0)
        
        # Обновляем предпочтения на основе эффективности
        if healing_value > 20:
            if "healing_potion" not in self.item_preferences:
                self.item_preferences["healing_potion"] = 0
            self.item_preferences["healing_potion"] += 1
        
        if mana_value > 10:
            if "mana_potion" not in self.item_preferences:
                self.item_preferences["mana_potion"] = 0
            self.item_preferences["mana_potion"] += 1
    
    def auto_heal_if_needed(self):
        """Автоматическое лечение при необходимости с учетом обучения"""
        if not self.auto_heal:
            return
        
        health_percentage = self.get_health_percentage()
        
        # Используем обученные пороги
        heal_threshold = 0.3  # Базовый порог
        if "healing_potion" in self.item_preferences and self.item_preferences["healing_potion"] > 5:
            heal_threshold = 0.4  # Более консервативный порог при опыте
        
        if health_percentage < heal_threshold:
            # Ищем лучшие лечебные предметы на основе обучения
            best_healing_item = self.find_best_healing_item()
            if best_healing_item:
                self.use_consumable(best_healing_item)
    
    def find_best_healing_item(self):
        """Находит лучший лечебный предмет на основе обучения"""
        consumables = self.inventory_manager.inventory.get_consumables()
        best_item = None
        best_score = 0
        
        for item in consumables:
            if hasattr(item, 'effects') and 'heal' in item.effects:
                healing_value = item.effects["heal"]
                item_type = getattr(item, 'item_type', 'unknown')
                
                # Вычисляем оценку предмета
                score = healing_value
                
                # Добавляем бонус за предпочтения
                if item_type in self.item_preferences:
                    score += self.item_preferences[item_type] * 2
                
                if score > best_score:
                    best_score = score
                    best_item = item
        
        return best_item
    
    def auto_equip_better_items(self):
        """Автоматически экипирует лучшие предметы"""
        if not self.auto_equip_better_items:
            return
        
        # Проверяем каждый слот экипировки
        for slot_name in ["weapon", "armor", "helmet", "gloves", "boots"]:
            self.optimize_equipment_slot(slot_name)
    
    def optimize_equipment_slot(self, slot_name: str):
        """Оптимизирует экипировку в указанном слоте"""
        current_item = self.inventory_manager.equipment.get_equipped_item(slot_name)
        inventory_items = self.inventory_manager.inventory.items
        
        best_item = None
        best_score = 0
        
        for item in inventory_items:
            if self.can_equip_to_slot(item, slot_name):
                score = self.calculate_item_score(item, slot_name)
                if score > best_score:
                    best_score = score
                    best_item = item
        
        # Экипируем лучший предмет
        if best_item and (not current_item or best_score > self.calculate_item_score(current_item, slot_name)):
            self.inventory_manager.equip_item(best_item, slot_name)
    
    def can_equip_to_slot(self, item, slot_name: str) -> bool:
        """Проверяет, можно ли экипировать предмет в слот"""
        item_type = getattr(item, 'item_type', 'unknown')
        
        slot_requirements = {
            "weapon": ["sword", "axe", "mace", "bow", "staff", "dagger"],
            "armor": ["armor"],
            "helmet": ["helmet"],
            "gloves": ["gloves"],
            "boots": ["boots"]
        }
        
        return item_type in slot_requirements.get(slot_name, [])
    
    def calculate_item_score(self, item, slot_name: str) -> float:
        """Вычисляет оценку предмета для слота"""
        score = 0.0
        
        # Базовые характеристики
        if hasattr(item, 'base_damage'):
            score += item.base_damage * 2
        if hasattr(item, 'defense'):
            score += item.defense * 3
        if hasattr(item, 'durability'):
            score += item.durability * 0.1
        
        # Бонусы за мастерство
        item_type = getattr(item, 'item_type', 'unknown')
        if item_type in self.weapon_mastery:
            score *= self.weapon_mastery[item_type]
        
        # Бонусы за предпочтения
        if item_type in self.item_preferences:
            score += self.item_preferences[item_type] * 5
        
        return score
    
    def update(self, delta_time: float):
        """Обновляет игрока"""
        super().update(delta_time)
        
        # Автоматические действия
        self.auto_heal_if_needed()
        self.auto_equip_better_items()
        
        # Обновляем AI системы
        self.update_player_ai(delta_time)
    
    def update_player_ai(self, delta_time: float):
        """Обновляет AI системы игрока"""
        # Анализируем текущую ситуацию
        self.analyze_combat_situation()
        
        # Принимаем тактические решения
        self.make_tactical_decisions()
    
    def analyze_combat_situation(self):
        """Анализирует текущую боевую ситуацию"""
        # Анализируем здоровье и ресурсы
        health_percentage = self.get_health_percentage()
        mana_percentage = self.get_mana_percentage()
        
        # Определяем стиль боя на основе ситуации
        if health_percentage < 0.3:
            self.combat_style_preference = "defensive"
        elif mana_percentage > 0.7:
            self.combat_style_preference = "magic"
        else:
            self.combat_style_preference = "balanced"
    
    def make_tactical_decisions(self):
        """Принимает тактические решения"""
        # Здесь можно добавить логику принятия тактических решений
        # Например, выбор оружия, использование способностей и т.д.
        pass
    
    def get_health_percentage(self) -> float:
        """Возвращает процент здоровья"""
        return self.combat_stats_manager.get_health_percentage()
    
    def get_mana_percentage(self) -> float:
        """Возвращает процент маны"""
        return self.combat_stats_manager.get_mana_percentage()
    
    def get_stamina_percentage(self) -> float:
        """Возвращает процент выносливости"""
        return self.combat_stats_manager.get_stamina_percentage()
    
    def get_weapon_mastery(self, weapon_type: str) -> float:
        """Возвращает мастерство в использовании оружия"""
        return self.weapon_mastery.get(weapon_type, 1.0)
    
    def get_combat_experience(self, combat_type: str) -> int:
        """Возвращает опыт в определенном типе боя"""
        return self.combat_experience.get(combat_type, 0)