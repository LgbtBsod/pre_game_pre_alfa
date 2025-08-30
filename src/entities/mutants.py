from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from src.core.architecture import BaseComponent, ComponentType, Priority
from src.entities.base_entity import BaseEntity, BaseEntityType
from typing import *
from typing import Dict, List, Optional, Any, Tuple, Callable
import logging
import math
import os
import random
import sys
import time

#!/usr/bin/env python3
"""Система мутантов AI - EVOLVE
Процедурно генерируемые противники с эволюционными способностями"""

# = ОСНОВНЫЕ ТИПЫ И ПЕРЕЧИСЛЕНИЯ
class MutationType(Enum):
    """Типы мутаций мутантов"""
    PHYSICAL = "physical"      # Физические мутации
    MENTAL = "mental"          # Ментальные мутации
    COMBAT = "combat"          # Боевые мутации
    MAGIC = "magic"            # Магические мутации
    ADAPTIVE = "adaptive"      # Адаптивные мутации
    COMBINATIONAL = "combinational" # Комбинационные мутации

class MutationLevel(Enum):
    """Уровни мутаций"""
    MINOR = "minor"            # Незначительные
    MODERATE = "moderate"      # Умеренные
    MAJOR = "major"            # Значительные
    EXTREME = "extreme"        # Экстремальные
    LEGENDARY = "legendary"    # Легендарные

class MutantPhase(Enum):
    """Фазы мутанта"""
    PHASE_1 = "phase_1"       # Базовая фаза
    PHASE_2 = "phase_2"       # Эволюционированная фаза
    PHASE_3 = "phase_3"       # Финальная фаза

# = ДАТАКЛАССЫ ДЛЯ МУТАЦИЙ И СПОСОБНОСТЕЙ
@dataclass
class Mutation:
    """Мутация мутанта"""
    mutation_id: str
    name: str
    description: str
    mutation_type: MutationType
    level: MutationLevel
    effects: Dict[str, float]
    visual_effects: List[str]
    sound_effects: List[str]
    duration: Optional[float] = None
    timestamp: float = field(default_factory=time.time)
    source: Optional[str] = None
    reversible: bool = True
    cascade_chance: float = 0.1

@dataclass
class VisualMutation:
    """Визуальная мутация"""
    mutation_id: str
    name: str
    description: str
    visual_type: str
    parameters: Dict[str, Any]
    intensity: float = 1.0
    duration: Optional[float] = None

@dataclass
class MutantAbility:
    """Способность мутанта"""
    ability_id: str
    name: str
    description: str
    ability_type: str
    cooldown: float
    range: float
    damage: float
    effects: Dict[str, float]
    visual_effects: List[str]
    sound_effects: List[str]
    requirements: Dict[str, Any]
    last_used: float = 0.0
    charges: Optional[int] = None

