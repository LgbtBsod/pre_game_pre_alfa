#!/usr/bin/env python3
"""
Система многофазовых боссов AI-EVOLVE
Сложные противники с адаптивным поведением
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

class BossPhase(Enum):
    """Фазы босса"""
    PHASE_1 = 1
    PHASE_2 = 2
    PHASE_3 = 3

class BossType(Enum):
    """Типы боссов"""
    ALPHA_MUTANT = "alpha_mutant"
    CHIMERA = "chimera"
    EVOLUTIONARY = "evolutionary"
    GENETIC_MASTER = "genetic_master"

@dataclass
class BossAbility:
    """Способность босса"""
    ability_id: str
    name: str
    description: str
    phase: BossPhase
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
class BossWeakness:
    """Слабость босса"""
    damage_type: DamageType
    multiplier: float
    phase: BossPhase
    description: str

@dataclass
class BossPhaseData:
    """Данные фазы босса"""
    phase: BossPhase
    health_threshold: float  # Процент здоровья для активации
    abilities: List[str]  # ID способностей
    weaknesses: List[str]  # ID слабостей
    resistances: List[str]  # ID сопротивлений
    visual_indicators: Dict[str, Any] = field(default_factory=dict)
    phase_transition_effects: List[str] = field(default_factory=list)

class Boss(BaseEntity):
    """Класс босса - многофазовый противник"""
    
    def __init__(self, boss_id: str, name: str, boss_type: BossType, position: Tuple[float, float, float]):
        # Инициализируем базовую сущность
        super().__init__(boss_id, BaseEntityType.BOSS, name)
        
        # Специфичные для босса параметры
        self.boss_type = boss_type
        self.position = position
        self.setPos(*position)
        
        # Фазы босса
        self.current_phase = BossPhase.PHASE_1
        self.max_phases = 3
        self.phase_data: Dict[BossPhase, BossPhaseData] = {}
        
        # Способности и слабости
        self.abilities: Dict[str, BossAbility] = {}
        self.weaknesses: Dict[str, BossWeakness] = {}
        self.resistances: Dict[DamageType, float] = {}
        
        # Боевые параметры
        self.max_health = 1000
        self.health = self.max_health
        self.phase_health_thresholds = [1.0, 0.7, 0.3]  # Пороги для смены фаз
        
        # Визуальные индикаторы
        self.phase_indicator = None
        self.health_bar = None
        self.ability_indicators = []
        
        # Состояние боя
        self.is_phase_transitioning = False
        self.phase_transition_time = 0.0
        self.phase_transition_duration = 2.0
        
        # Инициализация
        self._initialize_boss_type()
        self._create_phase_data()
        self._create_abilities()
        self._create_weaknesses()
        self._create_visual_indicators()
        
        logger.info(f"Создан босс {name} типа {boss_type.value}")
    
    def _initialize_boss_type(self) -> None:
        """Инициализация типа босса"""
        if self.boss_type == BossType.ALPHA_MUTANT:
            self.max_health = 1200
            self.health = self.max_health
        elif self.boss_type == BossType.CHIMERA:
            self.max_health = 1500
            self.health = self.max_health
        elif self.boss_type == BossType.EVOLUTIONARY:
            self.max_health = 2000
            self.health = self.max_health
        elif self.boss_type == BossType.GENETIC_MASTER:
            self.max_health = 3000
            self.health = self.max_health
    
    def _create_phase_data(self) -> None:
        """Создание данных для фаз"""
        # Фаза 1
        self.phase_data[BossPhase.PHASE_1] = BossPhaseData(
            phase=BossPhase.PHASE_1,
            health_threshold=1.0,
            abilities=["basic_attack", "defensive_stance"],
            weaknesses=["fire"],
            resistances=["physical"],
            visual_indicators={"color": (1, 0, 0, 1), "scale": 1.0},
            phase_transition_effects=["phase_1_complete"]
        )
        
        # Фаза 2
        self.phase_data[BossPhase.PHASE_2] = BossPhaseData(
            phase=BossPhase.PHASE_2,
            health_threshold=0.7,
            abilities=["basic_attack", "defensive_stance", "special_ability_1"],
            weaknesses=["fire", "cold"],
            resistances=["physical", "lightning"],
            visual_indicators={"color": (1, 0.5, 0, 1), "scale": 1.2},
            phase_transition_effects=["phase_2_complete", "unlock_special_abilities"]
        )
        
        # Фаза 3
        self.phase_data[BossPhase.PHASE_3] = BossPhaseData(
            phase=BossPhase.PHASE_3,
            health_threshold=0.3,
            abilities=["basic_attack", "defensive_stance", "special_ability_1", "ultimate_ability"],
            weaknesses=["fire", "cold", "true_damage"],
            resistances=["physical", "lightning", "acid"],
            visual_indicators={"color": (0.5, 0, 1, 1), "scale": 1.5},
            phase_transition_effects=["phase_3_complete", "unlock_ultimate", "final_form"]
        )
    
    def _create_abilities(self) -> None:
        """Создание способностей босса"""
        if self.boss_type == BossType.ALPHA_MUTANT:
            self._create_alpha_mutant_abilities()
        elif self.boss_type == BossType.CHIMERA:
            self._create_chimera_abilities()
        elif self.boss_type == BossType.EVOLUTIONARY:
            self._create_evolutionary_abilities()
        elif self.boss_type == BossType.GENETIC_MASTER:
            self._create_genetic_master_abilities()
    
    def _create_alpha_mutant_abilities(self) -> None:
        """Создание способностей Alpha Mutant"""
        # Базовая атака
        self.abilities["basic_attack"] = BossAbility(
            ability_id="basic_attack",
            name="Генетический удар",
            description="Базовая атака с генетическими мутациями",
            phase=BossPhase.PHASE_1,
            cooldown=2.0,
            damage=50,
            damage_type=DamageType.PHYSICAL,
            range=3.0,
            effects=["genetic_mutation"],
            visual_effects=["genetic_trail"],
            sound_effects=["genetic_hit"],
            unlocked=True
        )
        
        # Защитная стойка
        self.abilities["defensive_stance"] = BossAbility(
            ability_id="defensive_stance",
            name="Мутационная защита",
            description="Увеличивает защиту и регенерацию",
            phase=BossPhase.PHASE_1,
            cooldown=15.0,
            damage=0,
            damage_type=DamageType.PHYSICAL,
            range=0.0,
            effects=["defense_boost", "regeneration"],
            visual_effects=["mutation_shield"],
            sound_effects=["mutation_activate"],
            unlocked=True
        )
        
        # Специальная способность 1
        self.abilities["special_ability_1"] = BossAbility(
            ability_id="special_ability_1",
            name="Волна мутаций",
            description="Волна генетических мутаций по области",
            phase=BossPhase.PHASE_2,
            cooldown=20.0,
            damage=100,
            damage_type=DamageType.ACID,
            range=8.0,
            effects=["area_damage", "genetic_corruption"],
            visual_effects=["mutation_wave"],
            sound_effects=["mutation_wave"],
            unlocked=False
        )
        
        # Ультимативная способность
        self.abilities["ultimate_ability"] = BossAbility(
            ability_id="ultimate_ability",
            name="Генетический взрыв",
            description="Мощный взрыв генетической энергии",
            phase=BossPhase.PHASE_3,
            cooldown=60.0,
            damage=300,
            damage_type=DamageType.TRUE,
            range=12.0,
            effects=["massive_damage", "genetic_instability"],
            visual_effects=["genetic_explosion"],
            sound_effects=["genetic_explosion"],
            unlocked=False
        )
    
    def _create_chimera_abilities(self) -> None:
        """Создание способностей Chimera"""
        # Базовая атака
        self.abilities["basic_attack"] = BossAbility(
            ability_id="basic_attack",
            name="Хвост-кнут",
            description="Атака хвостом с огненным эффектом",
            phase=BossPhase.PHASE_1,
            cooldown=1.5,
            damage=60,
            damage_type=DamageType.FIRE,
            range=4.0,
            effects=["fire_damage", "burn"],
            visual_effects=["fire_trail"],
            sound_effects=["tail_whip"],
            unlocked=True
        )
        
        # Защитная стойка
        self.abilities["defensive_stance"] = BossAbility(
            ability_id="defensive_stance",
            name="Огненная броня",
            description="Защита огненной броней",
            phase=BossPhase.PHASE_1,
            cooldown=12.0,
            damage=0,
            damage_type=DamageType.FIRE,
            range=0.0,
            effects=["fire_armor", "damage_reflection"],
            visual_effects=["fire_armor"],
            sound_effects=["armor_activate"],
            unlocked=True
        )
        
        # Специальная способность 1
        self.abilities["special_ability_1"] = BossAbility(
            ability_id="special_ability_1",
            name="Кислотный плевок",
            description="Плевок кислотой по области",
            phase=BossPhase.PHASE_2,
            cooldown=18.0,
            damage=120,
            damage_type=DamageType.ACID,
            range=10.0,
            effects=["area_damage", "acid_corrosion"],
            visual_effects=["acid_spit"],
            sound_effects=["acid_spit"],
            unlocked=False
        )
        
        # Ультимативная способность
        self.abilities["ultimate_ability"] = BossAbility(
            ability_id="ultimate_ability",
            name="Берсерк ярость",
            description="Входит в состояние берсерка",
            phase=BossPhase.PHASE_3,
            cooldown=45.0,
            damage=0,
            damage_type=DamageType.PHYSICAL,
            range=0.0,
            effects=["berserk_mode", "damage_boost", "speed_boost"],
            visual_effects=["berserk_aura"],
            sound_effects=["berserk_roar"],
            unlocked=False
        )
    
    def _create_evolutionary_abilities(self) -> None:
        """Создание способностей Evolutionary"""
        # TODO: Реализовать способности Evolutionary
        pass
    
    def _create_genetic_master_abilities(self) -> None:
        """Создание способностей Genetic Master"""
        # TODO: Реализовать способности Genetic Master
        pass
    
    def _create_weaknesses(self) -> None:
        """Создание слабостей босса"""
        # Слабости по фазам
        self.weaknesses["fire"] = BossWeakness(
            damage_type=DamageType.FIRE,
            multiplier=1.5,
            phase=BossPhase.PHASE_1,
            description="Уязвим к огню"
        )
        
        self.weaknesses["cold"] = BossWeakness(
            damage_type=DamageType.COLD,
            multiplier=1.3,
            phase=BossPhase.PHASE_2,
            description="Уязвим к холоду"
        )
        
        self.weaknesses["true_damage"] = BossWeakness(
            damage_type=DamageType.TRUE,
            multiplier=2.0,
            phase=BossPhase.PHASE_3,
            description="Критически уязвим к истинному урону"
        )
    
    def _create_visual_indicators(self) -> None:
        """Создание визуальных индикаторов"""
        # TODO: Создание 3D индикаторов фаз
        pass
    
    def update_phase(self) -> bool:
        """Обновление фазы босса на основе здоровья"""
        try:
            health_percentage = self.health / self.max_health
            new_phase = None
            
            # Определяем новую фазу
            if health_percentage <= self.phase_health_thresholds[2] and self.current_phase != BossPhase.PHASE_3:
                new_phase = BossPhase.PHASE_3
            elif health_percentage <= self.phase_health_thresholds[1] and self.current_phase != BossPhase.PHASE_2:
                new_phase = BossPhase.PHASE_2
            
            if new_phase and new_phase != self.current_phase:
                return self._transition_to_phase(new_phase)
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обновления фазы босса: {e}")
            return False
    
    def _transition_to_phase(self, new_phase: BossPhase) -> bool:
        """Переход к новой фазе"""
        try:
            if self.is_phase_transitioning:
                return False
            
            self.is_phase_transitioning = True
            self.phase_transition_time = time.time()
            
            # Обновляем фазу
            old_phase = self.current_phase
            self.current_phase = new_phase
            
            # Разблокируем способности новой фазы
            self._unlock_phase_abilities()
            
            # Обновляем слабости
            self._update_phase_weaknesses()
            
            # Обновляем визуальные индикаторы
            self._update_visual_indicators()
            
            # Воспроизводим эффекты перехода
            self._play_phase_transition_effects()
            
            logger.info(f"Босс {self.name} перешел в фазу {new_phase.value}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка перехода к фазе {new_phase}: {e}")
            return False
    
    def _unlock_phase_abilities(self) -> None:
        """Разблокировка способностей фазы"""
        try:
            phase_data = self.phase_data[self.current_phase]
            
            for ability_id in phase_data.abilities:
                if ability_id in self.abilities:
                    ability = self.abilities[ability_id]
                    if ability.phase == self.current_phase:
                        ability.unlocked = True
                        logger.info(f"Разблокирована способность: {ability.name}")
            
        except Exception as e:
            logger.error(f"Ошибка разблокировки способностей: {e}")
    
    def _update_phase_weaknesses(self) -> None:
        """Обновление слабостей для новой фазы"""
        try:
            phase_data = self.phase_data[self.current_phase]
            
            # Очищаем старые сопротивления
            self.resistances.clear()
            
            # Устанавливаем новые сопротивления
            for resistance_id in phase_data.resistances:
                if resistance_id == "physical":
                    self.resistances[DamageType.PHYSICAL] = 0.3
                elif resistance_id == "lightning":
                    self.resistances[DamageType.LIGHTNING] = 0.4
                elif resistance_id == "acid":
                    self.resistances[DamageType.ACID] = 0.5
            
        except Exception as e:
            logger.error(f"Ошибка обновления слабостей: {e}")
    
    def _update_visual_indicators(self) -> None:
        """Обновление визуальных индикаторов"""
        try:
            phase_data = self.phase_data[self.current_phase]
            indicators = phase_data.visual_indicators
            
            # Обновляем цвет
            if "color" in indicators:
                color = indicators["color"]
                # TODO: Применить цвет к 3D модели
            
            # Обновляем размер
            if "scale" in indicators:
                scale = indicators["scale"]
                # TODO: Применить масштаб к 3D модели
            
        except Exception as e:
            logger.error(f"Ошибка обновления визуальных индикаторов: {e}")
    
    def _play_phase_transition_effects(self) -> None:
        """Воспроизведение эффектов перехода фазы"""
        try:
            phase_data = self.phase_data[self.current_phase]
            
            for effect_id in phase_data.phase_transition_effects:
                if effect_id == "phase_1_complete":
                    self._play_phase_1_complete_effect()
                elif effect_id == "phase_2_complete":
                    self._play_phase_2_complete_effect()
                elif effect_id == "phase_3_complete":
                    self._play_phase_3_complete_effect()
                elif effect_id == "unlock_special_abilities":
                    self._play_unlock_special_abilities_effect()
                elif effect_id == "unlock_ultimate":
                    self._play_unlock_ultimate_effect()
                elif effect_id == "final_form":
                    self._play_final_form_effect()
            
        except Exception as e:
            logger.error(f"Ошибка воспроизведения эффектов перехода: {e}")
    
    def _play_phase_1_complete_effect(self) -> None:
        """Эффект завершения первой фазы"""
        # TODO: Визуальные и звуковые эффекты
        logger.info("Воспроизведен эффект завершения первой фазы")
    
    def _play_phase_2_complete_effect(self) -> None:
        """Эффект завершения второй фазы"""
        # TODO: Визуальные и звуковые эффекты
        logger.info("Воспроизведен эффект завершения второй фазы")
    
    def _play_phase_3_complete_effect(self) -> None:
        """Эффект завершения третьей фазы"""
        # TODO: Визуальные и звуковые эффекты
        logger.info("Воспроизведен эффект завершения третьей фазы")
    
    def _play_unlock_special_abilities_effect(self) -> None:
        """Эффект разблокировки специальных способностей"""
        # TODO: Визуальные и звуковые эффекты
        logger.info("Воспроизведен эффект разблокировки специальных способностей")
    
    def _play_unlock_ultimate_effect(self) -> None:
        """Эффект разблокировки ультимативной способности"""
        # TODO: Визуальные и звуковые эффекты
        logger.info("Воспроизведен эффект разблокировки ультимативной способности")
    
    def _play_final_form_effect(self) -> None:
        """Эффект финальной формы"""
        # TODO: Визуальные и звуковые эффекты
        logger.info("Воспроизведен эффект финальной формы")
    
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
            
            logger.info(f"Босс {self.name} использовал способность: {ability.name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка использования способности {ability_id}: {e}")
            return False
    
    def _apply_ability_effects(self, ability: BossAbility, target_position: Tuple[float, float, float]) -> None:
        """Применение эффектов способности"""
        try:
            # TODO: Применение урона, эффектов, визуальных и звуковых эффектов
            logger.debug(f"Применены эффекты способности {ability.name}")
            
        except Exception as e:
            logger.error(f"Ошибка применения эффектов способности: {e}")
    
    def take_damage(self, damage: int, damage_type: DamageType, source: str = "") -> int:
        """Получение урона с учетом сопротивлений"""
        try:
            # Применяем сопротивления
            resistance = self.resistances.get(damage_type, 0.0)
            final_damage = int(damage * (1.0 - resistance))
            
            # Применяем слабости
            for weakness in self.weaknesses.values():
                if weakness.damage_type == damage_type and self.current_phase == weakness.phase:
                    final_damage = int(final_damage * weakness.multiplier)
                    break
            
            # Наносим урон
            self.health = max(0, self.health - final_damage)
            
            # Проверяем смену фазы
            self.update_phase()
            
            # Проверяем смерть
            if self.health <= 0:
                self._on_death()
            
            logger.debug(f"Босс {self.name} получил {final_damage} урона типа {damage_type.value}")
            return final_damage
            
        except Exception as e:
            logger.error(f"Ошибка получения урона: {e}")
            return 0
    
    def _on_death(self) -> None:
        """Обработка смерти босса"""
        try:
            logger.info(f"Босс {self.name} погиб")
            
            # TODO: Воспроизведение эффектов смерти
            # TODO: Выдача наград
            # TODO: Обновление статистики
            
        except Exception as e:
            logger.error(f"Ошибка обработки смерти босса: {e}")
    
    def update(self, delta_time: float) -> None:
        """Обновление босса"""
        try:
            # Завершаем переход фазы
            if self.is_phase_transitioning:
                current_time = time.time()
                if current_time - self.phase_transition_time >= self.phase_transition_duration:
                    self.is_phase_transitioning = False
            
            # Обновляем способности
            self._update_abilities(delta_time)
            
            # Обновляем визуальные индикаторы
            self._update_visual_indicators()
            
        except Exception as e:
            logger.error(f"Ошибка обновления босса: {e}")
    
    def _update_abilities(self, delta_time: float) -> None:
        """Обновление способностей"""
        try:
            # TODO: Автоматическое использование способностей
            pass
            
        except Exception as e:
            logger.error(f"Ошибка обновления способностей: {e}")
    
    def get_boss_status(self) -> Dict[str, Any]:
        """Получение статуса босса"""
        try:
            return {
                "boss_id": self.entity_id,
                "name": self.name,
                "boss_type": self.boss_type.value,
                "current_phase": self.current_phase.value,
                "health": self.health,
                "max_health": self.max_health,
                "health_percentage": self.health / self.max_health,
                "is_phase_transitioning": self.is_phase_transitioning,
                "unlocked_abilities": [aid for aid, ability in self.abilities.items() if ability.unlocked],
                "current_weaknesses": [weakness.description for weakness in self.weaknesses.values() if self.current_phase == weakness.phase],
                "current_resistances": {dt.value: resistance for dt, resistance in self.resistances.items()}
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статуса босса: {e}")
            return {}
    
    def get_phase_color(self) -> Tuple[float, float, float, float]:
        """Получение цвета фазы"""
        try:
            phase_data = self.phase_data[self.current_phase]
            return phase_data.visual_indicators.get("color", (1, 1, 1, 1))
            
        except Exception as e:
            logger.error(f"Ошибка получения цвета фазы: {e}")
            return (1, 1, 1, 1)
