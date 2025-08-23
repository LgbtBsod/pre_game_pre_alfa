#!/usr/bin/env python3
"""
Система навыков для эволюционной адаптации.
Включает различные типы навыков, их комбинирование и изучение ИИ.
"""

import random
import math
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class SkillType(Enum):
    """Типы навыков"""
    COMBAT = "combat"           # Боевые навыки
    MAGIC = "magic"             # Магические навыки
    SUPPORT = "support"         # Поддерживающие навыки
    UTILITY = "utility"         # Утилитарные навыки
    PASSIVE = "passive"         # Пассивные навыки
    ULTIMATE = "ultimate"       # Ультимативные навыки


class SkillElement(Enum):
    """Элементы навыков"""
    PHYSICAL = "physical"       # Физический
    FIRE = "fire"               # Огонь
    ICE = "ice"                 # Лед
    LIGHTNING = "lightning"     # Молния
    POISON = "poison"           # Яд
    HOLY = "holy"               # Святость
    DARK = "dark"               # Тьма
    COSMIC = "cosmic"           # Космический
    NONE = "none"               # Без элемента


class SkillTarget(Enum):
    """Цели навыков"""
    SELF = "self"               # На себя
    SINGLE_ENEMY = "single_enemy"  # Один враг
    ALL_ENEMIES = "all_enemies"    # Все враги
    SINGLE_ALLY = "single_ally"    # Один союзник
    ALL_ALLIES = "all_allies"      # Все союзники
    AREA = "area"               # Область
    RANDOM = "random"           # Случайная цель


@dataclass
class SkillRequirement:
    """Требования для использования навыка"""
    level: int = 1
    strength: int = 0
    dexterity: int = 0
    intelligence: int = 0
    magic: int = 0
    skill_points: int = 0
    previous_skills: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)


@dataclass
class SkillEffect:
    """Эффект навыка"""
    effect_type: str
    value: float
    duration: float = 0.0
    chance: float = 1.0
    scaling: str = "linear"  # linear, exponential, logarithmic
    element: SkillElement = SkillElement.NONE


@dataclass
class SkillCombo:
    """Комбинация навыков"""
    combo_id: str
    name: str
    description: str
    skills: List[str]
    requirements: SkillRequirement
    effects: List[SkillEffect]
    cooldown: float
    mana_cost: float
    unlock_condition: str = ""
    combo_bonus: float = 1.5


@dataclass
class Skill:
    """Навык"""
    skill_id: str
    name: str
    description: str
    skill_type: SkillType
    element: SkillElement
    target: SkillTarget
    requirements: SkillRequirement
    effects: List[SkillEffect]
    
    # Характеристики
    base_damage: float = 0.0
    base_healing: float = 0.0
    mana_cost: float = 0.0
    cooldown: float = 0.0
    range: float = 1.0
    accuracy: float = 1.0
    critical_chance: float = 0.05
    critical_multiplier: float = 1.5
    
    # Изучение
    learning_progress: float = 0.0
    mastery_level: int = 0
    max_mastery: int = 10
    experience_gained: float = 0.0
    
    # Комбинации
    combo_skills: List[str] = field(default_factory=list)
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def can_use(self, entity_stats: Dict[str, Any]) -> bool:
        """Проверяет, может ли сущность использовать навык"""
        req = self.requirements
        
        if entity_stats.get('level', 0) < req.level:
            return False
        if entity_stats.get('strength', 0) < req.strength:
            return False
        if entity_stats.get('dexterity', 0) < req.dexterity:
            return False
        if entity_stats.get('intelligence', 0) < req.intelligence:
            return False
        if entity_stats.get('magic', 0) < req.magic:
            return False
        
        return True
    
    def calculate_effectiveness(self, target_stats: Dict[str, Any]) -> float:
        """Рассчитывает эффективность навыка против цели"""
        effectiveness = 1.0
        
        # Учет элемента
        if self.element != SkillElement.NONE:
            element_resistance = target_stats.get(f"{self.element.value}_resistance", 0.0)
            effectiveness *= (1.0 - element_resistance)
        
        # Учет уровня мастерства
        effectiveness *= (1.0 + self.mastery_level * 0.1)
        
        return max(0.1, effectiveness)
    
    def gain_experience(self, amount: float):
        """Получает опыт использования навыка"""
        self.experience_gained += amount
        self.learning_progress += amount
        
        # Проверка повышения мастерства
        if self.learning_progress >= 100.0:
            self.learning_progress -= 100.0
            if self.mastery_level < self.max_mastery:
                self.mastery_level += 1
                logger.info(f"Навык {self.name} достиг уровня мастерства {self.mastery_level}")


