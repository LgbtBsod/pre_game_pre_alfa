#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
УНИФИЦИРОВАННЫЙ КЛАСС ПЕРСОНАЖА
Объединяет функционал character.py и enhanced_character.py
Соблюдает принцип единой ответственности
"""

import math
import time
from typing import Dict, List, Optional, Any
from panda3d.core import CardMaker, Vec3, Vec4, TransparencyAttrib

# Импорты систем
from systems.attributes import AttributeSystem, AttributeSet, BaseAttribute, DerivedStat
from systems.skills import SkillSystem, SkillType, SkillCategory
from systems.effects import EffectSystem, Effect, EffectType
from systems.evolution import EvolutionSystem, MutationType, EvolutionStage
from systems.combat import CombatSystem, AttackType, DamageType, CombatState
from systems.social import SocialSystem, DialogueType, QuestType, QuestStatus
from systems.memory import MemorySystem, MemoryType, MemoryCategory
from systems.content_generator import ContentGenerator
from systems.ai_agent import AIAgent, EmotionType
from systems.advanced_ai import AdvancedAISystem, AIType, AIState, MemoryType as AIMemoryType
from utils.logging_system import get_logger, log_system_event, log_error, log_performance

class Character:
    """Базовый класс персонажа"""
    
    def __init__(self, game, x=0, y=0, z=0, color=(1, 1, 1, 1)):
        self.game = game
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        self.node = None
        
        # Инициализация систем
        self.attribute_system = AttributeSystem()
        self.skill_system = SkillSystem()
        self.effect_system = EffectSystem()
        self.evolution_system = EvolutionSystem()
        self.combat_system = CombatSystem()
        self.social_system = SocialSystem()
        self.memory_system = MemorySystem()
        self.content_generator = ContentGenerator()
        
        # Инициализация инвентаря (через улучшенную систему предметов)
        self.inventory_id = f"character_{id(self)}"
        if hasattr(game, 'item_system'):
            game.item_system.create_inventory(self.inventory_id)
        
        # Инициализация логгера
        self.logger = get_logger("character")
        
        # Базовые атрибуты персонажа
        self.base_attributes = AttributeSet(
            strength=12.0,
            agility=10.0,
            intelligence=8.0,
            vitality=15.0,
            wisdom=9.0,
            charisma=7.0,
            luck=10.0,
            endurance=11.0
        )
        
        # Инициализация навыков для персонажа
        self.entity_id = f"player_{id(self)}"
        self.skill_system.initialize_entity_skills(self.entity_id)
        
        # Инициализация эффектов
        self.effect_system.initialize_entity_effects(self.entity_id)
        
        # Инициализация эволюции
        self.evolution_system.initialize_entity_evolution(self.entity_id, "warrior")
        
        # Инициализация боевой системы
        self.combat_system.initialize_entity_combat(self.entity_id)
        
        # Инициализация социальных систем
        self.social_system.initialize_player_social(self.entity_id)
        
        # Инициализация памяти
        self.memory_system.initialize_entity_memory(self.entity_id)
        
        # Инициализация ИИ систем
        self.advanced_ai_system = AdvancedAISystem()
        self.advanced_ai_system.create_ai_entity(self.entity_id, AIType.HYBRID, AIState.IDLE)
        
        # Инициализация ИИ агента
        self.ai_agent = AIAgent(self)
        
        # Логируем создание персонажа
        log_system_event("character", "character_created", {
            "entity_id": self.entity_id,
            "position": (x, y, z),
            "base_attributes": self.base_attributes.to_dict()
        })
        
        # Уровень и опыт
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100
        
        # Рассчитываем производные характеристики
        self._update_derived_stats()
        
        # Текущие значения (могут изменяться в процессе игры)
        self.health = self.max_health
        self.mana = self.max_mana
        self.stamina = self.max_stamina
        
        # Боевые параметры
        self.attack_cooldown = 0
        self.attack_cooldown_time = 1.0 / self.attack_speed  # Кулдаун зависит от скорости атаки
        self.attack_range = 2.0
    
    def _update_derived_stats(self):
        """Обновление производных характеристик на основе атрибутов и эффектов"""
        # Получаем все характеристики от системы атрибутов
        stats = self.attribute_system.calculate_derived_stats(self.entity_id, self.base_attributes)
        
        # Применяем эффекты навыков
        skill_effects = self.skill_system.get_skill_effects(self.entity_id)
        for effect_type, value in skill_effects.items():
            if effect_type in stats:
                stats[effect_type] += value
        
        # Применяем активные эффекты
        active_effects = self.effect_system.get_entity_effects(self.entity_id)
        for effect in active_effects:
            if effect.effect_type in stats:
                if effect.is_percentage:
                    stats[effect.effect_type] *= (1 + effect.value / 100)
                else:
                    stats[effect.effect_type] += effect.value
        
        # Применяем бонусы эволюции
        evolution_bonuses = self.evolution_system.get_evolution_bonuses(self.entity_id)
        for bonus_type, value in evolution_bonuses.items():
            if bonus_type in stats:
                stats[bonus_type] += value
        
        # Применяем модификаторы мутаций
        mutation_modifiers = self.evolution_system.get_mutation_modifiers(self.entity_id)
        for modifier_type, value in mutation_modifiers.items():
            if modifier_type in stats:
                stats[modifier_type] += value
        
        # Обновляем характеристики персонажа
        self.max_health = max(1, stats.get(DerivedStat.HEALTH.value, 100))
        self.max_mana = max(1, stats.get(DerivedStat.MANA.value, 100))
        self.max_stamina = max(1, stats.get(DerivedStat.STAMINA.value, 100))
        self.physical_damage = stats.get(DerivedStat.PHYSICAL_DAMAGE.value, 20)
        self.magical_damage = stats.get(DerivedStat.MAGICAL_DAMAGE.value, 0)
        self.defense = stats.get(DerivedStat.DEFENSE.value, 0)
        self.attack_speed = stats.get(DerivedStat.ATTACK_SPEED.value, 1.0)
        self.health_regen = stats.get(DerivedStat.HEALTH_REGEN.value, 1.0)
        self.mana_regen = stats.get(DerivedStat.MANA_REGEN.value, 5.0)
        self.stamina_regen = stats.get(DerivedStat.STAMINA_REGEN.value, 10.0)
        self.critical_chance = stats.get(DerivedStat.CRITICAL_CHANCE.value, 5.0)
        self.critical_damage = stats.get(DerivedStat.CRITICAL_DAMAGE.value, 150.0)
        self.dodge_chance = stats.get(DerivedStat.DODGE_CHANCE.value, 0.0)
        self.magic_resistance = stats.get(DerivedStat.MAGIC_RESISTANCE.value, 0.0)
        self.max_weight = stats.get(DerivedStat.MAX_WEIGHT.value, 100.0)
        self.speed = stats.get(DerivedStat.MOVEMENT_SPEED.value, 5.0)
        
        # Обновляем кулдаун атаки
        self.attack_cooldown_time = 1.0 / self.attack_speed
        
    def create_character(self):
        """Создание визуального представления персонажа"""
        from panda3d.core import CardMaker
        
        # Создаем персонажа как простой куб
        character = self.game.render.attachNewNode("character")
        
        # Основное тело (куб) - используем простой подход
        self.create_visible_cube(character, "body", 0, 0, 0.5, 0.6, 0.6, 0.6, self.color)
        
        # Голова
        head_color = (self.color[0] * 0.8, self.color[1] * 0.8, self.color[2] * 0.8, self.color[3])
        self.create_visible_cube(character, "head", 0, 0, 1.2, 0.4, 0.4, 0.4, head_color)
        
        # Ноги
        leg_color = (self.color[0] * 0.6, self.color[1] * 0.6, self.color[2] * 0.6, self.color[3])
        self.create_visible_cube(character, "leg1", -0.2, 0, 0.2, 0.2, 0.2, 0.4, leg_color)
        self.create_visible_cube(character, "leg2", 0.2, 0, 0.2, 0.2, 0.2, 0.4, leg_color)
        
        # Руки
        arm_color = (self.color[0] * 0.7, self.color[1] * 0.7, self.color[2] * 0.7, self.color[3])
        self.create_visible_cube(character, "arm1", -0.4, 0, 0.8, 0.2, 0.2, 0.4, arm_color)
        self.create_visible_cube(character, "arm2", 0.4, 0, 0.8, 0.2, 0.2, 0.4, arm_color)
        
        character.setPos(self.x, self.y, self.z)
        self.node = character
        return character
        
    def create_visible_cube(self, parent, name, x, y, z, width, height, depth, color):
        """Создание видимого куба с правильной ориентацией"""
        from panda3d.core import CardMaker
        
        # Создаем куб из 6 граней с правильной ориентацией
        cube = parent.attachNewNode(name)
        
        # Передняя грань (обращена к камере)
        cm = CardMaker(f"{name}_front")
        cm.setFrame(-width/2, width/2, -height/2, height/2)
        front = cube.attachNewNode(cm.generate())
        front.setPos(0, depth/2, 0)
        front.setColor(*color)
        
        # Задняя грань
        cm = CardMaker(f"{name}_back")
        cm.setFrame(-width/2, width/2, -height/2, height/2)
        back = cube.attachNewNode(cm.generate())
        back.setPos(0, -depth/2, 0)
        back.setHpr(0, 180, 0)
        back.setColor(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, color[3])
        
        # Левая грань
        cm = CardMaker(f"{name}_left")
        cm.setFrame(-depth/2, depth/2, -height/2, height/2)
        left = cube.attachNewNode(cm.generate())
        left.setPos(-width/2, 0, 0)
        left.setHpr(0, -90, 0)
        left.setColor(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8, color[3])
        
        # Правая грань
        cm = CardMaker(f"{name}_right")
        cm.setFrame(-depth/2, depth/2, -height/2, height/2)
        right = cube.attachNewNode(cm.generate())
        right.setPos(width/2, 0, 0)
        right.setHpr(0, 90, 0)
        right.setColor(color[0] * 0.6, color[1] * 0.6, color[2] * 0.6, color[3])
        
        # Верхняя грань
        cm = CardMaker(f"{name}_top")
        cm.setFrame(-width/2, width/2, -depth/2, depth/2)
        top = cube.attachNewNode(cm.generate())
        top.setPos(0, 0, height/2)
        top.setHpr(0, 0, -90)
        top.setColor(color[0] * 1.2, color[1] * 1.2, color[2] * 1.2, color[3])
        
        # Нижняя грань
        cm = CardMaker(f"{name}_bottom")
        cm.setFrame(-width/2, width/2, -depth/2, depth/2)
        bottom = cube.attachNewNode(cm.generate())
        bottom.setPos(0, 0, -height/2)
        bottom.setHpr(0, 0, 90)
        bottom.setColor(color[0] * 0.4, color[1] * 0.4, color[2] * 0.4, color[3])
        
        cube.setPos(x, y, z)
        return cube
        
    def create_simple_cube(self, parent, name, x, y, z, width, height, depth, color):
        """Создание простого куба"""
        from panda3d.core import CardMaker
        
        # Создаем куб из 6 граней
        cube = parent.attachNewNode(name)
        
        # Передняя грань
        cm = CardMaker(f"{name}_front")
        cm.setFrame(-width/2, width/2, -height/2, height/2)
        front = cube.attachNewNode(cm.generate())
        front.setPos(0, depth/2, 0)
        front.setColor(*color)
        
        # Задняя грань
        cm = CardMaker(f"{name}_back")
        cm.setFrame(-width/2, width/2, -height/2, height/2)
        back = cube.attachNewNode(cm.generate())
        back.setPos(0, -depth/2, 0)
        back.setHpr(0, 180, 0)
        back.setColor(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, color[3])
        
        # Левая грань
        cm = CardMaker(f"{name}_left")
        cm.setFrame(-depth/2, depth/2, -height/2, height/2)
        left = cube.attachNewNode(cm.generate())
        left.setPos(-width/2, 0, 0)
        left.setHpr(0, -90, 0)
        left.setColor(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8, color[3])
        
        # Правая грань
        cm = CardMaker(f"{name}_right")
        cm.setFrame(-depth/2, depth/2, -height/2, height/2)
        right = cube.attachNewNode(cm.generate())
        right.setPos(width/2, 0, 0)
        right.setHpr(0, 90, 0)
        right.setColor(color[0] * 0.6, color[1] * 0.6, color[2] * 0.6, color[3])
        
        # Верхняя грань
        cm = CardMaker(f"{name}_top")
        cm.setFrame(-width/2, width/2, -depth/2, depth/2)
        top = cube.attachNewNode(cm.generate())
        top.setPos(0, 0, height/2)
        top.setHpr(0, 0, -90)
        top.setColor(color[0] * 1.2, color[1] * 1.2, color[2] * 1.2, color[3])
        
        # Нижняя грань
        cm = CardMaker(f"{name}_bottom")
        cm.setFrame(-width/2, width/2, -depth/2, depth/2)
        bottom = cube.attachNewNode(cm.generate())
        bottom.setPos(0, 0, -height/2)
        bottom.setHpr(0, 0, 90)
        bottom.setColor(color[0] * 0.4, color[1] * 0.4, color[2] * 0.4, color[3])
        
        cube.setPos(x, y, z)
        return cube
        
    def create_cube_face(self, parent, name, x1, x2, y1, y2, px, py, pz, h, p, r, color):
        """Создание грани куба"""
        from panda3d.core import CardMaker
        cm = CardMaker(name)
        cm.setFrame(x1, x2, y1, y2)
        face = parent.attachNewNode(cm.generate())
        face.setPos(px, py, pz)
        face.setHpr(h, p, r)
        face.setColor(*color)
        return face
        
    def move_to(self, x, y, z=None):
        """Перемещение персонажа"""
        self.x = x
        self.y = y
        if z is not None:
            self.z = z
        if self.node:
            self.node.setPos(self.x, self.y, self.z)
    
    def move_by(self, dx, dy, dz=0, dt=0.016):
        """Перемещение персонажа на относительное расстояние"""
        # Используем скорость из характеристик
        move_speed = self.speed * dt
        self.x += dx * move_speed
        self.y += dy * move_speed
        self.z += dz * move_speed
        if self.node:
            self.node.setPos(self.x, self.y, self.z)
            
    def get_position(self):
        """Получение позиции персонажа"""
        return (self.x, self.y, self.z)
    
    def get_distance_to(self, target):
        """Получение расстояния до цели"""
        import math
        if hasattr(target, 'x') and hasattr(target, 'y'):
            return math.sqrt((self.x - target.x)**2 + (self.y - target.y)**2)
        return float('inf')
    
    def get_ai_stats(self):
        """Получение статистики ИИ"""
        if hasattr(self, 'ai_agent'):
            return {
                'emotion': self.ai_agent.current_emotion.name if self.ai_agent.current_emotion else 'NONE',
                'personality': {
                    'aggression': self.ai_agent.personality.get('aggression', 0),
                    'caution': self.ai_agent.personality.get('caution', 0),
                    'curiosity': self.ai_agent.personality.get('curiosity', 0),
                    'social': self.ai_agent.personality.get('social', 0),
                    'intelligence': self.ai_agent.personality.get('intelligence', 0),
                    'adaptability': self.ai_agent.personality.get('adaptability', 0)
                },
                'memory_count': len(self.memory_system.get_memories(self.entity_id)),
                'ai_type': 'HYBRID',
                'decision_count': getattr(self.ai_agent, 'decision_count', 0),
                'last_decision': getattr(self.ai_agent, 'last_decision', 'NONE')
            }
        return {'ai_type': 'NONE'}
    
    def get_ai_emotional_state(self):
        """Получение эмоционального состояния ИИ"""
        if hasattr(self, 'ai_agent'):
            return {
                'current_emotion': self.ai_agent.current_emotion.name if self.ai_agent.current_emotion else 'NONE',
                'active_emotions': [emotion.name for emotion in self.ai_agent.active_emotions],
                'emotional_stability': self.ai_agent.emotional_stability,
                'mood': self.ai_agent.mood
            }
        return {'current_emotion': 'NONE', 'active_emotions': [], 'emotional_stability': 0.5, 'mood': 0.5}
    
    def add_ai_emotion(self, emotion_type, intensity, duration, source):
        """Добавление эмоции ИИ"""
        if hasattr(self, 'ai_agent'):
            self.ai_agent.add_emotion(emotion_type, intensity, duration, source)
        
    def take_damage(self, damage, damage_type="physical"):
        """Получение урона с учетом защиты"""
        # Применяем защиту
        if damage_type == "physical":
            actual_damage = max(1, damage - self.defense)
        elif damage_type == "magical":
            actual_damage = max(1, damage * (1 - self.magic_resistance / 100))
        else:
            actual_damage = damage
        
        # Проверяем уклонение
        if damage_type == "physical" and self.dodge_chance > 0:
            import random
            if random.random() * 100 < self.dodge_chance:
                print("Dodged!")
                return False
        
        self.health = max(0, self.health - actual_damage)
        return self.health <= 0
        
    def heal(self, amount):
        """Лечение"""
        self.health = min(self.max_health, self.health + amount)
        
    def restore_mana(self, amount):
        """Восстановление маны"""
        self.mana = min(self.max_mana, self.mana + amount)
        
    def restore_stamina(self, amount):
        """Восстановление выносливости"""
        self.stamina = min(self.max_stamina, self.stamina + amount)
        
    def use_mana(self, amount):
        """Использование маны"""
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False
        
    def use_stamina(self, amount):
        """Использование выносливости"""
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False
        
    def is_alive(self):
        """Проверка, жив ли персонаж"""
        return self.health > 0
        
    def attack(self, target):
        """Атака цели с учетом критических ударов"""
        if self.attack_cooldown <= 0 and self.is_alive():
            # Проверяем расстояние до цели
            if hasattr(target, 'get_position'):
                target_x, target_y, target_z = target.get_position()
            elif hasattr(target, 'x') and hasattr(target, 'y') and hasattr(target, 'z'):
                target_x, target_y, target_z = target.x, target.y, target.z
            else:
                return False
            distance = math.sqrt((self.x - target_x)**2 + (self.y - target_y)**2)
            
            if distance <= self.attack_range:
                # Рассчитываем урон
                base_damage = self.physical_damage
                
                # Проверяем критический удар
                import random
                is_critical = random.random() * 100 < self.critical_chance
                if is_critical:
                    base_damage *= (self.critical_damage / 100)
                    print("Critical hit!")
                
                # Атакуем цель
                target.take_damage(base_damage, "physical")
                self.attack_cooldown = self.attack_cooldown_time
                print(f"Player attacked enemy for {base_damage:.1f} damage!")
                return True
        return False
    
    def use_skill(self, skill_id):
        """Использование навыка"""
        if not self.is_alive():
            return False
        
        effects = self.skill_system.use_skill(
            self.entity_id, skill_id, self.mana, self.stamina
        )
        
        if effects:
            # Применяем эффекты навыка
            for effect in effects:
                if effect.effect_type == "heal":
                    self.heal(effect.value)
                elif effect.effect_type == "physical_damage":
                    # Находим ближайшего врага и атакуем
                    # Это упрощенная реализация
                    pass
                elif effect.effect_type == "magical_damage":
                    # Магический урон
                    pass
            
            # Тратим ресурсы
            skill = self.skill_system.get_entity_skills(self.entity_id).get(skill_id)
            if skill:
                self.mana -= skill.mana_cost
                self.stamina -= skill.stamina_cost
                self.health -= skill.hp_cost
            
            return True
        return False
        
    def update_cooldown(self, dt):
        """Обновление кулдауна атаки и восстановление ресурсов"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        # Восстановление ресурсов
        self.restore_mana(self.mana_regen * dt)
        self.restore_stamina(self.stamina_regen * dt)
        self.heal(self.health_regen * dt)
        
        # Обновляем эффекты
        self.effect_system.update_effects(self.entity_id, dt)
        
        # Обновляем систему памяти
        self.memory_system.update_memory_system(dt)
        
        # Обновляем ИИ системы
        self._update_ai_systems(dt)
        
        # Обновляем характеристики если изменились эффекты
        self._update_derived_stats()
    
    def add_experience(self, amount):
        """Добавление опыта"""
        self.experience += amount
        if self.experience >= self.experience_to_next_level:
            self.level_up()
    
    def level_up(self):
        """Повышение уровня"""
        self.level += 1
        self.experience -= self.experience_to_next_level
        self.experience_to_next_level = int(self.experience_to_next_level * 1.2)
        
        # Увеличиваем атрибуты при повышении уровня
        self.base_attributes.strength += 1
        self.base_attributes.agility += 1
        self.base_attributes.intelligence += 1
        self.base_attributes.vitality += 2
        self.base_attributes.wisdom += 1
        self.base_attributes.charisma += 1
        self.base_attributes.luck += 1
        self.base_attributes.endurance += 1
        
        # Обновляем характеристики
        self._update_derived_stats()
        
        # Восстанавливаем здоровье и ману
        self.health = self.max_health
        self.mana = self.max_mana
        self.stamina = self.max_stamina
        
        print(f"Level up! Now level {self.level}")
    
    def apply_effect(self, effect_type, value, duration=-1, source="unknown"):
        """Применение эффекта к персонажу"""
        effect = Effect(
            effect_id=f"{effect_type}_{int(time.time())}",
            effect_type=effect_type,
            value=value,
            duration=duration,
            source=source
        )
        self.effect_system.add_effect(self.entity_id, effect)
        self._update_derived_stats()
    
    def get_attributes(self):
        """Получение текущих атрибутов"""
        return self.base_attributes.to_dict()
    
    def get_stats(self):
        """Получение всех характеристик"""
        return {
            'health': self.health,
            'max_health': self.max_health,
            'mana': self.mana,
            'max_mana': self.max_mana,
            'stamina': self.stamina,
            'max_stamina': self.max_stamina,
            'level': self.level,
            'experience': self.experience,
            'experience_to_next': self.experience_to_next_level,
            'physical_damage': self.physical_damage,
            'magical_damage': self.magical_damage,
            'defense': self.defense,
            'attack_speed': self.attack_speed,
            'critical_chance': self.critical_chance,
            'critical_damage': self.critical_damage,
            'dodge_chance': self.dodge_chance,
            'magic_resistance': self.magic_resistance,
            'speed': self.speed
        }
    
    def perform_combat_attack(self, target, attack_id: str):
        """Выполнение боевой атаки"""
        if not self.is_alive():
            return {'success': False, 'message': 'Character is dead'}
        
        target_stats = target.get_stats() if hasattr(target, 'get_stats') else {}
        result = self.combat_system.perform_attack(
            self.entity_id, target.entity_id, attack_id, self.get_stats(), target_stats
        )
        
        if result.get('hit', False):
            # Применяем урон к цели
            damage = result['damage']
            target.take_damage(damage, result.get('damage_type', 'physical'))
            
            # Добавляем опыт за атаку
            self.add_experience(5)
            
            # Добавляем очки эволюции
            self.evolution_system.add_evolution_points(self.entity_id, 1)
        
        return result
    
    def apply_mutation(self, mutation_id: str):
        """Применение мутации"""
        return self.evolution_system.apply_mutation(self.entity_id, mutation_id)
    
    def random_mutation(self, mutation_type: MutationType = MutationType.RANDOM):
        """Случайная мутация"""
        return self.evolution_system.random_mutation(self.entity_id, mutation_type)
    
    def can_evolve(self):
        """Проверка возможности эволюции"""
        return self.evolution_system.can_evolve(self.entity_id, self.get_stats())
    
    def evolve(self):
        """Эволюция персонажа"""
        if self.evolution_system.evolve(self.entity_id, self.get_stats()):
            # Обновляем характеристики после эволюции
            self._update_derived_stats()
            print("Evolution successful!")
            return True
        return False
    
    def start_dialogue(self, npc_id: str, dialogue_id: str = "greeting"):
        """Начало диалога"""
        return self.social_system.start_dialogue(self.entity_id, npc_id, dialogue_id)
    
    def select_dialogue_option(self, option_id: str):
        """Выбор варианта ответа в диалоге"""
        return self.social_system.select_dialogue_option(self.entity_id, option_id)
    
    def start_quest(self, quest_id: str):
        """Начало квеста"""
        return self.social_system.start_quest(self.entity_id, quest_id)
    
    def buy_item(self, npc_id: str, item_id: str, quantity: int = 1):
        """Покупка предмета"""
        return self.social_system.buy_item(self.entity_id, npc_id, item_id, quantity)
    
    def sell_item(self, npc_id: str, item_id: str, quantity: int = 1):
        """Продажа предмета"""
        return self.social_system.sell_item(self.entity_id, npc_id, item_id, quantity)
    
    def get_evolution_info(self):
        """Получение информации об эволюции"""
        return self.evolution_system.get_evolution_info(self.entity_id)
    
    def get_combat_stats(self):
        """Получение боевых характеристик"""
        return self.combat_system.get_combat_stats(self.entity_id)
    
    def get_available_attacks(self):
        """Получение доступных атак"""
        return self.combat_system.get_available_attacks(self.entity_id)
    
    def get_player_quests(self):
        """Получение квестов игрока"""
        return self.social_system.get_player_quests(self.entity_id)
    
    def get_inventory_contents(self):
        """Получение содержимого инвентаря (нормализовано под формат ИИ/UI)."""
        items = self.get_inventory_items()
        normalized = []
        for entry in items:
            normalized.append({
                'slot_index': entry.get('slot_index'),
                'item': {
                    'item_id': entry.get('item_id'),
                    'name': entry.get('name'),
                    'type': entry.get('item_type'),
                    'rarity': entry.get('rarity'),
                    'effects': [],
                    'description': entry.get('description', '')
                },
                'quantity': entry.get('quantity', 1),
                'durability': entry.get('durability', 100)
            })
        return normalized
    
    def add_memory(self, memory_type: MemoryType, category: MemoryCategory, title: str, 
                   description: str, data: dict = None, importance: float = 0.5):
        """Добавление воспоминания"""
        memory_id = self.memory_system.add_memory(
            self.entity_id, memory_type, category, title, description, data, importance
        )
        log_system_event("character", "memory_added", {
            "entity_id": self.entity_id,
            "memory_id": memory_id,
            "memory_type": memory_type.value,
            "title": title
        })
        return memory_id
    
    def get_memories(self, memory_type: MemoryType = None, category: MemoryCategory = None, limit: int = 10):
        """Получение воспоминаний"""
        return self.memory_system.get_memories(self.entity_id, memory_type, category, limit)
    
    def get_memory_stats(self):
        """Получение статистики памяти"""
        return self.memory_system.get_memory_stats(self.entity_id)
    
    def generate_content(self, content_type: str, level: int = None, rarity: str = None, count: int = 1):
        """Генерация контента"""
        session_id = f"session_{self.entity_id}"
        start_time = time.time()
        
        content = self.content_generator.generate_content(session_id, content_type, level, rarity, count)
        
        generation_time = time.time() - start_time
        log_performance("character", f"content_generation_{content_type}", generation_time, {
            "content_type": content_type,
            "count": count,
            "session_id": session_id
        })
        
        return content
    
    def generate_weapon(self, level: int = None, rarity: str = None):
        """Генерация оружия"""
        return self.content_generator.generate_weapon(f"session_{self.entity_id}", level, rarity)
    
    def generate_enemy(self, level: int = None, enemy_type: str = None):
        """Генерация врага"""
        return self.content_generator.generate_enemy(f"session_{self.entity_id}", level, enemy_type)
    
    def generate_quest(self, level: int = None, quest_type: str = None):
        """Генерация квеста"""
        return self.content_generator.generate_quest(f"session_{self.entity_id}", level, quest_type)
            
    def destroy(self):
        """Уничтожение персонажа"""
        if self.node:
            self.node.removeNode()
            self.node = None
    
    def _update_ai_systems(self, dt):
        """Обновление ИИ систем"""
        # Обновляем ИИ агента
        self.ai_agent.update(dt)
        
        # Обновляем продвинутую ИИ систему
        game_state = self._get_game_state_for_ai()
        decision = self.advanced_ai_system.make_decision(self.entity_id, game_state)
        
        if decision:
            self._execute_ai_decision(decision)
    
    def _get_game_state_for_ai(self) -> Dict[str, Any]:
        """Получение состояния игры для ИИ"""
        return {
            'position': (self.x, self.y, self.z),
            'health': self.health,
            'max_health': self.max_health,
            'mana': self.mana,
            'max_mana': self.max_mana,
            'stamina': self.stamina,
            'max_stamina': self.max_stamina,
            'level': self.level,
            'experience': self.experience,
            'nearest_enemy': self._get_nearest_enemy_info(),
            'time_of_day': 0.5,  # Время дня (0-1)
            'weather_intensity': 0.0,  # Интенсивность погоды
            'available_skills': self._get_available_skills(),
            'inventory_items': self._get_inventory_summary(),
            'equipment': self._get_equipment_summary()
        }
    
    def _get_nearest_enemy_info(self) -> Optional[Dict[str, Any]]:
        """Получение информации о ближайшем враге"""
        # В упрощенной реализации возвращаем None
        # В реальной игре нужно получать из game_manager
        return None
    
    def _get_available_skills(self) -> List[str]:
        """Получение доступных навыков"""
        skills = self.skill_system.get_entity_skills(self.entity_id)
        available = []
        for skill_id, skill in skills.items():
            if (self.mana >= skill.mana_cost and 
                self.stamina >= skill.stamina_cost and 
                self.health >= skill.hp_cost):
                available.append(skill_id)
        return available
    
    def _get_inventory_summary(self) -> Dict[str, Any]:
        """Получение сводки инвентаря"""
        inventory = self.get_inventory_contents()
        return {
            'total_items': len(inventory),
            'healing_items': len([item for item in inventory if 'heal' in item.get('effects', [])]),
            'weapons': len([item for item in inventory if item.get('type') == 'weapon']),
            'armor': len([item for item in inventory if item.get('type') == 'armor'])
        }
    
    def _get_equipment_summary(self) -> Dict[str, Any]:
        """Получение сводки экипировки"""
        equipment = self.get_equipment()
        return {
            'weapon_equipped': equipment.get('weapon') is not None,
            'armor_equipped': equipment.get('armor') is not None,
            'accessory_equipped': equipment.get('accessory') is not None
        }

    def get_equipment(self) -> Dict[str, Any]:
        """Возвращает сводку экипированных предметов по ключам weapon/armor/accessory."""
        summary = {'weapon': None, 'armor': None, 'accessory': None}
        if hasattr(self.game, 'item_system') and hasattr(self, 'entity_id'):
            stats = self.game.item_system.get_equipment_stats(self.entity_id)
            equipped = stats.get('equipped_items', {}) if isinstance(stats, dict) else {}
            # Пробуем извлечь по слотам
            # Оружие
            for key in ['main_hand', 'off_hand']:
                if equipped.get(key):
                    summary['weapon'] = equipped.get(key)
                    break
            # Броня
            for key in ['head', 'chest', 'legs', 'feet', 'hands']:
                if equipped.get(key):
                    summary['armor'] = equipped.get(key)
                    break
            # Аксессуары
            for key in ['neck', 'ring_1', 'ring_2']:
                if equipped.get(key):
                    summary['accessory'] = equipped.get(key)
                    break
        return summary
    
    def _execute_ai_decision(self, decision: str):
        """Выполнение решения ИИ"""
        try:
            if decision == "attack":
                self._ai_attack()
            elif decision == "chase":
                self._ai_chase()
            elif decision == "patrol":
                self._ai_patrol()
            elif decision == "flee":
                self._ai_flee()
            elif decision == "search":
                self._ai_search()
            elif decision == "use_skill":
                self._ai_use_skill()
            elif decision == "use_item":
                self._ai_use_item()
            elif decision == "equip_item":
                self._ai_equip_item()
            elif decision == "idle":
                self._ai_idle()
            
            # Добавляем память о решении
            self.advanced_ai_system.add_memory(
                self.entity_id, 
                AIMemoryType.MOVEMENT, 
                {'decision': decision, 'timestamp': time.time()},
                0.5
            )
            
        except Exception as e:
            print(f"Error executing AI decision {decision}: {e}")
    
    def _ai_attack(self):
        """ИИ атака"""
        # В упрощенной реализации просто логируем
        print(f"AI {self.entity_id} decided to attack")
    
    def _ai_chase(self):
        """ИИ преследование"""
        # Двигаемся в случайном направлении (имитация преследования)
        import random
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        self.move_by(dx, dy, 0, 0.016)
        print(f"AI {self.entity_id} is chasing")
    
    def _ai_patrol(self):
        """ИИ патрулирование"""
        # Двигаемся по патрульному маршруту
        import random
        dx = random.uniform(-0.5, 0.5)
        dy = random.uniform(-0.5, 0.5)
        self.move_by(dx, dy, 0, 0.016)
        print(f"AI {self.entity_id} is patrolling")
    
    def _ai_flee(self):
        """ИИ бегство"""
        # Двигаемся в противоположном направлении от угрозы
        import random
        dx = random.uniform(-2, 2)
        dy = random.uniform(-2, 2)
        self.move_by(dx, dy, 0, 0.016)
        print(f"AI {self.entity_id} is fleeing")
    
    def _ai_search(self):
        """ИИ поиск"""
        # Ищем что-то в окружении
        print(f"AI {self.entity_id} is searching")
    
    def _ai_use_skill(self):
        """ИИ использование навыка"""
        available_skills = self._get_available_skills()
        if available_skills:
            skill_id = available_skills[0]  # Используем первый доступный навык
            self.use_skill(skill_id)
            print(f"AI {self.entity_id} used skill {skill_id}")
    
    def _ai_use_item(self):
        """ИИ использование предмета"""
        # Ищем подходящий предмет для использования (расходник)
        inventory = self.get_inventory_contents()
        for item_data in inventory:
            item = item_data['item']
            if item.get('type') == 'consumable' and self.health < self.max_health * 0.5:
                slot_index = item_data.get('slot_index')
                if slot_index is not None:
                    self.use_item_from_inventory(slot_index)
                    print(f"AI {self.entity_id} used consumable from slot {slot_index}")
                    break
    
    def _ai_equip_item(self):
        """ИИ экипировка предмета"""
        # Ищем подходящее снаряжение и экипируем из инвентаря в подходящий слот
        inventory = self.get_inventory_contents()
        current_eq = self.get_equipment()
        for item_data in inventory:
            item = item_data['item']
            slot_index = item_data.get('slot_index')
            if slot_index is None:
                continue
            item_type = item.get('type')
            if item_type in ['weapon', 'armor', 'accessory'] and not current_eq.get(item_type):
                try:
                    from core.enhanced_item_system import EquipmentSlot
                    slot_map = {
                        'weapon': EquipmentSlot.MAIN_HAND,
                        'armor': EquipmentSlot.CHEST,
                        'accessory': EquipmentSlot.NECK
                    }
                    equipment_slot = slot_map[item_type]
                    if self.equip_item_from_inventory(slot_index, equipment_slot):
                        print(f"AI {self.entity_id} equipped {item.get('name', 'item')} from slot {slot_index}")
                        break
                except Exception:
                    continue
    
    def _ai_idle(self):
        """ИИ бездействие"""
        # Просто отдыхаем
        print(f"AI {self.entity_id} is idle")
    
    def add_ai_emotion(self, emotion_type: EmotionType, intensity: float, duration: float, source: str):
        """Добавление эмоции к ИИ агенту"""
        self.ai_agent.add_emotion(emotion_type, intensity, duration, source)
    
    def get_ai_emotional_state(self) -> Dict[str, Any]:
        """Получение эмоционального состояния ИИ"""
        return self.ai_agent.get_emotional_state()
    
    def get_ai_stats(self) -> Dict[str, Any]:
        """Получение статистики ИИ"""
        return self.ai_agent.get_ai_stats()
    
    def learn_from_experience(self, experience_data: Dict[str, Any]):
        """Обучение ИИ на основе опыта"""
        self.advanced_ai_system.learn_from_experience(self.entity_id, experience_data)
    
    def evolve_ai(self, fitness_score: float):
        """Эволюция ИИ"""
        self.advanced_ai_system.evolve_ai(self.entity_id, fitness_score)
    
    def save_ai_state(self):
        """Сохранение состояния ИИ"""
        self.advanced_ai_system.save_ai_state(self.entity_id)
    
    def load_ai_state(self) -> bool:
        """Загрузка состояния ИИ"""
        return self.advanced_ai_system.load_ai_state(self.entity_id)
    
    # === МЕТОДЫ ИНВЕНТАРЯ ===
    
    def add_item_to_inventory(self, item, quantity: int = 1) -> bool:
        """Добавление предмета в инвентарь"""
        if hasattr(self.game, 'item_system'):
            return self.game.item_system.add_item_to_inventory(self.inventory_id, item, quantity)
        return False
    
    def remove_item_from_inventory(self, item_id: str, quantity: int = 1) -> bool:
        """Удаление предмета из инвентаря"""
        if hasattr(self.game, 'item_system'):
            return self.game.item_system.remove_item_from_inventory(self.inventory_id, item_id, quantity)
        return False
    
    def get_inventory_items(self) -> List[Dict[str, Any]]:
        """Получение списка предметов в инвентаре"""
        if hasattr(self.game, 'item_system'):
            return self.game.item_system.get_inventory_items(self.inventory_id)
        return []
    
    def get_inventory_stats(self) -> Dict[str, Any]:
        """Получение статистик инвентаря"""
        if hasattr(self.game, 'item_system'):
            return self.game.item_system.get_inventory_stats(self.inventory_id)
        return {}
    
    def equip_item_from_inventory(self, slot_index: int, equipment_slot) -> bool:
        """Экипировка предмета из инвентаря"""
        if hasattr(self.game, 'item_system'):
            return self.game.item_system.equip_item_from_inventory(self.inventory_id, slot_index, equipment_slot)
        return False
    
    def unequip_item_to_inventory(self, equipment_slot) -> bool:
        """Снятие предмета в инвентарь"""
        if hasattr(self.game, 'item_system'):
            return self.game.item_system.unequip_item_to_inventory(self.inventory_id, equipment_slot)
        return False
    
    def use_item_from_inventory(self, slot_index: int) -> bool:
        """Использование предмета из инвентаря"""
        if hasattr(self.game, 'item_system'):
            items = self.get_inventory_items()
            if slot_index < len(items):
                item_id = items[slot_index]["item_id"]
                # Получаем предмет из кэша
                if item_id in self.game.item_system.items_cache:
                    item = self.game.item_system.items_cache[item_id]
                    return self.game.item_system.use_item(self.inventory_id, item)
        return False
    
    # === МЕТОДЫ ПОИСКА МАЯКА ===
    
    def search_for_lighthouse(self) -> Optional[Dict[str, Any]]:
        """Поиск маяка"""
        if hasattr(self.game, 'lighthouse_system'):
            # Получаем позицию персонажа
            position = (self.x, self.y, self.z)
            
            # Получаем уровень памяти ИИ
            ai_memory_level = 0
            if hasattr(self, 'entity_id') and hasattr(self.game, 'ai_memory_system'):
                ai_memory_level = self.game.ai_memory_system.get_entity_memory_level(self.entity_id)
            
            # Пытаемся обнаружить маяк
            discovery = self.game.lighthouse_system.attempt_discovery(
                self.inventory_id, position, "player", ai_memory_level
            )
            
            if discovery:
                # Записываем в память ИИ
                if hasattr(self, 'entity_id') and hasattr(self.game, 'ai_memory_system'):
                    self.game.ai_memory_system.add_memory(
                        self.entity_id, "lighthouse_discovery", {
                            "lighthouse_id": discovery.entity_id,
                            "distance": discovery.distance,
                            "method": discovery.discovery_method.value
                        }, 0.8
                    )
                
                return self.game.lighthouse_system.get_lighthouse_info(self.inventory_id)
            
            return None
        return None
    
    def get_lighthouse_info(self) -> Optional[Dict[str, Any]]:
        """Получение информации о маяке"""
        if hasattr(self.game, 'lighthouse_system'):
            return self.game.lighthouse_system.get_lighthouse_info(self.inventory_id)
        return None
    
    def get_navigation_hints(self) -> List[str]:
        """Получение подсказок для навигации к маяку"""
        if hasattr(self.game, 'lighthouse_system'):
            position = (self.x, self.y, self.z)
            return self.game.lighthouse_system.get_navigation_hints(self.inventory_id, position)
        return []
    
    def attempt_lighthouse_activation(self) -> bool:
        """Попытка активации маяка"""
        if hasattr(self.game, 'lighthouse_system'):
            # Получаем позицию персонажа
            position = (self.x, self.y, self.z)
            
            # Получаем инвентарь
            inventory_items = [item["item_id"] for item in self.get_inventory_items()]
            
            # Получаем уровень памяти ИИ
            ai_memory_level = 0
            if hasattr(self, 'entity_id') and hasattr(self.game, 'ai_memory_system'):
                ai_memory_level = self.game.ai_memory_system.get_entity_memory_level(self.entity_id)
            
            # Пытаемся активировать маяк
            success = self.game.lighthouse_system.attempt_activation(
                self.inventory_id, position, inventory_items, ai_memory_level
            )
            
            if success:
                # Записываем в память ИИ
                if hasattr(self, 'entity_id') and hasattr(self.game, 'ai_memory_system'):
                    self.game.ai_memory_system.add_memory(
                        self.entity_id, "lighthouse_activation", {
                            "lighthouse_id": self.game.lighthouse_system.active_lighthouse.lighthouse_id,
                            "success": True
                        }, 1.0
                    )
            
            return success
        return False
