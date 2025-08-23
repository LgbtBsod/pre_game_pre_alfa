"""
Универсальная сущность с интегрированными системами эффектов, эмоций, генетики и ИИ.
Объединяет все основные системы игры в единую архитектуру.
"""

import random
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

# Условный импорт pygame
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    pygame = None

from .effect_system import EffectSystem, EffectDatabase
from .genetic_system import AdvancedGeneticSystem
from .emotion_system import AdvancedEmotionSystem
from .ai_system import AdaptiveAISystem

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Типы сущностей"""
    PLAYER = "player"
    ENEMY = "enemy"
    NPC = "npc"
    CREATURE = "creature"
    BOSS = "boss"
    ELITE = "elite"
    MINION = "minion"


class DamageType(Enum):
    """Типы урона"""
    PHYSICAL = "physical"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"
    MAGIC = "magic"
    RADIATION = "radiation"
    COSMIC = "cosmic"


@dataclass
class EntityStats:
    """Характеристики сущности"""
    health: float = 100.0
    max_health: float = 100.0
    stamina: float = 100.0
    max_stamina: float = 100.0
    mana: float = 100.0
    max_mana: float = 100.0
    damage: float = 20.0
    defense: float = 15.0
    speed: float = 1.0
    accuracy: float = 0.8
    critical_chance: float = 0.05
    critical_multiplier: float = 2.0
    sheild: float = 0.0
    max_sheild: float = 100.0
    
    def get_health_percent(self) -> float:
        """Получение процента здоровья"""
        return self.health / self.max_health if self.max_health > 0 else 0.0
    
    def get_stamina_percent(self) -> float:
        """Получение процента выносливости"""
        return self.stamina / self.max_stamina if self.max_stamina > 0 else 0.0
    
    def is_alive(self) -> bool:
        """Проверка, жива ли сущность"""
        return self.health > 0
    
    def can_act(self) -> bool:
        """Проверка, может ли сущность действовать"""
        return self.is_alive() and self.stamina > 0


@dataclass
class EntityPosition:
    """Позиция сущности"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def distance_to(self, other_position) -> float:
        """Расчёт расстояния до другой позиции"""
        import math
        dx = self.x - other_position.x
        dy = self.y - other_position.y
        dz = self.z - other_position.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def move_towards(self, target_position, speed: float, delta_time: float):
        """Движение к целевой позиции"""
        dx = target_position.x - self.x
        dy = target_position.y - self.y
        dz = target_position.z - self.z
        
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        if distance > 0:
            move_distance = speed * delta_time
            if move_distance >= distance:
                self.x = target_position.x
                self.y = target_position.y
                self.z = target_position.z
            else:
                ratio = move_distance / distance
                self.x += dx * ratio
                self.y += dy * ratio
                self.z += dz * ratio