class SkillManager:
    """Менеджер навыков"""
    
    def __init__(self, db_path: Optional[str] = "data/game_data.db"):
        self.skills: Dict[str, Skill] = {}
        self.skill_combos: Dict[str, SkillCombo] = {}
        self.skill_trees: Dict[str, List[str]] = {}
        self.elemental_affinities: Dict[str, Dict[SkillElement, float]] = {}
        self.db_path = Path(db_path) if db_path else None
        
        # Попытка загрузки из БД, иначе инициализируем базовые
        loaded = False
        try:
            if self.db_path and self.db_path.exists():
                loaded = self._load_skills_from_db()
        except Exception as e:
            logger.error(f"Ошибка загрузки навыков из БД: {e}")
            loaded = False
        
        if not loaded:
            # Инициализация базовых навыков
            self._initialize_basic_skills()
            self._initialize_skill_combos()
    
    def _initialize_basic_skills(self):
        """Инициализация базовых навыков"""
        
        # Боевые навыки
        basic_attack = Skill(
            skill_id="basic_attack",
            name="Базовая атака",
            description="Простая физическая атака",
            skill_type=SkillType.COMBAT,
            element=SkillElement.PHYSICAL,
            target=SkillTarget.SINGLE_ENEMY,
            requirements=SkillRequirement(),
            effects=[SkillEffect("damage", 10.0, element=SkillElement.PHYSICAL)],
            base_damage=10.0,
            cooldown=0.0
        )
        
        fire_ball = Skill(
            skill_id="fire_ball",
            name="Огненный шар",
            description="Магическая атака огнем",
            skill_type=SkillType.MAGIC,
            element=SkillElement.FIRE,
            target=SkillTarget.SINGLE_ENEMY,
            requirements=SkillRequirement(intelligence=5, magic=10),
            effects=[SkillEffect("damage", 25.0, element=SkillElement.FIRE)],
            base_damage=25.0,
            mana_cost=15.0,
            cooldown=2.0
        )
        
        heal = Skill(
            skill_id="heal",
            name="Исцеление",
            description="Восстанавливает здоровье",
            skill_type=SkillType.SUPPORT,
            element=SkillElement.HOLY,
            target=SkillTarget.SINGLE_ALLY,
            requirements=SkillRequirement(intelligence=3, magic=8),
            effects=[SkillEffect("healing", 30.0, element=SkillElement.HOLY)],
            base_healing=30.0,
            mana_cost=12.0,
            cooldown=3.0
        )
        
        self.add_skill(basic_attack)
        self.add_skill(fire_ball)
        self.add_skill(heal)
    
    def _initialize_skill_combos(self):
        """Инициализация комбинаций навыков"""
        
        # Комбинация огня и льда
        fire_ice_combo = SkillCombo(
            combo_id="fire_ice_combo",
            name="Термический шок",
            description="Комбинация огня и льда создает взрыв",
            skills=["fire_ball", "ice_shard"],
            requirements=SkillRequirement(intelligence=8, magic=15),
            effects=[
                SkillEffect("damage", 50.0, element=SkillElement.COSMIC),
                SkillEffect("stun", 2.0, duration=2.0, element=SkillElement.COSMIC)
            ],
            cooldown=10.0,
            mana_cost=30.0,
            combo_bonus=2.0
        )
        
        self.add_skill_combo(fire_ice_combo)
    
    def add_skill(self, skill: Skill):
        """Добавляет навык"""
        self.skills[skill.skill_id] = skill
    
    def add_skill_combo(self, combo: SkillCombo):
        """Добавляет комбинацию навыков"""
        self.skill_combos[combo.combo_id] = combo

    def _load_skills_from_db(self) -> bool:
        """Загружает навыки и их эффекты из SQLite"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            # Загружаем навыки
            cur.execute("SELECT * FROM skills")
            rows = cur.fetchall()
            for r in rows:
                skill = Skill(
                    skill_id=r["skill_id"],
                    name=r["name"],
                    description=r["description"],
                    skill_type=SkillType(r["skill_type"]),
                    element=SkillElement(r["element"]),
                    target=SkillTarget(r["target"]),
                    requirements=SkillRequirement(),
                    effects=[],
                    base_damage=r["base_damage"],
                    base_healing=r["base_healing"],
                    mana_cost=r["mana_cost"],
                    cooldown=r["cooldown"],
                    range=r["range"],
                    accuracy=r["accuracy"],
                    critical_chance=r["critical_chance"],
                    critical_multiplier=r["critical_multiplier"]
                )
                self.add_skill(skill)
            
            # Загружаем эффекты
            cur.execute("SELECT * FROM skill_effects")
            eff_rows = cur.fetchall()
            for er in eff_rows:
                sid = er["skill_id"]
                if sid in self.skills:
                    effect = SkillEffect(
                        effect_type=er["effect_type"],
                        value=er["value"],
                        duration=er["duration"],
                        chance=er["chance"],
                        scaling=er["scaling"],
                        element=SkillElement(er["element"]) if er["element"] else SkillElement.NONE
                    )
                    self.skills[sid].effects.append(effect)
            
            conn.close()
            logger.info(f"Загружено навыков из БД: {len(self.skills)}")
            return len(self.skills) > 0
        except Exception as e:
            logger.error(f"Ошибка чтения БД навыков: {e}")
            return False
    
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Получает навык по ID"""
        return self.skills.get(skill_id)
    
    def get_available_skills(self, entity_stats: Dict[str, Any]) -> List[Skill]:
        """Получает доступные навыки для сущности"""
        return [
            skill for skill in self.skills.values()
            if skill.can_use(entity_stats)
        ]
    
    def get_skill_combo(self, combo_id: str) -> Optional[SkillCombo]:
        """Получает комбинацию навыков по ID"""
        return self.skill_combos.get(combo_id)
    
    def find_available_combos(self, entity_skills: List[str], entity_stats: Dict[str, Any]) -> List[SkillCombo]:
        """Находит доступные комбинации навыков"""
        available_combos = []
        
        for combo in self.skill_combos.values():
            # Проверяем, есть ли все необходимые навыки
            if all(skill_id in entity_skills for skill_id in combo.skills):
                # Проверяем требования
                if combo.requirements.level <= entity_stats.get('level', 0):
                    available_combos.append(combo)
        
        return available_combos
    
    def calculate_combo_damage(self, combo: SkillCombo, entity_stats: Dict[str, Any]) -> float:
        """Рассчитывает урон комбинации"""
        base_damage = sum(
            effect.value for effect in combo.effects
            if effect.effect_type == "damage"
        )
        
        # Применяем бонус комбинации
        total_damage = base_damage * combo.combo_bonus
        
        # Учитываем характеристики сущности
        intelligence_bonus = entity_stats.get('intelligence', 0) * 0.1
        magic_bonus = entity_stats.get('magic', 0) * 0.05
        
        total_damage *= (1.0 + intelligence_bonus + magic_bonus)
        
        return total_damage