# = ОСНОВНАЯ СИСТЕМА МУТАНТОВ
class Mutant(BaseEntity):
    """Класс мутанта - процедурно генерируемый противник"""
    
    def __init__(self, mutant_id: str, name: str, mutation_level: int,
                 position: Tuple[float, float, float]):
        # Инициализируем базовую сущность
        super().__init__(mutant_id, BaseEntityType.MUTANT, name)
        
        # Специфичные для мутанта параметры
        self.mutation_level = mutation_level
        self.position = position
        self.setPos(*position)
        
        # Система мутаций
        self.mutations: Dict[str, Mutation] = {}
        self.visual_mutations: Dict[str, VisualMutation] = {}
        self.mutation_history: List[Dict[str, Any]] = []
        
        # Способности
        self.abilities: Dict[str, MutantAbility] = {}
        self.derived_abilities: List[str] = []
        
        # Фазы мутанта
        self.current_phase = 1
        self.max_phases = 2
        self.phase_health_thresholds = [0.5]  # Переход в фазу 2 при 50% здоровья
        
        # Адаптивность
        self.adaptation_rate = 0.1
        self.learning_progress = 0.0
        self.evolution_stage = 1
        
        # Визуальные параметры
        self.base_scale = 1.0
        self.base_color = (1, 1, 1, 1)
        self.current_scale = 1.0
        self.current_color = (1, 1, 1, 1)
        
        # Инициализация
        self._generate_mutations()
        self._derive_abilities()
        self._create_visual_mutations()
        self._apply_mutation_effects()
        
        logger.info(f"Создан мутант {name} уровня {mutation_level}")
    
    def _generate_mutations(self) -> None:
        """Генерация мутаций на основе уровня"""
        try:
            # Базовые мутации для всех мутантов
            base_mutations = [
                self._create_base_mutation("enhanced_strength", MutationType.PHYSICAL, MutationLevel.MINOR),
                self._create_base_mutation("enhanced_agility", MutationType.PHYSICAL, MutationLevel.MINOR),
                self._create_base_mutation("enhanced_intelligence", MutationType.MENTAL, MutationLevel.MINOR)
            ]
            
            for mutation in base_mutations:
                self.mutations[mutation.mutation_id] = mutation
            
            # Дополнительные мутации на основе уровня
            additional_mutations = self.mutation_level - 3  # Уже есть 3 базовые
            for i in range(additional_mutations):
                mutation_type = random.choice(list(MutationType))
                mutation_level = random.choice(list(MutationLevel))
                mutation = self._create_random_mutation(f"mutation_{i + 1}", mutation_type, mutation_level)
                self.mutations[mutation.mutation_id] = mutation
            
            logger.info(f"Сгенерировано {len(self.mutations)} мутаций для мутанта {self.name}")
            
        except Exception as e:
            logger.error(f"Ошибка генерации мутаций: {e}")
    
    def _create_base_mutation(self, mutation_id: str, mutation_type: MutationType, level: MutationLevel) -> Mutation:
        """Создание базовой мутации"""
        if mutation_id == "enhanced_strength":
            return Mutation(
                mutation_id=mutation_id,
                name="Усиленная сила",
                description="Базовая мутация силы для всех мутантов",
                mutation_type=mutation_type,
                level=level,
                effects={"strength": 15, "health": 50},
                visual_effects=["muscle_definition"],
                sound_effects=["strength_growl"]
            )
        elif mutation_id == "enhanced_agility":
            return Mutation(
                mutation_id=mutation_id,
                name="Усиленная ловкость",
                description="Базовая мутация ловкости для всех мутантов",
                mutation_type=mutation_type,
                level=level,
                effects={"agility": 12, "dodge_chance": 0.3},
                visual_effects=["graceful_movement"],
                sound_effects=["agility_whisper"]
            )
        elif mutation_id == "enhanced_intelligence":
            return Mutation(
                mutation_id=mutation_id,
                name="Усиленный интеллект",
                description="Базовая мутация интеллекта для всех мутантов",
                mutation_type=mutation_type,
                level=level,
                effects={"intelligence": 10, "magic_power": 25},
                visual_effects=["intelligent_eyes"],
                sound_effects=["intelligence_hum"]
            )
        else:
            # Создаем случайную базовую мутацию
            return self._create_random_mutation(mutation_id, mutation_type, level)
    
    def _create_random_mutation(self, mutation_id: str, mutation_type: MutationType, level: MutationLevel) -> Mutation:
        """Создание случайной мутации"""
        mutation_templates = {
            MutationType.PHYSICAL: {
                "name": "Физическая мутация",
                "description": "Улучшает физические характеристики",
                "effects": {"strength": random.randint(5, 25), "health": random.randint(20, 100)}
            },
            MutationType.MENTAL: {
                "name": "Ментальная мутация",
                "description": "Улучшает умственные способности",
                "effects": {"intelligence": random.randint(5, 20), "magic_power": random.randint(10, 50)}
            },
            MutationType.COMBAT: {
                "name": "Боевая мутация",
                "description": "Улучшает боевые навыки",
                "effects": {"damage": random.randint(10, 40), "critical_chance": random.randint(5, 15)}
            },
            MutationType.MAGIC: {
                "name": "Магическая мутация",
                "description": "Улучшает магические способности",
                "effects": {"magic_power": random.randint(15, 60), "mana": random.randint(20, 80)}
            },
            MutationType.ADAPTIVE: {
                "name": "Адаптивная мутация",
                "description": "Адаптируется к окружающей среде",
                "effects": {"adaptation_rate": random.uniform(0.1, 0.3), "resistance": random.randint(5, 20)}
            },
            MutationType.COMBINATIONAL: {
                "name": "Комбинационная мутация",
                "description": "Комбинирует несколько типов мутаций",
                "effects": {"hybrid_power": random.randint(20, 80), "synergy_bonus": random.randint(10, 30)}
            }
        }
        
        template = mutation_templates.get(mutation_type, mutation_templates[MutationType.PHYSICAL])
        
        return Mutation(
            mutation_id=mutation_id,
            name=template["name"],
            description=template["description"],
            mutation_type=mutation_type,
            level=level,
            effects=template["effects"],
            visual_effects=[f"{mutation_type.value}_effect"],
            sound_effects=[f"{mutation_type.value}_sound"]
        )
    
    def _derive_abilities(self) -> None:
        """Выведение способностей на основе мутаций"""
        try:
            # Базовые способности для всех мутантов
            base_abilities = [
                self._create_base_ability("claw_attack", "Когти", "Базовая атака когтями", "melee", 2.0, 2.0, 15),
                self._create_base_ability("bite_attack", "Укус", "Атака укусом", "melee", 3.0, 1.5, 20),
                self._create_base_ability("roar", "Рев", "Устрашающий рев", "area", 8.0, 5.0, 0)
            ]
            
            for ability in base_abilities:
                self.abilities[ability.ability_id] = ability
            
            # Дополнительные способности на основе мутаций
            for mutation in self.mutations.values():
                if mutation.mutation_type == MutationType.COMBAT:
                    # Боевые способности
                    combat_ability = self._create_combat_ability(mutation)
                    if combat_ability:
                        self.abilities[combat_ability.ability_id] = combat_ability
                        self.derived_abilities.append(combat_ability.ability_id)
                
                elif mutation.mutation_type == MutationType.MAGIC:
                    # Магические способности
                    magic_ability = self._create_magic_ability(mutation)
                    if magic_ability:
                        self.abilities[magic_ability.ability_id] = magic_ability
                        self.derived_abilities.append(magic_ability.ability_id)
                
                elif mutation.mutation_type == MutationType.ADAPTIVE:
                    # Адаптивные способности
                    adaptive_ability = self._create_adaptive_ability(mutation)
                    if adaptive_ability:
                        self.abilities[adaptive_ability.ability_id] = adaptive_ability
                        self.derived_abilities.append(adaptive_ability.ability_id)
            
            logger.info(f"Создано {len(self.abilities)} способностей для мутанта {self.name}")
            
        except Exception as e:
            logger.error(f"Ошибка создания способностей: {e}")
    
    def _create_base_ability(self, ability_id: str, name: str, description: str, 
                            ability_type: str, cooldown: float, range: float, damage: float) -> MutantAbility:
        """Создание базовой способности"""
        return MutantAbility(
            ability_id=ability_id,
            name=name,
            description=description,
            ability_type=ability_type,
            cooldown=cooldown,
            range=range,
            damage=damage,
            effects={"damage": damage},
            visual_effects=[f"{ability_id}_effect"],
            sound_effects=[f"{ability_id}_sound"],
            requirements={}
        )
    
    def _create_combat_ability(self, mutation: Mutation) -> Optional[MutantAbility]:
        """Создание боевой способности на основе мутации"""
        try:
            if mutation.level in [MutationLevel.MAJOR, MutationLevel.EXTREME, MutationLevel.LEGENDARY]:
                return MutantAbility(
                    ability_id=f"combat_{mutation.mutation_id}",
                    name=f"Боевая {mutation.name}",
                    description=f"Боевая способность на основе {mutation.name}",
                    ability_type="melee",
                    cooldown=5.0,
                    range=3.0,
                    damage=mutation.effects.get("damage", 25),
                    effects=mutation.effects.copy(),
                    visual_effects=mutation.visual_effects.copy(),
                    sound_effects=mutation.sound_effects.copy(),
                    requirements={"mutation_level": mutation.level.value}
                )
            return None
            
        except Exception as e:
            logger.error(f"Ошибка создания боевой способности: {e}")
            return None
    
    def _create_magic_ability(self, mutation: Mutation) -> Optional[MutantAbility]:
        """Создание магической способности на основе мутации"""
        try:
            if mutation.level in [MutationLevel.MAJOR, MutationLevel.EXTREME, MutationLevel.LEGENDARY]:
                return MutantAbility(
                    ability_id=f"magic_{mutation.mutation_id}",
                    name=f"Магическая {mutation.name}",
                    description=f"Магическая способность на основе {mutation.name}",
                    ability_type="ranged",
                    cooldown=8.0,
                    range=8.0,
                    damage=mutation.effects.get("magic_power", 30),
                    effects=mutation.effects.copy(),
                    visual_effects=mutation.visual_effects.copy(),
                    sound_effects=mutation.sound_effects.copy(),
                    requirements={"mutation_level": mutation.level.value}
                )
            return None
            
        except Exception as e:
            logger.error(f"Ошибка создания магической способности: {e}")
            return None
    
    def _create_adaptive_ability(self, mutation: Mutation) -> Optional[MutantAbility]:
        """Создание адаптивной способности на основе мутации"""
        try:
            if mutation.level in [MutationLevel.MODERATE, MutationLevel.MAJOR, MutationLevel.EXTREME]:
                return MutantAbility(
                    ability_id=f"adaptive_{mutation.mutation_id}",
                    name=f"Адаптивная {mutation.name}",
                    description=f"Адаптивная способность на основе {mutation.name}",
                    ability_type="utility",
                    cooldown=15.0,
                    range=0.0,
                    damage=0,
                    effects=mutation.effects.copy(),
                    visual_effects=mutation.visual_effects.copy(),
                    sound_effects=mutation.sound_effects.copy(),
                    requirements={"mutation_level": mutation.level.value}
                )
            return None
            
        except Exception as e:
            logger.error(f"Ошибка создания адаптивной способности: {e}")
            return None
    
    def _create_visual_mutations(self) -> None:
        """Создание визуальных мутаций"""
        try:
            for mutation in self.mutations.values():
                visual_mutation = VisualMutation(
                    mutation_id=mutation.mutation_id,
                    name=f"Визуальная {mutation.name}",
                    description=f"Визуальное проявление {mutation.name}",
                    visual_type=mutation.mutation_type.value,
                    parameters={
                        "scale": random.uniform(0.8, 1.2),
                        "color_modifier": random.uniform(0.7, 1.3),
                        "intensity": random.uniform(0.5, 1.5)
                    },
                    intensity=1.0,
                    duration=None
                )
                
                self.visual_mutations[mutation.mutation_id] = visual_mutation
            
            logger.info(f"Создано {len(self.visual_mutations)} визуальных мутаций")
            
        except Exception as e:
            logger.error(f"Ошибка создания визуальных мутаций: {e}")
    
    def _apply_mutation_effects(self) -> None:
        """Применение эффектов мутаций к характеристикам"""
        try:
            # Применяем эффекты всех мутаций
            for mutation in self.mutations.values():
                for effect_name, effect_value in mutation.effects.items():
                    if hasattr(self, effect_name):
                        current_value = getattr(self, effect_name)
                        if isinstance(current_value, (int, float)):
                            setattr(self, effect_name, current_value + effect_value)
                        elif isinstance(current_value, dict):
                            if effect_name not in current_value:
                                current_value[effect_name] = 0
                            current_value[effect_name] += effect_value
            
            # Обновляем визуальные параметры
            self._update_visual_parameters()
            
            logger.info(f"Эффекты мутаций применены к мутанту {self.name}")
            
        except Exception as e:
            logger.error(f"Ошибка применения эффектов мутаций: {e}")
    
    def _update_visual_parameters(self) -> None:
        """Обновление визуальных параметров на основе мутаций"""
        try:
            # Вычисляем общий масштаб
            scale_modifier = 1.0
            for mutation in self.mutations.values():
                if "scale" in mutation.effects:
                    scale_modifier += mutation.effects["scale"] * 0.1
            
            self.current_scale = self.base_scale * scale_modifier
            
            # Вычисляем общий цвет
            color_modifier = 1.0
            for mutation in self.mutations.values():
                if "color" in mutation.effects:
                    color_modifier += mutation.effects["color"] * 0.1
            
            # Применяем изменения к модели
            self.setScale(self.current_scale)
            
            logger.debug(f"Визуальные параметры обновлены: масштаб={self.current_scale:.2f}")
            
        except Exception as e:
            logger.error(f"Ошибка обновления визуальных параметров: {e}")
    
    def can_use_ability(self, ability_id: str) -> bool:
        """Проверка возможности использования способности"""
        try:
            if ability_id not in self.abilities:
                return False
            
            ability = self.abilities[ability_id]
            current_time = time.time()
            
            # Проверяем кулдаун
            if current_time - ability.last_used < ability.cooldown:
                return False
            
            # Проверяем заряды
            if ability.charges is not None and ability.charges <= 0:
                return False
            
            # Проверяем требования
            for req_name, req_value in ability.requirements.items():
                if hasattr(self, req_name):
                    current_value = getattr(self, req_name)
                    if current_value < req_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки способности {ability_id}: {e}")
            return False
    
    def use_ability(self, ability_id: str, target_position: Tuple[float, float, float] = None) -> bool:
        """Использование способности"""
        try:
            if not self.can_use_ability(ability_id):
                return False
            
            ability = self.abilities[ability_id]
            current_time = time.time()
            
            # Обновляем время использования
            ability.last_used = current_time
            
            # Уменьшаем заряды
            if ability.charges is not None:
                ability.charges -= 1
            
            # Применяем эффекты способности
            self._apply_ability_effects(ability, target_position)
            
            # Добавляем в историю
            self.mutation_history.append({
                "timestamp": current_time,
                "action": "ability_used",
                "ability_id": ability_id,
                "ability_name": ability.name,
                "target_position": target_position
            })
            
            logger.info(f"Мутант {self.name} использовал способность {ability.name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка использования способности {ability_id}: {e}")
            return False
    
    def _apply_ability_effects(self, ability: MutantAbility, target_position: Tuple[float, float, float]) -> None:
        """Применение эффектов способности"""
        try:
            # TODO: Применение урона, эффектов, визуальных и звуковых эффектов
            logger.debug(f"Применены эффекты способности {ability.name}")
            
        except Exception as e:
            logger.error(f"Ошибка применения эффектов способности: {e}")
    
    def learn_from_experience(self, experience_type: str, amount: float) -> bool:
        """Обучение на основе опыта"""
        try:
            self.learning_progress += amount
            
            # Проверяем возможность эволюции
            if self.learning_progress >= 100.0:
                self._evolve()
                self.learning_progress = 0.0
            
            # Добавляем в историю
            self.mutation_history.append({
                "timestamp": time.time(),
                "action": "experience_gained",
                "experience_type": experience_type,
                "amount": amount,
                "total_progress": self.learning_progress
            })
            
            logger.debug(f"Мутант {self.name} получил опыт {experience_type}: {amount}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обучения мутанта: {e}")
            return False
    
    def _evolve(self) -> bool:
        """Эволюция мутанта"""
        try:
            self.evolution_stage += 1
            
            # Создаем новую мутацию
            new_mutation = self._create_evolutionary_mutation()
            self.mutations[new_mutation.mutation_id] = new_mutation
            
            # Обновляем способности
            self._derive_abilities()
            
            # Обновляем визуальные параметры
            self._update_visual_parameters()
            
            logger.info(f"Мутант {self.name} эволюционировал до стадии {self.evolution_stage}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка эволюции мутанта: {e}")
            return False
    
    def _create_evolutionary_mutation(self) -> Mutation:
        """Создание эволюционной мутации"""
        mutation_types = [MutationType.ADAPTIVE, MutationType.COMBINATIONAL]
        mutation_type = random.choice(mutation_types)
        
        return Mutation(
            mutation_id=f"evolutionary_{self.evolution_stage}",
            name=f"Эволюционная мутация {self.evolution_stage}",
            description=f"Мутация, полученная в результате эволюции",
            mutation_type=mutation_type,
            level=MutationLevel.MAJOR,
            effects={"evolutionary_power": 50, "adaptation_rate": 0.2},
            visual_effects=["evolutionary_glow"],
            sound_effects=["evolutionary_sound"]
        )
    
    def update(self, delta_time: float) -> None:
        """Обновление мутанта"""
        try:
            # Обновляем адаптацию
            self._update_adaptation(delta_time)
            
            # Проверяем переход в следующую фазу
            self._check_phase_transition()
            
            # Обновляем визуальные эффекты
            self._update_visual_effects(delta_time)
            
        except Exception as e:
            logger.error(f"Ошибка обновления мутанта {self.name}: {e}")
    
    def _update_adaptation(self, delta_time: float) -> None:
        """Обновление адаптации"""
        try:
            # Увеличиваем адаптацию со временем
            self.adaptation_rate += delta_time * 0.01
            
            # Ограничиваем максимальную адаптацию
            self.adaptation_rate = min(self.adaptation_rate, 1.0)
            
        except Exception as e:
            logger.error(f"Ошибка обновления адаптации: {e}")
    
    def _check_phase_transition(self) -> None:
        """Проверка перехода в следующую фазу"""
        try:
            if self.current_phase < self.max_phases:
                # Проверяем здоровье для перехода
                if hasattr(self, 'health') and hasattr(self, 'max_health'):
                    health_percentage = self.health / self.max_health
                    threshold = self.phase_health_thresholds[self.current_phase - 1]
                    
                    if health_percentage <= threshold:
                        self._transition_to_next_phase()
            
        except Exception as e:
            logger.error(f"Ошибка проверки перехода фазы: {e}")
    
    def _transition_to_next_phase(self) -> None:
        """Переход в следующую фазу"""
        try:
            self.current_phase += 1
            
            # Создаем фазу-специфичную мутацию
            phase_mutation = self._create_phase_mutation()
            self.mutations[phase_mutation.mutation_id] = phase_mutation
            
            # Обновляем способности
            self._derive_abilities()
            
            # Обновляем визуальные параметры
            self._update_visual_parameters()
            
            logger.info(f"Мутант {self.name} перешел в фазу {self.current_phase}")
            
        except Exception as e:
            logger.error(f"Ошибка перехода в следующую фазу: {e}")
    
    def _create_phase_mutation(self) -> Mutation:
        """Создание мутации для новой фазы"""
        return Mutation(
            mutation_id=f"phase_{self.current_phase}_mutation",
            name=f"Мутация фазы {self.current_phase}",
            description=f"Мутация, полученная при переходе в фазу {self.current_phase}",
            mutation_type=MutationType.COMBINATIONAL,
            level=MutationLevel.MAJOR,
            effects={"phase_power": 75, "phase_bonus": 25},
            visual_effects=[f"phase_{self.current_phase}_effect"],
            sound_effects=[f"phase_{self.current_phase}_sound"]
        )
    
    def _update_visual_effects(self, delta_time: float) -> None:
        """Обновление визуальных эффектов"""
        try:
            # Обновляем интенсивность визуальных эффектов
            for visual_mutation in self.visual_mutations.values():
                if visual_mutation.duration:
                    # Уменьшаем интенсивность со временем
                    visual_mutation.intensity -= delta_time / visual_mutation.duration
                    visual_mutation.intensity = max(0.0, visual_mutation.intensity)
                    
                    # Удаляем истекшие эффекты
                    if visual_mutation.intensity <= 0:
                        del self.visual_mutations[visual_mutation.mutation_id]
            
        except Exception as e:
            logger.error(f"Ошибка обновления визуальных эффектов: {e}")
    
    def get_mutation_summary(self) -> Dict[str, Any]:
        """Получение сводки по мутациям"""
        try:
            return {
                "mutant_id": self.entity_id,
                "name": self.name,
                "mutation_level": self.mutation_level,
                "current_phase": self.current_phase,
                "evolution_stage": self.evolution_stage,
                "total_mutations": len(self.mutations),
                "total_abilities": len(self.abilities),
                "adaptation_rate": self.adaptation_rate,
                "learning_progress": self.learning_progress,
                "mutations": [m.name for m in self.mutations.values()],
                "abilities": [a.name for a in self.abilities.values()],
                "visual_mutations": [vm.name for vm in self.visual_mutations.values()]
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения сводки по мутациям: {e}")
            return {}
    
    def get_combat_stats(self) -> Dict[str, Any]:
        """Получение боевых характеристик"""
        try:
            stats = {}
            
            # Базовые характеристики
            for attr in ['strength', 'agility', 'intelligence', 'health', 'mana']:
                if hasattr(self, attr):
                    stats[attr] = getattr(self, attr)
            
            # Характеристики от мутаций
            for mutation in self.mutations.values():
                for effect_name, effect_value in mutation.effects.items():
                    if effect_name in stats:
                        stats[effect_name] += effect_value
                    else:
                        stats[effect_name] = effect_value
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения боевых характеристик: {e}")
            return {}
    
    def destroy(self) -> bool:
        """Уничтожение мутанта"""
        try:
            # Очищаем все данные
            self.mutations.clear()
            self.visual_mutations.clear()
            self.abilities.clear()
            self.mutation_history.clear()
            
            logger.info(f"Мутант {self.name} уничтожен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения мутанта: {e}")
            return False