class AdvancedGameEntity:
    """Универсальная игровая сущность"""
    
    def __init__(
        self,
        entity_id: str,
        entity_type: str,
        effect_db: Optional[EffectDatabase] = None,
        name: Optional[str] = None,
        position: Optional[Tuple[float, float, float]] = None,
    ):
        self.id = entity_id
        self.type = entity_type
        self.guid = str(uuid.uuid4())
        self.name = name or entity_id
        
        # Базовые характеристики
        self.stats = self._generate_base_stats()
        self.position = EntityPosition()
        self.rotation = 0.0
        self.scale = 1.0
        
        # Сопротивления и слабости
        self.resistances = self._generate_resistances()
        self.weaknesses = self._generate_weaknesses()
        
        # Интегрированные системы
        if effect_db is None:
            # Локальная БД эффектов, если не передали внешнюю
            effect_db = EffectDatabase()
        self.effect_system = EffectSystem(effect_db)
        self.emotion_system = AdvancedEmotionSystem(effect_db)
        self.genetic_system = AdvancedGeneticSystem(effect_db)
        self.ai_system = AdaptiveAISystem(entity_id, effect_db)
        
        # Дополнительные системы
        self.memory_system = EntityMemorySystem()
        self.inventory_system = EntityInventorySystem()
        self.quest_system = EntityQuestSystem()
        
        # Состояние
        self.is_active = True
        self.is_visible = True
        self.is_interactable = True
        
        # Pygame поддержка
        self.pygame_sprite = None
        self.animation_frame = 0
        self.animation_speed = 0.15
        self.direction = pygame.math.Vector2() if PYGAME_AVAILABLE and pygame.get_init() else None
        
        # История и статистика
        self.creation_time = 0.0  # Здесь будет время игры
        self.last_update_time = 0.0
        self.update_count = 0
        
        # Установка позиции, если передана
        if position is not None:
            try:
                self.position.x, self.position.y, self.position.z = position
            except Exception:
                pass

        # Инициализация
        self._initialize_entity()
        
        logger.info(f"Создана сущность {entity_id} типа {entity_type}")
    
    def _generate_base_stats(self) -> EntityStats:
        """Генерация базовых характеристик"""
        stats = EntityStats()
        
        # Модификация характеристик на основе типа
        if self.type == EntityType.PLAYER.value:
            stats.health = 120.0
            stats.max_health = 120.0
            stats.stamina = 150.0
            stats.max_stamina = 150.0
            stats.mana = 120.0
            stats.max_mana = 120.0
            stats.damage = 25.0
            stats.defense = 20.0
            stats.speed = 1.2
            stats.accuracy = 0.85
            stats.critical_chance = 0.08
            stats.critical_multiplier = 2.5
            
        elif self.type == EntityType.ENEMY.value:
            stats.health = random.uniform(80, 150)
            stats.max_health = stats.health
            stats.stamina = random.uniform(60, 120)
            stats.max_stamina = stats.stamina
            stats.damage = random.uniform(15, 35)
            stats.defense = random.uniform(10, 25)
            stats.speed = random.uniform(0.8, 1.4)
            stats.accuracy = random.uniform(0.7, 0.9)
            stats.critical_chance = random.uniform(0.03, 0.07)
            stats.critical_multiplier = random.uniform(1.8, 2.2)
            
        elif self.type == EntityType.BOSS.value:
            stats.health = random.uniform(300, 500)
            stats.max_health = stats.health
            stats.stamina = random.uniform(200, 300)
            stats.max_stamina = stats.stamina
            stats.damage = random.uniform(50, 80)
            stats.defense = random.uniform(30, 50)
            stats.speed = random.uniform(0.6, 1.0)
            stats.accuracy = random.uniform(0.8, 0.95)
            stats.critical_chance = random.uniform(0.1, 0.15)
            stats.critical_multiplier = random.uniform(2.5, 3.5)
        
        return stats
    
    def _generate_resistances(self) -> Dict[str, float]:
        """Генерация сопротивлений"""
        resistances = {}
        
        # Базовые сопротивления для всех типов
        base_resistances = {
            DamageType.PHYSICAL.value: random.uniform(0.0, 0.2),
            DamageType.FIRE.value: random.uniform(0.0, 0.3),
            DamageType.ICE.value: random.uniform(0.0, 0.3),
            DamageType.LIGHTNING.value: random.uniform(0.0, 0.25),
            DamageType.POISON.value: random.uniform(0.0, 0.4),
            DamageType.MAGIC.value: random.uniform(0.0, 0.2)
        }
        
        # Специальные сопротивления на основе типа
        if self.type == EntityType.BOSS.value:
            # Боссы имеют повышенные сопротивления
            for damage_type, resistance in base_resistances.items():
                resistances[damage_type] = min(0.8, resistance * 2.0)
        else:
            resistances = base_resistances
        
        return resistances
    
    def _generate_weaknesses(self) -> Dict[str, float]:
        """Генерация слабостей"""
        weaknesses = {}
        
        # Случайные слабости (20% шанс для каждого типа урона)
        damage_types = [dt.value for dt in DamageType]
        
        for damage_type in damage_types:
            if random.random() < 0.2:
                weakness_value = random.uniform(0.1, 0.4)
                weaknesses[damage_type] = weakness_value
        
        return weaknesses
    
    def _initialize_entity(self):
        """Инициализация сущности"""
        try:
            # Применение стартовых эффектов на основе типа
            self._apply_starting_effects()
            
            # Инициализация систем
            self.memory_system.initialize(self.id, self.type)
            self.inventory_system.initialize(self.id)
            self.quest_system.initialize(self.id)
            
            # Установка базовых эмоций
            self._set_base_emotions()
            
            logger.info(f"Сущность {self.id} инициализирована")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сущности {self.id}: {e}")
    
    def _apply_starting_effects(self):
        """Применение стартовых эффектов"""
        try:
            if self.type == EntityType.PLAYER.value:
                # Игрок получает базовые положительные эффекты
                self.effect_system.apply_effect("PLAYER_BASE_BOOST", "entity_creation")
                
            elif self.type == EntityType.BOSS.value:
                # Боссы получают усиливающие эффекты
                self.effect_system.apply_effect("BOSS_POWER_BOOST", "entity_creation")
                self.effect_system.apply_effect("BOSS_DEFENSE_BOOST", "entity_creation")
                
        except Exception as e:
            logger.error(f"Ошибка применения стартовых эффектов: {e}")
    
    def _set_base_emotions(self):
        """Установка базовых эмоций"""
        try:
            if self.type == EntityType.PLAYER.value:
                # Игрок начинает с нейтрального эмоционального состояния
                self.emotion_system.current_state.emotional_stability = 0.8
                
            elif self.type == EntityType.ENEMY.value:
                # Враги начинают с агрессивных эмоций
                self.emotion_system.trigger_emotion("EMO_102", 0.6, "entity_creation")  # Гнев
                
            elif self.type == EntityType.BOSS.value:
                # Боссы начинают с доминирующих эмоций
                self.emotion_system.trigger_emotion("EMO_106", 0.8, "entity_creation")  # Возбуждение
                
        except Exception as e:
            logger.error(f"Ошибка установки базовых эмоций: {e}")
    
    def update(self, delta_time: float):
        """Обновление сущности"""
        try:
            # Обновление времени
            self.last_update_time += delta_time
            self.update_count += 1
            
            # Обновление систем
            self.effect_system.update(delta_time)
            self.emotion_system.update(delta_time)
            self.genetic_system.update(delta_time)
            self.ai_system.update(self, None, delta_time)  # world=None для упрощения
            
            # Обновление памяти
            self.memory_system.update(delta_time)
            
            # Обновление анимации Pygame
            if PYGAME_AVAILABLE and pygame.get_init():
                self.update_animation(delta_time)
            
            # Восстановление выносливости
            if self.stats.stamina < self.stats.max_stamina:
                self.stats.stamina = min(self.stats.max_stamina, 
                                       self.stats.stamina + 5.0 * delta_time)
            
        except Exception as e:
            logger.error(f"Ошибка обновления сущности {self.id}: {e}")
    
    def move_pygame(self, dx: float, dy: float):
        """Движение с поддержкой Pygame"""
        # Обновление позиции (работает независимо от pygame)
        self.position.x += dx * self.stats.speed
        self.position.y += dy * self.stats.speed
        
        # Обновление направления (только если pygame доступен)
        if PYGAME_AVAILABLE and pygame.get_init():
            if dx != 0 or dy != 0:
                if self.direction is None:
                    self.direction = pygame.math.Vector2()
                self.direction.x = dx
                self.direction.y = dy
    
    def update_animation(self, delta_time: float):
        """Обновление анимации"""
        if not PYGAME_AVAILABLE or not pygame.get_init():
            return
        
        self.animation_frame += self.animation_speed * delta_time
        if self.animation_frame >= 4:  # 4 кадра анимации
            self.animation_frame = 0
    
    def _check_entity_state(self):
        """Проверка состояния сущности"""
        try:
            # Проверка здоровья
            if self.stats.health <= 0:
                self._handle_death()
            
            # Проверка выносливости
            if self.stats.stamina <= 0:
                self._handle_exhaustion()
            
            # Проверка эмоционального состояния
            emotional_balance = self.emotion_system.current_state.get_emotional_balance()
            if emotional_balance < 0.2:
                self._handle_emotional_crisis()
                
        except Exception as e:
            logger.error(f"Ошибка проверки состояния сущности: {e}")
    
    def _handle_death(self):
        """Обработка смерти сущности"""
        try:
            self.is_active = False
            self.is_visible = False
            self.is_interactable = False
            
            # Запись в память
            self.memory_system.add_memory("death", "entity_died", 1.0)
            
            # Уведомление систем
            if hasattr(self, 'on_death'):
                self.on_death()
            
            logger.info(f"Сущность {self.id} погибла")
            
        except Exception as e:
            logger.error(f"Ошибка обработки смерти: {e}")
    
    def _handle_exhaustion(self):
        """Обработка истощения"""
        try:
            # Снижение характеристик
            self.stats.speed *= 0.5
            self.stats.accuracy *= 0.7
            
            # Запись в память
            self.memory_system.add_memory("exhaustion", "entity_exhausted", 0.8)
            
            # Восстановление выносливости
            self.stats.stamina = min(self.stats.max_stamina, 
                                   self.stats.stamina + 10.0)
            
        except Exception as e:
            logger.error(f"Ошибка обработки истощения: {e}")
    
    def _handle_emotional_crisis(self):
        """Обработка эмоционального кризиса"""
        try:
            # Снижение производительности
            self.stats.accuracy *= 0.8
            self.stats.defense *= 0.9
            
            # Запись в память
            self.memory_system.add_memory("emotional_crisis", "entity_crisis", 0.9)
            
            # Попытка восстановления эмоционального баланса
            if random.random() < 0.3:  # 30% шанс
                self.emotion_system.trigger_emotion("EMO_105", 0.5, "self_recovery")  # Спокойствие
                
        except Exception as e:
            logger.error(f"Ошибка обработки эмоционального кризиса: {e}")
    
    def take_damage(self, damage: float, damage_type: str = "physical", 
                   source: str = "unknown") -> Dict[str, Any]:
        """Получение урона"""
        try:
            # Расчёт модифицированного урона
            modified_damage = self._calculate_damage(damage, damage_type)
            
            # Применение урона
            old_health = self.stats.health
            self.stats.health = max(0, self.stats.health - modified_damage)
            actual_damage = old_health - self.stats.health
            
            # Запись в память
            self.memory_system.add_memory("damage_taken", f"damage_from_{source}", actual_damage)
            
            # Триггер эмоций
            if actual_damage > damage * 0.5:  # Значительный урон
                self.emotion_system.trigger_emotion("EMO_101", 0.7, "damage")  # Страх
            elif actual_damage < damage * 0.3:  # Незначительный урон
                self.emotion_system.trigger_emotion("EMO_102", 0.5, "damage")  # Гнев
            
            # Проверка критического урона
            is_critical = actual_damage > damage * 1.5
            
            result = {
                "damage_dealt": actual_damage,
                "damage_type": damage_type,
                "is_critical": is_critical,
                "source": source,
                "resistance_applied": damage - actual_damage
            }
            
            logger.info(f"Сущность {self.id} получила {actual_damage} урона от {source}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения урона: {e}")
            return {"damage_dealt": 0, "error": str(e)}
    
    def _calculate_damage(self, base_damage: float, damage_type: str) -> float:
        """Расчёт модифицированного урона"""
        try:
            modified_damage = base_damage
            
            # Применение сопротивлений
            if damage_type in self.resistances:
                resistance = self.resistances[damage_type]
                modified_damage *= (1.0 - resistance)
            
            # Применение слабостей
            if damage_type in self.weaknesses:
                weakness = self.weaknesses[damage_type]
                modified_damage *= (1.0 + weakness)
            
            # Случайная вариация (±10%)
            variation = random.uniform(0.9, 1.1)
            modified_damage *= variation
            
            return max(1.0, modified_damage)
            
        except Exception as e:
            logger.error(f"Ошибка расчёта урона: {e}")
            return base_damage
    
    def heal(self, amount: float, source: str = "unknown") -> bool:
        """Лечение сущности"""
        try:
            if not self.stats.is_alive():
                return False
            
            old_health = self.stats.health
            self.stats.health = min(self.stats.max_health, 
                                   self.stats.health + amount)
            actual_healing = self.stats.health - old_health
            
            if actual_healing > 0:
                # Запись в память
                self.memory_system.add_memory("healing", f"healed_by_{source}", actual_healing)
                
                # Триггер положительных эмоций
                self.emotion_system.trigger_emotion("EMO_108", 0.6, "healing")  # Радость
                
                logger.info(f"Сущность {self.id} восстановила {actual_healing} здоровья от {source}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка лечения: {e}")
            return False
    
    def restore_stamina(self, amount: float, source: str = "unknown") -> bool:
        """Восстановление выносливости"""
        try:
            old_stamina = self.stats.stamina
            self.stats.stamina = min(self.stats.max_stamina, 
                                   self.stats.stamina + amount)
            actual_restoration = self.stats.stamina - old_stamina
            
            if actual_restoration > 0:
                # Запись в память
                self.memory_system.add_memory("stamina_restoration", f"restored_by_{source}", actual_restoration)
                
                logger.info(f"Сущность {self.id} восстановила {actual_restoration} выносливости от {source}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка восстановления выносливости: {e}")
            return False
    
    def move_to(self, target_position: EntityPosition, speed: float = None):
        """Движение к целевой позиции"""
        try:
            if not self.stats.can_act():
                return False
            
            # Использование текущей скорости, если не указана другая
            if speed is None:
                speed = self.stats.speed
            
            # Расчёт времени движения
            distance = self.position.distance_to(target_position)
            movement_time = distance / speed
            
            # Запись в память
            self.memory_system.add_memory("movement", f"moving_to_{target_position.x}_{target_position.y}", distance)
            
            # Обновление позиции
            self.position.move_towards(target_position, speed, 1.0)  # delta_time = 1.0 для простоты
            
            logger.info(f"Сущность {self.id} движется к позиции ({target_position.x}, {target_position.y})")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка движения: {e}")
            return False
    
    def interact_with(self, target_entity) -> Dict[str, Any]:
        """Взаимодействие с другой сущностью"""
        try:
            if not self.is_interactable or not target_entity.is_interactable:
                return {"success": False, "reason": "entity_not_interactable"}
            
            # Определение типа взаимодействия
            interaction_type = self._determine_interaction_type(target_entity)
            
            # Выполнение взаимодействия
            result = self._execute_interaction(interaction_type, target_entity)
            
            # Запись в память
            self.memory_system.add_memory("interaction", f"interacted_with_{target_entity.id}", 1.0)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка взаимодействия: {e}")
            return {"success": False, "error": str(e)}
    
    def _determine_interaction_type(self, target_entity) -> str:
        """Определение типа взаимодействия"""
        try:
            if self.type == EntityType.PLAYER.value and target_entity.type == EntityType.NPC.value:
                return "dialogue"
            elif self.type == EntityType.PLAYER.value and target_entity.type == EntityType.ENEMY.value:
                return "combat"
            elif self.type == EntityType.PLAYER.value and target_entity.type == EntityType.CREATURE.value:
                return "tame"
            else:
                return "basic"
                
        except Exception as e:
            logger.error(f"Ошибка определения типа взаимодействия: {e}")
            return "basic"
    
    def _execute_interaction(self, interaction_type: str, target_entity) -> Dict[str, Any]:
        """Выполнение взаимодействия"""
        try:
            if interaction_type == "dialogue":
                return self._execute_dialogue(target_entity)
            elif interaction_type == "combat":
                return self._execute_combat(target_entity)
            elif interaction_type == "tame":
                return self._execute_tame(target_entity)
            else:
                return self._execute_basic_interaction(target_entity)
                
        except Exception as e:
            logger.error(f"Ошибка выполнения взаимодействия: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_dialogue(self, target_entity) -> Dict[str, Any]:
        """Выполнение диалога"""
        try:
            # Получение эмоций игрока
            player_emotions = self.emotion_system.get_current_emotions()
            
            # Получение базовой эмоции NPC
            npc_emotion = target_entity.emotion_system.current_state.get_dominant_emotion()
            
            # Обработка диалога через эмоциональную систему
            dialogue_result, bonus = self.emotion_system.handle_dialogue(npc_emotion, player_emotions)
            
            result = {
                "success": True,
                "interaction_type": "dialogue",
                "result": dialogue_result,
                "bonus": bonus
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка выполнения диалога: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_combat(self, target_entity) -> Dict[str, Any]:
        """Выполнение боя"""
        try:
            # Проверка возможности атаки
            if not self.stats.can_act():
                return {"success": False, "reason": "cannot_act"}
            
            # Расчёт урона
            damage = self.stats.damage
            if random.random() < self.stats.critical_chance:
                damage *= self.stats.critical_multiplier
                is_critical = True
            else:
                is_critical = False
            
            # Нанесение урона
            damage_result = target_entity.take_damage(damage, "physical", self.id)
            
            # Расход выносливости
            stamina_cost = 10.0
            self.stats.stamina = max(0, self.stats.stamina - stamina_cost)
            
            # Триггер эмоций
            if is_critical:
                self.emotion_system.trigger_emotion("EMO_106", 0.8, "critical_hit")  # Возбуждение
            
            result = {
                "success": True,
                "interaction_type": "combat",
                "damage_dealt": damage_result["damage_dealt"],
                "is_critical": is_critical,
                "stamina_cost": stamina_cost
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка выполнения боя: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_tame(self, target_entity) -> Dict[str, Any]:
        """Выполнение приручения"""
        try:
            # Проверка возможности приручения
            if target_entity.type not in [EntityType.CREATURE.value]:
                return {"success": False, "reason": "cannot_tame"}
            
            # Расчёт шанса приручения
            base_chance = 0.3
            emotional_bonus = self.emotion_system.current_state.get_emotional_balance() * 0.2
            final_chance = min(0.9, base_chance + emotional_bonus)
            
            # Проверка успеха
            if random.random() < final_chance:
                result = {
                    "success": True,
                    "interaction_type": "tame",
                    "creature_tamed": target_entity.id,
                    "chance": final_chance
                }
                
                # Триггер положительных эмоций
                self.emotion_system.trigger_emotion("EMO_108", 0.8, "successful_tame")  # Радость
                
                return result
            else:
                return {
                    "success": False,
                    "interaction_type": "tame",
                    "reason": "tame_failed",
                    "chance": final_chance
                }
                
        except Exception as e:
            logger.error(f"Ошибка выполнения приручения: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_basic_interaction(self, target_entity) -> Dict[str, Any]:
        """Выполнение базового взаимодействия"""
        try:
            result = {
                "success": True,
                "interaction_type": "basic",
                "message": f"Взаимодействие между {self.id} и {target_entity.id}"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка выполнения базового взаимодействия: {e}")
            return {"success": False, "error": str(e)}
    
    def get_entity_info(self) -> Dict[str, Any]:
        """Получение информации о сущности"""
        try:
            info = {
                "id": self.id,
                "type": self.type,
                "guid": self.guid,
                "stats": {
                    "health": self.stats.health,
                    "max_health": self.stats.max_health,
                    "stamina": self.stats.stamina,
                    "max_stamina": self.stats.max_stamina,
                    "damage": self.stats.damage,
                    "defense": self.stats.defense,
                    "speed": self.stats.speed,
                    "accuracy": self.stats.accuracy,
                    "critical_chance": self.stats.critical_chance,
                    "critical_multiplier": self.stats.critical_multiplier
                },
                "position": {
                    "x": self.position.x,
                    "y": self.position.y,
                    "z": self.position.z
                },
                "resistances": self.resistances,
                "weaknesses": self.weaknesses,
                "active_effects": len(self.effect_system.get_active_effects()),
                "current_emotions": self.emotion_system.get_current_emotions(),
                "unlocked_genes": len(self.genetic_system.unlocked_genes),
                "ai_level": getattr(self.ai_system, 'level', 1),
                "is_active": self.is_active,
                "is_visible": self.is_visible,
                "is_interactable": self.is_interactable
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о сущности: {e}")
            return {"error": str(e)}
    
    def save_entity_state(self, filepath: str) -> bool:
        """Сохранение состояния сущности"""
        try:
            import json
            
            entity_state = {
                "id": self.id,
                "type": self.type,
                "guid": self.guid,
                "stats": {
                    "health": self.stats.health,
                    "max_health": self.stats.max_health,
                    "stamina": self.stats.stamina,
                    "max_stamina": self.stats.max_stamina,
                    "damage": self.stats.damage,
                    "defense": self.stats.defense,
                    "speed": self.stats.speed,
                    "accuracy": self.stats.accuracy,
                    "critical_chance": self.stats.critical_chance,
                    "critical_multiplier": self.stats.critical_multiplier
                },
                "position": {
                    "x": self.position.x,
                    "y": self.position.y,
                    "z": self.position.z
                },
                "resistances": self.resistances,
                "weaknesses": self.weaknesses,
                "is_active": self.is_active,
                "is_visible": self.is_visible,
                "is_interactable": self.is_interactable
            }
            
            with open(filepath, 'w') as f:
                json.dump(entity_state, f, indent=2)
            
            logger.info(f"Состояние сущности {self.id} сохранено в {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения состояния сущности: {e}")
            return False
    
    def load_entity_state(self, filepath: str) -> bool:
        """Загрузка состояния сущности"""
        try:
            import json
            
            with open(filepath, 'r') as f:
                entity_state = json.load(f)
            
            # Восстановление характеристик
            stats_data = entity_state["stats"]
            self.stats.health = stats_data["health"]
            self.stats.max_health = stats_data["max_health"]
            self.stats.stamina = stats_data["stamina"]
            self.stats.max_stamina = stats_data["max_stamina"]
            self.stats.damage = stats_data["damage"]
            self.stats.defense = stats_data["defense"]
            self.stats.speed = stats_data["speed"]
            self.stats.accuracy = stats_data["accuracy"]
            self.stats.critical_chance = stats_data["critical_chance"]
            self.stats.critical_multiplier = stats_data["critical_multiplier"]
            
            # Восстановление позиции
            pos_data = entity_state["position"]
            self.position.x = pos_data["x"]
            self.position.y = pos_data["y"]
            self.position.z = pos_data["z"]
            
            # Восстановление других параметров
            self.resistances = entity_state["resistances"]
            self.weaknesses = entity_state["weaknesses"]
            self.is_active = entity_state["is_active"]
            self.is_visible = entity_state["is_visible"]
            self.is_interactable = entity_state["is_interactable"]
            
            logger.info(f"Состояние сущности {self.id} загружено из {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки состояния сущности: {e}")
            return False


class EntityMemorySystem:
    """Система памяти сущности"""
    
    def __init__(self):
        self.memories: List[Dict[str, Any]] = []
        self.memory_capacity = 100
        self.memory_decay_rate = 0.95
    
    def initialize(self, entity_id: str, entity_type: str):
        """Инициализация системы памяти"""
        self.entity_id = entity_id
        self.entity_type = entity_type
    
    def add_memory(self, memory_type: str, content: str, importance: float):
        """Добавление памяти"""
        memory = {
            "type": memory_type,
            "content": content,
            "importance": importance,
            "timestamp": 0.0,  # Здесь будет время игры
            "decay": 1.0
        }
        
        self.memories.append(memory)
        
        # Ограничение ёмкости памяти
        if len(self.memories) > self.memory_capacity:
            # Удаление наименее важных воспоминаний
            self.memories.sort(key=lambda x: x["importance"] * x["decay"])
            self.memories.pop(0)
    
    def update(self, delta_time: float):
        """Обновление системы памяти"""
        # Затухание воспоминаний
        for memory in self.memories:
            memory["decay"] *= (self.memory_decay_rate ** delta_time)
        
        # Удаление полностью затухших воспоминаний
        self.memories = [m for m in self.memories if m["decay"] > 0.1]
    
    def get_memories_by_type(self, memory_type: str) -> List[Dict[str, Any]]:
        """Получение воспоминаний по типу"""
        return [m for m in self.memories if m["type"] == memory_type]
    
    def get_important_memories(self, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Получение важных воспоминаний"""
        return [m for m in self.memories if m["importance"] * m["decay"] > threshold]


class EntityInventorySystem:
    """Система инвентаря сущности"""
    
    def __init__(self):
        self.items: List[Dict[str, Any]] = []
        self.inventory_capacity = 20
        self.gold = 0
    
    def initialize(self, entity_id: str):
        """Инициализация системы инвентаря"""
        self.entity_id = entity_id
    
    def add_item(self, item: Dict[str, Any]) -> bool:
        """Добавление предмета в инвентарь"""
        if len(self.items) < self.inventory_capacity:
            self.items.append(item)
            return True
        return False
    
    def remove_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Удаление предмета из инвентаря"""
        for i, item in enumerate(self.items):
            if item.get("id") == item_id:
                return self.items.pop(i)
        return None
    
    def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Получение предмета по ID"""
        for item in self.items:
            if item.get("id") == item_id:
                return item
        return None
    
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """Добавление предмета в инвентарь по ID"""
        if len(self.items) < self.inventory_capacity:
            # Проверяем, есть ли уже такой предмет
            for item in self.items:
                if item.get("id") == item_id:
                    item["quantity"] = item.get("quantity", 1) + quantity
                    return True
            
            # Добавляем новый предмет
            self.items.append({
                "id": item_id,
                "quantity": quantity
            })
            return True
        return False
    
    def clear_inventory(self):
        """Очистка инвентаря"""
        self.items.clear()
    
    def get_inventory_data(self) -> Dict[str, int]:
        """Получение данных инвентаря для сохранения"""
        inventory_data = {}
        for item in self.items:
            item_id = item.get("id")
            quantity = item.get("quantity", 1)
            if item_id:
                inventory_data[item_id] = quantity
        return inventory_data


class EntityQuestSystem:
    """Система квестов сущности"""
    
    def __init__(self):
        self.active_quests: List[Dict[str, Any]] = []
        self.completed_quests: List[Dict[str, Any]] = []
        self.quest_log_capacity = 10
    
    def initialize(self, entity_id: str):
        """Инициализация системы квестов"""
        self.entity_id = entity_id
    
    def add_quest(self, quest: Dict[str, Any]) -> bool:
        """Добавление квеста"""
        if len(self.active_quests) < self.quest_log_capacity:
            self.active_quests.append(quest)
            return True
        return False
    
    def complete_quest(self, quest_id: str) -> bool:
        """Завершение квеста"""
        for i, quest in enumerate(self.active_quests):
            if quest.get("id") == quest_id:
                completed_quest = self.active_quests.pop(i)
                self.completed_quests.append(completed_quest)
                return True
        return False


# Pygame интеграция для AdvancedGameEntity
def add_pygame_support_to_entity(entity):
    """Добавляет поддержку Pygame к существующей сущности"""
    
    def setup_pygame_sprite(self, sprite_path: str = None):
        """Настройка Pygame спрайта"""
        if not PYGAME_AVAILABLE or not pygame.get_init():
            return
        
        if sprite_path:
            try:
                self.pygame_sprite = pygame.image.load(sprite_path).convert_alpha()
            except Exception as e:
                logger.warning(f"Не удалось загрузить спрайт {sprite_path}: {e}")
                self.pygame_sprite = None
        
        if not self.pygame_sprite:
            # Создание простого спрайта
            sprite_size = 32
            self.pygame_sprite = pygame.Surface((sprite_size, sprite_size))
            color = (0, 255, 0) if self.type == "player" else (255, 0, 0)
            self.pygame_sprite.fill(color)
    
    def update_animation(self, delta_time: float):
        """Обновление анимации"""
        if not PYGAME_AVAILABLE or not pygame.get_init():
            return
        
        self.animation_frame += self.animation_speed * delta_time
        if self.animation_frame >= 4:  # 4 кадра анимации
            self.animation_frame = 0
    
    def move_pygame(self, dx: float, dy: float):
        """Движение с поддержкой Pygame"""
        # Обновление позиции (работает независимо от pygame)
        self.position.x += dx * self.stats.speed
        self.position.y += dy * self.stats.speed
        
        # Обновление направления (только если pygame доступен)
        if PYGAME_AVAILABLE and pygame.get_init():
            if dx != 0 or dy != 0:
                if self.direction is None:
                    self.direction = pygame.math.Vector2()
                self.direction.x = dx
                self.direction.y = dy
    
    def get_pygame_rect(self) -> pygame.Rect:
        """Получение Pygame прямоугольника для отрисовки"""
        if not PYGAME_AVAILABLE or not pygame.get_init() or not self.pygame_sprite:
            return pygame.Rect(0, 0, 32, 32) if PYGAME_AVAILABLE else None
        
        sprite_rect = self.pygame_sprite.get_rect()
        sprite_rect.center = (int(self.position.x), int(self.position.y))
        return sprite_rect
    
    def render_pygame(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """Отрисовка сущности на Pygame экране"""
        if not PYGAME_AVAILABLE or not pygame.get_init() or not self.pygame_sprite:
            return
        
        # Позиция с учетом камеры
        render_x = int(self.position.x - camera_offset[0])
        render_y = int(self.position.y - camera_offset[1])
        
        # Отрисовка спрайта
        screen.blit(self.pygame_sprite, (render_x, render_y))
        
        # Отрисовка имени
        if hasattr(self, 'name') and self.name:
            font = pygame.font.Font(None, 24)
            name_surf = font.render(self.name, True, (255, 255, 255))
            name_rect = name_surf.get_rect(center=(render_x, render_y - 20))
            screen.blit(name_surf, name_rect)
    
    # Добавление методов к сущности
    entity.setup_pygame_sprite = setup_pygame_sprite.__get__(entity)
    entity.update_animation = update_animation.__get__(entity)
    entity.move_pygame = move_pygame.__get__(entity)
    entity.get_pygame_rect = get_pygame_rect.__get__(entity)
    entity.render_pygame = render_pygame.__get__(entity)
    
    return entity


# Расширение AdvancedGameEntity для Pygame
class PygameGameEntity(AdvancedGameEntity):
    """Версия AdvancedGameEntity с полной поддержкой Pygame"""
    
    def __init__(self, entity_id: str, entity_type: str, effect_db: EffectDatabase, sprite_path: str = None):
        super().__init__(entity_id, entity_type, effect_db)
        
        # Инициализация Pygame компонентов
        if PYGAME_AVAILABLE and pygame.get_init():
            self.setup_pygame_sprite(sprite_path)
            self.animation_frame = 0
            self.animation_speed = 0.15
            self.direction = pygame.math.Vector2()
    
    def update(self, delta_time: float):
        """Обновление с поддержкой Pygame"""
        super().update(delta_time)
        
        # Обновление анимации
        if PYGAME_AVAILABLE and pygame.get_init():
            self.update_animation(delta_time)
    
    def move(self, direction: Tuple[float, float], speed: float, delta_time: float):
        """Движение с поддержкой Pygame"""
        if PYGAME_AVAILABLE and pygame.get_init():
            self.move_pygame(direction, speed, delta_time)
        else:
            # Fallback для консольного режима
            self.position.x += direction[0] * speed * delta_time
            self.position.y += direction[1] * speed * delta_time
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """Отрисовка на Pygame экране"""
        if PYGAME_AVAILABLE and pygame.get_init():
            self.render_pygame(screen, camera_offset)
    
    def load_animation_frames(self, folder_path: str) -> List[pygame.Surface]:
        """Загружает кадры анимации из папки"""
        if not PYGAME_AVAILABLE or not pygame.get_init():
            return []
        
        try:
            import os
            frames = []
            if os.path.exists(folder_path):
                for file in sorted(os.listdir(folder_path)):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        frame_path = os.path.join(folder_path, file)
                        frame = pygame.image.load(frame_path).convert_alpha()
                        frames.append(frame)
            
            if not frames:
                logger.warning(f"Не найдены кадры анимации в {folder_path}")
                return self._create_fallback_frames()
            
            return frames
            
        except Exception as e:
            logger.error(f"Ошибка загрузки кадров анимации из {folder_path}: {e}")
            return self._create_fallback_frames()
    
    def _create_fallback_frames(self) -> List[pygame.Surface]:
        """Создает резервные кадры анимации"""
        if not PYGAME_AVAILABLE or not pygame.get_init():
            return []
        
        fallback_surf = pygame.Surface((64, 64))
        fallback_surf.fill((255, 0, 255))  # Маджента для отладки
        return [fallback_surf]
    
    def update_animation(self, animation_frames: List[pygame.Surface]) -> None:
        """Обновляет анимацию сущности"""
        if not PYGAME_AVAILABLE or not pygame.get_init() or not animation_frames:
            return
        
        try:
            # Обновляем индекс кадра
            self.animation_frame += self.animation_speed
            if self.animation_frame >= len(animation_frames):
                self.animation_frame = 0

            # Устанавливаем текущее изображение
            frame_index = int(self.animation_frame)
            if 0 <= frame_index < len(animation_frames):
                self.pygame_sprite = animation_frames[frame_index]
            else:
                logger.warning(f"Неверный индекс кадра: {frame_index}")
                
        except Exception as e:
            logger.error(f"Ошибка обновления анимации: {e}")
    
    def get_direction_vector(self) -> pygame.math.Vector2:
        """Возвращает текущий вектор направления"""
        if not PYGAME_AVAILABLE or not pygame.get_init():
            return None
        return self.direction.copy() if self.direction else pygame.math.Vector2()
    
    def set_direction(self, direction: Tuple[float, float]) -> None:
        """Устанавливает направление движения"""
        if not PYGAME_AVAILABLE or not pygame.get_init():
            return
        
        if not self.direction:
            self.direction = pygame.math.Vector2()
        
        self.direction.x = direction[0]
        self.direction.y = direction[1]
    
    def is_moving(self) -> bool:
        """Проверяет, движется ли сущность"""
        if not PYGAME_AVAILABLE or not pygame.get_init() or not self.direction:
            return False
        return self.direction.magnitude() > 0
    
    def wave_value(self) -> int:
        """Возвращает значение для эффекта мерцания"""
        if not PYGAME_AVAILABLE or not pygame.get_init():
            return 255
        
        try:
            import math
            value = math.sin(pygame.time.get_ticks() * 0.01)
            return 255 if value >= 0 else 0
        except Exception as e:
            logger.error(f"Ошибка расчета мерцания: {e}")
            return 255
