#!/usr/bin/env python3
"""
Система мутантов AI-EVOLVE
Процедурно генерируемые мутанты с адаптивным поведением
"""

import logging
import time
import random
import math
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

from ..core.constants import constants_manager, StatType, DamageType, AIState, EntityType
from .base_entity import BaseEntity, EntityType as BaseEntityType

logger = logging.getLogger(__name__)

class MutationType(Enum):
    """Типы мутаций"""
    PHYSICAL = "physical"
    MENTAL = "mental"
    COMBAT = "combat"
    MAGIC = "magic"
    ADAPTIVE = "adaptive"
    COMBINATIONAL = "combinational"

class MutationLevel(Enum):
    """Уровни мутаций"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    EXTREME = "extreme"

@dataclass
class Mutation:
    """Мутация мутанта"""
    mutation_id: str
    name: str
    description: str
    mutation_type: MutationType
    level: MutationLevel
    effects: Dict[str, Any] = field(default_factory=dict)
    visual_effects: List[str] = field(default_factory=list)
    sound_effects: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    conflicts: List[str] = field(default_factory=list)
    synergies: List[str] = field(default_factory=list)

@dataclass
class MutantAbility:
    """Способность мутанта"""
    ability_id: str
    name: str
    description: str
    mutation_source: str
    cooldown: float
    damage: int
    damage_type: DamageType
    range: float
    effects: List[str] = field(default_factory=list)
    visual_effects: List[str] = field(default_factory=list)
    sound_effects: List[str] = field(default_factory=list)
    unlocked: bool = False
    last_used: float = 0.0

@dataclass
class VisualMutation:
    """Визуальная мутация"""
    mutation_id: str
    visual_type: str  # color, scale, shape, particles
    value: Any
    duration: float = 0.0
    transition_time: float = 0.5

class Mutant(BaseEntity):
    """Класс мутанта - процедурно генерируемый противник"""
    
    def __init__(self, mutant_id: str, name: str, mutation_level: int, position: Tuple[float, float, float]):
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
                
                mutation = self._create_random_mutation(f"mutation_{i+1}", mutation_type, mutation_level)
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
                description="Увеличивает физическую силу",
                mutation_type=mutation_type,
                level=level,
                effects={"strength": 10, "health": 50},
                visual_effects=["muscle_growth"],
                sound_effects=["muscle_flex"]
            )
        elif mutation_id == "enhanced_agility":
            return Mutation(
                mutation_id=mutation_id,
                name="Усиленная ловкость",
                description="Увеличивает ловкость и скорость",
                mutation_type=mutation_type,
                level=level,
                effects={"agility": 15, "speed": 1.2},
                visual_effects=["nimble_movement"],
                sound_effects=["quick_step"]
            )
        elif mutation_id == "enhanced_intelligence":
            return Mutation(
                mutation_id=mutation_id,
                name="Усиленный интеллект",
                description="Увеличивает интеллект и магическую силу",
                mutation_type=mutation_type,
                level=level,
                effects={"intelligence": 12, "magic_power": 20},
                visual_effects=["brain_glow"],
                sound_effects=["mental_power"]
            )
        
        # Fallback
        return Mutation(
            mutation_id=mutation_id,
            name="Базовая мутация",
            description="Базовая мутация",
            mutation_type=mutation_type,
            level=level,
            effects={},
            visual_effects=[],
            sound_effects=[]
        )
    
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
            self.abilities["basic_attack"] = MutantAbility(
                ability_id="basic_attack",
                name="Базовая атака",
                description="Базовая атака мутанта",
                mutation_source="base",
                cooldown=2.0,
                damage=30,
                damage_type=DamageType.PHYSICAL,
                range=2.0,
                effects=["physical_damage"],
                visual_effects=["attack_animation"],
                sound_effects=["attack_sound"],
                unlocked=True
            )
            
            # Способности на основе мутаций
            for mutation_id, mutation in self.mutations.items():
                if mutation.mutation_type == MutationType.COMBAT:
                    self._create_combat_ability(mutation)
                elif mutation.mutation_type == MutationType.MAGIC:
                    self._create_magic_ability(mutation)
                elif mutation.mutation_type == MutationType.ADAPTIVE:
                    self._create_adaptive_ability(mutation)
            
            # Способности на основе уровня памяти (если доступна система памяти)
            self._add_memory_based_abilities()
            
            logger.info(f"Выведено {len(self.abilities)} способностей для мутанта {self.name}")
            
        except Exception as e:
            logger.error(f"Ошибка выведения способностей: {e}")
    
    def _create_combat_ability(self, mutation: Mutation) -> None:
        """Создание боевой способности"""
        ability_id = f"combat_{mutation.mutation_id}"
        
        self.abilities[ability_id] = MutantAbility(
            ability_id=ability_id,
            name=f"Боевая {mutation.name}",
            description=f"Боевая способность на основе {mutation.name}",
            mutation_source=mutation.mutation_id,
            cooldown=8.0,
            damage=mutation.effects.get("damage", 50),
            damage_type=DamageType.PHYSICAL,
            range=4.0,
            effects=["combat_boost", "mutation_enhancement"],
            visual_effects=mutation.visual_effects + ["combat_aura"],
            sound_effects=mutation.sound_effects + ["combat_sound"],
            unlocked=True
        )
    
    def _create_magic_ability(self, mutation: Mutation) -> None:
        """Создание магической способности"""
        ability_id = f"magic_{mutation.mutation_id}"
        
        self.abilities[ability_id] = MutantAbility(
            ability_id=ability_id,
            name=f"Магическая {mutation.name}",
            description=f"Магическая способность на основе {mutation.name}",
            mutation_source=mutation.mutation_id,
            cooldown=15.0,
            damage=mutation.effects.get("magic_power", 60),
            damage_type=DamageType.LIGHTNING,  # По умолчанию молния
            range=6.0,
            effects=["magic_boost", "mutation_enhancement"],
            visual_effects=mutation.visual_effects + ["magic_aura"],
            sound_effects=mutation.sound_effects + ["magic_sound"],
            unlocked=True
        )
    
    def _create_adaptive_ability(self, mutation: Mutation) -> None:
        """Создание адаптивной способности"""
        ability_id = f"adaptive_{mutation.mutation_id}"
        
        self.abilities[ability_id] = MutantAbility(
            ability_id=ability_id,
            name=f"Адаптивная {mutation.name}",
            description=f"Адаптивная способность на основе {mutation.name}",
            mutation_source=mutation.mutation_id,
            cooldown=20.0,
            damage=0,
            damage_type=DamageType.PHYSICAL,
            range=0.0,
            effects=["adaptation_boost", "environmental_resistance"],
            visual_effects=mutation.visual_effects + ["adaptation_aura"],
            sound_effects=mutation.sound_effects + ["adaptation_sound"],
            unlocked=True
        )
    
    def _add_memory_based_abilities(self) -> None:
        """Добавление способностей на основе уровня памяти"""
        try:
            # TODO: Интеграция с системой памяти
            # Пока добавляем базовые способности на основе уровня мутаций
            
            if self.mutation_level >= 3:
                self.abilities["memory_blast"] = MutantAbility(
                    ability_id="memory_blast",
                    name="Взрыв памяти",
                    description="Атака на основе накопленного опыта",
                    mutation_source="memory",
                    cooldown=25.0,
                    damage=80,
                    damage_type=DamageType.TRUE,
                    range=5.0,
                    effects=["memory_damage", "experience_drain"],
                    visual_effects=["memory_explosion"],
                    sound_effects=["memory_blast"],
                    unlocked=True
                )
            
            if self.mutation_level >= 5:
                self.abilities["evolutionary_leap"] = MutantAbility(
                    ability_id="evolutionary_leap",
                    name="Эволюционный прыжок",
                    description="Мощный прыжок с эволюционным ускорением",
                    mutation_source="evolution",
                    cooldown=30.0,
                    damage=100,
                    damage_type=DamageType.PHYSICAL,
                    range=8.0,
                    effects=["evolutionary_boost", "temporary_enhancement"],
                    visual_effects=["evolutionary_trail"],
                    sound_effects=["evolutionary_leap"],
                    unlocked=True
                )
                
        except Exception as e:
            logger.error(f"Ошибка добавления способностей на основе памяти: {e}")
    
    def _create_visual_mutations(self) -> None:
        """Создание визуальных мутаций"""
        try:
            # Базовые визуальные мутации
            self.visual_mutations["base_scale"] = VisualMutation(
                mutation_id="base_scale",
                visual_type="scale",
                value=1.0,
                duration=0.0,
                transition_time=0.5
            )
            
            self.visual_mutations["base_color"] = VisualMutation(
                mutation_id="base_color",
                visual_type="color",
                value=(1, 1, 1, 1),
                duration=0.0,
                transition_time=0.5
            )
            
            # Визуальные мутации на основе генетических мутаций
            for mutation_id, mutation in self.mutations.items():
                if mutation.mutation_type == MutationType.PHYSICAL:
                    self._add_physical_visual_mutation(mutation)
                elif mutation.mutation_type == MutationType.MAGIC:
                    self._add_magic_visual_mutation(mutation)
                elif mutation.mutation_type == MutationType.COMBINATIONAL:
                    self._add_combinational_visual_mutation(mutation)
            
        except Exception as e:
            logger.error(f"Ошибка создания визуальных мутаций: {e}")
    
    def _add_physical_visual_mutation(self, mutation: Mutation) -> None:
        """Добавление физической визуальной мутации"""
        mutation_id = f"visual_{mutation.mutation_id}"
        
        # Увеличиваем размер на основе физических мутаций
        scale_boost = 1.0 + (mutation.effects.get("strength", 0) / 100.0)
        
        self.visual_mutations[mutation_id] = VisualMutation(
            mutation_id=mutation_id,
            visual_type="scale",
            value=scale_boost,
            duration=0.0,
            transition_time=1.0
        )
    
    def _add_magic_visual_mutation(self, mutation: Mutation) -> None:
        """Добавление магической визуальной мутации"""
        mutation_id = f"visual_{mutation.mutation_id}"
        
        # Изменяем цвет на основе магических мутаций
        magic_power = mutation.effects.get("magic_power", 0)
        color_intensity = min(1.0, magic_power / 100.0)
        
        self.visual_mutations[mutation_id] = VisualMutation(
            mutation_id=mutation_id,
            visual_type="color",
            value=(0.5, 0.5, 1.0, color_intensity),
            duration=0.0,
            transition_time=1.0
        )
    
    def _add_combinational_visual_mutation(self, mutation: Mutation) -> None:
        """Добавление комбинационной визуальной мутации"""
        mutation_id = f"visual_{mutation.mutation_id}"
        
        # Комбинированный эффект
        hybrid_power = mutation.effects.get("hybrid_power", 0)
        effect_intensity = min(1.0, hybrid_power / 100.0)
        
        self.visual_mutations[mutation_id] = VisualMutation(
            mutation_id=mutation_id,
            visual_type="particles",
            value=f"hybrid_effect_{effect_intensity}",
            duration=10.0,
            transition_time=2.0
        )
    
    def _apply_mutation_effects(self) -> None:
        """Применение эффектов мутаций"""
        try:
            # Применяем эффекты к базовым характеристикам
            for mutation in self.mutations.values():
                for stat, value in mutation.effects.items():
                    if hasattr(self, stat):
                        current_value = getattr(self, stat, 0)
                        setattr(self, stat, current_value + value)
                    else:
                        # Создаем атрибут если его нет
                        setattr(self, stat, value)
            
            # Обновляем визуальные параметры
            self._update_visual_parameters()
            
            logger.info(f"Применены эффекты {len(self.mutations)} мутаций для мутанта {self.name}")
            
        except Exception as e:
            logger.error(f"Ошибка применения эффектов мутаций: {e}")
    
    def _update_visual_parameters(self) -> None:
        """Обновление визуальных параметров"""
        try:
            # Вычисляем итоговый масштаб
            total_scale = self.base_scale
            for mutation in self.visual_mutations.values():
                if mutation.visual_type == "scale":
                    total_scale *= mutation.value
            
            self.current_scale = total_scale
            
            # Вычисляем итоговый цвет
            total_color = list(self.base_color)
            for mutation in self.visual_mutations.values():
                if mutation.visual_type == "color":
                    mutation_color = mutation.value
                    for i in range(min(len(total_color), len(mutation_color))):
                        total_color[i] = (total_color[i] + mutation_color[i]) / 2
            
            self.current_color = tuple(total_color)
            
            # TODO: Применить к 3D модели
            # self.setScale(self.current_scale)
            # self.setColor(*self.current_color)
            
        except Exception as e:
            logger.error(f"Ошибка обновления визуальных параметров: {e}")
    
    def update_phase(self) -> bool:
        """Обновление фазы мутанта"""
        try:
            health_percentage = self.health / self.max_health
            
            if health_percentage <= self.phase_health_thresholds[0] and self.current_phase == 1:
                return self._transition_to_phase(2)
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обновления фазы мутанта: {e}")
            return False
    
    def _transition_to_phase(self, new_phase: int) -> bool:
        """Переход к новой фазе"""
        try:
            self.current_phase = new_phase
            
            # Разблокируем способности фазы
            self._unlock_phase_abilities()
            
            # Показываем эффект эволюции
            self._show_mutation_evolution_effect()
            
            logger.info(f"Мутант {self.name} перешел в фазу {new_phase}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка перехода к фазе {new_phase}: {e}")
            return False
    
    def _unlock_phase_ability(self) -> None:
        """Разблокировка способности фазы"""
        try:
            # TODO: Разблокировка новых способностей
            pass
            
        except Exception as e:
            logger.error(f"Ошибка разблокировки способности фазы: {e}")
    
    def _show_mutation_evolution_effect(self) -> None:
        """Визуальный эффект эволюции мутанта"""
        try:
            # TODO: Визуальные эффекты эволюции
            # - Изменение размера
            # - Изменение цвета
            # - Эффект частиц
            
            logger.info(f"Воспроизведен эффект эволюции мутанта {self.name}")
            
        except Exception as e:
            logger.error(f"Ошибка показа эффекта эволюции: {e}")
    
    def can_use_ability(self, ability_id: str) -> bool:
        """Проверка возможности использования способности"""
        try:
            if ability_id not in self.abilities:
                return False
            
            ability = self.abilities[ability_id]
            
            # Проверяем разблокировку
            if not ability.unlocked:
                return False
            
            # Проверяем кулдаун
            current_time = time.time()
            if current_time - ability.last_used < ability.cooldown:
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
            
            # Применяем способность
            if target_position:
                self._apply_ability_effects(ability, target_position)
            else:
                self._apply_ability_effects(ability, self.getPos())
            
            logger.info(f"Мутант {self.name} использовал способность: {ability.name}")
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
            # Увеличиваем прогресс обучения
            self.learning_progress += amount * self.adaptation_rate
            
            # Проверяем эволюцию
            if self.learning_progress >= 100.0:
                self._evolve()
                self.learning_progress = 0.0
            
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
            # Обновляем фазу
            self.update_phase()
            
            # Обновляем способности
            self._update_abilities(delta_time)
            
            # Обновляем визуальные параметры
            self._update_visual_parameters()
            
        except Exception as e:
            logger.error(f"Ошибка обновления мутанта: {e}")
    
    def _update_abilities(self, delta_time: float) -> None:
        """Обновление способностей"""
        try:
            # TODO: Автоматическое использование способностей
            pass
            
        except Exception as e:
            logger.error(f"Ошибка обновления способностей: {e}")
    
    def get_mutant_status(self) -> Dict[str, Any]:
        """Получение статуса мутанта"""
        try:
            return {
                "mutant_id": self.entity_id,
                "name": self.name,
                "mutation_level": self.mutation_level,
                "current_phase": self.current_phase,
                "evolution_stage": self.evolution_stage,
                "learning_progress": self.learning_progress,
                "adaptation_rate": self.adaptation_rate,
                "mutations_count": len(self.mutations),
                "abilities_count": len(self.abilities),
                "unlocked_abilities": [aid for aid, ability in self.abilities.items() if ability.unlocked],
                "visual_mutations": [vm.mutation_id for vm in self.visual_mutations.values()],
                "current_scale": self.current_scale,
                "current_color": self.current_color
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статуса мутанта: {e}")
            return {}