class SkillLearningAI:
    """ИИ для изучения навыков"""
    
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        self.learned_skills: Set[str] = set()
        self.skill_combinations: Dict[str, List[str]] = {}
        self.skill_effectiveness: Dict[str, Dict[str, float]] = {}
        self.combo_discoveries: List[Dict[str, Any]] = []
        
        # Q-learning для навыков
        self.skill_q_table: Dict[str, Dict[str, float]] = {}
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        
        # Статистика изучения
        self.learning_stats = {
            "skills_learned": 0,
            "combos_discovered": 0,
            "total_skill_usage": 0,
            "successful_combos": 0
        }
    
    def learn_skill(self, skill_id: str, success_rate: float):
        """Изучает навык"""
        if skill_id not in self.learned_skills:
            self.learned_skills.add(skill_id)
            self.learning_stats["skills_learned"] += 1
            
            # Инициализируем Q-таблицу для навыка
            if skill_id not in self.skill_q_table:
                self.skill_q_table[skill_id] = {}
        
        # Обновляем эффективность навыка
        if skill_id not in self.skill_effectiveness:
            self.skill_effectiveness[skill_id] = {}
        
        # Упрощенная модель эффективности
        current_effectiveness = self.skill_effectiveness[skill_id].get("general", 0.5)
        new_effectiveness = current_effectiveness + (success_rate - current_effectiveness) * self.learning_rate
        self.skill_effectiveness[skill_id]["general"] = max(0.0, min(1.0, new_effectiveness))
    
    def discover_combo(self, skill_ids: List[str], effectiveness: float):
        """Открывает комбинацию навыков"""
        combo_key = "+".join(sorted(skill_ids))
        
        if combo_key not in self.skill_combinations:
            self.skill_combinations[combo_key] = skill_ids
            self.learning_stats["combos_discovered"] += 1
            
            # Записываем открытие
            self.combo_discoveries.append({
                "combo": combo_key,
                "skills": skill_ids,
                "effectiveness": effectiveness,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Открыта новая комбинация навыков: {combo_key}")
    
    def choose_best_skill(self, available_skills: List[str], target_type: str, 
                          situation: str) -> Optional[str]:
        """Выбирает лучший навык для ситуации"""
        if not available_skills:
            return None
        
        # Используем Q-learning для выбора
        best_skill = None
        best_value = float('-inf')
        
        for skill_id in available_skills:
            if skill_id in self.skill_q_table:
                q_value = self.skill_q_table[skill_id].get(situation, 0.0)
                
                # Добавляем элемент исследования
                if random.random() < self.exploration_rate:
                    q_value += random.uniform(0.0, 0.1)
                
                if q_value > best_value:
                    best_value = q_value
                    best_skill = skill_id
        
        # Если нет данных, выбираем случайно
        if best_skill is None:
            best_skill = random.choice(available_skills)
        
        return best_skill
    
    def choose_skill_combo(self, available_combos: List[str], target_type: str,
                          situation: str) -> Optional[str]:
        """Выбирает лучшую комбинацию навыков"""
        if not available_combos:
            return None
        
        # Простая логика выбора комбинации
        # В реальной игре здесь можно использовать более сложную логику
        return random.choice(available_combos)
    
    def update_skill_effectiveness(self, skill_id: str, target_type: str, 
                                 success: bool, damage_dealt: float):
        """Обновляет эффективность навыка"""
        if skill_id not in self.skill_effectiveness:
            self.skill_effectiveness[skill_id] = {}
        
        if target_type not in self.skill_effectiveness[skill_id]:
            self.skill_effectiveness[skill_id][target_type] = 0.5
        
        # Обновляем эффективность
        current_eff = self.skill_effectiveness[skill_id][target_type]
        success_rate = 1.0 if success else 0.0
        damage_bonus = min(damage_dealt / 100.0, 1.0)  # Нормализуем урон
        
        new_eff = current_eff + (success_rate + damage_bonus - current_eff) * self.learning_rate
        self.skill_effectiveness[skill_id][target_type] = max(0.0, min(1.0, new_eff))
        
        # Обновляем статистику
        self.learning_stats["total_skill_usage"] += 1
    
    def get_learning_progress(self) -> Dict[str, Any]:
        """Получает прогресс изучения"""
        return {
            "learned_skills": len(self.learned_skills),
            "discovered_combos": len(self.skill_combinations),
            "learning_stats": self.learning_stats.copy(),
            "skill_effectiveness": self.skill_effectiveness.copy()
        }
    
    def save_learning_state(self, filename: str):
        """Сохраняет состояние изучения"""
        state = {
            "entity_id": self.entity_id,
            "learned_skills": list(self.learned_skills),
            "skill_combinations": self.skill_combinations,
            "skill_effectiveness": self.skill_effectiveness,
            "combo_discoveries": self.combo_discoveries,
            "learning_stats": self.learning_stats
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.info(f"Состояние изучения навыков сохранено в {filename}")
        except Exception as e:
            logger.error(f"Ошибка сохранения состояния изучения: {e}")
    
    def load_learning_state(self, filename: str):
        """Загружает состояние изучения"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.learned_skills = set(state.get("learned_skills", []))
            self.skill_combinations = state.get("skill_combinations", {})
            self.skill_effectiveness = state.get("skill_effectiveness", {})
            self.combo_discoveries = state.get("combo_discoveries", [])
            self.learning_stats = state.get("learning_stats", {})
            
            logger.info(f"Состояние изучения навыков загружено из {filename}")
        except Exception as e:
            logger.error(f"Ошибка загрузки состояния изучения: {e}")


# Фабрика навыков
class SkillFactory:
    """Фабрика создания навыков"""
    
    @staticmethod
    def create_combat_skill(skill_id: str, name: str, damage: float, 
                           element: SkillElement = SkillElement.PHYSICAL) -> Skill:
        """Создает боевой навык"""
        return Skill(
            skill_id=skill_id,
            name=name,
            description=f"Боевой навык {name}",
            skill_type=SkillType.COMBAT,
            element=element,
            target=SkillTarget.SINGLE_ENEMY,
            requirements=SkillRequirement(),
            effects=[SkillEffect("damage", damage, element=element)],
            base_damage=damage,
            cooldown=1.0
        )
    
    @staticmethod
    def create_magic_skill(skill_id: str, name: str, damage: float, 
                          element: SkillElement, mana_cost: float) -> Skill:
        """Создает магический навык"""
        return Skill(
            skill_id=skill_id,
            name=name,
            description=f"Магический навык {name}",
            skill_type=SkillType.MAGIC,
            element=element,
            target=SkillTarget.SINGLE_ENEMY,
            requirements=SkillRequirement(intelligence=5, magic=mana_cost),
            effects=[SkillEffect("damage", damage, element=element)],
            base_damage=damage,
            mana_cost=mana_cost,
            cooldown=2.0
        )
    
    @staticmethod
    def create_support_skill(skill_id: str, name: str, healing: float,
                            mana_cost: float) -> Skill:
        """Создает поддерживающий навык"""
        return Skill(
            skill_id=skill_id,
            name=name,
            description=f"Поддерживающий навык {name}",
            skill_type=SkillType.SUPPORT,
            element=SkillElement.HOLY,
            target=SkillTarget.SINGLE_ALLY,
            requirements=SkillRequirement(intelligence=3, magic=mana_cost),
            effects=[SkillEffect("healing", healing, element=SkillElement.HOLY)],
            base_healing=healing,
            mana_cost=mana_cost,
            cooldown=3.0
        )
